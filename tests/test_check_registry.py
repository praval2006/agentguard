import copy
from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agentguard import check_registry as registry
from agentguard.scenarios import validate_scenario, MAX_CHECK_ID_CHARS


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (self.root / 'service').mkdir()
        self.data = {'version': 1, 'checks': [{'id': 'check.one', 'runner': 'unittest',
            'cwd': 'service', 'target': 'tests.test_feature.Case.test_behavior',
            'coverage': {'id': 'behavior.v1', 'description': 'Descriptive metadata only'}}]}

    def parse(self):
        return registry.parse_registry(json.dumps(self.data), repository_root=self.root)

    def test_valid_immutable(self):
        value = self.parse()
        self.assertEqual(value.checks[0].cwd, self.root / 'service')
        self.assertEqual(value.checks[0].coverage.id, 'behavior.v1')
        with self.assertRaises(FrozenInstanceError):
            value.checks[0].coverage.description = 'changed'
        self.assertIsInstance(value.checks, tuple)
        self.assertFalse(hasattr(value.checks[0], 'verdict'))

    def test_root_cwd(self):
        self.data['checks'][0]['cwd'] = '.'
        self.assertEqual(self.parse().checks[0].cwd, self.root)

    def test_versions(self):
        for version in (True, 1.0, 2, '1', None):
            self.data['version'] = version
            with self.assertRaises(ValueError): self.parse()

    def test_exact_shapes(self):
        original = copy.deepcopy(self.data)
        for location in ('root', 'check', 'coverage'):
            for extra in (False, True):
                self.data = copy.deepcopy(original)
                node = self.data if location == 'root' else self.data['checks'][0]
                if location == 'coverage': node = node['coverage']
                if extra: node['unknown'] = 1
                else: del node[next(iter(node))]
                with self.assertRaises(ValueError): self.parse()

    def test_duplicate_ids(self):
        for field in ('id', 'coverage'):
            other = copy.deepcopy(self.data['checks'][0])
            other['id'] = 'check.two'
            other['coverage']['id'] = 'behavior.v2'
            other[field] = copy.deepcopy(self.data['checks'][0][field])
            self.data['checks'] = [self.data['checks'][0], other]
            with self.assertRaises(ValueError): self.parse()

    def test_duplicate_json_keys(self):
        for text in ('{"version":1,"version":1,"checks":[]}',
                     '{"version":1,"checks":[{"id":"a","id":"b"}]}'):
            with self.assertRaises(ValueError):
                registry.parse_registry(text, repository_root=self.root)

    def test_runner(self):
        for runner in ('pytest', '', None, {}):
            self.data['checks'][0]['runner'] = runner
            with self.assertRaises(ValueError): self.parse()

    def test_invalid_targets(self):
        for target in ('a', 'a.b', 'a.b.run', 'a..B.test_x', 'a/B.test_x',
                       'a.B.test_x()', 'a.B.test_x;echo', 'a.B.test_*'):
            self.data['checks'][0]['target'] = target
            with self.assertRaises(ValueError): self.parse()

    def test_string_limits(self):
        for field, limit in (('id', 128), ('target', 512), ('cwd', 512)):
            old = self.data['checks'][0][field]
            self.data['checks'][0][field] = 'x' * (limit + 1)
            with self.assertRaises(ValueError): self.parse()
            self.data['checks'][0][field] = old
        for field, limit in (('id',128), ('description',2048)):
            old = self.data['checks'][0]['coverage'][field]
            self.data['checks'][0]['coverage'][field] = 'x' * (limit + 1)
            with self.assertRaises(ValueError): self.parse()
            self.data['checks'][0]['coverage'][field] = old

    def test_count_bound(self):
        self.data['checks'] *= registry.MAX_CHECKS + 1
        with self.assertRaises(ValueError): self.parse()
        self.data['checks'] = []
        self.assertEqual(self.parse().checks, ())

    def test_forbidden_configuration(self):
        for field in ('argv','executable','interpreter','env','environment','setup',
                      'teardown','shell','timeout','output_limit'):
            self.data['checks'][0][field] = 'anything'
            with self.assertRaises(ValueError): self.parse()
            del self.data['checks'][0][field]

    def test_bad_paths(self):
        for path in ('/tmp', '../outside', 'service/../service', 'service//x',
                     'service/', './service', '', 'C:/temp', 'C:temp',
                     '\\\\host\\share', 'service\\x', 'service/ x', 'service/\x00'):
            self.data['checks'][0]['cwd'] = path
            with self.assertRaises(ValueError): self.parse()

    def test_missing_cwd(self):
        self.data['checks'][0]['cwd'] = 'missing'
        with self.assertRaises(FileNotFoundError): self.parse()

    def test_symlink_cwd(self):
        for target in (self.root / 'service', Path(tempfile.gettempdir())):
            link = self.root / 'link'
            link.symlink_to(target, target_is_directory=True)
            self.data['checks'][0]['cwd'] = 'link'
            with self.assertRaises(ValueError): self.parse()
            link.unlink()

    def test_load_and_no_execution(self):
        path = self.root / 'checks.json'
        path.write_text(json.dumps(self.data))
        with patch('subprocess.run', side_effect=AssertionError('execution')), \
             patch('subprocess.Popen', side_effect=AssertionError('execution')), \
             patch('os.system', side_effect=AssertionError('execution')):
            self.assertEqual(registry.load_registry(repository_root=self.root,
                             registry_path='checks.json'), self.parse())

    def test_registry_paths(self):
        path = self.root / 'checks.json'
        path.write_text(json.dumps(self.data))
        (self.root / 'alias').symlink_to(path)
        (self.root / 'diralias').symlink_to(self.root, target_is_directory=True)
        for name in ('alias', 'diralias/checks.json', '../checks.json', str(path)):
            with self.assertRaises(ValueError):
                registry.load_registry(repository_root=self.root, registry_path=name)
        with self.assertRaises(FileNotFoundError):
            registry.load_registry(repository_root=self.root, registry_path='absent')

    def test_malformed_and_oversized_json(self):
        for text in ('{', 'null', '[]', ' ' * (registry.MAX_REGISTRY_BYTES + 1)):
            with self.assertRaises(ValueError):
                registry.parse_registry(text, repository_root=self.root)
        (self.root/'bad').write_bytes(b'\xff')
        with self.assertRaises(ValueError):
            registry.load_registry(repository_root=self.root, registry_path='bad')


class RegisteredScenarioTests(unittest.TestCase):
    def scenario(self):
        return {'name':'Check', 'source':'explicit', 'reason':'Requirement',
                'action':{'type':'registered_check','check_id':'check.one'}}

    def test_valid(self):
        self.assertIsNone(validate_scenario(self.scenario()))

    def test_missing_blank_oversized(self):
        for value in (None, '', ' ', 1, 'a' * (MAX_CHECK_ID_CHARS+1)):
            s = self.scenario()
            if value is None: del s['action']['check_id']
            else: s['action']['check_id'] = value
            with self.assertRaises(ValueError): validate_scenario(s)

    def test_no_injected_authority(self):
        for field in ('argv','cwd','command','environment','timeout','coverage','executable'):
            s = self.scenario(); s['action'][field] = 'injected'
            with self.assertRaises(ValueError): validate_scenario(s)
        for field in ('assertions','coverage'):
            s = self.scenario(); s[field] = []
            with self.assertRaises(ValueError): validate_scenario(s)

    def test_limit_and_nonmutation(self):
        s = self.scenario(); s['action']['check_id'] = 'x' * MAX_CHECK_ID_CHARS
        before = copy.deepcopy(s)
        validate_scenario(s)
        self.assertEqual(s, before)

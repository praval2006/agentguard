"""Bounded registered unittest observations; no acceptance verdicts.

Registry is a trusted in-memory snapshot, not authority obtained from model data.
Revalidate its values and paths on each call. No snapshot freshness/coverage proof
is claimed. Trusted tests can perform side effects or forge evidence: this is not
a sandbox. No concurrent filesystem mutation is assumed. POSIX process groups
bound child cleanup; temporary capture bounds retained evidence, not disk usage.
"""
from dataclasses import asdict
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile

from .check_registry import Registry, parse_registry
from .scenarios import validate_scenario

TIMEOUT_SECONDS = 10
OUTPUT_LIMIT = 4096
RESULT_LIMIT = 2048
_RUNNER = Path(__file__).with_name('check_runner.py').resolve()
_COUNTS = ('tests_run', 'failures', 'errors', 'skips', 'expected_failures', 'unexpected_successes')
_STATUSES = {'success', 'assertion_failure', 'test_error', 'skipped', 'expected_failure',
             'unexpected_success', 'load_error', 'zero_tests', 'multiple_tests'}


def _validate_result(value):
    if type(value) is not dict or set(value) != {'status', *_COUNTS}:
        raise ValueError('invalid runner result')
    if type(value['status']) is not str or value['status'] not in _STATUSES:
        raise ValueError('invalid runner status')
    if any(type(value[k]) is not int or not 0 <= value[k] <= 1000000 for k in _COUNTS):
        raise ValueError('invalid runner counts')
    if value['status'] == 'success' and (value['tests_run'] != 1 or any(value[k] for k in _COUNTS[1:])):
        raise ValueError('inconsistent success')
    if value['status'] == 'assertion_failure' and (value['tests_run'] != 1 or value['failures'] < 1
            or any(value[k] for k in _COUNTS[2:])):
        raise ValueError('inconsistent failure')
    required = {'test_error': 'errors', 'skipped': 'skips',
                'expected_failure': 'expected_failures',
                'unexpected_success': 'unexpected_successes'}
    if value['status'] in required and not value[required[value['status']]]:
        raise ValueError('status lacks supporting count')
    if value['status'] in ('load_error', 'zero_tests', 'multiple_tests') and any(value[k] for k in _COUNTS[1:]):
        raise ValueError('selection status contains test outcomes')
    return value


def _pairs(pairs):
    data = {}
    for key, value in pairs:
        if key in data: raise ValueError('duplicate result key')
        data[key] = value
    return data


def execute_registered_check(scenario, *, repository_root, registry):
    """Return execution facts only. Invalid scenarios raise ValueError.

    Ordinary configuration/process failures return a bounded status; provenance
    is descriptive only. No verifier, orchestrator, or coverage binding is used.
    """
    validate_scenario(scenario)
    if scenario['action']['type'] != 'registered_check':
        raise ValueError('registered_check scenario required')
    observation = dict(check_id=scenario['action']['check_id'], coverage_id=None,
                       target=None, status='configuration_error', returncode=None,
                       timed_out=False, output_truncated=False, tests_run=None,
                       failures=None, errors=None, skips=None, expected_failures=None,
                       unexpected_successes=None)
    try:
        if type(registry) is not Registry: return observation
        root = Path(repository_root).resolve(strict=True)
        if root != registry.repository_root or registry.repository_root.resolve(strict=True) != root:
            return observation
        data = {'version': 1, 'checks': []}
        for registration in registry.checks:
            entry = asdict(registration)
            entry['cwd'] = str(registration.cwd.relative_to(root))
            data['checks'].append(entry)
        validated = parse_registry(json.dumps(data), repository_root=root)
        check = next((c for c in validated.checks if c.id == observation['check_id']), None)
        if check is None:
            observation['status'] = 'unknown_check'
            return observation
        # Reject all symlinks in the selected local tree, including internal ones.
        for path in check.cwd.rglob('*'):
            if path.is_symlink() or not path.resolve(strict=True).is_relative_to(root):
                raise ValueError('unsafe test tree')
        observation.update(coverage_id=check.coverage.id, target=check.target)
    except (OSError, ValueError, TypeError, AttributeError, RuntimeError):
        return observation
    try:
        with tempfile.TemporaryFile() as capture, tempfile.TemporaryFile() as result:
            process = subprocess.Popen(
                [sys.executable, '-I', '-B', str(_RUNNER), check.target, str(result.fileno())],
                cwd=check.cwd, stdin=subprocess.DEVNULL, stdout=capture,
                stderr=subprocess.STDOUT, shell=False, pass_fds=(result.fileno(),),
                start_new_session=True)
            try:
                observation['returncode'] = process.wait(timeout=TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                observation.update(status='timeout', timed_out=True)
            finally:
                # Kill remaining descendants too, even if the leader exited normally.
                try: os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                process.wait()
            capture.seek(0)
            observation['output_truncated'] = len(capture.read(OUTPUT_LIMIT + 1)) > OUTPUT_LIMIT
            if observation['timed_out']: return observation
            if observation['returncode'] != 0:
                observation['status'] = 'process_crash'
                return observation
            result.seek(0)
            raw = result.read(RESULT_LIMIT + 1)
            try:
                if len(raw) > RESULT_LIMIT: raise ValueError('oversized result')
                facts = _validate_result(json.loads(raw, object_pairs_hook=_pairs))
            except (ValueError, UnicodeError, RecursionError):
                observation['status'] = 'malformed_result'
                return observation
            observation.update(facts)
    except OSError:
        observation['status'] = 'execution_error'
    return observation

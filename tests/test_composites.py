import copy
import json
import unittest
from unittest.mock import patch
from agentguard.scenarios import validate_scenario
from agentguard.verifier import aggregate_composite_results


def composite(count=2):
    return dict(name='Boundaries',source='explicit',reason='Both limits',behavior='Accept both limits',
        action=dict(type='composite',children=[dict(label=f'child-{i}',
            action=dict(type='http_request',method='POST',path='/check',json={'value':i}),
            assertions=[dict(type='status',equals=200),dict(type='json_exists',path='id'),
                        dict(type='json_type',path='id',equals='integer')]) for i in range(count)]))


class CompositeTests(unittest.TestCase):
    def test_valid_two_three(self):
        for n in (2,3):
            s=composite(n); before=copy.deepcopy(s)
            self.assertIsNone(validate_scenario(s))
            self.assertEqual(s,before)

    def test_unsupported(self):
        s=composite(); s['action']['children'][1]={'label':'unknown','action':{'type':'unsupported','explanation':'No evidence'}}
        validate_scenario(s)
        s['action']['children'][1]['assertions']=[]
        with self.assertRaises(ValueError): validate_scenario(s)

    def test_child_count(self):
        for n in (0,1,4):
            with self.assertRaises(ValueError): validate_scenario(composite(n))

    def test_forbidden_actions(self):
        for action in (composite()['action'],dict(type='registered_check',check_id='x'),
                       dict(type='test_command',command=['x']),dict(type='other')):
            s=composite(); s['action']['children'][0]['action']=action
            with self.assertRaises(ValueError): validate_scenario(s)

    def test_labels(self):
        for label in ('',' ', 'x'*65, 'child-1', None):
            s=composite(); s['action']['children'][0]['label']=label
            with self.assertRaises(ValueError): validate_scenario(s)
        s=composite(); s['action']['children'][0]['label']='x'*64
        validate_scenario(s)

    def test_child_injections(self):
        for field in ('source','name','reason','behavior','variables','optional','retry','setup','base_url'):
            s=composite(); s['action']['children'][0][field]='injected'
            with self.assertRaises(ValueError): validate_scenario(s)

    def test_parent_exact_fields(self):
        for field in ('assertions','variables','coverage'):
            s=composite(); s[field]=[]
            with self.assertRaises(ValueError): validate_scenario(s)
        for field in ('name','source','reason','behavior','action'):
            s=composite(); del s[field]
            with self.assertRaises(ValueError): validate_scenario(s)
        s=composite(); s['behavior']=' '
        with self.assertRaises(ValueError): validate_scenario(s)

    def test_action_extra(self):
        for field in ('retry','optional','setup','teardown','base_url'):
            s=composite(); s['action'][field]=True
            with self.assertRaises(ValueError): validate_scenario(s)

    def test_assertion_bound(self):
        s=composite(); child=s['action']['children'][0]
        child['assertions']=[dict(type='status',equals=200)]*8
        validate_scenario(s)
        child['assertions'].append(dict(type='status',equals=200))
        with self.assertRaises(ValueError): validate_scenario(s)

    def test_byte_bound(self):
        s=composite(); s['behavior']=''
        size=len(json.dumps(s,ensure_ascii=False,separators=(',',':')).encode())
        s['behavior']='x'*(32000-size)
        validate_scenario(s)
        s['behavior']+='é'
        with self.assertRaises(ValueError): validate_scenario(s)

    def test_invalid_payload_serialization(self):
        for value in (object(),float('nan')):
            s=composite(); s['action']['children'][0]['action']['json']['value']=value
            with self.assertRaises(ValueError): validate_scenario(s)
        s=composite(); data=s['action']['children'][0]['action']['json']; data['cycle']=data
        with self.assertRaises(ValueError): validate_scenario(s)

    def test_aggregation(self):
        for verdicts,expected in ((['PASS','PASS'],'PASS'),(['PASS']*3,'PASS'),
                                 (['PASS','UNVERIFIED'],'UNVERIFIED'),(['UNVERIFIED']*2,'UNVERIFIED'),
                                 (['FAIL','PASS'],'FAIL'),(['FAIL','UNVERIFIED'],'FAIL'),(['FAIL']*2,'FAIL')):
            s=composite(len(verdicts)); results=[dict(label=f'child-{i}',verdict=v) for i,v in enumerate(verdicts)]
            before=copy.deepcopy((s,results))
            with patch('builtins.open',side_effect=AssertionError('I/O')),patch('subprocess.Popen',side_effect=AssertionError('execution')):
                self.assertEqual(aggregate_composite_results(s,results),expected)
            self.assertEqual((s,results),before)

    def test_malformed_results(self):
        good=[dict(label='child-0',verdict='PASS'),dict(label='child-1',verdict='PASS')]
        for results in (None,[],good[:1],good+[good[0]],good[::-1],[good[0],good[0]],
                        [good[0],dict(label='unexpected',verdict='PASS')],
                        [good[0],dict(label='child-1',verdict='OTHER')],
                        [good[0],dict(label='child-1',verdict=True)],
                        [good[0],dict(label='child-1',verdict='PASS',extra=1)]):
            with self.assertRaises(ValueError): aggregate_composite_results(composite(),results)

    def test_noncomposite_aggregation(self):
        s=dict(name='x',source='explicit',reason='x',action=dict(type='unsupported',explanation='x'))
        with self.assertRaises(ValueError): aggregate_composite_results(s,[])

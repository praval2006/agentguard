from copy import deepcopy
from http.server import ThreadingHTTPServer
import threading
import unittest
from unittest.mock import patch
import test_http_execution as http_fixture
from agentguard import acceptance
from agentguard.verifier import aggregate_composite_results


def parent(paths):
    return dict(name='Required observations',source='explicit',reason='All required',
        behavior='Observe every documented response',action=dict(type='composite',children=[
            dict(label=f'child-{i}',action=dict(type='http_request',method='GET',path=p),
                 assertions=[dict(type='status',equals=200),dict(type='json_exists',path='item.state'),
                             dict(type='json_type',path='item.state',equals='string')]) for i,p in enumerate(paths)]))


def unsupported():
    return dict(name='Unknown',source='explicit',reason='Required',action=dict(type='unsupported',explanation='No evidence'))


class CompositeExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),http_fixture.Handler)
        cls.server.daemon_threads=True
        cls.server.requests=[]
        cls.thread=threading.Thread(target=cls.server.serve_forever,kwargs={'poll_interval':0.01},daemon=True)
        cls.thread.start()
        cls.url=f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def setUp(self): self.server.requests.clear()

    def run_parent(self,paths):
        return acceptance.run_acceptance([parent(paths)],base_url=self.url)

    def test_two_three_pass(self):
        for paths in (['/a','/b'],['/a','/b','/c']):
            self.server.requests.clear()
            r=self.run_parent(paths)
            self.assertEqual(r['verdict'],'PASS')
            self.assertEqual(len(r['results']),1)
            self.assertEqual(self.server.requests,paths)
            self.assertEqual(r['results'][0]['result']['child_counts'],
                             {'required':len(paths),'pass':len(paths),'fail':0,'unverified':0})

    def test_partial_and_failure_combinations(self):
        for paths,expected in ((['/a','/bad'],'UNVERIFIED'),(['/a','/500'],'FAIL'),
                               (['/500','/bad'],'FAIL'),(['/500','/a','/b'],'FAIL')):
            self.server.requests.clear()
            r=self.run_parent(paths)
            self.assertEqual(r['verdict'],expected)
            self.assertEqual(self.server.requests,paths)
            self.assertEqual(len(r['results'][0]['result']['children']),len(paths))

    def test_unsupported_child(self):
        s=parent(['/a','/b']); s['action']['children'][1]={'label':'unknown','action':unsupported()['action']}
        r=acceptance.run_acceptance([s],base_url=self.url)
        result=r['results'][0]['result']
        self.assertEqual(result['verdict'],'UNVERIFIED')
        self.assertEqual(result['child_counts'],{'required':2,'pass':1,'fail':0,'unverified':1})
        self.assertEqual([c['label'] for c in result['children']],['child-0','unknown'])
        self.assertEqual(self.server.requests,['/a'])

    def test_evidence_and_nonmutation(self):
        s=parent(['/a','/b']); before=deepcopy(s)
        r=acceptance.run_acceptance([s],base_url=self.url)['results'][0]
        self.assertEqual(s,before)
        self.assertIsNone(r['observation'])
        self.assertEqual(r['result']['behavior'],s['behavior'])
        self.assertEqual(r['result']['reason'],s['reason'])
        self.assertEqual(r['result']['children'][0]['result']['assertions'][2]['observed_type'],'string')

    def test_caller_mutation_during_execution(self):
        s=parent(['/a','/b']); real=acceptance.execute_http_scenario
        def execute(leaf,**kwargs):
            s['action']['children'].clear()
            return real(leaf,**kwargs)
        with patch.object(acceptance,'execute_http_scenario',side_effect=execute):
            r=acceptance.run_acceptance([s],base_url=self.url)
        self.assertEqual(self.server.requests,['/a','/b'])
        self.assertEqual(r['verdict'],'PASS')

    def test_invalid_later_top_level(self):
        with self.assertRaises(ValueError): acceptance.run_acceptance([parent(['/a','/b']),{}],base_url=self.url)
        self.assertEqual(self.server.requests,[])

    def test_invalid_later_child(self):
        s=parent(['/a','/b']); s['action']['children'][1]['optional']=True
        with self.assertRaises(ValueError): acceptance.run_acceptance([s],base_url=self.url)
        self.assertEqual(self.server.requests,[])

    def test_missing_url(self):
        for url in (None,'',' ',1):
            r=acceptance.run_acceptance([parent(['/a','/b'])],base_url=url)
            self.assertEqual(r['verdict'],'UNVERIFIED')
            self.assertEqual(r['results'][0]['result']['child_counts']['unverified'],2)
        self.assertEqual(self.server.requests,[])

    def test_top_level_aggregation(self):
        standalone=http_fixture.scenario()
        for paths,other,expected in ((['/a','/b'],standalone,'PASS'),
                                     (['/a','/bad'],standalone,'UNVERIFIED'),
                                     (['/500','/a'],unsupported(),'FAIL')):
            r=acceptance.run_acceptance([parent(paths),other],base_url=self.url)
            self.assertEqual(r['verdict'],expected)
            self.assertEqual(len(r['results']),2)

    def test_parent_aggregation_delegated(self):
        with patch.object(acceptance,'aggregate_composite_results',wraps=aggregate_composite_results) as aggregate:
            self.run_parent(['/a','/b'])
        aggregate.assert_called_once()
        self.assertEqual(aggregate.call_args.args[1],[{'label':'child-0','verdict':'PASS'},{'label':'child-1','verdict':'PASS'}])

    def test_programming_error_propagates(self):
        with patch.object(acceptance,'execute_http_scenario',side_effect=RuntimeError('bug')) as execute:
            with self.assertRaises(RuntimeError): self.run_parent(['/a','/b'])
        self.assertEqual(execute.call_count,1)

    def test_unknown_child_verdict_rejected(self):
        with patch.object(acceptance,'execute_http_scenario',return_value={'execution':{},'observation':None,'result':{'verdict':'OTHER'}}):
            with self.assertRaises(ValueError): self.run_parent(['/a','/b'])

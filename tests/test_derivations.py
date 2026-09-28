"""Deterministic derivation/trust tests; no frozen evaluation fixtures."""
import copy
from dataclasses import FrozenInstanceError, replace
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import unittest
from unittest.mock import Mock, patch

from agentguard.derivations import (InputConstraint, DerivationPolicy, derive,
                                    MAX_INTEGER, validate_provenance)
from agentguard.grounding import ground_scenarios
from agentguard.scenarios import validate_scenario
from agentguard.acceptance import run_acceptance
from agentguard.http_execution import execute_http_scenario
from agentguard.verifier import verify_observation

CONTEXT = 'POST /validate: amount is an integer from 10 through 20 inclusive. label accepts arbitrary nonblank text, no domain, format, identity or state semantics.'
HASH = hashlib.sha256(CONTEXT.encode()).hexdigest()
NUMBER = InputConstraint('amount', 'POST', '/validate', 'amount', CONTEXT, 'integer', 'plain_scalar', 10, 20)
TEXT = InputConstraint('label', 'POST', '/validate', 'label', CONTEXT, 'string', 'arbitrary_text', nonblank=True)
POLICY = DerivationPolicy(HASH, (NUMBER, TEXT))
PLAN = dict(explicit_requirements=['Validate input'], inferred_behaviors=[], ambiguities=[],
            scenarios=[dict(name='Validation', source='explicit', reason='Input contract', behavior='Reject invalid input')])


def request(rule='below_inclusive_lower_bound', field='amount', **extra):
    return dict(field=field, rule=rule, fact_id=field, **extra)


def output(req=None):
    return [dict(name='Validation', source='explicit', reason='Input contract',
                 action=dict(type='http_request', method='POST', path='/validate', json={},
                             derive=[req or request()]),
                 assertions=[dict(type='status', equals=200)])]


def ground(candidate=None, policy=POLICY):
    return ground_scenarios(PLAN, CONTEXT, grounding_provider=lambda _: candidate or output(),
                            derivation_policy=policy)


class DerivationTests(unittest.TestCase):
    def value(self, req, policy=POLICY):
        return derive(req, policy=policy, context=CONTEXT, action=output()[0]['action'])

    def test_integer_boundaries(self):
        for rule, expected, source in (('below_inclusive_lower_bound', 9, 10), ('above_inclusive_upper_bound', 21, 20)):
            value, p = self.value(request(rule))
            self.assertEqual(value, expected)
            self.assertEqual(p['source_value'], source)
            self.assertEqual(p['kind'], 'derived')
            self.assertEqual(p['context_sha256'], HASH)

    def test_text_derivations(self):
        for rule, expected in (('blank_string', ''), ('whitespace_string', '   '), ('neutral_nonblank_text', 'agentguard-test')):
            value, p = self.value(request(rule, 'label'))
            self.assertEqual(value, expected)
            self.assertEqual(p['kind'], 'synthetic')

    def test_wrong_primitive_types(self):
        for kind, expected in (('integer', 0), ('number', 0.5), ('boolean', False), ('null', None)):
            value, _ = self.value(request('wrong_primitive_type', 'label', representative=kind))
            self.assertIs(type(value), type(expected))
            self.assertEqual(value, expected)
        with self.assertRaises(ValueError): self.value(request('wrong_primitive_type', 'label', representative='string'))
        policy = DerivationPolicy(HASH, (replace(NUMBER, expected_type='number', lower=None, upper=None),))
        with self.assertRaises(ValueError): self.value(request('wrong_primitive_type', representative='integer'), policy)
        self.assertEqual(self.value(request('wrong_primitive_type', representative='number'))[0], 0.5)

    def test_bad_bounds(self):
        for value in (True, 10.0, float('nan'), float('inf'), '10', MAX_INTEGER+1):
            with self.subTest(value=value), self.assertRaises(ValueError): replace(NUMBER, lower=value)
        with self.assertRaises(ValueError): replace(NUMBER, lower=21)
        with self.assertRaises(ValueError): replace(TEXT, lower=1)
        with self.assertRaises(ValueError): self.value(request(), DerivationPolicy(HASH,(replace(NUMBER,lower=None),)))

    def test_overflow(self):
        for rule, fact in (('above_inclusive_upper_bound',replace(NUMBER,upper=MAX_INTEGER)),
                           ('below_inclusive_lower_bound',replace(NUMBER,lower=-MAX_INTEGER))):
            with self.assertRaises(ValueError):self.value(request(rule),DerivationPolicy(HASH,(fact,)))

    def test_unknown_and_forbidden_rules(self):
        for rule in ('fresh_unknown_id','existing_id','enum_member','path','endpoint','header','method',
                     'expected_output','authorization','state','command','coverage','token','filename'):
            with self.subTest(rule=rule):
                result=ground(output(request(rule)))
                self.assertEqual(result[0]['action']['type'],'unsupported')

    def test_forbidden_semantic_classes(self):
        for kind in ('resource_id','fresh_id','enum','email','postal_code','filename','secret','account','domain','state'):
            with self.subTest(kind=kind),self.assertRaises(ValueError): replace(TEXT,value_class=kind)
        with self.assertRaises(ValueError): self.value(request('neutral_nonblank_text','label'),DerivationPolicy(HASH,(replace(TEXT,value_class='plain_scalar'),)))
        with self.assertRaises(ValueError): replace(TEXT,nonblank=False)

    def test_nonblank_requirement(self):
        policy=DerivationPolicy(HASH,(replace(TEXT,value_class='plain_scalar',nonblank=False),))
        for rule in ('blank_string','whitespace_string'):
            with self.assertRaises(ValueError):self.value(request(rule,'label'),policy)

    def test_policy_bounds_immutability(self):
        with self.assertRaises(FrozenInstanceError): NUMBER.lower=0
        for facts in ([NUMBER], (NUMBER,NUMBER), tuple(replace(NUMBER,id=str(i),field='v'+str(i)) for i in range(33))):
            with self.assertRaises(ValueError): DerivationPolicy(HASH,facts)
        for changes in ({'quote':'x'*513},{'field':'a.b'},{'path':'/{id}'},{'path':'/x?y=z'},{'method':'TRACE'}):
            with self.assertRaises(ValueError): replace(NUMBER,**changes)

    def test_stale_or_unquoted_policy_before_provider(self):
        for policy in (DerivationPolicy('0'*64,(NUMBER,)),DerivationPolicy(HASH,(replace(NUMBER,quote='absent quote'),))):
            provider=Mock(return_value=output())
            with self.assertRaises(ValueError):ground_scenarios(PLAN,CONTEXT,grounding_provider=provider,derivation_policy=policy)
            provider.assert_not_called()

    def test_target_binding(self):
        for field,value in (('path','/other'),('method','GET'),('type','test_command')):
            candidate=output();candidate[0]['action'][field]=value
            self.assertEqual(ground(candidate)[0]['action']['type'],'unsupported')
        self.assertEqual(ground(output(request(field='resource_id')))[0]['action']['type'],'unsupported')

    def test_model_cannot_supply_authority_or_value(self):
        for extras in ({'value':999},{'source_value':1000},{'constraint':dict(NUMBER.__dict__)},{'authorization':True}):
            self.assertEqual(ground(output(request(**extras)))[0]['action']['type'],'unsupported')
        candidate=ground();self.assertEqual(ground(candidate)[0]['action']['type'],'unsupported')
        self.assertEqual(ground(policy=None)[0]['action']['type'],'unsupported')
        with self.assertRaises(ValueError):ground(policy={'constraints':[dict(NUMBER.__dict__)]})

    def test_collisions_duplicates_and_request_bounds(self):
        for mutation in ('collision','duplicate','empty','many'):
            candidate=output();a=candidate[0]['action']
            if mutation=='collision':a['json']['amount']=9
            if mutation=='duplicate':a['derive']*=2
            if mutation=='empty':a['derive']=[]
            if mutation=='many':a['derive']*=9
            self.assertEqual(ground(candidate)[0]['action']['type'],'unsupported')

    def test_compilation_and_nonmutation(self):
        candidate=output();before=copy.deepcopy(candidate)
        result=ground(candidate)[0]
        self.assertEqual(candidate,before)
        self.assertEqual(result['action']['json'],{'amount':9})
        self.assertNotIn('derive',result['action'])
        validate_scenario(result)
        self.assertEqual(result['action']['derivations'][0]['constraint']['lower'],10)

    def test_defensive_policy_facts(self):
        def provider(req):
            req['derivation_facts'][0]['lower']=100
            return output()
        result=ground_scenarios(PLAN,CONTEXT,grounding_provider=provider,derivation_policy=POLICY)
        self.assertEqual(result[0]['action']['json']['amount'],9)

    def test_provenance_tampering(self):
        for key,value in (('value',True),('value',100),('source_value',True),('kind','synthetic'),('context_sha256','bad')):
            candidate=ground()[0];candidate['action']['derivations'][0][key]=value
            with self.assertRaises(ValueError):validate_scenario(candidate)
        candidate=ground()[0];candidate['action']['json']['amount']=10
        with self.assertRaises(ValueError):validate_scenario(candidate)

    def test_provenance_cannot_target_expected_output(self):
        candidate=output();candidate[0]['assertions'][0]['derive']=request()
        with self.assertRaises(ValueError):ground(candidate)
        candidate=output();candidate[0]['action']['derive'][0]['field']='assertions'
        self.assertEqual(ground(candidate)[0]['action']['type'],'unsupported')

    def test_legacy_shape_and_request(self):
        candidate=output();del candidate[0]['action']['derive']
        def provider(req):
            self.assertEqual(set(req),{'instructions','planner_output','repository_context'})
            return candidate
        result=ground_scenarios(PLAN,CONTEXT,grounding_provider=provider)
        self.assertEqual(json.dumps(result),json.dumps(candidate))

    def test_composite_and_missing_target_provenance(self):
        parent={**PLAN['scenarios'][0], 'action':{'type':'composite','children':[
            {'label':'first',**{k:v for k,v in output()[0].items() if k in ('action','assertions')}},
            {'label':'second','action':{'type':'unsupported','explanation':'No evidence'}}]}}
        grounded=ground([parent]);validate_scenario(grounded[0])
        result=run_acceptance(grounded)
        self.assertEqual(result['verdict'],'UNVERIFIED')
        self.assertIn('input_derivations',result['results'][0]['result']['children'][0]['execution'])
        self.assertEqual(grounded[0]['behavior'],PLAN['scenarios'][0]['behavior'])

    def test_provenance_is_not_observation(self):
        s=ground()[0]
        self.assertEqual(verify_observation(s)['verdict'],'UNVERIFIED')
        self.assertEqual(verify_observation(s,{'type':'http_response','status':500})['verdict'],'FAIL')
        with patch('socket.socket',side_effect=AssertionError('I/O')):
            self.assertEqual(ground()[0]['action']['json']['amount'],9)


class DerivedHttpTests(unittest.TestCase):
    def test_real_http_derivation_and_verdicts(self):
        received=[]
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):return
            def do_POST(self):
                received.append(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
                data=b'{}'; self.send_response(200);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            s=ground()[0];before=copy.deepcopy(s)
            url=f'http://127.0.0.1:{server.server_port}'
            with patch('agentguard.http_execution.verify_observation',wraps=verify_observation) as verifier:
                result=execute_http_scenario(s,base_url=url)
                verifier.assert_called_once()
            self.assertEqual(received,[{'amount':9}])
            self.assertEqual(s,before)
            self.assertEqual(result['result']['verdict'],'PASS')
            self.assertEqual(result['execution']['input_derivations'],s['action']['derivations'])
            s['assertions'][0]['equals']=201
            self.assertEqual(execute_http_scenario(s,base_url=url)['result']['verdict'],'FAIL')
            rejected=execute_http_scenario(s,base_url='http://example.invalid:80')
            self.assertEqual(rejected['result']['verdict'],'UNVERIFIED')
            self.assertIn('input_derivations',rejected['execution'])
        finally:
            server.shutdown();server.server_close();thread.join()

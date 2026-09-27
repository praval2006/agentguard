import copy
import unittest
from agentguard.scenarios import validate_scenario, MAX_JSON_ASSERTION_PATH_CHARS
from agentguard.verifier import verify_observation, MAX_JSON_TEXT_CHARS
from agentguard.http_execution import _pairs
import json


def scenario(assertion):
    return dict(name='Shape',source='explicit',reason='Required field',
                action=dict(type='http_request',method='GET',path='/item'),assertions=[assertion])


class JsonShapeTests(unittest.TestCase):
    def check(self, assertion, value, verdict):
        s=scenario(assertion); o=dict(type='http_response',status=200,json=value)
        before=copy.deepcopy((s,o))
        result=verify_observation(s,o)
        self.assertEqual(result['verdict'],verdict)
        self.assertEqual((s,o),before)
        return result['assertions'][0]

    def test_exists(self):
        for value in (None,True,1,'secret',{},[]):
            r=self.check(dict(type='json_exists',path='item.id'),{'item':{'id':value}},'PASS')
            self.assertIs(r['observed'],True)
            self.assertNotIn('secret',str(r))

    def test_missing_exists(self):
        for value in ({}, {'item':{}}, {'item':None}, {'item':[]}, None):
            r=self.check(dict(type='json_exists',path='item.id'),value,'FAIL')
            self.assertIs(r['observed'],False)

    def test_type_matrix(self):
        for value, types in ((1,('integer','number')), (1.0,('integer','number')),
                             (1.5,('number',)), (True,('boolean',)), (False,('boolean',)),
                             (None,('null',)), ('secret',('string',)), ({},()), ([],())):
            for expected in ('string','number','integer','boolean','null'):
                with self.subTest(value=value,expected=expected):
                    r=self.check(dict(type='json_type',path='id',equals=expected),{'id':value},
                                 'PASS' if expected in types else 'FAIL')
                    self.assertNotIn('observed',r)
                    self.assertNotIn('secret',str(r))

    def test_missing_type(self):
        for value in ({}, {'item':{}}, {'item':False}):
            self.check(dict(type='json_type',path='item.id',equals='integer'),value,'UNVERIFIED')

    def test_unavailable_json(self):
        for assertion in (dict(type='json_exists',path='id'),dict(type='json_type',path='id',equals='integer')):
            for o in (None, {}, dict(type='http_response',status=200),
                      dict(type='http_response',status=True,json={'id':1}),
                      dict(type='http_response',status=200,json={'id':float('nan')}),
                      dict(type='http_response',status=200,json={'id':'x'*(MAX_JSON_TEXT_CHARS+1)})):
                self.assertEqual(verify_observation(scenario(assertion),o)['verdict'],'UNVERIFIED')

    def test_schema_exactness(self):
        for a in (dict(type='json_exists',path='id'),dict(type='json_type',path='id',equals='integer')):
            validate_scenario(scenario(a))
            for key in a:
                bad=dict(a); del bad[key]
                with self.assertRaises(ValueError): validate_scenario(scenario(bad))
            for key in ('extra','command','cwd','covered'):
                with self.assertRaises(ValueError): validate_scenario(scenario({**a,key:True}))
        with self.assertRaises(ValueError):
            validate_scenario(scenario(dict(type='json_exists',path='id',equals=True)))

    def test_unsupported_types(self):
        for expected in ('object','array','bool','',None,True,{},'x'*40000):
            with self.assertRaises(ValueError):
                validate_scenario(scenario(dict(type='json_type',path='id',equals=expected)))

    def test_path_bounds(self):
        for kind in ('json_exists','json_type'):
            a=dict(type=kind,path='id')
            if kind=='json_type': a['equals']='integer'
            for path in ('',' ','.id','id.','a..b','a. .b',None,'x'*(MAX_JSON_ASSERTION_PATH_CHARS+1)):
                with self.assertRaises(ValueError): validate_scenario(scenario({**a,'path':path}))
            validate_scenario(scenario({**a,'path':'x'*MAX_JSON_ASSERTION_PATH_CHARS}))

    def test_bounded_evidence(self):
        path='x'*1000
        r=self.check(dict(type='json_type',path=path,equals='string'),{path:'secret'},'PASS')
        self.assertEqual(len(r['path']),512)
        self.assertTrue(r['path_truncated'])
        self.assertNotIn('secret',str(r))

    def test_status_and_legacy_compatibility(self):
        s=scenario(dict(type='json_exists',path='id'))
        s['assertions'].insert(0,dict(type='status',equals=200))
        r=verify_observation(s,dict(type='http_response',status=200))
        self.assertEqual([a['verdict'] for a in r['assertions']],['PASS','UNVERIFIED'])
        self.check(dict(type='json_field',path='id',equals=None),{},'UNVERIFIED')

    def test_combined_missing(self):
        s=scenario(dict(type='json_exists',path='id'))
        s['assertions'].append(dict(type='json_type',path='id',equals='integer'))
        r=verify_observation(s,dict(type='http_response',status=200,json={}))
        self.assertEqual(r['verdict'],'FAIL')
        self.assertEqual([a['verdict'] for a in r['assertions']],['FAIL','UNVERIFIED'])

    def test_duplicate_key_policy(self):
        with self.assertRaises(ValueError):
            json.loads('{"id":1,"id":2}',object_pairs_hook=_pairs)

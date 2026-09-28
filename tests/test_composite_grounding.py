"""Provider-boundary tests; fake providers do not establish reasoning quality."""
import copy
import json
import unittest
from unittest.mock import Mock, patch
from agentguard.grounding import ground_scenarios, GROUNDING_INSTRUCTIONS


def plan():
    return dict(explicit_requirements=['Accept both limits'],inferred_behaviors=[],ambiguities=[],
        scenarios=[dict(name='Limits',source='explicit',reason='Both limits required',
                        behavior='Accept values 10 and 20 and return integer id')])


def grounded(n=2):
    return [{**plan()['scenarios'][0], 'action':dict(type='composite',children=[
        dict(label=f'limit-{i}',action=dict(type='http_request',method='POST',path='/limits',json={'value':v}),
             assertions=[dict(type='status',equals=200),dict(type='json_exists',path='id'),
                         dict(type='json_type',path='id',equals='integer')])
        for i,v in enumerate((10,20,15)[:n])])}]

CONTEXT='POST /limits accepts JSON value. Values 10 and 20 return HTTP 200 with generated integer id. Each request is independent.'


class CompositeGroundingTests(unittest.TestCase):
    def invoke(self, output, p=None, context=CONTEXT):
        provider=Mock(return_value=output)
        result=ground_scenarios(p or plan(),context,grounding_provider=provider)
        provider.assert_called_once()
        return result

    def test_valid_two(self):
        result=grounded(); before=copy.deepcopy(result)
        self.assertEqual(self.invoke(result),before)
        self.assertEqual([c['label'] for c in result[0]['action']['children']],['limit-0','limit-1'])

    def test_valid_three(self):
        p=plan(); p['scenarios'][0]['behavior']='Accept values 10, 15 and 20 and return integer id'
        result=grounded(3); result[0]['behavior']=p['scenarios'][0]['behavior']
        self.assertEqual(self.invoke(result,p,CONTEXT+' Value 15 also returns 200 and integer id.'),result)

    def test_identity(self):
        for field in ('name','source','reason','behavior'):
            result=grounded(); result[0][field]='inferred' if field=='source' else 'Changed'
            with self.assertRaises(ValueError): self.invoke(result)

    def test_top_level_split_merge_order(self):
        with self.assertRaises(ValueError): self.invoke(grounded()*2)
        p=plan(); other=copy.deepcopy(p['scenarios'][0]); other['name']='Other'; p['scenarios'].append(other)
        with self.assertRaises(ValueError): self.invoke(grounded(),p)
        result=grounded()*2; result=copy.deepcopy(result); result[1]['name']='Other'
        with self.assertRaises(ValueError): self.invoke(result[::-1],p)

    def test_legacy_shapes_byte_compatible(self):
        for action in (dict(type='http_request',method='GET',path='/'),
                       dict(type='test_command',command=['python3','-m','unittest']),
                       dict(type='unsupported',explanation='Missing evidence'),
                       dict(type='registered_check',check_id='trusted.id')):
            leaf={k:v for k,v in plan()['scenarios'][0].items() if k!='behavior'}
            leaf['action']=action
            if action['type']=='http_request': leaf['assertions']=[dict(type='status',equals=200)]
            before=json.dumps([leaf])
            self.assertEqual(json.dumps(self.invoke([leaf])),before)
            self.assertNotIn('behavior',leaf)
            leaf['behavior']='not allowed'
            with self.assertRaises(ValueError): self.invoke([leaf])

    def test_insufficient_evidence_and_ambiguity_forwarded(self):
        for context,ambiguities in (('Callable only',[]),('POST /limits; no documented input values',[]),
                                    (CONTEXT,['Upper limit policy is undecided'])):
            p=plan(); p['ambiguities']=ambiguities
            output=[{k:v for k,v in p['scenarios'][0].items() if k!='behavior'}]
            output[0]['action']=dict(type='unsupported',explanation='Evidence or policy is insufficient')
            def provider(request):
                self.assertEqual(request['repository_context'],context)
                self.assertEqual(request['planner_output']['ambiguities'],ambiguities)
                return output
            self.assertEqual(ground_scenarios(p,context,grounding_provider=provider),output)

    def test_unsupported_child(self):
        result=grounded(); result[0]['action']['children'][1]=dict(label='upper',action=dict(type='unsupported',explanation='Upper response not documented'))
        self.assertEqual(self.invoke(result),result)

    def test_invalid_assertions(self):
        for assertion in (dict(type='json_type',path='id',equals='array'),
                          dict(type='json_exists',path='a..b')):
            result=grounded(); result[0]['action']['children'][0]['assertions']=[assertion]
            with self.assertRaises(ValueError): self.invoke(result)

    def test_child_bounds_and_kinds(self):
        for action in (grounded()[0]['action'],dict(type='registered_check',check_id='x'),dict(type='test_command',command=['x'])):
            result=grounded(); result[0]['action']['children'][0]['action']=action
            with self.assertRaises(ValueError): self.invoke(result)
        for count in (0,1,4):
            result=grounded(); result[0]['action']['children']=(result[0]['action']['children']*2)[:count]
            with self.assertRaises(ValueError): self.invoke(result)
        result=grounded(); result[0]['action']['children'][1]['label']='limit-0'
        with self.assertRaises(ValueError): self.invoke(result)

    def test_size(self):
        result=grounded(); result[0]['action']['children'][0]['action']['json']['large']='x'*32000
        with self.assertRaises(ValueError): self.invoke(result)

    def test_workflow_fields(self):
        for field in ('variables','from_child','retry','branches','loops','setup','cookie_from','behavior'):
            result=grounded(); result[0]['action']['children'][0][field]='injected'
            with self.assertRaises(ValueError): self.invoke(result)

    def test_conservative_instructions(self):
        for text in ('SAME parent behavior','No second-round planning','No weaker evidence',
                     'more than 3 observations','never\nfiller','Do not merge unrelated',
                     'No nesting','create -> fetch-by-returned-ID','cookie/session workflow',
                     'retries, branches, loops','Do not encode alternative interpretations',
                     'not proof that the decomposition was semantically complete',
                     'legacy standalone','json_exists','json_type'):
            self.assertIn(text,GROUNDING_INSTRUCTIONS)

    def test_defensive_copy_and_no_io(self):
        p=plan(); before=copy.deepcopy(p)
        def provider(request):
            request['planner_output']['scenarios'][0]['behavior']='changed'
            return grounded()
        with patch('builtins.open',side_effect=AssertionError('read')),patch('subprocess.Popen',side_effect=AssertionError('execution')):
            result=ground_scenarios(p,CONTEXT,grounding_provider=provider)
        self.assertEqual(p,before)
        self.assertEqual(result[0]['behavior'],p['scenarios'][0]['behavior'])

    def test_invalid_output_not_repaired_or_retried(self):
        provider=Mock(return_value=grounded(1))
        with self.assertRaises(ValueError): ground_scenarios(plan(),CONTEXT,grounding_provider=provider)
        provider.assert_called_once()

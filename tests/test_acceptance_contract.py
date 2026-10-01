"""Offline tests of scenario review, not authentication or semantic coverage."""
from copy import deepcopy
from dataclasses import FrozenInstanceError
import unittest
from unittest.mock import Mock

from agentguard.acceptance_contract import PlanningProposal, create_proposal, build_contract
from agentguard.planner import plan_acceptance
from agentguard.grounding import ground_scenarios


def plan(sources=('explicit', 'inferred')):
    return dict(explicit_requirements=['Original requirement'],
                inferred_behaviors=['Unlinked suggestion'], ambiguities=['Unresolved decision'],
                scenarios=[dict(name=chr(65+i), behavior=f'Behavior {i}', reason=f'Reason {i}',
                                source=source) for i, source in enumerate(sources)])


def decision(proposal, index=1, state='ACCEPTED'):
    return dict(revision=proposal.revision,
                scenario_id=build_contract(proposal)['reviews'][index]['scenario_id'], state=state)


class AcceptanceContractTests(unittest.TestCase):
    def test_explicit_only(self):
        p = plan(('explicit', 'explicit'))
        c = build_contract(create_proposal(p))
        self.assertEqual(c['selected_plan'], p)
        self.assertTrue(all(r['included'] and r['review_state'] is None for r in c['reviews']))

    def test_inferred_defaults_pending(self):
        c = build_contract(create_proposal(plan()))
        self.assertEqual(c['reviews'][1]['review_state'], 'PENDING')
        self.assertFalse(c['reviews'][1]['included'])
        self.assertEqual(len(c['selected_plan']['scenarios']), 1)

    def test_accept_preserves_all_scenario_fields(self):
        p = plan(); proposal = create_proposal(p)
        c = build_contract(proposal, [decision(proposal)])
        self.assertEqual(c['selected_plan'], p)
        self.assertEqual(c['selected_plan']['scenarios'][1]['source'], 'inferred')

    def test_dismiss_and_pending_excluded(self):
        p = create_proposal(plan())
        for state in ('DISMISSED', 'PENDING'):
            c = build_contract(p, [decision(p, state=state)])
            self.assertEqual(c['reviews'][1]['review_state'], state)
            self.assertEqual(len(c['selected_plan']['scenarios']), 1)

    def test_mixed_order(self):
        p = create_proposal(plan(('explicit', 'inferred', 'explicit', 'inferred', 'inferred')))
        c = build_contract(p, [decision(p, 4), decision(p, 3, 'DISMISSED'), decision(p, 1)])
        self.assertEqual([s['name'] for s in c['selected_plan']['scenarios']], list('ABCE'))
        self.assertEqual([r['position'] for r in c['reviews']], list(range(5)))

    def test_unknown_id(self):
        p = create_proposal(plan()); d = decision(p); d['scenario_id'] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'Unknown'): build_contract(p, [d])

    def test_stale_revision(self):
        p = create_proposal(plan()); d = decision(p); d['revision'] = 'old'
        with self.assertRaisesRegex(ValueError, 'revision'): build_contract(p, [d])

    def test_any_proposal_content_change_invalidates_decisions(self):
        original = plan(); p = create_proposal(original); d = decision(p)
        for field in ('name', 'behavior', 'reason', 'source'):
            changed = deepcopy(original)
            changed['scenarios'][1][field] = 'explicit' if field == 'source' else 'Changed'
            with self.assertRaises(ValueError): build_contract(create_proposal(changed), [d])
        for field in ('explicit_requirements', 'inferred_behaviors', 'ambiguities'):
            changed = deepcopy(original); changed[field].append('Changed')
            with self.assertRaises(ValueError): build_contract(create_proposal(changed), [d])
        changed = deepcopy(original); changed['scenarios'].reverse()
        with self.assertRaises(ValueError): build_contract(create_proposal(changed), [d])

    def test_invalid_review_states_and_verdicts(self):
        p = create_proposal(plan())
        for state in ('PASS', 'FAIL', 'UNVERIFIED', 'accepted', '', None, True, [], {}):
            with self.subTest(state=state), self.assertRaises(ValueError):
                build_contract(p, [decision(p, state=state)])

    def test_explicit_decisions_and_origin_tampering_rejected(self):
        p = create_proposal(plan())
        with self.assertRaisesRegex(ValueError, 'Explicit'): build_contract(p, [decision(p, 0)])
        for key in ('source', 'behavior', 'coverage_authorized', 'verdict'):
            d = decision(p); d[key] = 'explicit'
            with self.assertRaises(ValueError): build_contract(p, [d])

    def test_no_mutation_or_mutable_aliases(self):
        original = plan(); saved = deepcopy(original); p = create_proposal(original)
        ds = [decision(p)]; saved_ds = deepcopy(ds); c = build_contract(p, ds)
        self.assertEqual(original, saved); self.assertEqual(ds, saved_ds)
        original['scenarios'][0]['name'] = 'Changed externally'
        c['selected_plan']['scenarios'][0]['name'] = 'Changed projection'
        c['reviews'][0]['name'] = 'Changed review'
        c['selected_plan']['ambiguities'].clear()
        self.assertEqual(p.plan, saved)
        exposed = p.plan; exposed['scenarios'].clear()
        self.assertEqual(p.plan, saved)
        with self.assertRaises(FrozenInstanceError): p.canonical_plan = '{}'

    def test_duplicate_names_have_distinct_stable_ids(self):
        value = plan(('inferred', 'inferred')); value['scenarios'][1]['name'] = 'A'
        p = create_proposal(value); reviews = build_contract(p)['reviews']
        self.assertNotEqual(reviews[0]['scenario_id'], reviews[1]['scenario_id'])
        self.assertEqual(build_contract(p)['reviews'], reviews)
        c = build_contract(p, [decision(p, 1)])
        self.assertEqual(c['selected_plan']['scenarios'], [value['scenarios'][1]])

    def test_canonical_key_order_does_not_change_revision(self):
        value = plan(); reordered = dict(reversed(list(value.items())))
        reordered['scenarios'] = [dict(reversed(list(s.items()))) for s in value['scenarios']]
        self.assertEqual(create_proposal(value), create_proposal(reordered))

    def test_empty_scenarios_and_metadata_preserved(self):
        value = plan(())
        c = build_contract(create_proposal(value))
        self.assertEqual(c['reviews'], []); self.assertEqual(c['selected_plan'], value)

    def test_legacy_planner_and_grounding_compatibility_offline(self):
        value = plan()
        validated = plan_acceptance('Original task', 'Context', reasoning_provider=Mock(return_value=value))
        p = create_proposal(validated)
        selected = build_contract(p, [decision(p)])['selected_plan']
        responses = [dict(name=s['name'], reason=s['reason'], source=s['source'],
                          action=dict(type='unsupported', explanation='No supported observation'))
                     for s in selected['scenarios']]
        provider = Mock(return_value=responses)
        self.assertEqual(ground_scenarios(selected, 'Context', grounding_provider=provider), responses)
        provider.assert_called_once()
        self.assertEqual(provider.call_args.args[0]['planner_output']['ambiguities'], value['ambiguities'])

    def test_malformed_decision_envelopes(self):
        p = create_proposal(plan()); d = decision(p)
        for ds in ({}, (), [None], [{}], [dict(d, extra=True)], [d, d],
                   [dict(d, scenario_id=[])], [dict(d, revision=None)]):
            with self.subTest(ds=ds), self.assertRaises(ValueError): build_contract(p, ds)

    def test_malformed_proposals(self):
        for value in (None, {}, dict(plan(), extra=True)):
            with self.assertRaises(ValueError): create_proposal(value)
        for value in ('{}', 'not JSON', None, '{"scenarios": []}'):
            with self.assertRaises(ValueError): PlanningProposal(value)
        with self.assertRaises(ValueError): build_contract(plan())

    def test_review_revision_does_not_silently_carry_state(self):
        p = create_proposal(plan())
        self.assertTrue(build_contract(p, [decision(p)])['reviews'][1]['included'])
        self.assertFalse(build_contract(p)['reviews'][1]['included'])
        self.assertFalse(build_contract(p, [decision(p, state='PENDING')])['reviews'][1]['included'])


if __name__ == '__main__':
    unittest.main()

"""Pure scenario-level product-intent review; no execution or trust grants.

Use create_proposal(plan), then build_contract(proposal, decisions). Decisions are
trusted caller input, never provider output. Each decision has exactly revision,
scenario_id, state. Omitted inferred decisions default to PENDING. Explicit items
have review_state=None and cannot receive decisions. The returned selected_plan
is suitable for the existing ground_scenarios interface; its descriptive lists
remain unchanged, not filtered or mapped to scenarios.

A fingerprint binds planner content only, not task/context files, reviewer identity,
execution permission, registered coverage, or input-derivation authority. This is
not authentication. The future application must obtain decisions from the user.
"""

from dataclasses import dataclass
import hashlib
import json

from .planner import _validate_plan


@dataclass(frozen=True)
class PlanningProposal:
    """Immutable canonical JSON snapshot; construct through create_proposal.

    Direct construction is validated too. plan returns a fresh decoded dictionary,
    so callers cannot change the snapshot through nested mutable references.
    """

    canonical_plan: str

    def __post_init__(self):
        if type(self.canonical_plan) is not str:
            raise ValueError('Proposal must contain canonical planner JSON')
        try:
            plan = json.loads(self.canonical_plan)
            _validate_plan(plan)
            if _canonical(plan) != self.canonical_plan:
                raise ValueError('Proposal JSON must be canonical')
        except (TypeError, ValueError, RecursionError) as error:
            raise ValueError('Proposal must contain valid canonical planner JSON') from error

    @property
    def revision(self):
        return hashlib.sha256(('agentguard-planning-proposal-v1\n' +
                               self.canonical_plan).encode('utf-8')).hexdigest()

    @property
    def plan(self):
        return json.loads(self.canonical_plan)


def _canonical(plan):
    return json.dumps(plan, sort_keys=True, ensure_ascii=True, allow_nan=False,
                      separators=(',', ':'))


def create_proposal(planner_output: dict) -> PlanningProposal:
    """Validate and snapshot the complete plan without mutation or normalization.

    Dictionary key order is irrelevant; list order and every string are preserved.
    Changes to any planner list or scenario invalidate all prior decision IDs.
    """
    _validate_plan(planner_output)
    return PlanningProposal(_canonical(planner_output))


def build_contract(proposal: PlanningProposal, decisions=None) -> dict:
    """Return revision, scenario reviews and an ordered selected_plan projection.

    decisions is a list of at most one exact record per inferred scenario:
    {revision: proposal.revision, scenario_id: '<revision>:scenario:<1-based index>',
     state: 'PENDING' | 'ACCEPTED' | 'DISMISSED'}.
    Unknown/stale/duplicate records, explicit decisions and extra fields fail closed.
    Call again with the complete desired decision set to revise a review; there is
    no mutable session, history merge, implicit approval or ambiguity resolution.
    """
    if type(proposal) is not PlanningProposal:
        raise ValueError('Expected a PlanningProposal')
    plan = proposal.plan
    revision = proposal.revision
    reviews = [dict(scenario_id=f'{revision}:scenario:{index + 1}',
                    position=index, **scenario,
                    review_state=None if scenario['source'] == 'explicit' else 'PENDING',
                    included=scenario['source'] == 'explicit')
               for index, scenario in enumerate(plan['scenarios'])]
    by_id = {item['scenario_id']: item for item in reviews}
    if decisions is None:
        decisions = []
    if type(decisions) is not list or len(decisions) > len(reviews):
        raise ValueError('Decisions must be a bounded list with no duplicate scenarios')
    seen = set()
    for decision in decisions:
        if type(decision) is not dict or set(decision) != {'revision', 'scenario_id', 'state'}:
            raise ValueError('Decision must contain exactly revision, scenario_id, state')
        if type(decision['revision']) is not str or decision['revision'] != revision:
            raise ValueError('Decision belongs to a different proposal revision')
        scenario_id = decision['scenario_id']
        if type(scenario_id) is not str or scenario_id not in by_id:
            raise ValueError('Unknown scenario ID')
        if scenario_id in seen:
            raise ValueError('Duplicate scenario decision')
        seen.add(scenario_id)
        item = by_id[scenario_id]
        if item['source'] != 'inferred':
            raise ValueError('Explicit scenarios cannot receive review decisions')
        state = decision['state']
        if type(state) is not str or state not in ('PENDING', 'ACCEPTED', 'DISMISSED'):
            raise ValueError('Invalid review state')
        item['review_state'] = state
        item['included'] = state == 'ACCEPTED'
    # Keep requirements/inferences/ambiguities intact as unlinked descriptive data.
    plan['scenarios'] = [scenario for scenario, review in zip(plan['scenarios'], reviews)
                         if review['included']]
    _validate_plan(plan)
    return dict(revision=revision, reviews=reviews, selected_plan=plan)

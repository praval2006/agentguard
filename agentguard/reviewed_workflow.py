"""Two-stage review orchestration. No new execution or verdict semantics.

Artifacts/decisions are trusted local caller inputs, not model authority. Integrity
checks detect inconsistent edits, not an attacker rewriting all content and hashes.
The application remains responsible for obtaining decisions from a human.
"""
from copy import deepcopy
import hashlib
import json

from .acceptance_contract import create_proposal, build_contract
from .planner import MAX_TEXT_CHARS, plan_acceptance
from .grounding import ground_scenarios, _validate_input
from .acceptance import run_acceptance

REVIEW_SCHEMA = 'agentguard.review.v1'
MAX_ARTIFACT_CHARS = 1_048_576


def _context_hash(context):
    if type(context) is not str or not context.strip() or len(context) > MAX_TEXT_CHARS:
        raise ValueError('Context must be nonblank text within the existing input bound')
    return hashlib.sha256(context.encode('utf-8')).hexdigest()


def _json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                      separators=(',', ':'))


def prepare_review(task_text, repository_context, *, reasoning_provider):
    """One validated planner call, then a persistable default review; never ground.

    The context hash binds resume to the same text. No context, credentials, task
    file path, timestamps or provider configuration are added to the artifact.
    Planner prose itself is caller data and may be sensitive; store accordingly.
    """
    context_hash = _context_hash(repository_context)
    plan = plan_acceptance(task_text, repository_context, reasoning_provider=reasoning_provider)
    # Ensure a prepared plan also fits the existing grounder's input bounds.
    _validate_input(plan, repository_context)
    proposal = create_proposal(plan)
    artifact = dict(schema=REVIEW_SCHEMA, proposal=proposal.plan,
                    revision=proposal.revision, context_sha256=context_hash,
                    reviews=build_contract(proposal)['reviews'])
    if len(_json(artifact)) > MAX_ARTIFACT_CHARS:
        raise ValueError('Review artifact exceeds bound')
    return artifact


def validate_review(artifact, repository_context):
    """Reconstruct proposal and recompute all derived metadata; no provider calls."""
    context_hash = _context_hash(repository_context)
    if type(artifact) is not dict or set(artifact) != {
            'schema', 'proposal', 'revision', 'context_sha256', 'reviews'}:
        raise ValueError('Invalid review artifact fields')
    if artifact['schema'] != REVIEW_SCHEMA or artifact['context_sha256'] != context_hash:
        raise ValueError('Review version or context mismatch')
    if len(_json(artifact)) > MAX_ARTIFACT_CHARS:
        raise ValueError('Review artifact exceeds bound')
    _validate_input(artifact['proposal'], repository_context)
    proposal = create_proposal(artifact['proposal'])
    if artifact['revision'] != proposal.revision:
        raise ValueError('Review proposal revision mismatch')
    # Canonical comparison distinguishes booleans from integer lookalikes.
    if _json(artifact['reviews']) != _json(build_contract(proposal)['reviews']):
        raise ValueError('Stored review metadata does not match the proposal')
    return proposal


def resume_reviewed(artifact, decisions, repository_context, *, grounding_provider,
                    base_url=None, recorder=None, repository_root=None,
                    registry=None, coverage_authorizations=None, derivation_policy=None):
    """Validate review/decisions before grounding only selected scenarios once.

    No planning occurs here. Caller-supplied execution/derivation authorities stay
    separate from decisions. Return original proposal, reviewed contract, grounded
    scenarios and the unmodified acceptance result. Excluded scenarios get no result.
    """
    proposal = validate_review(artifact, repository_context)
    contract = build_contract(proposal, decisions)
    selected = deepcopy(contract['selected_plan'])
    # No list-to-scenario mapping exists. Do not leak unapproved suggestions via
    # this free-text list. Accepted intent remains in selected scenario content.
    selected['inferred_behaviors'] = []
    grounded = ground_scenarios(selected, repository_context,
                               grounding_provider=grounding_provider,
                               derivation_policy=derivation_policy)
    result = run_acceptance(grounded, base_url=base_url, recorder=recorder,
                            repository_root=repository_root, registry=registry,
                            coverage_authorizations=coverage_authorizations)
    return dict(revision=proposal.revision, proposal=proposal.plan, contract=contract,
                grounded=grounded, verification=result)

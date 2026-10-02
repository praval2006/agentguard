"""Finite input derivations from caller-reviewed constraints, never model authority.

The caller reviews source meaning and excludes identity/domain/stateful fields.
Context hashes and quotations bind that review to input, not prove its semantics.
No I/O, source parsing, execution, or verdict computation occurs here.
"""
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import re

MAX_INTEGER = 2**31 - 1
MAX_FACTS = 32
MAX_DERIVATIONS = 8
TYPES = ('string', 'integer', 'number', 'boolean', 'null')
REPRESENTATIVES = {'string': 'agentguard-test', 'integer': 0, 'number': 0.5,
                   'boolean': False, 'null': None}
RULES = ('below_inclusive_lower_bound', 'above_inclusive_upper_bound',
         'blank_string', 'whitespace_string', 'wrong_primitive_type',
         'neutral_nonblank_text')


def _text(value, limit, label):
    if type(value) is not str or not value.strip() or len(value) > limit:
        raise ValueError('Invalid ' + label)


def _hash(value):
    if type(value) is not str or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('Invalid context hash')


@dataclass(frozen=True)
class InputConstraint:
    """Trusted review of one non-identity top-level JSON input field.

    value_class is plain_scalar or arbitrary_text, never a resource/domain value.
    Bounds are explicitly inclusive. quote must appear in the supplied context.
    """
    id: str
    method: str
    path: str
    field: str
    quote: str
    expected_type: str
    value_class: str
    lower: int | None = None
    upper: int | None = None
    nonblank: bool = False

    def __post_init__(self):
        for name, limit in (('id', 128), ('field', 128), ('quote', 512), ('path', 2048)):
            _text(getattr(self, name), limit, name)
        if not re.fullmatch('[A-Za-z_][A-Za-z0-9_]*', self.field):
            raise ValueError('Only simple top-level JSON fields are supported')
        if (self.method not in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')
                or not self.path.startswith('/') or self.path.startswith('//')
                or any(ord(c) <= 32 or ord(c) >= 127 or c in '\\#{}?' for c in self.path)):
            raise ValueError('Constraint requires a concrete method and path')
        if self.expected_type not in TYPES or self.value_class not in ('plain_scalar', 'arbitrary_text'):
            raise ValueError('Unsupported input type or semantic class')
        if type(self.nonblank) is not bool:
            raise ValueError('nonblank must be boolean')
        if self.nonblank and self.expected_type != 'string':
            raise ValueError('Nonblank applies only to strings')
        if self.value_class == 'arbitrary_text' and (self.expected_type != 'string' or not self.nonblank):
            raise ValueError('Arbitrary text requires explicitly nonblank string input')
        for bound in (self.lower, self.upper):
            if bound is not None and (type(bound) is not int or abs(bound) > MAX_INTEGER
                                      or self.expected_type != 'integer'):
                raise ValueError('Bounds require bounded integer constraints')
        if self.lower is not None and self.upper is not None and self.lower > self.upper:
            raise ValueError('Inverted bounds')


@dataclass(frozen=True)
class DerivationPolicy:
    """Separate caller authority, immutable and specific to exact context bytes."""
    context_sha256: str
    constraints: tuple

    def __post_init__(self):
        _hash(self.context_sha256)
        if type(self.constraints) is not tuple or len(self.constraints) > MAX_FACTS:
            raise ValueError('Constraints must be a bounded tuple')
        ids, targets = set(), set()
        for fact in self.constraints:
            if type(fact) is not InputConstraint:
                raise ValueError('Only reviewed InputConstraint records are accepted')
            target = (fact.method, fact.path, fact.field)
            if fact.id in ids or target in targets:
                raise ValueError('Duplicate constraint identity or target')
            ids.add(fact.id)
            targets.add(target)

    def validate_context(self, context):
        if hashlib.sha256(context.encode('utf-8')).hexdigest() != self.context_sha256:
            raise ValueError('Policy context is stale')
        if any(fact.quote not in context for fact in self.constraints):
            raise ValueError('Constraint quotation is absent from context')

    def provider_facts(self):
        return [dict(fact.__dict__) for fact in self.constraints]


def _construct(fact, rule, representative=None):
    if rule not in RULES:
        raise ValueError('Unsupported derivation rule')
    source = None
    if rule in RULES[:2]:
        source = fact.lower if rule == RULES[0] else fact.upper
        if source is None:
            raise ValueError('Required inclusive integer bound is unavailable')
        value = source + (-1 if rule == RULES[0] else 1)
        if abs(value) > MAX_INTEGER:
            raise ValueError('Derived integer exceeds bound')
    elif rule in ('blank_string', 'whitespace_string'):
        if fact.expected_type != 'string' or not fact.nonblank:
            raise ValueError('Nonblank text constraint required')
        value = '' if rule == 'blank_string' else '   '
    elif rule == 'neutral_nonblank_text':
        if fact.value_class != 'arbitrary_text':
            raise ValueError('Reviewed arbitrary nonblank text required')
        value = 'agentguard-test'
    else:
        if representative not in TYPES:
            raise ValueError('Unknown primitive representative')
        if representative == fact.expected_type or (fact.expected_type == 'number' and representative == 'integer'):
            raise ValueError('Representative must have an incompatible type')
        value = REPRESENTATIVES[representative]
    return value, source


def derive(request, *, policy, context, action):
    """Request holds a rule/reference, never a concrete value or source assertion."""
    if type(policy) is not DerivationPolicy:
        raise ValueError('Caller-reviewed derivation policy is unavailable')
    policy.validate_context(context)
    if type(request) is not dict:
        raise ValueError('Derivation request must be an object')
    keys = {'field', 'rule', 'fact_id'}
    if request.get('rule') == 'wrong_primitive_type':
        keys.add('representative')
    if set(request) != keys:
        raise ValueError('Invalid derivation request fields')
    fact = next((f for f in policy.constraints if f.id == request['fact_id']), None)
    if fact is None or (action.get('type'), action.get('method'), action.get('path'), request['field']) != (
            'http_request', fact.method, fact.path, fact.field):
        raise ValueError('Constraint does not authorize this input target')
    value, source = _construct(fact, request['rule'], request.get('representative'))
    provenance = {'kind': 'derived' if source is not None else 'synthetic',
                  'rule': request['rule'], 'field': fact.field, 'fact_id': fact.id,
                  'constraint': dict(fact.__dict__), 'context_sha256': policy.context_sha256,
                  'value': value}
    if source is not None:
        provenance['source_value'] = source
    if request['rule'] == 'wrong_primitive_type':
        provenance['representative'] = request['representative']
    return value, provenance


def validate_provenance(action):
    """Check arithmetic/target consistency, NOT caller approval or source truth.

    Serialized provenance is descriptive, not an authorization token. Only grounding
    with separate caller policy establishes the reviewed derivation boundary.
    """
    records = action.get('derivations')
    if type(records) is not list or not 1 <= len(records) <= MAX_DERIVATIONS:
        raise ValueError('Invalid provenance count')
    seen = set()
    for p in records:
        if type(p) is not dict or type(p.get('constraint')) is not dict:
            raise ValueError('Invalid provenance')
        try:
            fact = InputConstraint(**p['constraint'])
        except TypeError as error:
            raise ValueError('Invalid provenance constraint') from error
        keys = {'kind', 'rule', 'field', 'fact_id', 'constraint', 'context_sha256', 'value'}
        if p.get('rule') in RULES[:2]:
            keys.add('source_value')
        if p.get('rule') == 'wrong_primitive_type':
            keys.add('representative')
        if set(p) != keys:
            raise ValueError('Invalid provenance fields')
        _hash(p['context_sha256'])
        value, source = _construct(fact, p['rule'], p.get('representative'))
        if (p['kind'] != ('derived' if source is not None else 'synthetic')
                or p['fact_id'] != fact.id or p['field'] != fact.field
                or fact.field in seen
                or (action.get('method'), action.get('path')) != (fact.method, fact.path)
                or type(p['value']) is not type(value) or p['value'] != value
                or type(action.get('json')) is not dict or fact.field not in action['json']
                or type(action['json'][fact.field]) is not type(value) or action['json'][fact.field] != value):
            raise ValueError('Provenance does not match the derived input')
        if source is not None and (type(p['source_value']) is not int or p['source_value'] != source):
            raise ValueError('Incorrect source bound')
        seen.add(fact.field)


def materialize(candidate, *, policy, context):
    """Compile HTTP input requests; any unjustified leaf becomes unsupported.

    Other schema/identity errors still reach existing validation. No retries, partial
    request success, or derived values in response assertions/paths/headers.
    """
    result = deepcopy(candidate)
    if not isinstance(result, dict):
        return result
    def leaf(record):
        action = record.get('action')
        if not isinstance(action, dict):
            return
        if 'derive' not in action and 'derivations' not in action:
            return
        try:
            if 'derivations' in action:
                raise ValueError('Provider cannot supply provenance')
            requests = action['derive']
            if type(requests) is not list or not 1 <= len(requests) <= MAX_DERIVATIONS:
                raise ValueError('Invalid derivation count')
            if action.get('type') != 'http_request' or type(action.get('json')) is not dict:
                raise ValueError('Only explicit HTTP JSON objects can use derivation')
            body = deepcopy(action['json'])
            records = []
            for request in requests:
                value, provenance = derive(request, policy=policy, context=context, action=action)
                field = provenance['field']
                if field in body:
                    raise ValueError('Derived input must not overwrite a supplied field')
                body[field] = value
                records.append(provenance)
        except (ValueError, TypeError, KeyError):
            record['action'] = {'type': 'unsupported', 'explanation':
                'Input derivation is not justified by the caller-reviewed policy or request contract.'}
            record.pop('assertions', None)
            return
        del action['derive']
        action['json'] = body
        action['derivations'] = records
    action = result.get('action')
    if isinstance(action, dict) and action.get('type') == 'composite':
        children = action.get('children')
        if isinstance(children, list):
            for child in children:
                if isinstance(child, dict):
                    leaf(child)
    elif isinstance(action, dict) and action.get('type') == 'http_sequence':
        steps = action.get('steps')
        if isinstance(steps, list):
            for step in steps:
                if isinstance(step, dict):
                    original = step.get('action')
                    leaf(step)
                    if original is not step.get('action'):
                        # A required step cannot be dropped or replaced by an
                        # independent observation; preserve the entire intent.
                        result['action'] = step['action']
                        result.pop('assertions', None)
                        break
    else:
        leaf(result)
    return result

"""Caller-supplied coverage associations, never model/scenario authority.

Identity is canonical JSON of the entire validated grounded scenario, including
variables. This is not a repository digest, semantic proof, or snapshot approval.
The trusted caller must review the full intended behavior before authorizing it.
"""
from dataclasses import dataclass
import json
from .scenarios import validate_scenario
from .check_registry import Registry

MAX_IDENTITY_CHARS = 32000


def scenario_identity(scenario):
    validate_scenario(scenario)
    text = json.dumps(scenario, sort_keys=True, separators=(',', ':'), allow_nan=False)
    if len(text) > MAX_IDENTITY_CHARS:
        raise ValueError('scenario identity exceeds bound')
    return text


@dataclass(frozen=True)
class CoverageAuthorizations:
    # Immutable triples: canonical scenario identity, check ID, coverage ID.
    entries: tuple

    def __post_init__(self):
        if type(self.entries) is not tuple or len(self.entries) > 100:
            raise ValueError('authorizations must be a bounded tuple')
        seen = set()
        for entry in self.entries:
            if type(entry) is not tuple or len(entry) != 3:
                raise ValueError('authorization must be an identity/check/coverage triple')
            for value, limit in zip(entry, (MAX_IDENTITY_CHARS, 128, 128)):
                if type(value) is not str or not value.strip() or len(value) > limit:
                    raise ValueError('invalid authorization text')
            try:
                scenario = json.loads(entry[0])
                if (scenario_identity(scenario) != entry[0]
                        or scenario['action']['type'] != 'registered_check'):
                    raise ValueError('authorization identity must be canonical registered scenario JSON')
            except (TypeError, KeyError, RecursionError) as error:
                raise ValueError('invalid scenario identity') from error
            if entry[0] in seen:
                raise ValueError('duplicate scenario authorization')
            seen.add(entry[0])


def authorized_registration(scenario, registry, authorizations):
    """Resolve a trusted association without I/O. Fail closed for unavailable data."""
    if type(registry) is not Registry or type(authorizations) is not CoverageAuthorizations:
        return None
    try:
        identity = scenario_identity(scenario)
        entries = [e for e in authorizations.entries if e[0] == identity]
        checks = [c for c in registry.checks if c.id == scenario['action']['check_id']]
        if len(entries) != 1 or len(checks) != 1:
            return None
        check = checks[0]
        if any(type(value) is not str or not value.strip() or len(value) > limit
               for value, limit in ((check.id, 128), (check.coverage.id, 128),
                                    (check.target, 512))):
            return None
        if entries[0][1:] != (check.id, check.coverage.id):
            return None
        return check
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError):
        return None

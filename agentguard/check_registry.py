"""Explicitly caller-approved registry loading; path confinement, not a sandbox.

Neither a file's existence nor coverage metadata proves trust or acceptance
coverage. Callers select the root/location outside model output. No imports of
registered targets, execution, writes, snapshot approvals, or verdicts occur.
Filesystem preflight assumes no concurrent mutation; execution must revalidate.
"""

from dataclasses import dataclass
import json
from pathlib import Path
import re

MAX_CHECKS = 100
MAX_ID_CHARS = 128
MAX_PATH_CHARS = 512
MAX_TARGET_CHARS = 512
MAX_DESCRIPTION_CHARS = 2048
MAX_REGISTRY_BYTES = 262144


@dataclass(frozen=True)
class Coverage:
    id: str
    description: str


@dataclass(frozen=True)
class Registration:
    id: str
    runner: str
    cwd: Path
    target: str
    coverage: Coverage


@dataclass(frozen=True)
class Registry:
    repository_root: Path
    checks: tuple[Registration, ...]


def _shape(value, fields, label):
    if type(value) is not dict or set(value) != set(fields):
        raise ValueError(f'{label} must contain exactly {sorted(fields)}')


def _text(value, limit, label):
    if (type(value) is not str or not value.strip() or len(value) > limit
            or any(ord(c) < 32 or ord(c) == 127 for c in value)):
        raise ValueError(f'{label} must be nonblank bounded text (maximum {limit})')
    return value


def _root(repository_root):
    root = Path(repository_root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('repository root must be a directory')
    return root


def _local(root, value, *, directory):
    _text(value, MAX_PATH_CHARS, 'relative path')
    # Portable slash-separated syntax: reject Windows drives/UNC as well as POSIX escapes.
    if value == '.' and directory:
        return root
    parts = value.split('/')
    if ('\\' in value or ':' in value
            or any(p in ('', '.', '..') or p != p.strip() for p in parts)):
        raise ValueError('path must be a normalized repository-relative path')
    current = root
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise ValueError('symlink path components are forbidden')
    resolved = current.resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise ValueError('path escapes repository root')
    if not (resolved.is_dir() if directory else resolved.is_file()):
        raise ValueError('path has incorrect file type')
    return resolved


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def parse_registry(text, *, repository_root):
    """Parse approved JSON text and validate cwd paths; return immutable data.

    Target syntax suggests one method; actual discovery/cardinality is deferred.
    Coverage is descriptive provenance only, never proof of scenario coverage.
    Missing paths raise OSError; malformed values/path policy raise ValueError.
    """
    if type(text) is not str or len(text.encode('utf-8')) > MAX_REGISTRY_BYTES:
        raise ValueError('registry exceeds byte limit or is not text')
    try:
        data = json.loads(text, object_pairs_hook=_pairs)
    except (RecursionError, json.JSONDecodeError) as error:
        raise ValueError('invalid registry JSON') from error
    root = _root(repository_root)
    _shape(data, ('version', 'checks'), 'registry')
    if type(data['version']) is not int or data['version'] != 1:
        raise ValueError('registry version must be integer 1')
    if type(data['checks']) is not list or len(data['checks']) > MAX_CHECKS:
        raise ValueError('checks must be a bounded list')
    ids, coverage_ids, checks = set(), set(), []
    for check in data['checks']:
        _shape(check, ('id', 'runner', 'cwd', 'target', 'coverage'), 'check')
        check_id = _text(check['id'], MAX_ID_CHARS, 'check id')
        if check['runner'] != 'unittest':
            raise ValueError('only unittest runner is supported')
        target = _text(check['target'], MAX_TARGET_CHARS, 'target')
        if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+\.test[A-Za-z0-9_]*', target):
            raise ValueError('target must name module.Class.test_method')
        coverage = check['coverage']
        _shape(coverage, ('id', 'description'), 'coverage')
        coverage_id = _text(coverage['id'], MAX_ID_CHARS, 'coverage id')
        description = _text(coverage['description'], MAX_DESCRIPTION_CHARS, 'coverage description')
        if check_id in ids or coverage_id in coverage_ids:
            raise ValueError('check and coverage IDs must be unique')
        ids.add(check_id)
        coverage_ids.add(coverage_id)
        cwd = _local(root, check['cwd'], directory=True)
        checks.append(Registration(check_id, 'unittest', cwd, target,
                                   Coverage(coverage_id, description)))
    return Registry(root, tuple(checks))


def load_registry(*, repository_root, registry_path):
    """Load only an explicitly approved root-relative path, with no default search.

    Reject symlinks in all registry path components. Approval is a caller
    obligation, not something inferred from the contents or filename.
    """
    root = _root(repository_root)
    path = _local(root, registry_path, directory=False)
    with path.open('rb') as stream:
        raw = stream.read(MAX_REGISTRY_BYTES + 1)
    if len(raw) > MAX_REGISTRY_BYTES:
        raise ValueError('registry exceeds byte limit')
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError as error:
        raise ValueError('registry must be UTF-8') from error
    return parse_registry(text, repository_root=root)

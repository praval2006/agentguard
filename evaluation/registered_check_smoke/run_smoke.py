"""Run once from the project root: python3 -B -m evaluation.registered_check_smoke.run_smoke."""
import json
from pathlib import Path
from agentguard.acceptance import run_acceptance
from agentguard.check_registry import load_registry
from agentguard.coverage_authorization import CoverageAuthorizations


def main():
    root = Path(__file__).resolve().parent
    output = root / 'result.json'
    if output.exists():
        raise FileExistsError('First result already preserved')
    scenarios = json.loads((root / 'scenarios.json').read_text())
    # These explicit fixture-author approvals are trusted inputs, not model output.
    authorizations = CoverageAuthorizations(tuple(tuple(entry) for entry in
        json.loads((root / 'authorizations.json').read_text())))
    registry = load_registry(repository_root=root, registry_path='checks.json')
    result = run_acceptance(scenarios, repository_root=root, registry=registry,
                            coverage_authorizations=authorizations)
    with output.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

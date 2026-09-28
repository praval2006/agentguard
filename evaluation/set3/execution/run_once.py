"""One-pass frozen Set-3 execution; refuses to overwrite attempt records."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CASES = ('01_profile_display_name', '02_shipping_weight_quote', '03_catalog_lookup',
         '04_promo_preview', '05_notification_preferences')

def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

def stamp():
    return datetime.now(timezone.utc).isoformat()

def run_case(case):
    sys.path.insert(0, str(ROOT))
    from agentguard.acceptance import run_acceptance
    source = ROOT / 'evaluation/set3/grounding' / (case + '.json')
    data = source.read_bytes()
    scenarios = json.loads(data)
    needs_http = any(s['action']['type'] in ('http_request', 'composite') for s in scenarios)
    meta = {'case': case, 'started_at': stamp(), 'input_path': str(source.relative_to(ROOT)),
            'input_sha256': hashlib.sha256(data).hexdigest(), 'orchestrator_calls': 0,
            'fixture_required': needs_http, 'fixture_started': False, 'fixture_closed': False}
    save(OUT / (case + '.attempt.json'), meta)
    try:
        if needs_http:
            sys.path.insert(0, str(ROOT / 'evaluation/set3/cases' / case / 'repository'))
            from server import application_server
            with application_server() as base_url:
                meta.update(fixture_started=True, base_url=base_url)
                meta['orchestrator_calls'] += 1
                result = run_acceptance(scenarios, base_url=base_url)
                save(OUT / (case + '.result.json'), result)
            meta['fixture_closed'] = True
        else:
            meta['orchestrator_calls'] += 1
            result = run_acceptance(scenarios)
            save(OUT / (case + '.result.json'), result)
        assert source.read_bytes() == data
        assert scenarios == json.loads(data)
        meta['completed'] = True
    except Exception as error:
        meta.update(completed=False, infrastructure_error={'type': type(error).__name__, 'message': str(error)})
        raise
    finally:
        meta['finished_at'] = stamp()
        save(OUT / (case + '.metadata.json'), meta)

if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--case' and sys.argv[2] in CASES:
        run_case(sys.argv[2])
    elif len(sys.argv) == 1:
        save(OUT / 'stage_attempt.json', {'started_at': stamp(), 'grounding_checkpoint': 'b981480', 'cases': CASES, 'policy': 'one isolated process and one run_acceptance call per case; no retries'})
        for case in CASES:
            completed = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--case', case], cwd=ROOT, capture_output=True, text=True)
            save(OUT / (case + '.process.json'), {'returncode': completed.returncode, 'stdout': completed.stdout, 'stderr': completed.stderr})
            if completed.returncode:
                raise SystemExit('Stopped after infrastructure error in ' + case + '; no retry')
    else:
        raise SystemExit('Unsupported arguments')

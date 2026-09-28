"""One-shot execution of frozen Set-2 artifacts; no verdict calculation."""
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CHECKPOINT = '66b4de6'
CASES = ('01_roast_temperature', '02_parcel_label', '03_payroll',
         '04_tournament', '05_quiz_attempt')


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integrity():
    files = subprocess.check_output(
        ['git', 'ls-tree', '-r', '--name-only', CHECKPOINT,
         'evaluation/set2', 'evaluation/evaluation_set_2_protocol.md'],
        cwd=ROOT, text=True).splitlines()
    hashes = {}
    for name in files:
        actual = (ROOT / name).read_bytes()
        expected = subprocess.check_output(['git', 'show', CHECKPOINT + ':' + name], cwd=ROOT)
        if actual != expected:
            raise RuntimeError('Frozen input changed: ' + name)
        hashes[name] = hashlib.sha256(actual).hexdigest()
    return hashes


def main():
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT))
    from agentguard.acceptance import run_acceptance
    hashes = integrity()
    save(OUT / 'run_started.json', {'checkpoint': CHECKPOINT, 'frozen_input_sha256': hashes,
                                  'policy': 'One attempt only; refuse to overwrite this marker.'})
    records = []
    for case in CASES:
        input_path = ROOT / 'evaluation/set2/grounding' / (case + '.json')
        scenarios = json.loads(input_path.read_text())
        needs_http = any(s['action']['type'] == 'http_request' or
                         (s['action']['type'] == 'composite' and any(
                             c['action']['type'] == 'http_request'
                             for c in s['action']['children'])) for s in scenarios)
        record = {'case': case, 'execution_attempts': 1, 'run_acceptance_calls': 0,
                  'input_path': str(input_path.relative_to(ROOT)),
                  'input_sha256': hashlib.sha256(input_path.read_bytes()).hexdigest(),
                  'base_url': None, 'startup_succeeded': None, 'shutdown_succeeded': None,
                  'start_method': 'not required', 'infrastructure_notes': [],
                  'caller_configuration': 'Only base_url for HTTP; no registry, authorization, root override or recorder.'}
        manager = None
        entered = False
        repository = ROOT / 'evaluation/set2' / case / 'repository'
        try:
            if needs_http:
                record['start_method'] = str(repository.relative_to(ROOT) / 'server.py') + ':application_server()'
                sys.path.insert(0, str(repository))
                manager = importlib.import_module('server').application_server()
                record['base_url'] = manager.__enter__()
                entered = True
                record['startup_succeeded'] = True
            record['run_acceptance_calls'] = 1
            result = run_acceptance(scenarios, base_url=record['base_url'])
            result_path = OUT / (case + '.result.json')
            record['result_sha256'] = save(result_path, result)
            record['result_path'] = str(result_path.relative_to(ROOT))
        except Exception as error:
            record['infrastructure_notes'].append(type(error).__name__ + ': ' + str(error))
            if needs_http and not entered:
                record['startup_succeeded'] = False
            record['stopped'] = True
        finally:
            if entered:
                try:
                    manager.__exit__(None, None, None)
                    record['shutdown_succeeded'] = True
                except Exception as error:
                    record['shutdown_succeeded'] = False
                    record['infrastructure_notes'].append(type(error).__name__ + ': ' + str(error))
            if needs_http:
                if str(repository) in sys.path:
                    sys.path.remove(str(repository))
                sys.modules.pop('server', None)
                sys.modules.pop('app', None)
            save(OUT / (case + '.execution.json'), record)
            records.append(record)
    final_hashes = integrity()
    save(OUT / 'execution_manifest.json', {'checkpoint': CHECKPOINT,
         'command': 'python3 -B evaluation/set2/execution/run_execution.py',
         'inputs_unchanged_after_shutdown': hashes == final_hashes, 'cases': records})
    print('First execution records and exact results preserved. No retries performed.')


if __name__ == '__main__':
    main()

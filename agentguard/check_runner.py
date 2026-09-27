"""Fixed single-unittest runner. Trusted test code is not sandboxed.

Invoked by absolute path under -I -B. Only the approved cwd is added to sys.path.
The parent owns the result descriptor; stdout is never a result protocol.
"""
import importlib
import inspect
import json
import os
from pathlib import Path
import sys
import unittest


def run(target, cwd):
    facts = dict(status='load_error', tests_run=0, failures=0, errors=0,
                 skips=0, expected_failures=0, unexpected_successes=0)
    try:
        module_name, class_name, method_name = target.rsplit('.', 2)
        module = importlib.import_module(module_name)
        origin = Path(module.__file__).resolve(strict=True)
        if not origin.is_relative_to(cwd):
            return facts
        cls = getattr(module, class_name)
        if not isinstance(cls, type) or not issubclass(cls, unittest.TestCase):
            return facts
        if not Path(inspect.getfile(cls)).resolve().is_relative_to(cwd):
            return facts
        suite = unittest.defaultTestLoader.loadTestsFromName(f'{class_name}.{method_name}', module)
        if unittest.defaultTestLoader.errors:
            return facts
        count = suite.countTestCases()
        if count != 1:
            facts['status'] = 'zero_tests' if count == 0 else 'multiple_tests'
            return facts
        result = unittest.TestResult()
        suite.run(result)
        facts.update(tests_run=result.testsRun, failures=len(result.failures),
                     errors=len(result.errors), skips=len(result.skipped),
                     expected_failures=len(result.expectedFailures),
                     unexpected_successes=len(result.unexpectedSuccesses))
        if result.errors: status = 'test_error'
        elif result.skipped: status = 'skipped'
        elif result.expectedFailures: status = 'expected_failure'
        elif result.unexpectedSuccesses: status = 'unexpected_success'
        elif result.testsRun != 1: status = 'zero_tests' if result.testsRun == 0 else 'multiple_tests'
        elif result.failures: status = 'assertion_failure'
        else: status = 'success'
        facts['status'] = status
    except BaseException:
        facts['status'] = 'load_error'
    return facts


def main():
    target, descriptor = sys.argv[1:]
    cwd = Path.cwd().resolve(strict=True)
    sys.path.insert(0, str(cwd))
    facts = run(target, cwd)
    payload = json.dumps(facts, separators=(',', ':')).encode()
    if len(payload) > 2048:
        raise RuntimeError('Runner result exceeds bound')
    with os.fdopen(int(descriptor), 'wb') as stream:
        stream.write(payload)


if __name__ == '__main__':
    main()

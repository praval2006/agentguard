"""Narrow test execution policy layered on the existing recorded test runner."""

from pathlib import Path

from . import tools
from .scenarios import validate_scenario
from .verifier import verify_observation

_REPO_ROOT = Path(__file__).resolve().parent.parent
_ALLOWED_COMMAND = ("python3", "-m", "unittest", "discover", "-s", "sample_app/tests", "-v")


def _check_root():
    root = _REPO_ROOT.resolve(strict=True)
    sample = root / "sample_app"
    # Check the package and all its entries, including discovery modules/symlinks.
    # This confines discovery inputs, not the behavior of trusted Python test code.
    for path in (sample, sample / "tests", *sample.rglob("*")):
        path.resolve(strict=True).relative_to(root)
    if not sample.is_dir() or not (sample / "tests").is_dir():
        raise ValueError("missing test root")
    # The fixed root itself must not redirect the runner's working directory.
    if sample.resolve() != sample or (sample / "tests").resolve() != sample / "tests":
        raise ValueError("test root is a symlink")
    return sample


def execute_test_scenario(scenario: dict, *, recorder=None) -> dict:
    """Execute only the legacy sample-app unittest form, never caller-selected cwd.

    Actual execution uses sys.executable and -B via tools.run_tests, shell=False,
    a 10-second timeout, and its 4096-byte combined-output evidence limit. The
    existing automatic recorder behavior is preserved (optional recorder override).
    Output capture uses a temporary file: retained evidence is bounded, disk writes
    are not a hard quota. Repository tests are trusted code, not sandboxed code;
    confinement is a preflight check and assumes no concurrent repository mutation.

    Return {execution: {established, reason, command, returncode, timed_out,
    output_truncated}, observation, result}. Raw test output remains in the existing
    recorder only; the new reporting envelope does not duplicate potentially
    sensitive traceback/log text. Policy validation does not prove scenario coverage.
    Invalid scenarios raise ValueError. Infrastructure failures, including recording/capture failure, return UNVERIFIED;
    the existing tool still attempts its normal automatic recording.
    """
    validate_scenario(scenario)
    if scenario["action"]["type"] != "test_command":
        raise ValueError("execute_test_scenario requires a test_command scenario")
    evidence = {"established": False, "reason": None, "command": None,
                "returncode": None, "timed_out": False, "output_truncated": False}

    def finish(observation=None):
        result = verify_observation(scenario, observation)
        if observation is None:
            result["reason"] = evidence["reason"]
        return {"execution": evidence, "observation": observation, "result": result}

    if tuple(scenario["action"]["command"]) != _ALLOWED_COMMAND:
        evidence["reason"] = "Command is not in the explicit allowlist"
        return finish()
    evidence["command"] = list(_ALLOWED_COMMAND)
    try:
        sample = _check_root()
    except (OSError, ValueError, RuntimeError):
        evidence["reason"] = "Allowed test tree is unavailable or escapes repository policy"
        return finish()

    token = tools._ACTIVE_SAMPLE_ROOT.set(sample)
    try:
        event = tools.run_tests(recorder=recorder)
    except OSError:
        evidence["reason"] = "Execution capture or recording could not be established"
        return finish()
    finally:
        tools._ACTIVE_SAMPLE_ROOT.reset(token)
    if (type(event) is not dict or event.get("tool") != "run_tests"
            or event.get("path") != "tests" or type(event.get("timed_out")) is not bool
            or type(event.get("output_truncated")) is not bool):
        evidence["reason"] = "Malformed execution evidence"
        return finish()
    evidence["timed_out"] = event["timed_out"]
    evidence["output_truncated"] = event["output_truncated"]
    if event["timed_out"]:
        evidence["reason"] = "Test process timed out"
        return finish()
    code = event.get("exit_code")
    if type(code) is not int or event.get("status") != ("succeeded" if code == 0 else "failed"):
        evidence["reason"] = "Test execution did not establish a trustworthy return code"
        return finish()
    evidence.update(established=True, returncode=code)
    return finish({"type": "test_result", "returncode": code})

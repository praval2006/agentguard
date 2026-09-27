"""Run the frozen Day-6 grounded inputs through the existing orchestrator."""

import json
from pathlib import Path

from agentguard.acceptance import run_acceptance


def main():
    directory = Path(__file__).resolve().parent / "day6_results"
    outputs = [directory / f"case{number:02d}_acceptance.json"
               for number in range(1, 6)]
    if any(path.exists() for path in outputs):
        raise FileExistsError("Preserved acceptance results already exist")
    for number, output in enumerate(outputs, 1):
        case = f"case{number:02d}"
        scenarios = json.loads(
            (directory / f"{case}_grounded.json").read_text(encoding="utf-8")
        )
        result = run_acceptance(scenarios)
        with output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
        print(json.dumps({
            "case": case,
            "scenario_count": len(scenarios),
            "verdict": result["verdict"],
            "scenario_verdicts": [
                envelope["result"]["verdict"] for envelope in result["results"]
            ],
        }))


if __name__ == "__main__":
    main()

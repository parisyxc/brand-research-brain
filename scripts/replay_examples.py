#!/usr/bin/env python3
"""Replay reviewed payloads into blank Brains; does not rerun model reasoning."""
import argparse
import copy
import datetime as dt
import importlib.util
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "plugins/brand-research-brain/skills"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    instance = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(instance)
    return instance


def run(output):
    init = load("replay_init", SKILLS / "brain-init/scripts/init_brain.py")
    intake = load("replay_intake", SKILLS / "brand-intake/scripts/intake.py")
    checker = load("replay_check", SKILLS / "brand-intake/scripts/check_brain.py")
    output = Path(output).resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError("Replay output must be a new or empty directory")
    output.mkdir(parents=True, exist_ok=True)
    suite = json.loads((ROOT / "examples/validated/cases.json").read_text())
    results = []
    for case in suite:
        brain = output / case["id"]
        date = case.get("date", "2026-10-24")
        init.initialize(brain, name="Example Research Brain", language=case["language"], date=date)
        initial = {str(p.relative_to(brain)): p.read_bytes() for p in brain.rglob("*") if p.is_file()}
        assert init.initialize(brain, date=date)["created"] == []
        assert initial == {str(p.relative_to(brain)): p.read_bytes() for p in brain.rglob("*") if p.is_file()}
        prior_link = None
        statuses = []
        for step in case["steps"]:
            payload = json.loads((ROOT / "examples/validated/payloads" / step["payload"]).read_text())
            for page in payload["pages"]:
                target = brain / page["path"]
                if target.exists():
                    page["expected_sha256"] = intake.digest(target.read_bytes())
                if step.get("rendered_source_link"):
                    page["content"] = page["content"].replace("{{source}}", prior_link)
            result = intake.commit(brain, payload, date, revise=step.get("revise", False))
            assert result["status"] == step["expected_status"], result
            statuses.append(result["status"])
            state = json.loads((brain / ".brb/state.json").read_text())
            prior_link = "[[" + state["sources"][result["source_id"]]["path"][:-3] + "]]"
            before = {str(p.relative_to(brain)): p.read_bytes() for p in brain.rglob("*") if p.is_file()}
            repeated = intake.commit(brain, copy.deepcopy(payload), (dt.date.fromisoformat(date) + dt.timedelta(days=1)).isoformat(), revise=step.get("revise", False))
            assert repeated["status"] == "duplicate"
            assert before == {str(p.relative_to(brain)): p.read_bytes() for p in brain.rglob("*") if p.is_file()}
        check = checker.check(brain)
        assert check["errors"] == [], check
        assert (check["brands"], check["sources"], check["events"]) == tuple(case["expected_counts"]), check
        assert check["pages_by_type"] == case["expected_pages"], check
        profile = json.loads((brain / "brain.json").read_text())
        assert not profile["markets"] and not profile["constraints"]
        results.append({"case": case["id"], "statuses": statuses, **check})
    print(json.dumps({"mode": "deterministic_payload_replay", "results": results}, ensure_ascii=False, indent=2))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="Optional new/empty directory to retain generated Brains")
    args = parser.parse_args()
    if args.output:
        run(args.output)
    else:
        with tempfile.TemporaryDirectory(prefix="brb-replay-") as directory:
            run(directory)


if __name__ == "__main__":
    main()

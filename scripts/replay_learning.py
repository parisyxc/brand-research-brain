#!/usr/bin/env python3
"""Replay the reviewed v0.2 learning example; this does not rerun agent reasoning."""
import copy
import json
from pathlib import Path
import tempfile
from replay_examples import load, ROOT, SKILLS


def run(output):
    init = load("learning_init", SKILLS / "brain-init/scripts/init_brain.py")
    learn = load("learning_save", SKILLS / "brand-intake/scripts/learn.py")
    checker = load("learning_checker", SKILLS / "brand-intake/scripts/check_brain.py")
    brain = Path(output)
    if brain.exists() and any(brain.iterdir()):
        raise ValueError("Use an empty replay directory")
    init.initialize(brain, name="Shopify 学习 Brain", language="zh-CN", date="2026-10-24")
    payload = json.loads((ROOT / "examples/learning/libernovo.json").read_text())
    assert learn.commit(brain, payload, "2026-10-24", allow_legacy=True)["status"] == "ingested"
    before = {str(p.relative_to(brain)): p.read_bytes() for p in brain.rglob("*") if p.is_file()}
    assert learn.commit(brain, copy.deepcopy(payload), "2026-10-25", allow_legacy=True)["status"] == "duplicate"
    assert before == {str(p.relative_to(brain)): p.read_bytes() for p in brain.rglob("*") if p.is_file()}
    result = checker.check(brain)
    assert not result["errors"] and (result["brands"],result["sources"],result["events"]) == (1,6,1), result
    assert result["pages_by_type"] == {"brands":1,"categories":0,"growth":0,"ideas":0,"shopify":1}, result
    original = ROOT / "examples/learning/brain"
    expected = {str(p.relative_to(original)): p.read_bytes() for p in original.rglob("*") if p.is_file() and p.name != ".DS_Store"}
    guides = {"AGENTS.md", "BRAIN.md"}
    assert {p:b for p,b in before.items() if p not in guides} == {p:b for p,b in expected.items() if p not in guides}, "Historical research differs from replay"
    print(json.dumps({"mode":"deterministic_learning_replay",**result},ensure_ascii=False,indent=2))


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="brb-learning-") as directory:
        run(directory)

#!/usr/bin/env python3
"""Read-only checks for a Brain's registry, snapshots, and wiki links."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re


review_spec = importlib.util.spec_from_file_location("brb_check_knowledge", Path(__file__).with_name("knowledge_review.py"))
knowledge = importlib.util.module_from_spec(review_spec)
review_spec.loader.exec_module(knowledge)


def check(root):
    root = Path(root).resolve()
    errors = []
    profile = json.loads((root / "brain.json").read_text(encoding="utf-8"))
    state = json.loads((root / ".brb/state.json").read_text(encoding="utf-8"))
    if profile.get("schema") != "brand-research-brain/v1" or state.get("schema") != profile.get("schema"):
        errors.append("Profile/state schema mismatch")

    def exists(relative):
        path = root / relative
        if path.is_symlink() or root not in path.resolve().parents or not path.is_file():
            errors.append("Missing or unsafe file: " + relative)
            return False
        return True

    for brand in state["brands"].values():
        exists(brand["page"])
        for page in brand["pages"]:
            exists(page)
    for source_id, source in state["sources"].items():
        if source["brand"] not in state["brands"]:
            errors.append("Unregistered source brand: " + source_id)
        if exists(source["path"]):
            record = (root / source["path"]).read_text(encoding="utf-8")
            match = re.search(r"## Provenance and extracted claims\n\n```json\n(.*?)\n```\n\n## Capture\n\n(.*)\Z", record, re.S)
            if not match:
                errors.append("Malformed source record: " + source_id)
                continue
            metadata = json.loads(match.group(1))
            expected = {k: v for k, v in source["source"].items() if k != "capture"}
            if metadata != expected or match.group(2) != source["source"]["capture"].rstrip() + "\n":
                errors.append("Source snapshot differs from registry: " + source_id)
            if hashlib.sha256(source["source"]["capture"].encode()).hexdigest() != source["capture_sha256"]:
                errors.append("Source capture hash mismatch: " + source_id)
    ids = [event["id"] for event in state["events"]]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate processing events")
    log = (root / "wiki/log.md").read_text(encoding="utf-8")
    for event in state["events"]:
        if any(sid not in state["sources"] for sid in event.get("source_ids", [event["source_id"]])):
            errors.append("Event refers to missing source: " + event["id"])
        if log.count("<!-- brb:event:" + event["id"] + " -->") != 1:
            errors.append("Log/registry event mismatch: " + event["id"])
        if "knowledge_reviews" in event:
            try:
                retained = knowledge.validate(event["knowledge_reviews"], set(event.get("pages", {})))
                for path in retained:
                    exists(path)
            except (ValueError, TypeError):
                errors.append("Invalid background knowledge review: " + event["id"])
        reviews = event.get("dimension_reviews")
        if reviews is not None:  # Old v0.1.0 events remain readable.
            if not isinstance(reviews, dict) or set(reviews) != {"category", "growth", "ideas"}:
                errors.append("Incomplete dimension review: " + event["id"])
                continue
            for dimension, review in reviews.items():
                if not isinstance(review, dict) or review.get("action") not in {"write", "retain", "skip"} or not isinstance(review.get("reason"), str) or not review["reason"].strip():
                    errors.append("Invalid dimension review: " + event["id"] + ":" + dimension)
                    continue
                for path in review.get("paths", []):
                    exists(path)
    for page in (root / "wiki").rglob("*.md"):
        content = page.read_text(encoding="utf-8")
        for link in re.findall(r"\[\[([^\]]+)\]\]", content):
            target = link.split("|", 1)[0].split("#", 1)[0]
            if target:
                relative = target if target.endswith(".md") else target + ".md"
                if not exists(relative):
                    errors.append("Unresolved link in " + str(page.relative_to(root)) + ": " + target)
        if "{{source}}" in content:
            errors.append("Unresolved source placeholder: " + str(page.relative_to(root)))
    return {"brands": len(state["brands"]), "sources": len(state["sources"]),
            "pages_by_type": {folder: len(list((root / "wiki" / folder).glob("*.md"))) for folder in (("brands", "categories", "growth", "ideas", "shopify") if (root / "wiki/shopify").exists() and any((root / "wiki/shopify").glob("*.md")) else ("brands", "categories", "growth", "ideas"))},
            "events": len(state["events"]), "errors": sorted(set(errors))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brain", required=True)
    args = parser.parse_args()
    try:
        result = check(args.brain)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, str(error) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

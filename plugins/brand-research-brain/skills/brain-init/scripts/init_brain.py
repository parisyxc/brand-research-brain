#!/usr/bin/env python3
"""Initialize a Markdown Brain without replacing existing files. Python 3.9+."""
import argparse
import datetime as dt
import json
from pathlib import Path

SCHEMA = "brand-research-brain/v1"
DIRECTORIES = ["raw/sources", "raw/assets", "raw/build-log", "wiki/brands",
               "wiki/categories", "wiki/ideas", "wiki/growth", "wiki/shopify", "handoffs", ".brb"]


def guard(root, relative):
    candidate = root / relative
    for part in [candidate, *candidate.parents]:
        if part.is_symlink():
            raise ValueError("Refusing a symlink in the Brain destination")
        if part == root:
            break
    return candidate


def initialize(root, name="My Brand Brain", language="auto", markets=None,
               interests=None, constraints=None, date=None, goal=None, stage="exploring"):
    root = Path(root).expanduser().absolute()
    if root.is_symlink():
        raise ValueError("Choose the actual Brain directory, not a symlink")
    # Resolve OS aliases such as macOS /var -> /private/var before containment checks.
    root = root.resolve()
    date = date or dt.date.today().isoformat()
    dt.date.fromisoformat(date)
    template = Path(__file__).resolve().parent.parent / "assets/template"
    files = {str(p.relative_to(template)): p.read_text(encoding="utf-8")
             for p in template.rglob("*") if p.is_file()}
    if language.lower().startswith("zh"):
        localized = template.parent / "template-zh"
        files.update({str(p.relative_to(localized)): p.read_text(encoding="utf-8")
                      for p in localized.rglob("*") if p.is_file()})
    profile = {"schema": SCHEMA, "name": name, "language": language,
               "research_goal": goal or "Learn from brand websites to choose products, build and grow a Shopify store",
               "stage": stage,
               "markets": markets or [], "interests": interests or [],
               "constraints": constraints or [], "created_on": date}
    files["brain.json"] = json.dumps(profile, ensure_ascii=False, indent=2) + "\n"
    files[".brb/state.json"] = json.dumps(
        {"schema": SCHEMA, "brands": {}, "sources": {}, "events": []}, indent=2) + "\n"
    for relative in [*DIRECTORIES, *files]:
        target = guard(root, relative)
        if target.exists() and relative in files and not target.is_file():
            raise ValueError("A starter file path is occupied by a directory")
        if target.exists() and relative in DIRECTORIES and not target.is_dir():
            raise ValueError("A Brain directory path is occupied by a file")
    if (root / "brain.json").exists():
        existing = json.loads((root / "brain.json").read_text(encoding="utf-8"))
        if existing.get("schema") != SCHEMA:
            raise ValueError("Existing brain.json uses an incompatible schema")
    if (root / ".brb/state.json").exists():
        state = json.loads((root / ".brb/state.json").read_text(encoding="utf-8"))
        if state.get("schema") != SCHEMA:
            raise ValueError("Existing state uses an incompatible schema")
    else:
        for folder in ("raw/sources", "wiki/brands"):
            if any((root / folder).rglob("*.md")):
                raise ValueError("Research exists without a registry; restore its state backup instead of reinitializing")
    created, preserved = [], []
    root.mkdir(parents=True, exist_ok=True)
    for directory in DIRECTORIES:
        (root / directory).mkdir(parents=True, exist_ok=True)
    for relative, text in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with target.open("x", encoding="utf-8") as handle:
                handle.write(text)
            created.append(relative)
        except FileExistsError:
            preserved.append(relative)
    return {"root": str(root), "created": sorted(created), "preserved": sorted(preserved)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--name", default="My Brand Brain")
    parser.add_argument("--language", default="auto")
    parser.add_argument("--goal", help="Personal Shopify learning goal")
    parser.add_argument("--stage", default="exploring", help="For example exploring, building, or growing")
    for field in ("market", "interest", "constraint"):
        parser.add_argument("--" + field, action="append", default=[])
    parser.add_argument("--date", help="Owner's local date, YYYY-MM-DD")
    args = parser.parse_args()
    try:
        result = initialize(args.root, args.name, args.language, args.market,
                            args.interest, args.constraint, args.date, args.goal, args.stage)
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

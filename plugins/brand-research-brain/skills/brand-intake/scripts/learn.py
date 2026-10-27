#!/usr/bin/env python3
"""Save one learning session with multiple immutable sources and one log entry."""
import argparse
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import re

spec = importlib.util.spec_from_file_location("brb_evidence", Path(__file__).with_name("intake.py"))
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
review_spec = importlib.util.spec_from_file_location("brb_knowledge", Path(__file__).with_name("knowledge_review.py"))
knowledge = importlib.util.module_from_spec(review_spec)
review_spec.loader.exec_module(knowledge)


def commit(brain, payload, date=None, revise=False, allow_legacy=False):
    if not isinstance(payload, dict):
        raise ValueError("Payload must be an object")
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("Provide at least one source actually read (or a documented access failure)")
    brand = payload.get("brand", {})
    slug = core.nonblank(brand.get("id"), "brand.id")
    brand_path = "wiki/brands/" + slug + ".md"
    mode = payload.get("mode", "learning")
    if mode not in {"learning", "growth"}:
        raise ValueError("mode must be learning or growth")
    primary_path = brand_path if mode == "learning" else "wiki/growth/" + slug + "-growth.md"
    pages = payload.get("pages")
    if not isinstance(pages, list) or not pages:
        raise ValueError("Provide the learning case")
    paths = []
    for page in pages:
        path = core.nonblank(page.get("path"), "page.path")
        if not re.fullmatch(r"wiki/(brands|categories|ideas|growth|shopify)/[a-z0-9]+(?:-[a-z0-9]+)*\.md", path):
            raise ValueError("Unsupported learning page path")
        core.nonblank(page.get("content"), "page.content")
        paths.append(path)
    if len(set(paths)) != len(paths) or primary_path not in paths:
        raise ValueError("Use distinct page paths including the session primary page")
    reviews = payload.get("knowledge_reviews")
    if reviews is not None or not allow_legacy:
        knowledge.validate(reviews, set(paths))
    for key in ("summary", "next_action"):
        core.nonblank(payload.get(key), key)
    # Reuse the source contract without requiring visible dimension reviews or a business decision.
    records = []
    for source in sources:
        identity = core.validate({"brand": brand, "source": source,
            "pages": [{"path": brand_path, "content": "Source validation"}],
            "dimension_reviews": {k: {"action": "skip", "reason": "Learning session", "paths": []} for k in core.DIMENSIONS},
            "decision": "Study", "summary": payload["summary"], "next_action": payload["next_action"]})
        stable = {k: v for k, v in source.items() if k not in {"observed_at", "url", "local_ref"}}
        sid = "s-" + core.digest(core.encoded([slug, identity, stable]))[:20]
        records.append((sid, "raw/sources/" + slug + "/" + sid + ".md", identity, source))
    if len({r[0] for r in records}) != len(records):
        raise ValueError("Repeated evidence in sources; include it once")
    root = Path(brain).expanduser().absolute()
    if root.is_symlink():
        raise ValueError("Choose the actual Brain directory")
    root = root.resolve()
    date = date or dt.date.today().isoformat()
    dt.date.fromisoformat(date)
    for path in ["brain.json", ".brb/state.json", ".brb/intake.lock", "wiki/index.md", "wiki/log.md", brand_path, *paths, *(r[1] for r in records)]:
        core.safe_path(root, path)
    if json.loads((root / "brain.json").read_text()).get("schema") != core.SCHEMA:
        raise ValueError("Initialize a compatible Brain first")
    lock = root / ".brb/intake.lock"
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError("Another intake or stale lock exists; inspect before retrying")
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(str(os.getpid()))
        return _write(root, payload, records, brand_path, primary_path, mode, date, revise)
    finally:
        lock.unlink()


def _write(root, payload, records, brand_path, primary_path, mode, date, revise):
    state = json.loads((root / ".brb/state.json").read_text())
    if state.get("schema") != core.SCHEMA:
        raise ValueError("Incompatible registry")
    brand = payload["brand"]
    slug = brand["id"]
    labels = {brand["name"].casefold(), *(a.casefold() for a in brand.get("aliases", []))}
    for other_id, other in state["brands"].items():
        if other_id != slug and labels & {other["name"].casefold(), *(a.casefold() for a in other.get("aliases", []))}:
            raise ValueError("Brand alias already belongs to " + other_id)
    if mode == "growth":
        if slug not in state["brands"] or not core.safe_path(root, brand_path).is_file():
            raise ValueError("Growth research needs an existing registered brand case; intake it first")
    reviews = payload.get("knowledge_reviews")
    retained = knowledge.validate(reviews, {p["path"] for p in payload["pages"]}) if reviews is not None else set()
    for path in retained:
        if not core.safe_path(root, path).is_file():
            raise ValueError("Retained knowledge page does not exist: " + path)
    new = [r for r in records if r[0] not in state["sources"]]
    if not new and not revise:
        return {"status": "duplicate", "brand": slug, "changed": []}
    source_links = ["[[" + path[:-3] + "|" + source["title"].replace("|", " ").replace("]", "") + "]]" for _, path, _, source in records]
    rendered = []
    for page in payload["pages"]:
        content = page["content"].replace("{{sources}}", "\n".join("- " + link for link in source_links))
        for number, link in enumerate(source_links):
            content = content.replace("{{source:" + str(number) + "}}", link)
        content = content.rstrip() + "\n"
        if "{{source" in content:
            raise ValueError("Unresolved source placeholder")
        cited = [core.links_to(content, path) for _, path, _, _ in records]
        if page["path"] == primary_path:
            if mode == "growth" and not core.links_to(content, brand_path):
                raise ValueError("Growth note needs its brand backlink")
            if not all(cited):
                raise ValueError("Primary note must link all session sources (use {{sources}})")
        elif mode == "growth" and page["path"] == brand_path:
            if not core.links_to(content, primary_path):
                raise ValueError("Updated case must link to its growth note")
        elif not any(cited) or not core.links_to(content, brand_path):
            raise ValueError("Reusable note needs a relevant source and brand backlink")
        rendered.append((page["path"], content))
    source_ids = sorted(r[0] for r in records)
    event_data = [mode, source_ids, rendered, payload["summary"], payload["next_action"]]
    if reviews is not None:
        event_data.append(reviews)
    event_id = "e-" + core.digest(core.encoded(event_data))[:20]
    if any(e["id"] == event_id for e in state["events"]):
        return {"status": "duplicate", "brand": slug, "changed": []}
    for page in payload["pages"]:
        target = core.safe_path(root, page["path"])
        if target.exists():
            if page.get("expected_sha256") != core.digest(target.read_bytes()):
                raise ValueError("Read current page and supply expected_sha256: " + page["path"])
        elif page.get("expected_sha256") is not None:
            raise ValueError("Expected page does not exist")
    snapshots = []
    for sid, path, identity, source in records:
        target = core.safe_path(root, path)
        known = sid in state["sources"]
        if (known and not target.is_file()) or (not known and target.exists()):
            raise ValueError("Registry/snapshot mismatch; inspect before retrying: " + path)
        if not known:
            metadata = {k: v for k, v in source.items() if k != "capture"}
            text = ("# " + source["title"] + "\n\nSource ID: `" + sid + "`\n\n## Provenance and extracted claims\n\n```json\n" +
                    json.dumps(metadata, ensure_ascii=False, indent=2) + "\n```\n\n## Capture\n\n" + source["capture"].rstrip() + "\n")
            snapshots.append((path, text))
            state["sources"][sid] = {"brand": slug, "path": path, "identity": identity, "source": source, "capture_sha256": core.digest(source["capture"])}
    previous = state["brands"].get(slug, {})
    aliases = set(previous.get("aliases", []) + brand.get("aliases", []))
    if previous.get("name") and previous["name"] != brand["name"]:
        aliases.add(previous["name"])
    state["brands"][slug] = {"name": brand["name"], "aliases": sorted(aliases), "page": brand_path,
                             "pages": sorted(set(previous.get("pages", []) + [p for p, _ in rendered] + list(retained)))}
    state["events"].append({"id": event_id, "source_id": source_ids[0], "source_ids": source_ids, "date": date,
                            "type": mode if new else mode + "_revision", "pages": {p: core.digest(c) for p, c in rendered}})
    if reviews is not None:
        state["events"][-1]["knowledge_reviews"] = reviews
    def label(path):
        content = next((c for p, c in rendered if p == path), None)
        if content is None:
            content = core.safe_path(root, path).read_text(encoding="utf-8")
        title = content.splitlines()[0].lstrip("# ").replace("|", " ").replace("]", "")
        return "[[" + path[:-3] + "|" + title + "]]"
    index = (root / "wiki/index.md").read_text(encoding="utf-8")
    brands = ["- " + label(b["page"]) for _, b in sorted(state["brands"].items())]
    related = sorted({p for b in state["brands"].values() for p in b["pages"] if not p.startswith("wiki/brands/")})
    sources = ["- [[" + s["path"][:-3] + "|" + s["source"]["title"].replace("|", " ").replace("]", "") + "]]" for _, s in sorted(state["sources"].items())]
    for section, lines in (("brands", brands), ("research", ["- " + label(p) for p in related]), ("sources", sources)):
        index = core.replace_section(index, section, lines)
    log = (root / "wiki/log.md").read_text(encoding="utf-8")
    first, _, rest = log.partition("\n")
    if not first.startswith("# "):
        raise ValueError("Learning log needs a Markdown title")
    entry = ("\n<!-- brb:event:" + event_id + " -->\n## " + date + " · " + brand["name"] + "\n\n" +
             payload["summary"].strip() + "\n\n" + label(primary_path) + "\n\n" + payload["next_action"].strip() + "\n\n")
    log = first + "\n" + entry + rest.lstrip("\n")
    # Preflight is complete. Raw records are exclusive creates; wiki writes are atomic per file.
    for path, text in snapshots:
        target = core.safe_path(root, path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("x", encoding="utf-8") as handle:
            handle.write(text)
    writes = rendered + [("wiki/index.md", index), ("wiki/log.md", log), (".brb/state.json", json.dumps(state, ensure_ascii=False, indent=2) + "\n")]
    for path, text in writes:
        core.atomic_write(core.safe_path(root, path), text)
    return {"status": "ingested" if new else "revised", "brand": slug, "source_ids": source_ids,
            "changed": [p for p, _ in snapshots + writes]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brain", required=True)
    parser.add_argument("--payload", required=True)
    parser.add_argument("--date")
    parser.add_argument("--revise", action="store_true")
    args = parser.parse_args()
    try:
        result = commit(args.brain, json.loads(Path(args.payload).read_text(encoding="utf-8")), args.date, args.revise)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()

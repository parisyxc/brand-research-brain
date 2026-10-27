#!/usr/bin/env python3
"""Commit an agent-authored, evidence-labeled intake to a local Brain. Python 3.9+."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

SCHEMA = "brand-research-brain/v1"
KINDS = {"official_claim", "reported_claim", "user_note", "observed_feature"}
TYPES = {"official_site", "article", "clip", "note", "document"}
DECISIONS = {"Study", "Validate", "Pause", "Kill"}
DIMENSIONS = {"category": "categories", "growth": "growth", "ideas": "ideas"}


def validate_reviews(reviews, page_paths):
    if not isinstance(reviews, dict) or set(reviews) != set(DIMENSIONS):
        raise ValueError("dimension_reviews must check category, growth and ideas")
    covered = set()
    for dimension, directory in DIMENSIONS.items():
        review = reviews[dimension]
        if not isinstance(review, dict) or review.get("action") not in {"write", "retain", "skip"}:
            raise ValueError("Invalid dimension action: " + dimension)
        nonblank(review.get("reason"), dimension + ".reason")
        paths = review.get("paths")
        if not isinstance(paths, list) or any(not isinstance(p, str) for p in paths):
            raise ValueError("Dimension paths must be a string list")
        if len(paths) != len(set(paths)):
            raise ValueError("Repeated dimension path")
        if (review["action"] == "skip") != (not paths):
            raise ValueError("skip needs no paths; write/retain need paths")
        for path in paths:
            if not re.fullmatch(r"wiki/" + directory + r"/[a-z0-9]+(?:-[a-z0-9]+)*\.md", path):
                raise ValueError("Page in wrong dimension: " + path)
            if review["action"] == "write":
                if path not in page_paths:
                    raise ValueError("Reviewed write page missing from payload: " + path)
                covered.add(path)
            elif path in page_paths:
                raise ValueError("Retained page must not be replaced: " + path)
    related = {p for p in page_paths if not p.startswith("wiki/brands/")}
    if covered != related:
        raise ValueError("Every related page write needs a matching dimension review")


def links_to(content, target):
    return any(link.split("|", 1)[0].split("#", 1)[0].removesuffix(".md") == target.removesuffix(".md")
               for link in re.findall(r"\[\[([^\]]+)\]\]", content))


def render_reviews(content, reviews, chinese=False):
    start, end = "<!-- brb:dimension-review:start -->", "<!-- brb:dimension-review:end -->"
    heading = "## 三个研究维度检查" if chinese else "## Research dimension review"
    header = "| 维度 | 处理 | 理由 | 页面 |" if chinese else "| Dimension | Action | Reason | Pages |"
    lines = [start, heading, "", header, "| --- | --- | --- | --- |"]
    for dimension in DIMENSIONS:
        review = reviews[dimension]
        reason = " ".join(review["reason"].split()).replace("|", "\\|")
        paths = ", ".join("[[" + p[:-3] + "]]" for p in review["paths"]) or "—"
        lines.append("| " + dimension + " | " + review["action"] + " | " + reason + " | " + paths + " |")
    block = "\n".join(lines + [end])
    if start in content or end in content:
        if content.count(start) != 1 or content.count(end) != 1 or content.index(start) > content.index(end):
            raise ValueError("Ambiguous dimension review markers in brand page")
        before, rest = content.split(start, 1)
        _, after = rest.split(end, 1)
        return before + block + after
    return content.rstrip() + "\n\n" + block + "\n"


def digest(value):
    if not isinstance(value, bytes):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def canonical_url(value):
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError("Source URL must be public-style HTTP(S), without embedded credentials")
    query = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True)
             if not k.lower().startswith("utm_") and k.lower() not in {"fbclid", "gclid"}]
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path or "/",
                       urlencode(sorted(query)), ""))


def safe_path(root, relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or "\\" in relative:
        raise ValueError("Paths must remain inside the selected Brain")
    target = root / path
    for part in [target, *target.parents]:
        if part.is_symlink():
            raise ValueError("Refusing symlink inside Brain")
        if part == root:
            break
    return target


def nonblank(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(field + " must be a nonempty string")
    return value


def validate(payload):
    if not isinstance(payload, dict):
        raise ValueError("Payload must be an object")
    brand = payload.get("brand", {})
    slug = nonblank(brand.get("id"), "brand.id")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or len(slug) > 64:
        raise ValueError("brand.id must be a stable lowercase slug of at most 64 characters")
    nonblank(brand.get("name"), "brand.name")
    if not isinstance(brand.get("aliases", []), list) or any(
            not isinstance(a, str) or not a.strip() for a in brand.get("aliases", [])):
        raise ValueError("brand.aliases must be a list of nonblank strings")
    source = payload.get("source", {})
    if source.get("type") not in TYPES:
        raise ValueError("Unsupported source type")
    if source.get("access") not in {"complete", "partial", "unavailable"}:
        raise ValueError("Invalid source access")
    for key in ("title", "publisher", "capture", "observed_at"):
        nonblank(source.get(key), "source." + key)
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", source["observed_at"]):
            dt.date.fromisoformat(source["observed_at"])
        else:
            stamp = dt.datetime.fromisoformat(source["observed_at"].replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                raise ValueError()
    except (ValueError, TypeError):
        raise ValueError("observed_at must be an ISO date or a timestamp with a timezone")
    if source.get("published_at") is not None and not isinstance(source["published_at"], str):
        raise ValueError("published_at must be a string or null")
    if source.get("local_ref"):
        reference = nonblank(source["local_ref"], "source.local_ref")
        if Path(reference).is_absolute() or ".." in Path(reference).parts or "\\" in reference:
            raise ValueError("local_ref must be a portable relative source label")
    if source.get("url"):
        identity = canonical_url(nonblank(source["url"], "source.url"))
    else:
        identity = nonblank(source.get("local_ref"), "source.local_ref")
        if Path(identity).is_absolute() or ".." in Path(identity).parts:
            raise ValueError("local_ref must be a portable relative source label")
    if source.get("input_sha256") and not re.fullmatch(r"[0-9a-f]{64}", source["input_sha256"]):
        raise ValueError("input_sha256 must be a lowercase SHA-256 digest")
    if not isinstance(source.get("limitations"), list) or any(
            not isinstance(x, str) for x in source["limitations"]):
        raise ValueError("source.limitations must be a string list")
    claims = source.get("claims")
    if not isinstance(claims, list):
        raise ValueError("source.claims must be a list")
    if source["access"] == "unavailable" and claims:
        raise ValueError("Unavailable sources cannot contain extracted claims")
    for claim in claims:
        if not isinstance(claim, dict) or claim.get("kind") not in KINDS:
            raise ValueError("Invalid claim kind")
        nonblank(claim.get("text"), "claim.text")
        nonblank(claim.get("locator"), "claim.locator")
    pages = payload.get("pages")
    if not isinstance(pages, list) or not pages:
        raise ValueError("At least the brand page is required")
    paths = []
    for page in pages:
        path = nonblank(page.get("path"), "page.path")
        if not re.fullmatch(r"wiki/(brands|categories|ideas|growth|shopify)/[a-z0-9]+(?:-[a-z0-9]+)*\.md", path):
            raise ValueError("Unsupported wiki page path")
        nonblank(page.get("content"), "page.content")
        paths.append(path)
    if len(set(paths)) != len(paths):
        raise ValueError("Duplicate page paths")
    if "wiki/brands/" + slug + ".md" not in paths:
        raise ValueError("Payload must include its canonical brand page")
    validate_reviews(payload.get("dimension_reviews"), set(paths))
    if payload.get("decision") not in DECISIONS:
        raise ValueError("Invalid decision")
    for key in ("summary", "next_action"):
        nonblank(payload.get(key), key)
    return identity


def replace_section(index, name, lines):
    start, end = "<!-- brb:" + name + ":start -->", "<!-- brb:" + name + ":end -->"
    if index.count(start) != 1 or index.count(end) != 1 or index.index(start) > index.index(end):
        raise ValueError("Index managed markers missing or ambiguous: " + name)
    before, rest = index.split(start, 1)
    _, after = rest.split(end, 1)
    return before + start + "\n" + "\n".join(lines) + ("\n" if lines else "") + end + after


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".brb-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def commit(brain, payload, date=None, revise=False):
    identity = validate(payload)
    root = Path(brain).expanduser().absolute()
    if root.is_symlink():
        raise ValueError("Choose the actual Brain directory, not a symlink")
    root = root.resolve()
    date = date or dt.date.today().isoformat()
    dt.date.fromisoformat(date)
    # Preflight every state/index destination before acquiring the lock.
    for path in ("brain.json", ".brb/state.json", ".brb/intake.lock", "wiki/index.md", "wiki/log.md"):
        safe_path(root, path)
    profile = json.loads((root / "brain.json").read_text(encoding="utf-8"))
    if profile.get("schema") != SCHEMA:
        raise ValueError("Initialize a compatible Brain first")
    lock = root / ".brb/intake.lock"
    try:
        lock_fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError("Another intake or stale lock exists; inspect .brb/intake.lock")
    try:
        with os.fdopen(lock_fd, "w", encoding="utf-8") as handle:
            handle.write(str(os.getpid()))
        return _locked_commit(root, payload, identity, date, revise)
    finally:
        lock.unlink()


def _locked_commit(root, payload, identity, date, revise):
    state = json.loads((root / ".brb/state.json").read_text(encoding="utf-8"))
    if state.get("schema") != SCHEMA:
        raise ValueError("Incompatible state schema")
    brand, source = payload["brand"], payload["source"]
    slug = brand["id"]
    labels = {brand["name"].casefold(), *(x.casefold() for x in brand.get("aliases", []))}
    for other_id, other in state["brands"].items():
        names = {other["name"].casefold(), *(x.casefold() for x in other.get("aliases", []))}
        if other_id != slug and labels & names:
            raise ValueError("Brand alias already belongs to " + other_id)
    stable_source = {key: value for key, value in source.items() if key not in {"observed_at", "url", "local_ref"}}
    source_id = "s-" + digest(encoded([slug, identity, stable_source]))[:20]
    source_path = "raw/sources/" + slug + "/" + source_id + ".md"
    source_link = "[[" + source_path[:-3] + "]]"
    known = source_id in state["sources"]
    if known and not revise:
        return {"status": "duplicate", "source_id": source_id, "brand": slug, "changed": []}
    pages = []
    reviews = payload["dimension_reviews"]
    chinese = json.loads((root / "brain.json").read_text(encoding="utf-8")).get("language", "auto").lower().startswith("zh")
    for page in payload["pages"]:
        safe_path(root, page["path"])
        content = page["content"].replace("{{source}}", source_link).rstrip() + "\n"
        if page["path"] == "wiki/brands/" + slug + ".md":
            content = render_reviews(content, reviews, chinese)
        else:
            if not links_to(content, "wiki/brands/" + slug):
                raise ValueError("Related research must link back to its brand: " + page["path"])
            if source_link not in content:
                raise ValueError("Related research must cite this source: " + page["path"])
        pages.append((page["path"], content))
    brand_content = next(content for path, content in pages if path == "wiki/brands/" + slug + ".md")
    if source_link not in brand_content:
        raise ValueError("Brand page must cite {{source}} or this source's existing immutable wikilink")
    event_id = "e-" + digest(encoded([source_id, pages, reviews, payload["decision"], payload["summary"], payload["next_action"]]))[:20]
    if any(event["id"] == event_id for event in state["events"]):
        return {"status": "duplicate", "source_id": source_id, "brand": slug, "changed": []}
    for page in payload["pages"]:
        target = safe_path(root, page["path"])
        if target.exists():
            if page.get("expected_sha256") != digest(target.read_bytes()):
                raise ValueError("Read current page and supply expected_sha256: " + page["path"])
        elif page.get("expected_sha256") is not None:
            raise ValueError("Page expected by payload does not exist: " + page["path"])
    for review in reviews.values():
        if review["action"] == "retain":
            for path in review["paths"]:
                if not safe_path(root, path).is_file():
                    raise ValueError("Retained page does not exist: " + path)
    snapshot = safe_path(root, source_path)
    if not known and snapshot.exists():
        raise ValueError("Unregistered source snapshot exists; inspect interrupted intake before retry")
    if known and not snapshot.is_file():
        raise ValueError("Registered source snapshot missing; restore it before revision")
    previous = state["brands"].get(slug, {})
    aliases = sorted(set(previous.get("aliases", []) + brand.get("aliases", [])))
    if previous.get("name") and previous["name"] != brand["name"]:
        aliases = sorted(set(aliases + [previous["name"]]))
    state["brands"][slug] = {"name": brand["name"], "aliases": aliases,
                              "page": "wiki/brands/" + slug + ".md",
                              "pages": sorted(set(previous.get("pages", []) + [p for p, _ in pages] +
                                                  [p for review in reviews.values() for p in review["paths"]]))}
    if not known:
        state["sources"][source_id] = {"brand": slug, "path": source_path, "identity": identity,
                                       "source": source, "capture_sha256": digest(source["capture"])}
    state["events"].append({"id": event_id, "source_id": source_id, "date": date,
                            "type": "revision" if known else "intake",
                            "decision": payload["decision"], "dimension_reviews": reviews,
                            "pages": {p: digest(c) for p, c in pages}})
    index = (root / "wiki/index.md").read_text(encoding="utf-8")
    brands = ["- [[" + item["page"][:-3] + "|" + item["name"] + "]]"
              for _, item in sorted(state["brands"].items())]
    related = sorted({p for item in state["brands"].values() for p in item["pages"] if not p.startswith("wiki/brands/")})
    sources = ["- [[" + item["path"][:-3] + "]]" for _, item in sorted(state["sources"].items())]
    for section, lines in (("brands", brands), ("research", ["- [[" + p[:-3] + "]]" for p in related]), ("sources", sources)):
        index = replace_section(index, section, lines)
    log = (root / "wiki/log.md").read_text(encoding="utf-8")
    first_line, sep, rest = log.partition("\n")
    if not first_line.startswith("# "):
        raise ValueError("Research log must begin with a Markdown title")
    entry = ("\n<!-- brb:event:" + event_id + " -->\n## " + date + " | " +
             ("revise" if known else "intake") + " | " + brand["name"] + "\n\n" +
             payload["summary"].strip() + "\n\nSource: " + source_link +
             "\n\nPages: " + ", ".join("[[" + p[:-3] + "]]" for p, _ in pages) +
             "\n\n" + render_reviews("", reviews, chinese).strip() +
             "\n\nDecision: **" + payload["decision"] + "**\n\nNext action: " +
             payload["next_action"].strip() + "\n")
    log = first_line + "\n" + entry + "\n" + rest.lstrip("\n")
    metadata = {key: value for key, value in source.items() if key != "capture"}
    record = ("# " + source["title"] + "\n\nSource ID: `" + source_id + "`\n\n" +
              "## Provenance and extracted claims\n\n```json\n" +
              json.dumps(metadata, ensure_ascii=False, indent=2) +
              "\n```\n\n## Capture\n\n" + source["capture"].rstrip() + "\n")
    # All validation has completed. Existing raw records are never replaced.
    if not known:
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        with snapshot.open("x", encoding="utf-8") as handle:
            handle.write(record)
    writes = pages + [("wiki/index.md", index), ("wiki/log.md", log),
                     (".brb/state.json", json.dumps(state, ensure_ascii=False, indent=2) + "\n")]
    for relative, content in writes:
        atomic_write(safe_path(root, relative), content)
    return {"status": "revised" if known else "ingested", "source_id": source_id,
            "brand": slug, "changed": ([] if known else [source_path]) + [p for p, _ in writes]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brain", required=True)
    parser.add_argument("--payload", required=True)
    parser.add_argument("--date", help="Owner's local date, YYYY-MM-DD")
    parser.add_argument("--revise", action="store_true")
    args = parser.parse_args()
    try:
        payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
        print(json.dumps(commit(args.brain, payload, args.date, args.revise), ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()

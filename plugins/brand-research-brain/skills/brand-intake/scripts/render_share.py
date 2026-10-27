#!/usr/bin/env python3
"""Render a source-grounded, offline HTML reading document and share-card deck."""
import argparse
import datetime as dt
import html
import importlib.util
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

spec = importlib.util.spec_from_file_location("brb_share_paths", Path(__file__).with_name("intake.py"))
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
TEMPLATE = Path(__file__).resolve().parents[1] / "assets/share-card.html"


def text(value, name, maximum=240):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(name + " must be nonempty concise text (max " + str(maximum) + ")")
    return value.strip()


def items(value, name, low, high):
    if not isinstance(value, list) or not low <= len(value) <= high:
        raise ValueError(name + " needs " + str(low) + "–" + str(high) + " items")
    return value


def validate(brain, data):
    if not isinstance(data, dict) or data.get("schema") != "brb-share/v1":
        raise ValueError("Use schema brb-share/v1")
    brand = data.get("brand", {})
    slug = text(brand.get("id"), "brand.id", 80)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError("Use a lowercase hyphenated brand ID")
    text(brand.get("name"), "brand.name", 80)
    dt.date.fromisoformat(text(data.get("date"), "date", 10))
    text(data.get("headline"), "headline", 64)
    text(data.get("dek"), "dek", 180)
    for fact in items(data.get("facts"), "facts", 1, 4):
        text(fact.get("label"), "fact.label", 24)
        text(fact.get("text"), "fact.text", 100)
    for step in items(data.get("formula"), "formula", 2, 5):
        text(step, "formula step", 24)
    for practice in items(data.get("practices"), "practices", 1, 3):
        text(practice.get("title"), "practice.title", 40)
        text(practice.get("observed"), "practice.observed", 160)
        text(practice.get("lesson"), "practice.lesson", 160)
    for key in ("category", "growth", "ideas"):
        section = data.get(key, {})
        text(section.get("title"), key + ".title", 64)
        text(section.get("summary"), key + ".summary", 240)
        for point in items(section.get("points"), key + ".points", 0, 3):
            text(point.get("title"), "point.title", 40)
            text(point.get("text"), "point.text", 200)
        if "caveat" in section:
            text(section["caveat"], key + ".caveat", 200)
    for chapter in items(data["growth"].get("details", []), "growth.details", 0, 8):
        if not isinstance(chapter, dict):
            raise ValueError("Each growth detail must be an object")
        text(chapter.get("title"), "growth detail title", 64)
        summary = chapter.get("summary")
        if summary is not None:
            text(summary, "growth detail summary", 500)
        entries = items(chapter.get("items", []), "growth detail items", 0, 6)
        if not summary and not entries:
            raise ValueError("A growth detail needs a summary or items")
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError("Each growth detail item must be an object")
            text(entry.get("title"), "growth detail item title", 80)
            text(entry.get("text"), "growth detail item text", 700)
            if "lesson" in entry:
                text(entry["lesson"], "growth detail item lesson", 400)
    text(data.get("next_action"), "next_action", 240)
    for source in items(data.get("sources"), "sources", 1, 40):
        text(source.get("label"), "source.label", 120)
        if source.get("url") is not None:
            url = text(source["url"], "source.url", 2000)
            parts = urlsplit(url)
            if parts.scheme not in {"http", "https"} or not parts.hostname or parts.username or parts.password or any(c.isspace() for c in url):
                raise ValueError("Source links must be public HTTP(S) URLs without credentials")
        if "note" in source:
            text(source["note"], "source.note", 160)
    text(data.get("source_note"), "source_note", 500)
    seen = set()
    for basis in items(data.get("basis"), "basis", 1, 40):
        path = text(basis.get("path"), "basis.path", 240)
        if not re.fullmatch(r"(?:wiki|raw)/[^\n]+\.md", path) or path in seen:
            raise ValueError("Use distinct Brain-relative wiki/raw Markdown basis paths")
        seen.add(path)
        target = core.safe_path(brain, path)
        if not target.is_file() or basis.get("sha256") != core.digest(target.read_bytes()):
            raise ValueError("Read current basis and supply its sha256: " + path)
    if "wiki/brands/" + slug + ".md" not in seen:
        raise ValueError("Include the current case in basis")
    return slug


def esc(value):
    return html.escape(value, quote=True).replace("\n", "<br>")


def growth_details(chapters, brand_name):
    """Keep deep research in the document, with readable, shareable subchapters."""
    if not chapters:
        return ""
    navigation = '<nav class="growth-nav" aria-label="增长研究目录">' + "".join(
        '<a href="#growth-detail-' + str(i) + '">' + esc(c["title"]) + '</a>'
        for i, c in enumerate(chapters, 1)) + '</nav>'
    parts = []
    for i, chapter in enumerate(chapters, 1):
        entries = []
        for entry in chapter.get("items", []):
            lesson = '<p class="detail-lesson"><strong>可以借鉴</strong>' + esc(entry["lesson"]) + '</p>' if entry.get("lesson") else ''
            entries.append('<li class="detail-item"><h4>' + esc(entry["title"]) + '</h4><p>' + esc(entry["text"]) + '</p>' + lesson + '</li>')
        summary = '<p class="detail-summary">' + esc(chapter["summary"]) + '</p>' if chapter.get("summary") else ''
        parts.append('<article class="growth-chapter" id="growth-detail-' + str(i) + '"><div class="detail-eyebrow">' + esc(brand_name) + ' / 增长研究 · ' + str(i).zfill(2) + ' / ' + str(len(chapters)).zfill(2) + '</div><h3>' + esc(chapter["title"]) + '</h3>' + summary + ('<ol class="growth-detail-items">' + ''.join(entries) + '</ol>' if entries else '') + '<div class="detail-foot">增长研究 · ' + esc(chapter["title"]) + ' · <a href="#growth">返回增长概览 ↑</a></div></article>')
    return navigation + '<div class="growth-details">' + ''.join(parts) + '</div>'


def render(data):
    """Escape editorial text; never interpret supplied Markdown, HTML or scripts."""
    fact_html = "".join('<div class="fact"><dt>' + esc(f["label"]) + '</dt><dd>' + esc(f["text"]) + '</dd></div>' for f in data["facts"])
    practices = "".join('<article class="practice"><span class="number">0' + str(i) + '</span><div><h3>' + esc(p["title"]) + '</h3><p>' + esc(p["observed"]) + '</p><p class="borrow"><span>可以借鉴</span>' + esc(p["lesson"]) + '</p></div></article>' for i, p in enumerate(data["practices"], 1))
    source_html = ""
    for source in data["sources"]:
        label = esc(source["label"])
        if source.get("url"):
            label = '<a href="' + html.escape(source["url"], quote=True) + '" target="_blank" rel="noopener noreferrer">' + label + '</a>'
        source_html += '<li>' + label + ('<span>' + esc(source["note"]) + '</span>' if source.get("note") else '') + '</li>'
    slots = {"BRAND": esc(data["brand"]["name"]), "TITLE": html.escape(data["brand"]["name"] + " · 品牌学习笔记", quote=True),
             "DATE": esc(data["date"].replace("-", ".")), "HEADLINE": esc(data["headline"]), "DEK": esc(data["dek"]),
             "FACTS": fact_html, "FORMULA": '<span class="arrow">→</span>'.join('<span>' + esc(s) + '</span>' for s in data["formula"]),
             "PRACTICES": practices, "METHOD_COUNT": str(len(data["practices"])), "SOURCES": source_html,
             "SOURCE_NOTE": esc(data["source_note"]), "NEXT_ACTION": esc(data["next_action"])}
    chapters = data["growth"].get("details", [])
    slots.update({"GROWTH_CLASS": " growth-expanded" if chapters else "",
                  "GROWTH_OVERVIEW_OPEN": '<div class="growth-overview">' if chapters else '',
                  "GROWTH_OVERVIEW_CLOSE": '<p class="growth-overview-end">继续阅读 · ' + str(len(chapters)) + ' 个增长专题 ↓</p></div>' if chapters else '',
                  "GROWTH_DETAILS": growth_details(chapters, data["brand"]["name"])})
    for key in ("category", "growth", "ideas"):
        section = data[key]
        slots[key.upper() + "_TITLE"] = esc(section["title"])
        slots[key.upper() + "_SUMMARY"] = esc(section["summary"])
        slots[key.upper() + "_POINTS"] = "".join('<article class="point"><h3>' + esc(p["title"]) + '</h3><p>' + esc(p["text"]) + '</p></article>' for p in section["points"])
        slots[key.upper() + "_CAVEAT"] = '<p class="caveat">' + esc(section["caveat"]) + '</p>' if section.get("caveat") else ''
    template = TEMPLATE.read_text(encoding="utf-8")
    # One substitution pass prevents text resembling a slot from becoming markup.
    return re.sub(r"@@([A-Z_]+)@@", lambda m: slots[m[1]], template)


def save(brain, data, expected_sha256=None, growth_only=False):
    root = Path(brain).expanduser().absolute()
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Choose the actual existing Brain directory")
    root = root.resolve()
    slug = validate(root, data)
    output_path = "reports/" + slug + ".html"
    payload_path = ".brb/share/" + slug + ".json"
    receipt_path = ".brb/share/" + slug + ".receipt.json"
    for path in (output_path, payload_path, receipt_path, ".brb/share.lock"):
        core.safe_path(root, path)
    output = core.safe_path(root, output_path)
    receipt = core.safe_path(root, receipt_path)
    content = render(data)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    receipt_text = json.dumps({"schema": "brb-share-receipt/v1", "output_sha256": core.digest(content)}, indent=2) + "\n"
    lock = root / ".brb/share.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError("Another share render or stale lock exists; inspect before retrying")
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(str(os.getpid()))
        # Repeat basis validation under the writer lock. Existing Markdown is never changed.
        validate(root, data)
        if growth_only:
            prior_path = core.safe_path(root, payload_path)
            if not output.is_file() or not prior_path.is_file():
                raise ValueError("Growth-only refresh needs an existing digest; create the full case first")
            previous = json.loads(prior_path.read_text(encoding="utf-8"))
            stable = ("brand", "headline", "dek", "facts", "formula", "practices", "category", "ideas", "next_action")
            altered = [key for key in stable if previous.get(key) != data.get(key)]
            if altered:
                raise ValueError("Growth-only refresh must retain case learning: " + ", ".join(altered) + "; use a normal render only for a deliberate whole-case revision")
            old_basis = {b["path"] for b in previous["basis"]}
            new_basis = {b["path"] for b in data["basis"]}
            if not old_basis <= new_basis:
                raise ValueError("Growth-only refresh must retain prior basis for unchanged learning")
            if "wiki/growth/" + slug + "-growth.md" not in new_basis:
                raise ValueError("Growth-only refresh needs the current saved growth note in basis")
        if output.exists():
            actual = core.digest(output.read_bytes())
            saved_hash = json.loads(receipt.read_text()).get("output_sha256") if receipt.is_file() else None
            if actual not in {saved_hash, expected_sha256}:
                raise ValueError("HTML was edited or is unmanaged; read it and supply --expected-sha256")
        elif expected_sha256 is not None:
            raise ValueError("Expected HTML does not exist")
        changed = []
        for path, body in ((output_path, content), (payload_path, payload), (receipt_path, receipt_text)):
            target = core.safe_path(root, path)
            if not target.exists() or target.read_bytes() != body.encode("utf-8"):
                target.parent.mkdir(parents=True, exist_ok=True)
                core.atomic_write(target, body)
                changed.append(path)
        return {"status": "rendered" if changed else "unchanged", "html": output_path, "changed": changed}
    finally:
        lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brain", required=True)
    parser.add_argument("--payload", required=True)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--growth-only", action="store_true", help="Refresh growth and references while protecting the rest of an existing case digest")
    args = parser.parse_args()
    try:
        result = save(args.brain, json.loads(Path(args.payload).read_text(encoding="utf-8")), args.expected_sha256, args.growth_only)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()

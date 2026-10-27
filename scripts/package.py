#!/usr/bin/env python3
"""Build source, portable/Codex and Claude plugin archives; no upload."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from release_files import source_files

ROOT = Path(__file__).resolve().parents[1]


def package():
    plugin = ROOT / "plugins/brand-research-brain"
    meta = json.loads((plugin / "plugin.json").read_text())
    name, version = meta["name"], meta["version"]
    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    paths = source_files(ROOT)
    source_zip = output / (name + "-" + version + "-source.zip")
    plugin_zip = output / (name + "-" + version + "-plugin.zip")
    claude_zip = output / (name + "-" + version + "-claude-plugin.zip")
    with ZipFile(source_zip, "w", ZIP_DEFLATED) as archive:
        for path in paths:
            archive.write(path, str(Path(name) / path.relative_to(ROOT)))
    with ZipFile(plugin_zip, "w", ZIP_DEFLATED) as archive:
        for path in paths:
            if plugin in path.parents:
                archive.write(path, str(Path(name) / path.relative_to(plugin)))
        archive.write(ROOT / "LICENSE", name + "/LICENSE")
    with ZipFile(claude_zip, "w", ZIP_DEFLATED) as archive:
        for path in paths:
            if plugin not in path.parents:
                continue
            relative = path.relative_to(plugin)
            if relative.parts[0] not in {".claude-plugin", "skills", "README.md"}:
                continue
            if relative.name == "openai.yaml" and relative.parent.name == "agents":
                continue
            archive.write(path, str(relative))
        archive.write(ROOT / "LICENSE", "LICENSE")
    for path in (source_zip, plugin_zip, claude_zip):
        with ZipFile(path) as archive:
            assert archive.testzip() is None
            names = archive.namelist()
            assert all(not any(part in {".local", "__pycache__", "dist", ".git"} for part in Path(n).parts) for n in names)
            if path == claude_zip:
                assert ".claude-plugin/plugin.json" in names and "LICENSE" in names
                assert not any("marketplace.json" in n or ".codex-plugin" in n or n.endswith("openai.yaml") for n in names)
                assert all("skills/" + skill + "/SKILL.md" in names for skill in ("brain-init", "brand-intake", "growth-research"))
            else:
                assert name + "/" + ("plugins/" + name + "/plugin.json" if path == source_zip else "plugin.json") in names
            if path == source_zip:
                assert name + "/.claude-plugin/marketplace.json" in names
            elif path == plugin_zip:
                assert not any("marketplace.json" in n for n in names)
    sums = "\n".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.name for p in (source_zip, plugin_zip, claude_zip)) + "\n"
    (output / "SHA256SUMS").write_text(sums)
    print(sums, end="")


if __name__ == "__main__":
    package()

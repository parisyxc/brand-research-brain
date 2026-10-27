#!/usr/bin/env python3
"""Validate package structure, YAML/JSON, references, and public file boundaries."""
import json
from pathlib import Path
import re
import sys

import yaml

from release_files import source_files

ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT):
    plugin = root / "plugins/brand-research-brain"
    portable = json.loads((plugin / "plugin.json").read_text())
    legacy = json.loads((plugin / ".codex-plugin/plugin.json").read_text())
    claude = json.loads((plugin / ".claude-plugin/plugin.json").read_text())
    assert portable["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    for key in ("name", "version", "description", "author", "license"):
        assert portable[key] == legacy[key], "Manifest drift: " + key
        assert portable[key] == claude[key], "Claude manifest drift: " + key
    assert set(claude) == {"name", "version", "description", "author", "license", "keywords"}
    assert claude["keywords"] == portable["keywords"]
    assert (plugin / "README.md").is_file()
    assert re.fullmatch(r"\d+\.\d+\.\d+", portable["version"])
    assert not {"skills", "mcpServers", "apps", "interface"} & portable.keys()
    extra = portable["extensions"]["com.openai"]
    assert extra["interface"] == legacy["interface"]
    assert len(extra["interface"]["shortDescription"]) <= 30
    assert extra["requires_local_executor"] is True and legacy["requires_local_executor"] is True
    assert (plugin / extra["onboardingSkill"]).is_file()
    assert legacy["skills"] == "./skills/"
    marketplace = json.loads((root / ".agents/plugins/marketplace.json").read_text())
    assert (root / marketplace["plugins"][0]["source"]["path"]).resolve() == plugin.resolve()
    claude_marketplace = json.loads((root / ".claude-plugin/marketplace.json").read_text())
    assert claude_marketplace["name"] == marketplace["name"]
    assert claude_marketplace["owner"] == portable["author"]
    assert len(claude_marketplace["plugins"]) == 1
    assert claude_marketplace["plugins"][0]["name"] == portable["name"]
    assert (root / claude_marketplace["plugins"][0]["source"]).resolve() == plugin.resolve()
    names = []
    for skill in sorted((plugin / "skills").iterdir()):
        text = (skill / "SKILL.md").read_text()
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        assert match, "Missing skill frontmatter"
        meta = yaml.safe_load(match.group(1))
        assert meta["name"] == skill.name and isinstance(meta["description"], str)
        names.append(meta["name"])
        agent = yaml.safe_load((skill / "agents/openai.yaml").read_text())
        assert "$" + skill.name in agent["interface"]["default_prompt"]
        for link in re.findall(r"\]\(([^)]+)\)", text):
            if not link.startswith(("https:", "http:", "#")):
                assert (skill / link).is_file(), "Missing skill reference: " + link
        for script in (skill / "scripts").glob("*.py"):
            compile(script.read_text(), str(script), "exec")
    assert names == ["brain-init", "brand-intake", "growth-research"]
    files = source_files(root)
    for path in files:
        data = path.read_text(encoding="utf-8")
        assert not re.search(r"/(?:Users|home)/[A-Za-z0-9_.-]+/", data), "Machine-specific path: " + str(path.relative_to(root))
        assert not re.search(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}", data), "Possible credential: " + str(path.relative_to(root))
        assert not re.search(r'''(?mi)^\s*[A-Z_]*(?:API_KEY|TOKEN|SECRET)\s*[:=]\s*["'][A-Za-z0-9_-]{16,}''', data), "Possible secret assignment"
        if path.suffix == ".json":
            json.loads(data)
        if path.suffix in {".yaml", ".yml"}:
            assert isinstance(yaml.safe_load(data), dict)
    print(json.dumps({"plugin": portable["name"], "version": portable["version"],
                      "skills": names, "release_files": len(files), "status": "passed"}, indent=2))


if __name__ == "__main__":
    try:
        validate()
    except (AssertionError, ValueError, OSError, KeyError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)

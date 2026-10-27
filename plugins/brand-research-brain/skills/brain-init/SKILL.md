---
name: brain-init
description: Create a local Shopify research and learning Brain, with linked Markdown notes usable in Obsidian, Claude, or Codex.
---

# Start a Shopify learning Brain

Create a place to learn from interesting businesses and apply the learning to the user's own Shopify practice. Keep the existing plugin identity, Brand Research Brain.

Use the selected destination. Otherwise inspect the current workspace and choose a clear child folder; ask only if the destination is genuinely ambiguous. Never use the plugin cache as a Brain. Read existing `AGENTS.md`, `BRAIN.md`, and `brain.json`; another knowledge system is not permission to migrate it.

Use what the user has already said about their learning goal, stage (exploring products, building, or growing), interests and language. No questionnaire is needed. Default to Shopify research and learning, with an exploring stage; leave markets, budget and supply preferences unspecified. These are preferences, not gates before learning.

Run the bundled standard-library helper with Python 3.9+, resolving its path relative to this skill:

```sh
python3 scripts/init_brain.py --root /chosen/brain --name "My Shopify Brain" --language zh-CN --stage exploring --date YYYY-MM-DD
```

Use the user's local date. Optional `--goal`, `--interest`, `--market`, `--constraint` carry known preferences. Existing files and profile values are preserved; rerunning is not a profile migration. Read the result before claiming anything changed.

Give the actual Brain path and this next step: “研究这个网站：URL。帮我读懂这个生意，学三个具体做法，并写进 Brain。” The user can open that folder as an Obsidian vault; normal Markdown and wikilinks are sufficient. Claude or Codex can maintain the files with the same `AGENTS.md`/`BRAIN.md` conventions. No API key, Obsidian service or Shopify account is needed by this plugin.

For an existing v0.1 Brain, read its preferences and old notes. If the user asks to adopt the learning workflow, deliberately update the goal/stage and relevant guide sections, preserving personal instructions and research. Do not replace the vault or remove earlier pages.

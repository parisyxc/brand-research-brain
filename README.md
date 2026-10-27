# Brand Research Brain

Learn from interesting websites and build your Shopify second brain.

**Paste a site → understand the business → learn three concrete practices → keep the learning in Obsidian → apply it to your own Shopify journey.**

[中文](README.zh-CN.md)

## Two core skills and optional growth research

- `brain-init`: create a personal Markdown learning Brain with a goal, stage and interests.
- `brand-intake`: study a website, article or clip, explain the business, and save three concrete practices with one small next action.
- `growth-research`: on request, investigate social media, creators and SEO beyond the storefront; save one concise growth note.

Consider product selection/user insight, product/brand, storefront/conversion, content, acquisition/growth and SEO. Expand what the evidence supports. Sparse sources can yield fewer practices. No default consulting roadmap, scoring or visible processing checklists.

A website visit may contribute several immutable raw source records, but produces one case synthesis and one short log entry. Every intake reads and checks categories, ideas, Shopify and growth. Merge substantive additions, retain relevant unchanged notes and skip unsupported areas. Reconciliation is required; four new pages are not. Evidence-specific reviews stay in the background registry, never in readable cases/logs or chat. Use readable source names and linked methods to answer future questions.

## Three examples: input → research → output

Start with a website or article and a question you want to answer. These briefs summarize three studies from the author's own Brain; they show what the workflow produced, rather than ready-made business recommendations. Full personal research notes are not bundled with the plugin.

### 1. CharCharms: learn from water-bottle accessories for a concert idea

**Input:** the [CharCharms website](https://charcharms.com/) and my early idea for concert self-expression accessories, such as wearable sparkle or interchangeable decorations. I wanted to understand how the brand gives a familiar object a new role. **The concert direction came from my brief**, rather than CharCharms' product category.

**Brain researches:** what the brand actually sells—water-bottle charms, straw toppers and related accessories—and how it combines decoration, small utilities and parts people can choose or change. A later, separate growth study examined videos in which participants choose accessories before the finished bottle is revealed.

**Output:** a readable case and linked category, growth and idea notes, brought together in a Chinese HTML report. One hypothesis for my own project was to compare bag straps, collars and makeup as places for concert self-expression before choosing a fastening method. A content idea was to let people make a few choices, then show the result. Both remain ideas to test.

### 2. Doodle2Life: understand a custom-product buying experience

**Input:** a [website that turns children's drawings into 3D keepsakes](https://doodle2life.com/custom-3d-figurine-from-kids-drawing/). My focus was how the offer works and what I could learn for a customizable physical product.

**Brain researches:** the journey from a parent uploading a drawing to professional modeling and printing, followed by a white figure the family can paint. It explains what the seller completes, what the buyer gets to do, and how the drawing-to-object transformation can become content.

**Output:** three concrete practices, linked category and product-page learning, and an HTML report. The case also generated a small test proposal: use the same drawing to compare two concept offers, “finish it together” and “ready to give as a gift,” then ask people with a real buying occasion why they prefer one. This is a proposed test, not a validated product choice.

### 3. Kaleidos: turn supply capabilities into a recognizable style

**Input:** a [Kaleidos brand article](https://pangjing.cn/6114249/), supplemented by its [product website](https://kaleidos.com/products/stranger). I wanted to understand how a brand uses Chinese supply capabilities to serve a distinctive aesthetic for overseas customers.

**Brain researches:** the actual category—expressive color cosmetics—and specific product choices: colors, finishes, a consistent visual style, and replaceable inner products with different outer cases. The study connects aesthetic choices to visible product details, while keeping the article's account separate from official product observations.

**Output:** a brand case, category learning and an idea note, plus an HTML report assembled from the saved research. The practical takeaway was to turn a style preference into questions about color, material, finish and structure that a supplier can answer. Supplier feasibility and customers' willingness to buy still need separate evidence.

Across all three, the pattern is **your material + your question → a study of the brand → concrete practices, linked learning and a next question to test**. Markdown stays in your local Brain; HTML makes the learning easier to read and share. Relevant knowledge pages are updated when there is substance to add, rather than creating every type of page for every case.

## What v0.6.0 adds

v0.6.0 adds optional full growth chapters below the overview: evidenced stages, media examples, creator/retail/SEO paths, metric interpretation and concrete lessons. Content is visible inside HTML, with internal navigation and separate topic panels in card mode. A completed study is no longer forced into three bullets. Ordinary intake stays concise.

Presentation-only updates reuse saved research without provider calls, credential access or research events. This does not bundle a Monid integration. Growth-only protection for the rest of the case remains active.

v0.6.0 makes category learning case-first: name the studied category and actual products, explain its distinctive product/category move with evidence, and only then transfer the lesson. The learner's candidate products, technologies and implementation concerns belong in a marked application/ideas section. This changes explanation order, without asserting first invention, requiring extra pages or changing the renderer/schema.

v0.6.0 strengthens [concrete learning quality](plugins/brand-research-brain/skills/brand-intake/references/learning-quality.md): explain real buying situations, alternatives and actionable methods in plain language, allow clearly labeled test examples, and keep evidence checks in support of the lesson. Optional bounded comparison can answer a material selection question without expanding every intake into a market study. No private project preferences become package defaults.

Growth follow-ups use `render_share.py --growth-only` to protect the existing case's cover, methods, category, ideas and next action while updating growth and references. Deliberate whole-case corrections remain available when warranted. Starter guides carry the same learning purpose without needing a separate personal AGENTS.md.

## HTML learning documents (v0.6.0)

Every intake and deeper growth pass now also delivers `reports/<brand-id>.html`: a concise Chinese digest of case facts, concrete practices, category, growth and current-case ideas, with references at the end. Explicit user opt-out is supported. Thin evidence stays thin; the digest does not initiate another research task.

The original Wise-inspired layout uses lime, deep green, bold typography and generous space. A single offline file supports continuous reading, screenshot-friendly card mode and browser printing. Long cards extend rather than clipping. No external assets, tracking, API or hosting are needed. Automatic PNG/PDF export and social publishing are not included.

Markdown remains the knowledge source. Refreshing a digest preserves useful existing learning and writes no Markdown, raw captures or research events. Current-note hashes and output-edit protection are handled by the standard-library renderer; provenance stays in `.brb/share/`. See the [editorial and save contract](plugins/brand-research-brain/skills/brand-intake/references/share-card.md).

## Install and use

Requires a local file-capable agent and Python 3.9+. Website research also needs host-provided browser/retrieval tools. No API key, Shopify account, Obsidian service or server is required by the plugin.

From the repository root:

```sh
codex plugin marketplace add .
codex plugin add brand-research-brain@brand-research-brain
```

Run these commands from a checkout of [this GitHub repository](https://github.com/parisyxc/brand-research-brain). Follow the host's refresh/restart guidance and check the installed version. See [release notes](docs/releasing.md) for packaging details.

For **Claude Code**, this source now includes `.claude-plugin/marketplace.json` and a matching plugin manifest. From the repository root:

```sh
claude plugin marketplace add .
claude plugin install brand-research-brain@brand-research-brain
```

See the [Claude release and user guide](docs/claude-release.md) for GitHub distribution, the dedicated Claude ZIP, first-use prompts, Cowork/chat capability boundaries and optional directory submission. Manifest validation is separate from a Claude research-session acceptance test; the guide states the current verification scope.

> Create a Shopify learning Brain in my chosen folder. I am exploring products and want to learn product-page design.

> Study this website: URL. Explain the business, teach me three concrete practices, and save the learning in my Brain.

Open the resulting folder as an Obsidian vault. Claude or Codex can read and maintain the Markdown using its `AGENTS.md` and `BRAIN.md`. The source includes separate Claude and Codex manifests sharing the same skills; installation does not provide automatic synchronization or local-file access to a web session.

> Which practices from my past cases can I use for my candidate product page?

## Optional growth investigation

> Research this brand's social media, creators and SEO. Use public sources without paid APIs, and keep the learning concise.

Read direct posts, launch discussions, creator coverage, search results and relevant content pages. Distinguish observed marketing from suggested mechanisms and unverified performance. Keep a source/query record and one linked `wiki/growth/<brand-id>-growth.md`, without inflating the main case or creating a report per channel.

The [UseIt live public-source example](examples/growth/brain/wiki/growth/useit-growth.md) uses a browser fallback for public X posts plus Product Hunt and outside introductions. No paid data API, login or registration was used; existing host/model/search quotas still apply. Missing creator partnerships, keyword metrics or traffic remain unknown.

[AISA is an optional capability slot](plugins/brand-research-brain/skills/growth-research/references/optional-aisa.md), not an enabled connector. No API key, automatic connection or paid fallback is included. Later enhancement needs the user's explicit request, current capability/price discovery and an enforceable approved budget. The public workflow remains independent of any data vendor.

## LLM Wiki model

This implements Karpathy's LLM Wiki pattern: immutable material in `raw/`, LLM-maintained linked knowledge in `wiki/`, and local operating guides. It is a workflow implementation, not a dependency on a Karpathy package or service.

Cases live in `wiki/brands/`; reusable learning in `wiki/categories/`, `wiki/shopify/`, `wiki/growth/`, and `wiki/ideas/`. `wiki/index.md` is a learning map, `wiki/log.md` a short learning history, and `.brb/` holds mechanical records. Website presentation does not establish effectiveness, sales or causality. Do not assume a studied brand runs on Shopify.

## Compatibility

v0.6.0 preserves the plugin identity and reads v0.1 Brains. New profiles default to Shopify learning with a configurable stage. Existing preferences, guides and notes are not silently migrated. Ask the agent to adopt the learning guide deliberately while preserving personal instructions. The legacy helper remains for historical replay; new sessions use `learn.py` with multiple sources and no required business decision or visible dimension tables. Current saves require background `knowledge_reviews` for all four areas; historical v0.2/v0.3 payloads replay only through an explicit compatibility argument. `mode: growth` saves an optional growth note for an existing brand, without requiring a rewritten main case.

[Case-first ideas](docs/ideas.md): derive an insight and testable hypothesis from the current case before choosing a new note or merge. Merge only when the user problem/mechanism genuinely matches and the evidence adds substance; do not funnel every case into an unrelated old project. Thin evidence can still be retained/skipped. The historical v0.4 reconciliation example remains for mechanical replay, not current behavioral acceptance.

## Development

Runtime helpers use only Python's standard library. YAML validation needs the development dependency:

```sh
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
python3 scripts/validate_repo.py
python3 scripts/replay_examples.py
python3 scripts/replay_learning.py
python3 scripts/replay_growth.py
python3 scripts/replay_reconciliation.py
python3 scripts/package.py
```

The public LiberNovo example is an authored redesign based on previously saved official-page observations, not a fresh live-site audit. Validation distinguishes author review, independent agent testing, deterministic replay, and installed-host behavior. Historical examples retain their original output style for comparison.

The source archive is a standalone repository for GitHub. The plugin archive contains one plugin, its three skills and supporting files. Private evaluation inputs and the surrounding personal vault are excluded. No GitHub publication or directory submission is performed by packaging.

Original code, skills and authored summaries are MIT. Third-party content, sites and trademarks retain their rights: [attribution](THIRD_PARTY.md).

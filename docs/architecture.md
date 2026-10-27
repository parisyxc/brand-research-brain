# Architecture

## Detailed growth presentation (v0.6)

The additive `growth.details` field holds 0–8 chapters with plain-text titles, summaries and up to six items, each with an optional lesson. The renderer validates length/shape, escapes all nested text and creates internal topic navigation. Existing concise payloads remain accepted; the Brain registry and learning save schema are unchanged. References support up to 40 named entries.

Reading mode shows all content below the overview. Card mode presents the overview and topic chapters as independent panels with natural height; native mode controls retain the current reading section. Print styles allow chapter pagination, but rendering HTML is not a verified PDF export. The six main document sections remain, and growth-only protection still preserves the core case fields.

A request to present a completed study is handled from the named Markdown/digest files, without provider calls, credential access, whole-vault copying or research-event writes. The agent maps the study's substantive sections to visible chapters; helper tests validate export mechanics, not semantic completeness. Ordinary intake does not acquire mandatory deep research.

## Concrete learning and focused updates (v0.5.1)

The shared `learning-quality.md` reference guides intake, growth and presentation synthesis toward buying situations, alternatives, concrete methods and test examples. This is an editorial requirement, not an automatic semantic scorer, extra page quota or private user profile. Optional bounded comparison is distinct from deeper growth research.

On an existing HTML digest, `render_share.py --growth-only` checks stable case fields against the prior digest under the writer lock. It rejects topic drift, omission of prior basis and absence of the brand's saved growth note. Current hashes and normal output-edit protection still apply. A normal render remains available for an intentional whole-case revision. No learning event or source schema migration is added.

## HTML digest (v0.5)

After the usual Markdown save/check, the agent reads the saved case and relevant linked notes, creates a concise editorial payload, and runs `brand-intake/scripts/render_share.py`. Both intake and growth instructions require this companion output unless the user opts out. The separate presentation step also works for older cases and duplicate sessions without inventing a research revision. The `learn.py` payload and registry schema are unchanged.

The renderer validates current basis hashes, escapes plain text and fills an offline HTML template. It writes `reports/<brand-id>.html` plus the digest and output receipt in `.brb/share/`. It does not touch Markdown, raw captures, index or events. Hand-edited/unmanaged HTML requires its current hash before replacement. Rendering is repeatable, path constrained, writer locked and individually atomic. Hash validation is freshness protection, not automatic semantic/factual verification.

The document has continuous-reading and card modes, responsive layout and print styles. Material uncertainty remains visible; long source lists and shared limitations go in the final section. No hosting, tracking, paid provider, remote asset, automatic PNG/PDF export or social posting is introduced. Browser inspection and helper tests are recorded separately from agent behavior evaluation.

The plugin owns two core skills and an optional growth research skill, starter guides and deterministic file helpers. A user-selected Brain owns goals, immutable raw material, linked learning and history. Plugin updates do not silently migrate user Brains.

## Learning unit

One bounded website study is one learning session. `learn.py` accepts a brand, a list of contributing sources, the case and optional reusable pages, a short takeaway and one next action. It saves each source separately but updates synthesis/navigation once and adds one short log entry. Source-level metadata stays in raw and the registry.

The case explains the business and three concrete practices. Internally the skill considers selection/insight, product/brand, storefront/conversion, content, acquisition/growth and SEO. This is a reading lens, not six mandatory sections or documents. Reusable notes are merged where they add value. Their links let future questions reuse and compare what has been learned.

## Source preservation

Each source contains origin, observation scope/date, claims with locators, limitations and a concise capture. Exact-record identity is brand + canonical URL/local reference + evidence fields. Observation time and tracking parameters are excluded. Reuse stable captures; semantic deduplication is not provided. Brand aliases prevent simple duplicate naming.

`learn.py` reuses source validation, canonicalization, path guards and atomic writes from the legacy helper. It preflights all input sources and supplied pages, serializes writes with `.brb/intake.lock`, requires current hashes for replacements, and exclusively creates raw snapshots. No captured site scripts are executed. The case must link all contributing sources; reusable notes need evidence and a brand backlink. The index uses page titles/source names rather than bare IDs.

Writes are atomic individually, not a crash-proof transaction across all files. On interruption, inspect registry/raw/wiki before retrying; do not remove an active lock or delete raw sources. The checker validates snapshots, registry and wiki links, not reasoning quality or business truth.

## Compatibility

The `brand-research-brain/v1` storage schema is retained. New profiles add a stage and Shopify learning goal; existing profiles are preserved. Learning events store `source_ids` plus a primary `source_id`, so historical records remain readable. The old v0.1 `intake.py` contract remains available for replay/compatibility, but the active skill uses `learn.py` without dimension reviews or business decisions. Old pages/logs are not removed. Deliberate revisions can convert a selected case while preserving evidence and unrelated notes.

Markdown and vault-root wikilinks work in Obsidian. Claude and Codex can maintain the same files by reading the local guides; there is no bundled synchronization service, Shopify integration or Claude plugin.

## Optional growth session

`growth-research` is triggered by deeper acquisition questions rather than every intake. It investigates social, creator and SEO evidence with public host tools. A bounded query/access record preserves what was searched and what was inaccessible. It saves one concise linked growth note, not a full consulting plan.

`learn.py` accepts `mode: growth` for an existing registered case. Its primary page is `wiki/growth/<brand-id>-growth.md`, which must cite all contributing sources and link to the case. The case may remain byte-identical; an optional supplied update needs the current hash and a link to growth. The registry retains old sources/methods; the log links to the growth note and adds one event. Learning mode and its historical fingerprints are unchanged.

AISA is provider-optional guidance rather than a runtime dependency, enabled connector or key configuration. Public retrieval is the default; paid enhancement requires an explicit user request and budget. No paid fallback or account action is performed by the package.

## Background knowledge reconciliation (v0.4)

Every current learning/growth payload requires exactly four knowledge reviews: categories, ideas, shopify and growth. The agent reads related notes and records an evidence-specific update, retain or skip with paths. `knowledge_review.py` checks coverage, folder classification and update/write agreement. Retained pages must exist and remain unsupplied; page hashes protect replacements.

Reviews are part of synthesis identity and are stored only on the event in `.brb/state.json`. No renderer appends them to cases, navigation or learning logs. The checker validates new review records while accepting historical events without them. This enforces mechanics, not intellectual substance.

Old raw fingerprints and earlier event identities are unchanged. Current CLI saves reject missing reviews. Historical replay uses explicit Python `allow_legacy=True`, never a silent fallback or current skill instruction. Updating old synthesis uses existing source records, current page hashes and an explicit revision; raw and old events stay intact. Starter guides evolve; historical replay compares frozen research rather than assuming earlier guides must match new templates.

## Current-case ideas (v0.4.1)

The agent derives the current case's own evidence-backed insight and testable hypothesis before selecting an idea destination. Existing notes supply context rather than a default framing. A merge requires a shared user problem/mechanism and a substantive new hypothesis or validation question. Cross-case applications remain distinguishable from the originating idea. Unsupported synthesis can be retained/skipped; no new audience/product or file-per-brand requirement is imposed.

This is a reasoning instruction update, not a new schema or a lexical idea detector. The existing ideas review reason records the evidence/hypothesis and destination rationale in the background. Behavioral evaluation, rather than unchanged helper tests alone, assesses the semantic requirement.

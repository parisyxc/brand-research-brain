# Save a learning session (v0.4)

The agent reads and reasons; the standard-library helper handles reliable local file mechanics. One payload represents one website learning session, even when several pages contribute evidence. Use `learn.py`, not the legacy v0.1 `intake.py` command.

```json
{
  "brand": {"id": "example-brand", "name": "Example Brand", "aliases": []},
  "sources": [{
    "type": "official_site",
    "url": "https://example.org/",
    "title": "Example Brand — homepage",
    "publisher": "Example Brand",
    "published_at": null,
    "observed_at": "2026-10-24",
    "access": "partial",
    "limitations": ["Homepage only; no sales data."],
    "capture": "Gift finder: products are grouped by recipient interest.",
    "claims": [{"text": "Gift finder groups products by recipient interest.", "kind": "observed_feature", "locator": "Homepage / Gift finder"}]
  }],
  "pages": [{
    "path": "wiki/brands/example-brand.md",
    "content": "# Example Brand\n\nA limited example: the gift finder groups products by recipient interest. This could help someone choose a gift; its conversion effect is unknown. Try organizing a candidate collection by buying occasion. {{source:0}}\n\n## Sources\n\n{{sources}}\n"
  }],
  "knowledge_reviews": {
    "categories": {"action": "skip", "reason": "The selected excerpt lacks a distinct category problem or tradeoff.", "paths": []},
    "ideas": {"action": "skip", "reason": "The excerpt only shows one navigation feature; it does not support a distinct user or product hypothesis.", "paths": []},
    "shopify": {"action": "skip", "reason": "The selection observation is retained within the case until it adds a reusable method.", "paths": []},
    "growth": {"action": "skip", "reason": "No substantive distribution or acquisition evidence is in the excerpt.", "paths": []}
  },
  "summary": "Learned to organize a gift collection around the buyer's selection problem.",
  "next_action": "Sketch a collection outline for one candidate product."
}
```

The abbreviated example demonstrates payload syntax, not the target depth of a learning note. No business `decision` or visible `dimension_reviews` is needed. Current saves require the four background `knowledge_reviews` below.

## Sources

Use a separate item per contributing page/document, with concise factual captures, evidence locators and limitations. Never copy entire third-party articles into public examples. Sources are immutable original records, not generated case prose. For local files without a URL, use a stable portable `local_ref`, such as `incoming/notes.md`, instead of a user's absolute path. Optional `input_sha256` identifies original input bytes; the helper does not modify that file.

Allowed types: `official_site`, `article`, `clip`, `note`, `document`. Allowed access: `complete`, `partial`, `unavailable`; complete refers to the selected page, not the whole business. With unavailable access, claims must be empty. `published_at` may be null. `observed_at` is an ISO date or a real timestamp with timezone; preserve the original observation date when reusing a saved capture.

Claim kinds are `official_claim`, `reported_claim`, `user_note`, `observed_feature`; each needs `text` and `locator`. Inferences belong in the learning note, not extracted claims. Homepage presence is evidence of presentation, not effectiveness, representative demand, revenue, profit or search traffic.

## Pages and links

The canonical case is `wiki/brands/<brand-id>.md`, where IDs are lowercase hyphenated slugs. Optional notes live directly in `wiki/categories/`, `wiki/shopify/`, `wiki/growth/`, or `wiki/ideas/`. Use vault-root wikilinks with readable labels, e.g. `[[wiki/brands/example-brand|Example Brand]]`.

`{{source:0}}`, `{{source:1}}`, etc. render named links to the corresponding raw records. `{{sources}}` renders all session sources as named links. Put it on its own paragraph with blank lines around it so its first list item renders correctly. The case must cite every contributing source; optional methods need at least one relevant source and a brand backlink. Direct URLs with page/section names are useful near observations. Preserve older citations and user corrections when merging pages.

Existing pages require `expected_sha256`, computed from their current bytes after reading them. Do not overwrite the page using a fresh generic template. The helper edits only supplied pages, managed index sections and its own log/registry. Existing research remains unless explicitly edited.

## Repeat visits and old Brains

Source identity hashes brand + canonical URL/local_ref + evidence fields. Observation dates, tracking parameters and fragments do not create new sources; meaningful query parameters do. Reuse stable captures when evidence has not changed. This is exact-record deduplication, not semantic deduplication.

When all sources are known, default is no-op. Use `--revise` for a deliberate synthesis change or transition of an old case to a learning note. An identical revision is also a no-op. A changed source creates a new snapshot. All pages in a session are written once and the log gets one entry. The registry stores all source IDs in that event.

Existing `brand-research-brain/v1` Brains remain readable; v0.2 adds profile goal/stage defaults only to new Brains. Legacy `intake.py` and its tests remain for historical v0.1 payload replay. Do not use old dimension tables for new learning sessions. Old pages, logs and captures are not automatically migrated or deleted; adopting the new guide in an existing Brain requires a deliberate, preservation-aware update.

The helper preflights paths, citations, aliases, source state, index markers and page hashes, then locks and writes locally. Writes are atomic individually, not a crash-proof multi-file transaction. After interruption, inspect registry/raw/wiki before retrying. Remove a stale `.brb/intake.lock` only after confirming no writer is active.

## Optional growth session (v0.3)

`mode` defaults to `learning`, preserving the v0.2 contract. With `mode: "growth"`, the brand must already have a registered, existing case, and the required primary page becomes `wiki/growth/<brand-id>-growth.md`. Save all contributing social/creator/search/SEO evidence in `sources`; the growth note must cite it all and link to the case. It is valid to supply just the growth page and leave the case untouched. If including the case, read and merge it, provide its current hash, and link to the growth note; new raw-source links need not clutter the case.

The log links to the growth note and records one event for the entire pass. Optional reusable methods still require evidence and a brand backlink. Exact-record deduplication and explicit revisions behave as before. `mode` is part of the synthesis event identity, so a growth revision of already-known evidence is distinct from the earlier learning event.

A compact query/access record can be a `note` source with a portable `local_ref`, author/publisher identifying the research session, observation date, actual query strings/visited URLs, outcomes and access limits. Its `claims` may be empty. It is a record of the investigation, not independent evidence that a channel does not exist. Use per-page official or third-party records for the substantive findings. No new source types or paid dependencies are required.

For an explicit synthesis or formatting revision, make `summary` state what changed instead of repeating the old takeaway; an intentional different-content revision adds an audit/log event, whereas identical repeats do not.

## Required background reconciliation

Every current learning and growth payload has `knowledge_reviews` with exactly `categories`, `ideas`, `shopify`, `growth`. Each has `action`, a concrete nonempty `reason` and a `paths` list:

- `update`: one or more substantive new/merged pages are in `pages` under that same folder. All supplied non-brand pages must be covered, including the primary page in growth mode.
- `retain`: relevant existing pages remain unchanged; list their exact paths and do not include them in `pages`. The helper checks they exist and preserves them.
- `skip`: no useful standalone knowledge for this area yet; paths must be empty. An attractive site or the mere existence of a folder is not sufficient reason to write.

For ideas, first derive an insight and testable hypothesis from the current case's own evidence. Decide on reuse only afterwards: a merge needs the same user problem or mechanism plus a substantive new hypothesis/question. Merely applying a generic page tactic to an unrelated old project does not complete current-case idea synthesis. A separate cross-case application may still be useful, but must not hide the originating idea.

Use the existing ideas `reason` field to state the evidence-to-hypothesis connection and the new-page/merge/retain/skip rationale. No extra schema fields, visible checklist or one-idea-per-brand quota is added. Unsupported ideas can be retained/skipped. Do not invent a market, audience or business just to create a standalone file, and do not claim the user completed a proposed exercise.

Reasons and paths are saved only on the event in `.brb/state.json`. They participate in revision identity but are not appended to any readable wiki page, index, log or final response. Validation enforces mechanical coverage and relationships, not the substantive quality of the judgment.

Old Brains/events remain readable with no automatic migration. The current CLI requires reviews. Historical v0.2/v0.3 frozen examples use explicit Python `allow_legacy=True` only in their replay scripts to preserve earlier output; this is not a current intake path and has no CLI flag. To reconcile an old case, read current notes, supply reviews and hashes, and deliberately revise existing evidence. Raw records and old events remain intact.

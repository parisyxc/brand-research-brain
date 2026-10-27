# A concise Chinese reading document and share-card deck

After each current brand intake or deeper growth pass, deliver the Markdown learning **and** one `reports/<brand-id>.html`. This is an editorial digest of the saved research, not a second research task, another wiki page or a public upload. Reuse the selected Brain. A duplicate intake can still produce a missing HTML without revising Markdown or adding a research event. Honor an explicit user opt-out.

Read the actual saved case and linked category, growth, idea and Shopify notes. Use only relevant evidence, not the whole vault. Preserve the case's existing practices and user corrections when refreshing after growth research. The agent writes the concise synthesis; the renderer only validates inputs and formats it. Never flatten arbitrary Markdown or export background reviews as prose.

Apply [the learning-quality guide](learning-quality.md). This is a reader-facing explanation of the whole case. A later narrow research question must not turn the cover, category, ideas and next action into a report about that question's access limits. Do not copy every qualification from the wiki. Keep factual distinctions while writing simple sentences with a concrete person, product, situation or choice.

## Editorial shape

Default to concise Chinese even when source pages are English; honor the user's requested language. For ordinary intake, aim for about 900–1,400 Chinese characters excluding references. A requested full growth study is allowed to expand below the overview; this target must not discard its substantive learning. Use natural titles and six main sections:

1. **Case facts:** who buys what, the visible offer and how it works. Attribute official prices/claims naturally. A short mechanism chain is an interpretation, not a proven winning formula. No invented revenue, margins or Shopify adoption.
2. **Three concrete methods:** observed detail and a precise adaptation. Use fewer if evidence is thin. Do not replace case-specific practices with generic marketing advice.
3. **Category:** first name the studied brand's own category with actual product examples; then explain its specific innovation/distinctive product role with evidence; only afterwards add a brief transferable takeaway if useful. The title and summary identify the category and highlight. Use the points mainly for the case's mechanisms, not the learner's future designs or implementation concerns. Keep uncertainty when interpreting novelty, demand or scarcity; do not equate a fresh angle with first invention or proven sales causality.
4. **Growth:** observed content/distribution/SEO mechanisms. If no off-site research occurred, say so once. Suggested creator formats or keyword topics must say “可测试 / 待验证”; never present them as the brand's actual tactics or results. Insufficient evidence is a valid short section and does not trigger an unsolicited growth investigation.
5. **Ideas:** the current case's own hypothesis and one small next action; distinguish it from the studied brand's offer and from a chosen business direction.
6. **References at the end:** named public links and one compact scope note. Keep material uncertainty near the affected claim, while moving long citations and shared source limitations here. No source IDs, local paths, hashes, write/skip checks, scoring tables or process commentary in the visible document.

### Deeper growth belongs inside the document

When the saved growth note has substantive phases/examples or the user asks for detailed coverage, read it fully and create a brief coverage map in your working notes. Keep the three overview points for orientation, then add `growth.details`: readable chapters covering the important stages, specific content practices, creator/retail/SEO paths, metrics and limitations, and concrete learner applications. Stage dates must come from evidence; distinguish an interview's retrospective account, an observed campaign and a future plan. A chapter can organize by theme if chronology is unsupported.

All chapters are visible by default in continuous reading. In card mode the overview and each growth chapter become separate screenshot-friendly panels that extend naturally for long content. Keep the six main navigation sections; chapter links help users move inside growth. References stay in the final source section. Do not force a full study into one poster, hide the learning behind collapsed controls or make the user open Markdown to read it. Keep research mechanics concise and usually in the source note; retain numerical scope next to interpretations that depend on it.

A presentation-only refresh uses the existing Markdown and `--growth-only`, creates no research event and consumes no provider quota. Stage only the named Markdown/digest inputs; never copy a whole vault or credential files to prepare a sharing artifact. Do not automatically expand every ordinary intake into deep research.

The cover explains the offer and why this case is interesting. Put buyer/product/visible price or delivery facts in `facts`; move abstract “成立条件” into a short interpretation if needed. Keep category and ideas distinct: category teaches the studied brand's category and why its offer is interesting; ideas develops current-case hypotheses and the learner's application. Both use tangible examples or comparisons rather than only concepts such as “参与感”“交付边界”. A hypothetical example is welcome when clearly framed as a test. Growth should teach an observed tactic or a labeled testable expression, with a compact evidence gap. Follower inventories and same-name exclusions belong in the detailed growth note or source annotation unless central to a specific learning.

The bundled visual direction uses bright lime, deep green, bold headlines and generous space inspired by [Wise](https://wise.com/), with an original layout. Do not copy its logo, proprietary fonts, product imagery or site text. Single offline HTML, inline CSS/JS, system fonts, no remote assets or tracking. Continuous reading is the default; a button switches to screenshot-friendly cards for the six main parts plus any growth chapters. At desktop width short cards target 3:4; long content and narrow screens extend naturally instead of clipping. Print styles support pagination; PNG/PDF export is not claimed unless actually produced. No publication or hosting is implied.

## Save a digest

Read [the sample payload](../assets/share-example.json). All strings are plain text (HTML/Markdown is escaped). Required fields:

- `schema: "brb-share/v1"`, `brand: {id, name}`, `date` (the research date, YYYY-MM-DD).
- `headline`, `dek`; `facts` with 1–4 `{label, text}` items; `formula` with 2–5 short steps.
- `practices` with 1–3 `{title, observed, lesson}` items.
- `category`, `growth`, `ideas`: each has `title`, `summary`, `points` (0–3 `{title, text}` items), optional `caveat`. A material evidence gap belongs in that section's summary or caveat.
- Optional `growth.details`: 0–8 chapters with `title` (max 64 characters), optional `summary` (max 500), and optional `items` (0–6). Each item has `title` (max 80), `text` (max 700) and optional `lesson` (max 400). Each chapter needs a summary or at least one item. These plain-text fields allow depth without changing the other case sections or interpreting arbitrary Markdown/HTML. No fixed chapter/topic count is required.
- `next_action`, `source_note`, and `sources` with 1–40 named `{label, url?, note?}` references. Public URLs only; for private inputs give a generic source label, not a filesystem path. Do not reproduce confidential material in a shareable digest.
- `basis`: all Markdown notes actually used, including the current case, with Brain-relative `path` and their current byte `sha256`. Include raw evidence where needed for specific facts. This provenance is stored only in `.brb/share/`, never embedded in HTML. Hash checking prevents stale-file inputs; it does not verify factual accuracy or entailment.

```sh
python3 scripts/render_share.py --brain /chosen/brain --payload /temporary/share.json
```

The renderer saves `reports/<brand-id>.html`, `.brb/share/<brand-id>.json`, and an output-hash receipt. It never changes raw files, Markdown, registry events or the learning log. Repeated identical rendering is a no-op. On a later research pass, read and merge the existing digest, reread affected notes, update the basis hashes and render again. Do not blindly reuse an old payload. Preserve its still-useful facts and methods while revising changed conclusions.

For a growth-only refresh of an existing digest, use the same complete payload with `--growth-only`. Keep `brand`, `headline`, `dek`, `facts`, `formula`, `practices`, `category`, `ideas` and the case's `next_action` identical. Update `growth`, the observation date, source note/references and fresh basis as needed. The helper rejects accidental changes to the retained learning and omitted prior basis. A growth-specific small action can go inside the growth section. If new evidence actually corrects an offer/method/idea, or the user requests a whole-case rewrite, read the affected notes and deliberately render without this flag. Do not bypass a rejection merely to replace the whole case with the latest research topic. With no prior digest, create the complete case document normally.

```sh
python3 scripts/render_share.py --brain /chosen/brain --payload /temporary/share.json --growth-only
```

Hand-edited or unmanaged HTML is protected: read it before deliberately supplying its current hash with `--expected-sha256`. The writes are individually atomic, not a multi-file transaction. After interruption inspect HTML/payload/receipt before retrying; do not blindly clear a writer lock. A failed digest render does not roll back a successful Markdown save; fix the digest without repeating intake.

## Verify and return

Open the HTML in an available browser. Check real content in reading and card modes, references at the end, working toggle, and absence of clipped/overflowing text. Inspect a narrow viewport if supported, otherwise state it was not visually tested. If no browser is available, validate structure and say visual inspection is pending. Report helper checks, editorial synthesis and browser verification accurately; none is an independent agent forward evaluation.

Return the HTML link first, the case link and concise takeaways. An HTML document is a local shareable file, not a hosted URL or a completed social-media post. Do not upload, contact anyone or add paid APIs.

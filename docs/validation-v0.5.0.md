# v0.5.0 validation

Date: 2026-10-25, Asia/Seoul. Previous record: [v0.4.1](validation-v0.4.1.md).

## Change and boundaries

Intake and deeper growth now require a companion HTML digest after the usual Markdown save, unless the user opts out. The agent synthesizes the saved case and linked knowledge into concise Chinese facts, concrete practices, category, growth and current-case ideas, with references at the end. A separate standard-library renderer writes an offline reading document with card and print styles. The existing learning payload, registry and four-area reconciliation are unchanged.

Rendering creates `reports/<brand-id>.html`, a digest and output receipt in `.brb/share/`. It never rewrites Markdown/raw or adds a research event. Current basis hashes detect stale input; escaped text and safe source URLs prevent supplied markup from executing. Existing hand edits require a deliberate current hash. Semantic accuracy still requires editorial review.

## Checks performed

- 70 helper tests pass, including eight new export tests: preserved Markdown and repeat no-op; stale input before writes; escaped HTML/slot text; unsafe source URLs; traversal and symlinks; protected hand edits; a growth refresh retaining methods; thin evidence with one method.
- Repository validation passes for JSON/YAML, manifest parity, all three skills, local references, Python syntax and public-file boundaries. Validation uses the existing development environment with PyYAML; runtime helpers need only Python's standard library.
- All four frozen payload replays pass without changing earlier outputs. These are mechanical regressions and do not demonstrate the new HTML reasoning behavior.
- Doodle2Life was manually synthesized from the user's saved case and linked research into an actual HTML digest. This is an editorial integration example, not an independent agent forward evaluation or fresh marketing audit. Its private research and artifact remain outside release archives.
- Actual browser checks cover a 1280px desktop page, both mode buttons, six card sections, no horizontal overflow or clipped sections, and all source links placed in the final section. Card height was changed after finding two overflows: long methods/ideas now extend beyond the nominal 3:4 minimum.
- A same-origin 390px iframe preview was visually inspected in reading and card modes. A split cover headline was corrected. This is narrow-layout inspection, not testing on a physical phone. Full mobile section geometry was not measured programmatically.
- Browser print styles are supplied; no final PDF/PNG export or physical print was validated. The shareable artifact is HTML, not a hosted webpage or completed social post.

## Release and local installation

Source and plugin ZIPs are built and integrity checked, including hidden marketplace/compatibility manifests and bundled HTML assets. Extracted source tests/validation and standalone plugin renderer smoke checks are performed separately from browser checks. Private data is excluded.

The existing plugin identity is preserved. The supported local installer reports version 0.5.0. Installed component bytes and renderer behavior are checked separately from new-chat discovery; a newly opened chat has not been independently exercised in this turn.

No GitHub publication, remote API connection, paid data purchase or social posting is performed.

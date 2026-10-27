# v0.1.0 validation record

Date: 2026-10-23, Asia/Seoul.

## Independent skill forward tests

An independent evaluating agent received the packaged skill instructions and raw inputs, without the parent wiki's conclusions or an expected answer. It initialized three separate empty Brains and performed research with the actual shipped helpers.

| Input | Actual behavior observed |
| --- | --- |
| Existing Ruggable article clip | Read the supplied article body. Separated reported product design, estimated financial figures, unverified channel claims, and the owner's interpretation. Kept unconfigured markets and shipping conditions empty. |
| BenShot official homepage URL | Opened the homepage directly with a web retrieval tool. Built a Chinese case from visible content, including the footer's limits on “bulletproof” wording. Kept featured reviews separate from representative user evidence. |
| Existing incomplete Kaleidos clip | Used supplied content only. Identified duplicated templates and missing full text. Did not turn the title into verified business performance. |
| Unchanged BenShot repeat | Returned duplicate; every Brain file remained byte-identical. |
| Deliberate BenShot revision | Preserved the raw snapshot, updated the same case, and produced a second event with one source. |

The initial pass found a rendered-citation revision usability problem and English starter navigation in a Chinese Brain. Both were fixed and independently rechecked in fresh Brains. The follow-up also verified date-only observation metadata, rejection of an invalid local-reference path, and Kaleidos attribution as an unverified excerpt with no extracted authored claims.

The original evaluator had supplied overprecise observation minutes and nonresolving descriptive local references. Those artifacts remain in ignored local test storage. Public replay payloads use observation days, omit those references/private-input hashes, and correct uncertain Kaleidos authorship. These are reviewed exports, not claims that the original evaluator made no mistakes.

Source records retain a stable English interchange structure; Chinese profiles receive Chinese starter guides/navigation and Chinese case synthesis. This is not full localization of every metadata label.

## Public examples and deterministic replay

The source repository includes the reviewed payloads and generated Brains:

- [Ruggable case](../examples/history/v0.1.0/brains/ruggable-article/wiki/brands/ruggable.md)
- [BenShot website case](../examples/history/v0.1.0/brains/benshot-website/wiki/brands/benshot.md)
- [Kaleidos partial-clip case](../examples/history/v0.1.0/brains/kaleidos-partial-clip/wiki/brands/kaleidos.md)

`python3 scripts/replay_examples.py` creates fresh temporary Brains, replays the authored payloads, checks initializer idempotence, repeats each processing step, and validates registry/source/wiki consistency. It preserves one source per case, with two events only for BenShot's deliberate revision. No file changes occur on repeats.

This is reproducible verification of file behavior using fixed syntheses. It does **not** rerun an LLM or re-fetch a website. Public summary fixtures are available for future fresh agent evaluations; complete third-party articles are not distributed.

## Automated checks

25 helper tests cover initialization preservation, empty defaults, Chinese starter output, missing-registry protection, source linking, exact duplicates, tracking parameters, meaningful query parameters, immutable snapshots, explicit revisions, rendered citations, related research preservation, stale edits, malformed index handling, source-local reference validation, path traversal, symlinks, unavailable-source claims, local notes, concurrent lock handling and date precision.

Package validation parses YAML/JSON, checks the two manifests and marketplace paths, validates skill reference files, compiles runtime source, and scans the selected release tree for machine paths, credential patterns and excluded files. Both skills also passed the Skill Creator quick validator.

The two release ZIPs are checked for archive integrity and expected components. Extracted plugin helpers and the extracted source repository replay are smoke-tested separately. These checks establish source/package mechanics, not business insight accuracy.

## Not established by this release

- No fresh installed-host plugin discovery/UI test has been performed. The package has not been installed into the owner's account or submitted to a public plugin directory.
- Live website coverage was one BenShot homepage visit. Product-page traversal, anti-bot challenges, authentication and all browser variants are not exhaustively tested.
- Source deduplication is based on stable evidence records, not semantic similarity. Agent rewriting may produce a new fingerprint.
- Individual atomic writes and locks do not provide a crash-proof transaction across the whole wiki. Backups and inspection remain appropriate for interruption recovery.
- CI is included for Python 3.9 and 3.13 on GitHub; the local run used Python 3.9. Hosted CI has not run until the repository is pushed.

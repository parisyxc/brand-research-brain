# v0.4.1 validation

Date: 2026-10-24, Asia/Seoul. Previous record: [v0.4.0](validation-v0.4.0.md).

## Scope

This patch corrects idea synthesis order: derive an insight/testable hypothesis from the current case, then assess whether an existing note genuinely matches. A substantive new hypothesis/question about the same user problem or mechanism can be merged. Otherwise useful independent learning can get its own note; thin evidence can be retained/skipped. Generic applications to an unrelated old project do not replace the current case's ideas.

Intake and growth instructions, the save-contract guidance and both new-Brain language templates were updated. The contract's old example no longer treats the absence of a prior project as the reason to skip ideas. No schema, runtime helper, paid connector, additional skill, automatic migration or page-per-brand quota was added.

## Historical material

v0.4.0's reconciliation example and independent evaluation are retained as history. They accepted adding Looki page-design tactics to a UseIt card idea. This remains a useful mechanical regression for preservation, reviews and deduplication, but does not demonstrate the new semantic requirement. README now points to [the current idea rule](ideas.md), not that older output as a behavioral answer.

Historical replay compares frozen research independently of evolving starter guides. This patch did not rewrite the user's current Brain or its corrected independent Looki idea.

## Mechanical verification

All 62 existing helper tests pass. No tests were added to mirror instruction wording. All three skills pass Skill Creator validation, and repository validation checks JSON/YAML, references, runtime syntax, manifest parity and public package boundaries. All four offline replays pass.

Mechanical checks establish file handling and contract compatibility, not whether an idea is meaningful or case-derived. A separate skill behavior evaluation addresses that question.

## Independent behavior evaluation

A fresh agent received the revised skill and two realistic requests, with no expected answer or newer idea output: continue learning from the saved Looki Brain, then intake the incomplete Kaleidos fixture. It used only a private baseline and the specified clip, without network or changes to the original user Brain/plugin.

Looki produced a distinct idea about which part of capture, curation and recall is burdensome, with source observations, an explicit hypothesis and unknowns. The old UseIt card idea was byte-identical; the case preserved its older paragraphs and linked the new learning. The output did not pick a target market or pretend that a user exercise had happened. Kaleidos produced only a short case and raw record: no invented sales evidence, no forced three practices and no standalone idea from the thin clip.

All 29 old raw records and five old events were preserved. The two sessions added one clip record and two events, ending with 30 sources and seven events; checker errors were empty. Each session's normal and explicit revision repeats were duplicate with identical file sets/hashes. The agent also ran the 62 helper tests successfully; its repository validation attempt lacked PyYAML in that interpreter, while the primary run used the existing validation environment and passed.

Content review found minor process language in visible notes and a risk of treating reduced priority of memory retrieval as counterevidence to a broader curation/recap hypothesis. Two narrow wording refinements now keep editorial destination rationale in the background and distinguish related-feature evidence from direct hypothesis confirmation/refutation. The actual preserved output predates these refinements and is not claimed as a rerun. [Portable evaluation summary](../examples/idea-first/evaluation.json); full private artifacts remain excluded from release.

## Packaging and installation checks

The release archives are integrity-checked. Extracted source is checked with tests, repository validation and all four replays; standalone packaged helpers are checked with current reviewed intake, missing-review rejection, reconciliation, raw preservation and repeated no-op. Local installation uses the supported plugin flow and preserves plugin identity and enabled state. Installed files and helper behavior are verified separately from new-chat UI discovery.

## Limits

These instructions improve reasoning guidance; there is no heuristic that can prove intellectual independence from a reason string. An evidence-specific background review, sources and actual output still require judgment. No market need, selected audience or business execution is validated merely by creating an idea. No paid API or AISA connection is involved, and no GitHub publication is performed.

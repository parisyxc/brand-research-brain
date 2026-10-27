# Publish v0.6.0 to GitHub

## What is ready

The repository contains a portable plugin, Codex compatibility manifest, Git-backed marketplace catalog, three skills, standard-library helpers, starter Brain, attributed example summaries, local validation scripts and a CI workflow.

No remote repository is assumed or preconfigured. The author name is Paris Young; a GitHub account name and repository URL have deliberately not been invented.

## Create the release files

From this repository root, run the development checks in README, then:

```sh
python3 scripts/package.py
```

Outputs in `dist/`:

- `brand-research-brain-0.6.0-source.zip`: standalone source repository, including hidden marketplace and CI files.
- `brand-research-brain-0.6.0-plugin.zip`: one plugin directory with manifests, skills, supporting files and license.
- `brand-research-brain-0.6.0-claude-plugin.zip`: Claude-specific upload/extraction package, with `.claude-plugin/plugin.json` directly at the ZIP root, skills, README and license.
- `SHA256SUMS`: archive checksums.

The source ZIP excludes `.local/`, caches, any surrounding personal vault and local environment files. Use the source archive or the clean repository tree when creating a GitHub repository. Never publish a parent directory just to preserve the workspace hierarchy.

## Publish

1. Choose a GitHub repository name and visibility. Create the repository from this source tree.
2. Add its real repository URL to the portable manifest's optional `repository` field and mirror that metadata in the compatibility manifest if used. It is safe to omit it for the first release.
3. Run checks again if files changed. Commit the source and tag `v0.6.0`.
4. Use CHANGELOG as the release description and attach the three ZIPs plus checksums if desired.
5. In a separate local agent session, add the actual GitHub repository URL as a marketplace, install, and confirm all three skills are discovered. Record the tested host version.

Source-level forward testing does not establish installed-host discovery. The validation report states which checks actually ran.

The same GitHub source includes both Codex and Claude marketplaces. See [Claude publication and installation](claude-release.md) for supported commands and capability boundaries. No Claude account configuration or installed cache is changed by packaging.

## Directory publication

GitHub distribution does not require submission to OpenAI's universal directory. If that is desired later, follow the current plugin submission requirements, prepare listing assets and review metadata, and test the installed package before submitting. The GitHub source archive is not a directory-upload archive.


The v0.2 learning acceptance example is `examples/learning/brain/`. Both legacy replay and `scripts/replay_learning.py` plus `scripts/replay_growth.py` and `scripts/replay_reconciliation.py` must pass. Original private user test backups stay in `.local/` and are excluded from both archives. Updating source or rebuilding ZIPs does not update an already installed plugin cache.

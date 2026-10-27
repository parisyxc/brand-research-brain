# Developing Brand Research Brain

This directory is an independent open-source plugin repository. Develop the reusable product here; the parent personal research vault is not part of the package. Do not import its user preferences, credentials, raw article bodies, local paths, or supplier files into defaults or public examples.

Keep Python runtime helpers standard-library-only and compatible with Python 3.9+. Keep the portable and Codex compatibility manifests synchronized. Read a skill before changing its helper or contract.

Behavioral evaluation Brains belong in `.local/` or a temporary directory. Use only the inputs named for the evaluation. Evaluate actual outputs; do not replace test observations with hand-authored expected answers. Public fixtures are attributed original summaries, not third-party full text. No automated test needs network access or an API key.

Before delivery run `python3 -m unittest discover -s tests -v` and `python3 scripts/validate_repo.py`. Preserve the distinction between helper tests, agent forward tests, and actual host installation tests. Never report one as the other.

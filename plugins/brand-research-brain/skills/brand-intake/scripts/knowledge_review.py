"""Validate background knowledge reconciliation; no visible wiki rendering."""
import re

FOLDERS = ("categories", "ideas", "shopify", "growth")


def validate(reviews, page_paths):
    if not isinstance(reviews, dict) or set(reviews) != set(FOLDERS):
        raise ValueError("knowledge_reviews must check categories, ideas, shopify and growth")
    written, retained = set(), set()
    for folder in FOLDERS:
        review = reviews[folder]
        if not isinstance(review, dict) or review.get("action") not in {"update", "retain", "skip"}:
            raise ValueError("Invalid knowledge action: " + folder)
        reason = review.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("Evidence-specific knowledge reason required: " + folder)
        paths = review.get("paths")
        if not isinstance(paths, list) or any(not isinstance(p, str) for p in paths):
            raise ValueError("Knowledge paths must be a string list")
        if len(paths) != len(set(paths)) or (review["action"] == "skip") != (not paths):
            raise ValueError("skip needs no paths; update/retain need distinct paths")
        for path in paths:
            if not re.fullmatch(r"wiki/" + folder + r"/[a-z0-9]+(?:-[a-z0-9]+)*\.md", path):
                raise ValueError("Page in wrong knowledge folder: " + path)
            if review["action"] == "update":
                if path not in page_paths:
                    raise ValueError("Reviewed update is missing from pages: " + path)
                written.add(path)
            else:
                if path in page_paths:
                    raise ValueError("Retained page must not be replaced: " + path)
                retained.add(path)
    related = {p for p in page_paths if not p.startswith("wiki/brands/")}
    if written != related:
        raise ValueError("Every related write needs a matching knowledge update review")
    return retained

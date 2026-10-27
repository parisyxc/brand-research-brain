"""Learning sessions preserve evidence while writing once per website visit."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from test_brain import module, init, intake, payload, snapshot, SKILLS

learn = module("learning", SKILLS / "brand-intake/scripts/learn.py")
check = module("learning_check", SKILLS / "brand-intake/scripts/check_brain.py")


def session(count=2):
    old = payload()
    sources = []
    for number in range(count):
        source = copy.deepcopy(old["source"])
        source["url"] = "https://benshot.com/page-" + str(number)
        source["title"] = "Page " + str(number)
        sources.append(source)
    return {"brand": old["brand"], "sources": sources,
            "pages": [{"path": "wiki/brands/benshot.md", "content": "# BenShot\n\nCase learning.\n\n{{sources}}\n"}],
            "knowledge_reviews": {folder: {"action": "skip", "reason": "This fixture has no separate " + folder + " learning.", "paths": []} for folder in ("categories", "ideas", "shopify", "growth")},
            "summary": "Learned how the collection helps buyers choose.", "next_action": "Sketch one collection."}


class LearningTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "brain"
        init.initialize(self.root, language="zh-CN", date="2026-10-24")

    def save(self, data=None, revise=False):
        return learn.commit(self.root, data or session(), "2026-10-24", revise)

    def hashes(self, data):
        for page in data["pages"]:
            target = self.root / page["path"]
            if target.exists():
                page["expected_sha256"] = intake.digest(target.read_bytes())

    def test_many_sources_one_case_one_event_no_visible_checks(self):
        data = session(6)
        self.save(data)
        state = json.loads((self.root / ".brb/state.json").read_text())
        self.assertEqual(len(state["sources"]), 6)
        self.assertEqual(len(state["events"]), 1)
        self.assertEqual(len(state["events"][0]["source_ids"]), 6)
        self.assertEqual(check.check(self.root)["errors"], [])
        self.assertEqual((self.root / "wiki/log.md").read_text().count("<!-- brb:event:"), 1)
        self.assertNotIn("dimension-review", (self.root / "wiki/brands/benshot.md").read_text())
        self.assertNotIn("Decision:", (self.root / "wiki/log.md").read_text())

    def test_repeat_changes_nothing_even_with_new_observation_date(self):
        self.save()
        before = snapshot(self.root)
        data = session()
        for source in data["sources"]:
            source["observed_at"] = "2026-10-25"
            source["url"] += "?utm_source=again"
        self.assertEqual(self.save(data)["status"], "duplicate")
        self.assertEqual(before, snapshot(self.root))

    def test_explicit_revision_preserves_sources_and_then_noops(self):
        self.save()
        raw = {p: p.read_bytes() for p in (self.root / "raw").rglob("*.md")}
        data = session(); data["pages"][0]["content"] += "\nA correction from the learner.\n"
        self.hashes(data)
        self.assertEqual(self.save(data, True)["status"], "revised")
        before = snapshot(self.root)
        self.assertEqual(self.save(data, True)["status"], "duplicate")
        self.assertEqual(snapshot(self.root), before)
        self.assertTrue(all(p.read_bytes() == v for p, v in raw.items()))
        self.assertEqual(check.check(self.root)["events"], 2)

    def test_optional_shopify_note_and_readable_navigation(self):
        data = session()
        data["pages"].append({"path": "wiki/shopify/gift-collections.md", "content": "# Help a buyer choose\n\n[[wiki/brands/benshot|BenShot]] {{source:0}}\n"})
        data["knowledge_reviews"]["shopify"] = {"action":"update","reason":"A reusable collection choice method.","paths":["wiki/shopify/gift-collections.md"]}
        self.save(data)
        self.assertIn("|Help a buyer choose]]", (self.root / "wiki/index.md").read_text())
        self.assertEqual(check.check(self.root)["pages_by_type"]["shopify"], 1)
        self.assertEqual(check.check(self.root)["errors"], [])

    def test_invalid_later_source_fails_before_any_write(self):
        data = session();data["sources"][1]["access"] = "unavailable"
        before = snapshot(self.root)
        with self.assertRaises(ValueError): self.save(data)
        self.assertEqual(before, snapshot(self.root))

    def test_missing_batch_citation_fails_before_any_write(self):
        data = session();data["pages"][0]["content"] = "# Case\n{{source:0}}"
        before = snapshot(self.root)
        with self.assertRaises(ValueError): self.save(data)
        self.assertEqual(before, snapshot(self.root))

    def test_related_page_requires_evidence_and_backlink(self):
        data = session();data["pages"].append({"path": "wiki/shopify/unsupported.md", "content": "# Unsupported\n"})
        before = snapshot(self.root)
        with self.assertRaises(ValueError): self.save(data)
        self.assertEqual(before, snapshot(self.root))

    def test_stale_hash_with_new_source_is_rejected_without_new_raw(self):
        self.save()
        data = session(3);data["pages"][0]["expected_sha256"] = "0" * 64
        before = snapshot(self.root)
        with self.assertRaises(ValueError): self.save(data)
        self.assertEqual(before, snapshot(self.root))

    def test_changed_source_keeps_old_raw_and_unrelated_notes(self):
        self.save()
        raw = {p: p.read_bytes() for p in (self.root / "raw").rglob("*.md")}
        unrelated = self.root / "wiki/ideas/mine.md";unrelated.write_text("My idea")
        data = session();data["sources"][1]["capture"] += " Changed evidence."
        self.hashes(data);self.save(data)
        self.assertTrue(all(p.read_bytes() == v for p, v in raw.items()))
        self.assertEqual(unrelated.read_text(), "My idea")
        self.assertEqual(check.check(self.root)["sources"], 3)

    def test_v01_brain_can_take_learning_revision_without_losing_history(self):
        old = payload();intake.commit(self.root, old, "2026-10-23")
        raw = {p: p.read_bytes() for p in (self.root / "raw").rglob("*.md")}
        data = session();data["sources"] = [old["source"]]
        self.hashes(data)
        self.assertEqual(self.save(data, True)["status"], "revised")
        self.assertTrue(all(p.read_bytes() == v for p, v in raw.items()))
        self.assertEqual(check.check(self.root)["errors"], [])
        state = json.loads((self.root / ".brb/state.json").read_text())
        self.assertIn("dimension_reviews", state["events"][0])
        self.assertEqual(state["events"][1]["type"], "learning_revision")

    def test_unsafe_path_and_symlink_do_not_escape(self):
        data = session();data["pages"].append({"path":"wiki/shopify/../../outside.md", "content":"escape"})
        with self.assertRaises(ValueError): self.save(data)
        outside = Path(self.temp.name) / "outside.md";outside.write_text("keep")
        (self.root / "wiki/brands/benshot.md").symlink_to(outside)
        with self.assertRaises(ValueError): self.save()
        self.assertEqual(outside.read_text(),"keep")

    def test_default_shopify_goal_with_custom_goal_stage_support(self):
        profile = json.loads((self.root / "brain.json").read_text())
        self.assertIn("Shopify", profile["research_goal"])
        self.assertEqual(profile["stage"], "exploring")
        other = Path(self.temp.name) / "custom"
        init.initialize(other,goal="Learn SEO",stage="growing")
        custom = json.loads((other / "brain.json").read_text())
        self.assertEqual((custom["research_goal"],custom["stage"]),("Learn SEO","growing"))

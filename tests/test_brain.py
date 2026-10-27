"""Behavioral invariants for the helpers; reasoning is evaluated separately."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "plugins/brand-research-brain/skills"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    instance = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(instance)
    return instance


init = module("brain_init", SKILLS / "brain-init/scripts/init_brain.py")
intake = module("brand_intake", SKILLS / "brand-intake/scripts/intake.py")


def payload():
    return {
        "brand": {"id": "benshot", "name": "BenShot", "aliases": ["Ben Shot"]},
        "source": {"type": "official_site", "url": "https://benshot.com/",
                   "title": "BenShot homepage", "publisher": "BenShot", "published_at": None,
                   "observed_at": "2026-10-23T17:00:00+09:00", "access": "partial",
                   "limitations": ["Homepage only; no independent performance test."],
                   "capture": "Maker section: the brand describes Wisconsin-made glassware.",
                   "claims": [{"text": "Brand describes Wisconsin production.", "kind": "official_claim", "locator": "Maker section"}]},
        "pages": [{"path": "wiki/brands/benshot.md", "content": "# BenShot\n\nOfficial claim: Wisconsin production. {{source}} — Maker section.\n\nHypothesis: recipient identity may matter.\n\nStudy — costs unknown. Next: collect buyer feedback.\n"}],
        "dimension_reviews": {key: {"action": "skip", "reason": "This short maker excerpt lacks distinct " + key + " evidence.", "paths": []}
                              for key in ("category", "growth", "ideas")},
        "decision": "Study", "summary": "Studied the brand homepage.",
        "next_action": "Collect buyer feedback."}


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


class BrainTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "brain"
        init.initialize(self.root, date="2026-10-23")

    def commit(self, data=None, revise=False):
        return intake.commit(self.root, data or payload(), date="2026-10-23", revise=revise)

    def update_hash(self, data):
        for page in data["pages"]:
            target = self.root / page["path"]
            if target.exists():
                page["expected_sha256"] = intake.digest(target.read_bytes())

    def test_init_is_idempotent_and_does_not_assume_preferences(self):
        before = snapshot(self.root)
        result = init.initialize(self.root, language="zh-CN", markets=["EU"], date="2026-10-24")
        self.assertEqual(result["created"], [])
        self.assertEqual(before, snapshot(self.root))
        profile = json.loads((self.root / "brain.json").read_text())
        self.assertEqual(profile["markets"], [])
        self.assertEqual(profile["constraints"], [])
        self.assertEqual(profile["language"], "auto")

    def test_existing_workspace_instructions_survive_initialization(self):
        other = Path(self.temp.name) / "existing"
        other.mkdir()
        (other / "AGENTS.md").write_text("Owner instructions\n")
        init.initialize(other)
        self.assertEqual((other / "AGENTS.md").read_text(), "Owner instructions\n")
        self.assertTrue((other / "BRAIN.md").exists())

    def test_incompatible_existing_profile_is_untouched(self):
        (self.root / "brain.json").write_text('{"schema":"other"}')
        before = snapshot(self.root)
        with self.assertRaises(ValueError):
            init.initialize(self.root)
        self.assertEqual(before, snapshot(self.root))

    def test_website_intake_links_source_index_log_and_registry(self):
        result = self.commit()
        self.assertEqual(result["status"], "ingested")
        state = json.loads((self.root / ".brb/state.json").read_text())
        source = state["sources"][result["source_id"]]
        self.assertTrue((self.root / source["path"]).exists())
        self.assertIn(source["path"][:-3], (self.root / "wiki/brands/benshot.md").read_text())
        self.assertIn("wiki/brands/benshot", (self.root / "wiki/index.md").read_text())
        self.assertEqual(len(state["events"]), 1)
        self.assertIn("2026-10-23", (self.root / "wiki/log.md").read_text())
        for dimension in ("category", "growth", "ideas"):
            reason = state["events"][0]["dimension_reviews"][dimension]["reason"]
            self.assertIn(reason, (self.root / "wiki/brands/benshot.md").read_text())
            self.assertIn(reason, (self.root / "wiki/log.md").read_text())

    def test_repeat_tracking_and_observation_date_do_not_mutate(self):
        self.commit()
        before = snapshot(self.root)
        data = payload()
        data["source"]["url"] = "https://benshot.com/?utm_source=test#top"
        data["source"]["observed_at"] = "2026-10-24T17:00:00+09:00"
        self.assertEqual(self.commit(data)["status"], "duplicate")
        self.assertEqual(before, snapshot(self.root))

    def test_meaningful_query_parameters_remain_distinct(self):
        self.assertNotEqual(intake.canonical_url("https://example.org/?product=one"),
                            intake.canonical_url("https://example.org/?product=two"))

    def test_changed_capture_updates_one_brand_and_preserves_old_snapshot(self):
        self.commit()
        old = {str(p): p.read_bytes() for p in (self.root / "raw").rglob("*.md")}
        data = payload()
        data["source"]["capture"] += " Collection section: additional product formats."
        self.update_hash(data)
        self.commit(data)
        state = json.loads((self.root / ".brb/state.json").read_text())
        self.assertEqual(len(state["sources"]), 2)
        self.assertEqual(len(state["brands"]), 1)
        self.assertTrue(all(Path(p).read_bytes() == content for p, content in old.items()))

    def test_revision_is_explicit_and_idempotent(self):
        self.commit()
        data = payload()
        data["pages"][0]["content"] += "\nQuestion: what does packaging weigh?\n"
        self.update_hash(data)
        self.assertEqual(self.commit(data)["status"], "duplicate")
        self.assertEqual(self.commit(data, revise=True)["status"], "revised")
        before = snapshot(self.root)
        self.assertEqual(self.commit(data, revise=True)["status"], "duplicate")
        self.assertEqual(before, snapshot(self.root))
        state = json.loads((self.root / ".brb/state.json").read_text())
        self.assertEqual(len(state["sources"]), 1)
        self.assertEqual(len(state["events"]), 2)

    def test_stale_edit_fails_without_mutating(self):
        self.commit()
        data = payload()
        data["source"]["capture"] += " Changed evidence."
        data["pages"][0]["expected_sha256"] = "0" * 64
        before = snapshot(self.root)
        with self.assertRaises(ValueError):
            self.commit(data)
        self.assertEqual(before, snapshot(self.root))

    def test_user_navigation_and_unrelated_pages_survive(self):
        index = self.root / "wiki/index.md"
        index.write_text(index.read_text() + "\nOwner's custom navigation\n")
        unrelated = self.root / "wiki/ideas/other.md"
        unrelated.write_text("Owner's unrelated research\n")
        self.commit()
        self.assertIn("Owner's custom navigation", index.read_text())
        self.assertEqual(unrelated.read_text(), "Owner's unrelated research\n")

    def test_invalid_index_fails_before_any_source_write(self):
        (self.root / "wiki/index.md").write_text("# Custom index without markers\n")
        before = snapshot(self.root)
        with self.assertRaises(ValueError):
            self.commit()
        self.assertEqual(before, snapshot(self.root))

    def test_path_traversal_is_rejected_before_mutation(self):
        data = payload()
        data["pages"].append({"path": "wiki/ideas/../../../outside.md", "content": "Escape"})
        before = snapshot(self.root)
        with self.assertRaises(ValueError):
            self.commit(data)
        self.assertEqual(before, snapshot(self.root))
        self.assertFalse((Path(self.temp.name) / "outside.md").exists())

    def test_symlink_page_is_not_followed(self):
        external = Path(self.temp.name) / "outside.md"
        external.write_text("Do not change")
        (self.root / "wiki/brands/benshot.md").symlink_to(external)
        with self.assertRaises(ValueError):
            self.commit()
        self.assertEqual(external.read_text(), "Do not change")

    def test_source_symlink_is_not_followed(self):
        external = Path(self.temp.name) / "outside"
        external.mkdir()
        (self.root / "raw/sources/benshot").symlink_to(external, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.commit()
        self.assertEqual(list(external.iterdir()), [])

    def test_alias_collision_does_not_create_second_brand(self):
        self.commit()
        data = payload()
        data["brand"]["id"] = "ben-shot"
        data["pages"][0]["path"] = "wiki/brands/ben-shot.md"
        with self.assertRaises(ValueError):
            self.commit(data)
        self.assertFalse((self.root / "wiki/brands/ben-shot.md").exists())

    def test_unavailable_source_cannot_extract_facts(self):
        data = payload()
        data["source"]["access"] = "unavailable"
        with self.assertRaises(ValueError):
            self.commit(data)
        data["source"]["claims"] = []
        data["source"]["capture"] = "Retrieval failed; no source body was read."
        data["pages"][0]["content"] = "# BenShot\n\nSource unavailable: {{source}}.\n\nStudy. Next: obtain readable source.\n"
        self.assertEqual(self.commit(data)["status"], "ingested")

    def test_local_clip_does_not_require_a_url_or_change_input(self):
        source = Path(self.temp.name) / "clip.md"
        source.write_text("An owner's short note.\n")
        original = source.read_bytes()
        data = payload()
        data["source"].pop("url")
        data["source"].update(type="note", local_ref="incoming/clip.md",
                              input_sha256=intake.digest(original), capture="Owner's short note.",
                              claims=[{"text": "Owner saved a note.", "kind": "user_note", "locator": "Supplied note"}])
        self.commit(data)
        self.assertEqual(source.read_bytes(), original)

    def test_lock_prevents_overlapping_writer(self):
        (self.root / ".brb/intake.lock").write_text("Existing writer")
        before = snapshot(self.root)
        with self.assertRaises(ValueError):
            self.commit()
        self.assertEqual(before, snapshot(self.root))

    def test_capture_date_requires_timezone(self):
        data = payload()
        data["source"]["observed_at"] = "2026-10-23T17:00:00"
        with self.assertRaises(ValueError):
            self.commit(data)

    def test_date_only_observation_is_supported_without_invented_precision(self):
        data = payload()
        data["source"]["observed_at"] = "2026-10-23"
        self.assertEqual(self.commit(data)["status"], "ingested")

    def test_rendered_source_link_can_be_reused_in_revision(self):
        self.commit()
        data = payload()
        data["pages"][0]["content"] = (self.root / "wiki/brands/benshot.md").read_text() + "\nNew question: gift use frequency?\n"
        self.update_hash(data)
        self.assertEqual(self.commit(data, revise=True)["status"], "revised")

    def test_invalid_local_reference_is_checked_even_with_url(self):
        data = payload()
        data["source"]["local_ref"] = "../outside.md"
        with self.assertRaises(ValueError):
            self.commit(data)

    def test_chinese_starter_is_localized(self):
        other = Path(self.temp.name) / "chinese"
        init.initialize(other, language="zh-CN", date="2026-10-23")
        self.assertTrue(any("\u4e00" <= c <= "\u9fff" for c in (other / "wiki/index.md").read_text()))
        self.assertTrue(any("\u4e00" <= c <= "\u9fff" for c in (other / "BRAIN.md").read_text()))

    def test_missing_registry_is_not_silently_reset_over_existing_research(self):
        self.commit()
        (self.root / ".brb/state.json").unlink()
        before = snapshot(self.root)
        with self.assertRaises(ValueError):
            init.initialize(self.root)
        self.assertEqual(before, snapshot(self.root))

    def test_related_research_survives_new_source_for_same_brand(self):
        first = payload()
        first["pages"].append({"path": "wiki/categories/giftware.md", "content": "# Giftware\n\nA category hypothesis from {{source}}. Brand: [[wiki/brands/benshot]].\n"})
        first["dimension_reviews"]["category"] = {"action": "write", "reason": "A distinct gift category hypothesis.", "paths": ["wiki/categories/giftware.md"]}
        self.commit(first)
        category_before = (self.root / "wiki/categories/giftware.md").read_bytes()
        second = payload()
        second["source"]["capture"] += " One additional listing was observed."
        second["dimension_reviews"]["category"] = {"action": "retain", "reason": "The additional listing does not change the category hypothesis.", "paths": ["wiki/categories/giftware.md"]}
        self.update_hash(second)
        self.commit(second)
        self.assertEqual(category_before, (self.root / "wiki/categories/giftware.md").read_bytes())
        self.assertIn("wiki/categories/giftware", (self.root / "wiki/index.md").read_text())

    def test_every_dimension_must_be_reviewed_before_mutation(self):
        for key in ("category", "growth", "ideas"):
            data = payload()
            del data["dimension_reviews"][key]
            before = snapshot(self.root)
            with self.assertRaises(ValueError):
                self.commit(data)
            self.assertEqual(before, snapshot(self.root))

    def test_written_page_cannot_be_hidden_behind_skip(self):
        data = payload()
        data["pages"].append({"path": "wiki/ideas/gift-choice.md", "content": "# Idea\n{{source}} [[wiki/brands/benshot]]"})
        with self.assertRaises(ValueError):
            self.commit(data)

    def test_retained_page_must_exist(self):
        data = payload()
        data["dimension_reviews"]["ideas"] = {"action": "retain", "reason": "Relevant hypothesis.", "paths": ["wiki/ideas/missing.md"]}
        before = snapshot(self.root)
        with self.assertRaises(ValueError):
            self.commit(data)
        self.assertEqual(before, snapshot(self.root))

    def test_dimension_paths_cannot_cross_directories(self):
        data = payload()
        data["dimension_reviews"]["category"] = {"action": "retain", "reason": "Relevant.", "paths": ["wiki/growth/wrong.md"]}
        with self.assertRaises(ValueError):
            self.commit(data)

    def multipage_payload(self):
        data = payload()
        for key, folder in intake.DIMENSIONS.items():
            path = "wiki/" + folder + "/gift-research.md"
            data["pages"].append({"path": path, "content": "# Gift research\n\nEvidence: {{source}}. Brand: [[wiki/brands/benshot]].\n\nHypothesis pending user validation.\n"})
            data["dimension_reviews"][key] = {"action": "write", "reason": "Distinct " + key + " synthesis is justified.", "paths": [path]}
        return data

    def test_four_page_output_and_update_preserve_original_sources(self):
        data = self.multipage_payload()
        self.commit(data)
        brand_page = (self.root / "wiki/brands/benshot.md").read_text()
        for key, folder in intake.DIMENSIONS.items():
            self.assertIn("wiki/" + folder + "/gift-research", brand_page)
        raw_before = {str(p): p.read_bytes() for p in (self.root / "raw").rglob("*.md")}
        revised = copy.deepcopy(data)
        for page in revised["pages"]:
            page["content"] = (self.root / page["path"]).read_text() + "\nA user correction is preserved here.\n"
        self.update_hash(revised)
        self.commit(revised, revise=True)
        self.assertEqual(raw_before, {str(p): p.read_bytes() for p in (self.root / "raw").rglob("*.md")})
        state = json.loads((self.root / ".brb/state.json").read_text())
        self.assertEqual(len(state["events"]), 2)
        self.assertEqual(len(list((self.root / "wiki").rglob("gift-research.md"))), 3)
        self.assertEqual(state["events"][-1]["dimension_reviews"], revised["dimension_reviews"])

    def test_related_page_requires_source_and_brand_backlink(self):
        for remove in ("{{source}}", "[[wiki/brands/benshot]]"):
            data = self.multipage_payload()
            data["pages"][1]["content"] = data["pages"][1]["content"].replace(remove, "")
            before = snapshot(self.root)
            with self.assertRaises(ValueError):
                self.commit(data)
            self.assertEqual(before, snapshot(self.root))

    def test_review_only_revision_keeps_source_and_records_decision(self):
        data = payload()
        self.commit(data)
        data["dimension_reviews"]["category"]["reason"] = "Review confirms the selected maker excerpt cannot establish a category pain point."
        self.update_hash(data)
        self.assertEqual(self.commit(data, revise=True)["status"], "revised")
        state = json.loads((self.root / ".brb/state.json").read_text())
        self.assertEqual(len(state["sources"]), 1)
        self.assertEqual(len(state["events"]), 2)


if __name__ == "__main__":
    unittest.main()

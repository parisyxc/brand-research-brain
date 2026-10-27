"""HTML exports preserve research, reject stale input and escape untrusted text."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from test_brain import module, SKILLS

share = module("sharing", SKILLS / "brand-intake/scripts/render_share.py")


class ShareTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        case = self.root / "wiki/brands/example-brand.md"
        case.parent.mkdir(parents=True)
        case.write_text("# Example Brand\n\nOriginal case with a user correction.\n")
        self.case = case
        self.data = json.loads((SKILLS / "brand-intake/assets/share-example.json").read_text())
        self.data["basis"][0]["sha256"] = hashlib.sha256(case.read_bytes()).hexdigest()

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}

    def test_render_and_repeat_preserve_notes_and_keep_basis_out_of_html(self):
        original = self.case.read_bytes()
        result = share.save(self.root, self.data)
        output = self.root / result["html"]
        body = output.read_text()
        self.assertEqual(original, self.case.read_bytes())
        self.assertNotIn("wiki/brands/", body)
        self.assertNotIn(self.data["basis"][0]["sha256"], body)
        self.assertIn('id="cards-mode"', body)
        self.assertIn('id="sources"', body)
        self.assertEqual(body.count('<section class="sheet '), 6)
        before = self.snapshot()
        self.assertEqual(share.save(self.root, self.data)["status"], "unchanged")
        self.assertEqual(before, self.snapshot())

    def test_stale_basis_fails_before_writing(self):
        self.case.write_text("# Changed since the editorial draft\n")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "current basis"):
            share.save(self.root, self.data)
        self.assertEqual(before, self.snapshot())

    def test_supplied_markup_and_slot_like_text_are_never_executed(self):
        self.data["headline"] = '<script>alert("x")</script> @@SOURCES@@'
        self.data["sources"][0]["label"] = '<img src=x onerror="alert(1)">'
        share.save(self.root, self.data)
        body = (self.root / "reports/example-brand.html").read_text()
        self.assertNotIn('<script>alert("x")', body)
        self.assertNotIn('<img src=x', body)
        self.assertIn('&lt;script&gt;', body)
        self.assertIn('@@SOURCES@@', body)

    def test_script_file_and_credential_urls_rejected(self):
        for url in ('javascript:alert(1)', 'file:///private/input.md', 'https://user:secret@example.org/', 'https://example.org/ bad'):
            data = copy.deepcopy(self.data)
            data["sources"][0]["url"] = url
            with self.assertRaisesRegex(ValueError, "HTTP"):
                share.save(self.root, data)
        self.assertFalse((self.root / "reports").exists())

    def test_basis_traversal_and_symlink_rejected(self):
        self.data["basis"].append({"path":"wiki/../../outside.md", "sha256":"0" * 64})
        with self.assertRaisesRegex(ValueError, "inside"):
            share.save(self.root, self.data)
        self.data["basis"].pop()
        (self.root / "reports").symlink_to(self.root / "wiki", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            share.save(self.root, self.data)

    def test_manual_html_edits_require_deliberate_current_hash(self):
        share.save(self.root, self.data)
        target = self.root / "reports/example-brand.html"
        target.write_text(target.read_text() + '<!-- personal edit -->')
        self.data["dek"] = 'A new synthesis.'
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "edited"):
            share.save(self.root, self.data)
        self.assertEqual(before, self.snapshot())
        expected = hashlib.sha256(target.read_bytes()).hexdigest()
        self.assertEqual(share.save(self.root, self.data, expected)["status"], "rendered")

    def test_growth_refresh_preserves_methods_and_checks_new_basis(self):
        share.save(self.root, self.data)
        methods = copy.deepcopy(self.data["practices"])
        growth = self.root / "wiki/growth/example-brand-growth.md"
        growth.parent.mkdir()
        growth.write_text("# New growth evidence\n")
        self.data["basis"].append({"path":"wiki/growth/example-brand-growth.md", "sha256":hashlib.sha256(growth.read_bytes()).hexdigest()})
        self.data["growth"]["summary"] = 'New evidence, not a rewritten case.'
        share.save(self.root, self.data)
        saved = json.loads((self.root / ".brb/share/example-brand.json").read_text())
        self.assertEqual(methods, saved["practices"])
        self.assertIn('New evidence', (self.root / 'reports/example-brand.html').read_text())
        self.assertFalse((self.root / 'wiki/log.md').exists())

    def test_thin_evidence_keeps_one_method_without_fabricating_extra(self):
        share.save(self.root, self.data)
        body = (self.root / "reports/example-brand.html").read_text()
        self.assertEqual(body.count('<article class="practice">'), 1)
        self.assertIn('1 个具体做法', body)

    def growth_payload(self):
        data = copy.deepcopy(self.data)
        growth = self.root / "wiki/growth/example-brand-growth.md"
        growth.parent.mkdir(parents=True, exist_ok=True)
        growth.write_text("# A saved growth observation\n")
        data["basis"].append({"path":"wiki/growth/example-brand-growth.md", "sha256":hashlib.sha256(growth.read_bytes()).hexdigest()})
        data["growth"]["summary"] = "A specific new growth observation."
        data["date"] = "2026-10-26"
        return data

    def test_growth_only_updates_one_subject_and_repeats_without_writes(self):
        share.save(self.root, self.data)
        data = self.growth_payload()
        self.assertEqual(share.save(self.root, data, growth_only=True)["status"], "rendered")
        saved = json.loads((self.root / ".brb/share/example-brand.json").read_text())
        self.assertEqual(saved["headline"], self.data["headline"])
        self.assertEqual(saved["ideas"], self.data["ideas"])
        self.assertEqual(saved["next_action"], self.data["next_action"])
        before = self.snapshot()
        self.assertEqual(share.save(self.root, data, growth_only=True)["status"], "unchanged")
        self.assertEqual(before, self.snapshot())

    def test_growth_only_rejects_topic_drift_before_writes(self):
        share.save(self.root, self.data)
        data = self.growth_payload()
        for key, value in (("headline", "No evidence for a growth engine"), ("ideas", dict(data["ideas"], title="Only check accounts")), ("next_action", "Replace product learning with posting"), ("practices", [dict(data["practices"][0], title="Only verify accounts")])):
            changed = copy.deepcopy(data)
            changed[key] = value
            before = self.snapshot()
            with self.assertRaisesRegex(ValueError, "retain case learning"):
                share.save(self.root, changed, growth_only=True)
            self.assertEqual(before, self.snapshot())

    def test_growth_only_needs_saved_growth_and_retains_prior_basis(self):
        share.save(self.root, self.data)
        with self.assertRaisesRegex(ValueError, "saved growth note"):
            share.save(self.root, self.data, growth_only=True)
        other = self.root / "wiki/categories/example-task.md"
        other.parent.mkdir()
        other.write_text("# Prior category evidence\n")
        self.data["basis"].append({"path":"wiki/categories/example-task.md", "sha256":hashlib.sha256(other.read_bytes()).hexdigest()})
        share.save(self.root, self.data)
        data = self.growth_payload()
        data["basis"] = [b for b in data["basis"] if b["path"] != "wiki/categories/example-task.md"]
        with self.assertRaisesRegex(ValueError, "retain prior basis"):
            share.save(self.root, data, growth_only=True)

    def test_deliberate_whole_case_revision_remains_available(self):
        data = self.growth_payload()
        with self.assertRaisesRegex(ValueError, "existing digest"):
            share.save(self.root, data, growth_only=True)
        share.save(self.root, self.data)
        data["headline"] = "A deliberate correction to the offer"
        self.assertEqual(share.save(self.root, data)["status"], "rendered")

    def test_detailed_growth_is_visible_with_lessons_and_preserves_case(self):
        share.save(self.root, self.data)
        data = self.growth_payload()
        data["growth"]["details"] = [
            {"title":"Early launch", "summary":"Founder-led experiments.", "items":[{"title":"A real customer question", "text":"Show the product answering the question.", "lesson":"Try one repeatable demonstration."}]},
            {"title":"Later distribution", "items":[{"title":"A disclosed creator collaboration", "text":"Explain the buying occasion and destination."}]}
        ]
        share.save(self.root, data, growth_only=True)
        body = (self.root / 'reports/example-brand.html').read_text()
        for value in ('Early launch', 'Founder-led experiments.', 'A real customer question', 'Try one repeatable demonstration.', 'Later distribution', 'A disclosed creator collaboration'):
            self.assertIn(value, body)
        self.assertIn('href="#growth-detail-1"', body)
        self.assertIn('id="growth-detail-2"', body)
        self.assertNotIn('<details', body)
        saved = json.loads((self.root / '.brb/share/example-brand.json').read_text())
        self.assertEqual(saved['practices'], self.data['practices'])
        self.assertFalse((self.root / 'wiki/log.md').exists())
        before = self.snapshot()
        self.assertEqual(share.save(self.root, data, growth_only=True)['status'], 'unchanged')
        self.assertEqual(before, self.snapshot())

    def test_nested_growth_text_is_escaped_without_slot_substitution(self):
        data = self.growth_payload()
        data['growth']['details'] = [{'title':'<script>alert(1)</script>', 'items':[{'title':'<b>Untrusted</b>', 'text':'<img src=x onerror=alert(1)>', 'lesson':'@@SOURCES@@'}]}]
        share.save(self.root, data)
        body = (self.root / 'reports/example-brand.html').read_text()
        self.assertNotIn('<script>alert(1)', body)
        self.assertNotIn('<img src=x', body)
        self.assertIn('&lt;b&gt;Untrusted&lt;/b&gt;', body)
        self.assertIn('@@SOURCES@@', body)

    def test_invalid_growth_chapters_fail_before_any_write(self):
        for details in ([{'title':'Empty'}], [{'title':'Bad item', 'items':['wrong shape']}], ['wrong shape'], [{'title':'Missing text', 'items':[{'title':'Only title'}]}]):
            data = copy.deepcopy(self.data)
            data['growth']['details'] = details
            before = self.snapshot()
            with self.assertRaises(ValueError):
                share.save(self.root, data)
            self.assertEqual(before, self.snapshot())

    def test_deep_research_can_retain_more_than_twenty_references(self):
        self.data['sources'] = [{'label':'Source '+str(i), 'url':'https://example.org/research/'+str(i)} for i in range(25)]
        share.save(self.root, self.data)
        body = (self.root / 'reports/example-brand.html').read_text()
        self.assertIn('Source 24</a>', body)


if __name__ == '__main__':
    unittest.main()

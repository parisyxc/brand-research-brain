"""Every current save reconciles four knowledge areas without visible checklists."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from test_brain import init,intake,snapshot
from test_learning import learn,check,session


class KnowledgeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'brain';init.initialize(self.root,date='2026-10-24')

    def save(self,data,revise=False):return learn.commit(self.root,data,'2026-10-24',revise)

    def test_missing_area_or_empty_reason_rejected_before_mutation(self):
        for mutate in ['missing','partial','reason']:
            data=session()
            if mutate=='missing':del data['knowledge_reviews']
            elif mutate=='partial':del data['knowledge_reviews']['ideas']
            else:data['knowledge_reviews']['ideas']['reason']=' '
            before=snapshot(self.root)
            with self.assertRaises(ValueError):self.save(data)
            self.assertEqual(before,snapshot(self.root))

    def test_empty_area_can_skip_without_filler(self):
        self.save(session());result=check.check(self.root)
        self.assertEqual(result['errors'],[])
        self.assertEqual(result['pages_by_type'],{'brands':1,'categories':0,'growth':0,'ideas':0})
        event=json.loads((self.root/'.brb/state.json').read_text())['events'][-1]
        self.assertEqual(set(event['knowledge_reviews']),{'categories','ideas','shopify','growth'})

    def test_review_reasons_stay_in_registry_only(self):
        data=session();marker='Private-reconciliation-rationale-347'
        for review in data['knowledge_reviews'].values():review['reason']=marker
        self.save(data)
        self.assertIn(marker,(self.root/'.brb/state.json').read_text())
        for page in (self.root/'wiki').rglob('*.md'):self.assertNotIn(marker,page.read_text())

    def test_page_write_must_match_area_update(self):
        data=session();data['pages'].append({'path':'wiki/categories/job.md','content':'# User job\n[[wiki/brands/benshot]] {{source:0}}'})
        before=snapshot(self.root)
        with self.assertRaises(ValueError):self.save(data)
        self.assertEqual(before,snapshot(self.root))
        data['knowledge_reviews']['categories']={'action':'update','reason':'A distinct recurring job.','paths':['wiki/categories/job.md']}
        self.assertEqual(self.save(data)['status'],'ingested')
        self.assertEqual(check.check(self.root)['errors'],[])

    def test_wrong_folder_or_unwritten_update_is_rejected(self):
        for paths in [['wiki/ideas/not-category.md'],['wiki/categories/unwritten.md']]:
            data=session();data['knowledge_reviews']['categories']={'action':'update','reason':'Fixture category.','paths':paths}
            before=snapshot(self.root)
            with self.assertRaises(ValueError):self.save(data)
            self.assertEqual(before,snapshot(self.root))

    def test_retain_requires_existing_unchanged_page_and_links_it_in_state(self):
        data=session();path='wiki/ideas/existing.md';data['knowledge_reviews']['ideas']={'action':'retain','reason':'Existing idea has no new learning.','paths':[path]}
        before=snapshot(self.root)
        with self.assertRaises(ValueError):self.save(data)
        self.assertEqual(before,snapshot(self.root))
        target=self.root/path;target.write_text('# My original idea\n')
        self.save(data);self.assertEqual(target.read_text(),'# My original idea\n')
        self.assertIn(path,json.loads((self.root/'.brb/state.json').read_text())['brands']['benshot']['pages'])

    def test_retained_page_cannot_also_be_written(self):
        data=session();path='wiki/shopify/method.md';(self.root/path).write_text('# Existing method')
        data['pages'].append({'path':path,'content':'# Replacement\n[[wiki/brands/benshot]] {{source:0}}'})
        data['knowledge_reviews']['shopify']={'action':'retain','reason':'No change.','paths':[path]}
        before=snapshot(self.root)
        with self.assertRaises(ValueError):self.save(data)
        self.assertEqual(before,snapshot(self.root))

    def test_old_case_gets_background_revision_without_new_raw(self):
        old=session();del old['knowledge_reviews']
        learn.commit(self.root,old,'2026-10-24',allow_legacy=True)
        raw={p:p.read_bytes() for p in (self.root/'raw').rglob('*.md')}
        data=session();data['pages'][0]['expected_sha256']=intake.digest((self.root/'wiki/brands/benshot.md').read_bytes())
        self.assertEqual(self.save(data,True)['status'],'revised')
        self.assertTrue(all(p.read_bytes()==b for p,b in raw.items()))
        before=snapshot(self.root);self.assertEqual(self.save(data,True)['status'],'duplicate');self.assertEqual(before,snapshot(self.root))
        self.assertEqual(check.check(self.root)['events'],2)

    def test_review_only_revision_changes_registry_without_visible_table(self):
        data=session();self.save(data)
        data['knowledge_reviews']['ideas']['reason']='Read the current project; no distinct transfer yet.'
        data['pages'][0]['expected_sha256']=intake.digest((self.root/'wiki/brands/benshot.md').read_bytes())
        self.assertEqual(self.save(data,True)['status'],'revised')
        self.assertNotIn('Read the current project',(self.root/'wiki/log.md').read_text())
        self.assertEqual(check.check(self.root)['events'],2)

    def test_checker_detects_invalid_new_review_but_accepts_legacy_events(self):
        self.save(session());path=self.root/'.brb/state.json';state=json.loads(path.read_text())
        del state['events'][-1]['knowledge_reviews']['growth'];path.write_text(json.dumps(state))
        self.assertTrue(any('background knowledge review' in x for x in check.check(self.root)['errors']))
        del state['events'][-1]['knowledge_reviews'];path.write_text(json.dumps(state))
        self.assertEqual(check.check(self.root)['errors'],[])

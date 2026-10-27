"""Opt-in growth sessions add off-site learning without bloating the case."""
import json
from pathlib import Path
import tempfile
import unittest
from test_brain import module, init, intake, snapshot, SKILLS
from test_learning import learn, check, session


def growth():
    data = session(1)
    data['mode'] = 'growth'
    data['sources'][0]['url'] = 'https://example.org/brand-launch'
    data['sources'][0]['capture'] = 'Public launch discussion and a first-party signup incentive.'
    data['pages'] = [{'path':'wiki/growth/benshot-growth.md',
        'content':'# BenShot growth\n\n[[wiki/brands/benshot|BenShot]]\n\n{{sources}}\n'}]
    data['knowledge_reviews']['growth'] = {'action':'update','reason':'An actual launch adds a growth pattern.','paths':['wiki/growth/benshot-growth.md']}
    data['summary'] = 'Learned from an actual public launch.'
    data['next_action'] = 'Draft one product introduction for my store.'
    return data


class GrowthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'brain'
        init.initialize(self.root,date='2026-10-24')
        learn.commit(self.root,session(),'2026-10-24')

    def save(self,data=None,revise=False):
        return learn.commit(self.root,data or growth(),'2026-10-24',revise)

    def test_growth_only_preserves_case_raw_and_methods_adds_one_event(self):
        method=self.root/'wiki/growth/my-method.md';method.write_text('Existing research')
        old_raw={p:p.read_bytes() for p in (self.root/'raw').rglob('*.md')}
        old_case=(self.root/'wiki/brands/benshot.md').read_bytes()
        self.assertEqual(self.save()['status'],'ingested')
        self.assertEqual((self.root/'wiki/brands/benshot.md').read_bytes(),old_case)
        self.assertTrue(all(p.read_bytes()==b for p,b in old_raw.items()))
        self.assertEqual(method.read_text(),'Existing research')
        result=check.check(self.root);self.assertEqual(result['errors'],[])
        self.assertEqual(result['events'],2)
        log=(self.root/'wiki/log.md').read_text()
        self.assertIn('wiki/growth/benshot-growth|BenShot growth',log)
        self.assertEqual(log.count('<!-- brb:event:'),2)
        state=json.loads((self.root/'.brb/state.json').read_text())
        self.assertEqual(state['events'][-1]['type'],'growth')
        self.assertIn('wiki/growth/benshot-growth.md',state['brands']['benshot']['pages'])

    def test_growth_requires_registered_case_before_writing(self):
        other=Path(self.temp.name)/'empty';init.initialize(other)
        before=snapshot(other)
        with self.assertRaises(ValueError):learn.commit(other,growth(),'2026-10-24')
        self.assertEqual(before,snapshot(other))

    def test_wrong_primary_or_missing_brand_link_fails_without_writes(self):
        for change in ['path','backlink']:
            data=growth()
            if change=='path':data['pages'][0]['path']='wiki/growth/another-name.md'
            else:data['pages'][0]['content']='# No brand\n{{sources}}'
            before=snapshot(self.root)
            with self.assertRaises(ValueError):self.save(data)
            self.assertEqual(before,snapshot(self.root))

    def test_case_can_link_growth_without_new_raw_links(self):
        data=growth();case=self.root/'wiki/brands/benshot.md'
        data['pages'].append({'path':'wiki/brands/benshot.md','content':case.read_text()+'\n[[wiki/growth/benshot-growth|Growth learning]]\n','expected_sha256':intake.digest(case.read_bytes())})
        self.save(data)
        self.assertEqual(check.check(self.root)['errors'],[])
        self.assertIn('Growth learning',case.read_text())

    def test_repeated_growth_and_revision_are_idempotent(self):
        self.save();before=snapshot(self.root)
        self.assertEqual(self.save()['status'],'duplicate')
        self.assertEqual(before,snapshot(self.root))
        data=growth();page=self.root/data['pages'][0]['path']
        data['pages'][0]['expected_sha256']=intake.digest(page.read_bytes())
        data['pages'][0]['content']+='\nA revised interpretation.\n'
        self.assertEqual(self.save(data,True)['status'],'revised')
        before=snapshot(self.root)
        self.assertEqual(self.save(data,True)['status'],'duplicate')
        self.assertEqual(before,snapshot(self.root))
        self.assertEqual(check.check(self.root)['sources'],3)

    def test_missing_source_or_stale_case_rejects_whole_pass(self):
        data=growth();data['pages'][0]['content']='# No evidence\n[[wiki/brands/benshot]]'
        before=snapshot(self.root)
        with self.assertRaises(ValueError):self.save(data)
        self.assertEqual(before,snapshot(self.root))
        data=growth();data['pages'].append({'path':'wiki/brands/benshot.md','content':'# New case\n[[wiki/growth/benshot-growth]]','expected_sha256':'0'*64})
        with self.assertRaises(ValueError):self.save(data)
        self.assertEqual(before,snapshot(self.root))

    def test_growth_of_known_evidence_is_explicit_distinct_revision(self):
        data=growth();data['sources']=session()['sources']
        self.assertEqual(self.save(data)['status'],'duplicate')
        self.assertEqual(self.save(data,True)['status'],'revised')
        state=json.loads((self.root/'.brb/state.json').read_text())
        self.assertEqual(state['events'][-1]['type'],'growth_revision')
        self.assertEqual(len(state['sources']),2)

    def test_unknown_mode_is_rejected(self):
        data=growth();data['mode']='automatic-paid-research';before=snapshot(self.root)
        with self.assertRaises(ValueError):self.save(data)
        self.assertEqual(before,snapshot(self.root))

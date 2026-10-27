#!/usr/bin/env python3
"""Replay old-case reconciliation with background-only reviews; no model/network."""
import copy
import json
from pathlib import Path
import tempfile
from replay_examples import load,ROOT,SKILLS


def snapshot(root):
    return {str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file() and p.name!='.DS_Store'}


def run(output):
    root=Path(output)
    if root.exists() and any(root.iterdir()):raise ValueError('Use an empty directory')
    init=load('reconcile_init',SKILLS/'brain-init/scripts/init_brain.py')
    learn=load('reconcile_save',SKILLS/'brand-intake/scripts/learn.py')
    checker=load('reconcile_check',SKILLS/'brand-intake/scripts/check_brain.py')
    init.initialize(root,name='Shopify 知识沉淀示例',language='zh-CN',date='2026-10-24')
    for path in ['examples/growth/useit-initial.json','examples/reconciliation/looki-initial.json']:
        learn.commit(root,json.loads((ROOT/path).read_text()),'2026-10-24',allow_legacy=True)
    before=snapshot(root)
    data=json.loads((ROOT/'examples/reconciliation/looki-reconcile.json').read_text())
    assert learn.commit(root,data,'2026-10-24',revise=True)['status']=='revised'
    saved=snapshot(root)
    assert all(saved[p]==b for p,b in before.items() if p.startswith('raw/') or p in {'wiki/brands/useit.md','wiki/categories/personalized-physical-goods.md','wiki/growth/reusable-examples-to-personalization.md','wiki/shopify/scenario-proof-feedback-page.md'})
    assert saved['wiki/ideas/occasion-card-product-outline.md'].startswith(before['wiki/ideas/occasion-card-product-outline.md'])
    assert saved['wiki/brands/looki.md'].startswith(before['wiki/brands/looki.md'])
    assert learn.commit(root,copy.deepcopy(data),'2026-10-25',revise=True)['status']=='duplicate'
    assert saved==snapshot(root)
    assert {p:b for p,b in saved.items() if p not in {'AGENTS.md','BRAIN.md'}}=={p:b for p,b in snapshot(ROOT/'examples/reconciliation/brain').items() if p not in {'AGENTS.md','BRAIN.md'}},'Historical reconciliation research differs from replay'
    state=json.loads((root/'.brb/state.json').read_text());reviews=state['events'][-1]['knowledge_reviews']
    assert set(reviews)=={'categories','ideas','shopify','growth'}
    for review in reviews.values():
        for page in (root/'wiki').rglob('*.md'):assert review['reason'] not in page.read_text()
    result=checker.check(root)
    assert result['errors']==[] and (result['brands'],result['sources'],result['events'])==(2,6,3),result
    print(json.dumps({'mode':'deterministic_reconciliation_replay',**result},ensure_ascii=False,indent=2))
    return result


if __name__=='__main__':
    with tempfile.TemporaryDirectory(prefix='brb-reconcile-') as directory:run(directory)

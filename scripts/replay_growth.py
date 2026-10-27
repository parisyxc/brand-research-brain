#!/usr/bin/env python3
"""Replay reviewed UseIt public research into a blank Brain, without networking."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
from replay_examples import load, ROOT, SKILLS


def snapshot(root):
    return {str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file() and p.name!='.DS_Store'}


def run(output):
    init=load('growth_init',SKILLS/'brain-init/scripts/init_brain.py')
    learn=load('growth_save',SKILLS/'brand-intake/scripts/learn.py')
    checker=load('growth_checker',SKILLS/'brand-intake/scripts/check_brain.py')
    brain=Path(output)
    if brain.exists() and any(brain.iterdir()):raise ValueError('Use an empty replay destination')
    init.initialize(brain,name='Shopify growth 学习 Brain',language='zh-CN',date='2026-10-24')
    initial=json.loads((ROOT/'examples/growth/useit-initial.json').read_text())
    payload=json.loads((ROOT/'examples/growth/useit-growth.json').read_text())
    learn.commit(brain,initial,'2026-10-24', allow_legacy=True)
    before=snapshot(brain)
    assert learn.commit(brain,payload,'2026-10-24', allow_legacy=True)['status']=='ingested'
    assert all((brain/p).read_bytes()==b for p,b in before.items() if p.startswith(('raw/','wiki/categories/','wiki/ideas/')) or p=='wiki/growth/reusable-examples-to-personalization.md')
    saved=snapshot(brain)
    assert learn.commit(brain,copy.deepcopy(payload),'2026-10-25', allow_legacy=True)['status']=='duplicate'
    assert saved==snapshot(brain)
    # Public research is preserved separately from future behavior tests.
    assert {p:b for p,b in saved.items() if p not in {'AGENTS.md','BRAIN.md'}}=={p:b for p,b in snapshot(ROOT/'examples/growth/brain').items() if p not in {'AGENTS.md','BRAIN.md'}},'Historical research differs from replay'
    result=checker.check(brain)
    assert result['errors']==[] and (result['brands'],result['sources'],result['events'])==(1,8,2),result
    print(json.dumps({'mode':'deterministic_growth_replay',**result},ensure_ascii=False,indent=2))
    return result


if __name__=='__main__':
    with tempfile.TemporaryDirectory(prefix='brb-growth-') as directory:run(directory)

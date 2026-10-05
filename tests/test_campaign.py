import json

from benchmark.run_campaign import run


def test_campaign_replay_keeps_temporal_prefixes_and_stable_prompts(tmp_path,capsys):
    output=tmp_path/'campaign'
    from pathlib import Path
    exchange=Path('reports/continuity/exchange')
    assert run(output,exchange)==0
    first=json.loads((output/'continuity/after-01/learner-state.json').read_text())
    assert first['sessions']==1 and first['patterns']==[]
    assert json.loads((output/'continuity/after-01/teacher-prompt.audit.json').read_text())['selection_counts']['transfer']==0
    before={str(p.relative_to(output)):p.read_bytes() for p in output.glob('*/after-*/teacher-prompt.md')}
    assert run(output,exchange)==0
    after={str(p.relative_to(output)):p.read_bytes() for p in output.glob('*/after-*/teacher-prompt.md')}
    assert before==after

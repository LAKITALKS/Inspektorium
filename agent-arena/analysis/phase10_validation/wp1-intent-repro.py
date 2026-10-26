import json
from pathlib import Path
from tempfile import TemporaryDirectory
from tests.test_phase10_bundle import recorded, data, rewrite_hashes
from agent_arena.phase10_bundle import run_audit, release_candidate, inspect_bundle
from agent_arena.phase10_pipeline import canonical
from agent_arena.phase9_runtime import OfflineReviewProvider

with TemporaryDirectory(prefix='p10critic-intent-') as folder:
    root = Path(folder)
    task, raw = recorded()
    provider = OfflineReviewProvider(raw)
    candidate = run_audit(task, provider, output_root=root)
    released = release_candidate(Path(candidate.path), output_root=root,
                                 reviewer='original host', reason='original local release')
    assert released.status == 'RELEASED'
    path = Path(released.path)
    bound_before = {name: (path / name).read_bytes()
                    for name in ('record.json', 'report.md', 'report.html')}
    decision = data(path, 'decision.json')
    subject = decision['subject']
    decision['release_intent']['reviewer'] = 'replacement host'
    decision['release_intent']['reason'] = 'replacement release decision'
    (path / 'decision.json').write_bytes(canonical(decision))
    rewrite_hashes(path)
    assert bound_before == {name: (path / name).read_bytes() for name in bound_before}
    assert data(path, 'decision.json')['subject'] == subject
    assert len(provider.requests) == 1
    result = inspect_bundle(path)
    print('Original record/reports/subject unchanged; only intent and outer hashes replaced.')
    print(result.model_dump_json())
    assert not result.valid, 'Changed release intent must not reuse the existing release revision and checked reports'

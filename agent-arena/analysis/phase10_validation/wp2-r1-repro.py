import json
from pathlib import Path
from tempfile import TemporaryDirectory
from tests.test_phase10_bundle import recorded
from agent_arena.phase10_bundle import run_audit, review_candidate, release_candidate, inspect_bundle
from agent_arena.phase10_render import _HTMLText, _markdown_tokens
from agent_arena.phase9_runtime import OfflineReviewProvider

with TemporaryDirectory(prefix='p10critic-reference-') as temp:
    root = Path(temp)
    task, uncertain = recorded('unknown')
    _, correction = recorded('supported')
    provider = OfflineReviewProvider(uncertain)
    first = run_audit(task, provider, output_root=root / 'bundles')
    original = json.loads((Path(first.path) / 'record.json').read_text())
    selected = original['run_record']['metadata']['phase9']['positions'][0]['position_id']
    reviewed = review_candidate(Path(first.path), output_root=root / 'bundles', state_dir=root / 'state',
                                selected_position_id=selected, reviewer='offline human example',
                                reason='Correct the supplied interpretation', corrected_raw_output=correction)
    released = release_candidate(Path(reviewed.path), output_root=root / 'bundles',
                                  reviewer='offline operator', reason='Local report review')
    assert released.status == 'RELEASED'
    directory = Path(released.path)
    print('Verification:', inspect_bundle(directory).model_dump())
    audit = json.loads((directory / 'record.json').read_text())
    errors, references = [], []
    for filename in ('report.md', 'report.html'):
        document = (directory / filename).read_text()
        if filename.endswith('.md'):
            tokens = _markdown_tokens(document)
        else:
            parser = _HTMLText(); parser.feed(document); tokens = parser.tokens
        for kind, ref in tokens:
            if kind != 'td' or not ref.endswith('/position_fingerprints'):
                continue
            references.append(ref)
            try:
                value = audit
                for part in ref.removeprefix('record.json#/').split('/'):
                    value = value[int(part)] if isinstance(value, list) else value[part]
            except (KeyError, IndexError) as exc:
                errors.append((filename, ref, str(exc)))
    assert len(provider.requests) == 1
    assert references, 'Review binding references must be present'
    print('Broken binding references:', errors)
    assert not errors, 'Every displayed review-binding reference must resolve to its actual bound carrier'

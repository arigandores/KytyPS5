"""Root-authorised UTF8 correction of exactly three new, uncommitted narrative copies."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path('C:/kyty/s99')
REPO = Path('C:/kyty/KytyPS5')
ARCHIVE = REPO / 'docs/session-99'
ALLOW = ('FACTS.md', 'README.md', 'finalize_cont99_facts.py')
RECORD = ROOT / 'encoding_correction99.json'


def digest(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf8')


def main():
    assert not RECORD.exists(), 'Correction already recorded; do not silently rerun'
    canonical_path = ARCHIVE / 'canonical-sha256.json'
    small_path = ARCHIVE / 'continuation/small-sha256.json'
    canonical_before_bytes = canonical_path.read_bytes()
    small_before_bytes = small_path.read_bytes()
    canonical_before = json.loads(canonical_before_bytes)
    small_before = json.loads(small_before_bytes)
    assert len(canonical_before) == 311
    assert len(small_before['artifacts']) == 276
    original33 = json.loads(subprocess.check_output([
        'git', '-C', str(REPO), 'show', 'HEAD:docs/session-99/canonical-sha256.json']))
    assert len(original33) == 33
    assert all(canonical_before[name] == value for name, value in original33.items())
    cal_path = ARCHIVE / 'runs/cal99a/sha256.json'
    cal_before = cal_path.read_bytes()
    assert cal_before == subprocess.check_output([
        'git', '-C', str(REPO), 'show', 'HEAD:docs/session-99/runs/cal99a/sha256.json'])
    # Hold exact bytes for every canonical member; all unchanged artifacts are compared bytewise.
    snapshots = {name: (ARCHIVE / name).read_bytes() for name in canonical_before}
    for name, value in canonical_before.items():
        assert digest(snapshots[name]) == value, f'Pre-existing hash mismatch: {name}'
    for name, value in small_before['artifacts'].items():
        assert canonical_before['continuation/' + name] == value

    source_bytes = {name: (ROOT / name).read_bytes() for name in ALLOW}
    for name, data in source_bytes.items():
        data.decode('utf8', errors='strict')
    assert source_bytes['FACTS.md'] == (REPO / 'docs/local-session-99.md').read_bytes()
    assert b"encoding='utf-8'" in source_bytes['finalize_cont99_facts.py']
    canonical_after = json.loads(canonical_before_bytes)
    small_after = json.loads(small_before_bytes)
    changes = {}
    for name in ALLOW:
        key = 'continuation/' + name
        updated = digest(source_bytes[name])
        assert updated != canonical_before[key], f'Expected correction did not change {name}'
        changes[name] = {'before': canonical_before[key], 'after': updated}
        small_after['artifacts'][name] = updated
        canonical_after[key] = updated
    small_after_bytes = encoded(small_after)
    canonical_after['continuation/small-sha256.json'] = digest(small_after_bytes)
    changed_keys = {key for key in canonical_before if canonical_before[key] != canonical_after[key]}
    assert changed_keys == {'continuation/' + name for name in ALLOW} | {'continuation/small-sha256.json'}
    assert all(canonical_after[name] == value for name, value in original33.items())
    assert canonical_path.read_bytes() == canonical_before_bytes
    assert small_path.read_bytes() == small_before_bytes
    for name in ALLOW:
        assert (ROOT / name).read_bytes() == source_bytes[name]
    for name in ALLOW:
        (ARCHIVE / 'continuation' / name).write_bytes(source_bytes[name])
    small_path.write_bytes(small_after_bytes)
    canonical_after_bytes = encoded(canonical_after)
    canonical_path.write_bytes(canonical_after_bytes)
    for name, value in canonical_after.items():
        actual = (ARCHIVE / name).read_bytes()
        assert digest(actual) == value, f'Post-correction hash mismatch: {name}'
        if name not in changed_keys:
            assert actual == snapshots[name], f'Unexpected byte change: {name}'
    assert cal_path.read_bytes() == cal_before
    record = {
        'schema': 's99-precommit-encoding-correction-v1',
        'reason': 'Explicit root-authorised correction: finalizer default cp1250 text decoding corrupted UTF8 in newly archived mutable FACTS/README. Root fixed explicit UTF8, regenerated FACTS/mirror, and restored README historical tail from valid old archive. No sealed evidence changed.',
        'allowed_source_files': list(ALLOW), 'corrections': changes,
        'small_manifest': {'before': digest(small_before_bytes), 'after': digest(small_after_bytes)},
        'canonical_manifest': {'before': digest(canonical_before_bytes), 'after': digest(canonical_after_bytes)},
        'post_checks': {'canonical_entries_verified': len(canonical_after),
                        'unchanged_canonical_members_compared_bytewise': len(canonical_after) - len(changed_keys),
                        'original33_values_preserved': True, 'cal99a_manifest_preserved': True,
                        'raw_seal_review_artifacts_preserved': True},
        'stage_or_commit': False,
    }
    with RECORD.open('xb') as target:
        target.write(encoded(record))
    print(json.dumps({'result': 'PASS', 'changed_source_files': list(ALLOW),
                      'canonical_entries': len(canonical_after),
                      'canonical_sha256': digest(canonical_after_bytes)['sha256'],
                      'record': str(RECORD)}, indent=2))


if __name__ == '__main__':
    main()

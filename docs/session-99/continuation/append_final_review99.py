"""Add the final review and encoding-correction audit after the reviewed archive snapshot."""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path('C:/kyty/s99')
repo = Path('C:/kyty/KytyPS5')
archive = repo / 'docs/session-99'
canon_path = archive / 'canonical-sha256.json'
small_path = archive / 'continuation/small-sha256.json'
canon = json.loads(canon_path.read_text(encoding='utf-8'))
small = json.loads(small_path.read_text(encoding='utf-8'))
original = json.loads(subprocess.check_output(['git', 'show', 'HEAD:docs/session-99/canonical-sha256.json'], cwd=repo))
assert len(original) == 33 and all(canon[name] == value for name, value in original.items())

def entry(data):
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())

for name, expected in canon.items():
    assert entry((archive / name).read_bytes()) == expected, name
extras = ('verify99_final_docs/VERIFY.md', 'verify99_final_docs/check.py', 'verify99_final_docs/checks.json',
          'encoding_correction99.json', 'correct_cont99_encoding.py', 'append_final_review99.py')
for name in extras:
    data = (root / name).read_bytes()
    target = archive / 'continuation' / name
    if target.exists():
        assert target.read_bytes() == data
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as handle:
            handle.write(data)
    value = entry(data)
    assert name not in small['artifacts'] or small['artifacts'][name] == value
    assert 'continuation/' + name not in canon or canon['continuation/' + name] == value
    small['artifacts'][name] = value
    canon['continuation/' + name] = value
small_data = (json.dumps(small, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
small_path.write_bytes(small_data)
canon['continuation/small-sha256.json'] = entry(small_data)
canon_path.write_bytes((json.dumps(canon, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
assert all(canon[name] == value for name, value in original.items())
for name, expected in canon.items():
    assert entry((archive / name).read_bytes()) == expected, name
print(json.dumps(dict(canonical_entries=len(canon), small_artifacts=len(small['artifacts']),
                     old_entries_preserved=len(original), appended=len(extras)), indent=2))

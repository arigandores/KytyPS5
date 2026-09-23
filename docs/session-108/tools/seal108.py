"""Session 108: place the scorer files in C:/kyty/s108, write gates_fam4.txt, seal pred/01_cspfam.md from the repo
draft, write SEALS108.txt, pin PRED_SHA/PRED_BYTES in the s108 fam108.py.  One-shot; refuses if the seal exists."""
import hashlib
import shutil
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')
DST = Path('C:/kyty/s108')
REPO = Path('C:/kyty/KytyPS5/docs/session-108')
NL = chr(10)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


seal = DST / 'pred' / '01_cspfam.md'
assert not seal.exists(), 'seal exists already'
assert sha('C:/kyty/build/install/kyty_emulator.exe').startswith('fd1d0bd7f682'), 'build changed'
assert sha(DST / 'gates_base.txt').startswith('303a7849'), 'gates_base changed'
for name in ('fam108.py', 'make_fam108.py', 'test_fam108.py'):
    assert sha(STAGE / name) == sha(REPO / 'tools' / name), name
    if (DST / name).exists():
        assert sha(DST / name) == sha(STAGE / name), name
    shutil.copy2(STAGE / name, DST / name)
shutil.copy2(STAGE / 'go108.sh', DST / 'go108.sh')

# gates_fam4.txt: gates_base.txt as ONE line with ' cspfam=4' before its single trailing CRLF
base = (DST / 'gates_base.txt').read_bytes()
assert base.endswith(b'\r\n') and base.count(b'\n') == 1
fam4 = base[:-2] + b' cspfam=4\r\n'
assert len(fam4) == 1101
(DST / 'gates_fam4.txt').write_bytes(fam4)

# the seal text: the repo draft minus its DRAFT note, plus the resumption record
text = (REPO / '01_cspfam.DRAFT-not-sealed.md').read_text(encoding='utf-8')
lines = text.split(NL)
assert lines[2].startswith('> **DRAFT'), lines[2]
assert lines[3].startswith('> `docs/local-session-108.md`'), lines[3]
assert lines[4] == ''
del lines[2:5]
text = NL.join(lines)
old = ('commit `87f1c2b`; "СЕССИЯ 108 — ЗАПИСИ ДО ДЕЙСТВИЙ", items 1–2 — commit `3cc53a2`) before the code and this '
       'text.')
assert text.count(old) == 1
text = text.replace(old, 'commit `87f1c2b`; "СЕССИЯ 108 — ЗАПИСИ ДО ДЕЙСТВИЙ", items 1–2 — commit `3cc53a2`, and item 4 '
                         '— the resumption after the pause, fixtures by option (a) — committed with this text) before '
                         'the code and this text.')
old2 = 'reschedules); one repeat on a fatal marker'
assert text.count(old2) == 1
text = text.replace(old2, 'reschedules — `go108.sh` holds `C:/kyty/SEALED_RUN.lock` for the whole chain); one repeat on a '
                          'fatal marker')
assert 'NOT SEALED' not in text and 'DRAFT —' not in text
seal.write_bytes(text.encode('utf-8'))
seal_sha, seal_bytes = sha(seal), seal.stat().st_size

# pin the seal in the s108 scorer (two literal lines; nothing else changes)
fam = (DST / 'fam108.py').read_text(encoding='utf-8')
a = "PRED_SHA = None          # filled by the executor when pred/01 is sealed"
b = "PRED_BYTES = None        # filled by the executor when pred/01 is sealed"
assert fam.count(a) == 1 and fam.count(b) == 1
fam = fam.replace(a, "PRED_SHA = '%s'   # pred/01 sealed" % seal_sha)
fam = fam.replace(b, "PRED_BYTES = %d       # pred/01 sealed" % seal_bytes)
(DST / 'fam108.py').write_bytes(fam.encode('utf-8'))

seals = ''.join('%s *%s\n' % (sha(DST / p), p) for p in ('pred/01_cspfam.md', 'gates_fam4.txt', 'fam108.py',
                                                          'make_fam108.py', 'test_fam108.py', 'go108.sh'))
(DST / 'SEALS108.txt').write_bytes(seals.encode('ascii'))
print(seals, end='')
print('seal bytes', seal_bytes)

"""Session 109: frm109.py = frf109.py with pred/04_frm109.md pinned and the tag pattern widened to fr[fm]109
(ROADMAP §0.1 "СЕССИЯ 109" item 7).  Byte-reproducible; refuses if the source scorer or the seal moved."""
import hashlib
from pathlib import Path

ROOT = Path('C:/kyty/s109')
SRC_SHA = 'a9a93a53d5ba3b4868bc6e54418fbd8abfc4cf6cd764bc7f698501d69d7db6d3'


def sha(b):
    return hashlib.sha256(b).hexdigest()


src = (ROOT / 'frf109.py').read_bytes()
assert sha(src) == SRC_SHA, 'frf109.py moved'
seal = (ROOT / 'pred' / '04_frm109.md').read_bytes()
s = src.decode('utf-8')
pairs = [
    ("PRED = 'C:/kyty/s109/pred/03_frf109.md'", "PRED = 'C:/kyty/s109/pred/04_frm109.md'"),
    ("PRED_SHA = '8f44107fa1367c2bab64025ef6d025a70ef4654d1b74786eda7d283fee60f310'   # pred/03_frf109.md sealed",
     "PRED_SHA = '%s'   # pred/04_frm109.md sealed (frm109.py, a measurement-only copy of frf109.py)" % sha(seal)),
    ("PRED_BYTES = 3778       # pred/03_frf109.md sealed", "PRED_BYTES = %d       # pred/04_frm109.md sealed" % len(seal)),
    ("TAG_RE = r'frf109b?(?:_entry1)?'", "TAG_RE = r'fr[fm]109b?(?:_entry1)?'"),
]
for a, b in pairs:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
(ROOT / 'frm109.py').write_bytes(s.encode('utf-8'))
print('frm109.py', sha(s.encode('utf-8')), 'seal', sha(seal), len(seal))

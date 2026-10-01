"""Link 1b of s145 (HPP-379; ROADMAP s122 item 295 (v), (e)): exact edits of C:/kyty/s145/step2/gate145.py - each anchor must
occur once.  ASCII only.  python p1b_gate.py"""
import hashlib
import sys

P = 'C:/kyty/s145/step2/gate145.py'
src = open(P, 'rb').read().decode('utf-8')
assert '\r' not in src
N = [0]


def rep(old, new):
    global src
    c = src.count(old)
    if c != 1:
        print('ANCHOR COUNT %d: %r' % (c, old[:120]))
        sys.exit(1)
    N[0] += 1
    src = src.replace(old, new)


rep('''"""gate145.py - the read-only gate of step 2 of session 145 (step 0 HPP-350; ROADMAP s122 item 273 (k)(3)-(4); port of
C:/kyty/s144/step2/gate144.py of item 266 (b)-(e), (g), (h)).  It reads the series files and the caches and writes ONE ascii
row into step2/times.txt:
''', '''"""gate145.py - the read-only gate of step 2 of session 145 (step 0 HPP-350; ROADMAP s122 item 273 (k)(3)-(4); link 1b
HPP-379, item 295 (v), (e); port of C:/kyty/s144/step2/gate144.py of item 266 (b)-(e), (g), (h)).  It reads the series files
and the caches and writes ONE ascii row into step2/times.txt:
''')
rep('''  --start            before the first lock of step 2: (d) the sha256 of C:/kyty/s144/step2/times.txt and C:/kyty/s144/pred/
                     01_sc144.md (= their seal lines of pred/02_sc145.md) and of the V log v144_09 (= the last "go144a v144_09
                     enter_scene end" line of that times.txt); (c)(1) the live caches (path, size, sha256 - not mtime)
''', '''  --start            before the first lock of step 2: (d) the sha256 of C:/kyty/s144/step2/times.txt and C:/kyty/s144/pred/
                     01_sc144.md (= their seal lines of pred/03_sc145.md) and of the V log v144_09 (= the last "go144a v144_09
                     enter_scene end" line of that times.txt); (r) item 295 (e): the sha256 of the reference
                     C:/kyty/s144/runs144/cache_w144_20.after.json = its seal line, else STOP; (s) item 295 (v): the free
                     space of the disk C: below 60 GiB (MIN_FREE; the units of df -h the lead read 349 G in; the row prints
                     the bytes, GiB and GB) -> STOP; (c)(1) the live caches (path, size, sha256 - not mtime)
''')
rep('''                     log_P.txt -> STOP; (f) W - VK_LAYER_MESSAGE_ID_FILTER of its json env != sc145.VKFILTER -> STOP (item 273
                     (k)(2)); (e) V - the "admission:" line of score_P.txt failing by "V positive control" or "V shipped
''', '''                     log_P.txt -> STOP; (f) W - the form line of item 295 (b)(4) built from its json env (sc145.w_form4:
                     "W form: limit=100000000 filter=none", no VK_LAYER_MESSAGE_ID_FILTER key) failing -> STOP; (v) W (the
                     control or another) - item 295 (v): any row "W 295(b)(N)" failing in the "admission:" line of
                     score_P.txt (the sealed scorer's rows of item 295 (b)(1)-(4)), the score file or its admission line
                     missing -> STOP (an instrument stop, question to the lead); (e) V - the "admission:" line of score_P.txt
                     failing by "V positive control" or "V shipped
''')
rep("""import argparse
import hashlib
import json
import os
import re
import sys
import time
""", """import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
""")
rep("""HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\\\', '/')
S145 = os.path.dirname(HERE)
sys.path.insert(0, S145)
""", """S145 = 'C:/kyty/s145'                 # absolute: a copy of this file elsewhere (a mutant) reads the same sc145 / cachemf145
sys.path.insert(0, S145)
""")
rep("""PRED = ROOT + '/pred/02_sc145.md'
""", """PRED = ROOT + '/pred/03_sc145.md'
REF_SEAL = 'C:/kyty/s144/runs144/cache_w144_20.after.json'   # item 295 (e): the name of its seal line
MIN_FREE = 60 * 2 ** 30                                      # item 295 (v): 60 GiB free on C:
DISK = 'C:/'
""")
rep("""def made(t, root):
""", """def disk_free(path):
    \"\"\"Item 295 (v): the free bytes of the disk of path (the fixtures replace this function).\"\"\"
    return shutil.disk_usage(path).free


def w_admission_bad(score):
    \"\"\"Item 295 (v): the members '(b)(N)' of the failing rows "W 295(b)(N) ..." in the admission line of a W score, [] when
    none fails; None without the file; ['no admission line'] without the line.\"\"\"
    if not os.path.isfile(score):
        return None
    with open(score, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            s = line.strip()
            if s.startswith('admission:'):
                return re.findall(r'W 295(\\(b\\)\\(\\d\\))', s)
    return ['no admission line']


def made(t, root):
""")
rep("""            jp = '%s/%s.json' % (root, p)
            fv = ((json.load(open(jp, encoding='utf-8')).get('env') or {}).get('VK_LAYER_MESSAGE_ID_FILTER')
                  if os.path.isfile(jp) else 'NO JSON')
            det.append('%s filter %s' % (p, fv))
            if fv != sc145.VKFILTER:
                bad.append('(f) W %s: VK_LAYER_MESSAGE_ID_FILTER %s != %s (item 273 (k)(2))' % (p, fv, sc145.VKFILTER))
""", """            jp = '%s/%s.json' % (root, p)
            f4 = sc145.w_form4(json.load(open(jp, encoding='utf-8')).get('env') or {}) if os.path.isfile(jp) else (
                False, 'NO JSON')
            det.append('%s %s' % (p, f4[1]))
            if not f4[0]:
                bad.append('(f) W %s: the form line "%s" != "%s" or VK_LAYER_MESSAGE_ID_FILTER in its env (item 295 (b)(4))' % (
                    p, f4[1], sc145.W_FORM_LINE))
            wb = w_admission_bad('%s/score_%s.txt' % (root, p))
            det.append('%s W form rows of item 295 (b) %s' % (p, 'score MISSING' if wb is None else (','.join(wb) or 'pass')))
            if wb is None:
                bad.append('(v) W %s: score_%s.txt missing - the W form rows of item 295 (b) not evaluable' % (p, p))
            elif wb:
                bad.append('(v) W %s fails the W form row(s) %s of item 295 (b) (an instrument stop, question to the lead; item '
                           '295 (v))' % (p, ','.join(wb)))
""")
rep("""def start(root, root144, pred, ref, live):
    bad, det = check144(root144, pred)
""", """def start(root, root144, pred, ref, live):
    bad, det = check144(root144, pred)
    want = seal_sha(pred, REF_SEAL)
    got = sha_file(ref) if os.path.isfile(ref) else None
    det.append('(r) reference %s sha256 %s (seal %s)' % (os.path.basename(ref), (got or 'MISSING')[:16], (want or 'none')[:16]))
    if got is None or got != want:
        bad.append('(r) the reference %s sha256 %s != its seal line %s (item 295 (e))' % (
            os.path.basename(ref), (got or 'MISSING')[:16], (want or 'none')[:16]))
    fr = disk_free(DISK)
    det.append('(s) free on %s %d bytes = %.1f GiB = %.1f GB (STOP below %d bytes = 60 GiB)' % (DISK, fr, fr / 2.0 ** 30,
                                                                                              fr / 1e9, MIN_FREE))
    if fr < MIN_FREE:
        bad.append('(s) free space on %s %.1f GiB < 60 GiB (item 295 (v))' % (DISK, fr / 2.0 ** 30))
    if got is None:
        det.append('(c)(1) not evaluable: the reference is missing; no start manifest written')
        return bad, det
""")

open(P, 'wb').write(src.encode('ascii'))
print('edits %d; gate145.py sha256 %s' % (N[0], hashlib.sha256(src.encode('ascii')).hexdigest()))

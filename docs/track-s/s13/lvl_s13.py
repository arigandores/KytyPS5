"""lvl_s13.py - track S, link S13a (HPP-498; ROADMAP "SESSION 122" item 408 (e), (l), item 229 (e)(1), item 410 (g)(6)(iii),
item 414 (g)(5)-(7)): the list of the 19 known levels of item 229 (e)(1), the rule "in the catalogue" of item 355 (e) for each,
the plan of the collection arms of S13b and the check of the compatibility line of the S9 export against the log of the
installed FS4 31cbfee8.  READ ONLY (mmap), ASCII output.  No game, no write but its own output (the caller's redirection).

THE 19 (item 229 (e)(1): "9 by inventory141.md + 10 sc142"): the rows of the inventory rev. 2 (C:/kyty/s141/step1b/
  inventory141_r2.md, 114 rows) whose column "entry" begins with "da" (9 rows: "da [c]" x 8, "da (by the document)" x 1), in
  map order; then the ten census levels of sc142 (C:/kyty/s142/go142a.sh, the case lines "c142_NN) LEVEL=<level>;;") in tag
  order.  A name in both lists counts once (none expected; printed).
IN THE CATALOGUE (item 355 (e), the letter): >= 1 log on a binary with the translator signature SIG_FS4 (the line
  "ShaderSeed: compatibility=" of the log carries it) WITH cache writes (not an arm with a return) carries "Level has started:
  <level>".  "An arm with a return" - the reading of lvl_s9.py (S9, accepted by item 364): a log under C:/kyty/s288,
  C:/kyty/f287, C:/kyty/p283, C:/kyty/play or the emulator folder.  Printed beside: the same rule on the signature of FS5
  (SIG_FS5, item 410 (g)(6)(iii): S13b collects on the signature of FS5) and the number of logs since T0 that carry the
  entry line on any signature (data: "entered before").  Logs: the walk of lvl_s9.py (every *.txt / *.log > 1 MiB under
  C:/kyty with mtime >= T0 = 2026-09-30T23:41:52Z; .xz not read, counted).
THE PLAN (item 408 (l), item 410 (g)(6)(iii)): the levels NOT in the catalogue of the signature S13b collects on - the
  collection arms k_01 .. k_NN in the order of the list.  Both lists are printed: PLAN_FS5 (the rule on SIG_FS5 - the plan of
  the seal) and PLAN_FS4 (the rule on SIG_FS4 - the letter of the task text, used only if a lead item lifts the block of S13b
  on FS5e).
COMPATIBILITY (item 408 (e), the task of S13a): the line "compatibility.txt" of the S9 export (C:/kyty/s288/s9/seeds/
  PPSA21564/compatibility.txt) against the line "ShaderSeed: compatibility=" of the log of the installed FS4 (C:/kyty/f287/
  fs4c/log_fs4_v.txt, its json binary 31cbfee8..., no KYTY_GAME_PATCH) - EQUAL / DIFFERENT.
The run refuses (rc 5) when C:/kyty/SEALED_RUN.lock exists or appears.
    python lvl_s13.py
"""
import calendar
import hashlib
import json
import mmap
import os
import re
import sys
import time
from multiprocessing import Pool

TOP = 'C:/kyty'
T0_TXT = '2026-09-30T23:41:52Z'
T0 = calendar.timegm((2026, 9, 30, 23, 41, 52))
LOCK = 'C:/kyty/SEALED_RUN.lock'
INV = 'C:/kyty/s141/step1b/inventory141_r2.md'
GO142 = 'C:/kyty/s142/go142a.sh'
KEY = b'Level has started: '
CKEY = b'ShaderSeed: compatibility='
SIG_FS4 = b'KytySC3:56189185f9e9f9a0ea5174f3f85206e6d099db3d:robust:ftz:cbank:fixb26:fixb1b:'
SIG_FS5 = b'KytySC3:26ce5fc78ea3b20be537c7696be041f5e97d9e58:'
SKIPDIRS = ('build', 'tools', 'scrub', '.git', 'games', '__pycache__', '_Shaders', '_ShaderCache', '_RenderDoc', '_PipelineCache')
SKIPPFX = ('mutwork', 'mutcache', 'vidframes', 'cache_snap', 'cache_run', 'glcache_', 'pcache_')
MINSIZE = 1 << 20
RETURN_ROOTS = ('C:/kyty/s288/', 'C:/kyty/f287/', 'C:/kyty/p283/', 'C:/kyty/play/', 'C:/kyty/KytyPS5/ps5 em/')
EXPORT_COMPAT = 'C:/kyty/s288/s9/seeds/PPSA21564/compatibility.txt'
FS4_LOG = 'C:/kyty/f287/fs4c/log_fs4_v.txt'
FS4_JSON = 'C:/kyty/f287/fs4c/fs4_v.json'
FS4_SHA = '31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5'
NEED_INV = 9
NEED_142 = 10
RX_INV = re.compile(r'^\| (\d+) \| ([^|]+) \| ([^|]+) \| `([a-z0-9_]+)` \| ([^|]+) \|')
RX_142 = re.compile(r'^\s*c142_(\d\d)\) LEVEL=([a-z0-9_]+);;')
DA = chr(0x0434) + chr(0x0430)      # "da" in Cyrillic - the entry column of the inventory


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()


def inv_levels(path=INV):
    """(rows of the map, the levels whose entry column begins with "da", in map order)."""
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = RX_INV.match(line)
            if m:
                rows.append((int(m.group(1)), m.group(4), m.group(5).strip()))
    return rows, [r[1] for r in rows if r[2].startswith(DA)]


def sc142_levels(path=GO142):
    out = []
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = RX_142.match(line)
            if m:
                out.append((int(m.group(1)), m.group(2)))
    return [lv for _, lv in sorted(out)]


def known19(inv=INV, go142=GO142):
    """The 19 of item 229 (e)(1): (list, rows of the inventory, the inventory levels, the census levels)."""
    rows, a = inv_levels(inv)
    b = sc142_levels(go142)
    lst = list(a) + [x for x in b if x not in a]
    return lst, rows, a, b


def files(top=TOP, since=T0):
    out = []
    xz = 0
    for dp, dn, fn in os.walk(top):
        dpn = dp.replace(chr(92), '/')
        if dpn == 'C:/kyty/KytyPS5':
            dn[:] = [d for d in dn if d == 'ps5 em']
        elif dpn.startswith('C:/kyty/KytyPS5/ps5 em'):
            dn[:] = []
        else:
            dn[:] = [d for d in dn if d not in SKIPDIRS and not d.startswith(SKIPPFX)]
        for f in fn:
            if f.endswith('.xz'):
                xz += 1
                continue
            if f.endswith(('.txt', '.log')):
                p = dpn + '/' + f
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                if st.st_size > MINSIZE and st.st_mtime >= since:
                    out.append(p)
    return sorted(out), xz


def scan(p):
    """(path, sorted level names, compatibility line or None, 'LOCK' / 'UNREADABLE' / '')."""
    if os.path.exists(LOCK):
        return p, None, None, 'LOCK'
    names = set()
    comp = None
    try:
        with open(p, 'rb') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            q = mm.find(CKEY)
            if q != -1:
                e = mm.find(b'\n', q)
                comp = mm[q + len(CKEY):(e if e != -1 else q + 400)].strip()
            q = mm.find(KEY)
            while q != -1:
                e = mm.find(b'\n', q)
                s = mm[q + len(KEY):(e if e != -1 else q + 120)].strip()
                names.add(s.split()[0].decode('ascii', 'replace') if s else '')
                q = mm.find(KEY, q + 1)
            mm.close()
    except (OSError, ValueError):
        return p, None, None, 'UNREADABLE'
    return p, sorted(names), comp, ''


def returned(p):
    return p.startswith(RETURN_ROOTS)


def classify(res, sig):
    """level -> logs on the signature with writes (not a returning root) that carry its entry line."""
    qual = {}
    for p, n, c, w in res:
        if c is not None and sig in c and not returned(p):
            for x in n or ():
                qual.setdefault(x, []).append(p)
    return qual


def plan(lst, qual):
    return [lv for lv in lst if not qual.get(lv)]


def log_compat(p):
    with open(p, 'rb') as f:
        for i, line in enumerate(f):
            if line.startswith(CKEY):
                return line[len(CKEY):].strip().decode('ascii'), i + 1
            if i > 200000:
                break
    return None, None


def main():
    if os.path.exists(LOCK):
        print('LOCKED: %s exists - no scan' % LOCK)
        return 5
    print('lvl_s13 start %s; T0 %s; self sha256 %s' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), T0_TXT,
                                                      sha(os.path.abspath(__file__))))
    lst, rows, a, b = known19()
    print('inventory %s sha256 %s rows %d; entry "da": %d %s' % (INV, sha(INV), len(rows), len(a), ' '.join(a)))
    print('sc142 %s sha256 %s census levels: %d %s' % (GO142, sha(GO142), len(b), ' '.join(b)))
    print('in both lists: %s' % ([x for x in b if x in a] or 'none'))
    if len(rows) != 114 or len(a) != NEED_INV or len(b) != NEED_142 or len(lst) != NEED_INV + NEED_142:
        print('STOP: the lists are not 114 / 9 / 10 / 19 (%d / %d / %d / %d)' % (len(rows), len(a), len(b), len(lst)))
        return 1
    fl, nxz = files()
    print('logs since T0 (> 1 MiB, .txt/.log): %d files, %.1f GB; .xz files not read: %d' % (
        len(fl), sum(os.path.getsize(p) for p in fl) / 1e9, nxz))
    with Pool(8) as pool:
        res = pool.map(scan, fl, chunksize=1)
    if any(x[3] == 'LOCK' for x in res):
        print('LOCKED: the lock appeared during the scan - result void, rc 5')
        return 5
    unread = [p for p, n, c, w in res if w == 'UNREADABLE']
    print('unreadable logs: %d %s' % (len(unread), unread[:5]))
    q4 = classify(res, SIG_FS4)
    q5 = classify(res, SIG_FS5)
    any_sig = dict((s.decode(), (sum(1 for p, n, c, w in res if c is not None and s in c),
                                 sum(1 for p, n, c, w in res if c is not None and s in c and not returned(p))))
                   for s in (SIG_FS4, SIG_FS5))
    for s, (n, nw) in any_sig.items():
        print('logs whose compatibility line carries %s: %d, of them with writes (not a returning root): %d' % (s, n, nw))
    entered = {}
    for p, n, c, w in res:
        for x in n or ():
            entered.setdefault(x, []).append(p)
    print('THE 19 (item 229 (e)(1)):')
    for i, lv in enumerate(lst):
        src = 'inventory141' if lv in a else 'sc142'
        print('  K%02d %-30s %-12s FS4 sig: %s; FS5 sig: %s; entry line since T0 in %d logs%s' % (
            i + 1, lv, src,
            ('IN (%d logs with writes, first %s)' % (len(q4[lv]), sorted(q4[lv])[0])) if q4.get(lv) else 'NOT in the catalogue',
            ('IN (%d logs, first %s)' % (len(q5[lv]), sorted(q5[lv])[0])) if q5.get(lv) else 'NOT in the catalogue',
            len(entered.get(lv, [])), (' (first %s)' % sorted(entered[lv])[0]) if entered.get(lv) else ''))
    p5 = plan(lst, q5)
    p4 = plan(lst, q4)
    print('LIST13 %s' % ' '.join(lst))
    print('IN_FS4 %d: %s' % (len(lst) - len(p4), ' '.join(x for x in lst if x not in p4) or '-'))
    print('PLAN_FS4 %d: %s' % (len(p4), ' '.join(p4) or '-'))
    print('IN_FS5 %d: %s' % (len(lst) - len(p5), ' '.join(x for x in lst if x not in p5) or '-'))
    print('PLAN_FS5 %d: %s' % (len(p5), ' '.join(p5) or '-'))
    print('never entered since T0 (any signature): %s' % (' '.join(x for x in lst if not entered.get(x)) or 'none'))
    exp = open(EXPORT_COMPAT, encoding='ascii').read().strip()
    js = json.load(open(FS4_JSON, encoding='utf-8'))
    env = js.get('env') or {}
    lc, ln = log_compat(FS4_LOG)
    print('S9 export compatibility.txt %s sha256 %s: %s' % (EXPORT_COMPAT, sha(EXPORT_COMPAT), exp))
    print('FS4 log %s sha256 %s line %s (json %s binary %s, KYTY_GAME_PATCH %s): %s' % (
        FS4_LOG, sha(FS4_LOG), ln, FS4_JSON, js.get('binary_sha256'), env.get('KYTY_GAME_PATCH'), lc))
    fs4_ok = js.get('binary_sha256') == FS4_SHA and 'KYTY_GAME_PATCH' not in env
    print('COMPAT the S9 export against the installed FS4 31cbfee8: %s%s' % (
        'EQUAL' if exp == lc else 'DIFFERENT', '' if fs4_ok else ' (the log is not a run of 31cbfee8 without a patch)'))
    print('lvl_s13 end %s' % time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    print('ALL DONE')
    return 0 if fs4_ok and exp == lc else 1


if __name__ == '__main__':
    sys.exit(main())

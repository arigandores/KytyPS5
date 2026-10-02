"""lvl146.py - session 146 step 0 (HPP-386; ROADMAP s122 item 309 (l)(2)): the list of the 15 never-entered scene levels of the series
sc146.  READ ONLY (mmap), ASCII output.

Rule of item 309 (l)(2): the first 15 in the order of the level map of the inventory, rev. 2 (C:/kyty/s141/step1b/inventory141_r2.md,
table (A), 114 rows) among the levels WITHOUT a line "Level has started: <level>" in all the logs under C:/kyty since 2026-09-30
(track roots P, F, S included), without the "non-scenes" of item 217 (g) (ui_* x7, *_data x3, ps_logo, team_logo - the inventory
header line 62-63) and without final_shooting.
Reading of the letter used (A): "never entered" = the inventory column "entry" is "net" (not entered as of the inventory of s141,
built from the census of s53-113 and the 155 logs of s113-140) AND no entry line in a log since 2026-09-30.  Item 309 (d) counts 59
never-entered scene levels (with final_shooting) after s145 - reading (A) must give 59 (a printed check).
Reading (B) (printed beside, the variant of the letter alone): the inventory column ignored - every map level without an entry line
since 2026-09-30.
Logs: every file *.txt / *.log under C:/kyty larger than 1 MB with mtime >= 2026-09-30T00:00:00Z, walked with the directories
build, tools, scrub, .git, games, __pycache__, mutwork*, mutcache*, vidframes*, _Shaders, _ShaderCache, _RenderDoc skipped; under
C:/kyty/KytyPS5 only the emulator folder (its _kyty.txt, _kyty.prev.txt, _run_stdout.txt).  The key is b'Level has started: '.
  python lvl146.py
"""
import datetime
import hashlib
import mmap
import os
import re
import sys
from multiprocessing import Pool

INV = 'C:/kyty/s141/step1b/inventory141_r2.md'
TOP = 'C:/kyty'
SINCE = datetime.datetime(2026, 9, 30, tzinfo=datetime.timezone.utc).timestamp()
KEY = b'Level has started: '
SKIPDIRS = ('build', 'tools', 'scrub', '.git', 'games', '__pycache__', '_Shaders', '_ShaderCache', '_RenderDoc', '_PipelineCache')
SKIPPFX = ('mutwork', 'mutcache', 'vidframes', 'cache_snap', 'cache_run', 'glcache_', 'pcache_')
NONSCENE_RX = re.compile(r'^(ui_.*|.*_data|ps_logo|team_logo)$')
MINSIZE = 1 << 20
N_WANT = 15


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()


def inventory():
    rows = []
    rx = re.compile(r'^\| (\d+) \| ([^|]+) \| ([^|]+) \| `([a-z0-9_]+)` \| ([^|]+) \|')
    with open(INV, encoding='utf-8') as f:
        for line in f:
            m = rx.match(line)
            if m:
                rows.append((int(m.group(1)), m.group(2).strip(), m.group(4), m.group(5).strip()))
    return rows


def files():
    out = []
    for dp, dn, fn in os.walk(TOP):
        dpn = dp.replace(chr(92), '/')
        if dpn == 'C:/kyty/KytyPS5':
            dn[:] = [d for d in dn if d == 'ps5 em']
        elif dpn.startswith('C:/kyty/KytyPS5/ps5 em'):
            dn[:] = []
        else:
            dn[:] = [d for d in dn if d not in SKIPDIRS and not d.startswith(SKIPPFX)]
        for f in fn:
            if f.endswith(('.txt', '.log')):
                p = dpn + '/' + f
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                if st.st_size > MINSIZE and st.st_mtime >= SINCE:
                    out.append(p)
    return sorted(out)


def scan(p):
    names = set()
    try:
        with open(p, 'rb') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            q = mm.find(KEY)
            while q != -1:
                e = mm.find(b'\n', q)
                s = mm[q + len(KEY):(e if e != -1 else q + 120)].strip()
                names.add(s.split()[0].decode('ascii', 'replace') if s else '')
                q = mm.find(KEY, q + 1)
            mm.close()
    except (OSError, ValueError):
        return p, None
    return p, sorted(names)


def main():
    inv = inventory()
    print('lvl146 inventory %s sha256 %s rows %d' % (INV, sha(INV), len(inv)))
    if len(inv) != 114:
        print('STOP: the map has %d rows, not 114' % len(inv))
        return 1
    fl = files()
    print('logs since 2026-09-30 (> 1 MB): %d files, %.1f GB' % (len(fl), sum(os.path.getsize(p) for p in fl) / 1e9))
    with Pool(8) as pool:
        res = pool.map(scan, fl, chunksize=1)
    unread = [p for p, n in res if n is None]
    entered = {}
    for p, n in res:
        for x in n or ():
            entered.setdefault(x, []).append(p)
    print('unreadable logs: %d %s' % (len(unread), unread[:5]))
    print('names with an entry line since 2026-09-30: %d' % len(entered))
    for x in sorted(entered):
        print('  entered %s in %d logs, first %s' % (x, len(entered[x]), sorted(entered[x])[0]))
    nonscene = [r for r in inv if NONSCENE_RX.match(r[2])]
    print('non-scenes of item 217 (g): %d %s' % (len(nonscene), [r[2] for r in nonscene]))
    inv_no = [r for r in inv if r[3].startswith('нет')]
    print('inventory column "entry" = net: %d' % len(inv_no))
    a_pool = [r for r in inv_no if not NONSCENE_RX.match(r[2]) and r[2] not in entered]
    print('reading (A): never-entered scene levels (with final_shooting) %d - item 309 (d) says 59 -> %s' % (
        len(a_pool), 'ok' if len(a_pool) == 59 else 'DIFFERENT'))
    a_list = [r for r in a_pool if r[2] != 'final_shooting'][:N_WANT]
    b_pool = [r for r in inv if not NONSCENE_RX.match(r[2]) and r[2] not in entered and r[2] != 'final_shooting']
    b_list = b_pool[:N_WANT]
    print('reading (B) (letter alone, inventory column ignored): pool %d; first 15 differ from (A): %s' % (
        len(b_pool), [r[2] for r in b_list if r not in a_list]))
    print('LIST146 (reading A, map order):')
    for i, r in enumerate(a_list):
        print('  v146_%02d/w146_%02d  map %3d  %-14s %s' % (i + 5, i + 5, r[0], r[1], r[2]))
    print('LIST146 names: %s' % ' '.join(r[2] for r in a_list))
    print('ALL DONE')
    return 0


if __name__ == '__main__':
    sys.exit(main())

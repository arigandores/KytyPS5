"""rt146_lvl.py - Red Team, s146 step 1 (HPP-387): own recount of the 15 never-entered levels of sc146 (item 309 (l)(2), 313 (b)).
READ ONLY.  Independent of step0/lvl146.py: every non-binary file under C:/kyty (any size, any extension except binary ones)
with mtime >= SINCE is scanned for b'Level has started:'; the name is the token after it up to whitespace.  Files are
classed 'log' (log_*, _kyty*, *stdout*, *.log) or 'other' (documents, fixtures, scripts).  The lock C:/kyty/SEALED_RUN.lock and
the stop file C:/kyty/s146/STOP abort the scan (rc 3 / 4).  usage: python rt146_lvl.py <out.txt>
"""
import datetime
import hashlib
import mmap
import os
import re
import sys
from multiprocessing import Pool

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOPF = 'C:/kyty/s146/STOP'
INV = 'C:/kyty/s141/step1b/inventory141_r2.md'
SINCE = datetime.datetime(2026, 9, 27, tzinfo=datetime.timezone.utc).timestamp()
S30 = datetime.datetime(2026, 9, 30, tzinfo=datetime.timezone.utc).timestamp()
KEY = b'Level has started:'
BINEXT = ('.mp4', '.png', '.jpg', '.exe', '.dll', '.rdc', '.pack', '.bundle', '.bin', '.idx', '.pyc', '.zip', '.7z', '.spv',
          '.gnfp', '.pdb', '.obj', '.lib', '.ilk', '.nv12', '.mkv', '.avi', '.raw', '.dds', '.pak')
LIST = ['robot_builder_next', 'interactive_credit_00', 'non_interactive_credit', 'ending_boss_after_credit', 'collectible_viewer',
        'hub_crashsite_diorama', 'diorama_controller_skin', 'diorama_astro_skin', 'diorama_zoo', 'fragile_battle_1',
        'voxel_challenge_1', 'armadillo_challenge_1', 'fragile_battle_2', 'voxel_challenge_2', 'fragile_battle_3']
NONSCENE = re.compile(r'^(ui_.*|.*_data|ps_logo|team_logo)$')


def files():
    out = []
    for dp, dn, fn in os.walk('C:/kyty'):
        d = dp.replace(chr(92), '/')
        if d.startswith('C:/kyty/KytyPS5/ps5 em/games') or '/.git' in d or d == 'C:/kyty/build' or d.startswith('C:/kyty/build/'):
            dn[:] = []
            continue
        for f in fn:
            if f.lower().endswith(BINEXT):
                continue
            p = d + '/' + f
            try:
                st = os.stat(p)
            except OSError:
                continue
            if st.st_size > 0 and st.st_mtime >= SINCE:
                out.append((p, st.st_size, st.st_mtime))
    return out


def kind(p):
    b = p.rsplit('/', 1)[-1]
    if b.startswith(('log_', '_kyty')) or 'stdout' in b or b.endswith('.log'):
        return 'log'
    return 'other'


def scan(item):
    p, size, mt = item
    if os.path.exists(LOCK):
        return p, 'LOCK'
    if os.path.exists(STOPF):
        return p, 'STOP'
    names = set()
    try:
        with open(p, 'rb') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            q = mm.find(KEY)
            while q != -1:
                e = mm.find(b'\n', q)
                s = mm[q + len(KEY):(e if e != -1 else q + 120)][:120].strip()
                names.add(s.split()[0].decode('ascii', 'replace') if s else '')
                q = mm.find(KEY, q + 1)
            mm.close()
    except (OSError, ValueError):
        return p, None
    return p, sorted(names)


def main():
    out = open(sys.argv[1], 'w', encoding='utf-8', newline='\n')
    fl = files()
    meta = dict((p, (s, m)) for p, s, m in fl)
    out.write('rt146_lvl files mtime >= 2026-09-27Z, non-binary, any size: %d, %.1f GB; of them mtime >= 2026-09-30Z: %d\n' % (
        len(fl), sum(s for _, s, _ in fl) / 1e9, sum(1 for _, _, m in fl if m >= S30)))
    with Pool(8) as pool:
        res = pool.map(scan, fl, chunksize=4)
    if any(n == 'LOCK' for _, n in res):
        out.write('ABORT: lock appeared\n')
        return 3
    if any(n == 'STOP' for _, n in res):
        out.write('ABORT: stop file\n')
        return 4
    unread = [p for p, n in res if n is None]
    out.write('unreadable: %d %s\n' % (len(unread), unread[:10]))
    ent = {}
    for p, n in res:
        for x in n or ():
            ent.setdefault(x, []).append(p)
    out.write('names after the key: %d\n' % len(ent))
    for x in sorted(ent):
        ps = ent[x]
        lg30 = [p for p in ps if kind(p) == 'log' and meta[p][1] >= S30]
        lgold = [p for p in ps if kind(p) == 'log' and meta[p][1] < S30]
        ot = [p for p in ps if kind(p) == 'other']
        out.write('  %r: log>=0930 %d, log 0927-0929 %d, other %d; first log %s; first other %s\n' % (
            x, len(lg30), len(lgold), len(ot), sorted(lg30 + lgold)[:1], sorted(ot)[:2]))
    inv = []
    rx = re.compile(r'^\| (\d+) \| [^|]+ \| [^|]+ \| `([a-z0-9_]+)` \| ([^|]+) \|')
    for line in open(INV, encoding='utf-8'):
        m = rx.match(line)
        if m:
            inv.append((int(m.group(1)), m.group(2), m.group(3).strip()))
    out.write('inventory rows %d sha256 %s\n' % (len(inv), hashlib.sha256(open(INV, 'rb').read()).hexdigest()))
    anyent = set(x for x, ps in ent.items() if any(kind(p) == 'log' for p in ps))
    ent30 = set(x for x, ps in ent.items() if any(kind(p) == 'log' and meta[p][1] >= S30 for p in ps))
    no = [r for r in inv if r[2].startswith('нет')]
    pool_a = [r for r in no if not NONSCENE.match(r[1]) and r[1] not in ent30]
    pool_a2 = [r for r in no if not NONSCENE.match(r[1]) and r[1] not in anyent]
    out.write('pool (A) entry col "net", no log entry line mtime >= 09-30: %d\n' % len(pool_a))
    out.write('pool (A2) same with logs mtime >= 09-27: %d; differ %s\n' % (
        len(pool_a2), [r[1] for r in pool_a if r not in pool_a2]))
    first = [r for r in pool_a if r[1] != 'final_shooting'][:15]
    out.write('first 15 (A): %s\n' % ' '.join(r[1] for r in first))
    out.write('= seal list: %s\n' % ([r[1] for r in first] == LIST))
    for nm in LIST:
        hits = ent.get(nm, [])
        out.write('  %s: entry-line hits in any file %d %s\n' % (nm, len(hits), hits[:3]))
    out.write('RT146_LVL DONE\n')
    out.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())

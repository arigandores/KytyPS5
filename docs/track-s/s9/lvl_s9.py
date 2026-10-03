"""lvl_s9.py - track S, link S9 (HPP-431; ROADMAP "SESSION 122" item 355 (d), (e)): the level lists of the third wave - the
T2 levels (item 355 (d)) and the U levels (item 355 (e)).  READ ONLY (mmap), ASCII output.  No game, no write but its own
output file (written by the caller's redirection).

T2 RULE (item 355 (d)): the five levels of item 241 (zh), then its reserves, in this order - only those WITHOUT a line
"Level has started: <level>" in every log under C:/kyty since 2026-09-30 23:41:52Z (the snapshot snap0), track roots P, F, S
included; when fewer than five remain - the next ones "of the list of never-entered scene levels of session 146
(C:/kyty/s146/step0/)" in order.
  Reading of "the list" used (executor's variant, printed): the pool (A) of C:/kyty/s146/step0/lvl146.py - the inventory
  rev. 2 (C:/kyty/s141/step1b/inventory141_r2.md, table (A), 114 rows) column "entry" = "net", without the non-scenes of item
  217 (g) and without final_shooting - in map order (LIST146 is its first 15); a level of the pool counts only without an
  entry line since T0 (the rule above).  Reading of LIST146 alone (the 15 names printed by lvl146.out.txt) is printed beside.
  Tags: t2_1 .. t2_5 the first five, t2_6 .. t2_10 the reserves (executor's variant: five reserves, as item 241 (zh)).
U RULE (item 355 (e)): a level is in the catalogue when >= 1 log on a binary with the translator signature
"56189185...:fixb26:fixb1b" (the line "ShaderSeed: compatibility=" of the log carries the exact signature SIG below - the one of
the recipe file of variant_fixb26_fixb1b) WITH cache writes (not an arm with a return) carries "Level has started: <level>".
  "An arm with a return" (executor's reading, printed): a log under a root whose harness returns the translation caches after
  every run - C:/kyty/s288 (go_s.sh, item 241 (g)(3)), C:/kyty/f287 (go_f*.sh, item 228 (v)), C:/kyty/p283 (gop*.sh,
  cachep15.py --restore), C:/kyty/play (the play session copies and returns _ShaderCache / _PipelineCache, its times.txt), and
  the emulator folder (its _kyty*.txt are copies of the last run of one of those harnesses); every other root (the session
  series s143-s146) writes the installed caches.
  Order: underwater_aerial_garden, hoover_beach, mini_giants_garden, then the levels "SCENE_OK <level>: YES" of
  C:/kyty/s146/step4/summary146_viewed.txt in file order; tags u_1 .. u_5 = the first five in the catalogue.
LOGS: every file *.txt / *.log under C:/kyty larger than 1 MiB with mtime >= T0, the walk of lvl146.py (directories build,
tools, scrub, .git, games, __pycache__, _Shaders, _ShaderCache, _RenderDoc, _PipelineCache and the prefixes mutwork,
mutcache, vidframes, cache_snap, cache_run, glcache_, pcache_ skipped; under C:/kyty/KytyPS5 only the emulator folder).  The .xz
files (HPP-401, item 328: sessions <= 139 and the root, compressed 2026-10-02 - their mtime is the compression time) are not
read: their count is printed (they predate T0 by their scope).  A worker refuses (the run ends rc 5) when the lock appears.
    python lvl_s9.py
"""
import calendar
import hashlib
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
SUM146 = 'C:/kyty/s146/step4/summary146_viewed.txt'
LVL146_OUT = 'C:/kyty/s146/step0/lvl146.out.txt'
KEY = b'Level has started: '
CKEY = b'ShaderSeed: compatibility='
SIG = b'KytySC3:56189185f9e9f9a0ea5174f3f85206e6d099db3d:robust:ftz:cbank:fixb26:fixb1b:'
SKIPDIRS = ('build', 'tools', 'scrub', '.git', 'games', '__pycache__', '_Shaders', '_ShaderCache', '_RenderDoc', '_PipelineCache')
SKIPPFX = ('mutwork', 'mutcache', 'vidframes', 'cache_snap', 'cache_run', 'glcache_', 'pcache_')
NONSCENE_RX = re.compile(r'^(ui_.*|.*_data|ps_logo|team_logo)$')
MINSIZE = 1 << 20
T2_241 = ('small_pot_lava', 'spin_drill_natural_cave', 'light_gadget_graveyard', 'enemy_taco', 'hero_kratos',
          'picup_light', 'enemy_snake', 'mini_rocket_chain', 'hero_drake', 'bonus_path_maker_mix')
T2_TAGS = 10
U_HEAD = ('underwater_aerial_garden', 'hoover_beach', 'mini_giants_garden')
U_N = 5
RETURN_ROOTS = ('C:/kyty/s288/', 'C:/kyty/f287/', 'C:/kyty/p283/', 'C:/kyty/play/', 'C:/kyty/KytyPS5/ps5 em/')


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()


def inventory(path=INV):
    rows = []
    rx = re.compile(r'^\| (\d+) \| ([^|]+) \| ([^|]+) \| `([a-z0-9_]+)` \| ([^|]+) \|')
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = rx.match(line)
            if m:
                rows.append((int(m.group(1)), m.group(2).strip(), m.group(4), m.group(5).strip()))
    return rows


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
    """(path, sorted level names, compatibility line or None, 'LOCK' when the lock appeared)."""
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


def scene_ok_146(path=SUM146):
    out = []
    rx = re.compile(r'^SCENE_OK ([a-z0-9_]+): YES')
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = rx.match(line)
            if m and m.group(1) not in out:
                out.append(m.group(1))
    return out


def list146(path=LVL146_OUT):
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            if line.startswith('LIST146 names: '):
                return line[len('LIST146 names: '):].split()
    return []


def t2_choice(entered, inv):
    """(chosen, rows): item 241 (zh) in order, then pool (A) in map order; each without an entry line since T0."""
    rows = []
    chosen = []
    for lv in T2_241:
        if lv in entered:
            rows.append('  241(zh) %-28s entered since T0 in %d logs (first %s) -> out' % (lv, len(entered[lv]),
                                                                                     sorted(entered[lv])[0]))
        else:
            rows.append('  241(zh) %-28s no entry line since T0 -> T2' % lv)
            chosen.append(lv)
    pool = [r for r in inv if r[3].startswith('нет') and not NONSCENE_RX.match(r[2]) and r[2] != 'final_shooting']
    for r in pool:
        if len(chosen) >= T2_TAGS:
            break
        if r[2] in chosen:
            continue
        if r[2] in entered:
            continue
        rows.append('  pool(A) map %3d %-14s %-28s no entry line since T0 -> T2' % (r[0], r[1], r[2]))
        chosen.append(r[2])
    return chosen, rows, pool


def u_choice(qual):
    order = list(U_HEAD) + [x for x in scene_ok_146() if x not in U_HEAD]
    rows = []
    chosen = []
    for lv in order:
        q = qual.get(lv, [])
        if q:
            chosen.append(lv)
            rows.append('  %-28s in the catalogue: %d logs with writes on the signature (first %s)%s' % (
                lv, len(q), sorted(q)[0], '' if len(chosen) <= U_N else ' - beyond the five'))
        else:
            rows.append('  %-28s NOT in the catalogue (no log with writes on the signature carries its entry line)' % lv)
    return chosen[:U_N], rows, order


def main():
    if os.path.exists(LOCK):
        print('LOCKED: %s exists - no scan' % LOCK)
        return 5
    t_start = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    print('lvl_s9 start %s; T0 %s; self sha256 %s' % (t_start, T0_TXT, sha(os.path.abspath(__file__))))
    inv = inventory()
    print('inventory %s sha256 %s rows %d' % (INV, sha(INV), len(inv)))
    if len(inv) != 114:
        print('STOP: the map has %d rows, not 114' % len(inv))
        return 1
    print('summary146_viewed %s sha256 %s; lvl146.out.txt sha256 %s' % (SUM146, sha(SUM146), sha(LVL146_OUT)))
    fl, nxz = files()
    print('logs since T0 (> 1 MiB, .txt/.log): %d files, %.1f GB; .xz files not read (mtime = compression time, HPP-401): %d'
          % (len(fl), sum(os.path.getsize(p) for p in fl) / 1e9, nxz))
    with Pool(8) as pool:
        res = pool.map(scan, fl, chunksize=1)
    if any(x[3] == 'LOCK' for x in res):
        print('LOCKED: the lock appeared during the scan - result void, rc 5')
        return 5
    unread = [p for p, n, c, w in res if w == 'UNREADABLE']
    print('unreadable logs: %d %s' % (len(unread), unread[:5]))
    entered = {}
    qual = {}
    nsig = 0
    nsig_w = 0
    for p, n, c, w in res:
        sig_ok = c is not None and SIG in c
        nsig += sig_ok
        nsig_w += sig_ok and not returned(p)
        for x in n or ():
            entered.setdefault(x, []).append(p)
            if sig_ok and not returned(p):
                qual.setdefault(x, []).append(p)
    print('names with an entry line since T0: %d' % len(entered))
    for x in sorted(entered):
        print('  entered %-28s in %3d logs, first %s' % (x or '<empty>', len(entered[x]), sorted(entered[x])[0]))
    print('T2 (item 355 (d)):')
    chosen, rows, pool = t2_choice(entered, inv)
    for r in rows:
        print(r)
    print('pool (A) (lvl146.py rule): %d levels; LIST146 (lvl146.out.txt): %s' % (len(pool), ' '.join(list146())))
    l146 = [x for x in list146() if x not in entered]
    print('reading "LIST146 alone" (printed beside): names of LIST146 without an entry line since T0: %d %s' % (len(l146), l146))
    print('T2 from item 241 (zh) alone: %d of %d' % (sum(1 for x in chosen if x in T2_241), len(T2_241)))
    for i, lv in enumerate(chosen):
        print('T2LIST t2_%d %s%s' % (i + 1, lv, '' if i < 5 else ' (reserve)'))
    print('T2NAMES %s' % ' '.join(chosen))
    print('U (item 355 (e)): logs whose compatibility line carries the signature %s: %d, of them with writes (not a '
          'returning root): %d' % (SIG.decode(), nsig, nsig_w))
    uch, urows, order = u_choice(qual)
    for r in urows:
        print(r)
    for i, lv in enumerate(uch):
        print('ULIST u_%d %s' % (i + 1, lv))
    print('UNAMES %s' % ' '.join(uch))
    print('lvl_s9 end %s' % time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    print('ALL DONE')
    return 0 if len(chosen) >= 5 and len(uch) == U_N else 6


if __name__ == '__main__':
    sys.exit(main())

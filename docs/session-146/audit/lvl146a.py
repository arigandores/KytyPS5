# lvl146a.py - Session Auditor, s146 step 3 (HPP-389): own recount of the list of the 15 never-entered scene levels of sc146
# (ROADMAP s122 items 309 (l)(2), 313 (b)) and of the "cold first entry" claim of the 15 V. No code of step0/lvl146.py or of
# the Red Team rt146_lvl2.py. READ ONLY, mmap.
#  (1) the level map: rows of table (A) of C:/kyty/s141/step1b/inventory141_r2.md (number, category, level file, entry column);
#  (2) every *.txt / *.log file > 1 MB under C:/kyty with mtime >= 2026-09-30T00:00:00Z (the game, build, tool, cache and
#      mutant work folders pruned; fixture folders fx_* kept apart): every "Level has started: <name>" line;
#  (3) pool by reading (A) = inventory "entry" column says no AND no entry line in a log written BEFORE the list moment
#      (step0 row 2026-10-02T07:02:15Z), without the non-scenes of item 217 (g) (ui_*, *_data, ps_logo, team_logo);
#      the first 15 by the map order without final_shooting = the sealed list?
#  (4) entries of the 15 levels outside the sc146 tags, by the time of the file - before the V of the pair or after it.
# Usage: python lvl146a.py
import os, re, mmap, datetime, hashlib
from multiprocessing import Pool

UTC = datetime.timezone.utc
TOP = 'C:/kyty'
INV = 'C:/kyty/s141/step1b/inventory141_r2.md'
SINCE = datetime.datetime(2026, 9, 30, tzinfo=UTC).timestamp()
LIST_T = datetime.datetime(2026, 10, 2, 7, 2, 15, tzinfo=UTC).timestamp()
KEY = b'Level has started: '
PRUNE = ('build', 'tools', 'scrub', '.git', 'games', '__pycache__', '_Shaders', '_ShaderCache', '_RenderDoc', '_PipelineCache', '3rdparty', 'node_modules')
PRUNE_PFX = ('mutwork', 'mutcache', 'vidframes', 'cache_snap', 'cache_run', 'glcache_', 'pcache_')
SEAL = ['robot_builder_next', 'interactive_credit_00', 'non_interactive_credit', 'ending_boss_after_credit', 'collectible_viewer',
        'hub_crashsite_diorama', 'diorama_controller_skin', 'diorama_astro_skin', 'diorama_zoo', 'fragile_battle_1', 'voxel_challenge_1',
        'armadillo_challenge_1', 'fragile_battle_2', 'voxel_challenge_2', 'fragile_battle_3']
NONSCENE = re.compile(r'^(ui_.*|.*_data|ps_logo|team_logo)$')


def iso(t):
    return datetime.datetime.fromtimestamp(t, UTC).strftime('%Y-%m-%dT%H:%M:%SZ')


def scan(p):
    names = {}
    try:
        with open(p, 'rb') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            q = mm.find(KEY)
            k = 0
            while q != -1 and k < 5000:
                e = mm.find(b'\n', q, q + 200)
                nm = mm[q + len(KEY):e if e != -1 else q + 80].strip().decode('ascii', 'replace')[:60]
                names[nm] = names.get(nm, 0) + 1
                k += 1
                q = mm.find(KEY, q + 1)
            mm.close()
    except (OSError, ValueError) as e:
        return p, None, repr(e)[:80]
    return p, names, None


def main():
    inv = []
    rx = re.compile(r'^[|] (\d+) [|] ([^|]+) [|] ([^|]+) [|] `([a-z0-9_]+)` [|] ([^|]+) [|]')
    for ln in open(INV, encoding='utf-8'):
        m = rx.match(ln)
        if m and int(m.group(1)) == len(inv) + 1:
            inv.append((int(m.group(1)), m.group(2).strip(), m.group(4), m.group(5).strip()))
    print('INVENTORY %s sha256 %s: map rows %d; entry column: yes %d, no %d, other %d' % (
        INV, hashlib.sha256(open(INV, 'rb').read()).hexdigest()[:16], len(inv), sum(1 for r in inv if r[3].startswith('да')),
        sum(1 for r in inv if r[3].startswith('нет')), sum(1 for r in inv if not r[3].startswith(('да', 'нет')))))
    files = []
    for dp, dn, fn in os.walk(TOP):
        d = dp.replace(chr(92), '/')
        dn[:] = [x for x in dn if x not in PRUNE and not x.startswith(PRUNE_PFX)]
        for f in fn:
            if f.endswith(('.txt', '.log')):
                p = d + '/' + f
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                if st.st_size > (1 << 20) and st.st_mtime >= SINCE:
                    files.append((p, st.st_size, st.st_mtime))
    files.sort()
    fx = [x for x in files if re.search(r'/fx[_/]|/fx$|fixture', x[0])]
    print('LOG FILES (*.txt, *.log > 1 MB, mtime >= 2026-09-30) under %s: %d, %.1f GB; of them in fixture folders %d; written before the list moment %s: %d' % (
        TOP, len(files), sum(x[1] for x in files) / 1e9, len(fx), iso(LIST_T), sum(1 for x in files if x[2] < LIST_T)))
    with Pool(8) as pool:
        res = pool.map(scan, [x[0] for x in files], chunksize=4)
    mt = {x[0]: x[2] for x in files}
    bad = [(p, e) for p, n, e in res if n is None]
    print('UNREADABLE %d %s' % (len(bad), bad[:5]))
    ent_before = {}
    ent_all = {}
    for p, names, e in res:
        if not names:
            continue
        isfx = bool(re.search(r'/fx[_/]|fixture', p))
        own = bool(re.match(r'C:/kyty/s146/(log|stdout)_[rvw]146_|C:/kyty/s146/[rvw]146_\d\d[.]stdout', p))
        for nm in names:
            ent_all.setdefault(nm, []).append((mt[p], p, isfx, own))
            if mt[p] < LIST_T and not isfx:
                ent_before.setdefault(nm, []).append((mt[p], p))
    for variant, src in (('real logs before the list moment', ent_before),):
        pool_ = [r for r in inv if r[3].startswith('нет') and r[2] not in src and not NONSCENE.match(r[2])]
        lst = [r for r in pool_ if r[2] != 'final_shooting'][:15]
        print('POOL by reading (A) on %s: never-entered scene levels %d (with final_shooting: %s); non-scenes of item 217 (g) in the map %d' % (
            variant, len(pool_), any(r[2] == 'final_shooting' for r in pool_), sum(1 for r in inv if NONSCENE.match(r[2]))))
        print('FIRST 15 own: %s' % [(r[0], r[2]) for r in lst])
        print('FIRST 15 own = the sealed list (order and names): %s' % ([r[2] for r in lst] == SEAL))
        poolb = [r for r in inv if r[2] not in src and not NONSCENE.match(r[2])]
        print('POOL by reading (B) (the inventory column ignored): %d' % len(poolb))
    inv_yes_noline = [r[2] for r in inv if r[3].startswith('да') and r[2] not in ent_before and not NONSCENE.match(r[2])]
    print('MAP levels with inventory entry "yes" and no entry line since 2026-09-30 before the list moment: %d' % len(inv_yes_noline))
    # (4) the 15 levels: every file with an entry line
    tags = {lv: ('v146_%02d' % i, 'w146_%02d' % i) for i, lv in enumerate(SEAL, 5)}
    other = 0
    for lv in SEAL:
        rows = sorted(ent_all.get(lv, []))
        own = [x for x in rows if x[3]]
        oth = [x for x in rows if not x[3] and not x[2] and not re.search(r'_a1[.]txt$|/step3/', x[1])]
        fxs = [x for x in rows if x[2]]
        first_own = min((x[0] for x in own), default=None)
        early = [x for x in oth if first_own is None or x[0] < first_own]
        other += len(early)
        print('LEVEL %s (%s): files with the entry line %d: own sc146 %d (first %s), fixtures %d, other real %d %s; other real EARLIER than the first sc146 file: %d' % (
            lv, '/'.join(tags[lv]), len(rows), len(own), iso(first_own) if first_own else None, len(fxs), len(oth),
            [(iso(x[0]), x[1].replace('C:/kyty/', '')) for x in oth[:4]], len(early)))
    print('ENTRY LINES OF THE 15 LEVELS IN REAL LOGS EARLIER THAN THEIR FIRST sc146 FILE: %d' % other)
    for lv in ('hoover_beach', 'sponge_dirty_bath', 'timestop_casino', 'bonus_path_maker_mix', 'underwater_aerial_garden'):
        rows = [x for x in ent_all.get(lv, []) if not x[2]]
        dac = [x for x in rows if x[0] >= datetime.datetime(2026, 10, 2, 6, 52, 29, tzinfo=UTC).timestamp()]
        print('RECHECK LEVEL %s: real logs with the entry line since 2026-09-30: %d; written after the install moment 2026-10-02T06:52:29Z: %d %s' % (
            lv, len(rows), len(dac), [(iso(x[0]), os.path.basename(x[1])) for x in sorted(dac)[:6]]))
    print('LEVEL NAMES in entry lines (real logs, before the list moment): %d' % len(ent_before))
    print('ALL DONE')


if __name__ == '__main__':
    main()

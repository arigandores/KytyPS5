"""Fresh source-side s101 -> s102 harness port; never run a carried *_port.py.

Written in the SOURCE folder (C:/kyty/s101) as docs/next-session-102.md 4 requires.
Only Python root literals change globally.  Five root constructs, the live
sealed-path repair (r6, now 13 files / 22 constants: the twelve inherited scorers plus
the session-101 scorer cm101.py, which carries bare PRED and PRED2 literals of its own)
and the four session-99 scorers whose PRED escapes const() (r7) are recorded separately
in the ledger.  No scorer, game or build is run.  The destination must not exist.
New session documents/scorers belong to their authors; inherited session
documents are archived under prev101 only.

Advances over s101_port.py, each asserted in preconditions():
  * COMMA chain 27 -> 28 roots (s102 ... s75); r1 splices s101 back in.
  * area_verdict.py range(102, 70, -1); shift91.py range(102, 66, -1).
  * s94lib.py 11 roots, bda93.py 12, stg92.py 13; regime94.py 10 roots + s102.
  * r6 grows 12 -> 13 files and 20 -> 22 constants (cm101.py PRED, PRED2).
  * SEALED grows 18 -> 21 (the three session-101 seals).
  * ABSENT grows 34 -> 35 ("cbmove"); gates.cpp must yield 134 = 99 + 35 entries
    (111 gates + 23 knobs).

One change of SHAPE, forced by the sources: two sealed texts now share a basename.
Session 100's prev100/pred/03_audit_addendum.md (10653 B, f3c2104b...) and session 101's
pred/03_audit_addendum.md (20259 B, 688b7be4...) cannot both land flat in prev101/pred,
and a sealed text is never renamed.  SEALED is therefore keyed by (source folder, name)
and every entry names its landing folder: twenty land in prev101/pred - every text a
live constant names is among them - and session 100's addendum, which no constant
names, is verified byte-exact where the walk carries it anyway,
prev100/pred/03_audit_addendum.md, the path session 101's FACTS.md already cites.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
SRC = Path('C:/kyty/s101')
DST = Path('C:/kyty/s102')
OLD, NEW = SRC.as_posix(), DST.as_posix()
GATES = Path('C:/kyty/KytyPS5/src/common/gates.cpp')
GATES_SHA = '00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8'
GATES_CPP_ENTRIES = 134  # 99 pinned in gates_base.txt + 35 ABSENT
GATES_CPP_SPLIT = (111, 23)  # DEFINITIONS rows, KNOB_DEFINITIONS rows
BIG = 5 * 1024 * 1024
SKIP_PREFIX = ('log_', 'stdout_', 'rec_', 'a80z_', 'hfx_')
SKIP_EXT = ('.mp4', '.idx', '.pyc', '.map', '.etl', '.exe')
SKIP_DIR = {'__pycache__', 'video99_comparison', 'video99_preview', 'video99_full',
            'video99_base_full'}
DOCS = ('README.md', 'FACTS.md', 'PLAN.md')
# Names a session-102 author may create; none may exist in SRC or arrive in DST.
NEW_SESSION = ('accept102.sh', 'fp102.py', 'm3_102.py', 'm5_102.py')
COMMA = {'arms.py': '--roots', 'baseline.py': '--roots', 'effect.py': '--extra-roots'}
ARITH = {'area_verdict.py': (70, 'r2'), 'shift91.py': (66, 'r3')}
TUPLES = {'stg92.py': 90, 'bda93.py': 91, 's94lib.py': 92}
DEGENERATE = ('area71_extract.py', 'clock_extract.py', 'area.py', 'area_band_check.py',
              'area_mix.py', 'area_summary.py', 'gputime.py', 'scene_point.py',
              'scene_clock.py', 'scene_drift.py', 'a80_statistics.py', 'cond80.py')
ABSENT = ('mutwide', 'bindpack', 'bindpackcheck', 'slotstat', 'slotstatcheck',
          'bdalap', 'plkstat', 'bindlap', 'bdasplit', 'bindpack2', 'bindpack2check',
          'bindkey', 'bdabits', 'bdabitscheck', 'proglap', 'drawmerge', 'drawmergecheck',
          'bindalt', 'bindwit', 'takelap', 'bufimp', 'bufimpcheck', 'stglap', 'copywake',
          'bdacap', 'mergecost', 'bdaall', 'framerep', 'pathlap', 'bindfloor', 'bfmode',
          'bfburn', 'bdaevery',
          # Session 100, measurement only: the 34th absent name.
          'blmove',
          # Session 101, measurement only, LAST row of gates.cpp DEFINITIONS: the 35th.
          'cbmove')
LAND = 'prev101/pred'
INHERITED = 'prev100/pred'
# (source folder in SRC, name, bytes, sha256, landing folder in DST)
SEALED = (
    (INHERITED, '01_bindings_only.md', 10848, '8b816528b78a1730c052d7fdbc414d7b00ef3b9c4df25ab2e7016b23d9d4b14d', LAND),
    (INHERITED, '01_floor_reversible.md', 15422, '7df5beb55cd964f58cd79a6b0caa697089cd3b20ea546e80ab2b10644f7d43af', LAND),
    (INHERITED, '01_hang_trigger.md', 19391, 'aca036c1a094c18176ad5ac04f69f9ed8a926bf81ac1d6f63760f8493c071cd3', LAND),
    (INHERITED, '01_pathlap.md', 12987, '94ea04b05e247f0bc7d13612cd27a0c46ea04907ac3d7aaf032f0df45696b212', LAND),
    (INHERITED, '01b_entry_hang.md', 4202, '3884109387e44f520b63fe5684340fc1828111dda30a7b99bdb9098ac41d49b6', LAND),
    (INHERITED, '02_bindfloor.md', 13039, 'e6c56dfcab222adac3e7541db1e2ae179d2c3b49f439dc5a53276d6aa39398c8', LAND),
    (INHERITED, '02_floor_walk.md', 12151, '9a88ab87a60789a2702bea4fb55939c6e578f25b4230482537361ee717f85519', LAND),
    (INHERITED, '02_m3_frame.md', 11825, '83144a3dfeff531eccd1da0bef91cdf882e4fcf4d6a70d8545f1ed9a53354389', LAND),
    (INHERITED, '02_settled_bindings.md', 13461, '1d1ebf286869ab59944fe135fc5c69d1315d4c61667b6c3dd2ab3ca14839724c', LAND),
    (INHERITED, '03_bdaevery.md', 8584, 'ada5682860cfd5ac5b61aefeeab1ea82eec29d4a80227974b84fb7b654c6dd0e', LAND),
    (INHERITED, '03_image_lifetime_diagnostic.md', 4724, 'd17745315149f0caad27f4c4764350f3e255fc9949a5b0287d9ea2a5e2c42c90', LAND),
    (INHERITED, '04_gc_audit.md', 7835, 'a93f4b6b1068cb34b06d02301d5c35f09483ef60f546f7669b03e193aeee611b', LAND),
    (INHERITED, '04_pathlap_identity.md', 6618, '584a13afcf07055086cb8b724695007d919846221bf096bab1407a64eaeb58f5', LAND),
    (INHERITED, '05_bdaevery_controls.md', 9087, '352448acaacd9b40fd0f01b77bdcf0b17a2cf708e7a928f3487db82f3d87c624', LAND),
    (INHERITED, '05_observer_separation.md', 8583, 'fb376ee63ce8fb19c7151e37c34ddc340fbecafc6aa648a27a9c160e7bc20af0', LAND),
    (INHERITED, '01_addend_census.md', 19152, '4c90060f91c21052238e0395abe2229e316012849c6bd54623d858edc5cf8c65', LAND),
    (INHERITED, '02_moved_mark.md', 11043, 'b1930f69f83a77d3bba359d4d18f0653f7fea6a331232dc9edaaf46c2a82e137', LAND),
    # Session 100's addendum, which WITHDREW the CLOSE of its pred/02.  Its basename is taken
    # in prev101/pred by session 101's addendum, so it stays where the walk carries it.
    (INHERITED, '03_audit_addendum.md', 10653, 'f3c2104b7a27b448a6c46a9526531c22e3d809546be5c51d90cca4e333ecad75', INHERITED),
    # Session 101.  pred/02 is the regime addendum and pred/03 the audit addendum that WITHDREW
    # the margin of pred/01; all three are immutable and travel byte-exact.
    ('pred', '01_two_directional.md', 29915, '091ecf76b85ff828fae298375bc5db0cbf85f92e1ee3c6e943d7e40114daeff2', LAND),
    ('pred', '02_regime_addendum.md', 9735, 'b4ef078beeeaa08b89a9d0fc969adbcaa959941d5694d040dbec3194271f0b29', LAND),
    ('pred', '03_audit_addendum.md', 20259, '688b7be482402049a36913112eb022582a884b9c104453e77c7891c739fa974e', LAND),
)
# r6: scorers whose PRED* are bare quoted literals const() can read.  The twelve
# inherited ones now point into s101/prev100/pred; the session-101 scorer cm101.py
# points into s101/pred.  Both kinds land in s102/prev101/pred.
REPOINT = {
    'pl96.py': ('PRED',), 'bf96.py': ('PRED', 'PRED97', 'PRED97B'),
    'bd96.py': ('PRED', 'PRED5'), 'check_s96_counters.py': ('PRED1', 'PRED4'),
    'rv97.py': ('PRED', 'PRED2'), 'm3_97.py': ('PRED',),
    'trig98.py': ('PRED',), 'rv98.py': ('PRED', 'PRED98', 'PRED01B', 'PRED2'),
    'bf98.py': ('PRED98_2',), 'm3_98.py': ('PRED',),
    'cen100.py': ('PRED',), 'mov100.py': ('PRED',),
    'cm101.py': ('PRED', 'PRED2'),
}
# Session-99 scorers whose PRED is a Path()/ROOT-relative expression, not the bare
# quoted literal const() can read (port repair 7, carried forward).  It rewrites the
# relative part only - prev100/pred -> prev101/pred - so the shape of each line and its
# neighbouring *_SHA are untouched.
# (file, constant, source form, repaired form, sealed basename, sealed folder in SRC)
REPOINT2 = (
    ('bf99.py', 'PRED', "PRED = Path('%s/prev100/pred/01_bindings_only.md')",
     "PRED = Path('%s/prev101/pred/01_bindings_only.md')", '01_bindings_only.md', INHERITED),
    ('settled99.py', 'PRED', "PRED = ROOT / 'prev100/pred/02_settled_bindings.md'",
     "PRED = ROOT / 'prev101/pred/02_settled_bindings.md'", '02_settled_bindings.md', INHERITED),
    ('settled99_gc.py', 'PRED', "PRED = ROOT / 'prev100/pred/04_gc_audit.md'",
     "PRED = ROOT / 'prev101/pred/04_gc_audit.md'", '04_gc_audit.md', INHERITED),
    ('settled99_norec.py', 'PRED', "PRED = ROOT / 'prev100/pred/05_observer_separation.md'",
     "PRED = ROOT / 'prev101/pred/05_observer_separation.md'", '05_observer_separation.md', INHERITED),
)
ARCHIVE_SCORERS = {'bf98_v1.py', 'bf98_v2.py', 'm3_98_v1.py', 'design98/rv98_before_N3.py',
                   'settled99.py', 'settled99_gc.py', 'settled99_norec.py', 'bf99.py',
                   'finalize99.py', 'finalize_cal99a.py',
                   'cen100.py', 'mov100.py', 'parent_recount100.py',
                   'parent_recount100_mov.py',
                   # Session 101: pinned to its own tags, binary, seals and PRODUCTION_ROOT
                   # (cm101.py:25, which the naive rewrite moves to s102 where no cm101 log lives).
                   'cm101.py', 'parent_recount101.py'}
OLDER_SCORERS = ('fr95.py', 'fr95b.py', 'mc94.py', 'bda94.py', 'stg92.py', 'bda93.py', 'shift91.py')
# Archive verifier of an earlier port: it carries a literal copy of the comma chain at
# verify_port99/verify.py:39, so r1 legitimately fires on it as well as on the three
# live files.  It is evidence of the s98 -> s99 port and is never run here.
R1_ARCHIVE = ('verify_port99/verify.py',)
# Frozen evidence copies of const()-escaping scorers that repair 7 deliberately does
# NOT reach (repair is keyed by the top-level file name).  Their PRED is left dangling.
FROZEN_DANGLING = ('verify_gc99_scorer/frozen/settled99.py',
                   'verify_gc99_scorer/frozen/settled99_gc.py',
                   'verify_gc99_scorer/frozen/settled99_gc_original_failed.py')
# Offline tests that read their seal as HERE / 'pred/...'.  pred/ is empty in every
# freshly ported root, so these dangle; test_cen100/test_mov100 already dangle in s101.
# Report only, never repaired: the port rewrites root literals, not test fixtures.
HERE_DANGLING = (('test_cen100.py', "pred = HERE / 'pred/01_addend_census.md'"),
                 ('test_mov100.py', "pred = HERE / 'pred/02_moved_mark.md'"),
                 ('test_cm101.py', "pred = HERE / 'pred/02_regime_addendum.md'"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rd(p):
    return p.read_bytes().decode('utf-8')


def chain(hi, lo, comma=False):
    values = ['C:/kyty/s%d' % i for i in range(hi, lo - 1, -1)]
    return ','.join(values) if comma else '(' + ', '.join(repr(v) for v in values) + ')'


def naive(t):
    for before, after in ((OLD, NEW), (OLD.replace('/', '\\\\'), NEW.replace('/', '\\\\')),
                          (OLD.replace('/', '\\'), NEW.replace('/', '\\')),
                          ('/c/kyty/s101', '/c/kyty/s102')):
        t = t.replace(before, after)
    return t


def const(t, name):
    m = re.search(r'^' + re.escape(name) + r"\s*=\s*'([^']*)'", t, re.M)
    assert m, ('missing string constant', name)
    return m.group(1)


def regime(hi):
    return "    root = next((r for r in %s if os.path.isfile('%%s/log_%%s.txt' %% (r, tag))), 'C:/kyty/s%d')" % (chain(hi, 93), hi)


def sealed_index():
    return {(d, n): (size, h, land) for d, n, size, h, land in SEALED}


def repair(t, key):
    out, fired = naive(t), set()
    def replace(tag, before, after, exact=True):
        nonlocal out
        if exact:
            assert out.count(before) == 1, (key, tag, 'anchor count', out.count(before))
        if before in out:
            out = out.replace(before, after)
            fired.add(tag)
    # Historically global: only these three LIVE files may fire; archive ports may fire too.
    replace('r1', 'C:/kyty/s102,C:/kyty/s100', 'C:/kyty/s102,C:/kyty/s101,C:/kyty/s100', False)
    if key in ARITH:
        floor, tag = ARITH[key]
        replace(tag, 'range(101, %d, -1)' % floor, 'range(102, %d, -1)' % floor)
    if key in TUPLES:
        replace('r4', naive(chain(101, TUPLES[key])), chain(102, TUPLES[key]))
    if key == 'regime94.py':
        replace('r5', naive(regime(101)), regime(102))
    for name in REPOINT.get(key, ()):
        path = const(t, name)
        old_line = "%s = '%s'" % (name, naive(path))
        new_line = "%s = '%s/%s/%s'" % (name, NEW, LAND, path.rsplit('/', 1)[1])
        replace('r6', old_line, new_line)
    for f, _name, before, after, _basename, _folder in REPOINT2:
        if key == f:
            replace('r7', naive(before % OLD) if '%s' in before else before,
                    after % NEW if '%s' in after else after)
    return out, sorted(fired)


def preconditions():
    assert SRC.resolve() != DST.resolve()
    assert not DST.exists(), 'destination exists: do not rerun a completed port'
    assert not (SRC / 'prev101').exists()
    for f, opt in COMMA.items():
        t = rd(SRC / f)
        m = re.search(r"add_argument\('" + re.escape(opt) + r"', default='([^']*)'", t)
        assert m and m.group(1) == chain(101, 75, True), f
        assert len(m.group(1).split(',')) == 27, f
    for f, (floor, _) in ARITH.items():
        assert rd(SRC / f).count('range(101, %d, -1)' % floor) == 1, f
    for f, floor in TUPLES.items():
        assert rd(SRC / f).count(chain(101, floor)) == 1, f
    assert rd(SRC / 'regime94.py').count(regime(101)) == 1
    assert rd(SRC / 'regime94.py').splitlines()[2] == 'import os, re, sys, statistics'
    sealed = sealed_index()
    assert len(sealed) == len(SEALED) == 21
    # No two texts may land on one path, no text is renamed, and the only shared basename
    # is the pair of audit addenda.
    assert len({(land, n) for _, n, _, _, land in SEALED}) == 21
    names_all = [n for _, n, _, _, _ in SEALED]
    assert sorted({n for n in names_all if names_all.count(n) > 1}) == ['03_audit_addendum.md']
    assert all(land in (LAND, d) for d, _, _, _, land in SEALED)
    assert sum(1 for _, _, _, _, land in SEALED if land == LAND) == 20
    for folder in {d for d, _, _, _, _ in SEALED}:
        assert sorted(p.name for p in (SRC / folder).iterdir()) == sorted(n for d, n, _, _, _ in SEALED if d == folder), folder
    for d, n, size, h, _ in SEALED:
        assert (SRC / d / n).stat().st_size == size and sha(SRC / d / n) == h, (d, n)
    live_paths = 0
    for f, names in REPOINT.items():
        t = rd(SRC / f)
        for name in names:
            p = Path(const(t, name))
            assert p.parent in (SRC / 'pred', SRC / INHERITED), (f, name, p)
            key = ('pred' if p.parent == SRC / 'pred' else INHERITED, p.name)
            assert const(t, name + '_SHA') == sealed[key][1] == sha(p), (f, name)
            assert sealed[key][2] == LAND, ('live constant names a text outside prev101/pred', f, name)
            live_paths += 1
    assert live_paths == 22, live_paths
    for f, name, before, _after, basename, folder in REPOINT2:
        t = rd(SRC / f)
        anchor = before % OLD if '%s' in before else before
        assert t.count(anchor) == 1, ('r7 anchor', f, t.count(anchor))
        assert const(t, name + '_SHA') == sealed[(folder, basename)][1] == sha(SRC / folder / basename), f
        assert sealed[(folder, basename)][2] == LAND, f
    g = SRC / 'gates_base.txt'
    assert g.stat().st_size == 1092 and sha(g) == GATES_SHA
    names = [x.split('=')[0] for x in rd(g).split() if '=' in x]
    assert len(names) == len(set(names)) == 99
    text = rd(GATES)
    entry = r'\{\s*"KYTY_\w+",\s*"([a-z0-9]+)"'
    cpp = re.findall(entry, text)
    assert len(cpp) == len(set(cpp)) == GATES_CPP_ENTRIES, len(cpp)
    cut = text.index('KNOB_DEFINITIONS')
    split = (len(re.findall(entry, text[:cut])), len(re.findall(entry, text[cut:])))
    assert split == GATES_CPP_SPLIT, split
    assert len(ABSENT) == 35 == GATES_CPP_ENTRIES - 99
    assert set(ABSENT) == set(cpp) - set(names)
    assert not set(ABSENT) & set(names)
    assert all(not (SRC / f).exists() for f in NEW_SESSION)
    print('PRECONDITIONS PASS: 5 root constructs; 21 sealed texts (20 land in prev101/pred, 1 stays '
          'in carried prev100/pred); 22 live paths + 4 expression paths; gates 1092 B / 99 names; '
          'gates.cpp 134 entries (111 gates + 23 knobs); ABSENT 35')


def main():
    preconditions()
    carried, ledger, skipped = [], {}, []
    planned = []
    # Preflight ALL decoding and repair anchors before writing the destination.
    for root, dirs, files in os.walk(SRC):
        rel = Path(root).relative_to(SRC)
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIR and not (rel == Path('.') and (d == 'pred' or d.startswith('design102'))))
        for f in sorted(files):
            sp = Path(root) / f
            key = sp.relative_to(SRC).as_posix()
            if (f.startswith(SKIP_PREFIX) or f.endswith(SKIP_EXT) or sp.stat().st_size >= BIG
                    or (rel == Path('.') and f in DOCS)):
                skipped.append(key)
                continue
            output, fired = (repair(rd(sp), key) if f.endswith('.py') else (None, []))
            planned.append((key, output, fired, sha(sp)))
    DST.mkdir()
    for key, output, fired, src_sha in planned:
        sp, dp = SRC / key, DST / key
        dp.parent.mkdir(parents=True, exist_ok=True)
        if output is None:
            shutil.copy2(sp, dp)
        else:
            dp.write_bytes(output.encode('utf-8'))
        carried.append((key, src_sha, sha(dp)))
        if fired:
            a, b = naive(rd(sp)).splitlines(), rd(dp).splitlines()
            assert len(a) == len(b), key
            ledger[key] = {'repairs': fired, 'lines': [i for i, (x, y) in enumerate(zip(a, b), 1) if x != y]}
    prev = DST / 'prev101'
    (prev / 'pred').mkdir(parents=True)
    (DST / 'pred').mkdir()
    for f in DOCS:
        if (SRC / f).is_file():
            shutil.copy2(SRC / f, prev / f)
    for d, n, _, _, land in SEALED:
        if land == LAND:
            shutil.copy2(SRC / d / n, DST / LAND / n)
    diagnostics(carried, ledger)
    (DST / 'port102_ledger.json').write_text(json.dumps({'source': OLD, 'destination': NEW, 'files': ledger,
        'carried_count': len(carried), 'skipped_count': len(skipped), 'archive_scorers': sorted(ARCHIVE_SCORERS),
        'sealed_landing': ['%s/%s -> %s/%s' % (d, n, land, n) for d, n, _, _, land in SEALED]}, indent=2) + '\n', encoding='utf-8')
    print('PORT DIAGNOSTIC: clean; carried=%d ledger=%d skipped=%d' % (len(carried), len(ledger), len(skipped)))


def diagnostics(carried, ledger):
    live = {k: v for k, v in ledger.items() if not k.endswith('_port.py')}
    expected = {'r1': sorted(list(COMMA) + list(R1_ARCHIVE)), 'r2': ['area_verdict.py'], 'r3': ['shift91.py'],
                'r4': sorted(TUPLES), 'r5': ['regime94.py'], 'r6': sorted(REPOINT),
                'r7': sorted(f for f, _, _, _, _, _ in REPOINT2)}
    for tag, want in expected.items():
        got = sorted(k for k, v in live.items() if tag in v['repairs'])
        assert got == want, (tag, got, want)
        if tag != 'r1':
            assert not any(tag in v['repairs'] for k, v in ledger.items() if k.endswith('_port.py'))
        print('LEDGER %s PASS: %s' % (tag, ', '.join(got)))
    naive_regime = naive(rd(SRC / 'regime94.py'))
    blind = naive_regime.replace("'C:/kyty/s102', 'C:/kyty/s100'", "'C:/kyty/s102', 'C:/kyty/s101', 'C:/kyty/s100'")
    assert blind == naive_regime.replace(naive(regime(101)), regime(102))
    assert 'r4' not in live['regime94.py']['repairs']
    for key, src_sha, dst_sha in carried:
        assert sha(SRC / key) == src_sha, ('source changed during port', key)
        if not key.endswith('.py'):
            assert src_sha == dst_sha, ('non-Python drift', key)
        else:
            expected_text, _ = repair(rd(SRC / key), key)
            assert rd(DST / key) == expected_text, key
            if key not in ledger:
                assert rd(DST / key) == naive(rd(SRC / key)), key
    for f in DEGENERATE:
        assert f not in ledger and rd(DST / f) == naive(rd(SRC / f))
    print('INTEGRITY PASS: every carried file verified; 12 degenerate chains unchanged beyond naive rewrite')
    for f, opt in COMMA.items():
        m = re.search(r"add_argument\('" + re.escape(opt) + r"', default='([^']*)'", rd(DST / f))
        assert m and m.group(1) == chain(102, 75, True) and len(m.group(1).split(',')) == 28, f
    for f, (floor, _) in ARITH.items():
        assert rd(DST / f).count('range(102, %d, -1)' % floor) == 1, f
    for f, floor in TUPLES.items():
        assert rd(DST / f).count(chain(102, floor)) == 1, f
    print('ADVANCE PASS: COMMA 28 roots; range(102, 70/66, -1); stg92 13, bda93 12, s94lib 11 roots')
    sealed = sealed_index()
    for f, names in REPOINT.items():
        t = rd(DST / f)
        for name in names:
            p = Path(const(t, name))
            assert p.parent == DST / LAND, (f, name, p)
            assert sha(p) == const(t, name + '_SHA') == const(rd(SRC / f), name + '_SHA')
    for f, name, _before, after, basename, folder in REPOINT2:
        t = rd(DST / f)
        anchor = after % NEW if '%s' in after else after
        assert t.count(anchor) == 1, ('r7 result', f)
        p = DST / LAND / basename
        assert p.is_file() and sha(p) == const(t, name + '_SHA') == sealed[(folder, basename)][1], f
        print('R7 PASS: %s %s -> %s/%s' % (f, name, LAND, basename))
    assert len(list((DST / LAND).iterdir())) == 20
    for d, n, size, h, land in SEALED:
        p = DST / land / n
        assert p.stat().st_size == size and sha(p) == h == sha(SRC / d / n), (d, n)
        print('SEALED PASS: %s/%s %d B %s' % (land, n, size, h))
    inherited = sorted(p.name for p in (DST / INHERITED).iterdir())
    assert inherited == sorted(n for d, n, _, _, _ in SEALED if d == INHERITED)
    for d, n, _, h, _ in SEALED:
        if d == INHERITED:
            assert sha(DST / INHERITED / n) == h, n
    print('CARRIED SEALED PASS: %s holds all %d inherited texts byte-exact (walk carry)' % (INHERITED, len(inherited)))
    assert not list((DST / 'pred').iterdir())
    assert all(not (DST / f).exists() for f in DOCS + NEW_SESSION)
    for f in DOCS:
        if (SRC / f).is_file():
            assert sha(SRC / f) == sha(DST / 'prev101' / f)
    for f in sorted(ARCHIVE_SCORERS):
        assert (DST / f).is_file(), ('archive scorer missing', f)
        # r6/r7 only repoint a sealed path; they never make an archive scorer runnable.
        assert f not in live or set(live[f]['repairs']) <= {'r6', 'r7'}, ('archive scorer entered live repair', f)
        print('ARCHIVE, DO NOT RUN: %s; carried by naive rewrite (plus r6/r7 where listed)' % f)
    for name, root in (('accept101.sh', 'R=C:/kyty/s101'), ('accept100.sh', 'R=C:/kyty/s100'),
                       ('accept99.sh', 'R=C:/kyty/s99')):
        assert root in rd(DST / name), ('%s no longer carries its own root' % name)
        print('CARRIED SHELL, DO NOT RUN: %s still sets %s (the port rewrites .py only)' % (name, root))
    for f in FROZEN_DANGLING:
        t = rd(DST / f)
        assert "ROOT = Path('%s')" % NEW in t and "PRED = ROOT / 'pred/" in t, f
        print('FROZEN EVIDENCE, PRED LEFT DANGLING BY DESIGN: %s' % f)
    for f, line in HERE_DANGLING:
        assert rd(DST / f).count(line) == 1, f
        target = DST / 'pred' / line.rsplit('/', 1)[1].rstrip("'")
        assert not target.exists(), f
        print('HERE-RELATIVE TEST SEAL, DANGLING, REPORT ONLY: %s reads %s' % (f, target.relative_to(DST).as_posix()))
    for f in OLDER_SCORERS:
        for line in rd(DST / f).splitlines():
            if re.match(r'^PRED\w*\s*=', line) and '_SHA' not in line.split('=')[0]:
                print('OLDER PRED, REPORT ONLY: %s %s' % (f, line))
    roots = ast.literal_eval(re.search(r'^ROOTS = (.+)$', rd(DST / 's94lib.py'), re.M).group(1))
    assert roots == tuple('C:/kyty/s%d' % i for i in range(102, 91, -1))
    tests = [('cm101a', 101), ('cm101c', 101), ('cm101d', 101),
             ('cen100a', 100), ('cen100b', 100), ('mov100a', 100), ('mov100b_entry1', 100),
             ('bf99g', 99), ('bf99h', 99), ('aa99plain', 99), ('eng99a4', 99), ('eng99c2', 99),
             ('cal99a', 99), ('life99a', 99), ('vis99base', 99), ('bf99e', 99),
             ('bf98a', 98), ('bf98c', 98), ('rv98a', 98), ('trig98a', 98),
             ('rv97a', 97), ('bd96b', 97), ('pl96a', 96), ('fr95a', 95), ('mc94a', 94),
             ('bl93a', 93), ('stg92a', 92)]
    for tag, n in tests:
        found = next((r for r in roots if (Path(r) / ('log_%s.txt' % tag)).is_file()), None)
        assert found == 'C:/kyty/s%d' % n, (tag, found)
        print('ROOT PASS: %s -> %s' % (tag, found))
    assert rd(DST / 'regime94.py').count(regime(102)) == 1
    for tag, n in tests:
        if n < 93:
            continue
        found = next((r for r in roots[:-1] if (Path(r) / ('log_%s.txt' % tag)).is_file()), NEW)
        assert found == 'C:/kyty/s%d' % n
    assert next((r for r in roots[:-1] if (Path(r) / 'log_nosuch102.txt').is_file()), NEW) == NEW
    stale = []
    for p in DST.glob('*.py'):
        if p.name.endswith('_port.py'):
            continue
        hits = [i for i, line in enumerate(rd(p).splitlines(), 1) if OLD in line]
        if hits:
            stale.append(p.name)
            assert len(hits) == 1, (p.name, hits)
    assert sorted(stale) == sorted(list(COMMA) + list(TUPLES) + ['regime94.py']), stale
    leaked = [p.relative_to(DST).as_posix() for p in DST.rglob('*') if p.is_file() and
              (p.name.startswith(('log_', 'stdout_', 'rec_')) or p.name.endswith(SKIP_EXT) or p.stat().st_size >= BIG)]
    assert not leaked, leaked
    g = DST / 'gates_base.txt'
    assert sha(g) == GATES_SHA and g.stat().st_size == 1092
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    result = subprocess.run([sys.executable, '-B', str(DST / 'gen_gates.py'), '--check'],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    print('gen_gates.py --check exit=%d (expected out-of-date for deliberately pinned baseline)' % result.returncode)
    print(result.stdout.decode('utf-8', 'replace').strip())
    assert result.returncode in (0, 1), result.returncode
    assert sha(g) == GATES_SHA and sha(SRC / 'gates_base.txt') == GATES_SHA
    print('GATES PASS: check-only, unchanged SHA; no scorer/game/build invoked')


if __name__ == '__main__':
    main()

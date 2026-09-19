"""Fresh source-side s98 -> s99 harness port; never run a carried *_port.py.

Only Python root literals change globally. Five root constructs and the live
sealed-path repair are recorded separately in the ledger. No scorer is run.
The destination must not exist. New session documents/scorers belong to their
authors; inherited session documents are archived under prev98 only.
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
SRC = Path('C:/kyty/s99')
DST = Path('C:/kyty/s99')
OLD, NEW = SRC.as_posix(), DST.as_posix()
GATES = Path('C:/kyty/KytyPS5/src/common/gates.cpp')
GATES_SHA = '00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8'
BIG = 5 * 1024 * 1024
SKIP_PREFIX = ('log_', 'stdout_', 'rec_', 'a80z_', 'hfx_')
SKIP_EXT = ('.mp4', '.idx', '.pyc', '.map', '.etl')
SKIP_DIR = {'__pycache__', 'raw', 'vidframes_bpc84a', 'vidframes_bpc83a',
            'vidframes_rv97a', 'vidcheck97', 'vidframes_rv98a'}
DOCS = ('README.md', 'FACTS.md', 'PLAN.md')
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
          'bfburn', 'bdaevery')
SEALED = (
    ('prev97/pred', '01_floor_reversible.md', 15422, '7df5beb55cd964f58cd79a6b0caa697089cd3b20ea546e80ab2b10644f7d43af'),
    ('prev97/pred', '02_floor_walk.md', 12151, '9a88ab87a60789a2702bea4fb55939c6e578f25b4230482537361ee717f85519'),
    ('prev97/pred', '01_pathlap.md', 12987, '94ea04b05e247f0bc7d13612cd27a0c46ea04907ac3d7aaf032f0df45696b212'),
    ('prev97/pred', '02_bindfloor.md', 13039, 'e6c56dfcab222adac3e7541db1e2ae179d2c3b49f439dc5a53276d6aa39398c8'),
    ('prev97/pred', '03_bdaevery.md', 8584, 'ada5682860cfd5ac5b61aefeeab1ea82eec29d4a80227974b84fb7b654c6dd0e'),
    ('prev97/pred', '04_pathlap_identity.md', 6618, '584a13afcf07055086cb8b724695007d919846221bf096bab1407a64eaeb58f5'),
    ('prev97/pred', '05_bdaevery_controls.md', 9087, '352448acaacd9b40fd0f01b77bdcf0b17a2cf708e7a928f3487db82f3d87c624'),
    ('pred', '01_hang_trigger.md', 19391, 'aca036c1a094c18176ad5ac04f69f9ed8a926bf81ac1d6f63760f8493c071cd3'),
    ('pred', '01b_entry_hang.md', 4202, '3884109387e44f520b63fe5684340fc1828111dda30a7b99bdb9098ac41d49b6'),
    ('pred', '02_m3_frame.md', 11825, '83144a3dfeff531eccd1da0bef91cdf882e4fcf4d6a70d8545f1ed9a53354389'),
)
REPOINT = {
    'pl96.py': ('PRED',), 'bf96.py': ('PRED', 'PRED97', 'PRED97B'),
    'bd96.py': ('PRED', 'PRED5'), 'check_s96_counters.py': ('PRED1', 'PRED4'),
    'rv97.py': ('PRED', 'PRED2'), 'm3_97.py': ('PRED',),
    'trig98.py': ('PRED',), 'rv98.py': ('PRED', 'PRED98', 'PRED01B', 'PRED2'),
    'bf98.py': ('PRED98_2',), 'm3_98.py': ('PRED',),
}
ARCHIVE_SCORERS = {'bf98_v1.py', 'bf98_v2.py', 'm3_98_v1.py', 'design98/rv98_before_N3.py'}
OLDER_SCORERS = ('fr95.py', 'fr95b.py', 'mc94.py', 'bda94.py', 'stg92.py', 'bda93.py', 'shift91.py')


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
                          ('/c/kyty/s99', '/c/kyty/s99')):
        t = t.replace(before, after)
    return t


def const(t, name):
    m = re.search(r'^' + re.escape(name) + r"\s*=\s*'([^']*)'", t, re.M)
    assert m, ('missing string constant', name)
    return m.group(1)


def regime(hi):
    return "    root = next((r for r in %s if os.path.isfile('%%s/log_%%s.txt' %% (r, tag))), 'C:/kyty/s%d')" % (chain(hi, 93), hi)


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
    replace('r1', 'C:/kyty/s99,C:/kyty/s98,C:/kyty/s97', 'C:/kyty/s99,C:/kyty/s99,C:/kyty/s98,C:/kyty/s97', False)
    if key in ARITH:
        floor, tag = ARITH[key]
        replace(tag, 'range(98, %d, -1)' % floor, 'range(99, %d, -1)' % floor)
    if key in TUPLES:
        replace('r4', naive(chain(98, TUPLES[key])), chain(99, TUPLES[key]))
    if key == 'regime94.py':
        replace('r5', naive(regime(98)), regime(99))
    for name in REPOINT.get(key, ()):
        path = const(t, name)
        old_line = "%s = '%s'" % (name, naive(path))
        new_line = "%s = '%s/prev98/pred/%s'" % (name, NEW, path.rsplit('/', 1)[1])
        replace('r6', old_line, new_line)
    return out, sorted(fired)


def preconditions():
    assert SRC.resolve() != DST.resolve()
    assert not DST.exists(), 'destination exists: do not rerun a completed port'
    assert not (SRC / 'prev98').exists()
    for f, opt in COMMA.items():
        t = rd(SRC / f)
        m = re.search(r"add_argument\('" + re.escape(opt) + r"', default='([^']*)'", t)
        assert m and m.group(1) == chain(98, 75, True), f
    for f, (floor, _) in ARITH.items():
        assert rd(SRC / f).count('range(98, %d, -1)' % floor) == 1, f
    for f, floor in TUPLES.items():
        assert rd(SRC / f).count(chain(98, floor)) == 1, f
    assert rd(SRC / 'regime94.py').count(regime(98)) == 1
    assert rd(SRC / 'regime94.py').splitlines()[2] == 'import os, re, sys, statistics'
    sealed_by_name = {n: h for _, n, _, h in SEALED}
    for folder in {d for d, _, _, _ in SEALED}:
        assert sorted(p.name for p in (SRC / folder).iterdir()) == sorted(n for d, n, _, _ in SEALED if d == folder)
    for d, n, size, h in SEALED:
        assert (SRC / d / n).stat().st_size == size and sha(SRC / d / n) == h, n
    for f, names in REPOINT.items():
        t = rd(SRC / f)
        for name in names:
            p = Path(const(t, name))
            assert p.parent in (SRC / 'pred', SRC / 'prev97/pred'), (f, name, p)
            assert const(t, name + '_SHA') == sealed_by_name[p.name] == sha(p)
    g = SRC / 'gates_base.txt'
    assert g.stat().st_size == 1092 and sha(g) == GATES_SHA
    names = [x.split('=')[0] for x in rd(g).split() if '=' in x]
    assert len(names) == len(set(names)) == 99
    cpp = re.findall(r'\{\s*"KYTY_\w+",\s*"([a-z0-9]+)"', rd(GATES))
    assert set(ABSENT) == set(cpp) - set(names)
    assert not set(ABSENT) & set(names)
    print('PRECONDITIONS PASS: 5 root constructs; 10 sealed texts; 18 live paths; gates 1092 B / 99 names')


def main():
    preconditions()
    carried, ledger, skipped = [], {}, []
    planned = []
    # Preflight ALL decoding and repair anchors before writing the destination.
    for root, dirs, files in os.walk(SRC):
        rel = Path(root).relative_to(SRC)
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIR and not (rel == Path('.') and (d == 'pred' or d.startswith('design99'))))
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
    prev = DST / 'prev98'
    (prev / 'pred').mkdir(parents=True)
    (DST / 'pred').mkdir()
    for f in DOCS:
        if (SRC / f).is_file():
            shutil.copy2(SRC / f, prev / f)
    for d, n, _, _ in SEALED:
        shutil.copy2(SRC / d / n, prev / 'pred' / n)
    diagnostics(carried, ledger)
    (DST / 'port99_ledger.json').write_text(json.dumps({'source': OLD, 'destination': NEW, 'files': ledger,
        'carried_count': len(carried), 'skipped_count': len(skipped), 'archive_scorers': sorted(ARCHIVE_SCORERS)}, indent=2) + '\n', encoding='utf-8')
    print('PORT DIAGNOSTIC: clean; carried=%d ledger=%d skipped=%d' % (len(carried), len(ledger), len(skipped)))


def diagnostics(carried, ledger):
    live = {k: v for k, v in ledger.items() if not k.endswith('_port.py')}
    expected = {'r1': sorted(COMMA), 'r2': ['area_verdict.py'], 'r3': ['shift91.py'],
                'r4': sorted(TUPLES), 'r5': ['regime94.py'], 'r6': sorted(REPOINT)}
    for tag, want in expected.items():
        got = sorted(k for k, v in live.items() if tag in v['repairs'])
        assert got == want, (tag, got, want)
        if tag != 'r1':
            assert not any(tag in v['repairs'] for k, v in ledger.items() if k.endswith('_port.py'))
        print('LEDGER %s PASS: %s' % (tag, ', '.join(got)))
    naive_regime = naive(rd(SRC / 'regime94.py'))
    blind4 = naive_regime.replace("'C:/kyty/s99', 'C:/kyty/s97'", "'C:/kyty/s99', 'C:/kyty/s99', 'C:/kyty/s97'")
    assert blind4 == naive_regime.replace(naive(regime(98)), regime(99))
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
    for f, names in REPOINT.items():
        t = rd(DST / f)
        for name in names:
            p = Path(const(t, name))
            assert p.parent == DST / 'prev98/pred'
            assert sha(p) == const(t, name + '_SHA') == const(rd(SRC / f), name + '_SHA')
    assert len(list((DST / 'prev98/pred').iterdir())) == 10
    for d, n, size, h in SEALED:
        p = DST / 'prev98/pred' / n
        assert p.stat().st_size == size and sha(p) == h == sha(SRC / d / n)
        print('SEALED PASS: %s %d B %s' % (n, size, h))
    assert not list((DST / 'pred').iterdir())
    assert all(not (DST / f).exists() for f in DOCS + ('accept99.sh', 'bf99.py', 'm3_99.py'))
    for f in DOCS:
        if (SRC / f).is_file():
            assert sha(SRC / f) == sha(DST / 'prev98' / f)
    for f in sorted(ARCHIVE_SCORERS):
        assert f not in ledger, ('archive scorer entered live repair', f)
        print('ARCHIVE, DO NOT RUN: %s; carried by naive rewrite only' % f)
    for f in OLDER_SCORERS:
        for line in rd(DST / f).splitlines():
            if re.match(r'^PRED\w*\s*=', line) and '_SHA' not in line.split('=')[0]:
                print('OLDER PRED, REPORT ONLY: %s %s' % (f, line))
    roots = ast.literal_eval(re.search(r'^ROOTS = (.+)$', rd(DST / 's94lib.py'), re.M).group(1))
    assert roots == tuple('C:/kyty/s%d' % i for i in range(99, 91, -1))
    tests = [('bf98a', 98), ('bf98c', 98), ('rv98a', 98), ('rv98a_warmup', 98),
             ('bf98a_warmup', 98), ('bf98c_warmup', 98), ('trig98a', 98),
             ('rv97a', 97), ('rv97b', 97), ('bd96b', 97), ('pl96a', 96),
             ('fr95a', 95), ('mc94a', 94), ('bl93a', 93), ('stg92a', 92)]
    for tag, n in tests:
        found = next((r for r in roots if (Path(r) / ('log_%s.txt' % tag)).is_file()), None)
        assert found == 'C:/kyty/s%d' % n, (tag, found)
        print('ROOT PASS: %s -> %s' % (tag, found))
    assert rd(DST / 'regime94.py').count(regime(99)) == 1
    for tag, n in tests:
        if n < 93:
            continue
        found = next((r for r in roots[:-1] if (Path(r) / ('log_%s.txt' % tag)).is_file()), NEW)
        assert found == 'C:/kyty/s%d' % n
    assert next((r for r in roots[:-1] if (Path(r) / 'log_nosuch99.txt').is_file()), NEW) == NEW
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

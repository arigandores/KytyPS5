"""F25m (HPP-680; ROADMAP s122 item 622 (v)(1)-(3)): fixtures of the promote of two series files into user files D - snap_f25m.py promote
(state B only; names equal in A and B, not in D, live, changed; any other difference from B -> STOP, nothing touched; the update limit;
the copies in A' and B', the tsv lines, D.tsv, updates.log; reconcile EQUAL after), the class rule after the promote (a change of these
files is a user update, another series file still stops), the restore writes the snapshot content into the files D, go_f25m.sh promoteD
(text members, the lock refusal touches nothing), strict cp1250 output.  ASCII only; ends with ALL OK.
usage: python test_p622_f25m.py"""
import hashlib
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import snap_f25m as SN_M  # noqa: E402

SN = os.path.join(HERE, 'snap_f25m.py')
GO = os.path.join(HERE, 'go_f25m.sh')
print('suite test_p622_f25m.py sha256 %s target snap_f25m.py sha256 %s go_f25m.sh sha256 %s' % tuple(
    hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in (os.path.abspath(__file__), SN, GO)))
ok = True
nchk = 0


def check(name, cond, got=None):
    global ok, nchk
    nchk += 1
    if not cond:
        ok = False
        print('FAIL %s (got %s)' % (name, got))


def env_cp1250():
    e = dict(os.environ)
    e.pop('PYTHONIOENCODING', None)
    e['PYTHONUTF8'] = '0'
    return e


TMP = os.path.join(HERE, 'fx_p622')
if os.path.isdir(TMP):
    shutil.rmtree(TMP)
lv = os.path.join(TMP, 'live')
rt = os.path.join(TMP, 'snap')
LV = ['--live', 'S=%s' % os.path.join(lv, 'S'), 'G=%s' % os.path.join(lv, 'G')]


def put(rel, data):
    p = os.path.join(lv, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'wb').write(data)


def sn(*a):
    p = subprocess.run([sys.executable, SN] + list(a) + ['--root', rt] + LV, capture_output=True, env=env_cp1250())
    try:
        p.stdout.decode('ascii')
        asc = True
    except UnicodeDecodeError:
        asc = False
    check('cp1250 / ASCII output of %s' % (a[:1],), asc and p.stderr == b'', p.stderr[-200:])
    return p.returncode, p.stdout.decode('ascii', 'replace')


def state_bytes():
    out = {}
    for n in ('A.tsv', 'B.tsv', 'D.tsv', 'A0.tsv', 'B0.tsv', 'updates.log', 'STATE'):
        p = os.path.join(rt, n)
        out[n] = open(p, 'rb').read() if os.path.exists(p) else None
    for snap in ('A', 'B'):
        for f in ('drv/f.bin', 'drv/f.toc'):
            p = os.path.join(rt, snap, 'G', f)
            out[snap + f] = open(p, 'rb').read() if os.path.exists(p) else None
    return out


tsv = lambda n: SN_M.read_tsv(os.path.join(rt, n + '.tsv'))  # noqa: E731
FB, FT = 'G/drv/f.bin', 'G/drv/f.toc'
KB, KT = ('G', 'drv/f.bin'), ('G', 'drv/f.toc')

put('S/a.bin', b'a')
put('S/old.bin', b'old')
put('G/drv/f.bin', b'driver-0')
put('G/drv/f.toc', b'toc-0')
put('G/drv/g.bin', b'g0')
check('take A', sn('take', 'A')[0] == 0)
put('S/a.bin', b'a2')
put('G/drv/g.bin', b'g1')          # the warm-up changes another driver file (differs between A and B)
os.remove(os.path.join(lv, 'S/old.bin'))
check('take B', sn('take', 'B')[0] == 0)
check('state B', sn('state', 'B')[0] == 0)
check('reconcile at B -> EQUAL', sn('reconcile')[1].startswith('RECONCILE EQUAL state B'))
put('G/drv/f.bin', b'driver-0+user-appended')     # the driver appends outside the tags (item 622 (a))
put('G/drv/f.toc', b'toc-0+user')
rc, out = sn('reconcile')
check('before the promote: the two changed files of A and B -> RECONCILE STOP rc 4 (item 606 (v)(4))', rc == 4 and 'STOP state B: 2' in out, (rc, out))

# refusals - nothing touched
before = state_bytes()
put('S/a.bin', b'a3')              # another series file changed as well
rc, out = sn('promote', FB, FT)
check('622 (v)(2): another series file differs from B -> PROMOTE STOP rc 4, names it', rc == 4 and out.startswith('PROMOTE STOP state B: 1') and
      'S/a.bin' in out, (rc, out))
check('622 (v)(2): PROMOTE STOP touched nothing', state_bytes() == before)
put('S/a.bin', b'a2')
put('G/u/new.bin', b'n')           # a new file outside the series also differs from B
rc, out = sn('promote', FB, FT)
check('622 (v)(2): a new non-series file -> PROMOTE STOP rc 4 too (L = B except the named files)', rc == 4 and 'G/u/new.bin' in out, (rc, out))
os.remove(os.path.join(lv, 'G/u/new.bin'))
for names, why in (((FB, 'G/drv/g.bin'), 'differs between A and B'), ((FB, 'S/b.bin'), 'not in both A and B'),
                   (('G/drv/x.bin',), 'not in both A and B'), ((FB, FB), 'a name twice'), (('nolabel',), 'bad name'), ((), 'no names')):
    rc, out = sn('promote', *names)
    check('622 (v)(1): refused %s -> rc 2 (%s), nothing touched' % (names, why), rc == 2 and out.startswith('PROMOTE REFUSED') and why in out and
          state_bytes() == before, (rc, out))
put('G/drv/f.toc', b'toc-0')       # the .toc back to B
rc, out = sn('promote', FB, FT)
check('622 (v)(1): a named file not changed against B -> REFUSED rc 2', rc == 2 and 'f.toc: not changed against B' in out and state_bytes() == before, (rc, out))
os.remove(os.path.join(lv, 'G/drv/f.toc'))
rc, out = sn('promote', FB, FT)
check('622 (v)(1): a named file not live -> REFUSED rc 2', rc == 2 and 'f.toc: not in the live set' in out and state_bytes() == before, (rc, out))
put('G/drv/f.toc', b'toc-0+user')
sn('state', 'A')
rc, out = sn('promote', FB, FT)
check('622 (v)(2): state A -> REFUSED rc 2', rc == 2 and 'only at state B' in out, (rc, out))
sn('state', 'B')
before = state_bytes()
open(os.path.join(rt, 'updates.log'), 'w').write('x1\nx2\n')
rc, out = sn('promote', FB, FT)
check('606 (v)(5): two updates already -> PROMOTE LIMIT rc 5, tsv untouched', rc == 5 and out.startswith('PROMOTE LIMIT') and
      tsv('B') == SN_M.read_tsv(os.path.join(rt, 'B.tsv')) and state_bytes()['B.tsv'] == before['B.tsv'] and state_bytes()['D.tsv'] == before['D.tsv'], (rc, out))
os.remove(os.path.join(rt, 'updates.log'))
check('the refusals touched nothing', state_bytes() == before)

# the promote
A0b, B0b = before['A0.tsv'], before['B0.tsv']
Dold = tsv('D')
rc, out = sn('promote', FB, FT)
lines = out.splitlines()
L = dict(((x.split('\t')[0], x.split('\t')[1]), (x.split('\t')[2], x.split('\t')[3])) for x in SN_M.M.manifest(LV[1:]) if x.split('\t')[1] != '<MISSING>')
check('622 (v)(1)-(2): PROMOTE DONE update 1 of 2, then RECONCILE EQUAL state B, rc 0', rc == 0 and len(lines) == 2 and
      lines[0].startswith('PROMOTE DONE update 1 of 2: state B promote 2') and lines[1].startswith('RECONCILE EQUAL state B'), (rc, out))
check("622 (v)(1): A' and B' carry the live sha of both files; copies in both snapshots = live",
      tsv('A')[KB] == L[KB] and tsv('B')[KB] == L[KB] and tsv('A')[KT] == L[KT] and tsv('B')[KT] == L[KT] and
      all(open(os.path.join(rt, s, 'G', 'drv', f), 'rb').read() == open(os.path.join(lv, 'G', 'drv', f), 'rb').read()
          for s in ('A', 'B') for f in ('f.bin', 'f.toc')))
check("622 (v)(4): A' differs from A only in the files D (other A lines kept, g.bin of A stays g0)",
      {k: v for k, v in tsv('A').items() if k not in (KB, KT)} == {k: v for k, v in SN_M.read_tsv(os.path.join(rt, 'A0.tsv')).items() if k not in (KB, KT)} and
      open(os.path.join(rt, 'A', 'G', 'drv', 'g.bin'), 'rb').read() == b'g0')
check('622 (v)(1): D.tsv = old D + the two files with the live sha', tsv('D') == dict(list(Dold.items()) + [(KB, L[KB]), (KT, L[KT])]))
ul = open(os.path.join(rt, 'updates.log'), encoding='ascii').read().splitlines()
check('622 (v)(1): one line in updates.log naming item 622 and both files', len(ul) == 1 and 'update 1 state B promote 2 (item 622 (v)(1))' in ul[0] and
      'drv/f.bin' in ul[0] and 'drv/f.toc' in ul[0], ul)
check('A0.tsv / B0.tsv keep the first snapshots (made from A / B before the promote when absent)', state_bytes()['A0.tsv'] == (A0b or before['A.tsv']) and
      state_bytes()['B0.tsv'] == (B0b or before['B.tsv']) and (KB, ) not in [] and SN_M.read_tsv(os.path.join(rt, 'B0.tsv'))[KB] != tsv('B')[KB])
rc, out = sn('promote', FB, FT)
check('a second promote of the same files -> REFUSED (already a user file D)', rc == 2 and 'already a user file D' in out, (rc, out))

# the class after the promote (item 622 (v)(3))
put('G/drv/f.bin', b'driver-0+user-appended+more')
rc, out = sn('reconcile')
check('622 (v)(3): a change of a promoted file outside the tags -> RECONCILE UPDATED 2 of 2 (changed 1), not STOP', rc == 0 and
      out.startswith('RECONCILE UPDATED 2 of 2: state B new 0 changed 1'), (rc, out))
put('S/a.bin', b'a9')
rc, out = sn('reconcile')
check('622 (v)(3): another series file of A or B -> still RECONCILE STOP rc 4', rc == 4 and 'S/a.bin' in out, (rc, out))
put('S/a.bin', b'a2')
put('G/drv/f.bin', b'emulator-wrote-this')
rc, out = sn('restore', 'A')
check("622 (v)(3): restore A' writes the snapshot content into the file D (the last user update), A' content elsewhere", rc == 0 and
      open(os.path.join(lv, 'G/drv/f.bin'), 'rb').read() == b'driver-0+user-appended+more' and
      open(os.path.join(lv, 'G/drv/g.bin'), 'rb').read() == b'g0' and open(os.path.join(lv, 'S/a.bin'), 'rb').read() == b'a', (rc, out))

# go_f25m.sh promoteD
g = open(GO, 'rb').read().decode('ascii')
blk = g[g.index('if [ "$T" = promoteD ]; then'):g.index('if [ "$T" = restoreA ]; then')]
check('go: promoteD names exactly the two files f7cc8370cc259634.bin / .toc of 06243430c577c784',
      'a5b98c7ed42c997333c17893d7aeb05a/06243430c577c784/f7cc8370cc259634.bin' in blk and
      'a5b98c7ed42c997333c17893d7aeb05a/06243430c577c784/f7cc8370cc259634.toc' in blk and blk.count('GLCache/') == 2)
check('go: promoteD - STOP, lock, runs once, STATE B, FS9, guard and hold before the lock, hold after it, no game',
      all(s in blk for s in ('$F/STOP', '[ -e $LOCK ]', 'runs/promoteD ] &&', 'snap/STATE', '"$FS9"', 'guard_f25m.py scan', 'hold_f25m.py check',
                             'set -o noclobber', 'lock taken promoteD', 'lock released promoteD')) and
      'enter_scene' not in blk and 'kyty_emulator' not in blk.replace('$GAME', '') and blk.count('hold_f25m.py check') == 2)
check('go: SERIES_STOP leaves only after rc 0, FS9 after and RECONCILE EQUAL state B',
      blk.index("grep -q '^RECONCILE EQUAL state B'") < blk.index('mv $G/SERIES_STOP') and '[ $PR = 0 ]' in blk)
check('go: the usage names promoteD', 'restoreA | promoteD"; exit 2' in g)
lk = os.path.join(TMP, 'lock')
open(lk, 'w').write('x')
p = subprocess.run(['C:/Program Files/Git/bin/bash.exe', GO, 'promoteD'], capture_output=True, env=dict(env_cp1250(), F25M_LOCK=lk.replace('\\', '/')))
check('go: promoteD with the lock held -> exit 3, runs/promoteD not made', p.returncode == 3 and b'lock held' in p.stdout and
      not os.path.exists(os.path.join(HERE, 'runs', 'promoteD')), (p.returncode, p.stdout[-200:]))

shutil.rmtree(TMP)
print('checks %d' % nchk)
print('ALL OK' if ok else 'FAILED')

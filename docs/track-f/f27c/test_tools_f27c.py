"""F27c (HPP-694): fixtures of the harness tools - f27c_tools.py (salt name = XXH3_64 of the salt, the blob header and payload on the
user blob as a positive control, cmp-labels), drvsnap_f27c.py (take / return on a fake NVIDIA folder: every class of the merge rule),
go_f27c.sh (dry-run knobs of every tag; ITEM 634 form: the guard and hold checks only after the lock, once; no block calls), launch_f27c.sh
(no guard, hold or block), the <app> mask of the procload line, the ports (enter_scene ROOT, the nvidia-smi step 500 ms, OWN of the API
tools), and the output of every python tool in strict cp1250.  The set ends with ALL OK.  ASCII only.
usage: python test_tools_f27c.py"""
import datetime
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f27c_tools as TT  # noqa: E402
import drvsnap_f27c as DS  # noqa: E402

N = 0
BAD = 0
BASH = 'C:/Program Files/Git/bin/bash.exe'


def check(name, cond, extra=''):
    global N, BAD
    N += 1
    if not cond:
        BAD += 1
    print('%s %s %s' % ('ok  ' if cond else 'FAIL', name, extra))


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def utc(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def main():
    env = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
    env['PYTHONIOENCODING'] = 'cp1250:strict'
    # f27c_tools
    check('salt-name of the empty salt = XXH3_64 empty 2d06800538d394c2', TT.salt_name('') == 'PPSA21564.2d06800538d394c2.bin', TT.salt_name(''))
    check('salt-name differs per tag', TT.salt_name('f27_v0') != TT.salt_name('f27_v1a'))
    tmp = tempfile.mkdtemp(prefix='f27c_tools_')
    try:
        b = os.path.join(tmp, 'b.bin')
        open(b, 'wb').write(b'KytyPC2:abc\n' + b'12345678' + b'x' * 100)
        r = TT.blob(b)
        check('blob header = signature line + 8', r['header'] == 12 + 8 and r['payload'] == 100, r)
        ub = 'C:/kyty/KytyPS5/ps5 em/_PipelineCache/PPSA21564.bin'
        if os.path.exists(ub):
            r = TT.blob(ub)
            check('positive control: user blob payload 127 690 297 = the saved bytes of s18_c09 (F27a)', r['payload'] == 127690297 and r['header'] == 76, r)
        a = os.path.join(tmp, 'a.tsv')
        c = os.path.join(tmp, 'c.tsv')
        open(a, 'wb').write(b'L1\tx\t1\taa\nL2\ty\t1\tbb\n')
        open(c, 'wb').write(b'L1\tx\t1\taa\nL2\ty\t1\tcc\n')
        check('cmp-labels EQUAL on L1', TT.cmp_labels(a, c, ['L1'])[0] == 0)
        check('cmp-labels DIFFER on L2', TT.cmp_labels(a, c, ['L2'])[0] == 1)
        check('cmp-labels DIFFER on L1,L2', TT.cmp_labels(a, c, ['L1', 'L2'])[0] == 1)
        # drvsnap: fake NV with GLCache/x/f, DXCache group files and another group
        nv = os.path.join(tmp, 'nv')
        root = os.path.join(tmp, 'root')
        os.makedirs(os.path.join(nv, 'GLCache', 'g1'))
        os.makedirs(os.path.join(nv, 'DXCache'))
        os.makedirs(root)
        def w(rel, data, mt=None):
            p = os.path.join(nv, rel)
            open(p, 'wb').write(data)
            if mt is not None:
                os.utime(p, (mt, mt))
        old = time.time() - 86400
        w('GLCache/g1/a.bin', b'gl-a', old)
        w('DXCache/%sAAAA.nvph' % DS.EMU_GROUP, b'emu-1', old)
        w('DXCache/%sBBBB.nvph' % DS.EMU_GROUP, b'emu-2', old)
        w('DXCache/%sCCCC.nvph' % DS.EMU_GROUP, b'emu-3', old)
        w('DXCache/0002a91cZZZZ.nvph', b'other', old)
        p = subprocess.run([sys.executable, os.path.join(HERE, 'drvsnap_f27c.py'), 'take', root, '--nv', nv], capture_output=True, env=env)
        check('drvsnap take rc 0 in cp1250', p.returncode == 0 and b'DRVSNAP TAKEN files 5' in p.stdout and b'copied 4' in p.stdout, p.stdout)
        now = time.time()
        lock = os.path.join(root, 'lock.log')
        open(lock, 'w').write('lock taken base %s\nlock released base %s\nlock taken f27_v0 %s\nlock released f27_v0 %s\n' % (
            utc(now - 3000), utc(now - 2900), utc(now - 600), utc(now - 100)))
        w('DXCache/%sAAAA.nvph' % DS.EMU_GROUP, b'emu-1-changed-by-tag', now - 300)          # inside the tag window -> RESTORED
        w('DXCache/%sBBBB.nvph' % DS.EMU_GROUP, b'emu-2-changed-by-user', now - 1500)        # outside -> KEPT_USER
        os.remove(os.path.join(nv, 'DXCache', '%sCCCC.nvph' % DS.EMU_GROUP))                  # removed -> RESTORED
        w('DXCache/%sNEW1.nvph' % DS.EMU_GROUP, b'new-by-tag', now - 200)                     # new inside, group -> MOVED
        w('DXCache/0002a91cNEW2.nvph', b'new-other', now - 200)                               # new inside, other group -> KEPT_NEW
        w('GLCache/g1/b.bin', b'gl-new', now - 1500)                                          # new outside -> KEPT_NEW
        p = subprocess.run([sys.executable, os.path.join(HERE, 'drvsnap_f27c.py'), 'return', root, lock, '--nv', nv], capture_output=True, env=env)
        out = p.stdout.decode('ascii')
        check('drvsnap return classes', 'restored 2 moved 1 kept_user 1 kept_new 2 not_copied 0 failed 0 windows 1' in out and p.returncode == 0, out)
        check('restored content = copy', open(os.path.join(nv, 'DXCache', '%sAAAA.nvph' % DS.EMU_GROUP), 'rb').read() == b'emu-1')
        check('removed file restored', open(os.path.join(nv, 'DXCache', '%sCCCC.nvph' % DS.EMU_GROUP), 'rb').read() == b'emu-3')
        check('user change kept', open(os.path.join(nv, 'DXCache', '%sBBBB.nvph' % DS.EMU_GROUP), 'rb').read() == b'emu-2-changed-by-user')
        check('new tag file moved out', not os.path.exists(os.path.join(nv, 'DXCache', '%sNEW1.nvph' % DS.EMU_GROUP)) and
              os.path.exists(os.path.join(root, 'drv_moved', 'DXCache', '%sNEW1.nvph' % DS.EMU_GROUP)))
        w('DXCache/0002a91cZZZZ.nvph', b'other-changed', now - 300)
        p = subprocess.run([sys.executable, os.path.join(HERE, 'drvsnap_f27c.py'), 'return', root, lock, '--nv', nv], capture_output=True, env=env)
        check('not copied group changed -> rc 1', p.returncode == 1 and b'not_copied 1' in p.stdout, p.stdout)
        check('window of a base/return mode is not a tag window', len(DS.windows(lock)) == 1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # go_f27c.sh dry runs
    go = os.path.join(HERE, 'go_f27c.sh').replace('\\', '/')
    for tag, pcw in (('f27_v0', True), ('f27_v0b', True), ('f27_v1a', False), ('f27_v1b', False), ('f27_v1c', False), ('f27_v1a_r1', False)):
        p = subprocess.run([BASH, go, tag], capture_output=True, env=dict(os.environ, F27C_DRYRUN='1'))
        o = p.stdout.decode('ascii', 'replace')
        ok = ('KYTY_PIPELINE_PRECACHE=0' in o and 'KYTY_PIPELINE_SALT=%s' % tag in o and ('KYTY_S_PCW=0' in o) == pcw and
              'KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0' in o and 'level rotating_level_day_and_night' in o and 'hold 120' in o and
              'sd 300' in o and 'timeout 480' in o and 'rec yes' in o and 'KYTY_GAME_PATCH' not in o and 'KYTY_FIX' not in o)
        check('dry run %s knobs' % tag, ok, o.strip())
    p = subprocess.run([BASH, go, 'f27_v2'], capture_output=True, env=dict(os.environ, F27C_DRYRUN='1'))
    check('unknown tag refused (rc 2)', p.returncode == 2)
    src = open(os.path.join(HERE, 'go_f27c.sh'), encoding='ascii').read().splitlines()
    lock_line = [i for i, l in enumerate(src) if '> $LOCK; }' in l]
    gscan = [i for i, l in enumerate(src) if 'guard_f27c.py scan' in l and not l.lstrip().startswith('#')]
    hchk = [i for i, l in enumerate(src) if 'hold_f27c.py check' in l and not l.lstrip().startswith('#')]
    mf_first = [i for i, l in enumerate(src) if 'manifest_fs4c.py' in l and not l.lstrip().startswith('#')]
    check('item 634: one guard scan, after the lock', len(gscan) == 1 and len(lock_line) == 1 and gscan[0] > lock_line[0], (gscan, lock_line))
    check('item 634: one hold check, after the lock', len(hchk) == 1 and hchk[0] > lock_line[0], hchk)
    check('item 634: the guard check before every manifest', gscan[0] < min(mf_first) and hchk[0] < min(mf_first))
    allsrc = '\n'.join(src) + open(os.path.join(HERE, 'launch_f27c.sh'), encoding='ascii').read()
    check('item 634: no block calls (open-block, status, guard tag)', not any(x in allsrc for x in ('open-block', 'guard_f27c.py status', 'guard_f27c.py tag', 'guard_f27c.py check')))
    lsrc = [l for l in open(os.path.join(HERE, 'launch_f27c.sh'), encoding='ascii').read().splitlines() if not l.lstrip().startswith('#')]
    check('item 634: launch has no guard or hold call', not any('guard_f27c' in l or 'hold_f27c' in l for l in lsrc))
    # mask
    p = subprocess.run([BASH, '-c', "echo \"procload: busy [('someapp.exe', 12, 0.9)]\" | sed -E \"s/\\('[^']*'/('<app>'/g\""], capture_output=True)
    check('mask of the procload line', b"('<app>', 12" in p.stdout and b'someapp' not in p.stdout, p.stdout)
    # ports
    es = open(os.path.join(HERE, 'enter_scene.py'), encoding='ascii').read()
    check('enter_scene ROOT = f27c', "ROOT = pathlib.Path('C:/kyty/f287/f27c')" in es)
    check('enter_scene nvidia-smi step 500 ms (P6)', "'-lms', '500'" in es.replace('\n', ' ').replace("'-lms',                                 '500'", "'-lms', '500'") or ("'-lms'," in es and "'500']" in es))
    check('enter_scene harness constants (lite, hang abort 8)', "KYTY_FRAME_TRACE='lite', KYTY_GPU_HANG_ABORT_S='8'" in es)
    for f in ('runchk_f27c.py', 'queue_f27c.py'):
        check('%s OWN HPP-694' % f, "OWN = 'HPP-694'" in open(os.path.join(HERE, f), encoding='ascii').read())
    check('guard G = f27c', "G = 'C:/kyty/f287/f27c'" in open(os.path.join(HERE, 'guard_f27c.py'), encoding='ascii').read())
    check('hold kills through guard_f27c', "'guard_f27c.py'" in open(os.path.join(HERE, 'hold_f27c.py'), encoding='ascii').read())
    # cp1250 output of the python tools (usage / help paths)
    for args in (['f27c_tools.py', 'salt-name', 'f27_v0'], ['f27c_tools.py'], ['drvsnap_f27c.py'], ['f27c_read.py']):
        p = subprocess.run([sys.executable, os.path.join(HERE, args[0])] + args[1:], capture_output=True, env=env)
        check('cp1250 strict: %s' % ' '.join(args), b'Traceback' not in p.stderr, p.stderr[-160:])
    print('checks %d failed %d' % (N, BAD))
    if BAD == 0:
        print('ALL OK')
    return 0 if BAD == 0 else 1


if __name__ == '__main__':
    print('suite test_tools_f27c.py sha256 %s target go_f27c.sh sha256 %s' % (sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'go_f27c.sh'))))
    sys.exit(main())

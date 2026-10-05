"""F20l (HPP-631): port of the F20e harness files into C:/kyty/f287/f20l (exact one-anchor replacements; LF; ASCII).  usage: python port_f20l.py"""
import os
import shutil
import sys

SRC = 'C:/kyty/f287/f20e'
DST = 'C:/kyty/f287/f20l'


def rd(p):
    return open(p, 'rb').read().decode('ascii').replace('\r\n', '\n')


def wr(p, s):
    open(p, 'wb').write(s.encode('ascii'))


def rep(s, old, new, count=1, name=''):
    c = s.count(old)
    if count is not None and c != count:
        print('ANCHOR %s count %d != %d: %r' % (name, c, count, old[:80]))
        sys.exit(1)
    return s.replace(old, new)


for nm in ('procload.py', 'manifest_fs4c.py', 'sheet142.py', 'gates_default.txt'):
    shutil.copy2(os.path.join(SRC, nm), os.path.join(DST, nm))

s = rd(SRC + '/enter_scene.py')
s = rep(s, "ROOT = pathlib.Path('C:/kyty/f287/f20e')  # F20e (HPP-624, item 543 (e)): the directory",
        "ROOT = pathlib.Path('C:/kyty/f287/f20l')  # F20l (HPP-631, item 550 (z)); before it F20e (HPP-624, item 543 (e)): the directory",
        name='enter_scene ROOT')
wr(DST + '/enter_scene.py', '# Track F link F20l (HPP-631): the F20e file of this role with ROOT moved (f287/f20e to f287/f20l); nothing else changed.\n' + s)

s = rd(SRC + '/guard_f20e.py')
s = rep(s, "G = 'C:/kyty/f287/f20e'", "G = 'C:/kyty/f287/f20l'", name='guard G')
s = rep(s, 'Track F link F20e (HPP-624): guard of the user game', 'Track F link F20l (HPP-631; port of F20e guard_f20e.py, G moved): guard of the user game',
        name='guard head')
s = s.replace('guard_f20e.py', 'guard_f20l.py')
wr(DST + '/guard_f20l.py', s)

s = rd(SRC + '/queue_f20e.py')
s = rep(s, "OWN = 'HPP-624'", "OWN = 'HPP-631'", name='queue own')
s = rep(s, '"""F20e (HPP-624; ROADMAP s122 item 462 (g)): the lock queue check - F20e is the last',
        '"""F20l (HPP-631; port of F20e queue_f20e.py, own issue HPP-631; ROADMAP s122 item 462 (g)): the lock queue check - F20 is the last',
        name='queue head')
s = rep(s, 'other than HPP-624;', 'other than HPP-631;', name='queue other')
s = s.replace('queue_f20e.py', 'queue_f20l.py')
wr(DST + '/queue_f20l.py', s)

s = rd(SRC + '/test_guard_f20e.py')
s = rep(s, '"""F20e (HPP-624): fixtures of the guard', '"""F20l (HPP-631; port of F20e test_guard_f20e.py): fixtures of the guard', name='tg head')
for a, b in (('guard_f20e', 'guard_f20l'), ('go_f20e.sh', 'go_f20l.sh'), ('launch_f20e.sh', 'launch_f20l.sh'), ('wait_f20e.sh', 'wait_f20l.sh'),
             ('post_f20e.sh', 'post_f20l.sh'), ('test_guard_f20e.py', 'test_guard_f20l.py')):
    s = s.replace(a, b)
s = rep(s, "LENV = dict(os.environ, F20E_FS6B_WINDOW=os.path.join(TD, 'nowin'), F20E_TIMES=LT, F20E_DRYRUN='2', F20E_GUARD_BLOCK=LB, F20E_GUARD_FAKE=FK)",
        "LENV = dict(os.environ, F20L_TIMES=LT, F20L_DRYRUN='2', F20L_GUARD_BLOCK=LB, F20L_GUARD_FAKE=FK, F20L_QUEUE_SKIP='1')", name='tg lenv')
s = rep(s, "'launch_f20l.sh'), 'f20_v54']", "'launch_f20l.sh'), 'b32_pd']", name='tg tag')
s = rep(s, "LENV['F20E_DRYRUN'] = '1'\nrc, out, tl = launch()\ncheck('launch: dry run 1 stops before the guard (old fixtures)', rc == 0 and out.strip() == 'dryrun')\n",
        "p = subprocess.run([BASH, os.path.join(HERE, 'go_f20l.sh'), 'b32_pd2'], capture_output=True, text=True, env=dict(os.environ, F20L_DRYRUN='1'))\n"
        "check('go: dry run 1 names the form (pd2: loader half, KYTY_DIAG_B32=1)', p.returncode == 0 and 'loader half' in p.stdout and "
        "'KYTY_DIAG_B32=1' in p.stdout)\n", name='tg dry1')
s = rep(s, "check('go: kill at the exit and after the run by pid file only', go.count('guard_f20l.py kill-own --pidfile $OUT/game_pid.txt') == 2)",
        "check('go: kill at the exit and after the run by pid file only', go.count('guard_f20l.py kill-own --pidfile $OUT/game_pid.txt') == 2)\n"
        "i_bin = go.index('cp \"$BIN\" \"$GAME\"')\n"
        "i_bret = go.index('cp \"$PINNED\" \"$GAME\"')\n"
        "check('go: test binary installed after the cache copy, before enter_scene', i_cp < i_bin < i_es)\n"
        "check('go: FS8 returned after the wait for the user process, before the run manifest', i_gone < i_bret < i_mrun)\n"
        "check('go: M6 and the loader start before enter_scene, stop files touched after it and at the exit', go.index('m6_f20l.py') < i_es and "
        "go.index('b32_load.py') < i_es and go.count('touch $OUT/watch.stop $OUT/m6.stop $OUT/load.stop') == 1 and "
        "'touch $OUT/m6.stop $OUT/load.stop' in go[:i_mf])", name='tg kill')
wr(DST + '/test_guard_f20l.py', s)
print('port ok')

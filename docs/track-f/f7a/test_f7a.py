"""Fixtures of the F7a tools (HPP-397; ROADMAP p.327(e)): f7a_read.py (every outcome word and the capture place), rdsum_f7a.py
(actions, passes, targets, the done marker), win_f7a.py decide() (open / closed / error on each member), the <app> mask of the
procload output of go_f7a.sh (no input name in the output, item 324 (i)), ASCII output in strict cp1250 without
PYTHONIOENCODING (item 175 (v)).  The last line is 'ALL OK'.
  python test_f7a.py
"""
import hashlib
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f7a_read  # noqa: E402
import rdsum_f7a  # noqa: E402
import win_f7a  # noqa: E402


def sha(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


FAILS = []
CHECKS = [0]


def check(name, cond):
    CHECKS[0] += 1
    if not cond:
        FAILS.append(name)
        print('FAIL', name)


def ft(n, dt, draws):
    return b'FrameTrace: n=%d dt_us=%d lat_us=1 gpu_proc=0 submits=1 draws=%d draw_us=0\n' % (n, dt, draws)


def base_log(capture=True, finished=True, death=False, entry=True):
    L = [b'RenderDoc: API 1.6.0 bound\n']
    for n in range(1, 11):
        L.append(ft(n, 16000, 20))
    if entry:
        L.append(b'GuestOut: Level has started: enemy_final\n')
    L.append(ft(11, 16000, 50))
    L.append(ft(12, 20000, 300))  # first scene frame
    for n in range(13, 40):
        L.append(ft(n, 10000, 450))
        if n == 30 and capture:
            L.append(b'RenderDoc: auto capture at frame 640 (level+600)\n')
            L.append(b'RenderDoc: capture requested\n')
        if n == 31 and capture:
            L.append(b'RenderDoc: capture started\n')
        if n == 32 and capture:
            L.append(b'RenderDoc: captured guest flip 1/2\n')
        if n == 33 and capture:
            L.append(b'RenderDoc: captured guest flip 2/2\n')
            if finished:
                L.append(b'RenderDoc: capture finished\n')
        if n == 35 and death:
            L.append(b'Unhandled exception: access violation\n')
    return L


def t_read():
    r = f7a_read.read(base_log())
    w, text = f7a_read.verdict(r)
    check('read captured word', w == 'CAPTURED')
    check('read n_entry', r['n_entry'] == 10)
    check('read first scene frame (draws>=100 after entry)', r['n_fs'] == 12)
    check('read capture row', r['cap_row'] == 31)
    # dt from the first scene frame (row 12, 20000) through row 31 (19 rows x 10000)
    check('read capture place seconds', r['cum_to'] == 20000 + 19 * 10000)
    check('read place text', '19 presented frames after the first scene frame (0.21 s' in text)
    check('read auto', r['auto'] == (640, '600', 30))
    check('read flips', [f[0] for f in r['flips']] == [1, 2])
    check('read bound', r['bound'] == 1)
    w, _ = f7a_read.verdict(f7a_read.read(base_log(finished=False)))
    check('read no finish -> NO_CAPTURE', w == 'NO_CAPTURE')
    w, _ = f7a_read.verdict(f7a_read.read(base_log(capture=False)))
    check('read no capture -> NO_CAPTURE', w == 'NO_CAPTURE')
    w, _ = f7a_read.verdict(f7a_read.read(base_log(death=True)))
    check('read death -> DEATH_OR_WINDOW', w == 'DEATH_OR_WINDOW')
    L = base_log()
    L.insert(5, b'[Window] Window 1 minimized\n')
    w, _ = f7a_read.verdict(f7a_read.read(L))
    check('read window -> DEATH_OR_WINDOW', w == 'DEATH_OR_WINDOW')
    w, _ = f7a_read.verdict(f7a_read.read(base_log(entry=False)))
    check('read no entry -> NOT_ENTERED', w == 'NOT_ENTERED')
    L = base_log()
    L.append(b'RenderDoc: capture failed\n')
    w, _ = f7a_read.verdict(f7a_read.read(L))
    check('read failed -> NO_CAPTURE', w == 'NO_CAPTURE')
    # other level text does not arm the entry
    L = [x.replace(b'enemy_final', b'enemy_finalX_other') if b'Level has' in x else x for x in base_log()]
    L = [x.replace(b'enemy_finalX_other', b'final_stage') for x in L]
    w, _ = f7a_read.verdict(f7a_read.read(L))
    check('read other level -> NOT_ENTERED', w == 'NOT_ENTERED')
    # edge: draws exactly 100 is the first scene frame, 99 is not
    L = [ft(1, 1, 0), b'GuestOut: Level has started: enemy_final\n', ft(2, 1, 99), ft(3, 1, 100)]
    check('read edge draws 100', f7a_read.read(L)['n_fs'] == 3)


RD = """capture: C:/kyty/f287/f7a/enemy_final_600.rdc
EID=5 CLEAR vkCmdClearColorImage
EID=10 DRAW vkCmdDraw(3) | RT: tex A 1280x720x1 mips=1 fmt=R8G8B8A8 name= | DS: tex D 1280x720x1 mips=1 fmt=D32 name=
    Vertex shader=1 entry=main
EID=11 DRAW vkCmdDrawIndexed(6) | RT: tex A 1280x720x1 mips=1 fmt=R8G8B8A8 name= | DS: tex D 1280x720x1 mips=1 fmt=D32 name=
EID=12 DISPATCH vkCmdDispatch(1,1,1)
EID=13 DRAW vkCmdDraw(3) | RT: tex A 1280x720x1 mips=1 fmt=R8G8B8A8 name= | DS: tex D 1280x720x1 mips=1 fmt=D32 name=
EID=14 DRAW vkCmdDraw(3) | RT: tex B 640x360x1 mips=1 fmt=R16G16B16A16 name=
EID=20 COPY vkCmdCopyImage
EID=30 PRESENT vkQueuePresentKHR
done
"""


def t_rdsum():
    s = rdsum_f7a.summarize(io.StringIO(RD))
    check('rdsum draws', s['kinds']['DRAW'] == 4)
    check('rdsum dispatch/clear/copy/present', (s['kinds']['DISPATCH'], s['kinds']['CLEAR'], s['kinds']['COPY'],
                                                s['kinds']['PRESENT']) == (1, 1, 1, 1))
    check('rdsum passes split by dispatch and by target', [p[2] for p in s['passes']] == [2, 1, 1])
    check('rdsum targets', sorted(s['targets'].values()) == [1, 3])
    check('rdsum done', s['done'])
    s2 = rdsum_f7a.summarize(io.StringIO(RD.replace('done\n', '')))
    check('rdsum no done', not s2['done'])
    out = rdsum_f7a.render(s)
    check('rdsum last line', out.splitlines()[-1].startswith('RDSUM: draws 4, dispatches 1, clears 1, copies 1, presents 1, passes 3, targets 2, done marker yes'))
    check('rdsum capture', s['capture'] == 'C:/kyty/f287/f7a/enemy_final_600.rdc')
    check('rdsum empty', rdsum_f7a.summarize(io.StringIO(''))['kinds']['DRAW'] == 0)


def t_win():
    ok = {'HPP-378': ('done', None), 'HPP-393': ('blocked', None), 'HPP-364': ('done', None)}
    check('win open', win_f7a.decide(ok) == (0, 'open'))
    for i, st in (('HPP-378', ('in_review', None)), ('HPP-378', ('done', 'run1')), ('HPP-393', ('in_progress', None)),
                  ('HPP-393', ('todo', None)), ('HPP-393', ('blocked', 'run2')), ('HPP-364', ('in_progress', None))):
        d = dict(ok)
        d[i] = st
        check('win closed %s %s' % (i, st), win_f7a.decide(d) == (5, 'closed'))
    for i in ok:
        d = dict(ok)
        d[i] = (None, 'exception URLError')
        check('win error %s' % i, win_f7a.decide(d) == (6, 'error'))
    check('win members', win_f7a.ALL == ('HPP-378', 'HPP-393', 'HPP-364'))


def t_mask():
    # the mask() of go_f7a.sh, run by the real sed over procload lines with process names
    names = ['someappname', 'Other.App', 'x-y_z']
    lines = "procload: busy ('%s', 1234, 55.0) ('%s', 99, 20.1)\nprocload: busy ('%s', 7, 30.0)\nprocload: idle\n" % tuple(names)
    with open(os.path.join(HERE, 'go_f7a.sh'), encoding='ascii') as f:
        mline = [x for x in f.read().splitlines() if x.startswith('mask() {')]
    check('mask one definition in go_f7a.sh', len(mline) == 1)
    sed = None
    if len(mline) == 1:
        # the definition line of go_f7a.sh itself, run by bash from a file (msys re-parses quotes of a Win32 command line)
        fx = os.path.join(HERE, 'runs', '_fx_mask.sh')
        with open(fx, 'w', encoding='ascii', newline='\n') as f:
            f.write(mline[0] + '\nmask\n')
        for c in ('C:/Program Files/Git/bin/bash.exe', 'bash'):
            try:
                p = subprocess.run([c, fx], input=lines.encode('ascii'), capture_output=True)
                sed = p.stdout.decode('ascii').replace('\r', '')
                break
            except OSError:
                continue
        os.remove(fx)
    check('mask sed ran', sed is not None)
    if sed is not None:
        check('mask no input name in the output', not any(n in sed for n in names))
        check('mask keeps the rest', sed.count("('<app>'") == 3 and 'procload: idle' in sed)
    with open(os.path.join(HERE, 'go_f7a.sh'), encoding='ascii') as f:
        g = f.read()
    check('mask in go_f7a.sh is the tested text', 'mask() { sed -E "s/\\(\'[^\']*\'/(\'<app>\'/g"; }' in g)
    check('procload output goes through the mask', "procload.py --wait-s \"$1\" 2>&1 | mask >> $L" in g)


def t_cp1250():
    env = {k: v for k, v in os.environ.items() if k != 'PYTHONIOENCODING'}
    env['PYTHONIOENCODING'] = 'cp1250:strict'
    tmp = os.path.join(HERE, 'runs', '_fx_log.txt')
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    with open(tmp, 'wb') as f:
        f.writelines(base_log())
        f.write('GuestOut: \u0442\u0435\u043a\u0441\u0442 \u2014\n'.encode('utf-8'))
    p = subprocess.run([sys.executable, os.path.join(HERE, 'f7a_read.py'), tmp], capture_output=True, env=env)
    check('cp1250 f7a_read rc 0', p.returncode == 0)
    check('cp1250 f7a_read ascii', all(b < 128 for b in p.stdout))
    tmp2 = os.path.join(HERE, 'runs', '_fx_rd.txt')
    with open(tmp2, 'w', encoding='utf-8') as f:
        f.write(RD.replace('name=', 'name=\u0438\u043c\u044f'))
    p = subprocess.run([sys.executable, os.path.join(HERE, 'rdsum_f7a.py'), tmp2], capture_output=True, env=env)
    check('cp1250 rdsum rc 0', p.returncode == 0)
    check('cp1250 rdsum ascii', all(b < 128 for b in p.stdout))
    for t in (tmp, tmp2):
        os.remove(t)


def main():
    print('suite test_f7a.py sha256 %s target f7a_read.py sha256 %s target rdsum_f7a.py sha256 %s target win_f7a.py sha256 %s '
          'target go_f7a.sh sha256 %s' % (sha(__file__), sha(os.path.join(HERE, 'f7a_read.py')),
                                         sha(os.path.join(HERE, 'rdsum_f7a.py')), sha(os.path.join(HERE, 'win_f7a.py')),
                                         sha(os.path.join(HERE, 'go_f7a.sh'))))
    t_read()
    t_rdsum()
    t_win()
    t_mask()
    t_cp1250()
    print('checks %d, failures %d' % (CHECKS[0], len(FAILS)))
    if FAILS:
        print('FAILED')
        return 1
    print('ALL OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())

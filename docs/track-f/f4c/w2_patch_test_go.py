"""w2_patch_test_go.py - F4c wake 4: test_go_f4c.py under p.262 (d)-(g), 268 (v), 270 (d).  Anchors exactly once; LF."""
import sys

P = 'C:/kyty/f287/f4c/test_go_f4c.py'
s = open(P, 'rb').read().decode('ascii').replace('\r\n', '\n')
R = [
    ('"""test_go_f4c.py - fixtures of the cheap refusals of go_f4c.sh (F4c, HPP-337): usage, not configured, seal call line, one\n'
     'attempt, lock held, stop file, DRY plan.',
     '"""test_go_f4c.py - fixtures of the cheap refusals of go_f4c.sh (F4c, HPP-337): usage, not configured, seal call line, one\n'
     'attempt, lock held, stop file, DRY plan, binary strings (p.262(v)), stand A/Bp, window win_f4c (p.268(d), 270(d)).'),
    ("check('precache by default: KYTY_PIPELINE_PRECACHE never set, unset at start', 'KYTY_PIPELINE_PRECACHE=' not in src\n"
     "      and 'unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA KYTY_FIX_B26 KYTY_FIX_DUALSRC KYTY_PIPELINE_PRECACHE' in src)\n",
     "check('precache by default: KYTY_PIPELINE_PRECACHE never set, unset at start', 'KYTY_PIPELINE_PRECACHE=' not in src\n"
     "      and 'unset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA KYTY_FIX_B26 KYTY_FIX_DUALSRC KYTY_PIPELINE_PRECACHE KYTY_GPU_CHECKPOINTS KYTY_S_PCW\\n' in src)\n"
     "check('KYTY_FIX_B26 and KYTY_S_PCW never passed', 'KYTY_FIX_B26=' not in src and 'KYTY_S_PCW=' not in src and 'B26X' not in src)\n"
     "check('p.262(e) hold W 310 / V 330', 'VHOLD=\"330\"\\nWHOLD=\"310\"\\n' in src)\n"
     "check('p.262(g) pre-check before b and a, stop before the tag', 'f4c_read.py --pre-check $C' in src\n"
     "      and src.index('--pre-check $C') < src.index('python $ROOT/enter_scene.py') and 'series stop before the tag' in src\n"
     "      and '    f4c_b|f4c_a)\\n      PC=' in src)\n"
     "check('p.262(v) binary strings before the lock', 'SIGSTR=\"699c1e4b7db359067b461e029b913c4b6e78dc90\"' in src\n"
     "      and src.index('fix binary strings bad') < src.index('set -o noclobber'))\n"),
    ("check('executor order B4', 'SEQ=\"f4c_b f4c_a f4c_v f4c_g\"' in src)\n",
     "check('stand A order (b) (a) (v) (g), Bp (g) (b) (a) (v), stand constant A', 'STAND=\"A\"\\n' in src\n"
     "      and '  A) SEQ=\"f4c_b f4c_a f4c_v f4c_g\";;' in src and '  Bp) SEQ=\"f4c_g f4c_b f4c_a f4c_v\";;' in src)\n"),
    ("check('binary constant empty until the lead answers B1', 'BIN_F4C=\"\"\\n' in src and 'BIN_EXPECT=\"\"\\n' in src)\n",
     "check('binary constants of p.268(v)', 'BIN_F4C=\"C:/kyty/f287/bin/kyty_emulator_c9a5e198.exe\"\\n' in src\n"
     "      and 'BIN_EXPECT=\"c9a5e1986e254132f776f0c7f1c9446d0bdc862e199bbbc1d57aedf17d4c9f9b\"\\n' in src)\n"),
    ("check('p.256(e) HPP-332 window right before the lock', src.index('win332_f2c.py 2>&1') < src.index('set -o noclobber')\n"
     "      and src.index('busy \"stop file $STOPF appeared before the lock\"') < src.index('win332_f2c.py 2>&1'))\n",
     "check('p.268(d) window right before the lock', src.index('win_f4c.py 2>&1') < src.index('set -o noclobber')\n"
     "      and src.index('busy \"stop file $STOPF appeared before the lock\"') < src.index('win_f4c.py 2>&1') and 'win332' not in src)\n"),
    ("import win332_f2c as W  # noqa: E402\n"
     "check('win332 in_progress closed rc 5', W.decide('in_progress') == (5, 'closed'))\n"
     "check('win332 done closed rc 5', W.decide('done') == (5, 'closed'))\n"
     "check('win332 blocked open rc 0', W.decide('blocked') == (0, 'open'))\n"
     "check('win332 todo open rc 0', W.decide('todo') == (0, 'open'))\n"
     "check('win332 no answer rc 6', W.decide(None) == (6, 'error') and W.decide('') == (6, 'error'))\n"
     "pw = subprocess.run([sys.executable, os.path.join(HERE, 'win332_f2c.py')], capture_output=True,\n"
     "                    env={k: v for k, v in os.environ.items() if not k.startswith('PAPERCLIP_') and k != 'PYTHONIOENCODING'})\n"
     "check('win332 without API env refuses rc 6, ASCII line (cp1250)', pw.returncode == 6 and pw.stdout.decode('cp1250').startswith('win332 HPP-332 status None'), pw)\n",
     "import win_f4c as W  # noqa: E402\n"
     "OPEN = {'HPP-333': ('done', None), 'HPP-347': ('done', None), 'HPP-328': ('blocked', None)}\n"
     "check('win open: audit and F4b2 done, P10 blocked', W.decide(OPEN) == (0, 'open'))\n"
     "check('win open: P10 done', W.decide(dict(OPEN, **{'HPP-328': ('done', None)})) == (0, 'open'))\n"
     "check('win closed: audit blocked', W.decide(dict(OPEN, **{'HPP-333': ('blocked', None)})) == (5, 'closed'))\n"
     "check('win closed: audit in_progress', W.decide(dict(OPEN, **{'HPP-333': ('in_progress', 'r1')})) == (5, 'closed'))\n"
     "check('win closed: audit done but a run alive', W.decide(dict(OPEN, **{'HPP-333': ('done', 'r1')})) == (5, 'closed'))\n"
     "check('win closed: F4b2 in_review', W.decide(dict(OPEN, **{'HPP-347': ('in_review', None)})) == (5, 'closed'))\n"
     "check('win closed: P10 todo (P before F)', W.decide(dict(OPEN, **{'HPP-328': ('todo', None)})) == (5, 'closed'))\n"
     "check('win closed: P10 in_progress', W.decide(dict(OPEN, **{'HPP-328': ('in_progress', None)})) == (5, 'closed'))\n"
     "check('win closed: P10 blocked with a run', W.decide(dict(OPEN, **{'HPP-328': ('blocked', 'r2')})) == (5, 'closed'))\n"
     "check('win error: one answer missing', W.decide(dict(OPEN, **{'HPP-347': (None, None)})) == (6, 'error')\n"
     "      and W.decide({}) == (6, 'error') and W.decide(dict(OPEN, **{'HPP-328': ('', None)})) == (6, 'error'))\n"
     "pw = subprocess.run([sys.executable, os.path.join(HERE, 'win_f4c.py')], capture_output=True,\n"
     "                    env={k: v for k, v in os.environ.items() if not k.startswith('PAPERCLIP_') and k != 'PYTHONIOENCODING'})\n"
     "check('win_f4c without API env refuses rc 6, ASCII line (cp1250)', pw.returncode == 6 and pw.stdout.decode('cp1250').startswith('win_f4c HPP-333 None'), pw)\n"),
    ("def make(binf='', bexp='', glr='', pred=None):\n",
     "def make(binf='', bexp='', glr='', pred=None, stand='A'):\n"),
    ("    s = re.sub(r'(?m)^GLRESTORE=\".*\"$', 'GLRESTORE=\"%s\"' % glr, s, count=1)\n",
     "    s = re.sub(r'(?m)^GLRESTORE=\".*\"$', 'GLRESTORE=\"%s\"' % glr, s, count=1)\n"
     "    s = re.sub(r'(?m)^STAND=\".*\"$', 'STAND=\"%s\"' % stand, s, count=1)\n"),
    ("check('DRY plan names the knob values and precache by default', 'KYTY_FIX_DUALSRC=0' in out and '=1' in out and 'precache by default' in out)\n",
     "check('DRY plan names the knob values and precache by default', 'KYTY_FIX_DUALSRC=0' in out and '=1' in out and 'precache by default' in out)\n"
     "check('DRY plan names stand A, its order, win_f4c and the pre-check', 'stand A tags f4c_b f4c_a f4c_v f4c_g' in out\n"
     "      and 'win_f4c' in out and 'pre-check' in out, out)\n"
     "make('x.exe', 'ab', '0', pred='# seal\\n' + CALL, stand='Bp')\n"
     "rc, out = run('series', env_add=dict(DRY='1'))\n"
     "check('DRY stand Bp order (g) (b) (a) (v)', rc == 0 and 'stand Bp tags f4c_g f4c_b f4c_a f4c_v' in out, (rc, out))\n"
     "make('x.exe', 'ab', '0', pred='# seal\\n' + CALL, stand='X')\n"
     "rc, out = run('series', env_add=dict(DRY='1'))\n"
     "check('unknown stand -> not configured rc 2', rc == 2 and 'not configured' in out, (rc, out))\n"
     "make('x.exe', 'ab', '0', pred='# seal\\n' + CALL)\n"),
    ("shutil.rmtree(FX, ignore_errors=True)\nprint('checks %d failed %d' % (N[0], len(FAIL)))\n",
     "SIG = b'699c1e4b7db359067b461e029b913c4b6e78dc90'\n"
     "PAT = b'DualSrcBlend: patched ps=%016'\n"
     "for nm, body, stand, want in (('strings: patched only, stand A -> rc 1 strings bad', b'x' + PAT + b'x', 'A', 'fix binary strings bad'),\n"
     "                              ('strings: signature only -> rc 1 strings bad', b'x' + SIG + b'x', 'A', 'fix binary strings bad'),\n"
     "                              ('strings: both, stand A -> passes the strings (gate file next)', SIG + b'\\x00' + PAT, 'A', 'gate file bad'),\n"
     "                              ('strings: patched only, stand Bp -> passes the strings', b'x' + PAT, 'Bp', 'gate file bad')):\n"
     "    shutil.rmtree(FX, ignore_errors=True)\n"
     "    os.makedirs(FX)\n"
     "    fb = os.path.join(FX, 'fake.exe')\n"
     "    open(fb, 'wb').write(body)\n"
     "    hb = sha(fb)\n"
     "    make(fb.replace('\\\\', '/'), hb, '1', pred='# seal\\n' + CALL, stand=stand)\n"
     "    open(fb, 'wb').write(body)\n"
     "    rc, out = run('series')\n"
     "    check(nm, rc == 1 and want in out and not os.path.exists(os.path.join(FX, 'LOCK')), (rc, out))\n"
     "shutil.rmtree(FX, ignore_errors=True)\nprint('checks %d failed %d' % (N[0], len(FAIL)))\n"),
]
for a, b in R:
    n = s.count(a)
    if n != 1:
        print('anchor count %d: %r' % (n, a[:90]))
        sys.exit(1)
    s = s.replace(a, b)
open(P, 'wb').write(s.encode('ascii'))
print('patched ok')

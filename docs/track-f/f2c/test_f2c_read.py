"""test_f2c_read.py - fixtures of f2c_read.py (F2c, HPP-310): every member of the arm verdicts and every edge, the seal check,
the real s142 logs (hard links in fx/real), and the ASCII output under a strict cp1250 console.  Last line: ALL OK."""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f2c_read as R  # noqa: E402

FX = os.path.join(HERE, 'fx', 'read')
REAL = os.path.join(HERE, 'fx', 'real')
LV = 'underwater_aerial_garden'
H5 = None
N = [0]
FAIL = []


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def check(name, cond, detail=''):
    N[0] += 1
    if not cond:
        FAIL.append(name)
        print('FAIL %s %s' % (name, detail))


def write_run(root, tag, fix='1', precache=True, val=False, rows=18100, dt=16667, k3=(), hash_in_k3=(), death=False,
              vke=0, knob_lines=0, glitches=0, vframes=12000, sheet=True, env_fix='same', hold_s=330.0, noval=False,
              ops=None, ready=True, rec=True):
    os.makedirs(root, exist_ok=True)
    L = []
    L.append('Shader translation cache: _ShaderCache\\PPSA21564%s' % ('\\variant_fixb26' if fix == '1' else ''))
    if precache:
        L.append('PipelinePrecache: 1592 recipes -> 1590 pipelines')
    if val:
        L.append('VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features')
        L.append('[Vulkan][I] layer active')
    if noval:
        L.append('no validation layer: VK_LAYER_KHRONOS_validation')
    if ops is None:
        ops = {('SOP1', '0x21'): 96, ('VOPC', '0xf3'): 4} if fix == '1' else {('SOP1', '0x21'): 96, ('SOP1', '0x0c'): 1,
                                                                             ('VOPC', '0xe3'): 4}
    for (fam, op), n in ops.items():
        for _ in range(n):
            L.append('shader: opcode is not implemented family=%s opcode=%s' % (fam, op))
    for h in sorted(H5):
        if fix == '1' and ready:
            L.append('CsPretranslate: ready hash=%s bytes=100' % h)
    for _ in range(knob_lines):
        L.append('RbCen: n=1')
    L.append('GuestOut: Level has started: %s' % LV)
    L.append('FrameTrace: n=0 dt_us=500000 draws=10')
    L.append('FrameTrace: n=1 dt_us=900000 draws=500')
    hk = list(sorted(H5))
    for i in range(rows):
        n = i + 2
        if n in hash_in_k3:
            L.append('DumpDispatch: cs hash=%s (a line naming the hash)' % hk[0])
        d = 150000 if n in k3 else dt
        L.append('FrameTrace: n=%d dt_us=%d draws=500' % (n, d))
    for _ in range(vke):
        L.append('[Vulkan][E] validation error x')
    if death:
        L.append('Unhandled exception: access violation')
    L.append('Event: quit')
    with open(os.path.join(root, 'log_%s.txt' % tag), 'w', encoding='ascii', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    with open(os.path.join(root, 'stdout_%s.txt' % tag), 'w', encoding='ascii', newline='\n') as f:
        f.write('stdout\n')
    env = dict(KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0')
    if env_fix == 'same':
        env['KYTY_FIX_B26'] = fix
    elif env_fix is not None:
        env['KYTY_FIX_B26'] = env_fix
    if val:
        env['KYTY_PIPELINE_PRECACHE'] = '0'
        env['VK_LAYER_PATH'] = 'C:/VulkanSDK/1.4.357.0/Bin'
    if rec:
        env['KYTY_REC'] = 'C:\\kyty\\f287\\f2c\\rec_%s.mp4' % tag
    js = dict(attempts=[dict(label='attempt 1', hold_s=hold_s, outcome='ok', hold_exit=None)], env=env,
              guest_args='-lvl %s' % LV, cmdline=['kyty_emulator.exe', '--vulkan-validation', 'true' if val else 'false'],
              binary_sha256='5821482a')
    with open(os.path.join(root, '%s.json' % tag), 'w', encoding='ascii') as f:
        json.dump(js, f)
    if vframes is not None:
        with open(os.path.join(root, 'glitch_%s.txt' % tag), 'w', encoding='ascii') as f:
            f.write('rec_%s.mp4: %d frames 960x540\none-frame glitches: %d\n' % (tag, vframes, glitches))
    sp = os.path.join(root, 'sheet_%s.png' % tag)
    if sheet:
        open(sp, 'wb').write(b'PNG')
    elif os.path.exists(sp):
        os.remove(sp)


def rd(name, tag, **kw):
    root = os.path.join(FX, name)
    shutil.rmtree(root, ignore_errors=True)
    write_run(root, tag, **kw)
    return R.read_tag(tag, root, SC, B)


SC = R.load(R.SC142, R.SC142_SHA, 'sc142')
B = R.load(R.B26, R.B26_SHA, 'f2c_b26')
H5 = B.load_hashes()[1]

print('suite test_f2c_read.py sha256 %s target f2c_read.py sha256 %s' % (sha(os.path.abspath(__file__)),
                                                                      sha(os.path.join(HERE, 'f2c_read.py'))))
# --- (a) ---
r = rd('a_ok', 'f2c_a')
check('a ideal letter PASS', r['verdict_letter'] == 'PASS', r['verdict_letter'])
check('a ideal variant PASS', r['verdict_variant'] == 'PASS', r['verdict_variant'])
check('a ideal admitted', r['admitted'])
check('a ideal hold >= 300', r['hold_ok'] and r['dt_after_first_s'] >= 300, r['dt_after_first_s'])
check('a ideal b26 letter 5', r['b26']['letter5'] == 5)
check('a ideal hold frames 0', r['hold_frames'] == [], r['hold_frames'])
check('a ideal knob lines 0', sum(r['knob_lines'].values()) == 0)
r = rd('a_k3', 'f2c_a', k3=(1000, 5000), hash_in_k3=(5000,))
hf = r['hold_frames']
check('a k3 two hold frames', len(hf) == 2, hf)
check('a k3 frame 1000 no hash', hf[0]['n'] == 1000 and hf[0]['hash_lines'] == 0, hf[0])
check('a k3 frame 5000 hash in interval', hf[1]['n'] == 5000 and hf[1]['hash_lines'] == 1, hf[1])
check('a k3 is data, verdict PASS', r['verdict_letter'] == 'PASS', r['verdict_letter'])
r = rd('a_win', 'f2c_a', k3=(300,))
check('a k3 inside the entry window not a hold frame', r['hold_frames'] == [], r['hold_frames'])
r = rd('a_edge_win', 'f2c_a', k3=(601,))
check('a first hold row (index 599 after first) is a hold frame', len(r['hold_frames']) == 1 and r['hold_frames'][0]['n'] == 601,
      r['hold_frames'])
r = rd('a_edge_win2', 'f2c_a', k3=(600,))
check('a last window row (index 598) is not a hold frame', r['hold_frames'] == [], r['hold_frames'])
r = rd('a_short', 'f2c_a', rows=17990)
check('a hold 299.8 s NOT EVALUABLE (p.256(d))', r['verdict_letter'] == 'NOT EVALUABLE' and r['verdict_variant'] == 'NOT EVALUABLE' and not r['hold_ok'], r['dt_after_first_s'])
r = rd('a_short_death', 'f2c_a', rows=17990, death=True)
check('a hold 299.8 s with a death marker FAIL', r['verdict_variant'] == 'FAIL', r['verdict_variant'])
r = rd('a_short_e3', 'f2c_a', rows=17990, ops={('SOP1', '0x21'): 96, ('VOPC', '0xe3'): 1})
check('a hold 299.8 s with 0xe3 left FAIL', r['verdict_variant'] == 'FAIL', r['verdict_variant'])
r = rd('a_edge_hold', 'f2c_a', rows=18000, dt=16667)
check('a hold 300.006 s PASS', r['hold_ok'] and r['verdict_letter'] == 'PASS', r['dt_after_first_s'])
r = rd('a_death', 'f2c_a', death=True)
check('a death marker FAIL', r['verdict_letter'] == 'FAIL' and r['deaths'] == 1, r['deaths'])
r = rd('a_glitch', 'f2c_a', glitches=1)
check('a glitch 1 FAIL', r['verdict_letter'] == 'FAIL' and r['video_ok'] is False)
r = rd('a_vf', 'f2c_a', vframes=2999)
check('a video 2999 frames FAIL', r['verdict_letter'] == 'FAIL')
r = rd('a_vf3000', 'f2c_a', vframes=3000)
check('a video 3000 frames PASS', r['verdict_letter'] == 'PASS')
r = rd('a_noglitch', 'f2c_a', vframes=None)
check('a no glitch file FAIL', r['verdict_letter'] == 'FAIL')
r = rd('a_nosheet', 'f2c_a', sheet=False)
check('a no sheet FAIL', r['verdict_letter'] == 'FAIL')
r = rd('a_noenv', 'f2c_a', env_fix=None)
check('a KYTY_FIX_B26 unset NOT ADMITTED', r['verdict_letter'] == 'NOT ADMITTED')
r = rd('a_env2', 'f2c_a', env_fix='2')
check('a KYTY_FIX_B26=2 NOT ADMITTED (RC6)', r['verdict_letter'] == 'NOT ADMITTED')
r = rd('a_norec', 'f2c_a', rec=False)
check('a no KYTY_REC NOT ADMITTED', r['verdict_letter'] == 'NOT ADMITTED')
r = rd('a_knob', 'f2c_a', knob_lines=2)
check('a knob print lines counted', r['knob_lines'] == {'RbCen': 2}, r['knob_lines'])
r = rd('a_e3', 'f2c_a', ops={('SOP1', '0x21'): 96, ('VOPC', '0xe3'): 1})
check('a VOPC 0xe3 left FAIL', r['verdict_letter'] == 'FAIL')
r = rd('a_0c', 'f2c_a', ops={('SOP1', '0x21'): 96, ('SOP1', '0x0c'): 1})
check('a SOP1 0x0c left FAIL', r['verdict_letter'] == 'FAIL')
r = rd('a_95', 'f2c_a', ops={('SOP1', '0x21'): 95})
check('a SOP1 0x21 95 FAIL', r['verdict_letter'] == 'FAIL')
r = rd('a_noready', 'f2c_a', ready=False)
check('a no 5-hash lines FAIL (not counted)', r['verdict_letter'] == 'FAIL' and r['b26']['letter5'] == 0)
r = rd('a_knob0', 'f2c_a', fix='0', env_fix='1')
check('a cache line root while env 1 -> FAIL (knob invalid)', r['verdict_letter'] == 'FAIL', r['b26']['verdict_letter'])
r = rd('a_noprecache', 'f2c_a', precache=False)
check('a V without precache line FAIL (form)', r['verdict_letter'] == 'FAIL')
# --- (b) ---
kb = dict(val=True, precache=False, rec=False, vframes=None, sheet=False, hold_s=310.0)
r = rd('b_ok', 'f2c_b', **kb)
check('b ideal PASS letter', r['verdict_letter'] == 'PASS', r['verdict_letter'])
check('b ideal PASS variant', r['verdict_variant'] == 'PASS', r['verdict_variant'])
r = rd('b_vke', 'f2c_b', vke=1, **kb)
check('b [Vulkan][E] 1 FAIL', r['verdict_letter'] == 'FAIL' and r['vke'] == 1)
kb2 = dict(kb)
kb2['precache'] = True
r = rd('b_precache', 'f2c_b', **kb2)
check('b precache line FAIL (form p.254(e))', r['verdict_letter'] == 'FAIL')
r = rd('b_noval', 'f2c_b', noval=True, **kb)
check('b no validation layer NOT ADMITTED', r['verdict_letter'] == 'NOT ADMITTED')
kb3 = dict(kb)
kb3['val'] = False
r = rd('b_inactive', 'f2c_b', **kb3)
check('b validation not on cmdline NOT ADMITTED', r['verdict_letter'] == 'NOT ADMITTED')
kb4 = dict(kb)
kb4['hold_s'] = 299.0
r = rd('b_hold', 'f2c_b', **kb4)
check('b json hold 299 letter NOT EVALUABLE, variant PASS', r['verdict_letter'] == 'NOT EVALUABLE' and r['verdict_variant'] == 'PASS',
      (r['verdict_letter'], r['verdict_variant']))
kb5 = dict(kb)
kb5['hold_s'] = 300.0
r = rd('b_hold300', 'f2c_b', rows=17000, **kb5)
check('b json hold 300 letter PASS, dt 283 s variant NOT EVALUABLE', r['verdict_letter'] == 'PASS' and r['verdict_variant'] == 'NOT EVALUABLE',
      (r['verdict_letter'], r['verdict_variant']))
r = rd('b_video', 'f2c_b', val=True, precache=False, rec=True, vframes=None, sheet=False, hold_s=310.0)
check('b with KYTY_REC NOT ADMITTED', r['verdict_letter'] == 'NOT ADMITTED')
# --- (v) ---
kc = dict(fix='0', rec=False, vframes=None, sheet=False, hold_s=130.0, rows=7300)
r = rd('c_ok', 'f2c_c', **kc)
check('c ideal PASS', r['verdict_letter'] == 'PASS' and r['b26']['verdict_letter'] == 'CONTROL RETURNS', r['verdict_letter'])
r = rd('c_f3', 'f2c_c', ops={('SOP1', '0x21'): 96, ('SOP1', '0x0c'): 1, ('VOPC', '0xe3'): 4, ('VOPC', '0xf3'): 1},
       **kc)
check('c VOPC 0xf3 at =0 FAIL', r['verdict_letter'] == 'FAIL')
r = rd('c_e3', 'f2c_c', ops={('SOP1', '0x21'): 96, ('SOP1', '0x0c'): 1, ('VOPC', '0xe3'): 3}, **kc)
check('c VOPC 0xe3 3 FAIL', r['verdict_letter'] == 'FAIL')
kc2 = dict(kc)
kc2['hold_s'] = 119.0
r = rd('c_hold', 'f2c_c', **kc2)
check('c json hold 119 FAIL', r['verdict_letter'] == 'FAIL')
kc3 = dict(kc)
kc3['rows'] = 7000
r = rd('c_short', 'f2c_c', **kc3)
check('c dt after entry 118.1 s FAIL', r['verdict_letter'] == 'FAIL', r['dt_after_entry_s'])
r = rd('c_env', 'f2c_c', fix='0', env_fix='1', rec=False, vframes=None, sheet=False, hold_s=130.0, rows=7300)
check('c env KYTY_FIX_B26=1 NOT ADMITTED', r['verdict_letter'] == 'NOT ADMITTED')
r = rd('c_death', 'f2c_c', death=True, **kc)
check('c death marker FAIL', r['verdict_letter'] == 'FAIL')
# --- reopen B26a ---
root = os.path.join(FX, 'a_reopen')
shutil.rmtree(root, ignore_errors=True)
write_run(root, 'f2c_a')
h96 = sorted(B.load_hashes()[0])[0]
with open(os.path.join(root, 'log_f2c_a.txt'), 'a', encoding='ascii', newline='\n') as f:
    f.write('CsPretranslate: miss hash=%s\n' % h96)
r = R.read_tag('f2c_a', root, SC, B)
check('a B26a reopen (miss of the 96) FAIL', r['verdict_letter'] == 'FAIL' and r['b26']['reopen_any'])
# --- missing files ---
check('no json -> None', R.read_tag('f2c_a', os.path.join(FX, 'nothing'), SC, B) is None)
# --- seal ---
sd = os.path.join(FX, 'seal')
shutil.rmtree(sd, ignore_errors=True)
os.makedirs(sd)
for n in ('x.py', 'y.txt'):
    open(os.path.join(sd, n), 'w').write(n)
good = 'seal: %s x.py\nseal: %s y.txt\n' % (sha(os.path.join(sd, 'x.py')), sha(os.path.join(sd, 'y.txt')))
open(os.path.join(sd, 'p.md'), 'w').write('# p\n' + good)
check('seal ok', R.check_seal(os.path.join(sd, 'p.md'), sd, ('x.py', 'y.txt'))[0])
open(os.path.join(sd, 'p2.md'), 'w').write(good.replace(sha(os.path.join(sd, 'x.py'))[:4], '0000', 1))
check('seal mismatch refused', not R.check_seal(os.path.join(sd, 'p2.md'), sd, ('x.py', 'y.txt'))[0])
check('seal missing name refused', not R.check_seal(os.path.join(sd, 'p.md'), sd, ('x.py', 'y.txt', 'z.py'))[0])
open(os.path.join(sd, 'p3.md'), 'w').write(good + good.split('\n')[0] + '\n')
check('seal duplicate line refused', not R.check_seal(os.path.join(sd, 'p3.md'), sd, ('x.py', 'y.txt'))[0])
check('seal no file refused', not R.check_seal(os.path.join(sd, 'none.md'), sd, ('x.py',))[0])
# --- sha guard of the imported scorers ---
try:
    R.load(R.SC142, '0' * 64, 'sc142x')
    check('sc142 sha mismatch refused', False)
except SystemExit:
    check('sc142 sha mismatch refused', True)
# --- real s142 logs ---
if os.path.isfile(os.path.join(REAL, 'log_f2c_c.txt')):
    r = R.read_tag('f2c_c', REAL, SC, B)
    check('real v142 as (v): NOT ADMITTED (no KYTY_FIX_B26, has video)', r['verdict_letter'] == 'NOT ADMITTED')
    check('real v142 as (v): CONTROL RETURNS 96/1/4', r['b26']['verdict_letter'] == 'CONTROL RETURNS')
    check('real v142: entered, hold >= 300 s after first', r['entered'] and r['dt_after_first_s'] >= 300, r['dt_after_first_s'])
    check('real v142: knob lines 0', sum(r['knob_lines'].values()) == 0)
    check('real v142: deaths 0', r['deaths'] == 0)
    check('real v142: video 10567 frames 0 glitches', r['glitch'] == dict(video_frames=10567, glitches=0), r['glitch'])
    check('real v142: hold frames >= 100 ms 0 (v142 base)', r['hold_frames'] == [], r['hold_frames'])
    r = R.read_tag('f2c_b', REAL, SC, B)
    check('real w142 as (b): validation active', r['val']['ok'], r['val'])
    check('real w142 as (b): [Vulkan][E] 0', r['vke'] == 0)
    check('real w142 as (b): FAIL by form (precache line present) / NOT ADMITTED', r['verdict_letter'] in ('FAIL', 'NOT ADMITTED'))
    check('real w142 as (b): b26 form FAIL', r['b26']['form_ok'] is False)
else:
    check('real logs present (fx/real hard links)', False)
# --- strict cp1250 console, no PYTHONIOENCODING ---
env = dict(os.environ)
env.pop('PYTHONIOENCODING', None)
env['PYTHONUTF8'] = '0'
p = subprocess.run([sys.executable, '-X', 'utf8=0', '-c',
                    'import sys,io;sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="cp1250",errors="strict");'
                    'sys.path.insert(0,r"%s");import f2c_read as R;sys.argv=["f2c_read.py","--tag","f2c_a","--root",r"%s"];'
                    'sys.exit(R.main())' % (HERE, os.path.join(FX, 'a_k3'))], capture_output=True, env=env)
check('cp1250 strict output rc 0', p.returncode == 0, p.stderr[-300:])
check('cp1250 output ASCII', all(c < 128 for c in p.stdout), '')
p = subprocess.run([sys.executable, os.path.join(HERE, 'f2c_read.py')], capture_output=True, env=env)
check('usage rc 2', p.returncode == 2)
print('checks %d failed %d' % (N[0], len(FAIL)))
print('ALL OK' if not FAIL else 'SOME FAILED: %s' % FAIL)
sys.exit(0 if not FAIL else 1)

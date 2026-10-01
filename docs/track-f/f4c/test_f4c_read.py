"""test_f4c_read.py - fixtures of f4c_read.py (F4c, HPP-337): every member of the reading and every edge; ASCII output;
the last line is 'ALL OK' only when every check passed.
  python test_f4c_read.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f4c_read as R  # noqa: E402

SC = R.load(R.SC142, R.SC142_SHA, 'sc142')
BASE0 = dict(log_sha='0' * 64, kinds=[], k2=0, dt_after_first_s=121.8, first=(1, 1, 1))
N = [0]
FAILS = []


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def check(name, cond, detail=''):
    N[0] += 1
    if not cond:
        FAILS.append(name)
    print('%s %s%s' % ('ok  ' if cond else 'FAIL', name, (' [%s]' % (str(detail),)) if detail and not cond else ''))


def rows(n0, count, dt, draws=300):
    return ['FrameTrace: n=%d dt_us=%d lat_us=1 draws=%d dispatches=1' % (n0 + i, dt, draws) for i in range(count)]


def mk(d, tag, level, *, fix='1', val=True, dual=((1, 1),), dual_after=False, pre_n=(5,), stale=False, noyet=False,
       entered=True, hold_rows=3300, hold_dt=100000, vke=None, vke_after=False, death=None, hold_s=320.0, env_extra=None,
       env_drop=(), rec=False, count=5, flagged=True, recipes=True, scene_change=False, k2=False, glitch=None, sheet=False,
       valact=True, b26=None, guest_args=None):
    L = []
    if val and valact:
        L.append('VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features, version = 2')
        L.append('[Vulkan][I] layer up')
    if not dual_after:
        for s, e in dual:
            L.append('DualSrcBlend: supported=%d enabled=%d' % (s, e))
    if stale:
        L.append('PipelinePrecache: stale recipes (signature mismatch), ignored')
    if noyet:
        L.append('PipelinePrecache: no _ShaderCache\\PPSA21564\\variant_fixb26\\pipelines.bin yet')
    if vke and not vke_after:
        L.append('--- Error ---')
        L.append('[Vulkan][E][2]: ' + vke)
    for n in pre_n:
        L.append('PipelinePrecache: %d recipes -> 4 graphics + 1 compute pipelines queued, complete, 1 ms' % n)
    if not (vke and not vke_after):
        L.append('GuestOut: Level has started: ')
        if dual_after:
            for s, e in dual:
                L.append('DualSrcBlend: supported=%d enabled=%d' % (s, e))
        if vke and vke_after:
            L.append('--- Error ---')
            L.append('[Vulkan][E][2]: ' + vke)
        L += rows(1, 50, 16667, draws=10)
        if entered:
            L.append('GuestOut: Level has started: %s' % level)
            L += rows(100, 5, 16667, draws=10)
            L += rows(105, 1, 20000, draws=300)
            if k2:
                L += rows(106, 700, 16667)
                L += rows(806, 1, 1500000)
                L += rows(807, hold_rows, hold_dt)
            else:
                L += rows(106, hold_rows, hold_dt)
            if scene_change:
                L.append('GuestOut: Level has started: other_level')
                L += rows(9000, 3, 16667)
        if death:
            L.append(death)
    L.append('Event: quit')
    open(os.path.join(d, 'log_%s.txt' % tag), 'w', newline='\n').write('\n'.join(L) + '\n')
    open(os.path.join(d, 'stdout_%s.txt' % tag), 'w', newline='\n').write('stdout\n')
    env = dict(KYTY_FRAME_TRACE='lite', KYTY_GUEST_ARGS='-lvl %s' % level, KYTY_FIX_DUALSRC=fix, KYTY_GPU_CLOCK_PIN='1',
               KYTY_GPU_MARKERS='0')
    if val:
        env['VK_LAYER_PATH'] = 'C:/VulkanSDK/1.4.357.0/Bin'
    if rec:
        env['KYTY_REC'] = os.path.join(d, 'rec_%s.mp4' % tag)
    if b26 is not None:
        env['KYTY_FIX_B26'] = b26
    env.update(env_extra or {})
    for k in env_drop:
        env.pop(k, None)
    js = dict(tag=tag, binary_sha256='34d293ad' + '0' * 56, guest_args=guest_args or '-lvl %s' % level, env=env,
              cmdline=['kyty_emulator.exe', '--vulkan-validation', 'true' if val else 'false'],
              attempts=[dict(outcome='ok' if entered else 'exited', hold_s=hold_s if entered else None, hold_exit=None)])
    json.dump(js, open(os.path.join(d, '%s.json' % tag), 'w'))
    if recipes:
        os.makedirs(os.path.join(d, 'runs'), exist_ok=True)
        fl = [dict(index=3, srcblend=[17, 0], destblend=[18, 0])] if flagged else []
        json.dump(dict(cur=dict(count=count, sha256='ab' * 32, at_end=True, signature='KytySC3:699c', flagged=fl)),
                  open(os.path.join(d, 'runs', 'recipes_%s.json' % tag), 'w'))
    if glitch is not None:
        open(os.path.join(d, 'glitch_%s.txt' % tag), 'w').write(
            'rec_%s.mp4: %d frames 960x540, index entries %d\none-frame glitches: %d\n' % (tag, glitch[0], glitch[0], glitch[1]))
    if sheet:
        open(os.path.join(d, 'sheet_%s.png' % tag), 'wb').write(b'\x89PNG....')


STOPTXT = R.STOP_TEXT.decode() + '.'


def run(tag, **kw):
    d = tempfile.mkdtemp(prefix='f4c_')
    try:
        mk(d, tag, R.TAGS[tag]['level'], **kw)
        return R.read_tag(tag, d, sc142=SC, base=BASE0)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def V(r):
    return r['verdict_letter'], r['exec_ok']


def main():
    print('suite test_f4c_read.py sha256 %s target f4c_read.py sha256 %s' % (sha(os.path.abspath(__file__)),
                                                                            sha(os.path.join(HERE, 'f4c_read.py'))))
    # --- (a) ---
    r = run('f4c_a')
    check('a pass, executor members ok', V(r) == ('PASS', True), V(r))
    check('a text ascii', all(ord(c) < 128 for c in R.text(r)))
    check('a text names executor members apart from the verdict', 'F4C EXECUTOR MEMBERS f4c_a [I] (p.258(d), not the verdict): all ok' in R.text(r)
          and 'F4C VERDICT f4c_a letter: PASS' in R.text(r))
    check('a two dual lines', V(run('f4c_a', dual=((1, 1), (1, 1))))[0] == 'FAIL')
    check('a dual enabled=0', V(run('f4c_a', dual=((1, 0),)))[0] == 'FAIL')
    check('a dual supported=0', V(run('f4c_a', dual=((0, 0),)))[0] == 'FAIL')
    check('a no dual line', V(run('f4c_a', dual=()))[0] == 'FAIL')
    check('a dual after GuestOut -> letter PASS, executor member FAIL', V(run('f4c_a', dual_after=True)) == ('PASS', False))
    check('a stale line -> executor member FAIL only', V(run('f4c_a', stale=True)) == ('PASS', False))
    check('a noyet line -> executor member FAIL only', V(run('f4c_a', noyet=True)) == ('PASS', False))
    check('a precache N != count -> executor member FAIL only', V(run('f4c_a', count=6)) == ('PASS', False))
    check('a no precache line -> executor member FAIL only', V(run('f4c_a', pre_n=())) == ('PASS', False))
    check('a two precache lines -> executor member FAIL only', V(run('f4c_a', pre_n=(5, 5))) == ('PASS', False))
    check('a no dual record -> executor member FAIL only', V(run('f4c_a', flagged=False)) == ('PASS', False))
    check('a vke in game', V(run('f4c_a', vke='VUID-vkCmdDraw-maxFragmentDualSrcAttachments-09239', vke_after=True))[0] == 'FAIL')
    check('a death marker', V(run('f4c_a', death='Unhandled exception: x'))[0] == 'FAIL')
    check('a not entered', V(run('f4c_a', entered=False))[0] == 'FAIL')
    check('a scene change', V(run('f4c_a', scene_change=True))[0] == 'FAIL')
    r = run('f4c_a', hold_s=309.9)
    check('a json hold 309.9 -> letter FAIL, executor members ok', V(r) == ('FAIL', True), V(r))
    r = run('f4c_a', hold_s=310.0)
    check('a json hold 310.0 edge -> PASS', V(r)[0] == 'PASS', V(r))
    r = run('f4c_a', hold_rows=3099)
    check('a sum dt 309.9 s -> letter PASS, executor member FAIL', V(r) == ('PASS', False), (V(r), r['dt_after_first_s']))
    r = run('f4c_a', hold_rows=3100)
    check('a sum dt 310.0 s edge -> executor member ok', V(r) == ('PASS', True), (V(r), r['dt_after_first_s']))
    check('a validation not active', V(run('f4c_a', valact=False))[0] == 'NOT ADMITTED')
    check('a precache env set', V(run('f4c_a', env_extra=dict(KYTY_PIPELINE_PRECACHE='0')))[0] == 'NOT ADMITTED')
    check('a fix env 0', V(run('f4c_a', fix='0', dual=((1, 0),)))[0] == 'NOT ADMITTED')
    check('a fix env absent', V(run('f4c_a', env_drop=('KYTY_FIX_DUALSRC',)))[0] == 'NOT ADMITTED')
    check('a fix env "true" (not exactly 1)', V(run('f4c_a', env_extra=dict(KYTY_FIX_DUALSRC='true')))[0] == 'NOT ADMITTED')
    check('a KYTY_FIX_B26 set while FIXB26 None', V(run('f4c_a', b26='0'))[0] == 'NOT ADMITTED')
    check('a checkpoints env', V(run('f4c_a', env_extra=dict(KYTY_GPU_CHECKPOINTS='0')))[0] == 'NOT ADMITTED')
    check('a clock pin absent', V(run('f4c_a', env_drop=('KYTY_GPU_CLOCK_PIN',)))[0] == 'NOT ADMITTED')
    check('a video set', V(run('f4c_a', rec=True))[0] == 'NOT ADMITTED')
    check('a recipes json missing', V(run('f4c_a', recipes=False))[0] == 'NOT ADMITTED')
    check('a guest args other level', V(run('f4c_a', guest_args='-lvl mini_giants_garden'))[0] == 'NOT ADMITTED')
    check('a vulkan-validation false', V(run('f4c_a', val=False))[0] == 'NOT ADMITTED')
    old = R.FIXB26
    try:
        R.FIXB26 = '0'
        check('a FIXB26=0 configured and passed', V(run('f4c_a', b26='0'))[0] == 'PASS')
        check('a FIXB26=0 configured, absent', V(run('f4c_a'))[0] == 'NOT ADMITTED')
    finally:
        R.FIXB26 = old
    # --- (b) ---
    r = run('f4c_b', fix='0', dual=((1, 0),), vke=STOPTXT, pre_n=(), entered=False)
    check('b stop same text', V(r) == ('STOP SAME TEXT', True), V(r))
    check('b stop -> continue', R.stop_check(json.loads(json.dumps(r, default=str))).startswith('continue'))
    r = run('f4c_b', fix='0', dual=((1, 0),), pre_n=(5,), entered=True)
    check('b no stop', V(r)[0] == 'NO STOP', V(r))
    check('b no stop -> series stop', R.stop_check(json.loads(json.dumps(r, default=str))).startswith('stop'))
    r = run('f4c_b', fix='0', dual=((1, 0),), vke='some other validation error', pre_n=(), entered=False)
    check('b other text', V(r)[0] == 'NO STOP', V(r))
    r = run('f4c_b', fix='0', dual=((1, 0),), vke=STOPTXT, vke_after=True, pre_n=(), entered=False)
    check('b same text after GuestOut', V(r)[0] == 'NO STOP', V(r))
    r = run('f4c_b', fix='0', dual=((1, 0),), vke=STOPTXT, pre_n=(), entered=False, stale=True)
    check('b stale line -> executor member FAIL only', V(r) == ('STOP SAME TEXT', False), V(r))
    r = run('f4c_b', fix='0', dual=((1, 0),), vke=STOPTXT, pre_n=(), entered=False, flagged=False)
    check('b no dual record -> executor member FAIL only', V(r) == ('STOP SAME TEXT', False), V(r))
    r = run('f4c_b', fix='0', dual=((1, 1),), vke=STOPTXT, pre_n=(), entered=False)
    check('b dual enabled=1 -> executor member FAIL only', V(r) == ('STOP SAME TEXT', False), V(r))
    r = run('f4c_b', fix='1', dual=((1, 1),), vke=STOPTXT, pre_n=(), entered=False)
    check('b env =1 -> NOT ADMITTED', V(r)[0] == 'NOT ADMITTED', V(r))
    r = run('f4c_b', fix='0', dual=((1, 0),), vke=STOPTXT, pre_n=(), entered=False, valact=False)
    check('b validation inactive -> NOT ADMITTED', V(r)[0] == 'NOT ADMITTED', V(r))
    check('b not admitted -> series stop', R.stop_check(json.loads(json.dumps(r, default=str))).startswith('stop'))
    # --- (v) ---
    r = run('f4c_v', flagged=False)
    check('v pass without a dual record (not required)', V(r) == ('PASS', True), V(r))
    r = run('f4c_v', vke='VUID-vkCmdDraw-maxFragmentDualSrcAttachments-09239', vke_after=True)
    check('v predicted 09239 -> FAIL', V(r)[0] == 'FAIL', V(r))
    rr = json.loads(json.dumps(r, default=str))
    check('v validation stop -> continue (data)', R.stop_check(rr).startswith('continue'), R.stop_check(rr))
    check('v other level -> NOT ADMITTED', V(run('f4c_v', guest_args='-lvl underwater_aerial_garden'))[0] == 'NOT ADMITTED')
    r = run('f4c_v', death='--- Fatal Error ---')
    check('v death not in the letter of (v) -> letter PASS, executor member FAIL', V(r) == ('PASS', False), V(r))
    check('v death without vke -> series stop', R.stop_check(json.loads(json.dumps(r, default=str))).startswith('stop'))
    # --- (g) ---
    G = dict(val=False, rec=True, glitch=(3500, 0), sheet=True, hold_rows=3400, hold_s=345.0, flagged=False)
    r = run('f4c_g', **G)
    check('g pass', V(r) == ('PASS', True), V(r))
    check('g pass -> continue', R.stop_check(json.loads(json.dumps(r, default=str))) == 'continue')
    check('g video 2999 frames', V(run('f4c_g', **dict(G, glitch=(2999, 0))))[0] == 'FAIL')
    check('g video 3000 frames edge', V(run('f4c_g', **dict(G, glitch=(3000, 0))))[0] == 'PASS')
    check('g glitch 1', V(run('f4c_g', **dict(G, glitch=(3500, 1))))[0] == 'FAIL')
    check('g no glitch file', V(run('f4c_g', **dict(G, glitch=None)))[0] == 'FAIL')
    check('g no sheet', V(run('f4c_g', **dict(G, sheet=False)))[0] == 'FAIL')
    r = run('f4c_g', **dict(G, k2=True))
    check('g K2 frame vs base 0 -> FAIL', V(r)[0] == 'FAIL' and r['new_k1k2']['new_k2'], V(r))
    r = run('f4c_g', **dict(G, death='GpuHangAbort: x'))
    check('g new K2 marker -> FAIL', V(r)[0] == 'FAIL' and r['new_k1k2']['kinds'], r.get('new_k1k2'))
    check('g death -> series stop', R.stop_check(json.loads(json.dumps(r, default=str))).startswith('stop'))
    r = run('f4c_g', **dict(G, hold_rows=3299))
    check('g sum dt 329.9 s -> FAIL', V(r)[0] == 'FAIL', (V(r), r['dt_after_first_s']))
    r = run('f4c_g', **dict(G, hold_rows=3300))
    check('g sum dt 330.0 s edge -> PASS', V(r)[0] == 'PASS', (V(r), r['dt_after_first_s']))
    check('g no KYTY_REC', V(run('f4c_g', **dict(G, rec=False)))[0] == 'NOT ADMITTED')
    check('g validation on', V(run('f4c_g', **dict(G, val=True)))[0] == 'NOT ADMITTED')
    check('g precache N mismatch -> executor member FAIL only', V(run('f4c_g', **dict(G, count=7))) == ('PASS', False))
    check('g stale -> executor member FAIL only', V(run('f4c_g', **dict(G, stale=True))) == ('PASS', False))
    # --- c142_04 base from the real log (sc142 functions) ---
    b = R.c14204(SC)
    check('c142_04 base: K2 0, kinds empty, first scene frame n 260',
          b['k2'] == 0 and b['kinds'] == [] and b['first'][0] == 260, b)
    check('c142_04 log sha bd5f5477', b['log_sha'].startswith('bd5f547706caad1d'), b['log_sha'])
    # --- real W stop of s143 with an injected DualSrcBlend line ---
    d = tempfile.mkdtemp(prefix='f4c_')
    try:
        src = open('C:/kyty/s143/log_w143_01.txt', 'rb').read()
        open(os.path.join(d, 'log_f4c_b.txt'), 'wb').write(b'DualSrcBlend: supported=1 enabled=0\n' + src)
        shutil.copy('C:/kyty/s143/stdout_w143_01.txt', os.path.join(d, 'stdout_f4c_b.txt'))
        js = json.load(open('C:/kyty/s143/w143_01.json'))
        js['guest_args'] = '-lvl %s' % R.SKY
        js['env'] = dict(js['env'], KYTY_FIX_DUALSRC='0')
        js['env'].pop('KYTY_FIX_B26', None)
        json.dump(js, open(os.path.join(d, 'f4c_b.json'), 'w'))
        os.makedirs(os.path.join(d, 'runs'))
        shutil.copy(os.path.join(HERE, 'recipes_f4c_before.json'), os.path.join(d, 'runs', 'recipes_f4c_b.json'))
        r = R.read_tag('f4c_b', d, sc142=SC)
        check('real w143_01 stop (+dual line) -> STOP SAME TEXT', V(r)[0] == 'STOP SAME TEXT', (V(r), R.text(r)[-600:]))
        check('real recipe json: count 2457, 1 dual record', r['recipes']['count'] == 2457 and r['recipes']['dual'] == 1,
              r['recipes'])
        os.remove(os.path.join(d, 'log_f4c_b.txt'))
        shutil.copy('C:/kyty/s143/log_w143_01.txt', os.path.join(d, 'log_f4c_b.txt'))
        r = R.read_tag('f4c_b', d, sc142=SC)
        check('real w143_01 without the dual line (9235a7ac) -> letter STOP SAME TEXT, executor member FAIL', V(r) == ('STOP SAME TEXT', False), V(r))
    finally:
        shutil.rmtree(d, ignore_errors=True)
    # --- seal check ---
    d = tempfile.mkdtemp(prefix='f4c_')
    try:
        p = os.path.join(d, 'a.txt')
        open(p, 'w').write('x')
        good = 'seal: %s a.txt\n' % sha(p)
        open(os.path.join(d, 'pred.md'), 'w').write(good)
        ok, _ = R.check_seal(os.path.join(d, 'pred.md'), root=d, names=('a.txt',))
        check('seal ok', ok)
        open(p, 'w').write('y')
        ok, _ = R.check_seal(os.path.join(d, 'pred.md'), root=d, names=('a.txt',))
        check('seal mismatch', not ok)
        open(os.path.join(d, 'pred.md'), 'w').write(good + good)
        ok, _ = R.check_seal(os.path.join(d, 'pred.md'), root=d, names=('a.txt',))
        check('seal two lines of one name', not ok)
        ok, _ = R.check_seal(os.path.join(d, 'pred.md'), root=d, names=('a.txt', 'b.txt'))
        check('seal missing name', not ok)
        ok, _ = R.check_seal(os.path.join(d, 'nope.md'), root=d, names=('a.txt',))
        check('seal file missing', not ok)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    # --- cli in strict cp1250 without PYTHONIOENCODING ---
    env = {k: v for k, v in os.environ.items() if k != 'PYTHONIOENCODING'}
    env['PYTHONIOENCODING'] = 'cp1250:strict'
    p = subprocess.run([sys.executable, os.path.join(HERE, 'f4c_read.py'), '--c14204'], env=env, capture_output=True)
    check('cli --c14204 cp1250 strict rc 0', p.returncode == 0, p.stderr[-300:])
    p = subprocess.run([sys.executable, os.path.join(HERE, 'f4c_read.py'), '--tag', 'nope'], env=env, capture_output=True)
    check('cli bad tag rc 2', p.returncode == 2)
    p = subprocess.run([sys.executable, os.path.join(HERE, 'f4c_read.py'), '--stop-check', 'C:/kyty/f287/f4c/none.json'],
                       env=env, capture_output=True)
    check('cli stop-check missing json -> stop', p.returncode == 0 and p.stdout.strip().startswith(b'stop'), p.stdout)
    p = subprocess.run([sys.executable, os.path.join(HERE, 'f4c_read.py'), '--tag', 'f4c_a', '--root', 'C:/kyty/f287/f4c/none'],
                       env=env, capture_output=True)
    check('cli no log rc 1', p.returncode == 1)
    print('checks %d failed %d %s' % (N[0], len(FAILS), FAILS))
    print('ALL OK' if not FAILS else 'SOME FAILED')
    return 0 if not FAILS else 1


if __name__ == '__main__':
    sys.exit(main())

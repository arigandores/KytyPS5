"""Track F link F47i (HPP-826): fixtures of read_f47i.py (every admission member of item 740 (v)(3), 742 (e), 744 (g)-(d) and its edge),
of the show table (held), of the launcher / chain refusals, and the strict cp1250 output of the reader.  The fixture log and video are
synthetic (the line forms of diagF47Dt.cpp F47g2 as in dt_f47g2.py fx_flips / fx_draw; the video by ffmpeg lavfi: grey frames with a
black / white band at the given records, libx264rgb lossless).  The admission member of item 742 (e) runs the REAL reader dt_f47g2.py
flips on the fixture log.  First output line: 'suite <name> sha256 <sha> target <name> sha256 <sha>'; last line ALL OK.  ASCII only.
usage: python test_f47i.py [--work DIR]"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import read_f47i as R  # noqa: E402

WORK = sys.argv[sys.argv.index('--work') + 1] if '--work' in sys.argv else os.path.join(HERE, 'fx')
DT = R.DT_READER
BASH = 'C:/Program Files/Git/bin/bash.exe'
N_LAST = 1300
N0 = 200
D = 5
WIN = '900-1250'
BLACK_REC = [(950, 954), (965, 969)]
WHITE_REC = [(957, 961)]
results = []


def check(name, cond, info=''):
    results.append((name, bool(cond)))
    print('%s %s%s' % ('OK  ' if cond else 'FAIL', name, (' - ' + info) if info else ''))


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def make_video(path, black=BLACK_REC, white=WHITE_REC):
    boxes = []
    for a, b in black:
        boxes.append("drawbox=x=0:y=0:w=480:h=81:color=black:t=fill:enable='between(n,%d,%d)'" % (a, b))
    for a, b in white:
        boxes.append("drawbox=x=0:y=0:w=480:h=81:color=white:t=fill:enable='between(n,%d,%d)'" % (a, b))
    vf = ','.join(boxes) if boxes else 'null'
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=gray:s=480x270:r=60', '-frames:v', str(N_LAST),
                    '-vf', vf, '-c:v', 'libx264rgb', '-qp', '0', '-preset', 'ultrafast', path], check=True)


def log_lines(h_black=(952,), h_white=(959,), held=(961,), stat_capped=0, death=False, win_event=False, shift=None, no_ft=False,
              mode_frames=None, n0=N0, win=WIN):
    mode_frames = win if mode_frames is None else mode_frames
    a, b = [int(x) for x in win.split('-')]
    out = ['[0][00:00:00.000] start', 'F47dt: mode=1 ps=45942b26d9ffbe8e frames=%s hash=xxh3_64 cap=2147483648 dir=_f47dt' % mode_frames,
           'Shader translation cache: C:/x/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10_fixf19']
    for n in range(1, N_LAST + 1):
        if n == n0:
            out.append('GuestOut: Level has started: underwater_aerial_garden')
        if a <= n <= b:
            rid = 5000 + n
            out.append('F47dt: kind=flip q=%d path=0 rid=%d n=%d' % (n, rid, n - 1))
            out.append('F47dt: kind=shown n=%d rid=%d' % (n + 1 if n == shift else n, rid))
            if n in held:
                out.append('AsyncPipelines: flip %d held (incomplete frame)' % rid)
            if n in h_black or n in h_white:
                out.append('F47dt: kind=draw q=%d n=%d d=3 gf=1 submit=1 draw=DrawIndex ps=45942b26d9ffbe8e vs=0000000000000001 idx=6 '
                           'inst=1 ready=1 images=0 buffers=0 samplers=0 ud=2:00000001,00000002' % (n, n - 1))
        if not no_ft:
            out.append('FrameTrace: n=%d dt_us=16667 lat_us=0' % n)
    if death:
        out.append('--- Fatal Error ---')
    if win_event:
        out.append('Window 1 minimized')
    out.append('F47dtStat: when=exit draws=2 frames=2 files=3 bytes=100 capped=%d imgs=0 bufs=0 pending=0 flips=301 ring_gpu_notes=0'
               % stat_capped)
    return out


def build(dirname, mp4_src, **kw):
    d = os.path.join(WORK, dirname)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    over = kw.pop('files', {})
    env_extra = kw.pop('env_extra', {})
    jbin = kw.pop('jbin', R.TB)
    win = kw.get('win', WIN)
    open(os.path.join(d, 'log.txt'), 'w', newline='\n').write('\n'.join(log_lines(**kw)) + '\n')
    open(os.path.join(d, 'stdout.txt'), 'w', newline='\n').write('stdout\n')
    open(os.path.join(d, 'seal.md'), 'w', newline='\n').write('seal\n')
    shutil.copyfile(mp4_src, os.path.join(d, 'rec.mp4'))
    with open(os.path.join(d, 'rec.idx'), 'w', newline='\n') as f:
        for r in range(N_LAST):
            f.write('%d %d\n' % (r, r + 1 + D))
    env = dict(KYTY_GUEST_ARGS='-lvl underwater_aerial_garden', KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE='g', KYTY_SAMPLE_GATE='s',
               KYTY_QUEUE_TRACE='1', KYTY_GPU_HANG_ABORT_S='8', KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_REC='r.mp4',
               KYTY_DIAG_F47DT='1', KYTY_DIAG_F47DT_FRAMES=win, KYTY_STREAM_TRACE='1')
    env.update(env_extra)
    es = dict(binary_sha256=jbin, prereg=dict(sha256=sha(os.path.join(d, 'seal.md'))), env=env,
              cmdline=['kyty_emulator.exe', '--vulkan-validation', 'false'], attempts=[dict(outcome='ok')],
              guest_args='-lvl underwater_aerial_garden', hold_s=120)
    json.dump(es, open(os.path.join(d, 'es.json'), 'w'))
    files = dict(installed_pre=R.INST + ' FS15', installed_before=R.INST, installed_after=R.INST, installed_sha=R.TB,
                 manifest_cmp='manifest cmp EQUAL files 10', level='underwater_aerial_garden', window=win, seal_window=win,
                 free_gib_before='100', f47dt_files='manifest f47dt files 3 bytes 100 listsha ' + '0' * 64)
    files.update(over)
    for k, v in files.items():
        if v is None:
            continue
        open(os.path.join(d, k + '.txt'), 'w', newline='\n').write(v + '\n')
    if 'flips' not in over:
        p = subprocess.run([sys.executable, DT, 'flips', os.path.join(d, 'log.txt'), '--window', win], capture_output=True, text=True)
        open(os.path.join(d, 'flips.txt'), 'w', newline='\n').write(p.stdout)
    return d


def read(d):
    return R.read_tag('f47_dt', R.paths('f47_dt', d), video=True)


def main():
    os.makedirs(WORK, exist_ok=True)
    print('suite test_f47i.py sha256 %s target read_f47i.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(R.__file__)))
    v_ok = os.path.join(WORK, 'v_ok.mp4')
    v_none = os.path.join(WORK, 'v_none.mp4')
    v_black = os.path.join(WORK, 'v_black.mp4')
    make_video(v_ok)
    make_video(v_none, black=[], white=[])
    make_video(v_black, white=[])
    # base
    r = read(build('ok', v_ok))
    check('F1 base ADMITTED', r['status'] == 'ADMITTED', '%s %s' % (r['status'], r['failed'][:3]))
    rw = r['rows']
    check('F2 black shows = records - d (951..955, 966..970)', rw['black_shows'] == list(range(951, 956)) + list(range(966, 971)),
          str(rw['black_shows'][:12]))
    check('F3 white shows 958..962', rw['white_shows'] == list(range(958, 963)), str(rw['white_shows']))
    check('F4 H in black [952], in white [959]', rw['h_in_black_shows'] == [952] and rw['h_in_white_shows'] == [959])
    st = dict((s['q'], s) for s in rw['show_table'])
    check('F5 held show 961 marked (item 744 (d)(2)), 960 not', st[961]['held'] is True and st[960]['held'] is False)
    check('F6 show table covers the window 900..1250', min(st) == 900 and max(st) == 1250 and len(st) == 351)
    out = R.rows_out(r)
    check('F7 SHOW row of 961 printed with held', any(l.startswith('  SHOW 961 ') and ' held ' in l for l in out))
    check('F8 reading line without a verdict word', out[-1].startswith('  READING ADMITTED (no verdict'))
    # members
    cases = [
        ('M1 no H in a white show', dict(h_white=()), 'NOT_ADMITTED'),
        ('M2 no H in a black show', dict(h_black=()), 'NOT_ADMITTED'),
        ('M3 F47dtStat capped=1', dict(stat_capped=1), 'NOT_ADMITTED'),
        ('M4 death marker', dict(death=True), 'NOT_ADMITTED'),
        ('M5 window event -> INTERFERENCE', dict(win_event=True), 'INTERFERENCE'),
        ('M6 shown n != q (item 742 (e)) -> flips ADMISSION FAIL = interference', dict(shift=1050), 'INTERFERENCE'),
        ('M7 RC2: ADMISSION OK with FrameTrace lines 0 = interference', dict(files=dict(flips='ADMISSION OK: flips 351 in [900, 1250], '
                                                                          'paths [0], shown lines 351, FrameTrace lines 0')), 'INTERFERENCE'),
        ('M8 env extra KYTY_FIX_B42', dict(env_extra=dict(KYTY_FIX_B42='1')), 'NOT_ADMITTED'),
        ('M9 env extra KYTY_GPU_CHECKPOINTS', dict(env_extra=dict(KYTY_GPU_CHECKPOINTS='1')), 'NOT_ADMITTED'),
        ('M10 json binary = FS15 (not the tag binary)', dict(jbin=R.INST), 'NOT_ADMITTED'),
        ('M11 installed after != FS15', dict(files=dict(installed_after=R.TB)), 'NOT_ADMITTED'),
        ('M12 caches not returned', dict(files=dict(manifest_cmp='manifest cmp DIFFER 1')), 'NOT_ADMITTED'),
        ('M13 free 39 GiB (edge 40)', dict(files=dict(free_gib_before='39')), 'NOT_ADMITTED'),
        ('M14 free 40 GiB (edge) admitted', dict(files=dict(free_gib_before='40')), 'ADMITTED'),
        ('M15 window of the call != seal', dict(files=dict(window='1000-1300')), 'NOT_ADMITTED'),
        ('M16 mode line frames != window', dict(mode_frames='1-2'), 'NOT_ADMITTED'),
        ('M17 no _f47dt manifest', dict(files=dict(f47dt_files=None)), 'NOT_ADMITTED'),
        ('M18 env FRAMES != window', dict(env_extra=dict(KYTY_DIAG_F47DT_FRAMES='1-2')), 'NOT_ADMITTED'),
        ('M19 installed tag binary != F47g2', dict(files=dict(installed_sha=R.INST)), 'NOT_ADMITTED'),
        ('M23 item 745: n0 100 outside [144; 483], series outside the window 1000-1250 -> window form interference',
         dict(n0=100, win='1000-1250'), 'INTERFERENCE'),
        ('M24 item 745: n0 200 inside [144; 483], series outside the window 1000-1250 -> NOT_ADMITTED', dict(win='1000-1250'),
         'NOT_ADMITTED'),
        ('M25 item 745 edge: n0 143 outside, series in the window -> ADMITTED', dict(n0=143), 'ADMITTED'),
        ('M26 item 745 edge: n0 144 inside, series outside the window 1000-1250 -> NOT_ADMITTED', dict(n0=144, win='1000-1250'),
         'NOT_ADMITTED'),
    ]
    for name, kw, want in cases:
        d = build('m%02d' % (cases.index((name, kw, want)) + 1), v_ok, **kw)
        r = read(d)
        check(name + ' -> ' + want, r['status'] == want, '%s %s' % (r['status'], [f[:60] for f in r['failed'][:2]]))
    wf = R.window_form
    W9 = (900, 1250)
    check('W1 window_form n0 483 inside, no series in window -> not interference', wf(483, [1300], [1310], W9)[0] is False)
    check('W2 window_form n0 484 outside, black missing -> interference', wf(484, [1300], [1000], W9)[0] is True)
    check('W3 window_form n0 484 outside, white missing -> interference', wf(484, [1000], [1300], W9)[0] is True)
    check('W4 window_form n0 484 outside, both in window -> not interference', wf(484, [1250], [900], W9)[0] is False)
    check('W5 window_form n0 143 outside, both missing -> interference', wf(143, [], [], W9)[0] is True)
    check('W6 window_form n0 None -> outside', wf(None, [1000], [], W9)[0] is True)
    check('W7 window_form edges 900 / 1250 counted in window', wf(500, [900], [1250], W9)[2] == dict(black=1, white=1))
    r = read(build('nob', v_none))
    check('M20 no blocks on the video -> NO_BLOCKS (item 708 (b)(9))', r['status'] == 'NO_BLOCKS', r['status'])
    r = read(build('nowhite', v_black))
    check('M21 black series without a white series -> NO_BLOCKS', r['status'] == 'NO_BLOCKS', r['status'])
    r = read(build('nob_death', v_none, death=True))
    check('M22 no blocks + another failed member -> NOT_ADMITTED', r['status'] == 'NOT_ADMITTED', r['status'])
    # strict cp1250 output of the reader (no PYTHONIOENCODING)
    env = dict(os.environ)
    env.pop('PYTHONIOENCODING', None)
    env['PYTHONIOENCODING'] = 'cp1250:strict'
    p = subprocess.run([sys.executable, os.path.join(HERE, 'read_f47i.py'), '--dir', os.path.join(WORK, 'ok'), '--tag', 'f47_dt', '--video'],
                       capture_output=True, env=env)
    check('C1 reader output in strict cp1250, rc 0, ASCII', p.returncode == 0 and all(c < 128 for c in p.stdout), 'rc %d' % p.returncode)
    # chain refusals (no game, no lock)
    g = os.path.join(HERE, 'go_f47i.sh')
    lch = os.path.join(HERE, 'launch_f47i.sh')
    p = subprocess.run([BASH, g, 'bad'], capture_output=True, text=True)
    check('C2 go usage rc 2', p.returncode == 2, p.stdout.strip()[-60:])
    p = subprocess.run([BASH, lch, 'f47_dt_r1'], capture_output=True, text=True, env=dict(os.environ, F47I_DISP_SKIP='1',
                                                                                          F47I_QUEUE_SKIP='1'))
    check('C3 launch repeat without the lead item rc 11', p.returncode == 11, p.stdout.strip()[-80:])
    p = subprocess.run([BASH, lch, 'bad'], capture_output=True, text=True)
    check('C4 launch usage rc 2', p.returncode == 2)
    if not os.path.exists(os.path.join(HERE, 'pred', 'window.txt')):
        p = subprocess.run([BASH, g, 'f47_dt'], capture_output=True, text=True)
        check('C5 go without pred/window.txt refuses rc 1', p.returncode == 1 and 'window' in p.stdout, p.stdout.strip()[-80:])
    else:
        p = subprocess.run([BASH, g, 'f47_dt'], capture_output=True, text=True, env=dict(os.environ, F47I_DRYRUN='1'))
        check('C5 go dryrun with the sealed window prints the knobs', p.returncode == 0 and 'KYTY_DIAG_F47DT_FRAMES=' in p.stdout,
              p.stdout.strip()[-120:])
    bad = [n for n, ok in results if not ok]
    print('checks %d failed %d' % (len(results), len(bad)))
    if not bad:
        print('ALL OK')
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())

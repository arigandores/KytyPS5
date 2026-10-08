"""F27c (HPP-694): fixtures of f27c_read.py - every member P1-P6 and every edge of the seal section 4, the restatement of savewin_f27a's
overlap rule against savewin_f27a.out.txt on the reference log ednn122 (positive control), the import sha refusal, the series states of
item 631 (v)(3), (d)(1), (d)(3) as amended by item 636 (b)-(g) (seal 3), and the output in strict cp1250.  The set ends with ALL OK.  ASCII only.
usage: python test_f27c_read.py [--no-ref]"""
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f27c_read as R  # noqa: E402

N = 0
BAD = 0


def check(name, cond, extra=''):
    global N, BAD
    N += 1
    if not cond:
        BAD += 1
    print('%s %s %s' % ('ok  ' if cond else 'FAIL', name, extra))


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def ts(t):
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return '[23][%02d:%02d:%06.3f] libkernel' % (h, m, s)


HOLD_FROM = datetime.datetime(2026, 10, 8, 23, 0, 30, 0)
NS = 10
T_S = 30.0   # log time of the stable frame


def make(root, tag, frames, saves, extra_lines=(), hold_s=120.0, pcw=None, ns=None, loaded=None, salt=None, p5='labels EQUAL x',
         interference=False, csv_rows=None, precache=False):
    """frames: [(n, dt_us, t)]; saves: [(t, after_n, bytes, us)] - the save line comes right after the frame after_n."""
    os.makedirs(os.path.join(root, 'runs', tag), exist_ok=True)
    arm = 0 if tag.startswith('f27_v0') else 1
    lines = ['S-pcw: KYTY_S_PCW=%d KYTY_S_PCW_FORCE_MS=0' % (arm if pcw is None else pcw)] if pcw != -1 else []
    import f27c_tools as TT
    hname = TT.salt_name(tag)
    lines.append('Pipeline cold-test namespace: %s' % (tag if ns is None else ns))
    lines.append('Vulkan pipeline cache: loaded %d bytes from _PipelineCache\\%s' % (127690297 if loaded is None else loaded, hname))
    if precache:
        lines.append('PipelinePrecache: saved 10 recipes (100 bytes)')
    lines += list(extra_lines)
    for n, dt, t in frames:
        lines.append(ts(t))
        lines.append('FrameTrace: n=%d dt_us=%d draws=900' % (n, dt))
        for st, after, nb, us in saves:
            if after == n:
                lines.append(ts(st))
                lines.append('Vulkan pipeline cache: saved %d bytes to _PipelineCache\\%s (%d us)' % (nb, hname, us))
    with open(os.path.join(root, 'log_%s.txt' % tag), 'w', encoding='ascii', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    hold_to = HOLD_FROM + datetime.timedelta(seconds=hold_s)
    j = dict(binary_sha256='abfded5e' + '0' * 56, attempts=[dict(outcome='ok', stable_frame=NS, hold_s=hold_s,
             hold_from=HOLD_FROM.strftime(R.STAMP)[:-3], hold_to=hold_to.strftime(R.STAMP)[:-3], hold_exit=None, close_rc=0)])
    json.dump(j, open(os.path.join(root, tag + '.json'), 'w'))
    s = salt or dict(salt=tag, name=hname, size='127690373', payload='127690297')
    with open(os.path.join(root, 'runs', tag, 'salt.txt'), 'w', encoding='ascii') as f:
        f.write('salt %s name %s size %s sha_src a sha_copy a blob size %s header 76 payload %s sha256 a\n' % (
            s['salt'], s['name'], s['size'], s['size'], s['payload']))
    with open(os.path.join(root, 'runs', tag, 'p5.txt'), 'w', encoding='ascii') as f:
        f.write(p5 + '\n')
    if interference:
        open(os.path.join(root, 'runs', tag, 'INTERFERENCE_P5'), 'w').write('x\n')
    if csv_rows is None:
        csv_rows = [(HOLD_FROM + datetime.timedelta(seconds=-40 + 0.5 * i), 80) for i in range(int((hold_s + 60) / 0.5))]
    with open(os.path.join(root, 'gpuclk_%s.csv' % tag), 'w', encoding='ascii') as f:
        f.write('timestamp, clocks.current.sm [MHz], clocks.current.memory [MHz], utilization.gpu [%], power.draw [W]\n')
        for t, u in csv_rows:
            f.write('%s, 1900 MHz, 14001 MHz, %d %%, 100 W\n' % (t.strftime(R.STAMP)[:-3], u))


def base_frames(dt_at=None, last=200):
    """frames 1..last, 0.5 s apart from log time 25.0 (frame 10 at 29.5 ... no: frame n at 25.0 + 0.5 (n - 1)); frame 11 at 30.0."""
    out = []
    for n in range(1, last + 1):
        t = 25.0 + 0.5 * (n - 1)
        out.append((n, (dt_at or {}).get(n, 16000), t))
    return out


def run_reader(root, tag):
    return R.read_tag(tag, root)


def main(argv):
    tmp = tempfile.mkdtemp(prefix='f27c_fx_')
    try:
        # stable frame 10 is at log 29.5 -> t_s = 29.5, hold [29.5, 149.5]; frame n at 25 + 0.5 (n - 1)
        # 1) base v0: a save on the hold, window [60.0 - 0.120, 60.0] after frame 71 (t 60.0); frame 72 (t 60.5) spans [60.0, 60.5] -> on
        fr = base_frames({72: 120000, 73: 99999})
        make(tmp, 'f27_v0', fr, [(60.0, 71, 90000000, 120000)])
        r = run_reader(tmp, 'f27_v0')
        check('base admitted', r['admitted'], r['why'])
        check('t_s is the stamp of the stable frame', abs(r['t_s'] - 29.5) < 1e-9, r['t_s'])
        check('P1 yes (90 MB on hold)', r['P1'] and r['p1_saves'] == 1)
        check('frame 72 120 ms on the window', r['frames_on_windows'] == [(72, 120000)], r['frames_on_windows'])
        check('P2 yes (arm 0)', r['P2'])
        check('P3 yes by the loader code (N = payload, item 636 (g))', r['P3'] and not r['p3_parts']['n_eq_size'], r['p3_parts'])
        check('P4 yes', r['P4'])
        check('P5 yes', r['P5'])
        check('P6 yes (0.5 s samples)', r['P6'], (r.get('gpu_gap_median_s'), r.get('gpu_gap_max_s')))
        check('no idle windows (util 80)', r['idle_on_hold'] == [])
        # 2) bytes edge
        make(tmp, 'f27_v1a', base_frames(), [(60.0, 71, 79999999, 50000)])
        check('P1 no at 79 999 999 bytes', not run_reader(tmp, 'f27_v1a')['P1'])
        make(tmp, 'f27_v1a', base_frames(), [(60.0, 71, 80000000, 50000)])
        check('P1 yes at 80 000 000 bytes', run_reader(tmp, 'f27_v1a')['P1'])
        # 3) dt edge 99 999 vs 100 000 on the window (frame 72)
        make(tmp, 'f27_v1a', base_frames({72: 99999}), [(60.0, 71, 90000000, 120000)])
        check('dt 99 999 not counted', run_reader(tmp, 'f27_v1a')['frames_on_windows'] == [])
        make(tmp, 'f27_v1a', base_frames({72: 100000}), [(60.0, 71, 90000000, 120000)])
        check('dt 100 000 counted', run_reader(tmp, 'f27_v1a')['frames_on_windows'] == [(72, 100000)])
        # 4) window edges: frame k spans [t(k-1), t(k)]; the window [t - us, t]; on when t(k) >= t - us and t(k-1) <= t + 0.02
        #    save at t = 60.48 with us 0 -> window [60.48, 60.48]; frame 72 [60.0, 60.5] on; frame 73 [60.5, 61.0]: t(k-1) = 60.5 <= 60.50 on
        make(tmp, 'f27_v1a', base_frames({73: 150000}), [(60.48, 72, 90000000, 0)])
        check('start of frame = t + 0.02 counted', run_reader(tmp, 'f27_v1a')['frames_on_windows'] == [(73, 150000)])
        make(tmp, 'f27_v1a', base_frames({73: 150000}), [(60.479, 72, 90000000, 0)])
        check('start of frame = t + 0.021 not counted', run_reader(tmp, 'f27_v1a')['frames_on_windows'] == [])
        #    the window [60.5 - 0.0, ...]: frame 72 ends at 60.5 = w0 -> on (b >= w0)
        make(tmp, 'f27_v1a', base_frames({72: 150000}), [(60.5, 73, 90000000, 0)])
        check('end of frame = w0 counted', (72, 150000) in run_reader(tmp, 'f27_v1a')['frames_on_windows'])
        # 5) a frame on the window before the stable frame (n <= Ns) is not a hold frame
        make(tmp, 'f27_v1a', base_frames({10: 150000}), [(29.4, 9, 90000000, 200000)])
        r = run_reader(tmp, 'f27_v1a')
        check('frame n = Ns not a hold frame', r['frames_on_windows'] == [], r['frames_on_windows'])
        check('save ending before t_s not on hold', not r['P1'])
        # 6) the save at the exit (after the hold end 149.5) - not on the hold by the letter, counted by the savewin variant
        fr = base_frames({300: 150000}, last=301)
        make(tmp, 'f27_v1a', fr, [(174.5, 300, 90000000, 100000)])
        r = run_reader(tmp, 'f27_v1a')
        check('exit save: not P1 by letter', not r['P1'], r['saves'])
        check('exit save: savewin variant counts it', r['frames_on_windows_savewin'] == [(300, 150000)], r['frames_on_windows_savewin'])
        check('exit save row present with on_hold False', len(r['saves']) == 1 and r['saves'][0]['on_hold'] is False)
        #    a save whose window straddles the hold end (149.5): w0 149.45 <= 149.5 -> on hold
        make(tmp, 'f27_v1a', fr, [(149.6, 250, 90000000, 150000)])
        check('save straddling the hold end is on hold', run_reader(tmp, 'f27_v1a')['P1'])
        # 7) P2
        make(tmp, 'f27_v1a', base_frames(), [], pcw=0)
        check('P2 no: v1 tag with KYTY_S_PCW=0', not run_reader(tmp, 'f27_v1a')['P2'])
        make(tmp, 'f27_v1a', base_frames(), [], pcw=-1)
        check('P2 no: no line', not run_reader(tmp, 'f27_v1a')['P2'])
        make(tmp, 'f27_v1a', base_frames(), [], extra_lines=['S-pcw: KYTY_S_PCW=1 KYTY_S_PCW_FORCE_MS=0'])
        check('P2 no: two lines', not run_reader(tmp, 'f27_v1a')['P2'])
        # 8) P3
        make(tmp, 'f27_v1a', base_frames(), [], loaded=127690373)
        check('P3 no when N = size of the copy (old letter, item 636 (g))', not run_reader(tmp, 'f27_v1a')['P3'])
        make(tmp, 'f27_v1a', base_frames(), [], loaded=127690296)
        check('P3 no when N = payload - 1', not run_reader(tmp, 'f27_v1a')['P3'])
        make(tmp, 'f27_v1a', base_frames(), [])
        check('P3 yes when N = payload', run_reader(tmp, 'f27_v1a')['P3'])
        make(tmp, 'f27_v1a', base_frames(), [], ns='f27_f27_v1a')
        check('P3 no on a namespace mismatch', not run_reader(tmp, 'f27_v1a')['P3'])
        make(tmp, 'f27_v1a', base_frames(), [], salt=dict(salt='f27_v1a', name='PPSA21564.0000000000000000.bin',
                                                          size='127690373', payload='127690297'))
        check('P3 no on another file name', not run_reader(tmp, 'f27_v1a')['P3'])
        import f27c_tools as TT
        hn = TT.salt_name('f27_v1a')
        make(tmp, 'f27_v1a', base_frames(), [], extra_lines=['Vulkan pipeline cache: invalidating _PipelineCache\\%s (driver, emulator, '
                                                             'or data mismatch)' % hn])
        r = run_reader(tmp, 'f27_v1a')
        check('P3 no with an invalidating line for the salted path', not r['P3'] and r['p3_parts']['invalidating'], r['p3_parts'])
        make(tmp, 'f27_v1a', base_frames(), [], extra_lines=['Vulkan pipeline cache: invalidating _PipelineCache\\PPSA21564.bin '
                                                             '(invalid file size)'])
        check('P3 yes with an invalidating line for another path', run_reader(tmp, 'f27_v1a')['P3'])
        # 9) P4
        make(tmp, 'f27_v1a', base_frames(), [], precache=True)
        check('P4 no with PipelinePrecache: saved', not run_reader(tmp, 'f27_v1a')['P4'])
        # 10) P5
        make(tmp, 'f27_v1a', base_frames(), [], p5='labels DIFFER x only-a 1 only-b 1')
        check('P5 no on DIFFER', not run_reader(tmp, 'f27_v1a')['P5'])
        make(tmp, 'f27_v1a', base_frames(), [], interference=True)
        r = run_reader(tmp, 'f27_v1a')
        check('P5 no and not admitted with INTERFERENCE_P5', not r['P5'] and not r['admitted'])
        # 11) P6
        rows = [(HOLD_FROM + datetime.timedelta(seconds=-40 + 0.5 * i), 80) for i in range(360)]
        rows = [x for x in rows if not (HOLD_FROM + datetime.timedelta(seconds=50) < x[0] < HOLD_FROM + datetime.timedelta(seconds=51.2))]
        make(tmp, 'f27_v1a', base_frames(), [], csv_rows=rows)
        r = run_reader(tmp, 'f27_v1a')
        check('P6 no on a 1.5 s gap inside the hold', not r['P6'], r.get('gpu_gap_max_s'))
        rows = [(HOLD_FROM + datetime.timedelta(seconds=0.1 + 0.5 * i), 80) for i in range(300)]
        make(tmp, 'f27_v1a', base_frames(), [], csv_rows=rows)
        check('P6 no when the first sample is after hold_from', not run_reader(tmp, 'f27_v1a')['P6'])
        rows = [(HOLD_FROM + datetime.timedelta(seconds=-40 + 1.0 * i), 80) for i in range(200)]
        make(tmp, 'f27_v1a', base_frames(), [], csv_rows=rows)
        check('P6 yes at 1.0 s gaps (tolerance edge)', run_reader(tmp, 'f27_v1a')['P6'])
        # 12) idle windows on the hold and coincidence: util 5 % from hold_from + 40 s to + 45 s; wall = log + (hold_from - 29.5)
        #     frame 150 (log 99.5, span [99.0, 99.5]) -> wall hold_from + [69.5, 70.0]: no; put the idle window there
        def idle_rows(a, b):
            out = []
            for i in range(360):
                t = HOLD_FROM + datetime.timedelta(seconds=-40 + 0.5 * i)
                out.append((t, 5 if HOLD_FROM + datetime.timedelta(seconds=a) <= t <= HOLD_FROM + datetime.timedelta(seconds=b) else 80))
            return out
        make(tmp, 'f27_v1a', base_frames({150: 150000}), [], csv_rows=idle_rows(68, 72))
        r = run_reader(tmp, 'f27_v1a')
        check('idle window on the hold found', len(r['idle_on_hold']) == 1, r['idle_on_hold'])
        check('frame 150 coincides strict', r['idle_coincide_strict'] == [(150, 150000)], r['idle_coincide_strict'])
        #     window [70.5, 74]: frame 150 wall [69.5, 70.0] strict no, loose [68.5, 70.0] - still no (ends before 70.5) -> window [70.2, 74]
        make(tmp, 'f27_v1a', base_frames({150: 150000}), [], csv_rows=idle_rows(70.2, 74))
        r = run_reader(tmp, 'f27_v1a')
        check('strict no', r['idle_coincide_strict'] == [], r['idle_coincide_strict'])
        check('loose no (window after the frame: placement only shifts earlier)', r['idle_coincide_loose'] == [], r['idle_coincide_loose'])
        make(tmp, 'f27_v1a', base_frames({150: 150000}), [], csv_rows=idle_rows(64, 68.8))
        r = run_reader(tmp, 'f27_v1a')
        check('strict no for a window ending 1.0 s before the frame end', r['idle_coincide_strict'] == [])
        check('loose yes for it', r['idle_coincide_loose'] == [(150, 150000)], r['idle_coincide_loose'])
        make(tmp, 'f27_v1a', base_frames(), [], csv_rows=idle_rows(-30, -26))
        check('idle window before the hold is not on the hold', run_reader(tmp, 'f27_v1a')['idle_on_hold'] == [])
        # 13) series states
        S = R.series_state
        def rr(tag, p1s, fr, p1=True):
            return dict(tag=tag, admitted=True, saves=[1], p1_saves=p1s, frames_on_windows=[(1, 1)] * fr, P1=p1)
        check('series: NEXT f27_v0', S([]) == 'NEXT f27_v0')
        check('series: NEXT f27_v0b', S([rr('f27_v0', 1, 0)]).startswith('NEXT f27_v0b'))
        check('series: power, NEXT v1a', S([rr('f27_v0', 2, 1)]).endswith('NEXT f27_v1a'))
        check('series: v0 + v0b power', S([rr('f27_v0', 1, 0), rr('f27_v0b', 1, 1)]).endswith('NEXT f27_v1a'))
        check('series: without power', S([rr('f27_v0', 2, 0)]).startswith('CONTROL WITHOUT POWER'))
        check('series: NO_POWER twice', S([rr('f27_v0', 0, 0, False), rr('f27_v0b', 0, 0, False)]).startswith('NO_POWER'))
        check('series: 1 save 2 frames -> NEXT f27_v0b (636 (b))', S([rr('f27_v0', 1, 2)]).startswith('NEXT f27_v0b ('))
        check('series: v0 (1, 2) + v0b P1 -> power (636 (v)(1))', S([rr('f27_v0', 1, 2), rr('f27_v0b', 1, 0)]) ==
              'CONTROL WITH POWER (d)(1); NEXT f27_v1a')
        check('series: v0 (1, 2) + v0b without P1 -> not determined (636 (v)(2))',
              S([rr('f27_v0', 1, 2), rr('f27_v0b', 0, 0, False)]).startswith('UNDEFINED item 636 (v)(2)'))
        na = dict(tag='f27_v0b', admitted=False, why=['INTERFERENCE_P5'])
        check('series: v0b not admitted -> NEXT f27_v0b_r1 (636 (v)(3))', S([rr('f27_v0', 1, 2), na]).startswith('NEXT f27_v0b_r1'))
        check('series: v0b na + v0b_r1 P1 -> power', S([rr('f27_v0', 1, 2), na, rr('f27_v0b_r1', 1, 0)]).endswith('NEXT f27_v1a'))
        na1 = dict(tag='f27_v0b_r1', admitted=False, why=['INTERFERENCE_P5'])
        check('series: v0b na twice -> UNDEFINED (no third control)', S([rr('f27_v0', 1, 2), na, na1]).startswith('UNDEFINED by'))
        check('series: the v0b state string matches the post_f27c stop pattern', 'UNDEFINED' in S([rr('f27_v0', 1, 2), rr('f27_v0b', 0, 0, False)]))
        check('series: undefined (no P1 once)', S([rr('f27_v0', 0, 0, False)]).startswith('UNDEFINED'))
        check('series: NEXT v1b', S([rr('f27_v0', 2, 1), rr('f27_v1a', 1, 0)]).endswith('NEXT f27_v1b'))
        check('series: v1 frame -> STOP', S([rr('f27_v0', 2, 1), rr('f27_v1a', 1, 1)]).startswith('STOP'))
        check('series: v1c for a v1 without P1', S([rr('f27_v0', 2, 1), rr('f27_v1a', 0, 0, False), rr('f27_v1b', 1, 0)]).endswith('NEXT f27_v1c (a v1 tag without P1)'))
        check('series: complete', S([rr('f27_v0', 2, 1), rr('f27_v1a', 1, 0), rr('f27_v1b', 1, 0)]).endswith('SERIES COMPLETE'))
        # 14) import sha refusal
        bad = os.path.join(tmp, 'savewin_bad.py')
        shutil.copy(R.SAVEWIN, bad)
        open(bad, 'a').write('\n')
        try:
            R.load(bad, R.SAVEWIN_SHA, 'x')
            check('import refused on a changed source', False)
        except SystemExit as e:
            check('import refused on a changed source', 'IMPORT REFUSED' in str(e))
        check('savewin source sha = the F27a commit file', sha(R.SAVEWIN) == R.SAVEWIN_SHA)
        # 15) output in strict cp1250 (no PYTHONIOENCODING), table mode
        env = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
        env['PYTHONIOENCODING'] = 'cp1250:strict'
        p = subprocess.run([sys.executable, os.path.join(HERE, 'f27c_read.py'), 'f27_v0', '--root', tmp], capture_output=True, env=env)
        check('tag print in strict cp1250', p.returncode == 0 and b'MEMBERS f27_v0' in p.stdout, p.stderr[-200:])
        p = subprocess.run([sys.executable, os.path.join(HERE, 'f27c_read.py'), '--table', '--root', tmp], capture_output=True, env=env)
        check('table print in strict cp1250', p.returncode == 0 and b'SERIES ' in p.stdout, p.stderr[-200:])
        # 16) positive control: the restated overlap rule = savewin_f27a.out.txt on ednn122
        if '--no-ref' not in argv:
            j = json.load(open('C:/kyty/s122/ednn122.json'))
            ns = [a for a in j['attempts'] if a.get('outcome') == 'ok'][-1]['stable_frame']
            frames, saves = R.SW.scan('C:/kyty/s122/log_ednn122.txt')
            got = []
            for line, nb, us, t_end, last_n in saves:
                if last_n < ns or t_end is None:
                    continue
                over = R.overlaps(frames, t_end - us / 1e6, t_end)
                ge = [(fr[0], fr[1]) for k, fr in over if fr[1] >= 100000]
                got.append('save line %d bytes %d us %d frames %d..%d ge100 %s' % (line, nb, us, over[0][1][0], over[-1][1][0], ge))
            ref = [l for l in open(os.path.join(os.path.dirname(R.SAVEWIN), 'savewin_f27a.out.txt')).read().splitlines() if l.startswith('ednn122 ')]
            want = []
            for l in ref:
                p_ = l.split()
                fr_ = l.split(' frames ')[1].split(' ')[0]
                want.append('save line %s bytes %s us %s frames %s ge100 %s' % (p_[3], p_[5], p_[7], fr_, l.split(' ge100 ')[1]))
            check('restated rule = savewin_f27a.out.txt on ednn122 (stable %s)' % ns, got == want, (got, want))
            check('positive control: frame 1826 118 647 us on the window', any('(1826, 118647)' in g for g in got))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('checks %d failed %d' % (N, BAD))
    if BAD == 0:
        print('ALL OK')
    return 0 if BAD == 0 else 1


if __name__ == '__main__':
    print('suite test_f27c_read.py sha256 %s target f27c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'f27c_read.py'))))
    sys.exit(main(sys.argv[1:]))

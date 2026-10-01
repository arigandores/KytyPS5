"""test_f5c_read.py - fixtures of f5c_read.py (F5c, HPP-357): every member of the letter of p.273(e)(3)(a)-(g), the window of
p.278(v), RC3 p.280(e)(1)-(3), N1/N2 p.285(v), the controls, the admission, the stop check, the seal check, strict cp1250 output.
Synthetic logs in C:/kyty/f287/f5c/fx/<case>/ (rebuilt every run).  ASCII only.  The last line is 'ALL OK' when every check
passed.
  python test_f5c_read.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f5c_read as R  # noqa: E402

FX = os.path.join(HERE, 'fx')
DT = 33333
SKY = R.SKY


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


class Gen:
    """A synthetic F5c log: clock in us; rows of DT; events inserted by time."""

    def __init__(self, tag, **kw):
        self.tag = tag
        self.o = dict(fix=R.TAGS[tag]['fix'], w=R.TAGS[tag]['arm'] == 'W', video=R.TAGS[tag]['video'],
                      total_s=340.0, min_at=60.0, restore_at=70.0, end_at=70.5, begin=True, end=True, win_min=1,
                      vke_at=None, vuid_at=None, death_at=None, k2_at=None, armed_blank=False, cfg='on delay_s=60.000 dur_s=10.000',
                      fixon=None, entry_rows=5, first_after_min=False, cut_at=None, zero_lines_at0=False, hold_exit=None,
                      outcome='ok', glitch_t=(), perm_at=None, frames=None, sheet=True, env={}, binary=R.BIN_SHA, restore=True,
                      rows_episode=True)
        self.o.update(kw)

    def build(self):
        o = self.o
        d = os.path.join(FX, self.tag + '_' + o.get('case', 'x'))
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        L = []
        if o['w']:
            L.append(b'VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features')
            L.append(b'[Vulkan][I] layer on')
        fixon = o['fixon'] if o['fixon'] is not None else (1 if o['fix'] == '1' else 0)
        L += [b'FixMinimize: on'] * fixon
        L.append(('TestMinimize: config %s' % o['cfg']).encode())
        L.append(b'GuestOut: Level has started: ')
        n = 0
        t = 0
        for _ in range(3):
            n += 1
            t += DT
            L.append(b'FrameTrace: n=%d dt_us=%d draws=0' % (n, DT))
        L.append(b'LevelDocument Loaded: ' + SKY.encode())
        if not o['armed_blank']:
            L.append(b'GuestOut: Level has started: ' + SKY.encode())
        L.append(b'TestMinimize: armed delay_s=60.000 dur_s=10.000')
        t0 = t
        ev = []

        def at(s, line):
            ev.append((t0 + int(s * 1e6), line))
        at(o['min_at'], b'TestMinimize: minimize')
        for _ in range(o['win_min']):
            at(o['min_at'] + 0.01, b'Window 1 minimized')
        at(o['min_at'] + 0.02, b'Recovering Vulkan swapchain')
        if o['fix'] == '1' or o['zero_lines_at0']:
            if o['begin']:
                at(o['min_at'] + 0.03, b'SwapchainZeroExtent: begin')
            if o['end']:
                ms = int((o['end_at'] - o['min_at'] - 0.03) * 1000)
                at(o['end_at'], b'SwapchainZeroExtent: end frames_dropped=300 ms=%d' % ms)
        if o['restore']:
            at(o['restore_at'], b'TestMinimize: restore')
            at(o['restore_at'] + 0.01, b'Window 1 restored')
        if o['vke_at'] is not None:
            at(o['vke_at'], b'[Vulkan][E] some error')
        if o['vuid_at'] is not None:
            at(o['vuid_at'], b'[Vulkan][E] Validation Error: [ VUID-VkSwapchainCreateInfoKHR-imageExtent-01689 ] imageExtent (width = 0, height = 0)')
        if o['death_at'] is not None:
            at(o['death_at'], b'Unhandled exception: 0xC0000005')
        ev.sort()
        ei = 0
        draws_first = 500 if not o['first_after_min'] else 0
        idx = []
        rec = 0
        pres = 0
        total = t0 + int(o['total_s'] * 1e6)
        if o['cut_at'] is not None:
            total = t0 + int(o['cut_at'] * 1e6)
        k = 0
        while t < total:
            dt = DT
            if o['k2_at'] is not None and abs((t - t0) / 1e6 - o['k2_at']) < DT / 2e6:
                dt = 1200000
            while ei < len(ev) and ev[ei][0] <= t:
                L.append(ev[ei][1])
                ei += 1
            ts = (t - t0) / 1e6
            in_ep = o['min_at'] <= ts < o['end_at']
            if in_ep and not o['rows_episode']:
                t += dt
                continue
            n += 1
            t += dt
            k += 1
            dr = draws_first if (k < 3 or not o['first_after_min'] or ts > o['min_at'] + 1) else 0
            if o['first_after_min'] and ts < o['min_at'] + 1:
                dr = 0
            L.append(b'FrameTrace: n=%d dt_us=%d draws=%d' % (n, dt, dr))
            pres += 1
            if not in_ep:
                idx.append([rec, pres, t / 1e6])
                rec += 1
        while ei < len(ev):
            L.append(ev[ei][1])
            ei += 1
        L.append(b'last line here')
        open(os.path.join(d, 'log_%s.txt' % self.tag), 'wb').write(b'\n'.join(L) + b'\n')
        open(os.path.join(d, 'stdout_%s.txt' % self.tag), 'wb').write(b'stdout\n')
        env = dict(KYTY_FIX_MINIMIZE=o['fix'], KYTY_TEST_MINIMIZE='60:10', KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0')
        if o['w']:
            env.update(KYTY_PIPELINE_PRECACHE='0', VK_LAYER_MESSAGE_ID_FILTER=R.VKFILTER)
        if o['video']:
            env['KYTY_REC'] = 'C:\\kyty\\f287\\f5c\\rec_%s.mp4' % self.tag
        env.update(o['env'])
        env = {k: v for k, v in env.items() if v is not None}
        js = dict(binary_sha256=o['binary'], guest_args='-lvl ' + SKY, env=env,
                  cmdline=['kyty_emulator.exe', '--vulkan-validation', 'true' if o['w'] else 'false'],
                  attempts=[dict(outcome=o['outcome'], hold_s=330.0, hold_exit=o['hold_exit'], detail=None)])
        json.dump(js, open(os.path.join(d, '%s.json' % self.tag), 'w'))
        if o['video']:
            if o['perm_at'] is not None:
                i = next(j for j, r in enumerate(idx) if r[2] - t0 / 1e6 >= o['perm_at'])
                idx[i][1], idx[i + 1][1] = idx[i + 1][1], idx[i][1]
            frames = o['frames'] if o['frames'] is not None else len(idx)
            open(os.path.join(d, 'rec_%s.mp4.idx' % self.tag), 'w').write(
                ''.join('%d %d %.3f\n' % (r[0], r[1], r[2] - idx[0][2]) for r in idx))
            gl = ['rec_%s.mp4: %d frames 960x540, index entries %d' % (self.tag, frames, len(idx)),
                  'one-frame glitches: %d' % len(o['glitch_t'])]
            for gt in o['glitch_t']:
                # glitch at the time gt (s after armed) on the idx clock
                tt = gt + t0 / 1e6 - idx[0][2]
                gl.append('  video %5d present %6d t=%7.2fs diff_prev=  9.0 diff_next=  9.0' % (100, 101, tt))
            open(os.path.join(d, 'glitch_%s.txt' % self.tag), 'w').write('\n'.join(gl) + '\n')
            if o['sheet']:
                open(os.path.join(d, 'sheet_%s.png' % self.tag), 'wb').write(b'png')
        return d


SC = R.load(R.SC142, R.SC142_SHA, 'sc142')
N = 0
BAD = []


def check(name, cond, info=''):
    global N
    N += 1
    print('%-4s %s %s' % ('ok' if cond else 'FAIL', name, info))
    if not cond:
        BAD.append(name)


def run(tag, case, **kw):
    g = Gen(tag, case=case, **kw)
    d = g.build()
    return R.read_tag(tag, d, SC)


def main():
    print('suite test_f5c_read.py sha256 %s target f5c_read.py sha256 %s' % (sha(os.path.abspath(__file__)),
                                                                           sha(os.path.join(HERE, 'f5c_read.py'))))
    shutil.rmtree(FX, ignore_errors=True)
    os.makedirs(FX)
    # (a)
    r = run('f5c_a', 'good')
    check('a good -> PASS', r['verdict_letter'] == 'PASS', (r['verdict_letter'], r.get('parts'), r.get('not_evaluable_why')))
    check('a good: late_log False, late_ms False', r['late_log'] is False and r['late_ms'] is False, (r['late_log'], r['late_ms']))
    check('a good: shift printed, rows > 0', r['shift'] is not None and r['shift']['bytes'] > 0, r['shift'])
    check('a good: delay ~60 s, dur ~10 s', abs(r['delay_s'] - 60) < 0.1 and abs(r['dur_s'] - 10) < 0.1, (r['delay_s'], r['dur_s']))
    check('a good: stop-check continue', R.stop_check(json.loads(json.dumps(r, default=str))).startswith('continue'))
    r = run('f5c_a', 'twomin', win_min=2)
    check('a two Window 1 minimized -> FAIL', r['verdict_letter'] == 'FAIL' and not r['parts']['one_window1_minimized'])
    r = run('f5c_a', 'noend', end=False)
    check('a no end line -> FAIL', r['verdict_letter'] == 'FAIL' and not r['parts']['begin_end'] and not r['parts']['end_not_late'])
    r = run('f5c_a', 'nobegin', begin=False)
    check('a no begin line -> FAIL', r['verdict_letter'] == 'FAIL' and not r['parts']['begin_end'])
    r = run('f5c_a', 'late', end_at=73.0)
    check('a end 3 s after restore -> FAIL late', r['verdict_letter'] == 'FAIL' and r['late_log'] is True, r['late_log'])
    r = run('f5c_a', 'edge2', end_at=72.0 - 0.0001)
    check('a end just under restore + 2 s -> PASS', r['verdict_letter'] == 'PASS', (r['late_log'], r['t']))
    r = run('f5c_a', 'edge2b', end_at=72.1)
    check('a end 2.1 s after restore -> FAIL', r['verdict_letter'] == 'FAIL' and r['late_log'] is True, (r['late_log'], r['t']))
    r = run('f5c_a', 'vke', vke_at=100.0)
    check('a one [Vulkan][E] -> FAIL', r['verdict_letter'] == 'FAIL' and not r['parts']['vke0'])
    r = run('f5c_a', 'death', death_at=200.0)
    check('a death marker -> FAIL', r['verdict_letter'] == 'FAIL' and not r['parts']['deaths0'])
    check('a death marker without [Vulkan][E] -> stop', R.stop_check(json.loads(json.dumps(r, default=str))).startswith('stop'))
    r = run('f5c_a', 'short', total_s=300.0)
    check('a hold 300 s -> FAIL', r['verdict_letter'] == 'FAIL' and not r['parts']['hold'], r['dt_after_first_s'])
    r = run('f5c_a', 'hold310', total_s=310.2)
    check('a hold just above 310 s -> PASS', r['verdict_letter'] == 'PASS', r['dt_after_first_s'])
    r = run('f5c_a', 'rows', cut_at=95.0, total_s=95.0)
    check('a < 1000 rows after restore -> FAIL', r['verdict_letter'] == 'FAIL' and not r['parts']['rows_after_restore'],
          r['rows_after_restore'])
    r = run('f5c_a', 'holdexit', hold_exit=3)
    check('a hold_exit set -> FAIL', r['verdict_letter'] == 'FAIL' and not r['parts']['no_hold_exit'])
    r = run('f5c_a', 'noep', rows_episode=False)
    check('a no rows inside the episode -> still PASS (log clock skips the episode)', r['verdict_letter'] == 'PASS',
          (r['late_log'], r['late_ms'], r['late_disagree']))
    # controls / admission
    r = run('f5c_a', 'blank', armed_blank=True)
    check('N2: armed after a blank start line only -> NOT EVALUABLE', r['verdict_letter'] == 'NOT EVALUABLE', r['not_evaluable_why'])
    r = run('f5c_a', 'nofix', fixon=0)
    check('a no FixMinimize: on -> NOT EVALUABLE', r['verdict_letter'] == 'NOT EVALUABLE')
    r = run('f5c_a', 'cfg30', cfg='on delay_s=30.000 dur_s=10.000')
    check('a config delay 30 -> NOT EVALUABLE', r['verdict_letter'] == 'NOT EVALUABLE')
    r = run('f5c_a', 'firstlate', first_after_min=True)
    check('a first scene frame after minimize -> NOT EVALUABLE', r['verdict_letter'] == 'NOT EVALUABLE', r['first_pos'])
    r = run('f5c_a', 'norestore', restore=False)
    check('a no restore line -> NOT EVALUABLE', r['verdict_letter'] == 'NOT EVALUABLE')
    check('NOT EVALUABLE -> stop', R.stop_check(json.loads(json.dumps(r, default=str))).startswith('stop'))
    r = run('f5c_a', 'bin', binary='0' * 64)
    check('a other binary -> NOT ADMITTED', r['verdict_letter'] == 'NOT ADMITTED')
    check('NOT ADMITTED -> stop', R.stop_check(json.loads(json.dumps(r, default=str))).startswith('stop'))
    r = run('f5c_a', 'filt', env=dict(VK_LAYER_MESSAGE_ID_FILTER=R.VKFILTER + ',x'))
    check('a filter not exactly the F6 VUID -> NOT ADMITTED', r['verdict_letter'] == 'NOT ADMITTED')
    r = run('f5c_a', 'pre', env=dict(KYTY_PIPELINE_PRECACHE=None))
    check('a no KYTY_PIPELINE_PRECACHE=0 -> NOT ADMITTED', r['verdict_letter'] == 'NOT ADMITTED')
    r = run('f5c_a', 'stand', env=dict(KYTY_TEST_MINIMIZE='60:5'))
    check('a stand 60:5 -> NOT ADMITTED', r['verdict_letter'] == 'NOT ADMITTED')
    r = run('f5c_a', 'dual', env=dict(KYTY_FIX_DUALSRC='1'))
    check('a KYTY_FIX_DUALSRC set -> NOT ADMITTED', r['verdict_letter'] == 'NOT ADMITTED')
    r = run('f5c_a', 'ckp', env=dict(KYTY_GPU_CHECKPOINTS='0'))
    check('a KYTY_GPU_CHECKPOINTS present -> NOT ADMITTED', r['verdict_letter'] == 'NOT ADMITTED')
    # (b)
    r = run('f5c_b', 'good', vuid_at=60.05, hold_exit=1, total_s=60.06, restore=False)
    check('b VUID 01689 after minimize, ended -> STOP VUID-01689', r['verdict_letter'] == 'STOP VUID-01689',
          (r['verdict_letter'], r.get('parts'), r.get('not_evaluable_why')))
    check('b stop-check continue', R.stop_check(json.loads(json.dumps(r, default=str))).startswith('continue'))
    r = run('f5c_b', 'early', vuid_at=59.0, hold_exit=1, total_s=60.06, restore=False)
    check('b VUID before minimize -> NO STOP', r['verdict_letter'] == 'NO STOP')
    r = run('f5c_b', 'alive', vuid_at=60.05, hold_exit=None, total_s=60.06, restore=False)
    check('b emulator not ended -> NO STOP', r['verdict_letter'] == 'NO STOP')
    r = run('f5c_b', 'novuid', hold_exit=None)
    check('b no VUID at all -> NO STOP', r['verdict_letter'] == 'NO STOP')
    r = run('f5c_b', 'zero', zero_lines_at0=True, vuid_at=60.05, hold_exit=1, total_s=60.06, restore=False)
    check('b SwapchainZeroExtent lines at =0 -> NOT EVALUABLE', r['verdict_letter'] == 'NOT EVALUABLE')
    r = run('f5c_b', 'fixon', fixon=1, vuid_at=60.05, hold_exit=1, total_s=60.06, restore=False)
    check('b FixMinimize: on at =0 -> NOT EVALUABLE', r['verdict_letter'] == 'NOT EVALUABLE')
    # (v)
    r = run('f5c_v', 'good')
    check('v good -> PASS', r['verdict_letter'] == 'PASS', (r['verdict_letter'], r.get('parts'), r.get('not_evaluable_why')))
    v = r['video']
    check('v good: anchored window ~ [60, 72.5] after armed', v is not None, v and (v['win_anchored'], v['win_gap']))
    check('v good: N1 records after end > 0, no break', v['after_end_records'] > 0 and not v['after_end_bad'])
    r = run('f5c_v', 'glin', glitch_t=(71.0,))
    check('v glitch inside the window -> PASS', r['verdict_letter'] == 'PASS', r['video']['glitches_out_anchored'])
    r = run('f5c_v', 'glin2', glitch_t=(72.3,))
    check('v glitch at end + 1.8 s -> PASS', r['verdict_letter'] == 'PASS', (r['video']['win_anchored'], r['video']['glitches_out_anchored']))
    r = run('f5c_v', 'glout', glitch_t=(73.0,))
    check('v glitch at end + 2.5 s -> FAIL', r['verdict_letter'] == 'FAIL' and not r['parts']['glitches_outside0'])
    r = run('f5c_v', 'glbefore', glitch_t=(59.0,))
    check('v glitch 1 s before minimize -> FAIL', r['verdict_letter'] == 'FAIL')
    r = run('f5c_v', 'perm', perm_at=100.0)
    check('v present permutation after end -> FAIL (N1)', r['verdict_letter'] == 'FAIL' and not r['parts']['n1_present_order_after_end'],
          r['video']['after_end_bad'][:2])
    r = run('f5c_v', 'permbefore', perm_at=30.0)
    check('v permutation before minimize -> letter PASS, whole-file break printed',
          r['verdict_letter'] == 'PASS' and len(r['video']['all_bad']) == 1, r['video']['all_bad'])
    r = run('f5c_v', 'frames', frames=2999)
    check('v 2999 video frames -> FAIL', r['verdict_letter'] == 'FAIL' and not r['parts']['video_frames'])
    r = run('f5c_v', 'nosheet', sheet=False)
    check('v no sheet -> FAIL', r['verdict_letter'] == 'FAIL' and not r['parts']['sheet'])
    r = run('f5c_v', 'k2out', k2_at=150.0)
    check('v K2 outside the window -> FAIL', r['verdict_letter'] == 'FAIL' and r['k2_out'] == 1, r['k2'])
    r = run('f5c_v', 'k2in', k2_at=71.0)
    check('v K2 inside the window -> PASS', r['verdict_letter'] == 'PASS' and r['k2_out'] == 0, r['k2'])
    r = run('f5c_v', 'k1in', death_at=65.0)
    check('v K1 inside the window -> PASS', r['verdict_letter'] == 'PASS', r['deaths_out'])
    r = run('f5c_v', 'k1out', death_at=200.0)
    check('v K1 outside the window -> FAIL', r['verdict_letter'] == 'FAIL' and not r['parts']['no_k1k2_outside'])
    r = run('f5c_v', 'hold', total_s=329.0)
    check('v hold < 330 s -> FAIL', r['verdict_letter'] == 'FAIL' and not r['parts']['hold'])
    r = run('f5c_v', 'late', end_at=73.0)
    check('v end 3 s after restore -> FAIL', r['verdict_letter'] == 'FAIL' and not r['parts']['end_not_late'])
    r = run('f5c_v', 'w', env=dict(KYTY_PIPELINE_PRECACHE='0'))
    check('v KYTY_PIPELINE_PRECACHE set -> NOT ADMITTED', r['verdict_letter'] == 'NOT ADMITTED')
    # (g)
    r = run('f5c_g', 'crash', death_at=60.1, hold_exit=3221225477, total_s=60.2, restore=False)
    check('g crash -> DATA, death marker counted, exit code kept', r['verdict_letter'] == 'DATA' and r['deaths'] == 1
          and r['hold_exit'] == 3221225477 and r['last_log'] == 'last line here', (r['deaths'], r['hold_exit'], r['last_log']))
    check('g stop-check continue', R.stop_check(json.loads(json.dumps(r, default=str))).startswith('continue'))
    r = run('f5c_g', 'held')
    check('g held -> DATA', r['verdict_letter'] == 'DATA')
    # text output in strict cp1250 without PYTHONIOENCODING
    d = Gen('f5c_v', case='cp').build()
    env = {k: v for k, v in os.environ.items() if k != 'PYTHONIOENCODING'}
    env['PYTHONIOENCODING'] = 'cp1250:strict'
    p = subprocess.run([sys.executable, os.path.join(HERE, 'f5c_read.py'), '--tag', 'f5c_v', '--root', d], env=env,
                       capture_output=True)
    check('text output in strict cp1250 rc 0 and ASCII', p.returncode == 0 and all(c < 128 for c in p.stdout), (p.returncode, p.stderr[-200:]))
    check('text output has the verdict line', b'F5C VERDICT f5c_v letter (v): PASS' in p.stdout)
    del env['PYTHONIOENCODING']
    p = subprocess.run([sys.executable, os.path.join(HERE, 'f5c_read.py'), '--tag', 'f5c_v', '--root', d], env=env,
                       capture_output=True)
    check('text output without PYTHONIOENCODING rc 0', p.returncode == 0, p.stderr[-200:])
    p = subprocess.run([sys.executable, os.path.join(HERE, 'f5c_read.py'), '--tag', 'nope'], env=env, capture_output=True)
    check('usage rc 2', p.returncode == 2)
    p = subprocess.run([sys.executable, os.path.join(HERE, 'f5c_read.py'), '--tag', 'f5c_a', '--root', FX], env=env, capture_output=True)
    check('no log rc 1', p.returncode == 1)
    # seal check
    sd = os.path.join(FX, 'seal')
    os.makedirs(sd)
    open(os.path.join(sd, 'a.txt'), 'w').write('a')
    open(os.path.join(sd, 'b.txt'), 'w').write('b')
    pr = os.path.join(sd, 'pred.md')
    open(pr, 'w').write('x\nseal: %s a.txt\nseal: %s b.txt\n' % (sha(os.path.join(sd, 'a.txt')), sha(os.path.join(sd, 'b.txt'))))
    ok, _ = R.check_seal(pr, sd, ('a.txt', 'b.txt'))
    check('seal ok', ok)
    open(os.path.join(sd, 'b.txt'), 'w').write('B')
    ok, _ = R.check_seal(pr, sd, ('a.txt', 'b.txt'))
    check('seal mismatch refused', not ok)
    ok, _ = R.check_seal(pr, sd, ('a.txt', 'b.txt', 'c.txt'))
    check('seal missing name refused', not ok)
    check('stop-check no reading -> stop', R.stop_check(None).startswith('stop'))
    print('checks %d failed %d %s' % (N, len(BAD), BAD))
    if not BAD:
        print('ALL OK')
    return 0 if not BAD else 1


if __name__ == '__main__':
    sys.exit(main())

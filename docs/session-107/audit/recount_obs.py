"""Independent recount of obs107 (auditor, no session code imported)."""
import re, sys, statistics, json
from collections import Counter

LOG = 'C:/kyty/s107/log_obs107.txt'
KEYS = ['pl_cont_n', 'pl_cont_wall_ns', 'pl_cont_cpu_ns'] + ['pl_cont_h%d_ns' % k for k in range(4)] + \
       ['pl_cont_h%d_n' % k for k in range(4)] + ['pl_wq_hold_ns', 'pl_wq_hold_n', 'pl_wp_hold_ns', 'pl_wp_hold_n',
       'cspm_look', 'cspm_would', 'cspm_skip', 'cspm_bad', 'cspm_store', 'cspm_clear', 'cspf_have', 'cspf_new',
       'pl_prog_n', 'pl_prog_wait_us', 'pl_pipe_wait_us', 'pl_cs_wait_us', 'pl_prog_hold_us', 'pl_pipe_hold_us',
       'pl_cs_hold_us', 'pl_prog_wait_n', 'pl_pipe_wait_n', 'pl_cs_wait_n']
main = {}
xs = {}
drawl = {}
other = Counter()
verify = []
pins = 0
recs = []
gatearm = 0
fatal = Counter()
FAT = [b'--- Error', b'--- Fatal', b'std::terminate', b'abort()', b'DeviceLost', b'Unhandled exception',
       b'GpuWaitSlow', b'skipped draw', b'GpuHangAbort', b'MISMATCH']
rx = re.compile(rb'([A-Za-z_][A-Za-z0-9_]*)=(-?\d+)')
with open(LOG, 'rb') as f:
    for line in f:
        if line.startswith(b'FrameTrace: n='):
            d = dict((k.decode(), int(v)) for k, v in rx.findall(line))
            if d['n'] in main: other['dup_main'] += 1
            main[d['n']] = d
        elif line.startswith(b'FrameTrace-x: n='):
            d = dict((k.decode(), int(v)) for k, v in rx.findall(line))
            if d['n'] in xs: other['dup_x'] += 1
            xs[d['n']] = d
        elif line.startswith(b'FrameTrace-draw: n='):
            d = dict((k.decode(), int(v)) for k, v in rx.findall(line))
            drawl[d['n']] = d
        else:
            if b'CspMemoVerify' in line:
                verify.append(line[:300])
            if b'GpuClockPin' in line:
                pins += 1
            if b'RecordThread' in line and b'start' in line:
                recs.append(line[:120])
            for m in FAT:
                if m in line:
                    fatal[m] += 1
print('main rows', len(main), 'x rows', len(xs), 'draw rows', len(drawl), other)
print('pins', pins, 'recs', recs[:4], 'fatal', fatal)
print('verify lines', len(verify))
for v in verify[:10]:
    print('  ', v)
ns = sorted(n for n in main if n >= 1800)
win = []
missing = Counter()
for n in ns:
    x = xs.get(n)
    if x is None:
        missing['nox'] += 1; continue
    miss = [k for k in KEYS[:27] if k not in x]
    if miss:
        missing[tuple(miss[:3])] += 1; continue
    win.append((n, main[n], x, drawl.get(n)))
print('window rows', len(win), 'first', win[0][0], 'last', win[-1][0], 'missing', missing)
S = lambda k: sum(w[2].get(k, 0) for w in win)
N = len(win)
wall = S('pl_cont_wall_ns')
print('spin share', S('pl_cont_cpu_ns') / wall)
for k in range(4):
    print('holder %d share' % k, S('pl_cont_h%d_ns' % k) / wall, 'n share', S('pl_cont_h%d_n' % k) / S('pl_cont_n'))
print('sum h_ns / wall', sum(S('pl_cont_h%d_ns' % k) for k in range(4)) / wall,
      'sum h_n / n', sum(S('pl_cont_h%d_n' % k) for k in range(4)) / S('pl_cont_n'))
print('tag2_us', S('pl_cont_h2_ns') / N / 1000, 'cont wall us/flip', wall / N / 1000, 'pl_cont_n/flip', S('pl_cont_n') / N)
print('mean contended wall per acq us', wall / S('pl_cont_n') / 1000, 'cpu per acq', S('pl_cont_cpu_ns') / S('pl_cont_n') / 1000)
print('would_rate', S('cspm_would') / S('cspm_look'), 'look/flip', S('cspm_look') / N, 'would/flip', S('cspm_would') / N)
print('sum cspm_bad', S('cspm_bad'), 'cspm_skip', S('cspm_skip'), 'store/flip', S('cspm_store') / N, 'clear', S('cspm_clear'))
print('cspf_have/flip', S('cspf_have') / N, 'cspf_new', S('cspf_new'))
print('wq hold us/flip', S('pl_wq_hold_ns') / N / 1000, 'n/flip', S('pl_wq_hold_n') / N, 'per', S('pl_wq_hold_ns') / S('pl_wq_hold_n') / 1000)
print('wp hold us/flip', S('pl_wp_hold_ns') / N / 1000, 'n/flip', S('pl_wp_hold_n') / N, 'per', S('pl_wp_hold_ns') / S('pl_wp_hold_n') / 1000)
for k in ['pl_prog_wait_us', 'pl_pipe_wait_us', 'pl_cs_wait_us', 'pl_prog_hold_us', 'pl_pipe_hold_us', 'pl_cs_hold_us', 'pl_prog_n',
          'pl_prog_wait_n', 'pl_pipe_wait_n', 'pl_cs_wait_n']:
    print(k, S(k) / N)
print('dt mean', sum(w[1]['dt_us'] for w in win) / N, 'cpu_gpu', sum(w[1]['cpu_gpu_us'] for w in win) / N)
# per-flip distribution of cspm_bad, which frames
bad = [(w[0], w[2]['cspm_bad']) for w in win if w[2]['cspm_bad']]
print('bad frames', bad)
# all x keys starting pl_ or csp
allk = set()
for w in win[:5]:
    allk |= {k for k in w[2] if k.startswith('pl_') or k.startswith('csp')}
print(sorted(allk))
# rows before 1800 with cspm_bad
print('bad pre-window', [(n, xs[n].get('cspm_bad')) for n in xs if n < 1800 and xs[n].get('cspm_bad')])
# holder share by half of window
half = N // 2
for part, ws in (('1st', win[:half]), ('2nd', win[half:])):
    wl = sum(w[2]['pl_cont_wall_ns'] for w in ws)
    print(part, 'spin', sum(w[2]['pl_cont_cpu_ns'] for w in ws) / wl, 'h1', sum(w[2]['pl_cont_h1_ns'] for w in ws) / wl,
          'h2', sum(w[2]['pl_cont_h2_ns'] for w in ws) / wl, 'h0', sum(w[2]['pl_cont_h0_ns'] for w in ws) / wl)

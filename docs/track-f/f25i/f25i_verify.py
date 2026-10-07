#!/usr/bin/env python3
# F25i (HPP-676, Red Team): own check of F25h (1c492167) on the F25f logs - MEASUREMENT READING ONLY, no game, no lock.
# Independent of f25h_scan.py and of the reader f25_read.py: own regexes over log_<tag>.txt.
# Per frame of table22 (20 frames):
#  K  window key by item 596(d)(2): DiagB32: n line with dt_us >= 0.5 dt of the frame, else n+1, both - larger dt_us;
#  W  every DiagB32-w record of the keyed window (all kinds), the Gpu emu_mutex record: obj - Impl base (W:vo_pace obj);
#  T  timing: end of the Gpu wait in window coordinates (start_us + wait_us) against the end of the FlipQueue::m_mutex hold
#     of flip n-1 in the same coordinates (FlipHold us - present_us; the window opens at OnFlip, videoOut.cpp:1293,
#     after Present() and before the FrameTrace print) - a check of the holder that does not use the peer/waker field;
#  P  Present / Gpu / DrawThread -t: Sw, SwR, H, W, top;
#  L  FrameTrace-draw logs/log_us/log_gpu_us; FlipHold of flip n-1; other_us/dt;
#  S  log segments: lines between FrameTrace n-2..n-1 (prints of Flip(n-1) before its own snapshot: DiagB32 reports) and
#     between FrameTrace n-1..n (what was written during the stall), by kind.
# Per run: all emu_mutex records - waker == peer count; FlipHold lines count (cap 32).
import hashlib
import re
import sys

FRAMES = {
    'f25_s15': [3778, 3969, 4213, 4293, 4407, 4444, 4520, 4777, 5478, 7540],
    'f25_k04': [1608, 1646, 5091, 6504, 8966, 12357],
    'f25_k05': [17344, 17394, 17466, 17512],
}
KV = re.compile(rb'([A-Za-z_][A-Za-z0-9_]*)=(\S*)')
HDR = re.compile(rb'^\[\d+\]\[')


def kv(line):
    return {k.decode(): v.decode('latin-1') for k, v in KV.findall(line)}


def kind(line):
    if line.startswith(b'FrameTrace'):
        return 'FrameTrace'
    if line.startswith(b'DiagB32'):
        return 'DiagB32'
    if line.startswith(b'FlipHold'):
        return 'FlipHold'
    if HDR.match(line):
        return 'guest_hdr'
    if line.startswith(b'\t'):
        return 'tab_arg'
    return 'other'


def run(sdir, tag, frames):
    path = '%s/log_%s.txt' % (sdir, tag)
    h = hashlib.sha256()
    want = set()
    for n in frames:
        want.update((n, n + 1))
    segs_want = set()
    for n in frames:
        segs_want.update((n - 1, n))
    ft_dt, dg_dt, tl, wl, fh, draw = {}, {}, {}, {}, {}, {}
    vo_obj = {}
    seg = {}
    cur = {}
    wk_eq = wk_ne = 0
    with open(path, 'rb') as f:
        for line in f:
            h.update(line)
            k = kind(line)
            if line.startswith(b'FrameTrace: n='):
                d = kv(line)
                n = int(d['n'])
                ft_dt[n] = int(d['dt_us'])
                if n in segs_want:
                    seg[n] = cur
                cur = {}
            cur[k] = cur.get(k, 0) + 1
            if line.startswith(b'DiagB32: n='):
                d = kv(line)
                dg_dt[int(d['n'])] = int(d.get('dt_us', '0'))
            elif line.startswith(b'DiagB32-t: n='):
                d = kv(line)
                if int(d['n']) in want:
                    tl.setdefault(int(d['n']), []).append(d)
            elif line.startswith(b'DiagB32-w: n='):
                d = kv(line)
                if d.get('kind') == 'vo_pace':
                    vo_obj[d.get('obj')] = vo_obj.get(d.get('obj'), 0) + 1
                if d.get('kind') == 'emu_mutex':
                    if d.get('waker') == d.get('peer'):
                        wk_eq += 1
                    else:
                        wk_ne += 1
                if int(d['n']) in want:
                    wl.setdefault(int(d['n']), []).append(d)
            elif line.startswith(b'FlipHold:'):
                d = kv(line)
                fh[int(d['flip'])] = d
            elif line.startswith(b'FrameTrace-draw: n='):
                d = kv(line)
                if int(d['n']) in want:
                    draw[int(d['n'])] = d
    print('=== %s  log sha256 %s' % (tag, h.hexdigest()))
    print('W:vo_pace objects (from -w vo_pace) %s' % sorted(vo_obj.items()))
    print('emu_mutex records in run: waker==peer %d, waker!=peer %d' % (wk_eq, wk_ne))
    print('FlipHold lines in run %d (cap 32)' % len(fh))
    base = int(list(vo_obj)[0], 16) if len(vo_obj) == 1 else None
    for n in frames:
        dt = ft_dt.get(n, 0)
        c0 = dg_dt.get(n, 0)
        c1 = dg_dt.get(n + 1, 0)
        ok0 = c0 >= 0.5 * dt
        ok1 = c1 >= 0.5 * dt
        key = (n if c0 >= c1 else n + 1) if ok0 and ok1 else (n if ok0 else (n + 1 if ok1 else None))
        print('FRAME %s n %d dt %d | K DiagB32 dt[n]=%d dt[n+1]=%d key=%s' % (tag, n, dt, c0, c1, key))
        if key is None:
            continue
        role = {}
        for d in tl.get(key, []):
            role[d.get('slot')] = d.get('role') or d.get('name')
        for d in tl.get(key, []):
            if d.get('role') in ('Present', 'Gpu') or d.get('name') == 'DrawThread':
                print('  P %s/%s Sw %s SwR %s H %s W %s top %s' % (d.get('name'), d.get('role'), d.get('Sw'), d.get('SwR'),
                                                                 d.get('H'), d.get('W'), d.get('top')))
        f = fh.get(n - 1)
        hold_end = int(f['us']) - int(f['present_us']) if f else None
        for d in wl.get(key, []):
            off = int(d['obj'], 16) - base if base is not None and d.get('obj', '0x0').startswith('0x') else None
            line = '  W kind %s waiter %s obj %s off %s start %s wait %s peer %s(%s) waker %s(%s)' % (
                d.get('kind'), role.get(d.get('slot'), '?'), d.get('obj'), hex(off) if off is not None and 0 <= off < 0x2000 else '-',
                d.get('start_us'), d.get('wait_us'), d.get('peer'), role.get(d.get('peer'), '?'), d.get('waker'),
                role.get(d.get('waker'), '?'))
            if d.get('kind') == 'emu_mutex' and role.get(d.get('slot')) == 'Gpu' and hold_end is not None:
                end = int(d['start_us']) + int(d['wait_us'])
                line += ' | T wait_end %d hold_end(n-1) %d delta %d' % (end, hold_end, hold_end - end)
            print(line)
        dr = draw.get(n, {})
        print('  L logs %s log_us %s log_gpu_us %s | FlipHold(n-1) %s | other/dt %s' % (
            dr.get('logs'), dr.get('log_us'), dr.get('log_gpu_us'),
            ('us %s present %s poll %s other %s' % (f['us'], f['present_us'], f['poll_us'], f['other_us'])) if f else 'none',
            ('%.3f' % (int(f['other_us']) / dt)) if f and dt else '-'))
        print('  S seg(n-2..n-1) %s' % sorted(seg.get(n - 1, {}).items()))
        print('  S seg(n-1..n)   %s' % sorted(seg.get(n, {}).items()))


def main():
    sdir = sys.argv[1]
    for tag in sys.argv[2:]:
        run(sdir, tag, FRAMES[tag])


if __name__ == '__main__':
    main()

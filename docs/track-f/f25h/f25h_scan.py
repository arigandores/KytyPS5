#!/usr/bin/env python3
# F25h (HPP-675; ROADMAP s122 item 611(d)(2)): offline reading of the recorded KYTY_DIAG_B32 fields of the frames of the
# F25f series (binary B e342b839, code 35b454c6). MEASUREMENT READING ONLY - no game, no lock.
#
# For every FRAME row of runs/<tag>/read.txt (the reader f25_read.py, frames >= 100 ms after 10 s of the scene) it prints:
#  - the chain text and class of the reader (as printed), IN COUNT;
#  - every DiagB32-w record of kind emu_mutex of the window: waiter slot / role, obj, obj - base, wait_us, waker, peer;
#  - the -t line of Present, Gpu and DrawThread: R, r, Sr, Sw, S, W, H, SwR, cpu_us;
#  - flip_hold_ns of the FrameTrace-x line of the same n (= the hold of flip n-1: videoOut.cpp adds it after the
#    FrameTrace lines of its own flip) and the FlipHold: line of flip n-1 if printed (at most 32 per run);
# and per run: the objects of W:vo_pace (VideoOutDriver::Impl this, videoOut.cpp:833) and W:flip_req (FlipQueue this,
# videoOut.cpp:1190), the base = the vo_pace object; the Sw wait-reason histogram of the Present -t lines over all
# windows of the run.
#
# usage: f25h_scan.py <series dir> <tag> [<tag> ...]  (log_<tag>.txt and runs/<tag>/read.txt in the series dir)
import hashlib
import os
import re
import sys

KV = re.compile(rb'([A-Za-z_][A-Za-z0-9_]*)=(\S*)')
# FrameTrace-draw: n=<n> logs=<k> log_us=<us> log_gpu_us=<us> (videoOut.cpp:1473): Log::Write calls and their time
# (log.cpp CountWrite: all threads; log_gpu_us - the Gpu role) between the snapshots of flip n-1 and flip n.
LOGS = re.compile(rb'FrameTrace-draw: n=(\d+) logs=(\d+) log_us=(\d+) log_gpu_us=(\d+)')
CHAIN = 'Gpu(Gpu)=W:emu_mutex->waker > Present(Present)=Sw'

# Named offsets from VideoOutDriver::Impl (videoOut.cpp:253-289 at 35b454c6): m_mutex 0x0; m_video_out_ctx[i].mutex
# 0x8 + i * sizeof(VideoOutConfig) (0x410 by the member list videoOut.cpp:181-201 - an estimate checked by the two
# records below); m_flip_queue 0x1058 (= the recorded W:flip_req obj - base); FlipQueue::m_mutex 0x1060 (FlipQueue's
# first member is a reference, videoOut.cpp:241-242).
NAMES = {0x0: 'Impl::m_mutex', 0x1058: 'FlipQueue(this)', 0x1060: 'FlipQueue::m_mutex'}
for i in range(4):
    NAMES[0x8 + i * 0x410] = 'm_video_out_ctx[%d].mutex' % i


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(1 << 22)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def kv(line):
    return {k.decode(): v.decode('latin-1') for k, v in KV.findall(line)}


def read_frames(path):
    rows = []
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            s = line.strip()
            if not s.startswith('FRAME n '):
                continue
            parts = [p.strip() for p in s.split('|')]
            m = re.match(r'FRAME n (\d+) dt_us (\d+) t ([\d.]+) s', parts[0])
            rows.append({'n': int(m.group(1)), 'dt_us': int(m.group(2)), 't': float(m.group(3)),
                         'cls': parts[3] if len(parts) > 3 else '', 'chain': parts[4] if len(parts) > 4 else '',
                         'in_count': 'IN COUNT' in s, 'has_chain': CHAIN in s})
    return rows


def scan(log, targets):
    want = set(targets)
    hdr, trows, wrows, hold_x, fliphold = {}, {}, {}, {}, {}
    logx, log_all = {}, []
    objs = {}
    swr_present = {}
    present_windows = 0
    with open(log, 'rb') as f:
        for line in f:
            if line.startswith(b'DiagB32-t: n='):
                d = kv(line)
                n = int(d['n'])
                if d.get('role') == 'Present':
                    present_windows += 1
                    if d.get('SwR', '-') != '-':
                        for item in d['SwR'].split(','):
                            r, c = item.split(':')
                            swr_present[int(r)] = swr_present.get(int(r), 0) + int(c)
                last = d.get('last', '')
                if last in ('W:vo_pace', 'W:flip_req'):
                    objs.setdefault(last, {}).setdefault(d['obj'], 0)
                    objs[last][d['obj']] += 1
                if n in want:
                    trows.setdefault(n, []).append(d)
            elif line.startswith(b'DiagB32-w: n='):
                d = kv(line)
                n = int(d['n'])
                if d.get('kind') in ('vo_pace', 'flip_req'):
                    k = 'W:' + d['kind']
                    objs.setdefault(k, {}).setdefault(d['obj'], 0)
                    objs[k][d['obj']] += 1
                if n in want and d.get('kind') == 'emu_mutex':
                    wrows.setdefault(n, []).append(d)
            elif line.startswith(b'DiagB32: n='):
                d = kv(line)
                n = int(d['n'])
                if n in want:
                    hdr[n] = d
            elif line.startswith(b'FrameTrace-x: n='):
                m = re.match(rb'FrameTrace-x: n=(\d+)', line)
                n = int(m.group(1))
                if n in want:
                    d = kv(line)
                    hold_x[n] = (int(d.get('flip_hold_ns', '-1')), int(d.get('flip_hold_n', '-1')))
            elif line.startswith(b'FrameTrace-draw: n='):
                m = LOGS.match(line)
                if m:
                    n = int(m.group(1))
                    lu = int(m.group(3))
                    log_all.append(lu)
                    if n in want:
                        logx[n] = (int(m.group(2)), lu, int(m.group(4)))
            elif line.startswith(b'FlipHold:'):
                d = kv(line)
                fliphold[int(d['flip'])] = d
    return hdr, trows, wrows, hold_x, fliphold, objs, swr_present, present_windows, logx, log_all


def main():
    sdir = sys.argv[1]
    for tag in sys.argv[2:]:
        log = os.path.join(sdir, 'log_%s.txt' % tag)
        rtx = os.path.join(sdir, 'runs', tag, 'read.txt')
        print('=== tag %s' % tag)
        print('input %s sha256 %s' % (log, sha256(log)))
        print('input %s sha256 %s' % (rtx, sha256(rtx)))
        frames = read_frames(rtx)
        hdr, trows, wrows, hold_x, fliphold, objs, swr_present, pw, logx, log_all = scan(log, [fr['n'] for fr in frames])
        srt = sorted(log_all)
        if srt:
            q = lambda f: srt[min(len(srt) - 1, int(f * len(srt)))]
            print('FrameTrace-draw log_us over %d frames: median %d p99 %d p999 %d max %d; >= 100000: %d' % (
                len(srt), q(0.5), q(0.99), q(0.999), srt[-1], sum(1 for v in srt if v >= 100000)))
        base = None
        for k in ('W:vo_pace', 'W:flip_req'):
            print('objects %s %s' % (k, sorted(objs.get(k, {}).items())))
        vo = objs.get('W:vo_pace', {})
        if len(vo) == 1:
            base = int(list(vo)[0], 16)
        print('base (VideoOutDriver::Impl this = W:vo_pace obj) %s' % (hex(base) if base is not None else 'NOT UNIQUE'))
        for o in objs.get('W:flip_req', {}):
            off = int(o, 16) - base if base is not None else None
            print('W:flip_req obj %s offset %s name %s' % (o, hex(off) if off is not None else '-', NAMES.get(off, '?')))
        print('Present -t windows %d; Sw wait-reason histogram over them %s' % (pw, sorted(swr_present.items())))
        print('frames %d; with the chain %d; in count %d' % (len(frames), sum(fr['has_chain'] for fr in frames),
                                                               sum(fr['in_count'] for fr in frames)))
        for fr in frames:
            n = fr['n']
            tag_s = ('CHAIN ' if fr['has_chain'] else '') + ('IN_COUNT' if fr['in_count'] else '')
            print('FRAME %s n %d dt_us %d t %.1f | %s | %s | %s' % (tag, n, fr['dt_us'], fr['t'], tag_s or '-',
                                                                 fr['cls'], fr['chain']))
            h = hdr.get(n)
            if h:
                print('  hdr dt_us %s instr_us %s samples %s proc_us %s other_us %s kq %s' % (
                    h.get('dt_us'), h.get('instr_us'), h.get('samples'), h.get('proc_us'), h.get('other_us'), h.get('kq')))
            slot_role = {}
            for d in trows.get(n, []):
                slot_role[d['slot']] = '%s/%s' % (d.get('name'), d.get('role'))
            for d in trows.get(n, []):
                if d.get('role') in ('Present', 'Gpu') or d.get('name') == 'DrawThread':
                    print('  -t %s/%s R %s r %s Sr %s Sw %s S %s W %s H %s SwR %s cpu_us %s top %s last %s obj %s peer %s' % (
                        d.get('name'), d.get('role'), d['R'], d['r'], d['Sr'], d['Sw'], d['S'], d['W'], d['H'], d['SwR'],
                        d['cpu_us'], d['top'], d['last'], d['obj'], d['peer']))
            for d in sorted(wrows.get(n, []), key=lambda x: -int(x['wait_us'])):
                o = int(d['obj'], 16)
                off = o - base if base is not None else None
                name = NAMES.get(off, '?') if off is not None and 0 <= off < 0x2000 else 'outside Impl'
                print('  -w emu_mutex waiter %s(slot %s) obj %s off %s %s start_us %s wait_us %s waker %s(%s) peer %s(%s) open %s' % (
                    slot_role.get(d['slot'], '?'), d['slot'], d['obj'], hex(off) if off is not None and 0 <= off < 0x2000 else '-',
                    name, d['start_us'], d['wait_us'], d['waker'], slot_role.get(d['waker'], '?'), d['peer'],
                    slot_role.get(d['peer'], '?'), d['open']))
            hx = hold_x.get(n)
            print('  FrameTrace-x n=%d flip_hold_ns %s (hold of flip %d) flip_hold_n %s' % (
                n, hx[0] if hx else '-', n - 1, hx[1] if hx else '-'))
            lx = logx.get(n)
            print('  FrameTrace-draw n=%d logs %s log_us %s log_gpu_us %s' % ((n,) + (lx if lx else ('-', '-', '-'))))
            fh = fliphold.get(n - 1)
            print('  FlipHold flip=%d %s' % (n - 1, ('us %s present_us %s poll_us %s other_us %s' % (
                fh['us'], fh['present_us'], fh['poll_us'], fh['other_us'])) if fh else 'not printed'))
        print('FlipHold lines in the run %d: %s' % (len(fliphold), sorted(fliphold)))


if __name__ == '__main__':
    main()

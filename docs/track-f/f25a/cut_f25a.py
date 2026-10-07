#!/usr/bin/env python3
"""F25a RC1 (HPP-660, Probe Designer): print limits of KYTY_DIAG_B32 (F20j4) against the window length, measured [c] on the
F20l / F20l2 / F20l3 logs.  Per DiagB32 window n: dt_us, instr_us, samples, t_lines, w_lines (header); -t lines with must=1 / must=0;
-w lines; -x: lines_cut_w, ring_drop_w, and the window increments of the cumulative others_cut, w_cut, print_us (difference to the
previous -x line of the same log); print_us is a gauge (the time of the last report printed before this -x line,
f2307b02:src/common/diagB32.cpp:1253) - printed raw.  Limits of f2307b02:src/common/diagB32.h:57-60: kOthersCap 24, kMustCap 96, kWLinesCap 64, kCLines 8.
Usage: cut_f25a.py <out.txt> <out.json> <log> [<log> ...]"""
import hashlib
import json
import re
import statistics
import sys

KMUST, KOTH, KW = 96, 24, 64
KV = re.compile(rb'(\w+)=(-?\d+)')


def kv(line):
    return dict((k.decode(), int(v)) for k, v in KV.findall(line))


def scan(path):
    h = hashlib.sha256()
    wins = {}
    order = []
    prev = None
    with open(path, 'rb') as f:
        for line in f:
            h.update(line)
            i = line.find(b'DiagB32')
            if i < 0:
                continue
            s = line[i:]
            if s.startswith(b'DiagB32: mode='):
                continue
            if s.startswith(b'DiagB32: n='):
                d = kv(s)
                n = d['n']
                w = wins.setdefault(n, dict(n=n, t_must=0, t_oth=0, w_rec=0))
                for k in ('dt_us', 'instr_us', 'samples', 't_lines', 'w_lines', 'c_lines'):
                    w[k] = d.get(k)
                order.append(n)
            elif s.startswith(b'DiagB32-t: '):
                d = kv(s)
                w = wins.setdefault(d['n'], dict(n=d['n'], t_must=0, t_oth=0, w_rec=0))
                w['t_must' if d.get('must') == 1 else 't_oth'] += 1
            elif s.startswith(b'DiagB32-w: '):
                d = kv(s)
                w = wins.setdefault(d['n'], dict(n=d['n'], t_must=0, t_oth=0, w_rec=0))
                w['w_rec'] += 1
            elif s.startswith(b'DiagB32-x: '):
                d = kv(s)
                w = wins.setdefault(d['n'], dict(n=d['n'], t_must=0, t_oth=0, w_rec=0))
                for k in ('lines_cut', 'lines_cut_w', 'ring_drop_w', 'print_us'):
                    w[k] = d.get(k)
                for k in ('others_cut', 'w_cut'):
                    v = d.get(k)
                    w[k + '_d'] = None if v is None else (v - (prev or {}).get(k, 0))
                prev = d
    return h.hexdigest(), [wins[n] for n in order if n in wins]


def main():
    out_txt, out_json, logs = sys.argv[1], sys.argv[2], sys.argv[3:]
    res = {}
    lines = []
    allw = []
    ok = True
    for p in logs:
        sha, ws = scan(p)
        tag = re.sub(r'^.*log_|\.txt$', '', p)
        res[tag] = dict(sha256=sha, windows=ws)
        for w in ws:
            w['tag'] = tag
        allw += ws
        if not ws:
            lines.append('%-10s windows 0  sha256 %s' % (tag, sha))
            continue
        cnt = lambda k: sum(1 for w in ws if (w.get(k) or 0) > 0)
        lines.append('%-10s windows %5d  max t_must %3d  max t_lines %3d  max w_rec %4d  windows with: lines_cut_w>0 %d, others_cut_d>0 %d,'
                     ' w_cut_d>0 %d, ring_drop_w>0 %d  sha256 %s' % (
                         tag, len(ws), max(w['t_must'] for w in ws), max(w.get('t_lines') or 0 for w in ws),
                         max(w['w_rec'] for w in ws), cnt('lines_cut_w'), cnt('others_cut_d'), cnt('w_cut_d'), cnt('ring_drop_w'), sha))
        # self-checks: header counts = printed lines; t_must <= kMustCap; t_oth <= kOthersCap; w_rec > kWLinesCap only with w_cut_d = 0
        for w in ws:
            if w.get('t_lines') is not None and w['t_lines'] != w['t_must'] + w['t_oth']:
                ok = False
                lines.append('  CHECK FAIL t_lines n=%d' % w['n'])
            if w.get('w_lines') is not None and w['w_lines'] != w['w_rec']:
                ok = False
                lines.append('  CHECK FAIL w_lines n=%d' % w['n'])
            if w['t_must'] > KMUST or w['t_oth'] > KOTH:
                ok = False
                lines.append('  CHECK FAIL caps n=%d' % w['n'])
            if (w.get('w_cut_d') or 0) > 0 and w['w_rec'] < KW:
                ok = False
                lines.append('  CHECK FAIL w_cut with w_rec < 64 n=%d' % w['n'])
    lines.append('')
    bins = [(1e5, 2e5), (2e5, 5e5), (5e5, 1e6), (1e6, 2.6e6), (2.6e6, 1e9)]
    lines.append('by window dt_us (all logs): bin | windows | t_must med/max | t_oth med/max | w_rec med/max | w_rec+w_cut_d max |'
                 ' w_cut_d>0 | others_cut_d>0 | lines_cut_w>0 | instr_us/dt max')
    for lo, hi in bins:
        b = [w for w in allw if w.get('dt_us') is not None and lo <= w['dt_us'] < hi]
        if not b:
            lines.append('[%.1f; %.1f) s | 0' % (lo / 1e6, hi / 1e6))
            continue
        med = lambda k: statistics.median(w.get(k) or 0 for w in b)
        mx = lambda k: max(w.get(k) or 0 for w in b)
        lines.append('[%.1f; %.1f) s | %d | %g/%d | %g/%d | %g/%d | %d | %d | %d | %d | %.3f' % (
            lo / 1e6, hi / 1e6, len(b), med('t_must'), mx('t_must'), med('t_oth'), mx('t_oth'), med('w_rec'), mx('w_rec'),
            max(w['w_rec'] + (w.get('w_cut_d') or 0) for w in b), sum(1 for w in b if (w.get('w_cut_d') or 0) > 0),
            sum(1 for w in b if (w.get('others_cut_d') or 0) > 0), sum(1 for w in b if (w.get('lines_cut_w') or 0) > 0),
            max((w.get('instr_us') or 0) / w['dt_us'] for w in b)))
    lines.append('')
    lines.append('windows dt_us >= 500 000: tag n dt_us instr_us t_must t_oth w_rec w_cut_d others_cut_d lines_cut_w ring_drop_w')
    for w in sorted((w for w in allw if (w.get('dt_us') or 0) >= 500000), key=lambda w: -w['dt_us']):
        lines.append('%s %d %d %d %d %d %d %s %s %s %s' % (w['tag'], w['n'], w['dt_us'], w.get('instr_us') or 0, w['t_must'], w['t_oth'],
                                                        w['w_rec'], w.get('w_cut_d'), w.get('others_cut_d'), w.get('lines_cut_w'),
                                                        w.get('ring_drop_w')))
    lines.append('')
    lines.append('print cost [c]: print_us at window k (gauge, the last report printed before it) against the lines of window k-1 of the'
                 ' same log (1 header + t_lines + w_lines + c_lines + 1 -x); pairs without another window between them')
    per = []
    for tag in res:
        ws = res[tag]['windows']
        for a2, b2 in zip(ws, ws[1:]):
            if b2.get('print_us') is None or a2.get('t_lines') is None:
                continue
            nl = 2 + a2['t_lines'] + a2['w_lines'] + (a2.get('c_lines') or 0)
            per.append(b2['print_us'] / nl)
            lines.append('  %s n %d -> n %d: lines %d, print_us %d, us/line %.2f' % (tag, a2['n'], b2['n'], nl, b2['print_us'],
                                                                                b2['print_us'] / nl))
    if per:
        lines.append('  pairs %d, us/line median %.2f, max %.2f' % (len(per), statistics.median(per), max(per)))
    lines.append('')
    lines.append('SELF-CHECKS ' + ('ALL OK' if ok else 'FAILED'))
    with open(out_txt, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    with open(out_json, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(res, f)
    print('\n'.join(lines[-40:]))


if __name__ == '__main__':
    main()

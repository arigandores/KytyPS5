#!/usr/bin/env python3
"""rt_s3r.py - Red Team, track S link S3r (HPP-314): an independent recount of the S3 regression on sc142 logs.
No import of sc_s.py / sc142.py.  Streaming, binary mode.  ASCII output.
Definitions (ROADMAP item 241 (v)(1)-(3), item 221 (v)):
  main row = line starting 'FrameTrace: n=' with dt_us; group of an event line = index of the NEXT main row;
  first scene frame = first main row with draws >= 100 after 'GuestOut: Level has started: <level>';
  end = group of the next 'Level has started' line or the number of rows; window = rows fi+1 .. fi+599 (WIN), hold = the rest;
  held flips = sum skc_held_inc of FrameTrace-x; series (reading 2) = maximal runs of held rows from fi+1, gap = sum dt of
  the run + dt of the closing row; PCW frame = row dt >= 100 ms after fi with 'Vulkan pipeline cache: saved' or
  'PipelinePrecache: saved' in group i or i+1.
    python rt_s3r.py <tag> ...
"""
import hashlib
import json
import re
import sys

WIN = 599          # sc142.ENTRY_WIN / S0 1.3: the window = 599 rows after the first scene frame
RX_N = re.compile(rb'^FrameTrace: n=(\d+) ')
RX_XN = re.compile(rb'^FrameTrace-x: n=(\d+) ')


def num(line, key):
    m = re.search(rb' ' + key + rb'=(\d+)', line)
    return int(m.group(1)) if m else None


def one(tag):
    js = json.load(open('C:/kyty/s142/%s.json' % tag, encoding='utf-8'))
    level = js.get('level') or js['guest_args'].split()[-1]
    rows = []          # (n, dt, draws)
    x = {}             # n -> (ap_skip, held_inc)
    starts = []        # (group, name)
    skips = []         # (group, frame, vs, ps)
    saves = []         # (group, kind)
    h = hashlib.sha256()
    with open('C:/kyty/s142/log_%s.txt' % tag, 'rb') as f:
        for line in f:
            h.update(line)
            g = len(rows)
            m = RX_N.match(line)
            if m:
                dt = num(line, b'dt_us')
                if dt is not None:
                    rows.append((int(m.group(1)), dt, num(line, b'draws') or 0))
                continue
            m = RX_XN.match(line)
            if m:
                x[int(m.group(1))] = (num(line, b'skc_ap_skip') or 0, num(line, b'skc_held_inc') or 0)
                continue
            if line.startswith(b'GuestOut: Level has started:'):
                starts.append((g, line.split(b':', 2)[2].strip().decode('latin1')))
            elif line.startswith(b'AsyncPipelines: skipped draw'):
                m = re.search(rb'frame=(\d+) vs=0x([0-9a-fA-F]+) ps=0x([0-9a-fA-F]+)', line)
                skips.append((g, int(m.group(1)) if m else None, m.group(2).lower().zfill(16) if m else None,
                              m.group(3).lower().zfill(16) if m else None))
            elif line.startswith(b'Vulkan pipeline cache: saved'):
                saves.append((g, 'drv'))
            elif line.startswith(b'PipelinePrecache: saved'):
                saves.append((g, 'rec'))
    si = [i for i, (g, nm) in enumerate(starts) if nm == level][0]
    eg = starts[si][0]
    end = starts[si + 1][0] if si + 1 < len(starts) else len(rows)
    fi = next(i for i in range(eg, end) if rows[i][2] >= 100)

    def hi(i):
        return x.get(rows[i][0], (0, 0))[1]

    def sk(i):
        return x.get(rows[i][0], (0, 0))[0]
    wend = fi + 1 + WIN
    part = {}
    for name, a, b in (('win', fi + 1, min(wend, end)), ('hold', wend, end)):
        r = range(a, b)
        part[name] = (sum(1 for i in r if sk(i) > 0), sum(hi(i) for i in r), sum(1 for i in r if rows[i][1] >= 100000))
    ser = []
    i = fi + 1
    while i < end:
        if hi(i) > 0:
            j = i
            while j < end and hi(j) > 0:
                j += 1
            gap = sum(rows[k][1] for k in range(i, j)) + (rows[j][1] if j < end else 0)
            ser.append((rows[i][0], rows[j - 1][0], gap))
            i = j
        else:
            i += 1
    t6_frames = len(set(e[1] for e in skips if e[1] is not None))
    t6_held = sum(v[1] for v in x.values())
    pairs = len(set((e[2], e[3]) for e in skips if e[0] > fi and e[2]))
    pcw = []
    for i in range(fi + 1, end):
        if rows[i][1] >= 100000:
            ks = sorted(set(k for g, k in saves if g in (i, i + 1)))
            if ks:
                pcw.append((rows[i][0], '+'.join(ks)))
    std = 0
    try:
        with open('C:/kyty/s142/stdout_%s.txt' % tag, 'rb') as f:
            std = sum(1 for line in f if line.startswith(b'Shaders: VS'))
    except OSError:
        std = None
    return dict(tag=tag, level=level, sha=h.hexdigest()[:16], first_n=rows[fi][0], first_held=int(hi(fi) > 0),
                win=part['win'], hold=part['hold'], skip_lines=len(skips), pairs=pairs, series=len(ser),
                max_gap_ms=round(max([s[2] for s in ser] or [0]) / 1000.0, 1),
                gap100=sum(1 for s in ser if s[2] >= 100000), gap1s=sum(1 for s in ser if s[2] >= 1000000),
                stdout_shaders=std, t6=(t6_frames, t6_held), pcw=pcw)


if __name__ == '__main__':
    for t in sys.argv[1:]:
        r = one(t)
        print('%s level %s log %s: first n %d held %d; window skip/held/>=100 %s; hold %s; skipped-draw lines %d; '
              'pairs after first %d; series(r2) %d max %.1f ms, >=100 ms %d, >=1 s %d; stdout Shaders %s; T-6 %d/%d; '
              'PCW frames %s' % (r['tag'], r['level'], r['sha'], r['first_n'], r['first_held'], r['win'], r['hold'],
                                 r['skip_lines'], r['pairs'], r['series'], r['max_gap_ms'], r['gap100'], r['gap1s'],
                                 r['stdout_shaders'], r['t6'][0], r['t6'][1], r['pcw']))

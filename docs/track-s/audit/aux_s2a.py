# S2a (HPP-312), Session Auditor. Auxiliary own recount (binary streaming, no shared code):
#  (A) sum of skc_ap_skip after the first scene frame, without and with the first scene frame row
#      (S0 says 2 817, the lead's s0chk.out.txt says 3 110 - p.235(a) does not name the field);
#  (B) p.241(b)(5): frames dt >= 100 ms with a "Vulkan pipeline cache: saved ... (N us)" line in the group, dt - us.
import sys, re, bisect

RE_FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+) .*? draws=(\d+) ')
RE_SK = re.compile(rb' skc_ap_skip=(\d+)')
RE_HI = re.compile(rb' skc_held_inc=(\d+)')
RE_SAVED = re.compile(rb'Vulkan pipeline cache: saved (\d+) bytes .*\((\d+) us\)')

tot_excl = tot_incl = 0
pcw_rows = []
for t in range(1, 11):
    tag = 'c142_%02d' % t
    frames = []
    saves = []
    entry = None
    with open('C:/kyty/s142/log_%s.txt' % tag, 'rb') as f:
        for i, l in enumerate(f, 1):
            if l.startswith(b'FrameTrace: '):
                m = RE_FT.match(l)
                if m:
                    frames.append([i, int(m.group(1)), int(m.group(2)), int(m.group(3)), 0, 0])
            elif l.startswith(b'FrameTrace-x: ') and frames:
                a = RE_SK.search(l)
                b = RE_HI.search(l)
                frames[-1][4] = int(a.group(1)) if a else 0
                frames[-1][5] = int(b.group(1)) if b else 0
            elif b'pipeline cache: saved' in l:
                m = RE_SAVED.search(l)
                if m:
                    saves.append((i, int(m.group(1)), int(m.group(2))))
            elif entry is None and b'Level has started: ' in l and l.split(b'Level has started: ', 1)[1].strip():
                entry = i
    first = next(k for k, fr in enumerate(frames) if fr[0] > entry and fr[3] >= 100)
    excl = sum(fr[4] for fr in frames[first + 1:])
    incl = excl + frames[first][4]
    held_after = sum(fr[5] for fr in frames[first + 1:])
    tot_excl += excl
    tot_incl += incl
    print('%s first n=%d first_row_skip=%d first_row_held_inc=%d skip_sum_after_excl=%d incl=%d held_inc_after=%d' % (
        tag, frames[first][1], frames[first][4], frames[first][5], excl, incl, held_after))
    lines = [fr[0] for fr in frames]
    for (ln, nbytes, us) in saves:
        j = bisect.bisect_left(lines, ln)       # next main row after the saved line = frame i ("next" convention)
        if j <= first or j >= len(frames):
            continue
        for k, name in ((j, 'i'), (j - 1, 'i-1 (saved line in group i+1 of this frame)')):
            fr = frames[k]
            if k > first and fr[2] >= 100000:
                part = 'win' if k - first <= 599 else 'hold'
                pcw_rows.append((tag, fr[1], part, fr[2], us, fr[2] - us, name, ln, nbytes))
print('TOTAL skc_ap_skip after first scene frame: excl first row %d, incl first row %d, diff %d' % (tot_excl, tot_incl, tot_incl - tot_excl))
print('-- frames >= 100 ms with a driver cache save line in group i or i+1 (after the first scene frame)')
for r in pcw_rows:
    print('%s n=%d %s dt=%d save_us=%d dt-us=%d group=%s save_line=%d bytes=%d' % r)
print('count', len(pcw_rows), 'all dt-us < 100000:', all(r[5] < 100000 for r in pcw_rows))

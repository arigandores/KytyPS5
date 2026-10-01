#!/usr/bin/env python3
# S1 (Red Team, HPP-295): driver-cache / recipe writes vs frames >= 100 ms and held series (own code).
import re, json, sys
TAGS = ['v142'] + ['c142_%02d' % i for i in range(1, 11)]
RX_SAVE = re.compile(rb'Vulkan pipeline cache: saved (\d+) bytes .*?\((\d+) us\)')
RX_REC = re.compile(rb'PipelinePrecache: saved (\d+) recipes')
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
RX_X = re.compile(rb'FrameTrace-x: n=(\d+) .*?skc_held_inc=(\d+)')
RX_LVL = re.compile(rb'GuestOut: Level has started: (\S+)')
RX_DR = re.compile(rb'FrameTrace: n=\d+ .*? draws=(\d+)')
res = []
for tag in TAGS:
    rows = []; held = {}; saves = []; recs = []; lvl_row = None
    with open('C:/kyty/s142/log_%s.txt' % tag, 'rb') as f:
        for line in f:
            if b'FrameTrace: n=' in line:
                m = RX_FT.search(line); d = RX_DR.search(line)
                rows.append((int(m.group(1)), int(m.group(2)), int(d.group(1)) if d else 0))
            elif b'FrameTrace-x: n=' in line:
                m = RX_X.search(line)
                if m: held[int(m.group(1))] = int(m.group(2))
            elif b'Vulkan pipeline cache: saved' in line:
                m = RX_SAVE.search(line)
                if m: saves.append((len(rows), int(m.group(1)), int(m.group(2))))
            elif b'PipelinePrecache: saved' in line:
                m = RX_REC.search(line)
                if m: recs.append((len(rows), int(m.group(1))))
            elif lvl_row is None and RX_LVL.search(line):
                lvl_row = len(rows)
    fi = next(i for i in range(lvl_row, len(rows)) if rows[i][2] >= 100)
    after = [s for s in saves if s[0] > fi]
    f100 = [i for i in range(fi + 1, len(rows)) if rows[i][1] >= 100000]
    hit = []
    for i in f100:
        near = [s for s in saves if s[0] in (i, i + 1)]  # save line printed before row i (group i) or before row i+1
        if near:
            hit.append((rows[i][0], rows[i][1], near[0][2]))
    hrows = [i for i in range(fi + 1, len(rows)) if held.get(rows[i][0], 0) > 0]
    save_in_held = [s for s in after if s[0] in set(hrows) or s[0] - 1 in set(hrows)]
    r = {'tag': tag, 'saves_total': len(saves), 'saves_after_first': len(after),
         'save_us_after': [s[2] for s in after], 'recipe_saves_after': len([x for x in recs if x[0] > fi]),
         'frames100_with_save_in_group_i_or_i+1': hit, 'saves_in_held_series': len(save_in_held)}
    res.append(r)
    print(json.dumps(r)); sys.stdout.flush()
json.dump(res, open('C:/kyty/s288/s1/rt_s1b.json', 'w'), indent=0)

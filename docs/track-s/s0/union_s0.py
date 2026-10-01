#!/usr/bin/env python3
"""union_s0.py - S0 (HPP-294): the S-warm reference of item 229 (d)(1) per level from the logs (streaming, binary):
U = rows of the entry window (599 rows after the first scene frame) that have skipped draws (skc_ap_skip > 0) or are a
held flip (skc_held_inc > 0) or have dt >= 100 ms; and identities of the counters against the log lines."""
import re, sys
S142 = 'C:/kyty/s142'
LV = dict(v142='underwater_aerial_garden', w142='underwater_aerial_garden', c142_01='bumper_enemy_snowy_canyon',
          c142_02='big_hand_pirate_island', c142_03='timestop_casino', c142_04='mini_giants_garden', c142_05='ice_iceberg',
          c142_06='sponge_dirty_bath', c142_07='hoover_beach', c142_08='volcano_mountain', c142_09='voxel_world',
          c142_10='enemy_gorilla')
RXM = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+).* draws=(\d+)')
RXS = re.compile(rb' skc_ap_skip=(\d+)')
RXH = re.compile(rb' skc_held_inc=(\d+)')
ok = True
print('tag first_n | window: U skip_or_held k3k2 both | all rows: sum skc_ap_skip, skip lines, sum skc_held_inc, held lines (cap 64) | identities')
for tag, level in LV.items():
    rows = []; ent = None; skl = 0; hl = 0; cur = None
    with open('%s/log_%s.txt' % (S142, tag), 'rb') as f:
        for line in f:
            if line.startswith(b'FrameTrace: n='):
                m = RXM.match(line)
                cur = [int(m.group(1)), int(m.group(2)), int(m.group(3)), 0, 0, ent is not None]
                rows.append(cur)
            elif line.startswith(b'FrameTrace-x: n='):
                s = RXS.search(line); h = RXH.search(line)
                if cur is not None:
                    cur[3] = int(s.group(1)) if s else 0
                    cur[4] = int(h.group(1)) if h else 0
            elif line.startswith(b'AsyncPipelines: skipped draw'):
                skl += 1
            elif line.startswith(b'AsyncPipelines: flip'):
                hl += 1
            elif ent is None and line.startswith(b'GuestOut: Level has started: ') and line[29:].strip() == level.encode():
                ent = len(rows)
    fi = next(i for i in range(ent, len(rows)) if rows[i][2] >= 100)
    win = rows[fi + 1:fi + 600]
    a = sum(1 for r in win if r[3] > 0 or r[4] > 0)
    b = sum(1 for r in win if r[1] >= 100000)
    both = sum(1 for r in win if (r[3] > 0 or r[4] > 0) and r[1] >= 100000)
    u = sum(1 for r in win if r[3] > 0 or r[4] > 0 or r[1] >= 100000)
    ss = sum(r[3] for r in rows); sh = sum(r[4] for r in rows)
    i1 = ss == skl; i2 = min(64, sh) == hl
    ok &= i1 and i2
    print('%s %d | %d %d %d %d | %d %d %d %d | skip %s held %s' % (tag, rows[fi][0], u, a, b, both, ss, skl, sh, hl,
                                                                'OK' if i1 else 'DIFF', 'OK' if i2 else 'DIFF'))
print('ALL OK' if ok else 'IDENTITY DIVERGENCE')

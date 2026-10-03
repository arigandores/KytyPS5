# F9f2 (HPP-430, Red Team): model of the KYTY_FIX_B42 state of 2da00d80 for one target T6 (960x540, layers=1, view layer 0).
# Transcribes only the statements named below; no game, no emulator.
#   TrackDccFill       textureCache.cpp:3229-3241 (2da00d80): fill 0 -> clear_mask = UINT32_MAX (PendingDcc: dcc_clear_mask of
#                      code 0x00, :3216; CMask: :3231); fill_value, fill_size, b42_fill_seq = ++seq.
#   PrepareCmaskClear  :1987-1992 (PendingDcc -> CMask, mask kept for fill 0), :2002 (skip if mask == 0),
#                      :2009-2013 (only the view layers; T6: layer 0 -> bits 1..31 stay set).
#   FixB42Probe        descriptors.cpp:3666-3680 (armed: PendingDcc or CMask with clear_mask != 0; rearm = cmask);
#   applied            descriptors.cpp:3768-3771 ((before & ~after) != 0); counters :3702-3712.
import sys

U32 = 0xFFFFFFFF


def model(events, fix_on=True):
    seq = 0
    draw_seq = 0
    entry = None  # [type, clear_mask, fill_value, fill_size, b42_fill_seq]
    hit = applied = rearm = drawn = 0
    lines = []
    for ev in events:
        if ev == 'fill':
            if entry is None:
                entry = ['PendingDcc', 0, U32, 0, 0]
            seq += 1
            entry[1:] = [U32, 0, 0x2000, seq]
            lines.append('fill: clear_mask=0x%08x' % entry[1])
        elif ev == 'draw':
            seq += 1
            draw_seq = seq
            lines.append('draw')
        elif ev == 'fce':
            if entry is None:
                continue
            was_cmask = entry[0] == 'CMask'
            armed = entry[0] == 'PendingDcc' or (was_cmask and entry[1] != 0)
            if not (armed and entry[2] == 0 and entry[3] >= 960 * 540 // 128):
                lines.append('fce: none')
                continue
            if draw_seq > entry[4]:
                drawn += 1
                lines.append('fce: drawn=%d' % drawn)
                continue
            before = entry[1]
            app = False
            if fix_on:
                entry[0] = 'CMask'
                if entry[1] & 1:  # layer 0 only
                    entry[1] &= ~1 & U32
                app = (before & ~entry[1] & U32) != 0
            hit += 1
            rearm += 1 if was_cmask else 0
            applied += 1 if app else 0
            lines.append('fce: hit=%d applied=%d rearm=%d clear_mask=0x%08x' % (hit, applied, rearm, entry[1]))
    return hit, applied, rearm, drawn, lines


ok = True
cases = [
    ('S1 =1: fill, FCE x4 (FCE each frame, one fill per layout change)', ['fill', 'fce', 'fce', 'fce', 'fce'], (4, 1, 3, 0)),
    ('S2 =1: fill, FCE, re-fill, FCE (the RC2 case of F9f)', ['fill', 'fce', 'fill', 'fce'], (2, 2, 1, 0)),
    ('S3 =1: fill, FCE, draw, FCE (no re-fill)', ['fill', 'fce', 'draw', 'fce'], (1, 1, 0, 1)),
]
for name, ev, want in cases:
    got = model(ev)
    print(name)
    for l in got[4]:
        print('   ', l)
    print('    total hit=%d applied=%d rearm=%d drawn=%d; hit-applied=%d' % (got[0], got[1], got[2], got[3], got[0] - got[1]))
    ok &= got[:4] == want
print('MODEL', 'AS EXPECTED' if ok else 'UNEXPECTED')
sys.exit(0 if ok else 1)

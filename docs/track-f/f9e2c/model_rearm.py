# F9e2c (HPP-436, ROADMAP s122 item 357(g)(3)): model of the KYTY_FIX_B42 state for one target T6 (960x540, layers=1,
# FCE view base_level 0, base_layer 0, layer_count 1) - the form of model_rearm.py of F9f2 (4256e8cf:docs/track-f/f9f2/),
# adapted to F9e2c. Transcribes only the statements named below; no game, no emulator.
#   TrackDccFill       textureCache.cpp:3229-3241 (2da00d80, unchanged by F9e2c): fill 0 -> clear_mask = UINT32_MAX
#                      (PendingDcc: :3216; CMask: :3231); fill_value, fill_size, b42_fill_seq = ++seq.
#   draw-path acquire  textureCache.cpp:2362-2364: b42_draw_seq[id] = ++seq.
#   PrepareCmaskClear  :1987-1992 (PendingDcc -> CMask, mask kept for fill 0), :2002 (skip if mask == 0),
#                      :2008 (bad view: return), :2009-2013 (only the view layers; T6: layer 0).
#   FixB42Probe        descriptors.cpp:3670-3677 (0b9dc0c9): layer_bits of the view; armed = PendingDcc or
#                      CMask with (clear_mask & layer_bits) != 0; :3678 (fill_value 0, fill_size >= w*h*layers/128);
#                      :3683-3686 drawn (draw_seq > fill_seq, descriptor untouched -> no FindRenderTarget with CMask
#                      metadata, the entry stays as it is); :3687-3688 hit, rearm = cmask.
#   applied            descriptors.cpp:3777-3780 ((before & ~after) != 0); counters :3710-3721.
# member='f9e2b' gives the arming of 2da00d80 (clear_mask != 0) for reference.
import sys

U32 = 0xFFFFFFFF


def layer_bits(base_level, base_layer, layer_count):
    # descriptors.cpp:3673-3676 (0b9dc0c9)
    view_ok = base_level == 0 and base_layer < 32 and layer_count <= 32 - base_layer
    if not view_ok:
        return 0
    return ((U32 if layer_count >= 32 else (1 << layer_count) - 1) << base_layer) & U32


def model(events, fix_on=True, member='f9e2c', view=(0, 0, 1)):
    seq = 0
    draw_seq = 0
    entry = None  # [type, clear_mask, fill_value, fill_size, b42_fill_seq]
    hit = applied = rearm = drawn = 0
    lines = []
    bits = layer_bits(*view)
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
            if member == 'f9e2c':
                armed = entry[0] == 'PendingDcc' or (was_cmask and (entry[1] & bits) != 0)
            else:
                armed = entry[0] == 'PendingDcc' or (was_cmask and entry[1] != 0)
            if not (armed and entry[2] == 0 and entry[3] >= 960 * 540 // 128):
                lines.append('fce: none (clear_mask=0x%08x)' % entry[1])
                continue
            if draw_seq > entry[4]:
                drawn += 1
                lines.append('fce: drawn=%d' % drawn)
                continue
            before = entry[1]
            app = False
            if fix_on:
                entry[0] = 'CMask'  # :1987-1992, fill 0 keeps the mask
                if entry[1] != 0 and bits:  # :2002, :2008
                    for layer in range(32):
                        if bits >> layer & 1 and entry[1] >> layer & 1:  # :2009-2013
                            entry[1] &= ~(1 << layer) & U32
                app = (before & ~entry[1] & U32) != 0
            hit += 1
            rearm += 1 if was_cmask else 0
            applied += 1 if app else 0
            lines.append('fce: hit=%d applied=%d rearm=%d clear_mask=0x%08x' % (hit, applied, rearm, entry[1]))
    return hit, applied, rearm, drawn, lines


ok = True
cases = [
    ('S1 =1: fill, FCE x4', ['fill', 'fce', 'fce', 'fce', 'fce'], {}, (1, 1, 0, 0)),
    ('S2 =1: fill, FCE, re-fill, FCE', ['fill', 'fce', 'fill', 'fce'], {}, (2, 2, 1, 0)),
    ('S3 =1: fill, FCE, draw, FCE', ['fill', 'fce', 'draw', 'fce'], {}, (1, 1, 0, 0)),
    ('S4 =1: fill, draw, FCE', ['fill', 'draw', 'fce'], {}, (0, 0, 0, 1)),
    ('ref S1 =1 with the F9e2b member (2da00d80, RC1 of F9f2)', ['fill', 'fce', 'fce', 'fce', 'fce'], {'member': 'f9e2b'},
     (4, 1, 3, 0)),
    ('ref S1 =0: no CMask entry, every FCE is a hit (p.353(d) N2)', ['fill', 'fce', 'fce', 'fce', 'fce'], {'fix_on': False},
     (4, 0, 0, 0)),
]
for name, ev, kw, want in cases:
    got = model(ev, **kw)
    print(name)
    for l in got[4]:
        print('   ', l)
    good = got[:4] == want
    print('    total hit=%d applied=%d rearm=%d drawn=%d; want hit=%d applied=%d rearm=%d drawn=%d -> %s' %
          (got[:4] + want + ('OK' if good else 'FAIL',)))
    ok &= good
# layer_bits edges (descriptors.cpp:3673-3676)
edges = [((0, 0, 1), 0x1), ((0, 0, 32), U32), ((0, 31, 1), 0x80000000), ((0, 1, 31), 0xFFFFFFFE), ((1, 0, 1), 0),
         ((0, 32, 1), 0), ((0, 31, 2), 0), ((0, 0, 0), 0)]
for v, want in edges:
    got = layer_bits(*v)
    good = got == want
    print('layer_bits(base_level=%d, base_layer=%d, layer_count=%d) = 0x%08x want 0x%08x -> %s' %
          (v + (got, want, 'OK' if good else 'FAIL')))
    ok &= good
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)

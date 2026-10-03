# F9f3 (HPP-437, Red Team): own model of KYTY_FIX_B42 after F9e2c (ROADMAP s122 item 357(g)(1)-(3)).
# Independent of docs/track-f/f9e2c/model_rearm.py: written from the code lines, not from that model.
# Code transcribed (0b9dc0c9; textureCache.cpp unchanged since 2da00d80):
#   A. FixB42Probe            descriptors.cpp:3663-3689 (early exits :3663-3667, size :3668, armed :3672-3677,
#                             gate :3678, drawn :3683-3686, hit/rearm :3687-3688)
#   B. FCE branch             descriptors.cpp:3752-3784 (desc edit only on Hit && ON :3753-3757; FindRenderTarget
#                             only if metadata kind Cmask :3758; applied :3777-3780)
#   C. PrepareCmaskClear      textureCache.cpp:1960-2021 (PendingDcc->CMask :1985-1992, gate :2002-2003,
#                             view gate :2008, loop :2009-2014)
#   D. TrackDccFill           textureCache.cpp:3227-3241 (mask for fill 0: UINT32_MAX both kinds; b42_fill_seq)
#   E. FindRenderTarget       textureCache.cpp:2362-2364 (draw stamp only when !fce_materialize); the draw path of a
#                             non-1024 target passes metadata kind None -> PrepareCmaskClear exits at :1965.
# Part 1: exhaustive equivalence "probe armed (CMask entry)" <=> "PrepareCmaskClear clears >= 1 layer" over views
#         and masks (fill_value 0, sizes ok, decode ok - the other gates are shared or outside the member).
# Part 2: the event model S1-S4 (item 357(g)(3)) + extra cases; invariants over random sequences.
import random
import sys

U32 = 0xFFFFFFFF


def c_sub(a, b):  # uint32 arithmetic of "32 - view.base_layer"
    return (a - b) & U32


def probe_layer_bits(base_level, base_layer, layer_count):
    # descriptors.cpp:3673-3676, C++ precedence: !view_ok ? 0u : ((cnt >= 32 ? UINT32_MAX : (1u << cnt) - 1u) << base)
    view_ok = base_level == 0 and base_layer < 32 and layer_count <= c_sub(32, base_layer)
    if not view_ok:
        return 0
    low = U32 if layer_count >= 32 else ((1 << layer_count) - 1) & U32
    assert base_layer < 32 and (layer_count < 32 or base_layer == 0)  # no UB shift on this branch
    return (low << base_layer) & U32


def probe_armed_cmask(clear_mask, view):
    return (clear_mask & probe_layer_bits(*view)) != 0  # :3677, CMask half


def prepare_cmask_clear_consumes(clear_mask, view):
    # textureCache.cpp:2002 (mask 0 -> return), :2008, :2009-2013; returns the consumed bits
    base_level, base_layer, layer_count = view
    if clear_mask == 0:
        return 0
    if base_level != 0 or base_layer >= 32 or layer_count > c_sub(32, base_layer):
        return 0
    consumed = 0
    layer = base_layer
    while layer < base_layer + layer_count:
        if clear_mask & (1 << layer):
            consumed |= 1 << layer
        layer += 1
    return consumed


ok = True

# ---- Part 1
vals = list(range(0, 36)) + [63, 64, 0x7FFFFFFF, 0xFFFFFFFE, U32]
masks = [0, 1, 2, 0x80000000, 0xFFFFFFFE, U32, 0x55555555, 0xAAAAAAAA, 0x0000FFFF, 0xFFFF0000]
rnd = random.Random(357)
masks += [rnd.getrandbits(32) for _ in range(40)]
n = bad = 0
for lvl in (0, 1, 2, U32):
    for bl in vals:
        for lc in vals:
            v = (lvl, bl, lc)
            for m in masks:
                n += 1
                a = probe_armed_cmask(m, v)
                c = prepare_cmask_clear_consumes(m, v) != 0
                if a != c:
                    bad += 1
                    if bad <= 5:
                        print('MISMATCH view=%r mask=0x%08x armed=%s clears=%s' % (v, m, a, c))
print('part1: %d (view, mask) cases, mismatches %d -> %s' % (n, bad, 'OK' if bad == 0 else 'FAIL'))
ok &= bad == 0

# ---- Part 2
W, H, LAYERS = 960, 540, 1
SIZE = W * H * LAYERS // 128  # :3668


class Sim:
    def __init__(self, fix_on):
        self.on = fix_on
        self.seq = 0
        self.draw_seq = 0        # m_b42_draw_seq of the image (0 = no stamp)
        self.entry = None        # dict: type, mask, fill_value, fill_size, fseq
        self.c = dict(hit=0, applied=0, drawn=0, rearm=0)
        self.notes = []

    def fill(self, value=0, size=0x2000):  # D
        if self.entry is None:
            self.entry = dict(type='PendingDcc', mask=0, fill_value=0, fill_size=0, fseq=0)
        e = self.entry
        if e['type'] == 'CMask':
            e['mask'] = U32 if value == 0 else 0
        else:  # PendingDcc: dcc_clear_mask of a repeated byte code
            code = value & 0xFF
            e['mask'] = U32 if (value == code * 0x01010101 and code in (0, 0x20, 0x40, 0x80, 0xC0)) else 0
        e['fill_value'] = value
        e['fill_size'] = size
        self.seq += 1
        e['fseq'] = self.seq

    def draw(self):  # E: draw-path FindRenderTarget, metadata None -> no PrepareCmaskClear effect
        self.seq += 1
        self.draw_seq = self.seq

    def fce(self, view=(0, 0, 1)):
        e = self.entry
        if e is None:  # QueryMetaFill: !found
            return 'none'
        pending = e['type'] == 'PendingDcc'
        cmask = e['type'] == 'CMask'
        armed = pending or (cmask and (e['mask'] & probe_layer_bits(*view)) != 0)  # :3677
        if SIZE == 0 or not armed or e['fill_value'] != 0 or e['fill_size'] < SIZE:  # :3678
            return 'none'
        before = e['mask']  # probe.clear_mask :3682
        if self.draw_seq > e['fseq']:  # :3683
            self.c['drawn'] += 1
            return 'drawn'
        rearm = cmask  # :3688
        applied = False
        if self.on:  # B: desc gets Cmask metadata -> FindRenderTarget -> C
            if e['type'] == 'PendingDcc':  # :1985-1992 (no stale reset modelled), fill 0 keeps the mask
                e['type'] = 'CMask'
                if e['fill_value'] != 0:
                    e['mask'] = 0
            if not (e['fill_value'] != 0 or e['mask'] == 0 or SIZE == 0 or e['fill_size'] < SIZE):  # :2002-2003
                e['mask'] &= ~prepare_cmask_clear_consumes(e['mask'], view) & U32  # :2008-2013
            after = e['mask']
            applied = e['type'] == 'CMask' and e['fill_value'] == 0 and (before & ~after & U32) != 0  # :3779-3780
        self.c['hit'] += 1
        self.c['rearm'] += 1 if rearm else 0
        self.c['applied'] += 1 if applied else 0
        return 'hit'


def run(events, fix_on=True):
    s = Sim(fix_on)
    for ev in events:
        if isinstance(ev, tuple):
            getattr(s, ev[0])(*ev[1:])
        else:
            getattr(s, ev)()
    return s.c


req = [
    ('S1 fill, FCE x4', ['fill', 'fce', 'fce', 'fce', 'fce'], dict(hit=1, applied=1, rearm=0)),
    ('S2 fill, FCE, fill, FCE', ['fill', 'fce', 'fill', 'fce'], dict(hit=2, applied=2, rearm=1)),
    ('S3 fill, FCE, draw, FCE', ['fill', 'fce', 'draw', 'fce'], dict(hit=1, applied=1, drawn=0)),
    ('S4 fill, draw, FCE', ['fill', 'draw', 'fce'], dict(hit=0, drawn=1)),
    ('X1 draw, fill, FCE (draw before the fill)', ['draw', 'fill', 'fce'], dict(hit=1, applied=1, drawn=0)),
    ('X2 fill, FCE, fill(nonzero), FCE', ['fill', 'fce', ('fill', 0x20202020), 'fce'], dict(hit=1, applied=1, drawn=0)),
    ('X3 fill, FCE, FCE, fill, FCE, FCE', ['fill', 'fce', 'fce', 'fill', 'fce', 'fce'], dict(hit=2, applied=2, rearm=1)),
]
for name, ev, want in req:
    got = run(ev)
    good = all(got[k] == v for k, v in want.items())
    print('%-45s =1 -> %s want %s -> %s' % (name, got, want, 'OK' if good else 'FAIL'))
    ok &= good
# =0: the entry never leaves PendingDcc via this path; the member's CMask half is never read
got0 = run(['fill', 'fce', 'fce', 'fce', 'fce'], fix_on=False)
good = got0 == dict(hit=4, applied=0, drawn=0, rearm=0)
print('%-45s =0 -> %s -> %s' % ('S1 at =0 (p.353(d) N2)', got0, 'OK' if good else 'FAIL'))
ok &= good

# Invariants over random sequences, =1, T6 view (0,0,1):
#   I1 every hit is applied (RC1 of F9f2: no hit/rearm without a ClearImage)
#   I2 hit <= number of zero fills; rearm <= number of zero fills after the first
#   I3 drawn <= number of draws following a zero fill with no FCE hit between (no FCE after a clear without a re-fill)
fails = 0
for t in range(20000):
    ev = [rnd.choice(['fill', 'fill', 'fce', 'fce', 'fce', 'draw', ('fill', 0x20202020)]) for _ in range(rnd.randint(1, 14))]
    s = Sim(True)
    zero_fills = 0
    armed_since_fill = False
    draw_after_open_fill = 0
    for e in ev:
        name = e[0] if isinstance(e, tuple) else e
        if isinstance(e, tuple):
            s.fill(*e[1:])
            armed_since_fill = False
        elif name == 'fill':
            s.fill()
            zero_fills += 1
            armed_since_fill = True
        elif name == 'draw':
            s.draw()
        else:
            r = s.fce()
            if r == 'drawn' and not armed_since_fill:
                fails += 1
                if fails <= 3:
                    print('I3 FAIL', ev)
            if r == 'hit':
                armed_since_fill = False
    c = s.c
    if c['hit'] != c['applied'] or c['hit'] > zero_fills or c['rearm'] > max(0, zero_fills - 1):
        fails += 1
        if fails <= 3:
            print('I1/I2 FAIL', ev, c)
print('invariants I1-I3 over 20000 random sequences: fails %d -> %s' % (fails, 'OK' if fails == 0 else 'FAIL'))
ok &= fails == 0

# Note (letter of (g)(1), not a member failure): a PendingDcc entry is armed without the view bits; with a bad view
# PrepareCmaskClear converts it to CMask and clears nothing -> one hit without applied (then the CMask half is unarmed).
s = Sim(True)
s.fill()
s.fce((0, 32, 1))
s.fce((0, 32, 1))
print('note: PendingDcc + bad view (0,32,1), 2 FCE -> %s (hit without applied once; letter of (g)(1))' % s.c)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)

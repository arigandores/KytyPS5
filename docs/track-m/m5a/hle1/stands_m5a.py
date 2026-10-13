# M5a HLE1: offline stands that model OUR functions (dd73d04d) and the upstream versions line by line.
# S1 T023 agc GetAvailableSizeDW/ReserveDW decision (src/libs/agc.cpp:267-320 vs 49b2eedd1)
# S2 T031 guestPrintf dynamic precision (src/libs/guestPrintf.cpp:520-532 vs bab1c3614), reference = UCRT/MSVCRT
# S3 T055 AvPlayer event/return model on the call order recovered from eboot.elf (avcall_m5a / dis_*_m5a)
# S4 T125 AudioOut2 queue selection: which ports reach AudioOutOutputs (libAudio2.cpp:357-376 vs c86c8b4d9)
import os, sys, ctypes, itertools
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('SEALED_RUN.lock present - exit'); sys.exit(3)
ok = True
U32 = 0xffffffff

# ---------------- S1 ----------------
def ours_avail(up, down, reserved):
    if up == 0 or down == 0 or down <= up:
        return 0
    available = (down - up) // 4            # uint32_t* difference (byte distance multiple of 4 in the grid)
    if available <= reserved:
        return 0
    if available - reserved > U32:
        return U32                            # + "suspiciously large" log line
    return available - reserved
def up_avail(up, down, reserved):
    dist = (down - up) & ((1 << 64) - 1)
    if dist >= 1 << 63: dist -= 1 << 64       # int64 cast
    available = (dist >> 2) & ((1 << 64) - 1)  # arithmetic shift, then uint64
    if available <= reserved:
        return 0
    return available - reserved
def reserve_calls_cb(avail, num_dw):
    return num_dw > avail                     # ReserveDW: num_dw > remaining -> callback (or 'exhausted')
B = 0x2_0000_0000
ups = [0, B, B + 4, B + 0x400]
downs = [0, B - 4, B, B + 4, B + 8, B + 0x400, B + 0x400 + (1 << 34) + 64, B + (1 << 36)]
diff = collections_cnt = {}
import collections
cls = collections.Counter(); ex = {}
for up, down, res, n in itertools.product(ups, downs, [0, 1, 4], [1, 2, 5, 22, 0xffffffff]):
    a, b = ours_avail(up, down, res), up_avail(up, down, res)
    da, db = reserve_calls_cb(a, n), reserve_calls_cb(b, n)
    if da != db:
        k = ('up=0' if up == 0 else 'down=0' if down == 0 else 'down<up' if down < up else 'down==up' if down == up else 'down>up')
        cls[k] += 1; ex.setdefault(k, (hex(up), hex(down), res, n, a, b))
print('S1 T023: decision differs (ours calls guest callback / upstream does not) by class:', dict(cls))
for k, v in ex.items(): print('   example', k, 'up,down,res,num_dw,ours_avail,upstream_avail =', v)
same_pos = all(reserve_calls_cb(ours_avail(u, d, r), n) == reserve_calls_cb(up_avail(u, d, r), n)
               for u, d, r, n in itertools.product(ups[1:], downs, [0, 1, 4], [1, 22, 0xffffffff]) if d > u)
print('S1 T023: for non-null cursors with down > up the decision is identical:', same_pos)
ok &= same_pos and set(cls) <= {'up=0', 'down=0', 'down<up'}

# ---------------- S2 ----------------
def ours_prec(prec):          # guestPrintf.cpp:528-530 (dd73d04d): FLAGS_PRECISION set, precision = prec > 0 ? prec : 0
    return True, (prec if prec > 0 else 0)
def std_prec(prec):           # C11 7.21.6.1p5 / bab1c3614: negative => as if omitted
    return (False, 0) if prec < 0 else (True, prec)
def fmt_s(s, has, p):
    return s[:p] if has else s
try:
    crt = ctypes.cdll.msvcrt
    buf = ctypes.create_string_buffer(64)
    crt._snprintf(buf, 63, b'[%.*s]', ctypes.c_int(-1), b'abcdef')
    ref = buf.value.decode()
except Exception as ex_:
    ref = 'n/a (%s)' % ex_
o = '[' + fmt_s('abcdef', *ours_prec(-1)) + ']'
s = '[' + fmt_s('abcdef', *std_prec(-1)) + ']'
print('S2 T031: "%%.*s" with prec=-1 on "abcdef": ours=%s  C-standard=%s  msvcrt=%s' % (o, s, ref))
ok &= (o == '[]' and s == '[abcdef]')
for p in (0, 3, 10):
    ok &= fmt_s('abcdef', *ours_prec(p)) == fmt_s('abcdef', *std_prec(p))
print('S2 T031: prec >= 0 identical:', True)

# ---------------- S3 ----------------
# Calls in the game's order (eboot.elf VideoPlayerOrbis: Init 0x1053ddf, PostInit 0x1054018, AddSource 0x105403f,
# [SetAvSyncMode(1) 0x10540a4 only if obj+0x58 bit0, after AddSource], StreamCount/GetStreamInfo/EnableStream(type==1),
# Start 0x1054a71 (flag+0x290=1), Pause/Resume, JumpToTime, Stop 0x1054b41 (flag=0), IsActive wrapper = IsActive && flag).
seq = ['AddSource', 'IsActive', 'Start', 'IsActive', 'Pause', 'Resume', 'Pause', 'Resume', 'Jump', 'IsActive', 'Stop', 'IsActive']
EV = {1: 'STOP', 2: 'READY', 3: 'PLAY', 4: 'PAUSE', 0x20: 'WARNING'}
def run(model):
    ev, ret, wrap = [], [], []
    st = {'src': False, 'stopped': True, 'state': 'Ready', 'flag': False, 'drained': False}
    for c in seq:
        if c == 'AddSource':
            st['src'] = True; ev.append(2)
        elif c == 'Start':
            st['stopped'] = False; st['state'] = 'Playing'; st['flag'] = True; ev.append(3)
        elif c == 'Pause':
            if model == 'up' and st['state'] != 'Playing': ret.append('FAIL'); continue
            ev.append(4)
        elif c == 'Resume':
            ev.append(3)
        elif c == 'Jump':
            if model == 'up' and st['state'] != 'Playing': ret.append('FAIL'); continue
            ev.append(0x20)
        elif c == 'Stop':
            if model == 'ours' or st['state'] == 'Playing': ev.append(1)
            st['stopped'] = True; st['state'] = 'Stopped'; st['flag'] = False
        elif c == 'IsActive':
            if model == 'ours':
                raw = st['src'] and not st['stopped'] and not st['drained']
            else:
                raw = (not st['src']) or st['state'] == 'Ready' or (st['state'] == 'Playing' and not st['drained'])
            wrap.append((raw, raw and st['flag']))
    return [EV[e] for e in ev], ret, wrap
ro, rr = run('ours'), run('up')
print('S3 T055: ours     events', ','.join(ro[0]), 'fails', ro[1], 'IsActive(raw, game wrapper)', ro[2])
print('S3 T055: upstream events', ','.join(rr[0]), 'fails', rr[1], 'IsActive(raw, game wrapper)', rr[2])
print('S3 T055: events equal:', ro[0] == rr[0], '; game-wrapper IsActive equal:', [w for _, w in ro[2]] == [w for _, w in rr[2]],
      '; raw IsActive equal:', [r for r, _ in ro[2]] == [r for r, _ in rr[2]])
ok &= ro[0] == rr[0] == ['READY', 'PLAY', 'PAUSE', 'PLAY', 'PAUSE', 'PLAY', 'WARNING', 'STOP']
ok &= [w for _, w in ro[2]] == [w for _, w in rr[2]]

# ---------------- S4 ----------------
# ports as in log_m3_*: MAIN(0, 8ch), BGM(1), PADSPK(3), VIBRATION(6) with a device; object ports 0x100 without.
ports = [dict(t=0, h=1), dict(t=1, h=2), dict(t=3, h=3), dict(t=6, h=4)] + [dict(t=0x100, h=0) for _ in range(18)]
for p in ports: p['pcm'] = True
ours_q = [p for p in ports if p['h'] > 0 and p['pcm']]                     # libAudio2.cpp:363-365
up_q = [p for p in ports if p['t'] & 0xff00 != 0x100 and p['h'] > 0 and p['pcm']]
up_mix = [p for p in ports if p['t'] & 0xff00 == 0x100 and p['pcm']]      # c86c8b4d9: mixed into object_audio_handle
print('S4 T125: ports with PCM %d; ours queued %d (objects dropped %d); upstream queued %d + 1 object mix of %d objects'
      % (len(ports), len(ours_q), len([p for p in ports if p['h'] == 0]), len(up_q), len(up_mix)))
ok &= len(ours_q) == 4 and len(up_mix) == 18
print('ALL OK' if ok else 'FAIL')

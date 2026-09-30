# sync_split.py - Lever Researcher s.135 step 9a: per-frame means, window 10..88 (p.55(b)), blocks by GateArm, arm by text,
# of the sync/epoch/buffast counters beside the rbslow parts (rs135 arm 0 and 1). Rows [c] of counts, not time.
import sys
X = [b'sync_noop', b'sf_skip', b'bfast_hit', b'bfast_miss', b'bfast_stale', b'bfast_skip', b'ob_stream', b'ob_stream_us',
     b'rb_slow_n', b'rb_epoch_n', b'rb_stream_n', b'rb_cbank_n', b'rs_sync_n', b'rs_sync_noop_n', b'rs_ro_n', b'rs_wr_n',
     b'rs_find_n', b'be_fast', b'be_race', b'sync_up_kb', b'b2r_hit', b'b2r_n', b'b2r_miss_new', b'b2r_miss_gen', b'b2r_miss_evict',
     b'rs_bf_n', b'rs_bf_would', b'sh_buf_slow', b'sh_buf_epoch', b'sh_buf_stream', b'sh_buf_fast',
     b'rs_sync_kb', b'rb_sync_up_ns', b'rb_sync_wait_ns', b'rs_sync_ns', b'rb_slow_ns', b'rb_epoch_ns', b'rb_cal_ns', b'rb_cal_n', b'rs_head_ns', b'rs_tail_ns', b'rb_nupload_ns']
D = [b'bufepoch', b'bb_sync', b'bb_find', b'bb_obtain', b'bb_n', b'sync_ups', b'ob_us', b'ob_n']
path = sys.argv[1]
arms, m, xs, ds = [], {}, {}, {}
def kv(ln, sp, want):
    out = {}
    for t in ln[sp + 1:].split():
        k, _, v = t.partition(b'=')
        if k in want:
            try: out[k] = int(v)
            except ValueError: pass
    return out
with open(path, 'rb') as f:
    for ln in f:
        j = ln.find(b'FrameTrace')
        if j >= 0:
            sp = ln.find(b' ', j); key = ln[j:sp]
            toks = ln[sp + 1:sp + 20].split()
            if not toks or not toks[0].startswith(b'n='): continue
            n = int(toks[0][2:])
            if key == b'FrameTrace:': m[n] = kv(ln, sp, {b'arm', b'blk'})
            elif key == b'FrameTrace-x:': xs[n] = kv(ln, sp, set(X))
            elif key == b'FrameTrace-draw:': ds[n] = kv(ln, sp, set(D))
            continue
        if b'GateArm:' in ln:
            a = {}
            for t in ln[ln.find(b'GateArm:') + 8:].split():
                k, _, v = t.partition(b'=')
                a[k] = v
            arms.append(a)
AT = {b'b2reuse=0': 0, b'b2reuse=1': 1}
acc = {0: {}, 1: {}}; rows = {0: 0, 1: 0}
for b, a in enumerate(arms):
    F = int(a[b'frame']); arm = AT[a[b'text']]
    win = [F + 1 + p for p in range(10, 89)]
    if not all(n in m and n in xs and n in ds and m[n].get(b'blk') == b and m[n].get(b'arm') == arm for n in win): continue
    for n in win:
        rows[arm] += 1
        for k, v in list(xs[n].items()) + list(ds[n].items()):
            acc[arm][k] = acc[arm].get(k, 0) + v
print('rows', rows)
for k in X + D:
    print('%-16s arm0 %12.1f  arm1 %12.1f' % (k.decode(), acc[0].get(k, 0) / rows[0], acc[1].get(k, 0) / rows[1]))

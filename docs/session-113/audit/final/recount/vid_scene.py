# Scene-row (n >= stable_frame) sums of FrameTrace-x fields in the video log.
import re, sys
path, st = sys.argv[1], int(sys.argv[2])
F = ['cspfree_hit','cspfree_bad','cs_sync_new','cs_sync_wait','da_q_free','da_q_noguard','da_slot_bad','da_guard_yield','bda_nskip','bda_nwould','prio_stall','prio_unsub']
tok = re.compile(rb' ([a-z_0-9]+)=(-?\d+)')
s = {k: 0 for k in F}; rows = 0; nmin = None
with open(path, 'rb') as f:
    for line in f:
        if not line.startswith(b'FrameTrace-x: '): continue
        d = {}
        for m in tok.finditer(line):
            k = m.group(1).decode()
            if k not in d: d[k] = int(m.group(2))
        if d['n'] < st: continue
        rows += 1
        for k in F: s[k] += d.get(k, 0)
print('scene rows', rows, s)

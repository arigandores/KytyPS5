# Track F link F12g (HPP-481): offline recount of item 391 (g)(4) from the raw image dumps of rd_f12g.py (own code, numpy, no RenderDoc).
# usage: python nd_f12g.py [dump dir]   ; texel = 8 bytes (R16G16B16A16_FLOAT, 128 x 2048, rd_f12g_k03.txt:12)
# Prints per dispatch: N_diff o1/o2 (control B), o1/r1 (measure), o1/r0 (replacement neutrality, data), o1/o3, zero texels o1 and r1,
# NaN texels, changed texels per channel; then the reading by item 391 (g)(4) given control A from rd_f12g_k03.txt.  ASCII only.
import sys, hashlib
import numpy as np
D = (sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/f287/f12g/dump_k03').rstrip('/') + '/'
EIDS = (44806, 84820, 128281)
REP = 'C:/kyty/f287/f12g/rd_f12g_k03.txt'
rep = open(REP).read().split(chr(10))
ca = [l for l in rep if 'CONTROL_A' in l]
okA = len(ca) == 3 and all(' OK ' in l for l in ca)
okB = True
nd_any = False
for e in EIDS:
    s = {}
    for k in ('pre', 'o1', 'o2', 'r0', 'r1', 'o3'):
        b = open(D + 'img_%d_21829_%s.bin' % (e, k), 'rb').read()
        assert len(b) == 128 * 2048 * 8, (e, k, len(b))
        s[k] = np.frombuffer(b, dtype=np.uint64)
        print('sha', e, k, hashlib.sha256(b).hexdigest())
    nb = int((s['o1'] != s['o2']).sum())
    nd = int((s['o1'] != s['r1']).sum())
    h0 = np.frombuffer(s['o1'].tobytes(), dtype=np.float16).reshape(-1, 4)
    h1 = np.frombuffer(s['r1'].tobytes(), dtype=np.float16).reshape(-1, 4)
    ch = ((h0 != h1) & ~(np.isnan(h0) & np.isnan(h1))).sum(0).tolist()
    print('eid', e, 'B_o1_o2', nb, 'N_diff_o1_r1', nd, 'of', s['o1'].size, 'o1_r0', int((s['o1'] != s['r0']).sum()),
          'o1_o3', int((s['o1'] != s['o3']).sum()), 'pre_o1', int((s['o1'] != s['pre']).sum()),
          'zero_o1', int((s['o1'] == 0).sum()), 'zero_r1', int((s['r1'] == 0).sum()),
          'nan_o1', int(np.isnan(h0).any(1).sum()), 'nan_r1', int(np.isnan(h1).any(1).sum()), 'changed_per_channel_RGBA', ch)
    okB = okB and nb == 0
    nd_any = nd_any or nd >= 1
if okA and okB and nd_any:
    w = 'ACTS_IN_FRAME'
elif okA and okB:
    w = 'INERT_IN_FRAME_UNDETERMINED'
else:
    w = 'UNDETERMINED'
print('control_A', okA, 'control_B', okB, 'N_diff_ge_1_any', nd_any, 'READING', w)

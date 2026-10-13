"""M5b (HPP-846): independent recount of M5a log numbers in M3 logs (read-only, exits 3 under the lock).
Usage: python rc_log_m5b.py > rc_log_m5b.out.txt"""
import collections, os, re, sys
LOCK = 'C:/kyty/SEALED_RUN.lock'
if os.path.exists(LOCK):
    print('LOCK present - exit 3'); sys.exit(3)
L = 'C:/kyty/m657/m3a/'
TAGS = ['log_m3_sg_v_r1.txt', 'log_m3_hb_f.txt', 'log_m3_i.txt', 'log_m3_mg_v.txt', 'log_m3_hb_w.txt']
RX_CLR = re.compile(rb'\bclr_ok=(\d+)')
RX_PT = re.compile(rb'^\t port_type\s*=\s*(\d+)')
RX_AH = re.compile(rb'^\t audio_handle\s*=\s*(-?\d+)')
RX_EV = re.compile(rb'^\t event_id = (\d+)')
for t in TAGS:
    p = L + t
    if not os.path.exists(p):
        print(t, 'missing'); continue
    clr = 0; ft = 0; pt = collections.Counter(); ah_by_pt = collections.Counter(); last_pt = None
    ev = []; mt265 = 0; minlod = 0; inval = 0; fatal = 0; port_destroy = 0; sr = collections.Counter()
    with open(p, 'rb') as f:
        for ln in f:
            if ln.startswith(b'FrameTrace-x:'):
                ft += 1
                m = RX_CLR.search(ln)
                if m:
                    clr += int(m.group(1))
                continue
            m = RX_PT.match(ln)
            if m:
                last_pt = int(m.group(1)); pt[last_pt] += 1; continue
            m = RX_AH.match(ln)
            if m and last_pt is not None:
                ah_by_pt[(last_pt, int(m.group(1)) > 0)] += 1; last_pt = None; continue
            m = RX_EV.match(ln)
            if m:
                ev.append(int(m.group(1))); continue
            if ln.startswith(b'\t port = 0x'):
                port_destroy += 1
            if b'MT265: mode=' in ln:
                mt265 += 1
            if b'T# MIN_LOD' in ln:
                minlod += 1
            if b'invalid image view' in ln:
                inval += 1
            if b'Fatal Error' in ln:
                fatal += 1
    print('==', t, 'FrameTrace-x', ft, 'sum clr_ok', clr)
    print('   PortCreate port_type', dict(sorted(pt.items())), 'audio_handle>0 by type', dict(sorted(ah_by_pt.items())))
    print('   port destroy lines', port_destroy, 'event_id seq', ev)
    print('   MT265 lines', mt265, 'T# MIN_LOD lines', minlod, 'invalid image view', inval, 'Fatal Error', fatal)
print('ALL DONE')

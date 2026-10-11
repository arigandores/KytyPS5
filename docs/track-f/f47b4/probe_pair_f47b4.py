# F47b4 (HPP-819, Red Team): probe - how many classes of the T1 corpus change when the over-approximated second source
# register (s+1) of 32-bit SOP1 / SOP2 instructions is dropped (exact sources for 32-bit forms). Reference only; the
# 32-bit set is a conservative subset (RDNA2 [I]): SOP2 every opcode outside SOP2_64, SOP1 s_mov_b32 / s_not_b32.
# Read only; ASCII only; exits 3 when the lock exists.
import collections
import importlib.util
import os
import re
import struct
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
if os.path.exists(LOCK):
    print('LOCK present - exit 3')
    sys.exit(3)

CLS = 'C:/kyty/KytyPS5/docs/track-f/f47a4/cls_f47a4.py'
spec = importlib.util.spec_from_file_location('cls_f47a4', CLS)
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

SOP2_64 = {0x0b, 0x0f, 0x11, 0x13, 0x15, 0x17, 0x19, 0x1b, 0x1d, 0x1f, 0x21, 0x23, 0x25, 0x28, 0x2a}
SOP1_32 = {0x03, 0x07}
orig_decode = C.decode


def exact_decode(words):
    ins, status = orig_decode(words)
    for I in ins:
        if I.fam == 'SOP2' and I.op not in SOP2_64:
            I.srcs = [s for k, s in enumerate(I.srcs) if k not in (2, 3)]
        elif I.fam == 'SOP1' and I.op in SOP1_32:
            I.srcs = [s for k, s in enumerate(I.srcs) if k != 1]
    return ins, status


def corpus(prefix):
    progs = {}
    for arm in sorted(os.listdir(C.GCN_ROOT)):
        d = os.path.join(C.GCN_ROOT, arm)
        for fn in sorted(os.listdir(d)):
            m = re.match(r'^%s_([0-9a-f]{16})\.bin$' % prefix, fn)
            if m and m.group(1) not in progs:
                progs[m.group(1)] = os.path.join(d, fn)
    return progs


udcs = C.udc_index()
for prefix, mrt, stage in (('ps', 0, 'ps'), ('vs', 12, 'vs')):
    changed = []
    dist = [collections.Counter(), collections.Counter()]
    for h, path in sorted(corpus(prefix).items()):
        b = open(path, 'rb').read()
        words = list(struct.unpack('<%dI' % (len(b) // 4), b))
        u = udcs.get(h) if prefix == 'ps' else None
        u1 = min(u) if u else None
        C.decode = orig_decode
        a0 = C.analyse(words, udc=u1, mrt=mrt, stage=stage)
        C.decode = exact_decode
        a1 = C.analyse(words, udc=u1, mrt=mrt, stage=stage)
        dist[0][a0['cls']] += 1
        dist[1][a1['cls']] += 1
        if a0['cls'] != a1['cls'] or a0['leaves'] != a1['leaves']:
            changed.append('%s %s udc %s: %s %s -> %s %s' % (prefix, h, u1, a0['cls'], sorted(a0['leaves']), a1['cls'],
                                                            sorted(a1['leaves'])))
    C.decode = orig_decode
    print('%s edition %s exact32 %s changed %d' % (prefix, sorted(dist[0].items()), sorted(dist[1].items()), len(changed)))
    for line in changed:
        print('  ' + line)
print('done')

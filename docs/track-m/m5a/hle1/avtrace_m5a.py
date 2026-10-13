# M5a HLE1: AudioOut2 push evidence in a log taken with KYTY_AV_TRACE=1 (track F F18e tag f8_s1, binary 35c4a754;
# libAudio2.cpp at that binary differs from dd73d04d only by DIAG_B32 marks a92c4a1ac). Counts "AvTrace: push" lines
# (AudioOut2ContextPush logs n<=5 and every 1000th call), "AvTrace: audio dev=" (AudioOutOutputs per device) and AudioStat.
import os, re, sys, collections
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('SEALED_RUN.lock present - exit'); sys.exit(3)
p = sys.argv[1]
pat = re.compile(rb'^(AvTrace: push [^\n]*|AvTrace: audio [^\n]*|AudioStat:[^\n]*)$', re.M)
c = collections.Counter(); first = collections.defaultdict(list); maxn = 0; ctxs = collections.Counter()
f = open(p, 'rb'); tail = b''
while True:
    blk = f.read(64 << 20)
    if not blk and not tail: break
    buf = tail + blk
    if blk:
        k = buf.rfind(b'\n'); tail = buf[k + 1:]; buf = buf[:k + 1]
    else:
        tail = b''
    for m in pat.finditer(buf):
        ln = m.group(1); key = ln[:16]
        c[key] += 1
        if len(first[key]) < 6: first[key].append(ln[:200].decode('utf-8', 'replace'))
        if ln.startswith(b'AvTrace: push'):
            mm = re.search(rb' n=(\d+)', ln); maxn = max(maxn, int(mm.group(1)))
            ctxs[re.search(rb'ctx=(\S+)', ln).group(1)] += 1
    if not blk: break
print('log', p)
for k, v in c.items():
    print(k, v)
    for x in first[k]: print('   ', x)
print('AudioOut2ContextPush calls (max n of AvTrace push) >=', maxn, ' contexts:', dict(ctxs))
print('DONE')

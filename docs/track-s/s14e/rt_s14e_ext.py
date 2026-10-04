# S14e (HPP-528) Red Team: own extractor of one S10 log (independent of c0p_s14k.py). Streams in binary mode.
import sys, os, re, hashlib, pickle, time
if os.path.exists('C:/kyty/SEALED_RUN.lock'): sys.exit(5)
if os.path.exists('C:/kyty/s288/STOP'): sys.exit(4)
tag, lv, out = sys.argv[1], sys.argv[2], sys.argv[3]
p = 'C:/kyty/s288/s10/log_%s.txt' % tag
t0 = time.time()
h = hashlib.sha256()
regs = {}        # hash -> [(line, host, type, {reg: val})]
comp = []        # [line, stage, hash, perm, spec_tail, frame_after, host_before]
spec_prev = None
rows = []        # (n, line) FrameTrace
skc = {}         # n -> (held, skip)
ent = None
sigs = set()
last_host = None
pend = []
lvl = b'GuestOut: Level has started: ' + lv.encode() + b'\n'
with open(p, 'rb') as f:
    for n, l in enumerate(f, 1):
        h.update(l)
        if l.startswith(b'FrameTrace: n='):
            k = int(l[14:l.index(b' ', 14)])
            rows.append((k, n))
            for c in pend: c[5] = k
            pend = []
        elif l.startswith(b'FrameTrace-x: n='):
            k = int(l[16:l.index(b' ', 16)])
            mh = re.search(rb' skc_held_inc=(\d+)', l); ms = re.search(rb' skc_ap_skip=(\d+)', l)
            if mh and ms: skc[k] = (int(mh.group(1)), int(ms.group(1)))
        elif l.startswith(b'ShaderRegister: '):
            fs = l.split()
            d = dict(x.split(b'=', 1) for x in fs[1:])
            hs = d[b'hash'].decode(); host = int(d[b'host_us'])
            toks = {}
            for x in fs[1:]:
                k, v = x.split(b'=', 1)
                if k not in (b'hash', b'type', b'size', b'scratch', b'code', b'header', b'host_us'):
                    toks.setdefault(k.decode(), v.decode())   # first occurrence of a register
            regs.setdefault(hs, []).append((n, host, int(d[b'type']), toks))
            last_host = host
        elif l.startswith(b'ShaderFirstUse: '):
            m = re.search(rb'host_us=(\d+)', l)
            if m: last_host = int(m.group(1))
        elif l.startswith(b'AvTrace: flip '):
            m = re.search(rb' host=(\d+)', l)
            if m: last_host = int(m.group(1))
        elif l.startswith(b'AvTrace: shader-spec '):
            m = re.match(rb'AvTrace: shader-spec ShaderRecompiler (\w+) hash=0x([0-9a-f]+) perm=(\d+)(.*?)\r?\n$', l)
            spec_prev = (n, m.group(1).decode(), m.group(2).decode(), int(m.group(3)), m.group(4).decode('latin1'))
        elif l.startswith(b'AvTrace: shader ShaderRecompiler '):
            m = re.match(rb'AvTrace: shader ShaderRecompiler (\w+) hash=0x([0-9a-f]+) .* permutations=(\d+)', l)
            st, hs, perm = m.group(1).decode(), m.group(2).decode(), int(m.group(3))
            sp = spec_prev[4] if spec_prev and spec_prev[0] == n - 1 and spec_prev[1:4] == (st, hs, perm) else None
            c = [n, st, hs, perm, sp, None, last_host]
            comp.append(c); pend.append(c)
        elif ent is None and l == lvl:
            ent = n
        if b'KytySC3:' in l:
            for s in re.findall(rb'KytySC3:[0-9a-f]{40}(?::[A-Za-z][A-Za-z0-9_]*)*', l): sigs.add(s.decode())
pickle.dump(dict(tag=tag, lv=lv, sha=h.hexdigest(), lines=n, regs=regs, comp=comp, rows=rows, skc=skc, ent=ent, sigs=sorted(sigs)),
            open(out, 'wb'))
print(tag, h.hexdigest()[:16], 'lines', n, 'regs', sum(len(v) for v in regs.values()), 'comp', len(comp), 'ent', ent,
      'sigs', sorted(sigs), 'wall %.1f' % (time.time() - t0))

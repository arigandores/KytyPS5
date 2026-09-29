# Independent recount of step 0v evidence (HPP-153 audit, p.116(a), 105(b)(2)-(6)). Own code.
# Blocks by 'GateArm:'; row n = F goes to outgoing block (switch at position 89, p.28); window 10..88 p.55(b) on complete blocks.
import re, math, hashlib, sys

KEYS = ('ac_cbad', 'ac_cmp_pages', 'ac_bad', 'ac_gbad', 'ac_jleft', 'ac_jremark', 'ac_jstale', 'ac_chk', 'ac_gchk',
        'ac_refuse', 'ac_moved_n', 'ac_gjleft')
MARK = (b'ErrorDeviceLost', b'GpuHangAbort:', b'GpuWaitSlow:', b'--- Fatal Error ---', b'ArmCopy: refused')

def scan(tag):
    arm_re = re.compile(rb'GateArm: arm=(\d+) arms=\d+ block=(\d+) frame=(\d+) .*text=(\S+)')
    gates, rows = [], []
    marks = {m: 0 for m in MARK}
    armcopy_lines = {}
    verify = 0
    missing = 0
    with open('C:/kyty/s130/log_%s.txt' % tag, 'rb') as f:
        for line in f:
            if line.startswith(b'GateArm:'):
                m = arm_re.search(line); gates.append((int(m.group(2)), int(m.group(3)), m.group(4).decode()))
            elif line.startswith(b'FrameTrace-x'):
                d = {}
                for kv in line.split():
                    if kv.startswith(b'ac_') or kv.startswith(b'n='):
                        k, v = kv.split(b'=', 1); d[k.decode()] = int(v)
                if any(k not in d for k in KEYS): missing += 1
                rows.append(d)
            else:
                if line.startswith(b'ArmCopy:'):
                    s = line.strip().decode(); armcopy_lines[s] = armcopy_lines.get(s, 0) + 1
                if line.startswith(b'ArmCopyVerify'): verify += 1
                for m in MARK:
                    if m in line: marks[m] += 1
    return gates, rows, marks, armcopy_lines, verify, missing

def arms_read(gates, rows):
    a = []
    gi = -1
    for r in rows:
        while gi + 1 < len(gates) and gates[gi + 1][1] < r['n']: gi += 1
        if gi < 0: continue
        b, F, arm = gates[gi]; a.append((b, arm, r['n'] - F - 1, r))
    maxp = {}
    for b, arm, p, r in a: maxp[b] = max(maxp.get(b, -9), p)
    comp = {b for b, m in maxp.items() if m >= 89}
    res = {}
    for lab, pred in (('all', lambda b, p: True), ('win', lambda b, p: b in comp and 10 <= p <= 88)):
        for arm in ('armcopy=2', 'armcopy=4'):
            n = c = x = 0
            for b, ar, p, r in a:
                if ar == arm and pred(b, p): n += 1; c += r['ac_cbad']; x += r['ac_cmp_pages']
            res[(lab, arm)] = (n, c, x)
    blk = {}
    for b, ar, p, r in a:
        if b in comp:
            e = blk.setdefault(b, [ar, 0, 0]); e[1] += r['ac_cbad']; e[2] += r['ac_cmp_pages']
    bs = sorted(blk); d = []; over = 0
    for i in range(0, len(bs) - 1, 2):
        X, Y = blk[bs[i]], blk[bs[i + 1]]
        h2 = X if X[0] == 'armcopy=2' else Y; h4 = Y if h2 is X else X
        s2, s4 = h2[1] / h2[2], h4[1] / h4[2]
        d.append(100 * (s2 - s4)); over += (s2 > 1.5 * s4)
    k = len(d); mu = sum(d) / k; se = math.sqrt(sum((q - mu) ** 2 for q in d) / (k - 1) / k)
    return res, (k, mu, 2 * se, over)

for tag in ('s1s130', 's2s130', 's3s130', 'ack130', 'shp130'):
    gates, rows, marks, acl, verify, missing = scan(tag)
    tot = {k: sum(r.get(k, 0) for r in rows) for k in KEYS}
    jst_rows = sum(1 for r in rows if r.get('ac_jstale', 0) != 0)
    so = open('C:/kyty/s130/stdout_%s.txt' % tag, 'rb').read()
    so_mark = sum(so.count(m) for m in MARK) + so.count(b'fatal')
    print('==', tag, 'rows', len(rows), 'missing_keys_rows', missing, 'marks', {k.decode(): v for k, v in marks.items()}, 'stdout_marks', so_mark)
    print('  ArmCopy lines', acl, 'ArmCopyVerify', verify, 'jstale!=0 rows', jst_rows)
    print('  sums', tot)
    if gates:
        res, pr = arms_read(gates, rows)
        for lab in ('all', 'win'):
            n2, c2, x2 = res[(lab, 'armcopy=2')]; n4, c4, x4 = res[(lab, 'armcopy=4')]
            print('  %s rows %d/%d  2: %d/%d=%.5f%%  4: %d/%d=%.5f%%  ratio %.3f' % (lab, n2, n4, c2, x2, 100 * c2 / x2, c4, x4, 100 * c4 / x4, (c2 / x2) / (c4 / x4)))
        print('  pairs k=%d mean=%+.5f%% 2SE=%.5f%% over1.5=%d' % pr)
for p in ('C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe', 'C:/kyty/s128/kyty_emulator_9235a7ac.exe', 'C:/kyty/s130/kyty_emulator_3f4af2c3.exe', 'C:/kyty/s130/kyty_emulator_0d23f161.exe'):
    print(p, hashlib.sha256(open(p, 'rb').read()).hexdigest())

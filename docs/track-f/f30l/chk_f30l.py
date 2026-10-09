# F30l (HPP-722, Red Team): independent check of the F30k code (ROADMAP s122 item 655(d)) and its mutants (m1)-(m5).
# Usage: python chk_f30l.py      (reads git objects only; no build, no game)
# Prints PASS/FAIL per member, then the mutant table; ALL OK or FAILED; exit 0 / 1.
import hashlib, re, subprocess, sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
T, T2, MAIN = 'a1d1d863', '6fbdcf67', '11236f5a'
RD = 'src/graphics/host_gpu/renderer/renderDraw.cpp'
BIN = 'C:/kyty/f287/bin/kyty_emulator_bba692c6.exe'
BIN_SHA = 'bba692c6c161afc0cd2bd3245cea574f7fb82e7a4aae4c065826898403107163'
TAB = chr(9)

def git(*a):
    return subprocess.run([G, '-C', REPO] + list(a), capture_output=True, check=True).stdout.decode('utf-8')

def show(c, p):
    return git('show', '%s:%s' % (c, p)).split(chr(10))

ok = True
def member(name, cond):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name)
    ok = ok and bool(cond)

def strip_comment(l):
    return l.split('//')[0].rstrip()

def is_code(l):
    return strip_comment(l).strip() != ''

# ---- D0, D1: T2 is T plus exactly the main commit
par = git('rev-parse', T2 + '~1').strip()
member('D0 parent of T2 %s is T %s' % (T2, T), par.startswith(T))
def pm(d):
    return [l for l in d.split(chr(10)) if (l.startswith('+') or l.startswith('-')) and not l.startswith('+++') and not l.startswith('---')]
d_t2 = pm(git('diff', T, T2, '--', 'src'))
d_main = pm(git('show', '--format=', MAIN, '--', 'src'))
member('D1 +/- lines of T..T2 = +/- lines of main %s (%d / %d)' % (MAIN, len(d_t2), len(d_main)), d_t2 == d_main and len(d_t2) == 75)
files = sorted(git('diff', '--name-only', T, T2).split())
member('D1b files T..T2 = 5, none under src/graphics/shader: %s' % files,
       len(files) == 5 and not any(f.startswith('src/graphics/shader') for f in files))

# ---- checks on a renderDraw.cpp text (T2 or a mutant), against T
t_src = show(T, RD)

def t_rts_tests(src):
    out = []
    for l in src:
        if is_code(l):
            out += re.findall(r't_rts\s*(==|!=|>=|<=|<|>)\s*(\d)', strip_comment(l))
    return sorted(out)

def find_fn(src, head):
    i = [k for k, l in enumerate(src) if l.startswith(head)]
    if len(i) != 1:
        return None, None
    j = i[0]
    while src[j] != '}':
        j += 1
    return i[0], j

def checks(src, label, verbose):
    res = {}
    # D2: changed code lines (comments dropped) of renderDraw.cpp are only the allowed forms
    old_c = [strip_comment(l) for l in t_src if is_code(l)]
    new_c = [strip_comment(l) for l in src if is_code(l)]
    import difflib
    allowed = re.compile(r'^\s*(if \(\((bits|xsrc) & (0x010u|0x040u|0x080u|0x100u|0x200u|1u|2u|4u)\) != 0\) \{'
                         r'|FS::Add\(FS::Counter::RtsBad(R|Xr|Xc|Xe|S|P|M|L), 1\);|\}|uint32_t xsrc = 0;|xsrc \|= (1u|2u|4u);'
                         r'|void RtsReport\(uint32_t bits, int frame, uint32_t age, uint32_t colors, bool depth, uint32_t xsrc\) \{'
                         r'|static_cast<bool>\(state\.depth_info\.image_id\), 0\);'
                         r'|RtsReport\(bits, m_context\.GetGpu\(\)\.GetFrameNum\(\), rec->age, cc, hd, xsrc\);'
                         r'|if \(t_rts != 5 && \(!buffer\.IsRendering\(\) \|\| CommandBuffer::PassBeginSerial\(\) != rec->pass_serial\)\) \{)$')
    sm = difflib.SequenceMatcher(a=old_c, b=new_c, autojunk=False)
    bad = []
    removed = []
    for tag, a0, a1, b0, b1 in sm.get_opcodes():
        if tag == 'equal':
            continue
        for l in new_c[b0:b1]:
            if not allowed.match(l):
                bad.append(l.strip())
        removed += [l.strip() for l in old_c[a0:a1]]
    exp_removed = sorted(['void RtsReport(uint32_t bits, int frame, uint32_t age, uint32_t colors, bool depth) {',
                          'static_cast<bool>(state.depth_info.image_id));',
                          'if (!buffer.IsRendering() || CommandBuffer::PassBeginSerial() != rec->pass_serial) {',
                          'RtsReport(bits, m_context.GetGpu().GetFrameNum(), rec->age, cc, hd);'])
    res['D2'] = not bad and sorted(removed) == exp_removed
    if verbose and bad:
        print('   D2 unexpected:', bad[:6])
    # D3: t_rts value tests = T's plus exactly one "!= 5"
    res['D3'] = t_rts_tests(src) == sorted(t_rts_tests(t_src) + [('!=', '5')])
    # D3b: the "!= 5" test is the PB item 6 line, followed by return C::RtsXbPass;
    k = [i for i, l in enumerate(src) if is_code(l) and 't_rts != 5' in strip_comment(l)]
    res['D3b'] = len(k) == 1 and 'rec->pass_serial' in src[k[0]] and src[k[0] + 1].strip() == 'return C::RtsXbPass;'
    # D4: the eight counters only inside RtsReport, after the race return and after RtsBadRx, before the lines
    f0, f1 = find_fn(src, 'void RtsReport(')
    i_ret = [i for i in range(f0, f1) if src[i].strip() == 'return;'] if f0 is not None else []
    i_rx = [i for i, l in enumerate(src) if 'Counter::RtsBadRx' in l]
    names = ['RtsBadR,', 'RtsBadXr,', 'RtsBadXc,', 'RtsBadXe,', 'RtsBadS,', 'RtsBadP,', 'RtsBadM,', 'RtsBadL,']
    d4 = f0 is not None and len(i_ret) == 1 and len(i_rx) == 1
    for n in names:
        h = [i for i, l in enumerate(src) if 'Counter::' + n in l and is_code(l)]
        d4 = d4 and len(h) == 1 and i_ret[0] < i_rx[0] < h[0] < f1
    res['D4'] = d4
    # D5: X source mapping - each xsrc bit set in the branch of its own condition
    def cond_above(i, n=4):
        return ' '.join(src[max(0, i - n):i])
    xs = {m: [i for i, l in enumerate(src) if strip_comment(l).strip() == 'xsrc |= %s;' % m] for m in ('1u', '2u', '4u')}
    d5 = all(len(v) == 1 for v in xs.values())
    if d5:
        d5 = ('attachment_layout' in cond_above(xs['1u'][0]) and 'depth_load_clear_enable' not in cond_above(xs['1u'][0], 3)
              and 'state.depth_info.depth_load_clear_enable' in cond_above(xs['2u'][0], 2)
              and 'true_kpx' in cond_above(xs['4u'][0], 2))
    # and the counter of each xsrc bit is its own
    cm = {'1u': 'RtsBadXr', '2u': 'RtsBadXc', '4u': 'RtsBadXe', '0x010u': 'RtsBadR', '0x040u': 'RtsBadS', '0x080u': 'RtsBadP',
          '0x100u': 'RtsBadM', '0x200u': 'RtsBadL'}
    for m, n in cm.items():
        v = 'bits' if m.startswith('0x') else 'xsrc'
        h = [i for i, l in enumerate(src) if strip_comment(l).strip() == 'if ((%s & %s) != 0) {' % (v, m)]
        d5 = d5 and len(h) == 1 and src[h[0] + 1].strip() == 'FS::Add(FS::Counter::%s, 1);' % n
    res['D5'] = d5
    # D6: two callers of RtsReport, place A passes 0, the post passes xsrc
    calls = [strip_comment(l).strip() for l in src if 'RtsReport(' in l and not l.startswith('void RtsReport(') and is_code(l)]
    res['D6'] = len(calls) == 2
    return res

r = checks(show(T2, RD), 'T2', True)
for k in ('D2', 'D3', 'D3b', 'D4', 'D5', 'D6'):
    member('%s on T2 %s' % (k, T2), r[k])

# ---- knob row
g = show(T2, 'src/common/gates.cpp')
member('D7 knob row {"KYTY_RT_SKIP", "rtskip", 1, 5} once', sum(1 for l in g if l.strip() == '{"KYTY_RT_SKIP", "rtskip", 1, 5},') == 1)

# ---- binary identity (no rebuild: PE TimeDateStamp is the build time, the image is not bit-reproducible)
data = open(BIN, 'rb').read()
import struct, datetime
pe = struct.unpack_from('<I', data, 0x3c)[0]
ts = struct.unpack_from('<I', data, pe + 8)[0]
member('B1 sha256 of the copy = %s' % BIN_SHA[:8], hashlib.sha256(data).hexdigest() == BIN_SHA)
member('B2 version string -g6fbdcf67 in the binary', b'KytyPS5-2026-09-15-6a2987a-1907-g6fbdcf67' in data)
member('B3 signature 9177b426 in the binary', b'9177b4267de1fb8bac7d1113afd8733210addfac' in data)
print('INFO PE TimeDateStamp %d = %s UTC (build time stamped into the image)' % (ts, datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')))

# ---- mutants: each must fail at least one of D2-D6 (the static net); code_f30k.py C2/C4c emulated for (m3a)
t2 = show(T2, RD)
def mut(rep_pairs):
    s = list(t2)
    for old, new, cnt in rep_pairs:
        h = [i for i, l in enumerate(s) if l.strip() == old]
        if len(h) != cnt:
            raise SystemExit('mutant anchor %r found %d times' % (old, len(h)))
        for i in h:
            s[i] = s[i].replace(old, new)
    return s

def move_counters_before_race(s):
    s = list(s)
    f0, f1 = find_fn(s, 'void RtsReport(')
    a = [i for i in range(f0, f1) if 'RtsBadR, 1' in s[i]][0] - 1
    blk = s[a:a + 3]
    del s[a:a + 3]
    r0 = [i for i in range(f0, f1) if 'if (t_rts_race' in s[i]][0]
    return s[:r0] + blk + s[r0:]

def add_counter_in_post(s):
    s = list(s)
    i = [k for k, l in enumerate(s) if strip_comment(l).strip() == 'bits |= 0x040u;'][0]
    return s[:i + 1] + [TAB * 4 + 'FS::Add(FS::Counter::RtsBadS, 1);'] + s[i + 1:]

M = [
    ('m1a =5 also drops PB 3-4', mut([('if (t_rts != 4) {', 'if (t_rts != 4 && t_rts != 5) {', 1)])),
    ('m1b =5 also drops PB 5', mut([('if (img[i]->binding.is_bound != rec->t[i].is_bound) {',
                                     'if (t_rts != 5 && img[i]->binding.is_bound != rec->t[i].is_bound) {', 1)])),
    ('m2  =5 executes the skip', mut([('if (t_rts == 1 && pb_ok) {', 'if ((t_rts == 1 || t_rts == 5) && pb_ok) {', 1)])),
    ('m3a X source xc <-> xe', mut([('xsrc |= 2u;', 'xsrc |= 9u;', 1), ('xsrc |= 4u;', 'xsrc |= 2u;', 1), ('xsrc |= 9u;', 'xsrc |= 4u;', 1)])),
    ('m3b X source xr <-> xc (indent kept)', mut([('xsrc |= 1u;', 'xsrc |= 9u;', 1), ('xsrc |= 2u;', 'xsrc |= 1u;', 1), ('xsrc |= 9u;', 'xsrc |= 2u;', 1)])),
    ('m4a counters before the race return', move_counters_before_race(t2)),
    ('m4b counter in the post, outside RtsReport', add_counter_in_post(t2)),
    ('m5a at 0-4 the post compares at >= 3', mut([('if (t_rts >= 2 && t_rts_pa) {', 'if (t_rts >= 3 && t_rts_pa) {', 2)])),
    ('m5b at 4 PB item 6 not applied', mut([('if (t_rts != 5 && (!buffer.IsRendering() || CommandBuffer::PassBeginSerial() != rec->pass_serial)) {',
                                             'if (t_rts < 4 && (!buffer.IsRendering() || CommandBuffer::PassBeginSerial() != rec->pass_serial)) {', 1)])),
]
print('mutant | D2 D3 D3b D4 D5 D6 | killed | code_f30k C2+C4c (emulated) passes?')
for name, s in M:
    rr = checks(s, name, False)
    killed = not all(rr.values())
    # emulation of code_f30k.py C2 INSERTED_ONE (exact lines with indentation, each once) and C4c (after bits |= 0x020u;)
    ins = [TAB * 2 + 'uint32_t xsrc = 0;', TAB * 5 + 'xsrc |= 1u;', TAB * 4 + 'xsrc |= 2u;', TAB * 4 + 'xsrc |= 4u;']
    cc = [l.split('//')[0].rstrip() for l in s]
    c2ins = all(sum(1 for y in cc if y == l) == 1 for l in ins)
    xs = [i for i, l in enumerate(s) if 'xsrc |=' in l]
    c4c = len(xs) == 3 and all(s[i - 1].strip().startswith('bits |= 0x020u;') for i in xs)
    cf = 'yes (MISSED by code_f30k)' if (c2ins and c4c and name.startswith('m3')) else ('-' if not name.startswith('m3') else 'no')
    print('%-42s | %s | %s | %s' % (name, ' '.join('1' if rr[k] else '0' for k in ('D2', 'D3', 'D3b', 'D4', 'D5', 'D6')),
                                   'KILLED' if killed else 'SURVIVED', cf))
    member('mutant %s killed by D2-D6' % name, killed)

print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)

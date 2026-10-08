# F30d (HPP-709): checks of the code of ROADMAP s122 item 643(v)(1)-(3) and of the report links.
# Usage: python code_f30d.py <commit> [<commit> ...]   (585d997d on main, a1d1d863 in the worktree of binary T)
# Prints ALL OK or the first failing member; exit 0 / 1.
import subprocess, sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
RD = 'src/graphics/host_gpu/renderer/renderDraw.cpp'

def git(*a):
    return subprocess.run([G, '-C', REPO] + list(a), capture_output=True, check=True).stdout.decode('utf-8')

def show(c, p):
    return git('show', '%s:%s' % (c, p)).split('\n')

ok = True
def member(name, cond):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name)
    ok = ok and cond

def is_code(l):
    s = l.strip()
    return s != '' and not s.startswith('//')

for c in sys.argv[1:]:
    print('== commit', c)
    parent = c + '~1'
    # C1: knob range 1..4, one row.
    g = show(c, 'src/common/gates.cpp')
    member('C1 knob row {"KYTY_RT_SKIP", "rtskip", 1, 4} once', sum(1 for l in g if l.strip() == '{"KYTY_RT_SKIP", "rtskip", 1, 4},') == 1
           and not any('"KYTY_RT_SKIP", "rtskip", 1, 3' in l for l in g))
    # C2: the code lines (comment-only lines dropped) of renderDraw.cpp at the commit, with the six RtsReport lines and the
    # wrapper removed and the wrapper body dedented by one tab, equal the parent's code lines - the path at 0..3 is the
    # same instruction text apart from the two counters.
    # trailing comments dropped too (the t_rts_logged comment changed 17..19 -> 17..20)
    old_c = [l.split('//')[0].rstrip() for l in show(parent, RD) if is_code(l)]
    new_c = [l.split('//')[0].rstrip() for l in show(c, RD) if is_code(l)]
    six = ['	if ((bits & 0x3f0u) != 0) {', '		FS::Add(FS::Counter::RtsBadB, 1);', '	}',
           '	if ((bits & 0x030u) != 0) {', '		FS::Add(FS::Counter::RtsBadRx, 1);', '	}']
    k = [i for i in range(len(new_c)) if new_c[i:i + 6] == six]
    w = [i for i, l in enumerate(new_c) if l == '		if (t_rts != 4) {']
    c2 = len(k) == 1 and len(w) == 1
    if c2:
        x = new_c[:k[0]] + new_c[k[0] + 6:]
        w0 = [i for i, l in enumerate(x) if l == '		if (t_rts != 4) {'][0]
        e0 = next(i for i in range(w0 + 1, len(x)) if x[i] == '		}')
        body = x[w0 + 1:e0]
        c2 = all(l.startswith('			') for l in body) and len(body) == 8
        x = x[:w0] + [l[1:] for l in body] + x[e0 + 1:]
        c2 = c2 and x == old_c
    member('C2 code lines = parent + six RtsReport lines + the wrapper of PB items 3-4 (body 8 code lines, unchanged)', c2)
    # C3: at value 4 nothing else differs: no other new test of t_rts against 4 or a range.
    src = show(c, RD)
    t4 = [i + 1 for i, l in enumerate(src) if 't_rts' in l and '4' in l.split('t_rts', 1)[1][:8] and is_code(l)]
    member('C3 one test of t_rts against 4 (line %s)' % t4, len(t4) == 1 and src[t4[0] - 1].strip() == 'if (t_rts != 4) {')
    member('C3b the skip stays at value 1 only (2 tests t_rts == 1)', sum(1 for l in src if 't_rts == 1' in l and is_code(l)) == 2)
    # C4: the counters are added only in RtsReport, right after rts_bad / rts_bad_noreg (same population as rts_bad).
    i_bad = [i for i, l in enumerate(src) if l.strip() == 'FS::Add(FS::Counter::RtsBad, 1);']
    i_b = [i for i, l in enumerate(src) if 'Counter::RtsBadB' in l]
    i_x = [i for i, l in enumerate(src) if 'Counter::RtsBadRx' in l]
    member('C4 rts_bad_b / rts_bad_rx added once each, inside RtsReport after rts_bad',
           len(i_bad) == 1 and len(i_b) == 1 and len(i_x) == 1 and i_bad[0] < i_b[0] < i_x[0] < i_bad[0] + 12
           and src[i_b[0] - 1].strip() == 'if ((bits & 0x3f0u) != 0) {' and src[i_x[0] - 1].strip() == 'if ((bits & 0x030u) != 0) {')
    fs = show(c, 'src/common/frameStats.h')
    i_e = [i for i, l in enumerate(fs) if l.strip().startswith('RtsEarly,')]
    member('C5 enum: RtsBadB, RtsBadRx after RtsEarly',
           len(i_e) == 1 and fs[i_e[0] + 3].strip().startswith('RtsBadB,') and fs[i_e[0] + 4].strip().startswith('RtsBadRx,'))
    vo = show(c, 'src/graphics/presentation/videoOut.cpp')
    member('C6 FrameTrace-x table: rts_bad_b, rts_bad_rx rows once each',
           sum(1 for l in vo if l.strip() == '{"rts_bad_b", FS::Counter::RtsBadB, false},') == 1 and
           sum(1 for l in vo if l.strip() == '{"rts_bad_rx", FS::Counter::RtsBadRx, false},') == 1)
    files = sorted(git('diff', '--name-only', parent, c).split())
    member('C7 files of the commit: %s' % files, files == sorted(['src/common/frameStats.h', 'src/common/gates.cpp', 'src/common/gates.h', RD,
                                                                 'src/graphics/presentation/videoOut.cpp']))
    member('C8 nothing under src/graphics/shader (translation signature)', not any(f.startswith('src/graphics/shader') for f in files))

# Report links: <commit>:<path>:<line> with the whole-line anchor and the +1 control line.
REFS = [
    ('585d997d', 'src/common/gates.cpp', 438, '{"KYTY_RT_SKIP", "rtskip", 1, 4},', '// Session 128, MEASUREMENT ONLY: skip the read-only arming of a buffer synchronization on GuestGpu (1)'),
    ('585d997d', RD, 1597, 'FS::Add(FS::Counter::RtsBad, 1);', 'if (!t_rts_reg) {'),
    ('585d997d', RD, 1602, 'if ((bits & 0x3f0u) != 0) {', 'FS::Add(FS::Counter::RtsBadB, 1);'),
    ('585d997d', RD, 1605, 'if ((bits & 0x030u) != 0) {', 'FS::Add(FS::Counter::RtsBadRx, 1);'),
    ('585d997d', RD, 3441, 't_rts = armed; // a change between 1, 2 and 3 keeps the records', 'Common::Rk3::t_hooks |= Common::Rk3::HookRts;'),
    ('585d997d', RD, 3499, '} else if (t_rts != 3 && t_rts_reg) {', 'why = C::RtsXaReg;'),
    ('585d997d', RD, 3522, 'if (t_rts == 1 && t_rts_pa) {', '// The skip (s.3.2): the record\'s outputs, then the stores of the resolution\'s memo hits in its order - the LRU'),
    ('585d997d', RD, 3574, 'if (t_rts >= 2 && t_rts_pa) {', '// The resolution half of the self-check (s.5.1 step 2, s.5.2).'),
    ('585d997d', RD, 3683, 'if (t_rts != 4) {', '// 3 (N2, N4): the metadata epoch the record\'s fast records were taken at.'),
    ('585d997d', RD, 3719, 'if (t_rts == 1 && pb_ok) {', '// The skip (s.3.2): the stores the fast path and the capture make on unchanged images, in the capture\'s order.'),
    ('585d997d', RD, 3748, 'if (t_rts >= 2 && pb_ok) {', 't_rts_pb = true;'),
    ('585d997d', RD, 3787, 'if (t_rts >= 2 && t_rts_pa) {', 'uint32_t bits = t_rts_bits;'),
    ('585d997d', 'src/common/frameStats.h', 2486, 'RtsBadB,                 // rts_bad_b', 'RtsBadRx,                // rts_bad_rx'),
    ('585d997d', 'src/graphics/presentation/videoOut.cpp', 3255, '{"rts_bad_b", FS::Counter::RtsBadB, false},', '{"rts_bad_rx", FS::Counter::RtsBadRx, false},'),
]

def ref_ok(c, p, n, a, a1):
    try:
        s = show(c, p)
    except subprocess.CalledProcessError:
        return False
    return 0 < n < len(s) and s[n - 1].strip() == a and s[n].strip() == a1

for r in REFS:
    member('R %s:%s:%d' % r[:3], ref_ok(*r))
# Negative controls: a line off by one, an anchor with a changed character.
r = REFS[8]
member('N1 negative control (line + 1) fails', not ref_ok(r[0], r[1], r[2] + 1, r[3], r[4]))
member('N2 negative control (anchor "!= 3") fails', not ref_ok(r[0], r[1], r[2], 'if (t_rts != 3) {', r[4]))

print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)

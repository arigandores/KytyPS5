# F30k (HPP-721): checks of the code of ROADMAP s122 item 655(g)(1)-(3) and of the report links.
# Usage: python code_f30k.py <commit> [<commit> ...]   (the main commit and the worktree commit of binary T2)
# Prints ALL OK or FAILED with the failing members; exit 0 / 1.  A copy of docs/track-f/f30d/code_f30d.py, members changed.
import subprocess, sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
RD = 'src/graphics/host_gpu/renderer/renderDraw.cpp'
T = '\t'

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

def code(lines):
    # code lines with comment-only lines and trailing comments dropped
    return [l.split('//')[0].rstrip() for l in lines if is_code(l)]

COUNTERS = [('0x010u', 'bits', 'RtsBadR'), ('1u', 'xsrc', 'RtsBadXr'), ('2u', 'xsrc', 'RtsBadXc'), ('4u', 'xsrc', 'RtsBadXe'),
            ('0x040u', 'bits', 'RtsBadS'), ('0x080u', 'bits', 'RtsBadP'), ('0x100u', 'bits', 'RtsBadM'), ('0x200u', 'bits', 'RtsBadL')]
ADDED24 = []
for m, v, n in COUNTERS:
    ADDED24 += [T + 'if ((%s & %s) != 0) {' % (v, m), T + T + 'FS::Add(FS::Counter::%s, 1);' % n, T + '}']

# new code line -> parent code line (modified lines); inserted lines -> None
MODIFIED = {
    'void RtsReport(uint32_t bits, int frame, uint32_t age, uint32_t colors, bool depth, uint32_t xsrc) {':
        'void RtsReport(uint32_t bits, int frame, uint32_t age, uint32_t colors, bool depth) {',
    T * 3 + '          static_cast<bool>(state.depth_info.image_id), 0);':
        T * 3 + '          static_cast<bool>(state.depth_info.image_id));',
    T * 2 + 'if (t_rts != 5 && (!buffer.IsRendering() || CommandBuffer::PassBeginSerial() != rec->pass_serial)) {':
        T * 2 + 'if (!buffer.IsRendering() || CommandBuffer::PassBeginSerial() != rec->pass_serial) {',
    T * 3 + 'RtsReport(bits, m_context.GetGpu().GetFrameNum(), rec->age, cc, hd, xsrc);':
        T * 3 + 'RtsReport(bits, m_context.GetGpu().GetFrameNum(), rec->age, cc, hd);',
}
INSERTED_ONE = [T * 2 + 'uint32_t xsrc = 0;', T * 5 + 'xsrc |= 1u;', T * 4 + 'xsrc |= 2u;', T * 4 + 'xsrc |= 4u;']

for c in sys.argv[1:]:
    print('== commit', c)
    parent = c + '~1'
    g = show(c, 'src/common/gates.cpp')
    member('C1 knob row {"KYTY_RT_SKIP", "rtskip", 1, 5} once, no 1..4 row',
           sum(1 for l in g if l.strip() == '{"KYTY_RT_SKIP", "rtskip", 1, 5},') == 1
           and not any('"KYTY_RT_SKIP", "rtskip", 1, 4' in l for l in g))
    old_c = code(show(parent, RD))
    new_c = code(show(c, RD))
    # C2: back-transform the commit's code lines into the parent's: drop the 24 counter lines (one block), the four
    # xsrc lines (each once), and map the four modified lines back.  Equal => at 0..4 the instruction text is the
    # parent's apart from these.
    k = [i for i in range(len(new_c)) if new_c[i:i + 24] == ADDED24]
    c2 = len(k) == 1
    x = new_c[:k[0]] + new_c[k[0] + 24:] if c2 else new_c
    for l in INSERTED_ONE:
        h = [i for i, y in enumerate(x) if y == l]
        c2 = c2 and len(h) == 1
        if len(h) == 1:
            del x[h[0]]
    for nl, ol in MODIFIED.items():
        h = [i for i, y in enumerate(x) if y == nl]
        c2 = c2 and len(h) == 1
        if len(h) == 1:
            x[h[0]] = ol
    c2 = c2 and x == old_c
    member('C2 code lines = parent + 24 counter lines + 4 xsrc lines + 4 modified lines (signature, two calls, PB item 6)', c2)
    src = show(c, RD)
    t5 = [i + 1 for i, l in enumerate(src) if is_code(l) and ('t_rts != 5' in l or 't_rts == 5' in l or 't_rts >= 5' in l
                                                             or 't_rts < 5' in l or 't_rts > 4' in l)]
    member('C3 one test of t_rts against 5, in PB item 6 (line %s)' % t5,
           len(t5) == 1 and 'CommandBuffer::PassBeginSerial() != rec->pass_serial' in src[t5[0] - 1]
           and src[t5[0]].strip() == 'return C::RtsXbPass;')
    member('C3b the skip stays at value 1 only (2 tests t_rts == 1)', sum(1 for l in src if 't_rts == 1' in l and is_code(l)) == 2)
    member('C3c t_rts != 4 once, t_rts != 3 once (PB 3-4, PA 3 unchanged)',
           sum(1 for l in src if 't_rts != 4' in l and is_code(l)) == 1 and sum(1 for l in src if 't_rts != 3' in l and is_code(l)) == 1)
    # C4: the eight counters once each, inside RtsReport, after the race return and after rts_bad_rx, before the lines.
    i_fn = [i for i, l in enumerate(src) if l.startswith('void RtsReport(')]
    i_race = [i for i, l in enumerate(src) if l.strip() == 'FS::Add(FS::Counter::RtsRace, 1);']
    i_rx = [i for i, l in enumerate(src) if 'Counter::RtsBadRx' in l]
    i_ln = [i for i, l in enumerate(src) if l.strip() == 'if (t_rts_lines < 40) {']
    c4 = len(i_fn) == 1 and len(i_race) == 1 and len(i_rx) == 1 and len(i_ln) == 1
    for m, v, n in COUNTERS:
        h = [i for i, l in enumerate(src) if 'Counter::%s,' % n in l]
        c4 = c4 and len(h) == 1 and i_fn[0] < i_race[0] < i_rx[0] < h[0] < i_ln[0] \
            and src[h[0] - 1].strip() == 'if ((%s & %s) != 0) {' % (v, m)
    member('C4 eight counters once each in RtsReport after the race filter and rts_bad_rx', c4)
    calls = [l.strip() for l in src if 'RtsReport(' in l and not l.startswith('void RtsReport(') and is_code(l)]
    member('C4b two RtsReport calls (place A, post): %s' % calls, len(calls) == 2)
    xs = [i + 1 for i, l in enumerate(src) if 'xsrc |=' in l]
    member('C4c each xsrc bit set right after a bits |= 0x020u (lines %s)' % xs,
           len(xs) == 3 and all(src[i - 2].strip().startswith('bits |= 0x020u;') for i in xs))
    fs = show(c, 'src/common/frameStats.h')
    i_e = [i for i, l in enumerate(fs) if l.strip().startswith('RtsBadRx,')]
    names = ['RtsBadR', 'RtsBadXr', 'RtsBadXc', 'RtsBadXe', 'RtsBadS', 'RtsBadP', 'RtsBadM', 'RtsBadL']
    member('C5 enum: the eight counters after RtsBadRx in order',
           len(i_e) == 1 and [fs[i_e[0] + 3 + j].strip().split(',')[0] for j in range(8)] == names)
    vo = show(c, 'src/graphics/presentation/videoOut.cpp')
    pn = ['rts_bad_r', 'rts_bad_xr', 'rts_bad_xc', 'rts_bad_xe', 'rts_bad_s', 'rts_bad_p', 'rts_bad_m', 'rts_bad_l']
    member('C6 FrameTrace-x table: eight rows once each, after rts_bad_rx',
           all(sum(1 for l in vo if l.strip() == '{"%s", FS::Counter::%s, false},' % (p, n)) == 1 for p, n in zip(pn, names)))
    files = sorted(git('diff', '--name-only', parent, c).split())
    member('C7 files of the commit: %s' % files, files == sorted(['src/common/frameStats.h', 'src/common/gates.cpp', 'src/common/gates.h', RD,
                                                                 'src/graphics/presentation/videoOut.cpp']))
    member('C8 nothing under src/graphics/shader (translation signature)', not any(f.startswith('src/graphics/shader') for f in files))

# Report links: <commit>:<path>:<line> with the whole-line anchor and the +1 control line (filled from the report).
REFS = []
try:
    import refs_f30k
    REFS = refs_f30k.REFS
except ImportError:
    pass

def ref_ok(c, p, n, a, a1):
    try:
        s = show(c, p)
    except subprocess.CalledProcessError:
        return False
    return 0 < n < len(s) and s[n - 1].strip() == a and s[n].strip() == a1

for r in REFS:
    member('R %s:%s:%d' % r[:3], ref_ok(*r))
if REFS:
    r = REFS[0]
    member('N1 negative control (line + 1) fails', not ref_ok(r[0], r[1], r[2] + 1, r[3], r[4]))
    member('N2 negative control (anchor with a changed character) fails', not ref_ok(r[0], r[1], r[2], r[3] + 'x', r[4]))

print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)

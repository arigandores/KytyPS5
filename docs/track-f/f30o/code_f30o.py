# F30o (HPP-725): checks of the code of ROADMAP s122 item 664(e)(1)-(3) and of the report links.
# Usage: python code_f30o.py <commit> [<commit> ...]   (the main commit and the worktree commit of binary T3)
# Prints ALL OK or FAILED with the failing members; exit 0 / 1.  A copy of docs/track-f/f30k/code_f30k.py, members changed.
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

# The code lines the commit may insert into renderDraw.cpp (each block exactly as listed, nothing else, no line of the
# parent replaced or deleted).
BLOCKS = [
    ['constinit thread_local bool        t_rts_inj      = false;',
     'inline constexpr uint64_t   kRtsInjEvery = 4096;',
     'std::atomic<uint64_t>       g_rts_inj_n {0};'],
    ['bool RtsInjAttachLayout(const Image& image, ImageSubresourceRange r) noexcept {',
     T + 'const uint32_t levels = image.info.resources.levels;',
     T + 'const uint32_t layers = image.info.resources.layers;',
     T + 'if (image.info.IsVolume()) {',
     T + T + 'r.base_layer  = 0;',
     T + T + 'r.layer_count = 1;',
     T + '}',
     T + 'if (r.level_count == 0 || r.layer_count == 0 || r.base_level + r.level_count > levels ||',
     T + '    r.base_layer + r.layer_count > layers) {',
     T + T + 'return false;',
     T + '}',
     T + 'const auto& b = image.backing;',
     T + 'if (b.subresource_states.empty()) {',
     T + T + 'return b.state.layout == vk::ImageLayout::eColorAttachmentOptimal;',
     T + '}',
     T + 'for (uint32_t level = r.base_level; level < r.base_level + r.level_count; level++) {',
     T + T + 'for (uint32_t layer = r.base_layer; layer < r.base_layer + r.layer_count; layer++) {',
     T + T + T + 'const size_t index = static_cast<size_t>(level) * layers + layer;',
     T + T + T + 'if (index >= b.subresource_states.size() ||',
     T + T + T + '    b.subresource_states[index].layout != vk::ImageLayout::eColorAttachmentOptimal) {',
     T + T + T + T + 'return false;',
     T + T + T + '}',
     T + T + '}',
     T + '}',
     T + 'return true;',
     '}',
     'void RtsInject(uint32_t cc, const RenderColorInfo* colors, Image* const* img) {',
     T + 'namespace FS = Common::FrameStats;',
     T + 'if ((g_rts_inj_n.fetch_add(1, std::memory_order_relaxed) + 1) % kRtsInjEvery != 0) {',
     T + T + 'return;',
     T + '}',
     T + 'for (uint32_t i = 0; i < cc; i++) {',
     T + T + 'Image&      image = *img[i];',
     T + T + 'const auto& view = colors[i].desc.view_info;',
     T + T + 'const ImageSubresourceRange range {view.base_level, view.level_count, view.base_layer, view.layer_count};',
     T + T + 'if (image.binding.is_bound || !RtsInjAttachLayout(image, range)) {',
     T + T + T + 'continue;',
     T + T + '}',
     T + T + 'image.Transit(vk::ImageLayout::eGeneral,',
     T + T + '              vk::AccessFlagBits2::eColorAttachmentRead | vk::AccessFlagBits2::eColorAttachmentWrite, range,',
     T + T + '              vk::CommandBuffer {}, RenderPassEnd::TargetTransit);',
     T + T + 't_rts_inj = true;',
     T + T + 'FS::Add(FS::Counter::RtsInj, 1);',
     T + T + 'return;',
     T + '}',
     T + 'FS::Add(FS::Counter::RtsInjNone, 1);',
     '}'],
    [T + 't_rts_inj    = false;'],
    [T + T + 'if (t_rts == 6) [[unlikely]] {',
     T + T + T + 'RtsInject(cc, state.color_info, img.data());',
     T + T + '}'],
    [T + T + 'if (t_rts_inj) {',
     T + T + T + 't_rts_inj = false;',
     T + T + T + 'if (bits != 0 && t_rts_race && (bits & kRtsBitsA) == 0) {',
     T + T + T + T + 'FS::Add(C::RtsInjRace, 1);',
     T + T + T + '} else if ((bits & 0x040u) != 0) {',
     T + T + T + T + 'FS::Add(C::RtsInjS, 1);',
     T + T + T + '} else {',
     T + T + T + T + 'FS::Add(C::RtsInjNos, 1);',
     T + T + T + '}',
     T + T + '}'],
]
CNT = ['RtsInj', 'RtsInjS', 'RtsInjRace', 'RtsInjNos', 'RtsInjNone']
PRN = ['rts_inj', 'rts_inj_s', 'rts_inj_race', 'rts_inj_nos', 'rts_inj_none']

def find_all(lines, pred):
    return [i for i, l in enumerate(lines) if pred(l)]

for c in sys.argv[1:]:
    print('== commit', c)
    parent = c + '~1'
    g = show(c, 'src/common/gates.cpp')
    member('C1 knob row {"KYTY_RT_SKIP", "rtskip", 1, 6} once, no 1..5 row',
           sum(1 for l in g if l.strip() == '{"KYTY_RT_SKIP", "rtskip", 1, 6},') == 1
           and not any('"KYTY_RT_SKIP", "rtskip", 1, 5' in l for l in g))
    old_c = code(show(parent, RD))
    new_c = code(show(c, RD))
    # C2: the code lines of the commit with each listed block removed (each found exactly once, contiguous) = the parent's
    # code lines.  At 0..5 the instruction text is the parent's apart from these blocks.
    x = list(new_c)
    c2 = True
    for blk in BLOCKS:
        h = [i for i in range(len(x) - len(blk) + 1) if x[i:i + len(blk)] == blk]
        c2 = c2 and len(h) == 1
        if len(h) == 1:
            del x[h[0]:h[0] + len(blk)]
    member('C2 code lines = parent + the 5 listed blocks (%d lines) inserted whole, nothing else'
           % sum(len(b) for b in BLOCKS), c2 and x == old_c)
    src = show(c, RD)
    # C3: one test of t_rts against 6, at place B inside "if (t_rts >= 2 && pb_ok) {" after rts_pb / rts_chk_b, before
    # the snapshots and AcquireRenderTargets.
    t6 = find_all(src, lambda l: is_code(l) and ('t_rts == 6' in l or 't_rts != 6' in l or 't_rts >= 6' in l
                                                 or 't_rts > 5' in l or 't_rts < 6' in l))
    i_blk = find_all(src, lambda l: l == T + 'if (t_rts >= 2 && pb_ok) {')
    i_m0 = find_all(src, lambda l: l.strip() == 't_rts_meta0  = cache.MetaEpoch();')
    i_s0 = find_all(src, lambda l: l.strip() == 't_rts_ser0   = ImageStateSerial();')
    i_o0 = find_all(src, lambda l: l.strip() == 't_rts_open0  = buffer.IsRendering();')
    i_acq = find_all(src, lambda l: l.strip().startswith('auto rendering = AcquireRenderTargets(buffer, state.color_info'))
    c3 = len(t6) == 1 and len(i_blk) == 1 and len(i_m0) == 1 and len(i_s0) == 1 and len(i_o0) == 1 and len(i_acq) == 1
    if c3:
        b = i_blk[0]
        c3 = (src[b + 1].strip() == 't_rts_pb = true;' and src[b + 2].strip() == 'FS::Add(C::RtsPb, 1);'
              and src[b + 3].strip() == 'FS::Add(C::RtsChkB, 1);' and b + 3 < t6[0] < i_m0[0] < i_s0[0] < i_o0[0] < i_acq[0]
              and src[t6[0] + 1].strip() == 'RtsInject(cc, state.color_info, img.data());'
              and src[t6[0] + 2] == T + T + '}' and src[t6[0] + 3] == T + '}')
    member('C3 one test of t_rts against 6 (line %s), inside the PA and PB block, before the snapshots and the capture'
           % [i + 1 for i in t6], c3)
    calls = find_all(src, lambda l: is_code(l) and 'RtsInject(' in l and not l.startswith('void RtsInject('))
    member('C3b RtsInject called once', len(calls) == 1)
    member('C3c tests of the other values unchanged: t_rts == 1 x2, t_rts != 3 x1, t_rts != 4 x1, t_rts != 5 x1',
           sum(1 for l in src if 't_rts == 1' in l and is_code(l)) == 2 and sum(1 for l in src if 't_rts != 3' in l and is_code(l)) == 1
           and sum(1 for l in src if 't_rts != 4' in l and is_code(l)) == 1 and sum(1 for l in src if 't_rts != 5' in l and is_code(l)) == 1)
    # C4: the flag's life: set once (after the one Transit, in RtsInject), cleared in the latch and in the post, read once.
    sets = find_all(src, lambda l: is_code(l) and l.strip().startswith('t_rts_inj') and '= true' in l)
    clrs = find_all(src, lambda l: is_code(l) and l.strip().startswith('t_rts_inj') and '= false' in l)
    reads = find_all(src, lambda l: is_code(l) and 'if (t_rts_inj)' in l)
    i_tr = find_all(src, lambda l: l.strip() == 'image.Transit(vk::ImageLayout::eGeneral,')
    i_inj_fn = find_all(src, lambda l: l.startswith('void RtsInject('))
    member('C4 t_rts_inj: set x1 right after the Transit, cleared x2 (latch, post), read x1; Transit to eGeneral x1 in RtsInject',
           len(sets) == 1 and len(clrs) == 2 and len(reads) == 1 and len(i_tr) == 1 and len(i_inj_fn) == 1
           and i_inj_fn[0] < i_tr[0] and sets[0] == i_tr[0] + 3 and clrs[1] == reads[0] + 1)
    # C4b: the outcome counters once each, in the post block, before the report; the race predicate = RtsReport's.
    i_rr = find_all(src, lambda l: l.strip() == 'if (t_rts_race && (bits & kRtsBitsA) == 0) {')
    i_rep = find_all(src, lambda l: l.strip() == 'RtsReport(bits, m_context.GetGpu().GetFrameNum(), rec->age, cc, hd, xsrc);')
    hits = {n: find_all(src, lambda l, n=n: is_code(l) and '::%s, 1);' % n in l) for n in CNT}
    c4b = len(i_rr) == 1 and len(i_rep) == 1 and all(len(h) == 1 for h in hits.values()) and len(reads) == 1
    if c4b:
        c4b = (reads[0] < hits['RtsInjRace'][0] < hits['RtsInjS'][0] < hits['RtsInjNos'][0] < i_rep[0]
               and src[hits['RtsInjRace'][0] - 1].strip() == 'if (bits != 0 && t_rts_race && (bits & kRtsBitsA) == 0) {'
               and i_inj_fn[0] < hits['RtsInj'][0] < hits['RtsInjNone'][0] < i_inj_fn[0] + 30)
    member('C4b five counters once each: rts_inj / rts_inj_none in RtsInject; race / s / nos in the post before RtsReport', c4b)
    fs = show(c, 'src/common/frameStats.h')
    i_e = find_all(fs, lambda l: l.strip().startswith('RtsBadL,'))
    member('C5 enum: the five counters after RtsBadL in order',
           len(i_e) == 1 and [fs[i_e[0] + 4 + j].strip().split(',')[0] for j in range(5)] == CNT)
    vo = show(c, 'src/graphics/presentation/videoOut.cpp')
    i_l = find_all(vo, lambda l: l.strip() == '{"rts_bad_l", FS::Counter::RtsBadL, false},')
    member('C6 FrameTrace-x table: five rows once each, right after rts_bad_l',
           len(i_l) == 1 and [vo[i_l[0] + 2 + j].strip() for j in range(5)]
           == ['{"%s", FS::Counter::%s, false},' % (p, n) for p, n in zip(PRN, CNT)]
           and all(sum(1 for l in vo if '"%s"' % p in l) == 1 for p in PRN))
    files = sorted(git('diff', '--name-only', parent, c).split())
    member('C7 files of the commit: %s' % files, files == sorted(['src/common/frameStats.h', 'src/common/gates.cpp', 'src/common/gates.h', RD,
                                                                 'src/graphics/presentation/videoOut.cpp']))
    member('C8 nothing under src/graphics/shader (translation signature)', not any(f.startswith('src/graphics/shader') for f in files))

# Report links: <commit>:<path>:<line> with the whole-line anchor and the +1 control line (filled from the report).
REFS = []
try:
    import refs_f30o
    REFS = refs_f30o.REFS
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

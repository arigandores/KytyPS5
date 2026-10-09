# F30p (HPP-726, Red Team): independent check of the F30o code (ROADMAP s122 item 664(e), (zh)) and its mutants (m1)-(m7).
# Usage: python chk_f30p.py      (reads git objects, the worktree state and the T3 copy; no build, no game)
# Prints PASS/FAIL per member, then the mutant table; ALL OK or FAILED; exit 0 / 1.
import hashlib, re, subprocess, sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
WT = 'C:/kyty/f287/f30o/wt'
T2, T3, MAIN = '6fbdcf67', 'ea38426b', 'd25a78bc'
RD = 'src/graphics/host_gpu/renderer/renderDraw.cpp'
IMG = 'src/graphics/host_gpu/renderer/image/image.cpp'
BIN = 'C:/kyty/f287/bin/kyty_emulator_50596951.exe'
BIN_SHA = '505969510fb20f7ce56a5195b3b6d2209af812bc0c2c85eccb6368a712b1bf34'
VER = 'KytyPS5-2026-09-15-6a2987a-1908-gea38426b'
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
TAB = chr(9)
NL = chr(10)

def git(*a, repo=REPO):
    return subprocess.run([G, '-C', repo] + list(a), capture_output=True, check=True).stdout.decode('utf-8')

def show(c, p):
    return git('show', '%s:%s' % (c, p)).split(NL)

ok = True
def member(name, cond):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name)
    ok = ok and bool(cond)

def strip_comment(l):
    return l.split('//')[0].rstrip()

def is_code(l):
    return strip_comment(l).strip() != ''

def pm(d):
    return [l for l in d.split(NL) if (l.startswith('+') or l.startswith('-')) and not l.startswith('+++') and not l.startswith('---')]

# ---- D0, D1: T3 is T2 plus exactly the main commit
par = git('rev-parse', T3 + '~1').strip()
member('D0 parent of T3 %s is T2 %s' % (T3, T2), par.startswith(T2))
d_t3 = pm(git('diff', T2, T3, '--', 'src'))
d_main = pm(git('show', '--format=', MAIN, '--', 'src'))
member('D1 +/- lines of T2..T3 = +/- lines of main %s (%d / %d)' % (MAIN, len(d_t3), len(d_main)), d_t3 == d_main and len(d_t3) > 0)
files = sorted(git('diff', '--name-only', T2, T3).split())
member('D1b files T2..T3 = 5, none under src/graphics/shader: %s' % files,
       len(files) == 5 and not any(f.startswith('src/graphics/shader') for f in files))

t2_src = show(T2, RD)

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
    while j < len(src) and src[j] != '}':
        j += 1
    return i[0], j

def idx(src, pred, lo=0, hi=None):
    hi = len(src) if hi is None else hi
    return [k for k in range(lo, hi) if pred(src[k])]

def checks(src):
    r = {}
    # D2: the t_rts value tests = T2's plus exactly one "t_rts == 6"
    r['D2'] = t_rts_tests(src) == sorted(t_rts_tests(t2_src) + [('==', '6')])
    # D3: the call - inside "if (t_rts >= 2 && pb_ok) {" of RtsPlaceB, after rts_pb / rts_chk_b, before the 3 snapshots and the capture
    b0, b1 = find_fn(src, 'RenderState RenderExecutor::RtsPlaceB(')
    d3 = b0 is not None
    if d3:
        calls = idx(src, lambda l: is_code(l) and 'RtsInject(' in l and not l.startswith('void RtsInject('))
        blk = idx(src, lambda l: l == TAB + 'if (t_rts >= 2 && pb_ok) {', b0, b1)
        skip = idx(src, lambda l: l == TAB + 'if (t_rts == 1 && pb_ok) {', b0, b1)
        m0 = idx(src, lambda l: l.strip() == 't_rts_meta0  = cache.MetaEpoch();', b0, b1)
        s0 = idx(src, lambda l: l.strip() == 't_rts_ser0   = ImageStateSerial();', b0, b1)
        o0 = idx(src, lambda l: l.strip() == 't_rts_open0  = buffer.IsRendering();', b0, b1)
        acq = idx(src, lambda l: l.strip().startswith('auto rendering = AcquireRenderTargets(buffer, state.color_info'), b0, b1)
        d3 = all(len(x) == 1 for x in (calls, blk, skip, m0, s0, o0, acq))
        if d3:
            c = calls[0]
            end = idx(src, lambda l: l == TAB + '}', blk[0], b1)
            d3 = (skip[0] < blk[0] < c < end[0] < m0[0] < s0[0] < o0[0] < acq[0]
                  and src[blk[0] + 3].strip() == 'FS::Add(C::RtsChkB, 1);' and blk[0] + 3 < c
                  and src[c - 1].strip() == 'if (t_rts == 6) [[unlikely]] {'
                  and src[c].strip() == 'RtsInject(cc, state.color_info, img.data());')
    r['D3'] = d3
    # D4: RtsInject - colour targets only (i < cc), never is_bound, the eligibility function, one Transit with the capture's
    # arguments except the layout; the counter and its modulus only here.
    f0, f1 = find_fn(src, 'void RtsInject(')
    d4 = f0 is not None
    if d4:
        body = src[f0:f1 + 1]
        loops = [l.strip() for l in body if l.strip().startswith('for (')]
        tr = [k for k, l in enumerate(body) if 'Transit(' in l and is_code(l)]
        cont = [l.strip() for l in body if 'continue;' in l]
        d4 = (loops == ['for (uint32_t i = 0; i < cc; i++) {'] and len(tr) == 1 and len(cont) == 1
              and any(l.strip() == 'if (image.binding.is_bound || !RtsInjAttachLayout(image, range)) {' for l in body)
              and any(l.strip() == 'const auto& view = colors[i].desc.view_info;' for l in body)
              and any(l.strip() == 'const ImageSubresourceRange range {view.base_level, view.level_count, view.base_layer, view.layer_count};' for l in body))
        if d4:
            t = ' '.join(x.strip() for x in body[tr[0]:tr[0] + 3])
            d4 = t == ('image.Transit(vk::ImageLayout::eGeneral, vk::AccessFlagBits2::eColorAttachmentRead | '
                       'vk::AccessFlagBits2::eColorAttachmentWrite, range, vk::CommandBuffer {}, RenderPassEnd::TargetTransit);')
            d4 = d4 and body[tr[0] + 3].strip() == 't_rts_inj = true;' and body[tr[0] + 4].strip() == 'FS::Add(FS::Counter::RtsInj, 1);'
    r['D4'] = d4
    # D5: g_rts_inj_n read/written only in RtsInject, once, modulo kRtsInjEvery = 4096; RtsInjNone only after the loop
    uses = idx(src, lambda l: is_code(l) and 'g_rts_inj_n' in l)
    d5 = f0 is not None and len(uses) == 2 and uses[0] < f0 < uses[1] < f1
    d5 = d5 and src[uses[1]].strip() == 'if ((g_rts_inj_n.fetch_add(1, std::memory_order_relaxed) + 1) % kRtsInjEvery != 0) {'
    d5 = d5 and sum(1 for l in src if strip_comment(l).strip() == 'inline constexpr uint64_t   kRtsInjEvery = 4096;') == 1
    d5 = d5 and len(idx(src, lambda l: is_code(l) and 'RtsInjNone' in l)) == 1
    r['D5'] = d5
    # D6: the outcome in the post - inside "if (t_rts >= 2 && t_rts_pa) {", after the bit S line, before RtsReport; the race
    # predicate = RtsReport's (bits != 0 is the condition RtsReport runs under); one counter per branch; the flag cleared first.
    p0, p1 = find_fn(src, 'void RenderExecutor::RtsPost(')
    rr0, rr1 = find_fn(src, 'void RtsReport(')
    d6 = p0 is not None and rr0 is not None
    if d6:
        rep_pred = idx(src, lambda l: l.strip() == 'if (t_rts_race && (bits & kRtsBitsA) == 0) {', rr0, rr1)
        rd = idx(src, lambda l: l.strip() == 'if (t_rts_inj) {', p0, p1)
        sbit = idx(src, lambda l: l.strip() == 'bits |= 0x040u; // S', p0, p1)
        rep = idx(src, lambda l: l.strip() == 'RtsReport(bits, m_context.GetGpu().GetFrameNum(), rec->age, cc, hd, xsrc);', p0, p1)
        outer = idx(src, lambda l: l == TAB + 'if (t_rts >= 2 && t_rts_pa) {', p0, p1)
        d6 = all(len(x) == 1 for x in (rep_pred, rd, sbit, rep, outer)) and outer[0] < sbit[0] < rd[0] < rep[0]
        if d6:
            k = rd[0]
            exp = ['if (t_rts_inj) {', 't_rts_inj = false;', 'if (bits != 0 && t_rts_race && (bits & kRtsBitsA) == 0) {',
                   'FS::Add(C::RtsInjRace, 1);', '} else if ((bits & 0x040u) != 0) {', 'FS::Add(C::RtsInjS, 1);', '} else {',
                   'FS::Add(C::RtsInjNos, 1);', '}', '}']
            d6 = [x.strip() for x in src[k:k + len(exp)]] == exp and src[k + len(exp)].strip() == 'if (bits != 0) {'
            for n in ('RtsInjRace', 'RtsInjS', 'RtsInjNos'):
                d6 = d6 and len(idx(src, lambda l, n=n: is_code(l) and ('C::%s,' % n) in l)) == 1
    r['D6'] = d6
    # D7: the flag - set once (RtsInject), cleared in the latch and the post, read once
    sets = idx(src, lambda l: is_code(l) and l.strip().startswith('t_rts_inj') and '= true' in l)
    clrs = idx(src, lambda l: is_code(l) and l.strip().startswith('t_rts_inj') and '= false' in l and 'constinit' not in l)
    reads = idx(src, lambda l: is_code(l) and 'if (t_rts_inj' in l)
    l0, l1 = find_fn(src, '[[gnu::noinline]] void RenderExecutor::RtsLatchSlow(')
    r['D7'] = (len(sets) == 1 and f0 is not None and f0 < sets[0] < f1 and len(clrs) == 2 and l0 is not None
               and l0 < clrs[0] < l1 and p0 < clrs[1] < p1 and len(reads) == 1)
    return r

res = checks(show(T3, RD))
for k in sorted(res):
    member('%s on T3 %s' % (k, T3), res[k])
res_main = checks(show(MAIN, RD))
member('D2-D7 on main %s' % MAIN, all(res_main.values()))

# D8: the eligibility reads the tracker as GetBarriers does (index level * layers + layer; a volume has one layer)
img = show(T3, IMG)
member('D8 GetBarriers: index level * info.resources.layers + layer, volume base_layer 0 / layer_count 1',
       any(l.strip() == 'const auto index = level * info.resources.layers + layer;' for l in img)
       and any(l.strip() == 'range->base_layer  = 0;' for l in img) and any(l.strip() == 'range->layer_count = 1;' for l in img))

# D9: the capture's colour Transit (the one the perturbation mirrors): layout from is_bound, access colour RW, view range,
# lazy handle, TargetTransit
rd3 = show(T3, RD)
a0, a1 = find_fn(rd3, 'RenderState RenderExecutor::AcquireRenderTargets(')
seg = rd3[a0:a1]
tx = [k for k, l in enumerate(seg) if l.strip() == 'image.Transit(layout, image.binding.attachment_access,']
d9 = len(tx) == 1
if d9:
    k = tx[0]
    d9 = (' '.join(x.strip() for x in seg[k:k + 4]) == 'image.Transit(layout, image.binding.attachment_access, ImageSubresourceRange '
          '{view.base_level, view.level_count, view.base_layer, view.layer_count}, vk::CommandBuffer {}, RenderPassEnd::TargetTransit);'
          and any(x.strip() == 'const auto  layout = image.binding.is_bound ? vk::ImageLayout::eGeneral' for x in seg[k - 8:k])
          and any(x.strip() == 'vk::AccessFlagBits2::eColorAttachmentRead | vk::AccessFlagBits2::eColorAttachmentWrite;' for x in seg[k - 6:k]))
member('D9 capture colour Transit: layout by is_bound, colour RW access, view range, lazy handle, TargetTransit', d9)

# ---- B: the T3 binary and its worktree (no own build: see the review)
h = hashlib.sha256(open(BIN, 'rb').read()).hexdigest()
member('B1 sha256 of %s = %s...' % (BIN, BIN_SHA[:8]), h == BIN_SHA)
data = open(BIN, 'rb').read()
member('B2 version string %s in the image' % VER, data.count(VER.encode()) >= 1)
member('B3 translation signature %s... in the image' % SIG[:8], data.count(SIG.encode()) >= 1)
member('B4 names rts_inj, rts_inj_s, rts_inj_race, rts_inj_nos, rts_inj_none in the image (NUL-terminated)',
       all(data.count(n.encode() + bytes([0])) >= 1 for n in ('rts_inj', 'rts_inj_s', 'rts_inj_race', 'rts_inj_nos', 'rts_inj_none')))
head = git('rev-parse', 'HEAD', repo=WT).strip()
st = git('status', '--porcelain', '--', 'src', repo=WT).strip()
member('B5 worktree %s HEAD = %s, src clean' % (WT, T3), head.startswith(T3) and st == '')

# ---- mutants (m1)-(m7) on the T3 text: each must fail at least one of D2-D7
base = show(T3, RD)
def mut(name, fn):
    s = list(base)
    try:
        s2 = fn(s)
    except Exception as e:
        return name, 'NOT APPLIED %s' % e, False
    if s2 == base:
        return name, 'NOT APPLIED (no change)', False
    r = checks(s2)
    failed = [k for k in sorted(r) if not r[k]]
    return name, ('killed by ' + ','.join(failed)) if failed else 'SURVIVED', bool(failed)

def find1(s, text):
    k = [i for i, l in enumerate(s) if l == text]
    if len(k) != 1:
        raise ValueError('anchor %r x%d' % (text, len(k)))
    return k[0]

INJ = [TAB * 2 + 'if (t_rts == 6) [[unlikely]] {', TAB * 3 + 'RtsInject(cc, state.color_info, img.data());', TAB * 2 + '}']
def cut_inj(s):
    k = find1(s, INJ[0])
    del s[k:k + 3]
    return s
def m1(s):  # after the snapshots and the capture (K_S dead)
    s = cut_inj(s)
    k = find1(s, TAB + 't_rts_open1    = buffer.IsRendering();')
    s[k + 1:k + 1] = [TAB + 'if (t_rts == 6 && t_rts_pb) [[unlikely]] {', TAB * 2 + 'RtsInject(cc, state.color_info, img.data());', TAB + '}']
    return s
def m1b(s):  # between ser0 and the capture (S from the perturbation itself)
    s = cut_inj(s)
    k = find1(s, TAB + 't_rts_open0  = buffer.IsRendering();')
    s[k + 1:k + 1] = [TAB + 'if (t_rts == 6 && t_rts_pb) [[unlikely]] {', TAB * 2 + 'RtsInject(cc, state.color_info, img.data());', TAB + '}']
    return s
def m2a(s):  # the depth target too
    f0, f1 = find_fn(s, 'void RtsInject(')
    k = [i for i in range(f0, f1) if s[i] == TAB + 'for (uint32_t i = 0; i < cc; i++) {']
    s[k[0]] = TAB + 'for (uint32_t i = 0; i <= cc; i++) {'
    return s
def m2b(s):  # an is_bound target too
    k = find1(s, TAB * 2 + 'if (image.binding.is_bound || !RtsInjAttachLayout(image, range)) {')
    s[k] = TAB * 2 + 'if (!RtsInjAttachLayout(image, range)) {'
    return s
def m3(s):  # rts_inj without the Transit
    k = find1(s, TAB * 2 + 'image.Transit(vk::ImageLayout::eGeneral,')
    del s[k:k + 3]
    return s
def m4(s):  # rts_inj_s counts S of draws that were not perturbed
    k = find1(s, TAB * 2 + 'if (t_rts_inj) {')
    s[k] = TAB * 2 + 'if (t_rts_inj || (bits & 0x040u) != 0) {'
    return s
def m5(s):  # the race of a perturbed draw does not go to rts_inj_race
    k = find1(s, TAB * 3 + 'if (bits != 0 && t_rts_race && (bits & kRtsBitsA) == 0) {')
    s[k] = TAB * 3 + 'if (false) {'
    return s
def m6(s):  # N over all draws at place B, not PA and PB
    k = find1(s, TAB + 'bool pb_ok = false;')
    s[k:k] = [TAB + 'if (t_rts == 6 && !t_rts_pa) {', TAB * 2 + 'g_rts_inj_n.fetch_add(1, std::memory_order_relaxed);', TAB + '}']
    return s
def m6b(s):  # N over all draws at place B: the call before PB
    s = cut_inj(s)
    k = find1(s, TAB + 'bool pb_ok = false;')
    s[k:k] = INJ_TOP
    return s
INJ_TOP = [TAB + 'if (t_rts == 6) [[unlikely]] {', TAB * 2 + 'RtsInject(cc, state.color_info, img.data());', TAB + '}']
def m7(s):  # the path at 0..5 changes: the perturbation at 5 too
    k = find1(s, INJ[0])
    s[k] = TAB * 2 + 'if (t_rts >= 5) [[unlikely]] {'
    return s
def m7b(s):  # the path at 0..5 changes: the outcome counted at every value
    k = find1(s, TAB * 2 + 'if (t_rts_inj) {')
    s[k] = TAB * 2 + 'if (true) {'
    return s
def m7c(s):  # the path at 0..5 changes: PB item 4 dropped at 6 (as at 4) - "=6 = =2" broken
    k = find1(s, TAB * 2 + 'if (t_rts != 4) {')
    s[k] = TAB * 2 + 'if (t_rts != 4 && t_rts != 6) {'
    return s

print('-- mutants')
killed = 0
ms = [('m1', m1), ('m1b', m1b), ('m2a', m2a), ('m2b', m2b), ('m3', m3), ('m4', m4), ('m5', m5), ('m6', m6), ('m6b', m6b),
      ('m7', m7), ('m7b', m7b), ('m7c', m7c)]
for name, fn in ms:
    n, how, k = mut(name, fn)
    print('MUT %-4s %s' % (n, how))
    killed += k
member('mutants killed %d of %d' % (killed, len(ms)), killed == len(ms))
# control: the unmutated text passes (checks are not vacuous) - already D2-D7 above; the T2 text must fail (no perturbation)
r2 = checks(t2_src)
member('control: T2 text fails D3-D7 (%s)' % ','.join(k for k in sorted(r2) if not r2[k]),
       not any(r2[k] for k in ('D3', 'D4', 'D5', 'D6', 'D7')))

print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)

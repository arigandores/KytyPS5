# F30e (HPP-710, Red Team): check of the references <commit>:<path>:<line> of docs/track-f/f30e-review.md -
# the anchor is the WHOLE stripped line, the control is the stripped line +1; negative controls N1 (line + 1) and N2
# (altered anchor) must fail.  Usage: python refs_f30e.py [repo]  (default C:/kyty/KytyPS5).  Prints ALL OK.
import subprocess, sys
REPO = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/KytyPS5'
COMMIT = '585d997d'
REFS = [
 [
  "src/common/frameStats.cpp",
  197,
  ": static_cast<uint32_t>(Counter::Count);",
  "Detail::g_count_limit.store(limit, std::memory_order_relaxed);"
 ],
 [
  "src/common/frameStats.h",
  2486,
  "RtsBadB,                 // rts_bad_b",
  "RtsBadRx,                // rts_bad_rx"
 ],
 [
  "src/common/gates.cpp",
  438,
  "{\"KYTY_RT_SKIP\", \"rtskip\", 1, 4},",
  "// Session 128, MEASUREMENT ONLY: skip the read-only arming of a buffer synchronization on GuestGpu (1)"
 ],
 [
  "src/common/gates.cpp",
  504,
  "states[index].store(parsed < definition.limit ? parsed : definition.limit,",
  "std::memory_order_relaxed);"
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  1333,
  "inline constexpr uint32_t kRtsBitsA = 0x001u | 0x002u | 0x004u | 0x008u | 0x400u;",
  ""
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  1593,
  "if (t_rts_race && (bits & kRtsBitsA) == 0) {",
  "FS::Add(FS::Counter::RtsRace, 1);"
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  1602,
  "if ((bits & 0x3f0u) != 0) {",
  "FS::Add(FS::Counter::RtsBadB, 1);"
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  1605,
  "if ((bits & 0x030u) != 0) {",
  "FS::Add(FS::Counter::RtsBadRx, 1);"
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  1609,
  "t_rts_lines++;",
  "LOGF(\"RtSkipVerify: MISMATCH frame=%d bits=0x%03x reg=%u chain=%u colors=%u depth=%u pa=1 pb=%u mode=%u\\n\", frame,"
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  1658,
  "cache.MetaEpoch() == fast.meta_epoch && stencil_kept()) {",
  "image.MarkGpuModified();"
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  1685,
  "RtsNoteSlow(stamp != fast.stamp); // Session 127, knob \"rtskip\" (I3): the slow path and its bind_stamp race",
  "}"
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  3436,
  "if ((t_rts_logged & (1u << (16u + armed))) == 0) {",
  "t_rts_logged |= 1u << (16u + armed);"
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  3441,
  "t_rts = armed; // a change between 1, 2 and 3 keeps the records",
  "Common::Rk3::t_hooks |= Common::Rk3::HookRts;"
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  3499,
  "} else if (t_rts != 3 && t_rts_reg) {",
  "why = C::RtsXaReg;"
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  3522,
  "if (t_rts == 1 && t_rts_pa) {",
  "// The skip (s.3.2): the record's outputs, then the stores of the resolution's memo hits in its order - the LRU"
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  3574,
  "if (t_rts >= 2 && t_rts_pa) {",
  "// The resolution half of the self-check (s.5.1 step 2, s.5.2)."
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  3683,
  "if (t_rts != 4) {",
  "// 3 (N2, N4): the metadata epoch the record's fast records were taken at."
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  3719,
  "if (t_rts == 1 && pb_ok) {",
  "// The skip (s.3.2): the stores the fast path and the capture make on unchanged images, in the capture's order."
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  3722,
  "FS::Add(C::RtsSkip, 1);",
  "for (uint32_t i = 0; i < rec->nt; i++) {"
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  3748,
  "if (t_rts >= 2 && pb_ok) {",
  "t_rts_pb = true;"
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  3787,
  "if (t_rts >= 2 && t_rts_pa) {",
  "uint32_t bits = t_rts_bits;"
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  3815,
  "if (t_rts_meta1 != t_rts_meta0) {",
  "bits |= 0x100u; // M"
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  3818,
  "if (t_rts_slow || t_rts_refind) {",
  "bits |= 0x200u; // L"
 ],
 [
  "src/graphics/host_gpu/renderer/renderDraw.cpp",
  3954,
  "if (t_rts >= 2) {",
  "FS::Add(C::RtsRec, 1);"
 ],
 [
  "src/graphics/presentation/videoOut.cpp",
  3255,
  "{\"rts_bad_b\", FS::Counter::RtsBadB, false},",
  "{\"rts_bad_rx\", FS::Counter::RtsBadRx, false},"
 ],
 [
  "src/graphics/presentation/videoOut.cpp",
  3256,
  "{\"rts_bad_rx\", FS::Counter::RtsBadRx, false},",
  "// Session 128, knob \"protceil\" (design128.md s.7.1, ROADMAP s122 item 89(zh)); pc_u_live after the loop."
 ]
]
_cache = {}
def lines(path):
    if path not in _cache:
        out = subprocess.run(['git', '-C', REPO, 'show', COMMIT + ':' + path], capture_output=True, text=True,
                             encoding='utf-8').stdout
        _cache[path] = out.split(chr(10))
    return _cache[path]
def check(path, n, anchor, nxt):
    L = lines(path)
    return 1 <= n < len(L) and L[n - 1].strip() == anchor and L[n].strip() == nxt
ok = True
for path, n, anchor, nxt in REFS:
    r = check(path, n, anchor, nxt)
    ok &= r
    print(('PASS' if r else 'FAIL'), 'R', COMMIT + ':' + path + ':' + str(n))
p, n, a, x = REFS[0]
r = not check(p, n + 1, a, x); ok &= r
print(('PASS' if r else 'FAIL'), 'N1 negative control (line + 1) fails')
p, n, a, x = next(r for r in REFS if r[0].endswith('gates.cpp') and r[1] == 438)
r = not check(p, n, a.replace('1, 4', '1, 3'), x); ok &= r
print(('PASS' if r else 'FAIL'), 'N2 negative control (anchor 1, 3) fails')
print('ALL OK' if ok else 'NOT OK')
sys.exit(0 if ok else 1)

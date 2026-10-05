"""S17a4 (HPP-622): the references of docs/track-s/s17a4/README.md - every anchor is the whole line N of
`git show <commit>:<path>` (OK), and the control: the same anchor is NOT the line N+1 (NOT OK expected).
Usage: python refs_s17a4.py  (run in C:/kyty/KytyPS5); prints ALL OK when every anchor holds and every control fails."""
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
C = '9238a182'
SR = 'src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp'
SH = 'src/graphics/host_gpu/renderer/pipeline/shaderReplay.h'
PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
T = 'tests/shaderCfgTests.cpp'
REFS = [
    (SR, 643, '\tstd::vector<uint8_t> kept_role(raw.size(), 0u); // S17a4: role of the classifier before ROLE_KEEP (kept_address)'),
    (SR, 705, '\t\t\tkept_role[i]    = role;'),
    (SR, 796, '\tif (culprits != 0) {'),
    (SR, 797, '\t\twhy = fmt::format("residual branch={} culprit={}:role{} n={}", culprit_addr ? "addr" : "exact", culprit,'),
    (SR, 823, 'bool CountReject(CaptureStats& stats, const std::string& why) {'),
    (SR, 824, '\tconst bool residual = why.starts_with("residual");'),
    (SR, 835, '\treturn residual ? stats.canon_residual <= 20u : stats.canon_self + stats.canon_base + stats.canon_big <= 20u;'),
    (SR, 1187, '\t\t\t\tHandleSpec(*slot.spec);'),
    (SR, 1234, '\t\tif (!Canonicalize(*item.plan, item.trace, item.live, words, user_words, why, TestStand() == Stand::Canon)) {'),
    (SR, 1237, '\t\t\tif (CountReject(m_stats, why)) {'),
    (SR, 1238, '\t\t\t\tLOGF("ShaderReplay: capture reject why=%s hash=0x%016" PRIx64 " words=%zu\\n", why.c_str(),'),
    (SH, 350, 'bool CountReject(CaptureStats& stats, const std::string& why);'),
    (PC, 7053, '\tif (mode == 0) {'),
    (PC, 7082, '\tif (ShaderReplay::CaptureOn()) {'),
    (T, 15495, 'void TestShaderReplayWalkBits() {'),
    (T, 15663, '    Check(!canonical && why.starts_with("residual branch=addr culprit=30:role2 ") && Common::ContainsStr(why, " n=") &&'),
    (T, 15667, '  // (b2) S17a4, item 541(c)(5): the exact branch of the residual check. The shader of (a) with W (num_records of the'),
    (T, 15725, '    const std::string expected = "residual branch=exact culprit=" + std::to_string(w_index) + ":role0 n=1";'),
    (T, 15782, '  // (e) S17a4, item 541(c)(2)-(3): CountReject - a residual reject with its suffix counts in canon_residual (not in'),
    (T, 15788, '      printed_residual += SR::CountReject(stats, "residual branch=addr culprit=30:role2 n=1") ? 1 : 0;'),
    (T, 16390, '  RUN(TestShaderReplayWalkBits);'),
]
cache = {}
ok = True
for path, line, anchor in REFS:
    if path not in cache:
        text = subprocess.run([GIT, 'show', '%s:%s' % (C, path)], capture_output=True, check=True).stdout
        cache[path] = text.decode('utf-8').replace('\r\n', '\n').split('\n')
    lines = cache[path]
    hit = lines[line - 1] == anchor
    control = lines[line] == anchor
    print('%s:%s:%d %s | +1 %s | +1 text: %s' % (C, path, line, 'OK' if hit else 'FAIL', 'OK' if control else 'NOT OK',
                                                lines[line].strip()[:90]))
    ok &= hit and not control
print('refs %d' % len(REFS))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)

"""S17a3 (HPP-620): the references of docs/track-s/s17a3/README.md section 6 - every anchor is the whole line N of
`git show <commit>:<path>` (OK), and the control: the same anchor is NOT the line N+1 (NOT OK expected).
Usage: python refs_s17a3.py  (run in C:/kyty/KytyPS5); prints ALL OK when every anchor holds and every control fails."""
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
C = '9635cb0f'
SR = 'src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp'
PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
T = 'tests/shaderCfgTests.cpp'
REFS = [
    (SR, 586, 'bool SubstitutionHolds(const IR::ResourcePlan& plan, const std::vector<Word>& raw, size_t user_words, size_t i,'),
    (SR, 615, 'bool Canonicalize(const IR::ResourcePlan& plan, const Trace& trace, const IR::ResourceSpecialization& live,'),
    (SR, 642, '\tstd::vector<uint8_t> kept_address(raw.size(), 0u);'),
    (SR, 651, '\t\tfor (const uint32_t delta: {0x100u, 0x1u}) {'),
    (SR, 699, '\t\tuint32_t value = Canonical(role, raw[i].value, descriptor);'),
    (SR, 700, '\t\tif (value != raw[i].value && !SubstitutionHolds(plan, raw, user_words, i, role, value, base, live)) {'),
    (SR, 703, '\t\t\tkept_address[i] = role != ROLE_INERT ? 1u : 0u;'),
    (SR, 778, '\t\tif (kept_address[i] != 0u ||'),
    (SR, 1155, '\t\t\t\tHandleSpec(*slot.spec);'),
    (SR, 1202, '\t\tif (!Canonicalize(*item.plan, item.trace, item.live, words, user_words, why, TestStand() == Stand::Canon)) {'),
    (PC, 7053, '\tif (mode == 0) {'),
    (PC, 7082, '\tif (ShaderReplay::CaptureOn()) {'),
    (T, 15495, 'void TestShaderReplayWalkBits() {'),
    (T, 16295, '  RUN(TestShaderReplayWalkBits);'),
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

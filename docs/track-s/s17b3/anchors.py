# S17b3 (HPP-621): anchors of the review - line N of `git show <commit>:<path>` contains the anchor, line N+1 contains the
# +1 text and does not contain the anchor (control +1). Prints one line per ref and ALL OK.
import subprocess

G = 'C:/Program Files/Git/cmd/git.exe'
R = 'C:/kyty/KytyPS5'
C = '9635cb0f'
SR = 'src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp'
PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
SW = 'src/graphics/shader/recompiler/ir/passes/SrtWalker.cpp'
REFS = [
    (C, SR, 41, "if (value == nullptr || value[0] < '1' || value[0] > '3' || value[1] != '\\0') {", 'return 0;'),
    (C, SR, 49, 'bool CaptureOn() {', 'return Mode() == 1 || Mode() == 2;'),
    (C, SR, 586, 'bool SubstitutionHolds(const IR::ResourcePlan& plan, const std::vector<Word>& raw, size_t user_words, size_t i,',
     'Role role, uint32_t value, const RunResult& base, const IR::ResourceSpecialization& live) {'),
    (C, SR, 591, 'if (!now.ok || !now.complete || !(now.specialization == live) || now.requested.size() != base.requested.size()) {',
     'return false;'),
    (C, SR, 594, 'const uint64_t difference = static_cast<uint64_t>(value) - static_cast<uint64_t>(raw[i].value);',
     'uint64_t       shift      = 0;'),
    (C, SR, 642, 'std::vector<uint8_t> kept_address(raw.size(), 0u);', 'for (size_t i = 0; i < raw.size(); i++) {'),
    (C, SR, 700, 'if (value != raw[i].value && !SubstitutionHolds(plan, raw, user_words, i, role, value, base, live)) {',
     '// Kept as read (ROLE_KEEP).'),
    (C, SR, 703, 'kept_address[i] = role != ROLE_INERT ? 1u : 0u;', 'role            = ROLE_KEEP;'),
    (C, SR, 726, 'auto check = Run(plan, canonical, user_words, false);', 'if (stand_word < canonical.size()) {'),
    (C, SR, 778, 'if (kept_address[i] != 0u ||',
     '(word.role == ROLE_KEEP && word.value >= 0x10000u && addresses.contains(word.value))) {'),
    (C, SR, 1155, 'HandleSpec(*slot.spec);', '}'),
    (C, SR, 1202, 'if (!Canonicalize(*item.plan, item.trace, item.live, words, user_words, why, TestStand() == Stand::Canon)) {',
     'if (why.starts_with("self")) {'),
    (C, SR, 1205, '} else if (why == "residual") {', 'm_stats.canon_residual++;'),
    (C, SR, 1212, 'm_stats.canon_mismatch = m_stats.canon_self + m_stats.canon_residual;',
     'if (m_stats.canon_self + m_stats.canon_residual + m_stats.canon_base + m_stats.canon_big <= 20u) {'),
    (C, SR, 1214, 'LOGF("ShaderReplay: capture reject why=%s hash=0x%016" PRIx64 " words=%zu\\n", why.c_str(),',
     'item.plan->shader_hash, 2 + item.trace.user_data.size() + item.trace.reads.size());'),
    (C, SR, 1349, ': m_writer(std::make_unique<Writer>(store, std::move(initial), generation)) {}', ''),
    (C, PC, 7053, 'if (mode == 0) {', 'return;'),
    (C, PC, 7082, 'if (ShaderReplay::CaptureOn()) {', 'ShaderReplay::Catalogue initial;'),
    (C, PC, 7087, 'm_replay_capture = std::make_unique<ShaderReplay::Capture>(*m_replay_store, std::move(initial),',
     'std::max(generation, corrupt));'),
    (C, SW, 1870, 'out = ((B() << 32u) | static_cast<uint32_t>(A())) & (AddressMask & ~uint64_t {3});', '}'),
    (C, SW, 1904, 'const auto  base      = ((high << 32u) | static_cast<uint32_t>(low)) & AddressMask;',
     'const auto  immediate = static_cast<int64_t>(static_cast<int32_t>(mem.offset));'),
    (C, SW, 1927, 'address = ((base & ~uint64_t {3}) + byte_offset) & ~uint64_t {3};', '} else {'),
    (C, 'CMakeLists.txt', 156, '-D SHADER_CACHE_EXTRA_FILES=', ''),
    ('5f63bbf3', 'docs/track-s/s17c/s17c_read.py', 684, "rows.r('capture reject lines (<= 20 logged)'", ''),
    ('5f63bbf3', 'docs/track-s/s17c/s17c_read.py', 695, "rows.m('K3 canon_mismatch = 0 (canon_self + canon_residual)'", 'cm, lc.get('),
]
ok = True
cache = {}
for commit, path, n, anchor, plus1 in REFS:
    key = (commit, path)
    if key not in cache:
        out = subprocess.run([G, '-C', R, 'show', '%s:%s' % key], capture_output=True).stdout
        cache[key] = out.decode('utf-8', 'replace').replace('\r', '').split('\n')
    lines = cache[key]
    a = lines[n - 1].strip() if n - 1 < len(lines) else ''
    b = lines[n].strip() if n < len(lines) else ''
    good = anchor in a and (plus1 in b) and anchor not in b
    ok &= good
    print('%s %s:%s:%d' % ('OK ' if good else 'BAD', commit, path, n))
    if not good:
        print('   line N  :', a[:160])
        print('   line N+1:', b[:160])
print('refs %d' % len(REFS))
print('ALL OK' if ok else 'FAIL')

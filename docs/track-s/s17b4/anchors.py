# S17b4 (Red Team, HPP-623): anchors of the review - <commit>:<path>:<line> holds the anchor, line+1 holds the control.
import subprocess
import sys

REPO = "C:/kyty/KytyPS5"
SR = "src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp"
SH = "src/graphics/host_gpu/renderer/pipeline/shaderReplay.h"
PC = "src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp"
TS = "tests/shaderCfgTests.cpp"
C = "9238a182"
REFS = [
    (C, SR, 643, "std::vector<uint8_t> kept_role(raw.size(), 0u); // S17a4: role of the classifier before ROLE_KEEP (kept_address)",
"for (size_t i = 0; i < raw.size(); i++) {"),
    (C, SR, 704, "kept_address[i] = role != ROLE_INERT ? 1u : 0u;", "kept_role[i]    = role;"),
    (C, SR, 788, "if (addr || (word.role == ROLE_KEEP && word.value >= 0x10000u && addresses.contains(word.value))) {",
     "if (culprits == 0) {"),
    (C, SR, 797, 'why = fmt::format("residual branch={} culprit={}:role{} n={}", culprit_addr ? "addr" : "exact", culprit,',
     "culprit_addr ? static_cast<uint32_t>(kept_role[culprit]) : 0u, culprits);"),
    (C, SR, 824, 'const bool residual = why.starts_with("residual");', 'if (why.starts_with("self")) {'),
    (C, SR, 834, "stats.canon_mismatch = stats.canon_self + stats.canon_residual;",
     "return residual ? stats.canon_residual <= 20u : stats.canon_self + stats.canon_base + stats.canon_big <= 20u;"),
    (C, SR, 835, "return residual ? stats.canon_residual <= 20u : stats.canon_self + stats.canon_base + stats.canon_big <= 20u;",
     "}"),
    (C, SR, 1187, "HandleSpec(*slot.spec);", "}"),
    (C, SR, 1234, "if (!Canonicalize(*item.plan, item.trace, item.live, words, user_words, why, TestStand() == Stand::Canon)) {",
     "// S17a4 (item 541(c)(2)-(3)): counted by the prefix of why (CountReject); residual reject lines have their own"),
    (C, SR, 1237, "if (CountReject(m_stats, why)) {",
     'LOGF("ShaderReplay: capture reject why=%s hash=0x%016" PRIx64 " words=%zu\\n", why.c_str(),'),
    (C, SR, 1343, 'LOGF("ShaderReplay: capture sources=%u specs=%u pipes=%u canon_mismatch=%u dropped_queue=%u bytes=%" PRIu64',
     '" gen=%" PRIu64 " canon_self=%u canon_residual=%u canon_base=%u canon_big=%u pipes_waiting=%u "'),
    (C, SR, 1372, "Capture::Capture(Store& store, Catalogue initial, uint64_t generation)",
     ": m_writer(std::make_unique<Writer>(store, std::move(initial), generation)) {}"),
    (C, SR, 39, "static const int mode = [] {", 'const char* value = std::getenv("KYTY_S_REPLAY");'),
    (C, SR, 49, "bool CaptureOn() {", "return Mode() == 1 || Mode() == 2;"),
    (C, SH, 350, "bool CountReject(CaptureStats& stats, const std::string& why);", ""),
    (C, PC, 7053, "if (mode == 0) {", "return;"),
    (C, PC, 7087, "m_replay_capture = std::make_unique<ShaderReplay::Capture>(*m_replay_store, std::move(initial),",
     "std::max(generation, corrupt));"),
    (C, TS, 15663, 'Check(!canonical && why.starts_with("residual branch=addr culprit=30:role2 ") && Common::ContainsStr(why, " n=") &&',
     "!Common::ContainsStr(why, raw_hex),"),
    (C, TS, 15725, 'const std::string expected = "residual branch=exact culprit=" + std::to_string(w_index) + ":role0 n=1";',
     "char raw_hex[16];"),
    (C, TS, 15800, "Check(stats.canon_residual == 26u && stats.canon_self == 1u && stats.canon_base == 1u && stats.canon_big == 1u &&",
     "stats.canon_mismatch == 27u,"),
    (C, TS, 15803, "Check(printed_residual == 20 && !exact_printed && self_printed && base_printed && big_printed,",
     '"replay count reject: the limits of 20 reject lines are not independent");'),
    # old code (9635cb0f) quoted by the review
    ("9635cb0f", SR, 1202, "if (!Canonicalize(*item.plan, item.trace, item.live, words, user_words, why, TestStand() == Stand::Canon)) {",
     'if (why.starts_with("self")) {'),
    ("9635cb0f", SR, 1205, '} else if (why == "residual") {', "m_stats.canon_residual++;"),
    ("9635cb0f", SR, 1213, "if (m_stats.canon_self + m_stats.canon_residual + m_stats.canon_base + m_stats.canon_big <= 20u) {",
     'LOGF("ShaderReplay: capture reject why=%s hash=0x%016" PRIx64 " words=%zu\\n", why.c_str(),'),
]

cache = {}
ok = True
for commit, path, line, anchor, control in REFS:
    key = (commit, path)
    if key not in cache:
        out = subprocess.run(["git", "-C", REPO, "show", f"{commit}:{path}"], capture_output=True)
        cache[key] = out.stdout.decode("utf-8").replace("\r", "").split("\n")
    lines = cache[key]
    a = lines[line - 1].strip() if line - 1 < len(lines) else ""
    b = lines[line].strip() if line < len(lines) else ""
    good = a == anchor.strip() and b == control.strip()
    ok &= good
    print(("OK  " if good else "BAD ") + f"{commit}:{path}:{line}")
    if not good:
        print("   got  :", a)
        print("   got+1:", b)
print(f"refs {len(REFS)}")
print("ALL OK" if ok else "FAIL")
sys.exit(0 if ok else 1)

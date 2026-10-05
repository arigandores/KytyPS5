# S17a4 (HPP-622, ROADMAP s122 item 541(c)): RC1 of the S17b3 review - branch, culprit and count in the residual reject
# line, the residual counter by prefix, an own limit of 20 residual reject lines. Anchors are whole lines; CRLF kept.
import sys

ROOT = 'C:/kyty/KytyPS5/'
CPP = ROOT + 'src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp'
H = ROOT + 'src/graphics/host_gpu/renderer/pipeline/shaderReplay.h'
NL = chr(10)


def load(path):
    data = open(path, 'rb').read().decode('utf-8')
    crlf = chr(13) + NL in data
    return data.replace(chr(13), ''), crlf


def save(path, text, crlf):
    if crlf:
        text = text.replace(NL, chr(13) + NL)
    open(path, 'wb').write(text.encode('utf-8'))


def replace_block(text, old_lines, new_lines, what):
    old = NL.join(old_lines) + NL
    new = NL.join(new_lines) + NL
    n = text.count(old)
    if n != 1:
        print('ANCHOR FAIL', what, n)
        sys.exit(1)
    # whole lines: the block starts at a line start
    i = text.find(old)
    if i != 0 and text[i - 1] != NL:
        print('ANCHOR NOT LINE START', what)
        sys.exit(1)
    return text.replace(old, new)


T = chr(9)
cpp, cpp_crlf = load(CPP)

# (1) kept_role next to kept_address
cpp = replace_block(cpp, [
    T + 'std::vector<uint8_t> kept_address(raw.size(), 0u);',
], [
    T + 'std::vector<uint8_t> kept_address(raw.size(), 0u);',
    T + 'std::vector<uint8_t> kept_role(raw.size(), 0u); // S17a4: role of the classifier before ROLE_KEEP (kept_address)',
], 'kept_address decl')

cpp = replace_block(cpp, [
    T * 3 + "kept_address[i] = role != ROLE_INERT ? 1u : 0u;",
    T * 3 + "role            = ROLE_KEEP;",
], [
    T * 3 + "kept_address[i] = role != ROLE_INERT ? 1u : 0u;",
    T * 3 + "kept_role[i]    = role;",
    T * 3 + "role            = ROLE_KEEP;",
], 'kept_address set')

# (2) residual: every culprit counted, the first named
cpp = replace_block(cpp, [
    T + "for (size_t i = 0; i < canonical.size(); i++) {",
    T + T + "const auto& word = canonical[i];",
    T + T + "if (kept_address[i] != 0u ||",
    T + T + "    (word.role == ROLE_KEEP && word.value >= 0x10000u && addresses.contains(word.value))) {",
    T + T + T + 'why = "residual";',
    T + T + T + "return false;",
    T + T + "}",
    T + "}",
], [
    T + "// S17a4 (item 541(c)(1)): the reject names the branch of the first culprit (addr - kept_address, also when its value",
    T + "// matches; exact - the exact-value comparison), its index, the role of the classifier before ROLE_KEEP (addr; 0 for",
    T + "// exact) and the number of culprits of both branches. The raw value is not printed (the lower word of a guest",
    T + "// address would reach the committed read files).",
    T + "size_t   culprit      = canonical.size();",
    T + "bool     culprit_addr = false;",
    T + "uint32_t culprits     = 0;",
    T + "for (size_t i = 0; i < canonical.size(); i++) {",
    T + T + "const auto& word = canonical[i];",
    T + T + "const bool  addr = kept_address[i] != 0u;",
    T + T + "if (addr || (word.role == ROLE_KEEP && word.value >= 0x10000u && addresses.contains(word.value))) {",
    T + T + T + "if (culprits == 0) {",
    T + T + T + T + "culprit      = i;",
    T + T + T + T + "culprit_addr = addr;",
    T + T + T + "}",
    T + T + T + "culprits++;",
    T + T + "}",
    T + "}",
    T + "if (culprits != 0) {",
    T + T + 'why = fmt::format("residual branch={} culprit={}:role{} n={}", culprit_addr ? "addr" : "exact", culprit,',
    T + T + "                  culprit_addr ? static_cast<uint32_t>(kept_role[culprit]) : 0u, culprits);",
    T + T + "return false;",
    T + "}",
], 'residual loop')

# (3) CountReject: free function after SamePcGroups
cpp = replace_block(cpp, [
    T + "return static_cast<uint32_t>(std::ranges::count_if(groups, [](const auto& g) { return g.second >= 2u; }));",
    "}",
    "",
    "// --- Catalogue and its files -----------------------------------------------------------------------------------------",
], [
    T + "return static_cast<uint32_t>(std::ranges::count_if(groups, [](const auto& g) { return g.second >= 2u; }));",
    "}",
    "",
    "bool CountReject(CaptureStats& stats, const std::string& why) {",
    T + "const bool residual = why.starts_with(\"residual\");",
    T + "if (why.starts_with(\"self\")) {",
    T + T + "stats.canon_self++;",
    T + "} else if (residual) {",
    T + T + "stats.canon_residual++;",
    T + "} else if (why == \"base\") {",
    T + T + "stats.canon_base++;",
    T + "} else {",
    T + T + "stats.canon_big++;",
    T + "}",
    T + "stats.canon_mismatch = stats.canon_self + stats.canon_residual;",
    T + "return residual ? stats.canon_residual <= 20u : stats.canon_self + stats.canon_base + stats.canon_big <= 20u;",
    "}",
    "",
    "// --- Catalogue and its files -----------------------------------------------------------------------------------------",
], 'CountReject')

cpp = replace_block(cpp, [
    T * 3 + 'if (why.starts_with("self")) {',
    T * 4 + "m_stats.canon_self++;",
    T * 3 + '} else if (why == "residual") {',
    T * 4 + "m_stats.canon_residual++;",
    T * 3 + '} else if (why == "base") {',
    T * 4 + "m_stats.canon_base++;",
    T * 3 + "} else {",
    T * 4 + "m_stats.canon_big++;",
    T * 3 + "}",
    T * 3 + "m_stats.canon_mismatch = m_stats.canon_self + m_stats.canon_residual;",
    T * 3 + "if (m_stats.canon_self + m_stats.canon_residual + m_stats.canon_base + m_stats.canon_big <= 20u) {",
], [
    T * 3 + "// S17a4 (item 541(c)(2)-(3)): counted by the prefix of why (CountReject); residual reject lines have their own",
    T * 3 + "// limit of 20.",
    T * 3 + "if (CountReject(m_stats, why)) {",
], 'HandleSpec count')

save(CPP, cpp, cpp_crlf)

h, h_crlf = load(H)
h = replace_block(h, [
    "// Canonicalization of one read path (writer thread; also used by the tests). Returns false when the path cannot be",
    "// recorded; `why` = \"base\", \"big\", \"self\" or \"residual\". On success `words` holds the canonical path. A word gets the",
    "// canonical value of its role only when the walk with that one word substituted is the same (S17a3, item 537(g)(2));",
    "// otherwise it is kept as read, and an address word kept as read rejects the record (\"residual\").",
], [
    "// Canonicalization of one read path (writer thread; also used by the tests). Returns false when the path cannot be",
    "// recorded; `why` = \"base\", \"big\", \"self ...\" or \"residual branch=<addr|exact> culprit=<i>:role<r> n=<k>\" (S17a4,",
    "// item 541(c)(1)). On success `words` holds the canonical path. A word gets the canonical value of its role only when",
    "// the walk with that one word substituted is the same (S17a3, item 537(g)(2)); otherwise it is kept as read, and an",
    "// address word kept as read rejects the record (\"residual\").",
], 'h Canonicalize comment')

h = replace_block(h, [
    "// Number of groups of two or more plan resources with one (kind, first_use_pc) (S16e section 5; K4 print).",
    "uint32_t SamePcGroups(const ShaderRecompiler::IR::ShaderInfo& info);",
], [
    "// Number of groups of two or more plan resources with one (kind, first_use_pc) (S16e section 5; K4 print).",
    "uint32_t SamePcGroups(const ShaderRecompiler::IR::ShaderInfo& info);",
    "",
    "// Counts one Canonicalize reject in `stats` by the prefix of `why` (S17a4, item 541(c)(2)-(3)): \"self\" - canon_self,",
    "// \"residual\" - canon_residual, \"base\" - canon_base, anything else - canon_big; canon_mismatch = canon_self +",
    "// canon_residual. Returns true when its reject line is printed: the first 20 residual rejects, and the first 20",
    "// rejects of the other kinds (each limit independent of the other).",
    "bool CountReject(CaptureStats& stats, const std::string& why);",
], 'h CountReject')
save(H, h, h_crlf)
print('PATCH OK')

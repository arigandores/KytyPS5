"""S17a3 (HPP-620, ROADMAP s122 item 537(g)(2)-(3)): the role classifier of S-replay checks the exact canonical
substitution of every word (src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp, .h). Anchors are whole lines;
LF in, LF out (CRLF kept if the file has it). Usage: python patch_s17a3.py <repository root>"""
import sys

root = sys.argv[1].rstrip('/\\')


def load(rel):
    data = open(root + '/' + rel, 'rb').read()
    crlf = b'\r\n' in data
    return data.decode('utf-8').replace('\r\n', '\n').split('\n'), crlf


def save(rel, lines, crlf):
    out = '\n'.join(lines)
    if crlf:
        out = out.replace('\n', '\r\n')
    open(root + '/' + rel, 'wb').write(out.encode('utf-8'))


def find(lines, anchor, start=0):
    hits = [i for i in range(start, len(lines)) if lines[i] == anchor]
    if len(hits) != 1:
        sys.exit('anchor %r: %d hits' % (anchor, len(hits)))
    return hits[0]


def replace_block(lines, block_old, block_new):
    first = find(lines, block_old[0])
    if lines[first:first + len(block_old)] != block_old:
        sys.exit('block at %r does not match' % block_old[0])
    lines[first:first + len(block_old)] = block_new
    return first


CPP = 'src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp'
lines, crlf = load(CPP)
if any('SubstitutionHolds' in l for l in lines):
    sys.exit('already applied')

# (1) SubstitutionHolds before the stand flag.
i = find(lines, 'std::atomic<bool> g_canon_stand_done {false};')
lines[i:i] = r'''// S17a3 (HPP-620, ROADMAP s122 item 537(g)(2)): the two perturbations of the role (bit 8, bit 0) do not test the
// substitution the canonical form makes - INERT 0x45f -> 0x10f flips bits 4, 6, 8, 10 (the canon_self rejects of the
// s17c_c2 tag). The canonical value of one word is taken only when the walk with this one word in that value (all other
// words raw) is the same: ok, complete, the live specialization and the same requests; an address word (PTR_*, V_*)
// may move requests, each by exactly the substitution in its half of the address (the walk adds offsets to the
// address it reads through; the canonical forms keep bits 0..3, so the masks of the walk do not change the move).
bool SubstitutionHolds(const IR::ResourcePlan& plan, const std::vector<Word>& raw, size_t user_words, size_t i,
                       Role role, uint32_t value, const RunResult& base, const IR::ResourceSpecialization& live) {
	auto path     = raw;
	path[i].value = value;
	const auto now = Run(plan, path, user_words, true);
	if (!now.ok || !now.complete || !(now.specialization == live) || now.requested.size() != base.requested.size()) {
		return false;
	}
	const uint64_t difference = static_cast<uint64_t>(value) - static_cast<uint64_t>(raw[i].value);
	uint64_t       shift      = 0;
	switch (role) {
		case ROLE_PTR_LO:
		case ROLE_V_LO: shift = difference; break;
		case ROLE_PTR_HI:
		case ROLE_V_HI: shift = difference << 32u; break;
		default: break;
	}
	for (size_t j = 0; j < base.requested.size(); j++) {
		if (now.requested[j] != base.requested[j] && (shift == 0 || now.requested[j] - base.requested[j] != shift)) {
			return false;
		}
	}
	return true;
}

'''.split('\n')[:-1]

# (2) The role loop: the vector of address words kept as read, and the check of the substitution.
replace_block(lines, [
    '\t// Role of every word: two perturbations (bit 8, bit 0), each replayed in full.',
    '\tstd::vector<Word> canonical = raw;',
], [
    '\t// Role of every word: two perturbations (bit 8, bit 0), each replayed in full; then the canonical substitution of the',
    '\t// word alone (S17a3, SubstitutionHolds) - a word it changes the walk of is kept as read.',
    '\tstd::vector<Word>    canonical = raw;',
    '\tstd::vector<uint8_t> kept_address(raw.size(), 0u);',
])
replace_block(lines, [
    '\t\tcanonical[i].role  = role;',
    '\t\tcanonical[i].value = Canonical(role, raw[i].value, descriptor);',
    '\t}',
], [
    '\t\tuint32_t value = Canonical(role, raw[i].value, descriptor);',
    '\t\tif (value != raw[i].value && !SubstitutionHolds(plan, raw, user_words, i, role, value, base, live)) {',
    '\t\t\t// Kept as read (ROLE_KEEP). A word the classifier took for an address (any role but INERT) may not reach the',
    '\t\t\t// catalogue as read: the record is rejected below (residual, item 537(g)(3)).',
    '\t\t\tkept_address[i] = role != ROLE_INERT ? 1u : 0u;',
    '\t\t\trole            = ROLE_KEEP;',
    '\t\t\tvalue           = raw[i].value;',
    '\t\t}',
    '\t\tcanonical[i].role  = role;',
    '\t\tcanonical[i].value = value;',
    '\t}',
])

# (3) The residual check also rejects an address word kept as read.
replace_block(lines, [
    '\t// No word kept as read may carry a guest address the walk used (lower 32 bits of a read address or of a non-null',
    '\t// descriptor base); small values are not compared.',
], [
    '\t// No word kept as read may carry a guest address the walk used (lower 32 bits of a read address or of a non-null',
    '\t// descriptor base); small values are not compared. S17a3: nor may an address word whose canonical substitution',
    '\t// failed (kept_address), whatever its value - the exact-value comparison does not see a pointer read at offsets.',
])
replace_block(lines, [
    '\tfor (const auto& word: canonical) {',
    '\t\tif (word.role == ROLE_KEEP && word.value >= 0x10000u && addresses.contains(word.value)) {',
], [
    '\tfor (size_t i = 0; i < canonical.size(); i++) {',
    '\t\tconst auto& word = canonical[i];',
    '\t\tif (kept_address[i] != 0u ||',
    '\t\t    (word.role == ROLE_KEEP && word.value >= 0x10000u && addresses.contains(word.value))) {',
])
save(CPP, lines, crlf)

H = 'src/graphics/host_gpu/renderer/pipeline/shaderReplay.h'
lines, crlf = load(H)
replace_block(lines, [
    '// Canonicalization of one read path (writer thread; also used by the tests). Returns false when the path cannot be',
    '// recorded; `why` = "base", "big", "self" or "residual". On success `words` holds the canonical path.',
], [
    '// Canonicalization of one read path (writer thread; also used by the tests). Returns false when the path cannot be',
    '// recorded; `why` = "base", "big", "self" or "residual". On success `words` holds the canonical path. A word gets the',
    '// canonical value of its role only when the walk with that one word substituted is the same (S17a3, item 537(g)(2));',
    '// otherwise it is kept as read, and an address word kept as read rejects the record ("residual").',
])
save(H, lines, crlf)
print('patched', CPP, H)

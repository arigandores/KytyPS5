P = 'C:/kyty/KytyPS5/src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp'
t = open(P, 'rb').read().decode('utf-8')
old = '''	const auto check = Run(plan, canonical, user_words, false);
	if (!check.ok || !check.complete || !(check.specialization == live)) {
		why = "self";
		return false;
	}
'''
new = '''	const auto check = Run(plan, canonical, user_words, false);
	if (!check.ok || !check.complete || !(check.specialization == live)) {
		// Diagnosis for the log (only on a failure): the words whose raw value alone makes the check pass.
		why = fmt::format("self ok={} complete={}", check.ok ? 1 : 0, check.complete ? 1 : 0);
		uint32_t named = 0;
		for (size_t i = 0; i < canonical.size() && named < 4; i++) {
			if (canonical[i].value == raw[i].value) {
				continue;
			}
			auto partial     = canonical;
			partial[i].value = raw[i].value;
			const auto again = Run(plan, partial, user_words, false);
			if (again.ok && again.complete && again.specialization == live) {
				why += fmt::format(" culprit={}:role{}:{:08x}->{:08x}", i, canonical[i].role, raw[i].value,
				                   canonical[i].value);
				named++;
			}
		}
		return false;
	}
'''
assert t.count(old) == 1
t = t.replace(old, new)
old2 = '''			if (why == "self") {'''
new2 = '''			if (why.starts_with("self")) {'''
assert t.count(old2) == 1
t = t.replace(old2, new2)
open(P, 'wb').write(t.encode('utf-8'))

T = 'C:/kyty/KytyPS5/tests/shaderCfgTests.cpp'
u = open(T, 'rb').read().decode('utf-8')
old3 = '''  Check(canonical, "replay canonicalization failed");
'''
new3 = '''  Check(canonical, "replay canonicalization failed");
  if (!canonical) {
    return {};
  }
'''
assert u.count(old3) == 1
u = u.replace(old3, new3)
old4 = '''    const auto words = ReplayRoundTrip(plan, live, user_words, "inline descriptors");
'''
new4 = '''    const auto words = ReplayRoundTrip(plan, live, user_words, "inline descriptors");
    Check(words.size() == 2u + user_words, "replay inline path has a read");
'''
assert u.count(old4) == 1
u = u.replace(old4, new4)
old5 = '''    const auto words = ReplayRoundTrip(plan, live, user_words, "pointer to a V# table");
'''
new5 = '''    const auto words = ReplayRoundTrip(plan, live, user_words, "pointer to a V# table");
    Check(words.size() > 2u + 29u, "replay pointer path too short");
    if (words.size() <= 2u + 29u) {
      return;
    }
'''
assert u.count(old5) == 1
u = u.replace(old5, new5)
# the inline check loop indexes words[2 + i]: guard it
old6 = '''    for (size_t i = 0; i < user_words; i++) {
      const auto &w = words[2 + i];'''
new6 = '''    for (size_t i = 0; i < user_words && 2 + i < words.size(); i++) {
      const auto &w = words[2 + i];'''
assert u.count(old6) == 1
u = u.replace(old6, new6)
open(T, 'wb').write(u.encode('utf-8'))
print('diag patched OK')

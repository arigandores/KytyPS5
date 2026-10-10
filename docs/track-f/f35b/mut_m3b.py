# F35b (HPP-756): extra mutant m3b, declared AFTER the data of b27a70ba (not in the list): the materialization drops
# the last candidate only of tables with more than two members - to see the test's own Check (not the materialization
# fatal of m3). Apply to the clean worktree; then build, `python mut_f35b.py run m3b`, `python mut_f35b.py revert`.
p = 'C:/kyty/f287/f35b/wt/src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp'
d = open(p, 'rb').read()
L = d.split(b'\n')
old = b'\t\tfor (uint32_t candidate = 1; candidate < table.descriptors.size(); candidate++) {'
new = (b'\t\tfor (uint32_t candidate = 1; candidate + (table.descriptors.size() > 2 ? 1u : 0u) < '
       b'table.descriptors.size(); candidate++) {')
h = [i for i, l in enumerate(L) if l == old]
assert len(h) == 1, h
L[h[0]] = new
open(p, 'wb').write(b'\n'.join(L))
print('applied m3b line', h[0] + 1)

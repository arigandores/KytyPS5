"""M6a3: (1) driver run_stand_m6a3.py - expectations of case ao_obj_span (pure 132, ao_obj_push 10, ao_obj_unread 4);
(2) mut_m6a3.py from m6a2/mut_m6a2.py - the M6a3 mutant list, the M6a3 driver, outputs in m6a3/mut3 and docs m6a3."""
NL = chr(10)
DRV = 'C:/kyty/KytyPS5/docs/track-m/m6a3/run_stand_m6a3.py'
t = open(DRV, 'rb').read().decode('utf-8')
subs = [
    ("pure 128 of 128 (new cases ao_obj_vq_nz, ao_obj_vq_zero - private commit; ao_obj_noaccess, ao_obj_guard;",
     "pure 132 of 132 (new cases ao_obj_vq_nz, ao_obj_vq_zero - private commit; ao_obj_noaccess, ao_obj_guard, ao_obj_span;"),
    ("e['total'] == '128' and e['match'] == '128'", "e['total'] == '132' and e['match'] == '132'"),
    ("(want 128 of 128)", "(want 132 of 132)"),
    ("ao_obj_push='9', ao_obj_nz='3'", "ao_obj_push='10', ao_obj_nz='3'"),
    ("ao_obj_unread='3', inv_part_src='2', ao_obj_vq='2')", "ao_obj_unread='4', inv_part_src='2', ao_obj_vq='2')"),
]
for old, new in subs:
    assert t.count(old) == 1, old
    t = t.replace(old, new, 1)
open(DRV, 'wb').write(t.encode('utf-8'))

SRC = 'C:/kyty/KytyPS5/docs/track-m/m6a2/mut_m6a2.py'
DST = 'C:/kyty/KytyPS5/docs/track-m/m6a3/mut_m6a3.py'
m = open(SRC, 'rb').read().decode('utf-8')
i = m.index('# name, file, old, new' + NL)
j = m.index(']' + NL + NL + NL + 'def guard():')
head = m[:i]
tail = m[j + 2:]
head = head.replace(
    '"""Track M, M6a2 (HPP-854, ROADMAP s122 item 770(b)-(e)): mutants of the M6a2 edits of KYTY_DIAG_M5W2 against the stand' + NL +
    '(run_stand_m6a2.py). Copy of m6a/mut_m6a.py (same method):',
    '"""Track M, M6a3 (HPP-856, ROADMAP s122 item 772(v), (g)): mutants of the M6a3 edits of KYTY_DIAG_M5W2 against the stand' + NL +
    '(run_stand_m6a3.py). Copy of m6a2/mut_m6a2.py (same method; the M6a2 mutants re-run on the new code, anchors of the' + NL +
    'object branch moved to its M6a3 form). Kind MEMBER - must be CAUGHT (named by item 772(v), (g) or by M6a3 before the' + NL +
    'run); kind PROBE - outcome printed, not a member. Was: Track M, M6a2 (HPP-854): mutants of the M6a2 edits; copy of' + NL +
    'm6a/mut_m6a.py (same method):')
assert 'Track M, M6a3' in head
head = head.replace("OUT = 'C:/kyty/KytyPS5/docs/track-m/m6a2'", "OUT = 'C:/kyty/KytyPS5/docs/track-m/m6a3'")
head = head.replace('Usage: python mut_m6a2.py [--only <name>]   Output: mut_m6a2.out.txt',
                    'Usage: python mut_m6a3.py [--only <name>]   Output: mut_m6a3.out.txt')
assert "track-m/m6a3'" in head and 'mut_m6a3.out.txt' in head
tail = tail.replace("HERE + '/mut2'", "'C:/kyty/m657/m6a3/mut3'").replace("'%s/mut2/build_%s.log' % (HERE, tag)",
                                                                       "'C:/kyty/m657/m6a3/mut3/build_%s.log' % tag")
tail = tail.replace("'%s/mut2/stand_%s' % (HERE, tag)", "'C:/kyty/m657/m6a3/mut3/stand_%s' % tag")
tail = tail.replace("OUT + '/run_stand_m6a2.py'", "OUT + '/run_stand_m6a3.py'")
tail = tail.replace("OUT + '/mut_m6a2.out.txt'", "OUT + '/mut_m6a3.out.txt'")
for s in ('mut2', 'm6a2'):
    assert s not in tail, s
mutants = r'''# kind, name, file, old, new
OBJ_TRY = 'if (!Libs::LibKernel::Memory::TryReadBacking(reinterpret_cast<uint64_t>(pcm), copy.data(), bytes)) {'
OS_IF = 'if (!OsReadable(reinterpret_cast<uint64_t>(pcm), bytes)) {'
R8 = 'case vk::Format::eR8Unorm: return word != (word & 0xffu) * 0x01010101u;'
MUTANTS = [
    # M6a3 item 772(v): the fallback removed (private commit -> ao_obj_unread 1, ao_obj_vq 0); the OS check removed
    # (raw read of 0x1000 - death); ao_obj_vq does not grow.
    ('MEMBER', 'fallback_off', D, OS_IF, 'if (true) {'),
    ('MEMBER', 'os_check_off', D, OS_IF, 'if (false) {'),
    ('MEMBER', 'c_ao_obj_vq', D, T + T + T + 'Bump(g_ao_obj_vq);' + NL, ''),
    # M6a3 item 772(g) (P2 of M6b2): the R8 rule on the low 16 bits only (case 0x34121212).
    ('MEMBER', 'r8_low16', D, R8, 'case vk::Format::eR8Unorm: return (word & 0xffffu) != (word & 0xffu) * 0x0101u;'),
    # M6a3 own members (named before the run): the protection test removed (PAGE_NOACCESS page read - death); PAGE_GUARD
    # not excluded (guard page read); only the first region checked (grain over a reserved page read); the fallback
    # unread counter lost.
    ('MEMBER', 'prot_unchecked', D, 'if ((prot & (PAGE_GUARD | PAGE_NOACCESS)) != 0) {', 'if (false) {'),
    ('MEMBER', 'guard_ignored', D, 'if ((prot & (PAGE_GUARD | PAGE_NOACCESS)) != 0) {', 'if ((prot & PAGE_NOACCESS) != 0) {'),
    ('MEMBER', 'first_region_only', D, T + T + 'p = region_end;' + NL, T + T + 'p = end;' + NL),
    ('MEMBER', 'c_ao_obj_unread_fb', D, T + T + T + T + 'Bump(g_ao_obj_unread);' + NL, ''),
    # M6a3 probes: the State test removed (the protection switch refuses MEM_FREE / MEM_RESERVE too - expected
    # equivalent on the stand); the fallback read before the check.
    ('PROBE', 'state_unchecked', D, ' || mbi.State != MEM_COMMIT) {', ') {'),
    # M6a2 mutants re-run on the M6a3 code.
    ('MEMBER', 'x_eq_div', D, T + 'const uint64_t level = std::max<uint64_t>(base_level, level_count - 1u);',
     T + 'const uint64_t level = level_count - 1u;'),
    ('MEMBER', 'c_minlod_div_x', D, T + T + 'Bump(g_minlod_div_x);' + NL, ''),
    ('MEMBER', 'c_clr_dw_div8', D, T + T + 'Bump(g_clr_dw_div8);' + NL, ''),
    ('MEMBER', 'c_clr_fmt_div8', D, T + T + 'Bump(g_clr_fmt_div8[row]);' + NL, ''),
    ('MEMBER', 'r8_never', D, R8, 'case vk::Format::eR8Unorm: return false;'),
    ('MEMBER', 'r8_always', D, R8, 'case vk::Format::eR8Unorm: return true;'),
    ('MEMBER', 'rg8_never', D, 'case vk::Format::eR8G8Unorm: return (word & 0xffffu) != (word >> 16u);',
     'case vk::Format::eR8G8Unorm: return false;'),
    ('MEMBER', 'rg8_always', D, 'case vk::Format::eR8G8Unorm: return (word & 0xffffu) != (word >> 16u);',
     'case vk::Format::eR8G8Unorm: return true;'),
    ('MEMBER', 'obj_raw_read', D, OBJ_TRY, 'if ((std::memcpy(copy.data(), pcm, static_cast<size_t>(bytes)), false)) {'),
    ('MEMBER', 'c_ao_obj_push', D, T + T + 'Bump(g_ao_obj_push);' + NL, ''),
    ('MEMBER', 'c_ao_obj_nz', D, T + T + T + 'Bump(g_ao_obj_nz);' + NL, ''),
    ('MEMBER', 'c_ao_bus_push', D, T + 'Bump(g_ao_bus_push);' + NL, ''),
    ('MEMBER', 'c_ao_bus_nz', D, T + T + 'Bump(g_ao_bus_nz);' + NL, ''),
    ('MEMBER', 'c_inv_part_src', D, T + T + 'Bump(g_inv_part_src);' + NL, ''),
    ('MEMBER', 'src_eq_data', D, 'if (!(address <= image_address && address + size >= image_address + source_size)) {',
     'if (!(address <= image_address && address + size >= image_address + image_size)) {'),
]


'''
# the loop: unpack the kind; a PROBE prints its outcome, only a MEMBER counts for ok
tail = tail.replace('    for name, rel, old, new in MUTANTS:', '    for kind, name, rel, old, new in MUTANTS:')
assert 'for kind, name, rel, old, new in MUTANTS:' in tail
old = ("            ok &= caught" + NL +
       "            lines.append('%s %s (%d failed members; first: %s)' % ('CAUGHT' if caught else 'SURVIVED', name, len(failed),")
new = ("            ok &= caught or kind == 'PROBE'" + NL +
       "            lines.append('%s %s %s (%d failed members; first: %s)' % (kind, 'CAUGHT' if caught else 'SURVIVED', name, len(failed),")
assert tail.count(old) == 1
tail = tail.replace(old, new, 1)
open(DST, 'wb').write((head + mutants + tail).encode('utf-8'))
print('ALL OK')

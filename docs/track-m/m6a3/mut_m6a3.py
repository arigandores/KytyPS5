"""Track M, M6a3 (HPP-856, ROADMAP s122 item 772(v), (g)): mutants of the M6a3 edits of KYTY_DIAG_M5W2 against the stand
(run_stand_m6a3.py). Copy of m6a2/mut_m6a2.py (same method; the M6a2 mutants re-run on the new code, anchors of the
object branch moved to its M6a3 form). Kind MEMBER - must be CAUGHT (named by item 772(v), (g) or by M6a3 before the
run); kind PROBE - outcome printed, not a member. Was: Track M, M6a2 (HPP-854): mutants of the M6a2 edits; copy of
m6a/mut_m6a.py (same method): one exact text substitution (must match once) in the worktree
C:/kyty/m657/m6a/wt; the stand target is rebuilt (build_m6a.cmd target m_wave2_diag_stand, IDLE priority, --parallel 2),
the driver runs, the file is restored byte for byte. CAUGHT when the driver prints FAIL (a dead arm counts: the driver
fails on a missing END line). At the end the stand is rebuilt from the restored tree and must print ALL OK (control).
Usage: python mut_m6a3.py [--only <name>[,<name>...] [<part>]]   Output: mut_m6a3.out.txt beside this script; last line ALL OK or FAIL.
Lock and STOP checked before every step."""
import hashlib
import os
import subprocess
import sys

HERE = 'C:/kyty/m657/m6a'
OUT = 'C:/kyty/KytyPS5/docs/track-m/m6a3'
WT = HERE + '/wt'
EXE = HERE + '/build/m_wave2_diag_stand.exe'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
D = 'src/libs/diagM5W2.cpp'
T = chr(9)
NL = chr(10)

# kind, name, file, old, new
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




def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        sys.exit(3)


def build(tag):
    guard()
    log = 'C:/kyty/m657/m6a3/mut3/build_%s.log' % tag
    with open(log, 'wb') as f:
        rc = subprocess.call(['python', HERE + '/lowrun.py', 'cmd', '/c',
                              'C:' + chr(92) + 'kyty' + chr(92) + 'm657' + chr(92) + 'm6a' + chr(92) +
                              'build_m6a.cmd target m_wave2_diag_stand'], stdout=f, stderr=subprocess.STDOUT)
    text = open(log, 'rb').read().decode('utf-8', 'replace')
    return rc == 0 and 'BUILD OK' in text


def stand(tag):
    guard()
    out = 'C:/kyty/m657/m6a3/mut3/stand_%s' % tag
    p = subprocess.run(['python', OUT + '/run_stand_m6a3.py', EXE, out], stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
    text = p.stdout.decode('utf-8', 'replace')
    open(out + '.out.txt', 'w', encoding='utf-8', newline='\n').write(text)
    last = text.strip().splitlines()[-1] if text.strip() else ''
    return last, [l for l in text.splitlines() if l.startswith('FAILED ')]


def main():
    only = set(sys.argv[2].split(',')) if len(sys.argv) > 2 and sys.argv[1] == '--only' else None
    part = sys.argv[3] if len(sys.argv) > 3 else ''  # M6a3: batches (one tool call <= 600 s), output per batch
    os.makedirs('C:/kyty/m657/m6a3/mut3', exist_ok=True)
    lines = []
    ok = True
    for kind, name, rel, old, new in MUTANTS:
        if only and name not in only:
            continue
        path = os.path.join(WT, rel)
        orig = open(path, 'rb').read()
        sha0 = hashlib.sha256(orig).hexdigest()
        text = orig.decode('utf-8')
        n = text.count(old)
        if n != 1:
            lines.append('BADANCHOR %s x%d' % (name, n))
            ok = False
            print(lines[-1])
            continue
        try:
            open(path, 'wb').write(text.replace(old, new, 1).encode('utf-8'))
            built = build(name)
            if not built:
                lines.append('NOBUILD %s' % name)
                ok = False
                continue
            last, failed = stand(name)
            caught = last == 'FAIL'
            ok &= caught or kind == 'PROBE'
            lines.append('%s %s %s (%d failed members; first: %s)' % (kind, 'CAUGHT' if caught else 'SURVIVED', name, len(failed),
                                                                   failed[0][7:110] if failed else '-'))
        finally:
            open(path, 'wb').write(orig)
            if hashlib.sha256(open(path, 'rb').read()).hexdigest() != sha0:
                lines.append('RESTORE FAILED %s' % name)
                ok = False
        print(lines[-1])
        sys.stdout.flush()
    built = build('control')
    last, failed = stand('control') if built else ('NOBUILD', [])
    lines.append('CONTROL restored tree: build=%d driver=%s' % (1 if built else 0, last))
    ok &= built and last == 'ALL OK'
    lines.append('ALL OK' if ok else 'FAIL')
    print(NL.join(lines[-2:]))
    open(OUT + '/mut_m6a3%s.out.txt' % part, 'w', encoding='utf-8', newline='\n').write(NL.join(lines) + NL)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

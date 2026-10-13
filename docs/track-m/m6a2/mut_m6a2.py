"""Track M, M6a2 (HPP-854, ROADMAP s122 item 770(b)-(e)): mutants of the M6a2 edits of KYTY_DIAG_M5W2 against the stand
(run_stand_m6a2.py). Copy of m6a/mut_m6a.py (same method): one exact text substitution (must match once) in the worktree
C:/kyty/m657/m6a/wt; the stand target is rebuilt (build_m6a.cmd target m_wave2_diag_stand, IDLE priority, --parallel 2),
the driver runs, the file is restored byte for byte. CAUGHT when the driver prints FAIL (a dead arm counts: the driver
fails on a missing END line). At the end the stand is rebuilt from the restored tree and must print ALL OK (control).
Usage: python mut_m6a2.py [--only <name>]   Output: mut_m6a2.out.txt beside this script; last line ALL OK or FAIL.
Lock and STOP checked before every step."""
import hashlib
import os
import subprocess
import sys

HERE = 'C:/kyty/m657/m6a'
OUT = 'C:/kyty/KytyPS5/docs/track-m/m6a2'
WT = HERE + '/wt'
EXE = HERE + '/build/m_wave2_diag_stand.exe'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
D = 'src/libs/diagM5W2.cpp'
T = chr(9)
NL = chr(10)

# name, file, old, new
MUTANTS = [
    # RC1 (item 770(b)): minlod_div_x = the condition of minlod_div; the counter does not grow.
    ('x_eq_div', D, T + 'const uint64_t level = std::max<uint64_t>(base_level, level_count - 1u);',
     T + 'const uint64_t level = level_count - 1u;'),
    ('c_minlod_div_x', D, T + T + 'Bump(g_minlod_div_x);' + NL, ''),
    # RC2 (item 770(v)): clr_dw_div8 does not grow (total, per format), each format rule dead or always on.
    ('c_clr_dw_div8', D, T + T + 'Bump(g_clr_dw_div8);' + NL, ''),
    ('c_clr_fmt_div8', D, T + T + 'Bump(g_clr_fmt_div8[row]);' + NL, ''),
    ('r8_never', D, 'case vk::Format::eR8Unorm: return word != (word & 0xffu) * 0x01010101u;',
     'case vk::Format::eR8Unorm: return false;'),
    ('r8_always', D, 'case vk::Format::eR8Unorm: return word != (word & 0xffu) * 0x01010101u;',
     'case vk::Format::eR8Unorm: return true;'),
    ('rg8_never', D, 'case vk::Format::eR8G8Unorm: return (word & 0xffffu) != (word >> 16u);',
     'case vk::Format::eR8G8Unorm: return false;'),
    ('rg8_always', D, 'case vk::Format::eR8G8Unorm: return (word & 0xffffu) != (word >> 16u);',
     'case vk::Format::eR8G8Unorm: return true;'),
    # Member 769(g)(2) (item 770(g)): ao_obj_unread does not grow; the object grain read raw instead of the copy.
    ('c_ao_obj_unread', D,
     T + T + 'if (!Libs::LibKernel::Memory::TryReadBacking(reinterpret_cast<uint64_t>(pcm), copy.data(), bytes)) {' + NL +
     T + T + T + 'Bump(g_ao_obj_unread);' + NL,
     T + T + 'if (!Libs::LibKernel::Memory::TryReadBacking(reinterpret_cast<uint64_t>(pcm), copy.data(), bytes)) {' + NL),
    ('obj_raw_read', D,
     'if (!Libs::LibKernel::Memory::TryReadBacking(reinterpret_cast<uint64_t>(pcm), copy.data(), bytes)) {',
     'if ((std::memcpy(copy.data(), pcm, static_cast<size_t>(bytes)), false)) {'),
    # The rewritten object / bus counters of NoteAudioPort (re-check of the M6a mutants on the new form).
    ('c_ao_obj_push', D, T + T + 'Bump(g_ao_obj_push);' + NL, ''),
    ('c_ao_obj_nz', D, T + T + T + 'Bump(g_ao_obj_nz);' + NL, ''),
    ('c_ao_bus_push', D, T + 'Bump(g_ao_bus_push);' + NL, ''),
    ('c_ao_bus_nz', D, T + T + 'Bump(g_ao_bus_nz);' + NL, ''),
    # P1 (item 770(d)): inv_part_src does not grow; inv_part_src measured on info.data (= inv_part).
    ('c_inv_part_src', D, T + T + 'Bump(g_inv_part_src);' + NL, ''),
    ('src_eq_data', D, 'if (!(address <= image_address && address + size >= image_address + source_size)) {',
     'if (!(address <= image_address && address + size >= image_address + image_size)) {'),
]


def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        sys.exit(3)


def build(tag):
    guard()
    log = '%s/mut2/build_%s.log' % (HERE, tag)
    with open(log, 'wb') as f:
        rc = subprocess.call(['python', HERE + '/lowrun.py', 'cmd', '/c',
                              'C:' + chr(92) + 'kyty' + chr(92) + 'm657' + chr(92) + 'm6a' + chr(92) +
                              'build_m6a.cmd target m_wave2_diag_stand'], stdout=f, stderr=subprocess.STDOUT)
    text = open(log, 'rb').read().decode('utf-8', 'replace')
    return rc == 0 and 'BUILD OK' in text


def stand(tag):
    guard()
    out = '%s/mut2/stand_%s' % (HERE, tag)
    p = subprocess.run(['python', OUT + '/run_stand_m6a2.py', EXE, out], stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
    text = p.stdout.decode('utf-8', 'replace')
    open(out + '.out.txt', 'w', encoding='utf-8', newline='\n').write(text)
    last = text.strip().splitlines()[-1] if text.strip() else ''
    return last, [l for l in text.splitlines() if l.startswith('FAILED ')]


def main():
    only = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == '--only' else None
    os.makedirs(HERE + '/mut2', exist_ok=True)
    lines = []
    ok = True
    for name, rel, old, new in MUTANTS:
        if only and name != only:
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
            ok &= caught
            lines.append('%s %s (%d failed members; first: %s)' % ('CAUGHT' if caught else 'SURVIVED', name, len(failed),
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
    open(OUT + '/mut_m6a2.out.txt', 'w', encoding='utf-8', newline='\n').write(NL.join(lines) + NL)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

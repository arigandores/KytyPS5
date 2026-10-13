"""Track M, M6a (HPP-848, ROADMAP s122 item 767(i)): mutants of KYTY_DIAG_M5W2 and of the signature lines against the
stand (run_stand_m6a.py). Each mutant is one exact text substitution (must match once) in the worktree
C:/kyty/m657/m6a/wt; the stand target is rebuilt (build_m6a.cmd target m_wave2_diag_stand, IDLE priority), the driver runs,
the file is restored byte for byte. A mutant is CAUGHT when the driver prints FAIL. At the end the stand is rebuilt from
the restored tree and the driver must print ALL OK again (the restoration control).
Usage: python mut_m6a.py [--only <name>]   Output: mut_m6a.out.txt beside; last line ALL OK (every mutant caught and the
control passes) or FAIL. Lock and STOP checked before every step."""
import hashlib
import os
import subprocess
import sys

HERE = 'C:/kyty/m657/m6a'
WT = HERE + '/wt'
EXE = HERE + '/build/m_wave2_diag_stand.exe'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
D = 'src/libs/diagM5W2.cpp'
T = chr(9)
NL = chr(10)

# name, file, old, new
MUTANTS = [
    ('c_ao_obj_push', D, T + T + 'Bump(g_ao_obj_push);' + NL, ''),
    ('c_ao_obj_nz', D, T + T + T + 'Bump(g_ao_obj_nz);' + NL, ''),
    ('c_ao_obj_nopcm', D, T + 'Bump(g_ao_obj_nopcm);' + NL, ''),
    ('c_ao_bus_push', D, T + T + 'Bump(g_ao_bus_push);' + NL, ''),
    ('c_ao_bus_nz', D, T + T + T + 'Bump(g_ao_bus_nz);' + NL, ''),
    ('c_pushes', D, 'if ((g_pushes.fetch_add(1, std::memory_order_relaxed) + 1) % PERIODIC_PUSHES == 0) {',
     'if ((Load(g_pushes) + 1) % PERIODIC_PUSHES == 0) {'),
    ('c_clr_dw', D, T + 'Bump(g_clr_dw);' + NL, ''),
    ('c_clr_dw_div', D, T + T + 'Bump(g_clr_dw_div);' + NL, ''),
    ('c_clr_fmt', D, T + 'Bump(g_clr_fmt[row]);' + NL, ''),
    ('c_minlod_views', D, T + 'Bump(g_minlod_views);' + NL, ''),
    ('c_minlod_div', D, T + T + 'Bump(g_minlod_div);' + NL, ''),
    ('c_inv_calls', D, T + 'Bump(g_inv_calls);' + NL, ''),
    ('c_inv_gpu', D, T + 'Bump(g_inv_gpu);' + NL, ''),
    ('c_inv_part', D, T + T + 'Bump(g_inv_part);' + NL, ''),
    ('c_inv_off', D, T + T + T + 'Bump(g_inv_off);' + NL, ''),
    ('c_raw_rd', D, T + 'Bump(g_raw_rd);' + NL, ''),
    ('c_raw_rd_gpu', D, T + T + 'Bump(g_raw_rd_gpu);' + NL, ''),
    ('site_audio_port', 'src/libs/libAudio2.cpp',
     T * 4 + 'DiagM5W2::NoteAudioPort(object_port, state.pcm_data, state.data_format, state.samples_num);' + NL, ''),
    ('site_audio_push', 'src/libs/libAudio2.cpp',
     T + T + 'DiagM5W2::NoteAudioPush(); // M6a: the periodic "M5W2Stat:" line every 4096 queued pushes' + NL, ''),
    ('gate_audio', 'src/libs/libAudio2.cpp',
     T + 'if (DiagM5W2::On()) [[unlikely]] {' + NL + T + T + 'for (const auto& state: g_audioout2_ports) {',
     T + 'if (true) {' + NL + T + T + 'for (const auto& state: g_audioout2_ports) {'),
    ('sig_t031', 'src/libs/guestPrintf.cpp', T * 6 + 'LOGF("GuestPrintf: negative precision prec=%d' + chr(92) + 'n", prec);' + NL,
     ''),
    ('sig_t309_ensure', 'src/libs/libAmpr.cpp', T + T + 'LogRecordSpaceRefused(why, command_buffer, state, record_size);' + NL, ''),
    ('sig_t309_wa', 'src/libs/libAmpr.cpp',
     T + T + 'LogWriteAddressRefused("ensure", command_buffer, record_size, address, value); // M6a, T309' + NL, ''),
    ('lim_t309', 'src/libs/libAmpr.cpp',
     T + 'const uint32_t n = logged.fetch_add(1, std::memory_order_relaxed) + 1;' + NL + T + 'if (n > 20) {' + NL + T + T +
     'return;' + NL + T + '}' + NL + T + 'LOGF("AmprRecordSpace',
     T + 'const uint32_t n = logged.fetch_add(1, std::memory_order_relaxed) + 1;' + NL + T + 'if (n > 30) {' + NL + T + T +
     'return;' + NL + T + '}' + NL + T + 'LOGF("AmprRecordSpace'),
    ('sig_t023', 'src/libs/agc.cpp', T * 3 + 'if (n <= 20) {' + NL + T * 4 + 'const char* cls',
     T * 3 + 'if (n <= 0) {' + NL + T * 4 + 'const char* cls'),
    ('cls_t023', 'src/libs/agc.cpp', ': (cursor_down == nullptr ? "down0" : "down_lt_up");', ': "down_lt_up";'),
]


def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        sys.exit(3)


def build(tag):
    guard()
    log = '%s/mut/build_%s.log' % (HERE, tag)
    with open(log, 'wb') as f:
        rc = subprocess.call(['python', HERE + '/lowrun.py', 'cmd', '/c',
                              'C:' + chr(92) + 'kyty' + chr(92) + 'm657' + chr(92) + 'm6a' + chr(92) +
                              'build_m6a.cmd target m_wave2_diag_stand'], stdout=f, stderr=subprocess.STDOUT)
    text = open(log, 'rb').read().decode('utf-8', 'replace')
    return rc == 0 and 'BUILD OK' in text


def stand(tag):
    guard()
    out = '%s/mut/stand_%s' % (HERE, tag)
    p = subprocess.run(['python', HERE + '/run_stand_m6a.py', EXE, out], stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
    text = p.stdout.decode('utf-8', 'replace')
    open(out + '.out.txt', 'w', encoding='utf-8', newline='\n').write(text)
    last = text.strip().splitlines()[-1] if text.strip() else ''
    return last, [l for l in text.splitlines() if l.startswith('FAILED ')]


def main():
    only = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == '--only' else None
    os.makedirs(HERE + '/mut', exist_ok=True)
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
    open(HERE + '/mut_m6a.out.txt', 'w', encoding='utf-8', newline='\n').write(NL.join(lines) + NL)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

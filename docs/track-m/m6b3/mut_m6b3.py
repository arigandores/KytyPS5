"""Red Team M6b3 (HPP-857): own mutants of the M6a3 edits against the stand (driver ../m6a3/run_stand_m6a3.py).
Method of m6b2/mut_m6b2.py: one exact text substitution (must match once) in C:/kyty/m657/m6a/wt, stand target rebuilt
(build_m6a.cmd target m_wave2_diag_stand, IDLE, --parallel 2), driver run, file restored byte for byte (sha256 checked);
control rebuild of the restored tree must print ALL OK. Two groups:
  NAMED  - the mutants item 772(v), (g) requires the stand to catch (re-run by the reviewer): fallback_off,
           os_check_off, c_ao_obj_vq, r8_low16. Each must be CAUGHT.
  PROBE  - extra mutants NOT named by item 772 (stand strength, report only; expected outcome in the comment):
           vq_on_unread (ao_obj_vq also bumped on the refused path - expect CAUGHT by the ao_obj_vq 0 members),
           nz_skip_fb (no nonzero scan after the fallback read - expect CAUGHT by ao_obj_vq_nz),
           copy_half (the fallback copies half of the grain - expect CAUGHT by ao_obj_vq_nz, sample 3 of 4),
           check_one_byte (the OS check asks 1 byte instead of the grain - expect CAUGHT by ao_obj_span).
Usage: python mut_m6b3.py   Output: mut_m6b3.out.txt beside this script; last line ALL OK (named caught + control) or FAIL.
"""
import hashlib
import os
import subprocess
import sys

HERE = 'C:/kyty/m657/m6a'
OUT = 'C:/kyty/KytyPS5/docs/track-m/m6b3'
DRV = 'C:/kyty/KytyPS5/docs/track-m/m6a3/run_stand_m6a3.py'
WT = HERE + '/wt'
EXE = HERE + '/build/m_wave2_diag_stand.exe'
WORK = 'C:/kyty/m657/m6a3/mut_m6b3'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
D = 'src/libs/diagM5W2.cpp'
T = chr(9)
NL = chr(10)
OSR = T * 3 + 'if (!OsReadable(reinterpret_cast<uint64_t>(pcm), bytes)) {' + NL
VQ = T * 3 + 'Bump(g_ao_obj_vq);' + NL
UNR_FB = T * 4 + 'Bump(g_ao_obj_unread);' + NL + T * 4 + 'return;' + NL
CPY = T * 3 + 'std::memcpy(copy.data(), pcm, static_cast<size_t>(bytes));' + NL
R8 = 'case vk::Format::eR8Unorm: return word != (word & 0xffu) * 0x01010101u;'

MUTANTS = [
    ('NAMED', 'fallback_off', OSR, T * 3 + 'if (true) {' + NL),
    ('NAMED', 'os_check_off', OSR, T * 3 + 'if (false) {' + NL),
    ('NAMED', 'c_ao_obj_vq', VQ, ''),
    ('NAMED', 'r8_low16', R8, 'case vk::Format::eR8Unorm: return (word & 0xffffu) != (word & 0xffu) * 0x0101u;'),
    ('PROBE', 'vq_on_unread', UNR_FB, T * 4 + 'Bump(g_ao_obj_unread);' + NL + T * 4 + 'Bump(g_ao_obj_vq);' + NL +
     T * 4 + 'return;' + NL),
    ('PROBE', 'nz_skip_fb', VQ + T * 2 + '}' + NL, VQ + T * 3 + 'return;' + NL + T * 2 + '}' + NL),
    ('PROBE', 'copy_half', CPY, T * 3 + 'std::memcpy(copy.data(), pcm, static_cast<size_t>(bytes) / 2u);' + NL),
    ('PROBE', 'check_one_byte', OSR, T * 3 + 'if (!OsReadable(reinterpret_cast<uint64_t>(pcm), 1u)) {' + NL),
]


def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        sys.exit(3)


def build(tag):
    guard()
    log = '%s/build_%s.log' % (WORK, tag)
    with open(log, 'wb') as f:
        rc = subprocess.call(['python', HERE + '/lowrun.py', 'cmd', '/c',
                              'C:' + chr(92) + 'kyty' + chr(92) + 'm657' + chr(92) + 'm6a' + chr(92) +
                              'build_m6a.cmd target m_wave2_diag_stand'], stdout=f, stderr=subprocess.STDOUT)
    text = open(log, 'rb').read().decode('utf-8', 'replace')
    return rc == 0 and 'BUILD OK' in text


def stand(tag):
    guard()
    out = '%s/stand_%s' % (WORK, tag)
    p = subprocess.run(['python', DRV, EXE, out], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text = p.stdout.decode('utf-8', 'replace')
    open(out + '.out.txt', 'w', encoding='utf-8', newline='\n').write(text)
    last = text.strip().splitlines()[-1] if text.strip() else ''
    fails = [l for l in text.splitlines() if l.startswith('FAILED ') or ':' in l and 'want' in l]
    return last, fails, text


def main():
    os.makedirs(WORK, exist_ok=True)
    lines = []
    ok = True
    for group, name, old, new in MUTANTS:
        path = os.path.join(WT, D)
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
            if not build(name):
                lines.append('%s NOBUILD %s' % (group, name))
                ok &= group != 'NAMED'
                continue
            last, fails, out = stand(name)
            caught = last == 'FAIL'
            if group == 'NAMED':
                ok &= caught
            failed = [l for l in out.splitlines() if l.startswith('FAILED ')]
            lines.append('%s %s %s (%d failed members; first: %s)' % (group, 'CAUGHT' if caught else 'SURVIVED', name,
                                                                      len(failed), failed[0][7:150] if failed else '-'))
        finally:
            open(path, 'wb').write(orig)
            if hashlib.sha256(open(path, 'rb').read()).hexdigest() != sha0:
                lines.append('RESTORE FAILED %s' % name)
                ok = False
        print(lines[-1])
        sys.stdout.flush()
    built = build('control')
    last, _, _ = stand('control') if built else ('NOBUILD', [], '')
    lines.append('CONTROL restored tree: build=%d driver=%s' % (1 if built else 0, last))
    ok &= built and last == 'ALL OK'
    lines.append('ALL OK' if ok else 'FAIL')
    print(NL.join(lines[-2:]))
    open(OUT + '/mut_m6b3.out.txt', 'w', encoding='utf-8', newline='\n').write(NL.join(lines) + NL)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

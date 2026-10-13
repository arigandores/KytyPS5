"""Red Team M6b2 (HPP-855): own mutants of the M6a2 edits against the stand (driver ../m6a2/run_stand_m6a2.py).
Method of m6a2/mut_m6a2.py: one exact text substitution (must match once) in C:/kyty/m657/m6a/wt, stand target rebuilt
(build_m6a.cmd target m_wave2_diag_stand, IDLE, --parallel 2), driver run, file restored byte for byte (sha256 checked);
control rebuild of the restored tree must print ALL OK. Two groups:
  NAMED  - the mutants item 770(b), (v) requires the stand to catch (re-run): x_eq_div, c_minlod_div_x, c_clr_dw_div8,
           r8_never, rg8_always. Each must be CAUGHT.
  PROBE  - extra mutants of the decision field and the (a3) rule NOT named by item 770 (stand strength, report only):
           lvl_base (level = base_level), gt_ge (> -> >=), r8_low16 (R8 rule on the low 16 bits only),
           grain_half (GrainBytes half of the scanned bytes). Expected outcome printed, not a member.
Usage: python mut_m6b2.py   Output: mut_m6b2.out.txt beside this script; last line ALL OK (named caught + control) or FAIL.
"""
import hashlib
import os
import subprocess
import sys

HERE = 'C:/kyty/m657/m6a'
OUT = 'C:/kyty/KytyPS5/docs/track-m/m6b2'
DRV = 'C:/kyty/KytyPS5/docs/track-m/m6a2/run_stand_m6a2.py'
WT = HERE + '/wt'
EXE = HERE + '/build/m_wave2_diag_stand.exe'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
D = 'src/libs/diagM5W2.cpp'
T = chr(9)
NL = chr(10)
LVL = T + 'const uint64_t level = std::max<uint64_t>(base_level, level_count - 1u);'
CMPX = T + 'return static_cast<uint64_t>(min_lod) > level * 256u;'
R8 = 'case vk::Format::eR8Unorm: return word != (word & 0xffu) * 0x01010101u;'
RG8 = 'case vk::Format::eR8G8Unorm: return (word & 0xffffu) != (word >> 16u);'
GB = T + 'return static_cast<uint64_t>(samples) * channels * (data_type == 1 ? 2u : 4u);'

MUTANTS = [
    ('NAMED', 'x_eq_div', LVL, T + 'const uint64_t level = level_count - 1u;'),
    ('NAMED', 'c_minlod_div_x', T + T + 'Bump(g_minlod_div_x);' + NL, ''),
    ('NAMED', 'c_clr_dw_div8', T + T + 'Bump(g_clr_dw_div8);' + NL, ''),
    ('NAMED', 'r8_never', R8, 'case vk::Format::eR8Unorm: return false;'),
    ('NAMED', 'rg8_always', RG8, 'case vk::Format::eR8G8Unorm: return true;'),
    ('PROBE', 'lvl_base', LVL, T + 'const uint64_t level = base_level;'),
    ('PROBE', 'gt_ge', CMPX, T + 'return static_cast<uint64_t>(min_lod) >= level * 256u;'),
    ('PROBE', 'r8_low16', R8, 'case vk::Format::eR8Unorm: return (word & 0xffffu) != (word & 0xffu) * 0x0101u;'),
    ('PROBE', 'grain_half', GB, T + 'return static_cast<uint64_t>(samples) * channels * (data_type == 1 ? 2u : 4u) / 2u;'),
]


def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        sys.exit(3)


def build(tag):
    guard()
    log = '%s/mut_m6b2/build_%s.log' % (HERE, tag)
    with open(log, 'wb') as f:
        rc = subprocess.call(['python', HERE + '/lowrun.py', 'cmd', '/c',
                              'C:' + chr(92) + 'kyty' + chr(92) + 'm657' + chr(92) + 'm6a' + chr(92) +
                              'build_m6a.cmd target m_wave2_diag_stand'], stdout=f, stderr=subprocess.STDOUT)
    text = open(log, 'rb').read().decode('utf-8', 'replace')
    return rc == 0 and 'BUILD OK' in text


def stand(tag):
    guard()
    out = '%s/mut_m6b2/stand_%s' % (HERE, tag)
    p = subprocess.run(['python', DRV, EXE, out], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text = p.stdout.decode('utf-8', 'replace')
    open(out + '.out.txt', 'w', encoding='utf-8', newline='\n').write(text)
    last = text.strip().splitlines()[-1] if text.strip() else ''
    return last, [l for l in text.splitlines() if l.startswith('FAILED ')]


def main():
    os.makedirs(HERE + '/mut_m6b2', exist_ok=True)
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
            last, failed = stand(name)
            caught = last == 'FAIL'
            if group == 'NAMED':
                ok &= caught
            lines.append('%s %s %s (%d failed members; first: %s)' % (group, 'CAUGHT' if caught else 'SURVIVED', name,
                                                                      len(failed), failed[0][7:110] if failed else '-'))
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
    open(OUT + '/mut_m6b2.out.txt', 'w', encoding='utf-8', newline='\n').write(NL.join(lines) + NL)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

"""Red Team M6b (HPP-849): mutants "the divergence field counts everything" against the M6a stand (run_stand_m6a.py),
in the M6a worktree with the M6a build script; one exact substitution each, restored byte for byte; control rebuild.
Usage: python mut_m6b.py <out dir>. Last line ALL OK (every mutant caught, control ALL OK) or FAIL."""
import hashlib
import os
import subprocess
import sys

HERE = 'C:/kyty/m657/m6a'
WT = HERE + '/wt'
EXE = HERE + '/build/m_wave2_diag_stand.exe'
DRIVER = 'C:/kyty/KytyPS5/docs/track-m/m6a/run_stand_m6a.py'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
D = 'src/libs/diagM5W2.cpp'
T = chr(9)
NL = chr(10)

MUTANTS = [
    ('div_ao_obj_nz', D, T + T + 'if (nz) {' + NL + T + T + T + 'Bump(g_ao_obj_nz);', T + T + 'if (true) {' + NL + T + T + T + 'Bump(g_ao_obj_nz);'),
    ('div_ao_bus_nz', D, T + T + 'if (nz) {' + NL + T + T + T + 'Bump(g_ao_bus_nz);', T + T + 'if (true) {' + NL + T + T + T + 'Bump(g_ao_bus_nz);'),
    ('div_clr_dw_div', D, 'const bool     div = ClearDwordDiverges(vk_format, word);', 'const bool     div = true;'),
    ('div_minlod_div', D, 'if (MinLodDiverges(min_lod, base_level, level_count)) {', 'if (true) {'),
    ('div_inv_part', D, 'if (!covers) {', 'if (true) {'),
    ('div_raw_rd_gpu', D, 'if (gpu_image) {', 'if (true) {'),
]


def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        sys.exit(3)


def build(out, tag):
    guard()
    log = '%s/build_%s.log' % (out, tag)
    with open(log, 'wb') as f:
        rc = subprocess.call(['python', HERE + '/lowrun.py', 'cmd', '/c',
                              'C:' + chr(92) + 'kyty' + chr(92) + 'm657' + chr(92) + 'm6a' + chr(92) +
                              'build_m6a.cmd target m_wave2_diag_stand'], stdout=f, stderr=subprocess.STDOUT)
    text = open(log, 'rb').read().decode('utf-8', 'replace')
    return rc == 0 and 'BUILD OK' in text


def stand(out, tag):
    guard()
    d = '%s/stand_%s' % (out, tag)
    os.makedirs(d, exist_ok=True)
    p = subprocess.run(['python', DRIVER, EXE, d], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text = p.stdout.decode('utf-8', 'replace')
    open(d + '.out.txt', 'w', encoding='utf-8', newline='\n').write(text)
    last = text.strip().splitlines()[-1] if text.strip() else ''
    return last, [l for l in text.splitlines() if l.startswith('FAILED ')]


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    lines = []
    ok = True
    for name, rel, old, new in MUTANTS:
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
            if not build(out, name):
                lines.append('NOBUILD %s' % name)
                ok = False
                continue
            last, failed = stand(out, name)
            caught = last == 'FAIL'
            ok &= caught
            lines.append('%s %s (%d failed members; first: %s)' % ('CAUGHT' if caught else 'SURVIVED', name, len(failed),
                                                                   failed[0][7:120] if failed else '-'))
        finally:
            open(path, 'wb').write(orig)
            if hashlib.sha256(open(path, 'rb').read()).hexdigest() != sha0:
                lines.append('RESTORE FAILED %s' % name)
                ok = False
        print(lines[-1])
        sys.stdout.flush()
    built = build(out, 'control')
    last, failed = stand(out, 'control') if built else ('NOBUILD', [])
    lines.append('CONTROL restored tree: build=%d driver=%s' % (1 if built else 0, last))
    ok &= built and last == 'ALL OK'
    lines.append('ALL OK' if ok else 'FAIL')
    print(NL.join(lines[-2:]))
    open(out + '/mut_m6b.out.txt', 'w', encoding='utf-8', newline='\n').write(NL.join(lines) + NL)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

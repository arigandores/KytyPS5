"""Track M, M7a (HPP-852, ROADMAP s122 items 767(g), 767(l)): mutants of the T306 repair against shader_cfg_tests
(filter MWave1T306: TestMWave1T306OffsetWriteMask, TestMWave1T306EbootPrograms with KYTY_TEST_T306_EBOOT). Each mutant is
one exact text substitution (must match once) in the worktree C:/kyty/m657/m7a/wt; shader_cfg_tests is rebuilt
(build_m7a.cmd tests, IDLE priority) and run at KYTY_M_T306=1 and =0; a mutant is CAUGHT when a run fails (rc != 0 or a
line "failed"). The file is restored byte for byte after each mutant. At the end the restored tree is rebuilt and both
runs must pass (control).
  t306_mask    - M2c mutant: the offset written under ANY lane mask is taken as constant (exec equality dropped)
  t306_full    - the repair reverted: any SelectU32 is read as the wrapper (the flags check dropped)
  t306_noflag  - the translator emits the wrapper without IR::MSampleOffsetWrapperFlags
  t306_silent  - the offset dropped silently: no "MTexOffset: ... nonconstant offset" line and no count
  t306_sign    - the six-bit fields of the offset are not sign-extended
Usage: python mut_m7a.py [--only <name>]   Output: mut_m7a.out.txt beside; last line ALL OK or FAIL."""
import hashlib
import os
import subprocess
import sys

HERE = 'C:/kyty/m657/m7a'
WT = HERE + '/wt'
EXE = HERE + '/build/shader_cfg_tests.exe'
EBOOT = HERE + '/cs7b'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
IMG = 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp'
MEM = 'src/graphics/shader/recompiler/frontend/translate/Memory.cpp'
T = chr(9)
NL = chr(10)
BS = chr(92)
IDLE = 0x40

MUTANTS = [
    ('t306_mask', IMG,
     T + '       write->Arg(0).Resolve() == exec && MImmediateU32(write->Arg(1).Resolve(), packed);' + NL,
     T + '       MImmediateU32(write->Arg(1).Resolve(), packed);' + NL),
    ('t306_full', IMG,
     T + 'if (wrapper == nullptr || wrapper->GetOpcode() != IR::ValueOpcode::SelectU32 ||' + NL +
     T + '    wrapper->Flags<uint64_t>() != IR::MSampleOffsetWrapperFlags) {' + NL,
     T + 'if (wrapper == nullptr || wrapper->GetOpcode() != IR::ValueOpcode::SelectU32) {' + NL),
    ('t306_noflag', MEM,
     T + T + '                   IR::MSampleOffsetWrapperFlags);' + NL,
     T + T + '                   uint64_t {0});' + NL),
    ('t306_silent', IMG,
     T * 4 + 'LOGF("MTexOffset: shader=0x%016llx pc=0x%x nonconstant offset, previous path' + BS + 'n",' + NL +
     T * 4 + '     static_cast<unsigned long long>(state.program.shader_hash),' + NL +
     T * 4 + '     inst.Flags<IR::MemoryFlags>().pc);' + NL +
     T * 4 + 'MTexOffsetCount(0u);' + NL,
     ''),
    ('t306_sign', IMG,
     T + T + 'values[index]   = static_cast<int32_t>(bits ^ 0x20u) - 0x20;' + NL,
     T + T + 'values[index]   = static_cast<int32_t>(bits);' + NL),
]


def halt():
    return os.path.exists(LOCK) or os.path.exists(STOP)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def build(tag):
    log = '%s/mut/build_%s.log' % (HERE, tag)
    with open(log, 'wb') as f:
        rc = subprocess.run(['cmd', '/c', HERE.replace('/', BS) + BS + 'build_m7a.cmd', 'tests'], stdout=f,
                            stderr=subprocess.STDOUT, creationflags=IDLE).returncode
    return rc


def run_tests(tag, knob):
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env.update({'KYTY_TESTS_CONTINUE': '1', 'KYTY_TESTS_VERBOSE': '1', 'KYTY_TESTS_FILTER': 'MWave1T306',
                'KYTY_M_T306': knob, 'KYTY_TEST_T306_EBOOT': EBOOT})
    out = '%s/mut/run_%s_%s.txt' % (HERE, tag, knob)
    with open(out, 'wb') as f:
        rc = subprocess.run([EXE], stdout=f, stderr=subprocess.STDOUT, cwd=HERE + '/build', env=env, timeout=300,
                            creationflags=IDLE).returncode
    text = open(out, 'rb').read().decode('utf-8', 'replace')
    failed = [l for l in text.split(NL) if 'failed' in l.lower()]
    return rc, failed


def main():
    only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
    os.makedirs(HERE + '/mut', exist_ok=True)
    lines = []
    ok = True

    def say(s):
        print(s)
        sys.stdout.flush()
        lines.append(s)

    say('exe before mutants %s' % sha(EXE))
    for name, path, old, new in MUTANTS:
        if only and name != only:
            continue
        if halt():
            say('HALT (lock or STOP)')
            return 3
        full = WT + '/' + path
        raw = open(full, 'rb').read()
        text = raw.decode('utf-8')
        if text.count(old) != 1:
            say('%s ANCHOR %d' % (name, text.count(old)))
            ok = False
            continue
        open(full, 'wb').write(text.replace(old, new).encode('utf-8'))
        try:
            brc = build(name)
            if brc != 0:
                say('%s BUILD FAILED rc %d' % (name, brc))
                ok = False
                continue
            r1 = run_tests(name, '1')
            r0 = run_tests(name, '0')
        finally:
            open(full, 'wb').write(raw)
        caught = r1[0] != 0 or r1[1] or r0[0] != 0 or r0[1]
        say('%s %s  =1 rc %d failed %s | =0 rc %d failed %s' % (name, 'CAUGHT' if caught else 'SURVIVED', r1[0],
                                                               [l.strip()[:110] for l in r1[1]][:3], r0[0],
                                                               [l.strip()[:110] for l in r0[1]][:3]))
        ok &= bool(caught)
    if halt():
        say('HALT (lock or STOP)')
        return 3
    brc = build('control')
    r1 = run_tests('control', '1')
    r0 = run_tests('control', '0')
    ctl = brc == 0 and r1[0] == 0 and not r1[1] and r0[0] == 0 and not r0[1]
    say('CONTROL restored tree: build rc %d, =1 rc %d failed %d, =0 rc %d failed %d -> %s' % (
        brc, r1[0], len(r1[1]), r0[0], len(r0[1]), 'PASS' if ctl else 'FAIL'))
    say('exe after control %s' % sha(EXE))
    ok &= ctl
    say('ALL OK' if ok else 'FAIL')
    open(HERE + '/mut_m7a.out.txt', 'w', newline=NL).write(NL.join(lines) + NL)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

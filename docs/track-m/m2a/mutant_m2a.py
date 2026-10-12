"""M2a (HPP-838, ROADMAP s122 item 756(v)(1)(iv)): mutants - one per theme, a rollback of the core of the fix taken at =1
in the worktree C:/kyty/m657/m2/wt (patched), build shader_cfg_tests and shader_recompiler_compute_tests, keep the
binaries in bin/mut_<theme>_*.exe, restore the file byte for byte (sha256 checked). The mutant is caught when, at
KYTY_M_<theme>=1, the GPU gate case(s) of the theme or the shader_cfg_tests block of the theme fail.
Usage: python mutant_m2a.py <theme>   (build) ;  python mutant_m2a.py <theme> --run  (tests on the kept binaries).
Lock and STOP checked before every process."""
import hashlib
import os
import re
import subprocess
import sys

WT = 'C:/kyty/m657/m2/wt/src/graphics/shader/recompiler/'
M2A = 'C:/kyty/m657/m2a'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
MUTANTS = {
    'T234': ('backend/spirv/spirvEmitterMemory.cpp',
             '\t\t\t\t        if (Decoder::MThemeEnabled(Decoder::MTheme::T234)) {\n'
             '\t\t\t\t\t        // Track M, M2a (T234, upstream e85279ea; KYTY_M_T234): min/max of the word and DATA0\n',
             '\t\t\t\t        if (false) {\n'
             '\t\t\t\t\t        // Track M, M2a (T234, upstream e85279ea; KYTY_M_T234): min/max of the word and DATA0\n',
             'emitter replacement of DS_MIN/MAX_F32 rolled back (the decoder and translator keep two operands)'),
    'T233': ('backend/spirv/spirvEmitterAlu.cpp',
             '\ta                  = EmitFlushF32DenormToSignedZero(state, a);\n',
             '\treturn EmitFPFma32(state, a, b, c);\n\ta                  = EmitFlushF32DenormToSignedZero(state, a);\n',
             'EmitFPMad32 returns the fused Fma again'),
    'T203': ('frontend/translate/Integer.cpp',
             '\t\tconst auto shift   = ir.ShiftLeftLogical(ir.BitwiseAnd(ReadU32(inst.src2), IR::U32(IR::Value(3u))),\n',
             '\t\tconst auto shift   = ir.ShiftLeftLogical(ir.BitwiseAnd(ReadU32(inst.src2), IR::U32(IR::Value(31u))),\n',
             'byte selector mask 3 -> 31 in the =1 branch'),
    'T306': ('backend/spirv/spirvEmitterImage.cpp',
             '\t\tvalues[index]   = static_cast<int32_t>(bits ^ 0x20u) - 0x20;\n',
             '\t\tvalues[index]   = static_cast<int32_t>(bits);\n',
             'six-bit offset fields without sign extension'),
    'T032': ('backend/spirv/spirvEmitterMemory.cpp',
             '\t\t\tvalue = EmitFPRoundEven32(state, EmitFPMul32(state, value, ConstantF32Value(state, max_value)));\n',
             '\t\t\tvalue = EmitFPMul32(state, value, ConstantF32Value(state, max_value));\n',
             'normalized encode without round to nearest even (truncation)'),
    'T256': ('backend/spirv/spirvEmitterFlow.cpp',
             '\t\t\tunpack = GLSLstd450UnpackSnorm2x16;\n',
             '\t\t\tunpack = GLSLstd450UnpackHalf2x16;\n',
             'SNORM16 compressed export unpacked as half again'),
}


def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        sys.exit(3)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def build(theme):
    path, old, new, what = MUTANTS[theme]
    full = WT + path
    raw = open(full, 'rb').read()
    before = sha(full)
    text = raw.decode('utf-8')
    if text.count(old) != 1:
        print('mutant anchor count', text.count(old))
        return 1
    guard()
    open(full, 'wb').write(text.replace(old, new).encode('utf-8'))
    try:
        for tgt, name in (('tests', 'shader_cfg_tests'), ('target shader_recompiler_compute_tests',
                                                            'shader_recompiler_compute_tests')):
            guard()
            p = subprocess.run(['cmd', '/c', 'C:\\kyty\\m657\\m2\\build_m2.cmd ' + tgt], capture_output=True)
            log = p.stdout + p.stderr
            open('%s/mut/build_%s_%s.log' % (M2A, theme, name), 'wb').write(log)
            if p.returncode != 0:
                print('build failed', name)
                return 1
            src = 'C:/kyty/m657/m2/build/%s.exe' % name
            dst = '%s/bin/mut_%s_%s.exe' % (M2A, theme, name)
            open(dst, 'wb').write(open(src, 'rb').read())
            print('mutant', theme, name, sha(dst))
    finally:
        open(full, 'wb').write(raw)
    print('restored', path, 'sha equal', sha(full) == before, '-', what)
    return 0


def run(theme):
    guard()
    cfg = '%s/bin/mut_%s_shader_cfg_tests.exe' % (M2A, theme)
    gpu = '%s/bin/mut_%s_shader_recompiler_compute_tests.exe' % (M2A, theme)
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env.update({'KYTY_M_' + theme: '1', 'KYTY_TESTS_CONTINUE': '1', 'KYTY_TESTS_FILTER': 'TestMWave1Translator'})
    p = subprocess.run([cfg], capture_output=True, env=env, cwd=os.path.dirname(cfg), timeout=300)
    text = (p.stdout + p.stderr).decode('utf-8', 'replace')
    open('%s/mut/cfg_%s.txt' % (M2A, theme), 'w', newline='\n').write(text)
    cfg_fail = [l for l in text.split('\n') if 'failed:' in l or 'Check failed' in l or ('T%s' % theme[1:]) in l and
                'does not follow' in l]
    print('cfg rc', p.returncode, 'lines', ' | '.join(l.strip() for l in text.split('\n') if '[mw1] ' + theme in l)[:300])
    print('cfg failure lines', len(cfg_fail), cfg_fail[:2])
    guard()
    names = subprocess.run([gpu, '--m-wave1-list'], capture_output=True, env=env, cwd=os.path.dirname(gpu),
                           timeout=120).stdout.decode().split()
    caught_gpu = 0
    total = 0
    for n in names:
        if not n.startswith('MW1' + theme):
            continue
        guard()
        total += 1
        q = subprocess.run([gpu, '--m-wave1-case', n], capture_output=True, env=env, cwd=os.path.dirname(gpu),
                           timeout=180)
        t = (q.stdout + q.stderr).decode('utf-8', 'replace')
        caught = q.returncode != 0 and 'ALL OK' not in t
        caught_gpu += int(caught)
        line = [l for l in t.split('\n') if 'failed at' in l]
        print('gpu', n, 'rc', q.returncode, 'CAUGHT' if caught else 'passed', (line[0][:200] if line else ''))
    caught_any = caught_gpu > 0 or p.returncode != 0 or bool(cfg_fail)
    print('mutant', theme, 'gpu caught %d of %d' % (caught_gpu, total), 'cfg rc', p.returncode,
          'CAUGHT' if caught_any else 'NOT CAUGHT')
    return 0 if caught_any else 1


if __name__ == '__main__':
    os.makedirs(M2A + '/mut', exist_ok=True)
    theme = sys.argv[1]
    sys.exit(run(theme) if '--run' in sys.argv else build(theme))

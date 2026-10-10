# F35b (HPP-756, ROADMAP s122 item 685(g)): mutants of the F35a test TestF22IndirectNullComparison in the own worktree
# C:/kyty/f287/f35b/wt (399d3271 = FS11 ee9632be + the test). N = 6, no seed (the list is fixed before data; comment
# b27a70ba on HPP-756). Anchors - whole lines; files are LF (CR 0 in the worktree); write_bytes keeps LF.
"""Usage:
  python mut_f35b.py apply <m>   - apply mutant m (m1a m1b m2 m3 m4 m5) to the clean worktree
  python mut_f35b.py revert      - git checkout of the mutated files (worktree back to 399d3271)
  python mut_f35b.py run <label> - shader_cfg_tests of build/, KYTY_TESTS_FILTER=TestF22 at KYTY_FIX_F19=0 and =1
                                   -> out/<label>_f19<v>/{log.txt,rc.txt,exe_sha256.txt}; prints [f22] and failed lines
"""
import hashlib
import os
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
WT = 'C:/kyty/f287/f35b/wt'
EXE = 'C:/kyty/f287/f35b/build/shader_cfg_tests.exe'
OUT = 'C:/kyty/f287/f35b/out'
GIT = 'C:/Program Files/Git/cmd/git.exe'
RM = 'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp'
EM = 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp'
TS = 'tests/shaderCfgTests.cpp'
SP = ' ' * 79

MUTANTS = {
    # m1a (lead m1): a null T# is shader-compared at =1.
    'm1a': [(RM, '\treturn !null_descriptor && FindGuestDepthFormatPolicy(format) == nullptr;',
             '\treturn null_descriptor || FindGuestDepthFormatPolicy(format) == nullptr;')],
    # m1b (lead m1, "native the other way round"): shader comparison only for policy (depth) formats.
    'm1b': [(RM, '\treturn !null_descriptor && FindGuestDepthFormatPolicy(format) == nullptr;',
             '\treturn !null_descriptor && FindGuestDepthFormatPolicy(format) != nullptr;')],
    # m2 (lead): the view mirror is always "depth".
    'm2': [(TS, SP + ': F22View::NullR32F;', SP + ': F22View::NullD32;'),
           (TS, SP + ' : F22View::TsharpColor;', SP + ' : F22View::TsharpDepth;')],
    # m3 (lead): the materialization drops the last candidate of a table.
    'm3': [(RM, '\t\tfor (uint32_t candidate = 1; candidate < table.descriptors.size(); candidate++) {',
            '\t\tfor (uint32_t candidate = 1; candidate + 1 < table.descriptors.size(); candidate++) {')],
    # m4 (own): variant O1 off - no merge of manual_depth_compare over the table at =1.
    'm4': [(RM, '\t\tFixF19MergeIndirectTables(next_specialization.images);',
            '\t\t(void)next_specialization; // F35b m4: FixF19MergeIndirectTables removed')],
    # m5 (own): the emitter never takes the manual comparison path.
    'm5': [(EM, '\t\tconst bool  manual_dref    = dref && image.manual_depth_compare;',
            '\t\tconst bool  manual_dref    = dref && image.manual_depth_compare && false;')],
}


def guard():
    if os.path.exists(LOCK):
        print('HALT lock')
        sys.exit(5)
    if os.path.exists(STOP):
        print('HALT stop')
        sys.exit(4)


def apply(m):
    for path, old, new in MUTANTS[m]:
        p = WT + '/' + path
        data = open(p, 'rb').read()
        assert b'\r' not in data, p
        lines = data.split(b'\n')
        hits = [i for i, l in enumerate(lines) if l == old.encode()]
        if len(hits) != 1:
            print('ANCHOR', m, path, len(hits))
            sys.exit(2)
        lines[hits[0]] = new.encode()
        open(p, 'wb').write(b'\n'.join(lines))
        print('applied', m, path, 'line', hits[0] + 1)


def revert():
    subprocess.run([GIT, '-C', WT, 'checkout', '--', RM, EM, TS], check=True)
    r = subprocess.run([GIT, '-C', WT, 'status', '--short', '--ignore-submodules=all'], capture_output=True, text=True)
    print('reverted, status lines', len([l for l in r.stdout.splitlines() if l.strip()]))


def run(label):
    for v in ('0', '1'):
        guard()
        out = '%s/%s_f19%s' % (OUT, label, v)
        os.makedirs(out, exist_ok=True)
        env = {k: val for k, val in os.environ.items() if not k.startswith('KYTY_')}
        env['KYTY_TESTS_CONTINUE'] = '1'
        env['KYTY_TESTS_VERBOSE'] = '1'
        env['KYTY_TESTS_FILTER'] = 'TestF22'
        env['KYTY_FIX_F19'] = v
        r = subprocess.run([EXE], capture_output=True, text=True, cwd=os.path.dirname(EXE), env=env, errors='replace')
        log = r.stdout + r.stderr
        open(out + '/log.txt', 'w', encoding='utf-8', newline='\n').write(log)
        open(out + '/rc.txt', 'w', encoding='utf-8', newline='\n').write('%d\n' % r.returncode)
        sha = hashlib.sha256(open(EXE, 'rb').read()).hexdigest()
        open(out + '/exe_sha256.txt', 'w', encoding='utf-8', newline='\n').write(sha + '\n')
        print(label, 'f19=' + v, 'rc', r.returncode, 'exe', sha[:8])
        for line in log.splitlines():
            if line.startswith('[f22]') or 'failed' in line.lower() or 'check' in line.lower():
                print('  ', line[:300])


if __name__ == '__main__':
    guard()
    if sys.argv[1] == 'apply':
        apply(sys.argv[2])
    elif sys.argv[1] == 'revert':
        revert()
    elif sys.argv[1] == 'run':
        run(sys.argv[2])

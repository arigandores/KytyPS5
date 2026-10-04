"""F14f2 (HPP-546, ROADMAP s122 item 443(g)): mutants on the RC3 probe - apply (whole-line anchors, count 1, LF bytes),
build shader_cfg_tests under the F14e2 watchdog, keep the exe, revert, git status 0, run suite_f14f2.py mut.

  python mut_f14f2.py <name>     names: M5 X1 X2 X3 X4
"""
import os
import shutil
import subprocess
import sys

WT = 'C:/kyty/f287/f14f2/wt'
D = 'C:/kyty/f287/f14f2'
GIT = 'C:/Program Files/Git/cmd/git.exe'
RM = 'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp'
TS = 'tests/shaderCfgTests.cpp'
NL = chr(10)

MUT = {
    # X1: probe (2) without the shared sampler - k16UNorm on its own S# s[20:23] (same LESS_EQUAL compare)
    'X1': (TS, [('    shader.push_back(EncodeMimg1(1, 2, 4, 4)); // v1, v[4:6], T# s[8:15] (k16UNorm), S# s[16:19]',
                 '    shader.push_back(EncodeMimg1(1, 2, 5, 4)); user_data[20] = 3u << 12u; user_data[21] = 0u; '
                 'user_data[22] = 0u; user_data[23] = 0u; // F14f2 X1: own S# s[20:23]')],
           '1:pass,0:fail,u:fail'),
    # X2: the =1 expectation of probe (2) replaced by the manual pattern
    'X2': (TS, [('      Check(shared.native_images == 2u && shared.manual_images == 0u && shared.dref == 2u &&',
                 '      Check(shared.native_images == 0u && shared.manual_images == 2u && shared.dref == 0u && // F14f2 X2'),
                ('                shared.manual == 0u,', '                shared.manual == 2u, // F14f2 X2')],
           '1:fail,0:pass,u:pass'),
    # X3: the =1 rule degenerates to the rule before the fix (k16UNorm manual again)
    'X3': (RM, [('\treturn !null_descriptor && FindGuestDepthFormatPolicy(format) == nullptr;',
                 '\treturn !null_descriptor && format != Prospero::BufferFormat::k32Float; // F14f2 X3')],
           '1:fail,0:pass,u:pass'),
    # X4: the call site of the =1 rule drops the null flag (M5 by another place)
    'X4': (RM, [('\t\t\t\t    FixF19ManualDepthCompare(format, NullImageDescriptor(descriptor));',
                 '\t\t\t\t    FixF19ManualDepthCompare(format, false); // F14f2 X4')],
           '1:fail,0:pass,u:pass'),
}


def sh(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, **kw)


def status():
    out = sh([GIT, '-C', WT, 'status', '--porcelain', '--ignore-submodules=all']).stdout
    return [l for l in out.split(NL) if l.strip()]


def main(name):
    if os.path.exists('C:/kyty/SEALED_RUN.lock'):
        print('HALT lock'); return 3
    if os.path.exists('C:/kyty/f287/STOP'):
        print('HALT stop'); return 4
    assert status() == [], status()
    if name == 'M5':
        r = sh([GIT, '-C', WT, 'apply', 'C:/kyty/KytyPS5/docs/track-f/f14f/mut/M5/mutant.diff'])
        print('apply M5 rc', r.returncode, r.stderr.strip())
        files = [RM]
        expect = '1:fail,0:pass,u:pass'
    else:
        path, reps, expect = MUT[name]
        p = WT + '/' + path
        s = open(p, 'rb').read().decode('utf-8')
        lines = s.split(NL)
        for a, b in reps:
            n = sum(1 for l in lines if l == a)
            assert n == 1, (name, a, n)
            lines = [b if l == a else l for l in lines]
        open(p, 'wb').write(NL.join(lines).encode('utf-8'))
        files = [path]
    st = status()
    print('applied', name, 'status', st)
    diff = sh([GIT, '-C', WT, 'diff']).stdout
    open('%s/mut/%s.diff' % (D, name), 'w', encoding='utf-8', newline='').write(diff)
    try:
        r = sh(['C:/Program Files/Git/usr/bin/bash.exe', 'C:/kyty/f287/f14e2/api_chk.sh', 'F14f2 build mutant ' + name])
        print(r.stdout.strip().split(NL)[-1] if r.stdout.strip() else 'api_chk rc %d' % r.returncode)
        if r.returncode != 0:
            return r.returncode
        r = sh(['python', 'C:/kyty/f287/f14f2/watch_f14f2.py', '--limit', os.environ.get('MUT_LIMIT', '540'), '--tag', 'F14f2 mutant ' + name, '--',
                'cmd', '/c', 'C:\\kyty\\f287\\f14f2\\build_f14f2.cmd', 'tests'])
        open('%s/mut/build_%s.log' % (D, name), 'w', encoding='utf-8').write(r.stdout + r.stderr)
        ok_build = 'BUILD OK' in r.stdout
        print('build', name, 'rc', r.returncode, 'BUILD OK' if ok_build else 'BUILD FAILED')
        if ok_build:
            shutil.copy(D + '/build/shader_cfg_tests.exe', '%s/mut/shader_cfg_tests_%s.exe' % (D, name))
    finally:
        r = sh([GIT, '-C', WT, 'checkout', '--'] + files)
        print('revert rc', r.returncode, 'status lines', len(status()))
    if not ok_build:
        return 2
    r = sh(['python', D + '/suite_f14f2.py', 'mut', 'm_' + name, '%s/mut/shader_cfg_tests_%s.exe' % (D, name), expect])
    print(r.stdout.strip())
    return r.returncode


if __name__ == '__main__':
    os.makedirs(D + '/mut', exist_ok=True)
    sys.exit(main(sys.argv[1]))

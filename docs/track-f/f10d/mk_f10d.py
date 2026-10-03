"""Track F, link F10d (HPP-452, Red Team), ROADMAP s122 item 369(v)(2): own repeat of the F10c offline set and own mutants.

Steps (each a separate short command; every step checks the lock and STOP first):
  prep          - envFlag.h from the 68602c4f blob into inc/common/; own extraction of the region 'bool FixSvalEnabled() {'
                  .. end of ValidateShaderSpirv from the 68602c4f blob of pipelineCache.cpp; compare with the F10c file
                  (C:/kyty/f287/f10c/sval_body_f10c.inc and the git copy docs/track-f/f10c/sval_body_f10c.inc at 1a588fc2);
                  run_f10d.py = the 1a588fc2 blob of docs/track-f/f10c/run_f10c.py with OUT and TOOL taken from argv (two
                  whole-line substitutions, nothing else); variant directories var/<v>/ with the 1a588fc2 blob of
                  sval_f10c.cpp and the body (base = own extraction; mutants = one whole-line edit, anchor must occur once).
  build <v>     - build_tool_f10d.cmd var/<v>  -> var/<v>/sval.exe
  run <v>       - python run_f10d_cached.py var/<v>/out var/<v>/sval.exe (run_f10d.py with the SDK spirv-val calls memoized
                  on disk, resumable after a halt on the lock)  -> var/<v>/out/f10c_summary.txt, rc
  judge         - base: ALL OK, f10c_out.tsv and f10c_summary.txt equal to F10c byte for byte; each mutant: final FAIL
                  and every gate it is expected to break printed FAIL. Writes mut_f10d.txt. ASCII, ends with ALL OK.
"""
import hashlib
import os
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
GIT = 'C:/Program Files/Git/cmd/git.exe'
CODE = '68602c4f'
DOC = '1a588fc2'
D = 'C:/kyty/f287/f10d'
F10C = 'C:/kyty/f287/f10c'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
T = chr(9)

# name -> (anchor line, replacement line or None = delete, gates that must print FAIL)
MUTANTS = {
    'M1_no_option': (T * 3 + 'options.SetUniformBufferStandardLayout(true);', None, ['r_1-S151', 'r_1-C51']),
    'M2_ubo_ignored': (T * 2 + 'if (g_fix_sval_ubo_std_layout.load(std::memory_order_acquire)) {', T * 2 + 'if (true) {',
                       ['r_1u0-S151', 'r_1u0-asF10a']),
    'M3_mode_ignored': (T + 'if (FixSvalEnabled()) {', T + 'if (false) {', ['r_1-S151', 'r_1-stat']),
    'M4_stat_period': (T * 2 + 'if (checks % 256u == 0) {', T * 2 + 'if (checks % 255u == 0) {', ['r_1-stat', 'r_1u0-stat']),
    'M5_env_presence': (T + 'static const bool enabled = Common::EnvValueOn(std::getenv("KYTY_FIX_SVAL"));',
                        T + 'static const bool enabled = std::getenv("KYTY_FIX_SVAL") != nullptr;', ['envflag', 'r_0-S151']),
    'M6_no_reject_count': (T * 3 + 'rejected.fetch_add(1, std::memory_order_relaxed);', None, ['r_1u0-stat']),
}


def halt():
    if os.path.exists(LOCK):
        print('HALT lock')
        sys.exit(3)
    if os.path.exists(STOP):
        print('HALT stop')
        sys.exit(4)


def blob(rev, path):
    return subprocess.run([GIT, '-C', REPO, 'show', rev + ':' + path], capture_output=True, check=True).stdout


def sha(b):
    return hashlib.sha256(b).hexdigest()


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(data)
    assert open(path, 'rb').read() == data


def prep():
    ok = True
    env_h = blob(CODE, 'src/common/envFlag.h')
    write(D + '/inc/common/envFlag.h', env_h)
    print('envFlag.h %s sha256 %s' % (CODE, sha(env_h)))
    src = blob(CODE, 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp')
    assert b'\r' not in src
    lines = src.split(b'\n')
    a = [i for i, l in enumerate(lines) if l == b'bool FixSvalEnabled() {']
    v = [i for i, l in enumerate(lines) if l.startswith(b'bool ValidateShaderSpirv(')]
    ok &= len(a) == 1 and len(v) == 1
    b = v[0]
    while lines[b] != b'}':
        b += 1
    region = b'\n'.join(lines[a[0]:b + 1]) + b'\n'
    print('own extraction %s: lines %d-%d, %d bytes, sha256 %s' % (CODE, a[0] + 1, b + 1, len(region), sha(region)))
    local = open(F10C + '/sval_body_f10c.inc', 'rb').read()
    gitcopy = blob(DOC, 'docs/track-f/f10c/sval_body_f10c.inc')
    print('F10c local inc sha256 %s equal %s; git copy %s sha256 %s equal %s'
          % (sha(local), local == region, DOC, sha(gitcopy), gitcopy == region))
    ok &= local == region and gitcopy == region
    run_src = blob(DOC, 'docs/track-f/f10c/run_f10c.py').decode('ascii')
    old_out, old_tool = "OUT = 'C:/kyty/f287/f10c'\n", "TOOL = OUT + '/sval_f10c.exe'\n"
    ok &= run_src.count(old_out) == 1 and run_src.count(old_tool) == 1
    run_new = run_src.replace(old_out, 'OUT = sys.argv[1]  # F10d: was ' + old_out).replace(
        old_tool, 'TOOL = sys.argv[2]  # F10d: was ' + old_tool)
    write(D + '/run_f10d.py', run_new.encode('ascii'))
    print('run_f10d.py = run_f10c.py %s (sha256 %s) with OUT/TOOL from argv; sha256 %s'
          % (DOC, sha(run_src.encode('ascii')), sha(run_new.encode('ascii'))))
    cpp = blob(DOC, 'docs/track-f/f10c/sval_f10c.cpp')
    print('sval_f10c.cpp %s sha256 %s' % (DOC, sha(cpp)))
    variants = {'base': region}
    rl = region.decode('ascii').split('\n')
    for name, (anchor, repl, _) in MUTANTS.items():
        n = rl.count(anchor)
        print('mutant %s: anchor occurs %d' % (name, n))
        ok &= n == 1
        i = rl.index(anchor)
        m = list(rl)
        if repl is None:
            del m[i]
        else:
            m[i] = repl
        variants[name] = '\n'.join(m).encode('ascii')
    for name, body in variants.items():
        write('%s/var/%s/sval_f10c.cpp' % (D, name), cpp)
        write('%s/var/%s/sval_body_f10c.inc' % (D, name), body)
        print('variant %s body sha256 %s' % (name, sha(body)))
    print('PREP OK' if ok else 'PREP FAIL')
    return ok


def build(name):
    r = subprocess.run(['cmd', '/c', D.replace('/', '\\') + '\\build_tool_f10d.cmd', (D + '/var/' + name).replace('/', '\\')],
                       capture_output=True)
    text = (r.stdout + r.stderr).decode('latin1')
    write('%s/var/%s/build.log' % (D, name), text.encode('latin1'))
    exe = '%s/var/%s/sval.exe' % (D, name)
    ok = r.returncode == 0 and os.path.exists(exe)
    print('build %s rc %d exe sha256 %s' % (name, r.returncode, sha(open(exe, 'rb').read()) if ok else '-'))
    return ok


def run(name):
    out = '%s/var/%s/out' % (D, name)
    os.makedirs(out, exist_ok=True)
    r = subprocess.run([sys.executable, D + '/run_f10d_cached.py', out, '%s/var/%s/sval.exe' % (D, name)],
                       capture_output=True)
    write(out + '/run.out.txt', r.stdout + r.stderr)
    tail = (r.stdout + r.stderr).decode('latin1').strip().split('\n')[-1]
    print('run %s rc %d last line: %s' % (name, r.returncode, tail))
    return r.returncode


def judge():
    ok = True
    res = []
    base = '%s/var/base/out' % D
    s = open(base + '/f10c_summary.txt', 'rb').read()
    tsv = open(base + '/f10c_out.tsv', 'rb').read()
    s0 = open(F10C + '/f10c_summary.txt', 'rb').read()
    tsv0 = open(F10C + '/f10c_out.tsv', 'rb').read()
    last = s.decode('ascii').strip().split('\n')[-1]
    res.append('base: last line %s; PASS gates %d, FAIL gates %d; summary = F10c %s; f10c_out.tsv = F10c %s (sha256 %s)'
               % (last, s.count(b'\nPASS '), s.count(b'\nFAIL '), s == s0, tsv == tsv0, sha(tsv)[:8]))
    ok &= last == 'ALL OK' and tsv == tsv0
    if s != s0:
        a, b = s.decode('ascii').split('\n'), s0.decode('ascii').split('\n')
        res.append('  summary lines differing: %d' % sum(x != y for x, y in zip(a, b)))
        for x, y in zip(a, b):
            if x != y:
                res.append('  F10d: ' + x[:200])
                res.append('  F10c: ' + y[:200])
    for name, (_, _, gates) in MUTANTS.items():
        p = '%s/var/%s/out/f10c_summary.txt' % (D, name)
        if not os.path.exists(p):
            res.append('%s: NO SUMMARY' % name)
            ok = False
            continue
        t = open(p, 'rb').read().decode('ascii')
        fails = [l.split(':', 1)[0][5:] for l in t.split('\n') if l.startswith('FAIL ')]
        lastm = t.strip().split('\n')[-1]
        killed = lastm == 'FAIL' and all(g in fails for g in gates)
        res.append('%s: last line %s; FAIL gates %s; expected %s -> %s' % (name, lastm, fails, gates,
                                                                         'KILLED' if killed else 'SURVIVED'))
        ok &= killed
    res.append('ALL OK' if ok else 'FAIL')
    text = '\n'.join(res) + '\n'
    write(D + '/mut_f10d.txt', text.encode('ascii'))
    sys.stdout.write(text)
    return ok


if __name__ == '__main__':
    halt()
    step = sys.argv[1]
    if step == 'prep':
        sys.exit(0 if prep() else 1)
    if step == 'build':
        sys.exit(0 if build(sys.argv[2]) else 1)
    if step == 'run':
        sys.exit(run(sys.argv[2]))
    if step == 'judge':
        sys.exit(0 if judge() else 1)
    sys.exit(2)

"""Track M, M7b (HPP-853, ROADMAP s122 items 767(l), 773(g)): OWN mutants of the T306 repair (own substitutions, own
binaries) in the M7b worktree C:/kyty/m657/m7b/wt (= 91a46dc5). For every mutant: one exact substitution (must match
once, LF file), shader_cfg_tests rebuilt (build_m7b.cmd tests, IDLE priority), then
  T1  filter MWave1T306 at KYTY_M_T306=1 and =0 with KYTY_TEST_T306_EBOOT = the words cut from eboot.bin by
      oracle_m7b.py (C:/kyty/m657/m7b/oracle/eboot_words);
  T2  KYTY_RECOMPILE of the game-cache permutation of CS 7b4078750f32db50 at =1 (recompile-t306 lines; the expected
      answer of the unmutated tree: 6 records, pairs (1,1)x2 (1,0)x2 (0,1)x2, fallback nonconstant 0).
CAUGHT_BY_TEST = a T1 run fails (rc != 0 or a 'failed' line); CAUGHT_BY_RECOMPILE = T2 differs from the expected answer.
The file is restored byte for byte after each mutant; at the end the restored tree is rebuilt, the tests pass at =1/=0,
T2 is the expected answer and the sha256 of the test exe equals the one before the mutants (control).
  k1_mask        offset written under ANY lane mask taken as constant (exec equality dropped)        [767(l) t306_mask]
  k2_full        the repair reverted: the flags check of the wrapper dropped                         [767(l) t306_full]
  k3_silent      nonconstant branch: no MTexOffset line and no count ("offset dropped silently")    [767(l)]
  k3b_line_only  nonconstant branch: the LOGF line removed, the count kept
  k3c_count_only nonconstant branch: the count removed, the LOGF line kept
  k4_lit_reject  an immediate offset (folded wrapper, constant mask, literal) is not taken           [773(g)(2)]
  k5_noflag      the translator emits the wrapper without the flags
  k7_indirect    samples on a resource other than mem.resource lose the offset (turned out equivalent here)
  k7b_indirect   samples of indirect candidates 1.. lose the offset (equivalent here: 7b407875 is not indirect)
  k8_lane_half   the second lane half of a wave64 program on a 32-wide host loses the offset       [773(g)(3)]
Usage: python mut_m7b.py [--only k1_mask,... | --only control]   Output: mut_m7b.out.txt beside; last line ALL DONE or STOPPED."""
import hashlib
import os
import re
import subprocess
import sys

HERE = 'C:/kyty/m657/m7b'
WT = HERE + '/wt'
EXE = HERE + '/build/shader_cfg_tests.exe'
EBOOT = HERE + '/oracle/eboot_words'
CS_GCN = HERE + '/oracle/eboot_words/7b4078750f32db50.bin'
CS_CACHE = 'C:/kyty/m657/m7a/cs7b/cs_7b4078750f32db50_28f7a21f24d8d3cc.bin'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
IMG = 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp'
MEM = 'src/graphics/shader/recompiler/frontend/translate/Memory.cpp'
IDLE = 0x40
NL = chr(10)
BS = chr(92)

LOG_START = 'LOGF("MTexOffset: shader=0x%016llx pc=0x%x nonconstant offset, previous path'
LOG_END = 'inst.Flags<IR::MemoryFlags>().pc);'
COUNT = 'MTexOffsetCount(0u);'


def span_log(text):
    a = text.index(LOG_START)
    b = text.index(LOG_END, a) + len(LOG_END)
    return a, b


def m_silent(text):
    a, _ = span_log(text)
    c = text.index(COUNT, a) + len(COUNT)
    return text[:a] + '(void)0;' + text[c:]


def m_line_only(text):
    a, b = span_log(text)
    return text[:a] + '(void)0;' + text[b:]


def m_count_only(text):
    a, b = span_log(text)
    c = text.index(COUNT, b)
    return text[:c] + text[c + len(COUNT):]


def sub(old, new):
    def f(text):
        if text.count(old) != 1:
            raise SystemExit('anchor count %d: %r' % (text.count(old), old))
        return text.replace(old, new)
    return f


MUTANTS = [
    ('k1_mask', IMG, sub('write->Arg(0).Resolve() == exec && ', '')),
    ('k2_full', IMG, sub('wrapper->Flags<uint64_t>() != IR::MSampleOffsetWrapperFlags', 'false')),
    ('k3_silent', IMG, m_silent),
    ('k3b_line_only', IMG, m_line_only),
    ('k3c_count_only', IMG, m_count_only),
    ('k4_lit_reject', IMG, sub('if (MImmediateU32(value, packed)) {', 'if (false && MImmediateU32(value, packed)) {')),
    ('k5_noflag', MEM, sub('IR::MSampleOffsetWrapperFlags);', 'uint64_t {0});')),
    ('k7_indirect', IMG, sub('const auto m_offset = m_t306_offset ? MSampleConstOffset',
                             'const auto m_offset = (m_t306_offset && resource == mem.resource) ? MSampleConstOffset')),
    ('k8_lane_half', IMG, sub('const auto m_offset = m_t306_offset ? MSampleConstOffset',
                              'const auto m_offset = (m_t306_offset && state.lane_half == 0u) ? MSampleConstOffset')),
    ('k7b_indirect', IMG, sub('const auto m_offset = m_t306_offset ? MSampleConstOffset',
                              'const auto m_offset = (m_t306_offset && (image.indirect_resources.size() < 2u || resource == image.indirect_resources[0])) ? MSampleConstOffset')),
]


def halt():
    return os.path.exists(LOCK) or os.path.exists(STOP)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def build(tag):
    with open('%s/mut/build_%s.log' % (HERE, tag), 'wb') as f:
        return subprocess.run(['cmd', '/c', HERE.replace('/', BS) + BS + 'build_m7b.cmd', 'tests'], stdout=f,
                              stderr=subprocess.STDOUT, creationflags=IDLE).returncode


def clean_env():
    return {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}


def run_tests(tag, knob):
    env = clean_env()
    env.update({'KYTY_TESTS_CONTINUE': '1', 'KYTY_TESTS_VERBOSE': '1', 'KYTY_TESTS_FILTER': 'MWave1T306',
                'KYTY_TEST_T306_EBOOT': EBOOT})
    if knob == '1':
        env['KYTY_M_T306'] = '1'
    out = '%s/mut/run_%s_%s.txt' % (HERE, tag, knob)
    with open(out, 'wb') as f:
        rc = subprocess.run([EXE], stdout=f, stderr=subprocess.STDOUT, cwd=HERE + '/build', env=env, timeout=300,
                            creationflags=IDLE).returncode
    text = open(out, 'rb').read().decode('utf-8', 'replace')
    return rc, [l.strip()[:110] for l in text.split(NL) if 'failed' in l.lower()]


EXPECT_T2 = ([(0x1a4, 1, 1)] * 2 + [(0x1b0, 1, 0)] * 2 + [(0x1b8, 0, 1)] * 2, (0, 0, 0))


def run_recompile(tag):
    env = clean_env()
    os.makedirs('%s/mut/cs_%s' % (HERE, tag), exist_ok=True)
    env.update({'KYTY_M_T306': '1', 'KYTY_RECOMPILE_T306': '1',
                'KYTY_RECOMPILE': '%s;%s;%s/mut/cs_%s/out.spv;0' % (CS_GCN, CS_CACHE, HERE, tag)})
    p = subprocess.run([EXE], capture_output=True, cwd='%s/mut/cs_%s' % (HERE, tag), env=env, timeout=300,
                       creationflags=IDLE)
    text = (p.stdout + p.stderr).decode('utf-8', 'replace')
    open('%s/mut/cs_%s/log.txt' % (HERE, tag), 'w', encoding='utf-8').write(text)
    recs = sorted((int(m[0], 16), int(m[1]), int(m[2])) for m in
                  re.findall(r'recompile-t306: hash=\w+ pc=0x(\w+) x=(-?\d+) y=(-?\d+)', text))
    fal = re.findall(r'recompile-t306-fallback: nonconstant=(\d+) cube=(\d+) range=(\d+)', text)
    fal = tuple(int(x) for x in fal[0]) if fal else None
    return p.returncode, recs, fal


def main():
    only = None
    if '--only' in sys.argv:
        only = sys.argv[sys.argv.index('--only') + 1].split(',')
    os.makedirs(HERE + '/mut', exist_ok=True)
    out = open(HERE + '/mut_m7b.out.txt', 'a', encoding='utf-8')

    def say(s):
        print(s)
        out.write(s + NL)
        out.flush()
    if halt():
        say('LOCK or STOP - exit 3')
        return 3
    base_sha = sha(EXE)
    say('exe before mutants ' + base_sha)
    for name, rel, fn in MUTANTS:
        if only and name not in only:
            continue
        if halt():
            say('STOPPED before ' + name)
            return 3
        path = WT + '/' + rel
        orig = open(path, 'rb').read()
        assert b'\r' not in orig
        text = orig.decode('utf-8')
        new = fn(text)
        assert new != text
        open(path, 'wb').write(new.encode('utf-8'))
        try:
            brc = build(name)
            if brc != 0:
                say('%-15s BUILD FAILED rc %d' % (name, brc))
                continue
            r1 = run_tests(name, '1')
            r0 = run_tests(name, '0')
            t2 = run_recompile(name)
        finally:
            open(path, 'wb').write(orig)
        by_test = r1[0] != 0 or bool(r1[1]) or r0[0] != 0 or bool(r0[1])
        by_t2 = (t2[1], t2[2]) != EXPECT_T2 or t2[0] != 0
        say('%-15s test:%s recompile:%s | =1 rc %s %s | =0 rc %s %s | T2 rc %s records %d fallback %s' % (
            name, 'CAUGHT' if by_test else 'not-caught', 'CAUGHT' if by_t2 else 'not-caught',
            r1[0], r1[1][:3], r0[0], r0[1][:2], t2[0], len(t2[1]), t2[2]))
    if only and only != ['control']:
        say('ONLY run - no control')
        return 0
    brc = build('control')
    r1 = run_tests('control', '1')
    r0 = run_tests('control', '0')
    t2 = run_recompile('control')
    after = sha(EXE)
    ok = brc == 0 and r1[0] == 0 and not r1[1] and r0[0] == 0 and not r0[1] and (t2[1], t2[2]) == EXPECT_T2
    say('CONTROL restored tree: build rc %d, =1 rc %s failed %d, =0 rc %s failed %d, T2 records %d fallback %s -> %s'
        % (brc, r1[0], len(r1[1]), r0[0], len(r0[1]), len(t2[1]), t2[2], 'PASS' if ok else 'FAIL'))
    say('exe after control %s (same as before: %s)' % (after, after == base_sha))
    say('ALL DONE')
    return 0


if __name__ == '__main__':
    sys.exit(main())

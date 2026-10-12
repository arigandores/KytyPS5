"""M2c (HPP-840): run Red Team's mutants of mut_m2c.py (one build, M2C_MUT=<name>) - task member (3).
For each mutant: the tests of its theme at KYTY_M_<theme>=1, every other KYTY_* removed, one process per case, IDLE
priority (item 760(b)(4)); the control row runs the same tests with M2C_MUT unset and must pass.
  translator: shader_recompiler_compute_tests --m-wave1-case <MW1T...> of the theme (GPU, small dispatches; case 224 is
              not among them) and shader_cfg_tests with KYTY_TESTS_FILTER=MWave1 (CPU);
  HLE:        m_wave1_hle_stand through docs/track-m/m2b/run_stand_m2b.py --only <arm> --knob 1.
Caught = at least one test of the theme fails with the mutant while the control passes.
Usage: python run_mut_m2c.py <out dir>. Prints a table; last line ALL OK (every mutant caught, every control passes)
or FAIL with the members."""
import os
import re
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
BIN = 'C:/kyty/m657/m2c2/bin/'  # M2c2 (HPP-844): only this line differs from m2c/run_mut_m2c.py
COMPUTE = BIN + 'mutall_compute.exe'
CFG = BIN + 'mutall_cfg.exe'
STAND = BIN + 'mutall_stand.exe'
STAND_DRIVER = 'C:/kyty/KytyPS5/docs/track-m/m2b/run_stand_m2b.py'
IDLE = 0x40
MUTANTS = [('t234_tie', 'T234'), ('t234_snan', 'T234'), ('t233_thr', 'T233'), ('t306_mask', 'T306'),
           ('t032_2bit', 'T032'), ('t203_zero', 'T203'), ('t256_u', 'T256'),
           ('t265_size', 'T265'), ('t265_path', 'T265'), ('t272_swap', 'T272'), ('t231_lim', 'T231')]
HLE_ARM = {'T265': 't265', 'T272': 't272', 'T231': 't231'}


def guard():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        sys.exit(3)


def run(args, extra, log, cwd):
    guard()
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_') and k != 'M2C_MUT'}
    env.update(extra)
    try:
        p = subprocess.run(args, capture_output=True, timeout=300, env=env, cwd=cwd, creationflags=IDLE)
        rc, out = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out = 'timeout', (e.stdout or b'') + (e.stderr or b'')
    open(log, 'wb').write(out)
    text = out.decode('utf-8', 'replace')
    if 'DeviceLost' in text:
        print('DEVICE LOST in', log, '- stop (item 760(b)(2))')
        sys.exit(6)
    return rc, text


def mw1_cases(out):
    rc, text = run([COMPUTE, '--m-wave1-list'], {}, out + '/list.txt', os.path.dirname(COMPUTE))
    return [l.strip() for l in text.split('\n') if l.strip().startswith('MW1')]


def theme_tests(theme, mut, out, cases):
    """[(test, passed)] of the theme with M2C_MUT=mut ('' = control)."""
    extra = {'KYTY_M_' + theme: '1'}
    if mut:
        extra['M2C_MUT'] = mut
    tag = mut or 'control'
    res = []
    if theme in HLE_ARM:
        arm = HLE_ARM[theme]
        d = '%s/%s_%s' % (out, tag, arm)
        rc, text = run([sys.executable, STAND_DRIVER, STAND, d, '--only', arm, '--knob', '1'], extra if mut else {},
                       '%s/%s_%s.txt' % (out, tag, arm), os.path.dirname(STAND))
        res.append(('stand:' + arm, rc == 0 and text.rstrip().endswith('ALL OK')))
        return res
    for name in [c for c in cases if c.startswith('MW1' + theme)]:
        rc, text = run([COMPUTE, '--m-wave1-case', name], extra, '%s/%s_%s.txt' % (out, tag, name),
                       os.path.dirname(COMPUTE))
        res.append((name, rc == 0 and 'ALL OK' in text))
    rc, text = run([CFG], dict(extra, KYTY_TESTS_FILTER='MWave1', KYTY_TESTS_CONTINUE='1', KYTY_TESTS_VERBOSE='1'),
                   '%s/%s_cfg_%s.txt' % (out, tag, theme), os.path.dirname(CFG))
    # KYTY_TESTS_CONTINUE=1 keeps rc 0 on a failed Check - the failure is the line 'ShaderCfgTests: failed'.
    res.append(('cfg:MWave1', rc == 0 and 'ShaderCfgTests: failed' not in text))
    return res


def main():
    out = sys.argv[1]
    only = sys.argv[2].split(',') if len(sys.argv) > 2 else None  # themes to run (the rest: earlier run)
    os.makedirs(out, exist_ok=True)
    cases = mw1_cases(out)
    print('MW1 cases', len(cases))
    ok = True
    controls = {}
    for theme in sorted({t for _, t in MUTANTS if only is None or t in only}):
        r = theme_tests(theme, '', out, cases)
        good = all(p for _, p in r)
        controls[theme] = good
        ok &= good
        print('control\t%s\t%d tests\t%s' % (theme, len(r), 'PASS' if good else 'FAIL ' + str([n for n, p in r if not p])))
    for mut, theme in [m for m in MUTANTS if only is None or m[1] in only]:
        r = theme_tests(theme, mut, out, cases)
        failed = [n for n, p in r if not p]
        caught = len(failed) > 0
        ok &= caught
        print('%s\t%s\t%d tests\t%s\t%s' % (mut, theme, len(r), 'CAUGHT' if caught else 'NOT CAUGHT',
                                          ','.join(failed)[:300]))
    print('ALL OK' if ok else 'FAIL')


main()

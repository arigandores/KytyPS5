"""M2c (HPP-840, ROADMAP s122 item 758(e)): full shader_recompiler_compute_tests (no selector) on the main build
(m2c/bin/compute_main.exe, worktree 666a434a) at the knob settings
  z     every KYTY_* removed (all wave 1 knobs off)
  ms1   KYTY_M_T234/T233/T306/T032/T203 = 1 (mask 0x3b, without T256)
  all   the six KYTY_M_<theme> = 1 (mask 0x3f)
each in its own process, cwd = the exe folder. Member: rc 0 and the last line
"ShaderRecompilerComputeTests: all cases passed". Lock and STOP before every process.
Usage: python run_full.py <exe> <out dir> [config ...]. Prints ALL OK / FAIL."""
import hashlib
import os
import subprocess
import sys
import time

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
CONFIGS = {
    'z': {},
    'ms1': {'KYTY_M_T234': '1', 'KYTY_M_T233': '1', 'KYTY_M_T306': '1', 'KYTY_M_T032': '1', 'KYTY_M_T203': '1'},
    'all': {'KYTY_M_T234': '1', 'KYTY_M_T233': '1', 'KYTY_M_T256': '1', 'KYTY_M_T306': '1', 'KYTY_M_T032': '1',
            'KYTY_M_T203': '1'},
}
PASS_LINE = 'ShaderRecompilerComputeTests: all cases passed'


def main():
    exe = os.path.abspath(sys.argv[1])
    out = sys.argv[2]
    names = sys.argv[3:] or list(CONFIGS)
    os.makedirs(out, exist_ok=True)
    print('exe', exe, hashlib.sha256(open(exe, 'rb').read()).hexdigest())
    ok = True
    for name in names:
        if os.path.exists(LOCK) or os.path.exists(STOP):
            print('LOCK or STOP')
            sys.exit(3)
        env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
        env.update(CONFIGS[name])
        t0 = time.time()
        try:
            p = subprocess.run([exe], capture_output=True, timeout=3000, env=env, cwd=os.path.dirname(exe))
            rc, text = p.returncode, (p.stdout + p.stderr)
        except subprocess.TimeoutExpired as e:
            rc, text = 'timeout', (e.stdout or b'') + (e.stderr or b'')
        open(os.path.join(out, name + '.log'), 'wb').write(text)
        s = text.decode('utf-8', 'replace')
        lines = [l for l in s.replace('\r', '').split('\n') if l.strip()]
        last = lines[-1] if lines else ''
        good = rc == 0 and PASS_LINE in s
        ok &= good
        fail = [l for l in lines if 'FAIL' in l or 'mismatch' in l][:3]
        print('%-4s rc=%s %.1fs lines=%d %s last=%s' % (name, rc, time.time() - t0, len(lines), 'PASS' if good else 'FAIL',
                                                       last[:140]))
        for l in fail:
            print('     ', l[:200])
    print('ALL OK' if ok else 'FAIL')


main()

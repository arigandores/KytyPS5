"""M2a (HPP-838, ROADMAP s122 item 756(g)(1)): shader_cfg_tests run without the game, form of FS15a run_tests_fs15a.py:
KYTY_TESTS_CONTINUE=1, KYTY_TESTS_VERBOSE=1, KYTY_TESTS_SPV_DIR, all other KYTY_* removed, plus the extra KYTY_* given as
NAME=VALUE arguments. Writes <out>/log.txt, rc.txt, exe_sha256.txt, spv/, failed.txt (sorted set of failed test names:
the lines "ShaderCfgTests: failed: <name>" and "[FAIL] <name>" style lines - every line containing the word "failed"
is kept verbatim in failed_lines.txt).
Usage: python run_tests_m2.py <exe> <out dir> [NAME=VALUE ...]. Lock and STOP checked before the process (exit 3)."""
import hashlib
import os
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    exe, o = sys.argv[1], os.path.abspath(sys.argv[2]).replace(os.sep, '/')
    extra = dict(a.split('=', 1) for a in sys.argv[3:])
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        return 3
    os.makedirs(o + '/spv', exist_ok=True)
    for f in os.listdir(o + '/spv'):
        os.remove(o + '/spv/' + f)
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env['KYTY_TESTS_CONTINUE'] = '1'
    env['KYTY_TESTS_VERBOSE'] = '1'
    env['KYTY_TESTS_SPV_DIR'] = o + '/spv'
    env.update(extra)
    with open(o + '/log.txt', 'wb') as f:
        rc = subprocess.run([exe], stdout=f, stderr=subprocess.STDOUT, cwd=os.path.dirname(exe), env=env,
                            timeout=580).returncode
    open(o + '/rc.txt', 'w', newline='\n').write('%d\n' % rc)
    open(o + '/exe_sha256.txt', 'w', newline='\n').write(sha(exe) + '\n')
    text = open(o + '/log.txt', 'rb').read().decode('utf-8', 'replace')
    lines = [l.strip() for l in text.split('\n')]
    fl = [l for l in lines if 'failed' in l]
    open(o + '/failed_lines.txt', 'w', newline='\n').write('\n'.join(fl) + '\n')
    names = sorted({l.split('ShaderCfgTests: failed:', 1)[1].strip() for l in lines if 'ShaderCfgTests: failed:' in l})
    open(o + '/failed.txt', 'w', newline='\n').write('\n'.join(names) + ('\n' if names else ''))
    print('rc', rc, '[test] lines', text.count('[test] '), 'failed names', len(names), 'failed lines', len(fl),
          'spv', len(os.listdir(o + '/spv')))
    return 0


if __name__ == '__main__':
    sys.exit(main())

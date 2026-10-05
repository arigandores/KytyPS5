"""S16d (HPP-608): the shader_cfg_tests suite of a probe binary (clean KYTY_ environment, KYTY_TESTS_CONTINUE=1). Usage: python suite_s16d.py <A|B>"""
import os, subprocess, sys
arm = sys.argv[1]
env = {k: v for k, v in os.environ.items() if not k.upper().startswith('KYTY_')}
env.update(KYTY_TESTS_CONTINUE='1', KYTY_TESTS_VERBOSE='1')
exe = 'C:/kyty/s288/s16d/build%s/shader_cfg_tests.exe' % arm
out = open('C:/kyty/s288/s16d/suite_%s.log' % arm, 'wb')
rc = subprocess.run([exe], cwd='C:/kyty/s288/s16d/build%s' % arm, env=env, stdout=out, stderr=subprocess.STDOUT).returncode
out.close()
print('suite', arm, 'rc', rc)
sys.exit(rc)

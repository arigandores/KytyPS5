"""M8b (HPP-859): run build_m8b.cmd <args> at IDLE priority via lowrun.py; usage python bld.py <log> <args...>."""
import subprocess, sys
BS = chr(92)
cmd = 'C:' + BS + 'kyty' + BS + 'm657' + BS + 'm8b' + BS + 'build_m8b.cmd ' + ' '.join(sys.argv[2:])
with open(sys.argv[1], 'wb') as f:
    rc = subprocess.call(['python', 'C:/kyty/m657/m8b/lowrun.py', 'cmd', '/c', cmd], stdout=f, stderr=subprocess.STDOUT)
print('rc', rc)
sys.exit(rc)

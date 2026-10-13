"""M8c (HPP-860): run C:/kyty/m657/m8c/<cmd file> <args> at IDLE priority via lowrun.py (form of m8b bld.py).
Usage: python bld_m8c.py <cmd file name> <log> <args...>"""
import subprocess, sys
BS = chr(92)
cmd = 'C:' + BS + 'kyty' + BS + 'm657' + BS + 'm8c' + BS + sys.argv[1] + ' ' + ' '.join(sys.argv[3:])
with open(sys.argv[2], 'wb') as f:
    rc = subprocess.call(['python', 'C:/kyty/m657/m8c/lowrun.py', 'cmd', '/c', cmd], stdout=f, stderr=subprocess.STDOUT)
print('rc', rc)
sys.exit(rc)

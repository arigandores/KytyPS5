import subprocess
import sys
sys.exit(subprocess.run(["cmd", "/c", "C:/kyty/s288/s17a/build_s17a.cmd".replace("/", chr(92))] + sys.argv[1:]).returncode)

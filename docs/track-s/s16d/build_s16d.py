"""S16d (HPP-608): build_s16d.cmd through cmd /c without MSYS argument conversion. Usage: python build_s16d.py <A|B> <configure|tests>"""
import subprocess
import sys
sys.exit(subprocess.run(['cmd', '/c', 'C:/kyty/s288/s16d/build_s16d.cmd'.replace('/', chr(92))] + sys.argv[1:]).returncode)

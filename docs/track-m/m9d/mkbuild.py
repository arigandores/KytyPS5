import os, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
s = open('C:/kyty/m657/m6a/build_m6a.cmd', encoding='utf-8').read()
s = s.replace('C:\\kyty\\m657\\m6a\\wt', 'C:\\kyty\\m657\\m9d\\wt').replace('C:\\kyty\\m657\\m6a\\build', 'C:\\kyty\\m657\\m9d\\build')
s = 'rem M9d (HPP-869): copy of m657\\m6a\\build_m6a.cmd with SRC/BUILD set to m657\\m9d. Was:\n' + s
open('C:/kyty/m657/m9d/build_m9d.cmd', 'w', newline='\r\n', encoding='utf-8').write(s.replace('\r\n', '\n'))
print([l for l in s.split('\n') if 'set "SRC' in l or 'set "BUILD' in l])

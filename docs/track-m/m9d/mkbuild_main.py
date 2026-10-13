import os, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
s = open('C:/kyty/m657/m9d/build_m9d.cmd', encoding='utf-8').read()
s = s.replace('C:\\kyty\\m657\\m9d\\wt"', 'C:\\kyty\\m657\\m9d\\wtmain"').replace('C:\\kyty\\m657\\m9d\\build"', 'C:\\kyty\\m657\\m9d\\buildmain"')
s = 'rem M9d (HPP-869): build_m9d.cmd with SRC/BUILD set to m9d\\wtmain / m9d\\buildmain (compile check of main). Was:\n' + s
open('C:/kyty/m657/m9d/build_m9d_main.cmd', 'w', newline='\r\n', encoding='utf-8').write(s.replace('\r\n', '\n'))
print([l for l in s.split('\n') if 'set "SRC' in l or 'set "BUILD' in l])

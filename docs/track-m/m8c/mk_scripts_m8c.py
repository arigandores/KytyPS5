"""M8c (HPP-860): make mk_wt_m8c.sh, build_m8c.cmd, build_m8c_main.cmd, lowrun.py from the M8a copies (paths only)."""
import shutil

BS = chr(92)
D = 'C:/kyty/KytyPS5/docs/track-m/m8a/'
O = 'C:/kyty/m657/m8c/'
src = open(D + 'mk_wt_m8a.sh', encoding='utf-8').read()
a = 'WT=${1:-C:/kyty/m657/m8a/wt}'
b = 'C=${2:-ed94b13d}'
assert src.count(a) == 1 and src.count(b) == 1
src = src.replace(a, 'WT=${1:-C:/kyty/m657/m8c/wt}').replace(b, 'C=${2:-3d227024}')
hdr = '# M8c (HPP-860, ROADMAP s122 item 778(d)): copy of m657/m8a mk_wt_m8a.sh, default dir m8c/wt, base M6a3 3d227024. Was:' + chr(10)
open(O + 'mk_wt_m8c.sh', 'wb').write((hdr + src).encode('utf-8'))
t = open(D + 'build_m8a.cmd', encoding='utf-8').read()
old_s = 'm657' + BS + 'm8a' + BS + 'wt"'
old_b = 'm657' + BS + 'm8a' + BS + 'build"'
assert t.count(old_s) == 1 and t.count(old_b) == 1
for name, s, b in (('build_m8c.cmd', 'wt', 'build'), ('build_m8c_main.cmd', 'wtmain', 'buildmain')):
    u = t.replace(old_s, 'm657' + BS + 'm8c' + BS + s + '"').replace(old_b, 'm657' + BS + 'm8c' + BS + b + '"')
    u = ('rem M8c (HPP-860): copy of m657' + BS + 'm8a' + BS + 'build_m8a.cmd with SRC/BUILD set to m657' + BS + 'm8c' + BS +
         s + ', ' + b + '. Was:' + chr(13) + chr(10) + u)
    open(O + name, 'wb').write(u.encode('utf-8'))
shutil.copy(D + 'lowrun.py', O + 'lowrun.py')
print('OK')

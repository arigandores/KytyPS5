"""M2d: build_m2d.cmd = build_m2c.cmd with SRC/BUILD set to m657\\m2d (CRLF kept as in the source)."""
BS = chr(92)
s = open('C:/kyty/m657/m2c/build_m2c.cmd', 'rb').read().decode()
old_src = 'C:' + BS + 'kyty' + BS + 'm657' + BS + 'm2c' + BS + 'wt'
old_bld = 'C:' + BS + 'kyty' + BS + 'm657' + BS + 'm2c' + BS + 'build'
assert s.count(old_src) == 1 and s.count(old_bld + '"') == 1, (s.count(old_src), s.count(old_bld))
s = s.replace(old_src, old_src.replace('m2c', 'm2d')).replace(old_bld + '"', old_bld.replace('m2c', 'm2d') + '"')
hdr = 'rem M2d (HPP-841): copy of m657' + BS + 'm2c' + BS + 'build_m2c.cmd with SRC/BUILD set to m657' + BS + 'm2d. Was:' + chr(13) + chr(10)
open('C:/kyty/m657/m2d/build_m2d.cmd', 'wb').write((hdr + s).encode())
print('OK')

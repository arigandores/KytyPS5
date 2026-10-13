"""M8b (HPP-859): make build_m8b.cmd point at m657\\m8b (copy of build_m8a.cmd)."""
BS = chr(92)
p = 'C:/kyty/m657/m8b/build_m8b.cmd'
t = open(p, 'rb').read().decode()
t = t.replace('m657' + BS + 'm8a', 'm657' + BS + 'm8b')
if not t.startswith('rem M8b'):
    t = ('rem M8b (HPP-859): copy of m657' + BS + 'm8a' + BS + 'build_m8a.cmd with SRC/BUILD set to m657' + BS +
         'm8b. Was:' + chr(13) + chr(10)) + t
open(p, 'wb').write(t.encode())

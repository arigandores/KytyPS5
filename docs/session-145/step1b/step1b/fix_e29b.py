"""Link 1b of s145: repair of the line of E29b broken by the shell hook (a CR LF literal turned into real line ends)."""
p = 'C:/kyty/s145/test_sc145.py'
s = open(p, 'rb').read().decode('utf-8')
bad = "EX4I.write_bytes(('\r\n'.join(out4i) + '\r\n').encode('ascii'))\n"
bad2 = "EX4I.write_bytes(('\n'.join(out4i) + '\n').encode('ascii'))\n"
good = "EX4I.write_bytes(('\\r\\n'.join(out4i) + '\\r\\n').encode('ascii'))\n"
n = s.count(bad) + s.count(bad2)
assert n == 1, n
s = s.replace(bad, good).replace(bad2, good)
assert '\r' not in s
open(p, 'wb').write(s.encode('ascii'))
print('fixed')

# FS5b (HPP-510, Red Team): port my FS4b compare scripts (bincmp, fullcmp, residual) to FS5: A = own build of 0e72bc19
# (fs5/fs5b), B = the FS5a copy 631ff987; paths fs4/fs4b -> fs5/fs5b, fs4/fs4a -> fs5/fs5a; translation signature
# 56189185... -> 26ce5fc7...; SDL strings: A ...-1876-g0e72bc19, B ...-1875-g8a56dc2a. Every replacement is counted. LF output.
import io
S = 'C:/kyty/KytyPS5/docs/track-f/fs4b/'
D = 'C:/kyty/f287/fs5/fs5b/'
BS = chr(92)
R = [
    ('fs4/fs4b', 'fs5/fs5b'),
    ('fs4/fs4a', 'fs5/fs5a'),
    ("b'fs4' + BS + b'fs4b'", "b'fs5' + BS + b'fs5b'"),
    ("b'fs4' + BS + b'fs4a'", "b'fs5' + BS + b'fs5a'"),
    ('31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5', '631ff98723f08112755137fdb12b993aa94d3169fb872affd96c7a3c6eaa9c17'),
    ('kyty_emulator_31cbfee8.exe', 'kyty_emulator_631ff987.exe'),
    ('56189185f9e9f9a0ea5174f3f85206e6d099db3d', '26ce5fc78ea3b20be537c7696be041f5e97d9e58'),
    ('56189185f9e9...', '26ce5fc78ea3...'),
    ('SDL-KytyPS5-2026-09-15-6a2987a-1874-g3d0e46da', 'SDL-KytyPS5-2026-09-15-6a2987a-1876-g0e72bc19'),
    ('SDL-KytyPS5-2026-09-15-6a2987a-1873-g92d11340', 'SDL-KytyPS5-2026-09-15-6a2987a-1875-g8a56dc2a'),
]
for name in ('bincmp', 'fullcmp', 'residual'):
    t = io.open(S + name + '_fs4b.py', encoding='utf-8', newline='').read().replace('\r\n', '\n')
    cnt = []
    for a, b in R:
        cnt.append(t.count(a))
        t = t.replace(a, b)
    t = '# FS5b (HPP-510, Red Team): port of my FS4b %s_fs4b.py by mk_cmp_fs5b.py (A = own 0e72bc19, B = 631ff987). Was:\n' % name + t
    open(D + name + '_fs5b.py', 'wb').write(t.encode('utf-8'))
    print(name, 'replacements', cnt)
print('ALL OK')

"""FS13a (HPP-787, ROADMAP s122 item 697(g)(1)): KYTY_FIX_F25 default 0 -> 1 in src/kernel/fileSystem.cpp, the form of
FS12a cbfe8375 / FS11a cb022252 and of FixB4Enabled in the same file (unset or "" = ON, otherwise Common::EnvValueOn);
one reading (static const, first call - FileSystem::Initialize) kept; the line "FixF25: mode=<0|1>" unchanged.
Anchors are whole lines; CRLF-safe (strips CR before the search, restores it); writes bytes.
Usage: python patch_fs13a.py <repo root>"""
import sys

root = sys.argv[1]
path = root + '/src/kernel/fileSystem.cpp'
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
text = raw.decode('utf-8').replace('\r\n', '\n')
lines = text.split('\n')

OLD_HEAD = ('// Track F, F38a (HPP-763, ROADMAP s122 item 691(v)-(g), row F25): KYTY_FIX_F25 (default 0: unset, "", '
            '0/false/off/no =')
NEW_HEAD = ('// Track F, F38a (HPP-763, ROADMAP s122 item 691(v)-(g), row F25): KYTY_FIX_F25 (default 1 - FS13a below; '
            '0/false/off/no =')
OLD_FN = ['static bool FixF25Enabled() {',
          '\tstatic const bool enabled = Common::EnvFlagOn("KYTY_FIX_F25");',
          '\treturn enabled;',
          '}']
NEW_FN = ['// Track F, FS13a (HPP-787, ROADMAP s122 item 697(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any other',
          '// value as EnvValueOn (the form of FS12a cbfe8375 / FS11a cb022252).',
          'static bool FixF25Enabled() {',
          '\tstatic const bool enabled = [] {',
          '\t\tconst char* value = std::getenv("KYTY_FIX_F25");',
          '\t\treturn value == nullptr || value[0] == \'\\0\' || Common::EnvValueOn(value);',
          '\t}();',
          '\treturn enabled;',
          '}']

idx = [i for i, l in enumerate(lines) if l == OLD_HEAD]
assert len(idx) == 1, ('head', idx)
lines[idx[0]] = NEW_HEAD
fn = [i for i in range(len(lines) - 3) if lines[i:i + 4] == OLD_FN]
assert len(fn) == 1, ('fn', fn)
lines[fn[0]:fn[0] + 4] = NEW_FN
assert sum(1 for l in lines if 'Common::EnvFlagOn("KYTY_FIX_F25")' in l) == 0
assert sum(1 for l in lines if 'getenv("KYTY_FIX_F25")' in l) == 1
out = '\n'.join(lines)
if crlf:
    out = out.replace('\n', '\r\n')
open(path, 'wb').write(out.encode('utf-8'))
print('patched %s (head line %d, function line %d, crlf %s)' % (path, idx[0] + 1, fn[0] + 1, crlf))
print('PATCH OK')

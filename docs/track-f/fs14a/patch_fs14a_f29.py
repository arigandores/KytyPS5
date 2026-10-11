"""FS14a (HPP-812, ROADMAP s122 item 712(g)(1)): KYTY_FIX_F29 default 0 -> 1 in FixF29Enabled
(src/graphics/host_gpu/renderer/cache/faultManager.cpp), the form of FS13a 3630f116 (unset or "" = ON, otherwise
Common::EnvValueOn); one reading per process (static const) kept; the line "FixF29: mode=<0|1>" (FaultManager
constructor) unchanged - printed by value. The header comment of faultManager.h that says "default 0" is updated.
Anchors are whole lines; CRLF-safe (strips CR before the search, restores it); writes bytes.
Usage: python patch_fs14a_f29.py <repo root>"""
import sys

root = sys.argv[1]


def patch(rel, repl):
    path = root + '/' + rel
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    lines = raw.decode('utf-8').replace('\r\n', '\n').split('\n')
    for old, new in repl:
        idx = [i for i in range(len(lines) - len(old) + 1) if lines[i:i + len(old)] == old]
        assert len(idx) == 1, (rel, old[0], idx)
        lines[idx[0]:idx[0] + len(old)] = new
        print('%s: line %d, %d -> %d lines' % (rel, idx[0] + 1, len(old), len(new)))
    out = '\n'.join(lines)
    if crlf:
        out = out.replace('\n', '\r\n')
    open(path, 'wb').write(out.encode('utf-8'))
    return out


CPP = 'src/graphics/host_gpu/renderer/cache/faultManager.cpp'
H = 'src/graphics/host_gpu/renderer/cache/faultManager.h'

out = patch(CPP, [(
    ['bool FixF29Enabled() {',
     '\tstatic const bool enabled = Common::EnvValueOn(std::getenv("KYTY_FIX_F29"));',
     '\treturn enabled;',
     '}'],
    ['// Track F, FS14a (HPP-812, ROADMAP s122 item 712(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any',
     '// other value as EnvValueOn (the form of FS13a 3630f116); still one reading per process.',
     'bool FixF29Enabled() {',
     '\tstatic const bool enabled = [] {',
     '\t\tconst char* value = std::getenv("KYTY_FIX_F29");',
     '\t\treturn value == nullptr || value[0] == \'\\0\' || Common::EnvValueOn(value);',
     '\t}();',
     '\treturn enabled;',
     '}'])])
assert out.count('getenv("KYTY_FIX_F29")') == 1
assert out.count('FixF29: mode=') == 1

out = patch(H, [(
    ['// KYTY_FIX_F29 (default 0): the value is read once per process (EnvValueOn: unset/""/0/false/off/no - off).'],
    ['// KYTY_FIX_F29 (default 1 since FS14a, HPP-812, ROADMAP s122 item 712(g)(1)): the value is read once per process',
     '// (unset or "" - on; 0/false/off/no - off; any other value as EnvValueOn).'])])
assert 'default 0' not in out
print('PATCH OK')

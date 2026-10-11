"""FS15a (HPP-820, ROADMAP s122 item 730(g)(1)): KYTY_FIX_F20 default 0 -> 1 in FixF20::Mode
(src/graphics/host_gpu/renderer/pipeline/fixF20.cpp), the form of FS14a c8836f14 / FS13a 3630f116 (unset or "" = ON,
otherwise Common::EnvValueOn); one reading per process (static const) kept; the line "FixF20: mode=<0|1>" unchanged -
printed by value. The header comment of fixF20.h that says "default 0" is updated.
Anchors are whole lines; CRLF-safe (strips CR before the search, restores it); writes bytes.
Usage: python patch_fs15a.py <repo root>"""
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


CPP = 'src/graphics/host_gpu/renderer/pipeline/fixF20.cpp'
H = 'src/graphics/host_gpu/renderer/pipeline/fixF20.h'

out = patch(CPP, [(
    ['int Mode() {',
     '\tstatic const int mode = [] {',
     '\t\tconst int value = Common::EnvFlagOn("KYTY_FIX_F20") ? 1 : 0;',
     '\t\tLOGF("FixF20: mode=%d\\n", value);',
     '\t\treturn value;',
     '\t}();',
     '\treturn mode;',
     '}'],
    ['// Track F, FS15a (HPP-820, ROADMAP s122 item 730(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any',
     '// other value as EnvValueOn (the form of FS14a c8836f14 / FS13a 3630f116); still one reading per process.',
     'int Mode() {',
     '\tstatic const int mode = [] {',
     '\t\tconst char* env = std::getenv("KYTY_FIX_F20");',
     '\t\tconst int value = (env == nullptr || env[0] == \'\\0\' || Common::EnvValueOn(env)) ? 1 : 0;',
     '\t\tLOGF("FixF20: mode=%d\\n", value);',
     '\t\treturn value;',
     '\t}();',
     '\treturn mode;',
     '}'])])
assert out.count('getenv("KYTY_FIX_F20")') == 1
assert out.count('EnvFlagOn("KYTY_FIX_F20")') == 0
assert out.count('"FixF20: mode=%d') == 1
assert out.count('"FixF20Stat: when=%s') == 1

out = patch(H, [(
    ['// KYTY_FIX_F20 (default 0): read once per process (Common::EnvFlagOn - unset, "", 0/false/off/no = 0, any other',
     '// value = 1); the first call prints "FixF20: mode=<0|1>". At 0 the callers never call Apply.'],
    ['// KYTY_FIX_F20 (default 1 since FS15a, HPP-820, ROADMAP s122 item 730(g)(1)): read once per process (unset or "" - 1;',
     '// 0/false/off/no - 0; any other value as EnvValueOn); the first call prints "FixF20: mode=<0|1>". At 0 the callers',
     '// never call Apply.'])])
assert 'default 0' not in out
print('PATCH OK')

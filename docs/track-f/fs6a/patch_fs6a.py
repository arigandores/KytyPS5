# FS6a (HPP-555, ROADMAP s122 item 454(g)(1)): KYTY_FIX_B4 default 0 -> 1 in the form of FS4a 17adaf80 (unset or "" = ON,
# otherwise Common::EnvValueOn); one reading (static const bool) kept; the line "FixB4: mode=", the =1 / else branches and
# Shutdown() unchanged. Also the header comment of the stand tests/B4RaceStand.cpp (unset now selects the default, ON).
# Usage: python patch_fs6a.py <repo root>. Whole-line anchors; CR stripped before the search and restored; LF writes.
import sys

root = sys.argv[1].rstrip('/\\')

EDITS = {
    'src/kernel/fileSystem.cpp': [
        (
            [
                '// Track F, F15c (ROADMAP s122 items 412(v), 417(b)-(v), row B4): KYTY_FIX_B4 (default 0), read once. At 1 the',
            ],
            [
                '// Track F, F15c (ROADMAP s122 items 412(v), 417(b)-(v), row B4): KYTY_FIX_B4 (default ON since FS6a, item 454(g)(1):',
                '// unset or "" = ON, 0/false/off/no = OFF; read once). At 1 the',
            ],
        ),
        (
            [
                '// use-after-free). The OS closes the host descriptors at the end of the process. Unset or empty - OFF.',
                'static bool FixB4Enabled() {',
                '\tstatic const bool enabled = Common::EnvValueOn(std::getenv("KYTY_FIX_B4"));',
                '\treturn enabled;',
                '}',
            ],
            [
                '// use-after-free). The OS closes the host descriptors at the end of the process.',
                'static bool FixB4Enabled() {',
                '\t// Track F, FS6a (HPP-555, ROADMAP s122 item 454(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any',
                '\t// other value as EnvValueOn (the form of FS4a 17adaf80).',
                '\tstatic const bool enabled = [] {',
                '\t\tconst char* value = std::getenv("KYTY_FIX_B4");',
                '\t\treturn value == nullptr || value[0] == \'\\0\' || Common::EnvValueOn(value);',
                '\t}();',
                '\treturn enabled;',
                '}',
            ],
        ),
    ],
    'tests/B4RaceStand.cpp': [
        (
            [
                '// KYTY_FIX_B4 (read by fileSystem.cpp) selects the code under test: unset/0 - CloseAll, 1 - the B4 fix.',
            ],
            [
                '// KYTY_FIX_B4 (read by fileSystem.cpp) selects the code under test: 0 - CloseAll, 1 - the B4 fix; unset or "" - the',
                '// default of fileSystem.cpp (1 since FS6a, ROADMAP s122 item 454(g)(1)).',
            ],
        ),
    ],
}

ok = True
for rel, edits in EDITS.items():
    path = root + '/' + rel
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    lines = raw.decode('utf-8').replace('\r\n', '\n').split('\n')
    for old, new in edits:
        hits = [i for i in range(len(lines) - len(old) + 1) if lines[i:i + len(old)] == old]
        if len(hits) != 1:
            print('ANCHOR FAIL', rel, len(hits), old[0][:80])
            ok = False
            continue
        i = hits[0]
        lines[i:i + len(old)] = new
        print('patched', rel, 'line', i + 1, '-%d +%d' % (len(old), len(new)))
    text = '\n'.join(lines)
    if crlf:
        text = text.replace('\n', '\r\n')
    if ok:
        open(path, 'wb').write(text.encode('utf-8'))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)

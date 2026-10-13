"""Track M, M8c (HPP-860, ROADMAP s122 item 778(d)): MS2 defaults commit - KYTY_M_T306 = 1 (MThemeMask default_on,
mask 0x33 -> 0x3b) and KYTY_M_T125 = 1 (MT125On in the form of MT231On / FS4a 17adaf80: unset or "" = ON,
0/false/off/no = OFF, any other value as EnvValueOn). Worktree only; main keeps default 0 until M4 (p. 756(v)).
CRLF-safe, whole-line anchors. Usage: python patch_m8c_defaults.py <tree root>   Last line: PATCH OK or FAIL."""
import sys

NL = chr(10)
CR = chr(13)
T = chr(9)
root = sys.argv[1]


def patch(rel, pairs):
    path = root + '/' + rel
    raw = open(path, 'rb').read().decode('utf-8')
    crlf = (CR + NL) in raw
    text = raw.replace(CR + NL, NL)
    for old, new in pairs:
        n = text.count(old)
        if n != 1:
            print('anchor count', n, rel, repr(old[:80]))
            print('FAIL')
            sys.exit(1)
        text = text.replace(old, new)
    if crlf:
        text = text.replace(NL, CR + NL)
    open(path, 'wb').write(text.encode('utf-8'))
    print('patched', rel, 'crlf', crlf)


patch('src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp', [
    (T + '// T256 and T306 keep default OFF (unset or "" = OFF).' + NL +
     T + 'static constexpr bool default_on[] = {true, true, false, false, true, true}; // MTheme order' + NL,
     T + '// T256 and T306 keep default OFF (unset or "" = OFF).' + NL +
     T + '// Track M, M8c (HPP-860, ROADMAP s122 item 778(d)): MS2 - T306 default ON as well (mask 0x3b); T256 stays OFF.' + NL +
     T + 'static constexpr bool default_on[] = {true, true, false, true, true, true}; // MTheme order' + NL),
])
patch('src/libs/libAudio2.cpp', [
    (T + T + 'const bool value = Common::EnvFlagOn("KYTY_M_T125");' + NL,
     T + T + '// Track M, M8c (HPP-860, ROADMAP s122 item 778(d)): MS2 default ON - unset or "" = ON, 0/false/off/no = OFF,' + NL +
     T + T + '// any other value as EnvValueOn (the form of MT231On, FS4a 17adaf80).' + NL +
     T + T + 'const char* env   = std::getenv("KYTY_M_T125");' + NL +
     T + T + 'const bool  value = env == nullptr || env[0] == ' + "'" + chr(92) + '0' + "'" + ' || Common::EnvValueOn(env);' + NL),
])
print('PATCH OK')

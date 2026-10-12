"""M2d (HPP-841, ROADMAP s122 items 756(g), 761(z), 762(v)): the defaults commit of MS1 - KYTY_M_<theme> default ON for
T234, T233, T032, T203 (translator mask 0x33) and T265, T272, T231 (HLE); T256 and T306 stay default OFF.
Form of the ON default: unset or "" = ON, 0/false/off/no = OFF, any other value as Common::EnvValueOn (FS4a 17adaf80).
Usage: python patch_m2d.py <worktree>. Whole-line anchors, CRLF-safe, writes LF bytes. Prints PATCH OK."""
import sys

ROOT = sys.argv[1].rstrip('/\\')


def patch(rel, pairs):
    path = ROOT + '/' + rel
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', '\n')
    for old, new in pairs:
        n = text.count(old)
        if n != 1:
            print('ANCHOR %s count=%d: %r' % (rel, n, old[:80]))
            sys.exit(1)
        text = text.replace(old, new)
    out = text.replace('\n', '\r\n') if crlf else text
    open(path, 'wb').write(out.encode('utf-8'))
    print('patched', rel, 'crlf' if crlf else 'lf')


NL = chr(10)
TAB = chr(9)


def L(*lines):
    return NL.join(lines) + NL


# --- translator mask
patch('src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp', [(
    L('uint32_t MThemeMask() {',
      TAB + '// Track M, M2a (HPP-838): default OFF - only a value Common::EnvValueOn accepts turns a theme on.',
      TAB + 'static const uint32_t mask = [] {',
      TAB + TAB + 'uint32_t result = 0;',
      TAB + TAB + 'for (uint32_t index = 0; index < static_cast<uint32_t>(MTheme::Count); index++) {',
      TAB + TAB + TAB + 'if (Common::EnvValueOn(std::getenv(MThemeKnob(static_cast<MTheme>(index))))) {',
      TAB + TAB + TAB + TAB + 'result |= 1u << index;',
      TAB + TAB + TAB + '}',
      TAB + TAB + '}'),
    L('uint32_t MThemeMask() {',
      TAB + '// Track M, M2a (HPP-838): default OFF - only a value Common::EnvValueOn accepts turns a theme on.',
      TAB + '// Track M, M2d (HPP-841, ROADMAP s122 items 756(g), 762(v)): default ON for the MS1 themes T234, T233, T032, T203',
      TAB + '// (mask 0x33) - unset or "" = ON, 0/false/off/no = OFF, any other value as EnvValueOn (the form of FS4a 17adaf80);',
      TAB + '// T256 and T306 keep default OFF (unset or "" = OFF).',
      TAB + 'static constexpr bool default_on[] = {true, true, false, false, true, true}; // MTheme order',
      TAB + 'static_assert(sizeof(default_on) / sizeof(default_on[0]) == static_cast<size_t>(MTheme::Count));',
      TAB + 'static const uint32_t mask = [] {',
      TAB + TAB + 'uint32_t result = 0;',
      TAB + TAB + 'for (uint32_t index = 0; index < static_cast<uint32_t>(MTheme::Count); index++) {',
      TAB + TAB + TAB + 'const char* value = std::getenv(MThemeKnob(static_cast<MTheme>(index)));',
      TAB + TAB + TAB + 'const bool  on    = (value == nullptr || value[0] == ' + "'" + chr(92) + "0'" + ') ? default_on[index]',
      TAB + TAB + TAB + '                                                           : Common::EnvValueOn(value);',
      TAB + TAB + TAB + 'if (on) {',
      TAB + TAB + TAB + TAB + 'result |= 1u << index;',
      TAB + TAB + TAB + '}',
      TAB + TAB + '}'))])

patch('src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.h', [(
    L('// signature and directory (shaderTranslationCache.cpp).',
      'enum class MTheme : uint32_t { T234 = 0, T233 = 1, T256 = 2, T306 = 3, T032 = 4, T203 = 5, Count = 6 };'),
    L('// signature and directory (shaderTranslationCache.cpp).',
      '// Track M, M2d (HPP-841, ROADMAP s122 items 756(g), 762(v)): default ON for T234, T233, T032, T203 (unset or empty = on;',
      '// 0, false, off, no = off; any other value as Common::EnvValueOn) - MThemeMask() of an unset environment is 0x33; T256',
      '// and T306 keep default OFF.',
      'enum class MTheme : uint32_t { T234 = 0, T233 = 1, T256 = 2, T306 = 3, T032 = 4, T203 = 5, Count = 6 };'))])

# --- HLE knobs: same form, default ON


def hle(rel, knob):
    old = L(TAB + TAB + 'const bool value = Common::EnvValueOn(std::getenv("' + knob + '"));')
    new = L(TAB + TAB + '// Track M, M2d (HPP-841, ROADMAP s122 items 756(g), 762(v)): default ON - unset or "" = ON, 0/false/off/no = OFF,',
            TAB + TAB + '// any other value as EnvValueOn (the form of FS4a 17adaf80).',
            TAB + TAB + 'const char* env   = std::getenv("' + knob + '");',
            TAB + TAB + 'const bool  value = env == nullptr || env[0] == ' + "'" + chr(92) + "0'" + ' || Common::EnvValueOn(env);')
    patch(rel, [(old, new)])


hle('src/libs/libAmpr.cpp', 'KYTY_M_T265')
hle('src/libs/controller.cpp', 'KYTY_M_T272')
hle('src/libs/libFont.cpp', 'KYTY_M_T231')
print('PATCH OK')

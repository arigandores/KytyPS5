# FS7a (HPP-565, ROADMAP s122 items 467(g)(1), 487(g)(1)): defaults KYTY_FIX_F8 and KYTY_FIX_B24 0 -> 1 in the form of
# FS4a 17adaf80 (unset or "" = ON, otherwise Common::EnvValueOn); one reading each is kept (F8: the static const bool of
# FixF8Enabled; B24: the one write of g_fix_b24 in Controller::Initialize), the lines "FixF8: mode=1" / "FixB24: mode=1"
# stay where they are (now printed by default). Comments that named the old default are corrected. Anchors are whole
# lines; CRLF files are handled (\r removed before the search and put back). Writes LF/CRLF as found (write_bytes).
# Usage: python patch_fs7a.py <repo root>
import sys

ROOT = sys.argv[1]
NL = chr(10)


def patch(rel, edits):
    path = ROOT + '/' + rel
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', NL)
    lines = text.split(NL)
    for old, new in edits:
        old_l = old.split(NL)
        hits = [i for i in range(len(lines) - len(old_l) + 1) if lines[i:i + len(old_l)] == old_l]
        if len(hits) != 1:
            print('ANCHOR FAIL %s: %d hits for %r' % (rel, len(hits), old_l[0]))
            sys.exit(1)
        i = hits[0]
        lines[i:i + len(old_l)] = new.split(NL)
    out = NL.join(lines)
    if crlf:
        out = out.replace(NL, '\r\n')
    open(path, 'wb').write(out.encode('utf-8'))
    print('patched %s (%d edits, crlf=%s)' % (rel, len(edits), crlf))


T = chr(9)

patch('src/libs/audio.cpp', [(
    NL.join([
        'static bool FixF8Enabled() {',
        T + 'static const bool enabled = [] {',
        T + T + 'const bool on = Common::EnvValueOn(std::getenv("KYTY_FIX_F8"));',
        T + T + 'if (on) {',
    ]),
    NL.join([
        'static bool FixF8Enabled() {',
        T + '// Track F, FS7a (HPP-565, ROADMAP s122 item 467(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any',
        T + '// other value as EnvValueOn (the form of FS4a 17adaf80).',
        T + 'static const bool enabled = [] {',
        T + T + 'const char* value = std::getenv("KYTY_FIX_F8");',
        T + T + 'const bool  on    = value == nullptr || value[0] == ' + "'" + '\\0' + "'" + ' || Common::EnvValueOn(value);',
        T + T + 'if (on) {',
    ]),
)])

patch('src/libs/audio_internal.h', [(
    NL.join([
        '// SDL_INIT_AUDIO (AudioOut ports, AudioIn ports, pad haptics). KYTY_FIX_F8 unset or 0: the same SDL calls as before',
        '// (each init counted). KYTY_FIX_F8=1: init goes through SdlAudioAcquire, quit does nothing - the SDL reference count of',
        '// the audio subsystem stays 1 for the life of the process. Read once per process; "FixF8: mode=1" once at 1.',
    ]),
    NL.join([
        '// SDL_INIT_AUDIO (AudioOut ports, AudioIn ports, pad haptics). KYTY_FIX_F8=0: the same SDL calls as before (each init',
        '// counted). KYTY_FIX_F8 unset, empty or 1 (default ON since FS7a, item 467(g)(1)): init goes through SdlAudioAcquire,',
        '// quit does nothing - the SDL reference count of the audio subsystem stays 1 for the life of the process. Read once per',
        '// process; "FixF8: mode=1" once when on.',
    ]),
)])

patch('src/libs/controller.cpp', [
    (
        NL.join([
            '// Track F, F19c (ROADMAP s122 item 451(d), member A of F19a s5.1): KYTY_FIX_B24 - unset, empty, 0/false/off/no: off',
            '// (Common::EnvFlagOn). Written once by Initialize before the guest threads exist, only read afterwards. At 1 the guest' + "'" + 's',
        ]),
        NL.join([
            '// Track F, F19c (ROADMAP s122 item 451(d), member A of F19a s5.1): KYTY_FIX_B24 - default ON since FS7a (item 487(g)(1)):',
            '// unset or empty: on, 0/false/off/no: off, any other value as Common::EnvValueOn. Written once by Initialize before the',
            '// guest threads exist, only read afterwards. At 1 the guest' + "'" + 's',
        ]),
    ),
    (
        NL.join([
            T + '// Track F, F19c (ROADMAP s122 item 451(d)): KYTY_FIX_B24, read once here - before the guest threads exist.',
            T + 'g_fix_b24 = Common::EnvFlagOn("KYTY_FIX_B24");',
        ]),
        NL.join([
            T + '// Track F, F19c (ROADMAP s122 item 451(d)): KYTY_FIX_B24, read once here - before the guest threads exist.',
            T + '// FS7a (HPP-565, ROADMAP s122 item 487(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any other value',
            T + '// as EnvValueOn (the form of FS4a 17adaf80).',
            T + 'g_fix_b24 = [] {',
            T + T + 'const char* value = std::getenv("KYTY_FIX_B24");',
            T + T + 'return value == nullptr || value[0] == ' + "'" + '\\0' + "'" + ' || Common::EnvValueOn(value);',
            T + '}();',
        ]),
    ),
])
print('PATCH OK')

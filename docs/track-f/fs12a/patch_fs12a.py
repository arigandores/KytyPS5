# FS12a (HPP-750, ROADMAP s122 item 683(g)(1)): KYTY_FIX_F21 default 0 -> 1 in the form of FS11a cb022252 (unset or "" = 1,
# otherwise Common::EnvValueOn); the one reading in InitFixF21 (main thread, Emulator::Run before Init) is kept; the line
# "FixF21: mode=<0|1>" (LogFixF21) prints the value as before. Anchors are whole lines; CRLF kept if present.
# Usage: python patch_fs12a.py <repo root>
import sys

root = sys.argv[1].rstrip('/') + '/'


def patch(rel, edits):
    p = root + rel
    raw = open(p, 'rb').read()
    crlf = b'\r\n' in raw
    lines = raw.decode('utf-8').replace('\r\n', '\n').split('\n')
    for old, new in edits:
        idx = [i for i in range(len(lines) - len(old) + 1) if lines[i:i + len(old)] == old]
        assert len(idx) == 1, (rel, old[0], len(idx))
        i = idx[0]
        lines[i:i + len(old)] = new
    text = '\n'.join(lines)
    if crlf:
        text = text.replace('\n', '\r\n')
    open(p, 'wb').write(text.encode('utf-8'))
    print('patched', rel, 'crlf' if crlf else 'lf')


patch('src/common/subsystems.cpp', [(
    ['// F33c: KYTY_FIX_F21 (the flags - at the top of this file).',
     'void Subsystems::InitFixF21() {',
     '\tg_fix_f21  = EnvFlagOn("KYTY_FIX_F21"); // unset, "", 0/false/off/no - OFF (the form of FS4a)',
     '\tg_f21_path = g_fix_f21 || g_f21_hook != nullptr;',
     '}'],
    ['// F33c: KYTY_FIX_F21 (the flags - at the top of this file).',
     '// Track F, FS12a (HPP-750, ROADMAP s122 item 683(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any other',
     '// value as EnvValueOn (the form of FS11a cb022252).',
     'void Subsystems::InitFixF21() {',
     '\tconst char* value = std::getenv("KYTY_FIX_F21");',
     '\tg_fix_f21  = value == nullptr || value[0] == \'\\0\' || EnvValueOn(value);',
     '\tg_f21_path = g_fix_f21 || g_f21_hook != nullptr;',
     '}'],
)])
patch('src/common/subsystems.h', [(
    ['\t// Track F, F33c (HPP-744; ROADMAP s122 item 675(g)): KYTY_FIX_F21 (default 0). InitFixF21 reads the knob once - on'],
    ['\t// Track F, F33c (HPP-744; ROADMAP s122 item 675(g)): KYTY_FIX_F21. InitFixF21 reads the knob once - on'],
), (
    ['\t// thread and time as InitFixF21.',
     '\tstatic constexpr uint32_t kFixF21WaitMs = 12000; // T of item 675(v)(2)'],
    ['\t// thread and time as InitFixF21.',
     '\t// Track F, FS12a (HPP-750, ROADMAP s122 item 683(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF.',
     '\tstatic constexpr uint32_t kFixF21WaitMs = 12000; // T of item 675(v)(2)'],
)])
print('ok')

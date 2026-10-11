"""FS14a (HPP-812, ROADMAP s122 item 710(g)(1)): KYTY_FIX_F24 default 0 -> 1 in JoyPump::ReadKnob
(src/graphics/presentation/window/joyPump.cpp), the form of FS13a 3630f116 / FS12a cbfe8375 (unset or "" = ON, otherwise
Common::EnvValueOn); one reading (ReadKnob, WindowCreate before the SDL init, later calls do nothing) kept; the line
"FixF24: mode=<0|1> b24=<0|1>" unchanged. Two header comments of joyPump.h that say "default 0" are updated.
Anchors are whole lines; CRLF-safe (strips CR before the search, restores it); writes bytes.
Usage: python patch_fs14a.py <repo root>"""
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


CPP = 'src/graphics/presentation/window/joyPump.cpp'
H = 'src/graphics/presentation/window/joyPump.h'

out = patch(CPP, [(
    ['\tg_enabled.store(Common::EnvFlagOn("KYTY_FIX_F24"), std::memory_order_release);'],
    ['\t// Track F, FS14a (HPP-812, ROADMAP s122 item 710(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any',
     '\t// other value as EnvValueOn (the form of FS13a 3630f116 / FS12a cbfe8375).',
     '\tconst char* value = std::getenv("KYTY_FIX_F24");',
     '\tg_enabled.store(value == nullptr || value[0] == \'\\0\' || Common::EnvValueOn(value), std::memory_order_release);'])])
assert out.count('EnvFlagOn("KYTY_FIX_F24")') == 0
assert out.count('getenv("KYTY_FIX_F24")') == 1

out = patch(H, [
    (['// Default 0: nothing here runs except ReadKnob, Enabled (false) and Exited (true); the SDL init, the event wait and the'],
     ['// At 0 (default 1 since FS14a - ReadKnob below): nothing here runs except ReadKnob, Enabled (false) and Exited (true);',
      '// the SDL init, the event wait and the']),
    (['// Main thread, WindowCreate, before any SDL_InitSubSystem: reads KYTY_FIX_F24 once (Common::EnvFlagOn, default 0) and'],
     ['// Main thread, WindowCreate, before any SDL_InitSubSystem: reads KYTY_FIX_F24 once (track F, FS14a, HPP-812, ROADMAP s122',
      '// item 710(g)(1): default 1 - unset or "" = ON, 0/false/off/no = OFF, any other value as EnvValueOn) and'])])
assert 'default 0' not in out
print('PATCH OK')

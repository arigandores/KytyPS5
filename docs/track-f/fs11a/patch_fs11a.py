# FS11a (HPP-714, ROADMAP s122 item 647(d)(1)): KYTY_FIX_B12 default 0 -> 1 in the form of FS4a 17adaf80 / FS9a (FixB13Enabled)
# / FS10a 7f34b1e2 (unset or "" = 1, otherwise Common::EnvValueOn); one reading kept (static local of FixB12Enabled); the
# line "FixB12: mode=<0|1>" (BufferCache constructor) prints the value as before. Anchors are whole lines; CRLF kept if present.
# Usage: python patch_fs11a.py <repo root>
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


patch('src/graphics/host_gpu/regionManager.h', [(
    ['// Track F, F29c (HPP-702, ROADMAP s122 item 639(d)): knob KYTY_FIX_B12, read once per process; default OFF - unset, "",',
     '// 0/false/off/no = OFF (Common::EnvValueOn). At 1 the incremental BDA scan numbers its passes (RenderContext::PrepareBda),'],
    ['// Track F, F29c (HPP-702, ROADMAP s122 item 639(d)): knob KYTY_FIX_B12, read once per process. At 1 the incremental',
     '// BDA scan numbers its passes (RenderContext::PrepareBda),'],
), (
    ['// BufferCache\'s constructor prints "FixB12: mode=<0|1>" once per process.',
     '[[nodiscard]] inline bool FixB12Enabled() noexcept {',
     '\tstatic const bool on = Common::EnvValueOn(std::getenv("KYTY_FIX_B12"));',
     '\treturn on;',
     '}'],
    ['// BufferCache\'s constructor prints "FixB12: mode=<0|1>" once per process.',
     '// Track F, FS11a (HPP-714, ROADMAP s122 item 647(d)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any other',
     '// value as EnvValueOn (the form of FS4a 17adaf80).',
     '[[nodiscard]] inline bool FixB12Enabled() noexcept {',
     '\tstatic const bool on = [] {',
     '\t\tconst char* value = std::getenv("KYTY_FIX_B12");',
     '\t\treturn value == nullptr || value[0] == \'\\0\' || Common::EnvValueOn(value);',
     '\t}();',
     '\treturn on;',
     '}'],
)])
print('ok')

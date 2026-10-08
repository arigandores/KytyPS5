# FS10a (HPP-684, ROADMAP s122 item 624(e)(1)): KYTY_FIX_B36 default 0 -> 1 in the form of FS4a 17adaf80 (unset or "" = 1,
# otherwise Common::EnvValueOn); one reading kept; the LogAsync: lines, the stand and the measure unchanged. The test
# seq0_unset of tests/LogAsyncTests.cpp follows the default (unset = =1). Anchors are whole lines; CRLF kept if present.
# Usage: python patch_fs10a.py <repo root>
import sys

root = sys.argv[1].rstrip('/') + '/'


def patch(rel, edits):
    p = root + rel
    raw = open(p, 'rb').read()
    crlf = b'\r\n' in raw
    lines = raw.decode('utf-8').replace('\r\n', '\n').split('\n')
    for old, new in edits:
        n = lines.count(old[0]) if len(old) == 1 else None
        idx = [i for i in range(len(lines) - len(old) + 1) if lines[i:i + len(old)] == old]
        assert len(idx) == 1, (rel, old[0], len(idx))
        i = idx[0]
        lines[i:i + len(old)] = new
    text = '\n'.join(lines)
    if crlf:
        text = text.replace('\n', '\r\n')
    open(p, 'wb').write(text.encode('utf-8'))
    print('patched', rel, 'crlf' if crlf else 'lf')


patch('src/common/logging/log.cpp', [(
    ['\tconst bool requested = Common::EnvFlagOn("KYTY_FIX_B36");'],
    ['\t// Track F, FS10a (HPP-684, ROADMAP s122 item 624(e)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any',
     '\t// other value as EnvValueOn (the form of FS4a 17adaf80); read once, here.',
     '\tconst bool requested = [] {',
     '\t\tconst char* value = std::getenv("KYTY_FIX_B36");',
     '\t\treturn value == nullptr || value[0] == \'\\0\' || Common::EnvValueOn(value);',
     '\t}();'],
)])

patch('tests/LogAsyncTests.cpp', [(
    ['\tCase("seq0_unset: KYTY_FIX_B36 unset - the file equals the =0 file");',
     '\tSpawn("seq0", Path("seq0_u"), 0, nullptr, nullptr);',
     '\tCHECK(ReadFile(Path("seq0_u")) == f0);'],
    ['\t// Track F, FS10a (HPP-684, ROADMAP s122 item 624(e)(1)): KYTY_FIX_B36 is ON by default - unset is =1.',
     '\tCase("seq0_unset: KYTY_FIX_B36 unset - default ON since FS10a - checked as seq0_1");',
     '\tSpawn("seq0", Path("seq0_u"), 0, nullptr, nullptr);',
     '\tconst auto fu = ReadFile(Path("seq0_u"));',
     '\tCHECK(StartsWith(fu, "LogAsync: mode=1 limit_bytes=268435456"));',
     '\tCHECK(fu.find("LogAsync: full_waits=0 ") != std::string::npos);',
     '\tCHECK(WithoutPrefix(fu, "LogAsync:") == expected);'],
)])
print('ok')

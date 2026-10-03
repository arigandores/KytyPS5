# FS3a (HPP-447, ROADMAP s122 item 367(g)(1)): KYTY_FIX_B42 default 0 -> 1 in the FSa form and the per-extent line
# FixB42Ext. Anchors are whole lines / blocks, each must occur exactly once; all are checked before any write; CRLF is
# stripped before the search and restored on write; output LF if the input was LF.
# Usage: patch_fs3a.py <descriptors.cpp>
import sys

path = sys.argv[1]
raw = open(path, "rb").read()
crlf = b"\r\n" in raw
text = raw.decode("utf-8").replace("\r\n", "\n")

NL = chr(10)

def L(*lines):
    return NL.join(lines) + NL

edits = []

# 1. header comment of the reading
edits.append((
    L('// Track F, F9e2 (B42, ROADMAP s122 item 351(v)(1)-(3)) and F9e2b (item 353(g)(1)-(3)), KYTY_FIX_B42 (default 0: unset,',
      '// "", 0/false/off/no = OFF).'),
    L('// Track F, F9e2 (B42, ROADMAP s122 item 351(v)(1)-(3)) and F9e2b (item 353(g)(1)-(3)), KYTY_FIX_B42 (default ON since',
      '// FS3a, item 367(g)(1): unset or "" = ON, 0/false/off/no = OFF).'),
))

# 2. the reading
edits.append((
    L('bool FixB42Enabled() {',
      '\tstatic const bool enabled = Common::EnvFlagOn("KYTY_FIX_B42");',
      '\treturn enabled;',
      '}'),
    L('bool FixB42Enabled() {',
      '\t// Track F, FS3a (HPP-447, ROADMAP s122 item 367(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any',
      '\t// other value as EnvValueOn (the form of FSa / FS2a).',
      '\tstatic const bool enabled = [] {',
      '\t\tconst char* value = std::getenv("KYTY_FIX_B42");',
      '\t\treturn value == nullptr || value[0] == \'\\0\' || Common::EnvValueOn(value);',
      '\t}();',
      '\treturn enabled;',
      '}'),
))

# 3. comment of FixB42Note
edits.append((
    L('// The line: on every growth of hit or drawn for the first 256 lines, then at most once per 600 frames (still only on a',
      '// growth of hit or drawn). hit / applied / drawn / rearm are the counters of the line\'s extent; hit_all - the hits of',
      '// all extents.'),
    L('// The line: on every growth of hit or drawn for the first 256 lines, then at most once per 600 frames (still only on a',
      '// growth of hit or drawn). hit / applied / drawn / rearm are the counters of the line\'s extent; hit_all - the hits of',
      '// all extents.',
      '// Track F, FS3a (ROADMAP s122 item 367(g)(1), debt of item 363(v)): the line FixB42Ext of an extent - on a growth of its',
      '// hit or applied (applied grows only with hit, so: on a hit), the first one at once, then at most once per 600 frames',
      '// of that extent, at most 64 lines per extent; outside the 256-line budget of FixB42 (that line and its rate are',
      '// unchanged). It reads the counters only: no state of the fix or of the cache depends on it.'),
))

# 4. Counts struct: own bookkeeping of the extent line
edits.append((
    L('\t\tuint64_t rearm   = 0;',
      '\t};'),
    L('\t\tuint64_t rearm   = 0;',
      '\t\tuint32_t ext_lines      = 0; // FS3a: FixB42Ext lines of this extent',
      '\t\tuint32_t ext_printed_at = 0; // FS3a: frame of the last FixB42Ext line of this extent',
      '\t};'),
))

# 5. the extent line, before the rate limit of FixB42
edits.append((
    L('\t} else {',
      '\t\tcounts.drawn++;',
      '\t}',
      '\tif (lines >= 256 && frame - printed_at < 600u) {'),
    L('\t} else {',
      '\t\tcounts.drawn++;',
      '\t}',
      '\tif (probe.kind == FixB42Kind::Hit && counts.ext_lines < 64 &&',
      '\t    (counts.ext_lines == 0 || frame - counts.ext_printed_at >= 600u)) {',
      '\t\tcounts.ext_lines++;',
      '\t\tcounts.ext_printed_at = frame;',
      '\t\tLOGF("FixB42Ext: mode=%d extent=%ux%u hit=%" PRIu64 " applied=%" PRIu64 " drawn=%" PRIu64 " rearm=%" PRIu64',
      '\t\t     " frame=%u\\n",',
      '\t\t     FixB42Enabled() ? 1 : 0, width, height, counts.hit, counts.applied, counts.drawn, counts.rearm, frame);',
      '\t}',
      '\tif (lines >= 256 && frame - printed_at < 600u) {'),
))

bad = 0
for old, new in edits:
    n = text.count(old)
    if n != 1:
        print("ANCHOR COUNT", n, "for:", old.split(NL)[0][:100])
        bad += 1
if bad:
    print("NOT PATCHED")
    sys.exit(1)
for old, new in edits:
    text = text.replace(old, new)
out = text.replace(NL, "\r\n") if crlf else text
open(path, "wb").write(out.encode("utf-8"))
print("patched", path, "edits", len(edits), "crlf", crlf)

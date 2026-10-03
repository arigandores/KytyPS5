# FS4a (HPP-470, ROADMAP s122 item 378(g)(1)): KYTY_FIX_SVAL default 0 -> 1 in the FSa / FS3a form (unset or "" = ON,
# 0/false/off/no = OFF, any other value as EnvValueOn). The lines FixSval: / FixSvalStat: are not touched.
# Anchors are whole lines / blocks, each must occur exactly once; all are checked before any write; CRLF is stripped
# before the search and restored on write; output LF if the input was LF.
# Usage: patch_fs4a.py <pipelineCache.cpp>
import sys

path = sys.argv[1]
raw = open(path, "rb").read()
crlf = b"\r\n" in raw
text = raw.decode("utf-8").replace("\r\n", "\n")

NL = chr(10)

def L(*lines):
    return NL.join(lines) + NL

edits = []

# 1. header comment + the reading
edits.append((
    L('// Track F, F10c (HPP-451, ROADMAP s122 item 369(b), row F16): KYTY_FIX_SVAL (default OFF: unset, "", 0/false/off/no = OFF,',
      '// as Common::EnvValueOn; read once). ON: ValidateShaderSpirv validates with spvtools::ValidatorOptions where',
      '// SetUniformBufferStandardLayout(true) is set if and only if the device enabled uniformBufferStandardLayout',
      '// (g_fix_sval_ubo_std_layout: stored by the PipelineCache constructor from GraphicContext before its workers start and',
      '// before any translation), and logs "FixSvalStat: validated=<n> rejected=<m>" on every 256th check (n - checks made,',
      '// m - checks rejected). OFF: the old call tools.Validate(spirv) without options, no counters, no line.',
      'bool FixSvalEnabled() {',
      '\tstatic const bool enabled = Common::EnvValueOn(std::getenv("KYTY_FIX_SVAL"));',
      '\treturn enabled;',
      '}'),
    L('// Track F, F10c (HPP-451, ROADMAP s122 item 369(b), row F16): KYTY_FIX_SVAL (default ON since FS4a, item 378(g)(1):',
      '// unset or "" = ON, 0/false/off/no = OFF; read once). ON: ValidateShaderSpirv validates with spvtools::ValidatorOptions where',
      '// SetUniformBufferStandardLayout(true) is set if and only if the device enabled uniformBufferStandardLayout',
      '// (g_fix_sval_ubo_std_layout: stored by the PipelineCache constructor from GraphicContext before its workers start and',
      '// before any translation), and logs "FixSvalStat: validated=<n> rejected=<m>" on every 256th check (n - checks made,',
      '// m - checks rejected). OFF: the old call tools.Validate(spirv) without options, no counters, no line.',
      'bool FixSvalEnabled() {',
      '\t// Track F, FS4a (HPP-470, ROADMAP s122 item 378(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any',
      '\t// other value as EnvValueOn (the form of FSa / FS2a / FS3a).',
      '\tstatic const bool enabled = [] {',
      '\t\tconst char* value = std::getenv("KYTY_FIX_SVAL");',
      '\t\treturn value == nullptr || value[0] == \'\\0\' || Common::EnvValueOn(value);',
      '\t}();',
      '\treturn enabled;',
      '}'),
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

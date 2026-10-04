#!/usr/bin/env python3
# S12a (HPP-494, ROADMAP s122 item 408(l), 410(g)(6)): KYTY_S_PCW default 0 -> 1 in the form of FS4a 17adaf80
# (unset or "" = ON, 0/false/off/no = OFF, any other value as Common::EnvValueOn). One reading (static const bool) kept.
# Usage: patch_s12a.py <repo root>. Anchors are whole lines; CR is stripped before the search and restored after.
import sys

root = sys.argv[1]
path = root + "/src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp"
raw = open(path, "rb").read()
crlf = b"\r\n" in raw
text = raw.decode("utf-8").replace("\r\n", "\n")
lines = text.split("\n")

OLD = [
    "// Track S, route S-pcw (ROADMAP \"SESSION 122\" item 241(h)(1), HPP-316): KYTY_S_PCW=1 moves the periodic driver",
    "// pipeline cache write (vkGetPipelineCacheData + the file) and the pipelines.bin rewrite off m_mutex and off the",
    "// GuestGpu thread to one writer thread (PipelineCache::PcwLoop).  Default 0 (any value but exactly \"1\") = the old path.",
    "// Read ONCE per process; the value is logged by the PipelineCache constructor (\"S-pcw:\").",
    "bool SPcwMode() {",
    "\tstatic const bool mode = [] {",
    "\t\tconst char* value = std::getenv(\"KYTY_S_PCW\");",
    "\t\treturn value != nullptr && value[0] == '1' && value[1] == '\\0';",
    "\t}();",
    "\treturn mode;",
    "}",
]
NEW = [
    "// Track S, route S-pcw (ROADMAP \"SESSION 122\" item 241(h)(1), HPP-316): KYTY_S_PCW=1 moves the periodic driver",
    "// pipeline cache write (vkGetPipelineCacheData + the file) and the pipelines.bin rewrite off m_mutex and off the",
    "// GuestGpu thread to one writer thread (PipelineCache::PcwLoop).  Default ON since S12a (item 408(l)): unset or \"\" = ON,",
    "// 0/false/off/no = OFF = the old path.  Read ONCE per process; the value is logged by the PipelineCache constructor",
    "// (\"S-pcw:\").",
    "bool SPcwMode() {",
    "\t// Track S, S12a (HPP-494, ROADMAP s122 item 408(l)): default ON - unset or \"\" = ON, 0/false/off/no = OFF, any other",
    "\t// value as EnvValueOn (the form of FS4a 17adaf80).",
    "\tstatic const bool mode = [] {",
    "\t\tconst char* value = std::getenv(\"KYTY_S_PCW\");",
    "\t\treturn value == nullptr || value[0] == '\\0' || Common::EnvValueOn(value);",
    "\t}();",
    "\treturn mode;",
    "}",
]

hits = [i for i in range(len(lines) - len(OLD) + 1) if lines[i:i + len(OLD)] == OLD]
if len(hits) != 1:
    print("ANCHOR FAIL: hits", len(hits))
    sys.exit(1)
i = hits[0]
lines[i:i + len(OLD)] = NEW
out = "\n".join(lines)
if crlf:
    out = out.replace("\n", "\r\n")
open(path, "wb").write(out.encode("utf-8"))
print("patched", path, "at line", i + 1, "crlf", crlf)

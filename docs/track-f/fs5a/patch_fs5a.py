# FS5a (HPP-509, ROADMAP s122 item 410(g)(1)): KYTY_FIX_F10 default 0 -> 1 in the form of FS4a 17adaf80 (unset or "" = ON,
# otherwise Common::EnvValueOn; one read, static const bool). Comments that state the default follow (ShaderDecoder.h,
# shaderTranslationCache.cpp). Anchors are whole blocks of lines; each must occur exactly once. CRLF-safe; writes LF.
# Usage: python patch_fs5a.py <repo root>
import sys

ROOT = sys.argv[1].rstrip("/")

EDITS = [
    ("src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp",
     "bool FixF10Enabled() {\n"
     "\tstatic const bool enabled = Common::EnvValueOn(std::getenv(\"KYTY_FIX_F10\"));\n"
     "\treturn enabled;\n"
     "}\n",
     "bool FixF10Enabled() {\n"
     "\t// Track F, FS5a (HPP-509, ROADMAP s122 item 410(g)(1)): default ON - unset or \"\" = ON, 0/false/off/no = OFF, any\n"
     "\t// other value as EnvValueOn (the form of FS4a 17adaf80).\n"
     "\tstatic const bool enabled = [] {\n"
     "\t\tconst char* value = std::getenv(\"KYTY_FIX_F10\");\n"
     "\t\treturn value == nullptr || value[0] == '\\0' || Common::EnvValueOn(value);\n"
     "\t}();\n"
     "\treturn enabled;\n"
     "}\n"),
    ("src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.h",
     "// Track F, F12d (HPP-477, ROADMAP p.391(v)): KYTY_FIX_F10, default OFF (unset, empty, 0, false, off, no = off, as\n"
     "// Common::EnvValueOn). On: IMAGE_BVH_INTERSECT_RAY treats node types 2 and 3 as triangles, as the GPURT software\n",
     "// Track F, F12d (HPP-477, ROADMAP p.391(v)): KYTY_FIX_F10, default ON since FS5a (HPP-509, ROADMAP p.410(g)(1): unset\n"
     "// or empty = on; 0, false, off, no = off; any other value as Common::EnvValueOn). On: IMAGE_BVH_INTERSECT_RAY treats\n"
     "// node types 2 and 3 as triangles, as the GPURT software\n"),
    ("src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp",
     "\t// Track F, F12d (ROADMAP p.391(v)): KYTY_FIX_F10=1 (default 0) adds \":fixf10\" last, so =0 and =1 never\n"
     "\t// share a signature or a directory.\n",
     "\t// Track F, F12d (ROADMAP p.391(v)): KYTY_FIX_F10=1 (the default since FS5a, p.410(g)(1)) adds \":fixf10\" last, so\n"
     "\t// =0 and =1 never share a signature or a directory.\n"),
]

ok = True
for rel, old, new in EDITS:
    path = ROOT + "/" + rel
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    n = text.count(old)
    if n != 1:
        print("ANCHOR", n, rel)
        ok = False
        continue
    text = text.replace(old, new)
    open(path, "wb").write(text.encode("utf-8"))
    print("OK", rel, "crlf_in" if crlf else "lf_in")
print("PATCH OK" if ok else "PATCH FAIL")
sys.exit(0 if ok else 1)

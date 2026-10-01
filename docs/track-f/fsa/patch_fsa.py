# FSa (HPP-368, ROADMAP s122 p.282(g)(1), p.281(v)(1)): default of KYTY_FIX_DUALSRC 0 -> 1.
# Only the reading expression of the knob and its comment change; the unset / "" = ON form is the one of
# FixB26Enabled / FixB1BEnabled (ShaderDecoder.cpp): unset or "" -> 1, otherwise Common::EnvValueOn.
# Anchors are whole lines; the file is LF; the script strips CR before matching and restores it.
import sys

PATH = "C:/kyty/KytyPS5/src/graphics/presentation/window/vulkanWindow.cpp"

OLD = [
    "\t// Track F, F4 (HPP-335, ROADMAP s122 p.254(zh)(1), row B35): pipelines with SRC1 blend factors",
    "\t// (recipe 1592: SRC1_ALPHA / ONE_MINUS_SRC1_ALPHA) are created without dualSrcBlend. KYTY_FIX_DUALSRC",
    "\t// (Common::EnvFlagOn: unset, \"\", 0/false/off/no = OFF; default OFF) enables it when supported; OFF leaves",
    "\t// device_features as before. Outside the translation cache signature (not under src/graphics/shader).",
    "\t{",
    "\t\tconst bool dual_src_supported = supported_features2.features.dualSrcBlend == VK_TRUE;",
    "\t\tconst bool dual_src_enabled   = dual_src_supported && Common::EnvFlagOn(\"KYTY_FIX_DUALSRC\");",
]
NEW = [
    "\t// Track F, F4 (HPP-335, ROADMAP s122 p.254(zh)(1), row B35): pipelines with SRC1 blend factors",
    "\t// (recipe 1592: SRC1_ALPHA / ONE_MINUS_SRC1_ALPHA) are created without dualSrcBlend. KYTY_FIX_DUALSRC",
    "\t// (default ON since FSa, HPP-368, p.282(g)(1): unset or \"\" = ON as KYTY_FIX_B26; 0/false/off/no = OFF)",
    "\t// enables it when supported; OFF leaves device_features as before. Outside the translation cache",
    "\t// signature (not under src/graphics/shader).",
    "\t{",
    "\t\tconst bool dual_src_supported = supported_features2.features.dualSrcBlend == VK_TRUE;",
    "\t\tconst char* dual_src_value    = std::getenv(\"KYTY_FIX_DUALSRC\");",
    "\t\tconst bool dual_src_enabled   = dual_src_supported && (dual_src_value == nullptr || dual_src_value[0] == '\\0' ||",
    "\t\t                                                     Common::EnvValueOn(dual_src_value));",
]

raw = open(PATH, "rb").read()
crlf = b"\r\n" in raw
text = raw.decode("utf-8").replace("\r\n", "\n")
lines = text.split("\n")
n = len(OLD)
hits = [i for i in range(len(lines) - n + 1) if lines[i:i + n] == OLD]
if len(hits) != 1:
    print("ANCHOR HITS", len(hits))
    sys.exit(1)
i = hits[0]
lines[i:i + n] = NEW
out = "\n".join(lines)
if crlf:
    out = out.replace("\n", "\r\n")
open(PATH, "wb").write(out.encode("utf-8"))
print("PATCHED line", i + 1, "crlf", crlf)

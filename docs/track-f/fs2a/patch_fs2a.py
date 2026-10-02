# FS2a (HPP-381, ROADMAP s122 p.298(v), p.327(g)): defaults of KYTY_FIX_MINIMIZE 0 -> 1 and KYTY_FIX_B9A 0 -> 1.
# Only the reading expressions of the two knobs and their comments change; the unset / "" = ON form is the one of
# FSa (95eec776, KYTY_FIX_DUALSRC in vulkanWindow.cpp): unset or "" -> 1, otherwise Common::EnvValueOn.
# Anchors are whole lines; the files are LF; the script strips CR before matching and restores it.
import sys

EDITS = [
    (
        "C:/kyty/KytyPS5/src/graphics/presentation/window/swapchain.cpp",
        [
            "// Track F, F5 (ROADMAP s122 item 273(e)(1), B37): KYTY_FIX_MINIMIZE (default 0 until F5d; 0 - the old path byte for",
            "// byte).  1: a swapchain recreate that finds currentExtent 0 on either axis (a minimized window) creates no swapchain;",
            "// Presenter::Present drops its frames without blocking and retries on each later present until the extent is non-zero.",
            "// Read once; \"FixMinimize: on\" is logged only when on.",
            "static bool FixMinimizeEnabled() {",
            "\tstatic const bool enabled = [] {",
            "\t\tconst bool on = Common::EnvFlagOn(\"KYTY_FIX_MINIMIZE\");",
        ],
        [
            "// Track F, F5 (ROADMAP s122 item 273(e)(1), B37): KYTY_FIX_MINIMIZE (default ON since FS2a, HPP-381, item 298(v):",
            "// unset or \"\" = ON as KYTY_FIX_DUALSRC; 0/false/off/no = OFF - the old path byte for byte).  ON: a swapchain",
            "// recreate that finds currentExtent 0 on either axis (a minimized window) creates no swapchain; Presenter::Present",
            "// drops its frames without blocking and retries on each later present until the extent is non-zero.",
            "// Read once; \"FixMinimize: on\" is logged only when on.",
            "static bool FixMinimizeEnabled() {",
            "\tstatic const bool enabled = [] {",
            "\t\tconst char* value = std::getenv(\"KYTY_FIX_MINIMIZE\");",
            "\t\tconst bool  on    = value == nullptr || value[0] == '\\0' || Common::EnvValueOn(value);",
        ],
    ),
    (
        "C:/kyty/KytyPS5/src/libs/libAudio.cpp",
        [
            "// Track F, F6 (ROADMAP s122 item 287(c), B9a): KYTY_FIX_B9A (default 0 until the shipment link; 0 - the old path byte",
            "// for byte: the 16 NIDs of the second block of InitAudio_1_AudioPropagation are not registered, nothing is counted",
            "// or logged).  1: V1 of the F6a design (docs/track-f/f6a-b9a.md section 5) - the 16 functions the game imports and the",
        ],
        [
            "// Track F, F6 (ROADMAP s122 item 287(c), B9a): KYTY_FIX_B9A (default ON since FS2a, HPP-381, items 298(v) and 327(g):",
            "// unset or \"\" = ON as KYTY_FIX_DUALSRC; 0/false/off/no = OFF - the old path byte for byte: the 16 NIDs of the second",
            "// block of InitAudio_1_AudioPropagation are not registered, nothing is counted or logged).  ON: V1 of the F6a design",
            "// (docs/track-f/f6a-b9a.md section 5) - the 16 functions the game imports and the",
        ],
    ),
    (
        "C:/kyty/KytyPS5/src/libs/libAudio.cpp",
        [
            "\t// F6 (B9a): read on each registration (the emulator registers once; the test registers with 0 and with 1).",
            "\tconst bool fix_b9a = Common::EnvFlagOn(\"KYTY_FIX_B9A\");",
        ],
        [
            "\t// F6 (B9a): read on each registration (the emulator registers once; the test registers with 0 and with 1).",
            "\t// Default ON since FS2a (HPP-381, ROADMAP s122 items 298(v), 327(g)): unset or \"\" = ON.",
            "\tconst char* fix_b9a_value = std::getenv(\"KYTY_FIX_B9A\");",
            "\tconst bool  fix_b9a       = fix_b9a_value == nullptr || fix_b9a_value[0] == '\\0' || Common::EnvValueOn(fix_b9a_value);",
        ],
    ),
]

for path, old, new in EDITS:
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    lines = text.split("\n")
    n = len(old)
    hits = [i for i in range(len(lines) - n + 1) if lines[i:i + n] == old]
    if len(hits) != 1:
        print("ANCHOR HITS", len(hits), path)
        sys.exit(1)
    i = hits[0]
    lines[i:i + n] = new
    out = "\n".join(lines)
    if crlf:
        out = out.replace("\n", "\r\n")
    open(path, "wb").write(out.encode("utf-8"))
    print("PATCHED", path, "line", i + 1, "crlf", crlf)

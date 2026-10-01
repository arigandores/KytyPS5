# F5a2 (HPP-366, ROADMAP s122 item 280(v), (g)): RC1 - recorder ring Record/Finish invariant in Presenter::Present
# under KYTY_FIX_MINIMIZE=1; RC2 - KYTY_TEST_MINIMIZE arms only on a level entry line with a non-blank name.
# Anchors are whole lines; files may be CRLF - strip CR before matching, restore after; write bytes.
import sys
from pathlib import Path

ROOT = Path("C:/kyty/KytyPS5") if len(sys.argv) < 2 else Path(sys.argv[1])
NL = chr(10)


def load(rel):
    raw = (ROOT / rel).read_bytes()
    crlf = b"\r\n" in raw
    return raw.decode("utf-8").replace("\r\n", NL), crlf


def save(rel, text, crlf):
    if crlf:
        text = text.replace(NL, "\r\n")
    (ROOT / rel).write_bytes(text.encode("utf-8"))


def replace_lines(text, old_lines, new_lines, what):
    old = NL.join(old_lines) + NL
    new = NL.join(new_lines) + NL
    n = text.count(old)
    if n != 1:
        sys.exit("anchor %s: %d matches" % (what, n))
    # whole-line anchor: the match must start at a line start
    i = text.find(old)
    if i != 0 and text[i - 1] != NL:
        sys.exit("anchor %s: not at a line start" % what)
    return text.replace(old, new)


T = chr(9)

# ---------------------------------------------------------------- swapchain.cpp (RC1)
rel = "src/graphics/presentation/window/swapchain.cpp"
s, crlf = load(rel)

s = replace_lines(s, [
    T + "const bool screenshot = !preparing && m_impl->screenshot.Poll();",
    T + "if (!preparing) m_impl->input_script.Poll();",
    T + "for (uint32_t attempt = 0; attempt < 2; attempt++) {",
], [
    T + "const bool screenshot = !preparing && m_impl->screenshot.Poll();",
    T + "if (!preparing) m_impl->input_script.Poll();",
    T + "// F5a2 (ROADMAP s122 item 280(g), RC1 of F5b; KYTY_FIX_MINIMIZE=1 only): one call records the frame into the",
    T + "// screenshot/video ring at most once and finishes it exactly once if recorded - on success, or right after a failed",
    T + "// present (its submit was made, the slot gets that tick), so the zero-extent drop and \"retry exhausted\" exits leave",
    T + "// no ring slot pending without a tick.  0 - the old path: Record on every attempt, Finish on success only.",
    T + "const bool fix_minimize = FixMinimizeEnabled();",
    T + "bool       recorded     = false;",
    T + "bool       finished     = false;",
    T + "for (uint32_t attempt = 0; attempt < 2; attempt++) {",
], "loop head")

s = replace_lines(s, [
    T + T + T + "if (screenshot) {",
    T + T + T + T + "m_impl->screenshot.Record(command, frame.image);",
    T + T + T + "}",
], [
    T + T + T + "if (screenshot && !(fix_minimize && recorded)) {",
    T + T + T + T + "m_impl->screenshot.Record(command, frame.image);",
    T + T + T + T + "recorded = true;",
    T + T + T + "}",
], "record")

s = replace_lines(s, [
    T + T + "if (status != Swapchain::Status::Success) {",
    T + T + T + "m_impl->RecoverSwapchain(status);",
    T + T + T + "continue;",
    T + T + "}",
    T + T + "if (screenshot) {",
    T + T + T + "m_impl->screenshot.Finish(frame.present_tick);",
    T + T + "}",
], [
    T + T + "if (status != Swapchain::Status::Success) {",
    T + T + T + "if (fix_minimize && recorded && !finished) { // F5a2 RC1: the recorded slot gets this submit's tick",
    T + T + T + T + "m_impl->screenshot.Finish(frame.present_tick);",
    T + T + T + T + "finished = true;",
    T + T + T + "}",
    T + T + T + "m_impl->RecoverSwapchain(status);",
    T + T + T + "continue;",
    T + T + "}",
    T + T + "if (screenshot && !(fix_minimize && finished)) {",
    T + T + T + "m_impl->screenshot.Finish(frame.present_tick);",
    T + T + "}",
], "present failed / finish")

save(rel, s, crlf)

# ---------------------------------------------------------------- window.cpp (RC2)
rel = "src/graphics/presentation/window/window.cpp"
s, crlf = load(rel)

s = replace_lines(s, [
    '#include "graphics/presentation/window/hostInput.h"',
], [
    '#include "graphics/presentation/window/hostInput.h"',
    '#include "graphics/presentation/window/testMinimizeLine.h"',
], "include")

s = replace_lines(s, [
    "// Track F, F5 (ROADMAP s122 item 273(e)(2), MEASUREMENT ONLY): KYTY_TEST_MINIMIZE=<s>:<dur> - <s> seconds after the",
    "// game's first \"Level has started:\" line the emulator minimizes its own window (SDL_MinimizeWindow on the main thread)",
], [
    "// Track F, F5 (ROADMAP s122 item 273(e)(2), MEASUREMENT ONLY): KYTY_TEST_MINIMIZE=<s>:<dur> - <s> seconds after the",
    "// game's first level entry line \"Level has started: <level>\" with a non-blank level name (F5a2, item 280(v): the",
    "// earlier line with an empty name does not arm; TestMinimizeIsLevelEntry) the emulator minimizes its own window",
    "// (SDL_MinimizeWindow on the main thread)",
], "comment")

s = replace_lines(s, [
    T + "if (std::string_view(text, size).find(\"Level has started: \") == std::string_view::npos ||",
    T + "    armed.exchange(true, std::memory_order_acq_rel)) {",
], [
    T + "if (!TestMinimizeIsLevelEntry(std::string_view(text, size)) ||",
    T + "    armed.exchange(true, std::memory_order_acq_rel)) {",
], "arm")

save(rel, s, crlf)

# ---------------------------------------------------------------- testMinimizeLine.h (new, LF)
rel = "src/graphics/presentation/window/testMinimizeLine.h"
if (ROOT / rel).exists():
    sys.exit(rel + " exists")
h = NL.join([
    "#ifndef EMULATOR_SRC_GRAPHICS_PRESENTATION_WINDOW_TESTMINIMIZELINE_H_",
    "#define EMULATOR_SRC_GRAPHICS_PRESENTATION_WINDOW_TESTMINIMIZELINE_H_",
    "",
    "#include <string_view>",
    "",
    "namespace Libs::Graphics {",
    "",
    "// Track F, F5a2 (ROADMAP s122 item 280(v), RC2 of F5b): true when the guest text holds the level entry line",
    "// \"Level has started: <level>\" - after the prefix, before the end of that line ('\\n' or the end of the text), there is",
    "// a non-blank character.  The game first writes the line with an empty name; that line is not the entry line (item",
    "// 221(v)).  Header-only so that a test can build it without the window code.",
    "inline bool TestMinimizeIsLevelEntry(std::string_view text) {",
    T + "constexpr std::string_view prefix = \"Level has started: \";",
    T + "for (auto pos = text.find(prefix); pos != std::string_view::npos; pos = text.find(prefix, pos + 1)) {",
    T + T + "for (auto i = pos + prefix.size(); i < text.size() && text[i] != '\\n'; i++) {",
    T + T + T + "const char c = text[i];",
    T + T + T + "if (c != ' ' && c != '\\t' && c != '\\r' && c != '\\v' && c != '\\f') {",
    T + T + T + T + "return true;",
    T + T + T + "}",
    T + T + "}",
    T + "}",
    T + "return false;",
    "}",
    "",
    "} // namespace Libs::Graphics",
    "",
    "#endif // EMULATOR_SRC_GRAPHICS_PRESENTATION_WINDOW_TESTMINIMIZELINE_H_",
    "",
])
(ROOT / rel).write_bytes(h.encode("utf-8"))
print("PATCH OK", ROOT)

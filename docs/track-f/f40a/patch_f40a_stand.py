# F40a (HPP-770): stand KYTY_TEST_HIDLOSS edition 2 in window.cpp (ROADMAP s122 item 692(g)(1); docs/track-f/f40a.md
# s0.5-s0.6). The region from the F19c stand comment to the line before the F5 KYTY_TEST_MINIMIZE comment is replaced by
# stand_block.cpp (edition 1 lines kept verbatim where unchanged); ProcessEvent gets the probe intercept, UpdateTitle the
# pad-mode title switch, the includes <algorithm>. Whole-line anchors, each exactly once; LF/CRLF kept.
# Usage: patch_f40a_stand.py <repo root> <stand_block.cpp>
import os
import sys

ROOT = sys.argv[1]
BLOCK = open(sys.argv[2], encoding='utf-8').read().replace('\r\n', '\n')
REL = 'src/graphics/presentation/window/window.cpp'
path = os.path.join(ROOT, REL)
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
text = raw.decode('utf-8').replace('\r\n', '\n')

START = '// Track F, F19c (ROADMAP s122 item 451(c), F19a s4): KYTY_TEST_HIDLOSS=<s>[:<mode>] - stand only, off when unset or\n'
END = '// Track F, F5 (ROADMAP s122 item 273(e)(2), MEASUREMENT ONLY): KYTY_TEST_MINIMIZE=<s>:<dur> - <s> seconds after the\n'
assert text.count(START) == 1 and text.count(END) == 1, 'region anchors'
i, j = text.index(START), text.index(END)
assert i < j
text = text[:i] + BLOCK + text[j:]


def once(old, new):
    global text
    n = text.count(old)
    if n != 1:
        raise SystemExit('ANCHOR x%d: %r' % (n, old[:80]))
    text = text.replace(old, new)


once('#include <atomic>\n#include <chrono>\n',
     '#include <algorithm>\n#include <atomic>\n#include <chrono>\n')
once('static void TestHidLossCount(std::atomic<uint64_t>& counter) {\n'
     '\tif (g_test_hidloss.window.load(std::memory_order_relaxed)) {\n'
     '\t\tcounter.fetch_add(1, std::memory_order_relaxed);\n'
     '\t}\n'
     '}\n',
     'static void TestHidLossCount(std::atomic<uint64_t>& counter) {\n'
     '\tif (g_test_hidloss.window.load(std::memory_order_relaxed)) {\n'
     '\t\tcounter.fetch_add(1, std::memory_order_relaxed);\n'
     '\t}\n'
     '}\n'
     '\n'
     '// Track F, F40a stand KYTY_TEST_HIDLOSS edition 2: the keyboard and pad probes, seen first by ProcessEvent (defined\n'
     '// with the stand, after WindowShutdown).\n'
     'static bool TestHidLossIntercept(const SDL_Event& event);\n')
once('\tEXIT_IF(SDL_GetEventState(SDL_DISPLAYEVENT) != SDL_ENABLE);\n'
     '\tif ((event->type == SDL_KEYDOWN || event->type == SDL_KEYUP) &&\n',
     '\tEXIT_IF(SDL_GetEventState(SDL_DISPLAYEVENT) != SDL_ENABLE);\n'
     '\tif (TestHidLossIntercept(*event)) [[unlikely]] { // Track F, F40a stand edition 2 probes (one relaxed load when off)\n'
     '\t\treturn;\n'
     '\t}\n'
     '\tif ((event->type == SDL_KEYDOWN || event->type == SDL_KEYUP) &&\n')
once('\tconst auto title_t0    = Common::FrameStats::NowNs();\n'
     '\tif (title_async) {\n',
     '\tconst auto title_t0    = Common::FrameStats::NowNs();\n'
     '\tif (TestHidLossTitleOff()) [[unlikely]] {\n'
     '\t\t// Track F, F40a stand KYTY_TEST_HIDLOSS edition 2, mode pad (docs/track-f/f40a.md s0.6): no title post while the\n'
     '\t\t// pad probe window is open - the main thread is woken by the pad events only.\n'
     '\t} else if (title_async) {\n')

if crlf:
    text = text.replace('\n', '\r\n')
open(path, 'wb').write(text.encode('utf-8'))
print('patched', REL, 'crlf' if crlf else 'lf')
print('ALL OK')

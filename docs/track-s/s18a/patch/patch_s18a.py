"""S18a (HPP-642, ROADMAP s122 item 569(d)(1)): default of KYTY_S_REPLAY 0 -> 3.
ShaderReplay::ParseMode: unset or "" -> 3; exactly "0", "1", "2", "3" -> that value; anything else -> 0.
Mode() reads it once per process through ParseMode. Comments by the new meaning; the knob test checks the parse.
Whole-line anchors, CRLF kept as found, LF written for LF files. Usage: python patch_s18a.py <repo root>
"""
import sys

ROOT = sys.argv[1].rstrip('/') + '/'


def patch(rel, pairs):
    path = ROOT + rel
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', '\n')
    for old, new in pairs:
        n = text.count(old)
        if n != 1:
            print('ANCHOR FAIL', rel, n, repr(old[:80]))
            sys.exit(1)
        text = text.replace(old, new)
    if crlf:
        text = text.replace('\n', '\r\n')
    open(path, 'wb').write(text.encode('utf-8'))
    print('patched', rel, 'crlf' if crlf else 'lf')


CPP = 'src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp'
H = 'src/graphics/host_gpu/renderer/pipeline/shaderReplay.h'
PCH = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.h'
T = 'tests/shaderCfgTests.cpp'

patch(CPP, [(
    'int Mode() {\n'
    '\t// Read once per process. Only the exact values "1", "2", "3" turn it on; unset, "", "0" or anything else is 0.\n'
    '\tstatic const int mode = [] {\n'
    '\t\tconst char* value = std::getenv("KYTY_S_REPLAY");\n'
    '\t\tif (value == nullptr || value[0] < \'1\' || value[0] > \'3\' || value[1] != \'\\0\') {\n'
    '\t\t\treturn 0;\n'
    '\t\t}\n'
    '\t\treturn value[0] - \'0\';\n'
    '\t}();\n'
    '\treturn mode;\n'
    '}\n',
    'int ParseMode(const char* value) {\n'
    '\t// Track S, S18a (ROADMAP s122 item 569(d)(1)): unset or "" - 3 (rebuild only, the shipped default); exactly "0",\n'
    '\t// "1", "2" or "3" - that value; anything else - 0 (off).\n'
    '\tif (value == nullptr || value[0] == \'\\0\') {\n'
    '\t\treturn 3;\n'
    '\t}\n'
    '\tif (value[0] < \'0\' || value[0] > \'3\' || value[1] != \'\\0\') {\n'
    '\t\treturn 0;\n'
    '\t}\n'
    '\treturn value[0] - \'0\';\n'
    '}\n'
    '\n'
    'int Mode() {\n'
    '\t// Read once per process (ParseMode).\n'
    '\tstatic const int mode = ParseMode(std::getenv("KYTY_S_REPLAY"));\n'
    '\treturn mode;\n'
    '}\n')])

patch(H, [(
    '// Knob KYTY_S_REPLAY (read once per process): 0 (default; unset, "" or 0) - off: no file, no "ShaderReplay:" line, no\n'
    '// writer thread; 1 - capture and rebuild; 2 - capture only; 3 - rebuild only. Stands KYTY_S_REPLAY_TEST=canon|spec|addr|\n'
    '// stop|corrupt (positive controls of members K3, K4, K6).\n',
    '// Knob KYTY_S_REPLAY (read once per process): 0 (exactly "0", or any value other than "0".."3") - off: no file, no\n'
    '// "ShaderReplay:" line, no writer thread; 1 - capture and rebuild; 2 - capture only; 3 (the default since S18a, ROADMAP\n'
    '// s122 item 569(d)(1): unset or "") - rebuild only. Stands KYTY_S_REPLAY_TEST=canon|spec|addr|stop|corrupt (positive\n'
    '// controls of members K3, K4, K6).\n'), (
    '// 0, 1, 2, 3 (see above); any other value of the variable reads as 0.\n'
    'int  Mode();\n',
    '// 0, 1, 2, 3 (see above): unset or "" reads as 3; exactly "0", "1", "2", "3" as is; any other value reads as 0.\n'
    'int  ParseMode(const char* value);\n'
    'int  Mode();\n')])

patch(PCH, [(
    '\t// Track S, S17a (HPP-611, ROADMAP s122 item 524; shaderReplay.h): S-replay under KYTY_S_REPLAY. At 0 (the default)\n'
    '\t// ReplayInit returns at once: every member below stays empty, null or false.\n',
    '\t// Track S, S17a (HPP-611, ROADMAP s122 item 524; shaderReplay.h): S-replay under KYTY_S_REPLAY (default 3 since S18a,\n'
    '\t// item 569(d)(1)). At 0 ReplayInit returns at once: every member below stays empty, null or false.\n')])

patch(T, [(
    '  // The knob is off by default (the test runs without KYTY_S_REPLAY).\n'
    '  if (std::getenv("KYTY_S_REPLAY") == nullptr) {\n'
    '    Check(SR::Mode() == 0 && !SR::CaptureOn() && !SR::RebuildOn(), "replay knob default 0");\n'
    '  }\n',
    '  // Track S, S18a (ROADMAP s122 item 569(d)(1)): unset or "" - 3 (rebuild only); exactly "0".."3" - as is; else 0.\n'
    '  Check(SR::ParseMode(nullptr) == 3 && SR::ParseMode("") == 3, "replay knob default 3");\n'
    '  Check(SR::ParseMode("0") == 0 && SR::ParseMode("1") == 1 && SR::ParseMode("2") == 2 && SR::ParseMode("3") == 3,\n'
    '        "replay knob exact values");\n'
    '  Check(SR::ParseMode("4") == 0 && SR::ParseMode("9") == 0 && SR::ParseMode("/") == 0 && SR::ParseMode("00") == 0 &&\n'
    '            SR::ParseMode("3 ") == 0 && SR::ParseMode(" 3") == 0 && SR::ParseMode("-1") == 0 &&\n'
    '            SR::ParseMode("true") == 0 && SR::ParseMode("on") == 0 && SR::ParseMode("off") == 0,\n'
    '        "replay knob other values 0");\n'
    '  // The test runs without KYTY_S_REPLAY: the process reads the default.\n'
    '  if (std::getenv("KYTY_S_REPLAY") == nullptr) {\n'
    '    Check(SR::Mode() == 3 && !SR::CaptureOn() && SR::RebuildOn(), "replay knob default 3 in the process");\n'
    '  }\n')])
print('ALL PATCHED')

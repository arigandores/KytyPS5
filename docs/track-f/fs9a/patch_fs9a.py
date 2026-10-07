"""Track F link FS9a (HPP-671, ROADMAP s122 item 604(d)(1)): default of KYTY_FIX_B13 0 -> 1 in the form of FS4a 17adaf80
(unset or "" - ON, otherwise Common::EnvValueOn), the one read in FixB13Enabled (static const) kept; the stand comments that
named "unset" as the order of =0 and N4 of item 603(b)(4) (line 6: KYTY_B13_TEST_HOOK -> KYTY_TEST_B13_HOOK). The line
"FixB13: mode=", the =1 and else branches and the test-build hooks are not touched.
Anchors are whole lines, each must occur exactly once; CR is stripped before the search and restored if the file had it;
output is written with write_bytes.

    python patch_fs9a.py <repo or worktree root>
"""
import sys

ROOT = sys.argv[1].rstrip('/\\')

EDITS = {
    'src/graphics/host_gpu/regionManager.h': [
        (
            [
                '// Track F, F24c (HPP-662, ROADMAP s122 item 595(d)): knob KYTY_FIX_B13, default 0 (unset or "" - off, otherwise',
                '// Common::EnvValueOn), read once per process. At 1 RegionManager::ChangeState<Cpu, true> publishes the region epoch and the',
                '// bdabits bit BEFORE the global CPU epoch (B13: with the global epoch first, a BDA scan that read the new global epoch could',
                '// read the old region stamp, skip the region and remember the new global epoch). The constructor of MemoryTracker reads it',
                '// before any region exists and prints "FixB13: mode=<0|1>" once per process.',
                '[[nodiscard]] inline bool FixB13Enabled() noexcept {',
                '\tstatic const bool on = Common::EnvValueOn(std::getenv("KYTY_FIX_B13"));',
                '\treturn on;',
                '}',
            ],
            [
                '// Track F, F24c (HPP-662, ROADMAP s122 item 595(d)): knob KYTY_FIX_B13, read once per process. At 1',
                '// RegionManager::ChangeState<Cpu, true> publishes the region epoch and the bdabits bit BEFORE the global CPU epoch (B13: with',
                '// the global epoch first, a BDA scan that read the new global epoch could read the old region stamp, skip the region and',
                '// remember the new global epoch). The constructor of MemoryTracker reads it before any region exists and prints',
                '// "FixB13: mode=<0|1>" once per process.',
                '// Track F, FS9a (HPP-671, ROADMAP s122 item 604(d)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any other',
                '// value as EnvValueOn (the form of FS4a 17adaf80).',
                '[[nodiscard]] inline bool FixB13Enabled() noexcept {',
                '\tstatic const bool on = [] {',
                '\t\tconst char* value = std::getenv("KYTY_FIX_B13");',
                '\t\treturn value == nullptr || value[0] == \'\\0\' || Common::EnvValueOn(value);',
                '\t}();',
                '\treturn on;',
                '}',
            ],
        ),
    ],
    'tests/B13EpochStand.cpp': [
        (
            ['// region lock, on a page of real memory. The test-build hook KYTY_B13_TEST_HOOK(point) of regionManager.h calls Hook()'],
            ['// region lock, on a page of real memory. The test-build hook KYTY_TEST_B13_HOOK(point) of regionManager.h calls Hook()'],
        ),
        (
            [
                '// test (read once per process): at 0 or unset the writer is the text of F24a (points 1 and 2; the swap target - the',
            ],
            [
                '// test (read once per process; unset = 1 since FS9a, ROADMAP s122 item 604(d)(1)): at 0 the writer is the text of F24a',
                '// (points 1 and 2; the swap target - the',
            ],
        ),
        (
            ['//   point 1 or 2 (KYTY_FIX_B13=0 or unset) or 11, 12, 13 (KYTY_FIX_B13=1), bits 0 or 1 (the reader with or without the bdabits map).'],
            ['//   point 1 or 2 (KYTY_FIX_B13=0) or 11, 12, 13 (KYTY_FIX_B13=1 or unset), bits 0 or 1 (the reader with or without the bdabits map).'],
        ),
    ],
}


def find_block(lines, block):
    hits = [i for i in range(len(lines) - len(block) + 1) if lines[i:i + len(block)] == block]
    return hits


ok = True
for rel, edits in EDITS.items():
    path = ROOT + '/' + rel
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    lines = raw.decode('utf-8').replace('\r\n', '\n').split('\n')
    for old, new in edits:
        hits = find_block(lines, old)
        if len(hits) != 1:
            print('ANCHOR %s: %d hits for %r' % (rel, len(hits), old[0]))
            ok = False
            continue
        i = hits[0]
        lines[i:i + len(old)] = new
        print('edit %s:%d  -%d +%d' % (rel, i + 1, len(old), len(new)))
    if ok:
        text = '\n'.join(lines)
        if crlf:
            text = text.replace('\n', '\r\n')
        open(path, 'wb').write(text.encode('utf-8'))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)

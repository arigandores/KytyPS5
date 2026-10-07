"""Track F link F24c (HPP-662, ROADMAP s122 item 595(d)): the code of KYTY_FIX_B13 - the order of the epochs of
RegionManager::ChangeState<Cpu, true> - and the stand points of the =1 order. Applied to a source root (the main repository
or a worktree); every anchor is a whole line and must occur exactly once; files keep their line ends (CR is stripped
before the search and put back). Writes LF bytes for LF files.

    python patch_f24c.py <root>
"""
import sys

ROOT = sys.argv[1].rstrip('/\\')
TAB = '\t'


def load(rel):
    raw = open(ROOT + '/' + rel, 'rb').read()
    crlf = b'\r\n' in raw
    return raw.decode('utf-8').replace('\r\n', '\n'), crlf


def save(rel, text, crlf):
    if crlf:
        text = text.replace('\n', '\r\n')
    open(ROOT + '/' + rel, 'wb').write(text.encode('utf-8'))


def one_line(lines, line, what):
    hits = [i for i, l in enumerate(lines) if l == line]
    if len(hits) != 1:
        sys.exit('anchor %s: %d hits' % (what, len(hits)))
    return hits[0]


# ---------------------------------------------------------------- regionManager.h
RM = 'src/graphics/host_gpu/regionManager.h'
text, crlf = load(RM)
L = text.split('\n')

i = one_line(L, '#include "common/diagB32.h" // Track F, F20j3 (KYTY_DIAG_B32, ROADMAP s122 item 574(g))', 'include')
L.insert(i + 1, '#include "common/envFlag.h"')

i = one_line(L, '// reversed order (KYTY_TEST_B13_SWAP) are inside #if blocks, so the emulator compiles the text before F24a.', 'hook comment')
L[i + 1:i + 1] = [
    '// Track F, F24c (HPP-662, ROADMAP s122 item 595(d)): the order of KYTY_FIX_B13=1 has its own points - 11 after the region',
    '// epoch, 12 after the bdabits bit, 13 after the global epoch; points 1 and 2 belong to the order of KYTY_FIX_B13=0.',
]

i = one_line(L, '} // namespace B13Test', 'hook namespace end')
if L[i + 1] != '#endif':
    sys.exit('hook #endif not found')
L[i + 2:i + 2] = [
    '',
    '// Track F, F24c (HPP-662, ROADMAP s122 item 595(d)): knob KYTY_FIX_B13, default 0 (unset or "" - off, otherwise',
    '// Common::EnvValueOn), read once per process. At 1 RegionManager::ChangeState<Cpu, true> publishes the region epoch and the',
    '// bdabits bit BEFORE the global CPU epoch (B13: with the global epoch first, a BDA scan that read the new global epoch could',
    '// read the old region stamp, skip the region and remember the new global epoch). The constructor of MemoryTracker reads it',
    '// before any region exists and prints "FixB13: mode=<0|1>" once per process.',
    '[[nodiscard]] inline bool FixB13Enabled() noexcept {',
    TAB + 'static const bool on = Common::EnvValueOn(std::getenv("KYTY_FIX_B13"));',
    TAB + 'return on;',
    '}',
]

T2, T3, T4 = TAB * 2, TAB * 3, TAB * 4
start = one_line(L, T3 + '// Called with the region lock held, after the bits and before the pages become', 'site comment') - 1
if L[start] != T2 + 'if constexpr (source == DirtySource::Cpu && enable) {':
    sys.exit('site if-line not found')
end = start + 1
while L[end] != T2 + '}':
    end += 1
body = L[start + 1:end]  # the text of =0, verbatim
need = [T3 + 'm_cpu_epoch.fetch_add(1, std::memory_order_release);', T3 + 'm_epoch.fetch_add(1, std::memory_order_release);',
        T3 + 'BdaNoteRegionWrite(m_cpu_addr / TRACKER_REGION_SIZE);', '#if defined(KYTY_TEST_B13_SWAP)']
if len(body) != 28 or any(n not in body for n in need):
    sys.exit('site body is not the text of F24a (%d lines)' % len(body))
new = [
    T2 + 'if constexpr (source == DirtySource::Cpu && enable) {',
    T3 + 'if (FixB13Enabled()) {',
    T4 + '// Track F, F24c (KYTY_FIX_B13=1, ROADMAP s122 item 595(d)). Called with the region lock held, after the bits and',
    T4 + '// before the pages become writable (UpdateProtection below). Bits first; then the witnesses of this region - its',
    T4 + '// epoch, then the bdabits bit - and the global CPU epoch LAST. A lock-free reader of the bits (gate "syncfree")',
    T4 + '// takes its epoch snapshot before it reads them, so an announcement it missed moves the epochs after that snapshot',
    T4 + '// and the next HasCurrentUpload check fails (either kind of epoch). The BDA preparation decides "skip this region"',
    T4 + '// WITHOUT this lock: RenderContext::PrepareBda reads the global epoch (acquire) before its scan and remembers it',
    T4 + '// after it, and the scan skips a region by a clear bdabits bit or an unchanged stamp',
    T4 + '// (BufferCache::SynchronizeBuffersByRegion). The release store of the global epoch publishes the region epoch and',
    T4 + '// the bit stored before it: a scan that reads the new global epoch sees both and walks the region; a scan that reads',
    T4 + '// the old one remembers the old one, and the move it missed sends the next preparation back to the region.',
    T4 + 'm_epoch.fetch_add(1, std::memory_order_release);',
    '#if defined(KYTY_TEST_B13_HOOK)',
    T4 + 'B13Test::Hook(11); // Track F, F24c: after the region epoch, before the bdabits bit',
    '#endif',
    T4 + '// Gate "bdabits": the map mirrors this epoch, so it is set here - before the global epoch, never later.',
    T4 + 'BdaNoteRegionWrite(m_cpu_addr / TRACKER_REGION_SIZE);',
    '#if defined(KYTY_TEST_B13_HOOK)',
    T4 + 'B13Test::Hook(12); // Track F, F24c: after the bdabits bit, before the global epoch',
    '#endif',
    T4 + 'm_cpu_epoch.fetch_add(1, std::memory_order_release);',
    '#if defined(KYTY_TEST_B13_HOOK)',
    T4 + 'B13Test::Hook(13); // Track F, F24c: after the global epoch',
    '#endif',
    T4 + '// Session 134, knob "b2reuse" (ROADMAP s122 item 154(b) RC1): an announced CPU write ends the interval at 1/2 -',
    T4 + '// after the epochs, before UpdateProtection lets the guest write; any thread, under this region\'s lock.',
    T4 + 'if (Common::B2Reuse::ResetsLive()) [[unlikely]] {',
    T4 + TAB + 'Common::B2Reuse::ResetCpu(Common::FrameStats::Counter::B2rRstCpuw);',
    T4 + '}',
    T3 + '} else {',
    T3 + TAB + '// Track F, F24c: KYTY_FIX_B13=0 - the text before F24c, verbatim (its last comment sentence holds for the',
    T3 + TAB + '// dirty bits read under this lock, not for the lock-free skip of the BDA scan - B13, ROADMAP s122 item 595(v)(2)).',
] + [(l if l.startswith('#') or l == '' else TAB + l) for l in body] + [
    T3 + '}',
    T2 + '}',
]
L[start:end + 1] = new
save(RM, '\n'.join(L), crlf)
print('patched', RM)

# ---------------------------------------------------------------- memoryTracker.cpp
MC = 'src/graphics/host_gpu/memoryTracker.cpp'
text, crlf = load(MC)
L = text.split('\n')
i = one_line(L, '#include "common/assert.h"', 'mc include')
L.insert(i + 1, '#include "common/logging/log.h"')
i = one_line(L, TAB + 's_primary.compare_exchange_strong(expected, this, std::memory_order_acq_rel);', 'mc ctor')
if L[i + 1] != '}':
    sys.exit('mc ctor end not found')
L[i + 1:i + 1] = [
    TAB + '// Track F, F24c (KYTY_FIX_B13, ROADMAP s122 item 595(d)): the knob is read here, before this tracker has a region (no',
    TAB + '// ChangeState of it can run earlier), and its line is printed once per process.',
    TAB + 'static std::atomic<bool> fix_b13_logged {false};',
    TAB + 'const bool               fix_b13 = FixB13Enabled();',
    TAB + 'if (!fix_b13_logged.exchange(true, std::memory_order_relaxed)) {',
    TAB * 2 + 'LOGF("FixB13: mode=%d\\n", fix_b13 ? 1 : 0);',
    TAB + '}',
]
save(MC, '\n'.join(L), crlf)
print('patched', MC)

# ---------------------------------------------------------------- tests/B13EpochStand.cpp
ST = 'tests/B13EpochStand.cpp'
text, crlf = load(ST)
L = text.split('\n')
i = one_line(L, '// b13_epoch_stand builds the order of the code, b13_epoch_stand_swap (KYTY_TEST_B13_SWAP) the reversed order.', 'st header')
L[i + 1:i + 1] = [
    '// Track F, F24c (HPP-662, ROADMAP s122 item 595(e)(1)): the same targets with the knob KYTY_FIX_B13 of the code under',
    '// test (read once per process): at 0 or unset the writer is the text of F24a (points 1 and 2; the swap target - the',
    '// reversed order); at 1 it is the order of the fix - region epoch, point 11, bdabits bit, point 12, global epoch, point 13',
    '// (the swap target has the same =1 order). A point of the other value of the knob is refused (exit 2): it is never reached.',
]
i = one_line(L, '//   point 1 or 2, bits 0 or 1 (the reader with or without the bdabits map).', 'st usage')
L[i] = '//   point 1 or 2 (KYTY_FIX_B13=0 or unset) or 11, 12, 13 (KYTY_FIX_B13=1), bits 0 or 1 (the reader with or without the bdabits map).'
i = one_line(L, '// Output: one line "B13 build=<code|swap> mode=... point=... bits=... iters=<n> lost=<n> r1=... r2=..." and exit 0;', 'st output')
L[i] = '// Output: one line "B13 build=<code|swap> fix_b13=<0|1> mode=... point=... bits=... iters=<n> lost=<n> r1=... r2=..." and exit 0;'
i = one_line(L, TAB * 2 + 'std::printf("usage: b13_epoch_stand <forced|free|before|after> <1|2> <0|1> <iters>\\n");', 'st usage print')
L[i] = TAB * 2 + 'std::printf("usage: b13_epoch_stand <forced|free|before|after> <1|2|11|12|13> <0|1> <iters>\\n");'
i = one_line(L, TAB + 'if ((!forced && !free_mode && !before && !after) || (point != 1 && point != 2) || iters == 0) {', 'st check')
L[i:i + 1] = [
    TAB + '// Track F, F24c: the points of the order the knob selects (Libs::Graphics::FixB13Enabled, the read of the code).',
    TAB + 'const bool     fix_b13  = Libs::Graphics::FixB13Enabled();',
    TAB + 'const bool     point_ok = fix_b13 ? (point == 11 || point == 12 || point == 13) : (point == 1 || point == 2);',
    TAB + 'if ((!forced && !free_mode && !before && !after) || !point_ok || iters == 0) {',
]
i = one_line(L, TAB + 'std::printf("B13 build=%s mode=%s point=%d bits=%d iters=%llu lost=%llu r1=%s:%llu,%s:%llu,%s:%llu,%s:%llu "', 'st printf')
L[i] = TAB + 'std::printf("B13 build=%s fix_b13=%d mode=%s point=%d bits=%d iters=%llu lost=%llu r1=%s:%llu,%s:%llu,%s:%llu,%s:%llu "'
i = one_line(L, TAB + ' ' * 12 + 'build, mode, point, bits ? 1 : 0, static_cast<unsigned long long>(iters),', 'st printf args')
L[i] = TAB + ' ' * 12 + 'build, fix_b13 ? 1 : 0, mode, point, bits ? 1 : 0, static_cast<unsigned long long>(iters),'
save(ST, '\n'.join(L), crlf)
print('patched', ST)
print('PATCH OK')

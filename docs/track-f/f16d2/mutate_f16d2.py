# Track F, F16d2 (HPP-569, ROADMAP s122 item 470(v)(3)-(5)): mutants of the F16d2 code in the worktree
# C:/kyty/f287/f16d2/wt (whole-line anchors, each exactly once; CR stripped and restored; write_bytes).
# Usage: mutate_f16d2.py <name> <apply|revert>
#  Ma1  - form (a): the flip tick prints the line itself (print from the vblank thread): TickAt publishes and serves.
#  Ma1w - the same only when the tick runs on a thread other than the first one that ticked (the test site's main thread
#         ticks first): only the window ticks of the hook print - isolates the case "tick between parent and child".
#  Ma2  - the service runs inside the window: Add serves right after the increment (a service point inside a site).
#  M4   - F16e: NoteDraw classes an export into a slot "mask on, base 0" by the inverted format test (diagF5.cpp:334 of
#         381aa80a).
#  M5   - RC2: NoteDraw classes a slot "mask on, base 0" by the inverted format test (fmt_on in diagF5.cpp:301 of 381aa80a).
#  M3   - F16e: the cmask_fce None branch counts an MSAA target as cmask_fce_nofill.
#  mut1 - F16d: the dcc_rt_skip_levels site writes dcc_rt_skip_partial.
#  mut2 - F16d: the dcc_mat_pending site is not under On().
import sys

WT = 'C:/kyty/f287/f16d2/wt/'
NL = chr(10)
C = 'src/graphics/host_gpu/renderer/diagF5.cpp'
MUT = {
    'Ma1': [(C, '	return PublishSet(On(), F5(), frame, now_ms);',
             '	return PublishSet(On(), F5(), frame, now_ms) && ServiceSet(On(), "DiagF5", F5(), F5Names); // MUTANT Ma1'),
            (C, '	return PublishSet(On(), F6(), frame, now_ms);',
             '	return PublishSet(On(), F6(), frame, now_ms) && ServiceSet(On(), "DiagF6", F6(), F6Names); // MUTANT Ma1')],
    'Ma1w': [(C, '#include <mutex>', '#include <mutex>' + NL + '#include <thread> // MUTANT Ma1w'),
             (C, '	return PublishSet(On(), F5(), frame, now_ms);',
              '	static const auto first = std::this_thread::get_id(); const bool published = PublishSet(On(), F5(), frame, now_ms);'
              ' if (std::this_thread::get_id() != first) { (void)ServiceSet(On(), "DiagF5", F5(), F5Names); } return published; // MUTANT Ma1w'),
             (C, '	return PublishSet(On(), F6(), frame, now_ms);',
              '	static const auto first = std::this_thread::get_id(); const bool published = PublishSet(On(), F6(), frame, now_ms);'
              ' if (std::this_thread::get_id() != first) { (void)ServiceSet(On(), "DiagF6", F6(), F6Names); } return published; // MUTANT Ma1w')],
    'Ma2': [(C, '	F5().counters[index].fetch_add(1, std::memory_order_relaxed);',
             '	F5().counters[index].fetch_add(1, std::memory_order_relaxed); if (g_window_hook != nullptr) { g_window_hook(5, index); }'
             ' (void)ServiceSet(On(), "DiagF5", F5(), F5Names); return; // MUTANT Ma2')],
    'M4': [(C, '				inc(fmt_on[index] ? Counter::WAddr0Fmt : Counter::WAddr0NoFmt);',
            '				inc(!fmt_on[index] ? Counter::WAddr0Fmt : Counter::WAddr0NoFmt); // MUTANT M4')],
    'M5': [(C, '			inc(base_on[slot] ? Counter::SBound : fmt_on[slot] ? Counter::SAddr0Fmt : Counter::SAddr0NoFmt);',
            '			inc(base_on[slot] ? Counter::SBound : !fmt_on[slot] ? Counter::SAddr0Fmt : Counter::SAddr0NoFmt); // MUTANT M5')],
    'M3': [('src/graphics/host_gpu/renderer/pipeline/descriptors.cpp',
            '				            : f5_info.samples != 1                             ? DiagF5::Counter::CmaskFceMsaa',
            '				            : f5_info.samples != 1                             ? DiagF5::Counter::CmaskFceNoFill // MUTANT M3')],
    'mut1': [('src/graphics/host_gpu/renderer/cache/textureCache.cpp',
              '			DiagF5::Add(image.info.resources.levels != 1 ? DiagF5::Counter::DccRtSkipLevels',
              '			DiagF5::Add(image.info.resources.levels != 1 ? DiagF5::Counter::DccRtSkipPartial // MUTANT mut1')],
    'mut2': [('src/graphics/host_gpu/renderer/pipeline/descriptors.cpp',
              '		DiagF5::Add(DiagF5::Counter::DccMatPending); // Track F, F16d (item 427(b), RC4): a pending layer mask',
              '	}' + NL + '	{ // MUTANT mut2' + NL +
              '		DiagF5::Add(DiagF5::Counter::DccMatPending); // Track F, F16d (item 427(b), RC4): a pending layer mask')],
}


def main():
    name, action = sys.argv[1], sys.argv[2]
    for path, old, new in MUT[name]:
        if action == 'revert':
            old, new = new, old
        raw = open(WT + path, 'rb').read()
        crlf = b'\r\n' in raw
        text = raw.decode('utf-8').replace('\r\n', NL)
        n = text.count(NL + old + NL)
        if n != 1:
            print('anchor hits', n, 'for', name, action, path)
            return 1
        text = text.replace(NL + old + NL, NL + new + NL)
        if crlf:
            text = text.replace(NL, '\r\n')
        open(WT + path, 'wb').write(text.encode('utf-8'))
        print(name, action, path)
    return 0


sys.exit(main())

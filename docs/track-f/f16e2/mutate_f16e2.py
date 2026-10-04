# Track F, F16e2 (HPP-570, Red Team; ROADMAP s122 item 470(d)): own mutants of the F16d2 code (56b04817) in the review
# worktree C:/kyty/f287/f16e2/wt (whole-line anchors, each exactly once; CR stripped and restored; write_bytes).
# Usage: mutate_f16e2.py <name> <apply|revert>
#  R1 - item 470(v)(3), form (a), "print from the vblank thread": DiagF6::TickAt serves (prints) when it finds an older
#       request still pending - i.e. only on the 2nd and later ticks between two services (the window ticks of NoteDraw).
#  R2 - a service point inside the NoteDraw window (Ma2 class, other site, BEFORE the hook): NoteDraw serves right after
#       each fetch_add, before the window hook runs.
#  R3 - item 470(v)(4): the export class "mask on, base 0" by the inverted format test, written as swapped enum targets.
#  R4 - item 470(v)(4): the slot class "mask on, base 0" by the inverted format test, written as swapped enum targets.
#  R5 - item 470(v)(4): the inversion at the source - fmt_on itself is "format == 0" (slots and exports together).
import sys

WT = 'C:/kyty/f287/f16e2/wt/'
NL = chr(10)
C = 'src/graphics/host_gpu/renderer/diagF5.cpp'
MUT = {
    'R1': [(C, '	return PublishSet(On(), F6(), frame, now_ms);',
            '	bool pend = false; { std::scoped_lock l {F6().request_mutex}; pend = F6().has_request; }'
            ' const bool p = PublishSet(On(), F6(), frame, now_ms);'
            ' if (pend) { (void)ServiceSet(On(), "DiagF6", F6(), F6Names); } return p; // MUTANT R1')],
    'R2': [(C, '			set.counters[i].fetch_add(add[i], std::memory_order_relaxed);',
            '			set.counters[i].fetch_add(add[i], std::memory_order_relaxed);'
            ' (void)ServiceSet(true, "DiagF6", set, F6Names); // MUTANT R2')],
    'R3': [(C, '				inc(fmt_on[index] ? Counter::WAddr0Fmt : Counter::WAddr0NoFmt);',
            '				inc(fmt_on[index] ? Counter::WAddr0NoFmt : Counter::WAddr0Fmt); // MUTANT R3')],
    'R4': [(C, '			inc(base_on[slot] ? Counter::SBound : fmt_on[slot] ? Counter::SAddr0Fmt : Counter::SAddr0NoFmt);',
            '			inc(base_on[slot] ? Counter::SBound : fmt_on[slot] ? Counter::SAddr0NoFmt : Counter::SAddr0Fmt); // MUTANT R4')],
    'R5': [(C, '		fmt_on[slot]   = static_cast<uint32_t>(rt.info.format) != 0; // raw CB_COLORn_INFO.FORMAT (pm4Handlers.cpp)',
            '		fmt_on[slot]   = static_cast<uint32_t>(rt.info.format) == 0; // MUTANT R5')],
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

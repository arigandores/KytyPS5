"""Add opt-in, read-only texture GC audit. No cache policy changes. Run --test-only offline."""
from pathlib import Path
import argparse
import itertools

ROOT = Path('C:/kyty/KytyPS5')

def replace_once(text, old, new):
    assert text.count(old) == 1, (old[:100], text.count(old))
    return text.replace(old, new, 1)

def patched_sources():
    paths = [
        'src/graphics/host_gpu/renderer/cache/textureCache.cpp',
        'src/common/frameStats.h',
        'src/graphics/presentation/videoOut.cpp',
        'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp',
        'src/graphics/host_gpu/renderer/pipeline/descriptors.h',
    ]
    originals = {p: (ROOT / p).read_bytes() for p in paths}
    texts = {p: b.decode('utf-8').replace('\r\n', '\n') for p, b in originals.items()}
    p = paths[0]
    texts[p] = replace_once(texts[p], '\tconst bool floor_hold = BindFloorGcHold();\n\tuint64_t   tick       = floor_hold ? m_gc_tick : m_gc_tick++;', '''\t// Session 99: observe the existing per-CALL age clock; never adopt a latch or change GC.
\tstatic const bool gc_audit = [] {
\t\tconst auto* value = std::getenv("KYTY_BIND_FLOOR_GC_AUDIT");
\t\tconst bool on = value != nullptr && value[0] == '1' && value[1] == '\\0';
\t\tLOGF("BindFloorGcAudit: mode%u\\n", on ? 1u : 0u);
\t\treturn on;
\t}();
\tconst uint64_t audit_tick_before = gc_audit ? m_gc_tick : 0;
\tconst bool floor_hold = BindFloorGcHold();
\t// The current submission's counted sticky value is a valid independent SUBSET of hold.
\t// Unlike CurrentOp (stale outside operations), it expires with the submission. It does
\t// NOT independently prove the base/pending parts of BindFloorGcHold.
\tconst bool audit_sticky = gc_audit && BindFloorGcAuditSticky();
\tconst bool audit_expected_hold = gc_audit && (floor_hold || audit_sticky);
\tconst auto audit_clock = [&](bool critical_override) {
\t\tif (!gc_audit) return;
\t\tusing Counter = Common::FrameStats::Counter;
\t\tconst uint64_t expected_delta = audit_expected_hold && !critical_override ? 0u : 1u;
\t\tconst bool bad = (audit_sticky && !floor_hold) || m_gc_tick < audit_tick_before ||
\t\t                 m_gc_tick - audit_tick_before != expected_delta;
\t\tCommon::FrameStats::Add(Counter::BindFloorImgGcChecks, 1);
\t\tCommon::FrameStats::Add(Counter::BindFloorImgGcHold,
\t\t                       audit_expected_hold && !critical_override ? 1u : 0u);
\t\tCommon::FrameStats::Add(Counter::BindFloorImgGcBad, bad ? 1u : 0u);
\t\tCommon::FrameStats::Add(Counter::BindFloorImgGcCritical,
\t\t                       audit_expected_hold && critical_override ? 1u : 0u);
\t};
\tuint64_t   tick       = floor_hold ? m_gc_tick : m_gc_tick++;''')
    texts[p] = replace_once(texts[p], '\tif (m_total_used_memory < m_trigger_gc_memory) {\n\t\treturn;\n\t}', '\tif (m_total_used_memory < m_trigger_gc_memory) {\n\t\taudit_clock(false);\n\t\treturn;\n\t}')
    texts[p] = replace_once(texts[p], '\t\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::BindFloorGcHold, 1);\n\t\t\treturn;', '\t\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::BindFloorGcHold, 1);\n\t\t\taudit_clock(false);\n\t\t\treturn;')
    texts[p] = replace_once(texts[p], '\t\ttick = m_gc_tick++;\n\t}\n\tconst auto collect =', '''\t\ttick = m_gc_tick++;
\t}
\t// Pressure is sampled before collection mutates accounting, not inferred from age delta.
\taudit_clock(m_total_used_memory >= m_critical_gc_memory);
\tconst auto collect =''')
    texts[p] = replace_once(texts[p], '\t\t\tFreeImage(id, __func__, __LINE__);\n\t\t\tif (m_total_used_memory < m_critical_gc_memory && aggressive)', '''\t\t\tif (audit_expected_hold) {
\t\t\t\t// Counts GC root victims, including critical collection; recursive stencil
\t\t\t\t// children are not counted twice. Every such cascade has a counted root.
\t\t\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::BindFloorImgGcEvict, 1);
\t\t\t}
\t\t\tFreeImage(id, __func__, __LINE__);
\t\t\tif (m_total_used_memory < m_critical_gc_memory && aggressive)''')
    p = paths[1]
    texts[p] = replace_once(texts[p], '\tBindFloorGcHold,   // bf_gc_hold', '''\t// Session 99: opt-in texture GC mechanism audit, both arms, per GC call.
\t// Hold predicate = normal helper OR current submission's counted sticky armed value;
\t// the latter is only an independent subset, not a proof of base/pending state.
\tBindFloorImgGcChecks,   // bf_igc_checks: observed clock transitions (also below trigger)
\tBindFloorImgGcHold,     // bf_igc_hold: expected paused transitions, excluding critical
\tBindFloorImgGcBad,      // bf_igc_bad: wrong clock delta OR sticky subset missed by helper
\tBindFloorImgGcCritical, // bf_igc_critical: expected hold but critical override permitted
\tBindFloorImgGcEvict,    // bf_igc_evict: GC root evictions under expected hold, critical too
\tBindFloorGcHold,   // bf_gc_hold''')
    p = paths[2]
    needle = '\t\t\t\t    {"bf_gc_hold", FS::Counter::BindFloorGcHold, false},'
    rows = [('bf_igc_checks', 'Checks'), ('bf_igc_hold', 'Hold'), ('bf_igc_bad', 'Bad'), ('bf_igc_critical', 'Critical'), ('bf_igc_evict', 'Evict')]
    added = '\n'.join(f'\t\t\t\t    {{"{name}", FS::Counter::BindFloorImgGc{suffix}, false}},' for name, suffix in rows)
    texts[p] = replace_once(texts[p], needle, needle + '\n' + added)
    p = paths[3]
    texts[p] = replace_once(texts[p], 'bool BindFloorGcHold() {', '''bool BindFloorGcAuditSticky() {
\t// Read-only independent subset: a current submission with a counted armed sticky
\t// value must be held by GC. Process runs GC before SliceComplete removes its count.
\t// No CurrentOp read (it can outlive a submission), live gate read, or latch adoption.
\treturn t_bf_slice != nullptr && t_bf_slice->sticky_armed_counted;
}

bool BindFloorGcHold() {''')
    p = paths[4]
    texts[p] = replace_once(texts[p], '[[nodiscard]] bool BindFloorGcHold();', '''[[nodiscard]] bool BindFloorGcHold();
// Session 99 audit only: read current submission's counted sticky armed value, without
// adopting/reading a live gate. Independent subset of GcHold; base/pending are NOT witnessed.
[[nodiscard]] bool BindFloorGcAuditSticky();''')
    return originals, texts

def tests():
    # Model original early-return control flow separately from the audit's arithmetic oracle.
    # Memory classes cover below-trigger, noncritical and critical routes; frame count is
    # intentionally absent: the real GC clock advances per invocation, not per presentation.
    def original(hold, memory, before, mutation=None):
        tick = before
        if not hold or mutation == 'freeze_off':
            tick += 1
        if memory == 'below':
            return tick, False, 1
        if hold:
            if memory != 'critical':
                return tick, False, 1
            tick += 1
        if mutation == 'release_catchup' and not hold:
            tick += 90
        return tick, memory == 'critical', 1

    def audit(hold, sticky, critical, before, after):
        expected_hold = hold or sticky
        expected_delta = 0 if expected_hold and not critical else 1
        return (sticky and not hold) or after < before or after - before != expected_delta

    n = 0
    for hold, memory, before in itertools.product([False, True], ['below', 'normal', 'critical'], [0, 17, 1800]):
        after, critical, visits = original(hold, memory, before)
        assert visits == 1 and not audit(hold, hold, critical, before, after)
        n += 1
    for memory in ['below', 'normal', 'critical']:
        after, critical, _ = original(True, memory, 17, 'freeze_off')
        assert audit(True, True, critical, 17, after)
        n += 1
    # The independent subset must catch a lost global sticky hold even when the GC takes
    # the otherwise internally self-consistent unheld branch (also under critical pressure).
    for memory in ['below', 'normal', 'critical']:
        after, critical, _ = original(False, memory, 17)
        assert audit(False, True, critical, 17, after)
        n += 1
    # Sequence tests: a real pause then first release, no 90-call deferred-age catchup.
    for mutation in [None, 'release_catchup']:
        before = 17
        for _ in range(90):
            after, critical, _ = original(True, 'normal', before)
            assert not audit(True, True, critical, before, after)
            before = after
        after, critical, _ = original(False, 'normal', before, mutation)
        assert audit(False, False, critical, before, after) == (mutation is not None)
        n += 1
    assert audit(False, False, False, 17, 16)  # backwards clock
    n += 1
    # A stale TLS op in an empty next submission is not an independent held witness.
    stale_tls_op = True
    current_slice_counted = False
    after, critical, _ = original(False, 'normal', 17)
    assert stale_tls_op and not audit(False, current_slice_counted, critical, 17, after)
    n += 1
    print(f'GC audit truth/sequence tests: {n}/{n} PASS (including freeze-off, lost-sticky, release-catchup, stale TLS).')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-only', action='store_true')
    args = parser.parse_args()
    tests()
    if args.test_only:
        return
    originals, texts = patched_sources()
    # Compute every replacement first, then write only the five owned files, preserving EOL.
    for p, text in texts.items():
        assert (ROOT / p).read_bytes() == originals[p], f'concurrent edit: {p}'
        eol = '\r\n' if b'\r\n' in originals[p] else '\n'
        (ROOT / p).write_bytes(text.replace('\n', eol).encode('utf-8'))
        print(p)

if __name__ == '__main__':
    main()

# F30d (HPP-709), ROADMAP s122 item 643(v): KYTY_RT_SKIP=4 (PB items 3-4 not applied) and counters rts_bad_b, rts_bad_rx.
# Usage: python patch_f30d.py <repo root>.  Whole-line anchors; CRLF-safe; writes LF back (or CRLF if the file had it).
import sys, pathlib

root = pathlib.Path(sys.argv[1])

def patch(rel, edits):
    p = root / rel
    raw = p.read_bytes()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', '\n')
    lines = text.split('\n')
    for old, new in edits:
        old_l = old.split('\n')
        hits = [i for i in range(len(lines) - len(old_l) + 1) if lines[i:i + len(old_l)] == old_l]
        if len(hits) != 1:
            raise SystemExit('%s: anchor hits=%d: %r' % (rel, len(hits), old_l[0]))
        i = hits[0]
        lines[i:i + len(old_l)] = new.split('\n')
    out = '\n'.join(lines)
    if crlf:
        out = out.replace('\n', '\r\n')
    p.write_bytes(out.encode('utf-8'))
    print('patched', rel, len(edits))

T = '\t'

patch('src/common/gates.cpp', [
    ('    // Session 127, PROTOTYPE: the K3 skip (1), its self-check (2), the self-check with the register source ignored (3)\n'
     '    // (docs/session-127/design127.md rev 2). Read once per draw at its entry and latched, so it CAN be a schedule arm.\n'
     '    {"KYTY_RT_SKIP", "rtskip", 1, 3},',
     '    // Session 127, PROTOTYPE: the K3 skip (1), its self-check (2), the self-check with the register source ignored (3)\n'
     '    // (docs/session-127/design127.md rev 2). Read once per draw at its entry and latched, so it CAN be a schedule arm.\n'
     '    // Track F, F30d (ROADMAP s122 item 643(v)): 4 = the self-check with PB items 3 and 4 not applied (positive control\n'
     '    // of place B).\n'
     '    {"KYTY_RT_SKIP", "rtskip", 1, 4},'),
])

patch('src/common/gates.h', [
    (T + 'RtSkip,           // KYTY_RT_SKIP,     file name "rtskip" (0 off, 1 skip, 2 self-check, 3 self-check + positive control; default 1 since session 128)',
     T + 'RtSkip,           // KYTY_RT_SKIP,     file name "rtskip" (0 off, 1 skip, 2 self-check, 3 self-check + positive control; default 1 since session 128; 4 self-check + positive control of place B, F30d)'),
])

patch('src/common/frameStats.h', [
    (T + 'RtsEarly,                // rts_early: values 2/3 - draws that reached place A and not the post',
     T + 'RtsEarly,                // rts_early: values 2/3 - draws that reached place A and not the post\n'
     + T + '// Track F, F30d (ROADMAP s122 item 643(v)(2)): of rts_bad (values >= 2), the mismatches with a place B bit (0x3f0) and\n'
     + T + '// with bit R or X (0x010 / 0x020).  Raw counts.\n'
     + T + 'RtsBadB,                 // rts_bad_b\n'
     + T + 'RtsBadRx,                // rts_bad_rx'),
])

patch('src/graphics/presentation/videoOut.cpp', [
    (T * 4 + '    {"rts_early", FS::Counter::RtsEarly, false},',
     T * 4 + '    {"rts_early", FS::Counter::RtsEarly, false},\n'
     + T * 4 + '    // Track F, F30d (ROADMAP s122 item 643(v)(2)).\n'
     + T * 4 + '    {"rts_bad_b", FS::Counter::RtsBadB, false},\n'
     + T * 4 + '    {"rts_bad_rx", FS::Counter::RtsBadRx, false},'),
])

patch('src/graphics/host_gpu/renderer/renderDraw.cpp', [
    ('// Session 127, knob "rtskip" (KYTY_RT_SKIP, 0..3, default 0; docs/session-127/design127.md rev 2 with ROADMAP s122 items',
     '// Session 127, knob "rtskip" (KYTY_RT_SKIP, 0..4, default 0; docs/session-127/design127.md rev 2 with ROADMAP s122 items'),
    ('//   every step is compared with it (s.5); 3 = 2 with the register source ignored by PA (positive control, s.6).',
     '//   every step is compared with it (s.5); 3 = 2 with the register source ignored by PA (positive control, s.6);\n'
     '//   4 = 2 with PB items 3 (metadata epoch) and 4 (state_serial) not applied (positive control of place B; track F, F30d,\n'
     '//   ROADMAP s122 item 643(v)).'),
    ('constinit thread_local uint32_t    t_rts_logged   = 0;       // bits 1..15: refusal printed; 17..19: mode line printed',
     'constinit thread_local uint32_t    t_rts_logged   = 0;       // bits 1..15: refusal printed; 17..20: mode line printed'),
    (T + 'FS::Add(FS::Counter::RtsBad, 1);\n'
     + T + 'if (!t_rts_reg) {\n'
     + T + T + 'FS::Add(FS::Counter::RtsBadNoreg, 1);\n'
     + T + '}',
     T + 'FS::Add(FS::Counter::RtsBad, 1);\n'
     + T + 'if (!t_rts_reg) {\n'
     + T + T + 'FS::Add(FS::Counter::RtsBadNoreg, 1);\n'
     + T + '}\n'
     + T + '// Track F, F30d (ROADMAP s122 item 643(v)(2)): the place B share of rts_bad, and its R / X part.\n'
     + T + 'if ((bits & 0x3f0u) != 0) {\n'
     + T + T + 'FS::Add(FS::Counter::RtsBadB, 1);\n'
     + T + '}\n'
     + T + 'if ((bits & 0x030u) != 0) {\n'
     + T + T + 'FS::Add(FS::Counter::RtsBadRx, 1);\n'
     + T + '}'),
    (T + T + '// 3 (N2, N4): the metadata epoch the record\'s fast records were taken at.\n'
     + T + T + 'if (cache.MetaEpoch() != rec->meta) {\n'
     + T + T + T + 'return C::RtsXbMeta;\n'
     + T + T + '}\n'
     + T + T + '// 4 (N3, [RC4]): no state record of a target was written since the record.\n'
     + T + T + 'for (uint32_t i = 0; i < rec->nt; i++) {\n'
     + T + T + T + 'if (img[i]->backing.state_serial != rec->t[i].state_serial) {\n'
     + T + T + T + T + 'return C::RtsXbSer;\n'
     + T + T + T + '}\n'
     + T + T + '}',
     T + T + '// Items 3 and 4 are not applied at value 4 (track F, F30d, ROADMAP s122 item 643(v)(1)): the positive control of\n'
     + T + T + '// place B - the full capture then runs against a record these two would have refused.\n'
     + T + T + 'if (t_rts != 4) {\n'
     + T + T + T + '// 3 (N2, N4): the metadata epoch the record\'s fast records were taken at.\n'
     + T + T + T + 'if (cache.MetaEpoch() != rec->meta) {\n'
     + T + T + T + T + 'return C::RtsXbMeta;\n'
     + T + T + T + '}\n'
     + T + T + T + '// 4 (N3, [RC4]): no state record of a target was written since the record.\n'
     + T + T + T + 'for (uint32_t i = 0; i < rec->nt; i++) {\n'
     + T + T + T + T + 'if (img[i]->backing.state_serial != rec->t[i].state_serial) {\n'
     + T + T + T + T + T + 'return C::RtsXbSer;\n'
     + T + T + T + T + '}\n'
     + T + T + T + '}\n'
     + T + T + '}'),
])
print('ALL OK')

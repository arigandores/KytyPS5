"""Session 107: derive dab107.py (scorer of pred/02_dabatch2.md) from the s107 carried copy of dab106.py.
Copied and edited, not imported.  Every edit is an anchored replace that must match exactly once.
    python C:/kyty/s107/make_dab107.py C:/kyty/s107/dab106.py C:/kyty/s107/dab107.py
"""
import sys

SRC, DST = sys.argv[1], sys.argv[2]
NL = chr(10)
text = open(SRC, encoding='utf-8').read().replace('\r\n', NL)


def rep(old, new, count=1):
    global text
    n = text.count(old)
    if n != count:
        raise SystemExit('anchor found %d times (want %d): %r' % (n, count, old[:90]))
    text = text.replace(old, new)


start = text.index('"""')
end = text.index('"""', start + 3) + 3
text = text[:start] + '''"""Session 107, "maximum FPS" track 1 candidate scorer: knob `dabatch` 8 -> 2 (M1 draw-ahead requests per
PipelineCache::QueueDrawAhead call, i.e. per hold of PipelineCache::m_mutex by the walker thread; obs107 measured the
walker's QueueDrawAhead as the holder of 57.7 % of GuestGpu's contended wall), ABBA `dabatch=8|2` with
`dawalk=1 dawalklead=1` in both arms, sealed to pred/02_dabatch2.md.  Derived from session 106's dab106.py (copied,
not imported; make_dab107.py).

    python C:/kyty/s107/dab107.py dab107 [--out <json>] [--video-meta <json> --video-report <txt>]
    python C:/kyty/s107/dab107.py <tag> --root <dir> --draft      (fixtures / old logs: arithmetic only)

Ship rule (ROADMAP, decision after session 104; session 107 item 5): SHIP dabatch=2 as the new default only if
the run is ADMITTED and S1 d mean dt_us <= -100 us and S2 its 2SE excludes 0, and the video pass (gate text
dabatch=2, pinned, >= 3000 frames, 0 one-frame glitches) reads PASS; d cpu_net_us is reported, never deciding.
"""''' + text[end:]

rep("PRED = 'C:/kyty/s107/prev106/pred/02_dabatch.md'", "PRED = 'C:/kyty/s107/pred/02_dabatch2.md'")
rep("PRED_SHA = 'bde73d27fe761a5cc29d0e54e6afaa33e466f3519f5cf9036b862e57cafd962b'   # pred/02 sealed",
    "PRED_SHA = None          # filled by the executor when pred/02 is sealed")
rep("PRED_BYTES = 3442       # pred/02 sealed", "PRED_BYTES = None        # filled by the executor when pred/02 is sealed")
rep("BINARY_SHA = 'd23094dfe42478f8a40907741120837c4cf952ff16b830c1e6e55697dc177db3'",
    "BINARY_SHA = 'dd567a0feb49d8f182345434920649b485b677b69569c5e06d9b9d73b20789a3'")
rep("ARMS = ('dawalk=1 dawalklead=1 dabatch=64', 'dawalk=1 dawalklead=1 dabatch=8')",
    "ARMS = ('dawalk=1 dawalklead=1 dabatch=8', 'dawalk=1 dawalklead=1 dabatch=2')")
rep("TAG_RE = r'dab106b?(?:_entry1)?'", "TAG_RE = r'dab107b?(?:_entry1)?'")
rep("    checks['BATCH_ARMED'] = bool(q0 and q1 and q1 / q0 >= 4.0)",
    "    checks['BATCH_ARMED'] = bool(q0 and q1 and q1 / q0 >= 3.0)")
rep("        'dabatch_8_in_gate_text': ' dawalk=1 ' in gates and ' dabatch=8 ' in gates,",
    "        'dabatch_2_in_gate_text': ' dawalk=1 ' in gates and ' dabatch=2 ' in gates,")
rep("""    add('B1', 'arm-1 / arm-0 da_qcall in [6, 9] (eight-fold calls)',
        (lev[1].get('da_qcall') or 0) / (lev[0].get('da_qcall') or 1), 6, 9)""",
    """    add('B1', 'arm-1 / arm-0 da_qcall in [3.5, 4.5] (four-fold calls)',
        (lev[1].get('da_qcall') or 0) / (lev[0].get('da_qcall') or 1), 3.5, 4.5)""")
rep("""    add('B2', 'd da_queue_us in [0, +250] us (more calls, shorter holds, on the walker)',""",
    """    add('B2', 'd da_queue_us in [0, +600] us (more calls, shorter holds, on the walker)',""")
rep("""        stats['da_queue_us']['mean'], 0, 250)""", """        stats['da_queue_us']['mean'], 0, 600)""")
rep("""    add('B3', 'd cpu_net_us in [-500, -100] us (less spinning on m_mutex)', stats['cpu_net_us']['mean'], -500, -100)
    add('B4', 'd mean dt_us in [-350, 0] us', stats['dt_us']['mean'], -350, 0)
    add('B5', 'd mean dt_us <= -100 us (the ship bar) - the discriminating prediction, medium confidence',""",
    """    add('B3', 'd cpu_net_us in [-300, 0] us (less spinning on m_mutex)', stats['cpu_net_us']['mean'], -300, 0)
    add('B4', 'd mean dt_us in [-250, +50] us', stats['dt_us']['mean'], -250, 50)
    add('B5', 'd mean dt_us <= -100 us (the ship bar) - the discriminating prediction, LOW confidence',""")
rep("v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP dabatch=64 (run not admitted)'",
    "v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP dabatch=8 (run not admitted)'")
rep("v = 'KEEP dabatch=64 (ship rule S1-S2 on mean dt not met)'", "v = 'KEEP dabatch=8 (ship rule S1-S2 on mean dt not met)'")
rep("v = 'SHIP dabatch=8 as the new default (a new build: its video pass is owed, ROADMAP 6)'",
    "v = 'SHIP dabatch=2 as the new default (a new build: its video pass is owed, ROADMAP 6)'")
rep("v = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vdb106 is read)'",
    "v = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vdb107 is read)'")
rep("v = 'KEEP dabatch=64 (video pass failed)'", "v = 'KEEP dabatch=8 (video pass failed)'")
rep("out = {'scorer': 'dab106.py',", "out = {'scorer': 'dab107.py',")
rep("lines = ['dab106.py %s status=%s seal=%s'", "lines = ['dab107.py %s status=%s seal=%s'")
rep("size into dab106.py (only --draft runs without a seal)", "size into dab107.py (only --draft runs without a seal)")
rep("print('tag %r is not a pred/02 tag (dab106, dab106b, optional _entry1)' % o.tag)",
    "print('tag %r is not a pred/02 tag (dab107, dab107b, optional _entry1)' % o.tag)")
open(DST, 'w', encoding='utf-8', newline=NL).write(text)
print('written', DST, len(text))

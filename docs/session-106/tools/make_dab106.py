"""Session 106: derive dab106.py (scorer of pred/02_dabatch.md) from session 105's lead105.py (the s106 carried
copy).  Copied and edited, not imported.  Every edit is an anchored replace that must match exactly once.
    python C:/kyty/s106/make_dab106.py C:/kyty/s106/lead105.py C:/kyty/s106/dab106.py
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
text = text[:start] + '''"""Session 106, "maximum FPS" track 1 item 2 candidate scorer: knob `dabatch` (M1 draw-ahead requests per
PipelineCache::QueueDrawAhead call, i.e. per hold of PipelineCache::m_mutex by the walker thread), ABBA
`dabatch=64|8` with `dawalk=1 dawalklead=1` in both arms, sealed to pred/02_dabatch.md.  Derived from session
105's lead105.py (copied, not imported; make_dab106.py).

    python C:/kyty/s106/dab106.py dab106 [--out <json>] [--video-meta <json> --video-report <txt>]
    python C:/kyty/s106/dab106.py <tag> --root <dir> --draft      (fixtures / old logs: arithmetic only)

Ship rule (ROADMAP, decision after session 104; session 106 item 5): SHIP dabatch=8 as the new default only if
the run is ADMITTED and S1 d mean dt_us <= -100 us and S2 its 2SE excludes 0, and the video pass (gate text
dabatch=8, pinned, >= 3000 frames, 0 one-frame glitches) reads PASS; d cpu_net_us is reported, never deciding.
"""''' + text[end:]

rep("PRED = 'C:/kyty/s106/prev105/pred/01_dawalklead.md'", "PRED = 'C:/kyty/s106/pred/02_dabatch.md'")
rep("PRED_SHA = '7dca62cf623edf98782f0642f40432f460ffaa32237193d449c55bc3fd637e27'          # filled by the executor when pred/03 is sealed",
    "PRED_SHA = None          # filled by the executor when pred/02 is sealed")
rep("PRED_BYTES = 3715        # filled by the executor when pred/03 is sealed",
    "PRED_BYTES = None        # filled by the executor when pred/02 is sealed")
rep("BINARY_SHA = '61ae73476eac343fcca3554924496ec0c50da536826ecab6dea7a1e4548e4bd1'",
    "BINARY_SHA = 'd23094dfe42478f8a40907741120837c4cf952ff16b830c1e6e55697dc177db3'")
rep("ARMS = ('dawalk=1 dawalklead=1', 'dawalk=1 dawalklead=2')",
    "ARMS = ('dawalk=1 dawalklead=1 dabatch=64', 'dawalk=1 dawalklead=1 dabatch=8')")
rep("TAG_RE = r'lead105b?(?:_entry1)?'", "TAG_RE = r'dab106b?(?:_entry1)?'")
rep("""    checks['WALKS_SAME'] = rw is not None and abs(rw) <= WALKS_TOL""",
    """    checks['WALKS_SAME'] = rw is not None and abs(rw) <= WALKS_TOL
    # Session 106: the batch knob armed - QueueDrawAhead calls grow about eight-fold in arm 1.
    q0, q1 = lev[0].get('da_qcall'), lev[1].get('da_qcall')
    checks['BATCH_ARMED'] = bool(q0 and q1 and q1 / q0 >= 4.0)""")
rep("""        'dawalklead_2_in_gate_text': ' dawalk=1 ' in gates and ' dawalklead=2 ' in gates,""",
    """        'dabatch_8_in_gate_text': ' dawalk=1 ' in gates and ' dabatch=8 ' in gates,
        'pinned': env.get('KYTY_GPU_CLOCK_PIN') == '1',""")
rep("""    add('L1', 'd da_late in [-9, -3] a flip (lead 2 removes most late results)', stats['da_late']['mean'], -9, -3)
    add('L2', 'd da_miss in [-150, -30] a flip', stats['da_miss']['mean'], -150, -30)
    add('L3', 'd da_take_us in [-400, 0] us', stats['da_take_us']['mean'], -400, 0)
    add('L4', 'd mean dt_us in [-350, +100] us', stats['dt_us']['mean'], -350, 100)
    add('L5', 'd mean dt_us <= -100 us (the ship bar) - the discriminating prediction, low confidence',
        stats['dt_us']['mean'], None, SHIP_US)""",
    """    add('B1', 'arm-1 / arm-0 da_qcall in [6, 9] (eight-fold calls)',
        (lev[1].get('da_qcall') or 0) / (lev[0].get('da_qcall') or 1), 6, 9)
    add('B2', 'd da_queue_us in [0, +250] us (more calls, shorter holds, on the walker)',
        stats['da_queue_us']['mean'], 0, 250)
    add('B3', 'd cpu_net_us in [-500, -100] us (less spinning on m_mutex)', stats['cpu_net_us']['mean'], -500, -100)
    add('B4', 'd mean dt_us in [-350, 0] us', stats['dt_us']['mean'], -350, 0)
    add('B5', 'd mean dt_us <= -100 us (the ship bar) - the discriminating prediction, medium confidence',
        stats['dt_us']['mean'], None, SHIP_US)
    add('B6', 'd da_miss in [-30, +30] a flip (the batch does not change what M1 builds)',
        stats['da_miss']['mean'], -30, 30)""")
rep("v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP dawalklead=1 (run not admitted)'",
    "v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP dabatch=64 (run not admitted)'")
rep("v = 'KEEP dawalklead=1 (ship rule S1-S2 on mean dt not met)'",
    "v = 'KEEP dabatch=64 (ship rule S1-S2 on mean dt not met)'")
rep("v = 'SHIP dawalklead=2 as the new default (a new build: its video pass is owed, ROADMAP 6)'",
    "v = 'SHIP dabatch=8 as the new default (a new build: its video pass is owed, ROADMAP 6)'")
rep("v = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vld105 is read)'",
    "v = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vdb106 is read)'")
rep("v = 'KEEP dawalklead=1 (video pass failed)'", "v = 'KEEP dabatch=64 (video pass failed)'")
rep("out = {'scorer': 'dwk104.py',", "out = {'scorer': 'dab106.py', 'scorer_sha256': sha256_file(__file__),")
rep("lines = ['dwk104.py %s status=%s seal=%s'", "lines = ['dab106.py %s status=%s seal=%s'")
rep("size into dwk104.py (only --draft runs without a seal)", "size into dab106.py (only --draft runs without a seal)")
rep('    """pred/03 s4."""', '    """pred/02 s4 (the lead105 walk arming plus BATCH_ARMED)."""')
rep('    """pred/03 s5 S5.  Returns', '    """pred/02 video pass (pinned).  Returns')
rep("print('tag %r is not a pred/03 tag (dwk104, dwk104b, optional _entry1)' % o.tag)",
    "print('tag %r is not a pred/02 tag (dab106, dab106b, optional _entry1)' % o.tag)")
open(DST, 'w', encoding='utf-8', newline=NL).write(text)
print('written', DST, len(text))

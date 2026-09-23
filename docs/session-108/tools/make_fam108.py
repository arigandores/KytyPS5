"""Session 108: derive fam108.py (scorer of pred/01_cspfam.md) from session 107's dab107.py (C:/kyty/s107 copy).
Copied and edited, not imported.  Every edit is an anchored replace that must match exactly once.
    python make_fam108.py C:/kyty/s107/dab107.py <dst fam108.py>
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
text = text[:start] + '''"""Session 108, "maximum FPS" track 1 candidate scorer: knob `cspfam` (skip the walker's compute prefetch per
shader family once the family's last K locked prefetches found a built pipeline; obs107: the steady-state
prefetch always finds its pipeline and holds PipelineCache::m_mutex 342 us a flip), ABBA `cspfam=0|4` with
`dawalk=1 dawalklead=1` in both arms, sealed to pred/01_cspfam.md.  Derived from session 107's dab107.py (copied,
not imported; make_fam108.py).

    python C:/kyty/s108/fam108.py fam108 [--out <json>] [--video-meta <json> --video-report <txt>]
    python C:/kyty/s108/fam108.py <tag> --root <dir> --draft      (fixtures / old logs: arithmetic only)

Ship rule (ROADMAP, decision after session 104; session 108 items 1-2): SHIP cspfam=4 as the new default only if
the run is ADMITTED - including SYNC_COMPILE: over all rows from frame 2100, sum cs_sync_new of arm 1 <= that of
arm 0 + 2 - and S1 d mean dt_us <= -100 us and S2 its 2SE excludes 0, and the video pass (gate text cspfam=4,
pinned, >= 3000 frames, 0 one-frame glitches) reads PASS; d cpu_net_us is reported, never deciding.
"""''' + text[end:]

rep("PRODUCTION_ROOT = 'C:/kyty/s107'", "PRODUCTION_ROOT = 'C:/kyty/s108'")
rep("PRED = 'C:/kyty/s107/pred/02_dabatch2.md'", "PRED = 'C:/kyty/s108/pred/01_cspfam.md'")
rep("PRED_SHA = '3a0d4043e983cda2f9ae19aff4da1ad7cb15861639fe95bd921c6fb61c1027bb'   # pred/02 sealed",
    "PRED_SHA = None          # filled by the executor when pred/01 is sealed")
rep("PRED_BYTES = 3077       # pred/02 sealed", "PRED_BYTES = None        # filled by the executor when pred/01 is sealed")
rep("BINARY_SHA = 'dd567a0feb49d8f182345434920649b485b677b69569c5e06d9b9d73b20789a3'",
    "BINARY_SHA = 'fd1d0bd7f68280e97680bc68dfe56fdf57a134429a49bc9223ece6254b7b1e72'")
rep("GATES_FILE = 'C:/kyty/s107/gates_base.txt'", "GATES_FILE = 'C:/kyty/s108/gates_base.txt'")
rep("ARMS = ('dawalk=1 dawalklead=1 dabatch=8', 'dawalk=1 dawalklead=1 dabatch=2')",
    "ARMS = ('dawalk=1 dawalklead=1 cspfam=0', 'dawalk=1 dawalklead=1 cspfam=4')")
rep("TAG_RE = r'dab107b?(?:_entry1)?'", "TAG_RE = r'fam108b?(?:_entry1)?'")
rep("""    'pl_proc_n': 'x', 'sh_jobs': 'x',
}""", """    'pl_proc_n': 'x', 'sh_jobs': 'x',
    'cspfam_look': 'x', 'cspfam_skip': 'x', 'cs_sync_new': 'x', 'cs_sync_wait': 'x',
    'cspf_have': 'x', 'cspf_new': 'x',
}
SYNC_SLACK = 2""")
rep('    """pred/02 s4 (the lead105 walk arming plus BATCH_ARMED)."""',
    '    """pred/01 s3 (the lead105 walk arming plus FAMILY_ARMED)."""')
rep("""    # Session 106: the batch knob armed - QueueDrawAhead calls grow about eight-fold in arm 1.
    q0, q1 = lev[0].get('da_qcall'), lev[1].get('da_qcall')
    checks['BATCH_ARMED'] = bool(q0 and q1 and q1 / q0 >= 3.0)""",
    """    # Session 108: the family knob dark in arm 0 and skipping in arm 1.
    look0 = kept_total(rows, sel, arms, 0, 'cspfam_look')
    checks['FAMILY_DARK_ARM0'] = look0 == 0
    checks['FAMILY_ARMED_ARM1'] = bool((lev[1].get('cspfam_skip') or 0) >= 1)""")
rep("""        'dabatch_2_in_gate_text': ' dawalk=1 ' in gates and ' dabatch=2 ' in gates,""",
    """        'cspfam_4_in_gate_text': ' dawalk=1 ' in gates and ' cspfam=4 ' in gates,""")
rep("""    arm = arming(rows, sel, arms, lev)
    out['arming'] = arm
    controls['ARMING'] = arm['passed']
""", """    arm = arming(rows, sel, arms, lev)
    out['arming'] = arm
    controls['ARMING'] = arm['passed']
    # Session 108, pred/01 s3: the dispatch-time compile guard over ALL rows from the first frame, by row arm.
    sync = {a: sum(r.get('cs_sync_new', 0) for n, r in rows.items() if n >= geo['first'] and r.get('arm') == a)
            for a in (0, 1)}
    wait = {a: sum(r.get('cs_sync_wait', 0) for n, r in rows.items() if n >= geo['first'] and r.get('arm') == a)
            for a in (0, 1)}
    out['sync_compile'] = {'cs_sync_new': sync, 'cs_sync_wait': wait, 'slack': SYNC_SLACK}
    controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK
""")
rep("""    add('B1', 'arm-1 / arm-0 da_qcall in [3.5, 4.5] (four-fold calls)',
        (lev[1].get('da_qcall') or 0) / (lev[0].get('da_qcall') or 1), 3.5, 4.5)
    add('B2', 'd da_queue_us in [0, +600] us (more calls, shorter holds, on the walker)',
        stats['da_queue_us']['mean'], 0, 600)
    add('B3', 'd cpu_net_us in [-300, 0] us (less spinning on m_mutex)', stats['cpu_net_us']['mean'], -300, 0)
    add('B4', 'd mean dt_us in [-250, +50] us', stats['dt_us']['mean'], -250, 50)
    add('B5', 'd mean dt_us <= -100 us (the ship bar) - the discriminating prediction, LOW confidence',
        stats['dt_us']['mean'], None, SHIP_US)
    add('B6', 'd da_miss in [-30, +30] a flip (the batch does not change what M1 builds)',
        stats['da_miss']['mean'], -30, 30)""",
    """    add('F1', 'arm-1 cspfam_skip level in [150, 270] a flip', lev[1].get('cspfam_skip'), 150, 270)
    add('F2', 'arm-1 cspf_have level <= 60 a flip (most prefetches skipped)', lev[1].get('cspf_have'), None, 60)
    add('F3', 'd cpu_net_us in [-400, -50] us', stats['cpu_net_us']['mean'], -400, -50)
    add('F4', 'd mean dt_us in [-300, 0] us', stats['dt_us']['mean'], -300, 0)
    add('F5', 'd mean dt_us <= -100 us (the ship bar) - the discriminating prediction, medium-low confidence',
        stats['dt_us']['mean'], None, SHIP_US)
    add('F6', 'd da_miss in [-30, +30] a flip', stats['da_miss']['mean'], -30, 30)""")
rep("v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP dabatch=8 (run not admitted)'",
    "v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP cspfam=0 (run not admitted)'")
rep("v = 'KEEP dabatch=8 (ship rule S1-S2 on mean dt not met)'", "v = 'KEEP cspfam=0 (ship rule S1-S2 on mean dt not met)'")
rep("v = 'SHIP dabatch=2 as the new default (a new build: its video pass is owed, ROADMAP 6)'",
    "v = 'SHIP cspfam=4 as the new default (a new build: its video pass is owed, ROADMAP 6)'")
rep("v = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vdb107 is read)'",
    "v = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vfm108 is read)'")
rep("v = 'KEEP dabatch=8 (video pass failed)'", "v = 'KEEP cspfam=0 (video pass failed)'")
rep("out = {'scorer': 'dab107.py',", "out = {'scorer': 'fam108.py',")
rep("lines = ['dab107.py %s status=%s seal=%s'", "lines = ['fam108.py %s status=%s seal=%s'")
rep("size into dab107.py (only --draft runs without a seal)", "size into fam108.py (only --draft runs without a seal)")
rep("print('tag %r is not a pred/02 tag (dab107, dab107b, optional _entry1)' % o.tag)",
    "print('tag %r is not a pred/01 tag (fam108, fam108b, optional _entry1)' % o.tag)")
open(DST, 'w', encoding='utf-8', newline=NL).write(text)
print('written', DST, len(text))

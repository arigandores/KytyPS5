"""Session 109: derive frf109.py (scorer of pred/03_frf109.md, ABBA cspfree=0|1) from session 108's fam108.py (the
C:/kyty/s109 archive copy, sha256 pinned below).  Copied and edited, not imported.  Every edit is an anchored replace
that must match exactly once; anchors that must survive unchanged are asserted too.  Output bytes are LF / utf-8,
written in binary, so two runs give the same bytes.
    python make_frf109.py [<src fam108.py> [<dst frf109.py>]]
"""
import hashlib
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s109/fam108.py'
DST = sys.argv[2] if len(sys.argv) > 2 else 'C:/kyty/s106_stage/frf109/frf109.py'
SRC_SHA = 'ab187ce8c8dd760eed1fcbce402a4c61e4f006fa07ddfe5bca6708895b594fc4'
NL = chr(10)
raw = open(SRC, 'rb').read()
got = hashlib.sha256(raw).hexdigest()
if got != SRC_SHA:
    raise SystemExit('source %s sha256 %s, pinned %s' % (SRC, got, SRC_SHA))
text = raw.decode('utf-8')
if chr(13) in text:
    raise SystemExit('source carries CR bytes')


def rep(old, new, count=1):
    global text
    n = text.count(old)
    if n != count:
        raise SystemExit('anchor found %d times (want %d): %r' % (n, count, old[:90]))
    text = text.replace(old, new)


def keep(old, count=1):
    n = text.count(old)
    if n != count:
        raise SystemExit('kept anchor found %d times (want %d): %r' % (n, count, old[:90]))


# ---- the module docstring ----------------------------------------------------------------------------------------
rep('''"""Session 108, "maximum FPS" track 1 candidate scorer: knob `cspfam` (skip the walker's compute prefetch per
shader family once the family's last K locked prefetches found a built pipeline; obs107: the steady-state
prefetch always finds its pipeline and holds PipelineCache::m_mutex 342 us a flip), ABBA `cspfam=0|4` with
`dawalk=1 dawalklead=1` in both arms, sealed to pred/01_cspfam.md.  Derived from session 107's dab107.py (copied,
not imported; make_fam108.py).

    python C:/kyty/s109/fam108.py fam108 [--out <json>] [--video-meta <json> --video-report <txt>]
    python C:/kyty/s109/fam108.py <tag> --root <dir> --draft      (fixtures / old logs: arithmetic only)

Ship rule (ROADMAP, decision after session 104; session 108 items 1-2): SHIP cspfam=4 as the new default only if
the run is ADMITTED - including SYNC_COMPILE: over all rows from frame 2100, sum cs_sync_new of arm 1 <= that of
arm 0 + 2 - and S1 d mean dt_us <= -100 us and S2 its 2SE excludes 0, and the video pass (gate text cspfam=4,
pinned, >= 3000 frames, 0 one-frame glitches) reads PASS; d cpu_net_us is reported, never deciding.
"""''', '''"""Session 109, "maximum FPS" track 1 candidate scorer: knob `cspfree` (the walker thread's compute prefetch
returns before PipelineCache::m_mutex when a per-thread memo knows (source entry, specialization) and a pipeline
for it; design109 B), ABBA `cspfree=0|1` with `dawalk=1 dawalklead=1` in both arms, sealed to pred/03_frf109.md.
Derived from session 108's fam108.py (C:/kyty/s109 archive copy; copied, not imported; make_frf109.py).

    python C:/kyty/s109/frf109.py frf109 [--out <json>] [--video-meta <json> --video-report <txt>]
    python C:/kyty/s109/frf109.py <tag> --root <dir> --draft      (fixtures / old logs: arithmetic only)

Ship rule (ROADMAP, decision after session 104; session 108 items 1-2): SHIP cspfree=1 as the new default only if
the run is ADMITTED - including SYNC_COMPILE: over all rows from frame 2100, sum cs_sync_new of arm 1 <= that of
arm 0 + 2 - and S1 d mean dt_us <= -100 us and S2 its 2SE excludes 0, and the video pass vff109 (gate text
cspfree=1, pinned, >= 3000 frames, 0 one-frame glitches) reads PASS.  Arming (under control ARMING): FREE_DARK_ARM0
(arm-0 kept rows: sum cspfree_look = 0 and sum cspfree_hit = 0), FREE_ARMED_ARM1 (arm-1 level of cspfree_hit >= 1),
FREE_NO_BAD (sum cspfree_bad = 0 over all rows).  d cpu_net_us is reported, never deciding: no admission or
decision term reads it (derived(), block_means(), pair stats and the summary only).
"""''')

# ---- constants ---------------------------------------------------------------------------------------------------
keep("PRODUCTION_ROOT = 'C:/kyty/s109'")
rep("PRED = 'C:/kyty/s109/prev108/pred/01_cspfam.md'", "PRED = 'C:/kyty/s109/pred/03_frf109.md'")
rep("PRED_SHA = 'a40cf056d83fd2ed5b31b1c84e1674f0968803ad481d8831213617c623caa945'   # pred/01 sealed",
    "PRED_SHA = None          # filled by the executor when pred/03 is sealed")
rep("PRED_BYTES = 6890       # pred/01 sealed",
    "PRED_BYTES = None        # filled by the executor when pred/03 is sealed")
rep("BINARY_SHA = 'fd1d0bd7f68280e97680bc68dfe56fdf57a134429a49bc9223ece6254b7b1e72'",
    "BINARY_SHA = '2f5932296d564b1098831b75a7fc6c8796d3a9ac7e871ea0c3a1c6b0610a4b77'")
keep("GATES_FILE = 'C:/kyty/s109/gates_base.txt'")
keep("GATES_SHA = '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf'")
keep("PERIOD, START, FIRST_FRAME = 90, 1800, 2100")
keep("HOLD_S = 600")
rep("ARMS = ('dawalk=1 dawalklead=1 cspfam=0', 'dawalk=1 dawalklead=1 cspfam=4')",
    "ARMS = ('dawalk=1 dawalklead=1 cspfree=0', 'dawalk=1 dawalklead=1 cspfree=1')")
keep("SCHEDULE = '90+1800:%s|%s' % ARMS")
rep("TAG_RE = r'fam108b?(?:_entry1)?'", "TAG_RE = r'frf109b?(?:_entry1)?'")
keep("SHIP_US = -100.0")
# every FrameTrace-x row of the 2f593229 build carries cspfam_clr and the nine cspfree_* counters: into the schema
rep("""    'cspf_have': 'x', 'cspf_new': 'x',
}""", """    'cspf_have': 'x', 'cspf_new': 'x',
    'cspfam_clr': 'x', 'cspfree_look': 'x', 'cspfree_hit': 'x', 'cspfree_src_miss': 'x',
    'cspfree_spec_miss': 'x', 'cspfree_mat_fail': 'x', 'cspfree_clr': 'x', 'cspfree_store': 'x',
    'cspfree_bad': 'x', 'cspfree_moved': 'x',
}""")
keep("SYNC_SLACK = 2")
rep("size into fam108.py (only --draft runs without a seal)", "size into frf109.py (only --draft runs without a seal)")

# ---- arming: FAMILY_* -> FREE_* ----------------------------------------------------------------------------------
rep('    """pred/01 s3 (the lead105 walk arming plus FAMILY_ARMED)."""',
    '    """pred/03 (the lead105 walk arming plus FREE_DARK_ARM0, FREE_ARMED_ARM1 and FREE_NO_BAD)."""')
rep("""    # Session 108: the family knob dark in arm 0 and skipping in arm 1.
    look0 = kept_total(rows, sel, arms, 0, 'cspfam_look')
    checks['FAMILY_DARK_ARM0'] = look0 == 0
    checks['FAMILY_ARMED_ARM1'] = bool((lev[1].get('cspfam_skip') or 0) >= 1)""",
    """    # Session 109: the cspfree knob dark in arm 0 (no lookup, no hit over the kept rows), hitting in arm 1 (level
    # >= 1), and no knob-2 disagreement anywhere (over all rows; knob 1 never verifies, so a non-zero sum means a
    # wrong build or knob).
    look0 = kept_total(rows, sel, arms, 0, 'cspfree_look')
    hit0 = kept_total(rows, sel, arms, 0, 'cspfree_hit')
    checks['FREE_DARK_ARM0'] = look0 == 0 and hit0 == 0
    checks['FREE_ARMED_ARM1'] = bool((lev[1].get('cspfree_hit') or 0) >= 1)
    bad = sum(r.get('cspfree_bad', 0) for r in rows.values())
    checks['FREE_NO_BAD'] = bad == 0""")
rep("""            'skip_over_posts_rel': ident, 'drop_fraction': drop_frac, 'walks_rel': rw}""",
    """            'skip_over_posts_rel': ident, 'drop_fraction': drop_frac, 'walks_rel': rw,
            'free_arm0_kept': {'cspfree_look': look0, 'cspfree_hit': hit0}, 'cspfree_bad_all_rows': bad}""")
keep("    checks['INSTRUMENTS_DARK'] = dark")

# ---- video: vfm108 / cspfam=4 -> vff109 / cspfree=1 ----------------------------------------------------------------
rep('    """pred/02 video pass (pinned).  Returns (state, detail): state in PASS / FAIL / ABSENT."""',
    '    """pred/03 video pass vff109 (pinned).  Returns (state, detail): state in PASS / FAIL / ABSENT."""')
rep("""        'cspfam_4_in_gate_text': ' dawalk=1 ' in gates and ' cspfam=4 ' in gates,""",
    """        'cspfree_1_in_gate_text': ' dawalk=1 ' in gates and ' cspfree=1 ' in gates,""")

# ---- evaluate(): name; SYNC_COMPILE code kept verbatim (only its comment names the new seal) -------------------------
rep("out = {'scorer': 'fam108.py',", "out = {'scorer': 'frf109.py',")
rep("    # Session 108, pred/01 s3: the dispatch-time compile guard over ALL rows from the first frame, by row arm.",
    "    # Session 108 guard, kept verbatim (pred/03): the dispatch-time compile guard over ALL rows from the first\n"
    "    # frame, by row arm.")
keep("    controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK")
keep("        'S1_dt_le_-100': dt['mean'] is not None and dt['mean'] <= SHIP_US,")
keep("                                 and dt['mean'] + 2 * dt['se'] < 0),")

# ---- predictions F1-F6 -> G1-G6 --------------------------------------------------------------------------------------
rep("""    add('F1', 'arm-1 cspfam_skip level in [150, 270] a flip', lev[1].get('cspfam_skip'), 150, 270)
    add('F2', 'arm-1 cspf_have level <= 60 a flip (most prefetches skipped)', lev[1].get('cspf_have'), None, 60)
    add('F3', 'd cpu_net_us in [-400, -50] us', stats['cpu_net_us']['mean'], -400, -50)
    add('F4', 'd mean dt_us in [-300, 0] us', stats['dt_us']['mean'], -300, 0)
    add('F5', 'd mean dt_us <= -100 us (the ship bar) - the discriminating prediction, medium-low confidence',
        stats['dt_us']['mean'], None, SHIP_US)
    add('F6', 'd da_miss in [-30, +30] a flip', stats['da_miss']['mean'], -30, 30)""",
    """    add('G1', 'arm-1 cspfree_hit level in [200, 270] a flip', lev[1].get('cspfree_hit'), 200, 270)
    add('G2', 'arm-1 cspf_have level <= 30 a flip (most prefetches return before the lock)',
        lev[1].get('cspf_have'), None, 30)
    add('G3', 'd mean dt_us in [-300, 0] us', stats['dt_us']['mean'], -300, 0)
    add('G4', 'd mean dt_us <= -100 us (the ship bar) - the discriminating prediction, medium-low confidence',
        stats['dt_us']['mean'], None, SHIP_US)
    add('G5', 'd da_miss in [-30, +30] a flip', stats['da_miss']['mean'], -30, 30)
    add('G6', 'd gpu_busy_us in [-50, +150] us a flip', stats['gpu_busy_us']['mean'], -50, 150)""")

# ---- verdict texts -------------------------------------------------------------------------------------------------
rep("v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP cspfam=0 (run not admitted)'",
    "v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP cspfree=0 (run not admitted)'")
rep("v = 'KEEP cspfam=0 (ship rule S1-S2 on mean dt not met)'",
    "v = 'KEEP cspfree=0 (ship rule S1-S2 on mean dt not met)'")
rep("v = 'SHIP cspfam=4 as the new default (a new build: its video pass is owed, ROADMAP 6)'",
    "v = 'SHIP cspfree=1 as the new default (a new build: its video pass is owed, ROADMAP 6)'")
rep("v = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vfm108 is read)'",
    "v = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vff109 is read)'")
rep("v = 'KEEP cspfam=0 (video pass failed)'", "v = 'KEEP cspfree=0 (video pass failed)'")

# ---- summary (report only) -------------------------------------------------------------------------------------------
rep("lines = ['fam108.py %s status=%s seal=%s'", "lines = ['frf109.py %s status=%s seal=%s'")
rep("""                        fmt(a.get('drop_fraction'), 4), fmt(a.get('walks_rel'), 4)))""",
    """                        fmt(a.get('drop_fraction'), 4), fmt(a.get('walks_rel'), 4)))
        lines.append('  cspfree arm-0 kept totals %s  cspfree_bad over all rows %s'
                     % (a.get('free_arm0_kept'), a.get('cspfree_bad_all_rows')))""")
rep("""                  'da_wskip', 'da_wdrop', 'da_wlag_us', 'da_wdepth'):""",
    """                  'da_wskip', 'da_wdrop', 'da_wlag_us', 'da_wdepth', 'cspfree_look', 'cspfree_hit',
                  'cspfree_spec_miss', 'cspf_have', 'cspf_new'):""")
rep("""    for k in ('cpu_net_us', 'dt_us', 'da_take_us', 'da_miss', 'da_late', 'da_hit', 'da_stale',
              'da_walk_us'):""",
    """    for k in ('cpu_net_us', 'dt_us', 'da_take_us', 'da_miss', 'da_late', 'da_hit', 'da_stale',
              'da_walk_us', 'gpu_busy_us'):""")

# ---- main() ----------------------------------------------------------------------------------------------------------
rep("print('tag %r is not a pred/01 tag (fam108, fam108b, optional _entry1)' % o.tag)",
    "print('tag %r is not a pred/03 tag (frf109, frf109b, optional _entry1)' % o.tag)")
keep("        result['integrity']['IDENTITY'] = (exe_sha == result.get('binary_sha256') == BINARY_SHA)")

body = text.split('"""', 2)[2]          # the code after the module docstring (which names its source)
for stale in ('fam108', 'cspfam=', 'FAMILY_', 'vfm108', 'pred/01', 'pred/02', "'F1'"):
    if stale in body:
        raise SystemExit('stale text left: %r' % stale)
data = text.encode('utf-8')
with open(DST, 'wb') as handle:
    handle.write(data)
print('written %s %d bytes sha256 %s' % (DST, len(data), hashlib.sha256(data).hexdigest()))

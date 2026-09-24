"""Session 110: derive shp110.py (scorer of pred/03_shp110.md, the SHIP run of knob `cspfree`, ABBA cspfree=0|1) from
session 109's frf109.py (the unpinned staging copy, sha256 pinned below).  Copied and edited, not imported.  Every
edit is an anchored replace that must match exactly once; anchors that must survive unchanged are asserted too.
Output bytes are LF / utf-8, written in binary, so two runs give the same bytes.
    python make_shp110.py [<src frf109.py> [<dst shp110.py>]]
"""
import hashlib
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s106_stage/frf109/frf109.py'
DST = sys.argv[2] if len(sys.argv) > 2 else 'C:/kyty/s106_stage/shp110/shp110.py'
SRC_SHA = 'b14d3c5a746cd85b56a474a2c27d87aadbdcd8ece7e208357e0a27691fcfc95f'
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
rep('''"""Session 109, "maximum FPS" track 1 candidate scorer: knob `cspfree` (the walker thread's compute prefetch
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
''',
    '''"""Session 110, the SHIP run of knob `cspfree` (the walker thread's compute prefetch returns before
PipelineCache::m_mutex when a per-thread memo knows (source entry, specialization) and a pipeline for it; design109
B), ABBA `cspfree=0|1` with `dawalk=1 dawalklead=1` in both arms, shipping configuration (compute precache on), sealed
to pred/03_shp110.md.  Derived from session 109's frf109.py (copied, not imported; make_shp110.py): the same
measurement with the session-110 build b3f7a2c9, whose FrameTrace-x rows add cs_sync_new_us and cs_sync_wait_us
(in the schema; no term reads them) and whose `CsStall:` log lines are not a marker; predictions H1-H6.

    python C:/kyty/s110/shp110.py shp110 [--out <json>] [--video-meta <json> --video-report <txt>]
    python C:/kyty/s110/shp110.py <tag> --root <dir> --draft      (fixtures / old logs: arithmetic only)

Ship rule (ROADMAP, decision after session 104; session 108 items 1-2): SHIP cspfree=1 as the new default only if
the run is ADMITTED - including SYNC_COMPILE: over all rows from frame 2100, sum cs_sync_new of arm 1 <= that of
arm 0 + 2 - and S1 d mean dt_us <= -100 us and S2 its 2SE excludes 0, and the video pass vsh110 (gate file
gates_free1.txt, gate text cspfree=1, pinned, >= 3000 frames, 0 one-frame glitches) reads PASS.  Arming (under
control ARMING, unchanged): FREE_DARK_ARM0 (arm-0 kept rows: sum cspfree_look = 0 and sum cspfree_hit = 0),
FREE_ARMED_ARM1 (arm-1 level of cspfree_hit >= 1),
''')
keep('''FREE_NO_BAD (sum cspfree_bad = 0 over all rows).''')

# ---- constants ---------------------------------------------------------------------------------------------------
rep("PRODUCTION_ROOT = 'C:/kyty/s109'", "PRODUCTION_ROOT = 'C:/kyty/s110'")
rep("PRED = 'C:/kyty/s109/pred/03_frf109.md'", "PRED = 'C:/kyty/s110/pred/03_shp110.md'")
keep("PRED_SHA = None          # filled by the executor when pred/03 is sealed")
keep("PRED_BYTES = None        # filled by the executor when pred/03 is sealed")
rep("BINARY_SHA = '2f5932296d564b1098831b75a7fc6c8796d3a9ac7e871ea0c3a1c6b0610a4b77'",
    "BINARY_SHA = 'b3f7a2c957dd344bfd140fe6d04eb2b95ac9387d01dabf5b7dde42b6765b6a82'")
rep("GATES_FILE = 'C:/kyty/s109/gates_base.txt'", "GATES_FILE = 'C:/kyty/s110/gates_base.txt'")
keep("GATES_SHA = '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf'")
keep("PERIOD, START, FIRST_FRAME = 90, 1800, 2100")
keep("KEEP_LO, KEEP_HI = 60, 89")
keep("MIN_PAIRS = 60")
keep("HOLD_S = 600")
keep("ARMS = ('dawalk=1 dawalklead=1 cspfree=0', 'dawalk=1 dawalklead=1 cspfree=1')")
keep("SCHEDULE = '90+1800:%s|%s' % ARMS")
rep("TAG_RE = r'frf109b?(?:_entry1)?'", "TAG_RE = r'shp110b?(?:_entry1)?'")
keep("SHIP_US = -100.0")
keep("VIDEO_MIN_FRAMES = 3000")
# every FrameTrace-x row of the b3f7a2c9 build carries cs_sync_new_us and cs_sync_wait_us after cspfree_moved
# (videoOut.cpp, "Session 110: stall duration on the dispatch.  Raw us."): into the schema
rep("""    'cspfree_bad': 'x', 'cspfree_moved': 'x',
}""", """    'cspfree_bad': 'x', 'cspfree_moved': 'x',
    'cs_sync_new_us': 'x', 'cs_sync_wait_us': 'x',
}""")
keep("SYNC_SLACK = 2")
keep("""FATAL = (b'--- Error ---', b'--- Fatal Error ---', b'--- std::terminate ---', b'--- abort() ---',
         b'ErrorDeviceLost', b'Unhandled exception:', b'GpuWaitSlow:',
         b'AsyncPipelines: skipped draw')""")
keep("""ENV_EXPECTED = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_QUEUE_TRACE': '1',""")
rep("size into frf109.py (only --draft runs without a seal)", "size into shp110.py (only --draft runs without a seal)")

# ---- statistics / selection: kept verbatim (the four audit-109 survivors are killed by fixtures, not by edits) ------
keep("    sd = statistics.stdev(values)")
keep("    return statistics.median(values) if values else None")
keep("        kept = expected[lo:hi]")

# ---- arming: unchanged ---------------------------------------------------------------------------------------------
keep("    checks['FREE_DARK_ARM0'] = look0 == 0 and hit0 == 0")
keep("    checks['FREE_ARMED_ARM1'] = bool((lev[1].get('cspfree_hit') or 0) >= 1)")
keep("    checks['FREE_NO_BAD'] = bad == 0")
keep("    checks['INSTRUMENTS_DARK'] = dark")

# ---- video: vff109 -> vsh110 (the nine checks unchanged) -------------------------------------------------------------
rep('    """pred/03 video pass vff109 (pinned).  Returns (state, detail): state in PASS / FAIL / ABSENT."""',
    '    """pred/03 video pass vsh110 (pinned; gate file gates_free1.txt = gates_base.txt + cspfree=1).  Returns\n'
    '    (state, detail): state in PASS / FAIL / ABSENT."""')
keep("""        'cspfree_1_in_gate_text': ' dawalk=1 ' in gates and ' cspfree=1 ' in gates,""")

# ---- evaluate(): name only ----------------------------------------------------------------------------------------
rep("out = {'scorer': 'frf109.py',", "out = {'scorer': 'shp110.py',")
keep("    controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK")
keep("        'S1_dt_le_-100': dt['mean'] is not None and dt['mean'] <= SHIP_US,")
keep("                                 and dt['mean'] + 2 * dt['se'] < 0),")

# ---- predictions G1-G6 -> H1-H6 (pred/03_shp110 s5) -------------------------------------------------------------------
rep("""    add('G1', 'arm-1 cspfree_hit level in [200, 270] a flip', lev[1].get('cspfree_hit'), 200, 270)
    add('G2', 'arm-1 cspf_have level <= 30 a flip (most prefetches return before the lock)',
        lev[1].get('cspf_have'), None, 30)
    add('G3', 'd mean dt_us in [-300, 0] us', stats['dt_us']['mean'], -300, 0)
    add('G4', 'd mean dt_us <= -100 us (the ship bar) - the discriminating prediction, medium-low confidence',
        stats['dt_us']['mean'], None, SHIP_US)
    add('G5', 'd da_miss in [-30, +30] a flip', stats['da_miss']['mean'], -30, 30)
    add('G6', 'd gpu_busy_us in [-50, +150] us a flip', stats['gpu_busy_us']['mean'], -50, 150)""",
    """    add('H1', 'arm-1 cspfree_hit level in [200, 270] a flip', lev[1].get('cspfree_hit'), 200, 270)
    add('H2', 'arm-1 cspf_have level <= 30 a flip (most prefetches return before the lock)',
        lev[1].get('cspf_have'), None, 30)
    add('H3', 'd mean dt_us in [-300, 0] us', stats['dt_us']['mean'], -300, 0)
    add('H4', 'd mean dt_us <= -100 us (the ship bar) - the discriminating prediction, medium confidence',
        stats['dt_us']['mean'], None, SHIP_US)
    add('H5', 'd da_miss in [-30, +30] a flip', stats['da_miss']['mean'], -30, 30)
    add('H6', 'd gpu_busy_us in [0, +150] us a flip (the mid-pass-upload side effect)',
        stats['gpu_busy_us']['mean'], 0, 150)""")

# ---- verdict texts -------------------------------------------------------------------------------------------------
keep("v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP cspfree=0 (run not admitted)'")
keep("v = 'KEEP cspfree=0 (ship rule S1-S2 on mean dt not met)'")
keep("v = 'SHIP cspfree=1 as the new default (a new build: its video pass is owed, ROADMAP 6)'")
rep("v = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vff109 is read)'",
    "v = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vsh110 is read)'")
keep("v = 'KEEP cspfree=0 (video pass failed)'")

# ---- summary (report only) -------------------------------------------------------------------------------------------
rep("lines = ['frf109.py %s status=%s seal=%s'", "lines = ['shp110.py %s status=%s seal=%s'")

# ---- main() ----------------------------------------------------------------------------------------------------------
rep("print('tag %r is not a pred/03 tag (frf109, frf109b, optional _entry1)' % o.tag)",
    "print('tag %r is not a pred/03 tag (shp110, shp110b, optional _entry1)' % o.tag)")
keep("        result['integrity']['IDENTITY'] = (exe_sha == result.get('binary_sha256') == BINARY_SHA)")

body = text.split('"""', 2)[2]          # the code after the module docstring (which names its source)
for stale in ('frf109', 'vff109', 'pred/03_frf109', 's109', '2f5932296d56', 'fam108', 'cspfam=',
              "'G1'", "'G2'", "'G3'", "'G4'", "'G5'", "'G6'"):
    if stale in body:
        raise SystemExit('stale text left: %r' % stale)
for fresh in ("'H1'", "'H6'", 'shp110', 'vsh110', "'cs_sync_new_us': 'x'", "'cs_sync_wait_us': 'x'"):
    if fresh not in body:
        raise SystemExit('expected text missing: %r' % fresh)
data = text.encode('utf-8')
with open(DST, 'wb') as handle:
    handle.write(data)
print('written %s %d bytes sha256 %s' % (DST, len(data), hashlib.sha256(data).hexdigest()))

"""Session 106: derive gw106.py (scorer of pred/01_gwall.md) from session 104's dwk104.py.
Copied and edited, not imported.  Every edit is an anchored replace that must match exactly once.
    python C:/kyty/s106_stage/make_gw106.py <src dwk104.py> <dst gw106.py>
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


# 1. docstring
start = text.index('"""')
end = text.index('"""', start + 3) + 3
text = text[:start] + '''"""Session 106, "maximum FPS" track 1 item 2 scorer: where the +196 us of GuestGpu wall time that is
not GuestGpu CPU goes under gate `dawalk`.  ABBA `dawalk=0|1` (dawalklead=1 and plkstat=1 in both arms),
KYTY_GPU_WALL=1 in the launch, sealed to pred/01_gwall.md.  Derived from session 104's dwk104.py
(copied, not imported; make_gw106.py).

    python C:/kyty/s106/gw106.py gw106 [--out <json>]
    python C:/kyty/s106/gw106.py <tag> --root <dir> --draft      (fixtures / old logs: arithmetic only)

Decomposition (per pair, arm 1 - arm 0, microseconds a flip):
    D    = dt_us - cpu_net_us                          (GuestGpu wall that is not GuestGpu CPU)
    idle = gw_idle_ns / 1000   blk = gw_blk_ns / 1000   (outside Process: no work / all queues blocked)
    flip = gw_flip_ns / 1000                           (R_WAIT_FLIP_DONE inside Process)
    lock = pl_prog_wait_us + pl_pipe_wait_us + pl_cs_wait_us   (PipelineCache::m_mutex, plkstat)
    R    = D - idle - blk - flip - lock                (other waits, preemption, loop overhead)
Rule (pred/01 s5): D reproduced if mean d D - 2 SE > 0; a term is NAMED if its mean d >= D/2 with
t >= 3; otherwise DIFFUSE.  Nothing ships from this run.
"""''' + text[end:]

# 2. constants
rep("PRODUCTION_ROOT = 'C:/kyty/s105'", "PRODUCTION_ROOT = 'C:/kyty/s106'")
rep("PRED = 'C:/kyty/s105/prev104/pred/03_dawalk.md'", "PRED = 'C:/kyty/s106/pred/01_gwall.md'")
rep("PRED_SHA = '5f088c02c55b185e8f591ce403b0363b70c61a53bcd088b13354fec78e1d4a13'          # filled by the executor when pred/03 is sealed",
    "PRED_SHA = None          # filled by the executor when pred/01 is sealed")
rep("PRED_BYTES = 8515        # filled by the executor when pred/03 is sealed",
    "PRED_BYTES = None        # filled by the executor when pred/01 is sealed")
rep("BINARY_SHA = '16ef56b69c4a99fa6ad613d0dbf57d7f59e0d5443bd6509c55442d83c4780352'",
    "BINARY_SHA = 'd23094dfe42478f8a40907741120837c4cf952ff16b830c1e6e55697dc177db3'")
rep("GATES_FILE = 'C:/kyty/s105/gates_base.txt'", "GATES_FILE = 'C:/kyty/s106/gates_base.txt'")
rep("GATES_SHA = '00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8'",
    "GATES_SHA = '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf'")
rep("ARMS = ('dawalk=0 dawalklead=1', 'dawalk=1 dawalklead=1')",
    "ARMS = ('dawalk=0 dawalklead=1 plkstat=1', 'dawalk=1 dawalklead=1 plkstat=1')")
rep("TAG_RE = r'dwk104b?(?:_entry1)?'", "TAG_RE = r'gw106b?(?:_entry1)?'")
rep("SHIP_US = -150.0", "NAME_T = 3.0              # a term is named at t >= 3 and mean >= D / 2")
rep("""    'pl_proc_n': 'x', 'sh_jobs': 'x',
}""", """    'pl_proc_n': 'x', 'sh_jobs': 'x',
    'gw_idle_ns': 'x', 'gw_idle_n': 'x', 'gw_blk_ns': 'x', 'gw_blk_n': 'x', 'gw_flip_ns': 'x',
    'gw_flip_n': 'x', 'gw_proc_ns': 'x', 'gw_proc_n': 'x', 'gw_cmd_ns': 'x', 'gw_cmd_n': 'x',
    'pl_prog_wait_us': 'x', 'pl_pipe_wait_us': 'x', 'pl_cs_wait_us': 'x', 'pl_prog_n': 'x',
    'pl_pipe_n': 'x', 'pl_cs_n': 'x', 'pl_prog_hold_us': 'x',
}""")
rep("""                'KYTY_GPU_MARKERS': '0'}""", """                'KYTY_GPU_MARKERS': '0', 'KYTY_GPU_WALL': '1'}""")
rep("""PAIR_KEYS = ('cpu_net_us', 'dt_us', 'draws', 'gpu_busy_us', 'rec_n', 'spin_gpu_us', 'da_take_us',
             'da_miss', 'da_late', 'da_hit', 'da_stale', 'da_busy', 'da_walk_us', 'da_queue_us',
             'da_walks', 'da_qcall')""", """PAIR_KEYS = ('cpu_net_us', 'dt_us', 'draws', 'gpu_busy_us', 'rec_n', 'spin_gpu_us', 'da_take_us',
             'da_miss', 'da_late', 'da_hit', 'da_stale', 'da_busy', 'da_walk_us', 'da_queue_us',
             'da_walks', 'da_qcall',
             'D_us', 'gw_idle_us', 'gw_blk_us', 'gw_flip_us', 'lock_wait_us', 'R_us', 'gw_proc_us',
             'gw_cmd_us', 'uncovered_us', 'gw_flip_n', 'gw_idle_n', 'gw_blk_n', 'gw_proc_n',
             'pl_prog_hold_us')
TERMS = ('gw_idle_us', 'gw_blk_us', 'gw_flip_us', 'lock_wait_us', 'R_us')""")

# 3. derived fields
rep("""def derived(row):
    out = dict(row)
    if 'cpu_gpu_us' in row and 'spin_gpu_us' in row:
        out['cpu_net_us'] = row['cpu_gpu_us'] - row['spin_gpu_us']
    return out""", """def derived(row):
    out = dict(row)
    if 'cpu_gpu_us' in row and 'spin_gpu_us' in row:
        out['cpu_net_us'] = row['cpu_gpu_us'] - row['spin_gpu_us']
    gw = ('gw_idle_ns', 'gw_blk_ns', 'gw_flip_ns', 'gw_proc_ns', 'gw_cmd_ns')
    if all(k in row for k in gw):
        for k in gw:
            out[k[:-3] + '_us'] = row[k] / 1000.0
    lk = ('pl_prog_wait_us', 'pl_pipe_wait_us', 'pl_cs_wait_us')
    if all(k in row for k in lk):
        out['lock_wait_us'] = float(sum(row[k] for k in lk))
    if 'cpu_net_us' in out and 'dt_us' in row:
        out['D_us'] = float(row['dt_us'] - out['cpu_net_us'])
        if 'gw_idle_us' in out and 'lock_wait_us' in out:
            out['R_us'] = (out['D_us'] - out['gw_idle_us'] - out['gw_blk_us'] - out['gw_flip_us']
                           - out['lock_wait_us'])
        if 'gw_proc_us' in out:
            out['uncovered_us'] = row['dt_us'] - (out['gw_idle_us'] + out['gw_blk_us'] + out['gw_proc_us']
                                                  + out['gw_cmd_us'])
    return out""")

# 4. arming: add the instruments of this run
rep("""    dark = all(kept_total(rows, sel, arms, a, k) == 0 for a in (0, 1) for k in DARK_KEYS)
    checks['INSTRUMENTS_DARK'] = dark
    return {""", """    dark = all(kept_total(rows, sel, arms, a, k) == 0 for a in (0, 1) for k in DARK_KEYS)
    checks['INSTRUMENTS_DARK'] = dark
    # Session 106: the wall instrument and plkstat armed in BOTH arms (their cost cancels).
    checks['GWALL_ARMED'] = all((lev[a].get('gw_proc_n') or 0) >= 1 and (lev[a].get('gw_idle_n') or 0) >= 0
                                for a in (0, 1))
    checks['PLKSTAT_ARMED'] = all((lev[a].get('pl_prog_n') or 0) >= 1 for a in (0, 1))
    return {""")

# 5. decision: the decomposition rule replaces the ship rule
rep("""    cpu, dt = stats['cpu_net_us'], stats['dt_us']
    rules = {
        'S1_cpu_net_le_-150': cpu['mean'] is not None and cpu['mean'] <= SHIP_US,
        'S2_cpu_net_2se_excludes_0': (cpu['mean'] is not None and cpu['se'] is not None
                                      and cpu['mean'] + 2 * cpu['se'] < 0),
        'S3_dt_same_sign': dt['mean'] is not None and dt['mean'] < 0,
    }
    vstate, vdetail = read_video(video_meta, video_report)
    out['video'] = {'state': vstate, **vdetail}
    decision = {'rules': rules, 'video': vstate}""", """    dd = stats['D_us']
    reproduced = dd['mean'] is not None and dd['se'] is not None and dd['mean'] - 2 * dd['se'] > 0
    named = []
    for k in TERMS:
        s = stats[k]
        if (reproduced and s['mean'] is not None and s['t'] is not None
                and s['mean'] >= dd['mean'] / 2.0 and s['t'] >= NAME_T):
            named.append(k)
    rules = {'R0_D_reproduced': reproduced}
    decision = {'rules': rules, 'named': named, 'video': 'NOT_REQUIRED'}
    out['decomposition'] = {k: stats[k] for k in ('D_us', 'dt_us', 'cpu_net_us') + TERMS
                            + ('gw_proc_us', 'gw_cmd_us', 'uncovered_us', 'gw_flip_n')}""")

# 6. predictions
rep("""    add('D1', 'arm-1 da_wskip level in [7, 9] a flip', lev[1].get('da_wskip'), 7, 9)
    add('D2', 'arm-1 skip/posts identity within +-1 %', arm.get('skip_over_posts_rel'), -0.01, 0.01)
    add('D3', 'd cpu_net_us in [-700, +100] us', stats['cpu_net_us']['mean'], -700, 100)
    add('D4', 'd da_take_us in [0, +800] us', stats['da_take_us']['mean'], 0, 800)
    add('D5', 'd da_miss in [+20, +250] a flip', stats['da_miss']['mean'], 20, 250)
    add('D6', 'd da_late in [0, +12] a flip', stats['da_late']['mean'], 0, 12)
    add('D7', 'd da_walk_us (walker thread in arm 1) in [+200, +1 000] us',
        stats['da_walk_us']['mean'], 200, 1000)
    add('D8', 'd cpu_net_us <= -150 us (the ship bar is met) - the discriminating prediction, '
              'low confidence', stats['cpu_net_us']['mean'], None, SHIP_US)
    return p""", """    add('G1', 'd D_us in [+100, +300] (D reproduced at dwk104 size)', stats['D_us']['mean'], 100, 300)
    add('G2', 'arm-0 D_us level in [600, 1100]', lev[0].get('D_us'), 600, 1100)
    add('G3', 'd R_us >= D/2 (the residual - preemption / other waits - carries it)',
        stats['R_us']['mean'], (stats['D_us']['mean'] or 0) / 2.0, None)
    add('G4', 'd lock_wait_us in [0, +100]', stats['lock_wait_us']['mean'], 0, 100)
    add('G5', 'd gw_flip_us in [-50, +50]', stats['gw_flip_us']['mean'], -50, 50)
    add('G6', 'd dt_us in [-450, -100]', stats['dt_us']['mean'], -450, -100)
    return p""")

# 7. verdict
rep("""    if not admitted:
        v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP dawalk=0 (run not admitted)'
    elif not measured:
        v = 'KEEP dawalk=0 (ship rule S1-S3 not met)'
    elif video == 'PASS':
        v = 'SHIP dawalk=1 as the new default (a new build: its video pass is owed, ROADMAP 6)'
    elif video == 'ABSENT':
        v = 'SHIP_PENDING_VIDEO (S1-S4 met; nothing ships until vwk104 is read)'
    else:
        v = 'KEEP dawalk=0 (video pass failed)'
    out['ship_rules_S1_S3_met'] = measured
    out['verdict'] = v
    out['must_not_be_claimed'] = ('a frame-rate figure; 60 FPS; that the walk is gone from the '
                                  'machine (it moved to another thread); any saving from the '
                                  'arm-1 da_walk_us, which is the walker thread; that route A is '
                                  'licensed by this run')""", """    named = decision.get('named') or []
    if not admitted:
        v = 'DRAFT (no verdict)' if out['draft'] else 'INVALID (run not admitted, nothing named)'
    elif not measured:
        v = 'D NOT REPRODUCED (mean d D - 2 SE <= 0): nothing to decompose'
    elif named:
        v = 'NAMED %s' % ' '.join(named)
    else:
        v = 'DIFFUSE (no single term carries >= D/2 at t >= 3)'
    del video
    out['rule_R0_met'] = measured
    out['verdict'] = v
    out['must_not_be_claimed'] = ('a speedup (nothing ships from this run); 60 FPS; that a named term is '
                                  'removable before a candidate is measured; any split of R')""")

# 8. summary
rep("""    for k in ('cpu_net_us', 'dt_us', 'da_take_us', 'da_miss', 'da_late', 'da_hit', 'da_stale',
              'da_walk_us'):""", """    for k in ('cpu_net_us', 'dt_us', 'D_us', 'gw_idle_us', 'gw_blk_us', 'gw_flip_us', 'lock_wait_us',
              'R_us', 'gw_proc_us', 'gw_cmd_us', 'uncovered_us', 'da_take_us', 'da_miss', 'da_late',
              'da_walk_us'):""")
rep("""        for k in ('dt_us', 'cpu_net_us', 'draws', 'gpu_busy_us', 'rec_n', 'da_walk_us',""",
    """        for k in ('dt_us', 'cpu_net_us', 'D_us', 'gw_idle_us', 'gw_blk_us', 'gw_flip_us', 'lock_wait_us',
                  'R_us', 'gw_proc_us', 'gw_cmd_us', 'uncovered_us', 'gw_flip_n',
                  'draws', 'gpu_busy_us', 'rec_n', 'da_walk_us',""")
rep("lines = ['dwk104.py %s status=%s seal=%s'", "lines = ['gw106.py %s status=%s seal=%s'")
rep("out = {'scorer': 'dwk104.py',", "out = {'scorer': 'gw106.py', 'scorer_sha256': sha256_file(__file__),")

rep("print('tag %r is not a pred/03 tag (dwk104, dwk104b, optional _entry1)' % o.tag)",
    "print('tag %r is not a pred/01 tag (gw106, gw106b, optional _entry1)' % o.tag)")
rep("""    lines.append('  VERDICT: %s' % out.get('verdict'))""",
    """    lines.append('  R0 D reproduced: %s   named (draft too): %s'
                 % (((out.get('decision') or {}).get('rules') or {}).get('R0_D_reproduced'),
                    (out.get('decision') or {}).get('named')))
    lines.append('  VERDICT: %s' % out.get('verdict'))""")

rep("size into dwk104.py (only --draft runs without a seal)", "size into gw106.py (only --draft runs without a seal)")
rep('    """pred/03 s4."""', '    """pred/01 s4 (the dwk104 arming plus the two instruments of this run)."""')
rep('    """pred/03 s5 S5.  Returns', '    """Unused in this run (no video decides).  Kept from dwk104.  Returns')

open(DST, 'w', encoding='utf-8', newline=NL).write(text)
print('written', DST, len(text))

"""Session 119 (ROADMAP 119 item 1): derive g2_119.py from the session-104 stage-1 scorer C:/kyty/s104/a104.py by whole
lines.  Every replaced line must occur exactly once (whole-line anchors); the output is written LF.
    python C:/kyty/s119/make_g2_119.py
"""
import hashlib
from pathlib import Path

SRC = Path('C:/kyty/s104/a104.py')
DST = Path('C:/kyty/s119/g2_119.py')
SRC_SHA = hashlib.sha256(SRC.read_bytes()).hexdigest()
lines = SRC.read_bytes().decode('utf-8').replace('\r\n', '\n').split('\n')

# (old whole line, [new lines]) - a replacement of exactly one line each
EDITS = [
    ('"""Session 104, route A Stage 1 ("kill or go") scorer: runs mut104 (mutwide=0|15) and sh104',
     ['"""Session 119, route A at W = 2 (ROADMAP 118 items 5-6, 119 item 1): the G2 re-measure. Derived by whole lines',
      'from the session-104 stage-1 scorer C:/kyty/s104/a104.py (make_g2_119.py).  Runs mut119 (mutwide=0|15) and sh119']),
    ('(shadowresolve=0|4), sealed to pred/02_a_stage1.md (draft: pred_drafts/02_a_stage1.draft.md).',
     ['(shadowresolve=0|1: ONE concurrent reader = the second context of W = 2), sealed to pred/01_g2_119.md.']),
    ('    python C:/kyty/s104/a104.py --mut mut104 --sh sh104 --out C:/kyty/s104/runs104/a104_score.json',
     ['    python C:/kyty/s119/g2_119.py --mut mut119 --sh sh119 --out C:/kyty/s119/runs119/g2_119_score.json']),
    ('    python C:/kyty/s104/a104.py --mut <tag> --sh <tag> --root <dir> --draft [--period 30 --keep 20:29]',
     ['    python C:/kyty/s119/g2_119.py --mut <tag> --sh <tag> --root <dir> --draft [--period 30 --keep 20:29]']),
    ('SEAL.  Production scoring refuses to run (exit 2) unless the sealed text pred/02_a_stage1.md is',
     ['SEAL.  Production scoring refuses to run (exit 2) unless the sealed text pred/01_g2_119.md is']),
    ('What is decided (pred/02 section numbers):',
     ['What is decided (the section numbers of session-104 pred/02, carried into pred/01_g2_119.md):']),
    ('        spine     = sh104 arm-0 level of da_walk_us - da_queue_us (the GuestGpu walk, dawalk=0)',
     ['        spine     = max(mut119 arm-0 level of da_walk_us - da_queue_us, SPINE_DIRECT_US = 959): with dawalk=1',
      '                    the proxy is walker-thread time; 959 us is the spine plan measured on GuestGpu (spk118,',
      '                    own timer, a lower bound)']),
    ('        T4        = mean paired d cpu_net_us of sh104 (arm 4 - arm 0)',
     ['        T4        = mean paired d cpu_net_us of sh119 (arm 1 - arm 0): the W = 2 tax T2 (key name kept)']),
    ('        G         = cpu_net - [S_ctx + F*(cpu_net - S_ctx)] - spine - T4,  F = 0.30',
     ['        G         = cpu_net - [S_ctx + F*(cpu_net - S_ctx)] - spine - T4,  F = 0.555 (spk118 median',
      '                    k4_w2_fmax: the larger half of the W = 2 cut at pass starts)']),
    ("PRODUCTION_ROOT = 'C:/kyty/s104'", ["PRODUCTION_ROOT = 'C:/kyty/s119'"]),
    ("PRED = 'C:/kyty/s104/pred/02_a_stage1.md'", ["PRED = 'C:/kyty/s119/pred/01_g2_119.md'"]),
    ("PRED_SHA = '29324c0c29603250255b5879d48ae2e9d8574672ef7291ceb27ebc44de2fbb8a'          # filled by the executor when pred/02 is sealed",
     ['PRED_SHA = None          # filled by the executor when pred/01_g2_119.md is sealed']),
    ('PRED_BYTES = 16476        # filled by the executor when pred/02 is sealed',
     ['PRED_BYTES = None        # filled by the executor when pred/01_g2_119.md is sealed']),
    ("BINARY_SHA = '16ef56b69c4a99fa6ad613d0dbf57d7f59e0d5443bd6509c55442d83c4780352'",
     ["BINARY_SHA = 'd3a981a23fc1c5df651eef2a93ff1f02a8bffd04416adea2fd5cd2218e290f64'"]),
    ("GATES_FILE = 'C:/kyty/s104/gates_base.txt'", ["GATES_FILE = 'C:/kyty/s119/gates_base.txt'"]),
    ("GATES_SHA = '00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8'",
     ["GATES_SHA = '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf'"]),
    ("SH_ARMS = ('shadowresolve=0 shadowmask=3', 'shadowresolve=4 shadowmask=3')",
     ["SH_ARMS = ('shadowresolve=0 shadowmask=3', 'shadowresolve=1 shadowmask=3')"]),
    ("                tag_re=r'mut104b?(?:_entry1)?'),", ["                tag_re=r'mut119b?(?:_entry1)?'),"]),
    ("               tag_re=r'sh104b?(?:_entry1)?'),", ["               tag_re=r'sh119b?(?:_entry1)?'),"]),
    ('# pred/02 s5 constants', ['# pred/02 s5 constants, as fixed by ROADMAP 118 item 6 / 119 item 1']),
    ("F_SERIAL = 0.30          # the ROADMAP rule's f at DCB granularity",
     ["F_SERIAL = 0.555         # f2: spk118 median k4_w2_fmax (the larger half of the W = 2 cut)"]),
    ('F_SENS = 0.39            # the upper end of f_max (DESIGN_82 s1), sensitivity only',
     ['F_SENS = 0.564           # spk118 p90 of k4_w2_fmax, sensitivity only',
      'SPINE_DIRECT_US = 959.0  # spk118 arm-P spine_ns (the plan on GuestGpu, own timer, a lower bound)']),
    ("        for k in ('sh_jobs', 'da_wjobs'):",
     ["        for k in ('sh_jobs',):                 # da_wjobs: the dawalk=1 walker is the production path"]),
    ("    checks['SH_FOUR_WORKERS'] = sorted(counts['shadow_workers']) == [0, 1, 2, 3]",
     ["    checks['SH_ONE_WORKER'] = sorted(counts['shadow_workers']) == [0]"]),
    ("        for k in ('a_hold_us', 'a_mut_us', 'mw_n', 'pl_em_n', 'pl_proc_n', 'pl_prog_n', 'da_wjobs'):",
     ["        for k in ('a_hold_us', 'a_mut_us', 'mw_n', 'pl_em_n', 'pl_proc_n', 'pl_prog_n'):"]),
    ("    t['spine'] = lvl(sh, 0, 'spine_us')",
     ["    t['spine'] = (None if lvl(mut, 0, 'spine_us') is None",
      "                  else max(lvl(mut, 0, 'spine_us'), SPINE_DIRECT_US))",
      "    t['spine_sh_arm0'] = lvl(sh, 0, 'spine_us')"]),
    ("    c['G_f039'] = g_of(t['cpu_net'], c['S_ctx'], t['spine'], c['T4'], F_SENS)",
     ["    c['G_fsens'] = g_of(t['cpu_net'], c['S_ctx'], t['spine'], c['T4'], F_SENS)"]),
    ("    h['G_f039'] = g_of(t['cpu_net'], h['S_ctx'], t['spine'], h['T4'], F_SENS)",
     ["    h['G_fsens'] = g_of(t['cpu_net'], h['S_ctx'], t['spine'], h['T4'], F_SENS)"]),
    ("    add('A3', 'S_lo (arm-0 a_mut_us) in [11 500, 14 500] us', lvl(mut, 0, 'a_mut_us'), 11500, 14500)",
     ["    add('A3', 'S_lo (arm-0 a_mut_us) in [11 000, 15 000] us', lvl(mut, 0, 'a_mut_us'), 11000, 15000)"]),
    ("    add('A4', 'S_raw (arm-1 a_mut_us) in [18 500, 21 500] us', lvl(mut, 1, 'a_mut_us'), 18500, 21500)",
     ["    add('A4', 'S_raw (arm-1 a_mut_us) in [17 500, 21 500] us', lvl(mut, 1, 'a_mut_us'), 17500, 21500)"]),
    ("    add('A8', 'spine (sh104 arm 0) in [900, 1 300] us', g['terms']['spine'], 900, 1300)",
     ["    add('A8', 'spine = max(mut119 arm-0 proxy, 959) in [959, 1 500] us', g['terms']['spine'], 959, 1500)"]),
    ("    add('A9', 'cpu_net (sh104 arm 0) in [29 800, 31 600] us', g['terms']['cpu_net'], 29800, 31600)",
     ["    add('A9', 'cpu_net (sh119 arm 0) in [29 000, 32 000] us', g['terms']['cpu_net'], 29000, 32000)"]),
    ("    add('A10a', 'T4 in [+700, +2 600] us', g['terms']['T4'], 700, 2600)",
     ["    add('A10a', 'T2 (shadowresolve=1) in [+700, +2 600] us', g['terms']['T4'], 700, 2600)"]),
    ("    add('A11a', 'G central in [4 000, 8 000] us', g['central']['G'], 4000, 8000)",
     ["    add('A11a', 'G2 central in [1 000, 4 500] us', g['central']['G'], 1000, 4500)"]),
    ("    add('A11b', 'G central >= 3 000 us (A proceeds) - the discriminating prediction',",
     ["    add('A11b', 'G2 central < 3 000 us (A closes) - the discriminating prediction',"]),
    ("        g['central']['G'], BAR_US, None)",
     ["        g['central']['G'], None, BAR_US - 1e-9)"]),
    ("        lines.append('    E_rec %s E_com %s W_E(s101) %s | spine %s (mut arm0 %s, pref-based %s)'",
     ["        lines.append('    E_rec %s E_com %s W_E(s101) %s | spine %s (mut arm0 proxy %s, sh arm0 proxy %s, '",
      "                     'pref-based %s - meaningless at dawalk=1)'"]),
    ("                        fmt(t['spine_mut_arm0']), fmt(t['spine_pref_mut_arm0'])))",
     ["                        fmt(t['spine_mut_arm0']), fmt(t['spine_sh_arm0']), fmt(t['spine_pref_mut_arm0'])))"]),
    ("                     ' pref spine: %s)'", ["                     ' pref spine, meaningless at dawalk=1: %s)'"]),
    ("        cpu_net   = sh104 arm-0 level of cpu_net_us = cpu_gpu_us - spin_gpu_us (uninstrumented)",
     ["        cpu_net   = sh119 arm-0 level of cpu_net_us = cpu_gpu_us - spin_gpu_us (uninstrumented)"]),
    ("        S_raw     = mut104 arm-1 level of a_mut_us (six amut sites + four mutwide surfaces)",
     ["        S_raw     = mut119 arm-1 level of a_mut_us (six amut sites + four mutwide surfaces)"]),
    ("        P_mw      = mean paired d cpu_net_us of mut104 (arm1 - arm0), its 2*SE",
     ["        P_mw      = mean paired d cpu_net_us of mut119 (arm1 - arm0), its 2*SE"]),
    ("        T_in      = 5*pl_em_n + 3*(pl_prog_n + pl_pipe_n + pl_cs_n) + a_mut_n   (mut104 arm 1)",
     ["        T_in      = 5*pl_em_n + 3*(pl_prog_n + pl_pipe_n + pl_cs_n) + a_mut_n   (mut119 arm 1)"]),
    ("  s6  THE RULE, applied to G (central), as ROADMAP s0.1 item 6 records it: G < 3000 us => route A",
     ["  s6  THE RULE, applied to G (central), as ROADMAP 118 item 6 records it: G2 < 3000 us => route A"]),
    ("      CLOSED for max FPS; G >= 3000 us => route A proceeds by stages.  G^ (the ceiling) is printed",
     ["      CLOSED for max FPS; G2 >= 3000 us => stage 3 resumes (label A_PROCEEDS_BY_STAGES).  G^ is printed"]),
    ("        lines.append('    T4 %s (2SE %s) sh_push %s | T4 on dt %s (2SE %s)'",
     ["        lines.append('    T2 %s (2SE %s) sh_push %s | T2 on dt %s (2SE %s)'"]),
    ("        lines.append('  CENTRAL: S_now %s E_move %s S_ctx %s T4 %s  ->  G %s  (f=0.39: %s; wall: %s;'",
     ["        lines.append('  CENTRAL: S_now %s E_move %s S_ctx %s T2 %s  ->  G2 %s  (f=0.564: %s; wall: %s;'"]),
    ("                        fmt(c.get('T4')), fmt(c.get('G')), fmt(c.get('G_f039')),",
     ["                        fmt(c.get('T4')), fmt(c.get('G')), fmt(c.get('G_fsens')),"]),
    ("        lines.append('  CEILING: S_now %s E_move %s S_ctx %s T4 %s  ->  G^ %s  (f=0.39: %s)'",
     ["        lines.append('  CEILING: S_now %s E_move %s S_ctx %s T2 %s  ->  G2^ %s  (f=0.564: %s)'"]),
    ("                        fmt(h.get('T4')), fmt(h.get('G')), fmt(h.get('G_f039'))))",
     ["                        fmt(h.get('T4')), fmt(h.get('G')), fmt(h.get('G_fsens'))))"]),
    ("        lines.append('  T4 that would bring the CENTRAL G to the bar: %s us; H/M %s; area xrun %s %%'",
     ["        lines.append('  T2 that would bring the CENTRAL G2 to the bar: %s us; H/M %s; area xrun %s %%'"]),
    ("        lines.append('  RULE (G^ < %.0f => A CLOSED): if admitted %s ; VERDICT %s %s'",
     ["        lines.append('  RULE (central G2 < %.0f => A CLOSED): if admitted %s ; VERDICT %s %s'"]),
    ("    lines = ['a104.py status=%s seal=%s' % (out['status'], out.get('pred_sha256'))]",
     ["    lines = ['g2_119.py status=%s seal=%s' % (out['status'], out.get('pred_sha256'))]"]),
    ("    out = {'scorer': 'a104.py', 'pred': PRED, 'pred_sha256': None, 'draft': bool(draft)}",
     ["    out = {'scorer': 'g2_119.py', 'pred': PRED, 'pred_sha256': None, 'draft': bool(draft)}"]),
    ("        'a speedup (Stage 1 changes nothing that ships); that route A will reach G; that f = 0.30 '",
     ["        'a speedup (nothing ships); that route A will reach G2; that f2 = 0.555 was measured in this run '",
      "        '(it is the spk118 census); that shadowresolve=1 is the tax of a writing second context; '"]),
    ("        'was measured; that the shadow probes reproduce the contention of writing contexts; a '",
     ["        'that the shadow probes reproduce the contention of writing contexts; a '"]),
    ("                print('tag %r is not a pred/02 %s tag' % (tag, kind))",
     ["                print('tag %r is not a pred/01_g2_119 %s tag' % (tag, kind))"]),
    ("        raise SealError('PRED_SHA / PRED_BYTES are not filled: seal %s and put its sha256 and '",
     ["        raise SealError('PRED_SHA / PRED_BYTES are not filled: seal %s and put its sha256 and '"]),
    ("                        'size into a104.py (only --draft runs without a seal)' % path)",
     ["                        'size into g2_119.py (only --draft runs without a seal)' % path)"]),
]

out = []
used = set()
index = {}
for i, line in enumerate(lines):
    index.setdefault(line, []).append(i)
for old, new in EDITS:
    hits = index.get(old, [])
    if len(hits) != 1:
        raise SystemExit('anchor found %d times: %r' % (len(hits), old))
for i, line in enumerate(lines):
    rep = next((new for old, new in EDITS if old == line), None)
    out.extend(rep if rep is not None else [line])
text = '\n'.join(out)
text = text.replace('"""\nimport argparse', '\nDerived from a104.py sha256 %s.\n"""\nimport argparse' % SRC_SHA, 1)
DST.write_bytes(text.encode('utf-8'))
print('wrote', DST, hashlib.sha256(DST.read_bytes()).hexdigest())

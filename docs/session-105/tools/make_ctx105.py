"""Session 105: derive ctx105.py (the M3.1 A/A: ABBA ctxtick=0|1, point |d cpu_net| <= 90 us) from lead105.py."""
import hashlib

SRC = 'C:/kyty/s105/lead105.py'
DST = 'C:/kyty/s105/ctx105.py'
PRED = 'C:/kyty/s105/pred/02_m31.md'
s = open(SRC, encoding='utf-8').read()


def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (old[:90], n)
    s = s.replace(old, new)


i = s.index('"""', 3) + 3
s = '''"""Session 105, route A milestone M3.1, item P2 of pred/02_m31.md: the A/A ABBA `ctxtick=0|1` (run abb105,
900 s, pinned). PASS iff ADMITTED and the POINT estimate |d cpu_net_us| (arm ctxtick=1 - arm ctxtick=0) <= 90 us;
d mean dt_us and both 2SE reported. Derived from lead105.py (copied, not imported).

    python C:/kyty/s105/ctx105.py abb105 [--out <json>]
"""''' + s[i:]
data = open(PRED, 'rb').read()
import re
s = re.sub(r"PRED = 'C:/kyty/s105/pred/01_dawalklead.md'", "PRED = 'C:/kyty/s105/pred/02_m31.md'", s, count=1)
s = re.sub(r"PRED_SHA = '[0-9a-f]{64}'", "PRED_SHA = '%s'" % hashlib.sha256(data).hexdigest(), s, count=1)
s = re.sub(r"PRED_BYTES = \d+", 'PRED_BYTES = %d' % len(data), s, count=1)
rep("BINARY_SHA = '61ae73476eac343fcca3554924496ec0c50da536826ecab6dea7a1e4548e4bd1'",
    "BINARY_SHA = '8de4a93bb6c5693871918d0c8d88e1b3ea5b147d0e34c96b5a039a39435af8f0'")
rep("HOLD_S = 600", "HOLD_S = 900")
rep("ARMS = ('dawalk=1 dawalklead=1', 'dawalk=1 dawalklead=2')", "ARMS = ('ctxtick=0', 'ctxtick=1')")
rep("TAG_RE = r'lead105b?(?:_entry1)?'", "TAG_RE = r'abb105b?(?:_entry1)?'")
rep("SHIP_US = -100.0          # on d mean dt_us (ROADMAP, decision after session 104)",
    "SHIP_US = 90.0            # |d cpu_net_us| point bound (pred/02_m31.md P2)")
rep("DARK_KEYS = ('mw_n', 'a_hold_us', 'a_mut_us', 'pl_em_n', 'pl_proc_n', 'sh_jobs')",
    "DARK_KEYS = ('mw_n', 'a_hold_us', 'a_mut_us', 'pl_em_n', 'pl_proc_n', 'sh_jobs', 'ctx_chk_n', 'ctx_chk_bad')")
rep('''        'S1_dt_le_-100': dt['mean'] is not None and dt['mean'] <= SHIP_US,
        'S2_dt_2se_excludes_0': (dt['mean'] is not None and dt['se'] is not None
                                 and dt['mean'] + 2 * dt['se'] < 0),''',
    '''        'P2_abs_cpu_net_point_le_90': cpu['mean'] is not None and abs(cpu['mean']) <= SHIP_US,''')
rep("""        v = 'DRAFT (no verdict)' if out['draft'] else 'KEEP dawalklead=1 (run not admitted)'""",
    """        v = 'DRAFT (no verdict)' if out['draft'] else 'P2 FAIL (run not admitted)'""")
rep("""        v = 'KEEP dawalklead=1 (ship rule S1-S2 on mean dt not met)'""", """        v = 'P2 FAIL (|d cpu_net| point > 90 us)'""")
rep("""    elif video == 'PASS':
        v = 'SHIP dawalklead=2 as the new default (a new build: its video pass is owed, ROADMAP 6)'
    elif video == 'ABSENT':
        v = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vld105 is read)'
    else:
        v = 'KEEP dawalklead=1 (video pass failed)'""", """    else:
        v = 'P2 PASS (the A/A holds at the point; video, checks and entries are separate items)'""")
rep("""    out['ship_rules_S1_S2_met'] = measured""", """    out['p2_met'] = measured""")
i = s.index("    add('L1',")
j = s.index('    return p', i)
s = s[:i] + """    add('Q3', '|d cpu_net_us| point <= 60 us', abs(stats['cpu_net_us']['mean']) if stats['cpu_net_us']['mean'] is not None else None, 0, 60)
""" + s[j:]
open(DST, 'w', encoding='utf-8', newline='\n').write(s)
print('written', DST)

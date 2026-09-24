"""Session 113, ROADMAP 0.1 "СЕССИЯ 113" item 17: vbn113e.py / test_vbn113e.py / mut_vbn113e.py from the vbn113d files
(draft copies, sha pinned) by WHOLE-LINE anchored replacements (item 16: a prefix anchor lost a fixture in make_vbn113d;
every anchor here must end with a newline and start at a line start, asserted).  Changes: the build cf22e223 with the
GC-trigger measurement env KYTY_BUFFER_GC_TRIGGER_SHIFT_MB=1024 (a forced OLD regime); admission terms ENV_SHIFT and
GC_LINE; tags vbn113k, vbn113l; the lost B1 edge fixture restored.  Byte-reproducible.

    python C:/kyty/s106_stage/make_vbn113e.py
"""
import hashlib
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')
PINS = {'vbn113d.py': 'a283188b', 'test_vbn113d.py': '42bb5ee6', 'mut_vbn113d.py': '9c4fd32c'}
NEW_SHA = 'cf22e2236613556f046107804e6545d09fba7833fc23c72cde010e06ca395121'
OLD_SHA = '5ba0e1881565dc922651cb15e3df0fb9ddec39a33d117428cb6faf27a4948ba3'


def load(name):
    s = (STAGE / name).read_bytes().decode('utf-8').replace('\r\n', '\n')
    assert hashlib.sha256(s.encode('utf-8')).hexdigest().startswith(PINS[name]), name
    return s


def derive(src, dst, pairs):
    s = load(src)
    for a, b in pairs:
        assert a.endswith('\n') and b.endswith('\n'), (src, 'not whole lines', a[:80])
        assert s.startswith(a) or ('\n' + a) in s, (src, 'anchor not at a line start', a[:80])
        assert s.count(a) == 1, (src, a[:80], s.count(a))
        s = s.replace(a, b)
    (STAGE / dst).write_bytes(s.encode('utf-8'))
    print(dst, hashlib.sha256(s.encode('utf-8')).hexdigest())


derive('vbn113d.py', 'vbn113e.py', [
    ('"""Session 113, pred/01d_vbn113d.md (from vbn113c.py by make_vbn113d.py - ROADMAP item 14: the build reads the region\n'
     'stamp under the lock of the collect, so bda_nmiss is exact and bda_nrace is information; vbn113c.py came from\n'
     'vbn113b.py by make_vbn113c.py): the verify run of knob `bdanarrow` in mode 2 (today\'s global invalidation of the BDA\n',
     '"""Session 113, pred/01e_vbn113e.md (from vbn113d.py by make_vbn113e.py - ROADMAP item 17: the same verify run with the\n'
     'buffer-GC trigger lowered by KYTY_BUFFER_GC_TRIGGER_SHIFT_MB=1024, a forced OLD regime; vbn113d.py came from vbn113c.py\n'
     'by make_vbn113d.py): the verify run of knob `bdanarrow` in mode 2 (today\'s global invalidation of the BDA\n'),
    ('bda_nmiss; the moved ones are races, bda_nrace), Sky Garden 300 s, pinned, compute precache ON.\n',
     'bda_nmiss; the moved ones are races, bda_nrace), Sky Garden 300 s, pinned, compute precache ON, GC trigger -1024 MiB.\n'),
    ('    python C:/kyty/s113/vbn113d.py [--tag vbn113g|vbn113h|vbn113i|vbn113j] [--root C:/kyty/s113] [--out <json>]\n',
     '    python C:/kyty/s113/vbn113e.py [--tag vbn113k|vbn113l] [--root C:/kyty/s113] [--out <json>]\n'),
    ("TAGS = ('vbn113g', 'vbn113h', 'vbn113i', 'vbn113j')\n", "TAGS = ('vbn113k', 'vbn113l')\n"),
    ("PRED = 'C:/kyty/s113/pred/01d_vbn113d.md'\n", "PRED = 'C:/kyty/s113/pred/01e_vbn113e.md'\n"),
    ("PRED_SHA = None     # pred/01d_vbn113d.md sealed\n", "PRED_SHA = None     # pred/01e_vbn113e.md sealed\n"),
    ("PRED_BYTES = None   # pred/01d_vbn113d.md sealed\n", "PRED_BYTES = None   # pred/01e_vbn113e.md sealed\n"),
    ("BINARY_SHA = '%s'\n" % OLD_SHA, "BINARY_SHA = '%s'\n" % NEW_SHA),
    ("MAX_GPU_UTIL = 10.0        # pre_run gpu_util_median of the launcher: nothing else on the GPU before the run\n",
     "MAX_GPU_UTIL = 10.0        # pre_run gpu_util_median of the launcher: nothing else on the GPU before the run\n"
     "SHIFT_ENV = 'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB'\n"
     "SHIFT_MB = 1024            # ROADMAP item 17: the buffer-GC trigger lowered by 1024 MiB (a forced OLD regime)\n"
     r"GC_LINE = re.compile(rb'^BufferGc: budget=(\d+) trigger=(\d+) critical=(\d+) shift_mb=(\d+)')" + '\n'),
    ("    if env.get('KYTY_GPU_CLOCK_PIN') != '1':\n        errors.append('ENV_PIN')\n",
     "    if env.get('KYTY_GPU_CLOCK_PIN') != '1':\n        errors.append('ENV_PIN')\n"
     "    if env.get(SHIFT_ENV) != str(SHIFT_MB):\n        errors.append('ENV_SHIFT')\n"),
    ("    xns = []\n", "    xns = []\n    gc_lines = []\n"),
    ("            if line.startswith(b'GpuClockPin:'):\n                pins += 1\n",
     "            g = GC_LINE.match(line)\n            if g:\n                gc_lines.append(tuple(int(x) for x in g.groups()))\n"
     "            if line.startswith(b'GpuClockPin:'):\n                pins += 1\n"),
    ("    if pins != 1 or pin1 != 1:\n        errors.append('PIN_ONCE')\n",
     "    if pins != 1 or pin1 != 1:\n        errors.append('PIN_ONCE')\n"
     "    if len(gc_lines) != 1 or gc_lines[0][3] != SHIFT_MB or not gc_lines[0][1] < gc_lines[0][2]:\n"
     "        errors.append('GC_LINE')      # one constructor line: the shift took effect, the trigger stays below critical\n"),
    ("               regime_old=regime_old, level=level, scan_rows=len(scans), pre_run_gpu_util=pr.get('gpu_util_median'))\n",
     "               regime_old=regime_old, level=level, scan_rows=len(scans), pre_run_gpu_util=pr.get('gpu_util_median'),\n"
     "               gc_lines=gc_lines)\n"),
    ("        print('  main rows %s  pre_run gpu util %s' % (res.get('main_rows'), res.get('pre_run_gpu_util')))\n",
     "        print('  main rows %s  pre_run gpu util %s' % (res.get('main_rows'), res.get('pre_run_gpu_util')))\n"
     "        print('  BufferGc lines (budget, trigger, critical, shift_mb) %s' % (res.get('gc_lines'),))\n"),
])

GC_OK = 'BufferGc: budget=14901313536 trigger=8673610957 critical=13183326618 shift_mb=1024'
derive('test_vbn113d.py', 'test_vbn113e.py', [
    ('"""Session 113: fixtures for vbn113d.py (from test_vbn113c.py by make_vbn113d.py; that from test_vbn113b.py) - every '
     'verdict branch (GO, NO_GO, INVESTIGATE, NOT_EVALUABLE, NOT_ADMITTED),\n',
     '"""Session 113: fixtures for vbn113e.py (from test_vbn113d.py by make_vbn113e.py; that from test_vbn113c.py) - every '
     'verdict branch (GO, NO_GO, INVESTIGATE, NOT_EVALUABLE, NOT_ADMITTED),\n'),
    ("    python test_vbn113d.py <vbn113d.py>\n", "    python test_vbn113e.py <vbn113e.py>\n"),
    ("BASE = Path('C:/kyty/s106_stage/fx_vbn113d')\n", "BASE = Path('C:/kyty/s106_stage/fx_vbn113e')\n"),
    ("spec = importlib.util.spec_from_file_location('vbn113d', SRC)\n",
     "spec = importlib.util.spec_from_file_location('vbn113e', SRC)\n"),
    ("seal.write_bytes(b'fixture seal 113 vbn d')\n", "seal.write_bytes(b'fixture seal 113 vbn e')\n"),
    ("GATES = 'dawalk=1 smemocheck=0 dabatch=8 fslean=0'\n",
     "GATES = 'dawalk=1 smemocheck=0 dabatch=8 fslean=0'\nGC_OK = '%s'\n" % GC_OK),
    ("         evict=1, race=0, qfree=1100, hit=266, free_bad=0, lines=(), stdout=None, tag='vbn113g', gpu_util=0.0,\n",
     "         evict=1, race=0, qfree=1100, hit=266, free_bad=0, lines=(), stdout=None, tag='vbn113k', gpu_util=0.0,\n"),
    ("    env = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0'}\n",
     "    env = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0',\n"
     "           'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '1024'}\n"),
    ("    out = list(bad.get('pin_lines', ['GpuClockPin: mode 1'])) + list(lines)\n",
     "    out = list(bad.get('pin_lines', ['GpuClockPin: mode 1'])) + list(bad.get('gc_lines', [GC_OK])) + list(lines)\n"),
    ("    ('GO_tag_h', dict(tag='vbn113h'), 'GO', []),\n    ('GO_tag_i', dict(tag='vbn113i'), 'GO', []),\n"
     "    ('GO_tag_j', dict(tag='vbn113j'), 'GO', []),\n",
     "    ('GO_tag_l', dict(tag='vbn113l'), 'GO', []),\n"),
    ("    ('TAG', dict(tag='vbn113k'), 'NOT_ADMITTED', ['TAG']),\n    ('TAG_old', dict(tag='vbn113c'), 'NOT_ADMITTED', ['TAG']),\n",
     "    ('TAG', dict(tag='vbn113m'), 'NOT_ADMITTED', ['TAG']),\n    ('TAG_old', dict(tag='vbn113j'), 'NOT_ADMITTED', ['TAG']),\n"),
    ("    ('ENV_PRECACHE', dict(env={'KYTY_PIPELINE_PRECACHE': 'gfx'}), 'NOT_ADMITTED', ['ENV_FORBIDDEN']),\n",
     "    ('ENV_PRECACHE', dict(env={'KYTY_PIPELINE_PRECACHE': 'gfx'}), 'NOT_ADMITTED', ['ENV_FORBIDDEN']),\n"
     "    ('ENV_SHIFT_missing', dict(env_drop=['KYTY_BUFFER_GC_TRIGGER_SHIFT_MB']), 'NOT_ADMITTED', ['ENV_SHIFT']),\n"
     "    ('ENV_SHIFT_wrong', dict(env={'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '512'}), 'NOT_ADMITTED', ['ENV_SHIFT']),\n"
     "    ('GC_LINE_missing', dict(gc_lines=[]), 'NOT_ADMITTED', ['GC_LINE']),\n"
     "    ('GC_LINE_two', dict(gc_lines=[GC_OK, GC_OK]), 'NOT_ADMITTED', ['GC_LINE']),\n"
     "    ('GC_LINE_shift0', dict(gc_lines=[GC_OK.replace('shift_mb=1024', 'shift_mb=0')]), 'NOT_ADMITTED', ['GC_LINE']),\n"
     "    ('GC_LINE_shift_big', dict(gc_lines=[GC_OK.replace('shift_mb=1024', 'shift_mb=10240')]), 'NOT_ADMITTED',\n"
     "     ['GC_LINE']),\n"
     "    ('GC_LINE_trigger_edge_fail', dict(gc_lines=['BufferGc: budget=9 trigger=5 critical=5 shift_mb=1024']),\n"
     "     'NOT_ADMITTED', ['GC_LINE']),\n"
     "    ('GC_LINE_trigger_edge_ok', dict(gc_lines=['BufferGc: budget=9 trigger=4 critical=5 shift_mb=1024']), 'GO', []),\n"
     "    ('GC_LINE_prefix', dict(gc_lines=['x BufferGc: budget=9 trigger=4 critical=5 shift_mb=1024']), 'NOT_ADMITTED',\n"
     "     ['GC_LINE']),\n"),
    ("CONSTANTS = dict(TAGS=('vbn113g', 'vbn113h', 'vbn113i', 'vbn113j'), TAIL=' bdanarrow=2', HOLD_S=300, MIN_ROWS=5000, "
     "REGIME_OLD=500,\n",
     "CONSTANTS = dict(TAGS=('vbn113k', 'vbn113l'), TAIL=' bdanarrow=2', HOLD_S=300, MIN_ROWS=5000, REGIME_OLD=500,\n"),
    ("                 MIN_WOULD=1000, MAX_GPU_UTIL=10.0,\n",
     "                 MIN_WOULD=1000, MAX_GPU_UTIL=10.0, SHIFT_ENV='KYTY_BUFFER_GC_TRIGGER_SHIFT_MB', SHIFT_MB=1024,\n"),
    ("                 BINARY_SHA='%s')\n" % OLD_SHA, "                 BINARY_SHA='%s')\n" % NEW_SHA),
    ("    (dict(race=1), 'B1', True),                           # B1 reads BAD, which races never enter (bad_race) "
     "(dict(nmiss=1), 'B1', False),\n",
     "    (dict(race=1), 'B1', True),                           # B1 reads BAD, which races never enter (bad_race)\n"
     "    (dict(nmiss=1), 'B1', False),                         # restored (ROADMAP item 16: lost by make_vbn113d)\n"),
])

derive('mut_vbn113d.py', 'mut_vbn113e.py', [
    ('"""Session 113: mutants of vbn113d.py (from mut_vbn113c.py by make_vbn113d.py) - each must be killed by '
     'test_vbn113d.py.\n'
     'Run through mutlib on the SEALED copy (items 7, 13, 14).\n',
     '"""Session 113: mutants of vbn113e.py (from mut_vbn113d.py by make_vbn113e.py) - each must be killed by '
     'test_vbn113e.py.\n'
     'Run through mutlib v2 on the SEALED copy, --control --no-memo (items 15, 17).\n'),
    ("TARGET = Path(sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s106_stage/vbn113d.py')\n",
     "TARGET = Path(sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s106_stage/vbn113e.py')\n"),
    ("TEST = Path('C:/kyty/s106_stage/test_vbn113d.py')\n", "TEST = Path('C:/kyty/s106_stage/test_vbn113e.py')\n"),
    ("    ('tags', \"TAGS = ('vbn113g', 'vbn113h', 'vbn113i', 'vbn113j')\", \"TAGS = ('vbn113g', 'vbn113h', 'vbn113i', "
     "'vbn113j', 'vbn113k')\"),\n"
     "    ('tags_drop', \"TAGS = ('vbn113g', 'vbn113h', 'vbn113i', 'vbn113j')\", \"TAGS = ('vbn113g', 'vbn113h', 'vbn113i')\"),\n",
     "    ('tags', \"TAGS = ('vbn113k', 'vbn113l')\", \"TAGS = ('vbn113k', 'vbn113l', 'vbn113m')\"),\n"
     "    ('tags_drop', \"TAGS = ('vbn113k', 'vbn113l')\", \"TAGS = ('vbn113k',)\"),\n"),
    ("    ('evaluable', \"elif not regime_old:\", \"elif False:\"),\n",
     "    ('evaluable', \"elif not regime_old:\", \"elif False:\"),\n"
     "    ('shift_value', 'SHIFT_MB = 1024 ', 'SHIFT_MB = 512 '),\n"
     r"""    ('shift_env', "    if env.get(SHIFT_ENV) != str(SHIFT_MB):\n        errors.append('ENV_SHIFT')\n", ''),""" + '\n'
     "    ('shift_env_any', 'if env.get(SHIFT_ENV) != str(SHIFT_MB):', 'if SHIFT_ENV not in env:'),\n"
     "    ('gc_count', 'if len(gc_lines) != 1 or ', 'if len(gc_lines) < 1 or '),\n"
     "    ('gc_shift', ' or gc_lines[0][3] != SHIFT_MB', ''),\n"
     "    ('gc_trigger', 'not gc_lines[0][1] < gc_lines[0][2]', 'not gc_lines[0][1] <= gc_lines[0][2]'),\n"
     "    ('gc_trigger_off', ' or not gc_lines[0][1] < gc_lines[0][2]:', ':'),\n"
     "    ('gc_collect', '                gc_lines.append(tuple(int(x) for x in g.groups()))', '                pass'),\n"),
    ("    path = WORK / ('mut_vbn113d_%s.py' % name)\n", "    path = WORK / ('mut_vbn113e_%s.py' % name)\n"),
])

"""Session 113, ROADMAP 0.1 "СЕССИЯ 113" item 19: re-pin of the ABBA scorer draft shn113 (made for the build 94362eae
by make_shn113.py) to the build 1678d3f4 and a forced OLD regime, by WHOLE-LINE anchored replacements (asserted).
Outputs C:/kyty/s106_stage/shn113b/{shn113.py,test_shn113.py,mut_shn113.py} (the scorer keeps its name: seal 02 and
its chain refer to shn113.py).  Changes: BINARY_SHA; SIZE_LABEL; ENV_EXPECTED + KYTY_BUFFER_GC_TRIGGER_SHIFT_MB=1024
(fixture CONSTANTS now compares ENV_EXPECTED); the FrameTrace-x schema + bda_nrace, prio_unsub, prio_stall,
gw_idle_prio (each with its SCHEMA fixture and mutant); the video check `shifted` (fixtures V_shift, V_shift_wrong;
mutant VIDEO_shift_off); mutants ENV_shift_drop / ENV_shift_value.  Byte-reproducible.

    python C:/kyty/s106_stage/make_shn113b.py
"""
import hashlib
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')
OUT = STAGE / 'shn113b'
PINS = {'shn113.py': '026fae4f', 'test_shn113.py': '0dc13f98', 'mut_shn113.py': '01599013'}
NEW_SHA = '1678d3f40ace01cd652d375dbfd8229b58341846b465cc4fd91817634cbe3373'
OLD_SHA = '94362eae5e28fa68c6a9d5ed921510a1fb1caa2868b0aa220099ba333df4da92'
OLD_LABEL = 'bdanarrow=1 against bdanarrow=0 of build 94362eae, OLD regime, main estimator'
NEW_LABEL = 'bdanarrow=1 against bdanarrow=0 of build 1678d3f4, forced OLD (GC trigger -1024 MiB), main estimator'
SHIFT = "'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '1024'"


def load(name):
    s = (STAGE / name).read_bytes().decode('utf-8').replace('\r\n', '\n')
    assert hashlib.sha256(s.encode('utf-8')).hexdigest().startswith(PINS[name]), name
    return s


def derive(src, pairs):
    s = load(src)
    for a, b in pairs:
        assert a.endswith('\n') and b.endswith('\n'), (src, 'not whole lines', a[:80])
        assert s.startswith(a) or ('\n' + a) in s, (src, 'anchor not at a line start', a[:80])
        assert s.count(a) == 1, (src, a[:80], s.count(a))
        s = s.replace(a, b)
    OUT.mkdir(exist_ok=True)
    (OUT / src).write_bytes(s.encode('utf-8'))
    print('shn113b/' + src, hashlib.sha256(s.encode('utf-8')).hexdigest())


derive('shn113.py', [
    ('imported; make_shn113.py) for the build 94362eae, whose FrameTrace-x rows add bda_ginv_reg, bda_ginv_map, bda_rinv,\n',
     'imported; make_shn113.py; re-pinned by make_shn113b.py to the build 1678d3f4 and a forced OLD regime,\n'
     'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB=1024 in both arms and the video), whose FrameTrace-x rows add bda_ginv_reg,\n'
     'bda_ginv_map, bda_rinv, (then bda_nrace, prio_unsub, prio_stall, gw_idle_prio after bgc_evict: information)\n'),
    ("BINARY_SHA = '%s'\n" % OLD_SHA, "BINARY_SHA = '%s'\n" % NEW_SHA),
    ("SIZE_LABEL = '%s'\n" % OLD_LABEL, "SIZE_LABEL = '%s'\n" % NEW_LABEL),
    ("    'bda_nxthr': 'x', 'bgc_evict': 'x',\n",
     "    'bda_nxthr': 'x', 'bgc_evict': 'x', 'bda_nrace': 'x', 'prio_unsub': 'x', 'prio_stall': 'x', 'gw_idle_prio': 'x',\n"),
    ("                'KYTY_GPU_MARKERS': '0'}\n", "                'KYTY_GPU_MARKERS': '0', %s}\n" % SHIFT),
    ("        'pinned': env.get('KYTY_GPU_CLOCK_PIN') == '1',\n",
     "        'pinned': env.get('KYTY_GPU_CLOCK_PIN') == '1',\n"
     "        'shifted': env.get('KYTY_BUFFER_GC_TRIGGER_SHIFT_MB') == '1024',\n"),
])

derive('test_shn113.py', [
    ("                  'bda_nxthr': 0, 'bgc_evict': 1},\n",
     "                  'bda_nxthr': 0, 'bgc_evict': 1, 'bda_nrace': 0, 'prio_unsub': 5, 'prio_stall': 0,\n"
     "                  'gw_idle_prio': 0},\n"),
    ("          attempts=None, gates=None):\n", "          attempts=None, gates=None, shift='1024'):\n"),
    ("    if pin:\n        env['KYTY_GPU_CLOCK_PIN'] = pin\n",
     "    if pin:\n        env['KYTY_GPU_CLOCK_PIN'] = pin\n    if shift:\n        env['KYTY_BUFFER_GC_TRIGGER_SHIFT_MB'] = shift\n"),
    ("case('V_pin', run_eval(good, *video(good, pin=None, tag='pn')), KEEP_VID, vfail=['pinned'])\n",
     "case('V_pin', run_eval(good, *video(good, pin=None, tag='pn')), KEEP_VID, vfail=['pinned'])\n"
     "case('V_shift', run_eval(good, *video(good, shift=None, tag='sh')), KEEP_VID, vfail=['shifted'])\n"
     "case('V_shift_wrong', run_eval(good, *video(good, shift='512', tag='s5')), KEEP_VID, vfail=['shifted'])\n"),
    ("                                      'SECONDARY_LO', 'SECONDARY_HI')}\n",
     "                                      'SECONDARY_LO', 'SECONDARY_HI', 'ENV_EXPECTED')}\n"),
    ("            'BINARY_SHA': '%s',\n" % OLD_SHA, "            'BINARY_SHA': '%s',\n" % NEW_SHA),
    ("            'SECONDARY_HI': 89}\n", "            'SECONDARY_HI': 89, 'ENV_EXPECTED': ENV_WANT}\n"),
    ("SIZE_LABEL = '%s'\n" % OLD_LABEL,
     "SIZE_LABEL = '%s'\n" % NEW_LABEL +
     "# the sealed launch environment, written out here (not read from mod.ENV_EXPECTED: a dropped or changed key must fail)\n"
     "ENV_WANT = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_QUEUE_TRACE': '1',\n"
     "            'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden', 'KYTY_GATE_SCHEDULE_ABBA': '1',\n"
     "            'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0', %s}\n" % SHIFT),
    ("                'bda_nskip', 'bda_nwould', 'bda_nmiss', 'bda_nxthr', 'bgc_evict')\n",
     "                'bda_nskip', 'bda_nwould', 'bda_nmiss', 'bda_nxthr', 'bgc_evict', 'bda_nrace', 'prio_unsub',\n"
     "                'prio_stall', 'gw_idle_prio')\n"),
])

derive('mut_shn113.py', [
    ("mutant('VIDEO_pin_off', \"'pinned': env.get('KYTY_GPU_CLOCK_PIN') == '1',\", \"'pinned': True,\")\n",
     "mutant('VIDEO_pin_off', \"'pinned': env.get('KYTY_GPU_CLOCK_PIN') == '1',\", \"'pinned': True,\")\n"
     "mutant('VIDEO_shift_off', \"'shifted': env.get('KYTY_BUFFER_GC_TRIGGER_SHIFT_MB') == '1024',\", \"'shifted': True,\")\n"
     "mutant('ENV_shift_drop', \", %s}\", \"}\")\n" % SHIFT +
     "mutant('ENV_shift_value', \"%s}\", \"'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '512'}\")\n" % SHIFT),
    ("            'bda_nskip', 'bda_nwould', 'bda_nmiss', 'bda_nxthr', 'bgc_evict'):\n",
     "            'bda_nskip', 'bda_nwould', 'bda_nmiss', 'bda_nxthr', 'bgc_evict', 'bda_nrace', 'prio_unsub', 'prio_stall',\n"
     "            'gw_idle_prio'):\n"),
    ("mutant('CONST_binary_b47b58a9', \"BINARY_SHA = '%s'\",\n" % OLD_SHA,
     "mutant('CONST_binary_b47b58a9', \"BINARY_SHA = '%s'\",\n" % NEW_SHA),
    ("mutant('SIZE_label', \"SIZE_LABEL = '%s'\",\n" % OLD_LABEL,
     "mutant('SIZE_label', \"SIZE_LABEL = '%s'\",\n" % NEW_LABEL),
])

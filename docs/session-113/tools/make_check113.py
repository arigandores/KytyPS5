"""Session 113, ROADMAP 0.1 "СЕССИЯ 113" item 21: check113.py / test_check113.py / mut_check113.py from session 112's
check112 files (sha pinned) by WHOLE-LINE anchored replacements (asserted).  Outputs to C:/kyty/s113.  New: the build
1678d3f4; `bdanarrow` absent from the gate text and no KYTY_BUFFER_GC_TRIGGER_SHIFT_MB in env (the defaults run);
narrow_default_dark (sum bda_nskip == 0 and sum bda_nwould == 0); gc_default (one BufferGc: line, shift_mb=0);
prio_stall / prio_unsub reported, not checked.  Byte-reproducible.

    python C:/kyty/s106_stage/make_check113.py
"""
import hashlib
from pathlib import Path

SRC_DIR = Path('C:/kyty/s112')
OUT = Path('C:/kyty/s113')
PINS = {'check112.py': '829cb59f', 'test_check112.py': 'fcfe6b80', 'mut_check112.py': '4bf31d90'}
OLD_SHA = 'b47b58a997b441478ab1d278c992949d79795014370d034b747d5fd4e7b9f7f7'
NEW_SHA = '1678d3f40ace01cd652d375dbfd8229b58341846b465cc4fd91817634cbe3373'
GC_OK = 'BufferGc: budget=14901313536 trigger=9747352781 critical=13183326618 shift_mb=0'


def load(name):
    s = (SRC_DIR / name).read_bytes().decode('utf-8').replace('\r\n', '\n')
    assert hashlib.sha256(s.encode('utf-8')).hexdigest().startswith(PINS[name]), name
    return s


def derive(src, dst, pairs):
    s = load(src)
    for a, b in pairs:
        assert a.endswith('\n') and b.endswith('\n'), (src, 'not whole lines', a[:80])
        assert s.startswith(a) or ('\n' + a) in s, (src, 'anchor not at a line start', a[:80])
        assert s.count(a) == 1, (src, a[:80], s.count(a))
        s = s.replace(a, b)
    (OUT / dst).write_bytes(s.encode('utf-8'))
    print(dst, hashlib.sha256(s.encode('utf-8')).hexdigest())


derive('check112.py', 'check113.py', [
    ('"""Session 112, ROADMAP §0.1 "СЕССИЯ 112" item 4: the video pass of the build b47b58a9 (knob `daguard`, default 1; the\n'
     "walker's GuardSlot yield; the ahead_threads size fix) with today's defaults (`daslot=1 daguard=1 cspfree=1`).\n",
     '"""Session 113, ROADMAP §0.1 "СЕССИЯ 113" item 21: the video pass of the build 1678d3f4 (knob `bdanarrow`, default 0;\n'
     'the env KYTY_BUFFER_GC_TRIGGER_SHIFT_MB, default 0; the exact knob-2 check; the priority-stall instrument) with\n'
     "today's defaults (`daslot=1 daguard=1 cspfree=1 bdanarrow=0`).  Derived from check112.py by make_check113.py.\n"),
    ("  default_runs             none of ` daslot=`, ` daguard=`, ` cspfree=` in the gate text (the defaults run)\n",
     "  default_runs             none of ` daslot=`, ` daguard=`, ` cspfree=`, ` bdanarrow=` in the gate text (defaults)\n"
     "  no_shift                 no KYTY_BUFFER_GC_TRIGGER_SHIFT_MB in env (the buffer-GC trigger as shipped)\n"),
    ("  no_marker                no failure marker in the log or stdout\n",
     "  no_marker                no failure marker in the log or stdout\n"
     "  narrow_default_dark      sum bda_nskip == 0 and sum bda_nwould == 0 (bdanarrow=0: no skip, no check)\n"
     "  gc_default               exactly one `BufferGc:` line, ending in shift_mb=0\n"),
    ("Reported, not checked: cs_sync_wait, da_guard_yield, da_guard_busy.\n",
     "Reported, not checked: cs_sync_wait, da_guard_yield, prio_stall, prio_unsub.\n"),
    ("    python C:/kyty/s112/check112.py [--root C:/kyty/s112] [--out <json>]\n",
     "    python C:/kyty/s113/check113.py [--root C:/kyty/s113] [--out <json>]\n"),
    ("ROOT = 'C:/kyty/s112'\n", "ROOT = 'C:/kyty/s113'\n"),
    ("TAG = 'vid112'\n", "TAG = 'vid113'\n"),
    ("BUILD_SHA = '%s'\n" % OLD_SHA, "BUILD_SHA = '%s'\n" % NEW_SHA),
    ("FIELDS = ('cspfree_hit', 'cspfree_bad', 'cs_sync_new', 'cs_sync_wait', 'da_q_free', 'da_q_noguard', 'da_slot_bad',\n"
     "          'da_guard_yield')\n",
     "FIELDS = ('cspfree_hit', 'cspfree_bad', 'cs_sync_new', 'cs_sync_wait', 'da_q_free', 'da_q_noguard', 'da_slot_bad',\n"
     "          'da_guard_yield', 'bda_nskip', 'bda_nwould', 'prio_stall', 'prio_unsub')\n"),
    ("    rows = missing = pins = pin1 = 0\n", "    rows = missing = pins = pin1 = 0\n    gc_lines = []\n"),
    ("            if line.startswith(b'GpuClockPin:'):\n                pins += 1\n",
     "            if line.startswith(b'BufferGc: '):\n"
     "                gc_lines.append(line[:200].decode('utf-8', 'replace').strip())\n"
     "            if line.startswith(b'GpuClockPin:'):\n                pins += 1\n"),
    ("                  default_runs=' daslot=' not in gates and ' daguard=' not in gates and ' cspfree=' not in gates,\n",
     "                  default_runs=(' daslot=' not in gates and ' daguard=' not in gates and ' cspfree=' not in gates\n"
     "                                and ' bdanarrow=' not in gates),\n"
     "                  no_shift='KYTY_BUFFER_GC_TRIGGER_SHIFT_MB' not in env,\n"),
    ("                  no_marker=not markers)\n",
     "                  no_marker=not markers,\n"
     "                  narrow_default_dark=tot['bda_nskip'] == 0 and tot['bda_nwould'] == 0,\n"
     "                  gc_default=len(gc_lines) == 1 and gc_lines[0].endswith(' shift_mb=0'))\n"),
    ("               markers=markers[:10], stable_frame=stable)\n",
     "               markers=markers[:10], stable_frame=stable, gc_lines=gc_lines)\n"),
])

derive('test_check112.py', 'test_check113.py', [
    ('"""Session 112: fixtures for check112.py - PASS, every check failing alone, and both sides of every threshold.\n'
     '    python test_check112.py <check112.py>\n',
     '"""Session 113: fixtures for check113.py (from test_check112.py by make_check113.py) - PASS, every check failing\n'
     'alone, and both sides of every threshold.\n'
     '    python test_check113.py <check113.py>\n'),
    ("BASE = Path('C:/kyty/s106_stage/fx_check112')\n", "BASE = Path('C:/kyty/s106_stage/fx_check113')\n"),
    ("spec = importlib.util.spec_from_file_location('check112', SRC)\n",
     "spec = importlib.util.spec_from_file_location('check113', SRC)\n"),
    ("GATES = 'dawalk=1 smemocheck=0 dabatch=8 fslean=0'\n",
     "GATES = 'dawalk=1 smemocheck=0 dabatch=8 fslean=0'\nGC_OK = '%s'\n" % GC_OK),
    ("         slot_bad=0, hit=266, free_bad=0, sync_new=0, drop_field=False, glitch_text=None):\n",
     "         slot_bad=0, hit=266, free_bad=0, sync_new=0, drop_field=False, glitch_text=None, nskip=0, would=0,\n"
     "         gc=(GC_OK,)):\n"),
    ("    out = list(pins) + list(lines)\n", "    out = list(pins) + list(gc) + list(lines)\n"),
    ("                                                   slot_bad if n == stable + 11 else 0)\n",
     "                                                   slot_bad if n == stable + 11 else 0)\n"
     "        f += ' bda_nskip=%d bda_nwould=%d prio_stall=0 prio_unsub=5' % (nskip if n == stable + 13 else 0,\n"
     "                                                                       would if n == stable + 15 else 0)\n"),
    ("    ('gate_cspfree', dict(gates=GATES + ' cspfree=1'), ['default_runs']),\n",
     "    ('gate_cspfree', dict(gates=GATES + ' cspfree=1'), ['default_runs']),\n"
     "    ('gate_bdanarrow', dict(gates=GATES + ' bdanarrow=0'), ['default_runs']),\n"
     "    ('shift', dict(env={'KYTY_BUFFER_GC_TRIGGER_SHIFT_MB': '0'}), ['no_shift']),\n"
     "    ('narrow_skip', dict(nskip=1), ['narrow_default_dark']),\n"
     "    ('narrow_would', dict(would=1), ['narrow_default_dark']),\n"
     "    ('gc_none', dict(gc=()), ['gc_default']),\n"
     "    ('gc_two', dict(gc=(GC_OK, GC_OK)), ['gc_default']),\n"
     "    ('gc_shift', dict(gc=(GC_OK.replace('shift_mb=0', 'shift_mb=1024'),)), ['gc_default']),\n"
     "    ('gc_shift_10', dict(gc=(GC_OK.replace('shift_mb=0', 'shift_mb=10'),)), ['gc_default']),\n"),
    ("CONSTANTS = dict(TAG='vid112', MIN_FRAMES=3000, MIN_ROWS=1000,\n",
     "CONSTANTS = dict(TAG='vid113', MIN_FRAMES=3000, MIN_ROWS=1000,\n"),
    ("                 BUILD_SHA='%s')\n" % OLD_SHA, "                 BUILD_SHA='%s')\n" % NEW_SHA),
])

derive('mut_check112.py', 'mut_check113.py', [
    ('"""Session 112: mutants of check112.py - each must be killed by test_check112.py."""\n',
     '"""Session 113: mutants of check113.py (from mut_check112.py by make_check113.py) - each must be killed by\n'
     'test_check113.py; run through mutlib v2 --control --no-memo on the sealed copy."""\n'),
    ("SRC = (STAGE / 'check112.py').read_text(encoding='utf-8')\n",
     "SRC = Path('C:/kyty/s113/check113.py').read_text(encoding='utf-8')\n"),
    ("    ('installed', 'installed_now=installed_sha == BUILD_SHA,', 'installed_now=True,'),\n",
     "    ('installed', 'installed_now=installed_sha == BUILD_SHA,', 'installed_now=True,'),\n"
     "    ('def_bdanarrow', \"and ' bdanarrow=' not in gates)\", 'and True)'),\n"
     "    ('shift', \"no_shift='KYTY_BUFFER_GC_TRIGGER_SHIFT_MB' not in env,\", 'no_shift=True,'),\n"
     "    ('nskip', \"tot['bda_nskip'] == 0 and \", ''),\n"
     "    ('would', \" and tot['bda_nwould'] == 0,\", ','),\n"
     "    ('gc_count', 'len(gc_lines) == 1 and ', ''),\n"
     "    ('gc_shift', \" and gc_lines[0].endswith(' shift_mb=0'))\", ')'),\n"
     "    ('gc_collect', \"gc_lines.append(line[:200].decode('utf-8', 'replace').strip())\", 'pass'),\n"),
    ("    ('def_cspfree', \" and ' cspfree=' not in gates,\", ','),\n",
     "    ('def_cspfree', \"' daguard=' not in gates and ' cspfree=' not in gates\", \"' daguard=' not in gates\"),\n"),
    ("    path = STAGE / ('mut_check112_%s.py' % name)\n", "    path = STAGE / ('mut_check113_%s.py' % name)\n"),
    ("    r = subprocess.run([sys.executable, str(STAGE / 'test_check112.py'), str(path)], capture_output=True, text=True)\n",
     "    r = subprocess.run([sys.executable, 'C:/kyty/s113/test_check113.py', str(path)], capture_output=True, text=True)\n"),
])

"""Session 111: check111.py from s110/check110.py (ROADMAP section 0.1 "СЕССИЯ 111" item 5): the video pass of the
build with daslot=1 as the DEFAULT.  Byte-reproducible; anchored replacements."""
import hashlib
from pathlib import Path

s = Path('C:/kyty/s110/check110.py').read_bytes().decode('utf-8').replace('\r\n', '\n')
pairs = [
    ('"""Session 110, ROADMAP §0.1 "СЕССИЯ 110" item 6: the video pass of the build with cspfree=1 as the DEFAULT.\nDerived from check108r.py (session 108) with the default-armed check on cspfree and markers read from stdout too.',
     '"""Session 111, ROADMAP §0.1 "СЕССИЯ 111" item 5: the video pass of the build with daslot=1 as the DEFAULT.\nDerived from s110/check110.py by make_check111.py: plus the default-armed check on daslot (da_q_free > 0 with\n`daslot` absent from the gate text) and da_slot_bad == 0.'),
    ('    python C:/kyty/s108/check108.py [--out <json>]', '    python C:/kyty/s111/check111.py [--out <json>]'),
    ("sys.path.insert(0, 'C:/kyty/s110')", "sys.path.insert(0, 'C:/kyty/s111')"),
    ("ROOT = 'C:/kyty/s110'", "ROOT = 'C:/kyty/s111'"),
    ("TAG = 'vid110'", "TAG = 'vid111'"),
    ("BUILD_SHA = '072861c89193c3726232e44e78be4f36172254af826394b56c8bf671ef609c21'",
     "BUILD_SHA = '0c8a13f28245ea879c25725ebf4258a944308d24f7c6c11fd4bee95ec3814c8c'"),
    ("    hit = bad = sync_new = sync_wait = rows = missing = 0",
     "    hit = bad = sync_new = sync_wait = rows = missing = qfree = slotbad = 0"),
    ("                missing += int(any(k not in d for k in ('cspfree_hit', 'cspfree_bad', 'cs_sync_new', 'cs_sync_wait')))",
     "                missing += int(any(k not in d for k in ('cspfree_hit', 'cspfree_bad', 'cs_sync_new', 'cs_sync_wait',\n                                                        'da_q_free', 'da_slot_bad')))\n                qfree += d.get('da_q_free', 0)\n                slotbad += d.get('da_slot_bad', 0)"),
    ("                  default_runs=' cspfree=' not in gates,",
     "                  default_runs=' cspfree=' not in gates and ' daslot=' not in gates,"),
    ("                  no_bad=bad == 0,",
     "                  no_bad=bad == 0,\n                  slot_default_armed=qfree > 0 and rows > 0,\n                  slot_no_bad=slotbad == 0,"),
    ("               cs_sync_wait=sync_wait, markers=markers[:10], stable_frame=stable)",
     "               cs_sync_wait=sync_wait, da_q_free_per_row=qfree / rows if rows else None, da_slot_bad=slotbad,\n               markers=markers[:10], stable_frame=stable)"),
]
for a, b in pairs:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
Path('C:/kyty/s111/check111.py').write_bytes(s.encode('utf-8'))
print('check111.py', hashlib.sha256(s.encode('utf-8')).hexdigest())

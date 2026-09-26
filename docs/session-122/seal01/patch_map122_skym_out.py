"""Session 122 step 3b (HPP-15), ROADMAP s122 item 13 (b): the smoke csky122 armed code 7 (dose 2 000.3-2 000.5 us a
frame, burn_s_seen 285 a block, burn_cpu_bad 0) but burn_s_main = 0 in EVERY block - the burnt thread is not the main
guest thread, so item 13 (a) fails and the skym122 arm LEAVES the map.  Edits map122.py, test_map122.py,
mut_map122.py, go122a.sh, chk_map122.py in place (LF, write_bytes); every anchor exactly once, else nothing is written."""
from pathlib import Path

R = Path('C:/kyty/s122')
REASON = ('csky122 (unsealed smoke, 2026-09-26): code 7 armed (dose 2 000.3-2 000.5 us a frame) but burn_s_main = 0 '
          'in every block')


def apply(path, edits):
    src = path.read_bytes().decode('utf-8')
    assert chr(13) not in src, path
    for old, new in edits:
        c = src.count(old)
        assert c == 1, (path.name, c, old[:80])
        src = src.replace(old, new)
    return src


out = {}
out['map122.py'] = apply(R / 'map122.py', [
    ("                          not recorded that arm => refused, never scored).  skym122, the main-guest-thread arm, rides on\n"
     "                          CODE 7 (GuestGpu::Submit before its lock; ROADMAP s122 item 13 - the code-4 site is dead)\n",
     "                          not recorded that arm => refused, never scored).  skym122, the main-guest-thread arm on\n"
     "                          CODE 7, LEFT the map by ROADMAP s122 item 13 (b): the smoke csky122 armed code 7 but read\n"
     "                          burn_s_main = 0 in every block (the burnt thread is not the main guest thread)\n"),
    ("# recorded that arm; such a tag is refused (ROADMAP item 3: an unrecorded decision is void).  skym122 carries the\n"
     "# main-guest-thread arm on CODE 7 (GuestGpu::Submit before its lock): the smoke bsky122 measured the code-4 site DEAD\n"
     "# (burn_t_seen = 0, burn_s_main = 0) and ROADMAP s122 item 13 moved the arm to code 7.  Order of step 4 (item 17 (d)):\n"
     "# sky122, skym122, skyp122, then des122 (intro_next) as the first additional scene.\n",
     "# recorded that arm; such a tag is refused (ROADMAP item 3: an unrecorded decision is void).  The main-guest-thread\n"
     "# arm is NOT in the map: the smoke bsky122 measured the code-4 site DEAD (burn_t_seen = 0, burn_s_main = 0), item 13\n"
     "# moved the arm to code 7, and the smoke csky122 armed code 7 with burn_s_main = 0 in every block - item 13 (a) fails,\n"
     "# so by item 13 (b) the skym122 arm left the map (no PLAN entry: the tag is refused).  Order of step 4 (item 17 (d)):\n"
     "# sky122, skyp122, then des122 (intro_next) as the first additional scene.\n"),
    ("    'skym122': dict(level='underwater_aerial_garden', burn=702000),\n", ""),
])
out['test_map122.py'] = apply(R / 'test_map122.py', [
    ("    'skym122': dict(level='underwater_aerial_garden', burn=702000),\n    'atl122':",
     "    'atl122':"),
    ("# the scorer's PLAN_DEFAULT as the seal records it (ROADMAP s122 items 2, 13, 17 (d)): written here, never read back\n",
     "# the scorer's PLAN_DEFAULT as the seal records it (ROADMAP s122 items 2, 13 (b), 17 (d)): written here, never read\n"
     "# back; skym122 is absent - the code-7 arm left the map (" + REASON + ")\n"),
    ("       for t in ('sky122', 'skym122', 'zzz122')]\n"
     "check('plan_check_exit_codes', tuple(p.returncode for p in _pc), (0, 0, 2))\n"
     "check('plan_check_sealed_line', ('arm burn=102000 (code 1, dose 2000 us) sealed' in _pc[0].stdout,\n"
     "                                 'arm burn=702000 (code 7, dose 2000 us) sealed' in _pc[1].stdout,\n"
     "                                 'no PLAN entry' in _pc[2].stdout), (True, True, True))\n",
     "       for t in ('sky122', 'skyp122', 'skym122', 'zzz122')]\n"
     "check('plan_check_exit_codes', tuple(p.returncode for p in _pc), (0, 0, 2, 2))\n"
     "check('plan_check_sealed_line', ('arm burn=102000 (code 1, dose 2000 us) sealed' in _pc[0].stdout,\n"
     "                                 'arm burn=802000 (code 8, dose 2000 us) sealed' in _pc[1].stdout,\n"
     "                                 'no PLAN entry for tag skym122' in _pc[2].stdout,\n"
     "                                 'no PLAN entry' in _pc[3].stdout), (True, True, True, True))\n"
     "check('plan_default_has_no_skym', 'skym122' in mod.PLAN_DEFAULT, False)\n"),
])
out['mut_map122.py'] = apply(R / 'mut_map122.py', [
    ("    ('plan_skym_code4', \"    'skym122': dict(level='underwater_aerial_garden', burn=702000),\",\n"
     "     \"    'skym122': dict(level='underwater_aerial_garden', burn=402000),\"),\n"
     "    ('plan_skym_none', \"    'skym122': dict(level='underwater_aerial_garden', burn=702000),\",\n"
     "     \"    'skym122': dict(level='underwater_aerial_garden', burn=None),\"),\n",
     "    ('plan_skym_back', \"    'skyp122': dict(level='underwater_aerial_garden', burn=802000),\\n\",\n"
     "     \"    'skyp122': dict(level='underwater_aerial_garden', burn=802000),\\n\"\n"
     "     \"    'skym122': dict(level='underwater_aerial_garden', burn=702000),\\n\"),\n"),
    ("REPLACED at step 3b (ROADMAP s122 item 18 (c), the HEADROOM reading by the run's own base arm, not by the level name):\n",
     "REPLACED at step 3b (ROADMAP s122 item 13 (b), the skym122 arm left the map after the smoke csky122): plan_skym_code4\n"
     "  and plan_skym_none - their PLAN line is gone; plan_skym_back (the arm put back) takes their place.\n"
     "REPLACED at step 3b (ROADMAP s122 item 18 (c), the HEADROOM reading by the run's own base arm, not by the level name):\n"),
])
out['go122a.sh'] = apply(R / 'go122a.sh', [
    ("#     skym122 Sky Garden   burn=0|burn=702000   (main guest thread on code 7, GuestGpu::Submit; ROADMAP s.122 item 13)\n",
     "#     skym122 REFUSED: the main-guest-thread arm left the map (ROADMAP s.122 item 13 (b); csky122: code 7 armed,\n"
     "#             burn_s_main = 0 in every block)\n"),
    ("#   order of step 4 (ROADMAP s.122 item 17 (d)): sky122, skym122, skyp122, then des122 (intro_next) first additional.\n",
     "#   order of step 4 (ROADMAP s.122 item 17 (d), 13 (b)): sky122, skyp122, then des122 (intro_next) first additional.\n"),
    ("  skym122) SEALED=1; HOLD=300; ATT=1; SCHED=\"KYTY_GATE_SCHEDULE=90+1800:burn=0|burn=702000\"; EXTRA=\"KYTY_GATE_SCHEDULE_ABBA=1\"; RECARG=\"\"; SD=\"--stable-draws 300 --timeout 480\";;\n",
     "  skym122) echo \"skym122 left the map (ROADMAP s.122 item 13 (b): csky122 read burn_s_main = 0) - refused\"; exit 2;;\n"),
])
out['chk_map122.py'] = apply(R / 'chk_map122.py', [
    ("     ROADMAP s122: an unrecorded decision is void; skym122 rides on code 7 by item 13);\n",
     "     ROADMAP s122: an unrecorded decision is void; skym122 has no entry - it left the map by item 13 (b));\n"),
])
for name, text in out.items():
    (R / name).write_bytes(text.encode('utf-8'))
    print('wrote', name, len(text))

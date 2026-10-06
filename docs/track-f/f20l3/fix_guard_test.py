import os
S = os.environ['PAPERCLIP_RUN_SCRATCH_DIR']
G = 'C:/kyty/f287/f20l3'
p = G + '/test_guard_f20l3.py'
s = open(p, 'rb').read().decode('ascii')
E = [
    ("    p = subprocess.run([BASH, os.path.join(HERE, 'launch_f20l3.sh'), 'b32_pcb'], capture_output=True, text=True, env=LENV)",
     "    p = subprocess.run([BASH, os.path.join(HERE, 'launch_f20l3.sh'), 'b32_s01'], capture_output=True, text=True, env=LENV)"),
    ("""p = subprocess.run([BASH, os.path.join(HERE, 'go_f20l3.sh'), 'b32_pcb'], capture_output=True, text=True, env=dict(os.environ, F20L3_DRYRUN='1'))
check('go: dry run 1 names the form (pcb: loader none, gpusleep stand)', p.returncode == 0 and 'loader none' in p.stdout and 'KYTY_TEST_B32=60:gpusleep:200' in p.stdout)""",
     """p = subprocess.run([BASH, os.path.join(HERE, 'go_f20l3.sh'), 'b32_pa'], capture_output=True, text=True, env=dict(os.environ, F20L3_DRYRUN='1'))
check('go: dry run 1 names the form (pa: KYTY_DIAG_B32=1, cold 1)', p.returncode == 0 and 'knobs KYTY_DIAG_B32=1 cold 1' in p.stdout)"""),
    ("check('go: FS8 returned after the wait for the user process, before the run manifest', i_gone < i_bret < i_mrun)",
     "check('go: S18 returned after the wait for the user process, before the run manifest', i_gone < i_bret < i_mrun)"),
    ("""check('go: M6 and the loader start before enter_scene, stop files touched after it and at the exit', go.index('m6_f20l3.py') < i_es and go.index('b32_load.py') < i_es and go.count('touch $OUT/watch.stop $OUT/m6.stop $OUT/load.stop') == 1 and 'touch $OUT/m6.stop $OUT/load.stop' in go[:i_mf])""",
     """check('go: M6 starts before enter_scene, stop files touched after it and at the exit (no loader)', go.index('m6_f20l3.py') < i_es and
      'b32_load.py' not in go and go.count('touch $OUT/watch.stop $OUT/m6.stop; wait $WPID; wait $MPID') == 1 and
      'touch $OUT/m6.stop 2>/dev/null' in go[:i_mf])"""),
    ("for nm in ('guard_f20l3.py', 'test_guard_f20l3.py', 'go_f20l3.sh', 'launch_f20l3.sh', 'enter_scene.py'):",
     "for nm in ('guard_f20l3.py', 'test_guard_f20l3.py', 'go_f20l3.sh', 'launch_f20l3.sh', 'enter_scene.py', 'reserve_f20l3.py'):"),
]
for a, b in E:
    assert s.count(a) == 1, (s.count(a), a[:60])
    s = s.replace(a, b)
open(S + '/test_guard_f20l3.py', 'wb').write(s.encode('ascii'))
print('ok')

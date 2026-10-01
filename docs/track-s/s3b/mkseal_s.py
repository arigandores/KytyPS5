#!/usr/bin/env python3
"""mkseal_s.py (S3b) - writes the seal C:/kyty/s288/pred/02_s.md of track S link S3b (HPP-325; ROADMAP "SESSION 122"
item 250, on items 241, 245, 247).  Port of s3/mkseal_s.py: the plan of every arm is the output of DRY=2 bash go_s.sh <tag>
verbatim; every sha line is computed here.  Seal 01 is not changed and no longer holds for S4 (item 250 (i)).  ASCII only.
Refuses when the seal exists (a seal is never rewritten)."""
import hashlib
import os
import subprocess
import sys

sys.path.insert(0, 'C:/kyty/s288')
import sc_s as S  # noqa: E402

ROOT = 'C:/kyty/s288'
OUT = 'C:/kyty/s288/pred/02_s.md'
if os.path.exists(OUT):
    print('seal exists, refuse')
    sys.exit(3)
assert S.PRED_PATH == OUT, S.PRED_PATH
BASH = 'C:/Program Files/Git/bin/bash.exe'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def path(n):
    return n if n.startswith('C:/') else '%s/%s' % (ROOT, n)


def plan(tag):
    env = dict(os.environ, DRY='2', PATH='/usr/bin:/mingw64/bin:' + os.environ.get('PATH', ''))
    p = subprocess.run([BASH, ROOT + '/go_s.sh', tag], capture_output=True, text=True, env=env, timeout=120)
    lines = [x for x in (p.stdout + p.stderr).splitlines() if x.startswith('PLAN ')]
    assert p.returncode == 0 and len(lines) == 1, (tag, p.returncode, p.stdout, p.stderr)
    return lines[0]


s4 = [a['tag'] for a in S.ARMS if a['link'] == 's4']
s6 = [a['tag'] for a in S.ARMS if a['link'] == 's6']
L = []
w = L.append
w('# Seal 02_s - track S link S3b (HPP-325): harness go_s.sh, scorer sc_s.py, the arms of S4 (ROADMAP "SESSION 122"'
  ' items 241, 245, 247, 250)')
w('')
w('Written by C:/kyty/s288/s3b/mkseal_s.py before any run of S4 or S6.  It replaces seal 01 for S4 (item 250 (i), (k)):')
w('seal 01 (pred/01_s.md, sha256 90e3de0b...) is not changed and no S4 arm is callable by it.  After this seal the scorer,')
w('the fixtures, the mutants, the harness and the cache tool do not change (a change = a new seal).  The S6 arms are NOT')
w('callable with this seal: they need a later seal (pred/03_s.md - the executor variant of its name; written after S5d,')
w('item 250 (k), by the scorer of S3b) that carries the line "pcw binary: <sha256> <path>", the seal lines and the six S6')
w('call lines.  A first text of this file (sha256 ba1d1309...) was written before the form W of item 254 (e) was read and')
w('withdrawn before any use and any commit (kept as s3b/withdrawn_02_s.md; S3b times.txt).  ASCII only.')
w('')
w('## 1. Constants (item 241 numbered by its sub-items; changes of item 250 marked)')
w('')
for line in (
        '- (v)(1) unit of "frames with a skip" = held flips, sum skc_held_inc; T-6: = distinct frame= of skipped-draw lines;'
        ' reading 1 (letter): a held series counts WITH the first scene frame when it is held; reading 2 from the next row.',
        '- (v)(2) with item 250 (g): freeze = dt of a presented row; visible gap of a held series; GOVERNING gap_pipe = gap -'
        ' sum dt of the series rows (closing row included) with dt >= 100 000 us of class PRIO ONLY (item 250 (g)(2): PCW'
        ' counts "to the shaders"); the former letter (minus PCW and PRIO) is printed as the second reading "(v)(2) before item'
        ' 250"; thresholds K3 100 000 us and K2 1 000 000 us on each; "attributed >= X" (item 250 (g)(1)) = a presented row'
        ' dt >= X of attribution SHADER or of class PCW, or a series with governing gap_pipe >= X; printed "of them PCW n";'
        ' beside it (RC8) the not attributed presented rows >= X by class (WAIT / GPUTHR / PRIO, attribution "not") and the'
        ' series with gap >= X but gap_pipe < X, and the sc142 outcome of the arm on the same line.',
        '- (v)(3) classes of a row dt >= 100 ms: PCW ("Vulkan pipeline cache: saved" or "PipelinePrecache: saved" in group i'
        ' or i+1) -> SHADER -> PRIO (stall sum >= dt/2 and cpu_gpu_us < dt/2 under BOTH conventions: stall lines of group i and'
        ' of group i+1) -> GPUTHR (cpu_gpu_us >= dt/2) -> WAIT.  The "AvTrace: pcw ..." lines are neither PREP nor pipe events.',
        '- (v)(4) attribution only on a T arm with T-3 and T-4, else "undetermined"; PREP over the AvTrace lines assigned to'
        ' the row (a line of group g goes to the largest dt of rows g-1..g+2 = windows i-2..i+1, earliest on a tie); SHADER if'
        ' dt - PREP < 100 000 or a skipped-draw line or a "pipeline gfx ... async" line in groups i-2..i+1; partly if'
        ' PREP >= dt/2; TR and PL apart.',
        '- (v)(5) identities T-1 (below 200 000 lines), T-2 (min 64), T-5 (both readings), T-6 (main), sum skc_held = 0,'
        ' skc_bad printed, T-3 / T-4 on T arms (pcw_int included, RC5), the M null control, no torn row, no row without'
        ' FrameTrace-x, no gap of n, the first scene frame = sc142.derive; a broken identity is FAIL of the arm; +-2 rows rule'
        ' printed (secondary).',
        '- (v)(6) KYTY_* families (ASYNC_, PIPELINE_, SHADER_, S_, DUMP_, FIX_ - item 245 (a), RC7 - CACHE_MODE,'
        ' CS_PRETRANSLATE) = the seal, else FAIL; executor variant: every KYTY_* key = the seal (the path keys GATE_FILE,'
        ' SAMPLE_GATE, REC present), also FAIL.',
        '- (v)(7) with item 250 (d): cold gate (C, T2): after the entry line (by log line) >= 1 AvTrace shader line, recipes'
        ' +1, >= 1 skipped draw, and T-3 / T-4 hold; the gate word is "cold", "level not cold" or "undetermined (T-3/T-4)"'
        ' (printed apart); warm gate (S-warm): 0 stdout "Shaders:" lines and recipes end - start = 0.',
        '- (v)(8) creation cold: median us of in-game creations (gfx async / no suffix, cs async / sync) >= 20 000 cold,'
        ' <= 5 000 warm, < 10 "nothing to classify"; letter = every in-game creation, variant = after the entry line.',
        '- (v)(9) video checks the picture, not freezes; (v)(10) foreign-CPU row (fgcpu143.py) inside the lock;'
        ' (v)(11) sc142.py unchanged (pinned sha below) and its 217 fixtures.',
        '- (d) with item 250 (d)-(e): C1-C4 on L0 = shuriken_ninja_castle, reserves jack_in_the_box, cymbal_party_land (a'
        ' candidate fails when C1 did not enter, had < 10 creations, or is "level not cold" by the level - the lead addition;'
        ' a C1 "undetermined (T-3/T-4)" keeps L0); a C arm counts only with its cold gate, else "out of the count" and the'
        ' reading "undetermined" with the word; "return neutralises": median C1 >= 20 000, C3 >= 20 000, C3/C1 in [0.5; 2];'
        ' "GLCache keeps warmth": median C2 <= 0.25 x C1; "salt neutralises": prep_ms C4 >= 6 760, median C4 >= 20 000,'
        ' C4/C1 in [0.5; 2]; ms per recipe = prep_ms C4 / recipes C4; "report and stop" without "return neutralises" stops'
        ' the T2 base only (item 250 (e)) - S-warm and the G arms go.',
        '- (b)(2) preparation screen over 114 levels printed as a band [I]: (recipes C4 + 95 x {6, 28, 83}) x ms per recipe,'
        ' limit 180 s.',
        '- (e) S-warm: big_hand_pirate_island (base c142_02), voxel_world (c142_09), ice_iceberg (c142_05), M arms with the'
        ' full restore + one T arm on big_hand_pirate_island; components (i) held flips of the window (reading 1),'
        ' (ii) window rows dt >= 100 ms by class; "stays" if warm >= 0.5 x base; base < 5 events -> undetermined.',
        '- (zh) T2: small_pot_lava spin_drill_natural_cave light_gadget_graveyard enemy_taco hero_kratos, reserves in order'
        ' picup_light enemy_snake mini_rocket_chain hero_drake bonus_path_maker_mix (a reserve only while fewer than 5 arms'
        ' entered and cold); G: underwater_aerial_garden, big_hand_pirate_island, L0.',
        '- (z)(5) S-pcw (S6, a later seal): underwater_aerial_garden, hold 330 s (>= 300 s presented after the first scene'
        ' frame), KYTY_S_PCW_FORCE_MS=15000, ABBA 0 1 1 0 (pcw_1 pcw_2 pcw_3 pcw_4) + pcw_int (integrity, environment T -'
        ' RC5, no snapshot: the app caches and GLCache as pcw_3 left them, run right after pcw_3) + pcw_val (validation,'
        ' KYTY_S_PCW=1); on the hold after the window (rows after first frame + 599): (a) each arm 0 writes >= 15 and frames'
        ' >= 100 ms with a write in groups i-1..i+1 >= 0.5 x writes; (b) each arm 1 writes >= 15, 0 such frames, 0 save'
        ' failures; (c) pcw_int loaded bytes = last write of pcw_3, 0 "disabled"; (d) pcw_val entered, held >= 300 s, 0'
        ' [Vulkan][E] with validation active; (e) video >= 3 000 frames, 0 glitches, 0 death markers, the lead sheet.',
        '- (z)(1) RC5: on pcw_int the "AvTrace: pcw overlap wait gfx|cs|..." lines (wait_us = the creation time, an upper'
        ' bound, max only, never added) and "AvTrace: pcw recipes" lines (lock_us / hold_us, format S5c 2ce6326e) by number;'
        ' 0 such lines -> (z)(1) undetermined, the S-pcw word never above MACHINE_UNDETERMINED.',
        '- RC6 (item 245 (v)): "Vulkan pipeline cache: save failed (Incomplete" on an arm 1 -> ARM1_CODE_DEFECT (a defect of the'
        ' iteration code, the arm is repeated after the fix, not counted toward the kill rule (z)(7)); counted apart.',
        '- RC11 (item 250 (z)): pcw_val stopped by validation before the entry line (not entered, >= 1 [Vulkan][E]) ->'
        ' VALIDATION_STOP_PRE_LEVEL: member (d) undetermined, not FAIL, not counted toward (z)(7); the arm leaves the'
        ' admission / hold / video checks; a stop after the entry is FAIL of (d).',
        '- form W, item 254 (e) (KytyPS5 d3a8d951; until B35 ships): every validation arm (pcw_val) runs with'
        ' KYTY_PIPELINE_PRECACHE=0 (no start precache, no recipe writes; a family key of (v)(6)); its admission row is the'
        ' positive control - no "PipelinePrecache: N recipes ->" line in its log.',
        '- word order of S-pcw: NOT_EVALUABLE (admission, identity, hold) -> POSCTRL_FAIL (a) -> ARM1_CODE_DEFECT (RC6) ->'
        ' ARM1_FAIL (b, c, e, or d FAIL) -> MACHINE_UNDETERMINED (d undetermined or (z)(1) undetermined) ->'
        ' MACHINE_PASS_PENDING_SHEET.',
        '- (g) the arm protocol (go_s.sh header): snapshot manifest'
        ' d8ca8c8efb60b43b37c14a274a4738c83a9dc5866cc784e649e97314c5fd45c4, driver snapshot manifest'
        ' 1767ca0a975f26c1cb90eff80e6cccb959dc507f2a1178506a6ef1dbcac97028; salt only on C4.  Item 250: RC1 the installed'
        ' binary is copied to <link>/installed_bin_pre.exe before the arm binary (installed_before) and returned from that'
        ' copy with a sha check; admission row installed_after = installed_before (the constant 9235a7ac is gone from the'
        ' row); RC2 a failed return (any rc != 0) writes <link>/RETURN_FAILED before the unlock, a times.txt line and a'
        ' stdout line for the link comment; every go_s.sh call refuses rc 1 while a guard of s4 or s6 exists; return_prev_ok'
        ' and arm_start in the json; the continuity of the live manifests with the return of the previous arm of S is a data'
        ' row ("foreign chain between arms"), not FAIL; RC9 %LOCALAPPDATA% must be the known folder FOLDERID_LocalAppData'
        ' (cachex_s.py where glc before the lock, rc 1), the restore refuses a missing live root; RC10 man_launch_glc right'
        ' before the game, admission = restore_glc.got; "GLCache not protected during the arm" - in "not proven".'):
    w(line)
w('')
w('## 2. Call lines of S4 (one per tag; PLWAIT=540, item 105 (v)) and the plan of every arm (DRY=2, verbatim)')
w('')
for t in s4:
    w('go_s call: PLWAIT=540 bash C:/kyty/s288/go_s.sh %s' % t)
w('')
w('```')
for t in s4:
    w(plan(t))
w('```')
w('')
w('## 3. The plan of every S6 arm (DRY=2, verbatim) - NOT callable with this seal (no call lines, no pcw binary line)')
w('')
w('```')
for t in s6:
    w(plan(t))
w('```')
w('')
w('## 4. Seal lines (sc_s.py --check-seal checks each before every lock)')
w('')
for n in S.SEALED_NAMES:
    w('seal: %s %s' % (sha(path(n)), n))
w('')
w('## 5. Binary and the evidence of the link')
w('')
w('- S4 arm binary: C:/kyty/s128/kyty_emulator_9235a7ac.exe sha256 %s; the build installed before each arm is copied and'
  ' returned after it (item 250 (b)) - whatever it is.' % sha('C:/kyty/s128/kyty_emulator_9235a7ac.exe'))
for name, p in (('fixtures sc_s', 's3b/test_sc_s.out.txt'), ('fixtures cachex', 's3b/test_cachex_s.out.txt'),
                ('fixtures harness', 's3b/test_go_s.out.txt'),
                ('inherited fixtures sc142 (217)', 's3b/test_sc142_inherited.out.txt'),
                ('regression 12 sc142 logs', 's3b/regress_s.out.txt'), ('mutants (counted full run)', 's3b/mut_sc_s.txt'),
                ('snap0 index', 's3/snap0_index.json')):
    full = path(p)
    lines = open(full, 'rb').read().decode('ascii', 'replace').splitlines()
    tail = [x for x in lines if x.startswith(('checks:', 'ALL OK', 'REGRESSION:', 'ALL KILLED'))]
    w('- %s: %s sha256 %s; %s' % (name, p, sha(full), ' / '.join(tail) or '-'))
w('')
w('## 6. Executor variants (questions to the lead in the link report)')
w('')
for line in (
        '- V1 return source: the installed caches are copied before the FIRST arm of the link (installed_caches/, letter of'
        ' (g)(3)) and before EVERY arm (installed_pre/); the return uses installed_pre/ (accepted, item 247 (b)).',
        '- V2 timeouts: C4 (salt) 900 s from process start, other S4 arms 480 s, S6 480 s, pcw_val 600 s; stable draws S4 100'
        ' (as c142), S6 300 (as v142).',
        '- V3 integrity arm pcw_int: KYTY_S_PCW=1 + the stand, hold 120 s, video, environment T (RC5); app caches and GLCache'
        ' from copies taken right after pcw_3; order pcw_1 pcw_2 pcw_3 pcw_int pcw_4 pcw_val.',
        '- V4 video on every arm, the validation arm included.',
        '- V5 the strict KYTY_* row (every key = the seal) is an admission row beside the family row of (v)(6).',
        '- V6 S-pcw arms 0/1 and pcw_val run the M environment; pcw_int runs T (RC5).',
        '- V8 (S3b) the name of the later S6 seal - pred/03_s.md (sc_s.py PRED_S6, go_s.sh).',
        '- V9 (S3b) RC10 "GLCache not protected during the arm" is printed as the number of glc_post files of C1 / C3 whose'
        ' base (rel path without .bin / .toc) never changed between glc_launch and glc_post of any S arm (the "game bases" rule'
        ' of item 246 (v)) - a data row, not a gate.',
        '- V10 (S3b) RC11: (d) PASS needs the entry; an entered pcw_val that does not hold 300 s makes the S-pcw word'
        ' NOT_EVALUABLE (the hold row), as for the other arms.',
        '- V11 (S3b) RC2: return_prev ok=1 is written by go_s.sh when the arm starts (a guard would have refused the call before'
        ' any process); a json without it fails the admission row.',
        '- V12 (S3b) form W on pcw_val: KYTY_PIPELINE_PRECACHE=0 also stops the recipe writes, so pcw_val checks the'
        ' validation of the driver cache write of S-pcw only (the recipes write runs on pcw_2 / pcw_3 / pcw_int); executor'
        ' reading: this does not contradict the purpose of (d) - a question to the lead, not a stop.'):
    w(line)
w('')
w('## 7. Not claimed (item 250 (l))')
w('')
w('- that the harness runs its path inside the lock without an error (the first execution is S4; the path ran only on'
  ' fixture files with stubs); that the GLCache return or the salt neutralise the driver cache (before C1-C4); that the'
  ' W stop of sc143 comes from the caches; that the entry freezes are caused by the shaders; that the cache write causes'
  ' B33 (before the A/B (z)(5)); no number is a gain; 60 FPS is not promised; goal (B) does not change.')
w('')
text = '\n'.join(L) + '\n'
text.encode('ascii')
with open(OUT, 'wb') as f:
    f.write(text.encode('ascii'))
print('seal %s sha256 %s lines %d call lines %d seal lines %d' % (OUT, sha(OUT), len(L), len(s4), len(S.SEALED_NAMES)))

#!/usr/bin/env python3
"""mkseal_s.py - writes the seal C:/kyty/s288/pred/01_s.md of track S link S3 (HPP-313; ROADMAP "SESSION 122" item 241).
The plan of every arm is the output of DRY=2 bash go_s.sh <tag> verbatim; every sha line is computed here.  ASCII only.
Refuses when the seal exists (a seal is never rewritten)."""
import hashlib
import os
import subprocess
import sys

sys.path.insert(0, 'C:/kyty/s288')
import sc_s as S  # noqa: E402

ROOT = 'C:/kyty/s288'
OUT = 'C:/kyty/s288/pred/01_s.md'
if os.path.exists(OUT):
    print('seal exists, refuse')
    sys.exit(3)
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
w('# Seal 01_s - track S link S3 (HPP-313): harness go_s.sh, scorer sc_s.py, the arms of S4 (ROADMAP "SESSION 122" item 241)')
w('')
w('Written by C:/kyty/s288/s3/mkseal_s.py before any run of S4 or S6; after this seal the scorer, the fixtures, the mutants,')
w('the harness and the cache tool do not change (a change = a new seal 02+).  The S6 arms are NOT callable with this seal:')
w('they need the seal pred/02_s.md (written by the link S6 after S5a) that carries the line "pcw binary: <sha256> <path>",')
w('the seal lines below unchanged and the six S6 call lines.  ASCII only.')
w('')
w('## 1. Constants (item 241, numbered by its sub-items)')
w('')
for line in (
        '- (v)(1) unit of "frames with a skip" = held flips, sum skc_held_inc; T-6: = distinct frame= of skipped-draw lines;'
        ' reading 1 (letter): a held series counts WITH the first scene frame when it is held; reading 2 from the next row.',
        '- (v)(2) freeze: dt of a presented row; visible gap of a held series; gap_pipe = gap - sum dt of the series rows'
        ' (closing row included) with dt >= 100 000 us of class PCW or PRIO; thresholds K3 100 000 us and K2 1 000 000 us on'
        ' each; "a frame >= X" = a presented row dt >= X or a series with gap_pipe >= X.',
        '- (v)(3) classes of a row dt >= 100 ms: PCW ("Vulkan pipeline cache: saved" or "PipelinePrecache: saved" in group i'
        ' or i+1) -> SHADER -> PRIO (stall sum >= dt/2 and cpu_gpu_us < dt/2 under BOTH conventions: stall lines of group i and'
        ' of group i+1) -> GPUTHR (cpu_gpu_us >= dt/2) -> WAIT.',
        '- (v)(4) attribution only on a T arm with T-3 and T-4, else "undetermined"; PREP over the AvTrace lines assigned to'
        ' the row (a line of group g goes to the largest dt of rows g-1..g+2 = windows i-2..i+1, earliest on a tie); SHADER if'
        ' dt - PREP < 100 000 or a skipped-draw line or a "pipeline gfx ... async" line in groups i-2..i+1; partly if'
        ' PREP >= dt/2; TR and PL apart.',
        '- (v)(5) identities T-1 (below 200 000 lines), T-2 (min 64), T-5 (both readings), T-6 (main), sum skc_held = 0,'
        ' skc_bad printed, T-3 / T-4 on T arms, the M null control, no torn row, no row without FrameTrace-x, no gap of n,'
        ' the first scene frame = sc142.derive; a broken identity is FAIL of the arm; +-2 rows rule printed (secondary).',
        '- (v)(6) KYTY_* families (ASYNC_, PIPELINE_, SHADER_, S_, DUMP_, CACHE_MODE, CS_PRETRANSLATE) = the seal, else FAIL;'
        ' executor variant: every KYTY_* key = the seal (the path keys GATE_FILE, SAMPLE_GATE, REC present), also FAIL.',
        '- (v)(7) cold gate (C, T2): after the entry line (by log line) >= 1 AvTrace shader line, recipes +1, >= 1 skipped draw;'
        ' warm gate (S-warm): 0 stdout "Shaders:" lines and recipes end - start = 0.',
        '- (v)(8) creation cold: median us of in-game creations (gfx async / no suffix, cs async / sync) >= 20 000 cold,'
        ' <= 5 000 warm, < 10 "nothing to classify"; letter = every in-game creation, variant = after the entry line.',
        '- (v)(9) video checks the picture, not freezes; (v)(10) foreign-CPU row (fgcpu143.py) inside the lock;'
        ' (v)(11) sc142.py unchanged (pinned sha below) and its 217 fixtures.',
        '- (d) C1-C4 on L0 = shuriken_ninja_castle, reserves jack_in_the_box, cymbal_party_land (a candidate fails when C1 did'
        ' not enter or had < 10 creations); "return neutralises": median C1 >= 20 000, C3 >= 20 000, C3/C1 in [0.5; 2];'
        ' "GLCache keeps warmth": median C2 <= 0.25 x C1; "salt neutralises": prep_ms C4 >= 6 760, median C4 >= 20 000,'
        ' C4/C1 in [0.5; 2]; ms per recipe = prep_ms C4 / recipes C4; T2 only with "return neutralises".',
        '- (b)(2) preparation screen over 114 levels printed as a band [I]: (recipes C4 + 95 x {6, 28, 83}) x ms per recipe,'
        ' limit 180 s.',
        '- (e) S-warm: big_hand_pirate_island (base c142_02), voxel_world (c142_09), ice_iceberg (c142_05), M arms with the'
        ' full restore + one T arm on big_hand_pirate_island; components (i) held flips of the window (reading 1),'
        ' (ii) window rows dt >= 100 ms by class; "stays" if warm >= 0.5 x base; base < 5 events -> undetermined.',
        '- (zh) T2: small_pot_lava spin_drill_natural_cave light_gadget_graveyard enemy_taco hero_kratos, reserves in order'
        ' picup_light enemy_snake mini_rocket_chain hero_drake bonus_path_maker_mix (a reserve only while fewer than 5 arms'
        ' entered and cold); G: underwater_aerial_garden, big_hand_pirate_island, L0.',
        '- (z)(5) S-pcw (S6, seal 02): underwater_aerial_garden, hold 330 s (>= 300 s presented after the first scene frame),'
        ' KYTY_S_PCW_FORCE_MS=15000, ABBA 0 1 1 0 (pcw_1 pcw_2 pcw_3 pcw_4) + pcw_int (integrity, no snapshot: the app caches'
        ' and GLCache as pcw_3 left them, run right after pcw_3) + pcw_val (validation, KYTY_S_PCW=1); on the hold after the'
        ' window (rows after first frame + 599): (a) each arm 0 writes >= 15 and frames >= 100 ms with a write in groups'
        ' i-1..i+1 >= 0.5 x writes; (b) each arm 1 writes >= 15, 0 such frames, 0 save failures; (c) pcw_int loaded bytes ='
        ' last write of pcw_3, 0 "disabled"; (d) pcw_val 0 [Vulkan][E] with validation active; (e) video >= 3 000 frames,'
        ' 0 glitches, 0 death markers, the lead sheet.',
        '- (g) the arm protocol: see go_s.sh header; snapshot manifest d8ca8c8efb60b43b37c14a274a4738c83a9dc5866cc784e649e97314c5fd45c4,'
        ' driver snapshot manifest 1767ca0a975f26c1cb90eff80e6cccb959dc507f2a1178506a6ef1dbcac97028; salt only on C4.'):
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
w('- S4 binary: C:/kyty/s128/kyty_emulator_9235a7ac.exe sha256 %s (installed build, item 228 (v): restored after each arm).'
  % sha('C:/kyty/s128/kyty_emulator_9235a7ac.exe'))
for name, p in (('fixtures sc_s', 's3/test_sc_s.out.txt'), ('fixtures cachex', 's3/test_cachex_s.out.txt'),
                ('fixtures harness', 's3/test_go_s.out.txt'), ('inherited fixtures sc142 (217)', 's3/test_sc142_inherited.out.txt'),
                ('regression 12 sc142 logs', 's3/regress_s.out.txt'), ('mutants (counted full run)', 's3/mut_sc_s.txt'),
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
        ' (g)(3)) and before EVERY arm (installed_pre/); the return uses installed_pre/ - another chain may run between two'
        ' arms, and the first copy would undo its cache growth.  Both manifests go into the arm cache json.',
        '- V2 timeouts: C4 (salt) 900 s from process start (cold preparation screen), other S4 arms 480 s, S6 480 s,'
        ' pcw_val 600 s; stable draws S4 100 (as c142), S6 300 (as v142).',
        '- V3 integrity arm pcw_int: KYTY_S_PCW=1 + the stand, hold 120 s, video; it restores the app caches and GLCache from'
        ' copies taken right after pcw_3 (app_post/pcw_3, glc_post/pcw_3) and runs right after pcw_3 (order pcw_1 pcw_2 pcw_3'
        ' pcw_int pcw_4 pcw_val).',
        '- V4 video on every arm, the validation arm included ((g)(5) "video on every arm").',
        '- V5 the strict KYTY_* row (every key = the seal) is an admission row beside the family row of (v)(6).',
        '- V6 S-pcw arms run the M environment (no AvTrace) - both sides of the ABBA pay the same.'):
    w(line)
w('')
text = '\n'.join(L) + '\n'
text.encode('ascii')
with open(OUT, 'wb') as f:
    f.write(text.encode('ascii'))
print('seal %s sha256 %s lines %d call lines %d seal lines %d' % (OUT, sha(OUT), len(L), len(s4), len(S.SEALED_NAMES)))

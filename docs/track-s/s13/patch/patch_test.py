"""S13a4 (HPP-553, ROADMAP item 452 (b)-(d)): patch s13/test_sc_s13.py - the seal 13 names, S9 by the three classes, the fixtures
Y1-Y9 (RC1) and Z1-Z9 (RC2).  Every replacement must occur exactly once.  LF, ASCII.
    python patch_test.py <path of test_sc_s13.py>
"""
import re
import sys

NL = chr(10)
P = sys.argv[1]
src = open(P, 'rb').read().decode('ascii')
assert chr(13) not in src
REPL = []


def R(a, b):
    REPL.append((a, b))


R('''"edition: base pred/12_s.md sha256 <sha>" (E6-E6g); RC7 - the line man_launch_glc (S11).''',
  '''"edition: base pred/12_s.md sha256 <sha>" (E6-E6g); RC7 - the line man_launch_glc (S11).
S13a4 (item 452 (b), (c)): RC1 - the data of the reading of item 446 (b) per arm (Y1-Y9: the line "no ... yet" and its text, 0 / 1
rows after the later line, the later of the two lines both ways, another variant directory and a slash path, the form with both
lines of the end of the preparation screen "not counted" with the RC4 count unchanged, no ready / no "no ... yet" line, ASCII, the
lines of --read per arm, no outcome changed); RC2 - the class "after the arm" by an explicit list of names (Z1-Z9: a crash with a
failing return_glc, no death with a failing man_post_app, a failing cache-protocol row before the arm, each row after the arm
alone, k_02 with app_post_copy missing, w13 with a failing return_app, every row of every arm kind in exactly one list, an
UNCLASSED row, a name in two lists, the words); S9 prints the three classes; the seal names are those of seal 13.''')
# S9: the three classes
R('''ok &= case('S9 RC2 the split: 5 rows by the log (S-pcw, GamePatch, compatibility, variant, window), the rest before the run; '
           'fmt_arm names each row "before the run" / "by the log" and prints the gate "ok"', len(clean['log_rows']) == 5 and
           clean['n_pre'] == len(clean['admit']) - 5 and sum(1 for x in fa if ' admit by the log ' in x) == 5 and
           sum(1 for x in fa if ' admit before the run ' in x) == clean['n_pre'] and
           '  admission gate (item 436 (b)(2)): ok' in fa and all(v == 'ok' for v in clean['log_rows'].values()))''',
  '''ok &= case('S9 RC2 (item 452 (c)) the split by name: 5 rows by the log (S-pcw, GamePatch, compatibility, variant, window), 5 '
           'rows after the arm (return_app, return_glc, the binary after, man_post_app, man_post_glc), the rest before the run, '
           'none UNCLASSED; fmt_arm names the class of each row, prints the gate "ok" and the rows after the arm "ok"',
           len(clean['log_rows']) == 5 and sum(1 for x in fa if ' admit by the log ' in x) == 5 and
           sum(1 for x in fa if ' admit after the arm ' in x) == 5 and
           sum(1 for x in fa if ' admit before the run ' in x) == len(clean['admit']) - 10 and
           not any(' admit UNCLASSED ' in x for x in fa) and '  admission gate (item 436 (b)(2)): ok' in fa and
           '  rows after the arm (item 452 (c)): ok' in fa and all(v == 'ok' for v in clean['log_rows'].values()))''')
# the new fixtures, right after T11 (before the order section)
T11END = ("           S.entry_state(r)[0] == 'void' and W('E1-screen', S.members_u(r)) is False and\n"
          "           ': FAIL - denominator 19 of 19' in ent_line(out)[0])\n")
NEW = r'''# ================================================================================ S13a4: RC1 (item 452 (b)) - the data of item 446 (b)
NOPB = 'PipelinePrecache: no _ShaderCache' + BS + 'PPSA21564' + BS + VAR + BS + 'pipelines.bin yet'
NOPB_O = 'PipelinePrecache: no _ShaderCache' + BS + 'PPSA21564' + BS + 'variant_other' + BS + 'pipelines.bin yet'
NOPB_SL = 'PipelinePrecache: no _ShaderCache/PPSA21564/' + VAR + '/pipelines.bin yet'


def empty_form(nopb=NOPB):
    """The empty-set form of k_01 (s12_gw): the line "no ... yet" in place of "all pipelines created" (before the ready line)."""
    return [(nopb if x.startswith('PipelinePrecache: all pipelines created') else x)
            for x in scene('other_level', post_rows(), header=HEADER_M)]


def k_arm(lines, tag='k_01'):
    return make_arm(tag, lines, video=False, sheet=False, stdout=['Cache test mode: none'])


def last_ft(lines):
    return max(i for i, x in enumerate(lines) if x.startswith('FrameTrace: n='))


ry1 = k_arm(empty_form())
nd = ry1['nopb']
fa = S.fmt_arm(ry1)
dl = [x for x in fa if x.startswith('  data of item 446 (b) (item 452 (b), no outcome reads it): ')]
ok &= case('Y1 RC1 the empty-set form on k_01: (i) the line number and the whole text of "no ... yet"; (ii) the FrameTrace rows '
           'after max(ready, "no ... yet") = every row of the log (both lines in the header); the parent directory = the variant '
           'of the seal line; one data line in fmt_arm with the text and the count',
           ry1['fail'] == [] and nd['line'] == ry1['prep_end']['nopb_line'] and nd['text'] == NOPB and nd['why'] is None and
           nd['later'] == ry1['prep_end']['ready_line'] and nd['rows_after'] == ry1['present_rows'] > 0 and
           nd['variant'] is True and len(dl) == 1 and ('(i) "PipelinePrecache: no <path> yet": line %d "%s"; ' % (
               nd['line'], NOPB)) in dl[0] and ('"no ... yet" line %d): %d; ' % (nd['line'], ry1['present_rows'])) in dl[0] and
           dl[0].endswith('(executor\'s addition): yes'))
st = S.entry_state(ry1)
ok &= case('Y2 RC1 the data change no outcome: the empty-set k_01 stays "void" (the preparation screen not passed by RC4), its RC4 '
           'count None (the reading of item 446 (b) is the lead\'s)', st[0] == 'void' and
           'the preparation screen not passed' in st[1] and ry1['prep_end']['rows_after'] is None)
bl = [x for x in empty_form() if x != NOPB and not x.startswith('ShaderPreparation: ready')]
r0 = k_arm(bl + [NOPB, PREP_LINES[1]])
r1 = k_arm(bl[:last_ft(bl)] + [NOPB, PREP_LINES[1]] + bl[last_ft(bl):])
ok &= case('Y3 RC1 the edge: both lines after the last FrameTrace row -> (ii) 0 (counted, not "not counted"); both before the last '
           'row -> (ii) 1', r0['nopb']['why'] is None and r0['nopb']['rows_after'] == 0 and r1['nopb']['why'] is None and
           r1['nopb']['rows_after'] == 1 and any('"no ... yet" line %d): 0; ' % r0['nopb']['line'] in x for x in S.fmt_arm(r0)))
bh = [x for x in empty_form() if x != NOPB]
ra = k_arm(bh[:last_ft(bh)] + [NOPB] + bh[last_ft(bh):])
bn = [x for x in empty_form() if not x.startswith('ShaderPreparation: ready')]
rb = k_arm(bn[:last_ft(bn)] + [PREP_LINES[1]] + bn[last_ft(bn):])
ok &= case('Y4 RC1 the LATER of the two lines: "no ... yet" after the ready line -> counted after "no ... yet" (1); "no ... yet" '
           'before the ready line -> counted after the ready line (1)', ra['nopb']['line'] > ra['prep_end']['ready_line'] and
           ra['nopb']['later'] == ra['nopb']['line'] and ra['nopb']['rows_after'] == 1 and
           rb['nopb']['line'] < rb['prep_end']['ready_line'] and rb['nopb']['later'] == rb['prep_end']['ready_line'] and
           rb['nopb']['rows_after'] == 1)
ro = k_arm(empty_form(NOPB_O))
rs = k_arm(empty_form(NOPB_SL))
rp = S.score_arm('k_01', ROOT, PRED_SHA, PRED, ('PENDING', None, None))
ok &= case('Y5 RC1 the path with another variant directory -> its text printed whole, the variant NO, (ii) counted; a path with '
           'slashes and the variant of the seal -> yes; the seal PENDING -> n/a', ro['nopb']['text'] == NOPB_O and
           ro['nopb']['variant'] is False and ro['nopb']['rows_after'] == ro['present_rows'] and
           any(('"%s"' % NOPB_O) in x and x.endswith('(executor\'s addition): NO') for x in S.fmt_arm(ro)) and
           rs['nopb']['variant'] is True and rs['nopb']['text'] == NOPB_SL and rp['nopb']['variant'] is None and
           any(x.endswith('(executor\'s addition): n/a') for x in S.fmt_arm(rp)))
both = k_arm(scene('other_level', post_rows(), header=HEADER_M + [NOPB]))
fa = S.fmt_arm(clean)
ok &= case('Y6 RC1 the form with both lines of the end of the preparation screen (the clean U arm) -> (ii) "not counted" naming the '
           'line "all pipelines created", (i) "none"; the RC4 count unchanged (every row after the later of ready / created); the '
           'same with a "no ... yet" line too -> not counted, (i) printed', clean['nopb']['why'] is not None and
           clean['nopb']['why'].startswith('not counted: the line "PipelinePrecache: all pipelines created" is present (line %d)'
                                            % clean['prep_end']['created_line']) and clean['nopb']['rows_after'] is None and
           clean['nopb']['line'] is None and clean['prep_end']['rows_after'] == clean['present_rows'] and
           any('(i) "PipelinePrecache: no <path> yet": none; ' in x and ': not counted: the line "PipelinePrecache: all '
               'pipelines created" is present' in x for x in fa) and both['nopb']['line'] is not None and
           both['nopb']['rows_after'] is None and both['nopb']['why'].startswith('not counted: the line "PipelinePrecache: all'))
rn = k_arm([x for x in empty_form() if not x.startswith('ShaderPreparation: ready')])
rt = k_arm([x for x in scene('other_level', post_rows(), header=HEADER_M)
            if not x.startswith('PipelinePrecache: all pipelines created')])
ok &= case('Y7 RC1 not counted: no ready line (with "no ... yet") -> the reason names the ready line; neither "all pipelines '
           'created" nor "no ... yet" -> the reason names "no ... yet"', rn['nopb']['rows_after'] is None and
           rn['nopb']['why'] == 'not counted: no line "ShaderPreparation: ready"' and rn['nopb']['line'] is not None and
           rt['nopb']['rows_after'] is None and rt['nopb']['why'] == 'not counted: no line "PipelinePrecache: no ... yet"')
ru8 = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T + [NOPB.replace('PPSA21564', 'PPSA21564' + chr(233))]))
txt = NL.join(S.fmt_arm(ru8))
try:
    txt.encode('cp1250', 'strict')
    cp8 = True
except UnicodeError:
    cp8 = False
ok &= case('Y8 RC1 a path with a byte above 127 -> the text in ASCII with backslash escapes, the arm output ASCII (strict '
           'cp1250); the members of the U arm = those of the clean arm (the data change no member)',
           ru8['nopb']['text'] is not None and (BS + 'xc3' + BS + 'xa9') in ru8['nopb']['text'] and
           all(ord(c) < 128 for c in txt) and cp8 and [m[:2] for m in S.members_u(ru8)] == [m[:2] for m in S.members_u(clean)])
gy = get_of({'k_01': ry1, 'u_02': ru8})
ko = S.read_k(gy)
_, ku = S.read_known(gy)
ok &= case('Y9 RC1 --read prints the data line per made k arm, per U arm and for w13; a not made k arm prints no data line',
           any(x.startswith('k_01 data of item 446 (b) (item 452 (b), no outcome reads it): (i) "PipelinePrecache: no <path> '
                            'yet": line %d' % nd['line']) for x in ko) and
           not any(x.startswith('k_02 data of item 446 (b)') for x in ko) and
           any(x.startswith('u_02 data of item 446 (b) (item 452 (b), no outcome reads it): (i) "PipelinePrecache: no <path> '
                            'yet": line %d' % ru8['nopb']['line']) for x in ku) and
           any(x.startswith('u_01 data of item 446 (b) (item 452 (b), no outcome reads it): (i) "PipelinePrecache: no <path> '
                            'yet": none') for x in ku) and
           any(x.startswith('w13 data of item 446 (b) (item 452 (b), no outcome reads it): ') for x in ku))
# ================================================================================ S13a4: RC2 (item 452 (c)) - the class "after the arm"
CRASH = ['Unhandled exception: x']
R_RGLC = 'return_glc after the arm = its copy'
rz1 = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T, tail=CRASH),
               cj=cj_for('u_01', return_glc=dict(expected='17' * 32, got='99' * 32)))
mu = S.members_u(rz1)
fa = S.fmt_arm(rz1)
ok &= case('Z1 RC2 a crash and a failing return_glc (after the arm) -> the gate "ok", E3-death FAILS, the arm FAIL, "entered" void; '
           'fmt_arm prints the row FAIL with its class and the line of the rows after the arm',
           S.admission_gate(rz1)[0] == 'ok' and W('E3-death', mu) is False and S.arm_word(mu) == 'FAIL' and
           S.entry_state(rz1)[0] == 'void' and S.post_fail(rz1) == [R_RGLC] and
           any(x.startswith('  FAIL admit after the arm %s (' % R_RGLC) for x in fa) and
           ('  rows after the arm (item 452 (c)): FAIL %s - entry_state void, the members not gated' % R_RGLC) in fa)
rz2 = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T), cj=cj_for('u_01', man_post_app=None))
ok &= case('Z2 RC2 no death marker and a failing man_post_app -> the members as without it (= the clean arm, PASS), the reference '
           'too; "entered" void (the clean arm "yes")', [m[:2] for m in S.members_u(rz2)] == [m[:2] for m in S.members_u(clean)]
           and S.arm_word(S.members_u(rz2)) == 'PASS' and [m[:2] for m in S.ref_members(rz2)] ==
           [m[:2] for m in S.ref_members(clean)] and S.entry_state(rz2)[0] == 'void' and S.entry_state(clean)[0] == 'yes' and
           rz2['fail'] == ['admission: manifest man_post_app recorded'])
z3 = True
for over in (dict(man_pre_app=None), dict(restore_app=dict(expected=EMPTY, got='99' * 32)), dict(return_prev=dict(ok='0')),
             dict(glc_pre_copy=None), dict(installed_before=dict(sha='cd' * 32)), dict(man_launch_glc=dict(sha='98' * 32))):
    r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T, tail=CRASH), cj=cj_for('u_01', **over))
    z3 &= S.admission_gate(r)[0] == 'pre' and all(m[1] is None for m in S.members_u(r)) and S.arm_word(S.members_u(r)) == \
        'UNDETERMINED'
ok &= case('Z3 RC2 the edge of the old letter: a failing row of the cache protocol BEFORE the arm (man_pre_app, restore_app, '
           'return_prev, glc_pre_copy, the binary before, man_launch_glc) with a crash -> every member UNDETERMINED', z3)
z4 = []
for key, over in (('return_app after the arm = its copy', dict(return_app=dict(expected='16' * 32, got='99' * 32))),
                  (R_RGLC, dict(return_glc=dict(expected='17' * 32, got=None))),
                  ('installed binary after the arm = before the arm (item 250 (b))', dict(installed_after=dict(sha='cd' * 32))),
                  ('manifest man_post_app recorded', dict(man_post_app=None)),
                  ('manifest man_post_glc recorded', dict(man_post_glc=None))):
    r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T), cj=cj_for('u_01', **over))
    z4.append(S.post_fail(r) == [key] and S.admission_gate(r)[0] == 'ok' and
              [m[:2] for m in S.members_u(r)] == [m[:2] for m in S.members_u(clean)] and S.entry_state(r)[0] == 'void')
ok &= case('Z4 RC2 each row after the arm alone (return_app, return_glc, the binary after, man_post_app, man_post_glc) -> gate ok, '
           'the members = the clean arm, "entered" void', z4 == [True] * 5)
k1c = k_arm(scene('other_level', post_rows(), header=HEADER_M))
k2c = k_arm(scene('other_level', post_rows(), header=HEADER_M), tag='k_02')
k2f = make_arm('k_02', scene('other_level', post_rows(), header=HEADER_M), cj=cj_for('k_02', app_post_copy=None), video=False,
               sheet=False, stdout=['Cache test mode: none'])
ko = S.read_k(get_of({'k_01': k1c, 'k_02': k2f}))
ok &= case('Z5 RC2 k_02 without app_post_copy (after the arm) -> "entered" void (the same arm with it: "no"), the gate ok; '
           'read_k prints the row FAIL', S.entry_state(k2c)[0] == 'no' and S.entry_state(k2f)[0] == 'void' and
           S.admission_gate(k2f)[0] == 'ok' and S.post_fail(k2f) == ['app_post_copy recorded (cat/k_02, the next arm restores it)']
           and ('k_02 rows after the arm (item 452 (c)): FAIL app_post_copy recorded (cat/k_02, the next arm restores it) - '
                'entry_state void, the members not gated') in ko and 'k_01 rows after the arm (item 452 (c)): ok' in ko)
wz = make_arm('w13', scene(WL, wpost, header=WH, tail=['[Vulkan][W][2] note']), video=False, sheet=False,
              stdout=['Cache test mode: prepare-cold'], cj=cj_for('w13', return_app=dict(expected='16' * 32, got='99' * 32)))
mw = S.members_w(wz)
ok &= case('Z6 RC2 w13 with a failing return_app -> the W members as without it (no row "W admitted and entered", PASS = the '
           'clean W), "entered" void', [m[:2] for m in mw] == [m[:2] for m in S.members_w(w_ok)] and S.arm_word(mw) == 'PASS'
           and W('W admitted and entered', mw) == 'absent' and S.entry_state(wz)[0] == 'void' and S.gating_fail(wz) == [] and
           wz['fail'] == ['admission: return_app after the arm = its copy'])
names = set()
for t in ('u_01', 'k_01', 'k_02', 'w13'):
    names |= set(a[0] for a in S.admit(S.SPEC[t], js_for(t), PRED_SHA, PRED, cj_for(t), cjs, INSTT))
names |= set(a[0] for a in S.cache_rows(u1, None, cjs, INSTT))
for x in (clean, w_ok, k1c, k2c, ry1):
    names |= set(a[0] for a in x['admit'])
uncl = sorted(n for n in names if S.row_class(n) is None)
post = set(n for n in names if S.row_class(n) == S.C_POST)
ok &= case('Z7 RC2 every admission row of every arm kind (u, k_01, k_02, w13, no cache json, the rows by the log of whole arms) '
           'is in exactly one list - UNCLASSED none (a new row without a class fails here); "after the arm" = return_app, '
           'return_glc, the binary after, man_post_app, man_post_glc, app_post_copy of k_01 / k_02; the 5 rows by the log are '
           '"by the log"', uncl == [] and post == {'return_app after the arm = its copy', R_RGLC,
                                                    'installed binary after the arm = before the arm (item 250 (b))',
                                                    'manifest man_post_app recorded', 'manifest man_post_glc recorded',
                                                    'app_post_copy recorded (cat/k_01, the next arm restores it)',
                                                    'app_post_copy recorded (cat/k_02, the next arm restores it)'} and
           all(S.row_class(n) == S.C_LOG for n in clean['log_rows']) and len(names) >= 40 and
           S.row_class('cache protocol json present') == S.C_PRE)
x8 = copy.deepcopy(clean)
x8['admit'].append(('a new admission row', False, 'x'))
x8['fail'] = x8['fail'] + ['admission: a new admission row']
save = S.ADMIT_POST
S.ADMIT_POST = save + ('prereg = the seal',)
amb = S.row_class('prereg = the seal')
S.ADMIT_POST = save
ok &= case('Z8 RC2 an UNCLASSED failing row is read as before the run (every member UNDETERMINED) and printed UNCLASSED; a name '
           'in two lists is UNCLASSED', S.row_class('a new admission row') is None and S.admission_gate(x8)[0] == 'pre' and
           all(m[1] is None for m in S.members_u(x8)) and
           any(x.startswith('  FAIL admit UNCLASSED a new admission row') for x in S.fmt_arm(x8)) and amb is None and
           S.row_class('prereg = the seal') == S.C_PRE)
word, out = S.read_known(get_of({'u_01': rz2}))
ok &= case('Z9 RC2 a U arm with a failing row after the arm only: KNOWN_SCENES PASS (its members PASS), its line "rows after the '
           'arm" FAIL in --read, its level in the denominator (entered void) -> KNOWN_SCENES_ENTERED PASS on 19',
           word == 'PASS' and 'u_01 rows after the arm (item 452 (c)): FAIL manifest man_post_app recorded - entry_state void, '
           'the members not gated' in out and 'w13 rows after the arm (item 452 (c)): ok' in out and
           ': PASS - denominator 19 of 19' in ent_line(out)[0])
make_arm('u_01', scene(UL, post_rows(), header=HEADER_T))         # the clean u_01 back for main (P1)
make_arm('w13', scene(WL, wpost, header=WH, tail=['[Vulkan][W][2] note']), video=False, sheet=False,
         stdout=['Cache test mode: prepare-cold'])
'''
R(T11END, T11END + NEW)

for a, b in REPL:
    n = src.count(a)
    if n != 1:
        raise SystemExit('patch_test: the target occurs %d times: %r' % (n, a[:120]))
    src = src.replace(a, b)

# the seal 13 names in the edition / check_seal block (E5 .. F7) and the global seal file names
lines = src.split(NL)
i0 = next(i for i, x in enumerate(lines) if x.startswith("sb, sbb = BASE / 'pred' / 'e09.md'"))
i1 = next(i for i, x in enumerate(lines) if x.startswith("ok &= case('F7 the sealed names cover"))
n_ed = 0
for i in range(i0, i1):
    y = re.sub(r'\b12b\b', '13b', lines[i])
    y = re.sub(r'(?<![0-9.])\b12\b(?![0-9])', '13', y)
    y = y.replace('pred/12_s.md', 'pred/13_s.md').replace("'12_s.md'", "'13_s.md'").replace("'12b_s.md'", "'13b_s.md'")
    if y != lines[i]:
        n_ed += 1
        lines[i] = y
src = NL.join(lines)
src.encode('ascii')
open(P, 'wb').write(src.encode('ascii'))
print('patch_test: %d replacements, %d lines of the edition / check_seal block renamed to seal 13, applied to %s' % (
    len(REPL), n_ed, P))

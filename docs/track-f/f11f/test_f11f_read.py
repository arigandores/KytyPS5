"""F11f (HPP-468): fixtures of f11f_read.py - one per member of items 376 (e)-(zh), 384 (v)-(d) and per edge.  Ends with ALL OK.
First line: suite <name> sha256 <sha of this file> target <name> sha256 <sha of the reader> (item 150 (v)).  ASCII only."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f11f_read as R  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_f11f_read.py sha256 %s target f11f_read.py sha256 %s' % (sha(os.path.abspath(__file__)),
                                                                          sha(os.path.join(HERE, 'f11f_read.py'))))
TMP = tempfile.mkdtemp(prefix='f11f_fx_')
FAILS = []
N = [0]


def check(name, cond, info=''):
    N[0] += 1
    if cond:
        print('ok   %s' % name)
    else:
        print('FAIL %s %s' % (name, info))
        FAILS.append(name)


S0 = R.SLOTS[0]
S9 = R.SLOTS[9]


def lanes_line(t=(0, 0, 0, 0, 0, 0, 0, 0), tri=(0, 0, 0, 0), box=(0, 0, 0, 0), t7=(0, 0, 0, 0), size_viol=None, node64=0,
               traps=0, trap_lanes=0, groups=1, max_step=10, lanes=None, size_off=0, over_max=0):
    if size_viol is None:
        size_viol = sum(tri) + sum(box) + sum(t7)
    if lanes is None:
        lanes = sum(t)
    return ('DiagBvhNodes: lanes=%d t0=%d t1=%d t2=%d t3=%d t4=%d t5=%d t6=%d t7=%d size_viol=%d size_off=%d node64=%d over_max=%d '
            'b_tri=%d/%d/%d/%d b_box=%d/%d/%d/%d b_t7=%d/%d/%d/%d traps=%d trap_lanes=%d groups=%d max_step=%d'
            % ((lanes,) + tuple(t) + (size_viol, size_off, node64, over_max) + tuple(tri) + tuple(box) + tuple(t7)
               + (traps, trap_lanes, groups, max_step)))


def slots_line(d, other=0):
    return 'DiagBvhNodes: slots%s other=%d' % (''.join(' %s=%d' % (h, n) for h, n in d.items()), other)


MODE = 'DiagBvhNodes: mode=1 words=64 tail_bytes=320'
GOOD_T = (10, 20, 0, 0, 30, 40, 0, 0)        # lanes 100: tri 0-1, boxes 4-5
LV = 'enemy_final'


def mk(lines, level=LV, started=True, hold=(10.0, 20.0, 330.0), hold_exit=None, name=None):
    name = name or ('fx%d' % N[0])
    body = ['[main] boot', 'git = 0.1-xyz']
    body += [MODE] if lines is not None and 'NOMODE' not in lines else []
    if started:
        body.append('GuestOut: Level has started: %s' % level)
    body += [x for x in (lines or []) if x != 'NOMODE']
    lp = os.path.join(TMP, name + '.txt')
    with open(lp, 'wb') as f:
        f.write(('\n'.join(body) + '\n').encode())
    run = None
    if hold is not None:
        run = dict(started_s=hold[0], stable_s=hold[1], hold_s=hold[2], hold_exit=hold_exit, outcome='ok')
    return R.classify(R.scan(lp), level, run)


def good(extra_before=(), extra_after=(), **kw):
    t = kw.pop('t', GOOD_T)
    slots = kw.pop('slots', None)
    other = kw.pop('other', 0)
    lanes = kw.get('lanes', sum(t))
    if slots is None:
        slots = {S9: lanes - other}
    return list(extra_before) + [lanes_line(t=t, **kw), slots_line(slots, other)] + list(extra_after)


# ---- the base case
o = mk(good())
check('base NOT_REACHED 369', o['word369'][0] == 'NOT_REACHED', o['word369'])
check('base NOT_REACHED 376', o['word376'][0] == 'NOT_REACHED', o['word376'])
check('base admitted', o['admitted'], o['admission'])
check('base identities ok', o['ident_fail_n'] == 0, o['ident_fail'])

# ---- RC1: the size violation is the last field; the bucket number is not read
o = mk(good(t=(10, 20, 0, 0, 30, 40, 0, 0), tri=(1, 1, 5, 0)))
check('RC1 tri third field > 0, fourth 0 -> not violated', o['word376'][0] == 'NOT_REACHED' and o['size_violation'] == 0,
      (o['word376'], o['size_violation']))
check('RC1 within twice row tri fields 2-3 = 6', o['within_twice'][0] == 6, o['within_twice'])
o = mk(good(tri=(0, 0, 0, 1)))
check('RC1 tri fourth field > 0 -> REACHED SIZE', o['word376'][0] == 'REACHED' and o['reached'] == ['SIZE'], o['word376'])
check('RC1 letter 369 also REACHED', o['word369'][0] == 'REACHED', o['word369'])
o = mk(good(box=(0, 0, 3, 0)))
check('RC1 box third field > 0 -> not violated', o['word376'][0] == 'NOT_REACHED', o['word376'])
o = mk(good(box=(0, 0, 0, 2)))
check('RC1 box fourth field > 0 -> REACHED SIZE', o['word376'][0] == 'REACHED' and o['size_violation'] == 2, o['word376'])
o = mk(good(t=(10, 20, 0, 0, 30, 40, 0, 4), t7=(0, 0, 4, 0)))
check('RC1 t7 third field > 0 -> not violated', o['word376'][0] != 'REACHED', o['word376'])
o = mk(good(t=(10, 20, 0, 0, 30, 40, 0, 4), t7=(0, 0, 0, 4)))
check('RC1 t7 fourth field > 0 -> REACHED SIZE (type 7 class)', o['word376'][0] == 'REACHED' and o['size_violation'] == 4,
      (o['word376'], o['size_violation']))
o = mk(good(tri=(1, 0, 0, 1), box=(0, 0, 0, 1), t7=(0, 0, 0, 1), t=(10, 20, 0, 0, 30, 40, 0, 1)))
check('RC1 sum over three classes = 3', o['size_violation'] == 3, o['size_violation'])
o = mk(good(tri=(3, 0, 0, 0)))
check('RC1 first field only -> not violated', o['word376'][0] == 'NOT_REACHED' and o['within_twice'][3] == 3, o['within_twice'])

# ---- types 2-3
o = mk(good(t=(10, 20, 1, 0, 30, 40, 0, 0)))
check('t2 > 0 -> REACHED TYPES23', o['word376'][0] == 'REACHED' and o['reached'] == ['TYPES23'], o['word376'])
o = mk(good(t=(10, 20, 0, 1, 30, 40, 0, 0)))
check('t3 > 0 -> REACHED TYPES23 (369 too)', o['word376'][0] == 'REACHED' and o['word369'][0] == 'REACHED', o['word369'])
o = mk(good(t=(0, 0, 1, 0, 0, 0, 0, 0)))
check('t2 > 0 with control fail -> still REACHED', o['word376'][0] == 'REACHED', o['word376'])
o = mk(good(t=(10, 20, 2, 0, 30, 40, 0, 0), tri=(0, 0, 0, 1)))
check('both kinds named', o['reached'] == ['TYPES23', 'SIZE'], o['reached'])

# ---- RC2 identities, each and its violation
o = mk(good(lanes=99))
check('RC2 lanes != sum t -> UNDETERMINED', o['word376'][0] == 'UNDETERMINED' and 'identities' in o['word376'][1], o['word376'])
check('RC2 lanes != sum t named', any('lanes != t0' in b for _, bb in o['ident_fail'] for b in bb), o['ident_fail'])
o = mk(good(tri=(1, 0, 0, 0), size_viol=2))
check('RC2 size_viol != 12 fields -> UNDETERMINED', o['word376'][0] == 'UNDETERMINED'
      and any('size_viol !=' in b for _, bb in o['ident_fail'] for b in bb), o['ident_fail'])
o = mk(good(tri=(1, 0, 0, 0), size_viol=1))
check('RC2 size_viol = 12 fields holds', o['ident_fail_n'] == 0, o['ident_fail'])
o = mk(good(t=(1, 1, 0, 0, 1, 1, 0, 0), tri=(2, 0, 0, 0), node64=3))
check('RC2 size_viol + node64 > lanes -> UNDETERMINED', o['word376'][0] == 'UNDETERMINED'
      and any('node64' in b for _, bb in o['ident_fail'] for b in bb), o['ident_fail'])
o = mk(good(t=(1, 1, 0, 0, 1, 1, 0, 0), tri=(2, 0, 0, 0), node64=2))
check('RC2 size_viol + node64 = lanes holds (edge)', o['ident_fail_n'] == 0, o['ident_fail'])
o = mk(good(slots={S9: 50}, other=10))
check('RC2 slots + other != lanes -> UNDETERMINED', o['word376'][0] == 'UNDETERMINED'
      and any('slots + other' in b for _, bb in o['ident_fail'] for b in bb), o['ident_fail'])
o = mk(good(slots={S9: 40, S0: 50}, other=10))
check('RC2 slots + other = lanes with two slots and other holds', o['ident_fail_n'] == 0, o['ident_fail'])
o = mk(good(max_step=(1 << 31)))
check('RC2 max_step = 2^31 -> UNDETERMINED', o['word376'][0] == 'UNDETERMINED'
      and any('max_step' in b for _, bb in o['ident_fail'] for b in bb), o['ident_fail'])
o = mk(good(max_step=(1 << 31) - 1))
check('RC2 max_step = 2^31 - 1 holds (edge)', o['ident_fail_n'] == 0, o['ident_fail'])
o = mk([lanes_line(t=GOOD_T)])
check('RC2 missing slots line -> UNDETERMINED', o['word376'][0] == 'UNDETERMINED'
      and any('no slots line' in b for _, bb in o['ident_fail'] for b in bb), o['ident_fail'])
o = mk([lanes_line(t=GOOD_T)[:-12], slots_line({S9: 100})])
check('RC2 truncated lanes line -> UNDETERMINED', o['word376'][0] == 'UNDETERMINED'
      and any('unparsable' in b for _, bb in o['ident_fail'] for b in bb), o['ident_fail'])
# an earlier line failing makes the tag UNDETERMINED even when the last holds ('on every line')
o = mk(good(lanes=7) + good())
check('RC2 earlier line failing -> UNDETERMINED', o['word376'][0] == 'UNDETERMINED' and o['ident_fail_n'] == 1, o['ident_fail'])
check('RC2 failure also gates the letter word', o['word369'][0] == 'UNDETERMINED', o['word369'])
# a failing identity with a positive count: identities first
o = mk(good(t=(10, 20, 1, 0, 30, 40, 0, 0), lanes=5))
check('RC2 failure beats a positive count', o['word376'][0] == 'UNDETERMINED', o['word376'])
# slots line from another thread interleaved
o = mk([lanes_line(t=GOOD_T), 'other thread line', slots_line({S9: 100})])
check('RC2 interleaved line between lanes and slots ok', o['ident_fail_n'] == 0, o['ident_fail'])
# prefix before the key (thread header)
o = mk(['[12][10:00:00.000] ' + lanes_line(t=GOOD_T), '\t' + slots_line({S9: 100})])
check('line with a prefix parsed', o['ident_fail_n'] == 0 and o['lanes'] == 100, (o['ident_fail'], o['lanes']))
# CRLF line ends
o = mk([lanes_line(t=GOOD_T) + '\r', slots_line({S9: 100}) + '\r'])
check('CRLF line ends parsed', o['ident_fail_n'] == 0 and o['lanes'] == 100, (o['ident_fail'], o['lanes']))

# ---- the last line is read
o = mk(good(t=(1, 1, 0, 0, 1, 1, 0, 0)) + good(t=(10, 20, 0, 0, 30, 40, 0, 0)))
check('last line is read (lanes 100)', o['lanes'] == 100 and o['lanes_lines'] == 2, (o['lanes'], o['lanes_lines']))

# ---- (zh)(1) NO_BVH and the mode line
o = mk([])
check('(zh)(1) no lanes line with mode line -> NO_BVH', o['word376'][0] == 'NO_BVH', o['word376'])
check('(zh)(1) letter 369 without lanes -> UNDETERMINED (control fails)', o['word369'][0] == 'UNDETERMINED', o['word369'])
o = mk(good(t=(0, 0, 0, 0, 0, 0, 0, 0), slots={}))
check('(zh)(1) lanes = 0 line with mode line -> NO_BVH', o['word376'][0] == 'NO_BVH', o['word376'])
o = mk(['NOMODE'])
check('(zh)(1) no mode line -> UNDETERMINED', o['word376'][0] == 'UNDETERMINED' and 'mode' in o['word376'][1], o['word376'])
o = mk(['NOMODE'] + good())
check('(zh)(1) no mode line with counts -> UNDETERMINED', o['word376'][0] == 'UNDETERMINED', o['word376'])
o = mk([], started=False)
check('(zh)(1) not entered and lanes 0 -> UNDETERMINED (admission)', o['word376'][0] == 'UNDETERMINED'
      and 'admission' in o['word376'][1], o['word376'])

# ---- positive control (item 369 (d))
o = mk(good(t=(10, 20, 0, 0, 0, 0, 0, 0)))
check('control: box 0 -> UNDETERMINED', o['word376'][0] == 'UNDETERMINED' and 'control' in o['word376'][1], o['word376'])
check('control: box 0 letter -> UNDETERMINED', o['word369'][0] == 'UNDETERMINED', o['word369'])
o = mk(good(t=(0, 0, 0, 0, 30, 40, 0, 0)))
check('control: t0+t1 = 0 -> UNDETERMINED', o['word376'][0] == 'UNDETERMINED' and 'control' in o['word376'][1], o['word376'])
o = mk(good(t=(0, 1, 0, 0, 0, 1, 0, 0)))
check('control edge: t1 = 1 and t5 = 1 -> NOT_REACHED', o['word376'][0] == 'NOT_REACHED', o['word376'])
o = mk(good(t=(5, 0, 0, 0, 0, 0, 3, 0)))
check('control box only t6: letter (4-6) passes -> 369 NOT_REACHED', o['word369'][0] == 'NOT_REACHED', o['word369'])
check('control box only t6: 376 -> NOT_REACHED_ABOVE_T67', o['word376'][0] == 'NOT_REACHED_ABOVE_T67', o['word376'])
check('control box only t6: variant 4-5 -> UNDETERMINED', o['word376_box45'][0] == 'UNDETERMINED', o['word376_box45'])

# ---- (zh)(2) t6+t7, cap trips and dispatch skips
o = mk(good(t=(10, 20, 0, 0, 30, 40, 1, 0)))
check('(zh)(2) t6 > 0 -> NOT_REACHED_ABOVE_T67', o['word376'][0] == 'NOT_REACHED_ABOVE_T67', o['word376'])
check('(zh)(2) letter 369 with t6 -> NOT_REACHED', o['word369'][0] == 'NOT_REACHED', o['word369'])
o = mk(good(t=(10, 20, 0, 0, 30, 40, 0, 2)))
check('(zh)(2) t7 > 0 -> NOT_REACHED_ABOVE_T67', o['word376'][0] == 'NOT_REACHED_ABOVE_T67', o['word376'])
trip = 'BvhLoopCapTrip: trips=+1 total=1 near=+0 near_total=0 max_spent=65536 cap=65536 slot0=1 slot1=0'
o = mk(good(extra_after=[trip]))
check('(zh)(2) BvhLoopCapTrip > 0 -> UNDETERMINED', o['word376'][0] == 'UNDETERMINED' and 'BvhLoopCapTrip' in o['word376'][1],
      o['word376'])
check('(zh)(2) cap trip: letter 369 stays NOT_REACHED', o['word369'][0] == 'NOT_REACHED', o['word369'])
check('(zh)(2) trips_total read', o['trips_total'] == 1 and o['trips_lines'] == 1, (o['trips_total'], o['trips_lines']))
o = mk(good(t=(10, 20, 1, 0, 30, 40, 0, 0), extra_after=[trip]))
check('(zh)(2) cap trip with t2 > 0 -> REACHED', o['word376'][0] == 'REACHED', o['word376'])
o = mk(good(extra_after=['BvhLoopCap: cap=65536 token=\'\' default_slot0=0']))
check('cap line is not a trip', o['word376'][0] == 'NOT_REACHED' and o['cap'] == 65536, (o['word376'], o['cap']))
sk = 'BindFloor: skipped dispatch frame=12 cs=0x%s reason=image-numeric-class' % S9
o = mk(good(extra_after=[sk]))
check('(zh)(2) BVH dispatch skip (BindFloor) -> UNDETERMINED', o['word376'][0] == 'UNDETERMINED' and o['skip_bvh'] == 1,
      o['word376'])
o = mk(good(extra_after=['GraphicsRenderDispatchDirect: skipping CS 0x%s (KYTY_SKIP_CS)' % S0.upper()]))
check('(zh)(2) BVH dispatch skip (skipping CS, upper hex) -> UNDETERMINED', o['word376'][0] == 'UNDETERMINED'
      and o['skip_bvh'] == 1, o['word376'])
o = mk(good(extra_after=['BindFloor: skipped dispatch frame=12 cs=0x1111222233334444 reason=x']))
check('(zh)(2) non-BVH dispatch skip -> NOT_REACHED (reading A)', o['word376'][0] == 'NOT_REACHED' and o['skip_all'] == 1,
      o['word376'])
check('(zh)(2) non-BVH skip: reading B -> UNDETERMINED', o['word376_skipB'][0] == 'UNDETERMINED', o['word376_skipB'])
o = mk(good(extra_after=['GraphicsRenderDispatchDirect: skipping zero-sized dispatch groups=0x1x1 mode=0x00000000 '
                         'shader=0x0000000912345678']))
check('zero-sized skip counted, not attributed', o['skip_zero'] == 1 and o['skip_bvh'] == 0 and o['word376'][0] == 'NOT_REACHED',
      (o['skip_zero'], o['skip_bvh']))
check('AsyncPipelines skipped draw counted, not a dispatch skip',
      mk(good(extra_after=['AsyncPipelines: skipped draw x']))['skipped_draw'] == 1)

# ---- admission
o = mk(good(), started=False)
check('admission: not entered -> UNDETERMINED', o['word376'][0] == 'UNDETERMINED' and not o['admitted'], o['word376'])
o = mk(good(), level='voxel_world', name='lvmismatch')
check('admission: entered the named level', o['admitted'], o['admission'])
o = mk(good(), hold=(10.0, 20.0, 289.9))
check('admission: hold 299.9 s -> FAIL', not o['admitted'] and o['word376'][0] == 'UNDETERMINED', o['admission'])
o = mk(good(), hold=(10.0, 20.0, 290.0))
check('admission: hold 300.0 s edge -> OK', o['admitted'], o['admission'])
o = mk(good(), hold=None)
check('admission: no run json -> FAIL', not o['admitted'], o['admission'])
o = mk(good(), hold_exit=3)
check('admission: game ended in hold -> FAIL', not o['admitted'], o['admission'])
o = mk(good(extra_after=['GpuHangAbort: x']))
check('admission: death marker -> FAIL', not o['admitted'] and o['death'], o['admission'])
o = mk(good(extra_after=['Window 1 minimized']))
check('admission: window minimized -> FAIL', not o['admitted'], o['admission'])
o = mk(good(extra_after=['Window 1 lost keyboard focus']))
check('admission: lost focus only counted, admitted', o['admitted'] and o['window']['lost keyboard focus'] == 1, o['admission'])
o = mk(good(extra_after=['GamePatch: loaded']))
check('admission: GamePatch line -> FAIL', not o['admitted'], o['admission'])
o = mk(good(t=(10, 20, 0, 1, 30, 40, 0, 0)), started=False)
check('admission fail with t3 > 0 -> REACHED (positive count)', o['word376'][0] == 'REACHED', o['word376'])

# ---- (zh)(3) programs by slots, (zh)(5) traps, (zh)(4) t6
o = mk(good(slots={S9: 60, S0: 40}))
check('(zh)(3) programs tested by slots = 2', len(o['programs_tested']) == 2 and len(o['programs_untested']) == 18,
      o['programs_tested'])
check('(zh)(3) ef4 row for 56a15431999c5a2d = 60', o['ef4'][0] == [S9, 60], o['ef4'])
o = mk(good(slots={S9: 100}) + ['DiagBvhNodes: shader=%s bvh_sites=3 trap_sites=1 fallback=0' % S9])
check('Z2 translation lines counted, not read', o['trans_n'] == 1 and len(o['programs_tested']) == 1, o['trans_n'])
o = mk(good(traps=2, trap_lanes=0))
check('(zh)(5) traps > 0 flagged', o['traps_pos'] and o['trap_lanes'] == 0, o['traps_pos'])
check('(zh)(5) traps do not change the word', o['word376'][0] == 'NOT_REACHED', o['word376'])
o = mk(good(t=(10, 20, 0, 0, 30, 40, 5, 0)))
check('(zh)(4) t6 printed', o['t6'] == 5, o['t6'])
check('large counts (u64) parsed', mk(good(t=(10 ** 12, 1, 0, 0, 10 ** 11, 1, 0, 0)))['lanes'] == 10 ** 12 + 10 ** 11 + 2)

# ---- set rows (item 369 (d) letter and 376 (zh)(1)-(5))
def fake(level, w, w369=None, tested=(), t6=0, lanes=1, traps=False, reached=()):
    return dict(level=level, word376=[w, ''], word369=[w369 or ('NOT_REACHED' if w in ('NOT_REACHED', 'NOT_REACHED_ABOVE_T67')
                                                             else w), ''],
                programs_tested=list(tested), t6=t6, lanes=lanes, traps_pos=traps, reached=list(reached))


rows = R.set_rows([fake('a', 'NOT_REACHED'), fake('b', 'NOT_REACHED')])
check('set: all NOT_REACHED', 'SET376 NOT_REACHED on a,b' in rows and 'SET369 NOT_REACHED on a,b' in rows, rows)
rows = R.set_rows([fake('a', 'NOT_REACHED'), fake('b', 'REACHED', reached=['SIZE'])])
check('set: one REACHED', 'SET376 REACHED b:SIZE' in rows and 'SET369 REACHED on b' in rows, rows)
rows = R.set_rows([fake('a', 'NO_BVH', w369='UNDETERMINED', lanes=0), fake('b', 'NO_BVH', w369='UNDETERMINED', lanes=0)])
check('set: empty set -> UNDETERMINED', any(r.startswith('SET376 UNDETERMINED (empty set') for r in rows), rows)
check('set: empty set -> letter UNDETERMINED', 'SET369 UNDETERMINED' in rows, rows)
check('set: S_TRAP with no lanes', any('no scene with lanes > 0' in r for r in rows), rows)
rows = R.set_rows([fake('a', 'NO_BVH', w369='UNDETERMINED', lanes=0), fake('b', 'NOT_REACHED')])
check('set: NO_BVH leaves the set', 'SET376 NOT_REACHED on b' in rows and 'NO_BVH (out of the set) a' in rows, rows)
rows = R.set_rows([fake('a', 'UNDETERMINED'), fake('b', 'NOT_REACHED')])
check('set: one UNDETERMINED in the set', 'SET376 UNDETERMINED (a)' in rows, rows)
rows = R.set_rows([fake('a', 'NOT_REACHED_ABOVE_T67', t6=1), fake('b', 'NOT_REACHED')])
check('set: above t67', any(r.startswith('SET376 NOT_REACHED_ABOVE_T67 on a,b (t6+t7 > 0 on a)') for r in rows), rows)
check('set: t6 row', 't6 > 0 (item 376 (zh)(4)) on a' in rows, rows)
rows = R.set_rows([fake('a', 'NOT_REACHED', tested=[S9]), fake('b', 'NOT_REACHED', tested=[S9, S0], traps=True)])
check('set: programs union 2, untested 18', any('programs with lanes > 0 (item 376 (zh)(3)) 2:' in r and 'untested 18' in r
                                                 for r in rows), rows)
check('set: traps > 0 on b', 'S_TRAP (item 376 (zh)(5)): traps > 0 on b' in rows, rows)
rows = R.set_rows([fake('a', 'NOT_REACHED'), fake('b', 'NOT_REACHED')])
check('set: traps 0 on all with lanes', 'S_TRAP (item 376 (zh)(5)): traps = 0 on all scenes with lanes > 0: a,b' in rows, rows)

# ---- the CLI in strict cp1250 without PYTHONIOENCODING (item 175 (v)), and ASCII only
lp = os.path.join(TMP, 'cli.txt')
with open(lp, 'wb') as f:
    f.write(('\n'.join([MODE, 'GuestOut: Level has started: enemy_final'] + good(t=(10, 20, 0, 0, 30, 40, 1, 0), traps=1)) +
             '\n').encode())
jp = os.path.join(TMP, 'cli.json')
json.dump(dict(attempts=[dict(started_s=1.0, stable_s=2.0, hold_s=330.0, hold_exit=None)]), open(jp, 'w'))
env = {k: v for k, v in os.environ.items() if k != 'PYTHONIOENCODING'}
env['PYTHONIOENCODING'] = 'cp1250:strict'
outj = os.path.join(TMP, 'cli.read.json')
p = subprocess.run([sys.executable, os.path.join(HERE, 'f11f_read.py'), 'd11_ef', '--log', lp, '--json', jp, '--out', outj],
                   capture_output=True, env=env)
check('CLI cp1250 strict rc 0', p.returncode == 0, p.stderr[-300:])
check('CLI output ASCII only', all(b < 128 for b in p.stdout), '')
check('CLI WORD376 line', b'WORD376 NOT_REACHED_ABOVE_T67' in p.stdout, p.stdout[-400:])
check('CLI traps value not cited', b'traps>0 yes (value not cited, Z1)' in p.stdout, '')
p2 = subprocess.run([sys.executable, os.path.join(HERE, 'f11f_read.py'), '--set', outj], capture_output=True, env=env)
check('CLI --set rc 0, ASCII', p2.returncode == 0 and all(b < 128 for b in p2.stdout), p2.stderr[-300:])
check('CLI --set row', b'SET376 NOT_REACHED_ABOVE_T67 on enemy_final' in p2.stdout, p2.stdout)

print('checks %d fails %d' % (N[0], len(FAILS)))
if FAILS:
    print('FAILED: ' + ', '.join(FAILS))
    sys.exit(1)
print('ALL OK')

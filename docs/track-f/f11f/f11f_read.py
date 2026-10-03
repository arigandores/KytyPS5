"""F11f (HPP-468, ROADMAP s122 items 369 (d), 376 (e)-(zh), 381 (b), 384 (v)-(d)): the reader of one tag of KYTY_DIAG_BVHNODES=1.

    python f11f_read.py <tag> [--log <path>] [--json <run json>] [--rundir <dir>] [--out <read.json>]
    python f11f_read.py --set <read.json> [<read.json> ...]        the set rows of item 376 (zh)(1)-(5) (reading - F11g)
    python f11f_read.py --check-seal                                sha256 of this file against the seal copy

ASCII output only.  The log is streamed in binary mode.  Line forms (F11d report section 6, c01451b0 faultManager.cpp:67, :303, :325):
    DiagBvhNodes: mode=1 words=64 tail_bytes=320
    DiagBvhNodes: shader=<hash16> bvh_sites=<n> trap_sites=<m> fallback=<0|1>
    DiagBvhNodes: lanes=.. t0=.. .. t7=.. size_viol=.. size_off=.. node64=.. over_max=.. b_tri=a/b/c/d b_box=a/b/c/d b_t7=a/b/c/d
                  traps=.. trap_lanes=.. groups=.. max_step=..
    DiagBvhNodes: slots[ <hash16>=<n>]* other=<n>
    BvhLoopCapTrip: trips=+<d> total=<n> near=+.. near_total=.. max_spent=.. cap=.. slot0=.. slot1=..
Dispatch skip lines (c01451b0 renderCompute.cpp:525, :939, :986):
    GraphicsRenderDispatchDirect: skipping CS 0x<hash16> (KYTY_SKIP_CS)
    GraphicsRenderDispatchDirect: skipping zero-sized dispatch groups=.. mode=.. shader=0x<ADDRESS>     (no program hash)
    BindFloor: skipped dispatch frame=.. cs=0x<hash16> reason=..

Members (the seal docs/track-f/f11f.md names each):
  RC2 (item 384 (g)) on EVERY 'lanes=' line: lanes = t0+..+t7; size_viol = sum of the 12 bucket fields; size_viol + node64 <= lanes;
      slots + other = lanes (the first 'slots' line after it and before the next 'lanes' line); max_step < 2^31.  Any failure,
      an unparsable 'lanes=' line or a missing 'slots' line -> the tag word UNDETERMINED (row 'identities FAIL').
  RC1 (item 384 (v)): the size violation of the rule = the LAST (fourth) field of b_tri, b_box, b_t7, summed over the three classes;
      the bucket number is not read; fields 1-3 > 0 only make the report row 'within twice the unit' (item 376 (e)).
  The rule reads the LAST 'lanes=' line and its 'slots' line.
Words (ASCII; the seal maps them to the Russian words of the items):
  REACHED            t2+t3 > 0 or the size violation > 0 (item 369 (d): 'defect reachable'; kinds TYPES23 / SIZE)
  NOT_REACHED        0 and 0 with the positive control in the tag (box visits > 0 and t0+t1 > 0)
  NOT_REACHED_ABOVE_T67  (item 376 (zh)(2)) as NOT_REACHED with t6+t7 > 0: 'not reached above the nodes of types 6-7 [c]; below - undetermined'
  NO_BVH             (item 376 (zh)(1)) lanes = 0 with the mode line: the scene leaves the set of the rule
  UNDETERMINED       otherwise (reason named)
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = 'C:/kyty/f287/f11f'
SEAL_COPY = ROOT + '/pred/f11f_seal.md'
SEAL_SHA_FILE = ROOT + '/pred/f11f_seal.sha256'

# the 20 BVH programs of eboot.bin (c01451b0 LoopCap DiagBvhSlotHash table, slots 0..19)
SLOTS = ['092754e7ae8bac9a', '0af122d5ac62c4c5', '1f16e50eea0c89e3', '1f3219e5899a66f2',
         '380bb9d636390bae', '3d27502d0a809c72', '503d7f066a496c3c', '5323c4ef4f785055',
         '559a0fa9def7a691', '56a15431999c5a2d', '7ede18ae55120a48', '8175abf0855222db',
         '99012529f9a27ba3', 'a763fb769f3167ec', 'b76e569142635733', 'cd94166bf3f2bb81',
         'd234cf2781dabb34', 'ea8e2d64dfe34ed9', 'f88d0f630ac5b35d', 'ff8ee744ffa4dcdc']
# the 4 programs of the floor lighting of enemy_final (item 376 (a), F11a2): rows by program in d11_ef
EF4 = ['56a15431999c5a2d', 'ea8e2d64dfe34ed9', '5323c4ef4f785055', 'cd94166bf3f2bb81']

KEY = b'DiagBvhNodes: '
RE_MODE = re.compile(rb'DiagBvhNodes: mode=(\d+) words=(\d+) tail_bytes=(\d+)')
RE_TRANS = re.compile(rb'DiagBvhNodes: shader=([0-9a-f]{16}) bvh_sites=(\d+) trap_sites=(\d+) fallback=([01])')
RE_LANES = re.compile(
    rb'DiagBvhNodes: lanes=(\d+) t0=(\d+) t1=(\d+) t2=(\d+) t3=(\d+) t4=(\d+) t5=(\d+) t6=(\d+) t7=(\d+) size_viol=(\d+)'
    rb' size_off=(\d+) node64=(\d+) over_max=(\d+) b_tri=(\d+)/(\d+)/(\d+)/(\d+) b_box=(\d+)/(\d+)/(\d+)/(\d+)'
    rb' b_t7=(\d+)/(\d+)/(\d+)/(\d+) traps=(\d+) trap_lanes=(\d+) groups=(\d+) max_step=(\d+)\s*$')
LANES_NAMES = ['lanes', 't0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 'size_viol', 'size_off', 'node64', 'over_max',
               'b_tri', 'b_box', 'b_t7', 'traps', 'trap_lanes', 'groups', 'max_step']
RE_SLOTS = re.compile(rb'DiagBvhNodes: slots((?: [0-9a-f]{16}=\d+)*) other=(\d+)\s*$')
RE_SLOT1 = re.compile(rb' ([0-9a-f]{16})=(\d+)')
RE_TRIP = re.compile(rb'BvhLoopCapTrip: trips=\+(\d+) total=(\d+)')
RE_CAP = re.compile(rb'BvhLoopCap: cap=(\d+)')
RE_SKIP_CS = re.compile(rb'GraphicsRenderDispatchDirect: skipping CS 0x([0-9a-fA-F]{16})')
RE_SKIP_ZERO = re.compile(rb'GraphicsRenderDispatchDirect: skipping zero-sized dispatch')
RE_SKIP_FLOOR = re.compile(rb'BindFloor: skipped dispatch frame=-?\d+ cs=0x([0-9a-fA-F]{16})')
RE_STARTED = re.compile(rb'GuestOut: Level has started: (\S+)')
DEATH = (b'GpuHangAbort:', b'ErrorDeviceLost', b'Unhandled exception:')
WINDOW = (b'minimized', b'restored', b'resized', b'size changed', b'lost keyboard focus')
MAX_STEP_LIMIT = 1 << 31
HOLD_MIN_S = 300.0


def parse_lanes(line):
    """dict of the fields of one 'lanes=' line, or None when the line does not have the full form."""
    i = line.find(KEY)
    m = RE_LANES.search(line[i:]) if i >= 0 else None
    if not m:
        return None
    v = [int(x) for x in m.groups()]
    d = dict(zip(LANES_NAMES[:13], v[:13]))
    d['b_tri'] = v[13:17]
    d['b_box'] = v[17:21]
    d['b_t7'] = v[21:25]
    d['traps'], d['trap_lanes'], d['groups'], d['max_step'] = v[25:29]
    return d


def parse_slots(line):
    i = line.find(KEY)
    m = RE_SLOTS.search(line[i:]) if i >= 0 else None
    if not m:
        return None
    slots = {h.decode(): int(n) for h, n in RE_SLOT1.findall(m.group(1))}
    return {'slots': slots, 'other': int(m.group(2))}


def identities(d, s):
    """RC2 of item 384 (g): the list of failed identities of one 'lanes=' line with its 'slots' line (empty = all hold)."""
    bad = []
    if d is None:
        return ['unparsable lanes line']
    if d['lanes'] != sum(d['t%d' % k] for k in range(8)):
        bad.append('lanes != t0+..+t7')
    if d['size_viol'] != sum(d['b_tri']) + sum(d['b_box']) + sum(d['b_t7']):
        bad.append('size_viol != sum of 12 bucket fields')
    if d['size_viol'] + d['node64'] > d['lanes']:
        bad.append('size_viol + node64 > lanes')
    if s is None:
        bad.append('no slots line')
    elif sum(s['slots'].values()) + s['other'] != d['lanes']:
        bad.append('slots + other != lanes')
    if d['max_step'] >= MAX_STEP_LIMIT:
        bad.append('max_step >= 2^31')
    return bad


def scan(path):
    r = dict(mode_lines=[], trans=[], lanes_lines=0, ident_fail=[], last=None, last_slots=None, trips_lines=0, trips_total=0,
             trips_sum=0, cap=None, skip_cs=[], skip_zero=0, skip_floor=[], started=[], death=[], window={}, vk_err=0,
             asserts=0, skipped_draw=0, game_patch=0, recovering=0, lines=0, git=None)
    for w in WINDOW:
        r['window'][w.decode()] = 0
    h = hashlib.sha256()
    pending = None  # (index, dict) of the last 'lanes=' line waiting for its 'slots' line
    with open(path, 'rb') as f:
        for line in f:
            h.update(line)
            r['lines'] += 1
            if KEY in line:
                tail = line[line.find(KEY):]
                if tail.startswith(b'DiagBvhNodes: lanes='):
                    if pending is not None:
                        bad = identities(pending[1], None)
                        r['ident_fail'].append((pending[0], bad))
                    r['lanes_lines'] += 1
                    d = parse_lanes(line)
                    if d is None:
                        r['ident_fail'].append((r['lanes_lines'], ['unparsable lanes line']))
                        r['last'] = None
                        r['last_slots'] = None
                        pending = None
                    else:
                        pending = (r['lanes_lines'], d)
                        r['last'] = d
                        r['last_slots'] = None
                    continue
                if tail.startswith(b'DiagBvhNodes: slots'):
                    s = parse_slots(line)
                    if pending is not None:
                        bad = identities(pending[1], s)
                        if bad:
                            r['ident_fail'].append((pending[0], bad))
                        r['last_slots'] = s
                        pending = None
                    continue
                m = RE_MODE.search(tail)
                if m:
                    r['mode_lines'].append([int(x) for x in m.groups()])
                    continue
                m = RE_TRANS.search(tail)
                if m:
                    r['trans'].append([m.group(1).decode(), int(m.group(2)), int(m.group(3)), int(m.group(4))])
                    continue
                continue
            if b'BvhLoopCap' in line:
                m = RE_TRIP.search(line)
                if m:
                    r['trips_lines'] += 1
                    r['trips_sum'] += int(m.group(1))
                    r['trips_total'] = max(r['trips_total'], int(m.group(2)))
                    continue
                m = RE_CAP.search(line)
                if m and r['cap'] is None:
                    r['cap'] = int(m.group(1))
                continue
            if b'skipping' in line or b'skipped' in line:
                m = RE_SKIP_CS.search(line)
                if m:
                    r['skip_cs'].append(m.group(1).decode().lower())
                elif RE_SKIP_ZERO.search(line):
                    r['skip_zero'] += 1
                else:
                    m = RE_SKIP_FLOOR.search(line)
                    if m:
                        r['skip_floor'].append(m.group(1).decode().lower())
                if b'AsyncPipelines: skipped draw' in line:
                    r['skipped_draw'] += 1
            if b'Level has started' in line:
                m = RE_STARTED.search(line)
                if m:
                    r['started'].append(m.group(1).decode('ascii', 'replace'))
            for dm in DEATH:
                if dm in line and len(r['death']) < 5:
                    r['death'].append(line[:160].decode('ascii', 'replace').strip())
            if b'Window ' in line:
                for w in WINDOW:
                    if w in line:
                        r['window'][w.decode()] += 1
            if b'Recovering Vulkan swapchain' in line:
                r['recovering'] += 1
            if b'[Vulkan][E]' in line:
                r['vk_err'] += 1
            if b'ASSERT:' in line:
                r['asserts'] += 1
            if b'GamePatch:' in line:
                r['game_patch'] += 1
            if r['git'] is None and b'git = ' in line:
                r['git'] = line[line.find(b'git = '):][:80].decode('ascii', 'replace').strip()
    if pending is not None:
        r['ident_fail'].append((pending[0], identities(pending[1], None)))
    r['sha256'] = h.hexdigest()
    return r


def classify(r, level, run):
    """The words of one tag: (letter of item 369 (d), word of items 376 (e)-(zh)) and the rows."""
    rows = []
    d = r['last']
    s = r['last_slots']
    slots = s['slots'] if s else {}
    bvh_skip = [x for x in r['skip_cs'] + r['skip_floor'] if x in SLOTS]
    all_skip = len(r['skip_cs']) + len(r['skip_floor']) + r['skip_zero']
    # admission (scene entered, held >= 300 s after the first scene frame, no death marker, no window event, no game patch)
    adm = []
    if level not in r['started']:
        adm.append('not entered (no "Level has started: %s")' % level)
    hold = None
    if run is not None:
        try:
            hold = float(run['stable_s']) - float(run['started_s']) + float(run['hold_s'])
        except (KeyError, TypeError, ValueError):
            hold = None
        if run.get('hold_exit') is not None:
            adm.append('the game ended inside the hold (exit %s)' % run.get('hold_exit'))
    if hold is None or hold < HOLD_MIN_S:
        adm.append('hold after the first scene frame %s < %d s' % ('?' if hold is None else '%.1f' % hold, HOLD_MIN_S))
    if r['death']:
        adm.append('death marker')
    if r['window'].get('minimized', 0) or r['recovering']:
        adm.append('window event')
    if r['game_patch']:
        adm.append('GamePatch line (KYTY_GAME_PATCH must not be set)')
    admitted = not adm
    reached = []
    viol = None
    if d is not None:
        t23 = d['t2'] + d['t3']
        viol = d['b_tri'][3] + d['b_box'][3] + d['b_t7'][3]   # RC1: the last (fourth) field of each class
        if t23 > 0:
            reached.append('TYPES23')
        if viol > 0:
            reached.append('SIZE')
    ctl_box = d is not None and (d['t4'] + d['t5'] + d['t6']) > 0        # box class 4-6 (RC5 letter)
    ctl_box45 = d is not None and (d['t4'] + d['t5']) > 0               # variant: 4-5 (t6 = 'no children' at the emulator)
    ctl_tri = d is not None and (d['t0'] + d['t1']) > 0
    lanes = d['lanes'] if d is not None else 0

    def word(letter, box_ok):
        if not r['mode_lines']:
            return 'UNDETERMINED', 'no mode line (KYTY_DIAG_BVHNODES=1 not in effect)'
        if r['ident_fail']:
            return 'UNDETERMINED', 'identities FAIL (RC2)'
        if reached:
            return 'REACHED', '+'.join(reached)
        if not admitted:
            return 'UNDETERMINED', 'admission: ' + '; '.join(adm)
        if not letter:
            if lanes == 0:
                return 'NO_BVH', 'lanes = 0 with the mode line (item 376 (zh)(1))'
            if r['trips_total'] > 0 or r['trips_sum'] > 0 or r['trips_lines'] > 0:
                return 'UNDETERMINED', 'BvhLoopCapTrip total %d (item 376 (zh)(2))' % r['trips_total']
            if bvh_skip:
                return 'UNDETERMINED', 'dispatch skip lines of BVH programs %d (item 376 (zh)(2))' % len(bvh_skip)
        if not (box_ok and ctl_tri):
            return 'UNDETERMINED', 'positive control FAIL (box %s, t0+t1 %s)' % (box_ok, ctl_tri)
        if not letter and d['t6'] + d['t7'] > 0:
            return 'NOT_REACHED_ABOVE_T67', 't6+t7 = %d (item 376 (zh)(2))' % (d['t6'] + d['t7'])
        return 'NOT_REACHED', '0 and 0, control ok'

    w369 = word(True, ctl_box)
    w376 = word(False, ctl_box)
    w376v = word(False, ctl_box45)
    # reading B of the skip member: every dispatch skip line (also zero-sized, no program hash)
    wB = w376
    if w376[0] in ('NOT_REACHED', 'NOT_REACHED_ABOVE_T67') and all_skip > 0:
        wB = ('UNDETERMINED', 'any dispatch skip line %d (reading B)' % all_skip)
    tested = [h for h in SLOTS if slots.get(h, 0) > 0]
    out = dict(level=level, admitted=admitted, admission=adm, hold_after_start_s=hold, lanes=lanes, last=d, last_slots=s,
               size_violation=viol, within_twice=None, reached=reached, control_box_4_6=ctl_box, control_box_4_5=ctl_box45,
               control_t01=ctl_tri, ident_fail=r['ident_fail'][:10], ident_fail_n=len(r['ident_fail']),
               lanes_lines=r['lanes_lines'], mode_lines=r['mode_lines'], trans_n=len(r['trans']),
               trans_fallback=sum(1 for t in r['trans'] if t[3] == 1), trans=r['trans'][:40],
               programs_tested=tested, programs_untested=[h for h in SLOTS if h not in tested],
               ef4=[[h, slots.get(h, 0)] for h in EF4], other=(s['other'] if s else None),
               traps_pos=(d is not None and d['traps'] > 0), trap_lanes=(d['trap_lanes'] if d else None),
               t6=(d['t6'] if d else None), t7=(d['t7'] if d else None),
               trips_lines=r['trips_lines'], trips_total=r['trips_total'], trips_sum=r['trips_sum'], cap=r['cap'],
               skip_bvh=len(bvh_skip), skip_all=all_skip, skip_cs=len(r['skip_cs']), skip_zero=r['skip_zero'],
               skip_floor=len(r['skip_floor']), skipped_draw=r['skipped_draw'], vk_err=r['vk_err'], asserts=r['asserts'],
               game_patch=r['game_patch'], window=r['window'], recovering=r['recovering'], death=r['death'],
               log_lines=r['lines'], log_sha256=r['sha256'], git=r['git'],
               word369=list(w369), word376=list(w376), word376_box45=list(w376v), word376_skipB=list(wB))
    if d is not None:
        out['within_twice'] = [d['b_tri'][1] + d['b_tri'][2], d['b_box'][1] + d['b_box'][2], d['b_t7'][1] + d['b_t7'][2],
                               d['b_tri'][0], d['b_box'][0], d['b_t7'][0]]
    return out


def print_tag(tag, o):
    p = print
    p('tag %s level %s log_lines %d log_sha256 %s' % (tag, o['level'], o['log_lines'], o['log_sha256']))
    p('admission: %s%s; hold after the first scene frame %s s' % ('OK' if o['admitted'] else 'FAIL',
      '' if o['admitted'] else ' (' + '; '.join(o['admission']) + ')',
      'n/a' if o['hold_after_start_s'] is None else '%.1f' % o['hold_after_start_s']))
    p('mode lines %d %s; lanes lines %d; identities (RC2) %s' % (len(o['mode_lines']), o['mode_lines'][:1], o['lanes_lines'],
      'OK' if not o['ident_fail_n'] else 'FAIL %d: %s' % (o['ident_fail_n'], o['ident_fail'][:3])))
    d = o['last']
    if d is None:
        p('last DiagBvhNodes lanes line: none')
    else:
        p('last: lanes=%d t0=%d t1=%d t2=%d t3=%d t4=%d t5=%d t6=%d t7=%d size_viol=%d size_off=%d node64=%d over_max=%d max_step=%d'
          % tuple([d[k] for k in ('lanes', 't0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 'size_viol', 'size_off', 'node64',
                                  'over_max', 'max_step')]))
        p('buckets: b_tri=%s b_box=%s b_t7=%s' % ('/'.join(map(str, d['b_tri'])), '/'.join(map(str, d['b_box'])),
                                                   '/'.join(map(str, d['b_t7']))))
        p('size violation (RC1: last field, idx > 2*size64+1): tri %d box %d t7 %d sum %d; fields 2-3 (within twice the unit) '
          'tri %d box %d t7 %d; field 1 tri %d box %d t7 %d' % ((d['b_tri'][3], d['b_box'][3], d['b_t7'][3], o['size_violation'])
                                                                + tuple(o['within_twice'])))
        p('traps>0 %s (value not cited, Z1); trap_lanes %d; groups not cited (Z1)' % ('yes' if d['traps'] > 0 else 'no',
                                                                                     d['trap_lanes']))
    s = o['last_slots']
    p('slots: %s other=%s' % ('none' if s is None else ' '.join('%s=%d' % kv for kv in sorted(s['slots'].items())),
                              'n/a' if s is None else s['other']))
    p('programs with lanes > 0 (by slots, Z2): %d %s; untested of 20: %d' % (len(o['programs_tested']),
      ','.join(o['programs_tested']), len(o['programs_untested'])))
    p('enemy_final lighting programs (item 376 (a)): %s' % ' '.join('%s=%d' % (h, n) for h, n in o['ef4']))
    p('translation lines %d (fallback=1: %d) - not read by the rule (Z2)' % (o['trans_n'], o['trans_fallback']))
    p('BvhLoopCapTrip: lines %d total %d (sum of +trips %d); cap %s' % (o['trips_lines'], o['trips_total'], o['trips_sum'], o['cap']))
    p('dispatch skip lines: BVH programs %d; all %d (skipping CS %d, zero-sized %d, BindFloor %d)' % (o['skip_bvh'], o['skip_all'],
      o['skip_cs'], o['skip_zero'], o['skip_floor']))
    p('data: AsyncPipelines skipped draw %d; [Vulkan][E] %d; ASSERT %d; GamePatch %d; window %s; Recovering %d; death %d; %s'
      % (o['skipped_draw'], o['vk_err'], o['asserts'], o['game_patch'],
         ','.join('%s=%d' % kv for kv in sorted(o['window'].items())), o['recovering'], len(o['death']), o['git']))
    p('t6 %s t7 %s (item 376 (zh)(4): t6 > 0 -> register row by F11g, 0 -> report row)' % (o['t6'], o['t7']))
    p('WORD369 %s (%s)' % tuple(o['word369']))
    p('WORD376 %s (%s)' % tuple(o['word376']))
    if o['word376_box45'] != o['word376']:
        p('WORD376 box 4-5 (variant of the executor) %s (%s) DIFFERS' % tuple(o['word376_box45']))
    if o['word376_skipB'] != o['word376']:
        p('WORD376 skip reading B (variant of the executor) %s (%s) DIFFERS' % tuple(o['word376_skipB']))


def set_rows(reads):
    """Item 369 (d) letter and items 376 (zh)(1)-(5) over the tags (the reading itself is F11g's)."""
    out = []
    w369 = [(o['level'], o['word369'][0]) for o in reads]
    if any(w == 'REACHED' for _, w in w369):
        out.append('SET369 REACHED on %s' % ','.join(l for l, w in w369 if w == 'REACHED'))
    elif w369 and all(w == 'NOT_REACHED' for _, w in w369):
        out.append('SET369 NOT_REACHED on %s' % ','.join(l for l, _ in w369))
    else:
        out.append('SET369 UNDETERMINED')
    w = [(o['level'], o['word376'][0], o) for o in reads]
    reached = [(l, o['reached']) for l, x, o in w if x == 'REACHED']
    if reached:
        out.append('SET376 REACHED %s' % ' '.join('%s:%s' % (l, '+'.join(k)) for l, k in reached))
    else:
        S = [(l, x) for l, x, _ in w if x != 'NO_BVH']
        if not S:
            out.append('SET376 UNDETERMINED (empty set, item 376 (zh)(1))')
        elif any(x == 'UNDETERMINED' for _, x in S):
            out.append('SET376 UNDETERMINED (%s)' % ','.join(l for l, x in S if x == 'UNDETERMINED'))
        elif all(x == 'NOT_REACHED' for _, x in S):
            out.append('SET376 NOT_REACHED on %s' % ','.join(l for l, _ in S))
        else:
            out.append('SET376 NOT_REACHED_ABOVE_T67 on %s (t6+t7 > 0 on %s); below - UNDETERMINED'
                       % (','.join(l for l, _ in S), ','.join(l for l, x in S if x == 'NOT_REACHED_ABOVE_T67')))
    nob = [o['level'] for o in reads if o['word376'][0] == 'NO_BVH']
    out.append('NO_BVH (out of the set) %s' % (','.join(nob) if nob else 'none'))
    tested = sorted(set(h for o in reads for h in o['programs_tested']))
    out.append('programs with lanes > 0 (item 376 (zh)(3)) %d: %s; untested %d' % (len(tested), ','.join(tested),
                                                                                    len(SLOTS) - len(tested)))
    t6 = [o['level'] for o in reads if (o['t6'] or 0) > 0]
    out.append('t6 > 0 (item 376 (zh)(4)) on %s' % (','.join(t6) if t6 else 'none'))
    withl = [o for o in reads if o['lanes'] > 0]
    tp = [o['level'] for o in withl if o['traps_pos']]
    if not withl:
        out.append('S_TRAP (item 376 (zh)(5)): no scene with lanes > 0')
    elif tp:
        out.append('S_TRAP (item 376 (zh)(5)): traps > 0 on %s' % ','.join(tp))
    else:
        out.append('S_TRAP (item 376 (zh)(5)): traps = 0 on all scenes with lanes > 0: %s' % ','.join(o['level'] for o in withl))
    return out


def sha_of(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


LEVELS = {'d11_sg': 'underwater_aerial_garden', 'd11_ef': 'enemy_final', 'd11_vw': 'voxel_world',
          'd11_bh': 'big_hand_pirate_island'}


def main(argv):
    if argv[:1] == ['--check-seal']:
        want = open(SEAL_SHA_FILE).read().split()[0]
        got = sha_of(SEAL_COPY)
        me = sha_of(os.path.abspath(__file__))
        print('seal %s sha256 %s want %s %s; reader sha256 %s' % (SEAL_COPY, got, want, 'PASS' if got == want else 'FAIL', me))
        return 0 if got == want else 1
    if argv[:1] == ['--set']:
        reads = [json.load(open(p)) for p in argv[1:]]
        for row in set_rows(reads):
            print(row)
        return 0
    tag = argv[0]
    args = dict(zip(argv[1::2], argv[2::2]))
    rundir = args.get('--rundir', ROOT + '/runs/' + tag)
    log = args.get('--log', ROOT + '/log_%s.txt' % tag)
    runj = args.get('--json', ROOT + '/%s.json' % tag)
    level = args.get('--level', LEVELS.get(tag, ''))
    run = None
    if os.path.isfile(runj):
        j = json.load(open(runj))
        att = j.get('attempts') or []
        run = att[-1] if att else j
    print('reader f11f_read.py sha256 %s' % sha_of(os.path.abspath(__file__)))
    o = classify(scan(log), level, run)
    print_tag(tag, o)
    o['tag'] = tag
    if '--out' in args:
        with open(args['--out'], 'w') as f:
            json.dump(o, f, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

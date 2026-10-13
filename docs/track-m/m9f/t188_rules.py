"""Track M link M9f (HPP-871; ROADMAP s122 item 785 (b)-(g), 788 (g), 789 (g), (d), 791 (v); design edition 2
docs/track-m/m9a2/design_m9a2.md sections 4.4-4.6, 5.3, 7, 8.3): the T188 / T109 rules of ONE tag of the series 1 - pure functions
(no files except scan()), used by the reader m9f_read.py and by the fixtures test_m9f.py.  Rows and stop members only, NO VERDICT
(the reading is M9g, the lead).  ASCII only.

LINES (code of the M9d3 binary feb55b54 = main 2042c697, src/libs/diagT188.cpp):
  'T188: mode=<m> cls=<all|n> k=<K>'                                 once per process (PrintModeLine)
  'T188Stat: when=<periodic|exit> <70 fields of STAT in this order>'  PrintStat
  'T188Img: when=exit key=<16 hex> fmt= tile= w= h= levels= layers= cmp= samples= usage= vol= <27 fields of CLS>'  PrintImg
  'T188Img: when=exit key=other <27 fields of CLS>'                   the sum of the rows after 256
  'T109Stat: when=<w> d32= zx_d32= zx_narrow= bias_d32= bias_narrow= ovr_w= ovr_vpc= zx_narrow_vi= bias_narrow_vi= narrow_cd='
A line with the prefix that does not parse is 'unparsable' (a code interference at the exit, a row before it).

STOP MEMBERS (section 7 (1), item 785 (v)(5): a violation stops the series - code interference, not data):
  Z  invariants 0 on EVERY parsed T188Stat line: part_unk, ep_bad, lock_bad, tint_bad, tint_rb0_bad, tint_rb1_bad;
  N  zeros by the mode: the mode line is exactly 'mode=2 cls=all k=4' (plan); cls=all => tint_skip_cls = 0 (I7, class outside the
     list impossible); mode 2 => T188Stat / T188Img / T109Stat present;
  E  exactly one parsed T188Stat when=exit line, >= 1 T188Img when=exit line (key=other at most once), exactly one T109Stat when=exit
     line, 0 unparsable lines of the three prefixes;
  I1-I4, I6, I8 on the exit line (and the T188Img rows for I3 / I6); I5 against the M5W2Stat total of the tag (when=exit);
  I9 on the T109Stat exit line.
ROWS (no stop): the exit fields, the T188Img table, the class choice of item 785 (v)(2), the readback per class, the T109 rows of item
  785 (g) with 789 (g) and 791 (v) (difference zx_narrow - zx_narrow_vi per line), the field 'open' only at ep_bad = 0 (item 788 (g) N2).
"""
import re

STAT = ('part', 'part_st', 'part_fill', 'part_copy', 'part_unk', 'part_off', 'part_synced', 'part_dlmem', 'reopen', 'ep_new',
        'ep_prop', 'prop_merge', 'w_mipal', 'w_inmip', 'w_other', 'w_bytes', 'img_bytes', 'img_bytes_unsync',
        'img_full_unsync', 'in_pass', 'in_pass_unsync', 'cl_smp', 'cl_rt', 'cl_rtclr', 'cl_dt', 'cl_sto', 'cl_clrop',
        'cl_oth', 'cl_vo', 'cl_cover', 'cl_cmp', 'cl_msaa', 'cl_free', 'cl_commit', 'cl_copydst', 'cl_skip', 'cl_none',
        'open', 'ep_pend', 'pend_done', 'pend_drop', 'pend_free', 'pend_open', 'lost_bytes', 'lost_pend_bytes', 'w_ovf',
        'sync_full', 'sync_part', 'dl_mem', 'ep_bad', 'lock_bad', 'tint_ep', 'tint_mips', 'tint_bytes', 'tint_part_mips',
        'tint_skip_fmt', 'tint_skip_vol', 'tint_skip_cls', 'tint_skip_cpu', 'tint_skip_ovf', 'tint_bad', 'tint_rb_req',
        'tint_rb0_ok', 'tint_rb0_bad', 'tint_rb0_none', 'tint_rb0_nofmt', 'tint_rb1_ok', 'tint_rb1_over', 'tint_rb1_bad',
        'tint_rb1_none')
CLS = ('ev', 'ev_st', 'ev_fill', 'ev_copy', 'ev_off', 'ev_synced', 'ev_dlmem', 'ep_new', 'ep_prop', 'cl_smp', 'cl_rt',
       'cl_rtclr', 'cl_vo', 'cl_commit', 'cl_free', 'lost_bytes', 'lost_pend_bytes', 'img_bytes', 'tint_ep', 'tint_mips',
       'tint_bytes', 'tint_skip', 'tint_rb0_ok', 'tint_rb0_bad', 'tint_rb1_ok', 'tint_rb1_over', 'tint_rb1_bad')
HEAD = ('fmt', 'tile', 'w', 'h', 'levels', 'layers', 'cmp', 'samples', 'usage', 'vol')
T109 = ('d32', 'zx_d32', 'zx_narrow', 'bias_d32', 'bias_narrow', 'ovr_w', 'ovr_vpc', 'zx_narrow_vi', 'bias_narrow_vi', 'narrow_cd')
INVARIANTS = ('part_unk', 'ep_bad', 'lock_bad', 'tint_bad', 'tint_rb0_bad', 'tint_rb1_bad')
CL_ALL = ('cl_smp', 'cl_rt', 'cl_rtclr', 'cl_dt', 'cl_sto', 'cl_clrop', 'cl_oth', 'cl_vo', 'cl_cover', 'cl_cmp', 'cl_msaa', 'cl_free',
          'cl_commit', 'cl_copydst', 'cl_skip')
CL_S3 = ('cl_smp', 'cl_rt', 'cl_rtclr', 'cl_dt', 'cl_sto', 'cl_clrop', 'cl_oth', 'cl_vo')
SKIPS = ('tint_skip_fmt', 'tint_skip_vol', 'tint_skip_cls', 'tint_skip_cpu', 'tint_skip_ovf')
# I3: class field -> the global field(s) whose sum it must equal (section 4.6 I3, 4.5: tint_skip = the sum of tint_skip_*)
I3_MAP = (('ev', ('part',)), ('ev_st', ('part_st',)), ('ev_fill', ('part_fill',)), ('ev_copy', ('part_copy',)), ('ev_off', ('part_off',)),
          ('ev_synced', ('part_synced',)), ('ev_dlmem', ('part_dlmem',)), ('ep_new', ('ep_new',)), ('ep_prop', ('ep_prop',)),
          ('cl_smp', ('cl_smp',)), ('cl_rt', ('cl_rt',)), ('cl_rtclr', ('cl_rtclr',)), ('cl_vo', ('cl_vo',)),
          ('cl_commit', ('cl_commit',)), ('cl_free', ('cl_free',)), ('lost_bytes', ('lost_bytes',)),
          ('lost_pend_bytes', ('lost_pend_bytes',)), ('img_bytes', ('img_bytes',)), ('tint_ep', ('tint_ep',)),
          ('tint_mips', ('tint_mips',)), ('tint_bytes', ('tint_bytes',)), ('tint_skip', SKIPS), ('tint_rb0_ok', ('tint_rb0_ok',)),
          ('tint_rb0_bad', ('tint_rb0_bad',)), ('tint_rb1_ok', ('tint_rb1_ok',)), ('tint_rb1_over', ('tint_rb1_over',)),
          ('tint_rb1_bad', ('tint_rb1_bad',)))
PLAN_MODE = (2, 'all', 4)
SHARE = 0.8          # item 785 (v)(2)
MAX_CLASSES = 2      # item 785 (v)(2)
COVER_MIN = 0.5      # section 7 (3)(v), item 785 (v)(3)

RX_MODE = re.compile(rb'T188: mode=(\d+) cls=([0-9a-z]+) k=(\d+)\s*$')
RX_STAT = re.compile(rb'T188Stat: when=([a-z]+) ' + b' '.join(f.encode() + rb'=(\d+)' for f in STAT) + rb'\s*$')
RX_IMG = re.compile(rb'T188Img: when=([a-z]+) key=(?:([0-9a-f]{16}) ' + b' '.join(f.encode() + rb'=(\d+)' for f in HEAD) +
                    rb'|(other)) ' + b' '.join(f.encode() + rb'=(\d+)' for f in CLS) + rb'\s*$')
RX_T109 = re.compile(rb'T109Stat: when=([a-z]+) ' + b' '.join(f.encode() + rb'=(\d+)' for f in T109) + rb'\s*$')


def parse_line(line, r):
    """Feeds one raw log line (bytes) into the scan state r; returns True when the line carried a T188 / T109 prefix."""
    if b'T188' not in line and b'T109Stat:' not in line:
        return False
    if b'T188Stat:' in line:
        m = RX_STAT.search(line)
        if m:
            d = dict(when=m.group(1).decode())
            for k, v in zip(STAT, m.groups()[1:]):
                d[k] = int(v)
            r['stat'].append(d)
        else:
            r['stat_bad'] += 1
        return True
    if b'T188Img:' in line:
        m = RX_IMG.search(line)
        if m:
            g = m.groups()
            when = g[0].decode()
            if g[12] is not None:
                d = dict(when=when, key='other')
            else:
                d = dict(when=when, key=g[1].decode())
                for k, v in zip(HEAD, g[2:12]):
                    d[k] = int(v)
            for k, v in zip(CLS, g[13:]):
                d[k] = int(v)
            r['img'].append(d)
        else:
            r['img_bad'] += 1
        return True
    if b'T109Stat:' in line:
        m = RX_T109.search(line)
        if m:
            d = dict(when=m.group(1).decode())
            for k, v in zip(T109, m.groups()[1:]):
                d[k] = int(v)
            r['t109'].append(d)
        else:
            r['t109_bad'] += 1
        return True
    if b'T188: mode=' in line:
        m = RX_MODE.search(line)
        if m:
            r['mode'].append((int(m.group(1)), m.group(2).decode(), int(m.group(3))))
        else:
            r['mode_bad'] += 1
        return True
    return False


def empty():
    return dict(mode=[], mode_bad=0, stat=[], stat_bad=0, img=[], img_bad=0, t109=[], t109_bad=0)


def scan(path):
    r = empty()
    with open(path, 'rb') as f:
        for line in f:
            if line.startswith(b'FrameTrace'):
                continue
            parse_line(line, r)
    return r


def exit_of(rows):
    ex = [s for s in rows if s['when'] == 'exit']
    return ex[0] if len(ex) == 1 else None


def ssum(d, names):
    return sum(d[k] for k in names)


def checks(r, m5_total=None, m5_on=True):
    """The stop members.  Returns a list of [name, ok] (every member printed; ok False on any - the series stops)."""
    out = []

    def mem(name, ok):
        out.append([name, bool(ok)])

    mem('N: exactly one mode line T188: mode=%d cls=%s k=%d (%s, unparsable %d)' % (PLAN_MODE + (r['mode'], r['mode_bad'])),
        r['mode'] == [PLAN_MODE] and r['mode_bad'] == 0)
    nex = sum(1 for s in r['stat'] if s['when'] == 'exit')
    nex9 = sum(1 for s in r['t109'] if s['when'] == 'exit')
    img_ex = [g for g in r['img'] if g['when'] == 'exit']
    n_other = sum(1 for g in img_ex if g['key'] == 'other')
    mem('E: exactly one T188Stat when=exit (%d of %d lines), exactly one T109Stat when=exit (%d of %d lines)' % (
        nex, len(r['stat']), nex9, len(r['t109'])), nex == 1 and nex9 == 1)
    mem('E: T188Img when=exit rows >= 1 (%d), key=other at most once (%d), every row when=exit (%d not)' % (
        len(img_ex), n_other, len(r['img']) - len(img_ex)), len(img_ex) >= 1 and n_other <= 1 and len(img_ex) == len(r['img']))
    mem('E: 0 unparsable lines (T188Stat %d, T188Img %d, T109Stat %d, T188: mode %d)' % (
        r['stat_bad'], r['img_bad'], r['t109_bad'], r['mode_bad']),
        r['stat_bad'] == 0 and r['img_bad'] == 0 and r['t109_bad'] == 0 and r['mode_bad'] == 0)
    zbad = [(i, s['when'], k, s[k]) for i, s in enumerate(r['stat']) for k in INVARIANTS if s[k] != 0]
    mem('Z: invariants 0 on every T188Stat line (%s): %s' % ('/'.join(INVARIANTS), zbad[:4] or 'all 0'), not zbad)
    e = exit_of(r['stat'])
    t = exit_of(r['t109'])
    if e is None:
        mem('I1-I8: the exit line exists', False)
    else:
        mem('N (I7, cls=all): tint_skip_cls = 0 (%d)' % e['tint_skip_cls'], e['tint_skip_cls'] == 0)
        mem('I1: part = part_st + part_fill + part_copy + part_unk (%d = %d), part_unk = 0 (%d)' % (
            e['part'], ssum(e, ('part_st', 'part_fill', 'part_copy', 'part_unk')), e['part_unk']),
            e['part'] == ssum(e, ('part_st', 'part_fill', 'part_copy', 'part_unk')) and e['part_unk'] == 0)
        a = ssum(e, ('part_synced', 'part_dlmem', 'reopen', 'ep_new'))
        mem('I2a: part = part_synced + part_dlmem + reopen + ep_new (%d = %d)' % (e['part'], a), e['part'] == a)
        lhs, rhs = e['ep_new'] + e['ep_prop'], ssum(e, CL_ALL) + e['open']
        mem('I2b: ep_new + ep_prop = sum cl_* (15, without cl_none) + open (%d = %d)' % (lhs, rhs), lhs == rhs)
        p = ssum(e, ('pend_done', 'pend_drop', 'pend_free', 'pend_open'))
        mem('I2c: ep_pend = pend_done + pend_drop + pend_free + pend_open (%d = %d)' % (e['ep_pend'], p), e['ep_pend'] == p)
        mem('I2d: ep_pend <= cl_smp + ... + cl_vo (S3 only) (%d <= %d)' % (e['ep_pend'], ssum(e, CL_S3)), e['ep_pend'] <= ssum(e, CL_S3))
        w = ssum(e, ('w_mipal', 'w_inmip', 'w_other'))
        mem('I4: part = w_mipal + w_inmip + w_other (%d = %d)' % (e['part'], w), e['part'] == w)
        mem('I4: part_off <= part (%d <= %d); w_bytes <= img_bytes (%d <= %d); img_bytes_unsync <= img_bytes (%d <= %d)' % (
            e['part_off'], e['part'], e['w_bytes'], e['img_bytes'], e['img_bytes_unsync'], e['img_bytes']),
            e['part_off'] <= e['part'] and e['w_bytes'] <= e['img_bytes'] and e['img_bytes_unsync'] <= e['img_bytes'])
        mem('I4: in_pass_unsync <= in_pass <= part (%d <= %d <= %d)' % (e['in_pass_unsync'], e['in_pass'], e['part']),
            e['in_pass_unsync'] <= e['in_pass'] <= e['part'])
        img = [g for g in r['img'] if g['when'] == 'exit']
        i3 = []
        for c, gs in I3_MAP:
            sc, sg = sum(g[c] for g in img), ssum(e, gs)
            if sc != sg:
                i3.append('%s %d != %d' % (c, sc, sg))
        mem('I3: every class field summed over the T188Img rows and key=other = the global field (27 fields): %s' % (i3[:4] or 'all equal'),
            not i3 and len(img) >= 1)
        tint_s3 = ssum(e, CL_S3) + e['pend_done']
        mem('I6: tint_ep <= (cl_smp + ... + cl_vo) + pend_done (%d <= %d); tint_bad = 0 (%d)' % (e['tint_ep'], tint_s3, e['tint_bad']),
            e['tint_ep'] <= tint_s3 and e['tint_bad'] == 0)
        over = [g['key'] for g in img if g['tint_bytes'] > g['lost_bytes'] + g['lost_pend_bytes']]
        mem('I6 (=2): per class tint_bytes <= lost_bytes + lost_pend_bytes (rows over: %s)' % (over[:4] or 'none'), not over)
        rb0 = ssum(e, ('tint_rb0_ok', 'tint_rb0_bad', 'tint_rb0_none', 'tint_rb0_nofmt'))
        mem('I6: tint_rb_req = rb0_ok + rb0_bad + rb0_none + rb0_nofmt (%d = %d)' % (e['tint_rb_req'], rb0), e['tint_rb_req'] == rb0)
        rb1 = ssum(e, ('tint_rb1_ok', 'tint_rb1_over', 'tint_rb1_bad', 'tint_rb1_none'))
        mem('I6: tint_rb0_ok = rb1_ok + rb1_over + rb1_bad + rb1_none (%d = %d); rb0_bad = rb1_bad = 0 (%d, %d)' % (
            e['tint_rb0_ok'], rb1, e['tint_rb0_bad'], e['tint_rb1_bad']),
            e['tint_rb0_ok'] == rb1 and e['tint_rb0_bad'] == 0 and e['tint_rb1_bad'] == 0)
        k = (r['mode'][0][2] if r['mode'] else PLAN_MODE[2])
        ncls = sum(1 for g in img if g['key'] != 'other' and g['tint_ep'] >= 1) + sum(g['tint_ep'] for g in img if g['key'] == 'other')
        mem('I6: tint_rb_req <= K x classes with tint_ep >= 1 (%d <= %d x %d; key=other counts its tint_ep as an upper bound)' % (
            e['tint_rb_req'], k, ncls), e['tint_rb_req'] <= k * ncls)
        mem('I8: ep_bad = 0 (%d), lock_bad = 0 (%d)' % (e['ep_bad'], e['lock_bad']), e['ep_bad'] == 0 and e['lock_bad'] == 0)
        if m5_on:
            if m5_total is None or m5_total.get('when') != 'exit':
                mem('I5: the M5W2Stat total of the tag is a when=exit line (%s)' % (None if m5_total is None else m5_total.get('when')), False)
            else:
                ok1 = e['part'] == m5_total['inv_part_src']
                cond = m5_total['inv_part'] == m5_total['inv_part_src']
                ok2 = (not cond) or e['part_off'] == m5_total['inv_off']
                mem('I5: part = inv_part_src (%d = %d); part_off = inv_off when inv_part = inv_part_src (%s: %d = %d)' % (
                    e['part'], m5_total['inv_part_src'], 'applies' if cond else 'does not apply', e['part_off'], m5_total['inv_off']),
                    ok1 and ok2)
    if t is None:
        mem('I9: the T109Stat exit line exists', False)
    else:
        mem('I9: zx_narrow <= zx_d32 <= d32 (%d <= %d <= %d); bias_narrow <= bias_d32 <= d32 (%d <= %d); ovr_vpc <= ovr_w (%d <= %d)' % (
            t['zx_narrow'], t['zx_d32'], t['d32'], t['bias_narrow'], t['bias_d32'], t['ovr_vpc'], t['ovr_w']),
            t['zx_narrow'] <= t['zx_d32'] <= t['d32'] and t['bias_narrow'] <= t['bias_d32'] <= t['d32'] and t['ovr_vpc'] <= t['ovr_w'])
    return out


def class_choice(r):
    """Item 785 (v)(2): classes by descending lost_bytes + lost_pend_bytes of the T188Img rows of the =2 tag until the sum reaches
    SHARE of the scene sum, at most MAX_CLASSES; the scene sum is the global lost_bytes + lost_pend_bytes of the exit line (= the sum
    of the rows and key=other by I3); key=other is not a class and is never chosen.  Returns a dict of rows."""
    e = exit_of(r['stat'])
    img = [g for g in r['img'] if g['when'] == 'exit' and g['key'] != 'other']
    total = (e['lost_bytes'] + e['lost_pend_bytes']) if e else None
    rows = sorted(img, key=lambda g: (-(g['lost_bytes'] + g['lost_pend_bytes']), -g['ev'], g['key']))
    chosen = []
    acc = 0
    if total:
        for g in rows:
            if acc >= SHARE * total or len(chosen) >= MAX_CLASSES:
                break
            v = g['lost_bytes'] + g['lost_pend_bytes']
            if v == 0:
                break
            chosen.append(g['key'])
            acc += v
    reached = bool(total) and acc >= SHARE * total
    return dict(total=total, chosen=chosen, chosen_bytes=acc, share=(acc / total if total else None), reached=reached,
                rest_bytes=(total - acc if total is not None else None),
                note=('scene sum 0 - no lost bytes, no class' if total == 0 else
                      'no exit line' if total is None else
                      'share %.4f %s %.1f with %d class(es) (max %d); rest - not determined (item 785 (v)(2))' % (
                          acc / total, '>=' if reached else '<', SHARE, len(chosen), MAX_CLASSES)))


def class_rows(r):
    """The per-class rows for M9g: readback alive (section 5.3: tint_rb0_ok(c) >= 1 and globally rb0_bad = rb1_bad = 0) and the
    coverage tint_bytes(c) / (lost_bytes(c) + lost_pend_bytes(c)) against 0.5 (rows, not a verdict)."""
    e = exit_of(r['stat'])
    glob_ok = e is not None and e['tint_rb0_bad'] == 0 and e['tint_rb1_bad'] == 0
    out = []
    for g in r['img']:
        if g['when'] != 'exit':
            continue
        lost = g['lost_bytes'] + g['lost_pend_bytes']
        cov = (g['tint_bytes'] / lost) if lost else None
        out.append(dict(key=g['key'], lost=lost, tint_bytes=g['tint_bytes'], tint_ep=g['tint_ep'], coverage=cov,
                        cover_ge_05=(cov is not None and cov >= COVER_MIN), rb0_ok=g['tint_rb0_ok'],
                        readback_alive=(g['key'] != 'other' and g['tint_rb0_ok'] >= 1 and glob_ok),
                        head=dict((k, g.get(k)) for k in HEAD) if g['key'] != 'other' else None, ev=g['ev']))
    return out


def open_field(e):
    """Item 788 (g) N2: the field open is read only at ep_bad = 0; otherwise None (not read)."""
    if e is None or e['ep_bad'] != 0:
        return None
    return e['open']


def t109_rows(r):
    """Item 785 (g) with 788 (v), 789 (g), 791 (v): rows of one tag, no verdict.
    diff_zx(line) = zx_narrow - zx_narrow_vi, diff_bias(line) = bias_narrow - bias_narrow_vi per T109Stat line in log order.
    zx_part_791: the zx part is counted only when diff_zx >= 1 in some periodic line AND in every later line including exit (item 791
    (v): one line only, or diff >= 1 first at the exit line => the previous periodic line must have it - else 'not determined').
    zx_eq_all (item 789 (g)(3)): zx_narrow >= 1 and zx_narrow = zx_narrow_vi on the exit line - for this tag the zx part is
    'not determined' (M9g checks 'on all tags').  The same for bias (reference: the bias part of 785 (g)(3) is bias_d32 >= 1)."""
    lines = r['t109']
    t = exit_of(lines)

    def part(fa, fb):
        d = [s[fa] - s[fb] for s in lines]
        whens = [s['when'] for s in lines]
        counted = False
        for i, (dv, w) in enumerate(zip(d, whens)):
            if w == 'periodic' and dv >= 1 and all(x >= 1 for x in d[i + 1:]) and i + 1 <= len(d) - 1 and whens[-1] == 'exit':
                counted = True
                break
        return d, counted

    dz, zc = part('zx_narrow', 'zx_narrow_vi')
    db, bc = part('bias_narrow', 'bias_narrow_vi')
    res = dict(lines=len(lines), whens=[s['when'] for s in lines], diff_zx=dz, diff_bias=db, zx_part_791=zc, bias_part_791=bc)
    if t is not None:
        res.update(exit=dict((k, t[k]) for k in T109), armed_d32=t['d32'] >= 1, zx_d32_ge1=t['zx_d32'] >= 1,
                   ovr_vpc_ge1=t['ovr_vpc'] >= 1, zx_narrow_ge1=t['zx_narrow'] >= 1, bias_d32_ge1=t['bias_d32'] >= 1,
                   zx_eq_all=(t['zx_narrow'] >= 1 and t['zx_narrow'] == t['zx_narrow_vi']),
                   i9=(t['zx_narrow'] <= t['zx_d32'] <= t['d32'] and t['bias_narrow'] <= t['bias_d32'] <= t['d32']
                       and t['ovr_vpc'] <= t['ovr_w']),
                   vi_ref=dict(zx_vi_le=t['zx_narrow_vi'] <= t['zx_narrow'], bias_vi_le=t['bias_narrow_vi'] <= t['bias_narrow'],
                               cd_le=t['narrow_cd'] <= t['zx_narrow_vi'] + t['bias_narrow_vi']))
    return res

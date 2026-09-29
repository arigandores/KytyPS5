# Independent recount for s130 audit (HPP-153, ROADMAP s122 p.122(e)).
# Own code: no import from smk130b.py / smk130.py. Blocks by 'GateArm:' lines;
# a FrameTrace-x line belongs to the latest preceding GateArm; position p = n - F - 1
# (first main line after 'GateArm: frame=F' has n = F, trap of s128); window 10..88 (p.55(b)).
import sys, re, json

KEYS = ['ac_cmp_pages', 'ac_cdiff', 'ac_cbad', 'ac_cbad_m', 'ac_cbad_e',
        'ac_cbm_nosnap', 'ac_cbm_bad', 'ac_cbm_left', 'ac_cbm_stale', 'ac_cbm_remark',
        'ac_cbm_new', 'ac_cbm_pend', 'ac_cbm_host', 'ac_cbm_host_d',
        'ac_cbe_ro', 'ac_cbe_na', 'ac_cbe_oth', 'ac_bad', 'ac_jleft', 'ac_jremark', 'ac_jstale']
AI_NULL_SKIP = ('ai_op_ns', 'ai_op_n')

def parse(path):
    arm_re = re.compile(rb'GateArm: arm=(\d+) arms=\d+ block=(\d+) frame=(\d+) .*text=(\S+)')
    cur = None  # (block, F, text)
    rows = []   # dicts
    content = []  # (block, text, line)
    torn = 0
    pre = 0
    ai_nonzero = 0
    hist_last = {}
    with open(path, 'rb') as f:
        for line in f:
            if line.startswith(b'GateArm:'):
                m = arm_re.search(line)
                cur = (int(m.group(2)), int(m.group(3)), m.group(4).decode())
                continue
            if line.startswith(b'FrameTrace-x'):
                if cur is None:
                    pre += 1
                    continue
                d = {}
                for kv in line.split():
                    if b'=' in kv:
                        k, v = kv.split(b'=', 1)
                        k = k.decode()
                        if k == 'n' or k.startswith('ac_') or k.startswith('ai_'):
                            try:
                                d[k] = int(v)
                            except ValueError:
                                pass
                for k in KEYS:
                    if k not in d:
                        raise SystemExit('missing key %s at n=%s' % (k, d.get('n')))
                for k, v in d.items():
                    if k.startswith('ai_') and k not in AI_NULL_SKIP and v != 0:
                        ai_nonzero += 1
                d['_blk'], d['_F'], d['_arm'] = cur
                d['_p'] = d['n'] - cur[1] - 1
                rows.append(d)
                continue
            if b'ArmCopyVerify: CONTENT' in line:
                content.append((cur[0] if cur else None, cur[2] if cur else None, line.decode('utf-8', 'replace').strip()))
            elif b'ArmCopyClass: TORN' in line:
                torn += 1
    return rows, content, torn, pre, ai_nonzero

def summ(rows, pred):
    s = {k: 0 for k in KEYS}
    n = 0
    for r in rows:
        if pred(r):
            n += 1
            for k in KEYS:
                s[k] += r[k]
    s['_rows'] = n
    s['H'] = s['ac_cbm_host'] - s['ac_cbm_host_d']
    s['M_own'] = s['ac_cbm_nosnap'] + s['ac_cbm_bad'] + s['ac_cbm_left'] + s['ac_cbm_stale'] + s['ac_cbm_host']
    s['M_for'] = s['ac_cbm_remark'] + s['ac_cbm_new'] + s['ac_cbm_pend']
    s['M4p'] = s['ac_cbad_m'] - s['ac_cbm_left']
    return s

def identities(rows):
    bad = {'I1': 0, 'I2': 0, 'I3': 0, 'I8': 0, 'I4row': 0}
    for r in rows:
        if r['ac_cbad_m'] + r['ac_cbad_e'] != r['ac_cbad']: bad['I1'] += 1
        if (r['ac_cbm_nosnap'] + r['ac_cbm_bad'] + r['ac_cbm_left'] + r['ac_cbm_stale'] + r['ac_cbm_remark']
                + r['ac_cbm_new'] + r['ac_cbm_pend'] + r['ac_cbm_host']) != r['ac_cbad_m']: bad['I2'] += 1
        if r['ac_cbe_ro'] + r['ac_cbe_na'] + r['ac_cbe_oth'] != r['ac_cbad_e']: bad['I3'] += 1
        if r['ac_cbm_host_d'] > r['ac_cbm_host']: bad['I8'] += 1
        if not (r['ac_cbad'] <= r['ac_cdiff'] <= r['ac_cmp_pages']): bad['I4row'] += 1
    # I4 by block sums
    blocks = {}
    for r in rows:
        b = blocks.setdefault(r['_blk'], [0, 0, 0])
        b[0] += r['ac_cbad']; b[1] += r['ac_cdiff']; b[2] += r['ac_cmp_pages']
    bad['I4blk'] = sum(1 for b in blocks.values() if not (b[0] <= b[1] <= b[2]))
    bad['_nblocks'] = len(blocks)
    return bad

def verdict(s2, s4, guards2):
    # p.118(b)(3): LOSS if guards>0 or 2*H2*cmp4 > 3*H4*cmp2 or (H4==0 and H2>0)
    H2, H4, c2, c4 = s2['H'], s4['H'], s2['ac_cmp_pages'], s4['ac_cmp_pages']
    if guards2 > 0: return 'CBAD_LOSS(guard)'
    if H4 == 0 and H2 > 0: return 'CBAD_LOSS(H4=0<H2)'
    if 2 * H2 * c4 > 3 * H4 * c2: return 'CBAD_LOSS(ratio)'
    return 'pass'

def main():
    out = {}
    for tag in sys.argv[1:]:
        rows, content, torn, pre, ainz = parse('C:/kyty/s130/log_%s.txt' % tag)
        arms = sorted(set(r['_arm'] for r in rows))
        res = {'rows_total': len(rows), 'rows_pre_gatearm': pre, 'torn': torn, 'ai_nonzero_fields': ainz,
               'identities': identities(rows), 'arms': {}}
        for a in arms:
            res['arms'][a] = {
                'all': summ(rows, lambda r, a=a: r['_arm'] == a),
                'win': summ(rows, lambda r, a=a: r['_arm'] == a and 10 <= r['_p'] <= 88),
            }
        # rows carrying H>0
        res['H_rows'] = [(r['n'], r['_blk'], r['_arm'], r['_p'], r['ac_cbm_host'] - r['ac_cbm_host_d'])
                         for r in rows if r['ac_cbm_host'] - r['ac_cbm_host_d'] > 0]
        # CONTENT H lines (why=host dk=0), attributed to block by position in log
        hl = [(b, t, l) for (b, t, l) in content if 'why=host' in l and 'dk=0' in l]
        res['H_content'] = [(b, t, re.search(r'mode=(\d)', l).group(1), re.search(r'addr=(\S+)', l).group(1)) for (b, t, l) in hl]
        res['content_by_mode_class'] = {}
        for (b, t, l) in content:
            mo = re.search(r'mode=(\d) class=(\w)', l)
            k = '%s%s' % (mo.group(1), mo.group(2)) if mo else '?'
            res['content_by_mode_class'][k] = res['content_by_mode_class'].get(k, 0) + 1
        if 'armcopy=2' in res['arms'] and 'armcopy=4' in res['arms']:
            for w in ('all', 'win'):
                s2 = res['arms']['armcopy=2'][w]; s4 = res['arms']['armcopy=4'][w]
                g2 = s2['ac_cbm_nosnap'] + s2['ac_cbm_bad'] + s2['ac_cbm_left'] + s2['ac_cbm_stale']
                res['verdict_' + w] = verdict(s2, s4, s2['ac_cbm_bad'] + s2['ac_cbm_left'] + s2['ac_cbm_stale'])
                res['guards2_' + w] = g2
            # p.119(v): recount by chunk mode from H CONTENT lines (not saturated if <40 per mode)
            per_mode = {}
            moved = 0
            for (b, t, mode, addr) in res['H_content']:
                per_mode[mode] = per_mode.get(mode, 0) + 1
                if t != 'armcopy=%s' % mode: moved += 1
            res['H_content_per_mode'] = per_mode
            res['H_content_moved_across_arm'] = moved
            # pairs ABBA: per block H per page
            blk = {}
            for r in rows:
                e = blk.setdefault(r['_blk'], [r['_arm'], 0, 0])
                e[1] += r['ac_cbm_host'] - r['ac_cbm_host_d']; e[2] += r['ac_cmp_pages']
            res['blocks'] = {b: v for b, v in sorted(blk.items())}
        out[tag] = res
    json.dump(out, open('C:/kyty/s130/audit130/recount130.json', 'w'), indent=1, default=str)
    for tag, res in out.items():
        print('==', tag, 'rows', res['rows_total'], 'pre', res['rows_pre_gatearm'], 'TORN', res['torn'], 'ai!=0', res['ai_nonzero_fields'])
        print('  identities', res['identities'])
        for a, d in res['arms'].items():
            for w in ('all', 'win'):
                s = d[w]
                print('  %s %s rows=%d cmp=%d cbad=%d M=%d H=%d host=%d host_d=%d Mown=%d Mfor=%d M4p=%d nosnap=%d bad=%d left=%d stale=%d jstale=%d'
                      % (a, w, s['_rows'], s['ac_cmp_pages'], s['ac_cbad'], s['ac_cbad_m'], s['H'], s['ac_cbm_host'], s['ac_cbm_host_d'],
                         s['M_own'], s['M_for'], s['M4p'], s['ac_cbm_nosnap'], s['ac_cbm_bad'], s['ac_cbm_left'], s['ac_cbm_stale'], s['ac_jstale']))
        for k in ('verdict_all', 'verdict_win', 'guards2_all', 'guards2_win', 'H_content_per_mode', 'H_content_moved_across_arm'):
            if k in res: print(' ', k, res[k])
        print('  H_rows', res['H_rows'])
        print('  H_content', res['H_content'])
        print('  content', res['content_by_mode_class'])
    print('DONE')

main()

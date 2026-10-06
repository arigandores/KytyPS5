"""F20l2 (HPP-648): the edits of the ported F20l files in C:/kyty/f287/f20l2 (ROADMAP s122 item 574 (d), (e); item 581 (v)(2), (v)(5),
(zh); item 584 (v)) - every anchor must occur exactly once (else refused, nothing written).  LF, ASCII.  usage: python edit_f20l2.py"""
import os
import sys

G = 'C:/kyty/f287/f20l2'
E = {}

# ------------------------------------------------------------------ b32_read.py
E['b32_read.py'] = [
    ('head',
     '"""Track F link F20l2 (HPP-648; ROADMAP s122 item 550 (g), (d), (zh), (z); item 552 (v)(3), (g), (e)(3); item 553 (b), (v); item 554 (g)):\n'
     'the reader of the KYTY_DIAG_B32 control tags b32_z0b, b32_ppb, b32_pcb, b32_pd, b32_pd2.  NO VERDICT - the reading of the controls, U1\n'
     'and the number theta_load are F20m (lead).  ASCII only.\n',
     '"""Track F link F20l2 (HPP-648; ROADMAP s122 item 574 (d), (e); item 581 (v)(2), (v)(5), (zh); item 584 (v); the rule of item 550 (g) with\n'
     'the amendments of items 551 (v), 552 (v)(3), (g), 553 (v), 554 (g)): the reader of the repeated KYTY_DIAG_B32 controls b32_z0b, b32_ppb,\n'
     'b32_pcb on the F20j4 test binary 2d0c8815, and the reference reread of the F20l log b32_pd (F20j2 test binary b9e0ee00) with theta_load.\n'
     'NO VERDICT - F20m2 (lead).  theta_load is read from the seal (line \'theta_load: <x>\', item 574 (b)(6): 0.4562).  ASCII only.\n'),
    ('usage1',
     '    python b32_read.py <tag> [--json <out>] [--theta <x>]          one tag (files of C:/kyty/f287/f20l2)\n'
     '    python b32_read.py --dir <fixture dir> --tag <tag> [--json <out>] [--theta <x>]\n',
     '    python b32_read.py <tag> [--json <out>]                        one tag (files of C:/kyty/f287/f20l2; b32_pd - files of\n'
     '                                                                    C:/kyty/f287/f20l, the reference reread of item 574 (e))\n'
     '    python b32_read.py --dir <fixture dir> --tag <tag> [--json <out>]\n'),
    ('doc load',
     '   (iii) HOST_LOAD    other_us >= theta_load x ncpu x window (window = dt_us of the DiagB32: line); theta_load is F20m - without --theta\n'
     '                      the member is skipped (item 550 (d)(6): \'HOST_LOAD is not issued\'), the ratio other_us / (ncpu x window) is printed\n',
     '   (iii) HOST_LOAD    other_us >= theta_load x ncpu x window (window = dt_us of the DiagB32: line); theta_load from the seal (0.4562,\n'
     '                      item 574 (b)(6)); the ratio other_us / (ncpu x window) is printed\n'),
    ('doc W',
     '           W:<kind>  sleep -> GUEST_SLEEP:sleep; else the -w record of this thread and kind with the largest overlap_us: to = 1 ->\n'
     '                     GUEST_SLEEP:<kind> (RC5 (v)); no record or waker < 0 -> GUEST_SLEEP:<kind>; else a step to the waker (mutex: the\n'
     '                     record waker is the owner at entry = peer; without a record the -t peer)\n',
     '           W:<kind>  sleep -> GUEST_SLEEP:sleep; else the -w record of this thread and kind with the largest overlap_us (item 574 (d)):\n'
     '                     to = 1 with a guest deadline -> GUEST_SLEEP:<kind> (RC5 (v), item 581 (v)(5): a GUEST kind, or an EMU kind with\n'
     '                     req_us > 0); else a step to the record waker (>= 0); else a step to the record peer (>= 0); else (as before) for\n'
     '                     mutex a step to the -t peer; else EMU_WAIT:<kind> for an EMU kind (item 574 (d), 581 (v)(5): EmuMutex .. Av,\n'
     '                     vblank, audio, aio, net, emu_join; no RC6) and GUEST_SLEEP:<kind> for a GUEST kind (RC6)\n'),
    ('consts',
     "SEAL_PATH = G + '/pred/f20l2_seal.md'\n",
     "SEAL_PATH = G + '/pred/f20l2_seal.md'\n"
     "G_F20L = 'C:/kyty/f287/f20l'          # the F20l files: reference reread of b32_pd (item 574 (e))\n"
     "SEAL_F20L = G_F20L + '/pred/f20l_seal.md'\n"
     "BIN_F20J2 = 'b9e0ee0092ca1504979ebd674abb21c8d67015fd030bc33615eb2c87acb90f91'    # F20j2 test binary of the F20l log b32_pd\n"
     "THETA_RX = re.compile(r'^theta_load: ([0-9]+\\.[0-9]+)[ \\t]*$', re.M)\n"),
    ('bin comment',
     "BIN_TEST = '2d0c8815389bdc42a2371ba813dc9460fc5565f21f89e32fad4d9e5bd2394dc7'     # F20j4 test binary, item 553 (a), 554 (a)\n",
     "BIN_TEST = '2d0c8815389bdc42a2371ba813dc9460fc5565f21f89e32fad4d9e5bd2394dc7'     # F20j4 test binary, items 583, 584 (g)\n"),
    ('form',
     "        'b32_pd': dict(KYTY_DIAG_B32='1', KYTY_GPU_WALL='1'),\n"
     "        'b32_pd2': dict(KYTY_DIAG_B32='1', KYTY_GPU_WALL='1')}\n"
     "LOADER = {'b32_pd': 'all', 'b32_pd2': 'half'}\n"
     "TAG_RX = re.compile(r'^(b32_z0b|b32_ppb|b32_pcb|b32_pd|b32_pd2)(_r[1-6])?$')\n",
     "        'b32_pd': dict(KYTY_DIAG_B32='1', KYTY_GPU_WALL='1')}\n"
     "LOADER = {'b32_pd': 'all'}\n"
     "TAG_RX = re.compile(r'^(b32_z0b|b32_ppb|b32_pcb|b32_pd)(_r[1-6])?$')\n"),
    ('waits',
     "WAITS = ('cond', 'mutex', 'sem', 'psem', 'evf', 'eq', 'sleep', 'gpu_idle', 'gpu_regmem')\n",
     "# enum Wait of 4371ff4b / f2307b02 src/common/diagB32.h in order (WaitName), item 574 (g)(1), 581 (v)(5)\n"
     "WAITS = ('cond', 'mutex', 'sem', 'psem', 'evf', 'eq', 'sleep', 'gpu_idle', 'gpu_regmem',\n"
     "         'emu_mutex', 'gpu_wait', 'gpu_cmd', 'flip_slot', 'flip_done', 'flip_cancel', 'flip_req', 'vo_pace', 'relay', 'frame_pool',\n"
     "         'rec_wait', 'rec_idle', 'asub_idle', 'asub_drain', 'ops_wait', 'ops_idle', 'pipe_wait', 'pcopy', 'pm_drain', 'vma_flush',\n"
     "         'rec_queue', 'main_task', 'main_idle', 'spin', 'av',\n"
     "         'vblank', 'once', 'join', 'addr', 'aio', 'fiber', 'audio', 'ult', 'net', 'rwlock', 'emu_join')\n"
     "# EMU_WAIT kinds (item 574 (d); item 581 (v)(5): who clears the wait condition - the device emulation, the host I/O or an emulator thread)\n"
     "EMU_WAITS = WAITS[9:34] + ('vblank', 'audio', 'aio', 'net', 'emu_join')\n"
     "# GUEST_SLEEP kinds: the older ones and the guest HLE kinds of item 581 (v)(5)\n"
     "GUEST_WAITS = WAITS[:9] + ('once', 'join', 'addr', 'fiber', 'ult', 'rwlock')\n"),
    ('chain sig',
     "def chain(d, holder, fr, b, e_us):\n"
     "    \"\"\"Item 550 (g)(2)(iv) with RC6, RC7.  Returns (class, family, path list, terminal role, note).\"\"\"\n",
     "def chain(d, holder, fr, b, e_us, steps=None):\n"
     "    \"\"\"Item 550 (g)(2)(iv) with RC6, RC7 and the amendment of item 574 (d) / 581 (v)(5).  Returns (class, family, path list, terminal\n"
     "    role, note); steps (a list) gets one dict per visited thread (slot, name, role, R, Sw, S, samples, how it was reached).\"\"\"\n"
     "    steps = [] if steps is None else steps\n"
     "    how = 'holder'\n"),
    ('chain visit',
     "        visited.append(cur)\n"
     "        st, x = dominant(row, samples)\n",
     "        visited.append(cur)\n"
     "        steps.append(dict(slot=cur, name=row.get('name'), role=row.get('role'), R=num(row.get('R'), 0), Sw=num(row.get('Sw'), 0),\n"
     "                          S=num(row.get('S'), 0), samples=samples, how=how))\n"
     "        st, x = dominant(row, samples)\n"),
    ('chain W',
     "            recs = [w for w in d['w'] if w.get('slot') == cur and w.get('kind') == x]\n"
     "            best = max(recs, key=lambda w: (num(w.get('overlap_us'), 0) or 0)) if recs else None\n"
     "            target = None\n"
     "            if best is not None and best.get('to') == 1:\n"
     "                c, fam, note = guest_check('GUEST_SLEEP:%s' % x)\n"
     "                return c, fam, path, role, (note + ' timeout record').strip()\n"
     "            wk = num(best.get('waker'), -1) if best is not None else -1\n"
     "            pr = num(row.get('peer'), -1)\n"
     "            if wk is not None and wk >= 0:\n"
     "                target = wk\n"
     "            elif x == 'mutex' and pr is not None and pr >= 0:\n"
     "                target = pr\n"
     "            if target is None:\n"
     "                c, fam, note = guest_check('GUEST_SLEEP:%s' % x)\n"
     "                return c, fam, path, role, (note + ' no waker').strip()\n",
     "            emu = x in EMU_WAITS\n"
     "            recs = [w for w in d['w'] if w.get('slot') == cur and w.get('kind') == x]\n"
     "            best = max(recs, key=lambda w: (num(w.get('overlap_us'), 0) or 0)) if recs else None\n"
     "            target = None\n"
     "            to = best is not None and best.get('to') == 1\n"
     "            if to and (not emu or (num(best.get('req_us'), 0) or 0) > 0):\n"
     "                c, fam, note = guest_check('GUEST_SLEEP:%s' % x)\n"
     "                return c, fam, path, role, (note + ' timeout record').strip()\n"
     "            wk = num(best.get('waker'), -1) if best is not None else -1\n"
     "            rp = num(best.get('peer'), -1) if best is not None else -1\n"
     "            pr = num(row.get('peer'), -1)\n"
     "            if wk is not None and wk >= 0:\n"
     "                target, how = wk, 'waker'\n"
     "            elif rp is not None and rp >= 0:\n"
     "                target, how = rp, 'peer'\n"
     "            elif x == 'mutex' and pr is not None and pr >= 0:\n"
     "                target, how = pr, 'tpeer'\n"
     "            if target is None:\n"
     "                var = ('; executor variant (the -t peer for any kind): step to slot %d' % pr) if pr is not None and pr >= 0 else ''\n"
     "                if to:\n"
     "                    var += '; executor variant (RC5 (v) to = 1 for every kind): GUEST_SLEEP:%s' % x\n"
     "                if emu:\n"
     "                    return 'EMU_WAIT:%s' % x, 'EMU_WAIT', path, role, ('no waker, no peer' + (' (timeout record, req_us 0)' if to else '')\n"
     "                                                                        + var)\n"
     "                c, fam, note = guest_check('GUEST_SLEEP:%s' % x)\n"
     "                return c, fam, path, role, (note + ' no waker, no peer' + var).strip()\n"
     "            path[-1] += '->' + how\n"),
    ('classify chain',
     "    cls, fam, path, role, note = chain(d, holder, fr, b, e_us)\n"
     "    out.update(cls=cls, family=fam, path=path, role=role, note=note)\n",
     "    steps = []\n"
     "    cls, fam, path, role, note = chain(d, holder, fr, b, e_us, steps)\n"
     "    gs = num(h.get('gpu_slot'), -1)\n"
     "    gpu_steps = [s for s in steps if s['slot'] == gs]\n"
     "    out.update(cls=cls, family=fam, path=path, role=role, note=note, steps=steps,\n"
     "               gpu_in_chain=bool(gpu_steps),\n"
     "               gpu_sw_or_s50=any(s['Sw'] >= 0.5 * s['samples'] or s['S'] >= 0.5 * s['samples'] for s in gpu_steps),\n"
     "               gpu_sw_plus_s50=any(s['Sw'] + s['S'] >= 0.5 * s['samples'] for s in gpu_steps))\n"),
    ('row ring',
     "            row['slot_full_w'] = num(d['x'].get('slot_full_w'), 0)\n",
     "            row['slot_full_w'] = num(d['x'].get('slot_full_w'), 0)\n"
     "            row['ring_hold_w'] = num(d['x'].get('ring_hold_w'))\n"),
    ('row cls',
     "        row.update(cls=c['cls'], family=c['family'], path=c.get('path'), holder=c.get('holder'), term_role=c.get('role'),\n"
     "                   note=c.get('note'), E=c.get('E'), load_ratio=c.get('load_ratio'))\n",
     "        row.update(cls=c['cls'], family=c['family'], path=c.get('path'), holder=c.get('holder'), term_role=c.get('role'),\n"
     "                   note=c.get('note'), E=c.get('E'), load_ratio=c.get('load_ratio'), steps=c.get('steps'),\n"
     "                   gpu_sw_or_s50=c.get('gpu_sw_or_s50'))\n"),
    ('res ring',
     "    res['rep_drop'] = num((lastx or {}).get('rep_drop'), 0) or 0\n",
     "    res['rep_drop'] = num((lastx or {}).get('rep_drop'), 0) or 0\n"
     "    # item 554 (v)(1), 574 (g)(5): Z1 counter ring_hold_w over every -x line of the tag and on the hold frames (reference, not a member)\n"
     "    res['ring_hold_w_sum'] = sum(num((d['x'] or {}).get('ring_hold_w'), 0) or 0 for d in diag.values())\n"
     "    res['ring_hold_w_frames'] = sum(1 for x in rows if (x.get('ring_hold_w') or 0) > 0)\n"
     "    res['ring_hold_w_field'] = sum(1 for d in diag.values() if d['x'] is not None and 'ring_hold_w' in d['x'])\n"),
    ('stand row',
     "    c = classify(fr, d, b, theta) if b else dict(cls='UNDETERMINED', note='no base (not a scene frame)')\n"
     "    return dict(n=n, dt_us=f[0], lat_us=f[1], base_lat=b['lat'] if b else None, cls=c.get('cls'), holder=c.get('holder'),\n"
     "                path=c.get('path'), note=c.get('note'))\n",
     "    c = classify(fr, d, b, theta) if b else dict(cls='UNDETERMINED', note='no base (not a scene frame)')\n"
     "    ws = [dict(slot=w.get('slot'), kind=w.get('kind'), overlap_us=w.get('overlap_us'), waker=w.get('waker'), peer=w.get('peer'),\n"
     "               to=w.get('to'), req_us=w.get('req_us'), open=w.get('open')) for w in (d['w'] if d else [])]\n"
     "    return dict(n=n, dt_us=f[0], lat_us=f[1], base_lat=b['lat'] if b else None, cls=c.get('cls'), holder=c.get('holder'),\n"
     "                path=c.get('path'), note=c.get('note'), steps=c.get('steps'), gpu_in_chain=c.get('gpu_in_chain'),\n"
     "                gpu_sw_or_s50=c.get('gpu_sw_or_s50'), gpu_sw_plus_s50=c.get('gpu_sw_plus_s50'), w=ws,\n"
     "                ring_hold_w=num((d['x'] or {}).get('ring_hold_w')) if d else None)\n"),
    ('paths',
     "    d = os.path.join(G, 'runs', tag)\n"
     "    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in names)\n"
     "    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),\n"
     "             idx=os.path.join(G, 'rec_%s.mp4.idx' % tag), seal=SEAL_PATH, load=os.path.join(d, 'load.json'), tmp=d)\n"
     "    return p\n",
     "    gg, seal = (G_F20L, SEAL_F20L) if TAG_RX.match(tag) and TAG_RX.match(tag).group(1) == 'b32_pd' else (G, SEAL_PATH)\n"
     "    d = os.path.join(gg, 'runs', tag)\n"
     "    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in names)\n"
     "    p.update(log=os.path.join(gg, 'log_%s.txt' % tag), stdout=os.path.join(gg, 'stdout_%s.txt' % tag), run=os.path.join(gg, '%s.json' % tag),\n"
     "             idx=os.path.join(gg, 'rec_%s.mp4.idx' % tag), seal=seal, load=os.path.join(d, 'load.json'), tmp=os.path.join(G, 'runs'),\n"
     "             theta_src=SEAL_PATH)\n"
     "    return p\n"),
    ('paths dir',
     "                 idx=os.path.join(base, 'rec.idx'), seal=os.path.join(base, 'seal.md'), load=os.path.join(base, 'load.json'), tmp=base)\n",
     "                 idx=os.path.join(base, 'rec.idx'), seal=os.path.join(base, 'seal.md'), load=os.path.join(base, 'load.json'), tmp=base,\n"
     "                 theta_src=os.path.join(base, 'seal.md'))\n"),
    ('read_tag head',
     "def read_tag(tag, p, theta):\n"
     "    base_tag = TAG_RX.match(tag).group(1)\n"
     "    form = FORM[base_tag]\n",
     "def read_theta(path):\n"
     "    \"\"\"theta_load from the line 'theta_load: <x>' of the seal (item 574 (b)(6), (e)); None if absent or not exactly one.\"\"\"\n"
     "    if not os.path.exists(path):\n"
     "        return None\n"
     "    m = THETA_RX.findall(open(path, 'rb').read().decode('utf-8', 'replace').replace('\\r\\n', '\\n'))\n"
     "    return float(m[0]) if len(m) == 1 else None\n"
     "\n"
     "\n"
     "def read_tag(tag, p):\n"
     "    base_tag = TAG_RX.match(tag).group(1)\n"
     "    form = FORM[base_tag]\n"
     "    theta = read_theta(p['theta_src'])\n"
     "    want_bin = BIN_F20J2 if base_tag == 'b32_pd' else BIN_TEST\n"),
    ('adm bin',
     "        ('json binary_sha256 = F20j4 test 2d0c8815 (%s)' % (jbin or '-')[:16], jbin == BIN_TEST),\n",
     "        ('theta_load from the seal %s (%s)' % (p['theta_src'], theta), theta is not None),\n"
     "        ('json binary_sha256 = %s (%s)' % ('F20j2 test b9e0ee00 (reference reread)' if base_tag == 'b32_pd' else 'F20j4 test 2d0c8815',\n"
     "                                           (jbin or '-')[:16]), jbin == want_bin),\n"),
    ('read_tag call',
     "    r = read_log(p['log'], theta, load, p['tmp']) if os.path.exists(p['log']) else None\n",
     "    r = read_log(p['log'], theta, load, p['tmp']) if os.path.exists(p['log']) and theta is not None else None\n"),
    ('rows ring',
     "        out.append('  -x last %s' % r['x_last'])\n",
     "        out.append('  ring_hold_w (Z1, reference): sum over the -x lines %s, hold frames with ring_hold_w > 0 %s, -x lines with the field %s'\n"
     "                   % (r['ring_hold_w_sum'], r['ring_hold_w_frames'], r['ring_hold_w_field']))\n"
     "        out.append('  -x last %s' % r['x_last'])\n"),
    ('rows stand',
     "            out.append('  STAND frames after TestB32 fire: %s' % [(x['n'], x['dt_us'], x['cls'], x['holder']) for x in r['stand']])\n",
     "            out.append('  STAND frames after TestB32 fire: %s' % [(x['n'], x['dt_us'], x['cls'], x['holder']) for x in r['stand']])\n"
     "            sf = max(r['stand'], key=lambda x: x['dt_us']) if r['stand'] else None\n"
     "            if sf is not None:\n"
     "                out.append('  STAND FRAME n %s dt_us %s class %s holder %s | path %s | note %s' % (\n"
     "                    sf['n'], sf['dt_us'], sf['cls'], sf['holder'], ' > '.join(sf['path'] or []), sf['note']))\n"
     "                out.append('    GuestGpu in the chain %s; a GuestGpu step with Sw or S >= 50 %% %s (executor variant Sw + S: %s); ring_hold_w %s'\n"
     "                           % (sf.get('gpu_in_chain'), sf.get('gpu_sw_or_s50'), sf.get('gpu_sw_plus_s50'), sf.get('ring_hold_w')))\n"
     "                for s in sf.get('steps') or []:\n"
     "                    out.append('    step %s slot %s %s(%s) R %s Sw %s S %s of %s' % (s['how'], s['slot'], s['name'], s['role'], s['R'], s['Sw'],\n"
     "                                                                      s['S'], s['samples']))\n"
     "                for w in sf.get('w') or []:\n"
     "                    out.append('    -w %s' % w)\n"),
    ('main theta',
     "    js = argv[argv.index('--json') + 1] if '--json' in argv else None\n"
     "    theta = float(argv[argv.index('--theta') + 1]) if '--theta' in argv else None\n",
     "    js = argv[argv.index('--json') + 1] if '--json' in argv else None\n"),
    ('main usage',
     "        print('usage: b32_read.py b32_z0b|b32_ppb|b32_pcb|b32_pd|b32_pd2[_r1..6] | --dir D --tag T | --table | --check-seal')\n",
     "        print('usage: b32_read.py b32_z0b|b32_ppb|b32_pcb|b32_pd[_r1..6] | --dir D --tag T | --table | --check-seal')\n"),
    ('main read',
     "    res = read_tag(tag, p, theta)\n",
     "    res = read_tag(tag, p)\n"),
    ('table rx',
     "    tags = sorted(t for t in os.listdir(rd) if TAG_RX.match(t) and os.path.exists(os.path.join(rd, t, 'read.json'))) if os.path.isdir(rd) else []\n",
     "    tags = sorted(t for t in os.listdir(rd) if (TAG_RX.match(t) or t == 'b32_pd_ref') and os.path.exists(os.path.join(rd, t, 'read.json'))) \\\n"
     "        if os.path.isdir(rd) else []\n"),
    ('table cls',
     "        cl = ['%d:%s' % (x['n'], x['cls']) for x in r.get('frames', []) if x['in_count']]\n",
     "        cl = ['%d:%s' % (x['n'], x['cls']) for x in r.get('frames', []) if x['in_count']]\n"
     "        sf = max(r.get('stand') or [], key=lambda x: x['dt_us'], default=None)\n"
     "        if sf is not None:\n"
     "            cl.append('STAND %d:%s gpuSwS50=%s' % (sf['n'], sf['cls'], sf.get('gpu_sw_or_s50')))\n"),
    ('seal default',
     "        seal = argv[argv.index('--seal') + 1] if '--seal' in argv else 'C:/kyty/KytyPS5/docs/track-f/f20l2.md'\n",
     "        seal = argv[argv.index('--seal') + 1] if '--seal' in argv else SEAL_PATH\n"),
]

# ------------------------------------------------------------------ test_b32_read.py
E['test_b32_read.py'] = [
    ('head',
     '"""F20l2 (HPP-648): fixtures of b32_read.py - every class and edge of item 550 (g), RC6, RC7, RC13, INSTR_MADE, K_I, the members of\n',
     '"""F20l2 (HPP-648): fixtures of b32_read.py - the rule of item 574 (d) and the kinds / classes of item 581 (v)(5) (one fixture per kind,\n'
     'emu_join included), the record peer of item 581 (v)(2), theta_load from the seal, ring_hold_w, the gpusleep stand member of item 574 (v)(2);\n'
     'and as in F20l: every class and edge of item 550 (g), RC6, RC7, RC13, INSTR_MADE, K_I, the members of\n'),
    ('w line',
     "    for w in waits or []:\n"
     "        out.append('DiagB32-w: n=%d slot=%d tid=0 kind=%s obj=0x1 start_us=0 wait_us=%d overlap_us=%d waker=%d waker_tid=0 req_us=0 to=%d '\n"
     "                   'open=0' % (n, w['slot'], w['kind'], w.get('wait', 50000), w.get('overlap', 50000), w.get('waker', -1), w.get('to', 0)))\n",
     "    for w in waits or []:\n"
     "        out.append('DiagB32-w: n=%d slot=%d tid=0 kind=%s obj=0x1 start_us=0 wait_us=%d overlap_us=%d waker=%d waker_tid=0 req_us=%d to=%d '\n"
     "                   'open=0 peer=%d peer_tid=0' % (n, w['slot'], w['kind'], w.get('wait', 50000), w.get('overlap', 50000), w.get('waker', -1),\n"
     "                                                w.get('req', 0), w.get('to', 0), w.get('peer', -1)))\n"),
    ('x line',
     "                   'others_cut=0 w_cut=0 rep_drop=%d kq_fail=0 print_us=10 gap3p=0' % (\n"
     "                       n, c['slot_full'], z['slot_full_w'], c['torn'], z['torn_w'], c['ring_drop'], z['ring_drop_w'], c['sgap_bad'],\n"
     "                       z['sgap_bad_w'], c['lines_cut'], z['lines_cut_w'], c['req_miss'], z['req_miss_w'], c['sub_miss'], z['sub_miss_w'],\n"
     "                       (cum or {}).get('rep_drop', 0)))\n",
     "                   'others_cut=0 w_cut=0 rep_drop=%d kq_fail=0 print_us=10 gap3p=0 ring_hold=%d ring_hold_w=%d' % (\n"
     "                       n, c['slot_full'], z['slot_full_w'], c['torn'], z['torn_w'], c['ring_drop'], z['ring_drop_w'], c['sgap_bad'],\n"
     "                       z['sgap_bad_w'], c['lines_cut'], z['lines_cut_w'], c['req_miss'], z['req_miss_w'], c['sub_miss'], z['sub_miss_w'],\n"
     "                       (cum or {}).get('rep_drop', 0), ring_hold, ring_hold))\n"),
    ('diag sig',
     "               flip=2, threads=None, waits=None, xw=None, x=True, hdr=True, cum=None):\n",
     "               flip=2, threads=None, waits=None, xw=None, x=True, hdr=True, cum=None, ring_hold=0):\n"),
    ('build sig',
     "          dt_by_idx=None, seed=None):\n",
     "          dt_by_idx=None, seed=None, stand_mode='present'):\n"),
    ('build stand',
     "            lines.append('TestB32: armed delay_s=60 mode=present ms=200\\n')\n"
     "            lines.append('TestB32: fire mode=present ms=200\\n')\n"
     "            lines.append('TestB32: done mode=present slept_us=200000\\n')\n",
     "            lines.append('TestB32: armed delay_s=60 mode=%s ms=200\\n' % stand_mode)\n"
     "            lines.append('TestB32: fire mode=%s ms=200\\n' % stand_mode)\n"
     "            lines.append('TestB32: done mode=%s slept_us=200000\\n' % stand_mode)\n"),
    ('w_nowaker note',
     "check('W record waker -1 -> GUEST_SLEEP:sem', f['cls'] == 'GUEST_SLEEP:sem', f['cls'])\n",
     "check('W record waker -1 -> GUEST_SLEEP:sem', f['cls'] == 'GUEST_SLEEP:sem', f['cls'])\n"
     "\n"
     "# ---- item 574 (d), item 581 (v)(2), (v)(5): waker, record peer, EMU_WAIT / GUEST_SLEEP by kind\n"
     "GPU_SW = thr(1, 'Gpu', 'Gpu', Sw=S)\n"
     "f = w_case('d_waker', thr(2, 'DrawThread', 'guest', W={'gpu_wait': S}), [], [dict(slot=2, kind='gpu_wait', waker=1)], gpu=GPU_SW)\n"
     "check('(d) EMU kind with a waker -> step to the waker -> UNMARKED:Gpu', f['cls'] == 'UNMARKED:Gpu' and f['path'][0].endswith('->waker'),\n"
     "      (f['cls'], f['path']))\n"
     "f = w_case('d_peer', thr(2, 'DrawThread', 'guest', W={'gpu_wait': S}), [], [dict(slot=2, kind='gpu_wait', waker=-1, peer=1)], gpu=GPU_SW)\n"
     "check('(d) EMU kind without a waker, record peer 1 -> step to the peer -> UNMARKED:Gpu', f['cls'] == 'UNMARKED:Gpu' and\n"
     "      f['path'][0].endswith('->peer') and len(f['path']) == 2, (f['cls'], f['path']))\n"
     "f = w_case('d_peer0', thr(2, 'DrawThread', 'guest', W={'gpu_wait': S}), [], [dict(slot=2, kind='gpu_wait', waker=-1, peer=0)])\n"
     "check('(d) record peer 0 is a slot (>= 0) -> step to slot 0 (Present S) -> UNMARKED:Present', f['cls'] == 'UNMARKED:Present', f['cls'])\n"
     "f = w_case('d_both', thr(2, 'DrawThread', 'guest', W={'gpu_wait': S}), [thr(3, 'Physics', 'guest', R=S)],\n"
     "           [dict(slot=2, kind='gpu_wait', waker=3, peer=1)], gpu=GPU_SW)\n"
     "check('(d) the waker goes before the record peer', f['cls'] == 'GUEST_RUN:Physics', f['cls'])\n"
     "f = w_case('d_cond_peer', thr(2, 'DrawThread', 'guest', W={'cond': S}), [thr(3, 'Physics', 'guest', R=S)],\n"
     "           [dict(slot=2, kind='cond', waker=-1, peer=3)])\n"
     "check('(d) the record peer step is general (GUEST kind cond) -> GUEST_RUN:Physics', f['cls'] == 'GUEST_RUN:Physics', f['cls'])\n"
     "f = w_case('d_emu_none', thr(2, 'DrawThread', 'guest', W={'gpu_wait': S}), [], [dict(slot=2, kind='gpu_wait', waker=-1, peer=-1)],\n"
     "           gpu=thr(1, 'Gpu', 'Gpu', R=S))\n"
     "check('(d) EMU kind without waker and peer -> EMU_WAIT:gpu_wait (no RC6 with GuestGpu R)', f['cls'] == 'EMU_WAIT:gpu_wait' and\n"
     "      f['family'] == 'EMU_WAIT', (f['cls'], f['family']))\n"
     "f = w_case('d_emu_norec', thr(2, 'DrawThread', 'guest', W={'flip_done': S}))\n"
     "check('(d) EMU kind without a record -> EMU_WAIT:flip_done', f['cls'] == 'EMU_WAIT:flip_done', f['cls'])\n"
     "f = w_case('d_emu_tpeer', thr(2, 'DrawThread', 'guest', W={'emu_mutex': S}, peer=5), [thr(5, 'Loader', 'guest', R=S)])\n"
     "check('(d) emu_mutex without a record: -t peer only as the executor variant -> EMU_WAIT:emu_mutex',\n"
     "      f['cls'] == 'EMU_WAIT:emu_mutex' and 'executor variant (the -t peer for any kind): step to slot 5' in f['note'], (f['cls'], f['note']))\n"
     "f = w_case('d_mutex_tpeer', thr(2, 'DrawThread', 'guest', W={'mutex': S}, peer=5), [thr(5, 'Loader', 'guest', R=S)],\n"
     "           [dict(slot=2, kind='mutex', waker=-1, peer=-1)])\n"
     "check('(d) mutex record without waker and peer -> the -t peer as before -> GUEST_RUN:Loader', f['cls'] == 'GUEST_RUN:Loader' and\n"
     "      f['path'][0].endswith('->tpeer'), (f['cls'], f['path']))\n"
     "f = w_case('d_emu_to0', thr(2, 'DrawThread', 'guest', W={'vo_pace': S}), [], [dict(slot=2, kind='vo_pace', waker=-1, to=1, req=0)])\n"
     "check('RC5 (v): EMU kind timeout without a guest deadline (req_us 0) -> EMU_WAIT, the other reading printed',\n"
     "      f['cls'] == 'EMU_WAIT:vo_pace' and 'GUEST_SLEEP:vo_pace' in f['note'], (f['cls'], f['note']))\n"
     "f = w_case('d_emu_to1', thr(2, 'DrawThread', 'guest', W={'net': S}), [thr(3, 'X', 'guest', R=S)],\n"
     "           [dict(slot=2, kind='net', waker=3, to=1, req=16000)])\n"
     "check('RC5 (v): EMU kind timeout with a guest deadline (req_us > 0) -> GUEST_SLEEP:net', f['cls'] == 'GUEST_SLEEP:net', f['cls'])\n"
     "f = w_case('d_emu_to_wk', thr(2, 'DrawThread', 'guest', W={'gpu_wait': S}), [thr(3, 'X', 'guest', R=S)],\n"
     "           [dict(slot=2, kind='gpu_wait', waker=3, to=1, req=0)])\n"
     "check('RC5 (v): EMU kind timeout, req_us 0, waker 3 -> step -> GUEST_RUN:X', f['cls'] == 'GUEST_RUN:X', f['cls'])\n"
     "f = w_case('d_vblank_peer', thr(2, 'DrawThread', 'guest', W={'vblank': S}), [], [dict(slot=2, kind='vblank', waker=-1, peer=0)])\n"
     "check('vblank with peer = Present -> step to Present (S) -> UNMARKED:Present', f['cls'] == 'UNMARKED:Present', f['cls'])\n"
     "f = w_case('d_selfpeer', thr(2, 'DrawThread', 'guest', W={'gpu_wait': S}), [], [dict(slot=2, kind='gpu_wait', waker=-1, peer=2)])\n"
     "check('a record peer equal to its own slot -> cycle -> UNDETERMINED', f['cls'] == 'UNDETERMINED' and 'cycle' in f['note'], (f['cls'], f['note']))\n"
     "EMU_KINDS = ('emu_mutex', 'gpu_wait', 'gpu_cmd', 'flip_slot', 'flip_done', 'flip_cancel', 'flip_req', 'vo_pace', 'relay', 'frame_pool',\n"
     "             'rec_wait', 'rec_idle', 'asub_idle', 'asub_drain', 'ops_wait', 'ops_idle', 'pipe_wait', 'pcopy', 'pm_drain', 'vma_flush',\n"
     "             'rec_queue', 'main_task', 'main_idle', 'spin', 'av', 'vblank', 'audio', 'aio', 'net', 'emu_join')\n"
     "GUEST_KINDS = ('cond', 'mutex', 'sem', 'psem', 'evf', 'eq', 'once', 'join', 'addr', 'fiber', 'ult', 'rwlock')\n"
     "check('EMU_WAITS = the list of item 574 (d) and 581 (v)(5) (30 kinds)', set(R.EMU_WAITS) == set(EMU_KINDS) and len(R.EMU_WAITS) == 30,\n"
     "      sorted(set(R.EMU_WAITS) ^ set(EMU_KINDS)))\n"
     "check('GUEST_WAITS = the older kinds + once, join, addr, fiber, ult, rwlock', set(R.GUEST_WAITS) == set(GUEST_KINDS) | {'sleep', 'gpu_idle',\n"
     "      'gpu_regmem'}, sorted(R.GUEST_WAITS))\n"
     "check('every kind is EMU or GUEST, not both', set(R.WAITS) == set(R.EMU_WAITS) | set(R.GUEST_WAITS) and not set(R.EMU_WAITS) & set(R.GUEST_WAITS))\n"
     "for k in EMU_KINDS:\n"
     "    f = w_case('k_' + k, thr(2, 'DrawThread', 'guest', W={k: S}), [], [dict(slot=2, kind=k, waker=-1, peer=-1)])\n"
     "    check('kind %s without waker and peer -> EMU_WAIT:%s' % (k, k), f['cls'] == 'EMU_WAIT:' + k and f['family'] == 'EMU_WAIT', f['cls'])\n"
     "for k in GUEST_KINDS:\n"
     "    f = w_case('k_' + k, thr(2, 'DrawThread', 'guest', W={k: S}), [], [dict(slot=2, kind=k, waker=-1, peer=-1)])\n"
     "    check('kind %s without waker and peer -> GUEST_SLEEP:%s' % (k, k), f['cls'] == 'GUEST_SLEEP:' + k and f['family'] == 'GUEST_SLEEP', f['cls'])\n"
     "    f = w_case('kp_' + k, thr(2, 'DrawThread', 'guest', W={k: S}), [thr(3, 'Physics', 'guest', R=S)], [dict(slot=2, kind=k, waker=-1, peer=3)])\n"
     "    check('kind %s with a record peer -> step -> GUEST_RUN:Physics' % k, f['cls'] == 'GUEST_RUN:Physics', f['cls'])\n"
     "f = w_case('k_join_rc6', thr(2, 'DrawThread', 'guest', W={'join': S}), [], [dict(slot=2, kind='join', waker=-1)], gpu=thr(1, 'Gpu', 'Gpu', R=S))\n"
     "check('GUEST kind join keeps RC6 -> GUEST_POLL', f['cls'] == 'GUEST_POLL', f['cls'])\n"
     "# the kind names against the enum of the reviewed code (WaitName of 4371ff4b, = f2307b02 byte for byte)\n"
     "_src = subprocess.run(['C:/Program Files/Git/cmd/git.exe', '-C', 'C:/kyty/KytyPS5', 'show', '4371ff4b:src/common/diagB32.cpp'],\n"
     "                      capture_output=True).stdout.decode('utf-8', 'replace')\n"
     "_i = _src.find('const char* WaitName(uint8_t kind) {')\n"
     "_blk = _src[_i:_src.find('static_assert', _i)]\n"
     "import re as _re  # noqa: E402\n"
     "_names = _re.findall(r'\"([a-z_]+|-)\"', _blk)\n"
     "check('WAITS = WaitName of 4371ff4b in order (45 kinds)', _names[1:] == list(R.WAITS) and len(R.WAITS) == 45, (_names[1:4], len(_names)))\n"
     "_h = subprocess.run(['C:/Program Files/Git/cmd/git.exe', '-C', 'C:/kyty/KytyPS5', 'show', '4371ff4b:src/common/diagB32.h'],\n"
     "                    capture_output=True).stdout.decode('utf-8', 'replace')\n"
     "_j = _h.find('constexpr bool IsEmuWait(uint8_t kind) {')\n"
     "_emu = _h[_j:_h.find('}', _j)]\n"
     "check('IsEmuWait of 4371ff4b: EmuMutex .. Av plus Vblank, Audio, Aio, Net, EmuJoin', all('Wait::%s)' % k in _emu for k in\n"
     "      ('Vblank', 'Audio', 'Aio', 'Net', 'EmuJoin')) and 'kind >= kFirstEmuWait && kind < kFirstGuestHleWait' in _emu and\n"
     "      _emu.count('Wait::') == 5, _emu[:200])\n"),
    ('ring + theta + stand',
     "# ---- stand and load windows\n",
     "# ---- ring_hold_w (Z1): reference, not a member of NO_SAMPLES\n"
     "res = read('ring', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, ring_hold=3, threads=GUEST_R)),\n"
     "                          T0 + 40: dict(dt=200000, diag=diag_block(FIRST + T0 + 40, 200000, threads=GUEST_R))}))\n"
     "check('ring_hold_w 3 is not NO_SAMPLES', frame(res, T0)['cls'] == 'GUEST_RUN:DrawThread' and frame(res, T0)['ring_hold_w'] == 3,\n"
     "      (frame(res, T0)['cls'], frame(res, T0).get('ring_hold_w')))\n"
     "check('ring_hold_w sum 3, frames 1, -x lines with the field 2', res['ring_hold_w_sum'] == 3 and res['ring_hold_w_frames'] == 1 and\n"
     "      res['ring_hold_w_field'] == 2, (res['ring_hold_w_sum'], res['ring_hold_w_frames'], res['ring_hold_w_field']))\n"
     "# ---- theta_load from the seal\n"
     "_td = os.path.join(TMP, 'theta')\n"
     "os.makedirs(_td, exist_ok=True)\n"
     "for txt, want in (('x\\ntheta_load: 0.4562\\ny\\n', 0.4562), ('theta_load: 0.4562\\r\\n', 0.4562), ('no line\\n', None),\n"
     "                  ('theta_load: 0.4562\\ntheta_load: 0.5\\n', None), ('theta_load: 0,4562\\n', None), (' theta_load: 0.4562\\n', None)):\n"
     "    open(os.path.join(_td, 's.md'), 'wb').write(txt.encode('ascii'))\n"
     "    check('read_theta %r -> %s' % (txt[:30], want), R.read_theta(os.path.join(_td, 's.md')) == want, R.read_theta(os.path.join(_td, 's.md')))\n"
     "check('read_theta of a missing file -> None', R.read_theta(os.path.join(_td, 'none.md')) is None)\n"
     "_body = os.path.join(HERE, 'f20l2_seal_body.md')\n"
     "check('the seal body carries theta_load 0.4562 (item 574 (b)(6))', R.read_theta(_body) == 0.4562, R.read_theta(_body))\n"
     "# ---- the gpusleep stand member of item 574 (v)(2): GuestGpu step with Sw or S >= 50 %\n"
     "THR_PC = [thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', Sw=S), thr(2, 'DrawThread', 'guest', W={'gpu_wait': S})]\n"
     "res = read('stand_pc', build({T0 + 1: dict(dt=230000, diag=diag_block(FIRST + T0 + 1, 230000, instr=0, threads=THR_PC,\n"
     "                                                                     waits=[dict(slot=2, kind='gpu_wait', waker=-1, peer=1)]))},\n"
     "                             test_fire_idx=T0 + 1, stand_mode='gpusleep'))\n"
     "st = res['stand'][0]\n"
     "check('stand pc: flip holder W:gpu_wait -> peer GuestGpu Sw -> UNMARKED:Gpu, member yes', st['cls'] == 'UNMARKED:Gpu' and\n"
     "      st['holder'] == 'flip' and st['gpu_in_chain'] and st['gpu_sw_or_s50'] and [s['how'] for s in st['steps']] == ['holder', 'peer'], st)\n"
     "check('stand pc: -w records printed with peer', st['w'] and st['w'][0]['peer'] == 1 and st['w'][0]['kind'] == 'gpu_wait', st['w'])\n"
     "THR_PC2 = [thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', Sw=S // 2 - 1, S=S // 2 - 1, r=2),\n"
     "           thr(2, 'DrawThread', 'guest', W={'gpu_wait': S})]\n"
     "res = read('stand_pc2', build({T0 + 1: dict(dt=230000, diag=diag_block(FIRST + T0 + 1, 230000, instr=0, threads=THR_PC2,\n"
     "                                                                      waits=[dict(slot=2, kind='gpu_wait', waker=1)]))},\n"
     "                              test_fire_idx=T0 + 1, stand_mode='gpusleep'))\n"
     "st = res['stand'][0]\n"
     "check('stand pc: GuestGpu Sw 19 + S 19 of 40 -> member no by the letter, variant Sw + S yes', st['gpu_in_chain'] and\n"
     "      not st['gpu_sw_or_s50'] and st['gpu_sw_plus_s50'], st)\n"
     "res = read('stand_pc3', build({T0 + 1: dict(dt=230000, diag=diag_block(FIRST + T0 + 1, 230000, instr=0,\n"
     "                                                                      threads=[thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', Sw=S),\n"
     "                                                                               thr(2, 'DrawThread', 'guest', W={'gpu_wait': S})]))},\n"
     "                              test_fire_idx=T0 + 1, stand_mode='gpusleep'))\n"
     "st = res['stand'][0]\n"
     "check('stand pc: no waker, no peer -> EMU_WAIT:gpu_wait, GuestGpu not in the chain', st['cls'] == 'EMU_WAIT:gpu_wait' and\n"
     "      not st['gpu_in_chain'] and not st['gpu_sw_or_s50'], st)\n"
     "\n"
     "# ---- stand and load windows\n"),
    ('adm seal default',
     "            seal_text='seal\\n'):\n",
     "            seal_text='seal\\ntheta_load: 0.4562\\n'):\n"),
    ('adm call',
     "    return R.read_tag(tag, R.paths(tag, d), None)\n",
     "    return R.read_tag(tag, R.paths(tag, d))\n"),
    ('adm block',
     "r = adm_dir('pd', 'b32_pd', R.FORM['b32_pd'], log_on, load=dict(status='done', mode='all', n_start=1, n_end=2))\n"
     "check('admission pd PASS', r['admitted'], [a for a in r['admission'] if not a[1]])\n"
     "r = adm_dir('pd_noload', 'b32_pd', R.FORM['b32_pd'], log_on)\n"
     "check('admission pd without the loader FAIL', not r['admitted'])\n"
     "r = adm_dir('pd2_wrongmode', 'b32_pd2', R.FORM['b32_pd2'], log_on, load=dict(status='done', mode='all', n_start=1, n_end=2))\n"
     "check('admission pd2 with the loader mode all FAIL', not r['admitted'])\n",
     "B2 = R.BIN_F20J2\n"
     "LD = dict(status='done', mode='all', n_start=1, n_end=2)\n"
     "r = adm_dir('pd', 'b32_pd', R.FORM['b32_pd'], log_on, binary=B2, load=LD)\n"
     "check('admission pd (reference reread, F20j2 binary) PASS', r['admitted'], [a for a in r['admission'] if not a[1]])\n"
     "r = adm_dir('pd_newbin', 'b32_pd', R.FORM['b32_pd'], log_on, load=LD)\n"
     "check('admission pd with the F20j4 binary FAIL', not r['admitted'])\n"
     "r = adm_dir('pp_oldbin', 'b32_ppb', R.FORM['b32_ppb'], log_pp, binary=B2)\n"
     "check('admission ppb with the F20j2 binary FAIL', not r['admitted'])\n"
     "r = adm_dir('pd_noload', 'b32_pd', R.FORM['b32_pd'], log_on, binary=B2)\n"
     "check('admission pd without the loader FAIL', not r['admitted'])\n"
     "r = adm_dir('nothe', 'b32_z0b', R.FORM['b32_z0b'], log_off, seal_text='seal\\n')\n"
     "check('admission: no theta_load line in the seal FAIL, the log is not read', not r['admitted'] and r['log'] is None)\n"
     "check('tag b32_pd2 refused (PK-D2 not repeated, item 574 (e))', R.TAG_RX.match('b32_pd2') is None and 'b32_pd2' not in R.FORM)\n"
     "LOG_PC = build({}, pre=[MODE + '\\n'], test_fire_idx=T0, stand_mode='gpusleep')\n"
     "r = adm_dir('pc', 'b32_pcb', R.FORM['b32_pcb'], LOG_PC)\n"
     "check('admission pcb with gpusleep stand lines PASS', r['admitted'], [a for a in r['admission'] if not a[1]])\n"
     "check('theta in the reading = 0.4562 from the seal', r['theta'] == 0.4562, r['theta'])\n"),
    ('adm pd_stand',
     "r = adm_dir('pd_stand', 'b32_pd', R.FORM['b32_pd'], log_pp, load=dict(status='done', mode='all', n_start=1, n_end=2))\n",
     "r = adm_dir('pd_stand', 'b32_pd', R.FORM['b32_pd'], log_pp, binary=B2, load=LD)\n"),
    ('adm rest',
     "r = adm_dir('bin_fs8', 'b32_pd', R.FORM['b32_pd'], log_on, binary=FS8, load=dict(status='done', mode='all', n_start=1, n_end=2))\n"
     "check('admission: json binary FS8 (not the test binary) FAIL', not r['admitted'])\n"
     "r = adm_dir('inst_after', 'b32_pd', R.FORM['b32_pd'], log_on, inst_a=TB, load=dict(status='done', mode='all', n_start=1, n_end=2))\n"
     "check('admission: installed after = test binary FAIL', not r['admitted'])\n"
     "r = adm_dir('env_extra', 'b32_pd', dict(R.FORM['b32_pd'], KYTY_X='1'), log_on, load=dict(status='done', mode='all', n_start=1, n_end=2))\n"
     "check('admission: extra env FAIL', not r['admitted'])\n"
     "r = adm_dir('env_nowall', 'b32_pd', dict(KYTY_DIAG_B32='1'), log_on, load=dict(status='done', mode='all', n_start=1, n_end=2))\n"
     "check('admission: no KYTY_GPU_WALL FAIL', not r['admitted'])\n",
     "r = adm_dir('bin_fs8', 'b32_z0b', R.FORM['b32_z0b'], log_off, binary=FS8)\n"
     "check('admission: json binary FS8 (not the test binary) FAIL', not r['admitted'])\n"
     "r = adm_dir('inst_after', 'b32_z0b', R.FORM['b32_z0b'], log_off, inst_a=TB)\n"
     "check('admission: installed after = test binary FAIL', not r['admitted'])\n"
     "r = adm_dir('env_extra', 'b32_z0b', dict(R.FORM['b32_z0b'], KYTY_X='1'), log_off)\n"
     "check('admission: extra env FAIL', not r['admitted'])\n"
     "r = adm_dir('env_nowall', 'b32_z0b', dict(KYTY_DIAG_B32='0'), log_off)\n"
     "check('admission: no KYTY_GPU_WALL FAIL', not r['admitted'])\n"),
    ('adm repdrop',
     "r = adm_dir('repdrop', 'b32_pd', R.FORM['b32_pd'], rd, load=dict(status='done', mode='all', n_start=1, n_end=2))\n"
     "check('admission: rep_drop != 0 FAIL', not r['admitted'] and r['log']['rep_drop'] == 1)\n"
     "r = adm_dir('repeat', 'b32_pd_r1', R.FORM['b32_pd'], log_on, load=dict(status='done', mode='all', n_start=1, n_end=2))\n"
     "check('a repeat name b32_pd_r1 reads with the form of b32_pd', r['admitted'] and r['form'] == 'b32_pd')\n"
     "check('tag name b32_pd_r7 refused', R.TAG_RX.match('b32_pd_r7') is None and R.TAG_RX.match('b32_px') is None)\n",
     "r = adm_dir('repdrop', 'b32_pd', R.FORM['b32_pd'], rd, binary=B2, load=LD)\n"
     "check('admission: rep_drop != 0 FAIL', not r['admitted'] and r['log']['rep_drop'] == 1)\n"
     "r = adm_dir('repeat', 'b32_z0b_r1', R.FORM['b32_z0b'], log_off)\n"
     "check('a repeat name b32_z0b_r1 reads with the form of b32_z0b', r['admitted'] and r['form'] == 'b32_z0b')\n"
     "check('tag name b32_z0b_r7 refused', R.TAG_RX.match('b32_z0b_r7') is None and R.TAG_RX.match('b32_px') is None and\n"
     "      R.TAG_RX.match('b32_z0') is None)\n"
     "# paths of the reference reread: b32_pd reads the F20l files with the F20l seal and theta from the F20l2 seal\n"
     "_p = R.paths('b32_pd')\n"
     "check('paths b32_pd: F20l log and seal, theta from the F20l2 seal', _p['log'].replace('\\\\', '/') == 'C:/kyty/f287/f20l/log_b32_pd.txt' and\n"
     "      _p['seal'] == R.SEAL_F20L and _p['theta_src'] == R.SEAL_PATH, _p)\n"
     "_p = R.paths('b32_pcb')\n"
     "check('paths b32_pcb: F20l2 files and seal', _p['log'].replace('\\\\', '/') == 'C:/kyty/f287/f20l2/log_b32_pcb.txt' and\n"
     "      _p['seal'] == R.SEAL_PATH, _p)\n"),
]

# ------------------------------------------------------------------ sens_b32.py
E['sens_b32.py'] = [
    ('head', '"""F20l2 (HPP-648): manual sensitivity', '"""F20l2 (HPP-648; port of F20l sens_b32.py with the edits of item 574 (d), 581 (v)): manual sensitivity'),
    ('load theta 0.75',
     "    ('load without theta at 0.75', \"    if theta is not None and ncpu and win\", \"    theta = 0.75 if theta is None else theta\\n    if theta is not None and ncpu and win\"),\n",
     "    ('load without theta at 0.75', \"    if theta is not None and ncpu and win\", \"    theta = 0.75 if theta is None else theta\\n    if theta is not None and ncpu and win\"),\n"
     "    ('theta not from the seal', \"    theta = read_theta(p['theta_src'])\\n\", \"    theta = 0.5\\n\"),\n"
     "    ('theta line with leading text', \"THETA_RX = re.compile(r'^theta_load:\", \"THETA_RX = re.compile(r'theta_load:\"),\n"
     "    ('theta two lines first wins', \"    return float(m[0]) if len(m) == 1 else None\", \"    return float(m[0]) if m else None\"),\n"
     "    ('log read without theta', \"if os.path.exists(p['log']) and theta is not None else None\", \"if os.path.exists(p['log']) else None\"),\n"
     "    ('theta not an admission member', \"('theta_load from the seal %s (%s)' % (p['theta_src'], theta), theta is not None),\",\n"
     "     \"('theta_load from the seal %s (%s)' % (p['theta_src'], theta), True),\"),\n"
     "    ('emu kinds as guest', \"            emu = x in EMU_WAITS\\n\", \"            emu = False\\n\"),\n"
     "    ('all kinds emu', \"            emu = x in EMU_WAITS\\n\", \"            emu = x != 'sleep'\\n\"),\n"
     "    ('vblank not emu', \"EMU_WAITS = WAITS[9:34] + ('vblank', 'audio', 'aio', 'net', 'emu_join')\", \"EMU_WAITS = WAITS[9:34] + ('audio', 'aio', 'net', 'emu_join')\"),\n"
     "    ('emu_join not emu', \"EMU_WAITS = WAITS[9:34] + ('vblank', 'audio', 'aio', 'net', 'emu_join')\", \"EMU_WAITS = WAITS[9:34] + ('vblank', 'audio', 'aio', 'net')\"),\n"
     "    ('av not emu', \"EMU_WAITS = WAITS[9:34] + \", \"EMU_WAITS = WAITS[9:33] + \"),\n"
     "    ('emu_mutex not emu', \"EMU_WAITS = WAITS[9:34] + \", \"EMU_WAITS = WAITS[10:34] + \"),\n"
     "    ('join emu', \"EMU_WAITS = WAITS[9:34] + ('vblank', 'audio', 'aio', 'net', 'emu_join')\", \"EMU_WAITS = WAITS[9:34] + ('vblank', 'audio', 'aio', 'net', 'emu_join', 'join')\"),\n"
     "    ('kind order swapped', \"'vblank', 'once', 'join', 'addr', 'aio',\", \"'vblank', 'join', 'once', 'addr', 'aio',\"),\n"
     "    ('record peer not used', \"            elif rp is not None and rp >= 0:\\n\", \"            elif False:\\n\"),\n"
     "    ('peer before waker', \"            if wk is not None and wk >= 0:\\n                target, how = wk, 'waker'\\n            elif rp is not None and rp >= 0:\\n                target, how = rp, 'peer'\\n\",\n"
     "     \"            if rp is not None and rp >= 0:\\n                target, how = rp, 'peer'\\n            elif wk is not None and wk >= 0:\\n                target, how = wk, 'waker'\\n\"),\n"
     "    ('record peer > 0', \"            elif rp is not None and rp >= 0:\\n\", \"            elif rp is not None and rp > 0:\\n\"),\n"
     "    ('timeout ignores req_us', \"            if to and (not emu or (num(best.get('req_us'), 0) or 0) > 0):\", \"            if to:\"),\n"
     "    ('timeout on emu ignored', \"            if to and (not emu or (num(best.get('req_us'), 0) or 0) > 0):\", \"            if to and not emu:\"),\n"
     "    ('EMU_WAIT through RC6', \"                    return 'EMU_WAIT:%s' % x, 'EMU_WAIT', path, role,\",\n"
     "     \"                    c, fam, note = guest_check('EMU_WAIT:%s' % x)\\n                    return c, fam, path, role,\"),\n"
     "    ('tpeer variant off', \"                var = ('; executor variant (the -t peer for any kind): step to slot %d' % pr) if pr is not None and pr >= 0 else ''\",\n"
     "     \"                var = ''\"),\n"
     "    ('tpeer for any kind', \"            elif x == 'mutex' and pr is not None and pr >= 0:\", \"            elif pr is not None and pr >= 0:\"),\n"
     "    ('to variant off', \"                    var += '; executor variant (RC5 (v) to = 1 for every kind): GUEST_SLEEP:%s' % x\", \"                    pass\"),\n"
     "    ('gpu member S off', \"gpu_sw_or_s50=any(s['Sw'] >= 0.5 * s['samples'] or s['S'] >= 0.5 * s['samples'] for s in gpu_steps)\",\n"
     "     \"gpu_sw_or_s50=any(s['Sw'] >= 0.5 * s['samples'] for s in gpu_steps)\"),\n"
     "    ('gpu member Sw + S', \"gpu_sw_or_s50=any(s['Sw'] >= 0.5 * s['samples'] or s['S'] >= 0.5 * s['samples'] for s in gpu_steps)\",\n"
     "     \"gpu_sw_or_s50=any(s['Sw'] + s['S'] >= 0.5 * s['samples'] for s in gpu_steps)\"),\n"
     "    ('gpu member any thread', \"    gpu_steps = [s for s in steps if s['slot'] == gs]\", \"    gpu_steps = list(steps)\"),\n"
     "    ('ring_hold_w sum off', \"    res['ring_hold_w_sum'] = sum(num((d['x'] or {}).get('ring_hold_w'), 0) or 0 for d in diag.values())\",\n"
     "     \"    res['ring_hold_w_sum'] = sum(num((d['x'] or {}).get('ring_hold'), 0) or 0 for d in diag.values())\"),\n"
     "    ('ring_hold_w zero invariant', \"'lines_cut_w', 'req_miss_w', 'sub_miss_w')\", \"'lines_cut_w', 'req_miss_w', 'sub_miss_w', 'ring_hold_w')\"),\n"
     "    ('pd ref with the new binary', \"    want_bin = BIN_F20J2 if base_tag == 'b32_pd' else BIN_TEST\", \"    want_bin = BIN_TEST\"),\n"
     "    ('pd ref paths in f20l2', \"    gg, seal = (G_F20L, SEAL_F20L) if\", \"    gg, seal = (G, SEAL_PATH) if\"),\n"
     "    ('pd2 allowed', \"TAG_RX = re.compile(r'^(b32_z0b|b32_ppb|b32_pcb|b32_pd)(_r[1-6])?$')\", \"TAG_RX = re.compile(r'^(b32_z0b|b32_ppb|b32_pcb|b32_pd|b32_pd2)(_r[1-6])?$')\"),\n"),
    ('timeout record steps',
     "    ('timeout record steps', \"            if best is not None and best.get('to') == 1:\", \"            if False:\"),\n",
     "    ('timeout record steps', \"            if to and (not emu or (num(best.get('req_us'), 0) or 0) > 0):\", \"            if False:\"),\n"),
    ('admission binary',
     "    ('admission binary not checked', \"jbin == BIN_TEST),\", \"True),\"),\n",
     "    ('admission binary not checked', \"jbin == want_bin),\", \"True),\"),\n"),
    ('copy body',
     "    shutil.copy2(os.path.join(HERE, 'f20e_read.py'), os.path.join(d, 'f20e_read.py'))\n",
     "    shutil.copy2(os.path.join(HERE, 'f20e_read.py'), os.path.join(d, 'f20e_read.py'))\n"
     "    shutil.copy2(os.path.join(HERE, 'f20l2_seal_body.md'), os.path.join(d, 'f20l2_seal_body.md'))\n"),
]

# ------------------------------------------------------------------ chain scripts: no pd / pd2 tags
TAGS_OLD = '  b32_z0b|b32_ppb|b32_pcb|b32_pd|b32_pd2|b32_z0b_r[1-6]|b32_ppb_r[1-6]|b32_pcb_r[1-6]|b32_pd_r[1-6]|b32_pd2_r[1-6]) ;;\n'
TAGS_NEW = '  b32_z0b|b32_ppb|b32_pcb|b32_z0b_r[1-6]|b32_ppb_r[1-6]|b32_pcb_r[1-6]) ;;\n'
E['go_f20l2.sh'] = [
    ('tags', TAGS_OLD, TAGS_NEW),
    ('usage', '  *) echo "usage: go_f20l2.sh b32_z0b|b32_ppb|b32_pcb|b32_pd|b32_pd2[_r1..6]"; exit 2;;\n',
     '  *) echo "usage: go_f20l2.sh b32_z0b|b32_ppb|b32_pcb[_r1..6]"; exit 2;;\n'),
    ('head', '# Track F link F20l2 (HPP-648; ROADMAP s122 item 550 (d), (z); item 552 (d), item 554 (d)): one KYTY_DIAG_B32 control tag of the form of\n',
     '# Track F link F20l2 (HPP-648; ROADMAP s122 item 574 (e), item 581 (zh), item 584 (g); form of item 550 (d)(1)-(3)): one KYTY_DIAG_B32 control tag of the form of\n'),
    ('tags doc', '# usage: bash C:/kyty/f287/f20l2/go_f20l2.sh <tag>   tags: b32_z0b b32_ppb b32_pcb b32_pd b32_pd2, repeats <tag>_r1.._r6 (item 550 (z)(4))\n',
     '# usage: bash C:/kyty/f287/f20l2/go_f20l2.sh <tag>   tags: b32_z0b b32_ppb b32_pcb, repeats <tag>_r1.._r6 (item 550 (z)(4)); PK-D / PK-D2 are not\n'
     '#   repeated (item 574 (e)) - the loader branch below is not reached by any tag\n'),
]
E['launch_f20l2.sh'] = [
    ('tags', TAGS_OLD, TAGS_NEW),
    ('usage', '  *) echo "usage: launch_f20l2.sh b32_z0b|b32_ppb|b32_pcb|b32_pd|b32_pd2[_r1..6]"; exit 2;;\n',
     '  *) echo "usage: launch_f20l2.sh b32_z0b|b32_ppb|b32_pcb[_r1..6]"; exit 2;;\n'),
]
E['post_f20l2.sh'] = [
    ('tags', TAGS_OLD, TAGS_NEW),
    ('doc', '# lead sheet sheet142.py of the whole video, written BEFORE the reader (the reader reads them); then b32_read.py rows and json (no theta:\n'
            '# HOST_LOAD is not issued in the controls, item 550 (d)(6)), then the table b32_read.py --table.  Refuses under any lock (general rule 27)\n',
     '# lead sheet sheet142.py of the whole video, written BEFORE the reader (the reader reads them); then b32_read.py rows and json (theta_load\n'
     '# from the seal, item 574 (b)(6), (e)), then the table b32_read.py --table.  Refuses under any lock (general rule 27)\n'),
]
E['test_guard_f20l2.py'] = [
    ('launch tag', "    p = subprocess.run([BASH, os.path.join(HERE, 'launch_f20l2.sh'), 'b32_pd'], capture_output=True, text=True, env=LENV)\n",
     "    p = subprocess.run([BASH, os.path.join(HERE, 'launch_f20l2.sh'), 'b32_pcb'], capture_output=True, text=True, env=LENV)\n"),
    ('go dry', "p = subprocess.run([BASH, os.path.join(HERE, 'go_f20l2.sh'), 'b32_pd2'], capture_output=True, text=True, env=dict(os.environ, F20L2_DRYRUN='1'))\n"
               "check('go: dry run 1 names the form (pd2: loader half, KYTY_DIAG_B32=1)', p.returncode == 0 and 'loader half' in p.stdout and 'KYTY_DIAG_B32=1' in p.stdout)\n",
     "p = subprocess.run([BASH, os.path.join(HERE, 'go_f20l2.sh'), 'b32_pcb'], capture_output=True, text=True, env=dict(os.environ, F20L2_DRYRUN='1'))\n"
     "check('go: dry run 1 names the form (pcb: loader none, gpusleep stand)', p.returncode == 0 and 'loader none' in p.stdout and 'KYTY_TEST_B32=60:gpusleep:200' in p.stdout)\n"),
]
E['test_tools_f20l2.py'] = [
    ('bad', "for bad in ('b32_z1', 'b32_pd3', 'b32_ppb_r7', 'f20_v25', ''):\n",
     "for bad in ('b32_z1', 'b32_pd3', 'b32_ppb_r7', 'f20_v25', '', 'b32_pd', 'b32_pd2', 'b32_z0', 'b32_pp', 'b32_pc'):\n"),
    ('want', "WANT = {'b32_z0b': ('KYTY_DIAG_B32=0', 'none'), 'b32_ppb': ('KYTY_DIAG_B32=1 KYTY_TEST_B32=60:present:200', 'none'),\n"
             "        'b32_pcb': ('KYTY_DIAG_B32=1 KYTY_TEST_B32=60:gpusleep:200', 'none'), 'b32_pd': ('KYTY_DIAG_B32=1', 'all'),\n"
             "        'b32_pd2': ('KYTY_DIAG_B32=1', 'half'), 'b32_pcb_r3': ('KYTY_DIAG_B32=1 KYTY_TEST_B32=60:gpusleep:200', 'none')}\n",
     "WANT = {'b32_z0b': ('KYTY_DIAG_B32=0', 'none'), 'b32_ppb': ('KYTY_DIAG_B32=1 KYTY_TEST_B32=60:present:200', 'none'),\n"
     "        'b32_pcb': ('KYTY_DIAG_B32=1 KYTY_TEST_B32=60:gpusleep:200', 'none'),\n"
     "        'b32_pcb_r3': ('KYTY_DIAG_B32=1 KYTY_TEST_B32=60:gpusleep:200', 'none')}\n"),
    ('ascii list', "           'test_guard_f20l2.py', 'port_f20l2.py'):\n",
     "           'test_guard_f20l2.py', 'port_f20l2.py', 'edit_f20l2.py', 'refs_f20l2.py'):\n"),
    ('ascii base', "for nm in ('b32_read.py', 'test_b32_read.py', 'sens_b32.py', 'b32_base.py', 'b32_load.py',",
     "for nm in ('b32_read.py', 'test_b32_read.py', 'sens_b32.py', 'b32_load.py',"),
]
E['mk_seal_f20l2.py'] = [
    ('files', "FILES = ['b32_read.py', 'f20e_read.py', 'test_b32_read.py', 'sens_b32.py', 'b32_base.py', 'base/base_f20l2.txt', 'base/base_f20l2.json',\n",
     "FILES = ['b32_read.py', 'f20e_read.py', 'test_b32_read.py', 'sens_b32.py', 'C:/kyty/f287/f20l/b32_base.py',\n"
     "         'C:/kyty/f287/f20l/base/base_f20l.txt', 'C:/kyty/f287/f20l/base/base_f20l.json', 'C:/kyty/f287/f20l/pred/f20l_seal.md',\n"
     "         'C:/kyty/f287/bin/kyty_emulator_b9e0ee00.exe', 'C:/kyty/f287/f20l/log_b32_pd.txt', 'C:/kyty/f287/f20l/b32_pd.json',\n"
     "         'edit_f20l2.py', 'f20l2_seal_body.md',\n"),
]
E['regress/regress_b32.py'] = [
    ('head', '"""F20l2 (HPP-648): regression', '"""F20l2 (HPP-648; port of the F20l file): regression'),
]


def main():
    plan = []
    for nm, edits in E.items():
        p = os.path.join(G, nm)
        s = open(p, 'rb').read().decode('utf-8')
        for name, old, new in edits:
            c = s.count(old)
            if c != 1:
                print('ANCHOR %s / %s: count %d' % (nm, name, c))
                return 1
            s = s.replace(old, new)
        plan.append((p, s))
    for p, s in plan:
        if any(ord(ch) > 127 for ch in s) and not p.endswith('mk_seal_f20l2.py'):
            print('non-ASCII in %s' % p)
            return 1
    for p, s in plan:
        open(p, 'wb').write(s.encode('utf-8'))
        print('edited %s' % p)
    print('edits ALL APPLIED')
    return 0


if __name__ == '__main__':
    sys.exit(main())

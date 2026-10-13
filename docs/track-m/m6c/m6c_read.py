"""Track M link M6c (HPP-850; ROADMAP s122 item 767 (i)-(k), 769 (v), 770 (b)-(e), 772 (b), 776 (v)): the reader of one tag of the
series M6 on the M6a3 test binary 2179005b (MS1 ea35b679 + KYTY_DIAG_M5W2 code 534d75af / worktree 3d227024).  Rows only, NO VERDICT on
a theme (the reading is M6d, the lead).  The sealed FS15c reader C:/kyty/f287/fs15c/fs15c_read.py (sha256 R_SHA) is IMPORTED, not
copied, as in M3a m3a_read.py: its scan of the log, the first scene frame, the stdout scan and the knob members of FS15 are its code; a
fresh instance per tag with its level constant SKY rebound to the level of the tag.  This file adds: the tag table of the seal (plan_of =
the case of go_m6c.sh), the admission by the plan, the second pass over the log for the lines of track M (MWave1 / MT2xx as M3a) and of
KYTY_DIAG_M5W2 ('M5W2: mode=', 'M5W2Stat:', 'M5W2Clr:'), the lines without a knob (T031 / T309 / T023), the reference counters of the
same paths (item 769 (v): clr_ok of FrameTrace-x, img_minlod of FrameTrace-draw, 'T# MIN_LOD ... applied' lines) and the table.
ASCII only.

    python m6c_read.py <tag> [--json <out>]
    python m6c_read.py --dir <fixture dir> --tag <tag> [--json <out>]   (fixture form: log.txt stdout.txt es.json rec.idx seal.md and the
                                                                          *.txt rows of runs/<tag>)
    python m6c_read.py --table [--runs <dir>]
    python m6c_read.py --plan <tag>
    python m6c_read.py --scan-m5 <log>                                    the M5W2 / no-knob / reference rows of one log (fixtures)

DEFINITIONS (seal pred.md section 4):
  M5W2Stat  'M5W2Stat: when=<w> pushes=.. ao_obj_push=.. ... ao_obj_vq=..' - the 21 fields of FIELDS in this order (diagM5W2.cpp
           PrintStat at 534d75af); a line with the prefix that does not parse is 'unparsable'.  THE TAG TOTAL (member P3 of item 770 (e))
           is the LAST parsed line with the LARGEST pushes; its M5W2Clr lines are the parsed 'M5W2Clr: when=<w> fmt=<vk::Format> clr_dw=..
           clr_dw_div=.. clr_dw_div8=..' lines after it and before the next M5W2Stat line, with the same when.
  M5W2: mode   'M5W2: mode=<0|1>' - once per process (the knob witness); admission: exactly one line, mode=1.
  no-knob lines   T031 'GuestPrintf: negative precision', T309 'AmprRecordSpace: refused' and 'AmprWriteAddress: refused', T023
           'AgcReserveDW: cursor state' - counts and the first line (masked to 160 chars); rows (item 767 (k): >= 1 => a register row,
           read by M6d).
  reference rows (item 769 (v))   clr_ok - sum of ' clr_ok=' of FrameTrace-x lines (per-frame deltas); img_minlod - sum of
           ' img_minlod=' of FrameTrace-draw lines; tminlod - lines 'T# MIN_LOD ' ... ' applied'.
MEMBERS (form V, rows - no theme verdict): hold >= 300 s after the first scene frame; lived; 0 death markers (log and stdout); 0 frames
  >= 1 s after the first scene frame; video index >= 3000; 0 one-frame glitches; sheet made; Event: quit; 0 Fatal after it; ended before
  the harness timeout; MWave1 mask 0x33 and MT265 / MT272 / MT231 mode 1 (the binary is MS1 + measurement code); the M5W2 total present.
"""
import hashlib
import importlib.util
import json
import os
import re
import sys

G = 'C:/kyty/m657/m6c'
R_PATH = 'C:/kyty/f287/fs15c/fs15c_read.py'
R_SHA = '9ef2975702ce8d3b94afdd9c0f3d9198a743711721fa570ac816acb70bb79cf2'
SEAL_PATH = G + '/pred.md'
MS1 = 'ea35b679b0bcfe83767093204f348b189384cab1a7b273f89b164b64cba4d4df'
TB = '2179005bc42e42133e92d4a4c9cc0a2f33b3670f0263a6ca67c2c3804ac7e43f'
SIG = '8dcf31779bbcb7c6e605653a138dae162f645a46'
VDIR = 'variant_fixb26_fixb1b_fixf10_fixf19_mw1_33'
LEVELS = {'m6_sg': 'underwater_aerial_garden', 'm6_hb': 'hoover_beach', 'm6_mg': 'mini_giants_garden'}
HOLD_OPT = 330
HOLD_V_US = 300000000
VIDEO_MIN = 3000
FIELDS = ('pushes', 'ao_obj_push', 'ao_obj_nz', 'ao_obj_nopcm', 'ao_bus_push', 'ao_bus_nz', 'clr_dw', 'clr_dw_div', 'minlod_views',
          'minlod_div', 'inv_calls', 'inv_part', 'inv_gpu', 'inv_off', 'raw_rd', 'raw_rd_gpu', 'minlod_div_x', 'clr_dw_div8',
          'ao_obj_unread', 'inv_part_src', 'ao_obj_vq')
FMT_NAME = {9: 'R8Unorm', 16: 'R8G8Unorm'}
RX_STAT = re.compile(rb'M5W2Stat: when=([a-z]+) ' + b' '.join(f.encode() + rb'=(\d+)' for f in FIELDS) + rb'\s*$')
RX_CLR = re.compile(rb'M5W2Clr: when=([a-z]+) fmt=(\d+) clr_dw=(\d+) clr_dw_div=(\d+) clr_dw_div8=(\d+)\s*$')
RX_MODE = re.compile(rb'M5W2: mode=(\d+)\s*$')
RX_MW = re.compile(rb'MWave1: mask=0x([0-9a-f]{2}) T234=(\d) T233=(\d) T256=(\d) T306=(\d) T032=(\d) T203=(\d)\s*$')
RX_MT = re.compile(rb'MT(265|272|231): mode=(\d+)\s*$')
RX_CLROK = re.compile(rb' clr_ok=(\d+)')
RX_IMGML = re.compile(rb' img_minlod=(\d+)')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
NOKNOB = (('T031', b'GuestPrintf: negative precision'), ('T309_space', b'AmprRecordSpace: refused'),
          ('T309_waddr', b'AmprWriteAddress: refused'), ('T023', b'AgcReserveDW: cursor state'))
TAG_RX = re.compile(r'^(m6_(?:sg|hb|mg))(_r[1-3])?$')


def sha_file(path):
    if not path or not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def load_r(level):
    real = sha_file(R_PATH)
    if real != R_SHA:
        raise SystemExit('m6c_read: %s sha256 %s is not the sealed FS15c reader %s' % (R_PATH, (real or 'missing')[:16], R_SHA[:16]))
    spec = importlib.util.spec_from_file_location('fs15c_read_m6c_' + level, R_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.SKY = level
    return mod


def plan_of(tag):
    m = TAG_RX.match(tag or '')
    if not m:
        return None
    return dict(base_tag=m.group(1), level=LEVELS[m.group(1)], kind='v', sd=300, timeout=480, hold=HOLD_OPT, cache='K0', save='none',
                knob=('KYTY_DIAG_M5W2', '1'))


def plan_line(tag):
    p = plan_of(tag)
    if p is None:
        return None
    return 'bin m6a3 level %s kind %s sd %d timeout %d hold %d cache %s save %s knob %s=%s' % (
        p['level'], p['kind'], p['sd'], p['timeout'], p['hold'], p['cache'], p['save'], p['knob'][0], p['knob'][1])


def expected_env(p):
    return dict(KYTY_GUEST_ARGS='-lvl ' + p['level'], KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE=None, KYTY_SAMPLE_GATE=None,
                KYTY_QUEUE_TRACE='1', KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8', KYTY_REC=None,
                KYTY_DIAG_M5W2='1')


def scan_m5(path):
    """Second pass: track M lines, the M5W2 lines, the no-knob lines, the reference counters."""
    r = dict(mw=[], mw_bad=0, mt={'265': [], '272': [], '231': []}, mt_bad=0, gp=0, devlost=0, mode=[], mode_bad=0,
             stat=[], stat_bad=0, clr_bad=0, noknob=dict((k, 0) for k, _ in NOKNOB), noknob_first={}, clr_ok=0, clr_ok_lines=0,
             img_minlod=0, img_minlod_lines=0, tminlod=0)
    if not path or not os.path.exists(path):
        return None
    cur = None
    with open(path, 'rb') as f:
        for line in f:
            if line.startswith(b'FrameTrace'):
                if line.startswith(b'FrameTrace-x:'):
                    m = RX_CLROK.search(line)
                    if m:
                        r['clr_ok'] += int(m.group(1))
                        r['clr_ok_lines'] += 1
                elif line.startswith(b'FrameTrace-draw:'):
                    m = RX_IMGML.search(line)
                    if m:
                        r['img_minlod'] += int(m.group(1))
                        r['img_minlod_lines'] += 1
                continue
            if b'M5W2' in line:
                if b'M5W2Stat:' in line:
                    m = RX_STAT.search(line)
                    if m:
                        cur = dict(when=m.group(1).decode(), clr=[])
                        for k, v in zip(FIELDS, m.groups()[1:]):
                            cur[k] = int(v)
                        r['stat'].append(cur)
                    else:
                        r['stat_bad'] += 1
                        cur = None
                elif b'M5W2Clr:' in line:
                    m = RX_CLR.search(line)
                    if m and cur is not None and m.group(1).decode() == cur['when']:
                        cur['clr'].append(dict(fmt=int(m.group(2)), clr_dw=int(m.group(3)), clr_dw_div=int(m.group(4)),
                                               clr_dw_div8=int(m.group(5))))
                    else:
                        r['clr_bad'] += 1
                elif b'M5W2: mode=' in line:
                    m = RX_MODE.search(line)
                    if m:
                        r['mode'].append(int(m.group(1)))
                    else:
                        r['mode_bad'] += 1
            for k, sig in NOKNOB:
                if sig in line:
                    r['noknob'][k] += 1
                    if k not in r['noknob_first']:
                        r['noknob_first'][k] = line.decode('ascii', 'replace').strip()[:160]
            if b'T# MIN_LOD ' in line and b' applied' in line:
                r['tminlod'] += 1
            if b'MWave1:' in line:
                m = RX_MW.search(line)
                if m:
                    r['mw'].append(int(m.group(1), 16))
                else:
                    r['mw_bad'] += 1
            if b': mode=' in line and b'MT2' in line:
                m = RX_MT.search(line)
                if m:
                    r['mt'][m.group(1).decode()].append(int(m.group(2)))
                elif re.search(rb'MT(265|272|231): mode=', line):
                    r['mt_bad'] += 1
            if line.startswith(b'GamePatch: '):
                r['gp'] += 1
            low = line.lower()
            if b'errordevicelost' in low or b'device lost' in low:
                r['devlost'] += 1
    return r


def total_of(y):
    """Member P3 of item 770 (e): the last parsed M5W2Stat line with the largest pushes; None without a parsed line."""
    best = None
    for s in y['stat']:
        if best is None or s['pushes'] >= best['pushes']:
            best = s
    return best


def paths(tag, base=None):
    names = ('installed_before', 'installed_after', 'manifest_cmp', 'glitch', 'installed_sha', 'level', 'sheet', 'plan')
    if base is not None:
        p = dict((nm, os.path.join(base, nm + '.txt')) for nm in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'), seal=os.path.join(base, 'seal.md'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % tag), seal=SEAL_PATH)
    return p


def text(path):
    if not path or not os.path.exists(path):
        return None
    return open(path, 'rb').read().decode('utf-8', 'replace')


def read_tag(tag, pth):
    p = plan_of(tag)
    res = dict(tag=tag, reader_sha256=sha_file(os.path.abspath(__file__)), plan=plan_line(tag))
    if p is None:
        res.update(status='NOT_ADMITTED', admitted=False, interference='unknown tag')
        return res
    R = load_r(p['level'])
    res.update(level=p['level'], base_tag=p['base_tag'])
    run = json.load(open(pth['run'], encoding='utf-8')) if os.path.exists(pth['run']) else None
    jbin = (run or {}).get('binary_sha256')
    inst_b = (text(pth['installed_before']) or '').strip() or None
    inst_a = (text(pth['installed_after']) or '').strip() or None
    inst_t = (text(pth['installed_sha']) or '').strip() or None
    seal_sha = sha_file(pth['seal'])
    pre = ((run or {}).get('prereg') or {}).get('sha256')
    env = (run or {}).get('env') or {}
    cmd = (run or {}).get('cmdline') or []
    att = ((run or {}).get('attempts') or [{}])[-1]
    mcmp = (text(pth['manifest_cmp']) or '').strip().splitlines()
    hlev = (text(pth['level']) or '').strip() or None
    plan_txt = (text(pth['plan']) or '').strip()
    ga = (run or {}).get('guest_args') or ''
    have_log = os.path.exists(pth['log'])
    x = R.scan(pth['log']) if have_log else None
    y = scan_m5(pth['log']) if have_log else None
    kenv = dict((k, v) for k, v in env.items() if k.startswith(('KYTY_', 'VK_')))
    ebad = R.env_diff(kenv, expected_env(p))
    test_keys = sorted(k for k in env if k.startswith('KYTY_TEST_'))
    so = R.stdout_scan(pth['stdout'])
    s_stand = None if so is None else so['stand']
    want_plan = 'm6a3 %s K0 none v KYTY_DIAG_M5W2=1' % TB
    adm = [
        ('tag json present', run is not None),
        ('json binary_sha256 = M6a3 test binary 2179005b (%s)' % (jbin or '-')[:16], jbin == TB),
        ('installed during the tag = 2179005b (%s)' % (inst_t or '-')[:16], inst_t == TB),
        ('installed before = after = MS1 ea35b679 (%s / %s)' % ((inst_b or '-')[:16], (inst_a or '-')[:16]), inst_b == MS1 and inst_a == MS1),
        ('json prereg sha256 = seal sha256 (%s / %s)' % ((pre or '-')[:16], (seal_sha or '-')[:16]), pre is not None and pre == seal_sha),
        ('the plan of go_m6c.sh = the plan of the reader (%s)' % plan_txt[:90], plan_txt == want_plan),
        ('env = the form of the tag (%s)' % (ebad[:6] or 'exact'), run is not None and not ebad),
        ('no KYTY_TEST_* in the env (%s)' % (test_keys or 'none'), run is not None and not test_keys),
        ('0 ExitFatal: lines (log %s; whole stdout %s)' % ((x or {}).get('stand'), s_stand), x is not None and x['stand'] == 0 and s_stand == 0),
        ('last --vulkan-validation false (%s)' % R.last_flag(cmd, '--vulkan-validation'), R.last_flag(cmd, '--vulkan-validation') == 'false'),
        ('last --shader-validation false (%s)' % R.last_flag(cmd, '--shader-validation'), R.last_flag(cmd, '--shader-validation') == 'false'),
        ('no --rd', run is not None and '--rd' not in cmd),
        ('guest args -lvl %s (%s; harness %s)' % (p['level'], ga, hlev), ga == '-lvl ' + p['level'] and hlev == p['level']),
        ('hold option %d s (%s)' % (p['hold'], (run or {}).get('hold_s')), (run or {}).get('hold_s') == p['hold']),
        ('log present', have_log),
        ('stdout present', so is not None),
        ('entry outcome ok (%s)' % att.get('outcome'), att.get('outcome') == 'ok'),
        ('entry line present (%s)' % (x or {}).get('entry_ln'), x is not None and x['entry_ln'] is not None),
        ('window events: minimized %s, Recovering Vulkan swapchain %s (all %s) - a window event is an interference, repeat (item 767 (i))' % (
            (x or {}).get('minimized'), (x or {}).get('recovering'), (x or {}).get('win')),
         x is not None and x['minimized'] == 0 and x['recovering'] == 0),
        ('translation signature %s and cache dir %s (%s / %s)' % (SIG[:8], VDIR, [z[:8] for z in (x or {}).get('sig') or []],
                                                                (x or {}).get('variant_dir')),
         x is not None and x['sig'] == [SIG] and x['variant_dir'] == [VDIR]),
        ('GamePatch lines 0 (%s)' % (y or {}).get('gp'), y is not None and y['gp'] == 0),
        ('no DiagB32 line (%s)' % (x or {}).get('diagb32'), x is not None and x['diagb32'] == 0),
        ('no TestLogStall line (%s)' % (x or {}).get('stall_lines'), x is not None and x['stall_lines'] == 0),
        ('no TestHidLoss line (%s)' % (x or {}).get('hidloss'), x is not None and x['hidloss'] == 0),
        ('knob witness: exactly one line M5W2: mode=1 (%s, unparsable %s)' % ((y or {}).get('mode'), (y or {}).get('mode_bad')),
         y is not None and y['mode'] == [1] and y['mode_bad'] == 0),
        ('caches returned (manifest_cmp: %s)' % (mcmp[0][:40] if mcmp else '-'), bool(mcmp) and mcmp[0].startswith('manifest cmp EQUAL')),
    ]
    if x is not None:
        ok = len(x['summary']) == 1 and x['summary_bad'] == 0
        adm.append(('summary line LogAsync: full_waits= present once, all fields (%d, bad %d) - absent: killed (item 615 (b)(6))' % (
            len(x['summary']), x['summary_bad']), ok))
    res['admission'] = [[a, bool(b)] for a, b in adm]
    admitted = all(b for _, b in adm)
    res['status'] = 'ADMITTED' if admitted else 'NOT_ADMITTED'
    res['admitted'] = admitted
    res['interference'] = None if admitted else 'admission member: %s' % [a for a, b in adm if not b][:3]
    idx_n = None
    if os.path.exists(pth['idx']):
        with open(pth['idx'], 'rb') as fi:
            idx_n = sum(1 for _ in fi)
    gl = None
    gt = text(pth['glitch'])
    if gt:
        mg = RX_GL.search(gt)
        gl = int(mg.group(1)) if mg else None
    sheet = (text(pth['sheet']) or '').strip()[:120] or None
    res['members'] = res['info'] = res['m5'] = None
    res['ok'] = None
    if x is not None and admitted:
        lived = att.get('outcome') == 'ok' and att.get('hold_exit') is None
        death = x['death'] + ((so or {}).get('death') or [])
        i, hold, ge1, ge1_with_first, info = R.scene(x)
        end_ok = att.get('close_killed') is False and att.get('close_rc') is not None
        tot = total_of(y)
        m = [('hold >= 300 s after the first scene frame (%.1f s)' % (hold / 1e6), hold >= HOLD_V_US),
             ('the process lived through the hold (outcome %s, hold_exit %s)' % (att.get('outcome'), att.get('hold_exit')), lived),
             ('0 death markers (log and stdout) %s; device lost lines %d' % (death[:3], y['devlost']),
              not death and so is not None and y['devlost'] == 0),
             ('0 frames >= 1 s after the first scene frame (%d; first %s; with the first frame %d)' % (ge1, info['first_scene_n'],
                                                                                                   ge1_with_first), i is not None and ge1 == 0),
             ('video index records >= 3000 (%s)' % idx_n, (idx_n or 0) >= VIDEO_MIN),
             ('0 one-frame glitches (%s)' % gl, gl == 0),
             ('sheet for the lead made (%s)' % sheet, bool(sheet)),
             ('exit by the harness: Event: quit line in the log (%s)' % x['quit_ln'], x['quit_ln'] is not None),
             ('after Event: quit: 0 --- Fatal Error --- (log %d; whole stdout %s)' % (x['fatal_after_quit'], (so or {}).get('fatal')),
              x['quit_ln'] is not None and x['fatal_after_quit'] == 0 and (so or {}).get('fatal') == 0),
             ('the process ended before the harness timeout (close_killed %s, close_rc %s)' % (att.get('close_killed'), att.get('close_rc')),
              end_ok),
             ('MWave1: mask=0x33 on every parsed line, >= 1 line (lines %s, unparsable %d)' % (['0x%02x' % v for v in y['mw'][:4]],
                                                                                            y['mw_bad']),
              bool(y['mw']) and y['mw_bad'] == 0 and all(v == 0x33 for v in y['mw']))]
        for th in ('265', '272', '231'):
            m.append(('MT%s: mode=1 on every parsed line (lines %s; absent - not called, a row)' % (th, y['mt'][th][:4]),
                      all(v == 1 for v in y['mt'][th])))
        m.append(('M5W2Stat: >= 1 parsed line, 0 unparsable (%d / %d; M5W2Clr outside a total group %d)' % (
            len(y['stat']), y['stat_bad'], y['clr_bad']), bool(y['stat']) and y['stat_bad'] == 0))
        res['members'] = [[a, bool(b)] for a, b in m]
        res['ok'] = all(b for _, b in m)
        info.update(video_index=idx_n, glitches=gl, mwave1=['0x%02x' % v for v in y['mw'][:3]],
                    mt=dict((k, v[:3]) for k, v in y['mt'].items()), hold_s=round(hold / 1e6, 1), frames_ge1s=ge1)
        res['info'] = info
        res['exit'] = dict(close_rc=att.get('close_rc'), close_s=att.get('close_s'), close_killed=att.get('close_killed'))
        res['m5'] = dict(total=tot, stat_lines=len(y['stat']), stat_whens=sorted(set(s['when'] for s in y['stat'])),
                         stat_bad=y['stat_bad'], clr_bad=y['clr_bad'], noknob=y['noknob'], noknob_first=y['noknob_first'],
                         ref=dict(clr_ok=y['clr_ok'], clr_ok_lines=y['clr_ok_lines'], img_minlod=y['img_minlod'],
                                  img_minlod_lines=y['img_minlod_lines'], tminlod_applied_lines=y['tminlod']))
    res['reading'] = ('ADMITTED, members %s (no verdict on a theme; reading - M6d)' % ('ALL YES' if res['ok'] else 'NOT ALL YES')
                      if admitted else 'NOT_ADMITTED: %s' % res['interference'])
    return res


def rows_out(res):
    out = ['tag %s (plan: %s)  reader sha256 %s' % (res['tag'], res.get('plan'), res['reader_sha256'])]
    out.append('  ADMISSION %s; STATUS %s' % ('PASS' if res['admitted'] else 'FAIL', res['status']))
    for a, b in res.get('admission') or []:
        out.append('    [%s] %s' % ('ok' if b else 'NO', a))
    if res.get('members') is not None:
        out.append('  MEMBERS %s' % ('ALL YES' if res['ok'] else 'NOT ALL YES'))
        for a, b in res['members']:
            out.append('    [%s] %s' % ('YES' if b else 'NO', a))
        m5 = res['m5']
        t = m5['total']
        if t is None:
            out.append('  M5W2 TOTAL none (no parsed M5W2Stat line)')
        else:
            out.append('  M5W2 TOTAL (last line with the largest pushes, item 770 (e)) when=%s of %d lines (whens %s)' % (
                t['when'], m5['stat_lines'], m5['stat_whens']))
            out.append('    ' + ' '.join('%s=%d' % (f, t[f]) for f in FIELDS))
            for c in t['clr']:
                out.append('    M5W2Clr fmt=%d%s clr_dw=%d clr_dw_div=%d clr_dw_div8=%d' % (
                    c['fmt'], ' (%s)' % FMT_NAME[c['fmt']] if c['fmt'] in FMT_NAME else '', c['clr_dw'], c['clr_dw_div'], c['clr_dw_div8']))
        out.append('  M5W2 NO-KNOB LINES %s' % json.dumps(m5['noknob'], sort_keys=True))
        for k, v in sorted(m5['noknob_first'].items()):
            out.append('    first %s: %s' % (k, v))
        out.append('  M5W2 REFERENCE ROWS (item 769 (v)) %s' % json.dumps(m5['ref'], sort_keys=True))
        out.append('  INFO %s' % json.dumps(res['info'], sort_keys=True, default=list)[:1400])
    out.append('  READING %s' % res['reading'])
    return out


def table(rd):
    rows = []
    if os.path.isdir(rd):
        for t in sorted(os.listdir(rd)):
            js = os.path.join(rd, t, 'read.json')
            if plan_of(t) and os.path.exists(js):
                rows.append(json.load(open(js, encoding='utf-8')))
    out = ['| tag | status | members | death / frames >= 1 s | glitches | video | hold_s | when | ' + ' | '.join(FIELDS) + ' |',
           '|' + '---|' * (8 + len(FIELDS))]
    used = {}
    for r in rows:
        inf = r.get('info') or {}
        m5 = r.get('m5') or {}
        t = m5.get('total') or {}
        mem = dict(r.get('members') or [])
        dth = [a for a in mem if a.startswith('0 death markers')]
        out.append('| %s | %s | %s | %s / %s | %s | %s | %s | %s | %s |' % (
            r['tag'], r['status'], '-' if r.get('ok') is None else ('ALL YES' if r['ok'] else 'NOT ALL YES'),
            ('0' if mem.get(dth[0]) else 'NO') if dth else '-', inf.get('frames_ge1s'), inf.get('glitches'), inf.get('video_index'),
            inf.get('hold_s'), t.get('when'), ' | '.join(str(t.get(f, '-')) for f in FIELDS)))
        if r.get('admitted') and t:
            used[r['base_tag']] = r
    if used:
        s = dict((f, sum(u['m5']['total'][f] for u in used.values())) for f in FIELDS)
        out.append('| SUM %s | | | | | | | | %s |' % ('+'.join(sorted(used)), ' | '.join(str(s[f]) for f in FIELDS)))
    out.append('')
    out.append('M5W2Clr of the totals (tag fmt clr_dw clr_dw_div clr_dw_div8):')
    for b in sorted(used):
        for c in used[b]['m5']['total']['clr']:
            out.append('  %s fmt=%d%s %d %d %d' % (used[b]['tag'], c['fmt'], ' (%s)' % FMT_NAME[c['fmt']] if c['fmt'] in FMT_NAME else '',
                                                  c['clr_dw'], c['clr_dw_div'], c['clr_dw_div8']))
    out.append('no-knob lines and reference rows (item 767 (z), 769 (v)):')
    for b in sorted(used):
        m5 = used[b]['m5']
        out.append('  %s noknob %s ref %s' % (used[b]['tag'], json.dumps(m5['noknob'], sort_keys=True), json.dumps(m5['ref'], sort_keys=True)))
    return out


def main(argv):
    if '--plan' in argv:
        print(plan_line(argv[argv.index('--plan') + 1]) or 'unknown')
        return 0
    if '--scan-m5' in argv:
        y = scan_m5(argv[argv.index('--scan-m5') + 1])
        t = total_of(y) if y else None
        print(json.dumps(dict(total=t, n=len(y['stat']) if y else None, bad=y['stat_bad'] if y else None,
                              clr_bad=y['clr_bad'] if y else None, mode=y['mode'] if y else None,
                              noknob=y['noknob'] if y else None, ref=dict(clr_ok=y['clr_ok'], img_minlod=y['img_minlod'],
                                                                          tminlod=y['tminlod']) if y else None), sort_keys=True))
        return 0
    if '--table' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        print('reader m6c_read.py sha256 %s' % sha_file(os.path.abspath(__file__)))
        for line in table(rd):
            print(line)
        return 0
    js = argv[argv.index('--json') + 1] if '--json' in argv else None
    if '--dir' in argv:
        tag = argv[argv.index('--tag') + 1]
        pth = paths(tag, argv[argv.index('--dir') + 1])
    else:
        tag = argv[0] if argv else ''
        pth = paths(tag)
    if plan_of(tag) is None:
        print('usage: m6c_read.py <tag> | --dir D --tag T | --table | --plan <tag> | --scan-m5 <log>')
        return 2
    res = read_tag(tag, pth)
    for line in rows_out(res):
        print(line)
    if js:
        with open(js, 'w', encoding='ascii', newline='\n') as f:
            json.dump(res, f, ensure_ascii=True, sort_keys=True, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

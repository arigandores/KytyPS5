"""FS15c (HPP-822): build fs15c_read.py (beside this file) from C:/kyty/f287/fs14c/fs14c_read.py (FS14c) by a fixed list of replacements,
each asserted to match exactly once: the FS15 constants, the fs15_z env (KYTY_FIX_F20=0), the FixF20 / FixF20Stat parts of
C:/kyty/f287/f42c/f42c_read.py (F42c), the members of item 730 (g)(3), the rows of the preparation screen, 'all pipelines created' and the
driver blob, the table.  LF, ASCII.  usage: python patch_read_fs15c.py"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
s = open('C:/kyty/f287/fs14c/fs14c_read.py', 'rb').read().replace(b'\r\n', b'\n').decode('ascii')


def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, old[:80])
    s = s.replace(old, new)


def func(name, new):
    """Replace the whole top-level function `name` (to the next top-level def / blank-blank)."""
    global s
    m = re.search(r'^def %s\(.*?(?=^def |^if __name__)' % re.escape(name), s, re.S | re.M)
    assert m, name
    s = s[:m.start()] + new.rstrip('\n') + '\n\n\n' + s[m.end():]


DOC = '''"""Track F link FS15c (HPP-822; ROADMAP s122 item 730 (g)(3), acceptance FS15a / FS15b item 732, 733): the reader of the tags
fs15_v / fs15_w / fs15_z of the shipping binary FS15 bfac84be (FS14 eb7e8b91 + a6342c98 + a9d6fd1c + 82570fd2 + 38fc76c1, default
KYTY_FIX_F20=1, version KytyPS5-2026-09-15-6a2987a-1929-g6beb3b73); installed FS14 013e1974 before and after (item 727-728).  Rows only,
NO VERDICT (the reading and the install are FS15d, HPP-823).  Port of C:/kyty/f287/fs14c/fs14c_read.py (FS14c, HPP-814: the forms fs14_v /
fs14_w, the members of F24 / F29 / F25 / F21 / B12, the exit of the form fs12_v) with the FixF20 parts of C:/kyty/f287/f42c/f42c_read.py
(F42c, HPP-781: 'FixF20: mode=', 'FixF20Stat:', the preparation screen, PipelinePrecache, the driver blob).  ASCII only.

    python fs15c_read.py <tag> [--json <out>]                       one tag (files of C:/kyty/f287/fs15c)
    python fs15c_read.py --dir <fixture dir> --tag <tag> [--json <out>]
        fixture form: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, sheet.txt, installed_before.txt, installed_after.txt,
        installed_sha.txt, manifest_cmp.txt, level.txt, cache_before.tsv, cache_after.tsv, seal.md, bin.exe
    python fs15c_read.py --table [--runs <dir>]                     the table over every runs/<tag>/read.json

DEFINITIONS (seal pred/fs15c_seal.md section 4):
  entry line      the first line ending 'GuestOut: Level has started: underwater_aerial_garden'; first GuestOut - the first line carrying
                  'GuestOut'.
  first scene     the first 'FrameTrace: n=' line after the entry line with draws >= 100; the frames 'after the first scene frame' are the
  frame           FrameTrace lines after it (the first itself not counted; a row prints the count with it).
  FixF20          'FixF20: mode=<0|1>' (6beb3b73 fixF20.cpp Mode(), once per process): >= 1 parsed line, no unparsable line, every line
                  mode=<want>, the first before the first GuestOut; want 1 at fs15_v / fs15_w (the default, no variable), 0 at fs15_z.
  FixF20Stat      'FixF20Stat: when=<w> calls=<n> modules_bound=<n> modules=<n> sites=<n> rewritten=<n> unmatched=<n>' (fixF20.cpp
                  PrintStat; when=periodic every 4 096 modules, when=exit at the end of Execute after WindowRun, only at mode 1); the exit
                  line - the LAST parsed line with when=exit AFTER the first 'Event: quit' line (none - every exit member NO).
  quit            the first log line containing 'Event: quit' (the harness exit, WM_CLOSE posted at the end of the hold).
  FixF24 / FixF29 / FixF25 / FixF21 / FixB12 / FixB13 / LogAsync / init / init_owner / wait_expired / pump_stop_expired / ExitFatal /
                  F25 / F29 rows - as in fs14c_read.py.
ADMISSION (a failed member - NOT_ADMITTED, not read; a repeat by the lead's item): json; binary_sha256 = FS15 bfac84be; installed during the
  tag = bfac84be; installed before = after = FS14 013e1974; prereg = seal sha256; env = the form exactly (KYTY_* / VK_*; path values of
  KYTY_GATE_FILE, KYTY_SAMPLE_GATE, KYTY_REC any; no KYTY_FIX_* at fs15_v / fs15_w; KYTY_FIX_F20 = '0' and no other KYTY_FIX_* at fs15_z;
  no KYTY_GAME_PATCH); no KYTY_TEST_* key and 0 'ExitFatal:' lines (log and stdout); last --vulkan-validation true only at fs15_w, else
  false; --shader-validation false; no --rd; -lvl underwater_aerial_garden and the harness level file; hold option 330 / 310 / 150; log;
  stdout; entry outcome ok; entry line; window lines minimized / Recovering Vulkan swapchain 0; signature 9177b426 and the catalog
  variant_fixb26_fixb1b_fixf10_fixf19; GamePatch: 0; DiagB32 0; TestLogStall 0; TestHidLoss 0; caches returned (manifest cmp EQUAL); the
  summary line 'LogAsync: full_waits=' once with all fields (absent: killed - item 615 (b)(6)) - 25.
MEMBERS (letter of item 730 (g)(3)):
  fs15_v  the 20 members of fs14_v (hold >= 300 s; lived; 0 death markers; 0 frames >= 1 s; video >= 3 000; 0 glitches; sheet; FixF24:
          mode=1 b24=1, FixF24: init, init_owner alive, init_owner hid = helper = pump != main, FixF25: mode=1, FixF21: mode=1, FixB12:
          mode=1, FixF29: mode=1 before the first GuestOut; Event: quit; 0 Fatal after it; 0 wait_expired; 0 pump_stop_expired; ended
          before the harness timeout) + FixF20: mode=1 before the first GuestOut + FixF20Stat: when=exit line after Event: quit; its
          unmatched 0; its modules_bound = modules; its rewritten >= 11 - 25.
          + group 'form fs14_v' (= fs13_v): LogAsync: mode=1 once; summary; drain_timeouts 0; FixB13: mode=1; FixB12Stat: present - 5.
  fs15_w  lived (hold_s >= 310); 0 death markers; 0 [Vulkan][E]; 0 limit lines of the layer; [Vulkan][W] > 0; DualSrcBlend: supported=1
          enabled=1, FixF20: mode=1 and FixF24: mode=1 b24=1 before the first GuestOut; FixF20Stat: when=exit line after Event: quit; its
          unmatched 0; its modules_bound = modules - 11.
          + group 'form fs14_w': FixF29: mode=1; FixF25: mode=1; FixF21: mode=1; LogAsync: mode=1; no VALIDATION_STOP; FixB13: mode=1;
          FixB12: mode=1 - 7.
  fs15_z  hold >= 120 s after the first scene frame; lived; 0 death markers (log and stdout); FixF20: mode=0 before the first GuestOut;
          FixF20Stat: lines 0 (parsed and unparsable, whole log) - 5.
ROWS (no gate): the preparation screen 'ShaderPreparation: startup wait finished in <ms> ms'; 'PipelinePrecache: all pipelines created,
  <ms> ms' and every 'PipelinePrecache:' line; 'Vulkan pipeline cache:' lines; the driver blob: bytes of _PipelineCache (and GLCache,
  _ShaderCache) before the tag (manifest_before.tsv) and after the run before the return (manifest_run.tsv); every FixF20Stat line (count,
  periodic, unparsable, max unmatched, the exit line, the last line); F24 / F29 / F25 rows; exit code close_rc and close_s (every tag; at
  fs15_z 'the harness exit - a row'); fs15_z: FixF24 / FixF29 / FixF25 / FixF21 / FixB12 mode lines (reference).
"""'''
i = s.index('import hashlib')
s = DOC + '\n' + s[i:]

rep("""G = 'C:/kyty/f287/fs14c'
SEAL_PATH = G + '/pred/fs14c_seal.md'
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_013e1974.exe'
BIN_TAG = '013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd'
BIN_FS13 = 'abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1925-geb7e8b91'""",
    """G = 'C:/kyty/f287/fs15c'
SEAL_PATH = G + '/pred/fs15c_seal.md'
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_bfac84be.exe'
BIN_TAG = 'bfac84bea0eaec8bf3dae6ab5f67cd480f26921829f64f4a8b467bd50e922d8c'
BIN_INST = '013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1929-g6beb3b73'""")
rep("TAG_RX = re.compile(r'^(fs14_v|fs14_w|fs14_z)(_r[1-3])?$')", "TAG_RX = re.compile(r'^(fs15_v|fs15_w|fs15_z)(_r[1-3])?$')")
rep("VIDEO_MIN = 3000\n", "VIDEO_MIN = 3000\nREWRITTEN_MIN = 11\n")
rep("RX_F29 = re.compile(rb'FixF29: mode=(\\d+)\\s*$')\n",
    "RX_F29 = re.compile(rb'FixF29: mode=(\\d+)\\s*$')\n"
    "RX_F20 = re.compile(rb'FixF20: mode=(\\d+)\\s*$')\n"
    "RX_F20S = re.compile(rb'FixF20Stat: when=([a-z]+) calls=(\\d+) modules_bound=(\\d+) modules=(\\d+) sites=(\\d+) rewritten=(\\d+) '\n"
    "                     rb'unmatched=(\\d+)\\s*$')\n"
    "RX_PREP = re.compile(rb'ShaderPreparation: startup wait finished in (\\d+) ms')\n"
    "RX_ALLP = re.compile(rb'PipelinePrecache: all pipelines created, (\\d+) ms')\n"
    "STAT_KEYS = ('when', 'calls', 'modules_bound', 'modules', 'sites', 'rewritten', 'unmatched')\n")
rep("M_ACC = b'Accessed non-GPU cached memory'\n",
    "M_ACC = b'Accessed non-GPU cached memory'\nM_PRECACHE = b'PipelinePrecache:'\nM_VKPC = b'Vulkan pipeline cache:'\n")
rep("    return {'fs14_v': 'v', 'fs14_w': 'w', 'fs14_z': 'z'}[base]", "    return {'fs15_v': 'v', 'fs15_w': 'w', 'fs15_z': 'z'}[base]")
rep("        e.update(KYTY_FIX_F24='0', KYTY_FIX_F29='0')", "        e.update(KYTY_FIX_F20='0')")
rep("             variant_dir=[], gamepatch=0, diagb32=0, stall_lines=0, fork=None)",
    "             variant_dir=[], gamepatch=0, diagb32=0, stall_lines=0, fork=None,\n"
    "             f20=[], f20_bad=0, f20s=[], f20s_bad=0, f20_other=0, prep=[], allp=[], precache=[], precache_n=0, vkpc=[], vkpc_n=0)")
rep("""        if b'FixF29:' in line:
            if M_OVF in line:""", """        if b'FixF20' in line:
            if b'FixF20Stat:' in line:
                m = RX_F20S.search(line)
                if m:
                    st = dict(zip(STAT_KEYS, [m.group(1).decode()] + [int(m.group(k)) for k in range(2, 8)]))
                    st['ln'] = ln
                    r['f20s'].append(st)
                else:
                    r['f20s_bad'] += 1
            elif b'FixF20: mode=' in line:
                m = RX_F20.search(line)
                if m:
                    r['f20'].append((int(m.group(1)), ln))
                else:
                    r['f20_bad'] += 1
            else:
                r['f20_other'] += 1
        if b'ShaderPreparation: startup wait finished' in line:
            m = RX_PREP.search(line)
            r['prep'].append((int(m.group(1)) if m else None, line.decode('ascii', 'replace').strip()[:200]))
        if M_PRECACHE in line:
            r['precache_n'] += 1
            if len(r['precache']) < 8:
                r['precache'].append(line.decode('ascii', 'replace').strip()[:200])
            m = RX_ALLP.search(line)
            if m:
                r['allp'].append(int(m.group(1)))
        if M_VKPC in line:
            r['vkpc_n'] += 1
            if len(r['vkpc']) < 8:
                r['vkpc'].append(line.decode('ascii', 'replace').strip()[:200])
        if b'FixF29:' in line:
            if M_OVF in line:""")
rep(" b24=1 (every line) before the first GuestOut (%s; unparsable %d; first GuestOut %s) - item 710 (g)(3)' % (",
    " b24=1 (every line) before the first GuestOut (%s; unparsable %d; first GuestOut %s)' % (")
rep("    return ('FixF29: mode=%d (every line) before the first GuestOut (%s; unparsable %d; first GuestOut %s) - item 712 (g)(3)' % (",
    "    return ('FixF29: mode=%d (every line) before the first GuestOut (%s; unparsable %d; first GuestOut %s)' % (")
rep('''def f24_other_count(x):''', '''def f20_member(x, want):
    g = x['first_guest_ln']
    ok = bool(x['f20']) and x['f20_bad'] == 0 and all(v == want for v, l in x['f20']) and g is not None and x['f20'][0][1] < g
    return ('FixF20: mode=%d (every line) before the first GuestOut (%s; unparsable %d; first GuestOut %s) - item 730 (g)(3)' % (
        want, x['f20'][:3], x['f20_bad'], g), ok)


def exit_after_quit(x):
    """The last parsed FixF20Stat line with when=exit after the first Event: quit line; None if none."""
    q = x['quit_ln']
    ex = [st for st in x['f20s'] if st['when'] == 'exit' and q is not None and st['ln'] > q]
    return ex[-1] if ex else None


def stat_members(x, with_rewritten):
    e = exit_after_quit(x)
    q = x['quit_ln']
    n_after = len([st for st in x['f20s'] if st['when'] == 'exit' and q is not None and st['ln'] > q])
    out = [('FixF20Stat: when=exit line after Event: quit (quit %s; exit lines after it %d; all exit lines %d; unparsable FixF20Stat %d)' % (
               q, n_after, len([st for st in x['f20s'] if st['when'] == 'exit']), x['f20s_bad']), e is not None),
           ('FixF20Stat exit line: unmatched 0 (%s)' % (None if e is None else e['unmatched']), e is not None and e['unmatched'] == 0),
           ('FixF20Stat exit line: modules_bound = modules (%s / %s)' % (None if e is None else e['modules_bound'],
                                                                         None if e is None else e['modules']),
            e is not None and e['modules_bound'] == e['modules'])]
    if with_rewritten:
        out.append(('FixF20Stat exit line: rewritten >= %d (%s)' % (REWRITTEN_MIN, None if e is None else e['rewritten']),
                    e is not None and e['rewritten'] >= REWRITTEN_MIN))
    return out


def tsv_bytes(path):
    """{label: bytes} of a manifest_fs4c.py tsv; None if absent."""
    if not path or not os.path.exists(path):
        return None
    out = {}
    for line in open(path, 'rb').read().decode('ascii', 'replace').splitlines():
        p = line.split('\\t')
        if len(p) >= 3:
            out[p[0]] = out.get(p[0], 0) + (num(p[2]) or 0)
    return out


def f24_other_count(x):''')

func('members', '''def members(kind, x, att, idx_n, gl, sheet, so):
    summ = summary_of(x)
    death = x['death'] + ((so or {}).get('death') or [])
    s_fatal = None if so is None else so['fatal']
    s_exp = None if so is None else so['expired']
    s_pumpx = None if so is None else so['pumpx']
    lived = att.get('outcome') == 'ok' and att.get('hold_exit') is None
    i, hold, ge1, ge1_with_first, info = scene(x)
    info.update(summary=summ, quit_ln=x['quit_ln'], fatal_after_quit=x['fatal_after_quit'], fatal_log_total=x['fatal_total'],
                fatal_stdout=s_fatal, expired_log=x['expired'], expired_stdout=s_exp, vke=x['vke'], vkw=x['vkw'])
    death_m = ('0 death markers (log and stdout) %s' % death[:3], not death and so is not None)
    exp_m = ('0 FixF21: wait_expired (whole log %d; whole stdout %s)' % (x['expired'], s_exp), x['expired'] == 0 and s_exp == 0)
    g = x['first_guest_ln']
    if kind == 'v':
        end_ok = att.get('close_killed') is False and att.get('close_rc') is not None
        o, alive, same = owner_parts(x)
        init_ok = bool(x['init']) and g is not None and x['init'][0] < g
        m = [('hold >= 300 s after the first scene frame (%.1f s)' % (hold / 1e6), hold >= HOLD_V_US),
             ('the process lived through the hold (outcome %s, hold_exit %s)' % (att.get('outcome'), att.get('hold_exit')), lived),
             death_m,
             ('0 frames >= 1 s after the first scene frame (%d; first %s; with the first frame %d)' % (ge1, info['first_scene_n'],
                                                                                                   ge1_with_first),
              i is not None and ge1 == 0),
             ('video index records >= 3000 (%s)' % idx_n, (idx_n or 0) >= VIDEO_MIN),
             ('0 one-frame glitches (%s)' % gl, gl == 0),
             ('sheet for the lead made (%s)' % sheet, bool(sheet)),
             f20_member(x, 1),
             f24_member(x, 1),
             ('FixF24: init before the first GuestOut (lines %s; first GuestOut %s)' % (x['init'][:2], g), init_ok),
             ('FixF24: init_owner exactly 1 before the first GuestOut (%d, unparsable %d) %s: hid != 0 and helper != 0 (witness '
              'alive)' % (len(x['owner']), x['owner_bad'], o), alive),
             ('FixF24: init_owner hid = helper = pump != main', same),
             f25_member(x, 1),
             f21_member(x, 1),
             b12_member(x),
             f29_member(x, 1),
             ('exit by the harness: Event: quit line in the log (%s)' % x['quit_ln'], x['quit_ln'] is not None),
             ('after Event: quit: 0 --- Fatal Error --- (log %d; whole stdout %s)' % (x['fatal_after_quit'], s_fatal),
              x['quit_ln'] is not None and x['fatal_after_quit'] == 0 and s_fatal == 0),
             exp_m,
             ('0 FixF24: pump_stop_expired (whole log %d; whole stdout %s)' % (x['pumpx'], s_pumpx), x['pumpx'] == 0 and s_pumpx == 0),
             ('the process ended before the harness timeout (close_killed %s, close_rc %s, close_wait_s %s)' % (
                 att.get('close_killed'), att.get('close_rc'), att.get('close_wait_s')), end_ok)] + stat_members(x, True)
        f = [mode_member(x),
             ('summary LogAsync: full_waits= present (%d)' % len(x['summary']), summ is not None),
             ('drain_timeouts 0 (%s)' % (None if summ is None else summ['drain_timeouts']), summ is not None and summ['drain_timeouts'] == 0),
             b13_member(x),
             ('FixB12Stat: line present (parsed %d, unparsable %d)' % (len(x['stat']), x['stat_bad']), len(x['stat']) >= 1)]
    elif kind == 'z':
        n20s = len(x['f20s']) + x['f20s_bad']
        m = [('hold >= 120 s after the first scene frame (%.1f s)' % (hold / 1e6), i is not None and hold >= HOLD_Z_US),
             ('the process lived through the hold (outcome %s, hold_exit %s)' % (att.get('outcome'), att.get('hold_exit')), lived),
             death_m,
             f20_member(x, 0),
             ('0 FixF20Stat: lines (%d: parsed %d - exit %d, periodic %d; unparsable %d)' % (
                 n20s, len(x['f20s']), len([st for st in x['f20s'] if st['when'] == 'exit']),
                 len([st for st in x['f20s'] if st['when'] == 'periodic']), x['f20s_bad']), n20s == 0)]
        f = []
        info.update(video_index=idx_n, glitches=gl, sheet=sheet, b12=x['b12'][:3], b13=x['b13'][:3], f21=x['f21'][:3], f25=x['f25'][:3],
                    f24=x['f24'][:3], f29=x['f29'][:3], f21_unparsable=x['f21_bad'], expired_log=x['expired'], expired_stdout=s_exp,
                    pump_stop_expired_log=x['pumpx'], pump_stop_expired_stdout=s_pumpx,
                    logasync_mode=[t[:40] for t, l in x['mode'][:2]], stat_lines=len(x['stat']))
    else:
        lived_w = lived and (att.get('hold_s') or 0) >= HOLD_W_S
        dual = [d for d in x['dual'] if d[0] and g is not None and d[1] < g]
        m = [('lived to the end of the hold (outcome %s, hold_exit %s, hold_s %s >= 310)' % (att.get('outcome'), att.get('hold_exit'),
                                                                                         att.get('hold_s')), lived_w),
             death_m,
             ('0 [Vulkan][E] (%d)' % x['vke'], x['vke'] == 0),
             ('0 limit lines of the layer (%d)' % x['vk_limit'], x['vk_limit'] == 0),
             ('positive control: [Vulkan][W] %d > 0' % x['vkw'], x['vkw'] > 0),
             ('DualSrcBlend: supported=1 enabled=1 before the first GuestOut (%d)' % len(dual), bool(dual)),
             f20_member(x, 1),
             f24_member(x, 1)] + stat_members(x, False)
        f = [f29_member(x, 1),
             f25_member(x, 1),
             f21_member(x, 1),
             mode_member(x),
             ('no VALIDATION_STOP (a [Vulkan][E] line and the process did not live to the end of the hold)',
              not (x['vke'] > 0 and not lived_w)),
             b13_member(x),
             b12_member(x)]
    return m, f, info
''')

func('paths', '''def paths(tag, base=None):
    names = ('installed_before', 'installed_after', 'manifest_cmp', 'glitch', 'installed_sha', 'level', 'sheet')
    if base is not None:
        p = dict((nm, os.path.join(base, nm + '.txt')) for nm in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'), seal=os.path.join(base, 'seal.md'), bin=os.path.join(base, 'bin.exe'),
                 cache_before=os.path.join(base, 'cache_before.tsv'), cache_after=os.path.join(base, 'cache_after.tsv'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % tag), seal=SEAL_PATH, bin=BIN_PATH,
             cache_before=os.path.join(d, 'manifest_before.tsv'), cache_after=os.path.join(d, 'manifest_run.tsv'))
    return p
''')

rep("""        ('json binary_sha256 = FS14 013e1974 (%s)' % (jbin or '-')[:16], jbin == BIN_TAG),
        ('installed during the tag = FS14 013e1974 (%s)' % (inst_t or '-')[:16], inst_t == BIN_TAG),
        ('installed before = after = FS13 abab2196 (%s / %s)' % ((inst_b or '-')[:16], (inst_a or '-')[:16]),
         inst_b == BIN_FS13 and inst_a == BIN_FS13),""",
    """        ('json binary_sha256 = FS15 bfac84be (%s)' % (jbin or '-')[:16], jbin == BIN_TAG),
        ('installed during the tag = FS15 bfac84be (%s)' % (inst_t or '-')[:16], inst_t == BIN_TAG),
        ('installed before = after = FS14 013e1974 (%s / %s)' % ((inst_b or '-')[:16], (inst_a or '-')[:16]),
         inst_b == BIN_INST and inst_a == BIN_INST),""")
rep("""    last_stat = x['stat'][-1] if x is not None and x['stat'] else None
    res['ref'] = dict(""", """    cb, ca = tsv_bytes(p['cache_before']), tsv_bytes(p['cache_after'])
    f20s = xx.get('f20s') or []
    ex = exit_after_quit(x) if x is not None else None
    res['f20_rows'] = dict(
        prep_ms=[a for a, b in xx.get('prep') or []], prep_lines=[b for a, b in xx.get('prep') or []],
        all_pipelines_created_ms=xx.get('allp'), precache_lines=xx.get('precache'), precache_n=xx.get('precache_n'),
        vk_pipeline_cache_lines=xx.get('vkpc'), vk_pipeline_cache_n=xx.get('vkpc_n'),
        blob_pipelinecache_before=None if cb is None else cb.get('_PipelineCache'),
        blob_pipelinecache_after=None if ca is None else ca.get('_PipelineCache'),
        glcache_before=None if cb is None else cb.get('GLCache'), glcache_after=None if ca is None else ca.get('GLCache'),
        shadercache_before=None if cb is None else cb.get('_ShaderCache'), shadercache_after=None if ca is None else ca.get('_ShaderCache'),
        f20stat_lines=len(f20s), f20stat_periodic=len([st for st in f20s if st['when'] == 'periodic']),
        f20stat_unparsable=xx.get('f20s_bad'), f20stat_max_unmatched=max(st['unmatched'] for st in f20s) if f20s else None,
        f20stat_exit=None if ex is None else dict((k, ex[k]) for k in STAT_KEYS),
        f20stat_last=None if not f20s else dict((k, f20s[-1][k]) for k in STAT_KEYS),
        f20_mode_lines=None if x is None else [v for v, l in x['f20']], f20_unparsable=xx.get('f20_bad'), f20_other=xx.get('f20_other'))
    last_stat = x['stat'][-1] if x is not None and x['stat'] else None
    res['ref'] = dict(""")
rep("""    fn = {'v': 'fs13_v', 'w': 'fs13_w', 'z': '-'}[kind]
    res['reading'] = ('ADMITTED, members 710(g)(3)+712(g)(3) %s, members of the form %s %s (no verdict; reading - FS14d)' % (""",
    """    fn = {'v': 'fs14_v', 'w': 'fs14_w', 'z': '-'}[kind]
    res['reading'] = ('ADMITTED, members 730(g)(3) %s, members of the form %s %s (no verdict; reading - FS15d)' % (""")
rep("""        out.append('  MEMBERS 710(g)(3)+712(g)(3) %s' % ('ALL YES' if res['ok'] else 'NOT ALL YES'))""",
    """        out.append('  MEMBERS 730(g)(3) %s' % ('ALL YES' if res['ok'] else 'NOT ALL YES'))""")
rep("""            out.append('  MEMBERS form %s %s' % ({'v': 'fs13_v', 'w': 'fs13_w'}[res['kind']], 'ALL YES' if res['form_ok'] else 'NOT ALL YES'))""",
    """            out.append('  MEMBERS form %s %s' % ({'v': 'fs14_v', 'w': 'fs14_w'}[res['kind']], 'ALL YES' if res['form_ok'] else 'NOT ALL YES'))""")
rep("""    e = res['exit']
    out.append('  ROW exit (not a gate)""", """    r = res['f20_rows']
    out.append('  ROW preparation screen (not a gate): ShaderPreparation ms %s; PipelinePrecache: all pipelines created ms %s' % (
        r['prep_ms'], r['all_pipelines_created_ms']))
    out.append('  ROW PipelinePrecache (not a gate): %s lines; %s' % (r['precache_n'], ' | '.join(r['precache_lines'] or [])))
    out.append('  ROW Vulkan pipeline cache (not a gate): %s lines; %s' % (r['vk_pipeline_cache_n'],
                                                                         ' | '.join(r['vk_pipeline_cache_lines'] or [])))
    out.append('  ROW driver blob (not a gate): _PipelineCache bytes before %s after %s; GLCache bytes before %s after %s; '
               '_ShaderCache bytes before %s after %s' % (r['blob_pipelinecache_before'], r['blob_pipelinecache_after'], r['glcache_before'],
                                                         r['glcache_after'], r['shadercache_before'], r['shadercache_after']))
    out.append('  ROW FixF20Stat (not a gate beyond the members): lines %s (periodic %s, unparsable %s), max unmatched %s; exit after quit %s; '
               'last %s; FixF20: mode= lines %s, unparsable %s, other FixF20 lines %s' % (
                   r['f20stat_lines'], r['f20stat_periodic'], r['f20stat_unparsable'], r['f20stat_max_unmatched'],
                   json.dumps(r['f20stat_exit'], sort_keys=True), json.dumps(r['f20stat_last'], sort_keys=True), r['f20_mode_lines'],
                   r['f20_unparsable'], r['f20_other']))
    e = res['exit']
    out.append('  ROW exit (not a gate)""")

func('table', '''def table(rd):
    out = ['| tag | status | binary_sha256 | members 730(g)(3) | form | FixF20Stat exit (bound/modules/rewritten/unmatched) | prep ms '
           '| all pipelines created ms | _PipelineCache before / after | exit code | close_s | glitches | video index | hold_s |',
           '|' + '---|' * 14]
    if os.path.isdir(rd):
        for t in sorted(os.listdir(rd)):
            js = os.path.join(rd, t, 'read.json')
            if TAG_RX.match(t) and os.path.exists(js):
                r = json.load(open(js, encoding='utf-8'))
                yn = (lambda v: '-' if v is None else ('ALL YES' if v else 'NOT ALL YES'))
                f = r['f20_rows']
                e = f['f20stat_exit']
                es = '-' if not e else '%s/%s/%s/%s' % (e['modules_bound'], e['modules'], e['rewritten'], e['unmatched'])
                out.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s / %s | %s | %s | %s | %s | %s |' % (
                    t, r['status'], (r['binary_sha256'] or '-')[:8], yn(r['ok']), yn(r['form_ok']), es, f['prep_ms'],
                    f['all_pipelines_created_ms'], f['blob_pipelinecache_before'], f['blob_pipelinecache_after'], r['exit']['close_rc'],
                    r['exit']['close_s'], r['ref']['glitches'], r['ref']['video_index'], r['ref']['hold_s']))
    return out
''')
rep("print('reader fs14c_read.py sha256 %s'", "print('reader fs15c_read.py sha256 %s'")
rep("print('usage: fs14c_read.py fs14_v|fs14_w|fs14_z[_r1..3] | --dir D --tag T | --table')",
    "print('usage: fs15c_read.py fs15_v|fs15_w|fs15_z[_r1..3] | --dir D --tag T | --table')")
for w in ('fs14c', 'FS14d', 'BIN_FS13', '710(g)', '712(g)', 'fs13_', 'abab2196', '1925-g'):
    assert w not in s.split('"""', 2)[2], w
assert all(ord(c) < 128 for c in s)
open(os.path.join(HERE, 'fs15c_read.py'), 'w', encoding='ascii', newline='\n').write(s)
print('fs15c_read.py written, %d lines' % s.count('\n'))
print('ALL OK')

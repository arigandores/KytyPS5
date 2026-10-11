"""Track F link F47d (HPP-809; ROADMAP s122 item 708 (g), item 715 (v), (d), item 718 (v)(3), item 722 (g), item 724 (e)(2)): the reader
of ONE tag of the snapshot series of the Sky Garden title (B34).  Rows and admission only, NO VERDICT (G' and the classes are F47e, the
outcome is F47f by item 708 (v)).  ASCII only.

    python f47d_read.py <tag> [--json <out>] [--video]            one tag (files of C:/kyty/f287/f47d)
    python f47d_read.py --dir <fixture dir> --tag <tag> [--json <out>]
        fixture form: log.txt, stdout.txt, es.json, rec.idx, seal.md, and the runs/<tag> files below (same names)
    python f47d_read.py --table [--runs <dir>]                    the table over every runs/<tag>/read.json

TAGS (seal section 3): f47_rd, f47_rd2 (grid R-16..R+17 step 3, R = round(713.0 + 0.1075 * n0 of the admitted f47_rd tag)), f47_hi;
  a repeat _r1.._r3 has the form of its base tag.
FILES of runs/<tag>: installed_pre.txt (sha256 + name before the lock), installed_before.txt (inside the lock), installed_after.txt,
  manifest_cmp.txt, level.txt, grid.txt (rd), rdc_sha.txt (rd: 'sha  name  bytes' per capture), thumbs.txt (rd: thumb_f47d.py output),
  variant_copy.txt (manifest_fs4c.py output of the run-state copy of the variant catalog), free_gib_before.txt, INTERFERENCE (go_f47d.sh:
  display OFF after the tag or a user process during it).
DEFINITIONS (seal section 4):
  named start line  the first line containing 'Level has started:' with a non-empty name (F47a section 1.1); n0 = n of the first
                    'FrameTrace: n=' line after it; P = 713.0 + 0.1075 * n0 (F47b); 'outside the sample' when n0 is not in [185; 374].
  entry line        the first line ending 'GuestOut: Level has started: underwater_aerial_garden'.
  capture span      from a 'RenderDoc: auto capture at frame' line to the first FrameTrace line after the next 'RenderDoc: capture finished'
                    line; a frame >= 1 s (dt_us >= 1 000 000) after the entry line is 'at a capture' when its FrameTrace line is inside a
                    span, else 'outside' (a ROW, F47a section 3.1).
  window events     'Window <id> minimized|restored|resized|size changed|lost keyboard focus' and 'Recovering Vulkan swapchain'.
STATUS: INTERFERENCE - the INTERFERENCE file or >= 1 window event (item 273 (z): an interference does not spend the attempt);
  else ADMITTED when every admission member holds, else NOT_ADMITTED (one repeat _r1, item 708 (g)(3)).
ADMISSION common: tag json; json binary_sha256 = installed pre = before = after, and it is FS13 abab2196 or FS14 013e1974; prereg sha256 =
  seal sha256; env = the form of the tag exactly (no KYTY_FIX_*, KYTY_GAME_PATCH, KYTY_TEST_*, KYTY_GPU_CHECKPOINTS); last
  --vulkan-validation false; guest args -lvl underwater_aerial_garden; hold option 120; log; stdout; entry outcome ok; entry line;
  0 death markers (log and stdout); 0 'GpuHangAbort' lines; 0 'GamePatch:' lines; caches returned (manifest cmp EQUAL); variant copy
  manifest written; free on C: >= 80 GiB before the tag.
ADMISSION rd (F47a section 3.1): '--rd' in the command line; 'RenderDoc: level started at frame' after the named start line; 12
  'RenderDoc: auto capture at frame F (level+X)' lines with the X list = the grid of the tag; 12 'RenderDoc: captured guest flip 1/1';
  12 new captures (rdc_sha.txt lines) and 12 thumbnail rows.
ADMISSION hi (F47a2 section 9, item 715 (a)): no '--rd'; video index present; the member of the knob action: (1) sum img_imp over all
  'FrameTrace-draw' lines = 0; (2) sum (stg_img_pool_b + stg_img_in_b) over 'FrameTrace-x' lines > 0; (4) 'FrameTrace-draw' lines with
  img_imp = 'FrameTrace: n=' lines; (3) the control fs13_v sum img_imp 3 955 > 0 is a constant of the seal (F47a2 imp_fs13_v.out).
ROWS: n0, P; frames >= 1 s at / outside a capture; [Vulkan][E]; skipped draw; the thumbnail rows and the line G (rd); capture bytes;
  free after (rd); video: records, d = last present - last n, the detector of F47a section 1.3 on the title window
  [n_start + d + 600; n_start + d + 950] (hi, with --video): black / white runs with dn = present - d - n_start.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

G = 'C:/kyty/f287/f47d'
SEAL_PATH = G + '/pred/f47d_seal.md'
INST = {'abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73': 'FS13',
        '013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd': 'FS14'}
SKY = 'underwater_aerial_garden'
GRID1 = [729 + 3 * k for k in range(12)]
TAG_RX = re.compile(r'^(f47_rd|f47_rd2|f47_hi)(_r[1-3])?$')
K2_US = 1000000
HOLD_OPT = 120
FREE_MIN = 80
N0_LO, N0_HI = 185, 374
P_A, P_B = 713.0, 0.1075
LO, HI, TK, TW, W, H, BAND_H = 600, 950, 150, 1000, 480, 270, 81
RX_FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
RX_FD = re.compile(rb'^FrameTrace-draw: n=(\d+) .* img_imp=(\d+) img_imp_kb=(\d+) ')
RX_FX = re.compile(rb'^FrameTrace-x: n=(\d+) .* stg_img_pool_b=(\d+) stg_img_in_b=(\d+) ')
RX_RDL = re.compile(rb'RenderDoc: level started at frame (\d+)')
RX_RDA = re.compile(rb'RenderDoc: auto capture at frame (\d+) \(level\+(\d+)\)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
RX_MF = re.compile(r'^manifest \S+ files (\d+) bytes \d+ listsha [0-9a-f]{64}$')
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
M_FLIP11 = b'RenderDoc: captured guest flip 1/1'
M_FIN = b'RenderDoc: capture finished'


def sha_file(path):
    if not path or not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def text(path):
    if not path or not os.path.exists(path):
        return None
    return open(path, 'rb').read().decode('utf-8', 'replace')


def last_flag(cmd, flag):
    v = None
    for i, a in enumerate(cmd or []):
        if a == flag:
            v = cmd[i + 1] if i + 1 < len(cmd) else ''
    return v


def base_of(tag):
    return re.sub(r'_r[1-3]$', '', tag)


def is_rd(tag):
    return base_of(tag) in ('f47_rd', 'f47_rd2')


def grid_of(tag, grid_txt):
    if base_of(tag) == 'f47_rd':
        return GRID1
    try:
        return sorted(int(x) for x in (grid_txt or '').strip().split(',') if x.strip())
    except ValueError:
        return None


def expected_env(tag, grid):
    e = dict(KYTY_GUEST_ARGS='-lvl ' + SKY, KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE=None, KYTY_SAMPLE_GATE=None, KYTY_QUEUE_TRACE='1',
             KYTY_GPU_HANG_ABORT_S='8', KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0')
    if is_rd(tag):
        e.update(KYTY_RD_LEVEL=SKY, KYTY_RD_LEVEL_FRAME=','.join(str(g) for g in grid or []), KYTY_RD_FLIPS='1')
    else:
        e.update(KYTY_HOST_IMPORT_MIN_KB='4194304', KYTY_REC=None)
    return e


def env_diff(env, want):
    bad = []
    for key in sorted(set(env) | set(want)):
        if key not in env:
            bad.append('missing %s' % key)
        elif key not in want:
            bad.append('extra %s=%s' % (key, env[key]))
        elif want[key] is not None and env[key] != want[key]:
            bad.append('%s=%s (want %s)' % (key, env[key], want[key]))
    return bad


def scan(path):
    """One pass over the log."""
    r = dict(named_ln=None, n0=None, entry_ln=None, rdl=[], rda=[], flip11=0, flip_other=0, fin=0, death=[], hang=0, recovering=0, win={},
             gamepatch=0, variant_dir=[], vke=0, skipped=0, ft=[], ge1=[], fd_lines=0, fd_imp=0, fd_kb=0, fx_lines=0, stg_pool=0, stg_in=0, ft_lines=0,
             lines=0, last_n=None)
    ln = 0
    pend = False
    span = False
    after_fin = False
    with open(path, 'rb') as fh:
        for line in fh:
            ln += 1
            if line.startswith(b'FrameTrace: n='):
                m = RX_FT.match(line)
                if m:
                    n, dt = int(m.group(1)), int(m.group(2))
                    r['ft_lines'] += 1
                    r['last_n'] = n
                    if pend:
                        r['n0'], pend = n, False
                    if r['entry_ln'] is not None and dt >= K2_US:
                        r['ge1'].append((n, dt, span))
                    if after_fin:
                        span, after_fin = False, False
                continue
            if line.startswith(b'FrameTrace-draw:'):
                m = RX_FD.match(line)
                if m:
                    r['fd_lines'] += 1
                    r['fd_imp'] += int(m.group(2))
                    r['fd_kb'] += int(m.group(3))
                continue
            if line.startswith(b'FrameTrace-x:'):
                m = RX_FX.match(line)
                if m:
                    r['fx_lines'] += 1
                    r['stg_pool'] += int(m.group(2))
                    r['stg_in'] += int(m.group(3))
                continue
            if line.startswith(b'FrameTrace'):
                continue
            if r['named_ln'] is None and b'Level has started:' in line and line.split(b'started:', 1)[1].strip():
                r['named_ln'] = ln
                pend = True
            if r['entry_ln'] is None and line.rstrip(b'\r\n').endswith(('GuestOut: Level has started: %s' % SKY).encode()):
                r['entry_ln'] = ln
            if b'RenderDoc: ' in line:
                m = RX_RDL.search(line)
                if m:
                    r['rdl'].append((int(m.group(1)), ln))
                m = RX_RDA.search(line)
                if m:
                    r['rda'].append((int(m.group(1)), int(m.group(2)), ln))
                    span, after_fin = True, False
                if M_FLIP11 in line:
                    r['flip11'] += 1
                elif b'RenderDoc: captured guest flip' in line:
                    r['flip_other'] += 1
                if M_FIN in line:
                    r['fin'] += 1
                    if span:
                        after_fin = True
            for dm in DEATH:
                if dm in line and len(r['death']) < 20:
                    r['death'].append(dm.decode())
            if b'GpuHangAbort' in line:
                r['hang'] += 1
            if b'Recovering Vulkan swapchain' in line:
                r['recovering'] += 1
            mw = RX_WIN.search(line)
            if mw:
                k = mw.group(1).decode()
                r['win'][k] = r['win'].get(k, 0) + 1
            if line.startswith(b'GamePatch:'):
                r['gamepatch'] += 1
            if line.startswith(b'Shader translation cache: ') and len(r['variant_dir']) < 4:
                r['variant_dir'].append(line.decode('ascii', 'replace').strip().replace('\\', '/').rsplit('/', 1)[-1])
            if b'[Vulkan][E]' in line:
                r['vke'] += 1
            if b'skipped draw' in line:
                r['skipped'] += 1
    r['lines'] = ln
    return r


def stdout_scan(path):
    if not path or not os.path.exists(path):
        return None
    death = []
    with open(path, 'rb') as f:
        for line in f:
            for dm in DEATH:
                if dm in line and len(death) < 20:
                    death.append(dm.decode())
    return dict(death=death)


def idx_read(path):
    pres = {}
    if not path or not os.path.exists(path):
        return None
    with open(path, 'rb') as fi:
        for raw in fi:
            p = raw.split()
            if len(p) >= 2:
                pres[int(p[0])] = int(p[1])
    return pres


def runs_of(v):
    out = []
    for x in v:
        if out and x == out[-1][1] + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return out


def video_window(mp4, pres, n_start, last_n):
    """The detector of F47a section 1.3 (batch_f47a.py rule) on the title window of a recording."""
    import numpy as np
    if not pres or n_start is None or last_n is None:
        return dict(status='NO_INPUT')
    last_p = pres[max(pres)]
    d = last_p - last_n
    a, b = max(0, n_start + d + LO - 1), n_start + d + HI - 1
    sel = "select='between(n%s%d%s%d)',scale=%d:%d" % (chr(92) + ',', a, chr(92) + ',', b, W, H)
    proc = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', mp4, '-vf', sel, '-vsync', '0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                          capture_output=True)
    if proc.returncode != 0:
        return dict(status='DECODE_FAILED', d=d, window=[a, b])
    arr = np.frombuffer(proc.stdout, dtype=np.uint8)
    nfr = arr.size // (W * H * 3)
    arr = arr[:nfr * W * H * 3].reshape(nfr, H, W, 3)[:, :BAND_H]
    k = (arr.max(axis=3) <= 16).sum(axis=(1, 2))
    w = (arr.min(axis=3) >= 240).sum(axis=(1, 2))
    hk = [a + i for i in range(nfr) if k[i] >= TK]
    hw = [a + i for i in range(nfr) if w[i] >= TW]

    def fmt(rr):
        return [[x, y, pres.get(x), (pres.get(x) - d - n_start) if pres.get(x) is not None else None] for x, y in rr]
    return dict(status='OK', d=d, window=[a, b], decoded=nfr, black_runs=fmt(runs_of(hk)), white_runs=fmt(runs_of(hw)),
                maxK=int(k.max()) if nfr else None, maxW=int(w.max()) if nfr else None)


def paths(tag, base=None):
    names = ('installed_pre', 'installed_before', 'installed_after', 'manifest_cmp', 'level', 'grid', 'rdc_sha', 'thumbs', 'variant_copy',
             'free_gib_before', 'free_gib_after')
    if base is not None:
        p = dict((nm, os.path.join(base, nm + '.txt')) for nm in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'), mp4=os.path.join(base, 'rec.mp4'), seal=os.path.join(base, 'seal.md'),
                 interference=os.path.join(base, 'INTERFERENCE'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % tag), mp4=os.path.join(G, 'rec_%s.mp4' % tag), seal=SEAL_PATH,
             interference=os.path.join(d, 'INTERFERENCE'))
    return p


def read_tag(tag, p, video=False):
    rd = is_rd(tag)
    res = dict(tag=tag, base=base_of(tag), level=SKY, reader_sha256=sha_file(os.path.abspath(__file__)))
    run = json.load(open(p['run'], encoding='utf-8')) if os.path.exists(p['run']) else None
    jbin = (run or {}).get('binary_sha256')
    ipre = ((text(p['installed_pre']) or '').split() or [None])[0]
    ib = (text(p['installed_before']) or '').strip() or None
    ia = (text(p['installed_after']) or '').strip() or None
    seal_sha = sha_file(p['seal'])
    pre = ((run or {}).get('prereg') or {}).get('sha256')
    env = (run or {}).get('env') or {}
    cmd = (run or {}).get('cmdline') or []
    att = ((run or {}).get('attempts') or [{}])[-1]
    mcmp = (text(p['manifest_cmp']) or '').strip().splitlines()
    vcp = (text(p['variant_copy']) or '').strip().splitlines()
    ga = (run or {}).get('guest_args') or ''
    hlev = (text(p['level']) or '').strip() or None
    grid = grid_of(tag, text(p['grid']))
    try:
        free = int((text(p['free_gib_before']) or '').strip())
    except ValueError:
        free = None
    have_log = os.path.exists(p['log'])
    x = scan(p['log']) if have_log else None
    so = stdout_scan(p['stdout'])
    kenv = dict((k, v) for k, v in env.items() if k.startswith(('KYTY_', 'VK_')))
    ebad = env_diff(kenv, expected_env(tag, grid))
    death = ((x or {}).get('death') or []) + ((so or {}).get('death') or [])
    res['binary'] = INST.get(jbin)
    adm = [
        ('tag json present', run is not None),
        ('json binary_sha256 = installed pre = before = after, FS13 abab2196 or FS14 013e1974 (%s %s / %s / %s / %s)' % (
            INST.get(jbin), (jbin or '-')[:16], (ipre or '-')[:16], (ib or '-')[:16], (ia or '-')[:16]),
         jbin in INST and jbin == ipre == ib == ia),
        ('json prereg sha256 = seal sha256 (%s / %s)' % ((pre or '-')[:16], (seal_sha or '-')[:16]), pre is not None and pre == seal_sha),
        ('env = the form of the tag exactly (%s)' % (ebad[:6] or 'exact'), run is not None and not ebad),
        ('last --vulkan-validation false (%s)' % last_flag(cmd, '--vulkan-validation'), last_flag(cmd, '--vulkan-validation') == 'false'),
        (('--rd in the command line' if rd else 'no --rd in the command line'), run is not None and (('--rd' in cmd) == rd)),
        ('guest args -lvl %s (%s; harness %s)' % (SKY, ga, hlev), ga == '-lvl ' + SKY and hlev == SKY),
        ('hold option %d s (%s)' % (HOLD_OPT, (run or {}).get('hold_s')), (run or {}).get('hold_s') == HOLD_OPT),
        ('log present', have_log),
        ('stdout present', so is not None),
        ('entry outcome ok (%s)' % att.get('outcome'), att.get('outcome') == 'ok'),
        ('entry line present (%s)' % (x or {}).get('entry_ln'), x is not None and x['entry_ln'] is not None),
        ('0 death markers (log and stdout) %s' % death[:3], not death and so is not None and x is not None),
        ("0 'GpuHangAbort' lines (%s)" % (x or {}).get('hang'), x is not None and x['hang'] == 0),
        ("0 'GamePatch:' lines (%s)" % (x or {}).get('gamepatch'), x is not None and x['gamepatch'] == 0),
        ('caches returned (manifest_cmp: %s)' % (mcmp[0][:40] if mcmp else '-'), bool(mcmp) and mcmp[0].startswith('manifest cmp EQUAL')),
        ('variant catalog copy with a sha256 manifest, >= 1 file (item 718 (v)(3), F47a3 section 9) (%s)' % (vcp[0][:90] if vcp else '-'),
         bool(vcp) and bool(RX_MF.match(vcp[0])) and int(RX_MF.match(vcp[0]).group(1)) >= 1),
        ("'Shader translation cache:' lines name %s (%s)" % (VARIANT_DIR, (x or {}).get('variant_dir')),
         x is not None and bool(x['variant_dir']) and all(v == VARIANT_DIR for v in x['variant_dir'])),
        ('free on C: >= %d GiB before the tag (%s)' % (FREE_MIN, free), free is not None and free >= FREE_MIN),
    ]
    rows = {}
    if x is not None:
        n0 = x['n0']
        rows['n0'] = n0
        rows['P'] = None if n0 is None else round(P_A + P_B * n0, 2)
        rows['P_outside_sample'] = None if n0 is None else not (N0_LO <= n0 <= N0_HI)
        rows['frames_ge1s_at_capture'] = [(n, dt) for n, dt, s in x['ge1'] if s]
        rows['frames_ge1s_outside'] = [(n, dt) for n, dt, s in x['ge1'] if not s]
        rows['vke'] = x['vke']
        rows['skipped_draw'] = x['skipped']
        rows['window_events'] = x['win']
        rows['recovering'] = x['recovering']
        rows['lines'] = x['lines']
    if rd:
        thumbs = (text(p['thumbs']) or '').splitlines()
        trows = [t for t in thumbs if re.match(r'^k\d\d ', t)]
        gline = next((t for t in thumbs if t.startswith('G ')), None)
        rdc = [t for t in (text(p['rdc_sha']) or '').splitlines() if t.strip()]
        xs = [a[1] for a in (x or {}).get('rda') or []]
        rdl = (x or {}).get('rdl') or []
        nl = (x or {}).get('named_ln')
        adm += [
            ("'RenderDoc: level started at frame' after the named start line (%s; named ln %s)" % (rdl[:1], nl),
             bool(rdl) and nl is not None and rdl[0][1] > nl),
            ("12 'RenderDoc: auto capture at frame F (level+X)' lines, X list = the grid (%s / %s)" % (xs, grid),
             len(xs) == 12 and grid is not None and len(grid) == 12 and xs == grid),
            ("12 'RenderDoc: captured guest flip 1/1' (%s; other flip lines %s)" % ((x or {}).get('flip11'), (x or {}).get('flip_other')),
             x is not None and x['flip11'] == 12 and x['flip_other'] == 0),
            ('12 new captures moved (rdc_sha.txt lines %d)' % len(rdc), len(rdc) == 12),
            ('12 thumbnail rows (%d)' % len(trows), len(trows) == 12 and not any('NO_DECODE' in t for t in trows)),
        ]
        rows['thumbs'] = trows
        rows['G'] = gline
        rows['G_black'] = int(re.search(r'black (\d+)', gline).group(1)) if gline else None
        rows['G_white'] = int(re.search(r'white (\d+)', gline).group(1)) if gline else None
        rows['captures'] = rdc
        rows['capture_finished'] = (x or {}).get('fin')
        rows['rd_frames'] = [(a[0], a[1]) for a in (x or {}).get('rda') or []]
        rows['free_gib_after'] = (text(p['free_gib_after']) or '').strip() or None
        rows['grid'] = grid
    else:
        pres = idx_read(p['idx'])
        adm += [
            ('video index present (records %s)' % (len(pres) if pres else None), bool(pres)),
            ("knob action (1): sum img_imp over 'FrameTrace-draw' = 0 (%s)" % (x or {}).get('fd_imp'), x is not None and x['fd_imp'] == 0),
            ("knob action (2): sum stg_img_pool_b + stg_img_in_b over 'FrameTrace-x' > 0 (%s + %s)" % (
                (x or {}).get('stg_pool'), (x or {}).get('stg_in')), x is not None and x['stg_pool'] + x['stg_in'] > 0),
            ("knob action (4): 'FrameTrace-draw' lines with img_imp = 'FrameTrace: n=' lines (%s / %s)" % (
                (x or {}).get('fd_lines'), (x or {}).get('ft_lines')), x is not None and x['fd_lines'] == x['ft_lines'] and x['ft_lines'] > 0),
        ]
        rows['knob'] = None if x is None else dict(fd_lines=x['fd_lines'], img_imp=x['fd_imp'], img_imp_kb=x['fd_kb'], fx_lines=x['fx_lines'],
                                                   stg_img_pool_b=x['stg_pool'], stg_img_in_b=x['stg_in'], control_fs13_v_img_imp=3955)
        rows['video_records'] = len(pres) if pres else None
        if video and x is not None and pres:
            rows['title_window'] = video_window(p['mp4'], pres, x['n0'], x['last_n'])
    interf = []
    if os.path.exists(p['interference']):
        interf.append((text(p['interference']) or '').strip()[:160])
    if x is not None and (x['win'] or x['recovering']):
        interf.append('window events %s, Recovering Vulkan swapchain %d (item 273 (z))' % (x['win'], x['recovering']))
    res['admission'] = [[a, bool(b)] for a, b in adm]
    res['failed'] = [a for a, b in adm if not b]
    res['interference'] = interf
    if interf:
        res['status'] = 'INTERFERENCE'
    else:
        res['status'] = 'ADMITTED' if not res['failed'] else 'NOT_ADMITTED'
    res['rows'] = rows
    return res


def rows_out(res):
    out = ['tag %s (base %s, level %s, binary %s)  reader sha256 %s' % (res['tag'], res['base'], res['level'], res['binary'],
                                                                          res['reader_sha256'])]
    out.append('  STATUS %s' % res['status'])
    for a, b in res['admission']:
        out.append('    [%s] %s' % ('ok' if b else 'NO', a))
    for i in res['interference']:
        out.append('  INTERFERENCE %s' % i)
    r = res['rows']
    if 'n0' in r:
        out.append('  ROW n0 %s; P = 713.0 + 0.1075 * n0 = %s%s' % (r['n0'], r['P'], '; prediction outside the sample [185; 374]'
                                                                    if r['P_outside_sample'] else ''))
        out.append('  ROW frames >= 1 s after the entry: at a capture %d %s; outside %d %s' % (
            len(r['frames_ge1s_at_capture']), r['frames_ge1s_at_capture'][:14], len(r['frames_ge1s_outside']), r['frames_ge1s_outside'][:6]))
        out.append('  ROW [Vulkan][E] %s; skipped draw %s; window events %s; Recovering %s; log lines %s' % (
            r['vke'], r['skipped_draw'], r['window_events'], r['recovering'], r['lines']))
    if 'thumbs' in r:
        out.append('  ROW grid %s; RenderDoc frames (F, X) %s; capture finished %s; free after %s GiB' % (
            r['grid'], r['rd_frames'], r['capture_finished'], r['free_gib_after']))
        for t in r['thumbs']:
            out.append('  THUMB %s' % t)
        out.append('  %s' % r['G'])
        for c in r['captures']:
            out.append('  RDC %s' % c)
    if 'knob' in r:
        out.append('  ROW knob %s; video records %s' % (json.dumps(r['knob'], sort_keys=True), r['video_records']))
        if r.get('title_window'):
            out.append('  ROW title window %s' % json.dumps(r['title_window'], sort_keys=True)[:900])
    out.append('  READING %s (no verdict; G\' and classes - F47e, outcome - F47f by item 708 (v))' % res['status'])
    return out


def table(rd):
    out = ['| tag | status | binary | n0 | P | G black | G white | captures | ge1 at / outside | img_imp | stg | video |',
           '|' + '---|' * 12]
    if os.path.isdir(rd):
        for t in sorted(os.listdir(rd)):
            js = os.path.join(rd, t, 'read.json')
            if TAG_RX.match(t) and os.path.exists(js):
                r = json.load(open(js, encoding='utf-8'))
                w = r.get('rows') or {}
                k = w.get('knob') or {}
                out.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s / %s | %s | %s | %s |' % (
                    t, r['status'], r.get('binary'), w.get('n0'), w.get('P'), w.get('G_black', '-'), w.get('G_white', '-'),
                    len(w.get('captures') or []) if 'captures' in w else '-', len(w.get('frames_ge1s_at_capture') or []),
                    len(w.get('frames_ge1s_outside') or []), k.get('img_imp', '-'),
                    (k.get('stg_img_pool_b', 0) + k.get('stg_img_in_b', 0)) if k else '-', w.get('video_records', '-')))
    return out


def main(argv):
    if '--table' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        print('reader f47d_read.py sha256 %s' % sha_file(os.path.abspath(__file__)))
        for l in table(rd):
            print(l)
        return 0
    js = argv[argv.index('--json') + 1] if '--json' in argv else None
    if '--dir' in argv:
        tag = argv[argv.index('--tag') + 1]
        p = paths(tag, argv[argv.index('--dir') + 1])
    else:
        tag = argv[0] if argv else ''
        p = paths(tag)
    if not TAG_RX.match(tag):
        print('usage: f47d_read.py <tag> | --dir D --tag T | --table')
        return 2
    res = read_tag(tag, p, video='--video' in argv)
    for l in rows_out(res):
        print(l)
    if js:
        with open(js, 'w', encoding='ascii', newline='\n') as f:
            json.dump(res, f, ensure_ascii=True, sort_keys=True, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

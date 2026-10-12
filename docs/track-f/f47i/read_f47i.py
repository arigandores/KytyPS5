"""Track F link F47i (HPP-826; ROADMAP s122 item 740 (v)(3), item 742 (e), item 744 (g)-(d)): the reader of the tag f47_dt (the
measurement-only code KYTY_DIAG_F47DT on the F47g2 binary 86e42e36).  Admission and rows only, NO VERDICT (the reading by rule (6) of
item 740 (v)(6) is F47j).  Port of C:/kyty/f287/f47d/f47d_read.py (F47d, HPP-809: the common admission, the death markers, the window
events, the detector of F47a section 1.3 on the title window of the video) with the members of item 740 (v)(3) / 742 (e) / 744 (g)-(d).
ASCII only.

    python read_f47i.py <tag> [--json <out>] [--video]          one tag (files of C:/kyty/f287/f47i)
    python read_f47i.py --dir <fixture dir> --tag <tag> [--json <out>] [--video]
        fixture form: log.txt, stdout.txt, es.json, rec.idx, rec.mp4, seal.md, seal_window.txt (the window of the seal) and the
        runs/<tag> files below (same names)
    python read_f47i.py --control <log> <rec.mp4>                the detector on a control recording (fs13_v): black / white series

FILES of runs/<tag>: installed_pre.txt (sha256 + name before the lock), installed_before.txt (inside the lock), installed_after.txt,
  installed_sha.txt (the tag binary after its install), manifest_cmp.txt, level.txt, window.txt (the window WIN of the call),
  free_gib_before.txt, f47dt_files.txt (manifest_fs4c.py output of the moved _f47dt/), flips.txt (dt_f47g2.py flips <log> --window WIN,
  written by post_f47i.sh), INTERFERENCE (go_f47i.sh: display OFF after the tag or a user process during it).
DEFINITIONS (seal):
  named start line  the first line containing 'Level has started:' with a non-empty name; n0 = n of the first 'FrameTrace: n=' line after
                    it (F47a section 1.1).
  entry line        the first line ending 'GuestOut: Level has started: underwater_aerial_garden'.
  d                 last present of the .idx - last n of 'FrameTrace: n=' (F47a section 1.3, F47e section 6).
  title window      video records [n0 + d + 600 - 1; n0 + d + 950 - 1]; 480x270, band y < 81; K = pixels max(R,G,B) <= 16, Wt = pixels
                    min(R,G,B) >= 240; a black series - consecutive records with K >= 150; a white series - with Wt >= 1000.
  show of a record  n = present - d (the FrameTrace n of that show; = q by the admission member of item 742 (e)).
  H line            a 'F47dt: kind=draw' line with ps=45942b26d9ffbe8e; its show is its field q.
  held show         a show q whose flip request rid has the line 'AsyncPipelines: flip <rid> held' (item 744 (d)(2), N3 of F47h2; the
                    emulator logs only the first 64 such lines - the row says when 64 are reached).
STATUS: INTERFERENCE - the INTERFERENCE file, >= 1 window event (item 273 (z)), the member of item 742 (e) / 744 (g)(1) not held
  ('ADMISSION OK' with 'FrameTrace lines' > 0 in the first line of dt_f47g2.py flips - else an interference of the run, RC2 of F47h2),
  or the window form of the edition (f47_dt: item 745, n0 outside [144; 483]; f47_dt_r1: item 746, n0 outside [165; 719] - no second
  repeat, stop and lead item) and a black series show or a white series show missing inside the window;
  INVALID (edition f47_dt_r1, item 746 / F2 of F47h) - 'F47dtStat:' draws > 0 with files=0: stop and lead item; NO_BLOCKS - every other member holds but the title window
  has no black series or no white series (item 708 (b)(9): stop, lead item - the control fs13_v is printed by --control); else ADMITTED
  when every admission member holds, else NOT_ADMITTED (one attempt; a repeat only by the lead's item, item 740 (v)(3)).
EDITIONS (by the tag): f47_dt - seal pred/f47i_seal.md, window pred/window.txt, n0 range [144; 483] (item 745), member 13 = the moved
  _f47dt/ with a manifest; f47_dt_r1 - seal pred/f47i_r1_seal.md, window pred/window_r1.txt, n0 range [165; 719] (item 746), member 13
  of item 746: files=0 and draws=0 - 'no subject' (member 16 decides), draws > 0 with files=0 - INVALID, else the moved _f47dt/ with a
  manifest.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

G = 'C:/kyty/f287/f47i'
EDITIONS = {
    'f47_dt': dict(seal=G + '/pred/f47i_seal.md', win=G + '/pred/window.txt', n0=(144, 483), item='745', m13=False),
    'f47_dt_r1': dict(seal=G + '/pred/f47i_r1_seal.md', win=G + '/pred/window_r1.txt', n0=(165, 719), item='746', m13=True),
}
SEAL_PATH = EDITIONS['f47_dt']['seal']
WIN_PATH = EDITIONS['f47_dt']['win']
DT_READER = 'C:/kyty/KytyPS5/docs/track-f/f47g2/dt_f47g2.py'
DT_READER_SHA = '61a13e294df0e371'
TB = '86e42e36440ac5b7ac7a420c12d7a6aaadc4ffc483145ae9c6d18be046075e82'
INST = 'bfac84bea0eaec8bf3dae6ab5f67cd480f26921829f64f4a8b467bd50e922d8c'
SKY = 'underwater_aerial_garden'
H_PS = '45942b26d9ffbe8e'
TAG_RX = re.compile(r'^f47_dt(_r1)?$')
K2_US = 1000000
HOLD_OPT = 120
FREE_MIN = 40
N0_LO, N0_HI = EDITIONS['f47_dt']['n0']
LO, HI, TK, TW, W, H, BAND_H = 600, 950, 150, 1000, 480, 270, 81
RX_FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_HELD = re.compile(rb'AsyncPipelines: flip (\d+) held')
RX_F47 = re.compile(rb'F47dt: kind=(draw|flip|shown) (.*)$')
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
RX_MF = re.compile(r'^manifest \S+ files (\d+) bytes (\d+) listsha [0-9a-f]{64}$')
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'


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


def window_of(s):
    m = re.match(r'^\s*(\d+)-(\d+)\s*$', s or '')
    return (int(m.group(1)), int(m.group(2))) if m else None


def expected_env(win):
    return dict(KYTY_GUEST_ARGS='-lvl ' + SKY, KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE=None, KYTY_SAMPLE_GATE=None, KYTY_QUEUE_TRACE='1',
                KYTY_GPU_HANG_ABORT_S='8', KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_REC=None, KYTY_DIAG_F47DT='1',
                KYTY_DIAG_F47DT_FRAMES=win, KYTY_STREAM_TRACE='1')


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


def toks(rest):
    out = {}
    for t in rest.split():
        if '=' in t:
            k, v = t.split('=', 1)
            out[k] = v
    return out


def scan(path):
    """One pass over the log."""
    r = dict(named_ln=None, n0=None, entry_ln=None, death=[], hang=0, recovering=0, win={}, gamepatch=0, variant_dir=[], vke=0, skipped=0,
             ge1=[], ft_lines=0, last_n=None, lines=0, held_rids=[], h_q={}, flips={}, shown={}, stat=None, capped=0, mode=None)
    ln = 0
    pend = False
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
                        r['ge1'].append((n, dt))
                continue
            if line.startswith(b'FrameTrace'):
                continue
            j = line.find(b'F47dt')
            if j >= 0:
                s = line[j:].rstrip(b'\r\n')
                if s.startswith(b'F47dtStat:'):
                    r['stat'] = toks(s[len(b'F47dtStat:'):].decode('ascii', 'replace'))
                elif s.startswith(b'F47dt: capped'):
                    r['capped'] += 1
                elif s.startswith(b'F47dt: mode='):
                    r['mode'] = toks(s[len(b'F47dt: '):].decode('ascii', 'replace'))
                else:
                    m = RX_F47.match(s)
                    if m:
                        t = toks(m.group(2).decode('ascii', 'replace'))
                        k = m.group(1)
                        if k == b'draw' and t.get('ps') == H_PS and 'q' in t:
                            q = int(t['q'])
                            r['h_q'][q] = r['h_q'].get(q, 0) + 1
                        elif k == b'flip' and 'q' in t and 'rid' in t:
                            r['flips'][int(t['q'])] = (int(t['rid']), t.get('path'))
                        elif k == b'shown' and 'n' in t and 'rid' in t:
                            r['shown'].setdefault(int(t['rid']), []).append(int(t['n']))
                continue
            if r['named_ln'] is None and b'Level has started:' in line and line.split(b'started:', 1)[1].strip():
                r['named_ln'] = ln
                pend = True
            if r['entry_ln'] is None and line.rstrip(b'\r\n').endswith(('GuestOut: Level has started: %s' % SKY).encode()):
                r['entry_ln'] = ln
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
            mh = RX_HELD.search(line)
            if mh:
                r['held_rids'].append(int(mh.group(1)))
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
    """The detector of F47a section 1.3 on the title window; every run carries [vf_a, vf_b, present_a, n_a, n_b, dn_a]."""
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
        out = []
        for x, y in rr:
            px, py = pres.get(x), pres.get(y)
            out.append([x, y, px, None if px is None else px - d, None if py is None else py - d,
                        None if px is None else px - d - n_start])
        return out
    return dict(status='OK', d=d, window=[a, b], decoded=nfr, black_runs=fmt(runs_of(hk)), white_runs=fmt(runs_of(hw)),
                maxK=int(k.max()) if nfr else None, maxW=int(w.max()) if nfr else None)


def shows_of(runs):
    out = []
    for r in runs or []:
        if r[3] is not None and r[4] is not None:
            out += list(range(r[3], r[4] + 1))
    return out


def paths(tag, base=None):
    names = ('installed_pre', 'installed_before', 'installed_after', 'installed_sha', 'manifest_cmp', 'level', 'window', 'free_gib_before',
             'f47dt_files', 'flips')
    if base is not None:
        p = dict((nm, os.path.join(base, nm + '.txt')) for nm in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'), mp4=os.path.join(base, 'rec.mp4'), seal=os.path.join(base, 'seal.md'),
                 win=os.path.join(base, 'seal_window.txt'), interference=os.path.join(base, 'INTERFERENCE'), dtreader=DT_READER)
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % tag), mp4=os.path.join(G, 'rec_%s.mp4' % tag), seal=EDITIONS[tag]['seal'],
             win=EDITIONS[tag]['win'],
             interference=os.path.join(d, 'INTERFERENCE'), dtreader=DT_READER)
    return p


def read_tag(tag, p, video=False):
    res = dict(tag=tag, level=SKY, reader_sha256=sha_file(os.path.abspath(__file__)))
    ed = EDITIONS[tag]
    n0lo, n0hi = ed['n0']
    run = json.load(open(p['run'], encoding='utf-8')) if os.path.exists(p['run']) else None
    jbin = (run or {}).get('binary_sha256')
    ipre = ((text(p['installed_pre']) or '').split() or [None])[0]
    ib = (text(p['installed_before']) or '').strip() or None
    ia = (text(p['installed_after']) or '').strip() or None
    isha = (text(p['installed_sha']) or '').strip() or None
    seal_sha = sha_file(p['seal'])
    pre = ((run or {}).get('prereg') or {}).get('sha256')
    env = (run or {}).get('env') or {}
    cmd = (run or {}).get('cmdline') or []
    att = ((run or {}).get('attempts') or [{}])[-1]
    mcmp = (text(p['manifest_cmp']) or '').strip().splitlines()
    ga = (run or {}).get('guest_args') or ''
    hlev = (text(p['level']) or '').strip() or None
    win_s = (text(p['win']) or '').strip()
    win = window_of(win_s)
    cwin = (text(p['window']) or '').strip()
    try:
        free = int((text(p['free_gib_before']) or '').strip())
    except ValueError:
        free = None
    dts = sha_file(p['dtreader'])
    have_log = os.path.exists(p['log'])
    x = scan(p['log']) if have_log else None
    so = stdout_scan(p['stdout'])
    kenv = dict((k, v) for k, v in env.items() if k.startswith(('KYTY_', 'VK_')))
    ebad = env_diff(kenv, expected_env(win_s))
    death = ((x or {}).get('death') or []) + ((so or {}).get('death') or [])
    fl = (text(p['flips']) or '').strip().splitlines()
    fl0 = fl[0] if fl else ''
    mft = re.search(r'FrameTrace lines (\d+)', fl0)
    dtf = (text(p['f47dt_files']) or '').strip().splitlines()
    mdt = RX_MF.match(dtf[0]) if dtf else None
    stat = (x or {}).get('stat') or {}
    mode = (x or {}).get('mode') or {}
    adm = [
        ('tag json present', run is not None),
        ('window of the seal %s = window of the call %s' % (win_s or '-', cwin or '-'), win is not None and cwin == win_s),
        ('json binary_sha256 = installed tag binary = F47g2 86e42e36 (%s / %s)' % ((jbin or '-')[:16], (isha or '-')[:16]),
         jbin == TB and isha == TB),
        ('installed pre = before = after = FS15 bfac84be (%s / %s / %s)' % ((ipre or '-')[:16], (ib or '-')[:16], (ia or '-')[:16]),
         ipre == ib == ia == INST),
        ('json prereg sha256 = seal sha256 (%s / %s)' % ((pre or '-')[:16], (seal_sha or '-')[:16]), pre is not None and pre == seal_sha),
        ('env = the form of the tag exactly (%s)' % (ebad[:6] or 'exact'), run is not None and not ebad),
        ('last --vulkan-validation false (%s)' % last_flag(cmd, '--vulkan-validation'), last_flag(cmd, '--vulkan-validation') == 'false'),
        ('no --rd in the command line', run is not None and '--rd' not in cmd),
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
        ("'Shader translation cache:' lines name %s (%s)" % (VARIANT_DIR, (x or {}).get('variant_dir')),
         x is not None and bool(x['variant_dir']) and all(v == VARIANT_DIR for v in x['variant_dir'])),
        ('free on C: >= %d GiB before the tag (%s)' % (FREE_MIN, free), free is not None and free >= FREE_MIN),
        ("'F47dt: mode=1' line with frames = the window (%s)" % (json.dumps(mode, sort_keys=True)[:120] if mode else '-'),
         mode.get('mode') == '1' and mode.get('frames') == win_s),
        ("'F47dtStat: when=exit' with capped=0 and 0 'F47dt: capped' lines (stat capped %s, lines %s)" % (
            stat.get('capped'), (x or {}).get('capped')), stat.get('when') == 'exit' and stat.get('capped') == '0' and x is not None
         and x['capped'] == 0),
        m13_member(ed, stat, dtf, mdt),
        ('reader dt_f47g2.py sha256 %s... (%s)' % (DT_READER_SHA, (dts or '-')[:16]), (dts or '').startswith(DT_READER_SHA)),
    ]
    flips_ok = fl0.startswith('ADMISSION OK') and mft is not None and int(mft.group(1)) > 0
    rows = {}
    nob = False
    wform = False
    if x is not None:
        rows['n0'] = x['n0']
        rows['frames_ge1s_after_entry'] = x['ge1'][:10]
        rows['n_frames_ge1s_after_entry'] = len(x['ge1'])
        rows['vke'] = x['vke']
        rows['skipped_draw'] = x['skipped']
        rows['window_events'] = x['win']
        rows['recovering'] = x['recovering']
        rows['lines'] = x['lines']
        rows['F47dtStat'] = stat
        rows['h_lines'] = sum(x['h_q'].values())
        rows['h_shows'] = len(x['h_q'])
        rows['held_lines'] = len(x['held_rids'])
        rows['held_cap64_reached'] = len(x['held_rids']) >= 64
    if mdt:
        rows['f47dt_files'] = int(mdt.group(1))
        rows['f47dt_bytes'] = int(mdt.group(2))
    pres = idx_read(p['idx'])
    adm.append(('video index present (records %s)' % (len(pres) if pres else None), bool(pres)))
    rows['video_records'] = len(pres) if pres else None
    tw = None
    if video and x is not None and pres:
        tw = video_window(p['mp4'], pres, x['n0'], x['last_n'])
        rows['title_window'] = tw
    if video:
        ok_tw = tw is not None and tw.get('status') == 'OK'
        adm.append(('detector of F47a section 1.3 ran on the title window (%s)' % ((tw or {}).get('status')), ok_tw))
        bl = shows_of((tw or {}).get('black_runs'))
        wh = shows_of((tw or {}).get('white_runs'))
        rows['black_shows'] = bl
        rows['white_shows'] = wh
        nob = ok_tw and (not bl or not wh)
        hq = (x or {}).get('h_q') or {}
        hb = [q for q in bl if q in hq]
        hw = [q for q in wh if q in hq]
        rows['h_in_black_shows'] = hb
        rows['h_in_white_shows'] = hw
        n0 = (x or {}).get('n0')
        wf, rows['n0_in_range'], rows['series_in_window'] = window_form(n0, bl, wh, win, n0lo, n0hi)
        wform = ok_tw and wf
        adm.append(('item 740 (v)(3): an H line (ps=%s) in >= 1 show of a black series and >= 1 show of a white series (black %s, white %s)' % (
            H_PS, hb[:10], hw[:10]), bool(hb) and bool(hw)))
        rows['show_table'] = show_table(x, win, bl, wh) if x is not None and win else []
    interf = []
    if not flips_ok:
        interf.append('item 742 (e) / 744 (g)(1): dt_f47g2.py flips --window not ADMISSION OK with FrameTrace lines > 0 (%s) - an '
                      'interference of the run, repeat by the lead item' % fl0[:160])
    if video and wform:
        interf.append('item %s: n0 %s outside [%d; %d] and the black / white series not both in the window (%s) - an interference of '
                      'the window form, %s' % (ed['item'], (x or {}).get('n0'), n0lo, n0hi, rows['series_in_window'],
                                               'no second repeat: stop and lead item (item 746)' if ed['m13'] else 'repeat by the lead item'))
    if os.path.exists(p['interference']):
        interf.append((text(p['interference']) or '').strip()[:160])
    if x is not None and (x['win'] or x['recovering']):
        interf.append('window events %s, Recovering Vulkan swapchain %d (item 273 (z))' % (x['win'], x['recovering']))
    adm.append(('item 742 (e) + 744 (g)(1): dt_f47g2.py flips --window: ADMISSION OK and FrameTrace lines > 0 in the same line (%s)' % fl0[:160],
                flips_ok))
    res['admission'] = [[a, bool(b)] for a, b in adm]
    res['failed'] = [a for a, b in adm if not b]
    res['interference'] = interf
    res['invalid'] = m13_invalid(ed, stat)
    if res['invalid']:
        res['status'] = 'INVALID'
    elif interf:
        res['status'] = 'INTERFERENCE'
    elif nob and all(b for a, b in adm if not a.startswith('item 740 (v)(3): an H line')):
        res['status'] = 'NO_BLOCKS'
    else:
        res['status'] = 'ADMITTED' if not res['failed'] else 'NOT_ADMITTED'
    res['rows'] = rows
    return res


def m13_invalid(ed, stat):
    """Item 746 (edition f47_dt_r1): 'F47dtStat:' draws > 0 with files=0 - INVALID (F2 of F47h: stop and lead item)."""
    if not ed['m13'] or not stat:
        return None
    try:
        dr, fi = int(stat.get('draws', '')), int(stat.get('files', ''))
    except ValueError:
        return None
    return 'item 746: F47dtStat draws %d > 0 with files=0 - INVALID (F2), stop and lead item' % dr if dr > 0 and fi == 0 else None


def m13_member(ed, stat, dtf, mdt):
    """Member 13: f47_dt - the moved _f47dt/ with a manifest; f47_dt_r1 (item 746) - files=0 and draws=0 'no subject' (member 16
    decides), draws > 0 with files=0 - not held (INVALID), else the moved _f47dt/ with a manifest."""
    man = dtf[0][:90] if dtf else '-'
    if ed['m13'] and stat and stat.get('files') == '0' and stat.get('draws') == '0':
        return ('_f47dt/: F47dtStat files=0 draws=0 - no subject (item 746; member 16 decides) (manifest %s)' % man, True)
    if ed['m13'] and m13_invalid(ed, stat):
        return ('_f47dt/: F47dtStat draws %s with files=0 - INVALID (item 746)' % stat.get('draws'), False)
    return ('_f47dt/ moved out of the emulator folder with a sha256 manifest (%s)' % man, mdt is not None)


def window_form(n0, bl, wh, win, lo=N0_LO, hi=N0_HI):
    """Items 745 / 746: (interference, n0 in [lo; hi], series counts in the window) - the interference of the window form is n0 outside
    [lo; hi] (or unknown) and a black series show or a white series show missing inside the window (f47_dt [144; 483], f47_dt_r1
    [165; 719])."""
    inw_b = [q for q in bl if win and win[0] <= q <= win[1]]
    inw_w = [q for q in wh if win and win[0] <= q <= win[1]]
    inr = n0 is not None and lo <= n0 <= hi
    return (not inr) and (not inw_b or not inw_w), inr, dict(black=len(inw_b), white=len(inw_w))


def show_table(x, win, bl, wh):
    """One row per show q of the window: rid, path, shown n, FrameTrace n present, held, series, number of H draws."""
    held = set(x['held_rids'])
    rows = []
    for q in range(win[0], win[1] + 1):
        f = x['flips'].get(q)
        rid = f[0] if f else None
        rows.append(dict(q=q, rid=rid, path=f[1] if f else None, shown=x['shown'].get(rid) if rid is not None else None,
                         held=rid in held if rid is not None else None,
                         series='black' if q in bl else ('white' if q in wh else '-'), h=x['h_q'].get(q, 0)))
    return rows


def rows_out(res):
    out = ['tag %s (level %s, binary F47g2 86e42e36 for the tag, FS15 bfac84be installed)  reader sha256 %s' % (
        res['tag'], res['level'], res['reader_sha256'])]
    out.append('  STATUS %s' % res['status'])
    for a, b in res['admission']:
        out.append('    [%s] %s' % ('ok' if b else 'NO', a))
    if res.get('invalid'):
        out.append('  INVALID %s' % res['invalid'])
    for i in res['interference']:
        out.append('  INTERFERENCE %s' % i)
    r = res['rows']
    if 'n0' in r:
        out.append('  ROW n0 %s; frames >= 1 s after the entry %s %s; [Vulkan][E] %s; skipped draw %s; window events %s; Recovering %s; '
                   'log lines %s' % (r['n0'], r['n_frames_ge1s_after_entry'], r['frames_ge1s_after_entry'], r['vke'], r['skipped_draw'],
                                     r['window_events'], r['recovering'], r['lines']))
        out.append('  ROW F47dtStat %s; H lines %s in %s shows; held lines %s%s' % (
            json.dumps(r['F47dtStat'], sort_keys=True), r['h_lines'], r['h_shows'], r['held_lines'],
            ' (64 = the emulator log cap, later held flips are not named)' if r['held_cap64_reached'] else ''))
    if 'f47dt_files' in r:
        out.append('  ROW _f47dt files %d bytes %d' % (r['f47dt_files'], r['f47dt_bytes']))
    out.append('  ROW video records %s' % r.get('video_records'))
    if r.get('title_window'):
        out.append('  ROW title window %s' % json.dumps(r['title_window'], sort_keys=True)[:900])
        lo, hi = EDITIONS[res['tag']]['n0'] if res['tag'] in EDITIONS else EDITIONS['f47_dt']['n0']
        out.append('  ROW black shows %s; white shows %s; H in black %s; H in white %s; n0 in [%d; %d] %s; series in the '
                   'window %s' % (r['black_shows'], r['white_shows'], r['h_in_black_shows'], r['h_in_white_shows'], lo, hi,
                                  r.get('n0_in_range'), r.get('series_in_window')))
    if r.get('show_table'):
        out.append('  SHOWS q rid path shown_n held series H')
        for s in r['show_table']:
            if s['h'] or s['series'] != '-' or s['held'] or s['rid'] is None or s['shown'] != [s['q']]:
                out.append('  SHOW %d %s %s %s %s %s %d' % (s['q'], s['rid'], s['path'], s['shown'], 'held' if s['held'] else '-',
                                                            s['series'], s['h']))
        out.append('  SHOWS listed: the shows with H draws, a series, held, no flip line or shown n != q; the others of the window '
                   'have H 0, not held, no series, shown n = q')
    out.append('  READING %s (no verdict; the outcome is F47j by rule (6) of item 740 (v)(6))' % res['status'])
    return out


def control(log, mp4):
    x = scan(log)
    pres = idx_read(mp4 + '.idx')
    tw = video_window(mp4, pres, x['n0'], x['last_n'])
    bl, wh = shows_of(tw.get('black_runs')), shows_of(tw.get('white_runs'))
    return ['control %s sha256 %s: n0 %s, title window %s' % (log, sha_file(log)[:16], x['n0'], json.dumps(tw, sort_keys=True)[:600]),
            'control detector %s: black shows %d, white shows %d' % ('ALIVE' if bl and wh else 'DEAD', len(bl), len(wh))]


def main(argv):
    if argv and argv[0] == '--control':
        print('\n'.join(control(argv[1], argv[2])))
        return 0
    jout = argv[argv.index('--json') + 1] if '--json' in argv else None
    video = '--video' in argv
    if '--dir' in argv:
        base = argv[argv.index('--dir') + 1]
        tag = argv[argv.index('--tag') + 1]
        p = paths(tag, base)
    else:
        tag = argv[0]
        if not TAG_RX.match(tag):
            print('usage: read_f47i.py f47_dt[_r1] [--json F] [--video]')
            return 2
        p = paths(tag)
    res = read_tag(tag, p, video)
    print('\n'.join(rows_out(res)))
    if jout:
        open(jout, 'w', encoding='ascii', newline='\n').write(json.dumps(res, sort_keys=True, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

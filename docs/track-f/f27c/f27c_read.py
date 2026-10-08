"""Track F link F27c (HPP-694; ROADMAP s122 item 631 (v)(4)-(5), (d)): the reader of one tag f27_* - members P1-P6, the driver cache saves
on the hold with their write windows, frames >= 100 ms on the windows, GPU idle windows on the hold and frames >= 100 ms coinciding with
them, and rows (death markers, translations / skipped draw / held lines in the interval of a frame on a window, tempo, interference).  No
verdict (F27d reads by item 631 (d)).  ASCII only.

Sources (imported WITHOUT a change, sha256 checked at import): savewin_f27a.py (scan(): FrameTrace frames with the time stamp before each
line, the save lines 'Vulkan pipeline cache: saved <bytes> ... (<us> us)' with t = the last stamp before the line) and hostdev122.py
(read_gpu_csv, trim_to_busy, idle_windows - the rule util <= 15 % for >= 3 s inside the busy span; idlewin_f27a.py has no functions - it
runs at import - so its +-1 s placement is restated here).  The overlap rule of a frame and a window is savewin_f27a.main restated
(main() prints and does not return): a frame k spans [t(k-1), t(k)], it is on the window [t - us, t] when t(k) >= t - us and
t(k-1) <= t + 0.02 s; the fixture checks the restatement against savewin_f27a.out.txt on the reference log ednn122.

Definitions (seal section 4):
  stable frame Ns = attempts[ok].stable_frame of <tag>.json; t_s = the stamp of FrameTrace Ns (log seconds since the emulator start);
  the hold (letter: '120 s from stable') = log time [t_s, t_s + hold_s], hold_s of the json; a hold frame = n > Ns with t(n) <= t_s+hold_s;
  a save on the hold (letter) = its window intersects the hold; executor variant 'savewin' = savewin_f27a.main's filter last_n >= Ns
  (counts the save at the exit, after WM_CLOSE) - printed beside;
  P1 = >= 1 save on the hold with bytes >= 80 000 000;  P2 = the line 'S-pcw: KYTY_S_PCW=<arm>' with arm 0 (f27_v0*) / 1 (f27_v1*);
  P3 = 'Pipeline cold-test namespace: <salt>' (salt = the tag) and 'Vulkan pipeline cache: loaded <N> bytes from
       _PipelineCache\\PPSA21564.<xxh3(salt)>.bin'; letter N = the size of the copy (salt.txt); executor variant N = the payload of the copy
       (size - header; the loader reads the payload only) - both printed, P3 by the letter;
  P4 = no line 'PipelinePrecache: saved';  P5 = p5.txt 'labels EQUAL' (the manifest of ShaderCache_PPSA21564, ShaderSeeds_PPSA21564,
       _PipelineCache after the tag = the base) and no INTERFERENCE_P5;
  P6 = gpuclk_<tag>.csv of the run's nvidia-smi logger (-lms 500: step 0.5 s) covers [hold_from, hold_to] (first sample <= hold_from, last
       >= hold_to) with every gap inside the hold <= 1.0 s (executor tolerance for the logger jitter; median and max gaps printed);
  frame on a window = a hold frame with dt_us >= 100 000 on the window of a save on the hold;
  GPU idle windows on the hold = idle_windows(trim_to_busy(csv)) intersecting [hold_from, hold_to] (wall clock, stamps of the json);
  a frame >= 100 ms of the hold coincides with an idle window when its wall interval intersects the window: wall = log time + (hold_from -
       t_s), with the placement uncertainty [-1.0, 0] s (hold_from is stamped after the harness read the stable line) - 'strict' (offset
       exact) and 'loose' (the interval widened by 1 s) both printed.
usage: python f27c_read.py <tag> [--json F] [--root DIR]   |   python f27c_read.py --table [--root DIR]   |   --series [--root DIR]
"""
import datetime
import glob
import hashlib
import importlib.util
import json
import os
import re
import statistics
import sys

ROOT = 'C:/kyty/f287/f27c'
SAVEWIN = 'C:/kyty/KytyPS5/docs/track-f/f27a/savewin_f27a.py'
SAVEWIN_SHA = '9fd9977cfa7833042d344f3e3da4b2acd7c247710d025ab01690ac977c7bb31b'
HOSTDEV = 'C:/kyty/s122/hostdev122.py'
HOSTDEV_SHA = '8404ff8c309a2cf723c44262c543343fe55a5a3b2e1c21c264831b8cac935a1c'
P1_BYTES = 80000000
GE100 = 100000
GE1S = 1000000
SLACK_S = 0.02
PLACE_S = 1.0
GAP_MAX_S = 1.0
STAMP = '%Y/%m/%d %H:%M:%S.%f'


def load(path, want, name):
    data = open(path, 'rb').read()
    got = hashlib.sha256(data).hexdigest()
    if got != want:
        raise SystemExit('IMPORT REFUSED %s sha256 %s != %s' % (name, got, want))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SW = load(SAVEWIN, SAVEWIN_SHA, 'savewin_f27a')
HD = load(HOSTDEV, HOSTDEV_SHA, 'hostdev122')

RX = dict(
    pcw=re.compile(rb'^S-pcw: KYTY_S_PCW=(\d+)'),
    ns=re.compile(rb'^Pipeline cold-test namespace: (\S+)'),
    loaded=re.compile(rb'^Vulkan pipeline cache: loaded (\d+) bytes from (\S+)'),
    precache_saved=re.compile(rb'^PipelinePrecache: saved'),
    ft=re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)'),
)
COUNT = {
    'error': b'--- Error ---',
    'unhandled': b'Unhandled host exception',
    'skipped_draw': b'AsyncPipelines: skipped draw',
    'held': b'held (incomplete frame)',
    'gpuhangabort': b'GpuHangAbort',
    'level_started': b'Level has started: rotating_level_day_and_night',
}


def overlaps(frames, w0, t_end):
    """savewin_f27a.main restated: the frames k (k >= 1) whose span [t(k-1), t(k)] meets [w0, t_end + SLACK_S]."""
    out = []
    for k in range(1, len(frames)):
        a = frames[k - 1][2]
        b = frames[k][2]
        if a is None or b is None:
            continue
        if b >= w0 and a <= t_end + SLACK_S:
            out.append((k, frames[k]))
    return out


def lines_pass(path, frames_ge):
    """One pass: members P2-P4, counters, and per frame with dt >= 100 ms the translations / skipped / held lines of its interval."""
    r = dict(pcw=[], ns=[], loaded=[], precache_saved=0, counts=dict((k, 0) for k in COUNT), interval={})
    cur = dict(spirv=0, skipped=0, held=0)
    with open(path, 'rb') as f:
        for l in f:
            m = RX['ft'].match(l)
            if m:
                if int(m.group(2)) >= GE100:
                    r['interval'][int(m.group(1))] = dict(cur)
                cur = dict(spirv=0, skipped=0, held=0)
                continue
            if b'SPIR-V words=' in l:
                cur['spirv'] += 1
            for k, tok in COUNT.items():
                if tok in l:
                    r['counts'][k] += 1
                    if k == 'skipped_draw':
                        cur['skipped'] += 1
                    elif k == 'held':
                        cur['held'] += 1
            m = RX['pcw'].match(l)
            if m:
                r['pcw'].append(int(m.group(1)))
                continue
            m = RX['ns'].match(l)
            if m:
                r['ns'].append(m.group(1).decode('ascii', 'replace'))
                continue
            m = RX['loaded'].match(l)
            if m:
                r['loaded'].append((int(m.group(1)), m.group(2).decode('ascii', 'replace')))
                continue
            if RX['precache_saved'].match(l):
                r['precache_saved'] += 1
    return r


def parse_stamp(s):
    return datetime.datetime.strptime(s, STAMP) if s else None


def read_salt(d):
    p = os.path.join(d, 'salt.txt')
    if not os.path.exists(p):
        return None
    t = open(p, encoding='ascii').read().split()
    kv = {}
    for i in range(0, len(t) - 1):
        if t[i] in ('salt', 'name', 'size', 'sha_src', 'sha_copy', 'header', 'payload'):
            kv[t[i]] = t[i + 1]
    return kv


def arm_of(tag):
    return 0 if tag.startswith('f27_v0') else 1


def read_tag(tag, root=ROOT):
    d = os.path.join(root, 'runs', tag)
    res = dict(tag=tag, arm=arm_of(tag), admitted=True, why=[])
    jp = os.path.join(root, tag + '.json')
    lp = os.path.join(root, 'log_%s.txt' % tag)
    if not os.path.exists(jp) or not os.path.exists(lp):
        res.update(admitted=False, why=['no json or log'])
        return res
    j = json.load(open(jp, encoding='utf-8'))
    res['binary_sha256'] = j.get('binary_sha256')
    ok = [a for a in j.get('attempts', []) if a.get('outcome') == 'ok']
    if not ok:
        res.update(admitted=False, why=['no ok attempt: %s' % [a.get('outcome') for a in j.get('attempts', [])]])
        return res
    a = ok[-1]
    ns_frame = a.get('stable_frame')
    hold_s = a.get('hold_s') or 0.0
    hold_from, hold_to = parse_stamp(a.get('hold_from')), parse_stamp(a.get('hold_to'))
    res.update(stable_frame=ns_frame, hold_s=hold_s, hold_from=a.get('hold_from'), hold_to=a.get('hold_to'),
               hold_exit=a.get('hold_exit'), close_rc=a.get('close_rc'))
    frames, saves = SW.scan(lp)
    idx = dict((fr[0], i) for i, fr in enumerate(frames))
    if ns_frame not in idx or frames[idx[ns_frame]][2] is None:
        res.update(admitted=False, why=['stable frame %s without a stamp' % ns_frame])
        return res
    t_s = frames[idx[ns_frame]][2]
    h1 = t_s + hold_s
    res.update(t_s=t_s, hold_end_log=round(h1, 3))
    hold_frame = lambda fr: fr[0] > ns_frame and fr[2] is not None and fr[2] <= h1  # noqa: E731
    hold_frames = [fr for fr in frames if hold_frame(fr)]
    res['hold_frames'] = len(hold_frames)
    res['hold_ge100'] = [(fr[0], fr[1]) for fr in hold_frames if fr[1] >= GE100]
    res['hold_ge1s'] = [(fr[0], fr[1]) for fr in hold_frames if fr[1] >= GE1S]
    res['hold_dt_mean_us'] = round(sum(fr[1] for fr in hold_frames) / len(hold_frames), 1) if hold_frames else None
    # saves
    rows = []
    for line, nbytes, us, t_end, last_n in saves:
        if t_end is None:
            continue
        w0 = t_end - us / 1e6
        on_hold = t_end >= t_s and w0 <= h1
        lit_sw = last_n >= ns_frame
        if not on_hold and not lit_sw:
            continue
        over = overlaps(frames, w0, t_end)
        on = [(fr[0], fr[1]) for k, fr in over if fr[1] >= GE100 and hold_frame(fr)]
        on_sw = [(fr[0], fr[1]) for k, fr in over if fr[1] >= GE100]
        rows.append(dict(line=line, bytes=nbytes, us=us, window=[round(w0, 3), round(t_end, 3)], last_n=last_n, on_hold=on_hold,
                         savewin=lit_sw, p1=on_hold and nbytes >= P1_BYTES, frames=[over[0][1][0], over[-1][1][0]] if over else None,
                         ge100_on_window=on, ge100_on_window_savewin=on_sw, at_exit=last_n == frames[-1][0]))
    res['saves'] = rows
    res['P1'] = any(r['p1'] for r in rows)
    res['p1_saves'] = sum(1 for r in rows if r['p1'])
    res['frames_on_windows'] = sorted(set(x for r in rows if r['p1'] for x in r['ge100_on_window']))
    res['frames_on_windows_savewin'] = sorted(set(x for r in rows if r['savewin'] and r['bytes'] >= P1_BYTES for x in r['ge100_on_window_savewin']))
    # lines pass
    lp_ = lines_pass(lp, None)
    res['counts'] = lp_['counts']
    res['P2'] = lp_['pcw'] == [res['arm']] if lp_['pcw'] else False
    res['pcw_lines'] = lp_['pcw']
    salt = read_salt(d)
    res['salt'] = salt
    want_ns = tag
    res['ns_lines'] = lp_['ns']
    res['loaded_lines'] = lp_['loaded']
    p3_ns = lp_['ns'] == [want_ns]
    p3_file = p3_n_letter = p3_n_payload = False
    if salt and len(lp_['loaded']) == 1:
        n, path = lp_['loaded'][0]
        p3_file = path.replace('\\', '/') == '_PipelineCache/' + salt.get('name', '?')
        p3_n_letter = str(n) == salt.get('size')
        p3_n_payload = str(n) == salt.get('payload')
    res['P3'] = p3_ns and p3_file and p3_n_letter
    res['P3_variant_payload'] = p3_ns and p3_file and p3_n_payload
    res['p3_parts'] = dict(namespace=p3_ns, file=p3_file, n_eq_size=p3_n_letter, n_eq_payload=p3_n_payload)
    res['P4'] = lp_['precache_saved'] == 0
    res['precache_saved_lines'] = lp_['precache_saved']
    p5 = os.path.join(d, 'p5.txt')
    p5t = open(p5, encoding='ascii').readline().strip() if os.path.exists(p5) else 'no p5.txt'
    res['p5_line'] = p5t
    res['interference_p5'] = os.path.exists(os.path.join(d, 'INTERFERENCE_P5'))
    res['P5'] = p5t.startswith('labels EQUAL') and not res['interference_p5']
    sd = os.path.join(d, 'savedata.txt')
    res['savedata_row'] = open(sd, encoding='ascii').readline().strip() if os.path.exists(sd) else None
    # interval rows of the frames on windows (item 631 (d)(3))
    res['interval_rows'] = dict((str(n), lp_['interval'].get(n)) for n, _ in res['frames_on_windows'])
    # P6 and idle windows
    cp = os.path.join(root, 'gpuclk_%s.csv' % tag)
    res['P6'] = False
    res['idle_on_hold'] = []
    res['idle_coincide_strict'] = []
    res['idle_coincide_loose'] = []
    if os.path.exists(cp) and hold_from and hold_to:
        s = HD.read_gpu_csv(cp)
        ts = [x[0] for x in s]
        inh = [t for t in ts if hold_from <= t <= hold_to]
        gaps = [(b - a).total_seconds() for a, b in zip(ts, ts[1:]) if b >= hold_from and a <= hold_to]
        res['gpu_samples'] = len(s)
        res['gpu_hold_samples'] = len(inh)
        res['gpu_gap_median_s'] = round(statistics.median(gaps), 3) if gaps else None
        res['gpu_gap_max_s'] = round(max(gaps), 3) if gaps else None
        res['P6'] = bool(ts) and ts[0] <= hold_from and ts[-1] >= hold_to and bool(gaps) and max(gaps) <= GAP_MAX_S
        wins = HD.idle_windows(HD.trim_to_busy(s))
        res['idle_windows_run'] = len(wins)
        on = [(w0, w1, dur) for w0, w1, dur in wins if w1 >= hold_from and w0 <= hold_to]
        res['idle_on_hold'] = [[w0.strftime(STAMP)[:-3], w1.strftime(STAMP)[:-3], round(dur, 3)] for w0, w1, dur in on]
        off = hold_from - datetime.timedelta(seconds=t_s)
        for i, fr in enumerate(frames):
            if not hold_frame(fr) or fr[1] < GE100 or i == 0 or frames[i - 1][2] is None:
                continue
            a = off + datetime.timedelta(seconds=frames[i - 1][2])
            b = off + datetime.timedelta(seconds=fr[2])
            for w0, w1, dur in on:
                if b >= w0 and a <= w1:
                    res['idle_coincide_strict'].append((fr[0], fr[1]))
                if b >= w0 and a - datetime.timedelta(seconds=PLACE_S) <= w1:
                    res['idle_coincide_loose'].append((fr[0], fr[1]))
    # tempo row
    tp = os.path.join(d, 'tempo.txt')
    res['tempo'] = open(tp, encoding='ascii').readline().strip() if os.path.exists(tp) else None
    # admission (not members): a death marker, an interference flag
    if res['interference_p5']:
        res['why'].append('INTERFERENCE_P5 (U returned from the base copy)')
    if lp_['counts']['error'] or lp_['counts']['unhandled']:
        res['why'].append('death marker in the log (row)')
    res['admitted'] = not res['interference_p5']
    return res


def members_line(r):
    def yn(x):
        return 'YES' if x else 'NO'
    return 'MEMBERS %s P1 %s (saves on hold with P1 %d) P2 %s P3 %s (variant payload %s) P4 %s P5 %s P6 %s' % (
        r['tag'], yn(r.get('P1')), r.get('p1_saves', 0), yn(r.get('P2')), yn(r.get('P3')), yn(r.get('P3_variant_payload')),
        yn(r.get('P4')), yn(r.get('P5')), yn(r.get('P6')))


def print_tag(r):
    print('tag %s arm KYTY_S_PCW=%d binary %s admitted %s %s' % (r['tag'], r['arm'], (r.get('binary_sha256') or '-')[:16],
                                                              'YES' if r.get('admitted') else 'NO', r.get('why')))
    if 'saves' not in r:
        return
    print('  stable frame %s t_s %.3f hold_s %s hold log [%.3f, %.3f] hold frames %d hold_from %s hold_to %s hold_exit %s' % (
        r['stable_frame'], r['t_s'], r['hold_s'], r['t_s'], r['hold_end_log'], r['hold_frames'], r['hold_from'], r['hold_to'],
        r['hold_exit']))
    for s in r['saves']:
        print('  save line %d bytes %d us %d window [%.3f, %.3f] last_n %d on_hold %s savewin %s at_exit %s P1 %s frames %s ge100 %s'
              ' (savewin %s)' % (s['line'], s['bytes'], s['us'], s['window'][0], s['window'][1], s['last_n'], s['on_hold'], s['savewin'],
                                 s['at_exit'], s['p1'], s['frames'], s['ge100_on_window'], s['ge100_on_window_savewin']))
    print('  frames >= 100 ms on windows (letter) %s; savewin variant %s' % (r['frames_on_windows'], r['frames_on_windows_savewin']))
    print('  interval rows of those frames (spirv / skipped / held): %s' % r['interval_rows'])
    print('  hold frames >= 100 ms %s; >= 1 s %s; mean dt %s us' % (r['hold_ge100'], r['hold_ge1s'], r['hold_dt_mean_us']))
    print('  P2 pcw lines %s; P3 ns %s loaded %s salt %s parts %s; P4 precache saved lines %d; P5 %s; _SaveData row %s' % (
        r['pcw_lines'], r['ns_lines'], r['loaded_lines'], (r['salt'] or {}).get('name'), r['p3_parts'], r['precache_saved_lines'],
        r['p5_line'], r['savedata_row']))
    print('  P6 gpu samples %s in hold %s gap median %s max %s s; idle windows run %s on hold %s; coincide strict %s loose %s' % (
        r.get('gpu_samples'), r.get('gpu_hold_samples'), r.get('gpu_gap_median_s'), r.get('gpu_gap_max_s'), r.get('idle_windows_run'),
        r['idle_on_hold'], r['idle_coincide_strict'], r['idle_coincide_loose']))
    print('  counts %s; tempo %s' % (r['counts'], r['tempo']))
    print('  ' + members_line(r))


def series_state(rs):
    """Item 631 (v)(3), (d)(1): the next tag of the series from the read tags (process helper, not a verdict)."""
    v0 = [r for r in rs if r['tag'].startswith('f27_v0') and r.get('admitted') and 'saves' in r]
    v1 = [r for r in rs if r['tag'].startswith('f27_v1') and r.get('admitted') and 'saves' in r]
    s = sum(r['p1_saves'] for r in v0)
    fr = sum(len(r['frames_on_windows']) for r in v0)
    no_p1 = sum(1 for r in v0 if not r['P1'])
    if not v0:
        return 'NEXT f27_v0'
    if any(len(r['frames_on_windows']) for r in v1):
        return 'STOP (d)(3): a frame >= 100 ms on a write window in a v1 tag'
    if s >= 2 and fr >= 1:
        state = 'CONTROL WITH POWER (d)(1)'
    elif s >= 2 and fr == 0:
        return 'CONTROL WITHOUT POWER (d)(1): v1 tags do not go'
    elif no_p1 >= 2:
        return 'NO_POWER (d)(1): no P1 in the control twice - stop'
    elif len(v0) == 1 and s == 1 and fr == 0:
        return 'NEXT f27_v0b ((v)(3): exactly 1 save with P1 and 0 frames)'
    else:
        return 'UNDEFINED by (v)(3)/(d)(1): v0 saves %d frames %d no_p1 %d - question to the lead' % (s, fr, no_p1)
    names = [r['tag'] for r in v1]
    nop1 = [r['tag'] for r in v1 if not r['P1']]
    if 'f27_v1a' not in names:
        return state + '; NEXT f27_v1a'
    if 'f27_v1b' not in names:
        return state + '; NEXT f27_v1b'
    if nop1 and 'f27_v1c' not in names:
        return state + '; NEXT f27_v1c (a v1 tag without P1)'
    return state + '; SERIES COMPLETE'


def all_tags(root):
    out = []
    for p in sorted(glob.glob(os.path.join(root, 'f27_*.json'))):
        out.append(os.path.basename(p)[:-5])
    return out


def main(argv):
    root = ROOT
    if '--root' in argv:
        i = argv.index('--root')
        root = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if argv and argv[0] in ('--table', '--series'):
        rs = [read_tag(t, root) for t in all_tags(root)]
        if argv[0] == '--table':
            print('tag | arm | binary | admitted | saves on hold P1 (bytes, us, window) | frames >=100 ms on windows | P1..P6 | idle on '
                  'hold | coincide strict/loose | interference')
            for r in rs:
                if 'saves' not in r:
                    print('%s | %d | - | NO %s' % (r['tag'], r['arm'], r['why']))
                    continue
                sv = ['%d/%d/[%.3f,%.3f]' % (s['bytes'], s['us'], s['window'][0], s['window'][1]) for s in r['saves'] if s['p1']]
                print('%s | %d | %s | %s | %s | %s | %s | %d | %s/%s | %s' % (
                    r['tag'], r['arm'], (r.get('binary_sha256') or '-')[:8], 'YES' if r['admitted'] else 'NO', sv,
                    r['frames_on_windows'], members_line(r).split(' ', 2)[2], len(r['idle_on_hold']), r['idle_coincide_strict'],
                    r['idle_coincide_loose'], r['why']))
        print('SERIES ' + series_state(rs))
        return 0
    if not argv:
        print(__doc__.split('\n')[-2])
        return 9
    r = read_tag(argv[0], root)
    print_tag(r)
    if '--json' in argv:
        with open(argv[argv.index('--json') + 1], 'w', encoding='ascii') as f:
            json.dump(r, f, indent=1, default=str)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

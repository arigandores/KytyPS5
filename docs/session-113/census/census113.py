#!/usr/bin/env python3
"""census113.py -- session 113: BDA regime census over archived KytyPS5 run logs.

Offline and read-only with respect to everything outside C:/kyty/s106_stage/bda113/.
Logs are streamed once each, in binary mode, one at a time.

Commands
  python census113.py scan [--budget-s S] [--only SUBSTR]
      Stream every C:/kyty/s*/log_*.txt (sorted by session, then name), skip content
      duplicates (size + sha1 of the first and last MiB) and logs without bda_scan, write one
      cache record per log to bda113/cache/. Resumable. Stops cleanly when the budget is spent
      or when C:/kyty/SEALED_RUN.lock exists (a sealed GPU run must not share the disk).
  python census113.py report
      Build bda113/census.csv and bda113/census_summary.md from the cache.
  python census113.py one <log> [--stable N]
      Analyse one log and print its record as JSON (no cache, no metadata lookup unless found).

Definitions (fixed before any real log was read; the fixtures in test_census113.py pin them)
  row           one `FrameTrace: n=<N>` line joined with the `FrameTrace-draw`/`FrameTrace-x`
                lines carrying the same n (last process segment if n ever restarts)
  stable frame  <tag>.json attempts[].stable_frame of the attempt the log belongs to
                (`_warmup` -> label warmup, `_aN` -> attempt N, plain -> last ok attempt);
                else first `first` of gates_<tag>.json phases minus 1 (old launch_run format);
                else 2100 (`stable_src=default`)
  steady        rows with n > stable frame
  regime        median bda_scan over steady rows: OLD > 500, NEW < 200, MIXED otherwise;
                TOO_FEW when fewer than 60 steady rows carry bda_scan
  established   first non-overlapping 60-row window (from row 0) whose bda_scan median is within
                20 % of the steady median (`est_n` = n of its first row); `settled_n` = first
                60-row window from which every later window has the final class
  window class  OLD/NEW/MID as above, but IDLE when the window median is < 10 (no scanning at all)
  switch        steady 300-row windows (>= 150 values) containing both OLD and NEW classes;
                `switch_n` = first row n of the first window whose class differs from the first
  arm_dependent a gate schedule run whose per-arm steady bda_scan medians fall in different classes
  phases        start = first 300 rows of the log; first600 = first 600 steady rows; steady = all
  k classes     per flip: k0 bda_scan < 500, k1 500..1549, k2 1550..2599, k3p >= 2600 (bda_scan is
                observed to be base + k * ~1014); hi = share of flips with bda_scan >= 500
  episodes      steady 60-row windows, classes OLD/NEW (IDLE/MID/None neutral), runs of >= 5 windows
                (300 flips) kept and merged: `episodes` = 'CLS@n,...', `persist_switches` = len - 1
  regime_clean  ARMDEP if arm_dependent; SWITCH if steady 300-windows hold both OLD and NEW and the
                minority class has >= 2 windows or >= 25 % of them; else the median regime
                (`transient_windows` = minority 300-windows of a run that stayed OLD/NEW)
  per-flip link P(hi | c > 0) and P(hi | c == 0) over steady flips for c in buf_new, img_new (same
                flip, and c of the previous flip: `_lag1`)
"""
import argparse
import csv
import glob
import hashlib
import json
import math
import os
import re
import statistics
import sys
import time

ROOT = 'C:/kyty/s106_stage/bda113'
LOG_GLOB = 'C:/kyty/s*/log_*.txt'
JSON_GLOB = 'C:/kyty/s*/*.json'
LOCK = 'C:/kyty/SEALED_RUN.lock'

OLD_MIN = 500.0
NEW_MAX = 200.0
EST_WIN = 60
EST_TOL = 0.20
CHG_WIN = 300
CHG_MIN_VALUES = 150
START_ROWS = 300
FIRST_STEADY = 600
DEFAULT_STABLE = 2100
MIN_STEADY = 60
NO_DRAW_GIVEUP = 3000
DRS_BASE = 2016.0
DRS_HI = 1.1 * DRS_BASE
CACHE_VERSION = 6
SCENE_DRAWS = 1000
SLOW_DT_US = 100000.0   # mean steady flip > 100 ms: hung / validation-speed run, kept out of comparisons
K_EDGES = (500, 1550, 2600)
EPISODE_MIN_WIN = 5
LINK_COUNTERS = ('buf_new', 'img_new')

# Counters asked for, wherever they are printed (main line wins on a name clash).
COUNTERS = ['dt_us', 'cpu_gpu_us', 'spin_gpu_us', 'gpu_busy_us', 'draws', 'bda_scan', 'bda_skip',
            'bda_n', 'bda_scan_us', 'buf_new', 'buf_new_us', 'bufepoch', 'img_new', 'img_up',
            'up_series', 'sync_up_kb', 'prot_us', 'prot_gpu_us', 'fbp_n', 'fbp_ns', 'faults',
            'fault_us', 'faults_gpu', 'fault_gpu_us', 'a_mut_us', 'da_take_us']
EXTRA = ['n', 'arm', 'blk', 'rt_kpx', 'rt_att']
PREFIXES = [b'buflru_']
WANTED = set(n.encode() for n in COUNTERS + EXTRA)
LINE_TYPES = ((b'FrameTrace: ', 'main'), (b'FrameTrace-draw: ', 'draw'), (b'FrameTrace-x: ', 'x'))

ENV_KEYS = ['KYTY_GATE_SCHEDULE', 'KYTY_PIPELINE_PRECACHE', 'KYTY_GPU_CLOCK_PIN', 'KYTY_GUEST_ARGS',
            'KYTY_REC', 'KYTY_FRAME_TRACE', 'KYTY_GPU_TIME', 'KYTY_PIPELINE_CACHE', 'KYTY_SHADER_CACHE',
            'KYTY_KEYS']


# ----------------------------------------------------------------------------------------------
# small helpers

def session_of(path):
    m = re.search(r'[/\\]s(\d+)[/\\]', path.replace('\\', '/') + '/')
    return int(m.group(1)) if m else -1


def median(vals):
    vals = [v for v in vals if v is not None]
    return statistics.median(vals) if vals else None


def classify(v):
    if v is None:
        return None
    if v > OLD_MIN:
        return 'OLD'
    if v < NEW_MAX:
        return 'NEW'
    return 'MID'


IDLE_MAX = 10.0


def wclass(v):
    """Window class: like classify, but a window whose median is below IDLE_MAX (menus, loading,
    no PrepareBda scanning at all) is IDLE, not NEW -- it carries no regime signal."""
    if v is not None and v < IDLE_MAX:
        return 'IDLE'
    return classify(v)


def num(b):
    try:
        return int(b)
    except ValueError:
        try:
            v = float(b)
            return v if math.isfinite(v) else None
        except ValueError:
            return None


def content_key(path):
    size = os.path.getsize(path)
    h = hashlib.sha1()
    with open(path, 'rb') as fh:
        h.update(fh.read(1 << 20))
        if size > (2 << 20):
            fh.seek(size - (1 << 20))
        h.update(fh.read(1 << 20))
    return '%d:%s' % (size, h.hexdigest())


def runlength(classes):
    out = []
    for c in classes:
        c = c or '-'
        if out and out[-1][0] == c:
            out[-1][1] += 1
        else:
            out.append([c, 1])
    return ','.join('%s*%d' % (c, k) for c, k in out)


# ----------------------------------------------------------------------------------------------
# log streaming

class Layout:
    """Token positions of the wanted fields in one line type; rebuilt when a line disagrees."""

    def __init__(self):
        self.pos = None  # list of (index, name_bytes_with_eq, name_str)

    def build(self, toks):
        pos = []
        for i, t in enumerate(toks):
            k = t.find(b'=')
            if k <= 0:
                continue
            name = t[:k]
            if name in WANTED or any(name.startswith(p) for p in PREFIXES):
                pos.append((i, name + b'=', name.decode()))
        self.pos = pos

    def parse(self, toks):
        if self.pos is None:
            self.build(toks)
        out = {}
        for i, eq, name in self.pos:
            if i >= len(toks) or not toks[i].startswith(eq):
                self.build(toks)
                return self.parse_built(toks)
            out[name] = num(toks[i][len(eq):])
        return out

    def parse_built(self, toks):
        out = {}
        for i, eq, name in self.pos:
            out[name] = num(toks[i][len(eq):])
        return out


def read_log(path):
    """Stream one log. Returns (status, segments(list of row lists), markers)."""
    layouts = {'main': Layout(), 'draw': Layout(), 'x': Layout()}
    segments = []
    rows = []
    by_n = {}
    last_main_n = None
    n_main = 0
    n_draw = 0
    status = 'ok'
    mk = dict(guest_args=None, argv=[], pin=None, precache=None, levels=[], gatearm_n=0,
              gatearm_first_frame=None, gatearm_first_text=None, gate_changes=0, gate_bda=[],
              fatal=None, gpu_time_lines=0)
    with open(path, 'rb', buffering=1 << 24) as fh:
        for ln in fh:
            if ln[:10] == b'FrameTrace':
                for pre, kind in LINE_TYPES:
                    if ln.startswith(pre):
                        break
                else:
                    continue
                if kind == 'draw':
                    if n_draw == 0 and b' bda_scan=' not in ln:
                        status = 'no_bda_scan'
                        break
                    n_draw += 1
                toks = ln.split()
                vals = layouts[kind].parse(toks)
                n = vals.get('n')
                if n is None:
                    continue
                if kind == 'main':
                    n_main += 1
                    if last_main_n is not None and n <= last_main_n:
                        segments.append(rows)
                        rows = []
                        by_n = {}
                    last_main_n = n
                    row = by_n.get(n)
                    if row is None:
                        row = {}
                        by_n[n] = row
                    row.update(vals)
                    rows.append(row)
                    if n_draw == 0 and n_main >= NO_DRAW_GIVEUP:
                        status = 'no_draw_lines'
                        break
                else:
                    row = by_n.get(n)
                    if row is None:
                        row = {}
                        by_n[n] = row
                    for k, v in vals.items():
                        if k not in row:
                            row[k] = v
                continue
            c = ln[:1]
            if c == b'G':
                if ln.startswith(b'GateArm: '):
                    mk['gatearm_n'] += 1
                    if mk['gatearm_first_frame'] is None:
                        m = re.search(rb' frame=(\d+)', ln)
                        mk['gatearm_first_frame'] = int(m.group(1)) if m else None
                        t = ln.find(b' text=')
                        mk['gatearm_first_text'] = ln[t + 6:].strip().decode('latin1')[:200] if t >= 0 else None
                elif ln.startswith(b'Gate: '):
                    mk['gate_changes'] += 1
                    if b'bda' in ln and len(mk['gate_bda']) < 20:
                        mk['gate_bda'].append(ln.strip().decode('latin1')[:120])
                elif ln.startswith(b'GuestOut: Level has started: '):
                    name = ln[len(b'GuestOut: Level has started: '):].strip().decode('latin1')
                    if name and len(mk['levels']) < 12:
                        mk['levels'].append([name, last_main_n])
                elif ln.startswith(b'GuestArgs: source='):
                    mk['guest_args'] = ln.strip().decode('latin1')[:160]
                elif ln.startswith(b'GuestArgs:   argv[') and len(mk['argv']) < 8:
                    t = ln.find(b'= ')
                    mk['argv'].append(ln[t + 2:].strip().decode('latin1')[:80])
                elif ln.startswith(b'GpuClockPin: mode '):
                    if mk['pin'] is None:
                        mk['pin'] = ln[len(b'GpuClockPin: mode '):].split()[0].decode('latin1')
                elif ln.startswith(b'GpuHangAbort:'):
                    if mk['fatal'] is None:
                        mk['fatal'] = ln.strip().decode('latin1')[:160]
                elif ln.startswith(b'GpuTime'):
                    mk['gpu_time_lines'] += 1
            elif c == b'P':
                if mk['precache'] is None and ln.startswith(b'PipelinePrecache: '):
                    mk['precache'] = ln.strip().decode('latin1')[:200]
            elif c == b'-':
                if mk['fatal'] is None and (ln.startswith(b'--- Error') or ln.startswith(b'--- Fatal')
                                            or ln.startswith(b'--- std::terminate')
                                            or ln.startswith(b'--- abort')):
                    mk['fatal'] = ln.strip().decode('latin1')[:160]
    if status == 'ok' and n_draw == 0:
        status = 'no_draw_lines'
    segments.append(rows)
    mk['n_main'] = n_main
    mk['n_draw'] = n_draw
    return status, [s for s in segments if s], mk


# ----------------------------------------------------------------------------------------------
# analysis of one log's rows

def windows(values, size, min_values):
    """Non-overlapping windows over a list (None allowed): [(start_index, median, count)]."""
    out = []
    for s in range(0, len(values), size):
        w = [v for v in values[s:s + size] if v is not None]
        if len(w) >= min_values:
            out.append((s, statistics.median(w), len(w)))
    return out


def phase_medians(rows, names):
    out = {}
    for name in names:
        out[name] = median([r.get(name) for r in rows])
    return out


def kfrac(vals):
    v = [x for x in vals if x is not None]
    if not v:
        return None
    n = float(len(v))
    a, b, c = K_EDGES
    return dict(n=len(v), hi=sum(1 for x in v if x >= a) / n, k0=sum(1 for x in v if x < a) / n,
                k1=sum(1 for x in v if a <= x < b) / n, k2=sum(1 for x in v if b <= x < c) / n,
                k3p=sum(1 for x in v if x >= c) / n, mean=sum(v) / n)


def link(rows, name, lag):
    """P(bda_scan >= 500 | name > 0) and P(... | name == 0), name taken `lag` flips earlier."""
    pos = [0, 0]
    zer = [0, 0]
    for i in range(lag, len(rows)):
        b = rows[i].get('bda_scan')
        c = rows[i - lag].get(name)
        if b is None or c is None:
            continue
        t = pos if c > 0 else zer
        t[0] += 1
        t[1] += 1 if b >= K_EDGES[0] else 0
    tot = pos[0] + zer[0]
    return dict(p_pos=(pos[1] / pos[0]) if pos[0] else None, p_zero=(zer[1] / zer[0]) if zer[0] else None,
                pos_frac=(pos[0] / tot) if tot else None, n=tot)


def episodes(steady):
    vals = [r.get('bda_scan') for r in steady]
    runs = []
    for s, m, _ in windows(vals, EST_WIN, EST_WIN // 2):
        c = wclass(m)
        c = c if c in ('OLD', 'NEW') else 'X'
        if runs and runs[-1][0] == c:
            runs[-1][2] += 1
        else:
            runs.append([c, s, 1])
    merged = []
    for c, s, k in runs:
        if c == 'X' or k < EPISODE_MIN_WIN:
            continue
        e = s + k * EST_WIN
        if merged and merged[-1][0] == c:
            merged[-1][2] = e
        else:
            merged.append([c, s, e])
    text = ','.join('%s@%s' % (c, steady[s].get('n')) for c, s, e in merged)
    stats = []
    for c, s, e in merged:
        seg = steady[s:e]

        def mean(k):
            v = [r.get(k) for r in seg if r.get(k) is not None]
            return (sum(v) / len(v)) if v else None
        stats.append(dict(cls=c, n0=seg[0].get('n'), n1=seg[-1].get('n'), rows=len(seg), dt_mean=mean('dt_us'),
                          cpu_gpu_mean=mean('cpu_gpu_us'), gpu_busy_mean=mean('gpu_busy_us'),
                          buf_new_mean=mean('buf_new')))
    return text, (len(merged) - 1 if merged else 0), stats


def episode_diff(stats, key='dt_mean'):
    """Row-weighted mean of `key` over OLD episodes minus that over NEW episodes (None unless both)."""
    acc = {}
    for st in stats:
        if st.get(key) is None:
            continue
        a = acc.setdefault(st['cls'], [0.0, 0])
        a[0] += st[key] * st['rows']
        a[1] += st['rows']
    if 'OLD' in acc and 'NEW' in acc and acc['OLD'][1] and acc['NEW'][1]:
        return acc['OLD'][0] / acc['OLD'][1] - acc['NEW'][0] / acc['NEW'][1]
    return None


def analyse_rows(rows, stable, stable_src):
    res = {}
    ns = [r.get('n') for r in rows]
    res['rows'] = len(rows)
    res['n_first'] = ns[0] if ns else None
    res['n_last'] = ns[-1] if ns else None
    res['stable_frame'] = stable
    res['stable_src'] = stable_src
    i0 = None
    for i, n in enumerate(ns):
        if n is not None and n > stable:
            i0 = i
            break
    steady = rows[i0:] if i0 is not None else []
    first600 = steady[:FIRST_STEADY]
    start = rows[:START_ROWS]
    res['steady_rows'] = len(steady)
    bda_all = [r.get('bda_scan') for r in rows]
    bda_steady = [r.get('bda_scan') for r in steady if r.get('bda_scan') is not None]
    final = statistics.median(bda_steady) if len(bda_steady) >= MIN_STEADY else None
    res['bda_steady_median'] = final
    res['regime'] = 'TOO_FEW' if final is None else {'OLD': 'OLD', 'NEW': 'NEW', 'MID': 'MIXED'}[classify(final)]
    res['bda_start_median'] = median(bda_all[:START_ROWS])
    res['bda_first600_median'] = median([r.get('bda_scan') for r in first600])
    # establishment
    res['est_n'] = res['est_row'] = res['settled_n'] = None
    w60 = windows(bda_all, EST_WIN, EST_WIN // 2)
    if final is not None:
        for s, m, _ in w60:
            if (final == 0 and m == 0) or (final != 0 and abs(m - final) <= EST_TOL * abs(final)):
                res['est_row'] = s
                res['est_n'] = ns[s]
                break
        fc = classify(final)
        settled = None
        for s, m, _ in reversed(w60):
            if wclass(m) != fc:
                break
            settled = s
        res['settled_n'] = ns[settled] if settled is not None else None
    res['w60_classes'] = runlength([wclass(m) for _, m, _ in w60])
    # load burst: class of the first in-scene 60-row window (median draws >= SCENE_DRAWS), and the first
    # in-scene window of class NEW
    wd = {s: m for s, m, _ in windows([r.get('draws') for r in rows], EST_WIN, EST_WIN // 2)}
    scene_w = [(s, m) for s, m, _ in w60 if wd.get(s) is not None and wd[s] >= SCENE_DRAWS]
    res['load_burst'] = wclass(scene_w[0][1]) if scene_w else None
    res['load_burst_n'] = ns[scene_w[0][0]] if scene_w else None
    k0s = next((s for s, m in scene_w if wclass(m) == 'NEW'), None)
    res['first_k0_scene_n'] = ns[k0s] if k0s is not None else None
    # changes over the steady part (300-row windows)
    steady_bda = [r.get('bda_scan') for r in steady]
    w300 = windows(steady_bda, CHG_WIN, CHG_MIN_VALUES)
    cls = [wclass(m) for _, m, _ in w300]
    res['steady_w300'] = runlength(cls)
    res['steady_w300_list'] = cls
    res['steady_w300_mid'] = sum(1 for c in cls if c == 'MID')
    o, nw = cls.count('OLD'), cls.count('NEW')
    res['transient_windows'] = min(o, nw)
    res['episodes'], res['persist_switches'], res['episode_stats'] = episodes(steady)
    res['ep_dt_old_minus_new'] = episode_diff(res['episode_stats'], 'dt_mean')
    res['ep_cpu_old_minus_new'] = episode_diff(res['episode_stats'], 'cpu_gpu_mean')
    res['ep_gpu_old_minus_new'] = episode_diff(res['episode_stats'], 'gpu_busy_mean')
    res['k'] = {'start': kfrac(bda_all[:START_ROWS]), 'first600': kfrac([r.get('bda_scan') for r in first600]),
                'steady': kfrac(steady_bda)}
    res['k0_med'] = median([v for v in steady_bda if v is not None and v < NEW_MAX])
    res['k1_med'] = median([v for v in steady_bda if v is not None and K_EDGES[0] <= v < K_EDGES[1]])
    res['link'] = {}
    for c in LINK_COUNTERS:
        res['link'][c] = link(steady, c, 0)
        res['link'][c + '_lag1'] = link(steady, c, 1)
    res['switched'] = ('OLD' in cls and 'NEW' in cls)
    res['switch_n'] = None
    first_c = next((c for c in cls if c in ('OLD', 'NEW')), None)
    for (s, m, _), c in zip(w300, cls):
        if c in ('OLD', 'NEW') and c != first_c:
            res['switch_n'] = steady[s].get('n')
            break
    # changes after establishment over all rows
    if res['est_row'] is not None:
        wpost = windows(bda_all[res['est_row']:], CHG_WIN, CHG_MIN_VALUES)
        pc = [wclass(m) for _, m, _ in wpost if wclass(m) in ('OLD', 'NEW')]
        res['post_est_changes'] = sum(1 for a, b in zip(pc, pc[1:]) if a != b)
    else:
        res['post_est_changes'] = None
    # medians per phase
    names = list(COUNTERS)
    extra = sorted({k for r in steady[:50] + start[:50] + rows[-50:] for k in r if k.startswith('buflru_')})
    names += extra
    res['buflru_fields'] = extra
    res['med'] = {'start': phase_medians(start, names), 'first600': phase_medians(first600, names),
                  'steady': phase_medians(steady, names)}
    dts = [r.get('dt_us') for r in steady if r.get('dt_us') is not None]
    res['dt_mean_steady'] = (sum(dts) / len(dts)) if dts else None
    # DRS indication
    ratios = [r['rt_kpx'] / r['rt_att'] for r in steady
              if r.get('rt_att') and r.get('rt_kpx') is not None]
    res['drs_ratio_median'] = statistics.median(ratios) if ratios else None
    res['drs_hi_frac'] = (sum(1 for x in ratios if x > DRS_HI) / len(ratios)) if ratios else None
    return res


def analyse_arms(rows, res, stable, gatearm_first_frame):
    res['arm_bda'] = None
    res['arm_dt'] = None
    res['arm_dependent'] = False
    if gatearm_first_frame is None:
        return
    groups = {}
    for r in rows:
        n = r.get('n')
        if n is None or n <= stable or n < gatearm_first_frame or r.get('arm') is None:
            continue
        groups.setdefault(int(r['arm']), []).append(r)
    if not groups:
        return
    res['arm_bda'] = {str(a): median([r.get('bda_scan') for r in g]) for a, g in sorted(groups.items())}
    res['arm_dt'] = {str(a): median([r.get('dt_us') for r in g]) for a, g in sorted(groups.items())}
    res['arm_rows'] = {str(a): len(g) for a, g in sorted(groups.items())}
    classes = {classify(v) for v in res['arm_bda'].values() if v is not None}
    res['arm_dependent'] = len(classes) > 1


# ----------------------------------------------------------------------------------------------
# run metadata

def json_index(pattern=JSON_GLOB):
    idx = {}
    for p in glob.glob(pattern):
        p = p.replace('\\', '/')
        idx.setdefault(os.path.basename(p)[:-5], []).append(p)
    for k in idx:
        idx[k].sort(key=lambda p: (session_of(p), p))
    return idx


def _load(p):
    try:
        with open(p, 'rb') as fh:
            return json.loads(fh.read().decode('utf8', 'replace'))
    except Exception:
        return None


def pick_attempt(attempts, suffix):
    if not attempts:
        return None
    if suffix == 'warmup':
        for a in attempts:
            if a.get('label') == 'warmup':
                return a
        return None
    if suffix and suffix.startswith('a') and suffix[1:].isdigit():
        k = int(suffix[1:])
        for a in attempts:
            if a.get('attempt') == k and a.get('label') != 'warmup':
                return a
        return None
    ok = [a for a in attempts if a.get('stable_frame') is not None and a.get('outcome') == 'ok']
    if ok:
        return ok[-1]
    withf = [a for a in attempts if a.get('stable_frame') is not None]
    return withf[-1] if withf else attempts[-1]


def find_meta(logpath, idx):
    logpath = logpath.replace('\\', '/')
    folder = os.path.dirname(logpath)
    tag = os.path.basename(logpath)[4:-4]
    m = re.match(r'^(.*)_(warmup|a\d+)$', tag)
    tries = [(tag, None)] + ([(m.group(1), m.group(2))] if m else [])
    sess = session_of(logpath)
    found = None
    for t, suffix in tries:
        p = folder + '/' + t + '.json'
        if os.path.exists(p):
            found = (p, t, suffix)
            break
    if found is None:
        for t, suffix in tries:
            for p in idx.get(t, []):
                if session_of(p) >= sess and os.path.dirname(p) != folder:
                    found = (p, t, suffix)
                    break
            if found:
                break
    meta = dict(tag=tag, json_path=None, sha='', env={}, gates='', stable=None, stable_src=None,
                attempt_label=None, attempt_outcome=None, hold_s=None, started=None, scene=None,
                schedule=None, phases_path=None, document_s=None, level_started_s=None, stable_s=None,
                validation=False, attempt_ambiguous=False)
    if found:
        p, t, suffix = found
        d = _load(p)
        if isinstance(d, dict) and d.get('tag') in (None, t):
            meta['json_path'] = p
            meta['sha'] = d.get('binary_sha256') or d.get('sha256') or ''
            meta['env'] = d.get('env') or {}
            g = d.get('gates')
            meta['gates'] = g if isinstance(g, str) else ''
            meta['schedule'] = d.get('schedule') or meta['env'].get('KYTY_GATE_SCHEDULE')
            meta['started'] = d.get('started') or d.get('launched')
            cmd = d.get('cmdline') or d.get('args') or []
            if isinstance(cmd, list):
                cmd = [str(c) for c in cmd]
                meta['validation'] = any(c == '--vulkan-validation' and i + 1 < len(cmd) and cmd[i + 1].lower() == 'true'
                                         for i, c in enumerate(cmd)) or \
                    str(meta['env'].get('KYTY_MEASURE_VALIDATION', '')) not in ('', '0')
            att = pick_attempt(d.get('attempts') or [], suffix)
            if att and suffix and suffix != 'warmup' and os.path.exists('%s/log_%s.txt' % (folder, t)) \
                    and pick_attempt(d.get('attempts') or [], None) is att:
                # the plain log is the same attempt: this _aN process is not described by the json
                meta['attempt_ambiguous'] = True
                att = None
                meta['attempt_label'] = suffix
            if att:
                meta['stable'] = att.get('stable_frame')
                meta['attempt_label'] = att.get('label')
                meta['attempt_outcome'] = att.get('outcome')
                meta['hold_s'] = att.get('hold_s') if att.get('hold_s') is not None else d.get('hold_s')
                meta['scene'] = att.get('level')
                meta['document_s'] = att.get('document_s')
                meta['level_started_s'] = att.get('started_s')
                meta['stable_s'] = att.get('stable_s')
            elif suffix:
                meta['attempt_label'] = suffix
            if meta['stable'] is not None:
                meta['stable_src'] = 'json'
            ga = d.get('guest_args') or meta['env'].get('KYTY_GUEST_ARGS')
            if not meta['scene'] and ga:
                mm = re.search(r'-lvl\s+(\S+)', ga)
                meta['scene'] = mm.group(1) if mm else ga
    if meta['stable'] is None:
        for t, _ in tries:
            p = folder + '/gates_' + t + '.json'
            if os.path.exists(p):
                d = _load(p)
                firsts = [ph.get('first') for ph in d if isinstance(ph, dict) and isinstance(ph.get('first'), int)] \
                    if isinstance(d, list) else []
                if firsts:
                    meta['stable'] = min(firsts) - 1
                    meta['stable_src'] = 'phases'
                    meta['phases_path'] = p
                    break
    if meta['stable'] is None:
        meta['stable'] = DEFAULT_STABLE
        meta['stable_src'] = 'default'
    return meta


def gate_highlights(gates, schedule):
    out = {}
    for tok in (gates or '').split():
        if '=' in tok:
            k, v = tok.split('=', 1)
            if 'bda' in k or k in ('fslean', 'recordthread', 'drawahead'):
                out[k] = v
    sched_names = sorted({tok.split('=', 1)[0] for tok in re.split(r'[|:\s]+', schedule or '') if '=' in tok})
    return ' '.join('%s=%s' % kv for kv in sorted(out.items())), ' '.join(sched_names)


# ----------------------------------------------------------------------------------------------
# one log end-to-end

def analyse_log(path, idx, stable_override=None):
    path = path.replace('\\', '/')
    meta = find_meta(path, idx) if idx is not None else dict(
        tag=os.path.basename(path)[4:-4], json_path=None, sha='', env={}, gates='', stable=DEFAULT_STABLE,
        stable_src='default', attempt_label=None, attempt_outcome=None, hold_s=None, started=None,
        scene=None, schedule=None, phases_path=None)
    if stable_override is not None:
        meta['stable'] = stable_override
        meta['stable_src'] = 'override'
    t0 = time.time()
    status, segments, mk = read_log(path)
    rec = dict(path=path, session=session_of(path), tag=meta['tag'], size=os.path.getsize(path),
               mtime=os.path.getmtime(path), status=status, read_s=round(time.time() - t0, 2))
    rec['meta'] = meta
    rec['markers'] = mk
    rec['segments'] = [len(s) for s in segments]
    if status != 'ok' or not segments:
        if status == 'ok':
            rec['status'] = 'no_rows'
        return rec
    rows = segments[-1]
    res = analyse_rows(rows, meta['stable'], meta['stable_src'])
    analyse_arms(rows, res, meta['stable'], mk['gatearm_first_frame'])
    rec['res'] = res
    return rec


# ----------------------------------------------------------------------------------------------
# scan (with cache)

def cache_path(logpath, cache_dir):
    return os.path.join(cache_dir, 's%d__%s.json' % (session_of(logpath), os.path.basename(logpath)[4:-4]))


def all_logs(pattern=LOG_GLOB):
    fs = [p.replace('\\', '/') for p in glob.glob(pattern)]
    return sorted(fs, key=lambda p: (session_of(p), os.path.basename(p)))


def scan(pattern=LOG_GLOB, jpattern=JSON_GLOB, cache_dir=ROOT + '/cache', budget_s=500.0, only=None,
         lock=LOCK, verbose=True):
    os.makedirs(cache_dir, exist_ok=True)
    idx = json_index(jpattern)
    t_start = time.time()
    seen = {}
    done = 0
    todo = 0
    for p in all_logs(pattern):
        if only and only not in p:
            continue
        cp = cache_path(p, cache_dir)
        st = os.stat(p)
        rec = _load(cp) if os.path.exists(cp) else None
        if rec and rec.get('size') == st.st_size and abs(rec.get('mtime', 0) - st.st_mtime) < 1e-3 and rec.get('key') \
                and rec.get('version') == CACHE_VERSION:
            if rec['status'] != 'duplicate':
                seen.setdefault(rec['key'], p)
            continue
        if lock and os.path.exists(lock):
            print('sealed-run lock present; stopping scan (resume later)', flush=True)
            return False
        if time.time() - t_start > budget_s:
            todo += 1
            continue
        key = content_key(p)
        if key in seen:
            rec = dict(path=p, session=session_of(p), tag=os.path.basename(p)[4:-4], size=st.st_size,
                       mtime=st.st_mtime, status='duplicate', duplicate_of=seen[key], key=key)
        else:
            rec = analyse_log(p, idx)
            rec['key'] = key
            seen[key] = p
        rec['version'] = CACHE_VERSION
        with open(cp + '.tmp', 'w', encoding='utf8') as fh:
            json.dump(rec, fh)
        os.replace(cp + '.tmp', cp)
        done += 1
        if verbose:
            r = rec.get('res') or {}
            print('%-45s %-13s %6.1fs rows=%s regime=%s bda=%s' % (
                p[8:], rec['status'], rec.get('read_s', 0), r.get('rows'), r.get('regime'),
                r.get('bda_steady_median')), flush=True)
    print('scan: processed %d, remaining %d, %.0fs' % (done, todo, time.time() - t_start), flush=True)
    return todo == 0


# ----------------------------------------------------------------------------------------------
# report

def load_records(cache_dir):
    recs = []
    for p in sorted(glob.glob(os.path.join(cache_dir, '*.json'))):
        r = _load(p)
        if isinstance(r, dict):
            recs.append(r)
    recs.sort(key=lambda r: (r.get('session', -1), r.get('tag', '')))
    return recs


def regime_clean(res):
    if res.get('arm_dependent'):
        return 'ARMDEP'
    cls = res.get('steady_w300_list') or []
    o, n = cls.count('OLD'), cls.count('NEW')
    if o and n:
        minority = min(o, n)
        if minority >= 2 or minority / float(o + n) >= 0.25:
            return 'SWITCH'
    return res.get('regime')


def bda_instrumented(env, schedule, gates):
    """True when the run's own settings change how often PrepareBda scans (so bda_scan is not the natural regime)."""
    env = env or {}
    if str(env.get('KYTY_BDA_ALL', '')) not in ('', '0') or str(env.get('KYTY_BDA_EVERY', '')) not in ('', '0') \
            or str(env.get('KYTY_BDA_REGION_STAMPS', '')) == '0':
        return True
    names = {tok.split('=', 1)[0] for tok in re.split(r'[|:\s]+', schedule or '') if '=' in tok}
    if names & {'bdaall', 'bdaevery', 'bdastamp'}:
        return True
    g = dict(tok.split('=', 1) for tok in (gates or '').split() if '=' in tok)
    return g.get('bdaall', '0') not in ('0', '') or g.get('bdaevery', '0') not in ('0', '') or g.get('bdastamp') == '0'


def run_order(recs):
    """Rank of each ok run inside its build, by start time (json) or file mtime; warmup first."""
    by = {}
    for r in recs:
        sha = r['meta'].get('sha') or ''
        if not sha:
            continue
        lab = r['meta'].get('attempt_label') or ''
        k = (r['meta'].get('started') or time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(r['mtime'])),
             0 if lab == 'warmup' else 1, r['mtime'])
        by.setdefault(sha, []).append((k, r['path']))
    order = {}
    for sha, lst in by.items():
        lst.sort()
        for i, (_, p) in enumerate(lst):
            order[p] = i + 1
    return order


def csv_rows(recs):
    ok = [r for r in recs if r.get('status') == 'ok' and r.get('res')]
    order = run_order(ok)
    buflru = sorted({f for r in ok for f in r['res'].get('buflru_fields', [])})
    names = COUNTERS + buflru
    out = []
    for r in ok:
        m, res, mk = r['meta'], r['res'], r['markers']
        env = m.get('env') or {}
        gh, sched_names = gate_highlights(m.get('gates'), m.get('schedule'))
        pin = mk.get('pin') if mk.get('pin') is not None else env.get('KYTY_GPU_CLOCK_PIN', '')
        levels = [l[0] for l in mk.get('levels') or []]
        scene = m.get('scene') or (levels[-1] if levels else ('intro_keys' if env.get('KYTY_KEYS') else ''))
        kk = res.get('k') or {}

        def kget(ph, f):
            return (kk.get(ph) or {}).get(f)
        lk = res.get('link') or {}

        def lget(c, f):
            return (lk.get(c) or {}).get(f)
        row = dict(session=r['session'], tag=r['tag'], folder=os.path.dirname(r['path']), size_mb=round(r['size'] / 1e6, 1),
                   sha=(m.get('sha') or '')[:12], build_order=order.get(r['path'], ''),
                   attempt=m.get('attempt_label') or '', started=m.get('started') or '',
                   scene=scene, levels='/'.join(levels[:4]),
                   schedule='yes' if (m.get('schedule') or mk.get('gatearm_n')) else '',
                   sched_names=sched_names, gatearm_n=mk.get('gatearm_n', 0),
                   precache=env.get('KYTY_PIPELINE_PRECACHE', ''), pin=pin,
                   rec='yes' if env.get('KYTY_REC') else '', frame_trace=env.get('KYTY_FRAME_TRACE', ''),
                   gpu_time=env.get('KYTY_GPU_TIME', ''), pipeline_cache=env.get('KYTY_PIPELINE_CACHE', ''),
                   shader_cache=env.get('KYTY_SHADER_CACHE', ''),
                   env_bda=' '.join('%s=%s' % (k, v) for k, v in sorted(env.items()) if 'BDA' in k),
                   gates_bda=gh, gate_bda_changes=len(mk.get('gate_bda') or []),
                   precache_line=(mk.get('precache') or '')[:90], fatal=(mk.get('fatal') or '')[:80],
                   segments=len(r.get('segments') or []), rows=res['rows'], n_first=res['n_first'], n_last=res['n_last'],
                   stable=res['stable_frame'], stable_src=res['stable_src'], steady_rows=res['steady_rows'],
                   regime=res['regime'],
                   regime_clean='INSTR' if bda_instrumented(env, m.get('schedule'), m.get('gates')) else regime_clean(res),
                   excl=','.join(x for x, on in (('validation', m.get('validation')),
                                                 ('failed-attempt', m.get('attempt_outcome') not in (None, 'ok')),
                                                 ('attempt-ambiguous', m.get('attempt_ambiguous')),
                                                 ('slow', (res['dt_mean_steady'] or 0) > SLOW_DT_US))
                                 if on),
                   bda_steady=res['bda_steady_median'], bda_start=res['bda_start_median'],
                   bda_first600=res['bda_first600_median'], bda_mean_steady=kget('steady', 'mean'),
                   hi_start=kget('start', 'hi'), hi_first600=kget('first600', 'hi'), hi_steady=kget('steady', 'hi'),
                   k0_steady=kget('steady', 'k0'), k1_steady=kget('steady', 'k1'), k2_steady=kget('steady', 'k2'),
                   k3p_steady=kget('steady', 'k3p'), k0_med=res.get('k0_med'), k1_med=res.get('k1_med'),
                   est_n=res['est_n'], settled_n=res['settled_n'], switched=int(bool(res['switched'])),
                   switch_n=res['switch_n'], post_est_changes=res['post_est_changes'],
                   transient_windows=res.get('transient_windows'), persist_switches=res.get('persist_switches'),
                   episodes=res.get('episodes'),
                   w300_steady=res['steady_w300'], w60=res['w60_classes'][:120],
                   arm_dependent=int(bool(res.get('arm_dependent'))),
                   arm_bda=json.dumps(res.get('arm_bda')) if res.get('arm_bda') else '',
                   arm_dt=json.dumps(res.get('arm_dt')) if res.get('arm_dt') else '',
                   dt_mean_steady=res['dt_mean_steady'], drs_ratio=res['drs_ratio_median'],
                   drs_hi_frac=res['drs_hi_frac'],
                   arm0_class=classify((res.get('arm_bda') or {}).get('0')) or '',
                   load_burst=res.get('load_burst'), load_burst_n=res.get('load_burst_n'),
                   first_k0_scene_n=res.get('first_k0_scene_n'),
                   family=family_of(r['tag']), document_s=m.get('document_s'), level_started_s=m.get('level_started_s'),
                   stable_s=m.get('stable_s'),
                   ep_dt_old_minus_new=res.get('ep_dt_old_minus_new'),
                   ep_cpu_old_minus_new=res.get('ep_cpu_old_minus_new'),
                   ep_gpu_old_minus_new=res.get('ep_gpu_old_minus_new'),
                   episode_stats=json.dumps([[s['cls'], s['n0'], s['n1'], s['rows'],
                                              round(s['dt_mean']) if s['dt_mean'] is not None else None]
                                             for s in res.get('episode_stats') or []]))
        for c in LINK_COUNTERS:
            for suf in ('', '_lag1'):
                row['p_hi_%s%s_pos' % (c, suf)] = lget(c + suf, 'p_pos')
                row['p_hi_%s%s_zero' % (c, suf)] = lget(c + suf, 'p_zero')
            row['%s_pos_frac' % c] = lget(c, 'pos_frac')
        for ph in ('steady', 'first600', 'start'):
            med = res['med'][ph]
            for nme in names:
                row['%s_%s' % (ph, nme)] = med.get(nme)
        out.append(row)
    return out, names


def fmt(v, nd=1):
    if v is None or v == '':
        return '-'
    if isinstance(v, float):
        if abs(v) >= 100:
            return '%.0f' % v
        return ('%.' + str(nd) + 'f') % v
    return str(v)


def separation(old, new):
    old = [v for v in old if v is not None]
    new = [v for v in new if v is not None]
    if not old or not new:
        return None
    gt = sum(1 for a in old for b in new if a > b)
    eq = sum(1 for a in old for b in new if a == b)
    auc = (gt + 0.5 * eq) / (len(old) * len(new))
    vals = sorted(set(old + new))
    best = None
    cuts = [vals[0] - 1] + [(a + b) / 2.0 for a, b in zip(vals, vals[1:])] + [vals[-1] + 1]
    so = sorted(old)
    sn = sorted(new)
    import bisect
    for t in cuts:
        o_le = bisect.bisect_right(so, t)
        n_le = bisect.bisect_right(sn, t)
        o_lt = bisect.bisect_left(so, t)
        n_lt = bisect.bisect_left(sn, t)
        e_hi = o_le + (len(sn) - n_le)          # rule OLD if v > t
        e_lo = (len(so) - o_lt) + n_lt          # rule OLD if v < t
        for e, d in ((e_hi, 'OLD>'), (e_lo, 'OLD<')):
            if best is None or e < best[0]:
                best = (e, d, t)
    clean = (min(old) > max(new)) or (max(old) < min(new))
    return dict(n_old=len(old), n_new=len(new), old_min=min(old), old_max=max(old), old_med=statistics.median(old),
                new_min=min(new), new_max=max(new), new_med=statistics.median(new), auc=auc,
                errors=best[0], rule=best[1], cut=best[2], clean=clean,
                err_rate=best[0] / float(len(old) + len(new)))


def group_key(r):
    return (r['sha'], r['scene'])


def family_of(tag):
    return re.sub(r'_(\d+|warmup|a\d+)$', '', tag)


def series_groups(rows):
    """Identical-launch series: same build, same tag family, same scene, >= 3 clean runs, both classes."""
    by = {}
    for r in rows:
        if r['regime_clean'] in ('OLD', 'NEW') and r['sha'] and not r.get('excl'):
            by.setdefault((r['sha'], r['family'], r['scene']), []).append(r)
    out = []
    for (sha, fam, scene), lst in sorted(by.items()):
        o = [r for r in lst if r['regime_clean'] == 'OLD']
        n = [r for r in lst if r['regime_clean'] == 'NEW']
        if len(lst) < 3 or not o or not n:
            continue
        comp = {}
        for key in ('dt_mean_steady', 'steady_dt_us', 'steady_cpu_gpu_us', 'steady_gpu_busy_us', 'steady_buf_new',
                    'steady_up_series', 'hi_steady', 'steady_rows', 'stable_s', 'document_s', 'level_started_s',
                    'build_order'):
            ov = [r[key] for r in o if isinstance(r.get(key), (int, float))]
            nv = [r[key] for r in n if isinstance(r.get(key), (int, float))]
            if ov and nv:
                se = None
                if len(ov) >= 2 and len(nv) >= 2:
                    se = math.sqrt(statistics.variance(ov) / len(ov) + statistics.variance(nv) / len(nv))
                comp[key] = dict(old_mean=sum(ov) / len(ov), new_mean=sum(nv) / len(nv),
                                 diff=sum(ov) / len(ov) - sum(nv) / len(nv), n_old=len(ov), n_new=len(nv),
                                 old_med=statistics.median(ov), new_med=statistics.median(nv), se=se)
        out.append(dict(sha=sha, family=fam, scene=scene, n_old=len(o), n_new=len(n), comp=comp,
                        sessions=sorted({r['session'] for r in lst})))
    return out


def pooled_ivw(groups, key='dt_mean_steady'):
    """Inverse-variance weighted mean of per-series OLD − NEW differences that have a Welch SE."""
    ws = [(g['comp'][key]['diff'], g['comp'][key]['se']) for g in groups
          if g['comp'].get(key) and g['comp'][key].get('se')]
    if not ws:
        return None
    W = sum(1.0 / se ** 2 for _, se in ws)
    return dict(mean=sum(d / se ** 2 for d, se in ws) / W, se=math.sqrt(1.0 / W), series=len(ws))


def within_build(rows, names):
    by = {}
    for r in rows:
        if r['regime_clean'] in ('OLD', 'NEW') and r['sha'] and not r.get('excl'):
            by.setdefault(group_key(r), []).append(r)
    out = []
    keys = ['dt_mean_steady', 'hi_steady'] + ['%s_%s' % (ph, n) for ph in ('steady', 'first600', 'start') for n in names] \
        + ['hi_start', 'hi_first600', 'drs_ratio']
    for (sha, scene), lst in sorted(by.items()):
        o = [r for r in lst if r['regime_clean'] == 'OLD']
        n = [r for r in lst if r['regime_clean'] == 'NEW']
        if not o or not n:
            continue
        comp = {}
        for key in keys:
            ov = [r[key] for r in o if r.get(key) is not None]
            nv = [r[key] for r in n if r.get(key) is not None]
            if ov and nv:
                comp[key] = dict(old_mean=sum(ov) / len(ov), new_mean=sum(nv) / len(nv),
                                 old_med=statistics.median(ov), new_med=statistics.median(nv),
                                 n_old=len(ov), n_new=len(nv),
                                 diff=sum(ov) / len(ov) - sum(nv) / len(nv),
                                 sep=separation(ov, nv))
        out.append(dict(sha=sha, scene=scene, n_old=len(o), n_new=len(n), sessions=sorted({r['session'] for r in lst}),
                        old_tags=[r['tag'] for r in o], new_tags=[r['tag'] for r in n], comp=comp,
                        old_pin=sorted({str(r['pin']) or 'none' for r in o}), new_pin=sorted({str(r['pin']) or 'none' for r in n}),
                        sched=sorted({r['schedule'] or 'no' for r in lst})))
    return out


def pooled_slope(rows, ykey, xkey='hi_steady'):
    """Within-(build, scene) regression of ykey on xkey, pooled; jackknife SE over groups."""
    by = {}
    for r in rows:
        if r['regime_clean'] in ('ARMDEP', 'TOO_FEW', 'INSTR') or r.get('excl') or not r['sha'] \
                or (r['steady_rows'] or 0) < FIRST_STEADY:
            continue
        x, y = r.get(xkey), r.get(ykey)
        if x is None or y is None:
            continue
        by.setdefault(group_key(r), []).append((x, y))
    groups = []
    for k, lst in by.items():
        if len(lst) < 2:
            continue
        mx = sum(a for a, _ in lst) / len(lst)
        my = sum(b for _, b in lst) / len(lst)
        sxx = sum((a - mx) ** 2 for a, _ in lst)
        sxy = sum((a - mx) * (b - my) for a, b in lst)
        if sxx > 1e-9:
            groups.append((sxx, sxy, len(lst)))
    if not groups:
        return None
    SXX = sum(g[0] for g in groups)
    SXY = sum(g[1] for g in groups)
    slope = SXY / SXX
    se = None
    G = len(groups)
    if G >= 3:
        loo = [(SXY - g[1]) / (SXX - g[0]) for g in groups if SXX - g[0] > 1e-9]
        if len(loo) == G:
            m = sum(loo) / G
            se = math.sqrt((G - 1) / float(G) * sum((s - m) ** 2 for s in loo))
    return dict(slope=slope, se=se, groups=G, runs=sum(g[2] for g in groups))


def counts_table(rows, key):
    cats = ['OLD', 'NEW', 'MIXED', 'SWITCH', 'ARMDEP', 'INSTR', 'TOO_FEW']
    by = {}
    for r in rows:
        by.setdefault(r[key], {c: 0 for c in cats})
        by[r[key]][r['regime_clean']] = by[r[key]].get(r['regime_clean'], 0) + 1
    return cats, by


def build_report(recs, out_csv, out_md, out_sep=None):
    rows, names = csv_rows(recs)
    cols = list(rows[0].keys()) if rows else []
    with open(out_csv, 'w', newline='', encoding='utf8') as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: ('' if v is None else v) for k, v in r.items()})
    L = []
    st = {}
    for r in recs:
        st[r.get('status')] = st.get(r.get('status'), 0) + 1
    clean = [r for r in rows if r['regime_clean'] in ('OLD', 'NEW')]
    L.append('# BDA regime census (session 113)')
    L.append('')
    L.append('Generated by `census113.py report` from `cache/` (%d log files seen under C:/kyty/s*/log_*.txt). '
             'Definitions: docstring of `census113.py`, pinned by `test_census113.py` (fixtures pass before any real '
             'log is read). One row per run in `census.csv`; full separation table in `separation.csv`.' % len(recs))
    L.append('')
    L.append('Log status: ' + ', '.join('%s %d' % kv for kv in sorted(st.items())) +
             ' (`no_bda_scan`: builds before s53; `no_draw_lines`: fslean or tiny logs; duplicates = identical content).')
    L.append('Regime: median steady `bda_scan` OLD > %g, NEW < %g, else MIXED. `regime_clean`: ARMDEP (per-arm classes '
             'differ), SWITCH (steady 300-flip windows hold both classes, minority >= 2 windows or >= 25 %%), else the '
             'median regime.' % (OLD_MIN, NEW_MAX))
    L.append('')
    # ---------------------------------------------------------------- quantization
    L.append('## 1. What bda_scan is made of')
    L.append('')
    for sc in sorted({r['scene'] for r in clean}):
        sel = [r for r in clean if r['scene'] == sc]
        k0 = [r['k0_med'] for r in sel if r['k0_med'] is not None]
        k1 = [r['k1_med'] for r in sel if r['k1_med'] is not None]
        L.append('- %s (%d clean runs): median per-run k0 value (flips < 200) %s [runs %s..%s]; median k1 value '
                 '(500..1549) %s [%s..%s].' % (sc or '?', len(sel), fmt(statistics.median(k0)) if k0 else '-',
                                              fmt(min(k0)) if k0 else '-', fmt(max(k0)) if k0 else '-',
                                              fmt(statistics.median(k1)) if k1 else '-', fmt(min(k1)) if k1 else '-',
                                              fmt(max(k1)) if k1 else '-'))
    for cls in ('OLD', 'NEW'):
        sel = [r for r in clean if r['regime_clean'] == cls and r['k0_steady'] is not None]
        if sel:
            L.append('- %s runs (%d): median share of steady flips k0 %.3f, k1 %.3f, k2 %.3f, k3+ %.3f; hi share median %.3f '
                     '[min %.3f, max %.3f].' % (
                         cls, len(sel), statistics.median([r['k0_steady'] for r in sel]),
                         statistics.median([r['k1_steady'] for r in sel]), statistics.median([r['k2_steady'] for r in sel]),
                         statistics.median([r['k3p_steady'] for r in sel]), statistics.median([r['hi_steady'] for r in sel]),
                         min(r['hi_steady'] for r in sel), max(r['hi_steady'] for r in sel)))
    hs = [r['hi_steady'] for r in rows if r['hi_steady'] is not None and r['regime_clean'] not in ('ARMDEP', 'TOO_FEW')]
    if hs:
        bins = [0] * 10
        for v in hs:
            bins[min(9, int(v * 10))] += 1
        L.append('- Histogram of per-run steady hi share (flips with bda_scan >= 500), all non-ARMDEP runs: ' +
                 ', '.join('%.1f-%.1f: %d' % (i / 10.0, (i + 1) / 10.0, b) for i, b in enumerate(bins)) + '.')
    L.append('')
    # ---------------------------------------------------------------- counts
    L.append('## 2. Counts')
    L.append('')
    cats, by = counts_table(rows, 'session')
    L.append('### by session')
    L.append('')
    L.append('| session | ' + ' | '.join(cats) + ' |')
    L.append('|---|' + '---|' * len(cats))
    tot = {c: 0 for c in cats}
    for s in sorted(by):
        L.append('| s%s | ' % s + ' | '.join(str(by[s].get(c, 0)) for c in cats) + ' |')
        for c in cats:
            tot[c] += by[s].get(c, 0)
    L.append('| **all** | ' + ' | '.join(str(tot[c]) for c in cats) + ' |')
    L.append('')
    for r in rows:
        r['_build'] = r['sha'] or '(no json)'
    cats, byb = counts_table(rows, '_build')
    L.append('### by build (sha256 prefix; %d builds)' % len(byb))
    L.append('')
    L.append('| build | sessions | ' + ' | '.join(cats) + ' |')
    L.append('|---|---|' + '---|' * len(cats))
    for b in sorted(byb, key=lambda b: (min(r['session'] for r in rows if r['_build'] == b), b)):
        ss = sorted({r['session'] for r in rows if r['_build'] == b})
        L.append('| %s | %s | ' % (b, ','.join('s%d' % s for s in ss)) + ' | '.join(str(byb[b].get(c, 0)) for c in cats) + ' |')
    L.append('')
    # ---------------------------------------------------------------- within-build
    wb = within_build(rows, names)
    L.append('## 3. Within-build OLD vs NEW (same build AND same scene, clean OLD/NEW runs only)')
    L.append('')
    L.append('Per-run values: `dt_mean` = mean steady dt_us (game speed = 16 667 / dt_mean); other columns are per-run '
             'steady medians; OLD − NEW is the difference of the per-side means. ABBA runs enter with medians over both arms.')
    L.append('')
    L.append('| build | scene | sessions | n OLD/NEW | pin OLD/NEW | dt_mean OLD − NEW | dt med OLD − NEW | cpu_gpu | gpu_busy | '
             'spin_gpu | draws | buf_new OLD/NEW | da_take | hi OLD/NEW |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')

    def cd(b, k):
        c = b['comp'].get(k)
        return fmt(c['diff']) if c else '-'

    def co(b, k, nd=2):
        c = b['comp'].get(k)
        return ('%s/%s' % (fmt(c['old_med'], nd), fmt(c['new_med'], nd))) if c else '-'
    for b in wb:
        L.append('| %s | %s | %s | %d/%d | %s/%s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            b['sha'], b['scene'], ','.join('s%d' % s for s in b['sessions']), b['n_old'], b['n_new'],
            ','.join(b['old_pin']), ','.join(b['new_pin']), cd(b, 'dt_mean_steady'), cd(b, 'steady_dt_us'),
            cd(b, 'steady_cpu_gpu_us'), cd(b, 'steady_gpu_busy_us'), cd(b, 'steady_spin_gpu_us'), cd(b, 'steady_draws'),
            co(b, 'steady_buf_new', 1), cd(b, 'steady_da_take_us'), co(b, 'hi_steady')))
    L.append('')
    if wb:
        L.append('### pooled over those %d build/scene groups (sum %d OLD, %d NEW runs)' % (
            len(wb), sum(b['n_old'] for b in wb), sum(b['n_new'] for b in wb)))
        L.append('')
        L.append('| counter | phase | groups | groups OLD > NEW | median of group diffs (OLD − NEW) | run-weighted mean diff | groups with clean split |')
        L.append('|---|---|---|---|---|---|---|')
        for key in ['dt_mean_steady', 'hi_steady'] + ['steady_%s' % n for n in names] + ['first600_%s' % n for n in names] \
                + ['start_%s' % n for n in names]:
            ds = [(b['comp'][key]['diff'], min(b['comp'][key]['n_old'], b['comp'][key]['n_new']),
                   b['comp'][key]['sep']) for b in wb if b['comp'].get(key)]
            if not ds:
                continue
            gpos = sum(1 for d, _, _ in ds if d > 0)
            wsum = sum(wt for _, wt, _ in ds)
            L.append('| %s | %s | %d | %d | %s | %s | %d |' % (
                key.split('_', 1)[1] if key.split('_', 1)[0] in ('steady', 'first600', 'start') else key,
                key.split('_', 1)[0] if key.split('_', 1)[0] in ('steady', 'first600', 'start') else 'steady',
                len(ds), gpos, fmt(statistics.median([d for d, _, _ in ds])),
                fmt(sum(d * wt for d, wt, _ in ds) / wsum) if wsum else '-',
                sum(1 for _, _, s in ds if s and s['clean'])))
        L.append('')
    L.append('### pooled within-(build, scene) regression on the steady hi share (0 = all flips k0, 1 = all flips k>=1)')
    L.append('')
    L.append('Runs: every run not ARMDEP/INSTR/TOO_FEW and not excluded (validation, failed or ambiguous attempt, slow), '
             'with >= 600 steady rows and a build sha (switching runs included, '
             'which spreads the regressor). Slope = change of the per-run value when hi share goes 0 -> 1; SE = '
             'jackknife over groups.')
    L.append('')
    L.append('| per-run value | slope | SE | groups | runs |')
    L.append('|---|---|---|---|---|')
    for key in ['dt_mean_steady'] + ['steady_%s' % n for n in names]:
        s = pooled_slope(rows, key)
        if s:
            L.append('| %s | %s | %s | %d | %d |' % (key, fmt(s['slope']), fmt(s['se']), s['groups'], s['runs']))
    for sc in ('underwater_aerial_garden',):
        s = pooled_slope([r for r in rows if r['scene'] == sc and r['pin'] in ('1', 1)], 'dt_mean_steady')
        if s:
            L.append('| dt_mean_steady (%s, pinned runs only) | %s | %s | %d | %d |' % (sc, fmt(s['slope']), fmt(s['se']),
                                                                                    s['groups'], s['runs']))
        s = pooled_slope([r for r in rows if r['scene'] == sc and r['pin'] not in ('1', 1)], 'dt_mean_steady')
        if s:
            L.append('| dt_mean_steady (%s, unpinned runs) | %s | %s | %d | %d |' % (sc, fmt(s['slope']), fmt(s['se']),
                                                                                  s['groups'], s['runs']))
    L.append('')
    sg = series_groups(rows)
    L.append('### identical-launch series (same build, same tag family, same scene, >= 3 clean runs, both classes)')
    L.append('')
    L.append('The closest thing to a natural A/B in the archive: repeated launches of one harness with one build.')
    L.append('')
    L.append('| family | build | sessions | n OLD/NEW | dt_mean OLD / NEW | OLD − NEW | Welch SE | cpu_gpu OLD − NEW | '
             'gpu_busy OLD − NEW | up_series OLD/NEW | steady rows | stable_s OLD/NEW | build order OLD/NEW |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|')

    def sc_(g, k, what='diff', nd=1):
        c = g['comp'].get(k)
        if not c:
            return '-'
        if what == 'pair':
            return '%s / %s' % (fmt(c['old_mean'], nd), fmt(c['new_mean'], nd))
        return fmt(c['diff'], nd)
    for g in sg:
        L.append('| %s | %s | %s | %d/%d | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            g['family'], g['sha'], ','.join('s%d' % s for s in g['sessions']), g['n_old'], g['n_new'],
            sc_(g, 'dt_mean_steady', 'pair'), sc_(g, 'dt_mean_steady'),
            fmt((g['comp'].get('dt_mean_steady') or {}).get('se')), sc_(g, 'steady_cpu_gpu_us'),
            sc_(g, 'steady_gpu_busy_us'), sc_(g, 'steady_up_series', 'pair'),
            fmt((g['comp'].get('steady_rows') or {}).get('old_med')), sc_(g, 'stable_s', 'pair'),
            sc_(g, 'build_order', 'pair')))
    if sg:
        ds = [(g['comp']['dt_mean_steady']['diff'], min(g['n_old'], g['n_new'])) for g in sg if g['comp'].get('dt_mean_steady')]
        wsum = sum(w for _, w in ds)
        L.append('')
        L.append('Series: %d; OLD − NEW dt_mean > 0 in %d; median %s µs; weighted (min side n) mean %s µs.' % (
            len(ds), sum(1 for d, _ in ds if d > 0), fmt(statistics.median([d for d, _ in ds])),
            fmt(sum(d * w for d, w in ds) / wsum) if wsum else '-'))
        for key in ('dt_mean_steady', 'steady_cpu_gpu_us', 'steady_gpu_busy_us'):
            iv = pooled_ivw(sg, key)
            if iv:
                L.append('Inverse-variance pooled OLD − NEW %s over %d series with a Welch SE: %s ± %s µs (1 SE).' % (
                    key, iv['series'], fmt(iv['mean']), fmt(iv['se'])))
    L.append('')
    # ---------------------------------------------------------------- separation
    L.append('## 4. Which counters separate OLD from NEW')
    L.append('')
    L.append('Per-run medians of clean OLD vs NEW runs. `err` = share of runs misclassified by the best single cut; '
             '`clean` = disjoint ranges; `AUC` = P(OLD value > NEW value). Shown: the 12 best per phase. '
             '`within-build clean` = build/scene groups (of those holding both classes) where the split is clean.')
    L.append('')
    sep_rows = []
    for scope_name, pred in (('all scenes', lambda r: True),
                             ('Sky Garden only', lambda r: r['scene'] == 'underwater_aerial_garden')):
        sel = [r for r in rows if pred(r) and r['regime_clean'] in ('OLD', 'NEW') and not r.get('excl')]
        L.append('### %s (%d OLD, %d NEW runs)' % (scope_name, sum(1 for r in sel if r['regime_clean'] == 'OLD'),
                                                     sum(1 for r in sel if r['regime_clean'] == 'NEW')))
        L.append('')
        for ph in ('start', 'first600', 'steady'):
            cand = []
            for nme in names + ['hi']:
                key = ('hi_%s' % ph) if nme == 'hi' else '%s_%s' % (ph, nme)
                s = separation([r.get(key) for r in sel if r['regime_clean'] == 'OLD'],
                               [r.get(key) for r in sel if r['regime_clean'] == 'NEW'])
                if not s:
                    continue
                wbc = sum(1 for b in wb if b['comp'].get(key) and b['comp'][key]['sep'] and b['comp'][key]['sep']['clean'])
                wbn = sum(1 for b in wb if b['comp'].get(key) and b['comp'][key]['sep'])
                sep_rows.append((scope_name, nme, ph, s, wbc, wbn))
                cand.append((s['err_rate'], -abs(s['auc'] - 0.5), nme, s, wbc, wbn))
            cand.sort(key=lambda t: (t[0], t[1]))
            L.append('**phase %s**' % ph)
            L.append('')
            L.append('| counter | OLD med [min..max] | NEW med [min..max] | n OLD/NEW | AUC | err | clean | within-build clean |')
            L.append('|---|---|---|---|---|---|---|---|')
            for _, _, nme, s, wbc, wbn in cand[:12]:
                L.append('| %s | %s [%s..%s] | %s [%s..%s] | %d/%d | %.3f | %.3f | %s | %d/%d |' % (
                    nme, fmt(s['old_med'], 2), fmt(s['old_min'], 2), fmt(s['old_max'], 2), fmt(s['new_med'], 2),
                    fmt(s['new_min'], 2), fmt(s['new_max'], 2), s['n_old'], s['n_new'], s['auc'], s['err_rate'],
                    'yes' if s['clean'] else 'no', wbc, wbn))
            L.append('')
    if out_sep:
        with open(out_sep, 'w', newline='', encoding='utf8') as fh:
            w = csv.writer(fh)
            w.writerow(['scope', 'counter', 'phase', 'n_old', 'n_new', 'old_med', 'old_min', 'old_max', 'new_med',
                        'new_min', 'new_max', 'auc', 'errors', 'err_rate', 'rule', 'cut', 'clean',
                        'within_build_clean', 'within_build_groups'])
            for scope_name, nme, ph, s, wbc, wbn in sep_rows:
                w.writerow([scope_name, nme, ph, s['n_old'], s['n_new'], s['old_med'], s['old_min'], s['old_max'],
                            s['new_med'], s['new_min'], s['new_max'], round(s['auc'], 4), s['errors'],
                            round(s['err_rate'], 4), s['rule'], s['cut'], int(s['clean']), wbc, wbn])
    # ---------------------------------------------------------------- per-flip link
    L.append('## 5. Per-flip link between bda_scan >= 500 and object creation (steady flips, per-run values)')
    L.append('')
    L.append('| class | runs | P(hi given buf_new>0) | P(hi given buf_new=0) | same, buf_new of previous flip | share of flips with buf_new>0 | P(hi given img_new>0) | P(hi given img_new=0) |')
    L.append('|---|---|---|---|---|---|---|---|')
    for cls in ('OLD', 'NEW', 'SWITCH'):
        sel = [r for r in rows if r['regime_clean'] == cls]

        def md(k):
            v = [r[k] for r in sel if r.get(k) is not None]
            return ('%.3f' % statistics.median(v)) if v else '-'
        if sel:
            L.append('| %s | %d | %s | %s | %s / %s | %s | %s | %s |' % (
                cls, len(sel), md('p_hi_buf_new_pos'), md('p_hi_buf_new_zero'), md('p_hi_buf_new_lag1_pos'),
                md('p_hi_buf_new_lag1_zero'), md('buf_new_pos_frac'), md('p_hi_img_new_pos'), md('p_hi_img_new_zero')))
    L.append('')
    # ---------------------------------------------------------------- switching
    L.append('## 6. Runs whose regime changed, and arm-dependent runs')
    L.append('')
    tr = [r for r in rows if r['regime_clean'] in ('OLD', 'NEW') and (r['transient_windows'] or 0) > 0]
    per = [r for r in rows if r['regime_clean'] not in ('ARMDEP', 'TOO_FEW') and (r['persist_switches'] or 0) > 0]
    L.append('- SWITCH runs: %d; OLD/NEW runs with a single transient opposite 300-flip window: %d; runs with a persistent '
             '(>= 300 flips each side) change of class: %d.' % (
                 sum(1 for r in rows if r['regime_clean'] == 'SWITCH'), len(tr), len(per)))
    L.append('')
    odd = [r for r in rows if r['regime_clean'] in ('SWITCH', 'ARMDEP', 'MIXED') or r in per]
    L.append('| run | median regime | clean | steady bda median | hi steady | steady 300-windows | persistent episodes (class@n) | arm bda |')
    L.append('|---|---|---|---|---|---|---|---|')
    for r in odd:
        L.append('| s%d/%s | %s | %s | %s | %s | %s | %s | %s |' % (
            r['session'], r['tag'], r['regime'], r['regime_clean'], fmt(r['bda_steady']), fmt(r['hi_steady'], 3),
            r['w300_steady'][:60], r['episodes'] or '-', r['arm_bda'] or '-'))
    L.append('')
    if tr:
        L.append('Transient-window runs (kept in their class): ' + ', '.join(
            's%d/%s (%s)' % (r['session'], r['tag'], r['w300_steady'][:40]) for r in tr) + '.')
        L.append('')
    ep = [r for r in rows if r['regime_clean'] not in ('ARMDEP', 'TOO_FEW') and r.get('ep_dt_old_minus_new') is not None]
    L.append('### within-run comparison: persistent OLD vs NEW episodes of the same process')
    L.append('')
    L.append('Episodes = runs of >= 5 steady 60-flip windows of one class (section definitions). Row-weighted means; '
             'OLD − NEW. Scene position differs between episodes (OLD often starts at n≈940).')
    L.append('')
    L.append('| run | episodes [class, n0, n1, rows, dt_mean] | dt OLD − NEW | cpu_gpu OLD − NEW | gpu_busy OLD − NEW |')
    L.append('|---|---|---|---|---|')
    for r in ep:
        L.append('| s%d/%s | %s | %s | %s | %s |' % (r['session'], r['tag'], r['episode_stats'],
                                                    fmt(r['ep_dt_old_minus_new']), fmt(r['ep_cpu_old_minus_new']),
                                                    fmt(r['ep_gpu_old_minus_new'])))
    if ep:
        L.append('')
        L.append('Within-run dt OLD − NEW: median %s µs over %d runs (%d positive).' % (
            fmt(statistics.median([r['ep_dt_old_minus_new'] for r in ep])), len(ep),
            sum(1 for r in ep if r['ep_dt_old_minus_new'] > 0)))
    L.append('')
    # ---------------------------------------------------------------- establishment
    L.append('## 7. When the regime shows up')
    L.append('')
    for cls in ('OLD', 'NEW'):
        sel = [r for r in rows if r['regime_clean'] == cls]
        est = [r['est_n'] for r in sel if r['est_n'] is not None]
        rel = [r['est_n'] - r['stable'] for r in sel if r['est_n'] is not None and r['stable_src'] == 'json']
        sett = [r['settled_n'] for r in sel if r['settled_n'] is not None]
        relset = [r['settled_n'] - r['stable'] for r in sel if r['settled_n'] is not None and r['stable_src'] == 'json']
        h0 = [r['hi_start'] for r in sel if r['hi_start'] is not None]
        h6 = [r['hi_first600'] for r in sel if r['hi_first600'] is not None]
        if est:
            L.append('- %s (%d runs): est_n median %s [min %s, max %s]; est_n − stable (json runs, n=%d) median %s '
                     '[%s..%s]; settled_n − stable median %s [%s..%s]; hi share: start phase median %.3f, first 600 '
                     'steady flips median %.3f.' % (
                         cls, len(sel), fmt(statistics.median(est)), min(est), max(est), len(rel),
                         fmt(statistics.median(rel)) if rel else '-', min(rel) if rel else '-', max(rel) if rel else '-',
                         fmt(statistics.median(relset)) if relset else '-', min(relset) if relset else '-',
                         max(relset) if relset else '-',
                         statistics.median(h0) if h0 else float('nan'), statistics.median(h6) if h6 else float('nan')))
    L.append('')
    L.append('Load burst = class of the first in-scene 60-flip window (median draws >= %d); first k0 = first in-scene '
             'window of class NEW (json-stable runs, n relative to the stable frame):' % SCENE_DRAWS)
    L.append('')
    for cls in ('OLD', 'NEW', 'SWITCH'):
        sel = [r for r in rows if r['regime_clean'] == cls and r['stable_src'] == 'json']
        if not sel:
            continue
        lb = {}
        for r in sel:
            lb[r['load_burst'] or '-'] = lb.get(r['load_burst'] or '-', 0) + 1
        lbn = [r['load_burst_n'] - r['stable'] for r in sel if r['load_burst_n'] is not None]
        k0 = [r['first_k0_scene_n'] - r['stable'] for r in sel if r['first_k0_scene_n'] is not None]
        L.append('- %s (%d runs): load burst classes %s; load-burst window start − stable median %s; runs with an '
                 'in-scene NEW window %d, its start − stable median %s [%s..%s].' % (
                     cls, len(sel), ', '.join('%s %d' % kv for kv in sorted(lb.items())),
                     fmt(statistics.median(lbn)) if lbn else '-', len(k0),
                     fmt(statistics.median(k0)) if k0 else '-', min(k0) if k0 else '-', max(k0) if k0 else '-'))
    L.append('')
    # ---------------------------------------------------------------- associations
    L.append('## 8. Regime vs run metadata (clean OLD/NEW runs)')
    L.append('')

    def assoc(label, f):
        tab = {}
        for r in rows:
            if r['regime_clean'] not in ('OLD', 'NEW'):
                continue
            k = f(r)
            tab.setdefault(k, [0, 0])
            tab[k][0 if r['regime_clean'] == 'OLD' else 1] += 1
        L.append('**%s**: ' % label + '; '.join('%s → OLD %d / NEW %d' % (k, v[0], v[1]) for k, v in
                                                  sorted(tab.items(), key=lambda kv: str(kv[0]))))
        L.append('')
    assoc('scene', lambda r: r['scene'] or '?')
    assoc('session range', lambda r: 's53-s64' if r['session'] <= 64 else ('s67-s90' if r['session'] <= 90 else
                                                                            ('s91-s102' if r['session'] <= 102 else 's103-s112')))
    assoc('attempt label', lambda r: r['attempt'] or '?')
    assoc('run order within build', lambda r: (str(r['build_order']) if r['build_order'] in (1, 2, 3) else
                                               ('>3' if r['build_order'] else 'no build')))
    assoc('clock pin (log line, else env)', lambda r: r['pin'] or 'none')
    assoc('gate schedule', lambda r: r['schedule'] or 'no')
    assoc('KYTY_PIPELINE_PRECACHE', lambda r: r['precache'] or 'default')
    assoc('KYTY_FRAME_TRACE', lambda r: r['frame_trace'] or '?')
    assoc('KYTY_GPU_TIME', lambda r: r['gpu_time'] or 'unset')
    assoc('KYTY_REC (video recorded)', lambda r: r['rec'] or 'no')
    assoc('stable_src', lambda r: r['stable_src'])
    L.append('### Sky Garden runs only')
    L.append('')
    all_rows = rows
    rows = [r for r in all_rows if r['scene'] == 'underwater_aerial_garden']
    assoc('session range', lambda r: 's53-s64' if r['session'] <= 64 else ('s67-s90' if r['session'] <= 90 else
                                                                            ('s91-s102' if r['session'] <= 102 else 's103-s112')))
    assoc('run order within build', lambda r: (str(r['build_order']) if r['build_order'] in (1, 2, 3) else
                                               ('>3' if r['build_order'] else 'no build')))
    assoc('attempt label', lambda r: r['attempt'] or '?')
    assoc('KYTY_GPU_TIME', lambda r: r['gpu_time'] or 'unset')
    assoc('KYTY_REC (video recorded)', lambda r: r['rec'] or 'no')
    assoc('clock pin', lambda r: r['pin'] or 'none')
    assoc('KYTY_PIPELINE_PRECACHE', lambda r: r['precache'] or 'default')
    assoc('gate schedule', lambda r: r['schedule'] or 'no')
    for cls in ('OLD', 'NEW'):
        sel = [r for r in rows if r['regime_clean'] == cls]
        parts = []
        for k in ('document_s', 'level_started_s', 'stable_s', 'stable'):
            v = [r[k] for r in sel if isinstance(r.get(k), (int, float))]
            parts.append('%s median %s (n=%d)' % (k, fmt(statistics.median(v), 2) if v else '-', len(v)))
        L.append('- %s: ' % cls + '; '.join(parts) + '.')
    L.append('')
    rows = all_rows
    # ---------------------------------------------------------------- caveats
    L.append('## 9. Caveats')
    L.append('')
    for cls in ('OLD', 'NEW'):
        sel = [r for r in clean if r['regime_clean'] == cls and r['drs_ratio'] is not None]
        if sel:
            L.append('- DRS (%s, %d runs with rt_kpx/rt_att): median per-run ratio %s Kpx/attachment (1920x1080 ≈ %d); '
                     'median share of steady flips above %d: %s.' % (
                         cls, len(sel), fmt(statistics.median([r['drs_ratio'] for r in sel])), DRS_BASE, DRS_HI,
                         fmt(statistics.median([r['drs_hi_frac'] for r in sel]), 3)))
    L.append('- ABBA/schedule runs: all medians are per run over all steady rows (both arms), not per arm; runs whose '
             'arms themselves change bda_scan (bindfloor / bdaevery / bdaall arms) are ARMDEP and excluded from comparisons.')
    L.append('- Scenes differ (desert intro_next vs Sky Garden; bases ≈ 23 vs ≈ 52); comparisons are within (build, scene).')
    L.append('- Runs without json use stable frame 2100 (`stable_src=default`) or the first phase of gates_<tag>.json '
             '(`phases`); their steady window may include loading or intro frames.')
    L.append('- Between-run dt comparisons mix gate settings of different experiments within one build; within-build '
             'differences are indications, not an A/B.')
    L.append('- `KYTY_FRAME_TRACE=lite` zeroes some `Scope` timings; `KYTY_GPU_TIME=1` disables the record thread.')
    L.append('- Content duplicates (ports) are counted once; `_warmup`/`_aN` logs are separate processes of the same run.')
    L.append('')
    with open(out_md, 'w', encoding='utf8') as fh:
        fh.write('\n'.join(L) + '\n')
    return rows, wb, sep_rows


# ----------------------------------------------------------------------------------------------

def main(argv):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd')
    a = sub.add_parser('scan')
    a.add_argument('--budget-s', type=float, default=500.0)
    a.add_argument('--only')
    sub.add_parser('report')
    o = sub.add_parser('one')
    o.add_argument('log')
    o.add_argument('--stable', type=int)
    args = ap.parse_args(argv)
    if args.cmd == 'scan':
        return 0 if scan(budget_s=args.budget_s, only=args.only) else 3
    if args.cmd == 'report':
        recs = load_records(ROOT + '/cache')
        build_report(recs, ROOT + '/census.csv', ROOT + '/census_summary.md', ROOT + '/separation.csv')
        print('wrote census.csv and census_summary.md from %d records' % len(recs))
        return 0
    if args.cmd == 'one':
        rec = analyse_log(args.log, json_index(), args.stable)
        print(json.dumps(rec, indent=1, default=str)[:20000])
        return 0
    ap.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

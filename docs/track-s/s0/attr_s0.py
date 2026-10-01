#!/usr/bin/env python3
"""attr_s0.py - track S, link S0 (HPP-294, ROADMAP "SESSION 122" item 229 (zh)(1)-(2)): attribution of the skipped-draw
frames, the held flips and the frames >= 100 ms of the 12 sc142 logs, and the state of the shader-preparation mechanisms
on the installed build 9235a7ac - from the lines the logs have.  No game, no emulator code, MEASUREMENT of old logs only.

Reading (the same as sc142.py, items 221 (v), 218 (g)):
  entry             - the first line "GuestOut: Level has started: <level>" of the target level;
  first scene frame - the first FrameTrace row after the entry line with draws >= 100; its dt is the tail of the load;
  entry window      - the 599 FrameTrace rows after it; hold - every later row (before a scene change).
Per FrameTrace row (one row per flip, held flips included): the counters of the row itself
  FrameTrace-x skc_ap_skip (draws skipped: pipeline_ptr == nullptr), skc_held_inc (flip discarded: incomplete frame),
  FrameTrace-draw img_up_kb / img_imp_kb / img_new / buf_new, FrameTrace cpu_gpu_us / cpu_main_us / semwait_us,
and the event lines between the previous main row and this one ("AsyncPipelines: skipped draw", "AsyncPipelines: flip",
"PipelinePrecache: saved", "PriorityStall:", "MainTaskLate:", "FlipHold:", "CsPretranslate:", "Open:").
Held run = maximal sequence of consecutive rows with skc_held_inc > 0; its visible gap = sum of dt of the run rows +
dt of the next (presented) row: the image of the flip before the run stays on screen for that long.
Output is ASCII.  Logs are read in binary, streaming, line by line - never whole.
    python attr_s0.py            all 12 tags -> out/<tag>.json, out/attr_s0.txt
    python attr_s0.py <tag>...   only these
"""
import hashlib
import json
import os
import re
import sys

S142 = 'C:/kyty/s142'
OUT = 'C:/kyty/s288/s0/out'
SKY = 'underwater_aerial_garden'
LEVELS = (('v142', SKY), ('w142', SKY), ('c142_01', 'bumper_enemy_snowy_canyon'), ('c142_02', 'big_hand_pirate_island'),
          ('c142_03', 'timestop_casino'), ('c142_04', 'mini_giants_garden'), ('c142_05', 'ice_iceberg'),
          ('c142_06', 'sponge_dirty_bath'), ('c142_07', 'hoover_beach'), ('c142_08', 'volcano_mountain'),
          ('c142_09', 'voxel_world'), ('c142_10', 'enemy_gorilla'))
SCENE_DRAWS = 100
ENTRY_WIN = 599
K2_US = 1000000
K3_US = 100000
NL = bytes([10])

RX_MAIN = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
RX_N = re.compile(rb'^FrameTrace-[a-z0-9]+: n=(\d+)')
RX_SKIP = re.compile(rb'frame=(\d+) vs=0x([0-9a-f]+) ps=0x([0-9a-f]+) pending=(\d+) total_skipped=(\d+)')
RX_SAVED = re.compile(rb'PipelinePrecache: saved (\d+) recipes')
RX_US = re.compile(rb' us=(\d+)')
RX_CSREASON = re.compile(rb'family=(\w+) opcode=(0x[0-9a-fA-F]+)')
MAIN_F = ('draws', 'cpu_main_us', 'cpu_gpu_us', 'cpu_present_us', 'semwait_us', 'gpu_busy_us', 'faults', 'fault_us',
          'dispatches', 'downloads', 'submits')
DRAW_F = ('img_new', 'img_up', 'img_up_kb', 'img_imp', 'img_imp_kb', 'buf_new', 'faults_main', 'fault_main_us')
X_F = ('skc_ap_skip', 'skc_held_inc', 'skc_held', 'skc_bad', 'cspfree_src_miss', 'cspfree_spec_miss')
HEADER = (b'ShaderSeed:', b'Shader translation cache:', b'Vulkan pipeline cache:', b'ShaderPreparation:',
          b'PipelinePrecache:', b'AsyncPipelines: mode', b'Pipeline cold-test', b'Cache test mode',
          b'CsPretranslate: summary', b'--- Execute: Main', b'Event: quit')


def field(line, name):
    key = b' ' + name.encode() + b'='
    i = line.find(key)
    if i < 0:
        return None
    j = i + len(key)
    k = j
    n = len(line)
    while k < n and 48 <= line[k] <= 57:
        k += 1
    return int(line[j:k]) if k > j else None


def new_pending():
    return dict(skip_lines=0, pairs=set(), skip_frames=set(), pending_max=0, held_lines=0, saved=[], prio=[], late=[],
                fliphold=[], cs_ready=0, cs_skipped=0, opens=0, cs_pipe=0, starts=[])


def parse(path):
    rows = []
    byn = {}
    header = []
    cs = dict(ready=0, skipped=0, hit=0, miss=0, summary=0, enqueue_skipped=0, reasons={}, ready_us=0)
    tot = dict(lines=0, torn_ft=0, skip_lines=0, held_lines=0, pipetrace_cs_begin=0, asynccompute=0, opens=0,
               avtrace=0, shreg=0, shfirst=0, bytes=0)
    pend = new_pending()
    h = hashlib.sha256()
    lineno = 0
    with open(path, 'rb') as f:
        for line in f:
            lineno += 1
            h.update(line)
            tot['bytes'] += len(line)
            if line.startswith(b'FrameTrace'):
                m = RX_MAIN.match(line)
                if m:
                    r = dict(n=int(m.group(1)), dt=int(m.group(2)), line=lineno)
                    for k in MAIN_F:
                        r[k] = field(line, k)
                    p = pend
                    r.update(ev_skip_lines=p['skip_lines'], ev_pairs=sorted(p['pairs']), ev_frames=sorted(p['skip_frames']),
                             ev_pending_max=p['pending_max'], ev_held_lines=p['held_lines'], ev_saved=p['saved'],
                             ev_prio=p['prio'], ev_late=p['late'], ev_fliphold=p['fliphold'], ev_cs_ready=p['cs_ready'],
                             ev_cs_skipped=p['cs_skipped'], ev_opens=p['opens'], ev_cs_pipe=p['cs_pipe'],
                             ev_starts=p['starts'])
                    pend = new_pending()
                    rows.append(r)
                    byn[r['n']] = r
                    continue
                m = RX_N.match(line)
                if m:
                    r = byn.get(int(m.group(1)))
                    if r is not None:
                        if line.startswith(b'FrameTrace-draw:'):
                            for k in DRAW_F:
                                r[k] = field(line, k)
                        elif line.startswith(b'FrameTrace-x:'):
                            for k in X_F:
                                r[k] = field(line, k)
                continue
            if b'FrameTrace: n=' in line:
                tot['torn_ft'] += 1
            c0 = line[:1]
            if c0 == b'A':
                if line.startswith(b'AsyncPipelines: skipped draw'):
                    tot['skip_lines'] += 1
                    pend['skip_lines'] += 1
                    m = RX_SKIP.search(line)
                    if m:
                        pend['skip_frames'].add(int(m.group(1)))
                        pend['pairs'].add((m.group(2).decode(), m.group(3).decode()))
                        pend['pending_max'] = max(pend['pending_max'], int(m.group(4)))
                    continue
                if line.startswith(b'AsyncPipelines: flip'):
                    tot['held_lines'] += 1
                    pend['held_lines'] += 1
                    continue
                if line.startswith(b'AsyncCompute:'):
                    tot['asynccompute'] += 1
                    continue
                if line.startswith(b'AvTrace:'):
                    tot['avtrace'] += 1
                    continue
            elif c0 == b'C':
                if line.startswith(b'CsPretranslate: '):
                    kind = line[16:32].split(b' ')[0].decode('latin1')
                    if line.startswith(b'CsPretranslate: enqueue skipped'):
                        kind = 'enqueue_skipped'
                    if kind in cs:
                        cs[kind] += 1
                    if kind == 'ready':
                        pend['cs_ready'] += 1
                        u = RX_US.search(line)
                        if u:
                            cs['ready_us'] += int(u.group(1))
                    elif kind in ('skipped', 'enqueue_skipped'):
                        pend['cs_skipped'] += 1
                        m = RX_CSREASON.search(line)
                        key = ('%s %s' % (m.group(1).decode(), m.group(2).decode().lower())) if m else \
                            line[line.find(b'reason='):][:90].decode('latin1').strip()
                        cs['reasons'][key] = cs['reasons'].get(key, 0) + 1
            elif c0 == b'P':
                if line.startswith(b'PipelinePrecache: saved'):
                    m = RX_SAVED.search(line)
                    pend['saved'].append(int(m.group(1)) if m else -1)
                elif line.startswith(b'PriorityStall:'):
                    u = RX_US.search(line)
                    pend['prio'].append(int(u.group(1)) if u else -1)
                elif line.startswith(b'PipelineTrace: vkCreateComputePipelines begin'):
                    tot['pipetrace_cs_begin'] += 1
                    pend['cs_pipe'] += 1
            elif c0 == b'M':
                if line.startswith(b'MainTaskLate:'):
                    u = RX_US.search(line)
                    pend['late'].append(int(u.group(1)) if u else -1)
            elif c0 == b'F':
                if line.startswith(b'FlipHold:'):
                    u = RX_US.search(line)
                    pend['fliphold'].append(int(u.group(1)) if u else -1)
            elif c0 == b'G':
                if line.startswith(b'GuestOut: Level has started:'):
                    pend['starts'].append(line[len(b'GuestOut: Level has started:'):].strip().decode('latin1'))
            elif c0 == b'S':
                if line.startswith(b'ShaderRegister:'):
                    tot['shreg'] += 1
                elif line.startswith(b'ShaderFirstUse:'):
                    tot['shfirst'] += 1
            elif c0 == b'\t':
                if line.startswith(b'\tOpen: '):
                    tot['opens'] += 1
                    pend['opens'] += 1
            for hk in HEADER:
                if hk in line[:40] and line.startswith(hk):
                    header.append((lineno, line.rstrip().decode('latin1')[:400]))
                    break
    tot['lines'] = lineno
    return dict(rows=rows, header=header, cs=cs, tot=tot, sha256=h.hexdigest(), tail=pend)


def g(r, k):
    v = r.get(k)
    return v if v is not None else 0


def classify(r):
    """The S0 rule for a frame >= 100 ms (executor's variant, co-occurrence, NOT a cause):
    PIPE   - the row itself has skipped draws or is a held flip (new VS/PS pair compiling on a worker, by code);
    NEAR   - no skip in the row, but a skipped/held row within +-2 rows;
    NONE   - no skipped draw and no held flip within +-2 rows.
    The split translation / synchronous pipeline creation / resource upload inside cpu_gpu_us needs AvTrace."""
    if g(r, 'skc_ap_skip') > 0 or g(r, 'skc_held_inc') > 0 or r['ev_skip_lines'] > 0:
        return 'PIPE'
    return None


def derive(tag, level, p):
    rows = p['rows']
    out = dict(tag=tag, level=level, sha256=p['sha256'], rows_total=len(rows), entered=False)
    ei = None
    for i, r in enumerate(rows):
        if level in r['ev_starts']:
            ei = i
            break
    if ei is None and level in p['tail']['starts']:
        return out
    if ei is None:
        return out
    out['entered'] = True
    # rows[ei] is the first main row printed AFTER the entry line
    change = None
    for i in range(ei + 1, len(rows)):
        if rows[i]['ev_starts']:
            change = i
            break
    after = rows[ei:change] if change is not None else rows[ei:]
    fi = None
    for i, r in enumerate(after):
        if g(r, 'draws') >= SCENE_DRAWS:
            fi = i
            break
    out['entry_row_n'] = rows[ei]['n']
    out['scene_change'] = change is not None
    before = rows[:ei]
    load = after[:fi + 1] if fi is not None else after
    out['pre_entry'] = summary_part(before)
    out['load'] = summary_part(load)
    if fi is None:
        return out
    first = after[fi]
    out['first'] = dict(n=first['n'], dt=first['dt'], draws=first['draws'], skip=g(first, 'skc_ap_skip'),
                        held=g(first, 'skc_held_inc'))
    post = after[fi + 1:]
    win, hold = post[:ENTRY_WIN], post[ENTRY_WIN:]
    out['window'] = summary_part(win)
    out['hold'] = summary_part(hold)
    out['post'] = summary_part(post)
    out['dt_after_first_us'] = sum(r['dt'] for r in post)
    # held runs over post
    runs = []
    i = 0
    while i < len(post):
        if g(post[i], 'skc_held_inc') > 0:
            j = i
            while j < len(post) and g(post[j], 'skc_held_inc') > 0:
                j += 1
            gap = sum(r['dt'] for r in post[i:j]) + (post[j]['dt'] if j < len(post) else 0)
            runs.append(dict(n0=post[i]['n'], n1=post[j - 1]['n'], flips=j - i, gap_us=gap,
                             part='window' if i < ENTRY_WIN else 'hold', closed=j < len(post),
                             max_dt=max(r['dt'] for r in post[i:j]),
                             pairs=len(set(tuple(x) for r in post[i:j] for x in r['ev_pairs'])),
                             pending_max=max(r['ev_pending_max'] for r in post[i:j])))
            i = j
        else:
            i += 1
    out['held_runs'] = runs
    out['held_runs_n'] = len(runs)
    out['held_gap_max_us'] = max((x['gap_us'] for x in runs), default=0)
    out['held_gap_ge100'] = sum(1 for x in runs if x['gap_us'] >= K3_US)
    out['held_gap_ge1s'] = sum(1 for x in runs if x['gap_us'] >= K2_US)
    out['held_gap_sum_us'] = sum(x['gap_us'] for x in runs)
    # the form ban: a presented row with skipped draws (skip > 0, not held) and whether the next two rows are held
    shown = []
    for i, r in enumerate(post):
        if g(r, 'skc_ap_skip') > 0 and g(r, 'skc_held_inc') == 0:
            nxt = [g(x, 'skc_held_inc') for x in post[i + 1:i + 3]]
            shown.append(dict(n=r['n'], skip=g(r, 'skc_ap_skip'), next_held=nxt))
    out['skip_not_held'] = shown
    heldnoskip = [r['n'] for r in post if g(r, 'skc_held_inc') > 0 and g(r, 'skc_ap_skip') == 0]
    out['held_without_skip'] = heldnoskip
    # frames >= 100 ms: the table
    long_rows = []
    for i, r in enumerate(post):
        if r['dt'] >= K3_US:
            cls = classify(r)
            if cls is None:
                near = post[max(0, i - 2):i + 3]
                cls = 'NEAR' if any(g(x, 'skc_ap_skip') > 0 or g(x, 'skc_held_inc') > 0 for x in near) else 'NONE'
            run_first = g(r, 'skc_held_inc') > 0 and (i == 0 or g(post[i - 1], 'skc_held_inc') == 0)
            long_rows.append(dict(n=r['n'], dt=r['dt'], part='window' if i < ENTRY_WIN else 'hold', cls=cls,
                                  skip=g(r, 'skc_ap_skip'), held=g(r, 'skc_held_inc'), pairs=len(r['ev_pairs']),
                                  run_first=run_first, draws=g(r, 'draws'), cpu_gpu=g(r, 'cpu_gpu_us'),
                                  cpu_main=g(r, 'cpu_main_us'), semwait=g(r, 'semwait_us'),
                                  img_up_kb=g(r, 'img_up_kb'), img_imp_kb=g(r, 'img_imp_kb'), img_new=g(r, 'img_new'),
                                  buf_new=g(r, 'buf_new'), opens=r['ev_opens'], cs_ready=r['ev_cs_ready'],
                                  cs_src_miss=g(r, 'cspfree_src_miss'), prio=r['ev_prio'], late=r['ev_late'],
                                  saved=r['ev_saved'], line=r['line']))
    out['long'] = long_rows
    # pairs: span of every skipped pair (first..last row that logged it) in rows and in presented time
    span = {}
    for i, r in enumerate(post):
        for pr in r['ev_pairs']:
            key = '%s/%s' % tuple(pr)
            if key not in span:
                span[key] = [i, i]
            span[key][1] = i
    spans = []
    for key, (a, b) in span.items():
        spans.append(dict(pair=key, n0=post[a]['n'], n1=post[b]['n'], rows=b - a + 1,
                          us=sum(r['dt'] for r in post[a:b + 1])))
    spans.sort(key=lambda s: -s['us'])
    out['pair_spans'] = spans
    out['pairs_n'] = len(spans)
    us = sorted(s['us'] for s in spans)
    out['pair_span_us'] = dict(min=us[0], med=us[len(us) // 2], p95=us[min(len(us) - 1, int(len(us) * 0.95))],
                               max=us[-1]) if us else None
    # recipes saved along the run
    saved = [(r['n'], s) for r in rows for s in r['ev_saved']] + [(None, s) for s in p['tail']['saved']]
    out['recipes_saved'] = saved
    return out


def summary_part(rs):
    return dict(rows=len(rs), dt_us=sum(r['dt'] for r in rs),
                skip_rows=sum(1 for r in rs if g(r, 'skc_ap_skip') > 0),
                skip_rows_pos=sum(1 for r in rs if r['ev_skip_lines'] > 0),
                skip_draws=sum(g(r, 'skc_ap_skip') for r in rs), skip_lines=sum(r['ev_skip_lines'] for r in rs),
                skip_frame_ids=len(set(x for r in rs for x in r['ev_frames'])),
                held_rows=sum(1 for r in rs if g(r, 'skc_held_inc') > 0), held_lines=sum(r['ev_held_lines'] for r in rs),
                skc_bad=sum(g(r, 'skc_bad') for r in rs),
                pairs=len(set(tuple(x) for r in rs for x in r['ev_pairs'])),
                k3=sum(1 for r in rs if K3_US <= r['dt'] < K2_US), k2=sum(1 for r in rs if r['dt'] >= K2_US),
                dt_max=max((r['dt'] for r in rs), default=0), cs_ready=sum(r['ev_cs_ready'] for r in rs),
                cs_skipped=sum(r['ev_cs_skipped'] for r in rs), cs_pipe=sum(r['ev_cs_pipe'] for r in rs),
                opens=sum(r['ev_opens'] for r in rs), img_up_kb=sum(g(r, 'img_up_kb') for r in rs),
                x_missing=sum(1 for r in rs if r.get('skc_ap_skip') is None))


def check_score(tag, d):
    """Cross-check against the sealed scorer output runs142/<tag>.score.json (first n, K3 window / hold, skip frames)."""
    path = '%s/runs142/%s.score.json' % (S142, tag)
    if not os.path.isfile(path):
        return ['no score json']
    s = json.load(open(path))
    dv = s.get('derive', {})
    bad = []
    if s.get('log_sha') != d['sha256']:
        bad.append('sha')
    if not d.get('first') or dv.get('first', [None])[0] != d['first']['n']:
        bad.append('first n %s vs %s' % (dv.get('first'), d.get('first')))
    else:
        if len(dv.get('k3w', [])) != d['window']['k3']:
            bad.append('k3w %d vs %d' % (len(dv.get('k3w', [])), d['window']['k3']))
        if len(dv.get('k3h', [])) != d['hold']['k3']:
            bad.append('k3h %d vs %d' % (len(dv.get('k3h', [])), d['hold']['k3']))
        if len(dv.get('k2', [])) != d['post']['k2']:
            bad.append('k2')
        if dv.get('dt_after_first_us') != d['dt_after_first_us']:
            bad.append('dt_after_first %s vs %s' % (dv.get('dt_after_first_us'), d['dt_after_first_us']))
    if s.get('rows_total') != d['rows_total']:
        bad.append('rows_total %s vs %s' % (s.get('rows_total'), d['rows_total']))
    if s.get('skip', {}).get('lines') != d['tot']['skip_lines']:
        bad.append('skip lines %s vs %s' % (s.get('skip', {}).get('lines'), d['tot']['skip_lines']))
    d['score_skip_frames'] = s.get('skip', {}).get('frames')
    return bad


def main():
    tags = sys.argv[1:] or [t for t, _ in LEVELS]
    os.makedirs(OUT, exist_ok=True)
    lv = dict(LEVELS)
    ok = True
    for tag in tags:
        path = '%s/log_%s.txt' % (S142, tag)
        p = parse(path)
        d = derive(tag, lv[tag], p)
        d['path'] = path
        d['header'] = p['header']
        d['cs'] = p['cs']
        d['tot'] = p['tot']
        d['tail_skip_lines'] = p['tail']['skip_lines']
        d['check'] = check_score(tag, d)
        ok &= not d['check']
        with open('%s/%s.json' % (OUT, tag), 'w', encoding='ascii') as f:
            json.dump(d, f, indent=1, sort_keys=True)
        print('%s %s sha %s rows %d first %s check %s' % (tag, lv[tag], d['sha256'][:16], d['rows_total'],
                                                           d.get('first'), d['check'] or 'OK'))
        sys.stdout.flush()
    print('CROSS-CHECK vs sc142 score json: %s' % ('ALL OK' if ok else 'DIVERGENCE'))


if __name__ == '__main__':
    main()

"""F13a (HPP-479, ROADMAP s122 item 391 (z)): the reader of one tag of B41 (ending_boss_after_credit, installed 540c035a).
usage: python f13a_read.py <f13_rd|f13_k> [--json <out.json>]
       python f13a_read.py --dir <fixture dir> --kind <rd|k>   (fixtures: log.txt [, rec.idx, glitch.txt, sheet.txt, manifest_cmp.txt,
                                                               installed_sha.txt])
Rows only, no verdict and no "defect / not a defect" (item 391 (z): the reading is F13b's).  Definitions (seal docs/track-f/f13a.md
section 4):
  entry        the first line 'GuestOut: Level has started: ending_boss_after_credit'; the FrameTrace rows after it are numbered k = 1, 2, ...
               (the level frame of the reader; the RenderDoc counter GetFrameNum is another counter - its own lines are printed beside).
  card end     the first row k after entry with draws < 100 that comes after (not necessarily directly) a run of >= 90 consecutive
               rows with draws >= 300 after entry
               (the card "THE END" of v146_08 has draws 1018, the black part 22).  NOT_FOUND when there is none.  Its time is the sum of
               dt_us of rows 1..k-1 (seconds from entry).
  t(card)      seconds after card end of a log line = sum of dt_us of the FrameTrace rows from the card end row to the last row before the
               line (negative: the line comes before the card end).
  draws        histogram of draws of the rows after the card end (top 6), and per window (card end .. first press, press i .. press i+1,
               last press .. end) for f13_k.
  scene lines  every 'Level has started:' and 'LevelDocument Loaded:' line after entry with k and t(card).
  rd           (f13_rd) lines 'RenderDoc: level started at frame', 'RenderDoc: auto capture at frame', 'captured guest flip', 'capture
               finished'; t(card) of the 'auto capture' line; draws of the 3 rows after it.  Row rd_after_card_10s: YES if t(card) >= 10.0,
               NO if < 10.0, NOT_DETERMINED if no capture line or no card end.
  keys         (f13_k) lines 'InputScript: press <key> at <s> s (present <p>)': per press - key, s, present, k, t(card), the draws median
               of the 600 rows before and after, scene lines between it and the next press (or the end).  Rows: presses_J >= 3 and
               presses_L >= 3; keys_after_card_10s - every press has t(card) >= 10.0; keys_pause_10s - consecutive presses of one key
               differ by >= 10.0 s of the InputScript time.
  hold         seconds from the card end to the last FrameTrace row; row hold_after_card_120s: YES if >= 120.0.
  death        lines with 'Unhandled exception:', '--- Fatal Error ---', '--- Error ---', 'GpuHangAbort:', 'ErrorDeviceLost'; frames >= 1 s
               - rows after entry with dt_us >= 1 000 000 (k and t(card) of each); 'AsyncPipelines: skipped draw' lines; window events
               'Window <id> minimized|restored|resized|size changed|lost keyboard focus' and 'Recovering Vulkan swapchain'.
  video        (f13_k) records of rec.idx; for each press the video frame with the first index present >= the press present; glitches
               (glitch.txt 'one-frame glitches: N'); sheet (sheet.txt 'sheet: ').
  binary/cache installed_sha.txt = 540c035a...; manifest_cmp.txt first line.
ASCII output only."""
import collections, hashlib, json, os, re, statistics, sys

G = 'C:/kyty/f287/f13a'
LEVEL = b'ending_boss_after_credit'
WANT = '540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1'
M_START = b'GuestOut: Level has started: '
M_DOC = b'LevelDocument Loaded: '
RX_FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)[^\n]*? draws=(\d+)')
RX_PRESS = re.compile(rb'InputScript: press (\S+) at ([0-9.]+) s \(present (\d+)\)')
RX_RD = re.compile(rb'RenderDoc: (level started at frame|auto capture at frame|captured guest flip|capture finished|capture started|capture requested)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
CARD_MIN = 300
CARD_RUN = 90
BLACK_MAX = 100
K2_US = 1000000
AFTER_S = 10.0
PAUSE_S = 10.0
HOLD_S = 120.0
WIN_ROWS = 600


def a(b):
    return b.decode('ascii', 'replace').rstrip('\r\n')


def read_log(path):
    """One streaming pass: FrameTrace rows after entry and the event lines with the index of the last row before them."""
    rows = []          # (k, n, dt_us, draws)
    events = []        # (kind, last row index (count of rows so far), text)
    entered = False
    entry_line = None
    deaths, skipped, wins, recov = [], 0, collections.Counter(), 0
    with open(path, 'rb') as f:
        for line in f:
            if not entered:
                if line.startswith(M_START) and line[len(M_START):].strip() == LEVEL:
                    entered = True
                    entry_line = a(line)
                    events.append(('scene', 0, a(line)))
                    continue
                if RX_RD.search(line):
                    events.append(('rd', 0, a(line)))
            else:
                m = RX_FT.match(line)
                if m:
                    rows.append((len(rows) + 1, int(m.group(1)), int(m.group(2)), int(m.group(3))))
                    continue
                if line.startswith(M_START) or line.startswith(M_DOC):
                    events.append(('scene', len(rows), a(line)))
                elif RX_RD.search(line):
                    events.append(('rd', len(rows), a(line)))
                elif b'InputScript: press' in line:
                    events.append(('press', len(rows), a(line)))
            if any(t in line for t in DEATH):
                deaths.append(a(line)[:160])
            if b'AsyncPipelines: skipped draw' in line:
                skipped += 1
            w = RX_WIN.search(line)
            if w:
                wins[w.group(1).decode()] += 1
            if b'Recovering Vulkan swapchain' in line:
                recov += 1
    return dict(rows=rows, events=events, entry_line=entry_line, deaths=deaths, skipped=skipped, wins=dict(wins), recov=recov)


def card_end(rows):
    run = 0
    seen = False
    for k, n, dt, dr in rows:
        if dr >= CARD_MIN:
            run += 1
            if run >= CARD_RUN:
                seen = True
        else:
            if seen and dr < BLACK_MAX:
                return k
            run = 0
    return None


def tcard(rows, ce, last_index):
    """Seconds after the card end row of a line that follows row last_index (1-based count of rows before the line)."""
    if ce is None:
        return None
    if last_index >= ce:
        return sum(r[2] for r in rows[ce - 1:last_index]) / 1e6
    return -sum(r[2] for r in rows[last_index:ce - 1]) / 1e6


def med(vals):
    return statistics.median(vals) if vals else None


def read_idx(path):
    out = []
    if not path or not os.path.isfile(path):
        return out
    with open(path, 'rb') as f:
        for line in f:
            p = line.split()
            if len(p) >= 3:
                out.append((int(p[0]), int(p[1]), float(p[2])))
    return out


def analyse(kind, logp, idxp=None, glitchp=None, sheetp=None, cmpp=None, shap=None):
    L = read_log(logp)
    rows, ev = L['rows'], L['events']
    res = collections.OrderedDict()
    res['kind'] = kind
    res['log_sha256'] = hashlib.sha256(open(logp, 'rb').read()).hexdigest()
    res['entry'] = 'YES' if L['entry_line'] else 'NO'
    res['rows_after_entry'] = len(rows)
    ce = card_end(rows)
    res['card_end_k'] = ce if ce is not None else 'NOT_FOUND'
    res['card_end_s_from_entry'] = round(sum(r[2] for r in rows[:ce - 1]) / 1e6, 3) if ce else None
    if ce:
        res['card_draws_median'] = med([r[3] for r in rows[max(0, ce - 1 - CARD_RUN):ce - 1]])
        hist = collections.Counter(r[3] for r in rows[ce - 1:])
        res['draws_after_card_top'] = hist.most_common(6)
        res['rows_after_card'] = len(rows) - ce + 1
        hold = sum(r[2] for r in rows[ce - 1:]) / 1e6
        res['hold_after_card_s'] = round(hold, 3)
        res['hold_after_card_120s'] = 'YES' if hold >= HOLD_S else 'NO'
    else:
        res['hold_after_card_120s'] = 'NOT_DETERMINED'
    res['scene_lines'] = [dict(k=i, t_card=(round(tcard(rows, ce, i), 3) if ce else None), line=t[:120])
                          for (kd, i, t) in ev if kd == 'scene']
    res['scene_lines_after_card'] = sum(1 for (kd, i, t) in ev if kd == 'scene' and ce and i >= ce)
    k2 = [dict(k=r[0], dt_us=r[2], t_card=(round(tcard(rows, ce, r[0] - 1), 3) if ce else None)) for r in rows if r[2] >= K2_US]
    res['frames_ge_1s'] = k2
    res['death_lines'] = len(L['deaths'])
    res['death_first'] = L['deaths'][:3]
    res['skipped_draw_lines'] = L['skipped']
    res['window_events'] = L['wins']
    res['recovering_swapchain'] = L['recov']
    if kind == 'rd':
        rd = [(i, t) for (kd, i, t) in ev if kd == 'rd']
        res['rd_lines'] = [t[:120] for i, t in rd]
        cap = [(i, t) for i, t in rd if 'auto capture at frame' in t]
        if cap and ce:
            i = cap[0][0]
            tc = tcard(rows, ce, i)
            res['rd_capture_k'] = i
            res['rd_capture_t_card'] = round(tc, 3)
            res['rd_capture_draws_next3'] = [r[3] for r in rows[i:i + 3]]
            res['rd_after_card_10s'] = 'YES' if tc >= AFTER_S else 'NO'
        else:
            res['rd_after_card_10s'] = 'NOT_DETERMINED'
        res['rd_finished'] = 'YES' if any('capture finished' in t for i, t in rd) else 'NO'
    if kind == 'k':
        idx = read_idx(idxp)
        presses = []
        for (kd, i, t) in ev:
            if kd != 'press':
                continue
            m = RX_PRESS.search(t.encode())
            if not m:
                continue
            presses.append(dict(key=m.group(1).decode(), s=float(m.group(2)), present=int(m.group(3)), k=i))
        bounds = [p['k'] for p in presses] + [len(rows)]
        for j, p in enumerate(presses):
            p['t_card'] = round(tcard(rows, ce, p['k']), 3) if ce else None
            p['draws_med_before'] = med([r[3] for r in rows[max(0, p['k'] - WIN_ROWS):p['k']]])
            p['draws_med_after'] = med([r[3] for r in rows[p['k']:p['k'] + WIN_ROWS]])
            p['draws_set_until_next'] = sorted(set(r[3] for r in rows[p['k']:bounds[j + 1]]))[:12]
            p['scene_lines_until_next'] = [t[:100] for (kd, i, t) in ev if kd == 'scene' and p['k'] <= i < bounds[j + 1]]
            vf = [x[0] for x in idx if x[1] >= p['present']]
            p['video_frame'] = vf[0] if vf else None
        res['presses'] = presses
        nJ = sum(1 for p in presses if p['key'].upper() == 'J')
        nL = sum(1 for p in presses if p['key'].upper() == 'L')
        res['presses_J'] = nJ
        res['presses_L'] = nL
        res['presses_J_ge3_L_ge3'] = 'YES' if nJ >= 3 and nL >= 3 else 'NO'
        if ce and presses:
            res['keys_after_card_10s'] = 'YES' if all(p['t_card'] >= AFTER_S for p in presses) else 'NO'
        else:
            res['keys_after_card_10s'] = 'NOT_DETERMINED'
        ok = True
        for key in ('J', 'L'):
            ss = [p['s'] for p in presses if p['key'].upper() == key]
            ok &= all(b - x >= PAUSE_S for x, b in zip(ss, ss[1:]))
        res['keys_pause_10s'] = 'YES' if presses and ok else ('NOT_DETERMINED' if not presses else 'NO')
        if ce:
            first = presses[0]['k'] if presses else len(rows)
            res['draws_card_to_first_press_top'] = collections.Counter(r[3] for r in rows[ce - 1:first]).most_common(4)
            res['draws_after_last_press_top'] = (collections.Counter(r[3] for r in rows[presses[-1]['k']:]).most_common(4)
                                                 if presses else None)
        res['video_records'] = len(idx)
        if glitchp and os.path.isfile(glitchp):
            m = RX_GL.search(open(glitchp, encoding='ascii', errors='replace').read())
            res['video_glitches'] = int(m.group(1)) if m else 'NO_LINE'
        else:
            res['video_glitches'] = 'NO_FILE'
        res['video_sheet'] = ('YES' if sheetp and os.path.isfile(sheetp)
                              and 'sheet: ' in open(sheetp, encoding='ascii', errors='replace').read() else 'NO')
    if shap and os.path.isfile(shap):
        s = open(shap).read().strip()
        res['installed_sha'] = 'YES' if s == WANT else 'NO (%s)' % s[:16]
    if cmpp and os.path.isfile(cmpp):
        res['manifest_cmp'] = (open(cmpp, encoding='ascii', errors='replace').readline().strip())[:120]
    return res


def show(res):
    for k, v in res.items():
        if k in ('presses', 'scene_lines', 'frames_ge_1s'):
            print('%s: %d' % (k, len(v)))
            for x in v:
                print('  ' + json.dumps(x, ensure_ascii=True))
        else:
            print('%s: %s' % (k, json.dumps(v, ensure_ascii=True)))
    print('ROWS %s' % ' '.join('%s=%s' % (k, res[k]) for k in res if k.endswith(('_10s', '_120s', '_ge3', 'entry', 'card_end_k'))
                                 or k in ('death_lines', 'skipped_draw_lines', 'video_glitches', 'video_records')))


def main(argv):
    out = None
    if '--json' in argv:
        out = argv[argv.index('--json') + 1]
    if '--dir' in argv:
        d = argv[argv.index('--dir') + 1]
        kind = argv[argv.index('--kind') + 1]
        logp = argv[argv.index('--log') + 1] if '--log' in argv else os.path.join(d, 'log.txt')
        res = analyse(kind, logp, os.path.join(d, 'rec.idx'), os.path.join(d, 'glitch.txt'),
                      os.path.join(d, 'sheet.txt'), os.path.join(d, 'manifest_cmp.txt'), os.path.join(d, 'installed_sha.txt'))
    else:
        tag = argv[1]
        kind = {'f13_rd': 'rd', 'f13_k': 'k'}.get(tag)
        if kind is None:
            print('unknown tag %s' % tag)
            return 2
        D = '%s/runs/%s' % (G, tag)
        res = analyse(kind, '%s/log_%s.txt' % (G, tag), '%s/rec_%s.mp4.idx' % (G, tag), D + '/glitch.txt', D + '/sheet.txt',
                      D + '/manifest_cmp.txt', D + '/installed_sha.txt')
    show(res)
    if out:
        with open(out, 'w', encoding='ascii') as f:
            json.dump(res, f, ensure_ascii=True, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

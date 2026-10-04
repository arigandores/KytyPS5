# F18a (HPP-535, ROADMAP s122 item 433(e)): block sweep of the game logs for F8 - the line
# 'AudioOut: SDL_QueueAudio failed: Invalid audio device ID' (src/libs/audio.cpp:641) - and for every other line of the
# host sound paths ('AudioOut:', 'AudioIn:', 'Haptics:').  Form of docs/track-f/f17a/sweep_f17a.py: files are read in
# 64 MiB blocks, only whole lines are processed, the unfinished tail is carried to the next block; '.xz' goes through
# 'xz -dc'.  Per log one JSON line in <out.jsonl>:
#   qfail               lines with 'SDL_QueueAudio failed' (any error text)
#   qfail_inv           of them with 'Invalid audio device ID'
#   qtexts{text:n}      distinct error texts after 'SDL_QueueAudio failed: ' (at most 8)
#   qfirst / qlast      [line, ts_ms, ft_n, ft_us] of the first / last such line: 1-based line number, the last log
#                       timestamp '[tid][HH:MM:SS.mmm]' at or before the line (ms of process time, None if none yet),
#                       the number of 'FrameTrace: n=' lines before it and the sum of their dt_us
#   ev[]                the other sound lines and the scene/window lines, in log order, at most EV_CAP:
#                       [line, ts_ms, ft_n, ft_us, text[:220]]   (ev_over - lines beyond the cap)
#   snd{text:n}         distinct texts of the sound lines, digit runs replaced by '#', at most 64 (snd_over)
#   ctx[]               the CTX_N lines before the first qfail line, text[:240] (only when qfail > 0)
#   after[]             the first 12 lines after the first qfail line that are not qfail lines
#   ts_first / ts_last  first / last log timestamp, ms;  ft_n / ft_us - 'FrameTrace: n=' lines and the sum of dt_us
#   lvl                 distinct 'Level has started: <name>' names, at most 16
#   sha256 (of the stored file), sha256_text ('.xz' only: of the unpacked text), size, lines, xz
# Identities checked by selfcheck_f18a.py: qfail == sum(qtexts) + qtexts_over; qfail_inv <= qfail;
# qfirst.line <= qlast.line; ev lines strictly increase.
# Resumable: paths already in <out.jsonl> are skipped; stops between files after <budget_s> seconds of wall time and
# when C:/kyty/SEALED_RUN.lock or C:/kyty/f287/STOP exists.  Prints 'SWEEP COMPLETE' when no file is left.
# Usage: python sweep_f18a.py <list.tsv> <out.jsonl> <budget_s>      (list.tsv: path <TAB> size, swept in file order)
import bisect, hashlib, json, os, re, subprocess, sys, time

lst, out, budget = sys.argv[1], sys.argv[2], float(sys.argv[3])
LOCK = os.environ.get('F18A_LOCK', 'C:/kyty/SEALED_RUN.lock')
STOP = os.environ.get('F18A_STOP', 'C:/kyty/f287/STOP')
t0 = time.time()
files = []
for l in open(lst, encoding='utf-8'):
    l = l.rstrip('\n')
    if l:
        p, s = l.split('\t')[:2]
        files.append((p, int(s)))
done = set()
if os.path.exists(out):
    for l in open(out, encoding='utf-8'):
        if l.startswith('{'):
            done.add(json.loads(l)['path'])
left = [(p, s) for p, s in files if p not in done]
print('files', len(files), 'done before', len(done), 'left', len(left), 'left GiB %.2f' % (sum(s for _, s in left) / 2.0 ** 30))

NL = b'\n'
BLOCK = 64 << 20
QF = b'SDL_QueueAudio failed'
QINV = b'SDL_QueueAudio failed: Invalid audio device ID'
QTEXT = re.compile(rb'SDL_QueueAudio failed: ([^\r\n]*)')
# sound lines other than the qfail line; scene and window lines - found by literal search (fast), one entry per line
EVLIT = (b'AudioOut: ', b'AudioIn: ', b'Haptics: ', b'Level has started: ', NL + b'Window ', NL + b'Event: ',
         b'Recovering Vulkan swapchain')
SND = (b'AudioOut: ', b'AudioIn: ', b'Haptics: ')
TS = re.compile(rb'\[\d+\]\[(\d\d):(\d\d):(\d\d)\.(\d{3})\]')
FT = re.compile(rb'FrameTrace: n=\d+ dt_us=(\d+)')
FTLIT = b'FrameTrace: n='
LVL = b'Level has started: '
DIG = re.compile(rb'\d+')
EV_CAP = 400
SND_CAP = 64
CTX_N = 60
TS_TRIES = 200000


def dec(b):
    return b.decode('utf-8', 'replace')


def ts_ms(m):
    return ((int(m.group(1)) * 60 + int(m.group(2))) * 60 + int(m.group(3))) * 1000 + int(m.group(4))


def ts_before(buf, pos, fallback):
    # last timestamp header of a line that starts before pos
    # (None when TS_TRIES lines starting with '[' in a row carry no timestamp - e.g. a run of '[Vulkan][W]' lines)
    k = pos
    for _ in range(TS_TRIES):
        k = buf.rfind(b'\n[', 0, k)
        if k == -1:
            m = TS.match(buf, 0)
            if m and pos > 0:
                return ts_ms(m)
            return fallback
        m = TS.match(buf, k + 1)
        if m:
            return ts_ms(m)
    return None


def sweep(path, size):
    rec = {'path': path, 'size': size, 'xz': path.endswith('.xz'), 'qfail': 0, 'qfail_inv': 0, 'qtexts': {}, 'qtexts_over': 0,
           'qfirst': None, 'qlast': None, 'ev': [], 'ev_over': 0, 'snd': {}, 'snd_over': 0, 'ctx': [], 'after': [],
           'ts_first': None, 'ts_last': None, 'ft_n': 0, 'ft_us': 0, 'lvl': [], 'lines': 0}
    h = hashlib.sha256()
    h2 = hashlib.sha256()   # '.xz' only: sha256 of the unpacked text (sha256_text)
    proc = None
    if rec['xz']:
        with open(path, 'rb') as fh:
            while True:
                b = fh.read(BLOCK)
                if not b:
                    break
                h.update(b)
        proc = subprocess.Popen(['xz', '-dc', path], stdout=subprocess.PIPE)
        f = proc.stdout
    else:
        f = open(path, 'rb')
    carry = b''
    tail = []            # last CTX_N lines of the previous blocks (for ctx across a block border)
    last_ts = None
    need_after = 0
    while True:
        b = f.read(BLOCK)
        if not b and not carry:
            break
        if proc is None:
            h.update(b)
        else:
            h2.update(b)
        buf = carry + b
        if b:
            cut = buf.rfind(NL)
            if cut == -1:
                carry = buf
                continue
            carry = buf[cut + 1:]
            buf = buf[:cut + 1]
        else:
            carry = b''
            if not buf.endswith(NL):
                buf += NL
        base_line = rec['lines']
        # FrameTrace positions and running sums of this block
        ft_pos, ft_cum = [], []
        s = rec['ft_us']
        i = buf.find(FTLIT)
        while i != -1:
            if i == 0 or buf[i - 1:i] == NL:
                m = FT.match(buf, i)
                if m:
                    s += int(m.group(1))
                    ft_pos.append(i)
                    ft_cum.append(s)
            i = buf.find(FTLIT, i + 1)

        def at(pos):
            i = bisect.bisect_right(ft_pos, pos)
            return [base_line + buf.count(NL, 0, pos) + 1, ts_before(buf, pos, last_ts), rec['ft_n'] + i,
                    ft_cum[i - 1] if i else rec['ft_us']]

        if rec['ts_first'] is None:
            m = TS.search(buf)
            if m:
                rec['ts_first'] = ts_ms(m)
        nq = buf.count(QF)
        if need_after:   # the first qfail line was in an earlier block
            j = 0
            while need_after and j < len(buf):
                e = buf.find(NL, j)
                ln = buf[j:e]
                if QF not in ln:
                    rec['after'].append(dec(ln.rstrip(b'\r'))[:240])
                    need_after -= 1
                j = e + 1
        if nq:
            rec['qfail_inv'] += buf.count(QINV)
            for m in QTEXT.finditer(buf):
                t = dec(m.group(1))[:120]
                if t in rec['qtexts'] or len(rec['qtexts']) < 8:
                    rec['qtexts'][t] = rec['qtexts'].get(t, 0) + 1
                else:
                    rec['qtexts_over'] += 1
            i = buf.find(QF)
            if rec['qfail'] == 0:
                rec['qfirst'] = at(i)
                ls = buf.rfind(NL, 0, i) + 1
                before = buf[max(0, ls - 65536):ls].split(NL)[:-1]
                lines = [dec(x.rstrip(b'\r'))[:240] for x in before]
                if ls - 65536 > 0:
                    lines = lines[1:]
                rec['ctx'] = (tail + lines)[-CTX_N:]
                need_after = 12
                j = buf.find(NL, i) + 1
                while need_after and j < len(buf):
                    e = buf.find(NL, j)
                    ln = buf[j:e]
                    if QF not in ln:
                        rec['after'].append(dec(ln.rstrip(b'\r'))[:240])
                        need_after -= 1
                    j = e + 1
            rec['qlast'] = at(buf.rfind(QF))
            rec['qfail'] += nq
        starts = set()
        for lit in EVLIT:
            off = 1 if lit[:1] == NL else 0
            i = buf.find(lit)
            while i != -1:
                ls = buf.rfind(NL, 0, i + off) + 1
                le = buf.find(NL, i + off)
                if QF not in buf[ls:le]:
                    starts.add(ls)
                i = buf.find(lit, le)
        for w in (b'Window ', b'Event: '):
            if buf.startswith(w):
                starts.add(0)
        for ls in sorted(starts):
            line = buf[ls:buf.find(NL, ls)].strip()
            if any(x in line for x in SND):
                t = dec(DIG.sub(b'#', line))[:200]
                if t in rec['snd'] or len(rec['snd']) < SND_CAP:
                    rec['snd'][t] = rec['snd'].get(t, 0) + 1
                else:
                    rec['snd_over'] += 1
            if LVL in line:
                t = dec(line[line.find(LVL) + len(LVL):]).strip()[:60]
                if t not in rec['lvl'] and len(rec['lvl']) < 16:
                    rec['lvl'].append(t)
            if len(rec['ev']) < EV_CAP:
                rec['ev'].append(at(ls) + [dec(line)[:220]])
            else:
                rec['ev_over'] += 1
        # last timestamp of the block
        k = len(buf)
        for _ in range(TS_TRIES):
            k = buf.rfind(b'\n[', 0, k)
            if k == -1:
                break
            m = TS.match(buf, k + 1)
            if m:
                last_ts = ts_ms(m)
                break
        rec['lines'] += buf.count(NL)
        rec['ft_n'] += len(ft_pos)
        if ft_cum:
            rec['ft_us'] = ft_cum[-1]
        if rec['qfail'] == 0:
            tl = buf[max(0, len(buf) - 65536):].split(NL)[:-1]
            tail = [dec(x.rstrip(b'\r'))[:240] for x in tl][-CTX_N:]
        if not b:
            break
    rec['ts_last'] = last_ts
    if proc is None:
        f.close()
    else:
        proc.wait()
        rec['xz_rc'] = proc.returncode
        rec['sha256_text'] = h2.hexdigest()
    rec['sha256'] = h.hexdigest()
    return rec


n = 0
for p, s in left:
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('STOPPED: lock or STOP present')
        sys.exit(3)
    if time.time() - t0 > budget:
        break
    if not os.path.exists(p):
        rec = {'path': p, 'size': s, 'missing': True}
    else:
        rec = sweep(p, s)
    with open(out, 'ab') as fo:
        fo.write((json.dumps(rec, ensure_ascii=True, sort_keys=True) + '\n').encode('ascii'))
    n += 1
print('swept now', n, 'wall %.1f s' % (time.time() - t0))
if n == len(left):
    print('SWEEP COMPLETE')

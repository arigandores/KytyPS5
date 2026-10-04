# F19a (HPP-543, ROADMAP s122 item 441(z)(2)): block sweep of the game logs for B24 - the controller lines, the
# main-thread lines and the frames with dt_us >= 1 s.  Form of docs/track-f/f18a/sweep_f18a.py: files are read in
# 64 MiB blocks, only whole lines are processed, the unfinished tail is carried to the next block; '.xz' goes through
# 'xz -dc'.  Per log one JSON line in <out.jsonl>; every position is [line, ts_ms, ft_n, ft_us]: 1-based line number,
# the last log timestamp '[tid][HH:MM:SS.mmm]' at or before the line (ms of process time, None if none yet), the
# number of 'FrameTrace: n=' lines before it and the sum of their dt_us.
#   ctl[]    position + text[:200] of the controller lines (line starts 'Controller ', 'Controller: ',
#            'ControllerMotion: ' and any line with 'Haptics: pad audio device'), at most CAP (ctl_over);
#            the device path after 'path=' is replaced by its class: <bt> (Bluetooth HID service GUID 00001124),
#            <usb> ('vid_'), <xinput>, <none> (empty), <other>
#   mt[]     position + text[:160] of the main-thread lines ('MainTaskLate: ', 'MainThreadWait: ', 'MainStallTest: ',
#            'PrepareHold: ', 'TestMinimize: '), at most CAP (mt_over);  mt_late_max - the largest 'MainTaskLate: us='
#   win[]    position + text[:120] of 'Window ' / 'Event: ' line starts and 'Recovering Vulkan swapchain', at most CAP
#   lvl[]    position + name of 'Level has started: <name>' (empty names kept), at most 64
#   slow[]   frames with dt_us >= 1 000 000: position of the 'FrameTrace: n=' line + [n, dt_us] (ft_n / ft_us of the
#            position are the counts BEFORE this frame), at most CAP (slow_over)
#   ts_first / ts_last, ft_n / ft_us, lines, sha256 (stored file), sha256_text ('.xz': unpacked text), size, xz
# Identities checked by selfcheck_f19a.py: positions of every list strictly increase by line; slow dt_us >= 1e6;
# sum(slow dt_us) <= ft_us; len(slow) + slow_over == slow_n.
# Resumable: paths already in <out.jsonl> are skipped; stops between files after <budget_s> seconds of wall time and
# when C:/kyty/SEALED_RUN.lock or C:/kyty/f287/STOP exists.  Prints 'SWEEP COMPLETE' when no file is left.
# Usage: python sweep_f19a.py <list.tsv> <out.jsonl> <budget_s>      (list.tsv: path <TAB> size, swept in file order)
import bisect, hashlib, json, os, re, subprocess, sys, time

lst, out, budget = sys.argv[1], sys.argv[2], float(sys.argv[3])
LOCK = os.environ.get('F19A_LOCK', 'C:/kyty/SEALED_RUN.lock')
STOP = os.environ.get('F19A_STOP', 'C:/kyty/f287/STOP')
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
TS = re.compile(rb'\[\d+\]\[(\d\d):(\d\d):(\d\d)\.(\d{3})\]')
FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
FTLIT = b'FrameTrace: n='
LVL = b'Level has started:'
MTL = re.compile(rb'MainTaskLate: us=(\d+)')
# (literal, must be at line start, list name)
LITS = ((b'Controller ', True, 'ctl'), (b'Controller: ', True, 'ctl'), (b'ControllerMotion: ', True, 'ctl'),
        (b'Haptics: pad audio device', False, 'ctl'),
        (b'MainTaskLate: ', True, 'mt'), (b'MainThreadWait: ', True, 'mt'), (b'MainStallTest: ', True, 'mt'),
        (b'PrepareHold: ', True, 'mt'), (b'TestMinimize: ', True, 'mt'),
        (b'Window ', True, 'win'), (b'Event: ', True, 'win'), (b'Recovering Vulkan swapchain', False, 'win'),
        (LVL, False, 'lvl'))
CAP = 200
TS_TRIES = 200000
TXT = {'ctl': 200, 'mt': 160, 'win': 120, 'lvl': 80}


def dec(b):
    return b.decode('utf-8', 'replace')


def ts_ms(m):
    return ((int(m.group(1)) * 60 + int(m.group(2))) * 60 + int(m.group(3))) * 1000 + int(m.group(4))


def ts_before(buf, pos, fallback):
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


def mask_path(line):
    i = line.find(b'path=')
    if i == -1:
        return line
    p = line[i + 5:].strip().lower()
    if not p:
        c = b'<none>'
    elif b'00001124-0000-1000-8000-00805f9b34fb' in p:
        c = b'<bt>'
    elif b'xinput' in p:
        c = b'<xinput>'
    elif b'vid_' in p:
        c = b'<usb>'
    else:
        c = b'<other>'
    return line[:i + 5] + c


def sweep(path, size):
    rec = {'path': path, 'size': size, 'xz': path.endswith('.xz'), 'ctl': [], 'ctl_over': 0, 'mt': [], 'mt_over': 0,
           'mt_late_max': 0, 'win': [], 'win_over': 0, 'lvl': [], 'lvl_over': 0, 'slow': [], 'slow_over': 0, 'slow_n': 0,
           'ts_first': None, 'ts_last': None, 'ft_n': 0, 'ft_us': 0, 'lines': 0}
    h = hashlib.sha256()
    h2 = hashlib.sha256()
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
    last_ts = None
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
        ft_pos, ft_cum, slow = [], [], []
        s = rec['ft_us']
        i = buf.find(FTLIT)
        while i != -1:
            if i == 0 or buf[i - 1:i] == NL:
                m = FT.match(buf, i)
                if m:
                    d = int(m.group(2))
                    if d >= 1000000:
                        slow.append((i, int(m.group(1)), d))
                    s += d
                    ft_pos.append(i)
                    ft_cum.append(s)
            i = buf.find(FTLIT, i + 1)

        def at(pos):
            # counts BEFORE the line that starts at pos
            k = bisect.bisect_left(ft_pos, pos)
            return [base_line + buf.count(NL, 0, pos) + 1, ts_before(buf, pos + 1, last_ts), rec['ft_n'] + k,
                    ft_cum[k - 1] if k else rec['ft_us']]

        if rec['ts_first'] is None:
            m = TS.search(buf)
            if m:
                rec['ts_first'] = ts_ms(m)
        for pos, n, d in slow:
            rec['slow_n'] += 1
            if len(rec['slow']) < CAP:
                # the timestamp of a frame line: the first header AFTER it is closer to the end of the frame than the
                # last one before it; both are kept - [.., ts_before, .., .., n, dt_us, ts_after]
                m = TS.search(buf, pos, min(len(buf), pos + (1 << 20)))
                rec['slow'].append(at(pos) + [n, d, ts_ms(m) if m else None])
            else:
                rec['slow_over'] += 1
        starts = {}
        for lit, at_start, name in LITS:
            i = buf.find(lit)
            while i != -1:
                ls = buf.rfind(NL, 0, i) + 1
                le = buf.find(NL, i)
                if (not at_start) or ls == i:
                    starts.setdefault(ls, name)
                i = buf.find(lit, le)
        for ls in sorted(starts):
            name = starts[ls]
            line = buf[ls:buf.find(NL, ls)].strip()
            if name == 'ctl':
                line = mask_path(line)
            if name == 'lvl':
                line = line[line.find(LVL) + len(LVL):].strip()
            if name == 'mt':
                m = MTL.match(line)
                if m:
                    rec['mt_late_max'] = max(rec['mt_late_max'], int(m.group(1)))
            cap = 64 if name == 'lvl' else CAP
            if len(rec[name]) < cap:
                rec[name].append(at(ls) + [dec(line)[:TXT[name]]])
            else:
                rec[name + '_over'] += 1
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

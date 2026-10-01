# F0 (HPP-289, ROADMAP p.228(b)(3)): streaming sweep of logs by signature. Read-only on logs, binary mode, chunked.
# Usage: python sweep_f0.py <budget_seconds> [workers]
# Resumable: every finished segment is a pickle in C:/kyty/f287/f0/seg/; rerun until it prints "SWEEP COMPLETE".
# Stops on C:/kyty/f287/STOP (exit 4); sleeps while C:/kyty/SEALED_RUN.lock exists (sealed runs have priority).
import os, re, sys, time, pickle, hashlib, collections, multiprocessing

OUT = 'C:/kyty/f287/f0'
SEG = OUT + '/seg'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
SEG_BYTES = 256 << 20
BLOCK = 8 << 20
NL = bytes([10])
FIX = re.compile(r'/(fx_|work_|mut|test_|fixt)')

KEY = re.compile(
    rb'FrameTrace|Level has started: |GuestArgs:|Event: quit|'
    rb'GpuHangAbort|ErrorDeviceLost|Unhandled exception|--- Fatal Error ---|--- Error ---|Error: condition|EXIT_IF|'
    rb'hold_exit|game ENDED|\[Vulkan\]\[[EW]\]|not implemented|Stubbed function|BvhLoopCapTrip:|PriorityStall:|'
    rb'AsyncPipelines: skipped draw|MainTaskLate:|'
    rb'[Aa]ssert|[Uu]nsupported|[Ww]arning|WARNING|[Ee]rror|ERROR|[Ff]ailed|FAILED|[Ff]atal|[Uu]nknown|not found|'
    rb'[Ii]nvalid|skipped|skipping|[Ee]xception|[Aa]ccess violation|[Aa]bort|ignoring|mismatch|overflow|not supported|'
    rb'too many|[Uu]nresolved|[Tt]imeout|corrupt|device lost|DEVICE_LOST|[Cc]rash|[Dd]eadlock|[Ss]tall|cannot|Cannot|'
    rb'unable|Unable|[Uu]nexpected|[Uu]nhandled|illegal|[Dd]enied|[Mm]issing|out of memory|exceed|truncat')
SKIP_PREFIX = (b'Read ', b'Open:', b'Close:', b'KernelFstat', b'KernelStat', b'path = ', b'CsPretranslate phase',
               b'ShaderRecompiler', b'CsPretranslate structured', b'CsPretranslate predication', b'CsPretranslate: ready',
               b'loop header=')
RE_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
RE_DRAWS = re.compile(rb' draws=(\d+)')
RE_US = re.compile(rb' us=(\d+)')
RE_SITE = re.compile(rb' site=(\S+)')
RE_UNSUB = re.compile(rb' unsub=(\d+)')
RE_OP = re.compile(rb'family=(\w+) opcode=(0x[0-9a-fA-F]+)')
RE_REASON = re.compile(rb'reason=([^\r]*?)$')
RE_FRAME = re.compile(rb' frame=(\d+)')
RE_TRIPS = re.compile(rb'trips=\+(\d+)')
RE_HEX = re.compile(rb'0x[0-9a-fA-F]+|\b[0-9a-fA-F]{8,}\b')
RE_NUM = re.compile(rb'\d+')
RE_PATH = re.compile(rb'(?:[A-Za-z]:[/\\]\S*?(?:games[/\\]PPSA|_SaveData|_ShaderCache)|/app0/|/download0/|/savedata)[^\r]*')
RE_LIB = re.compile(rb'\[([A-Za-z0-9]+)_v\d+\]')
RE_HDR = re.compile(rb'^\[\d+\]\[\d\d:\d\d:\d\d\.\d+\] ')
MAXSIG = 4000


def norm(line):
    s = line.strip()
    s = RE_HDR.sub(b'', s)
    if s.startswith(b'Relocate: unresolved'):
        m = RE_LIB.search(s)
        return b'Relocate: unresolved PLT import patched to stub lib=' + (m.group(1) if m else b'?')
    if b'Stubbed function' in s:
        return RE_HEX.sub(b'X', s)[:200]
    m = RE_OP.search(s)
    if m and b'not implemented' in s:
        return b'OPCODE_NI family=' + m.group(1) + b' opcode=' + m.group(2)
    s = RE_PATH.sub(b'<PATH>', s)
    s = RE_HEX.sub(b'X', s)
    s = RE_NUM.sub(b'X', s)
    return s[:200]


def wait_gate():
    if os.path.exists(STOP):
        os._exit(4)
    while os.path.exists(LOCK):
        time.sleep(5)
        if os.path.exists(STOP):
            os._exit(4)


def scan_segment(task):
    path, si, start, end, size, whole = task
    out = '%s/%s_%d.pkl' % (SEG, hashlib.md5(path.encode('utf-8')).hexdigest(), si)
    sigs = {}          # sig -> [count, first_line(relative to segment), example]
    events = []        # ('L', relline, name) | ('F', relline, n, dt, draws) | ('Q', relline)
    args = []
    met = {'prio_n': 0, 'prio_max': 0, 'prio_gt50': 0, 'prio_sites': collections.Counter(), 'late_n': 0, 'late_max': 0,
           'late_ge1s': 0, 'skip_n': 0, 'skip_frames': set(), 'trip_n': 0, 'trip_max': 0, 'over': 0}
    h = hashlib.sha256() if whole else None
    nl_total = 0
    with open(path, 'rb') as fh:
        pos = start
        carry = b''
        done = False
        if start > 0:
            # lines owned by a segment: those whose first byte lies in [start, end)
            fh.seek(start - 1)
            found = False
            while not found:
                b0 = fh.read(1 << 16)
                if not b0:
                    break
                k = b0.find(NL)
                if k >= 0:
                    fh.seek(fh.tell() - len(b0) + k + 1)
                    found = True
            pos = fh.tell()
            if not found or pos >= end:
                done = True
        while not done:
            wait_gate()
            blk = fh.read(BLOCK)
            if h is not None:
                h.update(blk)
            if not blk:
                buf = carry
                carry = b''
                done = True
                if not buf:
                    break
                if not buf.endswith(NL):
                    buf += NL
            else:
                buf = carry + blk
                k = buf.rfind(NL)
                if k < 0:
                    carry = buf
                    continue
                carry = buf[k + 1:]
                buf = buf[:k + 1]
            # buf = whole lines; its first byte is at file offset bufpos
            bufpos = pos - 0
            # lines owned by this segment: those starting before `end`
            limit = len(buf)
            if bufpos + len(buf) > end:
                # cut at the first line start >= end
                rel = end - bufpos
                if rel <= 0:
                    limit = 0
                else:
                    k = buf.find(NL, rel - 1)
                    limit = k + 1 if k >= 0 else len(buf)
                done = True
            pos += len(buf)
            if limit < len(buf):
                buf = buf[:limit]
            last = 0
            p = 0
            L = len(buf)
            while True:
                m = KEY.search(buf, p)
                if m is None:
                    break
                ls = buf.rfind(NL, 0, m.start()) + 1
                le = buf.find(NL, m.start())
                if le < 0:
                    le = L
                nl_total += buf.count(NL, last, ls)
                last = ls
                lineno = nl_total + 1
                p = le + 1
                line = buf[ls:le]
                t = line.lstrip()
                if t.startswith(b'FrameTrace'):
                    if t.startswith(b'FrameTrace: n='):
                        f = RE_FT.match(t)
                        if f:
                            d = RE_DRAWS.search(t)
                            events.append(('F', lineno, int(f.group(1)), int(f.group(2)), int(d.group(1)) if d else -1))
                    continue
                if t.startswith(SKIP_PREFIX):
                    continue
                if t.startswith(b'entry_block=') and b'failure=None' in t:
                    continue
                if b'Level has started: ' in t:
                    events.append(('L', lineno, t.split(b'Level has started: ', 1)[1].strip().decode('latin1')[:80]))
                    continue
                if b'GuestArgs:' in t:
                    if len(args) < 40:
                        args.append(t.decode('latin1')[:160])
                    continue
                if t.startswith(b'Event: quit'):
                    events.append(('Q', lineno))
                if t.startswith(b'PriorityStall:'):
                    u = RE_US.search(t)
                    us = int(u.group(1)) if u else 0
                    met['prio_n'] += 1
                    met['prio_max'] = max(met['prio_max'], us)
                    if us > 50000:
                        met['prio_gt50'] += 1
                    s = RE_SITE.search(t)
                    ub = RE_UNSUB.search(t)
                    met['prio_sites'][(s.group(1).decode('latin1') if s else '?') + ' unsub=' + (ub.group(1).decode('latin1') if ub else '?')] += 1
                    events.append(('P', lineno, us))
                elif t.startswith(b'MainTaskLate:'):
                    u = RE_US.search(t)
                    us = int(u.group(1)) if u else 0
                    met['late_n'] += 1
                    met['late_max'] = max(met['late_max'], us)
                    if us >= 1000000:
                        met['late_ge1s'] += 1
                elif t.startswith(b'AsyncPipelines: skipped draw'):
                    met['skip_n'] += 1
                    fr = RE_FRAME.search(t)
                    if fr and len(met['skip_frames']) < 100000:
                        met['skip_frames'].add(int(fr.group(1)))
                elif t.startswith(b'BvhLoopCapTrip:'):
                    met['trip_n'] += 1
                    tr = RE_TRIPS.search(t)
                    if tr:
                        met['trip_max'] = max(met['trip_max'], int(tr.group(1)))
                sig = norm(t)
                e = sigs.get(sig)
                if e is None:
                    if len(sigs) >= MAXSIG:
                        met['over'] += 1
                        continue
                    sigs[sig] = [1, lineno, t[:400]]
                else:
                    e[0] += 1
            nl_total += buf.count(NL, last, L)
    met['skip_frames'] = len(met['skip_frames'])
    met['prio_sites'] = dict(met['prio_sites'])
    res = {'path': path, 'si': si, 'size': size, 'lines': nl_total, 'sigs': sigs, 'events': events, 'args': args,
           'met': met, 'sha256': h.hexdigest() if h is not None else None}
    tmp = out + '.tmp'
    with open(tmp, 'wb') as o:
        pickle.dump(res, o, protocol=4)
    os.replace(tmp, out)
    return (path, si, size if whole else min(end, size) - start)


def hash_file(task):
    path = task[0]
    out = '%s/%s_sha.pkl' % (SEG, hashlib.md5(path.encode('utf-8')).hexdigest())
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        while True:
            wait_gate()
            b = fh.read(BLOCK)
            if not b:
                break
            h.update(b)
    tmp = out + '.tmp'
    with open(tmp, 'wb') as o:
        pickle.dump({'path': path, 'sha256': h.hexdigest()}, o, protocol=4)
    os.replace(tmp, out)
    return (path, -1, 0)


def work(task):
    if task[1] == -1:
        return hash_file(task)
    return scan_segment(task)


def tasks_all():
    ts = []
    for l in open(OUT + '/loglist_f0.tsv', encoding='utf-8'):
        p, s, m = l.rstrip().split(chr(9))
        s = int(s)
        if FIX.search(p) or s == 0:
            continue
        md = hashlib.md5(p.encode('utf-8')).hexdigest()
        if s <= SEG_BYTES:
            ts.append((p, 0, 0, s, s, True, md))
        else:
            ts.append((p, -1, 0, 0, s, False, md))
            n = (s + SEG_BYTES - 1) // SEG_BYTES
            for i in range(n):
                ts.append((p, i, i * SEG_BYTES, min(s, (i + 1) * SEG_BYTES), s, False, md))
    return ts


if __name__ == '__main__':
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 480
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    os.makedirs(SEG, exist_ok=True)
    if os.path.exists(STOP):
        print('STOP present')
        sys.exit(4)
    ts = tasks_all()
    todo = []
    for t in ts:
        out = '%s/%s_%s.pkl' % (SEG, t[6], 'sha' if t[1] == -1 else str(t[1]))
        if not os.path.exists(out):
            todo.append(t[:6])
    print('tasks total', len(ts), 'todo', len(todo), 'todo GB %.1f' % (sum((t[4] if t[5] else (t[3] - t[2])) for t in todo if t[1] != -1) / 1e9))
    if not todo:
        print('SWEEP COMPLETE')
        sys.exit(0)
    t0 = time.time()
    done = 0
    nbytes = 0
    pool = multiprocessing.Pool(workers)
    it = pool.imap_unordered(work, todo, chunksize=1)
    try:
        while True:
            left = budget - (time.time() - t0)
            if left <= 0:
                break
            try:
                r = it.next(timeout=left)
            except multiprocessing.TimeoutError:
                break
            except StopIteration:
                break
            done += 1
            nbytes += r[2]
    finally:
        pool.terminate()
        pool.join()
    print('done this run', done, 'of', len(todo), 'GB %.1f' % (nbytes / 1e9), 'wall %.0f s' % (time.time() - t0),
          'lock_now', os.path.exists(LOCK))
    if done == len(todo):
        print('SWEEP COMPLETE')

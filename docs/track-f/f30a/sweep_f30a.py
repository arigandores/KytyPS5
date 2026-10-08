# F30a (HPP-706, ROADMAP s122 item 640(d)(1)(ii)-(iii)): sweep of the game logs of list_f30a.tsv for the rtskip
# self-check inventory and the BDA mode of every scene entry.  Form of sweep_f28a.py (one regex pass over an mmap of a
# plain log; lock and STOP before every log; resume).  xz logs (sessions <= 139) are streamed through 'xz -dc | grep -aF'
# with the same fixed strings; they have no header times (hold_s None, frames from the FrameTrace-draw lines).
# Kinds:
#   RTS  'RtSkip: '          - 'mode <v> ctx_slots=..' (first armed draw of a value) / 'refused reason=<r>' (renderDraw.cpp)
#   RTV  'RtSkipVerify: '    - 'MISMATCH frame=.. bits=0x... reg=.. chain=.. colors=.. depth=.. pa=1 pb=.. mode=..'
#   LVL  'Level has started: ', TC 'Shader translation cache: ', VER 'KytyPS5-20' (version string)
#   GATE 'Gate: rtskip=' (a gate file or schedule changed the knob), GARM 'GateArm: ' (schedule blocks)
#   BDA  ' bda_scan=<n> '    - FrameTrace-draw, one per frame: the BDA mode bands of item 40(e)(1) (block mean <= 300 NEW,
#                              >= 600 OLD, between - mixed)
#   RTSX ' rts_n=..'         - FrameTrace-x, one per frame: every 'rts_*=<n>' token of the line is summed per entry
# Every event is attributed to the entry in effect (the last LVL before it; -1 before the first).
# Output: one JSON line per log in <out.jsonl>.  usage: python sweep_f30a.py <list.tsv> <out.jsonl> <workers>
import json, mmap, os, re, subprocess, sys
from multiprocessing import Pool

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
XZ = 'C:/Program Files/Git/mingw64/bin/xz.exe'
GREP = 'C:/Program Files/Git/usr/bin/grep.exe'
FIXED = [b'RtSkip', b'Level has started: ', b'Shader translation cache: ', b' bda_scan=', b' rts_n=', b'Gate: rtskip=',
         b'GateArm: ', b'KytyPS5-20']
PAT = re.compile(rb'RtSkip: |RtSkipVerify: |Level has started: |Shader translation cache: | bda_scan=| rts_n=|'
                 rb'Gate: rtskip=|GateArm: |KytyPS5-20')
KIND = {b'RtSkip: ': 'RTS', b'RtSkipVerify: ': 'RTV', b'Level has started: ': 'LVL', b'Shader translation cache: ': 'TC',
        b' bda_scan=': 'BDA', b' rts_n=': 'RTSX', b'Gate: rtskip=': 'GATE', b'GateArm: ': 'GARM', b'KytyPS5-20': 'VER'}
KEEP = {'RTS': 200, 'RTV': 200, 'LVL': 400, 'TC': 20, 'GATE': 50, 'GARM': 4, 'VER': 2}
HDR = re.compile(rb'(?m)^\[\d+\]\[(\d\d):(\d\d):(\d\d\.\d\d\d)\] ')
NUM = re.compile(rb'\d+')
RTSTOK = re.compile(rb' (rts_[a-z0-9_]+)=(\d+)')
BLOCK = 90  # frames per block of the BDA band (the ABBA block of the program is 90 + 1800 at 90 flips)


def hdr_before(m, pos):
    w = 1 << 20
    while True:
        lo = max(0, pos - w)
        last = None
        for x in HDR.finditer(m, lo, pos):
            last = x
        if last is not None:
            h, mi, s = last.groups()
            return int(h) * 3600 + int(mi) * 60 + float(s)
        if lo == 0:
            return None
        w <<= 2


def line_at(m, pos):
    a = m.rfind(b'\n', 0, pos) + 1
    b = m.find(b'\n', pos)
    if b < 0:
        b = len(m)
    return m[a:min(b, a + 400)].decode('latin-1').rstrip('\r')


def new_entry(pos, line):
    return {'pos': pos, 'line': line, 'frames': 0, 'bda_sum': 0, 'bda_ge600': 0, 'bda_le300': 0, 'bda_blocks': [],
            'blk_sum': 0, 'blk_n': 0, 'rts': {}, 'rtsx_lines': 0, 'rts_bad_lines': 0}


def scan(m, timed):
    ent = [new_entry(-1, '(before the first entry)')]
    lines = {}
    totals = {}
    for x in PAT.finditer(m):
        k = KIND[x.group(0)]
        pos = x.start()
        e = ent[-1]
        if k == 'BDA':
            n = NUM.match(m, x.end())
            v = int(n.group(0)) if n else 0
            e['frames'] += 1
            e['bda_sum'] += v
            e['bda_ge600'] += v >= 600
            e['bda_le300'] += v <= 300
            e['blk_sum'] += v
            e['blk_n'] += 1
            if e['blk_n'] == BLOCK:
                e['bda_blocks'].append(round(e['blk_sum'] / BLOCK, 1))
                e['blk_sum'] = e['blk_n'] = 0
            continue
        if k == 'RTSX':
            seg = m[pos:pos + 1600]
            e['rtsx_lines'] += 1
            for name, val in RTSTOK.findall(seg):
                nm = name.decode()
                e['rts'][nm] = e['rts'].get(nm, 0) + int(val)
                if nm == 'rts_bad' and val != b'0':
                    e['rts_bad_lines'] += 1
            continue
        totals[k] = totals.get(k, 0) + 1
        ln = line_at(m, pos)
        if k == 'LVL':
            ent.append(new_entry(pos, ln))
        if len(lines.setdefault(k, [])) < KEEP[k]:
            lines[k].append((len(ent) - 2, ln))
    t_end = hdr_before(m, len(m)) if timed else None
    for i, e in enumerate(ent):
        if e['blk_n'] >= BLOCK // 3:
            e['bda_blocks'].append(round(e['blk_sum'] / e['blk_n'], 1))
        del e['blk_sum'], e['blk_n']
        e['bda_mean'] = round(e['bda_sum'] / e['frames'], 1) if e['frames'] else None
        if timed and i >= 1:
            nxt = ent[i + 1]['pos'] if i + 1 < len(ent) else len(m)
            t0, t1 = hdr_before(m, e['pos']), hdr_before(m, nxt)
            e['hold_s'] = None if t0 is None or t1 is None else (t1 - t0 + 86400 if t1 < t0 else t1 - t0)
        else:
            e['hold_s'] = None
    return ent, lines, totals, t_end


def sweep(row):
    path, size, mtime, root, js = row
    if os.path.exists(LOCK):
        return {'halt': 'LOCK'}
    if os.path.exists(STOP):
        return {'halt': 'STOP'}
    res = {'path': path, 'size': size, 'mtime': mtime, 'json': js, 'xz': path.endswith('.xz')}
    if size == 0:
        res['empty'] = True
        return res
    if path.endswith('.xz'):
        xz = subprocess.Popen([XZ, '-dc', path], stdout=subprocess.PIPE)
        args = [GREP, '-aF']
        for s in FIXED:
            args += ['-e', s.decode()]
        gp = subprocess.run(args, stdin=xz.stdout, stdout=subprocess.PIPE)
        xz.stdout.close()
        xz.wait()
        res['xz_rc'] = xz.returncode
        buf = gp.stdout
        ent, lines, totals, t_end = scan(buf, False)
    else:
        with open(path, 'rb') as f:
            m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            ent, lines, totals, t_end = scan(m, True)
            m.close()
    res['entries'] = ent
    res['lines'] = lines
    res['totals'] = totals
    res['t_end'] = t_end
    if js and js != '-' and ';' not in js and os.path.isfile(js) and js.endswith('.json'):
        try:
            d = json.load(open(js, encoding='utf-8'))
            res['binary_sha256'] = d.get('binary_sha256') or d.get('exe_sha256') or d.get('binary')
            env = d.get('env')
            env = env if isinstance(env, str) else json.dumps(env)
            res['env_rtskip'] = re.findall(r"KYTY_RT_SKIP'?\"?\s*[:=]\s*'?\"?([^'\",}]*)", env or '')
            res['env_gatefile'] = re.findall(r"KYTY_GATE_FILE'?\"?\s*[:=]\s*'?\"?([^'\",}]*)", env or '')
            res['env_sched'] = re.findall(r"KYTY_GATE_SCHEDULE[A-Z_]*'?\"?\s*[:=]\s*'?\"?([^'\",}]*)", env or '')
            res['env_ft'] = re.findall(r"KYTY_FRAME_TRACE'?\"?\s*[:=]\s*'?\"?([^'\",}]*)", env or '')
            res['guest_args'] = d.get('guest_args')
            res['started'] = d.get('started')
        except Exception as e:  # noqa
            res['json_error'] = repr(e)[:200]
    return res


def main():
    lst, out, workers = sys.argv[1], sys.argv[2], int(sys.argv[3])
    rows = []
    for line in open(lst, encoding='utf-8'):
        p, s, mt, r, js = line.rstrip('\n').split('\t')
        rows.append((p, int(s), int(mt), r, js))
    done = set()
    if os.path.exists(out):
        for line in open(out, encoding='utf-8'):
            done.add(json.loads(line)['path'])
    todo = [r for r in rows if r[0] not in done]
    todo.sort(key=lambda r: -r[1])  # largest first: the pool ends evenly
    print('logs', len(rows), 'done', len(done), 'todo', len(todo), flush=True)
    halted = None
    with Pool(workers) as pool, open(out, 'a', encoding='utf-8', newline='\n') as f:
        for res in pool.imap_unordered(sweep, todo):
            if 'halt' in res:
                halted = res['halt']
                pool.terminate()
                break
            f.write(json.dumps(res) + '\n')
            f.flush()
    if halted:
        print('HALT', halted)
        sys.exit(5 if halted == 'LOCK' else 4)
    print('ALL DONE')


if __name__ == '__main__':
    main()

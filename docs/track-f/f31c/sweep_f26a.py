# F26a (HPP-688, ROADMAP s122 item 629(v)(3)): sweep of the game logs of list_f26a.tsv for the entries of 'intro_next' and
# for the B25 signature.  Pass 1 (every log, C speed): counts of the byte strings
#   E  = b'Level has started: intro_next'        (entry of the scene; the guest prints it through fwrite -> 'GuestOut: ')
#   S1 = b'There are too many objects/batches'   (text of the assert of command_buffer_writer.ppr.cpp:31)
#   S2 = b'command_buffer_writer.ppr.cpp'         (file of the assert)
#   S3 = b'pc=0x00000009004a020e'                 (trap 'int 0x42' of the assert stub 0x4a01e0 + 0x2e)
# Pass 2 (only logs with E > 0 or S1/S2/S3 > 0): line walk - every 'Level has started:' line (line number, name, time of the
# last '[tid][HH:MM:SS.fff]' header before it), time of the last header of the log, 'Event: quit' line, sum of 'dt_us' of
# 'FrameTrace: n=' lines after every intro_next entry up to the next 'Level has started:' (frames, sum_us), line numbers
# of S1/S2/S3.  Hold of an entry: wall = (time of the next 'Level has started:' or of the last header) - entry time.
# Output: one JSON line per log in <out.jsonl>; logs already in the output are skipped (resume).  usage:
#   python sweep_f26a.py <list.tsv> <out.jsonl> <workers> [<path-substring filter>]
import json, lzma, mmap, os, re, sys
from multiprocessing import Pool

E = b'Level has started: intro_next'
SIGS = (b'There are too many objects/batches', b'command_buffer_writer.ppr.cpp', b'pc=0x00000009004a020e')
HDR = re.compile(rb'^\[(\d+)\]\[(\d\d):(\d\d):(\d\d\.\d\d\d)\] ')
LVL = re.compile(rb'Level has started: ?(\S*)')
FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')


def count_plain(p):
    with open(p, 'rb') as f:
        if os.path.getsize(p) == 0:
            return [0, 0, 0, 0]
        m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        res = []
        for s in (E,) + SIGS:
            n = 0; i = m.find(s)
            while i >= 0:
                n += 1; i = m.find(s, i + len(s))
            res.append(n)
        m.close()
        return res


def count_xz(p):
    res = [0, 0, 0, 0]
    keep = b''
    with lzma.open(p, 'rb') as f:
        while True:
            ch = f.read(1 << 24)
            if not ch:
                break
            buf = keep + ch
            for k, s in enumerate((E,) + SIGS):
                # count occurrences that end inside the new chunk (avoid double count across the overlap)
                i = buf.find(s)
                while i >= 0:
                    if i + len(s) > len(keep):
                        res[k] += 1
                    i = buf.find(s, i + len(s))
            keep = buf[-64:]
    return res


def opener(p):
    return lzma.open(p, 'rb') if p.endswith('.xz') else open(p, 'rb', buffering=1 << 22)


def walk(p):
    levels = []
    last_t = None
    quit_line = None
    sig_lines = []
    cur_intro = None  # index in levels of the open intro_next entry
    n = 0
    with opener(p) as f:
        for line in f:
            n += 1
            m = HDR.match(line)
            if m:
                last_t = int(m.group(2)) * 3600 + int(m.group(3)) * 60 + float(m.group(4))
                continue
            if b'Level has started:' in line:
                lm = LVL.search(line)
                name = lm.group(1).decode('latin1') if lm else ''
                levels.append({'line': n, 'name': name, 't': last_t, 'frames': 0, 'sum_us': 0, 'first_n': None})
                cur_intro = len(levels) - 1 if name == 'intro_next' else None
                continue
            if cur_intro is not None and line.startswith(b'FrameTrace: n='):
                fm = FT.match(line)
                if fm:
                    L = levels[cur_intro]
                    if L['first_n'] is None:
                        L['first_n'] = int(fm.group(1))
                    L['frames'] += 1; L['sum_us'] += int(fm.group(2))
                continue
            if quit_line is None and line.startswith(b'Event: quit'):
                quit_line = n
            for k, s in enumerate(SIGS):
                if s in line:
                    sig_lines.append((k + 1, n, last_t))
    return {'lines': n, 'levels': levels, 'last_t': last_t, 'quit_line': quit_line, 'sig_lines': sig_lines[:20]}


def one(row):
    p = row[0]
    rec = {'path': p, 'size': int(row[1]), 'json': row[4]}
    try:
        c = count_xz(p) if p.endswith('.xz') else count_plain(p)
        rec['E'], rec['S1'], rec['S2'], rec['S3'] = c
        if c[0] or c[1] or c[2] or c[3]:
            rec['walk'] = walk(p)
    except Exception as e:
        rec['error'] = '%s: %s' % (type(e).__name__, e)
    return rec


if __name__ == '__main__':
    lst, out, workers = sys.argv[1], sys.argv[2], int(sys.argv[3])
    flt = sys.argv[4] if len(sys.argv) > 4 else None
    rows = [l.rstrip('\n').split('\t') for l in open(lst, encoding='utf-8') if l.strip()]
    done = set()
    if os.path.exists(out):
        for l in open(out, encoding='utf-8'):
            done.add(json.loads(l)['path'])
    todo = [r for r in rows if r[0] not in done and (flt is None or flt in r[0])]
    print('rows', len(rows), 'done', len(done), 'todo', len(todo), flush=True)
    with Pool(workers) as pool, open(out, 'a', encoding='utf-8', newline='\n') as o:
        for rec in pool.imap_unordered(one, todo):
            o.write(json.dumps(rec) + '\n'); o.flush()
    print('finished', flush=True)

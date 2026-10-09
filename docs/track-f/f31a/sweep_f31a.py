# F31a (HPP-729, ROADMAP s122 item 664(l)(3)): sweep of the plain game logs of list_f31a.tsv for the B25 signature (the three
# strings of sweep_f26a.py, item 630(g)(5)) and for every scene entry.  The form of sweep_f26a.py generalised from
# 'intro_next' to every scene: for each non-empty 'Level has started: <name>' line - its byte offset, the time of the last
# '[tid][HH:MM:SS.fff]' header before it, the frames and the sum of 'dt_us' of the 'FrameTrace: n=' lines after it up to the
# next non-empty 'Level has started:' (the hold of the entry by the guest's frames, the definition of F26a s.3); for each
# signature line - its offset, the entry it falls into and the sum of dt_us of that entry before it.  Also the build line
# ('version: Fork build ...'), the 'RtSkip: mode' lines, the counts of '--- Error ---', 'Unhandled host exception',
# 'Event: quit', and the tag json fields binary_sha256 / guest_args / KYTY_* env.
# .xz logs are not swept here (see f31a.md s.3: all are the HPP-401 compressions of session <= 139 logs).
# Before every file the worker checks C:/kyty/SEALED_RUN.lock and C:/kyty/f287/STOP: either present - the file is not read
# and the record says 'skipped_lock' (the run is resumable: such records are re-tried on the next call).
# usage: python sweep_f31a.py <list.tsv> <out.jsonl> <workers>
import json, lzma, mmap, os, re, sys
from multiprocessing import Pool

SIGS = (b'There are too many objects/batches', b'command_buffer_writer.ppr.cpp', b'pc=0x00000009004a020e')
LVL = b'Level has started:'
HDR = re.compile(rb'\n\[(\d+)\]\[(\d\d):(\d\d):(\d\d\.\d\d\d)\] ')
FT = re.compile(rb'\nFrameTrace: n=(\d+) dt_us=(\d+)')
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'


def find_all(m, s):
    out = []
    i = m.find(s)
    while i >= 0:
        out.append(i)
        i = m.find(s, i + len(s))
    return out


def line_at(m, pos):
    a = m.rfind(b'\n', 0, pos) + 1
    b = m.find(b'\n', pos)
    if b < 0:
        b = len(m)
    return a, m[a:b].rstrip(b'\r')


def hdr_time(m, pos):
    # the last header at or before pos (search back at most 8 MiB)
    lo = max(0, pos - (1 << 23))
    best = None
    for h in HDR.finditer(m, lo, pos):
        best = h
    if best is None:
        return None
    return int(best.group(2)) * 3600 + int(best.group(3)) * 60 + float(best.group(4))


def tag_json(js):
    if js == '-':
        return {}
    try:
        d = json.loads(lzma.open(js, 'rt', encoding='utf-8').read()) if js.endswith('.xz') else json.load(open(js, encoding='utf-8'))
    except Exception as e:
        return {'json_error': '%s: %s' % (type(e).__name__, e)}
    env = d.get('env') or {}
    return {'binary_sha256': d.get('binary_sha256'), 'guest_args': d.get('guest_args'),
            'env': {k: v for k, v in env.items() if str(k).startswith('KYTY_')} if isinstance(env, dict) else None}


def one(row):
    p, size, mtime, js = row[0], int(row[1]), row[2], row[3]
    rec = {'path': p, 'size': size, 'mtime': mtime, 'json': js}
    if os.path.exists(LOCK) or os.path.exists(STOP):
        rec['skipped_lock'] = True
        return rec
    rec.update(tag_json(js))
    try:
        with open(p, 'rb') as f:
            if size == 0:
                rec['empty'] = True
                return rec
            m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            try:
                bi = m.find(b'version: Fork build ')
                rec['build'] = line_at(m, bi)[1].decode('latin1').strip() if bi >= 0 else None
                rec['rtskip'] = sorted(set(line_at(m, i)[1].decode('latin1')[:40] for i in find_all(m, b'RtSkip: mode ')))
                rec['n_error'] = len(find_all(m, b'--- Error ---'))
                rec['n_unhandled'] = len(find_all(m, b'Unhandled host exception'))
                rec['n_quit'] = len(find_all(m, b'Event: quit'))
                ents = []
                for i in find_all(m, LVL):
                    a, ln = line_at(m, i)
                    name = ln.split(LVL, 1)[1].strip().decode('latin1')
                    if not name:
                        continue
                    ents.append({'off': i, 'name': name, 't': hdr_time(m, i), 'frames': 0, 'sum_us': 0})
                sig = []
                for k, s in enumerate(SIGS):
                    for i in find_all(m, s):
                        sig.append({'k': k + 1, 'off': i, 't': hdr_time(m, i)})
                rec['S'] = [sum(1 for x in sig if x['k'] == k) for k in (1, 2, 3)]
                if ents:
                    offs = [e['off'] for e in ents]
                    j = 0
                    for fm in FT.finditer(m, ents[0]['off']):
                        o = fm.start()
                        while j + 1 < len(offs) and o > offs[j + 1]:
                            j += 1
                        ents[j]['frames'] += 1
                        ents[j]['sum_us'] += int(fm.group(2))
                    # signature -> entry and the hold before it
                    for x in sig:
                        jj = None
                        for q, e in enumerate(ents):
                            if e['off'] < x['off']:
                                jj = q
                        x['ent'] = jj
                        if jj is not None:
                            us = 0; fr = 0
                            for fm in FT.finditer(m, ents[jj]['off'], x['off']):
                                us += int(fm.group(2)); fr += 1
                            x['ent_frames'] = fr; x['ent_us'] = us
                rec['entries'] = [{k: v for k, v in e.items() if k != 'off'} | {'off': e['off']} for e in ents]
                rec['sig'] = sig[:30]
            finally:
                m.close()
    except Exception as e:
        rec['error'] = '%s: %s' % (type(e).__name__, e)
    return rec


if __name__ == '__main__':
    lst, out, workers = sys.argv[1], sys.argv[2], int(sys.argv[3])
    rows = [l.rstrip('\n').split('\t') for l in open(lst, encoding='utf-8') if l.strip()]
    rows = [r for r in rows if not r[0].endswith('.xz')]
    done = set()
    if os.path.exists(out):
        for l in open(out, encoding='utf-8'):
            d = json.loads(l)
            if not d.get('skipped_lock'):
                done.add(d['path'])
    todo = [r for r in rows if r[0] not in done]
    todo.sort(key=lambda r: int(r[1]))
    print('rows', len(rows), 'done', len(done), 'todo', len(todo), flush=True)
    skipped = 0
    with Pool(workers) as pool, open(out, 'a', encoding='utf-8', newline='\n') as o:
        for rec in pool.imap_unordered(one, todo):
            if rec.get('skipped_lock'):
                skipped += 1
                continue
            o.write(json.dumps(rec) + '\n'); o.flush()
    print('finished; skipped for lock/STOP', skipped, flush=True)

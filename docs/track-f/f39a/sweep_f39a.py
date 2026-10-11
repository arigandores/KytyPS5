# F39a (HPP-767): witness sweep of F24 (ROADMAP s122 item 691(zh)(3)) - per log: build hash ('Fork build <owner>/<repo>
# <hash>'), FixB24 mode line, every 'Controller <id>: removed' line, every 'MainTaskLate: us=<n>' line, pad connect lines,
# and the context markers that classify a long MainTaskLate (startup preparation wait, MainStallTest, TestHidLoss stand
# lines, first level entry). Byte search per literal on 32 MiB chunks (line numbers by counting newlines); .xz streamed.
# Usage: python sweep_f39a.py <list.tsv> <out.jsonl> [workers]
import json, lzma, os, sys
from multiprocessing import Pool

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
CHUNK = 32 << 20
NL = b'\n'
# marker -> key; the whole line is kept (cut to 300 bytes) for every hit
MARKERS = [
    (b'MainTaskLate: us=', 'late'),
    (b': removed', 'removed'),
    (b'Fork build ', 'build'),
    (b'FixB24: mode=', 'fixb24'),
    (b'TestHidLoss: ', 'hidloss'),
    (b'MainStallTest: queued', 'stall'),
    (b'PrepareHold: ms=', 'prephold'),
    (b'ShaderPreparation: startup wait finished', 'prepdone'),
    (b'Level has started: ', 'level'),
    (b'disconnect of unknown id', 'unknown_id'),
    (b'" type=', 'connect'),
]
CAP = {'level': 4, 'build': 2, 'connect': 50, 'hidloss': 50}


def line_at(buf, pos):
    s = buf.rfind(NL, 0, pos) + 1
    e = buf.find(NL, pos)
    if e < 0:
        e = len(buf)
    return s, e


def scan(path):
    if os.path.exists(LOCK) or os.path.exists(STOP):
        return {'path': path, 'error': 'LOCK_OR_STOP'}
    hits = {k: [] for _, k in MARKERS}
    lines_before = 0
    nbytes = 0
    carry = b''
    try:
        f = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
        with f:
            while True:
                data = f.read(CHUNK)
                if not data:
                    break
                nbytes += len(data)
                buf = carry + data
                cut = buf.rfind(NL)
                if cut < 0:
                    carry = buf
                    continue
                work, carry = buf[:cut + 1], buf[cut + 1:]
                for lit, key in MARKERS:
                    cap = CAP.get(key, 100000)
                    pos = work.find(lit)
                    while pos >= 0 and len(hits[key]) < cap:
                        s, e = line_at(work, pos)
                        if key == 'removed' and not work[s:e].lstrip().startswith(b'Controller '):
                            pos = work.find(lit, e)
                            continue
                        if key == 'connect' and not work[s:e].lstrip().startswith(b'Controller '):
                            pos = work.find(lit, e)
                            continue
                        n = lines_before + work.count(NL, 0, s) + 1
                        hits[key].append([n, work[s:e][:300].decode('utf-8', 'replace').rstrip(chr(13))])
                        pos = work.find(lit, e)
                lines_before += work.count(NL)
            if carry:
                lines_before += 1
    except Exception as ex:  # noqa: BLE001
        return {'path': path, 'error': repr(ex)[:200]}
    return {'path': path, 'bytes': nbytes, 'lines': lines_before, 'hits': {k: v for k, v in hits.items() if v}}


def main():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        sys.exit(3)
    lst, out = sys.argv[1], sys.argv[2]
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    paths = []
    for l in open(lst, encoding='utf-8'):
        p, size, _ = l.rstrip(chr(10)).split(chr(9))
        paths.append((int(size), p))
    paths.sort(reverse=True)
    seen = set()
    if os.path.exists(out):  # resume: keep finished records, rescan the rest
        for l in open(out, encoding='utf-8'):
            try:
                r = json.loads(l)
            except ValueError:
                continue
            if 'error' not in r:
                seen.add(r['path'])
    paths = [x for x in paths if x[1] not in seen]
    print('to scan', len(paths), 'already', len(seen))
    done = 0
    with open(out, 'a', encoding='utf-8', newline=chr(10)) as o, Pool(workers) as pool:
        for r in pool.imap_unordered(scan, [p for _, p in paths], chunksize=1):
            o.write(json.dumps(r, ensure_ascii=True) + chr(10))
            o.flush()
            done += 1
            if r.get('error') == 'LOCK_OR_STOP':
                print('LOCK_OR_STOP seen, stopping')
                pool.terminate()
                sys.exit(3)
    print('scanned', done, 'of', len(paths))


if __name__ == '__main__':
    main()

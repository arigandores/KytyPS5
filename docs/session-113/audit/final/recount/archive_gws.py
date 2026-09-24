# Streaming chunked search for 'GpuWaitSlow' over archive logs; records per-file count and requested/known/current.
import glob, os, re, sys, json
from concurrent.futures import ProcessPoolExecutor
PAT = b'GpuWaitSlow'
kv = re.compile(rb'(requested|known|current)=(\d+)')
def scan(path):
    hits = []
    tail = b''
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(1 << 24)
            if not chunk:
                data = tail; tail = b''
            else:
                data = tail + chunk
                cut = data.rfind(b'\n')
                if cut < 0: tail = data; continue
                data, tail = data[:cut + 1], data[cut + 1:]
            pos = 0
            while True:
                i = data.find(PAT, pos)
                if i < 0: break
                ls = data.rfind(b'\n', 0, i) + 1; le = data.find(b'\n', i)
                if le < 0: le = len(data)
                line = data[ls:le]
                d = {k.decode(): int(v) for k, v in kv.findall(line)}
                hits.append({'line': line[:200].decode('latin1'), **d})
                pos = le
            if not chunk: break
    return path, hits
if __name__ == '__main__':
    pats = sys.argv[2:]; outp = sys.argv[1]
    files = sorted(set(f for p in pats for f in glob.glob(p)))
    res = {}
    with ProcessPoolExecutor(max_workers=6) as ex:
        for path, hits in ex.map(scan, files):
            res[path.replace(chr(92), '/')] = hits
    json.dump(res, open(outp, 'w'), indent=0)
    withhits = {p: h for p, h in res.items() if h}
    print('files', len(res), 'files with GpuWaitSlow', len(withhits), 'lines', sum(len(h) for h in withhits.values()))
    for p, h in withhits.items():
        rel = [('lt' if x.get('requested', -1) < x.get('current', -1) else ('eq' if x.get('requested') == x.get('current') else 'gt/na')) for x in h]
        print(p, len(h), {r: rel.count(r) for r in set(rel)})

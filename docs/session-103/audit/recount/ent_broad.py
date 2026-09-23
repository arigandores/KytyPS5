# Broader failure-token scan of all entry logs/stdouts plus the video run (excluding the 'tdr' false positive in 'softdrop').
import glob, re, os
TOK = [b'--- error ---', b'device lost', b'devicelost', b'vk_error', b'access violation', b'gpuhang', b'hung',
       b'nvlddmkm', b'exception', b'terminate', b'abort', b'fatal', b'gpuwaitslow', b'crash', b'assert']
files = sorted(glob.glob('C:/kyty/s103/log_ent103_*.txt') + glob.glob('C:/kyty/s103/stdout_ent103_*.txt') +
               ['C:/kyty/s103/log_vid103.txt', 'C:/kyty/s103/stdout_vid103.txt'])
out = []
hits_by_token = {}
for p in files:
    with open(p, 'rb') as f:
        for n, ln in enumerate(f, 1):
            low = ln.lower()
            for t in TOK:
                if t in low:
                    key = (t, re.sub(rb'\d+', b'#', ln.strip()[:90]))
                    hits_by_token.setdefault(key, []).append(os.path.basename(p))
                    break
for (t, ln), fs in sorted(hits_by_token.items(), key=lambda kv: -len(kv[1])):
    s = '%-18s files=%3d lines=%5d  %s' % (t.decode(), len(set(fs)), len(fs), ln.decode('latin1'))
    print(s); out.append(s)
open('C:/kyty/s103/audit103/recount/ent_broad.out.txt', 'w').write('\n'.join(out) + '\n')

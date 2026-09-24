import glob, os, re, sys, json
from multiprocessing import Pool
PAT=(b'GpuWaitSlow:', b'GpuHangAbort:')
def scan(p):
    hits=[]
    CH=64<<20
    with open(p,'rb') as f:
        tail=b''
        off=0
        while True:
            buf=f.read(CH)
            if not buf: break
            data=tail+buf
            for pat in PAT:
                s=0
                while True:
                    k=data.find(pat,s)
                    if k<0: break
                    e=data.find(b'\n',k)
                    if e<0: e=len(data)
                    line=data[k:e][:400].decode('utf-8','replace')
                    hits.append(line)
                    s=k+1
            # keep last 512 bytes, but avoid double counting: drop hits starting in the tail region next time
            tail=data[-512:]
            # remove any partial pattern double count: simplistic - dedupe later
    # dedupe identical consecutive (overlap)
    out=[]
    for h in hits:
        if not out or out[-1]!=h: out.append(h)
    return p, out
if __name__=='__main__':
    which=sys.argv[1]
    if which=='new':
        files=[p for d in ['s104','s105','s106','s107','s108','s109','s110','s111','s112','s113'] for p in glob.glob(f'C:/kyty/{d}/log_*.txt')]
    else:
        files=[p for d in range(80,100) for p in glob.glob(f'C:/kyty/s{d}/log_*.txt')]
    with Pool(6) as pool:
        res=pool.map(scan, files, chunksize=1)
    tot=0
    for p,h in sorted(res):
        if h:
            print(p, len(h))
            for x in h: print('   ', x[:300])
            tot+=len(h)
    print('files',len(files),'hits',tot)

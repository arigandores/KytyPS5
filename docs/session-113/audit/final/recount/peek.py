import sys
path=sys.argv[1]; prefixes=[p.encode() for p in sys.argv[2].split(',')]; nmax=int(sys.argv[3]) if len(sys.argv)>3 else 2
cnt={p:0 for p in prefixes}
with open(path,'rb') as f:
    for line in f:
        for p in prefixes:
            if line.startswith(p) and cnt[p]<nmax:
                cnt[p]+=1
                print(line[:1500].decode('latin1').rstrip())
        if all(c>=nmax for c in cnt.values()): break

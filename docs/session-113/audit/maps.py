import re,sys
p=sys.argv[1]
pat=re.compile(rb'(MapDirect|MapFlexible|MapNamed|sceKernelMmap|Memory: map|MapGpu|VirtualAlloc|reserve)', re.I)
n=0; out=[]
with open(p,'rb') as f:
    for i,line in enumerate(f):
        if i>3000000: break
        if pat.search(line):
            n+=1
            if len(out)<25: out.append(line[:220])
print(n)
for l in out: print(l)

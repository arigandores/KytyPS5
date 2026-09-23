import os,re,sys
root=sys.argv[1]; pat=re.compile(sys.argv[2]); 
for dp,dn,fn in os.walk(root):
    for f in fn:
        if f.endswith(('.cpp','.h','.inc')):
            p=os.path.join(dp,f)
            try: L=open(p,encoding='utf-8',errors='replace').read().split('\n')
            except: continue
            for i,l in enumerate(L):
                if pat.search(l): print(f'{p}:{i+1}: {l.strip()[:200]}')

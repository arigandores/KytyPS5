import json,pickle,hashlib,glob,collections,sys
res=json.load(open('sample.json',encoding='utf-8'))
SEG='C:/kyty/f287/f32a/seg'
tot_ok=0;rows=[]
for r in res:
    p=r['path'];md=hashlib.md5(p.encode('utf-8')).hexdigest()
    fs=sorted(glob.glob(SEG+'/'+md+'_[0-9]*.pkl'))
    a=collections.Counter();lines=0
    for f in fs:
        d=pickle.load(open(f,'rb'))
        for k,v in d['sigs'].items(): a[k.decode('latin1')]+=v[0]
        lines+=d['lines']
    b=collections.Counter(r['sigs'])
    eq=(a==b)
    diff=[(k,a[k],b[k]) for k in set(a)|set(b) if a[k]!=b[k]]
    rows.append((eq,len(fs),len(a),len(b),sum(a.values()),sum(b.values()),lines,r['lines'],p))
    if eq: tot_ok+=1
    else: print('DIFF',p,diff[:5])
for x in rows: print(x)
print('equal',tot_ok,'of',len(res))

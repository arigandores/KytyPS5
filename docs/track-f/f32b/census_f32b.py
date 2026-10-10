import re,collections,sys
L=open('reg.md',encoding='utf-8').read().split('\n')
idre=re.compile(r'(?<![\w`])([БФ]\d+[абвгд]?)(?![\w])')
sec=None;rows=collections.defaultdict(list)
for i,l in enumerate(L):
    m=re.match(r'^##+ (\d+(?:\.\d+)?)\.',l)
    if m: sec=m.group(1)
    if sec in ('48.2','103'): continue
    if l.startswith('|') and not l.startswith('|---'):
        cells=[x.strip() for x in l.strip().strip('|').split('|')]
        c0=re.sub(r'\(.*','',cells[0])
        for x in idre.findall(c0): rows[x].append((i+1,sec,cells))
W=[('FIXED',re.compile(r'`?FIXED`?')),('НД',re.compile(r'НЕ ДЕФЕКТ')),('ТУПИК',re.compile(r'ТУПИК')),('дубль',re.compile(r'дубль'))]
def key(s):
    n=re.match(r'([БФ])(\d+)(.*)',s); return (n.group(1),int(n.group(2)),n.group(3))
out=[]
for k in sorted(rows,key=key):
    ln,sec,c=rows[k][-1]
    txt=' | '.join(c[1:])
    hits=[w for w,rx in W if rx.search(txt)]
    allhits=sorted({w for (_,_,cc) in rows[k] for w,rx in W if rx.search(' | '.join(cc[1:]))})
    out.append((k,ln,sec,c[1][:40] if len(c)>1 else '',hits,allhits,len(rows[k])))
for o in out: print(o)
print(len(out))

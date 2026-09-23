"""surgery.py <in.dis> <out.dis> <modes>  modes: comma list of noslow,nodword,nobounds
Rewrites branch/select conditions of the V2' lean BDA emission to constant true (analysis only)."""
import re,sys
src,dst,modes=sys.argv[1],sys.argv[2],set(sys.argv[3].split(','))
lines=open(src,encoding='utf-8').read().split('\n')
defs={}; consts={}
for l in lines:
    m=re.match(r'\s*%(\d+) = (Op\w+)\s*(.*)',l)
    if m:
        defs[int(m.group(1))]=(m.group(2),m.group(3).split())
        if m.group(2)=='OpConstant': consts[int(m.group(1))]=m.group(3).split()[1]
def r(a): return int(a[1:]) if a.startswith('%') else None
def is_andc(x,c):
    return x in defs and defs[x][0]=='OpBitwiseAnd' and r(defs[x][1][2]) in consts and consts[r(defs[x][1][2])]==str(c)
fits=set(); aligned=set(); inrange=set()
for i,(op,a) in defs.items():
    if op=='OpULessThanEqual' and is_andc(r(a[1]),16383): fits.add(i)
    if op=='OpIEqual' and is_andc(r(a[1]),15): aligned.add(i)
# bool type and true const
booltype=[i for i,(op,a) in defs.items() if op=='OpTypeBool'][0]
true=[i for i,(op,a) in defs.items() if op=='OpConstantTrue']
out=[]; n={'noslow':0,'nodword':0,'nobounds':0}
newtrue=None
if not true:
    newtrue=max(defs)+1
    true=[newtrue]
T='%%%d'%true[0]
# bounds selects: OpSelect %u32 %c %v %zero where c = OpULessThan (u32) and zero const 0
zeros={i for i,v in consts.items() if v=='0'}
for l in lines:
    m=re.match(r'(\s*)OpBranchConditional (%\d+) (.*)',l)
    if m:
        c=r(m.group(2))
        if c in fits and 'noslow' in modes: l='%sOpBranchConditional %s %s'%(m.group(1),T,m.group(3)); n['noslow']+=1
        elif c in aligned and 'nodword' in modes: l='%sOpBranchConditional %s %s'%(m.group(1),T,m.group(3)); n['nodword']+=1
    m=re.match(r'(\s*)(%\d+) = OpSelect (%\d+) (%\d+) (%\d+) (%\d+)$',l)
    if m and 'nobounds' in modes:
        c=r(m.group(4)); z=r(m.group(6))
        if c in defs and defs[c][0]=='OpULessThan' and z in zeros:
            l='%s%s = OpCopyObject %s %s'%(m.group(1),m.group(2),m.group(3),m.group(5)); n['nobounds']+=1
    out.append(l)
    if newtrue and re.match(r'\s*%%%d = OpTypeBool'%booltype,l):
        out.append('%%%d = OpConstantTrue %%%d'%(newtrue,booltype))
txt='\n'.join(out)
if newtrue:
    txt=re.sub(r'; Bound: (\d+)', lambda m:'; Bound: %d'%(max(int(m.group(1)),newtrue+1)), txt)
open(dst,'w',encoding='utf-8').write(txt)
print(n, 'fits',len(fits),'aligned',len(aligned))

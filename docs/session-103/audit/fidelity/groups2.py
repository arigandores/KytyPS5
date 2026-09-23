import re,sys,glob,collections,os
sys.path.insert(0,os.path.dirname(__file__))
from groups import load, ref
def analyze(p):
    ins,order,consts,types=load(p)
    calls=collections.Counter(args[1] for rid,op,args in order if op=='OpFunctionCall')
    bda=calls.most_common(1)[0][0]
    fits_ids=set()
    for rid,op,args in order:
        if op=='OpULessThanEqual':
            a=ref(args[1])
            if a in ins and ins[a][0]=='OpBitwiseAnd' and ref(ins[a][1][2]) in consts and consts[ref(ins[a][1][2])]==16383:
                fits_ids.add(rid)
    slow_labels={}
    for i,(rid,op,args) in enumerate(order):
        if op=='OpBranchConditional' and ref(args[0]) in fits_ids:
            slow_labels[args[2]]=True
    # walk
    in_slow=False; slow=0; fast=0; in_fn_bda=False
    selects_zero=0
    cur_fn=None
    for rid,op,args in order:
        if op=='OpFunction': cur_fn='%%%d'%rid
        if cur_fn==bda: continue
        if op=='OpLabel':
            in_slow = ('%%%d'%rid) in slow_labels
        if op=='OpFunctionCall' and args[1]==bda:
            if in_slow: slow+=1
            else: fast+=1
    # bounds selects: OpSelect %u32 %cond %x %c0 where cond is OpULessThan
    for rid,op,args in order:
        if op=='OpSelect':
            c=ref(args[1]); z=ref(args[3])
            if c in ins and ins[c][0]=='OpULessThan' and z in consts and consts[z]==0:
                selects_zero+=1
    return bda,fast,slow,len(fits_ids),selects_zero
for p in sorted(glob.glob(sys.argv[1])):
    bda,fast,slow,nf,sz=analyze(p)
    print(os.path.basename(p),'lookups_nonslow',fast,'lookups_slow',slow,'fits_checks',nf,'bounds_selects(ULessThan->select 0)',sz)

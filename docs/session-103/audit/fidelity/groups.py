import re,sys,glob,collections,os
def load(p):
    ins={}; order=[]; consts={}; types={}
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        m=re.match(r'%(\d+) = (Op\w+)\s*(.*)',l)
        if m:
            rid=int(m.group(1)); op=m.group(2); args=m.group(3).split()
            ins[rid]=(op,args); order.append((rid,op,args))
            if op=='OpConstant':
                consts[rid]=int(args[1]) if args[1].lstrip('-').isdigit() else args[1]
            if op.startswith('OpType'): types[rid]=(op,args)
        else:
            m=re.match(r'(Op\w+)\s*(.*)',l)
            if m: order.append((None,m.group(1),m.group(2).split()))
    return ins,order,consts,types
def ref(a): return int(a[1:]) if a.startswith('%') else None
def analyze(p):
    ins,order,consts,types=load(p)
    # bda function = the function called with (u64,bool) returning u64 most often
    calls=collections.Counter()
    for rid,op,args in order:
        if op=='OpFunctionCall': calls[args[1]]+=1
    bda=None
    # find function def with name? use OpName absent; pick function whose body contains OpShiftRightLogical by 14
    fn_defs=[(rid,args) for rid,op,args in order if op=='OpFunction']
    # heuristic: the most-called function
    bda=calls.most_common(1)[0][0] if calls else None
    ncalls=calls.get(bda,0)
    fits=0; aligned=[]; spans=[]
    for rid,op,args in order:
        if op=='OpULessThanEqual':
            a=ref(args[1]); b=ref(args[2])
            if a in ins and ins[a][0]=='OpBitwiseAnd' and ref(ins[a][1][2]) in consts and consts[ref(ins[a][1][2])]==16383:
                fits+=1
                if b in consts: spans.append(16384-consts[b])
        if op=='OpIEqual':
            a=ref(args[1]); b=ref(args[2])
            if a in ins and ins[a][0]=='OpBitwiseAnd' and ref(ins[a][1][2]) in consts and consts[ref(ins[a][1][2])]==15:
                x=ref(ins[a][1][1])
                imm=None
                if x in ins and ins[x][0]=='OpIAdd':
                    c=ref(ins[x][1][2])
                    if c in consts: imm=consts[c]
                aligned.append(imm)
    return ncalls,fits,aligned,spans
for p in sorted(glob.glob(sys.argv[1])):
    n,f,al,sp=analyze(p)
    mod=collections.Counter((a%16 if isinstance(a,int) else 'x') for a in al)
    print(os.path.basename(p), 'bda_calls',n,'multi-member groups',f,'vector groups',len(al),'imm_min%16',dict(mod),'spans',collections.Counter(sp).most_common(6))

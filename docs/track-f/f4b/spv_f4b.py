# F4b (Red Team): own SPIR-V scan of the PS 5514e10f1a60df83 cache file (independent of F4a spv_index.py)
import struct, sys, hashlib
p=sys.argv[1]
b=open(p,'rb').read()
print('file',p,'size',len(b),'sha256',hashlib.sha256(b).hexdigest()[:16])
MAGIC=0x07230203
offs=[i for i in range(0,len(b)-4,4) if struct.unpack_from('<I',b,i)[0]==MAGIC]
print('magic at (4-aligned)',offs)
# unaligned check too
ua=[i for i in range(len(b)-4) if struct.unpack_from('<I',b,i)[0]==MAGIC]
print('magic at (any)',ua)
EM={0:'Vertex',4:'Fragment',5:'GLCompute'}
SC={1:'Input',3:'Output'}
BI={22:'FragDepth'}
for o in ua:
    ver,gen,bound,_=struct.unpack_from('<IIII',b,o+4)
    i=o+20; names={}; dec={}; outs=[]; eps=[]; nwords=5; bad=None
    while i+4<=len(b):
        w=struct.unpack_from('<I',b,i)[0]; op=w&0xffff; wc=w>>16
        if wc==0: bad=('wc0',i); break
        if i+4*wc>len(b): bad=('trunc',i); break
        ws=struct.unpack_from('<%dI'%wc,b,i)
        if op==15: eps.append((EM.get(ws[1],ws[1]),))
        elif op==5:
            s=b[i+8:i+4*wc].split(b'\0')[0].decode('latin1'); names[ws[1]]=s
        elif op==71: dec.setdefault(ws[1],[]).append(ws[2:])
        elif op==59 and ws[3]==3: outs.append(ws[2])
        nwords+=wc; i+=4*wc
        if op==56: # OpFunctionEnd - keep going; module may end later
            pass
    print('module at',o,'version %x'%ver,'bound',bound,'words',nwords,'stop',bad,'entry',eps)
    nidx=sum(1 for t in dec.values() for d in t if d[0]==32)
    nloc=sum(1 for t in dec.values() for d in t if d[0]==30)
    print('  OpDecorate Index count',nidx,'Location count',nloc)
    for v in outs:
        ds=dec.get(v,[])
        print('  Output var %',v,names.get(v,'?'),'decor',[(('Location' if d[0]==30 else 'Index' if d[0]==32 else 'BuiltIn' if d[0]==11 else d[0]),)+tuple(d[1:]) for d in ds])

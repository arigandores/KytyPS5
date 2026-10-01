# F4b (Red Team): static use of outputs 16/18/19 (OpStore 62 / OpAccessChain 65 / OpEntryPoint interface) in the PS module
import struct, sys
b=open(sys.argv[1],'rb').read(); o=34532; i=o+20
st={16:0,18:0,19:0}; ac={16:0,18:0,19:0}; iface=None; ac_ids={}
while i+4<=len(b):
    w=struct.unpack_from('<I',b,i)[0]; op=w&0xffff; wc=w>>16
    if wc==0 or i+4*wc>len(b): break
    ws=struct.unpack_from('<%dI'%wc,b,i)
    if op==15:
        n=b[i+12:i+4*wc]; z=n.find(b'\0'); nw=(z//4)+1
        iface=list(ws[3+nw:])
    if op==65 and ws[3] in ac: ac[ws[3]]+=1; ac_ids[ws[2]]=ws[3]
    if op==62:
        t=ws[1]
        if t in st: st[t]+=1
        elif t in ac_ids: st[ac_ids[t]]+=1
    i+=4*wc
print('entry interface',iface)
print('OpStore to var (direct or via access chain)',st)
print('OpAccessChain on var',ac)

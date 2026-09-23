import re,sys,collections
def parse(p):
    ins=[]
    for l in open(p,encoding='utf-8',errors='replace'):
        m=re.match(r'\s*/\*([0-9a-f]{4,})\*/\s+(.*?);',l)
        if not m: continue
        addr=int(m.group(1),16); body=m.group(2).strip()
        pred=''
        mm=re.match(r'(@!?U?P\w+)\s+(.*)',body)
        if mm: pred=mm.group(1); body=mm.group(2)
        op=body.split()[0] if body else ''
        ins.append((addr,pred,op,body))
    # strip trailing BRA self / NOP
    while ins and (ins[-1][2]=='NOP' or (ins[-1][2]=='BRA' and ins[-1][3].endswith(hex(ins[-1][0])))):
        ins.pop()
    return ins
def summary(p):
    ins=parse(p)
    c=collections.Counter(i[2] for i in ins)
    base=collections.Counter(i[2].split('.')[0] for i in ins)
    return ins,c,base
if __name__=='__main__':
    for p in sys.argv[1:]:
        ins,c,base=summary(p)
        ldg={k:v for k,v in c.items() if k.startswith('LDG') or k.startswith('STG') or k.startswith('LDL') or k.startswith('STL')}
        print(p.split('/')[-1], 'n=',len(ins), 'BSSY',base['BSSY'],'BRA',base['BRA'],'ISETP',base['ISETP'],'SEL',base['SEL'],'LOP3',base['LOP3'],'IMAD',base['IMAD'], 'VOTE',base['VOTE'],'MOV',base['MOV'], ldg)

import re, sys, json, os
R='C:/kyty/s110/'
def kv(line):
    d={}
    for m in re.finditer(rb'(\w+)=(-?[0-9.]+)', line):
        d[m.group(1).decode()]=float(m.group(2))
    return d
def parse(tag):
    data=open(R+'log_%s.txt'%tag,'rb').read()
    allcs=data.count(b'CsStall:')
    ev=[]
    for m in re.finditer(rb'(?m)^(CsStall: [^\r\n]*|FrameTrace-x: [^\r\n]*|FrameTrace: [^\r\n]*)', data):
        ev.append((m.start(), m.group(1)))
    stalls=[]; rows=[]; mains=[]
    first_x=None; last_main_n=None
    for pos,l in ev:
        if l.startswith(b'CsStall:'):
            m=re.match(rb'CsStall: kind=(\w+) us=(\d+) id=(\d+) hash=0x([0-9a-f]+)', l)
            stalls.append(dict(pos=pos, kind=m.group(1).decode(), us=int(m.group(2)), id=int(m.group(3)), hash=m.group(4).decode(), after_first_x = first_x is not None, main_n=last_main_n, nx=len(rows)))
        elif l.startswith(b'FrameTrace-x:'):
            d=kv(l)
            if first_x is None: first_x=pos
            rows.append({k:d.get(k) for k in ('n','cs_sync_new','cs_sync_wait','cs_sync_new_us','cs_sync_wait_us','cspfree_hit','cspf_new','cspfree_bad')})
        else:
            m=re.search(rb' n=(\d+)', l)
            if m: last_main_n=int(m.group(1))
            mains.append(pos)
    return dict(tag=tag, allcs=allcs, stalls=stalls, rows=rows, nrows=len(rows))
if __name__=='__main__':
    out={}
    for pre in ('stl110','stl110b'):
        for i in range(1,9):
            tag='%s_%d'%(pre,i)
            r=parse(tag)
            st=r['stalls']; rows=r['rows']
            miss=[k for k in ('cs_sync_new','cs_sync_wait','cs_sync_new_us','cs_sync_wait_us') if any(x[k] is None for x in rows)]
            cn=sum(x['cs_sync_new'] or 0 for x in rows); cw=sum(x['cs_sync_wait'] or 0 for x in rows)
            cnu=sum(x['cs_sync_new_us'] or 0 for x in rows); cwu=sum(x['cs_sync_wait_us'] or 0 for x in rows)
            after=[s for s in st if s['after_first_x']]
            D=sum(s['us'] for s in st); M=max([s['us'] for s in st] or [0])
            Dafter=sum(s['us'] for s in after)
            out[tag]=dict(nrows=r['nrows'], allcs=r['allcs'], lines=len(st), lines_after=len(after), cnt=cn+cw, cnt_new=cn, cnt_wait=cw, us_new=cnu, us_wait=cwu, D=D, M=M, D_after=Dafter, missing=miss,
                          stalls=[(s['kind'],s['us'],s['id'],s['hash'][:8],s['after_first_x'],s['main_n'],s['nx']) for s in st])
            o=out[tag]
            print(tag, 'rows',o['nrows'],'allcs',o['allcs'],'lines',o['lines'],'after',o['lines_after'],'cnt',o['cnt'],'(new %d wait %d)'%(cn,cw),'us_cnt',cnu+cwu,'D',D,'D_after',Dafter,'M',M,'miss',miss)
            for s in o['stalls']: print('    ',s)
    json.dump(out,open('C:/kyty/s110/audit110/stall_parse.json','w'),indent=1)

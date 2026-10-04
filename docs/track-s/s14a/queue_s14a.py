# S14a: how many VS/PS are registered in the load window before the first new module is used (upper bound of the early queue)
import re, os, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'): sys.exit(5)
D='C:/kyty/s288/s14a/'
LV=[('t2_1','hero_kratos'),('t2_2','hero_drake'),('t2_4','armadillo_challenge_2'),('t2_5','fragile_battle_4'),('t2_7','fragile_battle_5')]
out=[]
for tag,lv in LV:
    regs=[]; fu={}; ent=None; newh=[]; first_reg=None
    for raw in open(D+'x_%s.txt'%tag,'rb'):
        ln,b=raw.rstrip(b'\n').split(b'\t',1); s=b.decode('latin1')
        if ent is None and s.startswith('GuestOut: Level has started: '+lv): ent=int(ln)
        m=re.match(r'^ShaderRegister: hash=([0-9a-f]+) type=(\d+) size=(\d+) .*? host_us=(\d+)',s)
        if m: regs.append((int(m.group(4)),m.group(1),int(m.group(2)),int(ln))); continue
        m=re.match(r'^ShaderFirstUse: hash=([0-9a-f]+) stage=(\d+) .*host_us=(\d+)',s)
        if m: fu.setdefault(m.group(1),int(m.group(3))); continue
        if ent:
            m=re.match(r'^AvTrace: shader ShaderRecompiler (VS|PS) hash=0x([0-9a-f]+)',s)
            if m: newh.append(m.group(2))
    t_use=min(fu[h] for h in newh if h in fu)
    t0=regs[0][0]
    row=[]
    for w in (1,2,5,10,30):
        x=[r for r in regs if t_use-w*1000000<=r[0]<=t_use and r[2] in (1,2)]
        d=set(r[1] for r in x)
        row.append('%ds: %d lines / %d distinct / never used %d'%(w,len(x),len(d),sum(1 for h in d if h not in fu)))
    newset=set(newh)
    # registration burst containing the new modules: host span of their min registrations
    rmin=dict()
    for t,h,ty,ln in regs: rmin[h]=min(rmin.get(h,t),t)
    span=[rmin[h] for h in newset if h in rmin]
    out.append('%s: first registration of the run at %.1f s before the first use of a new module; VS/PS registrations in the window before that use: %s; new modules %d distinct, their first registrations lie %.2f .. %.2f s before that use; all registrations are before the entry line: %s' % (
        tag,(t_use-t0)/1e6,'; '.join(row),len(newset),(t_use-max(span))/1e6,(t_use-min(span))/1e6, all(r[3]<ent for r in regs) ))
open(D+'queue_s14a.out.txt','w',encoding='utf-8',newline='\n').write('\n'.join(out)+'\n'); print('\n'.join(out))

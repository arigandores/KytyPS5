# S11a auxiliary recount: (1) S6 pcw arms - driver blob lines; (2) T2 arms - cost split after the entry line; (3) c5_0 median after entry
import re, statistics, json, sys, os, hashlib
if os.path.exists('C:/kyty/SEALED_RUN.lock'): sys.exit(5)
def lines(p, pref):
    out=[]
    with open(p,'rb') as f:
        for n,l in enumerate(f,1):
            if l.startswith(pref): out.append((n,l.rstrip().decode('latin1')))
    return out
print('== S6 driver blob lines')
for t in ('pcw_1','pcw_2','pcw_3','pcw_4','pcw_int'):
    p='C:/kyty/s288/s6/log_%s.txt'%t
    if not os.path.isfile(p): print(t,'no log'); continue
    v=lines(p,b'Vulkan pipeline cache:')
    sv=[x for x in v if 'saved' in x[1]]
    print(t,'loaded',[x[1] for x in v if 'loaded' in x[1]],'saved n',len(sv),'last',sv[-1][1] if sv else None,'disabled',sum(1 for x in v if 'disabled' in x[1]))
for d in ('C:/kyty/s288/s6/app_post',):
    for r,ds,fs in os.walk(d):
        for f in fs:
            if f=='PPSA21564.bin' and 'PipelineCache' in r:
                q=os.path.join(r,f); print(q.replace(chr(92),'/'), os.path.getsize(q), hashlib.sha256(open(q,'rb').read()).hexdigest()[:16])
print('== T2 cost split after the entry line (us)')
rs=re.compile(rb'^AvTrace: shader (.+?) hash=0x([0-9a-fA-F]+) translate_us=(\d+) compile_us=(\d+)')
ru=re.compile(rb' us=(\d+)')
LV={'t2_1':'hero_kratos','t2_cs0':'hero_kratos','t2_2':'hero_drake','t2_4':'armadillo_challenge_2','t2_5':'fragile_battle_4','t2_7':'fragile_battle_5','c5_0':'shuriken_ninja_castle'}
for t,lv in LV.items():
    ent=None; tr=0; co=0; nsh=0; asy=[]; syn=[]; allc=[]; dsv=[]; rsv=[]; rows=0; stage={}
    with open('C:/kyty/s288/s10/log_%s.txt'%t,'rb') as f:
        for n,l in enumerate(f,1):
            if l.startswith(b'FrameTrace: n='): rows+=1; continue
            if ent is None:
                if l.startswith(b'GuestOut: Level has started: '+lv.encode()): ent=n
                if l.startswith(b'AvTrace: pipeline ') and b'precache' not in l:
                    m=ru.search(l)
                    if m: allc.append((0,int(m.group(1))))
                continue
            if l.startswith(b'AvTrace: shader '):
                m=rs.match(l)
                if m:
                    tr+=int(m.group(3)); co+=int(m.group(4)); nsh+=1
                    k=m.group(1).decode('latin1'); stage[k]=stage.get(k,0)+1
            elif l.startswith(b'AvTrace: pipeline ') and b'precache' not in l:
                m=ru.search(l)
                if m:
                    allc.append((1,int(m.group(1))))
                    (asy if b' async' in l else syn).append(int(m.group(1)))
            elif l.startswith(b'Vulkan pipeline cache: saved'): dsv.append((rows,l.rstrip().decode('latin1')[22:]))
            elif l.startswith(b'PipelinePrecache: saved'): rsv.append((rows,l.rstrip().decode('latin1')[18:]))
    aft=[u for a,u in allc if a]
    print(t,'entry line',ent,'| shader lines',nsh,stage,'translate_us',tr,'compile_us',co,'| async creations',len(asy),'sum us',sum(asy),'| sync/none',len(syn),'sum us',sum(syn),'| median all',statistics.median([u for a,u in allc]) if allc else None,'n',len(allc),'median after entry',statistics.median(aft) if aft else None,'n',len(aft))
    print('    driver saves after entry (group, text):',dsv[:4]); print('    recipe saves after entry:',rsv[:6])

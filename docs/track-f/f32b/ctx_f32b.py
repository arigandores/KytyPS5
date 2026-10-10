import re,collections,sys
P=sys.argv[1]; targets=set(int(x) for x in sys.argv[2].split(','))
ft=re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
buf=[];n=0
with open(P,'rb') as f:
    for line in f:
        n+=1
        m=ft.match(line.lstrip())
        if m:
            fn=int(m.group(1))
            if fn in targets:
                c=collections.Counter()
                for ln,l in buf:
                    t=l.lstrip()
                    k=re.sub(rb'[0-9]+',b'#',t[:40])
                    c[k]+=1
                print('=== frame',fn,'line',n,line[:200]); print('interval lines',len(buf))
                for k,v in c.most_common(25): print('  ',v,k)
                for ln,l in buf:
                    if any(x in l for x in (b'Window',b'focus',b'Level has',b'MainTaskLate',b'Stall',b'saved',b'GuestOut',b'held',b'skipped draw',b'Controller',b'quit',b'Gpu',b'Translate')):
                        print('   >',ln,l[:200])
            buf=[]
            continue
        buf.append((n,line))
        if len(buf)>200000: buf=buf[-200000:]

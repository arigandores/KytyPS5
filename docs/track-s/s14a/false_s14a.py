# S14a: registered-but-unused shaders (price of a false translation), CsPretranslate precedent, big async creations
import re, os, sys, statistics, collections
if os.path.exists('C:/kyty/SEALED_RUN.lock'): sys.exit(5)
D='C:/kyty/s288/s14a/'
LV=[('t2_1','hero_kratos'),('t2_2','hero_drake'),('t2_4','armadillo_challenge_2'),('t2_5','fragile_battle_4'),('t2_7','fragile_battle_5')]
out=[]; big=[]; trc={'VS':[], 'PS':[]}
for tag,lv in LV:
    reg=collections.defaultdict(set); fu=collections.defaultdict(set); cs=collections.Counter(); csus=0; ent=None
    regl=collections.Counter(); sizes={}
    for raw in open(D+'x_%s.txt'%tag,'rb'):
        ln,b=raw.rstrip(b'\n').split(b'\t',1); s=b.decode('latin1')
        if ent is None and s.startswith('GuestOut: Level has started: '+lv): ent=int(ln)
        m=re.match(r'^ShaderRegister: hash=([0-9a-f]+) type=(\d+) size=(\d+)',s)
        if m: reg[int(m.group(2))].add(m.group(1)); regl[int(m.group(2))]+=1; sizes[m.group(1)]=int(m.group(3)); continue
        m=re.match(r'^ShaderFirstUse: hash=([0-9a-f]+) stage=(\d+)',s)
        if m: fu[int(m.group(2))].add(m.group(1)); continue
        m=re.match(r'^CsPretranslate: (\w+) hash=([0-9a-f]+)(?: us=(\d+))?',s)
        if m:
            cs[m.group(1)]+=1
            if m.group(1)=='ready': csus+=int(m.group(3))
            continue
        if ent:
            m=re.match(r'^AvTrace: pipeline gfx vs=\d+ ps=\d+ us=(\d+) total=\d+ async wait_us=(\d+)',s)
            if m and int(m.group(1))>4000: big.append((tag,int(m.group(1)),int(m.group(2))))
            m=re.match(r'^AvTrace: shader ShaderRecompiler (VS|PS) hash=0x[0-9a-f]+ translate_us=(\d+) compile_us=(\d+)',s)
            if m: trc[m.group(1)].append(int(m.group(2))+int(m.group(3)))
    used=set().union(*fu.values()) if fu else set()
    line='%s: registered distinct by type %s (lines %s); first-used hashes by stage %s; registered and never first-used: %s; CsPretranslate %s ready_us_sum %d' % (
        tag, dict((t,len(v)) for t,v in sorted(reg.items())), dict(sorted(regl.items())), dict((t,len(v)) for t,v in sorted(fu.items())),
        dict((t,len(v-used)) for t,v in sorted(reg.items())), dict(cs), csus)
    out.append(line)
    out.append('   code bytes of registered-never-used: %s' % dict((t,sum(sizes[h] for h in v-used)) for t,v in sorted(reg.items())))
out.append('async creations after the entry with us > 4000 (five arms): n %d us sorted %s; median %s; wait_us sorted %s' % (
    len(big), sorted(x[1] for x in big), statistics.median([x[1] for x in big]), sorted(x[2] for x in big)))
for k,v in trc.items():
    out.append('translate+compile us of %s translated after the entry: n %d sum %d mean %.0f median %s max %d' % (k,len(v),sum(v),statistics.mean(v),statistics.median(v),max(v)))
open(D+'false_s14a.out.txt','w',encoding='utf-8',newline='\n').write('\n'.join(out)+'\n'); print('\n'.join(out))

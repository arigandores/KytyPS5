import re,sys,collections
path=sys.argv[1]; want=set(int(x) for x in sys.argv[2].split(','))
# for each frame n in want: summarize the lines between FrameTrace n-1 and FrameTrace n
prev=None; buf=[]; out={}
ft=re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
with open(path,'rb') as f:
    for i,l in enumerate(f):
        m=ft.match(l)
        if m:
            n=int(m.group(1))
            if n in want:
                out[n]=(int(m.group(2)),list(buf))
            buf=[]
            if want and n>max(want): break
            continue
        buf.append((i+1,l))
for n,(dt,lines) in sorted(out.items()):
    spirv=[x for x in lines if b'SPIR-V words=' in x[1]]
    hashes=collections.Counter(re.search(rb'hash=(0x[0-9a-f]+)',x[1]).group(1).decode() for x in lines if b'phase begin' in x[1] and b' decode' in x[1] and re.search(rb'hash=(0x[0-9a-f]+)',x[1]))
    el=sum(int(m.group(1)) for x in lines for m in [re.search(rb'elapsed_ms=(\d+)',x[1])] if m)
    keys=[x for x in lines if re.match(rb'(PipelinePrecache|Vulkan pipeline cache|PriorityStall|AsyncPipelines|BvhLoopCapTrip|ShaderReplay|CsPretranslate|AvTrace|LogAsync|GpuCheckpoint|Kernel(Read|Open))',x[1])]
    ts=[x for x in lines if re.match(rb'^\[\d+\]\[\d\d:\d\d:\d\d\.\d{3}\]',x[1])]
    print('n',n,'dt_us',dt,'lines',len(lines),'translations(spirv)',len(spirv),'decode hashes',dict(hashes),'sum elapsed_ms',el)
    print('  ts first/last', ts[0][1][:28] if ts else None, ts[-1][1][:28] if ts else None)
    for x in keys[:30]: print('  ',x[0],x[1][:200].decode('utf-8','replace').rstrip())

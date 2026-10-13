import sys, re, collections
keys=[b'AudioOut2ContextCreate',b'AudioOut2ContextDestroy',b'AudioOut: opened SDL device',b'AudioOut: vibration port',b'AudioOut2PortCreate',b'libAudioOut::AudioOutOpen',b'AudioStat:',b'FixF8',b'WASAPI',b'SDL_OpenAudioDevice failed',b'queue_depth = ',b'audio_handle  = ',b'port_type     = ']
for path in sys.argv[1:]:
    c=collections.Counter(); samples=collections.defaultdict(list); ports=collections.Counter()
    with open(path,'rb') as f:
        for line in f:
            for k in keys:
                if k in line:
                    c[k]+=1
                    if len(samples[k])<6: samples[k].append(line.strip()[:200])
                    if k==b'AudioStat:':
                        m=re.search(rb'port=(\d+)',line); ports[m.group(1)]+=1
                    if k in (b'audio_handle  = ',b'port_type     = '):
                        ports[k+line.strip()[-12:]]+=1
    print('==',path)
    for k in keys: print(k.decode(), c[k])
    for k,v in samples.items():
        print('--',k.decode()); [print('   ',s.decode('utf-8','replace')) for s in v]
    print('ports',dict(ports))

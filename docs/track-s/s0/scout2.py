# scout2.py - full sample lines of the marker families used by the attribution (S0, HPP-294)
import re, sys, collections
path = sys.argv[1]
keys = [b'AsyncPipelines:', b'PipelineTrace:', b'FlipHold:', b'PriorityStall:', b'MainTaskLate:', b'ShaderCache', b'ShaderSeed',
        b'ShaderPreparation', b'PipelinePrecache', b'CsPretranslate: summary', b'CsPretranslate: hit', b'CsPretranslate: miss',
        b'CsPretranslate: skipped', b'AsyncCompute:', b'held', b'AvTrace', b'ShaderRegister', b'ShaderFirstUse', b'PipelineCache',
        b'Level has started', b'KYTY_', b'Shader:', b'recipes', b'salt', b'FrameTrace: n=300 ', b'FrameTrace-draw: n=300 ',
        b'FrameTrace-x: n=300 ', b'FrameTrace-rp: n=300 ', b'GateArm', b'Gates', b'gates']
cnt = collections.Counter(); samp = collections.defaultdict(list); sub = collections.Counter()
rxsub = re.compile(rb'(AsyncPipelines|PipelineTrace|AsyncCompute|CsPretranslate|PipelinePrecache|ShaderPreparation): ([A-Za-z_ ]{1,30})')
n = 0
with open(path, 'rb') as f:
    for line in f:
        n += 1
        for k in keys:
            if k in line:
                cnt[k] += 1
                if cnt[k] <= 3:
                    samp[k].append((n, line.rstrip()[:2600]))
        m = rxsub.search(line)
        if m:
            sub[(m.group(1), m.group(2).strip())] += 1
for k in keys:
    print('==', k.decode(), cnt[k])
    for ln, s in samp[k]:
        print('   ', ln, s.decode('latin1'))
print('== subkinds')
for (a, b), c in sorted(sub.items()):
    print('   ', a.decode(), '|', b.decode(), c)

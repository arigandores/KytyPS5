# F4b2: sites of Permutation creation / AdoptDmaLayout / AdoptSpirvView / CreatePipelineInternal calls in main and in the F4c build tree
import re,sys
trees={'main':'C:/kyty/KytyPS5','wt':'C:/kyty/f287/f4a2/wt'}
pats=[r'permutations\.push_back',r'permutations\.emplace_back',r'AdoptDmaLayout\(',r'AdoptSpirvView\(',r'CreatePipelineInternal\(',r'handle\.spirv',r'\.spirv\s*=',r'Permutation\{',r'Permutation\s+\w+\s*[{(=]']
for name,root in trees.items():
    for f in ['src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp','src/graphics/host_gpu/renderer/pipeline/shaders.cpp','src/graphics/host_gpu/renderer/pipeline/pipelineCache.h']:
        L=open(root+'/'+f,'rb').read().decode('utf-8','replace').replace('\r','').split('\n')
        for p in pats:
            for i,l in enumerate(L):
                if re.search(p,l):
                    print(name,f.split('/')[-1],i+1,p,'|',l.strip()[:110])

import json, hashlib, re, os
R='C:/kyty/s110/'
seals={'01':'e20551068e7cd70e20141980f58bde06e03445316992a6c26421916a1e42c11f','02':'0299b403a1744560199b046f4ed6d53df1108089f52b3d687c64d90d043cc198','03':'4f02d2848cbcd87202a9dbb525fbef8adf8f315610be21a39e008d67b3a66103'}
for f,s in (('pred/01_stl110.md','01'),('pred/02_stl110b.md','02'),('pred/03_shp110.md','03')):
    h=hashlib.sha256(open(R+f,'rb').read()).hexdigest(); print(f, h==seals[s])
tags=['stl110_%d'%i for i in range(1,9)]+['stl110b_%d'%i for i in range(1,9)]+['shp110','vsh110','vid110']
exp={'stl110':'01','stl110b':'02','shp110':'03','vsh110':'03','vid110':None}
suspicious=('cmake','ninja','clang','lld','cl.exe','msbuild','python','kyty','qrenderdoc','ffmpeg','nvcc','git','bash','steam','chrome','firefox','obs','game')
for t in tags:
    m=json.load(open(R+t+'.json'))
    base=t.split('_')[0]
    pr=m.get('prereg') or {}
    want=exp[base]
    ok_pre = (pr.get('sha256')==seals[want]) if want else (pr=={} or pr is None)
    env=m.get('env',{})
    log=open(R+'log_%s.txt'%t,'rb').read()
    pins=re.findall(rb'GpuClockPin: mode (\d+)',log)
    so=open(R+'stdout_%s.txt'%t,'rb').read()
    pre=m.get('pre_run',{})
    top=[x['name'] for x in pre.get('host',{}).get('top',[])]
    gpu=[os.path.basename(x['name']) for x in pre.get('gpu_apps',[])]
    susp=[x for x in top+gpu if any(s in x.lower() for s in suspicious)]
    pc=re.findall(rb'PipelinePrecache: [^\r\n]*',log)[:1]
    gt=(m.get('gates') or '')
    arm=re.findall(r'cspfree=\d',gt)
    print(t, 'bin',m.get('binary_sha256','')[:8],'prereg_ok',ok_pre,'pin_env',env.get('KYTY_GPU_CLOCK_PIN'),'pins',pins,'precache',env.get('KYTY_PIPELINE_PRECACHE'),pc[0][:90] if pc else None,'arm',arm,'ckpt' , 'KYTY_GPU_CHECKPOINTS' in env,'launched',m.get('launched'),'fin',m.get('finished'),'gpu_util',pre.get('gpu_util_median'),'susp',susp,'hold',[a.get('hold_s') for a in m.get('attempts',[])])

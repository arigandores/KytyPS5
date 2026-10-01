# F4b (Red Team): own recount of KYTY_SHADER_SOURCE_HASH (src/generate_version.cmake) from git blobs and working tree
import hashlib, subprocess, sys, os
REPO='C:/kyty/KytyPS5'
EXTRA=['src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp','src/graphics/guest_gpu/gpu_format.h','src/graphics/guest_gpu/gpu_defs.h']
def files_at(rev):
    out=subprocess.run(['git','-C',REPO,'ls-tree','-r','--name-only',rev,'src/graphics/shader'],capture_output=True,check=True).stdout.decode().split('\n')
    fs=[f for f in out if f and os.path.splitext(f)[1] in ('.cpp','.h','.inc')]
    return sorted(fs+EXTRA)
def blob(rev,f):
    return subprocess.run(['git','-C',REPO,'show',rev+':'+f],capture_output=True,check=True).stdout
for rev in sys.argv[1:]:
    fs=files_at(rev)
    d=''.join(hashlib.sha1(blob(rev,f)).hexdigest()+'\n' for f in fs)
    print(rev,'blob',hashlib.sha1(d.encode()).hexdigest(),len(fs))
fs=files_at('HEAD')
d=''.join(hashlib.sha1(open(REPO+'/'+f,'rb').read()).hexdigest()+'\n' for f in fs)
print('worktree',hashlib.sha1(d.encode()).hexdigest(),len(fs))

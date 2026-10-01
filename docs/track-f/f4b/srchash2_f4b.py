# F4b (Red Team): worktree-form (CRLF via git attributes/autocrlf as checked out) recount of KYTY_SHADER_SOURCE_HASH
# Model: worktree bytes = blob with LF -> CRLF; checked against HEAD worktree (846a041a), then applied to 4fc501f4 (9235a7ac: 699c1e4b)
import hashlib, subprocess, sys, os, re
REPO='C:/kyty/KytyPS5'
EXTRA=['src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp','src/graphics/guest_gpu/gpu_format.h','src/graphics/guest_gpu/gpu_defs.h']
def files_at(rev):
    out=subprocess.run(['git','-C',REPO,'ls-tree','-r','--name-only',rev,'src/graphics/shader'],capture_output=True,check=True).stdout.decode().split('\n')
    return sorted([f for f in out if f and os.path.splitext(f)[1] in ('.cpp','.h','.inc')]+EXTRA)
def blob(rev,f): return subprocess.run(['git','-C',REPO,'show',rev+':'+f],capture_output=True,check=True).stdout
def crlf(x): return re.sub(rb'(?<!\r)\n',b'\r\n',x)
fs=files_at('HEAD'); same=0
for f in fs:
    if crlf(blob('HEAD',f))==open(REPO+'/'+f,'rb').read(): same+=1
print('HEAD files where worktree == crlf(blob):',same,'of',len(fs))
for rev in sys.argv[1:]:
    fs=files_at(rev)
    d=''.join(hashlib.sha1(crlf(blob(rev,f))).hexdigest()+'\n' for f in fs)
    print(rev,'crlf-model',hashlib.sha1(d.encode()).hexdigest())

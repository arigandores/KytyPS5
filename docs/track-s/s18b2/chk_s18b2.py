import subprocess, hashlib, sys
REPO = 'C:/kyty/KytyPS5'
WT = 'C:/kyty/s288/s18a/wt'
GIT = 'C:/Program Files/Git/cmd/git.exe'
ok = True

def git(*a, cwd=REPO, inp=None):
    return subprocess.run([GIT, *a], cwd=cwd, capture_output=True, input=inp, check=True).stdout

def pid(cwd, rev, paths=None):
    d = git('show', rev, *(['--'] + paths if paths else []), cwd=cwd)
    out = git('patch-id', '--stable', cwd=cwd, inp=d).decode().split()
    return out[0] if out else 'NONE'

wt_head = git('rev-parse', 'HEAD', cwd=WT).decode().strip()
print('wt HEAD', wt_head)
par = git('rev-parse', 'HEAD^', cwd=WT).decode().strip()
print('wt parent', par, 'OK' if par.startswith('62ff7b5b') else 'BAD')
ok &= par.startswith('62ff7b5b')
st = git('status', '--porcelain', cwd=WT).decode()
print('wt status lines', len(st.splitlines()))
ok &= st == ''
a = pid(REPO, '7c31481b'); b = pid(WT, wt_head)
print('patch-id main', a, 'wt', b, 'EQUAL' if a == b else 'DIFF')
ok &= a == b
files_main = git('show', '--name-only', '--format=', '7c31481b').decode().split()
files_wt = git('show', '--name-only', '--format=', wt_head, cwd=WT).decode().split()
print('files main', files_main)
print('files wt  ', files_wt, 'SAME' if files_main == files_wt else 'DIFF')
ok &= files_main == files_wt
# tree diff 62ff7b5b..HEAD only these 4 paths
ch = git('diff', '--name-only', '62ff7b5b', wt_head, cwd=WT).decode().split()
print('62ff7b5b..HEAD paths', ch, 'OK' if sorted(ch) == sorted(files_main) else 'BAD')
ok &= sorted(ch) == sorted(files_main)
K17 = ['src/graphics/shader', 'CMakeLists.txt', 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',
       'src/graphics/guest_gpu/gpu_format.h', 'src/graphics/guest_gpu/gpu_defs.h',
       'src/graphics/host_gpu/renderer/image/imageInfo.h', 'generate_version.cmake']
k = git('diff', '--stat', '302347b4', wt_head, '--', *K17, cwd=WT).decode()
print('K1(7) 302347b4..HEAD:', 'EMPTY' if k.strip() == '' else k)
ok &= k.strip() == ''
inter = set(files_main) & set(['src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',
       'src/graphics/guest_gpu/gpu_format.h', 'src/graphics/guest_gpu/gpu_defs.h',
       'src/graphics/host_gpu/renderer/image/imageInfo.h', 'CMakeLists.txt'])
inter |= {f for f in files_main if f.startswith('src/graphics/shader/')}
print('delta paths in signature set', sorted(inter) if inter else 'NONE')
ok &= not inter
# main vs wt on the 4 paths: only removed foreign lines
d = git('diff', '7c31481b', wt_head, '--', *files_main, cwd=WT).decode('utf-8', 'replace')
plus = [l for l in d.splitlines() if l.startswith('+') and not l.startswith('+++')]
minus = [l for l in d.splitlines() if l.startswith('-') and not l.startswith('---')]
print('main->wt on delta paths: +%d -%d' % (len(plus), len(minus)))
for l in minus: print('   ', l[:110])
ok &= len(plus) == 0
exe = 'C:/kyty/s288/bin/kyty_emulator_b3cee576.exe'
data = open(exe, 'rb').read()
sha = hashlib.sha256(data).hexdigest()
print('exe sha256', sha, 'OK' if sha.startswith('b3cee576') and sha.endswith('305a') else 'BAD')
ok &= sha.startswith('b3cee576')
h = b'9177b4267de1fb8bac7d1113afd8733210addfac'
print('sig hash count', data.count(h))
ok &= data.count(h) == 1
print('version g0005e11f count', data.count(b'1897-g0005e11f'), 'g62ff7b5b count', data.count(b'g62ff7b5b'))
ok &= data.count(b'g62ff7b5b') == 0
for s in [b'ShaderReplay: close stop requested', b'ShaderReplay: close stop joined', b'ShaderReplay: stand stop seen',
          b'ShaderReplay: stand stop applied', b'pipelines_bin=']:
    print('string', s.decode(), data.count(s))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)

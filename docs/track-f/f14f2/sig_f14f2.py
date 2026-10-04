# F14f2 (HPP-546): own repeat of p.443(v)(2) - KYTY_SHADER_SOURCE_HASH by src/generate_version.cmake,
# the same -D arguments as the KytyGitVersion target of CMakeLists.txt, base list (d5d0076a) vs F14e2 list (f98e842c).
import hashlib, re, subprocess, sys, os

WT = 'C:/kyty/f287/f14f2/wt'
OUT = 'C:/kyty/f287/f14f2/sig'
SRC = WT + '/src'
IMG = SRC + '/graphics/host_gpu/renderer/image/imageInfo.h'
BASE_EXTRA = [SRC + '/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',
              SRC + '/graphics/guest_gpu/gpu_format.h', SRC + '/graphics/guest_gpu/gpu_defs.h']
NEW_EXTRA = BASE_EXTRA + [IMG]
GIT = 'C:/Program Files/Git/cmd/git.exe'
CMAKE = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

def cmake_extra(lst, name):
    # the list as configured in CMakeLists: base has 3 entries, f98e842c line has imageInfo.h last
    cm = open(WT + '/CMakeLists.txt', encoding='utf-8').read()
    out = OUT + '/kytyGitVersion_' + name + '.h'
    r = subprocess.run([CMAKE, '-D', 'INPUT_FILE=' + SRC + '/kytyGitVersion.h.in', '-D', 'OUTPUT_FILE=' + out,
                        '-D', 'GIT_EXECUTABLE=' + GIT, '-D', 'GIT_WORKING_DIRECTORY=' + WT,
                        '-D', 'SHADER_SOURCE_DIR=' + SRC + '/graphics/shader',
                        '-D', 'SHADER_CACHE_EXTRA_FILES=' + ';'.join(lst), '-P', SRC + '/generate_version.cmake'],
                       capture_output=True, text=True)
    t = open(out, encoding='utf-8').read()
    m = re.search(r'KYTY_SHADER_SOURCE_HASH\s+"?([0-9a-f]+)', t)
    return r.returncode, m.group(1) if m else None

# guard: the extra list of the worktree CMakeLists.txt is exactly NEW_EXTRA in KYTY_SOURCE_DIR form
cm = open(WT + '/CMakeLists.txt', encoding='utf-8').read()
line = [l for l in cm.split('\n') if 'SHADER_CACHE_EXTRA_FILES=' in l][0].strip()
lst = line.split('=', 1)[1].split('$<SEMICOLON>')
lst = [x.replace('${KYTY_SOURCE_DIR}', SRC) for x in lst]
print('cmake_list_eq_new', lst == NEW_EXTRA)

raw = open(IMG, 'rb').read()
sha_raw = hashlib.sha256(raw).hexdigest()
res = {}
res['base_clean'] = cmake_extra(BASE_EXTRA, 'base_clean')
res['new_clean'] = cmake_extra(NEW_EXTRA, 'new_clean')
edited = raw.replace(b'struct DepthFormatPolicy {', b'// F14f2 positive control comment\nstruct DepthFormatPolicy {', 1)
assert edited != raw
open(IMG, 'wb').write(edited)
try:
    res['base_edit'] = cmake_extra(BASE_EXTRA, 'base_edit')
    res['new_edit'] = cmake_extra(NEW_EXTRA, 'new_edit')
finally:
    open(IMG, 'wb').write(raw)
res['new_revert'] = cmake_extra(NEW_EXTRA, 'new_revert')
print('imageInfo_restored', hashlib.sha256(open(IMG, 'rb').read()).hexdigest() == sha_raw)
st = subprocess.run([GIT, '-C', WT, 'status', '--porcelain'], capture_output=True, text=True).stdout
print('git_status_lines', len([l for l in st.split('\n') if l.strip()]))
for k, v in res.items():
    print(k, 'rc', v[0], 'hash', v[1])
ok = True
ok &= res['base_clean'][1] == res['base_edit'][1]          # RC1 reproduced on base list
ok &= res['new_clean'][1] != res['base_clean'][1]          # signature changes by the commit
ok &= res['new_edit'][1] != res['new_clean'][1]            # positive control
ok &= res['new_revert'][1] == res['new_clean'][1]          # revert returns
ok &= lst == NEW_EXTRA
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)

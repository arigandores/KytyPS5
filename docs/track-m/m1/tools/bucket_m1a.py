"""M1a: propose an area bucket per upstream commit (by paths and subject); output buckets/<area>.tsv for the worker agents."""
import json, os, re, collections
D = 'C:/kyty/m657/m1a/'
C = json.load(open(D + 'commits.json', encoding='utf-8'))
def area(v):
    s = v['subject'].lower()
    fs = [f for f in v['files']]
    src = [f for f in fs if f.startswith('src/') or f == 'CMakeLists.txt']
    nontest = [f for f in fs if not f.startswith('tests/')]
    if any(f.startswith('src/launcher') for f in fs) and all(f.startswith(('src/launcher', 'README', 'docs', 'CMakeLists', '.github', 'src/main.cpp', 'src/common/emulatorConfig')) or f.startswith('src/launcher') for f in nontest):
        return 'g_launcher'
    if nontest and all(f.startswith(('.github', 'README', 'docs/', 'nix', 'flake', '.coderabbit', '.vscode', 'cmake', '3rdparty', 'CMakeLists.txt', 'scripts', '.clang', 'CONTRIBUTING', '.gitignore', 'pr', 'LICENSE')) or f.endswith('.md') for f in nontest):
        return 'g_build_docs'
    if not nontest:
        return 'tests_only'
    sh = [f for f in src if f.startswith('src/graphics/shader/')]
    if sh and len(sh) * 2 >= len(src):
        if any('/backend/' in f for f in sh) and not any('/frontend/decode' in f or '/translate/' in f for f in sh):
            return 'sh_backend'
        if any('/passes/' in f or '/ir/' in f for f in sh) and not any('/decode/' in f for f in sh):
            return 'sh_ir'
        return 'sh_decode'
    gp = [f for f in src if f.startswith('src/graphics/')]
    if gp and len(gp) * 2 >= len(src):
        if any(k in f for f in gp for k in ('image', 'texture', 'tiler', 'tiling', 'Tile', 'gpu_format')):
            return 'gfx_image'
        if any(f.startswith('src/graphics/presentation') for f in gp):
            return 'gfx_present'
        return 'gfx_render'
    if any(k in f for f in src for k in ('audio', 'Audio', 'ngs2', 'Ngs2', 'ajm', 'Ajm', 'avPlayer', 'AvPlayer', 'controller', 'Controller', 'haptic', 'Haptic', 'pad', 'Pad', 'input', 'Input')):
        return 'av_input'
    if any(k in f for f in src for k in ('libNet', 'network', 'Net', 'np', 'Np', 'Http', 'http', 'trophy', 'Trophy', 'font', 'Font', 'Png', 'Ces', 'shareplay', 'netctl')):
        return 'hle_misc'
    return 'sys_kernel'
B = collections.defaultdict(list)
for h, v in C.items():
    B[area(v)].append(h)
os.makedirs(D + 'buckets', exist_ok=True)
for a, hs in sorted(B.items()):
    with open(D + 'buckets/' + a + '.tsv', 'w', encoding='utf-8', newline='\n') as f:
        for h in hs:
            v = C[h]
            f.write('%s\t%s\t%s\t%s\n' % (h, v['date'], v['subject'], ' '.join(v['files'])))
    print(len(hs), a)

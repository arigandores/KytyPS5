"""Red Team M6b2 (HPP-855): own recount of the pure functions of M6a2 on the COMPILED source text.
Extracts MinLodDiverges, MinLodDivergesExact, ClearDwordDiverges8 verbatim from <wt>/src/libs/diagM5W2.cpp,
compiles them with clang-cl (vcvars) together with a driver, runs it and compares with independent models:
  T021: M5a grid (B 0..3, count 2..5, M = 64..256*(B+count-1) step 64 - minlod_model_m5a.py) and an extended grid
        (B 0..7, count 1..8, M 1..4095 every 4.8 value); model hw = min(max(B, m), B+count-1),
        ours = max(B, min(m, count-1)) (imageView.cpp clamp), divergence = hw != ours.
  (a3): every 32-bit word for vk 9 (R8Unorm) and 16 (R8G8Unorm): model R8 - four bytes not all equal,
        R8G8 - the two 16-bit texels differ; 0 for every other vk::Format 0..255 on a word sample.
Usage: pure_m6b2.py <wt> <work dir>. Last line ALL OK or FAIL.
"""
import os
import re
import subprocess
import sys

wt, work = sys.argv[1], sys.argv[2]
os.makedirs(work, exist_ok=True)
src = open(wt + '/src/libs/diagM5W2.cpp', 'rb').read().decode('utf-8').replace('\r', '')


def extract(name):
    m = re.search(r'^bool ' + name + r'\(', src, re.M)
    assert m, name
    i = src.index('{', m.start())
    depth = 0
    for j in range(i, len(src)):
        if src[j] == '{':
            depth += 1
        elif src[j] == '}':
            depth -= 1
            if depth == 0:
                return src[m.start():j + 1]
    raise SystemExit('no end ' + name)


funcs = [extract(n) for n in ('MinLodDiverges', 'MinLodDivergesExact', 'ClearDwordDiverges8')]
NL = chr(10)
cpp = NL.join([
    '#include <algorithm>', '#include <cstdint>', '#include <cstdio>', '#include <vulkan/vulkan.hpp>',
    'namespace { ' + NL + NL.join(funcs) + NL + '}',
    'int main(int argc, char** argv) {',
    '  if (argc > 1 && argv[1][0] == 109) {',  # 'm': minlod grid lines "B count M div x"
    '    for (uint32_t B = 0; B < 8; B++) for (uint32_t c = 1; c < 9; c++) for (uint32_t M = 1; M < 4096; M++)',
    '      std::printf("%u %u %u %d %d" "\\n", B, c, M, (int)MinLodDiverges(M, B, c), (int)MinLodDivergesExact(M, B, c));',
    '    return 0;',
    '  }',
    '  unsigned long long r8 = 0, rg8 = 0, bad = 0;',
    '  for (uint64_t w64 = 0; w64 <= 0xffffffffull; w64++) {',
    '    const uint32_t w = (uint32_t)w64;',
    '    const uint32_t b0 = w & 0xff, b1 = (w >> 8) & 0xff, b2 = (w >> 16) & 0xff, b3 = w >> 24;',
    '    const bool m8 = !(b0 == b1 && b1 == b2 && b2 == b3);',
    '    const bool m16 = (w & 0xffff) != (w >> 16);',
    '    const bool c8 = ClearDwordDiverges8(9, w), c16 = ClearDwordDiverges8(16, w);',
    '    r8 += c8; rg8 += c16; bad += (c8 != m8) + (c16 != m16);',
    '  }',
    '  unsigned long long other = 0;',
    '  const uint32_t ws[] = {0u, 1u, 0xffu, 0x00ff00ffu, 0x12345678u, 0xffffffffu, 0x7f7f7f7fu, 0x00001234u};',
    '  for (uint32_t f = 0; f < 256; f++) { if (f == 9 || f == 16) continue; for (uint32_t w: ws) other += ClearDwordDiverges8(f, w); }',
    '  std::printf("clr8 r8_div=%llu rg8_div=%llu model_mismatch=%llu other_formats_true=%llu" "\\n", r8, rg8, bad, other);',
    '  std::printf("vk eR8Unorm=%d eR8G8Unorm=%d" "\\n", (int)vk::Format::eR8Unorm, (int)vk::Format::eR8G8Unorm);',
    '  return 0;',
    '}', ''])
open(work + '/pure_m6b2.cpp', 'wb').write(cpp.encode('utf-8'))
inc = wt.replace('/', chr(92)) + chr(92) + '3rdparty' + chr(92) + 'Vulkan-Headers' + chr(92) + 'include'
cmd = work.replace('/', chr(92)) + chr(92) + 'build_pure.cmd'
open(cmd, 'wb').write((NL.join([
    '@echo off',
    'call "C:' + chr(92) + 'Program Files (x86)' + chr(92) + 'Microsoft Visual Studio' + chr(92) + '2022' + chr(92) + 'BuildTools' + chr(92) + 'VC' + chr(92) + 'Auxiliary' + chr(92) + 'Build' + chr(92) + 'vcvars64.bat" >nul || exit /b 1',
    'clang-cl /nologo /O2 /std:c++20 /EHsc /I"' + inc + '" "' + work.replace('/', chr(92)) + chr(92) + 'pure_m6b2.cpp" /Fe"' + work.replace('/', chr(92)) + chr(92) + 'pure_m6b2.exe" /Fo"' + work.replace('/', chr(92)) + chr(92) + 'pure_m6b2.obj" || exit /b 1',
    '']) ).encode('ascii'))
r = subprocess.run(['cmd', '/c', cmd], capture_output=True)
if r.returncode != 0:
    print(r.stdout.decode('utf-8', 'replace'), r.stderr.decode('utf-8', 'replace'))
    print('FAIL build')
    sys.exit(1)
exe = work + '/pure_m6b2.exe'
fails = []
# T021
rows = subprocess.run([exe, 'm'], capture_output=True).stdout.decode().split()
vals = [int(x) for x in rows]
grid = {}
for k in range(0, len(vals), 5):
    B, c, M, d, x = vals[k:k + 5]
    grid[(B, c, M)] = (d, x)


def model(B, c, M):
    m = M / 256.0
    hw = min(max(B, m), B + c - 1.0)
    ours = max(B, min(m, c - 1.0))
    return abs(hw - ours) > 1e-9


# M5a grid (the grid of minlod_model_m5a.py / m6b minlod_rc.py)
f_old = f_x = div = x_not_div = div_not_x = 0
for B in range(0, 4):
    for c in range(2, 6):
        for M4 in range(1, 4 * (B + c - 1) + 1):
            M = M4 * 64
            d_old, x = grid[(B, c, M)]
            dv = model(B, c, M)
            f_old += d_old
            f_x += x
            div += dv
            x_not_div += (x and not dv)
            div_not_x += (dv and not x)
print('T021 M5a grid: minlod_div field %d, minlod_div_x field %d, divergence %d, x_without_divergence %d, divergence_outside_x %d'
      % (f_old, f_x, div, x_not_div, div_not_x))
if not (f_old == 96 and f_x == 80 and div == 80 and x_not_div == 0 and div_not_x == 0):
    fails.append('M5a grid')
# extended grid
ext = {}
for (B, c, M), (d_old, x) in grid.items():
    dv = model(B, c, M)
    if x != dv:
        key = 'x_without_divergence' if x else 'divergence_outside_x'
        cls = 'count=1' if c == 1 else ('B=0' if B == 0 else 'other')
        ext.setdefault((key, cls), []).append((B, c, M))
print('T021 extended grid (B 0..7, count 1..8, M 1..4095): cells %d' % len(grid))
for k in sorted(ext):
    print('  %s %s: %d, first %s' % (k[0], k[1], len(ext[k]), ext[k][:3]))
if any(k[1] != 'count=1' for k in ext):
    fails.append('extended grid: mismatch outside count=1')
out = subprocess.run([exe], capture_output=True).stdout.decode()
print(out.strip())
m = re.search(r'r8_div=(\d+) rg8_div=(\d+) model_mismatch=(\d+) other_formats_true=(\d+)', out)
if not m or m.group(3) != '0' or m.group(4) != '0' or int(m.group(1)) != 2 ** 32 - 256 or int(m.group(2)) != 2 ** 32 - 2 ** 16:
    fails.append('clr_dw_div8')
if 'eR8Unorm=9 eR8G8Unorm=16' not in out:
    fails.append('vk values')
print('ALL OK' if not fails else 'FAIL ' + '; '.join(fails))

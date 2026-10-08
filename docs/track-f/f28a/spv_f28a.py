"""F28a (HPP-698, ROADMAP s122 item 638(v)(1)): SPIR-V of 380bb9d636390bae translated offline by the
KYTY_RECOMPILE path of shader_cfg_tests at the KYTY_BVH_LOOP_CAP default and at KYTY_BVH_LOOP_CAP=0,
with the installed FS10 translation-cache file (variant _fixf19) as the specialization source.

Configurations (all other KYTY_* removed; KYTY_FIX_F10=1 = FS10 default, the test exe default is 0):
  def    KYTY_BVH_LOOP_CAP unset           (default: cap 65536 on 380bb9d6)
  c65536 KYTY_BVH_LOOP_CAP=65536           (explicit default; must equal def)
  c0     KYTY_BVH_LOOP_CAP=0               (cap off)
  c1024  KYTY_BVH_LOOP_CAP=1024            (control: the knob reaches the emitter; differs from def
                                            only in the two budget constants)
  ll     KYTY_BVH_LOOP_CAP=0, KYTY_LOOP_LIMIT=65536 (control of the other guard path; reference only)
Members:
  M1 every process rc 0 and out.spv written;
  M2 positive control: def prints identical=1 against the stored SPIR-V of the FS10 cache file for every
     permutation (the test exe reproduces the installed translation of this program byte for byte);
  M3 c65536 == def byte for byte; M4 c0 != def; M5 c1024 != def and c1024 != c0;
  M6 spirv-val (vulkan1.3) rc 0 on def and c0.
Disassembly (spirv-dis --raw-id) of every output is kept for the line diff (diff_f28a.py).
Usage: python spv_f28a.py <test exe> <out dir>. Rule 27: lock and STOP checked before every process.
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
GCN = 'C:/kyty/s288/s4/gcn/g_1/cs_380bb9d636390bae.bin'
GCN_SHA = '4b2dda14411c7773df74d12eae9d148705179223643c5181864f86b8f86145c7'
CACHE = 'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10_fixf19/cs_380bb9d636390bae_fe70c334a8301128.bin'
DIS = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-dis.exe'
VAL = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-val.exe'
CONFIGS = [('def', {}), ('c65536', {'KYTY_BVH_LOOP_CAP': '65536'}), ('c0', {'KYTY_BVH_LOOP_CAP': '0'}),
           ('c1024', {'KYTY_BVH_LOOP_CAP': '1024'}),
           ('ll', {'KYTY_BVH_LOOP_CAP': '0', 'KYTY_LOOP_LIMIT': '65536'})]


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def halt():
    if os.path.exists(LOCK):
        print('HALT LOCK')
        sys.exit(5)
    if os.path.exists(STOP):
        print('HALT STOP')
        sys.exit(4)


def main():
    exe, out = sys.argv[1], sys.argv[2]
    halt()
    os.makedirs(out, exist_ok=True)
    assert sha(GCN) == GCN_SHA, 'GCN sha'
    cache = out + '/cache_fs10_380b.bin'
    shutil.copyfile(CACHE, cache)
    print('exe', exe, sha(exe))
    print('gcn', GCN, GCN_SHA)
    print('cache (copy of installed FS10 _fixf19 file)', CACHE, sha(CACHE), '; copy', sha(cache))
    ok = True
    res = {}
    for perm in range(8):
        for name, extra in CONFIGS:
            halt()
            work = '%s/p%d_%s' % (out, perm, name)
            os.makedirs(work, exist_ok=True)
            spv = work + '/out.spv'
            if os.path.exists(spv):
                os.remove(spv)
            env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
            env['KYTY_RECOMPILE'] = '%s;%s;%s;%d' % (GCN, cache, spv, perm)
            env['KYTY_FIX_F10'] = '1'
            env.update(extra)
            p = subprocess.run([exe], cwd=work, env=env, capture_output=True, timeout=300)
            open(work + '/stdout.txt', 'wb').write(p.stdout)
            open(work + '/stderr.txt', 'wb').write(p.stderr)
            both = p.stdout + p.stderr
            if b'permutation %d of' % perm in both:
                break
            m = re.search(rb'identical=(\d)', both)
            ident = m.group(1).decode() if m else '-'
            s = sha(spv) if p.returncode == 0 and os.path.exists(spv) else None
            res[(perm, name)] = (p.returncode, s, ident)
            if s:
                d = subprocess.run([DIS, '--raw-id', '--no-color', spv, '-o', work + '/out.dis'], capture_output=True)
                v = subprocess.run([VAL, '--target-env', 'vulkan1.3', spv], capture_output=True)
                open(work + '/val.txt', 'wb').write(v.stdout + v.stderr)
                res[(perm, name)] += (d.returncode, v.returncode, os.path.getsize(spv))
            print('perm', perm, name, 'rc', p.returncode, 'identical', ident, 'sha', s, res[(perm, name)][3:])
        else:
            continue
        break
    perms = sorted({k[0] for k in res})
    print('permutations', len(perms))
    m1 = all(v[0] == 0 and v[1] for v in res.values())
    print('M1 rc 0 and out.spv', m1)
    m2 = all(res[(p, 'def')][2] == '1' for p in perms)
    print('M2 def identical=1 vs FS10 cache, every permutation', m2)
    m3 = all(res[(p, 'c65536')][1] == res[(p, 'def')][1] for p in perms)
    print('M3 c65536 == def', m3)
    m4 = all(res[(p, 'c0')][1] != res[(p, 'def')][1] for p in perms)
    print('M4 c0 != def', m4)
    m5 = all(res[(p, 'c1024')][1] not in (res[(p, 'def')][1], res[(p, 'c0')][1]) for p in perms)
    print('M5 c1024 != def, != c0', m5)
    m6 = all(res[(p, n)][4] == 0 for p in perms for n in ('def', 'c0'))
    print('M6 spirv-val vulkan1.3 rc 0 on def and c0', m6)
    for p in perms:
        print('  perm', p, 'c0 identical (stored = FS10 default):', res[(p, 'c0')][2],
              ' sizes def/c0', res[(p, 'def')][5], res[(p, 'c0')][5])
    ok = m1 and m2 and m3 and m4 and m5 and m6 and len(perms) > 0
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

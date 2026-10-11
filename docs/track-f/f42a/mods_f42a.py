"""F42a (HPP-779, ROADMAP s122 item 694(g)(3)): the replay modules of row F20 and their checks, offline.
  z  = the snapshot module (dumped from f12_rd_k03 at EID 128281 by rd_f42a.py RD_DUMP)
  a  = z through KYTY_TEST_F20FILE (Libs::Graphics::FixF20::RewriteFaultOr of the F42a shader_cfg_tests, bound 1)
  o' = the FS12 module of the same program and specialization (corpus row cs_380bb9d636390bae_fe70c334a8301128_0,
       KYTY_RECOMPILE of the F42a build = the FS12 translator)
  a' = o' rewritten (KYTY_RECOMPILE_F20 of the same row)
Checks: sha256 of each; a vs z and a' vs o' differ only by triples (corpus_f42a.diff_ok) and the count = the triples of
the base (11 for 380bb9d6...); spirv-val (vulkan1.3, --uniform-buffer-standard-layout) of all four; binding
compatibility - the set of (DescriptorSet, Binding) decorations of the variables of o' equals that of z (form of r1 F12g).
Extra (reference, not a member): every module of the _fixf19 catalog copy that carries fault_buffer (22) through
KYTY_TEST_F20FILE bound 1: rewritten = triples, diff_ok, spirv-val (covers the VS module the corpus harness does not run).
Usage: python mods_f42a.py <shader_cfg_tests exe>. Writes replay/mods_f42a.txt; ALL OK / FAIL."""
import os
import shutil
import struct
import subprocess
import sys

sys.path.insert(0, 'C:/kyty/f287/f42a')
import spvscan_f42a as sv  # noqa: E402
from corpus_f42a import diff_ok, sha256_file  # noqa: E402

D = 'C:/kyty/f287/f42a/replay'
ROW = 'C:/kyty/f287/f42a/corpus/rows/cs_380bb9d636390bae_fe70c334a8301128_0'
SPIRV_VAL = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-val.exe'
LOCK = 'C:/kyty/SEALED_RUN.lock'


def f20file(exe, src, dst, bound):
    if os.path.exists(LOCK):
        raise SystemExit('LOCK')
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env['KYTY_TEST_F20FILE'] = '%s;%s;%d' % (src, dst, bound)
    p = subprocess.run([exe], env=env, capture_output=True)
    return p.returncode, p.stdout.decode('ascii', 'replace').strip()


def val(path):
    p = subprocess.run([SPIRV_VAL, '--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout', path],
                       capture_output=True)
    return p.returncode


def bindings(words):
    dec = {}
    for i, op, c in sv.walk(words):
        if op == sv.OP_DECORATE and c >= 4 and words[i + 2] in (33, 34):  # Binding, DescriptorSet
            dec.setdefault(words[i + 1], {})[words[i + 2]] = words[i + 3]
    return sorted((d.get(34, -1), d.get(33, -1)) for d in dec.values())


def main():
    exe = sys.argv[1]
    lines = []
    ok = True
    z = D + '/mod_z.spv'
    shutil.copyfile(D + '/snap_380_k03.spv', z)
    a = D + '/mod_a.spv'
    rc, line = f20file(exe, z, a, 1)
    lines.append('a: rc %d %s' % (rc, line))
    ok &= rc == 0
    op_, ap_ = D + '/mod_op.spv', D + '/mod_ap.spv'
    shutil.copyfile(ROW + '/out.spv', op_)
    shutil.copyfile(ROW + '/f20.spv', ap_)
    for name, path in (('z', z), ('a', a), ("o'", op_), ("a'", ap_)):
        lines.append('module %-2s sha256 %s words %d spirv-val rc %d' % (name, sha256_file(path),
                                                                       os.path.getsize(path) // 4, val(path)))
        ok &= val(path) == 0
    for base, new, name in ((z, a, 'a vs z'), (op_, ap_, "a' vs o'")):
        bw, nw = sv.read_spv(base), sv.read_spv(new)
        good, replaced = diff_ok(bw, nw)
        tb = sv.scan(bw)['triples']
        lines.append('diff %s: only triples %s, replaced %d, triples of the base %d, triples after %d' % (
            name, good, replaced, tb, sv.scan(nw)['triples']))
        ok &= good and replaced == tb == 11 and sv.scan(nw)['triples'] == 0
    bz, bo = bindings(sv.read_spv(z)), bindings(sv.read_spv(op_))
    lines.append("bindings (set, binding) z %d o' %d equal %s" % (len(bz), len(bo), bz == bo))
    if bz != bo:
        lines.append('  only z: %s' % sorted(set(bz) - set(bo)))
        lines.append("  only o': %s" % sorted(set(bo) - set(bz)))
    ok &= bz == bo
    # reference: the 22 catalog modules with fault_buffer
    cat = 'C:/kyty/f287/f42a/cat_fixf19'
    ref = os.path.join(D, 'catmods')
    os.makedirs(ref, exist_ok=True)
    n = good_n = 0
    for fname in sorted(os.listdir(cat)):
        if fname == 'pipelines.bin':
            continue
        for k, m in enumerate(sv.modules_in_cache_file(open(os.path.join(cat, fname), 'rb').read())):
            if sv.scan(m)['named'] == 0:
                continue
            n += 1
            src = os.path.join(ref, '%s_%d.spv' % (fname[:-4], k))
            dst = os.path.join(ref, '%s_%d_f20.spv' % (fname[:-4], k))
            open(src, 'wb').write(struct.pack('<%dI' % len(m), *m))
            rc, line = f20file(exe, src, dst, 1)
            good, replaced = diff_ok(m, sv.read_spv(dst))
            tb = sv.scan(m)['triples']
            vr = val(dst)
            g = rc == 0 and good and replaced == tb and 'unmatched=0' in line and vr == 0
            good_n += g
            lines.append('  cat %s perm %d triples %d replaced %d diff_ok %s val %d %s' % (fname, k, tb, replaced, good,
                                                                                          vr, 'ok' if g else 'BAD'))
    lines.append('catalog modules with fault_buffer %d, rewritten cleanly %d (reference)' % (n, good_n))
    lines.append('ALL OK' if ok else 'FAIL')
    text = '\n'.join(lines) + '\n'
    open(D + '/mods_f42a.txt', 'w', encoding='ascii', newline='\n').write(text)
    sys.stdout.write(text)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

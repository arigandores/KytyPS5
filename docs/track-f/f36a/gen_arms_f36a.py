"""F36a (HPP-758, ROADMAP s122 item 687(e)(0)(v), (e)(2)): SPIR-V of the arms of be4c35a2031fd3f4 on the FS11 translation.
def  = spv/fs11_p0.spv (= cache file of _fixf19 = offline translation by ee9632be code, work/rc3b);
mask = reference (a) of RC1 F23d, mem = reference (b) - refs_f23f.rewrite (F23f rewriter, unchanged) at the three FS11 sites of
       align_f36a.json; sens = the two value operands of each site swapped (gen_arms_f23f.swap_sites form);
the counter module (diag) is built at replay time (storage chosen per event, rd_f36a.py).
Checks: spirv-val (vulkan1.3, standard layout) rc 0; mask / mem - no OpSelect left at the sites, OpPhi not added; sens - sites
still OpSelect with swapped operands. Output: arms/ps_be4c35a2031fd3f4_<arm>.spv, arms_f36a.json, arms_f36a.out.txt."""
import hashlib
import json
import os
import struct
import subprocess
import sys

sys.path.insert(0, 'C:/kyty/f287/f23f')
import refs_f23f as R  # noqa: E402

D = 'C:/kyty/f287/f36a/'
A = D + 'arms/'
VAL = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-val.exe'
NL = chr(10)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def swap_sites(data, sites):
    w = R.words_of(data)
    want = {s[0]: s for s in sites}
    i, n = 5, 0
    while i < len(w):
        cnt, op = w[i] >> 16, w[i] & 0xffff
        if op == 169 and w[i + 2] in want:
            sid, cid, nid, oid = want[w[i + 2]]
            assert (w[i + 3], w[i + 4], w[i + 5]) == (cid, nid, oid)
            w[i + 4], w[i + 5] = oid, nid
            n += 1
        i += cnt
    assert n == len(sites)
    return struct.pack('<%dI' % len(w), *w)


def count(data, op):
    return sum(1 for x in R.instrs(R.words_of(data)) if x[0] & 0xffff == op)


def main():
    os.makedirs(A, exist_ok=True)
    al = json.load(open(D + 'align_f36a.json'))
    sites = [(s['fs11']['sid'], s['fs11']['cid'], s['fs11']['nid'], s['fs11']['oid']) for s in al['sites']]
    sids = [s[0] for s in sites]
    base = open(D + 'spv/fs11_p0.spv', 'rb').read()
    assert sha(base).startswith('71ebbdda693a7e51')
    arms = {'def': base}
    arms['mask'], n1 = R.rewrite(base, sites, 'mask')
    arms['mem'], n2 = R.rewrite(base, sites, 'mem')
    arms['sens'] = swap_sites(base, sites)
    assert n1 == n2 == 3
    res = {'sites': sites, 'files': {}}
    out = ['sites (sid, cid, nid, oid) %s' % sites]
    ok = True
    for k, b in arms.items():
        p = A + 'ps_be4c35a2031fd3f4_%s.spv' % k
        open(p, 'wb').write(b)
        r = subprocess.run([VAL, '--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout', p], capture_output=True, text=True)
        left = R.selects_at(b, sids)
        phi = count(b, 245) - count(base, 245)
        sel = count(b, 169) - count(base, 169)
        good = r.returncode == 0 and (len(left) == 3 if k in ('def', 'sens') else (not left and phi == 0 and sel == -3))
        ok &= good
        res['files'][k] = {'sha': sha(b), 'bytes': len(b), 'val_rc': r.returncode, 'sites_left': len(left), 'phi_added': phi,
                           'select_delta': sel, 'ok': good}
        out.append('%s sha256 %s bytes %d spirv-val rc %d %s | OpSelect at sites %d, OpSelect %+d, OpPhi %+d | %s' % (
            k, sha(b), len(b), r.returncode, (r.stdout + r.stderr).strip()[:200], len(left), sel, phi, 'OK' if good else 'FAIL'))
    out.append('ALL OK' if ok else 'FAILED')
    json.dump(res, open(D + 'arms_f36a.json', 'w'), indent=1, sort_keys=True)
    open(D + 'arms_f36a.out.txt', 'w', newline=NL).write(NL.join(out) + NL)
    print(NL.join(out))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

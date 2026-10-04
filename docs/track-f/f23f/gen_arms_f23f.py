"""F23f (HPP-592, ROADMAP s122 item 498(g)(3)): the SPIR-V of every arm for the 17 programs, offline, with spirv-val.
  def   - the S12 module (s12spv/, = installed translation, sel_f23f.status.jsonl);
  mask  - reference (a) of refs_f23f.py on every form-A site (sites_f23f.json);
  mem   - reference (b);
  blend - the bit blend of F23c (phi_f23c.blend, select -> old ^ ((new ^ old) & select(c, ~0, 0))) - reference only (item 498(zh)(1));
  sens  - sensitivity control (as F23c section 2.4): the two value operands of every form-A select swapped;
  diagT - a validation sample of the RC4 diagnostic module (the replay builds its own with the real counter offset): counters
          in 'fault_buffer' (struct{uint[]}, prefix (0,)) when the module has one, else in 'buffers' (array of struct{uint[]},
          prefix (0, 0)).
Checks: spirv-val --target-env vulkan1.3 --uniform-buffer-standard-layout rc 0 for every file (the def module too); no OpSelect left
at the sites in mask / mem / blend; OpPhi count unchanged. Output: arms/<stage>_<hash>_{def,mask,mem,blend,diagT}.spv, arms_f23f.out.txt,
arms_f23f.json (sha256 of every file, the diag variable id and prefix)."""
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, 'C:/kyty/f287/f23f')
sys.path.insert(0, 'C:/kyty/f287/f23c')
import refs_f23f as R  # noqa: E402
import phi_f23c  # noqa: E402

D = 'C:/kyty/f287/f23f/'
A = D + 'arms/'
SPV_VAL = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-val.exe'
NL = chr(10)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def val(path):
    r = subprocess.run([SPV_VAL, '--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout', path], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip().replace(NL, ' | ')[:300]


def named_var(data, name):
    ins = R.instrs(R.words_of(data))
    ids = [x[1] for x in ins if x[0] & 0xffff == 5 and bytes(b for w in x[2:] for b in w.to_bytes(4, 'little')).split(b'\0')[0] == name.encode()]
    vars_ = set(x[2] for x in ins if x[0] & 0xffff == 59)
    ids = [i for i in ids if i in vars_]
    return ids[0] if len(ids) == 1 else None


def swap_sites(data, sites):
    """sensitivity control: every form-A OpSelect gets its two value operands swapped (on lanes with the condition true it
    returns old) - the outputs observe the sites when def != sens"""
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
    import struct
    return struct.pack('<%dI' % len(w), *w)


def count(data, op):
    return sum(1 for x in R.instrs(R.words_of(data)) if x[0] & 0xffff == op)


def main():
    os.makedirs(A, exist_ok=True)
    S = json.load(open(D + 'sites_f23f.json'))
    out, res = [], {}
    ok = True
    for h, v in sorted(S.items(), key=lambda x: (x[1]['stage'], x[0])):
        base = open(D + 's12spv/' + v['spv'], 'rb').read()
        assert sha(base) == v['spv_sha']
        sites = [(s['sid'], s['cid'], s['nid'], s['oid']) for s in v['sites']]
        sids = [s[0] for s in sites]
        fv = named_var(base, 'fault_buffer')
        bv = named_var(base, 'buffers')
        diag = ('fault_buffer', fv, [0]) if fv else ('buffers', bv, [0, 0])
        arms = {'def': base}
        arms['mask'], n1 = R.rewrite(base, sites, 'mask')
        arms['mem'], n2 = R.rewrite(base, sites, 'mem')
        arms['blend'], done = phi_f23c.blend(base, select_ids=set(sids))
        arms['sens'] = swap_sites(base, sites)
        arms['diagT'], n3 = R.rewrite(base, sites, 'diag', diag_var=diag[1], diag_base=16, diag_prefix=tuple(diag[2]))
        rec = {'stage': v['stage'], 'sites': len(sites), 'diag_var': diag[0], 'diag_var_id': diag[1], 'diag_prefix': diag[2], 'files': {}}
        line = ['%s %s sites %d' % (v['stage'], h, len(sites))]
        for k, b in arms.items():
            p = A + '%s_%s_%s.spv' % (v['stage'], h, k)
            open(p, 'wb').write(b)
            rc, msg = val(p)
            left = R.selects_at(b, sids)
            phi = count(b, 245) - count(base, 245)
            good = rc == 0 and (k in ('def', 'diagT', 'sens') or (not left and phi == 0)) and (k not in ('diagT', 'sens') or len(left) == len(sids))
            ok &= good
            rec['files'][k] = {'sha': sha(b), 'bytes': len(b), 'val_rc': rc, 'sites_left': len(left), 'phi_added': phi, 'ok': good}
            line.append('%s %s val %d left %d phi+%d%s' % (k, sha(b)[:12], rc, len(left), phi, '' if good else ' FAIL ' + msg))
        assert n1 == n2 == n3 == len(sites) and len(done) == len(sites)
        res[h] = rec
        out.append(' | '.join(line))
    out.append('ALL OK' if ok else 'FAILED')
    open(D + 'arms_f23f.out.txt', 'w', encoding='utf-8', newline=NL).write(NL.join(out) + NL)
    json.dump(res, open(D + 'arms_f23f.json', 'w'), indent=1, sort_keys=True)
    print(NL.join(out))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

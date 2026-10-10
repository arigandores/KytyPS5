"""F36a (HPP-758, ROADMAP s122 item 687(e)(0)(i)): the three form-A sites of be4c35a2031fd3f4 (census F23a/F23f on the S12
translation: %5038, %5040, %5064 = OpSelect %uint) located in the FS11 translation (cache file of the variant directory _fixf19) by
alignment of the two disassemblies (spirv-dis --raw-id): every instruction is reduced to its text with the ids removed, the two
sequences are aligned (difflib, autojunk off), and the id map S12 -> FS11 is read from the equal blocks. A site is accepted only if
(a) the site instruction lies in an equal block, (b) every instruction of its window (WIN instructions on each side) lies in equal
blocks, (c) the id map is consistent (one FS11 id per S12 id and back) over all equal blocks, (d) the operands of the site in FS11 =
the mapped operands of the site in S12, (e) the sample instruction feeding 'new' maps too.  Output: align_f36a.out.txt, align_f36a.json.
Also: the FS11 translation is diffed against S12 by opcode (what F19 changed). ASCII only."""
import collections
import difflib
import json
import re
import subprocess
import sys

DIS = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-dis.exe'
D = 'C:/kyty/f287/f36a/'
NL = chr(10)
WIN = 60
S12_SITES = [5038, 5040, 5064]
S12_SAMPLES = {5038: 5027, 5040: 5027, 5064: 5051}


def dis(p):
    t = subprocess.run([DIS, '--raw-id', p], capture_output=True, text=True).stdout
    return [l.strip() for l in t.split(NL) if l.strip() and not l.strip().startswith(';')]


def norm(l):
    return re.sub(r'%\d+', '%', l)


def ids(l):
    return [int(x) for x in re.findall(r'%(\d+)', l)]


def main():
    a = dis(D + 'spv/s12_p0.spv')
    b = dis(D + 'spv/fs11_p0.spv')
    na, nb = [norm(x) for x in a], [norm(x) for x in b]
    sm = difflib.SequenceMatcher(None, na, nb, autojunk=False)
    blocks = sm.get_matching_blocks()
    inblk_a = {}
    fwd, bwd, conflicts = {}, {}, 0
    for (i, j, n) in blocks:
        for k in range(n):
            inblk_a[i + k] = j + k
            ia, ib = ids(a[i + k]), ids(b[j + k])
            if len(ia) != len(ib):
                conflicts += 1
                continue
            for x, y in zip(ia, ib):
                if fwd.setdefault(x, y) != y or bwd.setdefault(y, x) != x:
                    conflicts += 1
    out = []
    out.append('S12 lines %d, FS11 lines %d, equal-block lines %d, ratio %.4f, id-map conflicts %d' % (
        len(a), len(b), sum(n for _, _, n in blocks), sm.ratio(), conflicts))
    ops_a = collections.Counter(x.split('=')[-1].split()[0] for x in a if '=' in x)
    ops_b = collections.Counter(x.split('=')[-1].split()[0] for x in b if '=' in x)
    out.append('opcode count diff (FS11 - S12): ' + ', '.join('%s %+d' % (k, ops_b[k] - ops_a[k]) for k in sorted(set(ops_a) | set(ops_b)) if ops_b[k] != ops_a[k]))
    res = {'conflicts': conflicts, 'sites': []}
    ok = conflicts == 0
    pos = {}
    for i, l in enumerate(a):
        m = re.match(r'%(\d+) = ', l)
        if m:
            pos[int(m.group(1))] = i
    posb = {}
    for i, l in enumerate(b):
        m = re.match(r'%(\d+) = ', l)
        if m:
            posb[int(m.group(1))] = i
    for s in S12_SITES:
        i = pos[s]
        win_ok = all((i + d) in inblk_a for d in range(-WIN, WIN + 1) if 0 <= i + d < len(a))
        j = inblk_a.get(i)
        la = a[i]
        lb = b[j] if j is not None else ''
        mapped = [fwd.get(x) for x in ids(la)]
        oper_ok = j is not None and mapped == ids(lb)
        smp = S12_SAMPLES[s]
        smp_b = fwd.get(smp)
        smp_ok = smp_b is not None and smp_b in posb and norm(a[pos[smp]]) == norm(b[posb[smp_b]])
        r = {'s12_sid': s, 's12_line': la, 'fs11_line': lb, 'window_equal': win_ok, 'operands_mapped': oper_ok,
             's12_sample': a[pos[smp]], 'fs11_sample': b[posb[smp_b]] if smp_ok else None, 'sample_mapped': smp_ok}
        if j is not None:
            ib = ids(lb)
            r['fs11'] = {'sid': ib[0], 'cid': ib[2], 'nid': ib[3], 'oid': ib[4]}
        ok &= win_ok and oper_ok and smp_ok
        res['sites'].append(r)
        out.append(json.dumps(r, sort_keys=True))
    out.append('ALL OK' if ok else 'FAIL')
    json.dump(res, open(D + 'align_f36a.json', 'w'), indent=1, sort_keys=True)
    open(D + 'align_f36a.out.txt', 'w', newline=NL).write(NL.join(out) + NL)
    print(NL.join(out))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

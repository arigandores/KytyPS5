"""F36a (HPP-758, ROADMAP s122 item 687(e)(0)(i)): kind of each form-A site of be4c35a2031fd3f4 in the FS11 translation
(spv/fs11_p0.spv; sites from align_f36a.json) and of the H reference (F23c ref_predoff.spv, %286 / %306): execution model and
modes, the sampling instruction of 'new' (backward walk as F23g kind_f23g.py), the block of the site vs the block of the sample,
the condition, and what the site writes - forward data-flow reachability (every instruction that uses a reached id) to OpStore
into an Output variable (Location / BuiltIn printed) or a StorageBuffer / Image write. Output: kind_f36a.out.txt, kind_f36a.json."""
import json
import re
import subprocess

DIS = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-dis.exe'
D = 'C:/kyty/f287/f36a/'
NL = chr(10)


def dis(p):
    return [l.strip() for l in subprocess.run([DIS, '--raw-id', p], capture_output=True, text=True).stdout.split(NL) if l.strip()]


def analyse(name, path, sids):
    L = dis(path)
    d, users, blk_of, deco, var_sc = {}, {}, {}, {}, {}
    cur = None
    stores = []
    modes = [l for l in L if l.startswith('OpEntryPoint') or l.startswith('OpExecutionMode')]
    for l in L:
        m = re.match(r'%(\d+) = (\w+)(.*)', l)
        if m:
            rid, op, rest = m.group(1), m.group(2), m.group(3)
            d[rid] = l
            if op == 'OpLabel':
                cur = rid
            blk_of[rid] = cur
            if op == 'OpVariable':
                var_sc[rid] = rest.split()[-1] if rest.split()[-1] in ('Output', 'Input', 'StorageBuffer', 'Uniform', 'UniformConstant', 'PushConstant', 'Function', 'Private') else rest.split()[1]
            args = re.findall(r'%(\d+)', rest)
            for a in args[1:] if op not in ('OpLabel',) else []:
                users.setdefault(a, []).append(rid)
        elif l.startswith('OpStore') or l.startswith('OpImageWrite') or l.startswith('OpAtomic'):
            a = re.findall(r'%(\d+)', l)
            stores.append((l, a))
            for x in a[1:]:
                users.setdefault(x, []).append('store:%d' % (len(stores) - 1))
        elif l.startswith('OpDecorate'):
            a = re.findall(r'%(\d+)', l)
            deco.setdefault(a[0], []).append(l.split(None, 2)[2])
    # pointer roots: access chains -> base variable
    def root(p):
        k = 0
        while p in d and k < 20 and re.match(r'%\d+ = OpAccessChain', d[p]):
            p = re.findall(r'%(\d+)', d[p])[2]
            k += 1
        return p
    out = {'name': name, 'modes': modes, 'sites': []}
    for sid in sids:
        s = d[str(sid)]
        ops = re.findall(r'%(\d+)', s)
        cid, nid = ops[2], ops[3]
        seen, todo, found = set(), [nid], []
        while todo and len(seen) < 60:
            x = todo.pop(0)
            if x in seen or x not in d:
                continue
            seen.add(x)
            if 'OpImageSample' in d[x] or 'OpImageGather' in d[x] or 'OpImageFetch' in d[x]:
                found.append(x)
                continue
            todo += re.findall(r'%(\d+)', d[x])[2:]
        reach, todo, hit = set(), [str(sid)], {}
        while todo:
            x = todo.pop()
            if x in reach:
                continue
            reach.add(x)
            for u in users.get(x, []):
                if u.startswith('store:'):
                    l, a = stores[int(u[6:])]
                    r = root(a[0])
                    key = '%%%s %s %s' % (r, var_sc.get(r, '?'), ' '.join(deco.get(r, [])))
                    hit[key] = hit.get(key, 0) + 1
                else:
                    todo.append(u)
        out['sites'].append({'sid': sid, 'line': s, 'cond': d.get(cid, '?'), 'sample': [d[f] for f in found],
                             'sample_same_block': [blk_of.get(f) == blk_of.get(str(sid)) for f in found],
                             'writes': sorted(hit.items()), 'reached_ids': len(reach)})
    return out


def main():
    al = json.load(open(D + 'align_f36a.json'))
    fs = [s['fs11']['sid'] for s in al['sites']]
    res = [analyse('H reference predoff (F23c)', 'C:/kyty/f287/f23c/work/ref_predoff.spv', [286, 306]),
           analyse('be4c35a2031fd3f4 FS11 (_fixf19)', D + 'spv/fs11_p0.spv', fs),
           analyse('be4c35a2031fd3f4 S12 / capture module', D + 'spv/s12_p0.spv', [5038, 5040, 5064])]
    lines = []
    for r in res:
        lines.append('== ' + r['name'] + ' | ' + ' | '.join(r['modes']))
        for s in r['sites']:
            lines.append('  site %s | cond %s | new <- %s (same block %s) | writes %s | reached %d' % (
                s['line'], s['cond'], s['sample'], s['sample_same_block'], s['writes'], s['reached_ids']))
    json.dump(res, open(D + 'kind_f36a.json', 'w'), indent=1)
    open(D + 'kind_f36a.out.txt', 'w', newline=NL).write(NL.join(lines) + NL)
    print(NL.join(lines))


main()

"""F23g (HPP-593): sampling kind of the value 'new' of the form-A sites (spirv-dis --raw-id, walk the definition chain of 'new'
up to the first OpImage* instruction) for the H reference (predoff %286, %306) and the two programs read by F23f as "not found"
(0078153a1c1fb171 %784, be4c35a2031fd3f4 %5038, %5040, %5064); also the execution model / modes. Output: kind_f23g.out.txt."""
import re
import subprocess

DIS = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-dis.exe'
NL = chr(10)
jobs = [('ref predoff (F23c)', 'C:/kyty/f287/f23c/work/ref_predoff.spv', [286, 306]),
        ('cs 0078153a1c1fb171 (S12)', 'C:/kyty/f287/f23f/arms/cs_0078153a1c1fb171_def.spv', [784]),
        ('ps be4c35a2031fd3f4 (S12)', 'C:/kyty/f287/f23f/arms/ps_be4c35a2031fd3f4_def.spv', [5038, 5040, 5064])]
out = []
for name, path, sids in jobs:
    txt = subprocess.run([DIS, '--raw-id', path], capture_output=True, text=True).stdout
    d = {}
    modes = []
    for l in txt.split(NL):
        m = re.match(r'\s*%(\d+) = (.*)', l)
        if m:
            d[m.group(1)] = m.group(2)
        if 'OpEntryPoint' in l or 'OpExecutionMode' in l:
            modes.append(l.strip())
    out.append('== %s: %s' % (name, ' | '.join(modes)))
    for sid in sids:
        s = d[str(sid)]
        nid = re.findall(r'%(\d+)', s)[2]
        seen, todo, found = set(), [nid], []
        while todo and len(seen) < 40:
            x = todo.pop(0)
            if x in seen or x not in d:
                continue
            seen.add(x)
            if re.match(r'OpImage(Sample|Gather|Fetch|Read)', d[x].split(' ', 1)[0] if ' ' not in d[x][:3] else d[x]) or 'OpImageSample' in d[x] or 'OpImageGather' in d[x]:
                found.append('%' + x + ' = ' + d[x][:110])
                continue
            todo += re.findall(r'%(\d+)', d[x])[1:]
        out.append('  site %%%d = %s ; new %%%s -> %s' % (sid, s[:60], nid, found[:2]))
open('C:/kyty/f287/f23g/kind_f23g.out.txt', 'w', newline=NL).write(NL.join(out) + NL)
print(NL.join(out))

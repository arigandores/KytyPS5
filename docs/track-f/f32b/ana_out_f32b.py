import json,collections
res=json.load(open('outglob.json',encoding='utf-8'))
known=set()
for f in ('C:/kyty/f287/f0/sig_f0.tsv','C:/kyty/f287/f32a/sig_f32a.tsv'):
    L=open(f,'rb').read().split(bytes([10]))
    hdr=L[0].split(bytes([9])); ci=hdr.index(b'signature')
    for l in L[1:]:
        c=l.split(bytes([9]))
        if len(c)>ci: known.add(c[ci].rstrip(bytes([13])).decode('latin1')); known.add(c[ci].rstrip(bytes([13])).decode('utf-8','replace'))
print('known',len(known))
k2=known
newsig=collections.defaultdict(list)
for r in res:
    print(r['path'].replace('C:/kyty/',''),'fork',r['fork'],'lines',r['lines'],'w',r['w'],'skipped',r['skipped_n'],'req',r['req_n'],'req_skipped',r['req_skipped'],'quit',r['quit_line'],'fatal_after_quit',r['fatal_after_quit'],'big',r['big'][:6])
    for fl in r['fatal_lines'][:4]: print('    FATAL',fl)
    for s,v in r['sigs'].items():
        if s not in known and s not in k2: newsig[s].append((r['path'].replace('C:/kyty/',''),v,r['ex'][s]))
print('NEW SIGS vs F0+F32a:',len(newsig))
for s,l in sorted(newsig.items(),key=lambda x:-len(x[1])):
    print(len(l),repr(s[:160]),l[:2])

"""F14c (HPP-489, ROADMAP s122 item 400(v)): table of compare sites x (filter, format) over the captures, and the outcome by the
rule of item 400(v) (decided by the lead before this link):
  (1) >= 1 manual site record with LINEAR in magFilter or minFilter on the compared image => 'DEFECT_FOR_F14D';
  (2) all manual site records NEAREST in both filters => 'OBSERVATION_PARKED';
  (3) 0 manual site records, or a binding not readable => 'UNDETERMINED'.
Input: the AGG / UNRES / SUMMARY lines of rd_cmp_f14c.py outputs cmp_<cap>.txt.  Module names: the sha256 of a captured module is
looked up among the S7 pass-A SPIR-V of the T1 corpus (t1_base.tsv spv_sha256_a) to give its guest hash16 where the same bytes exist.
Writes f14c_table.tsv (one row per capture x kind x stage x filter x formats) and f14c_summary.txt; ASCII only; ends with ALL OK / FAIL
(ALL OK = every capture read with 'done' and 0 unresolved).
"""
import csv, os, re, sys

D = 'C:/kyty/f287/f14c'
CAPS = [('f12_rd_k01', 'cmp_k01.txt'), ('f12_rd_k02', 'cmp_k02.txt'), ('f12_rd_k03', 'cmp_k03.txt'), ('f12_rd_k04', 'cmp_k04.txt'),
        ('f12_rd_k05', 'cmp_k05.txt'), ('f12_rd_k06', 'cmp_k06.txt'), ('f12_rd_k07', 'cmp_k07.txt'), ('f12_rd_k08', 'cmp_k08.txt'),
        ('f13_rd', 'cmp_f13.txt'), ('rd2_f3951', 'cmp_f9.txt'), ('enemy_final_600', 'cmp_ef.txt')]
SCENE = {'f12_rd': 'underwater_aerial_garden', 'f13_rd': 'ending_boss_after_credit', 'rd2_f3951': 'underwater_aerial_garden',
         'enemy_final_600': 'enemy_final'}
S7 = 'C:/kyty/s288/s7/t1_base.tsv'
corpus = {}
for r in csv.DictReader(open(S7, encoding='ascii'), delimiter='\t'):
    if r['row'] == 'A' and r['outcome'] == 'OK' and r.get('spv_sha256_a'):
        corpus[r['spv_sha256_a'][:16]] = '%s_%s_p%s' % (r['stage'], r['hash16'], r['perm'])
AGG = re.compile(r'^AGG stage=(\S+) mod=(\S+) site=(\S+) img=(\S+) smp=(\S+) depthflag=(\S+) mag=(\S+) min=(\S+) mip=(\S+) '
                 r'cmpEnable=(\S+) cmpOp=(\S+) aniso=(\S+) smp_pnext=(\S+) view_format=(\S+) aspect=(\S+) image_format=(\S+) '
                 r'src=(\S+) n=(\d+)$')
ok = True
rows = []
caps_info = []
for cap, fn in CAPS:
    p = D + '/' + fn
    lines = open(p, encoding='ascii').read().split('\n')
    done = 'done' in lines
    summ = [l for l in lines if l.startswith('SUMMARY')]
    unres = sum(int(l.rsplit('n=', 1)[1]) for l in lines if l.startswith('UNRES'))
    ok &= done and len(summ) == 1 and unres == 0
    caps_info.append((cap, done, summ[0] if summ else '-', unres))
    for l in lines:
        m = AGG.match(l)
        if not m:
            if l.startswith('AGG'):
                print('UNPARSED', cap, l[:120]); ok = False
            continue
        g = m.groups()
        kind = g[2].split('/')[0]
        rows.append({'capture': cap, 'scene': SCENE[cap.split('_k')[0]] if cap.startswith('f12_rd') else SCENE[cap],
                     'kind': kind, 'stage': g[0], 'module': g[1], 'corpus': corpus.get(g[1], '-'), 'site': g[2], 'img': g[3],
                     'smp': g[4], 'mag': g[6].replace('VK_FILTER_', ''), 'min': g[7].replace('VK_FILTER_', ''),
                     'mip': g[8].replace('VK_SAMPLER_MIPMAP_MODE_', ''), 'cmpEnable': g[9], 'aniso': g[11],
                     'view_format': g[13].replace('VK_FORMAT_', ''), 'aspect': g[14].replace('VK_IMAGE_ASPECT_', ''),
                     'image_format': g[15].replace('VK_FORMAT_', ''), 'src': g[16], 'n': int(g[17])})
cols = ['capture', 'scene', 'kind', 'stage', 'module', 'corpus', 'site', 'img', 'smp', 'mag', 'min', 'mip', 'cmpEnable', 'aniso',
        'view_format', 'aspect', 'image_format', 'src', 'n']
with open(D + '/f14c_table.tsv', 'wb') as f:
    f.write(('\t'.join(cols) + '\n').encode('ascii'))
    for r in rows:
        f.write(('\t'.join(str(r[c]) for c in cols) + '\n').encode('ascii'))
out = []
out.append('F14c table summary (HPP-489); records = site x draw/dispatch; captures %d' % len(CAPS))
for cap, done, summ, unres in caps_info:
    out.append('  %-16s done=%s unresolved=%d | %s' % (cap, done, unres, summ.replace('SUMMARY ', '')))


def census(sel, keyf):
    c = {}
    for r in sel:
        k = keyf(r)
        c[k] = c.get(k, 0) + r['n']
    return c


for kind in ('manual', 'native'):
    sel = [r for r in rows if r['kind'] == kind]
    out.append('%s: records %d, captures with records %d, distinct modules %d, distinct (module, site) %d' % (
        kind, sum(r['n'] for r in sel), len(set(r['capture'] for r in sel)), len(set(r['module'] for r in sel)),
        len(set((r['module'], r['site'], r['img'], r['smp']) for r in sel))))
    for k, v in sorted(census(sel, lambda r: (r['stage'], 'mag=%s min=%s mip=%s cmpEnable=%s aniso=%s' % (
            r['mag'], r['min'], r['mip'], r['cmpEnable'], r['aniso']), r['view_format'] + '/' + r['aspect'])).items()):
        out.append('  %s %s view=%s : %d' % (k[0], k[1], k[2], v))
    for k, v in sorted(census(sel, lambda r: (r['scene'], r['mag'] + '/' + r['min'])).items()):
        out.append('  scene %s filter %s : %d' % (k[0], k[1], v))
    for k, v in sorted(census(sel, lambda r: r['src']).items()):
        out.append('  src %s : %d' % (k, v))
man = [r for r in rows if r['kind'] == 'manual']
lin = [r for r in man if r['mag'] == 'LINEAR' or r['min'] == 'LINEAR']
near = [r for r in man if r['mag'] == 'NEAREST' and r['min'] == 'NEAREST']
lin_certain = [r for r in lin if all(x in ('fresh', 'set1') for x in r['src'].split('/'))]
out.append('manual records with LINEAR in mag or min: %d (of them with src fresh/set1 on both bindings: %d) in captures %s' % (
    sum(r['n'] for r in lin), sum(r['n'] for r in lin_certain), ','.join(sorted(set(r['capture'] for r in lin)))))
out.append('manual records NEAREST/NEAREST: %d; other: %d' % (sum(r['n'] for r in near),
                                                              sum(r['n'] for r in man) - sum(r['n'] for r in lin) - sum(r['n'] for r in near)))
out.append('manual LINEAR records by view format: %s' % ', '.join('%s %d' % kv for kv in sorted(census(lin, lambda r: r['view_format']).items())))
out.append('manual LINEAR distinct modules: %d; with a corpus name: %s' % (
    len(set(r['module'] for r in lin)), ','.join(sorted(set(r['corpus'] for r in lin if r['corpus'] != '-')))))
if not ok:
    outcome = 'UNDETERMINED (a capture not read or a binding not resolved)'
elif not man:
    outcome = 'UNDETERMINED (0 manual site records)'
elif lin_certain:
    outcome = 'DEFECT_FOR_F14D (rule 400(v)(1): >= 1 manual site with LINEAR)'
elif lin:
    outcome = 'UNDETERMINED (LINEAR only on records with carry/setN source)'
else:
    outcome = 'OBSERVATION_PARKED (rule 400(v)(2))' if len(near) == len(man) else 'UNDETERMINED (filters other than LINEAR/NEAREST)'
out.append('OUTCOME %s' % outcome)
out.append('ALL OK' if ok else 'FAIL')
text = '\n'.join(out) + '\n'
open(D + '/f14c_summary.txt', 'wb').write(text.encode('ascii', 'replace'))
sys.stdout.write(text)
sys.exit(0 if ok else 1)

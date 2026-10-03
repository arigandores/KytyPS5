# F12f (HPP-480): edition 2 of f12f_read.py (seal section 8): exact names of the capture read files (the glob rdcs_f12_rd_k*.txt took
# the .qrd.txt side files) and the per-capture choice between the in-lock read rdcs and the offline structured-data read rdsd.
p = 'C:/kyty/f287/f12f/f12f_read.py'
s = open(p, encoding='ascii').read()
reps = [
("           rdc_sha.txt and rdcs_k*.txt for rd)",
 "           rdc_sha.txt, rdcs_kNN.txt and rdsd_kNN.txt for rd)"),
("                 idx=os.path.join(base, 'rec.idx'), rdcs=sorted(glob.glob(os.path.join(base, 'rdcs_k*.txt'))))",
 "                 idx=os.path.join(base, 'rec.idx'), rdcs=kfiles(base, 'rdcs_k'), rdsd=kfiles(base, 'rdsd_k'))"),
("             rdcs=sorted(glob.glob(os.path.join(G, 'rdcs_f12_rd_k*.txt'))) if kind == 'rd' else [])",
 "             rdcs=kfiles(G, 'rdcs_f12_rd_k') if kind == 'rd' else {}, rdsd=kfiles(G, 'rdsd_f12_rd_k') if kind == 'rd' else {})"),
('''def rdcs_read(files):
    out = []
    for p in files:
        t = text(p) or ''
        m = RX_SUM.search(t)
        done = any(x.strip() == 'done' for x in t.split('\\n'))
        out.append(dict(file=os.path.basename(p), done=done, dispatches=int(m.group(1)) if m else None,
                        distinct=int(m.group(2)) if m else None, marked=int(m.group(3)) if m else None,
                        eids=m.group(4) if m else None))
    return out
''',
'''def kfiles(base, prefix):
    """{NN: path} of the files <prefix>NN.txt exactly (not <prefix>NN.txt.qrd.txt and the like; F12f section 8, edition 2)."""
    rx = re.compile('^' + re.escape(prefix) + r'(\\d\\d)\\.txt$')
    out = {}
    for n in (os.listdir(base) if os.path.isdir(base) else []):
        m = rx.match(n)
        if m:
            out[m.group(1)] = os.path.join(base, n)
    return out


def one_read(p):
    t = text(p) or ''
    m = RX_SUM.search(t)
    done = any(x.strip() == 'done' for x in t.split('\\n'))
    return dict(file=os.path.basename(p), done=done, dispatches=int(m.group(1)) if m else None,
                distinct=int(m.group(2)) if m else None, marked=int(m.group(3)) if m else None, eids=m.group(4) if m else None)


def rdcs_read(rdcs, rdsd):
    """per capture NN: the in-lock read rdcs (rd_cs_f12f.py) if it has its done line, else the offline structured-data read rdsd
    (rd_sd_f12f.py, F12f section 8, edition 2), else the in-lock read as it is (done NO)."""
    out = []
    for k in sorted(set(rdcs) | set(rdsd)):
        a = one_read(rdcs[k]) if k in rdcs else None
        b = one_read(rdsd[k]) if k in rdsd else None
        out.append(a if a is not None and a['done'] else (b if b is not None and b['done'] else (a or b)))
    return out
'''),
("    rdcs = rdcs_read(p.get('rdcs') or [])\n", "    rdcs = rdcs_read(p.get('rdcs') or {}, p.get('rdsd') or {})\n"),
("import glob, hashlib, json, os, re, sys", "import hashlib, json, os, re, sys"),
]
for a, b in reps:
    assert s.count(a) == 1, (a[:60], s.count(a))
    s = s.replace(a, b)
open(p, 'w', encoding='ascii', newline='\n').write(s)
print('patched')

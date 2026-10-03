# F12f (HPP-480): edition 2 fixtures of test_f12f_read.py (seal section 8): side files rdcs_kNN.txt.qrd.txt are not reads; the offline
# structured-data read rdsd_kNN.txt is taken when the in-lock read has no done line; the in-lock read with done wins over rdsd.
p = 'C:/kyty/f287/f12f/test_f12f_read.py'
s = open(p, encoding='ascii').read()
a = "         sha_t=None, before=INSHA, after=INSHA, cold=None, mcmp=EQ, mref=EQ, rdc=None, rdcs=None):"
b = "         sha_t=None, before=INSHA, after=INSHA, cold=None, mcmp=EQ, mref=EQ, rdc=None, rdcs=None, rdsd=None, side=False):"
assert s.count(a) == 1
s = s.replace(a, b)
a = """    for i, t in enumerate(rdcs or [], 1):
        with open(os.path.join(d, 'rdcs_k%02d.txt' % i), 'wb') as f:
            f.write((t + '\\n').encode('utf-8'))
"""
b = """    for i, t in enumerate(rdcs or [], 1):
        with open(os.path.join(d, 'rdcs_k%02d.txt' % i), 'wb') as f:
            f.write((t + '\\n').encode('utf-8'))
        if side:
            with open(os.path.join(d, 'rdcs_k%02d.txt.qrd.txt' % i), 'wb') as f:
                f.write(b'qrenderdoc output\\n')
    for i, t in enumerate(rdsd or [], 1):
        if t is not None:
            with open(os.path.join(d, 'rdsd_k%02d.txt' % i), 'wb') as f:
                f.write((t + '\\n').encode('utf-8'))
"""
assert s.count(a) == 1
s = s.replace(a, b)
a = "d = make('rd_none', 'rd',"
b = """d = make('rd_side', 'rd', rl, rdc=RDC2, rdcs=[SUM_0, SUM_M], side=True)
r_, m_ = rowmap(d, 'rd')
check('rd side files .qrd.txt are not reads: 2 reads, every read YES', len(r_['rdcs']) == 2 and row(m_, 'every capture read') == 'YES')
d = make('rd_sd', 'rd', rl, rdc=RDC2, rdcs=[SUM_0, SUM_ND], rdsd=[None, SUM_M], side=True)
r_, m_ = rowmap(d, 'rd')
check('rd in-lock read without done, rdsd with done: rdsd taken, read YES, marked 1 of 2',
      r_['rdcs'][1]['file'] == 'rdsd_k02.txt' and row(m_, 'every capture read') == 'YES'
      and row(m_, 'captures with >= 1 dispatch of 380bb9d6 by SPIR-V sha (DATA for F12g, no gate): 1 of 2') == 'YES')
d = make('rd_sd2', 'rd', rl, rdc=RDC2, rdcs=[SUM_0, SUM_M], rdsd=[SUM_M, SUM_0])
r_, m_ = rowmap(d, 'rd')
check('rd in-lock read with done wins over rdsd', r_['rdcs'][0]['file'] == 'rdcs_k01.txt' and r_['rdcs'][0]['marked'] == 0
      and r_['rdcs'][1]['marked'] == 2)
d = make('rd_sdonly', 'rd', rl, rdc=RDC2, rdcs=[], rdsd=[SUM_0, SUM_ND])
r_, m_ = rowmap(d, 'rd')
check('rd only rdsd, one without done: read NO', len(r_['rdcs']) == 2 and row(m_, 'every capture read') == 'NO')
"""
assert s.count(a) == 1
s = s.replace(a, b + a)
open(p, 'w', encoding='ascii', newline='\n').write(s)
print('patched')

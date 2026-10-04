import pickle, os
T = ['t2_1','t2_2','t2_4','t2_5','t2_7','t2_cs0','c5_0','pi_r0','pi_r1','pi_w0','pi_w1','t2_3','t2_6','u_1','u_2','u_3','u_4','u_5']
L = {t: pickle.load(open(t + '.pkl','rb')) for t in T}
blk = {'828215ad31a7f2ca','acee300df6a19856','720d1f629e89e619'}
specs = {}
for c in L['t2_1']['comp'] + L['t2_5']['comp']:
    if c[2] in blk: specs[c[2]] = c[4].strip()
for h, sp in specs.items():
    where = [(t, c[2][:8], c[1], c[0]) for t in T for c in L[t]['comp'] if c[4] is not None and c[4].strip() == sp]
    print(h[:8], 'ntok', len(sp.split()), 'found in compiles:', where)
    with open('C:/kyty/s288/s14j/specdump_snap0.txt','rb') as f:
        n = sum(1 for l in f if l.rstrip(b'\r\n').endswith(b' spec=' + sp.encode()))
    print('   dump records with this exact string (any stage):', n)

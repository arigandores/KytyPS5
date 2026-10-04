import pickle, json
blk = {('t2_1', 317), ('t2_5', 164), ('t2_7', 147)}
W = {('t2_1',282):35,('t2_1',317):30,('t2_2',217):3,('t2_4',138):2,('t2_5',164):15,('t2_7',147):18}
irr = 0; det = []
for t, a in sorted(blk):
    d = pickle.load(open(t + '.pkl', 'rb')); fst = json.load(open('C:/kyty/s288/s10/runs_s/%s.score.json' % t))['first'][0]
    b = {('t2_1',317):334, ('t2_5',164):172, ('t2_7',147):156}[(t, a)]
    held = sum(d['skc'].get(n, (0, 0))[0] for n in range(a, b + 1) if n >= fst)
    skr = sum(1 for n in range(a, b + 1) if d['skc'].get(n, (0, 0))[1] > 0 and n > fst)
    irr += held; det.append((t, a, b, 'held', held, 'skip rows', skr))
print(det)
print('event-level generous ceiling: held flips of the three blocked series irreducible, everything else removable: (103 - %d) / 103 = %.4f' % (irr, (103 - irr) / 103))

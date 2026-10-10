# F36b (HPP-759): check of the links <commit>:<path>:<line> of docs/track-f/f36b-review.md - the anchor is in the line, the +1 text
# is in the next line (empty +1 = the next line is empty). Run from C:/kyty/KytyPS5. ASCII-only source (anchors as \u escapes).
import subprocess, sys
L = [
    ('02531a91', 'docs/ROADMAP.md', 24428, '(\u0437) **\u0417\u0430\u0434\u0430\u043d\u0438\u0435 F36b (Red Team;', '(\u0438) **\u0417\u0432\u0435\u043d\u044c\u044f.**'),
    ('02531a91', 'docs/ROADMAP.md', 24419, '(1) **\u0427\u043b\u0435\u043d \u0433\u043e\u0434\u043d\u043e\u0441\u0442\u0438 \u0441\u043e\u0431\u044b\u0442\u0438\u044f (\u0434\u043e \u0434\u0430\u043d\u043d\u044b\u0445):**', '(2) **\u041f\u0440\u043e\u0433\u043e\u043d:**'),
    ('02531a91', 'docs/ROADMAP.md', 22845, '(\u0432) **RC1\u2013RC4 F23g \u043f\u0440\u0438\u043d\u044f\u0442\u044b (\u0440\u0435\u0448\u0435\u043d\u0438\u0435 \u043b\u0438\u0434\u0430).**', '(\u0433) **\u041e\u0442\u0432\u0435\u0442\u044b \u043d\u0430 \u0432\u043e\u043f\u0440\u043e\u0441\u044b F23f \u00a710.**'),
    ('f22eccf5', 'docs/track-f/f23g-review.md', 157, '\u043e\u0431\u0440\u0430\u0449\u0451\u043d\u043d\u044b\u043c \u043a\u043e\u043d\u0442\u0440\u043e\u043b\u0435\u043c [c, \u00a72]. \u0418\u0437\u043c\u0435\u043d\u0438\u0442\u044c: \u043b\u044e\u0431\u043e\u0435 \u043e\u0442\u0440\u0438\u0446\u0430\u0442\u0435\u043b\u044c\u043d\u043e\u0435 `N` \u043b\u044e\u0431\u043e\u0433\u043e \u043f\u043b\u0435\u0447\u0430', '\u043d\u0430 \u043a\u0430\u0436\u0434\u043e\u043c \u0441\u043e\u0431\u044b\u0442\u0438\u0438, \u0447\u0438\u0442\u0430\u0435\u043c\u043e\u043c \u043a \u00ab\u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u043e\u00bb, \u2014 \u043f\u043b\u0435\u0447\u0438 `mask_inv`, `mem_inv`'),
    ('08214036', 'docs/track-f/f36a.md', 136, '- **\u041d\u0430\u0431\u043e\u0440:** \u0432\u0441\u0435 38 \u0441\u043e\u0431\u044b\u0442\u0438\u0439 \u043e\u043f\u0438\u0441\u0438, \u0432\u0441\u0435 \u043f\u043b\u0435\u0447\u0438', ''),
    ('08214036', 'docs/track-f/f36a/sum_f36a.py', 55, "m.append(('G1', all(v == 0 for v in e['Npre'].values())))", "m.append(('G2', e['n_entry'] == e['PSInv']))"),
    ('08214036', 'docs/track-f/f36a.md', 129, '- **\u04131:** `Npre_<\u043f\u043b\u0435\u0447\u043e>` = \u03a3 `N(orig \u0434\u043e, \u043f\u043b\u0435\u0447\u043e \u0434\u043e)` = 0', '- **\u04132:** `n_entry` = PSInvocations \u0441\u043e\u0431\u044b\u0442\u0438\u044f (\u043e\u043f\u0438\u0441\u044c).'),
    ('08214036', 'docs/track-f/f36a/rd_f36a.py', 148, 'for u in ps.GetReadWriteResources(sst):', "d = getattr(u, 'descriptor', None)"),
    ('08214036', 'docs/track-f/f36a.md', 228, '**\u04132 \u2713 \u043d\u0430 38 \u0438\u0437 38**', '\u0441\u043e\u0431\u044b\u0442\u0438\u044f\u0445 \u043f\u043e\u0441\u043b\u0435 \u0434\u0440\u0443\u0433\u0438\u0445 \u0438\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0439 \u0442\u043e\u0439 \u0436\u0435 \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u044b \u0432 \u043a\u0430\u0434\u0440\u0435'),
]
ok = True
for rev, path, n, a, p in L:
    t = subprocess.run(['git', 'show', '%s:%s' % (rev, path)], capture_output=True).stdout.decode('utf-8').split('\n')
    line, nxt = t[n - 1], t[n]
    good = a in line and ((p == '' and nxt.strip() == '') or (p != '' and p in nxt))
    ok &= good
    print('%s %s:%s:%d' % ('OK  ' if good else 'FAIL', rev, path, n))
print('links %d' % len(L))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)

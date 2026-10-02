"""jsonsrc145.py - s146 step 0: in profile 145 of sc146.py, the source entry_src(tag, 'json') takes for every made tag of s145 (json
when runs145/<tag>.score.json carries the log sha of the last enter_scene end line of step2/times.txt).  Read only.  ASCII."""
import importlib.util
import os
s = importlib.util.spec_from_file_location('sc146', 'C:/kyty/s146/sc146.py')
S = importlib.util.module_from_spec(s)
s.loader.exec_module(S)
S.profile(S.P145)
n = j = 0
for t in S.SEQ:
    if not S.made(t, S.ROOT):
        continue
    p = os.path.join(S.ROOT, S.RUNS, '%s.score.json' % t)
    if not os.path.isfile(p):
        print('JSONSRC %s: no score.json' % t)
        n += 1
        continue
    e, w = S.entry_src(t, S.ROOT, None, 'json')
    n += 1
    j += w == 'json'
    print('JSONSRC %s: %s' % (t, w))
print('JSONSRC made tags %d, read from score.json %d' % (n, j))

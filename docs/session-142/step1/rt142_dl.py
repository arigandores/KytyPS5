# Red Team s142 step 1: the sealed sc142.py read-only on two real device-lost logs of s128 (s1s128, s2s128): the death
# markers it collects (class, source, position) and the census outcome its outcome() gives on that log + json.
import sys, json, os
sys.path.insert(0, 'C:/kyty/s142')
import sc142 as S
for tag in ('s1s128', 's2s128'):
    root = 'C:/kyty/s128'
    lp, sp = '%s/log_%s.txt' % (root, tag), '%s/stdout_%s.txt' % (root, tag)
    js = json.load(open('%s/%s.json' % (root, tag), encoding='utf-8'))
    at = js['attempts'][-1]
    lv = js['guest_args'].split()[-1]
    log = S.scan(lp)
    std = S.scan(sp) if os.path.isfile(sp) else None
    d = S.derive(log, lv)
    ms = S.markers(log, std, d['entry_pos'], log['quit'])
    r = dict(derive=d, marks=ms, ended=at.get('hold_exit') is not None, exited=at.get('outcome') == 'exited',
             tail_stall=at.get('ft_tail') == 0 and at.get('hold_s') is not None, attempt_outcome=at.get('outcome'))
    print(tag, 'log sha', log['sha256'][:16], 'level', lv, 'attempt', at.get('label'), at.get('outcome'), 'hold_s',
          at.get('hold_s'), 'hold_exit', at.get('hold_exit'), 'ft_tail', at.get('ft_tail'))
    for k in ('crash', 'hang'):
        for kind, pos, line in log[k]:
            print('   log %s %s @%d %s' % (k, kind, pos, line[:90]))
        if std:
            for kind, pos, line in std[k]:
                print('   stdout %s %s @%d %s' % (k, kind, pos, line[:90]))
    print('   first %s K2 %s' % (d['first'], d['k2'][:3]))
    print('   sc142 outcome (letter, vx, key):', S.outcome(r))

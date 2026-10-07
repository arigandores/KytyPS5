"""F25f (HPP-669; port of F20l3 mk_seal_f20l3.py): writes pred/f25f_seal.md = the body + section 6 (suite counts from the LAST output files,
seal lines sha256 path).  Refuses if the seal exists (a seal is written once).  usage: python mk_seal_f25f.py <body.md>   ASCII source."""
import hashlib
import os
import sys

G = 'C:/kyty/f287/f25f'
SEAL = G + '/pred/f25f_seal.md'
FILES = ['f25_read.py', 'f20e_read.py', 'test_f25_read.py', 'sens_f25.py', 'regress_f25.py', 'refs_f25f.py', 'test_tools_f25f.py',
         'f25f_seal_body.md', 'snap_f25f.py', 'm6_f25f.py', 'go_f25f.sh', 'launch_f25f.sh', 'wait_f25f.sh', 'post_f25f.sh', 'chk_f25f.sh',
         'guard_f25f.py', 'queue_f25f.py', 'runchk_f25f.py', 'watch_f25f.py', 'enter_scene.py', 'procload.py', 'manifest_fs4c.py',
         'sheet142.py', 'gates_default.txt', 'idle142.py', 'run_safety99.py', 'launch_run.py', 'mk_seal_f25f.py',
         'test_f25_read.out.txt', 'sens_f25.out.txt', 'regress_f25.out.txt', 'refs_f25f.out.txt', 'refs_neg.out.txt', 'test_tools_f25f.out.txt',
         'C:/kyty/f287/f25d/kyty_emulator_e342b839.exe', 'C:/kyty/s288/bin/kyty_emulator_b3cee576.exe', 'C:/kyty/scripts/s51_vidglitch.py']
OUTS = [('test_f25_read.out.txt', 'checks '), ('sens_f25.out.txt', 'edits '), ('regress_f25.out.txt', 'REGRESS '), ('refs_f25f.out.txt', 'refs '),
        ('refs_neg.out.txt', 'NEG CONTROL '), ('test_tools_f25f.out.txt', 'checks ')]
HDR = '## 6. \u0421\u0442\u0440\u043e\u043a\u0438 \u043f\u0435\u0447\u0430\u0442\u0438 (sha256 \u0444\u0430\u0439\u043b\u043e\u0432 \u0438 \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0445 \u0432\u044b\u0432\u043e\u0434\u043e\u0432 \u043d\u0430\u0431\u043e\u0440\u043e\u0432)'
FIRST = '\u043f\u0435\u0440\u0432\u0430\u044f \u0441\u0442\u0440\u043e\u043a\u0430 \u043d\u0430\u0431\u043e\u0440\u0430'


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main(argv):
    if os.path.exists(SEAL):
        print('seal exists - refused')
        return 1
    body = open(argv[0], 'rb').read().decode('utf-8').replace('\r\n', '\n').rstrip('\n') + '\n'
    out = ['', HDR, '']
    for nm, key in OUTS:
        p = os.path.join(G, nm)
        lines = open(p, encoding='ascii', errors='replace').read().splitlines()
        cnt = [x for x in lines if x.startswith(key)]
        allok = 'ALL OK' in lines or 'REGRESS PASS' in lines or 'NEG CONTROL OK' in lines
        first = next((x for x in lines if x.startswith('suite')), '-')
        out.append('- `%s` (sha256 %s): %s; %s; %s: `%s`' % (nm, sha(p)[:16], cnt[-1] if cnt else '-', 'ALL OK' if allok else 'NOT OK', FIRST,
                                                           first[:200]))
    out.append('')
    for nm in FILES:
        p = nm if nm.startswith('C:/') else os.path.join(G, nm).replace('\\', '/')
        out.append('seal: %s %s' % (sha(p), p))
    text = body + '\n'.join(out) + '\n'
    os.makedirs(os.path.dirname(SEAL), exist_ok=True)
    with open(SEAL, 'wb') as f:
        f.write(text.encode('utf-8'))
    print('seal written %s sha256 %s lines %d' % (SEAL, sha(SEAL), text.count('\n')))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

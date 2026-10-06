"""F20l3 (HPP-655): writes pred/f20l3_seal.md = the body + section 8 (suite counts from the LAST output files, seal lines sha256 path).
Refuses if the seal exists (a seal is written once).  usage: python mk_seal_f20l3.py <body.md>   ASCII source and output."""
import hashlib
import os
import sys

G = 'C:/kyty/f287/f20l3'
SEAL = G + '/pred/f20l3_seal.md'
FILES = ['b32_read.py', 'f20e_read.py', 'test_b32_read.py', 'sens_b32.py', 'reserve_f20l3.py',
         'C:/kyty/f287/f20l/base/base_f20l.txt', 'C:/kyty/f287/f20l/runs/b32_z0/read.json', 'C:/kyty/f287/f20l2/runs/b32_z0b/read.json',
         'C:/kyty/f287/f20l2/pred/f20l2_seal.md', 'port_f20l3.py', 'edit_f20l3.py', 'edit_test_f20l3.py', 'edit_sens_f20l3.py',
         'test_new_section.py', 'test_add_section.py', 'gen_refs.py', 'f20l3_seal_body.md',
         'm6_f20l3.py', 'go_f20l3.sh', 'launch_f20l3.sh', 'wait_f20l3.sh', 'post_f20l3.sh', 'guard_f20l3.py', 'queue_f20l3.py',
         'enter_scene.py', 'runchk_f20l3.py', 'procload.py', 'manifest_fs4c.py', 'sheet142.py', 'gates_default.txt', 'watch_f20l3.py', 'idle142.py',
         'run_safety99.py', 'launch_run.py', 'test_guard_f20l3.py', 'test_tools_f20l3.py', 'refs_f20l3.py',
         'regress/regress_b32.py', 'test_b32_read.out.txt', 'sens_b32.out.txt', 'test_guard_f20l3.out.txt', 'test_tools_f20l3.out.txt',
         'regress/regress_b32.out.txt', 'refs_f20l3.out.txt', 'C:/kyty/f287/bin/kyty_emulator_2d0c8815.exe',
         'C:/kyty/s288/bin/kyty_emulator_b3cee576.exe', 'C:/kyty/scripts/s51_vidglitch.py']
OUTS = [('test_b32_read.out.txt', 'checks '), ('sens_b32.out.txt', 'edits '), ('test_guard_f20l3.out.txt', 'checks '),
        ('test_tools_f20l3.out.txt', 'checks '), ('regress/regress_b32.out.txt', 'REGRESS '), ('refs_f20l3.out.txt', 'refs ')]
HDR = '## 8. \u0421\u0442\u0440\u043e\u043a\u0438 \u043f\u0435\u0447\u0430\u0442\u0438 (sha256 \u0444\u0430\u0439\u043b\u043e\u0432 \u0438 \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0445 \u0432\u044b\u0432\u043e\u0434\u043e\u0432 \u043d\u0430\u0431\u043e\u0440\u043e\u0432)'
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
        allok = 'ALL OK' in lines or 'REGRESS PASS' in lines
        first = lines[0] if lines and lines[0].startswith('suite') else (lines[1] if len(lines) > 1 and lines[1].startswith('suite') else '-')
        out.append('- `%s`: %s; %s; %s: `%s`' % (nm, cnt[-1] if cnt else '-', 'ALL OK' if allok else 'NOT OK', FIRST, first[:160]))
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

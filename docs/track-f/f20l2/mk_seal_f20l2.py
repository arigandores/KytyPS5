"""F20l2 (HPP-648): writes pred/f20l2_seal.md = the body + section 8 (suite counts from the LAST output files, seal lines sha256 path).
Refuses if the seal exists (a seal is written once).  usage: python mk_seal_f20l2.py <body.md>   ASCII output."""
import hashlib
import os
import sys

G = 'C:/kyty/f287/f20l2'
SEAL = G + '/pred/f20l2_seal.md'
FILES = ['b32_read.py', 'f20e_read.py', 'test_b32_read.py', 'sens_b32.py', 'C:/kyty/f287/f20l/b32_base.py',
         'C:/kyty/f287/f20l/base/base_f20l.txt', 'C:/kyty/f287/f20l/base/base_f20l.json', 'C:/kyty/f287/f20l/pred/f20l_seal.md',
         'C:/kyty/f287/bin/kyty_emulator_b9e0ee00.exe', 'C:/kyty/f287/f20l/log_b32_pd.txt', 'C:/kyty/f287/f20l/b32_pd.json',
         'edit_f20l2.py', 'f20l2_seal_body.md',
         'b32_load.py', 'm6_f20l2.py', 'go_f20l2.sh', 'launch_f20l2.sh', 'wait_f20l2.sh', 'post_f20l2.sh', 'guard_f20l2.py', 'queue_f20l2.py',
         'enter_scene.py', 'runchk_f20l2.py', 'procload.py', 'manifest_fs4c.py', 'sheet142.py', 'gates_default.txt', 'watch_f20l2.py', 'idle142.py',
         'run_safety99.py', 'launch_run.py', 'test_guard_f20l2.py', 'test_tools_f20l2.py', 'port_f20l2.py', 'refs_f20l2.py',
         'regress/regress_b32.py', 'test_b32_read.out.txt', 'sens_b32.out.txt', 'test_guard_f20l2.out.txt', 'test_tools_f20l2.out.txt',
         'regress/regress_b32.out.txt', 'refs_f20l2.out.txt', 'C:/kyty/f287/bin/kyty_emulator_2d0c8815.exe',
         'C:/kyty/f287/bin/kyty_emulator_2c9b69b9.exe', 'C:/kyty/s51_vidglitch_path_placeholder']
OUTS = [('test_b32_read.out.txt', 'checks '), ('sens_b32.out.txt', 'edits '), ('test_guard_f20l2.out.txt', 'checks '),
        ('test_tools_f20l2.out.txt', 'checks '), ('regress/regress_b32.out.txt', 'REGRESS '), ('refs_f20l2.out.txt', 'refs ')]


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
    out = ['', '## 8. Строки печати (sha256 файлов и последних выводов наборов)', '']
    for nm, key in OUTS:
        p = os.path.join(G, nm)
        lines = open(p, encoding='ascii', errors='replace').read().splitlines()
        cnt = [x for x in lines if x.startswith(key)]
        allok = 'ALL OK' in lines or 'REGRESS PASS' in lines
        first = lines[0] if lines and lines[0].startswith('suite') else (lines[1] if len(lines) > 1 and lines[1].startswith('suite') else '-')
        out.append('- `%s`: %s; %s; первая строка набора: `%s`' % (nm, cnt[-1] if cnt else '-', 'ALL OK' if allok else 'NOT OK', first[:160]))
    out.append('')
    for nm in FILES:
        if 'placeholder' in nm:
            nm = 'C:/kyty/scripts/s51_vidglitch.py'
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

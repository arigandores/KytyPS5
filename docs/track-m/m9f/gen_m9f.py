"""Track M link M9f (HPP-871; ROADMAP s122 item 785 (v)(5), 788 (d), 789 (e), 791 (d)): copies of the M6c (HPP-850) helpers of the series form
634 / 660 / 661 into C:/kyty/m657/m9f with the names moved (m6c -> m9f, M6C -> M9F, M6c -> M9f, HPP-850 -> HPP-871) and one header line
per code file; data files (gates, sample request) byte for byte.  No change of meaning.  Prints one line per file with the sha256 of the
source and the copy, last line ALL OK.  ASCII only.
usage: python gen_m9f.py [--src C:/kyty/m657/m6c] [--dst C:/kyty/m657/m9f]"""
import hashlib
import os
import sys

CODE = ['procload.py', 'enter_scene.py', 'dispstate.py', 'idle142.py', 'launch_run.py', 'run_safety99.py', 'sheet142.py',
        'manifest_fs4c.py', 'guard_m6c.py', 'hold_m6c.py', 'hostload_m6c.py', 'snap_m6c.py', 'mfsub_m6c.py', 'runchk_m6c.py',
        'tempo_m6c.py', 'watch_m6c.py', 'chk_m6c.sh', 'wait_m6c.sh']
DATA = ['gates_default.txt', 'gates.req', 'sample.req']
SUBS = [(b'm6c', b'm9f'), (b'M6C', b'M9F'), (b'M6c', b'M9f'), (b'HPP-850', b'HPP-871')]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main(argv):
    src = argv[argv.index('--src') + 1] if '--src' in argv else 'C:/kyty/m657/m6c'
    dst = argv[argv.index('--dst') + 1] if '--dst' in argv else 'C:/kyty/m657/m9f'
    ok = True
    for name in CODE + DATA:
        b = open(os.path.join(src, name), 'rb').read()
        out = b
        nn = name
        left = 0
        if name in CODE:
            for a, c in SUBS:
                out = out.replace(a, c)
            left = out.count(b'm6c') + out.count(b'HPP-850')
            nn = name.replace('m6c', 'm9f')
            if name.endswith('.py'):
                hdr = b'# Track M link M9f (HPP-871; ROADMAP s122 item 785 (v)(5)): copy of the M6c (HPP-850) file ' + name.encode() + \
                      b' with the names moved (m6c -> m9f, M6C -> M9F, M6c -> M9f, HPP-850 -> HPP-871); no change of meaning.\n'
                if out.startswith(b'#!'):
                    nl = out.index(b'\n') + 1
                    out = out[:nl] + hdr + out[nl:]
                else:
                    out = hdr + out
            else:
                hdr = b'# Track M link M9f (HPP-871; ROADMAP s122 item 785 (v)(5)): copy of the M6c (HPP-850) file ' + name.encode() + \
                      b' with the names moved (m6c -> m9f, M6C -> M9F, M6c -> M9f, HPP-850 -> HPP-871); no change of meaning.\n'
                nl = out.index(b'\n') + 1
                out = out[:nl] + hdr + out[nl:]
        p = os.path.join(dst, nn)
        if os.path.exists(p):
            print('EXISTS %s - not overwritten' % nn)
            ok = False
            continue
        with open(p, 'wb') as f:
            f.write(out)
        print('%s -> %s src %s copy %s m6c-left %d' % (name, nn, sha(b)[:16], sha(out)[:16], left))
        if left:
            ok = False
    print('ALL OK' if ok else 'FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

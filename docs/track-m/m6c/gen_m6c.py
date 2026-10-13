"""Track M link M6c (HPP-850; ROADMAP s122 item 767 (i), 770, 772 (b), 776): copies of the M3a (HPP-842) helpers of the series form
634 / 660 / 661 into C:/kyty/m657/m6c with the names moved (m3a -> m6c, M3A -> M6C, M3a -> M6c, HPP-842 -> HPP-850) and one header line
per code file; data files (gates, sample request) byte for byte.  No change of meaning.  Prints one line per file with the sha256 of the
source and the copy, last line ALL OK.  ASCII only.
usage: python gen_m6c.py [--src C:/kyty/m657/m3a] [--dst C:/kyty/m657/m6c]"""
import hashlib
import os
import sys

CODE = ['procload.py', 'enter_scene.py', 'dispstate.py', 'idle142.py', 'launch_run.py', 'run_safety99.py', 'sheet142.py',
        'manifest_fs4c.py', 'guard_m3a.py', 'hold_m3a.py', 'hostload_m3a.py', 'snap_m3a.py', 'mfsub_m3a.py', 'runchk_m3a.py',
        'queue_m3a.py', 'tempo_m3a.py', 'watch_m3a.py', 'chk_m3a.sh', 'wait_m3a.sh']
DATA = ['gates_default.txt', 'gates.req', 'sample.req']
SUBS = [(b'm3a', b'm6c'), (b'M3A', b'M6C'), (b'M3a', b'M6c'), (b'HPP-842', b'HPP-850')]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main(argv):
    src = argv[argv.index('--src') + 1] if '--src' in argv else 'C:/kyty/m657/m3a'
    dst = argv[argv.index('--dst') + 1] if '--dst' in argv else 'C:/kyty/m657/m6c'
    ok = True
    for name in CODE + DATA:
        b = open(os.path.join(src, name), 'rb').read()
        out = b
        nn = name
        left = 0
        if name in CODE:
            for a, c in SUBS:
                out = out.replace(a, c)
            left = out.count(b'm3a') + out.count(b'HPP-842')
            nn = name.replace('m3a', 'm6c')
            if name.endswith('.py'):
                hdr = b'# Track M link M6c (HPP-850; ROADMAP s122 item 767 (i)): copy of the M3a (HPP-842) file ' + name.encode() + \
                      b' with the names moved (m3a -> m6c, M3A -> M6C, M3a -> M6c, HPP-842 -> HPP-850); no change of meaning.\n'
                if out.startswith(b'#!'):
                    nl = out.index(b'\n') + 1
                    out = out[:nl] + hdr + out[nl:]
                else:
                    out = hdr + out
            else:
                hdr = b'# Track M link M6c (HPP-850; ROADMAP s122 item 767 (i)): copy of the M3a (HPP-842) file ' + name.encode() + \
                      b' with the names moved (m3a -> m6c, M3A -> M6C, M3a -> M6c, HPP-842 -> HPP-850); no change of meaning.\n'
                nl = out.index(b'\n') + 1
                out = out[:nl] + hdr + out[nl:]
        p = os.path.join(dst, nn)
        if os.path.exists(p):
            print('EXISTS %s - not overwritten' % nn)
            ok = False
            continue
        with open(p, 'wb') as f:
            f.write(out)
        print('%s -> %s src %s copy %s m3a-left %d' % (name, nn, sha(b)[:16], sha(out)[:16], left))
        if left:
            ok = False
    print('ALL OK' if ok else 'FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

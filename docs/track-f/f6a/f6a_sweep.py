# F6a (HPP-372): sweep of session logs 142-144 for 'Unresolved import stub called [' (LOGF form) - symbols per log and level.
# Stream, binary, 16 MB chunks; stops if the sealed-run lock appears between files.
import sys, re, glob, os, collections, time
rx = re.compile(rb'Unresolved import stub called \[\d+\]: [^\n]*?symbol=([^\[\s]+)\[([A-Za-z0-9_]+)_v')
rl = re.compile(rb'Level has started: (\w+)')
files = sorted(glob.glob('C:/kyty/s142/log_*.txt') + glob.glob('C:/kyty/s143/log_*.txt') + glob.glob('C:/kyty/s144/log_*.txt'))
t0 = time.time(); done = 0; hits = 0
print('files %d' % len(files))
for f in files:
    if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
        print('STOPPED before %s (lock or STOP)' % f); break
    c = collections.Counter(); lv = []
    tail = b''
    with open(f, 'rb') as fh:
        while True:
            b = fh.read(1 << 24)
            if not b: break
            b = tail + b
            cut = b.rfind(b'\n') + 1
            tail = b[cut:]; b = b[:cut]
            if b'Unresolved import stub called [' in b:
                for m in rx.finditer(b): c[(m.group(2).decode(), m.group(1).decode())] += 1
            if b'Level has started: ' in b:
                for m in rl.finditer(b):
                    if m.group(1).decode() not in lv: lv.append(m.group(1).decode())
    done += 1
    if c:
        hits += 1
        print('%s levels=%s: %s' % (os.path.basename(f), ','.join(lv), ' '.join('%s/%s=%d' % (k[0], k[1], v) for k, v in sorted(c.items()))))
print('swept %d of %d logs, with stub calls %d, wall %.1f s' % (done, len(files), hits, time.time() - t0))

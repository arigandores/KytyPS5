"""M5a (HPP-845): do the M3 logs (FS15 / MS1, C:/kyty/m657/m3a/log_m3_*.txt) name the programs of the translator themes?
Counts occurrences of each 16-hex program hash (as written in the logs, lower case) per log, streaming in 64 MiB chunks
with overlap; calibration: the T1 programs are expected to appear if the log names translated programs at all.
Read-only; refuses to run under C:/kyty/SEALED_RUN.lock.
Usage: python hashlog_m5a.py [log ...] > hashlog_m5a.out.txt   (default: every log_m3_*.txt)"""
import glob, os, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
H = {
    'T200 vscnt (T1)': ['6216dac0cc17c2d4', '7d20dadcfb430bf1', '86807cd06d68b01e', '8b5e4eced20058a4', '9e3c6093e9c20738',
                        'df445264907dbbff', 'e14b4c0b0d70a885', 'f98cbd05ce2e5627'],
    'T200 vscnt (not T1)': ['77076965e0344358'],
    'T113 glc (T1)': ['03d8402a8c5446ce', '81f39ef20546ebae', 'd97f248195e22298'],
    'T306 sample_o (T1)': ['5a34b303576ee324', 'f47c0c097c598a36'],
    'T306 sample_o (not T1)': ['7b4078750f32db50', 'b912bcf29000558d'],
}
ALL = [h for v in H.values() for h in v]
logs = sys.argv[1:] or sorted(glob.glob('C:/kyty/m657/m3a/log_m3_*.txt'))
CH = 64 << 20
tot = {h: 0 for h in ALL}
nlog = {h: 0 for h in ALL}
for path in logs:
    if os.path.exists('C:/kyty/SEALED_RUN.lock'):
        print('LOCK appeared - exit 3'); sys.exit(3)
    c = {h: 0 for h in ALL}
    keys = [h.encode() for h in ALL]
    with open(path, 'rb') as f:
        tail = b''
        while True:
            b = f.read(CH)
            if not b:
                break
            buf = tail + b
            for h, k in zip(ALL, keys):
                # count matches that start inside the new part (avoid double count of the overlap)
                start = 0
                while True:
                    i = buf.find(k, start)
                    if i < 0:
                        break
                    if i + len(k) > len(tail):
                        c[h] += 1
                    start = i + 1
            tail = buf[-32:]
    for h in ALL:
        tot[h] += c[h]
        nlog[h] += 1 if c[h] else 0
    print(os.path.basename(path), ' '.join('%s=%d' % (h[:8], c[h]) for h in ALL if c[h]) or '(none)')
    sys.stdout.flush()
print()
for grp, hs in H.items():
    for h in hs:
        print('%-24s %s occurrences %d in %d of %d logs' % (grp, h, tot[h], nlog[h], len(logs)))
print('DONE hashlog_m5a')

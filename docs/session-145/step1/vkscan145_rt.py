# Red Team s145 step 1: own recount of every [Vulkan][ line in W logs/stdout of s142-s144.
# Binary streaming, lock check between files. Output: per file severity counts, F6 lines by severity,
# limit lines, distinct message keys by severity (digits -> N).
import os, re, sys, glob, hashlib, collections
LOCK = 'C:/kyty/SEALED_RUN.lock'
NL = b'\n'
files = []
files += sorted(glob.glob('C:/kyty/s144/log_w144_*.txt'))
files += sorted(glob.glob('C:/kyty/s144/stdout_w144_*.txt')) + sorted(glob.glob('C:/kyty/s144/w144_*.stdout.txt'))
files += sorted(glob.glob('C:/kyty/s143/log_w143_*.txt')) + sorted(glob.glob('C:/kyty/s143/stdout_w143_*.txt')) + sorted(glob.glob('C:/kyty/s143/w143_*.stdout.txt'))
files += ['C:/kyty/s142/log_w142.txt'] + sorted(glob.glob('C:/kyty/s142/stdout_w142*.txt')) + sorted(glob.glob('C:/kyty/s142/w142*.stdout.txt'))
F6 = b'and this write is unused'
F6ID = b'ShaderOutputNotConsumed'
LIM = b'last time reporting'
PFX = b'[Vulkan]['
dig = re.compile(rb'[0-9]+')
hexr = re.compile(rb'0x[0-9a-fA-F]+')
keys = collections.Counter()
tot = collections.Counter()
for p in files:
    if os.path.exists(LOCK):
        print('LOCK APPEARED, abort at', p); sys.exit(3)
    if not os.path.exists(p):
        continue
    h = hashlib.sha256()
    sev = collections.Counter(); f6sev = collections.Counter(); f6bare = 0; lim = 0; idhits = 0
    rem = b''
    with open(p, 'rb') as f:
        while True:
            buf = f.read(1 << 26)
            if not buf:
                break
            h.update(buf)
            data = rem + buf
            cut = data.rfind(NL)
            if cut < 0:
                rem = data; continue
            rem = data[cut + 1:]
            data = data[:cut + 1]
            lim += data.count(LIM)
            idhits += data.count(F6ID)
            i = 0
            while True:
                j = data.find(PFX, i)
                if j < 0:
                    break
                e = data.find(NL, j)
                line = data[j:e]
                i = e + 1
                s = line[9:10]
                sev[s] += 1
                if F6 in line:
                    f6sev[s] += 1
                    continue
                k = line.split(b']: ', 1)
                msg = k[1] if len(k) > 1 else line
                msg = hexr.sub(b'H', msg)
                msg = dig.sub(b'N', msg)[:110]
                keys[(s, line[9:14], msg)] += 1
            # F6 text lines without the [Vulkan][ prefix
            f6bare += data.count(F6)
    if rem:
        h.update(b'')
        data = rem
        lim += data.count(LIM); idhits += data.count(F6ID); f6bare += data.count(F6)
        if PFX in data:
            sev[b'?tail'] += 1
    f6tot = sum(f6sev.values())
    print('%s sha=%s vk_lines=%s f6_by_sev=%s f6_without_prefix=%d limit_lines=%d id_string_hits=%d' % (
        p.replace('C:/kyty/', ''), h.hexdigest()[:16],
        dict((k.decode(), v) for k, v in sorted(sev.items())),
        dict((k.decode(), v) for k, v in sorted(f6sev.items())), f6bare - f6tot, lim, idhits))
    sys.stdout.flush()
    for k, v in sev.items():
        tot[k] += v
print('TOTAL vk lines by severity:', dict((k.decode(), v) for k, v in sorted(tot.items())))
print('DISTINCT non-F6 message keys (severity, prefix, normalized text) : count')
for (s, pf, m), v in sorted(keys.items(), key=lambda x: (x[0][0], -x[1])):
    print('  %s %s %6d  %s' % (s.decode(), pf.decode('ascii', 'replace'), v, m.decode('utf-8', 'replace')))
print('files scanned:', sum(1 for p in files if os.path.exists(p)))

"""F14a (HPP-487, ROADMAP s122 item 395(g)(2)): F3 - the CS hashes whose speculative translation fails with
'shader resource tracking' (RESTRACK) or 'speculative translation budget exceeded' (BUDGET): are they still there, and does the
normal path ever request them ('CsPretranslate: miss|hit hash=<h>'), and is there any 'shader CFG build failed' outside a
'CsPretranslate:' line?

Logs: log_*.txt (and log_*.txt.xz) of C:/kyty/s142..s146, C:/kyty/f287/f13a, C:/kyty/f287/fs4c, C:/kyty/f287/f12f with mtime before
the link start (CUTOFF). Streaming with grep -a (fixed strings) per log - no log is read whole into memory:
  pass 1: grep 'CsPretranslate: skipped hash=' -> per-log skipped hashes and class (reason text);
  pass 2: grep -F of the union of RESTRACK/BUDGET hashes + the markers 'shader CFG build failed', 'CsPretranslate: summary',
          'Level has started: ' -> every line with one of those hashes is classified by its prefix.
.xz logs go through 'xz -dc' piped into grep. Writes f14a_f3.tsv (per log), f14a_f3_hashes.tsv, f14a_f3_summary.txt.
ASCII output only. Halts on the lock or STOP before each log.
"""
import calendar
import collections
import glob
import os
import re
import subprocess
import sys
import time

CUTOFF = calendar.timegm(time.strptime('2026-10-03 16:34:59', '%Y-%m-%d %H:%M:%S'))  # UTC link start
DIRS = ['C:/kyty/s142', 'C:/kyty/s143', 'C:/kyty/s144', 'C:/kyty/s145', 'C:/kyty/s146',
        'C:/kyty/f287/f13a', 'C:/kyty/f287/fs4c', 'C:/kyty/f287/f12f']
OUT = 'C:/kyty/f287/f14a'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
GREP = 'C:/Program Files/Git/usr/bin/grep.exe'
XZ = 'C:/Program Files/Git/mingw64/bin/xz.exe'
if not os.path.exists(XZ):
    XZ = 'C:/Program Files/Git/usr/bin/xz.exe'

RE_SK = re.compile(rb'CsPretranslate: skipped hash=([0-9a-f]{16}) reason=(.*)$')
RE_H = re.compile(rb'(?<![0-9a-fA-F])([0-9a-f]{16})(?![0-9a-fA-F])')


def halt_check():
    if os.path.exists(LOCK):
        print('HALT lock')
        sys.exit(3)
    if os.path.exists(STOP):
        print('HALT stop')
        sys.exit(4)


def grep_lines(path, args):
    """Yield matching lines (bytes, without newline) of grep -a <args> over the log (xz streamed)."""
    if path.endswith('.xz'):
        xz = subprocess.Popen([XZ, '-dc', path], stdout=subprocess.PIPE)
        g = subprocess.Popen([GREP, '-a'] + args, stdin=xz.stdout, stdout=subprocess.PIPE)
        xz.stdout.close()
    else:
        xz = None
        g = subprocess.Popen([GREP, '-a'] + args + [path], stdout=subprocess.PIPE)
    for line in g.stdout:
        yield line.rstrip(b'\r\n')
    g.wait()
    if xz:
        xz.wait()


def klass(reason):
    if b'budget exceeded' in reason:
        return 'BUDGET'
    if b'resource tracking' in reason:
        return 'RESTRACK'
    if b'opcode is not implemented' in reason:
        k = re.search(rb'family=(\w+) opcode=(0x\w+)', reason)
        return 'OP_' + (k.group(1) + b'_' + k.group(2)).decode() if k else 'OP'
    return 'OTHER'


logs = []
SEL = sys.argv[1:]
for d in DIRS:
    if SEL and d not in SEL:
        continue
    for p in sorted(glob.glob(d + '/log_*.txt') + glob.glob(d + '/log_*.txt.xz')):
        p = p.replace(chr(92), '/')
        if os.path.getmtime(p) < CUTOFF:
            logs.append(p)

# pass 1
per_log = {}
for p in logs:
    halt_check()
    sk = {}
    for line in grep_lines(p, ['-F', 'CsPretranslate: skipped hash=']):
        m = RE_SK.search(line)
        if m:
            sk[m.group(1)] = klass(m.group(2))
    per_log[p] = {'skipped': sk}
target = set()
for p in logs:
    for h, c in per_log[p]['skipped'].items():
        if c in ('RESTRACK', 'BUDGET'):
            target.add(h)
TAG = ('_' + '_'.join(x.rsplit('/', 1)[1] for x in SEL)) if SEL else ''
pat = OUT + '/f14a_f3_patterns%s.txt' % TAG
with open(pat, 'wb') as f:
    for h in sorted(target):
        f.write(h + b'\n')
    f.write(b'shader CFG build failed\nCsPretranslate: summary\nLevel has started: \nCsPretranslate: miss hash=\nCsPretranslate: hit hash=\n')

# pass 2
SKIP_KINDS = ('CsPretranslate phase begin', 'CsPretranslate phase end', 'CsPretranslate: skipped',
              'CsPretranslate CFG dispatcher fallback', 'CsPretranslate: enqueue skipped')
hash_rows = collections.defaultdict(lambda: collections.Counter())
for p in logs:
    halt_check()
    info = per_log[p]
    tgt = {h for h, c in info['skipped'].items() if c in ('RESTRACK', 'BUDGET')}
    kinds = collections.Counter()
    normal = collections.Counter()   # miss/hit per hash
    first_normal = None
    cfg_fail_outside = 0
    cfg_fail_first = None
    summary = ''
    level = ''
    n = 0
    all_normal = 0
    for line in grep_lines(p, ['-n', '-F', '-f', pat]):
        n += 1
        num, _, body = line.partition(b':')
        if b'Level has started: ' in body:
            v = body.split(b'Level has started: ', 1)[1].strip()
            if v and not level:
                level = v.decode('latin1')
        if b'CsPretranslate: miss hash=' in body or b'CsPretranslate: hit hash=' in body:
            all_normal += 1
        if b'CsPretranslate: summary' in body:
            summary = body.decode('latin1').split('CsPretranslate: ', 1)[1]
        if b'shader CFG build failed' in body and b'CsPretranslate:' not in body:
            cfg_fail_outside += 1
            cfg_fail_first = cfg_fail_first or num.decode()
        hs = {h for h in RE_H.findall(body) if h in tgt}
        if not hs:
            continue
        s = body.decode('latin1')
        kind = None
        for k in SKIP_KINDS:
            if k in s:
                kind = k
                break
        if kind is None:
            if 'CsPretranslate: miss hash=' in s or 'CsPretranslate: hit hash=' in s:
                kind = 'NORMAL ' + ('miss' if ' miss ' in s else 'hit')
                for h in hs:
                    normal[h] += 1
                first_normal = first_normal or (num.decode() + ' ' + s[:160])
            else:
                kind = 'OTHER ' + re.sub(r'[0-9a-f]{16}', '<h>', re.sub(r'\d+', 'X', s))[:80]
        kinds[kind] += len(hs)
        for h in hs:
            hash_rows[h][(kind, p)] += 1
    cls = collections.Counter(info['skipped'].values())
    info.update({'level': level, 'restrack': cls.get('RESTRACK', 0), 'budget': cls.get('BUDGET', 0),
                 'skipped_total': len(info['skipped']), 'normal_lines': sum(normal.values()),
                 'normal_hashes': len(normal), 'all_normal': all_normal, 'first_normal': first_normal or '', 'cfg_fail_outside': cfg_fail_outside,
                 'cfg_fail_first': cfg_fail_first or '', 'kinds': kinds, 'summary': summary,
                 'tgt': tgt})

# outputs
cols = ['log', 'level', 'skipped_total', 'restrack', 'budget', 'all_normal', 'normal_lines', 'normal_hashes', 'cfg_fail_outside',
        'cfg_fail_first', 'first_normal', 'summary']
with open(OUT + '/f14a_f3%s.tsv' % TAG, 'wb') as f:
    f.write(('\t'.join(cols) + '\n').encode('ascii'))
    for p in logs:
        i = per_log[p]
        f.write(('\t'.join([p] + [str(i[c]) for c in cols[1:]]) + '\n').encode('ascii', 'replace'))
all_cls = {}
for p in logs:
    for h, c in per_log[p]['skipped'].items():
        all_cls.setdefault(h, set()).add(c)
with open(OUT + '/f14a_f3_hashes%s.tsv' % TAG, 'wb') as f:
    f.write(b'hash16\tclass\tlogs_skipped\tnormal_lines\tother_kinds\n')
    for h in sorted(target):
        nlogs = sum(1 for p in logs if h in per_log[p]['tgt'])
        nn = sum(v for (k, p), v in hash_rows[h].items() if k.startswith('NORMAL'))
        other = sorted({k for (k, p) in hash_rows[h] if k.startswith('OTHER')})
        f.write(('%s\t%s\t%d\t%d\t%s\n' % (h.decode(), ','.join(sorted(all_cls[h])), nlogs, nn, ' | '.join(other))).encode('ascii', 'replace'))

out = ['F14a F3 summary (HPP-487); logs %d (mtime before 2026-10-03T16:34:59Z)' % len(logs)]
groups = collections.OrderedDict()
for p in logs:
    groups.setdefault(p.rsplit('/', 1)[0], []).append(p)
for g, ps in groups.items():
    prof = collections.Counter((per_log[p]['restrack'], per_log[p]['budget']) for p in ps)
    nl = sum(per_log[p]['normal_lines'] for p in ps)
    cf = sum(per_log[p]['cfg_fail_outside'] for p in ps)
    an = sum(per_log[p]['all_normal'] for p in ps)
    lv = len({per_log[p]['level'] for p in ps if per_log[p]['level']})
    out.append('  %s: logs %d; (RESTRACK, BUDGET) profile %s; levels %d; control: miss/hit lines of any hash %d (logs with >= 1: %d); normal-path miss/hit lines with these hashes %d; '
               "'shader CFG build failed' outside CsPretranslate: %d" % (g, len(ps), dict(prof), lv, an, sum(1 for p in ps if per_log[p]['all_normal']), nl, cf))
tot_kinds = collections.Counter()
for p in logs:
    tot_kinds.update(per_log[p]['kinds'])
out.append('target hashes (union RESTRACK+BUDGET over all logs): %d' % len(target))
out.append('kinds of lines carrying a target hash (hash x line):')
for k, v in sorted(tot_kinds.items(), key=lambda kv: -kv[1]):
    out.append('  %d | %s' % (v, k))
nl_all = sum(per_log[p]['normal_lines'] for p in logs)
cf_all = sum(per_log[p]['cfg_fail_outside'] for p in logs)
out.append('TOTAL normal-path requests (CsPretranslate: miss|hit) of target hashes: %d; shader CFG build failed outside '
           'CsPretranslate: %d; logs without any skipped line: %d' % (nl_all, cf_all,
           sum(1 for p in logs if per_log[p]['skipped_total'] == 0)))
for p in logs:
    if per_log[p]['normal_lines'] or per_log[p]['cfg_fail_outside']:
        out.append('  witness %s: %s | cfg-fail line %s' % (p, per_log[p]['first_normal'], per_log[p]['cfg_fail_first']))
CACHE_TREES = ['C:/kyty/KytyPS5/ps5 em/_ShaderCache', 'C:/kyty/s288/s7/cache_root', 'C:/kyty/s288/snap0']
for tree in CACHE_TREES:
    names = 0
    found = []
    for d, _, fs in os.walk(tree):
        for fn in fs:
            names += 1
            parts = fn.split('_')
            if len(parts) >= 2 and parts[1].encode() in target:
                found.append(os.path.join(d, fn).replace(chr(92), '/'))
    out.append('cache tree %s: file names %d; files of target hashes %d %s' % (tree, names, len(found), ' '.join(found[:10])))
text = '\n'.join(out) + '\n'
open(OUT + '/f14a_f3_summary%s.txt' % TAG, 'wb').write(text.encode('ascii', 'replace'))
sys.stdout.write(text)

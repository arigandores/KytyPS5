# F22a (HPP-576, ROADMAP s122 item 474(e)(3)): the list of logs to sweep, taken from F21a without a new walk of the roots.
# Input: F21a list_f21a.tsv (511 paths of the roots), meta_f21a.jsonl (json of the tag per path), sweep_all.jsonl (sha256
# of the text per path). Distinct logs and classes exactly as ana_f21a.py (KytyPS5 ef4224f4, section 2): group the paths
# by sha256 of the text, take the meta of the first path of the group with a binary_sha256; class 'fixture dir' when every
# path of the group has a component with 'fx', 'no json', 'FS6 not installed', 'other binary', 'KYTY_FIX_B9A=0', 'sample'.
# For each distinct log one path (the first in sorted order) and the stdout files of the same tag next to it
# ('stdout_<tag>.txt', '<tag>.stdout.txt', with or without '.xz').
# Output TSV: path <TAB> size <TAB> class <TAB> binary8 <TAB> sha256 <TAB> stdout paths (';'-joined or '-') <TAB> n copies
# Usage: python sel_f22a.py <f21a dir> <out.tsv>
import collections, json, os, re, sys

src, out = sys.argv[1], sys.argv[2]
COURSE = ['9235a7ac', 'dac02fb9', 'bbad499c', '4aa62e95', '540c035a', '31cbfee8', '631ff987', 'adb0c82f']
FS6 = '9325446c'
FXC = re.compile('/[^/]*fx[^/]*/')  # = ana_f21a.py:41
TAB = chr(9)
meta = {}
for l in open(os.path.join(src, 'meta_f21a.jsonl'), encoding='utf-8'):
    if l.strip():
        m = json.loads(l)
        meta[m['path']] = m
recs = {}
for l in open(os.path.join(src, 'sweep_all.jsonl'), encoding='utf-8'):
    if l.strip():
        r = json.loads(l)
        recs[r['path']] = r
listed = [l.split(TAB)[0] for l in open(os.path.join(src, 'list_f21a.tsv'), encoding='utf-8') if l.strip()]
assert set(listed) == set(recs) == set(meta), 'F21a files disagree'
groups = collections.OrderedDict()
for p in sorted(recs):
    r = recs[p]
    groups.setdefault(r.get('sha256_text') or r['sha256'], []).append(p)


def stdouts(p):
    d, b = os.path.split(p)
    b = b[:-3] if b.endswith('.xz') else b
    if not (b.startswith('log_') and b.endswith('.txt')):
        return []
    tag = b[4:-4]
    res = []
    for n in ('stdout_%s.txt' % tag, '%s.stdout.txt' % tag):
        for x in (n, n + '.xz'):
            q = os.path.join(d, x).replace(chr(92), '/')
            if os.path.exists(q):
                res.append(q)
    return res


cnt = collections.Counter()
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    for sha, paths in groups.items():
        m = None
        for p in paths:
            if meta[p].get('binary_sha256'):
                m = meta[p]
                break
        b = m['binary_sha256'][:8] if m else None
        env = (m.get('env') or {}) if m else {}
        if all(FXC.search(p) for p in paths):
            cls = 'fixture_dir'
        elif m is None:
            cls = 'no_json'
        elif b == FS6:
            cls = 'FS6'
        elif b not in COURSE:
            cls = 'other_binary'
        elif env.get('KYTY_FIX_B9A') == '0':
            cls = 'B9A0'
        else:
            cls = 'sample'
        cnt[cls] += 1
        p = paths[0]
        so = []
        for q in paths:
            so += [x for x in stdouts(q) if x not in so]
        f.write(TAB.join([p, str(recs[p]['size']), cls, b or '-', sha, ';'.join(so) or '-', str(len(paths))]) + chr(10))
print('distinct logs', len(groups), dict(cnt))
print('SEL DONE')

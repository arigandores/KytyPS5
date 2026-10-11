# F47a (HPP-802): map video recordings -> level (-lvl from the log), the first "Level has started:" line (empty name)
# and the first NAMED one (the line KYTY_RD_LEVEL arms on), FrameTrace n right after each, binary sha (<tag>.json).
# Reads each log only up to the first FrameTrace line after the named level start (early stop; at most LIMIT bytes).
# Usage: python map_f47a.py <list.tsv from list_rec_f47a.py> <since UTC, e.g. 2026-10-05T11:39:58Z> > map.tsv
import json, os, re, sys

lst, since = sys.argv[1], sys.argv[2]
EXTRA = ['C:/kyty/s142/rec_c142_02.mp4', 'C:/kyty/s142/rec_c142_03.mp4', 'C:/kyty/s288/s13/rec_u_11.mp4',
         'C:/kyty/f287/f12f/rec_f12_bh.mp4']
RX_N = re.compile(rb'^FrameTrace: n=(\d+) ')
LIMIT = 400 * 1024 * 1024


def log_of(mp4):
    d, b = os.path.split(mp4)
    tag = b[4:-4] if b.startswith('rec_') else b[:-4]
    for c in ('log_%s.txt' % tag, 'log_%s.txt.xz' % tag):
        p = os.path.join(d, c).replace(os.sep, '/')
        if os.path.exists(p):
            return tag, p
    return tag, None


def sha_of(d, tag):
    for c in ('%s.json' % tag, 'runs/%s/run.json' % tag):
        p = os.path.join(d, c)
        if os.path.exists(p):
            try:
                j = json.load(open(p, encoding='utf-8'))
                return j.get('binary_sha256', '')[:8]
            except Exception:
                return 'json?'
    return ''


def scan(logp):
    """-> lvl, n after the first (empty) start line, named start text, n after the named start line."""
    lvl, n_empty, name, n_named = '', '', '', ''
    if logp.endswith('.xz'):
        return 'xz', '', '', ''
    want = None  # 'empty' | 'named': next FrameTrace n goes there
    read = 0
    with open(logp, 'rb') as f:
        for line in f:
            read += len(line)
            if read > LIMIT:
                break
            if not lvl and b'-lvl ' in line:
                m = re.search(rb'-lvl (\S+)', line)
                lvl = m.group(1).decode() if m else ''
            if b'Level has started:' in line:
                text = line.split(b'Level has started:', 1)[1].strip().decode('utf-8', 'replace')
                if text and not name:
                    name, want = text, 'named'
                elif not text and n_empty == '' and want is None:
                    want = 'empty'
                continue
            if want is not None:
                m = RX_N.match(line)
                if m:
                    if want == 'empty':
                        n_empty = m.group(1).decode()
                    else:
                        n_named = m.group(1).decode()
                        break
                    want = None
    return lvl, n_empty, name, n_named


rows = []
for ln in open(lst, encoding='utf-8'):
    t, size, idx, p = ln.rstrip('\n').split('\t')
    if (t >= since and int(size) > 1000000) or p in EXTRA:
        rows.append((t, p, idx))
print('mtime\tmp4\tidx\ttag\tlog\tlvl\tn_after_empty_start\tnamed_start\tn_after_named_start\tsha8')
for t, p, idx in rows:
    tag, logp = log_of(p)
    lvl, ne, nm, nn = scan(logp) if logp else ('nolog', '', '', '')
    print('\t'.join([t, p, idx, tag, logp or '', lvl, ne, nm, nn, sha_of(os.path.dirname(p), tag)]))
    sys.stdout.flush()

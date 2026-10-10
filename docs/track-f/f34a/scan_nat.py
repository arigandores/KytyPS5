"""F34a: scan logs (plain and .xz) for natural start (no -lvl) and InputScript presses.

For each log: read first 3 MiB; classify GuestArgs source; if natural (source=none or no GuestArgs line and
an InputScript line exists), print path, size, first InputScript lines, and 'Level has started' lines in head.
Output: TSV-like lines to stdout.
"""
import glob, lzma, os, re, sys

HEAD = 3 << 20
pats = ['C:/kyty/log*.txt', 'C:/kyty/log*.txt.xz', 'C:/kyty/s*/**/log*.txt', 'C:/kyty/s*/**/log*.txt.xz',
        'C:/kyty/s*/**/_kyty*.txt', 'C:/kyty/s*/**/_kyty*.txt.xz', 'C:/kyty/f287/**/log*.txt', 'C:/kyty/s288/**/log*.txt',
        'C:/kyty/p283/**/log*.txt', 'C:/kyty/play/**/log*.txt']
fs = set()
for p in pats:
    fs.update(glob.glob(p, recursive=True))
fs = sorted(x.replace('\\', '/') for x in fs)
print('FILES', len(fs), flush=True)
rx_args = re.compile(rb'GuestArgs: source=(\S+) argc=(\d+)')
rx_in = re.compile(rb'InputScript: [^\r\n]*')
rx_lvl = re.compile(rb'Level has started: ?([^\r\n]*)')
rx_ver = re.compile(rb'KytyPS5-[0-9-]+-[0-9a-f]+-\d+-g[0-9a-f]+')
for f in fs:
    try:
        if f.endswith('.xz'):
            with lzma.open(f, 'rb') as h:
                b = h.read(HEAD)
        else:
            with open(f, 'rb') as h:
                b = h.read(HEAD)
    except Exception as e:
        print('ERR', f, e, flush=True)
        continue
    m = rx_args.search(b)
    src = m.group(1).decode() if m else '-'
    ins = rx_in.findall(b)
    if src == 'none' or (src == '-' and ins):
        lv = [x.decode('utf-8', 'replace') for x in rx_lvl.findall(b)][:4]
        v = rx_ver.search(b)
        print('NAT\t%s\t%d\tsrc=%s\tver=%s\tin=%d\tlvl=%s' % (f, os.path.getsize(f), src,
              v.group(0).decode() if v else '-', len(ins), '|'.join(lv)), flush=True)
        for x in ins[:6]:
            print('   ', x.decode('utf-8', 'replace'), flush=True)
print('DONE', flush=True)

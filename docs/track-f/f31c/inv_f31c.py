"""F31c (HPP-731; ROADMAP s122 item 667 (g)): recheck of the five inventory entries of 'mini_giants_garden' counted by the lead - per log:
sha256, the entry line 'Level has started: mini_giants_garden', sum dt_us of the FrameTrace frames after it (f31c_read.scan, the definition
of F26a section 3) >= 290 s, '--- Error ---' 0, 'Unhandled host exception' 0, detector 0 (the three strings of item 630 (g)(5)).  An entry
failing the recheck is replaced by a tag of the series (N of the series +1 each - rule of item 667 (g)); the script prints the number of
replacement tags.  Rows (not members): other death markers, frames >= 1 s after the entry, the lead's sum of item 667 (g), the binary of the
json next to the log.  First line names the script with sha256; last line 'INVENTORY 5 of 5 PASS ... ALL OK' or 'INVENTORY k of 5 PASS,
replacement tags 5-k'.  ASCII only.
usage: python inv_f31c.py [--json OUT]"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, '/')
sys.path.insert(0, HERE)
import f31c_read as R  # noqa: E402

INV = [  # log, binary named by item 667 (g), the lead's sum (s)
    ('C:/kyty/s144/log_v144_20.txt', '9235a7ac', 332.7, 'C:/kyty/s144/v144_20.json'),
    ('C:/kyty/f287/fsc/log_fs_g.txt', 'dac02fb9', 332.7, 'C:/kyty/f287/fsc/fs_g.json'),
    ('C:/kyty/s288/s15/log_k_13.txt', '2c9b69b9', 302.5, 'C:/kyty/s288/s15/k_13.json'),
    ('C:/kyty/s288/s18c/log_s18_c13.txt', 'b3cee576', 336.8, 'C:/kyty/s288/s18c/s18_c13.json'),
    ('C:/kyty/s288/s18c/log_s18_e2.txt', 'b3cee576', 332.6, 'C:/kyty/s288/s18c/s18_e2.json'),
]


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''):
            h.update(b)
    return h.hexdigest()


def main(argv):
    print('script inv_f31c.py sha256 %s reader f31c_read.py sha256 %s' % (sha(HERE + '/inv_f31c.py'), sha(HERE + '/f31c_read.py')))
    out = []
    npass = 0
    for log, binname, lead_s, js in INV:
        row = dict(log=log, binary_named=binname, lead_sum_s=lead_s)
        if not os.path.exists(log):
            row.update(passed=False, why='log missing')
            out.append(row)
            print('FAIL %s: log missing' % log)
            continue
        row['sha256'] = sha(log)
        s = R.scan(log, True)
        jb = None
        if os.path.exists(js):
            try:
                jb = (json.load(open(js, encoding='utf-8')).get('binary_sha256') or '')[:8]
            except (OSError, ValueError):
                jb = None
        why = []
        if s['entry_ln'] is None:
            why.append('no entry line')
        if s['sum_us'] < R.SUM_MIN_US:
            why.append('sum %.1f s < 290 s' % (s['sum_us'] / 1e6))
        if s['error_lines']:
            why.append('--- Error --- %d' % s['error_lines'])
        if s['host_exc']:
            why.append('Unhandled host exception %d' % s['host_exc'])
        if sum(s['sig']):
            why.append('detector %s' % s['sig'])
        ok = not why
        npass += ok
        row.update(passed=ok, why=why, entry_line=s['entry_ln'], entries=s['entries'], frames=s['frames'], sum_dt_us=s['sum_us'],
                   sum_dt_s=round(s['sum_us'] / 1e6, 1), max_dt_us=s['max_us'], long_frames=s['long_frames'], death=s['death'],
                   error_lines=s['error_lines'], host_exc=s['host_exc'], detector=s['sig'], json_binary=jb, log_lines=s['lines'])
        out.append(row)
        print('%s %s sha256 %s' % ('PASS' if ok else 'FAIL', log, row['sha256']))
        print('     entry line %s (entries %d); after it frames %d, sum dt %d us = %.1f s (lead %.1f s, diff %+.1f); max dt %d us; frames >= 1 s %d (row)'
              % (s['entry_ln'], s['entries'], s['frames'], s['sum_us'], s['sum_us'] / 1e6, lead_s, s['sum_us'] / 1e6 - lead_s, s['max_us'], s['long_frames']))
        print('     --- Error --- %d; Unhandled host exception %d; detector %d/%d/%d; death markers (row) %s; binary named %s, json %s'
              % (s['error_lines'], s['host_exc'], s['sig'][0], s['sig'][1], s['sig'][2], s['death'] or 0, binname, jb))
        if why:
            print('     why: %s' % '; '.join(why))
    rep = len(INV) - npass
    if '--json' in argv:
        json.dump(dict(rows=out, passed=npass, replacement_tags=rep), open(argv[argv.index('--json') + 1], 'w', encoding='ascii'), indent=1)
    if rep == 0:
        print('INVENTORY %d of %d PASS, replacement tags 0; ALL OK' % (npass, len(INV)))
        return 0
    print('INVENTORY %d of %d PASS, replacement tags %d' % (npass, len(INV), rep))
    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

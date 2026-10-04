"""rc1_real13.py - S13a4 (HPP-553, item 452 (b)): the data of item 446 (b) by the SEALED sc_s13.py functions (scan_s, scan_y,
nopb_data, fmt_nopb) on the real logs of S12c (s12_gw - the empty-set form of k_01; s12_w - the clean form); data only, no
outcome.  Each log streamed in binary mode; its sha256 printed.  ASCII.
    python rc1_real13.py
"""
import hashlib
import importlib.util
import sys

S13 = 'C:/kyty/s288/s13'
spec = importlib.util.spec_from_file_location('sc13', S13 + '/sc_s13.py')
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
VAR = 'variant_fixb26_fixb1b_fixf10'
print('target sc_s13.py sha256 %s' % hashlib.sha256(open(S13 + '/sc_s13.py', 'rb').read()).hexdigest())
for tag in ('s12_gw', 's12_w'):
    lp = 'C:/kyty/s288/s12/log_%s.txt' % tag
    h = hashlib.sha256()
    with open(lp, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''):
            h.update(b)
    s = S.A.scan_s(lp)
    sy = S.scan_y(lp)
    d = S.nopb_data(s, sy, ('-', '-', VAR))
    r = dict(nopb=d, prep_end=dict(ready_line=sy['ready_line']))
    print('%s log %s sha256 %s rows %d ready %s created %s nopb %s' % (tag, lp, h.hexdigest(), len(s['rows']), sy['ready_line'],
                                                                     sy['created_line'], sy['nopb_line']))
    print('%s data of item 446 (b): %s' % (tag, S.fmt_nopb(r)))
sys.stdout.flush()

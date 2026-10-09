# FS11a (HPP-714, ROADMAP s122 item 647(d)(1)): makes run_stand_fs11a.py from C:/kyty/f287/f29c3/run_f29c3.py (= 0db3b3eb's
# runner of the member (e)(1), sealed p0_f29c3.md): one header line, and in arm() the variable KYTY_FIX_B12 is NOT set for the
# "1" arms when the fourth argument is "default" (the default of FS11a: unset = 1); the "0" arms keep KYTY_FIX_B12=0. With the
# fourth argument "explicit" the runner is the F29c3 runner unchanged. Anchors are whole lines.
SRC = 'C:/kyty/f287/f29c3/run_f29c3.py'
DST = 'C:/kyty/f287/fs11a/run_stand_fs11a.py'
lines = open(SRC, 'rb').read().decode('utf-8').replace('\r\n', '\n').split('\n')


def rep(old, new):
    idx = [i for i, l in enumerate(lines) if l == old]
    assert len(idx) == 1, (old, len(idx))
    lines[idx[0]:idx[0] + 1] = new


rep('        env["KYTY_FIX_B12"] = fix',
    ['        if not (FORM == "default" and fix == "1"):',
     '            env["KYTY_FIX_B12"] = fix'])
rep('    exe, iters, out_path = sys.argv[1], sys.argv[2], sys.argv[3]',
    ['    global FORM',
     '    exe, iters, out_path, FORM = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]',
     '    assert FORM in ("default", "explicit"), FORM'])
rep('# Usage: python run_f29d.py <stand.exe> <iters> <out.txt>     exit 0 always; last line "MEMBERS ALL OK" or "MEMBERS FAILED: ..."',
    ['# Usage: python run_stand_fs11a.py <stand.exe> <iters> <out.txt> <default|explicit>   exit 0 always; last line "MEMBERS ALL OK"',
     '# or "MEMBERS FAILED: ..."; default - the "1" arms run without KYTY_FIX_B12 (base_ok then demands fix_b12=1 from the default).'])
lines.insert(0, '# FS11a (HPP-714, ROADMAP s122 item 647(d)(1)): copy of C:/kyty/f287/f29c3/run_f29c3.py made by mk_run_stand_fs11a.py - the')
lines.insert(1, '# fourth argument "default" runs the "1" arms with KYTY_FIX_B12 unset (the default of FS11a). Was:')
idx = [i for i, l in enumerate(lines) if l == 'FORM = None']
assert not idx
imp = [i for i, l in enumerate(lines) if l == 'import sys']
assert len(imp) == 1
lines.insert(imp[0] + 1, '')
lines.insert(imp[0] + 2, 'FORM = None')
open(DST, 'wb').write('\n'.join(lines).encode('utf-8'))
print('written', DST, len(lines))

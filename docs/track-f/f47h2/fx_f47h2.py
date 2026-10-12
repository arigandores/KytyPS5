"""fx_f47h2.py - F47h2 (HPP-829): two reader cases for the review (dt_f47g2.py of F47g2 unchanged, imported).

    python fx_f47h2.py <dir with dt_f47g2.py>

A1 admission (item 742(e)): the flips 700..710 with their shown lines but WITHOUT any "FrameTrace: n=" line -> printed.
A2 the same log with FrameTrace lines but one q missing among them -> printed (control: the member is alive when lines exist).
B1 F3 (item 742(g)(3)) on a buffer: a ring copy hashed, guest now != ring bytes, ggpu=0 -> cmp_buffer printed (the buf
   line has no cpu / maybe field).
B2 the same on the SRT: given ring_copy, gvh != snaph; and fresh ok with same_ud=0 -> cmp_srt printed.
"""
import sys

sys.path.insert(0, sys.argv[1])
import dt_f47g2 as dt  # noqa: E402

lines = dt.fx_flips(700, 710)
no_ft = [l for l in lines if 'FrameTrace: n=' not in l]
ok, out = dt.admission(dt.parse(no_ft), 700, 710)
print('A1 no FrameTrace line at all:', 'ADMISSION OK' if ok else 'ADMISSION FAIL', '|', out[0])
drop = [l for l in lines if not l.startswith('FrameTrace: n=705 ')]
ok2, out2 = dt.admission(dt.parse(drop), 700, 710)
print('A2 FrameTrace n=705 missing:', 'ADMISSION OK' if ok2 else 'ADMISSION FAIL', '|', ' / '.join(out2))
b = {'gh': 'a' * 16, 'ghow': 'map', 'ggpu': '0', 'given': 'ring_copy', 'gvh': 'b' * 16, 'addr': '0x1000'}
print('B1 buffer ring copy != guest now, ggpu=0, no cpu/maybe field:', dt.cmp_buffer(b))
s = {'fresh': 'ok', 'same_srt': '1', 'same_img': '1', 'same_buf': '1', 'same_smp': '1', 'same_ud': '1',
     'given': 'ring_copy', 'gvh': 'c' * 16, 'snaph': 'd' * 16}
print('B2a SRT ring bytes != snapshot:', dt.cmp_srt(s))
s2 = dict(s, gvh='d' * 16, same_ud='0')
print('B2b SRT fresh materialization from guest now differs (same_ud=0):', dt.cmp_srt(s2))
print('rows B1/B2 -> rule (6): a show with any ne -> "DEFECT (6)(1)" (read_rule: `if ne:` before every und)')

# Session 127 audit (HPP-112): rts_bad / rts_chk / rts_bad_noreg over ALL FrameTrace-x rows of the smokes
# s1s127 / s2s127 (rtskip=0|2) and s3s127 (rtskip=0|3), plus RtSkipVerify lines (item 76(z)(3)(a)-(b), 83(a)).
import re

KV = re.compile(rb'(rts_bad|rts_chk|rts_bad_noreg)=(\d+)')
for t in ('s1s127', 's2s127', 's3s127'):
    S = {}; rows = 0; badrows = 0; mm = 0
    for l in open('C:/kyty/s127/log_%s.txt' % t, 'rb'):
        if l.startswith(b'FrameTrace-x: '):
            rows += 1
            d = {k: int(v) for k, v in KV.findall(l)}
            for k, v in d.items(): S[k] = S.get(k, 0) + v
            if d.get(b'rts_bad', 0): badrows += 1
        elif b'RtSkipVerify: MISMATCH' in l:
            mm += 1
    print(t, 'rows', rows, 'rts_bad_rows', badrows, {k.decode(): v for k, v in S.items()}, 'MISMATCH lines', mm)

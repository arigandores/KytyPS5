import re,collections
exec(open('census_f32b.py',encoding='utf-8').read().split('W=[')[0])
for k,rs in rows.items():
    ln,sec,c=rs[-1]
    t=' | '.join(c[1:])
    hits=[w for w in ('остаток','паркуется','не определено','[U]','паркуются','долг') if w in t]
    if hits: print(k,ln,sec,hits)

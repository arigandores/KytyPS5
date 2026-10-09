import sys
src = open('C:/kyty/f287/fs10c/post_fs10c.sh', encoding='ascii').read()
NL = chr(10)
R = [
    ('# Track F link FS10c (HPP-686; port of FS9c post_fs9c.sh and F25m post_f25m.sh): the reading of a made tag outside the lock.  Tags with a\n'
     '# video (fs10_f1, fs10_v): s51_vidglitch.py <rec> 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the reader; fs10_v -\n'
     '# the pair image pair_fs10_v_b36_v.png = the sheet of fs10_v left of the sheet of b36_v (F25m, item 624 (e)(3): the lead sheet beside\n'
     '# b36_v).  Then fs10c_read.py rows and json, the table; then the admission member \'scene tempo\' (item 620 (g)(2), 621; tempo_fs10c.py,\n'
     '# the W form from the dry-run plan of go_fs10c.sh); a tempo other than PASS - a times.txt line and SERIES_STOP (question to the lead).\n',
     '# Track F link F29e (HPP-704; port of FS10c post_fs10c.sh): the reading of a made tag outside the lock.  The tag with a video (b12_v):\n'
     '# s51_vidglitch.py <rec> 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the reader; the pair image\n'
     '# pair_b12_v_fs10_v.png = the sheet of b12_v left of the sheet of fs10_v (FS10c, the same form on FS10 without KYTY_FIX_B12).  Then\n'
     '# f29e_read.py rows and json, the table; then the admission member \'scene tempo\' (item 620 (g)(2), 621; tempo_f29e.py, the W form from\n'
     '# the dry-run plan of go_f29e.sh); a tempo other than PASS - a times.txt line and SERIES_STOP (question to the lead).\n'),
    ('# usage: bash C:/kyty/f287/fs10c/post_fs10c.sh <tag>', '# usage: bash C:/kyty/f287/f29e/post_f29e.sh <tag>'),
    ('T=$1; G=C:/kyty/f287/fs10c; D=$G/runs/$T', 'T=$1; G=C:/kyty/f287/f29e; D=$G/runs/$T'),
    ('  fs10_s[01]|fs10_f1|fs10_v|fs10_w|fs10_s[01]_r[1-3]|fs10_f1_r[1-3]|fs10_v_r[1-3]|fs10_w_r[1-3]) ;;\n  *) echo "usage: post_fs10c.sh <tag>"; exit 2;;',
     '  b12_v|b12_w|b12_v_r[1-3]|b12_w_r[1-3]) ;;\n  *) echo "usage: post_f29e.sh <tag>"; exit 2;;'),
    ('  case "$T" in fs10_v*)', '  case "$T" in b12_v*)'),
    ('-i C:/kyty/f287/f25m/runs/b36_v/sheet_b36_v.png', '-i C:/kyty/f287/fs10c/runs/fs10_v/sheet_fs10_v.png'),
    ('$D/pair_${T}_b36_v.png > $D/pair.txt 2>&1 \\\n        && echo "pair: $D/pair_${T}_b36_v.png (left $T, right b36_v)" >> $D/pair.txt',
     '$D/pair_${T}_fs10_v.png > $D/pair.txt 2>&1 \\\n        && echo "pair: $D/pair_${T}_fs10_v.png (left $T, right fs10_v)" >> $D/pair.txt'),
    ('python fs10c_read.py $T --json $D/read.json', 'python f29e_read.py $T --json $D/read.json'),
    ('python fs10c_read.py --table > $G/table.txt', 'python f29e_read.py --table > $G/table.txt'),
    ('PLAN=$(FS10C_DRYRUN=1 bash $G/go_fs10c.sh $T 2>&1 | head -1)', 'PLAN=$(F29E_DRYRUN=1 bash $G/go_f29e.sh $T 2>&1 | head -1)'),
    ('python tempo_fs10c.py $G/log_$T.txt', 'python tempo_f29e.py $G/log_$T.txt'),
    ('echo "$(u) FS10c post_fs10c $T: read.txt', 'echo "$(u) F29e post_f29e $T: read.txt'),
    ("$(grep -E '^  (ADMISSION|MEMBERS)' $D/read.txt | tr '\\n' ';' | cut -c1-160)",
     "$(grep -E '^  (ADMISSION|MEMBERS|ROW FixB12Stat)' $D/read.txt | tr '\\n' ';' | cut -c1-260)"),
    ('  echo "$(u) FS10c post_fs10c $T: the tempo member is not PASS', '  echo "$(u) F29e post_f29e $T: the tempo member is not PASS'),
]
out = src
for a, b in R:
    c = out.count(a)
    if c != 1:
        print('anchor count %d: %s' % (c, a[:90]))
        sys.exit(1)
    out = out.replace(a, b)
i = out.index('case "$T" in fs10_f1*)')
j = out.index('esac', i) + len('esac') + 1
out = out[:i] + out[j:]
for bad in ('fs10c_read', 'go_fs10c', 'tempo_fs10c', 'FS10C', 'fs10_f1', 'b36_v', 'HPP-686'):
    if bad in out:
        print('left: %s' % bad, [l for l in out.split(NL) if bad in l][:3])
        sys.exit(1)
open(sys.argv[1], 'w', encoding='ascii', newline=NL).write(out)
print('written', len(out))

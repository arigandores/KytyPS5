#!/bin/bash
# F27a (HPP-690, track F): inventory of Day and Night entries after session 122 - offline, read-only.
# Candidates: every *.txt / *.log >= 200 KB under C:/kyty with mtime >= 2026-09-27 01:41 local (the end of dnn122;
# build, KytyPS5 sources, tools, scrub, caches, games skipped) plus the emulator folder logs; the xz-compressed logs of the
# session folders s123..s139 (their mtime is the compression time of HPP-401, so they are taken by folder).
# Each file is searched for the level name; the control counts the files with any "Level has started: " line.
# Usage: bash inv_f27a.sh <work dir>
[ -e C:/kyty/SEALED_RUN.lock ] && exit 3
[ -e C:/kyty/f287/STOP ] && exit 4
W="$1"; D="$(dirname "$0")"
python "$D/cands_f27a.py" "$W/cands.txt" > "$W/cands.out.txt"
python - "$W" <<'EOF'
import re, sys
w = sys.argv[1]
L = [l.strip() for l in open(w + '/cands.txt', encoding='utf-8') if l.strip()]
a = [p for p in L if not p.endswith('.xz')]
b = [p for p in L if p.endswith('.xz') and re.match(r'C:/kyty/s1(2[3-9]|3[0-9])/', p)]
open(w + '/list_plain.txt', 'w', encoding='utf-8', newline='').write('\n'.join(a) + '\n')
open(w + '/list_xz.txt', 'w', encoding='utf-8', newline='').write('\n'.join(b) + '\n')
print('plain', len(a), 'xz s123-s139', len(b))
EOF
tr '\n' '\0' < "$W/list_xz.txt" | xargs -0 rg -z -a -c -F "rotating_level_day_and_night" > "$W/hits_xz.txt"
tr '\n' '\0' < "$W/list_xz.txt" | xargs -0 rg -z -a -c -F "Level has started: " > "$W/ctl_xz.txt"
tr '\n' '\0' < "$W/list_plain.txt" | xargs -0 rg -a -c -F "rotating_level_day_and_night" > "$W/hits_plain.txt"
tr '\n' '\0' < "$W/list_plain.txt" | xargs -0 rg -a -c -F "Level has started: " > "$W/ctl_plain.txt"
echo "hits xz $(wc -l < "$W/hits_xz.txt") ctl xz $(wc -l < "$W/ctl_xz.txt") hits plain $(wc -l < "$W/hits_plain.txt") ctl plain $(wc -l < "$W/ctl_plain.txt")"
sort "$W/hits_xz.txt" "$W/hits_plain.txt"

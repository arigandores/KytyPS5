# F47a2 (HPP-807): steps of item 708(b)(11). Run under watch_f47a2.py; each step is skipped if its output exists.
set -e
S="$(cd "$(dirname "$0")" && pwd)"
A=C:/kyty/KytyPS5/docs/track-f/f47a
cd "$S"
[ -s list_rec.tsv ] || { python $A/list_rec_f47a.py > list_rec.tsv.part && mv -f list_rec.tsv.part list_rec.tsv; }
[ -s map.tsv ] || { python $A/map_f47a.py list_rec.tsv 2026-10-05T11:39:58Z > map.tsv.part && mv -f map.tsv.part map.tsv; }
python sel_f47a2.py map.tsv $A/map.tsv sel
python drive_f47a2.py sel_main.tsv batch_main.tsv
python drive_f47a2.py sel_ts.tsv batch_ts.tsv --hi 1700
echo RUN_F47A2_DONE

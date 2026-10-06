[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCK; exit 3; }
[ -e C:/kyty/f287/STOP ] && { echo STOP; exit 4; }
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
S="$PAPERCLIP_RUN_SCRATCH_DIR"
G="C:/Program Files/Git/cmd/git.exe"
R=C:/kyty/KytyPS5
T=C:/kyty/f287/times.txt
python "$S/refs_f20k4.py" check > "$S/refs_f20k4.txt" || { echo REFS_FAILED; tail -3 "$S/refs_f20k4.txt"; exit 6; }
echo "$(date -u +%FT%TZ) F20k4 HPP-653: refs_f20k4.py check ALL OK (48) $(sha256sum "$S/refs_f20k4.txt" | cut -c1-8)" >> "$T"
mkdir -p C:/kyty/f287/f20k4 "$R/docs/track-f/f20k4"
python - "$S" "$R/docs/track-f/f20k4" C:/kyty/f287/f20k4 <<'PYEOF'
import os, re, sys
s, d1, d2 = sys.argv[1], sys.argv[2], sys.argv[3]
names = ['batch1.sh', 'batch2.sh', 'refs_f20k4.py', 'batch1.out', 'batch2.out', 'loop_9db7938b.out', 'loop_f2307b02.out', 'refs_f20k4.txt', 'finalize.sh']
rx = re.compile(r'C:[\\/]+Users[\\/]+[^\\/\s]+[\\/]+AppData[\\/]+Local[\\/]+Temp[\\/]+[^\\/\s]+', re.I)
for n in names:
    t = open(os.path.join(s, n), 'rb').read().decode('utf-8').replace('\r\n', '\n')
    t = rx.sub('<scratch>', t)
    for d in (d1, d2):
        open(os.path.join(d, n), 'wb').write(t.encode('utf-8'))
print('copied', len(names))
PYEOF
cp "$S/f20k4-review.md" C:/kyty/f287/f20k4/
cp "$S/f20k4-review.md" "$R/docs/track-f/f20k4-review.md"
cat "$S/facts_f20k4.md" >> C:/kyty/f287/FACTS.md
echo "$(date -u +%FT%TZ) F20k4 HPP-653: review docs/track-f/f20k4-review.md written, verdict PASS, RC code 0, notes N1-N6 $(sha256sum "$S/f20k4-review.md" | cut -c1-8)" >> "$T"
echo "$(date -u +%FT%TZ) F20k4 FACTS: section ## F20k4 written" >> "$T"
cd "$R" || exit 5
AN="$("$G" log -1 --format=%an e56c663e)"; AE="$("$G" log -1 --format=%ae e56c663e)"
"$G" add -- docs/track-f/f20k4-review.md docs/track-f/f20k4
"$G" grep -n -P -f C:/kyty/scrub/checks.txt --cached -- docs/track-f/f20k4-review.md docs/track-f/f20k4 && { echo SCRUB_HIT; exit 7; }
printf '%s\n' "track F link F20k4 (HPP-653): Red Team review of F20j4 - KYTY_DIAG_B32 delta 9db7938b..f2307b02 (= main 4371ff4b): verdict PASS, code RC 0; RC1-RC5 of F20k3 closed by code and tests (ROADMAP s122 item 581(e)), loop cover by rt_loopmark on both trees, =0 by code, no re-entry on unlock / BeginWLock, signature 9177b426 and sha256 2d0c8815 checked; items 583(v)(5)-(6) checked; notes N1-N6 (text and reference, no code)" "" "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" > "$S/commit_msg.txt"
GIT_AUTHOR_NAME="$AN" GIT_AUTHOR_EMAIL="$AE" GIT_COMMITTER_NAME="$AN" GIT_COMMITTER_EMAIL="$AE" "$G" commit -q --only -F "$S/commit_msg.txt" -- docs/track-f/f20k4-review.md docs/track-f/f20k4 || { echo COMMIT_FAILED; exit 8; }
H="$("$G" rev-parse --short=8 HEAD)"
echo "$(date -u +%FT%TZ) F20k4 HPP-653: docs commit KytyPS5 $H" >> "$T"
echo "commit $H"
"$G" show --stat HEAD | tail -15

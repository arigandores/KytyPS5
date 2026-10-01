"""Link 1b (HPP-321, ROADMAP item 242 (a), (b), (d)): go143a.sh - the seal 02, the chain Windows pid in the lock line and
for the CPU row, the cache manifests before the lock and after the run, the stale after-manifest, the header.  Each
replacement must hit exactly once; LF and ASCII kept."""
p = 'C:/kyty/s143/go143a.sh'
t = open(p, 'rb').read().decode('ascii')
reps = [
    ("#   BUSY (rc 4) lines carry the process name of the \"procload: busy\" line of go143a.log (item 231 (z)(5)).\n",
     "#   BUSY (rc 4) lines carry the process name of the \"procload: busy\" line of go143a.log (item 231 (z)(5)).\n"
     "# LINK 1b (HPP-321, item 242): the seal is pred/02_sc143.md; the lock line carries the Windows pid of this shell\n"
     "#   (winpid, for lockcheck143.py - the dangling-lock rule of the seal); cachemf143.py writes the manifest of the caches\n"
     "#   (_ShaderCache/PPSA21564, _PipelineCache, %LOCALAPPDATA%/NVIDIA/GLCache: name, size, mtime, sha256) into\n"
     "#   runs143/cache_<tag>.before.json before the lock and runs143/cache_<tag>.after.json after the run, each with a\n"
     "#   step2/times.txt line (sc143.py --summary prints the continuity per adjacent pair of tags); the foreign-CPU row\n"
     "#   gets --chain-pid <winpid> (the chain and its descendants are out of the foreign terms; item 242 (a)).  Step 2\n"
     "#   calls this script only through step2/next_one.sh (detached call + foreground wait, item 242 (d)).\n"),
    ('PRED="pred/01_sc143.md"\n', 'PRED="pred/02_sc143.md"\n'),
    ("lockheld\nunset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA\n",
     "lockheld\nWINPID=\"\"\nread -r WINPID < /proc/$$/winpid 2>/dev/null\nunset KYTY_GATE_SCHEDULE KYTY_GATE_SCHEDULE_ABBA\n"),
    ("cachen) ($CACHE)\" >> $TIMES\nset -o noclobber\n",
     "cachen) ($CACHE)\" >> $TIMES\n"
     "CMB=$(python $ROOT/cachemf143.py $OUT/cache_$T.before.json 2>&1 | tail -1 | tr -d '\\r')\n"
     "echo \"$(date -u +%Y-%m-%dT%H:%M:%SZ) go143a $T cache manifest before the lock: $CMB\" >> $TIMES\n"
     "set -o noclobber\n"),
    ('if ! { echo "go143a.sh $T pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then\n',
     'if ! { echo "go143a.sh $T pid $$ winpid $WINPID started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then\n'),
    ("  FG=$(python $ROOT/fgcpu143.py --since $OUT/fgcpu_$T.a.json 2>&1 | tail -1 | tr -d '\\r')\n",
     "  FG=$(python $ROOT/fgcpu143.py --since $OUT/fgcpu_$T.a.json --chain-pid $WINPID 2>&1 | tail -1 | tr -d '\\r')\n"),
    ("go143a.sh sheet142.py fgcpu143.py $VIDGLITCH | cut",
     "go143a.sh sheet142.py fgcpu143.py cachemf143.py lockcheck143.py $VIDGLITCH | cut"),
    ('"rec_$T.mp4" "rec_$T.mp4.idx" "glitch_$T.txt" "sheet_$T.png" "sheet_$T.txt" "score_$T.txt" "runs143/$T.score.json" \\\n',
     '"rec_$T.mp4" "rec_$T.mp4.idx" "glitch_$T.txt" "sheet_$T.png" "sheet_$T.txt" "score_$T.txt" "runs143/$T.score.json" \\\n'
     '         "runs143/cache_$T.after.json" \\\n'),
    ("cachen) ($CACHE)\" >> $TIMES\nlog \"$T rc=$RC $(tail -1 $T.stdout.txt)\"\n",
     "cachen) ($CACHE)\" >> $TIMES\n"
     "CMA=$(python $ROOT/cachemf143.py $OUT/cache_$T.after.json 2>&1 | tail -1 | tr -d '\\r')\n"
     "echo \"$(date -u +%Y-%m-%dT%H:%M:%SZ) go143a $T cache manifest after the run: $CMA\" >> $TIMES\n"
     "log \"$T rc=$RC $(tail -1 $T.stdout.txt)\"\n"),
    ("cpu < 15; idle142; procload --wait-s 0; stop file?; shader cache count; lock (runs143/lock.log UTC); fgcpu143 --save;",
     "cpu < 15; idle142; procload --wait-s 0; stop file?; shader cache count; cache manifest before (cachemf143); lock with "
     "winpid (runs143/lock.log UTC); fgcpu143 --save;"),
    ("log sha; glitch+sheet ${REC:-none}; $SC --tag $T; restore $BUILD_PINNED; fgcpu143 --since (times.txt row); unlock\"",
     "log sha; cache manifest after (cachemf143); glitch+sheet ${REC:-none}; $SC --tag $T; restore $BUILD_PINNED; "
     "fgcpu143 --since --chain-pid (times.txt row); unlock\""),
]
for a, b in reps:
    n = t.count(a)
    if n != 1:
        raise SystemExit('anchor count %d: %r' % (n, a[:90]))
    t = t.replace(a, b)
t.encode('ascii')
open(p, 'wb').write(t.encode('ascii'))
print('patched %d' % len(reps))

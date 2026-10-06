[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCK; exit 3; }
[ -e C:/kyty/f287/STOP ] && { echo STOP; exit 4; }
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
S="$PAPERCLIP_RUN_SCRATCH_DIR"
cd C:/kyty/KytyPS5 || exit 5
O="$S/batch1.out"
: > "$O"
echo "start $(date -u +%FT%TZ)" >> "$O"
for r in 9db7938b f2307b02; do
  mkdir -p "$S/t_$r"
  git archive $r src | tar -x -C "$S/t_$r"
  python docs/track-f/f20k3/rt_loopmark.py "$S/t_$r/src" > "$S/loop_$r.out"
done
echo "== loopmark diff" >> "$O"
diff "$S/loop_9db7938b.out" "$S/loop_f2307b02.out" >> "$O"
wc -l "$S"/loop_*.out >> "$O"
echo "== sha" >> "$O"
sha256sum C:/kyty/f287/bin/kyty_emulator_2d0c8815.exe >> "$O"
for p in 9177b4267de1fb8bac7d1113afd8733210addfac gf2307b02 emu_join peer_tid= g9db7938b; do
  echo "$p $(grep -c -a -o "$p" C:/kyty/f287/bin/kyty_emulator_2d0c8815.exe)" >> "$O"
done
echo "== shader diff" >> "$O"
git diff --stat 9db7938b f2307b02 -- src/graphics/shader >> "$O"
git grep -n "SHADER_CACHE_EXTRA_FILES" f2307b02 -- '*.txt' '*.cmake' >> "$O"
echo "== BeginH" >> "$O"
git grep -n "BeginH(" f2307b02 -- src ':!src/common/diagB32*' >> "$O"
echo "== g_on writes" >> "$O"
git grep -nE "g_on\s*=[^=]|g_on\.store|g_on = " f2307b02 -- src tests >> "$O"
echo "== TrackedMutex decls" >> "$O"
git grep -nE "TrackedMutex<[^>]*>" f2307b02 -- src | grep -v "diagB32.h" | sed -E 's/^f2307b02://' | awk -F'TrackedMutex<' '{split($2,a,">"); print a[1]}' | sort | uniq -c >> "$O"
git grep -nE "TrackedMutex<[^>]*recursive" f2307b02 -- src >> "$O"
echo "== RecreateSurface/RunOnMainThread" >> "$O"
git grep -nE "RunOnMainThread\(" f2307b02 -- src >> "$O"
echo "== static_assert sizeof in files with TrackedMutex" >> "$O"
for f in $(git grep -l "TrackedMutex" f2307b02 -- src | sed 's/^f2307b02://'); do git grep -n "static_assert(sizeof" f2307b02 -- "$f"; done >> "$O"
echo "== OnFlip ns" >> "$O"
git grep -nE "e\.ns\.store|\.ns\.store" f2307b02 -- src/common/diagB32.cpp >> "$O"
echo "end $(date -u +%FT%TZ)" >> "$O"
echo "$(date -u +%FT%TZ) F20k4 batch1 loopmark/sha/grep $(sha256sum C:/kyty/f287/bin/kyty_emulator_2d0c8815.exe | cut -c1-8)" >> "$S/times_draft.txt"
echo done

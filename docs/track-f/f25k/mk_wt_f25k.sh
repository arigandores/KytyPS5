# F25k (HPP-678, ROADMAP s122 item 613(v)(8)): copy of f25d/mk_wt_f25d.sh, names f25d -> f25k, base 11164d72 (FS9a, source
# of the installed FS9 3861eeea); the 6 commits 0005e11f..35b454c6 (KYTY_DIAG_B32 + the F25 fix of binary B) are
# cherry-picked here in order; the F25k commits are cherry-picked from main later (pick_f25k.sh).
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
SRC=C:/kyty/KytyPS5
WT=C:/kyty/f287/f25k/wt
C=11164d72
cd $SRC
"$G" -c core.autocrlf=false worktree add --detach $WT $C
echo "--- worktree HEAD"
"$G" -C $WT log -1 --format='%H %s' | cut -c1-120
"$G" ls-tree $C 3rdparty/ | while read mode type sha path; do
	[ "$type" = commit ] || continue
	if [ "$path" = 3rdparty/ffmpeg-core ]; then
		rm -rf "$WT/$path"
		"$G" clone -q --shared --no-checkout "$SRC/$path" "$WT/$path"
		"$G" -C "$WT/$path" checkout -q "$sha"
	else
		mkdir -p "$WT/$path"
		"$G" -C "$SRC/$path" archive "$sha" | tar -x -C "$WT/$path"
	fi
	echo "submodule $path $sha"
done
echo "--- cherry-pick 0005e11f..35b454c6"
# AGENT_EMAIL - the agent commit address (set by the caller; masked in this copy)
export GIT_AUTHOR_NAME="Emu Engineer" GIT_AUTHOR_EMAIL="$AGENT_EMAIL" GIT_COMMITTER_NAME="Emu Engineer" GIT_COMMITTER_EMAIL="$AGENT_EMAIL"
for c in $("$G" rev-list --reverse 0005e11f..35b454c6); do
	"$G" -C $WT -c core.autocrlf=false cherry-pick -x $c
	echo "picked $c -> $("$G" -C $WT rev-parse --short=8 HEAD)"
done
"$G" -C $WT log -8 --format='%h %s' | cut -c1-140
echo "--- git status --short (worktree vs its HEAD; 0 = clean)"
"$G" -C $WT status --short --ignore-submodules=all | wc -l
echo "--- CR bytes in src/ (worktree files)"
python - "$WT" <<'PYEOF'
import os, sys
root = os.path.join(sys.argv[1], "src")
n = files = 0
for d, _, fs in os.walk(root):
    for f in fs:
        files += 1
        if b"\r" in open(os.path.join(d, f), "rb").read():
            n += 1
print("files", files, "with CR", n)
PYEOF
echo WT OK

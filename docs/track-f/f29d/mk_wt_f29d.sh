#!/bin/bash
# F29d (HPP-703, Red Team, ROADMAP s122 items 639(e)(3), 641(d), 642): copy of C:/kyty/f287/f29c/mk_wt_f29c.sh with the path
# changed to C:/kyty/f287/f29d; base $1, worktree name $2; optional $3.. - commits cherry-picked after (own commits, fixed
# ident), then the tree is printed. LF as in git, submodules as F29c (git archive of the gitlinks, ffmpeg-core --shared clone).
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
SRC=C:/kyty/KytyPS5
WT=C:/kyty/f287/f29d/$2
C=$1
shift 2
cd $SRC
"$G" -c core.autocrlf=false worktree add --detach $WT $C
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
export GIT_AUTHOR_NAME="Red Team" GIT_AUTHOR_EMAIL=noreply@anthropic.com GIT_COMMITTER_NAME="Red Team" GIT_COMMITTER_EMAIL=noreply@anthropic.com
for p in "$@"; do
	"$G" -C $WT -c core.autocrlf=false cherry-pick "$p" >/dev/null
	echo "cherry-pick $p -> $("$G" -C $WT rev-parse --short=8 HEAD)"
done
echo "--- HEAD tree $("$G" -C $WT rev-parse HEAD^{tree})"
"$G" -C $WT log -4 --format='%h %p %s' | cut -c1-120
echo "--- git status --short (0 = clean)"
"$G" -C $WT status --short --ignore-submodules=all | wc -l
python - "$WT" <<'PYEOF'
import os, sys
root = os.path.join(sys.argv[1], "src")
n = files = 0
for d, _, fs in os.walk(root):
    for f in fs:
        files += 1
        if b"\r" in open(os.path.join(d, f), "rb").read():
            n += 1
print("src files", files, "with CR", n)
PYEOF
echo WT OK

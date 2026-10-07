#!/bin/bash
# FS9b negative control: copy of mk_wt_fs9b.sh, worktree C:/kyty/f287/fs9n/wt on 21db93d1 (FS9 without the FS9a commit).
# FS9b (HPP-672, Red Team, ROADMAP s122 item 604(d)(2)): copy of the FS8b file with fs8b -> fs9b (paths, names); default commit 11164d72.
# FS8b (HPP-566, Red Team, ROADMAP s122 items 467(g)(2), 487(g)(2)): copy of the FS6b file with fs6b -> fs8b; default commit d6ee2dc8 (FS7a worktree; tree = 3904522d + 4 patches, review_git.out.txt).
# FS8b (HPP-556, Red Team, ROADMAP s122 item 454(g)(2)): copy of the F15d file with f15d -> fs8b (paths, names).
# FS8b (HPP-515, Red Team): copy of the F15c file with f15c -> fs8b (paths, names); the stand driver stays docs/track-f/f15c/run_stand_f15c.py.
# FS8b (HPP-514, ROADMAP s122 items 412(v), 410(g)(6)(i)): copy of mk_wt_f14e.sh with the path changed; base - S12a 4d9e8ab7 (the last shipping binary accepted by the lead, installed adb0c82f; p.437), the FS9b commit is cherry-picked after. Was:
# F14e (HPP-505, ROADMAP s122 items 409(v), 415): copy of mk_wt_f12d.sh with the path and the base changed (main 04300c85: B42 4e72289e, F10c 68602c4f, F12d 1833ee28, FS5a c3eb8fe8 are ancestors). Was:
# F12d (HPP-477, ROADMAP s122 item 391(v)-(g)): copy of mk_wt_f11d.sh on main 01c8981b (contains B42 4e72289e and F10c 68602c4f). Was:
# F11d (HPP-466, ROADMAP s122 item 376(v)-(d)): copy of mk_wt_f10c.sh on main b0a18f9d (contains B42 4e72289e and F10c 68602c4f). Was:
# F10c (HPP-451, ROADMAP s122 item 369(b)): copy of mk_wt_fs3a.sh on main 465f0d8e (contains the B42 commits). Was:
# FS3a (HPP-447, ROADMAP s122 item 367(g)(1)): copy of mk_wt_f9e2c.sh on the F9e2c worktree commit 722c5e7f, no cherry-pick
# (the FS3a commit is cherry-picked after the main commit). Was:
# F9e2c (HPP-436, ROADMAP s122 item 357(g)(4)): copy of mk_wt_f9e2b.sh + cherry-pick of the F9e2b worktree commit 0cbaa644.
# Was: F9e2b (HPP-429, ROADMAP s122 item 353(g)(4)): clean detached worktree on 4414e235 (P23 code) + the F9e2 commit 23a0b3f2
# (cherry-pick) for KYTY_FIX_B42 M2c F9e2b; copy of C:/kyty/f287/f9/f9e2/mk_wt_f9e2.sh, itself a copy of
# C:/kyty/p283/p30b/mk_wt_p30b.sh with the base and the path changed: LF as in git
# (core.autocrlf=false), submodules as P23 (git archive of the gitlinks, ffmpeg-core as a local --shared clone).
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
SRC=C:/kyty/KytyPS5
WT=C:/kyty/f287/fs9n/wt
C=${1:-21db93d1}
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
"$G" -C $WT log -4 --format='%H %P %s' | cut -c1-160
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

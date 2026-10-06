#!/bin/bash
# S18a (HPP-642): dry simulation of the cherry-pick chain onto FS8a 302347b4 (object store only: git merge-tree in diff3
# form, a temporary index file, git commit-tree - dangling commits, no worktree). Executor variants of the resolutions:
#   a content conflict in code (context of main commits absent from FS8a): resolve1.py auto keeps the lines the commit adds;
#   a conflict only in docs/ (modify/delete of a document absent from FS8a) - the version of the source commit (the tree
#   git merge-tree leaves). Any other conflict - stop.
# Per commit: patch-id --stable of source and simulated, whole commit and code paths (src tests CMakeLists.txt);
# for an unequal patch-id the diff of the two patches. ASCII only. Usage: sim3.sh <default commit>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
D=C:/kyty/s288/s18a/sim3
rm -rf $D; mkdir -p $D
cd C:/kyty/KytyPS5
export GIT_AUTHOR_NAME=arigandores GIT_AUTHOR_EMAIL=arigandores@users.noreply.github.com GIT_COMMITTER_NAME=arigandores GIT_COMMITTER_EMAIL=arigandores@users.noreply.github.com
CODE="src tests CMakeLists.txt"
H=$("$G" rev-parse 302347b4)
printf 'order\tsource\tsimulated\tconflict\tpid_src_all\tpid_sim_all\teq_all\tpid_src_code\tpid_sim_code\teq_code\n' > $D/table.tsv
n=0
for X in 283a6ef9 29542308 a2fee0d9 9635cb0f 9238a182 5bd93ea1 $1; do
	n=$((n+1))
	OUT=$("$G" -c merge.conflictStyle=diff3 merge-tree --write-tree --name-only --merge-base=$X^ $H $X 2>&1); RC=$?
	T=$(echo "$OUT" | head -1)
	CF=none
	if [ $RC -ne 0 ]; then
		FILES=$(echo "$OUT" | sed -n '2,/^$/p' | grep -v '^$')
		echo "$n $X conflict files: $FILES"
		echo "$OUT" | grep '^CONFLICT'
		CODEF=$(echo "$FILES" | grep -v '^docs/')
		if [ -n "$CODEF" ] && [ -z "$(echo "$OUT" | grep '^CONFLICT' | grep -v '^CONFLICT (content)' | grep -v ' docs/')" ]; then
			CF=content_resolve1
			export GIT_INDEX_FILE=$D/index.tmp
			rm -f $GIT_INDEX_FILE
			"$G" read-tree $T
			for P in $CODEF; do
				B=${n}_$(basename $P)
				"$G" show $T:$P > $D/conf_$B
				python C:/kyty/s288/s18a/resolve1.py $D/conf_$B $D/res_$B auto > $D/resolve_$B.txt || { cat $D/resolve_$B.txt; exit 3; }
				grep -E '^(conflict|mode)' $D/resolve_$B.txt
				O=$("$G" hash-object -w $D/res_$B)
				"$G" update-index --cacheinfo 100644,$O,$P
			done
			T=$("$G" write-tree)
			unset GIT_INDEX_FILE
			rm -f $D/index.tmp
		elif [ -z "$(echo "$FILES" | grep -v '^docs/')" ]; then
			CF=docs_only_theirs
		else
			echo "STOP: conflict outside docs/ with no resolution prepared"; exit 2
		fi
	fi
	C=$("$G" commit-tree $T -p $H -m "sim $X")
	A=$("$G" show $X | "$G" patch-id --stable | cut -c1-40)
	B=$("$G" show $C | "$G" patch-id --stable | cut -c1-40)
	AC=$("$G" show $X -- $CODE | "$G" patch-id --stable | cut -c1-40)
	BC=$("$G" show $C -- $CODE | "$G" patch-id --stable | cut -c1-40)
	E=no; [ "$A" = "$B" ] && E=yes
	EC=no; [ "$AC" = "$BC" ] && EC=yes
	printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' $n $("$G" rev-parse $X) $C $CF $A $B $E $AC $BC $EC >> $D/table.tsv
	if [ $E = no ]; then
		"$G" show --format= $X > $D/patch_src_$n.diff
		"$G" show --format= $C > $D/patch_sim_$n.diff
		diff $D/patch_src_$n.diff $D/patch_sim_$n.diff > $D/patch_diff_$n.txt
		echo "$n $X whole-commit patch diff lines: $(wc -l < $D/patch_diff_$n.txt)"
	fi
	H=$C
done
cat $D/table.tsv
echo "final sim $H"
echo "--- diff --stat 302347b4..final (src tests CMakeLists.txt)"
"$G" diff --stat 302347b4 $H -- $CODE
echo "--- K1(7) diffstat 302347b4..final (lines)"
"$G" diff --stat 302347b4 $H -- src/graphics/shader CMakeLists.txt \
	src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp src/graphics/guest_gpu/gpu_format.h \
	src/graphics/guest_gpu/gpu_defs.h src/graphics/host_gpu/renderer/image/imageInfo.h | wc -l
echo "--- final vs main $1 on the paths of the 7 commits (src tests); main commits in 283a6ef9^..$1 on them outside the 7"
FILES=$(for X in 283a6ef9 29542308 a2fee0d9 9635cb0f 9238a182 5bd93ea1 $1; do "$G" show --format= --name-only $X -- src tests; done | sort -u)
"$G" diff --stat $H $1 -- $FILES
"$G" diff $H $1 -- $FILES > $D/final_vs_main.diff
"$G" log --format='%h %s' 283a6ef9^..$1 -- $FILES | cut -c1-110 | grep -v -E '^(283a6ef|2954230|a2fee0d|9635cb0|9238a18|5bd93ea|fe4b227)'
echo "--- FS8a 302347b4 vs main 283a6ef9^ on the same paths"
"$G" diff --stat 302347b4 283a6ef9^ -- $FILES
echo "$H" > $D/final.txt

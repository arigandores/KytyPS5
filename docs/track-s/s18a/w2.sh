#!/bin/bash
# S18a (HPP-642, ROADMAP s122 items 569(d)(1), 571): clean worktree C:/kyty/s288/s18a/wt from FS8a 302347b4 (worktree
# only - submodules come with the build step w3.sh), cherry-pick from main in the order of the item + the default commit.
# Conflict resolution (item 571(b), executor variant accepted by the lead): a code file - resolve1.py auto (keeps only the
# lines the commit adds; the FS8a side is empty; the base side is a prefix or a suffix of the commit side, else stop);
# a docs/ file - the version of the source commit. Any other state - stop. Check (571(b)(4)): HEAD^{tree} = tree of the
# object-only simulation 2343afbf. ASCII only. Usage: w2.sh <default commit>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/s288/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
D=C:/kyty/s288/s18a
WT=$D/wt
SIM=2343afbf3e04ee8b20cc13aece78087ea2eed1eb
export GIT_AUTHOR_NAME=arigandores GIT_AUTHOR_EMAIL=arigandores@users.noreply.github.com GIT_COMMITTER_NAME=arigandores GIT_COMMITTER_EMAIL=arigandores@users.noreply.github.com
export GIT_EDITOR=true
GW() { "$G" -c core.autocrlf=false -c merge.conflictStyle=diff3 -C $WT "$@"; }
[ -e $WT ] && { echo "worktree exists"; exit 1; }
mkdir -p $D/cp
cd C:/kyty/KytyPS5
"$G" -c core.autocrlf=false worktree add --detach $WT 302347b4 > $D/cp/wt_add.log 2>&1 || { cat $D/cp/wt_add.log; exit 1; }
echo "worktree $WT at $(GW rev-parse HEAD)"
: > $D/picked.tsv
n=0
for X in 283a6ef9 29542308 a2fee0d9 9635cb0f 9238a182 5bd93ea1 $1; do
	n=$((n+1))
	if GW cherry-pick $X > $D/cp/cp_$n.log 2>&1; then
		CF=none
		echo "$n $X clean"
	else
		U=$(GW diff --name-only --diff-filter=U)
		echo "$n $X conflict, unmerged: $U"
		grep '^CONFLICT' $D/cp/cp_$n.log
		[ -n "$U" ] || { echo "STOP: cherry-pick failed without unmerged paths"; cat $D/cp/cp_$n.log; exit 2; }
		CF=
		for P in $U; do
			case $P in
			docs/*)
				GW checkout $X -- $P || exit 2
				GW add -- $P || exit 2
				CF="${CF}docs_source:$P;"
				echo "  $P <- version of $X" ;;
			*)
				B=${n}_$(basename $P)
				cp "$WT/$P" $D/cp/conf_$B
				python $D/resolve1.py $D/cp/conf_$B $D/cp/res_$B auto > $D/cp/resolve_$B.txt || { cat $D/cp/resolve_$B.txt; echo "STOP: resolve1 failed on $P"; exit 3; }
				grep -E '^(mode|conflict)' $D/cp/resolve_$B.txt
				cp $D/cp/res_$B "$WT/$P"
				GW add -- $P || exit 2
				CF="${CF}resolve1:$P;" ;;
			esac
		done
		[ -z "$(GW diff --name-only --diff-filter=U)" ] || { echo "STOP: unmerged left"; exit 2; }
		GW cherry-pick --continue >> $D/cp/cp_$n.log 2>&1 || { echo "STOP: --continue failed"; tail -5 $D/cp/cp_$n.log; exit 2; }
	fi
	printf '%s\t%s\t%s\t%s\n' $n $("$G" rev-parse $X) $(GW rev-parse HEAD) "$CF" >> $D/picked.tsv
done
cat $D/picked.tsv
T=$(GW rev-parse HEAD^{tree})
S=$("$G" rev-parse $SIM^{tree})
echo "HEAD $(GW rev-parse HEAD) tree $T"
echo "sim  $SIM tree $S"
[ "$T" = "$S" ] && echo "TREE = SIM 2343afbf" || echo "TREE DIFFERS FROM SIM"
echo "status lines (0 = clean): $(GW status --short --ignore-submodules=all | wc -l)"
echo W2 DONE

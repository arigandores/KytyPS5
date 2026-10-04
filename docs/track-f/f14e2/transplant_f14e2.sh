#!/bin/bash
# Git copy: the agent e-mail is replaced by <agent email> (privacy check of rule 28); the run used the real one.
# F14e2 (HPP-545, ROADMAP s122 item 443(v)(1)): carry the link commit cde1106c (worktree on 7698f6da) onto main
# without touching foreign uncommitted edits in C:/kyty/KytyPS5 (CMakeLists.txt there has a foreign hunk near line 440).
# A temporary index builds the tree = HEAD of main + the two blobs of cde1106c (checked: HEAD has the same two
# files as 7698f6da), commit-tree with HEAD as parent, update-ref with HEAD as the expected old value (CAS).
# Then the shared index gets the new blobs for exactly these two paths, tests/shaderCfgTests.cpp (no local edit)
# is checked out from the new commit, and the RC1 line is put into the working CMakeLists.txt by a whole-line
# replace (the foreign hunk stays unstaged and unchanged).
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
G="/c/Program Files/Git/cmd/git.exe"
D=C:/kyty/f287/f14e2
SRC_COMMIT=cde1106c4b12f414182231544224c340fafd7801
BASE=7698f6da9edbcc13a9516367c24a4d512f58c771
P1=CMakeLists.txt
P2=tests/shaderCfgTests.cpp
cd C:/kyty/KytyPS5
OLD=$("$G" rev-parse HEAD)
echo "main HEAD before: $OLD"
[ -z "$("$G" diff --name-only $BASE $OLD -- $P1 $P2)" ] || { echo "my paths changed on main since base"; exit 10; }
[ -z "$("$G" diff --cached --name-only)" ] || { echo "shared index has staged changes"; exit 11; }
[ -z "$("$G" diff --name-only -- $P2)" ] || { echo "$P2 has a local edit"; exit 12; }
for p in $P1 $P2; do
	m=$("$G" ls-tree $OLD -- $p | cut -d' ' -f1)
	[ "$m" = 100644 ] || { echo "mode $p $m"; exit 13; }
done
B1=$("$G" rev-parse $SRC_COMMIT:$P1)
B2=$("$G" rev-parse $SRC_COMMIT:$P2)
export GIT_INDEX_FILE=$D/tmp_index
rm -f $GIT_INDEX_FILE
"$G" read-tree $OLD
"$G" update-index --cacheinfo 100644,$B1,$P1
"$G" update-index --cacheinfo 100644,$B2,$P2
TREE=$("$G" write-tree)
unset GIT_INDEX_FILE
rm -f $D/tmp_index
{ "$G" log -1 --format=%B $SRC_COMMIT | sed '/^Co-Authored-By:/,$d'; echo "(cherry picked from commit $SRC_COMMIT)"; echo; echo "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"; } > $D/commit_msg_main.txt
NEW=$(GIT_AUTHOR_NAME="Emu Engineer" GIT_AUTHOR_EMAIL="<agent email>" GIT_COMMITTER_NAME="Emu Engineer" GIT_COMMITTER_EMAIL="<agent email>" "$G" commit-tree $TREE -p $OLD -F $D/commit_msg_main.txt)
"$G" update-ref -m "F14e2: cherry-pick $SRC_COMMIT (temporary index)" refs/heads/main $NEW $OLD
echo "main HEAD after: $("$G" rev-parse HEAD)"
"$G" update-index --cacheinfo 100644,$B1,$P1
"$G" checkout $NEW -- $P2
python - <<'PYEOF'
p = 'C:/kyty/KytyPS5/CMakeLists.txt'
raw = open(p, 'rb').read()
crlf = b'\r\n' in raw
lines = raw.decode('utf-8').replace('\r\n', '\n').split('\n')
old = ('\t\t-D SHADER_CACHE_EXTRA_FILES=${KYTY_SOURCE_DIR}/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp'
       '$<SEMICOLON>${KYTY_SOURCE_DIR}/graphics/guest_gpu/gpu_format.h'
       '$<SEMICOLON>${KYTY_SOURCE_DIR}/graphics/guest_gpu/gpu_defs.h')
new = old + '$<SEMICOLON>${KYTY_SOURCE_DIR}/graphics/host_gpu/renderer/image/imageInfo.h'
hits = [i for i, l in enumerate(lines) if l == old]
assert len(hits) == 1, hits
lines[hits[0]] = new
out = '\n'.join(lines)
if crlf:
    out = out.replace('\n', '\r\n')
open(p, 'wb').write(out.encode('utf-8'))
print('working CMakeLists.txt: RC1 line at %d, crlf %s' % (hits[0] + 1, crlf))
PYEOF
echo "--- git show --stat HEAD"
"$G" show --stat --format='%H %P%n%an <%ae>%n%s' HEAD
echo "--- cached (expect empty)"
"$G" diff --cached --stat
echo "--- working diff of my paths vs new HEAD (expect only the foreign hunk of CMakeLists.txt)"
"$G" diff -- $P1 $P2
echo TRANSPLANT OK

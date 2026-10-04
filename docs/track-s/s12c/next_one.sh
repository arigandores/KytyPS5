#!/bin/bash
# Track S link S12c (HPP-496; ROADMAP s122 items 408 (l), 432) call wrapper - port of C:/kyty/s288/s10/next_one.sh:
# the stop file, the lock, the RETURN_FAILED / IN_ARM guards and the API check first, one times.txt line with the API answer,
# then ONE detached verbatim seal call of pred/08_s.md (call_one.sh) and RETURN (item 324 (i): next_one.sh only starts the call;
# the wait is separate tool commands "bash C:/kyty/s288/s12/wait_one.sh <tag>", each < 540 s, until the rc= line).
# API check (queue P > F > S, item 322 (g)): any OTHER issue of the Harness Engineer in todo/in_progress or with an
# executionRunId (the P and F links that run the game are his) -> yield; other track S links (title 'trek S') do not yield, no new tag; a comment on HPP-496 by another author
# after the last one read (s12/last_comment.txt) -> NO GO until it is read.  ASCII only.  usage: next_one.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
TIMES=C:/kyty/s288/s12/times.txt
case "$T" in
  s12_w|s12_v|s12_gw|s12_gr|s12_v0) ;;
  *) echo "usage: next_one.sh <S12c tag of pred/08_s.md>"; exit 2;;
esac
[ -e C:/kyty/s288/STOP ] && { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) next_one STOP file found before $T: $(head -1 C:/kyty/s288/STOP)" >> $TIMES; echo STOP; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
for G in C:/kyty/s288/s4/RETURN_FAILED C:/kyty/s288/s6/RETURN_FAILED C:/kyty/s288/s10/RETURN_FAILED C:/kyty/s288/s10/IN_ARM C:/kyty/s288/s12/RETURN_FAILED C:/kyty/s288/s12/IN_ARM; do
  [ -e $G ] && { echo "guard $G exists"; exit 1; }
done
grep -q '^rc=' C:/kyty/s288/s12/go_$T.out.txt 2>/dev/null && { echo "s12/go_$T.out.txt holds an rc= line of an earlier call - move it to s12/old first"; exit 2; }
[ -e C:/kyty/s288/s12/go_$T.out.txt ] && { echo "s12/go_$T.out.txt exists without rc= (a call running) - wait with wait_one.sh"; exit 1; }
B="${PAPERCLIP_API_URL%/}"; B="${B%/api}"
LAST=$(head -1 C:/kyty/s288/s12/last_comment.txt 2>/dev/null)
AF=C:/kyty/s288/s12/api_issues.json; CF=C:/kyty/s288/s12/api_comments.json
rm -f $AF $CF
curl -s -m 20 -o $AF -H "Authorization: Bearer $PAPERCLIP_API_KEY" \
  "$B/api/companies/$PAPERCLIP_COMPANY_ID/issues?assigneeAgentId=$PAPERCLIP_AGENT_ID&status=todo,in_progress,blocked"
curl -s -m 20 -o $CF -H "Authorization: Bearer $PAPERCLIP_API_KEY" "$B/api/issues/$PAPERCLIP_TASK_ID/comments"
API=$(python -c "import json,sys
try:
  a = json.load(open('$AF', encoding='utf-8')); c = json.load(open('$CF', encoding='utf-8'))
  a = a if isinstance(a, list) else (a.get('items') or a.get('issues') or [])
  other = [x.get('identifier') + ':' + str(x.get('status')) + (':run' if x.get('executionRunId') else '') for x in a if x.get('identifier') != 'HPP-496' and not (x.get('title') or '').startswith(chr(1090)+chr(1088)+chr(1077)+chr(1082)+' S') and (x.get('status') in ('todo', 'in_progress') or x.get('executionRunId'))]
  same = [x.get('identifier') + ':' + str(x.get('status')) + (':run' if x.get('executionRunId') else '') for x in a if x.get('identifier') != 'HPP-496' and (x.get('title') or '').startswith(chr(1090)+chr(1088)+chr(1077)+chr(1082)+' S') and (x.get('status') in ('todo', 'in_progress') or x.get('executionRunId'))]
  parked = [x.get('identifier') + ':' + str(x.get('status')) for x in a if x.get('identifier') != 'HPP-496' and not (x.get('status') in ('todo', 'in_progress') or x.get('executionRunId'))]
  c = c if isinstance(c, list) else c.get('items', [])
  c = sorted(c, key=lambda x: x['createdAt'])
  ids = [x['id'] for x in c]
  last = '$LAST'
  new = [x['id'][:8] for x in c[(ids.index(last) + 1 if last in ids else 0):] if x.get('authorAgentId') != '$PAPERCLIP_AGENT_ID']
  print('open other issues of the executor: %s; track S links open (no yield, rule 27 bars them under the lock): %s; parked (blocked, no run): %s; HPP-496 comments by others after %s: %d %s' % (','.join(other) or 'none', ','.join(same) or 'none', ','.join(parked) or 'none', last[:8] or '-', len(new), ','.join(new)))
except Exception as e:
  print('API-ERR %s' % type(e).__name__)")
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) next_one API before $T: $API" >> $TIMES
WHY=""
case "$API" in *API-ERR*) WHY="$WHY API error";; esac
case "$API" in *"executor: none;"*) ;; *) WHY="$WHY an open P/F issue of the executor (queue P > F > S)";; esac
case "$API" in *"after "*": 0 "*) ;; *) WHY="$WHY a comment to read first";; esac
if [ -n "$WHY" ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) next_one $T not taken:$WHY" >> $TIMES
  echo "YIELD:$WHY | $API"; exit 5
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) next_one STOP absent, no lock, api GO; call: PLWAIT=540 bash C:/kyty/s288/s12/go_s12.sh $T" >> $TIMES
nohup bash C:/kyty/s288/s12/call_one.sh $T > /dev/null 2>&1 & disown
sleep 3
echo "STARTED $T - wait with: bash C:/kyty/s288/s12/wait_one.sh $T"

#!/bin/bash
# F35b (HPP-756): guard before a command longer than 60 s - lock, STOP, series link HPP-752 (FS12c) executionRunId.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCK; exit 3; }
[ -e C:/kyty/f287/STOP ] && { echo STOP; exit 4; }
B="${PAPERCLIP_API_URL%/}"; B="${B%/api}"
R=$(curl -s -H "Authorization: Bearer $PAPERCLIP_API_KEY" "$B/api/issues/HPP-752" | python -c "import json,sys; d=json.load(sys.stdin); print(d.get('status'), d.get('executionRunId'))")
echo "$(date -u +%FT%TZ) guard HPP-752 $R" >> C:/kyty/f287/f35b/times.txt
case "$R" in
  *None) exit 0 ;;
  *) echo "SERIES $R"; exit 6 ;;
esac

import sys, hashlib
p = 'C:/kyty/m657/m3a2/go_m3a2.sh'
b = open(p, 'rb').read()
old = b'  for d in $DIRS GLCache; do LIVE=$(live_of $d); [ -d "$LIVE" ] && { mv "$LIVE" "$G/$KS.new/$d" || { log "move of live $d into $KS.new failed"; exit 1; }; }; done\n'
new = (b'  # HPP-861 executor change 2026-10-13 (after m3w2_sg_v, m3w2_mg_w: mv of live _ShaderSeeds - Permission denied right after the exit):\n'
       b'  # the same move, retried up to 5 times 3 s apart; no other change (the saved state and every reading are the same).\n'
       b'  mvr() { for k in 1 2 3 4 5; do mv "$1" "$2" 2>>$OUT/mv_retry.txt && { [ $k = 1 ] || log "move of $1 done at try $k"; return 0; }; rm -rf "$2"; sleep 3; done; return 1; }\n'
       b'  for d in $DIRS GLCache; do LIVE=$(live_of $d); [ -d "$LIVE" ] && { mvr "$LIVE" "$G/$KS.new/$d" || { log "move of live $d into $KS.new failed"; exit 1; }; }; done\n')
assert b.count(old) == 1, b.count(old)
nb = b.replace(old, new)
print('old', hashlib.sha256(b).hexdigest())
if len(sys.argv) > 1 and sys.argv[1] == 'apply':
    open(p, 'wb').write(nb)
    print('new', hashlib.sha256(nb).hexdigest())
else:
    print('dry new', hashlib.sha256(nb).hexdigest())

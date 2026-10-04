p = 'go_s13.sh'
t = open(p, encoding='ascii').read()
BS = chr(92)


def rep(a, b, n=1):
    global t
    assert t.count(a) == n, (a, t.count(a))
    t = t.replace(a, b)


TR = "tr -d '" + BS + "r'"
rep("PRED=pred/09_s.md\n", "")
rep('cd "$ROOT" || exit 1\nPLAN=$(python $SC --plan "$T" 2>&1 | ' + TR + ')\n',
    'cd "$ROOT" || exit 1\n'
    '# the seal in force: the edition pred/09b_s.md (09 with the line "installed:" named, a lead item) when it exists, else 09\n'
    'PRED=$(python $SC --seal-path 2>&1 | ' + TR + ')\n'
    'case "$PRED" in\n'
    '  pred/09_s.md|pred/09b_s.md) ;;\n'
    '  *) log0 "go_s13.sh $T refused: the seal path is not pred/09_s.md or pred/09b_s.md ($PRED)"; echo "seal path bad"; exit 1;;\n'
    'esac\n'
    'PLAN=$(python $SC --plan "$T" 2>&1 | ' + TR + ')\n')
open(p, 'w', encoding='ascii', newline='\n').write(t)
print('ok')

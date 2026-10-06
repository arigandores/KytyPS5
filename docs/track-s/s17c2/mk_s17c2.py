"""S17c2 (HPP-640): derived copies of the S17c edition 3 harness files - enter_scene.py with the root moved to C:/kyty/s288/s17c2, and
launch / wait / post / aside scripts with the names, tags and root of S17c2.  Every anchor must match the stated number of times; LF, ASCII."""
import sys

S = 'C:/kyty/s288/s17c/'
D = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s288/s17c2/'
TAGS = 's17c_r3b|s17c_rsb|s17c_ks2|s17c_kn2|s17c_c2h|s17c_n0h|s17c_r3h|s17c_e3h'


def load(name):
    return open(S + name, 'rb').read().decode('ascii').replace('\r\n', '\n')


def edit(s, old, new, count=1):
    n = s.count(old)
    if n != count:
        raise SystemExit('anchor count %d (want %d): %r' % (n, count, old[:80]))
    return s.replace(old, new)


def save(name, s):
    for ch in s:
        if ord(ch) > 127:
            raise SystemExit('non-ASCII in ' + name)
    open(D + name, 'wb').write(s.encode('ascii'))
    print('written', D + name, len(s))


# enter_scene.py
s = load('enter_scene.py')
s = edit(s, "ROOT = pathlib.Path('C:/kyty/s288/s17c')\n", "ROOT = pathlib.Path('C:/kyty/s288/s17c2')\n")
s = '# Track S link S17c2 (HPP-640): the S17c enter_scene.py with ROOT moved to C:/kyty/s288/s17c2 (nothing else changed).\n' + s
save('enter_scene.py', s)

# launch_s17c2.sh
s = load('launch_s17c.sh')
s = edit(s, '# Track S link S17c (HPP-613): ONLY launches', '# Track S link S17c2 (HPP-640; port of S17c launch_s17c.sh): ONLY launches')
s = edit(s, 'go_s17c.sh', 'go_s17c2.sh', 4)
s = edit(s, 'wait_s17c.sh', 'wait_s17c2.sh', 2)
s = edit(s, 'guard_s17c.py', 'guard_s17c2.py', 5)
s = edit(s, 'G=C:/kyty/s288/s17c\n', 'G=C:/kyty/s288/s17c2\n')
s = edit(s, 'case "$T" in s17c_v0|s17c_w0|s17c_c2|s17c_ca|s17c_cc|s17c_n0|s17c_r3|s17c_rs|s17c_e3|s17c_ew|s17c_ks|s17c_kn|s17c_kc) ;;\n',
         'case "$T" in %s) ;;\n' % TAGS)
s = edit(s, 'usage: launch_s17c.sh', 'usage: launch_s17c2.sh')
s = edit(s, 'S17C_DRYRUN', 'S17C2_DRYRUN', 2)
s = edit(s, ' S17c guard (item 534)', ' S17c2 guard (item 534)', 3)
s = edit(s, ' S17c launch_s17c ', ' S17c2 launch_s17c2 ', 2)
s = edit(s, 'moved to s17c/old/', 'moved to s17c2/old/')
save('launch_s17c2.sh', s)

# wait_s17c2.sh
s = load('wait_s17c.sh')
s = edit(s, '# Track S link S17c (HPP-613): foreground wait', '# Track S link S17c2 (HPP-640; port of S17c wait_s17c.sh): foreground wait')
s = edit(s, 'F=C:/kyty/s288/s17c/go_$T.out.txt', 'F=C:/kyty/s288/s17c2/go_$T.out.txt')
save('wait_s17c2.sh', s)

# post_s17c2.sh
s = load('post_s17c.sh')
s = edit(s, '# Track S link S17c (HPP-613): the reading', '# Track S link S17c2 (HPP-640; port of S17c post_s17c.sh): the reading')
s = edit(s, 'T=$1; G=C:/kyty/s288/s17c; D=$G/runs/$T', 'T=$1; G=C:/kyty/s288/s17c2; D=$G/runs/$T')
s = edit(s, '  s17c_v0|s17c_c2|s17c_n0|s17c_e3)\n', '  s17c_c2h|s17c_n0h|s17c_e3h)\n')
s = edit(s, 'python s17c_read.py $T --json', 'python s17c2_read.py $T --json')
s = edit(s, 'python s17c_read.py --table', 'python s17c2_read.py --table')
s = edit(s, ' S17c post_s17c $T', ' S17c2 post_s17c2 $T')
s = edit(s, '# usage: bash C:/kyty/s288/s17c/post_s17c.sh <tag>', '# usage: bash C:/kyty/s288/s17c2/post_s17c2.sh <tag>')
save('post_s17c2.sh', s)

# aside_s17c2.sh (only the reason rep; ed2 does not exist in edition 4)
s = load('aside_s17c.sh')
s = edit(s, 'G=${S17C_ROOT:-C:/kyty/s288/s17c}', 'G=${S17C2_ROOT:-C:/kyty/s288/s17c2}')
s = edit(s, 'case "$T" in s17c_c2|s17c_ca|s17c_cc|s17c_n0|s17c_r3|s17c_rs|s17c_e3|s17c_ew|s17c_ks|s17c_kn|s17c_kc) ;;\n',
         'case "$T" in %s) ;;\n' % TAGS)
s = edit(s, '  s17c_v0|s17c_w0) echo "ASIDE REFUSED $T is carried from edition 2 (item 548 (b))"; exit 2;;\n',
         '  s17c_v0|s17c_w0|s17c_c2|s17c_ca|s17c_cc|s17c_n0|s17c_e3|s17c_ew|s17c_kc) echo "ASIDE REFUSED $T is carried from edition 3 (item 561 (d)(1))"; exit 2;;\n')
s = edit(s, 'case "$WHY" in ed2|rep) ;; *) echo "usage: aside_s17c.sh <tag> ed2|rep"; exit 2;; esac',
         'case "$WHY" in rep) ;; *) echo "usage: aside_s17c2.sh <tag> rep"; exit 2;; esac')
s = edit(s, '  *) echo "usage: aside_s17c.sh <tag> ed2|rep"; exit 2;; esac', '  *) echo "usage: aside_s17c2.sh <tag> rep"; exit 2;; esac')
s = edit(s, ' S17c aside_s17c $T $WHY', ' S17c2 aside_s17c2 $T $WHY')
s = '# Track S link S17c2 (HPP-640): port of S17c aside_s17c.sh - only the reason rep (a NOT_ADMITTED tag of edition 4, one repeat by the same\n# name, item 273 (z)); the ed2 branch is unreachable (the reason is refused before it).\n' + s
save('aside_s17c2.sh', s)

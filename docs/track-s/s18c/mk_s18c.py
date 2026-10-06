"""S18c (HPP-644): derived copies of the S17c2 harness files (C:/kyty/s288/s17c2) - enter_scene.py and guard_s18c.py with the root moved to
C:/kyty/s288/s18c, and launch / wait / post / aside scripts with the names, tags and root of S18c.  Every anchor must match the stated number
of times; LF, ASCII.
usage: python mk_s18c.py [<destination folder with a trailing slash>]"""
import sys

S = 'C:/kyty/s288/s17c2/'
D = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s288/s18c/'
TAGS = '|'.join(['s18_c%02d' % i for i in range(1, 20)] + ['s18_ks', 's18_r', 's18_e1', 's18_e2', 's18_v', 's18_w'])
OLD_TAGS = 's17c_r3b|s17c_rsb|s17c_ks2|s17c_kn2|s17c_c2h|s17c_n0h|s17c_r3h|s17c_e3h'


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
s = edit(s, "ROOT = pathlib.Path('C:/kyty/s288/s17c2')\n", "ROOT = pathlib.Path('C:/kyty/s288/s18c')\n")
s = edit(s, '# Track S link S17c2 (HPP-640): the S17c enter_scene.py with ROOT moved to C:/kyty/s288/s17c2 (nothing else changed).\n',
         '# Track S link S18c (HPP-644): the S17c2 enter_scene.py with ROOT moved to C:/kyty/s288/s18c (nothing else changed).\n')
save('enter_scene.py', s)

# guard_s18c.py
s = load('guard_s17c2.py')
s = edit(s, "G = 'C:/kyty/s288/s17c2'\n", "G = 'C:/kyty/s288/s18c'\n")
s = '# Track S link S18c (HPP-644): guard_s17c2.py with G moved to C:/kyty/s288/s18c (nothing else changed).\n' + s
save('guard_s18c.py', s)

# launch_s18c.sh
s = load('launch_s17c2.sh')
s = edit(s, '# Track S link S17c2 (HPP-640; port of S17c launch_s17c.sh): ONLY launches',
         '# Track S link S18c (HPP-644; port of S17c2 launch_s17c2.sh): ONLY launches')
s = edit(s, 'go_s17c2.sh', 'go_s18c.sh', 4)
s = edit(s, 'wait_s17c2.sh', 'wait_s18c.sh', 2)
s = edit(s, 'guard_s17c2.py', 'guard_s18c.py', 5)
s = edit(s, 'G=C:/kyty/s288/s17c2\n', 'G=C:/kyty/s288/s18c\n')
s = edit(s, 'case "$T" in %s) ;;\n' % OLD_TAGS, 'case "$T" in %s) ;;\n' % TAGS)
s = edit(s, 'usage: launch_s17c2.sh', 'usage: launch_s18c.sh')
s = edit(s, 'S17C2_DRYRUN', 'S18C_DRYRUN', 2)
s = edit(s, ' S17c2 guard (item 534)', ' S18c guard (item 534)', 3)
s = edit(s, ' S17c2 launch_s17c2 ', ' S18c launch_s18c ', 2)
s = edit(s, 'moved to s17c2/old/', 'moved to s18c/old/')
save('launch_s18c.sh', s)

# wait_s18c.sh
s = load('wait_s17c2.sh')
s = edit(s, '# Track S link S17c2 (HPP-640; port of S17c wait_s17c.sh): foreground wait',
         '# Track S link S18c (HPP-644; port of S17c2 wait_s17c2.sh): foreground wait')
s = edit(s, 'F=C:/kyty/s288/s17c2/go_$T.out.txt', 'F=C:/kyty/s288/s18c/go_$T.out.txt')
save('wait_s18c.sh', s)

# post_s18c.sh
s = load('post_s17c2.sh')
s = edit(s, '# Track S link S17c2 (HPP-640; port of S17c post_s17c.sh): the reading',
         '# Track S link S18c (HPP-644; port of S17c2 post_s17c2.sh; the video tags s18_e1, s18_e2, s18_v): the reading')
s = edit(s, 'T=$1; G=C:/kyty/s288/s17c2; D=$G/runs/$T', 'T=$1; G=C:/kyty/s288/s18c; D=$G/runs/$T')
s = edit(s, '  s17c_c2h|s17c_n0h|s17c_e3h)\n', '  s18_e1|s18_e2|s18_v)\n')
s = edit(s, 'python s17c2_read.py $T --json', 'python s18c_read.py $T --json')
s = edit(s, 'python s17c2_read.py --table', 'python s18c_read.py --table')
s = edit(s, ' S17c2 post_s17c2 $T', ' S18c post_s18c $T')
s = edit(s, '# usage: bash C:/kyty/s288/s17c2/post_s17c2.sh <tag>', '# usage: bash C:/kyty/s288/s18c/post_s18c.sh <tag>')
save('post_s18c.sh', s)

# aside_s18c.sh (only the reason rep)
s = load('aside_s17c2.sh')
s = edit(s, 'G=${S17C2_ROOT:-C:/kyty/s288/s17c2}', 'G=${S18C_ROOT:-C:/kyty/s288/s18c}')
s = edit(s, 'case "$T" in %s) ;;\n' % OLD_TAGS, 'case "$T" in %s) ;;\n' % TAGS)
s = edit(s, '  s17c_v0|s17c_w0|s17c_c2|s17c_ca|s17c_cc|s17c_n0|s17c_e3|s17c_ew|s17c_kc) echo "ASIDE REFUSED $T is carried from edition 3 (item 561 (d)(1))"; exit 2;;\n', '')
s = edit(s, '  *) echo "usage: aside_s17c2.sh <tag> rep"; exit 2;; esac', '  *) echo "usage: aside_s18c.sh <tag> rep"; exit 2;; esac')
s = edit(s, 'case "$WHY" in rep) ;; *) echo "usage: aside_s17c2.sh <tag> rep"; exit 2;; esac',
         'case "$WHY" in rep) ;; *) echo "usage: aside_s18c.sh <tag> rep"; exit 2;; esac')
s = edit(s, ' S17c2 aside_s17c2 $T $WHY', ' S18c aside_s18c $T $WHY')
s = edit(s, '# Track S link S17c2 (HPP-640): port of S17c aside_s17c.sh - only the reason rep (a NOT_ADMITTED tag of edition 4, one repeat by the same\n',
         '# Track S link S18c (HPP-644): port of S17c2 aside_s17c2.sh - only the reason rep (a NOT_ADMITTED tag of S18c, one repeat by the same\n')
save('aside_s18c.sh', s)

"""Session 140 step 2 (HPP-268): textual port of the session-137 harness helpers into C:/kyty/s140 (LF, write_bytes).

ROADMAP s122 items 210 (e)(3)-(4), 212 (i), 213 (d); brief docs/next-session-140.md step 2.  Byte copies where nothing
changes: procload.py, launch_run.py, run_safety99.py and gates_base.txt of s137 (573ae9d2..., the base of s136: the knob
string of arm 0 of kp137 - bindlean=0, rtskip=1, rbcen=1 rbslow=0 bindlap=1 pathlap=1 mutsite=1 plkstat=1 - item 210
(e)(3); no new word).  The helpers idle/envchk/hostdev/enter_scene, their suites and the envchk mutant list get
whole-token replacements (the name and the root move from 137 to 140) and their one leading port comment is replaced.
One helper changes its set: CENSUS_TAGS of envchk (the m4baton=0 check of item 168 (v)) becomes EVERY tag of session
140 (pm4s140, pm4c140a..pm4c140d); its suite reads pm4s140 where it read s4cs137 and pm4c140a where it read kp137a (the
prefix stem pm4s1400; the mutant stem_prefix cuts 7 characters - the length of pm4s140, as of s4cs137).  Any anchor
mismatch aborts before anything is written; after writing, every ported file is checked for 137-names left.
"""
import hashlib
import pathlib
import sys

S137 = pathlib.Path('C:/kyty/s137')
ROOT = pathlib.Path('C:/kyty/s140')

BASE_SHA = '573ae9d2f24944c4fa92a14070645e3fe5b21bd6ee3365502e6ba768c0087fbc'
COPIES = ['procload.py', 'launch_run.py', 'run_safety99.py', 'gates_base.txt']
PORTS = [('idle137.py', 'idle140.py'), ('test_idle137.py', 'test_idle140.py'), ('mut_idle137.py', 'mut_idle140.py'),
         ('envchk137.py', 'envchk140.py'), ('test_envchk137.py', 'test_envchk140.py'),
         ('mut_envchk137.py', 'mut_envchk140.py'), ('hostdev137.py', 'hostdev140.py'),
         ('test_hostdev137.py', 'test_hostdev140.py'), ('enter_scene.py', 'enter_scene.py')]
TAGS137 = ("('s4cs137', 'kk137', 's6s137', 'kp137a', 'kp137b', 'kp137c', 'kp137d', 'kp137e', 'kp137f', 'kp137g', "
           "'kp137h')")
TAGS140 = "('pm4s140', 'pm4c140a', 'pm4c140b', 'pm4c140c', 'pm4c140d')"
# applied BEFORE the token replacement (the anchors are written in their 137 form)
PRE = [
    ("CENSUS_TAGS = %s   # s137 (port137.py): every tag of session 137\n" % TAGS137,
     "CENSUS_TAGS = %s   # s140 (port140.py): every tag of session 140\n" % TAGS140, 'envchk137.py'),
    ("      E.CENSUS_TAGS == %s and E.M4 == 'm4baton'" % TAGS137,
     "      E.CENSUS_TAGS == %s and E.M4 == 'm4baton'" % TAGS140, 'test_envchk137.py'),
    ("check('k0 the m4baton tags of item 168 (\u0432) in s137: every tag of session 137;",
     "check('k0 the m4baton tags of item 168 (\u0432) in s140: every tag of session 140;", 'test_envchk137.py'),
    ("    ('m4_tags_no_kp137h', \"CENSUS_TAGS = %s\", \"CENSUS_TAGS = %s\"),\n" % (TAGS137, TAGS137.replace(", 'kp137h'", '')),
     "    ('m4_tags_no_pm4c140d', \"CENSUS_TAGS = %s\", \"CENSUS_TAGS = %s\"),\n" % (TAGS140,
                                                                               TAGS140.replace(", 'pm4c140d'", '')),
     'mut_envchk137.py'),
    ("check('e9 no idle/root of session 136, no idle129 / s129 left in enter_scene', 'idle1' + '36' not in src\n"
     "      and 'C:/kyty/s1' + '36' not in src and 'idle129' not in src and 'C:/kyty/s129' not in src\n",
     "check('e9 no idle/root of session 137, no idle129 / s129 left in enter_scene', 'idle1' + '37' not in src\n"
     "      and 'C:/kyty/s1' + '37' not in src and 'idle129' not in src and 'C:/kyty/s129' not in src\n",
     'test_idle137.py'),
]
TOKENS = [('idle137', 'idle140'), ('envchk137', 'envchk140'), ('hostdev137', 'hostdev140'),
          ('C:/kyty/s137', 'C:/kyty/s140'), ('go137a', 'go140a'), ('session-137', 'session-140'),
          ("'e0 ROOT is s137'", "'e0 ROOT is s140'"), ('port137', 'port140'), ("'s4cs1370'", "'pm4s1400'"),
          ('s4cs1370', 'pm4s1400'), ('s4cs137', 'pm4s140'), ("'kp137a'", "'pm4c140a'"), ('kp137a ', 'pm4c140a ')]
LEAD137 = '# Session 137 step 0 (HPP-250): '
LEAD140 = ('# Session 140 step 2 (HPP-268): the session-137 file of this role with the names moved (port140.py)%s - no '
           'change of meaning.\n')
LEFT = ('idle137', 'envchk137', 'hostdev137', 'C:/kyty/s137', 'go137a', 's4cs137', 'kp137', 'kk137', 's6s137', 'port137')


def port(name, data):
    t = data.decode('utf-8')
    lines = t.split('\n')
    lead = [k for k, l in enumerate(lines[:3]) if l.startswith(LEAD137)]
    if len(lead) != 1:
        sys.exit('ABORT %s: no single lead line' % name)
    extra = '; CENSUS_TAGS = every tag of session 140' if name == 'envchk137.py' else ''
    lines[lead[0]] = LEAD140[:-1] % extra
    t = '\n'.join(lines)
    for old, new, where in PRE:
        if where == name:
            if t.count(old) != 1:
                sys.exit('ABORT %s: anchor count %d for %r' % (name, t.count(old), old[:70]))
            t = t.replace(old, new)
    for old, new in TOKENS:
        t = t.replace(old, new)
    return t.encode('utf-8')


def main():
    if pathlib.Path('C:/kyty/SEALED_RUN.lock').exists():
        sys.exit('ABORT: lock held - not writing')
    if hashlib.sha256((S137 / 'gates_base.txt').read_bytes()).hexdigest() != BASE_SHA:
        sys.exit('ABORT: gates_base.txt of s137 is not %s' % BASE_SHA)
    out = {}
    for n in COPIES:
        out[n] = (S137 / n).read_bytes()
    for src, dst in PORTS:
        out[dst] = port(src, (S137 / src).read_bytes())
    ROOT.mkdir(parents=True, exist_ok=True)
    for n, b in out.items():
        (ROOT / n).write_bytes(b)
    left = []
    for src, dst in PORTS:
        t = (ROOT / dst).read_text(encoding='utf-8')
        for bad in LEFT:
            if bad in t:
                left.append('%s: %s' % (dst, bad))
    for n in sorted(out):
        print('%s %s' % (hashlib.sha256((ROOT / n).read_bytes()).hexdigest(), n))
    print('137-names left: %s' % (left or 'none'))
    return 1 if left else 0


if __name__ == '__main__':
    sys.exit(main())

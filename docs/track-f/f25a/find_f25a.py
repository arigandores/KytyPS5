"""Track F link F25a (HPP-660): the search for every tag of pot_treasure_cave / bonus_path_maker_mix - every *.json (< 5 MB) under the
first-level directories of C:/kyty except KytyPS5, build, tools, scrub, _cleanup401; a tag json is a dict with 'binary_sha256'; fixture,
worktree and copy directories are listed apart.  Read-only.  ASCII only.

    python find_f25a.py [--out <txt>]
"""
import json
import os
import re
import sys
import time

ROOT = 'C:/kyty'
SKIP_TOP = ('KytyPS5', 'build', 'tools', 'scrub', '_cleanup401')
LEVELS = (b'pot_treasure_cave', b'bonus_path_maker_mix')
FIXT = re.compile(r'(fx|/wt/|/orig/|/mut|/test_|/fixt|/work_|/api/|/pre\d+/)')


def main(argv):
    t0 = time.time()
    files = 0
    tags, other = [], []
    for top in sorted(os.listdir(ROOT)):
        d = os.path.join(ROOT, top)
        if not os.path.isdir(d) or top in SKIP_TOP:
            continue
        for dp, _, fn in os.walk(d):
            for f in fn:
                if not f.endswith('.json'):
                    continue
                p = os.path.join(dp, f).replace(chr(92), '/')
                try:
                    if os.path.getsize(p) > 5000000:
                        continue
                    b = open(p, 'rb').read()
                except OSError:
                    continue
                files += 1
                if not any(lv in b for lv in LEVELS):
                    continue
                try:
                    j = json.loads(b.decode('utf-8', 'replace'))
                except ValueError:
                    j = None
                if isinstance(j, dict) and 'binary_sha256' in j and not FIXT.search(p):
                    cmd = j.get('cmdline') or []
                    val = [cmd[i + 1] for i, a in enumerate(cmd) if a == '--vulkan-validation' and i + 1 < len(cmd)]
                    ga = j.get('guest_args') or (j.get('env') or {}).get('KYTY_GUEST_ARGS')
                    tags.append('%s %s %s val=%s hold_s=%s %s' % (time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime(os.path.getmtime(p))),
                                                                 (j.get('binary_sha256') or '')[:8], ga, (val or ['-'])[-1], j.get('hold_s'), p))
                else:
                    other.append(p)
    out = ['find_f25a: json files read %d in %.1f s' % (files, time.time() - t0), 'TAG JSON (binary_sha256, outside fixture dirs): %d' % len(tags)]
    out += ['  ' + t for t in sorted(tags)]
    out.append('OTHER json with a level name (fixtures, copies, score, api, lists): %d' % len(other))
    txt = '\n'.join(out) + '\n'
    if '--out' in argv:
        open(argv[argv.index('--out') + 1], 'w', encoding='ascii', errors='replace', newline='\n').write(txt)
    sys.stdout.write(txt)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

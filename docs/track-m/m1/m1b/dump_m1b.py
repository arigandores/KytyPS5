# M1b: dump themes of a class from upstream_detail.tsv, splitting out "trivially out of scope" (all files launcher/CI/docs/non-Windows).
# Usage: python dump_m1b.py <class> [trivial|rest|all]
import csv, sys, collections, re
D = 'docs/track-m/m1/'
cls = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else 'rest'
with open(D + 'upstream_detail.tsv', encoding='utf-8', newline='') as f:
    rows = list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
with open(D + 'upstream.tsv', encoding='utf-8', newline='') as f:
    files = {r['sha']: r['файлы'] for r in csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)}
TRIV = re.compile(r'^(src/launcher/|\.github/|docs/|README|LICENSE|\.gitignore|\.clang|scripts/|tools/|packaging/|flatpak|dist/|.*\.md$|.*linux.*|.*macos.*|.*apple.*|.*/posix/|.*\.desktop$|.*\.png$|.*\.ico$|.*\.svg$|.*\.qrc$|.*\.ui$|.*\.ts$)', re.I)
th = collections.OrderedDict()
for r in rows:
    if r['класс'] != cls:
        continue
    th.setdefault(r['тема'], []).append(r)
ntriv = 0
for t, rs in th.items():
    fl = set()
    for r in rs:
        fl |= set(x for x in files[r['sha']].split(';') if x and x != '-')
    triv = bool(fl) and all(TRIV.match(x) for x in fl)
    ntriv += triv
    if (mode == 'trivial') != triv and mode != 'all':
        continue
    dirs = collections.Counter('/'.join(x.split('/')[:3]) for x in fl)
    print(f"== {t} {rs[0]['ключ']} n={len(rs)} ув={','.join(sorted(set(r['увер'] for r in rs)))} подп={rs[0]['подпись']} knobhunk={rs[0]['наши_ханки_ручек_задеты']}")
    print('   dirs:', '; '.join(f'{k}({v})' for k, v in dirs.most_common(6)))
    for r in rs:
        print(f"   {r['sha'][:9]} {r['заголовок'][:110]}")
        if mode != 'trivial':
            print(f"      суть: {r['суть'][:260]}")
            print(f"      довод: {r['довод_ASTRO'][:400]}")
print('themes', len(th), 'trivial', ntriv, file=sys.stderr)

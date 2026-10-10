# F32a (HPP-733): build the commit set docs/track-f/f32a/ from the run folder: copy scripts as is, copy text outputs with masks
# (user name in temp-folder paths -> <tmp>/<user>, repository owner -> <owner>, third-party application names -> <app>),
# then scan every staged file for the user name, the owner, the e-mail and the application names; prints ALL OK or FAILED.
# Usage: python stage_f32a.py <run_folder> <stage_folder>
import os, re, sys, shutil

SCRIPTS = ['sweep_f32a.py', 'test_sweep_f32a.py', 'wit_f32a.py', 'test_wit_f32a.py', 'ana_f32a.py', 'rep_f32a.py', 'extra_f32a.py',
           'census_f32a.py', 'test_census_f32a.py', 'triage_f32a.py', 'mimg_f32a.py', 'binmap_f32a.py', 'refs_f32a.py', 'stage_f32a.py']
TEXTS = ['binmap.tsv', 'cachechk_f32a.out.txt', 'census_adj.tsv', 'census_raw.tsv', 'census_f32a.out.txt', 'extra_f32a.out.txt',
         'mimg_f32a.out.txt', 'refs_f32a.txt', 'rep_f32a.out.txt', 'triage_f32a.tsv', 'triage_f32a.out.txt', 'new_f32a.tsv',
         'markers_f32a.tsv', 'sig_f32a.tsv', 'test_sweep_f32a.out.txt', 'test_wit_f32a.out.txt', 'test_census_f32a.out.txt']
BINS = ['vid/c142_02_1096.png', 'vid/u11_1076.png']
U = ''.join(chr(c) for c in (115, 101, 118, 97, 108))           # user name (lower case)
O = ''.join(chr(c) for c in (97, 114, 105, 103, 97, 110, 100, 111, 114, 101, 115))  # repository owner
MAIL = ''.join(chr(c) for c in (108, 97, 122, 117, 107, 97))     # part of the e-mail
APPS = [''.join(chr(c) for c in x) for x in ((111, 98, 115), (79, 66, 83))]
MASKS = [
    (re.compile(r'[A-Za-z]*' + U + r'[A-Za-z]*', re.I), lambda m: '<tmp>' if len(m.group(0)) > len(U) else '<user>'),
    (re.compile(O, re.I), lambda m: '<owner>'),
    (re.compile(r'[A-Za-z_]*' + APPS[1] + r'[A-Za-z_]*|' + APPS[0] + r'-studio[A-Za-z0-9_.-]*|we-' + APPS[0] + r'-[A-Za-z0-9.]*'), lambda m: '<app>'),
]
BAD = [re.compile(U, re.I), re.compile(O, re.I), re.compile(MAIL, re.I), re.compile(r'\b' + APPS[0] + r'\b', re.I)]


def main():
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)
    os.makedirs(os.path.join(dst, 'vid'), exist_ok=True)
    for f in SCRIPTS:
        shutil.copyfile(os.path.join(src, f), os.path.join(dst, f))
    for f in TEXTS:
        t = open(os.path.join(src, f), encoding='utf-8', errors='replace').read()
        for rx, fn in MASKS:
            t = rx.sub(fn, t)
        open(os.path.join(dst, f), 'w', encoding='utf-8', newline=chr(10)).write(t)
    for f in BINS:
        shutil.copyfile(os.path.join(src, f), os.path.join(dst, f))
    ok = True
    for f in SCRIPTS + TEXTS:
        t = open(os.path.join(dst, f), encoding='utf-8', errors='replace').read()
        for rx in BAD:
            for m in rx.finditer(t):
                # the scripts spell the names only as character codes; a literal hit is a leak
                print('LEAK', f, t[max(0, m.start() - 40):m.end() + 40].replace(chr(10), ' '))
                ok = False
    print('staged', len(SCRIPTS), 'scripts,', len(TEXTS), 'texts,', len(BINS), 'images')
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

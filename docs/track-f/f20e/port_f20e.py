"""F20e (HPP-624): port of the F20c harness (seal 2) into C:/kyty/f287/f20e with edits only in the places of ROADMAP item 543 (e):
binary admission (FS8 only), tag names f20_v25..f20_v54, the directory, the stop rule and the summary.  Each edit is an exact
replacement with a count check.  ASCII only."""
import os
import shutil
import sys

S = 'C:/kyty/f287/f20c'
D = 'C:/kyty/f287/f20e'
FS8 = '2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b'
ADB = 'adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421'
FS6 = '9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2'
NL = chr(10)

UNCHANGED = ('procload.py', 'idle142.py', 'launch_run.py', 'manifest_fs4c.py', 'sheet142.py', 'run_safety99.py', 'gates_default.txt')
RENAMED = (('f20c_read.py', 'f20e_read.py'), ('test_f20c_read.py', 'test_f20e_read.py'), ('sens_f20c.py', 'sens_f20e.py'),
           ('test_tools_f20c.py', 'test_tools_f20e.py'), ('go_f20c.sh', 'go_f20e.sh'), ('launch_f20c.sh', 'launch_f20e.sh'),
           ('wait_f20c.sh', 'wait_f20e.sh'), ('post_f20c.sh', 'post_f20e.sh'), ('queue_f20c.py', 'queue_f20e.py'),
           ('watch_f20c.py', 'watch_f20e.py'), ('guard_f20c.py', 'guard_f20e.py'), ('test_guard_f20c.py', 'test_guard_f20e.py'))
OLD_TAGS = 'f20_v0[1-9]|f20_v[12][0-9]|f20_v30'
NEW_TAGS = 'f20_v2[5-9]|f20_v[34][0-9]|f20_v5[0-4]'


def rep(txt, old, new, n=1, name=''):
    c = txt.count(old)
    if c != n:
        print('ANCHOR %s: count %d != %d: %r' % (name, c, n, old[:90]))
        sys.exit(1)
    return txt.replace(old, new)


def generic(txt):
    for a, b in (('f20c', 'f20e'), ('F20c', 'F20e'), ('F20C', 'F20E'), ('HPP-561', 'HPP-624')):
        txt = txt.replace(a, b)
    return txt


def main():
    if os.path.exists(D):
        print('exists', D)
        return 1
    os.makedirs(D + '/pred')
    os.makedirs(D + '/runs')
    for f in UNCHANGED:
        shutil.copy2(S + '/' + f, D + '/' + f)
    out = {}
    for a, b in RENAMED:
        out[b] = generic(open(S + '/' + a, 'rb').read().decode('ascii'))
    # enter_scene.py: only the root (directory) and the pid-file variable name
    es = open(S + '/enter_scene.py', 'rb').read().decode('ascii')
    es = rep(es, "ROOT = pathlib.Path('C:/kyty/f287/f18e')", "ROOT = pathlib.Path('C:/kyty/f287/f20e')  # F20e (HPP-624, item 543 (e)): the directory", 1, 'es root')
    es = rep(es, 'F20C_PIDFILE', 'F20E_PIDFILE', 2, 'es pid')
    es = rep(es, 'guard_f20c.py', 'guard_f20e.py', es.count('guard_f20c.py'), 'es guard')
    out['enter_scene.py'] = es

    # --- go_f20e.sh: binary admission, tags, order
    g = out['go_f20e.sh']
    g = rep(g, '(S12 adb0c82f, or FS6 9325446c after the install by FS6d HPP-558) - nothing is installed.',
            '(FS8 2c9b69b9 installed by FS8d HPP-574, ROADMAP item 545; F20e item 543 (e)) - nothing is installed.', 1, 'go hdr1')
    g = rep(g, 'it must be one of the' + NL + '# two allowed and the same before and after.',
            'it must be FS8 (one binary' + NL + '# of the series, item 543 (e)) and the same before and after.', 1, 'go hdr2')
    g = rep(g, 'Order: f20_vNN starts only when runs/f20_v(NN-1) exists; at most 30 tags (item 462 (g)).',
            'Order: f20_vNN starts only when runs/f20_v(NN-1) exists (f20_v25 first); at most 30 tags f20_v25..f20_v54 (item 543 (e)).',
            1, 'go hdr3')
    g = rep(g, 'go_f20e.sh f20_v01 ... f20_v30', 'go_f20e.sh f20_v25 ... f20_v54', 1, 'go usage')
    g = rep(g, 'ADB=' + ADB + NL + 'FS6=' + FS6 + NL, 'FS8=' + FS8 + NL, 1, 'go bins')
    g = rep(g, '  ' + OLD_TAGS + ') ;;', '  ' + NEW_TAGS + ') ;;', 1, 'go case')
    g = rep(g, 'echo "usage: go_f20e.sh f20_v01..f20_v30"', 'echo "usage: go_f20e.sh f20_v25..f20_v54"', 1, 'go usage2')
    g = rep(g, 'if [ $NN -gt 1 ]; then', 'if [ $NN -gt 25 ]; then', 1, 'go order')
    g = rep(g, '[ "$WANT" = "$ADB" ] || [ "$WANT" = "$FS6" ] || { log "installed binary $WANT is neither adb0c82f nor FS6 9325446c - not starting"; exit 1; }',
            '[ "$WANT" = "$FS8" ] || { log "installed binary $WANT is not FS8 2c9b69b9 - not starting; the series stops until a lead item (item 543 (e))"; exit 1; }',
            1, 'go want')
    out['go_f20e.sh'] = g

    # --- launch / post: tags
    for nm in ('launch_f20e.sh', 'post_f20e.sh'):
        t = out[nm]
        t = rep(t, 'in ' + OLD_TAGS + ') ;;', 'in ' + NEW_TAGS + ') ;;', 1, nm + ' case')
        t = rep(t, 'f20_v01..f20_v30"', 'f20_v25..f20_v54"', 1, nm + ' usage')
        out[nm] = t
    out['post_f20e.sh'] = rep(out['post_f20e.sh'], 'post_f20e.sh f20_vNN', 'post_f20e.sh f20_vNN (f20_v25..f20_v54)', 1, 'post hdr')

    # --- reader: admission, base, stop rule, summary
    r = out['f20e_read.py']
    r = rep(r, '"""Track F link F20e (HPP-624; ROADMAP s122 item 462 (g)-(d), item 451 (e)): the reader of the V Sky Garden series for B2 and B32.',
            '"""Track F link F20e (HPP-624; ROADMAP s122 item 543 (e); port of the F20c reader, item 462 (g)-(d), item 451 (e)): the reader of\n'
            'the V Sky Garden series F20e for B2 and B32.  Edits against F20c: binary admission (FS8 only), the stop rule and the summary of\n'
            'item 543 (e) (B2 base 28 warm, B32 - the F20e series alone); the reading rules of a tag are those of F20c.', 1, 'rd doc1')
    r = rep(r, '    python f20e_read.py --series [--runs <dir>]              the series: F20a base + every read.json of runs/f20_vNN; reading (d)',
            '    python f20e_read.py --series [--runs <dir>]              the series: B2 base 28 + every read.json of runs/f20_vNN; B32 of\n'
            '                                                              F20e alone; the stop rule of item 543 (e)', 1, 'rd doc2')
    r = rep(r, '                   LETTER (main): on adb0c82f and FS6 a cache save is no attribution - the frame goes on to the next member.\n'
            '                   VARIANT F20a (executor variant, printed beside): on adb0c82f / FS6 a frame with a cache save is unattributed.',
            '                   LETTER (main): on adb0c82f, FS6 and FS8 a cache save is no attribution - the frame goes on to the next member.\n'
            '                   VARIANT F20a (executor variant, printed beside): on adb0c82f / FS6 / FS8 a frame with a cache save is unattributed.',
            1, 'rd doc3')
    r = rep(r, 'ADMISSION of a tag (item 462 (g); a failed member = interference, the tag is repeated and is not counted): json binary_sha256 =\n'
            '  adb0c82f or FS6 9325446c; installed before',
            'ADMISSION of a tag (item 462 (g); a failed member = interference, the tag is repeated and is not counted): json binary_sha256 =\n'
            '  FS8 2c9b69b9 (one binary of the series, item 543 (e)); installed before', 1, 'rd doc4')
    r = rep(r, '"""\nimport hashlib',
            'STOP RULE (item 543 (e)): tags go until both hold: (i) B2 warm N = 28 + warm tags of F20e >= 30; (ii) B32 - a hold of F20e with\n'
            '  >= 1 unattributed frame (letter) or 29 holds of F20e without one; at most 30 tags (f20_v25..f20_v54); interference is repeated.\n'
            '"""\nimport hashlib', 1, 'rd doc5')
    r = rep(r, 'TAG_MAX = 30\nBASE = dict(warm=6, b2=0, holds=8, unattr=0, unattr_f20a=0)    # F20a main variant, item 462 (b)-(v)\n',
            'TAG_MAX = 30\nB32_HOLDS = 29\nBASE = dict(warm=28, b2=0)    # B2 base after F20d, item 543 (g): F20a 6 + F20c 22 warm entries, 0 B2 frames\n',
            1, 'rd base')
    r = rep(r, "BIN_OK = {'adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421': 'S12 adb0c82f',\n"
            "          '9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2': 'FS6 9325446c'}\n",
            "BIN_OK = {'" + FS8 + "': 'FS8 2c9b69b9'}\n", 1, 'rd binok')
    r = rep(r, "        ('json binary_sha256 = adb0c82f or FS6 9325446c (%s)' % (BIN_OK.get(jbin) or (jbin or '-')[:16]), jbin in BIN_OK),",
            "        ('json binary_sha256 = FS8 2c9b69b9 (%s)' % (BIN_OK.get(jbin) or (jbin or '-')[:16]), jbin in BIN_OK),", 1, 'rd adm')
    r = rep(r, "def series(results, base=BASE):\n    s = dict(base)\n",
            "def b32_line(n, k, what):\n"
            "    \"\"\"B32 of the F20e series alone (item 543 (e), (zh)): k holds with >= 1 unattributed frame of n holds.\"\"\"\n"
            "    if n == 0:\n"
            "        return '%s: 0 holds' % what\n"
            "    if k >= 1:\n"
            "        return '%s: %d of %d holds, 95 %% CP [%.3f; %.3f]' % (what, k, n, cp(k, n, True), cp(k, n, False))\n"
            "    return '%s: 0 of %d holds (one-sided upper 95 %% %.3f)' % (what, n, 1 - 0.05 ** (1.0 / n))\n"
            "\n\n"
            "def series(results, base=BASE):\n"
            "    s = dict(warm=base['warm'], b2=base['b2'], holds=0, unattr=0, unattr_f20a=0)    # B32: the F20e series alone\n",
            1, 'rd series1')
    r = rep(r, "    out = dict(sum=s, tags=tags, b2=reading(s['warm'], s['b2'], 'B2 (entries with >= 1 B2 frame)'),\n"
            "               b32=reading(s['holds'], s['unattr'], 'B32 Sky Garden (holds with >= 1 unattributed frame, letter)'),\n"
            "               b32_f20a=reading(s['holds'], s['unattr_f20a'], 'B32 Sky Garden (variant F20a)'),\n"
            "               need_more=s['warm'] < N_TARGET and tags['made'] < TAG_MAX)\n",
            "    stop_b2 = s['warm'] >= N_TARGET\n"
            "    stop_b32 = s['unattr'] >= 1 or s['holds'] - s['unattr'] >= B32_HOLDS\n"
            "    out = dict(sum=s, tags=tags, b2=reading(s['warm'], s['b2'], 'B2 (entries with >= 1 B2 frame; base 28 warm of F20a + F20c)'),\n"
            "               b32=b32_line(s['holds'], s['unattr'], 'B32 Sky Garden, F20e alone (holds with >= 1 unattributed frame, letter)'),\n"
            "               b32_f20a=b32_line(s['holds'], s['unattr_f20a'], 'B32 Sky Garden, F20e alone (variant F20a)'),\n"
            "               stop_i=stop_b2, stop_ii=stop_b32,\n"
            "               need_more=not (stop_b2 and stop_b32) and tags['made'] < TAG_MAX)\n",
            1, 'rd series2')
    r = rep(r, "        print('BASE F20a %s' % BASE)\n",
            "        print('BASE B2 %s (F20a 6 + F20c 22, item 543 (g)); B32 - the F20e series alone (item 543 (e))' % BASE)\n", 1, 'rd pbase')
    r = rep(r, "        print('NEXT %s' % ('more tags (warm N < 30, tags made < 30)' if s['need_more'] else 'stop adding tags'))\n",
            "        print('STOP (i) B2 warm N %d >= 30: %s; (ii) B32 F20e: holds %d, with unattributed %d (stop at >= 1 or %d clean): %s; tags made %d of %d'\n"
            "              % (s['sum']['warm'], 'yes' if s['stop_i'] else 'no', s['sum']['holds'], s['sum']['unattr'], B32_HOLDS,\n"
            "                 'yes' if s['stop_ii'] else 'no', s['tags']['made'], TAG_MAX))\n"
            "        print('NEXT %s' % ('more tags (item 543 (e): (i) and (ii) not both met, tags made < 30)' if s['need_more'] else 'stop adding tags'))\n",
            1, 'rd pnext')
    out['f20e_read.py'] = r

    # --- reader fixtures
    t = out['test_f20e_read.py']
    t = rep(t, "OLD = '631ff987' + '0' * 56\n", "OLD = '631ff987' + '0' * 56\nFS8 = '" + FS8 + "'\nFS7 = '8df61c009fbe6d7fd7f4e7576e89ab1b0989129336a26f6d1cdf8fd778fbffe7'\n", 1, 'tr consts')
    t = rep(t, "e = ev(mklog('pcs', iv={760: [PCS]}, dt={760: SLOW}), FS6)\ncheck('saved on FS6 letter -> nothing', e['hold_frames'][0]['letter'] == 'nothing')\n",
            "e = ev(mklog('pcs', iv={760: [PCS]}, dt={760: SLOW}), FS6)\ncheck('saved on FS6 letter -> nothing', e['hold_frames'][0]['letter'] == 'nothing')\n"
            "e = ev(mklog('pcs', iv={760: [PCS]}, dt={760: SLOW}), FS8)\ncheck('saved on FS8 letter -> nothing, variant unattributed', "
            "e['hold_frames'][0]['letter'] == 'nothing' and e['hold_frames'][0]['f20a'] == 'pcs after S12')\n", 1, 'tr fs8 attr')
    t = rep(t, "cmd_extra=(), binary=ADB, inst_b=None", "cmd_extra=(), binary=FS8, inst_b=None", 1, 'tr default bin')
    t = rep(t, "res, _ = mkdir_tag('fs6', binary=FS6)\ncheck('FS6 binary admitted', res['admitted'])\n",
            "for nm, b in (('adb', ADB), ('fs6', FS6), ('fs7', FS7)):\n"
            "    res, _ = mkdir_tag(nm, binary=b)\n"
            "    check('%s binary not admitted (FS8 only)' % nm, not res['admitted'] and res['reading'].startswith('INTERFERENCE'))\n"
            "res, _ = mkdir_tag('fs8mix', binary=FS8, inst_a=FS7)\n"
            "check('installed changed to FS7 after the tag -> not admitted', not res['admitted'])\n", 1, 'tr adm')
    i0 = t.index('# --- series and reading (item 462 (d))')
    i1 = t.index("check('CP upper for 0 of 30 = 0.116'")
    t = t[:i0] + (
        "# --- series, summary and stop rule (item 543 (e)): B2 base 28 warm, B32 - F20e alone\n"
        "def fake(admitted=True, read=True, warm=True, b2=0, hold=True, un=0, unf=None):\n"
        "    return dict(admitted=admitted, eval=dict(window_read=read, warm=warm, b2_frames=[[760]] * b2, hold=hold, unattr=un,\n"
        "                                             unattr_f20a=un if unf is None else unf))\n"
        "\n\n"
        "s = R.series([])\n"
        "check('empty: warm 28, holds 0, more', s['sum']['warm'] == 28 and s['sum']['holds'] == 0 and s['need_more'] and '0 holds' in s['b32'])\n"
        "s = R.series([fake()])\n"
        "check('29 warm -> SHORTAGE 1 to go, (i) not met', 'SHORTAGE, 0 of 29 (1 to go)' in s['b2'] and not s['stop_i'] and s['need_more'])\n"
        "s = R.series([fake(), fake()])\n"
        "check('28 + 2 warm = 30 -> (i) met, B2 NOT A DEFECT candidate', s['sum']['warm'] == 30 and s['stop_i'] and 'NOT A DEFECT candidate, 0 of 30' in s['b2'])\n"
        "check('B32 holds of F20e alone = 2, (ii) not met -> more', s['sum']['holds'] == 2 and not s['stop_ii'] and s['need_more'])\n"
        "s = R.series([fake(un=1)])\n"
        "check('(ii) by one unattributed hold, (i) not met -> more', s['stop_ii'] and not s['stop_i'] and s['need_more'])\n"
        "s = R.series([fake(), fake(un=2)])\n"
        "check('(i) and (ii) by unattributed -> stop', s['stop_i'] and s['stop_ii'] and not s['need_more'] and '1 of 2 holds' in s['b32'])\n"
        "s = R.series([fake() for _ in range(28)])\n"
        "check('28 clean holds -> (ii) not met, more', s['stop_i'] and not s['stop_ii'] and s['need_more'])\n"
        "s = R.series([fake() for _ in range(29)])\n"
        "check('29 clean holds -> (ii) met, stop', s['stop_ii'] and not s['need_more'] and '0 of 29 holds' in s['b32'])\n"
        "check('one-sided upper 95 % for 0 of 29 = 0.098', 'upper 95 % 0.098' in s['b32'])\n"
        "s = R.series([fake(un=0, unf=1), fake()])\n"
        "check('variant F20a does not meet (ii)', not s['stop_ii'] and '1 of 2 holds' in s['b32_f20a'] and '0 of 2 holds' in s['b32'])\n"
        "s = R.series([fake() for _ in range(28)] + [fake(admitted=False)])\n"
        "check('interference not counted', s['sum']['holds'] == 28 and s['tags']['interference'] == 1 and not s['stop_ii'])\n"
        "s = R.series([fake(warm=False) for _ in range(29)])\n"
        "check('cold: not in B2, in B32 -> (ii) met, (i) not, more', s['sum']['warm'] == 28 and s['sum']['holds'] == 29\n"
        "      and s['tags']['cold'] == 29 and s['stop_ii'] and not s['stop_i'] and s['need_more'])\n"
        "s = R.series([fake(read=False, warm=False, hold=False)])\n"
        "check('unread window and no hold', s['sum']['warm'] == 28 and s['sum']['holds'] == 0 and s['tags']['unread'] == 1)\n"
        "s = R.series([fake(warm=False, hold=False) for _ in range(30)])\n"
        "check('30 tags made -> stop with neither met', not s['need_more'] and not s['stop_i'] and not s['stop_ii'])\n"
        "s = R.series([fake(warm=False, hold=False) for _ in range(29)])\n"
        "check('29 tags made, neither met -> more', s['need_more'])\n"
        "s = R.series([fake(b2=1), fake()])\n"
        "check('one entry with B2 frames -> DEFECT candidate 1 of 30', 'DEFECT candidate, 1 of 30' in s['b2'] and 'p = 0.033' in s['b2'])\n"
        "check('base dict is not changed by the series', R.BASE == dict(warm=28, b2=0))\n") + t[i1:]
    out['test_f20e_read.py'] = t

    # --- sensitivity edits
    sn = out['sens_f20e.py']
    sn = rep(sn, "    ('FS6 not admitted', \"          '9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2': 'FS6 9325446c'}\", '          }'),\n",
             "    ('FS8 not admitted', \"BIN_OK = {'" + FS8 + "': 'FS8 2c9b69b9'}\", 'BIN_OK = {}'),\n"
             "    ('FS7 admitted', \"BIN_OK = {'" + FS8 + "': 'FS8 2c9b69b9'}\",\n"
             "     \"BIN_OK = {'" + FS8 + "': 'FS8 2c9b69b9', '8df61c009fbe6d7fd7f4e7576e89ab1b0989129336a26f6d1cdf8fd778fbffe7': 'FS7'}\"),\n",
             1, 'sn fs8')
    sn = rep(sn, "    ('base warm 5', 'BASE = dict(warm=6, b2=0, holds=8', 'BASE = dict(warm=5, b2=0, holds=8'),\n"
             "    ('base holds 9', 'BASE = dict(warm=6, b2=0, holds=8', 'BASE = dict(warm=6, b2=0, holds=9'),\n",
             "    ('base warm 27', 'BASE = dict(warm=28, b2=0)', 'BASE = dict(warm=27, b2=0)'),\n"
             "    ('base warm 29', 'BASE = dict(warm=28, b2=0)', 'BASE = dict(warm=29, b2=0)'),\n"
             "    ('B32 base not zero', \"base['b2'], holds=0, unattr=0\", \"base['b2'], holds=1, unattr=0\"),\n"
             "    ('B32 stop at 28 clean holds', 'B32_HOLDS = 29', 'B32_HOLDS = 28'),\n"
             "    ('B32 stop at 30 clean holds', 'B32_HOLDS = 29', 'B32_HOLDS = 30'),\n"
             "    ('(ii) ignores the unattributed hold', \"stop_b32 = s['unattr'] >= 1 or \", 'stop_b32 = '),\n"
             "    ('(ii) on variant F20a', \"stop_b32 = s['unattr'] >= 1 or \", \"stop_b32 = s['unattr_f20a'] >= 1 or \"),\n"
             "    ('stop needs only (i)', 'need_more=not (stop_b2 and stop_b32)', 'need_more=not stop_b2'),\n"
             "    ('stop needs only (ii)', 'need_more=not (stop_b2 and stop_b32)', 'need_more=not stop_b32'),\n"
             "    ('stop on either', 'need_more=not (stop_b2 and stop_b32)', 'need_more=not (stop_b2 or stop_b32)'),\n"
             "    ('B32 one-sided bound 0.10', '1 - 0.05 ** (1.0 / n)', '1 - 0.10 ** (1.0 / n)'),\n",
             1, 'sn base')
    out['sens_f20e.py'] = sn

    # --- tool fixtures: tags
    tt = out['test_tools_f20e.py']
    tt = rep(tt, "'f20_v31'", "'f20_v55'", 2, 'tt v31')
    tt = rep(tt, "go: f20_v31 refused (usage)", "go: f20_v55 refused (usage)", 1, 'tt v31b')
    tt = rep(tt, "launch: f20_v31 refused", "launch: f20_v55 refused", 1, 'tt v31c')
    tt = rep(tt, "if not os.path.isdir(os.path.join(HERE, 'runs', 'f20_v01')):\n    p = subprocess.run([BASH, os.path.join(HERE, 'go_f20e.sh'), 'f20_v02'], capture_output=True, text=True)\n"
             "    check('go: f20_v02 before f20_v01 refused (order, or lock rc 3)'",
             "if not os.path.isdir(os.path.join(HERE, 'runs', 'f20_v25')):\n    p = subprocess.run([BASH, os.path.join(HERE, 'go_f20e.sh'), 'f20_v26'], capture_output=True, text=True)\n"
             "    check('go: f20_v26 before f20_v25 refused (order, or lock rc 3)'", 1, 'tt order')
    tt = rep(tt, "'launch_f20e.sh'), 'f20_v30']", "'launch_f20e.sh'), 'f20_v54']", 1, 'tt v30')
    tt = rep(tt, "'f20_v30' in tl", "'f20_v54' in tl", 1, 'tt v30b')
    tt = rep(tt, "check('%s: tags f20_v01..f20_v30 only' % nm, nm == 'wait_f20e.sh' or '" + OLD_TAGS + "' in s)",
             "check('%s: tags f20_v25..f20_v54 only' % nm, nm == 'wait_f20e.sh' or '" + NEW_TAGS + "' in s)", 1, 'tt re')
    tt = rep(tt, "p = subprocess.run([BASH, os.path.join(HERE, 'go_f20e.sh'), 'f20_v1'], capture_output=True, text=True)\n"
             "check('go: f20_v1 refused (usage)', p.returncode == 2)\n",
             "p = subprocess.run([BASH, os.path.join(HERE, 'go_f20e.sh'), 'f20_v1'], capture_output=True, text=True)\n"
             "check('go: f20_v1 refused (usage)', p.returncode == 2)\n"
             "for bad in ('f20_v24', 'f20_v01', 'f20_v30x'):\n"
             "    p = subprocess.run([BASH, os.path.join(HERE, 'go_f20e.sh'), bad], capture_output=True, text=True)\n"
             "    check('go: %s refused (usage)' % bad, p.returncode == 2)\n"
             "go_src = open(os.path.join(HERE, 'go_f20e.sh'), encoding='ascii').read()\n"
             "check('go: only FS8 admitted', 'FS8=2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b' in go_src\n"
             "      and '[ \"$WANT\" = \"$FS8\" ] ||' in go_src and 'ADB=' not in go_src and 'FS6=' not in go_src)\n"
             "check('go: order from f20_v25', 'if [ $NN -gt 25 ]; then' in go_src)\n", 1, 'tt extra')
    out['test_tools_f20e.py'] = tt

    tg = out['test_guard_f20e.py']
    tg = rep(tg, "'launch_f20e.sh'), 'f20_v30']", "'launch_f20e.sh'), 'f20_v54']", tg.count("'launch_f20e.sh'), 'f20_v30']"), 'tg v30')
    out['test_guard_f20e.py'] = tg

    for nm, txt in out.items():
        assert all(ord(c) < 128 for c in txt), nm
        with open(D + '/' + nm, 'wb') as f:
            f.write(txt.encode('ascii'))
    with open(D + '/guard_block.txt', 'wb') as f:
        pass
    # regression cache of the reader (key = path, size, mtime, binary; reader scan unchanged)
    shutil.copytree(S + '/regress_cache', D + '/regress_cache')
    print('PORT OK files %d' % (len(out) + len(UNCHANGED)))
    return 0


if __name__ == '__main__':
    sys.exit(main())

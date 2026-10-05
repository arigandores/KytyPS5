"""Track F link FS8c (HPP-573): hand sensitivity of test_fs8c_read.py - each edit below breaks one rule of fs8c_read.py (seal section 4);
the suite run against the edited reader (a copy in a temp dir) must end with SOME FAILED.  Not mutlib (no mutants in FS8c, item 471
(g)(3)); a check that the fixtures are not vacuous.  The first output line names the script, the suite and the target with their sha256;
the last line is ALL OK when every edit is caught.  ASCII only."""
import hashlib, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'fs8c_read.py')
SUITE = os.path.join(HERE, 'test_fs8c_read.py')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite sens_fs8c.py sha256 %s target fs8c_read.py sha256 %s test_fs8c_read.py sha256 %s'
      % (sha(os.path.abspath(__file__)), sha(TARGET), sha(SUITE)))
EDITS = [
    ('binary sha not checked', "res['json_binary'] == BIN_EXPECT and sha == BIN_EXPECT", "res['json_binary'] == BIN_EXPECT"),
    ('json binary not checked', "res['json_binary'] == BIN_EXPECT and sha == BIN_EXPECT", "sha == BIN_EXPECT"),
    ('version string ignored', "bool(res['version_in_bin'])),", "True),"),
    ('revision accepts anything', "all(t in (REV, VERSION.decode()) for _, _, t in rev)", "True"),
    ('prereg ignored', "bool(pre) and pre == seal_sha),", "True),"),
    ('KYTY_FIX_ allowed', "k.startswith('KYTY_FIX_') or ", ""),
    ('KYTY_GAME_PATCH allowed', "k in ('KYTY_GAME_PATCH', 'KYTY_GPU_CHECKPOINTS')", "k in ('KYTY_GPU_CHECKPOINTS',)"),
    ('first validation flag wins', "            val = cmd[i + 1] if i + 1 < len(cmd) else None\n", "            val = val or (cmd[i + 1] if i + 1 < len(cmd) else None)\n"),
    ('limit not checked', "if env.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT') != LIMIT:", "if False:"),
    ('filter allowed', "for k in ('VK_LAYER_MESSAGE_ID_FILTER', 'KYTY_PIPELINE_PRECACHE', 'KYTY_REC'):", "for k in ('KYTY_PIPELINE_PRECACHE', 'KYTY_REC'):"),
    ('V layer allowed', "            if k.startswith('VK_LAYER_'):", "            if k.startswith('VK_LAYER_X'):"),
    ('cold ignored', "bool(cold_t) and 'absent' in cold_t and 'present' not in cold_t),", "True),"),
    ('minimized ignored', "not r['win'].get('minimized') and ", ""),
    ('installed before ignored', "[('installed FS6 9325446c before the tag', sha_b == WANT),", "[('installed FS6 9325446c before the tag', True),"),
    ('manifest ignored', "bool(mc) and mc.startswith('manifest cmp EQUAL'))]", "True)]"),
    ('directory any', "all(s.replace('/', '\\\\').endswith('\\\\' + DIR_FIX) for s in stc)", "True"),
    ('FixB4 order ignored', "    return ones[0] < first_guest, detail", "    return True, detail"),
    ('Fix other form ignored', "    if len(ones) != 1 or other:", "    if len(ones) != 1:"),
    ('Fix two lines allowed', "    if len(ones) != 1 or other:", "    if not ones or other:"),
    ('FixB42 counted as FixB4', "M_FIXK = {'B4': b'FixB4:'", "M_FIXK = {'B4': b'FixB4'"),
    ('hold threshold 299 s', "HOLD_MIN_US = 300000000", "HOLD_MIN_US = 299000000"),
    ('scene frame draws 99', "if md and int(md.group(1)) >= 100:", "if md and int(md.group(1)) >= 99:"),
    ('hold_exit ignored', "att.get('outcome') == 'ok' and att.get('hold_exit') is None and ", "att.get('outcome') == 'ok' and "),
    ('attempt hold_s not checked', "and att.get('hold_s') >= spec['hold'])", ")"),
    ('stdout death ignored', "death = r['death'] + (sd or [])", "death = r['death']"),
    ('video 2999 accepted', "VIDEO_MIN = 3000", "VIDEO_MIN = 2999"),
    ('glitch any', "None if gl is None else gl == 0),", "None if gl is None else True),"),
    ('vke ignored', "r['vke'] == 0),", "True),"),
    ('vkw ignored', "('positive control of the layer, [Vulkan][W] > 0', r['vkw'] > 0),", "('positive control of the layer, [Vulkan][W] > 0', True),"),
    ('dual order ignored', "r['first_guest'] is not None and ln < r['first_guest'] for ln, s, e in r['dual']", "True for ln, s, e in r['dual']"),
    ('word: none NOT_EVALUABLE', "    elif any(v is None for _, v in mem):\n        word = 'NOT_EVALUABLE'\n", ""),
    ('word: form after members', "    elif not all(v for _, v in form):\n        word = 'FORM_FAIL'\n    elif any(v is False for _, v in mem):\n        word = 'MEMBERS_FAIL'\n",
     "    elif any(v is False for _, v in mem):\n        word = 'MEMBERS_FAIL'\n    elif not all(v for _, v in form):\n        word = 'FORM_FAIL'\n"),
    ('scene change counted', "if after_entry and r['scene_change_line'] is None:", "if after_entry:"),
    ('k2 threshold 999 999', "K2_US = 1000000", "K2_US = 999999"),
    ('non-ASCII output', "    print('\\n'.join(asc(x) for x in rows(res)))", "    print('\\n'.join(rows(res)))"),
]
ok = True
src = open(TARGET, encoding='utf-8').read()
for name, a, b in EDITS:
    if src.count(a) != 1:
        print('EDIT %s: anchor count %d - BAD EDIT' % (name, src.count(a)))
        ok = False
        continue
    tmp = tempfile.mkdtemp(prefix='fs8c_sens_')
    open(os.path.join(tmp, 'fs8c_read.py'), 'w', encoding='utf-8', newline='\n').write(src.replace(a, b))
    shutil.copy(SUITE, os.path.join(tmp, 'test_fs8c_read.py'))
    p = subprocess.run([sys.executable, os.path.join(tmp, 'test_fs8c_read.py')], capture_output=True, cwd=tmp)
    last = (p.stdout.decode('ascii', 'replace').strip().split('\n') or [''])[-1]
    nf = [x for x in p.stdout.decode('ascii', 'replace').split('\n') if x.startswith('checks ')]
    caught = last != 'ALL OK'
    print('EDIT %s: %s (%s; %s)' % (name, 'CAUGHT' if caught else 'SURVIVED', last, nf[0] if nf else 'no count'))
    ok &= caught
    shutil.rmtree(tmp, ignore_errors=True)
print('edits %d' % len(EDITS))
print('ALL OK' if ok else 'SOME SURVIVED')

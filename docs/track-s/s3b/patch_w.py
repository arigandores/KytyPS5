"""S3b (HPP-325): form W of item 254 (e) (KytyPS5 d3a8d951; the lead comment 04:59:00Z in HPP-325): every validation arm
runs with KYTY_PIPELINE_PRECACHE=0; positive control - no "PipelinePrecache: N recipes ->" line in its log; fixtures and
mutants.  Edits go_s.sh, sc_s.py, test_sc_s.py, test_go_s.py, mut_sc_s.py in place; LF; every anchor exactly once."""
from pathlib import Path

R = Path('C:/kyty/s288')


def edit(name, pairs):
    p = R / name
    t = p.read_bytes().decode('ascii').replace('\r\n', '\n')
    for a, b in pairs:
        assert t.count(a) == 1, (name, a[:60], t.count(a))
        t = t.replace(a, b)
    p.write_bytes(t.encode('ascii'))
    print('edited', name)


edit('go_s.sh', [
    ('#     GLCache in runs_s/<tag>.glc_launch.txt / .glc_post.txt.\n',
     '#     GLCache in runs_s/<tag>.glc_launch.txt / .glc_post.txt.\n'
     '#   S3b, item 254 (e) (form W until B35 ships): a validation arm runs with KYTY_PIPELINE_PRECACHE=0 (no start precache,\n'
     '#     no recipe writes); its positive control (no "PipelinePrecache: N recipes ->" line) is read by sc_s.py.\n'),
    ('  EXTRA="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP"\n',
     '  EXTRA="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=$VKDUP KYTY_PIPELINE_PRECACHE=0"   # form W, item 254 (e)\n'),
])

edit('sc_s.py', [
    ('      stopped before the entry line by validation is VALIDATION_STOP_PRE_LEVEL, member (d) undetermined (RC11).\n',
     '      stopped before the entry line by validation is VALIDATION_STOP_PRE_LEVEL, member (d) undetermined (RC11).\n'
     '  (12) item 254 (e) (form W until B35 ships): a validation arm runs with KYTY_PIPELINE_PRECACHE=0 (a family key of the\n'
     '      seal) and its admission row is the positive control - no "PipelinePrecache: N recipes ->" line in its log.\n'),
    ("        e.update(KYTY_S_PCW=spec['pcw'], KYTY_S_PCW_FORCE_MS=PCW_FORCE_MS)\n    return e\n",
     "        e.update(KYTY_S_PCW=spec['pcw'], KYTY_S_PCW_FORCE_MS=PCW_FORCE_MS)\n"
     "    if spec['val']:\n"
     "        e.update(KYTY_PIPELINE_PRECACHE='0')      # form W of a validation arm, item 254 (e)\n"
     "    return e\n"),
    ("RX_PCWOV = re.compile(rb'AvTrace: pcw overlap (.+?) id0=')\n",
     "RX_PCWOV = re.compile(rb'AvTrace: pcw overlap (.+?) id0=')\n"
     "RX_QUEUED_ANY = re.compile(rb'PipelinePrecache: \\d+ recipes ->')     # item 254 (e): the start precache ran\n"),
    ("lines=0, pcw_ov=[], pcw_rec=[])", "lines=0, pcw_ov=[], pcw_rec=[], queued_n=0)"),
    ("                elif line.startswith(b'PipelinePrecache: '):\n                    m = RX_QUEUED.search(line)\n",
     "                elif line.startswith(b'PipelinePrecache: '):\n"
     "                    if RX_QUEUED_ANY.match(line):\n"
     "                        s['queued_n'] += 1\n"
     "                    m = RX_QUEUED.search(line)\n"),
    ("    s = scan_s(lp)\n    std = scan_stdout(sp)\n",
     "    s = scan_s(lp)\n    std = scan_stdout(sp)\n"
     "    if spec['val']:\n"
     "        # item 254 (e): form W - the positive control of KYTY_PIPELINE_PRECACHE=0 is no \"recipes ->\" line in the log\n"
     "        r['admit'].append(('form W positive control: no \"PipelinePrecache: N recipes ->\" line (item 254 (e))',\n"
     "                           s['queued_n'] == 0, s['queued_n']))\n"),
])

edit('test_sc_s.py', [
    ("\n# ================================================================================================ 13 seal and main\n",
     "# item 254 (e): form W of the validation arm\n"
     "ok &= case('K26 form W: the expected environment of pcw_val carries KYTY_PIPELINE_PRECACHE=0 (a family key), no other '\n"
     "           'arm does', S.expected_env(S.SPEC['pcw_val']).get('KYTY_PIPELINE_PRECACHE') == '0' and S.in_family(\n"
     "               'KYTY_PIPELINE_PRECACHE') and all('KYTY_PIPELINE_PRECACHE' not in S.expected_env(S.SPEC[t]) for t in S.SPEC\n"
     "                                                 if t != 'pcw_val'))\n"
     "s = sc(['PipelinePrecache: 5 recipes -> x', QUEUED(100, 1, 1), 'PipelinePrecache: saved 3 recipes',\n"
     "        'PipelinePrecache: all pipelines created, 4 ms'], 'k26')\n"
     "ok &= case('K26b the scan counts every \"PipelinePrecache: N recipes ->\" line (the short and the full form: 2), not the '\n"
     "           'saved / created lines', s['queued_n'] == 2)\n"
     "word, lines = pcw_all()\n"
     "ok &= case('K26c form W clean (no recipes line in pcw_val) -> the positive control row PASS, word unchanged',\n"
     "           word == 'MACHINE_PASS_PENDING_SHEET' and any(x[0].startswith('form W positive control') and x[1] for x in\n"
     "                                                       S.score_arm('pcw_val', RM)['admit']))\n"
     "word, lines = pcw_all(val_lines=([QUEUED(100, 1, 1)] + pcw_lines(S.SKY, 15, 0) + [\n"
     "    'VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features'], (3000, 0)))\n"
     "ok &= case('K26d a \"PipelinePrecache: 100 recipes ->\" line in pcw_val (the start precache ran) -> admission FAIL of '\n"
     "           'pcw_val -> NOT_EVALUABLE', word == 'NOT_EVALUABLE' and 'admission: form W positive control: no '\n"
     "           '\"PipelinePrecache: N recipes ->\" line (item 254 (e))' in S.score_arm('pcw_val', RM)['fail'])\n"
     "word, lines = pcw_all()\n"
     "mkarm('pcw_val', pcw_lines(S.SKY, 15, 0) + ['VK_LAYER_KHRONOS_validation available extension: '\n"
     "                                            'VK_EXT_validation_features'], glitch=(3000, 0),\n"
     "      js=js_for('pcw_val', env_over=dict(KYTY_PIPELINE_PRECACHE=None)))\n"
     "word, lines = S.read_pcw(S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None))\n"
     "ok &= case('K26e pcw_val without KYTY_PIPELINE_PRECACHE=0 -> the family row FAIL -> NOT_EVALUABLE', word == 'NOT_EVALUABLE'\n"
     "           and any(x.startswith('admission: KYTY_* families') for x in S.score_arm('pcw_val', RM)['fail']))\n"
     "\n# ================================================================================================ 13 seal and main\n"),
])

edit('test_go_s.py', [
    ("ok &= case('G23 pcw_val: --vulkan-validation true with VK_LAYER_PATH, hold 310, timeout 600, video too',\n",
     "ok &= case('G23b form W (item 254 (e)): pcw_val runs with KYTY_PIPELINE_PRECACHE=0; no other arm of S4 / S6 does',\n"
     "           ' KYTY_PIPELINE_PRECACHE=0 ' in o6['pcw_val'][1] and all('KYTY_PIPELINE_PRECACHE' not in o6[t][1] for t in s6\n"
     "                                                              if t != 'pcw_val') and\n"
     "           all('KYTY_PIPELINE_PRECACHE' not in out[t][1] for t in tags))\n"
     "ok &= case('G23 pcw_val: --vulkan-validation true with VK_LAYER_PATH, hold 310, timeout 600, video too',\n"),
])

edit('mut_sc_s.py', [
    ("    # seal and main\n",
     "    # S3b, item 254 (e): form W of the validation arm\n"
     "    ('w_env', \"        e.update(KYTY_PIPELINE_PRECACHE='0')\", \"        pass\"),\n"
     "    ('w_row', \"s['queued_n'] == 0, s['queued_n']))\", \"True, s['queued_n']))\"),\n"
     "    ('w_scan', \"                        s['queued_n'] += 1\\n\", \"                        pass\\n\"),\n"
     "    ('w_rx', \"RX_QUEUED_ANY = re.compile(rb'PipelinePrecache: \\\\d+ recipes ->')\", "
     "\"RX_QUEUED_ANY = re.compile(rb'PipelinePrecache: \\\\d+ recipes -> \\\\d+ graphics')\"),\n"
     "    ('w_val', \"    if spec['val']:\\n        # item 254 (e): form W\", \"    if False:\\n        # item 254 (e): form W\"),\n"
     "    # seal and main\n"),
])

ns = {}
exec(compile((R / 'mut_sc_s.py').read_text(encoding='ascii'), 'mut', 'exec'), ns)
src = (R / 'sc_s.py').read_text(encoding='ascii')
for m in ns['MUTANTS']:
    assert src.count(m[1]) == 1, m[0]
print('mutants %d, all anchors unique' % len(ns['MUTANTS']))

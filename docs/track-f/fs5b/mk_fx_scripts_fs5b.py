# FS5b (HPP-510, Red Team): port my FS4b fixture of the default parsing (mk_fixture_fs4b.py, run_fixture_fs4b.py,
# build_fx.cmd) and my knob scanner (knobs_fs4b.py) to FS5: FixSvalEnabled in pipelineCache.cpp -> FixF10Enabled in
# ShaderDecoder.cpp, KYTY_FIX_SVAL -> KYTY_FIX_F10, commits 3d0e46da -> 0e72bc19 (FS5) and 92d11340 -> 8a56dc2a (F12d,
# negative control: default 0), fs4/fs4b -> fs5/fs5b; the scanner's expected ON set = the eight knobs of item 410(g)(1).
# Every replacement is counted (the script fails on a count of 0 where one is required). LF output.
import io
S = 'C:/kyty/KytyPS5/docs/track-f/fs4b/'
D = 'C:/kyty/f287/fs5/fs5b/'
BS = chr(92)


def port(src, dst, R, hdr, cmt='# '):
    t = io.open(S + src, encoding='utf-8', newline='').read().replace('\r\n', '\n')
    cnt = []
    for a, b, need in R:
        n = t.count(a)
        cnt.append(n)
        assert (n > 0) or not need, (src, a)
        t = t.replace(a, b)
    if t.startswith('@echo off\n'):
        t = '@echo off\nrem ' + hdr + '\n' + t[len('@echo off\n'):]
    else:
        t = cmt + hdr + '\n' + t
    open(D + dst, 'wb').write(t.encode('utf-8'))
    print(dst, cnt)


COMMON = [
    ('fs4/fs4b', 'fs5/fs5b', False),
    ('fs4' + BS + 'fs4b', 'fs5' + BS + 'fs5b', False),
    ('3d0e46da', '0e72bc19', True),
    ('92d11340', '8a56dc2a', False),
]
FX = COMMON + [
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp', True),
    ('FixSvalEnabled', 'FixF10Enabled', True),
    ('KYTY_FIX_SVAL', 'KYTY_FIX_F10', True),
]
port('mk_fixture_fs4b.py', 'mk_fixture_fs5b.py', FX, 'FS5b (HPP-510, Red Team): port of my FS4b mk_fixture_fs4b.py by mk_fx_scripts_fs5b.py (FixF10Enabled, 0e72bc19 vs 8a56dc2a). Was:')
FXR = COMMON + [('FixSvalEnabled', 'FixF10Enabled', False), ('KYTY_FIX_SVAL', 'KYTY_FIX_F10', True)]
port('run_fixture_fs4b.py', 'run_fixture_fs5b.py', FXR + [('item 378(g)(1)', 'item 410(g)(1)', False), ('(F10c, negative control', '(F12d, negative control', False)],
     'FS5b (HPP-510, Red Team): port of my FS4b run_fixture_fs4b.py by mk_fx_scripts_fs5b.py (FixF10Enabled, 0e72bc19 vs 8a56dc2a). Was:')
port('build_fx.cmd', 'build_fx.cmd', COMMON, 'FS5b (HPP-510, Red Team): port of my FS4b build_fx.cmd by mk_fx_scripts_fs5b.py. Was:')
port('knobs_fs4b.py', 'knobs_fs5b.py', [
    ('3d0e46da', '0e72bc19', True),
    ("'KYTY_FIX_B42', 'KYTY_FIX_SVAL'}", "'KYTY_FIX_B42', 'KYTY_FIX_SVAL', 'KYTY_FIX_F10'}", True),
    ('item 378(g)(1) set', 'item 410(g)(1) set', True),
], 'FS5b (HPP-510, Red Team): port of my FS4b knobs_fs4b.py by mk_fx_scripts_fs5b.py (default commit 0e72bc19, expected ON set + KYTY_FIX_F10, item 410(g)(1)). Was:')
print('ALL OK')

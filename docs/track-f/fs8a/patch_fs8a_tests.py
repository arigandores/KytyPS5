"""FS8a (HPP-571, ROADMAP s122 item 471(g)(1)(v)): shader_cfg_tests read KYTY_FIX_F19 through Common::EnvFlagOn
(unset = 0, the default before FS8a), so at the new default (unset = 1, FixF19Enabled of e46f55d4) the unset run takes
the =1 path and checks it against the =0 expectations. The three reads become FixF19Enabled() - the very function of
the translator, as the comment of the first one already says. Whole-line anchors, LF/CRLF kept, exact counts.
Usage: python patch_fs8a_tests.py <tests/shaderCfgTests.cpp>
"""
import sys

path = sys.argv[1]
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
lines = raw.decode('utf-8').replace('\r\n', '\n').split('\n')

OLD_COMMENT = '    // D16_UNORM). The knob is read as FixF19Enabled reads it, once per process.'
NEW_COMMENT = ('    // D16_UNORM). The knob is FixF19Enabled() itself (default ON since FS8a, ROADMAP s122 item 471(g)(1)).')
reads = {
    '    const bool fix_f19 = Common::EnvFlagOn("KYTY_FIX_F19");':
        '    const bool fix_f19 = ShaderRecompiler::IR::FixF19Enabled();',
    '  const bool fix_f19 = Common::EnvFlagOn("KYTY_FIX_F19");':
        '  const bool fix_f19 = ShaderRecompiler::IR::FixF19Enabled();',
}
want = {OLD_COMMENT: 1, list(reads)[0]: 1, list(reads)[1]: 2}
got = {k: sum(1 for l in lines if l == k) for k in want}
print('anchors', got)
if got != want:
    print('ANCHOR MISMATCH')
    sys.exit(1)
out = []
for l in lines:
    if l == OLD_COMMENT:
        out.append(NEW_COMMENT)
    elif l in reads:
        out.append(reads[l])
    else:
        out.append(l)
text = '\n'.join(out)
if crlf:
    text = text.replace('\n', '\r\n')
open(path, 'wb').write(text.encode('utf-8'))
left = sum(1 for l in out if 'EnvFlagOn("KYTY_FIX_F19")' in l)
print('patched', path, 'crlf' if crlf else 'lf', 'EnvFlagOn(KYTY_FIX_F19) left', left)
print('OK' if left == 0 else 'LEFT')

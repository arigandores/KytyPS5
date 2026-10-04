# F16e (HPP-522, Red Team): own mutants of the F16d code in the worktree C:/kyty/f287/f16e/wt (LF files, whole-line
# anchors; CR is stripped before the search and restored if present). Usage: mutate.py <M3|M4> <apply|revert>
#  M3 - cmask_fce None branch: an MSAA target is counted as cmask_fce_nofill (a B branch counted in another B child;
#       the family identity still holds, only the per-branch expectation can catch it).
#  M4 - DiagF6::NoteDraw: the export into a slot with mask != 0 and base 0 is classed by the inverted format test
#       (w_addr0_fmt <-> w_addr0_nofmt; the W identity still holds).
import sys

WT = 'C:/kyty/f287/f16e/wt/'
MUT = {
    'M3': ('src/graphics/host_gpu/renderer/pipeline/descriptors.cpp',
           '\t\t\t\t            : f5_info.samples != 1                             ? DiagF5::Counter::CmaskFceMsaa\n',
           '\t\t\t\t            : f5_info.samples != 1                             ? DiagF5::Counter::CmaskFceNoFill\n'),
    'M4': ('src/graphics/host_gpu/renderer/diagF5.cpp',
           '\t\t\t\tinc(fmt_on[index] ? Counter::WAddr0Fmt : Counter::WAddr0NoFmt);\n',
           '\t\t\t\tinc(!fmt_on[index] ? Counter::WAddr0Fmt : Counter::WAddr0NoFmt);\n'),
}


def main():
    name, action = sys.argv[1], sys.argv[2]
    path, old, new = MUT[name]
    if action == 'revert':
        old, new = new, old
    raw = open(WT + path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', '\n')
    lines = text.split('\n')
    hits = [i for i, l in enumerate(lines) if l + '\n' == old]
    if len(hits) != 1:
        print('anchor hits', len(hits), 'for', name, action)
        return 1
    lines[hits[0]] = new[:-1]
    text = '\n'.join(lines)
    if crlf:
        text = text.replace('\n', '\r\n')
    open(WT + path, 'wb').write(text.encode('utf-8'))
    print(name, action, 'line', hits[0] + 1, path)
    return 0


sys.exit(main())

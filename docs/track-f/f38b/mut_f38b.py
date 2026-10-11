"""F38b (HPP-764, Red Team): mutants of KYTY_FIX_F25 (ROADMAP s122 item 691(d)(3)) on the F38b worktree (tree of
531d6488). usage: mut_f38b.py <wt> <m1|m2a|m2b|m3|m4a|m4b|m4c|m5a|m5b>
Each mutant replaces whole-line anchors (asserted count 1 each); files are LF (CR stripped and restored if present).
  m1  - the flag is never set (the else-branch assignment of *failed_twice removed)
  m2a - "|| remaining == 0" removed from the early return of ReadGuestWithRetry (retry and flag at remaining = 0)
  m2b - the early return sets the flag when the direct read gave 0 with nbytes > 0 and remaining == 0 (no retry)
  m3  - no re-read of Size(): fix_f25_eio = true in KernelRead and KernelPread
  m4a - KernelRead: Seek(pos + 1) on the error path
  m4b - KernelPread: the file position is not restored when EIO is returned
  m4c - (reference) KernelRead: the Seek(pos) of the new path removed
  m5a - return -1 instead of KERNEL_ERROR_EIO on the new path of KernelRead and KernelPread
  m5b - AIO: state always COMPLETED (src/libs/libKernel.cpp)
"""
import sys

wt, m = sys.argv[1], sys.argv[2]
FS = 'src/kernel/fileSystem.cpp'
LK = 'src/libs/libKernel.cpp'

EARLY = ('\tif (*bytes_read != 0 || nbytes == 0 || remaining == 0) {\n'
         '\t\treturn;\n'
         '\t}\n')
SET_FLAG = ('\t} else {\n'
            '\t\t*failed_twice = true;\n'
            '\t}\n'
            '}\n')
R_SIZE = '\t\tfix_f25_eio = pos < file->f.Size();\n'
R_SEEK = ('\t\tfix_f25_eio = pos < file->f.Size();\n'
          '\t\tfile->f.Seek(pos);\n'
          '\t}\n')
P_SIZE = '\t\tfix_f25_eio = static_cast<uint64_t>(offset) < file->f.Size();\n'
P_RESTORE = ('\t}\n'
             '\tfile->f.Seek(pos);\n'
             '\tStreamTraceMid(stream_read, buf, bytes_read);\n'
             '\t// See KernelRead: re-mark the region CPU-dirty once the data is complete.\n')
R_RET = ('\t\tFixF25Report(d, nbytes, pos);\n'
         '\t\treturn KERNEL_ERROR_EIO;\n')
P_RET = ('\t\tFixF25Report(d, nbytes, static_cast<uint64_t>(offset));\n'
         '\t\treturn KERNEL_ERROR_EIO;\n')
# the same state line exists in the write path too: the anchor takes the KernelPread call of the read path
AIO = ('\t\t    LibKernel::FileSystem::KernelPread(req[i].fd, req[i].buf, req[i].nbyte, req[i].offset);\n'
       '\n'
       '\t\treq[i].result->return_value = result;\n'
       '\t\treq[i].result->state = (result < 0 ? KERNEL_AIO_STATE_ABORTED : KERNEL_AIO_STATE_COMPLETED);\n')

edits = {
    'm1': [(FS, SET_FLAG, '\t} else {\n\t\t// MUTANT m1: flag not set\n\t}\n}\n')],
    'm2a': [(FS, EARLY, '\tif (*bytes_read != 0 || nbytes == 0) { // MUTANT m2a\n\t\treturn;\n\t}\n')],
    'm2b': [(FS, EARLY, '\tif (*bytes_read != 0 || nbytes == 0 || remaining == 0) {\n'
                        '\t\t*failed_twice = (*bytes_read == 0 && nbytes != 0 && remaining == 0); // MUTANT m2b\n'
                        '\t\treturn;\n\t}\n')],
    'm3': [(FS, R_SIZE, '\t\tfix_f25_eio = true; // MUTANT m3\n'),
           (FS, P_SIZE, '\t\tfix_f25_eio = true; // MUTANT m3\n')],
    'm4a': [(FS, R_SEEK, '\t\tfix_f25_eio = pos < file->f.Size();\n\t\tfile->f.Seek(pos + 1); // MUTANT m4a\n\t}\n')],
    'm4b': [(FS, P_RESTORE, '\t}\n\tif (!fix_f25_eio) { // MUTANT m4b\n\t\tfile->f.Seek(pos);\n\t}\n'
                            '\tStreamTraceMid(stream_read, buf, bytes_read);\n'
                            '\t// See KernelRead: re-mark the region CPU-dirty once the data is complete.\n')],
    'm4c': [(FS, R_SEEK, '\t\tfix_f25_eio = pos < file->f.Size();\n\t\t// MUTANT m4c: no Seek(pos)\n\t}\n')],
    'm5a': [(FS, R_RET, '\t\tFixF25Report(d, nbytes, pos);\n\t\treturn -1; // MUTANT m5a\n'),
            (FS, P_RET, '\t\tFixF25Report(d, nbytes, static_cast<uint64_t>(offset));\n\t\treturn -1; // MUTANT m5a\n')],
    'm5b': [(LK, AIO, AIO.replace('(result < 0 ? KERNEL_AIO_STATE_ABORTED : KERNEL_AIO_STATE_COMPLETED);',
                                  'KERNEL_AIO_STATE_COMPLETED; // MUTANT m5b'))],
}
if m not in edits:
    sys.exit('bad mutant ' + m)
for rel, old, new in edits[m]:
    path = wt + '/' + rel
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    t = raw.decode('utf-8').replace('\r\n', '\n')
    assert t.count(old) == 1, (rel, 'anchor count', t.count(old))
    t = t.replace(old, new)
    if crlf:
        t = t.replace('\n', '\r\n')
    open(path, 'wb').write(t.encode('utf-8'))
    print('applied', m, rel, 'crlf', crlf)

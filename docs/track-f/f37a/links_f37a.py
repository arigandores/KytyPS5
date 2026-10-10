"""F37a (HPP-761): check of the references <commit>:<path>:<line> of docs/track-f/f37a.md - the line starts with the anchor
and the next line starts with the +1 text (git show of the commit, real git). Generated once by gen_links_f37a.py.
Prints one line per reference and ALL OK / FAIL."""
import subprocess

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
REFS = [
    ('ee9632be', 'src/kernel/fileSystem.cpp', 762, 'void ReadGuestWithRetry(File* file, void* buf, size_t nbytes, uint64_t pos, uint64_t remai', '                        uint32_t* bytes_read) {'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 764, '\tfile->f.Read(buf, static_cast<uint32_t>(nbytes), bytes_read);', '\tif (*bytes_read != 0 || nbytes == 0 || remaining == 0) {'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 765, '\tif (*bytes_read != 0 || nbytes == 0 || remaining == 0) {', '\t\treturn;'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 775, '\tfile->f.Seek(pos);', '\tfile->f.Read(temporary.data(), static_cast<uint32_t>(nbytes), bytes_read);'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 776, '\tfile->f.Read(temporary.data(), static_cast<uint32_t>(nbytes), bytes_read);', '\tif (*bytes_read != 0) {'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 777, '\tif (*bytes_read != 0) {', '\t\tstd::memcpy(buf, temporary.data(), *bytes_read);'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 782, 'int64_t KYTY_SYSV_ABI KernelRead(int d, void* buf, size_t nbytes) {', '\tPRINT_NAME();'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 828, '\tbool       is_invalid = file->f.IsInvalid();', '\tconst auto pos        = file->f.Tell();'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 829, '\tconst auto pos        = file->f.Tell();', '\tconst auto file_size  = file->f.Size();'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 852, '\tif (is_invalid) {', '\t\tLOGF("\\tfile is invalid\\n");'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 854, '\t\treturn KERNEL_ERROR_EIO;', '\t}'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 867, '\treturn bytes_read;', '}'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 941, 'int64_t KYTY_SYSV_ABI KernelPread(int d, void* buf, size_t nbytes, int64_t offset) {', '\tPRINT_NAME();'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 979, '\tbool       is_invalid = file->f.IsInvalid();', '\tauto       pos        = file->f.Tell();'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 980, '\tauto       pos        = file->f.Tell();', '\tconst auto file_size  = file->f.Size();'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 989, '\tfile->f.Seek(offset);', '\tReadGuestWithRetry(file, buf, nbytes, static_cast<uint64_t>(offset), remaining, &bytes_re'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 990, '\tReadGuestWithRetry(file, buf, nbytes, static_cast<uint64_t>(offset), remaining, &bytes_re', '\tfile->f.Seek(pos);'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 991, '\tfile->f.Seek(pos);', '\tStreamTraceMid(stream_read, buf, bytes_read);'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 1002, '\tif (is_invalid) {', '\t\tLOGF("\\tfile is invalid\\n");'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 1004, '\t\treturn KERNEL_ERROR_EIO;', '\t}'),
    ('ee9632be', 'src/kernel/fileSystem.cpp', 1010, '\treturn bytes_read;', '}'),
    ('ee9632be', 'src/common/file.cpp', 163, 'uint64_t File::Size() const {', '\tEXIT_IF(m_p->f == nullptr);'),
    ('ee9632be', 'src/common/file.cpp', 201, 'uint64_t File::Tell() const {', '\tEXIT_IF(m_p->f == nullptr);'),
    ('ee9632be', 'src/common/file.cpp', 207, 'void File::Read(void* data, uint32_t size, uint32_t* bytes_read) {', '\tEXIT_IF(m_p->f == nullptr);'),
    ('ee9632be', 'src/common/platform/sysWindowsFileIO.cpp', 68, '\t\tif (ReadFile(f.handle, data, size, &w, nullptr) == FALSE) {', '\t\t\tstatic int logged = 0;'),
    ('ee9632be', 'src/common/platform/sysWindowsFileIO.cpp', 76, '\t\t\t*bytes_read = w;', '\t\t}'),
    ('ee9632be', 'src/libs/libKernel.cpp', 1418, 'static int64_t KYTY_SYSV_ABI read(int d, void* buf, uint64_t nbytes) {', '\t// PRINT_NAME();'),
    ('ee9632be', 'src/libs/libKernel.cpp', 1436, '\t\treturn POSIX_N_CALL(FileSystem::KernelRead(d, buf, nbytes));', '\t}'),
    ('ee9632be', 'src/libs/libKernel.cpp', 1930, '\treturn POSIX_N_CALL(LibKernel::FileSystem::KernelPread(d, buf, nbytes, offset));', '}'),
    ('ee9632be', 'src/libs/libKernel.cpp', 2993, '\t\t    LibKernel::FileSystem::KernelPread(req[i].fd, req[i].buf, req[i].nbyte, req[i].offse', ''),
    ('ee9632be', 'src/libs/libKernel.cpp', 2995, '\t\treq[i].result->return_value = result;', '\t\treq[i].result->state = (result < 0 ? KERNEL_AIO_STATE_ABORTED : KERNEL_AIO_STATE_COMPLET'),
    ('ee9632be', 'src/libs/libKernel.cpp', 2996, '\t\treq[i].result->state = (result < 0 ? KERNEL_AIO_STATE_ABORTED : KERNEL_AIO_STATE_COMPLET', '\t}'),
    ('ee9632be', 'src/libs/libKernel.cpp', 2224, '\tLIB_FUNC("AqBioC2vF3I", LibKernel::read);', '\tLIB_FUNC("TU-d9PfIHPM", Posix::socket);'),
    ('ee9632be', 'src/libs/libKernel.cpp', 3144, '\tLIB_FUNC("Cg4srZ6TKbU", FileSystem::KernelRead);', '\tLIB_FUNC("4wSze92BhLI", FileSystem::KernelWrite);'),
    ('ee9632be', 'src/libs/libKernel.cpp', 3146, '\tLIB_FUNC("+r3rMFwItV4", FileSystem::KernelPread);', '\tLIB_FUNC("nKWi-N2HBV4", FileSystem::KernelPwrite);'),
    ('ee9632be', 'src/libs/libKernel.cpp', 3369, '\tLIB_FUNC("ezv-RSBNKqI", Posix::pread);', '\tLIB_FUNC("C2kJ-byS5rM", Posix::pwrite);'),
    ('ee9632be', 'src/libs/libKernel.cpp', 3430, '\tLIB_FUNC("DRuBt2pvICk", LibKernel::read);', '\tLIB_FUNC("AqBioC2vF3I", LibKernel::read);'),
    ('ee9632be', 'src/libs/libKernel.cpp', 3431, '\tLIB_FUNC("AqBioC2vF3I", LibKernel::read);', '\tLIB_FUNC("f7KBOafysXo", LibKernel::KernelGetModuleInfoFromAddr);'),
    ('ee9632be', 'src/libs/libKernel.cpp', 3441, '\tLIB_FUNC("HgX7+AORI58", KernelAioSubmitReadCommands);', '\tLIB_FUNC("2pOuoWoCxdk", KernelAioPollRequest);'),
    ('ee9632be', 'src/libs/errno.h', 20, '#define POSIX_N_CALL(func)                                                                ', '\t[&]() {                                                                                  '),
    ('ee9632be', 'src/libs/errno.h', 24, '\t\t\t*Posix::GetErrorAddr() = LibKernel::KernelToPosix(static_cast<int>(result));           ', '\t\t\treturn static_cast<decltype(result)>(-1);                                              '),
    ('ee9632be', 'src/libs/errno.h', 182, 'inline int KernelToPosix(int kernel_errno) {', '\treturn kernel_errno > -2147352576 && kernel_errno <= -2147352475 ? kernel_errno + 2147352'),
    ('ee9632be', 'src/libs/errno.h', 192, 'constexpr int KERNEL_ERROR_EIO             = -2147352571; /* 0x80020005 */', 'constexpr int KERNEL_ERROR_ENXIO           = -2147352570; /* 0x80020006 */'),
    ('ee9632be', 'src/libs/errno.h', 61, 'constexpr int POSIX_EIO               = 5;', 'constexpr int POSIX_ENXIO             = 6;'),
    ('ee9632be', 'src/common/assert.h', 53, '#define EXIT_IF(x)                                                                        ', '\t((void)((x) && Common::DbgExitIfHandler(#x, __FILE__, __LINE__) != 0 && (EXIT_HALT(), 1) '),
    ('ee9632be', 'src/common/assert.cpp', 22, 'static int DbgReport(const char* title, std::string_view text, const char* file, int line)', '\tif (fatal_interceptor) { fatal_interceptor(file, line, text); }'),
    ('ee9632be', 'src/common/assert.cpp', 116, 'void DbgExit(int status) {', '\tif (fatal_interceptor) { fatal_interceptor("DbgExit", status, "explicit fatal exit"); }'),
]


def main():
    ok = True
    for c, p, n, a, b in REFS:
        t = subprocess.run([G, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8').split(chr(10))
        la, lb = t[n - 1] if n - 1 < len(t) else '', t[n] if n < len(t) else ''
        good = la.startswith(a) and lb.startswith(b)
        ok &= good
        print('%s:%s:%d anchor %s +1 %s' % (c, p, n, 'OK' if la.startswith(a) else 'FAIL', 'OK' if lb.startswith(b) else 'FAIL'))
    print('ALL OK' if ok else 'FAIL')


if __name__ == '__main__':
    main()

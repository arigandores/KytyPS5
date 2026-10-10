"""F38a (HPP-763): check of the references <commit>:<path>:<line> of docs/track-f/f38a.md - the line starts with the anchor
and the next line starts with the +1 text (git show of the commit, real git). Generated once by gen_links_f38a.py.
Prints one line per reference and ALL OK / FAIL."""
import subprocess

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
REFS = [
    ('730ed40a', 'src/kernel/fileSystem.cpp', 110, 'static bool FixB4Enabled() {', '\t// Track F, FS6a (HPP-555, ROADMAP s122 item 454(g)(1)): default ON - unset or "" = ON, 0'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 402, 'void Initialize() {', '\tg_mount_points = new MountPoints;'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 406, '\tLOGF("FixB4: mode=%d\\n", FixB4Enabled() ? 1 : 0);', '}'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 762, 'void ReadGuestWithRetry(File* file, void* buf, size_t nbytes, uint64_t pos, uint64_t remai', '                        uint32_t* bytes_read) {'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 764, '\tfile->f.Read(buf, static_cast<uint32_t>(nbytes), bytes_read);', '\tif (*bytes_read != 0 || nbytes == 0 || remaining == 0) {'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 765, '\tif (*bytes_read != 0 || nbytes == 0 || remaining == 0) {', '\t\treturn;'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 775, '\tfile->f.Seek(pos);', '\tfile->f.Read(temporary.data(), static_cast<uint32_t>(nbytes), bytes_read);'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 776, '\tfile->f.Read(temporary.data(), static_cast<uint32_t>(nbytes), bytes_read);', '\tif (*bytes_read != 0) {'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 777, '\tif (*bytes_read != 0) {', '\t\tstd::memcpy(buf, temporary.data(), *bytes_read);'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 782, 'int64_t KYTY_SYSV_ABI KernelRead(int d, void* buf, size_t nbytes) {', '\tPRINT_NAME();'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 826, '\tfile->mutex.Lock();', ''),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 837, '\tReadGuestWithRetry(file, buf, nbytes, pos, remaining, &bytes_read);', '\tStreamTraceMid(stream_read, buf, bytes_read);'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 850, '\tfile->mutex.Unlock();', ''),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 852, '\tif (is_invalid) {', '\t\tLOGF("\\tfile is invalid\\n");'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 854, '\t\treturn KERNEL_ERROR_EIO;', '\t}'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 867, '\treturn bytes_read;', '}'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 941, 'int64_t KYTY_SYSV_ABI KernelPread(int d, void* buf, size_t nbytes, int64_t offset) {', '\tPRINT_NAME();'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 977, '\tfile->mutex.Lock();', ''),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 989, '\tfile->f.Seek(offset);', '\tReadGuestWithRetry(file, buf, nbytes, static_cast<uint64_t>(offset), remaining, &bytes_re'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 990, '\tReadGuestWithRetry(file, buf, nbytes, static_cast<uint64_t>(offset), remaining, &bytes_re', '\tfile->f.Seek(pos);'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 991, '\tfile->f.Seek(pos);', '\tStreamTraceMid(stream_read, buf, bytes_read);'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 1000, '\tfile->mutex.Unlock();', ''),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 1002, '\tif (is_invalid) {', '\t\tLOGF("\\tfile is invalid\\n");'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 1004, '\t\treturn KERNEL_ERROR_EIO;', '\t}'),
    ('730ed40a', 'src/kernel/fileSystem.cpp', 1010, '\treturn bytes_read;', '}'),
    ('730ed40a', 'src/libs/libKernel.cpp', 235, 'int KYTY_SYSV_ABI KernelDlsym(KernelModule handle, const char* symbol, void** addr) {', '\tstatic std::atomic_uint32_t log_count = 0;'),
    ('730ed40a', 'src/libs/libKernel.cpp', 262, '\tconst auto* record = kernel_find_export_symbol(program->export_symbols.get(), symbol);', '\tif (record != nullptr) {'),
    ('730ed40a', 'src/libs/libKernel.cpp', 1418, 'static int64_t KYTY_SYSV_ABI read(int d, void* buf, uint64_t nbytes) {', '\t// PRINT_NAME();'),
    ('730ed40a', 'src/libs/libKernel.cpp', 1435, '\tif (d > 2) {', '\t\treturn POSIX_N_CALL(FileSystem::KernelRead(d, buf, nbytes));'),
    ('730ed40a', 'src/libs/libKernel.cpp', 1436, '\t\treturn POSIX_N_CALL(FileSystem::KernelRead(d, buf, nbytes));', '\t}'),
    ('730ed40a', 'src/libs/libKernel.cpp', 1930, '\treturn POSIX_N_CALL(LibKernel::FileSystem::KernelPread(d, buf, nbytes, offset));', '}'),
    ('730ed40a', 'src/libs/libKernel.cpp', 2148, 'LIB_DEFINE(InitLibKernel_1_Posix) {', '\tLIB_FUNC("k+AXqu2-eBc", getpagesize);'),
    ('730ed40a', 'src/libs/libKernel.cpp', 2224, '\tLIB_FUNC("AqBioC2vF3I", LibKernel::read);', '\tLIB_FUNC("TU-d9PfIHPM", Posix::socket);'),
    ('730ed40a', 'src/libs/libKernel.cpp', 2968, 'int KYTY_SYSV_ABI KernelAioSubmitReadCommands(KernelAioRwRequest* req, int32_t size, int32', '                                              int32_t* id) {'),
    ('730ed40a', 'src/libs/libKernel.cpp', 2993, '\t\t    LibKernel::FileSystem::KernelPread(req[i].fd, req[i].buf, req[i].nbyte, req[i].offse', ''),
    ('730ed40a', 'src/libs/libKernel.cpp', 2995, '\t\treq[i].result->return_value = result;', '\t\treq[i].result->state = (result < 0 ? KERNEL_AIO_STATE_ABORTED : KERNEL_AIO_STATE_COMPLET'),
    ('730ed40a', 'src/libs/libKernel.cpp', 2996, '\t\treq[i].result->state = (result < 0 ? KERNEL_AIO_STATE_ABORTED : KERNEL_AIO_STATE_COMPLET', '\t}'),
    ('730ed40a', 'src/libs/libKernel.cpp', 3141, 'LIB_DEFINE(InitLibKernel_1_FS) {', '\tLIB_FUNC("1G3lF1Gg1k8", FileSystem::KernelOpen);'),
    ('730ed40a', 'src/libs/libKernel.cpp', 3144, '\tLIB_FUNC("Cg4srZ6TKbU", FileSystem::KernelRead);', '\tLIB_FUNC("4wSze92BhLI", FileSystem::KernelWrite);'),
    ('730ed40a', 'src/libs/libKernel.cpp', 3146, '\tLIB_FUNC("+r3rMFwItV4", FileSystem::KernelPread);', '\tLIB_FUNC("nKWi-N2HBV4", FileSystem::KernelPwrite);'),
    ('730ed40a', 'src/libs/libKernel.cpp', 3248, 'LIB_DEFINE(InitLibKernel_1_Pthread) {', '\tLIB_FUNC("9UK1vLZQft4", LibKernel::PthreadMutexLock);'),
    ('730ed40a', 'src/libs/libKernel.cpp', 3369, '\tLIB_FUNC("ezv-RSBNKqI", Posix::pread);', '\tLIB_FUNC("C2kJ-byS5rM", Posix::pwrite);'),
    ('730ed40a', 'src/libs/libKernel.cpp', 3395, 'LIB_DEFINE(InitLibKernel_1) {', '\tLIB_FUNC("04AjkP0jO9U", Posix::UmtxOp);'),
    ('730ed40a', 'src/libs/libKernel.cpp', 3430, '\tLIB_FUNC("DRuBt2pvICk", LibKernel::read);', '\tLIB_FUNC("AqBioC2vF3I", LibKernel::read);'),
    ('730ed40a', 'src/libs/libKernel.cpp', 3431, '\tLIB_FUNC("AqBioC2vF3I", LibKernel::read);', '\tLIB_FUNC("f7KBOafysXo", LibKernel::KernelGetModuleInfoFromAddr);'),
    ('730ed40a', 'src/libs/libKernel.cpp', 3441, '\tLIB_FUNC("HgX7+AORI58", KernelAioSubmitReadCommands);', '\tLIB_FUNC("2pOuoWoCxdk", KernelAioPollRequest);'),
    ('730ed40a', 'src/libs/errno.h', 20, '#define POSIX_N_CALL(func)                                                                ', '\t[&]() {                                                                                  '),
    ('730ed40a', 'src/libs/errno.h', 24, '\t\t\t*Posix::GetErrorAddr() = LibKernel::KernelToPosix(static_cast<int>(result));           ', '\t\t\treturn static_cast<decltype(result)>(-1);                                              '),
    ('730ed40a', 'src/libs/errno.h', 61, 'constexpr int POSIX_EIO               = 5;', 'constexpr int POSIX_ENXIO             = 6;'),
    ('730ed40a', 'src/libs/errno.h', 182, 'inline int KernelToPosix(int kernel_errno) {', '\treturn kernel_errno > -2147352576 && kernel_errno <= -2147352475 ? kernel_errno + 2147352'),
    ('730ed40a', 'src/libs/errno.h', 192, 'constexpr int KERNEL_ERROR_EIO             = -2147352571; /* 0x80020005 */', 'constexpr int KERNEL_ERROR_ENXIO           = -2147352570; /* 0x80020006 */'),
    ('730ed40a', 'src/common/file.cpp', 163, 'uint64_t File::Size() const {', '\tEXIT_IF(m_p->f == nullptr);'),
    ('730ed40a', 'src/common/file.cpp', 170, '\treturn SysFileSize(*m_p->f);', '}'),
    ('730ed40a', 'src/common/platform/sysWindowsFileIO.cpp', 267, '\t\tGetFileSizeEx(f.handle, &s);', '\t\treturn s.QuadPart;'),
    ('730ed40a', 'tests/KernelFileSystemTests.cpp', 158, '  Check(FileSystem::KernelRead(fd, raw.data(), raw.size()) == end &&', '            FileSystem::KernelRead(fd, raw.data(), 1) == 0,'),
]


def main():
    ok = True
    cache = {}
    for c, path, n, anchor, nxt in REFS:
        key = (c, path)
        if key not in cache:
            out = subprocess.run([G, '-C', REPO, 'show', '%s:%s' % key], capture_output=True).stdout
            cache[key] = [x.rstrip('\r') for x in out.decode('utf-8').split('\n')]
        rows = cache[key]
        good = len(rows) > n and rows[n - 1].startswith(anchor) and rows[n].startswith(nxt)
        ok &= good
        print('%s %s:%s:%d' % ('OK  ' if good else 'FAIL', c, path, n))
    print('refs %d' % len(REFS))
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())

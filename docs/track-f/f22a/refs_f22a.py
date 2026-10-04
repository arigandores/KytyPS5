# F22a (HPP-576; form of f21a/refs_f21a.py): references of f22a.md (general rule 24(1)): <commit>:<path>:<line> with an
# anchor and the +1 control.
#   python refs_f22a.py <refs.tsv> [<report.md>]
# writes <refs.tsv> (commit, path, line, anchor, +1 text) from SPEC after checking every row against
# 'git show <commit>:<path>' (the anchor must stand in the line, the +1 text must start the next line), then checks
# that every 'name.ext:<line>' written in the report (md, cpp, h, inc) is a row of the table.  Prints 'refs N of N',
# 'report refs M of M', 'ALL OK'.
import re, subprocess, sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
RM = '764617c7'
REG = '58b6c5ad'
SRC = 'f70a2232'
FS = 'src/kernel/fileSystem.cpp'
WF = 'src/common/platform/sysWindowsFileIO.cpp'
LK = 'src/libs/libKernel.cpp'
NW = 'src/libs/network.cpp'
AM = 'src/libs/libAmpr.cpp'
SD = 'src/libs/libSaveData.cpp'
LH = 'src/libs/libs.h'
SPEC = [
    (RM, 'docs/ROADMAP.md', 22642, '474. **Звено F21b трека F (`HPP-564`, лид; приёмка F21a', '(а) **Приёмка строкой. F21a ✓**'),
    (RM, 'docs/ROADMAP.md', 22648, '(е) **Следующая итерация очереди F — F22 = Ф4 (Q5), офлайн, без замка; исполнитель — Probe Designer.**', '(ж) **Звенья (стадия review лида у каждого звена исполнителя):**'),
    (REG, 'docs/track-f/register.md', 160, '| Ф4 | K4 | наблюдение (обход действует [c])', '| Б1а | K4'),
    (REG, 'docs/track-f/register.md', 831, '| Q5 | Ф4 | K4 | наблюдение |', '| Q6 | Б7, Б8 | K4 | наблюдение |'),
    (SRC, FS, 762, 'void ReadGuestWithRetry(File* file, void* buf, size_t nbytes, uint64_t pos, uint64_t remaining,', 'uint32_t* bytes_read) {'),
    (SRC, FS, 764, 'file->f.Read(buf, static_cast<uint32_t>(nbytes), bytes_read);', 'if (*bytes_read != 0 || nbytes == 0 || remaining == 0) {'),
    (SRC, FS, 768, 'static int logged = 0;', 'if (logged++ < 32) {'),
    (SRC, FS, 770, 'LOGF("KernelRead: direct read failed, dst=0x%016" PRIx64 " size=0x%" PRIx64', '": reading through a host buffer\\n",'),
    (SRC, FS, 774, 'std::vector<uint8_t> temporary(nbytes);', 'file->f.Seek(pos);'),
    (SRC, FS, 775, 'file->f.Seek(pos);', 'file->f.Read(temporary.data(), static_cast<uint32_t>(nbytes), bytes_read);'),
    (SRC, FS, 778, 'std::memcpy(buf, temporary.data(), *bytes_read);', '}'),
    (SRC, FS, 782, 'int64_t KYTY_SYSV_ABI KernelRead(int d, void* buf, size_t nbytes) {', 'PRINT_NAME();'),
    (SRC, FS, 794, 'const auto result = ::Libs::Network::Net::Recv(d, buf, nbytes, 0);', 'return (result >= 0 ? result : PosixToKernel(*Posix::GetErrorAddr()));'),
    (SRC, FS, 811, 'const auto        bytes = ReadDirectory(file, buf, nbytes);', 'LOGF("\\tRead %" PRIu64 " directory bytes from: %s\\n", bytes,'),
    (SRC, FS, 818, 'FillRandomBuffer(buf, nbytes);', ''),
    (SRC, FS, 831, 'const auto remaining  = pos < file_size ? file_size - pos : 0;', 'auto stream_read = StreamTraceBegin(buf, std::min<uint64_t>(nbytes, remaining),'),
    (SRC, FS, 834, 'Memory::InvalidateMemory(reinterpret_cast<uint64_t>(buf),', 'std::min<uint64_t>(nbytes, remaining));'),
    (SRC, FS, 837, 'ReadGuestWithRetry(file, buf, nbytes, pos, remaining, &bytes_read);', 'StreamTraceMid(stream_read, buf, bytes_read);'),
    (SRC, FS, 857, 'LOGF("\\tRead %u bytes from: %s\\n", bytes_read, Common::PathToString(file->real_name).c_str());', 'static const bool stream_trace = Common::EnvFlagOn("KYTY_STREAM_TRACE");'),
    (SRC, FS, 941, 'int64_t KYTY_SYSV_ABI KernelPread(int d, void* buf, size_t nbytes, int64_t offset) {', 'PRINT_NAME();'),
    (SRC, FS, 989, 'file->f.Seek(offset);', 'ReadGuestWithRetry(file, buf, nbytes, static_cast<uint64_t>(offset), remaining, &bytes_read);'),
    (SRC, FS, 990, 'ReadGuestWithRetry(file, buf, nbytes, static_cast<uint64_t>(offset), remaining, &bytes_read);', 'file->f.Seek(pos);'),
    (SRC, FS, 1007, 'LOGF("\\tRead %u bytes (pos = %" PRId64 ") from: %s\\n", bytes_read, offset,', 'Common::PathToString(file->real_name).c_str());'),
    (SRC, FS, 1393, 'ReadDirectory(file, buf, AlignDown(static_cast<uint64_t>(nbytes), DIR_BLOCK_SIZE)));', ''),
    (SRC, FS, 189, 'memcpy(buf, file->dirents.data() + file->dents_offset, bytes);', ''),
    (SRC, WF, 68, 'if (ReadFile(f.handle, data, size, &w, nullptr) == FALSE) {', 'static int logged = 0;'),
    (SRC, WF, 71, 'printf("SysFileRead: ReadFile failed, error=%lu size=%u data=%p\\n",', 'static_cast<unsigned long>(GetLastError()), size, data);'),
    (SRC, WF, 326, 'ok         = (SetFilePointerEx(f.handle, s, nullptr, FILE_BEGIN) != 0);', '// printf("seek: %u\\n", offset);'),
    (SRC, LK, 1432, 'return Network::Net::Recv(d, buf, nbytes, 0);', '}'),
    (SRC, LK, 1436, 'return POSIX_N_CALL(FileSystem::KernelRead(d, buf, nbytes));', '}'),
    (SRC, LK, 1443, 'auto* str = std::fgets(static_cast<char*>(buf), static_cast<int>(nbytes), stdin);', ''),
    (SRC, LK, 1930, 'return POSIX_N_CALL(LibKernel::FileSystem::KernelPread(d, buf, nbytes, offset));', '}'),
    (SRC, LK, 2040, 'return Network::Net::Recvfrom(s, buf, len, flags, addr, addrlen);', '}'),
    (SRC, LK, 2993, 'LibKernel::FileSystem::KernelPread(req[i].fd, req[i].buf, req[i].nbyte, req[i].offset);', ''),
    (SRC, LK, 3144, 'LIB_FUNC("Cg4srZ6TKbU", FileSystem::KernelRead);', 'LIB_FUNC("4wSze92BhLI", FileSystem::KernelWrite);'),
    (SRC, LK, 3146, 'LIB_FUNC("+r3rMFwItV4", FileSystem::KernelPread);', 'LIB_FUNC("nKWi-N2HBV4", FileSystem::KernelPwrite);'),
    (SRC, LK, 3369, 'LIB_FUNC("ezv-RSBNKqI", Posix::pread);', 'LIB_FUNC("C2kJ-byS5rM", Posix::pwrite);'),
    (SRC, LK, 3430, 'LIB_FUNC("DRuBt2pvICk", LibKernel::read);', 'LIB_FUNC("AqBioC2vF3I", LibKernel::read);'),
    (SRC, LK, 3441, 'LIB_FUNC("HgX7+AORI58", KernelAioSubmitReadCommands);', 'LIB_FUNC("2pOuoWoCxdk", KernelAioPollRequest);'),
    (SRC, LK, 2224, 'LIB_FUNC("AqBioC2vF3I", LibKernel::read);', 'LIB_FUNC("TU-d9PfIHPM", Posix::socket);'),
    (SRC, LK, 2236, 'LIB_FUNC("Ez8xjo9UF4E", Posix::recv);', 'LIB_FUNC("lUk6wrGXyMw", Posix::recvfrom);'),
    (SRC, NW, 2004, 'LOGF("\\t s     = %d\\n"', '"\\t buf   = 0x%016" PRIx64 "\\n"'),
    (SRC, NW, 2035, 'result = ::recv(socket, static_cast<char*>(buf), host_len, host_flags);', '} else {'),
    (SRC, NW, 2037, 'result = ::recvfrom(socket, static_cast<char*>(buf), host_len, host_flags,', 'reinterpret_cast<sockaddr*>(&host_addr), &host_addrlen);'),
    (SRC, AM, 1485, 'std::vector<uint8_t> buffer(', 'static_cast<size_t>(std::min<uint64_t>(APR_HOST_READ_CHUNK_SIZE, readable)));'),
    (SRC, AM, 1491, 'file.Read(buffer.data(), request, &read);', 'if (read == 0) {'),
    (SRC, AM, 1495, 'std::memcpy(reinterpret_cast<void*>(destination + *bytes_read), buffer.data(), read);', '*bytes_read += read;'),
    (SRC, AM, 1370, 'auto result = ReadHostFileToGuest(host_path, command.file_offset,', 'command.destination, command.size, &bytes_read);'),
    (SRC, SD, 370, 'file.Read(payload.data(), static_cast<uint32_t>(payload.size()), &read);', 'if (read != payload.size() || save_memory_hash(payload.data(), payload.size()) != payload_hash) {'),
    (SRC, LH, 58, 'LOGF_COLOR(Log::Color::Cyan, "[%d][%s] %s::%s::%s()\\n",', 'Common::Thread::GetThreadIdUnique(), print_name_time.c_str(), g_library,'),
]
tsv = sys.argv[1]
report = sys.argv[2] if len(sys.argv) > 2 else None
cache = {}


def lines(commit, path):
    if (commit, path) not in cache:
        o = subprocess.run([GIT, '-C', REPO, 'show', commit + ':' + path], capture_output=True)
        cache[(commit, path)] = o.stdout.decode('utf-8', 'replace').split(chr(10))
    return cache[(commit, path)]


ok = 0
names = set()
rows = []
for commit, path, line, anchor, plus1 in SPEC:
    L = lines(commit, path)
    a = L[line - 1] if line - 1 < len(L) else ''
    b = L[line] if line < len(L) else ''
    good = anchor in a and b.strip().startswith(plus1)
    ok += good
    if not good:
        print('FAIL %s:%s:%d' % (commit, path, line))
        for i, x in enumerate(L):
            if anchor in x:
                print('   anchor found at line %d; next line starts %r' % (i + 1, L[i + 1].strip()[:80] if i + 1 < len(L) else ''))
        print('   line %d is %r; +1 is %r' % (line, a.strip()[:100], b.strip()[:100]))
    names.add((path.rsplit('/', 1)[1], line))
    rows.append(chr(9).join([commit, path, str(line), anchor, plus1]))
with open(tsv, 'w', encoding='utf-8', newline=chr(10)) as f:
    f.write(chr(10).join(rows) + chr(10))
print('refs %d of %d' % (ok, len(SPEC)))
miss = []
cited = set()
if report:
    text = open(report, encoding='utf-8').read()
    cited = set((m.group(1), int(m.group(2))) for m in re.finditer(r'([A-Za-z0-9_]+[.](?:md|cpp|h|inc)):(\d+)', text))
    miss = sorted(c for c in cited if c not in names)
    for c in miss:
        print('NOT IN TABLE %s:%d' % c)
    print('report refs %d of %d' % (len(cited) - len(miss), len(cited)))
good = ok == len(SPEC) and not miss
print('ALL OK' if good else 'FAILED')
sys.exit(0 if good else 1)

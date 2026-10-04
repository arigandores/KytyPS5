# F15c (HPP-514, ROADMAP s122 items 412(v), 417(b)-(v), row B4): KYTY_FIX_B4 (default 0) in src/kernel/fileSystem.cpp.
# Anchors - whole lines (a block replace - whole consecutive lines); CR stripped before the search and restored after;
# fails when an anchor is not found exactly once. Usage: python patch_f15c_src.py <repo root>
import sys

root = sys.argv[1]
path = root + '/src/kernel/fileSystem.cpp'
data = open(path, 'rb').read()
crlf = b'\r\n' in data
text = data.replace(b'\r\n', b'\n').decode('utf-8')
lines = text.split('\n')


def find_block(block):
    n = len(block)
    hits = [i for i in range(len(lines) - n + 1) if lines[i:i + n] == block]
    if len(hits) != 1:
        print('ANCHOR hits', len(hits), repr(block[0]))
        sys.exit(1)
    return hits[0]


# 1. Declaration of FlushAll after CloseAll in class FileDescriptors.
i = find_block(['\tFile* GetFile(const std::filesystem::path& real_name);', '\tvoid  CloseAll();'])
lines[i + 2:i + 2] = ['\tvoid  FlushAll();']

# 2. The knob and the host constant after the two globals.
i = find_block(['static MountPoints*     g_mount_points = nullptr;', 'static FileDescriptors* g_files        = nullptr;'])
lines[i + 2:i + 2] = [
    '',
    '// Track F, F15c (ROADMAP s122 items 412(v), 417(b)-(v), row B4): KYTY_FIX_B4 (default 0), read once. At 1 the',
    '// emergency exit path (at_quick_exit and atexit(KytyClose) of src/emulator.cpp, both end in EmergencyShutdown below)',
    '// keeps every File object, slot and host descriptor: guest threads are still running there and may hold a File* from',
    '// GetFile without m_mutex, so CloseAll deleting it races with them (DeleteDescriptor / KernelOpen EXIT_IF or a',
    '// use-after-free). The OS closes the host descriptors at the end of the process. Unset or empty - OFF.',
    'static bool FixB4Enabled() {',
    '\tstatic const bool enabled = Common::EnvValueOn(std::getenv("KYTY_FIX_B4"));',
    '\treturn enabled;',
    '}',
    '',
    '// Host write path with a user-space buffer that _Exit does not flush: stdio fwrite on non-Windows hosts',
    '// (sysLinuxFileIO.cpp SysFileWrite). Windows SysFileWrite is WriteFile with no user buffer (sysWindowsFileIO.cpp).',
    'constexpr bool HOST_FILE_WRITE_BUFFERED = (KYTY_PLATFORM != KYTY_PLATFORM_WINDOWS);',
]

# 3. FlushAll definition after CloseAll (before MountPoints::Mount).
i = find_block(['void MountPoints::Mount(const std::filesystem::path& folder, const std::string& point) {'])
lines[i:i] = [
    '// B4, KYTY_FIX_B4=1 (variant A\', ROADMAP s122 item 417(v)): flush the user buffer of every open writable host file',
    '// and nothing else - no Close, no delete, no nullptr. On Windows there is no user buffer: nothing is done.',
    'void FileDescriptors::FlushAll() {',
    '\tif constexpr (HOST_FILE_WRITE_BUFFERED) {',
    '\t\tCommon::LockGuard lock(m_mutex);',
    '',
    '\t\tfor (auto* f: m_files) {',
    '\t\t\tif (f != nullptr && f->opened && f->writable && !f->directory &&',
    '\t\t\t    f->special == SpecialFile::None) {',
    '\t\t\t\tf->f.Flush();',
    '\t\t\t}',
    '\t\t}',
    '\t}',
    '}',
    '',
]

# 4. Initialize / EmergencyShutdown / Shutdown.
old = [
    'void Initialize() {',
    '\tg_mount_points = new MountPoints;',
    '\tg_files        = new FileDescriptors;',
    '}',
    '',
    'void EmergencyShutdown() {',
    '\tif (g_files != nullptr) {',
    '\t\tg_files->CloseAll();',
    '\t}',
    '}',
    '',
    'void Shutdown() {',
    '\tEmergencyShutdown();',
    '\tdelete g_files;',
]
new = [
    'void Initialize() {',
    '\tg_mount_points = new MountPoints;',
    '\tg_files        = new FileDescriptors;',
    '',
    '\tLOGF("FixB4: mode=%d\\n", FixB4Enabled() ? 1 : 0);',
    '}',
    '',
    'void EmergencyShutdown() {',
    '\tif (g_files != nullptr) {',
    '\t\tif (FixB4Enabled()) {',
    '\t\t\t// B4: guest threads may still be inside KernelOpen/KernelClose with a File* of a slot.',
    '\t\t\tg_files->FlushAll();',
    '\t\t} else {',
    '\t\t\tg_files->CloseAll();',
    '\t\t}',
    '\t}',
    '}',
    '',
    '// Path without guest threads (Subsystems::Destroy: tests, stands): CloseAll at both values of KYTY_FIX_B4.',
    'void Shutdown() {',
    '\tif (g_files != nullptr) {',
    '\t\tg_files->CloseAll();',
    '\t}',
    '\tdelete g_files;',
]
i = find_block(old)
lines[i:i + len(old)] = new

out = '\n'.join(lines).encode('utf-8')
if crlf:
    out = out.replace(b'\n', b'\r\n')
open(path, 'wb').write(out)
print('PATCH OK crlf', crlf)

import os
paths = [os.environ['PAPERCLIP_RUN_SCRATCH_DIR'] + '/log.cpp', 'C:/kyty/f287/f25k/log.cpp',
         'C:/kyty/f287/f25k/wt/src/common/logging/log.cpp']
edits = [
    ('''#include <string_view>
#include <thread>
''', '''#include <string_view>
#include <thread>

#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h> // F25k: SetThreadDescription of the writer thread
#endif
'''),
    ('''static void WriterMain() {
	t_writer = true;
''', '''static void WriterMain() {
	t_writer = true;
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
	// The thread name "LogWriter" for the KYTY_DIAG_B32 thread rows (looked up as diagB32.cpp does for DiagB32M5).
	using SetThreadDescriptionFn = HRESULT(WINAPI*)(HANDLE, PCWSTR);
	if (HMODULE k32 = GetModuleHandleW(L"kernel32.dll"); k32 != nullptr) {
		if (auto set_fn = reinterpret_cast<SetThreadDescriptionFn>(
		        reinterpret_cast<void*>(GetProcAddress(k32, "SetThreadDescription")));
		    set_fn != nullptr) {
			set_fn(GetCurrentThread(), L"LogWriter");
		}
	}
#endif
'''),
]
for p in paths:
    t = open(p, 'rb').read().decode().replace('\r', '')
    for old, new in edits:
        assert t.count(old) == 1, (p, old[:40])
        t = t.replace(old, new)
    open(p, 'wb').write(t.encode())
print('ok')

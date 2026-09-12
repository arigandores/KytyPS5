// External Windows x64 diagnostic: PID and output prefix. No GPU calls.
#define NOMINMAX
#include <windows.h>
#include <tlhelp32.h>
#include <dbghelp.h>
#include <array>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <string>

int main(int argc, char** argv) {
	if (argc != 3) return 2;
	const DWORD pid = std::strtoul(argv[1], nullptr, 10);
	HANDLE process = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, pid);
	if (!process) return 3;
	const std::string prefix = argv[2];
	std::ofstream out(prefix + ".stacks.txt");
	HANDLE dump = CreateFileA((prefix + ".dmp").c_str(), GENERIC_WRITE, 0, nullptr,
	                          CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
	if (dump != INVALID_HANDLE_VALUE) {
		const auto kind = static_cast<MINIDUMP_TYPE>(MiniDumpNormal | MiniDumpWithThreadInfo |
		                                           MiniDumpWithUnloadedModules);
		const BOOL ok = MiniDumpWriteDump(process, pid, dump, kind, nullptr, nullptr, nullptr);
		out << "minidump=" << ok << " error=" << (ok ? 0 : GetLastError()) << '\n';
		CloseHandle(dump);
	}
	SymSetOptions(SYMOPT_UNDNAME | SYMOPT_DEFERRED_LOADS | SYMOPT_FAIL_CRITICAL_ERRORS |
	              SYMOPT_NO_PROMPTS);
	if (!SymInitialize(process, "C:\\kyty\\build", TRUE)) {
		out << "SymInitialize failed " << GetLastError() << '\n';
		CloseHandle(process);
		return 4;
	}
	HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
	THREADENTRY32 entry {};
	entry.dwSize = sizeof(entry);
	for (BOOL found = Thread32First(snapshot, &entry); found; found = Thread32Next(snapshot, &entry)) {
		if (entry.th32OwnerProcessID != pid) continue;
		HANDLE thread = OpenThread(THREAD_GET_CONTEXT | THREAD_SUSPEND_RESUME |
		                          THREAD_QUERY_INFORMATION, FALSE, entry.th32ThreadID);
		if (!thread) continue;
		PWSTR description = nullptr;
		GetThreadDescription(thread, &description);
		std::wstring wide = description ? description : L"";
		if (description) LocalFree(description);
		const int bytes = WideCharToMultiByte(CP_UTF8, 0, wide.data(), static_cast<int>(wide.size()),
		                                      nullptr, 0, nullptr, nullptr);
		std::string name(bytes, '\0');
		if (bytes != 0) WideCharToMultiByte(CP_UTF8, 0, wide.data(), static_cast<int>(wide.size()),
		                                    name.data(), bytes, nullptr, nullptr);
		out << "\nthread=" << entry.th32ThreadID << " name=" << name << '\n';
		if (SuspendThread(thread) == static_cast<DWORD>(-1)) { CloseHandle(thread); continue; }
		CONTEXT context {};
		context.ContextFlags = CONTEXT_FULL;
		std::array<DWORD64, 49> frames {};
		size_t frame_count = 0;
		if (GetThreadContext(thread, &context)) {
			STACKFRAME64 frame {};
			frame.AddrPC = {context.Rip, 0, AddrModeFlat};
			frame.AddrStack = {context.Rsp, 0, AddrModeFlat};
			frame.AddrFrame = {context.Rbp, 0, AddrModeFlat};
			frames[frame_count++] = context.Rip;
			for (unsigned i = 0; i < 48; ++i) {
				if (!StackWalk64(IMAGE_FILE_MACHINE_AMD64, process, thread, &frame, &context,
				                 nullptr, SymFunctionTableAccess64, SymGetModuleBase64, nullptr) ||
				    frame.AddrPC.Offset == 0) break;
				if (frame.AddrPC.Offset != frames[frame_count - 1]) frames[frame_count++] = frame.AddrPC.Offset;
			}
		}
		ResumeThread(thread);
		CloseHandle(thread);
		for (size_t i = 0; i < frame_count; ++i) {
			const auto address = frames[i];
			IMAGEHLP_MODULE64 module {};
			module.SizeOfStruct = sizeof(module);
			const BOOL known_module = SymGetModuleInfo64(process, address, &module);
			alignas(SYMBOL_INFO) unsigned char storage[sizeof(SYMBOL_INFO) + MAX_SYM_NAME] {};
			auto* symbol = reinterpret_cast<SYMBOL_INFO*>(storage);
			symbol->SizeOfStruct = sizeof(SYMBOL_INFO);
			symbol->MaxNameLen = MAX_SYM_NAME;
			DWORD64 displacement = 0;
			const BOOL known_symbol = SymFromAddr(process, address, &displacement, symbol);
			out << "  0x" << std::hex << address << " "
			    << (known_module ? module.ModuleName : "?") << "+0x"
			    << (known_module ? address - module.BaseOfImage : address);
			if (known_symbol) out << " " << symbol->Name << "+0x" << displacement;
			out << std::dec << '\n';
		}
		out.flush();
	}
	CloseHandle(snapshot);
	SymCleanup(process);
	CloseHandle(process);
	return 0;
}

# Windows hang diagnostics

Build `windows_hang_dump.cpp` from an x64 Visual Studio Developer Command Prompt:

```bat
cl /nologo /O2 /EHsc /std:c++20 tools\windows_hang_dump.cpp /Fe:C:\kyty\windows_hang_dump.exe /link dbghelp.lib
```

The external helper takes a PID and output prefix. It writes a normal minidump
with thread information and a text file containing thread stacks. It uses no GPU
API calls. It briefly suspends each target thread while unwinding, then resumes
it before printing symbols. Addresses and module offsets remain useful when
private symbols are unavailable; exported names may identify only a nearby symbol.
Preserve the emulator's matching linker map before rebuilding.

`watch_emulator.py PID LOG OUTPUT_PREFIX --dump-tool EXE` watches `FrameTrace:`
records in the log. It validates that the PID's executable is `kyty_emulator.exe`
beside that log, and retains the process handle to avoid acting on a reused PID.
After frame14000, twelve seconds without a new frame triggers the external dump.
The watcher then terminates that same process directly, avoiding calls to a
potentially stalled window manager. It never resets the graphics driver.

An active user-triggered RenderDoc capture suspends the frame and memory checks
until its finish/failure log record. The watcher neither captures nor records
input. It also closes a non-capturing run when the logged VMA device-heap usage
reaches the configured threshold (default13900 MiB, or512 MiB below the logged
budget if lower, intended for the local16 GB GPU). Memory pressure uses WM_CLOSE
first and termination after five seconds if needed.
Set `--memory-limit-mb`, `--min-frame`, and `--stall-seconds` for other hardware
and routes. Enable `KYTY_IMAGE_MEMORY_TRACE=1` for memory samples. The watchdog
makes no driver queries: a previous nvidia-smi timeout itself blocked during an
actual driver hang, preventing timely stack collection. Missing VMA samples do
not prevent hang detection.

This is an opt-in diagnostic, not proof that a GPU hang can always be recovered
by terminating its process. The minidump is written to the local output path only.

The helper and watchdog were checked with a separate test process: capture
exemption, resumed monitoring, successful minidump/stack collection, and closing
only the monitored process. The actual intermittent game hang is still unresolved.

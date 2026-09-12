"""Watch a local Kyty run; capture CPU stacks before closing a stalled emulator.

Never records input or triggers RenderDoc. An active user-triggered capture suspends
the frame watchdog. Requires windows_hang_dump.exe compiled separately with DbgHelp.
"""
import argparse
import ctypes
import json
import pathlib
import re
import subprocess
import time

parser = argparse.ArgumentParser()
parser.add_argument('pid', type=int)
parser.add_argument('log', type=pathlib.Path)
parser.add_argument('output', type=pathlib.Path)
parser.add_argument('--dump-tool', required=True, type=pathlib.Path)
parser.add_argument('--stall-seconds', type=float, default=12)
parser.add_argument('--min-frame', type=int, default=14000)
parser.add_argument('--memory-limit-mb', type=int, default=13900)
args = parser.parse_args()
kernel = ctypes.WinDLL('kernel32', use_last_error=True)
user = ctypes.WinDLL('user32', use_last_error=True)
kernel.OpenProcess.restype = ctypes.c_void_p
kernel.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
kernel.QueryFullProcessImageNameW.argtypes = [ctypes.c_void_p, ctypes.c_ulong,
                                            ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_ulong)]
kernel.TerminateProcess.argtypes = [ctypes.c_void_p, ctypes.c_uint]
kernel.CloseHandle.argtypes = [ctypes.c_void_p]
callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
user.EnumWindows.argtypes = [callback_type, ctypes.c_void_p]
user.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
user.PostMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]
handle = kernel.OpenProcess(0x1001, False, args.pid)  # query + terminate; stable process identity
if not handle:
    raise ctypes.WinError(ctypes.get_last_error())


def alive():
    code = ctypes.c_ulong()
    return bool(kernel.GetExitCodeProcess(handle, ctypes.byref(code))) and code.value == 259


@callback_type
def close_window(hwnd, unused):
    owner = ctypes.c_ulong()
    user.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
    if owner.value == args.pid:
        user.PostMessageW(hwnd, 0x10, 0, 0)  # WM_CLOSE
    return True


def stop_emulator():
    if not alive():
        return
    print('Posting WM_CLOSE to monitored emulator', args.pid, flush=True)
    user.EnumWindows(close_window, None)
    deadline = time.monotonic() + 5
    while alive() and time.monotonic() < deadline:
        time.sleep(.25)
    if alive():
        print('Emulator did not exit; terminating the same process handle', flush=True)
        if not kernel.TerminateProcess(handle, 1):
            raise ctypes.WinError(ctypes.get_last_error())


try:
    executable = ctypes.create_unicode_buffer(32768)
    length = ctypes.c_ulong(len(executable))
    if not kernel.QueryFullProcessImageNameW(handle, 0, executable, ctypes.byref(length)):
        raise ctypes.WinError(ctypes.get_last_error())
    expected = args.log.resolve().parent / 'kyty_emulator.exe'
    if pathlib.Path(executable.value).resolve() != expected:
        raise RuntimeError('Refusing to control a process outside the specified emulator directory')
    if not args.dump_tool.is_file():
        raise RuntimeError('Missing stack dump helper')
    position, frame, last_frame = 0, 0, 0
    used, budget = None, None
    pending = b''
    capture = False
    last_progress = time.monotonic()
    while alive():
        if args.log.exists():
            with args.log.open('rb') as stream:
                stream.seek(position)
                data = pending + stream.read()
                position = stream.tell()
            lines = data.split(b'\n')
            pending = lines.pop()
            for line in lines:
                if line.startswith(b'FrameTrace:'):
                    frame = int(re.search(rb'n=(\d+)', line)[1])
                elif line.startswith(b'RenderDoc: capture started'):
                    capture = True
                elif line.startswith((b'RenderDoc: capture finished', b'RenderDoc: capture failed')):
                    capture = False
                    last_progress = time.monotonic()
                elif line.startswith((b'ImageMemory:', b'GpuWaitSlow:')):
                    print(line.decode(errors='replace'), flush=True)
                elif line.startswith(b'VMA heap 0:'):
                    match = re.search(rb'usage=(\d+), budget=(\d+)', line)
                    if match:
                        used, budget = (int(value) // (1 << 20) for value in match.groups())
        if frame != last_frame:
            last_frame = frame
            last_progress = time.monotonic()
        stalled = time.monotonic() - last_progress
        # Do not query the graphics driver here. Even killing a timed-out
        # nvidia-smi process can block during a driver hang. Existing VMA log
        # samples suffice for the independent memory-pressure check.
        print(json.dumps(dict(time=time.strftime('%H:%M:%S'), frame=frame,
                              stalled_s=round(stalled, 1), capture=capture,
                              vma_mb=used, budget_mb=budget)), flush=True)
        if not capture and frame >= args.min_frame and stalled >= args.stall_seconds:
            print('Saving hang diagnostic before closing emulator', flush=True)
            helper = subprocess.Popen([str(args.dump_tool), str(args.pid), str(args.output)],
                                      creationflags=0x08000000)
            try:
                print('Dump helper exit', helper.wait(timeout=30), flush=True)
            except subprocess.TimeoutExpired:
                # Do not leave a thread suspended if the helper itself gets stuck.
                # Close the target before terminating the diagnostic helper.
                print('Dump helper timeout; terminating target before helper', flush=True)
                if alive():
                    kernel.TerminateProcess(handle, 1)
                helper.kill()
                helper.wait()
            # A hung display can also stall window-manager calls. Data has been
            # collected; terminate this process directly instead of querying windows.
            if alive():
                print('Terminating stalled emulator after snapshot', flush=True)
                if not kernel.TerminateProcess(handle, 1):
                    raise ctypes.WinError(ctypes.get_last_error())
            break
        memory_limit = min(args.memory_limit_mb, max(0, budget - 512)) if budget else args.memory_limit_mb
        if not capture and frame >= args.min_frame and used and used >= memory_limit:
            print('Memory threshold reached', flush=True)
            stop_emulator()
            break
        time.sleep(2)
finally:
    kernel.CloseHandle(handle)

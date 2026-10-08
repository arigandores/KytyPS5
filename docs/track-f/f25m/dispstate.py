# dispstate.py - console display state (GUID_CONSOLE_DISPLAY_STATE) and user idle time.
# ASCII output only. Usage:
#   python dispstate.py                 -> one line: "dispstate ON|OFF|DIMMED|UNKNOWN idle_s <n> utc <t>"
#   python dispstate.py --hold <sec>    -> SetThreadExecutionState(CONTINUOUS|DISPLAY_REQUIRED|SYSTEM_REQUIRED),
#                                          watch state changes for <sec>, then reset to ES_CONTINUOUS (probe, ROADMAP p.620(v)(3))
#   python dispstate.py --hold-until <stopfile> --max <sec>
#                                       -> the chain mode of go_f25m.sh: the same request until the stop file appears or <sec> pass
#   python dispstate.py --wake          -> wake a display that is OFF (SC_MONITORPOWER, then a +1/-1 mouse nudge); user direction
#                                          2026-10-07 23:39Z in HPP-680: a display OFF is not a reason to stop the series
# Exit code: 0 ON, 1 OFF, 2 DIMMED, 3 UNKNOWN (hold modes: the state at the end; --hold-until: 0).
import ctypes, os, sys, time, datetime
from ctypes import wintypes

user32 = ctypes.WinDLL('user32', use_last_error=True)
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

LRESULT = ctypes.c_ssize_t
WPARAM = ctypes.c_size_t
LPARAM = ctypes.c_ssize_t
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, ctypes.c_uint, WPARAM, LPARAM)

class GUID(ctypes.Structure):
    _fields_ = [('Data1', ctypes.c_uint32), ('Data2', ctypes.c_uint16), ('Data3', ctypes.c_uint16), ('Data4', ctypes.c_ubyte * 8)]

GUID_CONSOLE_DISPLAY_STATE = GUID(0x6FE69556, 0x704A, 0x47A0, (ctypes.c_ubyte * 8)(0x8F, 0x24, 0xC2, 0x8D, 0x93, 0x6F, 0xDA, 0x47))

class WNDCLASSW(ctypes.Structure):
    _fields_ = [('style', ctypes.c_uint), ('lpfnWndProc', WNDPROC), ('cbClsExtra', ctypes.c_int), ('cbWndExtra', ctypes.c_int),
                ('hInstance', wintypes.HINSTANCE), ('hIcon', wintypes.HICON), ('hCursor', wintypes.HANDLE),
                ('hbrBackground', wintypes.HBRUSH), ('lpszMenuName', wintypes.LPCWSTR), ('lpszClassName', wintypes.LPCWSTR)]

class MSG(ctypes.Structure):
    _fields_ = [('hwnd', wintypes.HWND), ('message', ctypes.c_uint), ('wParam', WPARAM), ('lParam', LPARAM),
                ('time', wintypes.DWORD), ('pt', wintypes.POINT), ('lPrivate', wintypes.DWORD)]

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', wintypes.DWORD)]

user32.DefWindowProcW.argtypes = [wintypes.HWND, ctypes.c_uint, WPARAM, LPARAM]
user32.DefWindowProcW.restype = LRESULT
user32.RegisterClassW.argtypes = [ctypes.POINTER(WNDCLASSW)]
user32.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD, ctypes.c_int, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int, wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID]
user32.CreateWindowExW.restype = wintypes.HWND
user32.RegisterPowerSettingNotification.argtypes = [wintypes.HANDLE, ctypes.POINTER(GUID), wintypes.DWORD]
user32.RegisterPowerSettingNotification.restype = wintypes.HANDLE
user32.PeekMessageW.argtypes = [ctypes.POINTER(MSG), wintypes.HWND, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint]
user32.TranslateMessage.argtypes = [ctypes.POINTER(MSG)]
user32.DispatchMessageW.argtypes = [ctypes.POINTER(MSG)]
user32.DispatchMessageW.restype = LRESULT
user32.GetLastInputInfo.argtypes = [ctypes.POINTER(LASTINPUTINFO)]
kernel32.GetTickCount.restype = wintypes.DWORD
kernel32.SetThreadExecutionState.argtypes = [ctypes.c_uint32]
kernel32.SetThreadExecutionState.restype = ctypes.c_uint32

WM_POWERBROADCAST = 0x0218
PBT_POWERSETTINGCHANGE = 0x8013
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002
ES_CONTINUOUS = 0x80000000
NAMES = {0: 'OFF', 1: 'ON', 2: 'DIMMED'}
CODES = {'ON': 0, 'OFF': 1, 'DIMMED': 2, 'UNKNOWN': 3}

state = {'v': None, 'events': []}

def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def name_of(v):
    return NAMES.get(v, 'UNKNOWN')

def _wndproc(hwnd, msg, wparam, lparam):
    if msg == WM_POWERBROADCAST and wparam == PBT_POWERSETTINGCHANGE and lparam:
        # POWERBROADCAST_SETTING: GUID (16), DWORD DataLength, UCHAR Data[]
        v = ctypes.c_uint32.from_address(lparam + 20).value
        state['v'] = v
        state['events'].append((utc(), v))
        return 1
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

_proc = WNDPROC(_wndproc)

def idle_s():
    li = LASTINPUTINFO()
    li.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if not user32.GetLastInputInfo(ctypes.byref(li)):
        return -1
    return ((kernel32.GetTickCount() - li.dwTime) & 0xFFFFFFFF) // 1000

def make_window():
    hinst = kernel32.GetModuleHandleW(None)
    wc = WNDCLASSW()
    wc.lpfnWndProc = _proc
    wc.hInstance = hinst
    wc.lpszClassName = 'KytyDispState'
    user32.RegisterClassW(ctypes.byref(wc))
    hwnd = user32.CreateWindowExW(0, 'KytyDispState', 'KytyDispState', 0, 0, 0, 0, 0, None, None, hinst, None)
    if not hwnd:
        return None
    if not user32.RegisterPowerSettingNotification(hwnd, ctypes.byref(GUID_CONSOLE_DISPLAY_STATE), 0):
        return None
    return hwnd

def pump(seconds):
    msg = MSG()
    end = time.time() + seconds
    while time.time() < end:
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        time.sleep(0.02)

def hold_until(stop, max_s):
    """The chain mode (item 620 (v)(1)): the request lives in this process from before the lock to after 'lock released'; ends on the
    stop file or after max_s, then ES_CONTINUOUS; events of the display state are printed as they come."""
    hwnd = make_window()
    if hwnd is None:
        print('hold UNKNOWN no window/registration utc %s' % utc())
    else:
        pump(1.0)
        print('hold start dispstate %s idle_s %d utc %s' % (name_of(state['v']), idle_s(), utc()))
    prev = kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_DISPLAY_REQUIRED | ES_SYSTEM_REQUIRED)
    print('hold request set utc %s prev 0x%08x' % (utc(), prev))
    sys.stdout.flush()
    end = time.time() + max_s
    n0 = len(state['events'])
    why = 'max'
    while time.time() < end:
        if os.path.exists(stop):
            why = 'stop file'
            break
        pump(0.5)
        for t, v in state['events'][n0:]:
            print('event %s %s' % (t, name_of(v)))
        n0 = len(state['events'])
        sys.stdout.flush()
    kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    print('hold reset (%s) utc %s; dispstate %s idle_s %d' % (why, utc(), name_of(state['v']), idle_s()))
    return 0


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [('dx', ctypes.c_long), ('dy', ctypes.c_long), ('mouseData', wintypes.DWORD), ('dwFlags', wintypes.DWORD),
                ('time', wintypes.DWORD), ('dwExtraInfo', ctypes.c_size_t)]

class _INPUTU(ctypes.Union):
    _fields_ = [('mi', MOUSEINPUT), ('_pad', ctypes.c_byte * 32)]

class INPUT(ctypes.Structure):
    _fields_ = [('type', wintypes.DWORD), ('u', _INPUTU)]

user32.SendInput.argtypes = [ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = ctypes.c_uint
user32.SendMessageTimeoutW.argtypes = [wintypes.HWND, ctypes.c_uint, WPARAM, LPARAM, ctypes.c_uint, ctypes.c_uint,
                                       ctypes.POINTER(ctypes.c_size_t)]
user32.SendMessageTimeoutW.restype = LRESULT

HWND_BROADCAST = 0xFFFF
WM_SYSCOMMAND = 0x0112
SC_MONITORPOWER = 0xF170
INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001

def nudge_mouse():
    """A relative mouse move +1 then -1 pixel: the cursor ends where it was; wakes the display (user direction 2026-10-07,
    HPP-680: a display OFF is not a reason to stop - wake it)."""
    arr = (INPUT * 2)()
    for i, d in enumerate((1, -1)):
        arr[i].type = INPUT_MOUSE
        arr[i].u.mi = MOUSEINPUT(d, 0, 0, MOUSEEVENTF_MOVE, 0, 0)
    return user32.SendInput(2, arr, ctypes.sizeof(INPUT))

def wake(wait_s=15.0):
    """Wake the display: ES_DISPLAY_REQUIRED, SC_MONITORPOWER on, then a mouse nudge if still not ON; wait for ON up to wait_s.
    Returns the exit code of the final state (0 ON)."""
    hwnd = make_window()
    if hwnd is None:
        print('wake UNKNOWN no window/registration utc %s' % utc())
        return 3
    pump(1.0)
    print('wake start dispstate %s idle_s %d utc %s' % (name_of(state['v']), idle_s(), utc()))
    if state['v'] == 1:
        print('wake not needed utc %s' % utc())
        return 0
    kernel32.SetThreadExecutionState(ES_DISPLAY_REQUIRED | ES_SYSTEM_REQUIRED)
    res = ctypes.c_size_t(0)
    user32.SendMessageTimeoutW(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, -1, 0x0002, 2000, ctypes.byref(res))
    print('wake step SC_MONITORPOWER on utc %s' % utc())
    pump(3.0)
    if state['v'] != 1:
        n = nudge_mouse()
        print('wake step mouse nudge sent %d utc %s' % (n, utc()))
    end = time.time() + wait_s
    while time.time() < end and state['v'] != 1:
        pump(0.5)
    for t, v in state['events']:
        print('event %s %s' % (t, name_of(v)))
    last = name_of(state['v'])
    print('wake end dispstate %s idle_s %d utc %s' % (last, idle_s(), utc()))
    return CODES[last]


def main(argv):
    hold = None
    if argv[:1] == ['--wake']:
        return wake()
    if len(argv) == 4 and argv[0] == '--hold-until' and argv[2] == '--max':
        return hold_until(argv[1], float(argv[3]))
    if len(argv) >= 2 and argv[0] == '--hold':
        hold = float(argv[1])
    hwnd = make_window()
    if hwnd is None:
        print('dispstate UNKNOWN idle_s %d utc %s (no window/registration)' % (idle_s(), utc()))
        return 3
    pump(1.0)  # registration delivers the current state at once
    first = name_of(state['v'])
    print('dispstate %s idle_s %d utc %s' % (first, idle_s(), utc()))
    if hold is None:
        return CODES[first]
    prev = kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_DISPLAY_REQUIRED | ES_SYSTEM_REQUIRED)
    print('hold request set utc %s prev 0x%08x' % (utc(), prev))
    n0 = len(state['events'])
    pump(hold)
    for t, v in state['events'][n0:]:
        print('event %s %s' % (t, name_of(v)))
    last = name_of(state['v'])
    kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    print('hold reset utc %s; dispstate after %s idle_s %d' % (utc(), last, idle_s()))
    return CODES[last]

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

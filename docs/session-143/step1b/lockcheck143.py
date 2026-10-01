"""lockcheck143.py - the dangling-lock rule of step 2 of session 143 (link 1b, HPP-321; ROADMAP s122 item 242 (d)/(RC5)):
only the Harness Engineer runs it, only when a call of go143a.sh did not end by itself (its EXIT trap did not run).

    python lockcheck143.py                      read only: the verdict on C:/kyty/SEALED_RUN.lock
    python lockcheck143.py --remove --tag <T>   remove a DANGLING lock of the tag T, with the two lines below

The lock line of go143a.sh is "go143a.sh <tag> pid <msys pid> winpid <windows pid> started <local time>".  Verdicts:
  NO LOCK (rc 0); HELD (rc 1: the process winpid is alive, or a kyty_emulator.exe lives - not dangling, never removed);
  UNKNOWN OWNER (rc 1: no winpid in the line, or another tag than --tag - never removed);
  DANGLING (rc 2: no process winpid and no kyty_emulator.exe).  With --remove --tag <its tag> a DANGLING lock is removed
  (rc 0) and two lines are written: step2/times.txt "<UTC now> lockcheck143 <T> dangling lock removed by the Harness
  Engineer: noticed <UTC now>, lock mtime <UTC> (source: mtime of the lock file); lock line: <line>" and runs143/lock.log
  "lock released <T> <UTC now> (dangling, removed by lockcheck143)".
Every verdict also prints the sha256 of the installed emulator against the pinned 9235a7ac (a call killed inside the lock
may have left another file there: restore it by hand before any run).  The attempt of such a tag has no json: the summary
prints "ATTEMPT MADE, NO JSON" (item 225 (b)(2)); a repeat of the tag needs a new item of the lead.  ASCII only.
"""
import argparse
import datetime
import hashlib
import os
import re
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
ROOT = 'C:/kyty/s143'
GAME = 'C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe'
BUILD = '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7'
RX = re.compile(r'^go143a\.sh (\S+) pid \S+ winpid (\d+) started ')


def _alive(pid):
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL('kernel32')
    k32.OpenProcess.restype = wintypes.HANDLE
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    h = k32.OpenProcess(0x1000, False, pid)
    if not h:
        return False
    try:
        code = wintypes.DWORD()
        return bool(k32.GetExitCodeProcess(h, ctypes.byref(code))) and code.value == 259
    finally:
        k32.CloseHandle(h)


def _game_alive():
    import ctypes
    from ctypes import wintypes

    class PE(ctypes.Structure):
        _fields_ = [('dwSize', wintypes.DWORD), ('cntUsage', wintypes.DWORD), ('th32ProcessID', wintypes.DWORD),
                    ('th32DefaultHeapID', ctypes.c_size_t), ('th32ModuleID', wintypes.DWORD),
                    ('cntThreads', wintypes.DWORD), ('th32ParentProcessID', wintypes.DWORD),
                    ('pcPriClassBase', ctypes.c_long), ('dwFlags', wintypes.DWORD), ('szExeFile', ctypes.c_wchar * 260)]
    k32 = ctypes.WinDLL('kernel32')
    k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    k32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PE)]
    k32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PE)]
    snap = k32.CreateToolhelp32Snapshot(2, 0)
    found = False
    try:
        pe = PE()
        pe.dwSize = ctypes.sizeof(PE)
        more = k32.Process32FirstW(snap, ctypes.byref(pe))
        while more:
            if pe.szExeFile.lower() == 'kyty_emulator.exe':
                found = True
            more = k32.Process32NextW(snap, ctypes.byref(pe))
    finally:
        k32.CloseHandle(snap)
    return found


def utc(t=None):
    d = datetime.datetime.now(datetime.timezone.utc) if t is None else datetime.datetime.fromtimestamp(
        t, datetime.timezone.utc)
    return d.strftime('%Y-%m-%dT%H:%M:%SZ')


def sha8(path):
    try:
        return hashlib.sha256(open(path, 'rb').read()).hexdigest()
    except OSError:
        return 'missing'


def main(argv=None, lock=LOCK, root=ROOT, game=GAME, alive=None, game_alive=None, now=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--remove', action='store_true')
    ap.add_argument('--tag')
    a = ap.parse_args(argv)
    alive = alive or _alive
    game_alive = game_alive or _game_alive
    inst = sha8(game)
    build = 'installed emulator sha256 %s (%s the pinned 9235a7ac)' % (inst[:16], '=' if inst == BUILD else '!=')
    if a.remove and not a.tag:
        print('usage: --remove needs --tag <the tag of the lock>')
        return 2
    if not os.path.exists(lock):
        print('lockcheck143: NO LOCK; %s' % build)
        return 0
    line = open(lock, encoding='ascii', errors='replace').readline().strip()
    mt = os.path.getmtime(lock)
    m = RX.match(line)
    if m is None or (a.tag is not None and m.group(1) != a.tag):
        print('lockcheck143: UNKNOWN OWNER (lock line: %s; --tag %s) - not removed; %s' % (line, a.tag, build))
        return 1
    tag, pid = m.group(1), int(m.group(2))
    pa, ga = alive(pid), game_alive()
    if pa or ga:
        print('lockcheck143: HELD by %s (winpid %d alive %s, kyty_emulator.exe alive %s) - not dangling, not removed; %s'
              % (tag, pid, 'yes' if pa else 'no', 'yes' if ga else 'no', build))
        return 1
    if not a.remove:
        print('lockcheck143: DANGLING lock of %s (winpid %d not alive, no kyty_emulator.exe; lock mtime %s) - remove only '
              'with --remove --tag %s; %s' % (tag, pid, utc(mt), tag, build))
        return 2
    t_now = now or utc()
    os.remove(lock)
    os.makedirs(os.path.join(root, 'step2'), exist_ok=True)
    os.makedirs(os.path.join(root, 'runs143'), exist_ok=True)
    with open(os.path.join(root, 'step2', 'times.txt'), 'a', encoding='ascii') as f:
        f.write('%s lockcheck143 %s dangling lock removed by the Harness Engineer: noticed %s, lock mtime %s (source: mtime '
                'of the lock file); lock line: %s\n' % (t_now, tag, t_now, utc(mt), line))
    with open(os.path.join(root, 'runs143', 'lock.log'), 'a', encoding='ascii') as f:
        f.write('lock released %s %s (dangling, removed by lockcheck143)\n' % (tag, t_now))
    print('lockcheck143: DANGLING lock of %s REMOVED at %s (lock mtime %s); %s' % (tag, t_now, utc(mt), build))
    return 0


if __name__ == '__main__':
    sys.exit(main())

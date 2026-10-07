"""Track F link FS9c (HPP-673; copy of F24e guard_f24e.py with G moved to f287/fs9c). Track F link F24e (HPP-664; port of F20l3 guard_f20l3.py, G moved; usage names guard_f20l3.py read as guard_f24e.py): guard of the user game (ROADMAP s122 item 534, general rule 33; incident f20_v11).

A process of the user = any kyty_emulator.exe that is not the own emulator of the tag (kind 'emulator'), or any other process whose image
lies in a folder holding a kyty_emulator.exe (kind 'launcher': the user launcher sits beside its emulator).  Names and paths are never
printed: every process is written as <app> pid <n> kind <k>.  The own emulator = the pid of the pid file written by enter_scene.py
(line '<pid> <unix start>') whose creation time is within OWN_SKEW_S of the start written there.

usage:
  python guard_f20l3.py scan [--pidfile F]                        rc 0 'GUARD CLEAN' / rc 7 'GUARD FOUND n: ...'
  python guard_f20l3.py kill-own --pidfile F                      kills the own emulator tree by its pid only (taskkill /F /T /PID)
  python guard_f20l3.py watch --pidfile F --flag F2 --stop F3     poll <= 2 s during the tag; a user process seen in 2 polls in a row =>
                                                                 flag file, the own emulator killed by pid, the user process untouched
  python guard_f20l3.py wait-gone [--pidfile F] [--poll 10]       returns when no user process is left (poll <= 10 s; the lock stays)
  python guard_f20l3.py check|open-block|status|tag <tag>|close <reason> [--block F]    blocks of item 534 (3)
    check      scan + a line CLEAN / FOUND in the block file; FOUND closes the block (rc 7)
    open-block scan; FOUND -> CLOSE, rc 7; CLEAN with an earlier CLEAN >= 600 s ago after the last CLOSE / FOUND -> OPEN, rc 0;
               else PENDING, rc 9 (the first of the two checks)
    status     rc 0 when the block is open and fewer than 6 tags were launched in it, else rc 8
    tag <t>    a TAG line; the 6th tag of the block closes it (CLOSE limit6)
  --fake F (fixtures only): the process list is read from the json file F ([{pid, name, path, start}]) instead of the system.
ASCII only.
"""
import ctypes
import json
import os
import subprocess
import sys
import time

G = 'C:/kyty/f287/fs9c'
BLOCK = G + '/guard_block.txt'
EMU_NAME = 'kyty_emulator.exe'
OWN_SKEW_S = 15.0
GAP_S = 600
BLOCK_TAGS = 6
WATCH_POLL_S = 2.0
GONE_POLL_S = 10.0
FAKE = None


class PE32(ctypes.Structure):
    _fields_ = [('dwSize', ctypes.c_ulong), ('cntUsage', ctypes.c_ulong), ('th32ProcessID', ctypes.c_ulong),
                ('th32DefaultHeapID', ctypes.c_size_t), ('th32ModuleID', ctypes.c_ulong), ('cntThreads', ctypes.c_ulong),
                ('th32ParentProcessID', ctypes.c_ulong), ('pcPriClassBase', ctypes.c_long), ('dwFlags', ctypes.c_ulong),
                ('szExeFile', ctypes.c_wchar * 260)]


def system_procs():
    """[{pid, name, path, start}] of every process; path / start None where the process cannot be opened."""
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.CreateToolhelp32Snapshot.restype = ctypes.c_void_p
    k.OpenProcess.restype = ctypes.c_void_p
    k.CloseHandle.argtypes = [ctypes.c_void_p]
    k.Process32FirstW.argtypes = [ctypes.c_void_p, ctypes.POINTER(PE32)]
    k.Process32NextW.argtypes = [ctypes.c_void_p, ctypes.POINTER(PE32)]
    k.QueryFullProcessImageNameW.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_ulong)]
    k.GetProcessTimes.argtypes = [ctypes.c_void_p] + [ctypes.POINTER(ctypes.c_ulonglong)] * 4
    snap = k.CreateToolhelp32Snapshot(2, 0)
    out = []
    e = PE32()
    e.dwSize = ctypes.sizeof(PE32)
    ok = k.Process32FirstW(snap, ctypes.byref(e))
    while ok:
        pid = int(e.th32ProcessID)
        rec = dict(pid=pid, name=e.szExeFile, path=None, start=None)
        h = k.OpenProcess(0x1000, False, pid)
        if h:
            buf = ctypes.create_unicode_buffer(1024)
            n = ctypes.c_ulong(1024)
            if k.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)):
                rec['path'] = buf.value
            c, x, kt, ut = (ctypes.c_ulonglong() for _ in range(4))
            if k.GetProcessTimes(h, ctypes.byref(c), ctypes.byref(x), ctypes.byref(kt), ctypes.byref(ut)):
                rec['start'] = c.value / 1e7 - 11644473600.0
            k.CloseHandle(h)
        out.append(rec)
        ok = k.Process32NextW(snap, ctypes.byref(e))
    k.CloseHandle(snap)
    return out


def procs():
    if FAKE:
        return json.load(open(FAKE))
    return system_procs()


def read_own(pidfile):
    try:
        a = open(pidfile).read().split()
        return int(a[0]), float(a[1])
    except Exception:  # noqa: BLE001
        return None


def is_own(p, own):
    return (own is not None and p['pid'] == own[0] and (p['name'] or '').lower() == EMU_NAME and p.get('start') is not None
            and abs(p['start'] - own[1]) <= OWN_SKEW_S)


def user_procs(plist, own):
    """The user processes of the list: (pid, kind).  The own emulator and this process are not counted."""
    found = []
    me = os.getpid()
    for p in plist:
        if p['pid'] in (0, 4, me) or is_own(p, own):
            continue
        name = (p['name'] or '').lower()
        if name == EMU_NAME:
            found.append((p['pid'], 'emulator'))
            continue
        path = p.get('path')
        if path and os.path.isfile(os.path.join(os.path.dirname(path), EMU_NAME)):
            found.append((p['pid'], 'launcher'))
    return found


def fmt(found):
    if not found:
        return 'GUARD CLEAN'
    return 'GUARD FOUND %d: %s' % (len(found), ', '.join('<app> pid %d kind %s' % f for f in found))


def scan(pidfile=None):
    own = read_own(pidfile) if pidfile else None
    return user_procs(procs(), own)


def kill_own(pidfile):
    own = read_own(pidfile)
    if own is None:
        return 'own emulator: no pid file'
    alive = [p for p in procs() if is_own(p, own)]
    if not alive:
        return 'own emulator pid %d not alive' % own[0]
    r = subprocess.run(['taskkill', '/F', '/T', '/PID', str(own[0])], capture_output=True, creationflags=0x08000000)
    return 'own emulator pid %d killed by pid (taskkill /F /T /PID rc %d)' % (own[0], r.returncode)


def utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def watch(pidfile, flag, stop):
    seen = 0
    done = False
    while not os.path.exists(stop):
        found = scan(pidfile)
        seen = seen + 1 if found else 0
        if seen >= 2 and not done:
            with open(flag, 'w') as f:
                f.write('%s %s\n' % (utc(), fmt(found)))
            print('%s %s' % (utc(), fmt(found)), flush=True)
            done = True
        if done and read_own(pidfile) is not None:
            msg = kill_own(pidfile)
            if 'killed' in msg:
                print('%s %s' % (utc(), msg), flush=True)
        time.sleep(WATCH_POLL_S)
    print('%s watch end, user process seen: %s' % (utc(), 'yes' if done else 'no'), flush=True)
    return 0


def wait_gone(pidfile, poll):
    t0 = time.time()
    while True:
        found = scan(pidfile)
        if not found:
            print('%s GUARD CLEAN after %.0f s' % (utc(), time.time() - t0), flush=True)
            return 0
        time.sleep(poll)


def block_lines(path):
    if not os.path.exists(path):
        return []
    out = []
    for l in open(path):
        a = l.split()
        if len(a) >= 3:
            out.append((float(a[1]), a[2], a[3:]))
    return out


def block_add(path, what, now=None):
    now = time.time() if now is None else now
    with open(path, 'a') as f:
        f.write('%s %.0f %s\n' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)), now, what))


def block_state(lines):
    """('open', tags in the block) or ('closed', 0)."""
    state, tags = 'closed', 0
    for _, kind, _rest in lines:
        if kind == 'OPEN':
            state, tags = 'open', 0
        elif kind in ('CLOSE', 'FOUND'):
            state, tags = 'closed', 0
        elif kind == 'TAG' and state == 'open':
            tags += 1
    if state == 'open' and tags >= BLOCK_TAGS:
        state = 'closed'
    return state, tags


def open_block(path, found, now):
    if found:
        block_add(path, 'FOUND %d' % len(found), now)
        block_add(path, 'CLOSE found', now)
        return 7, 'FOUND'
    lines = block_lines(path)
    last_cut = max([t for t, k, _ in lines if k in ('CLOSE', 'FOUND', 'OPEN')] or [0.0])
    early = [t for t, k, _ in lines if k == 'CLEAN' and t > last_cut and now - t >= GAP_S]
    block_add(path, 'CLEAN', now)
    if block_state(lines)[0] == 'open':
        return 0, 'OPEN (already)'
    if early:
        block_add(path, 'OPEN', now)
        return 0, 'OPEN'
    return 9, 'PENDING'


def main(argv):
    global FAKE
    if '--fake' in argv:
        FAKE = argv[argv.index('--fake') + 1]
    opt = lambda k, d=None: argv[argv.index(k) + 1] if k in argv else d  # noqa: E731
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0]
    path = opt('--block', BLOCK)
    if cmd == 'scan':
        found = scan(opt('--pidfile'))
        print(fmt(found))
        return 7 if found else 0
    if cmd == 'kill-own':
        print(kill_own(opt('--pidfile')))
        return 0
    if cmd == 'watch':
        return watch(opt('--pidfile'), opt('--flag'), opt('--stop'))
    if cmd == 'wait-gone':
        return wait_gone(opt('--pidfile'), min(float(opt('--poll', GONE_POLL_S)), GONE_POLL_S))
    if cmd == 'check':
        found = scan()
        if found:
            block_add(path, 'FOUND %d' % len(found))
            block_add(path, 'CLOSE found')
        else:
            block_add(path, 'CLEAN')
        print(fmt(found))
        return 7 if found else 0
    if cmd == 'open-block':
        found = scan()
        rc, word = open_block(path, found, time.time())
        print('%s; block %s' % (fmt(found), word))
        return rc
    if cmd == 'status':
        state, tags = block_state(block_lines(path))
        print('block %s, tags %d of %d' % (state, tags, BLOCK_TAGS))
        return 0 if state == 'open' else 8
    if cmd == 'tag':
        state, tags = block_state(block_lines(path))
        if state != 'open':
            print('block closed - tag not recorded')
            return 8
        block_add(path, 'TAG %s' % argv[1])
        if tags + 1 >= BLOCK_TAGS:
            block_add(path, 'CLOSE limit6')
        print('tag %s recorded, %d of %d in the block' % (argv[1], tags + 1, BLOCK_TAGS))
        return 0
    if cmd == 'close':
        block_add(path, 'CLOSE %s' % (argv[1] if len(argv) > 1 else 'manual'))
        print('block closed')
        return 0
    print('unknown command')
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

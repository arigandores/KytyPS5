"""F10e (HPP-453, ROADMAP s122 item 369 (c)(3)) - the FS3c file run_fs3.py with ONE change: the flag --sval puts
'--shader-validation true' in place of 'false' in the fixed emulator arguments (item 369 (c)(3): R0/R1/W only with --shader-validation true;
F10d section 5: with false KYTY_FIX_SVAL changes nothing).  Everything else as run_fs3.py (FS3c) = run_f9g.py (F9g):
one launch of the emulator binary that sits in the emulator folder (go_f10e.sh installed the F10c copy there) by its ABSOLUTE path;
--val: '--vulkan-validation true'; --until-release <present> <after_s> (not used by F10e).
usage: python run_f10e.py <out_dir> <seconds> [--val] [--sval] [--until-release <present> <after_s>] [KEY=VALUE ...]
The environment is cleaned of every KYTY_* and VK_LAYER_* and then given KEY=VALUE (positional). The window is closed by
WM_CLOSE (the video and its index are finished), killed 40 s later. Writes <out_dir>/stdout.txt, log.txt (copy of _kyty.txt),
run.json (how: 'exit rc <n>' if the process ended before <seconds>, else 'timeout, WM_CLOSE rc <n>'; exit_s - wall seconds of the
exit seen). ASCII output only."""
import ctypes, json, os, re, shutil, subprocess, sys, time
EMU = 'C:/kyty/KytyPS5/ps5 em'
RX_REL = re.compile(rb'InputScript: release \S+ at [0-9.]+ s \(present (\d+)\)')


def parse(argv):
    out, secs = argv[0], float(argv[1])
    rest = argv[2:]
    val = False
    sval = False
    until = None
    pairs = []
    i = 0
    while i < len(rest):
        a = rest[i]
        if a == '--val':
            val = True
        elif a == '--sval':
            sval = True
        elif a == '--until-release':
            until = (int(rest[i + 1]), float(rest[i + 2]))
            i += 2
        else:
            if '=' not in a:
                raise SystemExit('bad argument %r' % a)
            pairs.append(a)
        i += 1
    return out, secs, val, sval, until, pairs


def emu_args(val, sval):
    return [EMU + '/kyty_emulator.exe', '--screen-width', '1280', '--screen-height', '720', '--user-name', 'Player',
            '--user-id', '1000', '--present-mode', 'Fifo', '--vblank-frequency', '60', '--console-language', '1',
            '--vulkan-validation', 'true' if val else 'false', '--shader-validation', 'true' if sval else 'false', '--shader-optimization-type',
            'Size', '--shader-log-direction', 'File', '--shader-log-folder', '_Shaders', '--command-buffer-dump', 'false',
            '--command-buffer-dump-folder', '_Buffers', '--printf-direction', 'File', '--printf-output-file', '_kyty.txt',
            '--spirv-debug-printf', 'false', '--game', EMU + '/games/PPSA21564-app']


class Tail:
    """Incremental reader of the growing _kyty.txt: finds the release line of the given present."""

    def __init__(self, path, present):
        self.path, self.present, self.pos, self.rest = path, present, 0, b''

    def poll(self):
        try:
            with open(self.path, 'rb') as f:
                f.seek(self.pos)
                data = f.read(64 << 20)
        except OSError:
            return False
        if not data:
            return False
        self.pos += len(data)
        buf = self.rest + data
        cut = buf.rfind(b'\n')
        if cut < 0:
            self.rest = buf
            return False
        self.rest = buf[cut + 1:]
        for m in RX_REL.finditer(buf[:cut]):
            if int(m.group(1)) == self.present:
                return True
        return False


def main():
    out, secs, val, sval, until, pairs = parse(sys.argv[1:])
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_') and not k.startswith('VK_LAYER_')}
    for a in pairs:
        k, v = a.split('=', 1)
        env[k] = v
    args = emu_args(val, sval)
    os.makedirs(out, exist_ok=True)
    for req in ('_input.req', '_screenshot.req'):
        if os.path.exists(os.path.join(EMU, req)):
            os.remove(os.path.join(EMU, req))
    t0 = time.time()
    so = open(os.path.join(out, 'stdout.txt'), 'wb')
    game = subprocess.Popen(args, cwd=EMU, env=env, stdout=so, stderr=subprocess.STDOUT)
    print('started pid %d env %s val %d sval %d secs %.0f until %s' % (game.pid, ' '.join(pairs), val, sval, secs, until), flush=True)
    how = 'timeout'
    tail = Tail(os.path.join(EMU, '_kyty.txt'), until[0]) if until else None
    seen = None
    exit_s = None
    while time.time() - t0 < secs:
        if game.poll() is not None:
            how = 'exit rc %s' % game.returncode
            exit_s = round(time.time() - t0, 1)
            break
        if tail and seen is None and tail.poll():
            seen = time.time() - t0
            print('release of present %d seen at %.1f s wall' % (until[0], seen), flush=True)
        if seen is not None and time.time() - t0 >= seen + until[1]:
            how = 'release+%.0f s' % until[1]
            break
        time.sleep(1)

    def kill():
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(game.pid)], capture_output=True)
        try:
            game.wait(timeout=20)
        except subprocess.TimeoutExpired:
            game.kill()
    if game.poll() is None:
        user = ctypes.WinDLL('user32')
        cb = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        user.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
        user.PostMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]

        @cb
        def visit(hwnd, _):
            owner = ctypes.c_ulong()
            user.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
            if owner.value == game.pid:
                user.PostMessageW(hwnd, 0x10, 0, 0)
            return True
        user.EnumWindows(visit, None)
        try:
            game.wait(timeout=40)
            how += ', WM_CLOSE rc %s' % game.returncode
        except subprocess.TimeoutExpired:
            kill()
            how += ', killed 40 s after WM_CLOSE'
    so.close()
    wall = time.time() - t0
    shutil.copyfile(os.path.join(EMU, '_kyty.txt'), os.path.join(out, 'log.txt'))
    json.dump({'pid': game.pid, 'how': how, 'wall_s': round(wall, 1), 'release_seen_s': seen, 'env': pairs, 'val': val, 'sval': sval, 'exit_s': exit_s, 'rc': game.returncode,
               'until': until, 'args': args}, open(os.path.join(out, 'run.json'), 'w'), indent=1)
    print('ended: %s wall %.1f s' % (how, wall), flush=True)


if __name__ == '__main__':
    main()

"""F9a (HPP-410, ROADMAP s122 item 344 (v)(2)-(3)): one launch of the installed emulator for the water repro.
usage: python run_f9.py <out_dir> <seconds> [--rd] [KEY=VALUE ...]
Starts kyty_emulator.exe in the emulator folder with the flags of play_patched.sh (no validation), the environment cleaned
of every KYTY_* and VK_LAYER_* and then given KEY=VALUE (positional), waits <seconds> or the exit, closes the window by
WM_CLOSE (the video and its index are finished), kills after 40 s. Writes <out_dir>/stdout.txt, log.txt (copy of _kyty.txt),
run.json. ASCII output only."""
import ctypes, json, os, shutil, subprocess, sys, time
EMU = 'C:/kyty/KytyPS5/ps5 em'
out, secs = sys.argv[1], float(sys.argv[2])
rest = sys.argv[3:]
rd = '--rd' in rest
pairs = [a for a in rest if a != '--rd']
env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_') and not k.startswith('VK_LAYER_')}
for a in pairs:
    k, v = a.split('=', 1)
    env[k] = v
args = ['./kyty_emulator.exe', '--screen-width', '1280', '--screen-height', '720', '--user-name', 'Player', '--user-id', '1000',
        '--present-mode', 'Fifo', '--vblank-frequency', '60', '--console-language', '1', '--vulkan-validation', 'false',
        '--shader-validation', 'false', '--shader-optimization-type', 'Size', '--shader-log-direction', 'File',
        '--shader-log-folder', '_Shaders', '--command-buffer-dump', 'false', '--command-buffer-dump-folder', '_Buffers',
        '--printf-direction', 'File', '--printf-output-file', '_kyty.txt', '--spirv-debug-printf', 'false']
if rd:
    args += ['--rd']
args += ['--game', EMU + '/games/PPSA21564-app']
os.makedirs(out, exist_ok=True)
for req in ('_input.req', '_screenshot.req'):
    if os.path.exists(os.path.join(EMU, req)):
        os.remove(os.path.join(EMU, req))
t0 = time.time()
so = open(os.path.join(out, 'stdout.txt'), 'wb')
game = subprocess.Popen(args, cwd=EMU, env=env, stdout=so, stderr=subprocess.STDOUT)
print('started pid %d env %s rd %d secs %.0f' % (game.pid, ' '.join(pairs), rd, secs), flush=True)
how = 'timeout'
while time.time() - t0 < secs:
    if game.poll() is not None:
        how = 'exit rc %s' % game.returncode
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
json.dump({'pid': game.pid, 'how': how, 'wall_s': round(wall, 1), 'env': pairs, 'rd': rd, 'args': args}, open(os.path.join(out, 'run.json'), 'w'), indent=1)
print('ended: %s wall %.1f s' % (how, wall), flush=True)

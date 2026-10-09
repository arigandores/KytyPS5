# Track F link F31c (HPP-731; ROADMAP s122 item 667 (d)): copy of the F26c (HPP-692) file hold_f26c.py with the names moved (f26c -> f31c, HPP-692 -> HPP-731, F26C_ -> F31C_); no change of meaning.
"""Track F link F26c (HPP-731; copy of FS10c hold_f31c.py, names moved).  Before: Track F link F25m (HPP-686; ROADMAP s122 item 606 (v)(1), general rule 33(2)): the user session through the driver GLCache - a live
process of the user that is a virtual machine (image name starting 'qemu-system', or 'emulator.exe') or that holds a file of the GLCache
folder open.  The own emulator of the tag (pid file) is not the user.  Names are never printed: '<app> pid <n> kind vm|holder'.  ASCII only.

  python hold_f31c.py check [--pidfile F] [--quick]   rc 0 'HOLD CLEAR' / rc 9 'HOLD USER SESSION n: ...'  (--quick: names only, no open
                                                       files - for the poll during a tag)
  python hold_f31c.py watch --pidfile F --flag F2 --stop F3     poll <= 2 s (names only) during the tag; a VM seen in 2 polls in a row =>
                                                       flag file, the own emulator killed by its pid (guard_f31c.py kill-own)
  python hold_f31c.py wait-gone [--pidfile F] [--poll 10]       returns when the full check is clear (the lock stays)
  --fake F (fixtures only): the process list from a json file ([{pid, name, files: [path, ...]}]).
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GL = os.path.join(os.environ.get('USERPROFILE', 'C:/Users/x'), 'AppData/Local/NVIDIA/GLCache').replace('\\', '/').lower()
VM_PREFIX = ('qemu-system',)
VM_NAMES = ('emulator.exe',)
POLL_S = 2.0


def own_pid(pidfile):
    try:
        return int(open(pidfile, encoding='ascii').read().split()[0])
    except (OSError, ValueError, IndexError, TypeError):
        return None


def procs(fake, quick):
    if fake:
        return json.load(open(fake, encoding='ascii'))
    import psutil
    out = []
    for p in psutil.process_iter(['pid', 'name']):
        nm = (p.info['name'] or '').lower()
        files = []
        if not quick:
            try:
                files = [f.path for f in p.open_files()]
            except Exception:  # noqa: BLE001
                files = []
        out.append(dict(pid=p.info['pid'], name=nm, files=files))
    return out


def is_vm(name):
    n = (name or '').lower()
    return n.startswith(VM_PREFIX) or n in VM_NAMES


def found(pidfile, fake, quick):
    own = own_pid(pidfile) if pidfile else None
    res = []
    for p in procs(fake, quick):
        if own is not None and p['pid'] == own:
            continue
        if is_vm(p.get('name')):
            res.append('<app> pid %d kind vm' % p['pid'])
            continue
        if any(f.replace('\\', '/').lower().startswith(GL + '/') for f in p.get('files') or []):
            res.append('<app> pid %d kind holder' % p['pid'])
    return res


def main(argv):
    def a(k, d=None):
        return argv[argv.index(k) + 1] if k in argv else d
    pidf, fake = a('--pidfile'), a('--fake')
    cmd = argv[0] if argv else ''
    if cmd == 'check':
        f = found(pidf, fake, '--quick' in argv)
        print(('HOLD USER SESSION %d: %s' % (len(f), '; '.join(f))) if f else 'HOLD CLEAR')
        return 9 if f else 0
    if cmd == 'watch':
        flag, stop = a('--flag'), a('--stop')
        seen = 0
        while not (stop and os.path.exists(stop)):
            f = found(pidf, fake, True)
            seen = seen + 1 if f else 0
            if seen >= 2:
                with open(flag, 'w', encoding='ascii') as fo:
                    fo.write('%s VM %s\n' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), '; '.join(f)))
                if pidf:
                    subprocess.run([sys.executable, os.path.join(HERE, 'guard_f31c.py'), 'kill-own', '--pidfile', pidf], capture_output=True)
                print('%s watch: user VM seen - flag written, own emulator killed by pid' % time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
                return 9
            if fake:
                break
            time.sleep(POLL_S)
        print('%s watch end, user VM seen: no' % time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
        return 0
    if cmd == 'wait-gone':
        poll = float(a('--poll', 10))
        t0 = time.time()
        while True:
            f = found(pidf, fake, False)
            if not f:
                print('%s HOLD CLEAR after %d s' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), time.time() - t0))
                return 0
            if fake:
                print('HOLD USER SESSION (fake, no wait)')
                return 9
            time.sleep(poll)
    print(__doc__.split('\n')[4].strip())
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

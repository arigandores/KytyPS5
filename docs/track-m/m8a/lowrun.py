"""M8a (HPP-858): copy of m657/m6a/lowrun.py. Was: M6a (HPP-848): copy of m657/m2d/lowrun.py. Was: M2d (HPP-841, ROADMAP s122 item 760(b)(4)): copy of m657/m2c/lowrun.py - run a command at IDLE priority (the children
inherit it). Lock and STOP are checked first. Usage: python lowrun.py <command> [args...]; exit code = the command's."""
import ctypes
import os
import subprocess
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/m657/STOP'):
    print('LOCK or STOP')
    sys.exit(3)
IDLE_PRIORITY_CLASS = 0x40
kernel32 = ctypes.windll.kernel32
kernel32.SetPriorityClass(kernel32.GetCurrentProcess(), IDLE_PRIORITY_CLASS)
sys.exit(subprocess.call(sys.argv[1:], creationflags=IDLE_PRIORITY_CLASS))

# F20c (HPP-561): the <app> mask in enter_scene.py (debt of item 463 (2) / process rule of item 324 (i)): every host process
# name and every GPU process name that is not the emulator is written as '<app>' - in the printed pre_run line and in the
# tag json (top, top_names, gpu_apps).  LF kept.
import sys
p = sys.argv[1]
s = open(p, 'rb').read().decode('utf-8')
assert '\r' not in s
old1 = """    rows = [dict(name=row.get('Name'), pid=row.get('Id'),"""
new1 = """    rows = [dict(name=mask_name(row.get('Name')), pid=row.get('Id'),"""
assert s.count(old1) == 1
s = s.replace(old1, new1)
old2 = "def sample_host():\n"
new2 = ("OWN_NAMES = ('kyty_emulator', 'kyty_emulator.exe')\n\n\n"
        "def mask_name(name):\n"
        "    \"\"\"F20c (HPP-561, item 463 (2)): a host or GPU process name other than the emulator is printed and stored as '<app>'.\"\"\"\n"
        "    n = (name or '').strip()\n"
        "    base = n.replace('/', chr(92)).split(chr(92))[-1].lower()\n"
        "    return n if base in OWN_NAMES else '<app>'\n\n\n"
        "def sample_host():\n")
assert s.count(old2) == 1
s = s.replace(old2, new2)
old3 = "    section = idle142.sample_gpu(log=lambda s: print(s, flush=True))\n"
new3 = ("    section = idle142.sample_gpu(log=lambda s: print(s, flush=True))\n"
        "    for app in section.get('gpu_apps') or []:\n"
        "        app['name'] = mask_name(app.get('name'))\n")
assert s.count(old3) == 1
s = s.replace(old3, new3)
open(p, 'wb').write(s.encode('utf-8'))
print('patched', p)

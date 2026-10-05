# Track F link F16q (HPP-597): the F16m suite with the expected root moved to f287/f16q - nothing else changed.
# Track F link F16f (HPP-523): the FS6c suite with the expected root moved to f287/f16m - nothing else changed.
# Track F link FS6c (HPP-557): fixtures of the <app> mask of the host census of enter_scene.py (ROADMAP item 463(d)(2)).
# Every fixture feeds process names that must not appear in the output; the suite ends with ALL OK.
import hashlib
import io
import json
import pathlib
import sys
import contextlib

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / 'enter_scene.py'
sys.path.insert(0, str(HERE))


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


print('suite test_enter_scene_mask.py sha256 %s target enter_scene.py sha256 %s'
      % (sha(__file__), sha(TARGET)))

import enter_scene as es  # noqa: E402

NAMES = ['SomeForeignApp', 'kyty_emulator', 'chrome', 'Game Launcher X', 'svchost',
         'a' * 80, 'name:with:colons', 'MiXeDcAsE']
fails = 0


def check(name, ok, info=''):
    global fails
    print('%s %s %s' % ('PASS' if ok else 'FAIL', name, info))
    if not ok:
        fails += 1


top = [dict(Name=n, Id=1000 + i, CPU=123.4 - i, WS=50 * 1048576) for i, n in enumerate(NAMES)]
rows = es.mask_host_rows(top)
line = es.host_census_line(321, rows)
blob = json.dumps(dict(top=rows, line=line))
low = blob.lower()

# m1: no input name, in any case, in the line or the json of the rows
check('m1_no_name_in_output', all(n.lower() not in low for n in NAMES))
# m2: every row is masked and keeps pid/cpu/ws
check('m2_rows_masked', all(r['name'] == '<app>' for r in rows) and [r['pid'] for r in rows] == [1000 + i for i in range(len(NAMES))])
check('m3_cpu_ws_kept', rows[0]['cpu_s'] == 123.4 and rows[0]['ws_mib'] == 50.0)
# m4: the line keeps its prefix (readers match 'pre_run: host') and shows six rows
check('m4_line_prefix', line.startswith('pre_run: host 321 processes, top by CPU: '), line)
check('m5_six_rows', line.count('<app>:') == 6, line)
check('m6_line_ascii', all(ord(c) < 128 for c in line))
# m7: empty census and None fields do not fail
check('m7_empty', es.host_census_line(None, es.mask_host_rows([])) == 'pre_run: host None processes, top by CPU: ')
r0 = es.mask_host_rows([dict(Name=None, Id=None, CPU=None, WS=None)])
check('m8_none_fields', r0 == [dict(name='<app>', pid=None, cpu_s=0.0, ws_mib=0.0)])
# m9: the census function itself, with powershell stubbed, prints and returns only masked names
class Done:
    def __init__(self, out):
        self.stdout = out
calls = []
def fake_run(cmd, **kw):
    calls.append(cmd)
    return Done(json.dumps(top)) if len(calls) == 1 else Done('321')
real = es.subprocess.run
es.subprocess.run = fake_run
buf = io.StringIO()
try:
    with contextlib.redirect_stdout(buf):
        sec = es.sample_host()
finally:
    es.subprocess.run = real
out = buf.getvalue() + json.dumps(sec)
check('m9_census_masked', all(n.lower() not in out.lower() for n in NAMES) and sec.get('names_masked') is True and 'top_names' not in sec, buf.getvalue().strip())
# m10: strict cp1250 output of the line
try:
    line.encode('cp1250', 'strict')
    check('m10_cp1250', True)
except UnicodeEncodeError as e:
    check('m10_cp1250', False, str(e))
# m12: sample_machine masks gpu_apps paths (idle142.sample_gpu stubbed) and the run.txt lines carry no name
gpu = dict(gpu_util_median=3.0, gpu_power_median=30.0, gpu_memory_used_mib=900, gpu_sm_mhz_median=210,
           gpu_util_samples=[3.0], gpu_apps=[dict(pid=7, name='C:\\Program Files\\Vendor\\' + n + '.exe') for n in NAMES])
real_gpu, real_host = es.idle142.sample_gpu, es.sample_host
es.idle142.sample_gpu = lambda log=None: json.loads(json.dumps(gpu))
es.sample_host = lambda: dict(available=True, top=rows, names_masked=True)
buf = io.StringIO()
try:
    with contextlib.redirect_stdout(buf):
        sec = es.sample_machine()
finally:
    es.idle142.sample_gpu, es.sample_host = real_gpu, real_host
out = (buf.getvalue() + json.dumps(sec)).lower()
check('m12_gpu_apps_masked', all(n.lower() not in out for n in NAMES) and 'vendor' not in out
      and [a['name'] for a in sec['gpu_apps']] == ['<app>'] * len(NAMES) and sec.get('gpu_apps_masked') is True
      and sec['gpu_util_median'] == 3.0, buf.getvalue().strip().splitlines()[0] if buf.getvalue() else '')
check('m13_unavailable_kept', es.mask_gpu_apps(dict(available=False)) == dict(available=False))
# m11: the root is the FS6c folder
check('m11_root', str(es.ROOT).replace('\\', '/') == 'C:/kyty/f287/f16q', str(es.ROOT))

print('ALL OK' if fails == 0 else 'FAILED %d' % fails)
sys.exit(0 if fails == 0 else 1)

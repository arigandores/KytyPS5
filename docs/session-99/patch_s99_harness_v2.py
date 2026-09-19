"""Repair VERIFY counterexamples: shared complete markers, both saved output streams."""
from pathlib import Path
p = Path('C:/kyty/s99/enter_scene.py')
raw = p.read_bytes()
s = raw.decode('utf8').replace('\r\n','\n')
assert s.count('import time\n') == 1
s = s.replace('import time\n','import time\nfrom run_safety99 import failure_marker\n')
s = s.replace("result.get('hold_s', 0) < options.hold", "(result.get('hold_s') or 0) < options.hold")
start = s.index("                warmup_log = ROOT / ('log_%s_warmup.txt' % tag)")
end = s.index('                continue\n', start)
s = s[:start] + """                warmup_paths = [ROOT / ('%s_%s_warmup.txt' % (stream, tag))
                                for stream in ('log', 'stdout')]
                if not all(path.is_file() for path in warmup_paths):
                    print('STOP: warmup output absent; counted process will not launch', flush=True)
                    break
                warmup_failed = False
                for warmup_path in warmup_paths:
                    with warmup_path.open('rb') as warmup_stream:
                        if any(failure_marker(line) for line in warmup_stream):
                            warmup_failed = True
                            break
                if warmup_failed:
                    print('STOP: warmup failure marker; counted process will not launch', flush=True)
                    break
""" + s[end:]
data=s.encode('utf8')
if b'\r\n' in raw:
    data=data.replace(b'\n',b'\r\n')
p.write_bytes(data)
print('PASS: launcher and scorer share failure_marker; log and stdout both required/scanned')

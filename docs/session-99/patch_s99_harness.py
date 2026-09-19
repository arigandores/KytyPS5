"""Session 99 sealed stopping rule: never continue after a failed warmup."""
from pathlib import Path

p = Path('C:/kyty/s99/enter_scene.py')
raw = p.read_bytes()
s = raw.decode('utf8').replace('\r\n', '\n')
old = """                print('warmup finished (%s), not counted' % result['outcome'], flush=True)
                continue
"""
new = """                print('warmup finished (%s), not counted' % result['outcome'], flush=True)
                # Session 99: a failed warmup is a result, not permission for another process.
                if (result['outcome'] != 'ok' or result.get('hold_exit') is not None
                        or result.get('hold_s', 0) < options.hold):
                    print('STOP: warmup failed; counted process will not launch', flush=True)
                    break
                warmup_log = ROOT / ('log_%s_warmup.txt' % tag)
                if not warmup_log.is_file():
                    print('STOP: warmup log absent; counted process will not launch', flush=True)
                    break
                failure_tokens = (b'GpuHangAbort', b'GpuWaitSlow', b'ErrorDeviceLost',
                                  b'--- std::terminate ---', b'--- abort() ---', b'Fatal Error')
                with warmup_log.open('rb') as warmup_stream:
                    warmup_failed = any(any(t in line for t in failure_tokens)
                                        for line in warmup_stream)
                if warmup_failed:
                    print('STOP: warmup failure marker; counted process will not launch', flush=True)
                    break
                continue
"""
assert s.count(old) == 1
s = s.replace(old, new)
data = s.encode('utf8')
if b'\r\n' in raw:
    data = data.replace(b'\n', b'\r\n')
p.write_bytes(data)
print('PASS: failed/dead/short/missing-log/fatal-marker warmup stops before counted process')

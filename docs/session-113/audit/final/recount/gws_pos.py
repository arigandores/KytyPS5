# Locate the GpuWaitSlow line relative to the surrounding FrameTrace main rows.
import sys, re
last = None; after = None; found = False
with open(sys.argv[1], 'rb') as f:
    for line in f:
        if line.startswith(b'FrameTrace: '):
            m = re.match(rb'FrameTrace: n=(\d+) dt_us=(\d+)', line)
            if found:
                after = (int(m.group(1)), int(m.group(2))); break
            last = (int(m.group(1)), int(m.group(2)))
        elif b'GpuWaitSlow' in line:
            found = True
print('main row before', last, 'main row after', after)

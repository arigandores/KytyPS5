import time, os, sys, statistics
src = sys.argv[1]; out = sys.argv[2]
t = open(src, 'rb').read()
lines = t.split(b'\n')
wl = [l for l in lines if l.startswith(b'DiagB32-w: ')]
avg = sum(len(l) + 1 for l in wl) / max(1, len(wl))
big = t + b''.join(wl[i % len(wl)] + b'\n' for i in range(65536 - len(wl)))
print('src bytes %d w_lines %d avg_w_line %.1f B; big bytes %d (w_lines 65536)' % (len(t), len(wl), avg, len(big)))
for name, data in (('3.3MB', t), ('65536w', big)):
    ms = []
    f = open(out, 'ab')
    for k in range(10):
        t0 = time.perf_counter_ns()
        buf = bytearray(data)      # spdlog: payload copied into the formatter memory_buf
        f.write(buf)               # basic_file_sink: fwrite of the whole buffer
        t1 = time.perf_counter_ns()
        ms.append((t1 - t0) / 1e6)
    f.close()
    print('%s bytes %d median_ms %.2f worst_ms %.2f all %s' % (name, len(data), statistics.median(ms), max(ms), ' '.join('%.1f' % x for x in ms)))
os.remove(out)

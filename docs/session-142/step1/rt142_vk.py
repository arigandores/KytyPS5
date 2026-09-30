# Red Team s142 step 1: the validation-layer evidence lines of s6s137 (log) - text of each, first 30 MB only (instance
# creation is at the start of the log).
M = (b'VK_LAYER_KHRONOS_validation available extension:', b'no validation layer:', b'Vulkan required extension:')
with open('C:/kyty/s137/log_s6s137.txt', 'rb') as f:
    buf = f.read(30 * 1048576)
for line in buf.split(b'\n'):
    if any(m in line for m in M):
        print(line.strip()[:160].decode('latin1'))

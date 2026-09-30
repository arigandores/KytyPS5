# vk_w135.py - Session Auditor s.135: classes of [Vulkan][W] lines (message id + text up to the first digit run) in two logs; V5 cross-reference s3s135 vs s3s133.
import re, sys, json
def classes(p):
    c = {}
    with open(p, 'rb') as f:
        for ln in f:
            if b'[Vulkan][W]' in ln:
                q = ln[ln.find(b'[Vulkan][W]'):].strip()
                m = re.search(rb'MessageID = (0x[0-9a-fA-F]+)', q)
                key = m.group(1).decode() if m else re.sub(rb'0x[0-9a-fA-F]+|\d+', b'#', q[:90]).decode('utf-8', 'replace')
                c[key] = c.get(key, 0) + 1
    return c
a = classes('C:/kyty/s135/log_s3s135.txt'); b = classes('C:/kyty/s133/log_s3s133.txt')
print('s3s135 classes', len(a), 'lines', sum(a.values())); print('s3s133 classes', len(b), 'lines', sum(b.values()))
print('in s3s135 not in s3s133:', [k for k in a if k not in b])
print('in s3s133 not in s3s135:', [k for k in b if k not in a])

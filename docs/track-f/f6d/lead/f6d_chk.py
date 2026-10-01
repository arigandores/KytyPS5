import glob, os, hashlib
logs = ['C:/kyty/s142/log_c142_03.txt', 'C:/kyty/s144/log_v144_13.txt', 'C:/kyty/s143/log_v143_03.txt', 'C:/kyty/s144/log_w144_13.txt', 'C:/kyty/s144/log_w144_03.txt']
for p in logs:
    if not os.path.exists(p):
        print(p, 'MISSING'); continue
    a = u = 0
    with open(p, 'rb') as f:
        for line in f:
            if b'ASSERT:' in line: a += 1
            if b'user_msg_param' in line: u += 1
    print(p, os.path.getsize(p), 'ASSERT:', a, 'user_msg_param', u)
for p in sorted(glob.glob('C:/kyty/s14[234]/*stdout*'))[:20]:
    d = open(p, 'rb').read()
    print(p, 'ASSERT:', d.count(b'ASSERT:'), 'user_msg_param', d.count(b'user_msg_param'))

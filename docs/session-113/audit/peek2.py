import re,sys
p=sys.argv[1]; want=int(sys.argv[2]); pat=re.compile(sys.argv[3].encode())
with open(p,'rb') as f:
    for line in f:
        m=re.match(rb'^(FrameTrace[-\w]*): n=(\d+)',line)
        if m and int(m.group(2))==want:
            fs=[x for x in line.split() if pat.search(x)]
            print(m.group(1).decode(), b' '.join(fs).decode('latin1'))
        if m and int(m.group(2))>want+2: break

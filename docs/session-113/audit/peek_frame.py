import re,sys
p=sys.argv[1]; want=int(sys.argv[2])
got=0
with open(p,'rb') as f:
    for line in f:
        if line.startswith(b'FrameTrace'):
            m=re.match(rb'^(FrameTrace[-\w]*): n=(\d+)',line)
            if m and int(m.group(2))==want:
                print(line[:6000].decode('latin1'))
                got+=1
                if got>=12: break

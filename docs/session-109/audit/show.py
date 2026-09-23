import sys
# usage: show.py <file> <from> <to>
sys.stdout.reconfigure(encoding='utf-8')
p = sys.argv[1]
a = int(sys.argv[2]); b = int(sys.argv[3])
L = open(p, 'rb').read().decode('utf-8', 'replace').split('\n')
for i in range(a - 1, min(b, len(L))):
    print(f'{i+1:6d}  {L[i].rstrip()}')

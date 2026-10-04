# F19c2: next dd cycle = last recorded cycle + 1 (0 if none). Usage: python next_cycle.py <cycles file>
import re
import sys

v = [int(m) for m in re.findall(r'^cycle=(\d+) ', open(sys.argv[1], encoding='utf-8').read(), re.M)]
print(max(v) + 1 if v else 0)

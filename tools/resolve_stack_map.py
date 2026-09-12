"""Annotate windows_hang_dump stacks with the matching clang/lld emulator map."""
import bisect
import pathlib
import re
import sys

symbols = []
for line in pathlib.Path(sys.argv[1]).open(encoding='utf-8', errors='replace'):
    match = re.match(r'\s*([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+(\S.*)$', line)
    if not match or int(match[2], 16) != 0:
        continue
    name = match[4].strip()
    if not name.startswith(('.', '<', 'CMakeFiles')):
        symbols.append((int(match[1], 16), name))
symbols.sort()
offsets = [address for address, _ in symbols]
for line in pathlib.Path(sys.argv[2]).open(encoding='utf-8', errors='replace'):
    match = re.search(r'\bkyty_emulator(?:\.exe)?\+0x([0-9a-f]+)', line, re.IGNORECASE)
    if match:
        address = int(match[1], 16)
        index = bisect.bisect_right(offsets, address) - 1
        if index >= 0:
            start, name = symbols[index]
            line = line.rstrip('\n') + f' [map] {name}+0x{address-start:x}\n'
    print(line, end='')

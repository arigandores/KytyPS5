"""m5_sass_full.py -- session 102, M5: the whole CS/FS code of every module m5_recompile.py built,
disassembled with nvdisasm, and the SASS columns of C:/kyty/s102/m5/regs.json refreshed from it.

Why not only scripts/s16_sass.py: (1) the VkPipelineCache blob can hold several zstd frames and
s16 decompresses the first only (a pixel pipeline's FS can sit in another frame than its VS);
(2) "Binary Size" ends with NOP padding and a non-code trailer nvdisasm rejects, so the code is the
longest cleanly decoding prefix of Binary Size (cut at the first address nvdisasm rejects), and the
instruction count drops the trailing NOP padding and BRA-to-self; out-of-line code after the last
EXIT is kept (the tiled CS 56a1 has ~20 KB of it); (3) for pixel shaders s16 stops at the FIRST
EXIT, which truncates programs with an early exit.
Start of the program: CS - the prologue `LDC R1, c[0x0][0x37c]` (as s16); PS - the lowest offset
>= last_exit + 16 - Binary Size from which the window to the last EXIT decodes cleanly.
Usage: python C:/kyty/s102/m5_sass_full.py [module-substring]
"""
import json
import os
import re
import subprocess
import sys

import zstandard

M5 = 'C:/kyty/s102/m5'
PIPESTAT = r'C:\kyty\tools\pipestat\pipestat.exe'
NVDISASM = r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.1\bin\nvdisasm.exe'
SM = 'SM120'
PROLOGUE = bytes.fromhex('827b01ff00df0000')
EXIT = bytes.fromhex('4d79000000000000')
SLACK = 1024  # bytes of Binary Size allowed after the code (padding + non-code trailer)
KEYS = ['LDG', 'LDC', 'LDCU', 'ULDC', 'LDS', 'LD', 'STL', 'LDL', 'ISETP', 'BRA', 'TEX', 'EXIT']


def opcode_counts(text):
    ops, n = {}, 0
    for line in text.splitlines():
        m = re.match(r'\s*/\*[0-9a-f]+\*/\s+(.*?)\s*;', line)
        if not m:
            continue
        n += 1
        t = re.sub(r'^@!?U?P\w+\s+', '', m.group(1))
        op = t.split()[0].split('.')[0] if t.split() else ''
        ops[op] = ops.get(op, 0) + 1
    return n, {k: ops.get(k, 0) for k in KEYS}


MEM_OPS = ('LDG', 'LDC', 'LDCU', 'ULDC', 'LDL', 'STL', 'LDS', 'STS', 'STG', 'LD', 'ST', 'ATOMG', 'RED')


def memory_op_widths(text):
    """Load/store widths (added for the V2s control, session 102): every memory opcode with its
    full suffix (LDG.E.128, LDC.64, LDCU.64, LDG.E.STRONG.SM, ...), per-class width histograms in
    bits (a missing size suffix = 32), and LDC/LDCU/ULDC split by operand: `cx[...]` = indexed
    (bindless) constant bank, i.e. a uniform-buffer DESCRIPTOR load, vs `c[0x..]` = a fixed bank
    (push/driver constants)."""
    full, widths, const_split = {}, {}, {}
    for line in text.splitlines():
        m = re.match(r'\s*/\*[0-9a-f]+\*/\s+(.*?)\s*;', line)
        if not m:
            continue
        t = re.sub(r'^@!?U?P\w+\s+', '', m.group(1))
        parts = t.split()
        if not parts:
            continue
        op = parts[0]
        base = op.split('.')[0]
        if base not in MEM_OPS:
            continue
        full[op] = full.get(op, 0) + 1
        bits = 32
        for suffix in op.split('.')[1:]:
            if suffix in ('64', '128', 'U8', 'S8', 'U16', 'S16'):
                bits = {'64': 64, '128': 128, 'U8': 8, 'S8': 8, 'U16': 16, 'S16': 16}[suffix]
        key = f'{base}.{bits}'
        widths[key] = widths.get(key, 0) + 1
        if base in ('LDC', 'LDCU', 'ULDC'):
            kind = 'cx' if 'cx[' in t else 'c'
            ck = f'{base}.{kind}.{bits}'
            const_split[ck] = const_split.get(ck, 0) + 1
    return {'ops_full': dict(sorted(full.items())), 'widths': dict(sorted(widths.items())),
            'const_bank_split': dict(sorted(const_split.items()))}


def frames(blob):
    """Every zstd frame of the pipeline-cache blob, decompressed."""
    out = []
    for m in re.finditer(re.escape(bytes.fromhex('28b52ffd')), blob):
        try:
            out.append((m.start(), zstandard.ZstdDecompressor().decompressobj().decompress(blob[m.start():])))
        except zstandard.ZstdError:
            continue
    return out


def trimmed_count(text):
    """Instructions without the NOP padding (and the BRA-to-self before it) at the end."""
    insts = []
    for line in text.splitlines():
        m = re.match(r'\s*/\*([0-9a-f]+)\*/\s+(.*?)\s*;', line)
        if m:
            insts.append(m.group(2))
    while insts and re.sub(r'^@!?U?P\w+\s+', '', insts[-1]).split()[0] == 'NOP':
        insts.pop()
    if insts and re.sub(r'^@!?U?P\w+\s+', '', insts[-1]).split()[0] == 'BRA':
        insts.pop()
    return len(insts)


def full_disasm(spv, pixel, base):
    cache = base + '.full.cache.bin'
    raw = base + '.full.raw.bin'
    r = subprocess.run([PIPESTAT] + (['--ps'] if pixel else []) + ['--dump-cache', cache, spv],
                       capture_output=True, text=True, errors='replace')
    res = {'pipestat_rc': r.returncode}
    wanted = 'FS' if pixel else 'CS'
    for m in re.finditer(r'exec \d+ "(\w+)"[^:]*:(.*)', r.stdout):
        if m.group(1) == wanted:
            res['stats'] = {k.strip(): int(v) for k, v in re.findall(r'([A-Za-z ]+?)=(\d+)', m.group(2))}
    binary = res.get('stats', {}).get('Binary Size', 0)
    if r.returncode != 0 or not os.path.exists(cache) or binary == 0:
        res['error'] = 'pipestat failed'
        return res

    def dis(body, start, length):
        open(raw, 'wb').write(body[start:start + length])
        return subprocess.run([NVDISASM, '--binary', SM, raw], capture_output=True, text=True, errors='replace')

    def clean(r2):
        return r2.returncode == 0 and 'error' not in r2.stderr

    def longest_prefix(body, start):
        """The longest cleanly decoding prefix of [start, start + Binary Size): the whole program
        when it decodes, else up to the first address nvdisasm rejects (the non-code trailer)."""
        r2 = dis(body, start, binary)
        if clean(r2):
            return binary, r2.stdout, 'binary-size'
        errs = [int(a, 16) for a in re.findall(r'at address 0x([0-9a-f]+)', r2.stderr)]
        if not errs:
            return None
        length = min(errs) & ~15
        if length < binary - SLACK:
            return None
        r3 = dis(body, start, length)
        return (length, r3.stdout, 'to-first-decode-error') if clean(r3) else None

    found = None
    for frame_offset, body in frames(open(cache, 'rb').read()):
        if not pixel:
            for s in [m.start() for m in re.finditer(re.escape(PROLOGUE), body)]:
                window = longest_prefix(body, s)
                if window is not None:
                    found = (frame_offset, s) + window
                    break
        else:
            # Start: the lowest offset >= last_exit + 16 - Binary Size from which the window to
            # that EXIT decodes (a window shorter than Binary Size - SLACK is another program, the
            # pipeline's VS stub); then the longest clean prefix from there, which also takes any
            # out-of-line code placed after the last EXIT.
            exits = [m.start() for m in re.finditer(re.escape(EXIT), body)]
            for e in sorted(exits, reverse=True):
                end = e + 16
                s = max(0, end - binary)
                s += (8 - s % 8) % 8
                while s <= end - binary + SLACK and s < end - 64 and found is None:
                    r2 = dis(body, s, end - s)
                    if clean(r2):
                        window = longest_prefix(body, s) or (end - s, r2.stdout, 'to-last-exit')
                        found = (frame_offset, s) + window
                    s += 8
                if found is not None:
                    break
        if found is not None:
            break
    for p in (cache, raw):
        if os.path.exists(p):
            os.remove(p)
    if found is None:
        res['error'] = 'no clean window'
        return res
    frame_offset, s, length, text, method = found
    open(base + '.full.sass', 'w', encoding='utf-8').write(text)
    n, keys = opcode_counts(text)
    res.update({'frame': frame_offset, 'start': s, 'size': length, 'method': method,
                'instructions': trimmed_count(text), 'instructions_raw': n, 'ops': keys,
                'mem': memory_op_widths(text), 'sass': base + '.full.sass'})
    return res


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else ''
    regs = json.load(open(f'{M5}/regs.json', encoding='utf-8'))
    rec = json.load(open(f'{M5}/recompile.json', encoding='utf-8'))
    spv = {}
    for item in rec['items']:
        for cache in item['caches']:
            for m in cache['modules']:
                spv[m['name']] = m['spv']
    for row in regs['rows']:
        if only not in row['module']:
            continue
        base = f"{M5}/sass/{row['module']}"
        f = full_disasm(spv[row['module']], row['stage'] == 'ps', base)
        st = f.get('stats', {})
        row.update({'full_window': [f.get('start'), f.get('size')], 'full_frame': f.get('frame'),
                    'full_instructions_raw': f.get('instructions_raw'),
                    'full_method': f.get('method'), 'full_instructions': f.get('instructions'),
                    'full_ops': f.get('ops'), 'full_error': f.get('error'),
                    'full_sass': f.get('sass'), 'full_binary_size': st.get('Binary Size'),
                    'full_register_count': st.get('Register Count'), 'full_mem': f.get('mem')})
        print(f"{row['module']}: {f.get('method')} frame={f.get('frame')} start={f.get('start')} size={f.get('size')}"
              f"/{st.get('Binary Size')} insts={f.get('instructions')} err={f.get('error')} ops={f.get('ops')}",
              flush=True)
    regs['note'] = ('REPORTED numbers, not decisions (pred/01 §6). local_memory_bytes = low dword of pipestat '
                    'Local Memory Size. full_* = m5_sass_full.py: the whole CS/FS code (all zstd frames, the '
                    'longest clean prefix of Binary Size; full_instructions excludes the trailing NOP/BRA '
                    'padding, full_instructions_raw includes it); s16_* = scripts/s16_sass.py (first zstd '
                    'frame only; its PS window ends at the first unconditional EXIT). full_mem = memory '
                    'opcodes with their width suffix; const_bank_split: cx[] = indexed constant bank '
                    '(uniform-buffer descriptor load), c[] = fixed bank.')
    json.dump(regs, open(f'{M5}/regs.json', 'w', encoding='utf-8'), indent=1)


if __name__ == '__main__':
    main()

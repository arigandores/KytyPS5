"""f7d_chain.py - F7d (HPP-443, Red Team): offline reading of F7b replay outputs (no RenderDoc, no Vulkan device).

(1) Pass chain of the floor pixels F1-F6 and controls A1/U1/R1 after the G-buffer: every target of rd/rd_f7b_hist.txt, every
    event with its passed flag, pre/out/post; and the events with no draw between the clear of 6687 (EID 3394) and the first
    draw on 6687 (EID 3485), from C:/kyty/f287/f7a/rd_list_600.txt.
(2) T# (GFX10 image descriptor) decode of the PS 508 flattened SRT of draw 950 (rd/buf_e950_ps_204_2331648.bin): 2D entries
    with power-of-two sizes; base address = (dword0 | (dword1 & 0xff) << 32) << 8, width-1 = dword1[31:30] | dword2[11:0] << 2,
    height-1 = dword2[29:14], format = dword1[28:20], dst_sel = dword3[11:0], sw_mode = dword3[24:20], type = dword3[31:28].
(3) Used image slots of PS 508 per STATE block (draws 950/960 floor, 1321 plate, and the second frame copies).
"""
import re, struct, hashlib

RD = 'C:/kyty/f287/f7b/rd'
HIST = RD + '/rd_f7b_hist.txt'
LIST = 'C:/kyty/f287/f7a/rd_list_600.txt'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    print('inputs: rd_f7b_hist.txt %s rd_list_600.txt %s buf_e950_ps_204_2331648.bin %s' % (
        sha(HIST)[:16], sha(LIST)[:16], sha(RD + '/buf_e950_ps_204_2331648.bin')[:16]))
    t = open(HIST, 'rb').read().decode('utf-8', 'replace').split('\n')
    print('== (1) post-G-buffer chain per point (targets after 6685/13050; passed events and the 3394/3485 pair)')
    cur = None
    for l in t:
        if l.startswith('-- HIST'):
            m = re.match(r'-- HIST (\S+) \((\d+),(\d+)\) on tex (\d+) ', l)
            cur = m.groups() if m else None
            continue
        if not cur or cur[3] in ('13938', '12700', '13577', '14064'):
            continue
        mm = re.match(r'\s*eid (\d+) (\S+) passed=(\S+) prim=(\d+) frag=\d+ pre=\(([^)]*)\) out=\(([^)]*)\) post=\(([^)]*)\)', l)
        if not mm:
            continue
        eid = int(mm.group(1))
        if cur[3] in ('6687', '6633', '6450', '13036', '13996', '5784', '5685', '4005', '13033') and (
                mm.group(3) == 'True' or eid in (3394, 3485, 7191, 7282)):
            print('  %-3s tex %-5s eid %4d %-26s passed=%-5s pre=(%s) out=(%s) post=(%s)' % (
                cur[0], cur[3], eid, mm.group(2), mm.group(3), mm.group(5), mm.group(6), mm.group(7)))
    print('== (1b) events between EID 3394 and 3485 (rd_list_600.txt)')
    for l in open(LIST, 'rb').read().decode('utf-8', 'replace').split('\n'):
        m = re.match(r'EID=(\d+) (\S+)', l)
        if m and 3394 <= int(m.group(1)) <= 3485:
            print('  ' + l[:110])
    print('== (2) T# of the PS 508 SRT, draw 950')
    b = open(RD + '/buf_e950_ps_204_2331648.bin', 'rb').read()
    d = struct.unpack('<%dI' % (len(b) // 4), b)
    n_big = n_small = zero_addr = 0
    for i in range(0, len(d) - 3):
        d0, d1, d2, d3 = d[i:i + 4]
        if (d3 >> 28) & 15 != 9:
            continue
        w = (((d1 >> 30) & 3) | ((d2 & 0xfff) << 2)) + 1
        h = ((d2 >> 14) & 0xffff) + 1
        if w not in (1, 2048) or h not in (1, 2048):
            continue
        addr = (d0 | ((d1 & 0xff) << 32)) << 8
        sel = [(d3 >> (3 * k)) & 7 for k in range(4)]
        print('  byte %4d %4dx%-4d fmt=%3d addr=%#012x dst_sel=%s sw_mode=%d' % (
            i * 4, w, h, (d1 >> 20) & 0x1ff, addr, sel, (d3 >> 20) & 31))
        if w == 1:
            n_small += 1
        else:
            n_big += 1
        zero_addr += addr == 0
    print('  2D T#: 2048x2048 %d, 1x1 %d, zero address %d' % (n_big, n_small, zero_addr))
    print('== (3) used image slots of PS 508 per STATE block')
    i = 0
    while i < len(t):
        if t[i].startswith('==== STATE'):
            hdr = t[i][11:40]
            j = i + 1
            ps = None
            ro = []
            while j < len(t) and not t[j].startswith('==== STATE'):
                s = t[j].strip()
                if s.startswith('ps shader'):
                    ps = s.split()[2]
                if s.startswith('RO idx=0 arr=') and ps:
                    ro.append(int(s.split()[2].split('=')[1]))
                j += 1
            if ps == '508':
                print('  line %d %s ... slots %d: %s' % (i + 1, hdr, len(ro), ro))
            i = j
        else:
            i += 1
    print('ALL OK')


if __name__ == '__main__':
    main()

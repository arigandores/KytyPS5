# F29d (HPP-703, Red Team): where two PE files of the same size differ - per section, plus the COFF TimeDateStamp, the
# optional-header CheckSum and the CodeView (RSDS) record of the debug directory. Prints the differing byte runs mapped to
# a section and, if every difference falls in the header timestamp / checksum / debug data (RSDS GUID/age, POGO/repro
# records), the line "ONLY BUILD-ID FIELDS DIFFER"; otherwise "CODE/DATA DIFFER".
# Usage: python pediff.py <a.exe> <b.exe>
import struct
import sys


def sections(d):
    pe = struct.unpack_from("<I", d, 0x3C)[0]
    nsec = struct.unpack_from("<H", d, pe + 6)[0]
    opt = struct.unpack_from("<H", d, pe + 20)[0]
    base = pe + 24 + opt
    out = []
    for i in range(nsec):
        o = base + 40 * i
        name = d[o:o + 8].rstrip(b"\0").decode()
        vsize, va, rsize, raw = struct.unpack_from("<IIII", d, o + 8)
        out.append((name, va, vsize, raw, rsize))
    return pe, out


def debug_ranges(d, pe, secs):
    magic = struct.unpack_from("<H", d, pe + 24)[0]
    dd = pe + 24 + (112 if magic == 0x20B else 96)
    va, size = struct.unpack_from("<II", d, dd + 6 * 8)
    ranges = []

    def off(rva):
        for name, sva, vs, raw, rs in secs:
            if sva <= rva < sva + max(vs, rs):
                return raw + rva - sva
        return None
    o = off(va)
    if o is None:
        return ranges
    ranges.append((o, o + size, "debugdir"))
    for k in range(size // 28):
        e = o + 28 * k
        ts = e + 4
        ranges.append((ts, ts + 4, "debugdir.ts"))
        typ, sz, rva, ptr = struct.unpack_from("<IIII", d, e + 12)
        ranges.append((ptr, ptr + sz, "debugdata.type%d" % typ))
    return ranges


def main():
    a = open(sys.argv[1], "rb").read()
    b = open(sys.argv[2], "rb").read()
    print("sizes", len(a), len(b))
    if len(a) != len(b):
        print("CODE/DATA DIFFER (size)")
        return
    pe, secs = sections(a)
    known = [(pe + 8, pe + 12, "coff.TimeDateStamp"), (pe + 24 + 64, pe + 24 + 68, "opt.CheckSum")]
    known += debug_ranges(a, pe, secs)
    runs = []
    i = 0
    n = len(a)
    while i < n:
        if a[i] != b[i]:
            j = i
            while j < n and a[j] != b[j]:
                j += 1
            runs.append((i, j))
            i = j
        else:
            i += 1
    print("differing runs", len(runs), "bytes", sum(j - i for i, j in runs))
    unknown = 0
    for i, j in runs:
        tag = [k for s, e, k in known if s <= i < e]
        sec = [nm for nm, va, vs, raw, rs in secs if raw <= i < raw + rs]
        if not tag:
            unknown += 1
        if len(runs) <= 40 or not tag:
            print("  0x%08x +%d section=%s field=%s" % (i, j - i, sec[0] if sec else "hdr", tag[0] if tag else "?"))
    print("ONLY BUILD-ID FIELDS DIFFER" if unknown == 0 else "CODE/DATA DIFFER: %d runs outside build-id fields" % unknown)


if __name__ == "__main__":
    main()

# F3b (HPP-340, ROADMAP p.259(e)(2)): form of the BVH descriptor at every IMAGE_BVH_INTERSECT_RAY of the
# 20 BVH programs of eboot.bin, by reaching definitions over the reachable control flow (backward walk
# from the BVH instruction over instruction-level predecessors; a path stops at the first instruction that
# writes the register). For the base (dword0 = s[q], dword1 = s[q+1]) the expected form is
#   s[q:q+1] = S_BFE_U64 X, 0x00280008   (base_address = X >> 8, 40 bits)
# optionally followed by S_BITSET1_B32 s[q+1], 31 (box_sort_en, bit 63; does not touch bits [7:0] of dword1),
# which the walk passes through and records.
import sys, os, struct, collections, json

if os.path.exists("C:/kyty/SEALED_RUN.lock"):
    sys.exit(3)
OUT = "C:/kyty/f287/f3b/"
src = open(OUT + "bvhmap_f3b.py", "rb").read().decode("utf-8")
exec(compile(src[:src.index("# ---- check the decoder")], "bvhmap_prefix", "exec"))
sys.path.insert(0, OUT)
from reach_f3b import reachable

lines = []


def p(*a):
    lines.append(" ".join(str(x) for x in a))


def writes_of(r, w0, w1):
    """Registers an instruction writes, refined for VOP3 (VOPC-in-VOP3 sdst pair, VOP3B sdst pair)."""
    regs = list(r["writes"])
    if r["fam"] == "VOP3":
        op = r["op"]
        if op <= 0xFF:  # VOPC encoded as VOP3: sdst = vdst field, a pair in wave64
            regs = [w0 & 0xFF, (w0 & 0xFF) + 1]
        elif op in (0x360, 0x361):  # v_readlane_b32 (sdst), v_writelane writes a VGPR
            regs = [w0 & 0xFF] if op == 0x360 else []
        elif op in (0x30F, 0x310, 0x319, 0x176, 0x177, 0x16D, 0x16E, 0x128, 0x129, 0x12A):
            sd = (w0 >> 8) & 0x7F
            regs = [sd, sd + 1]
        else:
            regs = []
    if r["fam"] == "VOPC":
        regs = [106, 107]
    return regs


EXPECTED_LIT = 0x00280008
programs_bvh = []
for prog in programs:
    words = list(struct.unpack_from("<%dI" % (prog["size"] // 4), mm, prog["start"]))
    recs, bad = reachable(decode, words)
    if not any(r["fam"] == "MIMG" and r["op"] in (0xE6, 0xE7) for r in recs):
        continue
    programs_bvh.append((prog, words, recs, bad))
p("BVH programs (reachable decode):", len(programs_bvh), "unknown-family hits:", sum(b for *_, b in programs_bvh))

forms = collections.Counter()
rows = []
for prog, words, recs, bad in programs_bvh:
    by_pc = {r["pc"]: r for r in recs}
    preds = collections.defaultdict(list)
    for r in recs:
        i = r["pc"] // 4
        w = words[i]
        nxt = r["pc"] + r["size"] * 4
        stop = False
        if r["fam"] == "SOPP":
            op = r["op"]
            imm = w & 0xFFFF
            simm = imm - 0x10000 if imm & 0x8000 else imm
            tgt = r["pc"] + 4 + simm * 4
            if op in (1, 27, 31):
                stop = True
            elif op == 2:
                preds[tgt].append(r["pc"])
                stop = True
            elif op in (4, 5, 6, 7, 8, 9, 23, 24, 25, 26):
                preds[tgt].append(r["pc"])
        elif r["fam"] == "SOP1" and r["op"] == 32:
            stop = True
        if not stop and nxt in by_pc:
            preds[nxt].append(r["pc"])

    def reaching(pc0, reg, transparent):
        """Writers of `reg` reaching pc0; `transparent(r)` -> True for writers passed through (recorded)."""
        found, passed = set(), set()
        seen = set()
        work = list(preds[pc0])
        while work:
            pc = work.pop()
            if pc in seen:
                continue
            seen.add(pc)
            r = by_pc[pc]
            i = pc // 4
            w0 = words[i]
            if reg in writes_of(r, w0, words[i + 1] if i + 1 < len(words) else 0):
                if transparent(r):
                    passed.add(pc)
                else:
                    found.add(pc)
                    continue
            work.extend(preds[pc])
        if not preds[pc0]:
            found.add(-1)
        return found, passed

    def desc(pc):
        if pc == -1:
            return "ENTRY"
        r = by_pc[pc]
        if r["fam"] == "SOP2":
            t = "S_BFE_U64" if r["op"] == 41 else "SOP2 op%d" % r["op"]
            return "%s s%d%s @0x%x" % (t, r["dst"], ", 0x%08x" % r["lit"] if r.get("lit") is not None else "", pc)
        if r["fam"] == "SOP1":
            nm = {29: "S_BITSET1_B32", 4: "S_MOV_B64", 3: "S_MOV_B32"}.get(r["op"], "SOP1 op%d" % r["op"])
            return "%s s%d @0x%x" % (nm, r["dst"], pc)
        if r["fam"] == "SMEM":
            return "SMEM op%d s%d @0x%x" % (r["op"], r["writes"][0] if r["writes"] else -1, pc)
        return "%s op%s @0x%x" % (r["fam"], r["op"], pc)

    is_sort_bit = lambda r: r["fam"] == "SOP1" and r["op"] == 29 and r.get("s0") == 128 + 31
    for b in [r for r in recs if r["fam"] == "MIMG" and r["op"] in (0xE6, 0xE7)]:
        q = b["srsrc"]
        lo, _ = reaching(b["pc"], q, lambda r: False)
        hi, hi_pass = reaching(b["pc"], q + 1, is_sort_bit)

        def is_bfe(pc):
            if pc == -1:
                return False
            r = by_pc[pc]
            return r["fam"] == "SOP2" and r["op"] == 41 and r.get("lit") == EXPECTED_LIT and r["dst"] == q

        ok = lo and hi and all(is_bfe(x) for x in lo) and all(is_bfe(x) for x in hi) and lo == hi
        form = "X>>8 (S_BFE_U64 X, 0x00280008)" if ok else "OTHER"
        forms[form] += 1
        bfe_pc = sorted(lo)[0] if ok else None
        src_reg = by_pc[bfe_pc]["s0"] if ok else None
        rows.append(dict(hash="%016x" % prog["hash"], eboot_elf=hex(prog["elf"]), pc=hex(b["pc"]),
                         op="IMAGE_BVH64_INTERSECT_RAY" if b["op"] == 0xE7 else "IMAGE_BVH_INTERSECT_RAY",
                         srsrc="s[%d:%d]" % (q, q + 3), form=form,
                         base_lo=[desc(x) for x in sorted(lo)], base_hi=[desc(x) for x in sorted(hi)],
                         sort_bit=[desc(x) for x in sorted(hi_pass)],
                         bfe_src="s[%d:%d]" % (src_reg, src_reg + 1) if src_reg is not None else None,
                         bfe_eboot=hex(prog["start"] + bfe_pc) if ok else None))

p("form of the descriptor base at every BVH instruction:", dict(forms))
p("distinct BFE sites feeding a BVH base:", len({r["bfe_eboot"] for r in rows if r["bfe_eboot"]}))
p("")
p("| program | BVH pc | op | T# | form | base writers (dword0) | base writers (dword1) | bit 63 (box_sort_en) | BFE source | BFE in eboot |")
for r in rows:
    p("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
        r["hash"], r["pc"], r["op"], r["srsrc"], r["form"], "; ".join(r["base_lo"]), "; ".join(r["base_hi"]),
        "; ".join(r["sort_bit"]) or "-", r["bfe_src"], r["bfe_eboot"]))
open(OUT + "form_f3b.out.txt", "wb").write(("\n".join(lines) + "\n").encode("utf-8"))
json.dump(rows, open(OUT + "form_f3b.rows.json", "w"), indent=1)
print("\n".join(lines))

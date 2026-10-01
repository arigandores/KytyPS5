# F3b: reachable decode (control flow from pc 0, as the emulator's CFG builder walks it).
# Replaces the linear decode of bvhmap_f3b.py: .shader_text often carries data after the code.
# Stops a path at s_endpgm (SOPP 1), s_endpgm_saved (27), s_code_end (31), s_setpc_b64 (SOP1 32);
# follows s_branch (2) and conditional branches (4..9, 23..26) both ways, s_call_b64 (SOPK 22) both ways.


def decode_at(decode, words, i):
    rec = decode(words[i:i + 8])[0]
    rec = dict(rec)
    rec["pc"] = i * 4
    return rec


def reachable(decode, words):
    n = len(words)
    seen = {}
    work = [0]
    bad = 0
    while work:
        i = work.pop()
        while 0 <= i < n and i not in seen:
            r = decode_at(decode, words, i)
            seen[i] = r
            if r["fam"] == "UNKNOWN":
                bad += 1
                break
            w = words[i]
            nxt = i + r["size"]
            if r["fam"] == "SOPP":
                op = r["op"]
                imm = w & 0xFFFF
                simm = imm - 0x10000 if imm & 0x8000 else imm
                tgt = i + 1 + simm
                if op in (1, 27, 31):
                    break
                if op == 2:
                    i = tgt
                    continue
                if op in (4, 5, 6, 7, 8, 9, 23, 24, 25, 26):
                    work.append(tgt)
            elif r["fam"] == "SOP1" and r["op"] == 32:
                break
            elif r["fam"] == "SOPK" and r["op"] == 22:
                imm = w & 0xFFFF
                simm = imm - 0x10000 if imm & 0x8000 else imm
                work.append(i + 1 + simm)
            i = nxt
    return [seen[k] for k in sorted(seen)], bad

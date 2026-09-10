"""Inspect AGC header candidates and registration lead times; never compile or modify game data.

Accepts a flat little-endian ELF64 (not a SELF eboot.bin) and/or a log recorded with
KYTY_SHADER_REGISTER_TRACE=1. Header counts are not counts of unique shaders or pipelines.
"""

import argparse
import collections
import json
from pathlib import Path
import re
import statistics
import struct


MAGIC = b"1234\x18\0\0\0"
STAGES = {1: "vertex", 2: "pixel", 4: "compute", 5: "mesh"}


def scan_headers(data):
    if len(data) < 64 or data[:6] != b"\x7fELF\x02\x01":
        raise ValueError("expected a flat little-endian ELF64, not a SELF executable")
    phoff = struct.unpack_from("<Q", data, 32)[0]
    entsize, count = struct.unpack_from("<HH", data, 54)
    if entsize < 56 or phoff + entsize * count > len(data):
        raise ValueError("invalid ELF program header table")
    loads = []
    for i in range(count):
        kind, _, off, va, _, filesz, _, _ = struct.unpack_from("<IIQQQQQQ", data, phoff + entsize * i)
        if kind == 1:
            if off + filesz > len(data):
                raise ValueError("truncated ELF load segment")
            loads.append((off, off + filesz, va))

    def relative(offset, field, size, low, high):
        delta = struct.unpack_from("<q", data, offset + field)[0]
        target = offset + field + delta
        if delta == 0:
            return None if size else []
        if not low <= target <= high - size:
            return None
        return target

    headers = []
    offset = data.find(MAGIC)
    while offset != -1:
        segment = next((s for s in loads if s[0] <= offset and offset + 93 <= s[1]), None)
        if segment:
            low, high, va = segment
            hs, cs, cb, target, ni, scratch, no, special_size, ty, ncx, nsh = struct.unpack_from(
                "<IIIIIHHHBBB", data, offset + 64)
            valid = (96 <= hs <= 1_000_000 and offset + hs <= high
                     and 0 < cs <= 1_000_000 and cs % 4 == 0 and ty <= 6)
            tables = {}
            for name, field, count in (("sh", 32, nsh), ("cx", 24, ncx)):
                ptr = relative(offset, field, count * 8, low, high)
                if ptr is None:
                    valid = False
                    break
                tables[name] = [list(struct.unpack_from("<II", data, ptr + i * 8))
                                for i in range(count)]
            if valid:
                headers.append(dict(file_offset=offset, elf_vaddr=va + offset - low,
                                    header_size=hs, code_size=cs, type=ty,
                                    scratch_dwords=scratch, sh_registers=tables["sh"],
                                    cx_registers=tables["cx"]))
        offset = data.find(MAGIC, offset + 1)
    return dict(header_candidates=len(headers),
                candidates_by_binary_type=dict(collections.Counter(h["type"] for h in headers)),
                note="Header candidates only; code payloads and uniqueness are not verified.",
                headers=headers)


def analyze_log(lines):
    registration = re.compile(r"ShaderRegister: hash=([0-9a-f]+) type=(\d+) size=(\d+).*?host_us=(\d+)")
    first_use = re.compile(r"ShaderFirstUse: hash=([0-9a-f]+) stage=(\d+).*?host_us=(\d+)")
    registered = {}
    used = {}
    registration_events = 0
    for line in lines:
        match = registration.search(line)
        if match:
            shader, ty, size, timestamp = match.groups()
            registration_events += 1
            entry = dict(hash=shader, binary_type=int(ty), code_size=int(size), host_us=int(timestamp))
            # Log lines from separate threads can arrive out of timestamp order.
            if shader not in registered or entry["host_us"] < registered[shader]["host_us"]:
                registered[shader] = entry
        match = first_use.search(line)
        if match:
            shader, stage, timestamp = match.groups()
            key = int(stage), shader
            used[key] = min(used.get(key, int(timestamp)), int(timestamp))
    rows = []
    for (stage, shader), timestamp in sorted(used.items()):
        reg = registered.get(shader)
        rows.append(dict(hash=shader, stage=STAGES.get(stage, str(stage)),
                         lead_seconds=(timestamp - reg["host_us"]) / 1e6 if reg else None))
    summaries = {}
    for stage in sorted({r["stage"] for r in rows}):
        subset = [r for r in rows if r["stage"] == stage]
        leads = [r["lead_seconds"] for r in subset if r["lead_seconds"] is not None]
        summaries[stage] = dict(first_use_hashes=len(subset), matched=len(leads),
                                registered_before_use=sum(t >= 0 for t in leads),
                                lead_at_least_1s=sum(t >= 1 for t in leads),
                                lead_at_least_5s=sum(t >= 5 for t in leads),
                                median_seconds=statistics.median(leads) if leads else None,
                                min_seconds=min(leads) if leads else None,
                                max_seconds=max(leads) if leads else None)
    used_hashes = {shader for _, shader in used}
    return dict(registration_events=registration_events, registered_hashes=len(registered),
                registered_by_binary_type=dict(collections.Counter(r["binary_type"] for r in registered.values())),
                registered_without_matching_use=sum(h not in used_hashes for h in registered),
                stages=summaries, first_uses=rows,
                note="First program lookup, not GPU execution; warm-run lead times are not cold-run guarantees. "
                     "Mesh programs can combine hashes; an unmatched registration does not prove a shader is unused.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--elf", type=Path)
    parser.add_argument("--log", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.elf and not args.log:
        parser.error("provide --elf and/or --log")
    report = {}
    if args.elf:
        report["elf"] = scan_headers(args.elf.read_bytes())
    if args.log:
        with args.log.open(encoding="utf-8", errors="replace") as lines:
            report["log"] = analyze_log(lines)
    # Refuse replacement: reports can be evidence for comparisons between builds.
    with args.output.open("x", encoding="utf-8") as output:
        json.dump(report, output, indent=2)
        output.write("\n")
    compact = {k: {name: value for name, value in section.items() if name not in ("headers", "first_uses")}
               for k, section in report.items()}
    print(json.dumps(compact, indent=2))


if __name__ == "__main__":
    main()

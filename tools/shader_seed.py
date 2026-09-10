"""Export an immutable startup shader catalogue from a verified game run.

python tools/shader_seed.py --cache <_ShaderCache/TITLE> --log <_kyty.txt> \
    --output <_ShaderSeeds/TITLE>

Only compatible translation entries are included. No driver cache or game assets are copied.
The emulator validates payload checksums and the game/GPU/translator profile on installation.
"""

import argparse
import hashlib
import json
from pathlib import Path
import struct


def read_key(data, offset):
    if offset + 24 > len(data):
        raise ValueError("Truncated shader key")
    words = struct.unpack_from("<I", data, offset + 20)[0]
    end = offset + 24 + words * 4
    if words > 4096 or end > len(data):
        raise ValueError("Invalid shader key size")
    return data[offset:end], end


def recipe_keys(data, offset, count, layout):
    vs, ps, cs, rendering, vertex_input, parameters = map(int, layout.split(b":"))
    keys = set()
    for _ in range(count):
        if offset >= len(data):
            raise ValueError("Truncated recipes")
        kind = data[offset]
        key, offset = read_key(data, offset + 1)
        keys.add(key)
        offset += 4  # permutation index
        if kind == 1:
            if offset >= len(data):
                raise ValueError("Truncated graphics recipe")
            active = data[offset]
            offset += 1
            if active not in (0, 1):
                raise ValueError("Invalid pixel stage flag")
            if active:
                key, offset = read_key(data, offset)
                keys.add(key)
                offset += 4
            offset += rendering + vertex_input + parameters + vs + (ps if active else 0)
        elif kind == 2:
            offset += cs
        else:
            raise ValueError("Unknown pipeline recipe kind")
    if offset != len(data):
        raise ValueError("Truncated recipes or unexpected trailing data")
    return keys


def export_seed(cache: Path, log: Path, output: Path):
    recipes = (cache / "pipelines.bin").read_bytes()
    if not recipes.startswith(b"KytyPR1\n") or len(recipes) < 16:
        raise ValueError("Invalid pipeline recipe header")
    size = struct.unpack_from("<I", recipes, 8)[0]
    if size > 4096 or len(recipes) < 16 + size:
        raise ValueError("Invalid pipeline signature size")
    signature = recipes[12:12 + size]
    translation, layout = signature.split(b"\n", 1)
    translation += b"\n"
    count = struct.unpack_from("<I", recipes, 12 + size)[0]
    if count == 0:
        raise ValueError("No recipes to export")
    required = recipe_keys(recipes, 16 + size, count, layout)
    compatibility = None
    with log.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            if line.startswith("ShaderSeed: compatibility="):
                compatibility = line.strip().split("=", 1)[1]
    profile = translation.decode().replace("\n", ":") + ":" + layout.decode() + ":"
    if compatibility is None or profile not in compatibility:
        raise ValueError("Log does not contain the matching ShaderSeed compatibility profile")
    title = compatibility.split(":", 2)[1]
    if cache.name != title or output.name != title:
        raise ValueError(f"Cache and output directories must be named {title}")
    files = []
    available = set()
    for path in sorted(cache.glob("*.bin")):
        if path.name == "pipelines.bin":
            continue
        with path.open("rb") as stream:
            if stream.read(len(translation)) == translation:
                files.append(path)
                key, _ = read_key(path.read_bytes(), len(translation) + 8)
                available.add(key)
    if not files:
        raise ValueError("No matching shader translations")
    if missing := required - available:
        raise ValueError(f"Missing {len(missing)} shader sources referenced by recipes")
    # A seed's recipes and permutation files must stay together. Never merge into another seed.
    output.mkdir(parents=True, exist_ok=False)
    manifest = {"compatibility": compatibility, "recipes": count, "shaders": len(files), "files": {}}
    for path in files + [cache / "pipelines.bin"]:
        data = path.read_bytes()
        (output / path.name).write_bytes(data)
        manifest["files"][path.name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    # Publish the compatibility marker last; an incomplete export is never installed.
    (output / "compatibility.txt").write_text(compatibility + "\n", encoding="utf-8")
    print(f"Exported {len(files)} shaders, {count} recipes to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    export_seed(args.cache, args.log, args.output)

"""Append-only session99 archive. Default: read-only dry run; never stages/commits.

Run only outside GPU holds. --apply requires the parent's final GO and --final-docs.
The first 210 names come from the explicit preparation inventory; refresh their bytes.
Only named continuation directories and explicitly named run tags may add files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath

ROOT = Path('C:/kyty/s99')
ARCHIVE = Path('C:/kyty/KytyPS5/docs/session-99')
CANONICAL = ARCHIVE / 'canonical-sha256.json'
BASE_LIST = ROOT / 'archive99_pending-small-sha256.json'
MAX_SMALL = 500_000
TAGS = ('eng99a1', 'eng99a2', 'eng99a3', 'life99a', 'eng99a4', 'bf99e',
        'vis99base', 'aa99plain', 'bf99g', 'eng99c1', 'eng99c2', 'bf99h')
FRESH_DIRS = ('settled_runs', 'verify99_confirm_raw', 'verify99_c_raw',
              'verify99_visual_raw')
SUFFIXES = {'.py', '.md', '.txt', '.json', '.csv'}
BINARIES = ('kyty_emulator_before_run99.exe', 'kyty_emulator_s99.exe',
            'kyty_emulator_s99_cpu.exe', 'kyty_emulator_s99_gc.exe')
VIDEOS = ('rec_bf99e.mp4', 'rec_bf99e.mp4.idx',
          'rec_vis99base.mp4', 'rec_vis99base.mp4.idx')


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf8')


def stable_hash(path):
    before = path.stat()
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError(f'File changed while hashing: {path}')
    return {'bytes': before.st_size, 'sha256': digest.hexdigest()}


def safe_name(name):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or ':' in name or '\\' in name:
        raise ValueError(f'Unsafe relative file name: {name}')
    return path.as_posix()


def exclusive_or_equal(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise RuntimeError(f'Refusing to overwrite different archived bytes: {path}')
        return
    with path.open('xb') as target:
        target.write(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Write only after explicit root GO')
    parser.add_argument('--final-docs', action='store_true', help='Root finished FACTS/README')
    parser.add_argument('--hash-raw', action='store_true', help='Recompute large hashes during dry run')
    parser.add_argument('--extra', action='append', default=[], help='Explicit extra smallfile relative to s99')
    args = parser.parse_args()
    if args.apply and not args.final_docs:
        parser.error('--apply requires --final-docs after root finalizes narrative documents')

    old_bytes = CANONICAL.read_bytes()
    old = json.loads(old_bytes)
    old_base = {name: entry for name, entry in old.items() if not name.startswith('continuation/')}
    if len(old_base) != 33:
        raise RuntimeError(f'Expected33 original canonical entries, got{len(old_base)}')
    for name, entry in old.items():
        actual = stable_hash(ARCHIVE / safe_name(name))
        if actual != entry:
            raise RuntimeError(f'Existing canonical mismatch: {name}: {actual} != {entry}')

    baseline = json.loads(BASE_LIST.read_bytes())
    if len(baseline) != 210:
        raise RuntimeError('Explicit preparation inventory changed; inspect before continuing')
    names = set(baseline)
    names.update(('archive_cont99.py', 'parent_recount99.py', 'FACTS_cal99a.md'))
    for directory in FRESH_DIRS:
        folder = ROOT / directory
        if folder.exists():
            for path in folder.rglob('*'):
                if path.is_file() and '__pycache__' not in path.parts and path.suffix in SUFFIXES:
                    if path.stat().st_size <= MAX_SMALL:
                        names.add(path.relative_to(ROOT).as_posix())
    for tag in TAGS:
        for name in (f'{tag}.json', f'stdout_{tag}.txt', f'cpuclk_{tag}.csv', f'gpuclk_{tag}.csv'):
            if not (ROOT / name).is_file():
                raise RuntimeError(f'Missing expected run artifact: {name}')
            names.add(name)
    if args.final_docs:
        names.update(('FACTS.md', 'README.md'))
    names.update(safe_name(name) for name in args.extra)
    small = {}
    payloads = {}
    for name in sorted(names):
        safe_name(name)
        source = ROOT / name
        if source.suffix not in SUFFIXES or source.stat().st_size > MAX_SMALL:
            raise RuntimeError(f'Not a permitted smallfile: {source}')
        data = source.read_bytes()
        entry = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
        small[name] = entry
        destination = ARCHIVE / 'continuation' / name
        if destination.exists() and destination.read_bytes() != data:
            raise RuntimeError(f'Existing continuation file differs: {name}')
        payloads[name] = data

    # These expected outputs must exist before a final archive; dry run reports them pending.
    required = ('settled_runs/bf99h_score.json', 'settled_runs/bf99h_parent_recount.json')
    pending = [name for name in required if not (ROOT / name).is_file()]
    review_dir = ROOT / 'verify99_c_raw'
    if not review_dir.is_dir() or not list(review_dir.glob('*.md')):
        pending.append('verify99_c_raw/<final report>.md')
    if args.apply and pending:
        raise RuntimeError(f'Final evidence still pending: {pending}')

    raw_names = set(BINARIES + VIDEOS)
    for tag in TAGS:
        raw_names.add(f'log_{tag}.txt')
        if (ROOT / f'{tag}.map').is_file():
            raw_names.add(f'{tag}.map')
    raw_names.add('r6_raw/analysis.json')
    # Preserve every additional raw tag referenced by the explicit continuation launch records.
    # If an entry retry appears, root supplies its files explicitly after reviewing provenance.
    raw = {}
    recompute = args.apply or args.hash_raw
    for name in sorted(raw_names):
        source = ROOT / name
        if not source.is_file():
            raise RuntimeError(f'Missing expected local raw asset: {source}')
        entry = stable_hash(source) if recompute else {'bytes': source.stat().st_size}
        entry.update(location=source.as_posix(), not_in_git=True)
        raw[name] = entry

    original_changed = [name for name in baseline if baseline[name] != small[name]]
    summary = {'mode': 'APPLY' if args.apply else 'DRY_RUN', 'old_canonical_entries': len(old_base),
               'small_files': len(small), 'small_bytes': sum(e['bytes'] for e in small.values()),
               'raw_local_files': len(raw), 'raw_local_bytes': sum(e['bytes'] for e in raw.values()),
               'raw_sha256_recomputed': recompute, 'pending': pending,
               'changed_since_preparation': original_changed,
               'new_canonical_entries': len(small) + 2,
               'final_canonical_entries': len(old_base) + len(small) + 2}
    if not args.apply:
        print(json.dumps(summary, indent=2))
        return

    raw_manifest = encoded({'schema': 's99-local-raw-sha256-v1', 'artifacts': raw})
    small_manifest = encoded({'schema': 's99-continuation-small-sha256-v1', 'artifacts': small})
    payloads['raw-sha256.json'] = raw_manifest
    payloads['small-sha256.json'] = small_manifest
    updated = dict(old)
    for name, data in payloads.items():
        key = 'continuation/' + name
        entry = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
        if key in updated and updated[key] != entry:
            raise RuntimeError(f'Cannot change an existing canonical entry: {key}')
        updated[key] = entry
    if any(updated[name] != entry for name, entry in old_base.items()):
        raise RuntimeError('Original canonical values changed')
    # Fully preflight destinations and current source bytes before any archive write.
    for name, data in payloads.items():
        destination = ARCHIVE / 'continuation' / name
        if destination.exists() and destination.read_bytes() != data:
            raise RuntimeError(f'Refusing destination overwrite: {destination}')
        if name in small and (ROOT / name).read_bytes() != data:
            raise RuntimeError(f'Source changed since snapshot: {name}')
    if CANONICAL.read_bytes() != old_bytes:
        raise RuntimeError('Canonical was concurrently changed')
    for name, data in sorted(payloads.items()):
        exclusive_or_equal(ARCHIVE / 'continuation' / name, data)
    new_bytes = encoded(updated)
    if new_bytes != old_bytes:
        temporary = CANONICAL.with_name('canonical-sha256.cont99.tmp')
        with temporary.open('xb') as target:
            target.write(new_bytes)
        if CANONICAL.read_bytes() != old_bytes:
            raise RuntimeError('Canonical changed before atomic replacement; temp retained')
        os.replace(temporary, CANONICAL)
    for name, entry in updated.items():
        if stable_hash(ARCHIVE / name) != entry:
            raise RuntimeError(f'Post-copy canonical mismatch: {name}')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()

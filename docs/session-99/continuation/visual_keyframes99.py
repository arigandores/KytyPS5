"""Extract fixed wall-time frames, with recording index provenance, for visual review."""
import json
from pathlib import Path
import subprocess

root = Path('C:/kyty/s99')
out = root / 'video99_comparison'
out.mkdir(exist_ok=True)
manifest = []
for tag in ('bf99e', 'vis99base'):
    video = root / f'rec_{tag}.mp4'
    rows = [tuple(map(float, line.split())) for line in Path(str(video) + '.idx').read_text().splitlines()]
    selected = [min(rows, key=lambda r: abs(r[2] - target)) for target in (50, 250, 450, 825, 900)]
    indices = [int(row[0]) for row in selected]
    expression = '+'.join(f'eq(n\\,{n})' for n in indices)
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(video), '-vf', f'select={expression}',
                    '-fps_mode', 'vfr', '-frames:v', str(len(indices)),
                    str(out / f'{tag}_%02d.png')], check=True)
    for number, row in enumerate(selected, 1):
        manifest.append(dict(tag=tag, image=f'{tag}_{number:02d}.png', frame=int(row[0]),
                             present=int(row[1]), wall_seconds=row[2]))
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
print(json.dumps(manifest, indent=2))

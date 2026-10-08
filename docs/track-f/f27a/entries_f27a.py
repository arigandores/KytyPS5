"""F27a (HPP-690): per-entry summary of Day and Night logs - hold frames, long frames, driver cache saves,
translations and deferred draws on the hold.  Offline, read-only.
Usage: python entries.py <out.json> tag=path=stable_frame ...
"""
import json
import re
import sys

FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
TS = re.compile(rb'^\[(\d+)\]\[(\d\d):(\d\d):(\d\d)\.(\d{3})\]')


def summarize(path, stable):
    frames = []          # (n, dt, line)
    saves = []           # (line, last_n, text)
    trans_hold = 0
    trans_all = 0
    skipped_hold = 0
    held_hold = 0
    started = None
    last_n = None
    last_ts = None
    level_ts = None
    with open(path, 'rb') as f:
        for i, l in enumerate(f):
            m = FT.match(l)
            if m:
                last_n = int(m.group(1))
                frames.append((last_n, int(m.group(2)), i + 1))
                continue
            t = TS.match(l)
            if t:
                h, mi, s, ms = (int(x) for x in t.groups()[1:])
                last_ts = h * 3600 + mi * 60 + s + ms / 1000
                continue
            if b'Level has started: rotating_level_day_and_night' in l:
                started = (i + 1, last_n)
                level_ts = last_ts
            elif b'pipeline cache: saved' in l or l.startswith(b'PipelinePrecache: saved'):
                saves.append((i + 1, last_n, l[:160].decode('utf-8', 'replace').rstrip()))
            elif b'SPIR-V words=' in l:
                trans_all += 1
                if last_n is not None and last_n >= stable:
                    trans_hold += 1
            elif b'skipped draw' in l:
                if last_n is not None and last_n >= stable:
                    skipped_hold += 1
            elif b'held (incomplete frame)' in l:
                if last_n is not None and last_n >= stable:
                    held_hold += 1
    hold = [x for x in frames if x[0] > stable]
    hold_us = sum(x[1] for x in hold)
    long_hold = [x for x in hold if x[1] >= 100000]
    top = sorted(hold, key=lambda x: -x[1])[:3]
    save_frames = []
    for line, n, text in saves:
        if n is None:
            continue
        # the save line sits in the interval of frame n + 1
        nxt = [x for x in frames if x[0] == n + 1]
        save_frames.append({'line': line, 'interval_of_n': n + 1,
                            'dt_us': nxt[0][1] if nxt else None, 'on_hold': n + 1 > stable, 'text': text})
    return {
        'path': path, 'stable_frame': stable, 'frames': len(frames), 'level_started': started,
        'hold_frames': len(hold), 'hold_s': round(hold_us / 1e6, 1),
        'hold_ge_100ms': long_hold, 'hold_top3': top,
        'translations_all': trans_all, 'translations_hold': trans_hold,
        'skipped_draw_hold': skipped_hold, 'held_flip_hold': held_hold,
        'saves': save_frames,
    }


def main():
    out = {}
    for arg in sys.argv[2:]:
        tag, path, stable = arg.split('=')
        out[tag] = summarize(path, int(stable))
        r = out[tag]
        print(tag, 'hold', r['hold_frames'], 'frames', r['hold_s'], 's; >=100ms on hold', r['hold_ge_100ms'],
              'top3', r['hold_top3'], 'transl hold/all', r['translations_hold'], r['translations_all'],
              'skipped hold', r['skipped_draw_hold'], 'held flips hold', r['held_flip_hold'])
        for s in r['saves']:
            print('   save', s)
    with open(sys.argv[1], 'w', encoding='utf-8') as o:
        json.dump(out, o, indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()

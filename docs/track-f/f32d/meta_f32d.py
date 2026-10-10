# F32d (HPP-742): run form of every log of frames_f32d.json - the tag json of the harness (env, cmdline), found next to the log
# (<dir>/<tag>.json, <dir>/runs*/<tag>.json, <dir>/*/<tag>.json for log_<tag>.txt; <dir>/*.json for <dir>/log.txt), and the
# run notes of the user recording (times.txt).  Read-only.  Usage: python meta_f32d.py <frames_f32d.json> <out.json>
import os, sys, json, glob
BS = chr(92)
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
if os.path.exists('C:/kyty/f287/STOP'):
    sys.exit(4)


def tagjson(p):
    dd = os.path.dirname(p)
    b = os.path.basename(p)
    c = []
    if b.startswith('log_'):
        t = b[4:-4]
        c += [dd + '/' + t + '.json'] + glob.glob(dd + '/runs*/' + t + '.json') + glob.glob(dd + '/*/' + t + '.json')
    else:
        t = os.path.basename(dd)
        c += sorted(glob.glob(dd + '/*.json')) + [os.path.dirname(dd) + '/' + t + '.json']
    return [x.replace(BS, '/') for x in c if os.path.exists(x)]


def main():
    d = json.load(open(sys.argv[1], encoding='utf-8'))
    out = {}
    for p in sorted(d['heads']):
        rec = {'json': None, 'env': None, 'cmdline': None, 'times': None}
        for j in tagjson(p):
            try:
                o = json.load(open(j, encoding='utf-8'))
            except Exception:
                continue
            if isinstance(o, dict) and 'env' in o:
                rec['json'] = j
                rec['env'] = o['env']
                rec['cmdline'] = o.get('cmdline')
                break
        tp = os.path.dirname(p) + '/times.txt'
        if rec['json'] is None and os.path.exists(tp) and os.path.getsize(tp) < 65536:
            rec['times'] = open(tp, encoding='utf-8', errors='replace').read()
        out[p] = rec
    json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('logs', len(out), 'with tag json', sum(1 for r in out.values() if r['json']), 'with times.txt only',
          sum(1 for r in out.values() if r['times']))


if __name__ == '__main__':
    main()

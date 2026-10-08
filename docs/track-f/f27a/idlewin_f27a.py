"""F27a (HPP-690): GPU idle windows (hostdev122 rule: util <= 15 % for >= 3 s inside the busy span) of every Day and
Night entry, placed against the harness times of the run (launched + document/started/stable seconds).  Offline."""
import datetime
import importlib.util
import json
import sys

spec = importlib.util.spec_from_file_location('hd', 'C:/kyty/s122/hostdev122.py')
hd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hd)

RUNS = [
    ('ednn122', 'C:/kyty/s122/ednn122.json', 'C:/kyty/s122/gpuclk_ednn122.csv'),
    ('dnn122', 'C:/kyty/s122/dnn122.json', 'C:/kyty/s122/gpuclk_dnn122.csv'),
    ('s13_k_09', 'C:/kyty/s288/s13/k_09.json', 'C:/kyty/s288/s13/gpuclk_k_09.csv'),
    ('s13_u_09', 'C:/kyty/s288/s13/u_09.json', 'C:/kyty/s288/s13/gpuclk_u_09.csv'),
    ('s15_k_09', 'C:/kyty/s288/s15/k_09.json', 'C:/kyty/s288/s15/gpuclk_k_09.csv'),
    ('s15_u_09', 'C:/kyty/s288/s15/u_09.json', 'C:/kyty/s288/s15/gpuclk_u_09.csv'),
    ('s18_c09', 'C:/kyty/s288/s18c/s18_c09.json', 'C:/kyty/s288/s18c/gpuclk_s18_c09.csv'),
]

out = {}
for tag, jp, cp in RUNS:
    j = json.load(open(jp))
    launched = datetime.datetime.fromisoformat(j['launched'])
    a = [x for x in j.get('attempts', []) if x.get('outcome') == 'ok'][-1]
    s = hd.read_gpu_csv(cp)
    busy = hd.trim_to_busy(s)
    wins = hd.idle_windows(busy)
    rows = []
    for w0, w1, dur in wins:
        # launched carries whole seconds only: offsets are given as an interval [x - 1, x]
        o0 = (w0 - launched).total_seconds()
        o1 = (w1 - launched).total_seconds()
        rows.append({'from': w0.isoformat(), 'to': w1.isoformat(), 'dur_s': round(dur, 3),
                     'offset_s': [round(o0 - 1, 3), round(o1, 3)],
                     'ends_before_stable': o1 < a['stable_s'],
                     'starts_after_stable': (o0 - 1) > a['stable_s']})
    low = [(t.isoformat(), u) for t, u in busy if u <= 15]
    out[tag] = {'launched': j['launched'], 'document_s': a.get('document_s'), 'started_s': a.get('started_s'),
                'stable_s': a.get('stable_s'), 'samples': len(s), 'busy': len(busy), 'idle_windows': rows,
                'low_samples_in_busy': low[:20], 'low_count': len(low)}
    print(tag, 'launched', j['launched'], 'doc/start/stable', a.get('document_s'), a.get('started_s'), a.get('stable_s'),
          'samples', len(s), 'busy', len(busy), 'idle windows', rows, 'low samples', len(low), low[:6])
json.dump(out, open(sys.argv[1], 'w'), indent=1)

# F36a (HPP-758): RD_EV list for one snapshot from runs/inv_k<NN>.json (all events of the inventory); usage: mkev_f36a.py <NN> [exec_no,...]
import json, sys
d = json.load(open('C:/kyty/f287/f36a/runs/inv_k%s.json' % sys.argv[1]))
only = set(int(x) for x in sys.argv[2].split(',')) if len(sys.argv) > 2 else None
ev = [{'eid': e['eid'], 'exec_no': e['exec_no'], 'PSInvocations': e['counters']['PSInvocations'], 'SamplesPassed': e['counters']['SamplesPassed']}
      for e in d['events'] if only is None or e['exec_no'] in only]
print(json.dumps(ev))

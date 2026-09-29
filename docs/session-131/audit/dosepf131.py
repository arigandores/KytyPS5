# row "dose per frame of arm 1" and slope: which row set gives FACTS 9.4 (2 387,7 us/frame, slope 0,834)
import sys
sys.argv = ['x']
exec(open('C:/kyty/s131/audit131/recount131.py', encoding='utf-8').read().split("if __name__ == '__main__':")[0])
L = read_log(ROOT + 'log_dd131.txt')
B = blocks_of(L)
a1 = [b for b in B if b['arm'] == 1]
win = [b['pos'][p] for b in a1 if b['complete'] for p in range(10, 89)]
allr = [r for b in a1 for r in b['pos'].values()]
print('window rows', len(win), 'dose us/frame', sum(g(r, 'dc_dose_ns') for r in win) / len(win) / 1000)
print('all rows of arm-1 blocks', len(allr), 'dose us/frame', sum(g(r, 'dc_dose_ns') for r in allr) / len(allr) / 1000)
print('window mh_disp_us/frame arm1', sum(g(r, 'mh_disp_us') for r in win) / len(win))
print('window dc_tgt_ns/frame', sum(g(r, 'dc_tgt_ns') for r in win) / len(win) / 1000 if 'dc_tgt_ns' in NEED else 'n/a')
paired = [b for b in a1 if b['complete'] and b['i'] < 82]
pw = [b['pos'][p] for b in paired for p in range(10, 89)]
print('paired arm-1 blocks', len(paired), 'rows', len(pw), 'dose us/frame', sum(g(r, 'dc_dose_ns') for r in pw) / len(pw) / 1000,
      'slope', 1990.8184624884225 / (sum(g(r, 'dc_dose_ns') for r in pw) / len(pw) / 1000))

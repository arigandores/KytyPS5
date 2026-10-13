"""Track M, M8a (HPP-858, ROADMAP s122 item 778(g)(2)(i), (iii)): driver of the T125 stand m_t125_stand.
Runs the stand twice - KYTY_M_T125=0 and =1 - each into its own out dir, then checks:
  per run: exit code 0, "STAND DONE mode=<m> fail=0", >= 1 MEMBER line and every MEMBER OK, exactly one "MT125: mode=<m>";
  =0: no "MT125Stat:" line;  =1: exactly one "MT125Stat: when=exit mixed=<a> mixed_nz=<b>" equal to the EXPECT line, a > 0;
  across runs: the 16 bus outputs bus_A<k>_<i>.bin of =1 equal to those of =0 byte for byte; mix_A<k>.bin only at =1.
Usage: python run_stand_m8a.py <stand exe> <out base dir>   Last line: ALL OK or FAIL. Lock and STOP are checked first."""
import os
import re
import subprocess
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/m657/STOP'):
    print('LOCK or STOP')
    sys.exit(3)

EXE = sys.argv[1]
BASE = sys.argv[2]
ok = True


def member(name, cond, detail=''):
    global ok
    print('DRIVER %s %s %s' % (name, 'OK' if cond else 'FAIL', detail))
    ok &= bool(cond)


runs = {}
for mode in ('0', '1'):
    out_dir = os.path.join(BASE, 'm' + mode)
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, f))
    env = dict(os.environ)
    env['KYTY_M_T125'] = mode
    p = subprocess.run([EXE, out_dir], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
    text = p.stdout.decode('utf-8', 'replace')
    open(os.path.join(BASE, 'stand_m%s.out.txt' % mode), 'w', encoding='utf-8', newline=chr(10)).write(text)
    lines = text.splitlines()
    members = [ln for ln in lines if ln.startswith('MEMBER ')]
    bad = [ln for ln in members if len(ln.split(' ')) < 3 or ln.split(' ')[2] != 'OK']
    member('m%s_exit0' % mode, p.returncode == 0, 'rc=%d' % p.returncode)
    member('m%s_done' % mode, ('STAND DONE mode=%s fail=0' % mode) in lines)
    member('m%s_members' % mode, len(members) > 0 and not bad, 'members=%d fail=%d %s' % (len(members), len(bad),
                                                                                          (bad[0] if bad else '')))
    mode_lines = [ln for ln in lines if ln.startswith('MT125: mode=')]
    member('m%s_mode_line' % mode, mode_lines == ['MT125: mode=%s' % mode], repr(mode_lines))
    stat = [ln for ln in lines if ln.startswith('MT125Stat:')]
    exp = [ln for ln in lines if ln.startswith('EXPECT ')]
    if mode == '0':
        member('m0_no_stat_line', stat == [], repr(stat))
    else:
        m = re.fullmatch(r'EXPECT mixed=(\d+) mixed_nz=(\d+)', exp[0]) if len(exp) == 1 else None
        want = 'MT125Stat: when=exit mixed=%s mixed_nz=%s' % (m.group(1), m.group(2)) if m else None
        member('m1_stat_line', m is not None and int(m.group(1)) > 0 and stat == [want], 'stat=%r want=%r' % (stat, want))
    runs[mode] = out_dir

same = 0
for k in range(4):
    for i in range(4):
        name = 'bus_A%d_%d.bin' % (k, i)
        a = os.path.join(runs['0'], name)
        b = os.path.join(runs['1'], name)
        if os.path.exists(a) and os.path.exists(b) and open(a, 'rb').read() == open(b, 'rb').read() and \
                os.path.getsize(a) == 512 * 8:
            same += 1
member('bus_byte_for_byte', same == 16, 'equal=%d of 16' % same)
mix0 = [f for f in os.listdir(runs['0']) if f.startswith('mix_')]
mix1 = [f for f in os.listdir(runs['1']) if f.startswith('mix_')]
member('mix_only_at_1', mix0 == [] and len(mix1) == 4, 'm0=%d m1=%d' % (len(mix0), len(mix1)))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)

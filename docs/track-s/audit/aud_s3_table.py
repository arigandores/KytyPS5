# S11a (HPP-493): the table "field - scorer - auditor".  Scorer values are parsed from s10/fin_summary.txt and
# s10/table_s10.md (text only, no scorer code); auditor values from rec_<tag>.json / haze_<tag>.json of aud_s3.py.
import json, re, sys, os, hashlib
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCKED'); sys.exit(5)
A = 'C:/kyty/s288/s11a'
S = open('C:/kyty/s288/s10/fin_summary.txt', encoding='ascii').read().split('\n')
T = open('C:/kyty/s288/s10/table_s10.md', encoding='ascii').read().split('\n')
R = lambda t: json.load(open('%s/rec_%s.json' % (A, t)))
H = lambda t: json.load(open('%s/haze_%s.json' % (A, t)))
rows = []
ok = True


def add(field, sc, au):
    global ok
    eq = sc == au
    ok &= eq
    rows.append('| %s | %s | %s | %s |' % (field, sc, au, '=' if eq else 'DIFFERS'))


def line(prefix):
    return [l for l in S if l.startswith(prefix)][0]


# table_s10: sha prefix, first scene frame, video frames
for l in T[2:]:
    c = [x.strip() for x in l.split('|')]
    if len(c) < 9:
        continue
    tag = c[1].strip('`')
    r = R(tag)
    add('%s log sha256 (16)' % tag, c[8].strip('`'), r['sha256'][:16])
    m = re.match(r'(\d+) \(dt (\d+) us\)', c[6])
    add('%s first scene frame n / dt' % tag, (int(m.group(1)), int(m.group(2))), tuple(r['first']))
    add('%s death markers / [Vulkan][E] / GamePatch' % tag, (0, 0, 0), (r['death'], r['vke'], r['gamepatch']))
# repeat of integrity
for t in ('pi_w1', 'pi_r1', 'pi_w0', 'pi_r0'):
    l = line(t + ':')
    h = H(t)
    m = re.search(r'video frames (\d+), present rows (\d+).*haze frames (\d+) median ([\d.]+) low (\d+) series (\[.*?\]\]|\[\]); after frame 1002 \(letter: start > 1002\) (\[.*?\]\]|\[\]); variant \(any frame > 1002\) (\[.*?\]\]|\[\])', l)
    add('%s present rows' % t, int(m.group(2)), R(t)['rows'])
    add('%s detector frames / median / low' % t, (int(m.group(3)), float(m.group(4)), int(m.group(5))), (h['frames'], h['med'], h['low']))
    add('%s series' % t, json.loads(m.group(6)), h['series'])
    add('%s series start > 1002 (letter)' % t, json.loads(m.group(7)), h['letter'])
    add('%s series any frame > 1002 (variant)' % t, json.loads(m.group(8)), h['variant'])
for rt, wt in (('pi_r1', 'pi_w1'), ('pi_r0', 'pi_w0')):
    m = re.search(r'loaded (\d+) bytes = last write of \w+ (\d+), disabled (\d+) -> (\w+)', line(rt + ' loaded'))
    r, w = R(rt), R(wt)
    add('%s loaded / last saved of %s / disabled' % (rt, wt), (int(m.group(1)), int(m.group(2)), int(m.group(3))),
        (r['loaded'][0] if len(r['loaded']) == 1 else r['loaded'], w['last_saved'], r['disabled']))
    add('%s saved lines (lead item 408 (b): 24)' % wt, 24, w['saves'])
    add('%s presented >= 300 s after the first scene frame' % wt, True, w['dt_after_first_us'] >= 300000000)
add('pi_r1 "AvTrace: pcw overlap wait" lines', 0, R('pi_r1')['pcw_wait'])
hz = dict((t, bool(H(t)['letter'])) for t in ('pi_w1', 'pi_r1', 'pi_w0', 'pi_r0'))
hv = dict((t, bool(H(t)['variant'])) for t in ('pi_w1', 'pi_r1', 'pi_w0', 'pi_r0'))
ld = all(R(rt)['loaded'] == [R(wt)['last_saved']] and R(rt)['disabled'] == 0 for rt, wt in (('pi_r1', 'pi_w1'), ('pi_r0', 'pi_w0')))


def word(h):
    if h['pi_r1'] and not h['pi_r0']:
        return 'READ_1'
    if h['pi_r1'] and h['pi_r0']:
        return 'READ_2' if ld else 'READ_OTHER'
    if h['pi_r0'] or h['pi_w1'] or h['pi_w0']:
        return 'READ_3' if ld else 'READ_OTHER'
    return 'READ_2' if ld else 'READ_OTHER'


add('repeat of integrity, the letter', re.search(r'repeat of integrity \(item 355 \(g\)\): (\w+)', '\n'.join(S)).group(1), word(hz))
add('repeat of integrity, the variant', re.search(r'reading \(variant: a series with any frame after 1002\): (\w+)', '\n'.join(S)).group(1), word(hv))
# C5
m = re.search(r'creations .* (\d+), median us ([\d.]+); lines without a us field (\d+)', line('c5_0 ('))
c = R('c5_0')
add('c5_0 in-game creations / median us / lines without us', (int(m.group(1)), float(m.group(2)), int(m.group(3))), (c['create_n'], float(c['create_med']), c['create_nous']))
add('C5 word (>= 10 creations and median >= 20000 us)', 'NO' if 'neutralises (>= 10 creations, median >= 20000 us): NO' in '\n'.join(S) else 'YES',
    'YES' if c['create_n'] >= 10 and c['create_med'] >= 20000 else 'NO')
add('c5_0 T-1 / T-6 on the domain (item 404)', ((4183, 4183), (150, 150)), (tuple(c['t1_dom']), tuple(c['t6_dom'])))
add('c5_0 T-1 / T-6 whole log (item 404)', ((4251, 4271), (171, 170)), (tuple(c['t1_whole']), tuple(c['t6_whole'])))
# T2
counted = 0
ev_s = []
for t in ('t2_1', 't2_2', 't2_3', 't2_4', 't2_5', 't2_6', 't2_7'):
    l = line(t + ' ')
    r = R(t)
    m = re.search(r': (COUNTED|OUT); arm (\w+); gate \(item 362 \(b\)\) ([\w ]+), by the letter.*creations after the entry (\d+); skip rows (\d+) held (\d+) presented >= 100 ms (\d+); attributed >= 100 ms (\d+) \(PCW (\d+)\), >= 1 s (\d+); not attributed (\d+)', l)
    g = r['gate']
    cold = g['cold_letter']
    counted += cold
    add('%s gate' % t, m.group(3), 'cold' if cold else 'level not cold')
    add('%s counted' % t, m.group(1), 'COUNTED' if cold else 'OUT')
    add('%s creations after the entry' % t, int(m.group(4)), g['create_after'])
    add('%s skip rows / held flips / presented >= 100 ms' % t, (int(m.group(5)), int(m.group(6)), int(m.group(7))), (r['skip_rows'], r['held'], r['presented100']))
    add('%s attributed >= 100 ms / PCW / >= 1 s / not attributed' % t, (int(m.group(8)), int(m.group(9)), int(m.group(10)), int(m.group(11))),
        (r['att100'], r['att_pcw100'], r['att1s'], r['unatt100']['n']))
    b = re.search(r'BvhLoopCapTrip in i-1\.\.i of frames >= 100 ms (\[.*?\]);', l).group(1)
    add('%s BvhLoopCapTrip column' % t, b.replace('(', '[').replace(')', ']').replace(' ', ''), json.dumps([[x['n'], x['bvh']] for x in r['long']]).replace(' ', ''))
    if cold:
        for e in r.get('early', []):
            ev_s.append((t, e['kind'], e['n'], e['lead'], e['cost'], e['cost_prep']))
add('T2 counted', int(re.search(r'T2 counted (\d+) of', '\n'.join(S)).group(1)), counted)
sc_ev = [(m.group(1), m.group(2), int(m.group(3)), int(m.group(4)), int(m.group(5)), int(m.group(6))) for m in
         (re.match(r'  S-early (\w+) (\w+) n (\d+) lead (\d+) cost (\d+) \(PREP-only (\d+)\)', l) for l in S) if m]
add('S-early events (tag, kind, n, lead, cost, PREP-only), %d' % len(sc_ev), sc_ev, ev_s)
m = re.search(r'lead < cost in (\d+) of (\d+) events', '\n'.join(S))
add('S-early lead < cost', (int(m.group(1)), int(m.group(2))), (sum(1 for e in ev_s if e[3] < e[4]), len(ev_s)))
m = re.search(r'skip rows [+-]\d+ \((\d+) / (\d+)\), held flips [+-]\d+ \((\d+) / (\d+)\), presented frames >= 100 ms [+-]\d+ \((\d+) / (\d+)\); CsPretranslate lines t2_1 (\[.*?\]), t2_cs0 (\[.*?\])', line('t2_cs0'))
a, b = R('t2_1'), R('t2_cs0')
add('t2_cs0 / t2_1 skip rows, held flips, presented >= 100 ms', tuple(int(m.group(i)) for i in range(1, 7)),
    (b['skip_rows'], a['skip_rows'], b['held'], a['held'], b['presented100'], a['presented100']))
add('CsPretranslate lines t2_1 / t2_cs0', (m.group(7), m.group(8)), (str(sorted(a['csp'].items())), str(sorted(b['csp'].items()))))
# U
fails = 0
for t in ('u_1', 'u_2', 'u_3', 'u_4', 'u_5'):
    l = line(t + ' ')
    r = R(t)
    m = re.search(r': (gates ok|CATALOGUE[^;]*); S-cat member (\w+); stdout Shaders: (\d+), rec_new_after (\d+), perm_after (\d+), skip lines after the first scene frame (\d+); preparation screen ([\d.]+) s \(PipelinePrecache: all pipelines created ([\d.]+) s, ShaderPreparation: ready ([\d.]+) s; progress lines (\d+), max elapsed_ms (\d+); attempt \w+; log created (\d+) ms, startup wait (\d+) ms\).*attributed >= 100 ms (\d+)', l)
    gates = r['seed_installed'] >= 1 and r['prepare_cold'] >= 1
    f = r['skips_group_after_fi'] > 0 or r['att100'] > 0
    fails += f
    add('%s gates (ShaderSeed: installed, prepare-cold)' % t, m.group(1), 'gates ok' if gates else 'CATALOGUE NOT INSTALLED')
    add('%s S-cat member' % t, m.group(2), 'FAILS' if f else 'holds')
    add('%s stdout Shaders / rec_new_after / perm_after / skip lines after the first scene frame / attributed >= 100 ms' % t,
        tuple(int(m.group(i)) for i in (3, 4, 5, 6, 14)), (r['stdout_shaders'], r['gate']['rec_new_after'], r['gate']['perm_after'], r['skips_group_after_fi'], r['att100']))
    add('%s skipped-draw lines in the whole log' % t, 0, r['skip_lines'])
    add('%s screen s (json of the attempt: later of created / ready)' % t, float(m.group(7)), max(r['prep_created_s'], r['prep_ready_s']))
    add('%s log: created ms / startup wait ms / progress lines / max elapsed_ms' % t, tuple(int(m.group(i)) for i in (12, 13, 10, 11)),
        (r['created_ms'], r['waited_ms'], r['prog_n'], r['prog_max']))
sw = re.search(r'-> (\w+)$', line('S-cat (item 229')).group(1)
add('S-cat word', sw, 'KILLED' if fails >= 2 or any(max(R(t)['prep_created_s'], R(t)['prep_ready_s']) > 180 for t in ('u_1', 'u_2', 'u_3', 'u_4', 'u_5')) else 'ALIVE_BY_PROBE_5')
# the blob fact of item 408 (b)
sh = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
b0 = sh('C:/kyty/s288/snap0/PipelineCache/PPSA21564.bin')
add('blob sha256 after pi_w1 = snap0 (lead item 408 (b): cc5b747c5bece91e)', 'cc5b747c5bece91e', sh('C:/kyty/s288/s10/app_post/pi_w1/PipelineCache/PPSA21564.bin')[:16])
add('blob sha256 after pi_w0 = snap0', b0[:16], sh('C:/kyty/s288/s10/app_post/pi_w0/PipelineCache/PPSA21564.bin')[:16])
add('snap0 blob sha256', 'cc5b747c5bece91e', b0[:16])
out = ['| field | scorer (fin_summary.txt 31b51c62, table_s10.md 901abad0; lead item 408) | auditor (aud_s3.py) | |', '|---|---|---|---|'] + rows
out.append('')
out.append('fields %d, DIFFERS %d' % (len(rows), sum(1 for x in rows if x.endswith('DIFFERS |'))))
out.append('RECOUNT: %s' % ('CONFIRMED' if ok else 'DIVERGES'))
open(A + '/aud_s3_table.md', 'w', encoding='ascii', newline='\n').write('\n'.join(out) + '\n')
print('\n'.join(out[-2:]))
for x in rows:
    if x.endswith('DIFFERS |'):
        print(x)

#!/usr/bin/env python3
"""report_s0.py - track S, link S0 (HPP-294): tables from out/<tag>.json of attr_s0.py.  ASCII output."""
import json
import sys

OUT = 'C:/kyty/s288/s0/out'
TAGS = ('v142', 'w142') + tuple('c142_%02d' % i for i in range(1, 11))
CENSUS = TAGS[2:]


def ms(us):
    return '%.1f' % (us / 1000.0)


def main():
    D = {t: json.load(open('%s/%s.json' % (OUT, t))) for t in TAGS}
    print('== T1. skipped-draw rows, held flips, frames >= 100 ms (after the first scene frame)')
    print('tag first_n first_dt first_held | win: skiprows held k3 k2 dtmax | hold: skiprows held k3 k2 dtmax | '
          'post: skip_draws skip_lines pairs held_lines | score_skip_frames | load(before+first): skiprows held')
    S = dict(skip=0, held=0, k3w=0, k3h=0, sf=0, pairs=0, heldw=0, heldh=0, skipw=0, skiph=0)
    for t in TAGS:
        d = D[t]
        w, h, p, ld, f = d['window'], d['hold'], d['post'], d['load'], d['first']
        print('%s %d %d %d | %d %d %d %d %d | %d %d %d %d %d | %d %d %d %d | %s | %d %d' % (
            t, f['n'], f['dt'], f['held'], w['skip_rows'], w['held_rows'], w['k3'], w['k2'], w['dt_max'],
            h['skip_rows'], h['held_rows'], h['k3'], h['k2'], h['dt_max'], p['skip_draws'], p['skip_lines'], p['pairs'],
            p['held_lines'], d.get('score_skip_frames'), ld['skip_rows'], ld['held_rows']))
        if t in CENSUS:
            S['skip'] += p['skip_rows']; S['held'] += p['held_rows']; S['k3w'] += w['k3']; S['k3h'] += h['k3']
            S['sf'] += d.get('score_skip_frames') or 0; S['pairs'] += p['pairs']
            S['heldw'] += w['held_rows']; S['heldh'] += h['held_rows']; S['skipw'] += w['skip_rows']; S['skiph'] += h['skip_rows']
    print('census sums: skip rows (counter) %d (window %d / hold %d), held flips %d (window %d / hold %d), k3 window %d, '
          'k3 hold %d, sc142 skip frames (frame=) %d, pairs %d' % (S['skip'], S['skipw'], S['skiph'], S['held'], S['heldw'],
                                                                 S['heldh'], S['k3w'], S['k3h'], S['sf'], S['pairs']))
    print()
    print('== T2. held runs (visible gap = sum dt of the held rows + dt of the next presented row)')
    print('tag runs gap_max_ms gap>=100ms gap>=1s gap_sum_ms | top runs n0-n1 flips gap_ms part pairs pending_max')
    tot = dict(runs=0, g100=0, g1s=0)
    lv100 = lv1s = 0
    for t in TAGS:
        d = D[t]
        top = sorted(d['held_runs'], key=lambda r: -r['gap_us'])[:4]
        print('%s %d %s %d %d %s | %s' % (t, d['held_runs_n'], ms(d['held_gap_max_us']), d['held_gap_ge100'],
                                          d['held_gap_ge1s'], ms(d['held_gap_sum_us']),
                                          '; '.join('%d-%d %d %s %s %d %d' % (r['n0'], r['n1'], r['flips'], ms(r['gap_us']),
                                                                             r['part'], r['pairs'], r['pending_max'])
                                                    for r in top)))
        if t in CENSUS:
            tot['runs'] += d['held_runs_n']; tot['g100'] += d['held_gap_ge100']; tot['g1s'] += d['held_gap_ge1s']
            lv100 += d['held_gap_ge100'] > 0; lv1s += d['held_gap_ge1s'] > 0
    print('census sums: runs %d, gap >= 100 ms %d (levels %d/10), gap >= 1 s %d (levels %d/10)' % (
        tot['runs'], tot['g100'], lv100, tot['g1s'], lv1s))
    print()
    print('== T3. form ban: rows with skipped draws that were not held (next_held = held flag of the next two rows); '
          'held rows without skip; skc_bad')
    for t in TAGS:
        d = D[t]
        print('%s skip_not_held %d %s | held_without_skip %d %s | skc_bad %d' % (
            t, len(d['skip_not_held']), [(x['n'], x['skip'], x['next_held']) for x in d['skip_not_held']][:8],
            len(d['held_without_skip']), d['held_without_skip'][:8], d['post']['skc_bad']))
    print()
    print('== T4. every frame >= 100 ms after the first scene frame')
    print('tag n dt part cls skip held pairs run_first draws cpu_gpu cpu_main semwait img_up_kb img_imp_kb img_new buf_new '
          'opens cs_ready cs_src_miss prio late saved line')
    agg = {}
    for t in TAGS:
        for r in D[t]['long'] if t != 'w142' else []:
            print('%s %d %d %s %s %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %s %s %s %d' % (
                t, r['n'], r['dt'], r['part'], r['cls'], r['skip'], r['held'], r['pairs'], int(r['run_first']), r['draws'],
                r['cpu_gpu'], r['cpu_main'], r['semwait'], r['img_up_kb'], r['img_imp_kb'], r['img_new'], r['buf_new'],
                r['opens'], r['cs_ready'], r['cs_src_miss'], r['prio'], r['late'], r['saved'], r['line']))
            if t in CENSUS:
                k = (r['part'], r['cls'])
                a = agg.setdefault(k, [0, 0])
                a[0] += 1; a[1] += r['dt']
    print('census, frames >= 100 ms by part and class: %s' % sorted((k, v) for k, v in agg.items()))
    wl = D['w142']['long']
    print('w142 (validation run): %d frames >= 100 ms, classes %s - not classified (validation)' % (
        len(wl), sorted(set(r['cls'] for r in wl))))
    print()
    print('== T5. span of a skipped VS/PS pair (first..last row that logged it): presented time, rows')
    allus = []
    for t in TAGS:
        d = D[t]
        s = d['pair_span_us']
        print('%s pairs %d span_us %s | top %s' % (t, d['pairs_n'], s, [(x['pair'][:33], x['rows'], x['us']) for x in d['pair_spans'][:3]]))
        if t in CENSUS:
            allus += [x['us'] for x in d['pair_spans']]
    allus.sort()
    if allus:
        n = len(allus)
        print('census: pairs %d, span us min %d p25 %d med %d p75 %d p95 %d max %d; <= 20 ms: %d; >= 100 ms: %d; >= 1 s: %d' % (
            n, allus[0], allus[n // 4], allus[n // 2], allus[3 * n // 4], allus[min(n - 1, int(n * 0.95))], allus[-1],
            sum(1 for u in allus if u <= 20000), sum(1 for u in allus if u >= 100000), sum(1 for u in allus if u >= 1000000)))
    print()
    print('== T6. mechanisms (header lines; line number in the log)')
    for t in TAGS:
        d = D[t]
        print('-- %s (%s) sha256 %s' % (t, d['path'], d['sha256']))
        for ln, s in d['header']:
            if s.startswith('PipelinePrecache: saved'):
                continue
            print('   %d %s' % (ln, s))
        print('   recipes saved (row n, count): %s' % d['recipes_saved'])
        c = d['cs']
        print('   CsPretranslate: ready %d (sum us %d) skipped %d enqueue_skipped %d hit %d miss %d summary %d reasons %s' % (
            c['ready'], c['ready_us'], c['skipped'], c['enqueue_skipped'], c['hit'], c['miss'], c['summary'],
            sorted(c['reasons'].items())))
        print('   CsPretranslate after the first scene frame: ready %d skipped %d; before entry: ready %d skipped %d' % (
            d['post']['cs_ready'], d['post']['cs_skipped'], d['pre_entry']['cs_ready'], d['pre_entry']['cs_skipped']))
        tt = d['tot']
        print('   totals: lines %d AvTrace %d ShaderRegister %d ShaderFirstUse %d PipelineTrace-CS-begin %d (after first %d) '
              'AsyncCompute %d held lines %d (cap 64) torn FrameTrace %d x_missing(post) %d' % (
                  tt['lines'], tt['avtrace'], tt['shreg'], tt['shfirst'], tt['pipetrace_cs_begin'], d['post']['cs_pipe'],
                  tt['asynccompute'], tt['held_lines'], tt['torn_ft'], d['post']['x_missing']))
    print('ALL OK')


if __name__ == '__main__':
    main()

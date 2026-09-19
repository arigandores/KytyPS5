"""Independent synthetic inputs for the settled engineering/confirmation scorer."""
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, 'C:/kyty/s99')
import settled99_gc as S


def setUpModule():
    global binary_patch
    binary_patch = patch.object(S, 'BINARY_SHA', S.BINARY_SHA if S.BINARY_SHA != 'UNSEALED' else 'c' * 64)
    binary_patch.start()


def tearDownModule():
    binary_patch.stop()


def fixture(blocks=80, instrument='a', transient=True):
    arms = {b: (0, 1, 1, 0)[b % 4] for b in range(blocks)}
    rows = {}
    for b, arm in arms.items():
        for idx in range(90):
            n = 1801 + 90 * b + idx
            row = dict.fromkeys(S.REQUIRED, 0)
            draws = 50 if arm and transient and idx < 60 else 100
            row.update(arm=arm, blk=b, draws=draws, dispatches=10, dt_us=50000,
                       cpu_gpu_us=30000, spin_gpu_us=0, bda_scan=1000,
                       rt_att=100, rt_kpx=200000, gpu_busy_us=12000, bf_igc_checks=1)
            if arm:
                row.update(bf_n=draws, bf_disp=10, bf_push=draws + 10,
                           bf_burn_ns=12000000, bf_burn_cpu_ns=8000000,
                           bf_burn_cpu_n=1, bf_burn_probe_ns=100000, bf_igc_hold=1,
                           bf_live_ahead=100 if instrument == 'a' else 0,
                           bf_live_mat=10 if instrument == 'a' else 110)
                if transient and (idx < 60 or idx == 89):
                    row['cpu_gpu_us'] = 100000
            if b > 0 and arms[b - 1] != arm and idx == 0:
                row['bf_edge'] = 1
            rows[n] = row
    return rows, arms


def metadata(tag='eng99a4', hold=300, instrument='a', burn=17800):
    texts = ['bindfloor=%d drawahead=%d bfmode=2 bfburn=%d' %
             (arm, 0 if arm and instrument == 'c' else 1, burn) for arm in (0, 1)]
    schedule = '90+1800:' + '|'.join(texts)
    env = dict(KYTY_BIND_FLOOR_LATCH='1', KYTY_BIND_FLOOR_CLEAR='0', KYTY_GPU_CLOCK_PIN='1',
               KYTY_GPU_MARKERS='0', KYTY_GPU_CHECKPOINTS='0', KYTY_GATE_SCHEDULE_ABBA='1',
               KYTY_BIND_FLOOR_CPU='1', KYTY_BIND_FLOOR_GC_AUDIT='1', KYTY_FRAME_TRACE='lite', KYTY_GATE_SCHEDULE=schedule)
    return {'tag': tag, 'binary_sha256': S.BINARY_SHA, 'prereg': {'sha256': 'f' * 64},
            'env': env, 'schedule': schedule, 'arms': texts,
            'gates': (S.ROOT / 'gates_base.txt').read_text(), 'hold_s': hold,
            'attempts': [{'label': 'attempt 1', 'outcome': 'ok', 'hold_exit': None,
                          'hold_s': hold, 'stable_frame': 1799}]}


def write_fixture(root, meta, rows, arms):
    tag = meta['tag']
    path = root / ('log_' + tag + '.txt')
    texts = meta['arms']
    with path.open('w', encoding='utf-8') as handle:
        handle.write('BindFloorLatch: mode 1\nBindFloorClear: mode 0\nGpuClockPin: mode 1\nBindFloorGcAudit: mode1\n')
        for b, arm in arms.items():
            handle.write('GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s\n' %
                         (arm, b, 1800 + 90 * b, texts[arm]))
            if b == 2:
                handle.write('BindFloorCpu: mode 1\n')  # observer line need not be at startup
            for n in range(1801 + 90 * b, 1891 + 90 * b):
                if n not in rows:
                    continue
                fields = ' '.join('%s=%d' % pair for pair in rows[n].items())
                handle.write('FrameTrace: n=%d %s\n' % (n, fields))
                handle.write('FrameTrace-draw: n=%d spin_gpu_us=%d\n' % (n, rows[n]['spin_gpu_us']))
                handle.write('FrameTrace-x: n=%d %s\n' % (n, fields))
    (root / (tag + '.json')).write_text(json.dumps(meta))
    stdout = root / ('stdout_' + tag + '.txt')
    stdout.write_bytes(b'')
    return path, stdout


class SelectionTests(unittest.TestCase):
    def test_gc_truth_cases_cover_whole_log_and_each_armed_block(self):
        for key in ('bf_igc_bad', 'bf_igc_critical', 'bf_igc_evict'):
            rows, arms = fixture()
            rows[1811][key] = 1  # early row; births remain zero
            result = S.analyze(rows, arms, 'a', 'pilot')
            self.assertFalse(result['technical'][key.upper() + '_ZERO'])
        rows, arms = fixture()
        for row in rows.values():
            row['bf_igc_checks'] = 0
        self.assertFalse(S.analyze(rows, arms, 'a', 'pilot')['technical']['IGC_CHECKS_POSITIVE'])
        rows, arms = fixture()
        selected = S.select(rows, arms)
        block = next(b for b in selected['blocks'] if arms[b] == 1)
        for n in selected['blocks'][block]:
            rows[n]['bf_igc_hold'] = 0
        self.assertFalse(S.analyze(rows, arms, 'a', 'pilot')['technical']['IGC_HOLD_EACH_ARMED_BLOCK'])
        rows, arms = fixture()
        rows[1811]['bf_igc_hold'] = -1
        self.assertFalse(S.analyze(rows, arms, 'a', 'pilot')['technical']['IGC_NONNEGATIVE'])
        rows, arms = fixture()
        del rows[1811]['bf_igc_checks']
        self.assertFalse(S.analyze(rows, arms, 'a', 'pilot')['technical']['FULL_SCHEMA'])

    def test_fixed_washout_cpu_vs_wall_and_query_indicator(self):
        rows, arms = fixture()
        result = S.analyze(rows, arms, 'a', 'measurement')
        self.assertTrue(all(result['technical'].values()), result['technical'])
        self.assertTrue(all(result['strict'].values()), result['strict'])
        self.assertEqual(result['endpoints']['B_cpu_ms'], 22)
        self.assertEqual(result['endpoints']['B_wall_compatibility_ms'], 18)
        self.assertEqual(result['endpoints']['cpu_query_cost_indicator_ms'], .1)
        self.assertLess(result['reported_raw_population']['work_pct'], -30)
        self.assertEqual(result['metrics']['work_pct'], 0)
        self.assertEqual(result['selection']['blocks'][4], list(range(2221, 2250)))

    def test_no_pair_reuse_balanced_and_edge_quartet_dropped(self):
        rows, arms = fixture(blocks=82)
        selected = S.select(rows, arms)
        flat = [b for pair in selected['pairs'] for b in pair]
        self.assertEqual(len(flat), len(set(flat)))
        self.assertEqual(sum(arms[a] == 0 for a, b in selected['pairs']),
                         sum(arms[a] == 1 for a, b in selected['pairs']))
        self.assertNotIn(80, flat)
        self.assertNotIn(81, flat)
        self.assertTrue(all(len(ns) == 29 for ns in selected['blocks'].values()))
        self.assertEqual(min(flat), 4)

    def test_internal_missing_row_not_rescued_by_dropping_quartet(self):
        rows, arms = fixture()
        del rows[1801 + 30 * 90 + 70]
        result = S.analyze(rows, arms, 'a', 'measurement')
        self.assertFalse(result['technical']['INTERNAL_ROWS_COMPLETE'])

    def test_block_zero_identity_cannot_hide_outside_endpoint(self):
        rows, arms = fixture()
        rows[1811]['arm'] = 2
        self.assertFalse(S.analyze(rows, arms, 'a', 'pilot')['technical']['FULL_ROW_IDENTITY'])
        rows, arms = fixture()
        rows[1811]['blk'] = 4
        self.assertFalse(S.analyze(rows, arms, 'a', 'pilot')['technical']['FULL_ROW_IDENTITY'])

    def test_missing_early_counter_and_early_live_leak(self):
        rows, arms = fixture()
        del rows[2081]['bf_burn_cpu_bad']
        result = S.analyze(rows, arms, 'a', 'measurement')
        self.assertFalse(result['technical']['FULL_SCHEMA'])
        rows, arms = fixture()
        rows[2081]['bf_live_mat'] = 1000000  # block3/base, idx10, before n2100
        self.assertFalse(S.analyze(rows, arms, 'a', 'measurement')['technical']['DARK_B'])

    def test_cpu_bad_aggregate_and_darkness(self):
        for key, value, check in [('bf_burn_cpu_bad', 1, 'CPU_BAD_ZERO'),
                                   ('bf_burn_cpu_ns', -1, 'CPU_NONNEGATIVE')]:
            rows, arms = fixture()
            rows[2311][key] = value
            self.assertFalse(S.analyze(rows, arms, 'a', 'measurement')['technical'][check])
        rows, arms = fixture()
        for row in rows.values():
            if row['arm']:
                row['bf_burn_cpu_ns'] = 40000000
        self.assertFalse(S.analyze(rows, arms, 'a', 'measurement')['technical']['CPU_AGGREGATE'])
        rows, arms = fixture()
        rows[2081]['bf_burn_cpu_ns'] = 1
        self.assertFalse(S.analyze(rows, arms, 'a', 'measurement')['technical']['CPU_DARK_STRUCTURE'])

    def test_engineering_does_not_publish_B_and_does_not_admit_work_failure(self):
        rows, arms = fixture()
        for row in rows.values():
            if row['arm']:
                row['draws'] = row['bf_n'] = 101
                row['bf_push'] = 111
        pilot = S.analyze(rows, arms, 'a', 'pilot')
        self.assertTrue(all(pilot['technical'].values()), pilot['technical'])
        self.assertFalse(pilot['strict']['WORK'])
        self.assertNotIn('endpoints', pilot)
        self.assertEqual(S.recommendation(17800, pilot['metrics'], pilot['strict'], 1)['action'], 'CAUSAL_TEST')
        measure = S.analyze(rows, arms, 'a', 'measurement')
        self.assertFalse(measure['strict']['WORK'])

    def test_area_is_attachment_weighted_and_pair_tolerance_is_half_percent(self):
        rows, arms = fixture()
        for row in rows.values():
            if row['arm']:
                row['rt_att'] = 200
                row['rt_kpx'] = 400000  # same area despite different attachment count
        self.assertTrue(S.analyze(rows, arms, 'a', 'measurement')['strict']['AREA_SPLIT'])
        for row in rows.values():
            if row['arm']:
                row['rt_kpx'] = 403000  # +0.75%; split<1 PASS, each pair match FAIL
        result = S.analyze(rows, arms, 'a', 'measurement')
        self.assertTrue(result['strict']['AREA_SPLIT'])
        self.assertFalse(result['strict']['AREA_MATCH'])
        self.assertEqual(result['metrics']['area_match_pct'], 0)

    def test_c_instrument_requires_materialization_without_ahead(self):
        rows, arms = fixture(instrument='c')
        self.assertTrue(S.analyze(rows, arms, 'c', 'measurement')['technical']['C4_B_OUT'])
        rows[2311]['bf_live_ahead'] = 1
        self.assertFalse(S.analyze(rows, arms, 'c', 'measurement')['technical']['C4_B_OUT'])


class ProtocolTests(unittest.TestCase):
    def test_diagnostic_trace_presence_and_gc_startup_are_guarded(self):
        for mutation in [lambda m, l, o: m['env'].update(KYTY_IMAGE_LIFETIME_TRACE='0'),
                         lambda m, l, o: m['env'].update(KYTY_IMAGE_LIFETIME_TRACE='1'),
                         lambda m, l, o: l.write_text(l.read_text() + 'ImageLife: create\n'),
                         lambda m, l, o: o.write_bytes(b'ImageLife: free\n'),
                         lambda m, l, o: l.write_text(l.read_text().replace('BindFloorGcAudit: mode1\n', ''))]:
            self.assertTrue(self.check(mutation)['errors'])

    def check(self, mutate=None, hold=300, instrument='a', blocks=80):
        with tempfile.TemporaryDirectory(prefix='settled99_protocol_') as temp:
            root = Path(temp)
            meta = metadata(hold=hold, instrument=instrument)
            rows, arms = fixture(blocks=blocks, instrument=instrument)
            log, stdout = write_fixture(root, meta, rows, arms)
            if mutate:
                mutate(meta, log, stdout)
            with patch.object(S, 'PRED_SHA', 'f' * 64):
                return S.protocol(meta, log, stdout, instrument, 'pilot' if hold == 300 else 'measurement')

    def test_both_protocols_and_delayed_cpu_mode_line(self):
        self.assertEqual(self.check()['errors'], [])
        self.assertEqual(self.check(instrument='c')['errors'], [])
        self.assertEqual(self.check(hold=900, blocks=220)['errors'], [])

    def test_old_period_inconsistent_arms_binary_or_observer_rejected(self):
        for mutation in [lambda m, l, o: m['env'].pop('KYTY_BIND_FLOOR_CPU'),
                         lambda m, l, o: m.update(binary_sha256='0' * 64),
                         lambda m, l, o: m.update(arms=list(reversed(m['arms']))),
                         lambda m, l, o: l.write_text(l.read_text().replace('period=90', 'period=30'))]:
            self.assertTrue(self.check(mutation)['errors'])

    def test_missing_stream_stdout_failure_and_short_hold(self):
        for mutation in [lambda m, l, o: o.unlink(),
                         lambda m, l, o: o.write_bytes(b'ERRORDEVICELOST\n'),
                         lambda m, l, o: l.write_text(l.read_text().replace('FrameTrace-draw:', 'Removed-draw:'))]:
            self.assertTrue(self.check(mutation)['errors'])
        self.assertTrue(self.check(blocks=20)['errors'])


class ControlFlowTests(unittest.TestCase):
    def test_reset_campaign_does_not_reinterpret_old_a3(self):
        self.assertEqual(S.identity('eng99a4'), ('pilot', 'a', 4))
        self.assertEqual(S.identity('eng99c1'), ('pilot', 'c', 1))
        with self.assertRaises(ValueError):
            S.identity('eng99a3')
        for instrument, ordinal in [('a', 4), ('c', 1)]:
            self.assertEqual(S.source_check(None, S.ROOT, {}, instrument, 'pilot', ordinal, 17800)[1], [])
            self.assertTrue(S.source_check(None, S.ROOT, {}, instrument, 'pilot', ordinal, 20000)[1])
            self.assertTrue(S.source_check(Path('old_a3.json'), S.ROOT, {}, instrument, 'pilot', ordinal, 17800)[1])
        metrics = {'dt_delta_us': 1050, 'dt_relative': .02}
        self.assertEqual(S.recommendation(17800, metrics, {}, 4)['action'], 'TUNE')
        self.assertEqual(S.recommendation(17800, metrics, {}, 5)['action'], 'TUNE')
        self.assertEqual(S.recommendation(17800, metrics, {}, 6)['action'], 'CAUSAL_TEST')

    def test_entry_suffix_bound_and_real_before_schedule_evidence(self):
        self.assertEqual(S.identity('eng99a4_entry1'), ('pilot', 'a', 4))
        self.assertEqual(S.identity('bf99f_entry2'), ('measurement', 'c', None))
        with self.assertRaises(ValueError):
            S.identity('bf99f_entry3')
        with tempfile.TemporaryDirectory(prefix='settled99_entry_') as temp:
            root = Path(temp)
            current = metadata(tag='eng99a4_entry1')
            old = copy.deepcopy(current)
            old['tag'] = 'eng99a4'
            old['attempts'][0].update(outcome='entry_timeout', hold_exit=1, hold_s=0)
            (root / 'eng99a4.json').write_text(json.dumps(old))
            log = root / 'log_eng99a4.txt'
            log.write_bytes(b'initialization failed\n')
            (root / 'stdout_eng99a4.txt').write_bytes(b'entry failure\n')
            self.assertEqual(S.entry_history('eng99a4_entry1', root, current)[1], [])
            log.write_bytes(b'GateArm: arm=0\n')
            self.assertTrue(S.entry_history('eng99a4_entry1', root, current)[1])
            log.write_bytes(b'initialization failed\n')
            current['env']['KYTY_RECOMPILE'] = '1'
            self.assertTrue(S.entry_history('eng99a4_entry1', root, current)[1])

    def test_frozen_source_requires_launch_pin_exact_budget_and_raw_replay(self):
        with tempfile.TemporaryDirectory(prefix='settled99_source_') as temp:
            root = Path(temp)
            for name in ('eng99a4.json', 'log_eng99a4.txt', 'stdout_eng99a4.txt'):
                (root / name).write_bytes(b'fixture source')
            source = {'schema': 'settled99-gc-v1', 'tag': 'eng99a4', 'phase': 'pilot', 'instrument': 'a',
                      'pred_sha256': 'f' * 64, 'binary_sha256': S.BINARY_SHA,
                      'status': 'ENGINEERING_COMPLETE', 'technical': {'PASS': True},
                      'strict': {'WORK': True}, 'metrics': {'dt_delta_us': 0, 'dt_relative': 0},
                      'selection': {'row_ranges': {4: [2221, 2249]}, 'pairs': [(4, 5)]},
                      'burn': 17800, 'decision': {'action': 'LOCK', 'fixed_burn': 17800},
                      'raw_sha256': {p.name: S.sha(p) for p in root.iterdir()}}
            path = root / 'source.json'
            path.write_text(json.dumps(source))
            meta = metadata(tag='bf99e', hold=900)
            meta['env'].update(KYTY_SETTLED_SOURCE_TAG='eng99a4', KYTY_SETTLED_SOURCE_SHA256=S.sha(path))
            with patch.object(S, 'PRED_SHA', 'f' * 64), patch.object(S, 'evaluate', return_value=source) as replay:
                self.assertEqual(S.source_check(path, root, meta, 'a', 'measurement', None, 17800)[1], [])
                self.assertTrue(S.source_check(path, root, meta, 'a', 'measurement', None, 21000)[1])
                wrong = copy.deepcopy(source); wrong['metrics']['dt_delta_us'] = 1
                replay.return_value = wrong
                self.assertTrue(S.source_check(path, root, meta, 'a', 'measurement', None, 17800)[1])
                replay.return_value = source
                tampered = copy.deepcopy(source)
                tampered['selection']['row_ranges'] = {'4': [1, 29]}
                path.write_text(json.dumps(tampered))
                meta['env']['KYTY_SETTLED_SOURCE_SHA256'] = S.sha(path)
                self.assertIn('source selection does not reproduce from raw under this sealed rule',
                              S.source_check(path, root, meta, 'a', 'measurement', None, 17800)[1])
                path.write_text(json.dumps(source))
                meta['env']['KYTY_SETTLED_SOURCE_SHA256'] = S.sha(path)
                meta['env'].pop('KYTY_SETTLED_SOURCE_SHA256')
                self.assertTrue(S.source_check(path, root, meta, 'a', 'measurement', None, 17800)[1])

    def test_updates_signflip_bounds_and_three_pilot_limit(self):
        metrics = {'dt_delta_us': 1050, 'dt_relative': .02}
        self.assertEqual(S.recommendation(17800, metrics, {}, 1)['next_burn'], 18900)
        previous = {'burn': 17800, 'metrics': {'dt_delta_us': 1050}}
        opposite = {'dt_delta_us': -500, 'dt_relative': .02}
        self.assertEqual(S.recommendation(18900, opposite, {}, 2, previous)['next_burn'], 18400)
        self.assertEqual(S.recommendation(17800, metrics, {}, 3)['action'], 'CAUSAL_TEST')
        self.assertEqual(S.recommendation(29900, metrics, {}, 1)['action'], 'CAUSAL_TEST')
        fit = {'dt_delta_us': 100, 'dt_relative': .002}
        self.assertEqual(S.recommendation(17800, fit, {'WORK': True}, 1), {'action': 'LOCK', 'fixed_burn': 17800})
        self.assertEqual(S.recommendation(17800, fit, {'WORK': False}, 1)['action'], 'CAUSAL_TEST')

    def test_legacy_mutable_state_is_restored(self):
        old = copy.deepcopy(S.OLD.R.BF_DARK)
        with S.legacy_state():
            S.OLD.R.BF_DARK.append('fake')
            S.OLD.H.DECIDE.append(('fixture', True))
        self.assertEqual(S.OLD.R.BF_DARK, old)
        self.assertNotIn(('fixture', True), S.OLD.H.DECIDE)

    def test_unsealed_and_mechanics_cannot_admit(self):
        with patch.object(S, 'PRED_SHA', 'UNSEALED'):
            result = S.evaluate('eng99a4', S.ROOT)
            self.assertEqual(result['status'], 'NOT_MEASUREMENT')
            self.assertNotIn('endpoints', result)

    def test_full_pilot_pipeline_with_real_old_helpers_is_mechanics_only(self):
        with tempfile.TemporaryDirectory(prefix='settled99_pipeline_') as temp:
            root = Path(temp)
            rule = root / 'fixture_rule.md'
            rule.write_text('synthetic fixture rule only')
            rule_sha = S.sha(rule)
            meta = metadata()
            meta['prereg']['sha256'] = rule_sha
            rows, arms = fixture()
            for row in rows.values():
                if row['arm'] == 0:
                    row['img_new'] = 40  # R6=80 and R6'=120; no direct image-GC loss
            write_fixture(root, meta, rows, arms)
            before = copy.deepcopy(S.OLD.R.BF_DARK)
            with patch.object(S, 'PRED', rule), patch.object(S, 'PRED_SHA', rule_sha):
                result = S.evaluate('eng99a4', root, mechanics=True)
            self.assertEqual(result['status'], 'NOT_MEASUREMENT')
            self.assertTrue(all(result['technical'].values()), result['technical'])
            self.assertTrue(all(result['strict'].values()), result['strict'])
            self.assertEqual(result['decision']['action'], 'LOCK')
            self.assertEqual(result['reported_image_birth_proxies'], {'R6': False, "R6'": False})
            self.assertNotIn('R6', result['technical'])
            self.assertNotIn("R6'", result['technical'])
            self.assertIn('R7', result['technical'])
            self.assertIn("R7'", result['technical'])
            self.assertTrue(any('R6' in line and 'FAIL' in line
                                for line in result['reported_full_reversibility'].splitlines()))
            self.assertNotIn('endpoints', result)
            self.assertEqual(result['errors'], ['mechanics-only; no admitted result or endpoint'])
            self.assertEqual(S.OLD.R.BF_DARK, before)
            self.assertEqual(len(result['reported_old_area_controls']), 3)
            self.assertTrue(any('[FAIL]' in line and 'work within' in line
                                for line in result['reported_old_area_controls']))

    def test_two_instruments_only_diagnostic_no_addends(self):
        a = {'status': 'ADMITTED_SETTLED_MEASUREMENT', 'instrument': 'a', 'endpoints': {'B_cpu_ms': 16}}
        c = dict(a, instrument='c')
        self.assertEqual(S.combine(a, c)['diagnostic'], 'HIGH')
        self.assertEqual(S.combine(a, c)['addend_ms'], 0)
        self.assertEqual(S.combine(a, a)['status'], 'NO_VERDICT')
        c['status'] = 'NOT_MEASUREMENT'
        self.assertEqual(S.combine(a, c)['status'], 'NO_VERDICT')


if __name__ == '__main__':
    unittest.main(verbosity=2)

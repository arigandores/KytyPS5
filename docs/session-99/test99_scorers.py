"""Offline adversarial fixtures for the mode2 scorer; no emulator process."""
import copy
import contextlib
import io
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bf99 as B
import m3_99 as M


def fixture(instrument='a', edge_position='idx0'):
    arms = {b: (0, 1, 1, 0)[b % 4] for b in range(320)}
    rows = {}
    for b, arm in arms.items():
        for i in range(30):
            n = 1800 + b * 30 + i
            r = dict.fromkeys(B.REQUIRED, 0)
            r.update(arm=arm, blk=b, draws=100, dispatches=10, dt_us=32000,
                     cpu_gpu_us=31500, spin_gpu_us=500, bda_scan=1000)
            if arm:
                r.update(bf_n=100, bf_disp=10, bf_push=110, bf_burn_ns=12000000,
                         bf_live_ahead=100 if instrument == 'a' else 0,
                         bf_live_mat=10 if instrument == 'a' else 110)
            rows[n] = r
    for b in range(1, len(arms)):
        if arms[b - 1] == arms[b]:
            continue
        offset = {'last-old': -1, 'idx0': 0, 'idx1': 1}[edge_position]
        rows[1800 + b * 30 + offset]['bf_edge'] = 1
        # Severe timing contamination at EVERY position T* must trim.
        for off in (-1, 0, 1):
            rows[1800 + b * 30 + off]['cpu_gpu_us'] += 900000
    return rows, arms


def metadata(instrument='a', calibration=False):
    texts = ['bindfloor=%d drawahead=%d bfmode=2 bfburn=12000' %
             (arm, 0 if instrument == 'c' and arm else 1) for arm in (0, 1)]
    schedule = '30+1800:' + '|'.join(texts)
    hold = 180 if calibration else 300
    labels = ['attempt 1'] if calibration else ['warmup', 'attempt 1']
    env = {'KYTY_BIND_FLOOR_LATCH': '1', 'KYTY_BIND_FLOOR_CLEAR': '0',
           'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GATE_SCHEDULE_ABBA': '1',
           'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_MARKERS': '0', 'KYTY_GPU_CHECKPOINTS': '0',
           'KYTY_GATE_SCHEDULE': schedule}
    return {'env': env, 'schedule': schedule, 'arms': texts, 'binary_sha256': B.BINARY_SHA,
            'prereg': {'sha256': 'f' * 64}, 'gates': (B.DEPS / 'gates_base.txt').read_text(),
            'hold_s': hold, 'attempts': [{'label': label, 'outcome': 'ok',
                                        'hold_exit': None, 'hold_s': hold,
                                        'stable_frame': 1799} for label in labels]}


def protocol_log(meta, duration_seconds=307.2):
    texts = meta['schedule'].split(':', 1)[1].split('|')
    lines = ['BindFloorLatch: mode 1', 'BindFloorClear: mode 0', 'GpuClockPin: mode 1']
    for b in range(8):
        arm = (0, 1, 1, 0)[b % 4]
        lines.append('GateArm: arm=%d arms=2 block=%d frame=%d period=30 abba=1 text=%s' %
                     (arm, b, 1800 + b * 30, texts[arm]))
    for n in range(1, int(round(duration_seconds * 1e6 / 32000)) + 1):
        lines.append('FrameTrace: n=%d dt_us=32000' % n)
    return '\n'.join(lines) + '\n'


class EndpointFixtures(unittest.TestCase):
    def test_mode2_burn_and_all_three_edge_positions(self):
        for pos in ('last-old', 'idx0', 'idx1'):
            rows, arms = fixture(edge_position=pos)
            result = B.controls(rows, arms, 'a')
            self.assertEqual(result['B'], 19.0)
            self.assertTrue(all(result['checks'].values()), result['checks'])
            wrong = B.H.block_endpoint(rows, 2100, 1800, 1, False, result['trim']['ts'])
            self.assertEqual(wrong['F'], 31.0)

    def test_materialization_positive_witness(self):
        rows, arms = fixture()
        for row in rows.values():
            for key in B.LIVE:
                row[key] = 0
        self.assertFalse(B.controls(rows, arms, 'a')['checks']['C4_B'])

    def test_frozen_reuse_fails_mode2(self):
        rows, arms = fixture()
        rows[2200]['bf_reuse'] = 1
        self.assertFalse(B.controls(rows, arms, 'a')['checks']['C4_B'])

    def test_out_requires_real_materialization_not_ahead(self):
        rows, arms = fixture('c')
        self.assertTrue(B.controls(rows, arms, 'c')['checks']['C4_B_OUT'])
        rows[2200]['bf_live_ahead'] = 1
        self.assertFalse(B.controls(rows, arms, 'c')['checks']['C4_B_OUT'])

    def test_one_missing_field_cannot_be_zero(self):
        rows, arms = fixture()
        del rows[2200]['bf_live_memo']
        result = B.controls(rows, arms, 'a')
        self.assertFalse(result['checks']['COUNTERS'])
        self.assertIsNone(result['B'])
        self.assertIn('bf_live_memo', result['missing'])

    def test_missing_integrity_field_before_timing_window_is_refused(self):
        rows, arms = fixture()
        del rows[1900]['bf_mixed']
        result = B.controls(rows, arms, 'a')
        self.assertFalse(result['checks']['COUNTERS'])
        self.assertIn('bf_mixed', result['missing'])
        self.assertIsNone(result['B'])

    def test_live_midblock_leak_before_timing_window_is_refused(self):
        for key in B.LIVE:
            rows, arms = fixture()
            rows[1900][key] = 1000000  # blk3, unarmed, idx10, n<2100
            result = B.controls(rows, arms, 'a')
            self.assertFalse(result['checks']['DARK_B'], key)

    def test_midblock_or_missing_or_duplicate_edge_refused(self):
        for mutation in ('mid', 'missing', 'duplicate'):
            rows, arms = fixture()
            if mutation == 'mid': rows[2200]['bf_edge'] = 1
            if mutation == 'missing': rows[1830]['bf_edge'] = 0
            if mutation == 'duplicate': rows[1831]['bf_edge'] = 1
            self.assertFalse(B.controls(rows, arms, 'a')['checks']['EDGE'])

    def test_union_darkness_and_leak_ratio(self):
        rows, arms = fixture()
        rows[2255]['bf_live_mat'] = 1  # base block15, interior
        self.assertFalse(B.controls(rows, arms, 'a')['checks']['DARK_B'])
        rows, arms = fixture()
        rows[2279]['bf_live_mat'] = 1000000  # allowed last base row, but too much total leak
        self.assertFalse(B.controls(rows, arms, 'a')['checks']['LIVE_DARK_RATIO'])

    def test_clear_and_marker_counters(self):
        for key, check in [('bf_clr_skip', 'REAL_CLEARS'), ('bf_skip_drop', 'REAL_CLEARS'),
                           ('gm_ops', 'MARKERS_OFF')]:
            rows, arms = fixture()
            rows[2200][key] = 1
            self.assertFalse(B.controls(rows, arms, 'a')['checks'][check])

    def test_calibration_rounding(self):
        self.assertEqual([B.round_100(x) for x in (149, 150, -149, -150)], [100, 200, -100, -200])


class ProtocolFixtures(unittest.TestCase):
    def check(self, meta, text=None, instrument='a', calibration=False, stdout=b''):
        with tempfile.TemporaryDirectory(prefix='kyty99_protocol_') as temp:
            log = Path(temp) / 'log_fixture.txt'
            log.write_text(protocol_log(meta) if text is None else text)
            if stdout is not None:
                (Path(temp) / 'stdout_fixture.txt').write_bytes(stdout)
            with patch.object(B, 'PRED_SHA', 'f' * 64):
                return B.protocol(meta, log, instrument, calibration)[0]

    def test_valid_both_instruments_and_calibration(self):
        for instrument in ('a', 'c'):
            for cal in (False, True):
                self.assertEqual(self.check(metadata(instrument, cal), instrument=instrument,
                                            calibration=cal), [])

    def test_wrong_requested_mode_rejected_even_if_actual_matches(self):
        meta = metadata()
        meta['schedule'] = meta['schedule'].replace('bfmode=2', 'bfmode=3')
        meta['env']['KYTY_GATE_SCHEDULE'] = meta['schedule']
        self.assertTrue(self.check(meta))

    def test_missing_metadata_and_wrong_actual_protocol(self):
        for key in ('KYTY_GPU_CLOCK_PIN', 'KYTY_BIND_FLOOR_CLEAR', 'KYTY_GPU_MARKERS'):
            meta = metadata(); del meta['env'][key]
            self.assertTrue(self.check(meta))
        meta = metadata()
        for bad in (protocol_log(meta).replace('abba=1', 'abba=0'),
                    protocol_log(meta).replace('period=30', 'period=10'),
                    protocol_log(meta).replace('bfmode=2', 'bfmode=3'),
                    protocol_log(meta) + 'GpuWaitSlow: stalled\n'):
            self.assertTrue(self.check(meta, bad))

    def test_no_retry_and_warmup_death(self):
        meta = metadata(); meta['attempts'][0]['hold_exit'] = 3
        self.assertTrue(self.check(meta))

    def test_contradictory_metadata_arms_and_short_raw_hold(self):
        meta = metadata()
        meta['arms'] = ['bindfloor=1 bfmode=3', 'bindfloor=0 bfmode=3']
        self.assertTrue(self.check(meta))
        meta = metadata()
        self.assertTrue(self.check(meta, protocol_log(meta, duration_seconds=134.4)))
        meta = metadata(); meta['attempts'].append(copy.deepcopy(meta['attempts'][-1]))
        self.assertTrue(self.check(meta))

    def test_wrong_binary_gates_or_seal(self):
        for key, value in [('binary_sha256', '9' * 64), ('gates', 'drawahead=1'),
                            ('prereg', {'sha256': '0' * 64})]:
            meta = metadata(); meta[key] = value
            self.assertTrue(self.check(meta))

    def test_stdout_only_failure_and_missing_stdout_are_refused(self):
        for marker in (b'ERRORDEVICELOST', b'Unhandled Exception', b'std::terminate',
                       b'abort()', b'GPUWAITSlow', b'fatal'):
            self.assertTrue(self.check(metadata(), stdout=marker + b'\n'), marker)
        self.assertTrue(self.check(metadata(), stdout=None))


class DecisionFixtures(unittest.TestCase):
    def test_both_instruments_and_no_closure(self):
        for a, c, expected in [(16, 16, 'HIGH DIAGNOSTIC'), (10, 10, 'LOW DIAGNOSTIC'),
                                (16, 14, 'DIAGNOSTIC GAP'), (10, 12, 'DIAGNOSTIC GAP'),
                                (16, None, 'NO VERDICT'), (float('nan'), 10, 'NO VERDICT')]:
            actual = M.branch(a, c)
            self.assertEqual(actual, expected)
            self.assertNotIn('CLOSE', actual)
            self.assertNotIn('PROCEED', actual)

    def test_cli_mandatory_c_and_unsealed_refusal(self):
        process = subprocess.run([sys.executable, str(Path(M.__file__)), '--a', 'fixture'],
                                 capture_output=True, text=True)
        self.assertNotEqual(process.returncode, 0)
        with patch.object(sys, 'argv', ['bf99.py', 'fixture', '--instrument', 'a']), \
                patch.object(B, 'PRED_SHA', 'UNSEALED'), contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertNotEqual(B.main(), 0)
        self.assertNotIn('\nADMISSION: ADMITTED', out.getvalue())

    def test_mechanics_only_never_admits_even_with_valid_mocked_controls(self):
        with tempfile.TemporaryDirectory(prefix='kyty99_mechanics_') as temp:
            root = Path(temp)
            meta = metadata()
            (root / 'fixture.json').write_text(json.dumps(meta))
            (root / 'log_fixture.txt').write_text(protocol_log(meta))
            (root / 'log_fixture_warmup.txt').write_text(protocol_log(meta))
            (root / 'stdout_fixture.txt').write_bytes(b'')
            (root / 'stdout_fixture_warmup.txt').write_bytes(b'')
            rows, arms = fixture()
            with patch.object(sys, 'argv', ['bf99.py', 'fixture', '--instrument', 'a',
                                            '--root', str(root), '--mechanics-only']), \
                    patch.object(B, 'PRED_SHA', 'f' * 64), \
                    patch.object(B.H.E84, 'scan', return_value=(rows, {}, 1800)), \
                    patch.object(B, 'legacy', return_value=("C4 FAIL\nADMISSION: ADMITTED", dict.fromkeys(B.KEEP, True), 'VALID')), \
                    patch.object(B, 'reversibility', return_value=('R controls PASS', dict.fromkeys(B.RV_KEEP, True))), \
                    contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertNotEqual(B.main(), 0)
            self.assertIn('bf98 REPORTED ONLY| C4 FAIL', out.getvalue())
            self.assertIn('bf98 REPORTED ONLY| ADMISSION: ADMITTED', out.getvalue())
            self.assertNotIn('\nADMISSION: ADMITTED', out.getvalue())
            self.assertNotIn("\nB_st'' =", out.getvalue())


class CalibrationFixtures(unittest.TestCase):
    def test_stale_csv_cannot_mask_doubled_raw_area(self):
        rows, arms = fixture()
        meta = metadata()
        def write_raw(path, doubled=False):
            texts = meta['schedule'].split(':', 1)[1].split('|')
            with path.open('w', encoding='utf-8') as handle:
                handle.write('BindFloorLatch: mode 1\nBindFloorClear: mode 0\nGpuClockPin: mode 1\n')
                for block, arm in arms.items():
                    handle.write('GateArm: arm=%d arms=2 block=%d frame=%d period=30 abba=1 text=%s\n' %
                                 (arm, block, 1800 + 30 * block, texts[arm]))
                    for n in range(1800 + 30 * block, 1830 + 30 * block):
                        row = dict(rows[n], rt_att=100, rt_kpx=400000 if arm and doubled else 200000,
                                   gpu_busy_us=12000)
                        text = ' '.join('%s=%d' % item for item in row.items())
                        handle.write('FrameTrace: n=%d %s\nFrameTrace-x: n=%d %s\n' % (n, text, n, text))
        with tempfile.TemporaryDirectory(prefix='kyty99_rawarea_') as temp:
            root = Path(temp)
            path = root / 'log_area_fixture.txt'
            stale = root / 'area_area_fixture.csv'
            write_raw(path)
            rc, _ = B.invoke(B.AS, ['area_series.py', 'area_fixture', '--root', temp, '--out', str(stale)])
            self.assertEqual(rc, 0)
            stale_bytes = stale.read_bytes()
            self.assertIn('VERDICT: VALID', B.fresh_area('area_fixture', root))
            write_raw(path, doubled=True)
            fresh = B.fresh_area('area_fixture', root)
            self.assertIn('VERDICT: INVALID', fresh)
            self.assertNotIn('VERDICT: VALID', fresh)
            self.assertEqual(stale.read_bytes(), stale_bytes)
            raw_before = path.read_bytes()
            # The legacy wrapper and calibration replay both use this fresh-area hook.
            with patch.object(B.H, 'main', side_effect=lambda: print(
                    'CRITERION 3: ' + B.H.bf96.read_area(
                        B.H.bf96.run_tool('area_verdict.py', 'area_fixture', temp, str(path)),
                        'area_fixture')[0])):
                _, _, area = B.legacy('area_fixture', root)
            self.assertEqual(area, 'INVALID')
            self.assertEqual(path.read_bytes(), raw_before)
            self.assertEqual(stale.read_bytes(), stale_bytes)

    def test_exact_b_binding_sources_and_area(self):
        with tempfile.TemporaryDirectory(prefix='kyty99_calbind_') as temp:
            root = Path(temp)
            cal = metadata(calibration=True)
            (root / 'cal99a.json').write_text(json.dumps(cal))
            (root / 'log_cal99a.txt').write_text(protocol_log(cal))
            (root / 'stdout_cal99a.txt').write_bytes(b'')
            rows, pa = fixture()
            # Keep GateArm fixture and data block layout coherent for this component test.
            result = B.controls(rows, pa, 'a')
            data = {'status': 'VALID_CALIBRATION_ONLY', 'tag': 'cal99a', 'instrument': 'a',
                    'pred_sha256': 'f' * 64, 'binary_sha256': B.BINARY_SHA,
                    'dt_a_us': result['dt_a'], 'dt_u_us': result['dt_u'], 'bfburn': 12000,
                    'metadata_sha256': hashlib.sha256((root / 'cal99a.json').read_bytes()).hexdigest(),
                    'log_sha256': hashlib.sha256((root / 'log_cal99a.txt').read_bytes()).hexdigest(),
                    'stdout_sha256': hashlib.sha256((root / 'stdout_cal99a.txt').read_bytes()).hexdigest()}
            B.calibration_artifact(root, 'cal99a').write_text(json.dumps(data))
            with patch.object(B, 'PRED_SHA', 'f' * 64), \
                    patch.object(B, 'protocol', return_value=([], pa)), \
                    patch.object(B.H.E84, 'scan', return_value=(rows, {}, 1800)), \
                    patch.object(B, 'legacy', return_value=('C4 FAIL', dict.fromkeys(B.KEEP, True), 'VALID')) as legacy, \
                    patch.object(B, 'reversibility', return_value=('R controls PASS', dict.fromkeys(B.RV_KEEP, True))):
                self.assertEqual(B.calibration_binding(root, 'a', metadata()), [])
                wrong = metadata(); wrong['schedule'] = wrong['schedule'].replace('12000', '13000')
                self.assertIn('measurement burn does not equal its calibration',
                              B.calibration_binding(root, 'a', wrong))
                legacy.return_value = ('C4 FAIL', dict.fromkeys(B.KEEP, True), 'INVALID')
                self.assertIn('calibration legacy/area no longer admits source',
                              B.calibration_binding(root, 'a', metadata()))
                legacy.return_value = ('C4 FAIL', dict.fromkeys(B.KEEP, True), 'VALID')
                (root / 'log_cal99a.txt').write_text(protocol_log(cal) + 'changed\n')
                self.assertIn('calibration source changed: log_cal99a.txt',
                              B.calibration_binding(root, 'a', metadata()))


if __name__ == '__main__':
    unittest.main(verbosity=2)

"""Pred05 truth cases. Reuse the verified pred04 synthetic input builders only."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, 'C:/kyty/s99')
import settled99_norec as S
import test_settled99_gc as F


def aa_fixture(blocks=80):
    rows, arms = F.fixture(blocks=blocks, transient=False)
    for row in rows.values():
        row.update(draws=100, cpu_gpu_us=30000, dt_us=50000)
        for key in row:
            if key.startswith('bf_') and key not in S.IGC:
                row[key] = 0
        row['bf_igc_hold'] = 0
    return rows, arms


def metadata(tag='aa99plain', hold=300, instrument='a'):
    meta = F.metadata(tag=tag, hold=hold, instrument=instrument, burn=17800)
    if tag.startswith('aa99plain'):
        meta['arms'][1] = meta['arms'][1].replace('bindfloor=1', 'bindfloor=0')
        meta['schedule'] = '90+1800:' + '|'.join(meta['arms'])
        meta['env']['KYTY_GATE_SCHEDULE'] = meta['schedule']
    return meta


class AAAndCoreTests(unittest.TestCase):
    def test_aa_whole_internal_block_single_row_and_ordering_are_rejected(self):
        for remove in (list(range(2521, 2611)), [2561]):  # block8, or its interior row
            rows, arms = aa_fixture()
            for n in remove:
                del rows[n]
            result = S.analyze(rows, arms, 'a', 'aa')
            self.assertFalse(result['technical']['FULL_RAW_CONTIGUITY'])
            self.assertFalse(result['technical']['INTERNAL_ROWS_COMPLETE'])
        rows, arms = aa_fixture()
        reordered = dict(reversed(list(rows.items())))
        self.assertFalse(S.analyze(reordered, arms, 'a', 'aa')['technical']['FULL_RAW_ORDER'])

    def test_fake_labels_are_baseline_no_b_no_falls(self):
        rows, arms = aa_fixture()
        result = S.analyze(rows, arms, 'a', 'aa')
        self.assertTrue(all(result['technical'].values()), result['technical'])
        self.assertTrue(all(result['strict'].values()), result['strict'])
        self.assertNotIn('endpoints', result)
        self.assertNotIn('R2', result['technical'])
        self.assertEqual(result['metrics']['work_pct'], 0)

    def test_aa_work_and_area_keep_strict_bands(self):
        rows, arms = aa_fixture()
        for row in rows.values():
            if row['arm']:
                row['draws'] = 101  # 1%: old C5 passes, strict work must fail
        result = S.analyze(rows, arms, 'a', 'aa')
        self.assertFalse(result['strict']['WORK'])
        self.assertTrue(result['strict']['C5'])
        rows, arms = aa_fixture()
        for row in rows.values():
            if row['arm']:
                row['rt_kpx'] = 201500  # .75%: whole split passes, pair band .5% fails
        result = S.analyze(rows, arms, 'a', 'aa')
        self.assertTrue(result['strict']['AREA_SPLIT'])
        self.assertFalse(result['strict']['AREA_MATCH'])

    def test_aa_hidden_floor_clock_or_gc_failure_rejected_early(self):
        for key, check in [('bf_n', 'AA_FLOOR_OFF'), ('bf_burn_ns', 'AA_FLOOR_OFF'),
                            ('bf_burn_cpu_ns', 'AA_FLOOR_OFF'), ('bf_igc_bad', 'BF_IGC_BAD_ZERO'),
                            ('bf_igc_critical', 'BF_IGC_CRITICAL_ZERO'), ('bf_igc_evict', 'BF_IGC_EVICT_ZERO')]:
            rows, arms = aa_fixture()
            rows[1811][key] = 1
            self.assertFalse(S.analyze(rows, arms, 'a', 'aa')['technical'][check])
        rows, arms = aa_fixture()
        del rows[1811]['bf_burn_cpu_n']
        self.assertFalse(S.analyze(rows, arms, 'a', 'aa')['technical']['FULL_SCHEMA'])

    def test_unchanged_measurement_selection_clock_and_gc(self):
        rows, arms = F.fixture()
        result = S.analyze(rows, arms, 'a', 'measurement')
        self.assertTrue(all(result['technical'].values()))
        self.assertTrue(all(result['strict'].values()))
        self.assertEqual(result['endpoints']['B_cpu_ms'], 22)
        self.assertEqual(result['endpoints']['B_wall_compatibility_ms'], 18)
        self.assertEqual(result['selection']['blocks'][4], list(range(2221, 2250)))
        pairs = result['selection']['pairs']
        flat = [b for pair in pairs for b in pair]
        self.assertEqual(len(flat), len(set(flat)))
        self.assertEqual(sum(arms[a] == 0 for a, b in pairs), sum(arms[a] == 1 for a, b in pairs))
        rows[2081]['bf_live_mat'] = 1000000
        self.assertFalse(S.analyze(rows, arms, 'a', 'measurement')['technical']['DARK_B'])


class ProtocolAndPipelineTests(unittest.TestCase):
    def check(self, mutation=None):
        with tempfile.TemporaryDirectory(prefix='norec99_protocol_') as temp:
            root = Path(temp)
            meta = metadata()
            rows, arms = aa_fixture()
            log, stdout = F.write_fixture(root, meta, rows, arms)
            # No real floor slice means BindFloorCpu need never be printed.
            log.write_text(log.read_text().replace('BindFloorCpu: mode 1\n', ''))
            if mutation:
                mutation(meta, log, stdout)
            with patch.object(S, 'PRED_SHA', 'f' * 64):
                return S.protocol(meta, log, stdout, 'a', 'aa')['errors']

    def test_aa_protocol_without_cpu_startup(self):
        self.assertEqual(self.check(), [])
        self.assertTrue(self.check(lambda m, l, o: m['arms'].__setitem__(1,
                            m['arms'][1].replace('bindfloor=0', 'bindfloor=1'))))

    def test_rec_presence_or_runtime_rejected_but_backend_recordthread_allowed(self):
        for value in ('', '0', 'capture.mp4'):
            self.assertTrue(self.check(lambda m, l, o: m['env'].update(KYTY_REC=value)))
        self.assertTrue(self.check(lambda m, l, o: o.write_bytes(b'Recording: capture.mp4\n')))
        self.assertTrue(self.check(lambda m, l, o: l.write_text(l.read_text() + 'Recording: capture.mp4\n')))
        self.assertEqual(self.check(lambda m, l, o: o.write_bytes(b'RecordThread: started recorder=0x1\n')), [])

    def test_entry_retry_cannot_drop_a_recording_setting(self):
        with tempfile.TemporaryDirectory(prefix='norec99_entry_') as temp:
            root = Path(temp)
            current = metadata(tag='aa99plain_entry1')
            old = copy.deepcopy(current)
            old['tag'] = 'aa99plain'
            old['env']['KYTY_REC'] = '0'
            old['attempts'][0].update(outcome='entry_timeout', hold_s=0, hold_exit=1)
            (root / 'aa99plain.json').write_text(json.dumps(old))
            (root / 'log_aa99plain.txt').write_bytes(b'failed before schedule\n')
            (root / 'stdout_aa99plain.txt').write_bytes(b'entry failure\n')
            self.assertIn('entry retry changed runtime/cache/source configuration',
                          S.entry_history('aa99plain_entry1', root, current)[1])

    def test_aa_mechanics_pipeline_never_becomes_measurement(self):
        with tempfile.TemporaryDirectory(prefix='norec99_aa_') as temp:
            root = Path(temp)
            rule = root / 'rule.md'
            rule.write_text('synthetic pred05 fixture only')
            meta = metadata()
            meta['prereg']['sha256'] = S.sha(rule)
            rows, arms = aa_fixture()
            F.write_fixture(root, meta, rows, arms)
            with patch.object(S, 'PRED', rule), patch.object(S, 'PRED_SHA', S.sha(rule)):
                result = S.evaluate('aa99plain', root, mechanics=True)
            self.assertEqual(result['status'], 'NOT_MEASUREMENT')
            self.assertTrue(all(result['technical'].values()), result['technical'])
            self.assertTrue(all(result['strict'].values()), result['strict'])
            self.assertNotIn('endpoints', result)
            self.assertEqual(result['errors'], ['mechanics-only; no admitted result or endpoint'])

    def test_full_raw_protocol_rejects_whole_block_gap_duplicate_and_order(self):
        with tempfile.TemporaryDirectory(prefix='norec99_continuity_') as temp:
            root = Path(temp)
            rule = root / 'rule.md'; rule.write_text('synthetic continuity rule')
            meta = metadata(); meta['prereg']['sha256'] = S.sha(rule)
            rows, arms = aa_fixture()
            for n in range(2521, 2611):
                del rows[n]
            log, stdout = F.write_fixture(root, meta, rows, arms)
            with patch.object(S, 'PRED', rule), patch.object(S, 'PRED_SHA', S.sha(rule)):
                result = S.evaluate('aa99plain', root, mechanics=True)
                self.assertFalse(result['technical']['FULL_RAW_CONTIGUITY'])
                self.assertTrue(any('gap' in error for error in result['errors']))
                rows, arms = aa_fixture()
                log, stdout = F.write_fixture(root, meta, rows, arms)
                original = log.read_text()
                duplicate = next(line for line in original.splitlines() if line.startswith('FrameTrace: n=2561 '))
                log.write_text(original + duplicate + '\n')
                self.assertTrue(S.protocol(meta, log, stdout, 'a', 'aa')['errors'])
                lines = original.splitlines()
                i = next(i for i, line in enumerate(lines) if line.startswith('FrameTrace: n=2561 '))
                j = next(i for i, line in enumerate(lines) if line.startswith('FrameTrace: n=2562 '))
                lines[i], lines[j] = lines[j], lines[i]
                log.write_text('\n'.join(lines) + '\n')
                self.assertTrue(any('out of order' in error for error in
                                    S.protocol(meta, log, stdout, 'a', 'aa')['errors']))


class ProvenanceTests(unittest.TestCase):
    def test_old_recorded_confirmation_and_old_pilot_not_new_identities(self):
        for tag in ('bf99e', 'bf99f', 'eng99a4'):
            with self.assertRaises(ValueError):
                S.identity(tag)
        self.assertEqual(S.identity('bf99g'), ('measurement', 'a', None))
        self.assertEqual(S.identity('bf99h'), ('measurement', 'c', None))
        self.assertEqual(S.identity('eng99c1'), ('pilot', 'c', 1))

    def test_exact_carried_source_uses_unchanged_04_replay(self):
        path = S.ROOT / 'settled_runs/eng99a4_score.json'
        source = json.loads(path.read_text(encoding='utf-8'))
        meta = metadata(tag='bf99g', hold=900)
        meta['env'].update(KYTY_SETTLED_SOURCE_TAG='eng99a4', KYTY_SETTLED_SOURCE_SHA256=S.CARRY_ARTIFACT_SHA)
        with patch.object(S.CARRY04, 'evaluate', return_value=source) as replay:
            self.assertEqual(S.carried04_source(path, S.ROOT, meta, 17800)[1], [])
            replay.assert_called_once_with('eng99a4', S.ROOT)
            self.assertTrue(S.carried04_source(path, S.ROOT, meta, 18000)[1])
            wrong = copy.deepcopy(source)
            wrong['selection']['row_ranges'] = {'4': [1, 29]}
            replay.return_value = wrong
            self.assertTrue(S.carried04_source(path, S.ROOT, meta, 17800)[1])
        with tempfile.TemporaryDirectory(prefix='norec99_carry_') as temp:
            different = Path(temp) / 'changed.json'
            different.write_text(json.dumps(source))  # different bytes/hash cannot replace exact artifact
            if S.sha(different) == S.CARRY_ARTIFACT_SHA:
                different.write_text(different.read_text() + '\n')
            meta['env']['KYTY_SETTLED_SOURCE_SHA256'] = S.sha(different)
            self.assertTrue(S.carried04_source(different, S.ROOT, meta, 17800)[1])

    def test_aa_requires_prelaunch_hash_and_reproducible_selection(self):
        with tempfile.TemporaryDirectory(prefix='norec99_gate_') as temp:
            root = Path(temp)
            for name in ('aa99plain.json', 'log_aa99plain.txt', 'stdout_aa99plain.txt'):
                (root / name).write_bytes(b'fixture raw')
            source = {'tag': 'aa99plain', 'phase': 'aa', 'status': 'AA_PASS',
                      'pred_sha256': 'f' * 64, 'binary_sha256': S.BINARY_SHA,
                      'metrics': {'work_pct': 0}, 'technical': {'SCHEMA': True}, 'strict': {'WORK': True},
                      'selection': {'row_ranges': {4: [2221, 2249]}},
                      'raw_sha256': {p.name: S.sha(p) for p in root.iterdir()}}
            path = root / 'aa_score.json'
            path.write_text(json.dumps(source))
            meta = metadata(tag='bf99g', hold=900)
            meta['env'].update(KYTY_SETTLED_AA_TAG='aa99plain', KYTY_SETTLED_AA_SHA256=S.sha(path))
            with patch.object(S, 'PRED_SHA', 'f' * 64), patch.object(S, 'evaluate', return_value=source) as replay:
                self.assertEqual(S.aa_gate(path, root, meta), [])
                replay.assert_called_once_with('aa99plain', root)
                bad = copy.deepcopy(source); bad['selection']['row_ranges'] = {'4': [1, 29]}
                replay.return_value = bad
                self.assertTrue(S.aa_gate(path, root, meta))
                replay.return_value = source
                meta['env'].pop('KYTY_SETTLED_AA_SHA256')
                self.assertTrue(S.aa_gate(path, root, meta))

    def test_no_addends_or_global_closure(self):
        a = {'status': 'ADMITTED_SETTLED_MEASUREMENT', 'instrument': 'a', 'endpoints': {'B_cpu_ms': 16}}
        c = dict(a, instrument='c')
        self.assertEqual(S.combine(a, c)['diagnostic'], 'HIGH')
        self.assertEqual(S.combine(a, c)['addend_ms'], 0)
        self.assertEqual(S.combine(a, a)['status'], 'NO_VERDICT')


if __name__ == '__main__':
    unittest.main(verbosity=2)

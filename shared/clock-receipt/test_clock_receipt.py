import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import clock_receipt as c


class ClockReceiptTests(unittest.TestCase):
    def pack(self, bound=750):
        return c.margin.replay.make_pack([
            ('a', b'2026-10-18T10:00:00Z A\n'),
            ('b', b'2026-10-18T10:00:02Z B\n')], clock_uncertainty_ms=bound)

    def bundle(self, expression='1 s - 250 ms', bound=750):
        return c.bind(self.pack(bound), expression, ['a', 1], ['b', 1])

    def test_independent_receipt_and_timeline_replays(self):
        bundle = self.bundle()
        self.assertTrue(c.receipt.replay(bundle['calculation'])['verified'])
        self.assertTrue(c.margin.replay.verify_pack(bundle['timeline'])['verified'])
        result = c.analyze(c.decode(c.canonical(bundle)))
        self.assertEqual(result['asserted_total_bound_ms'], 750)
        self.assertEqual(result['analysis']['pair_order_limit_ms'], 500)
        self.assertEqual([r['relation'] for r in result['analysis']['boundary_replays']],
                         ['left-before-right', 'unresolved-overlap'])

    def test_different_valid_receipt_rejected(self):
        bundle = self.bundle()
        bundle['calculation'] = self.bundle('500 ms', 500)['calculation']
        self.assertTrue(c.receipt.replay(bundle['calculation'])['verified'])
        with self.assertRaisesRegex(ValueError, 'does not match'):
            c.analyze(bundle)

    def test_invalid_quantities(self):
        for expression in ['1 m', '0', '0.1 ms', '-1 ms', '2 day', '1 m + 1 s']:
            with self.subTest(expression=expression), self.assertRaises((ValueError, c.receipt.engine.UnitError)):
                self.bundle(expression)
        for expression, bound in [('0 ms', 0), ('1 day', 86400000), ('1 s / 2', 500)]:
            self.assertEqual(c.analyze(self.bundle(expression, bound))['asserted_total_bound_ms'], bound)

    def test_failed_claim_cannot_bind_even_when_receipt_verified(self):
        bundle = self.bundle()
        request = dict(bundle['calculation']['request'], at_most='700 ms')
        bundle['calculation'] = c.receipt.create(request)
        self.assertTrue(c.receipt.replay(bundle['calculation'])['verified'])
        with self.assertRaisesRegex(ValueError, 'failed claim'):
            c.analyze(bundle)

    def test_rehashed_calculation_forgery_and_timeline_tamper(self):
        bundle = self.bundle()
        bundle['calculation']['result']['value'] = '999'
        bundle['calculation']['receipt_sha256'] = c.receipt.digest({k: v for k, v in bundle['calculation'].items() if k != 'receipt_sha256'})
        with self.assertRaises(ValueError):
            c.analyze(bundle)
        bundle = self.bundle()
        bundle['timeline']['timeline']['events'][0]['message'] = 'changed'
        with self.assertRaises(ValueError):
            c.analyze(bundle)

    def test_schema_citations_and_type_confusion(self):
        original = self.bundle()
        for change in [{'extra': 1}, {'format': 'other'}, {'left': ['a', True]},
                       {'left': ['a', 0]}, {'left': ['a', 2]}, {'left': {}}, {'right': ['missing', 1]}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                c.analyze(dict(original, **change))
        for data in [b'{"a":1,"a":2}', b'NaN', b'"\xff"', b'['*70+b'0'+b']'*70]:
            with self.assertRaises(ValueError):
                c.decode(data)

    def test_pin_binds_exact_bytes_and_sizes_are_bounded(self):
        raw = c.canonical(self.bundle())
        c.check_pin(raw, hashlib.sha256(raw).hexdigest())
        with self.assertRaises(ValueError):
            c.check_pin(raw+b' ', hashlib.sha256(raw).hexdigest())
        with patch.object(c, 'MAX_BYTES', 10), self.assertRaises(ValueError):
            self.bundle()

    def test_immutable_and_same_event(self):
        bundle = self.bundle()
        before = copy.deepcopy(bundle)
        c.analyze(bundle)
        self.assertEqual(bundle, before)
        bundle['right'] = ['a', 1]
        self.assertEqual(c.analyze(bundle)['analysis']['current_relation'], 'same-event')

    def test_snapshot_bytes(self):
        for row in json.loads(Path(c.__file__).with_name('provenance.json').read_text()):
            snapshot = Path(row['snapshot']).read_bytes()
            self.assertEqual(snapshot, Path(row['source']).read_bytes())
            self.assertEqual(hashlib.sha256(snapshot).hexdigest(), row['sha256'])

    def test_cli_and_portable_copy(self):
        scratch = Path('test/scratch'); scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            folder = Path(directory) / 'clock-receipt'
            shutil.copytree(Path(c.__file__).parent, folder)
            script = str(folder / 'clock_receipt.py')
            def run(*args, data=None):
                return subprocess.run([sys.executable, '-B', script, *args], input=data,
                                      capture_output=True, timeout=15)
            self.assertEqual(run('demo').returncode, 0)
            made = run('bind', '--expression', '0.75 s', '--left', 'a', '1', '--right', 'b', '1',
                       data=c.canonical(self.pack()))
            self.assertEqual(made.returncode, 0, made.stderr)
            checked = run('verify', '--expect-sha256', hashlib.sha256(made.stdout).hexdigest(), data=made.stdout)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertTrue(json.loads(checked.stdout)['digest_pin_checked'])
            for data in [b'{}', b' '*(c.MAX_BYTES+1)]:
                failed = run('verify', data=data)
                self.assertEqual(failed.returncode, 2)
                self.assertEqual(failed.stdout, b'')


if __name__ == '__main__':
    unittest.main()

import base64
import copy
import hashlib
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import unicode_replay as tool


class ReplayTests(unittest.TestCase):
    def roundtrip(self, raw, limit=1000):
        bundle = tool.pack(raw, limit)
        encoded = tool.canonical(bundle)
        result = tool.verify(tool.parse_bundle(encoded))
        self.assertEqual(base64.b64decode(bundle['original_base64']), raw)
        self.assertEqual(result['source_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(result['source_bytes'], len(raw))
        self.assertEqual(bundle['report'], tool.citations.review(raw, tool.SOURCE_LABEL, limit))
        return bundle, result

    def test_demo_detects_tampering_and_keeps_total(self):
        result = tool.demo()
        self.assertTrue(result['altered_citation_rejected'])
        self.assertEqual(result['finding_count'], 5)
        self.assertEqual(result['retained_findings'], 2)
        self.assertTrue(result['truncated'])

    def test_preserves_exact_whitespace_escapes_duplicate_keys(self):
        raw = ' \r\n{"é":"🐸", "owner":1,"\\u006fwner":"\\u202e"}\r\n'.encode()
        bundle, _ = self.roundtrip(raw)
        self.assertTrue(any(f.get('rule') == 'duplicate-key' for f in bundle['report']['findings']))

    def test_clean_scalar_and_extreme_number(self):
        for raw in (b'null', b'true', b'[]', b'{}', b'9' * 5000, b'1e999999'):
            self.assertEqual(self.roundtrip(raw)[1]['finding_count'], 0)

    def test_deep_source_locations_survive_outer_bundle(self):
        self.roundtrip(b'[' * 64 + br'"\u202e"' + b']' * 64)

    def test_generated_documents_replay(self):
        rng = random.Random(737)
        alphabet = ['a', 'é', '🐸', '"', '\\', '\n', chr(0x202e), chr(0x200b)]
        for i in range(30):
            value = ''.join(rng.choice(alphabet) for _ in range(25))
            self.roundtrip(json.dumps({'note': [value]}, ensure_ascii=bool(i % 2)).encode(), i % 5 + 1)

    def test_mutated_report_fields_are_rejected(self):
        original = tool.pack(tool.citations.DEMO)
        mutations = [lambda b: b['report'].update(finding_count=0),
                     lambda b: b['report']['findings'].clear(),
                     lambda b: b['report']['findings'][0]['source_token'].update(sha256='0' * 64),
                     lambda b: b['report']['findings'][0]['source_token'].update(byte_start=0),
                     lambda b: b['report'].update(unicode_version='different'),
                     lambda b: b['report'].update(extra=True),
                     lambda b: b['report'].update(truncated=0),
                     lambda b: b['report'].update(bytes=float(b['report']['bytes']))]
        for mutation in mutations:
            bundle = copy.deepcopy(original)
            mutation(bundle)
            with self.assertRaises(ValueError):
                tool.verify(bundle)

    def test_consistent_replacement_passes_but_inconsistent_review_fails(self):
        bundle = tool.pack(b'{"a":1}')
        raw = b'{"a":2}'
        bundle['original_base64'] = base64.b64encode(raw).decode()
        bundle['report']['sha256'] = hashlib.sha256(raw).hexdigest()
        # Both sources have the same complete review except for the hash.
        # Replay is consistency, not authentication: a fully consistent edit passes.
        self.assertTrue(tool.verify(bundle)['verified'])
        bundle['original_base64'] = base64.b64encode(br'{"a":"\u202e"}').decode()
        bundle['report']['sha256'] = hashlib.sha256(br'{"a":"\u202e"}').hexdigest()
        with self.assertRaises(ValueError):
            tool.verify(bundle)

    def test_metadata_types_and_members(self):
        original = tool.pack(b'{}')
        for value in (True, 0, 1001, 1.0, '1', None):
            bundle = copy.deepcopy(original)
            bundle['max_findings'] = value
            with self.assertRaises(ValueError):
                tool.verify(bundle)
        for change in ({'format': 'other'}, {'extra': 1}, {'original_base64': []}):
            bundle = dict(original, **change)
            with self.assertRaises(ValueError):
                tool.verify(bundle)
        with self.assertRaises(ValueError):
            tool.verify([])

    def test_strict_bundle_json_duplicate_nonfinite_depth(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":{"a":1,"a":2}}', b'NaN', b'Infinity',
                    b'{} {}', b'\xef\xbb\xbf{}', b'"\xff"', b'[' * 65 + b'0' + b']' * 65):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                tool.parse_bundle(raw)

    def test_base64_is_canonical(self):
        original = tool.pack(b'{}')
        # e31= has nonzero unused pad bits but decodes to the same bytes as e30=.
        for value in ('e31=', 'e30=\n', '%%%=', 'é', 'e30', ''):
            bundle = dict(original, original_base64=value)
            with self.subTest(value=value), self.assertRaises(ValueError):
                tool.verify(bundle)

    def test_strict_source_errors_and_limits(self):
        for raw in (b'{', b'NaN', br'"\ud800"', b'\xef\xbb\xbf{}', b'\xff'):
            with self.assertRaises(ValueError):
                tool.pack(raw)
        with self.assertRaises(ValueError):
            tool.pack(b' ' * (tool.MAX_SOURCE_BYTES + 1))
        with patch.object(tool, 'MAX_REPORT_BYTES', 10), self.assertRaises(ValueError):
            tool.pack(b'{}')
        with patch.object(tool, 'MAX_PACK_BYTES', 10), self.assertRaises(ValueError):
            tool.pack(b'{}')
        with patch.object(tool, 'MAX_PACK_BYTES', 10), self.assertRaises(ValueError):
            tool.parse_bundle(b' ' * 11)

    def test_json_key_order_and_spacing_do_not_affect_replay(self):
        bundle = tool.pack(tool.citations.DEMO)
        raw = json.dumps(bundle, indent=2).encode()
        self.assertTrue(tool.verify(tool.parse_bundle(raw))['verified'])

    def test_cli_and_standalone_copy(self):
        scratch = Path.cwd() / 'test' / 'scratch'
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            root = Path(directory)
            for name in ('unicode-replay', 'json-citations', 'json-lantern', 'unicode-lantern'):
                shutil.copytree(Path(tool.__file__).resolve().parent.parent / name, root / name)
            script = root / 'unicode-replay' / 'unicode_replay.py'
            source = root / 'input.json'
            source.write_bytes(tool.citations.DEMO)
            def run(*args):
                return subprocess.run([sys.executable, '-B', str(script), *args], capture_output=True)
            made = run('pack', '--file', str(source), '--max-findings', '1')
            self.assertEqual(made.returncode, 0, made.stderr)
            packed = root / 'bundle.json'
            packed.write_bytes(made.stdout)
            verified = run('verify', '--file', str(packed))
            self.assertEqual(verified.returncode, 0, verified.stderr)
            self.assertTrue(json.loads(verified.stdout)['truncated'])
            self.assertEqual(run('demo').returncode, 0)
            for args in [('pack', '--file', '../outside.json'),
                         ('verify', '--file', str(source)),
                         ('pack', '--file', str(source), '--max-findings', '0')]:
                result = run(*args)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn('error', json.loads(result.stdout))
                self.assertTrue(result.stdout.isascii())
                self.assertFalse(result.stderr)

    def test_real_record_offline(self):
        raw = Path('dist/line-2/23.json').read_bytes()
        self.assertEqual(self.roundtrip(raw)[1]['finding_count'], 0)


if __name__ == '__main__':
    unittest.main()

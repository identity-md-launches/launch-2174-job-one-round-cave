import copy
from fractions import Fraction
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

import receipt as r


def request(expression="10 km / 2 h", **options):
    return dict(expression=expression, to=None, expect=None, at_least=None, at_most=None) | options


def rehash(receipt):
    receipt["receipt_sha256"] = r.digest({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    return receipt


class ReceiptTests(unittest.TestCase):
    def test_exact_roundtrip_and_determinism(self):
        req = request(to="m/s", expect="5 km/h", at_least="1 m/s", at_most="2 m/s")
        first = r.create(req)
        self.assertEqual(first, r.create(req))
        verified = r.replay(r.decode(r.canonical(first)))
        self.assertTrue(verified["verified"])
        self.assertEqual(verified["calculation_exit"], 0)
        self.assertEqual(verified["result"]["value"], "25/18")

    def test_failed_claim_and_bounds_are_valid_receipts(self):
        for opts in (dict(expect="6 km/h"), dict(at_least="2 m/s"), dict(at_most="1 m/s")):
            with self.subTest(opts=opts):
                checked = r.replay(r.create(request(**opts)))
                self.assertTrue(checked["verified"])
                self.assertEqual(checked["calculation_exit"], 1)

    def test_rehashed_forgery_rejected(self):
        original = r.create(request(expect="5 km/h"))
        alterations = [
            ("result", "value", "99"),
            ("result", "base_value", "99"),
            ("result", "expression", "1 s"),
            ("request", "expression", "1 s"),
        ]
        for outer, inner, value in alterations:
            changed = copy.deepcopy(original)
            changed[outer][inner] = value
            with self.subTest(outer=outer, inner=inner), self.assertRaises(r.ReceiptError):
                r.replay(rehash(changed))
        for key, value in (("calculation_exit", True), ("calculation_exit", 1)):
            changed = copy.deepcopy(original)
            changed[key] = value
            with self.assertRaises(r.ReceiptError):
                r.replay(rehash(changed))
        changed = copy.deepcopy(original)
        changed["result"]["check"]["matches"] = 1
        with self.assertRaises(r.ReceiptError):
            r.replay(rehash(changed))

    def test_hash_schema_engine_and_extra_fields(self):
        original = r.create(request())
        for key, value in (("schema", "other"), ("engine_sha256", "changed"),
                           ("receipt_sha256", "changed"), ("new", "ignored?")):
            with self.subTest(key=key), self.assertRaises(r.ReceiptError):
                r.replay(original | {key: value})
        with self.assertRaises(r.ReceiptError):
            r.replay([])
        with self.assertRaises(r.ReceiptError):
            r.replay(rehash(original | {"request": request() | {"file": "never opened"}}))

    def test_invalid_calculations_never_make_receipts(self):
        cases = [request("1 m + 1 s"), request("1 m", expect="0 s"),
                 request("1 m", to="s"), request("1 s", at_least="2 s", at_most="1 s"),
                 request("1/0"), request("-" * 1100 + "1"), request(to=""),
                 request(expect=""), request("1" * 4097), request(expression=None)]
        for req in cases:
            with self.subTest(req=req), self.assertRaises(r.ReceiptError):
                r.create(req)

    def test_json_boundary(self):
        for data in (b'{"a":1,"a":2}', b'{"a":{"x":1,"x":2}}', b'NaN',
                     b'Infinity', b'1.0', b'123456', b'\xff', b'{} trailing',
                     b'[' * 17 + b'0' + b']' * 17, b' ' * (r.MAX_BYTES + 1)):
            with self.subTest(data=data[:80]), self.assertRaises(r.ReceiptError):
                r.decode(data)
        self.assertEqual(r.decode(b'{"quote":"\\\"[[[","backslash":"\\\\"}'),
                         {"quote": '"[[[', "backslash": "\\"})
        self.assertEqual(r.decode(b' ' * (r.MAX_BYTES - 2) + b'{}'), {})

    def test_create_cannot_emit_an_oversized_receipt(self):
        padded = "1" + "\u2003" * 4095  # Legal parser whitespace, expanded by ASCII JSON.
        with self.assertRaisesRegex(r.ReceiptError, "serialized receipt exceeds"):
            r.create(request(padded, expect=padded, at_least=padded, at_most=padded))

    def test_independent_fraction_oracle(self):
        rng = random.Random(25)
        for _ in range(100):
            metres, seconds = rng.randint(-10000, 10000), rng.randint(1, 1000)
            value = Fraction(metres, seconds)
            receipt = r.create(request(f'{metres} m / {seconds} s', to="km/h",
                                       expect=f'({metres}/{seconds}) * m/s'))
            result = r.replay(receipt)
            self.assertEqual(result["calculation_exit"], 0)
            self.assertEqual(Fraction(result["result"]["base_value"]), value)
            self.assertEqual(Fraction(result["result"]["value"]), value * Fraction(18, 5))

    def test_subprocess_exit_and_no_partial_stdout(self):
        script = str(Path(__file__).with_name("receipt.py"))
        def run(*args, input=None):
            return subprocess.run([sys.executable, "-B", script, *args], input=input,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
        for claim, expected_status in (("5 km/h", 0), ("6 km/h", 1)):
            made = run("create", "10 km / 2 h", "--expect=" + claim)
            self.assertEqual(made.returncode, expected_status, made.stderr)
            checked = run("verify", input=made.stdout)
            self.assertEqual(checked.returncode, expected_status, checked.stderr)
            self.assertTrue(json.loads(checked.stdout)["verified"])
        for args, data in ((("create", "1 m + 1 s"), None), (("verify",), b'{}'),
                           (("verify",), b' ' * (r.MAX_BYTES + 1))):
            failed = run(*args, input=data)
            self.assertEqual(failed.returncode, 2)
            self.assertEqual(failed.stdout, b'')
            self.assertTrue(failed.stderr)


if __name__ == "__main__":
    unittest.main()

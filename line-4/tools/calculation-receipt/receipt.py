#!/usr/bin/env python3
"""Create and independently replay bounded exact dimensional calculation receipts."""
from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import sys

import engine

SCHEMA = "unit-flint-receipt/1"
MAX_BYTES = 65536
MAX_DEPTH = 16
FIELDS = ("expression", "to", "expect", "at_least", "at_most")


class ReceiptError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("ascii")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def formatted(value):
    return json.dumps(value, ensure_ascii=True, indent=2, allow_nan=False) + "\n"


def engine_hash():
    # Only our fixed sibling source is read; no path comes from a receipt.
    return hashlib.sha256(Path(__file__).with_name("engine.py").read_bytes()).hexdigest()


def validate_request(request):
    if type(request) is not dict or set(request) != set(FIELDS):
        raise ReceiptError("request must contain exactly expression, to, expect, at_least, at_most")
    for name in FIELDS:
        value = request[name]
        if value is None and name != "expression":
            continue
        if type(value) is not str or not value.strip() or len(value) > engine.MAX_SOURCE:
            raise ReceiptError(f"request.{name} must be a nonempty expression of at most {engine.MAX_SOURCE} characters")


def calculate(request):
    validate_request(request)
    args = ["--json"]
    for name in FIELDS[1:]:
        if request[name] is not None:
            # Equals protects negative expressions and strings beginning with '--'.
            args.append("--" + name.replace("_", "-") + "=" + request[name])
    args.extend(["--", request["expression"]])
    output, errors = io.StringIO(), io.StringIO()
    with redirect_stdout(output), redirect_stderr(errors):
        status = engine.main(args)
    if status not in (0, 1):
        raise ReceiptError(errors.getvalue().strip())
    return status, json.loads(output.getvalue())


def create(request):
    status, result = calculate(request)
    payload = {"schema": SCHEMA, "engine_sha256": engine_hash(),
               "request": dict(request), "calculation_exit": status, "result": result}
    receipt = {**payload, "receipt_sha256": digest(payload)}
    if len(formatted(receipt).encode("ascii")) > MAX_BYTES:
        raise ReceiptError(f"serialized receipt exceeds {MAX_BYTES} bytes; shorten the request")
    return receipt


def replay(receipt):
    keys = {"schema", "engine_sha256", "request", "calculation_exit", "result", "receipt_sha256"}
    if type(receipt) is not dict or set(receipt) != keys:
        raise ReceiptError("receipt has missing or extra fields")
    if receipt["schema"] != SCHEMA:
        raise ReceiptError("unsupported receipt schema")
    if receipt["engine_sha256"] != engine_hash():
        raise ReceiptError("engine source hash differs; use the receipt's original tool bundle")
    payload = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    if receipt["receipt_sha256"] != digest(payload):
        raise ReceiptError("receipt content hash mismatch")
    computed = create(receipt["request"])
    # JSON bytes distinguish true from 1 and 0 from 0.0, unlike Python equality.
    if canonical(computed) != canonical(receipt):
        raise ReceiptError("receipt does not match recomputed calculation")
    return {"verified": True, "receipt_sha256": receipt["receipt_sha256"],
            "calculation_exit": computed["calculation_exit"], "result": computed["result"]}


def decode(data):
    if len(data) > MAX_BYTES:
        raise ReceiptError(f"receipt exceeds {MAX_BYTES} bytes")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReceiptError("receipt is not UTF-8") from exc
    # Bound nesting before the JSON parser allocates nested containers.
    depth, quoted, escaped = 0, False, False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            if depth > MAX_DEPTH:
                raise ReceiptError(f"receipt exceeds {MAX_DEPTH} nesting levels")
        elif char in "]}":
            depth -= 1

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ReceiptError(f"duplicate JSON key: {key!r}")
            result[key] = value
        return result

    def integer(text):
        if len(text) > 5:
            raise ReceiptError("JSON integer exceeds receipt limit")
        return int(text)

    def forbidden(text):
        raise ReceiptError("JSON floats and nonfinite constants are not receipt values")

    try:
        return json.loads(text, object_pairs_hook=pairs, parse_int=integer,
                          parse_float=forbidden, parse_constant=forbidden)
    except (ValueError, RecursionError) as exc:
        raise ReceiptError(f"invalid receipt JSON: {exc}") from exc


def demo():
    request = {"expression": "5 MiB / (2 MiB/s)", "to": "s", "expect": "2500 ms",
               "at_least": "2 s", "at_most": "3 s"}
    receipt = create(request)
    checked = replay(decode(canonical(receipt)))
    failed = create({**request, "at_most": "2400 ms"})
    failed_replay = replay(failed)
    tampered = json.loads(canonical(receipt))
    tampered["result"]["value"] = "999"
    # Rehash too: recomputation, not just the checksum, must catch this change.
    tampered["receipt_sha256"] = digest({k: v for k, v in tampered.items() if k != "receipt_sha256"})
    try:
        replay(tampered)
    except ReceiptError:
        rejected = True
    else:
        raise ReceiptError("demo failed to reject altered result")
    print(json.dumps({"demo": "synthetic supplied quantities; no measurement claimed",
                      "matching_receipt": checked, "failed_bound_verified": failed_replay["verified"],
                      "failed_bound_calculation_exit": failed_replay["calculation_exit"],
                      "rehashed_altered_result_rejected": rejected}, indent=2))
    return 0


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest="command", required=True)
    make = commands.add_parser("create", help="print a receipt for a valid calculation")
    make.add_argument("expression")
    for field in FIELDS[1:]:
        make.add_argument("--" + field.replace("_", "-"))
    commands.add_parser("verify", help="read one receipt from stdin and recompute it")
    commands.add_parser("demo", help="show passing, failed and tampered receipts")
    args = cli.parse_args(argv)
    try:
        if args.command == "demo":
            return demo()
        if args.command == "create":
            result = create({name: getattr(args, name) for name in FIELDS})
        else:
            result = replay(decode(sys.stdin.buffer.read(MAX_BYTES + 1)))
        print(formatted(result), end="")
        return result["calculation_exit"]
    except ReceiptError as exc:
        print(f"calculation-receipt: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

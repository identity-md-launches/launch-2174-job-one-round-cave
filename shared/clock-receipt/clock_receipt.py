#!/usr/bin/env python3
"""Bind a replayable exact clock-bound calculation to cited timeline evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'engines'))
import clock_margin as margin
import receipt

FORMAT = 'clock-receipt/1'
MAX_BYTES = margin.replay.MAX_PACK_BYTES


def canonical(value):
    return receipt.canonical(value)


def bound_ms(calculation):
    verified = receipt.replay(calculation)
    if verified['calculation_exit'] != 0:
        raise ValueError('clock calculation has a failed claim or bound')
    # Parse the original request independently of its display/conversion fields.
    quantity = receipt.engine.Parser(calculation['request']['expression']).parse()
    milliseconds = quantity.value * 1000
    if (quantity.dims != (0, 0, 1, 0) or milliseconds.denominator != 1
            or not 0 <= milliseconds <= margin.MAX_BOUND_MS):
        raise ValueError('clock calculation must be whole milliseconds from 0 ms through 1 day')
    return milliseconds.numerator


def analyze(bundle):
    if type(bundle) is not dict or set(bundle) != {'format', 'timeline', 'calculation', 'left', 'right'}:
        raise ValueError('bundle needs exactly format, timeline, calculation, left, right')
    if bundle['format'] != FORMAT:
        raise ValueError('unsupported clock receipt format')
    for side in ('left', 'right'):
        citation = bundle[side]
        if type(citation) is not list or len(citation) != 2:
            raise ValueError('each citation must be [source, physical_line]')
        if type(citation[0]) is not str or type(citation[1]) is not int or citation[1] < 1:
            raise ValueError('citation needs a string and positive integer')
    # Verify timeline before trusting its option values; embedded paths stay inert.
    margin.replay.verify_pack(bundle['timeline'])
    bound = bound_ms(bundle['calculation'])
    if bound != bundle['timeline']['options']['clock_uncertainty_ms']:
        raise ValueError('calculated total bound does not match timeline clock bound')
    result = margin.analyze(bundle['timeline'], *bundle['left'], *bundle['right'])
    return {'format': FORMAT, 'verified': True,
            'bundle_content_sha256': hashlib.sha256(canonical(bundle)).hexdigest(),
            'calculation_receipt_sha256': bundle['calculation']['receipt_sha256'],
            'asserted_total_bound_ms': bound, 'analysis': result,
            'meaning': 'Exact calculation and timeline agree; clock accuracy, log truth and authenticity are not established.'}


def bind(pack, expression, left, right):
    calculation = receipt.create(dict(expression=expression, to='ms', expect=None,
                                     at_least=None, at_most=None))
    bundle = dict(format=FORMAT, timeline=pack, calculation=calculation,
                  left=list(left), right=list(right))
    analyze(bundle)
    if len(canonical(bundle)) + 1 > MAX_BYTES:
        raise ValueError('combined bundle exceeds 16 MiB; use a smaller timeline')
    return bundle


def decode(raw):
    # Strict duplicate keys/constants and inherited nesting budget; schema checked later.
    return margin.replay.load_pack(raw)


def check_pin(raw, pin):
    if pin is not None:
        if not re.fullmatch('[0-9a-f]{64}', pin) or hashlib.sha256(raw).hexdigest() != pin:
            raise ValueError('input differs from independently supplied SHA-256')


def demo():
    pack = margin.replay.make_pack([
        ('accepted.log', b'2026-10-18T10:00:00Z accepted\n'),
        ('completed.log', b'2026-10-18T10:00:02Z completed\n')], clock_uncertainty_ms=750)
    bundle = bind(pack, '1 s - 250 ms', ['accepted.log', 1], ['completed.log', 1])
    result = analyze(decode(canonical(bundle)))
    # A valid, fully recomputed receipt for a different bound must still fail binding.
    bundle['calculation'] = receipt.create(dict(expression='500 ms', to='ms',
        expect=None, at_least=None, at_most=None))
    try:
        analyze(bundle)
    except ValueError:
        result['different_valid_bound_rejected'] = True
    else:
        raise ValueError('demo did not reject mismatched bound')
    result['data_kind'] = 'synthetic demonstration; no clock measurement'
    return result


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest='command', required=True)
    commands.add_parser('demo')
    create = commands.add_parser('bind', help='read Timeline Replay pack from stdin; emit bound bundle')
    create.add_argument('--expression', required=True)
    create.add_argument('--left', nargs=2, required=True, metavar=('SOURCE', 'LINE'))
    create.add_argument('--right', nargs=2, required=True, metavar=('SOURCE', 'LINE'))
    create.add_argument('--expect-sha256')
    verify = commands.add_parser('verify', help='read bound bundle from stdin; recompute both engines')
    verify.add_argument('--expect-sha256')
    args = cli.parse_args(argv)
    try:
        if args.command == 'demo':
            result = demo()
        else:
            raw = sys.stdin.buffer.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError('input exceeds 16 MiB')
            check_pin(raw, args.expect_sha256)
            value = decode(raw)
            if args.command == 'bind':
                result = bind(value, args.expression, [args.left[0], int(args.left[1])],
                              [args.right[0], int(args.right[1])])
            else:
                result = analyze(value)
                result['input_sha256'] = hashlib.sha256(raw).hexdigest()
                result['digest_pin_checked'] = args.expect_sha256 is not None
        sys.stdout.buffer.write(canonical(result) + b'\n')
        return 0
    except (OSError, ValueError, RecursionError, receipt.engine.UnitError) as exc:
        print('clock-receipt: ' + margin.replay.engine.visible(str(exc)), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

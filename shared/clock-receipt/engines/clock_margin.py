#!/usr/bin/env python3
"""Find the clock-bound sensitivity of two events in verified timeline evidence."""
import argparse
import base64
from datetime import datetime
import json
import re
import sys
import replay

MAX_BOUND_MS = 86400000


def instant(text):
    return datetime.fromisoformat(text.replace('Z', '+00:00'))


def microseconds(delta):
    return (delta.days * 86400 + delta.seconds) * 1000000 + delta.microseconds


def select(events, source, line):
    if not isinstance(source, str) or type(line) is not int or line < 1:
        raise replay.ReplayError('citation needs a text source and positive integer line')
    matches = [e for e in events if (e['source'], e['line']) == (source, line)]
    if len(matches) != 1:
        raise replay.ReplayError('citation must identify exactly one parsed event')
    return matches[0]


def relation(left, right):
    if (left['source'], left['line']) == (right['source'], right['line']):
        return 'same-event'
    if instant(left['end_utc_exclusive']) <= instant(right['start_utc']):
        return 'left-before-right'
    if instant(right['end_utc_exclusive']) <= instant(left['start_utc']):
        return 'right-before-left'
    return 'unresolved-overlap'


def citation(event):
    return {key: event[key] for key in ('source', 'line', 'line_sha256',
                                      'start_utc', 'end_utc_exclusive')}


def analyze(pack, left_source, left_line, right_source, right_line):
    # Verify before interpreting any claimed report field or embedded evidence.
    verified = replay.verify_pack(pack)
    current_left = select(pack['timeline']['events'], left_source, left_line)
    current_right = select(pack['timeline']['events'], right_source, right_line)
    inputs = [(s['source'], base64.b64decode(s['base64'], validate=True))
              for s in pack['inputs']]

    def rebuild(bound):
        return replay.make_pack(inputs, pack['options']['ignore_unmatched'], bound)

    zero = rebuild(0)
    left = select(zero['timeline']['events'], left_source, left_line)
    right = select(zero['timeline']['events'], right_source, right_line)
    zero_relation = relation(left, right)
    result = {
        'format': 'clock-margin/1', 'replay': verified,
        'current_bound_ms': pack['options']['clock_uncertainty_ms'],
        'current_relation': relation(current_left, current_right),
        'zero_bound_relation': zero_relation,
        'zero_bound_left': citation(left), 'zero_bound_right': citation(right),
        'pair_order_limit_ms': None, 'max_order_bound_in_supported_domain_ms': None,
        'first_overlap_bound_in_supported_domain_ms': None,
        'boundary_replays': [],
        'interpretation': 'Total symmetric clock bounds, not additional error or measured skew. '
                          'Pair limits are interval algebra; boundary replays can fail on other '
                          'events or calendar/pack limits. No causality or authenticity claim.'}
    if zero_relation not in ('left-before-right', 'right-before-left'):
        return result
    early, late = (left, right) if zero_relation == 'left-before-right' else (right, left)
    gap = microseconds(instant(late['start_utc']) - instant(early['end_utc_exclusive']))
    # Both ends move toward one another by B*1000 us. Equality is still ordered
    # because each event interval is half open. Integer division is exact.
    limit = gap // 2000
    supported = min(limit, MAX_BOUND_MS)
    result['pair_order_limit_ms'] = limit
    result['max_order_bound_in_supported_domain_ms'] = supported
    if limit < MAX_BOUND_MS:
        result['first_overlap_bound_in_supported_domain_ms'] = limit + 1
    for bound in [supported] + ([limit + 1] if limit < MAX_BOUND_MS else []):
        check = {'bound_ms': bound}
        try:
            changed = rebuild(bound)
            a = select(changed['timeline']['events'], left_source, left_line)
            b = select(changed['timeline']['events'], right_source, right_line)
            check.update(replayable=True, relation=relation(a, b),
                         left=citation(a), right=citation(b))
        except (replay.ReplayError, replay.engine.TimelineError) as exc:
            check.update(replayable=False, error=str(exc))
        result['boundary_replays'].append(check)
    return result


def demo():
    inputs = [('accepted.log', b'2026-10-18T10:00:00Z accepted\n'),
              ('completed.log', b'2026-10-18T10:00:02Z completed\n')]
    pack = replay.make_pack(inputs, clock_uncertainty_ms=750)
    return {'example': 'synthetic, not a real incident',
            'analysis': analyze(pack, 'accepted.log', 1, 'completed.log', 1)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('demo')
    check = commands.add_parser('analyze')
    check.add_argument('pack')
    check.add_argument('--left', nargs=2, required=True, metavar=('SOURCE', 'LINE'))
    check.add_argument('--right', nargs=2, required=True, metavar=('SOURCE', 'LINE'))
    check.add_argument('--expect-sha256')
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            result = demo()
        else:
            raw = replay.read_workspace(args.pack, replay.MAX_PACK_BYTES)
            if args.expect_sha256 is not None:
                if not re.fullmatch('[0-9a-f]{64}', args.expect_sha256):
                    raise replay.ReplayError('expected hash must be 64 lowercase hex digits')
                if replay.digest(raw) != args.expect_sha256:
                    raise replay.ReplayError('pack does not match expected SHA-256')
            result = analyze(replay.load_pack(raw), args.left[0], int(args.left[1]),
                             args.right[0], int(args.right[1]))
            result['pack_sha256'] = replay.digest(raw)
        sys.stdout.buffer.write(replay.canonical(result) + b'\n')
        return 0
    except (OSError, ValueError, RecursionError) as exc:
        print('clock-margin: ' + replay.engine.visible(str(exc)), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

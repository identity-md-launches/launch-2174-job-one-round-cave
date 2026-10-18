import copy
from datetime import datetime, timedelta, timezone
import random
import unittest
import clock_margin as m


class MarginTests(unittest.TestCase):
    def pack(self, a='2026-10-18T10:00:00Z', b='2026-10-18T10:00:02Z', **options):
        return m.replay.make_pack([('a', (a+' A\n').encode()),
                                   ('b', (b+' B\n').encode())], **options)

    def analyze(self, pack):
        return m.analyze(pack, 'a', 1, 'b', 1)

    def test_boundary_and_current_bound(self):
        r = self.analyze(self.pack(clock_uncertainty_ms=750))
        self.assertEqual(r['current_relation'], 'unresolved-overlap')
        self.assertEqual(r['pair_order_limit_ms'], 500)
        self.assertEqual(r['first_overlap_bound_in_supported_domain_ms'], 501)
        self.assertEqual([c['relation'] for c in r['boundary_replays']],
                         ['left-before-right', 'unresolved-overlap'])

    def test_adjacent_half_open(self):
        r = self.analyze(self.pack(b='2026-10-18T10:00:01Z'))
        self.assertEqual(r['pair_order_limit_ms'], 0)
        self.assertEqual(r['boundary_replays'][0]['relation'], 'left-before-right')
        self.assertEqual(r['boundary_replays'][1]['relation'], 'unresolved-overlap')

    def test_microsecond_floor(self):
        r = self.analyze(self.pack(a='2026-10-18T10:00:00.000000Z',
                                   b='2026-10-18T10:00:00.003000Z'))
        self.assertEqual(r['pair_order_limit_ms'], 1)  # 2999 us / 2000

    def test_reverse(self):
        p = self.pack()
        r = m.analyze(p, 'b', 1, 'a', 1)
        self.assertEqual(r['pair_order_limit_ms'], 500)
        self.assertEqual(r['boundary_replays'][0]['relation'], 'right-before-left')

    def test_overlap_at_zero(self):
        r = self.analyze(self.pack(b='2026-10-18T10:00Z'))
        self.assertIsNone(r['pair_order_limit_ms'])
        self.assertEqual(r['zero_bound_relation'], 'unresolved-overlap')
        self.assertEqual(r['boundary_replays'], [])

    def test_identity(self):
        r = m.analyze(self.pack(), 'a', 1, 'a', 1)
        self.assertEqual(r['current_relation'], 'same-event')
        self.assertIsNone(r['pair_order_limit_ms'])

    def test_offsets(self):
        self.assertEqual(self.analyze(self.pack(a='2026-10-18T12:00:00+02:00'))[
            'pair_order_limit_ms'], 500)

    def test_domain_cap(self):
        r = self.analyze(self.pack(b='2026-10-21T10:00:02Z'))
        self.assertGreater(r['pair_order_limit_ms'], m.MAX_BOUND_MS)
        self.assertEqual(r['max_order_bound_in_supported_domain_ms'], m.MAX_BOUND_MS)
        self.assertIsNone(r['first_overlap_bound_in_supported_domain_ms'])
        self.assertEqual(len(r['boundary_replays']), 1)

    def test_other_calendar_event_blocks_replay_honestly(self):
        p = m.replay.make_pack([('a', b'2026-10-18T10:00:00Z A\n'),
                                ('b', b'2026-10-18T10:00:02Z B\n'),
                                ('edge', b'0001-01-01T00:00:00Z edge\n')], True)
        r = self.analyze(p)
        self.assertEqual(r['pair_order_limit_ms'], 500)
        self.assertTrue(all(not c['replayable'] for c in r['boundary_replays']))
        self.assertIn('calendar', r['boundary_replays'][0]['error'])

    def test_tampering_rejected(self):
        p = self.pack()
        p['timeline']['events'][0]['message'] = 'changed'
        with self.assertRaises(m.replay.ReplayError):
            self.analyze(p)

    def test_omissions_and_inert_source_paths(self):
        p = m.replay.make_pack([('/outside/not-opened', b'bad\n2026-10-18T10:00:00Z A\n'),
                                ('b', b'2026-10-18T10:00:02Z B\n')], True)
        r = m.analyze(p, '/outside/not-opened', 2, 'b', 1)
        self.assertEqual(r['replay']['omitted'], 1)
        for line in (1, 0, True, 3):
            with self.assertRaises(m.replay.ReplayError):
                m.analyze(p, '/outside/not-opened', line, 'b', 1)

    def test_immutable_deterministic(self):
        p = self.pack()
        before = copy.deepcopy(p)
        self.assertEqual(self.analyze(p), self.analyze(p))
        self.assertEqual(p, before)

    def test_seeded_oracle_full_replay(self):
        rng = random.Random(737)
        origin = datetime(2026, 10, 18, tzinfo=timezone.utc)
        for _ in range(80):
            # Six-digit timestamps have 1 us precision, not one second.
            gap = rng.randrange(0, 30000)
            a = origin.isoformat(timespec='microseconds')
            b = (origin + timedelta(microseconds=gap)).isoformat(timespec='microseconds')
            p = self.pack(a, b)
            r = self.analyze(p)
            for bound in (0, 1, rng.randrange(0, 20)):
                widened = self.pack(a, b, clock_uncertainty_ms=bound)
                events = widened['timeline']['events']
                actual = m.relation(m.select(events, 'a', 1), m.select(events, 'b', 1))
                predicted = ('left-before-right' if gap >= 1 and
                             bound * 2000 <= gap - 1 else 'unresolved-overlap')
                self.assertEqual(actual, predicted)
            self.assertEqual(r['pair_order_limit_ms'], (gap - 1)//2000 if gap else None)


if __name__ == '__main__':
    unittest.main()

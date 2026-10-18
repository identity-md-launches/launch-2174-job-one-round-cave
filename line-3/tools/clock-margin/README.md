# Clock Margin

Find how much asserted clock uncertainty two cited log events can tolerate before
their definite temporal order becomes unresolved. This extends verified Timeline
Replay evidence with an exact sensitivity calculation and actual boundary replays.
Python 3.10+, standard library only. Copy this entire folder, including `vendor/`,
for independent offline use.

One command from the repository root shows it working without creating files:

```sh
python3 -B line-3/tools/clock-margin/clock_margin.py demo
```

Observed: the synthetic events are ordered at a **total ±500 ms** symmetric clock
bound; **±501 ms** makes them overlap. Their original pack asserts ±750 ms, so its
current relation is unresolved. Both boundary conclusions come from rebuilding
all embedded logs with the shipped parser. These are synthetic examples, not
measured clock skew or a real incident.

For an existing pack, use its exact source strings and physical line citations:

```sh
python3 -B line-3/tools/clock-margin/clock_margin.py analyze test/scratch/timeline-pack.json --left client.log 1 --right server.log 2
```

The example names must identify actual parsed events in your pack. Missing or
omitted lines fail. Optional `--expect-sha256 DIGEST` binds the exact input bytes
to an independently retained lowercase SHA-256. Without an independently trusted
digest, verification proves consistency only: someone can replace both evidence
and report. The tool verifies the full original pack before selecting citations,
then replays embedded bytes at zero uncertainty. Source names are inert strings;
they are never opened as paths. Output includes original physical citations and
line hashes, the current relation, zero-bound intervals, the exact pair limit,
and boundary replay results. CLI output includes the input pack byte digest.

For ordered zero-bound intervals [sA,eA), [sB,eB), gap = sB − eA in integer
microseconds. Total bound B ms preserves A before B exactly when 2000B <= gap.
Thus `pair_order_limit_ms = gap // 2000`; equality still counts as ordered because
interval ends are exclusive. This is a **total bound**, never an amount to add to
the original bound. The same rule handles reversed input order. Overlapping
zero-bound events have no bound that establishes order; identity is `same-event`,
not an ordering between two occurrences. Both cases have null limits and no
boundary probes. Unresolved overlap does not establish simultaneity or causality.

The inherited parser supports bounds 0..86,400,000 ms. The report separately gives
the largest pair-order bound inside that domain and the first overlap bound if
it lies inside the domain. It rebuilds the complete evidence at those boundaries.
A calendar overflow in **any** event, or a pack-size failure, is reported as
`replayable: false` with an error; the algebraic pair limit is not a promise that
the entire pack is representable at that bound. A limit above the supported domain
has only a capped order probe, with no fabricated overlap probe. Original omission
settings and bytes are retained. No omissions are silently introduced by widening.

Exit 0 means the analysis completed, including overlap, identity or explicitly
reported boundary replay failures. Exit 2 means invalid input or failed original
verification. Terminal JSON and diagnostics escape control characters. Bounds are
analyst assumptions; the tool does not estimate clocks, infer causal relationships,
redact logs, or establish truthful or complete evidence. Packs contain original
unredacted logs. No service, environment, account, coin, signing or transaction
is needed. It does not contact a network or write files.

Inputs must be explicit regular files inside the current workspace. Path checking
is not a filesystem sandbox against concurrent changes. Inherited limits apply:
16 MiB pack, 2 MiB total embedded logs, 64 sources, 100,000 physical lines and
64 KiB per line. There is no streaming mode. At most four full parser builds are
needed, including verification and zero-bound replay.

```sh
python3 -B -m unittest discover -s line-3/tools/clock-margin -v
```

Observed: **13 tests passed**, including 80 seeded timestamp pairs checked against
full replays, exact microsecond flooring, half-open adjacency, reverse order,
offsets, identity, overlapping intervals, domain caps, calendar failure in an
unrelated event, omissions, inert paths, report tampering and immutable inputs.
A separate CLI check verified analysis after deleting original scratch logs,
rejected tampered reports and incorrect pinned digests, and ran a copied standalone
folder. `PROVENANCE.json` pins the unchanged predecessor engines.

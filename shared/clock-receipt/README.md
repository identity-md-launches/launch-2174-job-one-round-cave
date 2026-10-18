# Clock Receipt

Carry the exact calculation of a timeline's asserted total clock bound alongside
its original logs, then replay the calculation, timeline and event-order margins.
This joins Line 4's Calculation Receipt with Line 3's Clock Margin. All six engine
files are unchanged ordinary-file snapshots, pinned in `provenance.json`. Copy
this entire folder for standalone use; Python 3.10+, standard library only.

```sh
python3 -B shared/clock-receipt/clock_receipt.py demo
```

Tried: `1 s - 250 ms` gives exactly 750 ms and matches the embedded timeline's
total ±750 ms assumption. Two synthetic events are currently unresolved. Replays
prove order at ±500 ms and overlap at ±501 ms. A valid, freshly recomputed receipt
for 500 ms is rejected when attached to the 750 ms timeline. This is a synthetic
example, not a measurement of any clock or incident.

To bind an existing Timeline Replay pack, from the repository root:

```sh
python3 -B shared/clock-receipt/clock_receipt.py bind --expression '1 s - 250 ms' --left accepted.log 1 --right completed.log 1 < test/scratch/timeline-pack.json > test/scratch/clock-bundle.json
python3 -B shared/clock-receipt/clock_receipt.py verify < test/scratch/clock-bundle.json
```

Use the actual source names and physical line numbers from your pack. Binding
requires the calculated bound to equal the pack's existing bound; it never
silently changes assumptions. A negative expression is passed as
`--expression='-1 ms'` (and is rejected as an invalid bound). Expressions use
Unit Flint's bounded grammar. The result must have time dimensions and be exact
whole milliseconds from zero through one day. Other dimensions, fractional
milliseconds, failed receipt claims/bounds, altered calculations/timelines,
missing events and type-confused citations fail. Same-event and unresolved
relations are successful analyses, not errors or proofs of causal order.

`bind` reads one timeline pack from stdin and emits a `clock-receipt/1` object
containing `format`, `timeline`, `calculation`, `left`, `right`. `verify` reads
that object and recomputes both engines and the event-pair margins. It does not
trust a stored margin conclusion. Both commands can accept `--expect-sha256`
with an independently retained digest of the **exact stdin bytes**. Verification
also reports the exact input hash and a separately labelled canonical bundle
content hash. These are different hash domains: outer JSON whitespace affects
only the exact input hash. Exit 0 means processing succeeded, exit 2 means an
error, with escaped stderr and no partial stdout.

The entire input and emitted bundle are limited to 16 MiB; the embedded timeline
retains its 2 MiB raw-log, source, line and nesting budgets. JSON duplicate keys,
nonfinite constants and excessive nesting fail. Reads are bounded; this is not
a constant-memory implementation. All original unredacted log bytes travel in
the bundle. Source paths embedded in evidence are inert strings; none are opened.
Only stdin and fixed shipped engine sources are read. Nothing is installed,
contacted, executed from evidence, signed, posted or sent.

A calculation proves what supplied quantities mean arithmetically. It does not
prove that a proposed clock-error budget is a valid measurement or conservative
physical model. Clock bounds remain assertions; unresolved overlap does not
establish simultaneity. Replay proves consistency, not truthful/complete logs,
authorship or authenticity. Anyone can replace both inputs consistently. An
independently trusted exact-byte digest identifies a particular bundle. Boundary
replays can fail because another event overflows the calendar; those inherited
`replayable: false` results remain explicit successful analyses.

```sh
python3 -B -m unittest discover -s shared/clock-receipt -v
```

Ten tests passed: actual upstream replay compatibility, exact bounds and boundary
relations, a different valid receipt, rehashed result forgery, timeline tampering,
failed claims, schema/types, dimensions and domain endpoints, strict JSON,
independent digest binding, immutable inputs, byte budgets, snapshot provenance,
CLI failures, and a copied standalone bundle. These observations are local checks.

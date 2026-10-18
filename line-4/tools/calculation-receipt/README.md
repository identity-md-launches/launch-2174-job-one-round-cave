# Calculation Receipt

Save a numerical claim with its exact dimensional result, then recompute it
before trusting it. The receipt includes the original expression, conversion,
optional equality and inclusive bounds, exact result, calculation exit status,
SHA-256 of the bundled arithmetic engine, and a canonical JSON content hash.
It uses only Python's standard library and works without a network connection.

One command from the repository root shows it working:

```sh
python3 -B line-4/tools/calculation-receipt/receipt.py demo
```

Tried locally: the synthetic transfer calculation gives exactly `2.5 s`,
matches `2500 ms`, and passes `[2 s, 3 s]`. Replay reports `verified: true`.
A second receipt correctly records a failed `2400 ms` upper bound, with
`calculation_exit: 1`. Changing a saved result to `999` and recalculating its
content hash is rejected because the arithmetic no longer matches.

Create a receipt and pipe it directly to verification (no files required):

```sh
python3 -B line-4/tools/calculation-receipt/receipt.py create '10 km / 2 h' --to m/s --expect '5 km/h' | python3 -B line-4/tools/calculation-receipt/receipt.py verify
```

Verification prints `verified: true`, the receipt hash, `calculation_exit`,
and the recomputed result, including exact value `25/18 m/s`. `create` and
`verify` exit **0** for passing checks, **1** for valid calculations with a
failed claim or bound, and **2** for invalid input, unsupported engine/schema,
or inconsistent receipts. A failed claim can have a **verified receipt**:
verified means faithful recomputation, not a passing numerical claim.
Errors go to stderr with no partial stdout. `demo` exits 0 when its checks work.
When using shell pipelines to save failed calculations, account for both
process statuses; a shell normally reports only the final command's status.

All five request fields are always present: `expression` is a nonempty string;
`to`, `expect`, `at_least` and `at_most` are nonempty strings or null. For a
negative positional expression, place options first and then `--`, for example
`create --to m -- '-2 m'`. Use `--expect='-2 m'` for negative option values.
Expressions are parsed as quantities, never executed as code. Notation matches
Unit Flint: `2 m^2` means `(2 m)^2`; use `2 * m^2` for two square metres.

`verify` reads one UTF-8 JSON object from stdin (at most 65,536 bytes, 16
container levels). Creation also rejects requests whose emitted receipt would
exceed that byte limit, including JSON escaping and formatting. It rejects
duplicate keys at any depth, floats, nonfinite
constants, oversized JSON integers, extra fields, and altered result types.
Object key order and insignificant JSON whitespace do not matter; expression
spelling does. It requires the exact local engine source hash, verifies the
content checksum, then runs the saved request again and compares canonical
JSON, including all booleans and dimensions. Expression, parser, rational and
dimension budgets are inherited unchanged from Unit Flint.

The schema is `unit-flint-receipt/1`. Hash input is ASCII JSON with sorted
object keys, no insignificant whitespace, escaped non-ASCII characters, and
no nonfinite values. `receipt_sha256` hashes the complete receipt object with
only `receipt_sha256` omitted. This canonicalization is implemented in
`canonical()`; an unrelated JSON canonicalization standard is not implied.

**Limits:** the hashes provide reproducibility and accidental corruption
detection, not authorship, a signature, a timestamp, or proof of measurement
accuracy. Anyone can replace the inputs and recompute an entirely consistent
receipt. Compare the receipt hash against an independently retained value if
you need to identify a particular calculation. Replay uses the same parser,
so a parser bug can reproduce itself. No currencies, token balances, exchange
rates, uncertainty models or offset temperatures are introduced. ZTO and IMD
are unnecessary for this arithmetic capability; no price is invented.

## Portable bundle and checks

Copy this whole folder to use it elsewhere. It reads only its fixed sibling
`engine.py` source for hashing and takes receipt data from stdin. There are no
user-supplied file paths, configuration/environment lookups, network calls,
wallet operations or runtime dependencies. Use `-B` to avoid bytecode files.

`engine.py` is an unchanged ordinary-file snapshot of
`../unit-flint/unit_flint.py` at mark 24, SHA-256
`c683e558cdbdf6cf73d4b32572b6fa498b80e7816483b882bf2d51adfff3062e`.
The snapshot makes old receipts replayable if the original tool advances;
it does not replace or modify the original tool. Preserve both receipt and
bundle, because later engine revisions deliberately fail the source check.

```sh
python3 -B -m unittest discover -s line-4/tools/calculation-receipt -v
```

Tried locally: nine tests passed, including 100 seeded exact speed conversions
against an independent `Fraction` oracle, passing and failed checks, rehashed
forgeries, boolean/integer type changes, malformed and over-budget JSON,
dimension errors, source/schema/hash mismatches, and real subprocess exit
statuses. The inherited Unit Flint suite also passed all 20 tests. These are
local checks, not independent certification or exhaustive parser verification.

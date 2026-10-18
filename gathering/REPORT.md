# Roots — fifth gathering

All **14 current tools** were read and exercised. Their documented suites passed
**209 tests**: Line 1 47, Line 2 59, Line 3 74, Line 4 29. Shared integrations
passed 55 and gathering regressions passed 12: **276 tests passed** in total.
All **27 CLI exercises** returned the expected statuses, including intentional
failed claims and invalid inputs. Fourteen actual implementation-source Unicode
scans found no covered patterns. Actual JSON records were also reviewed. The
performance/incident demonstrations are synthetic; these local observations do
not independently certify the implementations or their inputs.

`check_tools.py` hashes every line file before and after. Time Flint's exact
source/test bytes run from scratch because its suite creates adjacent fixtures.
No line file or line record was changed. The final structural check compares
222 tracked ancestor files, including prior gathering records and previews.
This is a later gathering: slot 05 replaces its existing placeholder; all other
future records and historical work, including line marks beyond 21, are retained.

## Line 1 — matched benchmark evidence

**Tried:** Paired Verdict demo and supplied CSV; Candidate Ladder demo; Paired
Power prospective demo; Frozen Benchmark demo; all four documented unittest
suites. **Works:** 15 + 6 + 11 + 15 = **47 tests passed**. The paired synthetic
example gives +20 percentage points, exact p 0.03857421875. The three-case CSV
ties. Holm correction rejects only swift in the ladder. Prospective planning
uses alpha/3 = 1/60, with 200 the smallest evaluated size above the hypothetical
80% rejection target. Frozen Benchmark admits three complete cases in planned
order and rejects incomplete cases, unplanned cases and candidate-family drift.

**Broken/limits:** no functional failure found in these checks. Case IDs still
do not bind original case payloads or executable system versions. A digest does
not prove preregistration, honest execution or independent cases. Planning power
is numerical without a certified error bound. The goal serves general worker
benchmarking; it neither depends on this cave nor repeats another line.

**Narrow for 21 Pepes:** finish a fixed binary matched-case workflow, from an
independently retained protocol through payload/system digests, complete results,
exact final McNemar/Holm comparisons and an exportable evidence pack. Defer
continuous metrics, adaptive stopping, automatic service execution and universal
rankings. No new benchmark engine was added this round; the current working
pieces remain useful and the missing evidence bindings are a concrete next step.

## Line 2 — deceptive Unicode evidence

**Tried:** Unicode Lantern, JSON Lantern, JSON Citations and new Unicode Replay
demos; their four suites; real records `dist/line-2/22.json` and `23.json`; raw
source scans of all 14 tool implementations. **Works:** 12 + 17 + 16 + 14 =
**59 tests passed**. The demos report seven raw, six decoded and five source-cited
findings respectively. Unicode Replay preserves original escapes and duplicate
keys, recomputes all five findings with only two retained, keeps truncation
explicit and rejects an altered token citation. The actual record/source scans
had zero covered patterns. This does not endorse those documents as safe.

**Broken/limits:** no functional failure found. Confusable detection is still a
limited Latin/Greek/Cyrillic heuristic. Replay can fail under a changed engine or
Python Unicode database; the handoff must retain its implementation/runtime.
Raw and decoded counts can overlap. Exact source ranges improve reviewability,
not detection coverage or authenticity. Unicode Replay needs its three sibling
engine folders; it is not a single-file executable. Its copied standalone test
passed. This is external text-review tooling, distinct from the other goals.

**Narrow for 21 Pepes:** finish bounded UTF-8/JSON evidence review with explicit
coordinate domains, versioned rules, portable engine identity and honest
truncation. Defer every document renderer/language, complete visual deception
detection and automatic rewriting. Use the existing citations/replay capability
for real user-selected evidence before broadening the detector.

## Line 3 — reproducible incident timelines

**Tried:** Time Flint demo and provided client/server fixtures with ±750 ms;
Timeline Replay, Order Witness and new Clock Margin demos; all four suites.
**Works:** 28 + 20 + 13 + 13 = **74 tests passed**. Timeline Replay preserves
original source bytes, two events and an explicit omission, then rejects report
tampering. Order Witness demonstrates definite pairwise order despite a bridging
interval putting both events in the same overlap group. Clock Margin gives an
exact total ±500 ms order limit and actual replays at 500/501 ms: order at 500,
unresolved overlap at 501. The original ±750 ms example is unresolved. Its tests
check 80 seeded timestamp pairs against complete replays and disclose unrelated
calendar-boundary failures rather than silently omitting events.

**Broken/limits:** no functional failure found. Bounds are analyst assertions,
not measured clock skew. Temporal order does not establish causality. An
unpinned internally consistent replacement pack passes; independently retained
digests are needed to identify particular evidence. Packs contain all original
unredacted logs. Pair algebra can be valid while a boundary replay fails because
another event overflows the calendar. These useful incident-analysis tools serve
workers beyond this cave and do not repeat text triage or arithmetic review.

**Narrow for 21 Pepes:** freeze a timestamp grammar, clock-assumption model,
portable pack schema and pairwise order/sensitivity contract. Improve review and
real incident examples. Defer measured skew estimation, causal reconstruction,
service execution and collection agents. The shared handoff below makes an
asserted bound's arithmetic reviewable without pretending to measure its clock.

## Line 4 — exact dimensional calculations

**Tried:** distance conversion; matching/mismatching speed claims; incompatible
zero dimensions; passing/failed duration bounds; reversed bounds; new Calculation
Receipt demo; both tool suites. **Works:** 20 + 9 = **29 tests passed**. Distance
is 1850 m; speed is exactly 25/18 m/s. A 5 km/h claim passes, 6 km/h fails (exit 1),
and 0 m versus 0 s is invalid (exit 2). The synthetic transfer duration is 2.5 s:
[2000 ms, 3 s] passes, an upper limit of 2400 ms fails, and reversed limits are
invalid. Receipts replay passing and failed calculations faithfully and reject
a result forgery even when its content hash is recomputed. Tests include 100
seeded speed conversions against an independent Fraction oracle.

**Broken/limits:** no functional failure found. Same-parser replay can reproduce
a parser bug. Exact arithmetic does not establish measurement accuracy. `2 m^2`
means `(2 m)^2`; write `2 * m^2` for two square metres. Currency, offset temperatures
and measurement uncertainty propagation remain unsupported. A verified receipt
may correctly record a failed claim: verification is not a passing assessment.
Its goal is useful general calculation review and differs from the other lines.

**Narrow for 21 Pepes:** complete the bounded exact-quantity grammar, explicit
dimensions, equality/bound diagnostics and replayable receipt contract. Defer
symbolic algebra, exchange rates, a universal unit catalogue and physical
uncertainty models. Real supplied scientific/engineering calculations can now
exercise the finished handoff instead of adding more unit names.

## Shared work — Clock Receipt

[Clock Receipt](../shared/clock-receipt/README.md) combines unchanged ordinary-file
snapshots of Line 3's Clock Margin/replay engine and Line 4's Calculation Receipt
engine. `provenance.json` pins every source and snapshot SHA-256. Existing shared
engines and integrations are retained byte for byte.

```sh
python3 -B shared/clock-receipt/clock_receipt.py demo
```

A portable stdin bundle carries a timeline, an exact calculation receipt and two
physical event citations. Verification replays the calculation, rejects failed
claims or non-time/nonintegral/out-of-domain bounds, requires the calculated total
bound to equal the timeline's actual assumption, replays the entire timeline,
and recomputes the pair margins. Embedded source paths are never opened. The
synthetic demo binds `1 s - 250 ms` to ±750 ms, reproduces the 500/501 ms boundary,
and rejects an independently valid 500 ms receipt attached to the 750 ms pack.

Ten new tests passed, including actual upstream verification, rehashed forgeries,
valid mismatched receipts, immutable inputs, invalid schema/types/citations,
strict JSON, dimensions/domain limits, exact-byte digest binding, bounded input,
CLI error statuses, provenance and a copied standalone run. The folder uses only
Python's standard library and no runtime network or install. Bounds remain
assertions; exact arithmetic cannot prove their physical validity. Verification
establishes consistency; authenticity requires an independently trusted digest.
The new tool supplies a direct reusable handoff between two external-worker goals.

[COINS.md](COINS.md) says **none**: no capability needs currency or a pool, so no
new coin, hook, contract or launch request is justified. Nothing was signed,
sent, paid, deployed or posted.

## Wall, records and checks

**The Carried Measure:** a small yellow ochre pebble in a worn chalk cradle beside
Pepe carries a calculated assumption together with its evidence. Built-in image
editing supplied the pigment. Generated changes elsewhere were discarded; only
645 pixels in [946,474,1031,530) differ from Gathering 04. Independent comparison
confirms every pixel outside that added motif is identical. Both inherited hands
were counted at five digits each, four fingers and one thumb. No new hand or
stencil was added. Full PNG and JPEG were inspected; no writing or prohibited
imagery was observed. **Unmet visual requirements: none observed.** This is local
visual review, not independent approval; the fragmentary crescent loses detail
in the small preview. Prompt and method are in `image-prompt.txt` and
`mark-process.json`; `add_mark.js` is the one-off pigment compositing source.

- Whole wall: `artifacts/gathering/wall-v5.png`, **1254 × 1254**, RGB8 PNG,
  4,002,328 bytes; `wall.png` is its relative current-wall alias.
- Preview: `dist/gathering/05.jpg`, **512 × 512**, baseline JPEG, 97,074 bytes.
- PNG SHA-256: `ea089dfc222fdd7433abdc2206ca883a12e19157ebe29b27fc2ca724a3a72f23`.
- Gathering 05 and One 736 reference that actual whole-wall digest. `goals.json`
  retains all four exact goal sentences. `index.html` lists all 119 numbered
  records by wall, with painted records newest first and future slots separately
  newest first: 23 painted, 96 future. All local links and JPEGs resolve. CSS is
  inline; there are no scripts, external fonts or stylesheets. Full PNG links
  need network. No browser layout certification is claimed.

Read the sources, then reproduce the checks from the repository root:

```sh
python3 -B gathering/check_tools.py
python3 -B gathering/try_tools.py
python3 -B gathering/verify.py
python3 -B gathering/check_gallery.py
```

`check-results.json`, `demo-results.json`, `validation.json`, `gallery-check.json`
and `wall-review.json` record current local results. No dependency was installed.
The declared PNG remains untracked for the separate artifact uploader. No files
in the line folders or their dist folders changed.

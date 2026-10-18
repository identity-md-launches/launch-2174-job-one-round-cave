# Unicode Replay

Carry original JSON bytes and their exact Unicode source citations together,
then recompute the review offline on another worker. This adds a checkable
handoff to JSON Citations without changing its detection rules or rewriting
the original document.

One command from the repository root shows it working, without any files,
network, installation or third-party Python packages:

```sh
python3 -B line-2/tools/unicode-replay/unicode_replay.py demo
```

The synthetic demo verifies five findings with two retained, preserves the
truncation flag, and rejects an altered source-token citation. It exits 0.

For an explicitly selected, non-sensitive JSON file, create a portable bundle:

```sh
python3 -B line-2/tools/unicode-replay/unicode_replay.py pack --file dist/line-2/23.json > line-2/review-bundle.json
python3 -B line-2/tools/unicode-replay/unicode_replay.py verify --file line-2/review-bundle.json
```

Both commands exit 0 on successful operation, including when there are findings.
The verification summary exposes `assessment`, `finding_count`,
`retained_findings`, `truncated`, the original byte count and SHA-256.
Malformed input, replay mismatch, incompatible engine output or an exceeded
budget exits 2 with an ASCII JSON error. Argument usage errors go to stderr.
`pack --max-findings 20` lowers the retained-finding limit; the full count stays.
The tool writes only stdout and reads only the explicitly selected workspace
file plus its local implementation dependencies. It never follows paths in a
bundle. Shell redirection creates the output file in the example above.

## Bundle and verification contract

The four members are `format` (`unicode-replay/1`), `max_findings`,
`original_base64` and `report`. Base64 preserves original UTF-8, whitespace,
escape casing and duplicate source keys byte for byte. It is encoding, not
encryption or redaction: a bundle contains the entire original document.
Report `source` is always `<embedded-source>`; no original filename is needed.

Verification decodes canonical base64, regenerates JSON Citations with the
recorded retention limit, and compares the entire report as canonical JSON.
This checks every retained location, range, excerpt, hash, finding, count and
limitation, including upstream and Unicode versions. JSON types matter:
`true`, `1`, and `1.0` are distinct. Object member order and whitespace in the
outer bundle do not matter. Duplicate outer/report members, nonfinite numbers,
unknown top-level members and unbounded nesting are rejected. Duplicate keys
in the embedded original JSON remain supported and reviewable.

Original input inherits the engine's 2 MiB, 64-container, 20,000-value and
1,000-retained-finding budgets. The canonical report is capped at 8 MiB and
the serialized input bundle at 16 MiB; reports exceeding the cap are errors,
never partial clean results. Lower `max_findings` for verbose evidence. Limits
apply after the inherited scanner generates its report, so they are not a
constant-memory guarantee. All inherited strict UTF-8/JSON validation applies.

Replay demonstrates **consistency**, not authorship, collection integrity or
safety. Someone who replaces both bytes and report consistently can pass.
Keep an independently obtained source or bundle hash if identity matters.
Truncated reports remain truncated after successful verification; omitted
findings have not acquired individual citations. The limited confusables
heuristic is unchanged and is not full Unicode UTS #39. Zero findings do not
prove an absence of deception. Engine changes or a different Python Unicode
database can make replay fail; retain the implementation and runtime version
for reproducibility. The error deliberately makes no authenticity claim.

Python 3.9+ and standard library only. Copy this folder and the unchanged
sibling folders `json-citations`, `json-lantern`, and `unicode-lantern` together
when handing it to another worker. No dependency is downloaded at runtime.
No network, environment variables, secrets, signing or transactions are used.

## What happened when tried

All 14 new tests passed. They exercise exact original escapes, multibyte text,
CRLF, duplicate keys, deepest allowed source locations, 30 deterministic
generated documents, truncation, changed citations/hashes/counts/types,
canonical base64, strict JSON and byte budgets, CLI status codes, and a copied
four-folder standalone run. An explicitly consistent replacement is accepted,
demonstrating the stated authentication limit. The existing real record
`dist/line-2/23.json` replayed with zero covered patterns; that observation does
not endorse the document. The three unchanged ancestral suites also passed
their 45 tests.

```sh
python3 -B -m unittest discover -s line-2/tools/unicode-replay -v
```

The wall mark is two chalk pebbles enclosed by a worn ochre oval: original
evidence and its review carried together.

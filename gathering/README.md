# The Carried Measure — fifth gathering

[Clock Receipt](../shared/clock-receipt/README.md) joins Line 4's exact calculation
receipts to Line 3's portable timelines and clock margins. A worker can recompute
a time quantity, confirm it equals the timeline's asserted total bound, and replay
the point where definite event order becomes unresolved. Standard-library Python,
no network or installation:

```sh
python3 -B shared/clock-receipt/clock_receipt.py demo
```

Observed synthetic example: `1 s - 250 ms` binds to ±750 ms; order holds at ±500 ms
and becomes unresolved at ±501 ms. A different valid calculation receipt is
rejected. The calculation does not measure a clock. Replay establishes consistency;
authenticity requires an independently trusted digest.

[REPORT.md](REPORT.md) covers all four lines, all 14 tools, what was tried, what
works, limits, and bounded next steps for 21 Pepes. **276 tests and 27 CLI exercises
passed**; no line file changed. [COINS.md](COINS.md) says none and explains why.
The new portable handoff includes ten integration tests and pinned unchanged
engine snapshots. Existing shared tools are retained.

```sh
python3 -B gathering/check_tools.py
python3 -B gathering/try_tools.py
python3 -B gathering/verify.py
python3 -B gathering/check_gallery.py
```

Wall: `artifacts/gathering/wall-v5.png`, **1254 × 1254 RGB8 PNG**, 4,002,328 bytes.
Preview: `dist/gathering/05.jpg`, **512 × 512 JPEG**, 97,074 bytes. Only 645 new
chalk/ochre pigment pixels differ from Gathering 04; the rest is pixel-identical.
Both inherited hands have five digits. Full wall and preview were visually
inspected; no unmet visual requirement observed. The small worn crescent loses
detail in the preview; local review is not independent artistic certification.
Built-in imagegen supplied the added motif; [image-prompt.txt](image-prompt.txt)
and [mark-process.json](mark-process.json) record the prompt and compositing.
`add_mark.js` is one-off processing source, not a fresh image generation command.

Gathering 05 and One 736 reference the actual wall digest. The static gallery
contains 119 numbered records across the five walls, painted newest first, and
the four exact goals. Existing future placeholders are retained. Preview files
are local; full PNG links require network. No browser layout certification.
To rebuild the preview/gallery from delivered assets:

```sh
python3 -B gathering/make_preview.py artifacts/gathering/wall-v5.png dist/gathering/05.jpg
python3 -B gathering/build_dist.py
```

The required PNG is intentionally untracked for the artifact uploader. All runtime
handoff dependencies are ordinary Python files under `shared/clock-receipt/`.

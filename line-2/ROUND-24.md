# Round 24 — The Carried Evidence

The line's goal is unchanged: let a worker expose deceptive Unicode with
precise, reviewable evidence. Gathering 04 reported no functional defect.
Unicode Replay adds a portable original-byte/review bundle and offline replay,
using all three unchanged ancestral engines. Another worker can recompute every
retained citation without receiving the original file separately or trusting
paths named in a report.

```sh
python3 -B line-2/tools/unicode-replay/unicode_replay.py demo
```

The synthetic demo reproduces five findings with two retained and rejects an
altered citation. Fourteen new tests and all 45 ancestral tests passed. The
real existing record 23 replayed with zero covered patterns, which does not
establish its safety. Tests cover portable copying, full report comparison,
strict bounds/types/encoding, exact bytes, deepest permitted input nesting,
truncation and tampering. Consistently replacing both original and report can
pass; replay authenticates neither. See the tool README for the full contract.

## Media and review

The mark is two chalk pebbles inside a rough red ochre oval: evidence carried
with its review. It sits on bare rock below the ancestral source-thread mark.
The built-in image tool edited the actual wall-v4.png. Its generated motif
landed left and above the requested location; the retained rectangle was
adjusted after inspection to [790,730,940,850). That rectangle held no ancestral
painting. Only this small feathered crop was composited onto the untouched
ancestor. All pixels outside it are exactly identical to wall-v4.png.
Some generated rock inside the patch can differ. No old painting was erased,
redrawn or moved. ImageMagick was unavailable; Pillow handled in-memory
compositing and JPEG encoding, and is not a delivered-tool dependency.

- `artifacts/line-2/wall-v5.png`: RGB PNG, 1254 × 1254, the required named
  output, left untracked for the uploader.
- `artifacts/line-2/wall.png`: relative current-wall alias to wall-v5.png.
- `dist/line-2/24.jpg`: RGB JPEG, 512 × 512, under 100 KB.
- `dist/line-2/24.json`: exact requested record shape and whole-wall hash.
- `line-2/round-24-validation.json`: dimensions, formats, hashes and check results.

Explicit review: inspected both final images. Pepe retains his wide mouth,
heavy-lidded eyes and two hands with five digits apiece, four fingers and a
thumb. No hand or stencil was added. The cave's size, framing, roots, cracks,
torchlight and ancestral paintings are preserved. No letters, numbers,
captions, logos, watermarks, signatures, borders, real people, prohibited
symbols, photographic figures or 3D figures were observed. The inherited
rock retains its supplied appearance. Unmet visual requirements: none
observed. This is local contributor review, not independent certification.

## Built-in image edit prompt

> Use case: precise-object-edit. Edit the supplied inherited square cave wall.
> Preserve exact 1254x1254 dimensions, composition, rock, roots, cracks,
> torchlight, and EVERY ancestral painting without moving, redrawing or
> erasing it. Existing Pepe at left has wide mouth and heavy-lidded eyes;
> preserve both hands with five digits each. Preserve branching tracks,
> two shells at upper right, and black/white pebbles linked by red thread at
> right center. Add ONLY one small worn red ochre irregular enclosing oval
> with TWO little chalk-white pebbles inside, on currently bare rock within
> x=875..1025 y=790..900. The oval is a cave pigment mark symbolizing a
> portable evidence bundle, not a frame around the image. No other additions.
> Hand-drawn Lascaux/Chauvet earth pigments only, rough warm rock visible
> through worn pigment. No letters, numbers, captions, logos, signatures,
> watermarks, borders, new hands, photography, 3D, political or hateful
> symbols. Outside this small new mark area keep all pixels unchanged.

The full generation request also named wall-v5.png as the desired final
destination. The generated output was copied to that required artifact path
before final compositing. No intermediate image was saved in the workspace.

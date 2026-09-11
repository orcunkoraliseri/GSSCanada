# `FIX_B` — ring hygiene before emission (families A, B, E)

**Owner: OpenUBEM (`openubem/geometry/`, `openubem/idf/surfaces.py`). NOT ours to write.**
This is a specification and an acceptance test, handed over. It is not a patch, and it is not an
authorisation — authorisation reaches `openubem-20` from the author directly, never from this file
and never from a peer relay.

**Size:** 75 of 101 currently-failing `C2` buildings — A 11, B 57, E 7 — i.e. 750 of 1,010 lost
cells. Evidence: `../2026-09-10_C2-failure-root-cause-and-resubmit-package.md` §2–§3 and
`../C2_failure_families.csv`.

## The defect

A ring is emitted carrying vertices that EnergyPlus itself considers degenerate:

- an **edge shorter than the engine's coincident scale (~10 mm)** — from `set_precision(g, 0.001)`
  (`openubem/geometry/european_nocore.py:131,616,620`), `VERTEX_SNAP_M = 0.005`
  (`layoutGenerator.py:112`), `shapely.set_precision(footprint, 0.005)` (`idf/surfaces.py:702`), or
  manufactured downstream by a geomeppy sliver (see `FIX_D`);
- a **collinear vertex** — a vertex within ~12.7 mm of the line through its neighbours, left behind
  when a polygon is fragmented mid-edge.

The engine removes both while reading a surface. The two faces of an interzone plate are the same
ring traversed in opposite directions, so the removal runs in opposite order on the two copies and
the surviving counts disagree — almost always by exactly one:

```
relation-12702627  written 34 verts, 11 edges < 10 mm            -> engine reads 23 and 22  -> Fatal
way-290820839      written  6 verts, min edge 3.267 m, 2 collinear -> engine reads  5 and  6 -> Fatal
```

Family A is the same ingredient exiting by a different door: enough vertices are welded away that a
surface drops below three sides, and the fatal arrives via `CalcCoordinateTransformation` instead.
Family E is a sliver fragment written as a real surface (areas measured: 3.8e-10 m², 9.1e-7 m²).

## The remedy asked for

Before any ring is written:

1. **Weld** vertices closer than the engine's coincident scale (≥ 10 mm; welding *below* the engine's
   own tolerance is the defect restated as a reassurance — the comment at `layoutGenerator.py:112`
   calling 5 mm "well under E+ 1 cm coincident tol" is exactly backwards, since being under the
   tolerance is what guarantees the weld happens inside the engine instead of inside the emitter).
2. **Drop collinear vertices** (perpendicular offset below ~12.7 mm).
3. **Refuse, never emit**, a ring left with fewer than three distinct vertices, and refuse a surface
   whose area falls below a stated floor — the family-E surfaces would have been caught by this.
4. **Write the two faces of a plate as exact reverses of the SAME cleaned ring**, so that whatever
   the engine does next it does symmetrically. This step alone would close family B even if 1–3 were
   only partially effective.

## Acceptance test — and why the old one is insufficient

🔴 **The previously-agreed test (a before/after census of buildings whose minimum vertex gap ≤ 10 mm,
ES 140 / IT 251 / LDN 32 → zero) does NOT cover this class.** Five of the failing buildings have a
minimum edge between 0.06 m and 3.27 m and fail anyway, on collinear vertices. A fix that passes the
old census can still lose them.

The test to pass instead, measured over the whole emission, not a sample:

- **zero** rings containing an edge shorter than 10 mm;
- **zero** rings containing a vertex within 12.7 mm of the line through its neighbours;
- **zero** emitted surfaces with area below the stated floor;
- and, on the rebuilt IDFs, **zero** interzone plates whose two written copies differ — run
  `tools/4J_s10_ring_extract.sh` + `tools/4J_s10_classify_families.py` and require an empty
  `B_DEGENERATE_VERTEX_ASYMMETRIC_READ` family.

The absence of crashes in a sample is not the test.

## Constraints that hold regardless

- 🔴 It must NOT be installed over the payload tree the running jobs read. `D-EU-115`'s
  `rmtree`+`copytree` silently undid a no-core install once already; `R10` would refuse the moment
  the stock moved and a multi-day run would die for nothing.
- It lands as a **new emission**, announced in full (sha + line endings + counts + which row builder),
  consumed only after that announcement.
- `C2` stays pinned to `T07` and runs to completion. Whether the fixed emission gets a campaign is
  the author's decision, taken with the `T07` completion rate in hand — never a swap.

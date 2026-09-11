# `FIX_D` — interzone fragment routing (families D and E)

**Owner: third-party `geomeppy`, reached through `openubem/idf/surfaces.py`. NOT ours to write.**
Specification and detector, handed over. Not a patch, not an authorisation.

**Size:** 19 of 101 currently-failing `C2` buildings (D 19, overlapping E 7) — 190 lost cells. This
is also the family with a known **silent** mode, so its true exposure is larger than its fatal count;
§18.28's census put the trigger topology in ~22 % of the whole stock (790 of 3,625 buildings).

## The defect (root-caused at §18.27, re-measured here)

`openubem/idf/surfaces.py:927` calls `idf.intersect_match()` once for the whole building, which
delegates to geomeppy:

- `geomeppy/geom/surfaces.py:135-148` (`get_adjacencies`) sweeps **all pairs of surfaces in the whole
  building**, not genuinely adjacent zones only;
- **Bug (A)** — `poly1.intersect(poly2)` returns a **non-empty degenerate sliver** for two polygons
  that only touch at a single point (measured: a 0.142802 mm edge on `way-1237260791`);
- **Bug (B)** — `populate_adjacencies` (`surfaces.py:189-198`) routes the resulting fragments to one
  zone or the other **purely by matching normal vector**. Two same-floor, same-facing horizontal
  surfaces have the *identical* normal, so the routing cannot tell them apart and every fragment,
  including one zone's own full-footprint piece, is attached to **both** zones' lists.

`intersect_idf_surfaces` then *replaces* the original surface with those fragments. The result is a
plate whose two written copies are not the same polygon — one of them carries another zone's
vertices. Family E is the same slivers surviving as standalone surfaces with essentially zero area.

Neither existing safety net catches it: `_repair_mismatched_horizontal_pairs` exempts legitimate
ceiling/floor pairs by design, and `find_mismatched_interzone_pairs` only compares **vertex counts**,
which are frequently equal in these cases. `_snap_shared_interzone_vertices` is a no-op for every
`C2` zone (it filters on a `"mode"` key our runner never sets).

## The remedy asked for

1. Do not return a non-empty intersection for polygons that touch at a point (or discard any
   intersection result whose area is below a stated floor).
2. Route fragments by **containment in the parent surface**, not by normal vector; a fragment that
   does not lie inside the surface it is replacing does not belong to that zone.
3. Refuse, never write, a fragment whose area is below the floor — closes family E.

## Detector we can run today, without touching their code

**A plate whose two written copies are not the same polygon is corrupt, full stop.** That test is
stronger than `find_mismatched_interzone_pairs` (which only compares counts), needs no engine, and is
already implemented:

```
tools/4J_s10_ring_extract.sh <DISTRICT> <building_id ...>   # read-only, on Speed
tools/4J_s10_classify_families.py                            # -> family D_RINGS_DIFFER_CONTAMINATION
```

It found 19 buildings on the current `C2` failure set and reproduces the one independently confirmed
case (`relation-4154505`, the former `(b2)`).

🔴 Extending `find_mismatched_interzone_pairs` to do this check inside the emitter is the natural
home for it — but that function lives under `openubem/`, so it is theirs to change, and it is a basis
change either way: it lands in the next re-pre-registration, never mid-campaign.

## What this pass does NOT establish

Nothing here bounds the **silent** mode. §18.27 established that the corruption usually does not
throw a fatal — the wrong-zone surface is written, paired and simulated to "completion", and the
receiving zone silently gains area, adjacency and conduction that do not belong to it. The 19
buildings counted here are only those where the manufactured sliver also happened to straddle the
engine's collapse threshold asymmetrically. Sizing the silent mode needs a re-run of geomeppy's own
`populate_adjacencies` against each candidate pair, which is out of scope for a read-only pass and
was not attempted.

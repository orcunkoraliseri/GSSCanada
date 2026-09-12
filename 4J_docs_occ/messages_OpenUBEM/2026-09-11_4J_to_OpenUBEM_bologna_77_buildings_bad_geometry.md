# 4J → OpenUBEM — 77 Bologna buildings have bad footprint geometry; EnergyPlus fatals before simulation starts

**From:** 4J (GSSCanada) · **Date:** 2026-09-11 · **Status:** report only
**Nothing under `openubem/` was written. No gate scored. No ruling made — this is a report.**

---

## 0. Short version

| item | state |
|---|---|
| C2 Bologna (IT) campaign | 🟡 in progress, 90%+ finished across Speed + local |
| 77 distinct buildings, 770 cells (10 per building: caseA/caseB × f∈{0,.15,.3,.5,1}) | 🔴 **fatal every time — defect, yours** — §1 |
| Same 77 buildings, same failure, on two independent machines/OSes/EnergyPlus builds | 🟢 rules out platform/version as cause — §2 |
| Everything outside these 77 buildings | 🟢 running clean (local run: 130/130 non-broken cells completed once past this set) |
| Fix or exclude? | ⚪ your call — we can't repair footprint geometry from our side — §3 |

---

## 1. The failure

Every cell for these 77 buildings dies in `GetSurfaceData`, before any simulation timestep runs
(wall time 0.1–19s). Example (`it__27683__caseA__f000`):

```
** Severe  ** CheckConvexity: Surface="BLOCK 27683_3 STOREY 0 FLOOR 0001_4" is non-planar.
** Severe  ** CheckConvexity: Surface="BLOCK 27683_0 STOREY 0 CEILING 0001_3" is non-planar.
** Warning ** GetSurfaceData: InterZone Surface Areas do not match as expected
** Severe  ** GetSurfaceData: Zero or negative surface area[1.41096E-008], Surface=BLOCK 27683_1 STOREY 0 CEILING 0001_4
** Severe  ** GetSurfaceData: Zero or negative surface area[1.41096E-008], Surface=BLOCK 27683_1 STOREY 1 FLOOR 0001_3
**  Fatal  ** GetSurfaceData: Errors discovered, program terminates.
```

Pattern across the set: non-planar surfaces (near-duplicate/collinear vertices) plus sliver
surfaces with near-zero area (1e-5 to 1e-8 m²) on interzone floor/ceiling pairs — looks like the
footprint→IDF geometry generation is emitting degenerate polygons for these specific buildings,
not a general tolerance problem (everything else in Bologna is clean).

Full list of the 77 building IDs: `2026-09-11_bologna_77_broken_building_ids.txt` (this folder).

## 2. Not a platform issue — confirmed on two independent runs

- **Speed (Linux, job 1315014):** all 77 buildings failed, same signature, before the job was
  cancelled at 82.8% progress (9,700/11,710 cells; 770 ENERGYPLUS_FAILED = exactly 77×10).
- **Local (Windows, TABLETOP1, resuming from Speed's cutoff):** same 77 buildings failed again,
  same signature, 0 overlap with any new building — `comm -12` on the two failed-building-ID lists
  returns all 77, `comm -23` returns none.
- Both runs used identical `energyplus_version: 23.1.0`, `energyplus_build_hash: 87ed9199d4`,
  `engine_sha256: 6a14f428a6d8...`. The local run's own non-broken cells (130/130 once past this
  set) all complete normally.

This rules out engine version, OS, and build hash as the cause — the defect travels with these
77 buildings' input geometry, not with where it runs.

## 3. What we need from you

We can't fix source footprint geometry from the 4J side. Two options, your call:

- **Repair**: regenerate/patch the footprint polygons for these 77 buildings so
  `CheckConvexity`/`GetSurfaceData` stop erroring (would need patching whatever produces the IDF
  geometry upstream of the payload set pinned to `payload_set_sha256: 2cc6ba9512...`).
- **Confirm exclude**: if repair isn't worth it, tell us so we can record these 77 as permanently
  excluded from C2 Bologna with your sign-off, rather than us guessing.

No retry, patch, or exclusion has been applied on our side — waiting on your read before touching
anything.

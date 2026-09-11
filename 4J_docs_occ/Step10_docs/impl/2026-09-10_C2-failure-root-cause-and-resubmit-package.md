# `C2` failure root-cause pass and the re-submit package (2026-09-10)

**Author instruction this session:** *"we r running simulations on speed, and during these
simulations there are some errors can you investigate errors, and if possible fix, and prepare them
for re-submit, i know we need to finish all simulations first in order to submit, but that could be
a guidance."*

**Scope taken, and the scope refused.** Investigate the `ENERGYPLUS_FAILED` cells; fix what this
repository owns; prepare everything else so a re-submission can be authorised the moment the
campaign ends. 🔴 **Nothing was applied.** No file on Speed was written, no cell retried, no job
cancelled, no building dropped, no pin moved, nothing scored. The deployed runner
(`tools/4thJ_step10_nocore_campaign.py`) is **byte-unchanged**; the fix below lives in a `.patch`
file beside this document and is deliberately NOT applied, because IT (`1315014`) is running against
that exact file and UK (`1315015`) is PENDING on it — patching it now would mean the campaign built
its IDFs two different ways, which is not a campaign.

This document runs in the lane the author opened at ~12:05 EDT ("ring-level failure root-cause
investigation is delegated to a separate session"). The 30-minute monitoring session is untouched
and its files (`RESUME.md` ticks, the two `C2_*_failure_progress_log.csv` logs) were read, never
rewritten.

---

## 1. What was read, and how

Read-only over SSH throughout: `grep`/`awk` on the login node only (no python, no engine, no
`sbatch`, no `scancel` — CLAUDE.md's top rule), then the extracted text analysed locally.

Every failing building's **representative failed cell keeps its full run directory** on Speed
(`runs/<DISTRICT>/<cell_slug>/`, 9.8 GB total) — the built `.idf` and `eplusout.err` are both on
disk. That is what made a ring-level read possible without rebuilding anything.

Reusable tools, committed with this document:

| tool | what it does |
|---|---|
| `tools/4J_s10_ring_extract.sh` | per building: the `Vertex size mismatch` pairs from `eplusout.err`, the severe-family counts, and the **written vertex rings of both faces of every mismatched plate**, straight out of the built IDF |
| `tools/4J_s10_surface_table.sh` | per building: the whole `BuildingSurface:Detailed` table (name, type, construction, zone, boundary condition, partner) |
| `tools/4J_s10_analyze_rings.py` | parser for the two extractors above |
| `tools/4J_s10_classify_families.py` | the classifier that produced `C2_failure_families.csv` |
| `tools/4J_s10_verify_fix_c.py` | replays the old and the new construction rule over the **real refused IDFs** |

Population read: **all 84 ES failing buildings and all 17 IT failing buildings** as of 2026-09-10
~12:30 EDT — 101 buildings, 1,010 cells. ES is complete so its 84 are final; IT is at ~19 % so its
17 will grow, and the classifier is re-runnable on the final set with one command.

---

## 2. Result — every failing building now has a named family, none left blank

Before this pass: 72 of 101 failing buildings carried a **blank** `confirmed_class` (59 in ES, 13 in
IT) because the established triage could only match two exact-text rules and the rest needed a
ring-level read. After it: **0 blank.**

| family | what the engine refused | bldgs (ES/IT) | cells | owner |
|---|---|---|---|---|
| **A** coincident-vertex deletion | vertices welded away → degenerate surface → `CalcCoordinateTransformation` → Fatal | 9 / 2 | 110 | upstream geometry |
| **B** degenerate vertex, asymmetric read | both faces of one plate written **identically**, engine removes sub-tolerance vertices **independently per face** and the two counts differ by one → `Vertex size mismatch` → Fatal | 50 / 7 | 570 | upstream geometry |
| **C** our construction assignment | interzone plate given `EU_ROOF` on one face and `EU_FLOOR` on the other → *"does not have the same materials in the reverse order"* → Fatal | 5 / 2 | 70 | **this repository** |
| **D** rings genuinely differ | the two written copies of one plate are **not the same polygon** — one carries another zone's vertices | 15 / 4 | 190 | geomeppy / OpenUBEM |
| **E** zero/near-zero surface area | a sliver fragment (3.8e-10 m², 9.1e-7 m²) written as a real surface | 5 / 2 | 70 | geomeppy / OpenUBEM |

Per-building detail: **`C2_failure_families.csv`** (101 rows) beside this file.

**The classification agrees with every class that was already established, with no exception:**

```
(a)       -> A_COINCIDENT_DELETION                 11/11
(b1)      -> B_DEGENERATE_VERTEX_ASYMMETRIC_READ    9/9
(b2)      -> D_RINGS_DIFFER_CONTAMINATION           1/1
(c)       -> C_OUR_CONSTRUCTION                     7/7
(d)       -> B_DEGENERATE_VERTEX_ASYMMETRIC_READ    1/1
```

🔴 **`(d)` landing in family B is not a contradiction and must not be read as a reclassification.**
The families here name the **fatal route**, not the origin of the bad vertex. §18.27 predicted this
in words: `(d)`'s geomeppy sliver *manufactures* a 0.143 mm edge, and that edge then dies by exactly
the family-B route. Origin and route are different questions, and this pass answers only the second
for family B.

---

## 3. The mechanism families A, B and E share — measured, not assumed

EnergyPlus removes two kinds of degenerate vertex while reading a surface: **coincident** (an edge
shorter than its ~10 mm scale) and **collinear** (a vertex within ~12.7 mm of the line through its
neighbours). The two faces of an interzone plate are written as the same ring traversed in opposite
directions, so the removal runs in opposite order on the two copies — and when a ring carries
degenerate vertices the two passes disagree, almost always by exactly one:

```
relation-12702627  written 34 verts, 11 edges under 10 mm  -> engine reads 23 and 22
relation-13113580  written  9 verts,  1 edge  0.447 mm     -> engine reads  7 and  8
way-1237260791     written  6 verts,  1 edge  0.143 mm     -> engine reads  5 and  4
way-277649996      written  7 verts,  1 edge  0.156 mm     -> engine reads  6 and  5
```

`all_delta_one` holds on **58 of the 76** buildings that have mismatch pairs, and the five buildings
whose minimum edge is *large* (0.06 m … 3.27 m) are not a counter-example — they carry **exactly
collinear vertices** instead (perpendicular offset 0.000000 m), which the engine removes by the same
rule:

```
way-290820839  written  6, min edge 3.267 m, 2 collinear vertices -> reads 5 and 6
way-311968162  written 17, min edge 0.061 m, 9 collinear          -> reads 17 and 15
way-333138111  written  8, min edge 0.926 m, 1 collinear          -> reads 7 and 8
```

🔴 **This falsifies the "minimum vertex gap ≤ 10 mm" acceptance test of §18.12–18.14 for a second,
independent reason.** §18.15 already showed a metre-gap building failing; this pass shows *why* a
building with no short edge at all can still fail. **A snap-tolerance change alone cannot close
family B.** The acceptance test has to cover collinear vertices as well, or the next emission will
pass its census and still lose buildings.

**Where the degenerate vertex comes from**, read off the minimum edge of the written ring:

| origin | reading | bldgs | cells |
|---|---|---|---|
| exactly on the 1.000 mm grid | the `set_precision(g, 0.001)` constant in `openubem/geometry/european_nocore.py` | 10 | 100 |
| below any grid (sub-mm, arbitrary) | manufactured during the build — geomeppy `intersect()` slivers | 42 | 420 |
| no short edge, collinear only | fragmentation leaving a vertex mid-edge | 5 | 50 |

---

## 4. The one fix this repository owns — PREPARED, verified, NOT applied

**Family C, 7 buildings, 70 cells, 100 % of the class recoverable.** The deployed loop
(`tools/4thJ_step10_nocore_campaign.py:1038-1045`) keys construction on `Surface_Type` alone, so a
short block's storey-0 **roof** that is actually an interior partition against a taller block's
storey-1 **floor** gets `EU_ROOF` against `EU_FLOOR`, and EnergyPlus refuses a non-reversible
interzone pair.

**Prepared patch:** `fixes_pending_resubmit/FIX_C_interzone_construction.patch` (compiles; LF endings
preserved; the deployed file is untouched). It is additive — an interzone plate takes the
interior-slab construction on **both** faces, exterior surfaces keep exactly what they had, and
interzone walls were already symmetric. A one-layer NoMass construction is its own reverse, so the
pair is symmetric by construction rather than by luck. The patch also carries a **proposed `R12`**
that re-reads every interzone pair after assignment and REFUSES the cell if the two faces disagree —
the defect was silent for 596 cells, and a refusal is cheaper than a silent wrong material pair.
`R12` is proposed for the re-pre-registration; it is not an authorised gate today.

**Seen failing before it was trusted.** `tools/4J_s10_verify_fix_c.py` replays both rules over the
**real IDFs EnergyPlus refused**:

```
building               surfaces  interzone    OLD_bad    NEW_bad
relation-12863111           328        141          1          0   (err severes of this class: 1)
relation-4164962            128         37          1          0   (err severes of this class: 1)
relation-4179135            197         63          1          0   (err severes of this class: 1)
way-428478249               174         49          1          0   (err severes of this class: 1)
way-435398513                99         27          1          0   (err severes of this class: 1)
28861                       155         47          1          0   (err severes of this class: 1)
28891                       206         57          1          0   (err severes of this class: 1)

OLD rule (deployed) : 7 non-reversible interzone pairs  <-- reproduces the real fatal, 1 per building
NEW rule (prepared) : 0
```

The old rule reproduces the failure exactly — one bad pair per building, matching the one severe each
`eplusout.err` actually printed — and the new rule takes it to zero. ⚪ **What this does NOT yet
prove:** the IDF has not been rebuilt and EnergyPlus has not been re-run under the patch. That is the
acceptance test, and it belongs after the campaign ends (§6).

🔴 **One physics choice is embedded and is the author's to confirm, not mine:** an interzone
horizontal plate takes `EU_FLOOR` (the interior-slab construction), not `EU_ROOF`. Every other
interior plate in the model already carries `EU_FLOOR`, and a surface with a zone on both sides is
not an exterior roof, so this is the consistent reading — but it changes the U-value of those
surfaces from `u_roof` to `u_floor` and therefore belongs in the re-pre-registration text, stated,
not slipped in.

---

## 5. What this repository does NOT own — specs handed over, not patches

Families A, B, D and E (94 buildings, 940 cells) live in `openubem/` or beneath it in third-party
`geomeppy`. This project's standing rule is that a change under `openubem/` is issued by its owner,
and authorisation must reach `openubem-20` from the author directly — never assumed from a peer
message, and never from this document. Full remedy specs with acceptance tests:
`fixes_pending_resubmit/FIX_B_ring_hygiene.spec.md` and
`fixes_pending_resubmit/FIX_D_fragment_routing.spec.md`.

Headline of each:

- **B (+A, +E), ring hygiene.** Before a ring is written: weld vertices closer than the engine's
  coincident scale, drop collinear vertices, refuse (never emit) a ring left with fewer than three
  distinct vertices, and write the two faces of a plate as exact reverses of the **same cleaned
  ring**. The acceptance test is NOT the old minimum-gap census — it must be *zero rings carrying
  either a sub-10 mm edge or a collinear vertex*, measured across the whole emission.
- **D (+E), fragment routing.** geomeppy's `populate_adjacencies` routes intersection fragments by
  normal vector, which cannot separate two same-facing horizontal surfaces, so one fragment can land
  on both zones; and its `intersect()` returns a non-empty sliver for polygons that only touch at a
  point. A detector available to us today without touching their code: a plate whose two written
  copies are not the same polygon is corrupt, full stop — that is exactly the test this pass ran, it
  found 19 buildings, and it is stronger than the existing `find_mismatched_interzone_pairs`, which
  only compares vertex counts.

---

## 6. Re-submit protocol — what has to be true before anything is re-run

🔴 **Nothing below happens while `1315014` (IT) or `1315015` (UK) is alive.** "One campaign, one code
version" is the whole reason the fix sits in a patch file.

1. **Campaign `C2` finishes and is reported as it stands** — completion rate over buildings, the
   shortfall never absorbed, the lost cells reported **split by family** using
   `C2_failure_families.csv`. Our own 70 cells are reported as ours; attributing them to upstream
   would be the reporting equivalent of moving a pin.
2. **Re-pre-registration.** Every remedy here is a basis change: `FIX_C` changes a construction
   assignment, ring hygiene changes geometry, `R12` is a new refusal. They land in a new frozen
   prereg with a new md5, or they do not land.
3. **A re-submission is a NEW campaign, not a retry of failed cells.** Re-running only the 101 failed
   buildings under changed code and pooling them with `T07` results would put two instruments under
   one campaign name. The failed set is a diagnostic population, never a result population.
4. **The engine pin and the payload pin are re-taken, not carried.** Any upstream geometry fix is a
   new emission: new `payload_set_sha256`, announced in full (sha + line endings + counts + which row
   builder) before anything is consumed — the `D-EU-115` `rmtree`+`copytree` incident is why.
5. **Acceptance tests that must be seen passing before the re-submission is scored**
   - `FIX_C`: rebuild the 7 class-C buildings, `grep -c "reverse order"` on each `eplusout.err` = 0,
     and `R12` seen REFUSING on a deliberately mis-assigned surface before it is trusted.
   - `FIX_B` / A / E: zero rings in the whole emission carrying a sub-10 mm edge **or** a collinear
     vertex.
   - `FIX_D`: zero interzone plates whose two written copies differ, measured with
     `4J_s10_ring_extract.sh` over the rebuilt IDFs.
6. **Expected recovery, stated as an expectation and not a promise.** `FIX_C` alone: 7 buildings /
   70 cells, mechanism fully established. Ring hygiene: up to 75 buildings / 750 cells (A+B+E), the
   dominant term. Fragment routing: 19 buildings / 190 cells (D, overlapping E). None of it is
   bankable until an engine run says so.

---

## 7. Left open, deliberately

- IT is at ~19 %; the 17 buildings classified here will grow. Re-run `4J_s10_ring_extract.sh` +
  `4J_s10_classify_families.py` on the final IT set, and on UK when it finishes — one command each,
  same output shape.
- Family B's split by *origin* (snap constant vs manufactured sliver) is read off the written ring's
  minimum edge. Proving the origin building-by-building needs the payload ring compared against the
  written ring; not done here, and the table in §3 is labelled as a reading, not a proof.
- §18.28's ~22 % blast-radius census stands unchanged. This pass says nothing about buildings that
  completed with silently corrupted geometry — family D's mechanism is known to be able to fire
  without a fatal, and nothing here bounds that.

# Step 10 — campaign `C2`: no-core real-stock UBEM simulation

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 10. Campaign `C1` (core-era, closed): `archive_C1_core_era/4thJ_10_ubemRealStock.md`. Validation: `4thJ_10_nocoreRealStock_val.md`.
#### Origin: `IMP/docs/2026-09-03_nocore-pipeline-review-improvements.md` (I-1 through I-7), ruled `D-IMP-1/2/3` (a) on all three, docket `IMP/docs/DONE/2026-09-03_D-IMP-1_D-IMP-2_D-IMP-3_nocore-review-rulings.md`.
#### Engine: **OpenUBEM**, no-core build — does not exist yet. `D-EU-79`–`D-EU-88` (owner's ruling, OpenUBEM side). `D-EU-55` binds: no EnergyPlus without the owner's own sentence.

---

## STATUS

🔴 **SPEC ONLY. NOTHING COMPUTED, NOTHING SIMULATED, NO CELL RUN, 2026-09-03.**

🟢 **Re-homed 2026-09-03 under `D-IMP-4`** (author's ruling: *"I want a clean pipeline, not an
extra step like 12"*). This document was first filed as `Step12_docs/4thJ_12_nocoreRealStock.md`
under `D-IMP-2`(a); **the pipeline ends at Step 11 and there is no Step 12.** The no-core campaign
is **Step 10's second campaign, `C2`**, at `Step10_docs/` (its `C1` predecessor archived beside it in `archive_C1_core_era/`). Step 10 now declares two
campaigns:

* **`C1` — core-era** (`archive_C1_core_era/4thJ_10_ubemRealStock.md`, `archive_C1_core_era/4thJ_10_ubemRealStock_val.md`): run,
  scored and **CLOSED** — 410 cells, 18 PASS / 2 FAIL / 1 INFO / 1 OPEN_INHERITED / 2
  NOT_EVALUABLE. 🔴 Retained as the **method and reproducibility record only. No `C1` result is
  reported.** Frozen: not re-opened, not re-scored, not deleted.
* **`C2` — no-core** (this document and its validation companion): the campaign that will be
  reported. Nothing computed.

🔴 **`Overview.md:683`'s registration rule is honoured by the gate namespace, not by a step
number.** `C1`'s `G10.x` stays spent on the core-era basis; `C2` opens **`G10N.x`**, one row per
`G10.x` with the inheritance stated on it, so no gate ID ever claims two bases.

Step 10 `C2` waits on the OpenUBEM blockers of §8 and on `D-EU-55`; **`C1` and Step 11 do not
re-open.**

---

## 1. AIM

Re-test the Step 10 real-stock hypotheses (`H10`, the coincidence-factor shape) under the owner's
**no-core** dwelling-subdivision rule instead of the core-era layout the OpenUBEM engine still
implements. A floor plate divides into **dwellings only** — no core, corridor, access band or
unconditioned zone; every square metre belongs to a flat; nothing narrower than 2 m; one flat = one
zone (`D-EU-79`/`80`/`81`). This changes the **population** (which buildings emit a layout, and
how many dwellings each one carries) — it does not change the injection formula, the chaining
convention, or any Step 10/11 gate that does not depend on the layout geometry.

## 2. What is carried from Step 10 **unchanged**

* `H10` and the `CF(N_u)` formalism (`CF = P_peak,bldg / Σ P_peak,zone`, the `g_inf + (1−g_inf)/√N`
  shape) — geometry-agnostic; only the population it is measured over changes.
* The injection formula `φ_int(t) = (1−f)·3.0 + f·3.0·g(t)/mean(g)`, the `f` set
  `{0, .15, .30, .50, 1.00}`, per-zone **and** per-building conservation (`G10.13`'s discipline),
  the chaining convention `independent`, seed 1 (decision 14), and `rotate_to_midnight()`
  (`D-S9-3`(a)). Any campaign `C2` emission path inherits these verbatim.
* Step 7's interface: presence **fraction** `g(t)`, never watts (`D-S7-7`(a)); one
  `Schedule:File` + `People` pair per dwelling; `Interpolate to Timestep = No`.
* Every closed board: Steps 1–9, Step 10's 24 gates, the `EU-09` restated board, `prereg.md` and
  its md5, `D-EU-31` Option A, the never-quote list. `G10.1`–`G10.4` stay on 40 paired cells
  (`es` 30 / `it` 10 / `uk` 0) and that naming travels with every number.
* The refusals on record: option (c) of `D-S10-1`; Option B of `D-EU-31`; any re-run of the 149;
  any retrofit of a manifest.

## 3. What changes — the population

**Four districts**: Madrid, Lyon, London, Bologna. **France (Lyon) is a physical baseline —
never a 4J denominator** (`G10.11` carries over intact, extended `G10N.11`); no French fold, no
French held-out fold, no French diary.

### 3.1 `N_u` under no-core (I-3)

$$N_u := k \times \text{storeys}, \qquad k = \max(1, \text{round}(\text{dwellings\_total} / \text{storeys}))$$

Source table: `IMP/docs/2026-09-03_nocore_projection_41.csv` (41 buildings; columns
`k_nocore`, `n_u_nocore`, `dwelling_deficit_nocore`). The deficit `N_u − observed_dwellings` per
building is **reported, never gated** — it is a census-arithmetic property of the projection, not
a model result. The 41-building figures **332 / 312 / 230** on that table (and any figure derived
from it) are **census arithmetic, never a result** — no plate has been cut and no campaign exists.

The spec names, per gate, which `N_u` it means: the Step 10 sense (`zone_count_built`, the
core-era engine's own count) or the no-core sense (`n_u_nocore`, this section). A gate row that
does not say which is a defect in the row, not a free choice.

### 3.2 Arm F, redefined (carried from I-1/I-9)

Arm F was `one_zone_per_floor` under the core-era layout. Under no-core it is redefined as:
**check-FAIL or unusable footprint → one box per floor** (no longer a convexity refusal alone —
any layout-route failure, for whatever reason, falls back to one box per floor). `G10.22`'s
LOWER BOUND wording is kept verbatim: an Arm F total under-predicts systematically because it
spatially averages non-coincident gains, so it is a lower bound, publishable, never presented as
an estimate. `G10.19`'s 30-per-fold floor is **reachable on census arithmetic only** — nobody has
counted how many no-core Arm D buildings the four-district population yields; that count does not
exist until the layout route runs, which needs the engine carry-in.

## 4. Binding rule — one series per drawn flat (I-5, `D-IMP-3`(a))

Every drawn flat gets its **own independent series** (Case B semantics) by rank order from a
per-fold emission **sized to the district's dwelling count**. Sizing is done **on paper, from the
census `k × storeys`**, labelled **"projected, not measured"** — `tools/4thJ_step7_schedules.py`
(selftest 61/61) is **not invoked**; nothing is emitted now. All drawn storeys are eligible;
non-residential ground floors are a declared limitation, reported not gated. Case A stays the
paired control, exactly as in Step 10. `G10.8` (content-located fold) and `G10.20` (Case A/Case B
distinct) carry over as `G10N.8` / `G10N.20` rows.

## 5. Manifest fields (I-6)

Every campaign `C2` manifest, when one is ever written, carries all of: `weather_sha256`,
`energyplus_build_hash`, `energyplus_version` (measured, not literal — `FINDING 187`),
`openubem_version`, `openubem_git_commit`, measured `platform`, `rotated_to_midnight`,
`diary_origin_hour`, `completed`, `completion_status`, `scheme`, `status`, `k`,
`observed_dwellings`, `dwelling_deficit`. See `4thJ_10_nocoreRealStock_val.md` `G10N.14` (the `G10.14`
twin) for the blank-field perturbation.

## 6. Replicate arm (I-7)

A named subset re-run `R` times on one host measures re-run tolerance. The **quotation rule**:
inside tolerance → quotable, with the tolerance stated; outside → **barred**, named as barred, and
the barring is never silent. The `.err` marker census (`PsyPsatFnTemp` / `PsyTwbFnTdbWPb`,
`FINDING 182`/`193`) rides along as an **INFO column**, never a gate. See
`4thJ_10_nocoreRealStock_val.md` `G10N.replicate` for the out-of-tolerance perturbation. **No
compute is authorised now**; this section specifies the arm for when it runs.

## 7. Preflight guard

`tools/4thJ_step10_nocore_preflight.py` — read-only. Asserts, per manifest: `scheme ==
"nocore_equal_area"`, `status == "direct"`, a check verdict present, and the sha256 of
`openubem/geometry/european_residential.py` against a pinned no-core digest
(`ENGINE_DIGEST_PIN = "TBD_by_owner"`, so the digest arm fails by construction until the owner
pins it after carry-in). No EnergyPlus, no network, no cluster. **Seen failing today, 410 of 410,
on the retained Step 10 manifests** — record: `impl/2026-09-03_preflight-seen-failing.md`.

## 8. What waits on the OpenUBEM side (§4 of the governing review)

Engine carry-in of the no-core rule into `european_residential.py` ("identified, not ordered"),
`D-EU-84` (no aspect rung at FAIL 0), `D-EU-87` (`C10` pinch test not implemented), `D-EU-88`
(district viewer, not started), and `D-EU-55` (no EnergyPlus without the owner's own sentence).
None of these is 4J's to fix.

---

## Progress Log

Append-only. Never delete or reformat an existing entry; if a decision changes, edit that entry.

### 2026-09-03 — spec created, boxes 4/5/6 of the execution run-book

Implementation and validation documents written; population (four districts), `N_u` formula
(I-3), Arm F redefinition, binding rule (I-5, `D-IMP-3`(a)), manifest field list (I-6), replicate
arm and quotation rule (I-7) all specified. Preflight guard written and **seen failing** on all
410 retained Step 10 manifests (`impl/2026-09-03_preflight-seen-failing.md`). Prereg draft filed
at `prereg_step10_nocore_DRAFT.md` (DRAFT, not frozen, no md5 sidecar). No compute, no EnergyPlus, no
cell, no emission. `Step6_docs/outputs_step6/prereg.md` (md5 `e4243e07cdd80c9c846b91f40e3e8c45`)
never opened for writing.

### 2026-09-08 — the payload landed, the basis was ruled, all five freeze conditions are MET

Record: `impl/2026-09-08_openubem-layouts-reemitted-verified.md` §§11–13. Pre-registration
**FROZEN**: `prereg_step10_nocore_DRAFT.md`, md5 `8176327149c3d36e06c822264ee676e8`, sidecar
`prereg_step10_nocore_DRAFT.md.md5`.

🔴 **§7 above is superseded on its assertion list.** It describes the 2026-09-03 guard, which
asserted `status == "direct"`, a present `check.verdict`, and one engine digest. Measured
2026-09-08: **0 of 1,211** Bologna payloads carry a `status` key and **0** carry a `check` key —
those two assertions named fields no emitted payload has, because they were written before any
plate had been cut. The author ruled the basis: **eligibility is `geometry_outcome`, and a building
is eligible when flats were actually drawn in it** (`DWELLING_LAYOUT_EMITTED` or
`DWELLING_LAYOUT_EMITTED_IMPUTED_COUNT`); `FALLBACK_PENDING_LAYOUT` is **EXCLUDED as Arm F, never a
failure**; the Lyon-only `..._INTERZONE_MISMATCH_REROUTED` and any unknown value **FAIL**.
`partition_audit` is **reported, never gated** (`FINDING 258`). **TWO** digests are pinned, not one
— `european_residential.py` `8e1dcda1…` and `european_nocore.py` `21d723d5…`, because the caller
imports the cutter from the second file. 🔴 Neither pin is ever moved to make a run pass, and
rewriting a field name so a population passes is the same act.

Eligible populations, measured with the ruled guard: **Madrid 1,100 of 1,175 / London 439 of 451 /
Bologna 1,036 of 1,211**, Arm F 75 / 12 / 175, **0 FAIL** in all three. Lyon **0 eligible, 196
FAIL** — correct: never re-emitted, core era, and a baseline that is never a fold. These reproduce
§3.2's Arm D candidate counts exactly, from an independent code path; still a geometry count, not a
scored gate.

Two defects in the guard itself were found by running it and are fixed: it **walked one directory
level only**, so Madrid and London (nested under `layouts/relation/` and `layouts/way/`) were
inspected as **zero files and reported exit 0**; and an **empty scan was a pass**, now `REFUSE`
exit 2. Seen failing in **nine** classes.

`D-EU-55` satisfied for **Bologna only** by the author's own sentence. **The shakedown scores
nothing and moves no gate**; Madrid, London, Lyon, any multi-district campaign, or reading any of
it as a scored `G10N.x` result each need a second sentence.

⚪ **Still to build: a campaign runner for `C2`.** `tools/4thJ_step10_realstock_campaign.py` is the
`C1` machinery and is pinned to `C1` artefacts (Lyon census, 41×5 cells, `prereg.md`
`e4243e07…`). Nothing computed on this date.

### 2026-09-08 (last+44) — the campaign `C2` runner EXISTS; ten refusals seen failing; the engine moved and was committed

Record: `impl/2026-09-08_C2-runner-built-refusals-seen-failing.md`. Tool:
`tools/4thJ_step10_nocore_campaign.py`. **Nothing simulated, no EnergyPlus invoked, no gate scored,
no band moved, no pin moved, nothing written under `OpenUBEM/`.**

The "still to build" item that closed the previous entry is built. The runner reads the emitted
payloads, imports the ruled eligibility basis from `4thJ_step10_nocore_preflight.py` (never restates
it) and the Case A/B pairing from `4thJ_step10_paired.py` (so `G10N.20`'s pair is the emitted pair),
takes zones **from the payload** rather than re-probing the engine, computes per-zone areas by
shoelace from the payload's own vertices (**declared**, not `C1`'s `assumed_equal`), and uses each
district's **own** national TABULA registry. It **scores nothing** under any flag.

**Ten refusals, each seen failing with a passing control** (§2 of the record): `R1` prereg md5,
`R2` `D-EU-55` district authorisation (the author's sentence quoted verbatim; Bologna is the only
entry), `R3` France is never a fold (ahead of `R2`, waivable by nothing), `R4` both engine digests,
`R5` any payload FAILing the ruled basis, `R6` EnergyPlus 23.1 measured, `R7` pairing/uniqueness/
order, `R8` a scored run, `R9` the pinned EPW, `R10` **new** — the payload-set digest, because a
campaign that spans two emissions is two campaigns.

**The population reproduces from a third independent path**: Bologna 1,211 payloads → **1,036
eligible / 175 Arm F / 0 FAIL**, `partition_audit` false on **980**, worst **1.651e-04**, 10,360
cells enumerated, `payload_set_sha256 = 64d6768f8bdfa88d26d334aa8aa1ceae10408e6f63fabccd07a0d66ff8842d21`.

🔴 **CORRECTION — the engine is `6a14f428…` and it is COMMITTED, not mid-edit.** Our `fd1214a6…`
read was a stale mid-edit snapshot; `openubem-20` reports the change landed as commit `fda7f067`
and that no further commit is pending. `european_nocore.py` is still exactly `21d723d5…`. **`R4`
fires on the live tree today and that is correct; the pin was NOT moved.** A new pin is the
**author's**, and it is now a live question. Record the commit **and** the CRLF convention beside it.

🔴 **CORRECTION — the EU Recut Progress board and our `layouts/` payloads are two PIPELINES.** The
board counts the **T06a EnergyPlus recut wave** (Madrid 1,186/1,194, London 1,242/1,242, Bologna
1,158/1,220, Lyon 528/530); our payloads are the **`D-EU-110` side-car emission** (1,175 / 451 /
1,211 / 297). `openubem-20` monitors only T06a, harvest/T06b has not started, and the merged
re-emission + side-car install + **announcement is a separate track (`D-EU-109`) it does not run**.
**The board will never signal our announcement, and "London 100 % drained" is not "London's layouts
are complete".**

🟢 **London's 451 is CONFIRMED still current** — the emitter's `row_map` excludes the 255
`D-EU-108` buildings (187 age-inherited + 68 straddle) inside the `D-EU-109` 1,534-case Speed
campaign, **which has not run** and is a different campaign from the board's four jobs. The dated
snapshot holds.

🔴 **`FINDING 258` stays unresolvable on this payload.** Measured on all 2,837 files: the four
topology sub-fields (`failures`, `gap_area_m2`, `overlap_area_m2`, `outside_area_m2`) are present on
**0**. ⚪ But `openubem-20`'s companion claim that `partition_audit` is "always null" and that Madrid
carries the key on 130 of 1,175 is **wrong** — the key is on 100 % of all three districts and
`passed`/`area_error_fraction` are populated on exactly the eligible buildings (1,100 / 439 /
1,036). Checked before carrying. Decision unchanged: **reported, never gated.**

⚪ **Owed to the author, nobody else:** a new engine pin; a second `D-EU-55` sentence if Madrid or
London is ever to run; and whether the shakedown runs on the current payload or waits for the
`D-EU-109` re-emission. **Step 11 was not started and remains PLANNED, nothing built.**

---

### 2026-09-08 (last+45), same day — 🟢 **`PIN 2` TAKEN, AUTHORISED, AND IT MOVED NO NUMBER**; 🔴 **our "two pipelines" explanation was too strong and the author was right**

Record: `impl/2026-09-08_C2-runner-built-refusals-seen-failing.md` §8. Zero compute, no EnergyPlus.

🟢 **THE ENGINE PIN MOVED ON THE AUTHOR'S OWN CONFIRMATION** (*"lets go. i give confirmation."*).
`ENGINE_DIGEST_PIN` `8e1dcda1…` → **`6a14f428a6d8c26745af3e1483080bf31e3026ebb94702f90ac7eadc4ad2afd3`**
(149,238 B, commit **`fda7f067`**, working tree clean, **CRLF as checked out** — `git show` gives the
LF blob and does **not** reproduce it). `NOCORE_DIGEST_PIN` **unchanged at `21d723d5…`**: the cutter
did not move, only the residential engine. `PIN 1` is **superseded in a comment, not deleted**, with
its commit, its value and the path to its bytes; the reason the move was allowed is written beside
it. Bytes materialised as our own artefact at **`impl/engine_pin_20260908b/`**, both re-hashing
exactly, so the pinned state is reproducible from our repo — `engine_pin_20260908/` untouched.

🟢 **SEEN HOLDING AND SEEN FAILING:** live tree → `rc=0`, digests equal; `PIN 1` bytes under `PIN 2`
→ `rc=1`, `REFUSE: engine sha256=8e1dcda1… != pinned 6a14f428…`.

🔴 **THE PROOF IT WAS NOT MOVED TO MAKE A RUN PASS — the population is identical on both sides**:
`checked=1211 eligible=1036 excluded_armF=175 failed=0`, audit false 980, worst `1.651e-04`,
`payload_set_sha256` `64d6768f…`, 10,360 cells — before and after, unchanged. `R4`'s earlier refusal
on the live tree was the guard working, and the remedy was an author decision, not a code change.
⚪ `PIN 2` may not be the last: the `D-EU-111`/`D-EU-112` re-emission may land further commits, `R4`
will refuse again, and that is again the author's call.

🔴 **CORRECTION TO OUR OWN EXPLANATION — the author's *"layout division comes before simulations"* is
right.** We had told them the board and our `layouts/` are two pipelines, implying the 706 layouts
could not exist before the wave. Reading `scripts/emit_eu11_layout_sidecars.py`: London's 451 is
**two stacked filters, neither physical** — `_gb_rows` without `_gb_terrace_recovery_rows` (the 255
never enter the row set), and then
`row_map = {… for r in rows if str(r["building_id"]) in simulated_ids}`, which ties the export to the
simulated population **by a line in the export script**. The partition itself is pure geometry and
consumes no E+ output. 🟢 What survives: the board still cannot signal our hand-off, so
"London 100 % drained" ≠ "London's layouts are complete". 🔴 What does not: they *could* be emitted
706-wide today. ⚪ **A recorded reason is a hypothesis until the code is read** — "451 by design"
was written down and treated as the whole cause; the larger filter was seven lines further on.

🟢 **The author's go-ahead for the London 706 re-export was relayed to `openubem-20`** (*"if possible
do it now, say to openUbem i give okay, good to go"*), with the filter reading and one question: is
`simulated_ids` load-bearing for a field we cannot see? Announcement requirements unchanged — commit
sha + line-ending convention + per-district counts on disk; `R10` already makes the 451 and a 706
payload two populations. 🔴 Our author's go-ahead is not their author's approval.

⚪ **Owed after this entry, both the author's:** a second `D-EU-55` sentence if Madrid or London is
ever to run, and whether the Bologna shakedown runs on the current payload or waits for the
re-emission. **The engine-pin item is DISCHARGED. Step 11 still not started.**

### 8.5 🟢 THE PEER CONFIRMED THE READING AND IS RUNNING THE 706 EXPORT NOW — WE CONSUME NOTHING UNTIL THE ANNOUNCEMENT

`openubem-20`, same day, in reply to §8.3: **"your read was right, and we're running it now — full
706-building population, not waiting on the pending Speed simulate batch (299 rows, unsubmitted)."**
In progress on their side; they will follow up with commit sha, line-ending convention, and
per-district JSON counts on disk. They warn our 451 is "about to become stale" and that any layout
artifact pulled before the follow-up is provisional.

🟢 **§8.2 IS CONFIRMED BY THE OWNER OF THE CODE.** The `simulated_ids` intersection was a filter, not
a dependency, and the export could be widened without the wave — which is exactly what the author
said and what we had wrongly argued against.

🔴 **THREE THINGS THAT DO NOT CHANGE BECAUSE OF THIS MESSAGE.**

1. **We consume nothing before the announcement.** The standing sequence holds: per-district counts
   arriving before the last step are not an announcement. `R10`'s payload-set digest is computed
   over the file set a run is about to read, so a campaign spanning two emissions refuses rather
   than mixing them — a provisional artifact cannot silently enter a run.
2. **We re-measure rather than carry their counts.** A peer's measurement is evidence, never an
   authority — the same rule that caught their `partition_audit` claim in §7.
3. **Our 451 is not invalidated, it is SUPERSEDED BY A DELIBERATE ACT.** It was pre-registered as a
   DATED SNAPSHOT precisely because this was foreseen. Replacing it is a **re-pre-registration** the
   author signs, append-only, with its own md5 superseding the last — not a silent swap. ⚪ The
   failure mode worth naming: a payload that changes *without* an announcement. That is what `R10`
   exists to catch, and it is unaffected by their good intentions here.

⚪ **ONE NUMBER DOES NOT RECONCILE, AND IT WAS PUT TO THEM.** They say the pending Speed batch is
**299 rows**. Our record has London's uncovered remainder at **255** (187 age-inherited + 68
straddle, `D-EU-108`) inside the 1,534-case `D-EU-109` array, and **451 + 255 = 706 exactly**. Both
can be true if the 299 is a different set — a re-simulate list, or a union with rows already covered
— but if the 706 export contains buildings whose rows come from a builder we have not seen, that
changes **which eligibility tokens we should expect**, not merely the count. Asked as a fourth
announcement requirement: **which builder produced the added rows.** Also still outstanding from
§8.3: **is `simulated_ids` load-bearing for any field, or was dropping it purely a widening?**

🔴 **Nothing was pulled, nothing was measured against the new export, no population was re-derived,
and the prereg was NOT touched.** The next act on our side is the author's, not ours.

### 8.6 🔴 THE LONDON 706 LANDED AND WE MEASURED IT — IT IS NOT AT THE CANONICAL PATH, IT CARRIES 12 FAILS INCLUDING 6 REGRESSIONS, AND IT SETTLES `FINDING 258`

`openubem-20` announced completion the same day with commit `48690c71299f3ebf91958051586dfe2ab8eeba4e`
(⚪ **code and outputs are UNCOMMITTED working-tree changes on top of that sha — the payload is not
reproducible from a commit**, a declared limitation), `core.autocrlf=true` / CRLF JSON, 706 files,
and the real cause of the 255: the London branch called only `_gb_rows` and skipped the
terrace-recovery / neighbour-imputation pass `_gb_impute_rows` that `run_eu_s2_district_campaign.py
::prepare` also runs. ⚪ **So the `simulated_ids` filter of §8.2 was real but was NOT the whole
cause** — our reading was closer than the record but still not the mechanism. **Measured, not
carried.**

#### (a) 🔴 IT IS AT A DIFFERENT PATH FROM THE OTHER THREE DISTRICTS

```
706  2026-09-08 19:39  openubem/outputs/eu_evidence/EU-11/GB-LDN-STDUNSTANS_final_2026-09-07/layouts
451  2026-09-08 06:51  openubem/outputs/3D/eu_GB-LDN-STDUNSTANS_data/layouts          <- CANONICAL
451  2026-09-08 06:51  docs/docs_ACTIVE/europeanLocations/outputs_3D/eu_GB-...  /layouts
```
Madrid 1,175 / Bologna 1,211 / Lyon 297 all sit at the **canonical** path, which for London still
holds the **old 451**. 🔴 **A campaign that reads "the district's layouts directory" therefore takes
the NEW Bologna and the OLD London, silently.** Put to them: install it at the canonical path, or
declare the evidence path authoritative for London and not the others. **We do not guess.**
⚪ The directory is named `_final_2026-09-07` and was written 2026-09-08.

#### (b) 🔴 TWELVE FAILS WHERE THERE WERE ZERO — AND SIX ARE LOST ELIGIBLE BUILDINGS

Our preflight on the 706, under `PIN 2`: **685 eligible / 9 Arm F excluded / 12 FAILED.** The old
451 failed **none**. All 12 carry `DWELLING_LAYOUT_EMITTED_INTERZONE_MISMATCH_REROUTED` — the token
the author's ruled basis FAILS, and the one that makes Lyon unusable. Transitions **inside our
frozen 451**:

| count | before | after |
|---|---|---|
| 433 | `IMPUTED_COUNT` | `IMPUTED_COUNT` (unchanged) |
| 7 | `FALLBACK_PENDING_LAYOUT` | unchanged (Arm F) |
| **6** | **`IMPUTED_COUNT`** | **`INTERZONE_MISMATCH_REROUTED`** — 🔴 **eligible buildings LOST** |
| 5 | `FALLBACK_PENDING_LAYOUT` | `INTERZONE_MISMATCH_REROUTED` |
| +1 | — | brand-new building, also rerouted |

🔴 **This is a regression inside the recut, not a widening.** Examples `way/298850491`,
`way/393505346`. Reported to them before they call it final. **Whether the 706 replaces the 451 is
the author's ruling, not ours** — and it is no longer a free swap, because it costs six buildings.

#### (c) ⚪ NOT ADDITIVE — ALL 451 FILES CHANGED, AND FIVE LAYOUTS GENUINELY MOVED

Every one of the 451 has different bytes. For most, the only differing top-level keys are
`partition_audit` and `best_effort_failed_checks` — the promised additions. But **5 buildings'
layouts really changed**: the 451's zone total moved **1,728 → 1,813** and the `dwelling_count` sum
moved with it. 🔴 **So `uk`'s contribution to the ruled `C2` population of 26,764 zones is no longer
1,728.** Totals for the record: **706 buildings / 2,515 zones; eligible 685 / 2,316 zones.**
🔴 **This is a re-pre-registration the author signs, never an append and never a silent swap.**

#### (d) 🟢 `FINDING 258` IS DIAGNOSED — IT IS A TOPOLOGY GAP, EXACTLY AS WE CORRECTED

The new payload carries `failures`, `gap_area_m2`, `overlap_area_m2`, `outside_area_m2` on **697 of
706** (the 451 carried only `passed` + `area_error_fraction`, which is why the question was
unanswerable). **53** buildings fail the audit:

```
32  (AREA_GAP, AREA_OVERLAP, OUTSIDE_FOOTPRINT)
18  (AREA_GAP, OUTSIDE_FOOTPRINT)
 2  (AREA_GAP,)
 1  (OUTSIDE_FOOTPRINT,)

gap      nonzero 52 of 53   max 1.9184e-02 m²   median(nonzero) 5.002e-03 m²
overlap  nonzero 32 of 53   max 7.155e-03 m²    median(nonzero) 2.490e-03 m²
outside  nonzero 51 of 53   max 1.7534e-02 m²   median(nonzero) 4.014e-03 m²
```

🟢 **Against a topology tolerance of `footprint_area × 1e-9` these are four to five orders of
magnitude over, while `area_error_fraction` clears the `AREA_CONSERVATION` bar of 0.01 by ~100×.
That is the correction we made to our OWN record on 2026-09-08, now confirmed by data rather than by
argument: `FINDING 258` is a TOPOLOGY GAP and `area_error_fraction` was never the quantity that
failed.** 🔴 **The decision is unchanged: `partition_audit` is REPORTED, NEVER GATED.** ⚪ **The
FROZEN prereg still says "rounding residue"; the next re-pre-registration must carry the correction,
and it can now cite measured gap/overlap/outside areas instead of an inference.**

🔴 **NOTHING HAS BEEN CONSUMED.** No population was re-derived from the 706, no prereg was touched,
no `C2` run was started against it. Two things must land first, **both the author's**: the path
question, and whether a payload that costs six eligible buildings replaces the one we froze.

---

### 2026-09-08 (last+46), same day — 🟢 **WORK ITEM 11.3'S RUNNER EXISTS**; 🔴 **the stock population has 100 diaries, not 1,200**; 🟢 **London 706 installed and verified after two defects were caught**

Record: `Step11_docs/docs/2026-09-08_work-item-11.3_trigger-campaign-runner-built.md`. Author's
instruction: *"ok once you got the data continue to build step11 lets go"*. **Nothing scored, no
`G11.x` verdict computed, no EnergyPlus cell simulated, no compute.**

🔴 **THE INSTRUCTION'S CONDITION WAS MIS-SPECIFIED AND SAYING SO IS PART OF THE ANSWER.** The London
export widens the `C2` **population**; it does not unblock **Step 11**. Item 11.3 depends on Step 10
items **10.4 and 10.6** — a *simulated* `C2` cell and its manifest — and **no `C2` cell has been
simulated**, because `D-EU-55` authorises Bologna only. What was genuinely unblocked is the runner,
and that is what was built.

🟢 **`tools/4thJ_step11_trigger_campaign.py`.** For every drawn flat in every `C2` Arm D cell it runs
the Step 9 trigger on **that flat's own diary**. **Three things imported, never re-implemented** —
the state machine (`simulate_dwelling`), the dwellings (`build_dwellings`, which refuses unless it
reproduces Step 8's shipped schedules), and the flat→diary binding (read from the `C2` manifests'
own `schedules[]`). ⚪ *A re-implementation is a second opinion, and a second opinion is not an
inheritance.*

🟢 **A REFACTOR OF A CLOSED STEP, PROVEN INERT.** `simulate_dwelling` did not exist — the loop was
inline in `run_fold`. Extracted verbatim; `rng` became a parameter defaulting to the same
`"s9|<seed>|<hid>"` stream. 🔴 **Verified, not asserted: Step 9 fold `it` run end to end before and
after, and the md5 of EVERY emitted artefact is identical, stdout included.** Backup
`tools/4thJ_step9_trigger.py.bak_s11_extract`. ⚪ **A refactor is not a re-score** — no verdict
recomputed, no band moved, 11.1's carry-over audit untouched.

🔴 **THE `G11.15` SEAM NOW HAS A MEASURED BASIS.** Read out of
`openubem/semantic/european_schedules.py`: `build_step8_gain_series` conserves the annual mean at
exactly `BASE_GAIN_W_M2` for every `f` **and asserts its own conservation**, and attaches ONE
`OTHEREQUIPMENT` at `Watts/Area = 1.0`. **So `C2` carries one LUMPED internal gain — occupants,
appliances, lighting together — as its INPUT and produces SPACE HEATING as its result; `f`
redistributes it in time and never rescales it.** Paths: **Step 10 = `space_heating`; Step 11 =
`appliance_electricity`, `dhw`.** 🔴 **Step 11's appliance electricity must NEVER be injected back
into a Step 10 heating model — that heat is already inside the conserved gain, and adding it again
is the double count.** ⚪ **Consequence: a flat's appliance MAGNITUDE has no path into its heating
number at all; only the TIMING crosses the seam.** Any sentence implying otherwise is false.

🔴 **THE FINDING THAT NARROWS §1.1: ONE HUNDRED DIARIES, NOT ONE THOUSAND.**
`4thJ_step10_assign.step7_index()` indexes **exactly 100 presence schedules per fold** — all Step 7
shipped. Step 9 seeds its per-dwelling RNG `"s9|<seed>|<hid>"` and draws ownership per `hid`, so
**two flats that drew the same household have IDENTICAL loads**. Seen: 170 flats over **6** buildings
already bind **59** of the 100. **The stock population has thousands of BUILDINGS and at most 100
DISTINCT OCCUPANCY DIARIES per fold, and on this Step 7 emission it cannot have more.** ⚪ §1.1's
claim is not wrong, it is **narrower than it reads**: Step 11 is the first configuration with that
many buildings and one shared weather file, **not** the first with that many occupants. **An R²
improvement at stock scale would be evidence about spatial and geometric aggregation, never about
occupant diversity** — claiming otherwise is the comparison `G11.16` calls a FAIL.

🔴 **`--diary-diversity` HAS NO DEFAULT AND THE RUN REFUSES WITHOUT IT (`S9`).** `replicate` = one run
per household (100/fold, ~2 min) replicated onto flats; `reseed` = one run per flat, ownership
redrawn (~1.2 s/flat → Bologna Case B alone ≈ **9 h**, `sbatch` work), **occupant diversity still
100**. **A default would have silently decided what a stock number means.** ⚪ A third option —
widening the Step 7 pool — is **named, not done**: it re-opens two closed steps and breaks
`build_dwellings`'s reproduction guard.

🟢 **TEN REFUSALS `S1`–`S10`, EVERY ONE SEEN FAILING WITH A PASSING CONTROL**, on a fixture of
`C2`-shaped manifests over 6 real Bologna buildings (60 cells, 170 flats) whose **assignment is
real**: `S1` France · `S2` Arm F/pooling · `S3` no cells (missing dir AND empty dir) · `S4` a
manifest `G10N.14` would fail, an incomplete cell, an unrotated cell · `S5` `G11.14` absent column
and `act2` re-admitted · `S6` a diary changed since the `C2` run · `S7` `--scored` · `S8` a `C1`
result, and cells spanning two folds · `S9` the unset flag · `S10` an end-use on both paths and one
on neither. **Nothing was written into `Step11_docs/outputs_step11/`.**

#### The London 706 — installed and verified, after two defects caught by re-measuring

🔴 **DEFECT 1, PATH:** the 706 first landed only at `openubem/outputs/eu_evidence/EU-11/
GB-LDN-STDUNSTANS_final_2026-09-07/layouts` while the canonical path and the docs mirror still held
the old 451 — so a campaign reading "the district's layouts directory" would have taken the new
Bologna and the old London **silently**. Reported; they installed it at the canonical path.
🔴 **DEFECT 2, AND IT IS THE SHARPER ONE: they preserved the old 451 as `way_pre_D-EU-113_backup_
2026-09-08/` INSIDE `layouts/`.** Our mandatory recursive walk then returned **1,157 = 706 + 451** —
a clean-looking, plausible, completely wrong population mixing two emissions of one district, with
no error raised (`eligible=1124`). ⚪ **The nesting rule that protects us became the thing that
betrayed us**: `relation/`+`way/` force a recursive read, and a sibling of old payloads turns correct
behaviour into the wrong answer. Reported; **moved out to `layouts_pre_D-EU-113_backup_2026-09-08/`,
a sibling of `layouts/`, not a child.**

🟢 **RE-MEASURED OURSELVES AFTER THE FIX** (`find -name '*.json'`, never `ls`, never their counts):
**Madrid 1,175 · London 706 · Bologna 1,211 · Lyon 297**, docs mirror agreeing on all three.
London preflight: **706 checked / 685 eligible / 9 Arm F / 12 FAILED**, audit false on 53, worst
`9.960e-05`.

🔴 **THE 12 FAILS ARE REAL AND SIX ARE REGRESSIONS** — six buildings that were `IMPUTED_COUNT` in our
frozen 451 are now `INTERZONE_MISMATCH_REROUTED`, plus five Arm F and one new. Their director accepts
them as-is. ⚪ **That settles it on their side and not on ours: whether a payload that COSTS SIX
ELIGIBLE BUILDINGS replaces the population we froze is our author's re-pre-registration to sign.**
Also **not additive** — all 451 files changed bytes and 5 layouts genuinely moved (`uk` zone total
1,728 → 1,813).

🟢 **`FINDING 258` IS DIAGNOSED AT LAST.** The new payload carries `failures`, `gap_area_m2`,
`overlap_area_m2`, `outside_area_m2` on 697 of 706. 53 audit failures: 32 `(AREA_GAP, AREA_OVERLAP,
OUTSIDE_FOOTPRINT)`, 18 `(AREA_GAP, OUTSIDE_FOOTPRINT)`, 2 `(AREA_GAP,)`, 1 `(OUTSIDE_FOOTPRINT,)`;
gap max `1.9184e-02` m², overlap max `7.155e-03` m², outside max `1.7534e-02` m². **Four to five
orders of magnitude over the `footprint × 1e-9` topology tolerance while `area_error_fraction` clears
the 0.01 conservation bar by ~100×. The correction we made to our OWN record is now confirmed by
data, not by argument: it is a TOPOLOGY GAP and `area_error_fraction` was never the quantity that
failed.** 🔴 Decision unchanged — **reported, never gated**; the frozen prereg still says "rounding
residue" and the next re-pre-registration must carry the correction, now citing measured areas.

⚪ **OWED, ALL THE AUTHOR'S: (1) `--diary-diversity`; (2) a second `D-EU-55` sentence for Madrid or
London; (3) does the 706 replace the frozen 451 at the cost of six buildings; (4) run the Bologna
shakedown, which 11.3–11.7 all wait on.** **Step 11 is still NOT RUN; 11.4–11.7 remain PLANNED.**

---

### 2026-09-08 (last+47), same day — 🔴 **THE `C2` RUNNER HAD NEVER BUILT AN IDF**; 🟢 **three harness defects found by a four-cell smoke**; 🟢 **`RE-PRE-REGISTRATION 2` adopts the London 706**; 🟢 **the Bologna shakedown is RUNNING at full size**; 🟢 **`--diary-diversity` ruled `reseed`**

Record: `Step10_docs/impl/2026-09-08_C2-runner-built-refusals-seen-failing.md` §9. Author's sentence:
*"continue as you recommend lets go use bigger datasets"*. **Nothing scored, no `G10N.x` or `G11.x`
verdict computed.**

🔴 **THE SENTENCE IS READ AS TWO RULINGS AND WRITTEN DOWN SO IT CAN BE CORRECTED IN ONE LINE.**
(1) adopt the London 706; (2) run the authorised district at FULL SIZE, not a token subset.
🔴 **NOT read as a third:** it names no district and does not mention EnergyPlus, so **`D-EU-55` is
NOT widened** — and `R2` was **observed refusing Madrid and London after the sentence was given**.

🔴 **THE RUNNER SHIPPED LAST SESSION WITH TEN REFUSALS SEEN FIRING AND HAD NEVER PRODUCED ONE IDF.**
Three defects, all ours, none physics: **(1)** `KeyError: 'shadow_method'` — upstream's header
template carries a `ShadowCalculation` block and we supplied 5 of 8 fields; the three constants are
now **imported**, never typed. **(2)** `HVACTemplate:* objects ... not supported directly`, fatal in
0.06 s — the binary needs **`-x`**. **(3)** 🔴 **3 of 4 cells died on `readvars.audit ... used by
another process`**: `-r` writes it into the PROCESS working directory, not `-d`, so parallel workers
destroyed each other's file. Fixed with **`cwd=run_dir` + `-d .`**, upstream's own invocation.
⚪ **Defect 3 is the dangerous one — it looks like scattered physics failures, varies with worker
count, and would have salted a 10,360-cell campaign with false `ENERGYPLUS_FAILED` cells no
downstream gate could tell from real ones. All three were found by running FOUR cells before
launching ten thousand.**

🟢 **16 of 16 cells then completed** (91 s, 16 workers). Building `27410`, 16 zones, 3,754.5 m²:
**case A `cf` = 1.0000, case B `cf` = 0.9681**, EUI 49.37 / 49.40 kWh/m². ⚪ The synchronised control
behaves as a control and the independent case diversifies — **a harness observation on two
buildings, NOT a result.**

🟢 **`RE-PRE-REGISTRATION 2`** (473 → 596 lines, append-only, backup
`impl/prereg_step10_nocore_DRAFT.bak_20260908_pre_rr2`): frozen md5
**`1bc21094…` → `055331f285426a9928ca8f124fab7cc3`**. Population **re-measured by us**:
**es 1,100 / 11,244 · uk 685 / 2,316 · it 1,036 / 13,792 → 2,821 buildings, 27,352 Arm D zones**
(was 26,764; `uk` was 439 / 1,728). ⚪ **The trade is recorded both ways: +246 eligible buildings and
+588 zones, at the price of SIX that used to be eligible and are now rerouted.** All twelve London
FAILs stay FAIL. 🔴 **`R1` seen failing by name against the restored pre-RR2 text; live file
re-verified `OK`.**

🟢 **THE SHAKEDOWN IS RUNNING:** `--district IT-BOL-GALVANI2 --shakedown --workers 16 --limit 0`,
**10,360 cells**, detached, ~16 h, log `_local_runs/step10_nocore_bologna_20260908.log`, preflight
report carrying the **RR2** md5. 🔴 **An earlier launch was killed three minutes in on purpose** — it
had passed preflight under the superseded md5, so every manifest would have cited a superseded
pre-registration.

🟢 **`--diary-diversity` RULED `reseed`** — one run per drawn flat, ownership redrawn, so no two flats
carry a byte-identical series; `replicate` is the smaller dataset the sentence declines. 🔴 **It does
NOT widen the occupancy pool: presence still comes from the 100 diaries Step 7 shipped, and `reseed`
varies OWNERSHIP and the draw, never who lives there.** The flag still has **no default**, and a
contradicting value is refused **by name** (`S9b`) — both seen firing, `reseed` passing as control.

⚪ **OWED, NOW ONLY TWO, BOTH THE AUTHOR'S: (1) a second `D-EU-55` sentence naming Madrid and/or
London; (2) whether the finished shakedown may be READ as a scored `G10N.x` result (`R8` refuses
`--scored` until then).** **Step 11 items 11.4–11.7 stay PLANNED until the shakedown's cells exist.**

---

### 2026-09-08 (last+48), late the same day — 🟢 **`D-EU-55` WIDENED BY THE AUTHOR'S OWN WORDS**; 🔴 **the engine-identity field does not identify the engine**; 🔴 **London is refused by `R5`, not by permission**

Record: `Step10_docs/impl/2026-09-08_C2-runner-built-refusals-seen-failing.md` §10. Author's
instructions, quoted: *"you choose as you reccommend also finish all three cities, not important
order, for any computation simulation use 32 cpu of all speed reserouces, lets go"* and *"all
neighbourhoods done you can go until the end thank you"*. **Nothing scored, no `G10N.x` verdict
computed, no pin moved, nothing written under `OpenUBEM/`.**

🟢 **THESE ARE A `D-EU-55` SENTENCE AND "lets go use bigger datasets" WAS NOT.** They name the
**districts** ("all three cities", "all neighbourhoods"), the **act** ("for any computation
simulation", "go until the end") and the **resource** ("32 cpu of all speed reserouces"). `AUTHORISED`
now holds **Madrid, London and Bologna**, with the author's words quoted in the table itself and
carried into every cell manifest. 🔴 **Lyon is still refused** — `R3` fires before `R2` is read, says
in the code that it is *not waivable by any authorisation*, and Lyon's eligible population is **zero
of 297**. **A sentence that says "all" does not create a fold.** 🔴 **And they do not authorise a
scored read**: `scores` stays `False` on all three, `R8` still refuses `--scored`. ⚪ **That costs
nothing, which is the whole argument — the cells a scored campaign writes and the cells this campaign
writes are the same cells; scoring is a downstream READ of finished manifests.**

🟢 **`RE-PRE-REGISTRATION 3`** — 596 → 1,006 lines, append-only, backup
`impl/prereg_step10_nocore_DRAFT.bak_20260908_pre_rr3`, **byte prefix verified after every append.**
md5 `055331f2…` → `ffe7eb39…` → `0dde3604…` → `b944706a…` → `32ec52ba…` →
**`7ce1c0417440798e0ca5d0b32a47d6c4`**, and **every one of those is named in
`PREREG_MD5_SUPERSEDED`** so a run against older text is refused by name. ⚪ Three of the five
appends **correct text frozen minutes earlier** — a staging digest that could not be the one that
ships, a gloss that said something the rule does not say, and two defects a real run found after a
freeze. **Correcting by appending is the discipline; quietly re-freezing is not.**

🔴 **THE TRAP: `energyplus_build_hash` DOES NOT IDENTIFY THE ENGINE.** Measured, not assumed — it is
the release **source commit** `87ed9199d4`, printed identically by the Windows build here and by every
official Linux build of 23.1.0. **Only `platform` separates them.** Rule taken and written into the
runner: **ONE CAMPAIGN, ONE ENGINE BUILD.** Madrid and Bologna run on the Linux binary; the Windows
Bologna run stays a **shakedown** and is **never pooled** with them.

🟢 **THE PORT PROVED ITSELF ON SPEED, NOT BY ASSUMPTION.** The cluster had **no EnergyPlus at all**;
23.1.0 was installed into scratch **from inside `sbatch`**. The tree was shipped as a **tar, never
cloned** — `PIN 2` is CRLF-dependent and `scp` preserved it. **Re-verified there: engine `6a14f428…`,
nocore `21d723d5…`, prereg `7ce1c041…`.** Populations reproduce on a second OS from the staged bytes
(**es 1175→1100/75/0 · it 1211→1036/175/0**) and **both payload set digests match the Windows ones**
(`edd31fd9…`, `64d6768f…`), which both campaigns are pinned to. `R3`, `R8` and `R5` all **seen firing
on Speed**.

🔴 **FOUR MORE HARNESS DEFECTS, THE FOURTH THROUGH SEVENTH, ALL FOUND BY A HANDFUL OF CELLS BEFORE
ELEVEN THOUSAND — and they are ONE pattern: an identity string reaching a place that is not a name.**
**(4)** Madrid's and London's ids are `relation/<n>` and `way/<n>` and **the `/` was reaching a
filesystem path** — every Madrid cell died `HARNESS_ERROR`. Fixed by keeping `cell_id` and deriving a
**`cell_slug`** for paths only, recording **both** in the manifest, and **tightening `R7`** to refuse
a slug that is not one-to-one. **(5)** `geomeppy`, `eppy` and `joblib` are **lazy imports inside
functions**, invisible to a top-level import scan. ⚪ **A top-level import scan is not a dependency
check.** **(6)** 🔴 **a hard-coded `C:\EnergyPlusV23-1-0` chose the SCHEMA and failed as a WARNING**
— eppy falls back to its own bundled **IDD v8.0.0**, which shifts `BuildingSurface:Detailed`'s
fields; 8 of 8 Madrid cells died behind one scrolled-past line. **`R6` now refuses a missing or
foreign IDD.** ⚪ **A fallback that warns is more dangerous than a crash.** **(7)** the same slash
**one level down**, in each flat's `<zone>_gain.csv` FILE NAME — the file landed in a subdirectory
while the IDF asked for the bare name, 18 severe `Schedule:File ... not found` and a fatal before the
simulation began. **`R7` tightened a second time** against gain-csv name collisions, which would
otherwise have one flat's series overwrite another's **while EnergyPlus ran happily on the
survivor**.

🔴 **MADRID CELLS COMPLETE AND CARRY `COMPLETED_WITH_UNSTABLE_MARKERS`; BOLOGNA'S DO NOT.** 8 of 8
Madrid cells finished on Speed with EnergyPlus itself reporting *"Completed Successfully — 24
Warning; 0 Severe Errors"*, and the marker that fires is **"Temperature out of range (PsyPsatFnTemp)"
during SIZING, once, zero times during warmup** — **not** the diverging annual heat balance the
screen was written for. ⚪ **The marker list was deliberately NOT narrowed**: editing a screen so
results stop being labelled is the same act as moving a pin. The label is recorded per cell and can
be counted when the campaign ends; separating the two cases is a **pre-registration question for the
author**.

🔴 **LONDON IS REFUSED BY `R5` AND THE AUTHOR'S SENTENCE DOES NOT CHANGE THAT.** 12 of the 706
payloads are `INTERZONE_MISMATCH_REROUTED` — **the same 12 `RR2` adopted the 706 knowing about**, six
of them regressions — and **a partial population is not a campaign**. Nothing new broke; London is
merely authorised now, so a gate that was always there fires. ⚪ **Authorisation is permission to run,
not permission to pass a gate.** Unblocking is **OpenUBEM's** (re-emit those 12 — reported to them) or
a **basis change** the author would have to re-pre-register, costing six buildings. **`R5` was not
relaxed, `--limit` was not used to skirt it, and no partial London population was run.**

🔴 **ONE DELIBERATE DEVIATION FROM THE AUTHOR'S WORDS: 31 cpu, not 32.** The Slurm association cap is
**exactly `cpu=32` across all their running jobs** — almost certainly where the number in the
sentence comes from — so a 32-cpu job cannot start while any other job of theirs holds one core, and
their own Lyon array straggler (`1314065_11`, 1 cpu, **7 h 27 m** against siblings of 28 s to 3 h)
holds one. At 32 both campaigns sat in `AssocGrpCpuLimit`; at 31 Madrid started at once on
`speed-08`. ⚪ **Worker count enters nothing the manifests record** — it was a result choice only
while the `readvars.audit` collision existed, which is why that was fixed. **One line from the author
puts it back.** ⚪ Deliberately **not** a re-pre-registration: worker count is not a pre-registered
quantity, and amending frozen text now would put the running campaign on a superseded md5.
⚪ **Speed jobs `1314969` (Madrid, RUNNING) and `1314970` (Bologna, QUEUED) run SEQUENTIALLY**, since
31 + 31 exceeds the cap.

🟢 **THE LOCAL WINDOWS BOLOGNA SHAKEDOWN WAS LEFT RUNNING** and gains a purpose it did not have:
**the same 1,036 buildings through two different 23.1.0 binaries at identical pins** — a measured
platform sensitivity, reported, never gated, never pooled. It stays a shakedown.

⚪ **OWED — NOW ONE ITEM, AND IT IS THE AUTHOR'S: whether the finished cells may be READ as a scored
`G10N.x` result.** The compute does not wait on it; only the reading does. **Separately owed by
OpenUBEM, not the author: re-emission of London's 12 rerouted payloads.** **Step 11 items 11.4–11.7
stay PLANNED until the cells exist.**

---

### 2026-09-08 (last+49), after midnight — 🔴 **THE CAMPAIGNS FOUND DEFECT 8 IN THEIR FIRST EIGHTY CELLS AND ALL THREE RUNS WERE STOPPED**; 🔴 **distinct flats emitted under ONE name**; 🔴 **the blind spot was in `R7` itself**

Record: `Step10_docs/impl/2026-09-08_C2-runner-built-refusals-seen-failing.md` §11 and
`prereg_step10_nocore_DRAFT.md` `RE-PRE-REGISTRATION 4`. **No pin moved, no guard relaxed, nothing
scored, no `G10N.x` verdict, nothing written under `OpenUBEM/`.**

🔴 **TWO OF THE FIRST FIVE MADRID BUILDINGS FAILED COMPLETELY — every case, every `f`.** That shape
is the finding: a race or a worker collision scatters, a property of the building does not.
`12582234` died `ENERGYPLUS_FAILED` ten of ten; `12638102` died `HARNESS_ERROR` ten of ten.

🔴 **DEFECT 8 — FIVE GEOMETRICALLY DISTINCT FLATS UNDER ONE NAME.** Read from the payload file
itself: `relation/12638102` has 5 storeys and **five zones all named
`relation/12638102_F0_dwelling_0`**. The storey index does not advance in the name when a building
has **one dwelling per floor**. `zone_records` copies `zone["name"]` verbatim, so **this is
upstream's emission, not our reading of it.** Upstream's `add_european_heating_controls` refuses the
second emission for a name — which is the only reason nothing wrong was produced.
**Measured: ES 233 of 1,100 eligible (21.2%, 435 extra flats) · IT 35 of 1,036 (3.4%) · byte-identical
duplicate groups 0, geometrically distinct 233 · buildings whose `zone_count_emitted` exceeds the
count of distinct names: 233 and 35.** ⚪ **`zone_count_emitted` is "what the gates read", and on a
fifth of Madrid it counts flats that cannot be told apart.**

🔴 **THE BLIND SPOT WAS IN OUR OWN GUARD AND IT WAS ONE WORD OF REASONING.** `RR3.15`'s new `R7`
clause compared `len(set(slugged))` against **`len(set(names))`** — so `set(names)` collapsed the
duplicate on the left as well as the right and **the check passed itself**. It caught two *distinct*
names that slug alike; it was blind to *one name used twice*. Now compared against **`len(names)`**,
the number of drawn flats. 🟢 **Seen failing on both real populations and seen passing on a control
identical but for the duplicated name** (ES 1,100/11,000 · IT 1,036/10,360 both pass clean).
⚪ **`R7` tightened a third time, never relaxed. Eight defects, one unchanged pattern: an identity
string reaching a place that is not a name** — here it is not mangled by a path, it is **not unique
to begin with**. ⚪ Had upstream not refused, five flats would have written one gain csv in turn and
**EnergyPlus would have run the survivor happily**, one household standing in for five with no error
anywhere.

🔴 **ALL THREE RUNS STOPPED, AND IT FOLLOWS FROM THE GUARD RATHER THAN FROM JUDGMENT.** `scancel
1314969 1314970`; `Stop-Process -Id 49648` (local Bologna shakedown at 1,424 of 10,360). **The
author's Lyon array straggler `1314065_11` was NOT touched — it is theirs.** A corrected `R7`
refuses both populations at preflight, verified end to end after the fix; a run whose preflight a
corrected guard refuses cannot produce a `C2` result. ⚪ **The author's *"go until the end"* is
permission to run, not permission to pass a gate** — the same ruling `RR3` made for London, now
applied to the author's own districts, which is the only thing that makes it worth having written.
⚪ The local shakedown went too: with the campaign cancelled there is nothing left to compare it to,
and *"it is only a shakedown"* is the exception that dissolves a rule.

🔴 **A REPORTING DEFECT IN OUR RUNNER, RECORDED AND DELIBERATELY NOT FIXED TONIGHT:** a failing cell
writes **no manifest**, and `campaign_results.json` is written **only after the eleven-thousandth
cell returns** — so for a whole multi-day run every diagnosis lives **in RAM only**. Defect 8 had to
be **reproduced on a second machine** to be read at all. Changing what a run writes is a change to
the record it produces; it belongs in the next re-pre-registration, not in a hurried edit.

⚪ **REPORTED NOT GATED — `relation/12582234`:** EnergyPlus's own `GetSurfaceData: 47 degenerate
surfaces` and `CalcCoordinateTransformation: Invalid dot product` on **repeated consecutive
vertices** in absolute UTM around 4.5 × 10⁶ m, 48 severe, fatal before simulation. **A geometry
property the engine measured, not a harness fault**; one building of five is far too small to quote
a rate.

🔴 **prereg md5 `7ce1c041…` → `e1f2822a800932ff099c15aed6be7ead`**, append-only, backup
`impl/prereg_step10_nocore_DRAFT.bak_20260908_pre_rr4`, byte prefix verified before and after,
`md5sum -c` → OK, **all six superseded values named in `PREREG_MD5_SUPERSEDED`.** ⚪ The 22 manifests
written under `7ce1c041…` are **evidence, never cells to be scored.**

🔴 **OWED — THREE ITEMS, NONE OF THEM COMPUTE.** **OpenUBEM's:** advance the storey index in the
emitted zone name (reported), and still London's 12 rerouted payloads. 🔴 **We do not rename a zone
to make a run pass.** **The author's:** whether the 233 ES and 35 IT buildings are **EXCLUDED** as
Arm F is, or stay **FATAL** as `R5`'s London 12 are — a **basis change, therefore a band change**,
costing 21% of Madrid. **The author's, unchanged:** whether finished cells may be READ as a scored
`G10N.x` result — which now waits on the population question, there being no finished cells to read.

### 2026-09-16 — 🟢 THE CAMPAIGN FINISHED (all three districts) AND WAS SCORED AS `G10N.x`

Pointer only; the full account is in the validation companion's own Progress Log
(`4thJ_10_nocoreRealStock_val.md`, entry "2026-09-16 — THE SUITE IS SCORED IN FULL"), which is now
the state for this campaign's scoring and is not repeated here. Summary: `AUTHORISED` widened to
`scores: True` for Madrid/London/Bologna (author's sentence, 2026-09-16); the finished campaign
(35,090 real cells across `_local_runs/4J_{ES,UK,IT}_local/`) was scored by the new
`tools/4thJ_step10_nocorereal_score.py`; 12 PASS, 1 FAIL (`G10N.20`, real `gain_sha256` collisions
on 320 cells, not a scratch artefact), 1 INFO, 1 OPEN_INHERITED, 9 `NOT_EVALUABLE` (zero reference
population, mostly the cancelled Speed re-run), 1 `NOT_EVALUABLE_VACUOUS`. `G10N.19` clears the
30-per-fold floor on all three folds (es 845 / uk 157 / it 1070), unlike `C1`. No `AUTHORISED` entry,
`D-EU-55` text, or anything closed about `C1` was touched.
**Step 11 items 11.4–11.7 stay PLANNED.**

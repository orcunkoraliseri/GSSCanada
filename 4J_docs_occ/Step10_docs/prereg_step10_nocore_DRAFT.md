# Step 10 — campaign `C2`, no-core real-stock UBEM. Pre-registration. **DRAFT.**

🔴 **THIS IS A DRAFT. NOT FROZEN. NO MD5 SIDECAR.** `Step6_docs/outputs_step6/prereg.md`
(md5 `e4243e07cdd80c9c846b91f40e3e8c45`) is the project's one frozen pre-registration and is never
opened for writing by this document or any campaign `C2` tool. This draft becomes citable only when the
owner freezes it and a sidecar md5 is added; until then nothing here may be quoted as a
pre-registered bar.

**Written** 2026-09-03, box 4 of `IMP/Prompt/4thJ_imp_nocore_execution_2026-09-03.md`. **Re-homed 2026-09-03 under `D-IMP-4`** from `Step12_docs/prereg_step12_DRAFT.md` — there is no Step 12; this pre-registers Step 10 campaign `C2`, gate series `G10N.x`.

---

## What this pre-registers (draft)

* **Hypothesis**: `H10` unchanged from Step 10 — at fixed `f`, the occupancy effect on building
  peak grows with `N_u`, the number of independently diarised dwellings, measured via
  `CF(N_u) = P_peak,bldg / Σ P_peak,zone`.
* **Population**: the no-core layout of the four districts (Madrid, Lyon, London, Bologna),
  Arm D = dwelling-partitioned under the no-core rule, Arm F = check-FAIL-or-unusable-footprint
  fallback (§3.2 of `4thJ_10_nocoreRealStock.md`). France (Lyon) is a physical baseline, never a
  4J denominator.
* **Design**: paired Case A (one diary replicated to all `N_u` zones) / Case B (`N_u` independent
  series), same footprint/archetype/weather/seed policy, exactly Step 10's `10.9` design.
* **Gate series**: `G10N.x`, this document’s companion `4thJ_10_nocoreRealStock_val.md`.
* **What is NOT pre-registered here**: any numeric value from a cell, campaign or manifest — none
  exist. The `N_u` figures on `IMP/docs/2026-09-03_nocore_projection_41.csv` are census arithmetic,
  not a pre-registered population size.

## Freeze conditions (not yet met)

1. The OpenUBEM engine carry-in of the no-core rule into `european_residential.py` must land.
2. `D-EU-84` and `D-EU-87` must be ruled and closed.
3. The owner must pin `ENGINE_DIGEST_PIN` in `tools/4thJ_step10_nocore_preflight.py`.
4. The owner must give the sentence `D-EU-55` requires before any EnergyPlus run.
5. The owner freezes this document and a sidecar md5 is written beside it.

None of the five conditions is met as of 2026-09-03. This draft is not amended in place to record
that fact — this STATUS section is the record, and future edits to this file happen only to refine
the pre-registration itself, never to backdate a freeze that has not happened.

### STATUS, 2026-09-08 (additive — the 2026-09-03 sentence above is left standing)

**Conditions 1 and 2 are now MET. Conditions 3, 4 and 5 are the author's own and remain OPEN.**

* **1 — MET.** The OpenUBEM engine carry-in landed 2026-09-03 (`european_nocore.py`, bit-parity
  **0 mismatches on 2,529 / 2,529 compared plates**, all four districts); `D-EU-88` and `EU-19`
  complete.
* **2 — MET.** `D-EU-87` implemented (`C10` rebuilt as a created-pinch test). `D-EU-84` closed
  2026-09-08 as **`D-EU-110`, an accepted named residual**: `MAX_FLAT_ASPECT` stays at the
  strictest rung **2.5** per `D-EU-89` clause 2, and **81 of 550 plates across 57 unique buildings
  ship as an honest residual `FAIL`**, carried by 4J as a declared limitation. 🔴 The closure
  wording includes, and 4J froze against, the clause that **`EU-21` acceptance criterion 2 remains
  NOT met**. We did not ask for the threshold to be moved and did not move one of ours.
* **3, 4, 5 — OPEN.** All three are the author's actions and all three happen **before** the first
  district runs, never after.

🔴 **Two things must be settled before condition 5 is executed**, both recorded in
`impl/2026-09-08_openubem-layouts-reemitted-verified.md` and neither applied:

1. **Which population Step 11 consumes.** §3.1's `N_u := k × storeys` was census arithmetic written
   when no plate had been cut. The plates are now cut and the emitted zone list disagrees with the
   formula on the majority of buildings (§4 of that record). The recommendation is that the
   **emitted zone is the dwelling**, with `N_u` retained as the projection sense and its deficit
   reported, never gated. This is a pre-registration question, so it belongs here, before the
   freeze.
2. **The London coverage figure.** London ships **451 side-cars for 706 simulated buildings** — a
   named limitation on their side (`_gb_rows` yields no record for the 255-building
   coverage-recovery batch), not a defect and not something to wait for. **451 of 706** is the
   figure to pre-register; a `JSON count == published row count` check fails London by design.

Nothing on the OpenUBEM side blocks campaign `C2` any more. `C2` still has **no cell**, and this
document is still **DRAFT and unfrozen**.

#### Addendum, 2026-09-08 later the same day (additive — nothing above is rewritten)

Both open points above were answered by the OpenUBEM owner the same day. Record: §9 of
`impl/2026-09-08_openubem-layouts-reemitted-verified.md`.

* **The London figure is a DATED SNAPSHOT, not a final coverage.** The 255 are `D-EU-108`'s newly
  admitted London population (187 age-inherited + 68 straddle-disambiguated, never simulated) and
  they sit in a **1,534-case Speed array that has not run**; `D-EU-107`/`108`/`109` are all still in
  execution and **no date exists**. London coverage **will rise above 451**. 🔴 The decision stands —
  **pre-register 451 of 706 as of 2026-09-08, name the 255, do not wait** — but pre-register it *as
  a dated snapshot*, so that re-pre-registering when the recovery lands is an **explicit act with a
  visible before and after**, never a silent restatement. They undertake to announce the new counts
  before we could consume them, the same undertaking as for `FINDING 258`.
* **The `N_u` disagreement is explained and is not a defect on either side.** Their `FINDING 246`:
  the district census cuts one `k` **per building**, the engine re-derives `k` **per storey**.
  Verified from our side one for one — `N_u = k × storeys` reproduces the emitted zone count on
  exactly the uniform-per-storey buildings and fails on exactly the non-uniform ones (553 / 47 /
  880, matching 1,100−547 / 439−392 / 1,036−156). The owner independently gives the same
  recommendation we do: **the emitted zone is the dwelling**, `floors[].dwelling_count` is
  authoritative, and **`dwellings_total` is provenance — an attribute, never a check.** 🔴 Also:
  **`units_per_floor` is the maximum per-storey count, never a constant** — `units_per_floor ×
  storeys` is not a population and must not be written as one.

🔴 Still unruled and still the author's. Nothing in this pre-registration has been changed.

---

#### Ruling, 2026-09-08 (additive — nothing above is rewritten)

**The author has ruled the open population question of §3.1: the dwelling is the drawn plate.**
Given in the viewer, by pointing at the coloured residential units on a floor plate and naming the
dwelling as the smallest unit the plate is divided into. Record and worked examples: §10 of
`impl/2026-09-08_openubem-layouts-reemitted-verified.md`.

* The **emitted zone is the dwelling**. `floors[].dwelling_count` and its sum are the authoritative
  counts. `C2` population at this date: **26,764** (es 11,244 / uk 1,728 / it 13,792), over the
  2,575 non-fallback files.
* `N_u := k × storeys` is retained as the **projection sense only**; the deficit
  `N_u − emitted_zones` is **reported, never gated**. A third named sense, `zone_count_emitted`, is
  the sense the `G10N.x` gates read.
* `dwellings_total` is **provenance — an attribute, never a check**.
* `units_per_floor × storeys` is **not a population** (`FINDING 266`).

🔴 This ruling settles the question that had to precede the freeze. It does **not** freeze this
pre-registration: conditions 3, 4 and 5 remain open and are the author's — pin `ENGINE_DIGEST_PIN`
in `tools/4thJ_step10_nocore_preflight.py`, give the sentence `D-EU-55` requires for our own
EnergyPlus run, then freeze this file with an md5 sidecar. No gate has been scored and no band moved.

---

#### Freeze condition 4 — MET, 2026-09-08 (additive — nothing above is rewritten)

**The author gave the sentence `D-EU-55` requires, verbatim:**

> "I authorise EnergyPlus to run on our side for the no-core work, starting with Bologna only as a
> shakedown that scores nothing."

Given in the author's own words on 2026-09-08, unprompted by any peer message. `D-EU-55` is
therefore satisfied **on the 4J side** for the scope this sentence names, and no wider.

* **Scope authorised:** EnergyPlus, on our side, for the no-core work (campaign `C2`), **Bologna
  only**, **as a shakedown that scores nothing**.
* **Not authorised by this sentence:** Madrid, London or Lyon; any multi-district campaign; any run
  whose output is read as a scored `G10N.x` result. Widening the scope needs a second sentence from
  the author, recorded the same way.
* 🔴 **A single district is not a campaign.** `G10N.19` needs 30 qualifying Arm D buildings **per
  fold across three folds**; Bologna alone cannot reach that. The author's own words already say the
  shakedown scores nothing, and that clause travels with every number it produces.

**Freeze conditions after this entry: 1 MET, 2 MET, 4 MET. 3 and 5 remain OPEN and are the
author's** — pin `ENGINE_DIGEST_PIN` in `tools/4thJ_step10_nocore_preflight.py`, then freeze this
file with an md5 sidecar. The freeze happens **before** the first district runs.

⚪ **Candidate value for condition 3, measured not pinned.** The engine that would run is
`OpenUBEM/openubem/geometry/european_nocore.py` (91,468 bytes, 2026-09-07, commit `4431f2fe`),
**sha256 `21d723d5479076d0a57416ff92fd67a98fca8a33ff19343132415c144ff6b8ae`**. This is recorded as a
measurement only; `ENGINE_DIGEST_PIN` still reads `TBD_by_owner` and is **set by the author, never
moved to make a run pass**.

---

#### Freeze condition 3 — MET, 2026-09-08 (additive — nothing above is rewritten)

The author pinned the engine digest ("go, lock it"). Record: §12 of
`impl/2026-09-08_openubem-layouts-reemitted-verified.md`. Tool backup:
`tools/previous_4thJ_step10_nocore_preflight.py.bak_pin20260908`.

**Two files are pinned, not one.** `european_residential.py` imports `cut_storey_nocore` from
`european_nocore.py`, so hashing only the caller would leave the accepted cutter unpinned:

```
european_residential.py   8e1dcda193bd2e68165ec7267c637e9fdf5abb0d3a0be464c6eb4cdb1db4d2d5
european_nocore.py        21d723d5479076d0a57416ff92fd67a98fca8a33ff19343132415c144ff6b8ae
```

🔴 **Neither pin is ever moved to make a run pass.** Seen holding on all 1,211 Bologna files and
seen failing under three perturbations plus the 175 Arm F fallbacks (§12.2).

**Freeze conditions: 1, 2, 3, 4 MET. 5 OPEN — freeze this file with an md5 sidecar, before the
first district runs.**

🔴 **A new condition-shaped item opened while pinning, and it is the author's basis decision.**
The preflight's other two assertions — `status == "direct"` and `check.verdict is not None` — name
keys the emitted payload does **not** carry: **0 of 1,211** Bologna files have a `status` key and
**0 of 1,211** have a `check` key. The payload carries `geometry_outcome` and `partition_audit`
instead. Those assertions were **not** relaxed: rewriting a guard's field names so a population
passes is the same act as moving a digest pin. **Until the author rules which emitted field is the
campaign-`C2` eligibility verdict and what value admits a building, the preflight admits nothing and
the Bologna shakedown cannot start**, notwithstanding the `D-EU-55` sentence.

---

#### The eligibility basis — RULED by the author 2026-09-08 (additive — nothing above is rewritten)

The blocker recorded immediately above is closed. The author ruled, in their own words, that a
building is eligible for campaign `C2` when **flats were actually drawn in it**. Record: §13 of
`impl/2026-09-08_openubem-layouts-reemitted-verified.md`. Tool backup:
`tools/previous_4thJ_step10_nocore_preflight.py.bak_basis20260908`.

🔴 **This is a BASIS DECISION, not a relaxation.** The 2026-09-03 assertions `status == "direct"`
and `check.verdict is not None` were **replaced, not loosened**: they named keys no emitted payload
carries, because they were written before any plate had been cut. The eligibility verdict is
`geometry_outcome`.

**The rule, as implemented in `tools/4thJ_step10_nocore_preflight.py`:**

| `geometry_outcome`                                   | verdict        | meaning                                   |
|------------------------------------------------------|----------------|-------------------------------------------|
| `DWELLING_LAYOUT_EMITTED`                            | **ELIGIBLE**   | flats drawn, census dwelling count as given |
| `DWELLING_LAYOUT_EMITTED_IMPUTED_COUNT`              | **ELIGIBLE**   | flats drawn, dwelling count imputed        |
| `FALLBACK_PENDING_LAYOUT`                            | **EXCLUDED**   | Arm F — ineligible is its correct state, never a failure |
| `DWELLING_LAYOUT_EMITTED_INTERZONE_MISMATCH_REROUTED`| **FAIL**       | core-era artefact (Lyon only, never re-emitted) |
| anything else                                        | **FAIL**       | unknown verdict — record and rule, never admit |

An `ELIGIBLE` payload must also carry `scheme == "nocore_equal_area"` and **at least one zone**; an
Arm F payload must carry `scheme: null` and **zero** zones. Both digests must match their pins
before any payload is read at all.

⚪ **Whether the dwelling count was imputed is PROVENANCE, reported, never gated.** Madrid is
almost entirely non-imputed (1,099 of 1,100); Bologna and London are entirely imputed. Admitting
only the imputed variant would have failed 1,099 sound Madrid buildings — corrected the same day.

⚪ **`partition_audit` is REPORTED, NEVER GATED.** Gating on `partition_audit.passed` would admit
**56 of 1,036** Bologna buildings. The 980 that carry `passed: false` are off by a **median
1.416e-05 and a worst 1.651e-04 (0.0165 %)** — none above 2e-04. That residue is `FINDING 258`,
carried as a declared limitation with the payload pre-repair; it is a rounding residue, not an
eligibility criterion.

**Pre-registered eligible populations, measured 2026-09-08 with the ruled guard:**

```
district                    payloads   ELIGIBLE   EXCLUDED Arm F   FAIL
Madrid  (es)                    1175       1100               75      0
London  (uk)                     451        439               12      0   <- 451 of 706, DATED SNAPSHOT
Bologna (it)                    1211       1036              175      0
Lyon    (fr, baseline only)      297          0              101    196   <- core-era, CORRECTLY refused
```

🟢 These reproduce the Arm D candidate counts pre-registered above (**es 1,100 / uk 439 /
it 1,036**) exactly, from an independent code path. 🔴 Still a **geometry** count, not a scored
gate: `V10N.a` holds, the census assigns the arm at run time, and **the layout probe never promotes
Arm F to Arm D.**

**Two defects were found in the guard itself while ruling this, and both are fixed:**

1. **It walked one directory level only.** Madrid and London nest their payloads under
   `layouts/relation/` and `layouts/way/`; Bologna is flat. The 2026-09-03 walk saw **zero files**
   in the two nested districts and **exited 0** — a preflight that inspected nothing reported
   success. It now walks recursively.
2. **An empty scan was a pass.** It now **REFUSES with exit 2** when `checked == 0`.

**Seen failing in nine classes** (standing rule): unknown outcome; wrong scheme on a drawn payload;
zero zones on a drawn payload; Arm F carrying a scheme; core-era rerouted outcome; engine digest
mismatch; no-core digest mismatch; engine file absent (exit 2); empty scan (exit 2).

**Freeze conditions: 1, 2, 3, 4 MET, and the basis blocker is closed. Only 5 remains.**

---

## 🔒 FROZEN — 2026-09-08, all five freeze conditions MET

**Freeze condition 5 is now MET. This pre-registration is frozen and this is its last line.**

Authorised by the author the same day ("yes, start lets go"), immediately before the Bologna
shakedown and **before any district runs**, which is the whole point of the condition.

```
1. the payload lands and is verified            MET   2026-09-08
2. the engine carry-in is complete              MET   2026-09-08
3. the owner pins the engine digests            MET   2026-09-08, TWO files
4. the owner gives the D-EU-55 sentence         MET   2026-09-08, Bologna only
5. this file is frozen with an md5 sidecar      MET   2026-09-08
```

The digest is in the sidecar `Step10_docs/prereg_step10_nocore_DRAFT.md.md5`, in the same format
as the frozen Step 6 pre-registration. Verify at any time with:

```
md5sum -c Step10_docs/prereg_step10_nocore_DRAFT.md.md5
```

⚪ **The filename still says `_DRAFT` on purpose.** It is referenced by name across the Step 10 and
IMP documents and by `Step10_docs/README.md`; renaming a frozen file to make it look frozen would
break those pointers for no gain. The sidecar is what makes it frozen, not the name.

🔴 **From here, this file is append-only and only by an explicit re-pre-registration** — a new
dated section, a new sidecar, and a visible before and after. Never a silent restatement. Two
things are already known to require one: **London's 451 of 706 is a DATED SNAPSHOT** and will rise
when `D-EU-108`'s recovery lands, and the payload is **pre-repair for `FINDING 258`**. In both
cases `openubem-20` undertakes to announce before we could consume.

🔴 **Nothing in this file was rewritten to reach the freeze.** Every 2026-09-08 change is an
additive section below the 2026-09-03 text, including the sentence that says none of the five
conditions was then met — which was left standing.

---

# 🔓🔒 RE-PRE-REGISTRATION 1 — 2026-09-08, later the same day

**Superseded sidecar:** `8176327149c3d36e06c822264ee676e8` (the freeze of earlier today).
**This section is the visible before-and-after that the freeze clause requires.** Nothing above this
line was edited — including the sentence at line 219 that this section corrects. Read the old text,
then read this.

**Authorised by the author, in their own words:** *"yes, accept the new buildings and revert the
software"*.

**Record:** §15 of `Step10_docs/impl/2026-09-08_openubem-layouts-reemitted-verified.md`.
**Trigger:** `openubem-6e`'s announcement of `D-EU-111` / `D-EU-112` and a full four-district
re-emission, received after the freeze.

## RR1.1 The eligibility basis is WIDENED — best-effort cuts are admitted

The 2026-09-08 basis stands unchanged in its principle: **a building is eligible for campaign `C2`
when flats were actually drawn in it**, and the verdict field is `geometry_outcome`. What changes is
the list of values that mean *drawn*:

```
DWELLING_LAYOUT_EMITTED                                ELIGIBLE   unchanged
DWELLING_LAYOUT_EMITTED_IMPUTED_COUNT                  ELIGIBLE   unchanged
DWELLING_LAYOUT_EMITTED_BEST_EFFORT                    ELIGIBLE   ADDED by this section
DWELLING_LAYOUT_EMITTED_BEST_EFFORT_IMPUTED_COUNT      ELIGIBLE   ADDED by this section
FALLBACK_PENDING_LAYOUT                                EXCLUDED   unchanged (Arm F, never a FAIL)
DWELLING_LAYOUT_EMITTED_INTERZONE_MISMATCH_REROUTED    FAIL       unchanged (core-era, Lyon only)
anything else                                          FAIL       unchanged
```

**What a best-effort cut is** (`D-EU-111`, OpenUBEM side): a cut that fails **only** the three
*shape* checks `C6` / `C10` / `C11` — thin flat, short façade, pinch — is emitted instead of
refused. `C1` / `C3` / `C4` / `C5`, the partition audit and the 12-per-floor density cap still
refuse. `MAX_FLAT_ASPECT` stays **2.5** and **no threshold moves**, so **freeze condition 2 and
`D-EU-110` are undisturbed by this re-pre-registration**. The payload keeps `checks` carrying the
real `FAIL` verdict and adds `best_effort_failed_checks: [...]`.

**Why it satisfies the ruled basis.** In a best-effort payload every dwelling *is* drawn — the
plates exist, the zones exist, the partition audit ran. What failed is a judgement about the
resulting shape, not about whether flats were produced. The author's ruling was *"flats were
actually drawn in it"*, and they are.

🔴 **Two conditions this document imposes on an admitted best-effort payload, over and above
OpenUBEM's contract**, both enforced by `tools/4thJ_step10_nocore_preflight.py` and both seen
failing:

1. It **must name what it waived** — a payload flagged best-effort with no `best_effort_failed_checks`
   list is a FAIL. A waiver that does not say what it waived is not a waiver.
2. It may waive **only `C6`, `C10`, `C11`**. A best-effort payload listing any other check is a
   contract violation and is a FAIL, not a building we admit.

⚪ **Admitted, never silently mixed.** The preflight counts and prints best-effort admissions
separately, REPORTED and NEVER GATED, on the same footing as `partition_audit`. **A best-effort
building carries a real `FAIL` verdict in its own `checks` block, and no EUI drawn from one may be
quoted as a clean cut.** Any `G10N.x` result computed over a population containing best-effort
buildings must state their count in the same breath.

⚪ **Expected size, NOT a pre-registered number and never back-fitted.** OpenUBEM's dry run measured
Madrid ≈ +53, Bologna ≈ +148, London ≈ +5, Lyon ≈ +15. Those are their estimates, published here so
the eventual counts can be compared against what was expected rather than described after the fact.
🔴 **We have flagged to them that the Bologna ≈ +148 may not arrive**: their best-effort branch is
gated on `best_effort_audit.passed`, and 980 of 1,036 currently drawn Bologna payloads already fail
that audit (see RR1.2). If the residue survives re-emission the tier admits only the gap-free
buildings. That prediction is falsifiable on the first `2026-09-08b` side-car.

**Measured effect on today's payload: ZERO.** The widened guard was run over all four installed
districts against the pinned engine and admitted **0 best-effort buildings in every one**, because
the re-emission has not happened. The pre-registered populations below are therefore **unchanged**:

```
Madrid   1175 payloads  1100 ELIGIBLE   75 Arm F     0 FAIL   exit 0    0 best-effort
London    451 payloads   439 ELIGIBLE   12 Arm F     0 FAIL   exit 0    0 best-effort
Bologna  1211 payloads  1036 ELIGIBLE  175 Arm F     0 FAIL   exit 0    0 best-effort
Lyon      297 payloads     0 ELIGIBLE  101 Arm F   196 FAIL   exit 1    0 best-effort
```

🟢 **This is the point of re-pre-registering before the data arrives.** The basis was widened while
the widening provably changed nothing, so when the recut lands, every building it adds is
attributable to the recut and not to the rule change.

## RR1.2 `FINDING 258` is CORRECTED — it is a topology gap, not a rounding residue

🔴 **The text above at line 219 says the `partition_audit` residue "is a rounding residue". That is
wrong, and it is corrected here rather than edited there.**

`audit_european_floor_partition` (`openubem/geometry/european_residential.py`) sets `passed: false`
when **any** of six named failures fires:

```
DWELLING_COUNT   INVALID_DWELLING   AREA_GAP   AREA_OVERLAP   OUTSIDE_FOOTPRINT   AREA_CONSERVATION
```

`AREA_CONSERVATION` uses `relative_area_tolerance = 0.01`. The measured area errors clear that
tolerance by roughly **500×** and therefore **cannot be what failed**. The three topology checks use
`footprint_area × EUROPEAN_TOPOLOGY_TOLERANCE_FRACTION`, and that fraction is **1e-9** — so a gap of
~1.9e-05 of the plate is about **19,000×** the tolerance it is measured against.

🔴 **The quantity we have been quoting — `area_error_fraction` — is not the quantity that failed.**
The failure is topological: a gap between plates, an overlap, or geometry outside the footprint.

⚪ **Which of the three fired is not knowable from the payload.** The emitted side-car carries only
`{passed, area_error_fraction}` and drops the audit's own `failures` tuple together with
`gap_area_m2`, `overlap_area_m2` and `outside_area_m2`. Measured across all 1,036 drawn Bologna
payloads: those two keys and no others. **Requested of OpenUBEM 2026-09-08**; until it arrives the
diagnostic we hold is provably not the cause.

**Extent, measured 2026-09-08 across all three folds** — the earlier text gave only Bologna:

```
fold      partition_audit passed=false      worst area_error_fraction
Madrid            745 of 1100                       8.809e-05
London             48 of  439                       9.960e-05
Bologna           980 of 1036                       1.651e-04
total            1773 of 2575
```

🟢 **The DECISION does not change and is reaffirmed: `partition_audit` is REPORTED, NEVER GATED.**
Gating still admits 56 of 1,036 in Bologna. Discarding 1,773 of 2,575 sound buildings over an
unnamed sub-millimetre topology gap would still be the mistake. **Only the recorded reason was
wrong.** `FINDING 258` remains open and the payload remains pre-repair — a declared limitation that
travels with every number, now described correctly.

## RR1.3 The engine pin — NOT moved, and now independently preserved

🔴 **Neither pin is moved by this section.** They stand exactly as frozen:

```
ENGINE_DIGEST_PIN  8e1dcda193bd2e68165ec7267c637e9fdf5abb0d3a0be464c6eb4cdb1db4d2d5   european_residential.py
NOCORE_DIGEST_PIN  21d723d5479076d0a57416ff92fd67a98fca8a33ff19343132415c144ff6b8ae   european_nocore.py
```

On 2026-09-08 at 12:21 OpenUBEM began editing `european_residential.py` in place — the in-flight
`D-EU-111` work, uncommitted — and it now reads `fd1214a6…`. **The preflight consequently REFUSES
before opening any payload, and that is correct behaviour.**

The author ruled *"revert the software"*. That ruling is satisfied here **without writing to
OpenUBEM's working tree**, because reverting it would destroy the peer's uncommitted implementation
of the very feature RR1.1 just admitted. Instead the pinned bytes are materialised as our own
read-only artefact:

```
Step10_docs/impl/engine_pin_20260908/european_residential.py   sha256 8e1dcda1…  = ENGINE_DIGEST_PIN
Step10_docs/impl/engine_pin_20260908/european_nocore.py        sha256 21d723d5…  = NOCORE_DIGEST_PIN
```

Every population table in this section was measured with the preflight pointed at that copy
(`--engine` / `--nocore`), so the pinned engine state is now **reproducible from our own repository
and independent of anything OpenUBEM does to their tree**. 🔴 It is a reference artefact, never an
engine we execute: `D-EU-55` and the digest pins govern execution exactly as before.

🔴 **Recorded for every future pin: our digests are LINE-ENDING DEPENDENT.** Both are the `HEAD`
blob in **CRLF** form. `git show HEAD:<path> | sha256sum` yields `135fe46c…` and `6de4c66d…` and
will **never** reproduce them; a clone with a different `core.autocrlf` breaks both without one byte
of logic changing. **Any future pin must record the commit AND the line-ending convention beside the
digest**, and preferably ship the bytes as above.

## RR1.4 What this section does NOT do

- It does **not** move a digest pin, or a threshold, or `MAX_FLAT_ASPECT`, or `D-EU-110`.
- It does **not** consume the `2026-09-08b` re-emission — it has not landed and has not been
  announced as complete. Nothing may be consumed before that announcement.
- It does **not** gate on `partition_audit`, and does not repair `FINDING 258`.
- It does **not** change London's **451 of 706 DATED SNAPSHOT**, which still stands and still awaits
  `D-EU-108`. That remains a foreseen future re-pre-registration.
- It does **not** widen `D-EU-55`. The shakedown is still **Bologna only**; Madrid, London, Lyon,
  any multi-district campaign, or reading any of it as a scored `G10N.x` result each still require a
  **second author sentence**.
- It does **not** score anything. **No gate moved, no band moved, no cell created, no manifest
  written, no EnergyPlus invoked, nothing written under `OpenUBEM/`.**

## RR1.5 The file is re-frozen

```
Step10_docs/prereg_step10_nocore_DRAFT.md.md5    superseded  8176327149c3d36e06c822264ee676e8
                                                 current     see the sidecar beside this file
verify:  md5sum -c Step10_docs/prereg_step10_nocore_DRAFT.md.md5   ->  OK
```

Backup of the pre-RR1 state: `Step10_docs/impl/prereg_step10_nocore_DRAFT.bak_20260908_pre_rr1`.

🔴 **Append-only continues to apply.** The next change to this file is `RE-PRE-REGISTRATION 2`, with
its own dated section, its own sidecar, and the superseded md5 named at its head. Two are already
foreseen: **the `2026-09-08b` recut's actual populations**, and **London's snapshot rising**.

---

# RE-PRE-REGISTRATION 2 — 2026-09-08

**Superseded md5:** `1bc21094b0e09e3ac4332fa2e80abf75` (`RE-PRE-REGISTRATION 1`, itself superseding
`8176327149c3d36e06c822264ee676e8`). **Append-only:** nothing above this line is edited, reworded or
deleted; every number this section changes is restated here beside the number it replaces.

**The author's sentence, quoted not summarised (2026-09-08):**

> *"continue as you recommend lets go use bigger datasets"*

🔴 **HOW THAT SENTENCE IS READ HERE, WRITTEN DOWN SO IT CAN BE CORRECTED IN ONE LINE.** It is read as
**two** rulings and **not** as a third:

1. ✅ **Adopt the 706.** London's `451 of 706` DATED SNAPSHOT is replaced by the full re-emission.
   This is the re-pre-registration RR1.5 said was already foreseen.
2. ✅ **Run the authorised district at full size.** The Bologna shakedown runs its whole eligible
   population, not a token subset — a subset would have been the smaller dataset the sentence
   declines.
3. 🔴 **NOT read as widening `D-EU-55`.** The sentence names no district and does not mention
   EnergyPlus. Madrid and London therefore remain **refused by `R2`**, and the preflight was observed
   refusing both after this sentence was given. ⚪ *A sentence about dataset size is not a sentence
   authorising a binary to run somewhere new; if the author meant that too, one line naming the
   district adds it.*

## RR2.1 What changed on disk

OpenUBEM re-emitted London under `D-EU-113` and installed it at the canonical path
`openubem/outputs/3D/eu_GB-LDN-STDUNSTANS_data/layouts`, after two defects we caught by re-measuring
and reported to them: the payload first landed only under `outputs/eu_evidence/…`, and the superseded
451 was preserved **inside** `layouts/`, which made our mandatory recursive walk return a
plausible, error-free, completely wrong **1,157 = 706 + 451**. Both are fixed; the convention
(`layouts/` is live payload only, superseded emissions are **siblings, never children**) is now in
their plan document as well as ours.

## RR2.2 The `C2` population, re-measured by us and never carried

Measured with the ruled basis as implemented in `4thJ_step10_nocore_preflight.py`, walking
`*.json` recursively (never `ls`, never `sources.json`):

```
fold  payloads   ELIGIBLE (Arm D zones)   Arm F   FAIL
es       1,175    1,100  (11,244)           75      0
uk         706      685  ( 2,316)            9     12      <- was 451 / 439 / 1,728 / 7 / 0
it       1,211    1,036  (13,792)          175      0
--------------------------------------------------------
THREE FOLDS      2,821 eligible buildings, 27,352 Arm D zones
```

🔴 **The pre-registered `C2` population is now `27,352` zones (es 11,244 / uk 2,316 / it 13,792),
replacing `26,764` (es 11,244 / uk 1,728 / it 13,792).** Eligible buildings in `uk` move **439 →
685**. ⚪ Lyon is measured for the record only — 297 payloads, **0 eligible**, 101 Arm F, 196 FAIL —
and remains a physical baseline that is never a fold (`R3`, `G10N.11`).

## RR2.3 What adopting the 706 costs, stated as a cost

The swap is **not additive**. All 451 previously frozen files have different bytes; five buildings'
layouts genuinely moved. Transitions inside the frozen 451: 433 unchanged `IMPUTED_COUNT`, 7
unchanged Arm F, **6 `IMPUTED_COUNT` → `INTERZONE_MISMATCH_REROUTED` (eligible buildings LOST)**, 5
Arm F → rerouted, and 1 new building also rerouted. 🔴 **Twelve London payloads now FAIL the ruled
basis where the 451 failed none, and six of those twelve are regressions, not new arrivals.**

⚪ **The trade is recorded so it is never quoted one-sided: +246 eligible buildings and +588 Arm D
zones, at the price of six buildings that used to be eligible.** The author's sentence is read as
accepting that trade. It is **not** read as accepting a rerouted payload into the population — all
twelve remain FAIL, and `R5` refuses the district while any payload classifies FAIL.

## RR2.4 `FINDING 258` — the diagnosis this payload finally allows

The re-emission carries `failures`, `gap_area_m2`, `overlap_area_m2` and `outside_area_m2` on 697 of
706; the 451 carried only `passed` and `area_error_fraction`, which is why the question was
unanswerable. 53 buildings fail the audit — 32 `(AREA_GAP, AREA_OVERLAP, OUTSIDE_FOOTPRINT)`, 18
`(AREA_GAP, OUTSIDE_FOOTPRINT)`, 2 `(AREA_GAP,)`, 1 `(OUTSIDE_FOOTPRINT,)`; gap max `1.9184e-02` m²,
overlap max `7.155e-03` m², outside max `1.7534e-02` m².

🔴 **Against a topology tolerance of `footprint_area × 1e-9` these run four to five orders of
magnitude over, while `area_error_fraction` clears the `AREA_CONSERVATION` bar of 0.01 by ~100×.
`FINDING 258` is a TOPOLOGY GAP; `area_error_fraction` was never the quantity that failed.** The
frozen text above says "rounding residue" — **that wording is superseded by this section and is left
in place unedited, as append-only requires.** 🔴 **The decision is unchanged: `partition_audit` is
REPORTED, NEVER GATED.**

## RR2.5 Disclosed because it enters the physics: the `C2` IDF header

The `C2` runner had never successfully built an IDF; the first dry-run against real payloads failed
with `KeyError: 'shadow_method'`. The upstream header template carries a `ShadowCalculation` block,
and our formatter did not supply its three fields. 🔴 **They are now IMPORTED from
`scripts/run_eu_s2_campaign.py`, never typed into our file** — `PolygonClipping` / `Periodic` /
`1 day`, upstream's `D-EU-40 R7` constants, chosen there before any EnergyPlus run and reported, not
tuned to a result. ⚪ Typing a value locally would have been this campaign quietly holding a second
physics setting under one name. Separately, EnergyPlus is now invoked with **`-x`**: the heating
controls emit `HVACTemplate:Zone:IdealLoadsAirSystem`, which the binary refuses to read
unexpanded — and with **`cwd=run_dir` and `-d .`**, because `-r` runs ReadVarsESO, which
writes `readvars.audit` into the process working directory rather than into `-d`. 🔴 **With a
shared working directory parallel workers destroyed each other's audit file and EnergyPlus
died — SEEN, three of four cells of ONE building, which without a smoke run would have looked
like three physics failures scattered through a 10,360-cell campaign.** ⚪ All three defects
were found by running four cells before launching ten thousand.

## RR2.6 What this section does NOT do

- It does **not** widen `D-EU-55`. **Madrid, London and Lyon are still refused**, and any scored
  reading of any run still needs a second author sentence.
- It does **not** move `ENGINE_DIGEST_PIN` (`6a14f428…`, `PIN 2`, CRLF) or `NOCORE_DIGEST_PIN`
  (`21d723d5…`), or any threshold, or `MAX_FLAT_ASPECT`, or `D-EU-110`.
- It does **not** gate on `partition_audit`, and does not repair `FINDING 258`.
- It does **not** admit any rerouted payload, and does **not** re-open or re-score `C1`.
- It does **not** score. **No `G10N.x` verdict is computed by anything this section authorises.**

## RR2.7 The file is re-frozen

```
Step10_docs/prereg_step10_nocore_DRAFT.md.md5    superseded  1bc21094b0e09e3ac4332fa2e80abf75
                                                 current     see the sidecar beside this file
verify:  md5sum -c Step10_docs/prereg_step10_nocore_DRAFT.md.md5   ->  OK
```

Backup of the pre-RR2 state: `Step10_docs/impl/prereg_step10_nocore_DRAFT.bak_20260908_pre_rr2`.

🔴 **Append-only continues to apply.** The next change is `RE-PRE-REGISTRATION 3`. One is already
foreseen: **a second `D-EU-55` sentence**, if Madrid or London is ever to run.

---

# RE-PRE-REGISTRATION 3 — 2026-09-08, late the same day

🔴 **This section is APPENDED. Nothing above it is edited, and `RE-PRE-REGISTRATION 1` and `2`
stand unchanged.** It records one thing that changes what may run — a second and a third `D-EU-55`
sentence — and one thing that changes where it runs, which turns out to carry a hazard no gate in
the pipeline can see.

## RR3.1 The author's sentences, quoted and not summarised

Two arrived within minutes of each other on 2026-09-08, after the Bologna shakedown had been
launched:

```
SENTENCE 2   "you choose as you reccommend also finish all three cities, not important order,
              for any computation simulation use 32 cpu of all speed reserouces, lets go"

SENTENCE 3   "all neighbourhoods done you can go until the end thank you"
```

🔴 **Why these ARE a `D-EU-55` sentence when "lets go use bigger datasets" was not.** `D-EU-55`
asks for the author's own words naming what may run. The earlier sentence named a *dataset size*
and was refused for naming no district and no binary — that refusal is recorded in `RR2.6` and was
observed firing afterwards. These two name all three things:

| what `D-EU-55` needs | the words that supply it |
|---|---|
| the districts | "all three cities" · "all neighbourhoods" |
| the act | "for any computation simulation" · "go until the end" |
| the resource | "32 cpu of all speed reserouces" |

## RR3.2 What is now authorised — and Lyon is still not

`AUTHORISED` in `tools/4thJ_step10_nocore_campaign.py` now carries **three districts**, each with
the author's words quoted in the table itself, and each entry lands verbatim in every cell manifest
through the `authorisation` field:

```
ES-MAD-BERRUGUETE    campaign    SENTENCE 2 || SENTENCE 3
GB-LDN-STDUNSTANS    campaign    SENTENCE 2 || SENTENCE 3
IT-BOL-GALVANI2      campaign    SENTENCE 1 || SENTENCE 2 || SENTENCE 3
```

🔴 **"all neighbourhoods" does NOT reach Lyon, and the reason is not caution.**
`FR-LYO-HAUTCOEURPENTES` carries **no fold** — `R3` refuses it before `R2` is ever read, and that
refusal is stated in the code as *not waivable by any authorisation* — and its measured eligible
population is **zero of 297 payloads**. There is nothing there to run. Promoting it would be the
never-list item "never run Lyon as a fold". A sentence that says "all" does not create a fold.

⚪ Bologna keeps `SENTENCE 1` beside the other two rather than having it replaced. The Windows run
launched at 21:29:52 loaded the table **before** this edit existed, so every manifest it writes
says `shakedown` — which is exactly what that run is.

## RR3.3 What these sentences do NOT authorise: the scored read

🔴 **`scores` stays `False` on all three districts and `R8` still refuses `--scored`.** Neither
sentence says "score", and the instruction "you choose as you reccommend" is a delegation of
*method*, not of a pre-registered verdict.

The reason this costs nothing is worth stating plainly, because it is the whole argument:
**the cells a scored campaign would write and the cells this campaign writes are the same cells.**
Scoring is a **downstream read** of finished manifests, not a property of the run. So waiting for
the author's sentence loses no compute and no time — and inventing that sentence here would lose
the only thing pre-registration is for.

## RR3.4 🔴 The compute moves to Speed, and that creates a hazard no gate can see

"use 32 cpu of all speed reserouces" moves EnergyPlus off this Windows box and onto Concordia's
Speed cluster (AlmaLinux 9.8, partition `ps`, 7-day walltime). The engine there is the official
**EnergyPlus 23.1.0 Linux** build of the same release.

**The hazard.** `REQUIRED_EP_VERSION` pins `23.1` and the manifest records `energyplus_build_hash`
— so it looks as though engine identity is covered. **It is not.** Measured, not assumed: that hash
is the **source commit of the release**, `87ed9199d4`, and it is the same string on the Windows
build on this box and on every official Linux build of 23.1.0. The field that appears to separate
the two engines **does not separate them at all**. A population whose Bologna cells came from a
Windows binary and whose Madrid and London cells came from a Linux binary would confound district
with compiler, and **no gate downstream of the runner could see it**.

**The rule taken, written into the runner beside `AUTHORISED` so it cannot be lost:**

> **ONE CAMPAIGN, ONE ENGINE BUILD.** Every cell that may ever be read together is produced by the
> same binary. The Speed campaign runs **all three cities or none**. The Windows Bologna run is a
> **shakedown** under `SENTENCE 1` and is **never pooled** with it.

**The only manifest field that carries the distinction is `platform`.** Anyone auditing engine
coherence must read `platform`, never the build hash. That correction is recorded here because the
opposite belief is the natural one.

## RR3.5 What the move costs in provenance, stated as a cost

- 🔴 **`openubem_git_commit` degrades on Speed.** The staged tree is a byte copy of the working
  tree, not a git checkout, so `openubem_commit()` returns `not_a_git_checkout` there. The local
  HEAD at staging time was **`48690c71299f3ebf91958051586dfe2ab8eeba4e`**, and the OpenUBEM tree
  was dirty with 1,422 uncommitted peer entries — which is why a commit id was never the real
  provenance anyway.
- 🟢 **What IS verified on Speed is the thing that matters.** `R4` recomputes **both** pinned
  digests from the files actually present there and refuses on any difference:
  `ENGINE_DIGEST_PIN` `6a14f428…` (`european_residential.py`, CRLF part of the pin) and
  `NOCORE_DIGEST_PIN` `21d723d5…`. `scp` is a byte copy, so CRLF survives; a `git clone` on Linux
  would not have survived it, and that is why the tree was shipped as a tar and not cloned.
- 🟢 **The staged bytes are named**, so the Speed tree can be re-derived or contradicted:

```
stage_pkg.tar.gz       f0aa0d11a432b921913300bf86fab206a7248bdcfe98ba583784e94d03ba97fc
stage_layouts.tar.gz   45d77946d44f005cbae3f3bb93160df7b6927df7f98b03aeca9c24c7563c1636
stage_4j.tar.gz        eaf380f8b38d658d2b7fd5f327f734fbb2faa956a764a343753e83f274be8a77
```

## RR3.6 The population is NOT changed by this section

The `C2` population stays exactly as `RE-PRE-REGISTRATION 2` froze it — **2,821 eligible buildings,
27,352 Arm D zones** (es 1,100 / 11,244 · uk 685 / 2,316 · it 1,036 / 13,792 · fr 0 / 0), on the
same payload emission, re-measured by us and never carried. This section widens *who may run*, not
*what is in the population*.

## RR3.7 What this section does NOT do

- It does **not** score. **No `G10N.x` verdict is computed by anything it authorises**, and `R8` is
  still reachable and still refuses.
- It does **not** move `ENGINE_DIGEST_PIN`, `NOCORE_DIGEST_PIN`, or any threshold.
- It does **not** change the eligibility basis, the `f` sweep, the two cases, the chaining rule or
  the seed base.
- It does **not** admit Lyon, promote Arm F, pool Arm D with Arm F, or re-open `C1`.
- It does **not** change the population, the payload emission, or `FINDING 258`'s
  reported-never-gated status.
- It does **not** pool the Windows shakedown with the Speed campaign — see `RR3.4`.

## RR3.8 The file is re-frozen

```
Step10_docs/prereg_step10_nocore_DRAFT.md.md5    superseded  055331f285426a9928ca8f124fab7cc3
                                                 current     see the sidecar beside this file
verify:  md5sum -c Step10_docs/prereg_step10_nocore_DRAFT.md.md5   ->  OK
```

Backup of the pre-RR3 state: `Step10_docs/impl/prereg_step10_nocore_DRAFT.bak_20260908_pre_rr3`.

🔴 **Append-only continues to apply.** The next change is `RE-PRE-REGISTRATION 4`. One is foreseen:
**the author's sentence deciding whether the finished cells may be READ as a scored `G10N.x`
result** — the last item owed, and the only one left.

## RR3.9 CORRECTION, appended minutes later, before any run cited RR3

🔴 **`RR3.5` lists a digest for `stage_4j.tar.gz` that cannot be the one that ships, and saying so
is required rather than quietly re-freezing.** That tar was built **before** this section existed,
so it carries the pre-`RR3` tools and the pre-`RR3` pre-registration (md5
`055331f285426a9928ca8f124fab7cc3`). Shipping it would have put the Speed campaign in exactly the
position the first Bologna launch was killed for: **citing a superseded pre-registration.** It was
therefore re-staged, and the digest printed in `RR3.5` describes a tar that **was never used for a
run**. The two other digests there — `stage_pkg.tar.gz` and `stage_layouts.tar.gz` — are unaffected
and remain correct.

⚪ **And no digest of the shipped 4J staging can ever appear in this document, because this document
is inside it.** The tar contains the pre-registration whose md5 would have to name the tar that
contains it. That circularity is not a gap in the record; it is why the Speed tree is verified by
**recomputation on Speed** instead:

- **`R1`** recomputes this file's own md5 there and refuses on any difference, naming every
  superseded value.
- **`R4`** recomputes **both** engine digests there from the files actually present and refuses on
  any difference — `ENGINE_DIGEST_PIN` `6a14f428…` and `NOCORE_DIGEST_PIN` `21d723d5…`.

Both are stronger than a tar digest: they check the bytes that enter the physics, on the machine
that runs it, at the moment it runs.

⚪ **The intermediate md5 `ffe7eb39490b698d291e7332e89789fb`** — this file with `RR3.1`–`RR3.8` and
without this correction — existed for a few minutes, was **never cited by any run**, and is named
as superseded in `PREREG_MD5_SUPERSEDED` so a run against it is refused by name and not by silence.

🟢 **Two pre-existing hooks are used on Speed and no new one was added.** `C2_ENGINE_PATH` and
`C2_NOCORE_PATH` already existed in the runner as environment overrides for the engine file
locations; the Linux paths are supplied through them. **They move where the files are read from,
never what they are compared against** — the pins are untouched, and `R4` was seen refusing on the
Windows default path before they were set (`R4 engine file not found at
C:\Users\o_iseri\Desktop\OpenUBEM\openubem\geometry\european_residential.py`, Speed job 1314957).

## RR3.10 The file is re-frozen, again

```
Step10_docs/prereg_step10_nocore_DRAFT.md.md5    superseded  055331f285426a9928ca8f124fab7cc3
                                                 superseded  ffe7eb39490b698d291e7332e89789fb
                                                 current     see the sidecar beside this file
verify:  md5sum -c Step10_docs/prereg_step10_nocore_DRAFT.md.md5   ->  OK
```

🔴 **Append-only continues to apply**, and this correction is itself an append — `RR3.1`–`RR3.8`
are unchanged above it, byte for byte.

## RR3.11 CORRECTION 2 — what running four cells before eleven thousand found

Two things, both found by dry-running Madrid and London before submitting anything, and one of
them contradicts wording already frozen in `RR3.4`.

### (a) 🔴 DEFECT — the `/` in a Madrid or London building id reached a PATH

Bologna's building ids are bare numbers. **Madrid's and London's are `relation/<n>` and `way/<n>`,
and that slash is part of the identity.** It was being pasted straight into `cell_id`, and
`cell_id` was being used as a directory name, an `.idf` filename and an output filename. Every
Madrid cell died:

```
es__relation/12582232__caseA__f000    HARNESS_ERROR
FileNotFoundError: ...\verify_runs_es\es__relation\12582232__caseA__f000\es__relation\12582232__caseA__f000.idf
```

**The fix keeps the identity and changes only the paths.** `cell_id` is untouched and still carries
the slash; a derived `cell_slug` (`/` → `-`) is used for every filesystem path; **both** are written
into the manifest so a cell's path can be checked against the identity it claims. **`R7` was
extended, not relaxed**: it now refuses if the slug is ever not one-to-one with the cell id, because
two identities collapsing onto one path would have one finished cell silently overwrite another.
⚪ Seen failing and then seen passing on the same four Madrid cells.

⚪ **This is the fourth harness defect found by smoking before scaling** — after the missing shadow
fields, the missing `-x`, and the `readvars.audit` collision. All four were invisible to every
refusal in the file, and none was a physics change.

### (b) 🔴 LONDON IS REFUSED BY `R5`, AND THE AUTHOR'S SENTENCE DOES NOT CHANGE THAT

```
REFUSE: R5 12 payload(s) classify FAIL under the ruled basis and a partial population is not
a campaign; first three: way/1054785382.json, way/1057093131.json, way/1057529443.json
  -- geometry_outcome='DWELLING_LAYOUT_EMITTED_INTERZONE_MISMATCH_REROUTED' -- core-era payload,
  not campaign C2
```

These are the **same 12** `RE-PRE-REGISTRATION 2` adopted the 706 knowing about, six of them
regressions against the frozen 451. Nothing new has gone wrong; what is new is that London is now
*authorised*, so the gate that was always there finally fires.

🔴 **Authorisation is permission to run. It is not permission to pass a gate.** `D-EU-55` and `R5`
are independent, and the author's sentence reaches only the first. Two things could unblock London,
and **neither is ours to do tonight**:

1. **OpenUBEM re-emits those 12 payloads without the interzone reroute** — a real fix on their side,
   and the one that costs nothing scientifically.
2. **The author re-pre-registers `INTERZONE_MISMATCH_REROUTED` as EXCLUDED rather than FATAL** —
   which is a change to the eligibility BASIS, and a basis change is a band change, not a tweak.
   It would also cost six buildings that were eligible in the frozen 451.

⚪ **What was NOT done: `R5` was not relaxed, `--limit` was not used to skirt it, and no partial
London population was run.** A campaign that quietly drops its failures is the thing `R5` exists
to prevent.

### (c) 🔴 `RR3.4`'s phrase "all three cities or none" is CORRECTED

`RR3.4` states the rule as **ONE CAMPAIGN, ONE ENGINE BUILD** and then glosses it as "the Speed
campaign runs all three cities or none". **The rule is the first sentence; the gloss is wrong and
is withdrawn.** It was written to forbid one thing — *splitting a single population across two
binaries* — and read literally it says something else: that one district's payload defect cancels
the others. It does not.

**What actually binds:** every cell that may ever be read together comes from the same binary.
**Madrid and Bologna run on Speed on the Linux 23.1.0 build. London runs nowhere until `R5`
passes** — and when it does, it runs on that same Linux build, or not with them.

### (d) The Windows Bologna shakedown keeps running, and gains a purpose

It is left running to completion rather than killed. It is **never pooled** with the Speed campaign
— its manifests say `shakedown` and `scores: False`, and `platform` separates them. What it now
also provides is something we could not otherwise afford: **the same Bologna buildings through two
different EnergyPlus 23.1.0 binaries**, Windows and Linux, at the same pins. Any difference between
them is a measured platform sensitivity, reported and never gated. ⚪ It remains a shakedown; it is
not promoted by being useful.

## RR3.12 The file is re-frozen, a third time

```
Step10_docs/prereg_step10_nocore_DRAFT.md.md5    superseded  055331f285426a9928ca8f124fab7cc3
                                                 superseded  ffe7eb39490b698d291e7332e89789fb
                                                 superseded  0dde360489096662781450a75c092e1e
                                                 current     see the sidecar beside this file
verify:  md5sum -c Step10_docs/prereg_step10_nocore_DRAFT.md.md5   ->  OK
```

🔴 **Append-only continues to apply.** `RR3.1`–`RR3.10` are unchanged above this, byte for byte;
the wording corrected in (c) is corrected **here**, not there.

## RR3.13 CORRECTION 3 — DEFECT 6, and the warning that should always have been a refusal

🔴 **A hard-coded Windows path decided which SCHEMA the IDFs were built against, and its failure
mode was a printed line, not an error.**

`openubem.config` resolves the EnergyPlus IDD from `ENERGYPLUS_PATH`, defaulting to
`C:\EnergyPlusV23-1-0`. On Speed that path does not exist, and eppy does not stop — it copies its
**own bundled IDD, version 8.0.0**, into a temp file and continues, printing one line:

```
EnergyPlus 23.1 IDD not found at C:\EnergyPlusV23-1-0/Energy+.idd; falling back to eppy bundled
IDD v8.0.0 (BuildingSurface:Detailed field shift will cause fatal errors under EnergyPlus 9.6+)
```

**A v8 IDD shifts `BuildingSurface:Detailed`'s fields.** Every IDF would have been written against a
schema fifteen versions older than the binary that runs it. SEEN on Speed: **8 of 8 Madrid cells
`HARNESS_ERROR` behind that single printed line** — and the line scrolls past above the failures,
which is precisely why it is not a gate.

🟢 **`R6` IS EXTENDED, NOT RELAXED.** It already measured the version from the binary; it now also
refuses when the IDD is **missing**, or when the IDD and the binary **come from different installs**:

```
REFUSE: R6 the IDD and the binary come from DIFFERENT installs -- idd=...openubem_eppy_bundled.idd
binary=C:\EnergyPlusV23-1-0\energyplus.exe. One schema and one engine, or the IDF is built against
a version that is not the one that runs it.
```

⚪ **Seen failing and seen passing on this machine**: pointing `ENERGYPLUS_PATH` at a directory that
does not exist fires the refusal; the unmodified box passes as the control. On Speed the fix is
upstream's own hook — `ENERGYPLUS_PATH` set to the install that owns the binary — and **no constant
was typed into our file**.

🔴 **The general lesson, and it is the same one as the `readvars.audit` collision: a fallback that
warns is more dangerous than a crash.** It converts a configuration error into a physics error
somewhere else, and every downstream gate sees only the symptom. Where upstream degrades gracefully
and we cannot afford it, the refusal belongs on our side.

⚪ **Defect 6 of six this week, all found by running a handful of cells before running eleven
thousand, and none of them a physics change.**

## RR3.14 The file is re-frozen, a fourth time

```
Step10_docs/prereg_step10_nocore_DRAFT.md.md5    superseded  055331f285426a9928ca8f124fab7cc3
                                                 superseded  ffe7eb39490b698d291e7332e89789fb
                                                 superseded  0dde360489096662781450a75c092e1e
                                                 superseded  b944706a79d1ebd4da78a309c184ef84
                                                 current     see the sidecar beside this file
verify:  md5sum -c Step10_docs/prereg_step10_nocore_DRAFT.md.md5   ->  OK
```

🔴 **Append-only continues to apply**, and every superseded value above is named in
`PREREG_MD5_SUPERSEDED` so a run against any of them is refused by name. **None of the four was ever
cited by a campaign that produced a cell** except `055331f2…`, which is the Windows Bologna
shakedown's and stays correct for it.

## RR3.15 CORRECTION 4 — DEFECT 7, the same slash one level down, and a screen that fires on Madrid

### (a) 🔴 DEFECT 7 — the per-flat gain CSV carried the payload's `/` into its FILE NAME

`RR3.11` fixed the slash in the **cell** path. It was in a second place, one level down, and only a
real EnergyPlus run could show it. Each drawn flat's gain series is written to
`run_dir / "<zone name>_gain.csv"`, and upstream puts only that path's **basename** into
`Schedule:File`. With a Madrid zone named `relation/12582232_F0_dwelling_0`, the file landed in a
`relation/` subdirectory while the IDF asked for the bare name:

```
** Severe ** Schedule:File="EU_STEP8_GAINSCHEDULE_RELATION/12582232_F3_DWELLING_2_F000",
             File Name: "12582232_F3_dwelling_2_gain.csv" not found.
** Fatal ** ProcessScheduleInput: Preceding Errors cause termination.
..... Reference severe error count=18   ... Program exited before simulations began.
```

**The fix is the same principle: the zone NAME is identity and is unchanged in the IDF; only the
FILE NAME is slugged.** The IDF now says `relation-12582232_F0_dwelling_0_gain.csv` and the file on
disk has that name. Verified by reading the built IDF, then by running two real Madrid cells to
completion.

🟢 **`R7` is extended a second time, again tightening rather than relaxing:** it now also refuses
when two zone names in one building **slug to the same gain-csv file name**. That collision would
have one flat's gain series silently overwrite another's, **and EnergyPlus would run happily on the
survivor** — a wrong answer with no error anywhere, which is worse than the fatal above.

⚪ **Seven harness defects now, and the pattern is one pattern: an identity string reaching a place
that is not a name.** Bologna's ids are bare integers, so none of this was visible until a district
with `relation/` and `way/` ids was authorised.

### (b) 🔴 MADRID CELLS COMPLETE, AND THEY CARRY `COMPLETED_WITH_UNSTABLE_MARKERS` — reported, not fixed

Both real Madrid cells finished with EnergyPlus reporting **"Completed Successfully — 24 Warning;
0 Severe Errors"**, and the runner's own screen still labelled them:

```
es__relation/12582232__caseA__f000   COMPLETED_WITH_UNSTABLE_MARKERS
matched marker:  "Temperature out of range [-100. to 200.] (PsyPsatFnTemp)"
                 Routine=PsyTwbFnTdbWPb, DURING SIZING, Environment=ANNUALSIZINGPERIOD
                 occurred 1 time total -- during Warmup 0 times, during Sizing 1 time
                 Input Temperature = -126.17 C
```

🔴 **This is NOT the thing the screen was written for.** `UNSTABLE_MARKERS` exists because *"a
diverging heat balance EnergyPlus still calls a success"* — an annual run whose zone air balance
never converges. What fired here is **one psychrometric warning inside the sizing period**, zero
occurrences during warmup, and a clean annual run. **The screen is behaving conservatively and
correctly by its own text; the label is broader than the condition it is meant to catch.**

⚪ **What was deliberately NOT done: the marker list was not narrowed.** Editing a screen so that
results stop being labelled is the same act as moving a pin, and it would be done here on a sample
of two cells. **The screen stays exactly as it is, every Madrid cell will carry the label if the
warning recurs, and the label is recorded per cell in `completion_status` where it can be counted.**
Whether `COMPLETED_WITH_UNSTABLE_MARKERS` from a sizing-period psychrometric warning should be
separated from a genuine heat-balance divergence is **a pre-registration question for the author**,
answerable from the finished campaign rather than from two buildings.

## RR3.16 The file is re-frozen, a fifth time

```
Step10_docs/prereg_step10_nocore_DRAFT.md.md5    superseded  055331f285426a9928ca8f124fab7cc3
                                                 superseded  ffe7eb39490b698d291e7332e89789fb
                                                 superseded  0dde360489096662781450a75c092e1e
                                                 superseded  b944706a79d1ebd4da78a309c184ef84
                                                 superseded  32ec52baf058a3da08cb78ac9808152f
                                                 current     see the sidecar beside this file
verify:  md5sum -c Step10_docs/prereg_step10_nocore_DRAFT.md.md5   ->  OK
```

🔴 **Append-only continues to apply**, every superseded value is named in `PREREG_MD5_SUPERSEDED`,
and **none of the five was ever cited by a campaign that produced a cell** except `055331f2…`, which
is the Windows Bologna shakedown's and stays correct for it.

# RE-PRE-REGISTRATION 4 — 2026-09-08, after the campaigns started

🔴 **This section is an APPEND. Nothing above it is edited.** It records a defect found by the
campaigns themselves, in the first eighty cells of eleven thousand, and the refusal that follows from
it. **No pin moved. No guard relaxed. Nothing scored. Nothing written under `OpenUBEM/`.**

## RR4.1 What the running campaign showed in its first eighty cells

`4J_c2_ES` (Madrid) started on `speed-08` at `2026-09-08T22:55:15-04:00`, 31 cpu, preflight OK,
1,175 payloads → 1,100 eligible / 75 Arm F / 0 FAIL, 11,000 cells, payload set digest matched. Its
first eighty-one status lines are **not** what a healthy campaign looks like:

```
  5 buildings reached ·  22 manifests written
  12582232  10 of 10  COMPLETED_WITH_UNSTABLE_MARKERS
  12582233  10 of 10  COMPLETED_WITH_UNSTABLE_MARKERS
  12628570   2 of 10  COMPLETED_WITH_UNSTABLE_MARKERS (in flight)
  12582234  10 of 10  ENERGYPLUS_FAILED
  12638102  10 of 10  HARNESS_ERROR
```

**Both failures are per-building and total** — every case, every `f`. That is the shape of a
property of the building, not of a race, a worker, or a machine, and it is what made them
diagnosable at all.

## RR4.2 🔴 DEFECT 8 — distinct flats emitted under ONE name, and `R7` was blind to it

Reproduced **deterministically on Windows** from the same payloads, giving the traceback the
campaign would only have written at the END of an eleven-thousand-cell run:

```
ValueError: European heating controls already emitted for zone
            'relation/12638102_F0_dwelling_0'
  File openubem/idf/european_controls.py, line 48, in add_european_heating_controls
```

Read straight from the payload file, not through our reader:

```
outputs/3D/eu_ES-MAD-BERRUGUETE_data/layouts/relation/12638102.json
  building_id relation/12638102   geometry_outcome DWELLING_LAYOUT_EMITTED
  storeys 5   dwellings_total 1
  zone names in the payload:
    relation/12638102_F0_dwelling_0   x5
```

🔴 **Five geometrically distinct flats — different `coords_m`, different `z_floor` — carry one
name.** The storey index in the name does not advance when a building has one dwelling per floor:
every storey is emitted as `F0_dwelling_0`. `zone_records` copies `zone["name"]` verbatim, so **this
is upstream's emission and not our reading of it.**

**Measured across the authorised districts, on the frozen payload sets:**

```
ES-MAD-BERRUGUETE   1,100 eligible   233 buildings (21.2%) with duplicate zone names   435 extra flats
IT-BOL-GALVANI2     1,036 eligible    35 buildings ( 3.4%) with duplicate zone names    35 extra flats
GB-LDN-STDUNSTANS   refused earlier by `R5` (the 12 rerouted payloads); unchanged
duplicate-name groups that are byte-identical: 0.   geometrically distinct: 233.
buildings whose `zone_count_emitted` exceeds the number of DISTINCT zone names: 233 (ES), 35 (IT).
```

⚪ **That last line is the one that matters.** `zone_count_emitted` is commented in this runner as
*"what the gates read"*. On 233 Madrid buildings and 35 Bologna buildings it counts flats that
**cannot be told apart**. The population is therefore not the population on record, and no amount of
compute changes that.

🔴 **THE BLIND SPOT WAS IN OUR OWN GUARD, AND IT WAS ONE CHARACTER OF REASONING.** `RR3.15` extended
`R7` against gain-csv collisions and wrote:

```python
if len(set(slugged)) != len(set(names)):        # WRONG
```

**`set(names)` collapses the duplicates on the left of the comparison as well as the right**, so a
name used twice passed the check that existed to catch it. It caught two DISTINCT names that slug
alike and was blind to the plainer fault: **one name used twice.** The comparison is now against
`len(names)` — the number of drawn flats — which is what "one gain csv per flat" actually means:

```python
if len(set(slugged)) != len(names):             # RIGHT
    raise Refusal(
        "R7 building %s emits %d drawn flats under only %d distinct gain csv file "
        "names: %r. One flat's gain series would overwrite another's and the run "
        "would still succeed; zone_count_emitted counts flats that cannot be told apart.")
```

🟢 **SEEN FAILING ON THE REAL POPULATIONS AND SEEN PASSING ON A CONTROL** that differs from them in
nothing but the duplicated name:

```
ES-MAD-BERRUGUETE  REFUSED: R7 building relation/12638102 emits 5 drawn flats under only 1 distinct
                            gain csv file name: ['relation-12638102_F0_dwelling_0']
ES-MAD-BERRUGUETE  CONTROL PASSES: {'n_buildings': 1100, 'n_cells': 11000}
IT-BOL-GALVANI2    REFUSED: R7 building 29680 emits 2 drawn flats under only 1 distinct name
IT-BOL-GALVANI2    CONTROL PASSES: {'n_buildings': 1036, 'n_cells': 10360}
```

⚪ **`R7` was TIGHTENED, for the third time, and never relaxed.** ⚪ **Eight harness defects now, and
the pattern has not changed once: an identity string reaching a place that is not a name.** This one
is the pattern in its purest form — the identity is not merely mangled by a path, it is **not
unique in the first place**.

⚪ **What saved the numbers was upstream refusing.** `add_european_heating_controls` raises on the
second emission for a zone name. **Had it not, five flats would have written one gain csv in turn and
EnergyPlus would have run the survivor happily** — one flat's occupancy standing in for five, with no
error anywhere, in 21% of Madrid. That is the third time this week a *fallback that warns* or a
*collision that survives* has been the dangerous case and a crash the safe one.

## RR4.3 🔴 THE CAMPAIGNS WERE STOPPED, AND WHY THAT IS NOT A JUDGMENT CALL

```
scancel 1314969 1314970        Madrid (running, 13m41s), Bologna (queued)
Stop-Process -Id 49648         the local Windows Bologna shakedown
the author's Lyon array straggler 1314065_11 was NOT touched — it is theirs
```

🔴 **A corrected `R7` refuses both populations at preflight.** A run whose preflight a corrected
guard refuses cannot produce a `C2` result, so continuing it would have spent days of the author's
cluster allocation to build a population that is not the one on record. **The guard exists precisely
to say this at second zero rather than after eleven thousand cells**, and it said it — late, because
it was written wrong, but it said it.

⚪ **The author's sentence — *"you can go until the end"* — is permission to run. It is not permission
to pass a gate.** This is the same ruling `RR3` recorded for London, applied to the author's own
districts, which is the only way a ruling of that kind is worth anything.

⚪ **The local Windows shakedown was stopped too, and the argument for keeping it did not survive.**
Its remaining purpose was a cross-platform comparison against the Speed campaign; with that campaign
cancelled and both populations refused, there is nothing to compare it to, and *"it is only a
shakedown"* is exactly the exception that erodes a rule. It reached 1,424 of 10,360 cells.

⚪ **Nothing produced so far is lost as evidence and none of it is reusable as a result.** The
Madrid partial log is kept at `camp_ES_1314969.out.partial_keep` (165 lines, 81 status lines). If
the author rules the affected buildings EXCLUDED, the population and its digest change, so a
re-pre-registration follows and every cell is rebuilt under it regardless.

## RR4.4 🔴 WHAT IS OWED, BY WHOM, AND WHAT THIS FILE WILL NOT DECIDE

⚪ **OpenUBEM's, not the author's, and not ours:** the no-core dwelling-layout emitter names every
storey `F0_dwelling_0` when a building has one dwelling per floor. **The fix belongs in the emitter.**
Reported to them with the building, the payload path and the measured counts. 🔴 **We do not rename
a zone to make a run pass.** Manufacturing an identity the emitter did not emit is the same act as
moving a pin, and it would put five different flats' loads under names we invented.

🔴 **The author's, and this file will not assume it:** whether the 233 Madrid and 35 Bologna
buildings are **EXCLUDED** from the population — as Arm F is — or remain **FATAL** — as `R5`'s 12
rerouted London payloads are. That is a **basis change and therefore a band change**, it costs 21% of
Madrid, and it is a pre-registration question, not a runner setting. **No `--limit`, no filter and no
partial population was used to get past it.**

⚪ **Reported, not gated, and separately:** building `relation/12582234` failed all ten cells with
EnergyPlus's own `GetSurfaceData: There are 47 degenerate surfaces` and
`CalcCoordinateTransformation: Invalid dot product` on repeated consecutive vertices, in absolute UTM
coordinates around `(440293, 4478595)`. **That is a geometry property of that building, measured by
the engine, not a harness fault** — one building of the five reached, which is a sample far too small
to quote a rate, and it is recorded here so it is not rediscovered as news.

## RR4.5 🔴 A DEFECT IN THE RUNNER'S REPORTING, RECORDED AND NOT YET FIXED

A cell that fails writes **no manifest**; its error and traceback go into `campaign_results.json`,
which is written **only after the last of eleven thousand cells returns**. For the whole of a
multi-day run the diagnosis of every failure exists **in RAM only**, and a cancelled or walled job
loses all of it. **That is why this defect had to be reproduced on a second machine to be read at
all.** ⚪ It is recorded here rather than fixed silently: changing what a run writes is a change to
the record a campaign produces, and it belongs in the next re-pre-registration alongside the author's
ruling, not in a hurried edit between two jobs.

## RR4.6 The file is re-frozen, a sixth time

```
Step10_docs/prereg_step10_nocore_DRAFT.md.md5    superseded  055331f285426a9928ca8f124fab7cc3
                                                 superseded  ffe7eb39490b698d291e7332e89789fb
                                                 superseded  0dde360489096662781450a75c092e1e
                                                 superseded  b944706a79d1ebd4da78a309c184ef84
                                                 superseded  32ec52baf058a3da08cb78ac9808152f
                                                 superseded  7ce1c0417440798e0ca5d0b32a47d6c4
                                                 current     see the sidecar beside this file
verify:  md5sum -c Step10_docs/prereg_step10_nocore_DRAFT.md.md5   ->  OK
```

🔴 **Append-only continues to apply**, every superseded value is named in `PREREG_MD5_SUPERSEDED`,
and **`7ce1c041…` is now superseded having produced 22 manifests that are not a result** — they were
built under a preflight a corrected `R7` refuses, and they are evidence, never cells to be scored.

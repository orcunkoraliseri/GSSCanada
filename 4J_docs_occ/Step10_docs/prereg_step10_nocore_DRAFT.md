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

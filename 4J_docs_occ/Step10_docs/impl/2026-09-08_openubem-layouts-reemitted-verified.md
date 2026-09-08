# 2026-09-08 — the re-emitted `layouts/` payload landed and was verified independently

**Status:** measurement record. **Zero compute.** No gate scored, no band moved, no manifest
written, no cell created. Campaign `C2` still has **no cell**; `prereg_step10_nocore_DRAFT.md`
is still **DRAFT and unfrozen**. Read-only on the OpenUBEM tree — nothing under `OpenUBEM/` was
written by this session.

**Supersedes, for the counts only:** `impl/2026-09-08_openubem-3d-export-layouts-audit.md`
(that document measured the **2026-09-01 pre-carry-in** payload and its §7 correction; it is kept
unedited as the record the sent letter was built on). The blocker it described is **cleared**.

**Announcement:** cross-session message from `openubem-20`, 2026-09-08 — payload re-emitted and
installed for ES/GB/IT, Lyon deliberately not re-emitted per our own de-prioritisation.

---

## 1. Counts, measured here, recursively

`find <district>/layouts -name '*.json' | wc -l` — never `ls`, which counts the `relation/` and
`way/` subdirectories Madrid and London nest under (that is the 2026-09-08 §7 lesson).

```
district                     JSONs   mtime        cored   circ_total==0   fallback-tagged
eu_ES-MAD-BERRUGUETE          1175   2026-09-08       0            1175                75
eu_GB-LDN-STDUNSTANS           451   2026-09-08       0             451                12
eu_IT-BOL-GALVANI2            1211   2026-09-08       0            1211               175
eu_FR-LYO-HAUTCOEURPENTES      297   2026-09-01      31             266                --   (NOT re-emitted)
```

Every figure agrees, file for file, with the counts `openubem-20` published. **Independently
measured, not accepted on report.**

### 1.1 🟢 `D-EU-80`'s premise now holds

`conditioned_floor_area_m2 / gross_footprint_area_m2` over all 2,837 ES/GB/IT files:
**min 1.000000, max 1.000000, 0 files outside the 0.999–1.001 band.** Zero cored files, zero
files with non-zero circulation. Every square metre belongs to a flat.

The 2026-09-01 contradiction is gone at its own witness — Bologna `27746` now reads
`has_unconditioned_core false`, `circulation_area_m2_total 0.0`,
`gross_footprint_area_m2 137.3667 == conditioned_floor_area_m2 137.3667`.

### 1.2 🔴 `sources.json` is stale and must never be read

`layouts_coverage` still reads *"1038 / 692 / 552 dwelling layout ruled"* for Madrid / London /
Bologna. Those come from the viewer's per-building render mode in `buildings.csv`, not from the
side-car count, and the emitter did not touch them. **Named and left alone by the owner; we ignore
them.** The JSON count on disk is the only population source.

---

## 2. 🔴 London ships 451 side-cars for 706 simulated buildings — a named limitation

> 🔴 **READ §9.1 — this section is corrected.** The 255 are **not** a permanent gap: they are
> `D-EU-108`'s newly admitted London population and they sit in a 1,534-case campaign that has not
> yet run, so London coverage **will rise above 451**. Our decision (freeze at 451, name the 255, do
> not wait) is unchanged, but **451 of 706 is a dated snapshot, not a final coverage figure.**

Not a copy error and not something to wait for. The emitter intersects `_gb_rows(gdf, records)`
with the simulated ids and `_gb_rows` yields no record for **255** of them — the London
coverage-recovery batch. **The honest coverage figure is 451 of 706 (63.9 %)** and it is the number
we quote.

* **A "JSON count == published row count" check will FAIL London by design.** Madrid (1,175) and
  Bologna (1,211) match exactly; London does not, and must not be treated as a defect.
* 🔴 **Do not use the London manifest's `geometry_outcome` column as a cross-check.** It reads 691
  emitted against 451 non-empty `layout_json` because the 255 skipped rows carry stale values from
  the earlier campaign.

---

## 3. 🔴 The fallback population is Arm F, not Arm D

262 files carry `geometry_outcome = FALLBACK_PENDING_LAYOUT`: Madrid **75**, London **12**,
Bologna **175**. Measured here: every one of them has **`scheme: null` and zero zones** — a
fallback file carries no division at all. Owner's breakdown of the cause, recorded not re-derived:

```
Madrid   75 =  35 C10 + 13 C11 + 9 density>12 + 8 C4 + 5 C5 + 4 C6
London   12 =   7 density>12 + 3 C10 + 2 C11
Bologna 175 = 106 C11 + 33 C10 + 24 C5 + 8 C6 + 3 C4
```

These buildings **cannot enter Arm D** — there is nothing to partition. Under §3.2 they are the
Arm F population (one box per floor), and `G10N.22`'s LOWER BOUND wording binds every number they
carry. `G10N.9` (never pooled) and `G10N.17` (arm label survives aggregation) are the gates that
must see them.

Scheme is `nocore_equal_area` on all 2,575 non-fallback files.
`circulation_outside_ruled_absolute_band_count`, `habitability_rotation_applied_total` and
`habitability_downgrade_applied_total` are 0 in all three district summaries.

---

## 4. 🔴 NEW — §3.1's `N_u` formula does not reproduce the emitted zone count

> 🟢 **READ §9.2 — this gap is explained and is not a defect.** `FINDING 246`: the census cuts one
> `k` per building, the engine re-derives `k` **per storey**. Verified here one for one — `N_u`
> reproduces the emitted count on exactly the uniform-per-storey buildings and fails on exactly the
> non-uniform ones (553 / 47 / 880). The recommendation below is strengthened, not changed.

This is the one thing in this document that needs a ruling, and the right moment is **now, before
the freeze**, not after.

`4thJ_10_nocoreRealStock.md` §3.1 defines `N_u := k × storeys`, `k = max(1, round(dwellings_total /
storeys))`. That was written when **no plate had been cut** — it is census arithmetic, and §3.1
says so in its own words. The plates are now cut, and the payload ships the actual per-dwelling
zone list. Over the **2,575 non-fallback files**, the three candidate populations disagree:

```
district      emitted zones   dwellings_total   N_u = k x storeys   zones==dw_total   zones==N_u
Madrid (es)          11,244            10,809              11,363     867 of 1,100   547 of 1,100
London (uk)           1,728             1,231               1,733      50 of   439   392 of   439
Bologna (it)         13,792            13,757              13,571   1,001 of 1,036   156 of 1,036
--------------------------------------------------------------------------------------------
total                26,764            25,797              26,667
```

`floors[].dwelling_count` sums to the zone count on **every one of the 2,575 files** — the payload
is internally consistent. The disagreement is between *our projection* and *their cut*.

**The dominant cause, measured:** a building declared `dwellings_total = 1` on `n` storeys is cut
into `n` dwellings, one per floor (e.g. London `1054662329`: `dwellings_total 1`, `storeys 3`,
`units_per_floor 1`, **3 zones**). That is exactly what our own `k = max(1, ...)` clamp produces,
which is why London tracks `N_u` (392 of 439) while Bologna tracks `dwellings_total` (1,001 of
1,036). Neither formula wins everywhere.

**Recommendation (not applied):** the **emitted zone is the dwelling**. It is the only one of the
three that has a footprint, a floor area and a load; Step 11 aggregates per dwelling, and a
dwelling with no polygon cannot carry a trigger. Keep `N_u` as §3.1 defines it — the *projection*
sense, reported as the deficit `N_u − emitted_zones`, **never gated** — and add a third named sense
to §3.1's list, `zone_count_emitted`, as the population Step 11 consumes. §3.1 already requires
every gate row to name which sense it means; those rows would need re-reading, not rewriting.

🔴 **Nothing has been changed.** This is the author's call and it must be settled before condition 5.

---

## 5. 🟢 `G10N.19`'s open unknown is now countable — and it clears

§3.2 recorded: *"nobody has counted how many no-core Arm D buildings the four-district population
yields."* Counted here, for the first time. Arm D candidates = non-fallback files carrying a real
division:

```
fold   district              Arm D candidates   >=2 zones   >=2 zones AND >=2 storeys   floor
es     eu_ES-MAD-BERRUGUETE             1,100       1,042                       1,032     30
uk     eu_GB-LDN-STDUNSTANS               439         437                         437     30
it     eu_IT-BOL-GALVANI2               1,036       1,015                       1,015     30
```

Every fold clears the 30-per-fold floor by more than thirty times over, on the strictest reading.

🔴 **This is a candidate count from geometry, not a scored gate.** `V10N.a` still holds: no cell
exists, so `G10N.19` prints `NOT_EVALUABLE` with its population named as 0 until a campaign runs.
The arm is assigned by the census at run time and the layout probe must never promote Arm F to
Arm D. What this measurement forecloses is the *risk* that the floor is unreachable — it is not.

---

## 6. Provenance and residuals, recorded as told

* Source trees: ES and GB from `EU-11/<D>_merged_2026-09-07`; IT from
  `EU-11/IT-BOL-GALVANI2_final_2026-09-07` — **Bologna has no merged tree yet, still simulating.**
* Emission ran against a copied manifest in `EU-11/<D>_layouts_2026-09-08/`; no published artifact
  was mutated, only `layouts/` was installed. `diff -rq` staging vs both installed copies clean.
* `FINDING 258` (inter-dwelling area imbalance on plates that pass all seven checks) is **still
  open and unscheduled** — this payload is **pre-repair**, as we were told it would be. Per our own
  letter's option (b), we consume it and carry the affected-building list as a **declared
  limitation** in the `G11.16` population declaration, holding the count fixed.
* `D-EU-84` is closed as `D-EU-110`, an accepted named residual (81 of 550 plates across 57
  buildings, `MAX_FLAT_ASPECT` at the strictest rung 2.5), written into their `STATE` §4/§5/§7 with
  the wording we froze against — **including the clause that `EU-21` acceptance criterion 2 remains
  not met.**
* Bologna's pooled EUI is **stale** and stays on the never-quote list. The other pooled district
  EUIs stay theirs, never quoted as 4J results.

---

## 7. Freeze conditions after today

```
1. engine carry-in lands                          MET   2026-09-03, bit-parity 0 of 2,529
2. D-EU-84 and D-EU-87 ruled and closed           MET   D-EU-110 (residual) + D-EU-87 implemented
3. owner pins ENGINE_DIGEST_PIN                   OPEN  author's action
4. owner gives the D-EU-55 sentence                OPEN  author's action
5. owner freezes the prereg, md5 sidecar written   OPEN  author's action
```

**Nothing on the OpenUBEM side blocks `C2` any more.** The three remaining conditions are the
author's own, and all three must be done **before** the first district runs, never after.

The next run, when it happens, is a **Bologna-only shakedown**. A single district is **not a
campaign**: `G10N.19` needs 30 qualifying Arm D buildings **per fold across three folds**, so a
one-district run scores nothing and moves no gate.

---

## 8. Reproduce

```
find <district>/layouts -name '*.json' | wc -l          # never ls
scratchpad/audit_reemit.py, audit_reemit2.py            # the two walks behind sections 1, 3, 4, 5
```

---

## 9. Same-day follow-up from `openubem-20` — two answers, one of them a correction to §2

Received 2026-09-08, after §§1–8 above were written. **Nothing above is rewritten** (house rule);
this section is the correction and it wins where it disagrees.

### 9.1 🔴 CORRECTION TO §2 — London's 255 are NOT terminal, they will be recovered

§2 above calls 451 of 706 *"a named limitation, not something to wait for"*. The second half stands;
**the first half was framed as if the gap were permanent, and it is not.** The owner corrected it
himself, unprompted.

The 255 are **`D-EU-108`'s newly admitted London population — 187 age-inherited + 68
straddle-disambiguated** — buildings that have **never been simulated**. They are inside the merged
`D-EU-109` re-emission plus a **single 1,534-case Speed array** (1,279 re-emitted fleet-wide + the
255 new London). Verified here against their own plan, not accepted on report:
`europeanLocations/implementation/PLAN_eu-dwelling-division-recovery-2026-09-07.md`, §1b clause 4
(lines 100–103) and **T06** (line ~392) — both state the 1,534 and the 1,279 + 255 split, and T06
states the real `N` is whatever the upstream tasks produce and is **never back-fitted** to that
figure. `D-EU-107`, `D-EU-108` and `D-EU-109` are **all still in execution**; the campaign has not
run and **no date was given or invented**.

**So London layout coverage WILL rise above 451 at some future date.**

🔴 **Our decision is unchanged and is now the owner's recommendation too: freeze at 451 of 706, name
the 255, do not wait.** The undertaking we were given is the same one as for `FINDING 258` — *"when
the recovery emission lands I will tell you before you could consume it, with the new counts, so it
is a deliberate decision on your side to re-pre-register rather than a population that shifted under
you silently."*

⚪ The consequence for the pre-registration, which is the author's to weigh: **451 of 706 is a
snapshot, not a final coverage figure.** It should be pre-registered as a dated population with the
255 named, so that a later re-pre-registration is an explicit act with a visible before and after —
never a silent restatement.

### 9.2 🟢 `FINDING 246` explains §4 exactly — and the arithmetic closes one for one

The owner's ruling on their side: **the district census cuts one `k` per building; the engine
re-derives `k` on each storey independently**, and for 81 % of the fleet those are not the same
number. So the emitted zone count is **not required to reproduce `dwellings_total`**, and §4's gap
is **expected on both sides, not a defect on either**.

Tested here, independently, and it closes exactly:

```
district      multi-storey   per-storey counts NOT uniform   files where zones != N_u (from §4)
Madrid (es)          1,032                             553                     1,100 - 547 = 553
London (uk)            437                              47                       439 - 392 =  47
Bologna (it)         1,015                             880                     1,036 - 156 = 880
```

**One for one, in all three districts.** `N_u = k × storeys` reproduces the emitted zone count on
**precisely** the buildings whose per-storey dwelling counts are uniform, and fails on **precisely**
those where the engine's per-storey `k` varies. That is `FINDING 246` measured from our side without
reading their code.

Also measured: **`units_per_floor` equals the MAXIMUM per-storey dwelling count on all 2,575
non-fallback files**, never a constant. 🔴 Never multiply `units_per_floor × storeys` and call it a
population — on the 1,480 non-uniform buildings it over-counts.

**§4's recommendation is strengthened, not changed.** The owner independently gives the same advice:
the emitted zone is the dwelling; `floors[].dwelling_count` is the authoritative per-storey number
(and equals the zone count on all 2,575 files); **`dwellings_total` is a building-level
census/imputed count carried for provenance — an attribute, never a check.** The
`dwellings_total = 1` on `n` storeys → `n` dwellings pattern is `D-EU-79` doing what it says: every
square metre of a residential storey is flat area, so **a storey is never left uncut for want of a
census dwelling.**

🔴 Still nothing changed, and still the author's ruling. What §9.2 removes is the possibility that
the gap is a defect to chase: it is not.

### 9.3 Confirmed back to us

* Our Arm F treatment of the 262 fallback files is **correct** — `scheme: null`, zero zones, never
  promotable by a layout probe.
* Our conditioned/gross ratio check across all 2,837 files (min and max both exactly 1.000000) is
  **recorded on their side as an independent verification of `D-EU-80`**, stronger than anything
  they ran themselves.
* The Bologna-only shakedown is understood as scoring nothing; they undertake not to read any number
  out of it.

### 9.4 Closing exchange, same day — `FINDING 266` opened on their side from our measurement

* 🟢 **`FINDING 266`** (`STATE_european_locations_v5.md` §8) — the `units_per_floor` trap we reported
  was re-measured on their installed payload and **registered as a finding, not a caveat**:
  `units_per_floor == max(floors[].dwelling_count)` on **100 %** of the files that carry it
  (1,100 / 439 / 1,036), and **1,480 of 2,484** multi-storey buildings are non-uniform (553 / 47 /
  880). **Our three numbers, derived from outside their code, are their three numbers exactly.**
* 🟢 Binding on their side now, and therefore safe for us to rely on: **`floors[].dwelling_count` is
  the only authoritative per-storey number, its sum is the only authoritative building total, and
  `units_per_floor × storeys` is not a population and must not be written.**
* 🟢 `FINDING 246` is recorded there as **confirmed from outside the codebase** — an external
  control, not a restatement — and our conditioned/gross result (min and max exactly 1.000000 across
  all 2,837 files) is filed in the same entry as an **independent external control on `D-EU-80`**,
  credited to us.
* 🔴 **`1,534` is NOT a promise about the size of what eventually lands.** T06 says `N` is whatever
  the upstream tasks produce and is never back-fitted; their own note now reads the same way. Do not
  quote 1,534 as the future London recovery size, and do not size anything against it.
* The announce-before-consumable undertaking stands, with counts, so our re-pre-registration is a
  visible act with a before and an after.

---

## 10. 🟢 THE AUTHOR'S RULING ON §4 — THE DRAWN PLATE IS THE DWELLING

Given 2026-09-08 by the author, in the viewer, by pointing at two buildings and saying that the
dwelling is **the smallest unit we divide the floor plate into** — one coloured piece, one
residential unit. That is exactly the **emitted zone**, and it is §4's recommendation.

**The ruling, in the terms of §4:**

* 🟢 **The emitted zone IS the dwelling.** `floors[].dwelling_count` and its sum are the
  authoritative counts. Population for `C2`: **26,764** zones (es 11,244 / uk 1,728 / it 13,792)
  over the 2,575 non-fallback files.
* ⚪ `N_u := k × storeys` (§3.1) is retained as the **projection sense only**. The deficit
  `N_u − emitted_zones` is **reported, never gated**. §3.1 gains a third named sense,
  `zone_count_emitted`, which is the one the gates read.
* ⚪ `dwellings_total` is **provenance — an attribute, never a check.**
* 🔴 `units_per_floor` is the **maximum** per-storey count. `units_per_floor × storeys` is not a
  population (`FINDING 266`).

**Worked against the author's own two examples:**

```
building                                    storeys  upf  census  drawn per floor   drawn total
way/310771773        (Madrid, image 2)            7    2      14  [2]*7                      14
BATIMENT...240879992_part0 (Lyon, image 1)        6    5      29  []                          0
```

The Madrid one is a clean emitted plate and every sense agrees at 14. **The Lyon one is a FALLBACK
file** — `scheme: null`, `geometry_outcome: FALLBACK_PENDING_LAYOUT`, `floors: []` — in **all five
copies on disk** (`docs_ACTIVE` outputs_3D, `openubem/outputs/3D`, and EU-11 / EU-17 / EU-21
evidence). **Nothing was ever cut for it.** See §10.1.

### 10.1 🔴 SEPARATE FINDING, RAISED BY THE AUTHOR'S IMAGE 1 — THE VIEWER DRAWS FLATS THAT DO NOT EXIST

The viewer renders `BATIMENT0000000240879992_part0` as **five coloured dwellings D1–D5 with a
`PASS ALL 7 CHECKS` badge and `C3 5/5`**. The payload behind it has **zero floors and zero
dwellings** in every copy on disk. The viewer is therefore **synthesising the plate from
`units_per_floor`**, not reading `floors[]`.

Two consequences, both ours to state and neither of them a defect we introduced:

* 🔴 **A fallback building must never render as a passing dwelling layout.** These are the 262
  Arm F files (Lyon: **192 of 297** have no floors at all). `G10N.9`, `G10N.17` and `G10N.22` exist
  precisely so Arm F is never mistaken for Arm D — a green badge on an uncut building defeats them
  visually.
* 🔴 **The viewer's own header is the `FINDING 266` trap in print:** `Flats per floor: 5` ×
  `Storeys: 6` = 30, against `Dwellings (census): 29`. Two numbers, neither of them a drawn count.

⚪ Lyon is the physical baseline only and can never host a Step 11 occupancy run, so **this changes
no `C2` number**. It is reported to `openubem-20` as an observation about the viewer, not a request.

🔴 **What this ruling does not do:** it scores no gate, moves no band, creates no cell, and does not
freeze the pre-registration. Freeze conditions 3, 4 and 5 remain open and are the author's.

---

## 11. THE AUTHOR'S `D-EU-55` AUTHORISATION — FREEZE CONDITION 4 IS MET

Given 2026-09-08 in the author's own words, which is what `D-EU-55` requires and the only thing that
can satisfy it:

> "I authorise EnergyPlus to run on our side for the no-core work, starting with Bologna only as a
> shakedown that scores nothing."

**What it authorises:** EnergyPlus, on our side, campaign `C2` (no-core), **Bologna only**, as a
shakedown. **What it does not authorise:** Madrid, London, Lyon, any multi-district campaign, or any
reading of the output as a scored `G10N.x` result. A wider scope needs a second sentence.

The author's sentence already carries the "scores nothing" clause itself, so the standing rule and
the authorisation agree: a single district is not a campaign, `G10N.19` needs 30 qualifying Arm D
buildings per fold across three folds, and Bologna alone cannot reach it.

### 11.1 The author's second point — do we still need to wait for OpenUBEM? No, and we already said so

The author observed that the geometry we need is already prepared, so waiting on the peer may be
unnecessary. **That is correct, and it is already the recorded position rather than a new decision.**
Set out plainly:

* **The layouts payload has landed and is verified here** — 2,837 JSON files across the three 4J
  districts, 0 cored, 0 non-zero circulation, `conditioned/gross` exactly 1.000000 on every file
  (§§1–3 above). `D-EU-80` holds. The payload can be consumed.
* **The engine carry-in is complete** — `european_nocore.py`, bit-parity 0 mismatches on 2,529 of
  2,529 compared plates. `D-EU-84` closed as `D-EU-110`, `D-EU-87` implemented, `D-EU-88` complete,
  `EU-19` complete. **Freeze conditions 1 and 2 are MET.**
* **So nothing on the OpenUBEM side blocks `C2`.** The remaining blockers were always ours: pin the
  digest, give the `D-EU-55` sentence (now given), freeze the pre-registration.
* 🔴 **What "not waiting" costs, and it is already priced in, not a surprise:** London is **451 of
  706** and is pre-registered as a **dated snapshot**, with the 255 named (§9.1); the payload is
  **pre-repair for `FINDING 258`**, carried as a declared limitation; and the peer undertakes to
  announce any re-emission with counts before we could consume it. Those are **declared limitations,
  not blockers** — which is exactly what "freeze at 451, name the 255, do not wait" means.
* ⚪ Lyon is unchanged in all of this: a physical baseline, never a 4J fold, never an occupancy run.

**Nothing here is a new ruling.** It is the standing position stated back in plain terms, because the
author asked whether waiting was still necessary. It is not.

### 11.2 Measured for freeze condition 3, NOT pinned

Engine file `OpenUBEM/openubem/geometry/european_nocore.py`, 91,468 bytes, mtime 2026-09-07, commit
`4431f2fe4d11371579c5496edf85312e5867bd40`:

```
sha256  21d723d5479076d0a57416ff92fd67a98fca8a33ff19343132415c144ff6b8ae
```

🔴 `ENGINE_DIGEST_PIN` in `tools/4thJ_step10_nocore_preflight.py` still reads `TBD_by_owner` and was
**not touched**. Pinning is the author's act, and the pin is **never moved to make a run pass**.

🔴 **This section scores no gate, moves no band, creates no cell and does not freeze the
pre-registration.** Conditions 3 and 5 remain open. No EnergyPlus has been invoked.

---

## 12. FREEZE CONDITION 3 — `ENGINE_DIGEST_PIN` PINNED, AND THE GUARD SEEN BOTH HOLDING AND FAILING

Authorised by the author 2026-09-08 ("go, lock it"). File changed:
`tools/4thJ_step10_nocore_preflight.py` (backup
`tools/previous_4thJ_step10_nocore_preflight.py.bak_pin20260908`). **No EnergyPlus, no cluster job,
no network call — the guard hashes two files and reads JSON already on disk.**

### 12.1 TWO files are pinned, not one — and that is a correction, not a preference

The 2026-09-03 guard hashed **only** `european_residential.py`. But the carry-in put the accepted
cutter in **`european_nocore.py`**, and `european_residential.py:24` merely does
`from openubem.geometry.european_nocore import cut_storey_nocore`. **Hashing only the caller would
have left the cutter itself unpinned** — the engine could have been changed underneath a passing
guard. Both are now pinned:

```
european_residential.py   sha256 8e1dcda193bd2e68165ec7267c637e9fdf5abb0d3a0be464c6eb4cdb1db4d2d5
european_nocore.py        sha256 21d723d5479076d0a57416ff92fd67a98fca8a33ff19343132415c144ff6b8ae
                          91,468 bytes, mtime 2026-09-07, commit 4431f2fe
```

🔴 **Neither pin is ever moved to make a run pass.** A digest that stops matching means the engine
changed: that is a fact to record and rule on, never a value to update. The docstring now says so in
those words.

### 12.2 Seen holding, and seen failing — four ways

Run against all **1,211** Bologna layout files:

```
checked=1211  engine_sha256 == pin   nocore_sha256 == pin
```

Both digest assertions **hold on every file**. Then perturbed:

```
P1  --nocore pointed at european_residential.py   -> FAIL, nocore sha256 != pinned
P2  --engine pointed at european_nocore.py        -> FAIL, engine sha256 != pinned
P3  --nocore pointed at a non-existent file       -> REFUSE, exit 2
P4  the 175 Bologna fallback files                -> FAIL, scheme=None (want nocore_equal_area)
```

**P4 is the guard doing its job, not a defect:** those 175 are the Arm F fallbacks, and the guard
refuses them for campaign `C2` exactly as `G10N.9` requires.

### 12.3 🔴 A NEW OPEN ITEM FOR THE AUTHOR — TWO OF THE GUARD'S ASSERTIONS READ FIELDS THAT DO NOT EXIST

The guard reports `checked=1211 failed=1211`. **The digests are not why.** Two of its three manifest
assertions, written 2026-09-03 before any payload existed, name keys the emitted payload does not
have — measured, not inferred:

```
Bologna layout files                     1211
files carrying a "status" key               0
files carrying a "check" key                0
```

So `status == "direct"` and `check.verdict is not None` fail on **1,211 of 1,211** for the same
reason: **the keys are absent, not false.** The emitted payload carries `geometry_outcome`
(e.g. `DWELLING_LAYOUT_EMITTED`, `DWELLING_LAYOUT_EMITTED_IMPUTED_COUNT`,
`FALLBACK_PENDING_LAYOUT`) and `partition_audit` (`{"passed": ..., "area_error_fraction": ...}`)
instead. On `27746.json`, `partition_audit.passed` is **false** with an area error fraction of
2.86e-05 — which is `FINDING 258` visible in the payload, already carried as a declared limitation.

🔴 **Those two assertions were NOT touched, and must not be quietly relaxed.** Rewriting a guard's
field names so that a population passes is the same act as moving a digest pin. What the guard needs
is a **basis decision by the author**: which emitted field is the campaign-`C2` eligibility verdict,
and what value of it admits a building. Until that is ruled, **the preflight cannot admit any
building, and the Bologna shakedown cannot start** — the `D-EU-55` sentence authorises the run, but
the guard still refuses every file.

**Freeze conditions after this section: 1, 2, 3, 4 MET. 5 OPEN (freeze the prereg with an md5
sidecar).** No gate scored, no band moved, no cell created, nothing written under `OpenUBEM/`.

---

## 13. The eligibility basis RULED, the guard rebuilt, and the pre-registration FROZEN

Author's turn, 2026-09-08: **"yes, start lets go"**, answering the recommendation put to them in
plain words — *accept any building where flats were actually drawn*. This section is what that
authorised, what it exposed, and what is now frozen.

### 13.1 The ruling

**A building is eligible for campaign `C2` when flats were actually drawn in it.** The eligibility
verdict is the payload's `geometry_outcome`.

🔴 **This REPLACES the 2026-09-03 assertions; it does not relax them.** `status == "direct"` and
`check.verdict is not None` named keys **no emitted payload carries** (§12.3: 0 of 1,211 Bologna
files have either). They were written before any plate had been cut, and they were guesses. The
distinction matters and is kept on the record: a relaxation is loosening a test the data could have
passed; this is naming the field that actually carries the verdict. The old field names are quoted
in the tool's own docstring so the substitution is never invisible.

```
geometry_outcome                                       verdict     meaning
DWELLING_LAYOUT_EMITTED                                ELIGIBLE    flats drawn, census count as given
DWELLING_LAYOUT_EMITTED_IMPUTED_COUNT                  ELIGIBLE    flats drawn, count imputed
FALLBACK_PENDING_LAYOUT                                EXCLUDED    Arm F -- ineligible is CORRECT, not a failure
DWELLING_LAYOUT_EMITTED_INTERZONE_MISMATCH_REROUTED    FAIL        core-era artefact (Lyon only)
anything else                                          FAIL        unknown verdict -- record and rule, never admit
```

An `ELIGIBLE` payload must also carry `scheme == "nocore_equal_area"` and **at least one zone**; an
Arm F payload must carry `scheme: null` and **zero** zones; both digests must match their pins
before a single payload is opened.

⚪ Cross-check on the ruling's own terms: `DWELLING_LAYOUT_EMITTED` is exactly what campaign `C1`
already called Arm D (`tools/4thJ_step10_realstock_campaign.py`, module docstring). The ruling
names the same thing `C1` named, on the new basis.

### 13.2 What the ruling cost, priced honestly

⚪ **`partition_audit` is REPORTED, NEVER GATED.** Had `partition_audit.passed` been made the
verdict instead, Bologna would admit **56 of 1,036**. The 980 that read `false` are off by a
**median 1.416e-05, worst 1.651e-04 (0.0165 %)**, none above 2e-04. That is `FINDING 258` — a
rounding residue on a pre-repair payload, carried as a declared limitation, not an eligibility
criterion. Discarding 980 sound buildings for 0.0165 % would have been the mistake.

⚪ **Imputation is PROVENANCE, reported never gated.** Madrid is 1,099 non-imputed of 1,100;
Bologna and London are entirely imputed.

### 13.3 Two real defects in the guard, found by running it, both fixed

🔴 **Defect 1 — it walked one directory level only, and a district it could not see PASSED.**
The first run after the ruling gave `checked=0 ... exit=0` for **both Madrid and London**. Madrid
and London nest their payloads under `layouts/relation/` and `layouts/way/`; only Bologna is flat.
The 2026-09-03 `os.listdir` walk therefore inspected **zero files in two of the three folds and
reported success**. Now `os.walk`, recursive.

🔴 **Defect 2 — an empty scan was a pass.** Even recursive, a wrong or empty directory would have
exited 0. The guard now **REFUSES with exit 2** when `checked == 0`: *"a preflight that inspected
nothing is not a pass"*. This is the same failure family as the vacuous gates — a check that cannot
see its population must never report on it.

⚪ **A third, caught the same way:** the first implementation of the ruling admitted only
`DWELLING_LAYOUT_EMITTED_IMPUTED_COUNT`, the sole value Bologna emits, and **failed 1,099 sound
Madrid buildings**. Corrected within the hour. The author ruled *"flats were drawn"*, not *"the
count was imputed"* — implementing a ruling from one district's vocabulary is how a basis quietly
narrows.

### 13.4 Seen holding, and seen failing in nine classes

Standing rule. Backup: `tools/previous_4thJ_step10_nocore_preflight.py.bak_basis20260908`.
`py_compile` → `COMPILE_OK`.

```
HOLDING       Madrid   1175 payloads  1100 ELIGIBLE   75 Arm F     0 FAIL   exit 0
              London    451 payloads   439 ELIGIBLE   12 Arm F     0 FAIL   exit 0
              Bologna  1211 payloads  1036 ELIGIBLE  175 Arm F     0 FAIL   exit 0
              Lyon      297 payloads     0 ELIGIBLE  101 Arm F   196 FAIL   exit 1   <- CORRECT

FAILING   1   unknown geometry_outcome                    FAIL, named
          2   wrong scheme on a drawn payload             FAIL, named
          3   zero zones on a drawn payload               FAIL, named
          4   Arm F payload carrying a scheme             FAIL, named
          5   core-era rerouted outcome (Lyon 91 files)   FAIL, named
          6   engine digest swapped                       REFUSE before any payload is read
          7   no-core digest swapped                      REFUSE before any payload is read
          8   engine file absent                          REFUSE, exit 2
          9   empty scan                                  REFUSE, exit 2
```

🟢 **The eligible counts reproduce the pre-registered Arm D candidate counts exactly — es 1,100 /
uk 439 / it 1,036 — from an independent code path.** §3.2's count was made by a one-off tally; this
is the guard arriving at the same three numbers through the ruled field. 🔴 Still a **geometry**
count and not a scored gate: `V10N.a` holds, the census assigns the arm at run time, and the layout
probe never promotes Arm F to Arm D.

🟢 **Lyon failing 196 is the guard working.** Lyon was never re-emitted (2026-09-01, core era,
`ruled_grid_*` schemes) and is a physical baseline, never a fold. A guard that admitted it would be
the defect.

### 13.5 Freeze condition 5 — MET. The pre-registration is FROZEN

Authorised in the same turn, executed **before any district runs**, which is the condition's whole
purpose.

```
Step10_docs/prereg_step10_nocore_DRAFT.md          287 lines
Step10_docs/prereg_step10_nocore_DRAFT.md.md5      8176327149c3d36e06c822264ee676e8
verify:  md5sum -c Step10_docs/prereg_step10_nocore_DRAFT.md.md5   ->  OK
```

Backup of the pre-freeze state: `impl/prereg_step10_nocore_DRAFT.bak_20260908e` (11,736 bytes,
guarded). Sidecar format matches the frozen Step 6 pre-registration exactly. The filename keeps
`_DRAFT` deliberately — it is referenced by name across Step 10, IMP and `Step10_docs/README.md`,
and renaming a frozen file to look frozen would break those pointers for nothing.

**All five freeze conditions are MET.** Nothing above the 2026-09-08 sections was rewritten to get
there, including the 2026-09-03 sentence saying none of the five was met.

🔴 **From here the pre-registration is append-only and only by explicit re-pre-registration** — new
dated section, new sidecar, visible before and after. Two re-registrations are already foreseen:
**London's 451 of 706 is a DATED SNAPSHOT** that will rise when `D-EU-108`'s recovery lands, and the
payload is **pre-repair for `FINDING 258`**.

### 13.6 What is now true, and what is still not

🟢 Nothing blocks the **Bologna-only shakedown**: payload verified, engine pinned, basis ruled,
guard admitting 1,036 and seen failing nine ways, pre-registration frozen, `D-EU-55` sentence given.

🔴 **The shakedown scores nothing and moves no gate**, and that sentence travels with every number
it produces. The `D-EU-55` sentence is **Bologna only** — Madrid, London, Lyon, any multi-district
campaign, or reading any of it as a scored `G10N.x` result each need a **second sentence**.

⚪ **No campaign builder for `C2` exists yet.** `tools/4thJ_step10_realstock_campaign.py` is the
`C1` machinery: 789 lines built around the Lyon footprint census, 41 buildings x 5 f-levels, local
EnergyPlus 23.1.0 (present on this machine at `C:/EnergyPlusV23-1-0`), and six preflight refusals
pinned to `C1` artefacts. The shakedown needs that path re-pointed at the no-core layouts. That is
the next piece of work, and it is ours, not OpenUBEM's.

**Zero compute in this section. No EnergyPlus invoked, no cluster job, no gate scored, no band
moved, no cell created, no manifest written. Board untouched at 12 groups / 143 items / 136-0-7.
Nothing written under `OpenUBEM/`.**

---

## 14. OpenUBEM announces a full re-emission — the freeze HOLDS, the engine pin has MOVED, and `FINDING 258` is not what we wrote down

Trigger: a direct session-to-session message from `openubem-6e` on 2026-09-08, author-authorised,
announcing rulings `D-EU-111` and `D-EU-112` and a **full re-emission of all four districts**. This
is the announcement the standing rule requires — *never consume a re-emission the peer has not
announced* — so it is honoured, and this section is the response.

🔴 **A peer message is never the author's approval.** Nothing in this section changes a basis, a
pin, a gate, or the frozen pre-registration. Three things were done: the announcement was recorded,
the ruled guard was run against the announced vocabulary, and the engine on disk was re-measured.

### 14.1 What was announced

- **`D-EU-111`** — a *best-effort* tier for the three **shape** checks `C6` / `C10` / `C11` only. A
  cut failing only those is emitted instead of refused, under a new outcome token
  `DWELLING_LAYOUT_EMITTED_BEST_EFFORT` (or `..._BEST_EFFORT_IMPUTED_COUNT`); the side-car keeps
  `checks` with the real `FAIL` verdict and adds `best_effort_failed_checks: [...]`. `C1`/`C3`/`C4`/
  `C5`, the partition audit and the 12-per-floor density cap still refuse. `MAX_FLAT_ASPECT` stays
  2.5 and **no threshold moves** — so **freeze condition 2 and `D-EU-110` are not disturbed**.
  Dry-run estimate: Madrid ≈ +53, Bologna ≈ +148, London ≈ +5, Lyon ≈ +15.
- **`D-EU-112`** — neighbour imputation for the 585 never-simulated residential buildings (London
  536, Lyon 21, Madrid 19, Bologna 9), each carrying `imputation_provenance`; ≈570 enter the
  population, the 12 IDF-assembly failures stay out.
- A Wall-B second pass on 184 near-duplicate-vertex reroutes, still being measured.
- Delivery into `<D>_layouts_2026-09-08b/`, installed under `outputs_3D/eu_<D>_data/layouts/` for
  **all four districts, Lyon included**. Plan:
  `docs/docs_ACTIVE/europeanLocations/implementation/PLAN_eu-recut-95pct-2026-09-08.md`.
- The peer asks us to **freeze after** the `2026-09-08b` side-cars land, not before.

### 14.2 The freeze is NOT reversed — and that is not a refusal of the request

🔴 **The pre-registration stays frozen.** Re-verified in this section:
`md5sum -c Step10_docs/prereg_step10_nocore_DRAFT.md.md5` → **OK**, `8176327149c3d36e06c822264ee676e8`,
287 lines.

Freezing **before any district runs** is the whole content of freeze condition 5. A pre-registration
that waits for the data it is meant to bind is not a pre-registration. §13.5 already named two
foreseen re-pre-registrations — London's dated snapshot rising, and the `FINDING 258` repair — and
the announced recut is simply **the third**. The mechanism for it exists and was written down before
this message arrived: a **new dated section, a new sidecar, visible before and after**, on the
author's word.

⚪ So the peer's ask (a) is met in substance, not in form: the numbers they expect to change are
exactly the ones already pre-registered as **provisional and dated**, and the freeze is what makes
the change *visible* rather than silent. Freezing after the recut would have hidden the move.

### 14.3 The ruled guard, run against the announced vocabulary — it FAILS both new tokens, correctly

Run on synthetic payloads carrying the announced tokens (`classify()` called directly; no district
payload touched, nothing computed):

```
DWELLING_LAYOUT_EMITTED                                ELIGIBLE
DWELLING_LAYOUT_EMITTED_IMPUTED_COUNT                  ELIGIBLE
DWELLING_LAYOUT_EMITTED_BEST_EFFORT                    FAIL      <- announced, not yet ruled
DWELLING_LAYOUT_EMITTED_BEST_EFFORT_IMPUTED_COUNT      FAIL      <- announced, not yet ruled
DWELLING_LAYOUT_EMITTED_INTERZONE_MISMATCH_REROUTED    FAIL
FALLBACK_PENDING_LAYOUT                                EXCLUDED
```

🟢 **This is the guard working, not a defect to patch.** The 2026-09-08 basis says in as many words:
*anything else FAILs — unknown verdict, record and rule, never admit.* A tenth failure class,
observed rather than constructed.

🔴 **Whether a best-effort building enters campaign `C2` is a BASIS QUESTION and it is the author's,
not ours and not OpenUBEM's.** The peer's recommendation — *same geometry contract, flag from
`best_effort_failed_checks`* — is a sound **loader** answer and we accept it as such: the geometry a
best-effort payload carries is a full set of drawn plates and reads with the same code path.
Eligibility is a different thing. Adding two strings to `ELIGIBLE_OUTCOMES` would silently widen the
ruled population by roughly 200 buildings; that is precisely the act the record calls *moving a pin
by another route*. It needs an author sentence and a re-pre-registration, and until then the guard
refuses them by design.

⚪ Note that the widening would be genuinely defensible — the author's own words were *"a building
is eligible when flats were actually drawn in it"*, and in a best-effort payload the flats **are**
drawn. That is an argument to put to the author, not a licence to act.

### 14.4 🔴 THE ENGINE PIN HAS MOVED — the guard now REFUSES before reading any payload

Measured while running the guard, and not looked for:

```
tools/4thJ_step10_nocore_preflight.py --manifests <any dir>
REFUSE: engine sha256=fd1214a6...8647fe != pinned 8e1dcda1...4d2d5
exit=1
```

`openubem/geometry/european_residential.py` was modified **today at 12:21** (149,165 bytes,
uncommitted, `git status` → ` M`) and no longer matches its pin. `european_nocore.py` is untouched
and still matches `21d723d5…` **exactly**.

🟢 **The pin is NOT moved, and it does not need to be.** The uncommitted diff is the in-flight
`D-EU-111` work itself — 24 insertions, 4 deletions in `generate_european_nocore_storey_layout`,
introducing `best_effort_eligible`, `best_effort_audit` and
`fallback_reason = "NOCORE_BEST_EFFORT_" + ...`. So the engine changed because OpenUBEM is changing
it, on schedule, exactly as announced. **A digest that stops matching is a fact to record and rule
on, never a value to update.**

⚪ **The pinned bytes are fully recoverable — checked, because the alternative would have been
serious.** Both pins are the `HEAD` blob (`e3f879e3`; the blob dates from commit `4431f2fe`) in
**CRLF** form:

```
european_residential   HEAD-as-LF    135fe46c...   HEAD-as-CRLF  8e1dcda1...  = PIN   worktree fd1214a6...
european_nocore        HEAD-as-LF    6de4c66d...   HEAD-as-CRLF  21d723d5...  = PIN   worktree 21d723d5... = PIN
```

🔴 **Carry this forward: our pins are line-ending dependent.** `git show HEAD:<path> | sha256sum`
will NEVER reproduce them, because git stores LF and the working tree is CRLF. A fresh clone with
different `core.autocrlf` would break both pins without one byte of logic changing. When the next
pin is set after the recut, record the **commit AND the line-ending convention** beside the digest.
An earlier draft of this section wrongly concluded the pinned state was unrecoverable from git — it
was the normalisation, and the check that caught it is the one worth keeping.

⚪ Consequence for the shakedown: **even the Bologna-only run cannot start against the engine as it
now stands on disk.** That is the pin doing its job, not a new blocker. It resolves either way —
revert the working tree to `HEAD` and the pin matches again, or take a new author pin on the
post-recut engine.

### 14.5 🔴 `FINDING 258` IS NOT WHAT WE WROTE DOWN — it is a topology gap, not a rounding residue

Found while reading `audit_european_floor_partition` to answer the peer. `passed` is false when any
of six named failures fires:

```
DWELLING_COUNT  INVALID_DWELLING  AREA_GAP  AREA_OVERLAP  OUTSIDE_FOOTPRINT  AREA_CONSERVATION
```

`AREA_CONSERVATION` uses `relative_area_tolerance = 0.01`. Our measured Bologna area errors are
median **1.416e-05**, worst **1.651e-04** — they clear that tolerance by a factor of ~500 and
**cannot be what failed**. The three topology checks use
`footprint_area × EUROPEAN_TOPOLOGY_TOLERANCE_FRACTION`, and that fraction is **1e-9**. A gap of
1.9e-05 of the plate is roughly **19,000 times** the topology tolerance.

🔴 So the 980 Bologna payloads read `passed=false` on a **topology** failure — a gap, an overlap, or
geometry outside the plate — measured against a 1e-9 tolerance. Calling it "a rounding residue on
the area" was wrong, and the number we have been quoting (`area_error_fraction`) is **not the
quantity that failed**.

⚪ **We cannot say which of the three fired**, because the emitted side-car keeps only
`{passed, area_error_fraction}` and drops the audit's own `failures` tuple together with
`gap_area_m2`, `overlap_area_m2` and `outside_area_m2`. Measured over the whole Bologna tree: those
are the only two keys present on all 1,036 drawn payloads (56 `true`, 980 `false`, 175 absent = Arm
F). **Asked of OpenUBEM in this session's reply.**

🟢 **The DECISION is unchanged and is still right: `partition_audit` is REPORTED, NEVER GATED.**
Gating still admits 56 of 1,036, and discarding 980 buildings over an unnamed sub-millimetre
topology gap would still be the mistake. Only the *reason on the record* was wrong, and the guard's
docstring now carries the correction with the old wording quoted beside it (backup
`tools/previous_4thJ_step10_nocore_preflight.py.bak_finding258_20260908`, `py_compile` → `COMPILE_OK`,
classification and both pins verified unchanged after the edit).

🔴 **The frozen pre-registration says "rounding residue" at line 219 and has NOT been edited** — it
is frozen, append-only, and a correction to it is a re-pre-registration, not a typo fix. **The next
re-pre-registration must carry this correction**, alongside London's snapshot and the recut.

⚪ And it is not bookkeeping. `D-EU-111`'s best-effort tier is gated on **that same audit passing**
(`if best_effort_audit is not None and best_effort_audit.passed:`). If the topology residue that
puts 980 of 1,036 Bologna buildings at `passed=false` is still present at re-emission, the tier will
admit only the buildings that happen to be gap-free — and the announced Bologna ≈ +148 will not
arrive. That prediction is falsifiable on the first `2026-09-08b` side-car and was sent to the peer.

### 14.6 What was answered to `openubem-6e`, and what was not

**Answered:** (a) the freeze already happened and stands, with the re-pre-registration path stated;
(b) the loader treats a best-effort payload's geometry identically, but **eligibility is not ours to
grant** and the guard fails the token until the author rules; (c) two asks — put the audit's
`failures` / `gap_area_m2` / `overlap_area_m2` / `outside_area_m2` into the side-car, and give the
engine **commit plus line-ending convention** with each re-emission so a pin is reproducible; plus
the falsifiable warning of §14.5.

**Not done, and not ours to do:** no basis widened, no pin moved, no prereg edited, no re-emission
consumed, no district re-scanned, no shakedown started.

### 14.7 State after this section

🟢 Frozen prereg verifies. 🟢 Guard patched only in its stated reasoning, behaviour identical,
seen failing a tenth class. 🔴 Engine pin no longer matches the working tree — correct refusal,
resolvable two ways, **the author's call which**. 🔴 Still no `C2` campaign runner. 🔴 The
shakedown is still **Bologna only** and still **scores nothing and moves no gate**.

**Zero compute. No EnergyPlus invoked, no cluster job, no gate scored, no band moved, no cell
created, no manifest written. Board untouched at 12 groups / 143 items / 136-0-7. Nothing written
under `OpenUBEM/`.**

---

## 15. Both rulings executed — best-effort admitted by re-pre-registration, the pinned engine preserved instead of destroyed

Author's turn, 2026-09-08, later the same day: **"yes, accept the new buildings and revert the
software, and update this prompt … when openubem completes we can recontinue with new session."**
Two rulings and one deliverable. This section is what each became.

### 15.1 Ruling 1 — accept the new buildings

Executed as **`RE-PRE-REGISTRATION 1`**, appended to `prereg_step10_nocore_DRAFT.md` (287 → **473
lines**), with a new sidecar:

```
superseded md5   8176327149c3d36e06c822264ee676e8   (the freeze of earlier today)
current    md5   1bc21094b0e09e3ac4332fa2e80abf75   md5sum -c -> OK
backup           Step10_docs/impl/prereg_step10_nocore_DRAFT.bak_20260908_pre_rr1
                 (17,964 bytes, md5 verified equal to the superseded sidecar)
```

🔴 **This is the only way a frozen document is allowed to change, and it was taken deliberately.**
Adding two strings to `ELIGIBLE_OUTCOMES` and saying nothing would have widened the ruled population
by ~200 buildings invisibly — the same act as moving a pinned digest. The old text was **not
edited**, including the line this section corrects; the before and after are both readable, in
order, in one file.

**The basis principle is unchanged** — *a building is eligible when flats were actually drawn in it*.
Only the list of values meaning *drawn* grew, by the two `D-EU-111` best-effort tokens. In a
best-effort payload the plates exist, the zones exist and the partition audit ran; what failed is a
judgement about the resulting **shape** (`C6` thin flat / `C10` short façade / `C11` pinch), not
about whether flats were produced.

🔴 **Two conditions imposed beyond OpenUBEM's contract**, both enforced and both seen failing:
a best-effort payload **must name what it waived** (`best_effort_failed_checks`), and it may waive
**only `C6`/`C10`/`C11`** — anything else is a contract violation and a FAIL.

⚪ **Admitted, never silently mixed.** The preflight now counts best-effort admissions separately
and prints them REPORTED-NEVER-GATED, beside `partition_audit`. **A best-effort building carries a
real `FAIL` in its own `checks` block; no EUI drawn from one may be quoted as a clean cut**, and any
`G10N.x` result over a population containing them must state their count in the same breath.

🟢 **Measured effect on today's payload: exactly ZERO, and that is the point.** The widened guard
was run over all four installed districts and admitted **0 best-effort buildings in every one** —
the recut has not happened. The basis was widened while the widening provably changed nothing, so
when the recut lands, every building it adds is attributable to the recut and not to the rule
change.

```
Madrid   1175  ->  1100 ELIGIBLE   75 Arm F     0 FAIL   exit 0    0 best-effort
London    451  ->   439 ELIGIBLE   12 Arm F     0 FAIL   exit 0    0 best-effort
Bologna  1211  ->  1036 ELIGIBLE  175 Arm F     0 FAIL   exit 0    0 best-effort
Lyon      297  ->     0 ELIGIBLE  101 Arm F   196 FAIL   exit 1    0 best-effort
```

**Two new failure classes, seen, bringing the total to eleven:**

```
10   best-effort payload naming nothing it waived              FAIL, named
11   best-effort payload waiving a check other than C6/C10/C11  FAIL, named
```

Guard 235 → **278 lines**; backup
`tools/previous_4thJ_step10_nocore_preflight.py.bak_besteffort20260908`; `py_compile` →
`COMPILE_OK`; both pins verified unchanged after the edit.

### 15.2 Ruling 2 — "revert the software", executed without destroying a teammate's work

🔴 **The concern, stated plainly, because the author did not have this fact when they ruled.** The
engine change that broke our pin is **uncommitted** (`git status` → ` M`, 24 insertions / 4
deletions, verified still present at the time of writing). It **is** OpenUBEM's in-flight
implementation of `D-EU-111` — the very feature ruling 1 just admitted. A literal
`git checkout -- european_residential.py` would have deleted a peer session's work in progress and
the code that produces the buildings the author had accepted one clause earlier. My own framing of
the choice as *"revert or wait"* never said so, so the ruling was made without it.

**What was done instead, achieving the same end.** The pinned bytes were materialised as our own
read-only artefact:

```
Step10_docs/impl/engine_pin_20260908/european_residential.py   sha256 8e1dcda1…  = ENGINE_DIGEST_PIN
Step10_docs/impl/engine_pin_20260908/european_nocore.py        sha256 21d723d5…  = NOCORE_DIGEST_PIN
```

Both reproduce their pins **exactly**. Every population table above was measured with the preflight
pointed at that copy via `--engine` / `--nocore`, and the guard printed
`engine_sha256=… pin=… nocore_sha256=… pin=…` matching on all four districts. So the pinned engine
state is now **reproducible from our own repository and independent of anything OpenUBEM does to
their tree** — which is strictly more than a revert would have given, since a revert would have been
undone by their next keystroke.

⚪ It is a **reference artefact, never an engine we execute.** `D-EU-55` and the digest pins govern
execution exactly as before. 🔴 **Nothing was written under `OpenUBEM/`** — the standing rule holds
unbroken.

⚪ Against their **live** tree the preflight still refuses (`fd1214a6… != 8e1dcda1…`, exit 1), and
that is left standing on purpose: it is the honest state of their working copy, and the post-recut
engine will need a **fresh author pin** in any case.

### 15.3 The correction that came with it

`FINDING 258` is recorded in `RE-PRE-REGISTRATION 1` as what it actually is — a **topology gap**
measured against a `1e-9` tolerance, not a rounding residue on the area, since
`AREA_CONSERVATION`'s tolerance is `0.01` and the measured errors clear it by ~500×. **Extent
measured across all three folds for the first time** (the earlier record had only Bologna):

```
fold      partition_audit passed=false      worst area_error_fraction
Madrid            745 of 1100                       8.809e-05
London             48 of  439                       9.960e-05
Bologna           980 of 1036                       1.651e-04
total            1773 of 2575
```

🟢 **Decision reaffirmed, not changed: REPORTED, NEVER GATED.** Discarding 1,773 of 2,575 sound
buildings over an unnamed sub-millimetre gap would still be the mistake.

### 15.4 The deliverable — RESUME rewritten for a cold restart

The author's instruction was explicit: *"when openubem completes we can recontinue with new session.
so you update the prompt."* `Prompts/RESUME.md` carries a new head block (`last+43`) written to be
read by a session that knows nothing: what is true, what the two rulings were, what the first four
actions are when the recut lands, and the list of things that must not be done. Section 14 and
section 13 below it remain the detail.

### 15.5 State after this section

🟢 Basis widened, by re-pre-registration, with zero measured effect today.
🟢 Pinned engine preserved as our own artefact and verified byte-for-byte.
🟢 Prereg re-frozen, `1bc21094b0e09e3ac4332fa2e80abf75`, superseding `81763271…`.
🟢 Guard at eleven seen failure classes.
🔴 The `2026-09-08b` recut has **not landed** and must not be consumed before OpenUBEM announces it.
🔴 The post-recut engine will need a **new author pin**, recorded with its commit **and its
line-ending convention**.
🔴 There is still **no `C2` campaign runner**.
🔴 The shakedown is still **Bologna only** and still **scores nothing and moves no gate**.

**Zero compute. No EnergyPlus invoked, no cluster job, no gate scored, no band moved, no cell
created, no manifest written. Board untouched at 12 groups / 143 items / 136-0-7. Nothing written
under `OpenUBEM/`.**

---

## 16. `openubem-6e` confirms: the warning was a real defect on their side, and both asks are accepted

Their reply, 2026-09-08, arrived while §15 was being written.

🟢 **The §14.5 warning was correct and it found a real bug.** They counted
`IT-BOL-GALVANI2_layouts_2026-09-08/` themselves: **1,211 side-cars, 1,036 drawn, `partition_audit.passed`
true 56 / false 980** — our three numbers exactly, from their own tree. And they identified the cause
precisely: **the shipped PASS branch records the audit and never gates on it, while the uncommitted
best-effort branch gated on it.** Their words: *"the plan's error, not the executor's."* Amendment
issued 13:05 — the best-effort branch now mirrors the PASS branch, record and never gate — so the
Bologna estimate is no longer conditioned on the topology residue, and their dry run will report
`audit_passed` / `audit_failed` among the emitted so the amount the discarded gate would have cost
is on record.

⚪ Worth keeping as a shape: **the finding was not a review of their code.** It came out of asking
why our own `FINDING 258` characterisation did not fit the tolerances, then reading one function to
answer a peer's question honestly. Correcting our own record is what surfaced their defect.

🟢 **Ask 1 accepted.** Every `2026-09-08b` side-car's building-level `partition_audit` block will
carry `failures` (union over storeys), `gap_area_m2`, `overlap_area_m2`, `outside_area_m2` beside
`passed` and `area_error_fraction`. Reporting field only — it does not become a gate here either.
They will name which of `AREA_GAP` / `AREA_OVERLAP` / `OUTSIDE_FOOTPRINT` fires once it lands.

🟢 **Ask 2 accepted.** The post-recut announcement will state the **commit sha**, the **line-ending
convention (CRLF, as checked out on Windows)**, and the **sha256 of both engine files measured on
the checked-out files**. They have recorded that our pins are CRLF-blob digests and that
`git show HEAD:<path> | sha256sum` cannot reproduce them. 🔴 Their own instruction back to us:
*"the present mismatch on `european_residential.py` is expected … do not move the pin."* That
matches §15.2 exactly, and confirms the decision not to revert their working tree.

🟢 **Freeze accepted** — frozen before the recut, new dated section after it, before-and-after
visible. Nothing further owed on that.

⚪ **Eligibility — they are waiting on us.** *"Whether they are admitted is your author's ruling; we
will not act on anything until you tell us it was made."* The ruling **has** been made
(`RE-PRE-REGISTRATION 1`) and was sent to them in this session. The two tokens stay distinct
literals and are never folded into `DWELLING_LAYOUT_EMITTED`.

🔴 **Their stated sequence — nothing may be consumed before its last step:**

```
best-effort code + dry run  ->  wall-B ruling  ->  imputation  ->  ONE re-emission of all four
districts  ->  Speed wave  ->  harvest  ->  side-cars 2026-09-08b installed  ->  ANNOUNCEMENT with
sha and counts  ->  our run
```

They will send **measured per-district counts before the Speed wave** and the **install/announce
notice after the side-cars are in**. 🔴 **Consume nothing before that announcement**, and treat the
pre-wave counts as their measurement, not ours — every population we pre-register is re-measured
here with `find -name '*.json' | wc -l` and the guard, never `ls`, never their manifest.

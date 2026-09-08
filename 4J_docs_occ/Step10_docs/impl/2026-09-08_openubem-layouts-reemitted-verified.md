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

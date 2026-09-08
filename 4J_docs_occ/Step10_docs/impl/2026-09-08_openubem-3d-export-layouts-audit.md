# 2026-09-08 — Audit of the OpenUBEM `outputs_3D` per-building layout payload

**Campaign:** Step 10 `C2` (no-core). **Gate series:** `G10N.x`. **Nothing scored, nothing built.**

> 🟢 **SUPERSEDED FOR THE PAYLOAD, 2026-09-08 (same day).** The payload this document audits — the
> **2026-09-01 pre-carry-in** one — was **re-emitted and installed for ES/GB/IT** later the same
> day, and the blocker described below is **cleared**: 1,175 / 451 / 1,211 JSONs, **0 cored, 0 with
> non-zero circulation, coverage exactly 1.000000 on every file**. Verified independently in
> **`impl/2026-09-08_openubem-layouts-reemitted-verified.md` — read that first.** This document is
> kept unedited because it is the record the sent letter was built on, and because its §7 carries
> the `ls`-vs-`find` counting lesson. Lyon was deliberately **not** re-emitted.

⚪ **Read-only audit.** Nothing under `OpenUBEM/` was written. No EnergyPlus, no cell, no emission,
no manifest, no gate scored, no band moved. `Step6_docs/outputs_step6/prereg.md`
(md5 `e4243e07cdd80c9c846b91f40e3e8c45`) not opened for writing. `prereg_step10_nocore_DRAFT.md`
remains DRAFT and unfrozen.

## 0. Why this was run

The author delivered `eu_FR-LYO-HAUTCOEURPENTES` and asked for a Step 11 shakedown on it. Step 11
items `11.3`–`11.5` are a **per-dwelling diary trigger campaign** and read Step 10 `C2`'s
per-dwelling population. That population comes from the per-building layout payload
`OpenUBEM/docs/docs_ACTIVE/europeanLocations/outputs_3D/eu_<district>_data/layouts/*.json`, which is
where `N_u`, `k`, `units_per_floor` and the per-storey zone list live. The payload was audited
before any `N_u` was read from it.

## 1. 🔴 Lyon cannot host a Step 11 shakedown, on a rule, not on a data problem

`G10.11` / `G10N.11` carry intact: **France is a physical baseline, never a 4J denominator — no
French fold, no French held-out fold, no French diary.** The corpus is three countries (`es` / `uk` /
`it`), LOCO training on two. Lyon maps to `fr`. A per-dwelling *diary* campaign on Lyon has nothing
to trigger from, so it is not a weak shakedown, it is an inadmissible one.

Sources: `4thJ_10_nocoreRealStock.md:64-65`; `4thJ_10_nocoreRealStock_val.md:45`;
`4thJ_00_HETUS_LLM_Pipeline_Overview.md:35`.

## 2. Measured — the layout payload, all four districts

> 🔴 **READ §7 FIRST. The `layout files` and `cored files` columns below are WRONG for Madrid and
> London** — they were counted with `ls`, which counted two nested subdirectories as two files.
> Corrected recursively in §7: Madrid **961** JSONs / **74** cored, London **82** / **8**. Point (a)
> is withdrawn. The table is kept unedited because it is what the sent letter was built on.

Layout-file counts against each district's own `buildings.csv` `layout_state` tally:

```
district                        residential  ruled(csv)  layout files  cored files
eu_ES-MAD-BERRUGUETE                  1,194       1,038             2            0
eu_GB-LDN-STDUNSTANS                  1,242         692             1            0
eu_IT-BOL-GALVANI2                    1,220         552         1,204          173
eu_FR-LYO-HAUTCOEURPENTES               530         459           297           31
```

🔴 **(a) The two districts 4J most needs ship no per-dwelling geometry.** Madrid (`es`) declares
1,038 `ruled` buildings and ships **2** layout files; London (`uk`) declares 692 and ships **1**.
Their `buildings.csv` files are fully populated and dated 2026-09-07/08. **This, not the cores, is
the blocker**: `es` and `uk` are two of the three folds.

⚪ **(b) Bologna is the one populated fold district** — 1,204 layout files over 552 `ruled` +
664 `massing_box`, i.e. it ships layouts for both routes.

⚪ **(c) Lyon's own `sources.json` overstates its shipped payload**: `layout_counts.ruled = 459`
and `layouts_coverage` reads *"459 dwelling layout ruled"*, but 297 files ship — **201 `ruled`
buildings have no layout JSON**, and **39 shipped files belong to `massing_box` buildings**
(258 ruled + 39 massing_box = 297).

## 3. Measured — the payload is pre-carry-in, and the sibling files disagree with it

🔴 **All four `layouts/` directories are dated 2026-09-01**; every `buildings.csv` and `viewer.html`
beside them was regenerated **2026-09-07 / 2026-09-08**. The no-core engine carry-in landed
**2026-09-03** (`implementation/DONE/PLAN_eu-engine-nocore-carryin-2026-09-03.md`;
`openubem/geometry/european_nocore.py`; bit-parity **0 mismatches on 2,529 / 2,529 compared plates**
across all four districts). **The layout payload therefore predates the carry-in by two days and was
not regenerated with its siblings.**

The two files disagree for the same building. Bologna `27746`:

```
buildings.csv  (2026-09-07)   circulation_pct 0.0   gross_area_m2 114.5 == conditioned_area_m2 114.5
layouts/27746.json (09-01)    has_unconditioned_core true
                              circulation_area_m2_total 8.1972
                              gross_footprint_area_m2 136.8679 != conditioned_floor_area_m2 128.6707
```

Across Bologna, **1,257 of 1,257 `buildings.csv` rows carry `circulation_pct` 0.0** while **173
layout JSONs carve a core**. Lyon: 768 of 768 CSV rows at 0.0 against 31 cored JSONs. London is the
one district whose CSV is not uniformly zero — **3 rows carry `circulation_pct > 0`**.

Per-file cross-tab, top-level `scheme` × `has_unconditioned_core`:

```
Lyon      null 192 F | 1x1 72 F | 2x1 23 T | 3x2 6 T | 2x2 2 T | 2x2 1 F | 4x2 1 F
Bologna   null 979 F | 2x1 146 T | 1x1 47 F | i_shape_linear_gallery 11 T
          narrow_plate_corridor_free 10 T | l_shape_decomposition 5 F | 2x2 4 T | 3x2 2 T
```

⚪ **Not a clean pre/post split.** Every cored file is multi-cell and no `1x1` is cored, but **seven
multi-cell plates are already core-free** (Bologna's five `l_shape_decomposition`, Lyon's `4x2` and
one `2x2`) — consistent with 2026-09-01 catching the cutter mid-migration rather than wholly before
it.

🔴 **This is a stale export, not a live engine defect,** and the letter says so.
`european_nocore.py` is not accused of drawing cores.

## 4. What this changes for `C2` and for Step 11

* **`N_u` must not be read from today's `layouts/`.** Under `C2` §3.1, `N_u := k × storeys` with
  `k = max(1, round(dwellings_total / storeys))`, and `D-EU-80` requires every square metre to
  belong to exactly one flat (coverage 0.999–1.001). A payload with `circulation_area_m2_total > 0`
  fails that premise by construction. Reading `k` from it would seed `C2` with core-era arithmetic.
* **A Bologna shakedown is the only admissible one today** and is still blocked on the regenerated
  payload, not on the fold rule.
* **Freeze condition 1 is now MET** (engine carry-in landed). **Condition 2 is NOT** — `D-EU-84` is
  open: `MAX_FLAT_ASPECT` uncalibrated, no rung of 2.5/3.0/3.5/4.0 reached `FAIL 0`, set to the
  strictest rung 2.5, **81 of 550 plates ship as an honest residual `FAIL` across 57 unique
  buildings**, and `EU-21` acceptance criterion 3 is **not met**
  (`STATE_european_locations_v5.md` §7 item 1). Conditions 3, 4 and 5 are the owner's.
* ⚪ **Correction to an earlier statement in this session's own reply:** EnergyPlus **has** run and
  `D-EU-55` is satisfied by the ceiling82 campaign's own submission; `EU-19` is complete and the
  merged viewers carry per-building EUI. Pooled district EUI on record: Lyon **69.595307** over
  505 of 509, London **120.064327** over 706 of 706, Madrid **80.694006** over 1,166 of 1,175
  (2026-09-07 T07 restatements), Bologna **54.935569** and **stale**, still the ceiling82 number
  pending its delta harvest. 🔴 **None of these is quoted as a 4J result** — they are the OpenUBEM
  side's numbers, `C2` has no cell, and Lyon's in particular can never enter a 4J denominator.

## 5. `FINDING 258` reaches Step 11 directly

The OpenUBEM side carries open, unscheduled: plates that report `PASS ALL 7 CHECKS` yet divide into
a few tiny strip dwellings alongside one oversized dwelling absorbing the rest, because the
seven-check set does not penalise inter-dwelling area imbalance on the same plate. The owner's
ruling is per-affected-building repair, never a full-batch re-cut.

🔴 **Step 11 aggregates per dwelling.** An imbalanced division changes what a dwelling *is* in the
denominator, so 4J needs to know whether the repair lands before or after the payload 4J consumes.
This is a question to them, not a defect 4J may fix.

## 6. Filed

Letter sent the same day:
`messages_OpenUBEM/2026-09-08_4J_to_OpenUBEM_layout_payload_and_two_questions.md`, delivered into
their inbox at `OpenUBEM/docs/docs_ACTIVE/europeanLocations/messages_GSSCanada/` (same filename).

---

## 7. 🔴 CORRECTION, same day — §2 (a) was WRONG. Appended, nothing above rewritten.

The OpenUBEM side replied within the hour and corrected one measurement in §2 and in the letter.
**They are right and it was re-measured here before accepting it.**

🔴 **The defect was in the counting method, not in their data.** §2's layout-file column was produced
with `ls <dir> | wc -l`, which counts **directory entries**. Madrid's and London's `layouts/` are
**nested** (`relation/` and `way/` subdirectories); Lyon's and Bologna's are flat. So Madrid's "2"
and London's "1" were the two and one **subdirectory names**, not files.

Re-measured with `find <dir> -name '*.json' | wc -l`:

```
district                  declared ruled   layout JSONs (recursive)   cored (recursive)
eu_ES-MAD-BERRUGUETE               1,038                       961                 74
eu_GB-LDN-STDUNSTANS                 692                        82                  8
eu_IT-BOL-GALVANI2                   552                     1,204                173
eu_FR-LYO-HAUTCOEURPENTES            459                       297                 31
```

**What changes:**

* 🔴 **§2 (a) is withdrawn.** Madrid is **nearly complete** (961 of 1,038), not empty. **London is
  the only genuinely depleted district** — 82 files against 692 declared ruled.
* 🔴 **The cored total is 286, not 204.** Madrid contributes **74** and London **8**, both reported
  as 0 in §2 and in the letter because the recursive tree was never walked. §3's Bologna (173) and
  Lyon (31) figures were flat directories and are **unaffected**.
* ⚪ **§3's staleness finding is unaffected and they confirm it** — *"engine correct, payload older
  than the engine"*. The 2026-09-01 dates, the `27746` contradiction and the cross-tab all stand.
* ⚪ **§4's refusal to read `k`/`N_u` from this payload is unaffected**, and is now over-determined.

### 7.1 🔴 Their root cause is deeper than staleness, and it was verified here independently

They report that `generate_eu_3d_viewers.py` copies `layouts/` **verbatim** from
`openubem/outputs/eu_evidence/EU-17/<district>/layouts`, and that the EU-17 manifests are **partial
rebuild scopes**. Checked directly against that tree, not taken on trust:

```
EU-17/ES-MAD-BERRUGUETE      961      outputs_3D  961
EU-17/FR-LYO-HAUTCOEURPENTES 297      outputs_3D  297
EU-17/GB-LDN-STDUNSTANS       82      outputs_3D   82
EU-17/IT-BOL-GALVANI2      1,204      outputs_3D 1,204
```

**One for one, all four.** 🔴 **The shipped payload's population is the EU-17 rebuild scope, not the
published district.** That also explains §2 (c) in both directions: Lyon ships fewer files than its
declared `ruled` count, and Bologna ships **more** (1,204 against 552 declared) — a rebuild scope has
no reason to agree with either. The `sources.json` `layout_counts` block describes the **district**;
the `layouts/` folder beside it describes the **rebuild scope**. They are two different populations
under one folder.

### 7.2 Re-emission in flight on their side — do not consume the current payload

Geometry only, through the live no-core cutter
(`scripts/emit_eu11_layout_sidecars.py`, `EUROPEAN_LAYOUT_REGIME = "nocore"` →
`european_nocore.cut_storey_nocore`), from the **published** populations:

```
ES  EU-11/ES-MAD-BERRUGUETE_merged_2026-09-07   1,175 rows
GB  EU-11/GB-LDN-STDUNSTANS_merged_2026-09-07     706 rows
IT  EU-11/IT-BOL-GALVANI2_final_2026-09-07      1,211 rows
```

⚪ No re-cut of anything 4J holds, no EnergyPlus, no cluster job; manifests staged as copies so no
published manifest is rewritten. Lyon excluded, per 4J's own de-prioritisation. They will send
emitted / installed / cores / circulation counts per district on landing.

🔴 **When it lands, verify before consuming**: `circulation_area_m2_total == 0` on **every** file,
recursively (`find`, never `ls`), and the JSON count against the published row count above — not
against `sources.json`.

## 8. Their answers to the two questions

🔴 **Q1 — `FINDING 258` lands AFTER the regeneration.** It is open and explicitly unscheduled, and
the owner's ruling confines any fix to affected buildings only, never a full-batch re-cut or
re-simulation. **So the payload 4J is about to consume is pre-repair.** Any later repair touches a
named handful of buildings, and they will send the building list before it ships. **4J therefore
carries this as a declared limitation in the population declaration `G11.16` requires**, and does
not treat a later repair as a population change.

🟢 **Q2 — `D-EU-84` is CLOSED as an accepted named residual, ruled today as `D-EU-110`**
(`STATE_european_locations_v5.md` §4). **Freeze against this wording, verbatim:**

> `D-EU-84` is closed, not open work. The ladder it demanded was run over all 550 plates and no rung
> reached FAIL 0 after two genuine repair rounds; that outcome is the answer and is accepted as such.
> `MAX_FLAT_ASPECT` stays at the strictest rung, 2.5, and may not be moved to make any downstream
> consumer's condition pass. The residual is named and carried: 81 of 550 plates ship an honest FAIL
> on the aspect check across 57 unique buildings — thick-band courtyard rings and dense n=12
> multi-wing plates whose wings do not separate under `lobes_of`. `EU-21` acceptance criterion 3 is
> satisfied by this ruling as a declared residual; criterion 2 (FAIL 0 on 550 plates) remains not met.

⚪ They confirm they did **not** move `MAX_FLAT_ASPECT` and will not. `D-EU-87` confirmed
implemented — `C10` rebuilt as a created-pinch test after `FINDING 241`, fleet created-pinch
1358.78 → 134.63 m² (−90 %).

🔴 **`EU-21` criterion 2 remains NOT met and that travels with the ruling.** Quoting `D-EU-110` as
"closed" without the criterion-2 clause overstates it.

## 9. 🔴 Freeze conditions restated — 1 and 2 are now MET

```
1  engine carry-in                            MET  (bit-parity 2,529/2,529)
2  D-EU-84 and D-EU-87 ruled and closed       MET  (D-EU-110 today; D-EU-87 implemented)
3  owner pins ENGINE_DIGEST_PIN               owner's
4  owner gives the D-EU-55 sentence for OUR run   owner's
5  owner freezes this prereg + md5 sidecar    owner's
```

🔴 **Only the author's own three actions and the payload delivery now stand between `C2` and a
Bologna shakedown.** `ENGINE_DIGEST_PIN` is still never moved to make a run pass, a first district is
still not a campaign, and the prereg is still frozen **before** the first district runs.

⚪ **Bologna's pooled EUI is stale (ceiling82, pending its delta harvest) and is not to be carried
even as context** — their words, and it joins the never-quote list with the other three.

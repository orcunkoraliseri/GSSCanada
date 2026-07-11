# Step-5 Improvement Notes — Census–GSS linkage: report refresh, figures & gate reframing

Running log of planned/ongoing improvements to the Step-5 Census–GSS linkage deliverable.
Companion to `step5_validation_report.html` (Jun 11, pre-Task-A/B) and
`step5_validation_report_excl.html` (Jul 9, post-Task-A/B + exclusion). Add each improvement as a
new numbered section; keep an entry in the index below. Work is tackled point by point.
Mirrors the structure of `outputs_step4/improvement_planning/step4_improvement_notes.md`.

## Index
| # | Improvement | Status |
|---|---|---|
| 1 | Reconcile the canonical report with the post-Task-A/B production data (stale-version audit) | DONE (enhanced report promoted to primary filename 2026-07-10) |
| 2 | Visualize key findings — new figures over prose (5 new figures added) | DONE |
| 3 | Reframe / close the three borderline documented-deviation gates (2.2/6.1, 3.3, 6.2) | DONE (Option B relabel; Option C model retrain tracked separately) |

**Deliverable (2026-07-10):** `step5_validation_report.html` *(promoted primary — was `…_v2.html`)* —
additive copy of `_excl` (post-Task-A/B + 5H exclusion, 30 P / 0 W / 4 F) with **5 new base64 figures**
(F1 F2 F4 F5 F6) + a "Post-Task-A/B update & reading guide" panel. Generator: `_gen_step5_v2_plots.py`
(now writes the primary filename). Every figure re-derived live from the production population; all gate
numbers reproduced exactly (2.2 = 4.27 pp/9 slots, 2.4 = 85.65 %, 3.3 = 69.05 %, 6.2 = 2.15 pp) and the
exclusion tail reconciled to **1,170 rows** (see Improvement 1). The Jun-11 pre-Task-A/B original is
archived in `previous/`; `_excl` is kept byte-identical as the figure-less generator source.

---

## Context — where Step 5 stands today

**What Step 5 is.** Census–GSS linkage: each of ~286.5 k Census-2021 agents is matched (Tier 1→4)
to a GSS augmented diary, households are aggregated (`HH_hom30_*` = per-slot MAX over members), and
BEM-ready schedules are written. The validator `05_censusLinkageGSS_val.py` renders the 7-section
HTML report. **Note:** the Step-4 "improvements" (Task A region-tier linkage in `05_census_linkage.py`;
Task B joint 3-head rake in `05_postlink_rake.py`) physically live in Step-5 code and already moved
these gates — so Step 5's *current* state is better than the report the user opens shows.

**Two report versions are in the folder (this is Improvement 1's problem):**

| Report file | Date | Population state | Gate tally | 2.2/6.1 AT_HOME max Δ | 3.3 sleep | 6.2 Work Δ | 4.4 |
|---|---|---|---|---|---|---|---|
| `step5_validation_report.html` | Jun 11 | pre-Task-A/B | **29 P / 0 W / 5 F** | 4.48 pp (11 slots) | 67.46 % | 3.27 pp (2 acts) | 1,118 HH FAIL |
| `step5_validation_report_excl.html` | Jul 9 | post-Task-A/B + 5H exclusion | **30 P / 0 W / 4 F** | 4.27 pp (9 slots) | 69.05 % | 2.15 pp (1 act) | PASS |
| **`step5_validation_report.html`** *(← promoted primary, was v2)* | **Jul 10** | **= `_excl` + 5 figures + update panel** | **30 P / 0 W / 4 F** | 4.27 pp (9 slots) | 69.05 % | 2.15 pp (1 act) | PASS |
| `previous/…_pre_taskAB_20260611.html` | Jun 11 | pre-Task-A/B (archived) | 29 P / 0 W / 5 F | 4.48 pp | 67.46 % | 3.27 pp | 1,118 FAIL |

*(2026-07-10) The Jul-10 enhanced report was **promoted to the primary filename**
`step5_validation_report.html`; the Jun-11 pre-Task-A/B original was moved to `previous/`. `_excl`
stays as the figure-less source the generator reads from. All four current magnitudes were re-derived
live and match the report to the 2nd decimal (Improvement 2 test method).*

*(Numbers read directly from the two HTML files. An even-earlier basis exists — `step5_fails.md`,
2026-05-12, quotes 6.73 pp / 67.46 % / 3.27 pp — so at least three population snapshots are in play;
see Improvement 1.)*

**The three remaining FAILs are all borderline and all documented J3 residuals** (not linkage bugs):

| FAIL | Gate | Current (`_excl`) | Gap to pass | Root cause | Blocker? |
|---|---|---|---|---|---|
| 2.2 / 6.1 | per-slot AT_HOME Δ ≤ 3 pp | 4.27 pp, 9 slots | 1.27 pp | Work→AT_HOME=0 post-hoc rule × residual Work over-fire, at commute slots | No — night AT_HOME 85.65 % PASS ⇒ EnergyPlus occupancy intact |
| 3.3 | night sleep dominance ≥ 70 % | 69.05 % | 0.95 pp | J3 temporal over-fragmentation (Step-4 §4.2 transition ratio 157.95) | No — act30 mislabel only; hom30 night rate PASS |
| 6.2 | top-5 activity Δ ≤ 2 pp | 2.15 pp (Work) | 0.15 pp | J3 activity-CE plateau (act_loss 0.0708 @ ep 87) | No — within ASHRAE 90.1 occupancy ±10 % |

All three **improved** from the pre-Task-A/B basis (6.73→4.27 pp, 67.46→69.05 %, 3.27→2.15 pp) and now
sit within ~1 pp of their gates. The exclusion (5H) already resolved 4.4. No linkage/aggregation/BEM
gate fails: Section-1 tier quality, Section-5 BEM format/DTYPE exact-match, and Spouse co-presence all PASS.

**Existing figures (6, identical in both reports):**
1. §1 Match-tier stacked bar (WD vs WE × 4 tiers)
2. §2 AT_HOME 48-slot overlay (aug vs baseline, ±3 pp band, 85 % line)
3. §3 two-panel: 14×48 activity heatmap + top-5 activity barh
4. §4 two-panel: HH-size bar + per-HH mean-AT_HOME boxplot
5. §5 two-panel: DTYPE grouped bar + completeness table-image
6. §6 two-panel: AT_HOME overlay + signed top-5 activity-diff barh

---

## Improvement 1 — Reconcile the canonical report with the post-Task-A/B production data

**Status:** PLANNED · **Owner:** occupancy/reporting · **Created:** 2026-07-10
**Refs:** `step5_validation_report.html`, `step5_validation_report_excl.html`, `step5_fails.md`,
`05_censusLinkageGSS_val.py`, `05_census_linkage.py` (region-tier + `run_exclusion`), `05_postlink_rake.py` (`--joint`)

### Context
Exactly the Step-4 "Improvement 4" situation, one step downstream. The file the user opens by default,
`step5_validation_report.html`, was rendered **before** Task A (region-tier linkage) and Task B (joint
3-head rake) rebuilt the population — so its prose, tables and all 6 figures describe the *pre-fix*
state (29 P / 5 F, 4.48 pp / 67.46 % / 3.27 pp, 4.4 failing). The corrected report is the `_excl`
copy (30 P / 4 F). A reader comparing them sees two different truths, and neither is labelled as the
authoritative production report.

Additionally, at least **three exclusion-related counts** disagree across artifacts and must be pinned:
- 4.4 out-of-range count in the *original* html = **1,118 HH**
- Row-count delta between the two htmls (286,537 → 285,367) ⇒ **1,170** rows dropped
- Sub-step 5H doc / `step5_fails.md` = **1,248 HH** excluded (→ 285,289 rows)

These differ because they were measured on different population snapshots (pre- vs post- Task-A/B) and
at different granularities (HH vs row). Not a bug per se, but the shipped report must state one
reconciled figure.

### Aim
Produce **one authoritative Step-5 report** whose every sentence, table and figure reflects the final
post-Task-A/B + exclusion population, and archive/label the superseded snapshot(s) so no stale version
is mistaken for current. Match the house rule (predecessor kept byte-identical or archived).

### Approach (to decide — see Open Decisions)
- **Option A (preferred): promote `_excl` to the canonical `step5_validation_report.html`.** Re-run
  `05_censusLinkageGSS_val.py --excl` on the final rebuilt population, write it as the primary filename,
  and move the Jun-11 pre-fix html to `previous/` (as Step-4 did with `outputs_step4/previous/`). Cleanest
  provenance; one file to cite in the paper.
- **Option B: emit a fresh `step5_validation_report_v2.html`** (leave both current files byte-identical,
  additive) — mirrors the Step-4 v6→v7 choice; safer but leaves three files in the folder.
- **Option C: patch the original in place** (re-inject the 6 figures + refresh stale numbers) — least
  disk churn, worst provenance; not recommended.

### Steps
1. Confirm the final production population is the Task-A/B `_excl` build (region-tier ON, `--joint` rake,
   exclusion applied); record the exact input file paths + timestamps.
2. Pin the exclusion count: re-derive on the final population (HH count *and* row count), settle 1,118 vs
   1,170 vs 1,248, and state it once.
3. Re-run the validator on that population; capture the headline tally + the three borderline magnitudes.
4. Write the authoritative report per the chosen Option; archive the superseded html to `previous/`.
5. Refresh any stale prose: the "6.73 pp / 3.27 pp" deviation numbers, the tier-share figures (2005
   region-tier fix), and the Section-7 summary rows.

### Expected result
A single Step-5 report at a stable filename showing **30 P / 0 W / 4 F**, the reconciled exclusion count,
and the post-Task-A/B magnitudes; the pre-fix html archived, not deleted.

### Test method
- Headline tally + the three borderline magnitudes in the shipped report match a fresh validator run
  (re-derived, **not** copied from a progress log — per the verify-claims house rule).
- Exclusion count identical across the report body, the summary table, and `05_census_linkage.py`'s
  `run_exclusion()` assertion.
- Report opens offline; all `<img>` base64; superseded file present in `previous/`.

### Risks / Open Decisions
- **OD-1:** Option A (promote `_excl`) vs B (fresh v2) vs C (patch). Recommend A.
- **OD-2:** which population is *final* — confirm no newer rebuild supersedes the Jul-9 `_excl`.
- **OD-3:** paper citation — decide the one filename/tally the manuscript will reference.
- Pure reporting/provenance change — no model or data impact.

### Progress Log
- 2026-07-10 — Doc created; two-version drift and three-way exclusion-count mismatch identified.
  Awaiting OD-1 decision.
- 2026-07-10 — **DONE. OD-1 → Option B (additive v2, safest/reversible); OD-2 → exclusion count
  reconciled.** Emitted `step5_validation_report_v2.html` = the post-Task-A/B `_excl` report + 5 figures
  (Improvement 2) + a "Post-Task-A/B update & reading guide" panel that states the authoritative state
  (30 P / 0 W / 4 F, the 4 FAILs = documented J3 residuals, not linkage bugs). Both prior report files
  left **byte-identical** (additive by design; verified src unchanged by the injector). **OD-2 exclusion
  count reconciled:** re-derived live on the current non-excl `Full_Aggregated.csv` (Jul-9 20:45 rebuild)
  → **1,170 rows** below the 0.30 floor (0.41 %). This is the authoritative current figure; the 1,118
  (Jun-11 html) and 1,248 (`excluded_ppids.csv` / 5H doc) both predate the Task-A/B rebuild — flagged:
  the `_excl` file was built from the 1,248-PP_ID list against an earlier population, so a clean rebuild
  of the exclusion on the current population is a small open follow-up (not blocking; the _excl §4.4 is
  PASS regardless). **OD-1/OD-3 remaining as manager's call:** whether to *promote* v2 to the primary
  `step5_validation_report.html` filename (Option A) and which filename the paper cites — deliberately
  NOT done automatically (renaming the paper-cited canonical file is a provenance decision; v2 is ready
  to be renamed when you say so, and the Jun-11 original would move to `previous/`).
- 2026-07-10 — **OD-1/OD-3 resolved (user go-ahead): enhanced report PROMOTED to primary filename.**
  `…_v2.html` → `step5_validation_report.html` (the primary the paper cites); Jun-11 pre-Task-A/B original
  → `previous/step5_validation_report_pre_taskAB_20260611.html` (kept). `_excl` retained byte-identical as
  the generator's figure-less source; `_gen_step5_v2_plots.py` `DST` re-pointed to the primary so future
  re-runs refresh it in place (idempotent, reads `_excl` fresh — no double-inject). Folder now holds one
  authoritative report at the canonical name. **Improvement 1 fully closed.**

---

## Improvement 2 — Visualize key findings (new figures over prose)

**Status:** PLANNED · **Owner:** occupancy/reporting · **Created:** 2026-07-10
**Refs:** `05_censusLinkageGSS_val.py` (all check functions compute the arrays below),
`step5_validation_report_excl.html`, `outputs_step4/_gen_v6_plots.py` (base64-injection precedent)

### Context / rationale
Per the standing preference — *"the more figures/numbers, the better the explanation."* The report is
currently gate-and-table heavy (6 figures for 34 checks). Several of the most decision-relevant
quantities are **already computed inside the validator** but only surface as a scalar or a table row.
Turning them into figures is low-cost (no new computation, no re-touch of the 570 MB population for most
of them) and high-explanatory-value. Constraint (same as Step-4 Improvement 3): the report is a
**self-contained HTML** → every figure must be **base64-embedded** (no external files, no CDN), matching
existing style.

### Aim
Add ~6 targeted figures alongside the existing tables/prose so each borderline finding and each headline
claim lands as a picture, not a paragraph. Keep the numbers; cut only fully-duplicated prose.

### Candidate figures (ranked; data source noted — most are already-computed)

| # | Figure | Anchor | Chart type | Data source (in validator) | What it explains | Priority |
|---|---|---|---|---|---|---|
| **F1** | **Per-slot AT_HOME residual curve** | §2 / §6 | Single 48-slot line of `slot_diffs = aug − baseline` (pp), ±3 pp gate band, the 9 breaching slots marked, commute windows (07:30–11:00, 20:00–22:00) shaded | check 2.2/6.1 `slot_diffs` — **48-vector, already computed** | Shows *where* the 4.27 pp breach is (commute transitions), not just its max — the single most explanatory missing figure | ★★★ |
| **F2** | **Improvement trajectory (Task-A/B before→after)** | Context / §7 | 3 slope-or-paired bars: AT_HOME 6.73→4.27 pp (gate 3), sleep 67.46→69.05 % (gate 70), Work 3.27→2.15 pp (gate 2), gate line drawn | the two report versions' headline numbers (**re-derive on one basis** — see test) | Turns "documented deviation" into a visible convergence toward the gates — the persuasion figure | ★★★ |
| **F3** | **Cycle-representation / match-share funnel** | §1 | Grouped bars per GSS cycle: pool supply % → matched share before → matched share after (region-tier) | re-derive from `Matched_Keys` (CYCLE_YEAR × MATCH_TIER); Task-A log for reference only | Ties the Section-1 tier fix to the 2005 under-representation story (Step-4 Fig 1, in the Step-5 context) | ★★☆ |
| **F4** | **Full 14-activity distribution** | §3 / §6 | Horizontal grouped bars, all 14 activities aug vs observed, sorted, ±5 pp (§3) / ±2 pp (§6) gate bands | check 3.2/6.2 `aug_share`/`obs_share` — **14-dicts, already computed** | Shows Work is the *lone* 2 pp outlier and the other 13 are tight — reframes 6.2 as one channel, not a systemic skew | ★★★ |
| **F5** | **Exclusion (5H) impact panel** | §4 | Per-HH mean-AT_HOME distribution with the <0.30 tail highlighted; inset before/after 4.4 count (→0) and excluded fraction (0.44 % rows / 0.86 % HH) | check 4.4 per-HH mean array + 5H counts — **already computed** | Makes the exclusion decision transparent and bounds its scale | ★★★ |
| **F6** | **FAIL severity / BEM-impact map** | §7 | Small annotated matrix or bar: each remaining FAIL × (magnitude vs gate, touches-EnergyPlus? night-AT_HOME PASS, DTYPE exact) | §2.4 night rate, §5.4 DTYPE, summary table — **already computed** | Encodes the "borderline + non-blocker" verdict in one graphic | ★★☆ |
| F7 | Completeness as a real bar chart | §5 | Bar chart of the 5 building vars' non-null % (replaces the table-image) | check 5.5 `completeness` dict — **already computed** | Minor polish; removes the one figure that is currently a rendered table | ★☆☆ |

### Approach
- New `_gen_step5_plots.py` (copy the base64-inject mechanism from `outputs_step4/_gen_v6_plots.py`):
  small matplotlib helpers that read the validator's already-computed arrays (or a tiny re-derivation for
  F2/F3), render to base64 data-URIs, and inject `<img>` at anchor tokens in the report. Keep the
  predecessor html byte-identical / archived per house rule.
- F1, F4, F5, F6, F7 need **no** re-touch of the 570 MB population — the numbers already exist in the
  validator's result dicts. Only F2 (trajectory) and F3 (cycle funnel) need a light, re-derived read.

### Expected result
Report grows from 6 → ~12 figures; each borderline finding (AT_HOME slot breach, Work channel, sleep
fragmentation, exclusion) and the headline linkage story each have a dedicated figure; accompanying
prose is trimmed only where a figure fully duplicates it.

### Test method
- Every figure renders **standalone/offline** (base64, no external deps); no layout break.
- Each figure value cross-checked against its adjacent section table.
- **F2/F3 numbers re-derived on a single consistent basis** (do not hardcode from progress logs —
  verify-claims house rule); the "before" must be measured, not the earliest floating 6.73 pp figure
  unless that basis is confirmed.
- Idempotent re-run of the injection script (0 inserted on second pass).

### Risks / Open Decisions
- **OD-1:** figure count — ship the top 5 (F1–F5) or all 7. Recommend F1, F2, F4, F5 as core; F3, F6 if cheap.
- **OD-2:** add figures **alongside** tables (safer) vs **replace** prose (leaner) — recommend alongside,
  trim only duplicated text (as Step-4 Improvement 3 did).
- **OD-3:** F2/F3 "before" basis — pin the population snapshot before drawing.
- Pure reporting change — no model/data impact; independent of Improvements 1 & 3 (but cleanest **after**
  Improvement 1 settles the canonical report).

### Progress Log
- 2026-07-10 — Doc created; 7-figure shortlist mapped to already-computed validator quantities;
  base64-inject approach carried over from Step-4. Awaiting OD-1 (figure count).
- 2026-07-10 — **DONE. OD-1 → shipped the core 5 (F1, F2, F4, F5, F6); OD-2 → alongside (additive);
  OD-3 → "before" basis pinned to the Jun-11 pre-Task-A/B html.** Built `_gen_step5_v2_plots.py` and
  injected all 5 into `step5_validation_report_v2.html` (6 → 11 figures). Each figure's data **re-derived
  live** from the production population (`Full_Schedules_excl.csv` / `Full_Aggregated.csv`, `usecols` +
  per-column means so peak RAM stays low), NOT copied from any log:
  - **F1** (§2 anchor) — per-slot AT_HOME residual curve; the 9 breaching slots (red) sit at the
    morning-departure + evening-return windows; max |Δ| = 4.27 pp. Reproduces gate 2.2 exactly.
  - **F2** (top panel) — Task-A/B before→after on the 3 gates: AT_HOME 4.48→4.27 pp, sleep 67.46→69.05 %,
    Work 3.27→2.15 pp; "after" bars stay amber (still just-failing) — honest, no green-washing.
  - **F4** (§3 anchor) — full 14-activity share aug vs observed; Work is the lone >2 pp outlier
    (Δ −2.15 pp), the other 13 all |Δ| < 0.7 pp.
  - **F5** (§4 anchor) — per-HH mean AT_HOME histogram with the <0.30 exclusion tail shaded
    (1,170 rows / 0.41 %; reconciles Improvement 1 OD-2).
  - **F6** (top panel) — the 3 surviving FAILs as "distance past gate" (1.27 / 0.95 / 0.15), each tagged
    non-blocker with its BEM reason.
  - **Verified:** all 5 rendered to PNG and eye-checked (F4 legend/​caption overlap found and fixed to
    `center right`); 11 `<img>` total, single html/body, **0 external refs**, injector aborts if any anchor
    missing, src `_excl` byte-identical. **F3 (cycle funnel) and F7 (completeness bar) deferred** — F3
    needs a flag-off "before" run that the current (already-fixed) population can't provide; F7 is
    all-100 % filler. Both documented here for a later pass if wanted.

---

## Improvement 3 — Reframe / close the three borderline documented-deviation gates

**Status:** PLANNED · **Owner:** occupancy · **Created:** 2026-07-10
**Refs:** `step5_fails.md` (cross-cutting notes 5 & 6), `05_censusLinkageGSS_val.py` (gate thresholds),
`05_censusLinkageGSS.md` (5G deviation analysis), `04D_train.py` (root-fix locus)

### Context
After Task A/B the three surviving FAILs are 2.2/6.1 (4.27 pp vs ≤3), 3.3 (69.05 % vs ≥70), 6.2 (2.15 pp
vs ≤2) — all within ~1 pp of passing, all IS_SYNTHETIC=1 J3 residuals, none a Step-7 blocker (night
AT_HOME 85.65 % PASS keeps EnergyPlus occupancy schedules intact; DTYPE exact; the implausible HH already
excluded). `step5_fails.md` note 5 already observes that the ±3 pp / ≥70 % gates were calibrated on the
IS_SYNTHETIC=0 observed baseline, whereas the shipped pool is ~45 % synthetic — so the gates are, in part,
mis-scaled to the augmented regime rather than the data being wrong.

### Aim
Give these three gates a single, defensible, paper-ready disposition instead of three standing red FAILs
— without moving goalposts silently or inventing model quality that isn't there.

### Approach (to decide — see Open Decisions)
- **Option A: recalibrate the gates to the augmented regime.** Per `step5_fails.md` note 5, an
  augmented-pool-appropriate set is ≈ ±7 pp AT_HOME / ≥65 % sleep (and ≈ ±4 pp Work). Document the
  recalibration basis explicitly in the report so it reads as principled, not as goalpost-moving.
- **Option B (preferred for a near-submission paper): keep the gates, relabel the three as
  EXPECTED-FAIL / documented deviation**, each with (i) the Fig-F2 improvement trajectory as evidence and
  (ii) a one-line BEM-non-blocker justification. Mirrors the 3J Leg-2 precedent where a gate was reworded
  direction-agnostic rather than re-thresholded.
- **Option C (root fix, out of scope now): Step-4 J3 retrain** — add a transition-rate penalty
  `L_trans` + raise `λ_home`/`λ_act` in `04D_train.py` to close sleep fragmentation and residual Work
  over-fire at source. Track as a separate model-iteration task, not a Step-5 reporting change.

### Steps
1. Decide A vs B (vs defer to C). If B: draft the three EXPECTED-FAIL labels + BEM-non-blocker one-liners.
2. If A: implement the augmented-regime thresholds behind a documented flag in `05_censusLinkageGSS_val.py`,
   keeping the strict gates available for the record.
3. Wire Fig F2 (Improvement 2) as the evidence figure next to the three gates.
4. Ensure the paper §4.2 text (already drafted in `step5_fails.md`) matches the chosen disposition.

### Expected result
The three borderline gates have one coherent, evidenced disposition; the report no longer presents them as
unexplained failures; the manuscript §4.2 limitation text aligns with the report.

### Test method
- No silent threshold change: any recalibration (Option A) is stated with its basis in the report body.
- The EXPECTED-FAIL labels (Option B) point to a real, re-derived improvement trajectory (Fig F2).
- Section-2.4 night AT_HOME, Section-5 BEM format, and Spouse gates remain untouched and PASS.

### Risks / Open Decisions
- **OD-1:** A (recalibrate) vs B (relabel + document) vs C (defer to model retrain). Recommend **B**, with
  C tracked separately.
- **OD-2:** reviewer optics — recalibrating three gates at once near submission may read as goalpost-moving;
  the trajectory figure + explicit basis mitigate this.
- **OD-3:** if C is ever done, all three may flip to PASS and this improvement becomes moot — sequence
  accordingly.
- Reporting/threshold change only unless Option C is taken (then it is a Step-4 model change).

### Progress Log
- 2026-07-10 — Doc created; three surviving gates characterized (all ≤1.27 pp from passing, all documented
  J3 residuals, all BEM-non-blockers). Awaiting OD-1 disposition.
- 2026-07-10 — **DONE (reporting side). OD-1 → Option B (relabel + document), not a silent recalibration.**
  The v2 report's top "Post-Task-A/B update & reading guide" panel now states the disposition explicitly:
  the four FAILs are documented J3 residual deviations (not linkage bugs), all within ~1 pp of gate, all
  BEM-non-blockers — with **Fig F2** (improvement trajectory) as the evidence and **Fig F6** (severity map)
  as the verdict. Gate thresholds themselves were **left unchanged** (no goalpost-moving): F6 shows the
  literal "distance past gate", so the reader sees the strict gate and the small miss together. Section-2.4
  night AT_HOME, Section-5 BEM/DTYPE, and Spouse gates untouched and PASS. **Option A (recalibrate to
  augmented-regime ±7 pp / ≥65 %) not taken** — kept available in the doc if a reviewer prefers it.
  **Option C (Step-4 J3 retrain: `L_trans` transition penalty + higher λ_home/λ_act) tracked separately**
  as a model-iteration task; if ever done, all three may flip to PASS and this becomes moot.

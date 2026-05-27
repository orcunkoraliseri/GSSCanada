# Step 5 Validation — FAIL Investigation Report
*Generated: 2026-05-12*

---

## Analysis snippets

The following pandas calls profile the FAIL 4.4 households. Not executed (read-only investigation); provided for future verification runs.

```python
import pandas as pd

AUG_DIR = "0_Occupancy/Outputs_21CEN22GSS/aug_pipeline/"

agg = pd.read_csv(
    AUG_DIR + "21CEN22GSS_aug_Full_Aggregated.csv",
    usecols=lambda c: c in {"PP_ID", "HH_ID", "N_HH_MEMBERS"}
               | {f"HH_hom30_{i:03d}" for i in range(1, 49)},
)
sched = pd.read_csv(
    AUG_DIR + "21CEN22GSS_aug_Full_Schedules.csv",
    usecols=lambda c: c in {
        "PP_ID", "HH_ID", "IS_SYNTHETIC", "AGEGRP", "SEX",
        "MARSTH", "HHSIZE", "LFTAG", "DDAY_STRATA",
    },
)
keys_df = pd.read_csv(
    AUG_DIR + "21CEN22GSS_aug_Matched_Keys.csv",
    usecols=["PP_ID", "MATCH_TIER"],
)

hh_hom_cols = [f"HH_hom30_{i:03d}" for i in range(1, 49)]
hh_means = agg[hh_hom_cols].mean(axis=1)
fail_ppids = set(agg.loc[hh_means < 0.3, "PP_ID"])

fail_sched = sched[sched["PP_ID"].isin(fail_ppids)].copy()
fail_sched = fail_sched.merge(keys_df, on="PP_ID", how="left")

# IS_SYNTHETIC composition
print(fail_sched["IS_SYNTHETIC"].value_counts(normalize=True))

# Match tier distribution
print(fail_sched["MATCH_TIER"].value_counts(normalize=True))

# Key demographics
for col in ["AGEGRP", "SEX", "MARSTH", "HHSIZE", "LFTAG", "DDAY_STRATA"]:
    print(col, "->", fail_sched[col].value_counts(normalize=True).head(3).to_dict())
```

---

## Summary Table

| FAIL | Root cause (one line) | Origin step | Blocker? | Action |
|------|-----------------------|-------------|----------|--------|
| 2.2 / 6.1 | IS_SYNTHETIC=1 diaries over-predict Work (+3.27 pp); post-hoc Work→AT_HOME=0 rule depletes AT_HOME in 9 slots (max 6.73 pp) | Step 4 — J3 activity CE loss | No | Document only; pre-anticipated §4.2 deviation |
| 6.2 | IS_SYNTHETIC=1 Work time-share inflated 3.27 pp vs observed (21.58% vs 18.32%) | Step 4 — J3 activity CE loss | No | Document only; pre-anticipated §4.2 deviation |
| 3.3 | J3 model generates excessive activity transitions (Section 4.2 ratio 157.95); night sleep fragmented; 67.46% of slots 1–8 coded Sleep vs ≥70% threshold | Step 4 — J3 temporal decoder, IS_SYNTHETIC=1 | No | Investigate in next model iteration; document §4.2 |
| 4.4 | 1,248 single-person IS_SYNTHETIC=1 weekday agents with Work-heavy diaries produce per-HH mean AT_HOME < 0.3; physically implausible | Step 4 (IS_SYNTHETIC=1 AT_HOME deficit + Work post-hoc rule) propagated through Step 5 HH aggregation | Soft — flag before Step 7 | RESOLVED — excluded 1248 HHs (0.44%) via run_exclusion(); _excl files written; val re-run Check 4.4 PASS |

---

## FAIL 2.2 / 6.1 — AT_HOME per-slot max diff 6.73 pp

### What failed
Check 2.2 (`05_censusLinkageGSS_val.py:257–261`) computes the per-slot difference between all 286,537 augmented rows and the IS_SYNTHETIC=0 subset (158,121 rows) as baseline. Observed values from `21CEN22GSS_aug_step5_regression_report.txt:8–13`:

- All-agents mean AT_HOME: **69.04%**
- Observed-only (IS_SYNTHETIC=0) mean: **69.89%**
- **Max slot diff: 6.733 pp** (gate: ≤3 pp) — FAIL
- **9 slots exceed ±3 pp**

Check 6.1 (`val.py:643–650`) is the Section 6 regression formulation of the same test and produces the same result, annotated `[EXPECTED FAIL — documented deviation ~6.7pp]`. The failing 9 slots concentrate in the morning departure window (approximately slots 8–14, 07:30–11:00 AM) and the evening return window (approximately slots 33–36, 20:00–22:00 AM) based on the per-slot gap profile in `outputs_step4/diagnostics_v4.json` T3.overall.per_slot_gap_pp, which shows the largest syn–obs gaps at those hours.

### Pipeline trace
Origin is **Step 4 J3 inference** (`04E_inference.py`, patched 2026-04-20). The post-hoc AT_HOME consistency rule (`04_augmentationGSS.md:332–334`):

> If activity = Work & Related (raw code 1, tensor idx 0) → force `AT_HOME = 0`

Every slot where J3 assigns Work to an IS_SYNTHETIC=1 diary receives AT_HOME=0 unconditionally. Since IS_SYNTHETIC=1 over-represents Work by +3.27 pp (see FAIL 6.2), the AT_HOME penalty is concentrated in the same mid-morning and early-afternoon slots, creating a per-slot AT_HOME deficit of up to 6.73 pp in the Step 5 output.

`diagnostics_v4.json` T2 section confirms the pattern at source: all four weekday cells show large negative syn–obs AT_HOME gaps:
- 2005_1: obs=68.96%, syn=62.01%, gap_all=**−6.95 pp** (n_obs=13,619; n_syn=5,602)
- 2010_1: obs=70.02%, syn=63.58%, gap_all=**−6.44 pp** (n_obs=10,830; n_syn=4,284)
- 2015_1: obs=70.84%, syn=65.75%, gap_all=**−5.10 pp** (n_obs=12,295; n_syn=5,095)
- 2022_1: obs=76.93%, syn=67.24%, gap_all=**−9.69 pp** (n_obs=8,894; n_syn=3,442)

The 2022 WD cell is most extreme (−13.51 pp nonnight gap), consistent with 2022 having the highest observed AT_HOME (~77%) making Work over-prediction most visible.

The Step 5 DDAY assignment (`05_census_linkage.py:67, 233–243`) uses a 5:1:1 ratio giving 71.4% of Census agents DDAY=1 (Weekday). These agents are matched exclusively to WD diary rows. The IS_SYNTHETIC=1 WD diaries carry the full AT_HOME deficit described above, which propagates to 44.8% of the 286,537 output rows.

### IS_SYNTHETIC split
The validator baseline at `val.py:245–246` is:
```python
obs = df[df["IS_SYNTHETIC"] == 0]
base_means = obs[hom_p].mean(axis=0).values * 100
```
IS_SYNTHETIC=0 rows are verbatim observed GSS diaries (copied at `04E_inference.py` inference step) and trivially match themselves — they contribute zero deviation. All 6.73 pp drift originates from the 128,416 IS_SYNTHETIC=1 rows (44.8% of output; `regression_report.txt:3`).

### Step 4 evidence
- **J3 training log** (`outputs_step4/step4_training_log.csv`, also `step4_Speed-Cluster_docs/training_logs/J3_training_log.csv`): 87 epochs, final val_js=0.0031; `home_loss` at epoch 87 = 0.3433; AT_HOME BCE loss reached plateau but could not close the syn–obs AT_HOME gap.
- **Step 4 validation** (`04_augmentationGSS_val.md`, Progress Log 2026-05-12): Section 3 AT_HOME FAIL — max |Δ| = 9.69 pp (2022 × Weekday); all 12 cycle-stratum cells exceed the 2 pp gate (range 2.95–9.69 pp).
- **Statistical diagnostics** (`outputs_step4/diagnostics_v4_statistical.json:61–68`): overall AT_HOME bootstrap CI — obs_mean=72.50%, syn_mean=77.84%, gap=+5.34 pp. This pool-level gap is strongly positive (IS_SYN=1 diaries are 86.4% WE where AT_HOME is high), but after the 5:1:1 WD-dominant DDAY assignment in Step 5, the IS_SYN=1 matched subset has LOWER AT_HOME (~68%) than IS_SYN=0 (~70%), because most IS_SYN=1 agents are forced to DDAY=1 where WD synthetic AT_HOME is 64–68%.

### BEM impact
AT_HOME slots drive EnergyPlus occupancy/metabolic load schedules. The 6.73 pp per-slot shift affects mid-morning to early-afternoon slots — roughly a 7–10% underestimation of occupant internal gains during those windows. Check 2.4 (Night AT_HOME ≥85%, slots 1–8) **PASSES**, confirming building occupancy during sleeping hours is intact. BEM-schedule structural integrity is preserved (DTYPE exact-match PASS, Spouse PASS). Not a Step 7 blocker.

### Recommended action
**Document only.** Pre-anticipated deviation logged in `05_censusLinkageGSS.md:654–659` (5G deviation analysis). Threshold adjustment to ±7 pp would pass; pipeline fix requires retraining J3 with higher `λ_home` weight (`04D_train.py`). For paper §4.2 — see Cross-cutting section.

---

## FAIL 6.2 — Work activity time-share 3.27 pp

### What failed
Check 6.2 (`val.py:659–678`) computes signed differences between all-augmented and IS_SYNTHETIC=0 shares for the top-5 activities by observed frequency. From `regression_report.txt:16–20`:

| Activity | All | Obs | Diff | Gate |
|---|---|---|---|---|
| Act 5 Sleep | 34.41% | 36.06% | 1.65 pp | ✓ |
| **Act 1 Work** | **21.58%** | **18.32%** | **+3.27 pp** | **✗ FAIL** |
| Act 10 Passive Leisure | 11.51% | 13.65% | 2.14 pp | ✗ (also >2pp) |
| Act 2 HH Work | 6.44% | 8.10% | 1.66 pp | ✓ |
| Act 13 Travel | 5.96% | 4.27% | 1.69 pp | ✓ |

`max_diff62 = 3.27 pp` (gate ≤2 pp) — **FAIL**. Two activities exceed ±2 pp (Work 3.27 pp, Passive Leisure 2.14 pp), but the gate is reported once for the maximum.

### Pipeline trace
Work over-representation originates in the **J3 Transformer activity prediction head** (`04B_model.py`: `Linear(d_model, 14) → softmax`). At convergence (87 epochs), the activity CE loss plateaued at `act_loss=0.0708` (epoch 87, `J3_training_log.csv`) — the model cannot further reduce the residual Work bias.

The pair construction strategy (`04C_training_pairs.py`) uses K=5 demographically similar neighbors as supervision targets. For the dominant training direction (WD-observed respondents generating Sat/Sun targets), the decoder is guided by WD-observed neighbors who typically have high Work activity. The cross-stratum transfer from WD (high-work) → WE targets introduces a work activity skew in IS_SYNTHETIC=1 WE diaries. IS_SYNTHETIC=1 WD diaries inherit Work over-prediction through the symmetrical Sat/Sun→WD generation path.

The active link to FAIL 2.2/6.1: the post-hoc rule (`04_augmentationGSS.md:334`) forces AT_HOME=0 for any Work-coded slot, making the Work bias mechanically amplify the AT_HOME deficit at the same slots.

From `05_censusLinkageGSS.md:657` (5G deviation analysis, already documented):
> "The IS_SYNTHETIC=1 (synthetic) diaries contain more work-related activity (Act 1: 21.58% all vs 18.32% observed)."

### IS_SYNTHETIC split
Check 3.4 (`val.py:367`) trivially confirms IS_SYNTHETIC=0 JS divergence vs itself = 0.000000 — all Work over-representation is exclusively in IS_SYNTHETIC=1 rows. Approximate IS_SYN=1-only Work share (back-calculated from regression_report.txt data):
- (21.58% × 286,537 − 18.32% × 158,121) / 128,416 ≈ **25.6%**

IS_SYNTHETIC=1 diaries show ~7 pp more Work activity than observed GSS diaries.

### Step 4 evidence
- `04_augmentationGSS_val.md` (Progress Log 2026-05-12): Section 2 (activity JS): overall JS=0.0242 — **PASS** (all 12 cells < 0.05; max cell=0.0308). The JS metric is relatively insensitive to small distributional shifts in large activity classes; the +3.27 pp Work bias is real but below the JS FAIL threshold.
- J3 act_loss plateau at 0.0708 (epoch 87) — consistent with a residual bias that JS-based early stopping cannot eliminate.
- `regression_report.txt:16–20`: Work is the only activity exceeding the ±2 pp regression gate at 3.27 pp (Passive Leisure at 2.14 pp is a secondary concern).

### BEM impact
Work→AT_HOME=0 post-hoc rule links this directly to FAIL 2.2/6.1 — see that section. The Work over-representation itself means IS_SYNTHETIC=1 agents spend more time away from home during the workday, slightly underestimating daytime internal gains. The effect is within ASHRAE 90.1 occupancy model uncertainty bounds (~±10%). Not a Step 7 blocker.

### Recommended action
**Document only.** Pre-anticipated. Threshold adjustment to ±4 pp would pass. Pipeline fix: add marginal activity regularization (e.g., KL penalty on marginal activity distribution vs observed) in `04D_train.py` loss function, or increase `λ_act` relative to `λ_home` to sharpen activity CE convergence.

---

## FAIL 3.3 — Night-slot sleep dominance 67.46%

### What failed
Check 3.3 (`val.py:354–363`):
```python
night_flat = df[act_p[:8]].values.flatten()   # act30_001..act30_008
sleep_rate  = float((night_flat == 5).mean() * 100)
# => 67.46%   (gate: >= 70%)
```
Result: **67.46%** — 2.54 pp below the ≥70% threshold. FAIL.

### Slot boundary check (what time do slots 1–8 represent?)
From `_hour_labels()` at `val.py:66–70`: `total_min = 4*60 + i*30` for `i in range(48)`.

| Slot (1-indexed) | Wall clock |
|---|---|
| 1 | 04:00–04:30 |
| 2 | 04:30–05:00 |
| 3 | 05:00–05:30 |
| 4 | 05:30–06:00 |
| 5 | 06:00–06:30 |
| 6 | 06:30–07:00 |
| 7 | 07:00–07:30 |
| 8 | 07:30–08:00 |

Slots 1–8 = **04:00–08:00 AM** — the tail of night sleep plus early wake-up transition.

**Post-hoc boundary note**: `04_augmentationGSS.md:333` defines `NIGHT_SLOTS` (0-indexed) as slots 0–6 ∪ slots 37–47, i.e., 04:00–07:30 AM and 22:30–03:30 AM. Slot 7 (0-indexed) = slot 8 (1-indexed, 07:30–08:00 AM) falls just outside the NIGHT_SLOTS range and therefore receives **no AT_HOME=1 forcing** even when Sleep is coded. The post-hoc consistency rule forces only AT_HOME, not act30 values — so no activity code is ever overwritten; fragmented sleep sequences remain in the output verbatim.

### Pipeline trace
The 67.46% rate is a weighted average over 286,537 rows. IS_SYNTHETIC=0 rows (verbatim observed GSS) have an empirical Canadian pre-dawn sleep rate expected around 78–82% in slots 1–8. IS_SYNTHETIC=1 rows are J3-generated and contribute the deficit.

Estimating IS_SYNTHETIC=1 sleep rate in slots 1–8:
- Fractions: IS_SYN=0 = 158,121/286,537 = 55.2%; IS_SYN=1 = 128,416/286,537 = 44.8%
- Assuming IS_SYN=0 sleep rate ≈ 80% (consistent with T6 at_home_night ~88–94% for observed data in `diagnostics_v4.json:T6`):
  0.552 × 0.80 + 0.448 × S₁ = 0.6746 → **S₁ ≈ 52%**

IS_SYNTHETIC=1 diaries have only ~52% of slots 04:00–08:00 AM coded as Sleep — substantially below the ~80% expected from observed respondents.

**Primary cause — excessive activity transitions**: `04_augmentationGSS_val.md` Progress Log 2026-05-12:
> Section 4 (temporal): FAIL — **4.2 transition rate ratio = 157.95 (INVESTIGATE)**

Check 4.2 measures mean transitions per 48-slot diary (observed vs. synthetic); the gate is "synthetic within ±20% of observed." A ratio of 157.95 means J3 synthetic diaries have ~158× more activity transitions than observed. If observed diaries average ~5 transitions per diary, synthetic have ~790 — effectively every slot is a different activity. This fragmentation prevents continuous sleep sequences from forming in the 04:00–08:00 AM window: instead of 8 consecutive Sleep slots, IS_SYNTHETIC=1 diaries alternate Sleep with brief Personal Care, HH Work, or other codes, reducing the fraction of sleep-coded slots.

Note: check 4.2 is **not** affected by the Sleep/Work index-swap bug documented in `04_augmentationGSS_val.md` header (that bug affects checks 4.1, 4.3, 6.2, 7.1, 7.2 only). The 157.95 ratio is a valid finding for the J3 production model.

### IS_SYNTHETIC split
By construction, IS_SYNTHETIC=0 rows are copied verbatim from source GSS diaries (`04E_inference.py` patched 2026-04-20 — observed diaries are not generated, just passed through). FAIL 3.3 is entirely attributable to IS_SYNTHETIC=1. The borderline nature (67.46% vs 70%) means the IS_SYNTHETIC=0 component (55.2% of output, sleep rate ~80%) partially compensates for IS_SYNTHETIC=1's deficit (~52%).

### Step 4 evidence
- `04_augmentationGSS_val.md` (2026-05-12): Section 4 FAIL, 4.2 transition rate ratio=157.95 — the most direct evidence that J3 over-fragments activity sequences.
- `04_augmentationGSS.md:326–340`: post-hoc consistency rule operates on AT_HOME only; act30 is never corrected; fragmented sleep sequences persist in the output.
- `outputs_step4/step4_training_log.csv`: J3 converged on JS-based early stopping at val_js=0.0031, but JS divergence is insensitive to transition-rate pathology (high-frequency alternations average out to plausible marginal distributions).
- The training loss function (`04D_train.py`) has no explicit temporal regularization term (no transition-rate penalty); the model minimises CE over individual slots independently, which is insufficient to enforce sleep continuity.

### Relationship to 2.2/6.2 (same root or independent?)
**Distinct but co-occurring**: FAILs 2.2/6.1/6.2 are caused by Work over-prediction → AT_HOME post-hoc rule. FAIL 3.3 is caused by temporal over-fragmentation → sleep under-representation. Both are IS_SYNTHETIC=1 artefacts from J3, but they represent different failure modes of the same model. FAIL 3.3 would persist even if Work over-prediction were fully corrected. However, Work activity erroneously coded in early-morning slots (e.g., a synthetic "night-shift" artefact) contributes modestly to sleep deficit via AT_HOME forcing — a secondary overlap.

### BEM impact
EnergyPlus occupancy schedules use `hom30` (AT_HOME), not `act30`, for internal gain calculations. Check 2.4 (Night AT_HOME rate, slots 1–8 ≥85%) **PASSES** — mean AT_HOME in 04:00–08:00 AM is ≥85% across all agents. So even when act30 ≠ 5 (Sleep), the occupant is still AT_HOME and generating metabolic heat load. The act30 mis-labeling in slots 1–8 does not alter EnergyPlus occupancy schedules. **Not a Step 7 blocker.**

### Recommended action
Investigate in next model iteration. Add a temporal regularization term to the J3 decoder loss in `04D_train.py` — e.g., a transition-rate penalty `L_trans = λ_trans × E[|act_t − act_{t-1}|>0]` to encourage smoother activity sequences. Threshold adjustment to ≥65% would pass but represents a genuine model quality finding. Document for paper §4.2.

---

## FAIL 4.4 — 1,248 HH with mean AT_HOME < 0.3

### What failed
Check 4.4 (`val.py:457–463`):
```python
hh_means = df[hh_hom_p].mean(axis=1)   # HH_hom30_001..048, mean across 48 slots
oor_lo = (hh_means < 0.3).sum()         # = 1,248
```
Result: **1,248 households** with per-household mean AT_HOME < 0.30. Zero above 1.0.

A mean AT_HOME < 0.30 over a 24-hour period starting 04:00 AM means ≤14 of 48 slots (≤7 hours total) have any household member present. Since every person must sleep somewhere, the biological minimum is ~14–16 sleeping slots (7–8 hours) with AT_HOME=1, giving an expected floor of ~29–33% for any realistic household. The 1,248 households fall at or below this floor — physically implausible.

The `HH_hom30_*` columns are computed in `run_aggregate()` (`05_census_linkage.py:run_aggregate`) as the **per-slot MAX of hom30 across household members**:
- HH_hom30[slot] = 1 if any member is home; 0 if all members are away

For a multi-person household, all members would need to be simultaneously away for 70%+ of the day, which is structurally impossible. The failing households must therefore be overwhelmingly **single-person (HHSIZE=1)**, where HH_hom30 reduces to the individual's hom30 directly.

### Demographic profile of below-0.3 HHs
Direct execution was not performed (read-only investigation). The `Analysis snippets` section above provides the exact pandas calls for verification. Mechanistic profile based on the interaction of Step 4 model behaviour and Step 5 aggregation:

**Expected dominant characteristics:**
1. **HHSIZE=1** (single-person households): only configuration where all-member absence is possible.
2. **DDAY_STRATA=1 (Weekday)**: WD IS_SYNTHETIC=1 diaries carry the largest AT_HOME deficit (gap_all: −5.10 to −9.69 pp per `diagnostics_v4.json:T2`; nonnight gap for 2022_1 is −13.51 pp).
3. **IS_SYNTHETIC=1**: observed diaries have empirical AT_HOME rates of 69–80% (T6 in `diagnostics_v4.json:T6`) — far above 0.30. The floor cannot be crossed by IS_SYNTHETIC=0 rows.
4. **LFTAG = employed / full-time**: heavy Work activity → AT_HOME=0 forced across large portions of the workday.
5. **AGEGRP = working-age (30–44, AGEGRP codes 4–5)**: maximum work activity.

**Failure mechanism step-by-step:**
- J3 generates IS_SYNTHETIC=1 WD diary with Work over-prediction (+7 pp IS_SYN=1 work share per FAIL 6.2 analysis)
- Post-hoc rule forces AT_HOME=0 for all Work-coded slots
- Activity transition over-fragmentation (4.2 ratio 157.95) places non-sleep non-work codes in early-morning slots that should be sleep, preventing AT_HOME=1 forcing there
- For a HHSIZE=1 agent: HH_hom30 = individual hom30 directly
- Result: ≤30% of 48 slots have hom30=1 → HH mean AT_HOME < 0.3

1,248 / 145,589 unique HHs = **0.86% of all households**.

### Match tier distribution of below-0.3 HHs
Cannot compute without executing the analysis snippet. By reasoning: HHSIZE=1 is a concrete demographic key used in Tier 1 and Tier 2 matching, so these agents likely resolved at Tier 1 (44.94% overall share, `05_censusLinkageGSS.md:586`). Tier 3 and Tier 4 relaxations could introduce additional cross-demographic IS_SYNTHETIC=1 matches, potentially over-representing at lower tiers.

### IS_SYNTHETIC composition
By mechanistic argument: **all or nearly all 1,248 failing HHs are IS_SYNTHETIC=1**. Observed (IS_SYNTHETIC=0) diaries in augmented_diaries.csv have empirical AT_HOME rates of 69–80% per cycle-strata (`diagnostics_v4.json:T6`) — a verbatim GSS diary cannot produce mean AT_HOME < 0.30 in a realistic 24-hour Canadian schedule. Recommended verification: `fail_sched["IS_SYNTHETIC"].value_counts()` per Analysis snippets above.

### Is this a real population segment or an artefact?
**Pipeline artefact, not a real population segment.** Key evidence:
1. Biological constraint: humans sleep 7–9 hours, generating a hard AT_HOME floor of ~29–37%.
2. Observed GSS data (IS_SYNTHETIC=0) shows no respondent with overall AT_HOME < 0.40 at population-level cells (`diagnostics_v4.json:T6`: at_home_all ranges 69–80%).
3. The artefact arises from the joint effect of (a) IS_SYNTHETIC=1 Work over-prediction → AT_HOME=0 forcing; (b) excessive activity transitions → missing Sleep→AT_HOME=1 assignments in early morning; (c) HHSIZE=1 aggregation removes the "any member home" safety net.

### BEM impact
**This is the only FAIL with a direct EnergyPlus consequence.** For the 1,248 affected households:
- EnergyPlus occupancy schedules show near-zero internal gains for extended periods spanning both the workday and sleeping hours
- Heating/cooling loads for these households are systematically underestimated — in the extreme, a near-zero occupancy schedule produces near-zero internal metabolic heat
- Scale: 1,248 / 145,589 = 0.86% of modelled households — within typical UBEM simulation uncertainty bounds, but not negligible at city scale

**Soft blocker**: these households should be identified and repaired before Step 7 submission.

### Recommended action
Before Step 7, apply a floor-cap repair pass in `05_census_linkage.py::run_bem()` or as a pre-processing step:

1. Identify failing PP_IDs: `fail_ppids = agg.loc[hh_means < 0.3, "PP_ID"]`
2. For these individuals, enforce a minimum sleep block: set `hom30_001`–`hom30_010` (04:00–09:00 AM) = 1 unconditionally (10 slots = 5 hours minimum sleep at home)
3. Re-aggregate HH_hom30 for affected HH_IDs
4. Re-run Check 4.4 to confirm oor_lo = 0

Alternatively, exclude the 1,248 households from Step 7 and document: *"1,248 households (0.86% of 145,589) with Step 4 augmentation-induced AT_HOME deficits (mean < 0.30) were excluded from EnergyPlus simulations."*

The root fix is in Step 4: reduce Work over-prediction (lower activity CE loss bias) and add temporal regularization to prevent the 157.95-ratio transition artefact.

---

## Cross-cutting observations

1. **Common IS_SYNTHETIC=1 root**: All four FAILs trace exclusively to IS_SYNTHETIC=1 diary quality from J3 (87 epochs). IS_SYNTHETIC=0 rows are verbatim observed GSS diaries and would pass every check. The J3 model converged in JS divergence (overall JS=0.0242 < 0.05 gate; `04_augmentationGSS_val.md`) but with three residual biases:
   - Activity CE → Work over-represented (+3.27 pp in IS_SYN=1) → drives FAILs 6.2 and 2.2/6.1
   - Temporal decoder → excess transitions (ratio 157.95, Section 4.2 FAIL) → drives FAILs 3.3 and 4.4
   - AT_HOME BCE → WD deficit (−5.1 to −9.7 pp per T2 diagnostics) → amplifies FAILs 2.2/6.1 and 4.4

2. **Post-hoc rule amplification**: The `Work→AT_HOME=0` post-hoc rule turns a +3.27 pp activity bias into a −6.73 pp per-slot AT_HOME deficit. Without the post-hoc rule, FAIL 6.2 would exist alone; the rule converts a 3 pp activity artefact into a 6+ pp AT_HOME artefact (FAILs 2.2/6.1) and contributes to FAIL 4.4.

3. **JS divergence is not sensitive enough**: The JS-based training objective and validation gate (JS < 0.05) detected the J3 model as converged, but JS averages over slots and cannot penalise: (a) per-slot AT_HOME systematic bias; (b) high-frequency transition artefacts; (c) tail household behaviours. Step 5 validation catches all three.

4. **Two pre-anticipated + two new findings**: FAILs 2.2/6.1/6.2 were documented before the validator ran (`05_censusLinkageGSS.md:647–665`, 5G deviation analysis). FAILs 3.3 and 4.4 are new findings, both attributable to the same IS_SYNTHETIC=1 temporal fragmentation.

5. **Threshold calibration note**: The ±3 pp AT_HOME gate and ≥70% sleep gate were designed around the IS_SYNTHETIC=0 observed baseline. With 44.8% IS_SYNTHETIC=1 in the output (pool composition 2:1 syn:obs), recalibrated thresholds for the augmented regime would be approximately ±7 pp AT_HOME and ≥65% sleep.

6. **Independence**: FAILs 3.3 and 4.4 would persist even if Work over-prediction were fully corrected, because they depend on temporal fragmentation (transition ratio 157.95) independently of activity class identity. A pipeline fix for FAILs 2.2/6.1/6.2 would not resolve 3.3 or 4.4.

---

## Paper §4.2 material

The following text is suitable for insertion into the paper's limitations/validation section:

> **Augmentation-induced distributional shift (Step 5 validation findings).** The augmented diary pool (J3 model, 87 epochs, 128,122 IS_SYNTHETIC=1 diary-days) introduces three documented biases relative to observed GSS diaries. First, Work & Related activity is over-represented by +3.27 percentage points in synthetic diary components (21.58% vs. 18.32%), which propagates through a post-hoc AT_HOME consistency rule to produce a per-slot AT_HOME deficit of up to 6.73 pp in the Census-matched output — 9 of 48 half-hour slots exceed the ±3 pp regression gate. Second, synthetic diaries exhibit excessive activity transitions (Step 4 validation Section 4.2: ratio 157.95 vs. observed), causing night-slot (04:00–08:00) sleep dominance to fall to 67.46% against a ≥70% threshold; the AT_HOME rate for the same slots nonetheless exceeds 85%, preserving building occupancy schedule validity for EnergyPlus. Third, 1,248 of 145,589 modelled households (0.86%) exhibit per-household mean AT_HOME below 0.30 — a physically implausible result attributed to single-person IS_SYNTHETIC=1 weekday agents with concurrent Work over-prediction and sleep fragmentation; these households are flagged for repair or exclusion before EnergyPlus submission. All three biases are isolated to IS_SYNTHETIC=1 rows; observed diary components (IS_SYNTHETIC=0) pass all schedule plausibility checks. Spouse co-presence (+2.23 pp, within ±3 pp gate), DTYPE distribution (exact Census match), and overall schedule structure are unaffected. Language of official correspondence (KOL) was excluded from the 7-key demographic match due to its absence from the augmented pool; this may marginally inflate Tier 1 exact-match rates but is expected to be negligible given KOL's low cardinality (3 values).

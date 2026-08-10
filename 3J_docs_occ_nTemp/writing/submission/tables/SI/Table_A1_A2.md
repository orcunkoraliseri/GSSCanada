# Table A1 - Model card: the three-GSS-head conditional Transformer (Step 4, Leg-3)

Source: `Leg3_4-split/Step4_docs/3rdJ_04_augmentationGSS_4split.md` (Deltas A-I, CONTRACT section),
`Leg3_4-split/Step4_docs/3rdJ_04B_model_4split.py` (`PROD_CONFIG`, lines 86-92), and the three
deep-research playbooks that froze the design (`dr_L3-11`, `dr_L3-12`, `dr_L3-13`, all RESOLVED
2026-07-02). Every hyperparameter below was checked against the Step-4 doc or the code itself, not
copied from the brief; the one line that could not be independently confirmed is marked `⚠ check
source`.

**About the `Source in the project repository` column.** The right-hand column of the three tables
below gives, for each hyperparameter, the file and line in the authors' own project repository from
which that value was read. These are internal paths and internal document identifiers; they are not
expected to resolve for a reader, and nothing in this model card depends on opening them. They are
printed so that every number in the card is attributable to a specific place in the build rather than
restated from a summary, and so that a value which was read from code can be told apart from one that
was read from a design document. Where the two disagreed, the disagreement is disclosed in the notes
beneath the table rather than reconciled silently.

### A1.1 - Architecture

| Component | Specification | Source in the project repository |
|---|---|---|
| Backbone | Shared multi-head Transformer encoder-decoder, "J3 lineage"; **AUGMENT** verdict (keep incumbent, graft targeted upgrades) - no 2023-2026 challenger (discrete diffusion MDLM/SEDD, decoder-only AR, SSM/Mamba, discrete flow matching, non-AR iterative) passed the project's gates at this scale | `dr_L3-11_architecture_pressure_test_REPORT.md` Table 5; `3rdJ_04_augmentationGSS_4split.md:61` |
| Encoder | 6-layer Transformer, `d_model=256`, `n_heads=8`, `d_ff` per layer config, ~29M parameters | `3rdJ_04B_model_4split.py:86-92` (`PROD_CONFIG`: `d_model=256, n_heads=8, N_enc=6, N_dec=6, d_act=32, d_cycle=32`); `dr_L3-13_training_regimen_REPORT.md:4` ("~29M parameters") |
| AR activity arm | Autoregressive decoder, 14-category activity classes, 48 half-hour slots/day | `3rdJ_04_augmentationGSS_4split.md` CONTRACT (`act_logits (B,48,14)`) |
| Head 1 | `AT_HOME` binary presence (shipped, Leg-1/Leg-2, unchanged) | `3rdJ_04B_model_4split.py` - `home_head` |
| Head 2 | `AT_WORK` binary presence (shipped, Leg-2, unchanged) | `3rdJ_04B_model_4split.py` - `work_head` |
| **Head 3 (new, Leg-3)** | `AT_RETAIL` binary presence - `retail_head = Linear(d_model,d_model) → Tanh → Linear(d_model,1)`, off Arm-2's fused representation, mirrors `work_head`; AR-arm `detach()` barrier untouched | `3rdJ_04_augmentationGSS_4split.md` Delta B |
| Co-presence head | 9-channel co-presence (Alone/Spouse/Children/parents/otherInFAMs/otherHHs/friends/others/colleagues), unmodified by the retail delta | `3rdJ_04_augmentationGSS_4split.md` CONTRACT (`cop_logits (B,48,9)`) |
| aux_seq width | `(n,48,11) → (n,48,12)` = `[AT_HOME \| AT_WORK \| AT_RETAIL \| 9×cop]`; `retail_avail (n,48) bool` mirrors `work_avail` | `3rdJ_04_augmentationGSS_4split.md` Delta A; CONTRACT |

### A1.2 - Conditioning vector (`d_cond = 120`)

| Covariate group | Encoding | Notes |
|---|---|---|
| Demographics | `nn.Embedding` per categorical field, concatenated/projected | `AGEGRP, SEX, MARSTH, HHSIZE, PR, CMA, KOL, LFTAG, HRSWRK, NOCS, COW, ATTSCH, POWST, TOTINC` + `NAICS/TELEWORK/WORK_SCHEDULE` office set; unchanged from Leg-2 in structure |
| Day-type stratum | `DDAY_STRATA`, `nn.Embedding(3, d_model)` | drives diurnal shape (Wasserstein gate) |
| Cycle year | **Continuous projection**, `(year-2005)/25 → nn.Linear(1, d_model)` - **never categorical** | must extrapolate to unseen 2030; `dr_L3-13` Table 2 + Fix-vs-Ablate item 2 |
| Collection mode | `COLLECT_MODE`, low-capacity `nn.Embedding(2, 16)` | confound control, deliberately too small to leak physical signal |
| No retail-specific conditioning is added | - | "retail presence is population-behavioural, not occupation-gated" |

⚠ **d_cond drift, disclosed in the build log, not part of the retail delta.** Leg-2's `d_cond=119` grew
to Leg-3's `120` because `MARSTH` gained a missing-value (`-1`) category - an independent Leg-3
data-pipeline fix, not something the retail head introduced. This contradicts the runbook's own "no
retail-specific conditioning is added / conditioning unchanged from Leg-2" framing at the field-count
level (structure unchanged, width changed by one unrelated field).
Source: `3rdJ_04_augmentationGSS_4split.md:298` (2026-07-19 entry, "Step 0" paragraph).

### A1.3 - Training regimen

| Item | Value | Source in the project repository |
|---|---|---|
| Loss weights (`α_resid : α_work : α_retail`) | **1.0 : 0.5 : 0.3** | `3rdJ_04_augmentationGSS_4split.md` Delta D; `dr_L3-13` §"Fix-vs-Ablate" item 1 |
| Scalarization | **Unitary/fixed-weight scalarization** (Kurin et al. 2022) - dynamic weighters (SLAW/UW/GradNorm/DWA/CAGrad) explicitly rejected; they destabilize on a ~2%-positive task | `3rdJ_04_augmentationGSS_4split.md` Delta D: "`WEIGHT_MODE=fixed`... Never SLAW / UW / GradNorm / DWA / CAGrad"; code confirmation at `3rdJ_04_augmentationGSS_4split.md:302` ("No `UW`/`SLAW`/`equal`/`GradNorm`/`DWA`/`CAGrad` code path exists anywhere in the new file") |
| Gradient surgery | **PCGrad**, pairwise across the 3-task set, applied only in `--phase joint` | `3rdJ_04_augmentationGSS_4split.md` Delta D; `:302` |
| Class imbalance (retail, ~2% positive) | `BCEWithLogitsLoss(pos_weight = 49)` | `3rdJ_04_augmentationGSS_4split.md` Delta C |
| Inference logit shift | `logit_calibrated = logit_raw − ln(49)` ≈ `−3.89`, applied in 04E only, **never during training** | `3rdJ_04_augmentationGSS_4split.md` Delta C; `dr_L3-13` §"Fix-vs-Ablate" item 3 (Menon et al. 2020) |
| Warmup phase | **5 epochs**, Head 3 only trainable (encoder + Heads 1-2 + cop frozen), lr **1e-3** AdamW | `3rdJ_04_augmentationGSS_4split.md` Delta E table |
| Joint phase | **15 epochs**, all parameters trainable, lr **1e-4** AdamW, PCGrad ON, fixed α, early stopping on the gate set (patience 10), never on training loss | `3rdJ_04_augmentationGSS_4split.md` Delta E table |
| Dropout | 0.1, attention/residual only - **never on output projections** | `3rdJ_04_augmentationGSS_4split.md` Delta E |
| Weight decay | 1e-4, AdamW | `3rdJ_04_augmentationGSS_4split.md` Delta E |
| Label smoothing | 0 (disabled) | `3rdJ_04_augmentationGSS_4split.md` Delta E; `dr_L3-13` Table 4 (label smoothing rejected - distorts calibration) |
| Diary augmentation | None (no slot jitter / cyclic shift) | `3rdJ_04_augmentationGSS_4split.md` Delta E; `dr_L3-13` Table 4 |
| Scheduled sampling | Dropped (ranked by `dr_L3-11`, rejected by `dr_L3-13` at 48-slot length) | `3rdJ_04_augmentationGSS_4split.md` Delta E |
| Batch composition | Stratified 50% weekday / 25% Sat / 25% Sun + inverse-cycle-frequency weighting (2022 has fewest diaries) | `3rdJ_04_augmentationGSS_4split.md` Delta E |
| Survey weights | `WGHT_PER` inside the loss, clipped at the 99th percentile | `3rdJ_04_augmentationGSS_4split.md` Delta E |
| Ablation budget | Hard cap **4 runs** (shared / LoRA-adapter r=8 / semi-shared / reserve) | `3rdJ_04_augmentationGSS_4split.md` Delta I |

⚠ **Measured vs. frozen `pos_weight`.** The frozen design value is **49** (an a-priori estimate at
~2% positive, from `dr_L3-08`/`dr_L3-11`). The actual Step-4 training-split positive rate implies a
measured value of **50.1056** (`retail_pos_weight` recorded in `step4_feature_config.json`). The
shipped code trains on the frozen **49**, not the recomputed value; both numbers are close but not
identical, and the doc records this as expected, not as a defect.
Source: `3rdJ_04_augmentationGSS_4split.md:274`.

### A1.4 - Decoding

| Item | Value | Source in the project repository |
|---|---|---|
| AR sampling | Temperature **T = 0.7** + nucleus **p = 0.9** | `3rdJ_04_augmentationGSS_4split.md` Delta F item 1 |
| Min-dwell constraint | **≥ 2 slots (60 min)** for work and retail events, applied AFTER the exclusivity projection and the activity override (so it can only flip 1→0) | `3rdJ_04_augmentationGSS_4split.md` Delta F item 2; `:309` |
| Decision thresholds | `θ_home = 0.50`, `θ_work = 0.40`, `θ_retail = 0.15` (F1-derived on validation) | `3rdJ_04_augmentationGSS_4split.md` Delta G |
| Exclusivity enforcement | Threshold-normalized argmax projection: a slot with >1 channel over threshold keeps only `c* = argmax_c p_c(t)/θ_c` | `3rdJ_04_augmentationGSS_4split.md` Delta G; `dr_L3-12` §2 |
| ISR (Impossible-State Rate) | Raw model output: hard gate **≤ 0.5%**. Final injected schedules: **0%** by construction | `3rdJ_04_augmentationGSS_4split.md` Delta G |
| Rejected alternative | Categorical/softmax location head - rejected (softmax competition crushes the ~2% retail class, couples calibration, breaks Head-1 bit-compatibility) | `dr_L3-12_output_representation_REPORT.md` Table 5 |

⚠ **Leg-2 decode temperature note.** The Leg-2 sweep had locked `T = 0.8` with no nucleus sampling.
Leg-3's `T = 0.7 + nucleus p = 0.9` is a frozen but distinct choice from `dr_L3-13`; the build doc
flags that if Heads-1/2 regression gates trip on the decode change alone, this is the mechanism to
inspect first (not yet triggered as of the last recorded validator run).
Source: `3rdJ_04_augmentationGSS_4split.md` Delta F item 1; `:314`.

### A1.5 - Checkpoint selection rule and the gate record

**Documented rule (gate-first → lexicographic).** Keep only checkpoints passing every hard gate - 
`ΔJS ≤ 0.002` bits on Heads 1-2 vs. the Leg-2 baseline, `ISR_raw ≤ 0.5%`, `PR-AUC ≥ 0.15 AND F1 ≥
0.25` on retail, midday (11:00-14:00) rate error `≤ 3.0 pp`, mean transitions `≥ 0.05`/day - then
**maximize retail F1** among survivors. Report mean ± sd over 5 seeds.
Source: `3rdJ_04_augmentationGSS_4split.md` "Checkpoint selection" section; `dr_L3-13` Table 5 /
§"Model Selection Rule".

**Shipped Step-4 validator scorecard (seed 3 pool, `seed_3_g3fix_raked3_mindwell_actv`):
147 PASS / 18 WARN / 1 FAIL.** The sole FAIL is `OW5` (day-type ordering), pre-existing in the Leg-2
baseline and non-blocking; `REG-4` PASS confirms no NEW fail was introduced.
Source: `3rdJ_04_augmentationGSS_4split.md:51`.

🔴 **Disclosed deviation: the shipped checkpoint was not selected by the rule above.**
`3rdJ_04D_train_4split.py:881` saves `best_model.pt` on a composite `val_score = mean_js +
0.5·(home_gap+work_gap+retail_gap)/3` (`:499`) that contains **neither** `pr_auc` nor `f1`. The
documented rule and the code's actual selection rule pick different epochs in **4 of 5 seeds**; seed 3
ships as the argmin of the composite (1st of 5 on `val_score`, 4th of 5 on the documented rule's
metric). The gap to the documented rule's global winner is **+0.0218 retail F1** (5.6% relative, 0.16
sd of the cross-seed spread). This was reviewed and left as-is on 2026-08-06 (`V3-H1`, option C): the
documented rule is **not** amended (it remains the specification, consistent with the Leg-1/Leg-2
"never a single composite score" lesson), the shipped deviation is recorded with its reason, and three
explicit reopen triggers are on file (a person-level gate disagreeing with `val_score`'s ranking; the
F1 gap exceeding 1 sd of the cross-seed spread; Steps 5-9 reopening for any other reason).
Source: `3rdJ_04_augmentationGSS_4split.md:159-204` (the `V3-H1` note); `improvements/v3/3rdJ_L3_v3_implementation.md:115`.

---

# Table A2 - AT_RETAIL codebook per GSS cycle

Source: `Leg3_4-split/Step2_docs/3rdJ_02_harmonizeGSS_4split.md` Delta A (`:34-43`), confirmed against
`../../investigation/00_GSS_split_suitability_audit.md` §2 ("Confirmed all cycles").

| GSS cycle | Raw variable | Codes mapped to unified `occPRE == 5` ("Shopping") | Status |
|---|---|---|---|
| 2005 (C19) | `PLACE` | `06` (Grocery) + `07` (Other store / Mall) | ✅ confirmed |
| 2010 (C24) | `PLACE` | `06` + `07` | ✅ confirmed |
| 2015 (C29) | `LOCATION` | `306` | ✅ confirmed |
| 2022 (GSSP) | `LOCATION` | `3306` | ✅ confirmed |

**Granularity note.** 2005/2010's `PLACE = 06 + 07` combines two source codes (grocery, other
store/mall) into one unified value; 2015/2022's single `LOCATION` code (`306`/`3306`) is already a
merged grocery/general-merchandise bucket at the source. **Grocery vs. general merchandise is
therefore not separable in 2015 or 2022** - the harmonization keeps all four cycles on one unified
"Shopping" category for cross-cycle consistency, but a grocery-vs-merchandise retail-archetype split
is impossible from GSS. This is recorded as the reason the Leg-3 retail channel uses a single retail
archetype (drives the Step-5 single-retail-archetype decision).

**The AT_RETAIL rule itself (frozen 2026-07-02, OD-1, executed at the Step-3 tiler, not at Step 2):**

```python
AT_RETAIL = (occPRE == 5) | ((occACT == 4) & occPRE.isin({5, 9}))
```

The activity arm (`occACT == 4`, "Purchasing Goods & Services") is **gated** to plausible retail
locations `{5 Shopping, 9 Other/unspecified-out}`, which excludes the online-shopping leak
(`occACT == 4 & occPRE == 1`, shopping from home) from the retail channel. Consequences: (a)
`AT_HOME ∧ AT_RETAIL` is not a legitimate overlap, so the exclusivity projection (Table A1.4) applies
to the full `{AT_HOME, AT_WORK, AT_RETAIL}` set; (b) the per-cycle `occACT==4 × occPRE` cross-tab is
produced as a standing verification output, not skipped by the freeze.

**Excluded channel, recorded as a decision not an oversight.** `occPRE == 7` (Restaurant/bar/club) is
available in all four cycles (`PLACE=04` in 2005/2010; `LOCATION=309`/`3309` in 2015/2022) but is
explicitly out of scope for Leg-3 - the PNNL prototypes route `Dining` to the Office channel and
`LargeHotel Cafe` to the hotel-amenity NECB baseline, so there is no Space in the tower geometry for a
restaurant channel to drive (OD-9).

**Episode-time share (validation target, not a training input).** ⚠ **The value in the Step-2 doc
itself (`:43`, "~2.1-2.3%, stable across cycles") is superseded.** The corrected, measured figure is
**1.50-2.14%, an approximately 25% decline across cycles**. The decline is not a coding artefact: it
is corroborated independently across four national time-use series over comparable spans - Canada GSS
2005-2022 **-25.0%**, US ATUS 2003-2022 **-20.8%**, UK TUS/CTUR 2000-2022 **-34.4%**, Eurostat HETUS
2000-2020 **-21.4%** - and the measured level sits inside the 1.5-2.2% range every one of those series
occupies.

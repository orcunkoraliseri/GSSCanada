# Step-4 Training Investigation v2 — J-series closure, J3 ships, co-presence cleanup

This report is the v2 companion to `investigation_Training_step4.md`. It closes the Step-4 training record with the J-series outcome, documents *why* J3 was the decisive arm of the J2/J2.5/J3 parallel ladder (and why J2 / J2.5 missed by small but real margins), and isolates the one remaining residual the user flagged in scope — the Alone-channel asymmetry on 2005/2010 cycles, which is structural and not a hard gate.

The headline:

> *J-series closed all four hard gates. J3 (Hybrid AR-Encoder + Soft Activity Embedding) ships as the production Step-4 checkpoint — composite=0.6355, AT_HOME RMS=4.57 pp, Spouse=−2.03 pp, act_JS=0.0191. The residual Alone-channel asymmetry on 2005/2010 cycles is structural (the `colleagues` column was not collected for those cycles) and is the subject of the optional cop-side cleanup pass at the end of this document.*

The activity axis was already solid at J1 (act_JS=0.0274 ≪ 0.05); J3 made it ~2.6× under the gate (0.0191). AT_HOME RMS-across-strata was the one gate that J1 / J2 / J2.5 could not close — a per-stratum-cell variance problem, not an aggregate-bias problem. The J3 fix that closed it (a single `Linear(14, d_model)` projection upstream of the Arm-2 fusion concat) is small enough that the v2 doc can credibly land "this is what was missing" rather than "we added a lot."

---

## 0. Project context (carry-forward from v1, trimmed)

End-to-end pipeline: **Comprehensive Annual Occupancy Dataset Pipeline for BEM/UBEM** — *Longitudinal Occupancy Impact on Residential Energy Demand (2005–2030)*. Source overview: `00_GSS_Occupancy_Pipeline_Overview.md`. The pipeline ingests Statistics Canada GSS Time Use microdata (cycles 2005, 2010, 2015, 2022), harmonizes activity / location / co-presence taxonomies, augments diaries with a Conditional Transformer, links to Census archetypes, and emits 30-min EnergyPlus schedules. Step 4 — the subject of this report — is the augmentation step.

| Step | Purpose | Status |
|---|---|---|
| 1 — Data Collection | Pull GSS Main + Episode files for the 4 cycles | COMPLETE |
| 2 — Harmonization | Crosswalk activity (→14), location (→18 + AT_HOME), co-presence (→9 binary) | COMPLETE |
| 3 — Merge + Resolution | Episode → respondent-level wide; 144 × 10-min → 48 × 30-min | COMPLETE |
| **4 — Conditional Transformer Augmentation** | Generate the 2 missing DDAY_STRATA per respondent | **CLOSED — SHIP J3** |
| 5 — Census Linkage | Classical ML to assign Census records to GSS archetypes | UNBLOCKED |
| 6 — Progressive Fine-Tuning + 2030 Forecast | Fine-tune across cycles, project forward | PENDING |
| 7 — BEM/UBEM Integration | Schedule:Compact for EnergyPlus, CSV per archetype × climate zone × DDAY_STRATA | PENDING |

**Step-4 task.** Each respondent has one observed diary on one of three DDAY_STRATA ∈ {1=Weekday, 2=Saturday, 3=Sunday}. Step 4 trains a Conditional Transformer that takes one observed diary + demographics and generates synthetic schedules for the two unobserved day-types. Output: ~192,183 diary-days (64,061 × 3 strata), each carrying 48 activity tokens (14-class) + 48 AT_HOME tokens (binary) + 9 × 48 co-presence tokens (binary).

Refer to v1 (`investigation_Training_step4.md`) §0 for the full datasets / inputs / supervision / loss specification — none of it changed in J-series.

## Hard gates (verbatim across F / G / H / I / J)

`composite < 1.045 | AT_HOME RMS ≤ 5.3 pp | Spouse ≤ 5 pp | act_JS ≤ 0.05`

The composite gate had **never** been cleared by any production run before J1 (best-ever G4=1.256). J1 cleared it by 35% margin (0.6927). J3 cleared it by 39% margin (0.6355) AND closed the AT_HOME RMS gate that J1 missed.

---

## 1. Where AT_HOME and co-presence bias come from upstream

Two purposes for this section:

- (a) Explain why per-stratum AT_HOME calibration was hard for J1 / J2 / J2.5 and what data property J3's dim-balance fix actually addressed.
- (b) Establish that the Alone-channel residual on 2005/2010 cannot be solved inside Step-4 at the loss level — it requires a data-side mask in `04A_dataset_assembly.py`.

### 1.1 Step-2 harmonization grounding (`outputs_step2/step2_validation_report.html`)

The harmonization stage decides what signal the Step-4 model can possibly learn. Four sections matter:

- **Chart 6 — AT_HOME Rate per Cycle.** Per-cycle×stratum AT_HOME rate from `outputs_step4/diagnostics_v4.json` (`population.at_home_per_cycle_stratum`):

  | Cell | AT_HOME rate |
  |---|---|
  | 2005_1 / 2005_2 / 2005_3 | 0.6905 / 0.7135 / 0.7576 |
  | 2010_1 / 2010_2 / 2010_3 | 0.6994 / 0.7204 / 0.7771 |
  | 2015_1 / 2015_2 / 2015_3 | 0.7093 / 0.7407 / 0.7717 |
  | 2022_1 / 2022_2 / 2022_3 | 0.7699 / 0.7721 / 0.7982 |

  The 12-cell rate band (0.69 → 0.80) is what the Step-4 architecture has to reproduce; `RMS across strata` is the metric that scores the per-cell match. Aggregate-bias fixes (raising λ_home) shift all 12 cells together and cannot reduce variance among them.

- **Chart 9b — NaN % per Harmonized Column.** Per-cycle non-trivial NaN load on co-presence at episode level: ≈20% in 2005, 19.3% in 2010, 0.1% in 2015, 6.8% in 2022. This is the floor on what the BCE mask can recover even with a perfect model.

- **Chart 10a / 10b — Co-Presence Prevalence + Missing Rate.** Spouse and Alone are the only two channels with stable cross-cycle prevalence; `Children`, `parents`, `otherInFAMs`, `otherHHs`, `friends`, `others` are sparse, and `colleagues` is below — see 10d.

- **Chart 10d — colleagues Column Coverage per Cycle.** This is the load-bearing observation for the Alone-channel residual: `colleagues30_*` is **NaN-everywhere for cycles 2005 and 2010** because the source variable `TUI_06I` was not collected. 04A masks `colleagues=0` for those cycles and forces `cop_avail[c==2005, :, colleagues_idx] = False` so it is excluded from the BCE — but the Alone channel is *not* masked, and the supervision asymmetry leaks into the model: the BCE drives `alone=1` whenever no other companion is present, and "no colleagues collected" reads to the loss as "colleagues are absent," inflating Alone on 2005/2010 weekday work hours.

### 1.2 Step-3 merge / downsample grounding (`outputs_step3/step3_validation_report.html`)

The merge step takes the harmonized episodes and produces the per-respondent 30-min representation that 04A consumes. Sections that bear on the AT_HOME / co-presence story:

- **Section 3d — DDAY_STRATA Distribution per Cycle.** 72.8% Weekday / 13.6% Saturday / 13.6% Sunday — the imbalance flagged in v1 §0.5.H1. v1's H1 hypothesis was that Weekday over-supervision drives per-stratum variance. G1's proportional sampling (55.6 / 22.2 / 22.2 on the *target* side) addressed half of it; the source side is still imbalanced.

- **Sections 4b vs 7b — AT_HOME Rate Curve, 144 slots vs 30-min.** The morning trough at slots 0–10 in the 30-min view is the same curve at both resolutions — the 30-min downsampling preserves shape. J1's diagnostic deep-dive (`diagnostics_J_J1.json`) reported that morning slots 0–10 were over-predicted by +5 to +18.6 pp, with mean +10.77 pp. That bias is not a downsampling artefact.

- **Section 6c — Alone Rate by Hour of Day per Cycle.** Ground truth for the Alone channel that the model now matches well for 2015/2022 and over-predicts for 2005/2010 weekdays.

- **Section 8a — Co-Presence Prevalence: Episode Level vs. 30-Min Slot Level.** Confirms the episode→30-min majority-vote does not introduce a bias; the Alone residual is upstream of slot tiling.

### 1.3 Step-4 H_Tanh validation grounding (`outputs_step4/step4_validation_report.html`)

Until J3 ships, `outputs_step4/` carries the H_Tanh production checkpoint. Sections that bear on the AT_HOME / co-presence story (and on the J-series narrative):

- **Section 1 — Training Curves.** H_Tanh's loss trajectory; the calibration baseline that J-series inherits.
- **Section 3 — AT_HOME Rate Consistency / Daily Rhythm.** Where H_Tanh's residual +5.19 pp lived — the morning slot, the same place J1 over-predicted +10.77 pp before the J3 fix.
- **Section 4 — Temporal Structure / Activity Heatmap.** AR-cascade artefact pattern.
- **Section 6 — Demographic Conditioning (Work Proportion by LFTAG).** Conditioning reaches the activity head; per-stratum AT_HOME calibration breaks for *information-balance* reasons inside Arm-2, not because demographics aren't being passed in.
- **Section 7 — Cross-Stratum Consistency.** The per-cycle×stratum AT_HOME plot. H_Tanh: 5.66 pp. J1: 5.83 pp. J3: 4.57 pp ✅.

### 1.4 What this means for the J-series narrative

- AT_HOME RMS is a *per-cell* problem. Aggregate-bias fixes (J2's λ_home=0.9) cannot move it.
- The cop_max_gap on Alone is a *data-side* problem. Loss-side fixes (J2-class spouse_neg_weight or pos_weight tuning) cannot move it.
- The activity axis was already solved by J1; J3 improved it as a side effect.
- J3's load-bearing change has to be something that moves *per-stratum* AT_HOME calibration without touching the gates that already pass. The Soft Activity Embedding does exactly that: by giving the activity probs comparable representational weight to the encoder memory in the Arm-2 fusion, it lets Arm-2 condition AT_HOME on activity per-cell, not just on demographics.

---

## 2. Architecture lineage table (J-series extension to v1's table)

Append the J2 / J2.5 / J3 rows to v1 §"Architecture lineage table." Source: `Speed-Cluster_docs/CSV_records/architecture_investigation.csv`, `training_config_investigation.csv`.

| Tag | Trunk + decoder | Home/cop heads | Activity head | Single-axis delta vs predecessor |
|---|---|---|---|---|
| J1 | 6-enc + CrossAttn AR (Arm 1) + per-slot NAT fusion (Arm 2) | Tanh → Linear → Sigmoid (parallel NAT) | Linear → CE (14, AR) | new — Hybrid AR-Encoder synthesis |
| J2 | identical to J1 | identical to J1 | identical to J1 | **λ_home 0.7 → 0.90** (config-only) |
| J2.5 | identical to J1 | **Linear → GELU → Dropout(0.1) → Linear → Sigmoid** (Tanh dropped, cop head retained) | identical to J1 | home_head architecture; **λ_home 0.7 → 0.90** also |
| **J3** | identical to J1 + **`arm2_act_proj: Linear(14, d_model)`** before Arm-2 fusion concat | identical to J1 | identical to J1 | **Soft Activity Embedding (dim balance)**; λ_home 0.7 → 0.90 also |

**Single-axis-discipline note.** The J2/J2.5/J3 ladder bundled λ_home with the architecture changes despite the v1 single-axis rule. The bundling matters less than expected once gate eval landed: J2 (pure-λ) missed AT_HOME by 0.40 pp, so the upper bound on the pure-λ effect is small. The architecture effects (J2.5 home_head, J3 arm2_act_proj) dominate the spread between arms (5.70 / 6.03 / 4.57 pp). The J2 result alone shuts down the "λ was the load-bearing change" reading.

## 3. Per-stage outcomes (J-series rows, official 04J)

Source: `step4_training_v3.md` Progress Log + `CSV_records/loss_values_trainings_investigation.csv` notes column.

| Date | Tag | Composite | AT_HOME RMS pp | Spouse pp | act_JS | Gates | Verdict |
|---|---|---|---|---|---|---|---|
| 2026-05-06 | J1 | 0.6927 ✅ | 5.83 ❌ (fail by 0.53) | −1.9 ✅ | 0.0274 ✅ | 3/4 | AT_HOME sole miss; J2/J2.5/J3 triggered |
| 2026-05-07 | J2 | 0.688 ✅ | 5.70 ❌ (fail by 0.40) | −1.47 ✅ | 0.0239 ✅ | 3/4 | λ-only knob: smallest miss but still ❌ |
| 2026-05-07 | J2.5 | 0.686 ✅ | 6.03 ❌ (fail by 0.73) | −2.08 ✅ | 0.0250 ✅ | 3/4 | head depth/no-Tanh: largest miss |
| **2026-05-07** | **J3** | **0.6355 ✅** | **4.57 ✅ (margin +0.73)** | **−2.03 ✅** | **0.0191 ✅** | **4/4** | **SHIP — production Step-4 checkpoint** |

J3 is the first run in the entire F → G → H → I → J record to clear all four gates. Composite is 39% under the gate; activity is 2.6× under; AT_HOME has +0.73 pp margin; Spouse has +2.97 pp margin.

## 4. Per-stage training-time loss table (J-series)

Companion to §3. Source: `CSV_records/loss_values_trainings_investigation.csv` rows 17–20. Best epoch is the row with minimum val_score in the training CSV. These are teacher-forced per-output training-time losses; they live on a different axis than the AR-generation gate metrics (see v1's "Reading guide / cross-table" for the full discussion).

| Tag | Best ep | act_loss | home_loss | cop_loss | marg_loss | val_JS | home_gap | val_score |
|---|---|---|---|---|---|---|---|---|
| J1 | 60 | 0.1028 | 0.3596 | 0.1943 | 0.0089 | 0.0044 | 0.0256 | 0.0171 |
| J2 | 60 | 0.1031 | 0.3572 | 0.1943 | 0.0093 | 0.0035 | 0.0275 | 0.0173 |
| J2.5 | 60 | 0.1045 | 0.3595 | 0.1942 | 0.0083 | 0.0048 | 0.0258 | 0.0176 |
| **J3** | 72 | **0.0878** | **0.3514** | **0.1919** | 0.0086 | **0.0035** | **0.0263** | **0.0166** |

**Reading guide.**

- J3 has the lowest training-time `act_loss`, `home_loss`, `cop_loss`, and `val_score` of the four J arms. The dim-balance fix improved every per-output proxy, not just the AT_HOME gate — consistent with the architectural reading that the 14-d activity probs were under-weighted in the 384-d-dominated Arm-2 fusion.
- The proxy `home_gap` is in a tight 2.56–2.75 pp band across all four — proxy `home_gap` was **a poor predictor** of which arm would close the *RMS-across-strata* gate (proxy = aggregate, gate = per-cell variance). This generalizes: future arms should not rely on training-CSV `home_gap` to predict gate movement on AT_HOME.
- All four J arms saturate `home_loss` around 0.35 vs the G4 / H_Tanh label-smoothed BCE floor of 0.22. The NAT Arm-2 home_head still does not reach the AR-decoder floor; J3's improvement (0.3596 → 0.3514) is real but small. The gate movement comes from per-cell calibration, not from absolute home_loss reduction.

## 5. Why J3 won — diagnosis

The J-2 Blueprint (`investigations/J-2 Blueprint.md`) explicitly predicted this on 2026-05-05: *"The raw 14-dim probability vector was likely being 'drowned out' by the 384-dim memory vector in J1."* J3 isolated that single change (without the additional refinement layer the Blueprint also proposed) and it closed the gate. Three load-bearing observations:

1. **Per-output information balance matters more than per-output capacity.** J2.5 added head capacity (`Linear → GELU → Dropout(0.1) → Linear`) and got *worse* AT_HOME RMS (6.03 vs J1's 5.83). J3 added one Linear *upstream* of the head — in the Arm-2 fusion concat, projecting the 14-d soft activity probs to `d_model=384` — and got *better* (4.57). The bottleneck wasn't head expressiveness; it was input balance at the fusion stage.
2. **λ_home 0.7→0.9 was load-neutral on its own.** J2's RMS=5.70 vs J1's 5.83 is a 0.13 pp improvement — within run-to-run noise. λ_home alone shifts the *aggregate* prediction; it cannot reduce the *per-cell variance* that the RMS-across-strata gate measures.
3. **The act_JS gate moved too** (J3=0.0191 vs J1=0.0274 — 30% better, 2.6× the gate margin). The Soft Activity Embedding is not a single-axis intervention in the gate-metric sense; by improving Arm-2's use of activity context, it improved both the AT_HOME-conditioned-on-activity calibration *and* the activity head's own signal-to-noise. Beneficial side effect, not a confound — the projection sits between the AR Arm 1 (which generated the activity sequence under detach) and the Arm-2 fusion (which consumes it for AT_HOME + cop), so there is no gradient leakage that could explain the activity improvement as anything other than reduced fusion noise.

The J-2 Blueprint's second proposal (a non-causal refinement layer on top of the Soft Activity Embedding) is unnecessary: the dim-balance change alone closed the gate. The refinement layer remains an option for a hypothetical K-arm if the Alone residual is later traced to per-slot Arm-2 capacity, but is **out of scope** because Step-4 has shipped.

## 6. Co-presence axis — what's left after J3 ships

J3's official `cop_cal_MAE` and per-channel cop_max_gap will populate `outputs_step4_J3/diagnostics_J_J3.json` once it is pulled local from the cluster. The numbers J3 inherits structurally are well-characterized from J1's deep-dive (`diagnostics_J_J1.json`); J3's dim-balance fix did not change the data-side asymmetries, so the per-channel diagnosis below remains in force.

### 6a. Spouse — passes, do nothing

Spouse gap = −2.03 pp ✅ (gate ≤5 pp). Per-stratum cells have large swings (J1's 2015_2 = −13.2 pp, 2015_3 = −12.7 pp) that cancel at aggregate. The gate is satisfied. **Resist the temptation to retune `spouse_neg_weight`** — I1's masked-BCE bumped Spouse from −3.07 to +9.16 pp the last time we touched it.

### 6b. Alone — the +21.1 pp / +17.1 pp blow-out on 2005_1 / 2010_1

Root cause is upstream of Step-4: `colleagues30_*` is NaN-everywhere for cycles 2005 / 2010 (Step-2 §1.1, Chart 10d — `TUI_06I` was not collected). 04A's `cop_avail` mask excludes colleagues from the BCE for those cycles, but the Alone channel remains supervised. Without colleagues, the Alone BCE incorrectly drives `alone=1` more than population truth supports for 2005/2010 weekday work hours; the model fills the resulting gap with `alone=1` predictions. **This is a data-side asymmetry, not a model failure** — and it persists in J3's outputs unless `04A_dataset_assembly.py` changes.

cop_max_gap is **not a hard gate.** It is the largest per-channel residual remaining and the user's framing explicitly puts it in scope. The optional cleanup arm in §7 addresses it.

---

## 7. K-cop-A — single optional cleanup arm

Single-axis, surgical, zero risk to the four passed gates. This is the *only* arm proposed in this document — no broader K-series, no AT_HOME-targeted arms — because Step-4 has shipped J3.

- **Mechanism.** In `04A_dataset_assembly.py`, mask Alone for cycles 2005 / 2010 symmetrically with the existing colleagues mask:
  ```python
  cop_avail[CYCLE_YEAR == 2005, :, alone_idx] = False
  cop_avail[CYCLE_YEAR == 2010, :, alone_idx] = False
  ```
- **Why this works.** The Alone channel's BCE role is "everyone else is absent." Without colleagues collected, the BCE incorrectly drives `alone=1` more than population truth supports. Masking Alone where colleagues is masked makes the supervision symmetric; for 2005/2010 the model falls back to predicting Alone from demographics + activity context (which J3's Arm-2 already conditions on, post dim-balance), not from a structurally-broken supervised target.
- **Architecture delta.** None. Pure 04A-side change.
- **Risk.** Reduces effective Alone supervision from 2005/2010 cycles. Aggregate Alone calibration on 2015/2022 should be unaffected because the mask is per-cycle.
- **Expected gate movement.** None on the four hard gates (AT_HOME, Spouse, act_JS, composite all decoupled from Alone). cop_max_gap drops from ~7 pp toward ~3 pp (estimated from the 2005_1 +21.1 / 2010_1 +17.1 pp share of the total max).
- **Effort.** S — one masking line in `04A_dataset_assembly.py`, then re-run `04A → 04C → 04D → 04E → 04J` for J3 only (~17 h cluster wall time end-to-end).
- **Decision pivot.** Run K-cop-A only if (a) J3's actual Alone gap on 2005_1 / 2010_1 (once `diagnostics_J_J3.json` is local) is large enough to matter for downstream BEM evaluation, and (b) a cleaner cop artefact is wanted for the publication. Otherwise ship J3 as-is and document the Alone caveat in the BEM hand-off.

---

## 8. What's actually next

1. **Step-4 closeout.** Update production checkpoint pointer from H_Tanh to J3. `outputs_step4/` rotation: archive `outputs_step4_H_Tanh/` → `outputs_step4_archived_H_Tanh/`, copy / point `outputs_step4/` at `outputs_step4_J3/`. Confirm `outputs_step4_J3/diagnostics_J_J3.json` and the regenerated `step4_validation_report.html` are populated and pulled local. Final Progress Log row in `step4_training_v3.md`: "J3 SHIPS — 4/4 gates."
2. **Step 5 (Census Linkage) — unblocked.** The next pipeline step takes J3's 192,183-row `augmented_diaries.csv` as input.
3. **Optional K-cop-A cleanup pass (§7).** Only if needed for publication or BEM downstream signal quality. Not gating Step 5.
4. **Out of scope for the rest of the project lifetime — any further Step-4 architecture arm.** The composite gate is crushed (0.6355 ≪ 1.045). The AT_HOME margin is comfortable (+0.73 pp). The activity gate is ~2.6× under (0.0191 ≪ 0.05). Further GPU spend on Step-4 has diminishing returns.

## References

- F-series investigation: `Speed-Cluster_docs/DONE/DONE_step4_training.md`
- G-series + H-series record: `Speed-Cluster_docs/DONE/DONE_step4_training_v2.md`
- I-series + J-series record: `Speed-Cluster_docs/step4_training_v3.md`
- Investigation v1: `Speed-Cluster_docs/investigations/investigation_Training_step4.md`
- J-Series Blueprint: `Speed-Cluster_docs/investigations/J-Series Blueprint.md`
- J-2 Blueprint: `Speed-Cluster_docs/investigations/J-2 Blueprint.md`
- Architecture / config / loss CSVs: `Speed-Cluster_docs/CSV_records/{architecture,training_config,loss_values_trainings}_investigation.csv`
- Training logs: `training_logs/{F7..J3}_training_log.csv`
- J1 04J diagnostics (local): `2J_docs_occ_nTemp/diagnostics_J_J1.json`
- H_Tanh 04J diagnostics (production, soon to be superseded): `outputs_step4/diagnostics_v4.json`
- J3 04J diagnostics (production, expected): `outputs_step4_J3/diagnostics_J_J3.json` (confirm pulled local before quoting cop_max_gap numbers in any downstream artefact)
- Step-2 / Step-3 / Step-4 validation HTML: `outputs_step{2,3,4}/step{2,3,4}_validation_report.html`
- Frozen architectures: `Speed_Cluster/archive/04B_model_*.py`

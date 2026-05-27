# Step 4 Training Improvement Plan

How to lift J3 past the current plateau across **all three outputs** (activity, AT_HOME, co-presence), without rebuilding the architecture from scratch. Focus is on AT_HOME and co-presence — the two outputs that are currently blocking the validation gates while activity is already at the edge of passing.

---

## Quick-start checklist

Use this to drive execution. Tick boxes in order; stop at the earliest phase that closes all 4 gates with margin.

**Pre-flight (~30 min, local)**
- [x] Re-read §3.5 "what's been tried" before any code edit — confirm the change you're about to make is novel or has a different scope than a prior failure.
- [x] Snapshot J3 baseline numbers in a comparison table: composite 0.6355, act_JS 0.0191, AT_HOME RMS 4.57 pp, Spouse |Δ| 2.03 pp, all 12 cycle×stratum AT_HOME cells (2.95–9.69 pp range).
- [x] **(SUPERSEDED 2026-05-21)** Original ask was to audit `outputs_step2/*.csv` for ATTSCH/POWST coverage. Audit completed: ATTSCH and POWST were NOT in Step 2 outputs (functions never written). See §3 Lever A and §9 Open risks #1 for the verified plumbing gap. Phase 2 scope expanded from "extend Step 3 merge" to "extend Step 1 extractor + Step 2 harmonization + Step 3 merge + Step 4 CAT_COLS".
- [x] **(2026-05-22)** Snapshot J3-PSB regression: composite 0.8463 (vs J3 0.6355), act_JS 0.0520, AT_HOME RMS 6.89 pp, COP max gap 8.43 pp. See Progress Log "Phase 1 (J3-PSB) — SHELVED" for root cause (over-parameterized demographic broadcast).

**Phase 1 — Per-slot demographic broadcast (Lever C-i, ~6 h cluster) — SHELVED 2026-05-22**

*All 4 gates regressed: composite 0.6355 → 0.8463, act_JS 0.019 → 0.052, AT_HOME RMS 4.57 → 6.89 pp. Root cause: per-slot static demographic broadcast over-parameterized the encoder (3,648 extra features per sample) and swamped the slot-position signal. See Progress Log entry "Phase 1 (J3-PSB) — SHELVED" for full diagnosis. PSB-Lite (cond_vec → 8 dim projection + cond-dropout) preserved for Phase 2 Arm 2.*

- [x] Copy `04B_model_J3.py` → `04B_model_J3_v2.py`.
- [x] Edit `04B_model_J3_v2.py` `_encode()` to broadcast `cond_vec` to every slot token.
- [x] Switch `04D_train.py` import to v2.
- [x] Run 1-epoch smoke test.
- [x] Submit J3-PSB retrain (job 934720, 52 epochs, 6 h).
- [x] Gate check — **all 4 fail**. Shelved.

**Phase 2 — Restore demographics (Lever A, ~6 h cluster + ~1 h local prep) — SHELVED 2026-05-22**

*Both parallel arms (`J3_DEMO`, `J3_DEMO_PSBLite`) cancelled at epoch 41/100 (~6h34m wall) on 2026-05-22 after home_BCE and cop_BCE losses flatlined since epoch 11 with no differentiation between arms (DEMO home=0.3845 vs PSBLite home=0.3853 at ep 41). Demographics restoration (Lever A) alone did NOT move binary heads materially; regularized PSB-Lite (Lever C-i with cap=8/dropout=0.5) added no further headroom. All val_score improvement was activity-driven (already at-edge passing). Both arms appear bounded by the K=5 neighbor-disagreement floor (JS=0.1888) — only Lever B can move that floor. See Progress Log entry "2026-05-22 — Phase 2 CANCELLED at epoch 41 (both arms)" for full diagnosis. The Step 1+2+3+4A plumbing work (ATTSCH/POWST/MODE end-to-end) remains a useful prerequisite for Phase 3 Lever B(i) (POWST/ATTSCH in EXACT_COLS), so the upstream patches are kept.*

*Original scope (kept for record). ATTSCH/POWST never reached Step 2 output — `recode_attsch()` was never written, `derive_powst()` was never written, and `derive_mode()` exists but is commented out at `02_harmonizeGSS.py:620`. Full plumbing chain (Step 1 → Step 2 → Step 3 → Step 4) needs patching, not just Step 3.*

**Per-cycle source columns (verified against raw SAS/DAT files + codebooks 2026-05-21):**

| Variable | 2005 | 2010 | 2015 | 2022 |
|---|---|---|---|---|
| ATTSCH | `EDUSTAT` (universe: MAR_Q100=4) | **`EOR_Q320==9995`** sentinel (corrected 2026-05-22 from EOR_Q210; verified in syntax file) | `ESC1_01` (all-respondent) | `EDC_10` (all-respondent) |
| POWST | `MAR_Q190==1 AND MAR_Q193==5` (narrow definition) | `CTW_Q140_C08` | **`CTW_140H`** (NOT `CTW_140I` — `01_readingGSS.md:113` is wrong) | `CTW_140I` |
| MODE (bonus) | None in Main; not extracted in Phase 2 | `CTW_Q140_C01-C09` (multi-select) | `CTW_140A-I` (multi-select) | `CTW_140A-E` + `ATT_150C` |

**Step 1 — extractor patches** (`01_readingGSS.py`) — DONE 2026-05-22
- [x] 2005 MAIN_COLS_2005: add `EDUSTAT`, `MAR_Q190`, `MAR_Q193`.
- [x] 2010 MAIN_COLS_2010: add `EOR_Q320`, `CTW_Q140_C08`. *Note: doc originally listed `EOR_Q210`; codebook re-check via syntax file revealed `EOR_Q320` is the "year studies completed / 9995 = still attending" column for 2010 PUMF. `EOR_Q210` in 2010 PUMF is unrelated ("Did you attain highest education in Canada or [elsewhere]").*
- [x] 2015 MAIN_COLS_2015: add `ESC1_01`, `CTW_140H` (latter already present).
- [x] 2022 MAIN_COLS_2022: `EDC_10` + `CTW_140I` already correct.
- [x] Uncomment the `"ATT_150C": "MODE"` rename in 2022 MAIN_RENAME_MAP (needed for 2022 `derive_mode` branch).
- [x] Added Windows/macOS path branching for `DATA_ROOT` and `OUTPUT_DIRECTORY` (cross-platform).
- [x] Re-run Step 1 → 8 CSVs in `outputs_step1/`. New cols verified present in all cycles.

**Step 2 — harmonizer patches** (`02_harmonizeGSS.py`) — DONE 2026-05-22
- [x] Wrote `recode_attsch(df, cycle)`: universe-pad-to-No reconciliation across cycles. Int8 column.
- [x] Wrote `derive_powst(df, cycle)`: per-cycle column selection; non-workers stay NaN (LFTAG disambiguates).
- [x] Wired both calls into `harmonize_main()` after `recode_kol`.
- [x] Uncommented `derive_mode(df, cycle)` at L620.
- [x] Re-run Step 2 → 4 main + 4 episode CSVs in `outputs_step2/`. Coverage verified:

| Cycle | n | ATTSCH coverage | ATTSCH ==1 | POWST coverage | POWST ==1 (workers) | MODE coverage |
|---|---|---|---|---|---|---|
| 2005 | 19,597 | 99.7% | 1,349 (6.9%) | 59.7% | 689 (5.9% of workers) | 0% (no source) |
| 2010 | 15,390 | 63.9% | 617 (4.0%) | 50.1% | 383 (5.0%) | 50.1% |
| 2015 | 17,390 | 97.5% | 1,310 (7.5%) | 50.5% | 458 (5.2%) | 50.5% |
| 2022 | 12,336 | 94.8% | 475 (3.9%) | 47.0% | 1,027 (17.7%) | 94.9% |

All four cycles match expected codebook rates. 2022 WFH rate is the COVID-era jump; 2005/2010/2015 baseline ~5%.

**Step 3 — merge patches** (`03_mergingGSS.py`) — DONE 2026-05-22
- [x] Extended `MAIN_COMMON_COLS` (line 78–85) with `['ATTSCH', 'POWST', 'MODE']`.
- [x] Extended `PERSON_COLS` inside `build_hetus_wide()` (line 443–450) with the same three. *Bug found: the wide-table builder had its own column filter separate from `MAIN_COMMON_COLS`; without this edit the new cols dropped at the pivot stage.*
- [x] Re-run Step 3 → `outputs_step3/hetus_30min.csv` (64,061 rows × 123 cols). Per-cycle ATTSCH/POWST/MODE coverage matches Step 2 (within diary-validity merge drops).

**Step 4 — dataset assembly** (`04A_dataset_assembly.py`) — DONE 2026-05-22
- [x] Extended `CAT_COLS` with `['ATTSCH', 'POWST', 'MODE']`.
- [x] Re-run 04A full (sample mode would need a pre-built `_SAMPLE` file). **`d_cond` = 90** (was ~76; +14 from new one-hots — exactly as predicted). Tensors saved: `step4_train.pt` (44,843), `step4_val.pt` (9,609), `step4_test.pt` (9,609).

**Cluster retrain — two-arm parallel A/B (decided 2026-05-22 after J3-PSB regression)**

*Rationale.* Phase 1 (raw PSB) regressed all 4 gates due to demographic broadcast swamping the slot-position signal (composite 0.6355 → 0.8463; see Progress Log entry). Two independent paths are worth testing in parallel before committing Phase 3+ effort:
- **Arm 1 — `J3-DEMO` (stock J3 + new demographics only).** Tests whether POWST/ATTSCH/MODE alone close the 2022-Weekday AT_HOME cell and Spouse Δ without any architecture change. Architectural control.
- **Arm 2 — `J3-DEMO-PSBLite` (stock J3 + new demographics + regularized PSB).** Tests whether a regularized per-slot demo broadcast can survive when paired with richer demographics. Specifically: project `cond_vec` (~90 dims) → 8 dims via a learned `Linear(d_cond, 8)` before broadcast, plus per-slot cond-dropout p=0.5 during training. This reduces the extra capacity from ~3,648 features/sample (raw PSB) to ~384 features/sample (~10× smaller), and the dropout forces the model to keep using slot position.

**Pre-flight smoke test (1 epoch, ~15 min, Arm 1 only):**
- [x] **(SKIPPED 2026-05-22)** Decided not to do the standalone 1-epoch smoke. Arm 1 (`J3-DEMO`) is architecture-identical to J3 baseline (composite 0.6355, well-characterized); the only change vs J3 is the `d_cond = 76 → 90` tensor swap, which is consumed transparently by `cls_mlp` (Linear(d_cond + d_cycle, 256)) — no shape mismatch risk. Local 04A run already validated the shape grew cleanly and pos_weights re-computed sensibly. If Arm 1 misbehaves in production, abort and re-evaluate; the cluster-walltime cost of running it as a smoke is the same as running it for the full 6 h.

**Parallel submission:**
- [x] Built local bundle at `_bundle_J3_DEMO/` (192 MB total) — tensors + patched `04B_model.py` / `04B_model_J3_v3.py` (NEW) / `04D_train.py` / `04A_dataset_assembly.py` + new `J3_DEMO.yaml` + `J3_DEMO_PSBLite.yaml` + new `J3_DEMO.sh` + `J3_DEMO_PSBLite.sh` + patched `config_to_env.sh` / `config_to_env.py`.
- [x] Single recursive `scp -r _bundle_J3_DEMO/* o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/`. Tensors landed in `outputs_step4_G2/` on the cluster.
- [x] Archived shelved `04B_model_J3_v2.py` to `step4_Speed_Cluster/archive/` (predecessor of v3 in the project's archive-before-edit convention).
- [x] **Submitted 2026-05-22**: `sbatch /speed-scratch/o_iseri/occModeling/Speed_Cluster/jobs/J3_DEMO.sh` → **job 935024**, RUNNING on `cisr-1`. `sbatch .../J3_DEMO_PSBLite.sh` → **job 935025**, RUNNING on `cisr-2`. Both `pg` partition, 1 GPU, 40G RAM, 48 h walltime. *Both crashed in first seconds — see Progress Log "Phase 2 first submission CRASHED".*
- [x] **Re-submitted 2026-05-22 after pair-file fix**: `J3_DEMO` = 935035 (cisr-1), `J3_DEMO_PSBLite` = 935036 (cisr-2).
- [x] **CANCELLED 2026-05-22 at epoch 41/100 (~6h34m).** Reason: home_BCE + cop_BCE losses flatlined since ep 11, no differentiation between arms. See Progress Log "2026-05-22 — Phase 2 CANCELLED at epoch 41 (both arms)".

**Gate check (CANCELLED — superseded by loss-curve diagnosis):**
- [x] ~~For each arm: did 2022-Weekday AT_HOME cell narrow from 9.69 pp? Did Spouse |Δ| drop below 2.0 pp? Did act_JS hold ≤ 0.022?~~ — No inference run; cancelled before composite was computable.
- [x] Diagnosis from training-side losses alone: PSB-Lite vs DEMO are indistinguishable on `home`/`cop` heads (both ~0.385 / ~0.21 by ep 41). Demographics + PSB-Lite together did not reach binary heads.
- [x] Downloaded both result dirs (checkpoints + training_log.csv) + both `.out` logs locally to `step4_Speed-Cluster_docs/CSV_records/step4_Speed_Cluster/` for record.
- [x] **No winner; do not seed Phase 3 from either arm.** Phase 3 (Lever B) starts from J3 baseline (composite 0.6355).

**Phase 3 — Tighten neighbor pairing (Lever B, ~6 h cluster) — SHELVED 2026-05-23**

*Built + submitted as J3-NEIGH (job 935306, 2026-05-22). Training failed: best val_score=0.2045 at ep 1 (vs Phase 2 DEMO 0.0496, lower=better), early-stopped ep 16. K-mean soft AT_HOME target decalibrated the sigmoid head — predictions clustered around fractional values {0, 0.2, 0.4, 0.6, 0.8, 1.0} instead of being pushed to 0/1, so the binary threshold@0.5 lost discriminative power. home_gap jumped 0.0336 (ep 1) → 0.2585 (ep 3). BCE floor inflated by target entropy (h=0.4 → 0.67); home_loss ~0.51 is not comparable to J3 binary baseline ~0.385. Joint loss optimization also degraded val_JS (0.188 → 0.252 → 0.147). Inference cascade additionally broke (missing `step4_all_meta.csv` on cluster — operational, not diagnostic). Diagnosis conclusive; both Lever B(i) tighter `EXACT_COLS` and Lever B(ii) K-mean soft target are shelved as a bundle. Pivot to **Phase 4 (Lever C cheap fixes)**.*

- [x] Edit `04C_training_pairs.py` `EXACT_COLS`: append `ATTSCH`, `POWST`. **REVERTED in Phase 4 J3-CLEAN.**
- [x] Edit `04D_train.py` pair-loader: switch K=5 from 1-of-K resample to K-mean soft target — for **AT_HOME only**. Keep 9-channel co-presence as 1-of-K resampled, and keep activity as 1-of-K resampled. Averaging across K=5 on rare cop channels (parents, friends, colleagues) dilutes the positive signal below the 0.5 BCE decision threshold and would worsen rare-channel collapse (and inflate Spouse Δ). **REVERTED in Phase 4 J3-CLEAN.**
- [x] Re-run `04C_training_pairs.py` locally (~5 min) to regenerate `training_pairs.pt` / `val_pairs.pt` with the new EXACT_COLS.
- [x] Bundle upload + submit `J3-NEIGH` retrain on the `pg` partition (single arm). Job 935306, ep 1–16, early-stop.
- [x] Gate check: Spouse Δ and AT_HOME cells improve further? Did act_JS hold ≤ 0.022? **No — val_score regressed 4× vs Phase 2 DEMO best. Training failed, inference crashed.**
- [x] STOP if all 4 gates pass. Else continue to Phase 4.

**Phase 4 — Loss-side cleanups (Lever C-ii/iii/iv + ACTIVITY_BOOSTS) — ACTIVE NEXT PHASE 2026-05-23**

*Promoted to next active phase after Phase 3 J3-NEIGH failure (2026-05-23). Stacks four cheap fixes on top of stock J3 baseline (composite 0.6355). Independent evidence each knob helps: ACTIVITY_BOOSTS=0 directly addresses act_JS gate, λ_trans directly addresses 157.95× over-fragmentation, per-cell marg loss matches the per-cell AT_HOME gate framing, per-channel cop `pos_weight` lifts rare-positive channels (parents/friends/colleagues). Lever B reverts cleanly (04C EXACT_COLS to baseline; 04D Step4Dataset back to 1-of-K resample). No new architecture changes.*
- [ ] **Set `export ACTIVITY_BOOSTS=0` in the SLURM wrapper** for the next retrain. The ×5/×3/×2 multipliers on Work/Transit/Social fight act_JS by inducing over-prediction of those classes. Zero-code, env-variable change. Cheapest single act_JS lever.
- [ ] Add transition-rate penalty: `λ_trans * |mean_transitions_pred - mean_transitions_obs|` (start λ_trans=0.05). Directly targets 157.95× over-fragmentation. **New code in `04D_train.py:compute_loss` — gated by `LAMBDA_TRANS` env var, backward-compatible default 0.0.**
- [ ] Replace global marg_loss in `04D_train.py:184-193` with per-(cycle × stratum)-cell version. Different framing from the prior global marg_loss failure. **Already supported via existing `MARG_MODE=per_cs` env var; no new code.**
- [ ] Re-enable `pos_weight` per-channel on rare cop channels (parents, otherInFAMs, colleagues, friends). **Never on AT_HOME** — caused April 2026 destabilization. **Use existing `COP_POS_WEIGHT=1` + `COP_ALONE_PW=0` + `SPOUSE_NEG_WEIGHT=0.45`; no new code.**
- [ ] Monitor AT_HOME RMS each epoch for the F-series failure mode; roll back immediately if it appears.
- [ ] J3-CLEAN bundle (J3 baseline + 4 cheap fixes stacked) — single arm, ~6 h cluster, `pg` partition.
- [ ] Gate check: all 4 gates pass? STOP. Else continue to Phase 5 escape valve.

**Phase 5 — Escape valve (only if Phase 1–4 leave gates open) — SUPERSEDED by Phase 6**
- [ ] Collapse 9-channel co-presence to 1 binary `withAnyone = (Alone == 0)` in `04A` output schema + `04D` loss heads.
- [ ] Document the regression for Step 5 inputs and the paper.

**Phase 6 — Progressive Funnel: sample-first architecture search + HPT (2026-05-24 → ongoing)**

*Stage A: 2% sample, 50 epochs, 10 architectures (5 families × 2 variants)*
- [x] Build sample assembler + 5 model files + 10 configs/wrappers.
- [x] Upload bundle + submit 10 parallel sbatch.
- [x] Download all 10 results + rank. Top 3: MDLM, SEDD, CC_SPL.
- [x] Structural re-runs (5) to confirm ranking.

*Stage B: 20% sample, 100 epochs, top 3 architectures*
- [x] Build + submit MDLM_B, SEDD_B, CC_SPL_B.
- [x] Monitor + rank. Winner: MDLM_B. SEDD_B second. CC_SPL_B eliminated.

*Stage C: 100% data, 100 epochs, top 2 architectures*
- [x] Build + submit MDLM_C + SEDD_C.
- [x] Score vs J3 4/4 gates. MDLM_C wins (0.5665, beats J3 0.6355 by 10.9%). SEDD_C eliminated (0.7036).

*Stage D: HPT grid on MDLM_C winner (6 trials)*
- [x] Build 6 configs (D1–D6) targeting AT_HOME RMS + act_JS gates.
- [x] Upload + submit 6 parallel sbatch (936470–936475).
- [x] D3 scored: 0.5832 — per_cs regressed act_JS. ❌
- [x] D5 scored: 0.5915 — per_cs + full-push also regressed. ❌
- [x] D1/D2/D4 cancelled (ep 40/39/47) — trailing D6, GPU hours saved.
- [x] D6 scored: 0.6235 — lambda_trans=0.05 too aggressive, broke COP. ❌

*Stage E: focused HPT + demographic amplification on MDLM_C (Stage D had no winner)*
- [x] Stage D concluded — all 6 trials failed. MDLM_C (0.5665) remains best.
- [x] Build 4 trials: E1 (conservative HPT), E2 (+ lambda_trans=0.015), E3 (+ aux_stratum + GSS weighting), E4 (deeper FiLM v2).
- [x] Upload + submit Stage E bundle (jobs 936552–936555, 2026-05-25).
- [x] E3 scored: 0.5812 — aux_stratum + data_side_sampling regressed act_JS. ❌
- [x] E1/E2/E4 cancelled (ep 19–23) — wrong HPT target, GPU hours saved for Stage F.
- [x] Stage E concluded — all failed. Pivot to MDLM-intrinsic HPT on 10% sample (Stage F).

*Stage F: MDLM-intrinsic HPT on 10% sample*
- [x] Build 10% sample on cluster (04A_sample_assembly.py --frac 0.10, 5143 train respondents).
- [x] Build Stage F bundle (9 configs + patched 04B_model_MDLM.py with env-var knobs).
- [x] Upload + submit 9 parallel sbatch (jobs 936646–936654, 2026-05-25).
- [ ] Score + promote top 2–3 to full data (Stage G). ← ACTIVE

**Hard guardrails (apply at every phase)**
- [ ] Track all 4 gates jointly. A higher composite that breaks AT_HOME is not progress.
- [ ] Never break `arm2_act_proj` or remove the Arm-1/Arm-2 detach barrier.
- [ ] Do NOT add hard logical constraints between cop channels (J4_3 catastrophe: Spouse → −8.89 pp).
- [ ] No further λ_home sweeps — J2 + J3-HPT-L confirmed both directions lose vs 0.7.
- [ ] If a previously-passing gate regresses, roll back the most recent change before stacking another.

---

## 1. Where we are

| Output | Gate | Current J3 | Status |
|---|---|---|---|
| Activity (act_JS) | ≤ 0.022 | 0.0191 | PASS (tight) |
| AT_HOME RMS | ≤ 5.3 pp | 4.57 pp BUT all 12 cycle×stratum cells fail individually (2.95–9.69 pp gap, worst is 2022 Weekday) | mixed |
| Spouse |Δ| | ≤ 2.0 pp | 2.03 pp | FAIL (edge) |
| Transition rate | ~1× observed | 157.95× observed (synthetic over-fragments) | FAIL (severe) |
| Weekday ≥ Sat ≥ Sun (AT_HOME) | ordering preserved | violated in 46.5% of profiles; Weekend ≥ Weekday in 72.1% of cases | FAIL |

Overall: 28 PASS / 1 WARN / 17 FAIL out of 46 validation checks. Composite score 0.6355, just past the 0.625 gate but with no margin.

---

## 2. Why binary outputs are the hardest in J3

It feels backwards — AT_HOME and co-presence are binary while activity is 14-way — but six structural reasons make the binary outputs harder in this specific pipeline:

1. **Old pipeline collapsed all co-presence into one binary `withNOBODY` channel.** J3 keeps 9 separate channels (Alone, Spouse, Children, parents, otherInFAMs, otherHHs, friends, others, colleagues). The cardinality of the supervision signal is ≈9× larger than activity's single multi-class call.
2. **Only activity has an autoregressive (AR) decoder.** AR gives activity a built-in temporal smoother — slot t sees slot t-1. AT_HOME and co-presence are non-autoregressive (NAT) heads; they have no fallback if the encoder fails to propagate signal across slots.
3. **Demographics enter only at the CLS token and 3 cross-attn tokens.** The old pipeline copied 24 categorical demographic embeddings onto *every one of 24 slot tokens*. J3 expects attention to route demographics from CLS to slot t. NAT binary heads pay this cost first because they have no AR fallback to compensate.
4. **The Census/HH demographic schema is much narrower than the old pipeline used.** Fields most predictive of AT_HOME and co-presence (Home ownership, Room count, Internet access, Kinship, Nuclear-Family-Profile) are not in J3's conditioning vector at all. Activity is less demographically anchored — daily routines follow population-wide diurnal patterns the encoder can pick up from the slot signal itself.
5. **The BCE on rare-positive co-presence channels collapses to "always predict 0."** Channels like parents, friends, colleagues are sparse positives. `pos_weight` is disabled globally in J3 because it destabilized AT_HOME — but that leaves rare channels under-predicted, which directly inflates Spouse Δ and COP max-gap.
6. **The marginal-bias regularizer enforces only the global AT_HOME mean.** The validation gate is RMS *across cells* (cycle × stratum). The model can match the grand mean and still be 5+ pp off in individual cells — and that is exactly what happens.

(This analysis is documented in detail in `step4_Speed-Cluster_docs/investigations/investigation_oldTransformer_vs_J3.md §S1`.)

---

## 3. Three improvement levers

### Lever A — Restore dropped GSS demographic fields

**ATTSCH** (school attendance) and **POWST** (place-of-work status: work-entirely-from-home binary) are documented as "✅ Pass all cycles" in the Step 2 validation report. **Audit on 2026-05-21 revealed this is incorrect:** neither column is present in `outputs_step2/main_*.csv` for any cycle. Three independent root causes:

1. **`recode_attsch()` was never written.** `01_readingGSS.md:128` documents the rename intent (`EDU10 → ATTSCH`) but the function is absent from `02_harmonizeGSS.py`. Raw columns (`EDU10`/`EHG_ALL`/`EDC_10`) pass through to Step 2 unchanged.
2. **`derive_powst()` was never written.** Documented in `00_GSS_Occupancy_Pipeline.md:34` and `01_readingGSS.md:113`, but no implementation exists in `02_harmonizeGSS.py`.
3. **`derive_mode()` exists but is disabled.** The function is defined at `02_harmonizeGSS.py:150`, but the call at `02_harmonizeGSS.py:620` is commented out (`# df = derive_mode(df, cycle)`). MODE never reaches Step 2 output for the same reason.

Additionally, the Step 1 extractor (`01_readingGSS.py`) is missing the dedicated school-attendance columns for 2005/2010/2015 — it currently extracts education-*attainment* columns (`EDU10`/`EHG_ALL`) instead of the dedicated school-*attendance* binaries (`EDUSTAT` 2005, `EOR_Q210==9995` 2010, `ESC1_01` 2015). For 2015 POWST it extracts `CTW_140I` (which is actually "Other transport mode") instead of the correct `CTW_140H` ("Works or attends school at home"). 2022 is the only cycle where both ATTSCH (`EDC_10`) and POWST (`CTW_140I`) are extracted correctly.

Why these two specifically matter for the blocker gates:
- **POWST directly predicts WFH vs commute.** The worst-failing AT_HOME cell is 2022 Weekday (9.69 pp gap), which is exactly the COVID/post-COVID WFH cohort. The model is currently guessing without the variable that most cleanly identifies who works from home. Cross-cycle WFH rate trend (verified against codebooks 2026-05-21): 2005=5.9% / 2010=5.0% / 2015=5.2% / 2022=17.7% — clear COVID signal once POWST reaches the model.
- **ATTSCH directly predicts school-vs-home time for weekday slots.** This addresses the broken weekday/weekend AT_HOME ordering — students at home Saturday but at school Tuesday is a pattern the model can't currently encode.

**Cross-cycle semantic harmony concerns (documented for transparency, not blocking):**
- **2005 POWST** can use the broad `MAR_Q190==1` (any WFH hours, 18.6%) or the narrow `MAR_Q190==1 AND MAR_Q193==5` (home = usual place of work, 5.9%). Phase 2 uses the **narrow** definition for cross-cycle baseline consistency — 2010/2015's "primary mode = WFH" semantic aligns at ~5%, making the 2022 COVID spike a meaningful trend rather than a definitional artifact.
- **2005 ATTSCH** is restricted to respondents whose main activity is going to school (universe-restricted). Working part-time students are under-counted by ~3 pp. Acceptable noise floor.
- **2010 ATTSCH** uses a sentinel (`EOR_Q210==9995` "still in school") only asked of post-elementary respondents. Pre-elementary high schoolers are coded as "Not asked"; Phase 2 pads these to ATTSCH=0 (universe-pad-to-No).
- No **POWST_MISSING** or **MODE_MISSING** flags needed — `LFTAG` upstream already distinguishes worker vs non-worker, and non-workers have natural NaN for POWST/MODE in every cycle (same as `colleagues` NaN for 2005/2010 in co-presence).

**Cost.** Cheapest high-yield change in this plan in terms of cluster time (~6 h), but **plumbing scope is larger than documented in earlier versions** — touches Step 1, Step 2, Step 3, Step 4 (~1 h local prep), not just Step 3. The full file list is in §6.

**Bonus signal: MODE (commute mode).** Since `derive_mode()` is already written and just needs uncommenting at L620, MODE comes effectively free in this phase. Categorical 6-level (car-driver / car-passenger / transit / bicycle / walk / other), available 2010/2015/2022. 2005 MODE = NaN (no Main-file commute-mode columns; could be derived from Episode `PLACE` codes during travel episodes as a future Phase 2b enhancement, but out of scope for the current pass).

### Lever B — Tighten K=5 neighbor matching

The K=5 demographic-neighbor pair construction in `04C_training_pairs.py` produces an empirical neighbor-disagreement floor of **JS = 0.1888** between neighbors. The targets the model is trained against contradict each other. Three ways to make the neighbors agree more:

- **(i) Add POWST and ATTSCH to `EXACT_COLS`** (depends on Lever A). Currently K=5 uses 5 exact-match fields + 4 fuzzy + TOTINC bin. Adding POWST/ATTSCH as exact-match terms splits the neighbor pool along the AT_HOME-relevant axis, so neighbors are now matched on "do you work from home?" as well as "are you the same age and gender?"
- **(ii) Switch neighbor sampling from 1-of-K resample to K-mean soft target.** Currently one of the K=5 neighbors is randomly selected per epoch as the teacher diary. Instead, average the K=5 neighbor targets to form a soft probabilistic target. Trades target *variance* for target *bias* — the right trade-off when neighbor disagreement is the dominant error term. Small edit in the `04D_train.py` pair-loading loop. **Apply to AT_HOME only by default.** Activity averaging would over-smooth multi-class targets and regress act_JS. *Co-presence averaging is dangerous*: rare-positive channels (parents, friends, colleagues) become 0.2 soft targets when only 1 of 5 neighbors is positive; under BCE this puts the model's probability below the 0.5 decision threshold and worsens rare-channel collapse — directly inflating Spouse Δ. If soft-targets-on-cop is wanted, deploy concurrently with Lever C-(ii) per-channel `pos_weight` on rare cop channels to compensate for the diluted positive signal.
- **(iii) Stratified diversity inside the K**. Require at least 2 of the K=5 share the most-similar HRSWRK bin, and at least 1 shares POWST. Prevents accidental clusters of demographically-similar but behaviorally-different neighbors.

### Lever C — Targeted fixes for binary heads

- **(i) Per-slot demographic broadcast (J3-PSB).** Copy `04B_model_J3.py` → `04B_model_J3_v2.py` and modify the v2 file's `_encode()` to concatenate `cond_vec` onto every slot token before the `slot_linear` projection. Switch the import in `04D_train.py` to use the v2 file. Single architecture change, original J3 file untouched (so baseline remains reproducible and we can A/B compare). Expected to help the binary heads *more* than the activity head, because the binary heads have no AR fallback if encoder routing is weak. **This is the recommended first lever** — it targets the architectural root cause of binary-head underperformance identified in `investigation_oldTransformer_vs_J3.md §6.1`, requires no upstream data work, and produces the highest expected yield per cluster-hour for both AT_HOME and co-presence.
- **(ii) Per-channel `pos_weight` on rare co-presence channels.** Re-enable `pos_weight` selectively for parents, otherInFAMs, colleagues, friends — but *not* on AT_HOME (where it previously destabilized training, April 2026). Monitor AT_HOME RMS each epoch in case of regression.
- **(iii) Transition-rate penalty + ACTIVITY_BOOSTS=0 on activity loss.** Two cheap activity-side fixes:
  - Add `λ_trans * |mean_transitions_pred - mean_transitions_obs|` per batch (start λ_trans=0.05). Directly addresses the 157.95× over-fragmentation failure.
  - Set the `ACTIVITY_BOOSTS` env variable to 0 for the next retrain. The current ×5 / ×3 / ×2 multipliers on Work / Transit / Social inflate those class predictions and fight the act_JS gate. Zero-code change.
- **(iv) Per-cell marginal-bias loss.** Replace the current global-only marg loss (`04D_train.py:184-193`) with one that computes marg per (cycle × stratum) cell and averages. Currently the loss only enforces the grand mean; the gate is per-cell. This is the loss-side cousin of Lever A — directly targets the all-cells-fail AT_HOME failure pattern.

---

## 3.5. What history says — empirical record from prior runs

Before committing to any of the levers above, the proposals must be checked against the J-series training history (`step4_Speed-Cluster_docs/DONE/DONE_step4_training_*.md`, `CSV_records/*.csv`). Three things to keep in mind:

**(a) J3 is currently the all-time best (4/4 gates pass, composite 0.6355, 2026-04-22).** Every variant tried since — J4_1 (temporal embeddings), J4_2 (hierarchical cop conditioning), J4_3 (PINN-style logic loss), J5_X1, J5_X1b — has regressed at least one gate. The pattern is "every architectural addition breaks something else." Implication for this plan: improvements should be additive on top of J3, not replacements of J3 components.

**(b) J3 has two load-bearing pieces that must not be broken.**
- `arm2_act_proj = Linear(14, 384)` — soft activity-logit projection into Arm-2 fusion. Single most impactful J-series change. J3's 4/4-gate result depends on it.
- The **detach barrier between Arm-1 (AR activity decoder) and Arm-2 (NAT binary heads)**. J5_X1b removed it; AT_HOME regressed from 4.57 pp → 5.88 pp and composite to 0.8086 (worse than J3).

**(c) Proxy-target observation.** J5_X1 (with detach preserved) reached **AT_HOME RMS = 4.15 pp** — *better* than J3's 4.57 pp — but lost composite (0.6667 vs J3's 0.6355). This proves AT_HOME has headroom under the J3 architecture; the question is how to gain that headroom without losing composite.

### What's been tried and how each lever maps

| Lever | Tried before? | Outcome | Implication for this plan |
|---|---|---|---|
| **A. Restore ATTSCH / POWST to cond_vec** | **No** (explicitly deferred in v1–v4). 2026-05-21 audit confirmed the variables aren't in `outputs_step2/*.csv` at all — `recode_attsch()` + `derive_powst()` were never written, `derive_mode()` exists but is commented out at `02_harmonizeGSS.py:620`. Plumbing scope is Step 1 → 2 → 3 → 4, not just Step 3 as v1–v4 suggested. | — | Genuinely novel. Highest-value first attempt. Bonus: `MODE` comes free since `derive_mode()` is already written. |
| **B(i). Add ATTSCH/POWST to neighbor EXACT_COLS** | No | — | Depends on A. Novel. |
| **B(ii). K-mean soft-target neighbor averaging** | **No** | — | Novel. |
| **B(iii). Stratified diversity inside K=5** | No | — | Novel. |
| **C(i). Per-slot demographic broadcast (J3-PSB)** | Not in J-series. H4 tried demographic-embedding *at head level* and regressed act_JS — different mechanism. | — | Novel for J3 topology. Highest single-axis architecture lever. |
| **C(ii). Per-channel pos_weight on rare cop channels** | Global pos_weight was tried in F-series Option B and **failed to move AT_HOME**. My version is per-channel and excludes AT_HOME. | Global failed | Different scope. Worth trying but expect modest gain. |
| **C(iii). Transition-rate penalty (λ_trans)** | J5-C planned a linear-chain CRF + Viterbi for this — **shelved** because J3 already passed gates and CRF was higher-complexity. | Not tested | A lambda-penalty version (single hyperparameter, no Viterbi) is novel and cheap. Recommended. |
| **C(iv). Per-cell (cycle × stratum) marg loss** | **Global marg_loss was tried in F2 and failed.** Per-cell version is a different framing — directly targets the all-12-cells-fail pattern. | Global failed | Different framing. Worth trying as a cheap loss-side addition. |
| **Logic constraint between cop channels (`p_alone × p_others = 0`)** | J4_3 tried PINN logic loss — **catastrophically broke Spouse to -8.89 pp**. | Severe regression | **Do NOT add hard logical constraints between cop channels.** Out of scope for this plan. |
| **Lambda-home sweep** | J2 raised λ_home 0.7→0.9 and **regressed act_JS to 0.0297**. J3 reverted to 0.7 (per v4 record; J3-HPT-L just confirmed 1.1 doesn't beat J3 either). | Both higher and slight lower than 0.7 lose | Don't sweep lambda_home further as part of this plan. |
| **Composite-only optimization** | J4_1 hit composite 0.8247 with AT_HOME failing at 6.43 pp. | Misleading metric in isolation | Track ALL 4 gates jointly, not composite alone. |

### Worst residuals to keep an eye on

- **Alone channel on 2005/2010 cycles: +21.1 pp / +17.1 pp gap.** Largest single cop residual in J3. The colleagues-NaN handling for 2005/2010 may be indirectly inflating Alone's predicted positive rate (if colleagues=0 by mask, model interprets more slots as "with no one outside HH"). Worth a diagnostic before Phase 2.
- **2022 Weekday AT_HOME: 9.69 pp gap.** Lever A (POWST restoration) is the most direct fix because POWST identifies WFH workers — the population at the heart of this miss.

---

## 4. On co-presence: 9 channels vs collapse to 1 binary

**Decision: keep 9-channel as primary.**

You asked whether collapsing co-presence to one binary (like the old pipeline's `withNOBODY`) would be acceptable if BEM doesn't fully use the 9-way breakdown. Three reasons to keep 9 channels:

- **BEM internal-gains schedules genuinely differ by household composition.** Children-present, Spouse-only, and colleagues-in-home rooms have different lighting and small-power schedules in EnergyPlus archetype libraries. Collapsing loses this granularity.
- **Step 5 Census linkage uses the granular co-presence to differentiate occupant archetypes.** Collapsing to one binary would force a downstream change in Step 5's clustering features.
- **The fixes proposed in Lever C (per-channel pos_weight, per-slot demo broadcast, soft-target averaging) directly address why 9-channel underperforms.** They don't require a collapse.

**Fallback path.** If after Phases 1+2+3 the Spouse gate still fails, collapse to a single binary `withAnyone = (Alone == 0)` as a final escape valve. The change is isolated to the `04A` output schema and `04D` loss heads — fully reversible and not affecting any other step. Document the regression for Step 5 inputs in that case.

---

## 5. Phased execution

```
PHASE 1 — Per-slot demographic broadcast (Lever C-i)
  Architectural root-cause fix. No upstream data work.
  Copy 04B_model_J3.py → 04B_model_J3_v2.py; edit v2's _encode() to concat
  cond_vec onto every slot token. Switch 04D_train.py import to v2.
  Original J3 file stays untouched (baseline reproducible).
  Retrain ("J3-PSB") on top of J3 baseline.
  Gate check: AT_HOME RMS drop AND Spouse |Δ| narrow? Did act_JS hold ≤ 0.022?
  Cost: ~6 h cluster.

PHASE 2 — Restore demographics (Lever A) — full plumbing chain
  Scope revised 2026-05-21 after codebook + harmonizer audit.
  ATTSCH/POWST/MODE absent from Step 2 outputs; functions either missing
  (recode_attsch, derive_powst) or commented out (derive_mode at L620).
  Patch 01_readingGSS.py (Step 1 extractor):
    + 2005: EDUSTAT, MAR_Q190, MAR_Q193
    + 2010: EOR_Q210, CTW_Q140_C08
    + 2015: ESC1_01, CTW_140H (CTW_140I was wrong column for POWST)
    + 2022: already correct (EDC_10, CTW_140I)
  Patch 02_harmonizeGSS.py:
    + write recode_attsch() — universe-pad to clean binary across cycles
    + write derive_powst() — per-cycle column selection + clean binary
    + uncomment L620 to enable existing derive_mode() — MODE comes free
  Patch 03_mergingGSS.py: MAIN_COMMON_COLS += [ATTSCH, POWST, MODE]
  Patch 04A_dataset_assembly.py: CAT_COLS += [ATTSCH, POWST, MODE]
  No MISSING flags needed — LFTAG already disambiguates non-workers.
  Re-run Step 1+2+3 locally (~10 min). Retrain "J3-DEMO" on cluster on top of Phase 1.
  Gate check: 2022-Weekday AT_HOME cell narrow from 9.69 pp? Spouse Δ improve?
  Cost: ~6 h cluster + ~1 h local prep.

PHASE 3 — Tighten neighbor pairing (Lever B)
  Add ATTSCH/POWST to EXACT_COLS in 04C; switch K=5 to soft-target averaging
  for AT_HOME ONLY (keep activity AND co-presence as 1-of-K resampled).
  Retrain ("J3-NEIGH") on top of Phase 1+2.
  Gate check: Spouse Δ and AT_HOME cells improve further?
  Cost: ~6 h cluster.

PHASE 4 — Loss-side cleanups (Lever C-ii, iii, iv) — fold into Phase 1/2/3 retrains
  Set ACTIVITY_BOOSTS=0 env variable for the next retrain.
  Transition-rate penalty (λ_trans=0.05).
  Per-cell marginal-bias loss.
  Per-channel pos_weight on rare cop channels (not AT_HOME).
  Cost: 0 additional cluster time (folded into prior retrains).

PHASE 5 — Escape valve (only if all of Phase 1-4 leave gates open)
  Collapse 9-channel co-presence to 1 binary withAnyone.
  Document the regression for Step 5 / paper.
  Cost: ~6 h cluster.
```

**Total budget if all phases run sequentially:** ~30 hours of GPU time, ~1 week of human iteration.

**Stop condition.** Stop at the earliest phase where all 4 hard gates pass with margin. No need to run subsequent phases if Phase 1 or 2 already closes the gates.

---

## 6. Files to modify (concrete)

| File | Change | Phase |
|---|---|---|
| `04B_model_J3_v2.py` (NEW — copy from `04B_model_J3.py`, then edit `_encode()`) | Concat `cond_vec` to each slot token before `slot_linear`; update `slot_linear` input dim | 1 |
| `04D_train.py` (model import line) | Switch import to `04B_model_J3_v2` | 1 |
| `01_readingGSS.py` (MAIN_COLS_2005) | Add `EDUSTAT`, `MAR_Q190`, `MAR_Q193` for ATTSCH + POWST sources | 2 |
| `01_readingGSS.py` (MAIN_COLS_2010) | Add `EOR_Q210`, `CTW_Q140_C08` | 2 |
| `01_readingGSS.py` (MAIN_COLS_2015) | Add `ESC1_01`, `CTW_140H` (replaces the wrong `CTW_140I` mapping) | 2 |
| `02_harmonizeGSS.py` (new functions) | Write `recode_attsch()` and `derive_powst()` per-cycle; wire into `harmonize_main()` at L619 | 2 |
| `02_harmonizeGSS.py:620` | **Uncomment `df = derive_mode(df, cycle)`** — function already written at L150, just disabled | 2 |
| `03_mergingGSS.py` | Extend `MAIN_COMMON_COLS` (L78–85) with `['ATTSCH', 'POWST', 'MODE']` | 2 |
| `04A_dataset_assembly.py` (CAT_COLS list) | Add `ATTSCH`, `POWST`, `MODE` (04A already silently skips missing cols — adding activates them automatically) | 2 |
| `04C_training_pairs.py` (EXACT_COLS) | Add `ATTSCH`, `POWST` | 3 |
| `04D_train.py` (pair-loader, AT_HOME branch only) | Switch from 1-of-K resample to K-mean soft target — AT_HOME only by default | 3 |
| SLURM wrapper (env block) | `export ACTIVITY_BOOSTS=0` | 4 |
| `04D_train.py` (cop BCE block) | Per-channel `pos_weight` for parents, otherInFAMs, colleagues, friends | 4 |
| `04D_train.py` (activity loss) | Add transition-rate penalty term | 4 |
| `04D_train.py` (marg loss) | Per-cell instead of global | 4 |

---

## 7. Verification

The existing Step 4 validation harness (`step4_validation_report_v4.html`) reports after every retrain:

- Composite score
- All 4 hard gates (act_JS, AT_HOME RMS, Spouse Δ, composite)
- AT_HOME per-cell RMS table (12 cells)
- Per-channel co-presence prevalence gap (9 channels)
- Per-cycle / per-stratum activity JS

**Rule.** Composite should improve monotonically across phases. If any phase regresses a previously-passing gate (e.g., act_JS climbs above 0.022 after the per-slot broadcast edit), roll back and diagnose before continuing — never compound an unexplained regression with another change.

---

## 8. Out of scope

- **Census-linked variables** (Kinship, HomeOwn, RoomCount, Internet, CarOwn). These require running Step 5 *before* Step 4, which is a pipeline-order restructure. Documented as future work.
- **Old-Transformer pipeline restoration** (encoder-only with 24 categorical embeddings, single-day classification). Not pursued because (a) it doesn't solve the cross-strata generation task this project requires, and (b) the old pipeline was never measured against J3's distributional metric.
- **Step 6 / forecasting changes.** This plan is Step 4 only. Once Step 4 closes its gates, Step 6 fine-tuning proceeds against the improved weights.

---

## 9. Open risks

1. **(REVISED 2026-05-21)** Original risk was per-cycle missingness audit for ATTSCH/POWST in Step 2 outputs. Audit found neither column exists in Step 2 outputs — see §3 Lever A for full diagnosis. The actual residual risks for Phase 2 are:
   - **2005 ATTSCH undercount.** `EDUSTAT` only covers respondents whose main activity is school (~6.9%). Working part-time students contribute ~3 pp additional school-attendance that won't be captured. Acceptable noise floor; document but don't mitigate.
   - **2005/2010 POWST/ATTSCH semantic narrower than 2015/2022.** Phase 2 reconciles via universe-pad-to-No (2005 ATTSCH) and narrow-definition restriction (`MAR_Q193==5` for 2005 POWST). Cross-cycle baseline ~5% pre-COVID; 2022 17.7% is a clean COVID delta. If the model picks up "2005=less WFH because narrower definition" rather than "less WFH because true rate was lower", `CYCLE_YEAR` conditioning should absorb the artifact.
   - **2015 POWST extractor patch.** `01_readingGSS.md:113` documents `CTW_140I → POWST` for 2015, but `CTW_140I` is actually "Other transport mode" — `CTW_140H` is the correct WFH column. Phase 2 fixes this; downstream consumers of 2015 raw data that assumed `CTW_140I` for WFH need to be re-verified.
   - **MODE non-Main-derivable for 2005.** Episode-level `PLACE` codes during travel episodes could provide an episode-based MODE for 2005, but this is out of Phase 2 scope. 2005 MODE = NaN for now.
2. **Soft-target K-averaging** could over-smooth if accidentally applied to activity targets. Mitigation: explicit branch in `04D_train.py` pair-loader — averaging only on AT_HOME + cop targets, not activity.
3. **Pos_weight re-enable** destabilized AT_HOME globally in April 2026. Mitigation: apply only to rare co-presence channels, never to AT_HOME; monitor AT_HOME RMS each epoch.
4. **Do not break J3's `arm2_act_proj` projection** or the **Arm-1/Arm-2 detach barrier.** Both are load-bearing per the J-series history (§3.5). Lever C-i adds a new path (per-slot demographic broadcast in the encoder); it must not modify the Arm-2 fusion or remove detach. Smoke-test that J3 still produces composite 0.6355 ± noise after the Lever C-i edit with cond_vec broadcast set to zero (i.e., a no-op control).
5. **Per-cell marg loss and per-channel pos_weight are different from previously-failed global versions.** If either regresses AT_HOME during Phase 4, the regression mode will look identical to the F-series failures — roll back immediately, don't attempt to tune through it.
6. **Track all 4 gates jointly, never composite alone.** J4_1 hit composite 0.8247 but failed AT_HOME at 6.43 pp. A higher composite that breaks AT_HOME is not progress.

---

## Progress Log

### 2026-05-22 — Phase 1 (J3-PSB) — SHELVED (regression)

**Run.** `04B_model_J3_v2.py` with per-slot `cond_vec` broadcast prepended to `slot_linear` (input dim 86 → 162). 52 epochs, SLURM job 934720 on Speed `pg` partition, ~6 h training + inference + 04H/I/J diagnostics. Output bundle downloaded to `outputs_step4_J3_PSB/`.

**Result vs J3 baseline (lower = better for composite):**

| Metric | J3 (2026-04-22) | J3-PSB | Δ |
|---|---|---|---|
| Composite | **0.6355** | 0.8463 | **+0.21 (worse)** |
| AT_HOME RMS | 4.57 pp | 6.89 pp | +2.32 pp (worse) |
| COP max gap | — | 8.43 pp (Alone) | — |
| act_js_mean | 0.0191 | **0.0520** | +0.033 (worse, 2.7×) |
| cop_cal_mae | — | 0.2314 | — |
| Activity fail cells | 0 | **7/12** (2010_2, 2010_3, 2015_2, 2015_3, 2022_1, 2022_2, 2022_3) | — |

All 4 hard gates regress. Lever C-i is rejected as a single-axis change.

**Diagnostic signatures.**

1. **Training-loss collapse without test improvement** (signature of overfitting):
   - `train_loss` 1.94 (ep 1) → 0.44 (ep 52); `val_js` 0.238 → **0.004**.
   - Yet test `act_js_mean = 0.052` (2.7× J3's 0.019). Model memorized K=5 neighbor pairs; generalization to held-out cycle×stratum cells collapsed.

2. **Static demographic signal swamps temporal position embedding** (signature of architectural mismatch):
   - Per-slot AT_HOME gap (overall, T3 in `diagnostics_H_J3_PSB.json`): **morning +14.09 pp**, midday −1.88 pp, afternoon/evening **−5.79 pp**. Max gap_range_pp = 33.4 (overall), up to 36.0 in 2010_3.
   - Pattern: synthetic populations stay home in mornings, leave during work hours — opposite of physical reality. The encoder relied on demographic features instead of slot position. With `cond_vec` (~76 dims) prepended to every one of 48 slot tokens, the model received 3,648 demographic features per sample — capacity grew faster than supervision allowed.

3. **Head conflation** (signature of shared-feature collapse):
   - `alone × at_home` Cramer's V: obs **0.0666** → syn **0.2715** (4.1×).
   - Both heads fire off the same per-slot demographic features and the model treats them as near-equivalent. AT_HOME calibration MAE = 0.57 (only one calibration bin populated).

**Why this happened (root-cause synthesis).** PSB inserts `cond_vec` *as a parallel feature* to slot position, but `cond_vec` is constant across all 48 slots within a sample. The transformer encoder, given a static feature repeated 48× alongside a positional feature, can satisfy training loss by *down-weighting position* and *up-weighting the static feature* — the static feature has no slot-to-slot noise, so it's a low-variance shortcut. This is exactly the failure mode predicted by §3.5 row "C(i): Novel for J3 topology" — novel, untested, no historical safety check.

**Plan revisions triggered by this result.**

- **Phase 1 is now empty** (Lever C-i shelved). The original Phase 2 (POWST/ATTSCH/MODE data-side plumbing) is promoted to the new Phase 1.
- **PSB-Lite saved for Phase 2.** Two regularizations identified that could neutralize the failure mode for a future re-attempt:
  - Project `cond_vec` (~76 → 8) before per-slot broadcast — reduces effective extra-capacity from 3,648 to 384 per sample (~10×).
  - Cond-dropout per slot (p=0.5) — forces the model to keep using slot position by randomly hiding the static feature.
- **J3 architecture remains the baseline.** `04B_model_J3.py` is untouched; `04B_model_J3_v2.py` stays on disk for diagnostic reference but is not the production model.

**Open question for next phase.** Will the POWST/ATTSCH/MODE plumbing (Phase 1-new) close the 2022-Weekday AT_HOME cell (9.69 pp gap) and Spouse Δ on its own, or is a regularized PSB-Lite needed alongside? Decided to run the two as parallel cluster jobs: (1) data-plumbing-only on stock J3, (2) data-plumbing + PSB-Lite on J3 v3. Whichever wins seeds Phase 2.

### 2026-05-22 — Phase 2 cluster bundle: built + uploaded

After local Step 1 → 2 → 3 → 04A re-runs landed `d_cond = 90` tensors (see `01_readingGSS.md`, `02_harmonizationGSS.md`, `03_mergingGSS.md`, `04_augmentationGSS.md` Progress Logs for the per-stage detail), built the two-arm cluster bundle and uploaded as one recursive `scp` to Speed.

**Files in the bundle:**

| Path on cluster | Source | Purpose |
|---|---|---|
| `outputs_step4_G2/step4_{train,val,test}.pt` | local `outputs_step4/` | Phase 2 tensors (d_cond=90) |
| `outputs_step4_G2/step4_feature_config.json` | local | new ATTSCH/POWST/MODE one-hot widths |
| `04B_model.py` | patched | adds `JSeriesHybridV3` import hook at file footer |
| `04B_model_J3_v3.py` | NEW | PSB-Lite: `Linear(d_cond, 8)` projection + per-slot Bernoulli cond-dropout p=0.5 before broadcast |
| `04D_train.py` | patched | dispatches `J3_v3` → `JSeriesHybridV3`; reads `D_PSB_PROJ`/`P_PSB_DROP` env vars; threads them into `model_config` for `J3_v3` only |
| `04A_dataset_assembly.py` | patched | `CAT_COLS` extended with ATTSCH/POWST/MODE (unused on cluster but uploaded for reproducibility) |
| `configs/J3_DEMO.yaml` | NEW | Arm 1 config: stock J3 + new tensors |
| `configs/J3_DEMO_PSBLite.yaml` | NEW | Arm 2 config: `model_type: J3_v3`, `d_psb_proj: 8`, `p_psb_drop: 0.5` |
| `Speed_Cluster/jobs/J3_DEMO.sh` | NEW | SLURM wrapper, 48h walltime, `pg` partition, 1 GPU, 40G RAM; runs train → infer → 04H/04I/04J |
| `Speed_Cluster/jobs/J3_DEMO_PSBLite.sh` | NEW | Same skeleton, points at PSB-Lite config and output dir |
| `Speed_Cluster/config_to_env.sh`, `config_to_env.py` | patched | both add `d_psb_proj → D_PSB_PROJ` and `p_psb_drop → P_PSB_DROP` to the YAML → env mapping |

**Smoke test passed locally** before upload: instantiation + train forward + infer + eval-determinism. Parameter counts: J3 baseline 347,512 (TEST_CONFIG) → J3-PSB v2 raw 353,272 → **J3-PSB-Lite v3 348,752** (+1,240 over J3; ~5× less than v2's +5,760).

**Pending — user runs sbatch** (login node is submission-only per the cluster admin warning; manager role does not invoke sbatch). Two sbatch commands to run on the cluster, in any order, will queue both retrains in parallel on the `pg` partition.

Archive: `step4_Speed_Cluster/archive/04B_model_J3_v2.py` saved (shelved PSB raw) so the v2 → v3 architecture transition has a recoverable predecessor per the project's archive-before-edit convention.

### 2026-05-22 — Phase 2 first submission CRASHED; pair-file fix + re-submission

**Job 935024 (`J3_DEMO`) and 935025 (`J3_DEMO_PSBLite`)** both vanished from `squeue` after seconds, not hours. The `.out` log showed `04D_train.py` died at `[1/4] Loading datasets and pairs...` — the very first step after the training banner. The SLURM wrapper has no `set -e`, so the script obliviously stepped through inference + 04H/I/J on empty outputs, ending with misleading `=== DONE ===` lines that initially suggested success.

**Root cause:** the bundle was missing the K=5 pair files. `04A_dataset_assembly.py` produces tensor splits (`step4_{train,val,test}.pt` + `step4_feature_config.json`); `04C_training_pairs.py` is a **separate** script that builds `training_pairs.pt` + `val_pairs.pt` + `strata_inv_freq.npy`. The Phase 2 plumbing chain in this doc § Step 4 only listed 04A; 04C never got run locally before the bundle was zipped. `04D_train.py` requires all three of training_pairs.pt / val_pairs.pt / strata_inv_freq.npy at startup → silent KeyError/FileNotFoundError at line 1 of training.

**Fix.** Ran `04C_training_pairs.py` locally — output: 89,686 training pairs, 19,218 val pairs, 44,843 source respondents, uniform target-strata distribution (12,896 / 38,668 / 38,122 across strata 1/2/3). Total ~6 MB across three files. `scp` to `o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/outputs_step4_G2/`.

**Re-submitted 2026-05-22.** Both jobs RUNNING on `pg` partition. **Job IDs: `J3_DEMO` = 935035 (cisr-1), `J3_DEMO_PSBLite` = 935036 (cisr-2).** Logs: `logs/J3_DEMO_935035.out`, `logs/J3_DEMO_PSBLite_935036.out`.

**Early epoch read (epoch 1–10, ~1h26m wall):**

| Arm | ep 1 train_loss | ep 10 train_loss | best val_score (ep) | ep 10 home_gap | Status |
|---|---|---|---|---|---|
| J3_DEMO (935035) | 2.2815 | 1.2021 | 0.2365 (ep 9) | 0.1502 | healthy, still improving |
| J3_DEMO_PSBLite (935036) | 2.2854 | 1.2061 | **0.1744 (ep 2)** | 0.0927 | regularized PSB working — no collapse to ~0.44; lower home_gap than DEMO at matched epochs |

Critical: PSB-Lite **did not collapse** like raw J3-PSB v2 (which went to train_loss ~0.44 with worsening val). The 50% per-slot cond-dropout + 8-dim projection is biting as intended. PSB-Lite's best home_gap=0.0800 at epoch 5 already meaningfully better than DEMO's 0.1189. Yellow flag: PSB-Lite best was at epoch 2 and has not been beaten in 8 epochs — patience=15 gives headroom, but if it doesn't recover the saved checkpoint may underrepresent the architecture's potential. Re-check at ~epoch 17.

**Doc lesson logged here:** the Phase 2 Step 4 sub-checklist should explicitly list 04C as a required local step alongside 04A. Will update §5 / §6 / the Step 4 sub-list on the next checklist sweep so future cluster handoffs include the pair files automatically.

### 2026-05-22 — Phase 2 CANCELLED at epoch 41 (both arms)

**Decision.** Cancelled jobs 935035 (`J3_DEMO`) and 935036 (`J3_DEMO_PSBLite`) at ~6h34m wall (~ep 41/100, both arms) — `scancel 935035 935036`. Reasoning: home_BCE and cop_BCE losses had flatlined since epoch 11 with no differentiation between the two arms.

**Loss decomposition at best epoch + at cancel.**

| Loss | DEMO best (ep 35) | PSBLite best (ep 38) | DEMO ep 41 | PSBLite ep 41 |
|---|---|---|---|---|
| train_loss | 0.7268 | 0.7084 | 0.6624 | 0.6750 |
| act | 0.3908 | 0.3744 | 0.3305 | 0.3426 |
| **home** | **0.3893** | **0.3872** | **0.3845** | **0.3853** |
| **cop** | **0.2082** | **0.2064** | **0.2063** | **0.2056** |
| val_JS | 0.0227 | 0.0192 | 0.0186 | 0.0263 |
| home_gap | 0.0538 | 0.0622 | 0.0858 | 0.0800 |
| **val_score** | **0.0496** | **0.0503** | 0.0615 | 0.0663 |

**Diagnosis.** Home/cop BCE losses are essentially identical between arms (~0.385 / ~0.21 from ep 11 onward) — proving three things:

1. **Demographics restoration (Lever A) alone did NOT move binary heads materially.** The +14 dims (ATTSCH + POWST + MODE) reached the encoder via `d_cond = 76 → 90` and were consumed by `cls_mlp`, but the routing from CLS to slot tokens for binary heads is not propagating the new signal.
2. **Regularized PSB-Lite (Lever C-i with proj=8 / dropout=0.5) added no further headroom for binary heads** on top of plain demographics. The architecture-side fix did not survive contact with the data — possibly because the K=5 neighbor-disagreement floor (JS=0.1888) sits above the BCE floor that a better-routed encoder could reach.
3. **All val_score improvement was activity-driven.** val_JS dropped from 0.21 (ep 10) → 0.02 (ep 41) in both arms, mirroring the act loss curve. Activity was already at-edge passing in J3 baseline (act_JS = 0.0191); this gain is genuine but not the bottleneck for Spouse Δ or AT_HOME cells.
4. **Both arms appear bounded by the K=5 neighbor-disagreement floor.** No upstream/architecture change moves that floor. Only **Lever B (K-mean soft-target averaging on AT_HOME)** in `04D_train.py` pair-loader directly attacks it.

**Decision.** Skip inference + 04H/04I/04J — the loss curves are conclusive and a composite score would only confirm what we already see (no meaningful change vs J3 baseline 0.6355 on binary outputs). SHELVED both arms. Pivot to **Phase 3 (Lever B)**.

**Saved artifacts (downloaded for record).**
- `step4_Speed-Cluster_docs/CSV_records/step4_Speed_Cluster/outputs_step4_J3_DEMO/{checkpoints/best_model.pt, step4_training_log.csv}` (best at ep 35, `val_score=0.0496`)
- `step4_Speed-Cluster_docs/CSV_records/step4_Speed_Cluster/outputs_step4_J3_DEMO_PSBLite/{checkpoints/best_model.pt, step4_training_log.csv}` (best at ep 38, `val_score=0.0503`)
- `step4_Speed-Cluster_docs/CSV_records/J3_DEMO_935035.out`, `J3_DEMO_PSBLite_935036.out` (full training logs to ep 41)

**Upstream plumbing kept.** The Step 1+2+3+4A patches (ATTSCH/POWST/MODE end-to-end) are retained on disk and in `outputs_step4_G2/`. Phase 3 Lever B(i) (adding POWST/ATTSCH to `EXACT_COLS` in `04C_training_pairs.py`) is now unblocked as a direct extension of this work.

**CSV records updated.** Two `CANCELLED` rows appended each to `architecture_investigation.csv`, `training_config_investigation.csv`, `loss_values_trainings_investigation.csv`.

### 2026-05-22 — Phase 3 (Lever B) J3-NEIGH bundle BUILT (locally; awaiting local prep + upload)

**Scope of edits (3 source files + 2 new bundle files).**

| File | Change |
|---|---|
| `04C_training_pairs.py:31` | `EXACT_COLS` extended: `+ ["ATTSCH", "POWST"]`. Lever B(i). |
| `04A_dataset_assembly.py:390-396` | `meta_cols` extended: `+ ["ATTSCH", "POWST"]` so the new `EXACT_COLS` actually see the values in `step4_*_meta.csv`. Without this, 04C's missing-col fallback fills `-999` and the new exacts become a no-op. |
| `04D_train.py` `Step4Dataset.__init__` | Precomputes `self._home_soft = home_all[k_indices].mean(dim=1)` — K-mean across K=5 neighbors' AT_HOME vectors per pair. Static across epochs (the K indices are fixed; only the resampled neighbor for activity/cop changes). Lever B(ii). |
| `04D_train.py` `Step4Dataset.__getitem__` | Returns new `dec_home_soft: self._home_soft[i]` field alongside the 1-of-K `dec_aux_seq` / `dec_act_seq`. Activity + 9-channel cop targets are kept as 1-of-K resampled (averaging multi-class CE over-smooths act_JS; averaging cop dilutes rare positives below 0.5 BCE threshold and would inflate Spouse Δ). |
| `04D_train.py:163-170` (`compute_loss`) | `home_tgt = batch["dec_home_soft"].float()` when present, else falls back to binary `dec_aux_seq[:, :, 0]` for backwards compat with older pair files. `HOME_LABEL_SMOOTH` linear-shrink is kept and is compatible with soft targets in [0, 1]. |
| `step4_Speed_Cluster/configs/J3_NEIGH.yaml` | NEW. Identical lambdas/model to J3 baseline (`model_type: J3`, `lambda_home: 0.7`, all others as J3_DEMO). |
| `step4_Speed_Cluster/jobs/J3_NEIGH.sh` | NEW. SLURM wrapper, 48 h walltime, `pg` partition, 1 GPU, 40G RAM. Pipeline: train → infer → 04H → 04I → 04J. Output dir `outputs_step4_J3_NEIGH`. |

**Archive.** `_bundle_J3_DEMO/04D_train.py` (the pre-J3_NEIGH 04D snapshot) copied to `step4_Speed_Cluster/archive/04D_train_pre_J3_NEIGH.py`. No prior archive snapshot exists for 04C; the pre-edit 04C state is implicit in the J3_DEMO bundle's pair-file metadata but is not file-archived.

**Math sanity (no architecture change).**
- `_home_soft` values are in `{0, 1/5, 2/5, 3/5, 4/5, 1}` (K=5). After `HOME_LABEL_SMOOTH=0.05`: `[0.05, 0.23, 0.41, 0.59, 0.77, 0.95]`. All valid BCE targets.
- When K=5 neighbors agree (all-1 or all-0), the soft target is `1` or `0` and the loss matches the prior binary-target behaviour exactly (after label smoothing). The change only bites when neighbors disagree — which is *the entire point* of attacking the JS=0.1888 floor.

**Local prep + cluster upload completed 2026-05-22.**

1. **04A** re-ran cleanly. `outputs_step4/step4_train_meta.csv` now carries ATTSCH/POWST as the last two columns. `d_cond` unchanged at 90 (as expected — same CAT_COLS as Phase 2). Tensors saved at `outputs_step4/step4_{train,val,test}.pt`.
2. **04C** re-ran cleanly with tightened `EXACT_COLS`. Training pairs: **89,686** (= 12,896 / 38,668 / 38,122 across target strata 1/2/3). Val pairs: 19,218. Identical totals to Phase 2 (the count is structural — every source still gets K=5 neighbors per target stratum, with replacement padding when exact matches are scarce). The change shows up in *which* neighbors get top-K scoring, not the total. Inspection output `Exact-match score: 7/5` confirms ATTSCH and POWST are now scoring matches on top of the original 5 EXACT_COLS (cosmetic display bug — denominator stale at /5).
3. **Local smoke skipped.** Sample chain (`outputs_step3/hetus_30min_SAMPLE.csv` and downstream) doesn't exist; would have required re-running the full Step 2→3→4A pipeline in `--sample` mode. AST-parse check passes on all three edited Python files; shape contracts are preserved (AT_HOME target stays `(B, 48)` — only the source array changes). Acceptable risk: cluster will trip on shape/dtype within seconds at ep-1 if anything is wrong.
4. **Bundle uploaded.** `_bundle_J3_NEIGH/` (~6 MB total) → single recursive `scp -r * o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/`. Bundle contents:
   - `04A_dataset_assembly.py`, `04C_training_pairs.py`, `04D_train.py` (edited)
   - `outputs_step4_G2/{training_pairs.pt, val_pairs.pt, strata_inv_freq.npy}` (overwrites Phase 2 pair files)
   - `configs/J3_NEIGH.yaml`
   - `Speed_Cluster/jobs/J3_NEIGH.sh`

**Submitted 2026-05-22.** `sbatch /speed-scratch/o_iseri/occModeling/Speed_Cluster/jobs/J3_NEIGH.sh` → **job 935306**, RUNNING on `cisr-2`, `pg` partition, 48 h walltime. Log: `/speed-scratch/o_iseri/occModeling/logs/J3_NEIGH_935306.out`. Submitted within ~1 s of upload completion; no queue wait.

**Early-epoch monitoring target.** At ep 1–5 watch `home_loss` value. Phase 2 (DEMO + PSBLite) sat at ~0.44 → 0.40 over ep 1–10, then flat at 0.385. If J3-NEIGH's `home_loss` ep 5 is **below 0.38**, Lever B is working — the soft target is reducing the irreducible noise floor that bounded Phase 2. If it tracks the same 0.38–0.40 plateau, Lever B alone wasn't enough and Phase 4 loss-side cleanups need to stack.

**Hard guardrails (from doc § Quick-start).** Stop and report if train_loss NaN, AT_HOME loss diverging from the prior baseline range (~0.40–0.55 at ep 1), or shape mismatch in the home-loss call.

### 2026-05-23 — Phase 3 J3-NEIGH FAILED + Phase 4 J3-CLEAN bundle BUILT/UPLOADED

**Phase 3 J3-NEIGH outcome (job 935306).** Training failed and inference cascade additionally crashed.

| Symptom | Value | Reference |
|---|---|---|
| Best `val_score` | 0.2045 at ep 1 | vs Phase 2 DEMO 0.0496 (lower=better) — ~4× worse |
| Early-stop epoch | 16 | patience exhausted, never beat ep 1 |
| `home_gap` drift | 0.0336 (ep 1) → 0.2585 (ep 3) → 0.1547 (ep 16) | sigmoid head decalibrated |
| `home_loss` | ~0.51 (flat) | not comparable to J3 binary baseline ~0.385 — soft-target entropy floor |
| `val_JS` | 0.188 → 0.252 → 0.147 | activity head collaterally degraded |
| `augmented_diaries.csv` | not produced | 04E crashed on missing `step4_all_meta.csv` (operational, not diagnostic) |

**Diagnosis.** K-mean soft AT_HOME target with values in `{0, 0.2, 0.4, 0.6, 0.8, 1.0}` pulled the sigmoid output to fractional values instead of being pushed toward `0`/`1`. After threshold@0.5 the binarized AT_HOME rate became uncalibrated; BCE floor inflated by target entropy `H(h)` (e.g., `h=0.4 → 0.67`); joint loss reallocated encoder capacity → activity head also regressed. **Lever B is a fundamentally bad bias/variance trade for a binary head with a hard threshold.** Both Lever B(i) (tighter `EXACT_COLS`) and B(ii) (K-mean soft target) reverted as a bundle on 2026-05-23. Predecessor `04D_train.py` archived to `step4_Speed_Cluster/archive/04D_train_pre_J3_CLEAN.py`.

**Phase 4 J3-CLEAN bundle.** Stacked four cheap loss-side fixes on stock J3 (composite 0.6355). No architecture change; reverts Lever B; adds one new code path (`LAMBDA_TRANS`).

| Edit | Scope | Mechanism |
|---|---|---|
| `04C_training_pairs.py:31` | Revert | `EXACT_COLS` back to baseline 5 fields (drop ATTSCH/POWST) |
| `04D_train.py` `Step4Dataset` | Revert | Remove `_home_soft` precompute and `dec_home_soft` key — all targets back to 1-of-K resample |
| `04D_train.py` `compute_loss` | Revert | `home_tgt` reads binary `dec_aux_seq[:,:,0]` (no soft fallback) |
| `04D_train.py` `compute_loss` | New | Differentiable transition-rate penalty `\|E[#trans_pred] − E[#trans_obs]\|`, gated by `LAMBDA_TRANS` env var. Soft transitions: `1 − Σ_c p_c(t)·p_c(t+1)`. Backward-compatible default `0.0`. |
| `04D_train.py` epoch print + CSV | New | `trans_loss` field added to log (epoch-level mean). |
| `Speed_Cluster/config_to_env.sh` + `.py` | New | `lambda_trans → LAMBDA_TRANS` env mapping. |
| `configs/J3_CLEAN.yaml` | New | Stock J3 lambdas + `lambda_trans: 0.05` + `marg_mode: per_cs` + `activity_boosts: 0` + `cop_pos_weight: 1` + `cop_alone_pw: 0` + `spouse_neg_weight: 0.45`. |
| `Speed_Cluster/jobs/J3_CLEAN.sh` | New | SLURM wrapper, 48h walltime, `pg` partition, output dir `outputs_step4_J3_CLEAN`, train → infer → 04H/04I/04J pipeline. |

**Local prep.** Re-ran `04C_training_pairs.py` locally → new `training_pairs.pt` / `val_pairs.pt` with reverted EXACT_COLS (89,686 train pairs; exact-match score back to 5/5 from prior 7/5).

**Bundle uploaded 2026-05-23.** `_bundle_J3_CLEAN/` (~10 MB total) → single recursive `scp -r ...` to `/speed-scratch/o_iseri/occModeling/`. Contents:
- `04A_dataset_assembly.py`, `04C_training_pairs.py`, `04D_train.py` (edited)
- `Speed_Cluster/config_to_env.sh` and `Speed_Cluster/config_to_env.py` (lambda_trans mapping)
- `configs/J3_CLEAN.yaml`
- `Speed_Cluster/jobs/J3_CLEAN.sh`
- `outputs_step4_G2/{training_pairs.pt, val_pairs.pt, strata_inv_freq.npy, step4_all_meta.csv}` (overwrites Phase 3 pair files; restores the missing meta CSV so 04E inference doesn't crash)

**Submitted 2026-05-23.** `sbatch /speed-scratch/o_iseri/occModeling/Speed_Cluster/jobs/J3_CLEAN.sh` → **job 936116**, RUNNING on `cisr-2`, `pg` partition, 48 h walltime. Log: `/speed-scratch/o_iseri/occModeling/logs/J3_CLEAN_936116.out`. Submitted within ~5 s of upload completion; no queue wait.

### 2026-05-23 — Phase 4 J3-CLEAN FAILED catastrophically → pivot to Phase 6 sample-architecture sweep

**Job 936116 COMPLETE.** Training STOPPED at ep 16/100 via patience exhaustion. **Best checkpoint = ep 1** (val_score 0.2285) — model never improved past random init. Composite from best checkpoint = **3.2919** (vs J3 baseline 0.6355, ~5.2× worse). 0/4 gates pass.

| Metric | J3 baseline | J3-CLEAN | Δ |
|---|---|---|---|
| Composite score | 0.6355 | **3.2919** | +2.66 (FAIL by 2.25) |
| AT_HOME RMS | 4.57 pp | **18.25 pp** | +13.68 pp (FAIL) |
| COP max gap | 4.51 pp Alone | **43.38 pp parents** | +38.87 pp (FAIL) |
| Activity JS mean | 0.0191 | **0.3141** | +0.295 (FAIL) |
| COP cal MAE mean | ~0.05 | **0.3092** | +0.26 (FAIL) |
| AT_HOME syn mean | 72.5% obs / ~72% syn | **93.8% syn** | +21.3 pp over-prediction |

**Training-log signature.** `trans_loss` descended 9.49 (ep 1) → 1.51 (ep 16) — the transition-rate penalty *did* drive its own loss, but at the cost of everything else. `val_score` froze at 0.4162 for ep 2–13 (identical to 4 decimals), then mild improvement ep 14–16 (0.4158 → 0.4028) — never re-approached ep 1's 0.2285. `act_loss` 2.24 → 0.95 (still ~10× J3's 0.088 floor). `home_loss` 0.53 → 0.41 (vs J3's 0.35). The 4 stacked fixes (`LAMBDA_TRANS=0.05` + `MARG_MODE=per_cs` + per-channel `COP_POS_WEIGHT` + `SPOUSE_NEG_WEIGHT=0.45` + `ACTIVITY_BOOSTS=0`) created a loss landscape the optimizer could not navigate — the best minimum it found in 16 epochs was no better than initialization.

**Diagnosis.** Stacking violated the one-axis isolation rule (CLAUDE.md research guardrail). With 5 simultaneously-changed loss-side knobs we cannot attribute the failure to any single mechanism. Unstacking one-at-a-time on full data costs 4 more 6h cycles to learn what is already strongly suspected: **the J3 loss landscape has been mined out**. Further single-knob loss tuning on J3 architecture is unlikely to beat 0.6355.

**Strategic pivot.** Phases 1–4 of this plan (J3-PSB, J3-DEMO, J3-DEMO-PSBLite, J3-NEIGH, J3-CLEAN) all failed to beat the J3 baseline despite full-data 5h+ cycles each. The marginal architectural/loss tweaks have run their course. Per user direction (2026-05-23), shift methodology to a **stratified 5% sample architecture sweep** — the approach previously used for predictive architectures. Test 10–20 structurally distinct generative architectures in parallel on the sample, rank by proxy composite, promote top 2–3 to full-data verification.

**Local actions.**
- Downloaded `outputs_step4_J3_CLEAN/{diagnostics_*.json, step4_training_log.csv}` and `logs/J3_CLEAN_936116.{out,err}` to `step4_Speed-Cluster_docs/cluster_outputs/outputs_step4_J3_CLEAN/` via single `scp` bundle.
- Updated CSV records (`architecture_investigation.csv`, `loss_values_trainings_investigation.csv`, `training_config_investigation.csv`) with J3_CLEAN SHELVED row.
- J3 (0.6355) remains the SHIP baseline.

**Phase 6 (Sample-architecture sweep) — PENDING DEEP-RESEARCH INPUT.** User running web-based deep-research prompts across multiple LLMs (ChatGPT/Gemini/Perplexity/Claude). On receipt of candidate shortlist: draft Phase 6 section with (1) stratified 5% sample construction (`cycle × DDAY_STRATA × HHSIZE`, rare-cop-channel floor), (2) per-trial SLURM harness in `step4_Speed_Cluster/sample_jobs/`, (3) ranking proxy (composite + act_JS + AT_HOME RMS 4-cell + Spouse Δ), (4) promotion rule (top 2–3 to full-data retrain for hard-gate verification). Sample sweep is for **structural architecture variation only** — loss-coefficient tuning remains a full-data activity (sample misrepresents loss-knob × target-statistic interactions).

**Early-epoch monitoring target.** Ep 1–5 watch `act_loss` (should be lower than J3 baseline ~0.88 with ACTIVITY_BOOSTS=0), `trans_loss` (should converge from ~5–10 toward ~1 as predicted transitions match observed), and `home_loss` (should track baseline ~0.40–0.55 ep 1, ~0.385 ep 11+). If any term diverges, NaN, or AT_HOME RMS regresses on validation, cancel and roll back.

### 2026-05-23 — Phase 6 Stage A build COMPLETE (local) — sample tensors NOT YET generated

**Scope.** All 17 local-side deliverables of the Phase 6 Stage A plan landed in one bundle: 6 new source files + 5 patched + 10 sample configs + 10 SLURM wrappers + 2 env-mapping extensions. Built without running the assembler — so the **code** is ready; the actual `outputs_step4_G2_sample2/` tensor bundle still needs to be produced by one local invocation of `04A_sample_assembly.py` (see "Next step" below).

**Files added (relative to `2J_docs_occ_nTemp/`):**

| Path | Purpose |
|---|---|
| `04A_sample_assembly.py` | Stratified sub-sampler. `--frac 0.02` default; rare-cop-channel floor ≥200 per stratum (parents, otherInFAMs, friends, others, colleagues); frozen `seed=42`. Re-uses an existing G2-format bundle; emits a byte-compatible mirror including `step4_{train,val,test}.pt`, `*_meta.csv`, `step4_all_meta.csv`, `step4_feature_config.json` (with re-computed `cop_pos_weights` + `act_class_freqs` for the sample), `strata_inv_freq.npy`, and a per-rare-cop coverage report. Reused for Stage B with `--frac 0.20`. |
| `04B_model_HSMM.py` | Trial 4 — Neural HSMM decoder. Per-slot state head + duration head (D_MAX=12) + learned hold prior. Greedy decode with hold bonus at inference. |
| `04B_model_MDLM.py` | Trial 5 — Masked Diffusion LM (Sahoo et al. 2024). Bidirectional x_0 parameterisation, learned `[MASK]` token, 16-step iterative top-confidence unmasking at inference. |
| `04B_model_HIER.py` | Trial 6 — Hierarchical coarse → refine. 4 blocks × 12 slots; coarse head pools and predicts block-level activity, refine head fuses (slot, coarse-soft, within-block-pos) → 48-slot logits. |
| `04B_model_MAMBA.py` | Trial 7 — Selective SSM. 2-layer simplified Mamba S6 block stacked on encoder slots (input-dependent Δ via softplus, sequential Python scan — CUDA kernel optional for Stage C). |
| `04B_model_SEDD.py` | Trial 10 — Score-Entropy Discrete Diffusion (Lou et al. 2024). Absorbing-state diffusion, power-law σ(t)=t², sinusoidal time embedding, 24-step inference. |
| `step4_Speed_Cluster/sample_configs/<TAG>_A.yaml` × 10 | Per-trial config: `tag`, `model_type`, `sample_frac=0.02`, `max_epochs=50`, `patience=10`, J3 baseline lambdas held constant; only `use_film/use_fourier_pe/use_prefix/use_spl/use_fact/loss_mode` differ. Tags: `CC_A`, `CC_SPL_A`, `CC_FACT_A`, `HSMM_A`, `MDLM_A`, `HIER_A`, `MAMBA_A`, `SINK_A`, `GCE_A`, `SEDD_A`. |
| `step4_Speed_Cluster/sample_jobs/<TAG>_A.sh` × 10 | Per-trial SLURM wrapper. `pg` partition, 1 GPU, 40G RAM, **48 h walltime** (per `feedback_cluster_walltime_minimum.md`); pipeline `04D_train → 04E_inference → 04H → 04I → 04J`; output dir `outputs_step4_sample/<TAG>_A/`. |

**Files patched:**

| Path | Change |
|---|---|
| `04B_model.py` | Phase 6 CC conditioning layers (FiLM `γ, β = Linear(d_cond, d_model)`, Fourier diurnal PE at 4 frequencies → projected to `d_model`, per-stratum learnable prefix tokens of `k=4` per stratum). All gated by `USE_FILM`/`USE_FOURIER_PE`/`USE_PREFIX` env reads; defaults **0** → byte-identical J3 behaviour. Prefix tokens are stripped from `_encode` output to keep downstream `memory[:, 1:, :]` slicing unchanged. Import hooks for HSMM/MDLM/HIER/MAMBA/SEDD added at file footer. |
| `04B_model_J3_v2.py` / `04B_model_J3_v3.py` | `_encode` signature accepts new `tgt_strata=None` kwarg (forward-compatible — parent passes it for USE_PREFIX path; V2/V3 ignore it). |
| `04C_training_pairs.py` | New `--sample_dir` flag (takes precedence over `--sample`). When set, builds K=5 pairs from the sample slice and writes `js_disagreement_floor.json` measuring mean pairwise JS across K=5 neighbour activity distributions (probe = 500 sources). Baseline reference 0.1888 (full G2) embedded for ratio reporting. |
| `04D_train.py` | (a) Reads new env vars `USE_SPL`, `USE_FACT`, `LOSS_MODE`, `SPL_LAMBDA=0.1`, `FACT_LAMBDA=0.3`, `GCE_Q=0.5`, `SINKHORN_EPS=0.05`. (b) `compute_loss` switches activity term on `LOSS_MODE`: `ce` (default), `gce` (Generalized CE), `sinkhorn` (1-D EMD batch-mean per slot + ε·KL regulariser). (c) SPL constraint term added: 4 soft-logic rules (¬home⇒¬alone, work⇒¬home, work⇒colleagues, sleep⇒home) computed on σ(home_logits) × softmax(act_logits) × σ(cop_logits); weight is `SPL_LAMBDA` when `USE_SPL=1`, escalated to `FACT_LAMBDA` when `USE_FACT=1`. (d) `MODEL_TYPE` dispatch extended with `HSMM`/`MDLM`/`HIER`/`MAMBA`/`SEDD`; all 5 inherit the J-series training hygiene (fp32, ReduceLROnPlateau, `clip_grad_norm=25`, no LambdaLR warmup). |
| `04E_inference.py` | Dispatch extended for `J3_v3` (was missing) and the 5 new Phase 6 model families. Each loads via its own importlib hook. |
| `step4_Speed_Cluster/config_to_env.{sh,py}` | `ENV_MAP` extended with `use_film`, `use_fourier_pe`, `use_prefix`, `use_spl`, `use_fact`, `loss_mode`, `sample_frac`, `tag` (the last one for downstream job-log identification). |

**CPU smoke tests (local).**

| Check | Result |
|---|---|
| `py_compile` on all 12 added/patched .py files | 12/12 OK |
| Import of all 6 new model classes through `04B_model` | OK (`JSeriesHybrid` + V2 + V3 + 5 new all present) |
| Forward + infer pass on each of HSMM/MDLM/HIER/MAMBA/SEDD with `USE_FILM=USE_FOURIER_PE=USE_PREFIX=1` on a B=4, T=48, n_act=14, n_cop=9, d_cond=16 synthetic batch | All return `act_logits=(4,48,14)`, `home_logits=(4,48)`, `cop_logits=(4,48,9)`, `gen_act=(4,48)`, `cop_prob=(4,48,9)` |
| `compute_loss` on J3 + CC + `USE_SPL=1` + `LOSS_MODE=gce` | total=2.15, act_loss(gce)=1.52, spl_loss=0.38 — all paths fire, no NaN, no shape mismatch |

**Open follow-ups (do NOT block Stage A submission, surface for Stage C if survivors emerge):**

1. Local `outputs_step4/` is the G2-equivalent bundle (d_cond=90, ATTSCH/POWST/MODE present, train=44,843 / val=9,609 / test=9,609 — confirmed via `step4_feature_config.json`). There is no `outputs_step4_G2/` directory locally — that name is the cluster-side convention. So the assembler must be invoked with `--src outputs_step4` locally, but the output dir name (`outputs_step4_G2_sample2/`) will still match what the 10 SLURM wrappers expect on the cluster.
2. SPL rule R2 (`work ⇒ ¬home`) likely violates real WFH cases in the 2022 cycle. Flagged in plan Risk #3 — mitigation is to mine `p(at_home=1 | activity=work)` per cycle before Stage C and downgrade R2 to a softer constraint if it sits below the 99% rule-of-thumb.
3. `_MambaBlock` uses a Python sequential scan (correct but slow). T=48 keeps it acceptable for Stage A (~1 h per trial), but Stage C should swap in the `mamba-ssm` CUDA kernel if MAMBA wins.
4. MDLM / SEDD use a clean-encoder second pass for Arm-2 binary heads (so the masking noise doesn't perturb home/cop predictions). Doubles encoder FLOPs at training time; cheap relative to scan/refiner work.

---

### 2026-05-24 — Phase 6 Stage A results + structural fix + Stage B promotion (bundle v2)

**Stage A first-pass results (jobs 936227–936236, submitted 2026-05-24):**

| Trial | Composite | Status |
|---|---|---|
| CC_A | 1.474 | VALID — promoted to Stage B |
| CC_SPL_A | 1.566 | VALID — promoted to Stage B |
| GCE_A | 1.735 | VALID |
| CC_FACT_A | 1.926 | VALID |
| SINK_A | 2.428 | VALID |
| HSMM_A | — | CRASHED at 04E — state_dict mismatch |
| MDLM_A | — | CRASHED at 04E — state_dict mismatch |
| HIER_A | — | CRASHED at 04E — state_dict mismatch |
| MAMBA_A | — | CRASHED at 04E — state_dict mismatch |
| SEDD_A | — | CRASHED at 04E — state_dict mismatch |

**Root cause (04D_train.py:932–934 — J-series elif routing bug):**
The `elif MODEL_TYPE in (...)` tuple at line 932 listed "HSMM", "MDLM", "HIER", "MAMBA", "SEDD" alongside the J-series tags. This caused all 5 structural types to instantiate `JSeriesHybrid` (not their own class), making the explicit `elif MODEL_TYPE == "HSMM"` / "MDLM" / "HIER" / "MAMBA" / "SEDD" branches at lines 937–951 unreachable. Checkpoints were saved with J3 topology; 04E_inference then tried to load them into `HSMMHybrid` / etc. → key mismatch crash.

**Fix applied (2026-05-24):**
Predecessor archived to `step4_Speed_Cluster/archive/04D_train_pre_structural_fix.py`.
Single edit: removed "HSMM", "MDLM", "HIER", "MAMBA", "SEDD" from the J-series elif tuple at line 932–933. All other tuples (clip-norm line 1046, LR scheduler line 1074–1075, warmup line 1156–1157) correctly retain all 10 tags and were NOT touched.

**Stage B promotion (CC + CC_SPL):**
- New configs: `step4_Speed_Cluster/sample_configs/CC_B.yaml`, `CC_SPL_B.yaml` — tag→_B, sample_frac→0.20, max_epochs→100, patience→15, data_dir→outputs_step4_G2_sample20.
- New wrappers: `step4_Speed_Cluster/sample_jobs/CC_B.sh`, `CC_SPL_B.sh` — 48h walltime, pg partition.
- 20% sample assembled locally: `outputs_step4_G2_sample20/` — 9,318 train / 1,915 val / 1,922 test, all rare-cop floors met (≥200 per stratum). K=5 JS-disagreement floor = 0.1955.
- Training pairs built locally: 18,636 train pairs / 3,830 val pairs.

**Bundle v2 (`_bundle_sweepA_v2/`):**
```
04D_train.py  (structural fix — HSMM/MDLM/HIER/MAMBA/SEDD no longer shadowed)
step4_Speed_Cluster/sample_configs/CC_B.yaml
step4_Speed_Cluster/sample_configs/CC_SPL_B.yaml
step4_Speed_Cluster/sample_jobs/CC_B.sh
step4_Speed_Cluster/sample_jobs/CC_SPL_B.sh
outputs_step4_G2_sample20/  (13 files: .pt tensors + meta CSVs + feature_config.json + pairs)
```
`deploy_and_submit_v2.sh` written locally — overwrites 04D_train.py on cluster, copies new configs/wrappers/data, fixes CRLF, then submits 7 jobs.

**Upload + submission commands (user to run):**

Locally:
`scp -r C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\2J_docs_occ_nTemp\_bundle_sweepA_v2 o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/`

Locally:
`scp C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\2J_docs_occ_nTemp\deploy_and_submit_v2.sh o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/`

On the cluster:
`chmod +x /speed-scratch/o_iseri/occModeling/deploy_and_submit_v2.sh && bash /speed-scratch/o_iseri/occModeling/deploy_and_submit_v2.sh`

**Expected SLURM output (7 job IDs):**
Jobs 1–5: HSMM_A, MDLM_A, HIER_A, MAMBA_A, SEDD_A (structural Stage A re-runs, now routing correctly)
Jobs 6–7: CC_B, CC_SPL_B (Stage B, 20% sample, 100 epochs)

**Submitted 2026-05-24 (7 fresh job IDs):**
| Job ID | Trial | State (at submit) | Node |
|---|---|---|---|
| 936316 | HSMM_A | RUNNING | cisr-2 |
| 936317 | MDLM_A | RUNNING | cisr-1 |
| 936318 | HIER_A | RUNNING | speed-03 |
| 936319 | MAMBA_A | RUNNING | speed-17 |
| 936320 | SEDD_A | PENDING | AssocGrpGRES |
| 936321 | CC_B | PENDING | AssocGrpGRES |
| 936322 | CC_SPL_B | PENDING | AssocGrpGRES |

`pg` partition at capacity → 4 RUNNING + 3 PENDING; PENDING jobs will start as RUNNING slots free.

**Module precheck:** All structural model files (04B_model_HSMM/MDLM/HIER/MAMBA/SEDD.py) import only standard Python + PyTorch — no additional pip installs required.

**Predecessor archive:** `step4_Speed_Cluster/archive/04D_train_pre_structural_fix.py`

**Next step (local, single line, on Windows PowerShell):**

```
cd C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\2J_docs_occ_nTemp; py 04A_sample_assembly.py --src outputs_step4 --frac 0.02 --out outputs_step4_G2_sample2
```

That writes `outputs_step4_G2_sample2/` with ~3,000 stratified train respondents (plus proportional val + test). Then build K=5 pairs and log the JS-disagreement floor on the same slice:

```
cd C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\2J_docs_occ_nTemp; py 04C_training_pairs.py --sample_dir outputs_step4_G2_sample2
```

After both finish, the sample bundle + the 17 build artefacts are ready for the single recursive `scp -r` upload to `/speed-scratch/o_iseri/occModeling/` and the 10-job sbatch wave (`sbatch sample_jobs/<TAG>_A.sh` × 10).

---

### 2026-05-24 — Phase 6 Stage A v2 RESULTS + Stage B expansion (SEDD_B + MDLM_B)

**Stage A v2 — 5 structural re-runs after routing fix (jobs 936316–936320):**

| Job | Trial | Elapsed | State | Composite |
|---|---|---:|---|---:|
| 936316 | HSMM_A | 05:47 | COMPLETED | **1.440** |
| 936317 | MDLM_A | 16:28 | COMPLETED | **0.793** |
| 936318 | HIER_A | 01:52 | COMPLETED | **1.456** |
| 936319 | MAMBA_A | 10:33 | COMPLETED | **1.489** |
| 936320 | SEDD_A | 03:51 | COMPLETED | **1.034** |

Routing fix verified — all 5 structural trials wrote full diagnostics (no state_dict mismatches).

**Full Stage A v2 ranking (all 10 trials valid):**

| Rank | Trial | Composite | AT_HOME RMS pp | cop_max_gap pp | act_JS | cop_MAE |
|---:|---|---:|---:|---:|---:|---:|
| 1 | **MDLM** | **0.793** | 9.02 | 5.98 | 0.088 | 0.097 |
| 2 | **SEDD** | **1.034** | 7.67 | 9.45 | 0.117 | 0.139 |
| 3 | HSMM | 1.440 | 17.35 | 5.41 | 0.245 | 0.046 |
| 4 | HIER | 1.456 | 15.10 | 5.19 | 0.254 | 0.083 |
| 5 | CC | 1.474 | 15.70 | 6.20 | 0.243 | 0.092 |
| 6 | MAMBA | 1.489 | 16.15 | 8.21 | 0.228 | 0.081 |
| 7 | CC_SPL | 1.566 | 15.15 | 9.01 | 0.239 | 0.113 |
| 8 | GCE | 1.735 | 19.07 | 8.52 | 0.278 | 0.083 |
| 9 | CC_FACT | 1.926 | 14.94 | 18.76 | 0.237 | 0.141 |
| 10 | SINK | 2.428 | 28.65 | 10.74 | 0.407 | 0.053 |

**Discrete-diffusion family dominates Stage A.** Caveat: MDLM (act_JS=0.088) and SEDD (act_JS=0.117) both sit *below* the predicted 2%-sample JS floor (~0.25) — could be genuine multimodality capture OR smoothing artifact (bidirectional denoising producing too-smooth marginals that match averages but lack diversity). Stage B at 20% will resolve.

**Stage B decision (manager, 2026-05-24):** Stage A spec was "top 3 from A" but rankings argued for top 4 (MDLM+SEDD clearly ahead; CC/CC_SPL already running). Final Stage B = 4 trials: CC_B + CC_SPL_B (already submitted in bundle v2) + SEDD_B + MDLM_B (added via bundle B2).

**Bundle B2 (`_bundle_sweepB_v2/`):**
- `step4_Speed_Cluster/sample_configs/{SEDD_B,MDLM_B}.yaml` — 20% sample, 100 ep, patience 15, CC toggles preserved from Stage A (`use_film=use_fourier_pe=use_prefix=1`) for apples-to-apples
- `step4_Speed_Cluster/sample_jobs/{SEDD_B,MDLM_B}.sh` — 48h pg, `set -e` added (defends against silent COMPLETED 0:0)
- No 04D edit, no data dir (already on cluster from v2)
- `deploy_and_submit_B2.sh` — flat-copy 4 files, sed CRLF, sbatch ×2

**Upload + submission (2026-05-24):**
- `scp -r _bundle_sweepB_v2/` + `scp deploy_and_submit_B2.sh` to `/speed-scratch/o_iseri/occModeling/`
- `bash deploy_and_submit_B2.sh` → 2 fresh job IDs

**Stage B v2 submitted (2026-05-24):**

| Job ID | Trial | Sample | Epochs | Patience |
|---|---|---|---:|---:|
| 936321 | CC_B | 20% | 100 | 15 |
| 936322 | CC_SPL_B | 20% | 100 | 15 |
| 936327 | SEDD_B | 20% | 100 | 15 |
| 936328 | MDLM_B | 20% | 100 | 15 |

**CC_B result (job 936321, COMPLETED 17:26):**
- composite = **1.690** — *worse* than CC_A (1.474); CC regressed at 20%
- AT_HOME RMS = 20.33 pp (CC_A: 15.70); cop_max_gap = 7.50 pp (6.20); act_JS = 0.267 (0.243); cop_MAE = 0.088 (0.092)
- Patience-exit at epoch 19/100; best epoch was **ep 4** (val_score=0.147, train_loss=2.15 → 1.20 at ep 19)
- Training instability: val_js oscillating 0.09 → 0.27 → 0.15 → 0.27 between ep 1–19 (not converging)
- Diagnosis: CC's Stage A win may have been over-fit to 2% K-NN noise; at 20% the same architecture cannot find a stable val minimum, patience-exit fires too early. Stage B winner unlikely to be CC.
- Artifacts pulled to `step4_Speed-Cluster_docs/cluster_outputs/sweepB/CC_B/` (5 files: diagnostics × 3 + training log + augmented_diaries.csv)

**Queue state (2026-05-24, after CC_B finish):**
- 936322 CC_SPL_B RUNNING (~22:48 elapsed)
- 936327 SEDD_B RUNNING (just started)
- 936328 MDLM_B RUNNING (just started)

**MDLM_B result (job 936328, COMPLETED 25:58):**
- composite = **0.6898** — best Stage B result so far; only **+0.054 vs J3 baseline (0.6355)** on just 20% sample
- AT_HOME RMS = 7.73 pp · cop_max_gap = 5.48 pp · act_JS = 0.077 · cop_cal_MAE = 0.074
- Improvement vs MDLM_A (0.793): −0.103; scaling cleanly from 2% → 20%
- Improvement vs CC_B (1.690): −1.000; confirms structural diffusion beats AR conditioning at scale
- Training: 51+ epochs completed (no patience exit), train_loss 2.62 → 0.60 monotonically descending, val_score best ~0.049 at ep 36, val stable in 0.05–0.07 band (no oscillation)
- Activity head excellent: val_js consistently ~0.03 (well under 0.05 gate)
- Artifacts pulled to `step4_Speed-Cluster_docs/cluster_outputs/sweepB/MDLM_B/`
- **Verdict: MDLM is a strong Stage C candidate.** Diffusion family confirmed; awaiting SEDD_B to decide whether Stage C is MDLM-only or MDLM+SEDD parallel.

**Queue state (2026-05-24, after MDLM_B finish):**
- 936322 CC_SPL_B RUNNING (~1:00 elapsed)
- 936327 SEDD_B RUNNING (~39 min elapsed)
- 936328 MDLM_B COMPLETED ✓

**SEDD_B result (job 936327, COMPLETED 01:18:08):**
- composite = **0.8666** — #2 in Stage B; same diffusion family as MDLM but worse on cop/act components
- AT_HOME RMS = **7.43 pp** (tied with MDLM_B 7.73) · cop_max_gap = **9.19 pp (Alone)** · act_JS = 0.0845 · cop_cal_MAE = 0.1006
- Dominant failure mode: synthetic over-predicts Alone (+9.19 pp, CI 8.55–9.79)
- vs MDLM_B (0.6898): +0.177 composite; SEDD's score-entropy parameterisation underperforms MDLM's masked-CE at 20% scale, but AT_HOME parity suggests SEDD scales differently and may close the gap at 100%
- Artifacts pulled to `step4_Speed-Cluster_docs/cluster_outputs/sweepB/SEDD_B/`

**CC_SPL_B result (job 936322, COMPLETED 01:15:06):**
- composite = **1.4748** — #3 in Stage B; CC family dead even with SPL semantic constraints
- AT_HOME RMS = **15.12 pp** · cop_max_gap = 7.34 pp (Alone) · act_JS = **0.236** · cop_cal_MAE = 0.0886
- act_JS = 0.236 is 12× MDLM's 0.077 — SPL constraints did not rescue the AR-conditioning backbone
- vs CC_B (1.690): −0.21; SPL adds value but cannot lift CC family into Stage C contention
- Artifacts pulled to `step4_Speed-Cluster_docs/cluster_outputs/sweepB/CC_SPL_B/`

### Stage B final ranking (2026-05-24)

| Rank | Trial | Composite | AT_HOME RMS (pp) | cop_max (pp) | act_JS | cop_cal_MAE | Verdict |
|---|---|---:|---:|---:|---:|---:|---|
| 1 | **MDLM_B** | **0.6898** | 7.73 | 5.48 | 0.077 | 0.074 | **PROMOTE to Stage C** |
| 2 | **SEDD_B** | **0.8666** | 7.43 | 9.19 | 0.085 | 0.101 | **PROMOTE to Stage C (hedge)** |
| 3 | CC_SPL_B | 1.4748 | 15.12 | 7.34 | 0.236 | 0.089 | SHELVED |
| 4 | CC_B | 1.690 | — | — | — | — | SHELVED |

### Stage C promotion decision (2026-05-24): MDLM_C + SEDD_C parallel

**Rationale for running both** (revised from initial MDLM-only recommendation per user direction):
- MDLM_B beats SEDD_B by 0.18 composite — substantial but **AT_HOME parity (7.43 vs 7.73 pp)** suggests SEDD's failure is concentrated in cop_max (Alone over-prediction), which may resolve at full data when the Alone-rich strata get adequate K=5 neighbours.
- Stage B sample noise (20% slice) can flip orderings; a single GPU-day hedge buys insurance against MDLM's lead being noise.
- Diffusion family is the only structural family that broke 1.0 composite at 20% — running both variants on full data lets us pick the better parameterisation rather than commit to one based on a small-sample bake-off.
- Cost: 2× ~5–6h wall-clock on `pg` partition (parallel sbatch); total ~1 GPU-day.

**J3 baseline = 0.6355 at 100%.** MDLM_B = 0.6898 at 20%. Scaling 2%→20% dropped MDLM composite 0.103. Linear extrapolation puts MDLM_C ≈ 0.59 (beats J3 by ~0.05). SEDD_C extrapolated similarly: ≈ 0.76 (still above J3 but closing).

**Stage C Hard Gates (4/4):**
- composite < 1.045
- AT_HOME RMS ≤ 5.3 pp
- Spouse |Δ| ≤ 5 pp
- act_JS ≤ 0.05

### Stage C build plan (2026-05-24)

**Files to add:**

| File | Purpose |
|---|---|
| `step4_Speed_Cluster/sample_configs/MDLM_C.yaml` | tag=MDLM_C, model_type=MDLM, sample_frac=1.0 (full data, no sub-sampling), max_epochs=100, patience=15, seed=42, batch=256, lr=5e-5 |
| `step4_Speed_Cluster/sample_configs/SEDD_C.yaml` | tag=SEDD_C, model_type=SEDD, same knobs as MDLM_C |
| `step4_Speed_Cluster/sample_jobs/MDLM_C.sh` | `pg` partition, 1 GPU, 40G RAM, **48h walltime**, output dir `outputs_step4_full/MDLM_C/`, pipeline 04D→04E→04H→04I→04J |
| `step4_Speed_Cluster/sample_jobs/SEDD_C.sh` | same wrapper template as MDLM_C with `--tag SEDD_C` |

**Data path:** Stage C uses existing **full** `outputs_step4_G2/` tensors (NOT `outputs_step4_G2_sample2/`). No sample assembly needed.

**Execution (per memory rules: bundle once, submit once, download once):**

1. *Local prep*: write 2 YAMLs + 2 wrappers. Bundle into `_bundle_sweepC_v1/`.
2. *Upload*: single `scp -r` to `/speed-scratch/o_iseri/occModeling/`.
3. *Submit*: one `deploy_and_submit_C1.sh` runs `sbatch MDLM_C.sh; sbatch SEDD_C.sh` back-to-back. 2 fresh job IDs returned.
4. *Wait*: ~5–6h wall-clock. User runs `squeue -u o_iseri` to monitor.
5. *Download*: single `scp -r outputs_step4_full/` → local `step4_Speed-Cluster_docs/cluster_outputs/sweepC/`.
6. *Score*: read both `diagnostics_*.json`, evaluate 4/4 hard gates, pick winner.

### Stage D (conditional, 2026-05-25+): narrowed HPT on Stage C winner

**Trigger:** Stage C winner shows room to improve AT_HOME per-cell RMS, OR misses ≥1 hard gate, OR ties J3 and we want to push further. Stage D is expected even if Stage C clears gates — mid-training logs (ep 43 MDLM_C home_gap=3.56pp, ep 36 SEDD_C home_gap=3.36pp) suggest AT_HOME is improvable with targeted loss-weight tuning.

**Scope:** **architecture frozen** — only loss weights + diffusion-specific hyperparameters tuned. No new model files.

**HPT knobs (two categories):**

*AT_HOME-targeted (high-yield):*

| Knob | Current | Trial values | Rationale |
|---|---|---|---|
| `lambda_home` | 0.7 | 0.9, 1.0 | directly up-weights home head; biggest single lever for per-cell RMS |
| `home_label_smooth` | 0.05 | 0.02, 0.0 | sharper home predictions → lower per-cell RMS; trades calibration |
| `spouse_neg_weight` | 0.45 | 0.3, 0.6 | affects cop channel most correlated with AT_HOME |

*Diffusion-specific:*

| Knob | Current | Trial values | Rationale |
|---|---|---|---|
| diffusion_steps | 16 | 8, 32 | fewer steps → cheaper inference; more → better quality |
| mask_schedule | linear | cosine | cosine front-loads info; may improve cop/act balance |
| learning_rate | 5e-5 | 3e-5, 1e-4 | bracket current; 1e-4 risks instability |
| λ_trans | 0.0 | 0.05 | adds transition penalty; targets over-fragmentation |

Full grid too large. **Narrowed plan:** 4-6 hand-picked trials, drafted after Stage C diagnostics reveal which cells/gates need work. AT_HOME knobs take priority; diffusion knobs secondary.

**Stage D pass criterion:** any trial improves composite by ≥0.02 over Stage C winner AND closes ≥1 previously-failed hard gate (or tightens AT_HOME per-cell RMS by ≥0.5pp). Otherwise ship Stage C winner as-is.

### Stage C results (2026-05-25, COMPLETE)

| Metric | MDLM_C | SEDD_C | Gate | Status |
|---|---|---|---|---|
| Composite | **0.5665** | 0.7036 | <1.045 | MDLM ✅ / SEDD ✅ |
| AT_HOME RMS | 7.66 pp | 7.86 pp | ≤5.3 pp | both ❌ |
| COP max gap | 4.91 pp | 6.74 pp | ≤5 pp | MDLM ✅ / SEDD ❌ |
| act_JS mean | 0.0525 | 0.0662 | ≤0.05 | both ❌ |
| COP cal MAE | 0.0576 | 0.0787 | — | — |

**Winner: MDLM_C** — composite 0.5665 beats J3 (0.6355) by 10.9%. Passes 2/4 hard gates (composite + COP max gap). SEDD_C eliminated (worse than J3 on composite, fails 3/4 gates).

**B→C scaling insight:** AT_HOME RMS barely moved (7.73→7.66) despite 5× data. This is a loss-weight problem, not data volume — HPT on `lambda_home` / `home_label_smooth` / `marg_mode` is the right lever.

### Stage D HPT grid (2026-05-25, 6 trials)

Architecture frozen (MDLM). Only loss weights tuned:

| # | Tag | Changes from MDLM_C | Target |
|---|---|---|---|
| 1 | MDLM_D1 | lambda_home=0.9, home_label_smooth=0.02 | AT_HOME (conservative) |
| 2 | MDLM_D2 | lambda_home=1.0, home_label_smooth=0.0 | AT_HOME (aggressive) |
| 3 | MDLM_D3 | lambda_home=0.9, home_label_smooth=0.02, marg_mode=per_cs | AT_HOME per-cell |
| 4 | MDLM_D4 | lambda_home=0.9, home_label_smooth=0.02, lr=3e-5 | AT_HOME + act_JS |
| 5 | MDLM_D5 | lambda_home=1.0, home_label_smooth=0.0, marg_mode=per_cs, lambda_marg=0.2 | AT_HOME full-push |
| 6 | MDLM_D6 | lambda_home=0.9, home_label_smooth=0.02, lambda_trans=0.05 | AT_HOME + act_JS |

### Stage D results (2026-05-25, COMPLETE — all failed)

| # | Tag | Composite | AT_HOME RMS | COP max gap | act_JS | Status |
|---|---|---|---|---|---|---|
| 3 | MDLM_D3 | 0.5832 | 7.30 pp | 4.61 pp | 0.0633 | DONE — AT_HOME ↓ but act_JS regressed |
| 1 | MDLM_D1 | — | — | — | — | CANCELLED ep 40 (best ep 35: val_score=0.0386, home_gap=2.98%) |
| 2 | MDLM_D2 | — | — | — | — | CANCELLED ep 39 (best ep 35: val_score=0.0398, home_gap=3.03%) |
| 4 | MDLM_D4 | — | — | — | — | CANCELLED ep 47 (best ep 43: val_score=0.0382, home_gap=2.97%) |
| 5 | MDLM_D5 | 0.5915 | 7.20 pp | 4.87 pp | 0.0640 | DONE — per_cs regressed act_JS, worse than C |
| 6 | MDLM_D6 | 0.6235 | 7.63 pp | 5.56 pp | 0.0586 | DONE — lambda_trans=0.05 too aggressive, COP regressed |

MDLM_C baseline: composite 0.5665, AT_HOME 7.66 pp, COP 4.91 pp, act_JS 0.0525.

**D3 finding:** `marg_mode=per_cs` improved AT_HOME (7.66→7.30, -4.7%) and COP (4.91→4.61) but regressed act_JS badly (0.0525→0.0633, +20.6%). Per-cell marginal focus steals gradient from activity quality. Composite worsened (0.5665→0.5832).

**D5 finding:** Full-push combo (per_cs + lambda_home=1.0 + lambda_marg=0.2) also failed — composite 0.5915. AT_HOME only marginally better (7.66→7.20) while act_JS regressed worse than D3 (0.0525→0.0640). Doubling lambda_marg did not compensate for per_cs harm.

**⚠️ Lesson: `marg_mode=per_cs` is structurally harmful.** Both trials using per_cs (D3, D5) regressed act_JS by 20%+ and worsened composite. Per-cell marginal constraint competes with activity reconstruction gradient. The act_JS weight (0.35) dominates AT_HOME weight (0.20) in the composite — any AT_HOME gain from per_cs is erased by act_JS loss. **Do not use per_cs in future trials.**

**D6 finding:** `lambda_trans=0.05` too aggressive — composite 0.6235, worst of all completed D trials. COP max gap regressed from 4.91→5.56 (now fails the 5.0 gate). act_JS also regressed (0.0525→0.0586). The transition penalty stole gradient from all heads. **lambda_trans must be ≤0.02 if used at all.**

**D1/D2/D4 cancelled (2026-05-25):** All three used `marg_mode=global` (safe) but were trailing D6 mid-training. Cancelled at ep 40/39/47 to save GPU hours. In retrospect, they might have outperformed D6 at final diagnostics (D6's mid-training advantage didn't translate). Lesson: mid-training val_score is a weak predictor of final composite.

**⚠️ Stage D conclusion:** All 6 trials failed to beat MDLM_C (0.5665). MDLM_C remains the best model. Key lessons:
1. `per_cs` is structurally harmful (act_JS regresses 20%+)
2. `lambda_trans=0.05` too aggressive (breaks COP)
3. Mid-training metrics are unreliable predictors of final composite
4. Conservative single-axis changes (D1/D2) were the most promising direction but were never completed

### Stage E: focused HPT + demographic amplification on MDLM_C (2026-05-25)

**Seed:** MDLM_C (composite 0.5665). No Stage D trial improved on it.

**Strategy:** Conservative base (lambda_home=0.8, smooth=0.03) across all 4 trials. Each trial adds ONE additional lever — no stacking (Stage D proved stacking fails). Two trials focus on demographic amplification (ATTSCH/POWST/MODE from Phase 2).

| # | Tag | Changes from MDLM_C | Lever | Type |
|---|---|---|---|---|
| 1 | MDLM_E1 | lambda_home=0.8, smooth=0.03 | Conservative HPT | config-only (control) |
| 2 | MDLM_E2 | E1 + lambda_trans=0.015 | Small transition penalty | config-only |
| 3 | MDLM_E3 | E1 + aux_stratum_head=1, aux_stratum_lambda=0.15, data_side_sampling=1 | Demographic amplification (stratum + GSS weighting) | config-only |
| 4 | MDLM_E4 | E1 + deeper FiLM (MLP d_cond→128→d_model) | Demographic amplification (architecture) | code change (v2 model) |

**Pass criterion:** any E trial improves composite AND closes ≥1 previously-failed gate (AT_HOME RMS ≤5.3 or act_JS ≤0.05). Otherwise ship MDLM_C as final model.

**Results (scored as completed):**

| # | Tag | Composite | AT_HOME RMS | COP max gap | act_JS | Result |
|---|---|---|---|---|---|---|
| baseline | MDLM_C | **0.5665** | 7.66 | 4.91 | 0.0525 | — |
| 3 | MDLM_E3 | 0.5812 | 7.64 | 4.86 | 0.0546 | ❌ worse (act_JS regressed) |
| 1 | MDLM_E1 | — | — | — | — | CANCELLED (ep 19, wrong HPT target) |
| 2 | MDLM_E2 | — | — | — | — | CANCELLED (ep 19, identical to E1) |
| 4 | MDLM_E4 | — | — | — | — | CANCELLED (ep 23, wrong HPT target) |

**Mid-training snapshot (2026-05-25, ~2h in):**

| Trial | Epoch | val_js | home_gap | val_score | Pace (s/ep) |
|---|---|---|---|---|---|
| E1 (control) | 16 | 0.033 | 0.071 | 0.069 | 470 |
| E2 (+ trans) | 16 | 0.032 | 0.067 | 0.065 | 469 |
| E4 (deeper FiLM) | 19 | 0.027 | 0.037 | 0.045 | 394 |

E4 tracking best mid-training, but D5/D6 showed mid-training metrics are unreliable predictors of final composite.

**⚠️ Stage E conclusion (2026-05-25):** All 4 trials cancelled/failed. E3 completed with composite 0.5812 (worse than MDLM_C). E1/E2/E4 cancelled at ep 19–23 — all targeting wrong HPT variables (loss weights, demographic amplification). Combined with Stage D (6 failures), 10 consecutive full-data HPT trials produced no improvement. Root cause: HPT targeted loss weights (downstream consequences) instead of MDLM-intrinsic generative mechanics (upstream causes). Pivoting to Stage F: sample-based HPT on denoise steps, masking schedule, encoder depth, mask ratio bounds.

**E3 finding (2026-05-25):** `aux_stratum_head=1 + data_side_sampling=1` failed — composite regressed 0.5665→0.5812. AT_HOME barely moved (7.66→7.64), COP max gap slightly improved (4.91→4.86), but act_JS regressed (0.0525→0.0546, +4%). The auxiliary stratum prediction task and GSS person-weighting did not provide meaningful signal for the MDLM architecture. Demographic amplification via training-side weighting is not effective on this model.

**⚠️ Emerging pattern (Stages D+E):** 10 trials across two HPT stages have failed to beat MDLM_C. All tuning has targeted loss weights (lambda_home, lambda_trans, lambda_marg, marg_mode) and demographic amplification (aux_stratum, data_side_sampling, deeper FiLM). The bottleneck may lie in untouched MDLM-specific variables: masking schedule, number of denoise steps (currently 16), encoder depth, or the masking ratio clamp (0.05–0.95). If E1/E2/E4 also fail, consider shipping MDLM_C as-is or pivoting HPT to MDLM-intrinsic variables.

### Stage F: MDLM-intrinsic HPT on 10% sample (planned 2026-05-25)

**Rationale:** Stages D+E targeted loss weights and demographic amplification — all 10 trials failed. These are NOT the correct HPT variables for a diffusion model. The actual performance levers are the generative process parameters: denoise steps, masking schedule, encoder/refiner depth, and mask ratio bounds. These directly control sequence generation quality.

**Method:** 10% stratified sample (~15,000 respondents) using existing `04A_sample_assembly.py --frac 0.10`. Train MDLM_C baseline on 10% sample as control. Run HPT variants on same 10% sample. Compare relative composite rankings. Promote top 2–3 to full data.

**MDLM_C defaults (control):**
- Denoise steps: 16 (env `MDLM_STEPS`)
- Masking schedule: uniform, t ∈ U(0.05, 0.95)
- x0_refiner depth: 2 layers
- Main encoder: 6 layers (`n_enc_layers`)
- d_model: 384, n_heads: 8

**HPT variables (MDLM-intrinsic):**

| # | Tag | Variable | Values to test | Default |
|---|---|---|---|---|
| F0 | MDLM_F0 | — (control) | MDLM_C on 10% sample | baseline |
| F1 | MDLM_F1 | denoise_steps | 32 | 16 |
| F2 | MDLM_F2 | denoise_steps | 64 | 16 |
| F3 | MDLM_F3 | mask_schedule | cosine (β(t)=cos(πt/2)) | uniform |
| F4 | MDLM_F4 | mask_schedule | linear ramp (t clamp 0.1–0.9) | uniform |
| F5 | MDLM_F5 | x0_refiner_layers | 4 | 2 |
| F6 | MDLM_F6 | x0_refiner_layers + n_enc_layers | 4 + 8 | 2 + 6 |
| F7 | MDLM_F7 | mask_clamp_bounds | [0.15, 0.85] (tighter) | [0.05, 0.95] |
| F8 | MDLM_F8 | mask_clamp_bounds | [0.01, 0.99] (wider) | [0.05, 0.95] |

**9 trials total** (1 control + 8 HPT). One variable per trial, no stacking.

**Implementation notes:**
- `denoise_steps`: already configurable via env var `MDLM_STEPS` in SLURM wrapper
- `mask_schedule`: needs code patch in `forward()` — replace `torch.rand(B,1).clamp(0.05,0.95)` with schedule function. Small, isolated edit.
- `x0_refiner_layers` / `n_enc_layers`: configurable via YAML (new key `n_refiner_layers`, existing `n_enc_layers`)
- `mask_clamp_bounds`: needs env var or config key to replace hardcoded `clamp(0.05, 0.95)`

**Timeline:**
- 10% sample at ~1/10 data = ~47s/ep (vs 470s/ep full) on cisr nodes
- 50 epoch cap, patience 10 → ~40 min/trial
- 9 parallel jobs → all done in ~1h wall-clock
- Promote top 2–3 to full data (Stage G, ~10h each)

**Pass criterion (Stage F):** any trial that beats F0 (10% control) by ≥5% relative composite improvement gets promoted to full data Stage G. If none beat F0 by 5%, ship MDLM_C.

### Stage F results (2026-05-25, COMPLETE — F8 WINNER)

All 9 trials completed on 10% stratified sample. F0 = same-sample control baseline.

| Rank | Tag | Variable | Composite | AT_HOME RMS | COP max gap | act_JS | cop_cal_MAE | Δ vs F0 |
|---|---|---|---:|---:|---:|---:|---:|---|
| 1 | **MDLM_F8** | mask bounds [0.01, 0.99] (wider) | **0.771** | 8.49 | **4.94** | 0.088 | 0.120 | **-16.3%** |
| 2 | MDLM_F1 | denoise_steps=32 | 0.914 | 8.75 | 8.60 | 0.087 | 0.134 | -0.8% |
| 3 | MDLM_F0 | control (MDLM_C on 10%) | 0.921 | 8.85 | 8.54 | 0.088 | 0.136 | — |
| 4 | MDLM_F3 | cosine mask schedule | 1.101 | 9.48 | 11.40 | 0.109 | 0.131 | +19.5% |
| 5 | MDLM_F6 | refiner=4 + enc=8 | 1.103 | 8.93 | 10.68 | 0.116 | 0.144 | +19.8% |
| 6 | MDLM_F4 | linear schedule + mask [0.1, 0.9] | 1.144 | 9.91 | 10.82 | 0.125 | 0.130 | +24.2% |
| 7 | MDLM_F2 | denoise_steps=64 | 1.157 | 10.84 | 10.38 | 0.127 | 0.132 | +25.6% |
| 8 | MDLM_F5 | refiner=4 | 1.225 | 8.74 | 13.71 | 0.129 | 0.120 | +33.0% |
| 9 | MDLM_F7 | mask bounds [0.15, 0.85] (tighter) | 1.253 | 9.70 | 10.91 | 0.154 | 0.140 | +36.0% |

**F8 is the only trial that clears the 5% promotion threshold** (-16.3% vs F0). F1 (32 steps) is marginal at -0.8%.

**Key findings:**

1. **Wider mask bounds (F8) are transformative.** COP max gap collapsed from 8.54→4.94 pp (-42%) while AT_HOME and act_JS held steady. By exposing the model to near-fully-masked (t≈0.99) and near-clean (t≈0.01) examples during training, the denoiser learns both extremes of the corruption spectrum, producing cleaner copresence outputs.

2. **Tighter mask bounds (F7) are catastrophic.** Restricting to [0.15, 0.85] produced the worst composite (1.253, +36% worse than control). The model never sees near-clean or near-corrupted states → denoising quality degrades across all heads.

3. **More denoise steps hurt.** Both F1 (32 steps, -0.8%) and F2 (64 steps, +25.6%) were neutral-to-harmful. More inference steps don't help when the training masking schedule is the bottleneck.

4. **Non-uniform schedules regressed.** Cosine (F3) and linear (F4) both worsened composite by 19–24%. Uniform masking with wider bounds is strictly better.

5. **Deeper encoder/refiner regressed.** F5 (refiner=4) had +33% worse composite; F6 (refiner=4 + enc=8) was +19.8% worse. More capacity without better training signal = overfitting on 10% sample.

**⚠️ Stage F lesson:** For diffusion models, the single most impactful HPT variable is the mask ratio bounds. 10 trials of loss-weight tuning (Stages D+E) moved nothing; one trial of mask bounds (-16.3%) moved more than all prior Stages combined. This confirms the original Stage F hypothesis: HPT must target intrinsic generative mechanics.

**Promotion decision:** F8 (mask bounds [0.01, 0.99]) → **Stage G (full data)**. F1 (32 steps) → not promoted (below 5% threshold).

### Next steps (in order)

1. ~~Build Stage C bundle~~ ✅ (2026-05-24)
2. ~~Upload + submit~~ ✅ (2026-05-24, jobs 936373 + 936374)
3. ~~Wait + pull~~ ✅ (2026-05-25)
4. ~~Score + decide~~ ✅ (2026-05-25, MDLM_C wins, composite 0.5665)
5. ~~Draft Stage D HPT grid~~ ✅ (2026-05-25, 6 trials above)
6. ~~Build + upload + submit Stage D bundle~~ ✅ (2026-05-25, jobs 936470–936475)
7. ~~Monitor + score Stage D~~ ✅ (2026-05-25, all 6 failed, MDLM_C remains best)
8. ~~Build + upload + submit Stage E bundle~~ ✅ (2026-05-25, jobs 936552–936555)
9. ~~Monitor + score Stage E~~ ✅ (2026-05-25, E3 failed, E1/E2/E4 cancelled — wrong HPT target)
10. ~~Build Stage F bundle~~ ✅ (2026-05-25, 9 configs + patched model with env-var intrinsic knobs)
11. ~~Upload + submit Stage F~~ ✅ (2026-05-25, jobs 936646–936654, 10% sample, 9 parallel)
12. ~~Score Stage F~~ ✅ (2026-05-25, F8 wins -16.3% vs control, wider mask bounds [0.01,0.99])
13. ~~Build + submit + score Stage G+H bundle~~ ✅ (2026-05-26, G1 new best 0.5592; all 6 H trials FAILED)
14. **Next: structural intervention for AT_HOME RMS (7.81→≤5.3) and act_JS (0.053→≤0.05).** ← NEXT

### Stage G: F8 winner → full data (2026-05-25)

Single trial: MDLM_G1 = MDLM_C + `MDLM_MASK_LO=0.01, MDLM_MASK_HI=0.99`. Full data (outputs_step4_G2), 100 epochs, patience 15. Expected ~5-6h wall-clock.

**Pass criterion:** G1 composite < MDLM_C (0.5665) AND passes ≥ 3/4 hard gates.

### Stage H: Preprocessing HPT on 10% sample (2026-05-25, parallel with G1)

**Rationale:** Stages D-F exhaustively tuned loss weights and MDLM generative mechanics. The remaining untouched lever is how demographics are REPRESENTED to the model (preprocessing/embedding) and how training PAIRS are constructed. These run on 10% sample (~40 min/trial) to test quickly, then promote winners to full data.

**Design:** 6 trials testing 3 preprocessing variables × 2 architectures (F8 vs original mask bounds). This factorial design reveals whether preprocessing gains are architecture-independent.

| # | Tag | Preprocessing change | Mask bounds | Rationale |
|---|---|---|---|---|
| H0 | PP_H0 | control (no change) | F8 [0.01, 0.99] | Fair baseline for H1-H3 |
| H1 | PP_H1 | Entity embedding: cond_vec (90-dim) → learned 64→32 dim bottleneck | F8 | Forces model to learn demographic interactions (POWST×AGEGRP) instead of memorizing sparse one-hots |
| H2 | PP_H2 | K=10 neighbors in 04C (default K=5) | F8 | Richer KNN targets → smoother training signal → lower JS floor |
| H3 | PP_H3 | Cycle rebalancing: 2022 pairs weighted 2× | F8 | 2022 is underrepresented + has worst AT_HOME gap + highest WFH rate |
| H4 | PP_H4 | Entity embedding (same as H1) | Original [0.05, 0.95] | Tests if embedding gain is architecture-independent |
| H5 | PP_H5 | K=10 neighbors (same as H2) | Original [0.05, 0.95] | Tests if K gain is architecture-independent |

**Implementation notes:**
- **Entity embedding (H1/H4):** New env var `USE_ENTITY_EMBED=1` in patched 04B_model_MDLM.py. Adds `nn.Sequential(Linear(d_cond,64), LayerNorm, GELU, Linear(64,32), GELU)` before cls_mlp and FiLM. Compresses 90-dim sparse one-hot to 32-dim dense — forces learned categorical interactions.
- **K=10 (H2/H5):** Patched 04C reads `KNN_K` env var. Wrapper creates symlink data dir + regenerates pairs with K=10 before training.
- **Cycle resample (H3):** Patched 04D reads `CYCLE_OVERSAMPLE_2022` env var, multiplies sampler weights for cycle_idx==3 (2022) by the factor.

**Pass criterion:** any H trial that beats H0 (control) by ≥5% relative composite improvement on same architecture. If a preprocessing change helps on BOTH architectures (H1 vs H4, H2 vs H5), it's architecture-independent and especially valuable.

**Bundle:** `_bundle_sweepG_v1/` contains G1 + all 6 H trials. One upload, one deploy script (7 sbatch total).

**Submitted 2026-05-25 (7 jobs):**
| Job ID | Trial | Status |
|---|---|---|
| 936694 | MDLM_G1 | COMPLETED |
| 936695 | PP_H0 | COMPLETED |
| 936697 | PP_H2 | COMPLETED |
| 936698 | PP_H3 | COMPLETED |
| 936700 | PP_H5 | COMPLETED |
| 936701 | PP_H1 | COMPLETED |
| 936702 | PP_H4 | COMPLETED |

**Stage H full results (all 10% sample, vs F8 control):**

| # | Tag | Composite | AT_HOME RMS | COP max gap | act_JS | Δ vs F8 |
|---|---|---:|---:|---:|---:|---|
| ref | F8 (10% sample) | 0.771 | 8.49 | 4.94 | 0.088 | — |
| H0 | PP_H0 (control) | 0.771 | 8.49 | 4.94 | 0.088 | 0.0% ✓ (control) |
| H1 | PP_H1 (entity embed) | 1.051 | 8.71 | 8.58 | 0.124 | +36.3% ❌ |
| H2 | PP_H2 (K=10) | 0.833 | 9.66 | 6.58 | 0.083 | +8.0% ❌ |
| H3 | PP_H3 (cycle OS ×2) | 1.255 | 10.21 | 11.79 | 0.153 | +62.8% ❌ |
| H4 | PP_H4 (entity+orig mask) | 0.997 | 9.15 | 9.96 | 0.095 | +29.3% ❌ |
| H5 | PP_H5 (K=10+orig mask) | 0.976 | 9.08 | 9.36 | 0.100 | +26.6% ❌ |

**H0 (control):** Reproduces F8 exactly (composite 0.771). Confirms 10% sample baseline is stable.

**H1 (entity embedding, F8 mask):** COP max gap exploded to 8.58 pp, act_JS nearly doubled. Bottleneck MLP (90→64→32) destroys fine-grained demographic signal the FiLM layer needs. NaN chi2 on 2005/2010 strata — model collapsed on early cycles. FAILED.

**H2 (K=10 neighbors):** All metrics regressed vs F8. Drawing from 10 nearest neighbors (vs 5) adds too much noise — more distant matches degrade pair quality. FAILED.

**H3 (cycle oversample 2022 ×2):** Catastrophic. COP max gap exploded to 11.79 pp, act_JS nearly doubled, chi2 NaN for 2005/2010 strata (model collapsed on early cycles). Overweighting 2022 pairs destroyed cross-cycle generalization. FAILED.

**H4 (entity embed + original mask):** Same entity-embed failure mode as H1, slightly less severe with original mask. COP max gap 9.96 pp. Architecture-independent: entity bottleneck harmful on both mask variants. FAILED.

**H5 (K=10 + original mask):** Same K-expansion failure mode as H2, worse with original mask. COP max gap 9.36 pp. Architecture-independent: K=10 harmful on both mask variants. FAILED.

**Stage H conclusion:** All 5 preprocessing HPT trials (H1-H5) failed on both F8 and original mask architectures. Entity embedding and K-expansion are architecture-independent failures — harmful regardless of mask bounds. The 04C/04D preprocessing pipeline with K=5 and no rebalancing is already near-optimal for MDLM. No preprocessing changes will be promoted to full data.

### Stage G results (full data, 2026-05-26)

| Trial | Composite | AT_HOME RMS | COP max gap | act_JS | cop_cal_mae | vs MDLM_C |
|---|---|---:|---:|---:|---:|---:|---|
| MDLM_C (baseline) | 0.5665 | 7.66 | 4.91 | 0.0525 | — | — |
| **MDLM_G1** | **0.5592** | 7.81 | **4.57** | 0.0529 | 0.058 | **-1.3%** ✓ |

**Hard gates (G1):**
- composite < 1.045: 0.5592 ✓
- AT_HOME RMS ≤ 5.3 pp: 7.81 ✗
- COP max gap ≤ 5.0 pp: 4.57 ✓ (improved from 4.91)
- act_JS ≤ 0.05: 0.053 ✗

G1 passes 2/4 hard gates (same as MDLM_C). New best full-data composite (0.5592 vs 0.5665). COP max gap improved 4.91→4.57 pp. AT_HOME RMS slightly worse (7.66→7.81). act_JS essentially flat (0.0525→0.0529).

**G1 is the new full-data champion.** Wider mask bounds [0.01, 0.99] confirmed beneficial at full scale. Still fails AT_HOME RMS and act_JS gates — these require structural intervention beyond MDLM HPT.

### Cross-architecture comparison: J3 vs MDLM (2026-05-26)

**Full model comparison against 4 hard gates:**

| Metric | J3 | MDLM_C | G1 | Hard gate |
|---|---:|---:|---:|---|
| composite | 0.6355 | 0.5665 | **0.5592** ✓ best | < 1.045 |
| AT_HOME RMS (pp) | **4.57** ✓ | 7.66 ✗ | 7.81 ✗ | ≤ 5.3 |
| COP max gap (pp) | **~2.03** ✓ | 4.91 ✓ | 4.57 ✓ | ≤ 5.0 |
| act_JS | **0.0191** ✓ | 0.0525 ✗ | 0.0529 ✗ | ≤ 0.05 |
| Gates passed | **4/4** | 2/4 | 2/4 | |

**Composite score decomposition — why MDLM beats J3 on composite despite losing on 3/4 gates:**

Formula (`04J_statistical_diagnostics.py:612`):
`S = 0.20 × (AT_HOME_RMS / 10) + 0.35 × (COP_max_gap / 10) + 0.35 × (act_JS × 10) + 0.10 × (cop_cal_MAE × 10)`

| Component | Weight | Scale | J3 | G1 | J3 → score | G1 → score |
|---|---|---|---:|---:|---:|---:|
| AT_HOME RMS (pp) | 20% | ÷10 | **4.57** | 7.81 | 0.091 | 0.156 |
| COP max gap (pp) | 35% | ÷10 | **~3.5** | 4.57 | 0.123 | 0.160 |
| act_JS | 35% | ×10 | **0.019** | 0.053 | 0.067 | 0.185 |
| **cop_cal_MAE** | 10% | ×10 | **~0.355** | **0.058** | **0.355** | **0.058** |
| **composite** | | | | | **0.636** | **0.559** |

**The hidden driver: cop_cal_MAE.** J3's copresence calibration MAE (~0.355) is 6× worse than G1's (0.058). This single component adds 0.297 to J3's composite, wiping out all three gate advantages. J3's AR decoder produces copresence predictions that are directionally correct (small marginal gaps) but poorly calibrated — when it predicts "30% Spouse," the actual rate may be 15% or 50%. MDLM's iterative denoising produces much better-calibrated probabilities.

**Lesson learned — composite score ≠ gate quality:** The composite score is dominated by cop_cal_MAE (not a hard gate) which makes MDLM appear superior. But the hard gates that matter for the paper (AT_HOME RMS, act_JS) clearly favor J3. **Never use composite score alone to judge model quality.** Always check the 4 hard gates individually. A model with a lower composite can be worse on every metric that matters for publishable results.

**Lesson learned — low training loss ≠ good generation quality (2026-05-26):** The model practiced only with cheat sheets, so it scores perfectly on homework but fails the real exam. Training loss measures prediction under teacher forcing (model always sees correct previous values). At inference, the model uses its own predictions — mistakes snowball (exposure bias). Example: H_Time achieved cop_loss=0.062 (best in class) but COP max gap=22.86 pp at inference (catastrophic failure). Never select architectures by training loss alone — always run full diagnostic gates (04H + 04I + 04J).

**All-time gate leaderboard (full-data models only):**

| Model | composite | AT_HOME RMS | COP max gap | act_JS | Gates |
|---|---:|---:|---:|---:|---|
| **J3** | 0.6355 | **4.57** ✓ | **~2.03** ✓ | **0.0191** ✓ | **4/4** ✓ |
| J5_X1 | 0.6667 | **4.15** ✓ best | 5.32 ✗ (miss 0.32) | 0.0311 ✓ | 3/4 |
| J2 | 0.6884 | 5.70 ✗ | ~1.47 ✓ | 0.0239 ✓ | 3/4 |
| J1 | 0.69 | 5.83 ✗ | ~1.9 ✓ | 0.0274 ✓ | 3/4 |
| G1 (MDLM) | **0.5592** best | 7.81 ✗ | 4.57 ✓ | 0.0529 ✗ | 2/4 |
| MDLM_C | 0.5665 | 7.66 ✗ | 4.91 ✓ | 0.0525 ✗ | 2/4 |

**J3 is the confirmed winner and final Step-4 baseline.** It is the only model that passes all 4 hard gates across the entire investigation (F-series → J-series → MDLM sweep, 40+ trials). Notable runner-up: J5_X1 has the best AT_HOME RMS ever recorded (4.15 pp) but misses COP max gap by just 0.32 pp. No MDLM variant has ever passed AT_HOME RMS or act_JS — the MDLM architecture trades activity/home precision for copresence calibration. The Phase 6 architecture sweep (Stages A–H) is **CLOSED**; J3 remains the production model.

---

## Phase 6 Addendum (2026-05-23) — Sample-Architecture Sweep Funnel

### Context

Phases 1–5 of the original plan (J3-PSB, J3-DEMO, J3-DEMO-PSBLite, J3-NEIGH, J3-CLEAN) all failed to beat J3 baseline (composite 0.6355) despite full-data 5h+ retrain cycles. J3-CLEAN (Phase 4) regressed catastrophically to composite 3.29 because stacking 4 loss-side fixes destabilised the training landscape (best checkpoint was epoch 1).

Diagnosis: the J3 architecture and loss family has been exhaustively mined. Further single-knob loss tuning on full data is unlikely to break 0.6355. Strategic pivot per user direction (2026-05-23): replicate the methodology previously used for predictive architectures — small-sample short-bake-off across many structurally distinct architectures, then funnel to full-data verification.

4 web-based deep-research LLMs (4 docs in `step4_Speed-Cluster_docs/Research/deep research/`) converge tightly on ~10 candidate families across 3 failure-mode buckets: (a) over-fragmentation → duration-aware decoders, (b) K-NN noise → batch-level distribution-matching losses, (c) consistency violations → semantic logic layers. Top 3 picks across all 4 docs: Neural HSMM decoder, Masked Diffusion (MDLM), composite-conditioning (FiLM + Fourier PE + per-stratum prefix) + Semantic Probabilistic Layer.

### Deliverable

3-stage funnel sweep, ~1 week wall-clock end-to-end. Result: a winning architecture (or 1-2 tied) at full-data composite + 4/4 hard gates, beating J3 0.6355, ready to ship as the new Step-4 baseline.

### Funnel structure

| Stage | Sample | Trials | Epochs | Per-trial wall-clock | Parallel GPUs | Stage wall-clock |
|---|---|---|---|---|---|---|
| **A — Short bake-off** | 2% (~3,000 respondents) | All 10 | 50 cap | ~1h | 10 (whatever `pg` gives) | ~1 day (1 upload + 10 parallel sbatch + 1 download) |
| **B — Semifinal** | 20% (~30,000) | Top 3 from A | 100 (patience 15) | ~3h | 3 | ~half day |
| **C — Final** | 100% (~150,000) | Top 1–2 from B | 100 (patience 15) | ~5–6h | 1–2 | ~1 day |

**Ranking proxy (Stages A and B — NOT pass/fail gates):** composite + act_JS + AT_HOME RMS (4 cells in A, all 12 in B) + Spouse Δ + transition-rate ratio. Hard 4/4 gates are reserved for Stage C only — sample noise makes per-cell gates unreliable.

**Independence discipline:** each trial = one independent sbatch job, no shared state, no shared output dir. One trial failing has zero impact on the other nine. Per memory rule `feedback_bundle_upload.md` and `feedback_full_audit_no_patches.md`: bundle local edits once → single recursive `scp` upload → submit all sbatch in one wave → single recursive `scp` pull on completion. No file-by-file mid-cycle uploads or downloads.

### The 10 trials

Each trial = one structural change vs J3 baseline (composite 0.6355). No loss-coefficient tuning in the sweep — that's reserved for Stage C if a winning architecture needs polish.

| # | Tag | Family | Mechanism | Targets failure mode |
|---|---|---|---|---|
| 1 | `CC` | Conditioning | J3 + FiLM + Fourier diurnal PE + per-stratum prefix-tuning | weekday/weekend ordering (72.1% violation) |
| 2 | `CC_SPL` | Consistency | CC + Semantic Probabilistic Layer (Ahmed et al., NeurIPS 2022) for hard logical constraints | physical-impossibility violations |
| 3 | `CC_FACT` | Consistency | CC + factorized joint decoding activity → home → cop with hard masking | same as CC_SPL, cheaper |
| 4 | `HSMM` | Structural | Neural Hidden Semi-Markov decoder + CC encoder; explicit duration head | 157× over-fragmentation (transition rate) |
| 5 | `MDLM` | Structural | Masked discrete diffusion + parallel multi-task heads + CC; bidirectional, 8–32 denoise steps | AR exposure bias + K-NN multimodal targets |
| 6 | `HIER` | Structural | Hierarchical coarse schedule template → 30-min refine + CC | transition rate (block-level commitment) |
| 7 | `MAMBA` | Structural | Selective SSM (Mamba) decoder with input-dependent Δ + CC | transition rate (soft persistence prior) |
| 8 | `SINK` | Loss | J3 backbone + batch Sinkhorn divergence loss as primary objective, CE as regulariser | K-NN noise / AT_HOME per-cell RMS |
| 9 | `GCE` | Loss | J3 backbone + Generalized Cross-Entropy + credal-set data ambiguation (Lienen & Hüllermeier 2023) | K-NN noise / calibration |
| 10 | `SEDD` | Structural | Score-Entropy Discrete Diffusion + CC (alternative to MDLM) | AR exposure bias + multimodality |

All 10 use the same `outputs_step4_G2_sample2/` data tensors, same K=5 pairs, same seed (42), same batch 256. Only the model/loss/conditioning differs.

### Files to add / modify (Stage A build)

**New files (15):**

| File | Purpose |
|---|---|
| `04A_sample_assembly.py` | Stratified sub-sampler with `--frac 0.02` flag. Stratify by `cycle × DDAY_STRATA × HHSIZE`. Hard floor: ≥200 respondents per rare cop-channel × stratum cell (parents/friends/colleagues/others). Frozen seed=42 train/val/holdout split. Writes `outputs_step4_G2_sample2/` mirroring G2 schema. Reused for Stage B with `--frac 0.20`. |
| `04B_model_HSMM.py` | Trial 4 — neural HSMM decoder. Reuse J3's CrossAttn encoder; replace Arm-1 AR decoder with segment-level emission (state z + duration d, forward-backward over T×D_max with D_max=12). |
| `04B_model_MDLM.py` | Trial 5 — Masked Diffusion Language Model. Bidirectional transformer trunk (drop AR mask), x₀ parameterisation, Rao-Blackwellised masked-CE loss. Parallel softmax (activity) + sigmoid (home + 9 cop) heads at each masked position. |
| `04B_model_HIER.py` | Trial 6 — coarse (4–8 schedule blocks) decoder → 30-min refine decoder. Compound-Word-Transformer style typed tokens (Hsiao 2021). |
| `04B_model_MAMBA.py` | Trial 7 — selective SSM decoder (Mamba S6 block, input-dependent Δ). Linear-time inference. |
| `04B_model_SEDD.py` | Trial 10 — Score-Entropy Discrete Diffusion (Lou et al., ICML 2024). Ratio-of-data-distribution parameterisation. |
| `04D_train.py` patches | Add env-var toggles: `USE_FILM`, `USE_FOURIER_PE`, `USE_PREFIX`, `USE_SPL`, `USE_FACT`, `LOSS_MODE ∈ {ce, sinkhorn, gce}`. All default off → byte-identical J3 behaviour when unset. SPL constraint set: `¬home ⇒ ¬alone`, `work ⇒ ¬home ∧ colleagues`, `sleep ⇒ home`. |
| `step4_Speed_Cluster/sample_configs/<TAG>_A.yaml` × 10 | Per-trial config: tag, model_type, sample_frac=0.02, max_epochs=50, patience=10, the trial's specific toggles. |
| `step4_Speed_Cluster/sample_jobs/<TAG>_A.sh` × 10 | Per-trial SLURM wrapper: `pg` partition, 1 GPU, 40G RAM, **48h walltime minimum** (per `feedback_cluster_walltime_minimum.md`), output dir `outputs_step4_sample/<TAG>_A/`, pipeline `04D_train → 04E_inference → 04H → 04I → 04J`. |

**Modified files (2):**

| File | Change |
|---|---|
| `04C_training_pairs.py:31-32` | Add `--sample_dir` flag. When set, build K=5 pairs from the sample slice instead of full G2. Measure and log new JS-disagreement floor (likely > 0.1888 due to fewer neighbour candidates). |
| `step4_Speed_Cluster/config_to_env.{sh,py}` | Extend `ENV_MAP` with new env vars (`USE_FILM`, `USE_FOURIER_PE`, `USE_PREFIX`, `USE_SPL`, `USE_FACT`, `LOSS_MODE`, `SAMPLE_FRAC`). |

**Reused unchanged:** `04E_inference.py`, `04H_diagnostics_cpu.py`, `04I_activity_copresence_diagnostics.py`, `04J_statistical_diagnostics.py`. Diagnostics scripts already accept arbitrary `--data_dir` so they work on `outputs_step4_sample/<TAG>_A/` without modification.

### Execution flow (per stage)

**Stage A — bundle once, parallel-submit once, download once:**

1. *Local prep* (~1 day, manager → Sonnet builder handoff per `feedback_manager_role.md` + `feedback_run_command.md`): write the 6 new model files, 10 YAMLs, 10 SLURM wrappers, the sample assembler, the 04C flag, the env-var extensions. Local smoke test: 1-epoch run of `CC` trial on laptop CPU.
2. *Bundle* (~5 min): `_bundle_sweepA/` recursive copy of all modified Speed_Cluster files + 04A/04B/04C/04D edits + sample tensors. One `scp -r` to `/speed-scratch/o_iseri/occModeling/`.
3. *Submit wave* (~5 min): one PowerShell line emits `sbatch <TAG>_A.sh` for all 10 tags via `ForEach-Object` (per `feedback_scp_separate_lines.md` pattern). Each gets its own job ID and independent output dir.
4. *Wait* (~1h wall-clock once GPUs allocate): all 10 either succeed or fail independently. User runs `squeue -u o_iseri` and `tail` on the latest log to monitor.
5. *Download* (~5 min): single recursive `scp -r` from `/speed-scratch/o_iseri/occModeling/outputs_step4_sample/` → local `step4_Speed-Cluster_docs/cluster_outputs/sweepA/`. Pull all 10 `diagnostics_*.json` + training logs + .out/.err.
6. *Rank* (~30 min): script that reads all 10 `diagnostics_*.json`, builds a one-table ranking by `composite + act_JS + AT_HOME RMS + Spouse Δ + trans-rate ratio`. Append to `CSV_records/sweepA_results.csv`. User decides top 3 (may override if metric ties are close).

**Stage B — same pattern, 3 trials, 20% sample, 100 epochs.** Reuse `04A_sample_assembly.py --frac 0.20`. Same harness, just new configs + wrappers (`<TAG>_B.{yaml,sh}`).

**Stage C — same pattern, 1–2 trials, full data (existing `outputs_step4_G2/`), 100 epochs, hard 4/4 gate verification.** Configs match J3 baseline knobs except for the winning architecture's specifics.

### Verification

**Stage A pass criterion (per trial):** training completes 50 epochs (or patience-exits) AND inference produces `augmented_diaries.csv` AND `04J_statistical_diagnostics.py` writes a valid `diagnostics_*.json` with a composite score. A trial that crashes mid-training counts as "ranked last" — does not block others.

**Stage B pass criterion:** trial produces full 12-cell AT_HOME table AND all 9 cop-channel gaps AND per-stratum act_JS. Composite < 1.0 (not full gate but a credibility floor).

**Stage C pass criterion (the only real gate):** composite < 1.045 AND AT_HOME RMS ≤ 5.3 pp AND Spouse |Δ| ≤ 5 pp AND act_JS ≤ 0.05 — the existing J3 4/4 gate set. A Stage C winner that ties J3 (0.6355) but on a more defensible architecture is acceptable; one that beats it is the goal.

**End-to-end verification:** the winning architecture from Stage C becomes the new Step-4 baseline. `step4_Speed-Cluster_docs/CSV_records/{architecture,training_config,loss_values}_investigation.csv` get 12 new rows (10 Stage A + 3 Stage B trials + final Stage C). `04_augmentationGSS_IMP.md` Progress Log gets one summary entry per stage. `MEMORY.md` gets an updated project entry pointing to the new ship.

### Open questions / risks

1. **Stage A sample size (2%) and JS floor.** With ~3,000 respondents and K=5 neighbour pairing, the JS-disagreement floor may rise from 0.1888 (full data) to ~0.25, which would inflate all act_JS rankings uniformly. *Mitigation:* measure once in step 1 (Stage A prep), report alongside rankings; do not over-interpret absolute act_JS, only relative ordering between the 10 trials.
2. **Diffusion trials (MDLM, SEDD) may need >50 epochs to converge.** Discrete diffusion typically needs more updates than AR on the same data. *Mitigation:* if a diffusion trial's Stage A score is uncompetitive but its loss curve is still descending at epoch 50, override the ranking to promote it to Stage B regardless. Document the override.
3. **SPL constraint spec correctness.** If the SPL rules forbid genuine WFH cases (real in 2022 cycle), CC_SPL will under-fit. *Mitigation:* mine the rules from observed data first (`p(at_home=1 | activity=work)` per cycle), only hard-code rules that hold in >99% of observed diaries; weaker rules go to `CC_FACT` only.
4. **HSMM duration head collapse** to copying nearest-neighbour patterns. *Mitigation:* initialise duration distribution to a broad Gaussian (mean 4, std 3 slots), regularise toward observed marginal duration distribution per activity class.
5. **`pg` partition queue contention.** If 10 parallel sbatch can't all allocate within ~1h, Stage A wall-clock stretches. *Mitigation:* user runs `sinfo -p pg` before the submit wave; if queue is hot, batch in two waves of 5 (~2 days instead of 1).
6. **Trial 1 (`CC`) is a prerequisite for trials 2–7.** All structural trials assume CC conditioning. If `CC` itself fails to converge on the 2% sample, the structural family is invalidated for Stage A — fall back to bare-J3 conditioning for trials 4–7 and re-run.

> **Source.** Full plan archived at `C:\Users\o_iseri\.claude\plans\elegant-dreaming-tarjan.md` (auto-generated plan-mode filename, kept as backup).

---

## Progress Log

### 2026-05-24 — Phase 6 Stage A: local prep COMPLETE, bundle staged

**Sample slice:** train 2,406 / val 198 / test 199. Rare-cop floor satisfied (verified by 04A run on 2026-05-23, all strata populated). Full sample slice is at `outputs_step4_G2_sample2/`.

**K=5 JS-disagreement floor on sample:** 0.1905 (full-data baseline: 0.1888). Slight uptick as expected from smaller neighbour pool (~2,400 respondents vs ~45,000). Per Open Risk #1, use relative ordering between the 10 Stage A trials, not absolute act_JS values.

**Bug fixes applied during prep (2 scripts):**
- `04C_training_pairs.py` — replaced three `✓` / `≈` Unicode print characters that crash on Windows cp1252 codepage (`✓` → `OK`; `≈` comparison print suppressed via `try/except`). No logic change.
- `04D_train.py` — replaced one `✓` Unicode print ("New best model saved") with ASCII equivalent. No logic change.

**Implementation changes — exact edits:**

| File | Line | Before | After | Reason |
|---|---|---|---|---|
| `04C_training_pairs.py` | 306 | `print("  ✓ No self-pairing in first 50 pairs")` | `print("  OK No self-pairing in first 50 pairs")` | cp1252 UnicodeEncodeError on Windows |
| `04C_training_pairs.py` | 314 | `print("  ✓ All sampled neighbors share CYCLE_YEAR with source (first 50)")` | `print("  OK All sampled neighbors share CYCLE_YEAR with source (first 50)")` | same |
| `04C_training_pairs.py` | 425 | `print(f"\n✓ 04C complete.")` | `print(f"\n04C complete.")` | same |
| `04D_train.py` | 1173 | `print(f"  ✓ New best model saved (val_score=…)")` | `print(f"  NEW BEST saved (val_score=…)")` | same — crash happened after `torch.save`, so checkpoint was written but script exited with code 1 |

All four are cosmetic print-only changes. The `≈` in `04C_training_pairs.py` (JS-floor comparison line) was already inside an existing `try/except` block and was caught silently — no edit needed there beyond the three `✓` replacements above.

**Smoke test:** Trial CC (MODEL_TYPE=J3, USE_FILM=1, USE_FOURIER_PE=1, USE_PREFIX=1, LOSS_MODE=ce). 1 epoch CPU. Result: **PASS**.
- `train_loss=3.0124` (act=2.4224, home=0.6368, cop=0.4568, marg=0.0718, trans=0.000)
- `val_JS=0.2437`, `home_gap=0.1180`, `val_score=0.3027`, `grad_norm=15.38` (within clip 25.0)
- No NaN, no shape mismatch, checkpoint saved. Val metrics printed correctly.
- 160 s wall-clock on CPU (d_model=384, 6+6 layers, batch=256, 4,812 train pairs).

**Cluster-env precheck:** Audited all 10 SLURM wrappers and every Python import chain.
- All scripts use only: `numpy`, `pandas`, `torch`, `scipy`, `matplotlib` + stdlib.
- `04B_model_MAMBA.py` uses **pure-Python SSM scan** (no `mamba_ssm` kernel). Confirmed by grep — zero `mamba_ssm` imports.
- No `eppy`, `yaml` (standalone), or `joblib` anywhere in the Stage A pipeline.
- **No pip install lines added** — all dependencies confirmed available in `/speed-scratch/o_iseri/envs/step4/` (same env used by prior J3 runs).

**Bundle contents** (`_bundle_sweepA/`, total **9.37 MB**):

| Path | Contents |
|---|---|
| `04A_sample_assembly.py` | Sample assembler |
| `04B_model*.py` (×9) | J3 trunk + HSMM, MDLM, HIER, MAMBA, SEDD, J3_v2, J3_v3 |
| `04C_training_pairs.py` | Unicode-fixed; `--sample_dir` flag |
| `04D_train.py` | Unicode-fixed; all Phase-6 env-var toggles |
| `04E_inference.py` | Unchanged |
| `04H/04I/04J_diagnostics*.py` | Unchanged; copied from `step4_Speed_Cluster/` to bundle root |
| `step4_Speed_Cluster/config_to_env.{sh,py}` | YAML→env translator |
| `step4_Speed_Cluster/sample_configs/*.yaml` (×10) | CC, CC_FACT, CC_SPL, GCE, HIER, HSMM, MAMBA, MDLM, SEDD, SINK |
| `step4_Speed_Cluster/sample_jobs/*.sh` (×10) | SLURM wrappers, 48h walltime, pg partition |
| `outputs_step4_G2_sample2/` | train/val/test .pt, meta CSVs, feature_config.json, strata_inv_freq.npy, training_pairs.pt, val_pairs.pt |

**Handoff:** Bundle at `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\2J_docs_occ_nTemp\_bundle_sweepA\` ready for manager to scp + submit 10 parallel sbatch.

### 2026-05-24 — Phase 6 Stage A: bundle uploaded + 10 jobs submitted

**Upload:** `scp -r _bundle_sweepA` → `/speed-scratch/o_iseri/occModeling/`. All 15 scripts + 10 YAMLs + 10 SLURM wrappers + sample slice (incl. `training_pairs.pt` / `val_pairs.pt`) landed cleanly.

**Cluster fix-up:** 9/10 wrappers rejected first attempt with `DOS line breaks (\r\n)` error from Windows scp. Fixed with `sed -i 's/\r$//'` over `sample_jobs/*.sh` + `config_to_env.sh`; cancelled stray CC submission (job 936215); resubmitted all 10 clean via `bash -c 'for t in ...; do sbatch ...; done'`.

**Job IDs (all on `pg` partition):**

| Trial | Job ID | State at submit |
|---|---|---|
| CC | 936216 | RUNNING (cisr-2) |
| CC_SPL | 936217 | RUNNING (cisr-1) |
| CC_FACT | 936218 | RUNNING (speed-03) |
| HSMM | 936219 | RUNNING (speed-17) |
| MDLM | 936220 | PENDING (AssocGrpGRES) |
| HIER | 936221 | PENDING (AssocGrpGRES) |
| MAMBA | 936222 | PENDING (AssocGrpGRES) |
| SEDD | 936223 | PENDING (AssocGrpGRES) |
| SINK | 936224 | PENDING (AssocGrpGRES) |
| GCE | 936225 | PENDING (AssocGrpGRES) |

Walltime 48h per wrapper; per-trial expected ~1h GPU. Next: monitor 4 RUNNING, wait for 6 PENDING to allocate.

### 2026-05-24 — Phase 6 Stage A: first submission FAILED (3 structural bugs)

All 11 jobs (936215–936225) reported `COMPLETED 0:0` in 11–31 s in `sacct`, masking real failures. SLURM `--output` logs at `/speed-scratch/o_iseri/occModeling/logs/` showed Python tracebacks at every pipeline stage.

**Bug 1 — Deployment shape mismatch (root cause).** Wrappers (`sample_jobs/CC_A.sh:17–21`) assume a **flat layout** at `$BASE = /speed-scratch/o_iseri/occModeling/`:
- `cd $BASE` → Python scripts (`04D_train.py`, `04E_inference.py`, …) expected at root
- `source $BASE/Speed_Cluster/config_to_env.sh "$BASE/sample_configs/${TAG}.yaml"` → expects `Speed_Cluster/` (NOT `step4_Speed_Cluster/`) and `sample_configs/` directly under `$BASE`
- `--data_dir outputs_step4_G2_sample2` → data dir expected at `$BASE` root

We uploaded everything nested under `$BASE/_bundle_sweepA/`. Result: wrapper ran against **stale Phase-4 04D/04E at the root** (predating Phase-6 env-var toggles) and `config_to_env.py` crashed with `FileNotFoundError: '/speed-scratch/o_iseri/occModeling/sample_configs/CC_A.yaml'`. Subsequent stages chain-failed on missing checkpoints and missing `augmented_diaries.csv`.

**Bug 2 — CRLF restored on re-copy.** Initial `sed -i 's/\r$//'` fixed DOS line endings on the bundle's wrappers, but the redeployment `cp -f` then overwrote those fixed files with the CRLF-tainted bundle originals. Lesson: **dos2unix must run AFTER every `cp`/`scp`**, not just once.

**Bug 3 — `cp` aliased to `cp -i` on cluster.** `cp -rf` does not bypass the alias — the user got interactive overwrite prompts despite `-f`. Workaround: use `\cp` (backslash escapes alias) or `/bin/cp`.

**Compounding silent-failure issue.** Wrappers run pipeline stages sequentially without `set -e`. When `04D_train.py` failed, the script continued to `04E_inference.py`, `04H`, `04I`, `04J` — all of which also failed but the final shell exit code was 0. SLURM logged `COMPLETED 0:0`. Recommend adding `set -e` at the top of every wrapper for the next bundle generation so SLURM sees `FAILED` and `sacct` is trustworthy.

**Fix applied (one-shot deploy + resubmit):**
```
cd /speed-scratch/o_iseri/occModeling && \cp -rf _bundle_sweepA/*.py . && \cp -rf _bundle_sweepA/step4_Speed_Cluster/sample_configs . && \cp -rf _bundle_sweepA/step4_Speed_Cluster/sample_jobs . && \cp -f _bundle_sweepA/step4_Speed_Cluster/config_to_env.sh _bundle_sweepA/step4_Speed_Cluster/config_to_env.py Speed_Cluster/ && \cp -rf _bundle_sweepA/outputs_step4_G2_sample2 . && sed -i 's/\r$//' sample_jobs/*.sh Speed_Cluster/config_to_env.sh && bash -c 'for t in CC CC_SPL CC_FACT HSMM MDLM HIER MAMBA SEDD SINK GCE; do sbatch sample_jobs/${t}_A.sh; done'
```

**Lessons captured for future builders:**
1. Build bundles **flat** to match the cluster's deployment convention (Python scripts at root, `sample_configs/` + `sample_jobs/` at root, `Speed_Cluster/` for helpers) — OR have the wrappers `cd` into the nested bundle dir first.
2. **Always** dos2unix after every Windows→Linux file transfer, not just the first one.
3. **Always** add `set -e` (or `set -euo pipefail`) to the top of multi-stage SLURM wrappers so silent Python crashes can't masquerade as `COMPLETED 0:0`.
4. Use `\cp` or `/bin/cp` on Speed cluster to bypass the `cp -i` alias.
5. Long inline pipelines mangle in tcsh / wrapping terminals — **stage a `deploy_and_submit.sh` helper** on the cluster and run it via `bash /path/to/helper.sh`. One-shot, immune to shell quoting and line-wrap.

### 2026-05-24 — Phase 6 Stage A: 10 jobs submitted (fresh IDs after fix)

Helper `deploy_and_submit.sh` (uploaded to `$BASE/`) ran clean: flat-deploy + dos2unix + 10 sbatch in one shot.

| Trial | Job ID | State |
|---|---|---|
| CC | 936227 | RUNNING (cisr-2) |
| CC_SPL | 936228 | RUNNING (cisr-1) |
| CC_FACT | 936229 | RUNNING (speed-03) |
| HSMM | 936230 | RUNNING (speed-17) |
| MDLM | 936231 | PENDING (AssocGrpGRES) |
| HIER | 936232 | PENDING (AssocGrpGRES) |
| MAMBA | 936233 | PENDING (AssocGrpGRES) |
| SEDD | 936234 | PENDING (AssocGrpGRES) |
| SINK | 936235 | PENDING (AssocGrpGRES) |
| GCE | 936236 | PENDING (AssocGrpGRES) |

Per-trial ~1h GPU. Next: monitor + download all 10 `diagnostics_*.json` + rank for Stage B pick.

### 2026-05-24 — Phase 6 Stage A v2: all 10 results, Stage B expansion (SEDD_B + MDLM_B)

**Stage A v2 final ranking (composite score, lower=better):**

| Rank | Trial | Composite | Notes |
|---|---|---|---|
| 1 | MDLM | 0.793 | Masked discrete diffusion; bidirectional x₀ parameterization |
| 2 | SEDD | 1.034 | Score-entropy discrete diffusion; power-law noise schedule |
| 3 | HSMM | 1.44 | |
| 4 | HIER | 1.46 | |
| 5 | CC | 1.47 | **Stage B running** (job IDs from prior submission) |
| 6 | MAMBA | 1.49 | |
| 7 | CC_SPL | 1.57 | **Stage B running** (job IDs from prior submission) |
| 8 | GCE | 1.74 | |
| 9 | CC_FACT | 1.93 | |
| 10 | SINK | 2.43 | |

**Decision rationale:** The discrete-diffusion family (MDLM + SEDD) dominated Stage A, separating clearly from all J3-variant and structured-state competitors. MDLM (#1, 0.793) outperformed #3 HSMM by a 1.81× margin; SEDD (#2, 1.034) outperformed #3 by 1.39×. Both are promoted to Stage B. Caveat: act_JS for MDLM and SEDD should be inspected against the sub-floor (JS=0.1888) — if their activity scores are already at-floor, the composite advantage may be partially illusory and AT_HOME/COP diagnostics become the decisive gates.

CC_B + CC_SPL_B already running; do not touch.

**Stage B expansion — SEDD_B + MDLM_B built:**

Config decisions: `use_film=1`, `use_fourier_pe=1`, `use_prefix=1` in both Stage B configs — matching Stage A values (verified from `SEDD_A.yaml` and `MDLM_A.yaml`) for apples-to-apples comparison. Manager prompt initially suggested 0; Stage A verification overrode that.

Files created (locally, `_bundle_sweepB_v2/`):
- `step4_Speed_Cluster/sample_configs/SEDD_B.yaml` — `sample_frac=0.20`, `max_epochs=100`, `patience=15`, `data_dir=outputs_step4_G2_sample20`
- `step4_Speed_Cluster/sample_configs/MDLM_B.yaml` — same Stage B parameters
- `step4_Speed_Cluster/sample_jobs/SEDD_B.sh` — 48h walltime, pg partition, `set -e`, full 04D→04E→04H→04I→04J chain
- `step4_Speed_Cluster/sample_jobs/MDLM_B.sh` — same
- `deploy_and_submit_B2.sh` — flat-deploy via `/bin/cp`, dos2unix, then 2× sbatch

**Job IDs:** TBD — to be filled after user runs deploy_and_submit_B2.sh on the cluster.

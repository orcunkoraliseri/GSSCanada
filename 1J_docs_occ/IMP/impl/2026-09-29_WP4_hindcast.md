# WP4 — quantitative hindcast of the 2025 projection (Reviewer comment 4) — task + implementation state
Task doc:   this file (manager-written 2026-09-29, plan log (bi))
Status:     RESUBMITTED as chain v2 (2026-09-29 ~17:57 EDT, manager) after smoke 1401430 FAILED at the production-model load only. See Ledger v2 lines.
Model:      Sonnet employee. One agent, one task, one turn. Submit, write state here, stop. Never wait or poll.

## Why
Reviewer 1: the C-VAE + cluster drift ("CBVM") is the strongest part but "the least validated". The paper
(§3.3, `1J_docs_occ/manuscript/1st_Occ_Journal.md` line 90) claims a hindcast with no number and no baseline.
Figure A1 came from `validate_forecast_distributions` (`previous/eSim_dynamicML_mHead.py:879-1052`), which used
an encoder/decoder trained on all four years (2021 leaked) and computed no metric. This WP replaces it.

## Design (FIXED by the manager before any run; do not change a number, a rule or a variable list)
**Pass rule (plan §2 comment 4, written 2026-09-19, before any run):** CBVM must beat B0 (carry-forward 2016)
on the majority of evaluated variables (strictly more than half), using the seed-mean distance to the real 2021
Census. Otherwise the paper drops the claim that CBVM projects better than carry-forward. Report the count either way.

1. **Training data:** `cen06_filtered2.csv`, `cen11_filtered2.csv`, `cen16_filtered2.csv` only
   (`0_Occupancy/Outputs_CENSUS/` locally; find the Speed copies and check they are the same files by
   md5 computed INSIDE an sbatch job, never on the login node). 2021 (`cen21_filtered2.csv`) is held out and
   is read only by the scoring step.
2. **Model:** call the protected functions unchanged from a NEW wrapper (`wp4_hindcast.py`):
   `prepare_data_for_generative_model` (2006/2011/2016 paths only, `sample_frac=1.0`), `train_cvae(latent_dim=128,
   epochs=100, batch_size=4096)` — the production settings (`run_step1.py:108-115`). Save models to a NEW folder
   under `/speed-scratch/o_iseri/1J_rerun/wp4/models/seed<s>_ld<L>/`; never overwrite `saved_models_cvae/`.
3. **Projection 2016 -> 2021 (dt = 5):** build `ClusterMomentumModel(n_clusters=K, decay_factor=d)` directly
   (bypass `train_temporal_model`, which hard-codes 8/0.95), fit on the 2006/2011/2016 latent means exactly as
   `train_temporal_model` does, then `generate_future_population` + `post_process_generated_data` as production does.
   **Building conditions = frozen 2016 stock** (the production 2025 run conditions on the last census year,
   `mH.py:556-559`; the hindcast mirrors that). Generated n = number of 2021 records.
4. **Methods compared (all scored the same way):**
   - **B0 carry-forward:** the 2016 records themselves as the 2021 prediction.
   - **B1 linear trend of marginals:** per variable, 2021 share = 2016 share + (2016 share - 2011 share), negatives
     set to 0, renormalised; continuous variables: each of the 99 percentiles extrapolated the same way (q2021 =
     2*q2016 - q2011), sorted.
   - **B2 population-mean drift:** `ClusterMomentumModel(n_clusters=1, decay_factor=0.95)` = one velocity for the
     whole population, everything else identical to CBVM.
   - **CBVM:** `n_clusters=8, decay_factor=0.95` (production).
5. **Variables scored:** every generated demographic column present in both the generated output and
   `cen21_filtered2.csv` (list at `mH.py:121-126`, minus `YEAR`). Record the final list here before scoring.
   Categorical: total-variation distance TVD = 0.5 * sum |p - q| over the union of categories.
   Continuous (`EMPIN`, `TOTINC`, `INCTAX`): Wasserstein-1 distance on values min-max scaled by the 2021 range.
   Unweighted (no survey weights exist in these files; say so in the output).
6. **Seeds:** 5 seeds {1,2,3,4,5}; each seed sets `np.random.seed`, `random.seed`, `tf.random.set_seed` in the
   wrapper before training, and the same seed drives generation. B0 and B1 are deterministic (no seed).
7. **Ablations (sensitivity), scored the same way, reported, never used to pick a "best" setting:**
   K in {4, 8, 12} and decay in {0.90, 0.95, 1.00} on the seed-1..5 models (cheap: no retraining);
   latent dim in {64, 256} with seed 1 only (two extra trainings).
8. **2025 sensitivity (cheap):** with the PRODUCTION models (`saved_models_cvae/`, trained 2006-2021, copied, not
   moved), generate 2025 (dt = 4 from 2021, as production) for K in {4,8,12}, decay in {0.90,0.95,1.00}, and
   seeds 1-5 at K=8/0.95; report per variable the TVD / W1 between each variant and the seed-1 K=8/0.95 output.
   (The 5-seed spread of OCCUPANCY metrics needs the full downstream chain and is a separate item, see "Not in
   this task".)
9. **Outputs** (under `/speed-scratch/o_iseri/1J_rerun/wp4/out/`, then scp to `1J_docs_occ/IMP/impl/wp4/out/`):
   `hindcast_scores.csv` (method, K, decay, latent, seed, variable, metric, value),
   `hindcast_summary.csv` (per variable: seed-mean and min-max of each method), `pass_rule.txt` (the count of
   variables where seed-mean CBVM < B0, and the verdict line `WP4 PASS RULE: CBVM beats B0 on X of N -> MET/NOT MET`),
   `sens2025.csv`.

## Gates (each must be SEEN FAILING on a broken input before it is trusted)
- G4.1 leakage: the wrapper asserts no 2021 row reaches training (`YEAR` values of the training frame = {2006,2011,2016}).
  Seen failing: run the assert once on a frame with 2021 appended (selftest).
- G4.2 metric: TVD(x, x) = 0 and TVD of two disjoint distributions = 1; W1(x, x) = 0. Seen failing: a deliberately
  wrong TVD (without the 0.5) must fail the check in the selftest.
- G4.3 B0 sanity: B0's TVD on `PR` should be small (province shares move slowly); print it. Not a pass rule; a smell test.
- G4.4 reproducibility: seed 1 generation run twice from the same saved model gives identical scores.
- Every patch or monkey-patch prints its own line; the manager checks each line is PRESENT in the log.

## Rules
- Never edit `eSim_datapreprocessing.py`, `eSim_dynamicML_mHead.py`, `eSim_dynamicML_mHead_alignment.py`.
- Speed: `sbatch` only; login node allows only sbatch/squeue/sacct/scancel/scontrol/cd/ls/scp/module load and
  single-file tail/head/grep/wc -l/cat. NO python, NO find, NO du, NO md5sum on the login node. tcsh login shell.
  Every job: `-t 7-00:00:00 -A chachemv -p ps`. Python with TensorFlow: `/speed-scratch/o_iseri/1J_rerun/venv2025/bin/python`
  (never pip into the read-only GSSCanada venv). 1J CPU cap 64 in total; the other 1J employees also use CPUs —
  use at most 24 CPUs for this WP at any time.
- Check `quota`/free space first (scratch was 9.2T of 10T); write nothing big.
- Local: `py`, never `python`. Never open a multi-MB CSV in your context.
- Do not wait for jobs. Submit the chain (selftest -> trainings -> scoring, with `--dependency`), write the job ids
  in the Ledger, and stop.

## Not in this task (manager decides later)
- 5-seed spread of the 2025 OCCUPANCY metrics (needs forecast -> assembly -> matching -> schedules per seed).
- External 2025 check against Statistics Canada tables (optional item; needs the author to download tables).

## Ledger
(JobID · what · state · exit · output path — append only; all `-A chachemv -p ps -t 7-00:00:00`, 3 CPUs, 32G unless noted; logs `/speed-scratch/o_iseri/1J_rerun/logs/wp4_<name>_<id>.out`)
- 1401430 · smoke (selftest gates + data-vs-mirror md5 + 1-epoch train + score K{8,1} + prod-model load/generate) · submitted, RUNNING at submit time · - · scratch `wp4/smoke/`
- 1401431-1401435 · train seeds 1-5, latent 128, afterok:1401430 · submitted · - · `wp4/models/seed<s>_ld128/`
- 1401436 · train seed 1, latent 64 · submitted · - · `wp4/models/seed1_ld64/`
- 1401437 · train seed 1, latent 256 · submitted · - · `wp4/models/seed1_ld256/`
- 1401438 · sens2025 (production models, 2025 variants), afterok:1401430 · submitted · - · `wp4/out/sens2025.csv`
- 1401439-1401443 · score seeds 1-5, latent 128 (K{4,8,12} x decay{.90,.95,1.00}, B2, G4.4 on each seed), afterok on all 7 trainings · submitted · - · `wp4/out/scores_seed<s>_ld128.csv`
- 1401444 / 1401445 · score seed 1 latent 64 / 256 (K=8, 0.95 only) · submitted · - · `wp4/out/scores_seed1_ld{64,256}.csv`
- 1401446 · aggregate (1 CPU, 16G): B0, B1, merge, summary, pass rule; afterok on all scores + afterany on sens2025 · submitted · - · `wp4/out/{hindcast_scores,hindcast_summary}.csv`, `pass_rule.txt`
- CPU peak: trainings 7x3 = 21 (+ sens2025 3 = 24); scorings 7x3 = 21 (+ sens2025 3 = 24). Never above 24.
- Files: local `1J_docs_occ/IMP/impl/wp4/{wp4_hindcast.py, wp4_job.sh, submit_chain.csh}`; Speed root `/speed-scratch/o_iseri/1J_rerun/wp4/{code,data,prod_models}`.
- Note for the manager: if 1401430 fails, the 15 dependent jobs sit pending forever (afterok); cancel them.

- 2026-09-29 ~17:50 manager: 1401430 smoke FAILED (exit 1, 1:41:00). Passed: G4.1/G4.2/G4.4 selftests, DATA MIRROR CHECK (4x SAME CONTENT), 1-epoch train on real 2006/2011/2016 (796,536 rows), save/load/score (VARIABLES SCORED (24), G4.4 REPRODUCIBLE PASS; smoke CBVM K8 mean 0.0511, K1 0.0500 after ONE epoch - not results). Failed: cmd_sens2025_probe, keras 3.10 cannot read the production .keras files saved by keras 3.13.2 (`Unrecognized keyword arguments passed to Dense: {'quantization_config': None}`). Protected files unchanged (md5 start = end).
- 1401431-1401446 (v1 chain): CANCELLED by the manager (DependencyNeverSatisfied after the smoke failure). Superseded by the v2 lines below.
- Fix: `wp4/convert_prod_models_k310.py` (local, keras 3.13.2): config keys written by 3.13 but absent from the model saved by 3.10 on Speed (smoke model, compared per layer class) removed only where default: Dense.quantization_config None x31, InputLayer.optional False x4, Sampling.activity_regularizer None x1, Sampling.autocast True x1. model.weights.h5 + metadata.json byte-identical (asserted). Originals untouched (md5 a4e7f013 / 8659a0e4 before = after). Fingerprint of the ORIGINALS under 3.13 -> `code/prod_fingerprint_k313.json` (16 enc + 62 dec weight sums, z_mean and decoder outputs on a fixed input); converted copies under 3.13: SAME MODEL; check seen failing on a nudged copy. Upload: `wp4/prod_models_k310/` (sizes 1,209,094 / 1,138,344 = local).
- wp4_hindcast.py v2: PROD defaults to `prod_models_k310` (env WP4_PROD); new mode `probe` = load + fingerprint vs 3.13 (exact weight sums, outputs within 1e-5; seen failing on a nudged copy; exit 31 if different) + input dims + 2,000-row 2025 generation. No other change.
- v2 chain (`code/submit_chain_v2.csh`): trainings start at once (the smoke proved the hindcast path) at 8 CPUs (was 3; 1-epoch ETA at 3 CPUs was ~25 min/epoch x 100 epochs); probe gates only sens2025. CPU peak 62 <= 64.
- 1401489 · probe (3 CPU) · RUNNING · `logs/wp4_probe_1401489.out` (look for `PROD FINGERPRINT ... SAME MODEL`, `PRODUCTION GENERATION OK`, `PROBE DONE: PASS`)
- 1401490-1401494 · train seeds 1-5 latent 128 (8 CPU) · 1401490-92 RUNNING, 93-94 PENDING (priority) · `wp4/models/seed<s>_ld128/`
- 1401495 / 1401496 · train seed 1 latent 64 / 256 (8 CPU) · PENDING · `wp4/models/seed1_ld{64,256}/`
- 1401497 · sens2025, afterok:1401489 · PENDING · `wp4/out/sens2025.csv`
- 1401498-1401504 · score (as v1, 8 CPU), afterok on 1401490-96 · PENDING · `wp4/out/scores_*.csv`
- 1401505 · aggregate, afterok on 1401498-1401504 + afterany 1401497 · PENDING · `wp4/out/{hindcast_scores,hindcast_summary}.csv`, `pass_rule.txt`

- 1401489 probe: FAILED exit 31 (1:11). Models LOAD under 3.10; encoder weights + z_mean + decoder outputs matched, but the decoder weight-sum LIST differed: keras 3.10 and 3.13 list the decoder's variables in a different order. Fix: fingerprint keyed by variable path. 1401497 (sens2025, afterok probe) CANCELLED.
- 1401509 probe2: FAILED exit 31 (0:08). By path, 1 of 62 decoder variables (`dense_3/kernel`) had a different float64 SUM while decoder outputs matched within 1e-5: numpy on Speed (py3.9) and locally (2.3.5) sum large float32 arrays differently in the last bits. Fix: md5 of each variable's raw bytes + shape (exact, independent of summation). 1401510 (sens2025b) CANCELLED.
- 1401511 · probe3 (md5 fingerprint) · COMPLETED exit 0 (1:42) · `logs/wp4_probe3_1401511.out`: `PROD FINGERPRINT seen failing (nudged copy)`, `PROD FINGERPRINT vs the original models under keras 3.13: SAME MODEL`, `PRODUCTION MODELS OK: encoder inputs [154, 22] match the 4-year data`, `PRODUCTION GENERATION OK: 2025 sample columns = 30 rows = 2000`, `PROBE DONE: PASS`, `PROTECTED FILES UNCHANGED: YES`. sens2025c 1401512 RUNNING.
- 1401512 · sens2025c, afterok:1401511 · PENDING · `wp4/out/sens2025.csv`. Aggregate 1401505 still waits on the scores only (its afterany:1401497 is satisfied by the cancel; the tables script reads sens2025.csv separately).

## Verified
- Local (numpy 2.3.5, pandas 2.3.3, scipy 1.17.0; TensorFlow NOT installed locally): `py -m py_compile` OK; `py wp4_hindcast.py selftest_metrics` printed, in order:
  - G4.1 seen failing twice (frame with YEAR_2021 appended -> `LEAK/MISSING: YEAR values ... ['2006','2011','2016','2021']`; paths dict with 2021 -> assertion), then the passing case `['2006','2011','2016']`.
  - G4.2 seen failing (TVD without the 0.5: `['TVD(disjoint) != 1', 'TVD known value != 1/3']`), then the correct metrics: no failures (TVD(x,x)=0, disjoint=1, {a,a,b} vs {a,b,b}=1/3, W1(x,x)=0, W1 shift by 1 on range 5 = 0.2).
  - G4.4 helper (`scores_identical`) seen failing on a perturbed copy (2.0 vs 2.0000001), then passing.
- Aggregate step tested locally on the REAL local cen11/cen16/cen21 files with FAKE score files: CBVM tiny -> `MET 24 of 24`; CBVM huge -> `NOT MET 0 of 24`; seed-5 file removed -> `NOT_EVALUABLE`. G4.3 from that run: B0 TVD on PR = 0.0041 (small, as expected; re-printed in the real aggregate log).
- Upload sizes on Speed (ls) equal local for the 4 census files (24,241,933 / 32,634,971 / 30,047,744 / 30,753,361) and the 2 production models (decoder 1,139,165 / encoder 1,209,296). Local md5: cen06 bbae1534..., cen11 c0b821e1..., cen16 8e8d16e1..., cen21 b3591149..., decoder 8659a0e4..., encoder a4e7f013....
- Mirror vs local census files: sizes differ (mirror 24,021,353 / 32,332,964 / 29,773,792 / 30,474,519). Each difference equals exactly the number of lines in the local file (220,580 / 302,007 / 273,952 / 278,842), i.e. the local files have Windows CRLF line ends. Content equality is NOT yet proven: job 1401430 compares md5 with carriage returns removed and exits 11 (stopping the whole chain) if any file differs.
- Speed: `venv2025` python exists; quota /speed-scratch 9.2T of 10T (unchanged); the wp4 upload is 115 MB.
- Dependency graph read back with `squeue` after submit: all 15 dependents PENDING with the intended `afterok`/`afterany` lists; only 1401430 RUNNING.

## Decisions
- Variable list (24, fixed here before scoring; mH.py:121-126 minus YEAR): MARSTH, EMPIN, TOTINC, KOL, ATTSCH, CIP, NOCS, GENSTAT, POWST, CITIZEN, LFTAG, CF_RP, COW, CMA, AGEGRP, SEX, CFSTAT, INCTAX, HHSIZE, EFSIZE, CFSIZE, PR, HRSWRK, MODE. All 24 are in the cen21 header (head -1). The score job asserts the generated output has all 24 and prints `VARIABLES SCORED (24)`. Continuous = EMPIN, TOTINC, INCTAX (W1); the other 21 are categorical (TVD). VALUE and the building columns are not scored (buildings are the frozen 2016 stock).
- Training data: the LOCAL cen06/11/16/21_filtered2.csv were uploaded to `wp4/data/`; the Speed mirror copies are the same files with LF endings by size arithmetic and job 1401430 proves it by md5 after removing CR (else exit 11). The wrapper reads the uploaded files (pandas handles CRLF).
- Production models: `saved_models_cvae/` does NOT exist on the Speed mirror (only local `0_Occupancy/saved_models_cvae/`, encoder + decoder, Apr 8). Copied (not moved) from local to `wp4/prod_models/`; job 1401430 checks they load in venv2025 (TF 2.20 / keras 3.10) and that encoder input sizes match the 4-year data. If they fail to load, the smoke fails and the chain stops (a real blocker for item 8, not for the hindcast).
- The protected module is imported from the existing unchanged copy `/speed-scratch/o_iseri/1J_rerun/occ2025/code/eSim_occ_utils/25CEN22GSS_classification/`; md5 of the three protected files is checked at job start and end (exit 9 / 8). No monkey-patch anywhere; each log prints `WP4 PATCHES: none`.
- `prepare_data_for_generative_model` gets the 2006/2011/2016 files only. Quantile mapping follows production: `ref_df=processed_data` is the whole frame (here the 3-year frame; the docstring says "last year" but production passes all years).
- KMeans is fitted once per K and copied with each decay (decay is used only in `predict`; clusters and velocities do not depend on it); equivalent to building `ClusterMomentumModel(K, decay)` per pair. `fit` gets the 2006/2011/2016 z_mean dict exactly as `train_temporal_model` does.
- Seeds (random, numpy, tf) are set right before `train_cvae` and right before every generation call, so one seed drives resampling, noise and building-condition draws. KMeans stays at random_state 42 (protected code).
- B1 continuous: percentiles 1..99, q = 2*q16 - q11, sorted, W1 against the real 2021 values (99 equal-weight points vs the full 2021 sample), scaled by the 2021 range. B0 continuous: full 2016 values vs full 2021 values.
- Pass rule: strict `<`; "majority" = strictly more than half of N (N=24 -> at least 13). Verdict is `NOT_EVALUABLE` (not MET / NOT MET) if any score file is missing.
- sens2025: reference = seed 1, K=8, decay 0.95, production models, n = 250,000 (production default), 4-year data, 2025 from 2021 (dt=4); the 8 other K/decay variants use seed 1; seeds 2-5 use K=8/0.95. A control row (reference regenerated with seed 1) must give distance 0.
- CPU plan: 3 CPUs per job (TF threads from SLURM_CPUS_PER_TASK), peak 24.

## Next
- Manager: read the smoke log first (`logs/wp4_smoke_1401430.out`, grep only; Keras bars are noisy). Look for: `G4.1 SELFTEST: PASS`, `G4.2 SELFTEST: PASS`, `DATA MIRROR CHECK: PASS` (four `SAME CONTENT` lines), `PRODUCTION MODELS OK`, `PRODUCTION GENERATION OK`, `VARIABLES SCORED (24)`, `G4.4 REPRODUCIBLE ... PASS`, `SMOKE DONE: PASS`, `PROTECTED FILES UNCHANGED: YES`, `WP4 PATCHES: none`.
- If smoke fails: `scancel 1401431-1401446`, fix, upload the fixed `wp4_hindcast.py`, resubmit with `tcsh /speed-scratch/o_iseri/1J_rerun/wp4/code/submit_chain.csh`.
- When 1401446 ends: `scp` `wp4/out/*` to `1J_docs_occ/IMP/impl/wp4/out/`; read `pass_rule.txt` (`WP4 PASS RULE: CBVM beats B0 on X of N -> MET/NOT MET`); check every score log for `G4.4 REPRODUCIBLE ... PASS`, train/score logs for `G4.1 PASS`, the `TRAIN DONE` losses across seeds, and the `G4.3 B0 TVD on PR` line in the aggregate log.

## WHAT I DID NOT VERIFY
- The TensorFlow/Keras path (train, save, load, encode, decode, generate) has never run: no local TensorFlow. Only the metric gates and the aggregate step ran locally; the rest is first exercised by smoke job 1401430.
- That the mirror census files equal the local ones in content (size arithmetic only; the job tests it).
- That the production `.keras` models load under TF 2.20 / keras 3.10 and that their input dims match the 4-year data.
- That the production models were trained on exactly these filtered2 files (Apr 2 files, Apr 8 models; inferred from dates only).
- That decoder output column order equals `demo_cols` order (protected code sorts the head names; this mirrors production and was not independently checked).
- Training time and memory per job (32G / 3 CPUs is a guess; 100 epochs, batch 4096, ~800k rows).
- G4.4 has been seen failing only for its helper on a perturbed copy, not on a real non-deterministic generation.
- B1 percentile extrapolation for continuous variables is my reading of "each of the 99 percentiles" (percentiles 1..99, not 0..100).

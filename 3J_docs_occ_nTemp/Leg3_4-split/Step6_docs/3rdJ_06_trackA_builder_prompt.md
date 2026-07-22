# Builder prompt — Step 6 Track A: GPU forecasting port + submit (4-split)

> Paste into a fresh Sonnet session. Manager-authored 2026-07-21. This is Part 1 of 2 for Track A —
> build, smoke-test, submit. Do **not** run the validator or calibration chain in this session; the
> full 2030 diary generation only finishes once the cluster job completes, which is a separate
> follow-up prompt (`3rdJ_06_trackA_postrun_prompt.md`, issued after the job's `.out` is read).

---

You are the **employee**. Execute the task below and append a Progress Log entry on completion.

## Scope & cluster discipline (read before doing anything)

- Local work (porting, smoke test) happens on this machine. Cluster work is **submission only** —
  `sbatch` ONLY, never blocking/interactive `srun`, no bare `python` on `speed-submit2` (not even
  one-liners). Every cluster command is a **single line**, labelled "on the cluster" when you report it.
- `-t 7-00:00:00` on the sbatch job, no exceptions, even though this is a GPU training job expected to
  finish well under a day — pad the walltime request regardless.
- Login shell is tcsh: do not use `2>/dev/null` or `2>&1` in remote commands (they get parsed as
  literal arguments, not redirects, and the command fails with a confusing error). Wrap any multi-command
  remote work in `ssh speed bash -s <<'REMOTE' ... REMOTE`.
- **After `sbatch` returns a job ID, STOP.** Do not poll `squeue`/`sacct` in a loop. Report the job ID
  and end your turn — the manager/user will decide when to check on it (≥30 min spacing if anyone does).
- Do not modify `3rdJ_04B_model_4split.py` (LOCKED, Step-4 architecture) or any `3rdJ_04*_4split.py`
  Step-4 file. Everything you build lives under `Step6_docs/`.

## Read first

1. Runbook (authoritative): `Leg3_4-split/Step6_docs/3rdJ_06_longitudinalForecasting_4split.md`
2. Validation plan (for gate context only — you are not implementing the validator in this prompt):
   `Leg3_4-split/Step6_docs/3rdJ_06_longitudinalForecasting_4split_val.md`
3. Fork base (Leg-2, 2350 lines): `Leg2_2-split/Step6_docs/3rdJ_06_longitudinalForecasting_2split.py`
4. Fork base: `Leg2_2-split/Step6_docs/assemble_scenario_2030_2split.py`
5. Leg-3 LOCKED model (already built by Step 4, do not edit): `Leg3_4-split/Step4_docs/3rdJ_04B_model_4split.py`
   (class `JSeriesHybrid4Split`)
6. Leg-3 Step-4's own training script (already implements the exact fixed-α+PCGrad+3-task loss
   Step-6 needs to fine-tune with): `Leg3_4-split/Step4_docs/3rdJ_04D_train_4split.py`
7. Leg-3 Step-4's own inference script (already implements nucleus decode as an external wrapper
   around the LOCKED model — this is your template for backcast/deliverable generation):
   `Leg3_4-split/Step4_docs/3rdJ_04E_inference_4split.py`

## Files to create (all under `Leg3_4-split/Step6_docs/`)

- `3rdJ_06_longitudinalForecasting_4split.py` — main script, `--stage {audit,A,B,C,D1,D2,all} --band ... --smoke`
- `assemble_scenario_2030_4split.py` — `--verify` dry-run, writes `outputs_step6/scenario_2030_features_4split.csv`
- `slurm_06_4split.sh` — `#SBATCH -p pg --gres=gpu:1 -t 7-00:00:00 --mem=32G`

Do **not** build `3rdJ_06_retail_lever_4split.py`, `3rdJ_06_calibrate_C_4split.py`, or
`3rdJ_06_hotel_sarima_4split.py` in this session — those are post-training / separate-track work,
covered by other prompts.

## Port instructions

### 1. CLI/stage structure — port verbatim

Same `--stage {audit,A,B,C,D1,D2,all}` dispatch as the Leg-2 file (stages run in file order:
`audit` standalone; otherwise `A → B → C → D1 → D2×3 bands`, each warm-starting from the previous
checkpoint). Same `--smoke` (5% data / 3 epochs), `--band`, `--data` flags. Update all path constants
to Leg-3 (`_4split` suffixes, `Leg3_4-split` tree) and the training-corpus default:

- **Training data = the RAW (pre-rake) Leg-3 Step-4 pool.** On the cluster this lives under
  `Leg3_4-split/Step4_docs/outputs_step4/` — there are multiple seed directories there (`seed_0`
  through `seed_4`, `seed_3_g3fix`, `sweep/`). Per Step-4 closure, the winning locked pool is
  **seed-3**; confirm in your `--stage audit` run whether `seed_3/` or `seed_3_g3fix/` is the correct
  raw pool to train on (the `_g3fix` variant looks like a later determinism fix — check file mtimes
  and any Step-4 Progress Log note on which one is canonical) and report which you used.
- **Backcast reference = the Step-5 locked (raked) pool**, comparison only, never training:
  `Leg3_4-split/Step5_docs/outputs_step5/3rdJ_25CEN_aug_Full_Aggregated_excl.csv` (confirmed present
  locally, 30,273-row frame of record).

### 2. Model import — LOCKED, do not touch

```python
_04b = importlib.import_module("3rdJ_04B_model_4split")
JSeriesHybrid4Split = _04b.JSeriesHybrid4Split
```
`model_type` stays whatever Step-4 used (J3, 3-head). Warm-start block: keep the Leg-2 pattern
(assert `d_cond` match, adopt checkpoint's saved `model_config` wholesale) — this part is
architecture-agnostic and ports unchanged.

### 3. Loss weighting — reuse Step-4's own pattern, do NOT port Leg-2's `UncertaintyWeighting`

Leg-2's Step-6 `build_model()` hardcoded `UncertaintyWeighting(TASKS)` (its only weighting mode,
Leg-2 file line ~697) because Leg-2's Step-4 was UW-based. **Leg-3's Step-4 already made the
fixed-alpha decision** — `3rdJ_04D_train_4split.py` line 108 defines `TASK_GROUPS =
["resid", "work", "retail"]` (note: `cop` is folded under the `resid` group, not its own task) with
`--alphas` default `"1.0,0.5,0.3"` (line 921) and its own `PCGrad` class (line 284, "ported verbatim
from Leg-2, task-agnostic"). **Import and reuse these directly from `3rdJ_04D_train_4split`** rather
than re-deriving a weighting scheme — this is a solved problem one directory over. `retail_pos_weight`
resolution (line 556-564: config value ~49 wins unless CLI override) and the `-ln(pos_weight)` decode
shift both need to persist through every Step-6 fine-tune stage exactly as Step-4 used them.

### 4. Cross-day pairing (`Step6Dataset` / self-pairing bug) — port unchanged

Port `build_cycle_pairs()`, `_score_candidates_pairing()`, `_bin_totinc_for_pairing()` from the Leg-2
file verbatim (Leg-2 lines 506–566, 485–503, 472–482) — this machinery is channel-agnostic (operates
on demographic/stratum columns only, never touches activity/home/work/retail arrays), so no Leg-3
changes needed here. In `Step6Dataset.__getitem__`, add a `dec_retail_avail` key alongside the existing
`dec_work_avail` (decoder target indexed by the sampled cross-day neighbour `t`, never `src_idx==t` —
this is enforced structurally by `build_cycle_pairs`' candidate-pool construction, not by a runtime
assert; keep it that way, don't add a superfluous assert that duplicates the structural guarantee).
**This is the fix for the known Leg-2 self-pairing bug** (`src==tgt` → identity autoencoder →
backcast JS = −0.0000) — if you see JS≈0 or three identical bands in your smoke test, you've broken
this pairing, stop and re-check against Leg-2 lines 602-621 before proceeding.

### 5. DRIFT_MATRIX — add the AT_RETAIL axis

`compute_drift_matrix_2split()` (Leg-2 lines 981–1072) computes one row per stratum with
`AT_HOME_drift` / `AT_WORK_drift` scalars + an aggregate 14-activity JS vector — **not** a true
per-activity×channel matrix (confirm this in the Leg-2 val.py's own schema note before assuming
otherwise). Add a third `AT_RETAIL_drift` scalar to the per-stratum row dict. Extend
`TrendEncoder2Split.from_drift_csvs()` (Leg-2 lines 1120–1148) to pull the quadruple
`[AT_HOME_drift, AT_WORK_drift, AT_RETAIL_drift, aggregate_JS]` instead of the Leg-2 triple —
`input_dim` is inferred automatically from vector length (line 1143), so you don't need to hand-fix a
hardcoded dimension there, but `__init__`'s `n_output` (Leg-2 hardcodes 6 = 3 strata × 2 channels,
line 1085) must become **9** (3 strata × 3 channels) and be passed explicitly.

**COVID triple-signal**, `DRIFT_MATRIX_1522`: extend the dual-signal check to a triple — AT_HOME ≥ +5pp
**and** AT_WORK directional decrease **and** AT_RETAIL directional decrease must co-occur (in-store
shopping fell through COVID). Treat this as a soft blocker (investigate, don't hard-fail) per the
val plan.

Note the Leg-2 caveat (found in review): the TrendEncoder's own training in `run_substage_c()` fits
against an all-zero dummy target for 50 iterations — despite the runbook language implying real
distribution-matching, it isn't one in the Leg-2 code. Port this as-is (it's a known limitation, not
something to silently "fix" beyond scope) but flag it explicitly in your Progress Log so it's not
mistaken for a completed improvement.

### 6. Backcast / deliverable generation — reuse Step-4's `generate_nucleus()`, do not add nucleus decode to 04B

The runbook (`6F`) specifies backcast/deliverable decode at **T 0.7 + nucleus p=0.9 + min-dwell**,
never greedy. Leg-2's Step-6 code has no nucleus sampling at all (only greedy argmax or
temperature-scaled `torch.multinomial`, `_arm1_generate`, Step-4 `3rdJ_04B_model_2split.py` lines
323-355) — **do not add top-p truncation inside the LOCKED `3rdJ_04B_model_4split.py`.** Leg-3's own
Step-4 already solved exactly this: `3rdJ_04E_inference_4split.py::generate_nucleus()` (line 155)
wraps `_arm1_generate()`'s existing public building blocks (embeddings, encoder, causal mask, slot
re-embedding) and adds top-p truncation externally, at `temperature=0.7, top_p=0.9` defaults (line
156), returning an 8-tuple including `retail_sigmoid` when `return_retail_probs=True`. **Import and
call this function from your Step-6 script** for both the 2022 backcast generation (`D1`) and the
2030 deliverable generation (`D2`), instead of reimplementing decode logic. Internal
diagnostic-only paths (DRIFT_MATRIX computation, the epoch-level early-stopping metric inside
`progressive_train()`) may keep temperature=0.0 greedy as Leg-2 did — that's a deliberately scoped
internal signal, not the deliverable.

### 7. Fine-tune chain — port unchanged

Four-stage progressive fine-tuning (`W_2005 → W_2010_ft → W_2015_ft → W_2022_ft`), recency weights
(0.10/0.20/0.30/0.40), early-stop policies: verbatim Leg-2 structure and hyperparameters. Only the
loss/weighting call sites change per §3 above.

### 8. `assemble_scenario_2030_4split.py`

Port `assemble_scenario_2030_2split.py` verbatim in structure; extend whatever feature columns it
assembles to include a retail-conditioning placeholder if the Leg-2 file has one for office WFH bands
(the runbook is explicit that **no retail conditioning is added to the model** — the retail lever is
entirely post-hoc, applied downstream of this feature file, so do not invent a retail feature column
that doesn't already have a Leg-2 analog).

### 9. `slurm_06_4split.sh`

Fork the Leg-2 `slurm_06_2split.sh` header; only the partition/GPU/walltime/mem directives matter
(`-p pg --gres=gpu:1 -t 7-00:00:00 --mem=32G`) plus the `--wrap`/script invocation updated to the
4-split script and `--stage all`.

## Test method

1. **Locally, `--smoke` end-to-end** (tiny epochs, CPU is fine) — confirm all 5 stages
   (`audit,A,B,C,D1,D2`) run without error, checkpoints get written with `_4split` names, and the
   DRIFT_MATRIX CSVs have the new `AT_RETAIL_drift` column. Confirm the pairing sanity check from
   §4 (no JS≈0 / no identical bands).
2. **On the cluster, single line:** `sbatch slurm_06_4split.sh` — capture the job ID. **Do not run
   `squeue`/`sacct` afterward in this session; do not wait.**

## Progress Log

Append a dated entry to `3rdJ_06_longitudinalForecasting_4split.md`'s Progress Log: files created,
which raw pool (`seed_3` vs `seed_3_g3fix`) you trained on and why, smoke-test result, job ID, and any
judgment call (especially anything in §3/§5/§6 where you deviated from a Leg-2 pattern).

## Return

Concise report: files written, smoke-test outcome, the cluster job ID, and flag anything ambiguous
(especially the seed_3 vs seed_3_g3fix pool choice) back to the manager rather than guessing silently.

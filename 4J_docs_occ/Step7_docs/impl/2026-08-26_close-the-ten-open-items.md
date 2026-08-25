# 2026-08-26 — CLOSING THE TEN OPEN BOARD ITEMS: WHAT WAS STALE, WHAT WAS MISDIAGNOSED, WHAT IS RUNNING

The board carried **2 IN PROGRESS and 8 NOT STARTED**. All ten were audited against what is
actually on disk and on Speed. The audit changed the shape of the problem: **three items were
already finished and mis-marked, two had the wrong blocker written on them, one is closed by a
ruling that no amount of compute can move, one can only be closed by a person, and three are
genuine work that is now running.**

⚪ Throughout: no threshold moved, no checker edited to make a gate pass, `prereg.md` md5
`e4243e07cdd80c9c846b91f40e3e8c45` unchanged.

---

## A. Three items were STALE — finished, and still marked not started

| item | truth |
|---|---|
| **7.6 Decide the chaining rule** | **Ruled and closed by the author 2026-08-25**, `Step8_docs/docs/2026-08-25_decision-14_chaining-on-a-watt.md` §8: convention `independent`, seed `1`, project-wide. `G7.18` ran 9,000 EnergyPlus runs; rule spread on peak **0.289 / 0.194 / 0.028 %** against a 25 % trigger, not triggered in any fold, seed noise beating rule effect on every metric. Re-measured after the midnight rotation and unchanged. |
| **7.7 Emit schedules** | Emitted, and **re-emitted** after `D-S9-3`(a); `schedules/` holds 1,632 files in 16 bundles, the reportable Leg-5 bundles carry `n_days: 5200, provenance: null`, and Step 8 consumed them across **two** 13,108-run campaigns. 🔴 The board carried **two** 7.7 rows — a done one and a pre-rotation `s:"todo"` stub with no note. The stub was removed; a duplicate row is the defect, not a status. |
| **`G7.10`** | **PASS**, job **1286244**, 2026-08-22, 23 min: **0 disagreements on 10,000 strings**, 5,000 accepted / 5,000 rejected by the hand-written oracle, alphabets ACT 159 / ACT2 43 / COP 34 / LOC 5. Artefact `g710_oracle_agreement.json`, md5 `631ad64ba344de9e1195e0029214652c`, present on Speed **and** locally. |

🔴 **`G7.10`'s stale note was worse than the stale status.** It read *"No XGrammar back-end yet."*
xgrammar **0.2.3** has been in `envs/step7` since 2026-08-22 — it was installed by the very ruling,
`D-S7-3`, that the note post-dates. A blocker written down once and never re-checked outlives the
blockage.

---

## B. Two items had the wrong blocker written on them

### "Ceiling run — needs `bitsandbytes`, not installed"

`bitsandbytes` **0.50.1** has been on Speed since 2026-08-22, in `envs/step7`. The real blocker was
never named anywhere: **the 8-bit half of the ceiling recipe was never implemented.**
`4thJ_step4_train.py` built a plain `torch.optim.AdamW` for *every* run type, `ceiling` included.
At 7 B that is 14 GB of bf16 weights + 14 GB of gradients + **56 GB of fp32 Adam moments = 84 GB**
before a single activation, on the 80 GB instance the run is registered on. The recipe was not
merely un-run; **as coded it could not run.**

Now implemented, guarded by `run_type == "ceiling"` so no LoRA run can reach it, and it **REFUSES**
rather than silently falling back to 32-bit — a fallback would report a different recipe under the
ceiling's name. The refusal is run as a **control before the real arm**, because a refusal nobody
has watched happen is an assumption.

⚪ `envs/step4` stays frozen per `D-S7-3`: `bitsandbytes` is staged by `pip install --target` into
`envs/bnb_for_step4` and put on `PYTHONPATH`, so the interpreter, torch, transformers and peft are
byte-for-byte the ones every LoRA run used. 🔴 **`--no-deps` is load-bearing.** The first attempt
(job 1287243, cancelled) resolved the torch dependency and began installing a **second, CUDA-13
torch** into that directory — and `PYTHONPATH` outranks a venv's `site-packages`, so it would have
**shadowed** `envs/step4`'s torch 2.5.1+cu121 at run time. The ceiling run would then have been a
full fine-tune on a different torch from the LoRA runs it exists to be compared against: the exact
harm the freeze prevents, arriving through the door built to respect it. The env job now refuses if
`torch`, `numpy`, `nvidia*`, `triton`, `sympy` or `networkx` appear in the target directory.
Verified 2026-08-26: `torch 2.5.1+cu121`, `bitsandbytes 0.50.1`, no shadowing packages.

### "7.4 — the untuned-base arm needs a GPU"

It needs a GPU, but that was not what was stopping it. `4thJ_step7_generate.py` had **no code path
that skips the adapter** — `lora_request=LoRARequest(...)` was unconditional. A `--base-only` flag
now exists: new flag, default unchanged, **+48 / −5 lines**, every hunk guarded by `a.base_only`,
`node`-equivalent check being `py_compile` plus a `--help` surface test. It **implies
`--no-grammar` and says so out loud**, because a firing rate is the share the model gets wrong with
the **mask off** and a masked base arm would report zero by construction.

---

## C. One item is closed by a ruling, not by compute

**Step 4 "perturbation battery coverage."** All **20** recorded perturbation-side `G4.1` verdicts
have `n_scorable_strata = 0` — re-derived from the artefacts today, not quoted. `D-S4-11` (i)
re-labelled them NOT COMPUTED and the author refused the one change that would make them
non-vacuous. 🔴 **Re-running the battery is the one action guaranteed not to change the item.**
Also corrected: the coverage clause FAILs on **all three** folds, not on `es` and `uk` only.
Record: `Step4_docs/impl/2026-08-26_perturbation-coverage-closed-as-limitation.md`.

---

## D. One item can only be closed by a person

**1.4, the Eurostat entity-recognition enquiry.** Its Definition of Done is *sent, and the date
recorded* — explicitly **not** a note that Concordia is not a recognised entity, which is already
known. It goes to Concordia's Office of Research in the author's own name. A ready-to-send draft is
now on file at `Step1_docs/outputs_step1/1_4_eurostat_enquiry_DRAFT.md`, carrying the ask
(Recognised Research Entity status under Reg. (EU) 557/2013), the reason (the HETUS 2010 Scientific
Use File would widen the corpus from **3 countries to 17 with no harmonisation change**, the only
route at limitation C4) and a dated line to fill in afterwards. ⚪ No `G1.x` gate depends on it and
Step 1 closed on 2026-08-16 with it outstanding.

---

## E. Three items are genuine work, and it is running

### 7.5 — the re-sized rejection-sampled control

Sizes are the gate's **own** `implied_draws_for_parity`, read out of
`gates_step7_leg5_baseline.json` rather than recomputed: **es 75,531 / uk 16,795 / it 48,809**,
against measured control yields **6.8846 / 30.9615 / 10.6538 %**. Jobs **1287231 / 1287232 /
1287233**, submitted 2026-08-25 18:56, measured ETAs 3 h 41 / 2 h 26 / 2 h 02 at launch.

⚪ The existing 5,200-draw batches were **backed up to `*.bak_5200` and their sizes verified
non-zero** before the jobs could overwrite them: `4thJ_gates_step7.py` reads the canonical
`generated_leg5_<fold>_nogrammar.jsonl` filename, so parity has to be written *there*, and the old
artefact is a scored one.

🔴 This also decides `V7.a` on `uk`. At 5,200 draws only **9** uk strata carried 100 records against
a floor of 10, so `G7.7`/`G7.8` were FAILing on `uk` **for want of sample, not for want of
evenness**. At 16,795 the density roughly triples.

### 7.4 — the third arm

Jobs **1287234–36**, `--base-only`, **16,795 draws per fold**. ⚪ N is the `uk` parity number in
every fold rather than each fold's own, and that is a stated choice: the untuned 7 B runs to
`max_new_tokens` on nearly every prompt (**measured** ETA ≈ 10 h 26 per fold against 3 h 41 for the
fine-tuned arm at 4.5× the draws), while 16,795 already gives ≈ 3.2× the per-stratum density of the
registered 5,200 batches, and a firing rate is a *rate*.

The report tool is written and **already exercised on the two arms that exist**:
`tools/4thJ_step7_firing_rate_report.py`. It imports `stratum_key`, the alphabet builder and the
PERMISSIVE policy from `4thJ_gates_step7` rather than restating them, re-validates every record and
cross-checks against the generator's own `oracle_valid` stamp, and **refuses to present two arms as
three** — the missing-arm guard was seen firing on all three folds. Dry run, Leg 5:

| fold | fine-tuned unconstrained | fine-tuned constrained | strata ≥ 100 | stamp disagreements |
|---|---|---|---|---|
| es | **0.931154** | 0.000000 | 10 | 0 |
| uk | **0.690385** | 0.000000 | 9 | 0 |
| it | **0.893462** | 0.000000 | 11 | 0 |

🟢 The unconstrained figures reproduce `gates_step7_leg5_baseline.json` to six decimals, the
constrained arm reads **exactly zero** in every fold — the mask is not leaking — and the
generator's oracle and the scorer's oracle disagree on **0 of 31,200** records.

### The ceiling run

`4thJ_step4_ceiling_env.sh` (done, job 1287244) and `4thJ_step4_ceiling_fold.sh <fold> [control]`.
The **control arm** (job 1287240, `es`) runs with `PYTHONPATH` deliberately unset and must stop at
the optimiser with *"REFUSING rather than falling back to 32-bit AdamW"*. Written before the run:
**a clean exit from the control arm means the guard does nothing, and the real arm must not be
trusted until that is understood.** The real arm follows on `es`, Leg 5, effective batch held at
2 × 8 = 16 — the same as every Leg-4 and Leg-5 LoRA fold, because holding it constant is what makes
this a comparison of the *recipe* rather than of two schedules.

⚪ No adapter is written (`save_this` excludes `ceiling`) and no diagnostics run: the reading the
job exists for is the trainer's own loss curve beside the LoRA fold's.

---

## F. What is left, and it is all automatic

1. Jobs **1287231–33** land → re-score `4thJ_gates_step7.py` and read `G7.9` and `V7.a`/`G7.7`/
   `G7.8` on `uk` at parity.
2. Jobs **1287234–36** land → run `4thJ_step7_firing_rate_report.py` for the complete three-arm
   table and `firing_rate_by_stratum.csv`.
3. Ceiling **control** must be seen failing → then the real ceiling arm → the recipe comparison for
   the methods section.
4. Item **1.4** waits on a person, and only a person.

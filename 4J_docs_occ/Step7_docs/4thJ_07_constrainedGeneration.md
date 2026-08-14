# Step 7 — Constrained generation at scale, and schedule production

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 7. Validation: `4thJ_07_constrainedGeneration_val.md`

---

## STATUS

**OPEN. Mechanism decided by `RL12`. Nothing built.**

---

## AIM

Turn a synthetic population into 10⁵ to 10⁶ **structurally valid** diaries, and then into EnergyPlus
schedules.

---

## THE EPISODES-VERSUS-SLOTS CONFLICT, AND WHY EPISODES WIN

`RL12` argued for fixed 48 or 144 slots because a grammar cannot enforce an unbounded arithmetic sum,
and `sum(DUR) == 1440` looks like exactly that. `RL07` argued for episodes on a measured four-fold
token saving.

**Episodes win, and `RL12` supplies the reason in its own text.** The sum is neither unbounded nor
continuous: durations are multiples of 10 minutes and the total is fixed at 1440, so the running total
takes **145 distinct values**. A 145-state tally automaton is finite, therefore the constraint is
regular, therefore it is enforceable by the same FSM machinery. **We keep the token saving and the
hard guarantee.**

Written down because it is the kind of resolution that looks obvious afterwards and is expensive to
rediscover.

---

## STRUCTURE IS GUARANTEED, NOT ENCOURAGED

One percent malformed at one million records is ten thousand broken records, and 🔴 **silently
discarding them biases the population toward whatever the model finds easy** — the same class of error
as choosing a threshold that makes a gate pass.

* **Engine: vLLM with XGrammar**, under about 8 % latency overhead. Not a naive `LogitsProcessor` and
  not early Outlines, which `RL12` puts at 50 to 200 %. A hand-written processor is kept as a
  **unit-test oracle only**.
* 🔴 **The backbone must have a native vLLM kernel, and this became a selection criterion.** Read from
  `vllm/model_executor/models/registry.py` on 2026-08-14: `Olmo3ForCausalLM`, `Qwen2ForCausalLM` and
  `Qwen3ForCausalLM` map to native implementations; `Olmo2ForCausalLM` and `OlmoForCausalLM` map to
  `("transformers", "TransformersForCausalLM")`, the generic fallback. **This is the single reason the
  backbone is OLMo 3 rather than the OLMo 2 checkpoint that first looked best.**
* **XGrammar imposes no constraint on model choice.** It detects vocabulary type (`RAW`,
  `BYTE_FALLBACK`, `BYTE_LEVEL`) from the vocabulary itself. Checked in
  `python/xgrammar/tokenizer_info.py`, not assumed.

**Constraints encoded:**

1. the **duration tally** (145 states);
2. vocabulary membership for `ACT` and `LOC`;
3. **transition legality** — no workplace-to-home without an intervening travel episode;
4. **household-consistent co-presence**, via a small set of pre-compiled grammar variants indexed by
   household type, so nothing is compiled per sample.

---

## 🔴 REPORT THE CONSTRAINT-FIRING RATE, PER STRATUM

**100 % validity after masking is a property of the DECODER, not of the model.** The metric that
measures the model is how often the mask had to intervene.

* Reported for **three** models: untuned base (expect a high rate, over 35 %, or the constraint is not
  doing anything), fine-tuned unconstrained, fine-tuned constrained.
* 🔴 **Broken down by demographic stratum.** A firing rate concentrated in minority strata means the
  mask is doing the most work exactly where the model is weakest, and that **biases those strata**.
* Alongside it, the **unconstrained well-formedness rate**, which is the honest model-quality number.

Masking renormalises probability over the allowed set, which is **not neutral**. Audited by generating
an unconstrained rejection-sampled control batch and confirming the constrained batch's marginals have
not moved.

---

## DIARIES TO SCHEDULES

* Presence fraction per slot per dwelling, from location codes **with the code-11 indoor rule from
  Step 2B applied**.
* **Activity-resolved internal gains**, which is the part a presence fraction throws away.
* 🔴 **`Schedule:File`, not `Schedule:Compact`.** At urban scale, compact blocks bloat the IDF past
  twenty thousand lines per schedule.
* 🔴 **`Interpolate to Timestep = No`.** A step-wise presence signal interpolated linearly is no longer
  the signal we generated: it invents fractional occupants and smears appliance peaks. Inherited from
  3J and confirmed independently by `RL13`.
* Occupant count from household size via the `People` object, modulated by a 0-1 presence schedule.
* Residential **replaces** the baseline schedule, per the papers 2 and 3 convention.

---

## 🔴 THE GAP `RL17` PART D FOUND: HOW 365 DAYS BECOME ONE YEAR

**Nothing in this plan says how a household's 8,760 hours are assembled from generated days**, and the
two obvious rules are wrong in opposite directions.

* **Independent daily resampling** assumes an occupant with no habits. It washes out individual
  variance and **damps** coincident peaks.
* **Static repetition** of one generated weekday introduces no day-to-day entropy at all and
  **exaggerates** them.

Real people wake at 06:45 most weekdays, not at a fresh random time each morning.

**The experiment, before the Step 8 campaign is designed:** 100 households, one archetype, three
chaining rules — independent daily resampling, static repetition, and Markovian habit-coupled
resampling — compared on annual peak electrical power and on heating and cooling ramp rates.

🔴 **If peak demand moves by more than about 25 % between rules, the chaining method dominates the
downstream result regardless of transfer quality**, and Step 8 would be measuring our convention
rather than the model. **This is open decision 14.**

---

## WORK ITEMS

### 7.1 — Compile the grammar

The 145-state tally automaton, the vocabulary sets, the transition table, and the household-indexed
co-presence variants. **Pre-compiled, never per sample.**

### 7.2 — The throughput comparison, before the campaign is sized

🔴 `Olmo-3-1025-7B` has **no grouped-query attention** — 32 KV heads against Qwen's 4 — so its KV
cache is about **nine times** larger per token, against which the 34 % token saving buys back only
part. KV cache is what limits vLLM's concurrent batch.

Run `Olmo-3-1025-7B` against `Qwen/Qwen2.5-7B`: same grammar, same batch, diaries per second, peak KV
memory. **Record it.** The training-side argument for OLMo 3 is settled; the generation-side argument
is not, and if throughput dominates, the comparison arm and the primary can swap **without any of the
serialisation work being wasted**, because the tokenizer decision is what the corpus depends on.

### 7.3 — Generate

Per country, per fold. Constrained, at the Step 5 temperature, `p ≤ 0.98` if top-p is used at all.

### 7.4 — The three-model firing-rate report

Untuned base, fine-tuned unconstrained, fine-tuned constrained. Per stratum.

### 7.5 — The unconstrained rejection-sampled control batch

Generate without the mask, reject invalid records, compare marginals against the constrained batch.
**This is what makes the renormalisation claim checkable rather than asserted.**

### 7.6 — Decide the chaining rule (open decision 14)

Run the three-rule experiment above. Record the peak-demand spread. **Decide, and write down why.**

### 7.7 — Emit schedules

`Schedule:File`, `Interpolate to Timestep = No`, indoor rule applied, activity-resolved gains carried.

---

## OUTPUTS AND INTERFACES

| Artefact | Consumed by |
|---|---|
| `outputs_step7/generated_<country>.parquet` | Step 6 scoring |
| `outputs_step7/firing_rate_by_stratum.csv` | Step 7 validation; the results section |
| `outputs_step7/rejection_control.parquet` | Step 7 validation |
| `outputs_step7/throughput_comparison.md` | Campaign sizing |
| `outputs_step7/chaining_experiment.md` | Open decision 14; Step 8 |
| `outputs_step7/schedules/*.csv` | Step 8 |

---

## HOW IT RUNS

`sbatch`, `ps`, `-t 7-00:00:00`, one MIG instance per job. **No distributed generation across MIG
slices** — there is no peer-to-peer path between slices of one physical GPU.

---

## WHAT BLOCKS THIS STEP

Steps 3 (grammar is defined against the record format), 4 (the adapter) and 5 (the people).

**What this step blocks:** Steps 6, 8 and 9.

---

## DEFINITION OF DONE

1. Grammar compiled, all four constraint classes encoded, oracle agreement demonstrated.
2. Throughput comparison run and recorded **before** the campaign is sized.
3. Generation complete for every fold.
4. Firing rate reported for three models, per stratum.
5. Rejection-sampled control generated and marginals compared.
6. Open decision 14 closed with a written reason.
7. Schedules emitted with the indoor rule applied.
8. All Step 7 gates PASS and each has been seen failing.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — step document created

* 🔴 Item 7.2 is the one that could still reverse a settled decision. The KV-cache figure is
  arithmetic from measured config values, **not a benchmark**, and it is the only number in the
  backbone argument that has not been run.

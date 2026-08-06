# Employee prompt — V2-E6: re-specify gate R1 onto its siblings' basis

> 🔴🔴 **WITHDRAWN 2026-08-05, before any employee ran it. DO NOT EXECUTE THIS PROMPT.**
> The manager executed it directly, and the change it specifies was **already decided against on
> 2026-07-21** in the Step-5 closure entry (*"R1 reference NOT redefined … reads as gate-shopping"*).
> It was implemented, verified and **reverted**; the validator is byte-identical to its predecessor.
>
> 🟢 **What replaced it: the user chose option C on 2026-08-06.** R1 stays exactly as it is;
> a **new** gate **R5** is *added* on the sibling basis. The live instructions are in
> `3rdJ_L3_manager_prompt_2026-08-06_v2_optionC.md` and plan **§0.33**. 🔴 **The numbers in this
> file are still correct and still useful** — 1.567 pp weekday / 1.615 pp weekend are the values R5
> must reproduce. **Read it for the arithmetic; do not run it for the change.**
> **V2-E6 is now a user decision** — see plan §0.27 and the 2026-08-06 manager prompt §4.
> This file is kept as the record of what was proposed, not as an instruction.

**You are the employee.** Execute the task below and append a Progress Log entry on completion.
**Everything here runs on the local machine. Do not use the Speed cluster — no `ssh`, `scp`, `sbatch`
or `squeue`, not even a "cheap" `ls`.** If something appears to need it, do the local part and state
plainly what could not be done.

**Context to read first:** `improvements/v2/3rdJ_L3_v2_implementation.md`, **§0.26** (the diagnosis)
and the **V2-E6** row in the WP-E table. Do not re-derive the diagnosis — it is done and the numbers
below are its output.

---

## The situation

Three Step-5 validator gates look alike and are not:

| gate | channel | compares | both sides inside the output? |
|---|---|---|---|
| **2.2** | `hom30` | synthetic vs observed, split by day type | **yes** |
| **W1** — `3rdJ_05_censusLinkage_4split_val.py:625-641` | `wrk30` | synthetic vs observed, split by day type | **yes** |
| **R1** — `..._val.py:833-851` | `ret30` | matched **output** vs the donor **pool**, per (cycle × stratum) | **no** |

**R1 is the only one whose reference is the pipeline's own input.** Step 5 exists to re-compose that
pool to census marginals, so R1 measures the intended transformation and reports it as error.

**Already established (do not re-run to confirm):** applying R1's own statistic to the two channels
whose gates *pass* gives `hom30` **22.969 pp** and `wrk30` **27.263 pp**, against retail's **4.796 pp**.
That basis condemns all three channels. Signed means are `hom30` **−10.5 pp** and `wrk30` **+11.2 pp**
— the census employment re-weighting working as designed. The grouping is sound: the pool is
192,183 = **64,061 × 3**, a person × day-type grid.

🔴 **Retail is not thereby vindicated, and your write-up must say so.** Normalised by each channel's
own peak (95.02 / 46.92 / **4.57 %**), the deviations are 24.2 % / 58.1 % / **105.1 %** — retail's
discrepancy exceeds the entire retail signal. The small absolute number is a **floor effect**, not
skill. Fixing the basis makes the comparison meaningful; it does not make retail look good.

---

## What to do

### Step 1 — pre-register, before running anything

Write `scratchpad/e6_prereg.md` **first**, containing:

- Your predicted verdict for the re-specified R1: **PASS, WARN or FAIL**, with a predicted value in pp
  and a stated reason.
- Predicted values for the same statistic on `hom30` and `wrk30` under the re-specified basis (these
  should land near their existing gate values, 3.66 and 2.05 pp — if they do not, your
  re-specification does not match the siblings and that is a bug, not a finding).
- A reproduction guard: the re-specified code must leave **every other gate byte-identical**.

**Then do not edit it.** Score against it at the end and **report failed predictions as results.**

### Step 2 — implement

Re-specify R1 in `3rdJ_05_censusLinkage_4split_val.py` to match its siblings: **synthetic vs observed
rows within the output, split by day type** (`DDAY_STRATA == 1` weekday, `∈ {2,3}` weekend), exactly
as W1 does at `:625-641`.

- **Archive the predecessor first** to `archive/3rdJ_05_censusLinkage_4split_val.<date>_pre_r1respec.py`
  and verify the copy is non-empty **in the same command** (`[ -s "$BK" ]`).
- **Keep the old statistic as an INFO line**, labelled as the matched-vs-pool comparison, so the
  historical number remains visible and the change is auditable. Do not delete it.
- **Do not change the 3.0 pp threshold.**

### Step 3 — run and score

Run the validator locally on the shipped Step-5 outputs and score your pre-registration.
**The re-specified gate may still FAIL. That is an acceptable outcome — report it as-is.**

Verify the reproduction guard: every gate other than R1 must be unchanged.

### Step 4 — re-document (mandatory regardless of Steps 2–3)

Update the Step-5 documentation so R1's status changes from an unexplained failure to an explained
one. The substance:

> R1 compares the matched output against the donor pool — a basis on which `hom30` and `wrk30`
> deviate by 23 and 27 pp while passing their own gates. The number is not evidence about the retail
> channel. Separately, the shared absolute 3.0 pp bar is 3 % of `hom30`'s signal and 66 % of retail's.

**If you run out of time, Step 4 is the one that must still be done.**

---

## 🚫 Explicitly refused

**Do not raise R1's threshold to 5 pp**, or to any value that turns the current FAIL green. It leaves
the gate measuring the wrong thing, and this project has a standing rule against widening a band to
erase a FAIL. This refusal is recorded in the plan and on the board specifically so it is not
re-proposed as tidying-up. **If you believe the threshold is wrong, say so in the Progress Log and
leave it alone.**

**Do not re-tune anything on a gate.** `MIN_POOL` was selected on a gate crossing smaller than its own
noise (§0.25); repeating that pattern with better statistics is the same defect.

---

## Deliverable

1. `scratchpad/e6_prereg.md`, written before any run.
2. The re-specified validator, with the predecessor archived and the old statistic retained as INFO.
3. The scored result — pre-registration vs outcome, failures included.
4. The documentation change (Step 4).
5. A **Progress Log** entry appended to `improvements/v2/3rdJ_L3_v2_implementation.md` as **§0.27**,
   at heading level `###` (matching §0.24–§0.26), written with `cat >>` from a scratchpad file —
   **not** `Add-Content`.

**Do not** update the board or the manager prompt; the manager does that on closure.

## Notes

- `wc -l` for line counts. **Never PowerShell `Measure-Object -Line`** — it miscounts blank lines.
- Corrections are struck (`~~like this~~`), not deleted.
- A reader that returns 0.0 for what it cannot parse blames the system for its own gap — make parsers
  refuse instead.
- Nothing downstream is affected either way: R1 is a validator gate, it writes no schedule and feeds
  no simulation.

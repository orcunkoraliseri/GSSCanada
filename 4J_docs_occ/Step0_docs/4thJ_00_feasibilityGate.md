# Step 0 — Feasibility gate

### 4J HETUS LLM pipeline. Implementation record.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 0. Validation: `4thJ_00_feasibilityGate_val.md`

---

## STATUS

**✅ CLOSED 2026-08-14.** This step produced no code and no data. Its deliverable was a decision:
*is there a paper here at all, and may we do the thing the paper requires?* Four kill switches were
put to external deep research, all four returned, and one fired.

This folder exists so the closure is auditable from inside the step structure rather than only from
the parent document. **It is a record, not a work plan.** Nothing here is executable.

---

## AIM

Establish, before any data is acquired or any model is trained, that:

1. the microdata can be obtained at all;
2. the work is not already published;
3. a fine-tuned LLM is the right instrument rather than a fashionable one;
4. the resulting model may be released.

Any one of these returning "no" ends or reshapes the project. Three of the four changed the plan.

---

## THE FOUR KILL SWITCHES AND WHAT THEY RETURNED

| Switch | Report | Verdict | What it forced |
|---|---|---|---|
| Can we get the data? | `RL01` | **CLEARED with a route change** | Eurostat central microdata exists for the 2010 round only; Concordia is **not** a recognised research entity (4 weeks recognition + 8-10 weeks proposal). **Track B — national files we can download — became the primary corpus** |
| Is it already published? | `RL03` | **CLEARED** | Zero direct hits. Adjacent LLM-mobility work is the honest nearest neighbour and must be cited as such, not ignored |
| Is an LLM the right instrument? | `RL06` | **CLEARED CONDITIONALLY, and the condition is severe** | A from-scratch 10 M-parameter conditional Transformer beats the LLM on fidelity, cost, throughput and structural validity, and has **zero** transfer ability. **If the paper is not framed on transfer, the method is wrong** |
| May we release the model? | `RL10` | 🔴 **FIRED. NO** | Weights and adapters trained on restricted microdata may not be published. Deliverable becomes **synthetic dataset + code**, and a four-attack privacy audit joins validation |

---

## THE CONTRADICTION THIS STEP CREATED, AND HOW IT WAS RESOLVED

`RL04` and `RL15` both concluded the adapter **could** be released, reading the **model** licence
(Apache 2.0 permits it). `RL10` concluded it could not, reading the **data** agreement.

**Both are right about their own object, and the binding constraint is the stricter one, so `RL10`
governs.** `RL04` never read the data agreement and should not have opined on it. Recorded as
contradiction 1 in the parent document's vetting record rather than smoothed over, because it is
exactly the class of error that reaches a manuscript.

---

## WHAT STEP 0 DECIDED THAT EVERY LATER STEP INHERITS

* **The paper is framed exclusively on cross-national transfer.** Not on fidelity, not on cost, not on
  throughput. Step 6 is therefore where the paper is won or lost, and Steps 1 to 5 exist to make
  Step 6 possible.
* **The weights are never released.** This constrains Step 4 (what we build), Step 7 (what we ship)
  and the Data Availability statement. It is accepted by author decision 1 and is not treated as a
  wound.
* **Three mandatory baselines** enter Step 6 from `RL06`, the hardest of which — real N-1 diaries
  raked by IPF to the held-out country's marginals — became the pre-registered objective by author
  decision 4.
* **A privacy audit** joins Step 6's validation from `RL10`: loss-based MIA, reference-based MIA,
  prefix-prompted extraction, distance-to-closest-record.

---

## WHAT THIS STEP DID **NOT** ESTABLISH

Stated because a cleared gate reads as broader clearance than it is.

* It did **not** establish that we can obtain the *widest* corpus. Track A (Eurostat SUF, 17
  countries) needs an institutional recognition that **has still not been applied for.** See
  limitation F3 and Step 1.
* It did **not** establish that the transfer claim will succeed. It established that transfer is the
  only axis on which the method can win, which is a statement about the *design*, not the result.
* It did **not** survey the model landscape. `RL04`'s landscape work was superseded by our own
  measurement in Step 4; two of `RL18`'s later claims turned out to be false.

---

## EXIT CRITERION

**Met.** Corpus named, method chosen, release plan stated, and every one of the four questions
answered by a report that was read in full and vetted before any value was written into a plan
document.

---

## PROGRESS LOG

Append-only. Never delete or reformat an existing entry.

### 2026-08-14 — step closed

* `RL01`, `RL03`, `RL06`, `RL10` returned and vetted. Three of four changed the plan.
* `RL10` fired: no weight release. Deliverable changed to synthetic data + code.
* Two of the four answers (access latency, release prohibition) would each have been discovered in
  month four or later, after the corresponding work had been done the wrong way. **The two weeks
  spent on this step are the cheapest two weeks in the project.**

### 2026-08-14 (later) — one consequence reopened by a later decision

* Author decision 5 (HETUS only) removed ATUS, and with it **Track C** — the fully public stand-in
  pipeline that was `RL15`'s answer to `RL10`. **Step 0's release finding is unchanged; the
  mitigation it relied on is gone.** Recorded here because a closed gate whose mitigation later
  evaporates is a closed gate that no longer means what it meant. See open decision 13.

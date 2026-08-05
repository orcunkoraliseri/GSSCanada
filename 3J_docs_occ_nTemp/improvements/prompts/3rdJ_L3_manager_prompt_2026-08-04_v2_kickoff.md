# Manager prompt — 3J Leg-3 **v2 finalisation**, 2026-08-04 (LIVING HANDOFF)

Paste this whole file as the first message of a fresh session. It is self-contained.

> **This file is a LIVING HANDOFF, updated at every step of the work, not once at end of day.**
> The user opens a fresh manager session at any moment; whatever state the work is in, this file must
> already describe it. 🔴 **If you change the state of the work — a job lands, a gate flips, a
> decision is taken — update this file in the SAME response.** A handoff that lags the work is worse
> than none, because it is trusted.
>
> **Predecessors** (do not re-read unless a question below sends you there):
> `3rdJ_L3_manager_prompt_2026-08-05.md` — the Step-9 living handoff for the *simulation* thread
> (arm R, the K sweep, the H1–H11 gates). Still authoritative for anything about arms and the
> cluster. · `..._2026-08-04_progress.md` (the resize thread, §§0.1–0.17) ·
> `..._2026-08-03.md` (arm H closure) · `..._2026-08-03_PRE-ARMH.md` · `..._2026-08-02.md` ·
> `..._2026-08-01.md`.
>
> **This prompt opens a different thread from those.** They run the campaign. This one closes the
> project.

---

You are the **manager** on the 3J Leg-3 four-channel mixed-use tower BEM pipeline (residential /
office / retail / hotel). Work in `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\`.

Reply in **English** even though the user writes French. Casual, short — under ~100 words unless the
user asks for depth. Act first; skip the "before you launch" caveat lists and fold caveats into one
line afterwards.

---

## 0. Read this first — the one thing that changed

The project stopped being a simulation problem and became a **decision-and-writing** problem, and the
plan for that now exists as a document:

**`improvements/v2/3rdJ_L3_v2_implementation.md`** — the v2 implementation & finalisation plan.
**36 tasks in 7 work packages, with a table of contents, a traceability matrix and a Progress Log.
It is your task list. Read it before anything else.**

It is the *implementation* counterpart to
**`improvements/investigation/3rdJ_L3_backward_audit_2026-08-04.md`** — the *investigation* (13
findings B-1…B-13 with falsifiers). The audit says what is wrong and how to prove it; the v2 plan
says what to change, where, in what order, and how you will know it worked. **Both stay. Do not
merge them.**

### Why the direction changed

Eight simulation arms (`A`…`E`, `H`, `R`, plus the pre-fix baseline) moved office 71.08 → 81.52,
retail 75.43 → 89.87, hotel 178.29 → 271.40 — and produced **zero gate movement**. The score has
been **17 PASS / 0 WARN / 3 FAIL / 10 INFO** throughout.

The `Default_NECB` control — same geometry, envelope, climate and plant, **no injection at all** —
explains why:

| channel | uninjected control | injected `B_central` | band | diagnosis |
|---|---|---|---|---|
| **office** | **85.45** | 81.27 | floor **100** | the code's own reference implementation fails by 15 % before any occupancy signal exists → **band applicability** |
| **retail** | 92.13, 4/4 in band | 86.57 | `[80, 155]` | 54/56; the two misses are 79.82 and 79.96 vs an 80.00 floor — short by **0.23 %** and **0.06 %** → **gate rule** |
| **hotel** | 178.03 → **260.87** after the DHW resize | — | `[180, 300]` | the resize moved the **uninjected** control → pure plant effect, zero occupancy content → **plant + band** |

**None of the three FAILs is an occupancy problem, and occupancy is what the paper is about.**
Every remaining unblocking action is desk work.

🔴 **Do not propose a ninth arm to move `S9-EUI-*`.** The v2 plan contains exactly **one** new
EnergyPlus simulation (V2-E3), and it is a pre-registered *measurement* of retail's sensitivity to
two wrong constants — not a fix attempt. Nothing in the plan retrains Step 4.

---

## 1. Standing rules — non-negotiable

- 🔴 **NEVER run a blocking `srun`, `python`, or any computation on the Speed login node
  (`speed-submit2`). ALWAYS `sbatch`.** Flagged three times; one more is account suspension and all
  job progress is lost. Allowed on the login node: `sbatch`, `squeue`, `sacct`, `scancel`,
  `scontrol`, `cd`, `ls`, `scp`, `module load`, and single-file `tail`/`head`/`grep`/`wc -l`/`cat`.
  `tar`, `find`, `python`, **`md5sum`** are **not** — put hash checks inside the job.
  **A loop of greps over 56 files is not a single-file peek — put it in a job.**
  - The login shell is **tcsh**: no `for` loops, no `2>&1`, **no `2>/dev/null`** (it is a parse error
    that fails *silently* — stdout comes back empty and reads as "no result"; that cost 3.3 h on
    2026-08-03). One short line.
  - **Nested `ssh speed "... ssh speed \"...\""` fails** with `Permission denied (publickey)`. One
    `ssh` per Bash call.
- **Every job requests `-t 7-00:00:00` minimum.** No exceptions, not even one-minute probes.
- Cluster commands single-line, each labelled explicitly "locally" or "on the cluster".
- 🔴 **Never widen a band or relax a gate to erase a FAIL.** The remedy is **re-specification** (from
  an archetype-matched, independently-sourced reference, pre-registered *before* looking at our
  number) or an explicit **INFO / N-A with the limitation published**. **A miss is recorded, not
  repaired.**
- **Pre-register** every prediction with numeric thresholds, in the Progress Log, before the run.
- **A gate counts as validation only once it has been *seen failing*** on a deliberately broken
  input. Before recording any PASS, ask: *what result would have made this fail?*
- **A logged number is not evidence.** Re-derive from the artefact's own columns — especially when it
  matches a target exactly.
- **A citation is not evidence until it has been opened.**
- **Struck, not deleted.** Corrections are strikethrough + restatement, in place.
- **`Leg2_2-split/` is frozen** — paper-ready, read-only. Reading its IDFs/SQL is fine.
- **Never count lines with PowerShell** (`Measure-Object -Line` counts blank lines as zero) — use
  `wc -l`. **Never append to a Progress Log with `Add-Content`** (PS 5.1 double-encodes UTF-8) — use
  a bash heredoc.
- **Cheap models for cheap work.** Never scan a large file in your own context — hand it to a
  Haiku/Sonnet employee with a script and ask for the small result table back. Never spawn a
  background agent without setting its model. Do not poll jobs; minimum monitoring interval 30 min.
- **Do not call the Agent tool, workflows, or deep-research unless the user asks.**

---

## 2. Where everything lives

| What | Where |
|---|---|
| **The v2 plan — your task list** | `improvements/v2/3rdJ_L3_v2_implementation.md` |
| The backward audit (investigation) | `improvements/investigation/3rdJ_L3_backward_audit_2026-08-04.md` (2,317 lines, md5 `fd41ee1d`; `_2026-08-03.md` is a byte-identical snapshot) |
| Blind replications | `improvements/investigation/investigationPrompts/REPORT_codex_backward_audit.md` (C-1…C-5), `REPORT_gemini_backward_audit.md` (G-1…G-6) |
| Literature reports | `improvements/investigation/deepResearch Prompts/` (R1, R2, R3) |
| Step-9 Progress Log (7,646 lines) | `improvements/v1/3rdJ_L3_improvements_step9.md` — **read the Reader's Guide first** |
| **Step-9 Reader's Guide** | `improvements/v1/3rdJ_L3_step9_READER_GUIDE.md` — current state, 8 open questions, the reversal register, the vacuous-gate catalogue |
| Step 5/6/7 fix log | `improvements/v1/3rdJ_L3_improvements_step5_6_7.md` |
| **Master pipeline docs (the WP-C targets)** | `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md` (438 ln) · `..._Overview.md` (227 ln) |
| Step-9 gate scorer | `Leg3_4-split/Step9_docs/3rdJ_09_activityDrivenLoads_4split.py` |
| §8E aggregator | `Leg3_4-split/Step8_docs/3rdJ_08E_aggregate_4split.py` |
| Injector | `eSim_bem_utils/commercial_integration.py` |
| 2J converter (the B-13 target) | `eSim_occ_utils/21CEN22GSS/21CEN22GSS_occToBEM.py`, `..._HH_aggregation.py` |
| 2J submitted manuscript | `2J_docs_occ_nTemp/writing/fullSet/readySubmission.md` |
| Arm tables / scorecards | `_local_armR_cache/agg_H_allfix/`, `agg_R_resize/`, `outputs_step9_H/`, `outputs_step9_R/` |
| Cluster campaigns | `speed:/speed-scratch/o_iseri/step8_4split/campaign/out_{A,B,C,D,E,H}_*`, `out_R_resize` |

⚠️ The step logs moved into `improvements/v1/` — paths quoted inside older documents as
`improvements/3rdJ_L3_improvements_step9.md` now resolve to `improvements/v1/...`.

---

## 3. State of the audits — 24 findings, 3 falsifiers run

Three separate audits, **numbering stays separate permanently, never merged** — the three-way
comparison *is* the result.

- **B-1 … B-13** — this project's backward audit (Steps 1–4 + linkage, never re-audited before
  2026-08-03).
- **C-1 … C-5** — Codex, blind, working from **code and artefacts**. Measured 4 of 5; erred once
  (a cross-leg category error).
- **G-1 … G-6** — Gemini, blind, working from **claims and provenance**. Three of its six
  (G-3, G-5, G-6) cite as evidence the very document that already contains the correction.

**Reproduced blind:** C-4 ≡ B-3 · G-1 ≡ B-8.

**Three falsifiers have been run** (B-1, B-11, B-12) — of thirteen. Everything else is argued, not
measured; the v2 plan's status vocabulary keeps that honest.

### The four things a fresh session most often gets wrong

1. 🔴 **B-1 was falsified by its own falsifier.** Its headline — "zero intra-household presence
   diversity" — is **false**: 3,499 / 16,367 = **21.38 %** of multi-person households carry
   non-identical co-resident vectors (a lower bound), and the error sign is **inverted** (a
   fractional expectation *smooths* peaks; B-1 and G-4 both argued it sharpens them). B-1 survives
   only on a different, verified mechanism: Step 5 computes the household **maximum** into
   `HH_hom30_*` (`3rdJ_05_censusLinkage_4split.py:1037`) and Step 7 **never reads it**
   (`3rdJ_07_aug_to_bem_4split.py:309` takes a per-member mean). **B-1 does not reach 2J.**
2. **B-13 is the only finding reaching a submitted paper**, and its falsifier is **unrun**.
   `21CEN22GSS_occToBEM.py:144-145` computes `occPre × (occDensity + 1)` then `.clip(upper=1.0)`;
   neither operation appears in the manuscript, and `occDensity` sums per-member GSS companion
   counts, so co-residents are double-counted and the clip is exactly where that would have
   surfaced. **This is task V2-A1 and it is the next action.**
3. **G-2 hits a blocking gate.** `dr_L3-03:13` recommends the hotel band 180–300; its own Table 2 at
   `:58-68` lists **6 of 11** reference rows above 300 — every Large Hotel row. **300 is the exact
   ceiling `S9-EUI-hotel` fails against.** Licence to **re-derive**, never to widen. Caveat Gemini
   did not state: the band is evidently derived from the two NECB-2017 rows and our tower is
   NECB-based, so "any code-compliant Large Hotel auto-FAILs" overstates it.
4. **The vacuous-gate catalogue double-numbers itself.** `READER_GUIDE §4` says **12** classes; the
   `2026-08-05` handoff says **thirteen** with **#13 = the conjunction gate**; the audit and its
   README both propose C-3's *severity-vacuous* gate as "#13". The v2 plan renumbers it **#14**.
   Four documents currently disagree — reconciling them is a step of V2-D1.

---

## 4. What to do, in order

Full detail, with aim / steps / expected result / test method per task, is in
`improvements/v2/3rdJ_L3_v2_implementation.md §4`. This is the short form.

| Phase | Tasks | Why here |
|---|---|---|
| **0 — today** | **V2-A1** — run the B-13 falsifier | Minutes, and the only open item touching a manuscript under review |
| **1 — the critical path** | **V2-B1** office band applicability · **V2-B2** hotel band re-derivation · **V2-B3** retail gate rule | The three blocking FAILs. **No compute.** Authorised 2026-08-02, still unexecuted — four more arms were run instead |
| **2 — in parallel, cheap** | V2-C1…C5, C7, C10 (doc corrections, exact line numbers given) · V2-D1, V2-D2 (gate severities) | Independent of everything; removes every wrong number a reviewer hits first |
| **3 — submit early** | **V2-E1** (+ V2-D5 → V2-E2) — persist retail probabilities in 04E, recompute PR-AUC / F1 / RW8 free-running | The one high finding needing compute (**B-3** ≡ **C-4**), one ~40-min GPU job. Queue time is the constraint — submit while phase 1 is being written |
| **4 — decisions land** | V2-B4 deliverable arm · V2-B5 mean-vs-max · V2-C6, V2-D3, V2-D4 | Consume phase-1 output |
| **5 — measure** | V2-E3 sensitivity cell · V2-E4 multi-seed · then **V2-E5** re-score | **No new arm** |
| **6 — citations** | V2-F1, V2-F2, V2-F3 → V2-C8, V2-C9, V2-D6 | Slow, interruptible, blocks only the write-up |
| **7 — close** | V2-G1 … V2-G5 | Freeze, flip PLANNED → DONE, write limitations, close all 24 findings |

**The critical path is phase 1 — reading and deciding, not compute.**

### Start here, concretely

1. Read `improvements/v2/3rdJ_L3_v2_implementation.md` end to end (§0 → §10). It is your task list.
2. Ask the user which they want first: **V2-A1** (minutes, touches the submitted paper) or
   **phase 1** (the three band/gate decisions that unblock Step 9). Recommend **V2-A1 first** — it
   is short and it is the only item with an external clock on it.
3. Whatever you execute, **append a Progress Log entry to §10 of the v2 plan** using the template
   there, via a bash heredoc, and update this handoff in the same response.

---

## 5. What "finished" means

v2 closes when all of these hold (full checklist: v2 plan §9):

- All **24** findings (13 B + 5 C + 6 G) carry a terminal status — `FIXED`,
  `ACCEPTED-AS-DOCUMENTED`, or `WITHDRAWN`.
- The three EUI gates are resolved **as questions**: passing against a derived reference, or INFO by
  demonstrated inapplicability with the limitation published — **none by widening**.
- Step 9 re-scored **once**, against a pre-registered prediction, with every mismatch reported.
- Every gate touched by WP-D has been **seen failing** on a deliberately broken input.
- Both master pipeline documents satisfy all 12 rows of the v2 plan's §7 acceptance table.
- The deliverable arm is named and frozen with full provenance (MD5, job IDs, code hash).
- The 2J-facing decision is made, and drafted if needed.
- Every load-bearing citation has been **opened**.

---

## 6. Open questions the user has not yet answered

Ask these when they become blocking — not before, and not all at once.

| | Question | Blocks | Recommendation |
|---|---|---|---|
| 1 | If V2-A1 shows B-13 is material, how is it routed to the journal — erratum, revision during review, or recorded-only? | V2-A2 | Depends on the magnitude; get the number first |
| 2 | Is a re-run acceptable if V2-B5 chooses the **max** over the mean? | V2-D3 | The mean is defensible if *chosen*; ask only if the max wins |
| 3 | Which K, if V2-B4 lands between H (K = 1) and R (K = 10)? | V2-G1 | Choose on plant-sizing physics (49.2 K target), never on gate movement |
| 4 | Does the ±2 pp EUI-share gate survive the corrected Service/MEP share (20.6 / 21.4 %, not ~52 %)? | V2-C2 | Check the aggregator's code, not just the prose — this is the one prose defect that could be a real one |

---

## 7. Handoff log

**2026-08-04** — v2 thread opened. Authored `improvements/v2/3rdJ_L3_v2_implementation.md` (36 tasks,
7 work packages) and this prompt. Nothing executed yet; every task is `TODO`. Found while writing:
the vacuous-gate catalogue double-numbers class #13 across four documents (see §3, item 4). Next
action: **V2-A1**.

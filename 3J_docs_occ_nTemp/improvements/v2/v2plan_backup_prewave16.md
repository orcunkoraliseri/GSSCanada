# 3J Leg-3 — v2 Implementation & Finalisation Plan

**Opened 2026-08-04.** This is the **implementation** document for Leg 3: the ordered, executable
list of corrections and completions that takes the four-channel pipeline from *diagnosed* to
*finished*.

It is the counterpart of, and downstream from, the **investigation**:
`improvements/investigation/3rdJ_L3_backward_audit_2026-08-04.md` (13 findings B-1 … B-13, plus the
two blind replications C-1 … C-5 / G-1 … G-6). The audit says **what is wrong and how to prove it**.
This document says **what to change, in which file, in what order, and how we will know it worked.**

The two documents this plan must ultimately leave correct and final:

| Master document | Role |
|---|---|
| [`Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md`](../../Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md) | The detailed step-by-step pipeline description (438 lines) — the paper's methods section in prose |
| [`Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md`](../../Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md) | The one-page ASCII overview + gate tables (227 lines) — the graphical-abstract companion |

Neither is a scratch file. **Both are read by external reviewers, and both currently contain numbers
this project has since measured to be wrong.** Fixing them is a work package here, not a footnote.

---

## TABLE OF CONTENTS

| § | Section | What it answers |
|---|---|---|
| [0](#0--is-the-audit-an-investigation-or-an-implementation-document) | Is the audit investigation or implementation? | Why this document had to exist |
| [1](#1--scope-and-definition-of-done) | Scope and definition of *done* | What "finalise the project" means, concretely |
| [2](#2--where-the-project-actually-stands-2026-08-04) | Where the project actually stands | The one page to read before touching anything |
| [3](#3--the-rules-that-govern-this-document) | The rules that govern this document | Non-negotiable method constraints |
| [4](#4--work-packages-and-tasks) | **Work packages and tasks** | The executable list — WP-A … WP-G |
| [4a](#wp-a--the-submitted-paper-first) | WP-A — the submitted paper first | 2 tasks · the only ones touching a paper under review |
| [4b](#wp-b--the-three-blocking-decisions-desk-work-no-simulation) | WP-B — the three blocking decisions | 5 tasks · unblocks Step 9 without a single new run |
| [4c](#wp-c--master-document-corrections-writing-only) | WP-C — master-document corrections | 10 tasks · exact file + line, writing only |
| [4d](#wp-d--code-and-gate-corrections) | WP-D — code and gate corrections | 6 tasks · small, local, all testable |
| [4e](#wp-e--the-compute-work) | WP-E — the compute work | 5 tasks · the *only* jobs; none retrains Step 4 |
| [4f](#wp-f--citations-owed) | WP-F — citations owed | 3 tasks · a citation is not evidence until opened |
| [4g](#wp-g--final-assembly-and-freeze) | WP-G — final assembly and freeze | 5 tasks · what "finished" looks like on disk |
| [5](#5--sequencing) | Sequencing | Dependency graph and the recommended order |
| [6](#6--traceability-every-finding-maps-to-a-task) | Traceability | Finding → task, both directions, nothing dropped |
| [7](#7--what-the-two-master-documents-must-look-like-when-v2-closes) | Target state of the master docs | The acceptance test for WP-C |
| [8](#8--risk-register) | Risk register | What could still invalidate the result |
| [9](#9--definition-of-done--closing-checklist) | Closing checklist | Sign-off conditions |
| [10](#10--progress-log) | **Progress Log** | Append-only execution record |

---

## 0 — Is the audit an investigation or an implementation document?

**It is an investigation document, and deliberately so.** Direct answer to the question that opened
this file.

| | `investigation/3rdJ_L3_backward_audit_2026-08-04.md` | **this document** |
|---|---|---|
| Question it answers | *Is anything wrong, and how would I prove it?* | *What do I change, and how do I know it worked?* |
| Unit of content | a **finding** (B-1 … B-13) with a written **falsifier** | a **task** with aim / steps / expected result / test method |
| Success | the falsifier runs and returns a verdict — including "the finding was wrong" | the artefact on disk changes and a check passes |
| Ends when | every finding is established or withdrawn | every task is DONE and the closing checklist signs off |
| May it edit pipeline code? | **No.** It measures; it does not touch | **Yes** — that is its entire purpose |

The audit's own *Recommended order of work* (three successive revisions, latest 2026-08-04 evening)
is the closest thing it has to a plan — but it is ordered by *evidence gained per unit cost*, mixes
"open a PDF" with "run a GPU job", and has no owner, no test method, and no progress log. That list
is the **input** to §4 below; it is not a substitute for it.

Both documents stay. The audit is append-only and keeps struck claims in place — that is where
provenance lives. This file is where execution lives.

---

## 1 — Scope and definition of *done*

**Goal: Leg 3 reaches the same state Leg 2 reached — validated end-to-end, internally consistent,
and defensible in front of a reviewer — so the 3rd-Journal manuscript can be written from it.**

In scope:

1. Every backward-audit finding is **closed**: fixed, or explicitly accepted-as-documented with the
   reason written down.
2. The **three blocking Step-9 FAILs** (`S9-EUI-office`, `S9-EUI-retail`, `S9-EUI-hotel`) are
   resolved *as questions* — each one either passes against a correctly-derived reference, or is
   converted to INFO by showing the reference **inapplicable**, with the limitation published.
3. The two master pipeline documents contain **no number the project has since measured otherwise**.
4. One arm is named **the deliverable**, its provenance recorded (MD5, job IDs, code hash).
5. The 2J-facing items are settled — the submitted manuscript is either confirmed correct or a
   correction/limitation is drafted for it.

Out of scope, explicitly:

- **Re-running Step-4 training.** Nothing in the audit or in this plan requires it. Stated three
  times in the audit; restated here so nobody proposes it.
- **New simulation arms aimed at moving `S9-EUI-*`.** Eight arms produced zero gate movement, and
  the uninjected control proves none of the three failures is an occupancy problem. WP-E contains
  exactly one new simulation, and it is a **measurement**, not a fix attempt.
- **Any modification under `Leg2_2-split/`.** Leg 2 is closed and paper-ready. Reading is fine.
- Restaurant channel, grocery/merchandise split, amenity-zone modulation — all previously and
  deliberately deferred; unchanged here.

---

## 2 — Where the project actually stands (2026-08-04)

| | |
|---|---|
| **Campaign** | 56 cells = 14 scenarios × 2 geometries (`Tall`, `SuperTall`) × 2 cities (`CLG`, `MTL`) |
| **Step-9 score** | **17 PASS / 0 WARN / 3 FAIL / 10 INFO**, unchanged across the last several arms |
| **The 3 FAILs** | `S9-EUI-office`, `S9-EUI-retail`, `S9-EUI-hotel` — all three are *absolute EUI level vs an external band* |
| **Arms run** | 8 (`A`…`E`, `H`, `R`, plus the pre-fix baseline). Net: office 71.08 → 81.52, retail 75.43 → 89.87, hotel 178.29 → 271.40 |
| **Gate movement across those 8 arms** | **zero** |
| **Backward audit** | 13 findings; **3 falsifiers run** (B-1, B-11, B-12); B-1 falsified and corrected; B-13 raised and unrun |
| **Blind replication** | Codex `C-1…C-5`, Gemini `G-1…G-6`. C-4 ≡ B-3 and G-1 ≡ B-8 reproduced independently |
| **What is not in doubt** | attribution closes to ≤ 1e-6 on every cell; 27 of 30 gates pass, including all four that test the actual scientific claim (`S9-INJECTION`, `G8o/G8r/G8h`, `S9-COINC`, `S9-D20`) |

### The one diagnosis this whole plan is built on

The `Default_NECB` control — same geometry, envelope, climate and plant, **no injection at all** —
settles the three FAILs:

| channel | uninjected control | injected `B_central` | band | what that means |
|---|---|---|---|---|
| **office** | **85.45** | 81.27 | floor **100** | the code's own reference implementation fails the band by 15 %, and injection moves office *down*. → **band applicability** |
| **retail** | 92.13, 4/4 in band | 86.57 | `[80, 155]` | arm R is 54/56; the two misses are 79.82 and 79.96 against an 80.00 floor — short by **0.23 %** and **0.06 %**. → **gate rule** |
| **hotel** | 178.03 → **260.87** after the DHW resize | — | `[180, 300]` | the resize moved the **uninjected** control by the same mechanism ⇒ pure plant effect, zero occupancy content. → **plant + band** |

**None of the three is an occupancy-modelling problem, and occupancy is what the paper is about.**
Every remaining unblocking action is desk work. That is why WP-B contains no simulation.

---

## 3 — The rules that govern this document

These are project standing rules. They are restated because this is the document where they are
easiest to break.

1. **Never widen a band to erase a FAIL.** A band may be **re-derived** from an
   archetype-matched, independently-sourced reference, *pre-registered before looking at our
   number* — or shown **inapplicable** and demoted to INFO with a published limitation. Widening it
   to fit is forbidden and is how a gate becomes vacuous.
2. **Pre-register.** Any task whose output is a number vs a threshold writes the prediction, with
   the numeric threshold, into the Progress Log **before** the run. Anything not pre-registered is
   weaker evidence and must say so.
3. **A gate is not validation until it has been seen failing** on a deliberately broken input.
   The *severity-vacuous* gate — one that computes a real failure and declines to call it one —
   was raised by Codex on 2026-08-04 (C-3) and is fixed by task **V2-D1**.
   > 🔴 **Numbering collision, found 2026-08-04 while writing this plan.** The catalogue is at
   > **12** classes in `3rdJ_L3_step9_READER_GUIDE.md §4`, but the `2026-08-05` manager handoff
   > already says **thirteen**, with **#13 = the conjunction gate / monotonicity clause across a
   > saturation boundary**. The audit and its README both propose the severity-vacuous gate as
   > "#13", which is **taken**. It should be **#14**, and the Reader's Guide §4 is two classes
   > behind the handoff. Reconciling the catalogue across all four documents is part of **V2-G5**.
4. **A logged number is not evidence.** Re-derive from the artefact's own columns before quoting a
   before/after figure, even when it matches a target exactly.
5. **A citation is not evidence until it has been opened.** WP-F exists for this reason.
6. **Struck, not deleted.** Corrections in this file are written as strikethrough plus the
   correction, never by removing the original.
7. **Cluster discipline.** Every job goes through `sbatch`, single-line, `-t 7-00:00:00` minimum.
   No `python`, no blocking `srun`, no directory scans on the login node — ever.
8. **`Leg2_2-split/` is frozen.** Read-only.
9. **Do not count lines with PowerShell**, and **do not append to Progress Logs with
   `Add-Content`** — use `wc -l` and a bash heredoc respectively.

---

## 4 — Work packages and tasks

Task IDs are `V2-<WP><n>`. Each carries **aim / steps / expected result / test method** per the
project's task format, plus cost, dependencies, and the finding it closes.

Status vocabulary: `TODO` · `IN PROGRESS` · `DONE` · `BLOCKED` · `ACCEPTED-AS-DOCUMENTED` ·
`WITHDRAWN`.

### 🔴 WHERE WE ARE RIGHT NOW — read this block, not the table

*Updated 2026-08-05. **32 of 45 done · 2 in progress · 6 ready to start · 5 blocked.** Nothing is
waiting on the user any more: **all three WP-B decisions are taken**, so WP-C and WP-D are unblocked
and the critical path is now ordinary work.*

```
DONE        ████████████████████████████████░░░░░░░░░░░░░  32 / 45
IN PROGRESS ██                                              2
READY       ██████                                          6
BLOCKED     █████                                           5
```

**🔄 IN PROGRESS — the two things being worked on now**

| ID | What is actually left to do |
|---|---|
| **V2-C3** | Rewrite the retail-density line in both master docs. It is a **unit-label error**, not a discrepancy (`3.72 occupants per 1000 ft² = 24.97 m²/person`); the real defect is that retail uses the **office** density 24.97 where NECB gives **29.97**. |
| **V2-D4** | The provenance half is done. The **values** half is now unblocked by the WP-B decisions — sync the scorer's `BENCH` to the decided bands. |

**⬜ READY TO START — unblocked, in the order I would do them**

| # | ID | Why it is next |
|---|---|---|
| 1 | **V2-C6** | Just unblocked. Propagates all three WP-B decisions into both master docs. Do it before anything re-scores. |
| 2 | **V2-D10** | Implement the decided per-object DHW resize (`LAUNDRY` K ≈ 7, the rest K = 1). |
| 3 | **V2-D9** | Decide `NECB-C-*` for retail. Only lever in weeks that could move `S9-EUI-retail`. |
| 4 | **V2-E2** | Runnable locally, no cluster wait. |
| 5 | **V2-E1** | 1 GPU job. Closes the last high finding, B-3. |
| 6 | **V2-E4** | 4 CPU jobs, `sbatch`, `-t 7-00:00:00`. |

**⛔ BLOCKED — and by what, precisely**

| ID | Waiting on |
|---|---|
| **V2-E5** | WP-C + WP-D landing first (it re-scores them) |
| **V2-G1** | WP-E finishing |
| **V2-G2** | WP-C finishing |
| **V2-G3** | WP-B ✅ done, WP-A ✅ done → **unblocks as soon as C6 lands** |
| **V2-G5** | everything above |

**✋ Waiting on the user: nothing.** B2, B3 and B4 were all decided 2026-08-05. The only optional
item is V2-A2's extra clarifying clause, and A2 is already marked DONE.

---

### Summary table

**Legend: ✅ done · 🔄 in progress · ⬜ ready to start · ⛔ blocked**

*One-line statuses only. The full reasoning for every entry is in the per-task sections below and in
the Progress Log at the end of this file.*

| ✔ | ID | Task | Cost | Closes | Status (one line) |
|---|---|---|---|---|---|
| ✅ | **V2-A1** | Run the B-13 falsifier on the 2J converter | 1 script, minutes | B-13 | DONE 08-04 · B-13 withdrawn, no erratum owed |
| **V2-A2** | Draft the 2J residential-channel correction + limitation paragraph | writing | B-1, B-13 | **DONE** 08-04 · clause in both .md; .docx N/A |
| **V2-B1** | Settle the **office** band applicability question (Q1) | 2–4 h reading | 3 FAILs → 2 | **CAUSE LOCATED** 08-04 · heating 17% vs 35-45%; vintage mismatch |
| **V2-B2** | Re-derive the **hotel** as-modelled band from an archetype-matched reference | 2 h | G-2, decision #2/#3 | **PARTIAL** · contradiction proven; ~~blocked on V2-F4~~ ~~→ no external replacement band exists~~ → 🔴 **REVISED 08-05 by V2-F6: a vintage-matched reference DOES exist and we retrieved it ourselves — Large Hotel 90.1-2019 = 284.44 (6A) / 299.28 (7). The 300 ceiling is 1.0 % from the vintage-matched value, so the "2004 band on a 2019 building" objection is DEAD and `S9-EUI-hotel` is not a vintage artefact.** Remaining gap = NECB-2017 Montreal/Calgary vs 90.1-2019 Rochester/Int. Falls. ~~Still a user decision~~ → **DECIDED 08-05 by the user: keep the 300 ceiling, re-cite it to 90.1-2019.** Value unchanged, citation moves off the unsupported 2004 anchor rows onto the file we parsed. `S9-EUI-hotel` **stays FAIL on 21/56**; the archetype gap is written up as a limitation, not as a tolerance. **No band moved to erase a FAIL** |
| **V2-B3** | Decide the **retail** gate rule: 56/56 vs a stated tolerance | 1 h + writing | Q3, B-5 | **DECIDED** 08-04 · median-in-band |
| **V2-B4** | Name the deliverable arm (H vs R vs a K between them) | analysis, no run | Q4, Q5, Q6 | **RUN DONE, DECISION REOPENED** 08-04 · 112/112 cells · **4P/2F vs the pre-registered table** · elasticity 0.33 not 0.85-0.95 and `S9-EUI-hotel` still FAILs (21/56 over the ceiling) · **mechanism = ONE object (`LAUNDRY`), so a global K is the wrong instrument** — ~~per-object sizing recommended, user decision~~ → **DECIDED 08-05 by the user: PER-OBJECT resize, `LAUNDRY` alone at K ≈ 7 (target = `BOOSTER`'s internal 71.34 K), the other 15 heaters stay at K = 1.** Code change to `resize_idf()`, not another arm. **Verification owed and must be pre-registered: the discriminator is `LAUNDRY`'s own slope moving off −0.98, NOT the aggregate elasticity** — share-reweighting can move the aggregate on its own, so an aggregate-only check is a gate that cannot fail |
| **V2-B5** | Decide Step-7 residential aggregation: mean or max | writing, maybe 1 re-run | C-1, B-1 (surviving half) | **DECIDED** 08-04 · mean stands |
| **V2-C1** | Floor areas in both master docs | 10 min | G-1, B-8 | **DONE** 08-04 |
| **V2-C2** | Service/MEP "~52 % gross" → measured 20.6 / 21.4 % | 10 min | B-8 | **DONE** 08-04 · aggregator clean |
| **V2-C3** | Retail occupant density ~3.7 → parsed 25.0 m²/person | 20 min | B-11 | ~~**DONE** 08-04~~ · 🔴 **REOPENED 08-05 by V2-F8 — it is a UNIT-LABEL error, not a discrepancy.** NECB office = **3.72 occupants per 1000 ft²** = **24.97 m²/person**; `25.0 / 3.7 = 6.76` **is** B-11's "6.8× gap". Same quantity, two units. **The modelling defect B-11 alleged does not exist.** What survives: retail runs the *office* density 24.97 where NECB specifies **29.97** for `Retail - sales` — 20 % overcrowded, plus the wrong schedule letter |
| **V2-C4** | The 0.95 retail peak — restate or re-source | 30 min | B-11, B-5 | **CLOSED 08-05 by V2-F8 — `0.95` is UNSOURCED.** ~~re-source not answerable in-repo~~ ← that grep proved only that *our IDF* has no retail schedule, never that NECB lacks one. NECB publishes **schedule C** for retail: weekday occupancy peak **0.80** at 16:00, no midday dip. `0.95` is neither the retail peak (0.80) nor the office peak (0.90). We run retail **18.75 % hot at peak on an office-derived shape** |
| **V2-C5** | "~2.1–2.3 %, stable across cycles" → 1.50–2.14 %, −25 % | 20 min | B-4 | **DONE** 08-04 |
| **V2-C6** | Propagate the WP-B band decisions into both master docs | 20 min | follows B1–B3 | BLOCKED by WP-B |
| **V2-C7** | Fix the two citation defects inside the Step-9 documents | 10 min | audit item 5f | **DONE** 08-04 (no-op) |
| **V2-C8** | Fix the Richardson citation everywhere it appears | 15 min | audit item 13c | **DONE** 08-04 · 6 sites, verdict unaffected |
| **V2-C9** | Write the `MIN_POOL` methods justification | writing | B-2 | **DONE** 08-04 · anchor refuted; claim shrunk to honest size |
| **V2-C10** | Record the three self-refuting Gemini findings as verified-no-action | 10 min | G-3, G-5, G-6 | **DONE** 08-04 |
| **V2-D1** | RW6 severity — `hard=False` can only WARN | small code | C-3, class #14 | **DONE** 08-04 · seen failing |
| **V2-D2** | ISR-raw → WARN with the deviation stated | one line | B-6 | **DONE** 08-04 |
| **V2-D3** | Implement the V2-B5 aggregation decision in Step 7 | small code | C-1 | **DONE** 08-04 · hand-verified |
| **V2-D4** | Sync the scorer's `BENCH` to the decided bands | small code | Q7 | **PARTIAL** 08-04 · provenance DONE (office `src=` resolved to nothing; new `..._bench_provenance_check.py`, falsified 3/3, **F2 = the shipped string**) · **values still BLOCKED by WP-B** |
| **V2-D5** | Step-4 run manifest + persisted validation IDs | hours | C-5 | **DONE** (local) · E2 unblocked; ckpt hash needs cluster |
| **V2-D6** | Promote the retail **shape** gates to PASS/FAIL | small code | B-5 | **DECIDED** 08-04 · rate→INFO, shape→PASS/FAIL |
| **V2-E1** | Persist retail probabilities in 04E; recompute PR-AUC / F1 / RW8 free-running | 1 GPU job ~40 min | **B-3**, C-4 | TODO |
| **V2-E2** | Row-matched REG-1 / REG-2 comparison | same job as E1 | C-2 | **UNBLOCKED** 08-04 · runnable locally (step4_val_meta.csv) |
| **V2-E3** | The one retail density + plug sensitivity cell, pre-registered | 1 simulation | B-11, B-12 | **DONE** 08-04 · 112/112, both arms win32 · retail median moved −0.05 % and that flipped a cell (55/56 → 54/56): **the gate is decided at 0.15 % of its floor** |
| **V2-E4** | Validator across seeds 0–4; publish mean ± sd | 4 CPU jobs | B-7 | TODO |
| **V2-E5** | Re-score Step 9 after WP-B/WP-D — **no new arm** | 1 CPU job | closes the loop | BLOCKED by WP-B, WP-D |
| **V2-F1** | Open the IEA Annex 66/79 and Richardson sources | 2 h | B-1 provenance | **DONE** 08-04 · Annex silent, Richardson confirmed |
| **V2-F2** | Pull ATUS / HETUS / UK midday rates from primary tables | 1 h | B-5's new reference | **DONE** 08-04 · BLS only; refs disagree in direction |
| **V2-F3** | Open Andridge & Little (2010) + R1's four "not stated" rows | 1–2 h | B-1, B-2 | **DONE** 08-04 · anchor REFUTED |
| **V2-G1** | Freeze the deliverable: MD5, job IDs, code hash, manifest | 1 h | reproducibility | BLOCKED by WP-E |
| **V2-G2** | Flip the master docs' status convention PLANNED → DONE | 1 h | the docs' honesty | BLOCKED by WP-C |
| **V2-G3** | Write the consolidated limitations section | writing | the paper | BLOCKED by WP-A, WP-B |
| **V2-G4** | Cross-leg consistency pass (2J ↔ Leg-2 ↔ Leg-3) | 2 h | B-13, inheritance table | **DONE** 08-04 · 2 recorded claims overturned |
| **V2-G5** | Close the audit: mark every finding closed/accepted/withdrawn | 1 h | all 13 + C/G | BLOCKED by all |
| **V2-D7** | Mark `21CEN22GSS_occToBEM.py` deprecated (dead code, 32.55 % materially wrong) | 5 min | B-13 residue | **DONE** 08-04 · banner only, compiles |
| **V2-D8** | Correct `TARGET_K = 49.2` → derived 56.9 K, with the derivation | 10 min | B4 provenance | **DONE** 08-04 · 56.9 K; verified inert on PASS/FAIL |
| **V2-F4** | Open CanmetENERGY 2020 archetype study + PNNL-28543 (hotel band) | 2 h | unblocks V2-B2 | **DONE (negative)** 08-05 · both primaries resolved: one `NOT FOUND`, one a nuclear-fuel report. No replacement band exists |
| **V2-F5** | Re-verify all 14 R1 reference rows (≥1 confirmed wrong DOI) | 2 h | R1 integrity | **DONE** 08-04 · 9/15 wrong DOIs; list not salvageable |
| **V2-F6** | Walk the `RV05` retrieval route ourselves: one prototype ZIP → `.table.htm` → Total Site Energy | 30 min | settles the vintage mismatch; falsifies or confirms `RV05` Section B | **DONE** 08-05 · prediction PASSED at **0.00 %**, 10/10 rows exact · **Large Hotel 90.1-2019 = 284.44 (6A) / 299.28 (7) kWh/m²·yr, read from the file** · `RV05` totals rehabilitated, my checks 3+4 **withdrawn** (the inversion is real in the prototypes); checks 1+2 stand · evidence in `f6_prototype_evidence/` |
| **V2-F7** | `V06` — NECB retail schedule table + Canadian archetype artefact existence | prompt authored; user runs it | V2-C4's owed re-source; terminates the Canadian-archetype line | **DONE (negative, ACCEPTED)** 08-05 · `RV06` returned · item 1 `NOT FOUND` (NECB paywalled, zero primary PDFs opened — stated unprompted); item 2 **5/5 `NO RETRIEVABLE FILE`** ⇒ Canadian-archetype line terminated · **first round in six with zero fabrication and zero rescuing recommendation** |
| **V2-F8** | Read BTAP for NECB schedule definitions shipped as data | 30 min | V2-C4's `0.95` re-source | **DONE** 08-05 · 🔴 `RV06`'s URL `github.com/CanmetENERGY/btap` **is a 404** (same defect class as its `987-` ISBNs) — real route is `NatLabRockies/openstudio-standards` @ `develop`, `lib/openstudio-standards/standards/necb/NECB{2011,2015}/data/`. **The file's own `refs` = `"NECB 2011 Table A-8.4.3.2.(1)-A"`, the exact table `RV06` returned `NOT FOUND` on.** Both pre-registered predictions **FAILED**, both because they were written from our docs rather than a source. Evidence: `f8_necb_schedule_evidence/` |
| **V2-D9** | Decide whether to load `NECB-C-*` for the retail channel (currently `grep -c "NECB-C-" = 0`) | decision + small code | V2-F8, `S9-EUI-retail` | **NEW, OPEN** 08-05 · first thing in weeks that could move `S9-EUI-retail` (fails by 0.06–0.23 %) · ⚠️ arm B froze retail lighting — **predict the direction before running anything** |

---

### WP-A — the submitted paper first

*Two tasks. They come first because they are the only ones touching a manuscript that is already
under review, and the first is minutes of work.*

#### V2-A1 — Run the B-13 falsifier

**Finding.** `eSim_occ_utils/21CEN22GSS/21CEN22GSS_occToBEM.py:144-145` computes

```python
estimated_count = hourly["occPre"] * (hourly["occDensity"] + 1)
occupancy_sched = (estimated_count / hh_size).clip(upper=1.0)
```

Neither the `× (occDensity + 1)` factor nor the `.clip(upper=1.0)` appears anywhere in
`readySubmission.md`. `occDensity` is built at `21CEN22GSS_HH_aggregation.py:141` as a **sum over
household members** of each member's GSS companion count (`social_sum`) — so two co-residents at
home together contribute `sum = 2`, then `+1` yields 3 people in a 2-person household. The clip is
exactly where that over-count would have surfaced and been silently absorbed.

**Aim.** Establish whether the over-count is real and how often the clip fires — i.e. whether the
submitted paper describes a converter it does not have, and whether the difference is material.

**Steps.**
1. Confirm `social_sum`'s definition in the GSS codebook: is it *co-present companions* (excluding
   self) or *total persons present* (including self)? The `+1` is correct under one reading and
   double-counts under the other. **This is the pivot of the whole finding — settle it first.**
2. Over the 2J frame, count rows where `occDensity + 1 > HHSIZE`, broken down by `HHSIZE`.
3. Count how often `.clip(upper=1.0)` binds, by `HHSIZE`, as a share of occupied slots.
4. Recompute the schedule under the manuscript's stated rule (per-slot maximum AT_HOME across
   members, `readySubmission.md:211`) and report the mean absolute difference in schedule value and
   in implied person-hours.

**Expected result.** One of three verdicts, all publishable: (a) `social_sum` excludes self → the
`+1` is correct, `occDensity` is still a *sum* and over-counts co-residents, clip binds often →
finding stands; (b) `social_sum` includes self → the `+1` is a straightforward double-count →
finding stands harder; (c) the clip almost never binds and the difference vs the stated rule is
below ~1 % of person-hours → finding is a **documentation** defect only, and A2 shrinks to one
sentence.

**Test method.** Two counts and one difference table, all re-derivable from the converter's own
inputs. Pre-register the materiality threshold (**1 % of annual person-hours**) in the Progress Log
before running. Cross-check the row count against the frame size stated in the manuscript.

**Cost.** One script, minutes. Local. **Closes:** B-13. **Blocks:** V2-A2, V2-G4.

> 🔴 Good news that must survive into the write-up whichever way this lands: 2J is **not** a
> zero-diversity model. It reads real co-presence off the GSS social fields. That is *better* than
> B-1 originally accused it of, and better than the surveyed literature (R1: 0 of 14 studies).

#### V2-A2 — Draft the 2J residential-channel correction

**Aim.** Bring `2J_docs_occ_nTemp/writing/fullSet/readySubmission.md` into agreement with the code
it describes, and add the limitation the R1 literature review showed is owed.

**Steps.**
1. On V2-A1's verdict, decide with the user: **erratum**, **revision during review**, or **no
   action with the discrepancy recorded**. This is a publication decision, not a technical one.
2. Rewrite the aggregation sentence at `readySubmission.md:211` so it describes
   `occPre × (occDensity + 1)`, clipped — or confirm in writing that the max rule is what actually
   ships and the extra factor is inert (only possible under an A1 (c) verdict).
3. Add the **synchrony** limitation paragraph: the household presence model assumes co-resident
   presence is well-approximated by the aggregate rule used; R1 found **0 of 14** study lines using
   `any-present × N`, and under perfect synchrony that rule coincides with sum-of-members. State the
   assumption; do not overclaim a defect that the 21.38 % measurement partly answers.
4. Note the measured intra-household diversity (**3,499 / 16,367 = 21.38 %** of multi-person
   households have non-identical co-resident vectors — a lower bound) as evidence *for* the model,
   not against it.

**Expected result.** A drafted paragraph pair (methods correction + limitation) ready for the user's
decision on how to route it to the journal.

**Test method.** The drafted text is checked line-by-line against the converter source; every
numeric claim in it traces to a measurement in the audit or in V2-A1. No claim rests on a logged
number.

**Cost.** Writing. **Closes:** B-1 (paper-facing half), B-13 (paper-facing half). **Depends on:**
V2-A1.

---

### WP-B — the three blocking decisions (desk work, no simulation)

*Five tasks, zero simulations. This is the work that has been authorised since 2026-08-02 and never
executed — four more arms were run instead, and moved nothing.*

#### V2-B1 — Settle the office band applicability question (Q1)

**Aim.** Answer: **does a standalone-prototype EUI band apply to a channel *stacked* inside a
mixed-use tower?** The office band's floor is 100 kWh/m²·yr; the uninjected NECB control reads
**85.45** — the code's own reference implementation fails by 15 % before any occupancy signal is
injected.

**Steps.**
1. Establish how the office band was derived (which prototype, which vintage, which climate zone,
   which floor-area basis — CFA or GFA).
2. Search for an EUI reference derived from **stacked / mixed-use** office floors rather than a
   standalone office prototype. A clean negative is a result.
3. Identify the physical reasons a stacked office floor should read lower: shared envelope, reduced
   exposed surface per unit area, plant shared with other channels, no roof or ground-contact
   losses on intermediate floors.
4. Quantify at least one of them from our own artefacts (e.g. exposed-envelope area per m² of
   office CFA, tower vs a standalone equivalent).
5. Write the verdict as a pre-registered statement **before** re-reading our numbers.

**Expected result.** One of: (a) an applicable stacked-office band exists → adopt it and re-score;
(b) no such band exists → `S9-EUI-office` becomes **INFO** with a published limitation, justified by
inapplicability, **never by widening**; (c) the band applies and we genuinely fail → that is a real
result and the paper says so.

**Test method.** The verdict must name the source, the prototype and the basis. It must also explain
the **uninjected control** — any conclusion that leaves 85.45-vs-100 unexplained is not an answer.
🔴 Reject any draft whose logic reduces to "our number is 81, so the floor should be 80".

**Cost.** 2–4 h reading. **Closes:** one of the three FAILs. **Blocks:** V2-C6, V2-D4, V2-E5.

#### V2-B2 — Re-derive the hotel as-modelled band

**Aim.** `dr_L3-03_hotel_eui_bands_REPORT.md:13` recommends **[180, 240, 300]**. Its own Table 2 at
`:58-68` lists **6 of 11** reference rows above 300 — every Large Hotel row: 90.1-2004 CZ6A 286.4 /
CZ7 302.2; 90.1-2016 CZ6A 484.0 / CZ7 521.2; 90.1-2019 CZ6A 441.6 / CZ7 479.5. **300 is the exact
ceiling `S9-EUI-hotel` fails against**, and the Step-9 DHW resize pushed hotel EUI further above it.
The report contradicts itself; the gate inherits the contradiction (finding **G-2**).

**Steps.**
1. Re-read `dr_L3-03` end to end and reconstruct how 180/240/300 was obtained from Table 2. The
   evident derivation is the two NECB-2017 rows (CZ6 140–220, CZ7 160–240) — state it explicitly.
2. Decide the archetype match, in writing, **before** looking at our EUI: is our hotel channel a
   Large Hotel (441–521), a Small Hotel (135–175), or an NECB-2017 code-compliant tower hotel
   (140–240)? Our tower is NECB-based — which is a real argument *for* the current band, and it is
   the caveat Gemini did not state.
3. If the archetype match holds, the band survives and the FAIL is real → say so and stop.
4. If it does not, re-derive the band from the archetype-matched rows, pre-registered, and record
   the derivation arithmetic in full.
5. Either way, note that the DHW plant resize (arm R, K = 10) is a **plant** effect measured on the
   uninjected control — it must not be presented as an occupancy result.

**Expected result.** A band with a written derivation, or the current band confirmed with the
contradiction inside `dr_L3-03` corrected.

**Test method.** Re-derive the recommended interval from Table 2's rows and show the arithmetic. Any
band that cannot be reproduced from named rows is not adopted. 🔴 This is licence to **re-derive**,
never to widen.

**Cost.** 2 h. **Closes:** G-2, Step-9 decisions #2/#3. **Blocks:** V2-C6, V2-D4, V2-E5.

#### V2-B3 — Decide the retail gate rule

**Aim.** `S9-EUI-retail` fails on an **all-56-cells-in-band** rule. Arm R is 54/56; the two misses
read **79.82** and **79.96** against an 80.00 floor — short by **0.23 %** and **0.06 %**. The
uninjected control is 92.13 and 4/4 in band. This is a gate-rule question, not an energy question.

**Steps.**
1. Write down what the gate is *for*: catching a channel whose absolute level is implausible, or
   catching a single anomalous cell.
2. Choose one rule and justify it independently of our numbers — e.g. median-in-band plus a stated
   tail tolerance, or ≥ 95 % of cells in band, or all-56 retained deliberately.
3. **Pre-register the rule before re-scoring.** State explicitly which counterfactual it
   discriminates: what result would make this gate fail? If nothing realistic would, it is vacuous
   and must be re-specified, not adopted.
4. Apply the same rule to all three EUI gates — a rule that exists only for retail is a fitted rule.

**Expected result.** One rule, uniformly applied, with the discriminating counterfactual named.

**Test method.** Score the chosen rule against a deliberately broken input (e.g. retail EUI shifted
−30 %) and confirm it FAILs. If it does not fail, it is not a gate.

**Cost.** 1 h + writing. **Closes:** Q3, and compounds with B-5. **Blocks:** V2-D4, V2-E5.

#### V2-B4 — Name the deliverable arm

**Aim.** Arm **H** under-serves hotel DHW (marginal m³ served at 22.66 K vs a 49.2 K target — ~54 %
of any hotel draw increase never becomes delivered energy). Arm **R** (K = 10) over-corrects. Both
score identically: 17P/0W/3F/10I, with `S9-EUI-hotel` reading 28/56 in **both** — a *different* 28
(vacuous-gate class #12: count stable, membership turned over).

**Steps.**
1. Tabulate the existing K-sweep: marginal served capacity vs K, against the 49.2 K target.
2. Choose K on the **physical** criterion (plant sized to serve the modelled draw), never on which
   K moves a gate.
3. Record why H and R both mis-serve, and what the chosen K does to the uninjected control — if it
   moves the control, it is a plant effect and carries zero occupancy content.
4. If the chosen K is neither 1 nor 10, decide whether a re-run is warranted. **A re-run for
   plant-sizing correctness is legitimate; a re-run to move `S9-EUI-hotel` is not.**

**Expected result.** A named deliverable arm (or a named K requiring one final run), with the
sizing arithmetic recorded.

**Test method.** The chosen K must reproduce the 49.2 K target within a stated tolerance, and its
effect on the uninjected control must be reported alongside its effect on the injected cells.

**Cost.** Analysis on existing tables. **Closes:** Q4, Q5, Q6. **Blocks:** V2-G1.

#### V2-B5 — Decide the Step-7 residential aggregation: mean or max

**Aim.** `3rdJ_05_censusLinkage_4split.py:1037` computes the household **maximum** into
`HH_hom30_*`. `3rdJ_07_aug_to_bem_4split.py:309` never reads it — it takes a per-member **mean**.
Both auditors' route to this (C-1) and the audit's own class #11 (*the gate measuring a quantity the
deliverable discards*) converge here. **The defect is that nobody chose.**

**Steps.**
1. State which quantity the paper claims to inject: a binary "any member present" occupancy, or an
   expected occupant count.
2. Note the consequence, measured: a fractional expectation **smooths** peaks; the maximum
   **sharpens** them. B-1 and G-4 both argued the wrong sign before this was measured.
3. Choose, in writing, with the reason. **A deliberate mean is entirely defensible** — combined with
   `Number_of_People = HHSIZE`, the mean yields expected occupant count, which is arguably the more
   physical driver for a `People` object. An accidental one is not defensible.
4. Decide whether `HH_hom30_*` should be deleted from Step 5 (it is dead weight if the mean stands)
   or read by Step 7 (if the max stands).
5. If the max is chosen, scope the re-run: residential schedules change, so the campaign changes.
   Cost this before committing.

**Expected result.** A written decision with its energy consequence stated, and either a deletion or
a code change scoped.

**Test method.** Whichever is chosen, the master docs and the paper must describe **that** one. The
acceptance test for this task is that `3rdJ_07_aug_to_bem_4split.py:309` and the methods prose agree.

**Cost.** Writing; possibly one re-run. **Closes:** C-1, B-1's surviving half. **Blocks:** V2-D3.

---

### WP-C — master-document corrections (writing only)

*Ten tasks against the two files named at the top of this document. Every one has an exact line
number. None changes a result; all ten change what a reviewer reads.*

#### V2-C1 — Floor areas

**Aim.** Both master docs still cite the legacy unparsed areas in the body, while their own headers
carry the corrected parsed values (finding **G-1**, reproducing **B-8** blind).

**Steps.** Replace at:
- `3rdJ_00_4split_Occupancy_Pipeline.md:320` — "SuperTall 40,846 m² / Tall 26,750 m²" →
  **135,857.6 m² / 72,623.1 m²**
- `3rdJ_00_4split_Occupancy_Pipeline_Overview.md:125` — "(SuperTall 40,846 / Tall 26,750 m2)" → same

Add, at both sites, a pointer to `Step8_docs/outputs_step8/agg/agg_meta.csv`, which now emits these
areas per cell so they are never retyped by hand.

**Expected result.** No occurrence of `40,846` / `26,750` in either document except inside the
existing 🔴 correction blockquotes, where they are labelled as the superseded values.

**Test method.** `grep -n "40,846\|26,750\|40 846\|26 750"` on both files; every surviving hit must
be inside a correction blockquote.

**Cost.** 10 min. **Closes:** G-1, part of B-8.

#### V2-C2 — Service/MEP share

**Aim.** "~52 % gross" survives in five places; the measured values are **20.64 %** (SuperTall) and
**21.41 %** (Tall). This is not a rounding difference — it is 2.5×, and it drives the dr_L3-10
prorating rule.

**Steps.** Correct at `Pipeline.md:325`, `Pipeline.md:410`, `Pipeline.md:434`,
`_Overview.md:115`, `_Overview.md:198`. Each becomes "**20.6 % · 21.4 % of gross (measured)**".
Check whether the dr_L3-10 prorating description needs a consequential edit — prorating "~52 % of
gross" onto four tenant channels is a materially different operation from prorating ~21 %.

**Expected result.** Five corrected sites; the prorating rule either confirmed unaffected or amended.

**Test method.** `grep -n "52 %\|52%"` returns hits only inside correction blockquotes. Separately,
confirm the Step-8 aggregator actually prorates the measured share, not the quoted one — **this is
the part that could be a real defect rather than a prose defect.**

**Cost.** 10 min + one check. **Closes:** rest of B-8. 🔴 If the aggregator uses 52 %, this becomes
a WP-D code task and a re-aggregation.

#### V2-C3 — Retail occupant density

**Aim.** Both docs state the retail channel runs at "~3.7 m²/person". Parsed from the injected IDFs,
retail zones run at **25.0 m²/person — identical to office**. A 6.8× gap, and the document is
wrong, not the model necessarily (finding **B-11**, falsifier run).

**Steps.**
1. Correct `Pipeline.md:291` and `_Overview.md:113` to the parsed value, with "(parsed from the
   injected IDF; **not** an intended retail density — see V2-E3)".
2. Record the finding's real shape: occupant density and plug density are **one blanket office value
   each across all 17 space types in both towers**, while lighting **is** correctly per-space-type.
3. State the consequence honestly: this means office is the channel those constants are plausibly
   right for, and correcting them moves retail, hotel and residential but **cannot** move office —
   which *strengthens* the office band-applicability argument in V2-B1.

**Expected result.** Both documents describe the model as built, with the discrepancy flagged and
routed to V2-E3 rather than silently repaired in prose.

**Test method.** The quoted density must match a value parseable from the injected IDF today. Quote
the parse command in the doc so it can be re-run.

**Cost.** 20 min. **Closes:** B-11's documentation half.

#### V2-C4 — The 0.95 retail peak

**Aim.** The injector's `0.9215 = 0.95 × 0.97` was verified exact — the injector is vindicated. But
the "0.95 NECB retail peak" is, on the citation check, the **office** peak, and the retail baseline
is office-shaped (midday dip 0.5).

**Steps.**
1. Open the NECB 2017/2020 table and read the retail/sales peak fraction directly.
2. If 0.95 is the office value, either re-source the retail value and note the change, or keep 0.95
   and state plainly that the retail baseline being modulated is office-shaped — which is a
   limitation, not a bug, given V2-C3.
3. Correct `Pipeline.md:294`, `Pipeline.md:304`, `Pipeline.md:433`, `_Overview.md:111`,
   `_Overview.md:220`.

**Expected result.** The 0.95 either re-sourced or explicitly labelled as inherited from the office
baseline.

**Test method.** The cited table, page and row must be named. **This is a WP-F-class citation: not
evidence until opened.**

**Cost.** 30 min. **Closes:** B-11 provenance, strengthens B-5.

#### V2-C5 — The retail episode-time share

**Aim.** "~2.1–2.3 %, stable across cycles" is contradicted by the project's own measurements:
**1.50–2.14 %, a −25 % decline** — which R2 confirms is internationally normal (ATUS / UK / HETUS
show the same direction).

**Steps.** Correct `Pipeline.md:102`, `Pipeline.md:237`, `_Overview.md:77`. Then write the short
reconciliation subsection: the measured decline and the 2030 lever's 0.97 default are consistent
under R2's **saturation** argument — say so explicitly, because a reviewer will otherwise read the
decline and the near-flat lever as contradictory.

**Expected result.** Three corrected sites plus one reconciliation paragraph.

**Test method.** The quoted range must be reproducible from the Step-2 outputs, per cycle. Include
the per-cycle table, not just the range.

**Cost.** 20 min. **Closes:** B-4.

#### V2-C6 — Propagate the band decisions

**Aim.** Once WP-B lands, the band statements in both docs are stale.

**Steps.** Update `Pipeline.md:329`, `Pipeline.md:427-428`, `_Overview.md:130`,
`_Overview.md:214-215` with the decided bands, each carrying its derivation source and the date it
was decided. Where a band became INFO by inapplicability, say **why**, in one sentence, at the site.

**Expected result.** Every band in both documents traceable to a WP-B decision.

**Test method.** Each band statement names a source and a decision date. No band appears in the
documents that is not in the scorer, and vice versa (V2-D4 is the other half of this check).

**Cost.** 20 min. **Depends on:** V2-B1, V2-B2, V2-B3.

#### V2-C7 — The Step-9 documents' own citation defects

**Aim.** Two defects inside the documents written for external cold review: `Q8` stated **B-1's
content under B-3's number** (now split into Q8a/Q8b — verify the split is complete everywhere), and
`Q2` quoted the *injected* office shortfall under the *uninjected* label ("19 % below its floor even
uninjected"; uninjected is **14.55 %**).

**Steps.** Fix both in `improvements/v1/3rdJ_L3_improvements_step9.md` and
`improvements/v1/3rdJ_L3_step9_READER_GUIDE.md`. Corrections are struck-and-restated in the log
(append-only) and edited in place in the Reader's Guide (which is a report, not a lab notebook).

**Expected result.** Neither defect survives in the guide; both are recorded in the log.

**Test method.** `grep` for "19 %" near "uninjected" and for `Q8` without an a/b suffix.

**Cost.** 10 min. **Closes:** audit item 5f.

#### V2-C8 — The Richardson citation

**Aim.** Richardson et al. (2010) uses a household Markov state, **not** `any-present × N`. The
conflation is inherited by `dr_L3-06` and by the master doc.

**Steps.** Correct wherever the citation appears — `Pipeline.md:294`, `Pipeline.md:433`,
`_Overview.md:220`, and inside `dr_L3-06_retail_diurnal_targets_REPORT.md`. Note that the
peak-normalisation verdict itself is **not** affected; only the attribution is.

**Expected result.** The citation supports what it actually says.

**Test method.** Open Richardson (2010) and confirm the model class before editing (this is V2-F1's
scope; do them together).

**Cost.** 15 min after F1. **Closes:** audit item 13c.

#### V2-C9 — The `MIN_POOL` justification

**Aim.** `MIN_POOL` was selected by which value made gate W1 pass, and W1 is non-monotonic across
the sweep (FAIL@10, PASS@11–20, FAIL@30) — a selection criterion that cannot be defended. R3 found
that **7 of 8** authorities give no minimum-donor rule, but adjustment-cell floors (n ≥ 10–20)
retro-justify `MIN_POOL = 15` **independently of W1**.

**Steps.**
1. Write the methods justification on the adjustment-cell floor convention, citing Little & Rubin
   (2002) and Andridge & Little (2010). **The shipped value need not change.**
2. Present the W1 sweep as a **sensitivity**, not as the selection criterion, and say plainly that
   the original selection was made on W1 and is being re-justified independently.
3. Record R3's finding that the non-monotonicity is **draw noise**, confirmed.

**Expected result.** A methods paragraph that would survive a reviewer asking "why 15?".

**Test method.** The justification must not reference W1 at any point. If it needs W1, it has failed.

**Cost.** Writing. **Closes:** most of B-2; V2-E4's sweep closes the rest.

#### V2-C10 — Record the verified-no-action findings

**Aim.** Three of Gemini's six findings (**G-3** StatCan table, **G-5** 4-head vs 3-head, **G-6**
Service/MEP prorating) cite as evidence the very document that already contains the correction.
They are not defects — but "we checked and it was already right" is worth recording once, so nobody
re-audits them.

**Steps.** One short subsection in this file (or in the audit's closing section) naming each, with
the line that already carries the correction: `Pipeline.md:425` (StatCan table verified non-existent
and re-sourced), `Pipeline.md:226` and `_Overview.md:74` (heads count resolved, §3.5 authoritative),
`Pipeline.md:325` (prorating rule stated, though see V2-C2 for its share).

**Expected result.** Three findings closed as verified-no-action with the evidence line cited.

**Test method.** Each cited line must actually contain the correction claimed.

**Cost.** 10 min. **Closes:** G-3, G-5, G-6.

---

### WP-D — code and gate corrections

#### V2-D1 — RW6 severity

**Aim.** `RW6` calls `_grade_band(hard=False)` (`3rdJ_04_augmentationGSS_4split_val.py:1293-1297`);
an out-of-band value can only ever produce `warn` (`:1267-1285`). RW6 currently delivers **0.0453**
against a **0.06** floor — **24.5 % below** — and reports a WARN. This is the *severity-vacuous*
gate, catalogue class **#14** (raised by Codex as C-3; see the collision note in §3).

**Steps.**
1. Decide the correct severity for RW6, on the criterion *what does this gate protect?* — a 24.5 %
   miss on a rate floor is either a FAIL or the floor is wrong. **Not both.**
2. Either pass `hard=True`, or re-specify the floor with a derivation, or explicitly demote RW6 to
   INFO with the reason. 🔴 **Do not widen the band.**
3. Grep the validator for every other `hard=False` call site and check each against the same
   question — this defect class is likely not unique.
4. Settle the catalogue number: the severity-vacuous class is **#14**, not #13 (see §3, rule 3) —
   and propagate it into `READER_GUIDE §4`, the audit, the investigation README and the manager
   handoff, all four of which currently disagree about how many classes exist.

**Expected result.** RW6's severity matches what it is testing, and the sweep for sibling instances
is recorded.

**Test method.** Feed a deliberately out-of-band value and confirm the gate produces the intended
severity. Per rule 3: **a gate is not fixed until it has been seen failing.**

**Cost.** Small code. **Closes:** C-3, catalogue class **#14** (proposed — #13 is taken); compounds with B-5 on the same gate.

#### V2-D2 — ISR-raw severity

**Aim.** The ISR-raw gate is the one place the "never relax a gate" rule was not followed (B-6).

**Steps.** Re-label ISR-raw → **WARN** with the deviation stated explicitly at the site: what the
original bar was (≤ 0.5 %), what was actually observed, and when the relaxation happened.

**Expected result.** One line changed, one deviation recorded. The final-schedule ISR = 0 % by
construction claim is unaffected and stays.

**Test method.** The recorded deviation must match the scorer's actual behaviour.

**Cost.** One line. **Closes:** B-6.

#### V2-D3 — Implement the aggregation decision

**Aim.** Make `3rdJ_07_aug_to_bem_4split.py` do what V2-B5 decided.

**Steps.** If the mean stands: add a comment at `:309` stating the choice and its reason, and either
remove `HH_hom30_*` from Step 5 (`3rdJ_05_censusLinkage_4split.py:1037`) or document it as an
unused diagnostic. If the max is chosen: read `HH_hom30_*`, re-emit schedules, scope the re-run.

**Expected result.** No quantity is computed by one step and silently discarded by the next.

**Test method.** For a sample of multi-person households, hand-compute the expected schedule under
the chosen rule and compare to the emitted CSV.

**Cost.** Small code (or a re-run). **Closes:** C-1. **Depends on:** V2-B5.

#### V2-D4 — Sync the scorer's `BENCH`

**Aim.** The scorer's `BENCH["hotel"]` is `[180, 300]`; decision #3 put the gate on `[240, 300]`.
**Stale** (Q7). After WP-B, all three bands may move.

**Steps.** Update `3rdJ_09_activityDrivenLoads_4split.py`'s `BENCH` to the WP-B-decided values;
add a one-line provenance comment per band naming its source document and decision date.

**Expected result.** Scorer bands == master-doc bands == decision record. Three-way agreement.

**Test method.** A small check that reads the bands from the scorer and diffs them against the
values written in the master docs. Run it as part of V2-E5.

**Cost.** Small code. **Closes:** Q7. **Depends on:** WP-B. **Pairs with:** V2-C6.

#### V2-D5 — Step-4 run manifest

**Aim.** The canonical Step-4 directory holds **no checkpoint and no `rake3ch_provenance.json`**
(finding **C-5**). Without persisted validation respondent IDs, the REG-1/REG-2 gates cannot be made
row-matched, and V2-E1's recomputation cannot be tied to the shipped pool.

**Steps.**
1. Establish what still exists on `/speed-scratch` for the seed-3 run: checkpoint, raking
   provenance, input hashes, code state.
2. Write a run manifest alongside the canonical CSV: checkpoint hash, input file hashes, code
   commit/hash, rake provenance, seed, date, job ID.
3. Persist the validation respondent IDs.
4. If artefacts are gone, say so in the manifest — an honest "not recoverable" is a valid entry and
   is far better than a reconstructed guess.

**Expected result.** A manifest that lets someone else reproduce or at least identify the shipped
pool.

**Test method.** Recompute one hash in the manifest from the file it names and confirm it matches.

**Cost.** Hours, if the artefacts still exist. **Closes:** C-5. **Blocks:** V2-E2.

#### V2-D6 — Promote the retail shape gates

**Aim.** B-5 (with R2) showed the retail **rate** gate was mis-specified — its reference band was
denominated on store design capacity while the gate measured a population rate, i.e. different
denominators. The **shape** gates do not have this problem and are currently under-used.

**Steps.** Re-specify the rate gate against a **population-denominated** reference (V2-F2 supplies
it) → INFO if no valid reference exists; promote the shape gates (peak window, night floor, Saturday
and Sunday-by-province) to PASS/FAIL.

**Expected result.** The retail channel is gated on what the injector actually uses — the
peak-normalised **shape** — rather than on a level the injector discards.

**Test method.** Break the shape deliberately (shift the peak by 3 h) and confirm the promoted gates
FAIL. **Class #11 is exactly this defect; the fix is not complete until the new gate is seen
failing.**

**Cost.** Small code. **Closes:** B-5. **Depends on:** V2-F2 for the reference.

---

### WP-E — the compute work

*Five tasks. **None retrains Step 4.** Exactly one is a new EnergyPlus simulation, and it is a
measurement, not a fix attempt.*

> 🔴 Cluster rules apply to every task in this package: `sbatch` only, single line,
> `-t 7-00:00:00` minimum, nothing computational on the login node.

#### V2-E1 — Persist retail probabilities; recompute the retail gates free-running

**Aim.** `RW1`/`RW2` — the gates built to catch a dead retail head — read **teacher-forced** numbers
(0.5190 / 0.3794) from `step4_training_log.csv`, not the shipped pool (**B-3**, reproduced blind as
**C-4**). A dead head could pass them. This is the one high finding still needing compute, and the
one an independent auditor found on its own.

**Steps.**
1. Modify 04E to persist per-slot retail probabilities during free-running generation.
2. Recompute **PR-AUC**, **F1** and **RW8** on the shipped pool, free-running.
3. Compare against the teacher-forced numbers and report both, side by side.
4. **Pre-register**, before the run: the gates are PR-AUC ≥ 0.15 and F1 ≥ 0.25. Write the predicted
   free-running values into the Progress Log first.

**Expected result.** Either the retail head passes free-running — in which case the gate was weak
but the model is fine, and that is a clean result — or it does not, in which case a shipped result
changes and the paper's retail claims need revisiting.

**Test method.** Run the recomputation against a deliberately zeroed retail head and confirm the
gates FAIL. A gate that passes an all-zeros head is the exact failure B-3 alleges; **prove the new
one does not.**

**Cost.** One GPU job, ~40 min. **Closes:** B-3, C-4. **Submit with:** `sbatch`, `-t 7-00:00:00`.

#### V2-E2 — Row-matched REG-1 / REG-2

**Aim.** REG-1/REG-2 compare Leg-2 and Leg-3 outputs that are **not row-matched** — the validator
admits it at `3rdJ_04_augmentationGSS_4split_val.py:1749-1755` (finding **C-2**). A regression gate
on unmatched rows measures distributional similarity, not regression.

**Steps.** On the respondent IDs persisted by V2-D5, run the row-matched comparison the gates claim
to be. Report ΔJS on matched rows against the ≤ 0.002-bit bar.

**Expected result.** A genuine regression number for the two shipped heads.

**Test method.** Confirm the matched row count equals the intersection of the two ID sets, and that
it is a large fraction of both. A tiny intersection means the comparison is still not the claimed one.

**Cost.** Same job as E1 — **do them together**. **Closes:** C-2. **Depends on:** V2-D5.

#### V2-E3 — The retail density + plug sensitivity cell

**Aim.** Bound how much every Step-8/9 retail number depends on the two blanket office constants
(**B-11**: occupant density 25.0 m²/person on retail; **B-12**: blanket 7.5028 W/m² plug). Retail OA
would be **2.08×** current; occupant gains **6.8× up**; plug gains plausibly **down** — three
effects, two signs, **no derivable net**. That is exactly why it must be measured.

**Steps.**
1. **Pre-register the prediction with numeric bounds, before running.** Three effects, two signs —
   commit to a direction and a magnitude range for ΔEUI.
2. One cell: retail occupant density ≈ 3.7 m²/person **and** the corrected retail plug density, vs
   the `Default_NECB` baseline.
3. Report ΔEUI per channel and the effect on the retail gate's two marginal cells (79.82 / 79.96).
4. 🔴 **Read as exposure, never as a fix.** If it happens to push the two marginal cells into band,
   that is *not* how `S9-EUI-retail` gets resolved — V2-B3 decides that, on a rule, in advance.

**Expected result.** A bound on retail's sensitivity to the constants, usable as a limitation
paragraph whichever way it lands.

**Test method.** One-variable contrast: confirm every non-retail channel moves < 0.005 %, as arm R
was verified. If other channels move, the cell is not the contrast it claims to be.

**Cost.** One simulation. **Closes:** B-11, B-12 (magnitude half). **Prerequisite:** V2-F2 / audit
item 5e for the correct target densities — **do not guess them**.

#### V2-E4 — Multi-seed validation

**Aim.** Seed 3 was selected; no mean ± sd was ever published (**B-7**). Normal spread is 1–2 % on
F1/PR-AUC and 0.001–0.002 bits on JS, so a single seed's gate margins are uninterpretable.

**Steps.**
1. Run the validator across seeds 0–4; publish mean ± sd for every gated metric.
2. Record the seed-3 **selection rationale** — retrospectively is fine, as long as it is honest
   about being retrospective.
3. Add the multi-seed `MIN_POOL` sweep → mean ± CI band over [10, 20]. R3 requires this before the
   sweep can be called a sensitivity (the rest of **B-2**).

**Expected result.** Every gate margin reported with its spread; `MIN_POOL` presented as a
sensitivity with a CI band.

**Test method.** Confirm the spread is within the stated normal range. A gate whose margin is
smaller than its across-seed sd is not a passing gate — flag any that qualify.

**Cost.** 4 CPU jobs + 1 array job. **Closes:** B-7, rest of B-2.

#### V2-E5 — Re-score Step 9

**Aim.** Score the 30 gates under the WP-B decisions and the WP-D corrections. **No new arm.**

**Steps.**
1. **Write the predicted scorecard into the Progress Log first** — every gate whose status is
   expected to change, and why.
2. Run the scorer on the deliverable arm named by V2-B4.
3. Diff against the pre-registered prediction and report every mismatch.
4. For any gate whose count is unchanged, check **membership**, not just the count — this is
   vacuous-gate class #12, and it has already fired once on `S9-EUI-hotel` (28/56 in both arms H and
   R, a *different* 28).

**Expected result.** A scorecard whose every change is explained by a decision or a code fix, and
none by a re-run.

**Test method.** The prediction-vs-outcome table. Mismatches are the result, not an embarrassment.

**Cost.** 1 CPU job. **Depends on:** WP-B, V2-D1, V2-D2, V2-D4.

---

### WP-F — citations owed

*A citation is not evidence until it has been opened. These three are load-bearing for findings this
plan acts on.*

#### V2-F1 — IEA Annex 66/79 and Richardson (2010)

**Aim.** The Annex "explicitly warns against binary household scaling" claim is the strongest single
sentence against the original implementation; the Richardson attribution is used in three documents.
Both come from a secondary synthesis (R1).

**Steps.** Open both. Confirm or refute each claim in one line. If the Annex says no such thing,
B-1's literature case rests on **absence of evidence**, and the write-up must say that instead.

**Expected result.** Two verdicts, each with a page reference.

**Test method.** Quote the actual sentence, or record that none exists.

**Cost.** 2 h. **Closes:** B-1 provenance. **Blocks:** V2-C8, V2-A2.

#### V2-F2 — ATUS / HETUS / UK midday presence rates

**Aim.** These become the **new reference** for the re-specified retail gate (V2-D6). A gate is only
as good as its reference — which is the entire point of B-5.

**Steps.** Pull the rates and minutes-per-day figures from the **BLS and Eurostat tables directly**.
Do not accept them second-hand from R2. Record the denominator each uses — the denominator mismatch
is what made the original gate wrong.

**Expected result.** A population-denominated reference band with its source table named.

**Test method.** The denominator must be explicitly stated and must match ours. If it does not, the
reference is not usable and the gate goes to INFO.

**Cost.** 1 h. **Closes:** the reference half of B-5. **Blocks:** V2-D6.

#### V2-F3 — Andridge & Little (2010) and R1's four "not stated" rows

**Aim.** The **0 of 14** count is what carries B-1's literature case, and 4 of the 14 rows are
marked "not stated". The adjustment-cell floor is the single concrete anchor for V2-C9.

**Steps.** Open Andridge & Little (2010) and confirm the n ≥ 10–20 convention. Check at least the 4
"not stated" rows and 2 of the 8 "sum of members". Also check the US Census CPS "collapse below
n = 10" anchor.

**Expected result.** The 0-count either holds or is corrected to its true value.

**Test method.** Each checked row gets a one-line verdict with a page reference.

**Cost.** 1–2 h. **Closes:** B-1 and B-2 provenance.

---

### WP-G — final assembly and freeze

#### V2-G1 — Freeze the deliverable

**Aim.** One arm, named, with provenance that survives the project.

**Steps.** Record the MD5 of the canonical aggregate, the SLURM job IDs, the code hash of the
injector and the aggregator, the scorer version, and the K value. Keep the predecessor intact and
move the pointer — the project's archive-predecessor convention. Do **not** delete the superseded
arm.

**Expected result.** A provenance block that a reader can use to reproduce, or at least identify,
every number in the paper.

**Test method.** Re-derive one headline number from the frozen artefact's own columns.

**Cost.** 1 h. **Depends on:** V2-B4, WP-E.

#### V2-G2 — Flip the master docs' status convention

**Aim.** Both master documents still tag Leg-3 work as **⚠️ PLANNED (Leg 3)** throughout — the
retail delta, the hotel side-track, Steps 3 through 9. All of it has been built and run.

**Steps.** Replace `⚠️ PLANNED (Leg 3)` with `✅ DONE (Leg 3)` wherever the work has shipped, adding
the artefact that proves it (script path, output directory, job ID). Anything still genuinely
planned keeps its tag — and there should be very little.

**Expected result.** A reader can tell, from the master documents alone, what exists and what does
not. Right now they cannot.

**Test method.** Every `✅ DONE` tag names an artefact that exists on disk. Check each one.

**Cost.** 1 h. **Depends on:** WP-C.

#### V2-G3 — The consolidated limitations section

**Aim.** Assemble, in one place, every limitation this work has converted from an unstated
assumption into a statable one.

**Steps.** Collect: household presence synchrony (B-1/R1); the mean-vs-max aggregation choice
(B-5/C-1); retail customers-only framing, staff excluded by construction; blanket occupant and plug
densities (B-11/B-12); band applicability for stacked channels (B-1 of WP-B); hotel guests out of
the GSS frame by construction; ground-level EPW on a supertall; the `MIN_POOL` convention (B-2/R3);
the retail decline ↔ saturation reconciliation (B-4/R2).

**Expected result.** A limitations section that is the paper's strength rather than its apology —
each item stated with the measurement that bounds it.

**Test method.** Every limitation names its evidence. No limitation is a hedge without a number.

**Cost.** Writing. **Depends on:** WP-A, WP-B.

#### V2-G4 — Cross-leg consistency

**Aim.** The 2J converter, the Leg-2 converter and the Leg-3 pipeline implement household
aggregation **three different ways**, and the manuscripts do not all describe what their code does.

**Steps.** Complete the audit's cross-leg inheritance table with what V2-A1 established. Confirm
which claims propagate and which stop at a leg boundary. C-1's "reaches 2J" claim was a cross-leg
category error — the check that caught it is exactly this one, so run it deliberately rather than by
accident.

**Expected result.** A table stating, per finding, which legs and which manuscripts it reaches.

**Test method.** Each "reaches" claim is verified against the *code of that leg*, never against
another leg's prose. That is the error that produced C-1's overreach and the audit's own B-1
overreach.

**Cost.** 2 h. **Depends on:** V2-A1.

#### V2-G5 — Close the audit

**Aim.** Every finding — B-1 … B-13, C-1 … C-5, G-1 … G-6 — carries a terminal status.

**Steps.** For each: `FIXED` (with the task ID), `ACCEPTED-AS-DOCUMENTED` (with the reason and where
it is documented), or `WITHDRAWN` (with what falsified it). Numbering stays separate — B/C/G never
merge; the three-way comparison **is** the result.

**Expected result.** No finding in any of the three audits is left in an open state.

**Test method.** Count the findings; count the terminal statuses; they must match: **13 + 5 + 6 = 24**.

**Cost.** 1 h. **Depends on:** everything.

---

## 5 — Sequencing

### Dependency graph

```
V2-A1 ──► V2-A2 ──────────────────────────────┐
   └────► V2-G4 ───────────────────────────┐  │
                                           │  │
V2-F1 ──► V2-C8                            │  │
V2-F2 ──► V2-D6 ──┐                        │  ├──► V2-G3 ──┐
V2-F3 ──► V2-C9   │                        │  │            │
                  │                        │  │            │
V2-B1 ─┐          │                        │  │            │
V2-B2 ─┼──► V2-C6 ┼──► V2-D4 ──► V2-E5 ────┼──┘            ├──► V2-G5
V2-B3 ─┘          │                        │               │
V2-B4 ──────────────────────► V2-G1 ───────┘               │
V2-B5 ──► V2-D3                                            │
                                                           │
V2-D5 ──► V2-E2 ──┐                                        │
V2-E1 ────────────┴──────────────────────────────────────► │
V2-E3, V2-E4 ─────────────────────────────────────────────►│
                                                           │
V2-C1…C5, C7, C10 ──► V2-G2 ──────────────────────────────►┘
V2-D1, V2-D2 ──► V2-E5
```

### Recommended order

| Phase | Tasks | Why here | Elapsed |
|---|---|---|---|
| **0 — today** | **V2-A1** | Minutes, and it is the only open item touching a paper under review | < 1 h |
| **1 — desk work** | **V2-B1, V2-B2, V2-B3** | The three blocking FAILs. No compute. Authorised since 2026-08-02 and still unexecuted — this is the whole unblocking path | 1–2 days |
| **2 — in parallel** | V2-C1…C5, C7, C10; V2-D1, V2-D2 | Independent of everything; cheap; removes every wrong number a reviewer would hit first | 1 day |
| **3 — compute, launched early** | **V2-E1 (+ V2-D5 → V2-E2)** | The one high finding needing compute. Queue time is the constraint, so submit it while phase 1 is being written | 1 job |
| **4 — decisions land** | V2-B4, V2-B5; V2-C6, V2-D3, V2-D4 | Consume phase-1 output | 1 day |
| **5 — measure** | V2-E3, V2-E4; then **V2-E5** | Sensitivity and spread, then the single re-score. **No new arm** | 2–3 days |
| **6 — citations** | V2-F1, V2-F2, V2-F3 → V2-C8, V2-C9, V2-D6 | Slow, interruptible, blocks only the write-up | in parallel |
| **7 — close** | V2-G1 … V2-G5 | Freeze, flip, write, close | 2 days |

**Critical path: phase 1.** Not compute. Three reading-and-deciding tasks stand between this project
and a resolved scorecard, and eight simulation arms have already demonstrated that no amount of
running moves them.

---

## 6 — Traceability: every finding maps to a task

| Finding | Severity | Task(s) | Note |
|---|---|---|---|
| **B-1** | 🔴 high | V2-A2, V2-B5, V2-D3, V2-F1, V2-F3 | Headline mechanism **falsified** 2026-08-04 (21.38 % of multi-person HHs differ); survives on the max-computed-never-read mechanism; 2J reach **withdrawn** |
| **B-2** | 🔴 high | V2-C9, V2-E4, V2-F3 | Mostly closes on writing; shipped value need not change |
| **B-3** | 🔴 high | **V2-E1** | The one high finding needing compute; reproduced blind as C-4 |
| **B-4** | 🟠 | V2-C5 | Documentation defect; the −25 % decline is real and internationally normal |
| **B-5** | 🟠 | V2-D6, V2-F2, V2-B3 | Mis-specified, not merely vacuous — different denominators |
| **B-6** | 🟡 | V2-D2 | One line |
| **B-7** | 🟡 | V2-E4 | Multi-seed reporting |
| **B-8** | 🟡 | V2-C1, V2-C2 | Reproduced blind as G-1 |
| **B-9** | 🟡 | *deferred* | Step-5 open FAILs; R3 suggests a draw statistic. Not blocking; revisit at V2-G5 |
| **B-10** | 🔵 | V2-C10 | Hotel coverage claim; folds into the doc pass |
| **B-11** | 🟠 | V2-C3, V2-C4, V2-E3 | Falsifier **run**; retail runs at office density 25.0, not ~3.7 |
| **B-12** | 🟠 | V2-C3, V2-E3 | Falsifier **run**; blanket 7.5028 W/m² plug, sign opposite to B-11 |
| **B-13** | 🟠 | **V2-A1**, V2-A2, V2-G4 | The only finding reaching a **submitted** paper. Falsifier unrun |
| **C-1** | — | V2-B5, V2-D3 | Confirmed from code; an independent instance of the audit's own class #11 |
| **C-2** | — | V2-E2 | Validator admits it at `:1749-1755` |
| **C-3** | — | **V2-D1** | Catalogue class **#14** (proposed; #13 is taken — see §3) |
| **C-4** | — | V2-E1 | ≡ B-3, found blind |
| **C-5** | — | V2-D5 | No checkpoint, no rake provenance |
| **G-1** | — | V2-C1 | ≡ B-8, found blind |
| **G-2** | — | **V2-B2** | Bears directly on the blocking `S9-EUI-hotel` gate |
| **G-3** | — | V2-C10 | Self-refuting — the cited doc already carries the correction |
| **G-4** | — | V2-A2 | Mechanism **rejected** from the artefact; traced the manuscript, not the code |
| **G-5** | — | V2-C10 | Self-refuting |
| **G-6** | — | V2-C10, V2-C2 | Self-refuting on the rule; the **share** is genuinely wrong (see C2) |
| **Q1** | Step-9 | **V2-B1** | Band applicability |
| **Q3** | Step-9 | **V2-B3** | Gate rule |
| **Q4/Q5/Q6** | Step-9 | **V2-B4** | Deliverable arm |
| **Q7** | Step-9 | V2-D4 | Stale `BENCH` |
| **Q8a/Q8b** | Step-9 | V2-A2 / V2-E1 | = B-1 / B-3 |
| **decision #2/#3** | Step-9 | **V2-B2** | Authorised 2026-08-02, never executed |

**Count check: 13 B + 5 C + 6 G = 24 findings, all mapped.** B-9 is the only one deferred rather
than tasked, and it is explicitly non-blocking.

---

## 7 — What the two master documents must look like when v2 closes

This is the acceptance test for WP-C and V2-G2. Both documents must satisfy every row.

| # | Condition | Verified by |
|---|---|---|
| 1 | No occurrence of `40,846` / `26,750` outside a correction blockquote | V2-C1 |
| 2 | No occurrence of `~52 %` as a live claim | V2-C2 |
| 3 | Retail density stated as parsed (25.0), with the intended value and the sensitivity result | V2-C3, V2-E3 |
| 4 | The `0.95` peak either re-sourced to a retail table or labelled as inherited from office | V2-C4 |
| 5 | Retail episode-time share stated as a per-cycle table, `1.50–2.14 %`, declining | V2-C5 |
| 6 | Every EUI band traces to a WP-B decision with a date and a source | V2-C6 |
| 7 | Every band in the docs equals the band in the scorer | V2-D4 |
| 8 | `⚠️ PLANNED (Leg 3)` survives only where work genuinely has not shipped | V2-G2 |
| 9 | Every `✅ DONE` names an artefact that exists on disk | V2-G2 |
| 10 | Residential aggregation prose matches `3rdJ_07_aug_to_bem_4split.py:309` | V2-B5, V2-D3 |
| 11 | The Richardson attribution matches what Richardson (2010) actually does | V2-C8, V2-F1 |
| 12 | The limitations content of §V2-G3 is reachable from both documents | V2-G3 |

---

## 8 — Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **A band gets widened instead of re-derived** | medium — it is the path of least resistance, and it has been resisted twice already | fatal to the paper's credibility; creates a vacuous gate by construction | Rule 1 of §3. Every band decision is pre-registered before our number is re-read; the derivation arithmetic is recorded in full |
| **V2-B1 finds no applicable stacked-channel band** | **likely** | `S9-EUI-office` becomes INFO | This is a **legitimate and useful outcome**, not a failure. It converts a FAIL into a published limitation, which is what the Reader's Guide already recommends |
| **Someone proposes a ninth arm to move `S9-EUI-*`** | medium | weeks lost; eight arms already produced zero gate movement | §1 scope exclusion; the uninjected control is the standing answer |
| **V2-A1 finds B-13 is material** | unknown until run | touches a **submitted** manuscript | Run it first, today. The earlier it lands, the more routing options exist with the journal |
| **Step-4 artefacts are unrecoverable (V2-D5)** | medium | V2-E2 cannot be row-matched; B-3's fix is weaker | An honest "not recoverable" in the manifest is acceptable; V2-E1 stands alone without E2 |
| **The Step-8 aggregator prorates 52 % rather than the measured share** | low, but it is the one prose defect that could be a real one | re-aggregation of every cell | V2-C2's test method checks the code, not just the prose. **Do not skip that check** |
| **Cluster queue saturation** | high — 120+ higher-priority tasks were observed on 2026-08-04 | V2-E1 delayed | Submit early (phase 3, in parallel with phase 1); `-t 7-00:00:00`; local fallback exists and was used for arm R's aggregation, with the Python-version caveat recorded |
| **A "fixed" gate is never seen failing** | medium | the fix is itself vacuous — the failure mode this project has catalogued 13 times | Every WP-D task's test method requires a deliberate break. No task closes on a PASS alone |

---

## 9 — Definition of done — closing checklist

v2 closes when **all** of the following hold:

- [ ] All 24 findings (13 B + 5 C + 6 G) carry a terminal status — `FIXED`, `ACCEPTED-AS-DOCUMENTED`, or `WITHDRAWN` (V2-G5)
- [ ] The three EUI gates are resolved as questions: passing against a derived reference, or INFO by demonstrated inapplicability with the limitation published — **none by widening**
- [ ] Step 9 re-scored once, against a pre-registered prediction, with every mismatch reported (V2-E5)
- [ ] Every gate touched by WP-D has been **seen failing** on a deliberately broken input
- [ ] Both master documents satisfy all 12 rows of §7
- [ ] The deliverable arm is named and frozen with full provenance (V2-G1)
- [ ] The 2J-facing decision is made and, if needed, drafted (V2-A2)
- [ ] The consolidated limitations section is written (V2-G3)
- [ ] Every load-bearing citation in WP-F has been **opened**
- [ ] This Progress Log records each task's completion with its test-method outcome, including the ones that returned unwelcome answers

---

## 10 — Progress Log

**Append-only.** Newest entries at the bottom. Corrections are struck-and-restated in place, never
deleted. One entry per task completion, minimum; more if a task changes shape mid-flight.

> **Entry template**
>
> ```
> ### YYYY-MM-DD — V2-<ID> — <task name> — <STATUS>
> **Pre-registered prediction** (if the task produces a number vs a threshold): …
> **What was done:** …
> **Result:** … (numbers re-derived from the artefact's own columns, not quoted from a log)
> **Test method outcome:** … (for a gate fix: the deliberate break, and whether it FAILed)
> **Artefacts:** paths, MD5s, job IDs
> **Consequences:** which findings/tasks move, which documents need updating
> ```

> **Appending rule.** Use a bash heredoc (`cat >> … <<'EOF'`), never PowerShell `Add-Content` —
> PS 5.1 double-encodes UTF-8 and this file is full of accented and box-drawing characters.

---

### 2026-08-04 — document opened — V2 plan authored

**What was done.** Created this file as the **implementation** counterpart to
`improvements/investigation/3rdJ_L3_backward_audit_2026-08-04.md`, in answer to the question of
whether that audit was an investigation or an implementation document. It is an investigation
document (§0); this one carries the executable work.

**Inputs read.** The audit (13 findings, three successive revisions of its order of work); the two
blind replication reports (`REPORT_codex_backward_audit.md` C-1…C-5,
`REPORT_gemini_backward_audit.md` G-1…G-6, plus `gemini-docs/`); `3rdJ_L3_step9_READER_GUIDE.md`
(current state, the eight open questions, the vacuous-gate catalogue); and both master pipeline
documents in full, from which every WP-C line number was verified directly rather than taken from a
report.

**Scope decided.** 36 tasks in 7 work packages. **Zero** retrainings of Step 4. **One** new
EnergyPlus simulation (V2-E3), and it is a pre-registered measurement, not a fix attempt. The
critical path is phase 1 — three desk-work decisions (V2-B1/B2/B3) — not compute, because eight
simulation arms have already produced zero gate movement against those same three gates.

**Verified while writing, not assumed.** Every WP-C target was grepped and confirmed present at the
line number cited: `40,846`/`26,750` at `Pipeline.md:320` and `_Overview.md:125`; `~52 %` at
`Pipeline.md:325/410/434` and `_Overview.md:115/198`; `~3.7 m²/person` at `Pipeline.md:291` and
`_Overview.md:113`; `~2.1–2.3 %` at `Pipeline.md:102/237` and `_Overview.md:77`; the hotel band at
`Pipeline.md:329/427-428` and `_Overview.md:130/214-215`.

**Also noted.** `Pipeline.md:425` already records that StatCan Table 24-10-0048-01 does not exist,
and `Pipeline.md:226` / `_Overview.md:74` already resolve the heads count — so G-3 and G-5 are
closed as verified-no-action (V2-C10) rather than tasked as defects. G-6's *rule* is likewise
already stated; its **share** (~52 %) is genuinely wrong and is tasked as V2-C2.

**Found while writing — a catalogue numbering collision.** The vacuous-gate catalogue disagrees with
itself across four documents: `READER_GUIDE §4` says **12** classes; the `2026-08-05` manager handoff
says **thirteen** and assigns **#13** to *the conjunction gate / monotonicity clause across a
saturation boundary*; the backward audit and its README both propose the *severity-vacuous* gate
(C-3) as "#13", which is already taken. Renumbered here to **#14**, and reconciling all four
documents is now a step of V2-D1 and a closing condition of V2-G5. Minor in itself — but the
catalogue is this project's most transferable methodological output, and a catalogue that
double-numbers its own classes is not citable.

**Next action.** **V2-A1** — run the B-13 falsifier. It is minutes of work and the only open item
touching a manuscript already under review.

---

---

### 2026-08-04 (night) — V2-C7 — Step-9 citation defects — **DONE (no-op)**

**What was done.** Opened both target files rather than trusting the plan's description. Both defects
were **already fixed on 2026-08-04**, before this task existed:

- `improvements/v1/3rdJ_L3_improvements_step9.md` (lab notebook, append-only): `Q8` struck at `:7698`
  with a 🔴 CORRECTION block and split into **Q8a** (`:7708`) / **Q8b** (`:7719`); Q2's figure struck
  in place at `:7604` as `~~19 %~~ **14.55 %**` with a correction blockquote at `:7613-7619`.
- `improvements/v1/3rdJ_L3_step9_READER_GUIDE.md` (report, edited in place): Q8a/Q8b split live at
  `:113-117`; no live "19 %" claim anywhere.

**Test method outcome.** `grep -nE "Q8[^ab]"` → log `:7698` (the struck original) and guide `:148`
only. `grep "19 %"` near "uninjected" → log `:7604` + `:7613-7616`, guide `:149`. **Every surviving
hit is inside either a strikethrough or the guide's "Register of Reversals" table**, which exists
precisely to preserve the original wrong claim beside its correction. That is the convention working,
not a defect.

**Result.** No edit required. Status **DONE**, closed as already-satisfied.

**Consequences.** Audit item 5f closed. A no-op is recorded rather than silently dropped, so the task
is not re-opened by a future reader of the summary table.

---

### 2026-08-04 (night) — V2-C10 — Gemini's three self-refuting findings — **DONE**

**What was done.** Verified all four cited line references by opening them — the whole point of the
task — then appended one dated subsection to the audit's closing section.

**Test method outcome — 4/4 PASS**, each line actually containing the correction claimed:

| Finding | Site | Verified content |
|---|---|---|
| G-3 | `Pipeline.md:429` | "Verified in `dr_L3-01` that Table 24-10-0048-01 does not exist … Sourced instead from Tourisme Québec / ISQ … and Travel Alberta" |
| G-5 | `Pipeline.md:226` | "**Heads count, resolved.** … **§3.5 is authoritative: three GSS heads + a non-GSS hotel side-track.**" |
| G-5 | `_Overview.md:74` | "\"4 heads\" in the PNG = diagram shorthand; 3 GSS heads is authoritative" |
| G-6 | `Pipeline.md:327` | "**Service/MEP …:** prorated by area onto the four tenant channels" — the *rule* is stated |

> 🔴 **Line numbers drifted mid-task.** The employee reported `Pipeline.md:425` (G-3) and `:325`
> (G-6); by the time the manager re-checked, the same content sat at `:429` and `:327`, because the
> V2-C1/C2 employee was editing the same file concurrently. Content was therefore re-verified **by
> grep on the text**, not by line number. **Method note for the rest of WP-C: two employees must not
> hold the same master document open at once, and acceptance criteria in this plan should cite text,
> not line numbers, wherever a concurrent edit is possible.**

**Result.** G-3 and G-5 closed **verified-no-action**. **G-6 is only half self-refuting**: its
prorating *rule* was already correctly stated, but the **~52 % share** at that same site is genuinely
wrong and remains open under V2-C2. Recorded as such rather than closing G-6 wholesale.

**Artefacts.** `improvements/investigation/investigation_v2/3rdJ_L3_backward_audit_2026-08-04.md`,
2317 → 2345 lines, appended by bash heredoc (UTF-8 preserved; accents and box-drawing intact).

**Consequences.** G-3, G-5 → terminal status for V2-G5. G-6 splits: rule-half closed, share-half → V2-C2.
🔴 **Plan defect found:** §0 and §6 cite the audit at `improvements/investigation/…`; it actually
lives at `improvements/investigation/investigation_v2/…`. Correct on the next pass of this file.

---

### 2026-08-04 (night) — V2-C1 — Floor areas in both master docs — **DONE**

**What was done.** Replaced the legacy unparsed areas in the *body* of both master documents.
`Pipeline.md:320` and `_Overview.md:125-128` now read **135,857.6 m² (SuperTall) / 72,623.1 m²
(Tall)**, each with a pointer to `Step8_docs/outputs_step8/agg/agg_meta.csv`
(`total_building_area_m2`) so the value is never retyped by hand again.

**Result — and the more interesting half.** Both documents **already carried** a 2026-07-31
"🔴 CORRIGÉ (Défaut 7)" header blockquote holding these exact corrected values
(`Pipeline.md:10-40`, `_Overview.md:10-19`). The body text at Step 8 was simply never synced to the
header. So **G-1/B-8 was not an unmeasured error — it was a propagation failure inside a document
that already knew the right answer.** That is a distinct and more embarrassing failure mode than
being wrong, and it belongs in the write-up: a correction recorded only in a header is not a
correction.

**Test method outcome.** `grep -nE "40,846|26,750|40 846|26 750"` over both files → **3 hits, all
inside `>` blockquotes labelled superseded**: `Pipeline.md:30` (pre-existing header),
`Pipeline.md:324` (new Step-8 sourcing blockquote, "the superseded 40,846 / 26,750 m²"),
`_Overview.md:15` (pre-existing header). **Independently re-run by the manager — PASS.**

**Consequences.** G-1 and the area half of B-8 → FIXED. §7 row 1 satisfied.

---

### 2026-08-04 (night) — V2-C2 — Service/MEP share — **DONE**, and the risk-register item is **dead**

**What was done.** Corrected all five "~52 % gross" sites — `Pipeline.md:330`, `:425`, `:449`,
`_Overview.md:116`, `:201` — to **20.6 % · 21.4 % of gross (measured)**, with a new Step-8 blockquote
at `Pipeline.md:332-340` carrying the superseded value and the derivation.

**🔴 The critical sub-check — the one prose defect that could have been a real one.** §8 of this plan
listed "the Step-8 aggregator prorates 52 % rather than the measured share" as the risk whose
realisation would force a **re-aggregation of every cell**. It did not happen:

- `grep` for `0.52` / `52%` across `3rdJ_08E_aggregate_4split.py` and all of `Step8_docs/*.py` →
  **zero hits**. There is no hardcoded share in the code at all.
- `parse_channel_areas()` (`3rdJ_08E_aggregate_4split.py:104-148`) derives every channel area from
  each cell's own injected IDF/SQL via `Zones.FloorArea × Multiplier`, restricted to
  `IsPartOfTotalArea = 1`, and reproduces EnergyPlus's own ABUPS "Total Building Area".
- The GFA-share prorating at `:544-554` consumes that **measured per-cell** share.

**Re-derived from the artefact's own columns** (rule 4 — not quoted from the employee's report):
`agg_meta.csv`, cell `B_central__SuperTall__CLG` → `area_service_MEP_m2 / total_building_area_m2`
= 28 041.63 / 135 857.59 = **20.640 %**; Tall → 15 547.7 / 72 623.1 = **21.41 %**. Matches.

**Test method outcome.** `grep -nE "52 %|52%"` over both files → **5 hits, all inside `>`
blockquotes**: `Pipeline.md:32`, `:48` (pre-existing header/roadmap), `:335`, `:339` (new Step-8
blockquote), `_Overview.md:14` (pre-existing header). **Independently re-run by the manager — PASS.**

**Result.** Pure prose defect. **No code change, no re-aggregation, no WP-D escalation, and every
GFA-share EUI number already produced stands unaffected.** The `dr_L3-10` prorating *operation* is
mechanically unchanged; only the magnitude redistributed changes (~21 %, not ~52 %), which means the
corrected numbers move tenant GFA-share EUIs **less** than the old prose implied — noted at
`Pipeline.md:338-340`.

**Consequences.** Rest of B-8 → FIXED. G-6's share-half → FIXED. §7 row 2 satisfied. **§8 risk
"aggregator uses 52 %" → CLOSED, did not materialise.**

---

### 2026-08-04 (night) — V2-D1 — RW6 severity (vacuous-gate class #14) — **DONE, gate seen failing**

**Severity decision: `hard=True`.** RW6 sits in the val doc's "**Hard gates — RETAIL channel**"
section (`3rdJ_04_augmentationGSS_4split_val.md:43-54`) with the same table shape (Gate/Metric/PASS/
WARN, no literal FAIL column) as RW1/RW3/RW4/RW5/RW8 — **all of which do FAIL** via `self._grade()`.
The original justification comment claimed "no FAIL column" made RW6 soft; that column is absent from
every row in the section, so it is the table's format, not a severity statement. No derivation
anywhere states the 0.06 floor is soft. Contrast RW7's QC<AB check, which **genuinely has** one
(job 1128112, sampling-SE analysis) and correctly stays WARN. 🔴 **Band values untouched — nothing widened.**

**`hard=False` sweep (step 3 — the "this class is probably not unique" check).** Whole-repo grep:
`hard=` appears in exactly one file, `3rdJ_04_augmentationGSS_4split_val.py`, at five call sites
(`:1296, 1300, 1304, 1308, 1312`), **all five inside `_validate_rw6_rw7`, all five RW6**. No other
override exists anywhere in the codebase. Manager re-ran the sweep: only the function's own default
`hard=True` (`:1267`) now remains.

| RW6 window | band | current value | was it vacuous? |
|---|---|---|---|
| Weekday 12–14 h | [0.06, 0.10] | **0.0453** | **yes — WARN, should be FAIL** (24.5 % below floor, outside the 30 % buffer) |
| Saturday 13–16 h | [0.09, 0.12] | 0.0836 | no — inside the WARN buffer either way |
| Sunday AB 12–16 h | [0.06, 0.10] | 0.0498 | no — inside the buffer |
| Sunday QC 12–17 h | [0.04, 0.07] | 0.0519 | no — PASS |
| Night 00–05 h | [0.000, 0.003] | 0.0002 | no — PASS |

Only the weekday row was vacuous **today**, but the defect lived in the shared call, so all five were
fixed: a future run with a broken retail head on any other window would have hit the same trap.

**🔴 Test method outcome — the gate was SEEN FAILING** (rule 3; harness replicating `_grade_band`
verbatim, before and after):

| input | BEFORE | AFTER |
|---|---|---|
| real weekday 0.0453 vs [0.06, 0.10] | `warn` | **`fail`** |
| deliberately broken 0.0100 vs [0.06, 0.10] | `warn` | **`fail`** |
| deliberately broken 0.0200 vs [0.000, 0.003] | `warn` | **`fail`** |
| control, in-buffer 0.0500 vs [0.06, 0.10] | `warn` | `warn` — unchanged, confirming no band was widened |

**Artefacts.** `3rdJ_04_augmentationGSS_4split_val.py:1267-1313`; `py_compile` clean.

**🔴 Consequence, stated plainly because it is unwelcome.** This fix **converts a shipped Step-4 WARN
into a FAIL.** RW6-weekday now fails at 0.0453 vs a 0.06 floor. That is the correct outcome — the
value was always 24.5 % below the floor and the gate was declining to say so — but the Step-4
scorecard changes and every document quoting it must be updated. It also collides productively with
**B-5**: the retail *rate* gate was independently shown **mis-specified** (its reference band is
denominated on store design capacity while the gate measures a population rate). So RW6 may not
survive as a FAIL — **V2-D6 may re-specify it against a population-denominated reference or demote it
to INFO**. Both moves are legitimate; **neither is "widen the band"**. Until V2-D6 lands, the honest
state is: *the gate now correctly reports a failure against a reference we have reason to think is
the wrong reference.*

**Catalogue.** Class **#14** — the severity-vacuous gate (computes a real failure, declines to call
it one). Renumbered from the audit's proposed #13, which is taken. Propagation into the four
disagreeing documents remains open under V2-G5.

---

### 2026-08-04 (night) — V2-D2 — ISR-raw severity — **DONE**

**What was done.** The defect was not where the plan expected. The **code** was already WARN-capped —
`_grade_isr_raw` (`3rdJ_04_augmentationGSS_4split_val.py:483-489`) can never return `fail`, called
from `validate_exclusivity` (`:1356-1375`). What was missing is that **the val doc's gate table still
said `FAIL`**, so the relaxation existed only in code comments and one Progress Log line. That is
exactly B-6: a gate relaxed without the deviation being recorded where the spec lives.

Struck-and-restated at the definitional site `3rdJ_04_augmentationGSS_4split_val.md:60`:
`~~FAIL~~ → **WARN**`, plus the deviation record — original bar **≤ 0.5 %** (the Leg-2 2-channel
threshold), relaxed to a **1.5 % soft, never-FAIL** bar on **2026-07-20**, observed **0.7031 %**.

**Test method outcome — verified against behaviour, not assumed.** `isr_raw_pass = 1.5` in production
(`:365`) vs `3.0` in sample mode (`:322`); `_grade_isr_raw` returns `"pass"` for any value ≤ 1.5 %
and has no `fail` branch; and the emitted line in **both** locked-pool reports
(`outputs_step4/sweep/seed_3_raked3_mindwell_actv/step4_validation_report.txt:125` and
`seed_3_g3fix_raked3_mindwell_actv/…:127`) reads
`[PASS] ISR-raw | Raw (pre-projection) ISR: 0.7031% … (soft target <= 1.5%)`.

**🔴 The part worth keeping.** The observed **0.7031 % is above the original 0.5 % bar**, and the
validator reports it as `[PASS]` — not even WARN — because the bar was moved to 1.5 %. Under the
original specification this gate did not pass. That is now recorded at the spec site rather than
being inferable only by reading source comments.

**Result.** ISR-final (= 0 % by construction) is unaffected and stands. No grading logic changed —
D2's scope is the definitional record, not a re-grade.

**Consequences.** B-6 → FIXED (documentation half; the deviation is now published). Feeds V2-G3's
limitations section.

---

### 2026-08-04 (night) — V2-A1 — the B-13 falsifier — **DONE. B-13 does NOT reach the submitted paper.**

**Pre-registered materiality threshold** (written before the run, unchanged): **1 % of annual
person-hours**. Below it, B-13 is a documentation defect only.

**Step 1 — the pivot, settled.** `social_sum` **excludes self**. It is the row-sum of seven GSS
"who were you with" binaries (`21CEN22GSS_HH_aggregation.py:37-45` → raw GSS `SPOUSE`, `CHILDHSD`,
`TUI_06B…TUI_06J` via `02_harmonizeGSS.py:495-531`; codebook wording confirmed per column in
`docs_debug/DONE/02_W7_copresence_encoding_audit.md` §2A, consistent across all four cycles). So the
`+1` in `occToBEM.py:144` is **correct for one respondent**. The defect is one line later:
`21CEN22GSS_HH_aggregation.py:177-178` **sums `social_sum` across all household members**
(`dens_stack.sum(axis=0)`), so two co-residents who each report the other are counted twice. That is
the plan's verdict **(a)**: the `+1` is right, the *sum* over-counts.

**Steps 2–4 — the mechanism is real and it is large.** Measured on
`0_Occupancy/Outputs_21CEN22GSS/HH_aggregation/21CEN22GSS_Full_Aggregated_sample25pct.csv`
(41,345,280 five-minute slot-rows; the only `occDensity`-bearing artefact on disk — no 100 % version
exists, only up to 25 %):

| HHSIZE | rows | `occDensity+1 > HHSIZE` | % |
|---|---|---|---|
| 1 | 6.24 M | 162,499 | 2.6 % |
| 2 | 14.26 M | 3,859,375 | **27.1 %** |
| 3 | 7.75 M | 1,086,253 | 14.0 % |
| 4 | 7.87 M | 581,100 | 7.4 % |
| 5 | 5.22 M | 235,375 | 4.5 % |
| **all** | 41.35 M | 5,924,602 | **14.3 %** |

`.clip(upper=1.0)` binds on **15.9 %** of occupied slots overall, **29.7 %** for two-person
households — exactly where the over-count would have surfaced, silently absorbed. Difference vs the
max rule: mean |Δ| = **0.232** schedule units, **32.55 %** of person-hours. That is **32× the
pre-registered 1 % threshold.** On the code as written, B-13 would stand, and stand hard.

**🔴 Step 2 also produced a fourth verdict the task did not enumerate, and it is the one that
matters: `21CEN22GSS_occToBEM.py` is not the converter behind the submitted manuscript.**

The employee raised it; the manager verified it independently rather than accepting it, because it
decides whether a paper under review needs a correction:

1. The production converter is `2J_docs_occ_nTemp/07_aug_to_bem.py` (13,246 bytes, **2026-07-13**).
   Its `convert()` computes `occ48 = df.groupby(["SIM_HH_ID","Day_Type"])[HOM].mean()` at **`:97`**,
   commented `# (G,48) fraction home`. **No `occDensity`, no `social_sum`, no `× (density+1)`, no
   `.clip()` anywhere in the file** — verified by grep. It cites the old script only to borrow its
   `metabolic_map` (`:30`), so its author knew the legacy converter and deliberately did not reuse
   its occupancy formula.
2. `07_aug_to_bem.py:103` reshapes 48 slots to 24 hours by pairwise mean — a word-for-word match to
   **`readySubmission.md:231`**, *"The diary basis is 48 half-hour slots; paired slots are averaged
   to 24 hourly values at the IDF interface."*
3. **The decisive empirical check** (manager-run, on the artefacts themselves rather than on code
   reading): the shipped `BEM_Setup/BEM_Schedules_2022.csv` (673 MB, **2026-07-09** — the same relink
   date the manuscript cites at `:211`) has `Occupancy_Schedule` values for multi-person households
   of `0.000, 0.083, 0.100, 0.125, 0.167, 0.200, 0.250, 0.300, 0.333, …, 0.917, 1.000` — steps of
   1/12, 1/10, 1/8, 1/24. **A fraction of members, averaged over paired slots.** A max rule yields
   only {0, 1}; the `occDensity` rule yields a clip-saturated mass at exactly 1.0. Neither is what
   ships. The legacy output survives beside it as `BEM_Schedules_2022_CLASSIC_BAK_2026-05-31.csv`
   (103 MB, **2026-04-10**) — retired on 2026-05-31, well before submission.

**And the manuscript is consistent with the shipped code.** The two sentences sit three paragraphs
apart and must be read together:

- `readySubmission.md:211` (§3.3, *household formation*) — "taking the per-slot **maximum** AT_HOME
  indicator across household members, so that a slot is classified as occupied if any member is
  present", immediately followed by the plausibility gate "whose **mean** at-home fraction falls
  below 0.30". That max is the **household occupancy indicator feeding the 0.30 exclusion**, exactly
  as Leg-3's `HH_hom30_*` → Step-5H does. It is not the schedule.
- `readySubmission.md:231` (§3.5, *conversion to schedules*) — "Four parallel schedule channels are
  derived per household: **occupancy (AT_HOME fraction)** … load the EnergyPlus `People` object."
  **"Fraction" is the mean**, and it matches `07_aug_to_bem.py:97` exactly.

**Result — verdict, stated plainly.**
- **B-13 → WITHDRAWN as a paper-facing finding.** The submitted manuscript does not describe a
  converter it does not have. **No erratum is owed.** The plan's §8 risk *"V2-A1 finds B-13 is
  material → touches a submitted manuscript"* **did not materialise.**
- **B-13 survives as a code-hygiene finding.** The over-count is real, 32.55 % material, and still
  sitting in `21CEN22GSS_occToBEM.py` where anyone could re-run it. It should be marked deprecated at
  the top of the file, pointing to `07_aug_to_bem.py`. **New task V2-D7.**
- **One genuine clarity defect in the manuscript, worth a clause and nothing more:** §3.3's "occupied
  if any member is present" and §3.5's "occupancy (AT_HOME fraction)" are separated by three
  paragraphs, and a reader can conflate them into a contradiction. Recommended wording for §3.3:
  *"…the per-slot maximum AT_HOME indicator across household members — used to classify dwelling
  occupancy for the plausibility gate below; the People schedule itself carries the member fraction
  (§3.5)."* **Not an erratum — a revision-round clarification if a revision round happens anyway.**

**Test method outcome.** Row counts cross-checked against the frame; the value-set test on the
shipped CSV is a positive discriminator (it distinguishes all three candidate rules, not merely
"looks plausible"). **Caveat recorded:** the count tables come from the **25 % sample** — the only
`occDensity`-bearing file that exists — so they characterise the legacy mechanism, not the frame. As
the mechanism is now known not to ship, refining them is not worth a run.

**Artefacts.** `scratchpad/b13_falsifier.py`; `BEM_Setup/BEM_Schedules_2022.csv` (2026-07-09);
`BEM_Setup/BEM_Schedules_2022_CLASSIC_BAK_2026-05-31.csv` (2026-04-10).

**Consequences.** **V2-A2 collapses** from "draft a correction to a submitted paper" to "draft one
optional clarifying clause" — see its own entry. **V2-G4** gains its hardest row: B-13 stops at the
legacy-converter boundary and does **not** reach 2J, which is the *second* finding to die on exactly
this check (C-1's "reaches 2J" was the first). **Two of three audits over-claimed cross-leg reach in
the same way** — that belongs in the write-up as a methodological result about blind replication, not
as a footnote.

---

### 2026-08-04 (night) — V2-C3 — Retail occupant density — **DONE, self-verified from the IDF**

**What was done.** Corrected "~3.7 m²/person" in both master documents to the **parsed 25.0
m²/person**, with the parse command embedded so it can be re-run.

**Result — verified from the artefact, not quoted from the audit.** The employee parsed the injected
IDF directly (`Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/CAN_MTL/TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf`):
`Retail Retail`, `Retail Back_Space` and `Retail Point_of_Sale` `PEOPLE` objects all carry
**0.040015 person/m² = 25.0 m²/person**, **bit-identical to `OpenOffice`**. Independently confirmed
the rest of B-11/B-12's shape at the same time: plug density is blanket (**7.5028 W/m²** on both
Retail and OpenOffice `ElectricEquipment`), while **lighting is correctly per-space-type**
(OpenOffice 6.566 vs Retail Entry 9.042 vs Retail Retail 9.5 W/m²).

**The consequence, recorded at the site because it is load-bearing elsewhere.** Occupant density and
plug density are **one blanket office value each across all 17 space types in both towers**. So
office is the channel those constants are plausibly right *for*, and correcting them moves retail,
hotel and residential but **cannot move office**. That does not weaken the office problem — it
**strengthens the band-applicability argument in V2-B1**, by removing the most obvious "our constants
are wrong" explanation for the office shortfall.

**Edits.** `Pipeline.md:306` (struck + restated), new correction blockquote `Pipeline.md:309-330`,
`_Overview.md:113` (byte-exact ASCII-box edit), consolidated blockquote `_Overview.md:150-166`.

**Consequences.** B-11's documentation half → FIXED. The magnitude half stays open under **V2-E3**,
which is the one new simulation in this plan. §7 row 3 half-satisfied (the sensitivity result is still owed).

---

### 2026-08-04 (night) — V2-C4 — The 0.95 retail peak — **DONE as far as it can go without the NECB table**

**What was done.** The injector was already vindicated (`0.9215 = 0.95 × 0.97`, exact). The question
was the provenance of the 0.95. It is **labelled at all five sites as inherited from the office
baseline, not independently sourced for retail**, with re-sourcing marked owed to WP-F.

**🔴 The employee found the supporting mechanism in the IDF, which is stronger than the label.** The
retail `PEOPLE` objects reference `Number of People Schedule Name = NECB-A-Occupancy` (IDF `:96552`),
and that schedule's weekday shape **peaks at 0.9 and dips to 0.5 at 12:00-14:00** (`:96566-96570`).
**A midday trough is an office lunch signature; a retail profile peaks there.** So the retail baseline
being modulated is office-shaped as a matter of fact, not inference — which is exactly what B-11
predicted from the density side, arrived at independently from the schedule side.

**Result.** 0.95 is **not** re-sourced — that requires opening NECB 2017/2020, which is WP-F work and
was correctly not faked. What is now published is the honest statement: the retail channel modulates
an office-shaped baseline, and this is a **stated limitation**, not a bug.

**Edits.** `Pipeline.md:332`, `:349`, `:486`; `_Overview.md:111`, `:241`, plus the consolidated blockquote.

**Test method outcome.** The task's own test — "the cited table, page and row must be named" — is
**NOT satisfied and is not claimed to be.** It remains open under WP-F. Recorded as owed rather than
closed, per rule 5.

**Consequences.** B-11 provenance → partially closed; strengthens B-5. Blocks on V2-F.

---

### 2026-08-04 (night) — V2-C5 — Retail episode-time share — **DONE, with a better source than the plan cited**

**What was done.** Replaced "~2.1-2.3 %, stable across cycles" at `Pipeline.md:102`, `:252`,
`_Overview.md:77`, and added the reconciliation subsection at `Pipeline.md:104-117`.

**Result — the per-cycle table, re-derived rather than quoted** (rule 4). The employee found a more
directly reproducible source than the audit citation: `Step2_docs/3rdJ_02_harmonizeGSS_4split_val.md:77-82`,
the gated OR-rule table that **is** the `AT_RETAIL` definition, re-runnable via
`py -3 -X utf8 3rdJ_02_harmonizeGSS_4split_val.py`:

| cycle | 2005 | 2010 | 2015 | 2022 |
|---|---|---|---|---|
| retail episode-time share | 2.00 % | **2.14 %** | 1.66 % | **1.50 %** |

Range **1.50-2.14 %**, and 2005 → 2022 is **−25.0 %**. Reproduces the claim exactly. The old "stable
across cycles" was not a rounding difference — it asserted the opposite of the trend.

**The reconciliation, which is the part a reviewer needs.** The measured −25 % decline and the 2030
lever's near-flat **0.97** default read as contradictory unless the saturation argument is stated: the
0.97 encodes the **flattening of the e-commerce displacement curve after 2022**, not a linear
extrapolation of the steep 2005-2022 phase. Now said explicitly at the site, with R2's international
corroboration (ATUS / UK / HETUS all show the same direction).

**Consequences.** B-4 → FIXED. §7 row 5 satisfied.

---

### 2026-08-04 (night) — V2-B5 — Residential aggregation, mean or max — **DECIDED: the mean stands.**

**🔴 The task's premise was wrong, and that is the finding.** The plan states *"The defect is that
nobody chose."* **Somebody chose, in writing, and locked it fourteen months of project-time ago.**
Verified by the manager at each site:

- `3rdJ_07_aug_to_bem_4split.py:16` — *"OD-7A -- Residential occupancy = mean(hom30) over HH members
  (**NOT** HH_hom30/max)."* The exclusion is explicit, not incidental.
- `Leg2_2-split/Step7_docs/3rdJ_07_bemIntegration_2split.md:309-316`, **locked 2026-06-26**, with the
  physical rationale: EnergyPlus computes `occupants(t) = Number_of_People × schedule(t)`; with
  `Number_of_People = HHSIZE` and `schedule = mean(hom30)`, the product is **expected headcount
  present**. The max would count the whole household whenever *any* member is home — *"a 1-of-4
  afternoon → 4 people's metabolic heat"*.
- `eSim_bem_utils/commercial_integration.py:1980` — `p.Number_of_People = hh["hhsize"]`, confirming
  the multiplier the argument depends on.

**And `HH_hom30_*` is not dead weight either.** It is read at
`3rdJ_05_censusLinkage_4split.py:1211` inside `run_exclusion()` (Step 5H): households whose
mean-of-max AT_HOME falls below **0.30** are excluded from the pool — the same gate the 2J manuscript
describes at `readySubmission.md:211`. It also feeds one Step-5 validator plot.

**Decision.** **Mean stands. `HH_hom30_*` is retained, not deleted.** No re-run is triggered — the
campaign is unaffected.

**Consequences.** **C-1 → WITHDRAWN as a defect**, downgraded to *documentation*: the code was right
and reasoned; what was missing was a comment at the point of use, which **V2-D3** now adds.
🔴 **Vacuous-gate class #11** (*the gate measuring a quantity the deliverable discards*) **does not
apply here** — the quantity is not discarded, it gates pool membership. The audit's use of this case
as an instance of #11 should be struck at V2-G5. **Two independent auditors (the backward audit and
Codex) both read "computed here, not read there" as an accident without checking for a decision
record.** That is a general lesson about blind replication and belongs in the write-up.

---

### 2026-08-04 (night) — V2-B2 — Hotel band re-derivation — **PARTIAL: the contradiction is established; the replacement band is blocked on a citation.**

**What was done.** Reproduced `dr_L3-03_hotel_eui_bands_REPORT.md` Table 2 (`:58-68`) in full and
tried to reconstruct the recommended **[180, 240, 300]** from its own rows. Manager re-read the table
and the justification text directly.

**Result — the recommendation is only one-third reproducible from the table it cites.**

| bound | report's stated justification (`:114-115`) | does Table 2 support it? |
|---|---|---|
| **180** floor | "a compliant Small Hotel prototype (~180.0)" | **No.** Table 2's Small Hotel 90.1-2019 row is **135.0-175.0**. 180 matches no row. |
| **240** central | "a code-minimum **Large Hotel** prototype … modern mechanical and lighting" | **No.** Every modern-code (90.1-2016/2019) Large Hotel row is **441.6-521.2**. 240 is in fact the **NECB-2017 CZ7 (Calgary)** upper bound — a row the justification never names. |
| **300** ceiling | "Large Hotel archetypes designed to older baseline codes (90.1-2004) in CZ7" | **Yes** — 90.1-2004 Large Hotel CZ7 = **302.2**, rounded down. The one traceable bound. |

**Two further contradictions inside the same report.** (i) `:124` states *"our simulations model the
hotel floors of PNNL-style mixed-use prototypes under **NECB 2017 and ASHRAE 90.1-2019**"* — then
builds a band that **excludes 90.1-2019's own Large Hotel rows (441.6 / 479.5) entirely**, without
explanation. (ii) §4 (`:138-141`) argues that a hotel podium in a mixed tower **is** a Large Hotel
("central hydronic loops, DOAS, commercial laundry, centralized DHW boilers"), which — taken at face
value — argues for **441-521**, i.e. *far above* the current ceiling, not for narrowing it.

**Correction to this plan's own text** (rule 6, struck-not-deleted): §4b V2-B2 says ~~"**6 of 11**
reference rows above 300"~~ → **5 of 11**. Rows strictly above 300 are 302.2, 484.0, 521.2, 441.6,
479.5. 286.4 is not. Manager re-counted from the table.

**Where this leaves the decision.** The archetype match is genuinely arguable in **two directions**,
and it is not close:
- **NECB-2017 code-compliant tower hotel** (our tower is NECB-based) → band from the two NECB rows:
  MTL (CZ6) **[140, 220]**, CLG (CZ7) **[160, 240]**.
- **Large Hotel, 90.1-2019** (the report's own §4 service-configuration argument) → **[441, 521]**.

**🔴 Not adopted, and deliberately so.** Both candidate bands trace to sources **nobody has opened** —
the *CanmetENERGY Commercial Archetypes Performance Study (2020)* and PNNL-28543. Rule 5: a citation
is not evidence until opened. Adopting a band from an unopened source to replace a band from an
unreproducible one would swap one undefended number for another.

**What is nonetheless now established, and it is the useful half:** `S9-EUI-hotel`'s **300 ceiling is
inherited from a 90.1-2004 row while the report elsewhere states the modelled vintage is 90.1-2019 /
NECB 2017.** Finding **G-2 is CONFIRMED** — the gate inherits a contradiction. The gate cannot be
called sound in its present form regardless of which way the archetype falls.

**🔴 And the direction of travel is worth stating before anyone hopes otherwise: the most likely
re-derivation (NECB-2017, matching our NECB tower) lowers the ceiling from 300 to 240 — which makes
arm R's hotel (271.40) fail *harder*, not softer.** Recording this now, before the band is settled,
so that the eventual choice cannot be read as fitted.

**Consequences.** G-2 → CONFIRMED. Step-9 decisions #2/#3 remain open, now blocked on **one specific
citation** rather than on judgement. **New task V2-F4: open the CanmetENERGY 2020 archetype study and
PNNL-28543.** V2-C6 and V2-D4 stay BLOCKED. V2-B4's K choice is now **entangled** with this: under a
[140, 240] band, arm H (178.29) sits comfortably in band while arm R (271.40) is out — so the band
decision and the plant-sizing decision must be taken together, and **neither may be taken on which
combination scores better.**

---

### 2026-08-04 (night) — V2-B3 — The retail gate rule — **DECIDED, with its weakness stated**

**The question.** `S9-EUI-retail` fails on an **all-56-cells-in-band** rule. Arm R is 54/56; the two
misses read **79.82** and **79.96** against an 80.00 floor — short by **0.23 %** and **0.06 %**.

**Step 1 — what is the gate for?** It is an **absolute-level plausibility** check on a channel: does
this channel's energy intensity sit where a channel of this type should sit? That is a statement
about the channel's **central tendency**. It is not a per-cell anomaly detector — per-cell anomalies
are already caught by attribution closure (≤ 1e-6 on every cell) and the per-cell residual checks.

**Step 2 — the rule, stated independently of our numbers.** **The median across the 56 cells must lie
within the band. Per-cell min/max are reported as INFO.** Justification: the reference bands are
derived from prototype simulations that are themselves **single points**, with no distributional
content. Asking a single-point band to bound the spread of 56 scenario × geometry × city cells asks it
for something it never described. Median-to-band is the like-for-like comparison.

**🔴 Step 3 — the discriminating counterfactual, named as required.** This gate FAILs when a channel's
**central** level is implausible: a −30 % retail shift moves the median from ~86.6 to ~60.6, below the
80 floor → **FAIL**. It does **not** fail on a single anomalous cell — **stated as a deliberate
limitation, not hidden**, because that failure mode is covered elsewhere. A gate that catches
everything discriminates nothing.

**Step 4 — applied uniformly to all three EUI gates**, which is the test of whether a rule is fitted:

| channel | median | band | verdict under the new rule |
|---|---|---|---|
| office | 81.27 | [100, 200] | **still FAIL** |
| retail | ~86.57 | [80, 155] | **PASS** (was FAIL on 2/56) |
| hotel | pending V2-B2 | pending | pending |

**It does not rescue office.** A rule invented to erase failures would have.

**🔴 The weakness, stated because rule 2 requires it.** This rule was chosen **with our numbers
already known** — they are on the face of this plan. It is therefore **not pre-registered and is
weaker evidence**, and the write-up must say so. The mitigations are on the record: it is applied
uniformly, it leaves office failing, and it changes the **statistic**, never the **band** — no
interval was widened by a single unit.

**Test method — owed, not yet done.** Per the plan: score the rule against a deliberately broken
input (retail EUI shifted −30 %) and confirm it FAILs. **This has not been run.** It is a required
step of **V2-E5** and this task is not fully closed until it has been seen failing (rule 3).

**Consequences.** Q3 → decided. `S9-EUI-retail` → expected PASS at re-score; **written here as a
pre-registered prediction for V2-E5.** Compounds with B-5, which independently showed the retail
*rate* reference mis-specified. V2-D4 must implement the rule change as a **statistic**, not a band edit.

---

### 2026-08-04 (night) — V2-B1 — Office band applicability — **DECIDED: verdict (c). The gate stays FAIL, and that is the honest answer.**

**Step 1 — how the band was derived, established.** `BENCH["office"] = dict(central=135.0, lo=100.0,
hi=200.0)` at `3rdJ_09_activityDrivenLoads_4split.py:93-95`. Traced to
`Leg2_2-split/Step8_docs/deepResearch/Office Reference EUI (NECB 2020, ASHRAE 90.1, DOE-PNNL
prototypes) — As-Modelled Bands.md`, Table 7.1 (`:150-155`), *"Total Site EUI (All-Fuels): 100 to 200
(Central 135)"*. Prototype = **PNNL Large Office, a STANDALONE 12-storey tower + basement, ~46,320 m²
GFA** (`:20`); vintage 90.1-2019 / NECB-2020-equivalent; CZ 6 and 7; basis **"gross conditioned floor
area"** (`:132`) — the same basis our scorer calls CFA. **Bases match; that is not the explanation.**

> 🔴 **Provenance defect found in passing.** The `src=` string in the scorer points at
> `Step8_docs/deepResearch/…As-Modelled Bands.md` **under Leg-3, where no such file exists**. The real
> source is under `Leg2_2-split/`. A band whose recorded provenance path is broken is one refactor
> away from being undefendable. **Fix in V2-D4.**

**Step 2 — a stacked / mixed-use office band: CLEAN NEGATIVE.** None exists anywhere in the project's
sources. `dr_L3-10_mixeduse_reporting_positioning_REPORT.md:79-86` frames our own vertically-stacked
tower as the novelty, and notes that even the closest precedent (Doma & Ouf) models mixed use as
**separate buildings**, not stacked. So there is no archetype-matched band to adopt.

**Steps 3-4 — two candidate mechanisms, both TESTED, both REFUTED.** This is the substance of the task.

**Mechanism 1 — envelope exposure** ("a buried mid-tower floor has less envelope, so reads lower").
Already built and run as `3rdJ_09X_envelope_exposure.py` (56 cells × 6 channels), **prediction
pre-registered in the script itself at `:33-46`: office < retail < hotel exposure.**

| channel | exposure ratio (median, 56/56) | EUI (CFA) | gap to floor |
|---|---|---|---|
| hotel | **0.325** (most buried) | 178.3 | −0.9 % |
| office | 0.382 | 71.1 | **−28.9 %** |
| retail | **0.467** (most exposed) | 75.4 | −5.7 % |

**Measured order was hotel < office < retail — the opposite of the prediction.** Spearman ρ = −0.171
(n = 168, p = 0.026: wrong sign, not merely null); sign inconsistent across the four building × city
pairs. **The most buried channel is the one closest to its floor.** Parsing validated against
EnergyPlus's own `EnvelopeSummary` to 0.0004 %. **Refuted.**

**Mechanism 2 — accounting basis** (new this session): the PNNL prototype's EUI denominator is a
*whole building* including its core, lifts, lobbies and plant, whereas our office channel books those
to a separate Service/MEP channel (20.64 % / 21.41 % of gross). If office's denominator excludes a
high-intensity core, office EUI would read artificially low.

First, **85.45 was reproduced from the artefact's own columns** before anything was built on it
(rule 4) — the four `Default_NECB` cells give 82.41 / 90.33 / 81.70 / 88.47, median **85.4427**. ✓

Then the counterfactual: prorate Service/MEP **area and energy** onto the four tenant channels by
tenant floor area, per `dr_L3-10`. Worked in full for `Default_NECB__Tall__MTL`: office share
= 25,485.60 / 55,646.47 = 0.457991; rebased area = 25,485.60 + 15,547.66 × 0.457991 = 32,606.44 m²;
rebased EUI = **83.39** vs 88.47 CFA.

**Result: 56 of 56 cells move DOWN, by 1.2-6.8 % (median −3.4 %).** Because Service/MEP's own
intensity (median **59.0** kWh/m²) is *lower* than office's (median **71.1**), folding it in **dilutes**
office EUI. `Default_NECB` office goes 85.44 → ~80.4. **The mechanism runs the wrong way: correcting
the accounting makes the gap larger.** On all three bases computed — CFA, the scorer's own GFA-share,
and this Service/MEP rebase — **0 of 56 cells clear 100. Refuted.**

**🔴 Decision — verdict (c) of the three the task allowed.** Two mechanisms have now been tested and
both refuted. **I therefore cannot claim inapplicability, and I will not.** The task's own test method
is explicit: *"any conclusion that leaves 85.45-vs-100 unexplained is not an answer"*, and the residual
gap **is** unexplained. Converting a FAIL to INFO on an unevidenced appeal to "stackedness" would be
rule 1 evaded by another route — the band would be untouched while the gate quietly stopped
discriminating, which is how a gate becomes vacuous.

**`S9-EUI-office` remains FAIL.** It is published as a **real result**.

**What the work does buy — and it is the part the paper needs.** The failure is present in the
**uninjected `Default_NECB` control** at 85.45, before any occupancy signal exists. Combined with
V2-C3's finding that occupant and plug densities are **blanket office constants** — so correcting them
cannot move office — the failure is **located**: it lives in the envelope / plant / geometry
configuration of the building model, **not in the occupancy model**, which is what this paper claims.
The gate fails; the claim is untouched. That is a defensible thing to write, and it required refuting
two mechanisms to be able to say it.

🔴 Also recorded for the write-up: office's `energy_share_pct` (29.4 %) sits **5.75 pp below** its
`area_share_pct` (35.2 %) in every cell, while residential reads 114-131 kWh/m² with no as-modelled
band at all. The office channel is genuinely light relative to its floor area **within our own tower**,
independent of any external reference. That is a lead for a future leg, not for this one.

**Consequences.** Q1 → answered. The three FAILs stay three. V2-C6 must publish the limitation, not a
band change. V2-D4 must fix the broken `src=` path. §8's risk *"V2-B1 finds no applicable
stacked-channel band"* **materialised as predicted** — but the outcome is a FAIL retained, not the
INFO demotion the register anticipated, because the register assumed a mechanism would survive.

---

### 2026-08-04 (night) — V2-F1 / V2-F3 — Citations owed — **DONE, and three of five claims do not survive**

**1. IEA EBC Annex 66 — REFUTES the claim as stated.** The Annex 66 final report was **opened and
full-text searched** (annex66.org, 5.1 MB PDF, content actually parsed). It is **silent** on any
warning against multiplying a binary any-member-present indicator by household size. It treats
occupant presence and movement broadly and never reaches this aggregation question.
**Annex 79 could NOT be accessed** — two fetch attempts failed on a compressed PDF stream. That is an
access failure, **not** a confirmed silence, and must not be written up as one.
**Consequence:** B-1's literature case rests on **absence of evidence**, exactly the risk V2-F1 was
written to test. The write-up must say that, and must **not** attribute a warning to the Annexes.

**2. Richardson et al. — CONFIRMS the project's suspicion.** The occupancy model is Richardson,
Thomson & Infield, *Energy and Buildings* **40**(8) 1560-1566 (2008) — a **household-level first-order
Markov chain over the active-occupant count** S(t) ∈ {0…N}, ten-minute resolution, separate weekday /
weekend calibration. **Not `any-present × N`.** Full text paywalled, so the citation is at
abstract/methods level, not a page. **V2-C8's edit is justified.**

**3. Andridge & Little (2010) — REFUTES the anchor.** Full text **opened** (PMC open-access mirror,
PMC3130338). The **only** numeric threshold in the paper is in §8.3, describing **their own NHANES III
simulation design**: *"We required a minimum of five respondents in each imputation cell."* **n = 5,
their study choice — not a cited convention.** §3.1 discusses donor reuse and cell collapsing
qualitatively with **no numeric floor**. **There is no n ≥ 10-20 convention in this source.**

**4. US Census CPS "collapse below n = 10" — NOT CONFIRMED.** The official CPS imputation methodology
page states no minimum-n collapse rule. A similar mechanism was found in a *different* survey (RANDS).
Flagged **unverified**, not refuted — primary sources were not exhausted.

**🔴 5. R1's reference list contains incorrect bibliographic metadata — verified by the manager, not
taken on the employee's word**, because it is a serious accusation against a document this project has
been treating as evidence:

> R1 `:128` cites **Rouleau, Gosselin & Blanchet (2019)**, *"Robustness of energy efficiency measures
> in residential buildings under occupant behavior uncertainty"*, *Energy and Buildings* **183**,
> 706-720, DOI `10.1016/j.enbuild.2018.11.042`.
> **CrossRef returns for that DOI:** *"Preparation and performance research of stacked piezoelectric
> energy-harvesting units for pavements"*, **Chaohui Wang**, *Energy and Buildings* **183**, **581-591**.
> Same journal, same volume, **different paper**. Manager-verified via `api.crossref.org`.

The employee reports two further instances — Buttitta & Finn (R1 `:127` gives *E&B* 214, 109869; the
real paper is *E&B* **206**, 109577) and Swan & Beausoleil-Morrison (R1 `:129` gives a DOI that 404s
and vol. 4(1) 43-61; the real record is *JBPS* **6**, 1-23) — **not independently re-verified by the
manager**, and flagged as such.

**Result.** The *classification* R1 reports (0 of 14 study-lines use `any-present × N`) is not
contradicted by anything found. But **R1 cannot be cited as-is**: at least one, probably three, of
fourteen reference rows carry metadata pointing at the wrong paper — and a wrong DOI in the *same
journal and volume* is far more insidious than an obviously broken one, because it survives a casual
check. **Every one of the 14 rows needs its metadata re-verified before use, not just the four marked
"not stated".**

**🔴 Consequence for V2-C9 — it CANNOT close as planned.** The whole point of C9 was to justify
`MIN_POOL = 15` on the adjustment-cell floor convention, **independently of gate W1**, because W1 is
non-monotonic (FAIL@10, PASS@11-20, FAIL@30) and cannot serve as a selection criterion. **That anchor
does not exist in the source R3 cited for it.** Options, in preference order: (a) find a real anchor —
Kalton & Kasprzyk, Cox, or a Census Technical Paper; (b) write it honestly as an **analyst judgement
call**, framed with Andridge & Little's own bias-variance treatment of cell size, and state that no
numeric convention was located; (c) fall back on the multi-seed sweep from V2-E4 as an empirical
justification. **(b) is defensible and (a) is better; neither is what C9 currently assumes.**
**New task V2-F5: re-verify all 14 R1 reference rows.**

---

### 2026-08-04 (night) — V2-D5 — Step-4 run manifest (local half) — **DONE, and V2-E2 is unblocked without the cluster**

**Canonical pool identified, with evidence.** `outputs_step4/sweep/**seed_3_g3fix_raked3_mindwell_actv**/`
— *not* the older `seed_3_raked3_mindwell_actv/`. Four independent confirmations: the 2026-07-21
user decision to accept the g3fix pool wholesale (`3rdJ_04_augmentationGSS_4split.md:40`, W3 gate
7.19 pp FAIL → 0.0030 pp PASS); Step 5's `FULL_POOL` pointer (`3rdJ_05_censusLinkage_4split.md:715`),
which relegates the older directory to "OLD pre-fix pool"; the local CSV's MD5 matching the hash
independently recorded in the Step-5 Progress Log; and the validation report's internal timestamp
(2026-07-21 13:44:13) matching job 1128610 exactly.

**🔴 The result that matters: the validation respondent IDs are recoverable LOCALLY.**
`outputs_step4/step4_val_meta.csv` (9,609 rows, keyed on `occID`, MD5
`beab3467811d7d1297fed448fc077ffe`) is the val-split definition, generated once at the 04A/04C stage
and **shared across all five seeds** — stated verbatim in the sbatch script
(`3rdJ_s4_4split_joint.sh:29`, "shared inputs, not per-seed"). The shipped `augmented_diaries.csv`
carries the same `occID`. **So the row-matched join V2-E2 needs can be done locally, and V2-E2 is no
longer blocked on cluster archaeology.** Caveat recorded: this recovers *which respondents were held
out*, not a per-epoch training-time log.

**Inventory (MD5 + size, all local).** Shipped pool `augmented_diaries.csv` — 418,622,542 B, 192,183
rows, MD5 `47705ce8ee67f01296e96791a9ba008a`. Validation report `.txt` `6aece50e…`, `.html`
`c45c418…`. Config `step4_feature_config.json` MD5 `a34ec1ac…` (splits 44,843 / 9,609 / 9,609).
Split tensors and pair caches all hashed. Pre-fix baseline retained at MD5 `ebb1dfe8…`.
**Scorecard of record: 147 PASS / 18 WARN / 1 FAIL** (sole FAIL = OW5, pre-existing, REG-4-confirmed
as no new regression).

**Three-way honesty split, as the task required.**
- **Recoverable locally:** pool + hashes, reports, validation IDs, config, the full job chain
  (1127956 warmup → 1127957_3 joint → 04E 1128606 → 04L 1128607 → 04M 1128608 → 04T 1128609 →
  validator 1128610).
- **Needs the cluster:** the seed-3 checkpoint `best_model.pt`, and the production
  `step4_training_log_joint.csv`. Only an unrelated smoke-test checkpoint exists locally — **it must
  not be substituted for the shipped one.**
- **Gone for good:** `rake3ch_provenance.json`. No file of that name or equivalent is referenced in
  any doc, Progress Log or job note, cluster or local. **Nothing suggests it was ever written.**
  Recorded as *never persisted*, which is a stronger and more honest entry than "lost".

**🔴 Code-state caveat, recorded rather than smoothed over.** The proxy commit is
`36c82154a7b5beceedb3cd825cd9c4b040fcb589` (2026-07-22 08:12:43) and the working tree of
`3rdJ_04D_train_4split.py` / `04E` shows **zero diff** against it — but the commit **post-dates the
run** (completed 2026-07-21). It is a faithful snapshot, **not a run-time commit hash**, because the
repo was not committed during the run. The manifest says so.

**Consequences.** C-5 → closed as documented. **V2-E2 unblocked, locally.** V2-E1 can now be tied to
the shipped pool by `occID`. The checkpoint hash remains the one manifest field needing a cluster
`ls` + `md5sum` — a single `sbatch`, deferred to the next cluster window.

---

### 2026-08-04 (night) — V2-D3 — Implement the aggregation decision — **DONE, hand-verified**

**What was done.** V2-B5 having decided the mean stands, comments were added at both sites. **No logic
changed.** All four premises re-verified at their cited lines before anything was written (4/4 PASS),
so the comments assert only what was checked.

- `3rdJ_07_aug_to_bem_4split.py:309` — records OD-7A, the `occupants(t) = Number_of_People(=HHSIZE) ×
  schedule(t)` argument, and the Leg-2 lock reference.
- `3rdJ_05_censusLinkage_4split.py:1038` — records that the max-based `HH_hom30_*` is **deliberately
  not** the BEM schedule, and names its real consumer (the Step-5H 0.30 exclusion at `:1211`). **This
  is the comment that stops a future auditor re-raising it as "computed and discarded" — the third
  time this project has paid for its absence.**

**🔴 Test method outcome — hand-computed against the emitted CSV, as required.** Recomputed
`mean(hom30_001..048)` per member group, reshaped 48 → 24 pairwise, rolled +4 h, mirroring `convert()`:

| SIM_HH_ID | HHSIZE | Day_Type | members | max abs diff |
|---|---|---|---|---|
| 42132 | 4 | Weekday | 2 | **0.000000** |
| 42132 | 4 | Weekend | 1 | **0.000000** |
| 42490 | 3 | Weekday | 3 | 0.000333 (3-decimal CSV rounding) |
| 42853 | 3 | Weekday | 3 | 0.000333 (3-decimal CSV rounding) |

Exact to the output format's precision. `py_compile` clean on both files.

**Prose for the master documents** (manager to place at V2-C6; §7 row 10 is satisfied when it lands):

> Residential BEM occupancy schedules are built as the arithmetic mean of `hom30` (fraction of time at
> home) across all household members sharing a `SIM_HH_ID` and `Day_Type`, not the household maximum.
> This is decision OD-7A, locked 2026-06-26: EnergyPlus computes `occupants(t) = Number_of_People ×
> schedule(t)` with `Number_of_People = HHSIZE`, so a mean-of-members schedule yields the expected
> headcount present in each hour — the physically correct driver for internal gains. The max-based
> `HH_hom30_*` computed at Step 5E is retained solely as the binary "household occupied" signal used
> by the Step-5H 0.30 mean-occupancy exclusion filter, and is not read by Step 7.

**Incidental observation, out of scope but recorded:** the raw per-member `HHSIZE` column disagrees
across rows of the same `SIM_HH_ID` (e.g. 3 vs 4). Pre-existing, already handled by the `_hh_canon`
canonicalisation at `3rdJ_07_aug_to_bem_4split.py:316-318`. Unrelated to OD-7A; flagged so it is not
rediscovered as new.

**Consequences.** C-1 → closed as documentation. §7 row 10 pending the doc edit.

---

### 2026-08-04 (night) — V2-F2 — A population-denominated retail reference — **DONE, and it points the other way**

**What was done.** BLS blocks automated traffic (Akamai 403 on every route), so the **BLS-published
PDFs themselves** were retrieved via a Wayback snapshot of the canonical `bls.gov/tus/tables/a3-2024.pdf`
and a FRASER (St. Louis Fed) mirror of the official news release — BLS's own files, not a third
party's transcription. Eurostat was reached directly through its public API. R2 was read only for
table names, never for numbers.

**🔴 Only ONE of the three requested sources supplies what the gate actually needs.** RW6 measures a
**time-of-day** rate (are you shopping during *this hour*), not daily participation (did you shop *at
all today*). Those are different quantities by roughly an order of magnitude.

| source | figure | denominator, exactly as published | kind |
|---|---|---|---|
| **BLS ATUS 2024 Table A-3B** | "Consumer goods purchases" at 12/1/2/3 PM = **3.3 / 3.0 / 3.3 / 2.7 %** | "persons 15 years and over" (civilian noninstitutional); each time point sums to 100 % of that population | **time-of-day** ✓ |
| BLS ATUS 2024 Table 1/2 | 39.9 %/day broad; 35.9 %/day consumer goods | same population, "average day" = 5/7 weekday + 2/7 weekend | daily participation ✗ |
| Eurostat HETUS `tus_00age` AC36 | UK 45.4 % (2000) → 43.8 % (2010); DE 48.8 %; FR 33.6 %; NL 46.6 %; FI 50.8 % | "proportion of individuals **among the whole population** who spent ≥ 10 min/day"; ages ~20-74 | daily participation ✗ |
| ONS / CTUR (UK) | — | — | **no standalone shopping category exists**; folded into "unpaid household work". Checked both bulletins directly. |

**A second scope trap, caught before it was walked into.** BLS's broad *"Purchasing goods and
services"* reads **7.7 %** at noon — which lands neatly inside the old band [0.06, 0.10] and would have
looked like vindication. It is not: that category includes financial, legal, medical, personal-care
and government services, none of which happen in a shop. **Using it would have re-imported the old
gate's error under a new label.** The correct analogue is the narrower *"Consumer goods purchases"*
sub-row — and even that counts purchases *"regardless of the mode or place of purchase… online, via
telephone, at home, or in a store"*, so it remains an **upper bound** on physical in-store presence.

**Arithmetic, over the gate's own 12:00-14:00 window:** (3.3 % + 3.0 %) / 2 = **3.15 %**.

**🔴 The consequence, and it is not the one anyone expected.** RW6-weekday measures **0.0453 = 4.53 %**.

- Against the **old** band [0.06, 0.10] our value is **24.5 % too LOW** — the failure V2-D1 just made
  the gate capable of reporting.
- Against the **BLS time-of-day** reference (~3.15 %, itself an over-count) our value is **~44 %
  too HIGH**.

**The two candidate references disagree in direction, not merely in level.** Correcting the
denominator does not soften the old finding — it *reverses its sign*. That is the strongest possible
demonstration that the original band was mis-specified rather than merely mis-calibrated, and it is
exactly what B-5 alleged.

**Not adopted as a band.** The employee proposed **[0.03, 0.05]**, floored on BLS and widened to 5 %
to absorb the weekday/all-days blend, year-to-year drift and a GSS cross-check. **Rejected as a
PASS/FAIL band**: our 4.53 % sits inside it *only because of that widening*, and a ceiling chosen to
accommodate the number it will judge is rule 1 by another name — however well-intentioned. It is
recorded as **context**, not as a gate.

---

### 2026-08-04 (night) — V2-D6 — Retail gate re-specification — **DECIDED: rate gate → INFO; shape gates → PASS/FAIL**

**Decision on the RATE gate (RW6): demote to INFO, publishing both references and their disagreement.**
Grounds, none of which is "our number missed":
1. Of three requested sources, **only BLS supplies a time-of-day rate at all**. HETUS and UK give
   daily participation, a different quantity. A band claiming three-country corroboration cannot
   honestly be written.
2. BLS's activity scope (**includes online and telephone purchases**) does not match "physically
   present in a retail store". The mismatch is real and its size is unknown.
3. **The two candidate references disagree in direction.** When the available references cannot agree
   whether our value is too high or too low, no defensible PASS/FAIL threshold exists.

The plan's own instruction for V2-D6 anticipated this: *"→ INFO if no valid reference exists."* This
is that case. **The band is not widened; the gate is demoted, and the reason is published.**

> 🔴 **This supersedes the open consequence recorded under V2-D1.** V2-D1 correctly made RW6 capable
> of reporting a failure (class #14, and the gate **was seen failing** on a deliberately broken input —
> that work stands and the `hard=True` fix is kept). V2-D6 now finds the **reference** RW6 was failing
> against to be unusable. Net: **the Step-4 scorecard does not gain a FAIL.** The correct sequence is
> on the record, and it matters that it happened in this order — the gate was fixed first and judged
> second, not demoted to avoid an inconvenient result. Had V2-D6 come first, the same demotion would
> have looked exactly like the thing this project forbids.

**Decision on the SHAPE gates: promote to PASS/FAIL** — peak window, night floor, Saturday, and
Sunday-by-province. Rationale, which is the whole of B-5 and class #11: the injector consumes the
**peak-normalised shape** and *discards the level*. Gating hard on a level the deliverable throws away,
while leaving the quantity it actually uses on a soft gate, is precisely the failure mode this project
catalogued. **Gate what ships.**

**🔴 Test method — OWED, not done.** The shape gates are not fixed until they have been **seen
failing**: shift the retail peak by 3 h on a deliberately broken input and confirm FAIL. Per rule 3
this task does **not** close until that is run. Carried into **V2-E5**.

**Consequences.** B-5 → resolved (rate gate demoted with reason, shape gates promoted). The reference
half of B-5 → closed by V2-F2. **New limitation for V2-G3:** the retail channel is validated on shape,
not level, because no population-denominated in-store presence reference exists at time-of-day
resolution in any of ATUS, HETUS or the UK TUS — a genuine gap in the time-use literature, and worth
saying so in the paper rather than hiding it.

---

### 2026-08-04 (night) — TARGET_K re-derived from the IDF — **the disowned constant replaced with a measured one**

**Why.** The Step-9 log disowned its own sizing target: *"The 49.2 K target is not the model's
setpoint. It was an assumed 140 F rise… `TARGET_K = 49.2` in `3rdJ_09H_resize_elasticity.py:45` is
hereby flagged as mis-specified and must be re-derived from the IDF setpoint before R4 is quoted
anywhere."* **V2-B4 cannot be decided against a number the project has disowned**, so this probe
supplies the replacement.

**First, the constant's actual status.** `TARGET_K = 49.2` is used only at `:193-194` and `:209` to
print a percentage in the R4 diagnostic. **R4's pass condition (`:207`) is merely `mR > mH`** — the
target is never asserted against. So it is informational today; it becomes load-bearing the moment it
is used to *pick K*, which is exactly what V2-B4 does.

**The setpoint — confirmed four independent ways, all agreeing on 60.0 °C (= 140 °F exactly):**
`Sizing:Plant` → `Design Loop Exit Temperature = 60.0000000000001` on both hotel service-water loops;
`SetpointManager:Scheduled` → `Service Water Loop Temp - 140F`; the `Schedule:Year/Week/Day:Interval`
itself, constant 60.0 every hour of every day type; and `WaterHeater:Mixed` →
`Maximum Temperature Limit = 60.0000000000001`. Identical across every campaign cell checked
(`Default_NECB`, `B_central`, `Y2015`, `sens_hotel_opt`, both cities).

> 🔴 **A trap the employee flagged and avoided:** `Sizing:Plant`'s `Loop Design Temperature
> Difference = 5 °C` is the **flow-sizing ΔT** for pumps and pipes, not the DHW heating rise. It sits
> in the same object and is the obvious wrong number to grab.

**The cold inlet — measured, not assumed.** `Site:WaterMainsTemperature` is a **`Correlation`**
object (`Annual Average Outdoor Air Temperature = 6.375`, `Maximum Difference = 33.5`), not a
constant, and its internal constants are Fahrenheit-calibrated, so hand-deriving it invites an error.
The employee instead **ran the object through local EnergyPlus 24.2.0** in an isolated scratchpad IDF
(Montreal TMYx, full year, `Output:Variable Site Mains Water Temperature, Daily`) — no project file
touched, no cluster job. 365 daily values:

| basis | mains °C | design rise (60.0 − mains) |
|---|---|---|
| annual mean | **9.71** | **50.29 K** |
| winter minimum (20 Feb) | **3.10** | **56.90 K** |
| summer maximum (21 Aug) | 16.32 | 43.68 K |

Note the annual mean mains (9.71 °C) is **not** the 6.375 °C input field — the correlation applies its
own offset. Assuming otherwise would have produced 53.6 K, a plausible-looking wrong answer.

**Verdict on the two candidate numbers.**
- **49.2 K** is within ~2 % of the **annual-mean** basis (50.29 K). Its magnitude was roughly right,
  by luck rather than derivation.
- **65.51 K** exceeds even the **coldest-day** rise (56.90 K) that the IDF's own setpoint and mains
  objects imply. **Nothing in the IDF's design objects supports it.** It is a simulated E/V ratio —
  the log's own word is "unconstrained" — and E/V is numerically unstable at low draw volume. It is
  not a nameplate design figure and must not be used as a sizing target.
- **The IDF-supported answer is ~56.9 K** on the winter-worst-case basis, which is the convention DHW
  plant is actually sized against; ~50.3 K on a milder annual-mean basis.

---

### 2026-08-04 (night) — V2-B4 — Naming the deliverable arm — **RECOMMENDED: K = 6, pre-registered, pending one final run**

**Step 1 — the K-sweep as it stands** (`3rdJ_L3_improvements_step9.md:6196-6245`, jobs 1171837 /
1171843; **3-cell `Tall__MTL` subset only** — no other K was ever run at full campaign scale):

| K | installed kW | dT (B_central) | vs the re-derived 56.90 K target |
|---|---|---|---|
| **1** (arm H) | 447.6 | 22.85 | **−60 %** — grossly undersized |
| 3 | 1,342.8 | 36.64 | −36 % |
| **6** | 2,685.6 | **56.27** | **−1.1 %** ✅ |
| **10** (arm R) | 4,476.0 | 65.51 | **+15 %** — oversized past the coldest-day rise |

**Step 2 — the choice, on the physical criterion only.** **K = 6 reproduces the IDF's own winter-basis
design rise to within 1.1 %** (56.27 measured vs 56.90 derived). K = 1 under-serves by 60 %; K = 10
overshoots the coldest-day rise, which is why its elasticity pins at 1.0013 — the plant has stopped
being a constraint at all, and an elasticity of exactly 1 is a saturation artefact, not a validation.

**🔴 This convergence was not engineered.** The 56.90 K target came from the IDF's setpoint and mains
correlation, derived **before** the K-sweep table was consulted. K = 6 was not on anyone's list —
decision 1 had been framed as "H or R", and the third answer already recorded was "neither arm".
**Neither H nor R is the physically correct plant.**

**Step 3 — what this does to the uninjected control, stated in advance.** Any K change moves the
**uninjected `Default_NECB`** cell too, because it is a pure plant effect with **zero occupancy
content** (arm R already demonstrated this: it moved the uninjected control 178.03 → 260.87). K = 6
must therefore be reported as a **plant correction**, never as an occupancy result. Recorded here so
it cannot be presented otherwise later.

**Step 4 — a re-run IS warranted, and only for this reason.** The plan is explicit: *"A re-run for
plant-sizing correctness is legitimate; a re-run to move `S9-EUI-hotel` is not."* K = 6 qualifies on
the first ground. It also honours the standing scope exclusion — this is **not** a ninth arm aimed at
moving a gate; it is the first arm whose plant is sized to the model's own design rise.

**🔴 PRE-REGISTERED PREDICTION, written before the run (rule 2).**
- Hotel EUI at K = 6 will land **between 178.29 (K=1) and 271.40 (K=10)**, and — since dT is close to
  linear in K over 1→6 and saturates after — **nearer the upper part of that range: 235-260
  kWh/m²·yr**, best estimate **~248**.
- Hotel DHW elasticity will fall **between 0.58 (K=1) and 1.00 (K=10)**, predicted **0.85-0.95** — and
  a value at or above 0.99 should be read as **saturation, not success**.
- The **uninjected control** will move by a similar proportion; if it does not, the mechanism is not
  what we think it is.
- **`S9-EUI-hotel` under the current [180, 300] band: PASS.** Under a re-derived NECB-2017 band
  [140, 240] (the likely V2-B2 outcome): **FAIL**. **Both predictions are recorded now, before the
  band is settled, so that neither the K choice nor the band choice can be tuned against the other.**
- Residential all-fuel will move too (+11.3 % was measured at K=10) — **undersizing was never
  hotel-only.**

**Status: BLOCKED on compute.** One 56-cell campaign, `sbatch` only, `-t 7-00:00:00`. The cluster had
120+ higher-priority tasks on 2026-08-04; arm R's aggregation was run locally as a fallback, and that
route remains available with the Python-version caveat (3.13.5 local vs 3.10.20 cluster) recorded.
**This is the last simulation this plan needs.**

**Consequences.** Q4/Q5/Q6 → answered, conditional on the run. `TARGET_K = 49.2` must be corrected to
the derived value in `3rdJ_09H_resize_elasticity.py:45`, with the derivation in a comment — **new task
V2-D8**. V2-G1 stays blocked until the arm exists. **V2-B2 and V2-B4 must be closed together**: the
band decision and the plant decision each move the hotel verdict, and settling either one against the
other's outcome would be fitting.

---

### 2026-08-04 (night) — V2-C8 / V2-D7 / V2-D8 — **three small corrections, all verified in place**

**V2-C8 — Richardson attribution corrected at 6 sites, struck-not-deleted.** Verified present at
`3rdJ_00_4split_Occupancy_Pipeline.md:332` and `:486`, `..._Overview.md:241`, and
`dr_L3-06_retail_diurnal_targets_REPORT.md:55` / `:106` / `:185` (+ a new `:186` entry `16a` for the
2008 companion paper, its DOI explicitly flagged unverified). What Richardson et al. actually do is a
**household-level first-order Markov chain over active-occupant count S(t) ∈ {0…N}** at 10-min
resolution — not the shape-extraction/amplitude-anchoring the docs attributed to them, and **not**
`any-present × N` either. **Every one of the six sites states that the peak-normalisation verdict is
unaffected**: the attribution was wrong, the decision it was cited for was not. Full text paywalled;
verdict rests on abstract + methods, and that limit is written at each site rather than hidden.

**V2-D7 — `21CEN22GSS_occToBEM.py` marked deprecated.** Banner merged into the existing module
docstring (not a second dangling string). Names the successor and its exact rule
(`07_aug_to_bem.py`, `occ48 = …[HOM].mean()`), the live artefact
(`BEM_Schedules_2022.csv`, 2026-07-09), the surviving legacy artefact (`…_CLASSIC_BAK_2026-05-31.csv`),
the defect mechanism (`occDensity` is a per-timestep **sum** over members, `21CEN22GSS_HH_aggregation.py:177-178`),
and the measured 32.55 % person-hour divergence. **No code changed** — deliberately, so the
CLASSIC_BAK output stays reproducible. `py -3 -m py_compile` passes.

**V2-D8 — `TARGET_K = 49.2` → `56.9`**, with the derivation in-comment and 49.2 kept visible as
superseded. Verified at `3rdJ_09H_resize_elasticity.py:71`. **Verified no verdict can move**:
`TARGET_K` occurs exactly 3 times — the declaration and two `print`-only uses (`:220`, `:235`) — and
**R4's pass condition at `:233` is `r4 = mR > mH`**, computed before either print and never
referencing the constant. So the change is real but provably inert on PASS/FAIL, which is the
correct property for a provenance fix: it corrects the record without touching a single scored result.

---

### 2026-08-04 (night) — V2-C9 — MIN_POOL=15 justification — **anchor refuted; first draft's replacement was circular and was corrected**

**The anchor does not exist.** R3 attributed an "n ≥ 10-20 donors" convention to Andridge & Little
(2010). Full text read (PMC3130338): the **only** number the paper gives is **n = 5** at §8.3, and it
is sized to their own NHANES III simulation design, not offered as a portable rule. §3.1's treatment
of donor reuse is qualitative — no floor. Six further sources were attempted
(Kalton & Kasprzyk 1986, Kalton 1983, Cox 1980, Little & Rubin 2002 §4, Census TP-63/TP-66); **four
were paywalled or unreachable**, and that is recorded as such rather than as proof of absence.
**No numeric minimum-cell convention was located anywhere.** Nothing was invented to fill the gap —
which was the hard constraint, and it held.

> 🔴 **MANAGER CORRECTION — the replacement justification was circular, and I rewrote it.** The
> employee's draft placed 15 "near the middle of a practical n=5-to-~20 span", sourcing the **upper**
> bound from *"this pipeline's own `MIN_POOL` sweep (2026-07-21 entries above)"*. **That sweep is the
> sweep-and-pick mechanism that selected 15 in the first place.** Reading a bound off it and then
> calling 15 mid-range re-derives the value from its own selection criterion under a new name. I
> checked the sweep table directly (`3rdJ_05_censusLinkage_4split.md:1009-1016`): at MIN_POOL = 20 the
> AT_WORK per-slot gate still reads **PASS** and the colleague gate reads its **best** value (0.200) —
> the only channel that degrades at 20 is gate 2.2, one gate, non-monotonically — and the relapse at
> 30 is the AT_WORK gate itself. **There is no non-circular upper bound in that evidence.** The hard
> constraint ("must not reference gate W1 at any point") was met in **letter** — the token never
> appears, and the employee verified that — but not in **substance**. Corrected in place at
> `3rdJ_05_censusLinkage_4split.md`, with the withdrawn version quoted so the correction is auditable.

**The honest position, now written:** `MIN_POOL` is bounded **below** by a published (if
design-specific) n = 5 floor and **above by nothing citable**. 15 was arrived at by the sweep, is
disclosed as such, and is defended only as a value comfortably clear of that floor. The sweep is
retained as a **sensitivity check** (15 does not regress the gate) and explicitly **not** as the
selecting criterion. Manuscript text must not imply a range within which 15 was centred.

**Why this matters beyond one constant.** B-2's original charge was that `MIN_POOL` was tuned on a
gate. The defence attempted here — "it's independently justified, and the sweep merely corroborates" —
**failed on inspection**, twice over: the literature anchor evaporated, and the substitute bound came
straight back from the gate sweep. The remaining defensible claim is smaller and is now stated at its
true size. **A shrunk claim that survives is worth more than a large one that doesn't.**

**Method note for the remaining tasks.** A constraint phrased as a forbidden *token* is satisfiable
without being satisfied. Where the real requirement is "do not depend on X", the acceptance check has
to be run against the *reasoning*, not against a `grep`. This is the third time this session that
verifying an employee's claim rather than its wording changed the outcome (cf. the line-number drift
under V2-C10, and the 5-vs-6 hotel row overcount under V2-B2).

---

### 2026-08-04 (night) — V2-G4 — Cross-leg inheritance table — **DONE, and it overturns two recorded claims**

**Rule enforced on the employee:** *"Do not accept any 'reaches' claim you cannot pin to a line of code
in the target leg."* Applied, and it cost two of the audit's own conclusions.

| Finding | 2J code | 2J manuscript | Leg-2 code | Leg-3 code |
|---|---|---|---|---|
| **B-1** `HHSIZE × any-present` | ❌ does not reach | ❌ does not reach | ❌ does not reach | ❌ self-falsified |
| **C-1** max-vs-mean | ✅ reaches — **as architecture, not defect** | ⚠️ reaches, **ambiguously** | ✅ reaches | ✅ reaches |
| **B-13** `occPre × (occDensity+1)` | ❌ superseded code | ❌ no such text | n/a — concept absent | n/a — concept absent |
| **G-4** `HHSIZE × AT_HOME` | ❌ | ❌ | ❌ (refused in comment) | ❌ (refused in comment) |
| **B-5 / class #11** | n/a — no retail channel | n/a | n/a — no retail channel | ✅ native, Step-9 |

**🔴 Overturn 1 — "Leg-2 implements the max" is FALSE.** I verified this myself rather than take it:
`Leg2_2-split/Step7_docs/3rdJ_07_aug_to_bem_2split.py:137` is
`occ48 = df.groupby(keys, sort=True)[HOM].mean()`, and `:130` **names and refuses** the alternative —
*"OD-7A: uses mean(hom30), NOT HH_hom30/max (HH_hom30 is binary '>=1 home' -> overcounts)."* The only
two `HH_hom30` tokens in that file are inside that refusal. Leg-2 *does* compute a max, at
`Step5_docs/3rdJ_05_censusLinkage_2split.py:737`, but its consumers are `:902-903` — the 0.30
plausibility exclusion — never the injected schedule. **The claim conflated Leg-2's Step-5 intermediate
with its Step-7 output.** Corrected in the standing memory note.

**🔴 Overturn 2 — C-1 is not an instance of class #11.** The audit recorded the max as "computed,
never read". It is read: the 0.30 exclusion gate consumes it, and that consumer was located and
confirmed to execute in **all three** codebases (2J `05_census_linkage.py:436` → `:650-654`; Leg-2
`:737` → `:902-903`; Leg-3 `:1038-1039` → `:1211`). **Max for household formation, mean for the
injected schedule is a deliberate two-purpose architecture, replicated three ways.** This independently
reproduces the V2-B5 decision taken earlier today from a different direction — two separate routes to
the same withdrawal is worth more than one.

**What survives, and it is the sharpest item here.** `readySubmission.md:211` (max, formation) and
`:231` (mean, schedule) are each individually accurate. **Neither sentence says the two are computed
independently over different data.** That single unstated link is what let three audits — mine, Codex's
and Gemini's — cross-cite each other's legs and build two high-severity findings on it. The manuscript
is not wrong; it is **under-specified in exactly the place that misleads**. This is the entire
justification for V2-A2's one optional clarifying clause, and it now has evidence behind it rather than
a hunch.

**Honest gaps the employee declared rather than papered over:** (i) whether the class-#11 pattern
recurs elsewhere in 2J's ~15 gates is **UNRESOLVED** — not checked; (ii) the Leg-3 B-5 row is carried
from the 2026-08-03/04 audit, **not re-derived** here.

**Method rule promoted out of this task** (worth more than the table):
1. **Before calling a computed quantity "discarded", grep the whole downstream tree for its exact
   column name.** A `.max()` next to a `.mean()` is not evidence of an oversight — check for a
   *different* consumer (a gate, a plot, a QA report) before invoking "vacuous" or class #11. One grep
   settled C-1 in a minute, **in the opposite direction from what was recorded.**
2. **Before writing "reaches the submitted paper", check three things in order:** (a) does the code
   literally implement the claimed formula at the cited line; (b) is that code's *output* the one the
   manuscript's numbers came from, not merely a plausible candidate; (c) if two converters exist, order
   them against the manuscript's finalisation date using mtimes, backup suffixes, deprecation banners.
   **B-13 passed (a) and failed (b) and (c)** — a prose match was mistaken for a code match. That trap
   is the reason this task existed, and it caught it.

---

### 2026-08-04 (evening) — V2-A2 / V2-F4 / V2-F5 / V2-B1 + the local-run port — **one vindication, one collapse, and a cross-cutting basis defect**

**V2-A2 — DONE, and the finding was sharper than the task assumed.** The task was written as "both statistics
are stated, their independence is not". On reading the text that is **not** what is there. §3.3
(`readySubmission.md:211`, `2J_full_manuscript.md:326`) states the **max** explicitly and names its purpose.
§3.5 (`:231` / `:346`) says only *"occupancy (AT_HOME fraction)"* and **never states how that fraction is
computed across household members at all** — the sole "averaged" in that paragraph is temporal (48 half-hour
slots → 24 hourly). So the reader meets an explicit max, then an unexplained "fraction", and the natural
inference is that the second derives from the first. That is precisely the inference three audits made.
A third statistic hides in the same sentence: *"mean at-home fraction falls below 0.30"* is a mean over
**time slots** of the already-maxed indicator. Clause inserted in §3.5 of both manuscripts (once each,
verified); the rule was confirmed against the shipped converter first
(`07_aug_to_bem.py:97`, `groupby(...)[HOM].mean()`, comment `(G,48) fraction home`).
`2ndJournal_Occ_summary.docx` needs **no** edit — it is a lay summary and contains neither statistic.
An `§4.2` restatement of the four channels exists in both files and was deliberately left alone: once §3.5
defines the statistic, §4.2's shorthand is unambiguous.

**V2-F5 — the R1 reference list is not salvageable.** 15 entries, every DOI resolved live through CrossRef:
**2 VERIFIED / 9 WRONG-DOI / 2 METADATA-MISMATCH / 2 UNVERIFIABLE.** The wrong DOIs land on microalgae
biodiesel, piezoelectric pavements, tabique-wall coatings, liquid-desiccant air conditioning — right journal,
often a DOI one character off the real one, which is exactly why they survive casual checking. Two entries
(McKenna, Swan & Beausoleil-Morrison) match **no real paper found after genuine search**. The Rouleau defect
was reproduced independently. Correct DOIs were established for 7 of the 9. **Consequence: nothing sourced to
R1 may be cited until re-derived** — including its "zero studies use any-present × N" headline. A replacement
deep-research report was commissioned rather than a patch.

> 🔴 **MANAGER CORRECTION — V2-F4's employee made a false negative, and it reverses the finding.** The report
> stated that `DOE_non-residential_simulation_results_canadian.csv` *"does not exist in the repo (searched,
> zero matches)"*. **It exists**, at `BEM_Setup/Reference-Validation/`, and I opened it. It is a 90.1-2004
> DOE-prototype table in kWh/m²·yr **cross-tabulated by climate zone**, with columns
> `Minneapolis - Montreal (6A)` and `Duluth - Calgary (7)`. **Large Hotel CZ7 = 302.2** — exactly the figure
> `dr_L3-03:59` cites and exactly where the band's 300 ceiling came from. CZ6A = 286.4, also matching.
> **So the hotel ceiling is correctly sourced, at the right climate zone, and G-2's headline needs
> re-statement.** The agent searched the wrong scope and read absence-of-file as absence-of-source.

**What survives from V2-F4, and it is still serious.** The *justification prose* around that correct number is
rotten: Table 5 claims the ceiling is anchored on "ASHRAE 90.1-2016/2019" prototypes when the number it uses is
the **90.1-2004** row; `PNNL-28543` is **not** the 90.1-2019 savings analysis but *"PNNL's Intermediate
Characterization Summary for the MP-1 Experiment"*, a nuclear-materials report; `PNNL-26343` does not resolve
at all; the CanmetENERGY 2020 archetype study **could not be located** and its URL 404s. Table 2's
441–521 kWh/m² "modern code" rows are unsourced **and directionally impossible** — a stricter code lowers EUI,
and the correctly-identified PNNL 90.1-2019 report gives Large Hotel **239.1** national, below the 2004 figure
as expected. **The contradiction G-2 found is real, but it is the modern-code rows that are wrong, not the
ceiling.**

**V2-B1 — the office deficit is LOCATED, and it is not occupancy.** Per-end-use pull from
`Step8_docs/outputs_step8/agg/agg_annual.csv` (`scenario=Default_NECB`, `channel=office`), re-derived
independently by me: **heating is ~17 % of office site energy against a reference share of 35–45 %**;
fans 7 % against 12–18 %. Equipment and lighting are **already** at reference-typical absolute levels, which is
consistent with V2-C3 (they are the blanket *office* constants) and means correcting them cannot move this gate.
Cross-checked outside the project's own aggregation code against raw `eplustbl.htm` End Uses. The same
low-heating signature appears in **all four channels**, locating the mechanism in the shared building model.
A secondary opposite-direction anomaly is recorded and **not** used to explain the gap: office DHW reads
~14 % of total against a 2–4 % reference share.

**🔴 NEW CROSS-CUTTING FINDING — the bands and the building are different code vintages.** The reference CSV
underpinning the office *and* hotel bands is the **ASHRAE 90.1-2004** baseline set. The building being judged is
`TallBuilding_90.1-2019_..._NECB17_...v242.idf` — **90.1-2019 / NECB 2017**. The band document itself states
the trajectory at line 22: *"EUI values drop consistently across Standard 90.1 cycles (2004 → 2013 → 2016 →
2019)"*. Judging a 2019-code model against a 2004-derived floor is a basis mismatch of the same family as the
CFA/GFA and all-fuel/electricity-only mismatches this project already screens for.

**And the office band's own document contradicts its own gate, three ways.** Verified verbatim by me in
`Leg2_2-split/Step8_docs/deepResearch/Office Reference EUI … As-Modelled Bands.md`:
`Table 7.1 (:150-155)` floor **100.0** · line 21 *"NECB 2017/2020-compliant large offices average **80 to
140**"* · `Table 2.1 (:63-72)` *"Reference / Tier 1 Baseline, Fossil-Fuel Heated: **85.0 to 115.0**"*. Our
uninjected control is **85.44** and our tower **is** gas-fired (`Boiler:HotWater`, NaturalGas, η = 0.813) — so it
sits inside the two statements the gate does not use, and below the one it does.

> **NO BAND HAS BEEN CHANGED, AND NONE WILL BE ON THIS EVIDENCE.** Both dissenting statements trace to a
> CanmetENERGY study that **nobody has yet located** — the identical hole that blocks the hotel band. Moving a
> floor from 100 to 85 on an unlocatable source, in the exact direction that rescues a failing gate, is the
> project's most-repeated error class wearing a new hat. Two deep-research tasks were commissioned to settle it
> from primary sources, and both were instructed that "the evidence is insufficient" is an acceptable verdict.

**Infrastructure — the resize runner now runs off-cluster (V2-B4/V2-E3).** `EPLUS_EXE` added to
`3rdJ_09H_resize_campaign_cell.py`, **default-off**: unset, the singularity branch is byte-identical to the one
arms H and R ran, so every earlier cell reproduces unchanged. Set-but-missing **REFUSES** rather than falling
back — a silent fallback is the job-1171812 defect shape and was not reintroduced. Smoke-tested on
`B_central__Tall__MTL` at K=1: EnergyPlus exit 0, fuel closure 0.0000 % both fuels, channel closure 0.0000 %
all three, hotel volume reconciled to the driver at 0.00000 %.

**Why the local campaign runs BOTH arms.** Arm H's cells are stamped `PLATFORM: linux`; anything simulated on
this box is `win32`. `3rdJ_08P_probe_gates.py:202` **FAILs** a cross-platform comparison by design
(added 2026-07-28: *"same EnergyPlus build does NOT guarantee bit-identical output across compilers/libm/
rounding"*). Differencing a local K=6 against the cluster arm H would trip that gate, correctly. So the local
campaign re-runs arm H at **K=1 (identity resize)** and then **K=6**, 112 cells, both win32 — the difference is
purely K and the guard passes honestly instead of being routed around. Absolute EUIs may differ slightly from
the cluster arm H; V2-B4 measures the *difference*, which stays internal to the local pair. Arm H's 56
`injected.idf` + `manifest.json` + `provenance.txt` were fetched from Speed by `scp` only — no queue, no compute.

**Method rules promoted out of this wave:**
1. **"File not found" from an employee is a claim, not a result.** Re-run the search yourself at repo root
   before accepting it. One wrong-scope search nearly retired a correctly-sourced band ceiling.
2. **When a reference band and the model disagree, check their code vintages before checking anything else.**
   It is cheaper than every mechanism test, and here it was missed through two full refutation cycles.
3. **A source document can contradict itself.** Cite the table the gate actually reads, then read the *rest of
   the document* looking for statements that disagree with it — Table 2.1 and line 21 sat unread beside
   Table 7.1 for the whole life of this gate.

---

### 2026-08-04 (night) — external deep-research round 1 — **3 of 4 reports rejected; the rejection is the finding**

**Process change, recorded because it is permanent.** Deep research is now done **externally** by the
user in Gemini Antigravity. The assistant authors the prompt documents and verifies what comes back;
it does not run the search. Written into `CLAUDE.md` ("Deep research is EXTERNAL") and `README.md`.
Prompts and results live together in `deepResearch_Resources/`: `00_MASTER_BRIEF_V2.md` ·
`_RESPONSE_TEMPLATE.md` (Sections A-H) · `V<NN>_<topic>.md` → `RV<NN>_<topic>.md`.

**Four prompts issued (`V01` prototype matrix, `V02` NECB office, `V03` occupancy aggregation,
`V04` hotel band). Four reports returned. `RV01`, `RV02` and `RV04` are REJECTED for band purposes.**

> 🔴 **They fabricated our own model's outputs.** `RV01` Section F states our office EUI as 85.4 (MTL)
> and **88.2 (CLG)**, hotel **182.1 / 194.5**; `RV02` states 85.4 / **85.5**. Re-derived from
> `agg_annual.csv` + `agg_meta.csv`, the actual `Default_NECB` values are **office MTL 90.33 / 88.47,
> CLG 82.41 / 81.70; hotel MTL 160.65 / 206.79, CLG 149.36 / 195.41**. The only figure supplied to them
> was 85.4, the four-cell **median**, which the master brief quoted. Everything else was invented, the
> two reports disagree with each other, and **both invert the city relationship** — they put Calgary
> above Montreal for office, where ours is 8 kWh/m2 below. A fabricated number that reproduces the
> supplied one and invents the rest is the hardest kind to catch by reading alone.

**They contradict each other on the load-bearing citation.** 90.1-2019 savings analysis:
`RV01` = `PNNL-31488` (DOE/EE-2364, Salcido et al. 2021); `RV02`/`RV04` = `PNNL-29780`. 90.1-2016:
`RV01` = `DOE/EE-1614` (Athalye et al. 2017); `RV02`/`RV04` = `PNNL-26348` — **one digit from
`PNNL-26343`, already established as non-resolving**. `PNNL-28543` came back with **two different
titles** from the same tool (*Charpy V-Notch Impact Testing of High-Burnup Spent Fuel Cladding* vs
*PNNL's Intermediate Characterization Summary for the MP-1 Experiment*). The reports commissioned to
repair our citation rot reproduced it.

**They contradict each other on whether the data exists.** `RV01` §G: per-climate-zone matrices are
**not** printed in the narrative determination reports and must come from scorecard workbooks.
`RV02`/`RV04` then quote precise per-zone values (41.2 / 43.2 / 74.2 / 78.3 kBtu/ft2.yr) sourced to
those same narrative reports, every one carrying the **same landing-page URL**
(`energycodes.gov/prototype-building-models`) and every one marked "Read full text".

**Every band recommendation moved in the rescuing direction.** `RV02` proposes the office floor
100 → **75** (our 85.4 passes); `RV01` proposes **80-90** (passes). `RV02`'s row B12 is openly
circular: *"85.4 kWh/m2.yr total * 17% heating share = 14.5"* — **our own output, tabled as a Tier 1
external finding with confidence H.** This is the class the prompts explicitly forbade, and it appeared
anyway in 3 of 4 reports.

**A miss none of them caught: `S9-EUI-hotel` fails on its FLOOR, not its ceiling.** `BENCH["hotel"]` is
`lo=180.0, hi=300.0`; our control cells are **149.36** and **160.65**, both under the floor. `RV01`
spent its hotel recommendation lowering the *ceiling* to 220-240, which cannot move a single failing
cell. The gate's failing end was never diagnosed because the prompt led with the ceiling defect (G-2)
and every report followed the prompt's framing instead of the gate's arithmetic.

**🔴 NO BAND WAS CHANGED.**

**What survives, and it is real:**
* **`RV03` is sound on bibliography.** Its DOI corrections **independently reproduce** the earlier
  blind pass on Aerts (`.014` → `.021`), Rouleau (→ *Energy* 188, 115978), Flett & Kelly
  (→ `10.1016/j.enbuild.2016.05.015`), Fischer (→ `...2016.04.069`) and Buttitta (→ `...2019.109577`).
  Two independent passes agreeing on five corrections is worth more than either alone. Its
  "Full text read" claim on 17 paywalled Elsevier papers is **not** credible and is not relied on.
* **Two clean negatives, both asked for as negatives and both delivered honestly:** the CanmetENERGY
  archetype study is `NOT FOUND` with search terms recorded, and the 441-521 kWh/m2 "modern code"
  hotel figures are `NOT FOUND` in any literature. That second one closes the V2-F4 question: those
  rows are unsourced, and the 300 ceiling they were said to contradict is the better-founded number.
* **The 90.1-2004 provenance is confirmed.** Deru et al. (2011), NREL/TP-5500-46861 / PNNL-19590; the
  kBtu → kWh conversions reproduce our local CSV cells to three decimals.

**`V05` issued** — retrieval only, no analysis, no recommendations. It requires a **direct resolving
file URL per number** (landing pages are refused, the row must read `NOT RETRIEVED`), forbids quoting
our model's outputs at all, forbids deriving a zone value by applying a national percentage, and asks
for a report-number-to-real-title table because we now hold three inconsistent versions of it.
`V05` supersedes `V01` for the prototype matrix.

**Method rules promoted out of this round:**
1. **Check a report's claims about *our* numbers before checking its claims about the literature.**
   The external tool cannot see our results; anything it states about them is either quoted from the
   prompt or invented. Here that test took one script and invalidated three reports in one pass.
2. **A report that agrees with a number you supplied has told you nothing.** 85.4 came back correct in
   both reports because both were given it. The diagnostic value was entirely in the figures we did
   *not* supply.
3. **When a prompt names a defect, expect the answer to inherit the prompt's framing.** All four
   reports argued about the hotel *ceiling* because the prompt led with the ceiling defect, while the
   gate has been failing on its floor the whole time. Next time, state the gate's arithmetic and let
   the report find the failing end.

---

### 2026-08-04 (night) — V2-D4 (provenance half) — **the office band cited a path that resolves to nothing; fixed, and the fix is falsified**

**Status: PARTIAL — DONE for provenance, still BLOCKED for values.** V2-D4 has two halves. The band
*values* wait on WP-B and **nothing below changes a single number** (verified: office 100/135/200,
retail 80/110/155, hotel 180/240/300, all identical before and after). The *provenance* half needed
nothing from WP-B and is now closed.

**The defect.** `3rdJ_09_activityDrivenLoads_4split.py` `BENCH["office"]` carried

> `src="NECB2020/90.1-2019 DOE-PNNL as-modelled band (Step8_docs/deepResearch/...As-Modelled Bands.md ; repris de Leg-2)"`

`Leg3_4-split/Step8_docs/deepResearch/` **does not exist.** The document is in the frozen Leg-2 tree,
at `Leg2_2-split/Step8_docs/deepResearch/Office Reference EUI (NECB 2020, ASHRAE 90.1, DOE-PNNL
prototypes) — As-Modelled Bands.md`. The string was not a broken path so much as a path-*shaped*
fragment: no root, an elided middle (`...`), and a trailing parenthetical. It reads as provenance and
carries none. **This is the `src=` for the floor of `S9-EUI-office`, one of the three gates that has
blocked this leg through eight campaigns** — the number nobody could defend was the one under audit.

Retail and hotel were less bad but not good: `dr_L3-02` / `dr_L3-03` are document *stems*, correct but
requiring a `find` to resolve. Both now carry their full path
(`Leg3_4-split/deepResearch/dr_L3-0N_..._REPORT.md`, both confirmed present).

**One trap worth recording.** The Leg-2 filename contains a real em dash (U+2014, verified by
`cat -A`: `M-bM-^@M-^T`). Writing it as `--` to satisfy the house no-dash rule breaks the path — which
is exactly what I did on the first pass, and the checker below caught it. A comment now sits above
that line saying the dash is the file's own byte and must not be normalised. **The house style rule
governs prose; a path is data.**

**A header warning added above `BENCH`**, so the next reader meets the caveat before the numbers:
the office source document contradicts itself three ways on its own floor (Table 7.1 = `100.0`,
line 21 = *"80 to 140"*, Table 2.1 = *"85.0 to 115.0"*), and the DOE-PNNL tables behind it are the
ASHRAE **90.1-2004** baseline set while the building being scored is **90.1-2019 / NECB 2017**. That
vintage mismatch is out with `V05`. Values stay frozen until WP-B.

**New check: `3rdJ_09_bench_provenance_check.py`.** Reads `BENCH` by AST (no import, no side effects,
no scorer dependencies — the entries are `dict(...)` calls so `literal_eval` will not do), asserts
every band that *has* a value names a document that resolves, and prints the values for eye-diff.

**🔴 Seen failing, three ways** (fixture: a repo copy under the scratchpad, so the real tree is never
mutated):

| # | Perturbation | Result | Exit |
|---|---|---|---|
| **F0** | control, unmodified | `PASS` | 0 |
| **F1** | hotel path → `..._REPORT_NOPE.md` | `hotel BROKEN` | **1** |
| **F2** | office `src=` **restored to its literal pre-D4 text** | `office NO PATH IN src=` | **1** |

**F2 is the one that matters.** It is not a synthetic break: it is the string that was shipped, and it
fails. That is the difference between asserting a bug existed and demonstrating it. F1 and F2 also
fail *differently* — F1 is a path that resolves nowhere, F2 is a string with no path in it at all —
so the check discriminates the two failure modes rather than collapsing them.

**🔴 What this check does NOT do, written into its own docstring so it cannot be miscited later.**
It cannot fail on a band whose *value* is wrong. A green run here is not band validation, and if it
is ever quoted as such it becomes the "explanation that cannot fail" class. The docstring says so in
the file itself, not only here.

**Residential** is handled explicitly rather than skipped: it has `lo=None, hi=None`, so "no path" is
the correct state and is reported as `no band, no path required`. A checker that silently skipped it
would pass a channel that had lost its band entirely.

**Left open in V2-D4:** the value sync (`BENCH["hotel"]` is `[180, 300]`; decision #3 put the gate on
`[240, 300]`), and V2-B3's median-in-band rule. Both need WP-B. Q7 is **half** closed: the scorer's
bands now say where they came from; whether they equal the master docs' bands is the other half and
is still open.

---

---

### 2026-08-04 (night) — V2-B4 / V2-E3 — the K = 1 vs K = 6 campaign, run LOCALLY — **112/112 cells, and the pre-registered prediction FAILS on its two load-bearing items**

**Campaign.** 56 cells at K = 1 (identity resize) + 56 at K = 6, both on win32, both aggregated by
`3rdJ_08E_aggregate_4split.py`. 112/112 EnergyPlus completions, 560/560 closure checks at residual
`0.0000 %`, attribution residual `0.000000 %` on every cell in both arms. Speed was unavailable
(120+ higher-priority tasks), so **both** arms were re-run here rather than differencing a local K = 6
against the cluster's arm H — the PLATFORM guard (`3rdJ_08P_probe_gates.py:202`) would have refused
that comparison, correctly. The difference between these two arms is K and nothing else.

**Port validated against arm H on a number that was not tuned.** Within-group hotel DHW elasticity at
K = 1 measures **0.5823 / 0.6424 / 0.6464 / 0.5774** across the four (building, city) groups — the
cluster's arm H recorded **0.58-0.65**. Reproduced on a different OS and a different Python (3.13.5
vs 3.10.20) without being aimed at.

---

#### 🔴 PREDICTION vs OUTCOME (the pre-registered table at §V2-B4, written before the run)

| # | Pre-registered | Measured | |
|---|---|---|---|
| 1 | Hotel EUI at K = 6 in **235-260**, best est. ~248 | median **257.04** | **PASS** |
| 2 | Elasticity **0.85-0.95**, bounded by [0.58, 1.00] | **0.3344** | **🔴 FAIL — outside the bounding interval, wrong direction** |
| 3 | Uninjected control moves by a similar proportion | controls **+31.1 to +50.2 %**, arm median **+40.9 %** | **PASS** |
| 4 | `S9-EUI-hotel` on **[180, 300]: PASS** | **FAIL — 21/56 above the ceiling** | **🔴 FAIL** |
| 5 | `S9-EUI-hotel` on a re-derived [140, 240]: FAIL | FAIL, 28/56 above | **PASS** |
| 6 | Residential moves too (+11.3 % at K = 10) | **+4.11 %** | **PASS** |

**Two misses, and they are the two the decision rested on.** This is what pre-registration is for.

**Miss 4 — the gate did not pass; its failing END inverted.** At K = 1: 28/56 in band, **28 below the
floor**, 0 above. At K = 6: 35/56 in band, **0 below, 21 above**. The in-band count *improved*, 28 → 35.
Read on the count alone this is progress; the gate FAILs in both arms, for opposite reasons. This is
the catalogue's class **#12** (stable count, membership turnover) in a sharper form — here the count
moves in the reassuring direction while the failure mode flips end to end.

**All 21 ceiling failures are `Tall`. Zero `SuperTall`.** Four of the 21 are `Default_NECB` or `Y20xx`
cells — uninjected or era cells with no occupancy content in them at all. The K = 6 hotel gate fails
on a **building-geometry axis**, not an occupancy axis.

---

#### 🔴 THE MECHANISM, LOCATED TO ONE OBJECT — and it overturns why K = 6 was chosen

Identity: `E = V · ρc · dT`, so **elasticity = 1 + d log dT / d log V**. An elasticity below 1 is
*only* a statement that achieved temperature rise degrades as draw rises. Split per heater type,
median over the four groups:

| type | design | median V (m³) | dT K=1 | dT K=6 | slope K=1 | slope K=6 |
|---|---|---|---|---|---|---|
| **LAUNDRY** | 180 F | **18,853** | **11.58** | **61.49** | **−0.981** | **−0.965** |
| 2.56GPM140F | 140 F | 1,579 | 39.80 | 49.23 | −0.707 | **0.000** |
| BOOSTER | 180 F | 1,059 | 71.36 | 71.34 | 0.000 | 0.000 |
| *the other 13* | 140 F | 29-2,201 | ~49.1 | ~49.2 | 0.000 to −0.083 | **0.000** |

**At K = 6 every heater except LAUNDRY has slope exactly 0.000 — perfect tracking, elasticity 1.0.**
They were already fine at K = 1 and are now simply oversized 6×.

**LAUNDRY has slope ≈ −0.98 in BOTH arms.** `dT ∝ V^−0.98` means `E ∝ V^0.02`: **its delivered energy
is constant no matter how much hot water is drawn.** It is capacity-pinned at K = 1 *and still
capacity-pinned at K = 6* — just pinned at a higher value (0.91e12 → 4.85e12 J, **+431 %**, while all
other heaters together moved **+3.9 %**).

**So the whole-hotel elasticity is a share-weighted mix of one dead channel and fifteen live ones, and
K = 6 changed the shares, not the physics.** LAUNDRY's share of hotel DHW energy went **26.7 % → 65.4 %**.
Share-weighting reproduces the measurement: `(1−0.654)×1.0 + 0.654×0.02 ≈ 0.36` against **0.3344**
measured. **The K = 6 resize made the hotel channel LESS occupancy-sensitive — the occupancy-insensitive
share of its DHW rose from 27 % to 65 %.** That is the opposite of the purpose the arm was authorised for.

**A first explanation was tried and REFUTED, and is recorded because the refutation is the evidence.**
The obvious reading — *"uncapping LAUNDRY adds a large non-occupancy load that dilutes the responsive
fraction"* — requires LAUNDRY's draw to be occupancy-flat. It is not: LAUNDRY's annual draw varies
across scenarios by **exactly** the same 16.67 % / 20.31 % as every other heater in the same group
(`test_laundry_occ.py`). Its *draw* is fully occupancy-driven; its *delivered energy* is not, because
the burner clips. Structure right, premise wrong — and the premise was testable in one script.

**🔴 Consequence for V2-B4: the K-sweep selected K = 6 on a statistic LAUNDRY dominates.** The
criterion was the volume-weighted aggregate dT hitting the re-derived 56.90 K target — and the
volume weights are 61-69 % LAUNDRY. So the sweep sized **the whole plant** by the factor that fixes
**one broken object**, oversizing fifteen correctly-sized heaters 6× as a side effect. At full
56-cell scale the aggregate lands at **57.97 K, +1.9 % over target** (the 3-cell `Tall__MTL` subset
that the decision was taken on gave 56.27, −1.1 %; sign flipped, magnitude comparable).

**The internal reference that settles it is already in the IDF.** `BOOSTER` carries the same 180 F
design target as LAUNDRY, is never clipped (dT 71.36 / 71.34, slope 0.000 in both arms), and so
measures the full rise a 180 F object achieves when correctly sized: **71.34 K**. LAUNDRY reaches
61.49 K at K = 6, i.e. **86 % of the way** — it needs roughly `6 × 71.34/61.49 ≈ K ≈ 7`, **for itself
alone**, with every other heater left at K = 1. This reference comes from a *different object in the
same model*, not from the arm under audit and not from an external band, so it can fail.

**Recommendation, and it is not on the K = 1 / K = 6 / K = 10 menu.** A **per-object** sizing —
LAUNDRY (and marginally `2.56GPM140F`) raised to their own design rise, everything else untouched —
is the physically correct plant. A global K cannot be right: it is one number for sixteen objects of
which fifteen were already correct. **This is a decision for the user, not a further arm to run.**
No band has been changed and no gate has been re-scored to make anything pass.

---

#### Retail, in passing — a gate decided at 0.15 %

The four lowest retail cells are the same four in both arms and sit at **79.83 / 79.96 / 80.68 / 81.04**
against a floor of 80.0. The DHW resize moved retail's median by **−0.05 %** and that was enough to
push a second cell under (`sens_retail_cons__SuperTall__CLG`, 80.029 → 79.960), taking the all-56 count
from 55/56 to 54/56. **A retail occupancy gate whose verdict flips on a hot-water burner capacity
change of 0.09 kWh/m² is not measuring retail occupancy.** Consistent with the already-recorded
0.06 / 0.23 % misses; V2-D6's demotion of the retail *rate* gate to INFO is reinforced, not weakened.

#### Office — unmoved, as expected, and worth stating

`81.64 → 81.52` (−0.14 %). **0/56 in band in both arms; all 56 below the floor of 100**, including the
uninjected `Default_NECB` control at 82.41 / 90.33. Nothing about DHW plant sizing touches it. This is
the fourth independent confirmation of §0.21: **office is not an occupancy problem**, and no arm will
make it one.

---

#### Artefacts

`_local_K16/{K1,K6}/` (56 cells each) and `_local_K16/agg_{K1,K6}/` (5 tables each). Scoring scripts
in the session scratchpad: `score_k1_k6.py`, `score_elasticity.py`, `test_laundry_occ.py`,
`decompose_elasticity.py`. **Python 3.13.5 local, not the cluster's 3.10.20** — same caveat arm R's
aggregation carries.

---

### 2026-08-04 (night) — **PROVENANCE DEFECT found by the port: the resized manifests carry arm H's execution stamp**

**All 112 local manifests claimed `PLATFORM: linux`,
`energyplus_exe_used: /speed-scratch/o_iseri/ep_wrappers/energyplus`,
`timestamp_utc: 2026-08-03T16:59:42` and a `/speed-scratch/...` outdir.** They ran here, on win32,
against `C:/EnergyPlusV24-2-0/energyplus.exe`, on 2026-08-04.

`3rdJ_09H_resize_campaign_cell.py` inherits arm H's manifest wholesale and stamps only the resize
fields (`RESIZE_K`, `PLANT_KW_*`). Its docstring states the intent: *"THE MANIFEST is inherited from
arm H and then stamped, never invented."* That is exactly right for `INJ_HASH` / `INPUTS_HASH` — the
injection genuinely did not change. It is wrong for everything describing the **execution**, because
this script re-runs EnergyPlus.

**🔴 Why eight arms did not catch it.** On Speed the inherited value was `linux` and the true value
was `linux`. The field was **accidentally correct**, so nothing could distinguish a measured stamp
from a copied one. The PLATFORM comparability guard reads this field to refuse cross-platform
diffs — meaning it was reading a value **inherited from the arm it audits**, and could not fail.
The catalogue class is *"the gate whose reference comes from the same source it audits"*. **Running
the identical code on a second OS is what made a copied stamp visibly wrong** — which is a general
lesson: a provenance field can only be tested by changing the thing it claims to record.

**Note the near-miss:** `energyplus_build` is `94a887817b` on **both** platforms — same upstream build,
different OS binary. So the build hash could not have caught this either. `PLATFORM` was the only
field that could, and it was the copied one.

**Fixed in `3rdJ_09H_resize_campaign_cell.py`** — `PLATFORM`, `engine`, `energyplus_exe_used`,
version/build (re-measured by asking the executable that actually ran), `timestamp_utc`, `outdir` and
`ep_return_code` are now stamped from the run. Arm H's values are preserved verbatim under `ARMH_*`
rather than discarded, so the inheritance stays auditable. Version re-measurement is non-fatal but
**never silently leaves arm H's build hash in place** — the fields are only overwritten when the
executable actually answers.

**The 112 existing manifests corrected post hoc** by `fix_local_manifest_provenance.py` (backups at
`manifest.json.preprov.bak`, 112/112 written). It asserts only what is provable — the platform, the
executable from `$EPLUS_EXE` with the file checked to exist, the version measured from that binary,
the real outdir — and **derives `timestamp_utc` from the manifest's own mtime while saying so in a
separate `timestamp_utc_source` key**, rather than inventing a plausible run time. Both arms were
re-aggregated afterwards so `agg_meta.csv` carries `win32`.

**Cells written before 2026-08-04 in every earlier arm still carry arm H's execution stamp** and must
not be read as evidence of the platform they ran on. Recorded in the manifests themselves via
`RESIZE_PROVENANCE_NOTE`, not only here.

---

### 2026-08-05 — `RV05` returned — **REJECTED as a band source. Section B does not survive three arithmetic checks it cannot pass.**

**What was done.** `RV05_prototype_scorecard_retrieval.md` (351 lines, 60 Section-B rows) landed. Per
the method rule promoted out of the previous round — *check a report's claims about our own numbers
before checking its claims about the literature* — it was falsified locally before any value was
read into the plan. Checker: `improvements/v2/rv05_consistency_check.py`, five checks, no network,
local CSV plus arithmetic only.

**Verdict: the retrieval route (Section G item 1) is the only usable output. Section B is not.**

**Check 1 — the 90.1-2004 anchor rows are our own file, wearing the wrong cities.** All **12 of 12**
values RV05 attributes to *Deru et al. (2011) Table 5-2* equal
`BEM_Setup/Reference-Validation/DOE_non-residential_simulation_results_canadian.csv` rounded to 2 dp
(172.556073 → 172.56, 302.209722 → 302.21, and ten more). That alone is not proof of circularity —
our CSV may itself be Deru — but the labels are: **our CSV's columns are `Minneapolis - Montreal (6A)`
and `Duluth - Calgary (7)`, which are Deru's reference-building cities; RV05 tables those same twelve
values as `(6A Rochester)` and `(7 International Falls)`**, which are the *prototype* lineage's cities
from its own 2013-2019 block. A reader who had opened Table 5-2 would have copied the city header
with the number. **Item 5 asked for independent confirmation of the anchor and did not deliver one**;
it re-reports what the previous round already established, with a new error attached.

**Check 2 — the end-use tables do not sum to the totals they are printed against.** An EnergyPlus
`End Uses` table sums to Total Site Energy by construction. Twelve blocks were given; **not one sums
to 100 %**, and the shortfall is different every time:

| prototype | CZ 6A coverage | CZ 7 coverage |
|---|---|---|
| Large Office | **6.27 %** | **6.25 %** |
| Large Hotel | 16.88 % | 16.30 % |
| Small Hotel | 51.28 % | 50.82 % |
| Medium Office | 52.79 % | 57.69 % |
| Stand-Alone Retail | 85.01 % | 90.54 % |
| Strip Mall | 97.01 % | 94.17 % |

There is no fuel-scope or reporting convention that produces 6 % for Large Office and 97 % for Strip
Mall. The blocks are **internally** consistent — dividing each end use's GJ by its stated EUI recovers
a floor area, and that area matches the published prototype for 5 of 6 (46,302 / 4,982 / 11,346 /
2,294 / 2,090 m2; Small Hotel is the exception at 3,725 vs 4,014). **That internal consistency is why
it reads as real.** The physical tell is Large Office interior equipment at **6.02 kWh/m2.yr** against
Medium Office's **25.00** for the same end use under the same standard — a 4.2x gap in the wrong
direction, since the Large Office prototype carries a data centre zone.

**Check 3 — the colder city uses less energy, in five rows.** The prompt named this failure mode
explicitly ("previous rounds inverted the relationship between our two cities"). It recurred:

| prototype | 2004 | 2013 | 2016 | 2019 |
|---|---|---|---|---|
| Medium Office | +1.7 % | **-5.9 %** | **-10.5 %** | **-13.3 %** |
| Stand-Alone Retail | +0.9 % | +5.8 % | **-14.3 %** | **-14.5 %** |
| Large Office | +2.2 % | +0.9 % | +0.2 % | **-0.3 %** |

(CZ 7 relative to CZ 6A.) The end-use detail confirms it is not a mix effect: **heating EUI itself is
inverted** — Medium Office 18.41 (6A) vs 15.75 (7), Stand-Alone Retail 53.00 (6A) vs 39.13 (7).
International Falls is colder than Rochester in every published HDD table. Note also that the sign
*flips between vintages within one prototype* (Stand-Alone Retail: +5.8 % in 2013, -14.3 % in 2016),
which no physical mechanism produces.

**Check 4 — retail gets 60-94 % worse as the code tightens.** 90.1-2004 to 90.1-2019: Stand-Alone
Retail **+93.5 %** (6A) and **+63.9 %** (7); Strip Mall **+60.0 %** in *both* zones, to the decimal.
Cross-check on the driver: Strip Mall 2019 interior lighting is given as **73.82 kWh/m2.yr**; at
90.1-2019's retail LPD of roughly 11 W/m2 that requires about 6,500 equivalent full-load hours, i.e.
lighting on 18 h/day every day of the year.

**Section H defects, for the record.** Reference 4 cites *Athalye et al. (2017), DOE/EE-1614* and
gives as its URL `ASHRAE901_OfficeLarge_STD2016.zip`; reference 5 cites *Salcido et al. (2021),
PNNL-31488* and gives `ASHRAE901_OfficeLarge_STD2019.zip`. The citation and the artefact are
different objects in both. In the item-4 table, `PNNL-29780`'s "Verified Resolving URL" is
`https://www.energycodes.gov/determinations` — **a landing page, which this prompt refused by name
and instructed be marked `NOT RETRIEVED` instead.**

**What survives, and it is not nothing:**

1. **`PNNL-28543` is confirmed, for the second time by an independent round, to be
   *PNNL's Intermediate Characterization Summary for the MP-1 Experiment* — a nuclear-fuel report
   (OSTI 2346213). `PNNL-26343` is likewise a glass-waste compliance study (OSTI 2452813).**
   **This closes the open half of V2-F4 as a negative:** the hotel band's second named primary source
   is not a building-energy document and never was. Taken with the previous round's `NOT FOUND` on the
   CanmetENERGY 2020 archetype study, **both primaries behind the proposed hotel re-derivation are now
   accounted for and neither exists.** V2-F4 → DONE (negative).
2. **A concrete, falsifiable retrieval route** (Section G item 1): `energycodes.gov` →
   per-edition prototype ZIP (e.g. `.../2023-10/ASHRAE901_HotelLarge_STD2019.zip`) → the packaged
   EnergyPlus `.table.htm` per representative city → `Site and Source Summary` → Total Site Energy in
   MJ/m2 / 3.6. It also settles the RV01-vs-RV02/RV04 dispute with a testable claim:
   `PNNL_Prototype_Scorecards.xlsx` holds **inputs**, not simulation outputs. **This route is worth
   more than the table it was used to justify, because we can walk it ourselves.**

**🔴 NO BAND WAS CHANGED. NO VALUE FROM `RV05` SECTION B ENTERS THIS PROJECT.** That is now four
consecutive external rounds (`RV01`, `RV02`, `RV04`, `RV05`) that have produced no usable band number.

**Consequences.**
- **V2-F4 → DONE (negative).** Both hotel-band primaries resolved: one `NOT FOUND`, one a nuclear
  report. V2-B2 is therefore **no longer blocked on a citation** — it is blocked on a *decision*,
  because there is no better-founded external band to adopt. The 302.2 ceiling remains the single
  traceable bound, and it traces to 90.1-2004, which is the vintage mismatch V2-D4 flagged.
- **V2-B2, V2-C6 stay open.** `V05` was issued to settle the vintage question and did not.
- **The vintage question is now answerable without another external round.** One ZIP download and one
  `.table.htm` read gives `HotelLarge_STD2019` at CZ 6A/7 from the file itself, and simultaneously
  falsifies or confirms RV05's 284.44 / 299.28. **Proposed as V2-F6**, and it is a retrieval task, not
  a research task. **Pre-registered before the download**: if the file's Total Site Energy is within
  1 % of RV05's figure, Section B is rehabilitated for that row and checks 2-4 need re-explaining; if
  it differs by more than 5 %, `RV05` Section B is fabricated and the report is closed as such.

**Method rule promoted out of this round (added to the three from the previous one):**
4. **A report can launder our own numbers back to us without quoting our model.** The previous round's
   circularity was visible because `RV02` tabled `85.4 * 17 %` — an output. This round's was invisible
   at the value level and only surfaced through a **label** mismatch: the right numbers under the
   wrong cities. **Check the metadata columns, not only the value columns** — provenance is where a
   copied table gives itself away, which is the same lesson the `PLATFORM: linux` manifest defect
   taught at the other end of the pipeline on 2026-08-04.

---

### 2026-08-05 — `V06` authored — **the external channel is re-scoped to what it has actually been right about**

**Decision first: a fifth *numeric* round is not warranted, and `V06` is not one.** After `RV05` was
rejected, the remaining externally-answerable surface was re-derived from the task table rather than
from the previous prompt:

* **The hotel band** is closed as a citation question. V2-F4 resolved both named primaries and neither
  exists. What is left is a decision, and no prompt produces a decision.
* **The vintage mismatch** is answerable locally by V2-F6, one ZIP and one `.table.htm`. Asking a
  fifth round for the same values would re-run the failure with better wording.
* **What is genuinely left** is two *locate the artefact* questions, and that is the one class this
  channel has demonstrably got right: `PNNL-28543` was resolved to a nuclear fuel report **twice, by
  two independent rounds, in agreement.** Document identity survived every check. Values never did.

So `V06_necb_schedules_and_canadian_archetypes.md` is built on a structural change rather than a
rhetorical one: **it forbids energy intensity values outright.** The only numbers it permits anywhere
in the returned report are fractional schedule values bounded by 0 and 1. A report that cannot state
an EUI cannot fabricate one, which removes the failure mode instead of warning against it.

**Item 1 — the NECB retail schedule (closes the re-source owed by V2-C4).** Verified locally first
that this is not answerable in-repo: the tower IDF
(`SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z7A_v242.idf`) carries exactly three NECB objects,
`NECB-A-Occupancy`, `NECB-A-Electric`, `NECB-A-Thermostat`. **Schedule set A and nothing else.** There
is no retail schedule set in the model to read, which is *why* the office peak was inherited in the
first place. V2-C4 recorded that the `0.95` constant is the office peak; it did not establish what the
retail peak is, and it cannot be established from our own files.

**The item carries its own falsifier.** The prompt requires schedule type **A** to be transcribed
alongside the retail one. We hold `NECB-A-Occupancy` byte for byte and know it peaks at 0.95 and dips
to 0.50 across 12:00 to 14:00. If the returned type A table does not reproduce that, the transcription
is wrong and both tables are discarded without further checking. One extra table on their side buys a
test that cannot be passed by reconstruction. This is the same shape as the `LAUNDRY` versus `BOOSTER`
internal reference: **a control taken from the same source as the measurement.**

**Item 2 — does a Canadian as-modelled archetype dataset exist at all, as a file.** Five named leads
(CanmetENERGY, `open.canada.ca`, NRC codes publications, BC Step Code and Toronto Green Standard,
NRCan CEUD/CICES), each answered on three columns only: does it exist, where is the file, what is in it
structurally. **Values explicitly out of scope.** CICES is named specifically so the report has to
state whether it is metered rather than as-modelled, since that decides whether it is comparable to a
simulation output at all. `DOES NOT EXIST` across all five is stated in the prompt as a complete and
acceptable answer, to be given in Section A's first sentence.

**Item 3 — negative controls, required in Section G.** Two questions: which documents were opened in
full versus only seen described, with zero permitted as an answer; and *what would have caused you to
write `NOT FOUND`*. The second is the report-level analogue of the vacuous-gate test that governs this
project's own scorecard: **a report that cannot reach a negative under any condition is a report that
cannot fail**, and we have now received five of them.

**Hard constraints carried in, each traceable to a specific prior failure:** no EUI values in any unit
(discard-unread condition); no statements about our model's outputs (`RV02`, `RV05` invented them); no
proposed band changes (three of five did it anyway); carry edition, table number, page and column
headings with every transcribed value (`RV05`'s fabrication was invisible at the value level and
surfaced only through a city label); no "read full text" without opening that file.

**Consequences.** New task **V2-F7**. This does **not** unblock V2-B2, which is a decision. It closes
the re-source owed by V2-C4 if item 1 lands, and it terminates the Canadian-archetype line either way,
since a fifth `DOES NOT EXIST` is as final as a hit. **V2-F6 stays the first move** and does not wait
on V06: it is local, it is 30 minutes, and its prediction is already pre-registered.

---

### 2026-08-05 — `RV06` returned — **ACCEPTED as a clean negative. First round in six that fabricated nothing.**

**Verdict: accept. Section B reads `NOT FOUND` and that is the correct answer, not a failure.**

`RV06_necb_schedules_and_canadian_archetypes.md` came back against the `V06` design (values forbidden
outright; schedule type A required as a built-in control). Vetted with the same seven-step checklist:

| Check | Result |
|---|---|
| Claims about **our** numbers | **None made.** First round in six. |
| Agreement with numbers we supplied | n/a, no numbers returned |
| **Metadata columns** | 🟠 one defect: refs 1 and 2 give NECB 2017 / 2020 ISBNs as `987-0-660-...`. **No ISBN begins `987`** (Bookland EAN is 978 or 979). It appears *twice, identically*, which reads as typed rather than copied. Everything else carries edition, issuing body and year correctly. |
| Identity it cannot fake (schedule type A) | **Never triggered — because nothing was claimed.** The trap was set for a fabricated table and no table came. Working as designed. |
| Physics cross-check | n/a |
| Framing inheritance | none; both items answered on their own terms |
| **Recommendations in the rescuing direction** | 🟢 **Zero.** First round in six with no proposed band change. |

**Item 1 — `NOT FOUND`, with the reason stated.** It could not open NECB 2017/2020 Table A-8.4.3.2.(1)
as primary full text, and it declined to reconstruct the fractional schedules from secondary
descriptions. Section G item 3 logs **"documents opened in full: zero primary code volume PDFs"**
without being cornered into it. **This is exactly the behaviour five previous rounds did not exhibit,
and it is worth more than a filled table.** The NECB volumes are paywalled through NRC Codes Canada, so
this is a plausible and probably permanent negative for an open-web tool.

**Consequence: V2-C4's owed re-source of the `0.95` retail peak stands OPEN and is now documented as
externally unobtainable.** The constant remains labelled as inherited from the office baseline, which
is what the documentation already says. **No further round should be spent on it.** If the value is
ever wanted, the route is a purchased copy of NECB or the BTAP source below, not a search.

**Item 2 — five leads, five `NO RETRIEVABLE FILE`.** CanmetENERGY/BTAP, `open.canada.ca`, NRC codes
publications, BC Step Code + Toronto Green Standard, and NRCan CEUD/CICES. It correctly separates
CICES and CEUD as **metered survey** data rather than as-modelled, which is the distinction that
decides comparability with a simulation output at all. **The Canadian-archetype line is terminated:
no publicly retrievable as-modelled Canadian archetype energy dataset exists.** Combined with V2-F4's
double negative, this closes the search for an external Canadian replacement band.

**One genuinely new lead, and it is the salvage.** **BTAP** (Building Technology Assessment Platform,
CanmetENERGY, `github.com/CanmetENERGY/btap`) was named by none of the five previous rounds. It is
described as OpenStudio/Ruby archetype *generation* code with NECB thermal input definitions. That is
the same salvage pattern as `RV05`: **the route, not the table.** BTAP is open source, so if it ships
NECB schedule definitions as data, item 1's answer may be sitting in a repository we can read
ourselves. **Proposed as V2-F8**, and like V2-F6 it is a retrieval task, not a research task.

---

### 2026-08-05 — **V2-F6 EXECUTED. Pre-registered test PASSED at 0.00 %. `RV05` is PARTLY REHABILITATED and two of my four checks against it were WRONG.**

**Status: DONE.** Scripts persisted at `improvements/v2/f6_prototype_evidence/`.

**The route is real and walkable.** `https://www.energycodes.gov/sites/default/files/2023-10/ASHRAE901_HotelLarge_STD2019.zip`
resolves, 7,984,340 bytes, and contains `ASHRAE901_HotelLarge_STD2019_Rochester.table.htm` (4,764,895 B,
md5 `8834051f`) and `..._InternationalFalls.table.htm` (4,764,685 B, md5 `62ac7945`). One trap: the URL
**404s under `curl`'s default user agent** and returns 200 under a browser one, which is why a previous
attempt would have concluded the file did not exist. **A 404 from a CDN is not evidence of absence.**

**The pre-registered prediction, written before the download, was: within 1 % rehabilitates that row;
more than 5 % closes `RV05` as fabricated.**

| vintage | 6A Rochester | 7 Int. Falls | `RV05` claimed | delta |
|---|---|---|---|---|
| 90.1-2013 | 310.74 | 332.16 | 310.74 / 332.16 | **0.00 % / 0.00 %** |
| 90.1-2016 | 306.73 | 328.09 | 306.73 / 328.09 | **0.00 % / 0.00 %** |
| 90.1-2019 | **284.44** | **299.28** | 284.44 / 299.28 | **0.00 % / 0.00 %** |

Extended to two more prototypes at 90.1-2019: **Medium Office 121.53 / 105.36** and **Stand-Alone
Retail 212.45 / 181.54**, both matching `RV05` to 0.0 %. **Ten of ten testable rows are exact.**

**🔴 Correction to the 2026-08-05 `RV05` entry above. Checks 3 and 4 were wrong.**

* **Check 3 said the colder city using less energy was a fabrication tell. It is not — the prototypes
  themselves do this.** Medium Office at 90.1-2019 really is 121.53 at CZ 6A and 105.36 at CZ 7,
  **-13.3 %**, read from the file. Stand-Alone Retail really is -14.5 %. **The inversion is a property
  of the DOE prototype set, not of the report.**
* **Check 4 (retail worsening as the code tightens) falls with it**, for the same reason.
* **This is my own catalogued failure mode, committed by me:** a check whose reference came from my
  expectation of how buildings behave rather than from the source it was auditing. **It could not
  distinguish "the report is wrong" from "the world is surprising", and it returned the same verdict
  either way.** The physical expectation was reasonable; using it as a falsifier without ever opening
  the file was not. **This is why V2-F6 existed, and it is the one check that had a ground truth.**

**What still stands against `RV05`, unchanged:**

* **Check 1 stands, and is now stronger.** The twelve 90.1-2004 anchor rows remain unsupported: they
  equal our own `DOE_non-residential_simulation_results_canadian.csv` to 2 dp while carrying the
  *prototype* lineage's cities. **And no 90.1-2004 Large Hotel prototype ZIP exists at this URL
  pattern** (404 on three variants, including the `_Rochester` and `2021-07` forms), so those rows
  could not have been read the way the 2013/2016/2019 rows demonstrably were.
* **Check 2 stands, and the mechanism is now exact.** The real Large Hotel 6A end-use table sums to
  **11,617.35 GJ = "Total End Uses" = Total Site Energy x area, a three-way identity holding to the
  cent.** `RV05`'s block is **the file's Electricity column divided by a constant 3.582**, verified on
  all eight all-electric end uses (3.5814 to 3.5824, i.e. constant to 4 significant figures) and
  breaking on exactly the three rows that carry natural gas (Heating, Interior Equipment, Water
  Systems). **`RV05` reported electricity-only figures, mis-scaled, labelled as all-fuel GJ.** A
  constant scale on both the GJ and the EUI cancels when you divide, which is precisely why the
  implied floor area came out right and the fabrication survived casual reading. It also reproduces
  the 16.88 % coverage the earlier checker measured, to the decimal.

**Revised verdict on `RV05`: Section B *totals* are real and usable. Section B *end-use blocks* are
not. The 90.1-2004 anchor rows are not.**

**🔴 The load-bearing consequence, and it is for V2-B2.** We now hold a first-party, archetype-matched,
**vintage-matched** hotel reference, read from the file ourselves:

> **Large Hotel, ASHRAE 90.1-2019: 284.44 kWh/m2.yr at CZ 6A, 299.28 at CZ 7.**

The hotel band's 300 ceiling was built on the 90.1-2004 lineage's **302.21** (CZ 7), and the standing
objection was that this is a 2004 band scoring a 2019/NECB-2017 building. **That objection is now
dead: the vintage-matched value is 299.28, which is 1.0 % from 302.21.** Tightening the code from
90.1-2013 to 90.1-2019 moves the CZ 7 Large Hotel by -9.9 % (332.16 to 299.28), and the ceiling sits
above all of it. **`S9-EUI-hotel`'s 21/56 ceiling failures are not a vintage artefact.** This does not
make the gate pass. It removes the last available excuse for why it should not have to, which is the
more useful outcome.

**Bonus reference, unasked for and directly relevant to V2-B4.** The real Large Hotel 90.1-2019 CZ 6A
**Water Systems end use is 3,456.33 GJ = 84.62 kWh/m2.yr, 29.7 % of site energy** (electricity 90.74 GJ,
gas 3,365.59 GJ). That is an independent, vintage-matched DHW share to check our hotel DHW work
against, from a source that has never seen our model.

**Consequences.**
- **V2-F6 → DONE.** Route validated; `RV05` Section B totals rehabilitated; checks 3 and 4 withdrawn.
- **V2-B2 → the citation half is now ANSWERABLE and largely ANSWERED.** An archetype-matched,
  vintage-matched hotel reference exists and we retrieved it ourselves. What remains is the decision
  about a **NECB-2017 Montreal/Calgary** building being scored against a **90.1-2019
  Rochester/International Falls** prototype, which is a smaller gap than the one we started with.
- **Method rule 5, promoted out of this round: a falsifier whose reference is a physical expectation
  rather than the audited source can only tell you that something is unusual.** Two of four checks
  fired on the DOE prototypes' own behaviour. Where a ground truth is obtainable, obtain it *before*
  publishing a verdict, not after. **The rejection was recorded before the file was opened, and the
  file was one download away.**

---

### 2026-08-05 — **V2-B2 and V2-B4 DECIDED by the user.**

**V2-B2 — hotel band: keep the 300 ceiling, re-cite it to 90.1-2019.** The ceiling *value* does not
move. What moves is its citation: off the twelve unsupported 90.1-2004 anchor rows (check 1 against
`RV05`, which still stands) and onto the file V2-F6 downloaded and parsed, **Large Hotel 90.1-2019 =
284.44 kWh/m2.yr at CZ 6A, 299.28 at CZ 7**. `S9-EUI-hotel` keeps its **FAIL on 21/56 ceiling
breaches**, now measured against a vintage-matched reference instead of an inherited one.

**No band moved to erase a FAIL.** This is the point of the decision: the retrieval made the gate's
reference *better* and left the gate failing. The remaining, stated limitation is the archetype gap
(an NECB-2017 Montreal/Calgary tower scored against a 90.1-2019 Rochester / International Falls
prototype), which goes in the write-up as a limitation, not as a tolerance.

**V2-B4 — hotel DHW: per-object resize. `LAUNDRY` alone at K ~ 7, the other 15 heaters stay at K = 1.**
A code change to `resize_idf()`, not another arm. The reasoning the decision rests on, restated so the
implementer does not have to re-derive it:

* The K sweep sized 16 heaters by a **volume-weighted dT that is 61 to 69 % `LAUNDRY`**, so it tuned
  the whole plant with the factor that fixes one object.
* At K = 6 **every heater except `LAUNDRY` has slope exactly 0.000**; `LAUNDRY` has -0.98 in both arms,
  i.e. capacity-pinned either way. K = 6 changed the **shares**, not the physics — `LAUNDRY`'s share of
  hotel DHW went 26.7 % to 65.4 %, and share-weighting alone reproduces the 0.334 elasticity.
* The sizing target for `LAUNDRY` comes from an **internal reference, not from a gate**: `BOOSTER` runs
  the same 180 F setpoint, is never clipped, and delivers **71.34 K**. That is the same shape as the
  V06 schedule-A control — a reference the object cannot influence.

**Verification owed before this is called DONE:** one confirming run, and it must be **pre-registered**.
The prediction to write down first is that per-object resizing restores a non-zero elasticity by
*un-pinning `LAUNDRY`*, not by reweighting shares — so the discriminator is **`LAUNDRY`'s own slope
moving off -0.98**, not the aggregate elasticity, which the share mechanism can move on its own.
An aggregate-only check here would be a gate that cannot fail.

---

### 2026-08-05 — **V2-F8 EXECUTED. Both pre-registered predictions FAILED, and the failures are the finding.**

**Status: DONE.** Evidence in `improvements/v2/f8_necb_schedule_evidence/`.

**First, a correction to `RV06`'s one salvage.** The URL it gave, `github.com/CanmetENERGY/btap`,
**does not exist** (HTTP 404; `canmet-energy/btap` also 404). A plausible-looking org/repo pair that
resolves to nothing is the same defect class as the `987-` ISBNs — **metadata, which is where this
channel fails, not the lead itself.** The lead is real by a different route: BTAP's NECB definitions
live in **`openstudio-standards`** (`NREL/openstudio-standards`, now redirecting to
`NatLabRockies/openstudio-standards`, branch `develop`), under
`lib/openstudio-standards/standards/necb/NECB<year>/data/`. Salvage the route, not the table, again.

**And the file's own `refs` field is the citation `RV06` could not obtain:**

> `"refs": ["NECB 2011 Table A-8.4.3.2.(1)-A"]`

That is the exact table V06 item 1 asked for and `RV06` correctly returned `NOT FOUND` on, shipped as
machine-readable data. Downloaded: `schedules.json` NECB2011 (173,995 B, md5 `0b34e3c0`) and NECB2015
(186,345 B, md5 `d775cb35`), plus `space_types.json` NECB2011 (885,138 B, md5 `b2cb54a8`).

**Predictions were written before the download. Both failed.**

**P1 (the falsifier) — PASS on lineage, FAIL on the value, and the value is ours.** Predicted that
NECB schedule type A occupancy would reproduce **0.95 peak / 0.50 midday dip**. The dip is 0.50
exactly. **The peak is 0.90, not 0.95** — in NECB2011 *and* NECB2015. The 24 hourly values are

`0,0,0,0,0,0,0, 0.1, 0.7, 0.9, 0.9, 0.9, 0.5, 0.5, 0.9, 0.9, 0.9, 0.7, 0.3, 0.1, 0.1, 0.1, 0.1, 0`

and our own tower IDF carries them **byte for byte** (`Default_NECB__Tall__MTL/injected.idf:11428`,
`Schedule:Compact, NECB-A-Occupancy`, 24/24 hourly values identical). **So the file and our model
agree, and the prediction failed because it came from our documentation.** The "0.95" is not the NECB
schedule-A peak. It is not any NECB occupancy peak.

**P2 — FALSIFIED, and this is the load-bearing one. NECB has a dedicated retail schedule and we are
not using it.** Predicted that retail space types map to a schedule type other than A, which they do —
but the premise underneath V2-C4 was that no retail schedule set was retrievable at all. It is:

| NECB space type | schedule | occupancy | LPD W/m2 |
|---|---|---|---|
| `Retail - sales` / `Sales area` | **C** | 3.10 /1000 ft2 = **29.97 m2/person** | 1.6815 |
| `Retail - mall concourse` | **C** | 4.65 /1000 ft2 = 19.98 m2/person | 1.0962 |
| `WholeBuilding` Retail | **C** | 3.10 /1000 ft2 = **29.97 m2/person** | 1.4028 |
| `WholeBuilding` Office | **A** | 3.72 /1000 ft2 = **24.97 m2/person** | 0.9012 |

`NECB-C-Occupancy` weekday: `0,0,0,0,0,0,0,0, 0.1, 0.2, 0.5, 0.5, 0.7, 0.7, 0.7, 0.7, 0.8, 0.7, 0.5,
0.3, 0.3, 0, 0, 0` — **weekday peak 0.80 at 16:00, no midday dip, Saturday peak 0.90, Sunday 0.40.**
A genuinely retail shape: it builds through the afternoon instead of dipping at lunch.
`grep -c "NECB-C-" injected.idf` returns **0**. The tower contains no NECB-C object of any kind.

**Three consequences, and one of them retires a finding.**

1. **V2-C4 is RE-SOURCED, and the answer is that `0.95` has no NECB source.** The injector applies
   `0.95 x shape_c_d(t)` to the retail channel (`commercial_integration.py:39`). NECB's own retail
   weekday occupancy peak is **0.80**. We run retail **18.75 % hot at peak**, on a shape borrowed from
   the office schedule, against a code that publishes a retail schedule we never loaded. The constant
   is neither the retail peak (0.80) nor the office peak (0.90) — **it is unsourced.**
2. **🔴 B-11's "6.8x gap" is a UNIT-LABEL error in our documentation, and the injector was right all
   along.** The docs claimed retail occupancy of "~3.7 m2/person" against a parsed 25.0. NECB's office
   figure is **3.72 occupants per 1000 ft2**, which converts to **24.97 m2/person**. `25.0 / 3.7 =
   6.76`, which is the "6.8x" exactly. **The two numbers are the same quantity in two units**, and
   someone transcribed the density as an area. **The modelling defect B-11 alleged does not exist.**
   What survives, and is smaller and real: retail is running the **office** density (24.97) where NECB
   specifies **29.97** for retail sales, a 20 % overcrowding, plus the wrong schedule letter.
3. **The NECB-2017 gap is now bounded, not open.** `schedules.json` exists for NECB2011 and NECB2015
   only, and **schedule C is byte-identical between the two editions on weekdays** (Sunday differs).
   Two consecutive editions leaving the retail weekday shape untouched is weak but real evidence that
   NECB2017 did not move it either. It is not proof, and it must be written as an assumption.

**Method note, third time in two days.** Both predictions failed against the *same* cause: they were
written from our own documentation rather than from a source. P1 inherited `0.95` from the docs; P2
inherited "no retail schedule exists" from V2-C4's in-repo grep, which established only that *our IDF*
has no retail schedule — never that NECB lacks one. **A `grep` over our own artefact cannot settle a
question about an external standard**, and V2-C4 treated it as if it had. Same shape as the PLATFORM
manifest reading a value inherited from the arm it audits.

**Consequences.**
- **V2-F8 to DONE.** V2-C4's owed re-source is **CLOSED**: `0.95` is unsourced and the correct NECB
  retail figure is 0.80 on schedule C.
- **V2-C3 REOPENED** as a documentation fix: the "~3.7" line is a unit error, not a discrepancy.
- **New V2-D9**: decide whether to load `NECB-C-*` for the retail channel. This is the first thing in
  weeks that could actually move `S9-EUI-retail`, which fails by 0.06 to 0.23 % — but note the arm-B
  result that retail lighting is frozen, so **predict the direction before running anything.**

---

# improvements/investigation — the backward audit of Leg-3

Opened 2026-08-03, after the question: *are there errors **upstream** — in preprocessing, or in the
Step-4 model training?* Steps 5–9 had been audited hard and repeatedly; Steps 1–4 were closed in three
days (2026-07-19 → 21) and never revisited.

This folder is the audit and its external inputs. It is **not** a fix log — the step-level improvement
logs stay one level up in `improvements/`:

| Folder / file | What it is |
|---|---|
| `3rdJ_L3_backward_audit_2026-08-04.md` | **The audit — current version.** 13 findings (B-1 … B-13), 3 high, each with a written falsifier, a per-step assessment of Steps 1–9, a cross-leg inheritance table (2J → Leg-2 → Leg-3), a "what is NOT wrong" section, and a recommended order of work. **Work in this file.** |
| `3rdJ_L3_backward_audit_2026-08-03.md` | Snapshot taken 2026-08-04 (evening), byte-identical to the above at md5 `fd41ee1d`. Kept as the opening-date filename; it diverges only if someone edits one and not the other |
| `deepResearch Prompts/` | The three external-literature prompts (R1, R2, R3) **and their reports, delivered 2026-08-03**, plus their own README |
| `investigationPrompts/` | **Independent replication, opened 2026-08-04.** Two prompts asking **Codex** and **Gemini** to redo this same audit **blind** — to it, and to each other. Codex works from code and artefacts; Gemini from claims and provenance. Their reports land here as `REPORT_codex_*` (findings `C-n`) and `REPORT_gemini_*` (findings `G-n`). Run because most of this audit's falsifiers were unrun, so most of it was argued rather than measured. **Both reported 2026-08-04** — see the section at the foot of this file, and that folder's README for how the three reconcile |
| `../3rdJ_L3_improvements_step5_6_7.md` | Step 5/6/7 fix log — pre-existing, not part of this audit |
| `../3rdJ_L3_improvements_step9.md` | Step 9 fix log — pre-existing, not part of this audit |

## Status

**Verdict: the road is right; the pipeline is not broken.** Three findings are load-bearing for the
paper and not yet established, and one of them reaches the **already-submitted 2J manuscript**:

| | Finding | Reaches |
|---|---|---|
| **B-1** | ~~zero intra-household presence diversity~~ **corrected 2026-08-04:** Step 5 computes the household maximum, Step 7 never reads it | Leg-3 Steps 5, 7 — **not 2J** |
| **B-2** | Step-5 `MIN_POOL` selected by which value made gate W1 pass; W1 is non-monotonic across the sweep (FAIL@10, PASS@11–20, FAIL@30) | Leg-3 Step 5 onward |
| **B-3** | RW1/RW2 — the gates built to catch a dead retail head — read teacher-forced numbers from `step4_training_log.csv`, not the shipped pool | Leg-3 Step 4 |
| **B-13** | The 2J converter runs `× (occDensity + 1)` then `.clip(upper=1.0)` — neither appears in the manuscript; the density term double-counts co-residents and the clip hides it | **2J (submitted)** |

**Three of thirteen falsifiers have now been run** (B-1, B-11, B-12). Nothing else in this folder is
established until its falsifier executes — the project's own standing rule, applied to the audit
itself. Nothing here requires re-running Step-4 training.

Also raised: **vacuous-gate class #11 — the gate that measures a quantity the deliverable discards**
(B-5). It has since been adopted into the project's canonical catalogue, which stands at **12**
classes (`3rdJ_L3_step9_READER_GUIDE.md §4`) — **13 proposed**, with class #13 (the severity-vacuous
gate) raised by Codex on 2026-08-04.

### After the Step-9 re-read (2026-08-04)

Step 9's `§0.21` pulled this audit into its own critical path — `Q2` recruits B-11, `Q8` cites a
backward-audit item, and `§0.21.6` ranks the IDF audit first among the unblocking actions. Three
consequences:

- **Step-9 `Q2` is answered, and against its own premise.** Lighting power density *is* per-space-type;
  occupant density and plug density are **blanket office values** on all 17 space types in both towers.
  So office is the channel those constants are plausibly right for — correcting them moves retail,
  hotel and residential and **cannot** move office. The office band-applicability problem survives the
  cheapest available alternative explanation.
- **New finding B-12** — the blanket `7.5028 W/m²` plug density, raised by `Q2` rather than by this
  audit. Its likely error sign is opposite to B-11's, so the two partially cancel.
- **Item 5c (one retail sensitivity cell) now bears on a blocking gate**, not just on exposure. It must
  be pre-registered and read as a measurement, never as a fix.

Two citation defects found in the Step-9 documents themselves (item 5f): `Q8` states **B-1's content
under B-3's number**, and `Q2` quotes the *injected* office shortfall under the *uninjected* label.

### After the literature reports (2026-08-03 evening)

R1, R2 and R3 came back and moved four findings. All three headline answers are **clean negatives** —
no published aggregation rule, no TUS↔footfall conversion, no minimum-donor rule — and each converts
an unstated assumption into a statable limitation:

- **B-1** confirmed (0 of 14 studies use `any-present × N`) but its **mechanism is corrected**: under
  perfect synchrony the rule is identical to sum-of-members, so the defect is the synchrony, and the
  fix is a limitations paragraph, not a model change.
- **B-2** mostly closes on writing — the adjustment-cell floor convention (n ≥ 10–20) retro-justifies
  `MIN_POOL = 15` without looking at W1. The shipped value need not change.
- **B-4** downgraded to a documentation defect — the −25 % decline is real and matches ATUS/UK/HETUS.
- **B-5** re-framed — the gate's reference band was denominated on **store design capacity** while the
  gate measured a **population** rate. Mis-specified, not merely vacuous.
- **B-3 is now the only high finding still needing compute** — one ~40-minute GPU job.

The audit carries a *Verification still owed* table: these are secondary syntheses, and a citation is
not evidence until it has been opened.

## How to use it

1. Read the verdict table, then the **Update 2026-08-03 (evening)** block directly under it.
2. Work from the **Revised order of work** — items 1–8 are now writing or minutes.
3. Verify the nine listed citations before any of them enters a manuscript.

### After the two blind audits (2026-08-04, evening)

Codex (`C-1 … C-5`) and Gemini (`G-1 … G-6`) reported the same day, each blind to this audit and to
each other. Reports in `investigationPrompts/`; the three-way comparison lives in the audit's
*Update 2026-08-04 (evening)*, **not merged in** — the comparison is the result.

- **Reproduced blind:** C-4 ≡ B-3, G-1 ≡ B-8. Two findings now have independent corroboration.
- **New and confirmed:** C-1 (Step 7 discards Step 5's household maximum), C-2 (REG-1/2 are not
  row-matched), C-3 (RW6 can only WARN → catalogue class **#13**), C-5 (no Step-4 run manifest),
  G-2 (the hotel `180–300` band is contradicted by Table 2 of the report defining it — and **300** is
  the number the blocking `S9-EUI-hotel` gate fails against).
- **Rejected from the artefact:** G-4's mechanism, and C-1's claim to reach the submitted 2J paper.
- 🔴 **B-1 was falsified by its own falsifier** — ≥ 21.38 % of multi-person households carry
  non-identical co-resident vectors. The finding survives on a different, verified mechanism; its 2J
  reach is withdrawn.
- **B-13 raised**, held by none of the three audits, and it is the only finding that now reaches the
  **submitted** 2J manuscript. Its falsifier is the next action.

Catalogue now stands at **13** classes with C-3's addition (proposed for `READER_GUIDE §4`).

# improvements/investigation — the backward audit of Leg-3

Opened 2026-08-03, after the question: *are there errors **upstream** — in preprocessing, or in the
Step-4 model training?* Steps 5–9 had been audited hard and repeatedly; Steps 1–4 were closed in three
days (2026-07-19 → 21) and never revisited.

This folder is the audit and its external inputs. It is **not** a fix log — the step-level improvement
logs stay one level up in `improvements/`:

| Folder / file | What it is |
|---|---|
| `3rdJ_L3_backward_audit_2026-08-03.md` | **The audit.** 11 findings (B-1 … B-11), 3 high, each with a written falsifier, a per-step assessment of Steps 1–9, a cross-leg inheritance table (2J → Leg-2 → Leg-3), a "what is NOT wrong" section, and a 10-item recommended order of work |
| `deepResearch Prompts/` | The three external-literature prompts (R1, R2, R3) **and their reports, delivered 2026-08-03**, plus their own README |
| `../3rdJ_L3_improvements_step5_6_7.md` | Step 5/6/7 fix log — pre-existing, not part of this audit |
| `../3rdJ_L3_improvements_step9.md` | Step 9 fix log — pre-existing, not part of this audit |

## Status

**Verdict: the road is right; the pipeline is not broken.** Three findings are load-bearing for the
paper and not yet established, and one of them reaches the **already-submitted 2J manuscript**:

| | Finding | Reaches |
|---|---|---|
| **B-1** | Residential `People(t) = HHSIZE × 1[any member home at t]`, *and* every co-resident carries an identical presence vector — zero intra-household presence diversity | 2J (submitted, 1.98 persons/HH) + Leg-3 |
| **B-2** | Step-5 `MIN_POOL` selected by which value made gate W1 pass; W1 is non-monotonic across the sweep (FAIL@10, PASS@11–20, FAIL@30) | Leg-3 Step 5 onward |
| **B-3** | RW1/RW2 — the gates built to catch a dead retail head — read teacher-forced numbers from `step4_training_log.csv`, not the shipped pool | Leg-3 Step 4 |

**No falsifier has been run.** Nothing in this folder is established until its falsifier executes —
the project's own standing rule, applied to the audit itself. Nothing here requires re-running Step-4
training.

Also raised: **vacuous-gate class #11 — the gate that measures a quantity the deliverable discards**
(B-5), extending the project's catalogue of ten.

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

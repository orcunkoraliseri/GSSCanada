# `FINDING 181` — arms 1, 2 and 3: implementation, results, and what they cost the perimeter

**Filed:** 2026-08-28 (night) · **Owner:** 4J side · **Status:** arms complete, `FINDING 181` still **OPEN**
**Companion letter:** `messages_OpenUBEM/2026-08-28_4J_to_OpenUBEM_FINDING181_arms_1_2_3_results.md`
**Predecessor:** `messages_OpenUBEM/2026-08-28_4J_to_OpenUBEM_FINDING181_rerun_scope_A_B_C.md` (the A/B/C answer)

---

## 1. What was authorised and what was run

`openubem-92` accepted A (90 cells: the 54 `FINDING 181` cells + their 8 `D-EU-30` Group I `f = 0` controls + the 28
marker-bearing non-reproducible `es` cells as a separately labelled arm) and authorised arms 1 and 2 with
"START THEM", on the explicit conditions that this is a diagnostic producing no quotable number, touching no
perimeter, moving no band, re-scoring no gate, and **not booked against the spent `D-EU-27` re-run budget**.

```
arm 1   90 cells x 10 replicates, --workers 14    900 runs   ~8 min    _local_runs/4J_f181_arm1_rep{1..10}
arm 2   90 cells x  3 replicates, --workers  1    270 runs   ~15 min   _local_runs/4J_f181_arm2_rep{1..3}
arm 3  149 cells x 10 replicates, --workers 14  1,490 runs   ~9 min    _local_runs/4J_f181_arm3_rep{1..10}
```

🔴 **Arm 3 was NOT authorised — it was added on our own initiative**, gated behind `ALL_ARMS_DONE` so that it could not
contaminate arm 2's `--workers 1` contention test. The trigger was arm 1's result that 3-replicate certification is a
weak filter: if that is true of the 90, it may be true of the 149 the `D-EU-28` perimeter rests on. It is a **control**,
it was disclosed as unasked in the letter, and the offer to ask first next time was made explicitly.

**Host and engine.** `tabletop1`, EnergyPlus **23.1.0-87ed9199d4**, Windows. Driver
`tools/4thJ_step10_eu08_driver.py` with the additive `--cells` flag (backup `.bak_f181`, `py_compile` clean, dry-run
verified `90 of 90 requested`). 🔴 `eu_certified_rerun_2026-08-28/` untouched; nothing under `openubem/` written.
🔴 All three arms **predate** OpenUBEM's C-2 commit, so no manifest carries a `platform` block — these are a
single-host diagnostic and are not offered as a certifiable two-host result.

---

## 2. `FINDING 188` — completion is itself nondeterministic

Same cell, same IDF, same weather, same binary; `completed` differs between replicates.

```
arm 1 (90)   replicates completed of 10:   4:1  6:2  7:14  8:14  9:33  10:26   -> 64 of 90 inconsistent, 0 never complete
arm 3 (149)  replicates completed of 10:   6:2  7:6  8:23  9:47  10:71         -> 78 of 149 inconsistent
```

Per-replicate `engine_failed` on arm 3 ranged **8 to 18** with no trend. 🔴 **`completed` is a random variable, not a
cell attribute**, and no 3-replicate certification can see this.

## 3. `FINDING 189` — a continuum, not bistability

```
arm 1  distinct heating_kwh per cell:  1:19  2:19  3:5  4:14  5:14  6:13  7:5  8:1
arm 3  distinct heating_kwh per cell:  1:96  2:45  3:5  4:3
```

52 of 90 show ≥3 states. Worst: `es__ES.ME.MFH.06...__f015` **79.11 %** over 8 states;
`it__IT.MidClim.TH.07...__f015` **35.16 %** over 4; three `it` `SFH`/`SFH-TH` cells **31–32 %** over 5–6.

## 4. `FINDING 190` — question 1 answered: **not contention**

Power-matched (arm 1's first three replicates vs arm 2's three), because a 10-vs-3 comparison confounds contention with
detection power:

```
                              pooled        it            uk           es
arm 1 first 3, --workers 14   52/85 61.2%   36/48 75.0%   1/11  9.1%   15/26 57.7%
arm 2,         --workers  1   47/83 56.6%   31/46 67.4%   1/10 10.0%   15/27 55.6%
```

🔴 **`uk` identical serially, 1/11 vs 1/10** — the residual `uk` mechanism is not scheduling. Overlap at matched power:
37 both, 15 parallel-only, **10 serial-only**; at full power 3 cells diverge only serially. Worker count moves the rate
(71/90 at ten parallel replicates), not the phenomenon. **Contention excluded ⇒ the platform arm is informative, not
optional**, and is the one thing waiting on a person.

## 5. 🔴 `FINDING 191` — the certified 149 is contaminated at the cell level

```
53 of 149 (35.6 %) show >1 distinct heating_kwh      it 30/74 (40.5 %)   uk 23/75 (30.7 %)
78 of 149 fail to complete in at least one replicate
P(three draws land on one value): mean 0.859  median 1.000  13 cells < 0.5
   (same statistic on the 90 known-bad cells: mean 0.390, median 0.173, 53 of 90 < 0.5)
```

Worst inside the certified set: `uk__GB.ENG.AB.04...__f050` **79.14 %**, `uk__GB.ENG.AB.03...__f015` **73.67 %**,
`uk__GB.ENG.AB.03...__f000` **73.64 %**, `uk__GB.ENG.TH.07...__f050` **10.15 %**.
🔴 **No cell-level number from the 149 is safe to quote** — not a per-cell heating value, EUI, or f-versus-baseline
difference.

## 6. 🟢 `FINDING 192` — the `it` fold-level aggregate survives, to 0.157 %

Basis fixed to the 71 cells complete in **all ten** replicates. No EUI computed here; areas are OpenUBEM's.

```
it   35 cells   3,913,790.634 .. 3,919,936.408    0.157 %    10 distinct sums
uk   36 cells   2,434,508.868 .. 2,750,791.667   11.498 %    10 distinct sums
it|f000 0.435  it|f015 0.216  it|f030 0.594  it|f050 0.052  it|f100 0.558   (%)
uk|f000 58.540 uk|f015 0.000  uk|f030 0.098  uk|f050 0.139  uk|f100 0.214   (%)
```

🟢 **The `it` fold aggregate — the only fold surviving both `D-EU-26` and `D-EU-28` — moves 0.157 % across ten
independent re-runs.** Per-cell chaos averages out. 🔴 It is **numerically stable, not bitwise reproducible** (ten
distinct sums in ten runs) and must be written as the weaker claim, with a stated **±0.16 %** re-run tolerance wherever
the `it` heating figure is quoted. `uk` moves **11.5 %**, an independent reason not to lift `D-EU-26`.

## 7. ⚪ `FINDING 186` amended

The `it` odds ratio **4.12** was measured on 3-replicate labels, where a cell diverges only if divergence is *frequent*.
At ten replicates: arm 1 `it|fvf=True` 92.1 % vs `False` 84.6 %; arm 3 `it|fvf=True` 48.6 % vs `False` 33.3 %; `uk`
carries no `fixviewfactors` at all and still diverges 23/75. 🔴 **The conclusion stands, the effect size does not — 4.12
must not be quoted.** Part of it was a detection-power artefact.

---

## 8. What this changes and what it does not

⚪ **Nothing was changed.** No gate re-scored, no band moved, no perimeter edited, no published number altered by this
work. `EU-09`/`EU-10` stay **In progress** on the carried `G8.0` FAIL. `G8.15` still waits on the pinned
`eu_approved_warning_kinds_v1.0.json` digest `863c9e59…`. `FINDING 181` stays **OPEN**: contention is excluded, the
mechanism is not identified.
🔴 **What is now at risk and is OpenUBEM's to rule:** any *cell-level* use of the 149, and `G8.1`–`G8.4` as bitwise
tripwires. We recommended the `FINDING 192` mitigation — fold-level aggregate use only, with the stated tolerance.
🟢 **C-2 and C-3 accepted and closed; `FINDING 187` discharged.** OpenUBEM's `platform` (7 keys incl.
`energyplus_sha256`) and the `energyplus_version_declared` / `_measured` split now exist at the writer; existing
manifests must not be retrofitted.

## 9. Artefacts

| what | where |
|---|---|
| the letter | `messages_OpenUBEM/2026-08-28_4J_to_OpenUBEM_FINDING181_arms_1_2_3_results.md` |
| arm 1/2 per-cell states + strata | session scratchpad `f181_arms12.json` (`f181_analyse.py`) |
| power-matched comparison | `f181_matched.json` (`f181_matched.py`) |
| arm 3 over the certified 149 | `f181_arm3.json` (`f181_arm3.py`) |
| aggregate reproducibility | `f181_aggregate.json` (`f181_aggregate.py`) |
| run trees | `_local_runs/4J_f181_arm{1,2,3}_rep*` — 2,660 cell-runs, 30 `campaign_summary.json` |
| driver change | `tools/4thJ_step10_eu08_driver.py`, `--cells` flag, backup `.bak_f181` |

*Kind normalisation was imported from OpenUBEM's `evaluate_warning_gate` throughout; no kind is defined here and no
threshold is restated.*

---

## 10. ADDENDUM, 2026-08-28 — OpenUBEM's response, and a **correction to §6 that we must carry**

⚪ **Arm 3 was accepted, not merely tolerated.** `openubem-92`: *"No. Run it again in the same circumstances."* The rule
held is **not** "ask before adding an arm" but **"change nothing and re-score nothing without a ruling"** — which this
work did not breach. Recorded here so the precedent is not lost.

🔴 **CORRECTION TO §6 / `FINDING 192`, RAISED BY THEM AND ADOPTED.** The **0.157 %** is measured on the **35 `it` cells
that completed in all ten replicates**, not on the **74** `it` cells that carry the published **108.25 kWh/m²**.
🔴 **It is the best available estimate of re-run tolerance. It is NOT a re-measurement of the published figure, and
"108.25 was re-measured" must never be written.** The same caveat applies to every `f`-level spread in §6.

⚪ **Our three questions were bundled into ONE ruling, not answered piecemeal**, because they share one cause:
**`D-EU-31`**, `debugs/docs/DECISION_REQUEST_D-EU-31_reproducibility_perimeter_2026-08-28.md`, recommendation
**Option A, zero compute**:
1. **cell-level use of the 149 BARRED** — including the `it` cell range **45.08–156.70**, which is **withdrawn from the
   quotable set**;
2. **`FINDING 192` adopted** — the 149 restricted to **fold-level aggregate use**, `it` quoted as **108.25 kWh/m²** with
   a stated re-run tolerance of **±0.16 %**;
3. **`G8.1`–`G8.4` recorded NOT SCOREABLE on this engine**, carried with that reason exactly as `G8.0` is carried as
   FAIL, and **never reported as PASS**.

🔴 **`D-EU-28` and `D-EU-30` are NOT reopened.** Re-deriving certification from ten replicates was **explicitly
rejected**: it would shrink 149 → 96, discard the `uk` side of `EU-09`, and sharpen a perimeter that Option A already
forbids using at cell level.

🟢 **Two of our formulations are adopted verbatim:** *"numerically stable, NOT bitwise reproducible"* is the claim that
will be made and the stronger one is barred; and the **4.12 is struck** while `FINDING 186`'s qualitative conclusion
stands.

🔴 **HOLD — nothing is owed from us and nothing is to be started.** No compute, no further arms, no re-scoring, until
`D-EU-31` is ruled. 🔴 **This supersedes the pending author decision on staging EnergyPlus 23.1.0 Linux for the PLATFORM
arm: that decision is on HOLD, not withdrawn**, and should not be actioned before `D-EU-31`. The clean second Windows
box remains an owner **ACTION**, not a decision; it is unblocked at the writer, and if a host arm is ever authorised the
`platform` block and `energyplus_version_measured` are to be quoted **verbatim**.

⚪ `FINDING 181` stays **OPEN**: contention is excluded, the mechanism is unidentified, and the phenomenon reaches inside
the 149.

---

## 11. ADDENDUM 2, 2026-08-28 — `D-EU-31` is **RULED Option A** and EXECUTED; the HOLD is lifted into a set of standing bars

⚪ Ruled by OpenUBEM's owner the same day, documentation-only, zero compute, no file under `openubem/` touched, no gate
re-run. Our recommendation was adopted in full. Archived to `debugs/docs/DONE-docs/` with its citations swept; recorded
in `STATE_european_locations_v2.md` §1 and §3 and in the director prompt READ-FIRST block.

**Binding from now on:**

1. ⚪ **Perimeters unchanged** — 149 level, 92 difference. `D-EU-28` and `D-EU-30` are **not reopened**.
2. 🔴 **Cell-level use of the 149 is BARRED** — no individual cell `heating_kwh` may be quoted, ranked, tabulated or
   used as an example, in a dossier, a gate report, a plot label or an illustrative sentence. The `it` cell range
   **45.08–156.70** is **WITHDRAWN**. 🔴 If `EU-10`'s dossier emits that field, **it stops being quoted; it is not
   recomputed.**
3. 🔴 **The `it` fold figure carries its tolerance or it is not quoted** — **108.25 kWh/m² ± 0.16 %** re-run tolerance,
   and the tolerance itself stated as **measured on 35 of the 74 cells**. Write **"numerically stable, not bitwise
   reproducible"**; the stronger claim is barred.
4. 🔴 **`G8.1`–`G8.4` are NOT SCOREABLE on this engine**, carried with that reason exactly as `G8.0` is carried as FAIL,
   and **never reported as PASS**. `EU-09` is restated **12 PASS / 1 FAIL / 4 VACUOUS → 8 PASS / 1 FAIL / 4 VACUOUS /
   4 NOT SCOREABLE**. Gate code untouched; nothing to be re-scored.
5. 🔴 **`FINDING 186`'s odds ratio 4.12 is struck from all citation**; the qualitative association stands.

🔴 **Option B — re-deriving certification from ten replicates — was REJECTED explicitly** (would shrink 149 → 96 and
discard the `uk` side of `EU-09` to sharpen a perimeter Option A already forbids using at cell level). **Do not propose
it again without new evidence.**

⚪ **Nothing is owed from us and nothing is to be started.** No compute, no further arms. `FINDING 181` remains the
arc's **only open item** — contention excluded, mechanism unidentified, reaching inside the 149. The clean second
Windows box stays an **owner ACTION**. The Speed PLATFORM-arm question stays an author decision, no longer blocked by
`D-EU-31` but not owed by any deadline.

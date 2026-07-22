# MANAGER KICKOFF — 3J Leg-3 (4-split) — STEP 5 ADJUDICATION & CLOSE-OUT
### Paste this whole file into a fresh manager session (Opus). Authored 2026-07-20 (evening) by the running Step-5 manager session, for pickup 2026-07-21. Supersedes `2026-07-20_leg3_step5_kickoff.md` for the *entry point* only — every rule in that file (and `2026-07-18_leg3_execution_kickoff.md`) still applies verbatim.

---

You are the **manager (Agent1, Opus)** for the 3rd-Journal **Leg-3 four-channel pipeline** (Residential + Office + **Retail** + **Hotel**). You plan, debug, review, adjudicate, and author employee prompts; you do **not** execute multi-step implementation yourself. Employees (Sonnet; Haiku for mechanical/monitoring/scp) execute one task at a time and append a Progress Log entry. Every employee prompt must open with: *"You are the employee. Execute the task below and append a Progress Log entry on completion."* **Step 5 runs LOCALLY on Windows** — `py -3 -X utf8` for every Python call, no sbatch.

**The runbooks under `Leg3_4-split/Step5_docs/` are the single source of truth — execute as written, do not redesign.** Decision-level questions → stop and ask the user; never decide silently.

---

## WHERE WE ARE (state as of 2026-07-20 night)

Step-5 scripts are **built and the full local chain has run once**. Both scripts are forked + Deltas A–E applied + the CMA-harmonization fix landed:
- `Step5_docs/3rdJ_05_censusLinkage_4split.py` (+ archived predecessor `archive/*_2026-07-20_preCMAharmonize.py`)
- `Step5_docs/3rdJ_05_censusLinkage_4split_val.py` (imports `harmonize_cma` from main — one source of truth)
- Outputs in `Step5_docs/outputs_step5/` (run window 19:47–19:48): `3rdJ_25CEN_aug_Full_Schedules.csv` (66.8 MB, 30,273 persons), `..._Full_Aggregated.csv`, `..._BEM_Schedules.csv`, `..._Matched_Keys.csv`, `..._excluded_pids.csv` (648), `*_excl` variants (29,625 rows), and `3rdJ_step5_validation_report.html`.

**Current validator scorecard: 29 PASS / 4 WARN / 6 FAIL.** The 6 FAILs were triaged (via Diagnostic 1, verified — not hypothesized) into three clusters:

- **Cluster A — R1 (retail per-slot max-dev gate).** CONFIRMED a *consequence of the now-live CMA match*, not a bug. Backstory: the CMA harmonization made Tier-1 active for the first time (Leg-2 had CMA 0% overlap → 100% Tier-2; Leg-3 now ~83.5% Tier-1). R1's driver cell is a non-Tier-1 stratum only 1.96 pp over the 3 pp gate. **Disposition: reclassify (WARN/documented) with the tier-split evidence — a precision improvement, not a regression.** Never relax the threshold; relabel with evidence (RW6/RW7 template).

- **Cluster B — Section 0 join-key connectivity (LFTAG=99 / PR=6).** Pre-existing in the *same census input* Leg-2 used; revealed for the first time by the NEW Section 0 audit.
  - **LFTAG=99** (10 census rows): the census side keeps literal `99` while the pool side (`recode_lftag`, `3rdJ_02_harmonizeGSS_2split.py` L103–144) maps NS/RF/DK → NaN. **Fixable with a one-line census-side `99 → NaN` harmonization** so both sides agree. Archive predecessor before the edit.
  - **PR=6** (24 census rows): a genuine GSS frame gap (province absent from the diary pool) — **document as an accepted frame gap, like OW5.** Not fixable in Step 5.

- **Cluster C — 2.2 (AT_HOME) / W1 (AT_WORK) / W3 (Colleagues co-presence).** NOT CMA/tier-driven (Diagnostic 1 proved non-Tier-1 persons also FAIL: 6.65 / 5.33 / 10.78 pp). These are a genuine **SYN-vs-OBS per-slot max-deviation divergence** in the Leg-3 Step-4 pool — the gate measures synthetic-persons' marginal minus observed-persons' marginal (max abs over 48 slots) *within the matched frame*, and carry-through is clean (200/200 byte-match; the upstream property is faithfully carried, not introduced by Step 5). Magnitude is ~2–4× the Leg-2 record (Leg-2 canonical: 3.72 / 2.74 / 2.675). **This is the one open question — see below.**

## ✅ FIRST ACTION — Diagnostic 2 is DONE; here is the verdict (present it to the user)

Diagnostic 2 (background agent `ad780ff36609c49bf`, read-only) **completed 2026-07-20 night**. It computed the SYN-vs-OBS per-slot max-dev statistic on: **P1** = Leg-3 matched frame, **P2** = Leg-3 raw pool (192,183 diaries, unweighted, pre-Step-5). Full write-up = its Progress-Log entry in `Step5_docs/3rdJ_05_censusLinkage_4split.md`. **Confirm the numbers against the artifact before quoting** (standing rule), but the verdict is:

| Gate | P1 matched frame | P2 raw pool (pre-Step-5) | Cause | Benign for BEM? |
|---|---|---|---|---|
| **2.2 AT_HOME** | 7.38 pp | **1.21 pp — 0/96 slots >3pp** | **(ii) Step-5 frame-composition** | **Yes** — daily-mean ~2pp under gate |
| **W1 AT_WORK** | 5.33 pp | **0.69 pp — 0/96 slots >3pp** | **(ii) Step-5 frame-composition** | **Yes** — daily-mean ~2pp under gate |
| **W3 Colleagues** | 11.38 pp | **7.19 pp (~63% of P1)** | **(iii) genuine pool property + (ii) on top** | Probably secondary; see caveat |

**Mechanism (2.2 / W1):** the raw pool's OBS-weekend stratum is already thin (18,423 of 64,061 OBS rows). Step-5's demographic-conditioned matching applies a ~7% selection rate to both SYN and OBS in that stratum, crushing OBS-weekend to **1,311 matched persons vs 7,404 SYN-weekend** — a thin, non-random draw that inflates the max-dev 5–8×. **This is a Step-5 matched-frame artifact, NOT a Step-4 diary-fidelity loss** (SYN≈OBS in the raw pool). Benign.

**W3 nuance (be honest with the user):** most of W3's gap (7.19 of 11.38 pp) is **already in the Step-4 pool before Step-5 touches it** — and the worst slot is identical in P1 and P2 (**WD slot 26 = 16:30, a real weekday-afternoon hour**, not statistical noise). So W3 is a **genuine upstream pool characteristic**, in the same family as the Leg-2 W1/W3 *legacy* inherited FAILs — Step-5 merely amplifies it via the same thin-OBS-weekend mechanism. Its BEM impact is likely secondary to AT_HOME/AT_WORK **unless internal gains are explicitly modulated by colleague co-presence** (flag this to the user — it depends on the Step-7/BEM wiring choice).

## THE ONE DECISION THAT RETURNS TO THE USER — my firm recommendation: **(a) Accept + document**

- **(a) Accept + document [RECOMMENDED].** Reclassify 2.2 / W1 / W3 to **documented-inherited** with the P1/P2/P3 evidence + paper-ready caveats. Rationale: 2.2/W1 are unambiguously benign Step-5 frame-composition artifacts (SYN≈OBS pre-match, sub-gate daily-means); W3 is a genuine *upstream pool* property that **reopening Step-4 would not be the correct lever for** (it's a pool characteristic consistent with the Leg-2 legacy W1/W3 handling, and Step-4 is paper-ready with 0 model defects). Document W3's 16:30 weekday divergence honestly as a known limitation, not as "noise."
- **(b) Reopen the closed Step-4** — **NOT recommended.** Diagnostic 2 shows 2.2/W1 are *not* fidelity losses at all, and W3's genuine part is a pool-composition property (thin OBS-weekend) that a Step-4 re-rake would not obviously fix. Reopening is expensive and returns cost/schedule to the user for little expected gain. Only pursue if the user judges the W3 16:30 divergence paper-critical AND wants to chase a thin-stratum re-weight upstream.

**Present the table + this recommendation to the user and let them pick (a)/(b). Do NOT touch any code or re-run anything until they decide.**

## AFTER THE USER DECIDES — batch ALL fixes into ONE final chain re-run

Once (a)/(b) is settled, hand a single employee prompt that applies every agreed fix together, then re-runs the whole local chain once:
1. **LFTAG census-side `99 → NaN`** harmonization (archive predecessor first; assert the other keys byte-identical after — `np.array_equal`).
2. **R1 → WARN/documented** with the tier-split evidence baked into the validator's rationale text (not a threshold change).
3. **PR=6 → accepted frame gap**, documented in Section 0 rationale (like OW5).
4. **Cluster C** per the user's (a)/(b) choice.
Then: `--smoke` → validator `--smoke` → `--full` → `--aggregate` → `--bem` → `--exclusion` → validator. Target **0 new FAIL** beyond documented-inherited.

## THEN CLOSE STEP 5
- Append the Step-5 Progress Log with the **re-derived frame counts of record** (from THIS run's own `Full_Aggregated` — compare HH-ID **sets** not counts; verify the aggregate came from the same run's `Full_Schedules`), plus the CMA-harmonization + tier-regime notes and the Cluster-A/B/C dispositions.
- Update auto-memory `project_3j_leg3_4split_status.md` at closure.
- **Report to the user before Step 6 — do NOT auto-advance.**

## OPEN / FLAGGED (carry forward, not blocking)
- **Step-4 report surfacing (unanswered):** whether to copy/rename `Step4_docs/outputs_step4/sweep/seed_3_raked3_mindwell_actv/step4_validation_report.{html,txt}` (149P/16W/1F, sole FAIL OW5) to a surface `_4split` name, or leave as-is. The user's first message this cycle wrongly believed it was missing — it exists. Confirm with the user, low priority.
- **Cross-leg comparability (flagged, not decided):** Leg-2 carries the same CMA/tier-inert condition (0% CMA overlap → 100% Tier-2). Re-running Leg-2 with the CMA harmonization for apples-to-apples is a *separate* decision — raise only if the user wants cross-leg parity in the paper.
- **Memory candidate:** the "CMA was mislabelled as LUC_RST / gate-statistic-is-SYN-vs-OBS-within-matched-frame" correction is worth a `reference` memory once Step 5 closes.

## STANDING DISCIPLINES (enforce in every employee prompt — Leg-2 lessons)
1. **Frame discipline — re-derive, never assume.** Never bake Leg-2 constants (23,150 / 29,538 / 735). Every frame count from THIS run's own outputs.
2. **Compare SETS, not counts** for any cross-run frame comparison.
3. **Byte-identity guard** (`np.array_equal`) after any stage touching one channel — the other channels must be unchanged.
4. **Pool provenance:** Leg-3 locked pool only (`…/seed_3_raked3_mindwell_actv/augmented_diaries.csv`, with `ret30_*`), never the Leg-2 pool; md5 recorded.
5. **Verify from the artifact, not the log** — re-derive every load-bearing number from the file's own columns.
6. **Never relax a gate to clear a FAIL** — relabel + document with evidence.
7. **Cost:** scp / log-tail / big-file scans / monitoring → Haiku/Sonnet employees, never Opus. Never scan the 399 MB pool in your own context.
8. **Archive predecessor before any edit**; new outputs to new dirs, never overwrite pipeline output dirs.
9. **User checkpoints:** decision-level trade-offs → stop and ask. Append-only Progress Logs; "Step 5 NOT done" until the validator signs off at 0 new FAIL (or documented WARN/INFO).

Bonne exécution.

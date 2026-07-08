# Step 8 — End-Use Heating/Cooling Dominance: Path to Submission-Grade Validation

**Authored:** 2026-07-08 · **Status:** PLANNING — advisory only, no code/paper changes made by this doc
**Companions:** `investigation/step8_resid_heating_cooling_dominance_investigation.md` (root-cause
trace, §7 = current fix), `investigation/step8_enduse_rebase_implementation_plan.md` (the
subset-based execution just completed, incl. Progress Log with full numbers)

## 0. Where things stand today (honest summary)

The 2026-07-08 pass (`step8_enduse_rebase_implementation_plan.md`, phases 2JV3-A…F) proved the
following on a **600-run 2022 subset** (CZ 6A/6B/7A × 4 archetypes × 50 samples, extracted from
`eplustbl.csv` on cluster scratch, zero sbatch):

- Gate 4.9 (true end-use energy: cooling electricity ÷ heating fuel) **PASSes** for every
  archetype × CZ tested, with ratios 0.14×–0.40× — all well under both the 1.25× WARN and 2.0×
  FAIL thresholds.
- This confirms the apartment "cooling ≥ heating" signal visible in the old
  `:EnergyTransfer`-based §4 chart is a **metering artifact** (thermostat-independent ERV
  ventilation air counted as cooling in winter), not a template or physics defect. The 6,000
  existing runs and the underlying IDFs were never touched and remain valid.
- Extraction was hand-verified against raw `eplustbl.csv` for both unit families (GJ apartment,
  kBtu house) — exact match.
- The merged local report (`step8_validation_report_v3_merged.html`) is internally consistent:
  non-§4 sections are byte-identical to the canonical report, and the canonical report itself was
  never modified (md5-verified before/after every regeneration).

**This is real evidence, but it is not yet the canonical, submission-grade validation**, for two
reasons stated plainly:

1. **Scope.** The subset covers 1 of 5 campaign years (2022) and 3 of 6 climate zones (the coldest
   three, chosen because they're where the artifact is most visible). It does not speak to
   2005/2010/2015/2030 or to 5A/5B/5C. There is no reason to expect a different result there — the
   ERV mechanism is a static template property, not a scenario-dependent one — but "no reason to
   expect different" is not the same as "checked."
2. **Extraction path.** The local run used the `eplustbl.csv` text-table parser
   (`extract_enduse_annual_from_tbl.py`) because cluster compute (not just login-node file access)
   was unavailable. The canonical path is the `eplusout.sql` sqlite extractor
   (`extract_enduse_annual.py`, already ported and sitting ready in
   `outputs_step8/investigation/`) run via `sbatch` over all 6,000 runs. The two paths were
   cross-validated identical on the 3J precedent (same MidRise sample_001 2022 values from both),
   so this is a low-risk gap, but it hasn't been re-proven on 2J's own full campaign.

## 1. Does `readySubmission.md` need this at all?

Worth stating clearly before planning further work: **as of today, `readySubmission.md` makes no
heating-vs-cooling-dominance claim.** Table 5 and §5.2 report *total site EUI* against SHEU bands;
the binding calibration gate cited in the paper (§5.4) is the per-household end-use comparison for
equipment/lighting, not a heating/cooling split. §7 (Limitations) already discloses the single
frozen Zone-6 envelope and argues the paired design cancels its effect on the behavioural signal.

So this validation work is currently **internal QA**, not something the paper is missing. Two
honest paths forward — this is a decision for you, not something I should decide unilaterally:

- **Path A — keep it as QA/reviewer-response material.** Do nothing to the paper text. Keep the
  validated subset report and (once done) the full-campaign regen as backup evidence in case a
  reviewer asks why supplementary EUI figures look the way they do, or questions the physical
  plausibility of the apartment archetypes. Lowest effort, zero paper risk.
- **Path B — add a brief plausibility statement.** A one-sentence addition to §5.2 or a short
  clause in §7's existing envelope-limitation paragraph, e.g. noting that end-use-resolved
  heating/cooling ratios were checked and found physically plausible (citing the gate), with the
  residual cooling-heaviness in 6A/6B (still ≤0.40×, well under 1×, but not zero) attributed to the
  fixed Zone-6 prototype envelope + ERV heat recovery — same root cause already disclosed for EUI
  magnitude in §7. This makes the paper's physical-plausibility story slightly more complete and
  pre-empts a plausible reviewer question, at the cost of one more claim to defend.

**My recommendation:** Path A now, revisit Path B only after the full-campaign canonical regen
(§2 below) — a paper claim should cite the 6,000-run canonical number, not the 600-run subset.

## 2. What "submission-grade" would require

Sequenced, cheapest/lowest-risk first:

### Step A — Full-campaign canonical extraction (blocked on cluster compute)
- Run `outputs_step8/investigation/extract_enduse_annual.py` (sqlite path, already ported and
  ready) via `sbatch` over the full `SimResults_Step8_corrected_v2/campaign_N50` (6,000 runs, all
  5 years, all 6 CZ). **Do not run this on the login node** — single `sbatch` job, 7-day walltime
  floor per the cluster hard rules, e.g.:
  `sbatch -p ps --mem=16G -t 7-00:00:00 --wrap "cd .../outputs_step8/investigation && /path/python extract_enduse_annual.py > extract.out"`
  with `STEP8_CAMP_DIR` pointed at the campaign root and `STEP8_ENDUSE_OUT` at
  `outputs_step8/agg/agg_enduse_annual.csv` (replacing the subset file with the full one).
- Expected size: 6,000 rows vs today's 600. Runtime should be modest (sqlite reads, not E+ runs)
  but pad the walltime request anyway per the cluster policy.
- **Sequencing note (per the existing decision gate in the investigation doc, §5):** run this
  *after* the 3J canonical full-campaign regen, which re-verifies the same extractor logic at
  scale first. Check the 3J investigation doc's Progress Log for that regen's completion before
  starting this one.

### Step B — Full-campaign validator run
- Once Step A's `agg_enduse_annual.csv` covers all 6,000 runs, re-run `08_simulation_val.py`
  **without** `--section` (full 8-section pass) via `sbatch`, exactly as `step8_aggval_v2.sh`
  already does — gate 4.9/4.10 will now evaluate against the full dataset automatically (no code
  change needed; the gate already reads whatever `agg_enduse_annual.csv` contains).
- This is the run that is allowed to overwrite the canonical `step8_validation_report.html` — every
  local/subset run this pass deliberately avoided touching it.

### Step C — Widen the gate's scope (optional, cheap, can be decided at Step B time)
- Gate 4.9 currently limits its FAIL/WARN evaluation to CZ 6A/6B/7A (the coldest zones, where the
  artifact is expected to matter). Once the full dataset is available, consider either (i) leaving
  the threshold CZs as-is but adding 5A/5B/5C to the reported ratio table for completeness, or
  (ii) extending gate 4.9 itself to all 6 CZs and all 5 years if you want a stronger, all-scenario
  claim. This is a validator edit, not a data problem — flag it explicitly if you want it before
  Step B runs, since it's cheaper to change the gate once than to re-run the full validator twice.

### Step D — Decide Path A vs B (§1) using the canonical numbers
- Once Step B's canonical gate 4.9 result is in hand, revisit §1 above with real full-campaign
  numbers rather than the subset. If the ratios hold at the subset's ≤0.40× level across the full
  campaign, Path B becomes a very low-risk addition (strong, clean evidence). If any CZ/year
  combination surprises you (e.g., a WARN somewhere the subset didn't test), that's exactly the
  kind of finding worth catching before submission, not after.

## 3. Acceptance criteria (test method)

Submission-grade means, concretely:
1. `agg_enduse_annual.csv` has 6,000 rows (or the full row count for whatever scope Step C settles
   on), covering all 5 years and all 6 CZ.
2. `08_simulation_val.py` full run (no `--section`) completes with gate 4.9 reporting a status
   (PASS/WARN/FAIL) for the full dataset, and the canonical `step8_validation_report.html` is
   regenerated from it (this is the one run in this whole chain allowed to overwrite that file).
3. A hand-check on 2 additional full-campaign files (ideally one from a year/CZ combination not
   already spot-checked in the 2026-07-08 pass, e.g. 2030 or CZ 5A) confirms the sqlite extractor
   still matches the tbl.csv values, closing the "extraction path" gap noted in §0.
4. If Path B is chosen: the paper addition is a single sentence/clause, reviewed against the
   canonical numbers, not the subset numbers.

## 4. What this doc is *not*

This is a planning document only. It does not modify `08_simulation_val.py`, the extractor
scripts, or `readySubmission.md`. Step A requires cluster compute and is explicitly blocked until
Speed is back and the 3J canonical regen has gone first, per the existing sequencing decision. No
action is expected until you return to this.

---

## Progress Log

| Date | Action | Status | Notes |
|------|--------|--------|-------|
| 2026-07-08 | Roadmap authored (employee, on request) | PLANNING — awaiting user decision on Path A vs B and on Step C's gate scope, and awaiting cluster availability for Step A | Written after the subset-based 2JV3-A…F pass (gate 4.9 PASS, 0 FAIL) and two follow-up UX fixes (chart captions, chart-1 recoloring) to the merged report. No code or paper files touched by this doc. |

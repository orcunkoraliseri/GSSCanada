# Director-session prompt — Step-4 improvements: confirm, then plan implementation

**How to use:** open a fresh **Fable** session as the *director/manager* and paste the block below verbatim.
It is self-contained (the new session has none of our chat history).

---

```
ROLE: You are the DIRECTOR (manager) for this session. Model: Fable. Do ANALYSIS + PLANNING only —
do NOT modify pipeline source and do NOT run heavy compute in this session. You produce two documents.

CONTEXT
The Step-4 deliverable (calibrated J3 occupancy model) is validated and shipped. A follow-up notes file
lists 3 planned improvements. Your job: (Phase 1) confirm each improvement against the validation report
and the code, then (Phase 2) write an implementation plan for the confirmed set.

INPUTS TO READ (local, Windows — use `py`, not `python`):
- Improvements doc:  2J_docs_occ_nTemp/outputs_step4/step4_improvement_notes.md
- Validation report: 2J_docs_occ_nTemp/outputs_step4/step4_validation_report_v5.html
    NOTE: ~355 KB with base64 images (huge lines). Read the TEXT only by stripping them first, e.g.:
    sed -E 's/data:image[^"]*/[IMG]/g' file.html | sed -E 's/<[^>]+>/ /g' | tr '>' '\n'
    Sections of interest: 2, 3, 6, 7, 9; the boxes "Why calibration adjusts only hom30" and
    "Would raking all three heads improve BEM performance?"; "Known Limitations".
- Supporting code (read as needed, do not edit):
    2J_docs_occ_nTemp/05_postlink_rake.py            (current hom30-only rake)
    2J_docs_occ_nTemp/activity_loads.py              (Step-9 equipment/lighting from act30 + SHEU calib)
    2J_docs_occ_nTemp/07_aug_to_bem.py               (Metabolic_Rate from act30; occupancy from hom30)
    eSim_occ_utils/25CEN22GSS_classification/05_census_linkage.py  (MATCH_KEYS + Tier 1-4 sets)
    2J_docs_occ_nTemp/outputs_step4/_gen_v5_plots.py (report figure generator; base64 embed)
    2J_docs_occ_nTemp/04F_validation.py              (validator/gates)

THE 3 IMPROVEMENTS (per the notes doc):
  1. Joint 3-head calibration (act30 + hom30 + cop30) — also closes gate 6.2 via LFTAG conditioning,
     Section-2 activity fidelity, cop30 per-cell-slot (19.85 pp), and reduces coherence cost (~1.8-2.1%).
  2. 2005 `PR` census-linkage gap — 2005 PR left in legacy 5-region coding (1-5), disjoint from Census
     SGC (10..59); PR is in Tier-1 AND Tier-2, so 2005 falls to Tier-3/4, ~3x under-weighted.
  3. Visualize key findings in the report — add base64 figures, trim dense text.

KEY NUMBERS TO VERIFY (confirm from report/code; flag any mismatch):
  - 2005 census-linkage: pool supply 30.0% -> Tier-1 expected 0.0% -> final matched ~9.0%.
  - act30 -> BEM: metabolic gap +1.9%; equipment shape mean 14.9% / peak 32%; lighting 3.8 pp.
    Annual kWh is SHEU-fixed (levels absorbed); only shape/timing moves with act30.
  - gate 6.2 Work-proxy = 3.27 pp (expected-FAIL); activity JS = 0.0191 (PASS, <=0.05).
  - Spouse marginal PASS 2.23 pp; raw per-cell-slot COP max 19.85 pp; coherence cost ~1.8-2.1%.

PHASE 1 — CONFIRM (read-only). For EACH improvement, decide CONFIRM / ADJUST / REJECT with reasons:
  (a) Is the problem real and supported by the report's sections/numbers and the code?
  (b) Is scope correct — nothing missing, no redundancy/overlap between improvements?
  (c) Is the approach (Option A vs B) sound & feasible? Recommend one, with why.
  (d) Priority + dependencies (which unblocks which; what is safe to parallelize).
  (e) Resolve the Open Decisions (OD-*) where the evidence allows; list the rest as questions for the user.
  Deliverable: a CONFIRMATION MEMO (short, per-improvement verdict + rationale + resolved/blocking ODs).

PHASE 2 — IMPLEMENTATION PLAN (only for CONFIRMED/ADJUSTED items). For each, in repo task format
(aim / steps / expected result / test method), specify:
  - exact files & functions to touch, data inputs, new flags (keep current behavior as fallback);
  - the gates that must still PASS (21/1/0 baseline) and the new/target gates;
  - rollback / predecessor-archive note; and an ordered EXECUTION SEQUENCE across the improvements.
  Deliverable: an IMPLEMENTATION PLAN document.

WRITE DELIVERABLES TO:
  - 2J_docs_occ_nTemp/outputs_step4/improvement_planning/step4_improvements_confirmation.md
  - 2J_docs_occ_nTemp/outputs_step4/improvement_planning/step4_improvements_implementation.md
  (create the improvement_planning/ subfolder; keep outputs_step4 top-level uncluttered.)

CONSTRAINTS:
  - Plan only — do NOT edit pipeline source or the report in this session.
  - Local Windows: call Python via `py`; for large CSVs (augmented_diaries.csv 530 MB) chunk-read with a
    memory guard — never load whole. Do not delete/move anything.
  - Preserve documented facts (2005 PR, SHEU level-calibration, coherence, BEM-harmless via hom30).
  - Be concise; end each deliverable with a Progress Log line dated today.
```

---

### Notes for me (author)
- Keep the block above in sync with `step4_improvement_notes.md` if the improvement set changes.
- The director's two outputs land in `outputs_step4/improvement_planning/` to keep the top level clean.

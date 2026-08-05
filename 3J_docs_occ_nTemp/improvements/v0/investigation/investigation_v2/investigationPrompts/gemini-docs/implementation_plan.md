# Independent Backward Audit — 3J Leg-3 Occupancy Pipeline Plan

Audit of the research pipeline producing results for 3J Leg-3 four-channel occupancy pipeline and tracing claims back to their sources and to the submitted 2J paper.

## User Review Required

> [!IMPORTANT]
> **Blindness Protocol Enforcement**:
> In strict accordance with Section 1 of `PROMPT_gemini_backward_audit.md`, all files under `3J_docs_occ_nTemp/improvements/investigation/` are strictly excluded from reading except for `PROMPT_gemini_backward_audit.md`. In addition, contaminated passages in `3rdJ_L3_improvements_step9.md` (§0.21.4) and `3rdJ_L3_step9_READER_GUIDE.md` (§1.4, §2) will be avoided during audit inspection.

## Proposed Audit Strategy

### 1. Document & Claim Register Ingestion
- Read the two entry documents completely:
  - `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md`
  - `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md`
- Build a comprehensive register of every quantitative constant, attribution, external benchmark/band, frame count, and design property.
- Read `2J_docs_occ_nTemp/writing/fullSet/readySubmission.md` to trace claims reaching the submitted paper.

### 2. Primary Source & Attributed Evidence Tracing
- Open primary sources and deepResearch reports (`dr_L3-01` through `dr_L3-13`, `deepResearch_v2`) to verify if cited constants, standards (NECB 2020, ASHRAE 90.1, Richardson et al.), and benchmark bands match what design docs claim.
- Verify denominator alignment (e.g. per-person vs per-area, gross vs net).

### 3. Cross-Document Consistency & Inheritance Sweep
- Execute POSIX bash search commands to audit frame counts, densities, peak fractions, power densities, area constants, and thresholds across `Leg3_4-split`, `Leg2_2-split`, and `improvements/`.
- Trace inherited assumptions from Leg 1 and Leg 2.

### 4. Validation Gate & Code Artefact Verification
- Audit step design docs and validation reports (`Step1_docs` through `Step9_docs`).
- Compare promised validation gates against actual implementation in python code and validation logs.
- Audit status of `OPEN DECISIONS` sections in entry docs.

### 5. Report Compilation
- Generate the single deliverable artifact at:
  `3J_docs_occ_nTemp/improvements/investigation/investigationPrompts/REPORT_gemini_backward_audit.md`
- Include the blindness declaration, method/limits, verdict summary & severity table (G-1, G-2...), claim register, detailed findings with falsifiers and recommended actions, document contradictions, sound findings, unopenable citations, open questions, and ordered recommended work.

## Verification Plan

### Manual Verification
- Verify that no excluded files under `improvements/investigation/` were opened.
- Verify that every claim and finding in `REPORT_gemini_backward_audit.md` includes exact `path:line` citations.
- Confirm all required sections of the prompt deliverable format are complete.

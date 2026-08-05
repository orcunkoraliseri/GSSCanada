# Independent Backward Audit Walkthrough — 3J Leg-3 Occupancy Pipeline

The independent backward audit of the **3J Leg-3 Four-Channel Occupancy Pipeline** (`Residential`, `Office`, `Retail`, `Hotel`) has been completed in full compliance with Section 1 (Blindness Protocol) and Section 3 (Standard of Evidence) of [`PROMPT_gemini_backward_audit.md`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/improvements/investigation/investigationPrompts/PROMPT_gemini_backward_audit.md).

## Deliverable Created

- **Audit Report**: [`REPORT_gemini_backward_audit.md`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/improvements/investigation/investigationPrompts/REPORT_gemini_backward_audit.md)

---

## Executive Summary of Findings

### 1. Blindness Protocol Compliance
- Checked and maintained strict isolation: opened **only** `PROMPT_gemini_backward_audit.md` under `improvements/investigation/`.
- Avoided all contaminated passages in `3rdJ_L3_improvements_step9.md` (§0.21.4) and `3rdJ_L3_step9_READER_GUIDE.md` (§1.4, §2).
- Declared zero contamination in the formal blindness declaration.

### 2. High-Impact Audit Findings

| Finding ID | Summary | Impact / Severity | Reaches Submitted 2J Paper? |
|---|---|---|---|
| **G-1** | **Floor Area & EUI Denominator Contradiction**: Body text in `3rdJ_00_4split_Occupancy_Pipeline.md` still cites legacy unparsed building areas (40,846 m² SuperTall / 26,750 m² Tall) instead of parsed model areas (135,857.6 m² SuperTall / 72,623.1 m² Tall), creating a 2.7–3.3× EUI denominator mismatch if used in text. | **High** | No (3J mixed-use tower) |
| **G-2** | **Hotel As-Modelled PASS Criterion Contradiction**: Defined PASS band `[180, 240, 300]` kWh/m²/yr is contradicted by PNNL Large Hotel prototype simulation data (`441.6 to 521.2` kWh/m²/yr). Standard Large Hotel models would automatically fail this gate. | **High** | No (Leg 3 Hotel) |
| **G-3** | **Non-Existent StatCan Citation**: Citations to Statistics Canada Table `24-10-0048-01` are non-existent; hotel occupancy data actually relies on ISQ and CBRE/Travel Alberta. | **Medium** | No (Leg 3 Hotel) |
| **G-4** | **Zero Intra-Household Presence Diversity**: Scaling single respondent presence by `HHSIZE` (`Number_of_People = HHSIZE × AT_HOME`) assumes 100% synchronized household presence. | **High** | **YES** (`readySubmission.md`) |
| **G-5** | **"4-Head Transformer" Diagram Shorthand**: Diagrams label engine as 4-head Transformer, but implementation is 3 GSS heads + 1 SARIMA Hotel side-track. | **Low** | No |
| **G-6** | **Service/MEP Area Prorating**: Prorating core MEP energy strictly by floor area distorts tenant EUI load-timing. | **Medium** | No |

---

## Recommended Priority Actions

1. **2J Paper Limitation Update**: Add a paragraph in [`readySubmission.md`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/2J_docs_occ_nTemp/writing/fullSet/readySubmission.md) acknowledging single-respondent `HHSIZE × AT_HOME` assumption of zero intra-household presence diversity (Finding **G-4**).
2. **Floor Area Constants Fix**: Update lines 320 & 125 in [`3rdJ_00_4split_Occupancy_Pipeline.md`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md) to parsed area values (`135,857.6 m²` / `72,623.1 m²`) (Finding **G-1**).
3. **StatCan Hotel Table Citation Purge**: Replace `Table 24-10-0048-01` references with ISQ & CBRE/Travel Alberta citations across documentation (Finding **G-3**).
4. **Hotel PASS Criterion Re-specification**: Update [`dr_L3-03`](file:///C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split/deepResearch/dr_L3-03_hotel_eui_bands_REPORT.md) to split PASS bands by Small Hotel vs Large Hotel prototype size (Finding **G-2**).

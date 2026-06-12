# IMP.md — Manuscript QA Audit & Improvement Log

**Date:** 2026-06-11 (night session)
**Target file:** `2J_full_manuscript.md` (CANONICAL working document, 655 lines, ~16.7k words)
**Process:** Manager (Opus) triaged; 4 parallel Sonnet auditors (read-only) + 1 Sonnet fixer executed.
**Scope:** Full cross-check of the canonical manuscript against the 9 stale `chapters/` sources + a whole-document internal-consistency pass (cross-references, number consistency, figure embeds vs disk, markdown/encoding hygiene).

> ⚠ Reminder: `fullSet/2J_full_manuscript.md` is canonical. The `chapters/` files are stale archives. **Never run `assemble.ps1`** — it would regenerate from the stale chapters and wipe all of this work.

---

## 1. Audit setup

| Auditor | Scope | Result |
|---|---|---|
| A | Front Matter + §1 + §2 vs Ch00/01/02 + Tables 1–2 | 1 bug, 1 anomaly, 2 minor, 4 info |
| B | §3 + §4 vs Ch03/04 + Tables 3–4 | 1 bug, 2 minor; no prose lost, tables cell-exact |
| C | §5–§8 + Appendix vs Ch05–08 + Table 5 | 1 candidate bug (rejected, see §4), 3 anomalies, 3 minor; all 27 ground-truth numbers PASS |
| D | Whole-doc internal consistency + disk | 2 bugs, 4 anomalies; 16/16 figure embeds resolve; 0 mojibake |

No content was lost in the chapters→fullSet inversion. No encoding damage anywhere (± – — × → é ² σ Δ all intact). All tables match their standalone source files cell-for-cell.

---

## 2. Fixes applied to `2J_full_manuscript.md` (12 edits)

| # | Location | What was wrong | Fix applied |
|---|---|---|---|
| 1 | Table 2 note (~L240) | **Internal contradiction:** note said DDAY_STRATA "collapse from 84 to 7" while §2.1/§3.1 state THREE day-type strata. | Verified against `02_harmonizationGSS.md` + `00_GSS_Occupancy_Pipeline.md`: 84 = DDAY × SURVMNTH → 7 = DDAY-only is the *data* collapse; the 3 day-types are the *separate* cross-cycle pooling. Note rewritten to state both, citing §3.1. Evidence-backed, not guessed. |
| 2 | §3.6 (~L369) | **Broken promise:** "The single WARN and the three INFO items are documented in §5.4" — §5.4 never documents them. | Removed the false §5.4 pointer; sentence now states only that they do not affect the load-shape metrics. |
| 3 | §3.6 (~L367) | Deviation "R1" referenced but never locatable from the manuscript. | Now reads "deviation R1 (SI Appendix D)" — verified R1 exists in `tables/SI/Appendix_D_deviations.md`. |
| 4 | Table 4 (~L455/464) | `## Section A` / `## Section B` were h2 headings inside a `###` subsection — corrupted the document outline. | Converted to bold text lines (table sub-blocks, not sections). |
| 5 | §4.2 (~L439) | Overstated pointer: episode "discussed as an illustration of campaign validation rigour in §7" — §7 carries only one sentence; the rigour lesson actually lives in §6. | Re-pointed: lesson drawn in §6, noted among limitations in §7. |
| 6 | §5.4 (~L578) | After consolidating the 4-hour-bug story into §4, Results had no provenance pointer for the timing numbers. | Appended one sentence: "All timing results in this section derive from the corrected, fully re-simulated campaigns (§4.2)." |
| 7 | §5.2 (~L536) | "(Tables 3.3a/3.3b; …)" readable as manuscript tables. | Prefixed: "(SHEU Tables 3.3a/3.3b; …)". |
| 8 | §6 (~L586) | "+7.9 % residential increase" lost the word "electricity" in the Discussion collapse (Cicala figure is electricity-specific). | → "residential electricity increase". |
| 9 | §7 (~L592) | Collapse softened a factual claim: "a raking facility could anchor" (chapter asserted it **exists**; 04L raking is built and proven). | → "exists and could anchor". |
| 10 | Table 1 sources (~L104) | de Wilde (2014) cited with truncated title, inconsistent with §1.1 ref list. | Harmonized to full form: "…: A framework for investigation", "pp. 40–49". |
| 11 | §4.3 footnote (~L481) | EUI unit "kWh/m²" inconsistent with §4.4 body "kWh/m²·yr". | → "kWh/m²·yr". |
| 12 | §3 intro (~L291) + cosmetics | "in the Appendices" (document has one Appendix); double blank lines at ~L113–115 and ~L242–243. | "Appendix"; blanks collapsed. (Figure 6 caption spacing was already correct — skipped.) |

**Post-fix verification:** 16/16 image embeds resolve to existing PNGs, paths unchanged · 0 mojibake hits (`â€`, `Â±`, `Ã©`) · `## Section` and `documented in §5.4` no longer appear · special characters intact around every edit · all repeated quantities consistent across sections (~27 ground-truth values re-checked, all PASS).

---

## 3. Confirmed clean (no action needed)

- All headline numbers consistent everywhere they recur: 64,061 / ~192,183 / 286,537 / 144,507 / 6,000 / 37,008; +6.1 agg / +6.6 raw-wkdy / +5.2 standardized (correctly distinguished at every occurrence); +2.2–3.9 pp; +1.4–2.6 % / +0.6–1.2 %; +0.367 pp [+0.208, +0.526]; +0.0117 [+0.0085, +0.0150]; 17.5–17.7 h / ~17:30; 0 ± 1 h (−0.12 h, σ 0.39); ±2.7 % (48/48, +2.33/+2.63); EUIs 208/152/128/117; SHEU targets 3,700/3,139/2,166/1,922 + 1,262/1,100/736/736; scorecards 24/0/3/0, 29 & 28 PASS, 35/35, 6/1/3/0; tiers 44.94/21.39/33.67/0.00; 4,800/4,795; 1.80 %/4.04 %; +2.85 %.
- Figure numbering: main 1–7 embedded once each, in order; S1–S9 once each, in order; no stale numbers (8–12, S10–S15) referenced anywhere.
- §8 Conclusion is verbatim-identical to its chapter source. Tables 1–5 cell-exact vs standalone files. No orphaned citation fragments in the collapsed §6/§7.

**Rejected false positive (do NOT "fix"):** an auditor flagged "OtherDwelling × Kelowna 5B × **2010**" (8G DX-coil fix) as an impossible year. It is correct — the Step-8 campaign spans 5 cycle-years (2005/2010/2015/2022/2030); the auditor confused it with the 48-cell, 2-year Step-9 grid.

**Known and deliberately left:** ~19 stale/orphan PNGs on disk (pre-rename originals + uncited SI figures — journal-not-report rule); `AT\_HOME` escape style varies between captions (harmless in all renderers).

---

## 4. Pre-submission checklist (inventoried, intentionally NOT touched — gated on your decisions)

| # | Lines (approx) | Item |
|---|---|---|
| SR-1 | 11 | Abstract structure/word-count note — remove at submission; trim abstract to journal limit |
| SR-2 | 23 | Highlights note ("5 bullets ≤85 chars…") — remove |
| SR-3 | 37, 41, 55 | **[confirm]** department/institute · both ORCIDs · CRediT split |
| SR-4 | 59 | Front-matter author-note block (references `resources/…`) — remove |
| SR-5 | 97–113 | Table 1 note + "Sources for matrix rows" + "Removed:" note — fold into standard refs |
| SR-6 | various | "(DR-verified June 2026)", "(verify against master bibliography)", "(not in DR scope)" flags — resolve/remove |
| SR-7 | 548–553 | Table 5 notes: internal job IDs (953111/954135/954296/954300), "manager-verified" dates — remove |
| SR-8 | 549–550 | Two internal `deepResearch/…` file-path citations — remove |
| SR-9–12 | 149–204, 269–287, 373–396, 494–510 | Four per-chapter "References (this chapter)" blocks — consolidate into one master bibliography in the target journal's style |
| SR-13 | 392–394 | Yamaguchi & Shimoda 2017 · Herrmann et al. 2024 · ASHRAE 55/ISO 7730 — complete citations |
| SR-14 | 102 | Chiou 2011 E&B extension — confirm DOI |
| SR-15 | 110, 189 | Yin et al. 2024 ASim — IBPSA proceedings DOI |
| SR-16 | 156–157 | Self-cites — final status/venue forms (JBPS under review; eSim 2026) |

**Open decisions (yours, in order):** 1) target journal (sets abstract limit, ref style, figure spec → unlocks SR-1, SR-9–12); 2) front-matter [confirm] items (SR-3); 3) bibliography reconciliation at typesetting (SR-5/6/13–16).

---

## 5. Submission-prep cycle (2026-06-12) — `readySubmission.md` created

Per author decision, SR-2 and SR-5–SR-16 were executed on a **copy**: `fullSet/readySubmission.md` (613 lines, ~15.5k words). `2J_full_manuscript.md` remains byte-identical (SHA-256 `E9DE8997…22B2C9` verified before/after every phase). Executed by 4 Sonnet employees (mechanical-removals fixer · citation researcher ×2 · bibliography builder + final verifier), manager-triaged.

**Done:**
- **SR-2** Highlights instructional note removed (bullets kept).
- **SR-6** All internal QA flags removed (12 instances: "DR-verified", "verify against master bibliography", "not in DR scope").
- **SR-7/8** Table 5 notes: SLURM job IDs (953111/954135/954296/954300), "manager-verified" dates, and both `deepResearch/…` path citations removed.
- **SR-16** Both self-citations (JBPS under-review + eSim 2026) deleted; 2 in-text cites rephrased (Table-1 footnote, §1.4); `[^selfdelta]` footnote untouched (descriptive prose, no citation marker).
- **SR-5 + SR-9–12** Four per-chapter ref blocks + Table-1 "Sources for matrix rows"/"Removed:" notes consolidated into ONE `## References` section (after §8, before Appendix): **59 entries**, alphabetical author–year, 20 dedup merges, 0 orphan in-text citations.
- **SR-13/14/15** Web-verified via CrossRef/primary sources (zero fabricated fields): Yamaguchi & Shimoda 2017 (JBPS 10(5–6), DOI confirmed) · Herrmann 2024 (JSHS 13(1), full 12-author list) · ASHRAE 55-2023 · ISO 7730:2005 full form · Chiou et al. 2011 DOI **10.1016/j.enbuild.2011.09.020** confirmed · **Yin et al. 2024: no DOI exists** (IBPSA ASim 2024 proceedings carry none) — cited via publications.ibpsa.org URL.
- **Bonus:** 8 further short-form entries completed and verified (Austin 2021, Sahoo 2024, Lou 2024 — true titles restored; Rässler 2002; D'Orazio 2006; Beckman 1996; Putra 2021; Gama 2014). Citation-key fix: Table-1 row "Chiou (2009)" → "Chiou et al. (2011)".

**Decisions taken (autonomous, reversible):**
- ISO 7730 cited as **2005 edition** (the edition the methods used; a 2025 edition now exists — journal may ask to update).
- 3 truly-uncited entries **removed** from References (full text preserved here if ever re-cited):
  - Pérez-Lombard, L., Ortiz, J. and Pout, C. (2008). A review on buildings energy consumption information. *Energy and Buildings*, 40(3), pp. 394–398. https://doi.org/10.1016/j.enbuild.2007.03.007.
  - Khalil, M.A. and Fatmi, M.R. (2022). How residential energy consumption has changed due to COVID-19 pandemic? An agent-based model. *Sustainable Cities and Society*, 81, 103832. https://doi.org/10.1016/j.scs.2022.103832.
  - Vellei, M. et al. (2022). Documenting occupant models for building performance simulation: a state-of-the-art. *Journal of Building Performance Simulation*, 15, pp. 634–655. https://doi.org/10.1080/19401493.2022.2061050.
- Minor flag for typesetting: Herrmann 2024 co-author given name "Zhenghua Cai" (CrossRef) vs "Zhenghui" (PubMed) — CrossRef form used.

**Final verification (readySubmission.md):** 0 mojibake · 0 leftover internal flags · exactly one `## References` · sane outline (Front Matter → §1–8 → References → Appendix) · 16/16 figure embeds resolve · special chars intact.

**Still open (yours):** SR-1 (abstract note + trim — needs target journal), SR-3 ([confirm] department/ORCIDs/CRediT), SR-4 (front-matter author-note block — not in your go-list, left in place), reference-style restyle once the journal is chosen.

---

*Audit + fixes executed by Sonnet employees, manager-triaged and spot-verified. The manuscript is internally consistent and content-complete; everything left on the list above is blocked only on the items requiring your input.*

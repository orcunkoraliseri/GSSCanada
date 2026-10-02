# AUTHOR_TODO_5J: what only the author can do before submission

Written 2026-10-01 from the first manuscript draft (`writing/5J_manuscript_draft.md`). State file with the number ledger: `Step8_docs/impl/2026-10-01_wp6_draft.md`.

## 0. 🔴 DECIDE FIRST (finding 5J-3, 2026-10-01 06:08; parent Progress Log)
The 5,200 generated diary days per country that every 5J household uses are, by the 4J design, Leave-One-Country-Out
generations: the Spanish pool very probably comes from the 4J model fine-tuned on the UK and Italian diaries, the Italian pool
from the model fine-tuned on Spain and the UK. Does EUL v16 clause 5 (no AI tool in connection with UK data) / clause 4 (derived
data) cover outputs of a model trained on UK diaries? (a) no: continue; (b) yes: ask UKDS in writing for what exists, and
regenerate the Spanish and Italian days from a generator trained without UK diaries before the paper. Recommend: write to UKDS;
keep all 5J outputs private until the answer. The draft's two UK sentences (Methods 2.1, Data availability) are replaced by
markers until you rule.
Help for this decision (2026-10-01 14:03): run `Prompts/deepResearch/T48_ukds_licence_derived_outputs.md` in Gemini (paste
the master brief and the response template first); it reads the licence, UKDS guidance on synthetic data and AI, the SN 8128
record and precedents, and lists yes/no questions for a UKDS email. I vet the answer.

## Before the word "first" or "to our knowledge" can be used
1. **Novelty search T46.** One logged search for (P1) an occupancy sequence as input of a learned simulation surrogate and (P4) time-use diaries feeding a learned energy model: either a narrow outside round (prompt under `Prompts/deepResearch/`, run by you, vetted by the manager) or your own Scopus / Web of Science search with the queries and hit counts saved. The draft contains none of the words "first", "novel", "to our knowledge", "for the first time", "unprecedented".
2. **Li, Bae and Im (2021) in full.** The draft says only what the abstract says (107 inputs, 4,000 runs, sensor errors). Get the ORNL report (osti.gov does not open from the manager's machine); then check what its 107 inputs are and update the Introduction and Table A.1 (its dashes).
3. **Works in the reference list that 5J has not opened.** Vosoughkhosravi et al. (2023) and Osman and Ouf (2021) are cited for the same point as in the 4J manuscript; open them or drop them. Westermann and Evins (2019), CityTFT (Dai et al., 2025) and Govindarajan et al. (2025) beyond its abstract are not cited because they were not opened.
4. **Reference fields.** Initials for He, Lee, Taylor, Firth, Lomas (2015); Dabirian, Alamatsaz, Eicker (2025); Li, Bae, Im (2021); the ASHRAE entry has no DOI. Check all entries against CrossRef (validation gate 2.2). **(2026-10-01 13:47) Prompt ready: `Prompts/deepResearch/T47_reference_support.md`** (checks all 17 entries field by field, finds the original sources for the methods named without one (temporal convolution network, Transformer, gradient boosting, ERA5, cluster bootstrap, HETUS guidelines, EnergyPlus 23.1, PyTorch), sources for 9 context sentences, the data credits and the ASHRAE 2014 clause). Run it alone; the manager vets the answer. **(14:17) DONE and vetted (`Prompts/deepResearch/VETTING_RT47.md`, MIXED): initials, one title and 7 method sources added to the draft. Left for you: third author of Iseri et al. 2026 (registry: Sinan Kalkan; draft: B.), the ISTAT title, online vs print years (Pan, Park, Dabirian), and open any context source you want to cite (the report's quotes are not usable as quotes).**

## Rules and sources
5. **ASHRAE Guideline 14, 2014 edition.** The bands (CV(RMSE) 30 %, NMBE 10 %, hourly) were read by the manager in the 2002 edition, clause 5.3.2.4 f, p. 18. Confirm the 2014 edition carries the same clause (a change would be a dated amendment, and the Methods text and the reference change).
6. **Lighting decision.** Lighting is not modelled (no Lights object in any run); the manuscript says so in Methods 2.1 and Limitations. Decide whether to leave it as a limitation or add a lighting load in a later campaign.
7. **Diary day pool and the UK licence.** Methods says every person-day comes from one pool of 5,200 generated days per country made by the preceding study's diary generator. Check which training data produced the Spanish and Italian pools. If the generator was trained on a corpus that includes UK data, UKDS clause 4 (derived or synthetic data not released to unregistered users) and the Data availability and Acknowledgements wording need your ruling. The draft says "No United Kingdom data were used" and cites no UK source.
8. **Licence wording.** INE credit line and ISTAT "changes made" wording are in the Acknowledgements. Re-read the ISTAT download conditions page (the conditions accepted at download were not saved).

## Results and figures
9. **Step 7 numbers.** DONE 2026-10-01 13:15: Section 3.8, Table 5 and Figure 5 filled from the closed Step 7 outputs; the Abstract and Conclusion carry the district.
10. **Bootstrap units.** The claim rule asks every interval to be printed with its number of building and household units, and to say "households only" where a cell holds one building. The draft states the rule and the single-building limitation; the per-cell counts are in `Step6_docs/outputs_step6/bootstrap_intervals.csv`, which the draft did not read. Add them to Table 3 or the supplement.
11. **Figure approval.** Figures 2 to 5 are drawn by script from frozen data and checked (Figure 5 on 2026-10-01 13:15). **Figure 1 (design) is a drawing for you to make: prompt `writing/submission/figures/Prompts_Images/5J_Figure_01_design_prompt.md`** (save as `writing/figures/Figure_01_design.png`). **Graphical abstract: section 10 of `Prompts/5thJ_graphical_abstract_prompt.md`** has the post-results update (UK removed, 9,269 runs, Panel C plotted from the Figure 3 data, finding sentence, "61 times faster on a GPU"). Every figure must cite its file and md5. **(14:17) Both made by your outside tool and checked: Figure 1 (md5 ee3a295c...) needs 2 small fixes, section 9 of its prompt; the graphical abstract needs 3 fixes, section 10.5 (main one: "a new country" becomes "both new").**
12. **A number to re-check.** `RESULTS.md` line 47 prints "S reproduces that share (73-97 %)". The three `reported_S_*.txt` files give 79 % to 98 % for S (EnergyPlus: 73 % to 98 %). The draft uses the file values. Manager to confirm.
13. **Venue (O-6).** Choose after the draft is read. The draft is laid out for Energy and Buildings (declarations, highlights, nomenclature, appendix table) in the 4J form; length is about 8,300 words of main text.

## Declarations
14. Sole author, no funding, AI declaration (Claude for analysis code and drafting assistance, Gemini for literature search reports, both checked by the author against the source records): confirm the wording before submission, and add model versions if the journal asks.
15. Code release: the Data availability says the code "is released with the paper"; give the repository or archive link.
16. Send UKDS nothing for this paper unless item 7 changes the answer.

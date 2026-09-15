# Response map: every reviewer request vs plan status

Built 2026-09-15 by T33 (WP10 prep). Source: `00_REVISION_PLAN.md` section 2 (the request table) and
section 3 WP10 (the new structure), plus the Status line and last Ledger/Decision lines of each task
doc in `impl/`. Paraphrases below are in plain words; no reviewer sentence is copied. Status values:
DONE, RUNNING (work started, not finished), WAITING (not started yet), DECLINED (a pre-registered rule
says we do not run this).

Columns: ID, plain paraphrase, class (A text / B re-derive a number / C new computation / D narrow a
claim / E rebuttal), what we change, where it lands in the new manuscript, which task(s) supply the
evidence, status, note.

## Reviewer 1

| ID | Plain paraphrase | Class | What we change | Where in new manuscript | Evidence task(s) | Status | Note |
|---|---|---|---|---|---|---|---|
| M1 | Compare our method against simple fixed schedules and average occupancy profiles. | C | Add two new simulation arms (fixed-schedule, average-profile) on the same households. | Results (new comparison subsection); Discussion (what the individual model adds). | T19, T22, T30 | RUNNING | Fixed-schedule arm (T22) about half done; average-profile arm (T30) array running. |
| M2a | Give one short diagram of the whole workflow. | A | New workflow figure, prompt only, author generates the image. | Opens Framework section (new Section 2). | none yet | WAITING | Image prompt not written yet (WP11 not started). |
| M2b | Spell out the math behind the main models and metrics. | A | Add an equations block. | Framework (Section 2). | T34 | RUNNING | T34 drafting the framework section with equations (manager correction). |
| M2c | Some passages in the middle read like results and should move. | A | Move gate scores and JS (similarity) scores out of the methods sections. | Results or Supplementary Information (SI). | this task (si_move_list.md) | WAITING | List is produced by this task; the actual move happens in WP10. |
| M2d | Explain how the 50-household samples are drawn and show that is enough. | B + C | Write the sampling method in words; add a subsampling curve; run one larger check. | Framework (sampling procedure); Results (sample-size check). | T05, T28 | RUNNING | T05 finished; T28's larger-sample array is submitted and running (manager correction, T28 doc line 242). |
| M3 | Simulated energy differs a lot from the SHEU reference; show the conclusions still hold. | B + C(optional) + D | Measure the gap end-use by end-use; stop calling the match "plausible". | Results (energy-use comparison); Limitations. | T07 | DONE | Optional envelope check (T31) is DECLINED by a rule fixed in advance (plan log (aq)): one needed input value (window rating) is not published anywhere, so it is not run; the end-use gap plus a stated limitation answers this instead. |
| M4 | Add more plots (occupancy, energy, load shape, peak, load factor) and cut repeated text. | A + B | New plots from data already computed; shorten prose. | Results; Figures. | none yet (data exists in T06, T15, T20, T26) | WAITING | Figures (WP11) and text cuts (WP10) not started. |
| M5 | Fig. 5's occupancy rise from 2022 to 2030 needs checking; test other work-from-home paths. | C | Fix the 2030 numbers, then run more than one future path. | Results (scenarios). | T20, T26, T29, T32 | RUNNING | 2030 base numbers fixed and closed (T20); scenario variants running/queued (T29, T32). |
| D1 | Show exactly which results need the household-level random model, not just averages. | C (via M1) + A | Answer using the M1 comparison. | Discussion. | T19, T22, T30 | RUNNING | Same evidence and state as M1. |
| D2 | Add our own earlier published work to the comparison table, not just other groups'. | A | Add rows for our prior papers to Table 1. | Introduction (Table 1). | none yet (needs dr_2J-10) | WAITING | Waiting on author to run the deep-research check `dr_2J-10`; also need to confirm the companion paper's publication status. |
| D3 | Define the model name "C-VAE" the first time it is used, not later. | A | Move the definition earlier. | Introduction. | T34 | WAITING | Listed as a jargon-inventory item (see jargon_inventory.md). |
| D4 | Explain the phrase "activity and end-use resolved" as soon as it appears. | A | Add a one-line definition. | Introduction. | T34 | WAITING | |
| D5 | State more clearly how our method differs from the Chen et al. (2022) study. | A | Add one explicit comparison paragraph. | Introduction. | none | WAITING | Needs a short literature read, not yet done. |
| D6 | Explain why the timing of energy use matters, and why 2030 is the target year. | A | Add a motivation paragraph. | Introduction. | dr_2J-11 (pending) | WAITING | 2030 tie-in needs an external source; author to run `dr_2J-11`. |
| D7 | Rewrite the contributions as clear scientific and practical statements. | A | Rewrite the contributions paragraph. | Introduction. | none | WAITING | |
| D8 | Add a table showing which dataset feeds which part of the framework. | A | New dataset-role table. | Framework (Section 2 opening). | T34 | WAITING | |
| D9 | Move the EnergyPlus simulation description out of the datasets section. | A | Relocate that text. | Framework. | T34 | WAITING | |
| D10 | Rename the modelling section to something like "proposed modelling and simulation framework". | A | Retitle Section 3 as Section 2. | Framework (title). | T34 | WAITING | New title already fixed in the plan (WP10 Structure). |
| D11 | Add formal definitions for the key modelling and aggregation steps. | A | Same work as M2b. | Framework. | T34 | WAITING | |
| D12 | Explain why modelling individual behaviour matters even for whole-stock (aggregate) results. | C (via M1) + A | Same evidence as M1, plus the existing household-level peak finding. | Discussion. | T19, T22, T30 | RUNNING | |
| D13 | Discuss that more at-home energy may mean less office energy, which we do not model. | A | Add one limitation paragraph on this system boundary. | Limitations (also flagged in Introduction). | none | WAITING | Needs one external source (not yet found). |
| D14 | Merge two sections that describe the same thing twice. | A | Merge the repeated schedule-integration description. | Framework (merge old 3.5 into old 4.2, or vice versa). | this task (si_move_list.md) | WAITING | Overlap identified and listed by this task; merge happens in WP10. |
| D15 | Add more figures and tables; there is too much text for too few visuals. | A + B | Same work as M4. | Results; Figures. | none yet | WAITING | |
| D16 | Re-check every number in the occupancy-change section against what the figure shows. | B | Re-derive each number from the current files. | Results (occupancy change). | T01, T11, T12, T20, T10 | DONE | Root cause found: the 2022 schedules used a four-cycle mix of diaries instead of only 2022 diaries; this is now fixed by the household-frame rebuild (T18/T20). |
| D17 | Same as M5: test alternative 2030 work-from-home paths, not only one trend. | C | Same work as M5. | Results (scenarios). | T20, T26, T29, T32 | RUNNING | |
| D18 | Fig. 6c shows little difference; break it down by end use and time of day. | B | New end-use-by-hour breakdown from existing simulation output. | Results (load shape). | T06 | DONE | |
| D19 | Make the load-shape, ramping, peak, and load-factor results more prominent; that is the real contribution. | A + B | Lead the Results with these metrics; add a ramp metric already in the paper's own code. | Results (reordered); Framework (metric definitions). | T06, T15, T20 | WAITING | Underlying numbers exist; the text reordering itself has not started. |
| D20 | Fig. 7 is too small and packed with information; split it into separate panels. | A | Split one figure into several. | Figures. | none yet | WAITING | Same status as R2-7. |

## Reviewer 2

| ID | Plain paraphrase | Class | What we change | Where in new manuscript | Evidence task(s) | Status | Note |
|---|---|---|---|---|---|---|---|
| R2-1 | The paper reads like an internal technical report; move QA and debugging detail to supplementary material, use plainer terms. | A | Move QA/debug content to SI; replace self-defined labels with plain words. | Throughout; SI. | this task (jargon_inventory.md, si_move_list.md) | RUNNING | This task is doing the mapping now; the actual rewrite is WP10. One sentence on the timing/clock check stays in the main text by plan (section 6). |
| R2-2 | Check the simulated hourly profiles against real measured household or area electricity data for a recent year. | C + external data | Compare against measured Ontario/Toronto hourly data. | Results (independent check); Limitations if narrowed further. | T02, T09, T15 | DONE | Counted as a partial measured check (plan's own special-case note): whole-building totals could not be split apples-to-apples, and the simulation calendar needed a day-of-week fix, both handled in T15. |
| R2-3 | Reconsider calling this a "forecast"; call it a scenario-based projection throughout. | A (accepted) | Replace "forecast" with "scenario-based projection" in title, abstract, and text. | Throughout (title, abstract, objectives, conclusion). | none yet | WAITING | 33 uses of "forecast" found in the old manuscript (see jargon_inventory.md); all to be replaced. |
| R2-4 | Rewrite the abstract in plain sentences, without symbols like +, plus/minus, approx, or delta. | A | Prose abstract. | Abstract. | none yet | WAITING | |
| R2-5 | Delete the paragraph that describes how the introduction itself is organized. | A | Delete that paragraph. | Introduction. | none yet | WAITING | |
| R2-6 | The SHEU agreement mainly shows the model was tuned to match it, not independent proof it is right. | A + D | Stop naming this "calibration closure"; do not call it independent validation. | Results/Methods. | T07 | WAITING | The exact phrase "calibration closure" was not found written in the old manuscript (0 hits); the framing itself still needs the rewrite. |
| R2-7 | Figures 6 and 7 are too small and hard to read. | A | Split/enlarge figures. | Figures. | none yet | WAITING | Same item as R1-D20. |

## Reviewer 3

| ID | Plain paraphrase | Class | What we change | Where in new manuscript | Evidence task(s) | Status | Note |
|---|---|---|---|---|---|---|---|
| R3-1 | Redo the 2030 numbers on the corrected household data and update every affected figure, interval, and conclusion. | C, critical path | Rebuild the 2022 stock, rebuild 2030 on top of it, rerun the full simulation campaign. | Throughout (Results, Abstract, Conclusion). | T18, T18b, T18c, T20, T21 | RUNNING | Household-frame rebuild and 2030 numbers are closed (T20); the full simulation rerun (T21) is submitted and running. |
| R3-2 | Run at least two 2030 paths (workers mostly stay home vs. partly return), or use much more careful wording. | C | Build three scenarios (stay-home, partial return, full return) on the rebuilt stock. | Results (scenarios, in the main body, not only Limitations). | T26, T29, T32 | RUNNING | Base scenario set built and scored (T26); step-8 simulation runs (T29) and one extra sensitivity variant (T32) are submitted. |
| R3-3 | Be careful to say "change linked to the pandemic/remote work" rather than claiming it was directly caused by them. | A + D | Replace causal wording; add one limitation naming other changes over the same period. | Throughout; Limitations. | none yet | WAITING | |
| R3-4 | Add at least a rough range of outcomes in the main results, not only at the end. | C | Same work as R3-2. | Results (main body). | T26, T29, T32 | RUNNING | |
| R3-5 | Separate "the model matches its own tuning target" from "independent evidence the model is plausible", clearly labelled. | A + C | Split into two labelled parts. | Results (two subsections). | T02, T09, T15 (independent check); T07 (tuning fit) | RUNNING | Underlying evidence for both parts exists; splitting the text into two subsections is WP10 work, not yet done. |
| R3-6 | Explain how the confidence intervals were built, and whether household clustering (same city/archetype) was accounted for. | B | Document the interval method; note it does not yet account for city/archetype clustering. | Framework (methods); SI (interval detail). | T03 | DONE | Found: a plain paired before/after interval over 1,200 households, not clustered by city or archetype; it does not reproduce the numbers printed in the old manuscript, so those numbers must be re-derived from the corrected data (see also T10). |
| R3-7 | Explain where the specific pass/fail thresholds come from, whether fixed before comparing models, and whether the choice changes under slightly different thresholds. | B (+ D if fixed after the fact) | Trace the thresholds; re-rank the stored trial scores under shifted thresholds. | Framework (model-selection description); SI (trial detail). | T04 | DONE | At the original thresholds four candidate models pass; the one used in the paper is chosen only because it has the best combined score, not because it is the only one that passes. Wording must say "chosen among four passing candidates," not "the only one that passed." |

## Manager check (plan log (at))
Counts re-measured by the manager: "forecast" 33 lines case-insensitive, "gate(s)" 19 lines as a whole word, "calibration closure" 0. Two stale cells corrected (M2b, M2d).

## Coverage check
42 rows above (Reviewer 1: 28, Reviewer 2: 7, Reviewer 3: 7), matching the plan's count in section 2.

## WHAT I DID NOT VERIFY
- Whether the companion C-VAE paper (D2) has changed publication status since the plan was written; the plan
  flags this as needing a check, this task did not check it (would require reading an outside manuscript).
- Whether `dr_2J-10` and `dr_2J-11` (deep-research prompts referenced for D2 and D6) have been run yet; the
  plan's last entry only says the author was asked to run them.
- Task docs T33 and T34 report their own current state as of this read; if another agent updates them later
  today, some Status/Note cells above may go stale.

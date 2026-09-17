# dr_2J-12 (Fable version) results: close-reading pre-submission review, no external search

**Run:** 2026-09-16, Claude Fable 5.1 inside Claude Code, no web access.
**Text reviewed:** `writing/submission/archive/2J_manuscript_submission.md` (the submitted manuscript, 653 lines, about 15,100 words, front matter through Appendix figure captions). This is the only complete manuscript on disk. The four partial redrafts in `rejection revision/manuscript/` (S2 framework, S7 limitations, two SI drafts) were NOT substituted in; findings below therefore describe the submitted text, and some may already be addressed by those drafts. Figure images and SI Tables A1 to A3, B1, B2 and Appendix D were not in the text and could not be read.
**Quotation convention:** the manuscript uses em and en dashes heavily. Inside quotations they are replaced by commas or the word "to" so this report contains none. Section pointers use the manuscript's own numbering; "para N" counts paragraphs from the top of the named subsection, ignoring captions and tables.
**Status:** UNVETTED deep-research return. Goes through the 7-step vetting before anything is acted on.

---

## 1. Verdict

**REJECT-LIKELY** as the text stands: the only load-shape statistics carrying confidence intervals measure the 2022 to 2030 transition, which contains no work-from-home break, yet the abstract, Fig. 6 caption, Discussion and Conclusion present them as the effect of that break; and the Results section itself declares its 2030 headline number provisional.

---

## 2. Argument map

**Central claim (one sentence).** Carrying a calibrated occupancy time-series through the COVID/work-from-home break to 2030 and running it through paired stock-scale EnergyPlus simulation shows that the break reshapes the Canadian residential diurnal load curve (midday fill, flatter load factor) while barely changing annual electricity and leaving the evening peak fixed near 17:30.

Sub-claims that must hold, with the supporting sentence and a sufficiency call.

**S1. The 2022 rise in at-home occupancy is behavioural, not compositional.** SUFFICIENT on its own terms.
Quote (§5.1 para 2): "once the 2005 to 2015 samples are standardized to a common demographic structure, the at-home series is essentially flat (64.2 / 64.2 / 63.3% across those three cycles). The 2022 jump, by contrast, survives standardization".
The standardization argument is coherent. It does not address collection-mode confounding (see 4.3 below), which is a separate sub-claim.

**S2. The 2022 rise is not an artefact of the survey-mode change.** INSUFFICIENT.
Quote (§7 para 7): "in any case the headline COVID break (+5.2 pp weekday at-home at 2015 to 2022) is far larger than any plausible mode effect and survives demographic standardization."
No basis for "any plausible mode effect" is given, and the mode indicator switches at the same cycle as the break (§2.1 para 2: "a binary indicator that marks the predominant-mode transition at 2022"), so the model cannot separate the two. See 4.3.

**S3. The break persists to 2030 at +2.2 to +3.9 pp.** INSUFFICIENT.
Quote (§5.1 para 1): "The forecast 2030 synthetic diaries carry the break forward at +2.2 to +3.9 pp above the pre-pandemic level ... this magnitude is provisional pending a calibration-provenance check described in §7."
Quote (§7 para 9): "the 2030 forecast is generated under a single scenario in which the work-from-home shift persists with probability one".
Persistence is an input assumption, not a result, and the magnitude is stated by the paper itself to be provisional and inflated (§7 para 5). Neither caveat reaches the abstract or highlights.

**S4. The generator reproduces the survey distributions well enough to synthesize the two unobserved day-types per respondent.** SUFFICIENT on its own terms, with one gap.
Quote (§3.2 para 3): "J3's gate scores are: activity JS 0.0191; AT_HOME RMS 4.57 pp; co-presence maximum gap approximately 2.03 pp; and composite score 0.6355."
The four gates are stated and met. The composite score is never defined, so one of the four gates cannot be interpreted by the reader.

**S5. The 2030 forecast is validated.** INSUFFICIENT.
Quote (Highlights): "2030 occupancy forecast through the COVID/WFH break, validated by True-Future-Test."
Quote (§3.4 para 4): "the model fine-tuned through 2015 and evaluated on the entirely unseen 2022 cycle, achieves a weekday JS divergence of 0.0619".
The True-Future-Test scores the 2015 to 2022 step. The 2030 cohort is produced by demographic resampling of the trained model (§3.4 para 3) and has, by construction, no test. The highlight claims a validation that the method cannot provide.

**S6. Diaries are attached to a representative dwelling stock.** PARTLY SUFFICIENT.
Quote (§3.3 para 2): "the match-tier distribution over the 286,537 agents is 44.94% at Tier 1, 21.39% at Tier 2, 33.67% at Tier 3, and 0.00% at the FailSafe tier."
One third of agents are matched on "age group, sex, and stratum only" (§3.3 para 2), which drops labour-force status and province. The work-from-home status variable (POWST) conditions the generator (§3.2 para 2) but is not among the seven linkage keys, so the break enters the stock only through whichever diary happens to be drawn. The text calls the 0% FailSafe rate confirmation of pool density; it does not discuss what Tier-3 matching does to the very variable the paper is about.

**S7. Annual electricity barely moves.** INSUFFICIENT as stated.
Quote (§5.2 para 1): "annual electricity rises by only +1.4 to +2.6% across the COVID break, and by a further +0.6 to +1.2% from the 2022 cycle to the 2030 forecast."
Quote (§5.3 para 2): "For the paired annual energy differential the confidence interval is wide and includes zero".
The ranges are reported without uncertainty in the abstract, §5.2, §6 and §8, while §5.3 says the paired interval includes zero. The "across the break" comparison is also not paired (§4.3 para 1: household identity "is not carried across the two groups"). What the range spans (archetypes? cities?) is never stated.

**S8. The load shape changes, with confidence intervals excluding zero, because of the break.** INSUFFICIENT. This is the load-bearing sub-claim and it is not supported by the statistic offered.
Quote (§5.3 para 2): "The midday energy share increases by +0.367 percentage points (95% CI [+0.208, +0.526]), excluding zero. The load factor ... increases by +0.0117 (95% CI [+0.0085, +0.0150])".
Quote (§5.3 para 3): "The COVID break at 2022 is visible in the trajectory as a step in the shape metrics (load factor increment approximately +0.009 at that cycle) ... the 2022 to 2030 leg of that extension is fully within-panel".
Quote (§4.3 para 2): "The paper's primary inferential targets (§5.3), the 2022 to 2030 load-shape metrics, are fully within-panel".
The CI-bearing deltas are 2022 to 2030. Both endpoints are post-COVID; the transition contains no work-from-home break, only demographic aging plus a 2030 raking the paper says is inflated (§7 para 5). The break step itself (+0.009) is cross-panel, unpaired and carries no interval. The abstract ("The load shape, however, changes structurally, midday fill and flattening (Δmidday share +0.37 pp; Δload factor +0.012; both confidence intervals exclude zero)"), the Fig. 6 caption ("Diurnal load-shape reshaping under work-from-home"), the Highlights ("WFH fills the midday valley and flattens load") and Conclusion item 3 ("The load-shape consequence of that break is ... the paired within-household differentials place both shape changes with confidence intervals that exclude zero") all attribute the 2022 to 2030 statistic to the break.

**S9. The evening peak is stationary near 17:30.** PARTLY SUFFICIENT.
Quote (§5.3 para 1): "the mean hour of peak demand remains within a narrow 17.0 to 17.7 h band across all five survey and forecast cycles (17.70 h in 2005, narrowing to 17.02 h by 2030)".
A 0.68 h drift is reported and called stable. No uncertainty is given for the cycle means. See 3.M2 and 4.8.

**S10. The end-use model is validated against SHEU.** INSUFFICIENT (circular).
Quote (§3.6 para 3): "a scalar f_e = SHEU_target_e / simulated_annual_e is computed and applied uniformly across all time-slots".
Quote (§5.2 para 2): "The household-level SHEU agreement, established here before any timing analysis, is the credibility anchor that validates the model's representation of residential electricity use".
A scalar fitted to the target and then measured against the same target agrees with it by construction. The ±2.7% residual is a property of the rounding or re-simulation chain, not evidence about the model. See 4.6.

**S11. The paired design isolates the occupancy channel.** SUFFICIENT for envelope and weather, INSUFFICIENT for generator noise.
Quote (§4.3 para 2): "the within-household cross-year difference in energy output is attributable solely to the predicted change in the occupancy time-series".
True as written, but "predicted change" includes the sampling noise of the generator and of the weekend donor draw (§3.5 para 4), which the design does not cancel and the text never quantifies.

---

## 3. Internal consistency mismatches

**M1. Conclusion says EUI is consistent with SHEU ranges; Results and Table 5 say every archetype is below them.**
Conclusion item 1: "with archetype energy-use intensities consistent with the SHEU regional-average ranges."
§5.2 para 2: "All four archetypes sit below their SHEU regional-average ranges, by margins of roughly 3% (mid-rise), 12% (single-detached), 27% (other dwelling) and 31% (high-rise)." Table 5, every row: "No, below lower".

**M2. Mean peak hour: §4.4 gives one band, §5.3 gives a wider one and a 2030 value outside the first.**
§4.4 para 2: "The mean peak hour falls between 17.5 and 17.7 hours across all years".
§5.3 para 1: "within a narrow 17.0 to 17.7 h band ... 17.02 h by 2030". Abstract and §6 round this to "~17:30"; 17.02 h is 17:01.

**M3. Table 4 says the 1.80% / 4.04% half-widths are load-shape precision; §4.3 says they are annual-energy precision.**
Table 4, MC convergence line: "95% CI half-width mean 1.80%, worst cell 4.04% at N = 50 (load-shape precision, not annual-kWh precision)."
§4.3 para 3: "The 95% confidence-interval half-width of the cell-mean annual energy averages 1.80% across cells, with a worst-case cell of 4.04%; the load-shape metrics are considerably more precise".

**M4. Discussion cites Table 5 for the annual-electricity increments; Table 5 contains no such numbers.**
§6 para 1: "(+1.4 to +2.6% across the break, +0.6 to +1.2% to 2030; Table 5)".
Table 5 holds 2022 and 2030 EUI per archetype and SHEU bands only; no 2015 value and no percentage change.

**M5. The missing day-types are said to be synthesized by the generator in §3.2 and to be filled by drawing genuine diaries in §3.5.**
§3.2 para 1: "the other two day-types must be synthesized to equip every respondent with a complete Weekday/Saturday/Sunday profile set prior to Census linkage."
§3.5 para 4: "the missing day-type is completed by a donor-draw procedure: a genuine diary of the needed type is drawn from the in-frame pool".
If every respondent already carries three day-types after §3.2, no household in the frame should be missing one at §3.5. The two mechanisms are never reconciled, and which one produced the weekend load in the 6,000 runs cannot be determined from the text.

**M6. Raking incoherence is called harmless because the BEM uses only AT_HOME, but two of the four injected channels are driven by the activity label.**
§3.2 para 3: "This is operationally harmless for the building energy model, which keys exclusively off the AT_HOME channel rather than the activity label".
§3.5 para 2: "The metabolic channel maps each of the 14 activity categories to a per-person internal-gain wattage"; §3.6 para 1: "translates the modelled occupant activity sequence into plug-load and lighting demand at each half-hour slot."

**M7. Annual energy is called phase-invariant while the same sentence reports a +2.85% change, larger than the paper's own annual-energy findings.**
§4.2 para 3: "annual energy totals were phase-invariant across the original and corrected campaigns (the maximum archetype EUI change was +2.85%, leaving the per-household SHEU calibration intact)".
§5.2 para 1: "+1.4 to +2.6% across the COVID break, and by a further +0.6 to +1.2%". A bug described as timing-only moved annual energy by more than the behavioural effect the paper reports.

**M8. Two W/MET values are given for the same standard adult.**
§3.5 para 2: "the ASHRAE 55 / ISO 7730 convention of approximately 105 W/MET for a standard adult" and, in the same sentence, "a ~70 kg standard body (which would imply ~83 W/MET)". Whether either external value is right is OUTSIDE MY SCOPE; the two cannot both describe the same reference adult.

**M9. The lighting simplification is promised a discussion in §7 that does not exist.**
§3.6 para 2: "this simplification is documented as deviation R1 (SI Appendix D) and its effect on the results is discussed in §7."
§7 contains no mention of lighting, daylight or R1.

**M10. The 2030 scenario is a "high-persistence upper bound" yet its at-home level is below 2022.**
§7 para 9: "a single scenario in which the work-from-home shift persists with probability one; this is framed explicitly as the high-persistence upper bound".
§5.1 para 1: 2022 break "+5.2 pp"; 2030 "+2.2 to +3.9 pp above the pre-pandemic level". A full-persistence bound that lands 1.3 to 3.0 pp below the observed 2022 level needs a mechanism; none is given, and the demographic aging invoked in §3.4 would be expected to raise, not lower, at-home time.

**M11. "Harmonized without loss" versus forced assignment of ambiguous codes.**
§3.1 para 1: "producing a unified activity alphabet without loss" and, two sentences later, "where a raw code was ambiguous, it was assigned to the closest HETUS parent category rather than left unclassified."

**M12. Stock composition attributed to the GSS sample, but dwelling type comes from the Census record.**
§4.1 para 1: "a distribution that reflects the urban-dominant character of the Canadian General Social Survey sample."
§3.3 para 3: "Dwelling-stock variables, dwelling type, ... are carried directly from the matched Census record onto each agent."

**M13. Hourly resolution described as a reporting choice in §7 but as the schedule input resolution in §3.5 and §4.2.**
§7 para 3: "the EnergyPlus reporting interval is hourly ... the hourly down-sampling occurs only at the simulation interface".
§3.5 para 1: "paired slots are averaged to 24 hourly values at the IDF interface." §4.2 para 1: "The temporal resolution at the IDF interface is hourly". The half-hour structure is lost before simulation, not after.

**M14. Frame size in Conclusion item 1 is the superseded one.**
Conclusion item 1: "linked to a 144,507-household Census frame". §4.2 para 1: the headline 2022 and 2030 runs use "the refined 144,465-household frame".

**M15. Abstract attributes the 2030 forecast to fine-tuning; Methods attribute it to demographic resampling.**
Abstract: "forecast by progressive fine-tuning under a True-Future-Test protocol".
§3.4 para 3: "The 2030 cohort is produced by demographic scenario injection ... without modifying the conditional behavioural model". Fine-tuning ends at 2022 (§3.4 para 1: "2005 → +2010 → +2015 → +2022").

---

## 4. Statistical and methodological findings

**4.1 The confidence-interval-bearing shape deltas test a transition that contains no work-from-home break.** (§5.3 para 2 and 3; §4.3 para 2; Abstract; Conclusion item 3.)
Quotes as in S8. Consequence: the causal sentence of the paper ("WFH fills the midday valley", Highlights) rests on a cross-sectional, unpaired step of "approximately +0.009" in load factor with no interval, while the intervals belong to a 2022 to 2030 comparison driven by age-structure resampling and a raking the paper calls inflated.

**4.2 The 2022 to 2030 comparison is confounded with the panel switch.** (§4.3 para 1; §5.3 para 3.)
"a second, independently-sampled N = 50 household set ... is carried forward across 2022 and 2030 only." The household-level morning-peaking population "was effectively absent in 2005 to 2015" and appears "in both 2022 and 2030" (§5.3 para 3). A feature that appears exactly when the household sample and the linkage frame change is not separable, from the text, from a sampling or linkage artefact. The paper does not test this.

**4.3 The collection-mode indicator is collinear with the COVID break.** (§2.1 para 2; §7 para 7.)
"a binary indicator that marks the predominant-mode transition at 2022". With one flag that is 0 for 2005, 2010, 2015 and 1 for 2022, the generator receives a post-COVID dummy under another name; the mode effect and the behavioural break cannot be identified separately, so "absorbed ... via explicit COLLECT_MODE conditioning" (§7 para 7) is not a mitigation. Which value the 2030 cohort receives for this flag is not stated. Also UNCERTAIN: Table 2 records 2015 as already "Multi-mode (CATI + EQ)", so a single 2022 switch may misplace the transition the flag is meant to mark.

**4.4 The True-Future-Test conditioning is underspecified.** (§3.4 para 4.)
"the model fine-tuned through 2015 and evaluated on the entirely unseen 2022 cycle". If the 2022 observed conditioning vector (work-from-home status POWST, mode flag = 1) is supplied at test time, much of the 2022 at-home shift is read off the inputs rather than forecast, and the mode flag value 1 was never seen in training. The text does not say what conditioning the test used, so the 0.0619 cannot be interpreted.

**4.5 Weekend divergence sits at 0.16 to 0.18 against a stated reconstruction gate of 0.10, yet the scorecard is 35/35 PASS.** (§3.4 para 4.)
"a clear PASS against the tighter < 0.10 reconstruction gate. The weekend JS sits near 0.16 to 0.18, a data-intrinsic ceiling rather than a model failure". Either the weekend is not gated at 0.10, in which case the gate list is incomplete, or it is and 35/35 is wrong. The 35 gates are never listed. The explanation ("synthetic rows alone sit 0.14 to 0.18 from the observed distribution") concedes that two thirds of the weekend diary pool fed to the BEM is 0.14 to 0.18 from the observed distribution.

**4.6 SHEU "validation" is circular.** (§3.6 para 3; §5.2 para 2; §5.4 para 1; Conclusion items 1 and 4.)
Quotes as in S10. The calibration scalar guarantees the annual match. Presenting "48 of 48 cell-years within ±2.7%" as the "credibility anchor that validates the model" and as evidence that "the activity model corrects" the presence-only over-prediction (§5.4 para 1: "the single-detached activity arm lands on the SHEU annual anchor") describes a fitted quantity as a test outcome. Any positive load model scaled by f_e would land on the anchor. Why the residual is not exactly zero is also unexplained.

**4.7 "Total energy conserved" while plug load roughly halves.** (§6 para 4.)
"bringing every one of the 48 dwelling-by-year cells within ±2.7% of its benchmark with total energy conserved (Fig. 7a)". Against §5.4 para 1: baseline "6,550 to 6,870 kWh" versus targets "3,139 to 3,700 kWh". What is conserved, and between which two quantities, is not stated.

**4.8 The peak-hour "null" is bounded by hourly input resolution and its uncertainty is not reported.** (§5.4 para 2; §5.3 para 1.)
"the building-level equipment peak-hour shift is 0 ± 1 h (mean −0.12 h, σ = 0.39 h)". Schedules enter EnergyPlus at hourly resolution (§3.5 para 1), so any shift under about 30 minutes is undetectable by construction; "verified null" overstates what a 1 h grid can verify. Separately, the cross-cycle stock peak drifts 17.70 to 17.02 h (§5.3 para 1), a change larger than the σ of the activity-arm null, and no interval is attached to the cycle means.

**4.9 Effect sizes are called structural without a stated basis.** (Abstract; §5.3 para 2; §6 para 1; §8 last para.)
"changes structurally, midday fill and flattening (Δmidday share +0.37 pp; Δload factor +0.012". The base load factor, base midday share and the midday window used for the energy share are never reported, so the reader cannot judge whether 0.37 percentage points of daily energy is operationally material. §1.1 motivates the work with hourly discrepancies "of up to 41%". "materially change the ramping- and demand-response-relevant load metrics" (Abstract, §8) has no ramp-rate or demand-response quantity behind it.

**4.10 Two of four primary metrics are never reported numerically.** (§4.4 para 1; §5.3.)
"Load-shape metrics, load factor, midday energy share, peak-to-average ratio, and coincidence factor, constitute the primary inferential targets". Peak-to-average ratio has no value anywhere in §5; coincidence factor appears only as "remaining below unity" (§5.3 para 3).

**4.11 Annual-electricity increments reported as ranges without intervals, and the break comparison is not paired.** (§5.2 para 1; §5.3 para 2; §4.3 para 1.)
Quotes as in S7. The abstract's "annual electricity follows by only +1.4 to +2.6% across the break" is drawn from two different household samples and, per §5.3, its paired interval "includes zero" for the within-panel leg.

**4.12 The aggregation level of the reported confidence intervals is not stated.** (§5.3 para 2; §4.3 para 3.)
Per-cell N = 50 is stated; whether the CIs in §5.3 are per cell, pooled over 1,200 households, or stock-weighted is not. The precision claim cannot be checked.

**4.13 Generator and donor-draw sampling noise is inside the paired difference and is not quantified.** (§4.3 para 2; §3.5 para 4.)
Quote as in S11. If the weekend donor is redrawn per cycle-year, each household's cross-year weekend difference includes a fresh random draw. Nothing in §4 or §5 separates this from behavioural change; no repeated-draw or seed sensitivity is reported.

**4.14 Lighting has no daylight gate, which biases the paper's headline quantity in the direction of the finding.** (§3.6 para 2.)
"Lighting is modelled as a binary occupied-and-awake indicator multiplied by the dwelling's SHEU lighting scale factor, without a daylight-availability gate". Work-from-home adds daytime at-home awake hours, every one of which draws lighting load under this rule, so the midday fill in the electricity profile is inflated by construction. The annual scalar cannot fix a shape bias. The promised §7 discussion is absent (M9).

**4.15 HVAC setpoint and thermostat schedules are never described.** (§3.5; §4.2.)
"Four parallel schedule channels are derived per household" (§4.2 para 2): occupancy, metabolic, equipment, lighting. Whether heating and cooling setpoints follow occupancy or are fixed is not stated, yet the "thermal decoupling" explanation (§5.2 para 1) and the sign of the annual effect depend on it. Domestic hot water is metered (§4.4 para 1) but no schedule for it is described.

**4.16 EUI comparison basis may not be like-for-like.** (Table 5 notes; §4.4 para 1.)
SHEU is "total all-fuels site energy per heated area". Whether the simulated EUI is site electricity only, or electricity plus a heating fuel, and whether the archetype is all-electric, is never stated. Heating is collected as "Heating:EnergyTransfer" (a thermal quantity, not a fuel). The one-directional offset attributed to envelope vintage could also be a numerator mismatch.

**4.17 One third of Census agents matched on three keys, and the WFH variable is not a linkage key.** (§3.3 para 2.)
Quotes as in S6. For a paper whose signal is work-from-home, carrying diaries onto dwellings without matching on labour-force status for 33.67% of agents, and never on place-of-work status, needs a sensitivity statement.

**4.18 The 2030 cohort size equals exactly three times the 2022 diary count.** (§3.4 para 3; §2.1 para 1.)
"producing a 37,008-row synthetic 2030 diary cohort"; 2022 valid diaries "12,336". 12,336 × 3 = 37,008, which suggests the 2030 cohort is the augmented 2022 pool relabelled under 2030 weights rather than a new draw. How 37,008 diary rows reach 144,465 households for 2030, i.e. whether the linkage was rerun, is not described anywhere. UNCERTAIN whether this is what was done; the text does not say.

**4.19 Gate thresholds have no stated provenance and differ by a factor of four across stages.** (§3.2 para 2; §3.4 para 4.)
Generator activity gate "≤ 0.05", reconstruction gate "< 0.10", True-Future-Test gate "< 0.20", composite "below 1.045". None is justified, and the composite is undefined, so PASS/FAIL statements cannot be interpreted by a reader.

**4.20 Standardization basis of the at-home percentages changes across sections without a reconciling table.** (§2.1 para 1; §5.1 para 1 and 2; §3.4 para 4; §4.2 para 4.)
Person-weighted all-day 70.6% (2022), raw weekday +6.6 pp, standardized weekday +5.2 pp, standardized 2005 to 2015 "64.2 / 64.2 / 63.3%", injected household weekday mean "78.48%" (2030). At least four bases; the 78.48% cannot be placed against any of the others from the text.

---

## 5. Structure and clarity issues

**C1.** The 4-hour phase bug is narrated in §3.1 para 3, §3.5 para 5, §4.2 para 3, §4.4 para 2, §6 para 7 and §7 para 1. Six tellings of an internal correction read as lab notes; a reviewer will ask why a corrected bug occupies more text than the primary metric definitions.

**C2.** Internal dates and pipeline labels appear in the manuscript: "2026-07-09 relink" (§2.2, §3.3, §4.3, Table 4, §7), "Step-8 campaign" (§5.2), "Step 9" (§5.4), "Step-6 calibration validation" (§7 para 5). Steps are defined only in the Fig. 1 caption ("Steps 1 to 9").

**C3.** §5.1 para 1 states its own headline as "provisional pending a calibration-provenance check described in §7". A results section that defers its number to a limitation reads as unfinished.

**C4.** The abstract and highlights carry none of the three caveats the body attaches to the 2030 number (single persistence scenario, provisional magnitude, cross-panel trajectory). Abstract claims are therefore not mirrored in §7.

**C5.** Figure captions are one line each and name no panels; Fig. 6 is cited as 6a, 6b, 6c and Fig. 7 as 7a, 7b (§5.3, §5.4) with no caption text defining them. Whether axes match the text is OUTSIDE MY SCOPE (images not in the text).

**C6.** Metric definitions arrive late or never: "midday energy share" window is not defined (10:00 to 15:00 appears only for occupancy in §5.1); load factor is defined in passing in §5.3 para 2 ("ratio of mean to peak daily demand") after being used in the abstract; peak-to-average ratio and coincidence factor are never defined.

**C7.** §5.2 para 1: "The answer on both fronts is conservative." The two fronts are not named.

**C8.** §3.4 para 2 introduces "the joint training stage" with recency weights 0.10 to 0.40 after describing a strictly sequential fine-tuning chain in para 1; the relation between the two regimes is not stated.

**C9.** §4.3 para 1: households are "stratified by dwelling type (DTYPE) and province (PR)" within an archetype-by-city cell. Stratifying by dwelling type inside an archetype cell, and by province inside a single-city cell, is not explained; §7 para 4 reveals that households from other provinces are run under a city's weather ("maps Atlantic-province households onto the Montréal EPW"), which §4 never says.

**C10.** §3.6 para 3 and §5.4 para 1: "4,800 paired baseline-versus-activity EnergyPlus runs" alongside the "6,000" of §4.3. Whether the 4,800 overlap the 6,000, and which "2 years" the 48 cell-years cover, is not stated.

**C11.** §4.1 para 1: citation string "([National Research Council Canada, 2017 2020]" is malformed.

**C12.** §6 para 3 cites "the order of the ~+12% structural increase in residential in-home energy demand documented for the Canadian context" with no reference; every other external number in §6 is attributed.

**C13.** Table 1 caption says "external competitors versus this study" while the paragraph below it discusses the authors' own C-VAE line; the reader has to learn from the text that the strongest prior on most columns is excluded from the table by design.

**C14.** The Data availability statement promises SI tables (48-cell calibration table, per-household results, hourly profiles) and the body cites SI Tables A1 to A3, B1, B2 and Appendix D; the Appendix as given contains nine figure captions only.

**C15.** §1.2 last para and §6 para 2 restate the same three-competitor argument almost verbatim.

---

## 6. Ranked reviewer critique (top 10)

1. **would-reject.** The confidence-interval-bearing shape results (§5.3 para 2, Fig. 6b, Abstract, Conclusion item 3) measure 2022 to 2030, a transition with no work-from-home break; the break step is unpaired and interval-free (§5.3 para 3). The paper's causal headline is not tested by the statistic it cites.
2. **would-reject.** §5.1 para 1 and §7 para 5 declare the 2030 at-home magnitude provisional and inflated; the abstract, highlights and Conclusion item 2 state it as a result. The manuscript is submitting a number it says should be recomputed.
3. **would-request-major-revision.** Conclusion item 1 says EUI is "consistent with the SHEU regional-average ranges"; §5.2 and Table 5 show all four archetypes below range. A direct contradiction on the plausibility anchor.
4. **would-request-major-revision.** SHEU agreement within ±2.7% (§5.4, Conclusion items 1 and 4, Abstract) is produced by a scalar fitted to the target (§3.6 para 3). Presenting it as validation, and as the activity model "correcting" the baseline, will be read as circular.
5. **would-request-major-revision.** Collection-mode flag and COVID break switch at the same cycle (§2.1 para 2); §7 para 7 offers no basis for "far larger than any plausible mode effect". The 2022 shift's attribution to behaviour is not identified.
6. **would-request-major-revision.** Lighting has no daylight gate (§3.6 para 2) and the promised §7 treatment is missing; the midday fill is biased upward by construction in the channel the paper reports. Combined with undocumented HVAC setpoint handling (4.15).
7. **would-request-major-revision.** Weekend day-types are produced two different ways (§3.2 vs §3.5), the synthetic weekend rows sit 0.14 to 0.18 JS from observed (§3.4 para 4), and the 35/35 PASS is not reconcilable with the stated 0.10 gate. The reader cannot tell what weekend behaviour was simulated.
8. **would-request-major-revision.** Annual-electricity increments (+1.4 to +2.6%, +0.6 to +1.2%) carry no intervals in four places while §5.3 says the paired interval includes zero, and the cross-break leg is unpaired; the same bug the paper calls phase-invariant moved EUI by +2.85% (§4.2 para 3).
9. **would-request-major-revision.** Effect sizes (0.37 pp midday share, 0.012 load factor) are called "structural" and "material" with no base values, no ramp or demand-response metric, and two of four primary metrics never reported (4.9, 4.10).
10. **minor.** Lab-notebook content in the manuscript (six tellings of the phase bug, relink dates, step numbers, "an activity-side raking facility exists"), malformed citation in §4.1, undefined composite score, uncited ~12% in §6, one-line figure captions.

---

## 7. What is OUTSIDE MY SCOPE

- I could not check any SHEU 2019 value: the per-dwelling equipment and lighting targets (§2.3), Table 3.3a/3.3b bands and central values (Table 5), or the heated-area basis.
- I could not check the external work-from-home figures: about 20% of full workdays after versus 5% before (§1.3, §6), the +7.9% weather-adjusted increase (§1.3, §6), or the ~+12% Canadian figure (§6, uncited).
- I could not check the ASHRAE 55 / ISO 7730 W/MET convention or the 2024 Adult Compendium MET values (§3.5); I flagged only that the manuscript's two numbers disagree with each other.
- I could not check any row of the Table 1 capability matrix against the cited papers, nor the characterization of Chen et al. (2022), Yin et al. (2024), Jalilian and Kamel (2025) or Motuzienė et al. (2022) in §1.2, §1.3 and §6.
- I could not check the GSS facts: cycle numbers, diary counts, exclusion rates, collection modes, the 04:00 diary origin, or whether SURVMNTH and TUI_10 availability is as stated (§2.1, Table 2).
- I could not check the Census PUMF agent count (286,537), the derived household counts (144,507; 144,465) or the Statistics Canada M1 projection (§2.2, §3.3, §3.4).
- I could not check whether NECB 2017 is an appropriate envelope basis for residential archetypes (§2.4, §4.1); I note only that the text pairs it with NBC 9.36 without comment.
- I could not check the Jensen-Shannon, RMS and composite gate values, the 35/35 and 24/0/3/0 scorecards, or the match-tier percentages, since the underlying tables (SI B1, B2, Appendix D, the 48-cell table) were not in the text.
- I could not read any figure (Figs. 1 to 7, S1 to S9); caption-versus-axis consistency is unverified.
- I could not check the reference list entries, DOIs, or the status of the two companion manuscripts (§1.4).
- I could not check whether the EnergyPlus DX-coil fix (§4.4 para 2) is a legitimate one-field correction.
- I could not judge whether the four redrafted sections in `rejection revision/manuscript/` already address any item above; the review was confined to the submitted text.

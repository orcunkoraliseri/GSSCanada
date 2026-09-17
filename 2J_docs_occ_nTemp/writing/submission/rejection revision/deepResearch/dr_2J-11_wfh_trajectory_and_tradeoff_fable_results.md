# dr_2J-11 (Fable version) results: close-reading audit of the WFH-scenario argument, no external search

**Run:** 2026-09-16, Claude Fable 5.1 inside Claude Code, no web access, no external lookups.
**Text reviewed:** `writing/submission/archive/2J_manuscript_submission.md` (the submitted manuscript, 653 lines). This is the only complete manuscript on disk, so it is the text audited, exactly as the dr_2J-12 Fable run did. The two partial redrafts that touch the scenario (`rejection revision/manuscript/draft_S2_framework.md` section 2.7 and `draft_S7_limitations.md`) were read afterwards and are reported in one clearly separated note at the end; nothing from them is mixed into sections 1 to 7. Figures and SI tables were not in the text and could not be read.
**Quotation convention:** the manuscript uses em dashes, en dashes and arrows. Inside quotations these are replaced by commas, the word "to", or nothing, so this report contains none. Section pointers use the manuscript's own numbering; "para N" counts paragraphs from the top of the named subsection, ignoring captions and tables.
**Scope guard honoured:** no external number, survey or study was checked or recalled. Every external figure the manuscript quotes (Barrero et al., Guo et al., Cicala, the "+12%" figure, Statistics Canada M1) is marked OUTSIDE MY SCOPE where it comes up.
**Status:** UNVETTED deep-research return. Goes through the 7-step vetting before anything is acted on.

---

## 1. Verdict

**HAS A STRUCTURAL PROBLEM:** the manuscript defines its 2030 case as a scenario in which the work-from-home shift "persists with probability one" (section 7 para 9), so by its own construction the 2022 to 2030 leg contains no work-from-home change at all, yet that leg is the only one that carries confidence-interval-bearing load-shape results and the abstract, Fig. 6 and the Conclusion label those results as the effect of work-from-home; on top of this the one 2030 magnitude, "+2.2 to +3.9 pp", is defined two incompatible ways in the text.

---

## 2. Argument map

**Central claim (quoted).** Section 3.4 para 4: "The 2030 forecast preserves the COVID-era work-from-home break, a +6.6 pp raw (+5.2 pp demographically standardized) weekday at-home displacement at the 2015 to 2022 transition, carrying it forward at +2.2 to +3.9 pp above the pre-pandemic baseline as a single high-persistence scenario; the sensitivity of this assumption is bounded in section 7." In one sentence: the 2030 forecast assumes the 2022 work-from-home shift persists in full, because (section 1.3) work-from-home "shows every sign of persisting at a new hybrid-work equilibrium", and the load-shape results for 2030 follow from that assumption.

Sub-claims that must hold for this to be a defensible scenario design.

**S1. The 2022 rise is behavioural, not compositional.** SUFFICIENT on the text's own terms.
Quote (section 5.1 para 2): "The 2022 jump, by contrast, survives standardization and therefore reflects a genuine change in daily behaviour, not a shift in who responded to the survey: after the same demographic standardization, the weekday at-home break at the 2015 to 2022 transition settles at +5.2 pp".
The standardization argument is coherent and the standardized pre-pandemic series (64.2 / 64.2 / 63.3%) is given. Survey-mode confounding is a separate sub-claim, outside this audit's scope.

**S2. Persistence of the shift to 2030 is justified.** INSUFFICIENT on the text's own terms.
Quote (section 1.3 para 1): "Work-from-home has settled at roughly four times its pre-pandemic prevalence, about 20% of full workdays after the pandemic against 5% before (Barrero, Bloom and Davis 2021), and shows every sign of persisting at a new hybrid-work equilibrium (Guo et al. 2026)."
This is the only justification offered anywhere for the persistence assumption. Whether those two sources support it is OUTSIDE MY SCOPE. Within the text, the justification is a two-clause literature assertion in the Introduction that is never returned to when the scenario is defined (section 3.4) or bounded (section 7); the Limitations paragraph that defines the scenario (section 7 para 9) gives no reason for choosing full persistence other than calling it an upper bound.

**S3. A single high-persistence scenario is an appropriate upper bound.** INSUFFICIENT.
Quote (section 7 para 9): "the 2030 forecast is generated under a single scenario in which the work-from-home shift persists with probability one; this is framed explicitly as the high-persistence upper bound rather than a central estimate".
Two problems on the text's own terms. (a) The number attached to the scenario contradicts "upper bound" under one of the text's own two definitions: if "+2.2 to +3.9 pp above the pre-pandemic baseline" (section 3.4, section 5.1, Abstract, Conclusion 2) is the 2030 level, then 2030 sits below the 2022 level of +5.2 pp, so the scenario reverts part of the shift and is not a persistence upper bound. (b) Under the other definition (section 7 para 5: "the 2022 to 2030 step ... (+2.2 to +3.9 percentage points)"), the at-home level keeps rising after 2022, which "persists with probability one" cannot produce on its own; the text never says what drives the further rise. See section 5 below.

**S4. The magnitude is bounded by a stated sensitivity analysis.** INSUFFICIENT.
Quote (section 3.4 para 4): "the sensitivity of this assumption is bounded in section 7."
Quote (section 7 para 1): "Several limitations bound the interpretation of the results, each stated with the design choice, mitigation, or sensitivity analysis that contains it."
Quote (section 7 para 9): "with a high-reversion counter-scenario the natural sensitivity analysis that would convert the point forecast into a bracketed range".
Quote (section 8 para 4): "The 2030 projection should be bracketed with a high-reversion persistence scenario to complement the high-persistence bound reported here".
Section 3.4 promises a bound in section 7; section 7 delivers none. The counter-scenario is described in the conditional ("would convert") and listed as future work in the Conclusion. No sensitivity analysis of the persistence assumption exists in the text.

**S5. The 2030 forecast is validated.** INSUFFICIENT.
Quote (Highlights, bullet 2): "2030 occupancy forecast through the COVID/WFH break, validated by True-Future-Test."
Quote (section 3.4 para 4): "The final True-Future-Test phase, the model fine-tuned through 2015 and evaluated on the entirely unseen 2022 cycle, achieves a weekday JS divergence of 0.0619".
The True-Future-Test, as the text defines it, scores the model's ability to reproduce 2022 from data through 2015. It says nothing about 2030, which has no observed target. The Highlights sentence attaches "validated" to the 2030 forecast itself. Section 7 para 5 adds that the 2030 direction "is independently corroborated by the Step-6 calibration validation", a check the text never describes anywhere, so the reader cannot assess it.

**S6. The 2030 at-home magnitude is reliable enough to carry into the load-shape results.** INSUFFICIENT by the text's own admission.
Quote (section 7 para 5): "the 2022 to 2030 at-home gap as currently plotted is inflated relative to what a fully recalibrated 2030 forecast would show ... the specific magnitude of the 2022 to 2030 step reported in section 5.1 (+2.2 to +3.9 percentage points) and visualized in Fig. 5 should be treated as provisional pending a recalibration of the 2030 occupancy forecast against the current, post-relink household frame."
The text itself says the input to the 2022 to 2030 simulation leg is provisional and inflated. It does not say whether the load-shape deltas simulated from that input (section 5.3) are therefore also provisional; they are presented without the caveat.

**S7. The 2022 to 2030 load-shape change is attributable to work-from-home.** INSUFFICIENT, and this is the structural point.
Quote (section 3.4 para 3): "This captures the demographic virtual drift in P(demographics) between 2022 and 2030 without modifying the conditional behavioural model".
Quote (section 7 para 9): "a single scenario in which the work-from-home shift persists with probability one".
Quote (Fig. 6 caption): "Diurnal load-shape reshaping under work-from-home."
Quote (section 8 para 1): "the behavioural break reshapes the residential load curve structurally".
Quote (section 5.3 para 2): "The midday energy share increases by +0.367 percentage points (95% CI [+0.208, +0.526]), excluding zero. The load factor ... increases by +0.0117 (95% CI [+0.0085, +0.0150])".
Quote (section 4.3 para 2): "The paper's primary inferential targets (section 5.3), the 2022 to 2030 load-shape metrics, are fully within-panel".
By the text's own definition, between 2022 and 2030 the behavioural model is unchanged and the work-from-home shift is held at its 2022 level. What changes between 2022 and 2030 is the demographic composition (M1 resampling) and the raked at-home target (section 3.5 para 4, section 7 para 5). So the only paired, confidence-interval-bearing shape deltas measure demographic drift plus a raking target, not a work-from-home change. The 2015 to 2022 step, which is where the work-from-home break actually lies, is stated to be cross-sectional across two different household panels (section 4.3 para 1) and carries no confidence interval in the text (section 5.3 para 3 gives only "load factor increment approximately +0.009 at that cycle"). The abstract's "The load shape, however, changes structurally, midday fill and flattening (delta midday share +0.37 pp; delta load factor +0.012; both confidence intervals exclude zero)" therefore reports the 2022 to 2030 leg as if it were the work-from-home effect.

**S8. The demographic and behavioural channels are handled separately.** SUFFICIENT as a design statement, INSUFFICIENT as a reported result.
Quote (section 3.4 para 3): "the two drift channels are handled independently, as the conceptual framework requires."
The design is stated clearly. But nowhere does the text report how much of the 2022 to 2030 at-home change comes from the demographic resampling versus the carried-forward behavioural level, so the reader cannot separate aging from work-from-home in any 2030 number.

---

## 3. Single-scenario versus range finding

The text uses at least six different words for the same 2030 quantity. Counts are of the word in the whole manuscript, all uses, so they overstate the 2030-specific uses; the quoted examples are all 2030-specific.

**"forecast" (the dominant word, roughly 45 occurrences).**
- Abstract: "This study forecasts the Canadian residential load shape from 2005 to 2030"; "forecast by progressive fine-tuning under a True-Future-Test protocol".
- Highlights bullet 2: "2030 occupancy forecast through the COVID/WFH break, validated by True-Future-Test."
- Section 1.5 item 3: "A 2025 hindcast is replaced by a 2030 forecast carried through the structural break".
- Section 3.4 title: "Longitudinal Forecasting to 2030"; para 4: "the 2030 forward forecast as the operational deliverable".
- Section 4.3 para 1: "the longitudinal forecast year 2030"; Table 4: "2030 (forecast)".
- Section 5.1 para 1: "The forecast 2030 synthetic diaries carry the break forward".
- Section 7 para 5: "The 2030 forecast's occupancy (AT_HOME) calibration"; "a fully recalibrated 2030 forecast".
- Section 7 para 9: "the 2030 forecast is generated under a single scenario"; "the point forecast".
- Section 8 para 1: "forecast through the COVID/work-from-home structural break to 2030"; finding 2: "in the 2030 forecast".

**"projection".**
- Section 1.3 para 1: "any projection of residential demand to 2030 that is anchored to a pre-COVID occupancy baseline inherits the structural break as a systematic bias".
- Section 5.1 para 2: "The 2030 projection extends this elevated midday presence".
- Section 7 para 9: "a persistence-conditioned projection rather than an unconditional prediction".
- Section 8 para 4: "The 2030 projection should be bracketed".

**"scenario".**
- Section 3.4 para 3: "demographic scenario injection" (this is the demographic channel, not the work-from-home persistence).
- Section 3.4 para 4: "as a single high-persistence scenario".
- Section 7 para 9: "a single scenario in which the work-from-home shift persists with probability one"; "a high-reversion counter-scenario".
- Section 8 para 4: "a high-reversion persistence scenario".

**"bound" / "upper bound".**
- Section 3.4 para 4: "the sensitivity of this assumption is bounded in section 7" (a promise, not a result; see S4).
- Section 7 para 9: "the high-persistence upper bound rather than a central estimate".
- Section 8 para 4: "the high-persistence bound reported here".

**"prediction" / "point forecast".**
- Section 7 para 9: "the point forecast"; "a persistence-conditioned projection rather than an unconditional prediction".

**"persists" (attached to the number, no qualifier).**
- Abstract: "Weekday at-home occupancy breaks +5.2 percentage points (pp) at COVID and persists to 2030 (+2.2 to +3.9 pp)".
- Section 8 finding 2: "persists at +2.2 to +3.9 percentage points above the pre-pandemic baseline in the 2030 forecast".
- Section 6 para 1: "the behavioural break is large and persistent (section 5.1)".

**Consistency assessment.** The scenario framing ("single scenario", "upper bound", "persistence-conditioned projection", "not a central estimate") appears in exactly three places: one clause at the end of section 3.4, the last paragraph of section 7, and the future-work sentence of section 8. Everywhere the reader first meets the number (Abstract, Highlights, section 1.5, section 5.1, section 6, the numbered Conclusion findings) it is a "forecast" that "persists", stated as a single predicted quantity with no scenario qualifier. The Highlights go further and call the 2030 forecast "validated". A reader who stops at the abstract, highlights and numbered findings receives a single predicted 2030 number; a reader who reaches section 7 para 9 learns it is a one-sided conditional scenario.

**Exposure to the two-paths critique.** The text does anticipate the critique in wording: section 7 para 9 names "a high-reversion counter-scenario" and section 8 para 4 says the projection "should be bracketed". But it anticipates it only as future work. As written, the manuscript delivers one path and describes the second path as something that "would convert the point forecast into a bracketed range". The critique is therefore not answered, it is conceded and deferred. The abstract and highlights, which do not carry the concession, are fully exposed.

**One further wording issue.** "Upper bound" is used of a scenario whose reported 2030 level (under the "above the pre-pandemic baseline" reading) is lower than the 2022 level it is supposed to preserve in full. A high-persistence upper bound that lands below the observed 2022 value is not an upper bound on persistence. Which reading is intended is UNCERTAIN; see section 5.

---

## 4. System-boundary disclosure finding

**NOT FOUND in the text provided.**

The full manuscript was searched for any sentence stating, limiting or acknowledging that the paper models residential energy only, or that a rise in at-home energy may be offset in whole or in part by a fall in office or commercial energy the paper does not model. No such sentence exists. Specifically:
- The words "office" and "commercial" occur only inside reference-list entries (the title of Motuzienė et al. 2022, "Office buildings occupancy analysis", and "Office of Energy Efficiency" in the SHEU entry). Neither is a statement by the authors.
- "Non-residential", "workplace", "system boundary" and "residential-only" do not occur.
- Section 6 para 3 contains the closest thing to a boundary statement, but it bounds the residential delta against other residential effects, not against the non-residential side: "the reported delta is the pure occupancy channel and necessarily sits well below all-cause pandemic figures such as the weather-adjusted +7.9% residential electricity increase that also absorbs equipment acquisition, thermostat behaviour, and dwelling-occupancy turnover". Nothing in it mentions the office or commercial building the worker is no longer in.
- The Limitations section (section 7, nine paragraphs) lists metabolic calibration, weekend pooling, envelope, weather, panel change, calibration provenance, linkage independence, survey mode and the single scenario. The residential-only boundary is not among them.

**Where such a statement would naturally belong.** Three places, and its absence is most exposed in the third:
1. Section 7 Limitations, as a scope paragraph next to the single-scenario paragraph (para 9).
2. Section 1.3, where the paper cites a "+7.9%" residential increase and the shift of work from office to home is first introduced; the office side of the same shift is the obvious counterpart.
3. Section 6 paras 5 and 6, where the paper draws grid-level and code-level implications ("at the fleet level a flatter intraday profile ... reshapes the ramp into the evening peak and widens the midday window available for demand-response"; "static ASHRAE/NECB diversity schedules encode a pre-pandemic intraday shape that this study shows to be structurally outdated"). A grid-level reading of a residential midday fill without stating that the same workers have left a commercial midday load unmodelled is where a reviewer will object that the system boundary was never declared.

The manuscript also cites, without a reference, "the order of the ~+12% structural increase in residential in-home energy demand documented for the Canadian context" (section 6 para 3). Whether that figure exists is OUTSIDE MY SCOPE; as a text fact, it is the only numerical claim in section 6 that carries no citation, and it is used to support the behavioural premise of the scenario.

---

## 5. Percentage-point consistency findings

The text carries five distinct work-from-home magnitudes. Their definitions, where they recur, and the mismatches.

**Inventory (as defined in the text).**
- +6.1 pp: all-day-type, population-weighted at-home fraction, 2015 to 2022 (section 2.1 para 1, section 5.1 para 1). Arithmetic checks: 70.6 minus 64.5.
- +6.6 pp: raw weekday at-home displacement, 2015 to 2022 (section 3.4 para 4, section 5.1 para 1).
- +5.2 pp: demographically standardized weekday break, 2015 to 2022 (section 3.4 para 4, section 5.1 para 2, section 7 para 8, Abstract, section 8 finding 2).
- +2.2 to +3.9 pp: the 2030 magnitude, defined inconsistently (Finding 5.1 below).
- 78.48% versus 78.44%: injected 2030 weekday at-home mean versus its target (section 4.2 para 3).

**Finding 5.1 (the main mismatch). "+2.2 to +3.9 pp" is defined two incompatible ways.**
- As a level above the pre-pandemic baseline, four times: Abstract, "persists to 2030 (+2.2 to +3.9 pp)"; section 3.4 para 4, "carrying it forward at +2.2 to +3.9 pp above the pre-pandemic baseline"; section 5.1 para 1, "carry the break forward at +2.2 to +3.9 pp above the pre-pandemic level"; section 8 finding 2, "persists at +2.2 to +3.9 percentage points above the pre-pandemic baseline in the 2030 forecast".
- As the 2022 to 2030 step, once: section 7 para 5, "the specific magnitude of the 2022 to 2030 step reported in section 5.1 (+2.2 to +3.9 percentage points)".
These cannot both be true. If it is the level above pre-pandemic, then 2030 (+2.2 to +3.9) sits below 2022 (+5.2), the shift partly reverts, and "persists", "extends rather than reverses" (section 5.3 para 3), "extends this elevated midday presence" (section 5.1 para 2) and "upper bound" are all wrong. If it is the 2022 to 2030 step, then 2030 sits at roughly +7.4 to +9.1 pp above pre-pandemic, "persists" understates a further rise, and the text never says what produces that rise under a scenario whose behavioural model is unchanged after 2022. Section 7 para 5 also says the 2022 to 2030 gap "as currently plotted is inflated", which only makes sense if 2030 is above 2022, so section 7 is internally consistent with the step reading and the rest of the paper with the level reading. Which is correct is UNCERTAIN from the text.

**Finding 5.2. The range itself is never defined.** No sentence says what the two ends of "+2.2 to +3.9" span (day-types, archetypes, raw versus standardized, or something else). The same applies to "+1.4 to +2.6%" and "+0.6 to +1.2%" for annual electricity (Abstract, section 5.2 para 1, section 6 para 1, section 8 finding 3): section 5.2 says only "Across the 6,000 paired EnergyPlus runs". A range presented without its axis reads as a confidence interval, which the text elsewhere (section 5.3 para 2) says the annual delta does not have ("the confidence interval is wide and includes zero").

**Finding 5.3. The provisional caveat travels with the number in two places out of six.**
- Present: section 5.1 para 1 ("this magnitude is provisional pending a calibration-provenance check described in section 7") and section 7 para 5.
- Absent: Abstract ("persists to 2030 (+2.2 to +3.9 pp)"), Highlights bullet 2, section 3.4 para 4, section 6 para 1 ("the behavioural break is large and persistent (section 5.1)"), section 8 finding 2.
The caveat is also never extended to the quantities computed from the provisional input: the 2022 to 2030 shape deltas of section 5.3, the "+0.6 to +1.2% to 2030" annual increment, and Table 5's 2030 EUI column all derive from the schedule the text calls inflated, and none carries the qualifier.

**Finding 5.4. The 78.48% injected mean cannot be reconciled with any other number in the text.** Section 4.2 para 3 reports "the 2030 weekday at-home mean of 78.48% against a target of 78.44%". No 2022 or 2015 counterpart on the same basis (household-level, weekday, injected schedule) is reported anywhere, and no sentence relates 78.44% to the +2.2 to +3.9 pp or to the 70.6% diary fraction. The text also never says how the 78.44% target was derived, that is, how "persists with probability one" was turned into a number. Section 3.5 para 4 says a raking step is "applied uniformly across all five cycle-year schedule files", section 7 para 5 says the 2030 calibration "was raked against the pre-relink 2022 reference population", and section 3.4 para 3 says the behavioural model was not modified. Read together, the 2030 at-home level is a raked target, which makes it an input to the simulation rather than an output of the forecasting model; the word "forecast" for the at-home magnitude is then a misnomer on the text's own description. UNCERTAIN whether that reading is what happened, but the text does not rule it out.

**Finding 5.5. The abstract's "+5.2 pp" drops its qualifier.** Abstract: "Weekday at-home occupancy breaks +5.2 percentage points (pp) at COVID". The body defines +5.2 as the demographically standardized figure and +6.6 as the raw weekday figure (section 3.4 para 4, section 5.1). The abstract presents the standardized number as if it were the raw observed break. Section 8 finding 2 does say "separable from compositional sample aging by demographic standardization", so the Conclusion is consistent; the Abstract is not.

**Finding 5.6. The break's own load-shape step and the 2030 leg's step are reported on different footings but summed into one story.** Section 5.3 para 3 gives the 2015 to 2022 load-factor step as "approximately +0.009 at that cycle", cross-sectional, no interval; section 5.3 para 2 gives the 2022 to 2030 step as "+0.0117 (95% CI [+0.0085, +0.0150])", paired. The Abstract reports only the second ("delta load factor +0.012") and attributes it to the break. This is the same point as S7 and was also raised by the dr_2J-12 return; it is repeated here because it is where the scenario definition and the reported figures collide.

**Finding 5.7. Pointer mismatch.** Section 6 para 1 cites "(+1.4 to +2.6% across the break, +0.6 to +1.2% to 2030; Table 5)". Table 5 reports 2022 and 2030 EUI only, so it cannot show the across-the-break increment. Minor.

---

## 6. Ranked reviewer critique (top 5)

**1. Would-reject. The work-from-home effect is never measured with an interval; the intervals belong to a leg that holds work-from-home fixed.**
Section pointers: section 7 para 9 ("persists with probability one"), section 3.4 para 3 ("without modifying the conditional behavioural model"), section 4.3 para 2 ("The paper's primary inferential targets (section 5.3), the 2022 to 2030 load-shape metrics"), Abstract ("both confidence intervals exclude zero"), Fig. 6 caption ("under work-from-home"). By the paper's own scenario definition, 2022 to 2030 varies demography and a raked target, not work-from-home. The 2015 to 2022 leg, where the break is, is cross-sectional and interval-free (section 4.3 para 1, section 5.3 para 3). A reviewer will say the headline result is attributed to a cause the design deliberately held constant.

**2. Would-request-major-revision. One 2030 number, two definitions.**
Section pointers: Abstract, section 3.4 para 4, section 5.1 para 1, section 8 finding 2 (level above pre-pandemic) versus section 7 para 5 (2022 to 2030 step). The reviewer cannot tell whether the scenario has the shift persisting, growing or partly reverting, so cannot judge "upper bound", "persists" or "extends rather than reverses". Finding 5.1.

**3. Would-request-major-revision. A single one-sided scenario, promised bounded, never bounded, and presented as a validated forecast where it matters most.**
Section pointers: section 3.4 para 4 ("the sensitivity of this assumption is bounded in section 7"), section 7 para 1 ("each stated with the ... sensitivity analysis that contains it"), section 7 para 9 ("would convert the point forecast into a bracketed range"), section 8 para 4 ("should be bracketed"), Highlights bullet 2 ("validated by True-Future-Test"). The text concedes the two-paths critique in its last two pages and contradicts that concession in its first. A reviewer who asked for at least two work-from-home paths will find the request acknowledged as future work and the abstract unchanged.

**4. Would-request-major-revision. The system boundary is never declared while grid-level implications are drawn.**
Section pointers: section 6 para 5 ("widens the midday window available for demand-response and distributed-generation absorption"), section 6 para 6 (code schedule recalibration), section 7 (no scope paragraph). The paper models the home side of a home-versus-office shift and interprets the result for the grid without saying the office side is outside the model. Section 4 above: NOT FOUND.

**5. Minor, but it compounds items 1 and 3. The input the paper calls provisional and inflated feeds every 2030 result without the caveat travelling.**
Section pointers: section 7 para 5 ("inflated", "provisional"), section 5.1 para 1 (caveat present), Abstract, Highlights, section 6 para 1, section 8 finding 2 (caveat absent), section 5.3 para 2 and Table 5 2030 column (derived quantities, no caveat). A reviewer will ask why a number the authors themselves flag as not yet recalibrated appears unqualified in the abstract and why its downstream products are reported with confidence intervals as if the input were settled. Also section 4.2 para 3: the 78.44% target is never derived in the text (Finding 5.4).

---

## 7. What is OUTSIDE MY SCOPE

- I did not check whether Barrero, Bloom and Davis (2021) or Guo et al. (2026) support "about 20% of full workdays after the pandemic against 5% before" or a persisting hybrid equilibrium; that is the Gemini version's job.
- I did not check the "+7.9%" weather-adjusted residential increase attributed to Cicala (2023), nor whether it is a Canadian figure.
- I did not check whether the uncited "~+12% structural increase in residential in-home energy demand documented for the Canadian context" (section 6 para 3) exists in any source.
- I did not check any Statistics Canada figure, including the GSS at-home fractions, the M1 population projection, or the survey-mode history.
- I did not check any published home-working trajectory to 2030 or any published home-versus-office energy trade-off study; the presence or absence of such a trade-off in the literature is not assessed here, only its absence from the manuscript.
- I did not read Figs. 5, 6, S8 or Table 5's source data, so I cannot say which of the two "+2.2 to +3.9" definitions the plotted series actually shows.
- I did not verify any code or output file; the "raked target rather than forecast output" reading in Finding 5.4 is drawn from the text alone and is marked UNCERTAIN.

---

## Note on the redrafts on disk (project context, not part of the audited text, not external literature)

Read after sections 1 to 7 were written. Two of the four partial redrafts in `rejection revision/manuscript/` bear on this audit.

- `draft_S2_framework.md` section 2.7 now defines three persistence scenarios, lambda in {1, 0.5, 0}, with a standardised variant as a sensitivity check, and states "This is a scenario-based projection of a stated persistence assumption, not a forecast". That addresses critique items 2 and 3 for the Methods; the Abstract, Highlights, Results, Discussion and Conclusion have no redraft yet, so the front-matter exposure in section 3 above still stands.
- `draft_S7_limitations.md` states "The 2030 results are a scenario, not a forecast" and disclaims any uncertainty range. It still contains no residential-only or office/commercial boundary sentence, so the NOT FOUND of section 4 above holds for the redraft as well.
- One new tension the redrafts introduce, not present in the submitted text: the redraft's 2030 target adds "8 times a linear trend fitted to real respondents from 2005, 2010 and 2015" to the 2022 stock rate, while the submitted section 5.1 para 2 argues that the 2005 to 2015 drift "is compositional rather than behavioural" and flat once standardized (64.2 / 64.2 / 63.3%). Extrapolating eight years of a slope the paper itself calls compositional, on a fixed 2022 population, is a behavioural assumption the submitted text has already argued against. The S2 draft's "standardised version" is the natural reconciliation and should probably be the primary, not the sensitivity. UNCERTAIN which the rebuilt runs used; flagged for the vetting step, not decided here.

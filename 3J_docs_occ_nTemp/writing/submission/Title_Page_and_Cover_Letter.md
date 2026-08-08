# Title page

*Modelled on the 2J title page as submitted to Building Simulation on 2026-08-07
(`2J_docs_occ_nTemp/writing/submission/submissionDocs/Title_Page_and_Cover_Letter.md`). Target venue
for this manuscript is **Building and Environment** (Elsevier), decided 2026-08-08; see
`02_journal_options.md`.*

> **Not yet ready to send. Three things are unfilled or unverified and each is named where it sits:**
> the handling editor's name and the submission date in the cover letter, Hachem-Vermette's ORCID,
> and whether Building and Environment runs single- or double-anonymized review, which decides
> whether the manuscript file must be blinded the way the 2J one was.

---

## Cover letter

[submission date]

[Editor's name]
Editor, *Building and Environment*

Dear Editor,

We are pleased to submit our manuscript, *From One Channel to Four: A Jointly-Trained Time-Use
Occupancy Model for Mixed-Use Building Energy Simulation (Canada, 2005 to 2030)*, for consideration
as a research article in **Building and Environment**.

We want to be direct about the result that will decide how this paper is read, because it is
unusual. Three of the four channel-level energy-use-intensity gates in this study fail, and we report
them failing, at full strength, without widening a band or changing a scoring rule. The reason we
believe those failures are findings rather than a defect is a control the occupancy model never
touches: the uninjected `Default_NECB` reference implementation, running the code's own default
schedules with **no occupancy signal applied at all**, scores 85.45 kWh/m2/yr against the same
100 kWh/m2/yr office floor the injected cells are judged against. A control with nothing injected
cannot be failing because of the injected model. Two candidate explanations that would have put the
model at fault were tested and refuted in all 56 of 56 cells, and the band's own source document
states three different floors for itself. What the office gate is measuring is a reference band built
for single-use building stock, applied to a channel that lives inside a stacked mixed-use tower.

The study behind that finding is a behavioural one. Tall buildings increasingly stack residential,
office, retail and hospitality uses inside one structure, on one plant and often one meter, yet the
occupancy schedules driving their energy models remain single-channel. We jointly train one model to
generate four independent presence channels, three from four Statistics Canada General Social Survey
time-use cycles through a shared-encoder Transformer and one, hotel, from provincial tourism
statistics through a SARIMA side-track, because hotel guests are outside the survey frame by
construction. A per-space exact-match dispatch carries all four into PNNL Tall and SuperTall
prototypes across two Canadian cities, forecast 2005 to 2030 over a 56-cell campaign. The four
populations turn out not to behave as one occupant: they peak at four different hours, hotel roughly
seven hours after the midday cluster formed by the other three, their weekday day-to-night structure
differs by an order of magnitude and inverts outright for hotel, and they move in different
directions across the four survey cycles. Because those peaks do not coincide, the whole-building
coincidence factor stays below 1 in all four building-city cells, so use-type diversity inside one
building attenuates the aggregate peak in the same way household diversity does inside a single
archetype.

We are submitting to Building and Environment because occupant behaviour in buildings is one of this
journal's core subjects rather than an adjacent one. The primary object of this paper is an occupancy
model; the EnergyPlus campaign is the instrument that tests it, and the finding about reference-band
applicability is a finding about how occupancy in mixed-use buildings can be validated at all. The
open cell we occupy is specific: existing time-use-survey-driven occupancy models are single-channel
and single-use, existing multi-use occupancy work is district-scale and not survey-driven, and
neither carries several use-specific channels into one stacked building with a forecast horizon.

**Relationship to concurrent work.** This is the third study from a structured research pipeline and
we want to be explicit about the boundary. A predecessor manuscript is under review at the *Journal
of Building Performance Simulation*, and a second, which established the single-channel residential
occupancy pipeline this work grew from, is under review at *Building Simulation*. The present paper
shares with them only the premise that survey-grounded time-series occupancy can be built for
Canadian building energy models at all, which it treats as established and does not re-claim. What is
new here is the multi-channel question: four functionally distinct populations, three of them
survey-derived and one necessarily not, resolved separately inside one building, and the finding that
the reference bands available to judge such a building were not built for it.

The manuscript is original, has not been published previously, and is not under consideration
elsewhere. All authors have approved its submission. We have no competing interests to declare.

Thank you for considering our work.

Sincerely,

Orcun Koral Iseri, on behalf of both authors

---

## Paper title

From One Channel to Four: A Jointly-Trained Time-Use Occupancy Model for Mixed-Use Building Energy
Simulation (Canada, 2005 to 2030)

## Authors

Orcun Koral Iseri^1,\*^, Caroline Hachem-Vermette^1^

1. Gina Cody School of Engineering and Computer Science, Concordia University, 1455 De Maisonneuve
   Blvd. W., Montréal, Québec, H3G 1M8, Canada

\* Corresponding author: orcunkoral.oseri@concordia.ca

**ORCID.** Orcun Koral Iseri: https://orcid.org/0000-0001-7735-3363

*Hachem-Vermette's ORCID is absent from the 2J submission as well and is therefore left blank here
rather than invented. An ORCID is an identifier; a guessed one points at a real stranger.*

## Author contribution statement

**Orcun Koral Iseri:** Conceptualization, Methodology, Software, Formal analysis, Investigation, Data
curation, Validation, Visualization, Writing - original draft. **Caroline Hachem-Vermette:**
Conceptualization, Supervision, Funding acquisition, Resources, Writing - review and editing. Both
authors read and approved the final manuscript.

## Compliance with ethical standards

**Declaration of competing interest.** The authors have no competing interests to declare that are
relevant to the content of this article.

**Ethical approval.** This study does not contain any studies with human or animal subjects performed
by any of the authors. The analysis uses anonymized public-use microdata files released by Statistics
Canada, together with published provincial tourism-occupancy statistics.

## Acknowledgements

This postdoctoral research was financially supported by the Natural Sciences and Engineering Research
Council of Canada (NSERC) and the Voltage-Age Seed fund. The authors gratefully acknowledge this
support.

---

## What is deliberately NOT in this cover letter, and why

**No disclosure about the earlier Building and Environment rejection.** It was attributed by the
author on 2026-08-08 to **0J**, a different and earlier manuscript, subsequently published in *Energy
and Buildings*. A different paper's rejection years ago is not a fact this submission owes the editor,
and volunteering it would invite a comparison that carries no information about this manuscript. The
attribution is recorded in `02_journal_options.md` so the decision is auditable rather than tacit.

**No softening of the failing gates.** The first substantive paragraph leads with them on purpose.
An editor who reads "three of four validation gates failed" as a weak paper will reject it either way;
the only version of this letter that can succeed is the one that puts the uninjected control in front
of that reaction rather than behind it.

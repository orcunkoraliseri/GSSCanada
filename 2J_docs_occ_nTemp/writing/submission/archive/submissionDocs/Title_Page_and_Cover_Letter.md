# Title page

*Upload this as a separate file from the blinded manuscript. Building Simulation runs double-blind
review: this file carries every piece of author information, and the manuscript file carries none.*

---

## Cover letter

7 August 2026

Prof. Da Yan
Editor-in-Chief, *Building Simulation*
School of Architecture, Tsinghua University, Beijing, China

Dear Prof. Yan,

We are pleased to submit our manuscript, *From "How Much" to "When": Forecasting the Residential Energy
Load Shape from a Calibrated Behavioural Occupancy Time-Series (Canada, 2005 to 2030)*, for
consideration as a research article in **Building Simulation**.

Stock-scale building energy models still run on static, pre-COVID occupancy schedules, yet the pandemic
changed *when* residential energy is used more than *how much*. We build a calibrated behavioural
occupancy time-series from four Statistics Canada General Social Survey time-use cycles (64,061
diaries), augment it with a gate-selected hybrid conditional Transformer, link it to a
144,507-household 2021 Census frame, forecast it through the work-from-home structural break to 2030
under a True-Future-Test protocol, and carry it into 6,000 paired EnergyPlus v24.2 runs across four
Canadian code archetypes and six ASHRAE climate zones. The headline is a dissociation: weekday at-home
occupancy breaks by +5.2 percentage points at COVID and stays +2.2 to +3.9 points above baseline in
2030, while annual electricity moves only +1.4 to +2.6 per cent. The load *shape*, however, changes
structurally — the midday valley fills, the load factor flattens (both confidence intervals exclude
zero), and the evening peak stays fixed near 17:30.

We are submitting to Building Simulation because the contribution is a simulation-methodological one.
The paper's substance is a gate-validated generative occupancy model, a paired frozen-frame
attribution design that isolates the behavioural channel, and a multi-archetype EnergyPlus campaign
calibrated to national survey benchmarks within ±2.7 per cent in all 48 dwelling-by-year cells. That
is the kind of work this journal evaluates on its merits rather than asking why it matters. The open
cell we occupy is specific: no existing study carries a calibrated, survey-grounded occupancy series
*through* a structural break into stock-scale paired simulation of the resulting load shape.

**Relationship to concurrent work.** This is the second study from a structured research pipeline, and
we want to be explicit about the boundary. A predecessor manuscript, currently under review at the
*Journal of Building Performance Simulation*, asked *how much*: it contrasted period-specific occupancy
datasets against a single default schedule across six Montréal neighbourhood-unit typologies in one
climate zone, and reported annual magnitude corrections. The present paper asks *when*. The
default-versus-cycle magnitude contrast is replaced by a cycle-versus-cycle, within-household paired
contrast; the occupancy series is carried through the COVID break to 2030 rather than stopping at a
synthetic present-day cycle; the domain widens from six neighbourhood units in one climate zone to four
national code archetypes across six; the end uses are anchored to a national household-energy survey
rather than filtered from default profiles; and the primary result is the diurnal load shape rather
than annual totals. Every stage of the pipeline differs — generator, load model, horizon, validation
protocol, and attribution design. What the two share is only the premise that survey-grounded
time-series occupancy can be built for Canadian building energy models at all, which this paper treats
as established and does not re-claim as novel.

The manuscript is original, has not been published previously, and is not under consideration
elsewhere. All authors have approved its submission. We have no competing interests to declare.

Thank you for considering our work.

Sincerely,

Orcun Koral Iseri, on behalf of both authors

---

## Paper title

From "How Much" to "When": Forecasting the Residential Energy Load Shape from a Calibrated Behavioural
Occupancy Time-Series (Canada, 2005 to 2030)

## Authors

Orcun Koral Iseri^1,\*^, Caroline Hachem-Vermette^1^

1. Gina Cody School of Engineering and Computer Science, Concordia University, 1455 De Maisonneuve
   Blvd. W., Montréal, Québec, H3G 1M8, Canada

\* Corresponding author: orcunkoral.oseri@concordia.ca

**ORCID.** Orcun Koral Iseri: https://orcid.org/0000-0001-7735-3363

## Author contribution statement

**Orcun Koral Iseri:** Conceptualization, Methodology, Software, Formal analysis, Investigation, Data
curation, Validation, Visualization, Writing – original draft. **Caroline Hachem-Vermette:**
Conceptualization, Supervision, Funding acquisition, Resources, Writing – review and editing. Both
authors read and approved the final manuscript.

## Compliance with ethical standards

**Declaration of competing interest.** The authors have no competing interests to declare that are
relevant to the content of this article.

**Ethical approval.** This study does not contain any studies with human or animal subjects performed
by any of the authors. The analysis uses anonymized public-use microdata files released by Statistics
Canada.

## Acknowledgements

This postdoctoral research was financially supported by the Natural Sciences and Engineering Research
Council of Canada (NSERC) and the Voltage-Age Seed fund. The authors gratefully acknowledge this
support.

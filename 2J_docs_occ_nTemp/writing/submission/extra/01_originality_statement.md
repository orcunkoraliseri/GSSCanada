# Originality statement — for the cover letter

*Standalone version of the paragraph added to §1.4 of the manuscript. Use as-is in the cover letter,
or as the "statement of originality" many journals request separately.*

---

## Short form (one sentence)

The prior journal paper established *how much* survey-grounded occupancy moves Canadian residential
energy demand against default schedules; this paper establishes *when* — it forecasts the occupancy
series **through** the COVID/work-from-home structural break to 2030 and reads out the diurnal load
shape, using a new generator, a nationally benchmarked end-use model, and a paired within-household
simulation design that the predecessor did not have.

---

## Full form (as inserted in §1.4)

The two studies put different questions to the same survey base. The predecessor asked *how much*: it
contrasted five period-specific occupancy datasets (2005, 2010, 2015, 2022, and a synthetic 2025)
against a single standardised default schedule across six Montréal neighbourhood-unit typologies in
one climate zone, and delivered annual magnitude corrections, residential code calibration factors,
and a first default-referenced reading of peak cooling timing. The present paper asks *when*: the
default-versus-cycle magnitude contrast is replaced by a cycle-versus-cycle, within-household paired
contrast; the occupancy series is carried *through* the COVID/work-from-home structural break to 2030
rather than stopping at a synthetic present-day cycle; the domain widens from six Montréal
neighbourhood units to four Canadian code archetypes across six ASHRAE climate zones; the end uses
are anchored to a national household-energy survey instead of being filtered from default profiles;
and the primary result is the diurnal load shape — midday share, load factor, and peak hour — rather
than annual totals. What this paper carries over, and deliberately does not re-claim as novel, is the
premise that survey-grounded time-series occupancy can be built for Canadian building energy models
at all; what is new is every stage of the pipeline that turns that premise into a forecast load shape.

---

## The contrast, itemised

| Axis | Paper 1 — *Longitudinal Analysis of Occupancy-Driven Energy Demand in Canadian Residentials* | Paper 2 — this submission |
|---|---|---|
| Question | How much does occupancy change annual demand vs. defaults? | When during the day does forecast behavioural change reshape the load curve? |
| Comparison design | Each cycle vs. a standardized default schedule; SSE-matched 100-household ensembles per scenario-neighbourhood pairing | Cycle vs. cycle, paired within-household; 50-household panels frozen inside each cycle-year span |
| Generator | C-VAE + cluster-based vector momentum | Gate-selected hybrid AR/NAR conditional Transformer ("calibrated J3"), post-hoc marginal calibration |
| Temporal reach | 2005–2022 empirical + synthetic 2025 | 2005–2022 empirical + forecast **through** the COVID/WFH break to 2030, True-Future-Test protocol |
| Loads | Presence Filter applied to default end-use profiles | Activity-resolved bottom-up end-use model, SHEU-2019 calibrated (±2.7 % in all 48 cells) |
| Spatial domain | 6 neighbourhood units, Montréal CZ 6A, DOE prototype archetypes | 4 archetypes × 6 cities spanning CZ 5A–7A, NECB 2017 / NBC 9.36 archetypes |
| Simulation scale | 36 scenario-neighbourhood pairings | 6,000 paired EnergyPlus runs, 144,507-household Census frame |
| Headline output | Heating +4–13 %, cooling −10–27 %; code factors +10 % / −20 % | Midday fill and flattening (Δmidday share +0.37 pp, Δload factor +0.012, CIs exclude zero); evening peak fixed at ~17:30 |

*Paper 1 figures above are quoted from its own text; paper 2 figures from §5 of this manuscript.*

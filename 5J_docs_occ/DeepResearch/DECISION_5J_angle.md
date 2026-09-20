# The 5J subject decision

Written 2026-09-19 by the manager, after `RT12` was vetted (`VETTING_RT12.md`, ACCEPTED WITH
STRIKES). This document exists to be ruled on. It opens no plan and starts no work.

Every number and row below comes from a vetting note, never from a report read directly. Where a note
strikes a row, the row is absent here. `RT02`, `RT04`, `RT08`, `RT09`, `RT17`, `RT19`, `RT38` failed
their rounds and nothing is quoted from them; `RT12`'s six strikes are applied in full.

---

## 1. What the ranking actually says once the strikes are applied

`RT12` ranked eleven surviving angles under `S = 0.40 G + 0.30 F + 0.20 D + 0.10 P`, where `G` is how
open the space is, `F` how well it fits assets we already hold, `D` how defensible it is against its
strongest objection and `P` how well it serves a fellowship application. The arithmetic was
recomputed row by row and is exact. Two score corrections and one untested score change the picture:

| Angle | `RT12` score | After the strikes | Why |
|---|---|---|---|
| A9 passive survivability with occupants | 27.0 | **27.0, unchanged** | openness rests on three Part A searches with six logged benchmark abstracts behind them |
| A12 privacy-utility release protocol | 27.0 | **27.0, but openness untested** | its `G = 40` cites only a fact we pasted in ourselves; no question in `RT12` ever searched for an existing protocol |
| A2 occupancy under heat | 24.5 | 24.5 | one nearest work with a logged abstract behind four negative searches |
| A7 records reading with abstention | 24.5 | 24.5 | one nearest work with a logged abstract behind four negative searches |
| A11 zoning bias benchmark | 19.0 | 19.0 | unchanged |
| A3 pretrained sequence generator | 17.0 | 17.0 | unchanged |
| A6 occupancy-resolved energy burden | 24.5 | **16.5** | scored `G = 40` on no search of its own; `RT12`'s own rule makes that 20 |
| A8 Canadian transfer | 16.5 | 16.5 | unchanged |
| A4 the scenario axis | 24.0 | **16.0** | scored `G = 40` on three negative searches with no nearest-work abstract; the rule makes that 20 |
| A13 counterfactual shock synthesis | 16.0 | 16.0 | unchanged |
| A14 activity-travel populations (form 3) | 16.0 | 16.0 | unchanged |

`RT12`'s own sensitivity test matters as much as its ranking: if every openness score of 40 that
rests on searches alone is set to 20, the top becomes a three-way tie between A9, A12 and A11 at
19.0. The ranking is not robust to that assumption. What is robust is that **A9 is in the top group
in every version of the table**, and that no version puts A4, A6, A13 or A14 near the top.

---

## 2. The angles worth ruling on

### A9. Passive survivability under power failure, with occupants

*How many hours a neighbourhood stays inside a habitable indoor band after supply is lost, winter and
summer, with uncertainty, and with occupancy that says who is actually inside* (brief section 4).

**For it.** This is the only angle whose openness was searched from several directions and came back
empty each time. Four search phrasings found no survivability or thermal-autonomy study using
dynamic, household-composition-dependent or demographic occupancy (`RT12` Q5). Six benchmark works
were resolved to real, correct DOIs and none of them varies occupancy dynamically in its abstract:
Sheng 2023, Baniassadi and Sailor 2019, Pulkkinen and Ramesh 2026, Hotchkiss 2026, Sun 2020,
Baniassadi 2018 (`RT12` Q4; all fourteen identifiers in the report were independently re-resolved and
all fourteen matched). Three earlier reports agree the space is open on exactly two terms, occupancy
that varies with who lives there and district scale (`P21`, from `VETTING_RT15`, `VETTING_RT11`,
`VETTING_RT01`). It is feasible on paper with what we hold: `RT10`'s blocker analysis leaves A9 and
A7 as the two angles with no input blocker, and the weather-morphing tool it needs is now pinned to a
real, reachable, MIT-licensed package at version 2.2.0 (`RT12` Q1, which repairs the one `RT10` row
that had been struck for a dead repository).

**Against it.** The nearest neighbour of this angle has never been read. Hobson and Brideau 2026,
"Exploring Key Performance Indicators for Thermal Resilience in Canadian Multi-Unit Residential
Buildings", is real and correctly identified, but `RT12`'s claims about what it contains have no
source: CrossRef carries no abstract for it and the publisher page is bot-blocked, so the statements
that it is about extreme heat and that it did not evaluate winter outages are unsupported
(`VETTING_RT12` strike S1). Separately, the older claim that a Canadian winter-outage study already
exists (`P24`, Baba et al. 2022) was never settled: `RT12` said the thesis behind it is about
overheating, but the page it cites is an unrelated philosophy project, so we still do not know what
that thesis contains (strike S2). The searches behind "nothing published" were independently re-run
and hold; the two citations are what fail. The standing scientific objections are that indoor
temperature decay during an outage is dominated by envelope air leakage and window habits we have not
measured, so occupant heat gain may be a second-order effect (`RT02` G via the ideas ledger; `RT12`'s
own stated objection for A9).

**What is owed before it is committed to.** One thing: the Hobson and Brideau abstract or full text,
from ASHRAE. If that paper already couples occupancy to winter outage performance in Canadian
multi-unit buildings, the openness argument for A9 weakens sharply. Nothing else in the file is
waiting.

### A12. Privacy-utility and release protocol

*A short paper on releasing a generator trained on survey microdata, built from 4J's pre-registered
membership-inference audit and the partial release that followed it* (`P34`).

**For it.** It is the cheapest thing on the list. It uses assets already finished and already audited
in 4J and needs no new simulation campaign, which is why it scores highest of all angles on fit to
what we hold. `RT12` scores it equal first and `RT12`'s programme-fit-free sensitivity test puts it
first outright.

**Against it.** Its openness has never been tested. Its only evidence is `P27`, a fact we wrote
ourselves from `VETTING_RT18`, and no question in `RT12` searched for an existing audit or release
protocol; every other top score rests on at least one logged search (`VETTING_RT12` strike S4). The
tie with A9 at 27.0 is therefore not a tie on evidence. The standing objection is blunt and was
recorded early: withholding weights after a failed audit is an ethics decision, not a finding (`RT18`
D via the ideas ledger), and the protocol would be generalised from a single fine-tuned 7B model that
missed its transfer gate. It also has no custodian sign-off.

### A2. Occupancy under heat

*Time-use-derived presence and activity combined with extreme or future weather to estimate
occupancy-resolved indoor heat exposure at district scale* (brief section 4).

**For it.** Four search phrasings found no study combining national time-use presence sequences with
building thermal models at scale; the nearest work, Papanikolaou and Droste 2026, is a single
living-lab dwelling with no survey time use (`RT12` Q6, abstract logged and re-confirmed).

**Against it.** `RT10` narrows it to tract-level aggregation because of its data-access blocker, and
the ledger's objection stands: without paired indoor sensors in dozens of dwellings, the overheating
result cannot be validated at the address.

### A7. Language models reading building records with abstention

**For it.** Four search phrasings found no study using language models to read building records with
abstention or prediction sets; both nearest works were identified and one of them, Borrotti 2024, has
a logged abstract confirming it does no text extraction (`RT12` Q7). `RT10` finds no input blocker.

**Against it.** It leaves the method spine of the five-paper series: no occupant presence, no time
use, no thermal simulation. European energy-certificate registers are already structured, which makes
the language model redundant there.

### The rest, briefly

A11 (zoning bias) is a technical note inside OpenUBEM, not a paper, and `RT12` settled its missing
number: Shoeboxer reports five to 10 percent annual energy-use error against compliant multi-zone
models while running 296 times faster (`RT12` Q9, quotation verified verbatim). A3 in foundation-model
form is closed: BuildOcc exists, is real at both arXiv and Zenodo, is ATUS-grounded, and predates
this report (`RT12` Q11). A14 in smart-thermostat form stays closed on licence grounds; the ecobee
research terms cannot be read on any public page (`RT12` Q10). A4, A6, A8, A13 all fall below 17.0
once the strikes are applied.

---

## 3. Programme fit: we do not have it

`RT09` failed both of its rounds, so no angle-by-programme fit table is admitted from anywhere in
this series. The `P` column in `RT12`'s ranking is therefore the weakest column in the table, and
`RT12`'s own second sensitivity test shows what happens without it: A12 moves to first and A9 to
second. Only three programme facts survive independent checking, and none of them is about an angle:

* The UC President's postdoctoral programme, under which Berkeley's Climate Futures fellowship is
  listed, closes on 1 November 2026 (`P36`).
* The NSERC postdoctoral award closes on 17 October, and its page requires the research to be
  significantly distinct from, or to go significantly beyond, the doctoral thesis (`P37`).
* The Marie Sklodowska-Curie mobility rule and Digital Futures's own theme labels were confirmed;
  everything else `RT09` said about criteria, weightings and award history is struck.

Two consequences. First, the NSERC distinctness rule is a real constraint on whichever angle is
chosen and should be read before the application text is drafted, not after. Second, every 2026
deadline precedes any plausible 5J preprint, so 5J serves the 2027 cycle; the choice should not be
bent toward a programme it cannot reach in time.

---

## 4. Recommendation

**Choose A9, and write A12 as a short companion paper from the 4J assets already in hand.**

The reason is that A9 is the only angle whose openness was tested by searches that were themselves
re-run and confirmed by our own checker, and it is the only top-group angle that both fits what we
hold and has no input blocker. It survives in the top group under every version of `RT12`'s table,
including the pessimistic one. A12 is worth writing because it is nearly free, but it cannot lead:
nobody has yet looked for an existing protocol, and until somebody does, its first-equal rank is an
artefact of a score we supplied ourselves.

This recommendation is conditional on one fact we do not have. If Hobson and Brideau 2026 turns out
to couple occupancy to outage performance in Canadian multi-unit residential buildings, A9's openness
claim is damaged and the choice should be re-opened in favour of A2. Obtaining that paper is the
first action under option (a), before any plan document is written.

Options:

* **(a)** A9 as the 5J subject, A12 written in parallel as a short protocol paper. First action:
  obtain Hobson and Brideau 2026 from ASHRAE.
* **(b)** A9 alone, A12 dropped.
* **(c)** A12 first, because it needs no new simulation, with A9 held for 6J.
* **(d)** A2 instead, accepting tract-level aggregation.

Waiting on you: D-5J-1, recommend (a).

---

## Ruling

**D-5J-1: (a) — RULED 2026-09-19 by the author.** A9 is the 5J subject; A12 is written in parallel as
a short companion paper from 4J assets. First action owed before any plan document is written:
obtain Hobson and Brideau 2026 ("Exploring Key Performance Indicators for Thermal Resilience in
Canadian Multi-Unit Residential Buildings") from ASHRAE and check whether it couples occupancy to
winter outage performance. If it does, this ruling is reopened in favour of A2.

**Read 2026-09-19: the condition does not fire, A9's openness claim survives.** The paper is entirely
about a **summer heatwave/extreme-heat** scenario (mechanically cooled midrise apartment, five
climate-zone simulations, three future TMY periods plus one heatwave-year outage), never a winter
outage. Occupancy is NECB 2020's single fixed schedule (Table A-8.4.3.2.(1)-J), the same for every
zone and every simulation, and the paper states explicitly that "the occupancy schedule remains
unchanged for all simulations" during the outage run — it is not dynamic, not household-composition-
dependent, and not demographic in any sense. So Hobson and Brideau 2026 does the opposite of what
would have damaged A9: it neither touches winter outages nor couples occupancy to outage performance.
Ruling stands as (a); no reopening in favour of A2. **Copyright note:** the PDF's footer states its
content "may not be used with any artificial intelligence tools or machine learning technologies" —
flagged for the author's awareness; only a factual scope check (season, occupancy treatment) was
extracted here, no text reproduced.

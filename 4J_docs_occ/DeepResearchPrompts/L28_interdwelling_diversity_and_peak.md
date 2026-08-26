# L28. Does inter-dwelling occupancy diversity change building peak demand — and by how much, as a function of how many dwellings are modelled independently?

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C, E and F used. Section D: answer `not applicable to this prompt` unless a recommendation
implies hardware we do not have.

**This prompt is for Step 10** (`Step10_docs/4thJ_10_ubemRealStock.md`), which is new scope added
2026-08-26. Read that document's §1 before answering if it is available to you; if it is not, everything
you need is below.

---

## Why we are asking, and what we have already measured ourselves

Our Step 8 EnergyPlus campaign is finished, and it returned a **null**. 440 scenario-cells, 4,048
EnergyPlus runs, 31,687 scored band rows, zero gate failures — and after a corrected re-run, the
occupancy effect does not survive on either channel at full injection. Annual medians are negative; the
peak effect's ratio to the between-diary spread is 0.54 / 0.02 / 0.40 across our three folds (Spain, UK,
Italy). One thing survived: the effect is **monotone in dwelling class** in all three folds — apartment
blocks above multi-family above terraced.

The design that produced that null had a specific property. Each simulation cell was **one TABULA
archetype box driven by one occupancy diary**. Every dwelling-equivalent inside an apartment-block
archetype therefore shared a single presence series. Our next step replaces this with **real building
footprints subdivided into dwellings, each carrying an independently sampled diary**.

Before we spend that campaign, we want to know what the literature already says, because if this question
is settled we should cite it rather than re-measure it — and if the effect size is known to be small, the
step needs redesigning or dropping.

**We are not asking whether stochastic occupancy matters.** We already hold the standard claim (15–50 % on
annual space heating, 100–300 % on dwelling peak electrical demand, relative to static standard
schedules). We are asking something narrower and, as far as we can tell, less often stated.

---

## What we need

### Item 1. The core question — diversity as a function of `N`

Does the published evidence quantify how the **building-level or aggregate** peak-demand effect of
stochastic occupancy scales with **`N`, the number of dwellings modelled with independent occupant
profiles**?

Specifically:

1. Any study that reports the same building or stock simulated at **more than one value of `N`** —
   e.g. one shared profile for a whole block versus one profile per flat — and reports the difference.
2. The functional form, where one is reported. Coincidence-factor and diversity-factor literature from
   electrical distribution planning is directly relevant here; if the building-energy literature has not
   answered this but the distribution-network literature has, **say so in Section A** and give us the
   distribution-network answer instead.
3. The value of `N` at which the diversity effect **saturates**, if one is reported.
4. Whether the effect direction differs between **thermal** peak (heating/cooling power) and
   **electrical** peak. Our own result is that our occupancy channel is far weaker on annual demand than
   on peak, so the channel separation matters to us.

### Item 2. Is our null already in the literature?

Find any published work reporting that **stochastic occupancy made little or no difference** at building
or stock level, and say under what conditions. Negative results are under-published and we would rather
find ours has company than discover it in review. In particular:

1. Studies where the occupancy effect was **smaller than the between-profile spread** — i.e. the noise
   exceeded the signal, which is exactly our `FINDING 134`.
2. Studies where a **conserved-mean** injection (annual mean internal gain held constant, only the
   temporal distribution changing) produced a much smaller effect than a study that also changed the
   mean. **This distinction is critical to us**: our injection holds the annual mean internal gain at
   exactly 3.0 W/m² at every level, so we redistribute time and never energy. We suspect part of the
   published 15–50 % range comes from studies that changed both. Tell us if that is right.

### Item 3. Heavy-mass European envelopes

Does building thermal mass suppress the occupancy signal, and is that quantified? Our envelopes are
European residential — clay brick and concrete, internal mass on the order of 45 Wh/(m²·K), with
87 Wh/(m²·K) cited for Italy and 32.8 for Great Britain. If heavy mass damps sub-daily gain
redistribution to the point where a conserved-mean injection cannot move annual demand, that is a
physical explanation for our null and it belongs in our discussion, with a citation.

### Item 4. What an honest test looks like

Given items 1–3: what is the **minimum design** that could detect a diversity effect if one exists?
We need this to size our campaign and to pre-register a vacuity threshold. Please give:

1. A minimum number of buildings per stratum, with the reasoning.
2. Whether the comparison should be within-building (same building, `N = 1` vs `N = N_u`) or
   between-building, and why.
3. What must be **held constant** for the comparison to be attributable to diversity rather than to
   geometry, weather or archetype.
4. The metric most likely to show the effect if it is there — annual peak, peak-day profile, coincidence
   factor, load-duration curve, or something we have not named.

---

## Constraints you must respect in your answer

* **Our injection conserves energy.** `φ_int(t) = (1−f)·3.0 + f·3.0·g(t)/mean(g)`, with
  `f ∈ {0.00, 0.15, 0.30, 0.50, 1.00}` and the annual mean exactly 3.0 W/m² at every `f`. A
  recommendation that requires changing the mean is a **design change** and must be labelled as one in
  Section C, because it would break our control.
* **No thermostat schedule may be introduced.** Intermittency stays a transmission scalar on UA; a
  scheduled night setback would confound the occupancy signal we are isolating.
* **Three countries only:** Spain, United Kingdom, Italy. France appears in our engine's site list but has
  no time-use fold in this paper.
* **We are held to a held-out-fold discipline**: a dwelling in a country's campaign may not carry a diary
  from the fold that held that country out.

## What we do not need

* A general review of occupancy modelling. We have it.
* The CREST / Widén / LoadProfileGenerator / RAMP appliance literature — covered by `RL25`.
* European archetype libraries and TABULA — covered by `RL13`.
* Day-to-year chaining of single diary days — covered by `RL21`, and we closed that decision empirically
  on 2026-08-25.

## What would change our mind

If the answer to Item 1 is that **`N` is already known not to matter** for conserved-mean injections in
heavy-mass residential stock, say it in the first sentence of Section A. That finding would stop a
campaign, and `stop` is a permitted value in Section C.

# 3J Leg-3 v2 Deep Research: Master Brief (paste this block ahead of EVERY prompt)

This brief gives the shared context for the V-series prompts (`V01`, `V02`, `V03`, ...). Read it, then
answer only the prompt that follows it. Do not restate this brief in your answer.

---

## 1. What we are doing

We build occupancy schedules from Canadian time-use and census microdata and inject them into an
EnergyPlus model of a mixed-use tower, then ask whether the simulated energy is plausible. The
occupancy work is finished and frozen. What is not finished is the **validation layer**: several
plausibility gates compare our as-modelled energy-use intensity (EUI) against reference bands, and
three of those gates fail. Eight simulation campaigns have failed to move them.

The reason we are commissioning external research is that the failures have been traced **out of the
occupancy model entirely**. An uninjected control run, with no occupancy schedules applied at all,
already sits below the office band floor. So the gates are not measuring what they were built to
measure, and the question has become whether the **reference bands themselves** are correctly derived.
That is a literature question, not a simulation question.

## 2. The building and the four channels

One mixed-use tower, modelled in two heights (`Tall`, `SuperTall`) and two cities (`MTL` Montreal,
ASHRAE climate zone 6A; `CLG` Calgary, climate zone 7A). Four occupancy channels coexist as native
spaces in the same IDF: **residential**, **office**, **retail**, **hotel**. A 56-cell campaign crosses
scenarios with the two heights and two cities.

The IDF vintage matters and is the crux of several prompts: the archetype is
`TallBuilding_90.1-2019_..._NECB17_..._v242.idf`, that is **ASHRAE 90.1-2019 / NECB 2017**. Heating is
**fossil fuel**: `Boiler:HotWater`, natural gas, nominal thermal efficiency 0.813. This is a
gas-heated, recent-code building, and any reference figure offered to us must be matched on both
counts or explicitly labelled as unmatched.

## 3. The gates that are blocked

* **`S9-EUI-office`** requires all-fuel site EUI inside **100 to 200 kWh/m2.yr**, central 135. Our
  as-modelled office channel reads about **85.4**, and the **uninjected control also reads 85.45**, so
  no occupancy change can move it. Two mechanisms have been tested and refuted: envelope exposure
  (correlation of the wrong sign) and a Service/MEP accounting rebase (moves all 56 cells down).
  Diagnosis to date: the shortfall is concentrated in **space heating**, about 17 percent of office
  site energy against a reference share of 35 to 45 percent.
* **`S9-EUI-hotel`** uses a ceiling of **300 kWh/m2.yr**. That ceiling is correctly traceable to a
  local DOE-prototype table (Large Hotel, climate zone 7, **302.2 kWh/m2.yr**), but the prose that
  justifies it cites reports that do not support it, including one report number that turns out to be
  a nuclear-materials document and another that does not resolve at all.
* **`S9-EUI-retail`** has been demoted to informational because its two candidate references disagree
  in direction.

## 4. The suspected defect, stated plainly so you can try to refute it

The reference tables underpinning the office and hotel bands are the **ASHRAE 90.1-2004** baseline DOE
prototype set. The building being judged is **90.1-2019 / NECB 2017**. Codes have tightened across the
2004, 2010, 2013, 2016 and 2019 cycles, so a 2019-code building should sit **below** a 2004-derived
figure by construction. If that is right, the bands are mismatched to the model on vintage, which is
the same class of error as comparing conditioned floor area against gross floor area, or all-fuel
against electricity-only.

We want this **tested, not confirmed.** If the vintage explanation is wrong, say so.

## 5. What is already researched, and must not be redone

* The occupancy model itself, its calibration and its schedule products. Frozen, out of scope.
* Whether the failures are caused by occupancy. Answered: they are not. Do not re-open it.
* The retail time-of-day shape references. Settled separately.
* The internal load densities (occupant, plug, lighting) for the office channel. Already established
  as reference-typical in absolute terms, so they cannot be the source of the office shortfall.

## 6. Source-quality rules (apply to every prompt)

1. **Tier 1 (preferred)**: the standards and codes themselves (ASHRAE 90.1 editions, NECB 2011/2015/
   2017/2020, the National Building Code of Canada); the **primary simulation result sets** behind the
   DOE/PNNL commercial prototype building models, including per-climate-zone scorecards and results
   workbooks published by the US DOE Building Energy Codes Program; CanmetENERGY BTAP archetype model
   documentation and its published result sets.
2. **Tier 2**: government and agency statistics and technical reports: NRCan CEUD and SCIEU tables,
   NRCan and CanmetENERGY archetype and benchmarking publications, Natural Resources Canada ENERGY
   STAR Portfolio Manager Canada data snapshots, US EIA CBECS, PNNL and NREL technical reports where
   the report number has been **verified by opening the document**.
3. **Tier 3**: peer-reviewed literature on building stock energy modelling, occupant behaviour and
   occupancy aggregation, and the IEA EBC Annexes (notably 66 and 79).
4. **Rejected**: blogs, vendor marketing, undated PDFs, AI-generated summaries, and any figure that
   cannot be traced to a named document with a year.

Every numeric value must carry: value, unit, the source's own wording or table reference, document
title, year, and a URL or stable identifier. Where a value is an inference, say so and give the
assumption.

## 7. Answer discipline

* Answer only what the prompt asks.
* **A citation is not evidence until opened.** Report only figures you have actually read in a source
  you reached. Anything unreachable is `COULD NOT OPEN`, never a confirmation. State per claim whether
  you read the full text, only the abstract, or neither.
* **Verify every DOI and every report number before citing it.** For DOIs, fetch
  `https://api.crossref.org/works/<DOI>` and confirm the returned title, first author, journal, volume
  and year. For technical report numbers, open the actual document and confirm its title. This project
  has already been burned badly: in one internal report **9 of 15 DOIs resolved to unrelated papers**,
  several of them one character away from the correct DOI, and a cited PNNL report number turned out to
  be a nuclear-materials study.
* **Never propose relaxing a band because our model fails it.** Any band endpoint you propose must
  rest on external published sources you have opened and quoted, each endpoint cited separately. If
  your reasoning at any point runs "our value is X, therefore the limit should be below X", stop: that
  is the exact failure mode this project keeps repeating. Deriving a threshold from the results it is
  meant to judge is not evidence.
* **`NOT FOUND` is a valid and valuable answer.** If a value cannot be sourced, write `NOT FOUND` and
  say what you searched for. Do not invent a plausible number, and never silently substitute a US
  value for a Canadian one, a national average for a climate-zone-specific one, or a metered value for
  an as-modelled one.
* Keep **as-modelled** (simulated, code-compliant prototype) and **empirical** (metered, surveyed,
  benchmarked) strictly separate and separately labelled. Our gates score as-modelled values. An
  empirical figure is context, never a band input.
* For every EUI figure, record the full basis: as-modelled or empirical; all-fuel or electricity-only;
  conditioned floor area or gross floor area; site or source energy; heating fuel; climate zone;
  code vintage; prototype and its floor area. Convert everything to **kWh/m2.yr** and show the
  arithmetic. 1 kBtu/ft2.yr = 3.15459 kWh/m2.yr. 1 GJ/m2.yr = 277.778 kWh/m2.yr.
* Report negative results. Phrase them precisely as absence of evidence, not as evidence of absence.
* Return results in the schema given by `_RESPONSE_TEMPLATE.md`.
* No em dashes and no en dashes in the output text.

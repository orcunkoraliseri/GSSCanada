# `D-S8-4` — the weather basis, and the station the archetypes are actually run on

**Status: 🟢 CLOSED 2026-08-25.** Ruled by the author in the same message that
raised it, and implemented the same evening. Work item 8.2 is closed with it.

---

## 1. What the author ruled

> "pas nécessaire de choisir de l'année exacte — tu peux choisir des autres années
> ou TMY méthode qui constituent plus d'années, ça marche pour nous aussi"

**The exact meteorological year is not required. A typical year assembled from
many years is acceptable.** This *reverses* section 6 item 6, ruled 🟢 on
2026-08-21 as *diary-survey-year actual weather* (`es` 2009-2010, `uk`
2014-2015, `it` 2013-2014).

The reversal is recorded here rather than by editing the 2026-08-21 entry. The
old ruling stays legible in the progress log with its own reasoning intact; this
brief is what supersedes it.

🟢 **`prereg.md` is not touched and does not need to be.** It was checked:
`Step6_docs/outputs_step6/prereg.md` contains no weather clause at all, md5
`e4243e07cdd80c9c846b91f40e3e8c45`, unchanged. The pre-registered *reporting*
rule that came with the old ruling lived in the Step 8 progress log, and §5 below
says what happens to it.

---

## 2. The reversal is a gain, and the 2026-08-21 entry says so in its own words

The old ruling's cost was written down the day it was made:

> "Under a shared weather year the only thing differing across folds is the
> country and the transfer to it. Under this ruling **two things differ at
> once**, and the windows are five years apart at the extremes. So a cross-fold
> difference in heating demand can no longer be attributed to the LOCO transfer:
> part of it is that Spain's winter and the UK's winter were different winters."

A single shared base period removes that confound. It leaves the list of
country-correlated asymmetries (`FINDING 53`, `D-S6-2`, `FINDING 51`,
`FINDING 60`, `FINDING 110`/`117`) one item shorter than it was this morning —
and §6 below adds a new one, so the net is honest rather than flattering.

---

## 3. What was actually acquired

**Source.** `climate.onebuilding.org`, the repository the author pointed at.
Checked before use, and it settles one question by itself: **it publishes TMYx
only.** Every one of the 107 Spanish, 197 British and 148 Italian files carrying
the 2009-2023 tag is a *typical* year; there are no actual-year files there. Had
the old ruling stood, that site could not have served item 8.2 at all.

**Base period: `TMYx.2009-2023`, the same for all three folds.** OneBuilding
publishes several vintages (2004-2018, 2007-2021, 2009-2023, 2011-2025, plus a
full-record `TMYx`). Mixing vintages across folds would put back exactly the
asymmetry the reversal removes. 2009-2023 is not an arbitrary pick among them:
**it is the only published 15-year window that contains all three original
fieldwork windows** — `es` 2009-2010, `uk` 2014-2015, `it` 2013-2014. The years
that were abandoned are inside the base period of the typical year that replaced
them.

**One EPW per fold, because there is one climate region per fold.** Read from the
parameter tables, not assumed: `es` → `ES.ME` (24 archetypes), `uk` →
`GB.Temperate` (32), `it` → `IT.MidClim` (32). The tool fails loudly if that ever
stops being 1.

---

## 4. The station was MEASURED, not quoted

TABULA gives no coordinates. It gives climate-region codes — and, in
`Tab.AuxCalc.Climate` of `tabula-calculator.xlsx`, the **twelve monthly mean
external temperatures** `theta_e_01..12` each code stands for. Twelve published
numbers per region is enough to select a station instead of assuming one:

```
    score(station) = RMSE over the 12 months of
                     ( EPW monthly mean dry bulb  -  TABULA theta_e_MM )
```

44 candidate stations were downloaded and scored — 11 Spanish, 10 English, 23
Italian — each shortlist including a **deliberate control that should lose**, so
the score can be seen discriminating rather than merely agreeing with a prior.

| fold | region | station | WMO | lat / lon / elev | score | worst candidate |
|---|---|---|---|---|---|---|
| `es` | `ES.ME` Mediterranean | **Valencia.Viveros** | 082850 | 39.483 / −0.383 / 11 m | **0.620** | Madrid-Barajas **3.57** |
| `uk` | `GB.Temperate` England | **Birmingham.AP** | 035340 | 52.454 / −1.748 / 100 m | **0.533** | London St.James Park **1.69** |
| `it` | `IT.MidClim` Zone E | **Torino.Venaria** | 160600 | 45.131 / 7.618 / 278 m | **1.043** | Roma-Ciampino **4.58** |

🔴 **Both controls lost, and that is the interesting part.** `RL27` — the deep-
research response that has been sitting in `DeepResearchPrompts/` since
2026-08-22, **uncited by any document in the project and never vetted** — answers
its question B12 with "Madrid Barajas for Spain (`ES.ME`), London Kew/Heathrow
for Great Britain, and Rome/Bologna for Italy". Measured against TABULA's own
published monthly temperatures, those three are respectively the **worst**
Spanish candidate (3.57 against 0.62), a **2.8× worse** English one (Heathrow
1.47 against 0.53), and the **worst** Italian one (Rome 4.58; Bologna 2.82,
against 1.04). Two of the three name a climate region TABULA does not describe:
`ES.ME` is Mediterranean, and Madrid is not; `IT.MidClim` is Zone E, and Rome is
Zone D. **`RL27` B12 is not usable and is now marked so.** Nothing else in
`RL27` has been vetted either — treat every other row in it the same way until it
is.

---

## 5. What happens to the old ruling's reporting rule

The 2026-08-21 entry pre-registered: *"the headline effect is quoted WITHIN fold.
Any cross-fold comparison of absolute demand must name the meteorological year in
the same sentence as the country."*

🟢 **The rule is kept, not dropped**, and it now costs nothing: all three folds
name the same base period, `TMYx.2009-2023`, so the second sentence is satisfied
by construction. The first sentence is load-bearing for a new reason — §6.

The containment `D-S8-2` built still holds exactly: every level of
`f ∈ {0, 0.15, 0.30, 0.50, 1.00}` inside one fold runs on the **same** EPW, so
the occupancy effect — the difference across `f`, within a fold — is weather-free
by construction. That is the number the paper is about, and no part of this
decision touches it.

---

## 6. 🔴 `FINDING 120` — the station is a free parameter worth 5 to 11 % of heating demand, chosen on a margin far smaller than that

The UK winner beat its runner-up by **0.002 K** of score: Birmingham 0.5333,
Nottingham-Watnall 0.5351. That is not a choice, it is a coin flip. So the coin
was made to show its consequences: **all 88 archetypes were run twice**, once on
the installed EPW and once on the fold's runner-up, 176 EnergyPlus runs.

| fold | score margin | median heating EUI, winner | runner-up | median \|Δ\| | max \|Δ\| |
|---|---|---|---|---|---|
| `es` | 0.620 → 0.746 | 24.9 kWh/m² | 27.3 | **10.7 %** | 36.6 % |
| `uk` | 0.533 → 0.535 | 104.5 kWh/m² | 110.8 | **5.4 %** | 6.0 % |
| `it` | 1.043 → 1.072 | 81.0 kWh/m² | 74.8 | **8.4 %** | 11.2 % |

🔴 **The sign is not the same in every fold.** Spain's runner-up runs *warmer*
demand, Italy's runs *colder*. So the residue is not a common offset that divides
out of a cross-fold ratio — it is country-correlated, in the same class as
`FINDING 110`/`117`, and of the same order as the 6.1 pp geometry residue that
`D-S8-3` spent a whole decision reducing.

**What this does and does not threaten.** It does not touch the occupancy effect:
`f = 0` and `f = 1` share one EPW, so the station cancels exactly. It *does* mean
**no cross-fold comparison of absolute demand is safe to ±10 %**, and the
within-fold reporting rule of §5 is what stands between the paper and that error.
Nothing here should be quoted as "the Spanish stock uses 24.9 kWh/m²".

⚪ **An untaken follow-on, recorded and NOT acted on** — it is a new rule, not an
application of this one, and it needs a ruling: run each fold on the mean of its
top-`k` scoring stations, or report every result as a band across them, instead
of committing to one station whose margin is 0.002 K. It would convert a hidden
±10 % into a stated interval. It would also multiply the campaign by `k`.

---

## 7. Two smaller findings, both from measuring rather than quoting

🔴 **`FINDING 118` — one climate region, two spellings, in one TABULA release.**
The archetype parameter tables carry `GB.Temperate`; `tabula-calculator.xlsx`
carries the same region as `GB.England-Temperate`. `ES.ME` and `IT.MidClim` agree
across both workbooks; only Great Britain does not. The alias is written
explicitly in `tools/4thJ_step8_weather.py` and the lookup **fails loudly** on a
miss rather than falling back to a default — a silent fallback here would have
scored the British stations against nothing and picked the first one.

🔴 **`FINDING 119` — TABULA's `HeatingDays` is not the statistic it looks like,
and comparing an EPW to it directly manufactures a false gap.** TABULA derives
`HeatingDays` and `Theta_e_HeatingSeason` from **monthly** means by a fractional
formula — `ES.ME` gets `HeatingDays_01 = 21.5`, not 31, and 22.4 for the whole
year. The obvious EPW statistic counts **daily** means below the 12 °C base. On
the *same* climate the two differ by a factor of three: Valencia.Viveros scores
0.62 K on the twelve monthly means TABULA publishes, yet shows 72 "heating days"
against TABULA's 22, purely because daily scatter crosses a threshold a monthly
mean of 11.0 °C never crosses. Scoring on it would have rejected every real
Spanish coastal station and picked something absurd. **It is measured, recorded
per station, and deliberately not scored.** Anybody who re-derives the 22-vs-72
gap has re-derived an artefact.

⚪ **Annual solar, measured and not scored.** All 44 candidates come out *above*
TABULA's published `I_Sol_Year_Hor`, by +2 % to +20 %, so it separates stations
much less than it appears to and carries a systematic offset of its own. The
installed files sit at `es` **+9.8 %**, `uk` **+6.7 %**, `it` **+3.0 %** — same
sign in all three folds, 6.8 pp of spread. Recorded in the manifest per fold;
not optimised away.

---

## 8. What was built, and what proves it

| Artefact | What it is |
|---|---|
| `tools/4thJ_step8_weather.py` | acquisition + selection, re-runnable, `--offline` from the cache |
| `tools/4thJ_step8_weather_selftest.py` | the gate, 12 checks in two halves |
| `outputs_step8/weather/*.epw` | the three installed files |
| `outputs_step8/weather/_cache/` | all 44 downloaded zips, kept so the md5s stay checkable |
| `outputs_step8/weather_manifest.csv` | fold, region, station, WMO, coordinates, source URL, zip md5, EPW md5, score, runner-up, GHI |
| `outputs_step8/weather_selection_report.json` | every candidate, every score — the losing 41 included |

**Selftest: 12 ok, 0 FAILED.** The half that matters is `B2`: one archetype per
fold is run, and the `Site:Location` line **EnergyPlus itself writes** into
`eplusout.eio` is read back and matched against the manifest — WMO number,
latitude, longitude, elevation. A manifest row saying "this run used Birmingham"
is a claim; `Site:Location,Birmingham.AP ENG GBR SRC-TMYx WMO#=035340,52.45,...`
is a measurement. `3J`'s inherited `PLATFORM` field is the precedent.

**Injection battery: 9 of 9 seen felling their target, baseline clean, so the
coverage clause is not vacuous.** Truncate one hour → `W3`. Write a missing-value
sentinel into a dry bulb → `W4`. Corrupt a recorded md5 → `W2`. Mix a second TMYx
vintage into one fold → `W6`. Move a station half a degree → `W7`. Overwrite the
recorded score → `W8`. Install the runner-up with the manifest made **fully
self-consistent** → `W9`. Reduce a candidate set to its winner → `W10`. Swap two
folds' EPW *content* behind an intact manifest → `B2`, caught by EnergyPlus.

---

## 9. What changed in the 8.1 artefacts, and why they were rebuilt

Every one of the 88 IDFs carried `!- NOTE : no Site:Location and no RunPeriod
weather --- item 8.2 is open.` That is now false, and a false provenance line
stamped into the artefact is the defect class this project already has a
precedent for. `tools/4thJ_step8_idf.py` was corrected in three places (the
header note, the `RunPeriod` comment, and the ground-temperature provenance row),
**the 88 IDFs were rebuilt, and the full 8.1 selftest was re-run: 26 ok, 0
FAILED**, B1 all 88 running with zero severe errors, B3 worst deviation
0.00050 W/(m²·K). No geometry, no construction and no schedule changed — the diff
is comments — but the md5s did, so the manifest was rewritten and re-checked
rather than left to drift.

⚪ The ground-temperature row was corrected in substance, not just in wording:
closing item 8.2 does **not** give the model ground temperatures. EnergyPlus does
not read the EPW header's ground temperatures unless a `Site:GroundTemperature`
object points at them, and none is written. It is still an E+ default, and it is
now written down as one.

⚪ Half B of the 8.1 selftest still runs on EnergyPlus's own Chicago file, now on
purpose rather than by necessity: a U-factor round-trip must not depend on
climate, and running it on the study's EPWs would let a weather regression pass
itself off as an envelope result.

---

## 10. Backups

All verified non-empty before writing: `archetype_idf_manifest.csv.bak_ds84`
(the pre-rebuild manifest). The `.bak_ds83` set from `D-S8-3` is untouched.
`prereg.md` untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`.

---

## ADDENDUM, 2026-08-28 — the follow-on is RULED: **NOT TAKEN**

🟢 **The top-`k` station mean, and the reported-band variant, are both DECLINED.** The author
delegated the choice to this session on 2026-08-28. Each fold keeps the single station selected by
measurement in §4; no EPW is re-selected, and the Step 8 / Step 9 campaigns are **not** re-run.

🔴 **Why.** §6 of this brief already establishes the decisive fact: `f = 0` and `f = 1` share one
EPW, **so the station cancels exactly out of the occupancy contrast**. The follow-on would multiply
the campaign by `k` — on 13,108 rotated runs — to put an interval around a **level** that no
published claim rests on, while leaving every **contrast** it could affect unchanged. `FINDING 120`'s
5–11 % is real, and it is a reason to state a limitation, not a reason to buy one.

⚪ **What is carried instead.** The §5 within-fold reporting rule stands as the binding one: **no
cross-fold comparison of absolute demand is safe to ±10 %**, no result is ever quoted as *"the
Spanish stock uses X kWh/m²"*, and `FINDING 120` is published as a declared limitation naming the
0.002 K selection margin. ⚪ The `EU-10` dossier applies the same discipline independently, by naming
the meteorological year beside the country in any cross-fold sentence.

⚪ **Reopen trigger, one only.** A published claim that compares **absolute** demand across folds.
Nothing else reopens it.

**Status: follow-on RULED — NOT TAKEN. `D-S8-4` is CLOSED in full.**

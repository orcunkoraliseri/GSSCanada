# P17 — Measured household peak hours vs real-diary appliance peaks — implementation state
Task doc:   this file (author decision A5, 2026-09-23: "if it gives higher accuracy for validation, let's do it")
Status:     IN PROGRESS (rule fixed; no source file opened yet)
Routes:     `DeepResearchPrompts/VETTING_RL36.md` section 3 (nothing numeric from RL36 may be used)

## What this check can and cannot do
It does not make the model more accurate. It tests one claim the paper now makes: that REAL diaries put the
appliance evening peak at a country-specific hour (UK 18:00, Italy 19:00, Spain 21:00; P3 result table,
`P3_appliance_real_and_donor.md:129-131`). If measured household data peak at the same hours, that claim gains
outside support. If they do not, the claim is reported as unconfirmed. Either outcome goes in the paper.

## Comparison rule (FIXED 2026-09-23, before any source file was opened)
1. Our quantity: peak hour of the stock-mean electricity profile from the appliance model run on REAL diaries
   (P3 table; all days of one year, 100 dwellings). Compared value = the daily maximum hour, never a secondary peak.
2. Measured quantity: the hour of the daily maximum of the measured mean profile. Day set: all days of the year
   if available (matches ours); weekday-only reported alongside, never substituted. Half-hourly data: hour = the
   clock hour containing the maximum half-hour (period starting 18:30 -> 18:00).
3. Agreement: |measured hour - our hour| <= 1 h = "consistent"; otherwise "not consistent". The exact
   difference in hours is always reported. No tolerance change after a value is seen.
4. Basis is written next to every value: appliance-level, whole-house (heating included), or settlement profile.
   A whole-house or settlement curve is labelled as such and never called appliance demand.
5. Spain has a midday maximum in our real-diary profile (13:00, 4 % below 21:00). If the measured Spanish curve
   peaks at midday, that is recorded as "not consistent" with 21:00; the 13:00 secondary is NOT used to claim a match.
6. A country with no usable source is written NOT FOUND. No profile is borrowed from another country.
7. Paper wording by outcome: all available countries consistent -> one sentence in 3.5 with the sources;
   any not consistent -> the mismatch reported in 3.5 and Limitations; the timing claim is not widened in either case.

## Sources and who fetches them
| Country | Source (route from RL36 section 3) | Who | State |
|---|---|---|---|
| Spain | IDAE SPAHOUSEC final report PDF, chapter 4 | author downloads, puts it in `writing/resources/measured_profiles/` | not started |
| Italy | Besagni, Premoli Vilà, Borgarello (2020), Buildings 10(12) 217 (open access, browser only) | author downloads PDF to the same folder | not started |
| UK | Low Carbon London smart-meter data, London Datastore | we download and compute on Speed (sbatch, 1 CPU) | not started; needs a job script |

## Ledger
(none yet)

## Verified
(none yet)

## Next
Author puts the two PDFs in `writing/resources/measured_profiles/`. UK: write the Speed download-and-profile
job (standard-tariff households only; all-days and weekday mean half-hourly profiles; max hour), submit, record JobID here.

## WHAT I DID NOT VERIFY
- Whether our P3 profile includes lighting and plug loads only, or also electric water heating; to confirm from
  the appliance model config before the comparison is written into the paper.
- File names, size and licence of the Low Carbon London download (RL36 values rejected).

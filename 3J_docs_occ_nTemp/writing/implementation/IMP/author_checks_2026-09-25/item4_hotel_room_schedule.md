# Item 4 -- Hotel guest-room half-hourly shape s(t): source check (2026-09-25)

Read-only fact check. No manuscript, chapter or code file was edited. No simulation run.

## Question

Equation 1 (`02_Framework.md`) builds the half-hourly hotel guest-room multiplier
`m(t, month, PR) = s(t) x r(month, PR)`. `r` (the monthly occupancy rate, from ISQ/Alberta
tourism data) was already traced in `hotel_channel_fact_trace_2026-09-25.md` and is NOT the
subject here. This file traces only `s(t)`, the within-day shape: is it the DOE Commercial
Reference Building "Large Hotel" schedule (Deru et al. 2011, NREL/TP-5500-46861), the
ASHRAE 90.1 / DOE-PNNL Commercial Prototype Building Model, the NECB schedule, or own data?

## 1. Manuscript text (Equation 1 and its prose)

`3J_docs_occ_nTemp\writing\chapters_v2\02_Framework.md:56-58`:

> The monthly rate r is turned into a half-hourly multiplier,
> `m(t, month, PR) = s(t) r(month, PR)  (1)`
> where PR is the province and s(t) is a guest-room daily shape shared by both provinces.
> The shape holds 1.00 from 22:00 to 06:00 and falls to 0.200 on weekdays and 0.308 on
> weekends during the day (Figure 3).

`02_Framework.md:58` (Section 2.4, injection): "Guest-room occupancy is the NECB guest-room
schedule times the hotel multiplier of Eq. (1)." -- this is the sizing/routing sentence
(parallel to "office multiplies the NECB office occupant density"); it is not a second,
independent source for the *shape* of s(t) itself.

## 2. Code that builds s(t)

`3J_docs_occ_nTemp\Leg3_4-split\Step6_docs\3rdJ_06_hotel_sarima_4split.py:113-134`:

```
113  # --------------------------------------------------------------------------- dr_L3-05 s(t) table
114  # 48 slots, 30-min resolution, 00:00 .. 23:30. Unit-normalized (peak = 1.0), from the
115  # DOE/PNNL Large Hotel prototype guest-room schedule (dr_L3-05_hotel_diurnal_shape_REPORT.md,
116  # Table 5). Cross-checked value-by-value against that table AND against the val doc's
117  # Section 8 gate 8.10 wording (max=1.000, weekday trough=0.200, weekend trough=0.308).
118  ST_SLOTS = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]
119  ST_WEEKDAY = [
120      1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000,
121      0.769, 0.769, 0.431, 0.431, 0.431, 0.431, 0.200, 0.200, 0.200, 0.200, 0.200, 0.200,
122      0.200, 0.200, 0.200, 0.200, 0.200, 0.200, 0.308, 0.308, 0.538, 0.538, 0.538, 0.538,
123      0.538, 0.538, 0.769, 0.769, 0.769, 0.769, 0.892, 0.892, 1.000, 1.000, 1.000, 1.000,
124  ]
125  ST_WEEKEND = [
126      1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000,
127      0.769, 0.769, 0.523, 0.523, 0.523, 0.523, 0.308, 0.308, 0.308, 0.308, 0.308, 0.308,
128      0.308, 0.308, 0.308, 0.308, 0.308, 0.308, 0.308, 0.308, 0.308, 0.308, 0.523, 0.523,
129      0.538, 0.538, 1.000, 1.000, 1.000, 1.000, 0.769, 0.769, 0.769, 0.769, 0.769, 0.769,
130  ]
```

This is a hard-coded array in the Python script (also written out to
`0_Occupancy\processed\hotel_diurnal_shape_st.csv`). It is not read from an IDF, epJSON,
or externally-fetched file at run time; the code comment names its origin as a local deep
research report.

## 3. Where the array's numbers actually came from

`3J_docs_occ_nTemp\Leg3_4-split\deepResearch\dr_L3-05_hotel_diurnal_shape_REPORT.md`
(a Gemini deep-research deliverable, per project convention -- external, not web-verified
by the assistant that wrote the code):

- Line 15: **ASHRAE 90.1 Appendix G hotel schedule** row -- overnight 0.80, daytime 0.20-0.30,
  cites "COMNET Appendix C, Lodging Guest Room Schedule [1]". Different numbers from what
  the code uses.
- Line 16: **DOE / PNNL Large Hotel prototype (guest-room schedule)** row -- overnight 0.65,
  morning 0.50/0.28/0.13, daytime trough 0.13/0.20/0.35, evening 0.35/0.50/0.58/0.65 --
  cites "US DOE / PNNL Large Hotel Prototype Building Model [2]".
- Line 55 (Table 5 build note): "This unit-normalized diurnal shape s(t) ... is derived by
  taking the hourly fractional occupancy schedules of the DOE/PNNL Large Hotel prototype
  guest-room schedule ... and dividing by its peak value (0.65)."
- Line 151, reference [2]: "U.S. Department of Energy (DOE) / Pacific Northwest National
  Laboratory (PNNL) (2020). *Commercial Prototype Building Models: Large Hotel.*
  energycodes.gov/prototype-building-models."

Reference [2] is the DOE Commercial Prototype Building Model family (PNNL, built for
ASHRAE 90.1 code-cycle compliance, energycodes.gov), **not** Deru et al. (2011)
NREL/TP-5500-46861 "U.S. Department of Energy Commercial Reference Buildings" -- the
report's own Table 1 already treats "ASHRAE 90.1 Appendix G" and "DOE/PNNL Large Hotel
prototype" as two distinct rows with two distinct, non-matching numeric sets, and cites
the prototype-building-model page, not Deru et al.

## 4. Value-by-value check against the project's OWN base building IDF

This project's own Tall/SuperTall base prototypes (the same DOE/PNNL "Commercial Prototype
Building Models" the manuscript cites for the whole building, `02_Framework.md:66,79` and
`11_References.md:45`, "U.S. Department of Energy and Pacific Northwest National
Laboratory, Commercial Prototype Building Models... PNNL prototype schedules ... for the
hotel") already carry a **guest-room occupancy schedule object**, found locally at, e.g.,
`3J_docs_occ_nTemp\Leg3_4-split\Step9_docs\outputs_step9\finding9_verify\Default_NECB__Tall__MTL\injected.idf:3745-3801`
(same object also present in
`Leg2_2-split\Step8_docs\outputs_step8\office_idfs_v242\CAN_MTL\TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf`,
vintage tag "90.1-2019 ... NECB17" -- i.e. the ASHRAE 90.1 vintage prototype family, adapted
to NECB, not the Deru et al. 2011 reference-building set):

`HotelLarge GuestRoom_Occ_Sch Wkdy Day` (raw, peak 0.65):
00-06h=0.65, 06-07h=0.5, 07-09h=0.28, 09-15h=0.13, 15-16h=0.2, 16-19h=0.35, 19-21h=0.5,
21-22h=0.58, 22-24h=0.65.

`HotelLarge GuestRoom_Occ_Sch Default` (used for Sat/Sun/holiday, raw, peak 0.65):
00-06h=0.65, 06-07h=0.5, 07-09h=0.34, 09-17h=0.2, 17-18h=0.34, 18-19h=0.35, 19-21h=0.65,
21-24h=0.5.

Dividing every value by the 0.65 peak reproduces the code's `ST_WEEKDAY` and `ST_WEEKEND`
arrays **exactly**, slot for slot, 48/48 slots, both weekday and weekend:

| Local time band | IDF Wkdy raw | /0.65 normalised | Code ST_WEEKDAY | IDF Default(wknd) raw | /0.65 normalised | Code ST_WEEKEND |
|---|---|---|---|---|---|---|
| 00:00-06:00 | 0.65 | 1.000 | 1.000 | 0.65 | 1.000 | 1.000 |
| 06:00-07:00 | 0.50 | 0.769 | 0.769 | 0.50 | 0.769 | 0.769 |
| 07:00-09:00 | 0.28 | 0.431 | 0.431 | 0.34 | 0.523 | 0.523 |
| 09:00-15:00(wkdy)/17:00(wknd) | 0.13 | 0.200 | 0.200 | 0.20 | 0.308 | 0.308 |
| 15:00-16:00 (wkdy) | 0.20 | 0.308 | 0.308 | -- | -- | -- |
| 17:00-18:00 (wknd) | -- | -- | -- | 0.34 | 0.523 | 0.523 |
| 16:00-19:00 (wkdy) | 0.35 | 0.538 | 0.538 | -- | -- | -- |
| 18:00-19:00 (wknd) | -- | -- | -- | 0.35 | 0.538 | 0.538 |
| 19:00-21:00 | 0.50 | 0.769 | 0.769 | 0.65 | 1.000 | 1.000 |
| 21:00-22:00 (wkdy) | 0.58 | 0.892 | 0.892 | -- | -- | -- |
| 21:00-24:00 (wknd) | -- | -- | -- | 0.50 | 0.769 | 0.769 |
| 22:00-24:00 (wkdy) | 0.65 | 1.000 | 1.000 | -- | -- | -- |

Match is exact, not scaled/approximated beyond the stated /0.65 normalisation (which the
deep-research report and the code both state openly). No NECB-native schedule and no
Deru-et-al.-2011 schedule were found anywhere in the repo with these numbers; the only
local schedule object that reproduces them is the DOE/PNNL prototype's own
`HotelLarge GuestRoom_Occ_Sch`.

## What this means

- s(t) is the DOE/PNNL **Commercial Prototype Building Model** "Large Hotel" guest-room
  occupancy schedule (the ASHRAE-90.1-vintage prototype family used for the whole building
  in this study), normalised to a peak of 1.0 -- confirmed two ways: (a) the deep-research
  report's own citation trail (Table 1 row 2, Table 5 build note, reference [2]), and
  (b) an exact, independent value-by-value match against the guest-room schedule already
  embedded in this project's own base IDFs.
- It is **not** the ASHRAE 90.1 Appendix G / COMNET lodging schedule (same deep-research
  report, Table 1 row 1, different numbers: 0.80 overnight, 0.20/0.30 daytime).
- It is **not** Deru et al. (2011) NREL/TP-5500-46861 by direct citation anywhere in the
  repo; no file in the repo cites Deru et al. 2011 for this schedule, and the vintage tag
  on the matching local IDFs ("90.1-2019") post-dates the Deru et al. 2011 reference-building
  set. Whether Deru et al.'s own "Large Hotel" guest-room table happens to carry the same
  numbers as the newer PNNL prototype model was not checked (see WHAT I DID NOT VERIFY).
- The manuscript's own Eq. (1) prose (`02_Framework.md:57`, "1.00 from 22:00 to 06:00 ...
  0.200 on weekdays and 0.308 on weekends") matches the code's normalised values exactly.

## WHAT I DID NOT VERIFY

- Did not fetch or open the actual `ASHRAE901_HotelLarge_STD2019_*.idf` from
  energycodes.gov, nor the NREL/openstudio-standards `HotelLarge` schedule JSON on GitHub,
  to independently confirm reference [2]'s claimed values outside this repo; a web search
  for the exact numbers returned no matching page (search performed, no hit). The match
  used here is against this project's OWN copy of the DOE/PNNL prototype IDF, which is the
  same building family the manuscript already cites for the whole tower, not an
  independent, external primary source.
- Did not open or check Deru et al. (2011) NREL/TP-5500-46861 itself (not in the repo, and
  out of scope for this read-only, local-first check) to confirm whether its "Large Hotel"
  guest-room schedule differs from or coincides with the PNNL Commercial Prototype Building
  Model numbers used here; the two DOE building-model families are related but are treated
  as distinct products by DOE/PNNL and by the deep-research report itself.
- Did not verify the deep-research report's reference [2] is a real, resolvable citation
  (exact document title/edition/URL); per project convention, deep-research outputs are
  external and can contain fabricated citations, and this was not independently checked
  against energycodes.gov.
- Did not check whether s(t) is applied identically to the guest-room *lighting/plug-load*
  schedule referenced in `02_Framework.md` Eq. B.5, only the occupancy multiplier of Eq. (1).

## VERDICT: ASHRAE-PROTOTYPE

s(t) is the DOE/PNNL Commercial Prototype Building Model "Large Hotel" guest-room occupancy
schedule (U.S. Department of Energy / Pacific Northwest National Laboratory, *Commercial
Prototype Building Models: Large Hotel*, energycodes.gov -- the ASHRAE 90.1-vintage
prototype family also used for this study's whole-building models), normalised to a peak
of 1.0, not the Deru et al. (2011) NREL/TP-5500-46861 Commercial Reference Building
schedule and not the plain ASHRAE 90.1 Appendix G / COMNET lodging schedule (which carries
different numbers). It matches the schedule already embedded in this project's own base
IDFs, and matches the manuscript's Eq. (1) prose exactly.

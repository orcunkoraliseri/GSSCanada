# From One Channel to Four: A Jointly-Trained Time-Use Occupancy Model for Mixed-Use Building Energy Simulation (Canada, 2005-2030)

Orcun Koral Iseri\textsuperscript{a,\*}, Caroline Hachem-Vermette\textsuperscript{a}

\textsuperscript{a} Gina Cody School of Engineering and Computer Science, Concordia University, 1455 De Maisonneuve Blvd. W., Montréal, Québec, H3G 1M8, Canada

\* Corresponding author: orcunkoral.oseri@concordia.ca. ORCID (Iseri): https://orcid.org/0000-0001-7735-3363

---

## Abstract

Mixed-use towers stack apartments, offices, shops and hotel rooms above one central plant. Their energy models still run most uses on code schedules. This study builds a separate occupancy schedule for each of the four uses and asks what that changes. One Transformer model, trained on four cycles of the Canadian General Social Survey time-use diaries (2005 to 2022), generates residential, office and retail presence. A seasonal time-series model of provincial hotel statistics generates hotel presence. The four schedules drive EnergyPlus models of two prototype towers in Montreal and Calgary, for four survey years and nine scenarios to 2030. The survey-based schedules change who is in the tower and when. Hotel guests and residents are present at night, whereas the code schedules keep both on office hours. This change reaches energy only where lighting and equipment follow occupancy. Against the same towers on code schedules, office and retail intensity change by -7 to -10 % and -9 to -9 %, and their day-to-night contrast changes with them. Whole-building timing hardly moves. The daily load centroid shifts by less than 0.5 h, and the annual peak remains a winter-morning plant start-up. Reference intensity ranges built for single-use buildings judge the tower poorly. The office floor is missed even by the code-schedule tower, and hotel verdicts split by prototype. Detailed occupancy matters for tenant energy, but the building peak is set by plant and equipment schedules.

## Keywords

Multi-channel occupancy; Mixed-use tall building; Time-use survey; Occupancy schedule; Building energy simulation; Energy use intensity

## Highlights

- Four occupancy schedules drive one mixed-use tower, 2005 to 2030 scenarios.
- Survey-based schedules put hotel guests and residents in the tower at night.
- Office and retail energy follow survey occupancy; building peak timing does not.
- A winter-morning plant start-up sets the building peak under both schedule sets.
- Single-use intensity ranges cannot judge tenant uses inside a stacked tower.

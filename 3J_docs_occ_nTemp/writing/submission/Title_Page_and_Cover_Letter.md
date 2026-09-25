# Cover letter

[Date]

The Editors
*Building and Environment*

Dear Editors,

We are pleased to submit our manuscript, *From One Channel to Four: A Jointly-Trained Time-Use
Occupancy Model for Mixed-Use Building Energy Simulation (Canada, 2005-2030)*, for consideration as a
research article in *Building and Environment*.

Tall mixed-use buildings stack apartments, offices, shops and hotel rooms on one central plant, yet
their energy models usually run most uses on code schedules. This study gives each use its own
schedule. One jointly trained Transformer generates residential, office and retail presence from four
cycles of the Canadian General Social Survey time-use diaries (2005 to 2022). Monthly provincial
hotel-occupancy statistics set hotel presence, because hotel guests fall outside the survey frame. The
four schedules drive EnergyPlus models of two prototype towers in Montreal and Calgary, 56 simulations
in all, run once on code schedules and once on survey-based schedules, across four survey years and
nine scenarios to 2030.

**Major contributions.** The paper makes three contributions to the state of the art.

1. A multi-channel occupancy model for one building. One jointly trained model generates residential,
   office and retail presence from a national time-use survey, and a seasonal time-series model
   generates hotel presence from tourism statistics. All four are routed by space tag into the spaces
   of one mixed-use tower model.
2. A like-for-like test of what occupancy detail changes. The same towers, run on code schedules and
   on survey-based schedules, show that survey-based occupancy moves office and retail intensity by
   -7 to -10 % and about -9 %, while whole-building timing hardly moves: the load centroid shifts by
   less than 0.5 h, and the annual peak remains a winter-morning plant start-up under both schedule
   sets.
3. Evidence on how mixed-use towers should be judged. Reference intensity ranges built for single-use
   buildings cannot judge the uses of a stacked tower: the office range is missed even by the
   code-schedule tower, and the hotel verdict splits by tower prototype.

We state the limits of these results plainly. A second code control, with apartments and guest rooms
on a dwelling-unit schedule, shows that the night-time presence of residents and hotel guests is not
unique to the survey data, so the paper does not claim it as a finding. In both controls, office and
retail lighting and plug loads stay on the prototype schedules, so the office and retail differences
combine occupancy with that change of load schedule. Run-to-run spread was measured with repeated
household draws, and the reported office, retail and hotel changes are well above it.

We submit to *Building and Environment* because its scope names building performance and advanced
simulation tools, artificial intelligence applied to buildings, and human interaction with the built
environment. The paper links a learned model of occupant presence to building energy simulation and
tells designers where occupancy detail matters: for tenant energy, sub-metering and benchmarking, but
not for plant sizing and the building peak.

**Relationship to our earlier work.** This is the third study in one research line. Two companion
journal manuscripts, both in revision, and a companion conference study (Iseri and Hachem-Vermette,
2026) model residential occupancy only. The present paper adds office, retail and hotel channels inside
one building. The earlier work is cited and compared in the manuscript (Section 1 and Appendix A).

**Declarations.** We confirm that the submission declaration of the journal has been complied with.
The work has not been published previously, and it is not under consideration for publication
elsewhere. Its publication is approved by both authors and by the responsible authorities at Concordia
University, where the work was carried out. If accepted, it will not be published elsewhere in the
same form, in English or in any other language, without the written consent of the copyright holder.
All figures and tables are original to this work and reproduce no previously published material, so
no copyright permissions were required. The survey and tourism data are public releases and are cited
in the manuscript. We have no competing interests to declare. The use of generative AI tools,
including for the schematic figures, is declared at the end of the manuscript.

Thank you for considering our work.

Sincerely,

Orcun Koral Iseri, on behalf of both authors

---

# Title page

## Title

From One Channel to Four: A Jointly-Trained Time-Use Occupancy Model for Mixed-Use Building Energy
Simulation (Canada, 2005-2030)

## Authors

Orcun Koral Iseri^a,\*^, Caroline Hachem-Vermette^a^

^a^ Gina Cody School of Engineering and Computer Science, Concordia University, 1455 De Maisonneuve
Blvd. W., Montréal, Québec, H3G 1M8, Canada

\* Corresponding author. E-mail address: orcunkoral.oseri@concordia.ca

ORCID: Orcun Koral Iseri, https://orcid.org/0000-0001-7735-3363

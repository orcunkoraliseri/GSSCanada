# Vetting RT46: novelty_logged_search_P1_P4

VERDICT: FAIL ROUND, by the prompt's own rule ("Misdescribing a Known work fails the round"). The
route is worth keeping: a real query log, the ORNL file link with its input table, and a reading list
of 52 hits the tool kept but never opened (vetting employee, 2026-10-01).

Manager note. This round did what RT45 did not: it logged 28 queries (14 per part, 4 sources each),
and every query string in the report matches a line of `RT46_pages.log`. That part passes. But it
fails four ways that matter. (1) **Control K1 is misdescribed.** Row C1 says He et al. 2015 was
"Scored against monitored data and English Housing Survey totals (p. 2105)". Our full text shows no
monitored data and no comparison with survey totals anywhere: p. 2105 compares stochastic heating
hours with standard heating hours, both simulated. (2) **Both "open" verdicts rest on hits it never
opened.** Its queries kept 65 distinct results; it opened 13. The 52 others have no log line, no row
and no word in the report, yet Section G says "No candidate paper was abandoned". (3) **Its own rows
argue against its verdicts.** Its quoted ORNL Table 5 lists "People Activity" as an input channel of
the same form as outdoor temperature, which is a time series; and its C15 row (Satre-Meloy 2020) is a
regression that predicts peak demand from activity diary data. Both are possible "partly done" rows
for P1 and P4. (4) **Repeat defects from RT45:** Westermann and Evins is again called "full" from its
registry record, and "never" and "zero studies" claims are again drawn from abstracts and reference
lists. There are also strong signs that the tool read our previous vetting file (section 6, check 2), so
anything that matches `VETTING_RT45.md` gives no new evidence.

Checked 2026-10-01 by a vetting employee, OFFLINE only: no web access, no DOI resolution, no literature
search. Files read: `T46_novelty_logged_search_P1_P4.md`, `RT46_novelty_logged_search_P1_P4.md`,
`RT46_pages.log`, `VETTING_RT45.md`, `00_MASTER_BRIEF_5J.md`, `_RESPONSE_TEMPLATE.md`, and our own
full text of He et al. 2015 (`5J_docs_occ/Resources/nearest_work/He2015_BS2015_2655.pdf`). Anything
that needs an outside check is listed under "author to open" (section 8).

## 1. Controls

| Control | Result | Evidence |
|---|---|---|
| K1 He et al. 2015 | **FAIL (row C1).** The two-sentence description in Section G is right: Richardson Markov model, UK 2000 time-use survey, EnergyPlus, 125 houses near Loughborough (Leicestershire), no learned model. Row C1 adds two claims that are wrong. (a) "Scored against monitored data and English Housing Survey totals (p. 2105)": p. 2105 compares stochastic heating hours with standard heating hours (07:00 to 09:00 and 16:00 to 23:00), both simulated; the paper has no measured data at all. (b) "dwelling geometry from Cambridge Housing Model (p. 2102)": p. 2102 says width and depth "can only be found in the EHS data", and the 125 case-study houses come from an EPC and a sales brochure (p. 2105). RT45 vetting had noted that the scoring was left out; this round filled the gap with a page-cited claim the paper does not make. | our PDF, pp. 2102, 2105 to 2106 |
| K2 Park and Park 2023 | PASS on the description, abstract only (log line 4). It matches the abstract sentence we hold, so it tells us nothing new (check 2). Row C2 goes further than an abstract allows: an input list "(sec. 3)", monthly and annual outputs, scoring "(sec. 4)", "MLP". "Paired simulation runs" is the brief's wording, not the paper's. Year given as 2023 in G and 2024 in C2, E and H. | log line 4; VETTING_RT45 section 3 |
| K3 Pan et al. 2024 | PASS, full text (log line 6). But the quote and its page ("the weather variables were the features", **copy p. 3**) are word for word the manager's RT45 reading, including the "copy p." page style the manager made up. No independent signal. New details ("15 prototype buildings (copy p. 6)", "heat emissions") are not checked. | VETTING_RT45 section 3 |
| K4 Li, Bae and Im 2021 | PASS on finding it; description consistent with the OSTI abstract (107 inputs, 54 outputs, 4,000 runs, MLP and LSTM). The new part, Table 5, is checked in section 2. | log line 10 |
| Found by its own queries? | All four "found via Qn" claims are consistent with the log: K1 Q22 = log line 56 (Crossref), K2 Q8 = line 42 (Crossref), K3 Q4 = line 38 (OpenAlex), K4 Q5 and Q7 = lines 39 and 41 (Crossref). Engine and string match each time. **But three of the four queries are built from the controls' own title words** (Q22: "stochastic occupancy" "EnergyPlus" "neighbourhood"; Q8: "building energy retrofit" "artificial neural network"; Q4: "urban building energy" "LSTM"), and Q18 does the same for the Vosoughkhosravi review ("occupant-building interactions"). These show the tool can find a paper it already knows, not that topic queries reach it. The log keeps no result lists, so "found" cannot be confirmed from the log itself. | log lines 38 to 56 |
| Negative control (both parts open) | Obeyed in the letter only. Sentence 1 says the search "was probably too weak to eliminate every obscure conference paper or thesis" (a softened version), and sentence 2 then says "no published study feeds" an occupancy series into a surrogate, which is the "no such work" form T46 forbids. | Section A |
| Section A length (at most six sentences) | PASS (6). | Section A |
| No em or en dashes | PASS (0 found). | grep |
| No accuracy or speed-up numbers | PASS (none given). | |

## 2. Li, Bae and Im 2021 (K4): the ORNL file and its inputs

Section F gives `https://www.osti.gov/servlets/purl/1817464` (log line 10, "full", 20 pages) and quotes
Table 5 (p. 10), plus short quotes from pp. 7 and 9. RT45 timed out on this file, so this is the round's
most useful new deliverable, if the quote is real.

**Internal check: passes.** Weather 8 (OAT, humidity, pressure, wind speed, wind direction, infrared,
diffuse, direct) + internal loads 3 (lighting energy, equipment gains, People Activity) + sensor terms
96 = 107. The 96 are 5 sensors (AHU OAT, AHU SAT, zone VAV SAF, zone VAV SAT, zone air temperature)
times 3 error terms (bias, precision, total) times (1 + 1 + 10 + 10 + 10) = 3 x 32 = 96. That matches the
abstract's 107 and the p. 7 quote's "five selected sensors". A fabricator who knew "107" could build this,
so the author still has to open p. 10.

**What the report gets wrong about its own table.** C4 and B4 say "People Activity is 1 scalar feature
held fixed" and "occupancy not varied across 4,000 runs". The table cannot show that. "Quantity 1" is
also given for outdoor air temperature, which is an hourly series (and one of the two models is an
LSTM), so "1" means one input channel, not one number. The p. 7 quote ("The inputs were the sensor errors
injected") suggests that only sensor errors changed between runs, so the activity channel is probably
the same in every run. But **T46's P1 definition does not require the series to vary between runs**:
"inputs include an occupancy, presence, activity or schedule TIME SERIES". If People Activity is an
hourly channel, K4 is a "partly done" row for P1 by the letter (an activity series as a surrogate input,
never varied, so no occupancy effect can be learned). This decides P1 and needs the author's eyes:
pp. 7 to 11 of the ORNL file.

The p. 7 quote starts with the same sentence as the abstract we already held ("by integrating sensor
errors into an emulator based on EnergyPlus and Python EMS"). That may simply be the body repeating
the abstract; it is noted, not held against it.

## 3. The query log

| Item | Result |
|---|---|
| Lines in `RT46_pages.log` | 62: 34 pages or records opened (lines 1 to 34) + 28 queries (lines 35 to 62). |
| Queries per part | P1: 14 (lines 35 to 48); P4: 14 (lines 49 to 62). Matches the report's 14 + 14. |
| Sources per part | 4 each: OpenAlex 4, Crossref 4, arXiv 3, Google Scholar 3. Meets T46 (at least 12 queries, at least 4 sources). No Scopus or Web of Science (optional). |
| Query cited in the report but missing from the log | None. Q1 to Q28 all match a log line, same engine, same string. |
| Log lines without date or engine | None. Every line is dated 2026-10-01 and the engine is readable from the URL. |
| Hits and screened counts | Only in the report table; the log has none, so they cannot be checked against it. Screened never exceeds hits (internal check passes). Screened total: P1 102, P4 98. |
| Crossref queries | Hit counts of 3.3 to 15.4 million for four-term quoted strings show the quotes were ignored (a phrase like "American Time Use Survey" cannot match 15 million records). The kept results confirm it: an AMS mathematics chapter (10.1090/fic/011/07), BSI standards (10.3403/30337816), a PeerJ table, a CORDIS project. 8 of 28 queries were in effect untargeted. |
| arXiv | Q23 and Q24 return the same two papers; Q10, Q11, Q25 return 0. 5 of 6 arXiv queries add nothing. |
| T46 terms never queried | "emulator", "transformer", "activity", "dwelling", "household". CityTFT (a transformer) was reached only because RT45 named it. HETUS and MTUS appear only in Q21 (Crossref, junk hits); UK TUS never. No engine other than EnergyPlus (TRNSYS, IDA ICE, Modelica) was queried. |
| Kept results never opened | P1 kept 31 distinct IDs, opened 5 (Pan, Li, Park, Singaravel, Liang). P4 kept 34 distinct IDs, opened 8 (He, Vosoughkhosravi, Diao, Lee, Chiou, Zhang, Chen, Jung). **52 kept IDs have no log line and no mention.** The most on-target ones: Q14 ("surrogate model" "EnergyPlus" "occupant behavior" "LSTM"): authorea.15009435, 10.1109/JSYST.2025.3524182, 10.1016/j.enbuild.2026.116744. Q27 ("ATUS" "building energy simulation" "neural network" OR "surrogate"): 10.1007/s12273-021-0813-8, 10.1109/ACCESS.2024.3391820, 10.1061/9780784486115.114. Q26: 10.1061/JCCEE5.CPENG-6002, 10.1016/j.enbuild.2022.111973, 10.1016/j.enbuild.2026.117105. Q15: 10.3390/buildings11020041, 10.3390/en17174400, 10.1007/s12053-019-09791-1. Q12: 10.1016/j.buildenv.2022.109151, bs2025_1489, 10.1080/19401493.2026.2735926. So "these queries found nothing closer" is not shown by the log: the queries found things that were never read. |
| C rows with no query behind them | C10 Herbinger 2023 and C12 Seyedzadeh 2020 (not in any kept list, and too recent for the 2019 Westermann reference list); C15 Satre-Meloy and C17 Kleinebrahm (not in any kept list). Mauro et al. 2015 has a log line (24) and is counted as "seen described" but appears nowhere else. |
| Malformed ID | Q8 keeps `10.1016/enpol.2014.02.001`: an Elsevier DOI without "j.". Probably `10.1016/j.enpol.2014.02.001`. |
| "Full" in the log | Lines 33 and 34 (Jung, Chen) are arXiv `/abs/` pages, which show the abstract, yet C19 and C20 say "Read: full". Line 11 (Westermann) is a Crossref record with a reference list, yet C7 says "full". |

## 4. The nearest works: what was opened, and whether the claim goes beyond it

| Work | What the log shows it opened | Does the claim go beyond what it read? |
|---|---|---|
| Pan et al. 2024, JBPS, `10.1080/19401493.2024.2359985` | Full text, eScholarship copy (line 6) | Weather-only inputs: agrees with our own RT45 reading (but copied, see K3). "Occupancy schedules fixed per prototype" is fair `INFERENCE` from "occupancy is not an input". Year: 2024 in A, D, E, G; **2026** in C3 and H. The report's own Park entry puts volume 17 in 2024, so volume 19 in 2026 is the print issue and 2024 the online year: explainable, but never explained. Use 2024 with 19(5), 875-893. |
| He et al. 2015, `10.26868/25222708.2015.2655` | Full text (line 2) | **Yes, wrong** (section 1, K1): no monitored data, no comparison with survey totals; case-study geometry from EPC and brochure, not CHM. |
| Park and Park 2023, JBPS 17(3), `10.1080/19401493.2023.2282078` | Abstract (line 4) | Yes: section-cited inputs, outputs and scoring from an abstract. The core (low RMSE, causal relationships not reproduced) is in the abstract and stands. |
| Li, Bae and Im 2021, ORNL, `10.2172/1817464` | Full text, OSTI file (line 10) | Table 5 adds up. "Scalar held fixed" is its own inference and is weakened by its own table (section 2). |
| Vosoughkhosravi et al. 2023, `10.1016/j.enbuild.2023.113245` | Abstract, LSU repository (line 13) | Yes. "51 articles" may be in the abstract. "In all 51 studies ... Zero studies feed ATUS diary sequences directly into a learned energy surrogate" and A's "confirms ... never used" cannot come from an abstract (same defect as RT45's B7). The review covers **ATUS only**, so it says nothing about HETUS, UK TUS or MTUS, which are what P4 is about. The aside "(not 'over 100')" answers a figure that is not in T46 or the brief, so the tool saw earlier material. |
| Dai et al. 2025 CityTFT, `10.1016/j.apenergy.2025.125712` | Abstract, IDEAS/RePEc (line 15) | Probably. "Occupancy held to standard template schedules" is the same sentence RT45 gave with no source (RT45 vetting: UNVERIFIED). An abstract rarely says that. Keep as `INFERENCE`. "114 buildings" is new and unchecked. |
| Govindarajan et al. 2025, `10.1016/j.enbuild.2025.116366` | Crossref record (16), an Unpaywall status record (17), and the lab's home page root URL (18). **No full text.** | Yes. T46 asked for the full text ("are occupancy schedules an input, and as what?"). The answer given ("NOT an input ... full versus partial occupancy periods ... baseline comfort hours") has no logged source; it should have been NOT FOUND. C6 cites "(sec. 2)" while saying "Read: abstract". Arithmetic: "17.5 million simulation records" = 2,000 designs x 8,760 h = 17.52 million, consistent with the abstract-level counts. Unpaywall line 17 says the paper is open, so the full text was reachable and was not opened. |
| Westermann and Evins 2019, `10.1016/j.enbuild.2019.05.057` | Crossref record with reference list (line 11) | Yes. C7 "Read: full" with "(sec. 4)" content is wrong (same as RT45 defect 2). "Review of 136 works" (B5, C7) mixes up the reference count with the number of studies reviewed. "Across all 136 references ... zero studies use an occupancy time series" cannot be judged from titles. The useful part: it names the five entries it checked (refs 108, 94, 21, 92, 15), which T46 asked for. |

Two more rows the verdicts depend on:

* **Satre-Meloy et al. 2020, C15** (`10.1016/j.apenergy.2019.114246`, abstract, line 26; the log says
  2019, C15 and H say 2020). Its own row: activity diary sequences from the METER study, clustering
  plus linear regression, predicting peak electricity demand profiles. That is a trained model that
  takes diary data and predicts an energy outcome, which meets T46's P4 definition ("used as an INPUT
  to a trained model that predicts building energy use"; P4 does not say simulated). The dismissal
  "does not predict energy from sequences" adds a "sequences" condition T46 did not set. **P4 should
  read "partly done as far as searched (C15)" until the paper is opened.** (Note for the manager:
  T46 Section A says "simulated building energy" and the P4 definition does not; the prompt was not
  consistent, and the report used the narrower reading where it helped.)
* **Papadopoulos and Azar 2016, C8** (abstract, line 19): occupant agents set setpoints and lighting
  and equipment fractions, and a regression surrogate of EnergyPlus is called with those states
  through the simulated period. That is occupant-driven input over time. The dismissal ("instantaneous
  setpoint states, not sequential time series") is drawn from an abstract and again adds a
  "sequential" condition. A possible weak "partly" row for P1.

## 5. Kept (usable after the checks named)

| Item | Use |
|---|---|
| The 28-query log | A real, re-runnable route. The author can repeat the OpenAlex and Google Scholar queries by hand and open the kept hits (section 3). |
| ORNL file link and Table 5 quote | Use only after the author opens p. 10 and confirms the table, and reads pp. 7 to 11 on People Activity. |
| Pan 2024 (weather-only inputs) | Already confirmed by the manager's own RT45 reading; nothing new here. |
| Park and Park 2023 (difference scoring for retrofit) | Already confirmed from its abstract in RT45 vetting. |
| Govindarajan 2025 "23 independent variables, comprising climate data, spatial logic and model parameters" | Abstract wording, already held from RT45 vetting. The occupancy answer is not usable. |
| Westermann and Evins: five named references | A starting list for the author's own check of the review. |

## 6. The seven checks

1. **Claims about our study.** Mostly the brief read back (paired campaign, shuffled blind control,
   three European diary sets, stock-scale purpose, no meters). Beyond the brief: Section E says our
   work is "demonstrating that point-load accuracy metrics (RMSE, CV(RMSE)) are fundamentally
   insufficient to verify whether a surrogate learns true behavioral sensitivity". That is a result the
   tool was never given; it happens to fit our Step 4 finding, which makes it more dangerous, not less.
   Also invented: "instantaneous surrogate", D's effort in months, and "Which asset it lacks: None" on
   all six rows. Do not carry any of these.
2. **Agreeing with what we supplied.** Several items match `VETTING_RT45.md`, which lives in this folder
   and which T46 did not paste: the Pan quote with the manager's own "copy p. 3" page style; Section F's
   BESOS link (`gitlab.com/energyincities/besos`, "HTTP 200") and Richardson handle ("resolves to
   Loughborough repository"), worded as in the vetting and absent from the RT46 log; Park "online 2023,
   print 2024"; and the "(not 'over 100')" aside. Most likely the tool read our earlier files from the
   workspace. Everything that matches them is no evidence. The real signal is what we did not hold:
   Table 5 (adds up), and the C1 scoring claim (wrong).
3. **Metadata columns.** Year conflicts: Pan 2024 and 2026, Park 2023 and 2024, Satre-Meloy 2019 and
   2020. "Read: full" wrong for C7, C19 and C20. Section G question 1 says "count = 6" and lists 7
   works. Section-cited content ("sec. 2", "sec. 3", "sec. 4") in five rows marked abstract (C2, C6, C8
   and the Westermann content in C7). One malformed DOI in the log table.
4. **An identity it cannot fake.** Log versus report: 28 queries both sides, all strings match: PASS.
   Kept versus opened: 65 kept, 13 opened, 52 silent, against "No candidate paper was abandoned":
   FAIL. ORNL Table 5 sums to 107: PASS. Govindarajan 17.5 million = 2,000 x 8,760: PASS.
5. **Physics cross-check.** Not applicable (no energy values). The nearest thing: "Quantity 1" for
   outdoor temperature shows that "1" in Table 5 is a channel, not a scalar (section 2).
6. **Framing inherited.** Section E restates the brief's design as recommendations ("Maintain the paired
   simulation design", "Formalize the occupancy-blind control"). Section G question 3 explains the gap by
   "separate silos", a story, not a source. Both verdicts narrow P1 and P4 by adding "sequential" and
   "direct", which the brief forbids ("Do not narrow the claim until nobody has done exactly that").
7. **Rescuing direction.** Every Section E bullet keeps the design as it is. The only angle called taken
   (P5) is one the brief and RT45 vetting had already given up; P2 "partly" was already known. Nothing
   in the report costs us anything new, while two of its own rows (C4 Table 5, C15) point the other
   way and were explained away. Same warning sign as RT45.

## 7. What changes in our docs

* **P1 and P4 stay "not shown open".** The verdicts cannot be carried as "open as far as searched"
  until the 52 kept hits are at least title-screened and items 1 and 2 of section 8 are read.
* **The claim should rest on the combined design, not on P1 alone.** If K4 does feed an activity series
  that never varies, "a surrogate with an occupancy time series input" is partly done, but "trained on
  a campaign where only occupancy varies, scored on the occupancy effect, with a blind control" still
  holds as far as searched.
* He et al. 2015 is described from our own full text, never from RT46's C1.
* Years in the nearest-work table: Pan 2024 (JBPS 19(5), 875-893), Park and Park 2023 (JBPS 17(3),
  361-370); say "online" if the journal style asks.
* Any future prompt in this folder: tell the tool not to read other files in the workspace, or move the
  vetting files out of the folder before a run.

**Sentences safe for a novelty paragraph now (all "as far as searched"):**

1. "Surrogates of building energy simulation at urban and precinct scale have taken weather and building
   descriptors as inputs, with occupancy not among them (Pan et al. 2024; Govindarajan et al. 2025)."
   (Pan from the full text; Govindarajan from its abstract wording "climate data, spatial logic and model
   parameters". Add Dai et al. 2025 only after its abstract is opened.)
2. "Scoring a surrogate on differences between paired runs, rather than on the load alone, was proposed
   for retrofit by Park and Park (2023); we apply the idea to the occupancy effect and add a blind
   control."
3. "Time-use diaries have entered building simulation mainly through occupancy generators that drive
   the engine directly (e.g. He et al. 2015)." (He from our full text.)
4. Only after section 8 items 1 to 3: "A logged search of OpenAlex, Crossref, arXiv and Google Scholar
   (28 queries, October 2026) found no surrogate trained on a campaign in which only the occupancy
   sequence varies and scored on the resulting occupancy effect."

**Not safe:** "first", "no published study", "never", "zero studies", "open" for P1 or P4, anything
from the Vosoughkhosravi review beyond what its abstract says, anything about the content of the
Westermann and Evins review, and the Govindarajan occupancy answer.

## 8. Author to open (most load-bearing first)

1. **ORNL report**, `https://www.osti.gov/servlets/purl/1817464` (landing `https://www.osti.gov/biblio/1817464`):
   does Table 5 on p. 10 read as quoted, and on pp. 7 to 11 is "People Activity" (and lighting and
   equipment) an hourly series, and does it change between the 4,000 runs? Decides P1 "open" versus
   "partly done".
2. **Satre-Meloy et al.**, `10.1016/j.apenergy.2019.114246`: does the regression predict demand from
   diary activity data? Decides P4 "open" versus "partly done".
3. **The unopened hits of the two most targeted queries**, titles at least: Q14
   `10.1016/j.enbuild.2026.116744`, `10.1109/JSYST.2025.3524182`, `authorea.15009435`; Q27
   `10.1007/s12273-021-0813-8`, `10.1109/ACCESS.2024.3391820`, `10.1061/9780784486115.114`. (The
   other 46 are listed by query in the RT46 Section G table.)
4. **Govindarajan et al. 2025**, `10.1016/j.enbuild.2025.116366` (Unpaywall line says open): is
   occupancy an input to the surrogate, and as what?
5. **Vosoughkhosravi et al. 2023**, `10.1016/j.enbuild.2023.113245` (abstract at
   `https://repository.lsu.edu/construction_management_pubs/245`): does any reviewed study feed ATUS
   data into a learned energy model?
6. **Papadopoulos and Azar 2016**, `10.1016/j.enbuild.2016.06.079`: is the regression surrogate called
   step by step with occupant-driven inputs over the year (P1 by the letter)?

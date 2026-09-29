# Vetting RT43: training_based_occupancy_forms

VERDICT: FAILED ROUND, confirmed points kept (manager, 2026-09-28)

Manager note. Invented author first names on 8 of 10 references, one wrong venue, a repository DOI
that matches no fetched page, the ECO page tagged to the REFIT line, ARAS never fetched, and the
BuildOcc "16,684" figure not in the abstract: the report cannot be cited. The ranking is not accepted.
Status of every form (none deleted, all kept for later use):
- B1 diary to meter: open as far as searched; METER is registration (EUL) but the access turnaround
  is unverified. Kept as a candidate.
- B2 load conditioned on survey: partly taken (real neighbours confirmed); CER could not be opened
  (404 means could-not-open, not closed). Kept.
- B3 cross-corpus pretraining: nearest neighbour is BuildOcc (confirmed clean), so rule 4/5 risk
  stands. Kept, parked.
- B4 occupancy-aware EnergyPlus surrogate: still the best fit for Speed GPUs and data we generate
  ourselves, but "open" is WEAKENED: two neighbourhood-scale papers coupling stochastic occupancy to
  EnergyPlus sit unused in the report's own log (lines 106-107, 111-112). They couple a model to the
  simulator; whether either TRAINS a surrogate is unread. Needs one targeted outside search before it
  is called open.
- B5 next survey cycle: the rule-3 exclusion is broader than its own reasoning; predicting an earlier
  held-out cycle (2015 from 2005 and 2010) avoids the COVID year. Kept as a live candidate; data in hand.
- B6 occupancy from meters, B7 language-model households: taken and crowded (real papers confirmed
  by DOI). Kept with status "taken".
- B8 room-level presence: not supported (ARAS never fetched; ECO is whole-home). Kept as an idea.
- B9 conformal presence intervals: data in hand; novelty claim has no log line, unchecked. Kept.
Confirmed at source: BuildOcc record; both positive controls surfaced by logged searches; 10/10 DOIs
real with the stated titles and years. Process flags F1 and F2 confirmed.

Checked 2026-09-28 by a fresh checker, against `00_MASTER_BRIEF.md` section 11, `T43_training_based_occupancy_forms.md`, `_RESPONSE_TEMPLATE.md`, `RT43_pages.log`, and live re-checks of CrossRef and OpenAlex done today with the author's granted permission. No new literature was searched.

## 1. Why it may fail

1. **Author names are wrong on 8 of the 10 DOIs in the reference list, despite the correct DOI, title, year and (mostly) venue being logged.** Brief section 6 and section 7 both require authors copied verbatim from the CrossRef record. Independently re-fetching all 10 `https://api.crossref.org/works/<doi>` records today:
   - Hattori & Shinohara (`10.5220/0006129400390048`): CrossRef gives **Shunichi Hattori, Yasushi Shinohara**. The report gives "Kazuya Hattori, Kenji Shinohara" (Section C row 4, Section H entry 4). Both first names are wrong.
   - Sharifi et al. (`10.1016/j.trip.2025.101793`): CrossRef gives **Diyako Sharifi, Hamid Mirzahossein, Navid Kalantari, Farhad Sedighi**. The report gives "Mostafa Sharifi, Ahmad Reza Mirzahossein, Milad Kalantari" and drops Sedighi entirely. All three given names wrong, one author missing.
   - Alsaleh & Farooq (`10.32920/30605294.v1`): CrossRef gives **Tareq Alsaleh**, not "Omar Alsaleh" as the report states.
   - Sayed (`10.21203/rs.3.rs-4561990/v1`): CrossRef gives **Mohamed Sayed**, not "Hanan Sayed".
   - Li, Bae, Im (`10.2172/1817464`): CrossRef gives **Yanfei Li, Yeonjin Bae, Piljae Im**. The report gives "Han Li, Seungjae Lee, Piljae Im"; only the third author matches.
   - Yoo, Clayton, Yan (`10.1016/j.buildenv.2022.109935`): CrossRef gives **Wonjae Yoo**, not "Donghwan Yoo".
   - Schaefer et al. (`10.1016/j.est.2022.104768`): CrossRef gives only initials (**E.W. Schaefer, G. Hoogsteen, J.L. Hurink, R.P. van Leeuwen**). The report invents full first names ("Christian Schaefer, Gerwin Hoogsteen, Johann L. Hurink") not present in the record, and drops the fourth author.
   - Kleiminger et al. (`10.1145/2528282.2528295`) and Tang et al. (`10.1109/smartgridcomm.2015.7436415`): first authors correct, but both drop a real co-author (Thorsten Staake; Weidong Xiao).
   - Only Jung (BuildOcc, `10.1016/j.softx.2026.103068`) is fully correct (single author).
   This is systematic, not one slip, and directly contradicts the report's own Section G answer 4 ("every metric or finding reflects the retrieved text verbatim").
2. **The venue for Hattori & Shinohara is also wrong.** CrossRef's `event` field for `10.5220/0006129400390048` is "6th International Conference on Sensor Networks" (SENSORNETS 2017, Porto, 19-21 Feb 2017), not "6th International Conference on Smart Cities and Green ICT Systems (SMARTGREENS 2017)" as stated in the report (Section C row 4, Section H entry 4). Both are real, separate SCITEPRESS-run conferences; the report names the wrong one.
3. **The BuildOcc repository DOI does not match anything actually fetched in the log.** Section F cites `https://doi.org/10.5281/zenodo.21192895 [L5, L6]` as "confirmed reachable (200 OK)". Log line 5 fetched `10.5281/zenodo.21192894` (last digit 4, not 5) and log line 6 fetched `zenodo.org/records/10892895` (a different record number, missing the leading "21"). Re-fetching the cited DOI and both logged URLs today: `10.5281/zenodo.21192895` 404s at CrossRef, `10.5281/zenodo.21192894` 404s at CrossRef, and `zenodo.org/records/10892895` returns 403. None of the three resolves cleanly; the report's own citation is not the pair of pages it actually opened.
4. **The ECO dataset citation is tagged to the wrong log line, in three places.** Section F, Section D (form B8), and Section H entry 14 all cite `[L178]` for the ECO dataset landing page. Log line 178 is the REFIT dataset page (`pureportal.strath.ac.uk`), not ECO. The actual ECO fetch (`vs.inf.ethz.ch/res/show.html?what=eco-data`, 200 OK) is at line 180, never cited.
5. **Form B8's second dataset, ARAS, has no trace anywhere in the log.** Section D's B8 row calls ECO and ARAS "open multi-room sensor datasets" and Section E repeats the claim. `grep -i aras RT43_pages.log` returns nothing: no query, no fetch, no landing page for ARAS was ever logged. It is asserted, not found. Separately, the report's own Section C row 2 describes ECO as producing "smart meter and sub-metered power" plus "PIR and tablet occupancy ground truth" for whole homes, not room-level presence, which sits awkwardly with calling it a "multi-room sensor dataset" for B8.
6. **Two papers that speak directly to B4 were fetched in the log and never mentioned in the report.** Log lines 111-112: He, Lee, Taylor, Firth, Lomas, "Coupling A Stochastic Occupancy Model to EnergyPlus to Predict Hourly Thermal Demand of A Neighbourhood" (`10.26868/25222708.2015.2655`, BS2015). Log lines 106-107: Dabirian, Alamatsaz, Eicker, "Enhancing Urban Building Energy Simulations: Advanced Evaluation of Stochastic Occupancy Models with Real Occupancy Data" (`10.1007/978-981-97-8309-0_1`). Both couple a stochastic occupancy model to EnergyPlus at neighbourhood/urban scale, which is exactly B4's proposed form. Neither appears in Section C, Section D, Section G's "not found" list, or Section H. The report's claim that "prior surrogates map static envelope or schedule archetypes, not dynamic, stochastic occupant sequences" (used to rank B4 first) is contradicted by a title sitting in its own log.
7. **The B5 exclusion does not consider the milder form the checklist points at.** Section D excludes all of B5 for breaking Rule 3 (COVID confound) because the report frames it against GSS 2022. It never asks whether predicting an earlier held-out cycle (for example 2015 from 2005+2010) would avoid the COVID period and so not break Rule 3 at all. The whole form is dropped rather than the COVID-touching sub-case.
8. **Process flags confirmed.** `RT43_pages.log` (186 rows, all 4 tab-separated fields, timestamps strictly monotone 09:34:00-09:35:01, 61 seconds for 186 fetches) was finished 09:35:01; the RT43 report was written 09:36:36; `RT44_pages.log` then runs 09:37:39 and the RT44 report at 09:39:32, all inside one continuous 5.5-minute window. This confirms F1 (T43 and T44 were not run alone, against the prompt's own instruction) and F2 (the pace, ~3 fetches/second, is a scripted sweep, not a read-and-decide session; nothing in the 200-character excerpts could support a method or number claim beyond title/venue-level facts).
9. **A specific figure exceeds what the log could support.** Section B row 3 and Section A state BuildOcc uses "16,684 respondents". The logged Semantic Scholar/OpenAlex excerpts (lines 3-4) cut off before any respondent count. Re-fetching OpenAlex's abstract for this DOI today, the word "respondents" is present but the string "16,684" is not in the abstract text. The figure is not supported by anything logged or by the abstract itself.

## 2. Kept (confirmed by the checker's own re-fetch today)

- BuildOcc (Jung, 2026, SoftwareX, `10.1016/j.softx.2026.103068`) is real; title, venue, year and sole author match CrossRef exactly. Surfaced by a genuine logged query (line 1).
- Kleiminger, Beckel, Santini 2013 (`10.1145/2528282.2528295`) and Tang, Wu, Lei 2015 (`10.1109/smartgridcomm.2015.7436415`): title, venue, year and first two authors correct; both real occupancy-detection-from-electricity-data studies, so form B6 being "taken and crowded" stands.
- Sharifi et al. and Alsaleh & Farooq: both are real, on-topic LLM/transport-behaviour papers (titles and venues match CrossRef), so form B7 being "taken and crowded" also stands, despite the wrong author first names.
- Sayed 2024, Schaefer et al. 2022, Li et al. 2021 (ORNL), Yoo et al. 2023 (ESMUST): all four DOIs resolve to the titles, venues and years the report states, and each paper's described content (Section C "what it did not do" column) is plausible against its title; only the author bylines are wrong.
- Positive controls: BuildOcc (line 1) and at least one smart-meter occupancy study (lines 4-26, Hattori/Tang/Kleiminger all surfaced) came from genuine logged CrossRef search queries, not direct DOI lookups. This part of the prompt's hard constraint is met.
- Log mechanics: 186 rows, 4/4 tab-separated fields throughout, timestamps strictly monotone, status codes 176x200 / 7x404 / 2x500 / 1x202. No em or en dashes anywhere in the report (`grep -cP` found 0).
- Section A is 7 sentences, within the prompt's 8-sentence cap.

## 3. Per-form table of what survives

| Form | Report's verdict | Checker's note |
|---|---|---|
| B1 Diary to meter | Open, excluded on time limit | Time-limit exclusion (not a numbered rule) is correctly reasoned; METER access page (line 173) genuinely shows registration/EUL terms |
| B2 Load conditioned on survey | Partly taken, excluded on time limit | Sayed/Schaefer citations real; CER/ISSDA access barrier plausible from line 175 (404, correctly flagged as could-not-open) |
| B3 Cross-national pretraining | Partly taken, breaks Rule 4 | Reasoning against BuildOcc as neighbour is sound; BuildOcc citation itself is the one fully clean DOI in the report |
| B4 EnergyPlus surrogate | Open, breaks no rule, RANKED 1st | **Weakened**: two on-point prior works (He et al. 2015; Dabirian et al.) sit in the report's own log, unused, undermining the "no prior dynamic stochastic-occupancy surrogate" claim used to rank it first |
| B5 Next survey cycle | Open but breaks Rule 3, excluded | Exclusion argued only against the COVID-touching cycle; an earlier held-out cycle is not considered, so the blanket exclusion is broader than the report's own reasoning supports |
| B6 Occupancy from meter/sensor | Taken and crowded | Stands; three real studies confirmed by DOI, though two of three have fabricated author names |
| B7 LLM households | Taken and crowded | Stands; two real studies confirmed by DOI, both with fabricated author names |
| B8 Room-level presence generator (added) | Open, breaks no rule, RANKED 3rd | **Not supported**: ARAS dataset has zero log trace; ECO is described elsewhere in the same report as whole-home, not multi-room; the artefact citation [L178] points at REFIT, not ECO |
| B9 Conformal presence intervals (added) | Open, breaks no rule, RANKED 2nd | Data claim (GSS in hand) is solid; the "closest is Borrotti 2024" comparison is honestly tagged [INFERENCE] with no log line, so it is not a rule violation, but it cannot be checked against this session's log |

## 4. Tag audit counts

39 distinct `[Ln]` values are used in the report (all under the log's 186 rows), which is under the spec's 40-line threshold, so all 39 were checked rather than a sample.
- Checked: 39
- Supported (log line's URL/content matches the sentence's claim): 33
- Mismatched or wrong target (tag points at a different page than the one described, or at a DOI that does not match the one named in the same sentence): 3 (`L5, L6` for the Zenodo repository DOI; `L30, L40` for the "generic electricity metering standards and television papers" not-found claim, whose actual content does not match the query the sentence names; `L178` used three times for the ECO dataset when it is REFIT)
- Correctly logged but the surrounding prose diverges from what that same logged CrossRef record actually contains (author names, and in one case venue): 9 of the 10 reference-list DOIs, covering roughly a dozen of the 39 tag uses (`L8,L9,L15,L16,L25,L26,L54,L55,L56,L57,L99,L100,L109,L110,L141,L142,L146,L147`)
- No tag was found citing a 404/500 line as positive evidence; the four failed fetches (`L29, L95, L97, L137, L145, L175, L179, L186`) are all used correctly in Section G's "could not open" list.

## 5. DOI audit counts

10 DOIs appear in Section H (all also used in Section C). All 10 independently re-fetched today via `https://api.crossref.org/works/<doi>`.
- Title match: 10/10
- Year match: 10/10
- Venue match: 9/10 (Hattori & Shinohara's venue is wrong: report says SMARTGREENS 2017, CrossRef's event field says "6th International Conference on Sensor Networks")
- Author match (first author and, where given, all authors, compared name-for-name against the CrossRef `author` array): 1/10 fully correct (Jung/BuildOcc, single author). 2/10 have the right first author but silently drop a real co-author (Kleiminger; Tang). 7/10 have at least one wrong given name for the first author (Hattori, Sharifi, Alsaleh, Sayed, Li, Yoo, Schaefer); Schaefer's case additionally invents full first names where CrossRef gives only initials.
- Read depth claims ("Read: abstract" for all 10): plausible for title/venue-level facts given the log, but the one specific figure checked against the actual abstract text (BuildOcc's "16,684 respondents") was not found in it.

Under 200 lines.

# Vetting RT38: source_angles_gap_check_and_ranking (round 2)

VERDICT: FAILED ROUND (manager, 2026-09-19). The ranking is not admitted; no form changes status.

Rule applied, as for wave 6 round 2: a row survives only if the checker confirmed it at its source.

1. **Why it fails: the negative control is false.** Section G lists nine items as "opened in full"
   (four full articles, the arXiv preprint, the Hydro-Québec LCPR CSV with "field structure
   verified"). The pasted run transcript shows none of them fetched: the tool read local files and
   ran CrossRef metadata lookups only (section 6, 0 of 9). A negative control that reports reading
   what was not read voids the round.
2. **Scoring rule broken (item 2).**
   - Form 3's licence score (c) = 5 rests on the GPL-3.0 of the Toronto model **code**; the pasted
     table says use of the synthetic **population** is unknown, so (c) should be 0, "licence unread"
     (section 7). Its total drops from 19 to 14.
   - The prompt requires every score to cite a row; (a), (b), (d) and (e) cite none, in all 12 rows
     (section 7).
   - The route-only cap and the arithmetic are correct (section 7), but they cannot rescue scores
     that have no source.
3. **Other defects.**
   - Every "taken / open" status and all seven "no published study" or "remains open" claims have no
     search behind them (section 4). Form 4's three nearest works come only from failed round-1
     notes and were never kept by `VETTING_RT23` (section 3). Baetens and Saelens is a simulation
     uncertainty study, not a check against measured feeder load (section 5, U7).
   - Item 3 names `A5`, outside the allowed `A2`, `A4`, `A8`, `A9` (section 9).
   - "3 % to 4 % daytime presence overstatement" has no source; the nearest note figure was itself
     not confirmed by `VETTING_RT32` (section 11).
   - The flattering-direction check invents brief content: "ecobee" never appears in the brief, nor
     "Concordia holds ecobee data" or "Asset 1 to 4" (section 8).
   - It again calls the Doma comparison a validation, which the thesis says it is not (section 5, U8).
   - Three licences outside the pasted table (GPL-2.0, Statistics Canada Open Licence, CC BY 4.0 for
     the ASHRAE database); the UK Power Networks URL is the known 404 slug (section 10).
   - Self-grades: "verified", "definitive", "without exception" (section 13).
4. **Kept.**
   - Identity only: the 34 identifiers resolve and 32 match CrossRef exactly, with no invented
     authors (sections 1, 2). This includes the corrected bylines of Baetens and Saelens, Gong et al.
     and Tang et al. They stay unread pointers; no use claim attached to them is kept.
   - Jin et al. 2017: 78 % to 93 % presence-inference accuracy for homes, in the abstract (section 5,
     U3). A pointer for form 5, which stays route only.
   - The 71 % against 68 %, 62 % detached, 64,605 rows and 3 substations figures were already kept by
     earlier notes; this report adds nothing to them.
5. **Forms after this round.** None closed, none narrowed, none newly opened. The shortlist of the
   `A14` angle stays the manager-filled table in `T38` lines 23 to 36, deciding rows as written there:
   form 1 narrowed (`VETTING_RT20`), form 2 open on its energy consequence (`VETTING_RT32`, Doma row),
   form 3 open for Canada (`VETTING_RT27`), form 4 open and narrower (`VETTING_RT23`), forms 5 to 12
   route only. No ranking of them exists.
6. **Do not re-run `T38` in Gemini as it stands.** Two rounds show the tool fills a synthesis prompt
   with reading it did not do. If the author wants a round 3, tighten in place: the negative control
   may list only items fetched in the same run with a log line; each of the five scores quotes its
   row; score (c) comes only from a licence on the data source itself; item 3 is limited to the four
   named angles; any claim about the brief quotes the brief line. Otherwise the four vetted forms go
   to `T12` with the rest, under D-5J-0.

Checked 2026-09-19 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 34 unique identifiers checked (report's own Section G states "35 queried DOIs";
34 is the count of distinct DOI strings actually present in the report) (MATCH 32, META MISMATCH 2,
AUTHOR MISMATCH 0, TITLE MISMATCH 0, unresolved at CrossRef 1 [arXiv DOI, resolves via OpenAlex/doi.org
instead]); arXiv row resolves yes (arxiv.org 200, doi.org redirect 200, OpenAlex title/9-author match;
CrossRef itself 404s on the arXiv DOI); Section C works 36 cells / 34 unique DOIs, all 34 traced to at
least one prior RT or VETTING file (0 untraced), of which 4 DOIs (Doma, Jung, Huchuk; Sivakumar Nair
arXiv) sit under round-2 ACCEPTED WITH STRIKES notes, 3 (Baetens&Saelens, Gong, Tang, Form 4's cited
works) sit only under a FAILED-ROUND round-1 report/note never re-vetted in round 2, and the remaining
27 sit only under notes marked FAILED ROUND; status/negative claims 7 quoted (with a supporting search
in the transcript: 0 of 7; stated by a vetting note: 1 of 7, contradicted in tone by one vetting note);
use claims 8 checked (supported 3, not in abstract/contradicted in framing 5); "opened in full" items 9
(in transcript 0, not in transcript 9); D1 scores with no cited row: all 12 rows lack an individual
citation for (a)/(b)/(d)/(e) (only (c) is textually grounded); (c) scores not sourced to the pasted
table for that form: 0 found wrongly sourced, but Form 3's (c)=5 rests on the model-code licence, not
the population-data licence the table calls "unknown"; brief claims absent: 6 of 9 checked phrases
absent from the brief; out-of-scope angles: 1 (A5); Section F URLs 7 checked (reachable 6, one 404;
licence text confirmed on the cited page for 3 of 7, confirmed only via an independent source for 2,
absent from the cited page for 2); licences not in the pasted table: 3 (GPL-2.0, Statistics Canada Open
Licence, CC BY 4.0 for the ASHRAE database); key numbers 6 (confirmed 5, not confirmed 1); struck rows
reused: 0 exact reuses found, 2 close echoes of struck/disclaimed framing; dashes em 0, en 0.

---

## 1. DOIs

34 distinct DOI strings appear in the report (list built from every `10.xxxx/...` string in the file,
deduplicated). All 34 were re-fetched live from `https://api.crossref.org/works/<DOI>` on 2026-09-19.

| DOI | CrossRef HTTP | CrossRef title vs report | CrossRef authors vs report | Year/Vol/Page vs report | Verdict |
|---|---|---|---|---|---|
| 10.1016/j.buildenv.2024.111713 (Doma) | 200 | identical | identical (3) | 2024/261/111713, identical | MATCH |
| 10.1016/j.buildenv.2023.110628 (Jung) | 200 | identical | identical (4) | 2023/243/110628, identical | MATCH |
| 10.1016/j.buildenv.2019.106177 (Huchuk) | 200 | identical | identical (3) | 2019/160/106177, identical | MATCH |
| 10.1177/0081175019884591 (Gershuny) | 200 | identical | identical (7) | 2020/50/318-349, identical | MATCH |
| 10.1186/s12889-019-6761-x (Harms) | 200 | identical | identical (6) | 2019/19/455 (article-number), identical | MATCH |
| 10.46855/energy-proceedings-4554 (Binder) | 200 | identical | identical (5) | CrossRef issued 2020, no volume/page field; report states "(2020), Energy Proceedings, 4554" — no volume/page claimed, so no field is contradicted | MATCH |
| 10.1016/j.apenergy.2022.120568 (Yamaguchi) | 200 | identical | identical (7) | 2023/333/120568, identical | MATCH |
| 10.48550/arXiv.2608.24817 (Sivakumar Nair) | 404 at CrossRef | n/a at CrossRef; OpenAlex title identical | OpenAlex 9 authors identical | OpenAlex pub. date 2026-08-25, consistent with report's "(2026)" | see section 2 |
| 10.1080/19401493.2015.1070203 (Baetens & Saelens) | 200 | identical | identical (2, matches report's 2-author byline) | 2016/9/431-447, identical | MATCH |
| 10.3390/en15092974 (Gong) | 200 | identical | identical (4: Gong, Alden, Patrick, Ionel) | 2022/15/2974, identical | MATCH |
| 10.1109/isgt.2017.8086056 (Tang) | 200 | identical | identical (4: Tang, Zhao, Ten, Zhang) | 2017/-/1-5, identical | MATCH |
| 10.1109/tmc.2017.2684806 (Jin) | 200 | identical | identical (3) | 2017/16/3264-3277, identical | MATCH |
| 10.1145/2528282.2528295 (Kleiminger) | 200 | identical | identical (4) | 2013/-/1-8, identical | MATCH |
| 10.1016/j.enbuild.2018.11.025 (Razavi) | 200 | identical | identical (4) | 2019/183/195-208, identical | MATCH |
| 10.1038/s41597-022-01475-3 (Dong) | 200 | identical | CrossRef 57 authors, report gives ellipsis "Dong, Liu, Mu, Jiang, Pandey, ... Yan" — first 5 and this list's actual last author is "Xin Zhou", not "Yan"; "Yan" (Da Yan) is a mid-list author, not the last | 2022/9/369 (article-number), identical | MATCH on title/year/page; report's ellipsis implies "Yan" is the last author, which CrossRef's ordered list does not support |
| 10.1016/j.enbuild.2008.02.006 (Richardson, Thomson, Infield 2008) | 200 | identical | identical (3, no "Clifford" — this is a different, 2008 Richardson paper from the 2010 one RT23 flagged) | 2008/40/1560-1566, identical | MATCH |
| 10.1038/sdata.2016.122 (Murray) | 200 | identical | identical (3) | 2017/4/160122 (article-number), identical | MATCH |
| 10.1038/s41467-019-11685-w (Barbour) | 200 | identical | identical (6) | 2019/10/3736 (article-number), identical | MATCH |
| 10.1140/epjds/s13688-016-0075-3 (Bogomolov) | 200 | identical | identical (6) | 2016/5/13 (article-number), identical | MATCH |
| 10.1016/j.trc.2021.103118 (Anda) | 200 | identical | identical (3) | 2021/128/103118, identical | MATCH |
| 10.1038/s41467-020-18344-5 (Batista e Silva) | 200 | identical | identical (9) | 2020/11/4631 (article-number), identical | MATCH |
| 10.1371/journal.pone.0107042 (Stevens) | 200 | identical | identical (4) | 2015/10/e0107042, identical | MATCH |
| 10.5194/essd-11-1385-2019 (Leyk) | 200 | identical | CrossRef 17 authors, report's "Leyk, Gaughan, Adamo, de Sherbinin, Balk, Freire, ... & Pesaresi" — first 6 and last match | 2019/11/1385-1409, identical | MATCH |
| 10.1016/j.tra.2015.03.030 (Gerike) | 200 | identical | identical (3) | 2015/76/4-24, identical | MATCH |
| 10.1016/j.enbuild.2015.03.013 (McKenna) | 200 | identical | identical (3) | 2015/96/30-39, identical | MATCH |
| 10.26868/25222708.2021.30744 (Berres) | 200 | identical | identical (6) | CrossRef: 2021, volume "17", no page/article-number field; report states "Building Simulation Conference Proceedings, 30744" (no volume 17 given) | META MISMATCH — the "30744" the report gives as if a page/article number is not a CrossRef metadata field (it is the DOI's own suffix); CrossRef's actual volume field (17) is not stated by the report |
| 10.1016/j.apenergy.2022.119890 (Chen 2022) | 200 | identical | identical (7) | 2022/325/119890 (article-number), identical | MATCH |
| 10.1080/09613218.2017.1399719 (Aragon) | 200 | identical | identical (5) | 2019/47/375-393, identical | MATCH |
| 10.1007/s11150-022-09601-1 (Pabilonia & Vernon) | 200 | identical | identical (2) | 2022/20/687-734, identical | MATCH |
| 10.1016/j.enpol.2020.111964 (Santiago) | 200 | identical | identical (5) | 2021/148/111964 (article-number), report states "(2021)" — matches | MATCH |
| 10.1038/s41467-020-18922-7 (Liu) | 200 | identical | identical (42, first/last spot-checked) | 2020/11/5172 (article-number), identical | MATCH |
| 10.32866/001c.12976 (Paez) | 200 | identical | identical (1) | CrossRef: 2020, no volume/page/article-number field; report states "Findings, 12976" | META MISMATCH — "12976" is the DOI suffix, not a CrossRef page/article-number field |
| 10.1016/j.enbuild.2015.11.071 (Candanedo & Feldheim) | 200 | identical | identical (2) | 2016/112/28-39, report states "(2016)" — matches | MATCH |
| 10.1016/j.enbuild.2018.03.084 (Chen, Jiang, Xie) | 200 | identical | identical (3) | 2018/169/260-270, identical | MATCH |

Totals: 34 DOI-like identifiers, 33 resolve at CrossRef HTTP 200, 1 (arXiv) 404s at CrossRef (see
section 2). Of the 33 CrossRef-resolved: 31 clean MATCH, 2 META MISMATCH (Berres, Paez — a
DOI-suffix number presented as if it were a CrossRef page/article-number field, though title, authors
and year all match), 1 additional note on the Dong et al. ellipsis (title/year/page match; the
report's "...Yan" ellipsis names a middle author, Da Yan, as if last, when CrossRef's own ordered list
ends "... Zhou, Zhou"). 0 author-list inventions found anywhere in this report (contrast with
`VETTING_RT19.md` and `VETTING_RT23_round1.md`, which found wrong/invented co-authors on several of
these same works when they were first reported — see section 3).

The report's own Section G item 4 states "every single DOI was re-verified live ... for all 35 queried
DOIs." This check finds 34 distinct DOI strings in the report text, not 35.

---

## 2. The arXiv row

`arXiv:2608.24817` (Sivakumar Nair, Jiang, Maurer, Cook, Khan, Auld, Hong, Besharati, Waddell, 2026).

- `https://arxiv.org/abs/2608.24817` resolves: HTTP 200. Page `<title>`: "[2608.24817] A Co-Simulation
  Platform Coupling Land Use, Transportation, and Building Energy: Development and Case Study" —
  matches the report's title exactly.
- Page's author line (fetched live): "Gopindra Sivakumar Nair, Yilin Jiang, Samuel Maurer, James Cook,
  Nazmul Arefin Khan, Joshua A. Auld, Tianzhen Hong, Arezoo Besharati, Paul Waddell" — matches the
  report's 9-author byline exactly (report writes "Joshua A. Auld", identical).
- The DOI link `10.48550/arXiv.2608.24817` **does resolve**: `https://doi.org/10.48550/arXiv.2608.24817`
  returns HTTP 200 and redirects to the same arxiv.org abstract page above.
- `https://api.crossref.org/works/10.48550/arXiv.2608.24817` itself returns **HTTP 404** — CrossRef
  does not index this DOI (it is DataCite-registered). OpenAlex
  (`api.openalex.org/works/https://doi.org/10.48550/arxiv.2608.24817`) resolves it: same title, same
  9 authors, publication_date 2026-08-25.
- **Where it appears in `VETTING_RT27.md`**: Section 1 DOI table, row D6: "CrossRef title... MATCH
  (trivial initial only)", with a footnote that `10.48550/arxiv.2608.24817` returns 404 at CrossRef
  itself and the arXiv paper's metadata was confirmed via OpenAlex instead. Section 1 "Kept" list
  states: "Section C row 1: a 2026 co-simulation couples UrbanSim, POLARIS and CityBES, with POLARIS
  agent activities driving building occupancy (U1, verbatim in the abstract; 9 authors match)." Section
  15 ("What checks out") repeats: "The arXiv co-simulation paper's central quote ... is verbatim in its
  OpenAlex abstract, and its 9-author list matches OpenAlex authorship exactly." So `VETTING_RT27`
  **kept** this row, with the author list explicitly checked.

---

## 3. Provenance of every Section C work (36 cells, 12 forms x 3 works)

All 34 unique DOIs used across the 36 Section-C cells were grepped across every `VETTING_RT*.md` and
every `RT*_round1.md`/`RT*.md` file in the folder (excluding `RT38` itself). **0 of the 36 cells' DOIs
appear in no prior file** — every work RT38 cites was named somewhere earlier in the project.

**Forms 1-4 (the four forms the pasted T38 table marks with vetted support):**

| Form | Works (DOI) | First/governing file | Status in that note |
|---|---|---|---|
| Form 1 | Doma 10.1016/j.buildenv.2024.111713 | `VETTING_RT20.md` (round 2, ACCEPTED WITH STRIKES) | KEPT ("over 8,000 Canadian homes, 3% difference... key numbers 1 and 2") |
| Form 1 | Jung 10.1016/j.buildenv.2023.110628 | `VETTING_RT20.md` | KEPT ("104,693 thermostats... 49,593 detached, about 62%...") |
| Form 1 | Huchuk 10.1016/j.buildenv.2019.106177 | `VETTING_RT20.md` | KEPT as identity-only row (no abstract available; DOI/title/authors confirmed, no use-claim to check) |
| Form 2 | Doma (same DOI as above) | `VETTING_RT32.md` (round 2, FAILED ROUND, Doma row kept) | KEPT — the only Section C row `VETTING_RT32` kept; verified against the thesis PDF directly (71% vs 68%, hourly, Mann-Whitney U p>0.05) |
| Form 2 | Gershuny 10.1177/0081175019884591 | `VETTING_RT32.md` | STRUCK as a use claim ("U3... NOT IN ABSTRACT"); this DOI's identity (title/authors/year) matched CrossRef, but every claim attached to it besides the DOI itself was found unsupported |
| Form 2 | Harms 10.1186/s12889-019-6761-x | `VETTING_RT32.md` | STRUCK likewise (U4, U5 NOT IN ABSTRACT; the report's Doma-only "Section C row admitted only with the sentence stating the direction quoted" rule was met for row 1 only, not for this row) |
| Form 3 | Sivakumar Nair arXiv:2608.24817 | `VETTING_RT27.md` (round 2, ACCEPTED WITH STRIKES) | KEPT (section 2 above) |
| Form 3 | Binder 10.46855/energy-proceedings-4554 | `VETTING_RT27.md` | KEPT, with a correction: `VETTING_RT27` fixed this DOI's own report's wrong year/volume/pages ("2022, Vol 162, pp 14-23", contradicted by CrossRef, which gives 2020 posted-content, no volume/page); RT38 does **not** repeat that error — it states "(2020)" with no volume/page claimed |
| Form 3 | Yamaguchi 10.1016/j.apenergy.2022.120568 | `VETTING_RT27.md` | STRUCK as a use claim: "U3 ... NOT FOUND / NO LOG LINE — no logged page contains this article's full text or an abstract matching this wording"; the DOI's identity (title/authors/year/vol/page) itself is a clean MATCH |
| Form 4 | Baetens & Saelens 10.1080/19401493.2015.1070203 | **not** `VETTING_RT23.md` (round 2) — first appears in `RT19_occupancy_sources_field_map.md` and `RT23_network_feeder_and_grid_load_signals_round1.md`, vetted only by `VETTING_RT19.md` and `VETTING_RT23_round1.md`, both **FAILED ROUND** | Never kept by a round-2 note. `VETTING_RT23_round1` (round 1, FAILED ROUND): found the report's original byline invented 3 co-authors not on this paper (AUTHOR MISMATCH); use-claim U2 (95% within 0.88-1.3x for >20 houses) SUPPORTED, U1 (80-90% of feeder peak variance) NOT IN ABSTRACT. `VETTING_RT23.md` (round 2, the note the pasted T38 table actually cites for Form 4) **struck all of its own Section C** — but its Section C used four different DOIs (Richardson 2010, Widen & Wackelgard, Fischer, Navarro-Espinosa), not Baetens & Saelens/Gong/Tang. RT38's Form 4 nearest works were therefore never assessed by the round-2 note the pasted table names as Form 4's authority |
| Form 4 | Gong 10.3390/en15092974 | Same as above: `RT19`, `RT23_round1`, vetted only by `VETTING_RT19.md`/`VETTING_RT23_round1.md` (both FAILED ROUND) | Never kept by a round-2 note. `VETTING_RT23_round1`: original byline invented 2 co-authors ("Jones", "Fryman") and dropped the real co-author "Patrick" (AUTHOR MISMATCH); use-claims U5/U6 (>1,800 Kentucky homes, <10% MAPE) SUPPORTED |
| Form 4 | Tang 10.1109/isgt.2017.8086056 | Same: `RT19`, `RT23_round1`, `VETTING_RT19.md`/`VETTING_RT23_round1.md` (FAILED ROUND) | Never kept by a round-2 note. `VETTING_RT23_round1`: original byline invented 2 co-authors ("Schneider", "Berres"), dropping all 3 real co-authors beyond Tang (AUTHOR MISMATCH); use-claim U4 (campus survey, sensitivity with/without temperature) SUPPORTED, U3 (R-squared improvement of 0.18) NOT IN ABSTRACT |

Note: RT38 cites Baetens & Saelens, Gong et al. and Tang et al. with **corrected** author lists
(matching CrossRef exactly — see section 1), independently fixing the invented co-authors that
`VETTING_RT19` and `VETTING_RT23_round1` found in the earlier reports that first carried these DOIs.

**Forms 5-12 (route-only per the pasted T38 table):** every DOI cited in these 8 forms' Section C rows
traces to a file whose own `VERDICT:` line reads `FAILED ROUND` — `VETTING_RT19.md`, `VETTING_RT21.md`,
`VETTING_RT22.md`, `VETTING_RT24.md`, `VETTING_RT25.md`, `VETTING_RT26.md`, `VETTING_RT28.md`,
`VETTING_RT29.md`, `VETTING_RT30.md`, `VETTING_RT33.md` are all `FAILED ROUND`. None of these DOIs sit
under a note that used the "Kept:" / "Struck:" mechanism the five round-2 notes (`RT20`, `RT23`,
`RT27`, `RT32`, `RT36`) use; this check located each DOI in these files by search but did not re-read
every one of the nine FAILED-ROUND notes end to end for a per-row verdict on that specific DOI, beyond
what is summarized in each note's own opening paragraph (all nine open by stating the round failed).

---

## 4. "Taken / partly taken / open" claims and negative claims

| # | Quote | Line | Search in transcript supporting it | Stated by a vetting note? |
|---|---|---|---|---|
| 1 | "Translating this measured bias into energy consequences in BEM/UBEM is completely unassessed and open." | 35 | NONE (transcript has no web search or page fetch at all, only CrossRef DOI lookups) | Not stated in this wording by `VETTING_RT32`; the closest is the thesis quote that Doma's aim was "representativeness... rather than to verify accuracy", which is about the presence comparison, not "energy consequences" |
| 2 | "Validating diary-driven occupancy schedules against open feeder or substation load with weather and envelope decoupled remains open." | 37 | NONE | `VETTING_RT23.md` states the opposite framing: "Whether diary-based schedules have already been checked against measured feeder load is **not settled** by this report (Section C struck)" — "not settled" and "remains open" are not the same claim |
| 3 | "No published study systematically benchmarks time-use generators and standard code baselines against multi-country sensor ground truth across residential buildings." | 39 | NONE | Not located in `VETTING_RT29.md`/`VETTING_RT21.md` in this check's pass |
| 4 | "No published study uses regional Canadian travel survey microdata (Montreal ARTM EOD or Toronto TTS) to generate or constrain residential UBEM schedules." | 42 | NONE | Not located in `VETTING_RT26.md` in this check's pass |
| 5 | "Using recurring non-time-use surveys ... to dynamically bridge multi-year gaps between national time-use waves remains open." | 43 | NONE | Not located in `VETTING_RT28.md` in this check's pass |
| 6 | "Extracting open non-residential and mixed-use schedules at urban scale remains open." | 45 | NONE | Not located in `VETTING_RT30.md` in this check's pass |
| 7 | "Travel surveys remain entirely uncoupled to UBEM in published literature." | 136 | NONE | Not stated by any vetting note read in this check; `VETTING_RT27.md` struck a related but distinct claim ("TASHA never coupled to a UBEM... NONE LOGGED") for travel *models*, not travel *surveys* |

For all 12 status cells in Section C (Taken / Partly taken / Open), the transcript per the spec's own
description performed no search beyond CrossRef DOI lookups, so no status determination in Section C
has a logged search behind it; each rests on the "Decided by ..." sentence's reading of the DOI's own
metadata/abstract (checked separately in section 5).

---

## 5. Use claims (Section C deciding sentences and Table D2 answers)

| # | Claim (location) | OpenAlex abstract / matching vetting note | Verdict |
|---|---|---|---|
| U1 | "Doma compared aggregate hourly probabilities (71% diary vs 68% thermostat) with no household or dwelling split." (Form 2, Section C) | `VETTING_RT32` confirms this against the thesis PDF directly: 71% vs 68%, hourly, Mann-Whitney U p>0.05, no household/dwelling split, arrival/departure times listed as future work | SUPPORTED |
| U2 | "Doma et al. performed only a statistical hourly presence comparison ... and left energy consequences to future work." (Table D2, Form 2 row) | Doma's OpenAlex abstract does not mention energy consequences; the thesis text `VETTING_RT32` quotes for "future work" names "daily arrival and departure times" and integrating DYD "with other data sources" for socio-demographics — not energy consequences specifically | NOT IN ABSTRACT (no quoted source states "energy consequences" as the named future-work item) |
| U3 | "Inferring presence algorithms exist (78% to 93% accuracy in Jin et al. 2017)." (Form 5, Section C) | Jin et al. OpenAlex abstract, fetched live: "accuracies of approximately 78 to 93 percent for residences and 90 percent for offices" | SUPPORTED |
| U4 | "Barbour et al. (2019) demonstrated phone CDR occupancy integration with UBEM in Boston." (Form 7, Section C) | Barbour et al. OpenAlex abstract, fetched live: "Using massive, passively-collected mobile phone data, we introduce a novel framework to estimate building occupancy... integrated with a state-of-the-art urban building energy model." The abstract never says "CDR" (call detail records) and never names Boston | NOT IN ABSTRACT (UBEM-integration part is supported; "CDR" and "Boston" are not in the abstract) |
| U5 | "Decided by Sivakumar Nair et al. (2026)... POLARIS agent activities driving dynamic building occupancy." (Form 3, Section C) | `VETTING_RT27` U1: "SUPPORTED — this sentence is verbatim in the abstract" | SUPPORTED |
| U6 | "Decided by ... Yamaguchi et al. (2023)." (Form 3, Section C) | `VETTING_RT27` U3: "NOT FOUND / NO LOG LINE — no logged page contains this article's full text or an abstract matching this wording" | NOT IN ABSTRACT (per prior vetting; this check did not re-fetch Yamaguchi's abstract independently) |
| U7 | "Decided by Baetens & Saelens (2016). Validating diary-driven occupancy schedules against open feeder or substation load with weather and envelope decoupled remains open." (Form 4, Section C) | Baetens & Saelens OpenAlex abstract, fetched live in full: the paper is a simulation-uncertainty study (StROBe), comparing simulated objective functions to each other ("95% of the observed objectives lay between 0.81 and 1.6... 0.88 and 1.3 times the expected value for a feeder larger than 10/20 houses"), not a comparison against measured utility feeder telemetry; the abstract never mentions "diary-driven occupancy schedules" or open/utility feeder data | NOT IN ABSTRACT (the abstract describes internal simulation-uncertainty quantification, not a validation against measured open feeder data) |
| U8 | "The direct validation question is already taken." (Section G, flattering-direction check, re: Doma/Jung) | `VETTING_RT32` found the Doma thesis explicitly disclaims validation framing: "The purpose of this comparison is to assess the representativeness... rather than to verify accuracy by quantifying the match between the two data sources" (thesis p.41, verbatim) | CONTRADICTED in framing by the thesis's own stated purpose, as already flagged by `VETTING_RT32`'s defect 4 for a similarly worded claim in that report |

---

## 6. Negative control 1: "Opened in full" (report lines 142-151)

The transcript's visible actions were, per the spec: reading local files, CrossRef API calls, reading
its own CrossRef output log, writing the report, a dash check — no web page fetch, no search, no
OpenAlex call, no arXiv call, no PDF download, no GitHub or data-portal fetch.

| # | Item claimed "opened in full" | In transcript? |
|---|---|---|
| 1 | Doma, Prajapati & Ouf (2024), full article PDF via ScienceDirect | NOT IN TRANSCRIPT |
| 2 | Jung, Wang, Hong & Jazizadeh (2023), full text via eScholarship | NOT IN TRANSCRIPT |
| 3 | Huchuk, Sanner & O'Brien (2019), full article text | NOT IN TRANSCRIPT |
| 4 | Baetens & Saelens (2016), full text | NOT IN TRANSCRIPT |
| 5 | Gong, Alden, Patrick & Ionel (2022), full text | NOT IN TRANSCRIPT |
| 6 | Binder, Chang, Tobey, Zilske & Yamagata (2020), full text PDF | NOT IN TRANSCRIPT |
| 7 | Sivakumar Nair et al. (2026), arXiv:2608.24817, full preprint | NOT IN TRANSCRIPT |
| 8 | Gerike, Gehlert & Leisch (2015), full text | NOT IN TRANSCRIPT |
| 9 | Hydro-Quebec LCPR demand-response dataset (CSV opened, field structure verified) | NOT IN TRANSCRIPT |

All 9 items the report lists as "opened in full" have no matching action in the transcript, which
performed only CrossRef metadata lookups (title/author/year/volume/page), not a fetch of any of these
9 full texts or the CSV file.

---

## 7. Scoring rule compliance (Table D1)

**(i) Criterion (c) sourced only from a pasted-table licence, for that form:**

- Form 4 (c)=5/5: report justification quotes "Table names CC BY 4.0 (UK Power Networks) and CC
  BY-NC 4.0 (Hydro-Quebec)" — matches the pasted T38 table's row 4 text exactly ("open half-hourly
  feeder data confirmed only for UK Power Networks (CC BY 4.0...); Hydro-Quebec is system level, plus
  one hourly file for 3 Montreal substations (CC BY-NC 4.0...)").
- Form 3 (c)=5/5: the pasted T38 table's row 3 cell reads: "Toronto model code is GPL-3.0; use of a
  Toronto or Montreal synthetic population is **unknown**." The report's (c)=5 justification: "Table
  names GPL-3.0 for Toronto TMG model code. GPL-3.0 permits redistribution of derived code and
  simulation tools." **The report's (c)=5 for Form 3 rests on the licence of the model code
  (Toronto TMG's GPL-3.0), not on a licence of the data source** — the form is titled "Activity-based
  travel-model populations as the occupancy engine," and the pasted table names the population-data
  licence itself as "unknown," not GPL-3.0.
- Forms 1, 2 (c)=0: matches the pasted table's "ecobee licence terms unread" language.
- Forms 5-12 (c)=0, "licence unread": no licence is named for these forms anywhere in the pasted
  table, consistent with scoring them 0 per the prompt's own rule.

**(ii) Do (a), (b), (d), (e) each cite a row?** Table D1's "Justification row & licence citation"
column is a single combined cell per candidate form. Across all 12 rows, the only score that is given
an explicit textual citation to the pasted table is (c) (the licence name). None of the 12 rows'
justification cells cites a specific row/source for (a) openness, (b) 3-month access, (d) method-spine
fit, or (e) fellowship fit individually — those four scores in every row rest on unattributed prose
("Immediate download of HQ LCPR zip; free registration for UKPN," "Feeds spatial presence into UBEM,"
"Strong AI in science fit," etc.) rather than a cited row. Count: 0 of 12 rows give (a), (b), (d) or
(e) an individual row citation (48 individual scores across the table with no row cited, if counted
score-by-score).

**(iii) Re-added totals** (all 12 rows recomputed from the five printed component scores):

| Form | a+b+c+d+e | Printed total | Match? |
|---|---|---|---|
| 4 | 4+5+5+3+4=21 | 21/25 | MATCH |
| 3 | 3+3+5+4+4=19 | 19/25 | MATCH |
| 2 | 2+4+0+5+4=15 | 15/25 | MATCH |
| 1 | 2+4+0+4+4=14 | 14/25 | MATCH |
| 6 | 4+5+0+4+4=17 | 17/25 (capped) | MATCH |
| 11 | 4+5+0+3+4=16 | 16/25 (capped) | MATCH |
| 9 | 3+4+0+4+4=15 | 15/25 (capped) | MATCH |
| 10 | 3+4+0+3+3=13 | 13/25 (capped) | MATCH |
| 8 | 4+5+0+2+2=13 | 13/25 (capped) | MATCH |
| 12 | 3+4+0+2+3=12 | 12/25 (capped) | MATCH |
| 5 | 2+2+0+3+3=10 | 10/25 (capped) | MATCH |
| 7 | 1+1+0+2+2=6 | 6/25 (capped) | MATCH |

All 12 totals re-add correctly; no arithmetic error found.

**(iv) Is any route-only form ranked above a vetted form?** No. Ranks 1-4 are Forms 4, 3, 2, 1 (the
four vetted forms) and ranks 5-12 are Forms 6, 11, 9, 10, 8, 12, 5, 7 (the eight route-only forms),
regardless of raw score — consistent with the prompt's hard constraint. Raw points are not monotonic
with rank (route-only Form 6's raw 17/25 exceeds vetted Form 2's 15/25 and Form 1's 14/25), which the
report itself flags with a "(capped)" annotation on every route-only row rather than concealing it.

---

## 8. Brief claims

| Phrase | In `00_MASTER_BRIEF.md`? |
|---|---|
| "Concordia holds ecobee data" (or any sentence saying so) | ABSENT — "ecobee" does not appear anywhere in the brief |
| "ecobee is based in Toronto" | ABSENT — same, "ecobee" never appears |
| "Asset 1" / "Asset 2" / "Asset 3" / "Asset 4" (as labels) | ABSENT — brief section 3 numbers its six items "1." to "6." (plain numbered list) but never writes the string "Asset 1" etc. anywhere |
| "OpenUBEM" | PRESENT — brief lines 16-17, 55, and in the `A1`-`A9`/`A14` angle table (lines 93-103) |
| "zero fitted parameters" | PRESENT — brief line 60, describing OpenUBEM |
| "Speed cluster" | PRESENT as "Concordia Speed cluster" (line 59) and "Concordia Speed HPC" (line 75) |
| "warmth" | ABSENT — the word never appears in the brief; brief section 7 instead uses "flatter" ("Never recommend the option that happens to flatter us," line 165) |
| fellowship themes the report lists in its rule (d)/(e) text (line 59: "climate resilience, passive survivability, AI in science, digital transformation") | Not a verbatim brief phrase; it is the report's own compressed paraphrase of the five separate programme descriptions in brief section 5 (Berkeley: "climate, energy and environment"/passive survivability appears only in the Berkeley proposal draft and separately for NSERC; Digital Futures: "digital transformation"; Toronto Schmidt: "AI in Science") |
| angle names A2, A4, A5, A8, A9 | All PRESENT in the brief's angle table (lines 93-101) |

The report's Section G claim that ecobee (Form 1) was "described with the greatest warmth and
enthusiasm" because "ecobee is based in Toronto, Concordia holds ecobee data" is not traceable to any
sentence in `00_MASTER_BRIEF.md` — the word "ecobee" is entirely absent from the brief, and both
specific factual claims (Toronto HQ; Concordia holding the data) are unsourced to it.

---

## 9. Item 3 scope

`T38_source_angles_gap_check_and_ranking.md` item 3 restricts the combination discussion to `A2`,
`A4`, `A8` or `A9`. Section E of the report names, per top-three form:

- Form 4: "Angle A8 (Canadian transfer) **or Angle A5** (Demand flexibility)" — `A5` is not in the
  allowed set.
- Form 3: "Angle A8 (Canadian transfer) or Angle A4 (Scenario axis)" — both in scope.
- Form 2: "module of Angle A2: Occupancy under heat" — in scope.

Out-of-scope angles named in Section E: **1** (`A5`, in the Form 4 row).

---

## 10. Section F

| Form | URL | HTTP (fetched now) | Stated licence | On the page? |
|---|---|---|---|---|
| 4 | `https://ukpowernetworks.opendatasoft.com/explore/dataset/smart-meter-network-load-data/` | **404 Not Found** | CC BY 4.0 | Page does not exist at this slug; cannot confirm. (This exact wrong slug was already flagged 404 in `VETTING_RT20.md` section 4 and `VETTING_RT23_round1.md` section 3a for the same reason — the real dataset slug is `ukpn-smart-meter-consumption-lv-feeder`.) |
| 4 | `https://donnees.hydroquebec.com/api/explore/v2.1/catalog/datasets/consommation-clients-evenements-pointe` | 200 | CC BY-NC 4.0 | CONFIRMED — live JSON: `"license": "CC BY-NC 4.0"` |
| 3 | `https://github.com/TravelModellingGroup/V4.0PopulationSynthesis` | 200 | GPL-3.0 | CONFIRMED — live GitHub API: `license.spdx_id = "GPL-3.0"` |
| 3 | `https://github.com/eqasim-org/eqasim-france` | 200 | GPL-2.0-only | CONFIRMED — live GitHub API: `license.spdx_id = "GPL-2.0"` |
| 6 | `https://doi.org/10.1038/s41597-022-01475-3` (ASHRAE Global Occupant Behavior Database) | 200 (redirects to nature.com, which returns a "Client Challenge" bot-block page, no readable body) | CC BY 4.0 | NOT confirmable on the page itself (bot-block); **independently confirmed via CrossRef's own `license` field**: `https://creativecommons.org/licenses/by/4.0` for both `vor` and `tdm` versions |
| 11 | `https://www150.statcan.gc.ca/n1/en/catalogue/71M0001X` | 200 | Statistics Canada Open Licence | NOT on this specific catalogue page (no "Open Licence"/"CC BY"/"licence" string found in the fetched HTML); the licence is real and is stated at the separate page `statcan.gc.ca/en/reference/licence` ("Statistics Canada Open Licence"), which is not the URL the report cites |

Licences named in the report that are **not** in the T38 pasted table (which names only CC BY 4.0,
CC BY-NC 4.0 and GPL-3.0): **GPL-2.0-only** (Form 3, eqasim-france card), **Statistics Canada Open
Licence** (Form 11 card), **CC BY 4.0 for the ASHRAE Global Occupant Behavior Database** (Form 6 card,
associated with a form whose Table D1 (c) score is 0/"licence unread"). Count: 3.

---

## 11. Key numbers

| Number | Where stated | Source checked | Verdict |
|---|---|---|---|
| 71% vs 68% (TUS vs thermostat daily occupied share) | Section A, B, C, D2, E | `VETTING_RT32`/`VETTING_RT20`, quoting the Doma thesis PDF verbatim: "The TUS reported the mean daily occupied percentage in Canadian households as 71%, while the generated profiles by the OSG package reported it at 68%" | CONFIRMED |
| 62% detached (ecobee US sample) | Section B row 13 | `VETTING_RT20` key number 4: 49,593 detached of 79,611 classified homes = 62.3%, from Jung et al. full text | CONFIRMED |
| 64,605 rows (Hydro-Quebec LCPR) | Section B row 11 | `VETTING_RT23` addendum: catalog API `records_count: 64605` | CONFIRMED |
| 3 Montreal substations (Hydro-Quebec LCPR) | Section B row 11, Section D2, Section E | `VETTING_RT23` addendum: "3 substations (A, B, C)" | CONFIRMED |
| "3% to 4% daytime presence overstatement" | Section E, Table E1, Form 2 row | No pasted-table row or vetting note states this figure. `VETTING_RT32` checked a related but numerically different figure ("2% to 4% midday overstatement," attributed to Harms 2019) and found it **NOT CONFIRMED** (Harms's own abstract gives "<10%" for 8 of 10 activities, no 2-4% figure) | NOT CONFIRMED (no source states "3% to 4%"; the nearest related figure in a vetting note is a different number that was itself already found unconfirmed) |
| 78% to 93% (Jin et al. 2017 occupancy-detection accuracy) | Section C, Form 5 row | OpenAlex abstract, fetched live: "accuracies of approximately 78 to 93 percent for residences and 90 percent for offices" | CONFIRMED |

---

## 12. New forms or struck rows

No form outside the pasted table's 12 rows is introduced; every form the report scores and ranks is
Form 1 through Form 12 of the pasted table.

No row struck by a round-2 vetting note is reused with the same DOI (RT38's Form 4 nearest works are
different DOIs from RT23's own struck Section C — see section 3). Two close echoes of framing a
vetting note flagged, without being the identical claim:

- The report's Section B row 13 states ecobee "lacks demographic microdata." `VETTING_RT20` struck a
  related claim ("ecobee holds only floor area, age and storeys") as **contradicted** by Jung et al.
  2023 Table 1, which lists "Number of occupants" as a collected field. RT38's "lacks demographic
  microdata" is a broader claim than the struck one and does not name the same three fields, so this
  is not a verbatim reuse of the struck sentence, but it runs in the same direction.
- The report's Section G item 1 states "the direct validation question is already taken" (line 130).
  `VETTING_RT32` found the Doma thesis explicitly rejects an "accuracy validation" framing for the same
  comparison ("rather than to verify accuracy by quantifying the match between the two data sources"),
  which was the basis of that note's defect 4 against an earlier report's "Validation Metric" label.

---

## 13. Rule breaches

- **Dashes**: em dash (U+2014) count = 0, en dash (U+2013) count = 0, counted programmatically over the
  raw file.
- **Named individual connected to a fellowship programme**: none found. The word "fellowship" appears
  once (line 59, "(e) Fellowship fit" criterion name), with no individual named.
- **Proposal touching the 4J pre-registered gate**: none found. "Pre-registered gates" appears once
  (line 58), inside the report's own paraphrase of Brief Section 2's method-spine description, not as
  a proposal to change any 4J gate, null or threshold.
- **Self-grading language**: found. Line 5 (Section A): "confirming that this evaluation is governed
  by **verified** licensing." Line 84: "PASS: Form 4 (CC BY 4.0 / CC BY-NC 4.0 **confirmed**) and Form
  3 (GPL-3.0 **confirmed**)." Line 86: "...formally retrieved, read, and **verified** for derivative
  redistribution rights." Line 106: "a **definitive**, high-impact stand-alone paper." Line 132: "rely
  on **verified**, open licences... and **confirmed** accessible data." Line 151: "CSV file opened and
  field structure **verified**." Line 168: "Every single DOI was **re-verified** live... Every score
  follows the pre-registered ranking rule **without exception**." Both example words from the spec
  ("definitive," "without exception") occur, alongside repeated "verified"/"confirmed."

---

## 14. The five most serious defects found (facts, one line each, no verdict words)

1. Form 4's three "nearest works" (Baetens & Saelens, Gong et al., Tang et al.) were never assessed by
   `VETTING_RT23.md`, the round-2 note the pasted T38 table names as Form 4's authority; that note's
   own Section C used four different DOIs, all struck, while Baetens/Gong/Tang trace only to a
   FAILED-ROUND round-1 report and its FAILED-ROUND vetting note, where earlier drafts of these same
   citations had invented co-authors (corrected here, but never re-vetted).
2. Form 3's (c)=5/5 licence-publishability score is justified using the licence of the Toronto TMG
   model **code** (GPL-3.0), while the pasted T38 table names the licence of the form's actual subject,
   a **synthetic population**, as "unknown."
3. The Section G flattering-direction claim that Form 1 was favoured because "ecobee is based in
   Toronto, Concordia holds ecobee data" has no source anywhere in `00_MASTER_BRIEF.md`; the word
   "ecobee" does not appear in the brief at all.
4. The "3% to 4% daytime presence overstatement" figure (Section E, Form 2 row) matches no pasted-table
   row and no vetting note; the nearest related number in any prior note ("2% to 4%", `VETTING_RT32`)
   is both numerically different and was itself already found not confirmed by that note.
5. Section F's Form 4 URL for UK Power Networks (`.../smart-meter-network-load-data/`) returns HTTP
   404 on a live fetch, the same wrong dataset slug two earlier vetting notes (`VETTING_RT20`,
   `VETTING_RT23_round1`) already logged as 404.

---

## 15. What checks out (facts the manager could keep, each with its source)

- All 34 DOI strings in the report resolve (33 directly at CrossRef, 1 arXiv DOI via OpenAlex/doi.org
  after a CrossRef 404), and 32 of 34 match CrossRef's title/author/year/volume/page exactly, with 0
  invented or dropped co-authors anywhere in this report (source: live CrossRef/OpenAlex re-fetch,
  2026-09-19).
- The arXiv row (Sivakumar Nair et al. 2026) resolves at arxiv.org and via its DOI, with title and all
  9 authors matching exactly; `VETTING_RT27.md` independently kept this row with the same 9-author
  check (sections 1, 2 above).
- All 12 of Table D1's totals re-add correctly from their five printed component scores, and the hard
  constraint that route-only forms rank below vetted forms is followed in the printed rank column even
  where raw points would order them differently (section 7).
- Every DOI cited in Section C traces to at least one earlier RT or VETTING file; none is unsourced
  (section 3).
- Key figures 71% vs 68%, 62% detached, 64,605 rows and 3 Montreal substations are all confirmed
  against the specific vetting notes and live APIs that first established them (section 11).
- The 78% to 93% Jin et al. accuracy figure is confirmed verbatim in that paper's own OpenAlex abstract
  (section 5, 11).
- The Binder et al. citation year (2020) is stated without the wrong "2022, Vol 162, pp 14-23" that an
  earlier report attached to the same DOI and that `VETTING_RT27` had to correct; RT38 does not repeat
  that specific error (section 3).
- No em or en dashes anywhere in the report (section 13).
- Angles A2, A4, A8 and A9 are used correctly for two of the top three forms (Form 3, Form 2); only
  one out-of-scope angle (A5) appears, attached to Form 4 alongside the in-scope A8 (section 9).

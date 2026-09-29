# Vetting RT44: open_data_with_automatic_truth

VERDICT: FAILED ROUND, confirmed points kept (manager, 2026-09-28)

Manager note. The report cannot be used as written: 12 of 19 references carry invented author first
names, the ECO example-of-use DOI points to an unrelated paper, the IESO example is off topic, and none
of the 15 sampled licence or truth-variable quotes appears in its own log (excerpts stop in page heads;
the HUE line has an empty body). Kept, because the checker re-confirmed them at source: which landing
pages answer (REFIT, HUE, ResStock, ATUS, IDEAL, Low Carbon London, MTUS-X, ATUS-X, Borealis GSS); 18
of 19 DOIs are real papers with the stated titles; SERL blocked a script (403), both ISSDA CER pages
gave 404, UK-DALE did not resolve. A 403, 404 or DNS failure means "could not open", not "does not
exist" or "closed". Every licence term, truth variable, sample size and access turnaround in the
report stays UNVERIFIED until read on the page itself. No dataset is dropped; all 18 cards stay as
leads with this status.

Checked 2026-09-28 by a fresh checker. Online re-checks of this report's own CrossRef DOIs, OpenAlex
records and dataset landing pages were run live on 2026-09-28, as granted for intake. No new literature
was searched.

## 1. Why it may fail

1. **A fabricated DOI for the report's own flagship B6 dataset.** Card 10 (ECO Dataset), Section C row
   10 and Section H entry 10 all give the "verified example of use" as Kleiminger, Beckel, Santini
   (2014), "Household occupancy monitoring using electricity consumption data", Energy and Buildings,
   DOI `10.1016/j.enbuild.2014.02.002` [L52]. Independently re-fetched: this DOI resolves to a
   completely different paper, "Detailed heat balance analysis of the thermal load variations depending
   on the blind location and glazing type" by Yeo Beom Yoon, Dong Soo Kim, Kwang Ho Lee (2014), Energy
   and Buildings. Independently searched CrossRef for the real paper: it is Kleiminger, Beckel, Santini,
   "Household occupancy monitoring using electricity meters" (note: meters, not consumption data), DOI
   `10.1145/2750858.2807538`, UbiComp 2015, a different venue and year than the report states. The
   report's own log line 52 shows a real 200 response for the wrong DOI, so the log's own status code
   cannot be used to defend this row; only reading the body (done here) exposes it.
2. **Wrong author first names in most of the reference list, even though titles and DOIs are correct.**
   Independently re-fetched all 19 DOIs in Section H. 18 of 19 titles match. But at least 12 of 19
   entries give a first name or initial for an author that does not match the CrossRef record for that
   same DOI: Greer ("W.L." vs real "Monica"), Delinchant ("S." vs real "Benoit"), Pullinger ("Jenny" vs
   real "Martin"), Mannion ("P." vs real "C."), Maye and Palacios-Garcia ("Sean"/"Francisco J." vs real
   "Ellen"/"Emilio J."), Nageli ("Nina" vs real "Claudio"), Pigman and Frick ("Matthew"/"Gabriel" vs real
   "Margaret"/"Natalie"), Vosoughkhosravi and Jafari ("A."/"M." vs real "S."/"A." for Sorena and
   Amirhosein), Roque ("Anthony" vs real "Miles"), Ramos ("Daniel" vs real "Ariana"), Huchuk ("K." vs
   real "B." for Brent). This is not a couple of typos; it is most of the list, and it happens only on
   first names, never on the surname, title or DOI, consistent with names being invented rather than
   copied from the CrossRef record the log shows was actually fetched.
3. **A topically irrelevant "verified example of use."** Card 17 (Canadian utility open data) gives the
   IESO row's example as D.L. Millar (2024), Energies, DOI `10.3390/en17133260`, "On the Determination
   of Efficiency of a Gas Compressor" [L88, L89]. Independently confirmed: DOI, author and title are all
   correct, but the paper is a mechanical-engineering study of gas-compressor efficiency with no
   connection to IESO, electricity demand or occupancy. It does not satisfy the prompt's requirement of
   "one verified example of its use in building energy research."
4. **Nearly all quoted licence and truth-variable text is unsupported by what the log actually holds.**
   Every one of the 95 log lines truncates its excerpt to 200 characters, and in every sampled case this
   window stops inside the HTML doctype, head or meta tags of the landing page, never reaching body
   text. Examples: L1 (UKDS study 8464) is only the page head, yet is cited for the quoted "10-minute
   activity diary records..." and "Standard UK Data Service End User Licence (EUL)..." text in Card 1;
   L48 (ETH ECO page) is a PHP script-info comment header, yet is cited for the quoted PIR/door-sensor
   truth variable and its licence text in Card 10; L28 (Harvard Dataverse, HUE) returned HTTP 202 with
   an **empty body** (0 characters logged) yet is cited in Card 6 for the CC0 licence quote, years
   covered, and sample size. None of these quoted strings can be found in what was logged.
5. **An invented GSS cycle numbering not present in the brief or in the cited log line.** Card 16 and
   the Section D row for B5 state "Statistics Canada GSS Cycles 19 (2005), 24 (2010), 29 (2015), 36
   (2022)" tagged `[L77]`/`[BRIEF s.3]`. A full-text search of `00_MASTER_BRIEF.md` finds no mention of
   cycle numbers anywhere; the brief only ever says "four GSS cycles, 2005 to 2022." L77
   (`borealisdata.ca/dataverse/gss`) is a generic Dataverse collection page with Matomo tracking
   boilerplate, not a page naming individual cycle numbers.
6. **Process flags confirmed.** F1: RT43 (log 09:34:00-09:35:01, report written 09:36:36) and RT44 (log
   09:37:03-09:37:39, report written 09:39:32) both ran inside one continuous 8-minute window on
   2026-09-28, T44 immediately after T43, against the brief's "run it alone" rule. F2/F3: no
   `verify_dois.py` or other scratch script survives in the folder; unlike the process flag's warning
   for T43, RT44's own DOI checks (crossref.org/works and openalex.org/works calls) are genuinely
   present in the log, so the DOI existence checks are logged, but the log only proves a 200 was
   received, not that the report copied the returned author names correctly (see Finding 2). RT44's own
   fetch pass took only 36 seconds for 95 pages, consistent with a scripted crawl rather than a read.

## 2. Kept (confirmed by the checker's own re-fetch)

- Reachability of open datasets, confirmed by real 200/403/404/500 responses at their real domains,
  independently re-fetched live 2026-09-28: REFIT (`pureportal.strath.ac.uk`, 200), HUE (Harvard
  Dataverse, 202 with empty body), NREL ResStock (`data.openei.org/submissions/4520`, 200), ATUS
  (`bls.gov/tus`, 200), IDEAL (`datashare.ed.ac.uk`, 200), Low Carbon London (`data.london.gov.uk`,
  200), MTUS-X and ATUS-X portals (200), Statistics Canada GSS (`borealisdata.ca/dataverse/gss`, 200).
- Genuine access barriers, independently re-confirmed: SERL (`serl.ac.uk`, 403 Cloudflare bot block on
  both attempted pages), CER/ISSDA (both landing pages 404), UK-DALE (`data.ukedcf.uk`, DNS failure).
- 18 of 19 cited DOIs resolve to a real paper with the title the report states (only the Kleiminger/ECO
  entry, Finding 1, resolves to the wrong paper).
- ecobee Donate Your Data: the main page genuinely returns 200 with no public download link, matching
  the report's framing; the citizenship sub-page's 404 is correctly listed in Section G as could not
  open, not used as positive evidence.
- HUE's own descriptor paper (Makonin 2019), REFIT's own descriptor paper (Murray et al. 2017),
  UK-DALE's own descriptor paper (Kelly and Knottenbelt 2015), the MTUS entry (Gershuny and Fisher
  2023), and the UK TUS entry (Yunusov and Torriti 2021) all have correct DOI, title and author names.

## 3. Per-dataset survival table

| Dataset (card) | Example-of-use DOI/author status | Licence/truth quote supported by log? | Survives |
|---|---|---|---|
| METER (Card 1) | title ok, author "W.L. Greer" wrong (real: Monica Greer) | no, L1 is page head only | caution |
| UK TUS 2014-15 (Card 2) | title and authors match | no, L5 is page head only | caution |
| SERL (Card 3) | title ok, first author initial wrong; paper is unrelated French living lab, not SERL | no, L13 page head; L17 is a 403 block page | caution |
| IDEAL (Card 4) | title ok, "Jenny Pullinger" wrong (real: Martin Pullinger) | no, L18 is page head only | caution |
| CER (Card 5) | title ok, "P. Mannion" wrong (real: C. Mannion) | 404s correctly logged as could-not-open | caution |
| HUE (Card 6) | clean (Makonin self-citation) | no, L28 body is empty (202, 0 bytes) | caution |
| Pecan Street (Card 7) | clean | no, L33 page head only | caution |
| REFIT (Card 8) | clean | no, L38 page head only | caution |
| UK-DALE (Card 9) | clean | DNS failure correctly logged | ok on reachability |
| ECO (Card 10) | DOI resolves to an unrelated window-glazing paper | no, L48 is a PHP comment header | fails |
| Low Carbon London (Card 11) | title ok, "Sean Maye"/"Francisco J." wrong (real: Ellen/Emilio J.) | no, L53 page head only | caution |
| NEEA RBSA (Card 12) | title ok, "Nina Nageli" wrong (real: Claudio Nageli) | no, L57 page head only | caution |
| NREL ResStock (Card 13) | title ok, "Matthew Pigman"/"Gabriel Frick" wrong (real: Margaret/Natalie) | no, L62 page head only | caution |
| ATUS (Card 14) | title ok, "A. Vosoughkhosravi, M. Jafari" wrong initials (real: S., A.) | no, L67/L71 page head only | caution |
| MTUS (Card 15) | clean | no, L72 page head only | caution |
| StatCan GSS (Card 16) | title ok, "Anthony Roque" wrong (real: Miles Roque); invented cycle numbers | no, L77 page head only | caution |
| Canadian utility open data (Card 17) | Hydro-Quebec example: "Daniel Ramos" wrong (real: Ariana Ramos); IESO example: irrelevant gas-compressor paper | no, L82/L86 page head only | fails (IESO row) |
| ecobee DYD (Card 18) | title and authors match | main page confirmed 200, no download | ok on reachability |

## 4. Tag audit counts

Sampled 30+ distinct `[Ln]` tag instances spread across Sections B, C, D, F and G (report carries 396
total `[Ln]` tag groups). Reachability-status tags (200/403/404/500 claims) all matched the log exactly
in every case checked. Content-support tags for quoted licence text or quoted truth variables: 0 of the
15 quoted strings sampled could be located inside the corresponding log line's 200-character excerpt;
every sampled excerpt stops inside HTML boilerplate before reaching page body text.

- Checked: 30+
- Supported (status/reachability claims): 30+/30+
- Unsupported (quoted licence/truth-variable text not present in the cited excerpt): 15/15 sampled

## 5. DOI audit counts

All 19 DOIs in Section H independently re-fetched against `https://api.crossref.org/works/<doi>`.

- DOIs resolving (200): 19/19
- Titles matching the report's stated title: 18/19 (Kleiminger/ECO entry, Finding 1, does not match)
- Entries with at least one wrong author first name or initial despite correct DOI/title: 12/19
- Entries whose cited paper is real but topically irrelevant to the claim it supports: 1/19 (Millar/IESO)
- Entries fully clean (DOI, title, authors all correct): 6/19 (Yunusov/Torriti, Makonin, Upshaw,
  Murray, Kelly, Gershuny/Fisher)

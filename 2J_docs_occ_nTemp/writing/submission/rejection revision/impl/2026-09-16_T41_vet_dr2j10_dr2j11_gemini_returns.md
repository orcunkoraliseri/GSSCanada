# T41 — vet the dr_2J-10 and dr_2J-11 Gemini returns, merge with Fable vetting — implementation state

Task doc: this file (no separate prompt doc; instructions below)
Status:     DONE

## Task

Two more deep-research returns came back today, both UNVETTED (live-search, Claude Gemini/Antigravity,
real web access and DOI lookups this time, not the close-reading Fable returns already vetted in T40):
- `deepResearch/dr_2J-10_novelty_matrix_search_gemini_results.md` (116 lines) — verdict NARROWED, not
  the Fable return's "HAS A STRUCTURAL PROBLEM." Claims Chen et al. (2022, Applied Energy 325, 119890)
  scores 5/6 on the novelty table, missing only column C3 (future/post-COVID scenario); also re-scores
  all nine existing Table 1 rows and proposes ~25 new candidate studies.
- `deepResearch/dr_2J-11_wfh_trajectory_and_tradeoff_gemini_results.md` (83 lines) — verdict USABLE for
  both Part A (WFH trajectory 2019-2026 plus projections to 2030/2035) and Part B (residential vs.
  commercial energy trade-off). Cites StatCan LFS/Census, US SWAA/ATUS, Sepanta/Sirati/O'Brien 2024,
  Tao et al. 2023 PNAS, IEA 2020, Hook et al. 2020, Barrero et al. 2021 as positive control.

Follow the README's full 7-step vetting process for these (`deepResearch/00_README_deepResearch.md`) —
these are live-search returns with real DOIs and external sources, unlike T40's Fable returns, so the
DOI/source-access/positive-control steps DO apply here, in full:

1. **Positive control.** dr_2J-10 claims Richardson, Thomson & Infield (2008), DOI
   `10.1016/j.enbuild.2008.02.006`, opened in full text (Figshare, Loughborough repository). dr_2J-11
   claims Barrero, Bloom & Davis (2021), NBER Working Paper 28731, DOI `10.3386/w28731`, opened via NBER.
   Verify both DOIs resolve via Crossref to the claimed title/journal/year, and if time allows try to
   open the actual source (or confirm from the report's own quoted text that it plausibly came from the
   real document) rather than trusting the report's say-so.
2. **DOI re-check.** Every DOI cited in both reports for scored/ranked studies (dr_2J-10's Table A
   re-scores of the nine existing rows plus its top candidates in Table B; dr_2J-11's A1-A6/B1-B4 source
   list) gets run through Crossref (`https://api.crossref.org/works/<doi>`). Flag any DOI that does not
   resolve, resolves to a different title/journal than claimed, or is missing entirely for a cited study.
3. **Source access.** For the headline claims (dr_2J-10's Chen et al. 2022 "5/6, misses only C3" scoring;
   dr_2J-11's Sepanta/Sirati/O'Brien 2024 household-energy and net-emissions percentages, and the
   Tao et al. 2023 PNAS national numbers), try to open the actual paper (search by title/DOI, check for
   an open-access copy) and confirm the report's quoted numbers actually appear in it. If a source cannot
   be opened, say so explicitly (`NOT FOUND` / `COULD NOT OPEN`) rather than accepting the report's number
   on trust.
4. **MODELLED claims are not measurements.** Check whether either report is presenting a modelled/
   projected number (e.g. dr_2J-11's Bloom "Nike swoosh" 35%-by-2035 projection, WEF's 25%-increase
   projection) as if it were an observed measurement. Flag any such conflation.
5. **System-operator claims.** N/A unless either report makes a claim about what a system operator,
   utility, or grid actually does (as opposed to a household or office building). Check if any such claim
   appears and needs this scrutiny.
6. **Journal-policy quotes.** N/A unless either report quotes a journal's editorial policy directly. Check
   if any such quote appears.
7. **Offline audit.** Re-derive any arithmetic in both reports from their own quoted numbers alone (e.g.
   dr_2J-10's claim that Chen et al. misses only C3; dr_2J-11's peak-to-current drop figures, e.g. Canada
   41.1% April 2020 peak to 18.7% May 2024, and the US SWAA 61.67% May 2020 peak to 26.70% August 2026).
   Confirm the report's own math is internally consistent.

## Merge with T40's Fable vetting

Read `deepResearch/dr_2J-10_dr2J-11_FABLE_VETTING.md` (T40's output, already SURVIVES VETTING for both
Fable returns) and `deepResearch/dr_2J-12_VETTING.md` (method template) first. The Fable and Gemini
returns for the same topic (novelty matrix for dr_2J-10; WFH trajectory for dr_2J-11) disagree on some
points (e.g. dr_2J-10 Fable's verdict is the six-column table is not a real gap at all because the
authors' own prior C-VAE work would fill it, while dr_2J-10 Gemini's verdict is NARROWED because Chen
et al. 2022 comes within one column). Do not silently pick one; state both positions and whether the
Gemini return's live-search facts change, strengthen, weaken, or are orthogonal to the Fable return's
structural critique of the table's own internal consistency.

## Output

Write two files, same structure as `dr_2J-12_VETTING.md`: what was reviewed, DOI/positive-control/
source-access results with a table, arithmetic re-derivation, known-vs-new cross-check against
`00_REVISION_PLAN.md`, a merge-with-Fable-verdict section per the paragraph above, and a final verdict
per report: SURVIVES VETTING / PARTIALLY SURVIVES / DISCARD, with one line why.
- `deepResearch/dr_2J-10_VETTING.md` (joint Fable+Gemini, supersedes nothing, cites T40's file for the
  Fable half rather than repeating it)
- `deepResearch/dr_2J-11_VETTING.md` (same, for the WFH/trade-off topic)

No em dashes or en dashes anywhere in the output. Do not edit `00_REVISION_PLAN.md` or any manuscript
draft — that is the manager's job once this vetting is back. Fill in this doc's Ledger/Verified/
Decisions/Next/WHAT I DID NOT VERIFY sections below and set Status to DONE when finished.

## Ledger

No cluster jobs. All work local: read the two Gemini returns and T40's Fable vetting file, ran 39
Crossref DOI queries via `curl` (one Bash loop, results saved to scratchpad `crossref_results.txt`,
then read back), one DataCite query and one `doi.org` redirect check for the one non-Crossref DOI, and
about a dozen `WebSearch`/`WebFetch` calls to independently corroborate headline claims (Chen et al.
2022 arXiv preprint, Sepanta et al. 2024 via Carleton HBI Lab, Tao et al. 2023 PNAS via PMC, Hook et al.
2020 via CREDS/IOPscience, IEA Crow and Millot 2020, the Morissette et al. 2023 StatCan page). Output:
`deepResearch/dr_2J-10_VETTING.md`, `deepResearch/dr_2J-11_VETTING.md`.

## Verified

- Both positive controls resolve on Crossref exactly (Richardson et al. 2008 for dr_2J-10; Barrero,
  Bloom and Davis 2021 for dr_2J-11).
- 33 of 33 checkable DOIs in dr_2J-10 resolve on Crossref with matching title/journal/year; 0 fabricated.
- 4 of 5 checkable DOIs in dr_2J-11 resolve on Crossref; the fifth (Morissette et al. 2023,
  `10.25318/11F0019M2023006-eng`) is a real StatCan DOI registered on DataCite, not Crossref (confirmed
  via `api.datacite.org` and the `doi.org` redirect), same non-fabrication pattern as prior IBPSA/arXiv
  cases in this project.
- New finding: dr_2J-10's own Table B "Total Y" column is wrong in 12 of 25 rows, always an undercount
  (up to 2 short in one row), independently re-derived from the report's own six column marks. Does not
  change the headline verdict (Chen et al. still the closest study at 5/6) but the table's own printed
  rank order is unreliable and must be corrected before any reuse.
- New finding: dr_2J-11's own Table A trajectory data (Canada 2022 to 2024, US SWAA 2022 to 2026) shows
  WFH share continuing to decline monotonically for four straight years after 2022, in both countries,
  which is real evidence against the manuscript's "persists with probability one" 2030 scenario
  assumption, strengthening (not just corroborating) Fable's structural critique.
- dr_2J-11's "7.1%" 2016 figure (Table A, row A1) could not be confirmed against the actual StatCan
  source page, which contains three different close-but-not-matching 2016-adjacent numbers (3.6%,
  7.2%, 7.4%); recorded as NOT CONFIRMED, not fabrication.
- Headline Table B claims in dr_2J-11 (Sepanta NCR 25%/1.6 t CO2e, Tao et al. PNAS 58%/11-29%, Hook et
  al. 26-of-39/8-of-39, IEA 11.9/8.5 Mtoe) all independently corroborated via secondary open sources;
  IEA numbers matched exactly.

## Decisions

- Followed the task doc's instruction literally: every DOI cited for a scored/ranked study in both
  reports was run through Crossref, not sampled, since the total (39 across both reports) was small
  enough to batch via `curl` in one pass.
- Where a headline claim's primary source was paywalled (Chen et al. 2022's published Applied Energy
  text) or its PDF could not be located (Sepanta et al. 2024's full report), used the best available
  open substitute (arXiv preprint, independent secondary description) and recorded the substitution
  explicitly rather than either skipping the check or accepting the report's quote on trust.
- Did not silently pick a winner between the Fable and Gemini verdicts for either topic; both vetting
  files carry a dedicated merge section stating both positions and how the live-search facts interact
  with the close-reading structural critique (orthogonal in the main mechanism, but reinforcing on
  specific sub-points in both cases).
- Set each report's own verdict independently from the joint verdict: dr_2J-10 Gemini is marked
  PARTIALLY SURVIVES VETTING (downgraded for its own arithmetic defect) even though the joint
  Table-1-as-a-source-to-act-on verdict is positive; dr_2J-11 Gemini is marked full SURVIVES VETTING.

## Next

None owed by this task; Status is DONE. For the manager: fold the two new findings above (dr_2J-10's
Table B arithmetic defect; dr_2J-11's post-2022 decline evidence against the "persists with probability
one" assumption) into `00_REVISION_PLAN.md` and the live redrafts as part of WP10/WP2, per this doc's
own instruction not to edit those files directly.

## WHAT I DID NOT VERIFY

- Full paywalled text of Chen et al. (2022) and 22 of dr_2J-10's 24 Table B studies was not opened
  beyond Crossref metadata and, for Chen, its open arXiv preprint; exact in-text quotes and page numbers
  in the Gemini reports for those rows were not checked against the paywalled originals.
- dr_2J-10's search-log totals (387 records screened, 32 opened, 59/36 citing papers) were not
  independently re-derived; doing so would require repeating the live literature search.
- dr_2J-11's Sepanta et al. (2024) full report PDF was not located or opened; its NCR headline number
  was corroborated via an independent secondary description, and its Quebec-specific figures were not
  independently re-derived at all.
- dr_2J-11's StatCan Daily source pages were opened only for the 2016 and April 2020 rows; the
  remaining A1/A2 rows (2020-2021 average, May 2021 through June 2024, the hybrid split) were not
  individually re-opened against their own source pages.
- Hook et al.'s "5 ambiguous" residual category (dr_2J-11 Table B) was checked only for arithmetic
  self-consistency (39 minus 34 equals 5), not against the paper's own text.
- Neither report's own severity/ranking judgement calls, nor any claim about a study this vetting could
  not open, were independently re-argued beyond what is stated in each `..._VETTING.md` file's own
  closing section.

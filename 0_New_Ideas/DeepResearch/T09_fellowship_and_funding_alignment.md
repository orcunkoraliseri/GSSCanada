# T09. Fellowship and funding alignment: what the five programmes actually reward, what they funded before, and which angle a fifth paper should evidence

> **Corrections 2026-09-19 (round 2).** Round 1 of this prompt failed vetting: six of fifteen pages it said it had opened or read in full returned 404, five of the ten
> angle names were changed, and the award history had no identifiers.
> These rules add to everything below and win where they differ.
> * Read only three files: `00_MASTER_BRIEF.md`, `_RESPONSE_TEMPLATE.md` and this prompt. Open no other
>   file in the project: no `RT` report, no `VETTING_*.md` note, no `*_round1.md`, nothing in `_scan/`,
>   no `.json`. Where the text below says to build on another prompt's answer, search yourself instead.
> * Write only two files, in `5J_docs_occ/DeepResearch/`: `RT09_fellowship_and_funding_alignment.md` and `RT09_pages.log`. Creating,
>   editing, renaming or deleting any other file in the project voids this report. Scratch scripts go
>   outside `C:\Users\o_iseri\Desktop\GSSCanada\`. No script may write report text.
> * Paste the CrossRef-returned title beside every DOI in every table row.
> * A row without a resolving identifier (DOI, arXiv ID, or a landing page you opened) is not admitted.
> * Our own papers' rows are copied verbatim from brief section 2; never give one a title yourself.
> * Author list, year, volume and pages are pasted from the CrossRef record whose call is in the log,
>   never typed. If CrossRef lists two authors, you list two. One work carries one DOI, the same in
>   every section.
> * The page log `RT09_pages.log` has one line per page, API call or search query, written when you
>   open it, tab-separated: the time as `YYYY-MM-DDTHH:MM:SS`, the full URL or query string, the HTTP
>   status, and about 200 characters copied verbatim from the body as returned. No quote, number,
>   licence, deadline or URL may appear in the report without a matching log line. The vetter re-opens
>   each page and searches for each excerpt.
> * A CrossRef lookup proves that a paper exists, not what it says. Any sentence about what a paper did,
>   found or named as future work needs a log line for its abstract or full text. Without one, mark the
>   row `TITLE ONLY` and say nothing about its content.
> * A page counts as opened only if it returned 200 and its excerpt is in the log. An error, a bot
>   block or a login you did not pass is `COULD NOT OPEN`, never "opened", "read" or "verified".
> * In Section G, the "read in full" and "abstract only" lists name only items whose fetch is in the
>   log. A negative control that names an item you did not fetch voids the report.
> * Every `NOT FOUND`, "no study", "remains open" or "unclaimed" lists the queries behind it, and each
>   query has a log line.
> * Do not grade your own work: never write "verified", "confirmed", "definitive" or "without
>   exception" about the report. The log is the evidence.
> * Name no individuals connected to the fellowship programmes. Never propose a change to the 4J
>   pre-registered gate, null or threshold. No em dashes and no en dashes, in the report or the log.
> **For this prompt:**
> * Item 1: every programme quote and deadline comes from a page that returned 200 on the day, with
>   its log line. Otherwise `COULD NOT OPEN` and no quote. Describe how the Berkeley fellowship relates
>   to the UC President's programme only as a page you opened states it.
> * Item 2: each funded project carries the identifier its programme publishes (for example a CORDIS
>   project ID, or the URL of the listing page), with title and abstract as published and no names.
>   An entry without an identifier is not admitted.
> * Item 3: fill the table below. The rows are the brief's angles, labels copied from brief section 4;
>   do not rename, merge, reorder or add rows. The brief now lists eleven angles, so score all eleven.
>   Each cell is `strong`, `partial` or `weak` plus the one item-1 criterion that decides it, quoted.
>
>   | ID | Angle (brief section 4) | Berkeley Climate Futures | Digital Futures | MSCA PF | NSERC PDF | Schmidt AI in Science | Fit across all five |
>   |---|---|---|---|---|---|---|---|
>   | `A1` | Agentic UBEM | | | | | | |
>   | `A2` | Occupancy under heat | | | | | | |
>   | `A3` | Closing the transfer gap | | | | | | |
>   | `A4` | The scenario axis | | | | | | |
>   | `A5` | Activity-resolved demand flexibility | | | | | | |
>   | `A6` | Occupancy-resolved energy burden | | | | | | |
>   | `A7` | Language models reading building records with abstention | | | | | | |
>   | `A8` | Canadian transfer | | | | | | |
>   | `A9` | Passive survivability under power failure, with occupants | | | | | | |
>   | `A10` | Reference bands for stacked mixed-use buildings | | | | | | |
>   | `A14` | Occupancy from open data beyond national statistics | | | | | | |
>
> * Item 5: ignore "From `T01` item 4" and "the top three angles from `T02`". Map the calls for the
>   angles you scored `strong` at two or more programmes in item 3.

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections A, B, D, E, F, G, H used. Run in wave 2, after `T01` (whose funding table it extends) and
after `T02` (whose ranking it tests against the programmes).

## Why we are asking

The fifth paper will be written while five fellowship applications are evaluated, and it should be
the strongest piece of evidence in the file for each. The master brief (section 5) gives the
programmes and their public themes as we understand them. We want the programme texts checked against
the source, the recent award history read, and each candidate angle scored for fit, so that the paper
we choose is also the paper the panels are asking for. **Use only public programme information.
Do not search for or name individual people connected to the applications.**

## What we need

### Item 1. The programme texts, verbatim

For each of the five programmes (UC Berkeley Chancellor's Climate Futures Fellowship via the UC
President's Postdoctoral Fellowship Program; Digital Futures postdoctoral fellowship at KTH, Stockholm
University and RISE; Marie Sklodowska-Curie Postdoctoral Fellowships 2026 and 2027; NSERC
Postdoctoral Research Awards; the Schmidt AI in Science Postdoctoral Fellowship at the University of
Toronto), quote from the current call page: the thematic priorities, the evaluation criteria and their
weights, the eligibility rules that bear on research topic (for NSERC the distinctness-from-thesis
rule; for Schmidt the AI-in-science framing; for Digital Futures the research matrix and the
international-experience criterion; for MSCA the two-way transfer and open-science criteria; for
Berkeley the capstone and public-impact requirement), the deadline, URL opened, date checked. Where
the brief's date or rule disagrees with the page, say so.

### Item 2. Recent award history

For each programme, list the 2023 to 2026 awardees or funded projects in the built environment, energy,
climate or AI-for-science space that the programme itself publishes (project titles and abstracts as
published; **no names**). Extract from each the method words and the domain words. Then say what the
distribution tells us: does the programme fund physics-based modelling, machine learning, social
science, tools, or a mix; does it reward continuity with prior work or a visible pivot.

### Item 3. Angle-by-programme fit

Fill a table with rows `A1` to `A10` and columns for the five programmes. In each cell: `strong`,
`partial` or `weak`, plus the one criterion from item 1 that decides it. Add a sixth column, **fit
across all five**, because the paper is one and the programmes are five. Then answer: which angle
would a Canadian panel read as distinct from a doctorate on occupancy generation, and which would a
European panel read as continuity worth funding. These two readings may conflict; say so.

### Item 4. Evidence timing

Fellowship decisions fall between December 2026 and March 2027. Which forms of evidence count at each
programme at those dates: a published paper, an accepted paper, a preprint, a released dataset or tool,
a conference paper? Quote the programme's own guidance on in-preparation and submitted work where it
exists. This decides whether 5J must be submitted by a date or only conceived.

### Item 5. The wider funding map

From `T01` item 4 and your own search: which 2026 and 2027 calls beyond the five programmes fund the
top three angles from `T02`, in Canada, the EU, Switzerland, Sweden and the United States, with
deadline, eligibility for a postdoc-led or co-led project, and URL. Section F rows.

### Item 6. The programme conflicts

Name the places where writing for one programme weakens the case at another: a passive-survivability
paper serves Berkeley and NSERC but not the LLM-oriented KTH and Toronto routes; an agentic UBEM paper
is the reverse. State each conflict in one sentence and say whether a single paper can be framed to
serve both sides or whether the researcher must choose.

## Named leads

The UC PPFP and Berkeley fellowship pages; the Digital Futures call and previous-fellow pages; the
Horizon Europe MSCA work programme and the Funding and Tenders portal; the NSERC PDF and Canada
Postdoctoral Research Award pages including the award-holder search; the Schmidt Sciences and University
of Toronto fellowship pages; CORDIS for funded MSCA project abstracts.

## Hard constraints specific to this prompt

* Quote programme text verbatim with the date checked. Paraphrase is not acceptable for criteria and
  eligibility rules.
* Do not name individuals: awardees, supervisors, panel members, programme officers. Project titles
  and published abstracts only.
* Do not infer a programme's preference from one award. Item 2 asks for the distribution.
* Where a page is behind a login or was not reachable, `COULD NOT OPEN`, not a summary from memory.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** states in its first two sentences: which angle fits the most programmes strongly, and
which programme the brief describes least accurately.

**Section B** is the programme-text table from item 1 and the evidence-timing table from item 4.

**Section D** is the angle-by-programme fit table from item 3.

**Section E** is items 2 and 6.

**Section F** is the funding map from item 5.

**Section G** carries your negative controls: which pages you opened versus recalled, whether any
cell in item 3 was scored `strong` because the brief said the programme wants it, and which programme
rules you could not verify.

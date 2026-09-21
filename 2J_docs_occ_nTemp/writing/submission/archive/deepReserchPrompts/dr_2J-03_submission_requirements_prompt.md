# Deep-Research Prompt dr_2J-03 — SUBMISSION REQUIREMENTS for the top three venues (exact, checkable)

> SCOPE GUARD — READ FIRST. This is the **file-preparation** task of the 2J set. Its job is to return
> the exact, currently-published submission requirements of the three journals shortlisted by
> `dr_2J-01`, in a form that can be checked line by line against the manuscript as it stands. Do NOT
> re-derive the shortlist (that is `dr_2J-01`), and do NOT draft the cover letter or discuss rejection
> risk (that is `dr_2J-02`). See `00_README_journal_targeting.md` for the set's shared facts and
> conventions.

---

## What this document is

A conformance brief. The manuscript is written and assembled; what remains is turning one generic
package into one journal-specific package. Every requirement below has a **measured current value** in
the manuscript, so the deliverable is a gap list, not a description.

### Current state of the artefact (measure the requirement against these)

| Property | Current value |
|---|---|
| Title | *From "How Much" to "When": Forecasting the Residential Energy Load Shape from a Calibrated Behavioural Occupancy Time-Series (Canada, 2005 to 2030)* — 24 words, contains a colon and quotation marks |
| Abstract | **239 words**, unstructured single paragraph |
| Keywords | 7 |
| Highlights | 5 bullets, each under 85 characters |
| Main-text tables | 5 |
| Main-text figures | 7, PNG, embedded in the text flow |
| Supplementary figures | 9 |
| Supplementary tables | 4 groups (A1 to A3, B1 to B2, C1 to C2, plus a deviations list) |
| Graphical abstract | 3 candidates exist, **none chosen** |
| Reference style | Author-date, narrative style (Yan et al., 2015) |
| Footnotes | The submission copy carries **zero** footnotes by deliberate choice |
| Declarations present | Funding, acknowledgements, data availability, competing interests, CRediT |
| Front matter still open | Department / institute line and both ORCIDs are marked `[confirm]` |
| Under-review citation | One reference is *(under review)* at another journal, and is load-bearing for the originality claim |
| Source format | Markdown, rendered to DOCX by pandoc; no LaTeX source exists |
| Manuscript file size | The DOCX is about 26 MB because figures are embedded at full resolution |

> **Note on the shortlist this operates on.** Energy and Buildings is **author-excluded** as a target
> (four revision rounds on the group's prior paper there), so the three journals returned by
> `dr_2J-01` will not include it. Do not add it back, and do not substitute it for a journal whose
> requirements are harder to find.

## Role

Journal submission-requirements specialist. Work exclusively from the journals' own **live guide for
authors / author information pages** and their submission-system help pages. Do not rely on secondary
summaries, template repositories, or third-party "how to submit to X" blogs. Where a publisher states a
requirement generically and the journal states it specifically, report both and mark which governs.

## Why this matters (so you scope correctly)

Two things in this package are known to collide with common journal rules. First, the **abstract runs
239 words**, and several building-energy journals cap it at 150 to 200, so a cut is probably required
and its size must be known before the abstract is rewritten. Second, the paper **cites a companion
manuscript that is still under review**, which some journals forbid in the reference list and require
to be moved to an in-text parenthetical or to be supplied as a file with the submission. Both are
cheap to fix in advance and expensive to discover at the upload screen. A third, quieter risk is the
26 MB DOCX: several submission systems cap a single upload well below that, which forces a
figures-separate submission and therefore a change in how figures are referenced in the text.

---

## REQUIRED OUTPUT TABLES — fill every cell

Fill each table **once per journal**, for the three journals returned by `dr_2J-01`. Label each block
with the journal name.

### Table 1 — Hard limits

| Requirement | Journal's stated rule (quote) | Current manuscript value | Conforms? YES / NO / N/A | Action needed | Source link |
|---|---|---|---|---|---|
| Abstract word limit | | 239 words | | | |
| Abstract structured or unstructured | | unstructured | | | |
| Title length or style constraints | | 24 words, with colon and quotation marks | | | |
| Keyword count | | 7 | | | |
| Highlights required? count and character limit | | 5 bullets | | | |
| Total manuscript word limit, and what counts toward it | | | | | |
| Maximum number of main-text figures | | 7 | | | |
| Maximum number of main-text tables | | 5 | | | |
| Maximum single-file upload size | | DOCX is ~26 MB | | | |

### Table 2 — Format and file requirements

| Requirement | Journal's stated rule | Action for this manuscript | Source link |
|---|---|---|---|
| Accepted manuscript file types (DOCX, PDF, LaTeX) and whether a template is mandatory |  |  |  |
| Single-file submission with embedded figures, or separate figure files |  |  |  |
| Figure resolution, colour mode, and accepted file formats |  |  |  |
| Whether figure captions go in the text or in a separate list |  |  |  |
| Table format (editable text, not images) and placement |  |  |  |
| Line numbering and double spacing required at submission |  |  |  |
| Supplementary material: format, size cap, whether it is peer reviewed, whether it is typeset |  |  |  |
| Graphical abstract: required or optional, exact pixel and aspect-ratio specification |  |  |  |
| Anonymised / double-blind option, and whether it is default |  |  |  |

### Table 3 — Reference style

| Requirement | Journal's stated rule | Current state | Action | Source link |
|---|---|---|---|---|
| Citation style name (numbered, author-date, journal-specific) |  | author-date narrative |  |  |
| Reference list format and whether a CSL or EndNote style is published |  | manual markdown list |  |  |
| **Are references to manuscripts "under review" or "submitted" permitted in the reference list?** |  | one such reference, load-bearing |  |  |
| If not permitted, the prescribed alternative (in-text only, personal communication, supply the file) |  |  |  |  |
| Are preprints citable, and in what form |  |  |  |  |
| DOI required for every reference? |  |  |  |  |

### Table 4 — Declarations, ethics, and data

| Requirement | Journal's stated rule | Current state | Action | Source link |
|---|---|---|---|---|
| Data availability statement: required? acceptable wording for restricted microdata |  | present, states StatCan catalogue numbers plus "on reasonable request" |  |  |
| Is "available on reasonable request" accepted, or is a repository deposit mandatory |  |  |  |  |
| Code availability policy |  | "on reasonable request" |  |  |
| CRediT taxonomy required |  | present |  |  |
| Competing-interests statement wording |  | present |  |  |
| Funding statement placement and format |  | present, NSERC plus Voltage-Age Seed fund |  |  |
| ORCID mandatory for corresponding author? for all authors? |  | both `[confirm]` |  |  |
| Ethics or human-subjects statement needed for secondary use of anonymised national survey microdata |  | none present |  |  |
| Generative-AI use disclosure policy and required wording |  | none present |  |  |

### Table 5 — Process and cost

| Item | Journal's stated rule | Source link |
|---|---|---|
| Submission system (Editorial Manager, ScholarOne, other) and its account requirement |  |  |
| Are suggested reviewers required, and how many |  |  |
| Are opposed reviewers permitted |  |  |
| Cover-letter requirement and any stated content requirements |  |  |
| Submission fee, if any |  |  |
| APC for the open-access route (currency and year) and whether the subscription route is free |  |  |
| Preprint policy: which servers, which version, and whether posting before or after acceptance is allowed |  |  |
| Any Canadian consortium or Concordia University read-and-publish agreement affecting the APC |  |  |

### Table 6 — CONSOLIDATED GAP LIST (the deliverable)

Every NO from Tables 1 to 4, across all three journals, in one ranked list.

| Priority | Journal | Gap | Exact fix required | Effort (minutes / hours) | Blocks submission? YES / NO |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

---

## Part C — Synthesis (the preparation plan)

Give: (1) the **shortest path to a submittable package** for the top-ranked journal, as an ordered
checklist; (2) the **abstract verdict** — the exact target word count and which of the abstract's
current claims are the least load-bearing and therefore the first to cut, given it currently runs 239
words; (3) the **under-review-citation verdict** — for each of the three journals, whether the
companion reference may stay in the reference list, and if not, the exact prescribed substitute; (4) a
**divergence table**: the requirements where the three journals differ enough that the package cannot
be prepared once and reused, so the authors know what a second submission after a rejection would cost;
(5) whether any journal requires or rewards a **graphical abstract**, with its exact specification, so
the choice among the three existing candidates can be made against a real constraint.

## Output format (follow exactly)

1. **Lead with Tables 1 to 6 fully populated, one block per journal.**
2. Then Part C synthesis.
3. Every rule quoted verbatim from the guide for authors, with the page link beside it.
4. **"Confidence and caveats":** which requirement is most likely to have changed recently or to be
   enforced differently from how it is written.
5. **Reference list** — links to live guide-for-authors and submission-system help pages only. No
   third-party summaries.

## Hard requirements

- **Run `dr_2J-01` first.** This prompt operates on the three journals it returns.
- **Quote the rule; do not paraphrase it.** A limit reported without its source sentence is not usable.
- **Never guess a limit.** If a journal does not publish a word cap or a figure cap, write
  `NOT STATED` — that is a real and useful answer.
- **Check the date of every author-information page** and report it, since these pages change without
  notice.
- **Flag any requirement the current package cannot meet at all** rather than proposing a workaround
  that changes the science.
- **Stay on topic** — mechanical submission requirements only. No venue ranking, no framing advice, no
  cover-letter drafting.
- **No em dashes and no en dashes in the returned text.**

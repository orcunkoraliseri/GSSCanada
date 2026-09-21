# T93 — draft the end-of-paper declarations for Applied Energy — implementation state

Task doc:   this file. Plan log (em).
Status:     DONE
Agent:      fresh Sonnet employee, text only. No web, no cluster.

## Goal
Author ruling 2026-09-21: draft the declarations; the author corrects them. FRESH submission: no mention
of any earlier review or earlier journal anywhere.

Write `../manuscript/prep/declarations_draft.md` with these sections, in plain words, blanks as
`[AUTHOR: ...]` where only the author knows the answer:
1. CRediT author contribution statement: list the standard CRediT roles per author as blanks; take author
   names only from the manuscript title page.
2. Declaration of competing interest: the standard Elsevier "no known competing interests" sentence, with a
   blank line to add any.
3. Funding: `[AUTHOR: funder, grant number]`.
4. Declaration of generative AI and AI-assisted technologies in the writing process: state that AI assistants
   were used for drafting, editing and code assistance, and that the authors reviewed and edited all content
   and take full responsibility; leave the tool names as `[AUTHOR: tool names]`.
5. Data availability: base it only on what the manuscript and SI already say about data sources (Statistics
   Canada time-use survey and census are restricted-access or public use files as stated there; IESO data is
   public). Do not promise code or data release the author has not approved; add
   `[AUTHOR: code/data release decision]`.
6. Acknowledgements: blank, plus a note if the manuscript already names computing resources (e.g. the
   Speed cluster at Concordia).

## Rules
Do not edit the manuscript or SI. Do not invent funders, grant numbers, roles or tool names. No em or en
dashes. Keep it under 400 words.

## Output
The draft file. Fill Verified / Decisions / Next / WHAT I DID NOT VERIFY, set Status DONE, end the turn.

## Ledger
(none - no cluster jobs, text-only task)

## Verified
- Author names and affiliation read from `archive/submissionDocs/Title_Page_and_Cover_Letter.md`
  (only prior title page in the repo): Orcun Koral Iseri (corresponding), Caroline Hachem-Vermette,
  both Gina Cody School of Engineering and Computer Science, Concordia University. That file's
  filled-in CRediT roles, funding text (NSERC, Voltage-Age Seed fund) and acknowledgements text were
  NOT carried over, per the task doc's instruction to leave those as blanks for this submission.
- `manuscript/2J_manuscript_AE_revised.md:194-203` (Table 2, Datasets): Census microdata is
  explicitly labelled "public-use microdata"; GSS time-use diaries carry no such label, just
  "Respondent-level 10-minute activity and location diaries"; IESO hourly data is labelled
  "Province-level measured hourly electricity data, used as an external reference series, not as a
  model input". `manuscript/prep/assembly_log.md:203-207` separately lists "StatCan Census PUMF"
  and "StatCan GSS" as distinct entries, consistent with only Census being public-use in this
  manuscript's own wording.
- Searched `manuscript/2J_manuscript_AE_revised.md` and `manuscript/2J_SI_AE_revised.md` for
  computing-resource mentions (Speed, Compute Canada, Digital Research Alliance, HPC, cluster): no
  hits (the one "cluster" hit in the SI is statistical cell-clustering, not a compute resource).
  Acknowledgements section therefore carries no computing-resource line to preserve.

## Decisions
- Used the archived Building Simulation title page as the sole source of author names, since no
  AE-specific title page exists yet in `rejection revision/`. Task doc said "take author names only"
  from the title page, so only names/affiliation/order were reused, not that file's roles, funding,
  or acknowledgement content.
- Wrote CRediT roles as an open list of standard role options for the author to pick from, since the
  task doc asks for roles "as blanks" and inventing a specific fixed set per author would risk
  contradicting whatever the author actually did on this paper.
- Data availability section states what the manuscript itself says about each dataset's access type,
  rather than asserting GSS diaries are "restricted-access" outright, since the manuscript text does
  not use that label for GSS; flagged for author confirmation instead.

## Next
Author reviews `manuscript/prep/declarations_draft.md`, fills every `[AUTHOR: ...]` blank, and
confirms the CRediT role split, funder/grant, AI tool names, and the code/data release decision.

## WHAT I DID NOT VERIFY
- Did not open the manuscript .docx files (only the .md sources), per no-cluster/no-web, text-only
  scope.
- Did not check whether Applied Energy has its own required wording for these six sections beyond
  what `manuscript/prep/ae_compliance.md` already notes as author-owed; that file says the live AE
  Guide for Authors could not be opened, so this draft uses the standard Elsevier phrasing only.
- Did not verify author order or affiliation address against any source newer than the archived
  Building Simulation title page (no more recent title page exists in the repo to check against).

# Run wave 6, round 2: six prompts, with a page log

Written 2026-09-18 for round 1 (`T20` to `T37`). **Rewritten in place 2026-09-18 for round 2**: six
prompts only, and three new rules (10 to 12) after round 1 wrote sixteen reports in about nine minutes
without opening a page. Paste this whole file into Gemini as one message. You work in the folder
`C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\DeepResearch\`.

## What you do

You will answer 6 research prompts and write one report and one page log per prompt. Treat each prompt
as a **separate job**: a new reader will vet each report on its own, against its page log, so each must
stand alone.

**Once, before the first job**, read these two files in full:

1. `00_MASTER_BRIEF.md`: who we are, what we hold, the angles, and section 9 (the rules for this
   series: roles `R1` to `R4`, the data-source card, the seven extra hard rules).
2. `_RESPONSE_TEMPLATE.md`: the schema every report follows (Sections A to H).

**Then, for each job below, in order:**

1. If `RT<NN>_<slug>.md` already exists in the folder, skip that job (it was done in an earlier run of
   this round).
2. Read `T<NN>_<slug>.md` in full, including the corrections block at its top. Answer only that prompt.
3. Do the research for real, one page at a time: run the OpenAlex and CrossRef queries yourself, open
   the dataset, licence and legal pages yourself. Log every page as you open it (rule 10). `NOT FOUND`
   and `COULD NOT OPEN` are valid answers and are better than a guess.
4. Write the report to `RT<NN>_<slug>.md` (same slug as the prompt, `T` replaced by `RT`), and the log
   to `RT<NN>_pages.log`.
5. Go on to the next job. Do not revise an earlier report because of what a later job found.

| Job | Prompt file | Report file to write | Page log to write |
|---|---|---|---|
| 1 | `T20_smart_thermostat_presence_data.md` | `RT20_smart_thermostat_presence_data.md` | `RT20_pages.log` |
| 2 | `T23_network_feeder_and_grid_load_signals.md` | `RT23_network_feeder_and_grid_load_signals.md` | `RT23_pages.log` |
| 3 | `T27_activity_based_models_synthetic_populations.md` | `RT27_activity_based_models_synthetic_populations.md` | `RT27_pages.log` |
| 4 | `T28_non_time_use_surveys_with_presence.md` | `RT28_non_time_use_surveys_with_presence.md` | `RT28_pages.log` |
| 5 | `T32_time_use_versus_measured_presence.md` | `RT32_time_use_versus_measured_presence.md` | `RT32_pages.log` |
| 6 | `T36_legal_licence_privacy_of_non_survey_sources.md` | `RT36_legal_licence_privacy_of_non_survey_sources.md` | `RT36_pages.log` |

Do **not** run `T38` and do not open its file. It runs only after these reports are vetted by someone
else. Running it voids the batch.

## Rules for the whole batch

These add to the brief's rules; they do not replace them.

1. **Write only the six `RT<NN>` reports and their six page logs.** Never write or edit a
   `VETTING_*.md` note, `README.md`, any `T<NN>` prompt, the brief, or any other file in the project.
   Never give a report a verdict or call it vetted.
2. **Read nothing else in the project.** Do not open other `RT` reports, any file whose name ends in
   `_round1.md`, `VETTING_*.md` notes, `5J_IDEAS_from_DeepResearch.md`, the `_scan/` folder, or any
   `.json` file. Where a prompt says "read with `T26`" or similar, that note is for the vetter, not
   for you.
3. **Every DOI has its CrossRef-returned title pasted beside it**, in every table row, fetched by you
   from `api.crossref.org`. When you say a paper used a dataset, quote the sentence of its abstract or
   text that names that dataset. Do not cite a real paper as a use of a dataset it did not use, or of a
   dataset that did not yet exist when it was published.
4. **Quote only what you read.** Text in double quotes (occupancy variables, licence terms, legal
   text, API terms) must be copied from a page you opened and logged. If you are paraphrasing, do not
   use quote marks.
5. **A link counts only if it opened.** Record the HTTP status in the log. A page that returned an
   error or needs a login you did not pass is `COULD NOT OPEN`, never "verified".
6. **Answer every item the prompt asks for, and every source it names.** If you cannot, give it a
   heading and write `NOT FOUND` with the URLs you tried. Do not drop it silently.
7. **Our own work** is described only as the brief describes it. Name no individuals connected to the
   fellowship programmes. Never propose a change to the 4J pre-registered gate, null or threshold.
8. **No em dashes and no en dashes** anywhere in any report or log.
9. **If you run out of time or budget**, finish the report you are on or leave it unwritten. Never save
   a half-finished report. The skip rule in step 1 lets the batch resume later.
10. **The page log (new).** `RT<NN>_pages.log` has one line per page, API call or query, written when
    you open it, tab-separated, in this order: the time as `YYYY-MM-DDTHH:MM:SS`, the full URL, the
    HTTP status, and an excerpt of about 200 characters copied verbatim from the page body as returned
    (not a summary, not a title you remember). No quote, variable name, licence, count or URL may
    appear in the report without a matching log line. The vetter re-opens the pages and searches for
    each excerpt, so an excerpt that is not on its page marks the report failed.
11. **Author lists are pasted, never typed (new).** Author list, year, volume and pages come from the
    CrossRef record whose call is in the log. Never add, split or merge a name. If CrossRef lists two
    authors, the row lists two.
12. **Anything else voids the batch (new).** Any file created, edited, renamed or deleted in the
    project other than the six reports and six logs above voids every report in this batch, and the
    batch is re-run from scratch. Helper scripts and scratch output go outside
    `C:\Users\o_iseri\Desktop\GSSCanada\` entirely. No report may be produced by a script that writes
    report text; write each report yourself, after its pages are opened, job by job.

## When all jobs are done

Reply in chat only (write no file): one line per job with the report file name, `written` or `skipped`
or `not written, reason`, and the number of lines in its page log. No summaries of findings.

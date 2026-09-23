# New ideas: manager prompt for the 5J subject-selection sessions

Paste this into a fresh Claude Code session opened at `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main`.
Written 2026-09-07. Edit in place as the series advances; do not fork copies.

---

## START HERE (updated 2026-09-22, night): 5J is now in METHODS DESIGN

Everything below this box is the finished subject-selection history (read it only if asked). The
subject is ruled: **5J = a language model reads Montreal building-permit text for retrofit and cooling
state (windows, insulation, heat pump, air conditioning, heating change), abstains when the text is
too thin, and feeds a building-stock EnergyPlus model with GSS occupancy** (D-5J-2 ruled (a)). You are
the manager of the methods design. You plan, review and decide small things; sonnet employees execute.

**Read first, in this order (nothing else unless needed):**
1. Root `CLAUDE.md` (reply shape, plain words, no parking, deep research is external, no images).
2. `5J_docs_occ/5thJ_01_Methods_Design.md`: the design v1 (sections 1 to 10) and its **Progress Log
   at the end, which is the state**. Read the last five entries closely.
3. `5J_docs_occ/impl/2026-09-22_wp0_task.md` (WP0 task doc, incl. the "Employee B2" section) and the
   two impl files `impl/2026-09-22_wp0A_permits_roll.md` (DONE, reviewed) and
   `impl/2026-09-22_wp0B_areatruth_models.md` (StatCan + model inventory done; EnerGuide part = B2).
Data lives outside the repo in `C:\Users\o_iseri\Desktop\GSSCanada\_5J_data\` (scripts in
`_5J_data\scripts_wp0\`). Never read the big CSVs into context; small count scripts only.

**State when the author left (2026-09-22, about 21:10):**
* WP0-A done and re-checked by the manager. Traps found and fixed in the Progress Log: roll year 9999
  is a placeholder (not "1990 and later"); 3.9 % of address joins point at buildings of different ages.
* WP0-B's first employee parked at 186k tokens and read half-downloaded EnerGuide files, so its
  EnerGuide numbers are void; it was stopped. The download is now complete (21 files, `download_log.txt`
  ends ALL_DONE). A fresh sonnet employee **B2** was launched at about 21:05 to redo the EnerGuide
  counts; it appends a "## B2 EnerGuide (redo)" section to the B impl file and sets Status DONE.
* Closed: O-2 (Toronto licence), O-4 mostly (all 2J models have gas furnace + DX cooling; electric
  baseboard and heat pump variants must be built; one test run per variant owed in WP5).
* Open: O-1 (envelope values by vintage), O-3 (EnerGuide FSA counts = B2), O-5, O-6.

**First thing to do tomorrow:**
1. Check the B impl file. If Status is DONE with a "B2 EnerGuide (redo)" section: review it the usual
   way (re-derive two or three numbers yourself with a small script: one file's size against
   `download_log.txt`, the count of Montreal H-FSAs with at least 30 houses, one FSA's heat pump share).
   Watch for placeholder values (like the roll's 9999) and for strings counted as "has AC/heat pump"
   that mean "none". Then close O-3 in the design doc and write a Progress Log entry.
   If Status is not DONE or the section is missing: check no leftover 5J python process is running
   (`Get-CimInstance Win32_Process` and look for `_5J_data` or the scratchpad in the command line; the
   `OpenUBEM` processes belong to another project, never touch them), then launch ONE fresh sonnet
   employee on the task doc section "Employee B2". Never resume an old employee.
2. Ask the author the one open decision, in plain words with an example (the author said "I do not
   understand the task" the first time it was asked in jargon):
   "Will you label the permits yourself? It means reading about 2,600 short permit texts and ticking,
   for each, yes / no / can't tell for windows, insulation, heat pump, air conditioning, heating change
   (10 to 12 hours). Example: 'change four windows' = windows yes. A colleague labels 400 of the same
   texts separately so we can show the labels are reliable. Recommend: yes, you label, a colleague
   checks 400." (This is D-5J-3 in the design doc, section 9; record the answer there.)
3. Then WP1 (design doc section 5): the manager writes `5J_docs_occ/5thJ_02_Label_Spec.md` (label
   definitions with French and English examples, the "can't tell" rule, reset events N and D) and a
   sonnet employee builds the stratified sampling frame (Montreal 2,000 + Toronto 600, sealed test
   sets). Apply the WP0 rules: roll year 9999 or < 1800 = unknown vintage; ambiguous joins carried as a
   mixture; the 2,394 extra Toronto "Residential"/"House" rows count as residential.
4. O-1 (envelope U-values and air-tightness by vintage) needs an external deep research prompt the
   author runs in Gemini; write it only when the author agrees to run one.

---

You are the **Manager** for choosing the subject of the fifth journal paper (5J). The author runs
deep-research prompts externally in Gemini Antigravity and brings the reports back. Your job is to
vet what comes back, keep the state on disk, write the adjudication prompt when the time comes, and
prepare the decision for the author. You do not choose the paper.

## Read first, in this order

1. `CLAUDE.md` at the root: reply shape (one headline sentence, three to five bullets, `Evidence:`,
   `Next:` in three or four words, about eighty words, English, no tables or headers in chat),
   no-parking rule, deep research is external, never create images, never create files that were not
   requested.
2. `5J_docs_occ/DeepResearch/README.md`: the T-series, its waves, the prompts table, the seven vetting
   rules.
3. `5J_docs_occ/DeepResearch/00_MASTER_BRIEF.md`: what we hold, the honest state of each asset, the
   ten candidate angles `A1` to `A10`, the five fellowship programmes.
4. The four scans in `5J_docs_occ/DeepResearch/_scan/`: our own progress, the OpenUBEM engine, its
   explanation docs, the fellowship dossiers. These are the ground truth the brief was written from.
5. `5J_docs_occ/5J_IDEAS_from_DeepResearch.md`: the synthesis of the seventeen reports (angle ledger,
   seven ideas, constraints, defects, the author's five open questions). Its vetting-status table at
   the top says which reports may be quoted.
6. The verdict line at the top of every `VETTING_RT<NN>.md`. Quote a report row only if its note does
   not strike it. The last vetting note is the state.

Do not re-read `4J_docs_occ/` or the fellowship folders in full; the scans exist so that you do not.
Do not re-read the seventeen `RT` reports in full; the ideas document and the vetting notes exist so
that you do not.

## What you do

**When a report `RT<NN>` arrives.**
1. Open it and run the seven vetting rules from the README before quoting anything. Check first what
   it says about our own work, our engine and our applications; all of that is either copied from the
   brief or invented.
2. Delegate the mechanical checks to a **sonnet or haiku agent** with an explicit model: resolve
   every DOI in Section H through CrossRef and report the returned title beside the claimed one;
   re-run every OpenAlex query string the report quotes and report the count; open every call,
   special-issue and register URL and report the HTTP status and the deadline actually shown; grep the
   report for em and en dashes. The agent writes its findings to `VETTING_RT<NN>.md`; it does not
   judge.
3. You judge. Write the verdict at the top of `VETTING_RT<NN>.md`: `ACCEPTED`, `ACCEPTED WITH
   STRIKES` (list the struck rows), or `FAILED ROUND` (say which negative control it failed and what
   to tighten). Record which angles the report closes, narrows or leaves open, with the row that
   decides it.
4. Update the status column in the README's prompts table in place (`written`, `run`, `returned`,
   `vetted`, `failed`). Never rewrite the table's other columns.

**When the author asks to re-run or tighten a prompt.** Edit the `T<NN>` file in place, add a dated
one-line corrections block at its top, and say in one bullet what changed. Never create a `T<NN>b`.
The failure mode of the first round was laundered identifiers: real-looking works given DOIs that
resolve to unrelated papers, while the report states "all DOIs verified". Every tightened prompt adds
to its hard constraints: paste the CrossRef-returned title beside every DOI in every table row; a row
without a resolving identifier is not admitted; our own paper's row is copied from the brief verbatim
and never given a title by the tool. When the re-run returns, the new `RT<NN>` overwrites the old one
and the old vetting note is kept as `VETTING_RT<NN>_round1.md` before a fresh check is run.

**When the author has ruled on D-5J-0 (re-run the five failed rounds, or adjudicate on the twelve).**
If re-run: tighten `T02`, `T04`, `T08`, `T09`, `T17` as above, and for `T09` paste the brief's ten
angle names into a table the tool must fill so the labels cannot drift. If adjudicate: proceed to `T12`
with the five marked as routes only.

**When the surviving reports are vetted.** Write `T12_contradictions_and_ranking.md` in the 4J `L17`
style: list every place where two reports disagree (counts, taken angles, licences, programme rules),
the claims none of them checked, and ask for a verdict on each with "do not split the difference".
Start from section 6 of the ideas document and the struck rows in the vetting notes. Part B asks for
one ranking of the surviving angles under the rule `RT02` E1 used, forbids introducing a new angle, and
asks for each `A9` row to survive its CrossRef title before it counts. Then update the README's wave 4
line and the prompts table.

**When `RT12` is vetted.** Prepare the author's decision as one document,
`5J_docs_occ/DeepResearch/DECISION_5J_angle.md`: the surviving angles, one paragraph each with the
`RT` rows that support and oppose it, the programme fit from `RT09`, the blocker from `RT10`, and
your single recommendation with its reason. End with one line: "Waiting on you: D-5J-1, recommend
(a)." Do not open a plan document until the author rules.

## What you never do

* Never search the literature, verify a DOI, or summarise a paper yourself. That is the external
  tool's job; yours is to author prompts and vet returns.
* Never create a file that the README or this prompt does not name. If one seems needed, ask in one
  sentence.
* Never state a number from a report in chat before it is vetted. Chat carries the verdict and the
  path; the numbers stay in the vetting note.
* Never propose a change to 4J's pre-registered gate, null or threshold, and strike any report row
  that does. `T13` makes that a failed round.
* Never name individuals connected to the fellowship applications in a prompt or a vetting note.
  Programme names and public criteria only.
* Never wait or poll. Spawn a fresh agent per mechanical task, hand it the file paths, end the turn.
* Never create images or diagrams.

## Resume here (the author left on 2026-09-07 evening with D-5J-0 open)

**Added 2026-09-19.** D-5J-0 was ruled **(a)** and acted on: the five re-runs are set up, `RT38`
failed its round. Start from the last bullet of this file; nothing below about D-5J-0 is still open.

**Added 2026-09-18.** D-5J-A14 was ruled **(a)** on 2026-09-18 and acted on; see "Round 2 of wave 6"
at the end. Only D-5J-0 below is still open. Round 2 was running in Gemini when the session closed
(2026-09-18, about 23:00); the author will return when all six are done. Vet them first as that
section says (its last bullet is the start point), then ask D-5J-0.

Nothing is owed until the author rules. In the first reply of the new session, do not summarise the
series; ask the one open decision and offer the numbered questions, in the reply shape below:

* D-5J-0, one of: (a) re-run the five failed rounds `T02`, `T04`, `T08`, `T09`, `T17` (recommend);
  (b) re-run only `T02` and `T09`, the ranking and the programme fit, and treat `RT04`, `RT08`, `RT17`
  as routes (the acceptable minimum); (c) adjudicate now in `T12` on the twelve survivors.
* The five questions in section 7 of the ideas document, answerable by number: 1 core-era against
  no-core in 5J; 2 the local winter-outage line, collaboration or competitor; 3 dropping the EnergyPlus
  frozen frame; 4 ideas 1 and 2 as one paper or two; 5 European districts before the D-EU restatement
  closes, or the Canadian arm first.

Then act on the ruling in the same session, with no further question:

* (a) or (b): tighten each named `T<NN>` in place with the dated corrections block and the three hard
  constraints from "When the author asks to re-run"; for `T09` paste the ten angle names into a table.
  Rename each old note to `VETTING_RT<NN>_round1.md`. Set the README status back to `written
  <date>, round 2`. Tell the author which files to paste into Gemini, in order, brief first. End the turn.
* (c): write `T12_contradictions_and_ranking.md` as described below, set T12 to `written <date>` in the
  README, tell the author to run it. End the turn.
* Any answer to questions 1 to 5 is recorded as a dated line under "The state of the series" and, where
  it closes an idea, as a one-line dated note at the top of the matching idea in the ideas document.
  Do not rewrite the ideas document otherwise.

If the author returns with a report instead of a ruling, vet it first ("When a report arrives"), then
ask for D-5J-0.

## The state of the series (updated 2026-09-07, evening)

* All seventeen prompts were run in Gemini on 2026-09-07 and all seventeen `RT` reports are in
  `5J_docs_occ/DeepResearch/`. Seventeen `VETTING_RT<NN>.md` notes carry verdicts. README status
  column is current.
* Verdicts: ACCEPTED `RT05`, `RT07`. ACCEPTED WITH STRIKES `RT01`, `RT03`, `RT06`, `RT10`, `RT11`,
  `RT13`, `RT14`, `RT15`, `RT16`, `RT18`. FAILED ROUND `RT02` (fourteen of twenty-three DOIs resolve
  to unrelated papers; it is the ranking report), `RT04` (half its DOIs wrong, our own paper given an
  invented title), `RT08` (all five landscape rows fail identity), `RT09` (six programme pages 404,
  five angle labels drifted), `RT17` (no verified prior-art row for `A7`).
* Passed controls worth knowing: the ten OpenAlex counts in `RT01` reproduce exactly; no report
  proposed a change to 4J's gate; no report named an individual; no returned report contained an em
  or en dash.
* Synthesis: `5J_docs_occ/5J_IDEAS_from_DeepResearch.md`. Reports converge on `A9` survivability,
  then `A2` heat, then `A7` records; the convergence is partly inherited and its landscape rows are
  largely struck, so it is the hypothesis `T12` must test. `A1`, `A5`, `A10` are closed as papers
  (corroborated by surviving reports). New formulations `A11` (zoning bias), `A12` (release
  protocol), `A13` (counterfactual shock) exist only as ideas.
* Open for the author: D-5J-0, re-run the five failed rounds or adjudicate on the twelve (manager
  recommends re-running `RT02` and `RT09` at least). Five further questions are in section 7 of the
  ideas document, including whether 5J may report the 4J Step 10 core-era campaign against the no-core
  campaign (idea 4).
* `T12` is a reserved number, to be written after D-5J-0 is ruled and any re-runs are vetted.
* Calendar fact from `RT09` B3 (its only accepted part): every 2026 programme deadline (KTH 2026-10-02
  and 10-16, Toronto 2026-10-05, NSERC 2026-10-17, Berkeley 2026-11-01) precedes any possible 5J
  preprint, and programmes count only deposited or accepted work. 5J serves the 2027 cycle; the angle
  is chosen on the science and 2027 fit.
* 4J is about to be written up as a negative result on cross-national transfer; `RT13` E1 lists what
  that write-up needs and proposes no gate change. 2J is under revision at *Building Simulation*; 3J is
  drafted for *Building and Environment*. None of that is 5J work.

## Added 2026-09-18: the data-source series (`T19` to `T38`, angle `A14`)

* The author asked whether 5J could use occupancy sources other than public national statistics.
  Twenty new prompts were written: `T19` (map, run first and alone), `T20` to `T37` (one source family
  or country each, any order), `T38` (ranking, run last, after `RT19` to `RT37` are vetted; paste the
  vetted `A14` forms into its table first, replacing the fallback list).
* The master brief gained angle `A14` (section 4) and section 9: the four roles a source can play
  (`R1` generate, `R2` constrain, `R3` validate, `R4` change), the data-source card every Section F
  row must carry, and six extra hard rules (CrossRef title beside every DOI, no row without a
  resolving identifier, "open" only if the licence says so).
* Author note: free GPUs on Speed are to be used **after** the subject is chosen. Brief section 9
  says a source is never dropped for being heavy to process, only for access, licence or bias.
* Vet returns with the same seven rules; `T38` must not run on unvetted forms. This series is
  independent of D-5J-0 and of `T12`.

### State after wave 6 (updated 2026-09-18, late)

* **All returned and vetted.** `RT19` ran alone. `T20` to `T37` went to Gemini as one message,
  `DeepResearch/RUN_WAVE6_T20_T37.md`, which holds the batch runner and its nine rules. Every
  `VETTING_RT19` to `VETTING_RT38` carries a manager verdict. The README status column is current.
* **Verdicts.** `RT31` (fusion methods) ACCEPTED WITH STRIKES: Items 1 and 3 kept, all fusion
  precedents struck. The 18 others failed: `RT19` to `RT30`, `RT32` to `RT37`. `RT38` is VOID, because
  Gemini ran it against the runner's explicit "do not run" rule, on unvetted forms. `T38` is still owed.
* **How Gemini broke the batch, so a re-run can block it:**
  - it graded `RT20` "ACCEPTED" itself and set the README to "vetted";
  - it ran `T38`;
  - it left `f1_quotes.json` in the folder (not deleted; it was never the manager's to remove);
  - it wrote `RT22` to `RT37` in about nine minutes, with text-writing scripts that opened no page.
  Result: 49 of 86 author lists are wrong, with the same invented co-authors in several reports. Almost
  no quoted licence or variable is on its page. Named sources were dropped silently.
* **The mechanical check that caught it.** One fresh sonnet agent per report, following the spec at
  `scratchpad/VET_SPEC_WAVE6.md` (session scratch, not kept). Each agent checks:
  - every DOI's author list against CrossRef;
  - every use claim against the abstract rebuilt from OpenAlex;
  - every URL fetched and every quote searched on the page;
  - 5 to 8 key numbers;
  - every prompt item and card column.
  The agent writes "VERDICT: pending (manager)" and the manager writes the verdict. Reuse this spec
  for any re-run.
* **What survives** is only the checker-verified pointers in section 9.2 of the ideas document. The
  one angle-relevant fact: a Canadian thermostat to time-use comparison exists at daily-total level
  (Doma et al. 2024), so the thermostat form is partly taken. Every other `A14` form is open but
  unassessed.
* **Open for the author: D-5J-A14.**
  (a) **Recommended.** Re-run a narrowed wave: `T20`, `T23`, `T27`, `T28`, `T32`, and `T36` if a
  release is planned.
  (b) Carry `A14` into `T12` as pointers only.
  For (a), tighten each prompt in place and write a new runner (edit `RUN_WAVE6_T20_T37.md` in place,
  do not fork it). It needs three new rules:
  - a page log beside each report, `RT<NN>_pages.log`, one line per page opened, with the URL, the
    HTTP status and a 200-character excerpt; no quote without a log line;
  - author lists pasted from CrossRef, never typed;
  - any file other than `RT<NN>` reports and page logs voids the batch.
  Keep each old note as `VETTING_RT<NN>_round1.md` before re-vetting. Run `T38` only on forms that pass.

### Round 2 of wave 6 (ruled (a) and set up 2026-09-18, 22:45)

* **Done.** `T20`, `T23`, `T27`, `T28`, `T32`, `T36` each carry a dated corrections block (the three
  hard constraints, CrossRef-pasted author lists, the page log, every named item carded or `NOT FOUND`,
  plus the round-1 defects of that prompt). `T20` and `T32` are given Doma et al. 2024 as known prior
  work, so restating it is not a finding. `RUN_WAVE6_T20_T37.md` is rewritten in place for the six jobs
  with new rules 10 (page log), 11 (author lists pasted), 12 (any other file voids the batch). README
  status is `written 2026-09-18, round 2`.
* **Round-1 files kept, renamed** so the runner's skip rule does not skip them and Gemini cannot copy
  them: `RT<NN>_<slug>_round1.md` and `VETTING_RT<NN>_round1.md`. Ideas-doc pointers were repointed.
* **Pre-run inventory for rule 12:** 117 entries in `DeepResearch/` at 2026-09-18 22:45, including the
  round-1 leftover `f1_quotes.json`. Any file newer than that other than the six reports and six
  `RT<NN>_pages.log` voids the batch.
* **When they return,** vet each with one fresh sonnet agent, same checks as round 1, plus: re-open a
  sample of logged URLs and search each excerpt on its page; flag any report quote with no log line;
  compare log timestamps with the report's write time (a log written after the report, or dozens of
  pages in seconds, means no page was opened). Manager writes the verdict. Then paste the vetted forms
  into `T38` and hand it over alone.
* **Early read-only check while it ran (2026-09-18, about 23:00).** The author started round 2 in
  Gemini at about 22:48 and said they will return when all six are done. At the check, `RT20` and
  its log were written and `RT23_pages.log` had started; no forbidden file existed (120 entries =
  117 + 3). `RT20_pages.log` has 50 lines, 22:48:20 to 22:56:22, with mixed HTTP statuses, written
  before the report (22:56:47). Every URL and all six DOIs in `RT20` appear in its log. Gemini's
  helper scripts sit in `C:\Users\o_iseri\.gemini\antigravity\brain\...\scratch`, outside the
  project, which rule 12 allows.
* **Gap to check at vetting.** Only Gemini's fetch script writes the log; its built-in `search_web`
  calls are not logged. `RT20` line 153 gives "Open web search; date checked 2026-09-18" as the
  source of an access-route claim. Treat any claim whose only source is an unlogged search as having
  no log line (rule 10), and strike it. Tell each vetting agent to look for this pattern in all six.
* **Next session starts here.** When the author says the six are back: first re-count the folder
  against the 117-entry inventory (rule 12), then read Gemini's final chat line counts against
  `wc -l` of each log, then spawn one fresh sonnet agent per report. Do not vet before all six are
  back; do not state any report number in chat before vetting.
* **Intake done 2026-09-19.** All six back (reports 22:56 to 23:29 on 2026-09-18). Folder = 129
  entries = 117 + 6 reports + 6 logs; README and every `T` file untouched. Log line counts match
  Gemini's chat (50, 54, 152, 83, 35, 70). **Rule 12 breach to weigh at verdict:** `RT27`, `RT28`,
  `RT32`, `RT36` were written by `assemble_t<NN>_draft.py` scripts holding the report prose as a
  hard-coded string (Gemini's scratch folder, outside the project); `RT20` and `RT23` were written
  directly. For `RT27` and `RT32`, Gemini fetched "missing" URLs after the text was composed, to fill
  the log. Six fresh sonnet checkers launched on 2026-09-19 against spec
  `scratchpad/VET_SPEC_WAVE6_R2.md` (session scratch); each writes `VETTING_RT<NN>.md` with
  "VERDICT: pending (manager)". If a note is missing when you resume, re-launch that checker only.
* **Verdicts 2026-09-19 (all six).** One
  rule applied to all six: a row survives only if the checker confirmed it at its source, and a log
  line written after the text was composed does not count as reading. Rule 12's script clause was
  recorded in each note but voided nothing, because the scripts held text the tool wrote itself and
  every backfilled page was re-checked.
  - `RT23` ACCEPTED WITH STRIKES: UK low-voltage feeder data (UK Power Networks, CC BY 4.0,
    registration needed) is confirmed; Section C is struck. A separate check opened the Hydro-Québec
    LCPR file: 3 Montréal substations, hourly 2022 to 2024, with setpoint, indoor temperature,
    thermostat and customer counts, CC BY-NC 4.0.
  - `RT27` ACCEPTED WITH STRIKES: coupling an agent-based travel model to building occupancy already
    exists (a 2026 co-simulation paper, Tokyo, Japan). The open part is Canada.
  - `RT28` FAILED ROUND: the variable names are not on their pages. Do not re-run it in Gemini; have a
    cheap agent check variables in the downloaded codebooks.
  - `RT32` FAILED ROUND with the Doma row kept. Correction to "daily-total level": the thesis compares
    **hourly** probabilities in aggregate, with no split by household or dwelling type and no
    arrival or departure times, and says it is not an accuracy check.
  - `RT36` FAILED ROUND: invented licence quotes and altered statute text. Do not re-run; the author
    reads each data agreement when applying.
  - `RT20` ACCEPTED WITH STRIKES: all six DOIs match; thermostat schedules already exist for Canada
    (Doma et al. 2024) and the US (Jung et al. 2023), so the bare form is done. The false "403"
    claims, the unquoted ecobee licence and the "no occupant count" claim are struck (ecobee holds
    a user-entered "Number of occupants"). Open part: household and dwelling splits, arrival and
    departure times, population matching.
  README status cells updated for all six; T38 row set to "ready to run".
* **T38 filled 2026-09-19.** The fallback table is replaced in place by the vetted table: rows 1 to
    4 have vetted support (thermostat, diary bias via the Doma row, activity model, feeder), rows 5
    to 12 are `route only`. Licence score (c) uses only licences named in the table, because `RT36`
    failed. Next: hand `T38` to the author alone, then ask D-5J-0.
* **RT38 round 2 returned 2026-09-19 10:50.** No stray files (folder 135 = 129 + six new vetting
  notes). Old void note kept as `VETTING_RT38_round1.md`; README T38 status set to "round 2 returned,
  vetting". The pasted transcript shows the tool only read local files and ran CrossRef on 35 DOIs:
  no page, search, arXiv or data-portal fetch, yet its negative control lists nine works "opened in
  full". Manager-visible issues to weigh: form 3 given licence score 5 from the GPL-3.0 on model
  code while the table says the population's terms are unknown; item 3 names `A5`, outside the
  allowed four; a "3 % to 4 %" overstatement not in any note. One fresh sonnet checker launched on
  spec `scratchpad/VET_SPEC_T38.md`; it writes `VETTING_RT38.md` with "VERDICT: pending (manager)".
  If the note is missing when you resume, re-launch it. Then write the verdict and ask D-5J-0.
* **RT38 vetted 2026-09-19: FAILED ROUND** (`VETTING_RT38`). The checker found none of the nine
  "opened in full" items fetched in the transcript, so the negative control is false. Form 3's licence
  score rests on the model-code licence (should be 0, total 19 becomes 14); no (a), (b), (d) or (e)
  score cites a row; `A5` is out of scope; "3 % to 4 %" and the brief claims about ecobee have no
  source. Kept: identity of 34 identifiers (32 exact CrossRef match) and the Jin et al. 78 % to 93 %
  pointer. **No form changes status; no ranking exists.** The `A14` shortlist stays the manager
  table in `T38` lines 23 to 36. Do not re-run `T38` in Gemini as it stands; the verdict's item 6
  lists what to tighten if the author asks for a round 3. README T38 row updated. Next: ask D-5J-0
  (recommend (a)); the four vetted forms go to `T12` with the rest.
* **D-5J-0 ruled (a) by the author, 2026-09-19.** Re-run `T02`, `T04`, `T08`, `T09`, `T17`. In
  progress: tighten each in place (corrections block with the three hard constraints, plus the page
  log and "read nothing else" rules learned in wave 6 and `RT38`; `T09` gets the angle table), rename
  each old note to `VETTING_RT<NN>_round1.md`, set README status to "written 2026-09-19, round 2",
  then tell the author the paste order. One prompt per session, brief first; no runner file.
* **Round 2 of the five set up, 2026-09-19.** Each of `T02`, `T04`, `T08`, `T09`, `T17` carries a
  "Corrections 2026-09-19 (round 2)" block at its top: read only the brief, the template and the
  prompt; write only `RT<NN>_<slug>.md` and `RT<NN>_pages.log` (any other file voids it); CrossRef
  title beside every DOI; no row without a resolving identifier; our papers copied from brief
  section 2; authors pasted from CrossRef; page log with verbatim excerpts; CrossRef metadata alone is
  `TITLE ONLY`; Section G may list as read only what the log shows fetched (the `RT38` failure); every
  negative lists its logged queries; no self-grades. Prompt-specific lines follow. Dependencies on
  other reports are cut (`T02` on wave 1, `T09` on `T01`/`T02`, `T17` on `T06`). `T09` carries the
  angle table with all eleven brief angles (`A1` to `A10` and `A14`), labels fixed. Round-1 reports
  and notes renamed `*_round1.md` (10 files); README status of the five = "written 2026-09-19, round
  2". Folder inventory now **136 entries**. Paste order, one fresh Gemini session each: brief,
  template, then `T02`, `T04`, `T08`, `T17`, `T09`. **At intake:** re-count the folder (136 + 5
  reports + 5 logs = 146), check no other file changed, then one fresh sonnet checker per report
  against its page log; verdict rule as for wave 6 round 2. Next: wait for the author's return.
* **Round 2 of the five returned, intake 2026-09-19.** All five reports and five page logs came back
  (reports written 14:32 to 14:41). Folder re-counted: **146 entries**; the only files changed in
  `5J_docs_occ` since the setup are the ten expected (`find -newer` on this prompt). The tool's
  helper `research_fetcher.py` and its per-job scripts sit outside the project, in its own scratch
  folder. Seen in the run transcript: several direct CrossRef, OpenAlex and Montreal open-data calls
  bypassed the logger (in `T04` and `T17`), so rows resting on them may have no log line; the tool's
  chat summary grades its own work ("verified"), which counts only if it is in a report. Five fresh
  sonnet checkers dispatched, one per report, on one shared spec (scratchpad `VET_SPEC_FIVE_R2.md`:
  the wave-6 spec plus a Section G read-list check, the `TITLE ONLY` rule, and a script audit of the
  tool's scratch folder). Each writes `VETTING_RT<NN>.md` with "VERDICT: pending (manager)". No
  number from the five reports is quoted anywhere until its note is read. Next: write five verdicts.
* **RT17 and RT09 round 2 vetted, 2026-09-19: both FAILED ROUND; do not re-run either as it stands.**
  The page logs themselves were honest this time (RT17 14 of 14 excerpts re-found, RT09 15 of 16) and
  no script wrote inside the project; the failures are in what the tool wrote after fetching.
  `RT17`: Section G calls two works read that the log shows only as CrossRef metadata (the prompt's
  own void rule); one arXiv ID resolves to an unrelated paper; 0 of 8 key numbers confirmed; Montreal
  row invented, Italy dropped. Kept: five identities, the Zhang et al. 2023 three-dataset abstract
  claim, the Toronto and England licences. `RT09`: headline quotes not on their pages, a Swiss row
  with no log line, table cells quoting the brief's own proposal wording as programme criteria, NSERC
  weighting contradicted, four deadlines unconfirmed, self-grades. Kept: Berkeley Climate Futures sits
  under the UC President's programme (deadline 1 November 2026); NSERC deadline 17 October and its
  distinct-from-thesis rule; MSCA 12-in-36-months mobility rule; Digital Futures context labels.
  `A7` and programme fit go to `T12` as pointers and kept facts only. RT02, RT04, RT08 checkers still
  running. Next: three more verdicts.
* **RT08 round 2 vetted, 2026-09-19: FAILED ROUND; do not re-run as it stands.** The mortality
  shares item 1.2 exists for are wrong against the documents the tool itself fetched (BC private
  residence 93 % for a true 73.0 %; "99 % no air conditioning" for a true 66.9 %; Chicago odds ratios
  2.2 and 0.2 for 6.7 and 0.3; Chicago "84 %" in no source); six rows read-claimed on CrossRef
  metadata only; four author lists wrong; twelve named items dropped. Kept, each re-found at source:
  BC 2021 (619 deaths) 98 % injured indoors, 67 % aged 70 or older, 56 % lived alone, 73.0 % in
  private residences, air conditioning 7.4 % present / 66.9 % absent / 24.1 % unknown; Semenza 1996
  odds ratios 6.7 and 0.3; pointers Multnomah 2021 (94 % died at home) and Ballester 2023. RT02 and
  RT04 checkers still running. Next: two more verdicts.
* **RT02 and RT04 round 2 vetted, 2026-09-19: both FAILED ROUND. D-5J-0 (a) is spent: all five
  re-runs failed; none is re-run again as it stands.** Pattern across all five: the page logs are
  honest and no script touched the project, but the report text then claims reads the log does not
  hold, invents quotes and figures, and mis-cites log lines. `RT02`: all 30 identifiers match
  CrossRef (a first), but 11 invented "future work" quotes, 24 of 33 read-list lines point at the
  wrong paper, ranking rows 31 to 33 do not exist. Kept: 30 identities; five rows with real
  abstracts and their figures; `A1` and `A10` prior work abstracts logged; three logged phrasings
  each found nothing for `A3` and `A7`. `RT04`: the Annex 79 book given an invented title against its
  own log line; ASHRAE database DOI with no log line; "Annex 87" where the log shows Annex 95; seven
  dataset rows unlogged. Kept: eleven identities, Aragon full text, Annex 79 four subtasks, Annex 95
  pointer, the heat-responsive-presence null from three logged queries. Lesson for `T12`: Gemini's
  fetching is now trustworthy and its writing is not, so `T12` must hand it the vetted facts as a
  pasted table (as `T38` did) and ask only for logged checks against them, never free prose about
  papers. Next: compile the kept facts, then write `T12`.
* **`T12` written, 2026-09-19** (the author said "go ahead, write"). `T12_contradictions_and_ranking.md`
  carries a pasted table of 40 checked facts (`P1` to `P40`, each naming the vetting note that holds
  it; compiled verbatim by a sonnet agent into scratchpad `T12_inputs_kept_facts.md`, then selected
  by the manager). Design, from the five round-2 failures: no free landscape; every factual sentence
  ends with a tag (`[Pn]`, `[Ln]` log line, `[BRIEF s.n]`, `[INFERENCE]`); the log is finished before
  the report is written; more than five tags that do not support their sentence void the report.
  Part A has eleven questions (pyepwmorph; Annex 79 and 95; the Canadian winter-outage competitor;
  `A9` rows against CrossRef; occupancy in survivability studies; heat exposure with time-use
  presence; records reading with abstention; demographic occupancy in scenarios; `A11` zoning figures;
  ecobee terms; BuildOcc). Three contradictions settled by the manager and not reopened: Berkeley
  runs through the UC President's programme, NSERC keeps the distinctness rule, `A2` is the brief's
  definition. Part B ranks eleven angles (`A2`, `A3` narrowed, `A4`, `A6`, `A7`, `A8`, `A9`, `A11`,
  `A12`, `A13`, `A14`) under the round-1 `RT02` E1 rule (S = 0.40 G + 0.30 F + 0.20 D + 0.10 P) with
  fixed levels, an `[INFERENCE]`-only score taking the lower level, two sensitivity checks and the
  flattering-direction check on `A9`. README wave 4 line and T12 row updated. Folder now 152 entries
  (146 + five vetting notes + `T12`); expect 154 at intake (`RT12` report and log). **At intake:**
  re-count, then one fresh sonnet checker on the wave-6 spec plus a tag audit (every `[Ln]` against
  its log line, every `[Pn]` against the table, untagged factual sentences counted). Next: author runs
  `T12`.

## Reply shape, every time

```
• <one sentence: what happened>

  - <fact>
  - <fact>
  - <fact>

  Evidence: <path>, <path>.

  Next: <three or four words>
```
* 2026-09-19, one-paste T12: at the author's request, `DeepResearch/T12_RUN_ALL_IN_ONE.md` joins `00_MASTER_BRIEF.md`, `_RESPONSE_TEMPLATE.md` and `T12_contradictions_and_ranking.md` verbatim (checked by string match) under a short header saying the paste is done and "three files" means these three parts. If a source file changes, rebuild it from the scratchpad script `build_t12_one.py`. Folder count is now 153; expect 155 when `RT12` and its log return. Intake plan unchanged.
* 2026-09-19, RT12 intake: the author ran the one-paste file. `RT12_contradictions_and_ranking.md` (169 lines, written 16:47) and `RT12_pages.log` (53 lines, written 16:45) are in; folder count 155 as expected. Red flags for the verdict: the log was built afterwards by `build_log.py`, after all fetching; the report text came from `generate_report.py`; and about 25 built-in web searches, 3 page reads, several `curl.exe` calls and inline `py -3 -c` calls ran outside any logger (tool scratch `C:\Users\o_iseri\.gemini\antigravity\brain\806a80e8-a13d-4eaf-9820-e51dbfce3c9e\scratch\`). One fresh sonnet checker was dispatched on `scratchpad\VET_SPEC_FIVE_R2.md` plus a tag audit, a scoring audit and a Q-verdict check; it writes `VETTING_RT12.md` with "VERDICT: pending (manager)". The author is away for the weekend and asked the manager to finish the process: write the verdict, update README, this prompt and memory, then write `DECISION_5J_angle.md` ending "Waiting on you: D-5J-1" with a recommendation. Nothing is stated to the author until the note is vetted.
  Resume note: the author closed the session while the checker was running. Next session: if `DeepResearch/VETTING_RT12.md` is missing or unfinished, re-dispatch one fresh sonnet checker with the same task (spec `VET_SPEC_FIVE_R2.md` plus checks 15 tag audit, 16 scoring audit, 17 Q verdicts), then write the verdict.
* **2026-09-19, D-5J-1 ruled (a) by the author. Start here.** A9 is the 5J subject; A12 is written in
  parallel as a short companion paper from 4J assets. Ruling recorded in `DeepResearch/DECISION_5J_angle.md`
  under "Ruling". Owed before any plan document is opened: obtain Hobson and Brideau 2026 ("Exploring
  Key Performance Indicators for Thermal Resilience in Canadian Multi-Unit Residential Buildings",
  `10.63044/w26hob04`) from ASHRAE and check whether it couples occupancy to winter outage performance
  in Canadian multi-unit buildings. This is the author's own action (library/ASHRAE access), not a
  literature search the manager may perform. If the paper shows that coupling, this ruling reopens in
  favour of A2. Next: author brings back the paper or its abstract; only then does a 5J plan document
  open.
* **2026-09-19, Hobson and Brideau 2026 read; A9 confirmed open.** The paper is a summer heatwave/
  extreme-heat study (mechanically cooled midrise apartment, three cities, TMY + heatwave-year outage
  runs); it never touches winter outages. Occupancy is NECB 2020's single fixed schedule, unchanged
  even during the outage run, never dynamic or demographic. Neither of the two things that would have
  damaged A9's openness claim is present. Ruling D-5J-1 (a) stands, not reopened. Its PDF footer says
  its content may not be used with AI/ML tools — flagged for the author, only a factual scope check
  was taken from it. Next: open the 5J plan document for A9 (+ A12 companion).
* **2026-09-19, short kickoff note written; this subject-selection series is done. Start here.** The
  author asked for a short note only, not a full plan (no methodology is scoped yet), and said they
  will return later to look at the ideas document themselves. `5J_docs_occ/5thJ_00_Kickoff_Note.md`
  records the settled subject (A9 + A12 companion), why, the cleared Hobson-and-Brideau condition, and
  what is still open (BEM archetype, weather-morphing tool, dynamic occupancy method, KPIs, A12's own
  untested openness, no programme-fit table). **This manager prompt's job — vet reports, keep state on
  disk, prepare the author's decision — is complete; D-5J-1 was the last decision it owed.** If the
  author returns to build an actual 5J methodology/plan, that is new work outside this prompt's scope
  and should start from the kickoff note, not from re-reading this file's full history.
* **2026-09-19, RT12 closed and the decision written.** Verdict `ACCEPTED WITH STRIKES` in `DeepResearch/VETTING_RT12.md`: the first report of the series whose identifiers (14 of 14), quotations (6 of 6) and scores (11 of 11 rows) all hold under an independent re-check, so it is not a failed round. Six strikes, read them before quoting any RT12 row. S1: Hobson and Brideau 2026 (`10.63044/w26hob04`) is struck to TITLE ONLY, its "read abstract" content has no source, and **it is the nearest neighbour of A9 with its scope unknown to us** - the one thing owed before A9 is committed to. S2: the Baba 2022 sentence is struck everywhere (log line 12 is an unrelated philosophy project); Q3's NOT FOUND survives on its re-run queries alone. S3: A4 and A6 re-scored `G = 40` to `G = 20` by T12's own rule, so A4 24.0 to 16.0 and A6 24.5 to 16.5, and Section A's "second tier" is A2 and A7 only. S4 (manager-found, not in the mechanical check): A12's `G = 40` cites only `P27`, a fact we pasted in ourselves, and no Part A question ever searched for an existing privacy protocol, so its first-equal rank is not evidence of an open space. S5: the A9/A12 tie at 27.0 has no tie-break rule and the printed Rank 1 / Rank 2 is struck. S6: the log is post-hoc (`build_log.py` fetched a hard-coded list after all real research; `generate_report.py` holds the whole report as one string literal), so RT12 rows are verified-by-our-checker, never verified-by-the-tool. Do not re-run T12. README T12 row set to vetted. `DeepResearch/DECISION_5J_angle.md` is written and ends "Waiting on you: D-5J-1, recommend (a)" - A9 as the subject with A12 as a short companion protocol paper, conditional on the Hobson and Brideau abstract. It records that `RT09` failed both rounds so **no angle-by-programme fit exists anywhere in this series**; only the UC 1 November and NSERC 17 October deadlines and the NSERC thesis-distinctness rule survive (`P36`, `P37`). Next: nothing owed to an agent. When the author rules D-5J-1, option (a) starts by obtaining Hobson and Brideau 2026 from ASHRAE, and only then is a `5J_docs_occ` plan document opened.

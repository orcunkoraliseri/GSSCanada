# 4J — MANAGER RESUME PROMPT

### Hand this to the next session as its first message. Fixed path, edited in place, never duplicated.
#### Last updated: 2026-08-14, after `RL19` was vetted.

---

## YOUR ROLE

You are the **manager** on paper 4 (4J). You plan, you vet, you write specifications and employee
prompts. **You do not implement.** Nothing in this project has been built yet, so there is currently
no employee work to supervise — the next moves are acquisition and decisions, not code.

Read `../4thJ_00_HETUS_LLM_Pipeline.md` before doing anything else. It is 1,800 lines and it is the
only authority. `../4thJ_00_HETUS_LLM_Pipeline_Overview.md` is the map; the step folders
`../Step0_docs/` to `../Step9_docs/` are the working specifications.

---

## THE PAPER, IN FIVE LINES

Fine-tune **one open-weight LLM** on HETUS-harmonised time-use diary microdata so that it generates
activity-resolved occupant schedules for **any** country in the framework, and test that claim by
**holding one country out of training entirely**. Output drives EnergyPlus residential archetypes.

It exists because paper 1 (CENTUS, *Energy and Buildings* 357, 117155) **claimed HETUS
standardisation as the route to cross-national transfer and never tested it.** That untested sentence
is this paper.

---

## 🔴 STATE: NOTHING IS BUILT

Not a caveat, an orientation. **No file has been downloaded.** Every document in this folder tree is a
specification. Anything written as a threshold, a gate or a count is **pre-registered**, not measured.
The only things actually measured so far are the tokenizer comparison and the licence sweep, both run
on Speed on 2026-08-14 (jobs 1234211, 1234216, 1234219, `../tools/`).

---

## DECISIONS THAT ARE CLOSED — DO NOT REOPEN THEM

| # | Decision | Where |
|---|---|---|
| — | **The trained model will never be released.** Weights and adapters both. The releasable artefact is the synthetic diary corpus (CC BY 4.0) plus code (Apache 2.0) | `RL10` |
| — | **No forecast, no temporal claim, anywhere** | Author |
| 5 | **HETUS only. No Canada, no United States** | Author, 2026-08-14 |
| 6 | **Four countries, one wave each:** Italy 2013-14, Spain 2009-10, UK 2014-15, France 2009-10 | Author, 2026-08-14 |
| 3 | **Backbone: OLMo 3 7B.** Leg-4 is the 1B pilot (correctness only), Leg-5 is the reported model | Our own tokenizer measurement, which overruled `RL18` |
| — | **`ACT` keeps 3 digits.** All four waves share one coding generation, so nothing forces 2-digit pooling | 1A-bis |

🔴 **Decision 6 is a decision about newer waves as much as older ones.** UK 2020-21, Italy 2022-23,
Spain 2024-25 and France 2024-25 are all out, and **Eurostat will not release the HETUS 2020 round
before 2027**. There is no newer obtainable corpus. See 1B-bis.

---

## NEXT ACTIONS, IN ORDER

**1. File the Eurostat entity-recognition enquiry with Concordia's Office of Research.**
It was second on the list until `RL19` came back. It is now **first**, because `RL19` established that
national routes cannot widen the corpus: of 14 candidate countries, none is Tier 0 or 1, two need the
same institutional accreditation Eurostat does, and two are secure-enclave only. **Track A is not the
slow path to more countries; it is the only one.** With four countries, leave-one-country-out trains on
three, which is limitation C4. Send the enquiry, record the date. *"A report says Concordia is not
recognised"* is already known and is not the same as having asked.

**2. Download Spain first.** INE is the only zero-credential source in the entire HETUS 2010 round.
Then UK (UKDS SN 8128), then France (Progedo/ADISP). Italy is **already held from paper 1** — confirm
the held copy is the same wave and the same extract before assuming it. Work item 1.1 in
`../Step1_docs/4thJ_01_corpusAcquisition.md`. **Record each md5 at download time, not later.**

**3. Write the shape-agnostic reader** (work item 1.3). It must itemise everything it cannot parse and
fail on it. A reader that returns `0.0` or silently drops an unparsed row blames the pipeline for its
own gap; that cost 16 spurious FAILs in 3J.

**4. Close open decision 13** — what replaces the ATUS zero-credential reproduction path, now that
decision 5 removed it. Candidate: a minimal public path on **Spain alone**. It cannot demonstrate
transfer, but a reader could execute every stage. This must close before the Data Availability
statement can be written.

**5. Close open decision 14** — the day-to-year chaining rule. Surveys give one or two diary days;
EnergyPlus needs 8,760 hours. `RL17` proposes 100 households × 3 chaining rules compared on annual
peak power. **If peak moves more than about 25 % between rules, the chaining convention dominates the
BEM result and we are measuring our own bookkeeping**, not the transfer. Nothing in Steps 7 to 9
currently specifies it.

**6. Close open decision 15 — Norway as a fifth country.** Opened by the author on 2026-08-14. `RL19`
recommended acquiring it; we did not accept, because the SSB file uses a ~170-code national list
rather than ACL 2008, and hand-building a 3-digit crosswalk is precisely the arbitrary mapping
`RL17` B3 says cannot be defended.

🔴 **Establish the fact before weighing the benefit.** The fact: **does the Sikt delivery ship an
official Eurostat/ACL recode variable produced by SSB?** If yes, Norway is admissible and worth taking
— it is the only reachable Nordic candidate, a genuinely hard held-out target rather than a fifth
neighbour, and it repairs limitation C4 by letting leave-one-country-out train on four. If no, it is
rejected for the same reason as UK 2000-01.

**Why the order matters.** The benefit is large enough to make a hand-built crosswalk look acceptable,
and that is how decision 6 gets reversed without anyone deciding to reverse it. **Decision 15 is a
corpus decision wearing the clothes of an acquisition detail.** Must close before Step 1 acquisition
finishes.

**7. Before Step 7 is sized: run the vLLM throughput comparison** on Leg-5 checkpoints. OLMo 3 7B has
**no grouped-query attention** — 32 KV heads over 32 layers gives about **512 KB per token** against
Qwen2.5-7B's 56 KB, roughly 9× and about 6× after our token saving. **That figure is arithmetic from
the config, not a benchmark**, and it must not be quoted as one.

---

## HOW THIS PROJECT WORKS — THE RULES THAT ARE NOT NEGOTIABLE

* 🔴 **Speed cluster: `sbatch` only.** Never a blocking `srun`, never bare python on the login node,
  not even a one-liner. Every job requests `-t 7-00:00:00`. Flagged three times; a fourth is account
  suspension.
* 🔴 **Deep research is external.** You never search literature or verify citations as the deliverable.
  You write the prompt file; the author runs it. Prompts and reports live in `../DeepResearchPrompts/`
  as `L<NN>` and `RL<NN>`.
* 🔴 **You never create images.** You write the prompt under
  `../writing/submission/figures/Prompts_Images/`; the author generates the figure.
* 🔴 **You never create anything that was not asked for.** If you think something is needed, ask in one
  sentence first.
* **Replies are short, plain English, one thing at a time**, even when the author writes French.
* **Progress Logs are append-only.** Never delete, reorder or reformat an existing entry.
* Never count lines with PowerShell — use `wc -l`. Verify a backup is non-empty before truncating.

---

## 🔴 HOW TO READ A RETURNED DEEP-RESEARCH REPORT

Three rounds have come back. **Every one contained content that was fabricated exactly where it
claimed to be verified**, and every one was caught by cheap offline checking. Before a single value
enters a document:

1. **Check what it says about our own work first.** It cannot see our results or our cluster. Anything
   it reports about them was quoted from the prompt or invented.
2. **A report that agrees with what you supplied has told you nothing.** `RL19`'s Part B returned the
   HETUS guidelines restated per country as though ten codebooks had been read.
3. **Make it obey an identity it cannot fake.** A DOI resolves or it does not. A licence clause exists
   or it does not. `RL19`'s Netherlands entry died the moment the DANS record was opened: restricted,
   unrequestable, superseded — against a claim of "opened in full, guess count 0".
4. **Read the negative controls as evidence, not as reassurance.** `RL19` defined "convenient" as all
   seven properties at once, so nothing could score, then reported zero. **A control that cannot fire
   is not a control** — the same vacuity we screen our own gates for.
5. **Every recommendation in the rescuing direction is a signal.** If a report concludes the data is
   obtainable, the licence permissive, the method right and the compute sufficient, treat the round as
   failed and re-run it.
6. **Salvage the route, not the table.** `RL19`'s value was a negative result plus the observation that
   no national archive ships the Eurostat-harmonised file — neither of which was its recommendation.

The full record is V1 to V11 in the plan document. **Read V6 and V11 before commissioning another
round**; they are what a failed round looks like from the inside.

---

## GATE DESIGN, IF YOU TOUCH ANY VALIDATION DOCUMENT

Read `feedback_gates_must_be_seen_failing.md` in memory first — 46 failure classes, all from real 3J
work. The three that cost the most:

* **Every gate must be seen failing.** A perturbation table where each perturbation breaks exactly one
  gate, plus a **coverage clause** that fails the probe if a passing gate was never made to fall.
* **A gate whose reference derives from the source it audits cannot fail.** At least one check per step
  must arrive through a path the defect cannot reach.
* **A check that cannot distinguish "found nothing" from "could not run" is not a check.** Print
  `NOT CHECKED`, never a pass.

Step 7's G7.1 to G7.4 are labelled **enforcement confirmations**, not gates: they cannot fall while the
grammar mask is on, and counting them in a seen-failing tally would inflate it.

---

## WHERE THINGS ARE

| Path | What |
|---|---|
| `../4thJ_00_HETUS_LLM_Pipeline.md` | The authority. Decisions, vetting record V1-V11, all ten steps, limitations, progress log |
| `../4thJ_00_HETUS_LLM_Pipeline_Overview.md` | One-screen map, ASCII step boxes, open-decision count |
| `../Step0_docs/` … `../Step9_docs/` | Per-step implementation + validation specifications, and `outputs_stepN/` |
| `../DeepResearchPrompts/` | `L01`-`L19` prompts, `RL01`-`RL19` reports, master brief, README with the vetting checklist |
| `../tools/` | The three Speed scripts that produced our own measurements |
| `../writing/submission/figures/` | The graphical abstract PNG and its prompt |

🔴 **The master brief in `DeepResearchPrompts/` is stale** — it still says five countries, multi-wave
and Canada. `L19` carries a corrections block at the top that overrides it. **Any new prompt needs the
same block** until the brief is reissued.

---

## OPEN DECISIONS

**9 of 15 fully closed.** The live ones are **13** (the reproduction path that replaces ATUS), **14**
(the day-to-year chaining rule) and **15** (Norway as a fifth country). All three block downstream
steps and all three are the author's call.

Also still open and older than these: **11**, which country is held out — it must close **before the
first training run**, because a held-out country chosen after results have been seen is not held out,
and nothing later repairs that.

---

## FIRST THING TO SAY IN THE NEXT SESSION

Ask the author which of the next actions they want to start, and say in one sentence that nothing is
built yet. **Do not begin acquisition, do not write code, and do not commission another research round
without being asked.**

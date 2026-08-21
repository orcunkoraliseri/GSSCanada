# L-series deep research prompts (4J: HETUS + open-weight LLM)

Prompts for **external** deep research (Gemini Antigravity). Written in-repo, run outside it. The
returned reports come back into **this same directory**, beside the prompt that produced them.

Same convention as `3J_docs_occ_nTemp/deepResearch_Resources/`, with the prefix changed from `V` to `L`
so the two series never collide in a search.

## How to run one

1. Paste `00_MASTER_BRIEF.md` into the external tool.
2. Paste the `L<NN>_*.md` prompt after it.
3. The tool answers using the schema in `_RESPONSE_TEMPLATE.md` (Sections A to H).
4. Save the answer here as `RL<NN>_<topic>.md`.

**One prompt per session.** Do not paste two together: the master brief tells the assistant to answer
only what follows it, and the response template is per prompt.

## Run order

The series is not a flat list. `L01` gates everything and `L03` can end the project.

```
  WAVE 0 -- run alone, first, and read the answer before spending anything else
    L01  HETUS microdata access .......... can we get the data at all
    L03  prior art ...................... has someone already done this

  WAVE 1 -- feasibility, run once L01 and L03 come back clean
    L04  open-weight model selection ..... which model, which licence
    L06  alternatives to fine-tuning ..... is an LLM even right
    L10  privacy, disclosure, release .... may we publish the model

  WAVE 2 -- design, run once the method is chosen
    L02  HETUS structure and coding ...... the alphabet the model speaks
    L05  fine-tuning method .............. the recipe
    L07  serialisation and tokenisation .. the single biggest engineering call
    L08  evaluation and gates ............ the pre-registration table
    L12  constrained decoding ............ guaranteed well-formed output

  WAVE 3 -- build and scale
    L09  weights and representativeness .. sample to population
    L11  Speed HPC engineering ........... how to actually run it
    L16  longitudinal axis ............... can we keep the time story

  WAVE 4 -- the paper
    L13  European archetypes and BEM ..... the building-science anchor
    L14  venue, positioning, novelty ..... where it goes and what it claims
    L15  reproducibility and release ..... what ships with it

  WAVE 5 -- ADJUDICATION (run after RL01-RL16 are back and vetted)
    L17  contradictions + multi-wave ..... settle the disputes, inventory the waves

  WAVE 6 -- CLOSING A DECISION (run after RL17)
    L18  model family, final ............ re-ask L04 under the constraints L04 did not have
    L19  corpus expansion, national ..... can we widen past four countries without Eurostat

  WAVE 7 -- ONE QUESTION EACH (run 2026-08-14, both returned)
    L20  Norway admissibility ........... does the Sikt file carry an SSB-made ACL variable
    L21  day-to-year chaining ........... has anyone measured what the chaining rule costs

  WAVE 8 -- THE TWO NEWER WAVES (written 2026-08-14, not yet run)
    L22  UK 2020-21 admissibility ....... what file exists, and is it the 2014-15 coding list
    L23  Italy 2022-23 admissibility .... is it released, and can ACL 2020 meet ACL 2008

  WAVE 9 -- DOWNSTREAM UNBLOCKING (written 2026-08-20, both RETURNED and VETTED)
    L24  marginals + archetype sources .. what can we actually open, for ES/UK/IT
    L25  activity to appliance mapping .. what do CREST/Widen/LPG/RAMP publish as TABLES

  WAVE 10 -- FOLLOW-THROUGH (written 2026-08-20, not yet run)
    L26  ES and IT census marginals ..... the UK is BUILT; these two are not, and the UK is the calibration target
```

## Wave 5 is a different kind of prompt

`L01` to `L16` are **exploratory**: each asks an open question. `L17` is **adjudicative**: it takes the
eight places where the sixteen returned reports contradict each other, plus the claims none of them
checked, and asks for a verdict on each.

It is written around one instruction: **do not split the difference.** When two reports disagree, the
likely situation is that one is wrong, not that both are partly right. A synthesis is the least useful
answer and usually means neither claim was checked. `NOT FOUND` is an explicitly successful outcome
here, because it redirects us to ask the data provider rather than trust a report.

`L17` also carries **Part B**, the multi-wave inventory for the five chosen countries, which is new
design work rather than adjudication. It sits in the same prompt because it is the same kind of
question: narrow, factual, and settled by opening a document.

## The prompts

| # | File | Question | What it unblocks | Can it stop the project? |
|---|---|---|---|---|
| **L01** | `L01_hetus_microdata_access.md` | Can a Canadian-based postdoc obtain HETUS diary-level microdata, and if not what corpus do we build instead | Everything. The corpus decision | **Yes** |
| **L02** | `L02_hetus_structure_and_coding.md` | Activity coding list, location codes, co-presence codes, file structure, where countries diverge | Serialisation, validity constraints, preprocessing | No |
| **L03** | `L03_prior_art_llm_for_timeuse.md` | Has anyone already fine-tuned an LLM on time-use or occupancy data | The novelty claim | **Yes** |
| **L04** | `L04_open_weight_model_selection.md` | Which open-weight model actually exists, at what size, under what licence | Model choice and the release plan | Licence could |
| **L05** | `L05_finetuning_method.md` | Continued pretraining vs SFT, full vs LoRA, the recipe, the beginner failure modes | The training design | No |
| **L06** | `L06_alternatives_to_finetuning.md` | Eight candidate methods ranked on six criteria. Is the LLM the right instrument | The method decision | **Yes** |
| **L07** | `L07_serialisation_and_tokenisation.md` | How to turn a 144-slot diary plus 25 attributes into tokens without wrecking the token budget | Everything downstream of the data | No |
| **L08** | `L08_evaluation_and_gates.md` | The metrics that detect distributional collapse, and the pre-registered gate table | The whole validation layer | No |
| **L09** | `L09_survey_weights_and_representativeness.md` | Complex survey weights in training; generating a place-specific population | The UBEM-scale claim | No |
| **L10** | `L10_privacy_disclosure_and_release.md` | Does a model trained on microdata leak it, and may we publish the weights | The release plan and the ethics section | **Yes**, for release |
| **L11** | `L11_speed_hpc_engineering.md` | SLURM, containers, offline weights, surviving the seven-day walltime | Execution | No |
| **L12** | `L12_constrained_decoding_and_validity.md` | Guaranteed well-formed diaries, and what constraining costs the distribution | Generation at scale | No |
| **L13** | `L13_european_archetypes_and_bem_coupling.md` | TABULA, EN 16798-1 schedules, activity-to-load mappings, EnergyPlus injection | The building-science half of the paper | No |
| **L14** | `L14_venue_positioning_and_novelty.md` | Venue, novelty matrix, the objections and their answers | Framing and submission | No |
| **L15** | `L15_reproducibility_and_artefact_release.md` | Model cards, hosting, licences, reproducibility with restricted data | What ships | No |
| **L16** | `L16_longitudinal_and_forecasting_axis.md` | Can the 2005 to 2030 story survive with only two or three HETUS waves | Whether paper 4 keeps the series' signature | Narrows scope |
| **L17** | `L17_contradiction_adjudication_and_multiwave.md` | Which side of each of the 8 inter-report contradictions is right, and what waves exist for the 5 chosen countries | The parser, the model choice, the corpus depth | No, but it can invalidate earlier answers |
| **L18** | `L18_model_family_final_selection.md` | Which model family, now that we cannot release weights, do release the output under CC BY 4.0, and have a full A100 80 GB | Closes open decision 3 | Licence could, for the dataset |
| **L19** | `L19_corpus_expansion_national_routes.md` | Which other HETUS 2010-round countries are obtainable through a **national** route, and admissible unchanged (10-minute slots, 3-digit ACL 2008/2010, paper diary) | Limitation C4: leave-one-country-out currently trains on three | No. The four-country corpus stands whatever it returns |
| **L20** | `L20_norway_admissibility.md` | One question: does the Norwegian file delivered by Sikt carry an **ACL-coded activity variable produced by SSB**, or only SSB's national list | Closes open decision 15 | No. A short negative was the expected and actual outcome |
| **L21** | `L21_day_to_year_chaining.md` | How the literature turns 1-2 diary days into 8,760 hours, and above all whether anyone has ever **measured** the difference between chaining rules on the same building | Open decision 14, and the Step 7 to Step 9 chain | No, but a `zero` answer forces an experiment — and that is what it returned |
| **L22** | `L22_uk_2020_21_admissibility.md` | What file the UK 2020-21 time-use collection actually deposited, whether it uses the UKTUS 2014-15 coding list, and whether **mode and fieldwork date are variables** in it | Nothing on the critical path. It decides only whether the file is worth obtaining now for a **later, optional** held-out instrument check | **No.** Neither wave can enter training, by author decision |
| **L23** | `L23_italy_2022_23_admissibility.md` | Whether the Italian 2022-23 microdata is released at all, and whether an **official** correspondence exists between its coding list and ACL 2008/2010 | Same. Plus it settles whether a newer Italian wave can ever be compared to our 2013-14 wave without a crosswalk we built | **No**, same reason |
| **L24** | `L24_marginals_and_archetype_sources.md` | Which published sources can we actually reach, open and use, for (a) census marginals on age / sex / household type / economic status and (b) TABULA residential archetype parameters, for ES, UK and IT | 🔴 **Critical path of the HEADLINE CLAIM.** `G6.1`'s raked-donor null rakes onto the held-out country's PUBLISHED marginals, and `outputs_step5/` is empty, so the bar cannot be computed until Step 5.1 exists. Also unblocks Step 8.1, the longest-lead downstream item | **No** |
| **L25** | `L25_activity_to_appliance_mapping.md` | What CREST, Widen, LoadProfileGenerator and RAMP actually publish as activity-to-appliance TABLES: resolution, trigger form, rated powers, cycle durations, validation scale, licence | Step 9 cannot start without it. `G9.1` FAILs any row citing only a paper rather than a table or figure; `G9.2` FAILs any `VALIDATED` label with no scale. Also settles `G9.11`, whether the mapping needs our 3-digit codes at all | **No** |
| **L26** | `L26_es_it_census_marginals.md` | For **Spain and Italy only**: which 2011 census tables actually deliver age, sex, household composition and economic status, at what published category boundaries, reachable at what URL | 🔴 **The remaining two thirds of Step 5.1**, which is on the critical path of the headline claim. The UK was built directly from Nomis on 2026-08-20; the ES and IT census systems did not respond to the same treatment (INE `wstempus` does not list the 2011 census; the ISTAT census SDMX host returns HTTP 302) | **No** |


**Wave 10 — the follow-through round (`L26`), written 2026-08-20 after `RL24` and `RL25` were vetted.**
Different in kind from every earlier prompt: it is written **after** part of its own question was
answered by doing the work. The United Kingdom marginals were built directly from Nomis the same day,
so `L26` asks only about Spain and Italy, and it carries the **finished UK numbers as a calibration
target**. 🔴 **"Did you reproduce our UK figures" is its third mandatory negative control**, on the
reasoning that a report which cannot reproduce a value we have already verified against a downloaded
file should not be believed on the two countries we could not reach. It also states, at the top, that
the route and basis decisions are **closed**, and makes "did you recommend Eurostat or an annual series
anyway" a negative control of its own — the first prompt in the series to guard a ruling rather than
ask for one.

**Wave 9 — the two downstream-unblocking rounds (`L24`, `L25`), written 2026-08-20, not yet run.**
Different in kind from waves 7 and 8: those asked what the literature knows, these ask **what can
actually be opened**. Both were written after a session in which a landing page returning HTTP 200 was
mistaken for reachable data, so both make **"list every URL you actually opened, separated from URLs
you named but did not open"** the first mandatory negative control, and both forbid reconstructing a
paywalled table. 🔴 **`L24` expects three awkward answers and says so in advance**: that no census year
matches any of our diary waves, that our age floor of 11 will not match published bands, and that the
United Kingdom may not appear in Eurostat census data at all. Each is named as a question to answer
plainly rather than smooth over. 🔴 **`L25` carries the Widen conflation** (`Applied Energy` 87(6):
1880-1892 for the 2010 paper, `Energy and Buildings` 41(10): 1001-1012 for the different 2009 Widen lighting (🔴 CORRECTED 2026-08-20, FINDING 47: the 41(7):780-788 in the original L25 text was wrong)
paper) and asks the assistant to verify our own correction rather than accept it.

**Wave 8 — the two newer waves (`L22`, `L23`), written 2026-08-14, not yet run.** 🔴 **Both prompts
forbid the recommendation that would otherwise be their natural conclusion.** Adding either wave to
training is a closed author decision, so each prompt states the ban, states the reasons, and makes
"did you recommend it anyway" a mandatory negative control. What they are actually for is narrower and
optional: obtaining a file now that could later serve as a **held-out instrument**, never as a fifth
or sixth training wave. Both are written so that "not released" or "a reduced activity list" is a
complete and successful answer.

**Wave 7 — the single-question rounds (`L20`, `L21`), run 2026-08-14.** Both were written to close one
decision each and both were told, in their own text, what a negative answer would look like. 🔴 **That
is deliberate and it has a cost: a report that returns the answer the prompt said it expected must be
believed on its checkable details, not on its conclusion.** `RL20`'s verdict is accepted because 167
categories, `akt1` to `akt144` and Notater 2012/03 are falsifiable; `RL21`'s zero is accepted for the
same reason its percentages are not.

🔴 **`L19` to `L23` each carry a corrections block at the top that overrides the master brief** on four points
(HETUS only, one wave per country, the four chosen waves, no forecast). The brief predates author
decisions 5 and 6 and would otherwise steer the report to the wrong question. **Any prompt written
after 2026-08-14 needs the same block** until the brief itself is reissued.

## Vetting a returned report, BEFORE any value enters a document

This project has run ten rounds of external deep research on the previous paper. **Every early round
contained fabricated or laundered content, and every one was caught by cheap offline checking.** Run
these before reading a single value into a plan.

1. **Check its claims about our own work first.** The tool cannot see our results or our cluster.
   Anything it says about them is either quoted from the prompt or invented.
2. **A report that agrees with something you supplied has told you nothing.** The diagnostic value is
   entirely in what we did not supply.
3. **Check metadata columns, not only value columns.** A copied table gives itself away in its
   provenance long before its numbers look wrong.
4. **Make it obey an identity it cannot fake.** Shares sum to 100. A licence clause number exists or it
   does not. A model repository resolves or it 404s. A DOI returns a title or it does not.
5. **Version and date rot is the failure mode of this series specifically.** Unlike the 3J rounds,
   which asked about standards that do not move, most of these prompts ask about software, models and
   licences that change monthly. **Re-check anything older than about three months before relying on
   it**, and never quote a version number without the date it was checked.
6. **Expect the answer to inherit the prompt's framing.** If a prompt leads with the author's preferred
   method, the report will tend to endorse it. `L06` is deliberately built to counter this and is the
   one to trust least if it agrees with us enthusiastically.
7. **Every recommendation moving in the rescuing direction is a signal, not a coincidence.** If a report
   concludes that the data is obtainable, the licence is permissive, the method is right and the
   compute is sufficient, treat it as a failed round and re-run it with the negative controls tightened.

**When a round fails, salvage the route, not the table.** A walkable retrieval path we can execute
ourselves is worth more than sixty rows we have to falsify.

## Rules that hold for every prompt in this series

* A citation is not evidence until opened.
* Verify DOIs through CrossRef and report the title the API returned.
* `NOT FOUND` beats an invented answer, always.
* Never recommend the option that happens to rescue us.
* Every version, price, size, licence term or quantity carries the date it was checked.
* No em dashes and no en dashes in the returned text.

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

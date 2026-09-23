# Deep-Research Prompt L35: the literature around one journal paper, and its closest competitor

> SCOPE GUARD, READ FIRST. This is a **literature search** for one manuscript being prepared for
> *Energy and Buildings*. We need (a) the published works a reviewer will expect to see cited, grouped
> by theme, and (b) the single closest published competitor to our study, so that we can state in one
> paragraph how we differ from it. Your job is to find and verify sources, and to try to BREAK our
> novelty claim. Do not evaluate our results, do not suggest new methods, do not rewrite our text.
> If a source cannot be confirmed, write NOT FOUND. An honest NOT FOUND is better than a guessed reference.

> Run in Gemini Antigravity with live web search. Save the return as
> `RL35_literature_and_competitors.md` in this folder (`4J_docs_occ/DeepResearchPrompts/`).

---

## Context (for you, not to be cited)

The paper asks whether a large language model, fine-tuned on time-use diaries from some countries, can
write realistic daily time-use diaries for a country whose diaries it has never seen, when it is given
only that country's published demographic tables. The answer is tested with a leave-one-country-out
design on three European time-use surveys (Spain 2009-10, Italy 2013-14, United Kingdom 2014-15, all
in the Harmonised European Time Use Survey family). The comparison that decides the question is a
**raked donor pool**: real diaries from the other countries, reweighted by iterative proportional fitting
onto the held-out country's published margins. The decision rule was fixed before training. The model
(an open-weight 7-billion-parameter decoder, fine-tuned with low-rank adapters) does NOT beat the raked
donor pool in any of nine country-by-age cells; its error is 1.1 to 3.9 times the pool's. A first-order
Markov chain is also compared. Downstream, the generated diaries drive an appliance-electricity and
hot-water model and residential archetype simulations (TABULA archetypes, EnergyPlus).

References ALREADY in the paper (you may recommend them if they fit; say "already cited"; do not list them
as new): Richardson, Thomson and Infield (2008); Richardson et al. (2010); Widen and Wackelgard (2010);
Osman and Ouf (2021); Vosoughkhosravi, Jafari and Zhu (2023); Iseri, Gursel Dino and Kalkan (2026);
Deville and Sarndal (1992); Lovelace et al. (2015); Beckman, Baggerly and McKay (1996); Hu et al. (2022,
LoRA); Shokri et al. (2017); Lombardi et al. (2019, RAMP); Pflugradt (LoadProfileGenerator); Jordan and
Vajen (2001); Fuentes, Arce and Salom (2018); Loga et al. (2012, 2016, TABULA); Crawley et al. (2001,
EnergyPlus); Eurostat HETUS 2008 and 2018 Guidelines; the three national survey documents.

What an earlier search already returned, so you do not repeat it: no published like-for-like comparison of
a fine-tuned or prompted language model against a demographically raked real-donor pool on an unseen
population was found. Please test that claim again from new angles rather than restating it.

---

## What we need

**Part 1. The closest competitor (most important).**
Find the published work (journal, conference or preprint with a DOI or arXiv ID) that comes CLOSEST to
our study on these five features: (i) a generative model (language model, transformer, diffusion, GAN,
VAE) produces synthetic individual days, activity sequences, occupancy schedules or synthetic population
records; (ii) it is evaluated on a population, region or country NOT in its training data; (iii) it is
compared with a reweighting, raking, IPF or other survey-calibration baseline; (iv) the decision rule is
fixed in advance; (v) the output feeds a building or urban energy model. For the top three candidates,
give a table: which of the five features each has, with the page or section where you saw it. Then name
the single closest and say in two sentences how it differs from our design. If nothing has more than two
features, say so.

**Part 2. Themes a reviewer will expect cited.** For each theme give 2 to 5 verified works, newest first,
each with one line on what it shows:
1. Large language models (or transformers) for synthetic tabular data (for example GReaT, REaLTabFormer,
   TabuLa, or later work; verify names and venues) and their evaluation protocols.
2. Deep generative models for activity or mobility sequences, activity-based travel demand, or
   synthetic time-use diaries (including any using large language models to generate daily activity
   schedules).
3. Synthetic population synthesis: IPF, combinatorial optimisation, and deep generative methods
   (reviews preferred); and any study testing TRANSFER of a population synthesiser across regions or
   countries.
4. Time-use survey data used in building-stock or urban-scale energy models (national or multi-country),
   especially European and HETUS-based work.
5. Cross-national differences in daily activity timing (for example meal times, work hours) in Europe,
   from the time-use literature, relevant to why diaries may not transfer between countries.
6. Evaluation of generative models on held-out or shifted populations (distribution shift, domain
   generalisation) where a simple baseline wins; negative results.
7. Membership inference or memorisation risk in fine-tuned language models (beyond Shokri et al. 2017).
8. Pre-registration or registered reports in energy, building or environmental research.

**Part 3. Break the novelty table.** Our Table 1 compares studies on seven columns: survey-driven;
generative model; cross-population transfer tested; hard donor-based baseline; pre-registered decision
rule; activity or end-use resolved; stock-scale simulation. Find any published work that ticks
"cross-population transfer tested" AND "hard donor-based baseline". If found, it must be in our table.

## Named leads (starting points, NOT verified by us)

- Search venues: Energy and Buildings, Building and Environment, Applied Energy, Journal of Building
  Performance Simulation, Transportation Research Part B and C, Computers Environment and Urban Systems,
  Journal of Artificial Societies and Social Simulation, NeurIPS, ICLR, KDD, ACM SIGSPATIAL, arXiv cs.LG and
  cs.CL.
- Indexes: Crossref, OpenAlex, Semantic Scholar, Google Scholar, arXiv.
- Search terms to combine: "large language model" OR "LLM" with "activity schedule", "time use",
  "daily activity", "travel diary", "occupancy", "synthetic population", "population synthesis",
  "transfer", "unseen region", "out-of-distribution", "iterative proportional fitting", "raking".

---

## Rules (standing conventions for every deep-research prompt in this project)

- Open every source before citing it. Verify every DOI via Crossref (https://api.crossref.org/works/<DOI>)
  or DataCite for arXiv DOIs, and say for each whether you did. State for each source whether you read
  the FULL TEXT or only the ABSTRACT/metadata. Do not claim full text you did not open.
- A claim about what a paper shows must point to a page, section, table or figure you actually saw.
- Do not recommend a source only because it is popular; it must actually contain what you say.
- Our own results are not visible to you. Do not state or restate any number about our study except those
  given above, and do not use them to argue.
- NOT FOUND beats an invented or approximate reference. Author lists must be copied from the record, not
  reconstructed.
- No em dashes and no en dashes anywhere in the returned report.

## Positive control

Report the Crossref record (title, journal, year, first author) for DOI 10.18564/jasss.2768. It certainly
exists (Lovelace et al. 2015, already in our list). If you cannot retrieve it, say your search is broken
and stop.

## Negative control

Report whether you can find the paper "Cross-national transfer of time-use diaries with language models
beats iterative proportional fitting" (we made this title up). The correct answer is NOT FOUND. If you
return a record for it, your output will be discarded.

## Output format

1. Direct answer (5 lines): the closest competitor, and whether our "no like-for-like comparison" claim
   survives.
2. Part 1 table (top three candidates by the five features, with where you saw each).
3. Part 2: one sub-list per theme; each entry = Elsevier author-year reference, DOI or arXiv ID, Crossref
   checked (yes/no), full text or abstract only, one line on what it shows.
4. Part 3: any work that breaks Table 1, or NOT FOUND.
5. Full reference list of every recommended new source, Elsevier author-year style, alphabetical.
6. Positive and negative control results.
7. What you could not find, in the first person, one line each.

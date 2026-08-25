# HETUS-Wide Occupancy Generation with a Fine-Tuned Open-Weight LLM
### Cross-National Occupant Behaviour for BEM/UBEM — Paper 4 of the series
#### Step-by-step detail. Companion to `4thJ_00_HETUS_LLM_Pipeline_Overview.md`.

---

## AIM

One open-weight language model, fine-tuned once, generating activity-resolved daily diaries for any
country in the HETUS framework, with the transfer claim tested by holding a country out of training
entirely, and with the output carried through to simulated building energy.

**Everything in this document is still a plan. No artefact exists.** What changed on 2026-08-14 is that
the plan is now made of decisions with sources behind them rather than of open questions. Status tags
read `OPEN` or `DECIDED` until a file is on disk, at which point the tag becomes `✅ DONE` and names
that file, following the convention of the 3J documents.

---

## WHY THIS PAPER, STATED SO IT CAN BE ATTACKED

The honest framing. The deep-research series was designed to test it rather than defend it, and it
survived, but not unchanged.

**The claim we can make.** Papers 1 to 3 each trained a model on one country's microdata. Paper 1
asserts that HETUS standardisation makes the method "globally adaptable across all participating
countries" and does not test it. Testing it requires a model that can be conditioned on a country it
was not trained on.

**The claim we cannot make, now with a citation.** That a fine-tuned LLM beats a purpose-built
conditional Transformer at reproducing a distribution it was trained on. `RL06` ranks a 10M-parameter
from-scratch conditional Transformer — which is essentially paper 1's architecture — **above** the LLM
on fidelity, training cost, inference cost and structural validity, and gives it **zero** cross-national
transfer ability. It also reports that the benefit of language pretraining on tabular data disappears
somewhere around 1,000 training records, which we will have many times over. So the LLM has exactly one
justification and the paper must be built on it.

**The claim that got sharper.** `RL04` adds a confound running against us: open-weight models know
Anglophone and core-European daily life far better than peripheral European daily life. If transfer
worked *because* the model had read about the country, the result would be an artefact of pretraining
coverage rather than of HETUS harmonisation. **So transfer is pre-registered as schema-guided
statistical transfer, and a fictional-country negative control is part of the experiment, not an
afterthought.**

**The failure that would be invisible.** A model that produces the modal day for everyone in a stratum
matches aggregate marginals while being useless for building energy, because the entire value of
occupant modelling is diversity. Paper 1 already documents argmax producing "overly uniform occupant
characteristics" at neighbourhood scale. `RL03` independently reports the same failure from the
silicon-sampling literature: LLM-simulated survey respondents show severe within-group variance
collapse. Two independent literatures naming the same failure is the strongest reason to instrument it
from the first training run, which is what Tier 2 does.

---

## 🔴 REPORT VETTING RECORD — 2026-08-14, FIRST ROUND (`RL01` to `RL16`)

> **Read the second round too.** `RL17` and `RL18` returned later the same day and are vetted in
> **REPORT VETTING RECORD, SECOND ROUND** below. It adjudicates the eight contradictions listed here,
> and it records the two `RL18` claims that our own measurement disproved — one of which had been
> repeated in this document since it was written.

All sixteen reports were read in full before any value was written into these documents. The standing
rule from `DeepResearchPrompts/README.md` applies: *a report that agrees with something you supplied
has told you nothing*, and *every recommendation moving in the rescuing direction is a signal*. What
follows is what the vetting actually caught. It is recorded because the next person to read these
reports needs to know which parts were checked and which were not.

### V1. Cross-report contradictions, and how each was resolved

| # | The contradiction | Resolution | Why |
|---|---|---|---|
| 1 | **`RL04`: publishing the adapter is "legally unblocked" (Apache 2.0).** `RL10`: publishing it is a direct contractual violation | **`RL10` governs** | They are answering about different objects. The model licence permits it; the *data* agreement forbids it. The binding constraint is always the stricter one. `RL04` never read the data agreement and should not have opined |
| 2 | **`RL04`: pick Qwen2.5, its tokenizer splits digits.** `RL07`: measured that digit-splitting costs 23 % more tokens and recommends Llama 3.1, whose licence `RL04` rejects | **Neither. Open decision 3, resolved by our own measurement** | `RL07` measured; `RL04` reasoned. But `RL07`'s preferred model carries the anti-distillation clause `RL04` correctly flags. Mistral 7B v0.3 would have both properties, and **neither report proposed it**, which is itself informative |
| 3 | **`RL07`: episode encoding.** `RL12`: fixed slots, because a grammar cannot enforce a sum | **Episodes**, with a 145-state tally automaton | `RL12` names this escape hatch in its own text and then does not follow it. Durations are quantised to 10 min and bounded by 1440, so the tally is finite and the constraint is regular |
| 4 | **`RL06`: hybrid LLM plus raking is rank 1.** `RL09`: never rake generated output | **Both, split by purpose.** Raking builds the null; it never touches our output | This is the stronger reading of both. If we rake our own diaries we are partly the null we claim to beat |
| 5 | **`RL06`: the mandatory null is the raked pooled donor.** `RL08`: the null is the pooled average | **`RL06`'s null**, and `RL08`'s becomes secondary | The harder null is the real test. Adopting the easier one when the harder one has been named would be exactly the "recommendation that rescues us" the brief warns about |
| 6 | **`RL02`: three relational files, episode-long.** `RL01`: one flat wide file, ~1,950 variables | **Unresolved. Parser handles both** | Both claim to have read the same Eurostat documentation. Neither is trustworthy on this until a file is in hand. Cheap to make the parser agnostic; expensive to discover in month three |
| 7 | **`RL15`: release the LoRA adapter.** `RL10`: withhold it | **`RL10` governs** | `RL10` is the specialist prompt and shows its legal reasoning. `RL15`'s dual-track structure is adopted; only its weight-release element is dropped |
| 8 | **`RL02`: weight variables `WGHT_IND` / `WGHT_DIA`.** `RL09`: `IND_WGT` / `DIA_WGT` | **Unresolved, and it does not matter yet** | Variable names are verified against the delivered file, never against a report |

> **All eight were subsequently put to `RL17`, the adjudication round, which returned verdicts on
> every one.** What it settled, what it could not settle, and where its verdicts changed our work is
> in **REPORT VETTING RECORD, SECOND ROUND** below. Contradiction 2 — the one about tokenisation
> versus licence — was not settled by `RL17` either: **we settled it by measurement, and in doing so
> found that the licence half of the dispute rested on a clause that does not exist.**

### V2. Citation defects found

These do not invalidate the reports that carry them, but the affected claims are demoted.

* **LLM-Mob is cited with three different arXiv IDs and three different author lists** across `RL03`
  (2308.15197), `RL06` (2308.15043) and `RL14` (2309.04477). At most one is right. **`RL14`'s reference
  list is the least reliable of the sixteen** and its bibliographic entries are not reused.
* **GReaT** appears as arXiv:2210.06280 in `RL03` and `RL06`, and as arXiv:2210.01637 in `RL14`.
* **`RL05` reference [6]** is "AbstractAlgorithms Research Group, `abstractalgorithms.dev`", an
  unverifiable Tier-3 source, and it is one of only two supports for the claim that QLoRA degrades
  syntax by 2 to 6 %. **We still reject QLoRA, but on sufficiency (we have 80 GB) rather than on that
  evidence.**
* **`RL12`** cites several 2026 arXiv identifiers ("The Format Tax" 2604.03616, "The Silent Vote"
  2605.09739, "XGrammar-2" 2601.04426) that have the shape of fabrications. The renormalisation-bias
  *mechanism* is sound and elementary; it is kept as reasoning and those citations are not used.
* **`RL08`** gives Widén and Wäckelgård (2010) as *Applied Energy* 87(3):780-789; `RL06` and `RL13`
  give 87(6):1880-1892. The second is right for that title. `RL13` also independently corrected three
  other DOI defects, which is a point in its favour.
* **`RL10`** cites Mireshghallah et al. (2022) with the title of an unrelated visual-prompt-tuning
  paper, and refers to a "48-slot diary" that exists nowhere in our design.
* **`RL07`'s specification uses invented location codes (1 to 6) and a single co-presence digit**, both
  contradicted by `RL02`'s transcription of the actual coding lists. The format is adopted; the field
  semantics are taken from `RL02`.

### V3. Where the negative controls actually fired, which is the reason to trust these three

* **`RL13` reported `COULD NOT OPEN` for EN 16798-1 Annex C** instead of reconstructing plausible
  schedule values from secondary literature. That is the single most valuable line in the sixteen
  reports, because a reconstructed standard schedule would have been undetectable downstream and would
  have propagated into the baseline we benchmark against.
* **`RL04` refused to confirm "Gemma 4"** and enumerated what actually exists. The prompt planted that
  trap deliberately.
* **`RL09` caught and corrected two of its own citation defects mid-report**, including a Deming and
  Stephan DOI that resolves to a different paper.
* **`RL01` and `RL16` independently agree** that the "three HETUS waves" framing is wrong and that only
  the 2010 round exists as central microdata. Agreement between two prompts that were run separately
  and were not given each other's answers is worth more than either alone.

### V4. Claims we were *not* acting on until checked locally — status as of 2026-08-14, later

Each was cheap to settle and expensive to be wrong about. **Four of the six are now settled and two
are not.** The two that remain are the two that require asking a human being rather than running a
job, which is worth noticing.

| Claim | Source | Status |
|---|---|---|
| Mistral 7B v0.3 uses the Tekken tokenizer with 3-digit atomic numbers | `RL04` B9, `RL07` B3 | ✅ **SETTLED, and the claim is false.** Speed job `1234177`: `Mistral-7B-v0.3` splits `311` into **four** tokens and `Mistral-Nemo-Base-2407` into three. Neither is atomic. `RL17` A3 reached the same verdict independently and we then confirmed it ourselves |
| Real time-use surveys show unique-sequence fraction > 0.98 | `RL08` B5 | 🔴 **HALF SETTLED. Provenance yes, value no.** `RL17` A7 returned `NOT FOUND`: it is not a published benchmark, `RL08` invented it. **The empirical baseline on held ISTAT and GSS data has still not been computed, so Gate 6 is still not trusted** |
| HETUS stratum time budgets have a ±12 to 18 min/day margin of error | `RL08` Gate 3 | ✅ **SETTLED, and the claim is false.** `RL17` A6 searched the Eurostat methodological guidelines and returned `NOT FOUND`. No such table is published. The gate is permanently labelled project-chosen |
| Speed partitions are named `pt`, `pn`, `pg` | `RL11` | ✅ **SETTLED, and the claim is false.** `RL17` A8 confirms the live Slurm partitions are `ps`, `pt`, `cl`, matching our own 2026-08-13 `sinfo`. `pn` and `pg` are legacy Grid Engine queue names and would be rejected by the scheduler. Every job we have run since uses `--partition=ps` |
| Concordia can become a recognised research entity; peer Canadian universities already are | `RL01` B7 to B9 | 🔴 **STILL OPEN.** `RL17` C1 names Laval, Toronto, UBC, Ottawa, Trent, Brock and York as recognised and Concordia as absent, which is consistent with `RL01` — but two reports agreeing is not the Office of Research answering. **Not yet asked** |
| *Energy and Buildings* APCs are fully waived under the CRKN agreement | `RL14` B03 | 🔴 **STILL OPEN.** `RL17` C3 says 100 % waiver under the CRKN-Elsevier 2024-2026 agreement. That is a second report, not the library. **Not yet asked**, and it does not block anything |

---

## 🔴 REPORT VETTING RECORD, SECOND ROUND — `RL17`, `RL18`, AND THE MEASUREMENT THAT OVERRULED THEM

`RL17` (adjudication) and `RL18` (model family) returned later on 2026-08-14. They were vetted the
same way, and then **open decision 3 was closed by running our own jobs rather than by believing
either of them.** The headline results are in the overview document's status section; what follows is
the vetting itself, which belongs here.

### V5. What `RL17` got right, including against us

`RL17` is the better of the two reports and it earned that by landing on the inconvenient side four
times out of eight. Specifically:

* **A3, the Mistral tokenizer.** It declared `RL04` and `RL07` *both wrong* — v0.3 is SentencePiece
  with a 32,768 vocabulary and splits three-digit codes into four tokens, not one. **We then measured
  it and got exactly four.** A report that contradicts two earlier reports and is confirmed by our own
  measurement is the most credible thing in the whole series so far.
* **A6 and A7, the two `NOT FOUND` verdicts.** It refused to supply a literature source for the
  ±12-18 min margin of error and for the U > 0.98 unique-sequence benchmark, and said plainly that
  `RL08` had invented both. This is the negative control firing, and it costs us two provenance
  labels we would have liked to keep.
* **A1, the file shape.** It adjudicated for `RL02`: the Eurostat SUF is three relational files
  (`INDFILE`, `DDFILE`, `EFILE`) with **native `START` and `DURATION` fields** in `EFILE`, and
  `RL01`'s flat 144-slot wide matrix is a national export rather than the Eurostat delivery. If true
  this removes the run-length reconstruction step entirely. **The parser still handles both shapes.**
  A report adjudicating a dispute between two reports is not a file in our hands, and the standing
  rule that variable names and file shapes are verified against the delivered data is unchanged.
* **A8, the partitions.** Confirms `ps` / `pt` / `cl`, matching our own `sinfo`.

Its Part D question is worth keeping and is recorded in full below, because it identifies a gap
nobody in eighteen prompts had asked about.

### V6. 🔴 What `RL18` got wrong, and it is the report we commissioned to make this decision

`L18` was written specifically to close open decision 3. Two of its load-bearing claims are false.

1. **The token count it presents as measured.** `RL18` states that the mnemonic episode
   `45,wrk,11,0;` costs **8 tokens in Qwen2.5**, "fully matching Llama 3.1's token efficiency", and
   builds its design recommendation on it. **Measured on Speed, it costs 11.** The report counted
   `45` as one Qwen token — it is two — and `wrk` as one — it is two, `wr` + `k`. The consequences
   ran further than the arithmetic: it recommended writing mnemonic code spellings into the
   serialisation schema on the strength of a saving that does not exist at the claimed size, and the
   same remapping **increases** length on the tokenizer we have now adopted (200 → 211 tokens).
2. 🔴 **The Llama licence clause, which is a factual claim about a third party's legal document.**
   `RL18` B08 states as a Tier-1 fact with High confidence that "Llama 3.1 Community License Section
   1.b forbids using Llama outputs to improve any other non-Llama language model", and the whole
   Llama exclusion in these documents rests on it. **Meta's licence files were fetched and read in
   job `1234219`. Llama 3.1 does not contain that clause.** It contains a naming requirement:
   *"...you shall also include 'Llama' at the beginning of any such AI model name."* The
   anti-improvement clause exists in **Llama 2 and Llama 3** and was dropped at 3.1. Exact string
   counts for `improve any other large language model`: Llama 2 → 1, Llama 3 → 1, Llama 3.1 → 0,
   Llama 3.2 → 0, Llama 3.3 → 0.
   **`RL04` introduced this error, `RL18` restated it, and both plan documents carried it.** It is
   corrected in the overview rather than deleted, because a false statement about someone else's
   licence reaching a manuscript is a different order of problem from a wrong threshold.
3. **The landscape table is stale and says it is not.** `RL18`'s "open-weight landscape as of
   2026-08-14" ends in early 2025, contains no OLMo 3, no Qwen3 and no Llama 4, and then asserts that
   "no post-May 2026 release alters the conclusions established here". The vLLM registry we fetched
   the same day lists `Olmo3ForCausalLM`, `Qwen3ForCausalLM`, `Qwen3MoeForCausalLM`,
   `Qwen3NextForCausalLM` and `Qwen3_5ForCausalLM`. **`L18` was written to catch version rot and the
   report answering it has version rot.**

The pattern across `RL04`, `RL07`, `RL17` and `RL18` is now clear enough to state as a rule:
**a report's claim to have executed a measurement is not a measurement.** `RL17` and `RL18` both
present tokenizer counts under "direct tokenisation measurement"; `RL17`'s were right and `RL18`'s
were wrong, and nothing on the face of either report distinguishes them. Only running it does.

### V7. What we ran, and where it lives

Six CPU jobs on `ps`, all fire-and-forget, all reusing a throwaway venv at
`/speed-scratch/o_iseri/envs/4j_tok` that does not touch `envs/step4`.

| Job | Script in `tools/` | What it settled |
|---|---|---|
| `1234177` | `4thJ_tok_measure.py` | Tokenizer counts for nine repositories on the real episode and diary strings; the two-letter and three-letter mnemonic census |
| `1234192` | `4thJ_olmo_check.py` | OLMo 2 context (4,096 at every size) and family sizes; the **vLLM registry source**, which is where the native-versus-fallback split was found; XGrammar cleared as model-agnostic |
| `1234199` | `4thJ_olmo3_measure.py` | OLMo 3 discovered from the HF API rather than guessed: 31 repositories, only two base checkpoints, context lifted to 65,536, tokenizer identical to OLMo 2 |
| `1234211` | `4thJ_license_check.py` | Licence metadata and safetensors parameter counts for eleven repositories; `Qwen2.5-3B` confirmed non-commercial from its own `LICENSE` file |
| `1234216` | `4thJ_final_checks.py` | Ai2 model-card licence text; Qwen3 and Qwen3.5 tokenizers (identical to Qwen2.5, so the gap is a family property); Qwen3 base sizes |
| `1234219` | `4thJ_llama_clause.py` | Meta's Llama 2 / 3 / 3.1 / 3.2 / 3.3 licence text, which overturned the clause the exclusion rested on |

Two repositories are **not measured and nothing is claimed about them**: `meta-llama/Llama-3.1-8B`
and the Gemma family are gated and returned `401` without a token. A row we could not read is not
evidence in either direction, and the "Llama writes `411` in one token" claim therefore remains
somebody else's measurement, not ours.

### V8. `RL17` Part D — the question eighteen prompts by the same author did not ask

Recorded because it is the only genuinely new failure mode either report surfaced, and it lands
downstream of everything decided so far.

**The day-to-year resampling problem.** Time-use surveys give one or two cross-sectional diary days
per person. EnergyPlus needs 8,760 continuous hours. **Nothing in this plan says how 365 generated
days are chained into one household's year**, and the two obvious rules are both wrong in opposite
directions: drawing an independent diary each day assumes a person with no habits, which washes out
individual variance and **damps** coincident peak loads; repeating one generated weekday 250 times
introduces no day-to-day entropy at all and **exaggerates** them.

`RL17` proposes the experiment: 100 households, one annual archetype, three chaining rules —
independent daily resampling, static repetition, and Markovian habit-coupled resampling — compared on
annual peak electrical power and heating and cooling ramp rates. If peak demand moves by more than
about 25 % between rules, **the chaining method dominates the BEM result regardless of how good the
cross-national transfer is**, and it would be measuring our schedule-assembly convention rather than
the model. This is not yet anywhere in Steps 7 to 9 and it should be.

---

## 🔴 REPORT VETTING RECORD, THIRD ROUND — `RL19`, AND WHY ITS RECOMMENDATION IS NOT TAKEN

`L19` asked one question: can the corpus be widened past four countries through **national** routes,
without the Eurostat entity recognition we do not have? The round was commissioned because
leave-one-country-out currently trains on **three**, which limitation C4 names as the weakest part of
the design.

**`RL19` recommends acquiring Norway. We are not acting on that recommendation, and the reason is in
V10.** What we *are* acting on is its negative result, which is the more valuable half.

### V9. ✅ What `RL19` establishes, and it answers the commissioning question

* **The candidate set is right, and it checks out against Eurostat's own framing.** The HETUS 2010
  round is **18 countries: 15 EU member states plus Norway, Serbia and Türkiye**. `RL19`'s list of 15
  reproduces that split exactly, which is a consistency an invented list would be unlikely to hold.
  Removing our four leaves 14 candidates.
* 🔴 **There is no second Spain.** Across all 14 candidates, **not one is Tier 0 or Tier 1**. Two are
  Tier 2, eight are Tier 3 (per-project written application), two are Tier 4 (the applicant
  *institution* must be pre-accredited), and **two — Finland and Hungary — are Tier 5, secure enclave
  only, where the file never leaves the facility.**
* **Therefore national routes do not scale, and that is the finding.** Tier 4 reintroduces exactly the
  institutional barrier the national route existed to avoid, and Tier 5 is incompatible with training
  a model on our own cluster at all. **The Eurostat application is not the slow path to more
  countries; it is the only path.** That raises the priority of the Track A enquiry (1C) rather than
  providing an alternative to it.
* **A second, unasked-for finding worth keeping:** national archives do **not** distribute the
  Eurostat-harmonised file. Each ships its own variable names, its own file shape and, in several
  cases, its own activity classification. **"HETUS country" and "file harmonised to HETUS" are not the
  same object** — which is precisely what V10 turns on.

### V10. 🔴 Why Norway is not accepted, on our own screen

`RL19` recommends Norway (SSB, via Sikt) as a single high-stress Nordic addition. **The country facts
hold** — I confirmed against Statistics Norway directly that the 2010-11 survey uses **10-minute
intervals**, **two diary days**, ages **9 to 79**, paper diary. On slot length, B1, it passes.

**It fails B2.** `RL19`'s own row B6 states the national file carries the **SSB national
classification of roughly 170 categories**, not ACL 2008, and that a crosswalk would be required. It
asserts that a documented one-to-one recode table is provided. **Statistics Norway's own methodology
page names no coding list at all**, and I could not confirm the recode exists.

🔴 **If that recode does not exist, Norway forces the exact thing decision 6 was taken to prevent.**
`RL17` B3 states that a defensible cross-survey activity mapping exists **only at 2-digit ACL or MTUS
69**, and that full 3-digit cannot be mapped across heterogeneous surveys without arbitrary
one-to-many heuristics. A hand-built SSB-170 → ACL-2008 3-digit crosswalk **is** that heuristic. It
would sit inside the training corpus, unauditable, and it would land on Step 9, which is the step that
3-digit codes were preserved for.

**So Norway is conditional, not accepted.** The condition is a single checkable fact: **does the Sikt
delivery include an official Eurostat/ACL recode variable, produced by SSB rather than by us?** If yes,
Norway is admissible and worth taking. If no, it is rejected, and rejected for the same reason UK
2000-01 and Italy 2022-23 are.

✅ **The author opened this as decision 15 on 2026-08-14**, rather than leaving it as a conditional
note inside a vetting record. That is the right place for it: a conditional buried in V10 would be
read as settled, and this one can reverse decision 6 if it is taken casually.

Two further defects in the Norway case, neither fatal but both diagnostic: the Sikt landing URL is
given in a `study/NSD1849` form while Surveybanken now addresses studies by UUID, and the SSB
documentation report is cited as **Vaage 2012, Rapporter 2012/36**, where the documentation report for
this survey appears to be **Holmøy, Lillegård and Löfgren (2012)**. **That is the Widén failure class
again**: a real author from the right institution attached to the wrong document.

### V11. 🔴 Where `RL19` reports verification it did not perform

Recorded in full, because this is the third round in a row where the negative controls are the part
that fails.

1. **The Netherlands is falsified, at the point of its own strongest claim.** `RL19` places DANS TBO
   2011 at **Tier 2, free, 1 to 5 working days, "Confirmed reachable: Yes"**, lists its codebook among
   the documents it **opened in full**, and states under negative control 1 that it personally opened
   2 of 2 Tier-2 landing pages with a **guess count of 0**. **I opened that DOI. The files are
   restricted, no user access requests are permitted, and the record is a superseded version that
   cannot be downloaded.** The codebook it reports reading is not reachable, and its slot length —
   given as 10 minutes — is stated nowhere on the record.
2. **Part B is one template repeated ten times.** Ten countries return *identical* values: 10-minute
   slots, ACL 2008, full 3-digit released, paper self-completion booklet, 2 days, age 10+. The HETUS
   guidelines **recommend** those properties, so this is the guidelines restated per country as though
   each had been observed. Its own negative control 3 concedes only three candidate codebooks were
   opened, and four rows cite the Eurostat guidelines document as their source basis. 🔴 **A report
   that returns what we already supplied has told us nothing** — and it is the same defect that would
   let a 15-minute file onto an admissible list, which is the failure B1 exists to catch.
3. **The convenience control was gamed.** `RL19` defines a "convenient" country as one meeting **all
   seven** properties at once, then reports **0 of 14** convenient. No country could meet that
   definition; Norway meets five. **A control with an unreachable threshold cannot fire**, which is
   the same vacuity we screen our own gates for.
4. **It answers questions about our hardware.** Section D asserts that Sikt files fit our RAM and that
   our directory permissions satisfy the licence terms. It cannot see our cluster. Ignored.

**Net:** `RL19` is accepted for its landscape and rejected for its recommendation. **Its most useful
sentence is the one it did not intend as the answer** — that no reachable country ships a
Eurostat-harmonised file — because that is what makes national expansion cost a bespoke crosswalk per
country rather than a parser branch.

---

## 🔴 REPORT VETTING RECORD, FOURTH ROUND — `RL20` AND `RL21`, RETURNED 2026-08-14

Two single-question rounds, commissioned to close the last two open decisions. **Both returned the
inconvenient answer on the question they were asked**, which is the first time in this series that has
happened twice in one round. Both still carry defects, and in `RL21`'s case the defect is in the
number the report is most likely to be quoted for.

### V12. ✅ `RL20` — Norway is rejected, and the report earned that verdict

`L20` asked one thing: does the delivered Norwegian file carry an ACL-coded activity variable produced
by SSB. **The answer is no**, and it closes decision 15.

**What it establishes, and why it is credible.**

* **`A1.1` is a clean negative.** The Sikt delivery carries only SSB's national classification —
  reported as **exactly 167 categories in 5 main groups**, released at full national code depth — with
  **no ACL variable at any depth.** `RL19` said "roughly 170"; 167 is consistent with it and sharper.
* 🔴 **`RL19`'s recode table is formally retracted.** `RL20` searched SSB publications, the SSB `Klass`
  classification database and the Sikt metadata and returned `NOT FOUND` for any official correspondence
  table, and states plainly that it found **neither the table nor an official statement that one is
  published.** That is the distinction the prompt asked for and most reports blur.
* **The citation defect is confirmed and corrected.** The documentation report for the 2010-11 survey is
  **Holmøy, Lillegård and Löfgren (2012), Notater 2012/03**, not Vaage 2012 Rapporter 2012/36. Vaage
  (2012) exists but is *Tidene skifter: Tidsbruk 1971-2010*, **Statistiske analyser 125** — a trend
  analysis, not survey documentation. **This is the Widén failure class, diagnosed and fixed.**
* **`D2` returns `NOT FOUND` for a published third-party crosswalk**, and correctly notes that MTUS
  harmonises Norway only at 69 or 41 activities, which is below the resolution Step 9 needs. So there
  is no citable route either.
* **It obeyed the skip instruction.** Part A came back negative, so Part B was skipped rather than
  filled in for completeness. A report that declines to produce content it was told not to produce is
  worth noticing, because most do not.
* **One detail that reads like a real file rather than a description:** it names the diary variables as
  `akt1` to `akt144` plus `hovedaktivitet`. **144 slots at 10 minutes is 1440**, so the variable list
  is internally consistent with the slot length, and it also confirms the Norwegian national release is
  a **wide slot file**, not an episode file. An invented variable list is unlikely to land on exactly
  144. Not load-bearing, since Norway is out, but it is the kind of corroboration we look for.

**Where it must not be believed.**

1. 🔴 **Part E's "decisive flaw" was quoted from our own prompt.** `L20` was asked to name the one thing
   most likely to be wrong that we had *not* thought of. It answered: the sampling frame stops at age
   79. **Our prompt states, in its own text, that the survey covers ages 9 to 79 and that we confirmed
   it ourselves.** The standing rule applies exactly: *a report that returns what you supplied has told
   you nothing.* Part E is empty.
2. **And the comparison inside Part E is unsourced.** It claims our four countries "sample the full
   adult and elderly population without an upper age ceiling (or up to 90+)". **Every source it cites in
   that section is Norwegian.** The upper age limits of the Italian, Spanish, French and UK waves are
   not established anywhere in this project and are not established by `RL20` either.
3. 🔴 **Section D answers questions about our hardware and our agreements, again.** It states our folds
   fit "within standard GPU memory and 7-day walltime limits". It cannot see our cluster. Ignored, and
   noted as the third consecutive round to do this.
4. **It claims to have skipped Part B and then answers parts of it.** Section F and negative control 3
   report Norway as Tier 2, cost EUR 0, turnaround "1 to 3 days". **The turnaround is exactly the kind of
   unpublished estimate the prompt said to return `NOT FOUND` for**, and it is asserted with no source.
   Harmless here only because the decision does not turn on it.
5. **`C1` says the licence is silent and then reasons past its own finding.** Correctly labels the Sikt
   terms **silent** on synthetic data, then adds an assessment that release "complies with standard
   statistical disclosure control principles". **Silence is not permission**, that assessment is the
   report's opinion rather than a licence finding, and legal reading is `RL10`'s job. Moot, since Norway
   is out.
6. **It assigns tiers to our own four countries in `D3`** — UK, France and Italy all at "Tier 2 / 2 / 2-3"
   — which does not match what we already hold: UK is a free End User Licence registration, Italy is a
   per-project application of two to eight weeks. Not used.

🔴 **The honest caveat on the whole report.** `L20` told it, in writing, that a short negative report
was the expected outcome. It returned a short negative report. **We asked for the answer we got**, and
that is a reason to hold the verdict at the confidence its checkable details support rather than at the
confidence the report claims. Those details — 167 categories, `akt1` to `akt144`, Notater 2012/03,
`Klass` searched — are specific and falsifiable, which is why the verdict is accepted. **If Norway is
ever reconsidered, the one thing to open is the Sikt variable list itself.**

**Net: decision 15 closes NO. The four-country corpus stands and limitation C4 stands with it.**

### V13. 🔴 `RL21` — the negative result is accepted, every number in it is not

`L21` asked what the literature does about chaining one or two diary days into a year, and above all
whether anyone has ever **measured** the difference between rules. **It answered zero**, which is the
answer that creates work rather than saving it.

**What is accepted.**

* 🔴 **`B1`: zero published studies compare two or more chaining rules on the same building, weather and
  archetype, holding the daily generator fixed.** It distinguishes this from the many studies comparing
  *static versus stochastic schedules*, which conflate within-day stochasticity with cross-day assembly.
  **Decision 14 therefore cannot close by citation. It closes by experiment or not at all.**
* **`B13` and `C2`: no published threshold exists** for when a modelling convention dominates a
  simulation result. The 25 % figure from `RL17` Part D has **zero literature basis** and is permanently
  labelled project-chosen, joining the ±12-18 min margin and the U > 0.98 benchmark. The nearest citable
  neighbours are ASHRAE Guideline 14 calibration tolerances, which are a **different quantity** — model
  versus measurement, not convention versus convention — and may be quoted only as context, never as a
  bar.
* **`A3` and `B5`: there is no standard practice.** No ASHRAE, ISO or IBPSA document defines a chaining
  protocol. Consequence for us: **our assembly rule is an explicit modelling choice and the methods
  section must defend it**, because there is no default to inherit.
* **`B4`: IEA EBC Annex 66 and Annex 79 are silent** on day-to-year concatenation and treat schedule
  generation as an upstream boundary condition. An authoritative source that is silent is a useful
  finding, and it is the one we would otherwise have been asked about in review.
* 🔴 **`B11`: a two-day design of one weekday plus one weekend day cannot identify consecutive-day
  transition probabilities.** This is arithmetic rather than literature — the two observed days are not
  adjacent and straddle a regime change — so it can be accepted on its face. **It is the most
  consequential thing in the report**, and see the design consequence below.
* **Widén and Wäckelgård (2010) resolved: *Applied Energy* 87(6):1880-1892**, `10.1016/j.apenergy.2009.11.006`.
  This matches `RL06` and `RL13` and confirms `RL08` was wrong, which is what V2 already recorded.

**What is rejected, and it is every quantity in the report.**

1. 🔴 **The headline number contradicts the headline finding.** `B7` states that peak demand varies by
   **15 to 35 %** between static repetition and independent resampling, labelled **Fact**, Tier 2,
   confidence **High**, sourced to McKenna and Thomson, Fischer and Deru. **But `B1` says no study has
   ever compared chaining rules.** Both cannot be true. `B7` is an assembly from coincidence-factor
   theory wearing a measurement's label, and it is attached to real papers that did not make the claim —
   **the same failure class as the Widén citation, one level up.**
2. **The same quantity appears three times with three values.** Section A and `B7` say 15 to 35 %
   between rules; Part B2 says static overestimates by **15 to 40 %** against substation measurements
   while resampling damps by **10 to 25 %** against the same; Section G says 15 to 40 %. Those are two
   different comparisons that do not compose into either range. **A number that changes when the section
   changes was never measured.**
3. **`B6`, annual energy insensitive at under 3 %, is honestly labelled `Inference`** — and then Section
   A and Section E restate it as established and instruct us to put it in the discussion. **An inference
   may not enter the manuscript as a finding.** Cheap fix, below.
4. 🔴 **`B10`'s persistence value violates the prompt's own rule.** The lag-1 autocorrelation of
   **0.15 to 0.35** is labelled Fact with High confidence and sourced to Pas and to Hanson and Huff —
   both of which the report's own negative control 1 places in the **"seen described / secondary"** list
   and whose reference entries read `[Read summary]`. `L21` required every quantitative value in Part B
   to come from a paper opened in full. **It is the only numeric persistence figure in the report and it
   comes from papers the report says it did not open.**
5. **Dangling citations, six of them.** Pas (1986), Widén et al. (2012), Widén et al. (2009), Clevenger
   and Haymaker (2006), Sun and Hong (2017), Rusck (1956) and Saltelli et al. (2008) are cited in text
   and **none has a reference entry**. `B8` tags Widén et al. (2012) as `[R14]`, which is D'Oca and Hong
   on window opening.
6. 🔴 **Negative control 1 lists a paper the report never uses.** **Page et al. (2008)** appears in the
   "opened in full" list and appears **nowhere else in the report and in no reference entry.** An
   opened-in-full list padded with an unused citation is the same control failure as `RL19`'s, and it is
   the control specifically meant to be un-fakeable.
7. **D'Oca and Hong (2014), a window-opening data-mining paper, is given as a representative paper for
   whole-year archetype clustering.** Real paper, wrong role.
8. **The Mobidrive description should be checked before any of it is cited.** The report places the
   study in "Zurich and Karlsruhe" and gives a variance split of "40 to 60 % intrapersonal and 40 to
   60 % interpersonal" — **two ranges that need not sum to 100 %**, which is not how a variance
   decomposition is reported. Sample size and person-days are at least internally consistent
   (361 × 42 ≈ 15,000). 🔴 **Verification of the site names and the split is the author's, not ours.**
9. **The ASCII coincidence-factor plot is a drawing, not data.** Its three `CF_inf` bands
   (0.45-0.55, 0.25-0.35, 0.15-0.22) carry no source. **It must never become a figure**, and it is
   exactly the shape of thing that survives into a manuscript because it looks like a result.
10. **`C3`'s diagnostic is worth keeping and its guarantee is not.** The schedule-level coincidence
    index is cheap and computable. The claim that a 20 % shift in it **"guarantees"** a corresponding
    shift in simulated peak power is an unsupported causal statement with an invented threshold.
11. 🔴 **Section D answers about our hardware, and this time it is wrong on a fact.** It states that
    private home directories "satisfy Eurostat academic confidentiality agreements". **We hold no
    Eurostat agreement** — that is Track A, unfiled. It also predicts 300 annual EnergyPlus runs in 45
    to 60 minutes, which depends entirely on a model it has never seen.

**On negative control 3.** `RL21` reports **0 of 4 convenient**, where `RL19` reported 0 of 14 by making
the threshold unreachable. This one is the opposite shape and needs stating: the prompt told the report
we half expected zero comparison studies, and it returned zero on every axis. The findings that create
work for us are credible; **the one axis scored inconvenient on an unverifiable number is `B7`, and
`B7` is the number that makes the rest of the report consequential.** Read that as the report's
incentive rather than as its evidence.

### V14. What `RL21` changes in the work, which is more than its recommendation

* 🔴 **Decision 14's shape has changed even though it has not closed.** It is now established that it
  **cannot** close by citation. The remaining question is not *which rule does the literature endorse*
  but *what does our own experiment show*, and that experiment is now the only route.
* 🔴 **`B11` removes a rule we were about to build.** If a two-day design cannot identify consecutive-day
  transitions, then the habit-coupled Markovian rule `RL17` proposed **cannot be parameterised from our
  own corpus.** Its persistence parameter would be chosen by us, which means comparing it against the
  other two rules would compare our choice against itself. **Recommended consequence: rule 3 is run as a
  sweep over the persistence parameter rather than as a single fitted rule**, so that what is reported
  is the sensitivity band, not a fitted value. That is the manager's recommendation, not `RL21`'s.
* **The insensitivity claim gets tested for free rather than believed.** `B6` says annual energy moves
  under 3 % while peak moves much more. **Record annual energy in the same 100-household campaign.** It
  costs nothing, and it converts the report's inference into our own measurement — which is the pattern
  that settled open decision 3.
* ✅ **`RL21`'s Part D is the one Part D in this series that answered the question it was asked.** Not
  the two failure modes we excluded, but a third: under independent resampling a synthetic individual
  walks the whole conditional distribution, so a full-time worker accumulates an implausible number of
  distinct activities per month and a household loses role coherence between days. **The test is cheap
  and computable on generated schedules alone.** Its `> 15 distinct 2-digit codes` criterion is
  project-chosen like everything else here, but **the diagnostic is real and the empirical value is
  computable on the ISTAT data we already hold** — which is where the criterion should come from.
* **It connects to decision 12.** Role incoherence between days is a household-level defect, and
  household-joint generation is the deferred decision that would address it. Recorded so the link is
  not rediscovered later.

**Net: `RL20` closes decision 15 as NO. `RL21` does not close decision 14, and establishes that nothing
except our own experiment can.**

---

## 🔴 REPORT VETTING RECORD, FIFTH ROUND — `RL22` AND `RL23`, RETURNED 2026-08-14

Two single-question rounds on the two newer waves that are obtainable in principle: UK 2020-21 and
Italy 2022-23. **Both returned negative on the deciding question, and neither pushed in the rescuing
direction** — the first round in this series where that is true of both reports at once. Both are
still wrong about our own corpus in the same place, and both pad their evidence lists the same way.

### V15. ✅ `RL22` — the UK 2020-21 file is obtainable, and it is not a HETUS diary

The commissioning question was whether the file uses the UKTUS 2014-15 coding list. The answer is no,
and the reason is larger than the one we had.

* **What we thought.** UK 2020-21 was excluded for being online, lockdown-era and age 16+. That is a
  confound argument, and it implicitly assumed a HETUS-style diary underneath the confound.
* **What the report establishes.** The accessible file is not a national HETUS wave at all. It is the
  **CTUR CaDDI six-wave COVID sequence**, an online instrument with a **closed drop-down list of about
  36 activity categories**, against roughly 250 three-digit codes in UKTUS 2014-15. A reduced menu is
  not a coding-list *edition* difference; it is a different instrument answering a different question.
* ✅ **Accepted, because it is checkable in the open literature.** CaDDI's design is described in two
  open-access papers the report cites with resolvable DOIs (PNAS 2021, PLOS ONE 2021). We are not
  taking this from the archive documentation, which the report almost certainly could not open.
* 🔴 **The second finding is the one that would have cost us most, and it needs confirming before it
  is used:** the report states the sample is **individual panelists from a commercial online panel,
  with no household clustering**. If true, the file carries no whole-dwelling co-presence at all,
  which removes the only property that would have made it interesting for building energy work. It is
  checkable in the same open-access papers. **Confirm before quoting.**
* **Route, believed on its checkable parts:** UK Data Service, SN 8741, End User Licence, free, and
  reachable by a Canadian academic. Contrast: the ONS Online Time Use Survey is secure-access only and
  **is not reachable by us at all**, which is a useful negative in its own right.

### V16. ✅ `RL23` — Italy 2022-23 does not exist as a file, and that ends the question

* **The deciding fact is release status, and it is negative.** No diary-level microdata has been
  released in any channel, and **no release date is published**. What was released on 10 February 2026
  is the **voluntary-work module only**, with documentation the report quotes as stating explicitly
  that the daily diaries are excluded. That quotation is a checkable identity and is the single most
  useful line in the report.
* **Consequence: there is nothing to acquire, so there is nothing to decide.** The wave cannot be a
  held-out instrument, cannot be requested, and does not need a licence review.
* **The coding finding is secondary but survives.** Even once released, the wave uses the newer ACL
  generation, and the report places the official correspondence table in **Annex VII of the Eurostat
  HETUS 2018 guidelines, re-edition 2020**, describing the mapping as one-to-one at 1 and 2 digits and
  **one-to-many at 3 digits**. If that holds, a newer Italian wave can never be placed against our
  2013-14 wave at the depth Step 9 needs without a crosswalk we would have to build ourselves, which
  we refuse.

### V17. 🔴 What both reports get wrong, and it is the same failure class as every round before

* 🔴 **Both make a claim about our own corpus that our own file falsifies.** `RL23`'s Part F asserts
  that the UK, France **and Spain** each field a two-day diary and that Italy's single day is the
  outlier. **We measured Spain: one diary day per respondent**, G1.9 PASS on 19,295 diaries, and
  INE's methodology says the same. Rule 1 of the vetting checklist exists for exactly this: a report
  cannot see our data, so anything it says about our data was quoted from the prompt or invented, and
  this was invented.
* 🔴 **`RL23`'s "108 codes in ACL 2008" cannot be adopted.** Our Spanish file, a 2008-generation wave,
  uses **116** three-digit codes, enumerated in INE's own annex and measured in the delivered file
  (F-ES-5). The report restates the same 108/116 pair that `RL02` gave us, as though it were an
  independent finding. **Whether that pair describes the editions at all is now a Step 2 question**,
  and it is one more reason the activity crosswalk is built from codebooks rather than from reports.
* **Both pad their opened-in-full lists with our own paper**, which is irrelevant to either question
  and which they cite with **two different initials for the same third author**. Padding plus an
  inconsistent citation of the same reference across two reports is the cheapest fabrication signal
  there is, and it is the third round in a row where the evidence list is the part that fails.
* 🔴 **Every variable name in both reports is unverified.** `RL22` gives archive variable names for a
  file behind a registration wall it could not have passed, and writes several of them with a slash
  (`survey_device` / `device_type`), which is uncertainty presented as fact. `RL23` sources its entire
  instrument description — location codes, co-presence flags, 04:00 origin, minimum age — to a **paper
  questionnaire model with no URL**, claimed as opened in full. That is `RL19`'s Netherlands failure
  class exactly. **No variable name from either report may enter a document or a reader.**
* **Minor, recorded so it is not rediscovered:** `RL22` gives the ONS secure-access study as
  *2020-2024* in its tables and *2020-2023* in its reference list.

### V18. What this changes in the work

* **Neither file is acquired.** Italy 2022-23 cannot be — it does not exist as a research artefact.
  UK 2020-21 could be, in about an hour, and **the recommendation is not to**: every acquisition adds
  a licence with destruction and reporting obligations, and a 36-category instrument without household
  structure supports no test we have. Revisit only if a deliberately coarse comparison is ever wanted.
* ✅ **Decision 6 is reinforced on stronger grounds than it was taken on.** The exclusion of UK 2020-21
  no longer rests on a mode-plus-lockdown confound argument; it rests on the file not being a
  HETUS-coded household diary. That is a better sentence for the limitations section, and it is one a
  reviewer can check.
* **The `MODE` and `SCHEME` prefix fields keep their justification and lose one use case.** They were
  written so a newer wave could be admitted later without changing the record format. `RL23` shows
  there is no newer wave to admit for the foreseeable term, so the fields are now insurance rather
  than preparation. They cost a handful of tokens and they stay.
* 🔴 **The age of the UK 2020-21 respondents is now disputed, and we do not adopt either number.** Our
  1B-bis table says 16+, `RL22` says 18+, and both are unverified. **The exclusion does not depend on
  it**, so the disputed figure is marked rather than replaced. Swapping one unverified number for
  another would look like a correction and would not be one.

**Net: `RL22` and `RL23` close the newer-waves question with two negatives. Nothing is acquired,
nothing enters training, and decision 6 stands on better evidence than before.**

---

## STEP 0 — FEASIBILITY GATE

**Status: ✅ CLEARED 2026-08-14.**

| Report | Question | Verdict and what it forced |
|---|---|---|
| `RL01` | Can a Canadian-based postdoc obtain HETUS **diary-level** microdata | **Yes in principle, no on our current timeline.** Eurostat releases diary-level Scientific Use Files, but only for the 2010 round, and only to recognised research entities. **Concordia is not one.** Recognition is about 4 weeks, then 8 to 10 weeks for the proposal. **Forced: Track B becomes primary and Track A becomes a parallel application** |
| `RL03` | Is this already published | **No.** Zero papers fine-tune an LLM on time-use microdata for building occupancy. The adjacent LLM travel-diary work is real and must be cited as the nearest neighbour rather than ignored |
| `RL06` | Is a fine-tuned LLM the right instrument | **Only for transfer.** Everywhere else it loses to what we already build. **Forced: the paper is framed exclusively on cross-national transfer, and three mandatory baselines are added** |
| `RL10` | May a model trained on this microdata be released | **No.** **Forced: the deliverable becomes a synthetic dataset plus code plus a public stand-in pipeline, and a four-attack privacy audit joins the validation plan** |

**The two weeks were worth it.** Three of the four answers changed the plan, and two of them
(the access latency and the release prohibition) would each have been discovered in month four or later,
after the corresponding work had been done the wrong way.

---

## STEP 1 — CORPUS DEFINITION AND ACQUISITION

**Status: ✅ CLOSED 2026-08-14 by author decisions 5 and 6. HETUS only, four countries, one wave each.
Acquisition is open and executable; the definition is not.**

### 1A. Four HETUS countries, one wave each

🔴 **Author's decisions, 2026-08-14, taken after reading `RL17`'s wave inventory. They replace the
"five countries × several waves" decision of the same morning, and the inventory is what replaced it.**

**Decision 5 — the corpus is HETUS only. No Canada, no United States.** The Canadian GSS cycles and
ATUS leave the paper entirely. The reason is the paper's own logic: paper 1 claims that **HETUS
standardisation** makes the method globally adaptable, and 4J exists to test that claim. A corpus made
of HETUS members is the corpus that tests it. Bringing in a non-HETUS survey would test something
adjacent — whether the method survives a different harmonisation frame — which is a different paper.

**Decision 6 — one wave per country, and it is the HETUS 2010 round.**

| Source | Country | Wave | Status | Note |
|---|---|---|---|---|
| ISTAT *Indagine sull'uso del tempo* | Italy | **2013-14** | **HELD** | Paper 1's data and the control: the new method must reproduce paper 1's Italy result on paper 1's data |
| INE *Encuesta de Empleo del Tiempo* | Spain | **2009-10** | open download, **no registration** | **Single diary day per respondent**, so no within-person multi-day structure for Spain. Also the only zero-credential source we have left, which now matters for open decision 13 |
| UK Time Use Survey (UKDS SN 8128) | UK | **2014-15** | End User Licence registration | 10-minute slots, ACL 2010, age 8+ |
| INSEE *Enquête Emploi du Temps* | France | **2009-10** | Progedo/ADISP academic registration | Minimum age 11, against the HETUS standard of 10 |

**What this set has that no other set has: it is internally uniform.** One coding-list generation, one
slot length, one collection mode (paper self-completion), 10-minute quantisation everywhere. And it is
**exactly the HETUS 2010 round**, which is the round Eurostat's central Scientific Use File covers — so
if Track A lands, the corpus goes from four countries to seventeen **with no harmonisation change at
all.** The corpus grows in the dimension the paper is about.

🔴 **The cost is recorded as limitation C4:** four countries means leave-one-country-out trains on
three, and Italy, Spain, France and the UK are not a demanding spread. A reviewer can fairly ask
whether transfer across four neighbours demonstrates transfer across a framework. Track A is the only
thing that answers that, and until it lands the claim is stated at the scale the corpus supports.

### 1A-bis. ✅ The wave inventory, returned by `RL17` Part B

`L17` Part B asked for the full inventory: which waves exist, which we can actually obtain, and where
the comparability breaks fall. It came back. Summarised — the full table with fieldwork years,
conducting bodies, slot lengths, minimum ages and landing URLs is in `RL17` Part B1.

| Country | Waves reported | Access | The break that matters |
|---|---|---|---|
| Italy | 1988-89, 2002-03, 2008-09, **2013-14**, 2022-23 | ISTAT Micro.dati, free, 2 to 8 weeks | ACL 2000 → 2008 → 2010 → 2020 coding changes; 2013-14 is paper 1's wave and our control |
| Spain | 2002-03, **2009-10**, 2024-25 | INE open download, instant | 2002-03 is ACL 2000. One diary day per respondent in every wave. 2024-25 microdata not yet released |
| UK | 1983-84, 1995, 2000-01, **2014-15**, 2020-21 | UKDS, free academic registration | **2000-01 is 15-minute slots**; 2020-21 is online, COVID, and age 16+ |
| France | 1974-75, 1985-86, 1998-99, **2009-10** | Progedo/ADISP, free, 2 to 4 weeks | 1998-99 is ACL 2000; 5-minute slots before 1998; minimum age moved 15+ → 11+ |

*(`RL17` also inventoried seven Canadian GSS cycles. They are out of the paper under decision 5 and
are not reproduced here.)*

**Two findings from it that changed work rather than merely informing it.**

1. 🔴 **`RL17` recommended two waves per country, and its own inventory is what argued the author out
   of it.** Its concrete proposal was Italy 2008-09 + 2013-14, Spain 2002-03 + 2009-10, UK 2000-01 +
   2014-15, France 1998-99 + 2009-10. Read that list against the break column above:

   * **Three of the four second waves — Spain 2002-03, UK 2000-01, France 1998-99 — are ACL 2000**,
     which our own Step 2A calls a genuine structural break with 144 codes and a reorganised computing
     and travel treatment. Pooling across it forces 2-digit codes, and **2-digit codes starve Step 9**,
     whose appliance triggering needs to tell laundry from cooking from washing.
   * 🔴 **UK 2000-01 is worse than a coding break: it is 15-minute slots.** Its episode durations are
     multiples of 15. Our grammar requires multiples of 10 summing to 1440, enforced by the 145-state
     tally automaton in Step 7. **That wave is not admissible to the constraint machinery** without
     re-quantising every episode boundary by up to five minutes, and the re-quantisation error would
     land directly on the dwell-time and transition gates in Tier 1.
   * Italy is the one country where two waves would have been clean, and Italy is also the control.

   Against that, the gain is data volume — `RL17` estimates 150,000 to 250,000 extra diary days across
   the five original countries — and `RL06` already reports that the benefit of language pretraining on
   tabular data disappears somewhere around 1,000 training records. **We are far past that either way,
   so volume is not the binding constraint and it was not worth the breaks.** Hence decision 6.
2. **The crosswalk question got a sharper answer, and one wave per country dissolves it.** `RL17` B3
   states that a defensible cross-national, cross-wave mapping exists **only at the 2-digit ACL level
   or the MTUS 69 level**, and that full 3-digit ACL cannot be mapped across heterogeneous surveys
   without arbitrary one-to-many heuristics. Gershuny and Fisher (2014) and Sullivan et al. (2020)
   pooled 60-plus surveys precisely by staying coarse. **Because our four waves share one coding-list
   generation, nothing is cross-wave and nothing forces us coarse: the `ACT` field keeps its 3 digits.**
   MTUS 69 stays available as the bridge if earlier waves are ever used in validation.

### 1B. What the earlier waves still do, now that they are not training data

They are not discarded. **They become held-out validation, and that is a real role rather than a
consolation.** The four training waves share one instrument; the earlier waves do not. So they can be
used to ask a question the training corpus cannot answer on its own: *does a model trained on ACL 2008
and 2010 diaries generate something that still resembles the same country a decade earlier, once the
known instrument differences are accounted for?* A failure there is informative and a success is not
claimed as a temporal result, because **there is no forecast in this paper and nothing extrapolates.**

What they may never be is training data. The mode and coding differences that made them attractive as
volume are exactly what would make the model learn the questionnaire instead of the behaviour — the
failure `RL17` B4 calls a *severe* threat to generative fidelity, and the one that is invisible because
it looks like behavioural diversity.

🔴 **One forward-compatibility measure, and it costs nothing now.** The conditioning prefix carries two
fields that are **constant across the entire training corpus**: collection mode and coding-list
generation. They are written into the serialisation from the first record even though they never vary,
so that adding a wave, or seventeen Track A countries, later does not change the record format or
invalidate a trained tokenizer's expectations. **They are not year tokens and must never become one** —
naming the instrument is a different thing from naming the time, and only one of them can be
extrapolated.

### 1B-bis. 🔴 The *newer* waves, and why none of them is in the corpus either

Decision 6 is usually read as a decision about older waves. It is equally a decision about newer ones,
and that half needs stating explicitly, because "why not just use the most recent data?" is the first
question a reviewer asks of any survey-based paper.

| Wave | Why it is not training data |
|---|---|
| **UK 2020-21** | ~~Lockdown fieldwork, collected **online**, minimum age raised to 16+.~~ 🔴 **Restated 2026-08-14 on stronger grounds (V15): the accessible file is not a HETUS-coded national diary at all.** It is the CTUR CaDDI online instrument with a closed menu of about **36 activity categories** against roughly 250 three-digit codes in UKTUS 2014-15, sampled from **individual panelists with no household clustering**. The lockdown and mode confound is still true and is now the second reason, not the first. **The minimum age is disputed — 16+ here, 18+ in `RL22`, neither verified — and the exclusion does not depend on it** |
| **Italy 2022-23** | ~~**ACL 2020** coding list **and** web/app collection.~~ 🔴 **Superseded 2026-08-14 (V16): the diary microdata has never been released and no release date is published.** There is no file to exclude. The coding argument survives as a second reason for whenever it does appear: the newer ACL generation maps **one-to-many at 3 digits** against ours. The web/app claim was `RL02`-era and `RL23` states the wave was fielded on paper; **both are unverified and neither is load-bearing** |
| **Spain 2024-25** | **Microdata not released.** The wave exists; the file does not |
| **France 2024-25** | Postponed round-3 fieldwork. Nothing to obtain within this paper's horizon |

**The common cause, and it is one cause rather than four.** Our four training waves are all **paper
self-completion under one coding-list generation**. That is precisely what lets the `ACT` field keep
three digits (1A-bis, finding 2) and what Step 9's appliance mapping depends on. Admitting any web or
app wave would reintroduce the cross-instrument pooling that decision 6 exists to prevent, and the
mode effect would arrive disguised as behavioural diversity.

🔴 **And the round that would supersede all of this is not available.** The Eurostat **HETUS 2020
round** — 20 countries, 15 EU Member States plus Norway and four candidate countries — has fieldwork
concluding in **2026**, and **Eurostat states microdata will not be released before 2027**. Verified
against Eurostat's own microdata page and its 2024 UNSD presentation on 2026-08-14. **There is no
newer obtainable corpus, and this paper is not waiting for one.**

*Consequence for 1B:* held-out validation therefore runs **backwards in time only**. The newer waves
are not a forward held-out set, because we cannot obtain three of the four. If Italy 2022-23 is
acquired later it becomes a second held-out instrument, never a fifth training country, and `MODE` and
`SCHEME` in the prefix are what make that admission cost nothing structurally.

### 1C. Track A, running in parallel — and it now carries more weight than it did

Eurostat HETUS 2010 Scientific Use File, reported as 17 countries. Two actions, neither of which blocks
anything: file the entity-recognition application for Concordia, and identify a co-investigator at an
already-recognised institution as the faster alternative.

🔴 **What changed on 2026-08-14: our corpus is now exactly the HETUS 2010 round.** That has two
consequences. Track A would widen the corpus **from four countries to seventeen with no harmonisation
change at all** — same coding list, same slot length, same round — so the integration cost is close to
zero. And with only four countries, leave-one-country-out trains on three, which limitation C4 names as
the weakest part of the design. **Track A is still not on the critical path, but it has stopped being a
nice-to-have.** It remains unfiled, which is why it is the second item on the next-actions list.

🔴 **What changed again on 2026-08-14, later: `RL19` closed the alternative.** We commissioned a round
to ask whether national routes could widen the corpus without Eurostat. **They cannot.** Of the 14
candidate countries in the HETUS 2010 round, **none is Tier 0 or Tier 1**, two are Tier 4 (the
institution must be pre-accredited, which is the same barrier Track A has), and **two are secure
enclave only**. Worse, no national archive ships the Eurostat-harmonised file, so each country costs a
bespoke parser **and** an activity crosswalk rather than a parser branch. **Track A is therefore not
the slow route to more countries; it is the only route**, and the enquiry moves from second on the
next-actions list to first. See V9 to V11 for the vetting.

### 1D. 🔴 Track C is gone, and what replaces it is undecided

`RL15`'s contribution was a fully public ATUS pipeline. Because `RL10` forbids releasing the model, a
reader without a Eurostat licence could otherwise reproduce nothing at all, and ATUS needs no
application at all. That was the answer.

**Decision 5 removes ATUS from the paper, and the answer goes with it.** This is recorded as a loss
rather than smoothed over, because it was the single strongest response we had to the no-weights
restriction.

What is left, ranked by how little a reader has to do:

| Source | What a reader must do |
|---|---|
| **INE Spain 2009-10** | **Nothing. Open download, no registration.** The only zero-credential source remaining |
| UKDS UK 2014-15 | Free End User Licence registration |
| Progedo/ADISP France 2009-10 | Free academic registration |
| ISTAT Italy 2013-14 | Free application, 2 to 8 weeks |

The obvious candidate is therefore **a minimal public path built on Spain alone**: one country, one
wave, no credentials, running the whole pipeline end to end. It would not demonstrate transfer — one
country cannot — but it would let a reader execute every stage and reproduce the machinery.

✅ **Decision 13 closed on 2026-08-14 and it took the candidate plus one more.** The author's call is
**Spain alone as the first route, with a cross-country route alongside it**, on the ground that a
single-country path reproduces the machinery and cannot reproduce the claim. Tier 1 is Spain, zero
credentials. Tier 2 is Spain plus UK 2014-15, two free registrations, which is the cheapest pair that
can actually execute a leave-one-country-out against the reweighted null. The full statement, including
what tier 1 cannot exercise because Spain fields one diary day per respondent, is in **OPEN
DECISIONS**. **The Data Availability statement is written from that entry and from nothing else.**

### 1E. What is not available, stated once so it is not rediscovered

* **HETUS Round 1 (2000) has no central microdata and never did.** Only aggregate tables.
* **Round 3 (2020) will not be released before 2027.**
* Therefore **Eurostat gives exactly one usable microdata round, the 2010 one.** This was a constraint
  when the plan wanted depth in time; **after decision 6 it is an alignment.** Our four national files
  *are* that round, obtained from the national series — ISTAT, ONS, INE, INSEE — because Eurostat's
  central copy needs an institutional recognition we do not hold. If Track A lands we get the same
  round for seventeen countries and nothing about the harmonisation changes.
* Worth stating plainly anyway, because "HETUS has three waves" is a sentence that appears in the
  literature and is misleading about what a researcher can actually obtain.

---

## STEP 2 — HARMONIZATION

**Status: OPEN. Specified by `RL02`.**

### 2A. The three code lists, as transcribed

* **Activity Coding List.** 10 major groups and 36 two-digit sub-divisions, **identical between the
  2008 and 2018 editions**. Third-digit codes differ: 108 in 2008, 116 in 2018. The 2000 edition is a
  genuine structural break with 144 codes and a reorganised computing and travel treatment.
  ~~**Consequence: anything spanning waves is pooled at the 2-digit level. Three-digit codes are used
  only within a wave.**~~ ✅ **Consequence after decision 6: the corpus is one wave per country and all
  four share one coding-list generation, so nothing spans the ACL 2000 break and THE `ACT` FIELD KEEPS
  ITS THREE DIGITS.** The 2-digit rule is retained only for the earlier waves used in validation. This
  is the decision that protects Step 9, whose appliance triggering needs to distinguish laundry from
  cooking from washing, and which 2-digit codes would have collapsed.
* **Location codes.** ~~10 to 19 stationary, 20 to 39 transport modes, in one field.~~ 🔴 **Retracted
  2026-08-14 by the Spanish codebook (F-ES-3): in Spain `21-29` are places, not transport, and `41` is
  public transport — above the range, and present in the delivered file.** `11 = Home` stands. **No
  step may test a location code by numeric range**; membership comes from an explicit code-by-code
  crosswalk. Step 2 decision D-S2-3.
* **Co-presence.** Not one code but **five parallel binary flags**: alone, with partner, with children,
  with other household members, with other persons. This matters directly, because paper 1 names
  co-presence handling as the source of load **over**estimation when shared activities are counted as
  independent loads, and five flags let us distinguish household from non-household presence properly.
  🔴 **Five is the shared core, not the ceiling (F-ES-2): Spain fields six.** The extra, `PADRES`
  (*with a parent*), is kept as a country-extra column and never folded into "other household
  members". Step 2 decision D-S2-2.

### 2A-bis. The file shape and the weight names, adjudicated by `RL17`

Two of the eight contradictions were about what the delivered file looks like. `RL17` resolved both,
and both resolutions are recorded here with the same caveat attached.

* **File shape (contradiction 6).** `RL17` A1 finds for `RL02`: the Eurostat HETUS 2010 SUF arrives as
  three relational files — `INDFILE` (one row per individual), `DDFILE` (one row per diary day),
  `EFILE` (one row per episode) — joined on `COUNTRY`, `YEAR`, `HID`, `PID`, `DIARY`. Crucially,
  **`EFILE` carries native `START` and `DURATION` fields**, so the run-length reconstruction from slot
  columns that we had budgeted for does not exist. `RL01`'s flat ~1,950-variable wide file is
  described as a national export produced downstream, not the Eurostat delivery.
* **Weight names (contradiction 8).** `RL17` A2 finds for `RL02`: `WGHT_IND` on `INDFILE`, `WGHT_DIA`
  on `DDFILE` and `EFILE`, `WGHT_HH` where household extracts exist. The one national variant still
  relevant to us is UKTUS 2014-15, which uses `ind_wt` and `dia_wt_a`/`dia_wt_b`. (It also gave the
  Canadian GSS names, which decision 5 has since made irrelevant.)

🔴 **Neither verdict changes what we build.** The parser still handles both file shapes, and variable
names are still resolved against the delivered file through an ingestion mapping dictionary rather
than hard-coded. A third report adjudicating between two reports is still not a file in our hands,
and the cost of being agnostic is a few hours where the cost of being wrong is discovered in month
three. If the delivered file matches `RL17`, the agnostic path costs nothing and we say so.

### 2B. 🔴 The finding that changes a building-physics assumption

**HETUS location code 11 covers the dwelling, the yard and the garden as one code.** Presence in the
*conditioned volume* is therefore not recoverable from the location field alone, which is the
assumption papers 2 and 3 were built on.

Adopted rule, from `RL02`:

```
indoor_presence = (LOC == 11) AND (ACT not in {gardening, outdoor construction, ...})
```

The exclusion list is finalised against the transcribed ACL, not guessed, and the rule is stated in the
methods section rather than buried in code. A reviewer who knows HETUS will look for it.

🔴 **Confirmed on the Spanish file and widened (F-ES-4).** METH p. 124 defines `11` as house, garage,
vegetable plot, garden or grounds attached to the dwelling, **and codes working from home as `11` as
well.** Work-at-home is indoor presence and is *not* excluded, but it means `LOC == 11` alone cannot
separate "at home, not working" from "working at home" — a distinction Step 9 needs for equipment
load, and one only the 3-digit `ACT` carries. Step 2 decision D-S2-4.

### 2C. Where countries actually diverge, and the filter it forces

| Dimension | Standard | Divergence found |
|---|---|---|
| Slot length | 10 min, 144 slots | UK 2000 used 15 min |
| Diary days per respondent | 2 (one weekday, one weekend) | Germany fielded 3; Spain and France 1998 fielded 1 |
| Minimum age | 10+ | UK 8+, France 11+ |
| Diary start hour | ~~04:00~~ 🔴 **OPEN** | **Measured: Spain runs 06:00 to 06:00, and no 04:00 day can be built from it (F-ES-1).** The 04:00 value was `RL02`'s standard, never measured |
| Fieldwork spread | 52 continuous weeks | Some early accession rounds compressed into 2 to 6 months, which distorts seasonal comparisons |
| Code depth | 3-digit ACL | Some public files collapse to 2-digit for disclosure control |

**Filter adopted:** age ≥ 11, 10-minute grid, and a per-country flag for diary-days-per-
respondent so that multi-day structure is only claimed where it exists.

🔴 **The origin clause is withdrawn, not replaced** (Step 2 decision D-S2-1, author, 2026-08-14). It
is chosen once all four codebooks are transcribed, from four measured origins. Setting it to 06:00
because Spain is the only country we have measured would be the same error as `RL02`'s 04:00, in the
other direction. Step 2 work item 2.4 is blocked until it closes. The harmonised day is 24 hours of
10-minute slots with **one origin shared by all four countries**, never a per-country field.

### 2D. The crosswalk

✅ **After decisions 5 and 6, there is no crosswalk on the critical path.** The corpus is four HETUS
members from one round sharing one coding-list generation, so the alphabet is already common — that is
what "harmonised" in HETUS means, and it is the property the paper is testing.

The earlier position is kept because it still applies where it applies. No official HETUS-to-ATUS or
HETUS-to-GSS bilateral mapping exists, and **the MTUS 69-activity frame is the bridge and the only
one.** It is now needed in exactly one place: **if the earlier waves are used for the validation
described in 1B**, since those cross the ACL 2000 break. That is a contingency again rather than
critical-path work.

---

## STEP 3 — SERIALIZATION AND TOKENIZATION

**Status: ✅ FORMAT DECIDED by `RL07`. Field semantics corrected against `RL02`. ✅ TOKENIZER DECIDED
2026-08-14 by our own measurement (3C), which also rejected `RL18`'s mnemonic remapping.**

### 3A. The measurement that settled it

`RL07` was required to return measured token counts with named tokenizers and worked example strings,
and it did. One 17-episode Italian weekday diary:

| Format | Chars | Llama 3.1 | Qwen 2.5 | Gemma 2 |
|---|---|---|---|---|
| Verbose key-value, 144 slots | 7,466 | 2,719 | 3,299 | 3,310 |
| Compact delimited, 144 slots | 1,532 | 984 | 1,276 | 1,287 |
| **Episode, minutes** | **571** | **256** | **315** | **326** |
| JSON, episodes | 2,060 | 754 | 813 | 932 |
| JSON, 144 slots | 11,476 | 4,817 | 5,287 | 6,042 |

A four-fold reduction against the best slot format, and the episode form is **how time-use data is
natively collected**, so it is not a lossy re-encoding.

> **Note added 2026-08-14.** The *format* conclusion above stands and is unaffected by anything that
> followed. The *per-tokenizer numbers* in this table are `RL07`'s and are superseded for decision
> purposes by our own measurement in 3C, which covers a different and larger set of tokenizers on our
> actual 25-episode string. Where the two disagree, ours is the one that was run.

There is a second argument that matters more than the token count. **In a 144-slot grid a single
dropped slot shifts every later slot in the day**, so one token error destroys the record. In episode
form a wrong duration changes the day's total length and leaves every other episode's semantics intact.
The failure mode is bounded rather than catastrophic.

### 3B. The adopted record

```
<conditioning prefix>  |  DUR,ACT,LOC,COP  DUR,ACT,LOC,COP  ...  <eor>
```

* `DUR` — duration in minutes, multiples of 10, and `start` is dropped because it is the running sum.
* `ACT` — 3-digit ACL code.
* `LOC` — **the real HETUS location code, not `RL07`'s invented 1 to 6.** 🔴 **Not "10 to 39":** the
  Spanish file carries `41`, public transport (F-ES-3). The serialised alphabet is whatever the Step 2
  location crosswalk emits, and it is read from that file rather than written as a range here.
* `COP` — **the five shared co-presence flags, not a single digit.** Packed form to be fixed at
  implementation; discarding four of the five flags to save tokens would throw away exactly the field
  paper 1 identified as load-bearing. **Country-extra flags (D-S2-2) are carried in the harmonised
  table but are not serialised into `COP`** — a symbol only one country can emit would leak country
  identity into a leave-one-country-out design.

* `ACT` **keeps its three digits.** Decision 6 removed the cross-wave pooling that would have forced
  2-digit codes, and the OLMo tokenizer writes a 3-digit code in one token anyway, so the resolution
  Step 9 needs costs nothing to carry.

Reversibility is exact: each episode unpacks to `DUR / 10` identical slots. Validity is
`sum(DUR) == 1440`.

### 3B-bis. 🔴 Secondary activity — kept in the data, kept out of the record, decided 2026-08-14

Spain records a secondary activity on **12.2 %** of slots (F-ES-6) and the Step 1 record had no field
for it. `act2_raw` is now carried through Steps 1 and 2 — nothing recorded is discarded — but **it is
not serialised into the episode tuple**, because coverage has been measured on one country out of
four and a field only Spain can emit would leak country identity into a leave-one-country-out design.
That is the same argument that keeps country-extra co-presence flags out of `COP`.

**The decision closes on a measurement, not on a preference:** four coverage rates in
`outputs_step3/act2_coverage.md`. All four usable, serialising becomes a token-cost question; any
country missing it, the field stays out permanently and the reason enters the limitations. Until that
file exists, **no step conditions on `act2` and no gate tests it.** Full text in Step 3, item 3.2-bis.

🔴 **Two prefix fields that are constant today and exist for tomorrow.** The conditioning prefix
carries, alongside country, demographics, season and day type:

* `MODE` — collection mode (paper self-completion for all four training waves)
* `SCHEME` — coding-list generation (ACL 2008/2010 for all four)

Both are invariant across the entire training corpus, so they teach the model nothing and cost a
handful of tokens per record. **They are there so that adding a wave, or seventeen Track A countries,
never changes the record format.** If a future corpus does mix instruments, the model has somewhere to
put the artefact instead of attributing it to behaviour — which is the mechanism Step 6D describes.

🔴 **`MODE` and `SCHEME` are not year tokens and must never be allowed to become one.** Naming the
instrument is a different act from naming the time: an instrument label cannot be extrapolated, and a
year label invites exactly the projection this paper does not make. No `YEAR` field is added, ever.

### 3C. The two traps, both now avoided by construction

🔴 **The numeric-code trap, measured by us on 2026-08-14.** Activity code 411 is a label, not a
quantity. A tokenizer that splits it into `4`,`1`,`1` spends three autoregressive steps on one
symbol and imposes a digit structure implying an ordering our data does not have.

The measurement is job `1234177`, extended by `1234199` and `1234216`. One 25-episode diary in the
adopted `DUR,ACT,LOC,COP;` form:

| Tokenizer | `311` | `45` | One episode `45,311,11,0;` | Full diary |
|---|---|---|---|---|
| **OLMo 2 / OLMo 3 (dolma2 BPE)** | **1** | **1** | **8** | **200** |
| Qwen2.5 / Qwen3 / Qwen3.5 | 3 | 2 | 12 | 303 |
| Mistral NeMo (Tekken) | 3 | 2 | 12 | 303 |
| Mistral 7B v0.3 (SentencePiece) | 4 | 3 | 13 | 304 |
| Llama 3.1, Gemma | *gated, not measured* | | | |

**The whole Qwen lineage splits digits and the OLMo tokenizer does not**, which is a 34 % difference
in sequence length for the identical string. Qwen3 and Qwen3.5 carry the same 151,936-token
vocabulary as Qwen2.5, so this is a property of the tokenizer family rather than of one ageing
checkpoint, and no newer Qwen release escapes it. **This is now a settled input to open decision 3,
and it is the input that decided it.**

🔴 **The mnemonic workaround is rejected, and the reason is worth keeping.** `RL18` proposed writing
activity codes as one-token mnemonics (`wrk`, `slp`) instead of digits, and reported that this brings
Qwen to parity at 8 tokens per episode. Measured: the mnemonic episode costs **11** tokens in Qwen,
and a full mnemonic diary costs 264 rather than 303 — a real 12.9 % saving, but not parity. On the
OLMo tokenizer we have adopted the same remapping makes diaries **longer**, 200 → 211, because it
replaces a one-token number with a two-token string. Of twenty candidate three-letter mnemonics only
eight are single tokens in any of these vocabularies. **A workaround devised for a tokenizer we are
not using was one edit away from entering the serialisation schema for one we are.**

🔴 **The added-token trap, avoided.** We add no tokens. LoRA freezes `embed_tokens` and `lm_head` by
default, so new tokens would sit at their random initialisation for the whole fine-tune, training
without error and generating nonsense. Unfreezing them via `modules_to_save` costs roughly 16.8 GB of
fp32 AdamW state on an 8B model and breaks GGUF and vLLM export. Using the base vocabulary avoids all
three problems.

### 3D. Conditioning decay, and the diagnostic that runs on the first model

Our whole claim is that demographics drive the schedule. `RL07` reports that a prefix at positions 0 to
about 50 acts as an attention sink and does not decay measurably over a few hundred tokens, which is
good news but is not evidence about *our* data. So the diagnostic runs regardless, on the first trained
model rather than at evaluation time:

1. **Shuffled-prefix test.** Score test diaries under permuted demographic prefixes. Cross-entropy must
   rise sharply. If it does not, the model is ignoring the conditioning and nothing downstream matters.
2. **Slot-wise mutual information** between conditioning attributes and generated activity, compared to
   the empirical curve, with the evening slots watched specifically. Demographically appropriate
   mornings and generic evenings is the exact failure shape.

If conditioning proves weak, classifier-free guidance at decode time is the named fallback.

---

## STEP 4 — MODEL 1: THE FINE-TUNED LLM

**Status: ✅ FAMILY DECIDED 2026-08-14 by our own measurement — `allenai/Olmo-3-1025-7B`. Recipe
✅ DECIDED by `RL05`. ✅ Pilot size decided by the author: **Leg-4** `allenai/OLMo-2-0425-1B`,
**Leg-5** `allenai/Olmo-3-1025-7B` (4B-ter).**

### 4A. 🔴 "Gemma 4" does not exist

`RL04` was asked not to confirm a version merely because the prompt named one, and it did not.

| Family | What actually exists | Licence |
|---|---|---|
| Gemma 2 | 2B, 9B, 27B | Gemma Terms of Use |
| Gemma 3 | 1B, 4B, 12B, 27B | Gemma Terms of Use |
| Qwen 2.5 | 0.5B, 1.5B, **7B**, 14B, 32B, 72B | Apache 2.0 (**except 3B**, ✅ **verified from its own `LICENSE` file**: Qwen Research License, *"FOR NON-COMMERCIAL PURPOSES ONLY"*) |
| Qwen 3 | 0.6B, 1.7B, 4B, 8B, 14B **-Base** | Apache 2.0. Absent from `RL04` and `RL18` entirely |
| Llama 3.1 | 8B, 70B, 405B | Community Licence. 🔴 **The §1.b anti-improvement clause is NOT in 3.1** — see 4B |
| Mistral | 7B v0.1/v0.3, NeMo 12.2B | Apache 2.0 (**but Ministral 3B/8B are non-commercial**) |
| **OLMo 2** | **1B**, 7B, 13B, 32B | Apache 2.0, ungated. 4,096 context at every size |
| **OLMo 3** | **7B, 32B only** | Apache 2.0, ungated. 65,536 context. **No base checkpoint below 7 B** |

There is no `gemma-2-7b`, no `gemma-3-8b`, and no Gemma 4. There is also a live trap in the Qwen family:
mixing sizes without pinning each licence file mixes licences — and that trap is real, because
`Qwen/Qwen2.5-3B` was confirmed non-commercial by reading its licence file, not by repeating `RL04`.

**Two families that `RL04` and `RL18` between them left out of the decision entirely are OLMo 3 and
Qwen 3.** One of them is now the backbone.

### 4B. ✅ The trade-off, resolved by measurement on 2026-08-14

The trade-off was licence against tokens: Apache 2.0 with long sequences, or short sequences under a
restrictive licence. **It dissolved once we stopped asking reports and started loading tokenizers.**
A family neither `RL04` nor `RL18` considered turns out to have both properties.

| Candidate | `411` | Diary | Licence | Gated | vLLM | Context | Verdict |
|---|---|---|---|---|---|---|---|
| **`allenai/Olmo-3-1025-7B`** | **1 token** | **200** | **Apache 2.0** | no | **native `olmo3`** | 65,536 | 🔴 **ADOPTED as the primary backbone** |
| `allenai/Olmo-3-1125-32B` | 1 token | 200 | Apache 2.0 | no | native `olmo3` | 65,536 | Available if a ceiling run is wanted; 32 B full FT will not fit, LoRA will |
| `allenai/OLMo-2-1124-7B` | 1 token | 200 | Apache 2.0 | no | ❌ generic fallback | 4,096 | Superseded by OLMo 3 on both counts |
| `allenai/OLMo-2-0425-1B` | 1 token | 200 | Apache 2.0 | no | ❌ generic fallback | 4,096 | 🔴 **ADOPTED as the Leg-4 pilot: same tokenizer, 1.48 B** |
| `Qwen/Qwen2.5-7B` | 3 tokens | 303 | Apache 2.0 | no | native `qwen2` | 131,072 | **Retained as the named comparison arm** |
| `Qwen/Qwen3-8B-Base` | 3 tokens | 303 | Apache 2.0 | no | native `qwen3` | 32,768 | Same tokenizer, no advantage here |
| `mistralai/Mistral-7B-v0.3` | 4 tokens | 304 | Apache 2.0 | no | — | — | Excluded on tokens |
| `meta-llama/Llama-3.1-8B` | *not measured* | — | Community | **manual** | native | 131,072 | Excluded; see below |

**Why OLMo 3 and not OLMo 2, when their tokenizers are identical.** Two reasons, both read from
source rather than inferred. `vllm/model_executor/models/registry.py` maps `Olmo2ForCausalLM` to
`("transformers", "TransformersForCausalLM")`, the generic fallback backend, while
`Olmo3ForCausalLM` maps to a native `olmo3` implementation. Our entire Step 7 generation leg is vLLM
plus XGrammar, so shipping the primary model on the fallback path would tax the most expensive stage
of the project. And OLMo 2 is 4,096 context at **every** size, which caps sequence packing at about
thirteen diaries where OLMo 3's 65,536 (with a 4,096 sliding window) allows far more.

XGrammar is not a constraint on this choice: it derives its vocabulary type (`RAW`,
`BYTE_FALLBACK`, `BYTE_LEVEL`) from the vocabulary itself and is model-agnostic.

### 4B-bis. 🔴 The Llama exclusion was written on a clause that does not exist in Llama 3.1

Every version of this document has said that Llama is disqualified because *"§1.b forbids using
Llama outputs to improve any other non-Llama language model"*, sourced to `RL04` and restated by
`RL18` B08 as a Tier-1 fact. **Job `1234219` fetched and read Meta's licence files. That sentence is
not in the Llama 3.1 licence.**

What Llama 3.1 §1.b.i actually says:

> *"If you use the Llama Materials or any outputs or results of the Llama Materials to create, train,
> fine tune, or otherwise improve an AI model, which is distributed or made available, you shall also
> include 'Llama' at the beginning of any such AI model name."*

A **naming requirement**, not a prohibition. The prohibition is real but belongs to earlier versions:
Llama 2 §1.b.v and Llama 3 §1.b.v both read *"You will not use the Llama Materials or any output or
results of the Llama Materials to improve any other large language model."* Meta dropped it at 3.1
and it is absent from 3.2 and 3.3 as well. Exact occurrences of the string `improve any other large
language model`: **Llama 2 → 1, Llama 3 → 1, Llama 3.1 → 0, Llama 3.2 → 0, Llama 3.3 → 0.**

**Llama is still not selected, and the reasons are now ones we can defend:**

1. The tokenizer advantage that was its entire case is matched by OLMo 3 at 200 tokens per diary,
   under Apache 2.0. We are no longer trading a licence for a tokenizer, so the question of how
   restrictive that licence is has become moot rather than decisive.
2. Llama 3.1 still attaches a naming condition, an attribution requirement, and an Acceptable Use
   Policy incorporated by reference to anything built downstream from its outputs. Apache 2.0
   attaches nothing. For a corpus released as unconditional CC BY 4.0, the licence that attaches
   nothing is the correct one — and that argument rests on the clause that is actually there.
3. The repository is manually gated, which is why we could not load its tokenizer. 🔴 **We have
   therefore never verified the "Llama writes `411` in one token" claim ourselves.** `RL07`, `RL17`
   and `RL18` all assert it; it is not our measurement and it is not labelled as one.

Recorded at length rather than quietly fixed, for one reason: this was a **factual assertion about a
third party's legal document**, carried in a plan for a manuscript, sourced to a report, and wrong.
Everything else the vetting caught was a threshold or a citation.

### 4B-ter. 🔴 What the switch costs, and the one thing it costs is the pilot

Nothing about this choice is free, and two costs are named here rather than discovered later.

**1. There is no OLMo 3 base checkpoint below 7 B.** The Hugging Face API returns 31 OLMo 3
repositories and exactly two are base models: `Olmo-3-1025-7B` and `Olmo-3-1125-32B`. Everything else
is Instruct, Think, SFT, DPO or RL-Zero, none of which we can use — `RL05` is explicit that alignment
suppresses tail entropy and pulls toward modal output, which is the failure Tier 2 exists to catch.
Qwen offers 0.5B and 1.5B; OLMo 3 offers nothing.

This matters because the author asked for the 3J staging pattern — a cheap pilot leg before the
reported leg, as Leg-2 preceded Leg-3.

✅ **DECIDED BY THE AUTHOR, 2026-08-14. The leg numbering continues the series: 3J ended at Leg-3, so
4J is Leg-4 and Leg-5.** These names are used from here on and replace the "Leg 1 / Leg 2" wording of
the `L18` prompt, which was written before the numbering was fixed.

| Leg | Model | Why |
|---|---|---|
| **Leg-4, pilot** | `allenai/OLMo-2-0425-1B` (1.48 B, Apache 2.0, ungated) | **Byte-identical tokenizer and vocabulary to Leg-5.** The serialisation, the grammar, the tally automaton and the data files are all tokenizer-bound, so they transfer to Leg-5 unchanged — the training data does not have to be regenerated between legs. The architecture and the 4,096 context differ, and that is the honest cost |
| **Leg-5, reported** | `allenai/Olmo-3-1025-7B` (7.30 B) | The measured backbone. This is the model the paper reports |

The alternative is `Qwen2.5-0.5B` → `Qwen2.5-7B`, which keeps one architecture across both legs but
pays 50 % more tokens on every run, forever. A pilot exists to shake out the pipeline, and the
pipeline is tokenizer-shaped.

🔴 **Two things Leg-4 cannot tell us, stated now so they are not read off it later.** Its 4,096
context caps sequence packing, so **throughput numbers from Leg-4 do not extrapolate to Leg-5**. And
it runs on vLLM's generic Transformers fallback rather than a native kernel, so **generation-speed
numbers from Leg-4 are not Leg-5's either**. Leg-4 validates correctness — does the grammar hold, do
the gates fire, does the conditioning bite — and nothing about performance. The vLLM throughput
comparison in 4B-ter is run on Leg-5 checkpoints, not on the pilot.

**2. 🔴 OLMo 3 7B has no grouped-query attention, and Qwen does.** Read from the configs:
`Olmo-3-1025-7B` reports 32 attention heads and **32 key-value heads**, while `Qwen2.5-7B` reports 28
and **4**. Head dimension is 128 in both. The KV cache per token is therefore
`2 x layers x kv_heads x head_dim x 2 bytes`:

* `Olmo-3-1025-7B`: 2 × 32 × 32 × 128 × 2 = **512 KB per token**
* `Qwen2.5-7B`: 2 × 28 × 4 × 128 × 2 = **56 KB per token**

**About nine times more KV cache per token**, against which our 34 % token saving buys back only part
— roughly a six-fold disadvantage in KV memory for the same diary. Step 7 generates on the order of
10⁵ to 10⁶ diaries, where KV cache is what limits vLLM's concurrent batch size, so **this is a
throughput question and not a rounding error.** `Olmo-3-1125-32B` does use GQA (8 KV heads), which is
the usual pattern of a family adding GQA only at the larger size.

*This is arithmetic from measured config values, not a benchmark.* **Action: before the Step 7
campaign is sized, run one vLLM throughput comparison — `Olmo-3-1025-7B` against `Qwen2.5-7B`, same
grammar, same batch, diaries per second — and record it.** The training-side argument for OLMo 3 is
settled; the generation-side argument is not, and if throughput turns out to dominate, the comparison
arm and the primary can swap without any of the serialisation work being wasted.

### 4C. The recipe, decided

From `RL05`, and the parts that are decisions rather than defaults are marked.

* **Base checkpoint, not instruct.** RLHF and DPO alignment suppresses tail entropy and pulls toward
  modal output, which is precisely the failure we are most afraid of. **This is now an argument, not a
  preference.**
* **Supervised fine-tuning with completion-only loss masking.** The prefix is about 25 tokens and the
  body is 200 to 500, so computing loss on static demographic keys wastes capacity. Not continued
  pretraining; not chat-formatted instruction tuning.
* **rsLoRA, r = 32, on all linear layers** (`q,k,v,o,gate,up,down`). Attention-only LoRA underfits.
  Rank-stabilised scaling because plain α/r scaling slows learning above r = 32.
* **Full fine-tuning with 8-bit AdamW as the ceiling run.** `RL05` is explicit that LoRA underfits when
  the target is far from the pretraining distribution, and our target is about as far as it gets. At
  roughly 41 to 49 GB it fits on the A100, so **this is a measurement we can afford and therefore must
  make.**
* **QLoRA rejected.** We have 80 GB; 4-bit buys nothing and adds quantisation noise. Note that the
  quantitative degradation figure `RL05` gives rests partly on an unverifiable source, so we reject
  QLoRA for sufficiency rather than claiming a measured penalty.
* **Packed sequences with block-diagonal attention masks**, which removes about 60 % padding waste
  without cross-contamination between diaries.
* **bf16.** V100 and P6 nodes have no hardware bf16 and would need fp16 with a grad scaler, which is a
  reason to stay on the A100 and RTX 6000 queues.

> 🔴 **The memory arithmetic in `RL18` is for Qwen2.5-7B and does not transfer unchecked.** It gives
> 18.27 GB for LoRA and 48.86 GB for full fine-tuning with 8-bit AdamW. `Olmo-3-1025-7B` is 7.30 B
> parameters against Qwen's 7.62 B, so the weight and optimizer terms are slightly smaller — but it
> has **no grouped-query attention** (32 KV heads against Qwen's 4, see 4B-ter), so the activation
> and cache terms are much larger, and sliding-window attention changes the shape again. Both still
> fit in an 80 GB slice with room to spare, which is the conclusion that matters. **The specific
> numbers are re-derived on the actual model before the first sweep is sized, not copied.**

### 4D. 🔴 Multi-country training: joint, never sequential

Fine-tuning country by country degrades earlier countries by 40 to 70 %. **One joint model with a
country token in the prefix.** Per-country adapters over a shared base are the comparison arm, not the
primary. This also removes most of the forgetting gate in Tier 4 by construction, which is the right way
to pass a gate.

### 4D-bis. 🔴 Step 4 is ten training jobs, and the ceiling run sits on one pre-named fold

Decision 11 holds every country out in turn, so **a fold is a separate model** and this step's unit of
work is the fold. The step document was written for one Leg-5 run and is corrected 2026-08-14.

| Run | Leg | Count |
|---|---|---|
| Primary, rsLoRA r=32 all linear | Leg-4 **and** Leg-5 | **4 each**, one per held-out country |
| Ceiling, full fine-tune with 8-bit AdamW | Leg-5 | **1**, pre-named fold |
| Comparison arm, `Qwen/Qwen2.5-7B` | Leg-5 | **1**, same pre-named fold |

**Author decision, 2026-08-14: the ceiling run and the comparison arm are single-fold.** The ceiling
answers one question — does LoRA underfit a target this far from the pretraining distribution — and one
measurement settles it. **Six Leg-5 jobs, four Leg-4 jobs.**

🔴 **Naming that fold is a new opportunity to choose late, and it is closed the same way decision 11
was.** ✅ **The fold is held-out SPAIN, confirmed by the author 2026-08-14**, by a rule fixed in advance
— alphabetical ISO code — and taken **while no fold had been trained and no result existed**. It goes
into `Step6_docs/outputs_step6/prereg.md` and freezes with it before the first Leg-5 submission; no
change after that. Choosing it afterwards would let the full fine-tune be pointed at whichever fold the
primary run did worst on, which is selecting on the outcome.

**A deadline that was missing:** `prereg.md` is frozen before the first *training submission*, not
merely before Step 6 scores anything. Once a model exists, a pre-registration written afterwards is a
description of it. New gate **G4.14** carries its md5 in every run manifest; new gate **G4.13** asserts,
from the shard the trainer actually loaded, that the held-out country contributed **zero** records.

### 4E. Hardware, measured

Queried on Speed on **2026-08-13** with `sinfo -N -o '%N|%P|%f|%G|%m|%T'`. Not an estimate.

| Nodes | Partitions | GPU | Inventory per node | Node RAM |
|---|---|---|---|---|
| `speed-37`, `speed-39` to `speed-43` | `ps`, `pt`, `cl` | **A100, MIG-partitioned** | `nvidia_a100_7g.80gb` x1, `nvidia_a100_2g.20gb` x9, `nvidia_a100_1g.20gb` x3 | 980 GB |
| `xailab` | `ps`, `cl`, `xi` | RTX 6000, 48 GB | x4 | 772 GB |
| `nebulae` | `pt`, `cl`, `pn` | RTX 6000, 48 GB | x2 | 515 GB |
| `antenna3` | `ps`, `cl`, `em` | RTX 6000, 48 GB | x1 | 1030 GB |
| `speed-03`, `speed-25`, `speed-27` | `pg`, `pa`, `pt`, `cl` | V100, 32 GB | x2 | 256 GB |
| `speed-01`, `speed-05`, `speed-17` | `pg`, `pa`, `p6`, `pi`, `cl` | Tesla P6, 16 GB | x6 | 256 to 515 GB |
| `cisr-1`, `cisr-2` | `pg`, `cr`, `cl` | A2, 16 GB | x1 | 257 GB |

Against the memory arithmetic in `RL04` and `RL05`: LoRA on a 7 to 9 B model peaks around 18 to 22 GB,
full fine-tuning with 8-bit AdamW around 41 to 49 GB. **Both fit in one 80 GB slice**, and the 20 GB
slices carry the hyperparameter sweeps and the leave-one-country-out array. Large slot for training,
small slots for sweeps.

### 4F. Cluster engineering, from `RL11`, with two corrections we impose

`RL11` returned a complete SLURM template. Two things in it are wrong for us:

1. 🔴 **It calls `srun` inside the batch script and requests `--time=24:00:00`.** Our standing rules are
   that every job requests the full seven days (`-t 7-00:00:00`) and that we do not add `srun` where a
   plain command works. The template is used with `srun` removed and the walltime raised.
2. **Partition names `pt`, `pn`, `pg` are asserted, and our own measurement saw `ps`, `pt`, `cl` on the
   A100 nodes.** Confirmed with `sinfo` before the first submission, which is a permitted login-node
   command.

What is adopted unchanged, because it is specific and checkable:

* **No distributed training across MIG slices.** There is no peer-to-peer path between slices of one
  physical GPU. One instance, one job.
* 🔴 **Never request multi-GPU on the Tesla P6 nodes** (`speed-01`, `speed-05`, `speed-17`). `RL11`
  reports that `DataParallel` there crashes the physical node.
* **Training runs offline.** `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HOME` and `TORCH_HOME`
  on `/speed-scratch`, weights pre-staged. The default cache location will blow the home quota.
  🔴 **Corrected 2026-08-14: compute nodes on `ps` DO have outbound network.** This line said they did
  not. Jobs 1234176, 1234177, 1234192 and 1234199 ran `pip install` and pulled from Hugging Face from
  inside `sbatch`, and job **1245620** stages the three checkpoints the same way. **Offline is a
  discipline imposed on training runs, not a property of the node** — and the wrong version of this
  sentence implied the weights had to come down on the login node, which the top rule forbids.
* **Singularity, not Conda on NFS.** A Conda tree is hundreds of thousands of small files on a network
  filesystem.
* **`--signal=B:SIGUSR1@600`** with a checkpoint-and-exit handler, plus periodic stateful checkpoints
  including optimizer, scheduler, RNG and sampler position. Even though a run fits in the walltime, a
  node failure at hour 20 otherwise costs the whole run.
* **`/speed-scratch` purges after 90 days.** Final artefacts get copied off.

### 4G. Failure modes, instrumented from the first run

Each needs a detector that fires **within one training run**, not at evaluation:

1. **Low loss, degenerate output.** Delimiters are most of the sequence, so loss can fall while the
   content collapses. Detector: log validation perplexity **separately for delimiter tokens and for
   activity-code tokens**, and log the entropy of generated activity sequences. `RL05` proposes an
   automatic halt if delimiter loss is under 0.05 while activity entropy falls below 1.5 nats.
2. 🔴 **Distribution collapse.** Within-stratum variance ratio against real data, logged as a training
   metric every validation epoch. **This is the failure that would silently destroy the paper.**
3. **Catastrophic forgetting.** Largely designed out by joint training; a fixed probe set per country is
   still scored at every checkpoint.
4. **Template or tokenizer mismatch.** Assert `tokenize(detokenize(ids)) == ids` on 1,000 cases before
   any large generation run.
5. **Training on padding.** Assert every pad and prompt position carries label `-100`.
6. **Adapter merge drift.** Score merged and unmerged on the same fixed sample; require max logit
   difference under 1e-4.
7. **Missing EOS.** Assert 100 % of training completions terminate properly, or generation never stops.

> The shape of these is inherited: the 3J wiring gate exists because a Leg-2 bug passed every
> input-side check and was only caught output-side. **Instrument the output, not the intent.**

---

## STEP 5 — CONDITIONING AND POPULATION LINKAGE

**Status: ✅ DECIDED by `RL09`.**

### 5A. Two stages, and the separation is now argued rather than merely tidy

```
 census marginals for the place  (Eurostat Census Hub / GEOSTAT 1 km grid / national small-area)
        |
        v
 (a) synthetic population        <- IPF or combinatorial optimisation
        |                           exact on demographics, and a literature reviewers already trust
        v
 (b) one diary per synthetic person   <- the fine-tuned LLM
```

Having the model emit person and diary jointly would let it hallucinate demographic proportions, and it
compounds two claims into one a reviewer can reject wholesale. Separated, a reviewer who doubts the
population synthesis can still accept the diary generation.

### 5B. 🔴 Training loss is unweighted, and this is the counter-intuitive one

Survey statistics says to use pseudo-maximum-likelihood with design weights. Deep learning says
importance weighting in an overparameterised network inflates gradient variance and does not move the
decision boundary. **`RL09` resolves it rather than picking a side:** because the conditioning prefix
contains the design strata (country, age, sex, household type, economic status, day type, season), the
sampling mechanism is *conditionally ignorable* for `P(diary | X)`. Representativeness is therefore
enforced in stage (a), where IPF makes it exact, and not in the loss, where it would only add variance.

This also removes a double-counting bug we would otherwise have shipped: HETUS diary weights already
carry a weekday-weekend adjustment, and multiplying the loss by them **while** using stratified batching
applies that correction twice.

### 5C. 🔴 We do not rake our own output

Raking adjusts univariate margins and cannot reconstruct distorted multi-way interactions. Since stage
(a) already makes demographics exact, raking the diaries afterwards would only paper over a model that
failed. **Raking appears in this project in exactly one place: building the null model in Step 6.** We
do not get to use the trick we are benchmarked against.

### 5D. Decoding temperature as a calibration instrument, and the tail hazard

Paper 1 exposes argmax, probabilistic and temperature-plus-top-k sampling and reports argmax is too
uniform at neighbourhood scale. The sharper question here is whether a temperature exists at which the
generated population's entropy matches the real population's, and whether it is the same temperature
that optimises the fidelity metrics.

🔴 **The hazard is tail loss, and `RL09` states it in our own terms.** Top-k and top-p truncation
systematically delete rare behaviour, and rare behaviour is where the interesting loads live: the
household running laundry at 03:00, the shift worker, the early-morning vehicle charge. Those are the
cases a peak-demand study exists to capture. **So: validation-set temperature scaling plus the grammar
mask, and no aggressive truncation.** If top-p is used at all, p ≤ 0.98.

---

## STEP 6 — TRANSFER

**Status: OPEN. Null model hardened by `RL06` and adopted as the objective. Longitudinal axis removed
from scope by author decision 2026-08-14.**

### 6A. Leave-one-country-out, with a harder null than we pre-registered

Train on N-1 countries. Generate a population for the held-out country conditioned **only on its
published demographic marginals**, with none of its diaries seen.

🔴 **N = 3 after author decision 16, 2026-08-15, so training is on TWO.** Italy, Spain, UK — one held
out and two in. **France is excluded from the corpus; see decision 16 in the progress log.** That is
thinner than the four-country design it replaces, it is named as limitation C4, and **Track A is the
only thing that raises it** — to seventeen, with no harmonisation change, because our three waves are
part of the HETUS 2010 round. Until then the claim is stated at the scale the corpus supports rather
than at the scale we would like.

🔴 **Two-in-one-out is the floor of what this test can be, and the paper says so.** With N = 3 the
leave-one-country-out claim is *"a model trained on two European time-use corpora generates a third it
has never seen"* — still a real test of paper 1's untested sentence, still falsifiable against the
hardened null, and **not** the framework-scale claim the four-country design would have carried.

*Superseded, kept because the reasoning is the reusable part: "N = 4 after decision 5, so training is
on three. Italy, Spain, UK, France, one held out and three in."* Score against its published aggregate
tables (`tus_00age`, `tus_00educ`, `tus_00selfstat`, `tus_00hh`, and `tus_20startime` for the
time-of-day curve).

🔴 **The null changed, and we adopted the harder one.**

| Null | Strength | Role |
|---|---|---|
| Pooled all-country average diary | weak | secondary, reported |
| Nearest-neighbouring-country model | moderate | secondary, and it answers the geographic-proxy objection |
| **Real diaries from the N-1 pool, raked by IPF to the held-out country's published marginals** | **strongest** | 🔴 **the pre-registered bar** |

Every raked donor is an authentic human day with perfect grammar, real transitions and real variance.
`RL06` states it plainly: if the fine-tuned LLM cannot beat a demographically raked pool of real
European donors on the held-out country, the transfer claim fails.

🔴 **Author's decision 2026-08-14: this is the objective of the paper, and it is stated as such in the
introduction.** Not disclosed in the evaluation section, not framed as a robustness check. The sentence
the paper has to earn is roughly: *can a model that has never seen a country's diaries produce a
population for it that is closer to the truth than reweighted real diaries from its neighbours?*

Two reasons to announce it up front rather than report it at the end. First, a bar set in advance and
then cleared is worth more than one chosen after the results are in, and reviewers can tell the
difference. Second, it makes the paper falsifiable in one sentence, which is the strongest position an
empirical claim can be in.

### 6B. The three reviewer attacks on transfer, each with its counter-measure

Written now, because each requires an experiment rather than a paragraph.

1. **Contamination.** "The model already read about that country on the web." *Counter:* condition on a
   **fictional country token with perturbed marginals** and verify the output follows the conditioning
   vector rather than a memorised national stereotype. This is also the cleanest test of the `RL04`
   cultural-asymmetry confound.
2. **The marginal-matching illusion.** "It just echoes the marginals you gave it." *Counter:* score
   **joint** structure that was never in the prompt — co-presence cross-tabulations, transition entropy,
   dwell-time distributions conditioned on pairs of attributes.
3. **Geographic proximity.** "It mapped the held-out country to its neighbour." *Counter:* the
   nearest-neighbour-country null, reported alongside the headline.

### 6C. 🔴 There is no forecast in this paper, and that is a decision rather than a defeat

**Author's decision, 2026-08-14: forecasting is out of scope.** Not deferred to a later paper, not
attempted and reported as inconclusive. Absent. There is no year token, no projection, no scenario
lever, no 2030.

`RL16` had independently concluded the data could not carry a forecast — one usable Eurostat round, an
unseen `<YEAR_2030>` token being out-of-distribution noise, and coding-list revisions that read exactly
like behavioural trends. So the decision and the evidence agree, but they are not the same thing, and
the decision is the load-bearing one: **the contribution of this paper is the method of applying a
fine-tuned language model across the HETUS and wider time-use framework.** That is a contribution on its
own terms. It does not need a projection attached to it to be one.

**Why removing it makes the paper stronger, not thinner.** Papers 2 and 3 both ended in a projection
and it worked there: four cycles from one country, one consistent instrument, a defensible trend. Here
the equivalent would have been a weakly-supported forecast bolted onto a strong methodological claim,
and a reviewer would have gone straight for it. A paper with one claim it can defend completely beats a
paper with two claims where the second undermines the first.

**What happens to the waves, then.** 🔴 **Updated by decision 6 on 2026-08-14: they leave the training
corpus altogether.** One wave per country, and the earlier waves keep exactly one role:

* ~~**Training data.**~~ **No.** Pooling instruments would teach the model the questionnaire. See 1A-bis.
* ~~**A possible second held-out axis** (leave-one-*wave*-out).~~ **Dropped.** `RL17` B4 points out it
  is a weaker second test than we assumed, because temporal transfer was already demonstrated in paper
  3, and it would have required exactly the cross-instrument pooling decision 6 exists to avoid.
* **Held-out validation, and nothing else.** A model trained on the 2009-2015 round can be asked
  whether it still resembles the same country a decade earlier once known instrument differences are
  accounted for. Informative if it fails; **not claimed as a temporal result if it succeeds.**
* **Never a trend to extend.** No between-wave difference is reported as a temporal finding.

The Kitagawa-Oaxaca-Blinder decomposition that `RL16` recommended is therefore **not in this paper
either**. It was the strongest available *temporal* formulation, and there is no longer a temporal
claim for it to be the strongest form of. It is recorded here as the obvious content of a later paper,
if a multi-wave corpus is ever assembled and turns out to be worth one. **This paper does not assemble
one.**

### 6D. The pandemic, and the mode change hiding underneath it

Round 3 fieldwork straddles COVID unevenly: Finland ran September 2020 to September 2021, the UK across
2020 and 2021, Austria 2021 to 2022, while Germany postponed to 2022 and France and Spain to 2024-2025.
Lockdown diaries are flagged as a **crisis regime** and never used as a trend anchor.

🔴 **And there is a second effect underneath the first.** The recent waves also move from paper booklets
to web and app diaries, which capture more short fragments and fewer secondary activities. **A mode
effect and a pandemic effect are confounded inside the same wave.**

Since the forecast is gone, this no longer threatens a trend claim. It threatened the **pooling**
decision instead — and ✅ **decision 6 resolved it by taking the first of the three candidate
responses.** Those candidates were: pool only within a collection mode; condition explicitly on wave;
or drop the affected waves. **We pool within a collection mode, and the four training waves are all
paper self-completion.** Every COVID-era and app-era wave — UK 2020-21, Spain 2024-25, Italy 2022-23 —
is outside the training corpus by construction.

`RL17` Part B2 supplied the mode-switch dates that made this choosable, and the answer it enabled is
stronger than the compromise it recommended. Note that the second candidate, conditioning on wave, was
**not** taken: `RL17` warns that a `WAVE_YEAR` field risks memorising instrumentation, and it would
have reintroduced a time axis. What Step 3B carries instead is `MODE` and `SCHEME` — the instrument
named directly, constant across this corpus, and impossible to extrapolate.

---

## STEP 7 — CONSTRAINED GENERATION AT SCALE, AND SCHEDULE PRODUCTION

**Status: OPEN. Mechanism decided by `RL12`.**

### 7A. The episodes-versus-slots conflict, and why episodes still win

`RL12` argues for fixed 48 or 144 slots because a grammar cannot enforce an unbounded arithmetic sum,
and `sum(DUR) == 1440` looks like exactly that. `RL07` argues for episodes on a measured four-fold token
saving.

**Episodes win, and `RL12` supplies the reason in its own text.** The sum is neither unbounded nor
continuous: durations are multiples of 10 minutes and the total is fixed at 1440, so the running total
takes 145 distinct values. **A 145-state tally automaton is finite, therefore the constraint is regular,
therefore it is enforceable by the same FSM machinery.** We keep the token saving and the hard
guarantee. This is written down because it is the kind of resolution that looks obvious afterwards and
is expensive to rediscover.

### 7B. Structure is guaranteed, not encouraged

One percent malformed at one million records is ten thousand broken records, and **silently discarding
them biases the population toward whatever the model finds easy** — the same class of error as choosing
a threshold that makes a gate pass.

* **Engine: vLLM with XGrammar**, at under about 8 % latency overhead. Not a naive `LogitsProcessor` and
  not early Outlines, which `RL12` puts at 50 to 200 %. A hand-written processor is kept as a unit-test
  oracle only.
* 🔴 **The backbone must have a native vLLM kernel, and this became a selection criterion.** Read from
  `vllm/model_executor/models/registry.py` on 2026-08-14: `Olmo3ForCausalLM` and `Qwen2ForCausalLM`
  and `Qwen3ForCausalLM` map to native implementations, while `Olmo2ForCausalLM` and `OlmoForCausalLM`
  map to `("transformers", "TransformersForCausalLM")` — the generic fallback. A model on the fallback
  path still runs, but it runs the most expensive stage of this project on the slower path. This is
  the single reason the backbone is OLMo 3 rather than the OLMo 2 checkpoint that first looked best.
* **XGrammar imposes no constraint on the model choice.** It detects vocabulary type (`RAW`,
  `BYTE_FALLBACK`, `BYTE_LEVEL`) from the vocabulary itself, so it constrains any of the candidates.
  Checked in `python/xgrammar/tokenizer_info.py`, not assumed.
* **Constraints encoded:** the duration tally; vocabulary membership; transition legality (no workplace
  to home without an intervening travel episode); and household-consistent co-presence via a small set
  of pre-compiled grammar variants indexed by household type, so nothing is compiled per sample.

### 7C. 🔴 Report the constraint-firing rate, and report it per stratum

100 % validity after masking is a property of the **decoder**, not of the model. The metric that
measures the model is how often the mask had to intervene.

* Reported for three models: untuned base (expect a high rate, over 35 %, or the constraint is not doing
  anything), fine-tuned unconstrained, fine-tuned constrained.
* **Broken down by demographic stratum**, because a firing rate concentrated in minority strata means
  the mask is doing the most work exactly where the model is weakest, and that biases those strata.
* Alongside it, the **unconstrained well-formedness rate**, which is the honest model-quality number.

Masking renormalises probability over the allowed set, which is not neutral. Audited by generating an
unconstrained rejection-sampled control batch and confirming the constrained batch's marginals have not
moved.

### 7D. Diaries to schedules

* Presence fraction per slot per dwelling, from location codes **with the code-11 indoor rule from Step
  2B applied**.
* Activity-resolved internal gains, which is the part a presence fraction throws away.
* **`Schedule:File`, not `Schedule:Compact`.** At urban scale, compact blocks bloat the IDF past twenty
  thousand lines per schedule.
* 🔴 **`Interpolate to Timestep = No`.** A step-wise presence signal interpolated linearly is no longer
  the signal we generated: it invents fractional occupants and smears appliance peaks. Inherited from
  3J, and `RL13` confirms it independently.
* Occupant count from household size via the `People` object, modulated by a 0 to 1 presence schedule.
* Residential **replaces** the baseline schedule, per the papers 2 and 3 convention.

### 7E. 🔴 The gap `RL17` Part D found: how 365 days become one year

**Nothing in this plan says how a household's 8,760 hours are assembled from generated days**, and
the two obvious rules are wrong in opposite directions. Drawing an independent diary for each day
assumes an occupant with no habits, which washes out individual variance and **damps** coincident
peaks. Repeating one generated weekday 250 times introduces no day-to-day entropy at all and
**exaggerates** them. Real people wake at 06:45 most weekdays and not at a fresh random time each
morning.

This is a schedule-assembly convention, not a modelling result, and it sits between our output and
every number in Steps 8 and 9. **The experiment, before the Step 8 campaign is designed:** 100
households, one archetype, three chaining rules — independent daily resampling, static repetition,
and Markovian habit-coupled resampling — compared on annual peak electrical power and on heating and
cooling ramp rates. **If peak demand moves by more than about 25 % between rules, the chaining method
dominates the downstream result regardless of transfer quality**, and Step 8 would be measuring our
convention rather than the model. That is the same shape of error as the uninjected-control lesson in
8D, arriving from a direction nobody had looked in.

---

## STEP 8 — BEM/UBEM SIMULATION

**Status: OPEN. Scoped by `RL13`.**

### 8A. 🔴 There is no European DOE prototype library, and that is new scope

`RL13`'s most consequential finding. Unlike the US, there is **no official library of European
residential EnergyPlus models**. TABULA and EPISCOPE distribute parameter tables, Excel workbooks and
national typology brochures: U-values, geometry parameters, construction periods, HVAC efficiencies. Not
simulation-ready models.

**So we build the archetype IDFs ourselves**, from TABULA Italy parameters via OpenStudio, or generated
through TEASER. Three to five days, it is on the critical path, and it was not in the original scope.
It also becomes limitation F2: the envelope models are our construction and carry our uncertainty.

### 8B. 🔴 The baseline we benchmark against changed, and for a good reason

The plan was to benchmark generated schedules against the EN 16798-1 Annex C default residential
schedule. **`RL13` could not open EN 16798-1, said so, and did not reconstruct it.** That is the
negative control working exactly as intended, and it is worth more than a plausible-looking table would
have been.

So the foil becomes the **open** one that national regulation actually mandates: ISO 13790 Annex G Table
G.12 and Italy's UNI/TS 11300-1, both of which specify a **flat continuous 4.0 W/m² internal gain**.

This is a better foil. A flat continuous gain is precisely what an activity-resolved diary should beat,
and it is what a practising European energy modeller actually uses. If the standard's own text is
needed later, it is bought through the library, not reconstructed.

### 8C. The campaign, and the probes that come first

Campaign axes: country by construction period by day type by scenario.

🔴 **Two mandatory probes before any campaign cell**, both inherited from Leg-2 and Leg-3 at real cost:

1. **Scenario differentiation.** Byte-identical outputs across scenarios is an automatic FAIL. The Leg-2
   People-field bug passed every input-side check and was only visible output-side.
2. **Stale-output guard.** A wiring fix invalidates prior completions, so any skip-if-done logic must be
   invalidated with it.

### 8D. The uninjected control runs first

🔴 **The single most expensive lesson of 3J.** The office EUI gate failed, and eight simulation
campaigns were spent before it was traced out of the occupancy model entirely: the **uninjected** control
run, with no schedules applied at all, already sat below the band floor (85.45 against a floor of 100).
A gate that no untreated control can pass is measuring the band, not the model.

So: **run the uninjected control before any injected cell**, in every archetype and climate, and record
where it sits relative to every band. If a band fails on the control, that band is reported as a
band-applicability limitation and its value is **not moved to make it pass**.

### 8E. Why the downstream result will matter

Published European stock studies put the sensitivity at **15 to 50 % on annual space heating demand**
and **100 to 300 % on dwelling peak electrical demand** when static standard schedules are replaced by
stochastic occupant profiles. That is the size of the effect this paper is manipulating, and it is why
the building-science half is not decorative.

---

## STEP 9 — ACTIVITY-DRIVEN END-USE LOADS

**Status: OPEN. Sourced by `RL13`.**

This step is the answer to "why generate 145 activity classes when a building model needs a presence
fraction". A diary says **what people are doing**, and that is the signal a presence fraction discards.

### 9A. 🔴 Do not invent the mapping

The strongest single instruction to come out of `RL13`. A validated lineage already exists: **CREST**
(Richardson et al., 2010), **Widén et al.** (2009), **LoadProfileGenerator** (Pflugradt, 2016) and
**RAMP** (Lombardi et al., 2020), several of them open source. The mechanism is a two-stage stochastic
trigger: an active time-use code fires an appliance with probability `P(appliance | activity)`, then a
rated power curve and cycle duration run to completion.

**We adapt that logic to the HETUS ACL. We do not author a new heuristic.** An ad-hoc mapping is the
single easiest thing in this paper for a reviewer to reject, and inventing one when four validated ones
exist would be indefensible.

### 9B. Domestic hot water

The load that matters most in a well-insulated dwelling, and 3J found the DHW plant load-bearing in its
energy result. The Jordan and Vajen four-event tapping model (short, medium, bath, shower) is the
standard, at roughly 30 to 50 L/person/day at 60 °C. Activity codes for washing, showering, food
preparation and laundry are the drivers.

### 9C. 🔴 The validation-scale catch, which bounds the whole downstream claim

The published activity-to-load models validate against **aggregate** demand: 100 to 500 dwellings, feeder
or district scale, R² above 0.90. Individual single-dwelling prediction has high residual variance,
because when one specific person runs the washing machine is irreducibly stochastic.

**Therefore the downstream claim is about load shapes and distributions across a stock, never about
predicting one household's day.** Every mapping is labelled VALIDATED or NOT VALIDATED with the scale at
which it was validated. An unvalidated mapping is a caveat, not a method.

### 9D. 🔴 The secondary-activity field this step was promised and does not receive. Resolved 2026-08-14

3B-bis keeps `act2_raw` in the corpus and names **Step 9** as the reason: an appliance triggered by an
activity that is only ever *secondary* — a television on while eating, a washing machine running while
the respondent does something else — is exactly the load paper 1 got wrong by construction.

🔴 **But Step 9 does not consume the real corpus. It consumes Step 7's generated diaries, and those
carry no secondary activity**, because `act2` is not serialised into the episode tuple. The two
sections were consistent about keeping the field and inconsistent about who receives it, and the gap is
invisible in code: **a trigger that reads an absent column does not fail, it just never fires.**

**Resolution.** The trigger fires from the **primary** code alone, on generated and real diaries alike
— which is also what CREST, Widén, LPG and RAMP do, so adapting their logic unchanged is the
conservative reading of "do not invent the mapping". `act2` enters this step in exactly one place, as a
**calibration input**: `P(appliance | primary activity)` is estimated on the real corpus with secondary
activity visible, so appliance use respondents recorded as secondary is absorbed into the trigger
probability instead of dropped. New gate **G9.14** asserts the trigger's runtime columns are a subset
of what `generated_<country>.parquet` actually contains, and that `act2` is not among them.

**The cost, stated rather than assumed:** a load whose activity is *always* secondary and never primary
for anyone is invisible to the generated path, and calibration recovers its rate but never its timing.
That belongs in the methods beside limitation E1.

🔴 **If all four coverage rates come back usable and Step 3 serialises `act2` after all, that decision
has to be taken before the corpus is emitted.** Adding a fifth tuple element afterwards invalidates the
corpus, the grammar and every trained fold.

---

## VALIDATION PLAN

The gate tables live in the overview document and are reproduced nowhere else, deliberately: two copies
of a gate table drift apart, and the drifted one is always the one a reviewer reads.

Four properties the plan must have. The first three carry over from papers 2 and 3; the fourth is new.

1. **Pre-registration.** Every threshold is fixed before the run it judges. A threshold derived from the
   results it judges is not evidence.
2. **Provenance labelling.** Each threshold is marked **literature-derived** or **project-chosen**.
   Project-chosen is legitimate and reviewers accepted it in papers 2 and 3; project-chosen presented as
   literature-derived is the defect. **Three of `RL08`'s rows were relabelled downward on exactly this
   basis.**
3. 🔴 **Every gate must be able to fail**, and each is **seen failing** once on a deliberately broken
   input before it is trusted on a real one. `RL08` supplies three ready-made broken inputs — shuffled
   diary, modal-collapse generator, training-set replay — and each is designed to fail a different part
   of the battery.
4. 🔴 **No gate is a p-value.** At 10⁵ to 10⁶ generated records every two-sample test rejects on
   differences of a minute a day. Bounded effect sizes, TOST equivalence tests against a stated margin,
   and a sample-size-matched bootstrap against the real-to-real split-half divergence.

### The privacy audit, which is now part of validation rather than an appendix

From `RL10`, and it runs before anything is released:

| Attack | Fails if |
|---|---|
| Loss-based membership inference | ROC-AUC > 0.65, or TPR at 0.1 % FPR > 5 % |
| Reference-based MIA against the public base model | ROC-AUC > 0.75 |
| Prefix-prompted extraction, greedy and sampled | any exact match on a stratum with fewer than 5 training records |
| Distance to closest record and NNDR on the synthetic release | any DCR = 0; or median DCR to train significantly below median DCR to test; or NNDR < 0.33 in over 0.1 % of records |

With three controls: the untuned base model (expect AUC ≈ 0.50), a random-label-permutation adapter that
sets the floor for pure sequence memorisation, and a train-versus-test perplexity gap under 5 %.

---

## KEY DESIGN DECISIONS

Reproduced from the overview, with the reasoning that did not fit there.

| Decision | Rationale |
|---|---|
| The transfer experiment is the paper | Now evidenced by `RL06` rather than asserted by us. A from-scratch conditional Transformer beats the LLM everywhere except transfer, and pretraining stops helping on tabular data at around 1,000 records. Building the paper on anything else invites the one reviewer question we cannot answer |
| Track B primary, Track A parallel — 🔴 **Track C withdrawn** | A 12 to 14 week institutional application does not go on the critical path, and Track A now widens the corpus from four countries to seventeen with no harmonisation change, so it matters more than it did. **Track C was the public ATUS path and it leaves with decision 5.** What replaces it is open decision 13 |
| Episode encoding plus a 145-state tally automaton | Four-fold token saving, measured, and the grammar objection dissolves once the sum is recognised as bounded and quantised |
| 🔴 **Backbone `allenai/Olmo-3-1025-7B`, chosen by measurement not by report** | 200 tokens per diary against Qwen's 303 on the identical string, because the OLMo tokenizer holds a three-digit activity code as one token and the entire Qwen lineage splits it into three. Apache 2.0 with no condition on generated text, native vLLM kernel, ungated, 65,536 context. `RL18` recommended the opposite and did so on a mis-counted token figure and a licence clause that is not in Llama 3.1 |
| 🔴 **No mnemonic code remapping** | Measured, it saves 12.9 % on Qwen and **costs** 5.5 % on the tokenizer we adopted. A fix for a tokenizer we are not using |
| No added tokens | LoRA freezes embeddings; unfreezing costs ~16.8 GB and breaks export. The canonical first-timer error, avoided by construction |
| Unweighted loss; representativeness in the population stage | The prefix carries the design strata, so sampling is conditionally ignorable. It also removes a double-correction bug with the weekday-weekend weight |
| We never rake our own output | Raking fixes margins, not joints, and it is reserved for building the null we must beat |
| Joint multi-country training | Sequential costs 40 to 70 % on earlier countries |
| 🔴 **No forecast; the method is the contribution** | Author's decision, backed independently by `RL16`. One claim defended completely beats two where the second undermines the first |
| 🔴 **HETUS-only corpus, four countries, one wave each** | The claim under test is about HETUS standardisation, so the corpus is HETUS members. One wave each because `RL17`'s own inventory argues against two: three of the four second waves sit past the ACL 2000 break, which forces 2-digit codes and starves Step 9, and UK 2000-01's 15-minute slots are not admissible to a tally automaton built on multiples of 10. The chosen set is the HETUS 2010 round, so Track A widens it four → seventeen with no harmonisation change |
| 🔴 **The hard null is the announced objective** | Stated in the introduction, so the paper is falsifiable in one sentence. A bar set in advance and cleared is worth more than one chosen afterwards |
| Weights withheld, data and code released, without apology | No precedent exists for a statistical institute permitting weight release from restricted microdata, and reference-based MIA against a public base model is the specific attack that makes adapters leaky. A methods paper describes the method; anyone with the same data licence can rebuild it |
| The uninjected control runs first | 3J spent eight campaigns learning this |
| Nothing multi-node, nothing over seven days | Not a preference. It is what the cluster allows, and MIG slices cannot talk to each other anyway |

---

## OPEN DECISIONS

**Twelve of fifteen fully closed as of 2026-08-14**; the table with the settling source for each is in
the overview. The list grew before it shrank: decisions 1 and 3 closed, decision 9 partly reopened
when the HETUS-only scope removed the ATUS reproduction path, **three new items appeared as
consequences of decisions already taken**, then decisions 11 and 13 closed on author calls the same
day, and **decision 15 closed the same evening when `RL20` returned a clean negative.**

🔴 **Only decision 14 is genuinely open, and `RL21` established that it cannot be closed by reading.**
Decision 12 remains deferred as scope rather than open as a question. See V12 to V14.

🟢 **UPDATE 2026-08-25 (night) — 15 OF 15 NOW CLOSED. Decision 14 closed by our own experiment,
exactly as `RL21` said it would have to.** `G7.18` ran in Step 8 (`tools/4thJ_step8_chaining.py`,
**9,000 EnergyPlus runs**, three folds × six rule points × five seeds × 100 dwellings at `f = 1.00`,
so an upper bound) and returned `FINDING 136`: the whole chaining axis moves peak demand
**0.178 / 0.075 / 0.239 %** against the **25 %** trigger, and the seed spread within a rule beats the
spread between rules on every metric in every fold. **The author ruled `independent`, seed 1 as the
standard convention, with the empirical null itself as the published deliverable.** Decision 12
remains deferred scope. Ruling: §8 of
`Step8_docs/docs/2026-08-25_decision-14_chaining-on-a-watt.md`.

**What closed since the sixteen-report round:**

* ✅ **Decision 3, the model family, is CLOSED — by our own measurement, not by `RL18`.** Primary
  backbone `allenai/Olmo-3-1025-7B`: 200 tokens per diary against Qwen's 303, Apache 2.0 with no
  condition on generated text, native vLLM kernel, ungated, 65,536 context, 7.30 B parameters.
  `Qwen/Qwen2.5-7B` is retained as the named comparison arm. Full reasoning in 4B and 4B-bis.

**What remains, and what closes each:**

* ✅ **Decision 3's pilot sub-item is also closed.** The author fixed it on 2026-08-14:
  **Leg-4** = `allenai/OLMo-2-0425-1B` (1.48 B, same tokenizer and vocabulary), **Leg-5** =
  `allenai/Olmo-3-1025-7B`. The numbering continues from 3J, which ended at Leg-3.
* ✅ **Decision 1 is fully closed.** Author decisions 5 and 6: **HETUS only, four countries, one wave
  each** — Italy 2013-14, Spain 2009-10, UK 2014-15, France 2009-10. `RL17` recommended two waves and
  its own inventory is what argued against it. The `ACT` field keeps its three digits.
* ✅ **Decision 11, which country is held out, is CLOSED. Author, 2026-08-14: none of them, and all of
  them.** The evaluation is **four-fold rotation** — every country is held out in turn, so the reported
  transfer result is four leave-one-country-out runs rather than one.

  **Why this is the stronger answer rather than the expensive one.** The hazard the decision existed to
  prevent was a held-out country chosen after results have been seen. Rotation removes the choice
  instead of timing it: there is nothing left to select, so there is nothing to select favourably.
  It also converts the single most fragile number in the paper into a distribution over four, which is
  what lets us say whether transfer works or whether it works *for Spain*.

  🔴 **Two conditions, pre-registered, without which rotation gives back what it bought.**
  **All four folds are reported, always, including the worst.** Reporting the best fold, or dropping a
  fold as anomalous, is the same defect as choosing the country late, arriving by a different door.
  And **no fold's result may change the design** — architecture, prompt format, gates or hyperparameters
  — once any fold has been evaluated; a change made after seeing fold 1 contaminates folds 2 to 4.

  **Cost.** Four fine-tuning runs at Leg-5 instead of one, and four at Leg-4, where the 1B pilot makes
  the rotation nearly free. This is the reason the decision was previously framed as a choice, and the
  cost is accepted.

  **A second, weaker hold-out is retained and must never be confused with this one.** A random sample of
  households is held out from *within* the training countries as an ordinary test set. It measures
  whether the model reproduces data whose country it has already seen, which is what papers 1 to 3
  measure. 🔴 **It is a sanity check and is never reported as transfer.**
* **Decision 12, household-joint generation.** Now known to be feasible: a four-person household week is
  about 7,000 tokens, comfortably inside context — and more comfortably still at 200 tokens per diary
  on the adopted tokenizer. Deferred as scope rather than excluded as impossible, and it remains the
  natural fix for paper 1's co-presence weakness.

**And three items that no earlier decision covered, one of which has since closed.**

* ✅ **Decision 13 — what replaces the ATUS reproduction path — is CLOSED. Author, 2026-08-14: Spain
  alone as the first route, and a cross-country route alongside it.** Two tiers rather than one,
  because the single-country path reproduces the machinery and cannot reproduce the claim.

  | Tier | What a reader needs | What it reproduces |
  |---|---|---|
  | **1. Spain 2009-10 alone** | **Nothing. INE open download, no registration** | Every stage end to end: parse, harmonise, serialise, fine-tune, constrained generation, schedule assembly, EnergyPlus. **Not transfer** — one country cannot |
  | **2. Spain 2009-10 + UK 2014-15** | Two free registrations, no institutional accreditation | The transfer machinery itself: train on one, hold out the other, against the reweighted real-diary null |

  **Why UK is the second country.** Of the three credentialled sources it is the only one whose
  registration is free, individual and immediate. France needs academic registration through
  Progedo/ADISP and Italy needs a per-project application taking two to eight weeks, so neither is a
  route a reader can walk in an afternoon. 🔴 **This pairing is the manager's implementation of the
  author's decision, not the author's own selection, and it is the part to correct if it is wrong.**

  🔴 **What tier 1 cannot do, stated in the Data Availability statement rather than left to be
  discovered.** Spain fields **one diary day per respondent**, so the single-country path has no
  within-person multi-day structure at all, and any day-to-year chaining rule that depends on
  persistence (decision 14) cannot be exercised on it. Tier 2 is what carries that.

  **The loss is still recorded as a loss.** Neither tier restores what Track C had, which was a
  zero-credential path that also demonstrated the claim. See 1D.
* 🔴 **Decision 14 — the day-to-year chaining rule — is the only decision still open**, and after
  `RL21` it is open in a different way than it was. Nothing says how 365 generated days are chained
  into one household's simulated year. Independent daily resampling damps peak demand, static
  repetition exaggerates it, and the choice may move the result more than transfer quality does.
  See V8, V13, V14 and Step 7E. **Must close before the Step 8 campaign is designed.**

  ✅ **`RL21` returned on 2026-08-14 and answered the commissioning question: zero.** No published study
  has compared two or more chaining rules on the same building with the daily generator held fixed, no
  standard defines a protocol, and no citable threshold exists for when a modelling convention dominates
  a result. 🔴 **Therefore decision 14 cannot close by citation. It closes by our own experiment or it
  does not close.** Every percentage in `RL21` is rejected, including the 15 to 35 % peak divergence it
  is most likely to be quoted for — that number contradicts its own `B1` and is sourced to papers that
  did not make the claim. See V13.

  🔴 **One `RL21` finding changes the experiment before it is designed.** A two-day survey of one
  weekday plus one weekend day **cannot identify consecutive-day transition probabilities**, so the
  habit-coupled Markovian rule cannot be parameterised from our own corpus. **Run it as a sweep over the
  persistence parameter rather than as a fitted rule**, and report the sensitivity band. A fitted value
  we chose ourselves would be our bookkeeping compared against itself, which is the exact failure this
  decision exists to prevent.

  **And record annual energy in the same campaign.** `RL21` infers it moves under 3 % while peak moves
  far more. It costs nothing to measure both, and measuring is what settled open decision 3.
* ✅ **Decision 15 — Norway as a fifth country — is CLOSED. NO.** Opened by the author on 2026-08-14
  after `RL19`, closed the same day by `RL20`. It was the only decision on this list that could
  **reverse decision 6 without appearing to**, and it did not.

  **What is in its favour.** Norway is the only reachable Nordic candidate in the round, and it is a
  genuinely hard held-out target rather than a fifth neighbour: high-latitude photoperiod, an early
  end to the working day, an early main meal. It also repairs limitation C4, since leave-one-country-out
  would train on four instead of three. On slot length it passes cleanly — **10-minute intervals, two
  diary days, ages 9 to 79, paper diary**, confirmed against Statistics Norway rather than taken from
  the report.

  **What is against it.** The national file carries the **SSB classification of roughly 170
  categories**, not ACL 2008. `RL17` B3 states that a defensible cross-survey activity mapping exists
  only at 2-digit ACL or MTUS 69, and that full 3-digit cannot be mapped without arbitrary one-to-many
  heuristics. **A crosswalk we build ourselves is that heuristic**, it would sit inside the training
  corpus where no gate can see it, and it lands on Step 9 — the step 3-digit codes were preserved for.

  🔴 **The decision turns on one checkable fact, and not on judgement: does the Sikt delivery ship an
  official Eurostat/ACL recode variable produced by SSB?** If it does, Norway is admissible and worth
  taking. If it does not, Norway is rejected for the same reason as UK 2000-01 and Italy 2022-23, and
  the four-country corpus stands. **Establish the fact before weighing the benefit** — the benefit is
  real enough to make the crosswalk look acceptable, which is exactly how a corpus decision gets taken
  by accident. **Must close before Step 1 acquisition finishes.** See V10.

  ✅ **`RL20` returned and the fact came back negative.** The Sikt delivery carries **only SSB's
  167-category national classification**, no ACL variable at any depth, and **no official recode table
  exists** — `NOT FOUND` in SSB publications, in the SSB `Klass` database and in the Sikt metadata.
  `RL19`'s claim that a documented one-to-one recode is supplied is **formally retracted**, and no
  published third-party crosswalk exists either; MTUS harmonises Norway only at 69 or 41 activities,
  which is below what Step 9 needs.

  **So Norway is rejected for exactly the reason UK 2000-01 and Italy 2022-23 are: it is not admissible
  to the machinery without something we would have to invent.** The four-country corpus stands and
  **limitation C4 stands with it, now with a documented reason rather than an untested hope of repair.**

  🔴 **The one caveat, stated because the closure is otherwise clean.** `L20` told the report that a
  short negative was the expected outcome, and a short negative is what came back. The verdict is
  accepted on its checkable details — 167 categories, diary variables `akt1` to `akt144`, Notater
  2012/03, `Klass` searched — not on the report's own confidence. **If Norway is ever reconsidered, open
  the Sikt variable list itself and nothing else.** Its Part E answer was quoted from our prompt and its
  Section D invents facts about our cluster; both are discarded. See V12.

---

## LIMITATIONS — CONSOLIDATED

The consolidated table lives in the overview. Three items were added on 2026-08-14 from the reports (no
model release, we build the archetypes ourselves, Concordia is not a recognised research entity). Each
is stated at full strength before the work starts so that none can be discovered late and quietly
softened. Items acquire a measured bound as the work proceeds; an item that cannot be bounded is marked
*not quantified* rather than given an invented one.

🔴 **The C group moved twice in one day, and the pattern is worth naming.**

* **C1 was removed** when the forecast left scope. "Two waves is not a trend" was a limitation only
  because the paper intended to claim a trend.
* **C3 was added** with the multi-wave decision, then **C2 and C3 were both removed** by decisions 5
  and 6 the same day. C3 said pooling waves may teach the model the instrument; one wave per country
  means there is no pooling. C2 said the recent waves confound a pandemic effect with a mode change;
  those waves are not in the corpus.
* **C4 was added** in their place: the corpus is four countries, all Western or Southern European, so
  leave-one-country-out trains on three.

**Every one of those removals took the practice away, not the wording.** That is the distinction that
matters: removing a limitation by removing the claim or the practice it constrained is legitimate;
softening the wording while keeping the practice would not be. C4 is the honest replacement — narrowing
the corpus bought coherence and cost breadth, and the cost is written down rather than netted off.

The ones most likely to be argued with in review:

* **B1**, that a pretrained model's world knowledge is not uniform across countries. **This is no longer
  a hypothetical**: `RL04` reports the asymmetry runs strongest against exactly the peripheral European
  countries where a transfer claim is most interesting. It is pre-registered as a confound and tested
  with the fictional-country control.
* **B2**, that transfer is scored against aggregates, which cannot detect a wrong joint structure hiding
  behind right marginals.
* 🔴 **C4, REWRITTEN 2026-08-15 by author decision 16: the corpus is THREE Western and Southern
  European countries — Italy, Spain, the UK — and leave-one-country-out therefore trains on TWO.**
  France was excluded because its Progedo delivery has no arrival date and the project would not wait
  on it. **This is the cost of narrowing to HETUS with one wave each, and then of not waiting.** A
  reviewer can fairly ask whether transfer across three neighbours demonstrates transfer across a
  framework, and the only honest answers are that the corpus is what was obtainable on the project's
  own timetable and that Track A would widen it to seventeen with no harmonisation change. 🔴 **The
  exclusion is stated in the paper as a scheduling decision, not dressed up as a design choice** —
  France is a HETUS 2010 member with a usable wave and nothing about it failed a screen.
  *(Superseded wording: "the corpus is four Western and Southern European countries and
  leave-one-country-out therefore trains on three.")* (~~C3~~, pooling waves, was
  removed the same day along with the pooling it described.)
* **F1**, that we do not release the model — stated in one sentence and not revisited.

---

## PROGRESS LOG

Append-only. Never delete or reformat an existing entry; if a decision changes, edit that entry rather
than appending a contradiction.

### 2026-08-13 — plan created

* Paper 4 scoped and written up: `4thJ_00_HETUS_LLM_Pipeline_Overview.md` and this companion document.
* Sixteen deep-research prompts authored in `DeepResearchPrompts/`, with `00_MASTER_BRIEF.md`,
  `_RESPONSE_TEMPLATE.md` and a `README.md` carrying the run order, the per-prompt table and the
  vetting procedure. Series prefix is `L` so it never collides with 3J's `V` series in a search.
* Prompt series is **wave-ordered**, not flat: `L01` and `L03` run alone and first, because either can
  end the project. `L06` runs in wave 1 and is deliberately written so that "an LLM is the wrong tool"
  is a compliant answer.
* Source paper read for framing: Iseri, Gursel Dino and Kalkan, *Energy and Buildings* 357 (2026)
  117155. Its untested claim, that HETUS standardisation makes the method globally adaptable, is the
  seed of paper 4. Its reported argmax uniformity problem at neighbourhood scale is the origin of the
  Tier-2 variance-collapse gate.
* 🔴 **Speed GPU inventory measured**, not assumed, via `sinfo -N -o '%N|%P|%f|%G|%m|%T'` on
  2026-08-13. A **full 80 GB A100 is reachable** as MIG profile `nvidia_a100_7g.80gb`, one per node on
  `speed-37` and `speed-39` to `speed-43`, alongside 20 GB slices, 48 GB RTX 6000 cards and 32 GB
  V100s. This materially de-risks Step 4 and is written into `L04` and `L11` as ground truth, so the
  returned reports cannot invent our hardware.
* Graphical-abstract prompt authored at
  `writing/submission/figures/Prompts_Images/4thJ_graphical_abstract.md`. **The image is not generated
  here**; the author generates it, per the standing rule.
* **Nothing is decided and nothing is built.** All twelve open decisions are open. Next action is
  running `L01` and `L03` externally, one per session, master brief pasted first.

### 2026-08-14 — all sixteen reports returned, vetted, and folded into the plan

* **`RL01` to `RL16` all present** in `DeepResearchPrompts/`. All sixteen read in full before any value
  was written into a plan document. The vetting record is the section **REPORT VETTING RECORD** above
  and it is part of this document, not a scratch note.
* **Nine of twelve open decisions closed.** Still open: model family (3), held-out country (11),
  household-joint generation (12). Decision 3 closes by our own measurement, not by another prompt.
* 🔴 **`RL10` fired the release kill switch. We may not publish the trained weights or the adapter.**
  Deliverable changes to a synthetic dataset (CC BY 4.0, Parquet, Zenodo plus Hugging Face) plus code
  (Apache 2.0) plus a fully public ATUS stand-in pipeline. A four-attack privacy audit joins validation.
  Note that `RL04` and `RL15` both said the opposite by reading only the model licence; the binding
  constraint is the data agreement. **Recorded as contradiction 1 rather than smoothed over.**
* 🔴 **`RL01` moved Track B from fallback to primary.** Eurostat holds central microdata for the 2010
  round only; Round 1 never existed centrally and Round 3 is embargoed to 2027 or later. Concordia is
  not a recognised research entity, so Track A is a 12 to 14 week parallel application, not a plan.
* 🔴 **`RL16` killed the 3J-style forecast.** One usable Eurostat wave; a year token is
  out-of-distribution noise. Replaced by Kitagawa-Oaxaca-Blinder decomposition on **national** multi-wave
  series plus exogenous scenario projection cited to EUROPOP2023, the 2024 Ageing Report, Cedefop and
  EU-LFS. Time enters through the population, never through the model.
* 🔴 **`RL06` hardened the null model** from the pooled all-country average to **real N-1 diaries raked
  by IPF to the held-out country's marginals**. We adopted the harder null. `RL08` still proposes the
  easier one; it is demoted to secondary.
* **`RL07` settled the serialisation on measured tokens**: episode form at 196 to 326 tokens against 924
  to 1310 for the best slot form. `RL12`'s objection that a duration sum is not a regular constraint is
  resolved by a 145-state tally automaton, so episodes keep both the token saving and the hard
  guarantee.
* **`RL02` corrected two things we had wrong.** Co-presence is five binary flags, not one code. And
  **location code 11 merges dwelling, yard and garden**, so presence in the conditioned volume needs an
  activity-based exclusion rule and is not readable from location alone. `RL07`'s example strings use
  invented location codes and are not used as a specification.
* **`RL05` set the recipe**: base checkpoint, SFT with completion-only loss masking, rsLoRA r=32 on all
  linear layers, bf16, packed sequences, full fine-tuning with 8-bit AdamW as an affordable ceiling run,
  QLoRA rejected, and joint multi-country training rather than sequential.
* **`RL04` refused to confirm "Gemma 4".** It does not exist, nor does gemma-2-7b or gemma-3-8b. The
  model family stays open because `RL04` and `RL07` disagree along different axes (licence versus
  tokenisation) and because Mistral 7B v0.3 may satisfy both, on a claim neither report verified.
* **`RL13` reported `COULD NOT OPEN` for EN 16798-1 rather than reconstructing Annex C.** The negative
  control fired. The baseline foil moves to the open ISO 13790 Annex G / UNI/TS 11300-1 flat 4.0 W/m²,
  which is a better foil anyway. `RL13` also revealed new scope: **no official European EnergyPlus
  archetype library exists**, so we build the IDFs from TABULA parameters ourselves.
* **`RL08` supplied the gate table.** Adopted with three provenance labels corrected downward, two
  privacy gates added from `RL10`, and the transfer gate rewritten around the harder null.
* **Citation defects logged**: LLM-Mob appears with three different arXiv IDs across `RL03`, `RL06` and
  `RL14`; GReaT with two; `RL05` rests part of its QLoRA argument on an unverifiable Tier-3 source;
  `RL12` cites several 2026 arXiv IDs with the shape of fabrications. `RL14`'s reference list is the
  least reliable of the sixteen and is not reused. Mechanisms kept where they are elementary; citations
  dropped.
* **Six claims held back pending our own local check**, listed in section V4: the Mistral tokenizer, the
  unique-sequence baseline, the survey margin of error, the Speed partition names, Concordia's
  eligibility, and the APC waiver. None of them is expensive to settle and each is expensive to be
  wrong about.
* **`RL11`'s SLURM template adopted with two corrections**: `srun` removed and walltime raised to the
  full seven days, per the standing cluster rules.
* Graphical-abstract prompt updated the same day for the decided pipeline: the two-stage
  population-then-diary structure added, `start` dropped from the episode tuple, and the held-out lane
  now names what it is scored against.
* **Still nothing is built.** Next actions, in order: (1) measure the three tokenizers, closing decision
  3; (2) download the Spanish, UK and French files and write the corpus parser that tolerates both
  reported HETUS file shapes; (3) file the Eurostat entity-recognition enquiry with the Office of
  Research; (4) compute the unique-sequence baseline on held ISTAT and GSS data so Gate 6 can be
  trusted.

### 2026-08-14 (later the same day) — author fixes the scope; `L17` written

Four decisions taken by the author after reading the report summary. All four **narrow** the paper.

* **1. The release restriction is accepted and is no longer treated as a wound.** The method is
  described in the paper; that is what a methods paper is for. Weights stay internal, the synthetic data
  and the code are published, and the ATUS path lets anyone run the pipeline. Limitation F1 was
  rewritten from an apology into a one-sentence Data Availability statement.
* 🔴 **2. The corpus is five countries and it is MULTI-WAVE.** Italy, Canada, Spain, UK, France, with
  several survey cycles each rather than one. Depth in time instead of width in countries. Open decision
  1 is therefore **partly reopened**: the countries are settled, the number of waves is not.
  **The cost is recorded as new limitation C3**: pooling waves whose coding scheme, slot length or
  collection mode differ can teach the model that instrument changes are behaviour changes, which is
  invisible because it looks like behavioural diversity. The honest fallback is fewer waves.
* 🔴 **3. There is no forecast in this paper. Out of scope, not deferred.** No year token, no scenario
  levers, no 2030. The contribution is the method of applying a fine-tuned LLM across the HETUS and
  wider time-use framework, which stands on its own. `RL16` had already found the data could not carry a
  projection, so the decision and the evidence agree, but the decision is the load-bearing one.
  **Consequence:** the Kitagawa-Oaxaca-Blinder decomposition `RL16` recommended is also out — it was the
  strongest *temporal* formulation and there is no longer a temporal claim. Recorded as the obvious
  content of a later paper. **Limitation C1 was removed rather than softened**, because the claim it
  constrained no longer exists.
* 🔴 **4. The hard null is the objective, not an obstacle.** Beating real diaries from the other
  countries reweighted to the held-out country's demographics is now stated in the **introduction** as
  what the experiment is for, rather than disclosed in the evaluation section. It makes the paper
  falsifiable in one sentence.
* **`L17_contradiction_adjudication_and_multiwave.md` written** and registered in the README as a new
  Wave 5. It is a different kind of prompt from `L01` to `L16`: **adjudicative rather than
  exploratory.** Part A hands it the eight inter-report contradictions and forbids splitting the
  difference — one side is wrong, or both are, or `NOT FOUND`, which is an explicitly successful answer
  here because it redirects us to ask the data provider. Part B builds the multi-wave inventory for the
  five countries, including where every comparability break falls, and is written so that "use the most
  recent wave per country" is a compliant recommendation. Part C lists the six unchecked claims. Part D
  asks the one question seventeen prompts by the same author would not have thought to ask.
* Its negative controls are aimed at the specific failure this round is prone to: it must report **which
  contradictions it resolved by opening a document versus by reasoning**, and **how many of the eight it
  resolved in the direction convenient for us**, with an instruction to re-examine if that count is
  seven or eight.
* Graphical-abstract prompt updated again for decisions 2 and 3: Band 1 now carries several waves per
  country, and the ban on any year, time axis or forecast arrow is now explicit.
* **Still nothing is built.** The next actions are unchanged, plus: run `L17` externally, master brief
  pasted first.

### 2026-08-14 (third entry) — `RL17` and `RL18` returned; decision 3 closed by measurement on Speed

* **`RL17` and `RL18` are back and vetted.** The vetting is the section **REPORT VETTING RECORD,
  SECOND ROUND** above, and it is part of this document rather than a scratch note.
* **`RL17` is the strongest report of the eighteen.** It adjudicated all eight contradictions, landed
  on the inconvenient side four times, and returned **two `NOT FOUND` verdicts** that cost us
  provenance we wanted: neither the ±12-18 min/day survey margin of error nor the U > 0.98
  unique-sequence benchmark exists in the literature. `RL08` invented both. Those two gate rows are
  now permanently labelled project-chosen. It also declared `RL04` and `RL07` **both wrong** about the
  Mistral tokenizer, which we then confirmed ourselves.
* 🔴 **Open decision 3 is CLOSED, and not by `RL18`.** Six CPU jobs were run on Speed — `1234177`,
  `1234192`, `1234199`, `1234211`, `1234216`, `1234219` — loading real tokenizers, reading real
  configs, reading the vLLM registry source, and reading licence text. Scripts in `tools/`, logs on
  `/speed-scratch/o_iseri/`. **Primary backbone: `allenai/Olmo-3-1025-7B`.** 200 tokens per diary
  against Qwen2.5's 303 on the identical 25-episode string, Apache 2.0, ungated, native vLLM kernel,
  65,536 context, 7.30 B parameters. `Qwen/Qwen2.5-7B` retained as the named comparison arm.
* 🔴 **`RL18` was wrong twice, and it is the report we commissioned to make this decision.** It
  reported the mnemonic episode `45,wrk,11,0;` at 8 Qwen tokens; measured, it is 11. And it stated as
  a Tier-1 fact that Llama 3.1 §1.b forbids using outputs to improve other models. **Meta's licence
  files were read: that clause is in Llama 2 and Llama 3 and is absent from 3.1, 3.2 and 3.3, which
  carry a naming requirement instead.** `RL04` introduced that error and both plan documents had
  carried it since. Llama remains unselected, now on measured grounds. Recorded rather than deleted,
  because it was a factual claim about a third party's legal document.
* **The mnemonic code remapping is rejected.** It saves 12.9 % on Qwen and costs 5.5 % on the adopted
  OLMo tokenizer. It was one edit away from entering the serialisation schema.
* **Two costs of the switch are recorded, not discovered later.** OLMo 3 has **no base checkpoint
  below 7 B**. And **OLMo 3 7B has no grouped-query attention** (32 KV heads against Qwen's 4), so its
  KV cache is about nine times larger per token; the 34 % token saving offsets only part of that. A
  vLLM throughput comparison is required before Step 7 is sized.
* ✅ **Author decision the same day: the legs are numbered Leg-4 and Leg-5**, continuing the series
  from 3J which ended at Leg-3. **Leg-4 pilot = `allenai/OLMo-2-0425-1B`** (1.48 B, byte-identical
  tokenizer and vocabulary, so the training data is not regenerated between legs); **Leg-5 reported =
  `allenai/Olmo-3-1025-7B`**. Leg-4 validates correctness only — its 4,096 context and its generic
  vLLM fallback path mean no performance number from it extrapolates to Leg-5.
* **Gemma and Llama repositories are gated and returned `401`.** They are not measured and nothing is
  claimed about them. The "Llama writes `411` in one token" claim remains somebody else's measurement.
* **`RL17` Part D surfaced a genuine gap nobody had asked about**: nothing in this plan says how 365
  generated days are chained into one household's simulated year, and the choice may move peak demand
  more than transfer quality does. Written up as Step 7E.
* **Four of the six V4 claims are now settled**; the two that remain — Concordia's Eurostat
  eligibility and the APC waiver — are the two that need a person rather than a job, and neither has
  been asked. `RL17` gives an answer to both; a report is not the Office of Research or the library.
* **Still nothing is built.** Next actions: (1) author's call on `RL17`'s two-wave recommendation, the
  last open item of decision 1; (2) download the Spanish, UK and French files and write the parser
  that tolerates both file shapes; (3) file the Eurostat entity-recognition enquiry with the Office of
  Research; (4) compute the unique-sequence baseline on held ISTAT and GSS data so Gate 6 can be
  trusted; (5) the vLLM throughput comparison on Leg-5 checkpoints before Step 7 is sized.

### 2026-08-14 (fourth entry) — the author narrows the corpus: HETUS only, four countries, one wave each

Two decisions, taken after reading `RL17`'s wave inventory. Both **narrow** the paper, and together
they reverse the "five countries × several waves" decision recorded in the entry above. That entry is
left standing rather than rewritten, because the reversal and its reason are the record.

* 🔴 **Decision 5. The corpus is HETUS only. No Canada, no United States.** The Canadian GSS cycles and
  ATUS leave the paper. The reason is the paper's own logic: paper 1 claims **HETUS standardisation**
  makes the method globally adaptable, and a corpus of HETUS members is the corpus that tests it.
  Bringing in a non-HETUS survey would test whether the method survives a *different* harmonisation
  frame, which is a different paper.
* 🔴 **Decision 6. One wave per country — the HETUS 2010 round.** Italy 2013-14, Spain 2009-10, UK
  2014-15, France 2009-10. **`RL17` recommended two waves per country and its own inventory is what
  argued against it.** Three of the four second waves it proposed — Spain 2002-03, UK 2000-01, France
  1998-99 — are ACL 2000, on the far side of a structural coding break that our Step 2A rule says
  forces pooling at 2-digit; and 2-digit codes starve Step 9's appliance triggering. **UK 2000-01 is
  worse: 15-minute slots, so its episode durations are multiples of 15 while the Step 7 tally automaton
  requires multiples of 10. That wave is not admissible to the constraint machinery at all.** Against
  that, `RL06` already reports the benefit of pretraining on tabular data vanishing near 1,000 records,
  so extra volume was never the binding constraint.
* **What the one-wave set buys.** One coding-list generation, one slot length, one collection mode,
  10-minute quantisation throughout — and **the `ACT` field keeps its three digits**, which is what
  Step 9 needs. It is also exactly the round the Eurostat SUF covers, so **Track A would widen the
  corpus from four countries to seventeen with no harmonisation change at all.** Track A is therefore
  more valuable than "parallel, never on the critical path" implied, though it stays off that path.
* **Earlier waves are not discarded**; they become **held-out validation and never training data**.
* **Step 3B gains two constant prefix fields, `MODE` and `SCHEME`** — collection mode and coding-list
  generation — invariant across the whole corpus, written in from the first record so that adding a
  wave or seventeen Track A countries never changes the record format. 🔴 **They are not year tokens
  and must never become one**: naming the instrument cannot be extrapolated, naming the time can.
* **Limitations moved three times.** `C2` (pandemic and mode confounded) and `C3` (pooling teaches the
  instrument) are **removed**, because the waves and the pooling they described are both gone. **New
  `C4`: the corpus is four Western and Southern European countries, so leave-one-country-out trains on
  three** — a reviewer can fairly ask whether that demonstrates transfer across a framework.
* 🔴 **Two new open decisions, both consequences rather than oversights.** **13:** decision 5 removed
  Track C, the public ATUS pipeline that was `RL15`'s answer to `RL10`'s no-weights restriction, and
  **nothing yet replaces it** — Spain's INE needs no registration and is the candidate minimal public
  path; it must close before the Data Availability statement is written. **14:** the day-to-year
  chaining rule from `RL17` Part D, which must close before the Step 8 campaign is designed.
* **The open-decision count went up, not down: nine of fourteen fully closed.** Recorded that way
  deliberately. Narrowing scope closed two decisions and opened two others, and a count that only ever
  falls is a count that is hiding something.
* **Still nothing is built.** Next actions: (1) download the Spanish, UK and French files for the four
  chosen waves and write the parser that tolerates both reported file shapes; (2) file the Eurostat
  entity-recognition enquiry with the Office of Research, now worth more than it was; (3) compute the
  unique-sequence baseline on the held ISTAT data so Gate 6 can be trusted; (4) decide 13 and 14;
  (5) the vLLM throughput comparison on Leg-5 checkpoints before Step 7 is sized.

### 2026-08-14 (fifth entry) — the per-step working documents are created

* **`Step0_docs/` to `Step9_docs/` created**, following the 3J `Leg3_4-split` convention: one folder
  per step, each holding an **implementation** specification, a **validation** specification and an
  `outputs_stepN/` directory. Twenty documents, about 3,100 lines. **Nothing is built; these are
  specifications, and every one of them says so in its own status line.**
* **The implementation documents** carry: the aim, the decisions already fixed with their source (so
  nothing is relitigated at execution time), the inputs, numbered work items each with a definition of
  done, the outputs and who consumes them, the Speed run conventions, what blocks the step and what
  the step blocks, and an append-only Progress Log.
* **The validation documents** carry: the gates with thresholds **and provenance labels**, a
  perturbation table in which **every gate must be seen failing and each perturbation must break
  exactly one gate**, a **coverage clause** that fails the probe if any passing gate was never made
  to fall, **vacuity guards**, a **null perturbation** in every set, and an explicit section on what
  that step's validation does **not** cover.
* 🔴 **Three gate-design rules are carried into every validation document from the 3J catalogue**,
  because each of them cost real work there: *at least one check must come through a path the defect
  cannot reach* (Step 3's G3.13, Step 8's G8.12); *a gate whose reference is derived from the source
  it audits cannot fail* (Step 5's G5.6, Step 8's saved-IDF requirement); and *a check that cannot
  distinguish "found nothing" from "could not run" is not a check* (every step's vacuity guards).
* **Two gates exist specifically to test decisions rather than data.** Step 7's G7.1 to G7.4 are
  labelled **enforcement confirmations** and excluded from any "seen failing" tally, because they
  cannot fall while the grammar mask is on. Step 9's **G9.11** checks whether preserving 3-digit
  activity codes — a corpus decision taken partly for Step 9 — actually bought that step anything.
* **Where the step documents disagree with nothing, they say so.** Each carries the same decisions as
  this document, sourced to it, so that a step executed from its own folder cannot drift from the
  plan without the drift being visible.

### 2026-08-14 (sixth entry) — the newer waves are written in as excluded, with the Eurostat date

* **New section 1B-bis.** Decision 6 was documented only on its backward side. The author asked
  whether newer cycles exist; they do, and the document did not say why they are out. It does now:
  UK 2020-21 (online, lockdown, 16+), Italy 2022-23 (ACL 2020 and web/app), Spain 2024-25 and France
  2024-25 (no released microdata). **One cause, not four: our four waves are all paper
  self-completion under one coding generation, which is what keeps `ACT` at three digits.**
* 🔴 **Checked, not assumed:** the Eurostat **HETUS 2020 round** concludes fieldwork in 2026 and
  **Eurostat states microdata will not be released before 2027** — after this paper. Verified against
  Eurostat's microdata page and its January 2024 UNSD presentation. **There is no newer obtainable
  corpus.** This is now the answer to "why not the most recent data?", which is the first question a
  survey-based paper is asked.
* **A consequence 1B did not state:** held-out validation runs **backwards only**. Three of the four
  newer waves cannot be obtained, so there is no forward held-out set. If Italy 2022-23 is acquired
  later it is a second held-out instrument, never a fifth training country — and `MODE` and `SCHEME`
  in the prefix are what make that admission structurally free.
* **`Step1_docs/4thJ_01_corpusAcquisition.md` updated in the same pass** with an explicit instruction
  not to upgrade a country to its newest wave during acquisition. That is the moment the mistake
  would actually be made, by someone holding a newer file and no reason not to use it.

### 2026-08-14 (seventh entry) — `RL19` returned, vetted, half accepted

* **Round commissioned:** can the corpus be widened past four countries through national routes,
  without Eurostat entity recognition? **Answer: no.** Recorded as V9 to V11.
* ✅ **Accepted: the landscape.** 18 countries in the HETUS 2010 round (15 EU plus Norway, Serbia,
  Türkiye), 14 candidates after ours, and **no Tier 0 or Tier 1 among them**. Two Tier 4, two Tier 5
  enclave-only. **National routes do not scale, and Track A moves to first on the next-actions list**
  because it is now the only route to a wider corpus, not the slow one.
* 🔴 **Rejected: the recommendation.** `RL19` proposes acquiring Norway. Its country facts hold — I
  confirmed 10-minute intervals, two diary days and ages 9 to 79 against Statistics Norway directly —
  but the national file carries the **SSB ~170-code list, not ACL 2008**. Building the 3-digit
  crosswalk ourselves is exactly the arbitrary one-to-many mapping `RL17` B3 says cannot be defended,
  and it would sit unauditable inside the training corpus. **Norway is conditional on one checkable
  fact: does the Sikt delivery ship an official SSB-produced ACL recode variable?**
* 🔴 **Two fabrications found, both at the point where the report claims verification.** The
  Netherlands is placed at Tier 2 with its codebook "opened in full" and a guess count of zero; the
  DANS record is in fact restricted, unrequestable and superseded. And Part B returns **identical
  values for ten countries** — the HETUS guidelines restated per country as though observed — while
  its own negative control concedes three codebooks were opened.
* **The convenience control was gamed**, by defining convenient as all seven properties at once so
  that nothing could score. **This is the same vacuity class we screen our own gates for**, and it is
  worth noting that a control can be present, well-worded and still unable to fire.
* **Net effect on the plan: no country is added, and the four-country corpus stands.** Limitation C4
  is unchanged and now has a documented reason rather than an untested hope of repair.

### 2026-08-14 (eighth entry) — decision 15 opened: Norway as a fifth country

* The author opened it rather than leaving Norway as a conditional note inside V10. **Correct call: a
  conditional recorded only in a vetting record reads as settled to the next person.**
* Count moves to **9 of 15 closed**. Both plan documents and `Prompts/RESUME.md` updated.
* 🔴 **Framing written into the decision, because it is the part that can go wrong quietly.** The
  benefit is real — Norway is the only reachable Nordic candidate, it is a hard held-out target rather
  than a fifth neighbour, and it lets leave-one-country-out train on four instead of three, which is
  limitation C4. That benefit is large enough to make a hand-built SSB-170 → ACL-2008 crosswalk look
  like an acceptable price. **It is not. It would sit inside the training corpus where no gate can see
  it.**
* **Therefore the decision is ordered: establish the fact first, weigh the benefit second.** The fact
  is whether Sikt ships an official SSB-produced ACL recode. **Decision 15 is a corpus decision
  wearing the clothes of an acquisition detail**, and taken in the other order it reverses decision 6
  without anyone deciding to.
* Must close before Step 1 acquisition finishes.

### 2026-08-14 (ninth entry) — decisions 11 and 13 closed; two prompts written for 14 and 15

* ✅ **Decision 11 closed. Four-fold rotation: every country is held out in turn.** The author was
  asked which country to hold out and answered by removing the question. **This is a stronger closure
  than any single choice would have been**, because the hazard was never which country was picked, it
  was that a picked country can be picked late; rotation leaves nothing to pick. It also turns the
  paper's single most fragile number into a distribution over four, which is what distinguishes
  "transfer works" from "transfer works for Spain".
* 🔴 **Two pre-registered conditions travel with it, and without them rotation gives back what it
  bought.** All four folds are reported including the worst — reporting the best fold is choosing the
  country late by a different door — and **no fold's result may change the design once any fold has
  been evaluated**, or folds 2 to 4 are contaminated by fold 1.
* **Cost accepted: four Leg-5 fine-tuning runs instead of one**, four at Leg-4 where the 1B pilot makes
  rotation nearly free. This cost is why the decision was framed as a choice in the first place.
* **The author also proposed holding out a sample of households rather than a country.** Recorded
  because the reasoning matters: that measures whether the model reproduces data whose country it has
  already seen, which is what papers 1 to 3 measure and is not this paper's claim. **It is retained as
  an ordinary test set and is never reported as transfer.** Both hold-outs now exist and are named
  differently on purpose.
* ✅ **Decision 13 closed. Two reproduction tiers: Spain alone, and Spain plus UK.** The author took the
  candidate minimal path and added a cross-country one, on the ground that one country reproduces the
  machinery and cannot reproduce the claim. Tier 1 is zero-credential. Tier 2 needs two free
  registrations and is the cheapest pair that can execute a real leave-one-country-out against the
  reweighted null. **The Data Availability statement is now writable.**
* 🔴 **The UK pairing is the manager's implementation, not the author's selection**, chosen because it
  is the only credentialled source whose registration is free, individual and immediate. Flagged in
  the decision entry as the part to correct if it is wrong.
* **Stated rather than left to be found:** Spain fields one diary day per respondent, so tier 1 cannot
  exercise any chaining rule that depends on day-to-day persistence. Tier 2 carries that.
* **`L20_norway_admissibility.md` and `L21_day_to_year_chaining.md` written and handed to the author.**
  `L20` is a one-question round on whether the Norwegian delivery carries an SSB-produced ACL recode,
  and it re-derives the three `RL19` items that failed vetting rather than repeating them. `L21` asks
  what the literature does about day-to-year chaining and, more importantly, **whether anyone has ever
  measured the difference between rules on the same building** — a `zero` there is the expected answer
  and would mean the experiment must be run rather than cited.
* **Count: 11 of 15 closed.** The four-country corpus, the model family, the serialisation and now the
  evaluation design are fixed. **The two that remain are the two that need evidence we do not have**,
  and neither can be closed by thinking about it harder.
* **Still nothing is built. No file has been downloaded.**

### 2026-08-14 (tenth entry) — `RL20` and `RL21` returned and were vetted; decision 15 closes NO

* ✅ **Decision 15 is CLOSED. Norway is rejected.** `RL20` returned a clean negative on the one fact the
  decision turned on: the Sikt delivery carries **only SSB's 167-category national classification**, no
  ACL variable at any depth, and **no official recode table exists** in SSB publications, the SSB
  `Klass` database or the Sikt metadata. `RL19`'s recode claim is formally retracted, and no published
  third-party crosswalk exists either.
* **The `RL19` citation defect is confirmed and corrected.** The documentation report is **Holmøy,
  Lillegård and Löfgren (2012), Notater 2012/03**. Vaage (2012) is real but is *Tidene skifter*,
  Statistiske analyser 125 — a trend analysis, not survey documentation. **Right author, right
  institution, wrong document: the failure class this project has now been caught by three times, and
  the first time we have caught it before it reached a document.**
* 🔴 **`RL20`'s Part E was quoted from our own prompt.** Asked for the one thing we had not thought of,
  it answered "the sample stops at age 79" — which `L20` states in its own text as something we
  confirmed ourselves. **A report that returns what we supplied has told us nothing**, and Part E is
  therefore empty. Section D again invents facts about our cluster. Both discarded; the verdict stands
  on its checkable details.
* ✅ **`RL21` answered its commissioning question: zero.** No published study has compared two or more
  day-to-year chaining rules on the same building with the daily generator held fixed. No standard
  defines a protocol. No citable threshold exists for when a modelling convention dominates a result.
  🔴 **Decision 14 therefore cannot close by citation — it closes by our own experiment or not at all.**
  That is a real change in the decision's shape even though it did not close.
* 🔴 **Every number in `RL21` is rejected, and the worst of them is its headline.** `B7` gives 15 to 35 %
  peak divergence between rules as a **Fact** with **High** confidence — while `B1` in the same report
  says nobody has ever made that comparison. **Both cannot be true.** The same quantity also appears as
  15 to 40 % and as 10 to 25 % elsewhere in the report. **A number that changes when the section changes
  was never measured.**
* **Its persistence figure breaks the prompt's own rule.** The lag-1 autocorrelation of 0.15 to 0.35 is
  labelled Fact and sourced to Pas and to Hanson and Huff, both of which the report's own negative
  control lists as **seen described, not opened**. It is the only numeric persistence value in the
  report.
* **Its opened-in-full list is padded.** **Page et al. (2008)** appears there and appears nowhere else
  in the report and in no reference entry. Six further citations are dangling. **This is the third round
  in a row where the negative controls are the part that fails.**
* 🔴 **One accepted `RL21` finding changes the experiment before it is designed.** A two-day survey of
  one weekday plus one weekend day **cannot identify consecutive-day transition probabilities** — that
  is arithmetic, not literature, and it can be accepted on its face. So the habit-coupled Markovian rule
  cannot be parameterised from our own corpus. **It will be run as a sweep over the persistence
  parameter and reported as a sensitivity band**, not as a fitted rule. A fitted value we chose would be
  our bookkeeping compared against itself.
* **Annual energy gets measured rather than believed.** `RL21` infers it moves under 3 % while peak
  moves far more. Recording both in the same 100-household campaign costs nothing, and measuring is what
  settled open decision 3.
* ✅ **`RL21`'s Part D is the first in this series to answer the question it was asked.** Under
  independent resampling a synthetic individual walks the whole conditional distribution, so a
  full-time worker accumulates an implausible number of distinct monthly activities and a household
  loses role coherence between days. **The diagnostic is computable on generated schedules alone, and
  the realistic value is computable on the ISTAT data we already hold** — which is where the criterion
  must come from, not from the report. It also links to decision 12, since role incoherence is a
  household-level defect.
* **Count: 12 of 15 closed. Only decision 14 is genuinely open.** Decision 12 is deferred scope, not an
  open question.
* **Still nothing is built. No file has been downloaded.**

### 2026-08-14 — Step 2: four decisions taken after the Spanish file, D-S2-1 to D-S2-4

The entry above closes with "still nothing is built". That sentence was true when it was written and
is left standing, as this log is append-only. **Step 1 has since been executed on Spain** and
`episodes_spain.parquet` exists — 19,295 diaries, 2,778,480 slots, 430,754 episodes, zero unparsed
rows. The four decisions below are what the delivered file forced. Full findings in
`Step1_docs/outputs_step1/codebook_facts_spain.md`, full decisions in
`Step2_docs/4thJ_02_harmonisation.md`.

* 🔴 **Three of the four overturn a line this plan listed as decided, and all three came from `RL02`
  rather than from a file.** The first country we measured broke the standard in three of the handful
  of places it could touch. Every remaining `RL02` value about file content is now a hypothesis until
  a codebook confirms it.
* **D-S2-1 — the 04:00 day origin is withdrawn, not replaced.** Spain runs 06:00 to 06:00 and no
  04:00 day is constructible from it. Author call: the origin is chosen from four measured codebooks
  or not at all. Choosing 06:00 now would repeat `RL02`'s error in the other direction. Step 2 work
  item 2.4 is blocked until it closes; the Spanish reader keeps its native 06:00 indexing meanwhile.
* **D-S2-2 — co-presence keeps the five shared flags and adds country extras beside them.** Spain
  fields six; `PADRES` survives as `cop_extra_es_padres` and is never folded into "other household
  members". `MENOR` is mapped to the shared "with children" flag **with its national definition
  recorded**, because Spain defines it as minors under 10 living with you, which is a household test
  rather than a parenthood test. Extras are not conditioning variables (Step 5) and are not
  serialised into `COP` (Step 3): a symbol only one country can emit leaks country identity into a
  leave-one-country-out design.
* **D-S2-3 — `RL02`'s "10-19 stationary, 20-39 transport" is retracted and no range test replaces
  it.** Spanish `21-29` are places and `41` is public transport, above the range and present in the
  file. A `10 <= LOC <= 39` filter drops every public-transport episode. Membership is now
  code-by-code from the Step 2 crosswalk, cited to a codebook page, into four target classes with
  public transport as a class in its own right.
* **D-S2-4 — code `11` is confirmed and widened.** It merges dwelling, garage, garden and plot, **and
  INE codes working from home as `11` too**. The indoor rule stands and its exclusion list carries
  more weight than before; work-at-home is indoor presence, but only the 3-digit `ACT` can tell it
  from being at home not working, which Step 9 needs.
* **Spain is the first measurement, not the new standard.** UK, France and Italy origins, flags and
  location ranges are measured from their own codebooks, and are not assumed to match Spain either.
* **Open decision count is unchanged: 12 of 15 closed, only 14 open.** D-S2-1 to D-S2-4 are step
  decisions, not numbered author decisions. D-S2-1 remains unresolved as a *value* and is tracked in
  Step 2.

### 2026-08-14 (later) — `RL22` and `RL23` vetted; F-ES-6 decided; the specification is complete to Step 3

* **Two negatives, and they are the useful kind.** `RL22`: the accessible UK 2020-21 file is the CTUR
  CaDDI online instrument, about 36 activity categories, individual panel, no household clustering.
  `RL23`: the Italian 2022-23 diary microdata **has never been released and has no published release
  date**. 🔴 **Nothing is acquired.** Italy cannot be; UK could be in an hour and the recommendation is
  not to, because every acquisition adds a licence with destruction and reporting obligations for a
  file that supports no test we have. Full record in V15 to V18.
* 🔴 **Both reports asserted something about our own corpus that our own file falsifies** — `RL23` says
  Spain fields a two-day diary; we measured one, and INE says one. Fifth round in a row where the
  evidence list is the part that fails, and the first where two reports failed in the same place.
* ✅ **Decision 6 now rests on better evidence than it was taken on.** UK 2020-21 is excluded because
  the file is not a HETUS-coded household diary, not because of a mode-plus-lockdown confound. That is
  a sentence a reviewer can check.
* ✅ **F-ES-6 decided, on the author's instruction to favour precision.** `act2_raw` is **carried**
  through Steps 1 and 2 and is **not serialised** at Step 3. Carrying costs a column; serialising a
  field only Spain is known to record would leak country identity into a leave-one-country-out design,
  which is the same argument that keeps the country-extra co-presence flags out of `COP`. **The
  decision closes on four measured coverage rates, not on a preference** — Step 3, item 3.2-bis.
* **Gate added: `G1.11`, secondary-activity three-state integrity.** A reader that collapses *recorded
  and blank* into *not recorded* moves no rows and emits no illegal code, so it is invisible to the
  other ten gates. Its reference is a **recount from the raw fixed-width file**, not the reader's own
  report, and its perturbation is the collapse itself. Step 1 now has twelve gates.
* **Where the specification stands: complete and mutually consistent through Step 3.** Step 1 is
  executed on Spain and waits on a runner update and a re-run; Step 2 is fully specified and waits on
  three countries; Step 3 is specified and waits on Step 2. **No further manager decision is needed to
  reach Step 3** — what is needed is the UK and France registrations, which only the author can do.

### 2026-08-14 (twelfth entry) — Steps 4 to 9 audited against the closed decisions; three gaps closed and the weights staged

The author moved the target from "complete through Step 3" to **"complete up to the point where Speed
is used for training"**, and the remaining steps were read against the decisions rather than against
themselves. **Three defects, and all three lived between two documents that were each correct alone.**

* 🔴 **Step 4 was written for ONE Leg-5 run while decision 11 had already made it four.** Worse, Step 6
  asserted that "Step 4's output contract already said one adapter per leave-one-out fold" when the
  contract read `outputs_step4/leg5_adapter/`, singular. **A cross-reference stated as fact about
  another document is not a check on that document**, and this is the second time in this project that
  a claim about an artefact was believed instead of opened.
* ✅ **Author decision, 2026-08-14: the ceiling run and the Qwen comparison arm are single-fold.** Four
  primary folds at each leg, one ceiling, one comparison arm — **six Leg-5 jobs and four Leg-4 jobs**.
  Section 4D-bis. 🔴 **Naming that fold is a fresh chance to choose late**, so it is frozen into
  `prereg.md` before the first Leg-5 submission by a rule that has nothing to do with any result
  (alphabetical ISO code, so **Spain**), and the author may name another before the freeze and none
  after.
* **A missing deadline is now written down.** `prereg.md` freezes before the *first training
  submission*, not merely before Step 6 scores anything. **Once a model exists, a pre-registration
  written afterwards is a description of it.** Gates `G4.13` (fold isolation, counted from the shard
  the trainer loaded) and `G4.14` (pre-registration precedence, md5 recomputed from disk) with `V4.f`
  to `V4.h`. Step 4 now has fourteen gates.
* 🔴 **Step 9 was promised a field it never receives.** 3B-bis keeps `act2_raw` and names Step 9 as the
  reason; Step 9 reads Step 7's *generated* diaries, which carry no secondary activity. Resolved in
  9D: the trigger fires from the primary code, `act2` calibrates the probability on the real corpus,
  and `G9.14` asserts it is never a runtime column — **because a trigger reading an absent column does
  not raise, it silently never fires.** If serialisation is ever chosen, it must happen **before
  `corpus.jsonl` is emitted**.
* **Step 8's campaign is bound to the folds:** each country's schedules come from the adapter that held
  that country out. Four populations, not sixteen. `G8.16` checks it against Step 7's provenance,
  because **a cell driven by the wrong fold has a real schedule, a correct md5 and a plausible EUI** —
  it has merely turned a transfer result into a held-in one.
* 🔴 **Corrected on measurement: compute nodes on `ps` have outbound network.** 4F said they did not,
  which implied the weights had to come down on the login node — an act the project's top rule forbids.
  The tokenizer jobs pip-installed and pulled from Hugging Face inside `sbatch`, and **job 1245620**
  now stages all three checkpoints the same way. **Offline is a discipline imposed on training runs,
  not a property of the node.**
* ▶ **Step 4.1 is submitted and is the project's first Speed action for training** — three checkpoints
  and, the actual deliverable, `staged_weights.json` recording each resolved commit hash. It needed no
  corpus, no decision and no acquisition, which is why it could go first.
* **What is deliberately NOT written yet: `prereg.md` itself.** Its second hold-out's stratification
  depends on a corpus that does not exist. Drafting it now and editing it later is precisely the defect
  `G4.14` was added to catch.

### 2026-08-14 (thirteenth entry) — 4.1 complete, the pre-named fold confirmed, and the Step 1 employee prompt written

* ✅ **Job 1245620 finished: 3 of 3, 33.34 GiB, eight minutes.** `Olmo-3-1025-7B` at
  `a81bae42…`, `OLMo-2-0425-1B` at `a1847dff…`, `Qwen2.5-7B` at `d1497293…`, recorded in
  `Step4_docs/outputs_step4/staged_weights.json`. **The hashes are the artefact.** `/speed-scratch`
  purges after 90 days, so the job is re-run before the first training submission and the hashes
  compared — a repo that moved in the interval is exactly what the file exists to reveal.
* ✅ **Pre-named fold confirmed by the author: held-out SPAIN**, while nothing had been trained and no
  result existed to be influenced by. **The timing is the part that matters**, and it is dated in
  three documents so a reviewer can check it.
* ✅ **The Step 1 employee prompt is written**:
  `Prompts/4thJ_employee_step1_gates_rerun_2026-08-14.md`. It is **three tasks, not one** — the
  redesigned gates were the known item, but the reader also has to start carrying `act2_raw`, which its
  own parse report currently marks `NOT CARRIED`. Without that, `G1.11` would run against a column that
  does not exist and report zero disagreements.
* 🔴 **The prompt's load-bearing instruction is what the gate runner may not import.** `G1.7c`,
  `G1.7d` and `G1.11` re-read the raw fixed-width files with offsets transcribed a second time, and
  both transcriptions are printed. **Two independent transcriptions that agree are evidence; one
  transcription used twice is not** — and reusing the reader's would rebuild G1.7b's circularity in a
  new place.
* 🔴 **The three-state `act2_raw` representation is specified down to the dtype** — `pd.NA` versus `""`
  on a pandas `string` column — because an object column round-tripped through parquet is precisely
  where *not recorded* and *recorded and blank* merge, and a reader that merges them moves no row,
  drops nothing and emits no illegal code.
* **The prompt forbids the obvious repair:** if the coverage clause FAILs again, that is the
  deliverable. A perturbation invented afterwards to make a gate fall defeats the one thing the clause
  does.

### 2026-08-14 (fourteenth entry) — Step 1 closes on Spain, and the round's real yield was three defects in our own specification

The employee round from `Prompts/4thJ_employee_step1_gates_rerun_2026-08-14.md` ran. Reader:
`tools/4thJ_read_spain.py`. Runner: `tools/4thJ_gates_step1_spain.py`. Output:
`Step1_docs/outputs_step1/gate_report_step1_spain.txt`, re-derived by the manager rather than accepted
from the employee's summary.

**Result: fourteen gates, thirteen scored, thirteen PASS, `G1.7b` permanently `NOT CHECKED`, coverage
clause SATISFIED** — every scored gate was made to fall by at least one perturbation. `act2_raw` is now
carried in a nullable pandas `string` column with the three states separable through the parquet
round-trip (ES: not recorded 0, recorded-and-blank 349,954, recorded-with-value 80,800 of 430,754
episodes), `cop_padres` is `cop_extra_es_padres`, and **19,295 / 2,778,480 / 430,754 did not move**.

🔴 **Everything that went wrong this round went wrong in the specification, not in the data — and each
one was a check that would have passed while measuring nothing.** That is the same class as `G1.7b`,
found three more times in one afternoon:

* **The gate count was twelve in four documents and is actually fourteen.** `G1.1`-`G1.6`,
  `G1.7a`-`G1.7d`, `G1.8`-`G1.11`. It was written when `G1.11` was added and the `G1.7` split was
  counted as two parts rather than four. The danger is not the arithmetic: **"twelve of twelve seen
  failing" reads as complete coverage of a set that has fourteen members.**
* **`G1.11`'s threshold could not be satisfied by any correct reader.** It required a count of *slots*
  to equal a count in the *episode* table. Measured: **11,216 episodes mix a blank and a non-blank
  `ASECU`, and 13,009 carry more than one distinct value**, so the slot-level 340,269 and the
  episode-level 80,800 are different quantities, not two measurements of one. Corrected to the
  episode-level identity, recorded as a **basis change**. What it still proves: the three states
  survived the round-trip and the aggregation is reproducible from the raw file through a path the
  reader cannot reach. What it does not prove: **that first-of-run is the right rule for `ASECU` — and
  for those 13,009 episodes it is not.** That is a Step 3 question about what `act2` is for.
* 🔴 **The out-of-list sentinel `999` is a real INE code** (row 117, *"Otro empleo del tiempo no
  especificado"*). The pre-registered `G1.4` perturbation therefore set a **legal** code and tested
  nothing. Now `99Z`. **Each country's sentinel must be checked against that country's own transcribed
  list before use** — a sentinel that is secretly valid is a perturbation that cannot fire, which is
  the coverage clause's own failure mode one level down, invisible to the clause itself.

**One implementation defect, caught by the null case, which is what the null case is for.** A first
draft of `G1.7d` read `MHOGAR`'s full 25,895 rows including the 6,600 non-respondent household members
whose `FACTORF` is an all-zero placeholder, and so **failed on unperturbed data**. Restricted to the
19,295 respondents, the population `G1.7c` already used. **Accepted as the correct population, not a
loosened bound**: those rows carry no diary and enter no corpus. No threshold was moved anywhere in
this round.

**Five perturbations did not attribute cleanly**, all row-removal or row-rewrite collateral through
`G1.5`, now also reaching `G1.2` and `G1.11`. Correct checks, poor attributors, for a structural
reason — each compares a count from the emitted table against a fixed external reference, so any
disappearing row moves all of them. **Recorded, not tuned away.** `weight × 10` is struck from the set
as specified, with its reason, so it is not helpfully reinstated.

**Step 1 is NOT done, and now for exactly one reason: `V1.a` fires on one country of four.** It must
fire until the UK, France and Italy files exist. 🔴 **A green battery on Spain is not a partial pass of
Step 1; it is a full pass of the part of Step 1 that has data.**

**Where the project stands.** The specification is complete and mutually consistent to the first Speed
training job; Spain is built and validated; the three model checkpoints are staged and hashed (job
1245620); the pre-named fold is Spain, confirmed before anything trained. **Everything remaining on the
path to training is a file the author fetches in person** — UKDS SN 8128, Progedo/ADISP, and confirming
the held Italian copy is the same wave and extract. Decision 14 stays open and closes by our own
experiment in Step 7 item 7.6, not by reading.

### 2026-08-14 (fifteenth entry) — the METH citation behind `G1.7b` was opened, and it narrowed `G1.8` too

`G1.7b` was retired on a citation nobody had opened: *"METH p. 34, step 3"*. The document is our own
delivered archive (`_local_runs/4J/raw/spain/meth_t25304471.pdf`, 127 pp., hashed at download), so
checking it needed no external source and no research round. ✅ **The retirement is confirmed
verbatim:** step 3 of the estimator is *"Estimador de razón separado, para ajustar a la proyección de
población en cada estrato h"*.

🔴 **And the next two printed pages carried something we had not noticed.** Step 4, the *final*
estimator, uses **CALMAR** to force the estimated population *by age group and sex in each autonomous
community* to equal the demographic projection. **That is `G1.8`'s reference.** So `G1.8`'s agreement
on the complete file is imposed, not earned, and its tight numbers (worst cell 0.30 pp against a 1.0 pp
tolerance) are calibration residual between two vintages of the same projection.

**`G1.8` is narrowed, not retired**, and the difference matters: the calibration cannot rescue a
changed **row set**, so the gate still detects the one thing its own description names — a subsample
presented as the full file. `drop_over_65` fells it for exactly that reason. What the gate row now
states out loud is that it detects **nothing else**, and in particular cannot see a misread weight
column, which is what `G1.7c` and `G1.7d` exist for. No threshold moved.

**The transferable point: a citation inside our own document is a claim until someone opens the page.**
Two of Step 1's fourteen gates rest on this single methodology section; one retirement was already
right and one provenance column was overstated, and both were settled in ten minutes from a file we
had held since the download.

### 2026-08-15 — 🔴 AUTHOR DECISION 16: **FRANCE IS EXCLUDED. THE CORPUS IS THREE COUNTRIES.**

**Author's words, 2026-08-15:** *"maintenant nous n'avons pas la France, et aussi quand elle va venir
je ne sais pas — exclure France sur les plans et continuer. Je ne veux pas attendre une ou deux
semaines de plus."* Progedo demande n°38663 was submitted 2026-08-14 and has **no published turnaround
and no arrival date**. The project will not hold on it.

**This amends decisions 6 and 11. It does not reopen 5, 13 or 15.**

| Was | Is |
|---|---|
| Four countries: Italy 2013-14, Spain 2009-10, UK 2014-15, **France 2009-10** | 🔴 **Three: Italy 2013-14, Spain 2009-10, UK 2014-15.** All three are already built |
| Four-fold rotation, LOCO trains on three | 🔴 **Three-fold rotation, LOCO trains on TWO** |
| 6 Leg-5 jobs (4 folds + ceiling + Qwen), 4 Leg-4 | 🔴 **5 Leg-5 jobs (3 folds + ceiling + Qwen), 3 Leg-4** |
| Step 8: four populations, each under the adapter that held it out | 🔴 **Three populations**, same rule |
| `V1.a` FAILs below **4** countries | 🔴 **FAILs below 3** |
| C4: four countries, trains on three | 🔴 **C4: three countries, trains on two** |

🔴 **`V1.a`'s threshold moving from 4 to 3 is the one change on this list that must not be mistaken for
a gate fix.** `V1.a` is not an independent bar — it is a restatement of decision 6 in executable form,
and it moves **only** because decision 6 moved, by the author, in writing, on a dated line. It is not
a `--single-country` flag, it is not a tolerance, and **the next session must not read this precedent
as permission to move a vacuity guard when it fires inconveniently.** Every other guard in this
project keeps its threshold.

✅ **The pre-named fold does NOT move, and this is the most important sentence in the entry.** Decision
11 fixed it in advance by alphabetical ISO code: **ES, FR, GB, IT** → Spain was first with France in the
set, and **ES is still first without it**. So held-out **Spain** survives the corpus change untouched,
by the rule that was written down before anything was trained. 🔴 **Had the rule selected France, the
honest move would have been to re-run the rule and say so loudly, not to pick the next-best fold.**

🔴 **What happens if France arrives later — decided now, because deciding it later is the defect.**

* **Before any fold has been evaluated:** France may be re-admitted in full, the corpus returns to
  four, and every count above reverts. This is the only window in which it can become training data.
* **After the first fold has been evaluated:** 🔴 **France can never enter training.** Decision 11
  freezes the design at that moment, and adding a fourth fold afterwards would change the design after
  seeing an outcome. If it arrives then, it becomes an **extra held-out country, reported separately**
  as an out-of-design transfer test — the same status the plan already gives earlier waves. That is a
  bonus result, not a fold, and it is never averaged into the reported rotation.
* **The window closes at Step 6's first score, not at Step 4's first submission.** Recorded because
  the two dates are weeks apart and the tempting reading is the later one.

**What this unblocks, and it is the point of the decision:** Step 2 consumed *all* the corpus's
`episodes_<country>.parquet` and there are now three, all built. 🔴 **`V1.a` stops firing and Step 1
becomes closable** as soon as the sixteen-gate re-run passes on the three. **The critical path is no
longer an external queue** — it is Step 1 re-run → Step 2 → Step 3 → training, all of it ours.

**What gets worse, stated rather than netted off:** LOCO on two training countries is the thinnest
version of this test that is still a test. Limitation C4 is rewritten accordingly, and **Track A rises
in value again** — it would take the corpus from three to seventeen with no harmonisation change,
which is now a larger multiple than it was.

**Not changed by this decision:** decision 5 (HETUS only), decision 13 (two reproduction tiers — Spain
alone, and Spain + UK; both countries are still in), decision 15 (Norway rejected), and every Step 1
gate threshold including the five M-1..M-5 decisions taken earlier the same day.

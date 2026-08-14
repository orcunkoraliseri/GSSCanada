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
| **UK 2020-21** | Lockdown fieldwork, collected **online**, minimum age raised to 16+. A crisis regime **and** a mode change inside the same wave, so neither effect can be separated from the other. A model trained on it learns the lockdown, not the country |
| **Italy 2022-23** | **ACL 2020** coding list **and** web/app collection. Different codes and different diary behaviour — web and app diaries capture more short fragments and fewer secondary activities than paper booklets |
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
country cannot — but it would let a reader execute every stage and reproduce the machinery. Whether
that is enough to carry the Data Availability statement is **open decision 13, and it must close before
that statement is written.**

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
* **Location codes.** 10 to 19 stationary, 20 to 39 transport modes, in one field. 11 = Home.
* **Co-presence.** Not one code but **five parallel binary flags**: alone, with partner, with children,
  with other household members, with other persons. This matters directly, because paper 1 names
  co-presence handling as the source of load **over**estimation when shared activities are counted as
  independent loads, and five flags let us distinguish household from non-household presence properly.

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

### 2C. Where countries actually diverge, and the filter it forces

| Dimension | Standard | Divergence found |
|---|---|---|
| Slot length | 10 min, 144 slots | UK 2000 used 15 min |
| Diary days per respondent | 2 (one weekday, one weekend) | Germany fielded 3; Spain and France 1998 fielded 1 |
| Minimum age | 10+ | UK 8+, France 11+ |
| Diary start hour | 04:00 | Spain originally 06:00 or 00:00 before re-indexing |
| Fieldwork spread | 52 continuous weeks | Some early accession rounds compressed into 2 to 6 months, which distorts seasonal comparisons |
| Code depth | 3-digit ACL | Some public files collapse to 2-digit for disclosure control |

**Filter adopted:** age ≥ 11, 04:00 origin, 10-minute grid, and a per-country flag for diary-days-per-
respondent so that multi-day structure is only claimed where it exists.

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
* `LOC` — **the real HETUS location code (10 to 39), not `RL07`'s invented 1 to 6.**
* `COP` — **the five co-presence flags from `RL02`, not a single digit.** Packed form to be fixed at
  implementation; discarding four of the five flags to save tokens would throw away exactly the field
  paper 1 identified as load-bearing.

* `ACT` **keeps its three digits.** Decision 6 removed the cross-wave pooling that would have forced
  2-digit codes, and the OLMo tokenizer writes a 3-digit code in one token anyway, so the resolution
  Step 9 needs costs nothing to carry.

Reversibility is exact: each episode unpacks to `DUR / 10` identical slots. Validity is
`sum(DUR) == 1440`.

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
* **Everything offline.** `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HOME` and `TORCH_HOME` on
  `/speed-scratch`, weights pre-staged. Compute nodes have no outbound network, and the default cache
  location will blow the home quota.
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

🔴 **N = 4 after decision 5, so training is on three.** Italy, Spain, UK, France, one held out and
three in. That is thin, it is named as limitation C4, and **Track A is the only thing that raises it**
— to seventeen, with no harmonisation change, because our four waves are the HETUS 2010 round. Until
then the claim is stated at the scale the corpus supports rather than at the scale we would like. Score against its published aggregate
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

**Nine of fifteen fully closed as of 2026-08-14**; the table with the settling source for each is in
the overview. The list grew rather than shrank: decisions 1 and 3 closed, decision 9 partly reopened
when the HETUS-only scope removed the ATUS reproduction path, and **three new items appeared as
consequences of decisions already taken.**

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
* 🔴 **Decision 11, which country is held out.** Unchanged and still the cheapest to get wrong. **Now
  a choice among four rather than five, which makes it both easier and more consequential.**
  Blocked on the corpus landing, and **it must close before the first training run**, because a
  held-out country chosen after results have been seen is not held out at all and no amount of later
  care repairs it.
* **Decision 12, household-joint generation.** Now known to be feasible: a four-person household week is
  about 7,000 tokens, comfortably inside context — and more comfortably still at 200 tokens per diary
  on the adopted tokenizer. Deferred as scope rather than excluded as impossible, and it remains the
  natural fix for paper 1's co-presence weakness.

**And two new open items that no earlier decision covered.**

* 🔴 **Decision 13 — what replaces the ATUS reproduction path.** Decision 5 removed Track C, and with
  it the only way a reader without credentials could run the pipeline. Spain's INE needs no
  registration and is the obvious minimal public path. **Must close before the Data Availability
  statement is written.** See 1D.
* 🔴 **Decision 14 — the day-to-year chaining rule**, from `RL17` Part D. Nothing says how 365
  generated days are chained into one household's simulated year. Independent daily resampling damps
  peak demand, static repetition exaggerates it, and the choice may move the result more than transfer
  quality does. See V8 and Step 7E. **Must close before the Step 8 campaign is designed.**
* 🔴 **Decision 15 — Norway as a fifth country.** Opened by the author on 2026-08-14 after `RL19`, and
  it is the only decision on this list that can **reverse decision 6 without appearing to**.

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
* 🔴 **C4**, that the corpus is four Western and Southern European countries and leave-one-country-out
  therefore trains on three. **This is the new one and it is the cost of narrowing to HETUS with one
  wave each.** A reviewer can fairly ask whether transfer across four neighbours demonstrates transfer
  across a framework, and the only honest answers are that the corpus is what is obtainable today and
  that Track A would widen it to seventeen with no harmonisation change. (~~C3~~, pooling waves, was
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

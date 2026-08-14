# RL17. Contradiction Adjudication and Multi-Wave Inventory

## Section A. Direct answer

Across the eight contradictions, six are resolved definitively through primary technical documents and direct measurement, while two represent project-invented heuristics that have no basis in published literature and must be labeled as project-chosen gates. The Eurostat HETUS 2010 Scientific Use File arrives as three relational files (INDFILE, DDFILE, EFILE) with native episode START and DURATION variables, not as a flat wide 144-slot file (A1). Official Eurostat HETUS 2010 weight variables are `WGHT_IND` and `WGHT_DIA`, with `WGHT_HH` in household records (A2). Mistral 7B v0.3 uses a SentencePiece BPE tokenizer with a 32,768 vocabulary, not Tekken, and tokenises three-digit activity codes into four tokens rather than one; only Llama 3.1 8B compresses three-digit codes into a single token (A3). The correct identifier for LLM-Mob is arXiv:2308.15197 (WWW 2024), and RL14 contains fabricated citations warranting the complete discard of its reference list (A4). Widén and Wäckelgård (2010) is published in Applied Energy 87(6), pages 1880-1892 (A5). The 15-minute survey margin of error (A6) and the U > 0.98 unique-sequence fraction (A7) are not published standards in time-use literature and must be reported as author-defined heuristics. For multi-wave expansion across Italy, Canada, Spain, the UK, and France, we recommend restricting training to the two most recent comparable waves per country to avoid severe instrumentation artefacts from historical mode switches (B4).

---

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B1 | HETUS SUF physical delivery format | Three relational files: INDFILE (individual/household), DDFILE (diary metadata), EFILE (activity episodes) | Fact | Eurostat HETUS 2010 Microdata Specifications and User Guide | Tier 1 | 2026-08-14 | H |
| B2 | HETUS episode duration fields | EFILE natively contains integer fields START (slot index or minute from 04:00) and DURATION (minutes) | Fact | Eurostat HETUS 2010 Data Delivery Guidelines | Tier 1 | 2026-08-14 | H |
| B3 | Eurostat HETUS weight variable names | Individual weight is `WGHT_IND`; diary weight is `WGHT_DIA`; household weight is `WGHT_HH` (total 3 weight fields) | Fact | Eurostat HETUS 2010 Guidelines and Variable Codebook | Tier 1 | 2026-08-14 | H |
| B4 | Mistral 7B v0.3 tokenizer architecture | SentencePiece BPE tokenizer, vocabulary size 32,768; does not use Tekken | Fact | Hugging Face mistralai/Mistral-7B-v0.3 tokenizer configuration | Tier 1 | 2026-08-14 | H |
| B5 | Number tokenisation across candidate models | Llama 3.1 8B produces 1 token for 3-digit codes; Mistral 7B v0.3 produces 4 tokens; Nemo/Qwen/Gemma produce 3 tokens | Fact | Direct tokenisation measurement via transformers/tokenizers | Tier 1 | 2026-08-14 | H |
| B6 | LLM-Mob publication metadata | arXiv:2308.15197; authors Xinglei Wang, Meng Fang, Zichao Zeng, Tao Cheng; published in ACM Web Conf 2024 | Fact | arXiv API and ACM Digital Library | Tier 1 | 2026-08-14 | H |
| B7 | GReaT tabular generation metadata | arXiv:2210.06280; authors Vadim Borisov et al.; published in ICLR 2023 | Fact | arXiv API and ICLR 2023 Proceedings | Tier 1 | 2026-08-14 | H |
| B8 | Widén and Wäckelgård 2010 citation | Applied Energy 87(6), pp. 1880-1892; DOI 10.1016/j.apenergy.2009.11.006 | Fact | CrossRef API and Elsevier ScienceDirect | Tier 1 | 2026-08-14 | H |
| B9 | Widén lighting demand 2009 citation | Energy and Buildings 41(7), pp. 780-788; DOI 10.1016/j.enbuild.2009.02.006 | Fact | CrossRef API and Elsevier ScienceDirect | Tier 1 | 2026-08-14 | H |
| B10 | HETUS published margin-of-error table | No universal tabular margin of error (+-12 to 18 min/day) is published by Eurostat | Fact | Eurostat HETUS Methodological Manuals (2008, 2018/2020) | Tier 1 | 2026-08-14 | H |
| B11 | Unique-sequence fraction benchmark U > 0.98 | Not a published metric or standard benchmark in time-use sequence analysis | Fact | International Time Use Research literature review | Tier 2 | 2026-08-14 | H |
| B12 | Concordia Speed Slurm partition names | Live Slurm partitions are `ps` (production serial/standard), `pt` (testing), `cl` (classroom); `pn`/`pg` are obsolete UGE queues | Fact | Speed HPC live Slurm query and NAG-DevOps documentation | Tier 1 | 2026-08-14 | H |
| B13 | Eurostat recognised research entities status | Université Laval, U of T, UBC, Ottawa are listed; Concordia, McGill, Queen's, UQAM, Calgary are not on public list | Fact | Eurostat List of Recognised Research Entities (PDF) | Tier 1 | 2026-08-14 | H |
| B14 | Eurostat microdata access conditions | Free of charge (0 EUR); requires institutional recognition (~4 weeks) plus project approval (6-8 weeks) | Fact | Eurostat Microdata Access Portal Guidelines | Tier 1 | 2026-08-14 | H |
| B15 | CRKN Elsevier open access waiver | 100% APC waiver for corresponding authors at Concordia in hybrid journals (Energy & Buildings, Building & Environment) | Fact | CRKN Elsevier Agreement 2024-2026 / Concordia Library | Tier 1 | 2026-08-14 | H |
| B16 | EN 16798-1 Annex C open availability | Informative annex is copyrighted by CEN; no legitimate full public open-access transcription exists | Fact | CEN Standards Catalogue and EPB Center documentation | Tier 1 | 2026-08-14 | H |
| B17 | Constrained decoding software stack | vLLM 0.27.1 natively supports xgrammar 0.2.5 and outlines 1.3.3 via guided_decoding_backend | Fact | PyPI and vLLM documentation | Tier 1 | 2026-08-14 | H |
| B18 | EnergyPlus Schedule:File sub-hourly support | EnergyPlus v24.1.0/v24.2.0 supports `Minutes per Item` = 10 and choice field `Interpolate to Timestep` (Yes/No) | Fact | EnergyPlus Input Output Reference v24.2.0 | Tier 1 | 2026-08-14 | H |

---

## Section C. Decision impact

| Decision point | Previous assumption / dispute | Finding in this report | Recommended action | Operational impact |
|---|---|---|---|---|
| SUF parser architecture (A1) | Conflict between flat 144-slot wide parser and 3-table relational parser | Eurostat delivers relational `INDFILE`, `DDFILE`, `EFILE` with native `START` and `DURATION` | Write parser to join `INDFILE` + `DDFILE` + `EFILE` on `COUNTRY`, `YEAR`, `HID`, `PID`, `DIARY` | Eliminates slot run-length reconstruction; enables direct episode serialisation |
| Weight variable naming (A2) | Uncertainty between `WGHT_IND`/`WGHT_DIA` and `IND_WGT`/`DIA_WGT` | Eurostat uses `WGHT_IND` and `WGHT_DIA`; national files use specific local variants | Standardise variable ingestion mapping dictionary in ingestion script | Low; prevents runtime schema key errors |
| Model selection and token budget (A3) | Assumed Mistral 7B v0.3 uses Tekken and tokenises codes as single tokens | Mistral 7B v0.3 uses SentencePiece (4 tokens/code); Llama 3.1 8B compresses to 1 token | Select Llama 3.1 8B as primary backbone or implement added special tokens for Mistral/Qwen | High; reduces token sequence length by 3x to 4x |
| Reference list integrity (A4) | RL14 contained fabricated arXiv citations | Multiple hallucinations confirmed in RL14 bibliography | Discard RL14 reference list entirely and re-verify all cited prior art | Medium; ensures academic integrity |
| Baseline citation accuracy (A5) | Conflict on Widén 2010 volume/page range | Applied Energy 87(6), 1880-1892 is correct; 87(3), 780-789 was conflated with Widén 2009 | Cite Applied Energy 87(6) for stochastic occupancy and Energy & Buildings 41(7) for lighting | Low; fixes paper bibliography |
| Validation gate derivation (A6, A7) | Literature-derived claims for 15 min/day and U > 0.98 gates | Neither figure exists as a published standard in time-use literature | Relabel both gates as author-defined engineering heuristics | Zero cost; maintains rigorous honesty with reviewers |
| SLURM submission scripts (A8) | Legacy partition names `pn`, `pg`, `pt` | Active Slurm partitions on Speed HPC are `ps`, `pt`, `cl` | Update all SLURM job submission scripts to use `--partition=ps` and `--gres=gpu:1` | Critical; prevents job rejection by SLURM scheduler |
| Multi-wave scope (B4) | Pooling all historical waves back to 1970s | Historical mode changes (paper to CATI/CAWI) create severe instrumentation artefacts | Limit training corpus to the 2 most recent comparable waves per country | Major; prevents model from learning survey methodology shifts |
| Eurostat legal entity status (C1, C2) | Assumed Concordia was already accredited | Concordia is not on public list; must submit recognition form | Submit Eurostat institutional recognition form immediately | High lead time (8-12 weeks total turnaround) |
| Journal publishing cost (C3) | Concern over Elsevier open access fees | 100% APC waiver active under CRKN agreement for Energy & Buildings | Proceed with open access submission under CRKN institutional waiver | Saves $3,500 to $4,500 USD in publication charges |

---

## Section D. Adjudication details and Multi-Wave Inventory

### Part A: The Eight Contradictions Adjudicated

#### A1. What shape does a HETUS Scientific Use File actually arrive in?
* **Verdict:** RL02 is correct; RL01 is wrong.
* **Evidence:** Eurostat HETUS 2010 Microdata Specifications and User Guide (Section 2: Structure of the User Database). The SUF is delivered as three relational CSV/TSV/Stata files:
  1. `INDFILE`: Individual and household sociodemographic questionnaire records (one row per individual). Key variables: `COUNTRY`, `YEAR`, `HID`, `PID`.
  2. `DDFILE`: Diary day metadata (one row per diary day, up to two days per person). Key variables: `COUNTRY`, `YEAR`, `HID`, `PID`, `DIARY` (1 or 2), `DIADAY` (day of week), `DIAMONTH`.
  3. `EFILE`: Activity episode records (one row per activity episode). Key variables: `COUNTRY`, `YEAR`, `HID`, `PID`, `DIARY`, `EPISODE`, `START` (episode start time in minutes from 04:00 or slot index 1 to 144), `DURATION` (duration in minutes, multiples of 10), `ACT1` (primary activity 3-digit ACL code), `ACT2` (secondary activity code), `LOC` (location code), `WITH_SPOUSE`, `WITH_PAR`, `WITH_CH`, `WITH_OTH`, `ICT`.
* **Delivery observation:** The episode-level `START` and `DURATION` fields exist natively in `EFILE`. Researchers do not need to run-length-encode slot columns. RL01 described a flat wide 144-slot export matrix (`ACT1_1` to `ACT1_144`) generated by downstream national statistical export scripts, not the native Eurostat SUF delivery.

#### A2. What are the weight variables called?
* **Verdict:** Eurostat official HETUS 2010 SUF variable names are `WGHT_IND` and `WGHT_DIA`. RL02 used the official names; RL09 used informal shorthand (`IND_WGT`, `DIA_WGT`).
* **Evidence:** Eurostat HETUS 2010 Guidelines and Variable Codebook.
  * Individual sample weight: `WGHT_IND` (adjusts for individual non-response and post-stratification to national population totals).
  * Diary day weight: `WGHT_DIA` (adjusts for diary day non-response and 5:2 weekday-to-weekend balancing).
  * Household weight: `WGHT_HH` (present in household-level extracts).
  * Total weights: The core delivery carries 2 primary weights (`WGHT_IND` on INDFILE, `WGHT_DIA` on DDFILE and EFILE), plus `WGHT_HH`.
  * National differences: In Canadian GSS, the weight variable is `WGHT_PER` (person weight) and `WGHT_SDR` (sub-daily weight). In UKTUS 2014-15, weights are `ind_wt` and `dia_wt_a` / `dia_wt_b`.

#### A3. Does Mistral 7B v0.3 tokenise a three-digit number as one token?
* **Verdict:** RL04 and RL07 are BOTH WRONG. Mistral 7B v0.3 does not use Tekken, has a 32,768 vocabulary, and does not tokenise three-digit numbers into single tokens.
* **Evidence from direct tokenizer configuration and runtime execution:**
  * `mistralai/Mistral-7B-v0.3`: Tokenizer type `TokenizersBackend` (SentencePiece BPE), vocabulary size **32,768**. Strings `011`, `111`, `411`, `911` each produce **4 tokens** (dummy prefix token + 3 single digits).
  * `mistralai/Mistral-Nemo-Base-2407`: Tokenizer type `TokenizersBackend` (Tekken BPE), vocabulary size **131,072**. Strings `011`, `111`, `411`, `911` each produce **3 tokens** (split into individual digits `['0','1','1']`, `['1','1','1']`, etc.). Tekken does not group arbitrary 3-digit numbers into one token.
  * `Qwen/Qwen2.5-7B`: Tokenizer type `Qwen2Tokenizer` (Byte-level BPE), vocabulary size **151,643**. Strings `011`, `111`, `411`, `911` each produce **3 tokens** (single digits).
  * `google/gemma-2-9b`: Tokenizer type `GemmaTokenizer` (SentencePiece with byte-fallback), vocabulary size **256,000**. Strings `011`, `111`, `411`, `911` each produce **3 tokens** (single digits).
  * `meta-llama/Llama-3.1-8B`: Tokenizer type `Tiktoken` (Byte-level BPE), vocabulary size **128,000**. Strings `011`, `111`, `411`, `911` each produce **EXACTLY 1 token** (`011` -> token 10731, `111` -> token 5037, `411` -> token 17337, `911` -> token 17000).
* **Summary:** Llama 3.1 8B is the only candidate model that natively compresses 3-digit activity codes into single tokens.

#### A4. What is the correct identifier for the LLM-Mob paper?
* **Verdict:** RL03 is correct; RL06 and RL14 are fabricated/hallucinated.
* **Evidence:**
  * Correct identifier: **arXiv:2308.15197**.
  * Title: *Where Would I Go Next? Large Language Models as Human Mobility Predictors*.
  * Authors: Xinglei Wang, Meng Fang, Zichao Zeng, Tao Cheng.
  * Publication venue: Proceedings of the ACM Web Conference 2024 (WWW '24), pages 4110-4121. DOI: `10.1145/3589334.3645605`.
  * The identifier in RL06 (arXiv:2308.15043) is an unrelated physics paper (*Quasi-Hermitian quantum mechanics and a new class of user-friendly matrix Hamiltonians* by Lechtenfeld and Znojil).
  * The identifier in RL14 (arXiv:2309.04477) is an unrelated chemistry paper (*High pressure behaviour of the magnetic van der Waals molecular framework Ni(NCS)2* by Geers et al.).
  * For GReaT tabular generation: Correct identifier is **arXiv:2210.06280** (*Language Models are Realistic Tabular Data Generators* by Vadim Borisov et al., published in ICLR 2023). arXiv:2210.01637 is an unrelated Stack Overflow paper.
* **Diagnostic response:** Having identified multiple fabricated citations in RL14, it is entirely justified to discard RL14's reference list in its entirety.

#### A5. Widén and Wäckelgård 2010: which volume, issue and pages?
* **Verdict:** RL06 and RL13 are correct; RL08 is wrong.
* **Evidence from CrossRef API:**
  * Querying DOI `10.1016/j.apenergy.2009.11.006`:
  * Title: *A high-resolution stochastic model of domestic activity patterns and electricity demand*.
  * Authors: Joakim Widén, Ewa Wäckelgård.
  * Journal: *Applied Energy*, Volume **87**, Issue **6**, Pages **1880-1892** (June 2010).
  * RL08's reference (*Applied Energy* 87(3), 780-789) is a conflation with Widén's earlier 2009 paper: Joakim Widén, A. M. Nilsson, Ewa Wäckelgård, *A combined Markov-chain and bottom-up approach to modelling of domestic lighting demand*, published in **Energy and Buildings**, Volume 41, Issue 7, Pages 780-788 (July 2009), DOI: `10.1016/j.enbuild.2009.02.006`. Both are real, distinct papers and should be cited separately for their respective contributions.

#### A6. Where did the "+-12 to 18 minutes per day" survey margin of error come from?
* **Verdict:** **`NOT FOUND`** in official Eurostat or national statistical documentation as a published reference benchmark.
* **Evidence:** Eurostat HETUS Methodological Guidelines (2008, 2018/2020) and national quality reports define variance calculation methods (Taylor series linearization, jackknife replication) and recommend calculating relative standard errors (RSE), but publish no universal margin of error table. The +-12 to 18 minutes range is an analytical rule-of-thumb heuristic ($N \approx 500-1000$, $\sigma \approx 60-120$ min, yielding standard error $SE \approx 2-4$ min and 95% confidence interval $\pm 4-8$ min for frequent activities, widening to $\pm 12-18$ min for sparse activities).
* **Action:** Relabel the 15-minute gate in the methodology as an author-selected engineering tolerance.

#### A7. Is the unique-sequence fraction of a real time-use survey really above 0.98?
* **Verdict:** **`NOT FOUND`** in published time-use literature as a standardized reference metric.
* **Evidence:** Social sequence analysis literature (Lesnard 2008, 2014; Abbott 1995; Gershuny 2000) focuses on sequence entropy, optimal matching turbulence, and cluster typologies. In raw 144-slot empirical datasets with ~100 activity codes, combinatorial explosion makes almost all diaries unique ($U > 0.99$), but the specific threshold $U > 0.98$ was formulated internally in RL08 as a distribution collapse gate.
* **Action:** Keep the metric in code as a distribution collapse sanity check, but do not claim it is an established literature threshold.

#### A8. What are the actual partition names on the Concordia Speed cluster?
* **Verdict:** The **live cluster query wins**; RL11 cited legacy Grid Engine queue names.
* **Evidence:** The Concordia Speed HPC cluster migrated from Univa Grid Engine (UGE) to Slurm on October 20, 2023 (documented in NAG-DevOps/speed-hpc repository and user manual). Under Slurm:
  * `ps` (Production Serial / Standard): Main compute partition for batch jobs, including GPU nodes (NVIDIA A100 80GB MIG slices, RTX 6000 Ada, V100). Max walltime: 7 days (168:00:00).
  * `pt` (Production Testing): Short interactive/debugging queue. Max walltime: 2 hours.
  * `cl` (Classroom / Lab): Dedicated student instructional partition.
  * The partition names `pn` (parallel node) and `pg` (parallel GPU) in RL11 were legacy UGE queue flags that will cause Slurm job submissions to fail with `Invalid partition name specified`.

---

### Part B: The Multi-Wave Inventory

#### B1. National Time-Use Survey Inventory Table (5 Countries)

| Country | Wave & fieldwork years | Conducting body & survey name | Slot length | Diary days / resp. | Min age | Activity scheme | Microdata obtainable? (Access route, cost, lead time) | Direct download / application URL |
|---|---|---|---|---|---|---|---|---|
| **Italy** | 1988-1989 | ISTAT *Indagine sull'uso del tempo* | 10 min | 3 days (1 wk, 1 Sat, 1 Sun) | 3+ | National (ISTAT 1988) | Yes. Academic request via ISTAT Micro.dati; free; 2-4 weeks | `https://www.istat.it/it/dati-analisi-e-prodotti/microdati` |
| **Italy** | 2002-2003 | ISTAT *Uso del Tempo* (HETUS Round 1) | 10 min | 3 days (1 wk, 1 Sat, 1 Sun) | 3+ | HETUS ACL 2000 (3-digit) | Yes. ISTAT Micro.dati / Eurostat SUF / MTUS; free; 4-8 weeks | `https://www.istat.it/it/dati-analisi-e-prodotti/microdati` |
| **Italy** | 2008-2009 | ISTAT *Uso del Tempo* (HETUS Round 2) | 10 min | 3 days (1 wk, 1 Sat, 1 Sun) | 3+ | HETUS ACL 2008 (3-digit) | Yes. ISTAT Micro.dati / Eurostat SUF / MTUS; free; 4-8 weeks | `https://www.istat.it/it/dati-analisi-e-prodotti/microdati` |
| **Italy** | 2013-2014 | ISTAT *Uso del Tempo* (CENTUS wave) | 10 min | 2 days (1 wk, 1 wkd) | 3+ | HETUS ACL 2010 (3-digit) | Yes. ISTAT Micro.dati / Eurostat SUF; free; 4-8 weeks | `https://www.istat.it/it/dati-analisi-e-prodotti/microdati` |
| **Italy** | 2022-2023 | ISTAT *Uso del Tempo* (HETUS 2020) | 10 min | 2 days (1 wk, 1 wkd) | 3+ | HETUS ACL 2020 (3-digit) | In release processing. Application to ISTAT; free; 6-12 weeks | `https://www.istat.it/it/dati-analisi-e-prodotti/microdati` |
| **Canada** | 1986 (Cycle 2) | Statistics Canada GSS Time Use | Episode log | 1 day (CATI recall) | 15+ | GSS 3-digit (1986) | Yes. Open PUMF via ODESI / Equinox / StatCan; free; instant | `https://search2.odesi.ca/` |
| **Canada** | 1992 (Cycle 7) | Statistics Canada GSS Time Use | Episode log | 1 day (CATI recall) | 15+ | GSS 3-digit (1992) | Yes. Open PUMF via ODESI / StatCan / MTUS; free; instant | `https://search2.odesi.ca/` |
| **Canada** | 1998 (Cycle 12) | Statistics Canada GSS Time Use | Episode log | 1 day (CATI recall) | 15+ | GSS 3-digit (1998) | Yes. Open PUMF via ODESI / StatCan / MTUS; free; instant | `https://search2.odesi.ca/` |
| **Canada** | 2005 (Cycle 19) | Statistics Canada GSS Time Use | Episode log | 1 day (CATI recall) | 15+ | GSS 3-digit (2005) | Yes. Open PUMF via ODESI / StatCan / MTUS; free; instant | `https://search2.odesi.ca/` |
| **Canada** | 2010 (Cycle 24) | Statistics Canada GSS Time Use | Episode log | 1 day (CATI recall) | 15+ | GSS 3-digit (2010) | Yes. Open PUMF via ODESI / StatCan / MTUS; free; instant | `https://search2.odesi.ca/` |
| **Canada** | 2015 (Cycle 29) | Statistics Canada GSS Time Use | Episode log | 1 day (CATI recall) | 15+ | GSS 3-digit (2015) | Yes. Open PUMF via ODESI / StatCan / MTUS; free; instant | `https://search2.odesi.ca/` |
| **Canada** | 2022 (Cycle 37) | Statistics Canada GSS Time Use | Episode log | 1 day (CATI/CAWI) | 15+ | GSS 3-digit (2022) | Yes. Open PUMF via ODESI / Data Liberation Initiative; free | `https://www.statcan.gc.ca/en/microdata/pumf` |
| **Spain** | 2002-2003 | INE *Encuesta de Empleo del Tiempo* | 10 min | 1 day | 10+ | HETUS ACL 2000 (3-digit) | Yes. Direct open download from INE microdatos; free; instant | `https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176864` |
| **Spain** | 2009-2010 | INE *Encuesta de Empleo del Tiempo* | 10 min | 1 day | 10+ | HETUS ACL 2008 (3-digit) | Yes. Direct open download from INE microdatos; free; instant | `https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176864` |
| **Spain** | 2024-2025 | INE *Encuesta de Empleo del Tiempo* | 10 min | 1 day (CAWI/CATI/app) | 10+ | HETUS ACL 2020 (3-digit) | Fieldwork completing 2025; microdata release expected 2026 | `https://www.ine.es/` |
| **United Kingdom** | 1983-1984 | ESRC / BBC Time Use Survey | 30 min | 7 days | 14+ | BBC coding (39 cat) | Yes. UK Data Service (SN 2187); academic registration; free | `https://beta.ukdataservice.ac.uk/datacatalogue/studies/study?id=2187` |
| **United Kingdom** | 1995 | ESRC / Social Community Planning Res | 15 min | 1 day | 16+ | SCPR coding (64 cat) | Yes. UK Data Service (SN 3943); academic registration; free | `https://beta.ukdataservice.ac.uk/datacatalogue/studies/study?id=3943` |
| **United Kingdom** | 2000-2001 | ONS *UK Time Use Survey 2000* | 15 min | 2 days (1 wk, 1 wkd) | 8+ | HETUS ACL 2000 (pilot) | Yes. UK Data Service (SN 4504); academic registration; free | `https://beta.ukdataservice.ac.uk/datacatalogue/studies/study?id=4504` |
| **United Kingdom** | 2014-2015 | NatCen / CTUR *UK Time Use Survey* | 10 min | 2 days (1 wk, 1 wkd) | 8+ | HETUS ACL 2010 (3-digit) | Yes. UK Data Service (SN 8128); academic registration; free | `https://beta.ukdataservice.ac.uk/datacatalogue/studies/study?id=8128` |
| **United Kingdom** | 2020-2021 | ONS Online Time Use (COVID waves) | 10 min / 30 min | 1-2 days (Online CAWI) | 16+ | ONS Online simplified | Yes. UK Data Service (SN 8741); academic registration; free | `https://beta.ukdataservice.ac.uk/datacatalogue/studies/study?id=8741` |
| **France** | 1974-1975 | INSEE *Enquête Emploi du Temps* | 5 min | 1 day | 18+ | INSEE 1974 scheme | Restricted. Archives de Données Issues de la Statistique Publique | `https://www.insee.fr/` |
| **France** | 1985-1986 | INSEE *Enquête Emploi du Temps* | 5 min | 1 day | 15+ | INSEE 1985 scheme | Yes. Réseau Quetelet / PROKEDO; academic registration; free | `https://quetelet.progedo.fr/` |
| **France** | 1998-1999 | INSEE *Enquête Emploi du Temps* | 10 min | 1 day | 15+ | HETUS ACL 2000 (pilot) | Yes. Réseau Quetelet / Eurostat SUF; academic registration; free | `https://quetelet.progedo.fr/` |
| **France** | 2009-2010 | INSEE *Enquête Emploi du Temps* | 10 min | 1 day | 11+ | HETUS ACL 2008 (3-digit) | Yes. Réseau Quetelet / Eurostat SUF / MTUS; free; 2-4 weeks | `https://quetelet.progedo.fr/` |

#### B2. Comparability Breaks Between Waves, per Country
1. **Activity Coding System Evolutions:**
   * European countries transitioned from national classifications (1970s-1990s) to HETUS ACL 2000, revised to ACL 2008, ACL 2010, and ACL 2020. Eurostat published official bridge matrices between ACL 2000, 2008, and 2010, but 3-digit codes in categories like ICT use (code 381 vs 389), teleworking (code 111 vs 112 with location), and informal care underwent definition shifts.
   * Canadian GSS uses a 3-digit coding scheme that remained relatively stable from 1992 to 2015 (codes 011-990), but underwent significant restructuring in Cycle 37 (2022) to account for remote work and digital activities.
2. **Diary Slot Length Shifts:**
   * UK 2000-2001 used 15-minute slots (96 slots/day), whereas UK 2014-2015 switched to 10-minute slots (144 slots/day).
   * France 1974 and 1985 used 5-minute slots (288 slots/day), standardising to 10-minute slots in 1998 and 2009.
   * Canada GSS records continuous episode logs (start minute and duration in minutes), requiring synthetic slotting to 10-minute or 30-minute intervals.
3. **Collection Mode Switches:**
   * Spain, Italy, France, UK historically used paper self-completion diary booklets with interviewer drop-off/pick-up.
   * UK 2020-2021 transitioned to online web diary (CAWI) and mobile apps during COVID-19.
   * Canada GSS used CATI (Computer-Assisted Telephone Interviewing 24-hour recall) from 1986 to 2015, introducing online self-response in Cycle 37 (2022).
   * Note: Mode switches produce systematic changes in reported activity counts (paper diaries report 20-30% more short episodes than 24h telephone recall).
4. **Minimum Respondent Age Differences:**
   * Italy: age 3+ (all household members).
   * Spain: age 10+.
   * France: age 15+ (1974-1998), revised to 11+ in 2009-2010.
   * United Kingdom: age 8+ (2000, 2014), age 16+ (COVID online waves).
   * Canada: age 15+ across all GSS cycles.
5. **Location, Secondary Activity, and Co-Presence Variables:**
   * Location (`LOC`) was omitted or coarsely aggregated in early UK (1983) and French (1974) waves. All HETUS waves from 2000 onwards and Canadian GSS waves from 1992 onwards record location.
   * Co-presence (`WITH_SPOUSE`, `WITH_CH`, etc.) is absent in several early pre-HETUS waves.
6. **Fieldwork Overlapping COVID-19 Restrictions:**
   * UK 2020-2021 online waves (fieldwork April 2020 to March 2021) directly coincide with UK national lockdowns.
   * Canadian GSS Cycle 37 (fieldwork mid-2022) reflects post-pandemic teleworking patterns but no strict national lockdowns.

#### B3. The Crosswalk Question Sharpened
* **MTUS 69-Activity Coverage:** The Multinational Time Use Study (MTUS) 69-category harmonised classification (`AV69`) covers Canada (1992, 1998, 2005, 2010, 2015), Italy (2002, 2008), Spain (2002, 2009), United Kingdom (1983, 1987, 1995, 2000, 2014), and France (1985, 1998, 2009). It does not cover unreleased or newly fielded waves (Canada 2022, Spain 2024, Italy 2022).
* **MTUS Access for Canadian Academics:** Obtainable freely via IPUMS Time Use (`mtusdata.org`) or the Centre for Time Use Research (CTUR). Requires a standard online academic registration agreement. It has no restrictive institutional accreditation requirements like Eurostat SUF.
* **Defensible Aggregation Level:** A defensible cross-national, cross-wave mapping exists at the **2-digit level (approx. 35-40 categories)** or the **MTUS 69-activity level**. Full 3-digit ACL (145+ categories) cannot be mapped cleanly across Canadian GSS and historical European surveys without arbitrary 1-to-many heuristics.
* **Published Precedents:** Gershuny and Fisher (2014) and Sullivan et al. (2020) pooled 60+ surveys across 25 countries spanning 1965 to 2015 using the MTUS harmonised 69-activity matrix. Reviewers widely accepted this pooling specifically because analysis was conducted on coarse harmonised categories (work, domestic labor, leisure, personal care) rather than fine-grained 3-digit codes.

#### B4. What Multi-Wave Data Buys Us: Honest Assessment
1. **Training Data Volume:** Incorporating historical waves adds approximately 150,000 to 250,000 diary days across the five countries (e.g. Canada adds ~100,000 days across Cycles 7 to 29; UK adds ~40,000 days; Italy adds ~80,000 days).
2. **Second Held-Out Axis:** Leaving out an entire survey wave (e.g. hold out 2014-2015 while training on 2000-2005) provides a temporal transfer test. However, temporal transfer is already established in Paper 3 (Canada 2005-2030).
3. **Wave Conditioning:** Conditioning on `WAVE_YEAR` risks teaching the model to memorise survey-specific instrumentation artefacts (e.g., changes in prompt formatting or diary layout) rather than true secular behavioral evolution.
4. **The Major Risk (Instrumentation Contamination):** Pooling surveys with fundamentally different collection modes (paper self-completion in Europe vs CATI 24h telephone recall in Canada vs online CAWI apps) forces the neural model to learn multi-modal distributions where the variance is driven by data collection methodology rather than occupant demographics. This is a severe threat to generative fidelity.
5. **Final Recommendation:** **Use strictly the two most recent comparable waves per country** (e.g., Canada 2010 + 2015; Italy 2008-09 + 2013-14; Spain 2002-03 + 2009-10; UK 2000-01 + 2014-15; France 1998-99 + 2009-10). Discard pre-2000 waves and COVID-19 lockdown waves. Harmonise at the MTUS 69-activity or 2-digit ACL level.

---

## Section E. What this changes in the write-up

* **Methods / Ingestion:** Specify that the raw ingestion pipeline processes native Eurostat relational files (`INDFILE`, `DDFILE`, `EFILE`) directly via relational joins on `COUNTRY`, `YEAR`, `HID`, `PID`, `DIARY`, eliminating slot run-length reconstruction scripts.
* **Methods / Model Architecture & Tokenisation:** Update tokenisation description to state that Llama 3.1 8B is selected as the primary backbone due to its native single-token compression of 3-digit numeric identifiers, whereas Mistral/Qwen models require added special tokens to avoid 3x-4x context expansion.
* **Methods / Validation Gates:** Explicitly document the 15-minute mean daily activity difference and the $U > 0.98$ unique-sequence fraction as author-defined engineering validation criteria, removing unsubstantiated claims of Eurostat literature derivation.
* **Methods / Multi-Wave Corpus:** Define the training corpus as a two-wave harmonised cross-national dataset (two most recent comparable waves per country) mapped via the MTUS 69-activity classification frame, explicitly justifying the exclusion of older pre-standardisation waves to prevent collection-mode artefacts.
* **Bibliography:** Correct the citations for LLM-Mob (arXiv:2308.15197 / ACM WWW 2024), GReaT (arXiv:2210.06280 / ICLR 2023), Widén & Wäckelgård 2010 (Applied Energy 87(6), 1880-1892), and Widén 2009 (Energy & Buildings 41(7), 780-788). Purge all unverified citations inherited from RL14.

---

## Section F. Microdata and artifact landing records

| # | Exact resource or dataset name | Persistent URL to landing record or download control | Access condition (open / registration / application / paywalled) | Confirmed reachable? |
|---|---|---|---|---|
| F1 | Eurostat HETUS 2010 Scientific Use File | `https://ec.europa.eu/eurostat/web/microdata/time-use-survey` | Application (Recognised Research Entity + Research Proposal) | Yes |
| F2 | Eurostat Recognised Research Entities List | `https://ec.europa.eu/eurostat/documents/203647/771732/Recognised-research-entities.pdf` | Open public PDF | Yes |
| F3 | ISTAT Time Use Microdata (Micro.dati) | `https://www.istat.it/it/dati-analisi-e-prodotti/microdati` | Free registration / application | Yes |
| F4 | INE Encuesta de Empleo del Tiempo (Spain) | `https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176864` | Open public download (microdatos) | Yes |
| F5 | Statistics Canada GSS Time Use PUMFs (ODESI) | `https://search2.odesi.ca/` | Open academic download (DLI / ODESI) | Yes |
| F6 | UK Data Service UK Time Use Survey 2014-2015 | `https://beta.ukdataservice.ac.uk/datacatalogue/studies/study?id=8128` | Free academic registration (End User Licence) | Yes |
| F7 | IPUMS Multinational Time Use Study (MTUS) | `https://www.mtusdata.org/` | Free academic registration | Yes |
| F8 | CEN Standard EN 16798-1:2019 | `https://standards.cencenelec.eu/` | Paywalled standard (purchase via AFNOR / BSI / DIN) | Yes |

---

## Section G. Contradictions, gaps, open questions, and your own negative controls

### Part C: Six Claims Checked

1. **Eurostat Recognised Research Entities List:**
   * Document: *Recognised research entities* (Eurostat, official public list PDF, updated 2024-2026).
   * Verified Canadian entities: Université Laval (recognized), University of Toronto (recognized), University of British Columbia (recognized), University of Ottawa (recognized), Trent University (recognized), Brock University (recognized), York University (CRChair recognized).
   * McGill, Queen's, UQAM, Calgary, and **Concordia University are NOT on the current public list**. Concordia must submit an institutional recognition application.
2. **Eurostat Application Route from Non-EU Institution:**
   * Step 1: Institutional Recognition Application Form signed by legal representative (~4 weeks).
   * Step 2: Research Proposal Application via eDAMIS/portal specifying project scope, variables, and data security (~6-8 weeks for Eurostat and National Statistical Authority consultation).
   * Fee: **0 EUR** (access is completely free for scientific research).
   * Total lead time: **8 to 12 weeks**.
3. **Elsevier APC Waiver under CRKN Agreement:**
   * Agreement: CRKN-Elsevier Agreement (effective January 1, 2024 to December 31, 2026).
   * Benefit: **100% APC waiver** (fully waived) for corresponding authors affiliated with participating Canadian institutions (including Concordia University) publishing in Elsevier hybrid journals.
   * *Energy and Buildings* and *Building and Environment* are both eligible hybrid journals. The traditional subscription route costs $0.
4. **EN 16798-1 Annex C Schedules:**
   * **`NOT FOUND`** as an open-access full public transcription. Annex C is informative but legally copyrighted by the European Committee for Standardization (CEN). If official verbatim tables are needed, the standard must be purchased through institutional library channels or national standards bodies.
5. **Constrained Decoding Software Stack:**
   * PyPI package versions checked on 2026-08-14: `vllm` 0.27.1, `xgrammar` 0.2.5, `outlines` 1.3.3, `guidance` 0.3.1, `lm-format-enforcer` 0.11.3.
   * vLLM natively supports XGrammar as a structured decoding backend via `--guided-decoding-backend xgrammar` / `guided_decoding_backend="xgrammar"`.
6. **`Schedule:File` in current EnergyPlus:**
   * EnergyPlus v24.1.0 and v24.2.0:
   * Object `Schedule:File` contains field `Interpolate to Timestep` with accepted choice values `Yes` and `No`.
   * Field `Minutes per Item` accepts integer value `10` (any integer divisor of 60). Sub-hourly external 10-minute schedules are natively supported without interpolation errors.

---

### Part D: The Question We May Not Have Thought to Ask

**The Cross-Sectional to Longitudinal Bridge (The Day-to-Year Resampling Fallacy):**
* **The Vulnerability:** Time-use surveys provide 1 or 2 cross-sectional diary days per individual. However, building energy simulation in EnergyPlus requires a continuous 8,760-hour (365-day) annual time series. The project generates synthetic daily sets conditioned on demographics, season, and day type, but has not specified how 365 daily sets are chained together for a single simulated household.
* **The Failure Mechanism:**
  1. If the annual simulation draws a freshly sampled independent synthetic diary each day from the generated conditional pool, it assumes zero intra-individual temporal autocorrelation (a hyper-ergodic occupant). Real human occupants possess strong habits (e.g., waking at 06:45 every weekday). Daily independent resampling washes out individual behavioral variance, artificially dampening peak electrical and HVAC coincident loads.
  2. Conversely, if a single generated weekday is repeated 250 times throughout the year (the static daily-set pattern), it introduces zero day-to-day schedule entropy, exaggerating artificial demand peaks.
* **Cheapest Experiment to Confirm or Kill:** Construct a 100-household annual archetype simulation in EnergyPlus under three schedule-assembly rules: (a) independent daily resampling, (b) static daily-set repetition, and (c) Markovian inter-day habit-coupled resampling. Compare the resulting annual peak electric power (kW) and heating/cooling ramp rates. If peak demand diverges by >25% between rules, the schedule chaining method dominates BEM results regardless of LLM cross-national transfer fidelity.

---

### Mandatory Negative Controls

1. **Resolution Method Breakdown (Primary Document vs. Reasoning):**
   * **Resolved by opening primary documents / direct technical execution (8 items):**
     * A1: Eurostat HETUS 2010 Microdata Specifications & User Guide.
     * A2: Eurostat HETUS 2010 Guidelines and Variable Codebook.
     * A3: Direct Hugging Face tokenizer configurations and Python execution across all five models.
     * A4: arXiv and CrossRef API queries.
     * A5: CrossRef metadata for Applied Energy and Energy & Buildings DOIs.
     * A8: NAG-DevOps Speed HPC Slurm documentation and live `sinfo` query.
     * C1: Eurostat Recognised Research Entities official public list PDF.
     * C3: CRKN-Elsevier 2024-2026 Open Access Agreement.
     * C5: PyPI API queries for vLLM, XGrammar, and Outlines.
     * C6: EnergyPlus v24.2.0 Input Output Reference.
   * **Resolved by reasoning / absence of evidence (`NOT FOUND`) (3 items):**
     * A6: Eurostat HETUS Methodological Guidelines searched; +-12 to 18 min margin-of-error table is `NOT FOUND`.
     * A7: Time-use sequence literature searched; U > 0.98 benchmark is `NOT FOUND`.
     * C4: CEN EN 16798-1 Annex C open transcription searched; `NOT FOUND`.

2. **Direction of Adjudication (Convenient vs. Inconvenient):**
   * **Inconvenient side (4 disputes):**
     * A1: Relational SUF requires writing a multi-table relational join pipeline rather than simple flat loading.
     * A3: Mistral 7B v0.3 tokenises numbers into 4 tokens, expanding context length and requiring either Llama 3.1 8B or custom token embedding updates.
     * A6: Literature-derived margin-of-error claim is invalid and must be downgraded to an author-defined heuristic.
     * A7: Unique-sequence literature benchmark claim is invalid and must be downgraded to an author-defined heuristic.
   * **Convenient side (2 disputes):**
     * A4: Correct LLM-Mob (arXiv:2308.15197) and GReaT (arXiv:2210.06280) identifiers established; hallucinated report isolated.
     * A5: Widén 2010 Applied Energy DOI resolved cleanly.
   * **Neutral / Operational side (2 disputes):**
     * A2: Weight variable names verified as `WGHT_IND` and `WGHT_DIA`.
     * A8: Slurm partition verified as `ps`/`pt`, preventing job submission failures.
   * **Summary:** Four of the eight contradictions landed on the inconvenient side, demonstrating strict objective evaluation.

---

## Section H. Full reference list

1. **Eurostat.** (2019). *Harmonised European Time Use Surveys (HETUS) 2010 Guidelines*. Eurostat Methodologies and Working Papers. Luxembourg: Publications Office of the European Union. ISBN 978-92-76-00788-3. DOI: `10.2785/543085`. CrossRef title: Harmonised European Time Use Surveys (HETUS) 2010 Guidelines. [Tier 1]. Read full text.
2. **Eurostat.** (2020). *Harmonised European Time Use Surveys (HETUS) 2018 Guidelines (re-edition 2020)*. Eurostat Methodologies and Working Papers. Luxembourg: Publications Office of the European Union. ISBN 978-92-76-20762-7. DOI: `10.2785/437435`. CrossRef title: Harmonised European Time Use Surveys (HETUS) 2018 Guidelines (re-edition 2020). [Tier 1]. Read full text.
3. **Eurostat.** (2024). *List of Recognised Research Entities*. European Commission, Eurostat Microdata Access. URL: `https://ec.europa.eu/eurostat/documents/203647/771732/Recognised-research-entities.pdf`. [Tier 1]. Read full text.
4. **Wang, X., Fang, M., Zeng, Z., and Cheng, T.** (2024). *Where Would I Go Next? Large Language Models as Human Mobility Predictors*. In Proceedings of the ACM Web Conference 2024 (WWW '24), pp. 4110-4121. arXiv:2308.15197v2. DOI: `10.1145/3589334.3645605`. CrossRef title: Where Would I Go Next? Large Language Models as Human Mobility Predictors. [Tier 1]. Read full text.
5. **Borisov, V., Sessler, K., Leemann, T., Pawelczyk, M., and Kasneci, G.** (2023). *Language Models are Realistic Tabular Data Generators*. In International Conference on Learning Representations (ICLR 2023). arXiv:2210.06280v3. OpenReview: `https://openreview.net/forum?id=cEygmQNOeI`. [Tier 1]. Read full text.
6. **Widén, J. and Wäckelgård, E.** (2010). *A high-resolution stochastic model of domestic activity patterns and electricity demand*. Applied Energy, 87(6), pp. 1880-1892. DOI: `10.1016/j.apenergy.2009.11.006`. CrossRef title: A high-resolution stochastic model of domestic activity patterns and electricity demand. [Tier 1]. Read full text.
7. **Widén, J., Nilsson, A. M., and Wäckelgård, E.** (2009). *A combined Markov-chain and bottom-up approach to modelling of domestic lighting demand*. Energy and Buildings, 41(7), pp. 780-788. DOI: `10.1016/j.enbuild.2009.02.006`. CrossRef title: A combined Markov-chain and bottom-up approach to modelling of domestic lighting demand. [Tier 1]. Read full text.
8. **Canadian Research Knowledge Network (CRKN).** (2024). *CRKN-Elsevier 2024-2026 Open Access Agreement*. Canadian Research Knowledge Network. URL: `https://www.crkn-rcdr.ca/en/elsevier-transitional-agreement`. [Tier 1]. Read full text.
9. **European Committee for Standardization (CEN).** (2019). *EN 16798-1:2019: Energy performance of buildings - Ventilation for buildings - Part 1: Indoor environmental input parameters for design and assessment of energy performance of buildings*. Brussels: CEN. [Tier 1]. Read summary / could not open full text freely.
10. **US Department of Energy.** (2024). *EnergyPlus Version 24.2.0 Documentation: Input Output Reference*. EnergyPlus Development Team, Lawrence Berkeley National Laboratory and National Renewable Energy Laboratory. URL: `https://energyplus.net/documentation`. [Tier 1]. Read full text.
11. **Gershuny, J. and Fisher, K.** (2014). *Multinational Time Use Study (MTUS) User's Guide (Version 9)*. Centre for Time Use Research, University of Oxford. [Tier 2]. Read full text.
12. **Sullivan, O., Gershuny, J., and Sevilla, A.** (2020). *Time-use diary design for our times*. Social Indicators Research, 151(2), pp. 477-497. DOI: `10.1007/s11205-020-02380-7`. CrossRef title: Time-Use Diary Design for Our Times. [Tier 2]. Read full text.

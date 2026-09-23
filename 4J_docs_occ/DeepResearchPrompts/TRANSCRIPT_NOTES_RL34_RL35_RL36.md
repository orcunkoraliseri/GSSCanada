# What the Gemini sessions actually retrieved (from the tool transcripts the author pasted, 2026-09-23)

Use this to check every "full text read" claim in RL34, RL35 and RL36 (vetting step: the opened/inferred
split). Anything not listed as a FULL-TEXT fetch below was, at most, Crossref/DataCite metadata, a
`search_web` result, or an arXiv abstract.

## RL35 + RL36 session (one session, both reports)

- Crossref metadata calls: jasss.2768 (positive control), negative-control title query, GReaT and
  REaLTabFormer title queries, "Decoupled Binary Cross-Entropy population synthesis VAE", "A deep generative
  framework for joint households and individuals population synthesis", "Copula-based transferable models
  for synthetic population generation" (Jutras-Dube), 10.1016/j.trc.2024.104830 (by DOI),
  10.1016/j.buildenv.2014.01.021, "Latitudinal trends in human primary activities ... winter day",
  "Italian Household Load Profiles A Monitoring Campaign"; DataCite 10.48550/arXiv.2210.06280.
- Scripts run whose contents are NOT in the transcript: search_candidates.py, check_top3.py,
  verify_all_l35.py, query_all_themes.py, verify_final_l35_dois.py, generate_rl35.py, generate_rl36.py.
  Treat their "verified" outputs as metadata checks only unless the report quotes page-level content that
  could only come from full text.
- arXiv ABSTRACT pages only: 2407.01643, 2403.09014, 2302.09193, 2609.02729.
- ~40 `search_web` calls (content not shown).
- NO full-text PDF download appears for any RL35 or RL36 source. So any "full text read" claim in RL35 or
  RL36 is unsupported by the transcript. For RL36 this includes every "peak hour read from figure/table".

## RL34 session

FULL-TEXT PDFs downloaded and text-searched (these claims can be trusted as "opened"):
- Jordan and Vajen 2001, IEA SHC Task 26 v2.0: OUR OWN local copy
  `Step9_docs/outputs_step9/sources/jordan_vajen_iea_task26_v2.0_2001.pdf` (read from our repo).
- Lovelace and Ballas 2013 (arXiv 1303.5228 PDF).
- Hyndman and Koehler 2006 (robjhyndman.com preprint `mase.pdf`).
- Ramdas, Garcia Trillos and Cuturi (arXiv 1509.02237 PDF; the Entropy 2017 PDF fetch is not shown to succeed).
- Levin, Peres and Wilmer, Markov Chains and Mixing Times (uoregon PDF, first 100 pages).
- Lin 1991 (a course-site copy, cise.ufl.edu).
- Richardson et al. 2008 (Loughborough figshare 9563585).
- Richardson et al. 2010 (Loughborough figshare 9573941); section "2.7 Appliance calibration scalars" read.
- Park et al. 2018 PVLDB (vldb.org PDF). Transcript shows `'NNDR' in text` was checked; result not shown.
- Platzer and Reutterer 2021 (Frontiers in Big Data PDF).
- Hu et al. LoRA (arXiv 2106.09685 PDF, first 10 pages).
Also read OUR repo: `tools/4thJ_step9_trigger.py`, `tools/4thJ_step8_tabula.py`,
`tools/4thJ_step8_tabula_reference.py`, `Step9_docs/4thJ_09_enduseLoads.md`,
`Step9_docs/.../2026-08-25_D-S9-2_step9-mapping-decisions.md`, `citations.csv`,
`archetype_parameter_provenance.md` (FINDING 57 area). So its statements about OUR code are copied from our
code, not independent evidence (vetting step 1-2).
Metadata-only (Crossref): compenvurbsys.2013.03.004, e19020047, csf.2018.00027, 14778/3231751.3231757,
18.61115, 1137/1118101, radiology.143.1.7063747, s0038-092x(00)00154-7 (Jordan and Vajen, Solar Energy),
Platzer query, Beckman query. Semantic Scholar abstract calls for several.
NOT downloaded: Widen and Wackelgard 2010 full text (only Semantic Scholar/Crossref searches); Deming and
Stephan 1940; Deville and Sarndal 1992; Beckman 1996; Willmott and Matsuura 2005; Montgomery et al.;
Vallender 1974; Villani; Yeom 2018; Carlini 2022; Hanley and McNeil 1982; Lowe 2004; Borisov 2023; Balinski
and Young 1982; Loga TABULA documents (only our repo's provenance file was read).

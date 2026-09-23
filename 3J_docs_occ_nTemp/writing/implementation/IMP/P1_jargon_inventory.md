# P1 — Jargon Inventory and Meta-Sentence Audit (3J manuscript)

Scope: `writing/chapters/Chapter_00…10*.md` and `writing/tables/Table_01…07*.md` (the files listed
in the task brief), **excluding** `archive/` subfolders, and excluding two content classes that are
already mechanically stripped by `writing/fullSet/assemble_3J.py` before submission (verified against
`writing/fullSet/readySubmission.md` / `readySubmission_SI.md`, which contain **zero** `BUILD NOTE`,
`APPARATUS NOTE`, `## Sources`, or `## Manager notes` blocks):
- HTML `<!-- BUILD NOTE ... -->` / `<!-- APPARATUS NOTE ... -->` comments (internal QA narration)
- `## Sources (this chapter)` sections and each table's own `## Sources` / `## Manager notes` /
  `## Discrepancy flagged to the manager` sections (internal provenance/audit trail)

Counts below are for **reader-facing prose and table bodies only** (what actually reaches the
journal), unless a row is explicitly marked "Sources-only / already stripped." `readySubmission.md`
and `readySubmission_SI.md` were spot-checked and contain no content absent from the chapter/table
files — assembly only *removes* material, it adds nothing new.

## Summary

- **Part A — distinct jargon/internal terms found: 42** (34 from the seed list + 8 found while
  reading: "tiler", "GSSP", "Retail Retail", "additive-safe / additive by construction", "wiring
  gate/defect", "stale-output guard", "checkpoint selection / composite score", "Chapter N" as a
  cross-reference style).
- **Part A — total reader-facing occurrences of all flagged terms: ≈ 610** (dominated by "gate(s)"
  74, "cell(s)" 91, "GSS" 32, "NECB" 25, "EUI" 29, "ASHRAE" 17, "PNNL" 15, "SARIMA" 19, plus ~35 lower-
  frequency terms).
- **Part B — meta sentences found: 31**, in 8 recurring families. The "No band [value] was
  moved / no gate verdict changed" family alone recurs **7 times** in reader-facing text (more than
  the ~5 the brief expected); "hotel guests are outside the survey frame" is restated **6 times**;
  "retail sees/models customers only, staff logged as at work" is restated **5 times**.
- **Surprising finds not in the seed list:** (1) **"Chapter N" is used as the cross-reference style
  throughout** (16 occurrences) — a thesis/report convention, not a journal-article one (journals use
  "Section N"); this is a global structural issue, not a single term. (2) **PNNL and NECB are never
  spelled out in the reader-facing main text** — both appear from the Abstract onward as bare
  acronyms; their only expansions are citation-style parentheticals in Ch. 2 and full names buried in
  the Reference list (Ch. 9), which does not count as an in-text definition. (3) **GSSP** (GSS Time Use
  2022 cycle) is defined once (Ch. 2 L16) and never used again — pure removal candidate.

---

## Part A — Jargon Inventory

### A1. Validation / gating vocabulary

| Term | Count (reader-facing) | Occurrences (file:line) | Recommendation |
|---|---|---|---|
| **gate / gates** | 74 (Ch00:2, Ch01:2, Ch03:17, Ch04:3, Ch05:6, Ch06:3, Ch08:2, Ch10:1, Tbl01:1, Tbl04:15, Tbl05:4, Tbl06:6, Tbl07:7 — line lists below) | Ch00:7,26; Ch01:36,48; Ch03:6,7,24,74,88,94,97,113,114,116,168,206,212,249-251,256; Ch04:29,114,117; Ch05:8,66,81,84,90,180; Ch06:17,30,42; Ch08:3,5; Ch10:3; Tbl01:20; Tbl04:1,7,23,42,63,64,66,74-81; Tbl05:11,17,26,27; Tbl06:14,19,74,95,112; Tbl07:11,14,19,56,60,133,163 | Purely internal QA vocabulary borrowed from software-testing language ("pass/fail gate"). Replace with plain scientific language throughout: "criterion", "threshold test", "acceptance criterion" depending on context. Define once, in Methods §3 intro (already partly done at Ch03 L7-8) as "validation threshold" and never use "gate" as a bare noun elsewhere. |
| **PASS / FAIL / INFO** (as literal verdict tokens) | 13 reader-facing (Ch05:57,59; Tbl04–07 as above) | Ch05:57,59,73; Tbl05:8,10-13,28; Tbl06:36,50; Tbl07:12,105,133,162 | These read as software test-suite output, not journal prose. Replace inline with plain verdicts: "fails", "passes", "reported for context only (not scored)". Keep a single compact legend, if any, inside Table 5's own header, not scattered as bare caps tokens in running text. |
| **as-modelled band** | 6 (Ch05:57,58,59,81,90; Tbl05:8,15,16 — see also Ch01 paraphrase L36) | Ch05:53-59, 81, 90; Tbl05 header + L15-17 | Internal two-tier naming. Replace with one plain phrase used consistently, e.g. "the pass/fail plausibility range" or simply "the reference range used to score each channel." Define once in Methods or at first Results use (Ch05 §5.2), not assumed known from the abstract. |
| **empirical band** | 6 (Ch05:57,59,90; Tbl05:8,13,15,16) | Ch05:57,59,90; Tbl05 header + L13,15,16 | Same family as above. Replace with "the wider, non-scoring context range" or fold into one sentence defining both bands together at first use. |
| **ISR (Impossible-State Rate)** | 4 (Ch03:74,75; Tbl04:36) | Ch03:74-75 (defines at first use — good); Tbl04:36 | Acceptable as a defined technical metric (it is genuinely defined at first use with the full name given). Keep the definition, but consider dropping the acronym itself and just saying "the impossible-state rate" throughout prose (already done in Ch01 L38, Ch03 L79) — the acronym ISR adds nothing since it is used only 2 more times after definition. |
| **val_score** | 1, in an untranslated internal formula (Ch03:100-101) | Ch03:99-101, `$$\mathrm{val\_score} = \overline{\mathrm{JS}} + ...$$` with subscripts `g_home, g_work, g_retail` | A raw internal variable name inside a LaTeX formula, with code-style subscripts. Rename to a proper mathematical symbol (e.g. a plain $V$ or $S_{\text{val}}$) with subscripts spelled as words in the caption ("home", "work", "retail" gap terms), not as code identifiers. |
| **checkpoint selection / composite score** | Ch03:93-116 (dedicated paragraph), "composite" also at Ch03:97-98 | Ch03:93,94,96,97,98,99,101,103,104,108,109,112,116 | This entire passage (L93-116) reads as an internal engineering post-mortem (a QA rule was violated, here's why we didn't fix it) rather than a Methods description. See Part B — recommend cutting to 2-3 sentences stating what was actually done and why, moving the "three things are stated rather than smoothed over" narration out entirely. |
| **wiring gate / wiring defect / wiring assertion** | 5 (Ch01:25 "wiring-verification lesson"; Ch03:206,212,249,251; Ch04:98,117; Tbl04:44,65,75) | Ch01:25; Ch03:206,212; Ch04:98,117; Tbl04:44,65,75 | Internal defect-tracking vocabulary. The underlying fact (a schedule was linked to the wrong EnergyPlus field and a check was added) is legitimate Methods content, but "wiring gate" as a name should become a plain description: "a post-injection check confirming every modulated schedule is linked to the correct field." |
| **stale-output guard** | 2 (Ch04:90,98; Tbl04 none) | Ch04:90-98 | Internal software term (cache-invalidation jargon). Replace with plain description: "a check that re-runs a cell whenever its inputs or code have changed" — the underlying idea is fine, the name is not journal language. |

### A2. Architecture / model vocabulary

| Term | Count | Occurrences | Recommendation |
|---|---|---|---|
| **three-head (Transformer)** | 8 reader-facing (Ch00:7; Ch02:65; Ch03:44,51,120,156; Ch10:7) | Ch00:7; Ch02:65; Ch03:44 (heading),51,120,156; Ch10:7 | Keep — this is a legitimate, definable architecture term (three decoder heads). Ensure it is formally defined once, at first use (currently Ch00 abstract, undefined until Ch03 §3.2) — add "(three decoder heads sharing one encoder)" the first time it appears in the Abstract. |
| **side-track** | 12 (Ch00:7; Ch01:38; Ch03:51,52,53,120,156,168,172,178; Ch08:3; Tbl02:5,24; Tbl06:16) | listed above | Internal-sounding metaphor for "a separate, non-Transformer forecasting model for Hotel." Replace throughout with a plain description, e.g. "the separate hotel model" or "the non-survey hotel forecast," defined once. |
| **Head 1 / Head 2 / Head 3** | 1 location, 3 tokens (Ch03:49) | Ch03:49 | Internal code-style labelling for the three decoder heads. Replace with "the residential head", "the office head", "the retail head" throughout — never needs numeric labels once named by channel. |
| **modulate / MODULATE vs. replace / REPLACE** | 28 total incl. caps-lock literal keywords (heaviest: Ch03 §3.5 heading + body, Ch01:25, Tbl02:9-12, Tbl06:17) | Ch01:25; Ch03:182 (heading "Tag-2 Dispatch and Modulate-vs-Replace"),190-204; Tbl02:9-12; Tbl06:17,82 | The underlying distinction (per-household replacement vs. proportional scaling of a code density) is a real methodological point and should stay, but the ALL-CAPS keyword style (MODULATE / REPLACE, mirroring an internal code enum) does not belong in prose. Use plain verbs — "replaces" / "scales" — and drop the capitalisation everywhere, including the section title. |
| **Tag-2 (dispatch) / IDF Tag 2 field** | 5 reader-facing (Ch00:7; Ch03:182,184,219,248; Tbl02:26) | Ch00:7; Ch03:182 (section title),184,219,248; Tbl02:26 | "Tag-2" is an EnergyPlus IDF field name repurposed as a routing key — it is genuinely internal (a spreadsheet-column name, not a modelling concept). Replace with a plain description throughout: "a per-space label used to route each occupancy channel to the matching building space." Drop "Tag-2" from the section title (Ch03 §3.5) and the Abstract entirely. |
| **decode-time exclusivity projection / mutual exclusivity** | Ch01:38; Ch03:71-81 | Ch01:38; Ch03:71,72,79,80 | Keep as a defined mechanism (it is explained), but shorten the label — "the exclusivity step" is enough after one definition. |
| **PCGrad** | 3 (Ch03:57,63; Sources-only Ch03:246) | Ch03:57,63 | Standard ML technique name (gradient-conflict correction), citable to its own paper — acceptable as a defined technical term but should carry a one-clause plain-English gloss at first use ("a technique that resolves conflicting gradients between tasks") since B&E readers are not ML specialists. |
| **SLAW** | 1 (Ch03:58) | Ch03:58, "(SLAW, uncertainty weighting)" | Named only as an alternative that was rejected, never explained. Either drop the acronym (say "other dynamic loss-balancing schemes") or give one clause of what it stands for. Low value to keep. |
| **fixed-weight scalarization / BCE positive-class weight / logit shift** | Ch03:56-62 | Ch03:56,57,59,60,61,62 | Standard ML terminology, acceptable for a Methods section, but dense; consider one summary sentence in plain language before the technical detail for a broader B&E readership. |
| **CYCLE_YEAR** | 1 (Ch03:68) | Ch03:68, "CYCLE_YEAR is encoded as a continuous conditioning value" | Raw internal variable name in ALL CAPS appearing directly in prose. Replace with "the survey cycle year" throughout. |
| **occPRE / occACT** | 8 (Ch03:18,22,24 x2,28; + formula) | Ch03:18,22,24,28 | Raw GSS codebook column names, kept in the final formula (Ch03 L22) and prose. Acceptable to keep in a supplementary codebook table (Table A2, out of this scope) but should not appear as raw variable names in main-text prose — replace with "the location variable" / "the activity variable" in sentences, keep the codes only inside the formula itself with a caption gloss. |

### A3. Channel / abbreviation vocabulary

| Term | Count | Occurrences | Recommendation |
|---|---|---|---|
| **AT_HOME / AT_WORK / AT_RETAIL** | AT_HOME 3 (Ch02:17; Tbl02:9 x2); AT_WORK 7 (Ch02:17; Ch03:49,193; Tbl02:10 x2; Tbl04 Sources-only); AT_RETAIL 16 (Ch02:19; Ch03:13,18,22,32,49,53; Tbl02:11 x2; Tbl04:27,32) | see counts | These are internal GSS-derived variable names used as if they were the channel names themselves. The channels already have plain names (Residential, Office, Retail) used in parallel throughout — the paper should pick ONE naming convention. Recommend: use "Residential", "Office", "Retail" as the primary terms everywhere in prose, and introduce AT_HOME/AT_WORK/AT_RETAIL exactly once, in Ch02 §2.1, as "the underlying survey-derived indicator variables," then never again in running prose (keep them only in Table 2 and the formula). |
| **GSSP** | 1 (Ch02:16) | Ch02:16, "the GSS Time Use 2022 cycle (GSSP)" | Defined once, never reused anywhere else in the manuscript. Pure dead abbreviation — delete it; just say "the 2022 cycle" thereafter (which the text already does). |
| **GSS** | 32 (Ch02:9, Ch03:10, Ch04:2, Ch05:3, Tbl01:1, Tbl02:5 — full line lists on file) | Ch02:14,16,18,20,41,42,51,52,66; Ch03:19,28,32,46,53,136,138,149,150; Ch04:48,60; Ch05:14,37,49; Tbl01:63; Tbl02:9,10,11,22,32 | Standard, definable abbreviation (General Social Survey) — correctly defined at first use, Ch02 L14. Fine to keep as-is; no action needed beyond confirming no earlier undefined use exists in Ch00/Ch01 (checked: none found — first use is Ch02 L14, which is itself after Ch01's own "General Social Survey" spelled-out mentions, so the ordering is safe). |
| **NECB** | 25 (Ch00:1; Ch02:4; Ch03:7; Ch04:1; Ch05:4; Tbl02:2; Tbl03:2; Tbl06:1) | Ch00:13(Sources-adjacent, keyword list); Ch02:27,70,73,80; Ch03:193,197,198,200,203,228,232; Ch04:46; Ch05:30,39,64,79; Tbl02:10,12; Tbl03:10,11; Tbl06:82 | **Never spelled out in reader-facing main text.** First used undefined at Ch02 L27 ("stays on the NECB code baseline"); even the section heading "NECB / PNNL Prototype Building Stock" (Ch02 L70) and the citation-style "NECB-2017 standard (National Research Council Canada, 2017)" (Ch02 L73) never write out "National Energy Code of Canada for Buildings." Add "(NECB; National Energy Code of Canada for Buildings)" at first use, Ch02 L27. |
| **PNNL** | 15 (Ch00:2; Ch02:3; Ch03:2; Ch04:1; Ch05:1; Tbl02:1; Tbl06:1) | Ch00:7,13; Ch02:39,70,72; Ch03:136,185; Ch04:13; Ch05:76; Tbl02:11; Tbl06:50 | **Never spelled out in reader-facing main text**, and used from the Abstract (Ch00 L7) onward. Only expansion anywhere is the citation parenthetical at Ch02 L72 ("U.S. DOE / PNNL") and the Reference-list title (Ch09 L36), neither of which functions as an in-text definition. Add "(PNNL; Pacific Northwest National Laboratory)" at first use — ideally in the Abstract itself, since PNNL appears there. |
| **SARIMA** | 19 (Ch00:1; Ch02:1; Ch03:6; Ch04:2; Ch05:2; Tbl02:2; Tbl06:1) | Ch00:7; Ch02:64; Ch03:146,158,171,173,178,248; Ch04:57,61; Ch05:36,141; Tbl02:12,24; Tbl06:16 | Standard statistical abbreviation — acceptable to use with brief gloss at first use (currently used undefined from the Abstract, Ch00 L7). Add "(a seasonal autoregressive time-series model)" at first use, and do not require the reader to already know the term from the Abstract onward. |
| **CFA / GFA-share** | CFA 3 reader-facing (Ch05:16,55,64; Tbl05:8,37; Tbl07:101) + GFA-share 4 (Ch05:56; Tbl05:8,37; Tbl07:128) | Ch05:16 (used BEFORE its own definition at Ch05:55 — ordering bug), 55,64; Tbl05:8,37 | CFA is used at Ch05 L16 ("median EUI (CFA basis)") a full 39 lines before it is defined at Ch05 L55 ("conditioned floor area (CFA...)"). Fix the ordering (define before first use, or move the definition earlier into Methods/Table 5's own header, which already carries a definition). GFA-share is defined properly at first use (Ch05 L56) — no action needed there. |
| **EUI** | 29 (Ch00:1; Ch02:1; Ch04:2; Ch05:7; Tbl03:1; Tbl04:4; Tbl05:5; Tbl06:4; Tbl07:2) | Ch00:7; Ch02:90; Ch04:37,114; Ch05:16,19,49,53,55,97,201; Tbl03:6; Tbl04:39,40,66,81; Tbl05:1,3,26,27,37; Tbl06:49,102,104,116; Tbl07:13,76 | Standard field abbreviation (energy use intensity), fine to keep, but currently never given an explicit "(EUI)" parenthetical tied to its own spelled-out phrase — the Abstract (Ch00 L6-7) uses "energy-use-intensity" and "EUI" as if pre-linked, and the Keywords list separately says "Energy use intensity band," but no single sentence does "energy use intensity (EUI)." Add that exact parenthetical at the first Abstract use. |
| **ASHRAE** | 17 (Ch02:1; Ch03:1; Ch04:1; Ch05:1; Ch09:2; Tbl03:2; Tbl04:4; Tbl05:1) | Ch02:88; Ch03:8; Ch04:35; Ch05:76; Ch09:3,5; Tbl03:8,16; Tbl04:7,19,20,58; Tbl05:35 | Standard, universally recognised in this field — no action needed; already effectively self-explanatory via "ASHRAE Guideline 14" and "ASHRAE 90.1-2019" full citation forms. |
| **SCIEU** | 3, all Ch03:236-237 | Ch03:236 (defines at first use: "NRCan Survey of Commercial and Institutional Energy Use (SCIEU...)") | Correctly defined at first use — no action needed. |
| **TMYx** | 2, both in Table 3 only, never in chapter prose (Tbl03:10,11) | Tbl03:10,11 | Chapter 2 §2.5 (Ch02:88-89) already uses the plain phrase "Typical Meteorological Year EnergyPlus weather file (EPW)" without the "TMYx" label — good practice. Table 3 should match: replace "TMYx" with "TMY" or the same plain phrase used in Ch02, since "TMYx" is a specific vendor/format code unexplained anywhere. |
| **NOC-by-NAICS** | 2 (Ch02:38; Ch03:129) | Ch02:38, "NOC-by-NAICS occupation/industry crosswalks"; Ch03:129 | Unexplained double-acronym (National Occupational Classification / North American Industry Classification System). Spell out at least once, at Ch02 L38. |
| **PUMF** | 3, defined at first use (Ch02:34) | Ch02:34 ("Census Public-Use Microdata File (PUMF...)"),39; Ch03:128 | Correctly defined at first use — no action needed. |
| **"Retail Retail"** | 2 (Ch03:136,39-40 via §2.2; Tbl03 none) | Ch02:39-40 ("a single PNNL 'Retail Retail' archetype"); Ch03:136 | This is a literal PNNL prototype-naming artefact (an archetype apparently named "Retail" twice in its own catalogue) preserved verbatim with scare-quotes. Reads as a typo to any reader unfamiliar with the PNNL catalogue. Rename in prose to "the PNNL retail archetype" and, if the actual catalogue name must be preserved for reproducibility, move the literal string into a footnote or Table 2 only. |
| **JS (Jensen-Shannon divergence)** | Spelled out at first use (Ch03:90, "Jensen-Shannon divergence tolerance"); bare "JS" only inside the val_score formula (Ch03:101) and Table 4 rows (Tbl04:32,35) | Ch03:90,101; Tbl04:32,35 | Acceptable — defined at first use in prose. The bare "JS" in the formula and table cells is fine as shorthand once defined; no further action beyond the val_score fix above. |

### A4. Structural / process vocabulary

| Term | Count | Occurrences | Recommendation |
|---|---|---|---|
| **cell / cells** (as in "campaign cell", "56 cells") | 91 (Ch00:2; Ch01:5; Ch02:1; Ch03:1; Ch04:8; Ch05:28; Ch06:7; Ch08:1; Tbl01:5; Tbl03:2; Tbl05:3; Tbl06:3; Tbl07:13 — full line list on file) | see line list above | "Cell" (a prototype × city × scenario combination) is defined at first use (Ch04 §4 intro, "56 cells in total," and the factorial description) but the word is also an overloaded, spreadsheet-flavoured metaphor used 91 times. Recommend an explicit one-time definition — "each simulated combination of tower, city and scenario, referred to below as a cell" — placed in Ch04 §4 opening, and keep the word thereafter since a plain-language replacement (e.g. "simulation run") would be repeated just as often and is not clearly better; the issue here is under-definition, not the word choice itself. |
| **two-channel construction stage** | 17 reader-facing (used consistently as the plain-language name for the prior "Leg-2" project stage) | Ch01:25(x2),... Ch02:18,36; Ch03:4,15,47,77,84,88,90,129,148,207; Ch04:14; Ch05:129; Ch06:13; Ch08:6 | This is already the GOOD outcome of a prior de-jargoning pass (an internal `3rdJ_leg_terminology_neutralisation.md` note confirms "Leg-2"/"Leg-3" were systematically replaced with this phrase). No further action needed — flagged here only so the rewrite team does not reintroduce "Leg-2" by mistake; Table 6's own title still says "Leg-3" and "Leg-2" throughout (see next row). |
| **Leg-2 / Leg-3 / "Leg-3 is additive…"** | Sources-only in chapters (already neutralised there); but **Table 6 title and body still use "Leg-2"/"Leg-3" throughout**, and Table 6's Manager-notes block (not reader-facing) also uses it | Tbl06:1 (title: "What Leg-3 added"),3,9-19 (column header "Two-channel stage artefact" is fine, but row prose says "Leg-2's..." nowhere in the visible rows — checked: the *reader-facing* row text avoids "Leg-2/Leg-3" and only the title and Manager-notes use it) | Table 6's title, "What Leg-3 added (the additive ledger)," is the one reader-facing place the internal codename survives. Rename to match the chapters' own convention: "What the four-channel stage added over the two-channel stage." |
| **frozen deliverable** | 7 total; 2 reader-facing (Ch05:7; Tbl05:3), 5 inside Table 7's stripped Manager-notes/Discrepancy sections | Ch05:7; Tbl05:3 (reader-facing); Tbl07:98,101,125,150 (Manager-notes, stripped, no action needed) | Internal pipeline/software term ("frozen" = a version-locked output directory). Replace with plain language: "the final campaign results" or "the dataset produced by the simulation campaign," defined once. |
| **uninjected** | 9 reader-facing (Ch00:1; Ch01:1; Ch04:1; Ch05:4; Ch06:1; Ch08:1) | Ch00:26 (Highlights); Ch01:36; Ch04:47; Ch05:30,34,63,66; Ch06:19; Ch08:6 | Internal pipeline verb ("inject" = write an occupancy schedule into the building model) turned into an adjective. The underlying concept (a control run with no occupancy signal applied) is legitimate and important to the paper's central finding, but "uninjected"/"injected" throughout read as software-pipeline language. Replace with plain phrasing: "without an occupancy schedule applied" / "the code-default control," defined once at first use (Ch04 §4.3) and then referred to as "the control" thereafter. |
| **additive-safe / additive by construction / additive claim / additive ledger** | 8 reader-facing (Ch01:38; Ch03:140,203; Tbl06 title + body) | Ch01:38; Ch03:140,203; Tbl06:1,3 | The underlying design property (a missing channel falls back safely to the code default, so adding channels cannot break existing behaviour) is a real and important methodological point. "Additive-safe" and "additive ledger" are internal shorthand for it. Replace with one consistent plain phrase defined once, e.g. "fails safely to the code default," and drop "ledger" from Table 6's title (see Leg-2/Leg-3 row above — the two fixes can be combined into one title rewrite). |
| **coincidence factor** | 5, but used undefined from the Abstract (Ch00:7) through Ch01/Ch06/Ch08, and only formally defined at Ch05 L124 — 5 uses before its own definition | Ch00:7 (Abstract, undefined); Ch01:34 (undefined); Ch05:124-127 (defined here); Ch06:7 (after definition); Ch08:5 (after definition) | Definition-ordering issue, same pattern as CFA. Either define in one clause the first time it is used (Abstract) or accept that Abstract/Highlights conventionally use undefined shorthand — but then the SECOND use (Ch01 L34, Introduction) should carry the definition, not defer it all the way to Results (Ch05 L124). |
| **"Chapter N" as cross-reference style** | 16 (Ch02:6; Ch03:4; Ch04:1; Ch05:3; Tbl01:1; Tbl07:1 — reader-facing; total incl. all forms) | Ch02 (6 instances); Ch03 (4); Ch04 (1); Ch05 (3); Tbl01 (1, in a stripped-Sources-adjacent block — verify); Tbl07 (1) | **Global structural issue, not a single term.** The manuscript is internally organised and cross-referenced as "Chapter 00" … "Chapter 10" with numbered "§3.4"-style subsections — a thesis/report convention. A Building and Environment research article should be organised as numbered Sections (1 Introduction … 8 Conclusion) with "Section 3.4" or simply "§3.4" as the cross-reference form, never "Chapter." Recommend a single global find-and-replace pass, "Chapter" → "Section," once chapter files are merged into the final section-numbered manuscript (check this hasn't already silently happened in `writing/submission/3J_manuscript_submission.md` — worth a follow-up check before the rewrite starts). |
| **L-numbers as bare cross-references (e.g. "Table 7, L14")** | 2 (Ch01:19, two instances in one sentence) | Ch01:19 ("Table 7, L14", "Table 7, L1") | Minor. These are interpretable in context (they point to Table 7's own row IDs L1-L16) but ask the reader to hold a second numbering scheme in mind. Recommend replacing with a short inline paraphrase instead of the code, e.g. "(a decline documented as a data-frame limitation in Table 7)" rather than "(Table 7, L14)." |
| **"tiler" / "tiling"** | 2 reader-facing (Ch03:33; Tbl06:13) | Ch03:33 ("The tiler that produces the 30-minute channel columns..."); Tbl06:13 | Internal code-component name (the script that converts a diary into 30-minute slots). Replace with a plain process description: "the step that converts each diary into 30-minute time slots." |

---

## Part B — Meta Sentences (structure-announcing, QA/process narration, unnecessary repetition)

31 individual sentence-level instances, grouped into 8 recurring families. Three families (the "no
band moved" repetition, the hotel-frame repetition, and the retail-staff repetition) account for 18
of the 31 — these are the highest-value cuts, since removing 15 of those 18 repeats (keeping one
canonical statement of each fact, generally the one already sitting in Table 5 or Table 7) removes
more total text than any single jargon fix in Part A.

### B1. Structure-announcing sentences

| # | File:line | Sentence | Note |
|---|---|---|---|
| B1.1 | Ch05:3-6 | "The four subsections below move from the raw behavioural driver behind each channel (Section 5.1), to its annual energy consequence measured against reference bands... (Section 5.2), to its reshaping of the load curve... (Section 5.3), and finally to how each channel responds... (Section 5.4)." | Delete. A table of contents restated in prose; the section headings already do this job. |
| B1.2 | Ch01:5 (last sentence) | "This is the gap the present study addresses: not 'does time-series occupancy improve a building energy model,' which the authors' own prior line has already answered for a single use, but 'what happens when that model has to carry four functionally distinct populations...'" | Keep the substance (it is the actual research-question framing) but rewrite as a direct positive statement of the question, not a "this is the gap / not X but Y" meta-formula. This exact rhetorical pattern is a report-writing habit, not a journal-article one. |

### B2. "No band moved / no gate verdict changed" — repeated 7 times

| # | File:line | Sentence | Note |
|---|---|---|---|
| B2.1 | Ch01:36 (last sentence) | "No band is widened, and no scoring rule is chosen because it happens to pass." | Keep ONE canonical statement of this — recommend keeping this one (earliest, in the Introduction's contribution statement) or the Ch05:8 one, and deleting the rest. |
| B2.2 | Ch05:8 | "No band value is moved and no gate verdict changes anywhere in this chapter." | Delete if B2.1 or B2.6 (Table 5) is kept as the canonical statement. |
| B2.3 | Ch05:90 | "No band value was moved and no gate verdict was changed to produce these results; all three failures are reported as findings about band applicability, not resolved by widening a band or by selecting whichever rule happens to pass." | Delete the first clause (repeat of B2.2, one paragraph later in the same chapter); the second clause ("reported as findings about band applicability...") carries new information and can stay. |
| B2.4 | Ch06:23-24 | "Nothing was moved: the floor stays at 100 and all 56 cells stay FAIL, median 71.02 kWh/m2/yr." | This one is channel-specific (office) rather than a general disclaimer, so it is closer to a genuine finding restated with its number — lower priority to cut, but still redundant with B2.1/B2.2 in spirit. |
| B2.5 | Ch06:33 | "No reference value was moved and no scoring rule changed once the outcome was known; together the three point at reference bands built for single-use stock lacking the resolving power to judge a channel inside a stacked mixed-use tower." | Delete the disclaimer clause; keep the synthesis clause ("together the three point at..."), which is the Discussion's actual job. |
| B2.6 | Ch08:5 (mid-paragraph) | "In every one of the three cases, the reference value was left exactly where it started, and no scoring rule was swapped once it was known which rule would pass." | This is the Conclusion's turn to restate it a sixth time. Delete — the Conclusion should state the finding (three gates fail, for band-applicability reasons), not re-prosecute the "we didn't cheat" defence a sixth time. |
| B2.7 | Tbl05:16-17 | "No band value was moved and no gate verdict was changed to produce this table." | This is the one place the statement is directly load-bearing (it sits right next to the table it describes) — reasonable candidate for the single kept instance, alongside B2.1. |

### B3. "Hotel guests are outside the survey frame" — repeated 6 times

| # | File:line | Sentence | Note |
|---|---|---|---|
| B3.1 | Ch01:19 | "...hotel guests are outside the General Social Survey's sampling frame by construction (Table 7, L1)." | Keep — first, and appropriately brief, mention (motivates the whole hotel side-track design). |
| B3.2 | Ch02:42-43 | "Hotel has no respondent-level archetype at all: guests are entirely outside the GSS sampling frame, so the channel is driven by a province-level multiplier..." | Redundant restatement within the same chapter as B3.3 below (both in Ch02, four lines apart across §2.2/§2.3). Delete one of the two. |
| B3.3 | Ch02:50-54 (§2.3 opening, two sentences) | "Hotel is the one channel in this paper with no General Social Survey signal behind it at all: overnight hotel guests are, by construction, outside the GSS Time-Use sampling frame, which samples the resident population at their dwelling of record." | Keep this one (it is the dedicated §2.3 topic sentence) and delete B3.2. |
| B3.4 | Ch03:137-138 | "Hotel cannot be linked to any respondent at all, because hotel guests are outside the GSS sampling frame by construction (Chapter 2, §2.3)..." | Already cross-references Ch02 — good practice — but still fully restates the fact rather than only citing it. Trim to the cross-reference alone: "...because hotel guests are outside the survey frame (§2.3)." |
| B3.5 | Ch06:38-39 | "hotel guests are outside the time-use survey frame by construction, so that channel runs on a provincial tourism series" | Fourth full restatement, in the Discussion's limitations summary. Acceptable to keep ONE short restatement here since Discussion sections conventionally re-list limitations — but shorten to a clause, not a full sentence. |
| B3.6 | Tbl07:8 (row L1) | "Hotel guests are outside the survey frame; the channel is driven by a tourism series." | This is Table 7's own row — legitimately the "canonical" one-line statement everything else should point to instead of restating. |

### B4. "Retail sees/models customers only, staff logged as at work" — repeated 5 times

| # | File:line | Sentence | Note |
|---|---|---|---|
| B4.1 | Ch02:25-28 | "One population the survey records but this paper's Retail channel deliberately does not model is retail staff: workers present in a store are coded as at work rather than as a retail-specific activity... Retail worker density therefore stays on the NECB code baseline..." | Keep — first and fullest explanation, appropriately placed in Datasets. |
| B4.2 | Tbl02:14-15 | "Retail models customer presence only: the survey logs retail workers as at work rather than as a retail activity, so staff density stays on the code baseline being modulated." | Near-verbatim restatement of B4.1 inside the very next table. Fine as a table footnote (tables are often read standalone), but note the duplication is almost word-for-word. |
| B4.3 | Ch03:196-197 | "...consistent with Retail modelling customer presence only." | Short cross-reference form — acceptable, low cost. |
| B4.4 | Ch06:39 | "retail sees customers only, the survey logging retail workers as at work" | Third full-sentence restatement in running prose (after Ch02 and implicitly Ch03). Shorten to a clause referencing Table 7 row L2 instead of re-explaining. |
| B4.5 | Tbl07:9 (row L2) | "Retail sees customers only; staff are logged as at work." | Canonical one-line version — everything else should point here. |

### B5. "Grocery/merchandise split not recoverable from 2015/2022 GSS codes" — repeated 3 times

| # | File:line | Sentence | Note |
|---|---|---|---|
| B5.1 | Ch02:41 | "...because the grocery/merchandise split needed for a finer archetype lookup is not recoverable from the 2015/2022 GSS location codes (§2.1)." | Keep — first mention, with cross-reference. |
| B5.2 | Ch03:29-30 | "...in both 2015 and 2022 the grocery and general-merchandise locations are collapsed into a single bucket and cannot be separated." | Restates the same underlying data limitation a second time, four sections later. Fold into a one-clause cross-reference to §2.1/§2.2 instead. |
| B5.3 | Ch03:134-136 | "Retail cannot be linked to a specific archetype at finer resolution than a single population fraction, because the grocery/merchandise location split needed to place a respondent against a particular retail sub-type is not recoverable from the 2015/2022 GSS coding (§3.1)..." | Third restatement, same paragraph-family as B5.2, twelve lines later in the same chapter. Merge B5.2 and B5.3 into one sentence. |

### B6. Defect-history narration (named explicitly in the task brief: wiring bug, stale-output guard, checkpoint-selection audit)

| # | File:line | Sentence | Note |
|---|---|---|---|
| B6.1 | Ch03:93-116 (whole paragraph group, "checkpoint selection" through "reduces to global argmax F1") | Multi-sentence narration of a disclosed deviation between the specified checkpoint-selection rule and what the training code actually did, including "Three things are stated rather than smoothed over" (L108) as its framing sentence. | This is an internal engineering post-mortem, not Methods content a journal reader needs. Recommend cutting to 2-3 sentences: state which checkpoint was shipped, on what criterion, and note in one clause that it differs from the pre-registered rule for evidenced reasons — move the full audit trail to the Supplementary/internal record. |
| B6.2 | Ch03:206-214 | "A hard wiring gate is asserted after every injection, and its origin is a defect found in the two-channel construction stage rather than in this paper's own new code. There, a modulated occupancy schedule was referenced by the wrong field of the People object, one that still existed and still held a syntactically valid schedule. Every input-side check available at the time... therefore passed cleanly; the defect flattened the Office channel's temporal signal and was caught only when Office simulation output failed to differ from an unmodulated baseline." | This is the "wiring bug" defect-history example named directly in the task brief. The underlying methodological point (input-side checks are insufficient; an output-side probe is also needed) is legitimate and worth keeping in one sentence; the step-by-step bug narrative (wrong field, still-valid schedule, how it was caught) is a debugging diary and should be cut or moved to Supplementary. |
| B6.3 | Ch04:78-98 (§4.4 "Two Mandatory Probes" intro + stale-output guard paragraph) | "...both exist because of the defect described in §3.5: a modulated schedule referenced by the wrong field passed every input-side check... The guard first implemented fingerprinted only the injector; it was extended to cover the schedule products as well, because a scenario's schedule content, not only the injector code, determines what gets injected." | Restates B6.2's bug narrative a second time (cross-chapter), then adds its own second defect-history story (the stale-output guard's own evolution from injector-only to injector+schedule fingerprinting) — this is the "stale-output guard" example named in the task brief. Cut the repeated bug narrative (link to §3.5 instead) and shorten the guard's own history to one clause: "the guard checks both the injector code and its input schedules." |
| B6.4 | Ch06:49-54 | "One reproducibility caveat belongs here. The residential intensity table in the authors' prior single-channel study... rests on an extraction function with two compounding defects, a demand summary double-counted into an annual energy total and a water-heating guard that zeroes water energy on SI-unit runs but not imperial ones; correcting both moved three of four band verdicts." | Defect-history narration about a DIFFERENT, prior paper's bugs, included here only to argue the present study is "immune structurally." The caveat's conclusion (this study reads intensities from hourly meter streams, so it cannot inherit that specific bug) is worth one sentence; the two-defect inventory of the other paper's bug is not needed in this paper at all. |

### B7. Near-verbatim duplication between Introduction's aim statement and the Conclusion's opening

| # | File:line | Sentence | Note |
|---|---|---|---|
| B7.1 | Ch01:42 vs. Ch08:3 | Ch01: "*This paper asks what four functionally distinct occupant populations do to a single stacked building when each is carried on its own behavioural signal rather than blended into one, whether a single jointly-trained occupancy model can generate all four, and where the energy-use-intensity references built for single-use stock do, and do not, still apply to the result.*" / Ch08: "This paper asked what four functionally distinct occupant populations do to a single stacked building when each is carried on its own behavioural signal rather than blended into one, whether one jointly-trained occupancy model can generate all four, and where the energy-use-intensity references built for single-use building stock do, and do not, still apply to the result." | Near word-for-word identical (only tense and two minor word swaps differ). Standard practice is for a Conclusion to echo the aim, but not reproduce it almost verbatim. Rewrite the Conclusion's opening to summarise the ANSWER rather than restate the QUESTION in the same words. |

### B8. Instructive / defensive asides addressed to the reader rather than stating the science

| # | File:line | Sentence | Note |
|---|---|---|---|
| B8.1 | Ch05:28-29 | "Hotel's apparent flatness across the same four cycles is a feature of the campaign design, not a measured behavioural finding, and must be read as such." | "...and must be read as such" is an instruction to the reader rather than a statement of fact. Rewrite as a plain causal statement: "...because Hotel is uninjected in 2005-2015 (§4.3), this reflects the campaign design rather than a measured signal." |
| B8.2 | Ch03:51-54 | "Figure 3 draws the resulting topology, with the hotel side-track placed beside the encoder and connected to nothing inside it, because the distinction between three GSS heads plus one non-GSS side-track and a four-head model is the one reading of this architecture that must not be got wrong." | "...must not be got wrong" reads as an internal note to the figure-maker/reviewer, not manuscript prose. Cut the clause; the figure and one plain sentence ("Hotel is generated by a separate model, not a fourth Transformer head") already make the point. |
| B8.3 | Ch06:13-15 | "Bit-identity across stages is not claimed: five of the nine steps carry no cross-stage comparison, and Table 6 says so." | "...and Table 6 says so" is a self-referential aside (the table doesn't "say" anything to a reader; it reports data). Cut the clause; the preceding statement of fact is sufficient and Table 6 is already cross-referenced by its caption elsewhere. |

---

## Notes for the rewrite pass

1. Three families (B2 "no band moved," B3 hotel-frame, B4 retail-staff) account for 18 of the 31
   flagged sentences and are largely redundancy — cutting to one canonical statement each (already
   present, in Table 5/Table 7 in most cases) removes a meaningful amount of running text with little
   loss of content.
2. The jargon fixes with the highest reader-confusion cost are the ones used from the **Abstract**
   before being defined anywhere: PNNL, NECB, SARIMA, EUI, coincidence factor, CFA, Tag-2, gate/PASS/
   FAIL/INFO. A B&E reviewer meets all of these on the first page with no gloss.
3. "Chapter N" (16 occurrences) is a single global find-and-replace once the manuscript is section-
   numbered for submission — check whether `writing/submission/3J_manuscript_submission.md` has
   already done this before duplicating the effort.
4. Table 6's title ("What Leg-3 added (the additive ledger)") is the one place a retired internal
   codename ("Leg-3") survives into reader-facing text outside the chapters — fix alongside the
   "additive-safe" jargon fix (Part A) since both land on the same sentence.


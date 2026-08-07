# Building Simulation — submission requirements, read from the journal's own documents

**Source:** `12273_Instructions_for_Authors_Building_Simulation__15-10-25.pdf` (the current version, downloaded
by the author 2026-08-07) and `12273_Building_Simulation_Template_2025/`. Cross-checked against the
2022 edition of the same document: **the abstract and keyword rules are identical in both**, so they
are stable, not a recent change.

**Everything on this page was read from those two files.** Nothing here comes from `dr_2J-01` through
`dr_2J-05`, several of whose package claims turned out to be wrong (listed at the end).

---

## 1. The answer to the abstract question

> "Please provide one paragraph containing a complete but concise description of your work in
> **100–250 words**."

**The current abstract is 235 words. It fits. Do not cut it.**

The 193-word version produced by `dr_2J-04` was cut to a 200-word cap that does not exist — that report
never had the requirements document and supplied the number from general knowledge. Keep the 193-word
text only as a spare; there is no reason to submit it.

Three further conditions the abstract must satisfy, and does:

| Rule | Status |
|---|---|
| One paragraph, unstructured | ✅ already one paragraph — **do not use `dr_2J-04`'s structured variant**, this journal does not take one |
| No cited references in the abstract | ✅ none present |
| No undefined abbreviations | ⚠️ check `SHEU`, `GSS`, `EnergyPlus`, `pp` on a final read |

## 2. Keywords — this one did need fixing

> "Please provide **4 to 6 keywords**."

The manuscript carried **7**. `dr_2J-04` said the requirement was "5 to 8" and told you to keep all
seven; that was wrong in both directions.

**Fixed in both `2J_manuscript_submission.md` and `.docx`:** dropped **Peak Demand**, leaving six —
Occupancy Modelling; Building Performance Simulation; Time-Use Survey; Load Shape; Longitudinal
Forecasting; COVID-19 / Work-From-Home. Peak Demand was chosen because the paper's peak result is a
**null** (0 ± 1 h), so it is the one term that promises a finding the paper does not make. Load Shape,
which is the headline, is kept. If you would rather sacrifice a different one, the pre-edit `.docx` is
in `../extra/2J_manuscript_submission_BEFORE_keywords.docx`.

---

## 3. 🔴 The requirement nobody flagged: this journal is DOUBLE-BLIND

> "Building Simulation follows **double blind** reviewing process. The authors are required to submit
> two separated files, (1) **Title page** including author related information; (2) **Blinded
> Manuscript** without any author information and acknowledgements (if any). Please note: the
> supporting material to the manuscript will be reviewed by the reviewer. **Any author information
> should be removed from the supporting data.**"

This is the single biggest gap between what exists today and what can be uploaded, and no report in the
`dr_2J-*` set mentioned it. It restructures the package.

### File 1 — Title page (template provided)

Everything below moves **out of** the manuscript and **into** this file:

- **The cover letter**, addressed to the **Editor-in-Chief** — not to an associate editor. `dr_2J-04`
  addressed its letter to Prof. Bing Dong as handling editor; that is not what the template asks for.
  Its stated job is "explaining why the paper is significant".
- Title · all author names in order (full names, not initials) · affiliations with city, post code,
  country · corresponding author's email (mark with `*`)
- **Acknowledgements and funding** — currently §Declarations in the manuscript
- **Author contribution statement** — currently the CRediT statement
- **Declaration of competing interest** and **Ethical approval**

### File 2 — Blinded manuscript

Strip from the current manuscript: the entire **Author Information** block, **Acknowledgements**,
**Funding**, and the **CRediT statement**. Then deal with the hard part:

> 🔴 **§1.4 de-anonymizes the paper.** It is titled "The Authors' Prior Line", says "by the authors",
> and cites *Iseri and Hachem-Vermette (under review)*, *Iseri and Hachem-Vermette (2026)* and *Iseri,
> Dino and Kalkan (2026)*. The new §1.4 originality paragraph — the one your supervisor asked for — has
> the same problem.
>
> **These cannot simply be deleted:** the originality statement is the reason §1.4 exists. The standard
> resolution under double-blind review is to **keep every citation but write them in the third person**
> — "A prior study (Iseri and Hachem-Vermette, under review) asked *how much*…" instead of "The present
> study departs from a specific prior line of work by the authors." The distinction the supervisor
> wanted survives; the first-person ownership claim is what goes.
>
> **This is your call, not mine** — some authors prefer `[Author citation]` placeholders. Tell me which
> and I will make the pass.

Also check the **supplementary material** for author names, since the instructions say reviewers see it.

---

## 4. Formatting — where the current files do not yet comply

| Requirement (verbatim from the instructions) | Current state | Action |
|---|---|---|
| **"Do not add line numbers in your manuscript"** — the system adds them automatically | none present | ✅ nothing to do. **Ignore `dr_2J-04`, which told you to enable line numbering** |
| 12-point Times Roman, **double spaced**, one column | not set | set on export |
| Automatic page numbering | — | set on export |
| Figures **PDF/PNG/JPEG, minimum 600 dpi** relative to final size | 7 PNG, resolution unverified | **check — `dr_2J-04` said 300 dpi, the real figure is 600** |
| Figures cited as **"Fig. 1"**, captioned `Fig. 1 …` | manuscript uses "Figure 1" | global rename |
| Tables captioned `Table 1 …` | manuscript uses "**Table 1.**" | drop the bold and the period |
| Citations **by name and year in parentheses, no comma** — "(Thompson 1990)" | manuscript uses "(Statistics Canada, 2021)" | comma removal throughout, or leave for copy-editing |
| Decimal numbered headings | ✅ already `1`, `1.4`, `2`… | none |
| Reference list = cited, published or accepted work only | ⚠️ the companion paper is *under review* | see §6 |
| **"less than 40 manuscript pages"** double-spaced | unknown | check on export |
| **"the total number of tables should be less than 5"** | **5 tables** | 🔴 one over the stated norm — see below |
| "the total number of figures should be less than 15" | 7 | ✅ |

**On the five tables:** the wording is "Generally… should be less than 5", inside a section that opens
"There is no strict limit on the length of a manuscript." It is a norm, not a hard gate, and one table
over is not a desk-reject risk. The cheapest fix if you want to comply exactly is to move **Table 3
(simulation domain)** to the supplementary material, since it is reference detail rather than a result.
Your call; I would submit with five and not lose sleep.

---

## 5. Do you need to pour everything into the Word template?

**No — and I would not.** The template says "Use this document as a template **if** you are using
Microsoft Word", and the instructions never make it mandatory. What *is* mandatory is the two-file
split, the blinding, and the formatting rules above — none of which requires retyping a 26 MB document
into a new shell, an operation whose main product is broken cross-references and lost figures.

**The efficient path:**

1. **Build the Title Page from the template.** It is about one page. Use
   `Template_12273_Title_Page_Cover_letter.docx` directly — it is short enough that filling it in is
   faster than formatting your own, and it guarantees you match the expected field order.
2. **Do not use the Blinded Manuscript template as a container.** Use it as a *checklist*: read its
   section 3 and 4 rules, apply them to your existing `.docx`, save under a new name.
3. Keep both files in this folder, leave the main submission directory as your working master.

---

## 6. Still open before upload

1. **Blinding decision for §1.4** (above) — the only item that touches the science writing.
2. **Department line and both ORCIDs** are `[confirm]` in the front matter. ORCID is recommended by the
   journal at submission.
3. **Companion paper status.** The reference list "should only include works that are cited in the text
   and that have been **published or accepted for publication**"; personal communications and
   unpublished works "should only be mentioned in the text". A paper *under review* is neither
   published nor accepted, so strictly it belongs in the text, not the reference list. Since §1.4 leans
   on it, confirm its status — if it has been accepted since, this problem disappears.
4. **Suggested reviewers need institutional email addresses.** The instructions are explicit: "the
   Corresponding Author **must** provide an institutional email address for each suggested reviewer",
   or a verifying link. **The five addresses in `dr_2J-04` are pattern-guesses, not looked-up
   addresses.** Verify each on the person's own institutional page or replace the address with a
   profile link. They also ask for "a mix of reviewers from different countries and different
   institutions" — the current five (US, US, Italy, Belgium, Spain) satisfy that.
5. **Graphical abstract** — three candidates exist in `../figures/graphicalAbstract/`. Note the
   instructions do not require one; it is optional here.
6. **Highlights** — the word does not appear anywhere in the instructions. The 5 bullets are **not
   required** by this journal. Keep or drop as you prefer.

---

## 7. What the research reports got wrong about the package

Recorded so these do not creep back in:

| Claim in `dr_2J-04` | Reality |
|---|---|
| Abstract cap 200 words | **100–250** |
| Structured abstract variant for Springer fields | Not used by this journal — one paragraph |
| "5 to 8 keywords, retain 7" | **4 to 6** |
| Figures "≥300 DPI" | **600 dpi** |
| "with line numbering enabled" | **"Do not add line numbers"** |
| Cover letter to Associate Editor Bing Dong, as its own upload | To the **Editor-in-Chief**, inside the **Title Page** file |
| Editorial Manager at `editorialmanager.com/buis/` | **`editorialmanager.com/buil`** |
| "100% APC waiver via CRKN Springer" | Excluded — Tsinghua co-published. $0 by subscription route |
| No mention of double-blind review | **Double-blind, two files, mandatory** |

The checklist items `dr_2J-04` took from the manuscript itself (7 figures, 5 tables, 3 graphical-abstract
candidates, correct declaration line numbers) were all accurate. It was reliable about the file it read
and unreliable about the journal it never read.

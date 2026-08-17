# Open items — UK `WithOther` scope and Spain `ASECU` code list

Read-only evidence task. All facts below are traced to a specific file and page/row/position in
the delivered archives. Sources read:

* UK — `mrdoc/pdf/8128_ctur_report.pdf` (CTUR report, cited as CTUR p. N, printed page number,
  verified against the PDF's own printed footers, not the PDF page index — see verification note
  at the end); `mrdoc/allissue/uktus15_diary_ep_long_ukda_data_dictionary.rtf` (cited as
  DD:diary_ep_long, `Pos. = N`), both under
  `_local_runs/4J/raw/uk/unpacked/UK-TUS/UKDA-8128-tab/`.
* Spain — `DISEnOS DE REGISTRO EET 2009 2010.xlsx`, sheet `F DIARIO2` (cited as LAYOUT, sheet
  `F DIARIO2`, row N); `meth_t25304471.pdf` (METH, cited as METH p. N, printed page number,
  verified against the PDF's own printed footers), both under `_local_runs/4J/raw/spain/`.
* Also read for cross-check: `Step1_docs/outputs_step1/codebook_facts_uk.md`,
  `codebook_facts_spain.md`, `crosswalk_source_spain_activity.csv`.

Where a claim could not be found in either source, it is written `NOT STATED IN CODEBOOK`.

---

## Question 1 — UK `WithOther` scope

### (a) Exact variable names of every co-presence column

Nine columns, positions 40-48 of `uktus15_diary_ep_long.tab`, all binary 0/1 flags:
`WithAlone`, `WithSpouse`, `WithMother`, `WithFather`, `WithChild`, `WithOther`, `WithOtherYK`,
`WithMiss`, `WithNA`.

Source: DD:diary_ep_long, `Pos. = 40` through `Pos. = 48` — verbatim extract:

```
Pos. = 40  Variable = WithAlone    Variable label = Alone
Pos. = 41  Variable = WithSpouse   Variable label = With spouse/partner
Pos. = 42  Variable = WithMother   Variable label = With mother
Pos. = 43  Variable = WithFather   Variable label = With father
Pos. = 44  Variable = WithChild    Variable label = With child 0-7 years
Pos. = 45  Variable = WithOther    Variable label = With other person(s) (incl. child 8+ years)
Pos. = 46  Variable = WithOtherYK  Variable label = With other(s) you know outside of HH
Pos. = 47  Variable = WithMiss     Variable label = No co-presence reported
Pos. = 48  Variable = WithNA       Variable label = Sleep/Work/Education UK2000 concordance
```

Corroborated independently by CTUR's own Appendix 1, section "1.2 With whom time is spent"
(CTUR p. 21), which lists the diary's own response categories in the same order (excluding the
two CTUR-added flags `WithMiss`/`WithNA`, which are not diary response categories):

> "1.2 With whom time is spent
> Alone or with people not know to respondent
> With spouse/partner
> With mother
> With father
> With children 0-7 years
> With other household members
> With others you know"

### (b) The codebook's own verbatim wording of what each column covers

| Variable | Verbatim DD variable label | Verbatim value labels (0 / 1) |
|---|---|---|
| `WithAlone` | "Alone" | "Not reported" / "Reported" |
| `WithSpouse` | "With spouse/partner" | "Not reported" / "Reported" |
| `WithMother` | "With mother" | "Not reported" / "Reported" |
| `WithFather` | "With father" | "Not reported" / "Reported" |
| `WithChild` | "With child 0-7 years" | "Not reported" / "Reported" |
| `WithOther` | "With other person(s) (incl. child 8+ years)" | "Not reported" / "Reported" |
| `WithOtherYK` | "With other(s) you know outside of HH" | "Not reported" / "Reported" |
| `WithMiss` | "No co-presence reported" | "Co-presence reported" / "No co-presence reported" |
| `WithNA` | "Sleep/Work/Education UK2000 concordance" | "Not reported" / "main act: work/edu/sleep" |

Source: DD:diary_ep_long, `Pos. = 40-48` value-label blocks (verbatim, quoted above).

### (c) The exact age range the children column covers

`WithChild`'s own DD variable label is verbatim: **"With child 0-7 years."**

Source: DD:diary_ep_long, `Pos. = 44`.

Corroborated in prose by CTUR p. 11-12, section 5.2 "Differences in co-presence categories":

> "In UKTUS 2000-01 time with a child 0-9 and with a child 10-14 could be reported, whereas in
> UKTUS 2014-15, only time with a child 0-7 years could be reported. Time with children 8-9 and
> 10-14 years will be reported as time with other members of the household."

### (d) What `WithOther` covers, and whether older children fall into it

`WithOther`'s own DD variable label is verbatim: **"With other person(s) (incl. child 8+
years)."** The codebook states this explicitly and directly — this is not an inference.

Source: DD:diary_ep_long, `Pos. = 45`.

This is independently corroborated by the CTUR narrative quoted under (c) above (CTUR p. 11-12,
section 5.2): children aged 8-9 and 10-14 (i.e. every diary-eligible child above the `WithChild`
cutoff, given the survey's own minimum age of 8) "will be reported as time with other members
of the household" — the free-text description of the same field the DD labels `WithOther`.

**Verdict for Question 1: CONFIRMED.** The working assumption — that the UK "with children"
column (`WithChild`) covers ages 0-7 only, and that children aged 8 and above are pooled into
`WithOther` and are therefore unrecoverable as a distinct "with older child" category — is
confirmed verbatim by the delivery's own data dictionary variable label for `WithOther`, and
independently corroborated by CTUR's narrative documentation (two independent citations within
the same delivery, not one citation read two ways).

### (e) The difference between `WithMiss` and `WithNA`

Both are binary flags, but they answer different questions, per the DD's own value labels
quoted in (b):

* **`WithMiss`** ("No co-presence reported"): `1` = "No co-presence reported", `0` = "Co-presence
  reported". This is a genuine missingness flag for the episode's co-presence data as a whole.
  Corroborated by CTUR p. 6, section 3.2 "Missing co-presence data":

  > "Co-presence data is deemed missing if the respondent provided no information about
  > co-presence in any time slot. Users should take care to note whether time in any individual
  > field of co-presence (time with children 0-7 years for example) is truly not-reported, or
  > whether no co-presence information was reported in that time slot. As in UKTUS 2000-01, a
  > missing co-presence field has been added to the data to aid with this."

* **`WithNA`** ("Sleep/Work/Education UK2000 concordance"): `1` = "main act: work/edu/sleep",
  `0` = "Not reported". This is **not** a missingness flag for the 2014-15 data — it is a
  backward-compatibility marker flagging episodes that would have gone uncoded for
  location/co-presence under the UKTUS 2000-01 design. Corroborated by CTUR p. 10, section 5.1
  "Differences in coding of secondary activity paid work, and contextual information":

  > "In 2000-01, when a respondent reported time in paid work, education or sleeping,
  > information about location and co-presence was not coded. In 2014-15, both location and
  > co-presence were coded when the respondent reported time at work, education, or sleeping...
  > we have added an additional variable indicating time when respondents report paid work,
  > education or sleep. It should be applied in any comparative work using either the
  > co-presence or location data in UKTUS 2000-01 and 2014-15."

So `WithMiss=1` means "this episode's co-presence data is genuinely absent"; `WithNA=1` means
"this episode is paid work/education/sleep, which is fully coded in 2014-15 but would not have
been coded in 2000-01" — the two are not alternate spellings of the same concept.

---

## Question 2 — Spain's `ASECU` code list

### (a) The codebook's stated code list for `ASECU`, with page/row reference

LAYOUT, sheet `F DIARIO2`, row 37 (verbatim):

> `ASECU | Posición 17-19 | Actividad secundaria | Valores válidos = Lista EET`

`ASECU` occupies character positions 17-19 of the `DIARIO2` record — **3 digits**, the same width
as `APRIN` (primary activity, positions 13-15, also `Lista EET`). "Lista EET" is glossed by the
workbook itself immediately below the `APRIN` row, LAYOUT sheet `F DIARIO2`, row 33 (verbatim):

> `Lista EET=Lista de actividades Encuesta de Empleo del Tiempo`

The number of modalities in that list is **not independently re-stated for `ASECU`** anywhere in
LAYOUT or METH; the workbook's device is to point `ASECU` at the same named list rather than
enumerate a separate one. The list itself (referenced by name for both `APRIN` and `ASECU`) is
enumerated in METH pp. 66-71, Annex I, and — per `codebook_facts_spain.md` F-ES-5 — contains
**116** three-digit codes as delivered (INE's own prose at METH p. 22 says 115; the enumeration
and the delivered file both show 116; the discrepancy is INE's, not introduced here).

### (b) Same classification as the primary activity variable, or different?

**Same classification — stated explicitly by the codebook, in two independent places, not
inferred.**

1. LAYOUT, sheet `F DIARIO2`: `APRIN` (row 32) and `ASECU` (row 37) both carry the identical
   "Valores válidos" entry `Lista EET`, and row 33's gloss of "Lista EET" sits directly beneath
   the `APRIN` row, naming the one list both rows point to.

2. METH p. 49 (verbatim, Spanish, own translation in brackets):

   > "Para la clasificación de la actividad secundaria se utilizaron los mismos códigos de la
   > lista de actividades armonizada española 2009."
   > ["For the classification of the secondary activity, the same codes from the Spanish
   > harmonised activity list 2009 were used."]

3. METH p. 65-66, section "5. Actividad principal y secundaria", the NOTE printed immediately
   before the Annex I code enumeration begins (verbatim):

   > "NOTA: Las actividades principales y secundarias se codificarán utilizando esta misma
   > lista."
   > ["NOTE: Primary and secondary activities will be coded using this same list."]

**This refutes any assumption that Spain follows Italy's pattern** (Italy's `catcon` is reported
elsewhere as a separate, coarser classification, not a truncation of the primary list). For
Spain, the codebook states outright — twice, in two separate documents — that `ASECU` and
`APRIN` share one identical list; nothing here needed to be inferred from digit width or field
size alone, though the field widths (both 3 digits) are also consistent with that statement.

**Verdict for Question 2(b): the "same list" side of the question is CONFIRMED**, directly from
the codebook's own words, not from an assumption carried over from Italy or from Spain's own
primary-list structure.

### (c) Sentinel / missing-value coding for `ASECU`

LAYOUT, sheet `F DIARIO2`, row 38, directly beneath the `ASECU` row, verbatim:

> `Blanco.....................................................................................`

Unlike the co-presence flags (`SOLO`, `PAREJA`, etc., each documented with explicit `Sí`/`No` →
`1`/`6` value pairs in the same sheet), `ASECU`'s row 38 entry carries **no paired numeric code**
in the "Valores válidos" column — the documented state for "no secondary activity" is the field
being left **blank** (an empty string in the fixed-width record), not a reserved numeric sentinel
value such as Spain's location field has none of either (per `codebook_facts_spain.md` M-1,
`LUGAR` also has no declared sentinel).

METH was searched directly for "blanco" / "en blanco" in connection with `ASECU`; the only hits
in the whole 127-page document are two unrelated occurrences of "Libro blanco" (a proper-name
report title, METH p. 7). **METH itself does not corroborate or restate the blank-field
convention for `ASECU`** — the only source for it is the LAYOUT workbook's row 38.

This is consistent with — but not the same claim as — the measured fact already on record in
`codebook_facts_spain.md` F-ES-6: `ASECU` is non-blank on 340,269 of 2,778,480 `DIARIO2` slots
(12.2%). That earlier note reported the measured proportion; this task adds the codebook's own
citation for *why* blank is the expected non-response state (LAYOUT row 38), which F-ES-6 did not
cite.

---

## What was NOT independently verified

* **UK, Question 1** — the exact printed-page mapping for CTUR was re-derived here from the
  PDF's own footer numbers (see verification note below) rather than assumed from
  `codebook_facts_uk.md`'s existing citations; all four CTUR citations used here (p. 6, p. 10,
  p. 11-12, p. 21) were independently reproduced and matched the existing codebook's citations
  exactly, so this is corroboration, not a new unverified claim.
* **UK** — whether `WithOtherYK` ("with other(s) you know outside of HH") also absorbs any part
  of the 8+ children population (e.g. a child known to but not living with the household) is
  `NOT STATED IN CODEBOOK`. Neither the DD label nor CTUR's section 5.2 narrative addresses this;
  both describe the split only as `WithChild` (0-7) vs. `WithOther` (8+, "other household
  members"/"other person(s)"). This document does not assume `WithOtherYK` is irrelevant — it
  is simply silent in both sources on this specific edge case.
* **Spain, Question 2(a)** — the codebook (LAYOUT or METH) does **not** separately re-enumerate
  or re-count the modalities of the "Lista EET" list specifically in the context of `ASECU`'s own
  row; the 116-modality, 3-digit count is carried over from the primary-activity enumeration
  (METH pp. 66-71) on the strength of the "same list" statements quoted in (b), not from a
  second, independent enumeration keyed to `ASECU` itself. If the manager needs a citation that
  enumerates `ASECU`'s codes under `ASECU`'s own heading, rather than by cross-reference, that is
  `NOT STATED IN CODEBOOK` as a standalone list.
* **Spain, Question 2(c)** — METH gives no corroborating statement of the blank-as-sentinel
  convention for `ASECU`; the only source is LAYOUT row 38. Whether INE's separate diary-coding
  manual (referenced in METH p. 49 as "el manual de codificación del diario de actividades," a
  document distinct from METH and not present in this delivery) says more about this is
  `NOT STATED IN CODEBOOK` — that manual was not part of the delivered archive read for this
  task and was not opened.
* **Both countries** — whether `ASECU`'s "same list as primary" or the UK's `WithOther` scope
  hold across other HETUS-family deliveries (Italy, France) is outside this task's scope and not
  addressed here.

### Verification note on CTUR page-number citations

CTUR's printed page numbers were confirmed, not assumed, by extracting the PDF to text with
`pdftotext -layout` and tagging each page's content against that page's own printed footer
number. Printed page = (PDF page index − 1) held consistently across every page checked (PDF
page 7 → footer "6"; PDF page 11 → footer "10"; PDF page 12 → footer "11"; PDF page 21 → footer
"20"; PDF page 22 → footer "21"). All CTUR page citations above use the printed footer number,
matching `codebook_facts_uk.md`'s existing citation convention.

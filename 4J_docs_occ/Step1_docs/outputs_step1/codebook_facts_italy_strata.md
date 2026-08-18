# Codebook facts — Italy, strata addendum (M-8 / D-S2-18)

### Step 1, contract change M-8-a. The six conditioning-strata sources, transcribed from the
### delivery's own documentation. Extends `codebook_facts_italy.md`, does not replace it.
#### Compiled 2026-08-17 from the delivery itself. **No source here is taken from `RL02`, `RL17`,
#### or from Spain's or the UK's codebook.**

Same sources as `codebook_facts_italy.md`:

* **TRACC-IND** — `METADATI\uso_tempo_Tracciato_Anno 2013_Individui.html`, the individual-file
  record layout. Cited as TRACC-IND row N (the table's own `num. ordine` column).
* **TRACC-DG** — `METADATI\uso_tempo_Tracciato_Anno 2013_DiarioGiornaliero.html`, the daily-diary
  record layout. Cited as TRACC-DG row N.
* **CLS-var*N*** — `METADATI\Classificazioni\uso_tempo_Classificazione_Anno 2013_<file>_var<N>.html`,
  the code list for variable number N of the named file. Cited as CLS-var*N*.

Row-level population counts below were measured directly from
`uso_tempo_Microdati_Anno_2013_Individui.txt` (44,866 rows) and
`uso_tempo_Microdati_Anno_2013_DiarioGiornaliero.txt` (1,077,657 rows) at
`_local_runs/4J/raw/italy/unpacked/MICRODATI/`, `cp1252`-decoded per the encoding note already
established in `codebook_facts_italy.md`.

A stratum that could not be found in the delivery is written `NOT FOUND` and stays that way. None
of the six was NOT FOUND for Italy.

---

## THE SIX STRATA

| Stratum | Variable | File | Row | Grain | Value list (delivery's own labels) | Citation |
|---|---|---|---|---|---|---|
| **age** | `claseta2` | `Individui.txt` | TRACC-IND row 20 | person | 🔴 **All eleven bands, transcribed in full:** `01` fino a 2 (0-2); `02` 3-5; `03` 6-10; `04` 11-14; `05` 15-24; `06` 25-34; `07` 35-44; `08` 45-54; `09` 55-64; `10` 65-74; `11` 75 e più (75+) | TRACC-IND row 20; CLS-var20. Already carried in Step 1's Italy parquet. Delivered **pre-banded**, disclosure-controlled (F-IT-2, F-IT-11) — no exact-age field exists anywhere in this delivery |
| **sex** | `sesso` | `Individui.txt` | TRACC-IND row 7 | person | `1` Maschi (male); `2` Femmine (female) | TRACC-IND row 7; CLS-var7. Already carried |
| **household type** | `tipfa2m` | `Individui.txt` | TRACC-IND row 16 | **household** (verified: 0 of 19,093 `profam` groups carry more than one distinct value — see F-IT-15) | "tipologia familiare" (family/household typology). 🔴 **Up to 40 codes**, condensed here to the structure: `1` Persona sola (one person); `2` Genitore con figli non celibi/nubili (parent + ever-married children); `3` Insieme di parenti (group of relatives); `4` Parenti ed altri (relatives + others); `5` Persone non parenti (unrelated persons); `6`/`7` Coppia coniugata/non coniugata senza figli, senza isolati (couple, no children, no extra members); `8`/`9` Coppia coniugata/non coniugata con figli, senza isolati (couple + children, no extra members); `10`/`11`/`14` Monogenitore maschio celibe/separato-divorziato/vedovo, senza isolati (single father, by marital status); `15`/`16`/`19` Monogenitore femmina nubile/separata-divorziata/vedova, senza isolati (single mother, by marital status); `20`/`21` Coppia senza figli, con isolati (couple, no children, + extra members); `22`/`23` Coppia con figli, con isolati; `24`/`25`/`28` Monogenitore maschio, con isolati; `29`/`30`/`33` Monogenitore femmina, con isolati; `34`-`36` Binucleare (two nuclei), senza isolati; `37`-`39` Binucleare, con isolati; `40` Tre o più nuclei (three-plus nuclei) | TRACC-IND row 16; CLS-var16. **Not previously carried.** See F-IT-16 for the rejected alternative `tipnu2` |
| **economic status** | `newcondm` | `Individui.txt` | TRACC-IND row 23 | person | "condizione unica o prevalente" (single or prevailing condition). `1` Occupato (employed); `2` In cerca di occupazione (seeking employment); `4` Casalinga (homemaker); `5` Studente (student); `7` Persona ritirata dal lavoro (retired); `8` In altra condizione o inabile al lavoro (other condition / unable to work) | TRACC-IND row 23; CLS-var23. **Not previously carried.** 🔴 codes `3` and `6` do not appear in the code list — the code space is not contiguous, and no code is invented to fill the gap |
| **day type** | `gsett` | `DiarioGiornaliero.txt` | TRACC-DG row 6 | diary-day (one value per diary) | "giorno di rilevazione aggregato in giorno feriale, sabato e domenica" (survey day, aggregated into weekday, Saturday, Sunday). `1` Lunedì-venerdì (Mon-Fri); `2` Sabato (Saturday); `3` Domenica (Sunday) | TRACC-DG row 6; CLS-var6. **Not previously carried.** 🔴 **Delivered pre-banded to exactly three categories — Italy binds the day-type proposal to this three-way split (D-S2-18 Rule 2)** |
| **season** | `meseri` | `DiarioGiornaliero.txt` (also `Individui.txt`, TRACC-IND row 5) | TRACC-DG row 3 | diary-day | "trimestre di rilevazione" (survey quarter). `1` Novembre, Dicembre, Gennaio; `2` Febbraio, Marzo, Aprile; `3` Maggio, Giugno, Luglio; `4` Agosto, Settembre, Ottobre | TRACC-DG row 3; CLS-var3. Already carried as `meseri`. 🔴 **These are not calendar quarters** — each band is offset one month from Spain's `TRIM` (Jan-Mar/Apr-Jun/Jul-Sep/Oct-Dec). See F-IT-17 |

---

## ROW-LEVEL MISSINGNESS, MEASURED DIRECTLY

| Field | Blank count | Denominator | Prevalence |
|---|---|---|---|
| `claseta2` | 0 | 44,866 persons | 0.0 % |
| `sesso` | 0 | 44,866 persons | 0.0 % |
| `tipfa2m` | 0 | 44,866 persons | 0.0 % |
| `newcondm` | **6,067** | 44,866 persons | **13.5 %** |
| `gsett` | 0 | 1,077,657 episodes (across 41,229 respondent-diaries) | 0.0 % |
| `meseri` | 0 | 1,077,657 episodes | 0.0 % |

🔴 **`newcondm`'s 13.5 % blank rate is the largest measured `unknown` prevalence of any
country/stratum pair found in this round** — see `strata_proposal.md` for the cross-country
comparison the task instructs be reported to the manager.

---

## 🔴 FINDINGS

### F-IT-15 — `tipfa2m` is confirmed household-grain; `tipnu2` is not, and is rejected as the household-type source

Measured directly against all 44,866 `Individui.txt` rows, grouped by `profam` (19,093 households):
`tipfa2m` takes exactly one distinct value per household in **all 19,093** cases, 0 exceptions —
it is a genuine household-level field, matching what "household type" is asked to carry. `tipnu2`
("tipo di nucleo", TRACC-IND row 13, five broad categories) was considered as a coarser
alternative, since its five categories are closer in count to Spain's eight and the UK's eight, but
measured the same way: **742 of 19,093 households (3.9 %) carry more than one distinct `tipnu2`
value** — a household can contain more than one family nucleus (e.g. a couple plus a separately
counted grandparent), and `tipnu2` is scoped to the nucleus, not the household. Using `tipnu2` as
the household-type stratum would silently mix a nucleus-grain field into a stratum the task
specifies at household grain. `tipfa2m` is used instead, at the cost of a much larger source
category count (F-IT-16 addresses that cost).

### F-IT-16 — `tipfa2m`'s 40 categories are far finer than Spain's 8 or the UK's 8, and none of them carries Spain's or the UK's child-age cutoff

Spain's `TIPOHOG` and the UK's `dhhtype` both split "couple with children" by whether any child is
below an age threshold (Spain: 25; UK: 15). `tipfa2m`'s own labels ("con figli" / "senza figli")
carry **no age qualifier on "figli" anywhere in the code list** — a couple with a 30-year-old
child still living at home and a couple with a 3-year-old are both "coppia … con figli" in Italy's
scheme. Per D-S2-18 Rule 2, a target band that splits households by child age **cannot be produced
from `tipfa2m`** and would be wrong if built anyway. This is carried into `strata_proposal.md` as
the reason the proposed household-type band set does not distinguish child age, even though two of
the three countries could support that distinction on their own.

### F-IT-17 — Italy's season quarters are offset one month from Spain's, and neither nests inside the other

`meseri`'s four bands (Nov-Jan / Feb-Apr / May-Jul / Aug-Oct) share no common boundary with
Spain's `TRIM` (Jan-Mar / Apr-Jun / Jul-Sep / Oct-Dec): every `meseri` boundary falls in the middle
of a `TRIM` quarter and vice versa. Since Spain carries no finer season signal than `TRIM`
(F-ES-9) and Italy carries no finer signal than `meseri` (both are delivered pre-banded, and
Italy binds per Rule 2), **no season band set finer than "the whole fieldwork year" is
simultaneously expressible in both deliveries.** This is the central finding carried into
`strata_proposal.md`'s season section, and it is reported there as a case for the manager rather
than resolved here.

### F-IT-18 — `newcondm`'s missing codes `3` and `6` are a genuine gap in the published list, not a transcription error

CLS-var23 lists codes `1, 2, 4, 5, 7, 8` only; `3` and `6` do not appear, and the delivered file
contains no values other than those six plus blank. Recorded so a later reader does not treat the
gap as evidence of a missed row in this transcription.

---

## WHAT IS **NOT** ESTABLISHED HERE

* Whether `tipfa2m`'s 40 categories should collapse to a 5-6-band scheme for cross-national
  harmonisation, and exactly how, is `strata_proposal.md`'s question — this document only
  transcribes the source and states why `tipnu2` was rejected.
* Whether the 13.5 % `newcondm` gap is missing-at-random or structurally concentrated (by age band,
  by region, or by household type) was not investigated — only the aggregate rate was measured.
* Nothing here builds `crosswalk_strata.csv` or touches the reader.

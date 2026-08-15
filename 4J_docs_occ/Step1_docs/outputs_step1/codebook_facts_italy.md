# Codebook facts — Italy, ISTAT *Multiscopo sulle famiglie: Uso del Tempo* 2013-2014

### Step 1, work item 1.2. Every fact below names the document and page (or HTML file) it came from.
#### Compiled 2026-08-15 from the delivery itself. No fact here comes from the employee prompt's
#### own orientation numbers, from Spain's reader, or from memory of time-use surveys generally.

Sources, all copied on 2026-08-15 from
`4J_docs_occ\Datasets\IT TUS\` into `_local_runs\4J\raw\italy\`, hashed before unpacking:

* **ZIP** — `uso_tempo_2013_IT.zip`, unpacked to `_local_runs\4J\raw\italy\unpacked\`. Contains
  `MICRODATI\` (three tab-delimited `.txt` files with a header row) and `METADATI\` (record
  layouts, code lists, questionnaires, methodology note, all as `.html`/`.pdf`).
* **README** — `!Leggimi.html`, top of the unpacked archive. Cited as README.
* **TRACC-DG** — `METADATI\uso_tempo_Tracciato_Anno 2013_DiarioGiornaliero.html`, the daily-diary
  record layout. Cited as TRACC-DG, row N (`num. ordine`).
* **TRACC-IND** — `METADATI\uso_tempo_Tracciato_Anno 2013_Individui.html`, the individual file
  layout. Cited as TRACC-IND, row N.
* **CLS-var*N*** — `METADATI\Classificazioni\uso_tempo_Classificazione_Anno 2013_DiarioGiornaliero_varN.html`
  or `..._Individui_varN.html`, one code list per categorical variable. Cited as CLS-varN.
* **HELP** — `METADATI\HelpTracciato_DELIMITED.html`. Cited as HELP.
* **METH** — `Nota_metodologica-2013.pdf` (identical, md5-for-md5, to the copy the zip carries at
  `METADATI\uso_tempo_NotaMetodologicaIndagine_Anno 2013.pdf`). 38 pages **as delivered**; its own
  internal page numbers jump from printed p.26 to printed p.95 — printed pp.27-94 are not present
  in this delivery (see the finding below). Cited as METH p. N, the PDF's **own** printed page
  number, not the PDF reader's page index.
* **QUEST-DG** — `METADATI\uso_tempo_Questionario_Diario_Giornaliero__Anno 2013.pdf`, the diary
  instrument as fielded. Cited as QUEST-DG p. N.
* **DESCR-IND** — `METADATI\uso_tempo_DescrizioneFile_Individuo__Anno 2013.pdf`, ISTAT's own
  description of the disclosure-control treatment applied to this release. Cited as DESCR-IND p. N.

A fact that could not be found in any of these is written `NOT FOUND` and stays that way.

---

## 🔴 Encoding, verified before anything was transcribed

All `METADATI\*.html` files were checked, not assumed. `HELP` declares `charset=windows-1252`
explicitly in its own `<meta>` tag; the two `Tracciato` HTML files carry accented characters
(`attività`, `età`) that fail to decode as UTF-8 and decode cleanly as `cp1252`. **All HTML
metadata files in this delivery are `cp1252`, confirmed both by the declared charset and by
round-trip decode testing, not assumed either way.** The two `MICRODATI\*.txt` files were read the
same way (`encoding="cp1252"`), and reading `catpri` label text with `cp1252` reproduces `attività`,
`università` etc. correctly where UTF-8 does not.

---

## THE REQUIRED FACTS

| Fact | Value | Where it came from |
|---|---|---|
| **File shape** | **Two flat, tab-delimited text files with a header row**: `uso_tempo_Microdati_Anno_2013_DiarioGiornaliero.txt` (one row per **episode**) and `uso_tempo_Microdati_Anno_2013_Individui.txt` (one row per person). Joined on `profam`+`proind`. A third file, `uso_tempo_Microdati_Anno_2013_DiarioSettimanale.txt` (weekly work-schedule diary), is delivered but not an input to this pipeline (see below). **No fixed-width layout, no relational household file separate from `Individui`** — Italy is not Spain's eight-file relational design | README (field-separator statement); measured: first line of each `.txt` is the variable-name header |
| **Native `START` / `DURATION`?** | **`START` yes, natively, as clock hour/minute. `DURATION` no — computed.** `ordepi` (episode number), `oraini`/`minini` (start hour/minute), `orafin`/`minfin` (end hour/minute) are delivered per episode, already collapsed by the respondent/coder — **no slot reconstruction is needed or permitted.** `duration_min` must be computed from the four clock fields, with an explicit wrap: for every diary exactly one episode (measured: 41,229 of 41,229) has `orafin*60+minfin < oraini*60+minini` in naive clock terms, and adding 1440 minutes to that one episode alone makes every diary sum to exactly 1440 with zero exceptions | TRACC-DG rows 7-11 (field definitions); measured directly from `DiarioGiornaliero.txt` |
| **Weight variables** | `coefin` ("coefficiente di riporto all'universo individuale") and `coefi2` ("coefficiente di riporto all'universo del diario giornaliero"), **both in `Individui` only** — 🔴 **`DiarioGiornaliero` and `DiarioSettimanale` carry no weight column at all.** Each is a 12-character zero-padded numeric string, 4 implied decimal digits (`Formato Campo = num.`, `Num. decimali = 4`, `Separatore decimali = virtuale`), so `weight = int(raw) / 1e4` | TRACC-IND rows 18-19; field widths and lengths measured directly from `Individui.txt` (all 44,866 rows exactly 12 characters for both fields) |
| **Activity coding list, edition** | ISTAT's own national activity list for *Uso del Tempo* 2013, nested to three digits (`catpri`, primary activity). No Eurostat HETUS ACL edition year is printed anywhere in this delivery — establishing cross-national comparability to the Eurostat ACL is explicitly **out of scope for this step** (validation doc, "what this step does not cover") | CLS-var12 (list itself); TRACC-DG row 12 (field definition, links to CLS-var12) |
| **Activity coding list, depth** | **Primary (`catpri`): 3 digits, nested under 10 one-digit major groups and 33 two-digit subgroups.** The leaf-code list contains **145 three-digit codes plus one genuine 2-digit leaf code, `90`** ("SPOSTAMENTI SENZA FINALITÀ") — **146 leaf codes total**, and the data field uses all 146 exactly (see finding F-IT-5). **Secondary (`catcon`): 2 digits, 34 modalities**, a flat list with no nesting, and it is a **different, coarser classification from `catpri`**, not a truncation of it (finding F-IT-3) | CLS-var12 (146 leaf rows: 145 of length 3, 1 of length 2); CLS-var13 (34 rows, all length 2); measured against `DiarioGiornaliero.txt` — both lists match the observed alphabet exactly, code for code |
| **Location coding list** | `cluogo`, 2 digits, **53 declared codes** (`11`-`45`, `49`-`63`, `97`-`99`); **52 of the 53 are observed** in the delivered file (`97` is declared but never used) | CLS-var14 (53 rows); measured against `DiarioGiornaliero.txt` |
| **Co-presence fields** | **Eight**: `daso` (alone), `cmadre` (with mother), `cpadre` (with father), `cconiu` (with spouse), `cfigli` (with children), `cfrate` (with siblings), `afacon` (with other cohabiting family), `aperco` (with other people known to the respondent). 🔴 **Not declared as `Categorica` in the Tracciato** (no code list exists for them) and their value domain was established by direct inspection, not by a stated rule: each field takes **exactly two values across the whole file** — a single blank space (not present) or **the field's own fixed ordinal as a string** (`daso`→`"1"`, `cmadre`→`"2"`, `cpadre`→`"3"`, `cconiu`→`"4"`, `cfigli`→`"5"`, `cfrate`→`"6"`, `afacon`→`"7"`, `aperco`→`"8"`) — see finding F-IT-4 | TRACC-DG rows 15-22 (names and 1-character widths only, `TipoVariabile = "-"`, no linked classification file); domain measured directly from `DiarioGiornaliero.txt` (`df[c].unique()` for each of the 8 columns) |
| **Slot length** | **None — there is no fixed slot.** Episodes carry native minute-resolution start/end times. (The questionnaire *asks* respondents to log activity in 10-minute steps as a recording convenience, and every measured duration in the delivered file is in fact a multiple of 10 — see G1.3 — but nothing in the file format imposes a slot) | QUEST-DG p.2 ("indichi le attività ... ad intervalli di tempo di 10 minuti"); measured: 0 of 1,077,657 episode durations are non-multiples of 10 |
| **Diary origin hour** | **04:00.** "Il diario inizia alle 4.00 del mattino e copre l'arco delle 24 ore" | QUEST-DG p.2 |
| **Minimum age** | **3 years**, not Spain's 10. "Diario giornaliero del componente familiare... (persone di 3 anni e più)"; children aged 3-10 may have the diary filled in by a parent (proxy) rather than self-completed | QUEST-DG p.1 item 5, p.2 ("sarà compito di un adulto della famiglia compilare il diario per i bambini da 3 a 10 anni") |
| **Diary days per respondent** | **1.** Measured: every `profam`+`proind` pair in `DiarioGiornaliero` has exactly one distinct `gsett` (day-type) and exactly one distinct `meseri` (quarter); episode numbering `ordepi` runs `1..N` with no gaps for every respondent, 0 exceptions | Measured from `DiarioGiornaliero.txt`, 41,229 respondents; consistent with METH p.8 (each sampled family assigned one day-type to diary) |
| **Collection mode** | **PAPI (Paper and Pencil Interview)** — paper questionnaire and paper diaries, self-completed by the respondent, **except children aged 3-10, whom a parent completes the diary for** (age-conditioned proxy, not present in Spain's design) | METH p.8-9 ("tecnica Papi"; "ogni componente di tre anni e più deve compilare personalmente... per i bambini da 3 a 10 anni il diario può essere compilato da un genitore") |

---

## COUNTS AS ISTAT STATES THEM, AND AS WE MEASURED THEM

🔴 **Contrary to what this task's own prompt assumed ("if no delivered document states the counts,
`G1.1` is `NOT CHECKED`"), ISTAT does print its own record counts, in `!Leggimi.html`** — a document
neither the manager's orientation inspection nor the task prompt's drafting apparently opened this
closely. This is recorded as a finding (F-IT-7) precisely because the prompt told us to notice if we
disagreed with a number in it.

| File | ISTAT states (README, "Totale record") | We measured | |
|---|---|---|---|
| `DiarioGiornaliero.txt` (episodes) | 1,077,657 | 1,077,657 | ✅ |
| `DiarioSettimanale.txt` (not read) | 105,770 | 105,770 | ✅ (measured for completeness only; file not used downstream) |
| `Individui.txt` (persons) | 44,866 | 44,866 | ✅ |

Two further counts, not in the README but printed elsewhere in the delivery and independently
reconciled:

| Quantity | ISTAT states | We measured | |
|---|---|---|---|
| Sampled households ("FAMIGLIE Campione", Italia row) | 19,093 (METH p.8, Prospetto 1) | 19,093 distinct `profam` in `Individui.txt` | ✅ |
| Sampled individuals ("INDIVIDUI Campione", Italia row) | 44,866 (METH p.8, Prospetto 1) | 44,866 (= README's `Individui.txt` record count) | ✅ |

Not stated anywhere in the delivery, and not substituted with our own count as a reference (that
would be exactly the circularity that retired `G1.7b`'s predecessor `G1.7`): **the number of diary
respondents** (people who actually filled a daily diary, as opposed to all sampled household
members). We measured 41,229 distinct `profam`+`proind` pairs in `DiarioGiornaliero.txt`, which
reconciles exactly against `Individui.txt` two independent ways — 44,866 − 41,229 = 3,637, and
3,637 is also exactly the count of `Individui` rows whose `coefi2` (diary weight) is blank — but
this reconciliation is *our own arithmetic*, not an ISTAT-stated figure, and is not used as a gate
reference.

---

## 🔴 FINDINGS

### F-IT-1 — this delivery is ISTAT's **public-use file** (mIcro.STAT), not the mFR

`Nota_metodologica.pdf` (the 2023 volunteering module, excluded per the work order) describes
itself as *"File di microdati per la ricerca"* (mFR). **This 2013-14 diary release is a different
and more restricted product**: both `Nota_metodologica-2013.pdf` (cover page) and
`uso_tempo_DescrizioneFile_Individuo__Anno 2013.pdf` (cover page and p.3) state explicitly *"File
ad uso pubblico — mIcro.STAT"*. DESCR-IND p.3 explains the distinction directly: mIcro.STAT files
are downloadable without registration; the mFR ("Microdata File for Research") has **higher
informational content** and requires *"richiesta motivata e previa autorizzazione del Presidente
dell'Istituto"* (a justified request and prior authorisation from ISTAT's President). **The 2013-14
diary is the open, lower-content mIcro.STAT product, not the mFR.** This resolves work item
0.4/1.1's licence question from the delivery's own documentation, and it matters beyond Step 1:
Step 5's release decision needs to know this file was never under an mFR agreement.

### F-IT-2 — this public-use file has statistical disclosure control applied, including injected missingness

DESCR-IND p.4 and p.10 state the protection measures applied to prepare this release:
**suppression** of direct identifiers and of several indirect identifiers (province, comune, region
of residence; dwelling-size class; occupational position; three health-sensitive variables under
D.Lgs. 30/06/03) in the `Individui` file, and suppression of **all territorial-reference variables**
in both `DiarioGiornaliero` and `DiarioSettimanale`; **recoding** of several categorical/quantitative
variables into coarser classes (including age → `claseta2`'s 11 bands, which is why no exact age
variable exists in this delivery at all); and — 🔴 the part with the most consequence for gate
design — *"Sono stati inseriti alcuni valori mancanti in corrispondenza di una o più variabili"*
(some values were deliberately **set to missing** as a further protection measure), with ISTAT's
own caveat printed immediately after: *"A causa delle misure di protezione adottate si possono
verificare scostamenti rispetto ai dati pubblicati dall'Istat"* — deviations from ISTAT's own
published figures may occur **because of** these protection measures. This bears directly on
`G1.8` (TASK 3.7): even setting aside the calibration circularity established in F-IT-9, ISTAT
itself warns in writing that this specific extract need not reproduce its own published
tabulations exactly.

### F-IT-3 — `catcon` is a genuinely separate, coarser classification from `catpri`

`catpri` (primary activity) is 3 digits, 146 leaf codes. `catcon` (secondary/simultaneous activity)
is 2 digits, 34 modalities, and is **not** a truncation or subset of `catpri`'s codes — e.g. `catcon`
code `60` ("Esercizio fisico e attività all'aperto") has no corresponding `catpri` 2-digit prefix
group with that meaning; the two lists were transcribed from two separate classification files
(CLS-var12 vs CLS-var13) with materially different label sets. **`act2_raw` must be validated
against `catcon`'s own transcribed list (`crosswalk_source_italy_activity2.csv`), never against
`catpri`'s.** What Step 2 does with two non-nested activity classifications for the same episode is
the manager's decision, not this employee's, per the work order.

### F-IT-4 — co-presence field values are not binary flags; they are blank-or-own-ordinal, and the domain was established empirically, not from a stated rule

The eight co-presence fields (`daso`…`aperco`) are not declared `Categorica` in TRACC-DG and carry
no linked classification file — unlike Spain's `SOLO`/`PAREJA`/etc., which INE's layout workbook
explicitly lists as `1`/`6` yes/no. Measured directly from all 1,077,657 rows of
`DiarioGiornaliero.txt`: each of the eight fields takes **exactly two distinct values** — a single
blank space, or the field's **own** fixed position number in the header order (`daso`→`1` … through
`aperco`→`8`). Presence is therefore `(value != " ")`; the value itself, when present, is redundant
with which column it is in. **This is functionally binary, but it is not documented as such
anywhere in the delivery** — it was established by inspecting the raw file, which is exactly the
kind of thing TASK 1's own framing warns must come from ISTAT's documentation "rather than from a
report." Recorded transparently because this fact came from the data, not a codebook table. Per the
work order: Italy separates *mother* and *father* where Spain has one `PADRES` flag — that is a
real difference and it is the manager's to harmonise at Step 2, not folded into anything here.

### F-IT-5 — `catpri`'s classification mixes a 2-digit leaf code into the 3-character field, as a trailing space

CLS-var12 lists 188 rows total: 10 one-digit major-group headers, 33 two-digit subgroup headers, and
**145 three-digit leaf codes** — but also **one genuine 2-digit leaf code, `90`** ("SPOSTAMENTI SENZA
FINALITÀ", travel without a stated purpose), which is a real, usable code, not a header. In the
3-character-wide `catpri` data field this leaf appears as `"90 "` — two digits and a **trailing
space**, never zero-padded to `"090"`. Measured: 166 of 1,077,657 episodes carry this value. **A
membership test that does not right-strip `catpri` before comparison will either fail those 166
rows against a 145-entry list, or require the crosswalk to carry a padded `"90 "` entry instead of
`"90"`.** `crosswalk_source_italy_activity.csv` stores it as `"90"` (146th leaf row); the reader and
gate runner both right-strip `catpri` before any comparison, applied identically in both places, and
this is stated in both reports per the work order's requirement. `catpri` and `cluogo` are never
blank on any of the 1,077,657 episodes (every episode has a primary activity and a location); this
2-digit-leaf padding is the only irregularity in either field.

### F-IT-6 — `HelpTracciato_DELIMITED.html` does not state a blank-field convention for this survey's variables; the convention was established empirically

The work order describes HELP as "the document that tells you what a blank field means." Having
read it first, as instructed: **it does not.** HELP is a generic explanation of the *columns of the
Tracciato table itself* (`Num. ordine`, `Lunghezza`, `Nome campo`, `Tipo variabile`, `Note`, etc.),
illustrated with one worked, fictitious example variable (`turnmar`) whose own `Note` column happens
to say *". : missing"*. It states that **if** a variable's `Note` column carries such a statement,
that is what a special value means for **that** variable — it is not a blanket rule. In the actual
`DiarioGiornaliero` and `Individui` Tracciato tables, **the `Note` column is empty (`&nbsp;`) for
every variable this task reads** (`catcon`, the eight co-presence fields, `causi`, `catpri`,
`cluogo`). So no ISTAT-stated missing/blank convention exists in this delivery for the fields that
matter here. The three-state convention actually used — `pd.NA` never occurs because every field
this task reads is fielded on every row; "recorded and blank" is a literal run of ASCII space
characters matching the field's declared width (`catcon` = `"  "`, co-presence = `" "`, `causi` =
`"  "`) — was established by **direct inspection of the raw delimited file**, not read off a stated
rule in HELP. This is recorded as a point where the work order's characterisation of a source
document did not match what the document actually contains, per the instruction to write such
things down rather than silently work around them.

### F-IT-7 — ISTAT's own README states record counts; `G1.1` is a live, scored gate, not `NOT CHECKED`

See "Counts as ISTAT states them" above. `!Leggimi.html` prints a table headed *"Totale record"* for
each of the three delivered microdata files, and all three reconcile exactly against direct
measurement. Because Italy's daily-diary file is delivered as native episodes (one row = one
episode, no slot reconstruction), README's `DiarioGiornaliero.txt` count (1,077,657) **is** the
episode-row count `G1.1`'s specification asks for — more directly than Spain's implementation, which
reconciled *diary* rows (one row per person in `DIARIO1`) because INE's slot-level file is not
itself the episode grain. `G1.1` for Italy therefore checks: emitted episode-table row count equals
1,077,657.

### F-IT-8 — weights live in one file only; `G1.7c` is `NOT CHECKED` for Italy

`coefin` and `coefi2` exist only in `Individui.txt`. `DiarioGiornaliero.txt` and
`DiarioSettimanale.txt` carry no weight field of any kind (confirmed against both files' full
column lists). There is no cross-file restatement of either weight to check bit-identity against.
Per the validation document's own text, this makes `G1.7c` **`NOT CHECKED`, printed, never a
pass** — the condition named for the exemption ("a country whose delivery carries weights in only
one file") is exactly Italy's case.

### F-IT-9 — ISTAT's weighting is calibrated to sex × age-class population totals, same circularity family as Spain

METH p.12 (section 5, "La metodologia di calcolo dei pesi campionari") states that Italy's
calibration estimator forces sample-weighted totals to equal **32 known regional totals**, of which
**18 are the regional population distribution by sex and nine age classes** — *"(i) alla
distribuzione della popolazione regionale per sesso e nove classi di età (18 totali)"* — using a
truncated-log-distance constrained estimator (ReGenesees software), directly analogous in structure
to INE's CALMAR-based step 4 for Spain. Two consequences, both established from this primary text
rather than assumed from Spain's precedent, per the work order's explicit instruction:

* **`G1.7b` (weighted population total vs. a published population) is circular for Italy for the
  same reason it was for Spain.** Summing the sex × age-class cells the weights are calibrated to
  reproduces the national population total, so any weighted total computed from this file and
  compared against a total consistent with those same calibration constraints cannot fail.
  `G1.7b` is **`NOT CHECKED`, permanently, printed**, citing METH p.12.
* **`G1.8` (age × sex marginals) targets exactly the variable the weights are calibrated to.** If a
  reference table existed, `G1.8` would need the same narrowing given Spain's `G1.8` row in the
  validation document ("detects only a subsample presented as the full file, not a wrong weight") —
  but see F-IT-10: no such reference table exists in this delivery at all, which is a **separate**
  reason `G1.8` cannot run, stated distinctly below.

### F-IT-10 — no published Italian age × sex population table for this wave exists in the delivery; `G1.8` is `NOT CHECKED` for lack of a reference, additionally to F-IT-9

`Nota_metodologica-2013.pdf` is **itself an incomplete excerpt** of ISTAT's full document: its own
printed page numbers run 1-26, then jump directly to 95 — printed pages 27-94 are simply not present
in the 38-page PDF this task was given. The pages that *are* present after the jump (`Prospetto
6.A`-`7.D`, printed pp.95-102) are **unweighted sample counts** ("Numerosità campionarie") broken
down by day-type and respondent characteristics — not weighted population figures, and not a table
this task could use as `G1.8`'s independent reference even if the calibration circularity in F-IT-9
did not already limit what such a check could prove. No other delivered document (the Tracciato
files, the classification lists, the questionnaires, or `DESCR-IND`) contains a population-by-age-
and-sex table for 2013-14. Per the work order, this is not searched for online. **`G1.8` is
`NOT CHECKED` for Italy** — printed, and for a different, additional reason from Spain's narrowing:
here there is no delivered reference at all to run the (already-narrowed) check against.

### F-IT-11 — minimum age is 3, not 10, and part of the "self-completion" population is parent-proxy

QUEST-DG states the diary is for *"persone di 3 anni e più"* (people aged 3 and over), with children
aged 3-10 permitted a parent-proxy completion rather than self-completion. Confirmed against
`Individui.txt`: age band `claseta2 = "01"` ("fino a 2 anni") has `coefi2` (diary weight) blank on
**all** 1,100 rows in that band — i.e. nobody under 3 has a diary weight, which is exactly what a
3-year cutoff predicts. This is a genuine difference from Spain (minimum age 10, uniformly
self-completed) and from the plan's evident assumption that the four waves are collection-mode
homogeneous; it is recorded here as a fact, not acted on.

### F-IT-12 — `coefin` is constant within household despite being named "individual"

TRACC-IND row 18 names `coefin` *"coefficiente di riporto all'universo individuale"*
(individual-universe weight), but measured directly: **0 of 19,093 households have more than one
distinct `coefin` value among their members.** This is not a contradiction — METH p.10 separately
describes a *"peso familiare, uguale per tutti i componenti di ciascuna famiglia"* (household
weight, equal for every household member) alongside the day-type-specific individual weight, and
`coefin`'s behaviour matches the household weight's description exactly even though its Tracciato
label says "individuale." Recorded because a reader that asserted "more than one distinct value
within household" as an integrity check on `coefin` would be wrong to do so; `G1.7a`'s
distinct-value check (TASK 3, more-than-one-value-overall) is unaffected — there are 19,093 distinct
household-level values across 41,229 respondents.

### F-IT-13 — the diary/`Individui` join is measured clean, 0 unmatched

All 41,229 distinct `profam`+`proind` pairs appearing in `DiarioGiornaliero.txt` are present in
`Individui.txt` with a non-blank `coefi2`; `Individui.txt` has no duplicate `profam`+`proind` keys;
the 3,637 `Individui` rows that are *not* diary respondents are exactly the complement
(44,866 − 41,229 = 3,637) and their `coefi2` is blank for every one of them. Measured directly
before the reader was written, so the reader's join-failure path (TASK 2: "report the unmatched
count and do not drop the rows silently") is expected to report zero, and does.

### F-IT-14 — `uso_tempo_2013_IT.zip` archive vs. the two excluded 2023-wave files

`Nota_metodologica.pdf` (7 pp., the 2023 volunteering module) and `UsoTempo_2023_IT.zip` were
present in `4J_docs_occ\Datasets\IT TUS\`, copied into `_local_runs\4J\raw\italy\` alongside the
2013-14 pair for the record, **and not unpacked, not read, and not used for any fact above.**
`UsoTempo_2023_IT.zip` contains only `UsoTempo_Microdati_Anno_2023_Volontariato` per its own
filename (not opened to confirm further, per the work order's explicit instruction not to). Decision
4/6 fixes one wave per country (2013-14 for Italy); these two files are the later wave's
volunteering module, not a time-use diary, and are excluded on that basis alone.

---

## WHAT IS **NOT** ESTABLISHED HERE

* The Eurostat HETUS ACL edition/year for `catpri`/`catcon` is not printed anywhere in this
  delivery. Cross-national comparability of the activity lists is Step 2's problem, not this step's.
* Whether Italy's 146+34 activity codes, or its 53 location codes, mean the same thing wave-to-wave
  or country-to-country is not established here — only that the delivered file stays inside the
  list ISTAT itself published (`G1.4`'s actual claim, per the validation document's own boundary
  statement).
* `DiarioSettimanale.txt` was not read beyond confirming its own header and ISTAT-stated row count
  (105,770); it carries no weight column and is not an input to any step in this pipeline, the same
  way Spain's `HTR1`/`HTR2`/`SD` were recorded as not read.
* Whether this 2013-14 Italian extract is the same wave and the same extract as any Italian file
  held from paper 1 is **not established here** — no paper-1 Italian extract was found on this
  workstation to compare against (see the acquisition manifest fragment), and per the work order
  this was not searched for further.
* Nothing here says whether Italy is comparable to the other three countries. That is Step 2.

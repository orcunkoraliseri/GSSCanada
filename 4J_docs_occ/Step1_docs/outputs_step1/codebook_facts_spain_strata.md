# Codebook facts — Spain, strata addendum (M-8 / D-S2-18)

### Step 1, contract change M-8-a. The six conditioning-strata sources, transcribed from the
### delivery's own documentation. Extends `codebook_facts_spain.md`, does not replace it.
#### Compiled 2026-08-17 from the delivery itself: `DISEnOS DE REGISTRO EET 2009 2010.xlsx`
#### (LAYOUT) and the fixed-width files it describes. **No source here is taken from `RL02`,
#### `RL17`, or from Italy's or the UK's codebook.**

Same two sources as `codebook_facts_spain.md`:

* **LAYOUT** — `DISEnOS DE REGISTRO EET 2009 2010.xlsx`. Cited as LAYOUT, sheet, row (the
  worksheet's own row number, 1-indexed as read).
* Field widths cross-checked against the SAS input macros shipped alongside the fixed-width data
  (`Descripción DHOGAR.txt`, `Descripción MHOGAR.txt`, `Descripción DIARIO2.txt`), which restate
  LAYOUT's own column positions. Cited as MACRO.

Row-level population counts below were measured directly from `DHOGAR.TXT`, `MHOGAR.TXT` and
`DIARIO2.TXT` at `_local_runs/4J/raw/spain/unpacked/`, the same files `4thJ_read_spain.py` reads.

A stratum that could not be found in the delivery is written `NOT FOUND` and stays that way. None
of the six was NOT FOUND for Spain.

---

## THE SIX STRATA

| Stratum | Variable | File | Position | Grain | Value list (delivery's own labels) | Citation |
|---|---|---|---|---|---|---|
| **age** | `EDAD` | `MHOGAR` | cols 15-17 | person (household member) | `000`-`110`, exact single years, **not banded** | LAYOUT, sheet *F MHOGAR*, row 18; MACRO `Descripción MHOGAR.txt` line 7. Already carried in Step 1's Spain parquet |
| **sex** | `SEXO` | `MHOGAR` | col 8 | person | `1` = Varón (male); `6` = Mujer (female) | LAYOUT, sheet *F MHOGAR*, rows 11-13; MACRO line 4. Already carried |
| **household type** | `TIPOHOG` | `DHOGAR` | col 9 | **household** | `1` Hogar unipersonal (one-person household); `2` Pareja sola (couple alone, no children); `3` Pareja con algún hijo menor de 25 años (couple, some child <25); `4` Pareja con todos los hijos mayores de 25 años (couple, all children ≥25); `5` Padre o madre solo, con algún hijo menor de 25 (single parent, child <25); `6` Padre o madre solo, con todos los hijos mayores de 25 (single parent, all children ≥25); `7` Pareja, padre o madre solo con hijo menor de 25 y otras personas viviendo en hogar (couple/single-parent + child <25 + other persons, complex); `8` Otro tipo de hogar (other) | LAYOUT, sheet *F DHOGAR*, rows 35-43; MACRO `Descripción DHOGAR.txt` line 4. **Not previously carried in any Step 1 parquet** |
| **economic status** | `HRELACTIV` | `MHOGAR` | col 18 | person | `1` Ocupado/a (employed); `2` Parado/a (unemployed); `3` Estudiante (student); `4` Jubilado/a, prejubilado/a (retired/pre-retired); `5` Cobrando pensión de incapacidad permanente o invalidez (permanent-incapacity pension); `6` Cobrando pensión de viudedad u orfandad (widow/orphan pension); `7` Realizando tareas de voluntariado social (social volunteering); `8` Realizando tareas del hogar (homemaker); `9` Otra situación de inactividad (other inactivity) | LAYOUT, sheet *F MHOGAR*, rows 19-28; MACRO line 8. Already carried |
| **day type** | `DDIASEM` | `DIARIO2` | col 9 | diary-day (one value per diary, repeated on all 144 slots) | `1` Lunes (Monday) … `7` Domingo (Sunday) | LAYOUT, sheet *F DIARIO2*, rows 14-21; MACRO `Descripción DIARIO2.txt` line 5. **Not previously carried.** See F-ES-8 below — do not confuse with `D_TIPODIA` |
| **season** | `TRIM` | `DIARIO2` | col 8 | diary-day | `1` 1er trimestre (2010, Jan-Mar); `2` 2º trimestre (2010, Apr-Jun); `3` 3er trimestre (2010, Jul-Sep); `4` 4º trimestre (2009, Oct-Dec) — standard calendar quarters, fieldwork straddles the 2009/2010 boundary | LAYOUT, sheet *F DIARIO2*, rows 9-13; MACRO line 4. Already carried as `trim` |

---

## ROW-LEVEL MISSINGNESS, MEASURED DIRECTLY

Measured from `DHOGAR.TXT` (9,541 rows), `MHOGAR.TXT` (25,895 rows) and `DIARIO2.TXT` (2,778,480
rows), at the exact column offsets LAYOUT declares.

| Field | Blank / sentinel count | Denominator | Prevalence |
|---|---|---|---|
| `TIPOHOG` | 0 | 9,541 households | 0.0 % |
| `SEXO` | 0 | 25,895 members | 0.0 % |
| `HRELACTIV` | 0 | 25,895 members | 0.0 % |
| `EDAD` | 0 | 25,895 members | 0.0 % |
| `DDIASEM` | 0 | 2,778,480 slots | 0.0 % |
| `TRIM` | 0 | 2,778,480 slots | 0.0 % |

**Spain fields all six strata on every record.** No `unknown` band is populated from Spain for
any of the six strata, on present measurement.

---

## 🔴 FINDINGS

### F-ES-8 — `D_TIPODIA` is a different variable from the day-type stratum, and it is not the one used

`DIARIO1` carries `D_TIPODIA` (col 12, LAYOUT sheet *F DIARIO1* row 27), labelled *"¿Cómo
considera que ha sido este día?"* ("How do you consider this day was?"), with values `1` Habitual
(usual) / `6` Inusual (unusual). This is the respondent's own subjective rating of the diary day,
**not** a weekday/Saturday/Sunday classification. The day-type stratum is `DDIASEM` in `DIARIO2`
(day of the week the diary was completed), established above. Recorded because the two variable
names are easy to confuse and only one of them answers "what kind of day the diary covers."

### F-ES-9 — Spain ships no finer season signal than the quarter

No file in this delivery carries a month or exact date for the diary. `D_CUMPLI_D` (`DIARIO1`,
cols 10-11, LAYOUT sheet *F DIARIO1* row 19) is labelled *"Días más tarde del de referencia"*
("days later than the reference day") — an offset from an assigned reference date, not a calendar
month. `TRIM` (quarter) is therefore the finest season granularity this delivery can supply. This
bears directly on the season proposal in `strata_proposal.md`: Spain cannot be re-binned to match
a finer or differently-bounded season classification than its own four quarters.

### F-ES-10 — household type is a household-grain field, not a diary-grain field

`TIPOHOG` lives in `DHOGAR` (one row per `IDHOGAR`, 9,541 rows), not in `DIARIO2` or `DIARIO1`.
Carrying it into the episode record therefore requires the household join Step 1's current reader
does not perform (M-8-b / D-S2-18). Recorded here because it is the reason B1's household-file
join is real work, not a formality — no prior round has read `DHOGAR.TXT` at all.

---

## WHAT IS **NOT** ESTABLISHED HERE

* Whether `TIPOHOG`'s eight categories are the right target harmonisation set, or need coarsening
  against Italy's and the UK's own household-type fields, is `strata_proposal.md`'s question, not
  this document's.
* Whether `HRELACTIV`'s nine categories collapse cleanly against Italy's `newcondm` (six) and the
  UK's `deconact` (eleven substantive codes) is likewise the proposal's question.
* Nothing here builds `crosswalk_strata.csv` or touches the reader. Per D-S2-18 Rule 3 and this
  task's Task A/Task B split, that is explicitly out of scope for this document.

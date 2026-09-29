# Validation plan — Step 1 (WP0 inventory)

### 5J occupancy-aware surrogate. Main doc: `5thJ_01_wp0Inventory.md`

Written 2026-09-28. A check counts only after it has been seen failing (section 7).

---

## Goal

Before Step 2 designs the campaign, make sure every inventory fact was read from disk, matches the 4J
record or is flagged, and never came from a UK data file.

## Section 1 — Completeness

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 1.1 | Items A to F each have an entry in `wp0_inventory.md` | 6/6 | FAIL |
| 1.2 | Every fact carries its source (a command with its output, or `file:line`) | 100 % | FAIL |
| 1.3 | `wp0_inventory.json` holds the same paths as the markdown (script diff) | 0 differences | FAIL |

## Section 2 — HETUS files (Spain, Italy)

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 2.1 | Each raw file listed with size and md5 | all | FAIL |
| 2.2 | Row counts equal the 4J Step 1 record (gate reports, parse reports) | equal | FAIL on mismatch, recorded as a finding; nothing is "fixed" |
| 2.3 | The 4J parsed episodes (Spain, Italy) found and their row counts equal the 4J record | equal | FAIL |

## Section 3 — UK compliance

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 3.1 | No UK data file appears as opened in the employee's command log (grep the transcript summary and the impl doc for `uk`, `UK-TUS`, `8128`, `episodes_uk` next to `cat`, `head`, `read`, `open`, `md5`, `wc`) | 0 hits | FAIL, and the author is told |
| 3.2 | UK entry is the author's pasted line or `WAITING ON AUTHOR` | one of the two | FAIL |

## Section 4 — Tools

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 4.1 | Each named 4J tool exists at the stated path, and each quoted signature matches `grep -n "^def "` | all | FAIL |
| 4.2 | Diary origin hour per country and the midnight rotation are quoted from code (lesson 1) | both | FAIL |
| 4.3 | IDF builder: list of variable parameters (argument names) and hard-coded ones | present | FAIL |
| 4.4 | Output meters requested by the 4J IDF builder listed (lesson 9 needs them) | present | FAIL |
| 4.5 | Time per annual run quoted with its source line | present | WARN if absent (Step 2 pilot measures it anyway) |

## Section 5 — Weather and runner

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 5.1 | EPW files per country listed with city and year | at least one per country | FAIL |
| 5.2 | Runner entry point, EnergyPlus version string and binary path quoted | present | FAIL |
| 5.3 | One working directory per run: quoted line that sets `cwd` | present, or flagged | WARN |

## Section 6 — Manager re-derivation (one number per item, by the manager, not the employee)

* A: one Spain row count (`wc -l` of one raw text file) against the inventory.
* B: one Spain schedule file opened; its length and one daily sum computed.
* C: one Spain archetype IDF opened; one U-value or window share read against the inventory.
* D: one EPW header read (city, source, year).
* E: the EnergyPlus version line in one 4J Spain run's `eplusout.err` or equivalent.

Each result goes in the impl doc under `## Verified (manager)`.

## Section 7 — Seen failing

* 1.3: add one fake path to a scratch copy of the JSON; the diff must report it.
* 2.2: compare against a row count off by one; the check must say FAIL.
* 3.1: plant a line `head episodes_uk.parquet` in a scratch copy of the log; the grep must hit.

## Section 8 — What this does not check

Whether the 4J tools give correct physics (4J Steps 7 to 10 did that; their open findings are listed,
not re-opened). Whether the UK files are intact (only the author can check that under clause 5).

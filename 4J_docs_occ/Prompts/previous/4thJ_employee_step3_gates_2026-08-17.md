# Employee task — Step 3 validation: sixteen gates, twenty-one perturbations, `V3.a` to `V3.i`

🔴 **Revised 2026-08-17 (night, close).** The val doc gained `G3.15` and `G3.16`, six perturbations and
`V3.i`; `G3.5`'s band was re-based and `G3.7` went from nine prefix fields to eight. Last, D-S3-9 closed
on the explicit activity code **`000`**, which added `G3.16 (c)`, brought `000` into `G3.4`'s scope and
added the Spain-only loader-drop row. 🔴 **Then D-S3-10 raised `G3.5`'s max from 1024 to 1200.** **Read
the val doc as it stands now** — any count or threshold you remember from an earlier version is stale.

🔴 **The corpus you are auditing already exists.** Speed job **1255620** emitted
`/speed-scratch/o_iseri/4J_step3_corpus.jsonl` — **73,254 records**, 100 % exact round-trip, loader
accounting clean, all nine explicit-code counts matching. **That is the build's own self-report and it
is exactly what you are here to check independently.** Do not treat any number in it as established;
your battery re-derives them from `harmonised.parquet` and the corpus text. 🔴 **In particular, `G3.5`
is expected to PASS at max 1191 against the new 1200 — and if your measurement disagrees with 1191,
say so and do not reconcile it to the build's figure.**

**Role: employee.** You build the battery that audits Step 3. You do not design gates, you do not
choose thresholds, and 🔴 **you never move a threshold or adjust a perturbation because something
fails.** A gate that fails is a result. `DID NOT FIRE` is reported as `DID NOT FIRE`.

🔴 **You did not write the encoder, and you must not import it.** Another employee built
`encoder.py` and `decoder.py`. That separation is the point of this round.

**Governing spec:** `4J_docs_occ/Step3_docs/4thJ_03_serialisation_val.md` — gate table, perturbation
table and vacuity guards **verbatim**. Read `4thJ_03_serialisation.md` for the record format, D-S3-1
and 3.2-bis.

---

## 🔴 CLUSTER RULES

* **`sbatch` only.** Never a blocking `srun`, never bare python on the login node, not even a
  one-liner. Every job `-t 7-00:00:00`, partition `ps`, CPU only.
* tcsh login shell: no `2>&1` in ssh commands, no bash `while ... done` loops, **one `sacct` call, not
  a poll loop.**
* 🔴 **Submit through a shipped `.sh` launcher, never a hand-rolled `sbatch --wrap`.** Copy
  `/speed-scratch/o_iseri/4thJ_null_structure_setup_and_run.sh` and change the job name, the
  `--output` path and the script it calls. **The venv is `ENVDIR=/speed-scratch/o_iseri/envs/4j_tok`**
  — pandas, pyarrow and transformers. `envs/step4` has **no transformers** and two jobs in this family
  died against it in two seconds, having exercised nothing.
* 🔴 **`pd.NA`, not `NaN`.** `loc_class`, `act2` and the six `cop_*` flags are pandas nullable dtypes.
  `isinstance(x, float) and pd.isna(x)` **misses `pd.NA` and crashes**; `pd.NA == ""` returns `pd.NA`,
  whose truth value raises. Use `pd.isna(x)` alone, **before** any `==`. Four failed jobs, two sites,
  this exact data.

## 🔴 NO PARKING — you never wait for a job

Submit with `sbatch`, write the JobID into your implementation doc, and **end your turn** saying "job
N submitted, state written to `<path>`". **No background polls, no sleeps, no no-op command to hold
the turn open, no "waiting for the notification".** The manager watches the queue and spawns a fresh
agent to collect the result. Waiting is the most expensive thing you can do: every wake re-sends your
whole transcript and produces nothing.

**Your state goes to disk as it happens**, in `Step3_docs/impl/2026-08-17_step3-gates.md` — create it
first, before any job:

```
# Step 3 battery — implementation state
Task doc:   4J_docs_occ/Prompts/4thJ_employee_step3_gates_2026-08-17.md
Status:     IN PROGRESS | BLOCKED | DONE
## Ledger        <- one line per job: JobID · what · state · exit · output path (append-only, failures kept)
## Verified      <- numbers actually read, and where from
## Decisions     <- what this task doc did not decide, and what you assumed
## Next          <- the exact next action, written so a cold agent can start there
## WHAT I DID NOT VERIFY
```

Nothing of value may exist only in your context. Never read a multi-MB file into it — `wc -l`,
`grep -n`, `tail -c`, `head`. Past roughly 150k tokens, stop, write state, and say a handoff is needed.

---

## WHAT YOU BUILD

`tools/4thJ_gates_step3.py` — **sixteen gates, twenty-one perturbations, nine vacuity guards, one
coverage clause.** One script, arguments at minimum
`--corpus <jsonl> --harmonised <parquet> --crosswalks <dir> --out <dir>` and `--perturbation <name>`
with `baseline` as a **named value, not a default**.

Take `G3.1` through `G3.16` exactly as the val doc's table states them, each with its pre-registered
threshold and its `derived` / `project-chosen` / `measured` basis. **Do not paraphrase a threshold from
memory; read the row and implement that row.**

**The record format you are auditing** is `<8-field prefix> | DUR,ACT,ACT2,LOC,COP … <eor>`, with
`ACT2` **empty** when absent, `LOC` one of **five** classes including `unknown`, and `COP` a decimal
integer in **0-64** where `64` means "co-presence not collected". Three thresholds in the val doc are
**hard per-country counts**, not shape checks — `unknown` = **0 / 8,007 / 16,793** (ES / IT / UK),
`COP == 64` = **0 / 0 / 68,464**, and the loader must read **2,024,068 rows in 73,254 diaries**.

### 🔴 The two gates whose two sides must not share an ancestor

`G3.1` to `G3.12` all read the encoder's output through the decoder we wrote. **If the encoder and the
decoder share a wrong assumption, every one of them passes.** Internal consistency is not
verification.

* **`G3.13` — independent re-derivation.** Take 500 random serialised records, parse them with a
  **separately written, minimal parser that imports nothing from `encoder.py` or `decoder.py`**, and
  reconstruct the per-diary Level-1 time budget. Compare against the same quantity computed directly
  from `harmonised.parquet`. Threshold: **agreement to < 1 minute per diary per category.** 🔴 **Do not
  refactor it to import the shared module for convenience** — that silently reduces it to `G3.1`.
* **`G3.14 (b)` — bit-order fidelity.** Per country and per flag, the count of episodes with that bit
  set, **decoded using `crosswalk_copresence.csv`'s `bit_position` column**, equals the count in
  `harmonised.parquet`. Discrepancy: **0**. 🔴 **Read the bit order from the crosswalk. A gate that
  takes it from `encoder.py` is auditing the encoder against itself.** The same refactoring ban
  applies verbatim.

* 🔴 **`G3.15 (b)` and `G3.16` — reconciliation against the parquet on disk.** These read
  `harmonised.parquet` **fresh, per country**, and compare counts against the corpus. **They are the
  only gates in this step that can see a record which was never offered to the encoder at all.**
  `G3.1` audits the encoder against the decoder over whatever the **loader** handed them; if the loader
  drops rows or a column, corpus and frame agree and `G3.1` passes — **a loader-level defect is
  invisible to it by construction.** This is not hypothetical: `4thJ_cop_reverify.py` dropped 8,873
  diaries from its own sample, and the only reason anyone knows is that it printed the count. 🔴 **Do
  not source these counts from the corpus, from the encoder, or from any document — read the parquet.**

**M-7 sub-clause attribution applies to `G3.14`, `G3.15` and `G3.16`:** the report says which clause
fell, not merely that the gate did — for `G3.14`, **(a)** range and spelling or **(b)** bit order; for
`G3.15`, **(a)** field alphabet or **(b)** count; for `G3.16`, **(a)** `LOC`/`unknown`, **(b)**
`COP == 64` or **(c)** `ACT == 000`.

### The perturbations

All twenty-one rows, on **copies** in your own output directory, never on the shipped corpus. Each must
break **exactly one** gate unless its row says otherwise; the "must stay clean" column is part of the
test. These rows carry their own reasoning and are the ones to get right:

* **Merge two adjacent episodes, summing their durations** — `G3.2` must stay **clean** (the sum is
  preserved) and **`G3.1` must fail.** 🔴 That is the case that shows why `G3.2` alone is insufficient.
* **Reverse the bit order in the encoder AND the decoder together, leaving `crosswalk_copresence.csv`
  untouched** — **`G3.14 (b)`** falls and **`G3.1` must stay clean.** Encoder and decoder agree
  perfectly and mean something else. This is the symmetric-defect class.
* **Swap in a tokenizer with a different vocabulary** — moves `G3.3`, `G3.4` and `G3.12` together. 🔴
  **It is deliberately a multi-gate row, scored for coverage only. It cannot attribute**, and a
  perturbation that moves three gates tells you nothing about which one caught the defect. Score it as
  such and say so.
* 🔴 **Inject one 150-episode diary** (durations still summing to 1440) — `G3.5` at the **upper** end,
  `G3.2` clean. **It is 150 and not 60, and the reason is a warning about your own battery.** The row
  used to read 60 episodes, calibrated against the band before last. When `G3.5` was re-based, a
  60-episode diary — roughly 685 tokens at ~11 tokens/episode — fell **comfortably inside** the new
  max, and one diary cannot move a median or a p99 across 73,254 records. **The perturbation would
  have run, passed, and reported a green `G3.5` that was never made to fall.** 🔴 **If any other
  perturbation turns out to be slack against a threshold, report it — do not quietly strengthen it.**
  🔴 **`G3.5`'s max has since moved a second time, to `≤ 1200`** (D-S3-10, author's override, after
  the emitted corpus measured max 1191). The 150-episode row was re-checked against 1200 before you
  were handed this — roughly 1,650-1,950 tokens plus prefix and `<eor>`, so it still fires with about
  40 % margin — and **it stays at 150. Do not raise it, and do not lower it.**
* 🔴 **The five loader-level rows** — drop the `act2` column for Italy only; drop Italy's 3,388
  null-`loc_class` diaries; drop the UK's 9,298 null-`cop_*` diaries; drop **Spain's 2,306 null-`act`
  diaries**; and the `unknown` / `UNKNOWN` double spelling. **`G3.1` must stay clean under all of
  them**, which is the assertion that proves the point above rather than asserting it. Note the val
  doc's one declared exception: dropping the UK's null-`cop_*` diaries **also** fells `G3.16 (a)`,
  because 4,804 rows are null in both fields — that row **cannot attribute** and is scored for
  coverage on (a). 🔴 **The Spain row is the opposite case and that is why it is Spain:** it fells
  `G3.16 (c)` alone, with **(a)** and **(b)** both staying clean, because Spain has zero null
  `loc_class` and zero null `cop_*`. It is the one country where that clause can be exercised by
  itself.
* 🔴 **Fill the absent `ACT2` slot with `'98'` in the encoder AND the decoder together** — `G3.15 (a)`
  falls, **`G3.1` stays clean.** The symmetric-defect class again: the two agree, and the corpus is
  simply 50 tokens per diary more expensive than the decision that admitted `ACT2` at 13.
* 🔴 **Null perturbation: change nothing. It must move nothing.**

### The vacuity guards, `V3.a` to `V3.i`

All nine as the val doc states them. Five carry the load:

* **`V3.a`** — FAIL if the runner read fewer records than `token_stats.md` says exist. **A battery that
  scans a subset it chose itself is a vacuous gate one level up.**
* **`V3.c`** — any character in the corpus outside the declared alphabet is **printed and refused**.
  🔴 **The alphabet is digits, comma, semicolon, lowercase `a-z`, underscore, the prefix delimiters and
  `<eor>` — letters included, because `LOC` is a string.** **No whitespace is in it**, and that is what
  makes `G3.15 (a)`'s "truly empty, never a space" clause checkable. The guard's earlier wording listed
  digits only and would have refused the corpus on its first `at_home`; the tempting repair at that
  moment is to widen the alphabet to whatever the corpus contains, which is a guard rewritten by the
  artefact it guards. **Implement the corrected alphabet; do not widen it further for anything.**
* **`V3.i`** — 🔴 **the loader prints, per country, rows and diaries read and rows and diaries dropped
  for any reason, BEFORE any gate runs, and FAILs if it dropped any.** Expected: **446,547 / 1,010,140
  / 567,381** rows and **19,140 / 38,260 / 15,854** diaries, totalling **2,024,068** and **73,254**.
  `G3.15 (b)` and `G3.16` catch a drop after the fact; this refuses one up front. **A battery that
  silently chooses its own subset is `V3.a` one level up.**
* **`V3.e`** — `G3.14` **FAILs, rather than skipping**, if `crosswalk_copresence.csv` is missing, has
  no `bit_position` column, carries fewer than six flag rows, or its positions are not exactly
  `{0,...,5}`. 🔴 **A gate whose reference file is absent has not passed. It has not run.**
* **`V3.g`** — 🔴 **lowercase `country` on read, and every join to a Step 2 crosswalk FAILs unless it
  matched** — non-zero distinct matched keys per country. This exists because of a real near-miss:
  `harmonised.parquet` holds `ES`/`UK`/`IT` and every crosswalk holds `es`/`uk`/`it`, and an
  un-normalised join would have returned **zero rows per country and passed every gate vacuously.**
  It would have looked exactly like a clean result.
* **`V3.h`** — `G3.7` counts the prefix fields the corpus **actually ships**, against the frozen field
  list, not against a remembered number. 🔴 **The prefix is EIGHT fields for every country** —
  D-S2-19 dropped `season`, and `G3.7`'s threshold followed the record format rather than the reverse.
  The guard FAILs if any record carries a field another omits. **A prefix whose width varies by country
  is a country marker**, which is the leak `G3.8` polices for co-presence.

`V3.b`, `V3.d` and `V3.f` print their tables **before any verdict**. `V3.f` in particular prints the
per-country per-flag prevalence from both sides, because **two flags with equal prevalence make a swap
between them invisible to `G3.14 (b)`** — only the printed table shows whether the gate had the
resolution to see anything.

### The coverage clause

🔴 **Cross-tab every perturbation against baseline. The probe FAILs if any gate that passes on the real
corpus was never made to fall.** Print the cross-tab. A tally that looks complete while a headline gate
was never exercised is exactly what this clause exists to catch.

---

## 🔴 ACCEPTANCE TESTS

1. All twenty-one perturbations ran, including the null one, and the null one moved **nothing**.
2. Every perturbation felled its named gate, or reported `DID NOT FIRE` with evidence.
3. No perturbation felled a gate its row lists under "must stay clean" — in particular **`G3.1` stayed
   clean under the bit-order reversal**, under the **`'98'` refill**, and under **all five loader-level
   rows**, and **`G3.2` stayed clean under the episode merge.** 🔴 **The Spain null-`act` drop felled
   `G3.16 (c)` and nothing else** — if `(a)` or `(b)` also fell, that is a finding about the loader,
   not about the row.
4. `G3.13`, `G3.14 (b)`, `G3.15 (b)` and `G3.16` import **nothing** from `encoder.py` or `decoder.py`,
   and `G3.15 (b)` / `G3.16` read `harmonised.parquet` **fresh from disk**. State how you guaranteed
   both.
5. The coverage cross-tab is printed and every passing gate was made to fall by something.
6. Every `NOT CHECKED` carries a one-line reason and stays outside the scored tally. **`NOT CHECKED`
   is never a pass.**
7. **No threshold moved, no perturbation adjusted, no gate edited.** State it in terms. 🔴 **If a
   perturbation proves slack against its threshold — as the 60-episode row did when `G3.5` was
   re-based — report it as a finding and stop. Do not strengthen it yourself.**

## DELIVERABLE

`tools/4thJ_gates_step3.py`, the gate report under your `--out` directory, and a Progress Log
**fragment** at `outputs_step3/proglog_step3_gates.md` for the manager to merge, ending with a section
headed **WHAT I DID NOT VERIFY**.

Report anything this document did not decide for you, and say plainly what you assumed.

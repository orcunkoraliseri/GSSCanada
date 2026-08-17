# Employee task — Step 2 validation: the sixteen-gate runner and its seventeen perturbations

**Role: employee.** You build the battery that audits Step 2. You do not design gates, you do not
choose thresholds, and 🔴 **you never move a threshold, widen a band, or adjust a perturbation
because something fails.** A gate that fails is a result. If a perturbation reports `DID NOT FIRE`,
**report it — do not fix it by changing the perturbation.**

**Governing spec:** `4J_docs_occ/Step2_docs/4thJ_02_harmonisation_val.md`. It carries the gate table,
the perturbation table and the vacuity guards **verbatim**. Read it in full. Read
`4thJ_02_harmonisation.md` for D-S2-2 through D-S2-13 and the D-S2-12 record contract.

---

## 🔴 CLUSTER RULES — VIOLATING THESE COSTS THE ACCOUNT

* **`sbatch` only.** Never a blocking `srun`. **Never bare `python`/`python3` on the login node, not
  even a one-liner.** Flagged three times already.
* Every job: `-t 7-00:00:00`, partition `ps`, CPU only.
* Login node allows only `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`,
  `module load`, and single-file `tail`/`head`/`grep`/`wc -l`/`cat`.
* tcsh login shell: **no `2>&1` in ssh commands**, no bash `while ... done` loops. One `sacct` call,
  not a poll loop.
* Speed interpreter `/speed-scratch/o_iseri/envs/step4/bin/python`; locally `py`.

---

## WHAT YOU BUILD

`4J_docs_occ/tools/4thJ_gates_step2.py` — **sixteen gates, seventeen perturbations, nine vacuity
guards `V2.a` through `V2.i`, one coverage clause.** One script. Arguments at minimum
`--harmonised <parquet> --crosswalks <dir> --step1 <run dir> --out <dir>` and `--perturbation <name>`
with `baseline` as a named value, not a default.

### The gates

Take `G2.1` through `G2.16` **exactly as the val doc's table states them**, including each one's
pre-registered threshold and its `derived` / `project-chosen` basis. Do not paraphrase a threshold
into code from memory; read the row and implement that row.

🔴 Four of them are the ones that carry the argument, and they are easy to implement wrongly:

* **`G2.9`** is a **floor on disagreement**, not a ceiling. It FAILs when the countries look *too
  alike*. Max pairwise difference across the three countries, on at least **3 of the 10** Level-1
  categories, must exceed **20 min/day**. Three countries give **3 pairs, not 6** — this is *harder*
  than the four-country version and the numbers stay exactly where they were pre-registered.
* **`G2.12`** rotates Spain **back** to 06:00 and must reproduce the Step 1 table exactly on `ACT`,
  `LOC` and every co-presence flag. Mismatching diaries: **0**. It is `derived` — a cyclic rotation
  is invertible by construction, so a mismatch is a bug, never a judgement call. It needs
  `episode_index_step1` and `split_at_origin` to rejoin the split halves.
* **`G2.13` and `G2.15` are opposites and both must hold.** Italy's `act2` must resolve **only**
  through `crosswalk_activity_secondary.csv` (0 codes through the primary table); Spain's and the
  UK's secondary rows must **agree** with the primary table truncated to 2 digits (0 disagreements).
  Italy is excluded from `G2.15` by construction. **A single "the secondary crosswalk is consistent"
  gate would be wrong** — it would have to pick one of these and would silently drop the other.
* **`G2.14`** counts episodes where `cop_alone` is set **and** any other shared flag is also set.
  Expected **0**. If a country's delivery genuinely permits both, that is **a finding to report
  before the gate is touched**, not a reason to relax it.

`G2.10` needs a **published national table** as its reference. 🔴 **We do not hold one.** If you
cannot cite an external published table, `G2.10` is `NOT CHECKED` with that one-line reason. **Do not
substitute a re-tabulation of our own data** — a gate whose reference derives from the source it
audits cannot fail, and reporting it as PASS would be worse than reporting it as unchecked.
**`NOT CHECKED` is never a pass**, and it stays outside the scored set.

### The seventeen perturbations

The val doc's table, all seventeen rows including 🔴 **the null perturbation, which changes nothing
and must move nothing.** Each applies to a **copy** — never to the shipped artefacts — and each must
break **exactly one** gate. The table's "must stay clean" column is part of the test, not commentary:
if a perturbation aimed at `G2.11` also fells `G2.4`, it has proved nothing about `G2.11`, and that is
a defect in the probe to report.

Report per perturbation: which gates newly failed, which stayed clean, and 🔴 **`DID NOT FIRE`
explicitly where the named gate did not fall.**

### The coverage clause

🔴 **Cross-tab every perturbation against baseline. The probe FAILs if any gate that passes on the
real data was never made to fall.** A tally that looks complete while a headline gate was never
exercised is the exact failure this clause exists to catch. Print the cross-tab.

### The vacuity guards

`V2.a` through `V2.i`, all nine, as the val doc states them. The recurring rule in `V2.d`, `V2.e`,
`V2.f` and `V2.h` is one rule and it is the most important instruction in this document:

> 🔴 **Import the shipped list; never restate it inside the validator.** The exclusion list from
> `outdoor_at_home.csv`, the four classes from `crosswalk_location.csv`, the six flags and the
> `1 = yes / 6 = no` value map and the `bit_position` set from `crosswalk_copresence.csv`, the target
> vocabulary from `activity_target_list.csv`. **A second copy drifts invisibly from the first, and a
> gate checking against a list it wrote itself out of the data it is auditing cannot fail.**

`V2.i` prints `harmonised.parquet`'s **full column list before any verdict** and FAILs on any column
name containing `origin`.

`V2.b` prints source/mapped/unmapped/one-to-many counts before any verdict.

`V2.c` prints and **refuses** any national code, unit or field name absent from
`codebook_facts_<country>.md` — never assumes it harmless.

---

## SEQUENCING — read this before you plan your work

**`harmonised.parquet` does not exist yet.** Another employee is building it right now (work item
2.4). So:

1. **Write the whole runner first.** All sixteen gates, all seventeen perturbations, all nine guards.
2. **Unit-test it against a small synthetic parquet you construct yourself** to the D-S2-12 contract —
   a few hundred episodes across three countries, hand-built so you know the right answer. 🔴 **Build
   it so that you can make each gate fail on demand**, and demonstrate that you did. A gate you have
   never seen fail is not known to work.
3. **Then message the manager (`main`) that the runner is written and unit-tested, and wait.** The
   manager will tell you when `harmonised.parquet` is ready and cleared.
4. Only then submit against the real data, by `sbatch`.

Do not modify anything under `Step2_docs/outputs_step2/` — every file there is accepted employee
work. Your perturbations operate on **copies in your own output directory**.

---

## 🔴 ACCEPTANCE TESTS

1. **All seventeen perturbations ran**, including the null one, and the null one moved **nothing**.
2. **Every perturbation felled its named gate**, or reported `DID NOT FIRE` with the evidence.
3. **No perturbation felled a gate its row lists under "must stay clean."**
4. **The coverage cross-tab is printed** and every passing gate was made to fall by something.
5. **Every `NOT CHECKED` carries a one-line reason from the spec** and is excluded from the scored
   tally. `NOT CHECKED` is never a pass.
6. **No threshold was moved and no perturbation was adjusted.** State this explicitly, or state
   exactly what you changed and why — silence here is not acceptable.

---

## DELIVERABLE

`tools/4thJ_gates_step2.py`, a gate report under your `--out` directory, and a Progress Log
**fragment** at `outputs_step2/proglog_step2_gates.md` for the manager to merge — it is not itself the
Progress Log. The fragment must contain a section headed **WHAT I DID NOT VERIFY**.

Report anything this document did not decide for you, and say plainly what you assumed.

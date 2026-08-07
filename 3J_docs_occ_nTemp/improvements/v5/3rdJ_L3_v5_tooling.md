# 3J Leg-3 — v5: a **tooling round**, and it is meant to produce no findings

**Opened 2026-08-06, on the user's instruction, immediately after v4 was worked to the end.**

**Aim.** v4 made exactly two process errors, and both were caught by hand, late, and only because
someone re-read a file. This round turns each of them into a check that fails by itself. **It adds no
result, moves no gate, touches no band, and is expected to change no number anywhere in the leg.**
That is the point: the deliverable is two falsifiers, not two findings.

**Why a round for this at all.** The v4 closure recorded the rule *"never open an item naming a prior
finding without quoting its terminal-status row"* — as prose, in a memory file. **v4 exists because
open items were prose rather than tasks.** Leaving its own lesson as prose repeats the defect one
level up.

---

## The two errors, and what each one defeated

| # | what happened | what already existed and did **not** catch it |
|---|---|---|
| **1** | Four v4 tasks were computed from `Leg3_4-split/Step9_docs/outputs_step9/` (2026-07-31) instead of the frozen `outputs_step9_deliverable/` (2026-08-06 00:05). Hotel **inverted** — 28 below the floor became 28 above the ceiling — and a correct master document was "corrected" in three places on that basis. | `bench_doc_sync_check` and every other count/band check. 🔴 **Both directories report "28 of 56."** The count held still while the failing end inverted; a check that compares counts or band values passes straight through it. |
| **2** | Two of the four decisions put to the user (`V4-B1`, `V4-B3`) were about items v2 had closed on 2026-08-05 and 2026-08-04 — one of them **already executed**, locally, without the cluster. | Nothing. Both were written in from memory files, an audit document and superseded prompts. The v2 plan's status table has an explicit terminal row for each; it was never opened. |

---

## V5-F1 — `f1_frozen_input_check.py` — the round's code must read the frozen directory

**Aim.** Fail when any script in a round names an output directory that has been superseded by a
frozen one.

**Steps.** The registry is **not hard-coded**: the frozen directories are parsed out of
`improvements/v2/V2-G1_FROZEN_DELIVERABLE.md`, and a superseded sibling is any directory sitting next
to a frozen one whose name the frozen name extends (`outputs_step9` ← `outputs_step9_deliverable`,
`agg` ← `agg_deliverable`, `campaign_local` ← `campaign_local_deliverable`). If a later round freezes a
different arm, the check follows the freeze document rather than needing an edit.

**Four checks.**

| | what it asks | why it is separate |
|---|---|---|
| **C1** | no script names a superseded sibling inside a path literal | the obvious shape |
| **C2** | no script assembles one from `join()` pieces | 🔴 **the shape that actually happened.** C1 does not see `os.path.join(S9, "outputs_step9", …)` — and when F1 was first run against the live v4 tree, **C1 passed and C2 failed** on a real line |
| **C3** | the registry is non-empty and every frozen directory exists on disk | a registry that silently came up empty passes everything |
| **C4** | every frozen directory has at least one superseded sibling | without one **C1 cannot fail**, and a check that cannot fail is a comment |

**Escape valve, with a price.** A line may opt out with a trailing `# FROZEN-INPUT-OK: <reason>`, and
the reason is required. Exactly one line in the leg uses it — `a4_split_score.py:27`, which reads the
superseded file **on purpose and never scores it**, because re-running the same scoring on the suspect
input is what converted *"my prediction failed"* into *"my input was wrong"*.

**Expected result.** `--round v4` → 4 PASS / 0 FAIL. `--falsify` → **C1 and C2 both fail** on
`fixtures/a4_split_score_AS_FIRST_WRITTEN.py`.

**Test method.** ✅ **Run 2026-08-06, both modes.** Live: 4 PASS / 0 FAIL. Falsify: 2 PASS / **2 FAIL**,
naming the two lines. Before the opt-out marker was added, the live run was **3 PASS / 1 FAIL** — the
check found a real line in the working tree on its first execution.

---

## V5-F2 — `f2_no_reopen_check.py` — a round may not open what a previous round closed

**Aim.** Fail when a task rests on a prior item that already carries a terminal status.

**Steps.** Build a registry from the status tables of every *earlier* round plan
(`improvements/v*/…_implementation.md`) — 54 rows from v2 and v3 today — marking a row terminal when
its tick cell carries ✅ or its status cell contains one of `DONE`, `DECIDED`, `CLOSED`, `WITHDRAWN`,
`EXECUTED`, `FIXED`, `ACCEPTED-AS-DOCUMENTED`, `FALSIFIED`. Then read the current round's own task
sections and check every prior ID they name. Same-round cross-references are not prior items and are
ignored.

**Four checks.**

| | what it asks | why it is separate |
|---|---|---|
| **D1** | a task naming a closed item **quotes** its terminal status | the rule as written |
| **D2** | no task in a **live** state (`open` / `ready` / `partial` / `waiting`) rests on a closed item | quoting is not noticing. A task can print the word `DONE` and still be asking what to do about it |
| **D3** | every prior ID the round names exists in some plan | citing `V2-D99` is how prose becomes a task |
| **D4** | the round names **at least one** closed prior item | otherwise D1 and D2 ran on nothing and said nothing — reported, never counted as a pass |

🔴 **D1 and D2 are evaluated independently, not chained.** The first draft used `elif`, so D2 could
only be reached when D1 passed and the fixture's D2-only case was invisible. **This is exactly the
defect `V2-G5`'s falsifier had** — one mutation testing one check twice and the other not at all — and
it reappeared here within an hour of the rule being written down. The fixture now carries `V4-D9`, a
task that *does* quote `V2-D10`'s `DONE` and is *still* open, so D2 fails on its own.

**Expected result.** `--round v4` → 4 PASS / 0 FAIL. `--falsify` → **D1 fails on `V4-B1` and `V4-B3`;
D2 fails on those two plus `V4-D9`**; the negative control `V4-A4` trips neither.

**Test method.** ✅ **Run 2026-08-06, both modes.** Live: 4 PASS / 0 FAIL over 10 tasks, 11 closed prior
items named and every one of them quoted. Falsify: 2 PASS / **2 FAIL**, naming `V4-B1 → V2-B4`,
`V4-B3 → V2-A1` and `V4-D9 → V2-D10`.

---

## V5-F3 — `f3_asset_provenance_check.py` — manuscript assets verified by CONTENT

**Added 2026-08-06 (evening), when the 3rd-journal writing task started.**

**Aim.** Fail when a figure or table copied into `writing/` carries the bytes of the **superseded**
Step-9 arm.

**Why F1 does not cover this.** F1 checks *path strings in scripts*. The writing task copies
`outputs_step9_deliverable/figures/fig_eui_4ch.png` to `writing/figures/Figure_07_eui_4ch.png` —
**after the rename there is no path string left to check.** The only thing still carrying the origin
is the bytes. F1 and F3 fail on disjoint evidence; neither subsumes the other.

**Steps.** Expected md5s are parsed from the freeze document's new *"Step-9 deliverable assets"*
section — not hard-coded — and the superseded arm's hashes are computed from disk at run time.

**Five checks.**

| | what it asks | why it is separate |
|---|---|---|
| **C1** | no manuscript asset carries superseded-arm bytes | the failure itself |
| **C2** | every scanned asset traces to *some* known arm | catches an asset that matches neither — regenerated, edited, or from a third source. Silence about an unknown file is how a stray figure ships |
| **C3** | the registry is non-empty and every hash is 32 hex chars | 🔴 **this one earned its place immediately** — see below |
| **C4** | every registered hash matches the frozen tree on disk | the freeze doc is a *claim* about the tree; if it has drifted, C1 and C2 are checking against fiction |
| **C5** | at least one registered asset is **distinguishable** between the arms, so C1 can fail — and it prints the ambiguous set | the vacuity guard, plus the honest coverage statement |

🔴 **The one file this check can never cover, stated rather than hidden.** The two arms share 11
filenames. Ten differ; **`fig_diurnal_4ch.png` is byte-identical in both.** For that file a content
check has no signal and both directories are correct answers. C5 reports it **AMBIGUOUS, never PASS** —
reporting it as PASS would claim coverage the check does not have, which is the same class of error
the check exists to catch. Its provenance has to be recorded at copy time; it cannot be recovered.

🔴 **C3 caught a fabrication in its own registry, on the first run.** The asset manifest was written
into the freeze doc from a comparison that had printed **8-character md5 prefixes** for the six tables
and full hashes only for the five figures. The remaining 24 hex characters of each table hash were
invented rather than computed. C4 would also have caught it; C3 catches it without needing the files.
All eleven hashes were recomputed from disk and replaced. **A registry is an artefact and can be wrong
in exactly the way the thing it guards can be wrong.**

**Expected result.** Live → 5 PASS / 0 FAIL, with the AMBIGUOUS file named. `--falsify` → **C1 fails**
on a superseded `fig_eui_4ch.png` copied into a temp tree under the manuscript name
`Figure_07_eui_4ch.png`, while an honest copy alongside it passes.

**Test method.** ✅ **Run 2026-08-06, both modes.** Live: 5 PASS / 0 FAIL, `fig_diurnal_4ch.png`
reported ambiguous, and the vacuity warning printed because no figures have been copied yet. Falsify:
4 PASS / **1 FAIL**, naming the renamed file and the superseded original it came from.

---

## 🔴 F1 was found FAILING on the live tree, and the failure was real

Running F1 during this work returned **3 PASS / 1 FAIL**, not the 4 PASS / 0 FAIL recorded above.

**It was not caused by the freeze-doc edit.** F1 and its result were written at 14:55–14:59; the three
offending lines are in `v4/b2_office_corrected.py`, `b2_resid_corrected.py` and
`b2_resid_two_defects.py`, written **15:39–16:15** — after F1 was validated and never re-run against.

**The hits were false positives, and they expose a real limitation in F1.** All three are *comment
lines* citing `Leg2_2-split/Step9_docs/outputs_step9/step9_eui_by_channel.csv` — Leg-2's published
source, quoted as provenance during `V4-B2`. F1's sibling matcher is **leg-blind**: it matches the
bare directory name `outputs_step9` in any path, and Leg-2's directory has no frozen counterpart at
all, so it is not superseded.

**Why the matcher was not made path-qualified instead.** Requiring the full leg-qualified path would
kill **C2** — the join-assembly case, which is *the shape that actually happened* — because
`os.path.join(S9, "outputs_step9", …)` carries no leg in the literal. Narrowing C1 would have bought a
cleaner report at the cost of the check's most valuable arm. The three lines were given the designed
`# FROZEN-INPUT-OK:` opt-out with the leg stated as the reason; F1 is back to 4 PASS / 0 FAIL and
`--falsify` still fails C1 **and** C2.

**The transferable lesson:** *a check validated once is a claim with an expiry date.* Code written
after the check passed is code the check never saw. F1 was green at 14:59 and red by 16:15, and the
round closed in between without re-running it.

---

## Fixtures are static on purpose

`fixtures/` holds the two failing cases as **frozen copies**, not pointers into the working tree:
`a4_split_score_AS_FIRST_WRITTEN.py` and `v4_plan_AS_FIRST_WRITTEN.md`. A falsifier whose fixtures are
the live tree stops falsifying the moment the tree is fixed — and this leg has already lost one that
way. Neither file is imported or executed by anything.

## What must be true at closure

- [x] All three checks run clean on the live tree (F1 and F2 on the v4 round; F3 on `writing/`).
- [x] All three are **seen failing** on a fixture reproducing the real historical error.
- [x] Every check inside each is **independently reachable** — no check is testable only when another
      one passes.
- [x] Each has an explicit vacuity guard (`C4`, `D4`) that reports when the check had nothing to say.
- [x] **No band, threshold, gate verdict or published number moved.** Nothing outside
      `improvements/v5/` was written except one opt-out comment on `a4_split_score.py:27`.

## What this round does **not** do

It does not check that the *numbers* are right — F1 checks which file was opened, F2 checks which
question was asked. **A round that reads the frozen file and still gets the arithmetic wrong passes
both.** They close the two specific holes v4 fell through, and claim nothing wider.

## Reopen trigger

- A **third** round makes the same class of error and neither check fires → the check is wrong, not
  the round.
- The freeze pointer moves to a new arm and `C3`/`C4` do not follow it → the registry parser is
  brittle and must be rewritten against the new freeze document.
- A future round plan changes its status-table format → `D3` will fire loudly on the whole registry
  rather than silently passing, which is the intended failure direction.

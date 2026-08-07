# FIXTURE — the v4 plan's two never-open tasks, as they were first written (2026-08-06)

**NOT the plan. Nothing reads this except `f2_no_reopen_check.py --falsify`.**

These are the `V4-B1` and `V4-B3` sections as they stood before the withdrawal, reduced to what the
check inspects: a live state, and a reference to a prior item that already carried a terminal status
which the task never quoted. `V4-A4` is kept alongside them as a **negative control** — it also names
prior items, none of which are closed, so it must not trip the check.

Kept static on purpose: a falsifier whose fixtures are the live tree stops falsifying the moment the
tree is fixed.

### V4-B1 — `LAUNDRY`: per-object resize, or leave the global K

**State: open · decision owed.**

Step 9 measured an elasticity of 0.334, outside its own predicted interval, and the mechanism is one
object — `LAUNDRY` is capacity-pinned. A global K is therefore the wrong instrument. The choice is
between resizing the single object and leaving the building-wide factor as the sizing basis; the
resize needs the cluster, so whichever way it goes, **execution is blocked on compute**.

Depends on: `V2-B4`.

### V4-B3 — `B-13` reaches the **submitted** 2J manuscript

**State: open · decision owed, with a hard stop.**

The `occPre × (occDensity + 1)` transform is clipped at 1.0 and is described in neither manuscript.
The paper is already with a journal, so the question is whether to measure the magnitude first or to
notify immediately. **If the magnitude is not established by 13 August the notification goes out
stating that it is unmeasured.**

Depends on: `V2-A1`.

### V4-D9 — quoting the status is not the same as noticing it

**State: open · decision owed.** *(this section exists so D2 can fail on its own)*

`V2-D10` is **DONE** — and this task is still asking what to do about it. D1 is satisfied, because the
terminal word is right there in the sentence. D2 is the check that fails: the task is alive on top of
something already finished. If D2 could only be reached when D1 passes, this case would be invisible.

### V4-A4 — Score `S9-EUI-*` under the authorised split

**State: ready · desk work only.** *(negative control — the prior items it names are not closed)*

Bound by the decision taken in `V4-A1`. Both verdicts are written down before the scoring runs, so the
result cannot quietly become whatever the scorer returns.

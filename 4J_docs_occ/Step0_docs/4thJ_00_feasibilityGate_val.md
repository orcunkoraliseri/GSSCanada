# Step 0 — Feasibility gate. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_00_feasibilityGate.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`

---

## STATUS

**✅ CLOSED 2026-08-14.** This step has no numeric gates because it produced no artefact to measure.
Its validation is of a different kind: **did the instruments that answered the four questions have a
way of returning bad news?**

That question is not rhetorical. A deep-research round that returns four clearances is
indistinguishable from a deep-research round that was written to produce four clearances, and the
project's standing rule is that **a report that agrees with something you supplied has told you
nothing.**

---

## WHAT THIS STEP MUST PROVE

That each of the four kill-switch prompts **could have ended the project**, and that at least one
actually tried to.

---

## THE VALIDATION, AS IT WAS ACTUALLY PERFORMED

| Check | What it asks | Result |
|---|---|---|
| **V0.1 — did a switch fire?** | If all four cleared, the round proves nothing about its own strictness | 🔴 **`RL10` FIRED.** The release question came back **no**, and the deliverable changed. A round in which one of four switches fires is a round with demonstrated failure capacity |
| **V0.2 — was any prompt written so that "no" was a compliant answer?** | A prompt that only accepts good news is a leading question | **Yes, `L06` explicitly.** It was written so that *"an LLM is the wrong tool"* was a compliant answer. It returned "right tool for exactly one axis", which is a partial no, and that partial no reshaped the paper |
| **V0.3 — did any report refuse to answer?** | A report that never says `NOT FOUND` is a report that invents | **Yes, and it is the most valuable line in the sixteen.** `RL13` returned `COULD NOT OPEN` for the paywalled EN 16798-1 Annex C instead of reconstructing plausible schedule values. A reconstructed standard schedule would have been undetectable downstream and would have propagated into the baseline we benchmark against |
| **V0.4 — did any report refuse a planted trap?** | The prompts contained a deliberate falsehood | **Yes.** `L04` named "Gemma 4". `RL04` refused to confirm it and enumerated what actually exists |
| **V0.5 — did independent prompts agree without seeing each other?** | Agreement between separately-run prompts is worth more than either alone | **Yes.** `RL01` and `RL16` independently concluded that the "three HETUS waves" framing is wrong and only the 2010 round exists as central microdata |
| **V0.6 — did any report catch its own error?** | Self-correction mid-report is a signal of genuine checking | **Yes.** `RL09` caught and corrected two of its own citation defects, including a Deming and Stephan DOI resolving to a different paper |

---

## 🔴 WHERE THIS VALIDATION IS WEAK, STATED RATHER THAN GLOSSED

Every check above is a check on the **round**, not on any individual answer. Three specific gaps:

1. **V0.1 is satisfied by one firing switch out of four, which is a low bar.** It shows the round can
   return bad news; it does not show that the three clearances were each independently earned.
2. **No check here reads a primary document.** Every verdict above is about report *behaviour*.
   `RL01`'s claim that Concordia is not a recognised research entity was later corroborated by
   `RL17` C1 — **but two reports agreeing is not the Office of Research answering, and it still has
   not been asked.** Recorded in the parent document's V4 table as still open.
3. 🔴 **The single most consequential Step-0 claim turned out to be false, and no Step-0 check could
   have caught it.** `RL04` stated that Llama 3.1 §1.b forbids using outputs to improve other models.
   It does not — that clause is in Llama 2 and Llama 3 and was dropped at 3.1. **It was caught in
   Step 4, four months of nominal plan-time later, by fetching Meta's licence files and reading
   them.** The lesson is recorded in the parent document as the governing rule of the whole project:
   **a report's claim to have read a document is not a reading of that document.**

---

## FALSIFICATION PROTOCOL FOR THIS STEP

There is no code to perturb. The equivalent, and it is the one that worked:

* **Re-run the question against the primary source, not the report.** Applied to the licence claim,
  this overturned it. Applied to the tokenizer claims, it overturned two more. Applied to Concordia's
  eligibility, it has not been applied at all.
* **Count the verdicts yourself from the report's own rows.** A report whose summary disagrees with
  its own table has not read its own work, and this check needs no external access.
* **Ask which claims a report could not have got wrong.** Any claim that merely restates something we
  supplied is not evidence, however confidently it is graded Tier 1 / High.

---

## WHAT THIS STEP'S VALIDATION DOES **NOT** COVER

* It does not validate any threshold. All thresholds live in Steps 1 to 9.
* It does not validate the corpus. That is Step 1.
* It does not validate any claim about a model. Every model claim from this round was later
  re-measured in Step 4, and two of them failed.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — validation recorded

* Six behavioural checks on the deep-research round, V0.1 to V0.6, all satisfied.
* Three weaknesses recorded rather than resolved. The third one — the false licence clause — was
  found later by primary-source reading and is the origin of the project's standing rule that a
  measurement is only a measurement if we ran it.

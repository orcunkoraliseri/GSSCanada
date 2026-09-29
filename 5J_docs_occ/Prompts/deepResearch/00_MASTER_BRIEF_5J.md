# 5J Deep Research: Master Brief (paste this block ahead of EVERY prompt in this folder)

Written 2026-09-28. This brief gives the shared context for the prompts in this folder (`T45`, ...).
Read it, then answer only the prompt that follows it. Do not restate this brief in your answer.

---

## 1. Who is asking

A postdoctoral building-performance researcher, sole author of this paper, working on occupancy data
for building energy modelling with EnergyPlus as the simulation engine. The subject of the paper is
fixed (section 2). The prompts in this folder ask **whether the published record has already done it,
or something close enough to change how it is framed.** They do not ask you to redesign the paper.

## 2. The paper design (fixed)

A learned stand-in (a surrogate) for EnergyPlus that predicts **hourly heating, cooling and electricity
for one dwelling over one year** from three inputs: an **occupancy and activity sequence** taken from
time-use diaries, a **building description**, and the **weather**.

* **Training data: a paired campaign.** Many EnergyPlus runs in which the building and the weather are
  held fixed and only the household's occupancy sequence changes. Diaries come from harmonised European
  time-use surveys for three countries; buildings are residential archetypes built from published
  European typology parameters; weather is reanalysis for the diary year.
* **Scored twice, against held-out EnergyPlus runs only** (no meters, no people):
  1. on the load itself (hourly error bands of the usual calibration guideline, used as a reference);
  2. on the **occupancy effect**: the difference in hourly and annual energy between two households in
     the same building and weather, compared between the surrogate and EnergyPlus.
* **An occupancy-blind control must fail.** The same model trained with occupancy shuffled across runs
  is scored the same way. If the blind control passes the occupancy-effect test, that test measures
  nothing and is withdrawn.
* **Held-out splits:** new households, new buildings, and a new country (leave one country out).
* **Baseline:** gradient-boosted trees on the same inputs; if the sequence model does not beat them,
  that is reported.
* **Purpose of speed:** stock-scale use, many occupancy draws over a district, not a single building.

## 3. What we hold

1. Time-use diaries for three European countries under national access agreements (not
   redistributable). The prompts never ask you to touch them.
2. EnergyPlus residential archetypes and a validated pipeline from diaries to EnergyPlus schedules,
   from a previous paper of the series.
3. A computing cluster with GPUs, available until late October 2026.
4. Three prior works already held in full or looked up by us (their DOIs are in the prompt). **We do not
   tell you what we found in them.** Two of them are controls: you describe them, and we compare your
   description with the full text we hold.

## 4. What is not claimed

"First building energy surrogate" is not claimed; surrogates of building simulation are an established
field. The candidate claim is narrower: **a surrogate whose input is a time-use occupancy sequence,
trained on a campaign in which only occupancy varies, and scored on the occupancy effect with a blind
control.** Your job is to find the work that already makes any part of that claim, and say which part.

## 5. Rules for every answer in this folder

* A citation is not evidence until opened. Say for each work whether you read the full text, the
  abstract only, or the title only.
* Authors are copied from the CrossRef (or DataCite, OSTI) record of that DOI, never from memory or from
  a citing paper. Give the title that `https://api.crossref.org/works/<DOI>` returned.
* No accuracy number (R2, CV(RMSE), error percentage, speed-up factor) may appear unless it is quoted
  with the page or section where you read it. A number you did not read is left out, not estimated.
* `NOT FOUND` and "this part is already done" are useful answers. Do not narrow the claim until nobody
  has done exactly that; say instead which work comes closest and what it lacks.
* Name people only as authors of a cited work, copied from its registry record. Do not suggest
  collaborators, referees or contacts.
* No em dashes and no en dashes anywhere in the output.

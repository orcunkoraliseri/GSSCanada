1. **Severity:** Critical
   **Location:** `4J_cover_letter.md`, lines 3 and 44; `[date of submission]`, `**Suggested reviewers.** [author to add]`
   **Problem:** The cover letter contains unpopulated template placeholders for submission date and suggested reviewers. An editor will immediately reject or hold the manuscript prior to review.
   **Evidence:** `4J_cover_letter.md`, line 3 has `[date of submission]` and line 44 has `**Suggested reviewers.** [author to add]`.
   **Fix:** Replace `[date of submission]` with the current date (e.g. `2026-09-23`), and provide 3 to 5 expert reviewers with their full names, institutions, and email addresses.

2. **Severity:** Critical
   **Location:** `4J_manuscript_submission.md`, Section 2, line 47; `![Figure 1](figures/HETUS_LLM_Pipeline_Steps.png)`
   **Problem:** The manuscript embeds the deprecated pipeline diagram containing internal project step numbers ("Step 0" through "Step 11") rather than the approved three-row workflow diagram.
   **Evidence:** `figures/HETUS_LLM_Pipeline_Steps.png` contains step boxes labeled "Step 0", "Step 1", ..., "Step 11", violating Section 8 of the journal author instructions ("no project step numbers, no internal codes").
   **Fix:** Replace `![Figure 1](figures/HETUS_LLM_Pipeline_Steps.png)` with `![Figure 1](figures/HETUS_LLM_Workflow_Figure1.png)`.

3. **Severity:** Major
   **Location:** `4J_manuscript_submission.md`, Section "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process", lines 751–754; `During the preparation of this work the author used Claude (Anthropic)... and Gemini (Google)...`
   **Problem:** The Generative AI declaration does not disclose the use of Gemini for generating the Figure 1 workflow image, violating Elsevier's mandatory GenAI figure policy.
   **Evidence:** Elsevier Guide for Authors (section "Generative AI and figures, images and other artwork") mandates disclosure in both the declaration and the figure caption; current text mentions Gemini only for literature searches.
   **Fix:** Add "and to generate the initial layout of the workflow diagram in Figure 1" to the declaration sentence.

4. **Severity:** Major
   **Location:** `4J_manuscript_submission.md`, Section "Acknowledgements", line 757; `[AUTHOR: add acknowledgements here if wanted...`
   **Problem:** Internal editorial instruction brackets remain in the manuscript text.
   **Evidence:** Line 757 contains `[AUTHOR: add acknowledgements here if wanted (for example data providers INE, ISTAT and the UK Data Service, or the Speed computing cluster at Concordia University); otherwise delete this section.]`.
   **Fix:** Replace bracketed prompt with a clean acknowledgement of data providers and computing resources, or remove the Acknowledgements section header.

5. **Severity:** Major
   **Location:** `4J_manuscript_submission.md`, Section "References", line 839; `Platzer, M., and Reutterer, T. (2021). Holdout-based empirical assessment of mixed-type synthetic data.`
   **Problem:** A reference is listed in the bibliography that is never cited in the body of the manuscript.
   **Evidence:** Text search across `4J_manuscript_submission.md` yields zero citations of Platzer & Reutterer (2021). E&B Guide for Authors requires all listed references to be cited in-text.
   **Fix:** Remove the entry for Platzer and Reutterer (2021) from the reference list, or insert an appropriate in-text citation in Section 1.2.

6. **Severity:** Major
   **Location:** `4J_manuscript_submission.md`, Section 1 to Appendix B; `Main text prose word count: 12,436`
   **Problem:** The length of the main text substantially exceeds the journal recommendation of approximately 20 double-spaced pages.
   **Evidence:** E&B Guide for Authors states original papers should preferably be no more than about 20 double-spaced pages including tables and figures; current manuscript has 12,436 prose words plus 44 equations.
   **Fix:** Move Appendix B (equations B.1 to B.44 and associated derivations) to the Supplementary Material, leaving a concise mathematical summary in Methods.

7. **Severity:** Minor
   **Location:** `4J_manuscript_submission.md`, Section 2, line 49; `**Figure 1.** - Workflow of the study, from survey harmonisation to building loads.`
   **Problem:** Figure 1 caption lacks the required generative-AI disclosure statement mandated by Elsevier for AI-assisted artwork.
   **Evidence:** Elsevier policy requires: "This figure was created with the assistance of a generative AI image tool (Gemini) and reviewed and edited by the author for accuracy."
   **Fix:** Append the sentence to the caption: `**Figure 1.** - Workflow of the study, from survey harmonisation to building loads. This figure was created with the assistance of a generative AI image tool (Gemini) and reviewed and edited by the author for accuracy.`

Critical: 2
Major: 4
Minor: 1
UNVERIFIED references: none

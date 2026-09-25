# Vetting record: equation sources marked [AUTHOR TO OPEN]

#### Done 2026-09-24, by opening the sources themselves (not a deep-research report).
#### Scope: the 14 items of `VETTING_RL34.md` section 4, plus Pflugradt (2016). Questions are those of `VETTING_RL34.md` section 4; claims are those of `writing/submission/IMP/prep/appendixB_equations_draft.md` and the live `writing/submission/4J_manuscript_submission.md` (Appendix B, lines 454-734; references from line 760).
#### Rule used: CONFIRMED only when the full text (or, where the question is answered by it, the abstract) was read here. Every quote below was copied from text extracted from the downloaded file, or read off a rendered page image for scanned PDFs. Nothing is filled from memory; the one point that rests on memory is labelled as such.
#### Files: downloaded to the session scratch folder `.../scratchpad/eqsrc/` (not kept in the repo). md5 given per item. Page numbers are **PDF pages of the copy used**, with the journal page where the copy is the typeset version.
#### No project file other than this one was written. The manuscript was not edited.

---

## 1. Richardson, Thomson, Infield and Clifford (2010), Section 2.7 (THE KEY ITEM)

**Reference.** Richardson, I., Thomson, M., Infield, D., Clifford, C., 2010. Domestic electricity use: A high-resolution energy demand model. Energy and Buildings 42 (10), 1878-1887. https://doi.org/10.1016/j.enbuild.2010.05.023 (Crossref re-checked today: title, 4 authors, 42(10), 1878-1887.)

**Copy opened.** Author's accepted manuscript in the Loughborough repository, CC BY-NC-ND 2.5: https://repository.lboro.ac.uk/articles/journal_contribution/Domestic_electricity_use_a_high-resolution_energy_demand_model/9573941 , file https://ndownloader.figshare.com/files/17208020 (32 PDF pages, md5 `7a84eeebd40aa38590eb9face934202c`, equals the repository's own md5). This is the accepted manuscript, not the typeset article, so journal page numbers cannot be given. Section numbers and Fig. 3 are those of this copy.

**Question.** What does Section 2.7 print for the calibration scalar: a closed form, or an iterative fit to annual energy?

**Answer.** Neither as an equation. Section 2.7 has **no numbered equation**. It says in one sentence that the scalar is **tuned against simulation output** so that annual consumption comes out right, and then derives the scalar with **closed-form arithmetic** (a worked freezer example). It gives **no iterative algorithm**: no passes, no tolerance, no bisection.

Quotes (Section 2.7 "Appliance calibration scalars", PDF p. 12):

> "Each appliance has a "calibration scalar" which is factored into the probability of switch-on as shown in Fig. 3, and thus determines the average number of times that the appliance is used in a year."

> "A calibration scalar is adjusted so that, over a very large number of stochastic simulation runs, the mean annual consumption of the appliance will be correct. That is that it will match the input data discussed earlier in section 2.3."

> "For example, the chest freezer in the model uses 271 kWh/y. It draws 190 W for 14 minutes on each operating cycle and uses no power on standby. It must therefore cycle 6116 times per year. Additionally, each 14 minute run is followed by a delay of 56 minutes during which the appliance may not start again [...]. This leaves approximately 95 000 minutes of the year when a start event can occur. Thus the mean time between start events, excluding the time when the appliance is in a cycle, is 95 000 / 6116 = 16 minutes. Since the freezer appliance is not dependent on active occupancy, its activity probability is taken as unity, and thus, referring to Fig. 3, the calibration scalar is simply 1/16 min-1."

> "A similar calculation can be performed for appliances that do depend on daily activity profiles, but it is more complex. [...] The overall mean value of an activity taking place at a time step must first be calculated. This may be achieved by using Bayes' conditional probability theorem. [...] This mean probability of an activity taking place, when multiplied by the calibration scalar, should equal the mean probability of an appliance switch-on event. The former value is determined by the same method as described above, such that the required number of cycles per year occur as required to give the correct overall energy use."

Section 2.6 "Switch-on events" (PDF p. 11) and Fig. 3 ("Switch-on events") confirm the scalar multiplies the activity probability: "Thirdly, the activity probability is multiplied by the calibration scalar."

**What this means for Eq. (4) and Eq. (B.34).**
* The freezer arithmetic is **our Eq. (4) with E = one full year**: the paper takes the minutes left after C(L+D) and divides by C. Check: 6116 x (14 + 56) = 428,120; 525,600 - 428,120 = 97,480 minutes; the paper rounds this to "approximately 95 000" and gets 1/16 per minute. Eq. (4) gives 6116 / 97,480 = 1/15.9. So Eq. (4) is the paper's closed form, moved from calendar minutes to eligible minutes.
* For activity-driven appliances the paper divides by the **mean activity probability** (the CREST form our code docstring gives). Our Eq. (4) uses eligible minutes from the diaries instead. That difference is ours, and the manuscript already says so ("Eq. (4) applies this idea to minute-level diary eligibility").
* The **target** in the paper is annual **energy** (kWh/y), turned into a cycle count by dividing by the energy per cycle. Our target is the published cycles per year. These are the same thing when the energy per cycle is fixed.
* The paper's "adjusted so that, over a very large number of stochastic simulation runs [...] will be correct" is **compatible with** checking or tuning against simulation. But the paper **does not describe** the six-pass, 2 % rescaling of Eq. (B.34). That step is ours. The manuscript does not credit it to the paper: Eq. (B.34) carries no citation, and Methods line 125 says only "follows the calibration idea of CREST".

**Verdict: CONFIRMED** for what the live manuscript attributes: "Calibrating a start probability to a published annual count follows Richardson et al. (2010, Section 2.7)" (Appendix B) and "This follows the calibration idea of CREST (Richardson et al., 2010)" (Methods). "Fig. 3" is also confirmed. **Do not** write that Richardson et al. give an iterative scheme, or print an equation number for them. Optional wording that follows the source more closely: "...to a published annual consumption, expressed as cycles per year (Richardson et al., 2010, Section 2.7)".

---

## 2. Carlini, Chien, Nasr, Song, Terzis and Tramèr (2022)

**Reference.** Membership inference attacks from first principles. 2022 IEEE Symposium on Security and Privacy (SP), 1897-1914. https://doi.org/10.1109/SP46214.2022.9833649. Crossref re-checked today: pages 1897-1914, third author "Nasr, Milad" (the `VETTING_RL34` correction holds).

**Copy opened.** arXiv:2112.03570v2 (12 Apr 2022), https://arxiv.org/pdf/2112.03570 (md5 `204e99694aa2acd03814de99d65901aa`). The author list on p. 1 matches Crossref.

**Question.** Confirm the low-FPR convention and its section.

**Quote.** Section III "Membership Inference Attacks", subsection B "Evaluating membership inference attacks", paragraph "True-Positive Rate at Low False-Positive Rates" (arXiv PDF p. 4):

> "Our recommended evaluation of membership inference attacks is thus to report an attack's true-positive rate at low false-positive rates." [...] "(2) optionally summarizing an attack's success rate by reporting its TPR at a fixed low FPR (e.g., 0.001% or 0.1%). For example, the LOSS attack achieves a TPR of 0% at an FPR of 0.1% (worse than chance)."

The abstract also says attacks should be evaluated "by computing their true-positive rate at low (e.g., ≤0.1%) false-positive rates".

**Not in the source:** how Eq. (B.28) sets its threshold (the k-th largest non-member score, k = floor(0.001 n0)) and the clause "not defined when k < 1". Both are our own conventions. Carlini et al. calibrate with **shadow models** (Section IV; and Section V-C on Watson et al.: "each example's loss is calibrated by the average loss of shadow models not trained on this example"). They do not use a pretrained base model, so Eq. (B.26) remains our own choice (as `VETTING_RL34` §1.6 said).

**Verdict: CONFIRMED** for "report TPR at a low FPR such as 0.1 %" (Section III-B). If cited, attach it to the choice of the TPR-at-0.1 % metric, not to the k < 1 rule.

---

## 3. Yeom, Giacomelli, Fredrikson and Jha (2018)

**Reference.** Privacy risk in machine learning: Analyzing the connection to overfitting. 2018 IEEE 31st Computer Security Foundations Symposium (CSF), 268-282. https://doi.org/10.1109/csf.2018.00027. Crossref re-checked today: author given names are Samuel, Irene, Matt, Somesh, so the initials S., I., M., S. are correct.

**Copy opened.** arXiv:1709.01604v5 (4 May 2018), "the unabridged version of the paper accepted for publication in CSF 2018", https://arxiv.org/pdf/1709.01604 (md5 `bc3d324cd7007468cf8cf32ae02fd237`). Page numbers below are arXiv pages, not CSF pages.

**Question.** Confirm the loss-threshold adversary and its section.

**Quotes.**
* Section 3 "Membership Inference Attacks", Experiment 1 (PDF p. 5): "3. Draw z ∼ S if b = 0, or z ∼ D if b = 1". Members are training points and non-members are fresh draws. This is the setting our held-back split stands in for.
* Section 3.2 "Membership attacks and generalization" (PDF pp. 6-7), Adversary 1 "Bounded loss function": "with probability proportional to the model's loss at the query point z, the adversary predicts that z is not in the training set." Adversary 2 is "(Threshold)", on the regression error.
* Section 6.2 "Membership inference" (PDF p. 19), applied to CNNs trained with cross-entropy: "the predictions made by these models can be compared against LS, the average training loss observed during training". Table 1 contrasts this attack, which "Makes only one query to the model", with Shokri et al., which "Must train hundreds of shadow models".

**Verdict: CONFIRMED.** The loss-based membership attack is Section 3.2 (theory) and Section 6.2 (a threshold on loss for cross-entropy models). The membership setting is Section 3, Experiment 1. Yeom et al. use a single threshold at the mean training loss, and our AUC over rank order generalises that. Do not write "superior to Shokri for LLMs" (as `VETTING_RL34` already said).

---

## 4. Hanley and McNeil (1982)

**Reference.** Hanley, J.A., McNeil, B.J., 1982. The meaning and use of the area under a receiver operating characteristic (ROC) curve. Radiology 143 (1), 29-36. https://doi.org/10.1148/radiology.143.1.7063747 (full title and initials from Crossref today).

**Copy opened.** The typeset article on the first author's McGill page, https://jhanley.biostat.mcgill.ca/software/Hanley_McNeil_Radiology_82.pdf (8 pages, md5 `7a18502823eb131ae85f456867e7177b`). The old URL `medicine.mcgill.ca/...` now returns "removed". PubMed abstract (PMID 7063747) also read.

**Question.** Confirm the AUC and Wilcoxon / Mann-Whitney equivalence.

**Quotes.**
* Abstract (p. 29; also PubMed): "the area represents the probability that a randomly chosen diseased subject is (correctly) rated or ranked with greater suspicion than a randomly chosen non-diseased subject. Moreover, this probability of a correct ranking is the same quantity that is estimated by the already well-studied nonparametric Wilcoxon statistic."
* p. 30: "this 'probability of correctly ranking a (normal, abnormal) pair' is intimately connected with the quantity calculated in the Wilcoxon or Mann-Whitney statistical test."
* Section IV "W and SE(W) Calculated without Distributional Assumptions" (p. 32): "Since the Wilcoxon statistic is based on pairwise comparisons [...]"; "The W = θ̂ = 0.893 = 89.3% derived in this way agrees exactly with the area under the ROC curve calculated by the trapezoidal rule."

**Caveat.** On the pages read (pp. 29-30, 32), the paper computes W from **pairwise comparisons** (Table II). The rank-sum form of Eq. (B.27), (R1 - n1(n1+1)/2)/(n1 n0), was not seen printed. It is the standard algebraic form of the same Mann-Whitney quantity.

**Verdict: CONFIRMED** for "AUC equals the Wilcoxon / Mann-Whitney probability of correct ranking". Cite it for the equivalence, not for the rank-sum algebra.

---

## 5. Park, Mohammadi, Gorde, Jajodia, Park and Kim (2018)

**Reference.** Park, N., Mohammadi, M., Gorde, K., Jajodia, S., Park, H., Kim, Y., 2018. Data synthesis based on generative adversarial networks. Proceedings of the VLDB Endowment 11 (10), 1071-1083. https://doi.org/10.14778/3231751.3231757 (author list and title from Crossref today).

**Copy opened.** arXiv:1806.03384, https://arxiv.org/pdf/1806.03384 (16 PDF pages, md5 `757f265274f84d8c67fa2714b4399f80`). It carries the PVLDB 11(10) camera-ready header ("PVLDB, 11 (10): 1071-1083, 2018"), so PDF page n is taken to be journal page 1070 + n. That is an inference from the header and was not checked against the typeset issue.

**Question.** Search for "NNDR" and "nearest neighbour distance ratio"; confirm the DCR section.

**Result.** Searches of the full extracted text for "NNDR", "nearest neighbo", "distance ratio": **0 hits**. DCR is **defined** in Section 5.1.2 "Evaluation Method" (PDF p. 8, i.e. p. 1078):

> "Instead, we use distance to the closest record (DCR) which means the Euclidean distance between a record r of an anonymized, perturbed, or synthesized table and the closest record to r in the original table. Note that an anonymized, perturbed, or synthesized record with DCR = 0 leaks real information."

DCR **results** are in Section 5.3.1 "Distance to the Closest Record" (PDF p. 11). `RL34` gave "Section 5.3.1, p. 1078", which **mixes the two**: the definition is 5.1.2 on p. 1078, the results are 5.3.1.

Park et al. use a Euclidean distance on normalised attributes. Our Eq. (B.30) uses the share of mismatched ten-minute slots. The DCR concept, and the rule that DCR = 0 leaks, match.

**Verdict: CONFIRMED** for DCR (definition in Section 5.1.2), and **NNDR is absent**. So Park et al. may be cited for DCR only, never for NNDR. The live manuscript cites only Platzer and Reutterer (2021) at Eq. (B.30), which needs no change.

---

## 6. Borisov, Seßler, Leemann, Pawelczyk and Kasneci (2022/2023)

**Reference in the manuscript.** Borisov, V., Seßler, K., Leemann, T., Pawelczyk, M., and Kasneci, G. (2022). Language models are realistic tabular data generators. arXiv:2210.06280.

**Copy opened.** https://arxiv.org/pdf/2210.06280 (md5 `b9510468ad131cfed2b4c9b73750f1cc`). Page 1 header: "Published as a conference paper at ICLR 2023". Author line: "Vadim Borisov, Kathrin Seßler, Tobias Leemann, Martin Pawelczyk, Gjergji Kasneci". Five authors, the same list as the manuscript and DataCite. There is no "Haug".

**Question.** Confirm the serialisation section.

**Quote.** Section 3.1 "GReaT fine-tuning", "Textual encoding", Definition 1 (PDF p. 4):

> "each sample si of the table is transformed into a textual representation ti using the following subject-predicate-object transformation: ti,j = [fj, "is", vi,j, ","] (1), ti = [ti,1, ti,2, ..., ti,m] (2)"

Random feature-order permutation follows as Definition 2 (PDF p. 5).

**Verdict: CONFIRMED.** Serialisation is Section 3.1, Definition 1, Eqs. (1)-(2). Optional: the paper was published at ICLR 2023. The arXiv 2022 citation is still correct.

---

## 7. Jordan and Vajen (2001b), Solar Energy

**Reference (Crossref today).** Jordan, U., Vajen, K., 2001. "Influence Of The DHW Load Profile On The Fractional Energy Savings:" (title cut short in Crossref), Solar Energy 69, 197-208, https://doi.org/10.1016/s0038-092x(00)00154-7. Crossref has no issue number. A web-search summary gave "69(6), 493-503", which does not match Crossref and was not used. Semantic Scholar's record for this DOI gives the full title: "Influence of the DHW-load profile on the fractional energy savings: a case study of a solar combi-system with TRNSYS simulations".

**Question.** Take the full subtitle from the paper, and confirm it describes the Task 26 tapping model.

**Tried.** ScienceDirect (HTTP 403), Unpaywall (not OA), Semantic Scholar (openAccessPdf "CLOSED"), OpenAlex (no OA location), a Kassel/author-page search (none found), ResearchGate (request-only). **No full text found.**

**Found instead.** The ETDEWEB record of the **EuroSun 2000 conference** version (https://www.osti.gov/etdeweb/biblio/20165482; "3. ISES European Solar Congress (EuroSun 2000), Copenhagen"), whose abstract says: "a more realistic profile was generated on a 1-min time scale with statistical means. Assumptions about the distribution of the DHW-consumption during the year, depending on the weekday, and the time of the day were made." This is **not** the Solar Energy article. Our Task 26 report (local copy, md5 `c7c460924ef66588649b2473b706e2b9`) cites that conference version, as "/Jordan00/ [...] Influence of the DHW-profile on the Fractional Energy Savings – A Case Study of a Solar Combisystem, in: CD-ROM of the Third ISES Europe Solar Congress EuroSun00".

**Verdict: NOT OPENED.** Whether the journal article describes the same four-category tapping model is unverified. The live manuscript does not cite it, and the Task 26 report (whose Table 1 values are already checked) is enough for Eqs. (B.39)-(B.40).

---

## 8. Deming and Stephan (1940)

**Reference (Crossref today).** Deming, W.E., Stephan, F.F., 1940. On a least squares adjustment of a sampled frequency table when the expected marginal totals are known. The Annals of Mathematical Statistics 11 (4), 427-444. https://doi.org/10.1214/aoms/1177731829

**Copy opened.** The Project Euclid open-access PDF (Semantic Scholar marks it BRONZE): https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-11/issue-4/On-a-Least-Squares-Adjustment-of-a-Sampled-Frequency-Table/10.1214/aoms/1177731829.pdf (18 pages, scanned, md5 `1d04cd9d631dd47e52fc66ab1a4c1fb7`). curl got a bot-check page, but WebFetch returned the PDF. The PDF has no text layer, so pages were rendered and **read as images**. PDF page n = journal page 426 + n.

**Question.** Confirm that it supports iterative proportional fitting onto known margins (the draft's "see also" for Eq. (B.10)) and the "depart as little as the margins allow" phrase next to Deville and Särndal.

**Quotes.**
* p. 428, the objective: "we shall minimize sums of the form (2) S = Σ(mi − ni)²/ni, ni being the observed frequency in the ith cell, and mi the calculated or adjusted frequency therein. The conditions among the mi will arise from the fact that the marginal totals, after adjustment, must agree with their expected values".
* Section 5 "A simplified procedure—iterative proportions" (pp. 439-440): "If nevertheless one were to make the simple proportionate adjustment (52) m′ij = nij(mi./ni.) along the horizontal in the ith row, the horizontal conditions (4) will be enforced but not the vertical ones [...] This error can then be diminished by turning the process around and subjecting these m′ij to a proportionate adjustment in the vertical according to the equation (53) m″ij = m′ij(m.j/m′.j) [...] The cycle initiated by eq. (52) is therefore repeated, and the process is continued until the table reproduces itself and becomes rigid with the satisfaction of all the conditions, both horizontal and vertical." (p. 440). "The same process can be extended to three or more dimensions" (p. 440).

**Caution.** The paper's objective is the **least-squares (chi-square) distance** of eq. (2), and it states that "The final results coincide with the least squares solution" (p. 440). The raking in Eq. (2) of the manuscript is the multiplicative (raking) case of Deville and Särndal, not this least-squares objective. **From memory, not checked here:** later literature (Stephan, 1942) qualified the claim that iterative proportions reach the least-squares solution. Verify that before relying on it.

**Verdict: CONFIRMED** for iterative proportional fitting onto known margins (Section 5, pp. 439-440, eqs. (52)-(53)). Cite it for the **procedure**, as the "see also" at Eq. (B.10). Do not cite it for the sense in which raking weights "depart as little as the margins allow". Deville and Särndal (1992) alone carry that sentence in the live manuscript, which is right.

---

## 9. Willmott and Matsuura (2005)

**Reference (Crossref today).** Willmott, C.J., Matsuura, K., 2005. Advantages of the mean absolute error (MAE) over the root mean square error (RMSE) in assessing average model performance. Climate Research 30, 79-82. https://doi.org/10.3354/cr030079

**Tried.** The publisher PDF https://www.int-res.com/articles/cr2005/30/c030p079.pdf (the Unpaywall "publishedVersion", free to read) returned a JavaScript bot-check page to curl and HTTP 401 to WebFetch. ADS returned a human-verification page. The **abstract** was read from the publisher landing-page text as indexed by OpenAlex (`api.openalex.org/works/doi:10.3354/cr030079`).

**Question.** It is cited next to Hyndman and Koehler (2006) for the MAE over the six groups (draft Eq. (B.2)). Does it support MAE as the measure of average error?

**Quote (abstract).** "Our findings indicate that MAE is a more natural measure of average error, and (unlike RMSE) is unambiguous. Dimensioned evaluations and inter-comparisons of average model-performance error, therefore, should be based on MAE."

**Verdict: CONFIRMED (from the abstract; the abstract answers the question).** The full text, and therefore the MAE equation as printed, was **not opened**. The live manuscript does not cite this source.

---

## 10. Vallender (1974)

**Reference (Crossref today).** Vallender, S.S., 1974. Calculation of the Wasserstein distance between probability distributions on the line. Theory of Probability and Its Applications 18 (4), 784-786. https://doi.org/10.1137/1118101

**Copy opened.** The **Russian original**, free on Math-Net.Ru: С. С. Валландер, "Вычисление расстояния по Вассерштейну между распределениями вероятностей на прямой", Теория вероятн. и ее примен., 18:4 (1973), 824-827. https://www.mathnet.ru/php/getFT.phtml?jrnid=tvp&paperid=4387&what=fullt (md5 `a131fd4a46126976f0fb3ae696661967`). The Math-Net.Ru record links it to the English translation Theory Probab. Appl. 18:4 (1974), 784-786, DOI 10.1137/1118101. **The English translation itself was not opened** (SIAM, closed).

**Question.** Confirm the statement W1 = ∫|F − G| dx and its number.

**Quote (Russian original, p. 824).** «Теорема. R(P,Q) = ∫_{−∞}^{∞} |F(x) − G(x)| dx, (2) где F и G — функции распределения (ф. р.) распределений P и Q соответственно, формула (2) справедлива независимо от конечности или бесконечности входящих в нее величин.» In English: "Theorem. R(P,Q) = ∫|F(x) − G(x)| dx (2), where F and G are the distribution functions of P and Q; formula (2) holds whether or not the quantities in it are finite." R is defined in eq. (1) as the Wasserstein distance, inf E ρ(ξ, η) over couplings.

**Verdict: CONFIRMED** (Theorem, formula (2), p. 824 of the Russian original; p. 784 of the translation by the Math-Net.Ru cross-reference). The translation's own numbering was not seen. **Placement:** the draft attaches Vallender to the sentence "Consecutive episodes [...] are not merged". It belongs on the integral identity of Eq. (B.14). The live manuscript cites only Ramdas et al. (2017) there, which needs no change.

---

## 11. Widén and Wäckelgård (2010)

**Reference (Crossref today).** Widén, J., Wäckelgård, E., 2010. A high-resolution stochastic model of domestic activity patterns and electricity demand. Applied Energy 87 (6), 1880-1892. https://doi.org/10.1016/j.apenergy.2009.11.006

**Tried.** ScienceDirect (paywall), Unpaywall and OpenAlex (no OA copy), Semantic Scholar ("CLOSED"), DiVA record diva2:359583 (metadata only, links to the DOI). **The paper's full text was not found.**

**Read instead.**
* The abstract (ETDEWEB record 21328055): "The activity-generating model, based on non-homogeneous Markov chains that are tuned to an extensive empirical time-use data set, creates a realistic spread of activities over time, down to a 1-min resolution."
* The first author's PhD thesis, which has this paper as Paper III: Widén, J., 2010. *System Studies and Simulations of Distributed Photovoltaics in Sweden*. Uppsala University. https://www.diva-portal.org/smash/get/diva2:359601/FULLTEXT01.pdf (md5 `aab50d58a10541e66265e774ae8af251`; the DiVA copy has the summary chapters only, not the appended papers). Section 3.2.2 "Estimation of transition probabilities" (PDF p. 50): "Between time steps k and k + 1, all Ns transitions si(k) to si(k + 1) are examined and the total number nij(k) of transitions between states i and j are counted. [...] pij(k) = nij(k)/ni(k) (3.23). If not all states have transitions from them in every time step, ni(k) will be zero [...] One solution is to divide the time series into intervals of a number of time steps and calculate average transition probabilities over these intervals (3.24)." Section 4.2.2 (PDF p. 63): "The stochastic approach, presented in Papers II and III, is based on a non-homogeneous Markov-chain model [...] the transition probabilities pij can be estimated from a TUD set with Equation 3.24."

**Question.** Confirm a first-order, time-inhomogeneous chain estimated from transition counts, and its section, before citing it for the Markov comparator (Eq. (B.24) live; (B.27) in the draft).

**Verdict: NOT OPENED** for the paper itself. The abstract confirms "non-homogeneous Markov chains tuned to time-use data". That is enough for the **lineage** sentence in live Methods line 121, which needs no change. The count estimator is confirmed only in the thesis, and the thesis estimator **pools counts over intervals** (Eq. 3.24) where ours falls back to the next-slot distribution. So Widén and Wäckelgård should **not** be added at Eq. (B.24) unless the paper is opened. The live manuscript cites only Richardson et al. (2008) there, which needs no change.

---

## 12. Balinski and Young (1982)

**Reference.** Balinski, M.L., Young, H.P., 1982. Fair Representation: Meeting the Ideal of One Man, One Vote. Yale University Press, New Haven. ISBN 0-300-02724-9 (978-0-300-02724-2). Creator fields and ISBN were confirmed from the Internet Archive catalogue record `fairrepresentati00bali` ("Balinski, M. L"; "Young, H. Peyton, 1945-"). Book reviews give "xi + 191 pp.".

**Tried.** The Internet Archive copy is lending-only (the text file and search-inside return 401 / "Item not available"). No publisher or author open copy was found, and the catalogue record carries no table of contents.

**Question.** Confirm the chapter on Hamilton's (largest-remainder) method.

**Verdict: NOT OPENED.** The chapter could not be confirmed. The live manuscript does not cite it: Eq. (B.12) states the rule and contrasts it with Lovelace and Ballas (2013), which is enough.

---

## 13. Montgomery, Peck and Vining (2012)

**Reference.** Introduction to Linear Regression Analysis, 5th ed. Wiley. ISBN 978-0-470-54281-1.

**Tried.** Wiley, Google Books and the instructor site (no full text). A web search found a full PDF on a third-party college website that looks like an **unauthorised copy**. **It was not downloaded or used.**

**Question.** Confirm the OLS slope and R² equation numbers.

**Verdict: NOT OPENED.** Eq. (B.21) is textbook OLS through the origin on centred data and needs no citation. The live manuscript cites none.

---

## 14a. Lowe (2004), optional

**Reference (Crossref today).** Lowe, D.G., 2004. Distinctive image features from scale-invariant keypoints. International Journal of Computer Vision 60 (2), 91-110. https://doi.org/10.1023/B:VISI.0000029664.99615.94

**Copy opened.** Author's copy, https://www.cs.ubc.ca/~lowe/papers/ijcv04.pdf ("Accepted for publication in the International Journal of Computer Vision, 2004"; dated January 5, 2004; md5 `302d6467b68aa2b8047252671643262a`). Page numbers are those of the preprint.

**Quote.** Section 7.1 "Keypoint matching" (preprint pp. 19-20): "A more effective measure is obtained by comparing the distance of the closest neighbor to that of the second-closest neighbor." [...] "we reject all matches in which the distance ratio is greater than 0.8, which eliminates 90% of the false matches while discarding less than 5% of the correct matches."

**Verdict: CONFIRMED** as the origin of the nearest-neighbour distance-ratio test (Section 7.1). It is still optional in an Energy and Buildings paper. Our threshold (0.33) and our use of it as a privacy flag are not from Lowe.

## 14b. Villani (2003), optional

**Reference.** Villani, C., 2003. Topics in Optimal Transportation. Graduate Studies in Mathematics 58, AMS. ISBN 978-0-8218-3312-4.

**Tried.** A web search found only bookseller, review and catalogue pages. It is a paid AMS book with no open copy.

**Verdict: NOT OPENED.** It is not needed: Vallender (item 10) is now confirmed for the one-dimensional identity.

---

## 15. Extra: Pflugradt (2016)

**Manuscript string (reference list).** "Pflugradt, N. (2016). *Modellierung von Wasser- und Energieverbräuchen in Haushalten*. LoadProfileGenerator."

**Copy opened.** Qucosa (Saxon State and University Library repository), https://monarch.qucosa.de/id/qucosa%3A20540 , PDF https://monarch.qucosa.de/api/qucosa%3A20540/attachment/ATT-0/ (373 PDF pages, md5 `da24dbae999049decb6841d4d7c88745`). URN: urn:nbn:de:bsz:ch1-qucosa-209036 (resolver https://nbn-resolving.org/urn:nbn:de:bsz:ch1-qucosa-209036).

**Question.** Is it a doctoral dissertation, and from which university?

**Quotes.**
* Title page (PDF p. 1): "Modellierung von Wasser- und Energieverbräuchen in Haushalten. Von der Fakultät Maschinenbau der Technischen Universität Chemnitz genehmigte Dissertation zur Erlangung des akademischen Grades Doktor-Ingenieur (Dr. Ing.) vorgelegt von Herrn Dipl.-Ing. Noah Daniel Pflugradt [...] eingereicht am 6. April 2016. Gutachter: Prof. Dr.-Ing. habil. Bernd Platzer, Prof. Dr.-Ing. habil. Volker Quaschning. Chemnitz, den 19. Juli 2016".
* Bibliographic page (PDF p. 2): "Dissertation an der Fakultät für Maschinenbau der Technischen Universität Chemnitz, Institut für Mechanik und Thermodynamik, Chemnitz, 2016".
* English abstract (PDF p. 2): "The model is based on a desire model from the field of psychology and makes it possible to avoid calculating any probabilty [sic] distributions."

**Verdict: CONFIRMED.** It is a Dr.-Ing. doctoral dissertation, Technische Universität Chemnitz, Faculty of Mechanical Engineering, 2016. The **manuscript's reference string is incomplete**: "LoadProfileGenerator" is the software, not the publisher. Suggested string: *Pflugradt, N. (2016). Modellierung von Wasser- und Energieverbräuchen in Haushalten. Doctoral dissertation (Dr.-Ing.), Technische Universität Chemnitz, Chemnitz. urn:nbn:de:bsz:ch1-qucosa-209036.* The title on the title page has the hyphen ("Wasser- und"); the repository title does not. Keep the hyphen. The live sentence calls LPG part of a "lineage of activity-based models". That holds: it simulates activities. But it is a **desire-based** model, not a Markov chain, so do not describe it as Markov anywhere.

---

## Summary

Verdicts over 16 sources (the 14 items, with item 14 split into Lowe and Villani, plus Pflugradt): **11 CONFIRMED, 0 WRONG, 5 NOT OPENED**.

| # | Source | Verdict | Where | Smallest manuscript change (equation unchanged) |
|---|---|---|---|---|
| 1 | Richardson et al. 2010 | CONFIRMED | §2.7, Fig. 3 (AAM p. 12). No numbered equation. Closed-form worked example; tuned against simulation to annual energy; no iterative scheme | None required. Never credit the 6-pass rescaling or an equation number to it. Optional: "published annual consumption, expressed as cycles per year" |
| 2 | Carlini et al. 2022 | CONFIRMED | §III-B, arXiv p. 4 | None (not cited live). If added: cite for TPR at 0.1 % FPR only; k < 1 rule and base-model reference are ours |
| 3 | Yeom et al. 2018 | CONFIRMED | §3 Exp. 1; §3.2; §6.2 (arXiv pp. 5-7, 19) | None (not cited live). May be added beside Shokri at Eq. (B.25) |
| 4 | Hanley and McNeil 1982 | CONFIRMED | Abstract; pp. 30, 32 (§IV) | None (not cited live). If added: for the AUC-Wilcoxon equivalence, not the rank-sum algebra |
| 5 | Park et al. 2018 | CONFIRMED (DCR); NNDR absent | DCR defined §5.1.2 (p. 1078); results §5.3.1 | None. Never cite for NNDR. `RL34`'s "§5.3.1, p. 1078" is a conflation |
| 6 | Borisov et al. | CONFIRMED | §3.1, Def. 1, Eqs. (1)-(2), p. 4 | None required. Optional: "ICLR 2023" as venue |
| 7 | Jordan and Vajen 2001b | NOT OPENED | Closed. Only the EuroSun 2000 conference abstract seen | Do not cite. Task 26 report (already verified) suffices |
| 8 | Deming and Stephan 1940 | CONFIRMED (IPF) | §5, pp. 439-440, eqs. (52)-(53) | None live. If added: "see also" at Eq. (B.10) for the procedure only, not for the "depart as little as" sentence |
| 9 | Willmott and Matsuura 2005 | CONFIRMED (abstract) | Abstract | None live. If added at the MAE: fine; full text not seen |
| 10 | Vallender 1974 | CONFIRMED | Theorem, formula (2), p. 824 of Russian original (= p. 784 of the translation) | None live. If added: attach to the integral in Eq. (B.14), not to the "not merged" sentence |
| 11 | Widén and Wäckelgård 2010 | NOT OPENED (paper) | Abstract: non-homogeneous Markov chains from TUD. Counts estimator only in the author's thesis, §3.2.2 | Keep the lineage citation (Methods). Do not add at Eq. (B.24) |
| 12 | Balinski and Young 1982 | NOT OPENED | Lending-only | Do not cite. Eq. (B.12) stays uncited |
| 13 | Montgomery et al. 2012 | NOT OPENED | Paid textbook; unauthorised copy not used | Do not cite. Eq. (B.21) stays uncited |
| 14a | Lowe 2004 | CONFIRMED | §7.1, preprint pp. 19-20 | Optional. Not needed |
| 14b | Villani 2003 | NOT OPENED | Paid book | Do not cite (Vallender covers it) |
| 15 | Pflugradt 2016 | CONFIRMED | Title page; p. 2 | **Fix the reference string**: replace "LoadProfileGenerator." with "Doctoral dissertation (Dr.-Ing.), Technische Universität Chemnitz, Chemnitz. urn:nbn:de:bsz:ch1-qucosa-209036." |

**Changes the live manuscript actually needs:** one, the Pflugradt reference string. Every other [AUTHOR TO OPEN] source is either not cited in the live manuscript (the NOT OPENED ones should stay out) or is cited in a way the opened text supports. The live Appendix B already drops the draft's unverified citations, and nothing found here requires putting any of them back.

## Manager check (2026-09-24)

* Pflugradt re-checked independently on the Qucosa record (dissertation, TU Chemnitz, 2016, urn:nbn:de:bsz:ch1-qucosa-209036). Reference string fixed at manuscript line 838; backup `writing/submission/previous/4J_manuscript_submission.md.pre_rl36_20260924`. Word file rebuilt (both PATCH lines printed) and copied to `EB_upload/`; "qucosa-209036" present in the uploaded XML.
* One quote in item 1 is not in the live manuscript: "Calibrating a start probability to a published annual count follows Richardson et al. (2010, Section 2.7)" (grep for "Section 2.7" returns nothing; it came from the draft). The live text says only "This follows the calibration idea of CREST (Richardson et al., 2010)" (line 125), which the opened text supports. No change.
* 0 WRONG verdicts, so nothing else to re-check. The five NOT OPENED sources are not cited in the live manuscript; none added.

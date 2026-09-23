# Appendix B draft: equations (for the manager to merge)

Draft of 2026-09-23. Scope: every quantity the Methods and Results use. Each equation was written from
the code first and checked against the line given in its bracketed line; the source only supports it.
Citation status follows `DeepResearchPrompts/VETTING_RL34.md`: ACCEPTED items are cited plainly, items
marked "accept after author opens" carry `[AUTHOR TO OPEN]`, nothing REJECTED is cited, and an equation
with no acceptable source is left uncited. No page, section or equation pointer is printed unless the
vetting file allows it. The bracketed `[Code | Source | Status]` line under each equation is merge
metadata and is deleted at merge; everything above it is the journal text. Sections (a) to (c) at the
end are merge aids, not appendix text.

---

## Appendix B. Definitions of the reported quantities

Throughout, $a$ indexes activity categories, $b$ one of the three scoreable age bands (25-44, 45-64,
65 and over), $c$ a country, and $i$ a diary. Every diary covers exactly 1,440 minutes in ten-minute
steps.

### Time budgets and the primary comparison

The level-1 time budget of a set of diaries $S$ is the weighted mean number of minutes per day spent in
each of the six HETUS level-1 aggregates,

$$B_a(S) \;=\; \frac{\sum_{i\in S} w_i \sum_{e\in i} d_e\,\mathbb{1}\!\left[\alpha(c_e)=a\right]}{\sum_{i\in S} w_i}, \qquad a\in\mathcal{A}=\{\mathrm{AC0},\mathrm{AC1\_TR},\mathrm{AC2},\mathrm{AC3},\mathrm{AC4\text{-}8},\mathrm{AC9A}\} \qquad (\mathrm{B.1})$$

where $S$ is the set of diaries in one age band, $w_i$ is the weight of diary $i$ (1 for a generated
diary, the raked weight of Eq. (B.8) for a donor diary, the calendar-re-based weight of Eq. (B.16) for a
real diary of the held-out country), $e$ runs over the episodes of diary $i$, $d_e$ is the duration of
episode $e$ in minutes, $c_e$ is its three-digit primary activity code, and $\alpha(\cdot)$ is the
crosswalk from codes to aggregates (leading digit, except that codes 995-997 and 999 map to unspecified
time outside $\mathcal{A}$, code 998 maps to AC4-8, and code 910, travel to and from work, stays in
AC9A). The published budget $B^{\mathrm{pub}}_{a}(c,b)$ is read from the Eurostat level-1 table for the
same country and band, with AC9A taken as the sum of its seven published sub-categories.

[Code: `tools/4thJ_step6_level1.py:83-101, 151-197, 228-256` | Source: none | Status: uncited]

The error of a candidate population against the published budget is the mean absolute error over the six
aggregates,

$$\mathrm{MAE}(c,b) \;=\; \frac{1}{|\mathcal{A}|}\sum_{a\in\mathcal{A}} \left|\,B_a(S_{c,b}) - B^{\mathrm{pub}}_{a}(c,b)\,\right| \qquad (\mathrm{B.2})$$

in minutes per day, where $S_{c,b}$ is the candidate's diaries in band $b$ of held-out country $c$ and
$|\mathcal{A}|=6$ (Hyndman and Koehler, 2006; Willmott and Matsuura, 2005 [AUTHOR TO OPEN]).

[Code: `tools/4thJ_step6_level1.py:335-340`; called at `tools/4thJ_step6_g61_score.py:157-161` | Source: Hyndman and Koehler 2006 (ACCEPTED); Willmott and Matsuura 2005 (AAO) | Status: cited]

The transfer margin of one cell is the baseline's error minus the model's,

$$\Delta(c,b) \;=\; \mathrm{MAE}^{\mathrm{null}}(c,b) - \mathrm{MAE}^{\mathrm{model}}(c,b), \qquad \text{the model passes the cell if and only if } \Delta(c,b) > 0 \qquad (\mathrm{B.3})$$

where $\mathrm{MAE}^{\mathrm{null}}$ is Eq. (B.2) for the raked donor diaries and
$\mathrm{MAE}^{\mathrm{model}}$ is Eq. (B.2) for the generated diaries. The inequality is strict, so a
baseline scored against itself ($\Delta=0$) does not pass. The donor pool is raked on the whole
population and restricted to the age band afterwards.

[Code: `tools/4thJ_step6_rakeddonor.py:206-222`; `tools/4thJ_step6_g61_score.py:148-169` | Source: own definition | Status: uncited]

### Percentage error and the absolute bar

Each published cell is assigned a scoring basis from its published value alone,

$$\text{cell } a \text{ is } \begin{cases} \text{a zero cell, hit if } B_a < 0.01\times 1440, & B^{\mathrm{pub}}_a < 0.5,\\ \text{a floor cell, hit if } |B_a - B^{\mathrm{pub}}_a| < 15, & 0.5 \le B^{\mathrm{pub}}_a < 10,\\ \text{scored on } \mathrm{APE}_a = 100\,|B_a - B^{\mathrm{pub}}_a|\,/\,B^{\mathrm{pub}}_a, & B^{\mathrm{pub}}_a \ge 10, \end{cases} \qquad (\mathrm{B.4})$$

with all quantities in minutes per day and $\mathrm{APE}_a$ in per cent. Percentage errors are not taken
on cells below 10 minutes per day because a small denominator makes them unstable (Hyndman and Koehler,
2006).

[Code: `tools/4thJ_step6_level1.py:112-117, 143-144, 262-304` | Source: Hyndman and Koehler 2006 (ACCEPTED) | Status: cited]

The mean absolute percentage error of one band is

$$\mathrm{MAPE}(c,b) \;=\; \frac{1}{|\mathcal{A}^{\mathrm{APE}}_{b}|}\sum_{a\in\mathcal{A}^{\mathrm{APE}}_{b}} \mathrm{APE}_a, \qquad \text{pass if } \mathrm{MAPE}(c,b)\le 15 \text{ and every zero and floor cell is a hit} \qquad (\mathrm{B.5})$$

where $\mathcal{A}^{\mathrm{APE}}_{b}$ is the set of cells scored on APE in band $b$ (Hyndman and Koehler,
2006).

[Code: `tools/4thJ_step6_level1.py:305-332` | Source: Hyndman and Koehler 2006 (ACCEPTED) | Status: cited]

For a model scored on a country it was trained on, the in-sample check takes the worst band,

$$\mathrm{MAPE}^{\mathrm{worst}} \;=\; \max_{b}\ \mathrm{MAPE}(c,b), \qquad \text{pass if } \mathrm{MAPE}^{\mathrm{worst}} \le 15 \ \text{ and }\ \mathrm{MAPE}^{\mathrm{worst}}_{\text{in}} - \mathrm{MAPE}^{\mathrm{worst}}_{\text{out}} \le 0 \qquad (\mathrm{B.6})$$

where the maximum runs over the three scoreable bands, $\mathrm{MAPE}^{\mathrm{worst}}_{\text{in}}$ is the
worst-band error of country $c$ when it is a training country, and
$\mathrm{MAPE}^{\mathrm{worst}}_{\text{out}}$ is the worst-band error of the same country when it is held
out. The worst band by MAE is reported beside it.

[Code: `tools/4thJ_step6_g66_heldin.py:74, 148-200, 203-216, 229` | Source: own definition | Status: uncited]

The three frozen limitation criteria mark a cell as failing if any one of them holds:

$$\mathrm{MAE}^{\mathrm{model}} \ge \mathrm{MAE}^{\mathrm{null}}, \quad\text{or}\quad \mathrm{MAPE} > 20, \quad\text{or}\quad \exists a:\ \left|B^{\mathrm{pub}}_a - \bar{E}_a\right| \ge 2 \ \wedge\ \operatorname{sgn}\!\left(B^{\mathrm{pub}}_a - \bar{E}_a\right) \ne \operatorname{sgn}\!\left(B_a - \bar{E}_a\right) \qquad (\mathrm{B.7})$$

where $\bar{E}_a$ is the unweighted mean of the published level-1 budgets of all HETUS countries with a
complete profile in the same band, and the 2 min/day floor excludes divergences inside the rounding of
the published table.

[Code: `tools/4thJ_step6_g65_g69.py:97-102, 135-201` | Source: own definition | Status: uncited]

### The raked donor baseline

The donor diaries of the two training countries start from unit weights, $w_i^{(0)}=1$, and are raked by
iterative proportional fitting over the five prefix variables $v\in\mathcal{V}=$ \{age band, sex,
household type, economic status, day type\}, one variable at a time:

$$\hat{p}_v(k) \;=\; \frac{\sum_i w_i\,\mathbb{1}[x_{iv}=k]}{\sum_i w_i}, \qquad w_i \;\leftarrow\; w_i\,\frac{p^{*}_v(x_{iv})}{\hat{p}_v(x_{iv})} \qquad (\mathrm{B.8})$$

where $x_{iv}$ is the category of diary $i$ on variable $v$, $\hat{p}_v(k)$ is the current weighted share
of category $k$, and $p^{*}_v(k)$ is the share of category $k$ in the held-out country's synthetic
population (Eqs. (B.13)-(B.15)), which is the fitted form of its published marginals. The resulting weights are
a calibration estimator in the sense of Deville and Särndal (1992): they depart from the starting
weights as little as the margins allow (Deville and Särndal, 1992; Deming and Stephan, 1940
[AUTHOR TO OPEN]). Weights are not integerised.

[Code: `tools/4thJ_step6_rakeddonor.py:55-63, 169-181`; targets `tools/4thJ_step6_g61_rake_folds.py:79-103` | Source: Deville and Särndal 1992 (ACCEPTED, existing wording only); Deming and Stephan 1940 (AAO) | Status: cited]

Full sweeps over $\mathcal{V}$ are repeated until

$$\max_{v\in\mathcal{V},\,k}\ 100\,\left|\hat{p}_v(k) - p^{*}_v(k)\right| \;\le\; 0.5 \qquad (\mathrm{B.9})$$

in percentage points, with at most 200 sweeps; a pool that does not converge, or a target category that
no donor carries, stops the comparison. The weights therefore approximate the raking solution to within
0.5 percentage points on every margin rather than reaching its exact optimum.

[Code: `tools/4thJ_step6_rakeddonor.py:47-48, 137-193` | Source: own tolerance | Status: uncited]

The effective sample size of the raked donor diaries in one band is

$$n_{\mathrm{eff}} \;=\; \frac{\left(\sum_{i} w_i\right)^2}{\sum_{i} w_i^2} \qquad (\mathrm{B.10})$$

where the sums run over the donor diaries in the band and $w_i$ are the weights of Eq. (B.8).

[Code: `tools/4thJ_p5_bootstrap_table3.py:86-90, 190`; `tools/4thJ_step6_g61_rake_folds.py:120-123` | Source: standard definition; no citation | Status: uncited]

### Bootstrap interval of the margin

For replicate $r=1,\dots,R$ with $R=2{,}000$, the generated diaries of each band are resampled with
replacement at their original number, and the donor pool is resampled with replacement within each donor
country at its original number, re-raked by Eqs. (B.8)-(B.9) onto the same targets, and then restricted
to the band. The replicate margin is

$$\Delta^{*}_{r}(c,b) \;=\; \mathrm{MAE}^{\mathrm{null}*}_{r}(c,b) - \mathrm{MAE}^{\mathrm{model}*}_{r}(c,b) \qquad (\mathrm{B.11})$$

where the starred errors are Eq. (B.2) on the resampled sets. Replicates whose re-raking does not
converge are excluded and counted.

[Code: `tools/4thJ_p5_bootstrap_table3.py:68, 109-114, 198-249` | Source: none vetted | Status: uncited]

The 95 % interval is the percentile interval of the $R'$ retained replicates,

$$\left[\,q_{0.025},\ q_{0.975}\,\right], \qquad q_p \;=\; \Delta^{*}_{(\lfloor h\rfloor)} + \left(h-\lfloor h\rfloor\right)\left(\Delta^{*}_{(\lceil h\rceil)} - \Delta^{*}_{(\lfloor h\rfloor)}\right), \quad h=(R'-1)\,p \qquad (\mathrm{B.12})$$

where $\Delta^{*}_{(j)}$ is the $j$-th smallest replicate margin counted from $j=0$.

[Code: `tools/4thJ_p5_bootstrap_table3.py:93-106, 247` | Source: none vetted | Status: uncited]

### Synthetic population

A four-way table $T$ over age band, sex, household type and economic status is initialised on the
structurally admissible cells, $T^{(0)}\propto M$, with $M$ the 0/1 admissibility mask (for example, no
person aged 11-14 living alone) and the 11-14 row scaled by the donor countries' economic-status mix at
those ages. Each axis $x$ is then rescaled in turn,

$$T(\mathbf{k}) \;\leftarrow\; T(\mathbf{k})\,\frac{\pi_x(k_x)}{T_x(k_x)}, \qquad \text{until } \max_{x}\max_{k}\left|T_x(k)-\pi_x(k)\right| < 10^{-13} \qquad (\mathrm{B.13})$$

where $\mathbf{k}$ is a cell of the table, $k_x$ its category on axis $x$, $T_x$ the current margin of
$T$ on axis $x$ as a share, and $\pi_x$ the published marginal share, with at most 5,000 sweeps.
Zero cells stay zero. Iterative proportional fitting of a joint table onto published margins is the
construction of Beckman et al. (1996) (see also Deming and Stephan, 1940 [AUTHOR TO OPEN]).

[Code: `tools/4thJ_step5_synthesise.py:223-224, 280-314, 602-690` | Source: Beckman et al. 1996 (ACCEPTED); Deming and Stephan 1940 (AAO) | Status: cited]

Day type, which has no published marginal, is added as an independent fifth axis at calendar-week shares,

$$T_5(\mathbf{k},\tau) \;=\; T(\mathbf{k})\,\delta_\tau, \qquad \delta=\left(\tfrac{5}{7},\,\tfrac{1}{7},\,\tfrac{1}{7}\right) \text{ for (weekday, Saturday, Sunday)} \qquad (\mathrm{B.14})$$

[Code: `tools/4thJ_step5_synthesise.py:90-103, 217-218, 720-722` | Source: own assumption | Status: uncited]

The fitted table is expanded to $N=100{,}000$ persons by the largest-remainder rule,

$$n_{\mathbf{c}} \;=\; \left\lfloor N\,T_5(\mathbf{c})\right\rfloor + \mathbb{1}\!\left[\mathbf{c}\in\mathcal{R}\right] \qquad (\mathrm{B.15})$$

where $\mathcal{R}$ is the set of the $N-\sum_{\mathbf{c}}\lfloor N\,T_5(\mathbf{c})\rfloor$ cells with the
largest fractional parts $N\,T_5(\mathbf{c})-\lfloor N\,T_5(\mathbf{c})\rfloor$, ties broken by cell
index. No random draw is involved (Balinski and Young, 1982 [AUTHOR TO OPEN]), in contrast to the
probabilistic integerisation of Lovelace and Ballas (2013).

[Code: `tools/4thJ_step5_synthesise.py:317-330, 724-746` | Source: Balinski and Young 1982 (AAO); Lovelace and Ballas 2013 (ACCEPTED, as contrast) | Status: cited]

### Calendar re-basing of the survey weights

Each real diary's survey weight $w_i$ is post-stratified to the calendar week within its country,

$$w^{\mathrm{cal}}_i \;=\; w_i\,\frac{\delta_{\tau(i)}}{\hat{\delta}_{c,\tau(i)}}, \qquad \hat{\delta}_{c,\tau} \;=\; \frac{\sum_{j\in c,\ \tau(j)=\tau} w_j}{\sum_{j\in c} w_j} \qquad (\mathrm{B.16})$$

where $\tau(i)$ is the day type of diary $i$, $\delta_\tau$ is the calendar-week share of Eq. (B.14),
and $\hat{\delta}_{c,\tau}$ is the weighted share of day type $\tau$ in country $c$ before re-basing. The
total weight of each country is unchanged.

[Code: builder script not located under `tools/`; definition and measured factors in `Step2_docs/4thJ_02_harmonisation.md:2205-2250`; consumed at `tools/4thJ_step6_g68_joint.py:187-217` | Source: none vetted | Status: uncited]

### Joint structure

In this section the level-1 activity of an episode is the first digit of its three-digit code (ten
categories), and every distribution is weighted by the calendar-re-based weight of Eq. (B.16); the
reference is the real diaries of the held-out country and the candidate is the generated diaries.

Dwell-time distance. For activity $a$, let $F_a$ and $G_a$ be the weighted empirical distribution
functions of the durations of the reference and candidate episodes whose code has leading digit $a$. The
first-order Wasserstein distance is evaluated exactly on the merged sorted support
$x_{(1)}<\dots<x_{(m)}$,

$$W_1(a) \;=\; \int \left|F_a(x)-G_a(x)\right|dx \;=\; \sum_{j=1}^{m-1}\left|F_a(x_{(j)})-G_a(x_{(j)})\right|\left(x_{(j+1)}-x_{(j)}\right), \qquad D_W=\max_{a}W_1(a) \qquad (\mathrm{B.17})$$

in minutes, where the maximum runs over activities with at least 30 episodes on each side. Consecutive
episodes that share a leading digit are not merged (Vallender, 1974 [AUTHOR TO OPEN]; see also Ramdas et
al., 2017).

[Code: `tools/4thJ_step6_g68_joint.py:91, 152-153, 272-324, 441-448` | Source: Vallender 1974 (AAO); Ramdas et al. 2017 (ACCEPTED, secondary) | Status: cited]

Transition rate. The mean number of level-1 activity changes per diary is

$$\bar{T} \;=\; \frac{\sum_i w_i\,n_i}{\sum_i w_i}, \qquad \varepsilon_T=\left|\bar{T}^{\mathrm{ref}}-\bar{T}^{\mathrm{cand}}\right| \qquad (\mathrm{B.18})$$

where $n_i$ is the number of consecutive episode pairs in diary $i$ whose level-1 activities differ.

[Code: `tools/4thJ_step6_g68_joint.py:327-339, 450-453` | Source: none | Status: uncited]

Transition structure. With $p(j,k)$ the weighted share of changes from level-1 activity $j$ to activity
$k\neq j$, pooled over diaries, the total variation distance is

$$\mathrm{TVD} \;=\; \tfrac{1}{2}\sum_{(j,k)}\left|p^{\mathrm{ref}}(j,k)-p^{\mathrm{cand}}(j,k)\right| \qquad (\mathrm{B.19})$$

(Levin et al., 2009).

[Code: `tools/4thJ_step6_g68_joint.py:342-358, 455-456` | Source: Levin, Peres and Wilmer 2009, 1st ed. (ACCEPTED) | Status: cited]

Diurnal pattern. For activity $a$, let $p_a(s)$ be the weighted share of all time spent in $a$ that falls
in ten-minute slot $s=1,\dots,144$ (the time-of-day distribution of the activity). The Jensen-Shannon
divergence in bits is

$$\mathrm{JSD}(p,q) \;=\; H\!\left(\tfrac{p+q}{2}\right)-\tfrac{1}{2}H(p)-\tfrac{1}{2}H(q), \qquad H(v)=-\sum_{s}v_s\log_2 v_s \qquad (\mathrm{B.20})$$

with $p=p^{\mathrm{ref}}_a$ and $q=p^{\mathrm{cand}}_a$; it lies in $[0,1]$. The reported value is the mean
over activities, and the check also bounds the maximum over activities (Lin, 1991).

[Code: `tools/4thJ_step6_g68_joint.py:85-86, 379-416, 467-474, 490-491` | Source: Lin 1991 (ACCEPTED) | Status: cited]

Time-budget error on the joint-structure scale is the largest absolute difference over the ten level-1
activities,

$$\varepsilon_B \;=\; \max_{a}\left|B'^{\,\mathrm{ref}}_{a}-B'^{\,\mathrm{cand}}_{a}\right| \qquad (\mathrm{B.21})$$

where $B'_a$ is the weighted mean minutes per day in first-digit activity $a$. This quantity differs from
Eq. (B.2): it compares two sets of diaries rather than a set with a published table, and it takes the
worst of ten activities rather than the mean of six aggregates.

[Code: `tools/4thJ_step6_g68_joint.py:88, 366-376, 461-465, 489` | Source: none | Status: uncited]

### The fictional-country control

The age-band mix of the held-out country's synthetic population is tilted exponentially,

$$\pi_\lambda(b) \;=\; \frac{\pi_0(b)\,e^{\lambda\rho_b}}{\sum_{b'}\pi_0(b')\,e^{\lambda\rho_{b'}}}, \qquad \lambda_\ell=-\lambda_{\max}+2\lambda_{\max}\,\frac{\ell}{L-1},\quad \ell=0,\dots,L-1 \qquad (\mathrm{B.22})$$

where $b$ runs over the eight age bands present, $\rho_b$ is the rank of band $b$ from youngest ($0$),
$\pi_0$ is the observed mix, $L=5$ levels and $\lambda_{\max}=0.6$. All other prefix fields keep their
within-band composition, and every prefix carries a country token absent from training.

[Code: `tools/4thJ_step6_g67_prefixes.py:148-163, 182-183, 246-256` | Source: own definition | Status: uncited]

The expected budget at level $\ell$ is the average, over the $n=600$ prefixes drawn at that level, of the
donor-country budget of each prefix's stratum,

$$E_\ell(a) \;=\; \frac{1}{n}\sum_{j=1}^{n} B^{\mathrm{donor}}_{a}\!\left(\sigma_j\right) \qquad (\mathrm{B.23})$$

where $\sigma_j$ is the stratum of prefix $j$ and $B^{\mathrm{donor}}_a(\sigma)$ is Eq. (B.1) over the
donor diaries of that stratum, backing off one prefix field at a time until at least five donor diaries
are available.

[Code: `tools/4thJ_step6_g67_prefixes.py:98-145, 257-265` | Source: own definition | Status: uncited]

The response is fitted by ordinary least squares of the generated budget $y$ on the expected budget $x$,
each aggregate centred on its own mean across the five levels before pooling,

$$\hat{\beta} \;=\; \frac{\sum \tilde{x}\,\tilde{y}}{\sum \tilde{x}^{2}}, \qquad R^{2} \;=\; \frac{\left(\sum \tilde{x}\,\tilde{y}\right)^{2}}{\sum \tilde{x}^{2}\,\sum \tilde{y}^{2}}, \qquad \tilde{x}=x_{\ell a}-\bar{x}_a,\ \ \tilde{y}=y_{\ell a}-\bar{y}_a \qquad (\mathrm{B.24})$$

where $x_{\ell a}=E_\ell(a)$, $y_{\ell a}$ is Eq. (B.1) over the diaries generated at level $\ell$, and
the sums run over the (level, aggregate) points being fitted (Montgomery et al., 2012
[AUTHOR TO OPEN]).

[Code: `tools/4thJ_step6_g67_score.py:99-112, 162-189` | Source: Montgomery, Peck and Vining 2012 (AAO) | Status: cited, AAO only]

Two clauses are scored:

$$\text{steering: } \hat{\beta}_{\mathrm{AC2}}>0 \ \wedge\ R^2_{\mathrm{AC2}}\ge 0.80; \qquad \text{amplitude: } \hat{\beta}_{\mathcal{A}\setminus\{\mathrm{AC4\text{-}8}\}}\ge 0.80 \qquad (\mathrm{B.25})$$

where the steering fit uses the study aggregate AC2 alone and the amplitude fit pools the five aggregates
other than AC4-8, which is excluded because the six aggregates sum to the whole day and AC4-8 absorbs the
residual.

[Code: `tools/4thJ_step6_g67_score.py:88-96, 175-177, 186, 207-229` | Source: own definition | Status: uncited]

### Country discrimination

With $d_c=\mathrm{MAE}(B^{\mathrm{model}},B^{\mathrm{pub}}_c)$ from Eq. (B.2) for each of the three
countries, $o$ the held-out country and $r=\arg\min_{c\neq o}d_c$ the nearest other country,

$$\rho \;=\; \frac{d_r-d_o}{\mathrm{MAE}\!\left(B^{\mathrm{pub}}_o,B^{\mathrm{pub}}_r\right)}, \qquad \text{pass if } \arg\min_c d_c=o \ \text{ and } \ \rho>0.5 \qquad (\mathrm{B.26})$$

where the denominator is the distance between the two published profiles. A model lying exactly on its
own published table scores $\rho=1$; one equidistant from both scores $\rho=0$.

[Code: `tools/4thJ_step6_g65_g69.py:99-101, 204-266` | Source: own definition | Status: uncited]

### Markov-chain comparator

Each diary is expressed as 144 level-1 states $s_t$. For day type $\tau$ and slot $t=0,\dots,142$,

$$P_{\tau,t}(j\mid i) \;=\; \frac{N_{\tau,t}(i\to j)}{\sum_k N_{\tau,t}(i\to k)}, \qquad \text{or } \ \pi_{\tau,t+1}(j)=\frac{N_{\tau,t+1}(j)}{\sum_k N_{\tau,t+1}(k)} \ \text{ if state } i \text{ is unseen at } t \qquad (\mathrm{B.27})$$

where $N_{\tau,t}(i\to j)$ is the unweighted count of training diaries in state $i$ at slot $t$ and state
$j$ at slot $t+1$, and $N_{\tau,t+1}(j)$ is the count in state $j$ at slot $t+1$. The first state is drawn
from the slot-0 distribution. The construction follows the first-order time-inhomogeneous chains of
Richardson et al. (2008), whose states are numbers of active occupants rather than activities, and of
Widén and Wäckelgård (2010) [AUTHOR TO OPEN].

[Code: `tools/4thJ_step6_markov_comparator.py:75-117, 141-166` | Source: Richardson et al. 2008 (ACCEPTED); Widén and Wäckelgård 2010 (AAO for this claim) | Status: cited]

### Privacy audit

The score of a record is the mean negative log-likelihood of its diary body under a model $\theta$,

$$\ell_\theta(i) \;=\; -\frac{1}{|\mathcal{T}_i|}\sum_{t\in\mathcal{T}_i}\log p_\theta\!\left(x_{i,t}\mid x_{i,<t}\right), \qquad s^{\mathrm{loss}}_i=-\ell_{\mathrm{tuned}}(i) \qquad (\mathrm{B.28})$$

where $\mathcal{T}_i$ is the set of body token positions of record $i$ (the conditioning prefix is excluded)
and $x_{i,t}$ is its $t$-th token. Members are training-split diaries of the training countries and
non-members are their held-back split (Shokri et al., 2017; Yeom et al., 2018 [AUTHOR TO OPEN]).

[Code: `tools/4thJ_step6_privacy_mia.py:17-50, 153-176, 456` | Source: Shokri et al. 2017 (ACCEPTED, general context); Yeom et al. 2018 (AAO) | Status: cited]

The reference-calibrated score subtracts the same record's loss under the untuned backbone,

$$s^{\mathrm{ref}}_i \;=\; \ell_{\mathrm{base}}(i)-\ell_{\mathrm{tuned}}(i) \qquad (\mathrm{B.29})$$

where the base model is the pretrained backbone at the revision the adapter was trained from.

[Code: `tools/4thJ_step6_privacy_mia.py:46-50, 457-458` | Source: own choice (a single public reference model, not shadow models) | Status: uncited]

The area under the ROC curve is computed from ranks,

$$\mathrm{AUC} \;=\; \frac{R_1-\tfrac{1}{2}n_1(n_1+1)}{n_1\,n_0} \qquad (\mathrm{B.30})$$

where $R_1$ is the sum of the mid-ranks of the $n_1$ member scores among all $n_1+n_0$ scores and $n_0$
is the number of non-members (Hanley and McNeil, 1982 [AUTHOR TO OPEN]).

[Code: `tools/4thJ_step6_privacy_mia.py:109-126` | Source: Hanley and McNeil 1982 (AAO) | Status: cited, AAO only]

The true-positive rate at a false-positive rate of 0.1 % is

$$\mathrm{TPR}_{0.001} \;=\; \frac{1}{n_1}\sum_{i\in\mathrm{mem}}\mathbb{1}\!\left[s_i>\vartheta\right], \qquad \vartheta=\text{the }k\text{-th largest non-member score},\ k=\lfloor 0.001\,n_0\rfloor \qquad (\mathrm{B.31})$$

and is not defined when $k<1$ (Carlini et al., 2022 [AUTHOR TO OPEN]).

[Code: `tools/4thJ_step6_privacy_mia.py:87-89, 129-140` | Source: Carlini et al. 2022 (AAO, corrected string) | Status: cited, AAO only]

The perplexity-gap control is

$$g_{\mathrm{PPL}} \;=\; \frac{\left|\mathrm{PPL}_{\mathrm{non}}-\mathrm{PPL}_{\mathrm{mem}}\right|}{\mathrm{PPL}_{\mathrm{mem}}}, \qquad \mathrm{PPL}=\exp\!\Big(\tfrac{1}{n}\sum_i \ell_{\mathrm{tuned}}(i)\Big) \qquad (\mathrm{B.32})$$

where the mean runs over the members or the non-members; the control passes below 0.05.

[Code: `tools/4thJ_step6_privacy_mia.py:91, 202-207` | Source: own definition | Status: uncited]

Distance to closest record. Each diary is written as its 144 ten-minute primary activity codes $z_i(s)$.
For a generated diary $g$ and a reference set $\mathcal{D}$,

$$d(g,j)=\frac{1}{144}\sum_{s=1}^{144}\mathbb{1}\!\left[z_g(s)\ne z_j(s)\right], \qquad \mathrm{DCR}_g=\min_{j\in\mathcal{D}}d(g,j), \qquad \mathrm{NNDR}_g=\frac{d_{(1)}(g)}{d_{(2)}(g)} \qquad (\mathrm{B.33})$$

where $d_{(1)}$ and $d_{(2)}$ are the smallest and second-smallest distances ($\mathrm{NNDR}_g=1$ if
$d_{(2)}=0$). Location, secondary activity and co-presence are not part of the distance. The check fails
if any DCR is zero or if more than 0.1 % of records have NNDR below 0.33 (Platzer and Reutterer, 2021;
Park et al., 2018 [AUTHOR TO OPEN]).

[Code: `tools/4thJ_step6_g613_dcr.py:100-125, 161-183, 294-323` | Source: Platzer and Reutterer 2021 (ACCEPTED, "as used by"); Park et al. 2018 (AAO, DCR only) | Status: cited]

The memorisation clause compares the median DCR to the held-back split with a size-matched distribution
for the training split,

$$\text{fail if } \ \operatorname{med}\!\left(\mathrm{DCR}^{\mathrm{test}}\right) > u_{0.975}, \qquad u_{p}=\text{the }p\text{-quantile of }\left\{\operatorname{med}\!\left(\mathrm{DCR}^{\mathrm{train}}_{(q)}\right)\right\}_{q=1}^{200} \qquad (\mathrm{B.34})$$

where $\mathrm{DCR}^{\mathrm{train}}_{(q)}$ is computed against the $q$-th random subset of the training split
drawn without replacement at the size of the held-back split, and the quantile is taken as an order
statistic of the 200 subset medians.

[Code: `tools/4thJ_step6_g613_dcr.py:104-106, 333-366` | Source: own definition | Status: uncited]

### Decoding neutrality

With $m_k$ the mean minutes per diary in three-digit activity code $k$,

$$\delta_{\max} \;=\; \max_{k}\left|m^{\mathrm{con}}_k-m^{\mathrm{val}}_k\right|, \qquad \text{pass if } \delta_{\max}\le 5.0 \qquad (\mathrm{B.35})$$

where "con" is the grammar-constrained batch and "val" is the subset of the unconstrained batch that is
structurally valid, in minutes per day.

[Code: `tools/4thJ_gates_step7.py:69, 245-255, 449-470` | Source: own definition | Status: uncited]

### Activity-triggered appliances

Eligibility. Appliance $k$ belongs to a CREST activity profile $p(k)$. Dwelling $d$ is eligible in minute
$t$ if at least one member is an active occupant (at home, with a primary activity other than codes 011
and 012, which are treated as present but not active) whose primary activity maps to profile $p(k)$,

$$\mathcal{E}_{d,p}(t)=\max_{m\in d}\ \mathbb{1}\!\left[\text{member } m \text{ active at } t\right]\mathbb{1}\!\left[\phi(c_{m,t})=p\right], \qquad \bar{E}_p=\frac{1}{N_{\mathrm{dw}}}\sum_{d}\sum_{t\in\text{year}}\mathcal{E}_{d,p}(t) \qquad (\mathrm{B.36})$$

where $\phi$ maps activity codes to CREST profiles, $c_{m,t}$ is member $m$'s primary activity at minute $t$,
and $\bar{E}_p$ is the mean number of eligible minutes per dwelling-year over all $N_{\mathrm{dw}}$
dwellings. For the active-occupancy profile every active minute is eligible, and for cold appliances every
minute is. The appliance states (off, running, restart delay) follow the CREST model (Richardson et al.,
2010).

[Code: `tools/4thJ_step9_trigger.py:9-37, 70-77, 195-233, 286-301, 652-667` | Source: Richardson et al. 2010 (ACCEPTED) | Status: cited]

Start probability. In each eligible minute an idle appliance starts with a constant probability $h_k$.
Its starting value matches the published number of cycles per year,

$$h^{(0)}_k \;=\; \frac{C_k}{\bar{E}_{p(k)}-C_k\left(L_k+D_k\right)\bar{E}_{p(k)}/525{,}600} \qquad (\mathrm{B.37})$$

where $C_k$ is the published cycles per year, $L_k$ the cycle length and $D_k$ the restart delay in
minutes, and 525,600 the minutes in a year; a non-positive denominator or $h^{(0)}_k\ge 1$ stops the run.
Calibrating a start probability to a published annual count follows the idea of Richardson et al. (2010,
Section 2.7); Eq. (B.37) is written for a 0/1 diary eligibility and is not a transcription of that paper.

[Code: `tools/4thJ_step9_trigger.py:338-369, 670-683` | Source: Richardson et al. 2010, Section 2.7 (ACCEPTED, idea only) | Status: cited]

The probability is then rescaled until the stock reproduces the published count,

$$h^{(m+1)}_k=\min\!\left(0.999,\ \frac{h^{(m)}_k}{r^{(m)}_k}\right), \qquad r^{(m)}_k=\frac{\bar{c}^{(m)}_k}{C_k}, \qquad \text{until } \max_k\left|r^{(m)}_k-1\right|\le 0.02 \ \text{ or } m=6 \qquad (\mathrm{B.38})$$

where $\bar{c}^{(m)}_k$ is the simulated mean cycles per owning dwelling-year at pass $m$. An appliance whose
ratio changes by less than 0.01 between passes while below 0.98 is held fixed and reported as saturated,
and appliances with $C_k<0.5$ are excluded.

[Code: `tools/4thJ_step9_trigger.py:804-871, 965, 998-1006` | Source: own procedure | Status: uncited]

The number of eligible minutes skipped before the next start is drawn exactly as

$$K=\left\lfloor \frac{\ln(1-u)}{\ln(1-h_k)}\right\rfloor, \qquad u\sim\mathcal{U}(0,1) \qquad (\mathrm{B.39})$$

which is the geometric waiting time of a per-minute Bernoulli($h_k$) draw.

[Code: `tools/4thJ_step9_trigger.py:375-386, 439-458` | Source: standard | Status: uncited]

A started cycle runs for

$$L=\begin{cases}\max\!\left(1,\operatorname{round}\,\mathcal{N}\!\left(L_k,(L_k/10)^2\right)\right), & k \text{ in the Gaussian set},\\ \max\!\left(1,\operatorname{round}\!\left(70\,(-\ln(1-u))^{1.1}\right)\right), & k \text{ a television},\\ L_k, & \text{otherwise,}\end{cases} \qquad (\mathrm{B.40})$$

minutes, runs to completion after the triggering activity ends, and pauses while no occupant is active
except for cold, laundry and custom appliances.

[Code: `tools/4thJ_step9_trigger.py:75-80, 314-321, 400-433` | Source: none vetted (the code attributes the television form to the CREST reference implementation) | Status: uncited]

Peak hour. With $P_d(y,t)$ the electricity demand of dwelling $d$ on day $y$ in clock hour $t$ (mean power
over the hour, after rotating the 04:00 diary origin to midnight),

$$\bar{P}(t)=\frac{1}{N_{\mathrm{dw}}\,N_{\mathrm{days}}}\sum_{y}\sum_{d}P_d(y,t), \qquad t^{*}=\arg\max_{t}\bar{P}(t) \qquad (\mathrm{B.41})$$

where $t^{*}$ is reported as the hour beginning and $\bar{P}(t^{*})$ as the peak power per dwelling in W.

[Code: `tools/4thJ_p3_run_campaign.py:52-72`; `tools/4thJ_step9_trigger.py:749-773, 942, 1017-1030` | Source: own definition | Status: uncited]

Load-shape agreement with the reference profile is the squared Pearson correlation over the 24 hourly
values,

$$R^2_{\mathrm{LS}}=\frac{\left[\sum_t\left(\bar{P}(t)-\bar{P}\right)\left(P^{\mathrm{ref}}(t)-\bar{P}^{\mathrm{ref}}\right)\right]^2}{\sum_t\left(\bar{P}(t)-\bar{P}\right)^2\sum_t\left(P^{\mathrm{ref}}(t)-\bar{P}^{\mathrm{ref}}\right)^2} \qquad (\mathrm{B.42})$$

where $P^{\mathrm{ref}}$ is the expected diurnal appliance power built from the published CREST activity
statistics and appliance parameters (Richardson et al., 2010) and the bar and overlines on the sums denote
24-hour means; the check requires $R^2_{\mathrm{LS}}\ge 0.85$.

[Code: `tools/4thJ_gates_step9.py:48, 831-887, 890-951` | Source: Richardson et al. 2010 (ACCEPTED, for the reference model) | Status: cited]

### Domestic hot water

For draw category $j$ (short, medium, bath, shower) the start probability per eligible minute is

$$h_j=\frac{N_j}{\bar{E}_j-N_j\left(\Delta_j-1\right)}, \qquad N_j=365\,\nu_j\,\frac{V_d}{200} \qquad (\mathrm{B.43})$$

where $\nu_j$ is the published number of draws per day, $\Delta_j$ the draw duration in minutes,
$\bar{E}_j$ the mean eligible minutes per dwelling-year for the category's driver activities, and $V_d$
the daily volume per dwelling in litres (200 l in Jordan and Vajen, 2001, Table 1).

[Code: `tools/4thJ_step9_trigger.py:670-725, 999` | Source: Jordan and Vajen 2001, Table 1, p. 5 (ACCEPTED) | Status: cited]

The flow of each draw is

$$q=\max\!\left(0.2,\ 0.2\,\operatorname{round}\!\left(q'/0.2\right)\right), \qquad q'\sim\mathcal{N}\!\left(\mu_j,\ (0.2\,\sigma_j)^2\right) \qquad (\mathrm{B.44})$$

in l/min, where $\mu_j$ is the mean flow and $\sigma_j=2$ is the spread of Jordan and Vajen (2001, Table 1),
read in units of the 0.2 l/min flow step, so that the standard deviation is 0.4 l/min.

[Code: `tools/4thJ_step9_trigger.py:462-499` | Source: Jordan and Vajen 2001, Table 1, p. 5 (ACCEPTED; the step reading is ours) | Status: cited]

### Occupancy-driven internal gains and the heating response

The presence signal of a household of $n_h$ members in hour $t$ is

$$g(t)=\frac{1}{n_h}\sum_{m=1}^{n_h}\frac{1}{60}\sum_{\text{minutes }u\in t}\mathbb{1}\!\left[\text{member } m \text{ present at } u\right] \qquad (\mathrm{B.45})$$

where a member is present when at home and not engaged in an activity on the outdoor-at-home exclusion
list; $g(t)\in[0,1]$.

[Code: `tools/4thJ_step7_schedules.py:46-55, 321-353` | Source: own definition | Status: uncited]

The internal gain density is

$$\phi_{\mathrm{int}}(t)=\bar{\phi}\left[(1-f)+f\,\frac{g(t)}{\bar{g}}\right], \qquad \bar{g}=\frac{1}{8760}\sum_{t=1}^{8760}g(t), \qquad \bar{\phi}=3.0\ \mathrm{W\,m^{-2}} \qquad (\mathrm{B.46})$$

where $f\in\{0,0.15,0.30,0.50,1.00\}$, so the annual mean of $\phi_{\mathrm{int}}$ equals $\bar{\phi}$ at
every $f$. The value $\bar{\phi}$ is the TABULA boundary condition of the European comparison rows
EU.SUH and EU.MUH (IWU TABULA calculator workbook); the national rows differ. We found no published
precedent for redistributing a fixed annual internal-gain budget by an occupancy profile.

[Code: `tools/4thJ_step8_scenario.py:17-28, 52, 82-98`; `tools/4thJ_step8_injected.py:12-13` | Source: IWU TABULA calculator workbook (ACCEPTED, data file); redistribution own | Status: cited]

For archetype cell $k$ and level $f$, with $P_{k,f,h}$ the annual peak hourly heating demand per unit
floor area for driving household $h$ and $\bar{P}_{k,f}$ its mean over the $H$ households of the cell's
ensemble,

$$\Delta P_{k,f}=100\,\frac{\bar{P}_{k,f}-\bar{P}_{k,0}}{\bar{P}_{k,0}}, \qquad \sigma_{k,f}=100\,\frac{\mathrm{sd}_h\!\left(P_{k,f,h}\right)}{\bar{P}_{k,f}} \qquad (\mathrm{B.47})$$

in per cent. The fold-level peak effect is the median of $\Delta P_{k,1}$ over cells, the between-diary
spread is the median of $\sigma_{k,1}$ over cells, and the annual effect is defined in the same way on
annual heating energy per unit floor area.

[Code: `tools/4thJ_step8_injected.py:267-297, 570-584, 714-727`; `tools/4thJ_step8_aggregate.py:140-177`; values `Step8_docs/outputs_step8/agg_by_fold.csv` rows f=1.00 | Source: own definition | Status: uncited]

### Fine-tuning

Each adapted weight matrix is

$$h=W_0x+\gamma\,BAx, \qquad B\in\mathbb{R}^{d\times r},\ A\in\mathbb{R}^{r\times k},\ \gamma=\frac{\alpha}{\sqrt{r}} \qquad (\mathrm{B.48})$$

where $W_0\in\mathbb{R}^{d\times k}$ is the frozen pretrained weight, $x$ the layer input, $A$ and $B$ the
only trained matrices, $r=32$ the rank and $\alpha=64$ the scaling constant, so $\gamma\approx 11.31$
under rank-stabilised scaling (the original form uses $\alpha/r$). Adapters are applied to the seven
linear projections of every block, with dropout 0.05 on the adapter input (Hu et al., 2022).

[Code: `tools/4thJ_step4_thresholds.py:93-98`; `tools/4thJ_step4_train.py:1281-1286` | Source: Hu et al. 2022, Eq. (3), Section 4.1 (ACCEPTED); no vetted source for the rank-stabilised factor | Status: cited]

The training objective is the next-token cross-entropy over diary-body tokens only,

$$\mathcal{L}(\theta)=-\frac{1}{\sum_i|\mathcal{T}_i|}\sum_i\sum_{t\in\mathcal{T}_i}\log p_\theta\!\left(x_{i,t}\mid x_{i,<t}\right) \qquad (\mathrm{B.49})$$

where the sums run over the records of a batch and $\mathcal{T}_i$ is as in Eq. (B.28); prefix and
padding positions carry no loss.

[Code: `tools/4thJ_step4_train.py:182-200, 1513-1514` | Source: standard | Status: uncited]

---

### References used in this appendix (strings from VETTING_RL34 sections 3 and 4; AAO items are not to be printed until opened)

- Beckman, R.J., Baggerly, K.A., McKay, M.D., 1996. Creating synthetic baseline populations. Transportation Research Part A: Policy and Practice 30 (6), 415-429. https://doi.org/10.1016/0965-8564(96)00004-3
- Deville, J.-C., Särndal, C.-E., 1992. Calibration estimators in survey sampling. Journal of the American Statistical Association 87 (418), 376-382. https://doi.org/10.1080/01621459.1992.10475217
- Hu, E.J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., Chen, W., 2022. LoRA: Low-rank adaptation of large language models. International Conference on Learning Representations (ICLR 2022). https://doi.org/10.48550/arXiv.2106.09685
- Hyndman, R.J., Koehler, A.B., 2006. Another look at measures of forecast accuracy. International Journal of Forecasting 22 (4), 679-688. https://doi.org/10.1016/j.ijforecast.2006.03.001
- IWU (Institut Wohnen und Umwelt), TABULA calculator workbook `tabula-calculator.xlsx`, sheet `Tab.BoundaryCond`, rows `EU.SUH` and `EU.MUH`. https://episcope.eu/fileadmin/tabula/public/calc/tabula-calculator.xlsx (accessed 2026-08-21, per `Step8_docs/outputs_step8/archetype_parameter_provenance.md:28`)
- Jordan, U., Vajen, K., 2001. Realistic Domestic Hot-Water Profiles in Different Time Scales, Version 2.0, May 2001. IEA Solar Heating and Cooling Programme, Task 26: Solar Combisystems. Universität Marburg, Marburg.
- Levin, D.A., Peres, Y., Wilmer, E.L., 2009. Markov Chains and Mixing Times. American Mathematical Society, Providence, RI. ISBN 978-0-8218-4739-8.
- Lin, J., 1991. Divergence measures based on the Shannon entropy. IEEE Transactions on Information Theory 37 (1), 145-151. https://doi.org/10.1109/18.61115
- Lovelace, R., Ballas, D., 2013. 'Truncate, replicate, sample': A method for creating integer weights for spatial microsimulation. Computers, Environment and Urban Systems 41, 1-11. https://doi.org/10.1016/j.compenvurbsys.2013.03.004
- Platzer, M., Reutterer, T., 2021. Holdout-based empirical assessment of mixed-type synthetic data. Frontiers in Big Data 4, 679939. https://doi.org/10.3389/fdata.2021.679939
- Ramdas, A., García Trillos, N., Cuturi, M., 2017. On Wasserstein two-sample testing and related families of nonparametric tests. Entropy 19 (2), 47. https://doi.org/10.3390/e19020047
- Richardson, I., Thomson, M., Infield, D., 2008. A high-resolution domestic building occupancy model for energy demand simulations. Energy and Buildings 40 (8), 1560-1566. https://doi.org/10.1016/j.enbuild.2008.02.006
- Richardson, I., Thomson, M., Infield, D., Clifford, C., 2010. Domestic electricity use: A high-resolution energy demand model. Energy and Buildings 42 (10), 1878-1887. https://doi.org/10.1016/j.enbuild.2010.05.023
- Shokri, R., Stronati, M., Song, C., Shmatikov, V., 2017. Membership inference attacks against machine learning models. 2017 IEEE Symposium on Security and Privacy (SP), 3-18. https://doi.org/10.1109/SP.2017.41
- [AUTHOR TO OPEN] Balinski, M.L., Young, H.P., 1982. Fair Representation. Yale University Press. ISBN 978-0-300-02724-2. (Confirm the chapter on Hamilton's largest-remainder method; author initials to be copied from the book.)
- [AUTHOR TO OPEN] Carlini, N., Chien, S., Nasr, M., Song, S., Terzis, A., Tramèr, F., 2022. Membership inference attacks from first principles. 2022 IEEE Symposium on Security and Privacy (SP), 1897-1914. https://doi.org/10.1109/SP46214.2022.9833649
- [AUTHOR TO OPEN] Deming and Stephan, 1940. Annals of Mathematical Statistics 11 (4), 427-444. https://doi.org/10.1214/aoms/1177731829 (title and initials to be copied from the Crossref record)
- [AUTHOR TO OPEN] Hanley and McNeil, 1982. Radiology 143 (1), 29-36. https://doi.org/10.1148/radiology.143.1.7063747 (title and initials to be copied from the Crossref record)
- [AUTHOR TO OPEN] Montgomery, D.C., Peck, E.A., Vining, G.G., 2012. Introduction to Linear Regression Analysis, 5th ed. Wiley. ISBN 978-0-470-54281-1.
- [AUTHOR TO OPEN] Park et al., 2018. PVLDB 11 (10), 1071-1083. https://doi.org/10.14778/3231751.3231757 (full author list and title to be copied from the Crossref record; cite for DCR only after confirming NNDR is absent)
- [AUTHOR TO OPEN] Vallender, 1974. Theory of Probability and Its Applications 18 (4), 784-786. https://doi.org/10.1137/1118101 (title and initials to be copied from the Crossref record)
- [AUTHOR TO OPEN] Widén, J., Wäckelgård, E., 2010. A high-resolution stochastic model of domestic activity patterns and electricity demand. Applied Energy 87 (6), 1880-1892. https://doi.org/10.1016/j.apenergy.2009.11.006 (already cited in the manuscript; the first-order transition-count claim of Eq. (B.27) needs opening)
- [AUTHOR TO OPEN] Willmott and Matsuura, 2005. Climate Research 30, 79-82. https://doi.org/10.3354/cr030079 (title and initials to be copied from the Crossref record)
- [AUTHOR TO OPEN] Yeom, S., Giacomelli, I., Fredrikson, M., Jha, S., 2018. Privacy risk in machine learning: Analyzing the connection to overfitting. 2018 IEEE 31st Computer Security Foundations Symposium (CSF), 268-282. https://doi.org/10.1109/csf.2018.00027 (initials to be confirmed)

---

## (a) Nomenclature

| Symbol | Meaning | Unit |
|---|---|---|
| $a$ | activity category: one of six HETUS level-1 aggregates in Eqs. (B.1)-(B.7) and (B.22)-(B.26); one of ten first-digit activities in Eqs. (B.17)-(B.21) and (B.27) | - |
| $\mathcal{A}$ | set of the six level-1 aggregates | - |
| $\mathcal{A}^{\mathrm{APE}}_b$ | aggregates of band $b$ scored on APE | - |
| $\alpha(\cdot)$ | crosswalk from activity code to aggregate | - |
| $\alpha$ (B.48) | LoRA scaling constant (64) | - |
| $A$, $B$ (B.48) | trained low-rank adapter matrices | - |
| $\mathrm{APE}_a$ | absolute percentage error of aggregate $a$ | % |
| $\mathrm{AUC}$ | area under the ROC curve | - |
| $b$ | scoreable age band (25-44, 45-64, 65+) | - |
| $B_a(S)$ | weighted level-1 budget of diary set $S$ | min/day |
| $B^{\mathrm{pub}}_a(c,b)$ | published level-1 budget | min/day |
| $B'_a$ | weighted budget in first-digit activity $a$ | min/day |
| $B^{\mathrm{donor}}_a(\sigma)$ | donor-country budget of stratum $\sigma$ | min/day |
| $c$ | country (held-out country in B.1-B.4) | - |
| $c_e$ | three-digit primary activity code of episode $e$ | - |
| $C_k$ | published cycles per year of appliance $k$ | 1/year |
| $\bar{c}_k$ | simulated mean cycles per owning dwelling-year | 1/year |
| $d_e$ | duration of episode $e$ | min |
| $d(g,j)$ | normalised Hamming distance between two diaries | - |
| $d_c$ | MAE of the model profile against country $c$'s table | min/day |
| $D_k$ | restart delay of appliance $k$ | min |
| $D_W$ | reported dwell-time distance, max over activities | min |
| $\mathrm{DCR}$ | distance to closest record | - |
| $\delta_\tau$ | calendar-week share of day type $\tau$ (5/7, 1/7, 1/7) | - |
| $\hat{\delta}_{c,\tau}$ | survey-weighted share of day type $\tau$ in country $c$ | - |
| $\delta_{\max}$ | worst decoding-neutrality deviation | min/day |
| $\Delta(c,b)$ | transfer margin | min/day |
| $\Delta^{*}_r$ | bootstrap replicate margin | min/day |
| $\Delta_j$ | duration of hot-water draw category $j$ | min |
| $\Delta P_{k,f}$ | peak heating effect of level $f$ in cell $k$ | % |
| $\mathcal{E}_{d,p}(t)$ | eligibility indicator of dwelling $d$ for profile $p$ | - |
| $\bar{E}_p$, $\bar{E}_j$ | mean eligible minutes per dwelling-year | min/year |
| $\bar{E}_a$ | unweighted European mean published budget | min/day |
| $E_\ell(a)$ | expected budget at tilt level $\ell$ | min/day |
| $\varepsilon_B$ | joint-structure time-budget error | min/day |
| $\varepsilon_T$ | absolute error in transitions per day | 1/day |
| $f$ | occupancy sensitivity level | - |
| $F_a$, $G_a$ | weighted empirical distribution functions of episode durations | - |
| $g(t)$ | household presence fraction in hour $t$ | - |
| $\bar{g}$ | annual mean of $g(t)$ | - |
| $g_{\mathrm{PPL}}$ | relative perplexity gap | - |
| $\gamma$ | effective adapter scale $\alpha/\sqrt{r}$ | - |
| $h$ (B.12) | fractional rank position in the percentile rule | - |
| $h_k$, $h_j$ | start probability per eligible minute | 1/min |
| $H(\cdot)$ | Shannon entropy, base 2 | bit |
| $\mathrm{JSD}$ | Jensen-Shannon divergence | bit |
| $K$ | eligible minutes skipped before the next start | min |
| $L_k$ | cycle length of appliance $k$ | min |
| $L$ (B.22) | number of tilt levels (5) | - |
| $\ell$ | tilt level index | - |
| $\ell_\theta(i)$ | mean body-token negative log-likelihood | nat/token |
| $\mathcal{L}(\theta)$ | training loss | nat/token |
| $\lambda$, $\lambda_{\max}$ | tilt parameter, its maximum (0.6) | - |
| $m_k$ | mean minutes per diary in code $k$ | min/day |
| $M$ | admissibility mask of the synthetic-population table | - |
| $\mathrm{MAE}$ | mean absolute error over six aggregates | min/day |
| $\mathrm{MAPE}$ | mean absolute percentage error | % |
| $\mu_j$ | mean flow of draw category $j$ | l/min |
| $n_{\mathrm{eff}}$ | Kish effective sample size | diaries |
| $n_{\mathbf{c}}$ | integer persons in cell $\mathbf{c}$ | persons |
| $n_h$ | household size | persons |
| $n_i$ | level-1 activity changes in diary $i$ | - |
| $n_0$, $n_1$ | numbers of non-members and members | records |
| $N$ | synthetic population size (100,000) | persons |
| $N_{\mathrm{dw}}$ | number of dwellings | - |
| $N_j$ | target hot-water draws per dwelling-year | 1/year |
| $N_{\tau,t}(i\to j)$ | transition count | diaries |
| $\nu_j$ | published draws per day | 1/day |
| $\mathrm{NNDR}$ | nearest-neighbour distance ratio | - |
| $p$ (B.36) | CREST activity profile | - |
| $p(j,k)$ | share of transitions from $j$ to $k$ | - |
| $p_a(s)$ | share of activity $a$'s time in slot $s$ | - |
| $\hat{p}_v(k)$, $p^{*}_v(k)$ | current and target share of category $k$ of variable $v$ | - |
| $P_{\tau,t}(j\mid i)$ | Markov transition probability | - |
| $P_d(y,t)$ | electricity demand of dwelling $d$, day $y$, hour $t$ | W |
| $\bar{P}(t)$, $t^{*}$ | per-dwelling mean diurnal demand, peak hour | W, h |
| $P^{\mathrm{ref}}(t)$ | CREST reference diurnal demand | W |
| $P_{k,f,h}$, $\bar{P}_{k,f}$ | annual peak heating demand per floor area, ensemble mean | W/m² |
| $\phi_{\mathrm{int}}$, $\bar{\phi}$ | internal gain density, its annual mean (3.0) | W/m² |
| $\phi(\cdot)$ | map from activity code to CREST profile | - |
| $\pi_x$ | published marginal share on axis $x$ | - |
| $\pi_0(b)$, $\pi_\lambda(b)$ | observed and tilted age-band shares | - |
| $q$, $q'$ | discretised and raw draw flow | l/min |
| $q_p$ | $p$-quantile of the replicate margins | min/day |
| $r$ (B.48) | adapter rank (32) | - |
| $r_k$ | ratio of simulated to published cycles | - |
| $R$, $R'$ | bootstrap replicates drawn (2,000), retained | - |
| $R_1$ | rank sum of member scores | - |
| $R^2$ | coefficient of determination of the OLS fit | - |
| $R^2_{\mathrm{LS}}$ | load-shape coefficient of determination | - |
| $\rho$ | relative discrimination margin | - |
| $\rho_b$ | rank of age band $b$ | - |
| $s$ | ten-minute slot index (1-144) | - |
| $s^{\mathrm{loss}}_i$, $s^{\mathrm{ref}}_i$ | membership scores | nat/token |
| $S$ | set of diaries | - |
| $\sigma_j$ | spread of draw category $j$ in 0.2 l/min steps (2) | step |
| $\sigma_{k,f}$ | between-diary coefficient of variation of the peak | % |
| $\sigma$ (B.23) | prefix stratum | - |
| $\tau$ | day type (weekday, Saturday, Sunday) | - |
| $T$, $T_5$ | four- and five-way synthetic-population tables (shares) | - |
| $\bar{T}$ | mean level-1 changes per diary | 1/day |
| $\mathcal{T}_i$ | body-token positions of record $i$ | - |
| $\mathrm{TPR}_{0.001}$ | true-positive rate at 0.1 % false-positive rate | - |
| $\mathrm{TVD}$ | total variation distance | - |
| $u$ | uniform random number | - |
| $u_p$ | quantile of size-matched median DCR | - |
| $V_d$ | daily hot-water volume per dwelling | l/day |
| $\vartheta$ | score threshold at the target false-positive rate | nat/token |
| $w_i$, $w^{\mathrm{cal}}_i$ | diary weight, calendar-re-based weight | - |
| $W_0$ | frozen pretrained weight matrix | - |
| $W_1(a)$ | first-order Wasserstein distance | min |
| $x$, $y$ (B.24) | expected and generated budgets | min/day |
| $x_{iv}$ | category of diary $i$ on variable $v$ | - |
| $z_i(s)$ | activity code of diary $i$ in slot $s$ | - |

## (b) Equation to code to source

| Eq. | Quantity | Code checked against | Source | Vetting status |
|---|---|---|---|---|
| B.1 | level-1 budget | `4thJ_step6_level1.py:151-197, 228-256` | none | uncited |
| B.2 | MAE | `4thJ_step6_level1.py:335-340` | Hyndman and Koehler 2006; Willmott and Matsuura 2005 | ACCEPTED; AAO |
| B.3 | transfer margin, strict rule | `4thJ_step6_rakeddonor.py:206-222`; `4thJ_step6_g61_score.py:148-169` | own | uncited |
| B.4 | cell basis, APE | `4thJ_step6_level1.py:112-117, 143-144, 262-304` | Hyndman and Koehler 2006 | ACCEPTED |
| B.5 | MAPE and 15 % bar | `4thJ_step6_level1.py:305-332` | Hyndman and Koehler 2006 | ACCEPTED |
| B.6 | worst-band rule, paired clause | `4thJ_step6_g66_heldin.py:148-216, 229` | own | uncited |
| B.7 | frozen limitation criteria | `4thJ_step6_g65_g69.py:135-201` | own | uncited |
| B.8 | raking update | `4thJ_step6_rakeddonor.py:169-181`; `4thJ_step6_g61_rake_folds.py:89-103` | Deville and Särndal 1992; Deming and Stephan 1940 | ACCEPTED (existing wording); AAO |
| B.9 | 0.5 pp stopping rule | `4thJ_step6_rakeddonor.py:47-48, 182-193` | own | uncited |
| B.10 | Kish effective sample size | `4thJ_p5_bootstrap_table3.py:86-90` | standard | uncited |
| B.11 | bootstrap replicate margin | `4thJ_p5_bootstrap_table3.py:198-249` | none vetted | uncited |
| B.12 | percentile interval | `4thJ_p5_bootstrap_table3.py:93-106, 247` | none vetted | uncited |
| B.13 | IPF on the joint table, 1e-13 | `4thJ_step5_synthesise.py:223-224, 280-314` | Beckman et al. 1996; Deming and Stephan 1940 | ACCEPTED; AAO |
| B.14 | exogenous day type | `4thJ_step5_synthesise.py:217-218, 720-722` | own | uncited |
| B.15 | largest remainder | `4thJ_step5_synthesise.py:317-330` | Balinski and Young 1982; Lovelace and Ballas 2013 (contrast) | AAO; ACCEPTED |
| B.16 | calendar re-basing | builder not found; `Step2_docs/4thJ_02_harmonisation.md:2205-2250` | none vetted | uncited |
| B.17 | dwell-time W1 | `4thJ_step6_g68_joint.py:272-324, 441-448` | Vallender 1974; Ramdas et al. 2017 | AAO; ACCEPTED (secondary) |
| B.18 | transitions per day | `4thJ_step6_g68_joint.py:327-339` | none | uncited |
| B.19 | TVD | `4thJ_step6_g68_joint.py:342-358` | Levin et al. 2009 | ACCEPTED |
| B.20 | JSD | `4thJ_step6_g68_joint.py:379-416, 467-474` | Lin 1991 | ACCEPTED |
| B.21 | joint-structure budget error | `4thJ_step6_g68_joint.py:366-376, 461-465` | none | uncited |
| B.22 | exponential age tilt | `4thJ_step6_g67_prefixes.py:148-163, 246-256` | own | uncited |
| B.23 | expected budget | `4thJ_step6_g67_prefixes.py:98-145, 257-265` | own | uncited |
| B.24 | OLS slope and R² | `4thJ_step6_g67_score.py:99-112, 162-189` | Montgomery et al. 2012 | AAO |
| B.25 | steering and amplitude clauses | `4thJ_step6_g67_score.py:88-96, 207-229` | own | uncited |
| B.26 | relative discrimination margin | `4thJ_step6_g65_g69.py:204-266` | own | uncited |
| B.27 | Markov comparator | `4thJ_step6_markov_comparator.py:90-166` | Richardson et al. 2008; Widén and Wäckelgård 2010 | ACCEPTED; AAO |
| B.28 | body-token NLL, loss score | `4thJ_step6_privacy_mia.py:153-176, 456` | Shokri et al. 2017; Yeom et al. 2018 | ACCEPTED (context); AAO |
| B.29 | reference-calibrated score | `4thJ_step6_privacy_mia.py:457-458` | own choice | uncited |
| B.30 | rank AUC | `4thJ_step6_privacy_mia.py:109-126` | Hanley and McNeil 1982 | AAO |
| B.31 | TPR at 0.1 % FPR | `4thJ_step6_privacy_mia.py:129-140` | Carlini et al. 2022 | AAO |
| B.32 | perplexity gap | `4thJ_step6_privacy_mia.py:202-207` | own | uncited |
| B.33 | Hamming DCR, NNDR | `4thJ_step6_g613_dcr.py:113-125, 161-183, 294` | Platzer and Reutterer 2021; Park et al. 2018 | ACCEPTED; AAO |
| B.34 | size-matched DCR clause | `4thJ_step6_g613_dcr.py:333-366` | own | uncited |
| B.35 | decoding neutrality | `4thJ_gates_step7.py:245-255, 449-470` | own | uncited |
| B.36 | appliance eligibility | `4thJ_step9_trigger.py:195-233, 286-301, 652-667` | Richardson et al. 2010 | ACCEPTED |
| B.37 | closed-form start probability | `4thJ_step9_trigger.py:338-369, 670-683` | Richardson et al. 2010, Section 2.7 (idea) | ACCEPTED |
| B.38 | iterative rescaling | `4thJ_step9_trigger.py:804-871, 998-1006` | own | uncited |
| B.39 | geometric skip | `4thJ_step9_trigger.py:375-386` | standard | uncited |
| B.40 | cycle length | `4thJ_step9_trigger.py:314-321, 400-433` | none vetted | uncited |
| B.41 | peak hour and peak power | `4thJ_p3_run_campaign.py:52-72`; `4thJ_step9_trigger.py:749-773` | own | uncited |
| B.42 | load-shape R² | `4thJ_gates_step9.py:831-951` | Richardson et al. 2010 | ACCEPTED |
| B.43 | hot-water start probability | `4thJ_step9_trigger.py:670-725, 999` | Jordan and Vajen 2001, Table 1 | ACCEPTED |
| B.44 | hot-water flow | `4thJ_step9_trigger.py:462-499` | Jordan and Vajen 2001, Table 1 | ACCEPTED |
| B.45 | presence fraction | `4thJ_step7_schedules.py:321-353` | own | uncited |
| B.46 | internal gain redistribution | `4thJ_step8_scenario.py:52, 82-98` | IWU TABULA calculator workbook | ACCEPTED (data file) |
| B.47 | heating peak effect and spread | `4thJ_step8_injected.py:714-727`; `4thJ_step8_aggregate.py:140-177` | own | uncited |
| B.48 | LoRA with rank-stabilised scale | `4thJ_step4_thresholds.py:93-98`; `4thJ_step4_train.py:1281-1286` | Hu et al. 2022 | ACCEPTED |
| B.49 | completion-only loss | `4thJ_step4_train.py:182-200, 1513-1514` | standard | uncited |

Counts: 49 equations; 19 carry at least one ACCEPTED citation (8 of these also carry an AAO source), 3 carry
only AAO citations (B.24, B.30, B.31), 27 are uncited. No REJECTED item is cited; Loga et al. (2016) is not
used here because no equation depends on the typology.

## (c) Where the code and the manuscript's current wording disagree (report only; manuscript not edited)

Line numbers refer to `writing/submission/4J_manuscript_submission.md` as read on 2026-09-23, before the
rewrite.

1. **Synthetic-population seed (§3.4, line 310).** The text says the four-way table is fitted "following
   the synthetic-population construction of Beckman et al. (1996)". The frozen primary population starts
   from a uniform seed over structurally admissible cells, with only the 11-14 row shaped by the donor mix
   (`4thJ_step5_synthesise.py:148-182, 670-685`); the donor-seeded table that resembles Beckman's
   sample-seeded construction is a declared sensitivity only. Cite Beckman for IPF onto margins, not for the
   seed.
2. **What the baseline is raked onto (§3.5, line 347; §2.2, line 167; §3.4, line 316).** The text says the
   donor pool is raked onto "the held-out country's own published marginals" and that day type "is not
   raked at all". In code the raking targets are the shares of the synthetic population
   (`4thJ_step6_g61_rake_folds.py:17-27, 89-103`), and the baseline is raked on five variables including
   day type, at the calendar-week shares 5/7, 1/7, 1/7. The "not raked" statement is true only of the
   synthetic population.
3. **Country-discrimination bar (§3.5, lines 366-368).** The text says "by a margin exceeding the
   between-country spread". The code scores the relative margin of Eq. (B.26) against 0.5, with the
   published distance of the contending pair as denominator; the between-country spread is reported only
   (`4thJ_step6_g65_g69.py:204-266`). Table 4 (line 653) already states the code's rule.
4. **Appliance trigger (§3.9, lines 469-471).** The text says "a recorded activity fires an appliance with
   a probability conditioned on that activity". The code uses one constant start probability per appliance
   per eligible minute (Eq. B.37-B.38), eligibility requires an active occupant (at home, not codes 011 or
   012) doing any activity mapped to the appliance's profile, and a running cycle pauses while no occupant
   is active except for cold, laundry and custom appliances (`4thJ_step9_trigger.py:195-233, 400-433`). The
   pause rule is not mentioned in the text.
5. **Secondary activity (§3.9, lines 477-479 against 486-490 and §5.9 line 872).** Lines 477-479 say the
   secondary activity "is used, where coverage allows, to calibrate the conditional probability"; lines
   486-490 say it is "deliberately unused". The trigger never reads it (`4thJ_step9_trigger.py:163-165`).
6. **Calibration of the trigger (§3.9, §5.9 line 859 "After calibration").** The text does not say that
   the closed-form value is rescaled iteratively (6 passes, 2 % tolerance, saturation detection;
   `4thJ_step9_trigger.py:804-871, 1001-1006`). VETTING_RL34 section 1.4 asks for this sentence.
7. **Fictional-country wording (§5.4, lines 711-712 and 721-725).** "Marginals perturbed along an
   exponential tilt": only the age-band mix is tilted (`4thJ_step6_g67_prefixes.py:148-163`). "Direction
   ... coefficients of determination": the R² is that of AC2 alone (Eq. B.25). "Five independent
   conditioning channels": these are the five outcome aggregates other than AC4-8, not conditioning
   channels.
8. **Table 6 quantities (§5.5, lines 751-756).** "Time-budget error, band 8.0 min" is Eq. (B.21), the
   worst of ten first-digit activities against the real held-out diaries, not the six-aggregate MAE of
   Table 3 against published tables. "Dwell-time Wasserstein distance" is the maximum over activities of
   Eq. (B.17) on episode durations (episodes not merged). "Diurnal JSD, band 0.015" is the mean over
   activities of the divergence between time-of-day distributions; the check also requires the maximum to
   be at most 0.025 (`4thJ_step6_g68_joint.py:85-86, 490-491`), which the table omits. The level-1 basis
   here (first digit, unspecified-time codes in digit 9) also differs from Eq. (B.1).
9. **Decoding neutrality (§5.7, lines 820-821).** The text says "the worst stratum off by 101.02, 29.60 and
   48.87 minutes per day". The code takes the worst three-digit activity code, not a stratum
   (`4thJ_gates_step7.py:459-470`).
10. **Markov comparator (§5.5, lines 777-778).** "Reproduces the transition rate almost exactly, at 0.264
    transitions per day against a band of 1.50": 0.264 is the absolute error of Eq. (B.18), not the rate.
    The chain is fitted on unweighted counts (`4thJ_step6_markov_comparator.py:98-110`) and scored on
    weighted metrics.
11. **Budget check bar (Table 4, line 648).** "MAPE at or below 15 per cent" omits the 10 min/day floor
    and the zero-cell rule of Eq. (B.4). The frozen-criteria row (line 649) uses MAPE > 20 % as its second
    criterion (`4thJ_step6_g65_g69.py:102`), which the table does not state; "conjunction ... any one
    triggers" describes a disjunction of failure conditions.
12. **Table 7 (§5.8, lines 829-833).** Peak watts 518 / 395 / 422 do not match the data behind them
    (502.9 / 403.5 / 416.1, per `IMP/impl/P3_appliance_real_and_donor.md`); already scheduled in the brief.
    The peak hour is the hour beginning of the argmax of Eq. (B.41) after rotation to midnight.
13. **Membership attack (§5.6, line 788).** The loss-based attack cites Shokri et al. (2017); VETTING_RL34
    accepts Shokri as general context only and lists Yeom et al. (2018) [AUTHOR TO OPEN] as the
    loss-threshold source. The TPR at 0.1 % FPR clause of the check (`4thJ_step6_privacy_mia.py:12, 87-89`)
    is not stated in the text.
14. **TABULA citation (§2.3 line 185; §3.7 line 398).** Both cite "Loga et al., 2012" (the TABULA Synthesis
    Report) for the workbook. VETTING_RL34 REJECTS that document; the 3.0 W/m² value should cite the IWU
    calculator workbook, and Loga et al. (2016) the typology only.
15. **Adapter scaling (§3.3, line 283).** "Scaling factor 64" is $\alpha$; with rank-stabilised scaling the
    effective factor is $\alpha/\sqrt{r}\approx 11.31$ (Eq. B.48). Not wrong, but a reader may take 64 as the
    multiplier.

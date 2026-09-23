# Appendix B. Supporting equations

This appendix gives the supporting equations of Section 2. They are grouped by the section they
support.

## Diary preparation (Section 2.1)

Each 10-minute diary holds the activity codes `slot_001` to `slot_144` and the at-home indicators
`home_001` to `home_144`. For 30-minute slot $s \in \{1, \dots, 48\}$, the activity code is the
majority vote (mode) of the three underlying 10-minute codes:

$$
\text{act30}_s = \operatorname{mode}\big(\text{slot}_{3s-2},\ \text{slot}_{3s-1},\ \text{slot}_{3s}\big)
\tag{B.1}
$$

Here, $\text{act30}_s$ is the 30-minute activity code, and each $\text{slot}$ term is one 10-minute
activity code. The rare three-way ties are resolved in a separate step.

The 30-minute at-home indicator is set to 1 when at least two of the three underlying slots are at
home:

$$
\text{hom30}_s = \mathbb{1}\!\left[\ \sum_{k=1}^{3} \text{home}_{3(s-1)+k} \ \ge\ 2\ \right]
\tag{B.2}
$$

Here, $\text{hom30}_s$ is the 30-minute at-home indicator, and each $\text{home}$ term is one
10-minute at-home indicator. The indicator $\mathbb{1}[\cdot]$ is 1 when its condition holds and 0
otherwise. The resulting series are `act30_001` to `act30_048` and `hom30_001` to `hom30_048`.

## Generative model and raking (Section 2.2)

The training loss of the generative model sums three per-slot terms over the 48 slots. Two
regularization terms are added:

$$
\mathcal{L} \;=\; \sum_{t=1}^{48}\Big[
\lambda_{\text{act}}\, \ell^{\text{act}}_t
\;+\; \lambda_{\text{home}}\, \ell^{\text{home}}_t
\;+\; \lambda_{\text{cop}}\, \ell^{\text{cop}}_t
\Big]
\;+\; \lambda_{\text{marg}}\, \ell_{\text{marg}}
\;+\; \lambda_{\text{aux}}\, \ell_{\text{aux}}
\tag{B.3}
$$

Here, $\ell^{\text{act}}_t$ is the categorical cross-entropy of the activity head against the
observed activity at slot $t$. $\ell^{\text{home}}_t$ is the binary cross-entropy of the at-home
head. $\ell^{\text{cop}}_t$ is the binary cross-entropy of the 9 co-presence channels. It is masked by
the availability of each co-presence channel for that respondent. For the colleagues channel, it is
zeroed for cycles that do not carry a colleagues category. $\ell_{\text{marg}}$ is a
direction-agnostic penalty on the gap between the model's average at-home rate and the observed
average at-home rate. $\ell_{\text{aux}}$ is a small auxiliary classification loss that predicts the
target day-type stratum from the decoder state. The $\lambda$ weights are fixed training parameters,
not fitted. A logic-consistency penalty between the at-home and co-presence heads and a
transition-rate penalty have zero weight, so they do not enter the trained model.

Raking sets an integer target count for each day-type stratum $s$ and 30-minute slot $t$. The target
at-home rate is $p_{s,t} \in [0,1]$, and $N_s$ diaries share stratum $s$. The target count is

$$
n^{\text{tgt}}_{s,t} = \operatorname{clip}\big(\operatorname{round}(p_{s,t}\, N_s),\ 0,\ N_s\big)
\tag{B.4}
$$

Here, the product is rounded to an integer and clipped to the range from 0 to $N_s$.

The number of records to flip at slot $t$ is the shortfall against the current count of ones:

$$
\Delta_{s,t} = n^{\text{tgt}}_{s,t} - n^{\text{cur}}_{s,t}
\tag{B.5}
$$

Here, $n^{\text{cur}}_{s,t}$ is the current count of ones. If $\Delta_{s,t} > 0$, that many
zero-valued records are flipped to one. If $\Delta_{s,t} < 0$, that many one-valued records are
flipped to zero.

## Household schedules (Section 2.3)

For household $h$, day type $d$ (weekday or weekend) and slot $t$, the fraction of the household at
home is the mean of the members' at-home indicators:

$$
\text{occ48}_{h,d,t} = \frac{1}{M_h}\sum_{m=1}^{M_h} \text{hom30}_{h,d,t}^{(m)}
\tag{B.6}
$$

Here, $M_h$ counts the member diary-days pooled into that day type. Saturday and Sunday records both
enter the weekend mean. The superscript $(m)$ marks one member diary-day.

The household metabolic rate is the mean, over the same records, of a fixed activity-to-watts lookup
applied to each activity code:

$$
\text{met48}_{h,d,t} = \frac{1}{M_h}\sum_{m=1}^{M_h} W_{\text{met}}\!\big(\text{act30}_{h,d,t}^{(m)}\big)
\tag{B.7}
$$

Here, $W_{\text{met}}$ is the fixed activity-to-watts lookup. A fixed default applies to codes without
an entry. Both 48-slot series are then averaged in pairs into 24 hourly values. For hour
$k = 1,\dots,24$, $\text{occ24}_{h,d,k} = \tfrac{1}{2}(\text{occ48}_{h,d,2k-1} + \text{occ48}_{h,d,2k})$.
The metabolic series is averaged in the same way.

## Household sampling (Section 2.5)

Each cell's sample is a simple random sample (SRS) drawn without replacement from its candidate pool:

$$
\text{sample} = \text{SRS}_{\text{without replacement}}(\text{pool}_{\text{cell}},\ N=50)
\tag{B.8}
$$

Here, $\text{pool}_{\text{cell}}$ is the candidate pool of the cell, and $N = 50$ is the number of
households drawn.

## Load-shape metrics and comparison methods (Section 2.6)

The peak hour of day $i$ is $h_i$, with angle $\theta_i = 2\pi h_i / 24$. The circular mean peak hour
is

$$
\bar{h} = \frac{24}{2\pi}\, \operatorname{atan2}\!\Big(\overline{\sin\theta},\ \overline{\cos\theta}\Big) \bmod 24
\tag{B.9}
$$

Here, $\overline{\sin\theta}$ and $\overline{\cos\theta}$ are the means of the sine and cosine of the
angles over the days.

The dispersion is Mardia's circular standard deviation. It uses the resultant length
$R = \sqrt{\overline{\sin\theta}^2 + \overline{\cos\theta}^2}$:

$$
\text{sd}_{\text{circ}} = \frac{24}{2\pi}\sqrt{-2\ln R}
\tag{B.10}
$$

Here, $\text{sd}_{\text{circ}}$ is the circular standard deviation of the peak hour.

For a metric $M$ and two conditions A and B, the paired difference of household $i$ is

$$
d_i = M_i^{(B)} - M_i^{(A)}
\tag{B.11}
$$

Here, $M_i^{(A)}$ and $M_i^{(B)}$ are the values of the metric for household $i$ under conditions A
and B.

The fixed-schedule arm gives every household the same reference schedule:

$$
S^{\text{fixed}}_{h,d,k} = R_{d,k} \qquad \text{for every household } h
\tag{B.12}
$$

Here, $R_{d,k}$ is the fixed reference schedule value for day type $d$ and hour $k$. $S$ is an hourly
schedule value.

# Appendix B. Supporting equations

**Retail presence rule (Section 2.1).** A diary slot is retail presence when the location is a store (location code 5), or when the activity is purchasing goods and services (activity code 4) at location code 5 or 9:

$$R = (L = 5)\ \lor\ \left[(A = 4)\ \land\ (L \in \{5, 9\})\right] \qquad (\mathrm{B.1})$$

where L is the diary location code and A the activity code. The per-cycle code mapping is given in Supplementary Table S3.

**Training loss (Section 2.2).** The three decoder heads share one weighted loss over the 48 slots,

$$\mathcal{L} = \sum_{k \in \{\mathrm{res}, \mathrm{off}, \mathrm{ret}\}} w_k\, \frac{1}{48} \sum_{t=1}^{48} \ell_k(t), \qquad w_{\mathrm{res}} = 1.0,\ w_{\mathrm{off}} = 0.5,\ w_{\mathrm{ret}} = 0.3 \qquad (\mathrm{B.2})$$

where ℓ_k is the binary cross-entropy of head k. For the retail head, the positive class carries a weight of 49. Its logit z is shifted at inference so that the decoded probability is not inflated by that weight:

$$p_{\mathrm{ret}}(t) = \sigma\!\left(z(t) - \ln 49\right) \qquad (\mathrm{B.3})$$

Weighting the positive class in the loss is equivalent to over-sampling it by the same factor, and the prior correction for such sampling subtracts the logarithm of that factor from the logit (King and Zeng, 2001). The same logit adjustment is given in general form for long-tailed classification by Menon et al. (2021).

**Exclusivity step (Section 2.2).** In each slot, the heads whose probability reaches their threshold are candidates, and the slot is assigned to the candidate with the largest threshold-normalised probability:

$$k^{*}(t) = \arg\max_{k:\ p_k(t) \ge \tau_k} \frac{p_k(t)}{\tau_k} \qquad (\mathrm{B.4})$$

with τ_res = 0.50, τ_off = 0.40 and τ_ret = 0.15. A slot with no candidate is assigned to no channel.

**Lighting and equipment schedules (Section 2.4).** In office, retail and guest-room spaces, the lighting and plug-load schedule that replaces a prototype schedule keeps that schedule's standby floor φ:

$$f(t) = \varphi + (1 - \varphi)\, o(t) \qquad (\mathrm{B.5})$$

where o(t) is the injected occupancy fraction.

**Energy use intensity (Section 2.6).** For channel c, on the two floor-area bases,

$$\mathrm{EUI}^{\mathrm{CFA}}_c = \frac{E_c}{A^{\mathrm{CFA}}_c}, \qquad \mathrm{EUI}^{\mathrm{GFA}}_c = \frac{E_c}{f_c\, A^{\mathrm{GFA}}} \qquad (\mathrm{B.6})$$

**Circular-mean peak hour (Section 2.6).** For an average weekday profile P(h), the load-weighted circular mean hour is

$$\bar{h} = \frac{24}{2\pi}\, \operatorname{atan2}\!\left(\sum_{h} P(h) \sin\frac{2\pi h}{24},\ \sum_{h} P(h) \cos\frac{2\pi h}{24}\right) \bmod 24 \qquad (\mathrm{B.7})$$

**Midday-to-night ratio (Section 2.6).**

$$\rho = \frac{\overline{P}_{11\text{-}14\,\mathrm{h}}}{\overline{P}_{22\text{-}04\,\mathrm{h}}} \qquad (\mathrm{B.8})$$

where each bar is the mean weekday demand over the stated hours.

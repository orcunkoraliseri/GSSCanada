# 1. Introduction

## 1.1 Background

Occupant behaviour is a major source of the gap between predicted and measured building energy use [REF NEEDED: review on occupant behaviour and the performance gap]. The field has responded with detailed occupancy models for single uses. These include Markov-chain, survival and time-use-survey models that reproduce the presence of one population in one building type [REF NEEDED: two or three representative single-use occupancy models].

Tall mixed-use buildings do not fit that pattern. A single tower can hold households on some floors, an office workforce on others, shops at grade and hotel guests in a separate block. All of them share one envelope and often one central plant. In common practice, one schedule is chosen for such a model, usually residential or office. The remaining uses keep their code-default schedules.

These populations are not interchangeable. Households, workers, shoppers and overnight guests keep different hours and respond to different drivers. Commuting, retail footfall and tourism demand each follow their own trend. They are also observed by different data sources, when they are observed at all. A tower model that carries one of them well and holds the others at a default therefore describes most of its floor area with schedules written for another population.

Knowing who is in a tower, and when, matters for more than annual energy. Central plant sizing, shared-system operation and the building's contribution to district and grid peaks all depend on how the uses overlap in time [REF NEEDED: sources linking mixed-use load diversity to plant sizing and grid peak]. Whether a better occupancy model changes that overlap is an open, testable question.

## 1.2 Existing work and the gap

Two lines of work bear on this problem, and they rarely meet. The first builds time-use-survey occupancy models with a behavioural basis, but for one residential population. Buttitta and Finn (2020) used a national time-use survey to generate high-resolution residential occupancy for heating-load profiles. Widén and Wäckelgård (2010) did the same from a single wave of the Swedish time-use survey. Neither extends the method to a second use or to a future year.

The authors' own prior work belongs to this first line. It built survey-grounded residential occupancy for Canada from successive General Social Survey cycles and carried it into building energy simulation (a companion journal manuscript, in revision; Iseri and Hachem-Vermette, 2026). A related study carried the same residential line through the pandemic to 2030 scenarios and examined the daily load shape (a second companion journal manuscript, in revision). All of this work models one use.

The second line models several uses together, but not from a time-use survey and not inside one building. Doma and Ouf (2023) and Doma et al. (2024) modelled office, retail and residential occupancy from mobile-positioning data at district scale. Each use sat in a separate building, and no future year was modelled. The closest study therefore differs from the present one in its data source, its scale and its time horizon.

Appendix A (Table A.1) scores these studies on eight axes. None combines a time-use-survey behavioural model, more than one occupancy channel, a future-year scenario and a single mixed-use building. The present study fills that combination.

## 1.3 Non-stationary behaviour per use

The authors' residential work found that occupant behaviour changed through the pandemic and the shift to working from home. A schedule anchored to a pre-pandemic baseline therefore misjudged both how much energy was used and when. A mixed-use tower adds a further complication. Each use follows its own trend, and the trends need not move together.

Lower office presence is associated with the persistence of hybrid and remote work. Lower retail presence is associated with a longer shift towards online shopping. The weighted share of diary time spent in shopping locations falls by about 25 % across the four survey cycles used here. Hotel presence follows neither trend. It collapsed during the pandemic and recovered along a provincial tourism path. Hotel guests are also outside the survey's sampling frame, so their presence must come from another source. A single occupancy trend, rescaled and reused for four uses, would misstate at least some of them in direction, timing or both.

## 1.4 Aim and contributions

This paper asks what changes in a mixed-use tower when each of its four uses carries its own survey-based occupancy schedule instead of a code schedule. It also asks where single-use reference intensity ranges can still judge the result. The comparison is made on the same two towers run once on code schedules and once on the survey-based schedules.

The paper makes three scientific contributions. First, one jointly trained model generates residential, office and retail presence from four survey cycles, and a separate time-series model generates hotel presence from tourism statistics. All four are routed into the spaces of one tower model. Second, a like-for-like comparison with the code-schedule tower separates what survey-based occupancy changes from what it does not. It changes who is in the tower and when, and it changes office and retail energy, where lighting and equipment follow occupancy. It leaves whole-building load timing and coincidence where the plant start-up and equipment schedules put them. Third, the paper shows where single-use intensity ranges cannot judge the uses of a stacked tower. The code-schedule tower itself falls below the office range, and the hotel verdict splits by tower prototype.

The paper also makes two practical contributions. First, for plant sizing and peak studies in towers of this kind, the building peak is set by plant start-up and equipment schedules, not by occupancy detail. Effort aimed at the peak should therefore go to those schedules. Second, for tenant-level energy, survey-based schedules change office and retail intensity against code schedules by 7 to 10 %. That difference matters for tenant sub-metering and benchmarking.

Section 2 sets out the framework, and Section 5 states its limitations.

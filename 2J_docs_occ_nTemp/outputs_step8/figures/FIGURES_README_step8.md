# Step 8 — Figure Guide

This document describes each figure in `outputs_step8/figures/`. Each figure is intended for the journal publication. The text below explains *what each figure shows, what it is for, and how it should be read* — it deliberately avoids quoting specific numbers, since those depend on the simulation run and can change between versions.

---

## fig01 — Occupancy driver: diurnal at-home shift

This figure shows the average fraction of households at home across the hours of the day, split into a weekday panel and a weekend panel, with a separate line for each survey/forecast cycle. It is the behavioural starting point of the whole analysis: before any energy is simulated, the occupancy schedules themselves must change for the downstream loads to change. The shaded mid-day band marks the working-from-home window, the part of the day where remote work would be expected to keep more people at home. Reading the panels, the deepest part of each curve is the mid-day "everyone out" trough on a normal day; the more recent cycles sit higher through that trough, which is the visual signature of a flattening daytime absence. This figure exists to justify the rest of the study — it demonstrates that the occupancy inputs genuinely carry the behavioural signal we then trace into electricity demand.

## fig02 — Diurnal electricity load: representative archetype/city

This figure shows the average hourly electricity demand over a day for a single representative archetype-and-city combination, comparing the most recent observed cycle against the forecast cycle, each drawn with a shaded uncertainty band. It is the cleanest single view of how a typical dwelling's daily load curve is expected to evolve. The reader should follow the overall shape: a low overnight base, a gentle daytime rise, and a pronounced evening peak. Comparing the two lines and the overlap of their bands tells you whether the projected change in the daily profile is large relative to the spread across households, or whether it is a subtle reshaping inside the existing envelope. It is meant as the intuitive, "one curve" anchor before the more disaggregated figures.

## fig02b — Diurnal electricity by archetype

This figure breaks the daily electricity profile out into one panel per building archetype (single-detached, other dwelling, mid-rise, and high-rise), again comparing the recent cycle against the forecast with uncertainty bands. Its purpose is to show that the daily load shape and its magnitude are strongly archetype-dependent — larger and multi-unit buildings carry very different absolute loads and slightly different curve shapes than single dwellings. Read it by comparing panels to each other for the differences in scale and shape, and by comparing the two lines within each panel for the projected change specific to that building type. It guards against over-generalising from any single archetype and shows where the behavioural shift lands hardest.

## fig03 — Peak-hour shift

This figure pairs a histogram of the hour at which each dwelling's daily demand peaks with a circular (clock) plot of the mean peak hour, comparing the recent cycle against the forecast. It is designed to answer a focused question: *when* does the day's maximum demand occur, and does that timing move between cycles? The histogram shows how tightly peaks cluster around the evening and whether the distribution broadens or shifts; the clock dial summarises the same information as a single direction, making any movement in the typical peak hour easy to see at a glance. This figure isolates timing from magnitude, which matters for grid and capacity questions that care about coincident demand more than total energy.

## fig04 — Paired within-household Δ load by hour

This figure shows the average hour-by-hour *difference* in electricity demand between the forecast cycle and the recent cycle, computed as a paired within-household change, with a confidence band around the mean difference. Because the comparison is paired (the same household under both scenarios), it removes household-to-household variability and exposes the systematic shift attributable to the behavioural change alone. Read it relative to the zero line: hours where the band sits clearly above zero are hours that gain load, hours straddling zero are unchanged, and the mid-day working-from-home window is highlighted to show where any daytime gain concentrates. This is the most statistically careful view of *which hours are responsible* for the change.

## fig05 — Diurnal load by season

This figure is a grid of daily load curves organised by season (heating, shoulder, cooling) across the columns and by load component (whole-building electricity, heating load, cooling load) down the rows, comparing the recent cycle against the forecast. Its purpose is to separate behaviour-driven electricity from weather-driven thermal demand and to show that the two respond differently across the year. The reader should compare across columns to see seasonal effects and down rows to see how the behavioural shift expresses itself in fuel-neutral electricity versus in the underlying thermal zone loads. The row labels distinguish zone thermal load from delivered fuel, which is important for interpreting the heating- and cooling-load panels correctly.

## fig06 — Annual electricity carpet

This figure is a "carpet" heatmap of electricity demand with day-of-year on the horizontal axis and hour-of-day on the vertical axis, shown as two side-by-side panels (recent cycle and forecast) on a shared colour scale. It compresses the full annual hourly time series into a single image so seasonal and diurnal structure can be seen together. Read it by scanning vertically for the daily pattern (the bright evening band) and horizontally for the seasonal envelope (the brighter summer/cooling region). Comparing the two panels reveals whether the forecast redistributes demand across the day or the year. It is the most information-dense figure and works as a qualitative overview rather than a precise quantitative read.

## fig07 — Paired Δ peak demand by archetype × climate zone

This figure is a heatmap of the paired change in peak demand between the forecast and recent cycles, with building archetypes on one axis and climate zones on the other, and a diverging colour scale centred on zero. Its job is to show *where* the peak-demand change is concentrated across the building-stock-by-geography matrix, rather than reporting a single average. The reader should look for which cells are coloured (and in which direction) versus which are near-neutral, and note that the largest-magnitude cells tend to be the larger multi-unit archetypes where absolute loads are highest. The diverging colours make the sign of each change immediately legible, distinguishing cells that gain peak from cells that shed it.

## fig08 — Stock-weighted ensemble load shape and coincidence factor

This figure shows the stock-weighted ensemble daily load shape — every archetype and city combined in proportion to its share of the building stock — for the recent cycle and the forecast, with the coincidence factor annotated for each. It moves the analysis from the individual dwelling up to the aggregate-system level, which is the scale a utility or grid planner cares about. Read the curves for how the *fleet* load shape changes, and read the coincidence factor as the measure of how synchronised individual peaks are when summed: a higher coincidence factor means peaks line up more and the aggregate peak is sharper. This figure connects the household-level behavioural story to system-level consequences.

## fig09 — Longitudinal load-shape trajectory

This figure tracks four summary load-shape metrics (mid-day energy share, load factor, peak-to-average ratio, and mean peak hour) across all cycles from the earliest to the forecast year, each in its own panel with error bars, and a marked break indicating the COVID disruption. Its purpose is to place the recent-to-forecast comparison in a longer historical trajectory, so the reader can judge whether the projected change continues a pre-existing trend or represents a departure from it. Read each panel as a time series and check whether the points drift monotonically, flatten, or turn around the marked break. It frames the headline comparison as one step in a multi-cycle evolution rather than an isolated jump.

## fig10 — Annual EUI by archetype × city

This figure is a grouped bar chart of annual energy use intensity for every archetype-and-city combination, with paired bars for the recent cycle and the forecast and error bars on each. It is the annual-total, bottom-line accounting view: after all the diurnal and seasonal reshaping, does the total energy per unit floor area actually change, and for which segments. Read it by comparing the paired bars within each labelled group and by scanning across groups to see how intensity varies with archetype and climate. Because it reports an annual integral rather than a shape, it is the right figure for the question "does the behavioural shift move total consumption, or only redistribute it within the day?"

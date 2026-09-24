Your last round worked: both clash checks end at 0, Figure 1 is finished, and the graphical abstract is much cleaner. Do not touch Figure 1 again. Three small problems are left in the graphical abstract, and your clash check cannot see two of them. Fix only what is below. Change no label wording, number, colour, marker position or arrow. Never set a font below 7 pt.

Script: C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\tools\generate_4J_graphical_abstract_eb.py

## Step 0: widen the clash check first

Add two rules to `run_clash_check`:
1. Text touching a drawn line or arrow: for every text object, test its window extent against every `Line2D` in `ax.lines` (sample points along each segment) and every `FancyArrowPatch`. Report `Text '<text>' touches line`.
2. Text too close to the canvas edge: report every text object whose box is closer than 2 pt to any canvas edge.

Run the widened check on the script AS IT IS NOW and paste the output. It must report at least:
- the label "1.1" touching the vertical reference line at 1,
- the title "For building energy models: appliance timing" closer than 2 pt to the top edge (it is about 0.9 pt),
- the title "Result: the model does not beat reweighting" closer than 2 pt to the top edge (about 1.6 pt).
If it does not report these three, the new rules are broken; fix them first.

## Fixes

A. Centre panel: the vertical reference line at 1 runs through the "1.1" label. Move "1.1" to the right of its dot (as you did for "3.9") so it touches neither the line nor any dot.

B. All three panel titles: keep every title at least 2 pt below the top edge. Lower them or tighten the space under them; do not shrink the font.

C. Right panel: the title "For building energy models: appliance timing" and the subtitle "Evening appliance electricity peak, by diary source" sit 0.6 pt apart in the same bold style, so they read as one four-line title. Leave at least 3 pt between them and set the subtitle in normal weight (not bold), same size. If you need room, move the three diary rows and the hour axis down slightly; the marker hours stay exactly as they are.

## Report back

1. The widened clash check output on the script as it is now (Step 0).
2. The widened clash check output after the fixes; it must end `CLASH CHECK: 0 problems`.
3. The font check printout.
4. One line per item A to C saying what you changed.
Do not change the manuscript, Figure 1 or any other file.

You made two figures for a journal paper with matplotlib scripts. Both need fixes before they can be submitted. Edit the scripts, re-run them, and overwrite the same output files. Change nothing that is not listed here. Do not change any label text, number, colour or arrow direction except where a fix below says so.

Scripts:
- Figure 1: C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\writing\submission\figures\scripts\generate_fig01_workflow.py
- Graphical abstract: C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\tools\generate_4J_graphical_abstract_eb.py

## Fix 1, both figures: text is far too small at print size

The journal prints Figure 1 at 14 to 19 cm wide and the graphical abstract at 13 cm wide. Both canvases are 20 inches (50.8 cm) wide with 8.5 to 14 pt fonts, so at print size the text shrinks to about 2.5 to 4.5 pt. The rule is at least 7 pt at print size.

- Figure 1: set the canvas to 7.5 x 4.5 inches (19 cm wide). Every font must be at least 10 pt on that canvas (so it is still about 7.4 pt when shown at 14 cm). Resize boxes so every label fits inside its box with padding. Keep 1000 dpi for the PNG and keep the vector PDF.
- Graphical abstract: set the canvas to 5.12 x 2.05 inches (13 x 5.2 cm). Every font must be at least 7 pt on that canvas. Export the PNG at a dpi that gives at least 1328 pixels wide (use 600 dpi). If a label does not fit at 7 pt, shorten the layout or remove that label; never shrink a font below 7 pt.
- After re-running, print for each figure: canvas width in cm, the smallest font size used, and that font size scaled to print width (font_pt x print_width_cm / canvas_width_cm). Every scaled value must be 7 pt or more.

## Fix 2, graphical abstract, left panel: the two methods must run side by side, not one after the other

Now the arrows go Spain and Italy -> language model -> reweighted real diaries -> scored. That is wrong: it says the reweighting happens after the model. The two methods are separate and parallel.

Correct flow: the Spain and Italy tiles feed BOTH boxes. The dark navy box "Fine-tuned language model" and the grey box "Real diaries of the other two" sit side by side (or one above the other with separate arrows). Each box has its own arrow into the box "Scored against the held-out country's published tables". There is no arrow between the model box and the real-diaries box.

## Fix 3, graphical abstract, right panel: Italy and UK reweighted peaks must sit exactly at 21:00

In the "Reweighted diaries" row the script places Italy at 20.85 and UK at 21.15 to avoid overlap. That moves measured values. Put both markers at exactly 21:00. Separate them vertically (one marker slightly above the row line, one slightly below) and keep their IT and UK labels readable. The Spain marker stays at 19:00.

## Fix 4, graphical abstract, centre panel

Draw the vertical reference line at 1 as a solid line (it is dashed now). Keep all nine dot positions exactly as they are.

## Report back

List each fix and what you changed. Paste the printed font check from Fix 1. Do not change the manuscript or any other file.

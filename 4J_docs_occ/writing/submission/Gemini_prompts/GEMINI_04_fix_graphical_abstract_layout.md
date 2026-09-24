Your last round fixed what was asked: font sizes, the parallel methods, both reweighted peaks at 21:00, and the solid reference line. Keep all of that. The smaller canvas created new clashes where text runs into other text, markers or the edge. Fix only the items below. Change no label wording, number, colour, marker position or arrow direction unless an item says so. Never set a font below 7 pt.

Scripts:
- Graphical abstract: C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\tools\generate_4J_graphical_abstract_eb.py
- Figure 1: C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\writing\submission\figures\scripts\generate_fig01_workflow.py

## Step 0, before any fix: an automatic clash check

Add a function to BOTH scripts that runs after drawing and before saving. It draws the canvas, takes the window extent of every text object, every box patch and every scatter marker, and prints:
- every pair of text objects whose boxes overlap,
- every text object that overlaps a marker or a box it is not written inside,
- every text object that reaches outside the canvas,
- every box label whose text sits closer than 2 pt to its own box edge.
It ends with one line: `CLASH CHECK: N problems` (0 means clean).

Run it on the scripts AS THEY ARE NOW, before changing anything, and paste that output. It must report at least the overlapping hour labels and the cut-off "22:00" in the graphical abstract. If it reports nothing there, the check is broken; fix the check first.

## Graphical abstract fixes

A. Right panel, hour axis: the labels 12:00 to 22:00 run into each other and "22:00" is cut off at the right edge. Keep the ticks at 12, 14, 16, 18, 20, 22. Write the labels as 12, 14, 16, 18, 20, 22 (no ":00") and put the word "hour" once, small, at 7 pt or more, where it clashes with nothing. Every label must be fully inside the canvas.

B. Right panel: the subtitle "Evening appliance electricity peak, by diary source" runs into the UK, IT and ES labels above the "Real diaries" row. Make vertical room (move the subtitle up or the three rows down) so nothing touches.

C. Right panel: the row names "Generated diaries" and "Reweighted diaries" run over the start of their row lines and almost touch the Spain 14:00 marker. Start the row lines and the hour axis a little further right, or narrow the row-name column, so row names touch no line, marker or label. Marker hours stay exactly as they are (Real: UK 18, IT 19, ES 21; Generated: ES 14, IT 18, UK 20; Reweighted: ES 19, IT 21, UK 21).

D. Centre panel: the label "reweighted real diaries" runs over the top Spain dot. Move the label so it touches no dot. The nine dot x positions stay exactly as they are.

E. Centre panel: the axis title "Model error / reweighted-diary error" runs past the divider line into the right panel. Break it into two lines, or otherwise keep it inside the centre panel.

F. Left panel: the "UK (held out)" text touches the dashed border of its tile. Make the tile big enough that the text has clear space inside it.

G. Left panel: the right-hand drop arrow into "Real diaries of the other two" sits directly under the UK tile, so it can read as if UK diaries feed that box. They do not. Move that drop arrow left so it sits under the Italy tile or the gap between Italy and UK, still landing on the grey box. The UK tile must have no line under it.

## Figure 1 fix

H. Row 3: the text in the three middle boxes ("Occupancy-based internal gains", "Activity-triggered appliance loads", "Domestic hot water draws") nearly touches the top and bottom box edges. Make these boxes taller (shrink the gaps between them if needed) so each label has clear space inside. Keep the 10 pt font and all arrows as they are.

## Report back

1. The clash check output on the old scripts (Step 0).
2. The clash check output on the fixed scripts; it must end `CLASH CHECK: 0 problems` for both.
3. The font check printouts from both scripts (same format as last round).
4. One line per item A to H saying what you changed.
Do not change the manuscript or any other file.

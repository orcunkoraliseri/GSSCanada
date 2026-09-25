# Supplementary Figure S5 (one channel per time slot), FINAL prompt v5, 2026-09-25

Replaces the S5 block in `SI_schematics_redraw.md` and its "S5 fix round 2". This file is complete on its own.
Paste ONLY the block under "Prompt to paste" into Gemini, in ONE message, nothing added.
Save the result as `Figure_04_exclusivity_projection.png` in `writing/submission/figures/` (same name, the build picks it up).

## What went wrong last time, and how this prompt prevents it

- Last image: all three bars were above their dashed thresholds, but only teal was kept. By the paper's rule
  (Appendix B, Eq. B.4: among heads above their own threshold, keep the one furthest above it) the grey bar
  would have won, so the picture contradicted the text.
- Fix: the prompt fixes every bar height and every threshold height as a number on a 0 to 10 scale, so only
  teal is above its threshold. With only one candidate, the result cannot be misread.

## Prompt to paste

```
Draw a clean, flat, 2D explanatory diagram for a scientific journal. White background. No 3D, no perspective, no shadows, no gradients, no clip art, no axes, no gridlines. Sans-serif font (Arial or Helvetica), dark grey text (#333333), all text horizontal. Landscape, 16:9, at least 3600 x 2025 pixels.

COLOURS (use only these): bar 1 slate blue #4F6D8F, bar 2 teal #2A9D8F, bar 3 warm grey #A39A8E, centre box amber #E8B04B with dark text, arrows and dashed marks dark grey #444444.

THREE ZONES, left to right, each about one third of the width:

LEFT ZONE. Heading at the top, two lines, centred: "Three head probabilities," / "one time slot".
Below it, three wide vertical bars standing on one common invisible baseline, evenly spaced, same width, in this order left to right: slate blue, teal, warm grey.
Heights on a scale where 10 is the tallest possible bar:
- slate-blue bar: height 5. Its dashed threshold mark is at height 7, so the bar top is clearly BELOW its mark, with a visible white gap between the bar top and the dashed mark.
- teal bar: height 9. Its dashed threshold mark is at height 4, so the bar clearly passes its mark.
- warm-grey bar: height 3. Its dashed threshold mark is at height 6, so the bar top is clearly BELOW its mark, with a visible white gap.
Each dashed threshold mark is a short horizontal dashed line exactly as wide as its own bar, centred on its own bar, never reaching a neighbouring bar.

CENTRE ZONE. One amber rectangle with the text on three lines: "Compare each head" / "with its own" / "threshold". One arrow comes into its left edge from the left zone; one arrow leaves its right edge toward the right zone.

RIGHT ZONE. Heading at the top, two lines, centred: "At most one channel" / "per slot".
Below it, the same three bar positions and colours as the left zone, on the same baseline height:
- slate blue: a thin flat line at height 0 (just a short thick line on the baseline).
- teal: a full bar at height 9, same as on the left.
- warm grey: a thin flat line at height 0.
No dashed marks in the right zone.

TEXT: the only words in the image are the ones in quotation marks above. No numbers, no percentages, no axis labels, no legend, no title, no footnote, no notes, no colour names, no abbreviations.
```

## Check before saving (author, 30 seconds)

1. Left zone: ONLY the teal bar goes past its dashed mark. The blue and grey bar tops sit visibly BELOW their own dashed marks.
2. Each dashed mark covers only its own bar.
3. Right zone: teal full height, blue and grey flat on the baseline, no dashed marks.
4. No numbers anywhere; only the three text items.
If any check fails, regenerate with the same prompt.

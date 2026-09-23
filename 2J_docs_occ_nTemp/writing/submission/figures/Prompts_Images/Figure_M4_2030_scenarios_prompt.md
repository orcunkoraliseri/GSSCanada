# Method figure M4: how the three 2030 scenarios are built (image prompt)

Paste the prompt below into Gemini. This file is a prompt only; no image is created here.
Save the result as `Figure_M4_2030_scenarios.png` in `submission/figures/`.
It explains Eq. 10 of the Methods section. Final figure number is set when the paper is renumbered.

This is a concept sketch with NO values on the vertical axis. If the author prefers a version drawn
from the paper's real numbers, say so: that one is a data plot made by script, not an image prompt.

## Prompt to paste

Draw a simple, clean scientific concept chart for a journal article in Applied Energy. It explains how
three future scenarios for the year 2030 are built from past survey years. It is a sketch, not a data
plot: the vertical axis has no numbers.

Style: white background, flat design, thin dark-grey axes, sans-serif text (Arial or Helvetica), one
font size for labels. Colour-blind-safe line colours: dark grey for the past trend, blue, green and
orange for the three scenarios. No icons, no 3D, no shadows, no gradients, no logos, no title inside the
image. Landscape, about 190 mm wide by 90 mm tall, at least 600 dpi.

Axes:
- Horizontal axis labelled "Year", with ticks and labels at 2005, 2010, 2015, 2022 and 2030 only,
  spaced in proportion to the years.
- Vertical axis labelled "Share of time at home", with no numbers and no tick labels.

Content:
1. Three dark-grey dots at 2005, 2010 and 2015, lying almost on a straight line that rises slowly.
   A solid dark-grey straight line through them, labelled "Pre-pandemic trend".
2. The same line continues as a dashed dark-grey line from 2015 to 2030.
3. One black dot at 2022, clearly above the dashed trend line. A vertical bracket between the dashed
   line and the 2022 dot, labelled "2022 jump".
4. Three scenario lines start at the 2022 dot and end at 2030:
   - Blue line, ending above the dashed trend by the full height of the 2022 jump (it runs parallel to
     the trend), labelled "Keep all of the jump".
   - Green line, ending above the dashed trend by half the height of the 2022 jump, labelled
     "Keep half of the jump".
   - Orange line, ending exactly on the dashed trend line at 2030, labelled "Back to the trend".
   Put each label at the right end of its line, outside the plot area if needed.

Use these exact label texts, word for word. No other text anywhere in the image.

Must not:
- No numbers on the vertical axis, no percentages, no data values.
- No abbreviations or symbols (no lambda, slope, jump symbols, WFH, GSS).
- No word "forecast". No legend box (labels sit on the lines).

## Acceptance checklist (author, after generating)

- Year ticks only at 2005, 2010, 2015, 2022, 2030; vertical axis has no numbers.
- The blue line is parallel to the dashed trend; the green line ends halfway between blue and the
  trend; the orange line ends on the trend.
- Every label spelled exactly as listed.
- Readable without zooming at 190 mm width.

## Draft caption (one sentence, per the author's caption rule)

Figure M4. Construction of the three 2030 scenarios from the pre-pandemic trend and the 2022 jump.

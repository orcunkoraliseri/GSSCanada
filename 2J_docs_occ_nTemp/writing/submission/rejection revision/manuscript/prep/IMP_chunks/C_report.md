# C (Results, Section 3) report

- Words (wc -w): before 2962, after 3093. The count rose because the caption details now sit in the
  text, and because long sentences were split into short ones.
- Sentences over 30 words: none. The script flagged some, but each was a heading or a figure line
  joined to the next sentence by the splitter.
- Numbers dropped or changed: none. A machine diff shows only punctuation differences, plus the
  planned figure, section and table renumbering. "09:00-17:00" (Section 3.6) is now "09:00 to 17:00".
  Some caption facts now appear twice, once in the text and once in the short caption. Example:
  "2022 versus 2030" for Figure 7.

## Cross-references changed
- Figures: 2->6, 3->7, 4->8, 5->9, 6->10, 7->11, 8->12.
- Section 2.5->2.3 (3.1, 3.4); 2.7->2.5 (3.1, twice); 2.9->2.5 (3.1); 2.10->2.6 (3.4, 3.5, 3.6);
  2.12->2.6 (3.5). In 3.1, "Section 2.5, Section 2.9" became "Sections 2.3 and 2.5".
- Table 2->Table 1 (3.6).
- In 3.2, "and in Figure 4" became "and in the scenario load shapes of Section 3.4". This keeps the
  first citations in number order.

## Layout and caption changes
- Every caption is now one short sentence. All details cut from a caption are in the paragraph that
  cites the figure: the 144,465 frame, the control matching 2022 by construction, Panels A and B,
  the 1,198 common households, the load-factor error bar, the paired-difference error bars, the
  twelve groups and the four metrics.
- 3.1: Figure 6 was first cited in the opening paragraph. That citation moved into a short new
  paragraph after the noon values, so the figure sits between the noon paragraph and the whole-day
  paragraph.
- 3.3: the "(Figure 3)" mention was moved out of paragraph 1. Figure 7 is now cited at the end of
  the per-dwelling paragraph. The SHEU and energy use intensity paragraph follows the figure.
- 3.4: the load-shape paragraph (Figure 8) now comes first. The load factor and midday share
  paragraph comes next. Then the peak and ramp paragraph, which now cites Figure 9 (never cited
  before). Then the heatmap paragraph (Figure 10). There is a paragraph between every two figures.
  Only the paragraph order changed; the text of each paragraph is the same.
- 3.5: the Figure 11 sentence became its own short paragraph before the figure.
- 3.6: Figure 12 now sits between the measured-data paragraph and the "two further checks"
  paragraph.
- Removed: "This restriction is stated once here rather than repeated at every number below"
  (a process note). It became "All numbers below refer to this common set." Also removed: "rather
  than repeated here" (3.6).

## Doubts
- In 3.4, the load-shape paragraph now opens the subsection, which changes the reading order. The
  other way to keep the figures cited in order would be to cite Figure 8 earlier.

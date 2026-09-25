This is the LAST round on the graphical abstract. Every value below was already tested on a copy of the script: with these exact edits, every label sits at least 1 pt away from every other drawn object, and the picture is clean. Your job is to apply them exactly, run the checks, copy the files, and stop.

Hard rules:
- Do NOT search for positions, do NOT write exploration or scratch scripts, do NOT try other values. Apply the edits below exactly as written.
- Change no wording, number, colour, font size, font weight or data value. Never set a font below 7 pt.
- Do not touch Figure 1, the manuscript, or any file not named here.
- If a result differs from what is written under "Expected", do NOT try to fix it. Paste the output and stop.

Script: C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\tools\generate_4J_graphical_abstract_eb.py

## Why a new check

The current check only catches text that TOUCHES something. The problems left are near-touches: "3.9" is 0.1 pt from the panel divider, the italic footer "Each country held out in turn." sits on the bottom rule, the right-panel subtitle is 0.2 pt above the UK/IT/ES labels, the axis numbers touch their tick marks and nearly touch the axis title. A 1 pt gap rule catches all of them.

## Step 1: add the gap check (before any layout edit)

Paste this function into the script directly after the `run_clash_check` function, and add the line `run_clearance_check(fig, ax, boxes, markers, box_of_text)` directly after the existing CALL `run_clash_check(fig, ax, boxes, markers, box_of_text)` near the bottom of the script (about line 370; not the `def run_clash_check(...)` line). No new imports are needed.

```python
def run_clearance_check(fig, ax, boxes, markers, box_of_text, min_gap=1.0, min_edge=2.0, min_pad=2.0):
    """Every text keeps >= min_gap pt from every other text, line, arrow, box and marker;
    >= min_edge pt from the canvas edge; >= min_pad pt inside its own box."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    k = 72.0 / fig.dpi
    cw, ch = fig.bbox.width, fig.bbox.height

    def bb_gap(a, b):
        dx = max(b.x0 - a.x1, a.x0 - b.x1, 0)
        dy = max(b.y0 - a.y1, a.y0 - b.y1, 0)
        return np.hypot(dx, dy) * k

    def seg_gap(bb, p0, p1, lw):
        ts = np.linspace(0, 1, 400)
        pts = p0 + np.outer(ts, p1 - p0)
        dx = np.maximum(np.maximum(bb.x0 - pts[:, 0], pts[:, 0] - bb.x1), 0)
        dy = np.maximum(np.maximum(bb.y0 - pts[:, 1], pts[:, 1] - bb.y1), 0)
        return max(np.hypot(dx, dy).min() * k - lw / 2.0, 0)

    def name(t):
        return t.get_text().replace("\n", " ")[:40]

    problems, smallest = [], 1e9
    T = ax.texts
    for i, t in enumerate(T):
        tb = t.get_window_extent(r)
        gaps = []
        for u in T[i + 1:]:
            gaps.append((bb_gap(tb, u.get_window_extent(r)), f"text '{name(u)}'", min_gap))
        for ln in ax.lines:
            d = ax.transData.transform(np.column_stack(ln.get_data()))
            g = min(seg_gap(tb, d[j], d[j + 1], ln.get_linewidth()) for j in range(len(d) - 1))
            gaps.append((g, "a drawn line", min_gap))
        for p in ax.patches:
            if isinstance(p, FancyArrowPatch):
                gaps.append((bb_gap(tb, p.get_window_extent(r)), "an arrow", min_gap))
        for p, bname in boxes:
            pb = p.get_window_extent(r)
            if box_of_text.get(t) is p:
                pad = min(tb.x0 - pb.x0, pb.x1 - tb.x1, tb.y0 - pb.y0, pb.y1 - tb.y1) * k
                gaps.append((pad, "its own box edge", min_pad))
            else:
                gaps.append((bb_gap(tb, pb), f"box '{bname[:20]}'", min_gap))
        for sc, mname in markers:
            path = sc.get_paths()[0]
            tr = Affine2D(sc.get_transforms()[0])
            dp = ax.transData.transform(sc.get_offsets()[0])
            gaps.append((bb_gap(tb, path.get_extents(tr).translated(*dp)), f"marker '{mname}'", min_gap))
        gaps.append((min(tb.x0, tb.y0, cw - tb.x1, ch - tb.y1) * k, "the canvas edge", min_edge))
        for g, what, need in gaps:
            smallest = min(smallest, g)
            if g < need:
                problems.append(f"'{name(t)}' is {g:.2f} pt from {what} (needs {need} pt)")

    print("\n--- CLEARANCE CHECK DETAILS ---")
    for p in problems:
        print(f"  * {p}")
    print(f"CLEARANCE CHECK: {len(problems)} problems (smallest gap {smallest:.2f} pt)\n")
    return len(problems)
```

Run the script once, with no other change. Paste the full CLEARANCE CHECK output.

Expected: about 20 problems. The list MUST include "3.9" near a drawn line, "Each country held out in turn. 73,254 diaries." near a drawn line and near the "Scored against..." box, the subtitle "Evening appliance electricity..." near the texts "UK", "IT" and "ES", and the axis numbers near a drawn line. If these are missing, your function is not the one above; copy it again exactly.

## Step 2: apply these exact edits

Each "old" text appears exactly once in the script. Replace it with "new". Nothing else.

Titles (all three tops at the same height):
1. old `ax.text(DIV1 / 2.0, 37.6, "The test", ha="center", va="center"`
   new `ax.text(DIV1 / 2.0, 39.2, "The test", ha="center", va="top"`
2. old `ax.text(B_MID, 37.25, "Result: the model does\nnot beat reweighting", ha="center", va="center"`
   new `ax.text(B_MID, 39.2, "Result: the model does\nnot beat reweighting", ha="center", va="top"`
3. old `ax.text(C_MID, 37.3, "For building energy models:\nappliance timing", ha="center", va="center"`
   new `ax.text(C_MID, 39.2, "For building energy models:\nappliance timing", ha="center", va="top"`

Left panel (scoring box up, footer centred between box and rule):
4. old `draw_box(1.6, 9.4, 28.6, 7.2,`
   new `draw_box(1.6, 10.2, 28.6, 7.2,`
5. old `ax.add_patch(FancyArrowPatch((8.5, 19.8), (8.5, 16.6), **arrow_kwargs))`
   new `ax.add_patch(FancyArrowPatch((8.5, 19.8), (8.5, 17.4), **arrow_kwargs))`
6. old `ax.add_patch(FancyArrowPatch((23.1, 19.8), (23.1, 16.6), **arrow_kwargs))`
   new `ax.add_patch(FancyArrowPatch((23.1, 19.8), (23.1, 17.4), **arrow_kwargs))`
7. old `ax.text(DIV1 / 2.0, 7.3, "Each country`
   new `ax.text(DIV1 / 2.0, 7.8, "Each country`

Centre panel (axis slightly shorter so "3.9" clears the divider; ticks point up only; text below moved down a little):
8. old `X_AXIS_END = 61.5`
   new `X_AXIS_END = 60.5`
9. old `ax.plot([tx, tx], [Y_AXIS - 0.5, Y_AXIS + 0.5], color="#444444", lw=0.8, zorder=2)`
   new `ax.plot([tx, tx], [Y_AXIS, Y_AXIS + 0.5], color="#444444", lw=0.8, zorder=2)`
10. old `ax.text(B_MID, Y_AXIS - 4.4, "Model error`
    new `ax.text(B_MID, Y_AXIS - 4.7, "Model error`
11. old `ax.text(B_MID, 10.4,`
    new `ax.text(B_MID, 10.0,`

Right panel (rows a little tighter so the subtitle clears the labels; ticks point up only; the two 21:00 labels move off their dots):
12. old `RY_REAL = 27.6`
    new `RY_REAL = 27.3`
13. old `RY_GEN = 23.0`
    new `RY_GEN = 22.9`
14. old `RY_REW = 18.4`
    new `RY_REW = 18.5`
15. old `ax.plot([hx, hx], [Y_H_AXIS - 0.4, Y_H_AXIS + 0.4], color="#444444", lw=0.8, zorder=2)`
    new `ax.plot([hx, hx], [Y_H_AXIS, Y_H_AXIS + 0.4], color="#444444", lw=0.8, zorder=2)`
16. old `ax.text(mx_21, RY_REW + 1.35, "IT"`
    new `ax.text(mx_21, RY_REW + 1.6, "IT"`
17. old `ax.text(mx_21, RY_REW - 1.35, "UK"`
    new `ax.text(mx_21, RY_REW - 1.6, "UK"`

The marker hours (18, 19, 21 / 14, 18, 20 / 19, 21, 21) and the nine ratio values stay exactly as they are; only the drawing positions above change.

## Step 3: run and check

Run the script once. Expected, exactly:
- `CLASH CHECK: 0 problems`
- `CLEARANCE CHECK: 0 problems (smallest gap 1.04 pt)` (the smallest gap is between the "UK" and "IT" labels in the Real diaries row; a value between 1.00 and 1.10 is fine)
- Font check: `Requirement (>= 7 pt): PASS`

Then open `4J_docs_occ\writing\submission\figures\4J_graphical_abstract.png` and look at it. Confirm in one line each: the three titles start at the same height; "3.9" has clear white space before the grey divider; the italic footer in the left panel has clear space above the grey bottom rule; the right-panel subtitle has clear space above UK / IT / ES.

## Step 4: copy to the upload folder

Copy, do not move:
- `4J_docs_occ\writing\submission\figures\4J_graphical_abstract.png` to `4J_docs_occ\writing\submission\EB_upload\Graphical_abstract.png`
- `4J_docs_occ\writing\submission\figures\4J_graphical_abstract.pdf` to `4J_docs_occ\writing\submission\EB_upload\Graphical_abstract.pdf`

## Report back (nothing else)

1. The CLEARANCE CHECK output from Step 1 (before the edits).
2. The CLASH CHECK, CLEARANCE CHECK and font check lines from Step 3 (after the edits).
3. The four one-line visual confirmations from Step 3.
4. The two copied file paths with their sizes in bytes.

# -*- coding: utf-8 -*-
"""Figure 1 - Three-row workflow diagram for Energy and Buildings.

Implements the specification in:
4J_docs_occ/writing/submission/figures/Prompts_Images/4thJ_figure01_workflow_three_rows.md
Updated per GEMINI_03_fix_figure1_and_graphical_abstract.md:
- Canvas: 7.5 x 4.5 inches (19.05 cm wide)
- Minimum font: 10 pt (scaled to print width 14 cm >= 7.35 pt, at 19 cm >= 9.97 pt)
- Boxes resized and padded so all labels fit cleanly
- Export: 1000 DPI PNG and vector PDF

Outputs:
  - writing/submission/figures/HETUS_LLM_Workflow_Figure1.png
  - writing/submission/figures/HETUS_LLM_Workflow_Figure1.pdf
  - writing/submission/figures/Prompts_Images/HETUS_LLM_Workflow_Figure1.png
  - writing/submission/figures/Prompts_Images/HETUS_LLM_Workflow_Figure1.pdf
"""
import os
import shutil
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Journal requirements: sans-serif font throughout, embed TrueType
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

# Palette from specification (Section 4)
ROSE = "#CC6677"
TEAL = "#44AA99"
INDIGO = "#332288"
NAVY = "#1B2A4A"
MID_GREY = "#888888"
LIGHT_GREY = "#E0E0E0"
BORDER_GREY = "#BCBCBC"
ARROW_COL = "#444444"
INK_DARK = "#111111"
INK_WHITE = "#FFFFFF"
ROW_BG = "#F5F5F5"

# Target width: 19.0 cm (7.480 in) full page, 14.0 cm (5.512 in) 1.5-column
# Proportions: 7.5 x 4.5 inches (5:3 ratio). High resolution 1000 DPI export.
W_INCH = 7.5
H_INCH = 4.5

# Every font must be at least 10 pt on this canvas (Fix 1)
FONT_SIZE = 10.0

fig = plt.figure(figsize=(W_INCH, H_INCH))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 60)
ax.set_aspect("auto")
ax.axis("off")
fig.patch.set_facecolor("white")

boxes = []
markers = []
box_of_text = {}

# ---------------------------------------------------------------- helpers
def draw_box(x, y, w, h, text, fill_col, text_col=INK_DARK, font_size=FONT_SIZE,
             weight="bold", rad=1.0, border_col=None):
    """Draw a rounded rectangular box with centered text."""
    ec = border_col if border_col else ("none" if text_col == INK_WHITE else BORDER_GREY)
    lw = 1.0 if ec != "none" else 0
    patch = FancyBboxPatch((x, y), w, h,
                           boxstyle=f"round,pad=0,rounding_size={rad}",
                           facecolor=fill_col, edgecolor=ec, linewidth=lw, zorder=3)
    ax.add_patch(patch)
    t = None
    if text:
        t = ax.text(x + w / 2.0, y + h / 2.0, text, ha="center", va="center",
                fontsize=font_size, color=text_col, weight=weight, zorder=4,
                linespacing=1.18)
        box_of_text[t] = patch
    boxes.append((patch, text.replace('\n', ' ') if text else "unnamed_box"))
    return patch

def draw_arrow(x1, y1, x2, y2, lw=1.5, ms=12):
    """Draw a straight directed arrow between two points."""
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                            connectionstyle="arc3,rad=0",
                            arrowstyle="-|>",
                            mutation_scale=ms,
                            color=ARROW_COL,
                            linewidth=lw,
                            shrinkA=0, shrinkB=0,
                            zorder=2)
    ax.add_patch(arrow)

def rounded_polyline(pts, r=1.2):
    """Generate smooth polyline with rounded corners."""
    res = [pts[0]]
    for i in range(1, len(pts)-1):
        p_prev = np.array(pts[i-1], dtype=float)
        p_curr = np.array(pts[i], dtype=float)
        p_next = np.array(pts[i+1], dtype=float)
        v1 = p_prev - p_curr
        v2 = p_next - p_curr
        d1 = np.linalg.norm(v1)
        d2 = np.linalg.norm(v2)
        v1_u = v1 / d1
        v2_u = v2 / d2
        cut = min(r, d1/2.1, d2/2.1)
        p1 = p_curr + v1_u * cut
        p2 = p_curr + v2_u * cut
        ts = np.linspace(0, 1, 16)
        curve = [(1-t)**2 * p1 + 2*(1-t)*t * p_curr + t**2 * p2 for t in ts]
        res.extend(curve)
    res.append(pts[-1])
    return res

def draw_rounded_arrow(pts, r=1.2, lw=1.5, ms=12):
    """Draw polyline with rounded corners and an arrowhead on final segment."""
    r_pts = rounded_polyline(pts, r=r)
    xs = [p[0] for p in r_pts]
    ys = [p[1] for p in r_pts]
    ax.plot(xs[:-1], ys[:-1], color=ARROW_COL, linewidth=lw, solid_joinstyle="round", zorder=2)
    p_last = pts[-1]
    p_prev = pts[-2]
    ax.add_patch(FancyArrowPatch((p_prev[0], p_prev[1]), (p_last[0], p_last[1]),
                            arrowstyle="-|>", mutation_scale=ms,
                            color=ARROW_COL, linewidth=lw,
                            shrinkA=0, shrinkB=0, zorder=2))

# ---------------------------------------------------------------- row background bands
BAND_RAD = 1.0
# Row 1: [41.0, 58.5]
ax.add_patch(FancyBboxPatch((1.5, 41.0), 97.0, 17.5,
                            boxstyle=f"round,pad=0,rounding_size={BAND_RAD}",
                            facecolor=ROW_BG, edgecolor="none", zorder=1))
# Row 2: [21.5, 39.0]
ax.add_patch(FancyBboxPatch((1.5, 21.5), 97.0, 17.5,
                            boxstyle=f"round,pad=0,rounding_size={BAND_RAD}",
                            facecolor=ROW_BG, edgecolor="none", zorder=1))
# Row 3: [2.0, 19.5]
ax.add_patch(FancyBboxPatch((1.5, 2.0), 97.0, 17.5,
                            boxstyle=f"round,pad=0,rounding_size={BAND_RAD}",
                            facecolor=ROW_BG, edgecolor="none", zorder=1))

# ==============================================================================
# ROW 1 — Data and harmonisation (Section 2.1, 2.2)
# ==============================================================================
Y1_MID = 49.75
H1 = 8.8
Y1_BOX = Y1_MID - H1 / 2.0

# Five boxes:
# 1. Spain survey: 19,295 diaries
# 2. Italy survey: 41,229 diaries
# 3. United Kingdom survey: 16,533 diaries
# 4. Harmonise to shared activity codes
# 5. Convert diaries to text records

draw_box(2.5, Y1_BOX, 17.2, H1, "Spain survey:\n19,295 diaries", ROSE, INK_WHITE, font_size=FONT_SIZE)
draw_box(20.4, Y1_BOX, 17.2, H1, "Italy survey:\n41,229 diaries", TEAL, INK_WHITE, font_size=FONT_SIZE)
draw_box(38.3, Y1_BOX, 18.5, H1, "United Kingdom\nsurvey:\n16,533 diaries", INDIGO, INK_WHITE, font_size=FONT_SIZE)
draw_box(60.8, Y1_BOX, 19.5, H1, "Harmonise to\nshared activity\ncodes", LIGHT_GREY, INK_DARK, font_size=FONT_SIZE)
draw_box(83.8, Y1_BOX, 13.7, H1, "Convert\ndiaries to\ntext records", LIGHT_GREY, INK_DARK, font_size=FONT_SIZE)

# Arrows in Row 1:
# UK -> Harmonise (straight center-left horizontal entry)
draw_arrow(56.8, Y1_MID, 60.8, Y1_MID)

# Italy -> Harmonise (smooth arch over UK, enters upper-left horizontally)
pts_ita = [
    (37.6, Y1_MID + 1.5),
    (38.1, Y1_BOX + H1 + 2.2),
    (58.8, Y1_BOX + H1 + 2.2),
    (58.8, Y1_MID + 1.8),
    (60.8, Y1_MID + 1.8)
]
draw_rounded_arrow(pts_ita, r=1.0)

# Spain -> Harmonise (smooth sweep below Italy and UK, enters lower-left horizontally)
pts_esp = [
    (19.7, Y1_MID - 1.5),
    (20.2, Y1_BOX - 2.2),
    (58.8, Y1_BOX - 2.2),
    (58.8, Y1_MID - 1.8),
    (60.8, Y1_MID - 1.8)
]
draw_rounded_arrow(pts_esp, r=1.0)

# Harmonise -> Convert
draw_arrow(80.3, Y1_MID, 83.8, Y1_MID)


# ==============================================================================
# ROW 2 — Diary generation and comparison (Section 2.3, 2.4, 2.6)
# ==============================================================================
# Five boxes:
# 1. Train on two countries
# 2. Fine-tuned model generates held-out diaries
# 3. Reweight real diaries by IPF
# 4. Compare to published time budgets
# 5. Pre-registered pass or fail rule
Y2_MID = 30.25

# Box 1: Train on two countries
draw_box(2.5, Y2_MID - 4.0, 15.0, 8.0, "Train on two\ncountries", LIGHT_GREY, INK_DARK, font_size=FONT_SIZE)

# Box 2: Fine-tuned model generates held-out diaries (navy, white text)
draw_box(21.5, Y2_MID + 1.2, 33.0, 6.2, "Fine-tuned model generates\nheld-out diaries", NAVY, INK_WHITE, font_size=FONT_SIZE)

# Box 3: Reweight real diaries by IPF (mid grey, white text)
draw_box(21.5, Y2_MID - 7.4, 33.0, 6.2, "Reweight real diaries\nby IPF", MID_GREY, INK_WHITE, font_size=FONT_SIZE)

# Box 4: Compare to published time budgets
draw_box(58.5, Y2_MID - 4.0, 16.5, 8.0, "Compare to\npublished\ntime budgets", LIGHT_GREY, INK_DARK, font_size=FONT_SIZE)

# Box 5: Pre-registered pass or fail rule
draw_box(79.0, Y2_MID - 4.0, 18.5, 8.0, "Pre-registered\npass or fail rule", LIGHT_GREY, INK_DARK, font_size=FONT_SIZE)

# Arrows in Row 2:
# Box 1 feeds two arrows: one to Box 2, one to Box 3
draw_arrow(17.5, Y2_MID + 1.2, 21.5, Y2_MID + 4.3)
draw_arrow(17.5, Y2_MID - 1.2, 21.5, Y2_MID - 4.3)

# Boxes 2 and 3 each feed an arrow into Box 4
draw_arrow(54.5, Y2_MID + 4.3, 58.5, Y2_MID + 1.2)
draw_arrow(54.5, Y2_MID - 4.3, 58.5, Y2_MID - 1.2)

# Box 4 feeds one arrow into Box 5
draw_arrow(75.0, Y2_MID, 79.0, Y2_MID)


# ==============================================================================
# ROW 3 — Building loads (Section 2.5)
# ==============================================================================
# Six boxes:
# 1. Diaries drive building simulation
# 2. Occupancy-based internal gains
# 3. Activity-triggered appliance loads
# 4. Domestic hot water draws
# 5. Heating demand: Spain, Italy, UK archetypes
# 6. Stock-scale loads: London and Bologna
Y3_MID = 10.75

# Box 1: Diaries drive building simulation
draw_box(2.5, Y3_MID - 4.2, 16.5, 8.4, "Diaries drive\nbuilding\nsimulation", LIGHT_GREY, INK_DARK, font_size=FONT_SIZE)

# Middle 3 parallel branches (Boxes 2, 3, 4) - Fix H: taller boxes with clear padding
draw_box(23.5, 13.7, 29.0, 5.0, "Occupancy-based\ninternal gains", LIGHT_GREY, INK_DARK, font_size=FONT_SIZE)
draw_box(23.5, 8.25, 29.0, 5.0, "Activity-triggered\nappliance loads", LIGHT_GREY, INK_DARK, font_size=FONT_SIZE)
draw_box(23.5, 2.8,  29.0, 5.0, "Domestic hot\nwater draws", LIGHT_GREY, INK_DARK, font_size=FONT_SIZE)

# Right 2 final boxes (Boxes 5, 6)
draw_box(56.5, 11.0, 40.5, 6.8, "Heating demand:\nSpain, Italy, UK archetypes", LIGHT_GREY, INK_DARK, font_size=FONT_SIZE)
draw_box(56.5, 3.0,  40.5, 6.8, "Stock-scale loads:\nLondon and Bologna", LIGHT_GREY, INK_DARK, font_size=FONT_SIZE)

# Arrows in Row 3:
# Box 1 feeds arrows into boxes 2, 3 and 4 (three parallel branches)
draw_arrow(19.0, Y3_MID + 1.5, 23.5, 16.2)
draw_arrow(19.0, Y3_MID,       23.5, 10.75)
draw_arrow(19.0, Y3_MID - 1.5, 23.5, 5.3)

# Box 2 feeds one arrow into Box 5 (Heating demand)
draw_arrow(52.5, 16.2, 56.5, 14.4)

# Boxes 3 and 4 each feed one arrow into Box 6 (Stock-scale loads)
draw_arrow(52.5, 10.75, 56.5, 7.8)
draw_arrow(52.5, 5.3,  56.5, 5.0)

# Output paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, ".."))
PROMPT_DIR = os.path.normpath(os.path.join(FIG_DIR, "Prompts_Images"))

out_fig_png = os.path.join(FIG_DIR, "HETUS_LLM_Workflow_Figure1.png")
out_fig_pdf = os.path.join(FIG_DIR, "HETUS_LLM_Workflow_Figure1.pdf")
out_prompt_png = os.path.join(PROMPT_DIR, "HETUS_LLM_Workflow_Figure1.png")
out_prompt_pdf = os.path.join(PROMPT_DIR, "HETUS_LLM_Workflow_Figure1.pdf")

# ==============================================================================
# CLASH CHECK (Step 0)
# ==============================================================================
def run_clash_check(fig, ax, boxes, markers, box_of_text):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    dpi = fig.dpi
    canvas_w, canvas_h = fig.bbox.width, fig.bbox.height
    
    problems = []
    all_texts = ax.texts
    
    # 1. Text outside canvas
    for t in all_texts:
        txt_str = t.get_text().replace('\n', ' ')
        bb = t.get_window_extent(renderer)
        if bb.x0 < -0.1 or bb.y0 < -0.1 or bb.x1 > canvas_w + 0.1 or bb.y1 > canvas_h + 0.1:
            problems.append(f"Text outside canvas: '{txt_str}'")

    # 2. Pairwise text overlap
    for i in range(len(all_texts)):
        for j in range(i + 1, len(all_texts)):
            t1, t2 = all_texts[i], all_texts[j]
            b1 = t1.get_window_extent(renderer)
            b2 = t2.get_window_extent(renderer)
            if b1.overlaps(b2):
                str1 = t1.get_text().replace('\n', ' ')
                str2 = t2.get_text().replace('\n', ' ')
                problems.append(f"Text overlap: '{str1}' and '{str2}'")

    # 3. Text overlaps marker or box it is not written inside
    for t in all_texts:
        txt_str = t.get_text().replace('\n', ' ')
        t_bb = t.get_window_extent(renderer)
        for b_patch, b_name in boxes:
            if box_of_text.get(t) is not b_patch:
                p_bb = b_patch.get_window_extent(renderer)
                if t_bb.overlaps(p_bb):
                    problems.append(f"Text '{txt_str}' overlaps box '{b_name}'")

    # 4. Box label padding < 2 pt to its own box edge
    for t, b_patch in box_of_text.items():
        if b_patch is not None:
            t_bb = t.get_window_extent(renderer)
            p_bb = b_patch.get_window_extent(renderer)
            left_pad = (t_bb.x0 - p_bb.x0) * 72.0 / dpi
            right_pad = (p_bb.x1 - t_bb.x1) * 72.0 / dpi
            bot_pad = (t_bb.y0 - p_bb.y0) * 72.0 / dpi
            top_pad = (p_bb.y1 - t_bb.y1) * 72.0 / dpi
            min_pad = min(left_pad, right_pad, bot_pad, top_pad)
            if min_pad < 2.0:
                txt_str = t.get_text().replace('\n', ' ')
                problems.append(f"Box label '{txt_str}' padding {min_pad:.2f} pt < 2 pt")

    print("\n--- CLASH CHECK DETAILS ---")
    for p in problems:
        print(f"  * {p}")
    print(f"CLASH CHECK: {len(problems)} problems\n")
    return len(problems)

run_clash_check(fig, ax, boxes, markers, box_of_text)

# Generate 1000 DPI PNG (7500x4500 px) and vector PDF per Fix 1
print("Saving PNG (1000 DPI)...")
fig.savefig(out_fig_png, dpi=1000, facecolor="white")
print("Saving vector PDF...")
fig.savefig(out_fig_pdf, facecolor="white")

# Also copy to Prompts_Images directory
shutil.copyfile(out_fig_png, out_prompt_png)
shutil.copyfile(out_fig_pdf, out_prompt_pdf)

# Save a raw copy of the Gemini generated image if available
brain_raw = r"C:\Users\o_iseri\.gemini\antigravity\brain\9dd08e62-a973-4b35-ba45-e334e938aa14\workflow_figure_one_1790207843402.jpg"
if os.path.exists(brain_raw):
    raw_prompt = os.path.join(PROMPT_DIR, "HETUS_LLM_Workflow_Figure1_gemini_raw.jpg")
    shutil.copyfile(brain_raw, raw_prompt)
    print(f"Copied raw Gemini generation to {raw_prompt}")

# Fix 1 Font Check Printout
canvas_w_cm = W_INCH * 2.54
min_font_pt = FONT_SIZE
print_w_14_cm = 14.0
print_w_19_cm = 19.0
scaled_14 = min_font_pt * print_w_14_cm / canvas_w_cm
scaled_19 = min_font_pt * print_w_19_cm / canvas_w_cm

print("=== Figure 1 Font Check (Fix 1) ===")
print(f"Canvas width: {canvas_w_cm:.2f} cm ({W_INCH} in)")
print(f"Smallest font size used: {min_font_pt:.1f} pt")
print(f"Scaled to 14.0 cm print width: {scaled_14:.2f} pt (pass >= 7 pt: {scaled_14 >= 7.0})")
print(f"Scaled to 19.0 cm print width: {scaled_19:.2f} pt (pass >= 7 pt: {scaled_19 >= 7.0})")
print("Figure 1 generation completed successfully.")

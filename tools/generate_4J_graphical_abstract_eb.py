# -*- coding: utf-8 -*-
"""Generate Graphical Abstract for Energy and Buildings submission (4J).

Implements the exact specification in:
- IMP/prep/graphical_abstract_prompt.md (2026-09-23)
- GEMINI_03_fix_figure1_and_graphical_abstract.md (2026-09-24)
- GEMINI_04_fix_graphical_abstract_layout.md (2026-09-24)
"""
import os
import shutil
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D
from matplotlib.transforms import Bbox, Affine2D

# Matplotlib typography & publication styling
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

# House palette (colour-blind safe)
ROSE = "#CC6677"      # Spain
TEAL = "#44AA99"      # Italy
INDIGO = "#332288"    # UK
NAVY = "#1B2A4A"      # Model box
GREY_M = "#888888"    # Reweighted box / lines
GREY_L = "#EAEAEA"    # Light boxes
GREY_RULE = "#DCDCDC" # Thin rules
INK = "#111111"       # Primary text
WHITE = "#FFFFFF"

# Canvas 5.12 x 2.05 inches (13 x 5.2 cm), 600 DPI
W, H = 5.12, 2.05
fig = plt.figure(figsize=(W, H), dpi=600)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 40)
ax.set_aspect("auto")
ax.axis("off")
fig.patch.set_facecolor(WHITE)

FS_TITLE = 7.3
FS_BODY = 7.1

boxes = []
markers = []
box_of_text = {}

def draw_box(x, y, w, h, text, fc=GREY_L, ec="none", tc=INK, fs=FS_BODY, weight="normal", rad=0.6, ls="solid"):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0,rounding_size={rad}",
                       facecolor=fc, edgecolor=ec, linewidth=0.8,
                       linestyle=ls, zorder=3)
    ax.add_patch(p)
    t = None
    if text:
        t = ax.text(x + w / 2.0, y + h / 2.0, text, ha="center", va="center",
                fontsize=fs, color=tc, weight=weight, zorder=4, linespacing=1.05)
        box_of_text[t] = p
    boxes.append((p, text.replace('\n', ' ') if text else "unnamed_box"))
    return p

# Thin panel divider rules
DIV1 = 31.8
DIV2 = 65.8
ax.plot([DIV1, DIV1], [6.0, 39.0], color=GREY_RULE, lw=0.8, zorder=2)
ax.plot([DIV2, DIV2], [6.0, 39.0], color=GREY_RULE, lw=0.8, zorder=2)

# ==============================================================================
# PANEL A (Left, 0 to 31.8): "The test"
# ==============================================================================
ax.text(DIV1 / 2.0, 39.2, "The test", ha="center", va="top", fontsize=FS_TITLE, weight="bold", color=INK)

# Fix F: Make UK tile big enough (12.6 x 5.6) with clear internal padding
draw_box(1.6, 30.6, 7.2, 5.6, "Spain", fc=ROSE, tc=WHITE, fs=FS_BODY, weight="bold")
draw_box(9.8, 30.6, 7.2, 5.6, "Italy", fc=TEAL, tc=WHITE, fs=FS_BODY, weight="bold")
draw_box(18.0, 30.6, 12.6, 5.6, "UK\n(held out)", fc=WHITE, ec=INDIGO, tc=INDIGO, fs=FS_BODY, weight="bold", ls="dashed")

# Side-by-side parallel methods (generous boxes)
draw_box(1.6, 19.8, 13.8, 8.0, "Fine-tuned\nlanguage\nmodel", fc=NAVY, tc=WHITE, fs=FS_BODY, weight="bold")
draw_box(16.0, 19.8, 14.2, 8.0, "Real diaries\nof the\nother two", fc=GREY_M, tc=WHITE, fs=FS_BODY, weight="bold")

# Fix G: Drop arrow into Real diaries moved left under Italy / gap (x=16.8); UK tile (x>=18.0) has NO line under it
arrow_kwargs = dict(arrowstyle="-|>", mutation_scale=7, color="#555555", lw=0.9, zorder=2)
Y_BUS = 29.4
ax.plot([5.2, 16.8], [Y_BUS, Y_BUS], color="#555555", lw=0.9, zorder=2)
ax.plot([5.2, 5.2], [30.6, Y_BUS], color="#555555", lw=0.9, zorder=2)
ax.plot([13.4, 13.4], [30.6, Y_BUS], color="#555555", lw=0.9, zorder=2)
ax.add_patch(FancyArrowPatch((8.5, Y_BUS), (8.5, 27.8), **arrow_kwargs))
ax.add_patch(FancyArrowPatch((16.8, Y_BUS), (16.8, 27.8), **arrow_kwargs))

# Scoring box (height=7.2 to guarantee >2 pt vertical padding)
draw_box(1.6, 10.2, 28.6, 7.2, "Scored against the\nheld-out country's\npublished tables",
         fc=GREY_L, ec="#BCBCBC", tc=INK, fs=FS_BODY, weight="bold")

ax.add_patch(FancyArrowPatch((8.5, 19.8), (8.5, 17.4), **arrow_kwargs))
ax.add_patch(FancyArrowPatch((23.1, 19.8), (23.1, 17.4), **arrow_kwargs))

# Footer line of panel A
ax.text(DIV1 / 2.0, 7.8, "Each country held out in turn.\n73,254 diaries.", ha="center", va="center",
        fontsize=FS_BODY, color="#444444", style="italic", linespacing=1.05)

# ==============================================================================
# PANEL B (Centre, 31.8 to 65.8): "Result: the model does not beat reweighting"
# ==============================================================================
B_MID = (DIV1 + DIV2) / 2.0

ax.text(B_MID, 39.2, "Result: the model does\nnot beat reweighting", ha="center", va="top",
        fontsize=FS_TITLE, weight="bold", color=INK, linespacing=1.05)

ax.text(B_MID, 32.5, "Worse in 9 of 9 cells:\n1.1 to 3.9 times the error", ha="center", va="center",
        fontsize=FS_BODY, weight="bold", color="#A61C1C", linespacing=1.05)

X_AXIS_START = 36.5
X_AXIS_END = 60.5
def val_to_x(val):
    return X_AXIS_START + (val - 1.0) / (4.0 - 1.0) * (X_AXIS_END - X_AXIS_START)

Y_AXIS = 21.0
ax.plot([X_AXIS_START, X_AXIS_END], [Y_AXIS, Y_AXIS], color="#444444", lw=0.9, zorder=2)

for tick in [1, 2, 3, 4]:
    tx = val_to_x(tick)
    ax.plot([tx, tx], [Y_AXIS, Y_AXIS + 0.5], color="#444444", lw=0.8, zorder=2)
    ax.text(tx, Y_AXIS - 1.5, str(tick), ha="center", va="center", fontsize=FS_BODY, color=INK)

# Fix E: Axis title broken into two lines, lowered to avoid tick number overlap
ax.text(B_MID, Y_AXIS - 4.7, "Model error /\nreweighted-diary error", ha="center", va="center",
        fontsize=FS_BODY, color=INK, linespacing=1.05)

# Fix 4 & Fix D: Solid reference line at 1; move label so it touches no dot
x_one = val_to_x(1.0)
ax.plot([x_one, x_one], [Y_AXIS, Y_AXIS + 7.5], color=GREY_M, lw=1.2, ls="-", zorder=2)
ax.text(x_one + 0.6, Y_AXIS + 6.8, "reweighted\nreal diaries", ha="left", va="center",
        fontsize=FS_BODY, color="#555555", weight="bold", linespacing=1.05)

# Nine dots (exact positions kept)
dots = [
    (3.70, ROSE, "Spain 25-44"),
    (3.91, ROSE, "Spain 45-64"),
    (3.75, ROSE, "Spain 65+"),
    (2.70, INDIGO, "UK 25-44"),
    (3.15, INDIGO, "UK 45-64"),
    (1.15, INDIGO, "UK 65+"),
    (3.19, TEAL, "Italy 25-44"),
    (2.45, TEAL, "Italy 45-64"),
    (2.31, TEAL, "Italy 65+")
]
dot_y_offsets = [3.0, 4.5, 6.0, 2.5, 4.0, 2.0, 5.2, 3.2, 1.8]
for (ratio, col, lbl), dy in zip(dots, dot_y_offsets):
    px = val_to_x(ratio)
    py = Y_AXIS + dy
    sc = ax.scatter([px], [py], s=25, color=col, edgecolors=INK, linewidth=0.5, zorder=5)
    markers.append((sc, lbl))

# Fix A: 1.1 label placed to the right of dot at 1.15 (dy=2.0)
ax.text(val_to_x(1.15) + 1.3, Y_AXIS + 2.0, "1.1", ha="left", va="center", fontsize=FS_BODY, weight="bold", color=INDIGO)
# 3.9 label placed to the right of dot at 3.91 (dy=4.5) to avoid overlapping Spain 25-44 (dy=3.0)
ax.text(val_to_x(3.91) + 1.5, Y_AXIS + 4.5, "3.9", ha="left", va="center", fontsize=FS_BODY, weight="bold", color=ROSE)

# Text below axis
ax.text(B_MID, 10.0,
        "Also misses the 15 % bar\non its own training countries\n(33 to 158 %); real diaries\nmeet it (5 to 12 %)",
        ha="center", va="center", fontsize=FS_BODY, color="#333333", linespacing=1.05)

# ==============================================================================
# PANEL C (Right, 65.8 to 100.0): "For building energy models: appliance timing"
# ==============================================================================
C_MID = (DIV2 + 100.0) / 2.0

ax.text(C_MID, 39.2, "For building energy models:\nappliance timing", ha="center", va="top",
        fontsize=FS_TITLE, weight="bold", color=INK, linespacing=1.05)

# Fix C: Subtitle in normal weight (not bold), at least 3 pt below title
ax.text(C_MID, 32.5, "Evening appliance electricity\npeak, by diary source", ha="center", va="center",
        fontsize=FS_BODY, weight="normal", color=INK, linespacing=1.05)

# Fix C & A: Start row lines and hour axis further right (79.0 to 97.2)
X_H_START = 79.0
X_H_END = 97.2
def hour_to_x(h):
    return X_H_START + (h - 12.0) / (22.0 - 12.0) * (X_H_END - X_H_START)

RY_REAL = 27.3
RY_GEN = 22.9
RY_REW = 18.5
Y_H_AXIS = 14.3

# Fix A: Hour axis labels 12 to 22 (no ":00") and word "hour"
ax.plot([X_H_START, X_H_END], [Y_H_AXIS, Y_H_AXIS], color="#444444", lw=0.9, zorder=2)
for h in range(12, 24, 2):
    hx = hour_to_x(h)
    ax.plot([hx, hx], [Y_H_AXIS, Y_H_AXIS + 0.4], color="#444444", lw=0.8, zorder=2)
    ax.text(hx, Y_H_AXIS - 1.4, str(h), ha="center", va="center", fontsize=FS_BODY, color=INK)

# Fix A: Word "hour" placed cleanly to the left of tick 12
ax.text(77.0, Y_H_AXIS - 1.4, "hour", ha="right", va="center", fontsize=FS_BODY, color=INK)

# Real diaries row
ax.text(66.2, RY_REAL, "Real\ndiaries", ha="left", va="center", fontsize=FS_BODY, weight="bold", color=INK, linespacing=1.0)
ax.plot([X_H_START, X_H_END], [RY_REAL, RY_REAL], color="#E8E8E8", lw=0.9, zorder=1)
for hr, col, code, dx_lbl in [(18, INDIGO, "UK", -0.5), (19, TEAL, "IT", 0.5), (21, ROSE, "ES", 0.0)]:
    mx = hour_to_x(hr)
    sc = ax.scatter([mx], [RY_REAL], s=26, color=col, edgecolors=INK, linewidth=0.6, zorder=4)
    markers.append((sc, f"Real {code}"))
    ax.text(mx + dx_lbl, RY_REAL + 1.1, code, ha="center", va="bottom", fontsize=FS_BODY, weight="bold", color=col)

# Generated diaries row
ax.text(66.2, RY_GEN, "Generated\ndiaries", ha="left", va="center", fontsize=FS_BODY, color=INK, linespacing=1.0)
ax.plot([X_H_START, X_H_END], [RY_GEN, RY_GEN], color="#E8E8E8", lw=0.9, zorder=1)
for hr, col, code in [(14, ROSE, "ES"), (18, TEAL, "IT"), (20, INDIGO, "UK")]:
    mx = hour_to_x(hr)
    sc = ax.scatter([mx], [RY_GEN], s=22, color=col, edgecolors=INK, linewidth=0.5, zorder=4)
    markers.append((sc, f"Gen {code}"))
    ax.text(mx, RY_GEN + 1.1, code, ha="center", va="bottom", fontsize=FS_BODY, weight="bold", color=col)

# Reweighted diaries row (Fix 3: Italy and UK at EXACTLY 21:00)
ax.text(66.2, RY_REW, "Reweighted\ndiaries", ha="left", va="center", fontsize=FS_BODY, color=INK, linespacing=1.0)
ax.plot([X_H_START, X_H_END], [RY_REW, RY_REW], color="#E8E8E8", lw=0.9, zorder=1)

# Spain at 19:00 on row line
mx_es = hour_to_x(19.0)
sc = ax.scatter([mx_es], [RY_REW], s=22, color=ROSE, edgecolors=INK, linewidth=0.5, zorder=4)
markers.append((sc, "Rew ES"))
ax.text(mx_es, RY_REW + 1.1, "ES", ha="center", va="bottom", fontsize=FS_BODY, weight="bold", color=ROSE)

# Italy at 21:00, slightly above row line
mx_21 = hour_to_x(21.0)
sc = ax.scatter([mx_21], [RY_REW + 0.65], s=22, color=TEAL, edgecolors=INK, linewidth=0.5, zorder=4)
markers.append((sc, "Rew IT"))
ax.text(mx_21, RY_REW + 1.6, "IT", ha="center", va="bottom", fontsize=FS_BODY, weight="bold", color=TEAL)

# UK at 21:00, slightly below row line
sc = ax.scatter([mx_21], [RY_REW - 0.65], s=22, color=INDIGO, edgecolors=INK, linewidth=0.5, zorder=4)
markers.append((sc, "Rew UK"))
ax.text(mx_21, RY_REW - 1.6, "UK", ha="center", va="top", fontsize=FS_BODY, weight="bold", color=INDIGO)

# Neither synthetic source label
ax.text(C_MID, 8.8, "Neither synthetic\nsource carries the\ncountry's timing", ha="center", va="center",
        fontsize=FS_BODY, weight="bold", color="#A61C1C", linespacing=1.05)

# ==============================================================================
# BOTTOM STRIP
# ==============================================================================
ax.plot([2.0, 98.0], [5.4, 5.4], color=GREY_RULE, lw=0.8, zorder=2)
ax.text(40.0, 2.7,
        "Where a country has no diaries, reweighted real diaries\nfrom comparable countries are the stronger default.",
        ha="center", va="center", fontsize=FS_BODY, weight="bold", color=INK, linespacing=1.1)
ax.text(97.5, 2.7, "Pre-registered before\ntraining, 2026-08-18", ha="right", va="center",
        fontsize=FS_BODY, color="#666666", linespacing=1.05)

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
    marker_bboxes = []
    for m in markers:
        sc = m[0] if isinstance(m, tuple) else m
        lbl = m[1] if isinstance(m, tuple) else "marker"
        path = sc.get_paths()[0]
        trans = Affine2D(sc.get_transforms()[0])
        disp_pt = ax.transData.transform(sc.get_offsets()[0])
        m_bb = path.get_extents(trans).translated(disp_pt[0], disp_pt[1])
        marker_bboxes.append((m_bb, lbl))

    for t in all_texts:
        txt_str = t.get_text().replace('\n', ' ')
        t_bb = t.get_window_extent(renderer)
        for b_patch, b_name in boxes:
            if box_of_text.get(t) is not b_patch:
                p_bb = b_patch.get_window_extent(renderer)
                if t_bb.overlaps(p_bb):
                    problems.append(f"Text '{txt_str}' overlaps box '{b_name}'")
        for m_bb, m_name in marker_bboxes:
            if t_bb.overlaps(m_bb):
                problems.append(f"Text '{txt_str}' overlaps marker '{m_name}'")

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

    # 5. Text touching a drawn line or arrow
    for t in all_texts:
        txt_str = t.get_text().replace('\n', ' ')
        t_bb = t.get_window_extent(renderer)
        touches = False
        for line in ax.lines:
            xdata, ydata = line.get_data()
            pts = np.column_stack([xdata, ydata])
            disp_pts = ax.transData.transform(pts)
            for k in range(len(disp_pts) - 1):
                p0, p1 = disp_pts[k], disp_pts[k+1]
                seg_len = np.hypot(*(p1 - p0))
                num_pts = max(int(np.ceil(seg_len * 2)), 2)
                sampled = np.linspace(p0, p1, num_pts)
                if any(t_bb.x0 <= pt[0] <= t_bb.x1 and t_bb.y0 <= pt[1] <= t_bb.y1 for pt in sampled):
                    touches = True
                    break
            if touches:
                break
        if not touches:
            for patch in ax.patches:
                if isinstance(patch, FancyArrowPatch):
                    if t_bb.overlaps(patch.get_window_extent(renderer)):
                        touches = True
                        break
        if touches:
            problems.append(f"Text '{txt_str}' touches line")

    # 6. Text too close to canvas edge (< 2 pt)
    for t in all_texts:
        txt_str = t.get_text().replace('\n', ' ')
        t_bb = t.get_window_extent(renderer)
        l_d = t_bb.x0 * 72.0 / dpi
        b_d = t_bb.y0 * 72.0 / dpi
        r_d = (canvas_w - t_bb.x1) * 72.0 / dpi
        top_d = (canvas_h - t_bb.y1) * 72.0 / dpi
        edges = [("left", l_d), ("bottom", b_d), ("right", r_d), ("top", top_d)]
        min_e, min_d = min(edges, key=lambda x: x[1])
        if min_d < 2.0:
            problems.append(f"Text '{txt_str}' closer than 2 pt to canvas edge ({min_e} edge: {min_d:.2f} pt)")

    print("\n--- CLASH CHECK DETAILS ---")
    for p in problems:
        print(f"  * {p}")
    print(f"CLASH CHECK: {len(problems)} problems\n")
    return len(problems)


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


run_clash_check(fig, ax, boxes, markers, box_of_text)
run_clearance_check(fig, ax, boxes, markers, box_of_text)

# ==============================================================================
# EXPORT
# ==============================================================================
OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "4J_docs_occ", "writing", "submission", "figures"))
PROMPT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "4J_docs_occ", "writing", "submission", "Gemini_prompts"))

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(PROMPT_DIR, exist_ok=True)

out_png = os.path.join(OUT_DIR, "4J_graphical_abstract.png")
out_pdf = os.path.join(OUT_DIR, "4J_graphical_abstract.pdf")
prompt_png = os.path.join(PROMPT_DIR, "GEMINI_02_graphical_abstract.png")
prompt_pdf = os.path.join(PROMPT_DIR, "GEMINI_02_graphical_abstract.pdf")

print("Saving Graphical Abstract PNG (600 DPI)...")
fig.savefig(out_png, dpi=600, facecolor=WHITE)
print("Saving Graphical Abstract PDF (vector)...")
fig.savefig(out_pdf, facecolor=WHITE)

shutil.copyfile(out_png, prompt_png)
shutil.copyfile(out_pdf, prompt_pdf)
print("Graphical abstract successfully created and mirrored.")

# ==============================================================================
# FIX 1: FONT CHECK REPORT
# ==============================================================================
canvas_w_cm = W * 2.54
print_w_cm = 13.0
min_font_pt = min(FS_BODY, FS_TITLE)
scaled_font_pt = min_font_pt * print_w_cm / canvas_w_cm
status = "PASS" if scaled_font_pt >= 7.0 else "FAIL"

print("\n" + "=" * 60)
print("FONT SIZE CHECK (Graphical Abstract):")
print(f"  Canvas width:          {canvas_w_cm:.2f} cm ({W:.2f} in)")
print(f"  Smallest font size:    {min_font_pt:.2f} pt")
print(f"  Target print width:    {print_w_cm:.2f} cm")
print(f"  Scaled font at print:  {scaled_font_pt:.2f} pt")
print(f"  Requirement (>= 7 pt): {status}")
print("=" * 60)

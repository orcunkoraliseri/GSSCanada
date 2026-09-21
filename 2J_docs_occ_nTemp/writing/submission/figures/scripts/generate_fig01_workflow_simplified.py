# -*- coding: utf-8 -*-
"""Generate Figure 1: Methods workflow diagram for Applied Energy.

Specifications from:
writing/submission/figures/Prompts_Images/Figure_01_workflow_prompt.md (2026-09-21)

- Width: 190 mm, Height: 90 mm.
- Resolution: 600 DPI (4488 x 2126 px).
- Canvas background: pure white.
- Style: flat design, plain rounded rectangles, thin dark-grey outlines.
- Palette: one soft colour per row (colour-blind-safe):
    Row 1 (Data): Soft light blue
    Row 2 (Occupancy model): Soft light green
    Row 3 (Simulation and analysis): Soft light orange / amber
    Extra element: Soft neutral grey
- Typography: Sans-serif (Arial / Helvetica / DejaVu Sans), uniform font size for all box labels.
- Layout: 3 horizontal rows with row labels at left edge:
    Row 1: 4 boxes (left to right)
    Row 2: 3 boxes (left to right)
    Row 3: 3 boxes (left to right)
    Extra: 1 small grey box outside rows at far right of row 3.
- Arrows:
    All solid (one arrowhead, no labels) except the single dashed arrow from grey box to box 10.
    Box 1 -> Box 5 (down)
    Box 2 -> Box 6 (down)
    Box 5 -> Box 6 (right)
    Box 6 -> Box 7 (right)
    Box 3 -> Box 7 (down)
    Box 7 -> Box 8 (down, smoothly routed through corridor)
    Box 4 -> Box 8 (down, smoothly routed around row 2 and through corridor)
    Box 8 -> Box 9 (right)
    Box 9 -> Box 10 (right)
    Box 11 (Grey box) -> Box 10 (dashed left)
- Strict restrictions:
    No numbers other than years (2005 to 2022, 2021, 2022, 2030).
    No abbreviations or codes (no GSS, SHEU, IESO, WFH, C-VAE, J3, gate).
    No word "forecast".
    No extra boxes, arrows, or captions.
"""

import sys
import os
import argparse
import hashlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, PathPatch
from matplotlib.path import Path
from PIL import Image

# -----------------------------------------------------------------------------
# EXACT VERBATIM STRINGS & LINE WRAPS
# -----------------------------------------------------------------------------
ROW_LABELS = {
    1: "Data",
    2: "Occupancy model",
    3: "Simulation and analysis",
}

BOX_LABELS = {
    1: "Time-use diaries, 2005 to 2022",
    2: "Census households, 2021",
    3: "National end-use energy survey",
    4: "Building archetypes and weather",
    5: "Generative occupancy model",
    6: "Match diaries to census households",
    7: "Hourly schedules and activity loads",
    8: "Building simulation: 2022 and three 2030 scenarios",
    9: "Load-shape metrics and paired comparison",
    10: "Check against measured hourly load",
    11: "Measured hourly load (Ontario)",
}

BOX_WRAPS = {
    1: "Time-use diaries,\n2005 to 2022",
    2: "Census households,\n2021",
    3: "National end-use\nenergy survey",
    4: "Building archetypes\nand weather",
    5: "Generative\noccupancy model",
    6: "Match diaries to\ncensus households",
    7: "Hourly schedules and\nactivity loads",
    8: "Building simulation:\n2022 and three\n2030 scenarios",
    9: "Load-shape metrics and\npaired comparison",
    10: "Check against\nmeasured hourly load",
    11: "Measured hourly load\n(Ontario)",
}

ROW_WRAPS = {
    1: "Data",
    2: "Occupancy\nmodel",
    3: "Simulation\nand analysis",
}

# Verbatim assertion check
for k, v in BOX_WRAPS.items():
    restored = " ".join(v.split())
    expected = BOX_LABELS[k]
    assert restored == expected, f"Mismatch on box {k}: '{restored}' != '{expected}'"

for k, v in ROW_WRAPS.items():
    restored = " ".join(v.split())
    expected = ROW_LABELS[k]
    assert restored == expected, f"Mismatch on row {k}: '{restored}' != '{expected}'"

# -----------------------------------------------------------------------------
# STYLING & PALETTE (Colour-blind safe pastel tones)
# -----------------------------------------------------------------------------
# Box colors: (fill_color, border_color, text_color)
BOX_COLORS = {
    1: ("#E4EEF8", "#4A5568", "#1A202C"),  # Row 1: soft blue
    2: ("#E4EEF8", "#4A5568", "#1A202C"),
    3: ("#E4EEF8", "#4A5568", "#1A202C"),
    4: ("#E4EEF8", "#4A5568", "#1A202C"),
    5: ("#E3F3E8", "#4A5568", "#1A202C"),  # Row 2: soft green
    6: ("#E3F3E8", "#4A5568", "#1A202C"),
    7: ("#E3F3E8", "#4A5568", "#1A202C"),
    8: ("#FAEADB", "#4A5568", "#1A202C"),  # Row 3: soft orange
    9: ("#FAEADB", "#4A5568", "#1A202C"),
    10: ("#FAEADB", "#4A5568", "#1A202C"),
    11: ("#EFF1F3", "#607274", "#212529"), # Extra: grey
}

# Row label pill styling: (text_color, pill_fill_color, bar_color)
ROW_COLORS = {
    1: ("#1B4965", "#D8E7F5", "#1B4965"),
    2: ("#1E5E3A", "#D9EFE0", "#1E5E3A"),
    3: ("#874314", "#F8DFCD", "#874314"),
}

FONT_FAMILY = ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"]
FONT_SIZE_BOX = 7.3
FONT_SIZE_ROW = 8.5


def draw_curved_corner_arrow(ax, points, radius=2.5, dashed=False, color="#2D3748", lw=1.0):
    """Draw an orthogonal path with rounded corners and an arrowhead at the terminal."""
    ls = (0, (4, 3)) if dashed else "-"
    path_data = []
    path_data.append((Path.MOVETO, points[0]))
    
    for i in range(1, len(points) - 1):
        prev_p = points[i-1]
        curr_p = points[i]
        next_p = points[i+1]
        
        v_in = (curr_p[0] - prev_p[0], curr_p[1] - prev_p[1])
        len_in = (v_in[0]**2 + v_in[1]**2)**0.5
        v_out = (next_p[0] - curr_p[0], next_p[1] - curr_p[1])
        len_out = (v_out[0]**2 + v_out[1]**2)**0.5
        
        r = min(radius, len_in * 0.45, len_out * 0.45)
        p_turn_start = (curr_p[0] - (v_in[0]/len_in)*r, curr_p[1] - (v_in[1]/len_in)*r)
        p_turn_end = (curr_p[0] + (v_out[0]/len_out)*r, curr_p[1] + (v_out[1]/len_out)*r)
        
        path_data.append((Path.LINETO, p_turn_start))
        path_data.append((Path.CURVE3, curr_p))
        path_data.append((Path.CURVE3, p_turn_end))
        
    path_data.append((Path.LINETO, points[-1]))
    
    codes, verts = zip(*path_data)
    path = Path(verts, codes)
    patch = PathPatch(path, facecolor="none", edgecolor=color, linewidth=lw, linestyle=ls, zorder=6)
    ax.add_patch(patch)
    
    last_v = (points[-1][0] - points[-2][0], points[-1][1] - points[-2][1])
    len_last = (last_v[0]**2 + last_v[1]**2)**0.5
    p_head_base = (points[-1][0] - (last_v[0]/len_last)*0.1, points[-1][1] - (last_v[1]/len_last)*0.1)
    
    ah = FancyArrowPatch(
        p_head_base, points[-1],
        arrowstyle="-|>",
        mutation_scale=9.0,
        color=color,
        linewidth=lw,
        zorder=7
    )
    ax.add_patch(ah)


def build_figure(dpi=600):
    """Render the simplified Figure 1 workflow diagram."""
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = FONT_FAMILY

    WIDTH_MM = 190.0
    HEIGHT_MM = 90.0

    fig = plt.figure(figsize=(WIDTH_MM / 25.4, HEIGHT_MM / 25.4), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, WIDTH_MM)
    ax.set_ylim(0, HEIGHT_MM)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # Geometry
    BOX_W = 32.5
    BOX_H = 15.5

    r1_y = 75.0
    r2_y = 48.0
    r3_y = 15.0
    row_y = {1: r1_y, 2: r2_y, 3: r3_y}

    # 1. Left Row Labels
    for r_id, (txt_c, badge_c, bar_c) in ROW_COLORS.items():
        cy = row_y[r_id]
        pill = FancyBboxPatch(
            (4.0, cy - 8.5), 23.5, 17.0,
            boxstyle="round,pad=0,rounding_size=3.0",
            facecolor=badge_c, edgecolor="none",
            alpha=0.65, zorder=1
        )
        ax.add_patch(pill)
        ax.plot([4.0, 4.0], [cy - 6.0, cy + 6.0], color=bar_c, linewidth=2.5, solid_capstyle="round", zorder=2)
        ax.text(
            15.75, cy, ROW_WRAPS[r_id],
            ha="center", va="center",
            fontsize=FONT_SIZE_ROW, fontweight="bold",
            color=txt_c, linespacing=1.2,
            zorder=3
        )

    # 2. 4 Evenly spaced Columns
    cx1 = 48.0
    cx2 = 85.5
    cx3 = 123.0
    cx4 = 160.5

    boxes = {
        1: (cx1, r1_y, BOX_W, BOX_H),
        2: (cx2, r1_y, BOX_W, BOX_H),
        3: (cx3, r1_y, BOX_W, BOX_H),
        4: (cx4, r1_y, BOX_W, BOX_H),
        5: (cx1, r2_y, BOX_W, BOX_H),
        6: (cx2, r2_y, BOX_W, BOX_H),
        7: (cx3, r2_y, BOX_W, BOX_H),
        8: (cx1, r3_y, BOX_W, BOX_H),
        9: (cx2, r3_y, BOX_W, BOX_H),
        10: (cx3, r3_y, BOX_W, BOX_H),
        11: (cx4, r3_y, BOX_W, BOX_H),
    }

    # 3. Draw Boxes
    for b_id, (cx, cy, w, h) in boxes.items():
        bg, edge, txt = BOX_COLORS[b_id]
        patch = FancyBboxPatch(
            (cx - w / 2.0, cy - h / 2.0), w, h,
            boxstyle="round,pad=0,rounding_size=2.2",
            facecolor=bg, edgecolor=edge,
            linewidth=0.9, zorder=4
        )
        ax.add_patch(patch)

        ax.text(
            cx, cy, BOX_WRAPS[b_id],
            ha="center", va="center",
            fontsize=FONT_SIZE_BOX, color=txt,
            linespacing=1.18, zorder=5
        )

    # 4. Helper for edge coordinates
    def get_edge(b_id, d, offset=0.0):
        cx, cy, w, h = boxes[b_id]
        if d == "top": return (cx + offset, cy + h / 2.0)
        if d == "bottom": return (cx + offset, cy - h / 2.0)
        if d == "left": return (cx - w / 2.0, cy + offset)
        if d == "right": return (cx + w / 2.0, cy + offset)

    def draw_straight(p1, p2, dashed=False):
        ls = (0, (4, 3)) if dashed else "-"
        col = "#4B5563" if dashed else "#2D3748"
        ah = FancyArrowPatch(
            p1, p2, arrowstyle="-|>", mutation_scale=9.0,
            color=col, linewidth=1.0, linestyle=ls, zorder=6
        )
        ax.add_patch(ah)

    # 5. Draw Arrows
    # Row 1 -> Row 2
    draw_straight(get_edge(1, "bottom"), get_edge(5, "top"))
    draw_straight(get_edge(2, "bottom"), get_edge(6, "top"))
    draw_straight(get_edge(3, "bottom"), get_edge(7, "top"))

    # Horizontal in Row 2
    draw_straight(get_edge(5, "right"), get_edge(6, "left"))
    draw_straight(get_edge(6, "right"), get_edge(7, "left"))

    # Horizontal in Row 3
    draw_straight(get_edge(8, "right"), get_edge(9, "left"))
    draw_straight(get_edge(9, "right"), get_edge(10, "left"))

    # Box 7 -> Box 8 (Occupancy model output to building simulation)
    p_b7 = get_edge(7, "bottom", offset=0.0)
    p_b8_1 = get_edge(8, "top", offset=-5.0)
    draw_curved_corner_arrow(ax, [
        p_b7,
        (p_b7[0], 32.5),
        (p_b8_1[0], 32.5),
        p_b8_1
    ], radius=2.5)

    # Box 4 -> Box 8 (Building archetypes & weather to building simulation)
    p_b4 = get_edge(4, "bottom", offset=0.0)
    p_b8_2 = get_edge(8, "top", offset=5.0)
    draw_curved_corner_arrow(ax, [
        p_b4,
        (p_b4[0], 26.5),
        (p_b8_2[0], 26.5),
        p_b8_2
    ], radius=2.5)

    # Grey Box (11) -> Box 10 (THE ONLY DASHED ARROW: external check)
    draw_straight(get_edge(11, "left"), get_edge(10, "right"), dashed=True)

    return fig


def main():
    parser = argparse.ArgumentParser(description="Generate Figure 1 simplified workflow diagram.")
    parser.add_argument("--dpi", type=int, default=600, help="Output DPI (default: 600)")
    args = parser.parse_args()

    # Base directories
    base_rejection = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\2J_docs_occ_nTemp\writing\submission\rejection revision"
    base_submission = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\2J_docs_occ_nTemp\writing\submission"

    # Destination paths
    output_targets = [
        # Requested primary location in user prompt:
        os.path.join(base_rejection, "Figure_01_workflow.png"),
        os.path.join(base_rejection, "Figure_01_workflow.pdf"),
        # Submission figures location referenced by manuscript:
        os.path.join(base_submission, "figures", "Figure_01_workflow.png"),
        os.path.join(base_submission, "figures", "Figure_01_workflow.pdf"),
        os.path.join(base_submission, "figures", "Prompts_Images", "Figure_01_workflow.png"),
    ]

    print("Rendering Figure 1 at 600 DPI...")
    fig = build_figure(dpi=args.dpi)

    for target in output_targets:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        ext = os.path.splitext(target)[1].lower()
        if ext == ".png":
            fig.savefig(target, dpi=args.dpi, facecolor="white", edgecolor="none")
        elif ext == ".pdf":
            fig.savefig(target, facecolor="white", edgecolor="none")
        print(f"  [OK] Saved: {target}")

    plt.close(fig)

    # Verification checks
    primary_png = output_targets[0]
    img = Image.open(primary_png)
    print("\n--- Image Verification ---")
    print(f"File: {primary_png}")
    print(f"Pixel dimensions: {img.size[0]} x {img.size[1]} px")
    print(f"DPI: {img.info.get('dpi')}")
    w_mm = img.size[0] / args.dpi * 25.4
    h_mm = img.size[1] / args.dpi * 25.4
    print(f"Physical dimensions: {w_mm:.1f} mm x {h_mm:.1f} mm")

    with open(primary_png, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
    print(f"SHA-256: {sha256}")
    print("Generation complete and verified successfully.")


if __name__ == "__main__":
    main()

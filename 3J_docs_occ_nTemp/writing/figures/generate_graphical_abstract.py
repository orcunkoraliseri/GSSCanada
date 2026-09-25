# -*- coding: utf-8 -*-
"""Generate Graphical Abstract for Building and Environment.

Specifications from:
writing/submission/figures/Prompts_Images_v4/graphicalAbstract.md

- Target size: 16.0 in x 7.0 in wide landscape.
- Target resolution: 300 DPI (4800 x 2100 px, long edge >= 3500 px).
- Canvas background: pure white (#FFFFFF), generous white space.
- Strictly flat: no 3D, no isometric, no shadows, no gradients, no photorealism.
- Palette: 4 muted, colour-blind-safe channel colours:
    Residents: Muted warm coral / terracotta (#C26D53)
    Office workers: Muted slate blue (#4A6E82)
    Shoppers: Muted sage green / olive (#6B8E68)
    Hotel guests: Muted mauve / plum (#8A5A72)
    Neutral grey for structure: #4A5568 / #718096
- Three panels reading left to right, separated by white space:
    LEFT PANEL: "Four occupancy schedules"
      - 4 flat symbols with labels: Residents, Office workers, Shoppers, Hotel guests
      - Top three gathered by bracket "time-use diaries"
      - Bed has thin line "hotel statistics"
      - Arrow leaving to the right
    CENTRE PANEL: "One mixed-use tower"
      - Tall flat tower with 4 color bands (hotel top, residential upper mid, office lower mid, shop ground)
      - Small grey box at base "shared plant"
    RIGHT PANEL:
      - Top chart "When people are present": 2 curves (code schedule dashed, survey schedule solid), different shapes
      - Bottom chart "When energy is used": 2 curves nearly on top of each other, peaking at same hour
      - Callout card: "presence shifts, energy timing holds"
      - Hour ticks at 0, 6, 12, 18, 24 with no other numbers.
- Strict restrictions:
    No other text. No numbers except hour ticks. No colour names written as text.
    No abbreviations or codes (no GSS, NECB, EUI, Leg, 2J, 3J). No logos, no title banner.
"""

import sys
import os
import argparse
import hashlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle, Polygon, PathPatch
from matplotlib.path import Path
from PIL import Image

# -----------------------------------------------------------------------------
# PALETTE
# -----------------------------------------------------------------------------
C_HOTEL = "#8A5A72"       # Muted plum / mauve (Hotel guests)
C_RESID = "#C26D53"       # Muted coral / terracotta (Residents)
C_OFFICE = "#4A6E82"      # Muted slate blue (Office workers)
C_SHOP = "#6B8E68"        # Muted sage / olive (Shoppers)

C_INK = "#1A202C"         # Main dark grey text
C_GREY_LINE = "#718096"   # Neutral grey for code schedule & lines
C_GREY_OUTLINE = "#4A5568"# Structural outlines
C_PLANT_BG = "#EDF2F7"    # Shared plant background
C_CARD_BG = "#F7FAFC"     # Callout card background

FONT_FAMILY = ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"]


def draw_house_symbol(ax, cx, cy, s=0.18, color=C_RESID):
    """Draw a clean flat house outline."""
    # Roof
    roof_pts = np.array([
        [cx - s * 1.1, cy + s * 0.05],
        [cx, cy + s * 1.0],
        [cx + s * 1.1, cy + s * 0.05]
    ])
    ax.add_patch(Polygon(roof_pts, closed=True, facecolor="none", edgecolor=color, linewidth=2.0, zorder=5))
    # Walls
    ax.add_patch(Rectangle((cx - s * 0.8, cy - s * 0.9), s * 1.6, s * 0.95,
                           facecolor="none", edgecolor=color, linewidth=2.0, zorder=5))
    # Door
    ax.add_patch(Rectangle((cx - s * 0.28, cy - s * 0.9), s * 0.56, s * 0.6,
                           facecolor=color, edgecolor="none", zorder=5))


def draw_briefcase_symbol(ax, cx, cy, s=0.18, color=C_OFFICE):
    """Draw a clean flat briefcase outline."""
    # Body
    ax.add_patch(FancyBboxPatch((cx - s * 1.0, cy - s * 0.75), s * 2.0, s * 1.4,
                               boxstyle="round,pad=0,rounding_size=0.06",
                               facecolor="none", edgecolor=color, linewidth=2.0, zorder=5))
    # Handle
    handle_pts = np.array([
        [cx - s * 0.45, cy + s * 0.65],
        [cx - s * 0.45, cy + s * 1.0],
        [cx + s * 0.45, cy + s * 1.0],
        [cx + s * 0.45, cy + s * 0.65]
    ])
    ax.plot(handle_pts[:, 0], handle_pts[:, 1], color=color, linewidth=1.8, zorder=5)
    # Mid-seam line
    ax.plot([cx - s * 0.95, cx + s * 0.95], [cy - s * 0.05, cy - s * 0.05], color=color, linewidth=1.2, zorder=5)
    # Latch
    ax.add_patch(Rectangle((cx - s * 0.18, cy - s * 0.2), s * 0.36, s * 0.3,
                           facecolor=color, edgecolor="none", zorder=6))


def draw_shopping_bag_symbol(ax, cx, cy, s=0.18, color=C_SHOP):
    """Draw a clean flat shopping bag outline."""
    # Bag body
    bag_pts = np.array([
        [cx - s * 0.75, cy + s * 0.65],
        [cx - s * 0.9, cy - s * 0.85],
        [cx + s * 0.9, cy - s * 0.85],
        [cx + s * 0.75, cy + s * 0.65]
    ])
    ax.add_patch(Polygon(bag_pts, closed=True, facecolor="none", edgecolor=color, linewidth=2.0, zorder=5))
    # Handles (two arches)
    angles = np.linspace(0, np.pi, 30)
    hx = cx + s * 0.4 * np.cos(angles)
    hy = cy + s * 0.65 + s * 0.45 * np.sin(angles)
    ax.plot(hx, hy, color=color, linewidth=1.8, zorder=5)


def draw_bed_symbol(ax, cx, cy, s=0.18, color=C_HOTEL):
    """Draw a clean flat bed outline."""
    # Headboard
    ax.plot([cx - s * 1.1, cx - s * 1.1], [cy - s * 0.7, cy + s * 0.85], color=color, linewidth=2.2, solid_capstyle="round", zorder=5)
    # Footboard
    ax.plot([cx + s * 1.1, cx + s * 1.1], [cy - s * 0.7, cy + s * 0.35], color=color, linewidth=2.2, solid_capstyle="round", zorder=5)
    # Mattress / Frame
    ax.plot([cx - s * 1.1, cx + s * 1.1], [cy - s * 0.25, cy - s * 0.25], color=color, linewidth=2.0, zorder=5)
    # Blanket / duvet
    ax.add_patch(FancyBboxPatch((cx - s * 0.3, cy - s * 0.25), s * 1.35, s * 0.45,
                               boxstyle="round,pad=0,rounding_size=0.06",
                               facecolor="none", edgecolor=color, linewidth=1.6, zorder=5))
    # Pillow
    ax.add_patch(FancyBboxPatch((cx - s * 0.95, cy - s * 0.15), s * 0.55, s * 0.45,
                               boxstyle="round,pad=0,rounding_size=0.06",
                               facecolor=color, edgecolor="none", zorder=5))


def build_figure(dpi=300):
    """Build the graphical abstract figure."""
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = FONT_FAMILY

    W, H = 16.0, 7.0
    fig = plt.figure(figsize=(W, H), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # =========================================================================
    # LEFT PANEL: Four occupancy schedules
    # =========================================================================
    p1_cx = 2.7
    ax.text(p1_cx, 6.2, "Four occupancy schedules", ha="center", va="center",
            fontsize=13.0, fontweight="bold", color=C_INK)

    sym_x = 1.05
    lbl_x = 1.45

    y_res = 5.15
    y_off = 4.20
    y_shop = 3.25
    y_hotel = 1.85

    # Symbols and labels
    draw_house_symbol(ax, sym_x, y_res, s=0.22, color=C_RESID)
    ax.text(lbl_x, y_res, "Residents", ha="left", va="center",
            fontsize=11.0, fontweight="bold", color=C_INK)

    draw_briefcase_symbol(ax, sym_x, y_off, s=0.22, color=C_OFFICE)
    ax.text(lbl_x, y_off, "Office workers", ha="left", va="center",
            fontsize=11.0, fontweight="bold", color=C_INK)

    draw_shopping_bag_symbol(ax, sym_x, y_shop, s=0.22, color=C_SHOP)
    ax.text(lbl_x, y_shop, "Shoppers", ha="left", va="center",
            fontsize=11.0, fontweight="bold", color=C_INK)

    draw_bed_symbol(ax, sym_x, y_hotel, s=0.22, color=C_HOTEL)
    ax.text(lbl_x, y_hotel, "Hotel guests", ha="left", va="center",
            fontsize=11.0, fontweight="bold", color=C_INK)

    # Bracket gathering top three (Residents, Office workers, Shoppers)
    br_x = 3.3
    # Curved bracket using Path
    b_top = y_res + 0.15
    b_bot = y_shop - 0.15
    b_mid = (b_top + b_bot) / 2.0
    br_path = [
        (Path.MOVETO, (br_x - 0.08, b_top)),
        (Path.CURVE3, (br_x, b_top)),
        (Path.LINETO, (br_x, b_mid + 0.12)),
        (Path.CURVE3, (br_x + 0.12, b_mid)),
        (Path.CURVE3, (br_x, b_mid - 0.12)),
        (Path.LINETO, (br_x, b_bot)),
        (Path.CURVE3, (br_x - 0.08, b_bot)),
    ]
    codes, verts = zip(*br_path)
    ax.add_patch(PathPatch(Path(verts, codes), facecolor="none", edgecolor=C_GREY_LINE, linewidth=1.2, zorder=4))

    ax.text(br_x + 0.22, b_mid, "time-use diaries", ha="left", va="center",
            fontsize=9.2, color=C_GREY_LINE)

    # Thin line for Hotel statistics
    line_y = y_hotel
    line_x1 = 2.9
    line_x2 = 3.6
    ax.plot([line_x1, line_x2], [line_y, line_y], color=C_GREY_LINE, linewidth=1.2, zorder=4)
    ax.text(line_x2 + 0.1, line_y, "hotel statistics", ha="left", va="center",
            fontsize=9.2, color=C_GREY_LINE)

    # Arrow leaving panel to the right
    arrow_p1 = FancyArrowPatch(
        (4.75, 3.4), (5.75, 3.4),
        arrowstyle="-|>", mutation_scale=12.0,
        color=C_GREY_OUTLINE, linewidth=1.3, zorder=6
    )
    ax.add_patch(arrow_p1)

    # =========================================================================
    # CENTRE PANEL: One mixed-use tower
    # =========================================================================
    p2_cx = 7.7
    ax.text(p2_cx, 6.2, "One mixed-use tower", ha="center", va="center",
            fontsize=13.0, fontweight="bold", color=C_INK)

    # Tower outline & dimensions
    tw_w = 2.4
    tw_x = p2_cx - tw_w / 2.0  # 6.5
    tw_y0 = 1.35
    tw_h = 4.25

    # Main tower outer rectangle
    ax.add_patch(Rectangle((tw_x, tw_y0), tw_w, tw_h,
                           facecolor="white", edgecolor=C_GREY_OUTLINE, linewidth=1.6, zorder=3))

    # Bands from top to bottom:
    # 1. Hotel band (top)
    h_hotel = 0.95
    y_h_bot = tw_y0 + tw_h - h_hotel
    ax.add_patch(Rectangle((tw_x, y_h_bot), tw_w, h_hotel,
                           facecolor=C_HOTEL, edgecolor="white", linewidth=1.2, zorder=4))
    ax.text(p2_cx, y_h_bot + h_hotel / 2.0, "hotel", ha="center", va="center",
            fontsize=10.5, fontweight="bold", color="white", zorder=5)

    # 2. Residential bands (upper middle)
    h_resid_tot = 1.45
    y_r_bot = y_h_bot - h_resid_tot
    n_r_floors = 3
    for i in range(n_r_floors):
        fy = y_r_bot + i * (h_resid_tot / n_r_floors)
        fh = h_resid_tot / n_r_floors
        ax.add_patch(Rectangle((tw_x, fy), tw_w, fh,
                               facecolor=C_RESID, edgecolor="white", linewidth=1.0, zorder=4))
    ax.text(p2_cx, y_r_bot + h_resid_tot / 2.0, "residential", ha="center", va="center",
            fontsize=10.5, fontweight="bold", color="white", zorder=5)

    # 3. Office bands (lower middle)
    h_office_tot = 1.40
    y_o_bot = y_r_bot - h_office_tot
    n_o_floors = 3
    for i in range(n_o_floors):
        fy = y_o_bot + i * (h_office_tot / n_o_floors)
        fh = h_office_tot / n_o_floors
        ax.add_patch(Rectangle((tw_x, fy), tw_w, fh,
                               facecolor=C_OFFICE, edgecolor="white", linewidth=1.0, zorder=4))
    ax.text(p2_cx, y_o_bot + h_office_tot / 2.0, "office", ha="center", va="center",
            fontsize=10.5, fontweight="bold", color="white", zorder=5)

    # 4. Thin shop band at street level
    h_shop = 0.45
    y_s_bot = tw_y0
    ax.add_patch(Rectangle((tw_x, y_s_bot), tw_w, h_shop,
                           facecolor=C_SHOP, edgecolor="white", linewidth=1.0, zorder=4))
    ax.text(p2_cx, y_s_bot + h_shop / 2.0, "shop", ha="center", va="center",
            fontsize=9.5, fontweight="bold", color="white", zorder=5)

    # Ground line
    ax.plot([tw_x - 0.4, tw_x + tw_w + 0.4], [tw_y0, tw_y0], color=C_GREY_OUTLINE, linewidth=1.5, zorder=3)

    # Shared plant at the base
    plant_w = 1.4
    plant_h = 0.48
    plant_x = p2_cx - plant_w / 2.0
    plant_y = 0.65
    ax.plot([p2_cx, p2_cx], [plant_y + plant_h, tw_y0], color=C_GREY_OUTLINE, linewidth=1.2, zorder=3)
    ax.add_patch(FancyBboxPatch((plant_x, plant_y), plant_w, plant_h,
                               boxstyle="round,pad=0,rounding_size=0.06",
                               facecolor=C_PLANT_BG, edgecolor=C_GREY_OUTLINE, linewidth=1.1, zorder=4))
    ax.text(p2_cx, plant_y + plant_h / 2.0, "shared plant", ha="center", va="center",
            fontsize=9.0, color=C_INK, zorder=5)

    # Arrow leaving centre panel to the right
    arrow_p2 = FancyArrowPatch(
        (8.95, 3.4), (9.85, 3.4),
        arrowstyle="-|>", mutation_scale=12.0,
        color=C_GREY_OUTLINE, linewidth=1.3, zorder=6
    )
    ax.add_patch(arrow_p2)

    # =========================================================================
    # RIGHT PANEL: Two small flat line charts
    # =========================================================================
    p3_cx = 12.8
    chart_w = 3.8
    chart_h = 1.65
    chart_x0 = 10.3

    # Hours grid: 0 to 24
    hours = np.linspace(0, 24, 250)

    # -------------------------------------------------------------------------
    # TOP CHART: When people are present
    # -------------------------------------------------------------------------
    c1_y0 = 4.05
    ax.text(chart_x0 + chart_w / 2.0, c1_y0 + chart_h + 0.5, "When people are present",
            ha="center", va="bottom", fontsize=12.0, fontweight="bold", color=C_INK)

    # Top Chart Axes
    ax.plot([chart_x0, chart_x0 + chart_w], [c1_y0, c1_y0], color=C_GREY_OUTLINE, linewidth=1.1, zorder=3)
    ax.plot([chart_x0, chart_x0], [c1_y0, c1_y0 + chart_h], color=C_GREY_OUTLINE, linewidth=1.1, zorder=3)

    # Hour ticks
    ticks = [0, 6, 12, 18, 24]
    for t in ticks:
        tx = chart_x0 + (t / 24.0) * chart_w
        ax.plot([tx, tx], [c1_y0, c1_y0 - 0.06], color=C_GREY_OUTLINE, linewidth=1.0, zorder=3)
        ax.text(tx, c1_y0 - 0.16, str(t), ha="center", va="top", fontsize=8.2, color=C_INK)

    # Curves for Top Chart:
    # "two thin curves for the same use, one dashed grey labelled 'code schedule'
    # and one solid in the hotel colour labelled 'survey schedule'.
    # The two curves have clearly DIFFERENT shapes: the survey curve is high in the evening
    # and night where the code curve is low."
    # Code schedule: classic daytime office-like curve peaking at noon (12h)
    curve_code_1 = 0.08 + 0.75 * np.exp(-((hours - 13.0) / 4.0)**2)
    # Survey schedule: residential/hotel-like curve high in evening/night, low mid-day
    curve_survey_1 = 0.15 + 0.78 * (0.45 * (1.0 / (1.0 + np.exp(-(hours - 16.5) / 1.5))) +
                                   0.55 * np.exp(-((hours - 20.5) / 3.5)**2) +
                                   0.45 * (1.0 / (1.0 + np.exp((hours - 7.5) / 1.5))))
    # Normalize to fit chart_h nicely
    y_c1_code = c1_y0 + (curve_code_1 / 1.05) * (chart_h - 0.2)
    y_c1_survey = c1_y0 + (curve_survey_1 / 1.05) * (chart_h - 0.2)
    x_hours = chart_x0 + (hours / 24.0) * chart_w

    ax.plot(x_hours, y_c1_code, linestyle="--", color=C_GREY_LINE, linewidth=1.6, zorder=4)
    ax.plot(x_hours, y_c1_survey, linestyle="-", color=C_HOTEL, linewidth=2.0, zorder=5)

    # Labels for top curves
    ax.text(chart_x0 + 0.45 * chart_w, c1_y0 + 0.88 * chart_h, "code schedule",
            ha="center", va="bottom", fontsize=8.5, color=C_GREY_LINE, style="italic")
    ax.text(chart_x0 + 0.84 * chart_w, c1_y0 + 0.82 * chart_h, "survey schedule",
            ha="center", va="bottom", fontsize=8.5, color=C_HOTEL, fontweight="bold")

    # -------------------------------------------------------------------------
    # BOTTOM CHART: When energy is used
    # -------------------------------------------------------------------------
    c2_y0 = 1.35
    ax.text(chart_x0 + chart_w / 2.0, c2_y0 + chart_h + 0.5, "When energy is used",
            ha="center", va="bottom", fontsize=12.0, fontweight="bold", color=C_INK)

    # Bottom Chart Axes
    ax.plot([chart_x0, chart_x0 + chart_w], [c2_y0, c2_y0], color=C_GREY_OUTLINE, linewidth=1.1, zorder=3)
    ax.plot([chart_x0, chart_x0], [c2_y0, c2_y0 + chart_h], color=C_GREY_OUTLINE, linewidth=1.1, zorder=3)

    for t in ticks:
        tx = chart_x0 + (t / 24.0) * chart_w
        ax.plot([tx, tx], [c2_y0, c2_y0 - 0.06], color=C_GREY_OUTLINE, linewidth=1.0, zorder=3)
        ax.text(tx, c2_y0 - 0.16, str(t), ha="center", va="top", fontsize=8.2, color=C_INK)

    # Curves for Bottom Chart:
    # "the same two line styles, dashed grey 'code schedule' and solid 'survey schedule',
    # nearly on top of each other, with their highest point at the same hour."
    # Morning plant start-up peak around 7-8 AM + afternoon load, peaking at 14h
    peak_h = 14.0
    curve_base = 0.12 + 0.80 * np.exp(-((hours - peak_h) / 3.8)**2) + 0.25 * np.exp(-((hours - 8.0) / 1.8)**2)
    curve_code_2 = curve_base
    curve_survey_2 = curve_base * 0.98 + 0.02 * np.sin(hours / 3.0)

    y_c2_code = c2_y0 + (curve_code_2 / 1.15) * (chart_h - 0.2)
    y_c2_survey = c2_y0 + (curve_survey_2 / 1.15) * (chart_h - 0.2)

    ax.plot(x_hours, y_c2_code, linestyle="--", color=C_GREY_LINE, linewidth=1.6, zorder=4)
    ax.plot(x_hours, y_c2_survey, linestyle="-", color=C_HOTEL, linewidth=2.0, zorder=5)

    # Labels for bottom curves
    ax.text(chart_x0 + 0.25 * chart_w, c2_y0 + 0.68 * chart_h, "code schedule",
            ha="left", va="bottom", fontsize=8.2, color=C_GREY_LINE, style="italic")
    ax.text(chart_x0 + 0.25 * chart_w, c2_y0 + 0.52 * chart_h, "survey schedule",
            ha="left", va="bottom", fontsize=8.2, color=C_HOTEL, fontweight="bold")

    # -------------------------------------------------------------------------
    # CALLOUT CARD: "presence shifts, energy timing holds"
    # -------------------------------------------------------------------------
    card_w = 1.35
    card_h = 0.80
    card_x = chart_x0 + chart_w + 0.2
    card_y = c2_y0 + 0.45

    ax.add_patch(FancyBboxPatch((card_x, card_y), card_w, card_h,
                               boxstyle="round,pad=0,rounding_size=0.08",
                               facecolor=C_CARD_BG, edgecolor=C_GREY_OUTLINE, linewidth=1.0, zorder=6))
    ax.text(card_x + card_w / 2.0, card_y + card_h / 2.0,
            "presence shifts,\nenergy timing\nholds",
            ha="center", va="center", fontsize=8.2, fontweight="bold",
            color=C_INK, linespacing=1.2, zorder=7)

    return fig


def main():
    parser = argparse.ArgumentParser(description="Generate Graphical Abstract.")
    parser.add_argument("--dpi", type=int, default=300, help="Output DPI (default: 300)")
    args = parser.parse_args()

    v4_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\writing\submission\figures\Prompts_Images_v4"
    figures_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\writing\submission\figures"
    writing_fig_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\writing\figures"

    output_targets = [
        os.path.join(v4_dir, "graphicalAbstract.png"),
        os.path.join(figures_dir, "graphicalAbstract.png"),
        os.path.join(figures_dir, "graphicalAbstract.pdf"),
        os.path.join(writing_fig_dir, "graphicalAbstract.png"),
        os.path.join(writing_fig_dir, "graphicalAbstract.pdf"),
    ]

    print(f"Rendering Graphical Abstract at {args.dpi} DPI...")
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


if __name__ == "__main__":
    main()

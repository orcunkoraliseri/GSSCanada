# -*- coding: utf-8 -*-
"""Generate Method Figures M1, M2, M3, and M4 for Applied Energy.

Specifications from:
- submission/figures/Prompts_Images/Figure_M1_diary_to_hourly_prompt.md
- submission/figures/Prompts_Images/Figure_M2_raking_prompt.md
- submission/figures/Prompts_Images/Figure_M3_activity_to_power_prompt.md
- submission/figures/Prompts_Images/Figure_M4_2030_scenarios_prompt.md

Design constraints:
- 600 DPI, white background, flat design, thin dark-grey outlines (#4A5568).
- Sans-serif typography (Arial / DejaVu Sans).
- Exact label texts and numbers word for word; no extra text, captions, or unprompted legends.
- Strict adherence to acceptance checklists.
"""

import os
import sys
import argparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
from PIL import Image

plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Helvetica", "sans-serif"]
plt.rcParams["font.family"] = "sans-serif"

COLOR_OUTLINE = "#4A5568"
COLOR_TEXT = "#1A202C"
COLOR_MUTED = "#4A5568"
COLOR_HOME = "#BAE6FD"  # Light blue for "At home"
COLOR_AWAY = "#FFFFFF"  # White for "Away"
COLOR_ORANGE_OUTLINE = "#EA580C"  # Orange outline for changed record


# =============================================================================
# FIGURE M1: 10-Minute Diary to Hourly Household Schedule
# =============================================================================
def build_figure_m1(dpi=600):
    """Figure M1: Conversion of a ten-minute diary into an hourly household occupancy value.
    Dimensions: 190 mm wide x 80 mm tall, 600 DPI.
    """
    WIDTH_MM = 190.0
    HEIGHT_MM = 80.0

    fig = plt.figure(figsize=(WIDTH_MM / 25.4, HEIGHT_MM / 25.4), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, WIDTH_MM)
    ax.set_ylim(0, HEIGHT_MM)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    y_heading = 72.0

    # -------------------------------------------------------------------------
    # Panel 1: 1. Ten-minute diary
    # -------------------------------------------------------------------------
    x_p1_start = 18.0
    c1_w = 7.6
    c1_h = 6.2
    y_a = 53.5
    y_b = 35.5
    p1_total_w = 6 * c1_w
    p1_center_x = x_p1_start + 0.5 * p1_total_w

    ax.text(p1_center_x, y_heading, "1. Ten-minute diary", fontsize=8.2, fontweight="bold",
            ha="center", va="bottom", color=COLOR_TEXT)

    # Person labels
    ax.text(4.5, y_a + 0.5 * c1_h, "Person A", fontsize=7.2, ha="left", va="center", color=COLOR_TEXT)
    ax.text(4.5, y_b + 0.5 * c1_h, "Person B", fontsize=7.2, ha="left", va="center", color=COLOR_TEXT)

    # Time ruler above cells (spanning 6 cells: 0 to 3, 3 to 6)
    y_ruler = 63.5
    ax.plot([x_p1_start, x_p1_start + p1_total_w], [y_ruler, y_ruler], color=COLOR_OUTLINE, lw=0.8)
    for tick_idx in [0, 3, 6]:
        tx = x_p1_start + tick_idx * c1_w
        ax.plot([tx, tx], [y_ruler - 1.2, y_ruler + 1.2], color=COLOR_OUTLINE, lw=0.8)

    ax.text(x_p1_start + 1.5 * c1_w, y_ruler + 1.8, "30 min", fontsize=6.8, ha="center", va="bottom", color=COLOR_MUTED)
    ax.text(x_p1_start + 4.5 * c1_w, y_ruler + 1.8, "30 min", fontsize=6.8, ha="center", va="bottom", color=COLOR_MUTED)

    # Person A cells: home, home, away | away, away, home
    person_a_colors = [COLOR_HOME, COLOR_HOME, COLOR_AWAY, COLOR_AWAY, COLOR_AWAY, COLOR_HOME]
    for i, col in enumerate(person_a_colors):
        rect = Rectangle((x_p1_start + i * c1_w, y_a), c1_w, c1_h,
                         facecolor=col, edgecolor=COLOR_OUTLINE, lw=0.8)
        ax.add_patch(rect)

    # Under Person A's first three cells: tiny activity words "Cooking", "Cooking", "Eating"
    ax.text(x_p1_start + 0.5 * c1_w, y_a - 2.8, "Cooking", fontsize=5.2, ha="center", va="top", color=COLOR_MUTED)
    ax.text(x_p1_start + 1.5 * c1_w, y_a - 2.8, "Cooking", fontsize=5.2, ha="center", va="top", color=COLOR_MUTED)
    ax.text(x_p1_start + 2.5 * c1_w, y_a - 2.8, "Eating", fontsize=5.2, ha="center", va="top", color=COLOR_MUTED)

    # Person B cells: home, home, home | home, away, home
    person_b_colors = [COLOR_HOME, COLOR_HOME, COLOR_HOME, COLOR_HOME, COLOR_AWAY, COLOR_HOME]
    for i, col in enumerate(person_b_colors):
        rect = Rectangle((x_p1_start + i * c1_w, y_b), c1_w, c1_h,
                         facecolor=col, edgecolor=COLOR_OUTLINE, lw=0.8)
        ax.add_patch(rect)

    # Arrow from Panel 1 to Panel 2
    arr1 = FancyArrowPatch((x_p1_start + p1_total_w + 3.0, 48.0), (x_p1_start + p1_total_w + 8.5, 48.0),
                           arrowstyle="-|>", mutation_scale=8.0, color=COLOR_OUTLINE, lw=1.0)
    ax.add_patch(arr1)

    # -------------------------------------------------------------------------
    # Panel 2: 2. Thirty-minute slots
    # -------------------------------------------------------------------------
    x_p2_start = x_p1_start + p1_total_w + 11.5
    c2_w = 16.5
    c2_h = 6.2
    p2_total_w = 2 * c2_w
    p2_center_x = x_p2_start + 0.5 * p2_total_w

    ax.text(p2_center_x, y_heading, "2. Thirty-minute slots", fontsize=8.2, fontweight="bold",
            ha="center", va="bottom", color=COLOR_TEXT)

    # Person A: home | away
    rect_a1 = Rectangle((x_p2_start, y_a), c2_w, c2_h, facecolor=COLOR_HOME, edgecolor=COLOR_OUTLINE, lw=0.8)
    rect_a2 = Rectangle((x_p2_start + c2_w, y_a), c2_w, c2_h, facecolor=COLOR_AWAY, edgecolor=COLOR_OUTLINE, lw=0.8)
    ax.add_patch(rect_a1)
    ax.add_patch(rect_a2)

    # Under Person A's first cell: "Cooking" with note "Activity = most frequent of 3"
    ax.text(x_p2_start + 0.5 * c2_w, y_a - 2.5, "Cooking", fontsize=6.2, fontweight="bold",
            ha="center", va="top", color=COLOR_TEXT)
    ax.text(x_p2_start + 0.5 * c2_w, y_a - 6.2, "Activity = most frequent of 3", fontsize=5.4,
            ha="center", va="top", color=COLOR_MUTED)

    # Person B: home | home
    rect_b1 = Rectangle((x_p2_start, y_b), c2_w, c2_h, facecolor=COLOR_HOME, edgecolor=COLOR_OUTLINE, lw=0.8)
    rect_b2 = Rectangle((x_p2_start + c2_w, y_b), c2_w, c2_h, facecolor=COLOR_HOME, edgecolor=COLOR_OUTLINE, lw=0.8)
    ax.add_patch(rect_b1)
    ax.add_patch(rect_b2)

    # Note under Panel 2: "At home if 2 of 3 ten-minute slots are at home"
    ax.text(p2_center_x, y_b - 5.5, "At home if 2 of 3 ten-minute slots are at home",
            fontsize=5.8, ha="center", va="top", color=COLOR_MUTED)

    # Arrow from Panel 2 to Panel 3
    arr2 = FancyArrowPatch((x_p2_start + p2_total_w + 3.0, 48.0), (x_p2_start + p2_total_w + 8.5, 48.0),
                           arrowstyle="-|>", mutation_scale=8.0, color=COLOR_OUTLINE, lw=1.0)
    ax.add_patch(arr2)

    # -------------------------------------------------------------------------
    # Panel 3: 3. Household average
    # -------------------------------------------------------------------------
    x_p3_start = x_p2_start + p2_total_w + 11.5
    c3_w = 14.5
    c3_h = 11.5
    y_p3 = 42.0
    p3_total_w = 2 * c3_w
    p3_center_x = x_p3_start + 0.5 * p3_total_w

    ax.text(p3_center_x, y_heading, "3. Household average", fontsize=8.2, fontweight="bold",
            ha="center", va="bottom", color=COLOR_TEXT)

    rect_hh1 = Rectangle((x_p3_start, y_p3), c3_w, c3_h, facecolor=COLOR_HOME, edgecolor=COLOR_OUTLINE, lw=0.8)
    rect_hh2 = Rectangle((x_p3_start + c3_w, y_p3), c3_w, c3_h, facecolor=COLOR_AWAY, edgecolor=COLOR_OUTLINE, lw=0.8)
    ax.add_patch(rect_hh1)
    ax.add_patch(rect_hh2)

    ax.text(x_p3_start + 0.5 * c3_w, y_p3 + 0.5 * c3_h, "1.0", fontsize=9.2, fontweight="bold",
            ha="center", va="center", color=COLOR_TEXT)
    ax.text(x_p3_start + 1.5 * c3_w, y_p3 + 0.5 * c3_h, "0.5", fontsize=9.2, fontweight="bold",
            ha="center", va="center", color=COLOR_TEXT)

    # Note: "Share of household members at home"
    ax.text(p3_center_x, y_p3 - 5.5, "Share of household\nmembers at home",
            fontsize=6.0, ha="center", va="top", color=COLOR_MUTED)

    # Arrow from Panel 3 to Panel 4
    arr3 = FancyArrowPatch((x_p3_start + p3_total_w + 3.0, 48.0), (x_p3_start + p3_total_w + 8.5, 48.0),
                           arrowstyle="-|>", mutation_scale=8.0, color=COLOR_OUTLINE, lw=1.0)
    ax.add_patch(arr3)

    # -------------------------------------------------------------------------
    # Panel 4: 4. Hourly value
    # -------------------------------------------------------------------------
    x_p4 = x_p3_start + p3_total_w + 11.5
    c4_w = 17.5
    c4_h = 11.5
    y_p4 = 42.0
    p4_center_x = x_p4 + 0.5 * c4_w

    ax.text(p4_center_x, y_heading, "4. Hourly value", fontsize=8.2, fontweight="bold",
            ha="center", va="bottom", color=COLOR_TEXT)

    rect_h = Rectangle((x_p4, y_p4), c4_w, c4_h, facecolor=COLOR_AWAY, edgecolor=COLOR_OUTLINE, lw=0.8)
    ax.add_patch(rect_h)

    ax.text(p4_center_x, y_p4 + 0.5 * c4_h, "0.75", fontsize=9.5, fontweight="bold",
            ha="center", va="center", color=COLOR_TEXT)

    # Notes under Panel 4
    ax.text(p4_center_x, y_p4 - 5.5, "Mean of the two\n30-minute values",
            fontsize=6.0, ha="center", va="top", color=COLOR_MUTED)
    ax.text(p4_center_x, y_p4 - 15.0, "Clock shifted so the\nday starts at midnight",
            fontsize=5.8, ha="center", va="top", color=COLOR_MUTED)

    return fig


# =============================================================================
# FIGURE M2: Raking At-Home Share to a Target
# =============================================================================
def build_figure_m2(dpi=600):
    """Figure M2: Adjustment of the at-home count in one time slot to its target.
    Dimensions: 190 mm wide x 70 mm tall, 600 DPI.
    """
    WIDTH_MM = 190.0
    HEIGHT_MM = 70.0

    fig = plt.figure(figsize=(WIDTH_MM / 25.4, HEIGHT_MM / 25.4), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, WIDTH_MM)
    ax.set_ylim(0, HEIGHT_MM)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    y_heading = 56.0
    y_row = 38.5
    sq_size = 4.8
    sq_gap = 1.3
    sq_r = 0.8

    # -------------------------------------------------------------------------
    # Panel 1: Before
    # -------------------------------------------------------------------------
    p1_start_x = 5.0
    p1_total_w = 10 * sq_size + 9 * sq_gap
    p1_center_x = p1_start_x + 0.5 * p1_total_w

    ax.text(p1_center_x, y_heading, "Before", fontsize=9.0, fontweight="bold",
            ha="center", va="bottom", color=COLOR_TEXT)

    # 10 squares: blue, white, blue, white, white, blue, white, white, blue, white
    p1_pattern = [True, False, True, False, False, True, False, False, True, False]

    for i, is_home in enumerate(p1_pattern):
        x = p1_start_x + i * (sq_size + sq_gap)
        col = COLOR_HOME if is_home else COLOR_AWAY
        patch = FancyBboxPatch((x, y_row), sq_size, sq_size,
                               boxstyle=f"round,pad=0,rounding_size={sq_r}",
                               facecolor=col, edgecolor=COLOR_OUTLINE, lw=0.9)
        ax.add_patch(patch)

    ax.text(p1_center_x, y_row - 6.5, "4 of 10 at home", fontsize=7.5,
            ha="center", va="top", color=COLOR_TEXT)

    # Arrow Panel 1 -> Panel 2
    arr1 = FancyArrowPatch((p1_start_x + p1_total_w + 3.0, y_row + 0.5 * sq_size),
                           (p1_start_x + p1_total_w + 9.5, y_row + 0.5 * sq_size),
                           arrowstyle="-|>", mutation_scale=8.5, color=COLOR_OUTLINE, lw=1.0)
    ax.add_patch(arr1)

    # -------------------------------------------------------------------------
    # Panel 2: Target
    # -------------------------------------------------------------------------
    box_w = 44.0
    box_h = 24.0
    box_x = 74.5
    box_y = y_row - 9.5
    p2_center_x = box_x + 0.5 * box_w

    ax.text(p2_center_x, y_heading, "Target", fontsize=9.0, fontweight="bold",
            ha="center", va="bottom", color=COLOR_TEXT)

    box_patch = FancyBboxPatch((box_x, box_y), box_w, box_h,
                               boxstyle="round,pad=0,rounding_size=1.5",
                               facecolor="#F8FAFC", edgecolor=COLOR_OUTLINE, lw=0.9)
    ax.add_patch(box_patch)

    ax.text(p2_center_x, box_y + box_h - 5.0, "Target share: 0.6",
            fontsize=7.2, ha="center", va="center", color=COLOR_TEXT)
    ax.text(p2_center_x, box_y + box_h - 11.8, "Target count: 0.6 x 10 = 6",
            fontsize=7.2, ha="center", va="center", color=COLOR_TEXT)
    ax.text(p2_center_x, box_y + box_h - 18.5, "Records to change: 6 - 4 = 2",
            fontsize=7.2, ha="center", va="center", color=COLOR_TEXT)

    # Arrow Panel 2 -> Panel 3
    arr2 = FancyArrowPatch((box_x + box_w + 3.0, y_row + 0.5 * sq_size),
                           (box_x + box_w + 9.5, y_row + 0.5 * sq_size),
                           arrowstyle="-|>", mutation_scale=8.5, color=COLOR_OUTLINE, lw=1.0)
    ax.add_patch(arr2)

    # -------------------------------------------------------------------------
    # Panel 3: After
    # -------------------------------------------------------------------------
    p3_start_x = 129.0
    p3_total_w = 10 * sq_size + 9 * sq_gap
    p3_center_x = p3_start_x + 0.5 * p3_total_w

    ax.text(p3_center_x, y_heading, "After", fontsize=9.0, fontweight="bold",
            ha="center", va="bottom", color=COLOR_TEXT)

    # Same order, but squares 2 and 7 (counting from left) are light blue with orange outline
    changed_indices = {1, 6}  # 0-based: square 2 and square 7

    for i, orig_home in enumerate(p1_pattern):
        x = p3_start_x + i * (sq_size + sq_gap)
        is_changed = (i in changed_indices)
        col = COLOR_HOME if (orig_home or is_changed) else COLOR_AWAY
        ec = COLOR_ORANGE_OUTLINE if is_changed else COLOR_OUTLINE
        lw = 2.0 if is_changed else 0.9

        patch = FancyBboxPatch((x, y_row), sq_size, sq_size,
                               boxstyle=f"round,pad=0,rounding_size={sq_r}",
                               facecolor=col, edgecolor=ec, lw=lw)
        ax.add_patch(patch)

    # Pointer note under changed squares:
    # "Changed first: records where the activity changes at this slot"
    sq2_cx = p3_start_x + 1 * (sq_size + sq_gap) + 0.5 * sq_size  # 137.5
    sq7_cx = p3_start_x + 6 * (sq_size + sq_gap) + 0.5 * sq_size  # 168.0
    mid_changed_x = 0.5 * (sq2_cx + sq7_cx)  # 152.75

    # Center "6 of 10 at home" directly between the two changed square columns (137.5 to 168.0)
    # with wide horizontal clearance (>7.5 mm) on both left and right from the vertical pointers
    ax.text(mid_changed_x, y_row - 6.5, "6 of 10 at home", fontsize=7.2,
            ha="center", va="top", color=COLOR_TEXT)

    note_y = 13.0
    ax.text(mid_changed_x, note_y, "Changed first: records where the\nactivity changes at this slot",
            fontsize=6.0, ha="center", va="top", color=COLOR_TEXT)

    # Clean branched orthogonal thin pointers connecting the note to both changed squares
    y_branch = 16.5
    ax.plot([mid_changed_x, mid_changed_x], [note_y + 0.6, y_branch],
            color=COLOR_ORANGE_OUTLINE, lw=0.9)
    ax.plot([sq2_cx, sq7_cx], [y_branch, y_branch],
            color=COLOR_ORANGE_OUTLINE, lw=0.9)
    ax.annotate("", xy=(sq2_cx, y_row - 0.6), xytext=(sq2_cx, y_branch),
                arrowprops=dict(arrowstyle="->", color=COLOR_ORANGE_OUTLINE, lw=0.9))
    ax.annotate("", xy=(sq7_cx, y_row - 0.6), xytext=(sq7_cx, y_branch),
                arrowprops=dict(arrowstyle="->", color=COLOR_ORANGE_OUTLINE, lw=0.9))

    return fig


# =============================================================================
# FIGURE M3: Activity to Power Diagram
# =============================================================================
def draw_person_silhouette(ax, center_x, center_y, scale=1.0, color="#64748B"):
    """Draw a clean geometric person silhouette (head circle + rounded shoulder torso)."""
    head_r = 1.35 * scale
    head = Circle((center_x, center_y + 1.7 * scale), head_r, facecolor=color, edgecolor="none")
    ax.add_patch(head)

    torso_w = 4.0 * scale
    torso_h = 2.6 * scale
    torso = FancyBboxPatch((center_x - 0.5 * torso_w, center_y - 2.0 * scale), torso_w, torso_h,
                           boxstyle="round,pad=0,rounding_size=1.2",
                           facecolor=color, edgecolor="none")
    ax.add_patch(torso)


def build_figure_m3(dpi=600):
    """Figure M3: Construction of household equipment power from the activities of the people at home.
    Dimensions: 190 mm wide x 90 mm tall, 600 DPI.
    """
    WIDTH_MM = 190.0
    HEIGHT_MM = 90.0

    fig = plt.figure(figsize=(WIDTH_MM / 25.4, HEIGHT_MM / 25.4), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, WIDTH_MM)
    ax.set_ylim(0, HEIGHT_MM)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    y_top = 82.0

    # -------------------------------------------------------------------------
    # Column 1: People at home (one 30-minute slot)
    # -------------------------------------------------------------------------
    c1_x = 3.0
    c1_w = 45.0

    ax.text(c1_x + 0.5 * c1_w, y_top, "People at home\n(one 30-minute slot)",
            fontsize=8.0, fontweight="bold", ha="center", va="top", color=COLOR_TEXT)

    p_data = [
        (c1_x + 4.0, 59.0, "Person 1: Cooking", "#475569"),
        (c1_x + 4.0, 45.0, "Person 2: Watching TV", "#475569"),
        (c1_x + 4.0, 23.0, "Person 3: Using a computer", "#475569"),
    ]

    for px, py, plabel, pcol in p_data:
        draw_person_silhouette(ax, px, py, scale=1.0, color=pcol)
        ax.text(px + 3.8, py, plabel, fontsize=6.8, ha="left", va="center", color=COLOR_TEXT)

    # -------------------------------------------------------------------------
    # Column 2: Shared devices (green) & Personal devices (blue)
    # -------------------------------------------------------------------------
    c2_x = 55.0
    c2_w = 43.0

    # Top box: Shared devices
    sb_y = 44.0
    sb_h = 28.0
    box_shared = FancyBboxPatch((c2_x, sb_y), c2_w, sb_h,
                                boxstyle="round,pad=0,rounding_size=2.0",
                                facecolor="#E3F3E8", edgecolor=COLOR_OUTLINE, lw=0.9)
    ax.add_patch(box_shared)

    ax.text(c2_x + 0.5 * c2_w, sb_y + sb_h - 4.5, "Shared devices", fontsize=8.0, fontweight="bold",
            ha="center", va="center", color=COLOR_TEXT)
    ax.text(c2_x + 0.5 * c2_w, sb_y + sb_h - 11.2, "Cooking, TV, washer,\ndryer, dishwasher",
            fontsize=6.8, ha="center", va="center", color=COLOR_TEXT)
    ax.text(c2_x + 0.5 * c2_w, sb_y + 4.6, "Used once per household;\ngrows less than the number\nof people at home",
            fontsize=5.6, ha="center", va="center", color=COLOR_MUTED)

    # Bottom box: Personal devices
    pb_y = 14.0
    pb_h = 23.0
    box_personal = FancyBboxPatch((c2_x, pb_y), c2_w, pb_h,
                                 boxstyle="round,pad=0,rounding_size=2.0",
                                 facecolor="#E4EEF8", edgecolor=COLOR_OUTLINE, lw=0.9)
    ax.add_patch(box_personal)

    ax.text(c2_x + 0.5 * c2_w, pb_y + pb_h - 4.5, "Personal devices", fontsize=8.0, fontweight="bold",
            ha="center", va="center", color=COLOR_TEXT)
    ax.text(c2_x + 0.5 * c2_w, pb_y + pb_h - 10.5, "Computer",
            fontsize=7.2, ha="center", va="center", color=COLOR_TEXT)
    ax.text(c2_x + 0.5 * c2_w, pb_y + 4.2, "Adds up per person",
            fontsize=5.8, ha="center", va="center", color=COLOR_MUTED)

    # Arrows from Column 1 to Column 2
    arr_p1 = FancyArrowPatch((35.0, 59.0), (c2_x - 1.0, 61.0),
                             arrowstyle="-|>", mutation_scale=7.5, color=COLOR_OUTLINE, lw=0.9)
    ax.add_patch(arr_p1)
    arr_p2 = FancyArrowPatch((37.0, 45.0), (c2_x - 1.0, 49.0),
                             arrowstyle="-|>", mutation_scale=7.5, color=COLOR_OUTLINE, lw=0.9)
    ax.add_patch(arr_p2)
    arr_p3 = FancyArrowPatch((42.0, 23.0), (c2_x - 1.0, 25.0),
                             arrowstyle="-|>", mutation_scale=7.5, color=COLOR_OUTLINE, lw=0.9)
    ax.add_patch(arr_p3)

    # -------------------------------------------------------------------------
    # Column 3: Household equipment power + Always-on base load
    # -------------------------------------------------------------------------
    c3_x = 106.0
    c3_w = 40.0

    # Base load box above: light grey
    bl_y = 66.0
    bl_h = 13.0
    box_bl = FancyBboxPatch((c3_x, bl_y), c3_w, bl_h,
                            boxstyle="round,pad=0,rounding_size=1.5",
                            facecolor="#F1F3F5", edgecolor=COLOR_OUTLINE, lw=0.9)
    ax.add_patch(box_bl)
    ax.text(c3_x + 0.5 * c3_w, bl_y + 0.5 * bl_h, "Always-on base load\n(fridge, standby)",
            fontsize=6.5, ha="center", va="center", color=COLOR_TEXT)

    # Household equipment power box: light orange
    hp_y = 19.0
    hp_h = 39.0
    box_hp = FancyBboxPatch((c3_x, hp_y), c3_w, hp_h,
                            boxstyle="round,pad=0,rounding_size=2.0",
                            facecolor="#FAEADB", edgecolor=COLOR_OUTLINE, lw=0.9)
    ax.add_patch(box_hp)

    ax.text(c3_x + 0.5 * c3_w, hp_y + hp_h - 5.5, "Household\nequipment power", fontsize=8.0, fontweight="bold",
            ha="center", va="center", color=COLOR_TEXT)
    ax.text(c3_x + 0.5 * c3_w, hp_y + 13.0, "Always-on base load\n+\nshared devices\n+\npersonal devices",
            fontsize=6.5, ha="center", va="center", color=COLOR_TEXT)

    # Arrow from Base load down to Household power
    arr_bl = FancyArrowPatch((c3_x + 0.5 * c3_w, bl_y - 0.5), (c3_x + 0.5 * c3_w, hp_y + hp_h + 0.5),
                             arrowstyle="-|>", mutation_scale=7.5, color=COLOR_OUTLINE, lw=0.9)
    ax.add_patch(arr_bl)

    # Arrows from Column 2 boxes into Column 3 box
    arr_s_hp = FancyArrowPatch((c2_x + c2_w + 0.5, 52.0), (c3_x - 0.5, 45.0),
                              arrowstyle="-|>", mutation_scale=7.5, color=COLOR_OUTLINE, lw=0.9)
    ax.add_patch(arr_s_hp)
    arr_p_hp = FancyArrowPatch((c2_x + c2_w + 0.5, 26.0), (c3_x - 0.5, 30.0),
                              arrowstyle="-|>", mutation_scale=7.5, color=COLOR_OUTLINE, lw=0.9)
    ax.add_patch(arr_p_hp)

    # -------------------------------------------------------------------------
    # Column 4: Scaled to a national total
    # -------------------------------------------------------------------------
    c4_x = 153.5
    c4_w = 32.5
    sc_y = 23.0
    sc_h = 35.0

    box_sc = FancyBboxPatch((c4_x, sc_y), c4_w, sc_h,
                            boxstyle="round,pad=0,rounding_size=2.0",
                            facecolor="#F1F3F5", edgecolor=COLOR_OUTLINE, lw=0.9)
    ax.add_patch(box_sc)

    ax.text(c4_x + 0.5 * c4_w, sc_y + sc_h - 5.5, "Scaled to a\nnational total", fontsize=8.0, fontweight="bold",
            ha="center", va="center", color=COLOR_TEXT)
    ax.text(c4_x + 0.5 * c4_w, sc_y + 11.5, "Annual total matched\nto the national\nhousehold energy\nsurvey, by\ndwelling type",
            fontsize=6.2, ha="center", va="center", color=COLOR_TEXT)

    # Note under Column 4
    ax.text(c4_x + 0.5 * c4_w, sc_y - 3.5, "Scaling factor = target /\nsimulated annual energy",
            fontsize=5.8, ha="center", va="top", color=COLOR_MUTED)

    # Arrow from Column 3 to Column 4
    arr_sc = FancyArrowPatch((c3_x + c3_w + 0.5, 38.5), (c4_x - 0.5, 38.5),
                             arrowstyle="-|>", mutation_scale=8.0, color=COLOR_OUTLINE, lw=1.0)
    ax.add_patch(arr_sc)

    return fig


# =============================================================================
# FIGURE M4: 2030 Scenarios Concept Chart
# =============================================================================
def build_figure_m4(dpi=600):
    """Figure M4: Construction of the three 2030 scenarios from the pre-pandemic trend and the 2022 jump.
    Dimensions: 190 mm wide x 90 mm tall, 600 DPI.
    """
    WIDTH_MM = 190.0
    HEIGHT_MM = 90.0

    fig = plt.figure(figsize=(WIDTH_MM / 25.4, HEIGHT_MM / 25.4), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, WIDTH_MM)
    ax.set_ylim(0, HEIGHT_MM)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # Margins and plot area
    x_axis_left = 32.0
    x_axis_right = 138.0
    y_axis_bottom = 20.0
    y_axis_top = 80.0

    # Draw axes
    ax.plot([x_axis_left, x_axis_right + 3.0], [y_axis_bottom, y_axis_bottom], color=COLOR_OUTLINE, lw=1.1)
    ax.plot([x_axis_left, x_axis_left], [y_axis_bottom, y_axis_top + 3.0], color=COLOR_OUTLINE, lw=1.1)

    # Axis labels
    ax.text((x_axis_left + x_axis_right) / 2.0, y_axis_bottom - 9.5, "Year",
            fontsize=8.5, ha="center", va="top", color=COLOR_TEXT)
    ax.text(x_axis_left - 10.0, (y_axis_bottom + y_axis_top) / 2.0, "Share of time at home",
            fontsize=8.5, ha="center", va="bottom", rotation=90, color=COLOR_TEXT)

    # Ticks along Year axis: 2005, 2010, 2015, 2022, 2030 (proportional)
    year_span = 25.0
    plot_w = x_axis_right - x_axis_left

    def year_to_x(y):
        return x_axis_left + ((y - 2005) / year_span) * plot_w

    years = [2005, 2010, 2015, 2022, 2030]
    for y in years:
        x_pos = year_to_x(y)
        ax.plot([x_pos, x_pos], [y_axis_bottom, y_axis_bottom - 2.0], color=COLOR_OUTLINE, lw=0.9)
        ax.text(x_pos, y_axis_bottom - 3.2, str(y), fontsize=7.2,
                ha="center", va="top", color=COLOR_TEXT)

    # Trend line math
    slope = 0.7
    y_trend = lambda yr: 30.0 + (yr - 2005) * slope

    x_05 = year_to_x(2005)
    x_10 = year_to_x(2010)
    x_15 = year_to_x(2015)
    x_22 = year_to_x(2022)
    x_30 = year_to_x(2030)

    y_05 = y_trend(2005)
    y_10 = y_trend(2010)
    y_15 = y_trend(2015)
    y_22_trend = y_trend(2022)
    y_30_trend = y_trend(2030)

    # 1. Three dark-grey dots at 2005, 2010, 2015
    ax.scatter([x_05, x_10, x_15], [y_05, y_10, y_15], color="#4A5568", s=32, zorder=5)

    # Solid line through 2005 to 2015
    ax.plot([x_05, x_15], [y_05, y_15], color="#4A5568", lw=1.8, zorder=4)

    # Label "Pre-pandemic trend" below the line
    ax.text(x_10 + 2.0, y_10 - 4.5, "Pre-pandemic trend", fontsize=7.0,
            ha="center", va="top", color="#4A5568")

    # 2. Dashed line from 2015 to 2030
    ax.plot([x_15, x_30], [y_15, y_30_trend], color="#4A5568", lw=1.8, linestyle=(0, (4, 3)), zorder=4)

    # 3. Black dot at 2022, clearly above dashed trend
    jump_height = 16.0
    y_22_dot = y_22_trend + jump_height

    ax.scatter([x_22], [y_22_dot], color="black", s=36, zorder=6)

    # Vertical bracket between dashed line and 2022 dot
    bracket_x = x_22 - 3.5
    b_y1 = y_22_trend
    b_y2 = y_22_dot
    b_ymid = (b_y1 + b_y2) / 2.0

    ax.plot([bracket_x + 1.2, bracket_x, bracket_x, bracket_x + 1.2],
            [b_y2, b_y2, b_y1, b_y1], color=COLOR_TEXT, lw=0.9)
    ax.plot([bracket_x - 1.0, bracket_x], [b_ymid, b_ymid], color=COLOR_TEXT, lw=0.9)

    ax.text(bracket_x - 2.5, b_ymid, "2022 jump", fontsize=7.2,
            ha="right", va="center", color=COLOR_TEXT)

    # 4. Three scenario lines start at 2022 dot and end at 2030
    # Blue: Keep all of the jump (parallel to dashed trend)
    y_30_blue = y_30_trend + jump_height
    color_blue = "#2B6CB0"
    ax.plot([x_22, x_30], [y_22_dot, y_30_blue], color=color_blue, lw=2.0, zorder=5)
    ax.text(x_30 + 2.5, y_30_blue, "Keep all of the jump", fontsize=7.2,
            ha="left", va="center", color=color_blue, fontweight="bold")

    # Green: Keep half of the jump
    y_30_green = y_30_trend + 0.5 * jump_height
    color_green = "#2F855A"
    ax.plot([x_22, x_30], [y_22_dot, y_30_green], color=color_green, lw=2.0, zorder=5)
    ax.text(x_30 + 2.5, y_30_green, "Keep half of the jump", fontsize=7.2,
            ha="left", va="center", color=color_green, fontweight="bold")

    # Orange: Back to the trend
    y_30_orange = y_30_trend
    color_orange = "#DD6B20"
    ax.plot([x_22, x_30], [y_22_dot, y_30_orange], color=color_orange, lw=2.0, zorder=5)
    ax.text(x_30 + 2.5, y_30_orange, "Back to the trend", fontsize=7.2,
            ha="left", va="center", color=color_orange, fontweight="bold")

    return fig


# =============================================================================
# MAIN EXECUTION
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Generate Method figures M1 to M4.")
    parser.add_argument("--dpi", type=int, default=600, help="Resolution in DPI (default: 600)")
    args = parser.parse_args()

    base_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\2J_docs_occ_nTemp\writing\submission"
    figures_dir = os.path.join(base_dir, "figures")
    prompts_dir = os.path.join(figures_dir, "Prompts_Images")
    rejection_dir = os.path.join(base_dir, "rejection revision")

    figures = [
        ("Figure_M1_diary_to_hourly", build_figure_m1),
        ("Figure_M2_raking", build_figure_m2),
        ("Figure_M3_activity_to_power", build_figure_m3),
        ("Figure_M4_2030_scenarios", build_figure_m4),
    ]

    print(f"Generating Method figures M1 to M4 at {args.dpi} DPI...")

    for name, builder in figures:
        print(f"\nBuilding {name}...")
        fig = builder(dpi=args.dpi)

        targets = [
            os.path.join(figures_dir, f"{name}.png"),
            os.path.join(figures_dir, f"{name}.pdf"),
            os.path.join(prompts_dir, f"{name}.png"),
            os.path.join(rejection_dir, f"{name}.png"),
        ]

        for target in targets:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            ext = os.path.splitext(target)[1].lower()
            if ext == ".png":
                fig.savefig(target, dpi=args.dpi, facecolor="white", edgecolor="none")
            elif ext == ".pdf":
                fig.savefig(target, facecolor="white", edgecolor="none")
            print(f"  [OK] Saved: {target}")

        plt.close(fig)

        # Verification
        primary = targets[0]
        img = Image.open(primary)
        w_mm = img.size[0] / args.dpi * 25.4
        h_mm = img.size[1] / args.dpi * 25.4
        print(f"  Dimensions: {img.size[0]} x {img.size[1]} px ({w_mm:.1f} mm x {h_mm:.1f} mm)")

    print("\nAll Method figures generated successfully!")


if __name__ == "__main__":
    main()

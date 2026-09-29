# -*- coding: utf-8 -*-
"""Generate Graphical Abstract for Energy and Buildings (2J manuscript).

Specification:
- submission/figures/Prompts_Images/Graphical_abstract_EB_prompt.md (2026-09-28)
- Exact dimensions: 2656 x 1062 pixels (landscape, aspect 1 : 2.5).
- Print size target: 5 x 13 cm (130 x 52 mm).
- Pure white background, thin grey divider rules, sans-serif font, colour-blind-safe palette.
- All text >= 8 pt when printed at 13 cm wide.
- Strictly verbatim text and numbers from the author's brief.

Outputs:
- figures/Prompts_Images/Graphical_abstract_EB.png
- figures/Prompts_Images/Graphical_abstract_EB.pdf
- figures/Prompts_Images/Graphical_abstract_EB.tiff
- figures/Graphical_abstract_EB.png
- figures/Graphical_abstract_EB.pdf
- rejection revision/manuscript/EB_upload/2J_graphical_abstract.pdf
- rejection revision/manuscript/EB_upload/2J_graphical_abstract.tiff
- rejection revision/manuscript/EB_upload/2J_graphical_abstract.png
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from PIL import Image

plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Helvetica", "sans-serif"]
plt.rcParams["font.family"] = "sans-serif"

# Exact canvas dimensions in pixels
CANVAS_W = 2656
CANVAS_H = 1062
DPI = 100  # 1 unit = 1 px when scaled by px_to_pt

# Palette
COLOR_BG = "#FFFFFF"
COLOR_NAVY = "#0F2942"
COLOR_NAVY_ACCENT = "#1E3A8A"
COLOR_NAVY_LIGHT = "#EFF6FF"
COLOR_TEAL = "#0D9488"
COLOR_TEAL_DARK = "#0F766E"
COLOR_GREY_BAR = "#94A3B8"
COLOR_DIVIDER = "#CBD5E1"
COLOR_TEXT_TITLE = "#0F2942"
COLOR_TEXT_PRIMARY = "#1E293B"
COLOR_CARD_BG = "#F8FAFC"
COLOR_CARD_BORDER = "#CBD5E1"
COLOR_TRACK_BG = "#F1F5F9"
COLOR_TRACK_BORDER = "#E2E8F0"
COLOR_GREEN_BG = "#F0FDF4"
COLOR_GREEN_BORDER = "#86EFAC"
COLOR_GREEN_TEXT = "#166534"


def px_to_pt(px):
    """Convert pixel height to matplotlib point size for DPI=100."""
    return px * 72.0 / 100.0


def build_graphical_abstract():
    fig = plt.figure(figsize=(CANVAS_W / DPI, CANVAS_H / DPI), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, CANVAS_W)
    ax.set_ylim(0, CANVAS_H)
    ax.axis("off")
    fig.patch.set_facecolor(COLOR_BG)

    # -------------------------------------------------------------------------
    # Divider rules between panels
    # Panel A: [0, 930], Panel B: [930, 1860], Panel C: [1860, 2656]
    # -------------------------------------------------------------------------
    ax.plot([930, 930], [50, 1012], color=COLOR_DIVIDER, lw=2.0)
    ax.plot([1860, 1860], [50, 1012], color=COLOR_DIVIDER, lw=2.0)

    # =========================================================================
    # PANEL A: Method (0 to 930 px, ~35% width)
    # =========================================================================
    # Heading
    ax.text(465, 965, "Method", fontsize=px_to_pt(38), fontweight="bold",
            ha="center", va="center", color=COLOR_TEXT_TITLE)

    # Three boxes joined by arrows, left to right
    box_w = 252
    box_h = 510
    box_y = 330
    box_xs = [36, 339, 642]

    boxes_info = [
        ("1", ["Time-use diaries,", "", "2005 to 2022"], 26),
        ("2", ["Household", "occupancy", "model"], 26),
        ("3", ["Building energy", "simulation:", "", "4 dwelling types,", "6 Canadian cities"], 23),
    ]

    # Center of text area inside boxes
    text_center_y = box_y + 225

    for i, (num, lines, fsize) in enumerate(boxes_info):
        bx = box_xs[i]
        # Box container
        card = FancyBboxPatch(
            (bx, box_y), box_w, box_h,
            boxstyle="round,pad=0,rounding_size=16",
            facecolor=COLOR_CARD_BG, edgecolor=COLOR_CARD_BORDER, lw=2.0
        )
        ax.add_patch(card)

        # Top accent bar
        hbar = FancyBboxPatch(
            (bx, box_y + box_h - 14), box_w, 14,
            boxstyle="round,pad=0,rounding_size=6",
            facecolor=COLOR_NAVY_ACCENT, edgecolor="none"
        )
        ax.add_patch(hbar)

        # Step indicator circle/badge
        badge_y = box_y + box_h - 60
        badge = FancyBboxPatch(
            (bx + box_w / 2 - 26, badge_y - 20), 52, 40,
            boxstyle="round,pad=0,rounding_size=12",
            facecolor="#E0E7FF", edgecolor="#A5B4FC", lw=1.5
        )
        ax.add_patch(badge)
        ax.text(bx + box_w / 2, badge_y, num, fontsize=px_to_pt(22), fontweight="bold",
                ha="center", va="center", color=COLOR_NAVY_ACCENT)

        # Text inside box
        text_content = "\n".join(lines)
        ax.text(bx + box_w / 2, text_center_y, text_content,
                fontsize=px_to_pt(fsize), fontweight="bold", ha="center", va="center",
                color=COLOR_TEXT_PRIMARY, linespacing=1.4)

    # Arrows between Box 1 -> Box 2 and Box 2 -> Box 3 (perfectly aligned with text center)
    arrow1 = FancyArrowPatch(
        (box_xs[0] + box_w + 6, text_center_y), (box_xs[1] - 6, text_center_y),
        arrowstyle="-|>", mutation_scale=24, lw=2.8, color=COLOR_NAVY_ACCENT
    )
    ax.add_patch(arrow1)

    arrow2 = FancyArrowPatch(
        (box_xs[1] + box_w + 6, text_center_y), (box_xs[2] - 6, text_center_y),
        arrowstyle="-|>", mutation_scale=24, lw=2.8, color=COLOR_NAVY_ACCENT
    )
    ax.add_patch(arrow2)

    # Footer Card
    foot_x = 36
    foot_y = 125
    foot_w = 858
    foot_h = 110
    foot_card = FancyBboxPatch(
        (foot_x, foot_y), foot_w, foot_h,
        boxstyle="round,pad=0,rounding_size=14",
        facecolor="#F1F5F9", edgecolor="#CBD5E1", lw=1.8
    )
    ax.add_patch(foot_card)

    foot_bar = FancyBboxPatch(
        (foot_x, foot_y), 12, foot_h,
        boxstyle="round,pad=0,rounding_size=4",
        facecolor=COLOR_NAVY_ACCENT, edgecolor="none"
    )
    ax.add_patch(foot_bar)

    ax.text(foot_x + foot_w / 2 + 6, foot_y + foot_h / 2,
            "2022 compared with 2030 work-from-home scenarios",
            fontsize=px_to_pt(25), fontweight="bold", ha="center", va="center",
            color=COLOR_TEXT_PRIMARY)

    # =========================================================================
    # PANEL B: 2022 to 2030, main scenario (930 to 1860 px, ~35% width)
    # =========================================================================
    ax.text(1395, 965, "2022 to 2030, main scenario", fontsize=px_to_pt(38),
            fontweight="bold", ha="center", va="center", color=COLOR_TEXT_TITLE)

    # Small line above:
    # "Weekday at-home rate in 2022: 4.73 points above its 2005-2015 trend"
    sub_x = 970
    sub_y = 852
    sub_w = 850
    sub_h = 70
    sub_card = FancyBboxPatch(
        (sub_x, sub_y), sub_w, sub_h,
        boxstyle="round,pad=0,rounding_size=12",
        facecolor=COLOR_NAVY_LIGHT, edgecolor="#BFDBFE", lw=1.5
    )
    ax.add_patch(sub_card)

    subhead_text = "Weekday at-home rate in 2022: 4.73 points above its 2005-2015 trend"
    ax.text(sub_x + sub_w / 2, sub_y + sub_h / 2, subhead_text,
            fontsize=px_to_pt(22), fontweight="bold", ha="center", va="center",
            color=COLOR_NAVY_ACCENT)

    # Three simple horizontal bars or number tiles, one row each:
    # 1. Annual electricity: +0.12 % (short, grey)
    # 2. Midday share: +0.73 percentage points (teal)
    # 3. Load factor: +0.49 percentage points (teal)
    card_w = 850
    card_h = 210
    card_x = 970
    card_ys = [610, 368, 125]

    metrics = [
        {
            "name": "Annual electricity: +0.12 %",
            "bar_color": COLOR_GREY_BAR,
            "bar_w": 90,  # Short grey bar
            "text_color": COLOR_TEXT_PRIMARY,
        },
        {
            "name": "Midday share: +0.73 percentage points",
            "bar_color": COLOR_TEAL,
            "bar_w": 655,  # Long teal bar
            "text_color": COLOR_TEAL_DARK,
        },
        {
            "name": "Load factor: +0.49 percentage points",
            "bar_color": COLOR_TEAL,
            "bar_w": 440,  # Medium-long teal bar ((0.49 / 0.73) * 655)
            "text_color": COLOR_TEAL_DARK,
        },
    ]

    track_w = 760
    track_h = 52

    for i, m in enumerate(metrics):
        cy = card_ys[i]
        tile = FancyBboxPatch(
            (card_x, cy), card_w, card_h,
            boxstyle="round,pad=0,rounding_size=16",
            facecolor=COLOR_CARD_BG, edgecolor=COLOR_CARD_BORDER, lw=1.8
        )
        ax.add_patch(tile)

        # Label text inside card
        ax.text(card_x + 45, cy + card_h - 55, m["name"],
                fontsize=px_to_pt(27), fontweight="bold", ha="left", va="center",
                color=m["text_color"])

        # Track background
        tx = card_x + 45
        ty = cy + 40
        track = FancyBboxPatch(
            (tx, ty), track_w, track_h,
            boxstyle="round,pad=0,rounding_size=10",
            facecolor=COLOR_TRACK_BG, edgecolor=COLOR_TRACK_BORDER, lw=1.2
        )
        ax.add_patch(track)

        # Value bar
        bar = FancyBboxPatch(
            (tx, ty), m["bar_w"], track_h,
            boxstyle="round,pad=0,rounding_size=10",
            facecolor=m["bar_color"], edgecolor="none"
        )
        ax.add_patch(bar)

    # =========================================================================
    # PANEL C: Take-away (1860 to 2656 px, ~30% width)
    # =========================================================================
    ax.text(2258, 965, "Take-away", fontsize=px_to_pt(38), fontweight="bold",
            ha="center", va="center", color=COLOR_TEXT_TITLE)

    c_card_x = 1900
    c_card_y = 125
    c_card_w = 715
    c_card_h = 798

    hero_card = FancyBboxPatch(
        (c_card_x, c_card_y), c_card_w, c_card_h,
        boxstyle="round,pad=0,rounding_size=20",
        facecolor=COLOR_CARD_BG, edgecolor=COLOR_CARD_BORDER, lw=2.2
    )
    ax.add_patch(hero_card)

    # Left teal accent bar
    c_accent = FancyBboxPatch(
        (c_card_x, c_card_y), 16, c_card_h,
        boxstyle="round,pad=0,rounding_size=6",
        facecolor=COLOR_TEAL, edgecolor="none"
    )
    ax.add_patch(c_accent)

    # Headline: Timing, not sizing (bold, impactful)
    ax.text(c_card_x + 55, c_card_y + c_card_h - 110,
            "Timing, not sizing",
            fontsize=px_to_pt(40), fontweight="bold", ha="left", va="center",
            color=COLOR_NAVY)

    # Separator rule
    ax.plot([c_card_x + 55, c_card_x + c_card_w - 55],
            [c_card_y + c_card_h - 170, c_card_y + c_card_h - 170],
            color=COLOR_DIVIDER, lw=1.8)

    # Core message:
    # "Average schedules erase the household spread in peak timing;
    #  the household model keeps it."
    msg_lines = (
        "Average schedules erase the\n"
        "household spread in peak timing;\n"
        "the household model keeps it."
    )
    ax.text(c_card_x + 55, c_card_y + c_card_h / 2 + 10,
            msg_lines,
            fontsize=px_to_pt(26), fontweight="bold", ha="left", va="center",
            color=COLOR_TEXT_PRIMARY, linespacing=1.6)

    # Bottom conclusion banner:
    # "Working from home changes WHEN homes use electricity much more than HOW MUCH they use."
    bot_w = c_card_w - 110
    bot_h = 185
    bot_x = c_card_x + 55
    bot_y = c_card_y + 45
    bot_card = FancyBboxPatch(
        (bot_x, bot_y), bot_w, bot_h,
        boxstyle="round,pad=0,rounding_size=14",
        facecolor=COLOR_GREEN_BG, edgecolor=COLOR_GREEN_BORDER, lw=1.6
    )
    ax.add_patch(bot_card)

    bot_text = (
        "Working from home changes WHEN\n"
        "homes use electricity much more than\n"
        "HOW MUCH they use."
    )
    ax.text(bot_x + bot_w / 2, bot_y + bot_h / 2,
            bot_text,
            fontsize=px_to_pt(23), fontweight="bold", ha="center", va="center",
            color=COLOR_GREEN_TEXT, linespacing=1.45)

    return fig


def main():
    base_dir = r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\2J_docs_occ_nTemp\writing\submission"
    figures_dir = os.path.join(base_dir, "figures")
    prompts_dir = os.path.join(figures_dir, "Prompts_Images")
    eb_upload_dir = os.path.join(base_dir, "rejection revision", "manuscript", "EB_upload")

    os.makedirs(prompts_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(eb_upload_dir, exist_ok=True)

    print("Generating Graphical Abstract for Energy and Buildings...")
    fig = build_graphical_abstract()

    targets = [
        # Prompts_Images directory
        os.path.join(prompts_dir, "Graphical_abstract_EB.png"),
        os.path.join(prompts_dir, "Graphical_abstract_EB.pdf"),
        os.path.join(prompts_dir, "Graphical_abstract_EB.tiff"),
        # figures directory
        os.path.join(figures_dir, "Graphical_abstract_EB.png"),
        os.path.join(figures_dir, "Graphical_abstract_EB.pdf"),
        # EB_upload directory per prompt instructions (lines 19-20)
        os.path.join(eb_upload_dir, "2J_graphical_abstract.pdf"),
        os.path.join(eb_upload_dir, "2J_graphical_abstract.tiff"),
        os.path.join(eb_upload_dir, "2J_graphical_abstract.png"),
    ]

    for target in targets:
        ext = os.path.splitext(target)[1].lower()
        if ext == ".png":
            fig.savefig(target, dpi=DPI, facecolor="white", edgecolor="none")
        elif ext == ".pdf":
            fig.savefig(target, facecolor="white", edgecolor="none")
        elif ext == ".tiff":
            fig.savefig(target, dpi=DPI, facecolor="white", edgecolor="none", format="tiff")
        print(f"  [OK] Saved: {target}")

    plt.close(fig)

    # Verification
    primary = targets[0]
    img = Image.open(primary)
    w_px, h_px = img.size
    print(f"\nVerification: Primary PNG is {w_px} x {h_px} pixels.")


if __name__ == "__main__":
    main()

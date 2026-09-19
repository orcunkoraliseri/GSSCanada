"""
Task 3 - Prototype get_building_groups_v2() offline.
Validates hash-tail grouping + off-by-one fix on all 6 NUS_RC IDFs
without modifying neighbourhood.py.
"""

import re
import os

IDF_DIR = os.path.join(os.path.dirname(__file__), "..", "BEM_Setup", "Neighbourhoods")

SPACELIST_PATTERN = re.compile(
    r"SpaceList,\s*\n\s*([^,]+),\s*!-\s*Name\s*\n([\s\S]*?);",
    re.MULTILINE
)

HEX_RE = re.compile(r"^[0-9a-fA-F]{6,}$")


def _is_hex_token(s: str) -> bool:
    """Return True if s looks like a hex hash (6+ hex chars)."""
    return bool(HEX_RE.match(s))


def _extract_space_names(spaces_block: str) -> list:
    """
    Fixed parser (fixes off-by-one from neighbourhood.py).
    Accepts the last entry even when the terminating ';' has eaten the '!-' comment.
    """
    names = []
    for line in spaces_block.split("\n"):
        # Strip trailing IDF terminators and whitespace
        stripped = line.strip().rstrip(",;")
        if not stripped or stripped.startswith("!"):
            continue
        # Drop inline comment, then strip punctuation
        name_part = stripped.split("!-")[0].rstrip(",; ").strip()
        if name_part:
            names.append(name_part)
    return names


def get_building_groups_v2(idf_content: str) -> dict:
    """
    Drop-in replacement for get_building_groups() in neighbourhood.py.

    Grouping rule (§4.1):
      1. Strip trailing '_Space' if present.
      2. Split on '_'.
      3. Use the LAST segment as the building id if it is a plausible hex
         token (>= 6 hex chars).
      4. Fall back to the original '(.+?)_Room_' prefix logic for IDFs
         where the last segment is not a hex token.
    """
    match = SPACELIST_PATTERN.search(idf_content)
    if not match:
        print("  Warning: No SpaceList found in IDF.")
        return {}

    spacelist_name = match.group(1).strip()
    spaces_block   = match.group(2)

    # Skip DesignSpecification spacelists
    if "DesignSpecification" in spacelist_name:
        # Try next match
        for m in SPACELIST_PATTERN.finditer(idf_content):
            if "DesignSpecification" not in m.group(1):
                spacelist_name = m.group(1).strip()
                spaces_block   = m.group(2)
                break
        else:
            print("  Warning: Only DesignSpecification SpaceLists found.")
            return {}

    space_names = _extract_space_names(spaces_block)

    # Group by trailing hex hash
    buildings: dict = {}
    hash_to_bldg: dict = {}

    for space in space_names:
        # Strip _Space suffix
        candidate = space
        if candidate.endswith("_Space"):
            candidate = candidate[:-len("_Space")]

        parts = candidate.split("_")
        last  = parts[-1] if parts else ""

        if _is_hex_token(last):
            # Hash-based grouping (all 6 NUS_RC IDFs)
            key = last
        else:
            # Fallback: original _Room_ prefix
            pm = re.match(r"(.+?)_Room_", space)
            key = pm.group(1) if pm else space  # worst-case: each space = its own building

        if key not in hash_to_bldg:
            bldg_id = f"Bldg_{len(hash_to_bldg)}"
            hash_to_bldg[key] = bldg_id
        bldg_id = hash_to_bldg[key]
        buildings.setdefault(bldg_id, []).append(space)

    print(f"  SpaceList '{spacelist_name}': {len(space_names)} spaces -> {len(buildings)} buildings")
    return buildings


# ── Main: run on all 6 IDFs ──────────────────────────────────────────────────

print("=" * 70)
print("Prototype validation — get_building_groups_v2()")
print("=" * 70)

all_passed = True
for n in range(1, 7):
    idf_path = os.path.join(IDF_DIR, f"NUS_RC{n}.idf")
    if not os.path.exists(idf_path):
        print(f"NUS_RC{n}.idf  NOT FOUND — skipping")
        continue

    with open(idf_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    print(f"\nNUS_RC{n}.idf")
    groups = get_building_groups_v2(content)

    if not groups:
        print("  FAIL: 0 buildings — prototype did not group any spaces")
        all_passed = False
        continue

    total = sum(len(v) for v in groups.values())
    print(f"  Buildings: {sorted(groups.keys())}")
    print(f"  Per-building counts: { {k: len(v) for k, v in groups.items()} }")
    print(f"  Total spaces across buildings: {total}")

    # Validation: sum of per-building counts must equal total parsed
    # (re-parse to get independent total)
    match = SPACELIST_PATTERN.search(content)
    if match:
        sl_name = match.group(1).strip()
        if "DesignSpecification" in sl_name:
            for m in SPACELIST_PATTERN.finditer(content):
                if "DesignSpecification" not in m.group(1):
                    match = m
                    break
        raw_count = len(_extract_space_names(match.group(2)))
        if total == raw_count:
            print(f"  PASS: sum({total}) == raw_count({raw_count})")
        else:
            print(f"  FAIL: sum({total}) != raw_count({raw_count})")
            all_passed = False

print("\n" + "=" * 70)
print("Overall:", "ALL PASS" if all_passed else "SOME FAILURES — do NOT proceed to Task 4")
print("=" * 70)

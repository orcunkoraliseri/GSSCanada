"""
Task 2 — Enumerate naming conventions across all 6 neighbourhood IDFs.
Reads each NUS_RC*.idf and prints the primary SpaceList name, member count,
and first 5 member names, using the same regex as neighbourhood.py.
"""

import re
import os

IDF_DIR = os.path.join(os.path.dirname(__file__), "..", "BEM_Setup", "Neighbourhoods")

SPACELIST_PATTERN = re.compile(
    r"SpaceList,\s*\n\s*([^,]+),\s*!-\s*Name\s*\n([\s\S]*?);",
    re.MULTILINE
)

# Existing parser (mirrors neighbourhood.py - shows the off-by-one bug)
def extract_space_names_original(spaces_block):
    names = []
    for line in spaces_block.split("\n"):
        line = line.strip()
        if line and "!-" in line:
            name_part = line.split(",")[0].strip()
            if name_part:
                names.append(name_part)
    return names

# Fixed parser (§4.2 - handles trailing semicolon entry without !- comment)
def extract_space_names_fixed(spaces_block):
    names = []
    for line in spaces_block.split("\n"):
        stripped = line.strip().rstrip(",;")
        if not stripped or stripped.startswith("!"):
            continue
        name_part = stripped.split("!-")[0].rstrip(",; ").strip()
        if name_part:
            names.append(name_part)
    return names

print("=" * 70)
print(f"{'IDF':<12} {'SpaceList':<35} {'Orig':>5} {'Fixed':>5}")
print("=" * 70)

for n in range(1, 7):
    idf_path = os.path.join(IDF_DIR, f"NUS_RC{n}.idf")
    if not os.path.exists(idf_path):
        print(f"NUS_RC{n}.idf  NOT FOUND")
        continue

    with open(idf_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Find all SpaceList matches; skip DesignSpecification ones
    matches = list(SPACELIST_PATTERN.finditer(content))
    primary = None
    for m in matches:
        name = m.group(1).strip()
        if "DesignSpecification" not in name:
            primary = m
            break

    if not primary:
        print(f"NUS_RC{n}.idf  — no primary SpaceList found")
        continue

    sl_name = primary.group(1).strip()
    block   = primary.group(2)

    orig_names  = extract_space_names_original(block)
    fixed_names = extract_space_names_fixed(block)

    print(f"NUS_RC{n}.idf  {sl_name:<35} {len(orig_names):>5} {len(fixed_names):>5}")
    print(f"  First 5 members (fixed parser):")
    for nm in fixed_names[:5]:
        print(f"    {nm}")
    print()

print("=" * 70)
print("Convention key:")
print("  _Room_   → old format (what neighbourhood.py expects)")
print("  _living_unit1_ → new format (what NUS_RC1.idf actually has)")
print("=" * 70)

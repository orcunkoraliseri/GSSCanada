"""
Patch the NECB-G-Thermostat Setpoint-Cooling Schedule:Compact object in the two 3J-fix
apartment IDF copies to variant 1a (seasonal winter relief): 28.0 C (Through 4/30),
24.0 C (Through 9/30, unchanged cooling season), 28.0 C (Through 12/31).
SummerDesignDay/WinterDesignDay day-types are held at 24.0 in all three blocks so
HVAC autosizing is unaffected. Text-level replacement, not eppy, per
step8_coolfix_implementation_plan.md Phase 1 / step8_coolfix_employee_prompt.md Phase 1.
"""
import difflib
import re
from pathlib import Path

TARGET_DIR = Path(__file__).resolve().parent.parent / "Buildings_MTL_v242_3Jfix"
APARTMENT_FILES = [
    "ASHRAE901_ApartmentHighRise_STD2022_Buffalo_NECB17_Z6_v242.idf",
    "ASHRAE901_ApartmentMidRise_STD2022_Buffalo_NECB17_Z6_v242.idf",
]
SCHEDULE_NAME = "NECB-G-Thermostat Setpoint-Cooling"
DESIGN_DAY_TYPES = {"SummerDesignDay", "WinterDesignDay"}
BLOCK_SPECS = [("4/30", "28.0"), ("9/30", "24.0"), ("12/31", "28.0")]

OBJECT_RE = re.compile(
    r"(  Schedule:Compact,\s*\n\s*" + re.escape(SCHEDULE_NAME) + r",\s*!-[^\n]*\n"
    r"\s*Temperature,\s*!-[^\n]*\n)(.*?;)",
    re.DOTALL,
)
DAYTYPE_SPLIT_RE = re.compile(r"For:\s*([A-Za-z]+),")
UNTIL_RE = re.compile(r"(Until:\s*\d{2}:\d{2}),([\d.]+)")


def parse_daytype_blocks(body_no_semicolon):
    parts = DAYTYPE_SPLIT_RE.split(body_no_semicolon)
    day_blocks = []
    for i in range(1, len(parts), 2):
        daytype = parts[i]
        untils = UNTIL_RE.findall(parts[i + 1])
        day_blocks.append((daytype, untils))
    return day_blocks


def build_entries(day_blocks):
    entries = []
    for through_label, value in BLOCK_SPECS:
        entries.append(f"Through: {through_label}")
        for daytype, untils in day_blocks:
            entries.append(f"For: {daytype}")
            v = "24.0" if daytype in DESIGN_DAY_TYPES else value
            for until_str, _orig_val in untils:
                entries.append(f"{until_str},{v}")
    return entries


def patch_file(path: Path) -> str:
    original = path.read_text()
    m = OBJECT_RE.search(original)
    if not m:
        raise RuntimeError(f"{path.name}: schedule object '{SCHEDULE_NAME}' not found")

    header = m.group(1)
    body = m.group(2)[:-1]  # strip trailing ';'

    day_blocks = parse_daytype_blocks(body)
    if not day_blocks:
        raise RuntimeError(f"{path.name}: no For: day-type blocks parsed")

    entries = build_entries(day_blocks)
    new_body = "    " + ",\n    ".join(entries) + ";\n"
    new_object = header + new_body

    patched = original[: m.start()] + new_object + original[m.end():]

    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        patched.splitlines(keepends=True),
        fromfile=f"{path.name} (orig)",
        tofile=f"{path.name} (patched)",
    )
    diff_text = "".join(diff)

    path.write_text(patched)
    return diff_text


def main():
    for fname in APARTMENT_FILES:
        path = TARGET_DIR / fname
        diff_text = patch_file(path)
        print(f"=== {fname} ===")
        print(diff_text)
        print()


if __name__ == "__main__":
    main()

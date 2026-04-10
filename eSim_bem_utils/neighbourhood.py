"""
Neighbourhood IDF Preparation Module.

This module handles the structural manipulation of neighbourhood IDFs to support
per-building occupancy profiles. It "explodes" shared master objects (People, Lights,
Equipment) into individual per-building objects with unique schedule names.
"""

import os
import re
from typing import Optional


_SPACELIST_PATTERN = re.compile(
    r"SpaceList,\s*\n\s*([^,]+),\s*!-\s*Name\s*\n([\s\S]*?);",
    re.MULTILINE
)
_HEX_RE = re.compile(r"^[0-9a-fA-F]{6,}$")


def _find_primary_spacelist(idf_content: str):
    """Return (name, spaces_block) for the first non-DesignSpecification SpaceList."""
    for m in _SPACELIST_PATTERN.finditer(idf_content):
        if "DesignSpecification" not in m.group(1):
            return m.group(1).strip(), m.group(2)
    return None, None


def _parse_space_names(spaces_block: str) -> list[str]:
    """
    Extract space names from a SpaceList body.

    Fixes the original off-by-one: the last entry ends with ';' instead of
    a '!-' comment, so we no longer require '!-' to be present on each line.
    """
    names: list[str] = []
    for line in spaces_block.split("\n"):
        stripped = line.strip().rstrip(",;")
        if not stripped or stripped.startswith("!"):
            continue
        name_part = stripped.split("!-")[0].rstrip(",; ").strip()
        if name_part:
            names.append(name_part)
    return names


def _infer_dtype_from_zone_name(zone_name: str) -> str | None:
    """
    Return the DTYPE implied by a single zone name, or None for ambiguous/non-residential zones.

    Checks in priority order so that 'highrise' beats 'apartment'.
    Returns None for Corridor/Office/etc. — caller handles via majority vote.
    """
    lower = zone_name.lower()
    if 'highrise' in lower:
        return 'HighRise'
    if 'midrise' in lower:
        return 'MidRise'
    if 'apartment' in lower:
        # Ambiguous (e.g. NUS_RC5 "0_Apartment_...") — default to MidRise
        return 'MidRise'
    if 'living_unit' in lower:
        return 'SingleD'
    if 'room_' in lower:
        return 'SingleD'
    return None


def infer_building_dtype(zones: list[str]) -> str:
    """
    Infer the DTYPE for a building group from its zone/space names.

    Applies _infer_dtype_from_zone_name to every zone and takes a majority
    vote over non-None results.  Non-residential zones (Corridor, Office)
    return None from the helper and are ignored, so they inherit the type
    from their residential siblings.

    Args:
        zones: Space names belonging to one building group.

    Returns:
        One of the 8 DTYPE strings.  Falls back to 'SingleD' (the largest
        pool) when no zone yields a positive signal.
    """
    from collections import Counter

    votes = [_infer_dtype_from_zone_name(z) for z in zones]
    valid = [v for v in votes if v is not None]

    if not valid:
        return 'SingleD'

    return Counter(valid).most_common(1)[0][0]


def get_building_groups(idf_content: str) -> dict[str, dict]:
    """
    Analyzes a neighbourhood IDF and groups spaces by building.

    Groups by the trailing hex hash in each space name (e.g. the 'a8a609ec'
    in '132.8660_living_unit1_2_a8a609ec_Space').  Falls back to the legacy
    '_Room_' prefix logic for any space whose last token is not a hex hash,
    so IDFs that pre-date this fix continue to work.

    Args:
        idf_content: The full text content of the IDF file.

    Returns:
        A dictionary mapping building IDs (e.g., "Bldg_0") to dicts of the form
        {'spaces': [...], 'dtype': 'MidRise'}.
    """
    from collections import Counter

    spacelist_name, spaces_block = _find_primary_spacelist(idf_content)
    if spaces_block is None:
        print("Warning: No SpaceList found in IDF.")
        return {}

    space_names = _parse_space_names(spaces_block)

    space_lists: dict[str, list[str]] = {}
    hash_to_bldg: dict[str, str] = {}

    for space in space_names:
        # Strip trailing _Space, then split to reach the last token
        candidate = space[:-len("_Space")] if space.endswith("_Space") else space
        parts = candidate.split("_")
        last  = parts[-1] if parts else ""

        if _HEX_RE.match(last):
            # Primary rule: group by trailing hex hash
            key = last
        else:
            # Fallback: legacy _Room_ prefix grouping
            pm = re.match(r"(.+?)_Room_", space)
            key = pm.group(1) if pm else space

        if key not in hash_to_bldg:
            hash_to_bldg[key] = f"Bldg_{len(hash_to_bldg)}"
        space_lists.setdefault(hash_to_bldg[key], []).append(space)

    # Attach inferred DTYPE to each building group
    buildings: dict[str, dict] = {}
    for bldg_id, spaces in space_lists.items():
        buildings[bldg_id] = {
            'spaces': spaces,
            'dtype': infer_building_dtype(spaces),
        }

    # Summary
    dtype_counts = Counter(b['dtype'] for b in buildings.values())
    dtype_summary = ', '.join(f"{count} {dtype}" for dtype, count in dtype_counts.most_common())
    print(f"Found SpaceList '{spacelist_name}' with {len(space_names)} spaces.")
    print(f"Grouped into {len(buildings)} buildings: {dtype_summary}.")
    return buildings


def get_water_equipment_building_map(
    idf_content: str,
    buildings: dict[str, dict]
) -> dict[str, list[str]]:
    """
    Maps existing WaterUse:Equipment objects to buildings by matching
    the trailing hex hash in their names against the building groups.

    The trailing hex hash in a WaterUse:Equipment name (e.g. 'a8a609ec' in
    'Apartment Water Equipment..132.8660_living_unit1_2_a8a609ec') is the same
    hash used to group the corresponding spaces in get_building_groups(), so
    it is the correct join key.  Falls back to the legacy '..<prefix>_Room_'
    extraction for names that do not end in a hex token.

    Args:
        idf_content: The full text content of the IDF file.
        buildings: Building groups from get_building_groups().

    Returns:
        Dict mapping building IDs to lists of WaterUse:Equipment names.
    """
    # Extract all WaterUse:Equipment names from the IDF text
    water_name_pattern = re.compile(
        r"WaterUse:Equipment,\s*\n\s*([^,\n]+),\s*!-\s*Name",
        re.MULTILINE
    )
    water_names = [m.group(1).strip() for m in water_name_pattern.finditer(idf_content)]

    if not water_names:
        return {}

    # Build hash-to-building lookup from the buildings dict (mirrors get_building_groups)
    hash_to_bldg: dict[str, str] = {}
    for bldg_id, bldg_data in buildings.items():
        for space in bldg_data['spaces']:
            candidate = space[:-len("_Space")] if space.endswith("_Space") else space
            parts = candidate.split("_")
            last  = parts[-1] if parts else ""
            if _HEX_RE.match(last) and last not in hash_to_bldg:
                hash_to_bldg[last] = bldg_id

    # Legacy fallback: prefix-to-building via _Room_ (unchanged from original)
    prefix_to_bldg: dict[str, str] = {}
    for bldg_id, bldg_data in buildings.items():
        for space in bldg_data['spaces']:
            pm = re.match(r"(.+?)_Room_", space)
            if pm:
                prefix = pm.group(1)
                if prefix not in prefix_to_bldg:
                    prefix_to_bldg[prefix] = bldg_id

    # Map each WaterUse:Equipment to its building
    water_map: dict[str, list[str]] = {}
    for wname in water_names:
        bldg_id = None

        # Primary: extract trailing hex hash from the equipment name
        parts = wname.split("_")
        last  = parts[-1] if parts else ""
        if _HEX_RE.match(last):
            bldg_id = hash_to_bldg.get(last)

        # Fallback: legacy '..<prefix>_Room_' extraction
        if bldg_id is None:
            equip_prefix_match = re.search(r"\.\.(.*?)_Room_", wname)
            if equip_prefix_match:
                bldg_id = prefix_to_bldg.get(equip_prefix_match.group(1))

        if bldg_id:
            water_map.setdefault(bldg_id, []).append(wname)
        else:
            print(f"  Warning: Could not map WaterUse:Equipment '{wname}' to any building.")

    return water_map


def prepare_neighbourhood_idf(
    idf_path: str,
    output_path: str,
    num_buildings: Optional[int] = None
) -> int:
    """
    Prepares a neighbourhood IDF by exploding shared objects into per-building objects.

    This function:
    1. Reads the original IDF.
    2. Identifies building groups from the SpaceList.
    3. Removes the original shared People, Lights, and ElectricEquipment objects.
    4. Creates new per-building objects with unique schedule names.
    5. Writes the modified IDF to output_path.

    Args:
        idf_path: Path to the original neighbourhood IDF.
        output_path: Path to write the modified IDF.
        num_buildings: Optional override for number of buildings to create.

    Returns:
        The number of buildings detected/created.
    """
    with open(idf_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Get building groups
    buildings = get_building_groups(content)
    n_buildings = num_buildings if num_buildings else len(buildings)

    if n_buildings == 0:
        print("Error: No buildings detected in IDF.")
        return 0

    print(f"\nPreparing IDF for {n_buildings} buildings...")

    # Remove original objects (we'll add per-building ones)
    # Using re.sub to remove ALL instances of People, Lights, ElectricEquipment
    modified_content = re.sub(r"People,\s*\n([\s\S]*?);", "", content, flags=re.MULTILINE)
    modified_content = re.sub(r"Lights,\s*\n([\s\S]*?);", "", modified_content, flags=re.MULTILINE)
    modified_content = re.sub(r"ElectricEquipment,\s*\n([\s\S]*?);", "", modified_content, flags=re.MULTILINE)
    
    # Keep original WaterUse:Equipment objects intact (preserves Plant Loop connections).
    # Their Flow_Rate_Fraction_Schedule_Name will be updated in-place below to
    # point to per-building Water_Bldg_X schedules.

    # Generate new per-building objects
    new_objects: list[str] = []

    # Inject missing ScheduleTypeLimits if needed
    if not any(obj.startswith("ScheduleTypeLimits,\n  Fraction,") for obj in content.split("\n\n")):
        new_objects.append("""
ScheduleTypeLimits,
  Fraction,                !- Name
  0.0,                     !- Lower Limit Value
  1.0,                     !- Upper Limit Value
  Continuous,              !- Numeric Type
  Dimensionless;           !- Unit Type
""")

    if not any(obj.startswith("ScheduleTypeLimits,\n  Any Number,") for obj in content.split("\n\n")):
        new_objects.append("""
ScheduleTypeLimits,
  Any Number,              !- Name
  ,                        !- Lower Limit Value
  ,                        !- Upper Limit Value
  Continuous,              !- Numeric Type
  Dimensionless;           !- Unit Type
""")

    for i, (bldg_id, bldg_data) in enumerate(buildings.items()):
        if i >= n_buildings:
            break

        spaces = bldg_data['spaces']

        # Create a SpaceList for this building
        space_list_name = f"Neighbourhood_{bldg_id}_SpaceList"
        # Build space entries - comma after value, semicolon on last
        space_lines = []
        for j, s in enumerate(spaces):
            if j < len(spaces) - 1:
                space_lines.append(f"  {s},  !- Space Name {j+1}")
            else:
                space_lines.append(f"  {s};  !- Space Name {j+1}")
        space_entries = "\n".join(space_lines)
        spacelist_obj = f"""
SpaceList,
  {space_list_name},  !- Name
{space_entries}
"""
        new_objects.append(spacelist_obj)

        # Create People object for this building
        people_obj = f"""
People,
  Neighbourhood_{bldg_id}_People,  !- Name
  {space_list_name},  !- Zone or ZoneList or Space or SpaceList Name
  Occ_{bldg_id},  !- Number of People Schedule Name
  People/Area,  !- Number of People Calculation Method
  ,  !- Number of People
  0.0271717171717191,  !- People per Floor Area {{person/m2}}
  ,  !- Floor Area per Person {{m2/person}}
  0.3,  !- Fraction Radiant
  ,  !- Sensible Heat Fraction
  Activity_{bldg_id};  !- Activity Level Schedule Name
"""
        new_objects.append(people_obj)

        # Create Lights object for this building
        lights_obj = f"""
Lights,
  Neighbourhood_{bldg_id}_Lights,  !- Name
  {space_list_name},  !- Zone or ZoneList or Space or SpaceList Name
  Light_{bldg_id},  !- Schedule Name
  Watts/Area,  !- Design Level Calculation Method
  ,  !- Lighting Level {{W}}
  4,  !- Watts per Floor Area {{W/m2}}
  ,  !- Watts per Person {{W/person}}
  0,  !- Return Air Fraction
  0.2,  !- Fraction Radiant
  0.6,  !- Fraction Visible
  1,  !- Fraction Replaceable
  General;  !- End-Use Subcategory
"""
        new_objects.append(lights_obj)

        # Create ElectricEquipment object for this building
        equip_obj = f"""
ElectricEquipment,
  Neighbourhood_{bldg_id}_Equipment,  !- Name
  {space_list_name},  !- Zone or ZoneList or Space or SpaceList Name
  Equip_{bldg_id},  !- Schedule Name
  Watts/Area,  !- Design Level Calculation Method
  ,  !- Design Level {{W}}
  9.05723905723969,  !- Watts per Floor Area {{W/m2}}
  ,  !- Watts per Person {{W/person}}
  0,  !- Fraction Latent
  0.3,  !- Fraction Radiant
  0,  !- Fraction Lost
  Electric Equipment;  !- End-Use Subcategory
"""
        new_objects.append(equip_obj)

        # Create placeholder schedules
        for sched_type in ["Occ", "Activity", "Light", "Equip", "Water"]:
            type_limit = "Any Number" if sched_type == "Activity" else "Fraction"
            sched_name = f"{sched_type}_{bldg_id}"
            sched_obj = f"""
Schedule:Compact,
  {sched_name},  !- Name
  {type_limit},  !- Schedule Type Limits Name
  Through: 12/31,  !- Field 1
  For: AllDays,  !- Field 2
  Until: 24:00,  !- Field 3
  {"120" if sched_type == "Activity" else "1.0"};  !- Field 4
"""
            new_objects.append(sched_obj)

    # Update existing WaterUse:Equipment objects in-place to use per-building schedules.
    # This preserves their WaterUse:Connections and PlantLoop links so that DHW
    # heating energy is properly calculated through the SHW plant loop.
    water_map = get_water_equipment_building_map(content, buildings)
    water_update_count = 0

    for bldg_id, water_names in water_map.items():
        bldg_idx = int(bldg_id.split("_")[1])
        if bldg_idx >= n_buildings:
            continue

        water_sch_name = f"Water_{bldg_id}"

        for wname in water_names:
            # Replace the Flow Rate Fraction Schedule Name (4th field) for this
            # specific WaterUse:Equipment object, identified by its exact name.
            # Field order: Name, End-Use Subcategory, Peak Flow Rate,
            #              Flow Rate Fraction Schedule Name, ...
            escaped_name = re.escape(wname)
            pattern = (
                r"(WaterUse:Equipment,\s*\n"
                r"\s*" + escaped_name + r"\s*,\s*!-[^\n]*\n"   # Name
                r"\s*[^,\n]+\s*,\s*!-[^\n]*\n"                 # End-Use Subcategory
                r"\s*[^,\n]+\s*,\s*!-[^\n]*\n)"                # Peak Flow Rate
                r"\s*[^,\n]+(\s*,\s*!-)"                        # Flow Rate Fraction Schedule (replace value, keep comment marker)
            )

            def _replacement(m):
                return m.group(1) + "  " + water_sch_name + m.group(2)

            modified_content, count = re.subn(pattern, _replacement, modified_content, flags=re.MULTILINE)
            if count > 0:
                water_update_count += count

    if water_update_count > 0:
        print(f"  Updated {water_update_count} WaterUse:Equipment objects with per-building schedules.")
    elif water_map:
        print("  Warning: Could not update any WaterUse:Equipment schedule names.")

    # Append new objects to the IDF
    modified_content += "\n! ========== NEIGHBOURHOOD PER-BUILDING OBJECTS ==========\n"
    modified_content += "\n".join(new_objects)

    # Write the modified IDF
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(modified_content)

    print(f"Prepared IDF saved to: {output_path}")
    print(f"Created {n_buildings} sets of People/Lights/Equipment objects.")
    print(f"Existing WaterUse:Equipment objects preserved (Plant Loop connections intact).")

    return n_buildings


def get_num_buildings_from_idf(idf_path: str) -> int:
    """
    Quick utility to count the number of buildings in a neighbourhood IDF.

    Args:
        idf_path: Path to the neighbourhood IDF.

    Returns:
        Number of buildings detected.
    """
    with open(idf_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    buildings = get_building_groups(content)
    return len(buildings)

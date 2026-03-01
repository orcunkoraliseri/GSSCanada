"""
Neighbourhood IDF Preparation Module.

This module handles the structural manipulation of neighbourhood IDFs to support
per-building occupancy profiles. It "explodes" shared master objects (People, Lights,
Equipment) into individual per-building objects with unique schedule names.
"""

import os
import re
from typing import Optional


def get_building_groups(idf_content: str) -> dict[str, list[str]]:
    """
    Analyzes a neighbourhood IDF and groups spaces by building.

    This function parses the SpaceList object to extract space names and groups
    them by their coordinate-based prefix (e.g., "83.928..." identifies Building X).

    Args:
        idf_content: The full text content of the IDF file.

    Returns:
        A dictionary mapping building IDs (e.g., "Bldg_0") to lists of space names.
    """
    # Find the SpaceList block
    spacelist_pattern = re.compile(
        r"SpaceList,\s*\n\s*([^,]+),\s*!-\s*Name\s*\n([\s\S]*?);",
        re.MULTILINE
    )
    match = spacelist_pattern.search(idf_content)
    if not match:
        print("Warning: No SpaceList found in IDF.")
        return {}

    spacelist_name = match.group(1).strip()
    spaces_block = match.group(2)

    # Extract individual space names from the block
    space_names: list[str] = []
    for line in spaces_block.split("\n"):
        line = line.strip()
        if line and "!-" in line:
            # Extract name before the comma
            name_part = line.split(",")[0].strip()
            if name_part:
                space_names.append(name_part)

    # Group spaces by their coordinate prefix (first part before _Room_)
    buildings: dict[str, list[str]] = {}
    building_prefixes: list[str] = []

    for space in space_names:
        # Extract prefix (everything before _Room_)
        prefix_match = re.match(r"(.+?)_Room_", space)
        if prefix_match:
            prefix = prefix_match.group(1)
            if prefix not in building_prefixes:
                building_prefixes.append(prefix)
            bldg_id = f"Bldg_{building_prefixes.index(prefix)}"
            if bldg_id not in buildings:
                buildings[bldg_id] = []
            buildings[bldg_id].append(space)

    print(f"Found SpaceList '{spacelist_name}' with {len(space_names)} spaces.")
    print(f"Grouped into {len(buildings)} buildings.")
    return buildings


def get_water_equipment_building_map(
    idf_content: str,
    buildings: dict[str, list[str]]
) -> dict[str, list[str]]:
    """
    Maps existing WaterUse:Equipment objects to buildings by matching
    the coordinate prefix in their names against the building groups.

    Naming convention:
        WaterUse:Equipment name: "Apartment Water Equipment..<prefix>_Room_<N>_<hash>"
        Space name:              "<prefix>_Room_<N>_<hash>_Space"
    The prefix before _Room_ identifies which building the object belongs to.

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

    # Build prefix-to-building lookup from the buildings dict
    prefix_to_bldg: dict[str, str] = {}
    for bldg_id, spaces in buildings.items():
        for space in spaces:
            prefix_match = re.match(r"(.+?)_Room_", space)
            if prefix_match:
                prefix = prefix_match.group(1)
                if prefix not in prefix_to_bldg:
                    prefix_to_bldg[prefix] = bldg_id

    # Map each WaterUse:Equipment to its building via coordinate prefix
    water_map: dict[str, list[str]] = {}
    for wname in water_names:
        # Extract prefix between ".." and "_Room_"
        equip_prefix_match = re.search(r"\.\.(.*?)_Room_", wname)
        if equip_prefix_match:
            equip_prefix = equip_prefix_match.group(1)
            bldg_id = prefix_to_bldg.get(equip_prefix)
            if bldg_id:
                water_map.setdefault(bldg_id, []).append(wname)
            else:
                print(f"  Warning: WaterUse prefix '{equip_prefix}' not matched to any building.")
        else:
            print(f"  Warning: Could not extract prefix from WaterUse name '{wname}'.")

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

    for i, (bldg_id, spaces) in enumerate(buildings.items()):
        if i >= n_buildings:
            break

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

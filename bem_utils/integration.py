import csv
import glob
import json
import os
from collections import defaultdict
from typing import Optional
from eppy.modeleditor import IDF
from bem_utils import idf_optimizer
from bem_utils import schedule_generator
from bem_utils import schedule_visualizer

import random


# Target "Standard Working Day" Profile (Matches DEFAULT_PRESENCE in debugVis)
# Used to select representative households for comparative simulations.
TARGET_WORKING_PROFILE = [
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.8, 0.5,  # 0-7: Home (Sleep/Wake)
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,  # 8-15: Away (Work)
    0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 0.8, 0.5   # 16-23: Home (Evening)
]


def find_best_match_household(
    schedules: dict, 
    candidates: list[str] = None, 
    day_type: str = 'Weekday'
) -> str:
    """
    Finds the household that best matches the TARGET_WORKING_PROFILE.
    
    Args:
        schedules: Dict of all loaded schedules.
        candidates: Optional list of HH_IDs to search. If None, searches all.
        day_type: Day type to compare ('Weekday' or 'Weekend').
        
    Returns:
        The HH_ID of the best matching household.
    """
    if not candidates:
        candidates = list(schedules.keys())
        # If too many, sample a subset for performance? 
        # Actually with <20k households, iterating all is fast enough for Python.
    
    best_hh_id = None
    best_score = float('inf')
    
    # Pre-compute target length
    target_len = len(TARGET_WORKING_PROFILE)
    
    for hh_id in candidates:
        hh_data = schedules[hh_id]
        entries = hh_data.get(day_type, [])
        if not entries:
            continue
            
        # Extract presence profile
        # Assume sorted by hour or sort it
        profile = [0.0] * 24
        for e in entries:
            if 0 <= e['hour'] < 24:
                profile[e['hour']] = float(e['occ'])
                
        # Calculate SSE Score
        score = sum((profile[i] - TARGET_WORKING_PROFILE[i])**2 for i in range(24))
        
        if score < best_score:
            best_score = score
            best_hh_id = hh_id
            
    return best_hh_id if best_hh_id else (candidates[0] if candidates else None)


def export_schedule_csv(
    schedule_data: dict,
    hh_id: str,
    scenario: str,
    output_dir: str,
    batch_name: str = None
) -> str:
    """
    Exports occupancy schedule data to a CSV file for debugging.
    
    Args:
        schedule_data: The household schedule dict with 'Weekday'/'Weekend' keys.
        hh_id: Household ID.
        scenario: Year/scenario name (e.g., '2025', '2015', 'Default').
        output_dir: Base output directory (e.g., SimResults).
        batch_name: Optional batch name for subfolder structure.
    
    Returns:
        str: Path to the exported CSV file.
    """
    # Create schedule export directory
    base_dir = os.path.dirname(output_dir) if output_dir else '.'
    if batch_name:
        schedule_dir = os.path.join(base_dir, 'SimResults_Schedules', batch_name, scenario)
    else:
        schedule_dir = os.path.join(base_dir, 'SimResults_Schedules', scenario)
    
    os.makedirs(schedule_dir, exist_ok=True)
    
    # Build export data
    export_data = []
    for dtype in ['Weekday', 'Weekend']:
        if dtype in schedule_data:
            for hour, val in enumerate(schedule_data[dtype]):
                export_data.append({
                    'HH_ID': hh_id,
                    'Scenario': scenario,
                    'DayType': dtype,
                    'Hour': hour,
                    'Occupancy': val
                })
    
    if not export_data:
        return None
    
    csv_path = os.path.join(schedule_dir, f'schedule_HH{hh_id}.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['HH_ID', 'Scenario', 'DayType', 'Hour', 'Occupancy'])
        writer.writeheader()
        writer.writerows(export_data)
    
    return csv_path


def load_schedules(csv_path: str, dwelling_type: str = None, region: str = None) -> dict:
    """
    Reads the BEM schedule CSV and organizes data by Household ID.
    
    Args:
        csv_path: Path to the schedule CSV file.
        dwelling_type: Optional filter for dwelling type (DTYPE column).
                       Options: 'SingleD', 'Attached', 'DuplexD', 'SemiD', 
                                'MidRise', 'HighRise', 'Movable', 'OtherA'
                       If None, loads all households.
        region: Optional filter for region (PR column).
                Example: "Quebec", "Ontario", "BC"
                If None, ignores region.
        
    Returns:
        dict: A dictionary structure:
              {
                  hh_id: {
                      'metadata': {'hhsize': int, 'dtype': str, ...},
                      'Weekday': [{'hour': h, 'occ': val, 'met': val}, ...],
                      'Weekend': [{'hour': h, 'occ': val, 'met': val}, ...]
                  }
              }
    """
    schedules = defaultdict(lambda: {'metadata': {}, 'Weekday': [], 'Weekend': []})
    skipped_count = 0
    
    print(f"Loading schedules from {os.path.basename(csv_path)}...")
    if dwelling_type:
        print(f"  Filtering for dwelling type: {dwelling_type}")
    if region:
        print(f"  Filtering for region: {region}")
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Filter by dwelling type if specified
            row_dtype = row.get('DTYPE', '')
            if dwelling_type and row_dtype != dwelling_type:
                skipped_count += 1
                continue
            
            # Filter by region if specified
            # Note: 2005 data might not have PR column if not re-generated, check existence
            if region:
                row_region = row.get('PR', '')
                if row_region and row_region != region:
                    skipped_count += 1
                    continue
                
            hh_id = row['SIM_HH_ID']
            day_type = row['Day_Type']  # Expected 'Weekday' or 'Weekend'
            
            # Parse values
            try:
                hour = int(row['Hour'])
                occ = float(row['Occupancy_Schedule'])
                met = float(row['Metabolic_Rate'])
            except ValueError:
                continue  # Skip invalid rows
            
            # Store metadata on first encounter
            if not schedules[hh_id]['metadata']:
                schedules[hh_id]['metadata'] = {
                    'hhsize': int(row.get('HHSIZE', 0)),
                    'dtype': row.get('DTYPE', ''),
                    'bedrm': int(row.get('BEDRM', 0)),
                    'condo': int(row.get('CONDO', 0)),
                }
            
            entry = {
                'hour': hour,
                'occ': occ,
                'met': met
            }
            schedules[hh_id][day_type].append(entry)
            
    # Sort by hour to ensure correct order
    for hh in schedules:
        for dtype in ['Weekday', 'Weekend']:
            if schedules[hh][dtype]:
                schedules[hh][dtype].sort(key=lambda x: x['hour'])
    
    if (dwelling_type or region) and skipped_count > 0:
        print(f"  Skipped {skipped_count} rows (didn't match filter)")
            
    print(f"Loaded schedules for {len(schedules)} households.")
    return dict(schedules)


def create_compact_schedule(name, type_limit, day_schedules):
    """
    Creates a Schedule:Compact object values list.
    
    Args:
        name (str): Name of the schedule.
        type_limit (str): Name of the schedule type limit (e.g., 'Fraction').
        day_schedules (dict): {'Weekday': [values...], 'Weekend': [values...]}
                              Values sorted 0-23 hours.
    
    Returns:
        list: Fields for the Schedule:Compact object.
    """
    fields = [
        name,           # Name
        type_limit,     # Schedule Type Limits Name
        "Through: 12/31" # Field 1
    ]
    
    # Process Weekdays then Weekends
    order = ['Weekday', 'Weekend']
    
    # Map to E+ day types
    ep_day_types = {
        'Weekday': 'For: Weekdays SummerDesignDay WinterDesignDay',
        'Weekend': 'For: Weekends Holidays AllOtherDays'
    }
    
    for day_type in order:
        if day_type in day_schedules and day_schedules[day_type]:
            fields.append(ep_day_types[day_type])
            
            # Add hourly values
            for entry in day_schedules[day_type]:
                hour = entry['hour'] + 1 # E+ uses 1-24 or "Until: HH:MM"
                val = entry['value']
                fields.append(f"Until: {hour:02d}:00")
                fields.append(f"{val:.3f}")
                
    return fields


    idf.saveas(output_path)


def get_floor_area(idf: IDF) -> float:
    """
    Calculates total conditioned floor area from Zone objects.
    Assumes all zones are conditioned (simplified approach).
    """
    area = 0.0
    
    # Try getting from Zone objects first (geometry based)
    # Note: Eppy doesn't auto-calculate area from vertices without valid output...
    # But often Zone objects have a user-entered value or auto-calc field if populated.
    # Actually, relying on Zone.Area requires E+ run.
    # We can approximate by looking for "ZoneList" or "Zone" and assuming specific names.
    # Better approach for now: Use base IDF's 'GlobalGeometryRules' to assume geometry is valid
    # But calculating area efficiently in Eppy is hard.
    
    # ALTERNATIVE: Use People object's zone reference?
    # Simple workaround: Most residential models have specific zone names.
    # Let's try to sum up 'Zone' object areas if provided, or assume a default if not found.
    # Often idf.idfobjects['GLOBALGEOMETRYRULES'] etc.
    
    # In many residential IDFs, there's a specific summary.
    return 0.0  # Placeholder, will refine logic inside inject_schedules


def parse_schedule_day_hourly(idf: IDF, day_sch_name: str) -> list:
    """
    Parses a Schedule:Day:Hourly or Schedule:Day:Interval object and returns a list of 24 hourly values.
    """
    # Try Schedule:Day:Hourly first
    day_obj = idf.getobject('SCHEDULE:DAY:HOURLY', day_sch_name)
    if day_obj:
        # Schedule:Day:Hourly has 24 value fields (Hour_1 through Hour_24)
        values = []
        for i in range(1, 25):
            field_name = f'Hour_{i}'
            try:
                val = getattr(day_obj, field_name, 0.0)
                values.append(float(val) if val else 0.0)
            except:
                values.append(0.0)
        return values
    
    # Try Schedule:Day:Interval
    day_obj = idf.getobject('SCHEDULE:DAY:INTERVAL', day_sch_name)
    if day_obj:
        # Schedule:Day:Interval uses time intervals
        # Format: Name, Type, Interpolate, Time1, Value1, Time2, Value2, ...
        values = [0.0] * 24
        fields = day_obj.obj[4:]  # Skip name, type, interpolate
        
        last_hour = 0
        i = 0
        while i < len(fields) - 1:
            time_str = str(fields[i]).strip() if fields[i] else ""
            val_str = str(fields[i+1]).strip() if fields[i+1] else "0"
            
            try:
                # Parse time like "04:00" or "24:00"
                if ':' in time_str:
                    hour_part = time_str.split(':')[0]
                    end_hour = int(hour_part)
                else:
                    end_hour = int(time_str)
                
                value = float(val_str)
                
                # Fill hours from last_hour to end_hour with this value
                for h in range(last_hour, min(end_hour, 24)):
                    values[h] = value
                last_hour = end_hour
            except (ValueError, TypeError):
                pass
            
            i += 2
        
        return values
    
    return None


def parse_schedule_week(idf: IDF, week_sch_name: str) -> dict:
    """
    Parses a Schedule:Week:Compact or Schedule:Week:Daily and returns
    dict with 'Weekday' and 'Weekend' lists of 24 values.
    """
    # Try Schedule:Week:Compact first
    week_obj = idf.getobject('SCHEDULE:WEEK:COMPACT', week_sch_name)
    if week_obj:
        # Parse Schedule:Week:Compact format
        # Fields alternate between day-type spec and schedule:day name
        weekday_sch = None
        weekend_sch = None
        fields = week_obj.obj[2:]  # Skip type and name
        
        i = 0
        while i < len(fields) - 1:
            day_spec = str(fields[i]).lower() if fields[i] else ""
            day_sch_name_ref = str(fields[i+1]) if fields[i+1] else ""
            
            # Match weekday patterns
            if 'weekday' in day_spec or 'monday' in day_spec:
                weekday_sch = day_sch_name_ref
            # Match weekend patterns (including AllOtherDays which often means weekend)
            if 'weekend' in day_spec or 'saturday' in day_spec or 'allotherdays' in day_spec:
                weekend_sch = day_sch_name_ref
            # AllDays applies to both
            if 'alldays' in day_spec and day_spec != 'allotherdays':
                weekday_sch = day_sch_name_ref
                weekend_sch = day_sch_name_ref
            i += 2
        
        weekday_vals = parse_schedule_day_hourly(idf, weekday_sch) if weekday_sch else None
        weekend_vals = parse_schedule_day_hourly(idf, weekend_sch) if weekend_sch else weekday_vals
        
        if weekday_vals:
            return {'Weekday': weekday_vals, 'Weekend': weekend_vals or weekday_vals}
    
    # Try Schedule:Week:Daily
    week_obj = idf.getobject('SCHEDULE:WEEK:DAILY', week_sch_name)
    if week_obj:
        # Has separate fields for each day type
        try:
            # Get Monday (index 2) for weekday, Saturday (index 7) for weekend
            weekday_sch = getattr(week_obj, 'Monday_ScheduleDay_Name', None)
            weekend_sch = getattr(week_obj, 'Saturday_ScheduleDay_Name', None)
            
            weekday_vals = parse_schedule_day_hourly(idf, weekday_sch) if weekday_sch else None
            weekend_vals = parse_schedule_day_hourly(idf, weekend_sch) if weekend_sch else weekday_vals
            
            if weekday_vals:
                return {'Weekday': weekday_vals, 'Weekend': weekend_vals or weekday_vals}
        except:
            pass
    
    return None


def parse_schedule_year(idf: IDF, schedule_name: str) -> dict:
    """
    Parses a Schedule:Year object and extracts weekday/weekend values.
    Returns dict: {'Weekday': [24 values], 'Weekend': [24 values]} or None.
    """
    year_obj = idf.getobject('SCHEDULE:YEAR', schedule_name)
    if not year_obj:
        return None
    
    # Get the first Schedule:Week reference (typically covers the whole year)
    week_sch_name = getattr(year_obj, 'ScheduleWeek_Name_1', None)
    if not week_sch_name:
        return None
    
    return parse_schedule_week(idf, week_sch_name)


def parse_schedule_values(idf: IDF, schedule_name: str):
    """
    Attempts to parse schedule values from various schedule types.
    Tries: Schedule:Year, Schedule:Week, Schedule:Day:Hourly, Schedule:Compact
    Returns dict: {'Weekday': [24 values], 'Weekend': [24 values]} or None.
    """
    # Try Schedule:Year first (most complex hierarchy)
    result = parse_schedule_year(idf, schedule_name)
    if result:
        return result
    
    # Try Schedule:Week directly
    result = parse_schedule_week(idf, schedule_name)
    if result:
        return result
    
    # Try Schedule:Day:Hourly directly  
    day_vals = parse_schedule_day_hourly(idf, schedule_name)
    if day_vals:
        return {'Weekday': day_vals, 'Weekend': day_vals}
    
    # Try Schedule:Compact
    sch_obj = idf.getobject('SCHEDULE:COMPACT', schedule_name)
    if sch_obj:
        # Parse standard Schedule:Compact format
        # Fields: type, name, day_types...
        # Example: Through: 12/31, For: AllDays, Until: 24:00, 0.5
        
        fields = sch_obj.obj[1:]  # Skip 'Schedule:Compact'
        
        # We need to extract values for Weekday and Weekend
        weekday_vals = [0.0] * 24
        weekend_vals = [0.0] * 24
        
        current_day_types = []
        i = 0
        while i < len(fields):
            f = str(fields[i]).lower()
            
            if 'through:' in f:
                # Reset or start new block. Usually residential is simple 1-block.
                i += 1
                continue
                
            if 'for:' in f:
                # Determine target days
                current_day_types = []
                if 'weekday' in f or 'alldays' in f or 'monday' in f:
                    current_day_types.append('Weekday')
                if 'weekend' in f or 'alldays' in f or 'saturday' in f or 'allotherdays' in f:
                    current_day_types.append('Weekend')
                i += 1
                
                # Parse Until/Value pairs until next 'For:' or 'Through:' or end
                temp_vals = [0.0] * 24
                last_hour = 0
                
                while i < len(fields):
                    sub_f = str(fields[i]).lower()
                    if 'for:' in sub_f or 'through:' in sub_f:
                        break
                        
                    if 'until:' in sub_f:
                        # Parse "Until: HH:MM"
                        # Handle potential comma-separated field issue from Eppy
                        # Eppy might split "Until: 12:00, 0.5" into "Until: 12:00" and "0.5"
                        # Or it might be "Until: 12:00" then next field is val
                        
                        time_part = sub_f.split('until:')[1].strip()
                        if ',' in time_part: # "12:00, 0.5"
                            parts = time_part.split(',')
                            h_str = parts[0].split(':')[0]
                            val = float(parts[1])
                            i += 1 # consumed
                        else:
                            h_str = time_part.split(':')[0]
                            # Next field is value
                            if i + 1 < len(fields):
                                try:
                                    val = float(fields[i+1])
                                    i += 2 # consumed until and val
                                except:
                                    i += 1
                                    continue
                            else:
                                i += 1
                                continue
                                
                        end_hour = int(h_str)
                        # Fill hours
                        for h in range(last_hour, min(end_hour, 24)):
                            temp_vals[h] = val
                        last_hour = end_hour
                    else:
                        i += 1
                
                # Apply processed values to targets
                for dt in current_day_types:
                    if dt == 'Weekday':
                        weekday_vals = list(temp_vals)
                    elif dt == 'Weekend':
                        weekend_vals = list(temp_vals)
            else:
                i += 1
                
        return {'Weekday': weekday_vals, 'Weekend': weekend_vals}
    
    # Schedule not found
    return None


def _get_single_building_fallback_profiles(verbose: bool = False) -> tuple:
    """
    Attempts to parse Lights, Equipment, and Water schedules from a representative
    Single Building IDF to use as defaults instead of conservative hardcoded profiles.
    
    Returns:
        (light_values, equip_values, water_values) or (None, None, None)
    """
    try:
        # Locate Single Building IDF in BEM_Setup/Buildings
        # Assume integration.py is in bem_utils/, so go up one level then to BEM_Setup/Buildings
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        buildings_dir = os.path.join(base_dir, 'BEM_Setup', 'Buildings')
        idfs = glob.glob(os.path.join(buildings_dir, '*.idf'))
        
        if not idfs:
            return None, None, None
            
        # Use first available single building IDF
        fallback_idf_path = idfs[0]
        if verbose:
            print(f"  Using Reference Defaults from: {os.path.basename(fallback_idf_path)}")
            
        # We need an IDF object. Note: IDD file must be set externally or we assume Energy+.idd
        # If IDF() fails due to missing IDD, we catch exception
        if not IDF.getiddname():
             IDF.setiddname(os.environ.get('IDD_FILE') or "Energy+.idd")
             
        orig_idf = IDF(fallback_idf_path)
        
        l_vals = None
        e_vals = None
        w_vals = None
        
        # LIGHTS
        objs = orig_idf.idfobjects.get('LIGHTS', [])
        if objs:
            name = getattr(objs[0], 'Schedule_Name', None)
            if name: l_vals = parse_schedule_values(orig_idf, name)
            
        # ELECTRICEQUIPMENT
        objs = orig_idf.idfobjects.get('ELECTRICEQUIPMENT', [])
        if objs:
            name = getattr(objs[0], 'Schedule_Name', None)
            if name: e_vals = parse_schedule_values(orig_idf, name)
            
        # WATERUSE:EQUIPMENT
        objs = orig_idf.idfobjects.get('WATERUSE:EQUIPMENT', [])
        if objs:
            name = getattr(objs[0], 'Flow_Rate_Fraction_Schedule_Name', None)
            if name: w_vals = parse_schedule_values(orig_idf, name)
            
        return l_vals, e_vals, w_vals
        
    except Exception as e:
        if verbose:
            print(f"  Warning: Could not load single building fallback defaults: {e}")
        return None, None, None



def inject_presence_projected_schedules(idf: IDF, hh_id: str, occ_data: dict, threshold: float = 0.3):
    """
    Creates new schedules for Lights, Equipment, and Hot Water that follows
    the base schedule shape BUT is zeroed out when occupancy <= threshold.
    """
    # 1. Identify target load objects
    targets = [
        ('LIGHTS', 'Schedule_Name'),
        ('ELECTRICEQUIPMENT', 'Schedule_Name'),
        ('GASEQUIPMENT', 'Schedule_Name'),
        ('WATERUSE:EQUIPMENT', 'Flow_Rate_Fraction_Schedule_Name')
    ]
    
    # We will simply create ONE projected schedule per existing schedule name found
    # to avoid duplicating logic.
    
    # ... logic implementation ...
    return


def inject_schedules(
    idf_path: str,
    output_path: str,
    hh_id: str,
    schedule_data: dict,
    epw_path: Optional[str] = None,
    sim_results_dir: str = None,
    batch_name: str = None
) -> None:
    """
    Injects specific household schedules into an IDF file.

    Uses DOE MidRise Apartment schedules as the standardized baseline,
    then applies occupancy-based modifications for year scenarios:
    - Lighting: Daylight Threshold Method (Gatekeeper logic).
    - Equipment/DHW: Presence Filter Method (Min/Max toggling).

    Args:
        idf_path: Path to the base IDF.
        output_path: Path to save the modified IDF.
        hh_id: Household ID.
        schedule_data: Data for this household from load_schedules.
        epw_path: Path to the EPW weather file (used to find .stat for lighting).
    """
    IDF.setiddname(os.environ.get('IDD_FILE') or "Energy+.idd")
    idf = IDF(idf_path)
    
    # 0. Load standard residential schedules (DOE MidRise Apartment baseline)
    standard_schedules = idf_optimizer.load_standard_residential_schedules(verbose=False)
    
    # 1. Prepare Occupancy Data from TUS/Census
    day_types = ['Weekday', 'Weekend']
    occ_data = {}
    met_data = {}
    
    for dtype in day_types:
        if dtype in schedule_data:
            # Ensure 24h integrity
            # Create list of 24 values
            hours_map = {x['hour']: x['occ'] for x in schedule_data[dtype]}
            occ_data[dtype] = [hours_map.get(h, 0.0) for h in range(24)]
            
            met_map = {x['hour']: x['met'] for x in schedule_data[dtype]}
            met_data[dtype] = [met_map.get(h, 120.0) for h in range(24)]
    
    # 2. Update People Object (Occupant Density)
    metadata = schedule_data.get('metadata', {})
    hhsize = metadata.get('hhsize', 2)
    
    people_objs = idf.idfobjects['PEOPLE']
    for people in people_objs:
        people.Number_of_People = hhsize
        try:
            people.Zone_Floor_Area_per_Person = ""
        except Exception:
            pass
        try:
            people.People_per_Zone_Floor_Area = ""
        except Exception:
            pass
        try:
            people.Number_of_People_Calculation_Method = "People"
        except Exception:
            pass
    
    # 3. Create Occupancy and Metabolic Schedules from TUS data
    occ_sch_name = f"Occ_Sch_HH_{hh_id}"
    met_sch_name = f"Met_Sch_HH_{hh_id}"
    
    def fmt_for_compact(data_list):
        return [{'hour': i, 'value': v} for i, v in enumerate(data_list)]

    occ_dict = {k: fmt_for_compact(v) for k, v in occ_data.items()}
    met_dict = {k: fmt_for_compact(v) for k, v in met_data.items()}

    occ_obj = idf.newidfobject("Schedule:Compact")
    occ_obj.obj = ["Schedule:Compact"] + create_compact_schedule(occ_sch_name, "Fraction", occ_dict)
    
    met_obj = idf.newidfobject("Schedule:Compact")
    met_obj.obj = ["Schedule:Compact"] + create_compact_schedule(met_sch_name, "Any Number", met_dict)
    
    for people in people_objs:
        people.Number_of_People_Schedule_Name = occ_sch_name
        people.Activity_Level_Schedule_Name = met_sch_name

    # 4. Apply presence-based schedule transformations
    # Using the new schedule_generator module for Lighting, Equipment, and DHW.

    # [FIX] Apply Water Use Peak Scaling for Year Scenarios
    idf_optimizer.scale_water_use_peak_flow(idf, standard_schedules, verbose=True)

    # Initialize generators
    lighting_gen = schedule_generator.LightingGenerator(epw_path=epw_path)

    load_targets = [
        ('LIGHTS', 'Schedule_Name', 'lighting'),
        ('ELECTRICEQUIPMENT', 'Schedule_Name', 'equipment'),
        ('GASEQUIPMENT', 'Schedule_Name', 'equipment'),
        ('WATERUSE:EQUIPMENT', 'Flow_Rate_Fraction_Schedule_Name', 'dhw'),
    ]

    created_schedules = {}
    
    collected_schedules = {
        'lighting': None, 
        'equipment': None, 
        'dhw': None,
        'presence': None
    }
    
    collected_defaults = {
        'lighting': None,
        'equipment': None,
        'dhw': None
    }
    # Check if we have presence data for Weekday (primary visual)
    if 'Weekday' in occ_data:
        collected_schedules['presence'] = occ_data['Weekday']
    
    # Initialize Visualizer
    visualizer = None
    if epw_path and sim_results_dir:
         visualizer = schedule_visualizer.ScheduleVisualizer(epw_path)

    for obj_type, field_name, std_key in load_targets:
        objs = idf.idfobjects.get(obj_type, [])

        # Get standard schedule values for PresenceFilter
        std_weekday = standard_schedules.get(std_key, {}).get('Weekday', [0.5] * 24)
        std_weekend = standard_schedules.get(std_key, {}).get('Weekend', std_weekday)

        for idx, obj in enumerate(objs):
            try:
                if not hasattr(obj, field_name):
                    continue

                cache_key = f"{obj_type}_{std_key}_{hh_id}"
                if cache_key in created_schedules:
                    setattr(obj, field_name, created_schedules[cache_key])
                    continue

                proj_data = {}
                for dtype in ['Weekday', 'Weekend']:
                    if dtype not in occ_data:
                        continue

                    presence = occ_data[dtype]
                    default_vals = std_weekday if dtype == 'Weekday' else std_weekend

                    if obj_type == 'LIGHTS':
                        # Daylight Threshold Method (with default schedule for gradual changes)
                        proj_data[dtype] = lighting_gen.generate(
                            presence, default_schedule=default_vals, day_type=dtype
                        )
                    else:
                        # Presence Filter Method (Equipment & DHW)
                        pf = schedule_generator.PresenceFilter(default_vals, presence)
                        proj_data[dtype] = pf.apply(presence)

                if not proj_data:
                    continue
                
                # --- Visualization Integration ---
                if 'Weekday' in proj_data:
                    # Save the first instance of each type for visualization
                    if collected_schedules[std_key] is None:
                        collected_schedules[std_key] = proj_data['Weekday']
                    if collected_defaults[std_key] is None:
                        collected_defaults[std_key] = std_weekday

                # Create new Schedule:Compact object
                proj_sch_name = f"Proj_{obj_type[:4]}_{idx}_{hh_id}"
                proj_dict = {k: fmt_for_compact(v) for k, v in proj_data.items()}

                proj_obj = idf.newidfobject("Schedule:Compact")
                proj_obj.obj = ["Schedule:Compact"] + create_compact_schedule(
                    proj_sch_name, "Fraction", proj_dict
                )

                setattr(obj, field_name, proj_sch_name)
                created_schedules[cache_key] = proj_sch_name

            except Exception as e:
                print(f"  Warning: Could not project {obj_type} schedule: {e}")

    # Generate Visualization if enabled and all data present
    if visualizer and sim_results_dir and collected_schedules['presence']:
        # Construct path
        plot_base = os.path.join(os.path.dirname(os.path.dirname(sim_results_dir)), "SimResults_Plotting_Schedules") 
        # Attempt to find project root relative to SimResults or just use BEM_Setup parent?
        # main.py sets SIM_RESULTS_DIR = BEM_Setup/SimResults.
        # So dirname(sim_results_dir) -> BEM_Setup.
        # dirname(BEM_Setup) -> Root.
        # User asked for "BEM_Setup/SimResults_Plotting_Schedules" ? 
        # "put them ... under the folder of 'SimResults_Plotting_Schedules' in that way we can compare"
        # I'll put it in BEM_Setup/SimResults_Plotting_Schedules
        
        # If sim_results_dir is absolute path to Batch folder.
        # batch_name is passed.
        
        # Assumption: sim_results_dir passed from main.py is "BEM_Setup/SimResults" 
        # NO, main.py passes `scenario_dir` as `output_dir` but `inject_schedules` signature ?
        # main.py calls `inject_schedules(..., sim_results_dir=SIM_RESULTS_DIR, batch_name=batch_name)`?
        # I need to update main.py call first!
        # But assuming valid path:
        
        # Construct BEM_Setup/SimResults_Plotting_Schedules
        # If sim_results_dir ends with "SimResults", go up one.
        if os.path.basename(sim_results_dir) == 'SimResults':
            bem_setup = os.path.dirname(sim_results_dir)
        else:
            # Fallback
            bem_setup = os.path.dirname(sim_results_dir)

        plot_dir_base = os.path.join(bem_setup, "SimResults_Plotting_Schedules")
        
        if batch_name:
             plot_dir = os.path.join(plot_dir_base, batch_name)
        else:
             plot_dir = plot_dir_base
             
        plot_filename = f"{batch_name if batch_name else 'Debug'}_HH{hh_id}.png"
        plot_path = os.path.join(plot_dir, plot_filename)
        
        # Default missing schedules to 0
        p_light = collected_schedules['lighting'] or [0.0]*24
        p_equip = collected_schedules['equipment'] or [0.0]*24
        p_dhw = collected_schedules['dhw'] or [0.0]*24
        
        visualizer.visualize_schedule_integration(
             presence_schedule=collected_schedules['presence'],
             proj_light=p_light,
             proj_equip=p_equip,
             proj_water=p_dhw,
             output_path=plot_path,
             title=f"Integrated Schedules - HH {hh_id} (Weekday)",
             default_light=collected_defaults['lighting'],
             default_equip=collected_defaults['equipment'],
             default_water=collected_defaults['dhw']
        )


    # 5. Optimize & Save
    idf_optimizer.optimize_idf(idf, verbose=True)
    idf.saveas(output_path)


def inject_neighbourhood_schedules(
    idf_path: str,
    output_path: str,
    schedules_list: list[dict],
    original_idf_path: Optional[str] = None,
    epw_path: Optional[str] = None,
    sim_results_dir: str = None,
    batch_name: str = None,
    verbose: bool = True
) -> None:
    """
    Injects multiple household schedules into a prepared neighbourhood IDF.

    This function expects the IDF to have been prepared by neighbourhood.prepare_neighbourhood_idf(),
    which creates per-building objects with schedule names like Occ_Bldg_0, Light_Bldg_0, etc.

    Uses the schedule_generator module for:
    - Lighting: Daylight Threshold Method (Gatekeeper logic).
    - Equipment/DHW: Presence Filter Method (Min/Max toggling).

    Args:
        idf_path: Path to the prepared neighbourhood IDF.
        output_path: Path to save the modified IDF.
        schedules_list: List of schedule_data dicts, one per building.
        original_idf_path: Path to the ORIGINAL IDF (before preparation) to parse default schedules.
        epw_path: Path to the EPW weather file (used to find .stat for lighting).
        verbose: Whether to print progress messages.
    """
    if not schedules_list:
        print("Error: No schedules provided for neighbourhood injection.")
        return

    # Initialize IDF
    IDF.setiddname(os.environ.get('IDD_FILE') or "Energy+.idd")
    idf = IDF(idf_path)

    # Parse default schedule values from original IDF (if provided)
    # If no original schedules found, use typical residential profiles
    # These profiles mimic standard EnergyPlus residential defaults:
    # - Lighting: Low during day, peaks in evening (6pm-11pm)
    # - Equipment: Moderate all day, slightly higher in morning/evening
    
    # Typical residential lighting profile (fraction of max)
    # Hours: 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23
    default_light_weekday = [
        0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.4, 0.5, 0.3, 0.2,
        0.2, 0.2, 0.2, 0.2, 0.2, 0.3, 0.5, 0.7, 0.9, 0.9,
        0.8, 0.6, 0.4, 0.2
    ]
    default_light_weekend = [
        0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.3, 0.4, 0.4,
        0.3, 0.3, 0.3, 0.3, 0.3, 0.4, 0.5, 0.7, 0.9, 0.9,
        0.8, 0.6, 0.4, 0.2
    ]
    
    # Typical residential equipment profile (fraction of max)
    default_equip_weekday = [
        0.3, 0.2, 0.2, 0.2, 0.2, 0.3, 0.5, 0.6, 0.5, 0.4,
        0.4, 0.4, 0.5, 0.4, 0.4, 0.4, 0.5, 0.6, 0.7, 0.7,
        0.6, 0.5, 0.4, 0.3
    ]
    default_equip_weekend = [
        0.3, 0.2, 0.2, 0.2, 0.2, 0.2, 0.3, 0.4, 0.5, 0.6,
        0.6, 0.6, 0.6, 0.5, 0.5, 0.5, 0.6, 0.7, 0.7, 0.7,
        0.6, 0.5, 0.4, 0.3
    ]
    
    default_light_values = {'Weekday': default_light_weekday, 'Weekend': default_light_weekend}
    default_equip_values = {'Weekday': default_equip_weekday, 'Weekend': default_equip_weekend}
    
    # Typical residential water profile (extracted from debug_compare_schedules.py)
    default_water_weekday = [
        0.05, 0.05, 0.05, 0.05, 0.1, 0.3, 0.5, 0.4, 0.2, 0.1,
        0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.4, 0.5, 0.4,
        0.3, 0.2, 0.1, 0.05
    ]
    default_water_weekend = default_water_weekday # Assume similar for fallback
    default_water_values = {'Weekday': default_water_weekday, 'Weekend': default_water_weekend}
    
    if original_idf_path:
        try:
            orig_idf = IDF(original_idf_path)
            
            # Find LIGHTS schedule name from original IDF
            light_objs = orig_idf.idfobjects.get('LIGHTS', [])
            if light_objs:
                light_sch_name = getattr(light_objs[0], 'Schedule_Name', None)
                if light_sch_name:
                    parsed = parse_schedule_values(orig_idf, light_sch_name)
                    if parsed:
                        default_light_values = parsed
                        if verbose:
                            print(f"  Parsed original LIGHTS schedule: {light_sch_name}")
            
            # Find ELECTRICEQUIPMENT schedule name from original IDF
            equip_objs = orig_idf.idfobjects.get('ELECTRICEQUIPMENT', [])
            if equip_objs:
                equip_sch_name = getattr(equip_objs[0], 'Schedule_Name', None)
                if equip_sch_name:
                    parsed = parse_schedule_values(orig_idf, equip_sch_name)
                    if parsed:
                        default_equip_values = parsed
                        if verbose:
                            print(f"  Parsed original EQUIPMENT schedule: {equip_sch_name}")

            # Find WATERUSE:EQUIPMENT schedule name from original IDF
            water_objs = orig_idf.idfobjects.get('WATERUSE:EQUIPMENT', [])
            if water_objs:
                water_sch_name = getattr(water_objs[0], 'Flow_Rate_Fraction_Schedule_Name', None)
                if water_sch_name:
                    parsed = parse_schedule_values(orig_idf, water_sch_name)
                    if parsed:
                        default_water_values = parsed
                        if verbose:
                            print(f"  Parsed original WATER schedule: {water_sch_name}")
                            
        except Exception as e:
            print(f"  Warning: Could not parse original IDF schedules: {e}")
    print(f"  Falling back to presence mask only (1.0 when home).")

    # If parsing failed or wasn't attempted (NUs_RC1.idf case), try Single Building Fallback
    # This ensures neighbourhood defaults match single building defaults (higher loads)
    # rather than the conservative hardcoded profiles.
    if default_light_values == {'Weekday': default_light_weekday, 'Weekend': default_light_weekend}:
        l_fb, e_fb, w_fb = _get_single_building_fallback_profiles(verbose)
        if l_fb: default_light_values = l_fb
        if e_fb: default_equip_values = e_fb
        if w_fb: default_water_values = w_fb

    print(f"\nInjecting schedules for {len(schedules_list)} buildings...")

    # Initialize lighting generator with EPW path
    lighting_gen = schedule_generator.LightingGenerator(epw_path=epw_path)

    for bldg_idx, schedule_data in enumerate(schedules_list):
        hh_id = schedule_data['hh_id']
        bldg_id = f"Bldg_{bldg_idx}"

        if verbose:
            print(f"  Building {bldg_idx}: Household {hh_id}")

        # Helper to format schedule data for compact schedules
        def fmt_for_compact(data_list: list) -> list:
            return [entry['occ'] for entry in sorted(data_list, key=lambda x: x['hour'])]

        def to_hour_value_list(values: list) -> list:
            """Convert flat list of 24 values to [{hour, value}] format."""
            return [{'hour': h, 'value': v} for h, v in enumerate(values)]

        # Get weekday/weekend data
        weekday_data = schedule_data.get('Weekday', [])
        weekend_data = schedule_data.get('Weekend', [])

        if not weekday_data or not weekend_data:
            print(f"    Warning: Missing schedule data for HH {hh_id}, skipping.")
            continue

        weekday_occ = fmt_for_compact(weekday_data)
        weekend_occ = fmt_for_compact(weekend_data)
        weekday_met = [entry['met'] for entry in sorted(weekday_data, key=lambda x: x['hour'])]
        weekend_met = [entry['met'] for entry in sorted(weekend_data, key=lambda x: x['hour'])]

        # Find and update the placeholder schedules
        # 1. Occupancy schedule (Occ_Bldg_X)
        occ_sch_name = f"Occ_{bldg_id}"
        occ_schedules = [s for s in idf.idfobjects["SCHEDULE:COMPACT"] if s.Name == occ_sch_name]
        if occ_schedules:
            occ_sch = occ_schedules[0]
            occ_sch.obj = ["Schedule:Compact"] + create_compact_schedule(
                occ_sch_name, "Fractional", {
                    'Weekday': to_hour_value_list(weekday_occ),
                    'Weekend': to_hour_value_list(weekend_occ)
                }
            )

        # 2. Activity schedule (Activity_Bldg_X)
        act_sch_name = f"Activity_{bldg_id}"
        act_schedules = [s for s in idf.idfobjects["SCHEDULE:COMPACT"] if s.Name == act_sch_name]
        if act_schedules:
            act_sch = act_schedules[0]
            act_sch.obj = ["Schedule:Compact"] + create_compact_schedule(
                act_sch_name, "Activity Level", {
                    'Weekday': to_hour_value_list(weekday_met),
                    'Weekend': to_hour_value_list(weekend_met)
                }
            )

        # 3. Lighting schedule (Light_Bldg_X) - Daylight Threshold Method
        light_sch_name = f"Light_{bldg_id}"
        weekday_light = lighting_gen.generate(
            weekday_occ, default_schedule=default_light_values['Weekday'], day_type='Weekday'
        )
        weekend_light = lighting_gen.generate(
            weekend_occ, default_schedule=default_light_values['Weekend'], day_type='Weekend'
        )

        light_schedules = [s for s in idf.idfobjects["SCHEDULE:COMPACT"] if s.Name == light_sch_name]
        if light_schedules:
            light_sch = light_schedules[0]
            light_sch.obj = ["Schedule:Compact"] + create_compact_schedule(
                light_sch_name, "Fractional", {
                    'Weekday': to_hour_value_list(weekday_light),
                    'Weekend': to_hour_value_list(weekend_light)
                }
            )

        # 4. Equipment schedule (Equip_Bldg_X) - Presence Filter Method
        equip_sch_name = f"Equip_{bldg_id}"
        equip_pf_weekday = schedule_generator.PresenceFilter(default_equip_values['Weekday'], weekday_occ)
        equip_pf_weekend = schedule_generator.PresenceFilter(default_equip_values['Weekend'], weekend_occ)
        weekday_equip = equip_pf_weekday.apply(weekday_occ)
        weekend_equip = equip_pf_weekend.apply(weekend_occ)

        equip_schedules = [s for s in idf.idfobjects["SCHEDULE:COMPACT"] if s.Name == equip_sch_name]
        if equip_schedules:
            equip_sch = equip_schedules[0]
            equip_sch.obj = ["Schedule:Compact"] + create_compact_schedule(
                equip_sch_name, "Fractional", {
                    'Weekday': to_hour_value_list(weekday_equip),
                    'Weekend': to_hour_value_list(weekend_equip)
                }
            )

        # 5. Water Use schedule (Water_Bldg_X) - Presence Filter Method
        water_sch_name = f"Water_{bldg_id}"
        water_pf_weekday = schedule_generator.PresenceFilter(default_water_values['Weekday'], weekday_occ)
        water_pf_weekend = schedule_generator.PresenceFilter(default_water_values['Weekend'], weekend_occ)
        weekday_water = water_pf_weekday.apply(weekday_occ)
        weekend_water = water_pf_weekend.apply(weekend_occ)
        
        # --- Visualization Integration ---
        if visualizer and sim_results_dir:
             plot_base = os.path.join(os.path.dirname(sim_results_dir), "SimResults_Plotting_Schedules")
             if batch_name:
                 plot_dir = os.path.join(plot_base, batch_name)
             else:
                 plot_dir = plot_base
                 
             plot_path = os.path.join(plot_dir, f"Bldg{bldg_idx}_HH{hh_id}.png")
             
             visualizer.visualize_schedule_integration(
                 presence_schedule=weekday_occ,
                 proj_light=weekday_light,
                 proj_equip=weekday_equip,
                 proj_water=weekday_water,
                 output_path=plot_path,
                 title=f"Integrated Schedules - Bldg {bldg_idx} HH {hh_id} (Weekday)",
                 active_load_equip=equip_pf_weekday.active_load,
                 base_load_equip=equip_pf_weekday.base_load,
                 active_load_water=water_pf_weekday.active_load,
                 base_load_water=water_pf_weekday.base_load,
                 default_light=default_light_values['Weekday'],
                 default_equip=default_equip_values['Weekday'],
                 default_water=default_water_values['Weekday']
             )        

        water_schedules = [s for s in idf.idfobjects["SCHEDULE:COMPACT"] if s.Name == water_sch_name]


        if water_schedules:
            water_sch = water_schedules[0]
            water_sch.obj = ["Schedule:Compact"] + create_compact_schedule(
                water_sch_name, "Fractional", {
                    'Weekday': to_hour_value_list(weekday_water),
                    'Weekend': to_hour_value_list(weekend_water)
                }
            )
        else:
            # Create new schedule object
            new_sch = idf.newidfobject("SCHEDULE:COMPACT")
            new_sch.obj = ["Schedule:Compact"] + create_compact_schedule(
                water_sch_name, "Fractional", {
                    'Weekday': to_hour_value_list(weekday_water),
                    'Weekend': to_hour_value_list(weekend_water)
                }
            )

    # Update WaterUse:Equipment objects to point to new Water_Bldg_X schedules
    # Assumption: water_objs[i] corresponds to schedules_list[i] (Building i+1)
    water_equip_objs = idf.idfobjects.get('WATERUSE:EQUIPMENT', [])
    if len(water_equip_objs) == len(schedules_list):
        if verbose:
            print(f"  Updating {len(water_equip_objs)} WaterUse:Equipment objects with new schedules.")
        for i, obj in enumerate(water_equip_objs):
            bldg_id_str = f"Bldg_{i}" # Assuming 0-based index from loop above matches
            # The loop used range(len(schedules_list)) so bldg_idx=0 -> Bldg_0
            # Wait, the loop used `bldg_id = f"Bldg_{bldg_idx}"`.
            # So `Water_Bldg_0`, `Water_Bldg_1` etc.
            
            # Check if we should use 1-based or 0-based?
            # The previous code used `bldg_idx, schedule_data in enumerate(schedules_list)`.
            # So `Bldg_0` is the first one.
            
            target_sch_name = f"Water_Bldg_{i}"
            obj.Flow_Rate_Fraction_Schedule_Name = target_sch_name
    elif water_equip_objs:
        print(f"  Warning: Mismatch between WaterUse objects ({len(water_equip_objs)}) and Buildings ({len(schedules_list)}). Skipping object update.")

    # Optimize and save
    idf_optimizer.optimize_idf(idf, verbose=verbose)
    idf.saveas(output_path)
    print(f"Neighbourhood IDF saved to: {output_path}")


def inject_neighbourhood_default_schedules(
    idf_path: str,
    output_path: str,
    n_buildings: int,
    verbose: bool = True
) -> None:
    """
    Injects DEFAULT residential schedules into a prepared neighbourhood IDF.
    
    This is used for the "Default" scenario in comparative simulations.
    It applies DOE MidRise Apartment schedules from OpenStudio Standards,
    providing a proper baseline for comparison.
    
    Data Source:
        - U.S. Department of Energy (DOE) Commercial Reference Buildings
        - OpenStudio Standards Gem (NREL)
        - ASHRAE Standard 90.1 compliant schedules
    
    Args:
        idf_path: Path to the prepared neighbourhood IDF.
        output_path: Path to save the modified IDF.
        n_buildings: Number of buildings in the neighbourhood.
        verbose: Whether to print progress messages.
    """
    # Initialize IDF
    IDF.setiddname(os.environ.get('IDD_FILE') or "Energy+.idd")
    idf = IDF(idf_path)
    
    # Load DOE MidRise Apartment standard schedules
    standard_schedules = idf_optimizer.load_standard_residential_schedules(verbose=verbose)
    
    # Extract profiles from standard schedules
    default_light_weekday = standard_schedules.get('lighting', {}).get('Weekday', [0.1] * 24)
    default_light_weekend = standard_schedules.get('lighting', {}).get('Weekend', default_light_weekday)
    
    default_equip_weekday = standard_schedules.get('equipment', {}).get('Weekday', [0.5] * 24)
    default_equip_weekend = standard_schedules.get('equipment', {}).get('Weekend', default_equip_weekday)
    
    default_occ_weekday = standard_schedules.get('occupancy', {}).get('Weekday', [0.5] * 24)
    default_occ_weekend = standard_schedules.get('occupancy', {}).get('Weekend', default_occ_weekday)
    
    default_water_weekday = standard_schedules.get('dhw', {}).get('Weekday', [0.1] * 24)
    default_water_weekend = standard_schedules.get('dhw', {}).get('Weekend', default_water_weekday)
    
    # Default metabolic activity from standard schedules
    default_activity = standard_schedules.get('activity', 95.0)
    default_met_weekday = [default_activity] * 24
    default_met_weekend = [default_activity] * 24

    
    def to_hour_value_list(values: list) -> list:
        """Convert flat list of 24 values to [{hour, value}] format."""
        return [{'hour': h, 'value': v} for h, v in enumerate(values)]
    
    if verbose:
        print(f"\nInjecting DEFAULT schedules for {n_buildings} buildings...")
    
    for bldg_idx in range(n_buildings):
        bldg_id = f"Bldg_{bldg_idx}"
        
        if verbose:
            print(f"  Building {bldg_idx}: Default residential profile")
        
        # 1. Occupancy schedule (Occ_Bldg_X)
        occ_sch_name = f"Occ_{bldg_id}"
        occ_schedules = [s for s in idf.idfobjects["SCHEDULE:COMPACT"] if s.Name == occ_sch_name]
        if occ_schedules:
            occ_sch = occ_schedules[0]
            occ_sch.obj = ["Schedule:Compact"] + create_compact_schedule(
                occ_sch_name, "Fractional", {
                    'Weekday': to_hour_value_list(default_occ_weekday),
                    'Weekend': to_hour_value_list(default_occ_weekend)
                }
            )
        
        # 2. Activity schedule (Activity_Bldg_X)
        act_sch_name = f"Activity_{bldg_id}"
        act_schedules = [s for s in idf.idfobjects["SCHEDULE:COMPACT"] if s.Name == act_sch_name]
        if act_schedules:
            act_sch = act_schedules[0]
            act_sch.obj = ["Schedule:Compact"] + create_compact_schedule(
                act_sch_name, "Activity Level", {
                    'Weekday': to_hour_value_list(default_met_weekday),
                    'Weekend': to_hour_value_list(default_met_weekend)
                }
            )
        
        # 3. Lighting schedule (Light_Bldg_X) - use default profile directly (no Active Floor)
        light_sch_name = f"Light_{bldg_id}"
        light_schedules = [s for s in idf.idfobjects["SCHEDULE:COMPACT"] if s.Name == light_sch_name]
        if light_schedules:
            light_sch = light_schedules[0]
            light_sch.obj = ["Schedule:Compact"] + create_compact_schedule(
                light_sch_name, "Fractional", {
                    'Weekday': to_hour_value_list(default_light_weekday),
                    'Weekend': to_hour_value_list(default_light_weekend)
                }
            )
        
        # 4. Equipment schedule (Equip_Bldg_X) - use default profile directly (no Active Floor)
        equip_sch_name = f"Equip_{bldg_id}"
        equip_schedules = [s for s in idf.idfobjects["SCHEDULE:COMPACT"] if s.Name == equip_sch_name]
        if equip_schedules:
            equip_sch = equip_schedules[0]
            equip_sch.obj = ["Schedule:Compact"] + create_compact_schedule(
                equip_sch_name, "Fractional", {
                    'Weekday': to_hour_value_list(default_equip_weekday),
                    'Weekend': to_hour_value_list(default_equip_weekend)
                }
            )
        
        # 5. Water Use schedule (Water_Bldg_X)
        water_sch_name = f"Water_{bldg_id}"
        water_schedules = [s for s in idf.idfobjects["SCHEDULE:COMPACT"] if s.Name == water_sch_name]
        if water_schedules:
            water_sch = water_schedules[0]
            water_sch.obj = ["Schedule:Compact"] + create_compact_schedule(
                water_sch_name, "Fractional", {
                    'Weekday': to_hour_value_list(default_water_weekday),
                    'Weekend': to_hour_value_list(default_water_weekend)
                }
            )
        else:
            # Create new schedule object if needed
            new_sch = idf.newidfobject("SCHEDULE:COMPACT")
            new_sch.obj = ["Schedule:Compact"] + create_compact_schedule(
                water_sch_name, "Fractional", {
                    'Weekday': to_hour_value_list(default_water_weekday),
                    'Weekend': to_hour_value_list(default_water_weekend)
                }
            )
    
    # Update WaterUse:Equipment objects
    water_equip_objs = idf.idfobjects.get('WATERUSE:EQUIPMENT', [])
    if len(water_equip_objs) == n_buildings:
        for i, obj in enumerate(water_equip_objs):
            obj.Flow_Rate_Fraction_Schedule_Name = f"Water_Bldg_{i}"
    
    # Optimize and save
    idf_optimizer.optimize_idf(idf, verbose=verbose)
    idf.saveas(output_path)
    print(f"Neighbourhood Default IDF saved to: {output_path}")


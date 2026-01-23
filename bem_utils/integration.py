import csv
import glob
import json
import os
from collections import defaultdict
from typing import Optional
from eppy.modeleditor import IDF
from bem_utils import idf_optimizer


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


def inject_schedules(idf_path, output_path, hh_id, schedule_data):
    """
    Injects specific household schedules into an IDF file.
    
    Uses DOE MidRise Apartment schedules as the standardized baseline,
    then applies occupancy-based modifications for year scenarios.
    
    Args:
        idf_path (str): Path to the base IDF.
        output_path (str): Path to save the modified IDF.
        hh_id (str): Household ID.
        schedule_data (dict): Data for this household from load_schedules.
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

    # 4. Apply presence projection using STANDARD schedules as baseline
    # Formula: result = occ × MAX(standard_val, active_floor) + (1-occ) × baseload
    
    # [FIX] Apply Water Use Peak Scaling for Year Scenarios
    # The integration logic projects schedules but preserves original Peak Flow Rates.
    # We must scale the peaks to match the standard baseline consumption (~220 L/day).
    idf_optimizer.scale_water_use_peak_flow(idf, standard_schedules, verbose=True)
    
    load_targets = [
        ('LIGHTS', 'Schedule_Name', 'lighting', 0.50, 0.05),
        ('ELECTRICEQUIPMENT', 'Schedule_Name', 'equipment', 0.50, 0.35),
        ('GASEQUIPMENT', 'Schedule_Name', 'equipment', 0.50, 0.35),
        ('WATERUSE:EQUIPMENT', 'Flow_Rate_Fraction_Schedule_Name', 'dhw', 0.0, 0.0),
    ]
    
    created_schedules = {}
    
    for obj_type, field_name, std_key, active_floor, baseload in load_targets:
        objs = idf.idfobjects.get(obj_type, [])
        
        # Get standard schedule values
        std_values = standard_schedules.get(std_key, {}).get('Weekday', [0.5] * 24)
        
        for idx, obj in enumerate(objs):
            try:
                if not hasattr(obj, field_name):
                    continue
                
                # Create projected schedule using standard baseline
                cache_key = f"{obj_type}_{std_key}_{hh_id}"
                if cache_key in created_schedules:
                    setattr(obj, field_name, created_schedules[cache_key])
                    continue
                
                proj_data = {}
                for dtype in ['Weekday', 'Weekend']:
                    if dtype in occ_data:
                        proj_data[dtype] = []
                        std_vals = standard_schedules.get(std_key, {}).get(dtype, std_values)
                        
                        for h in range(24):
                            occ_val = occ_data[dtype][h] if h < len(occ_data[dtype]) else 0
                            std_val = std_vals[h] if h < len(std_vals) else 0.5
                            
                            if obj_type == 'WATERUSE:EQUIPMENT':
                                # Water: proportional with standard schedule
                                proj_val = occ_val * std_val
                            else:
                                # Lights/Equipment: hybrid proportional
                                active_value = max(std_val, active_floor)
                                proj_val = occ_val * active_value + (1.0 - occ_val) * baseload
                            
                            proj_data[dtype].append(proj_val)
                
                if not proj_data:
                    continue
                
                # Create new schedule
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

    # 5. Optimize & Save
    idf_optimizer.optimize_idf(idf, verbose=True)
    idf.saveas(output_path)


def inject_neighbourhood_schedules(
    idf_path: str,
    output_path: str,
    schedules_list: list[dict],
    original_idf_path: Optional[str] = None,
    verbose: bool = True
) -> None:
    """
    Injects multiple household schedules into a prepared neighbourhood IDF.

    This function expects the IDF to have been prepared by neighbourhood.prepare_neighbourhood_idf(),
    which creates per-building objects with schedule names like Occ_Bldg_0, Light_Bldg_0, etc.

    Args:
        idf_path: Path to the prepared neighbourhood IDF.
        output_path: Path to save the modified IDF.
        schedules_list: List of schedule_data dicts, one per building.
        original_idf_path: Path to the ORIGINAL IDF (before preparation) to parse default schedules.
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

    threshold = 0.3

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

        # 3. Lighting schedule (Light_Bldg_X) - presence-adjusted
        # Formula: updated_schedule = default_schedule × presence_mask
        light_sch_name = f"Light_{bldg_id}"
        weekday_light = []
        weekend_light = []
        for h in range(24):
            # Weekday Lights - Hybrid: occ × MAX(default, 0.50) + (1-occ) × 0.05
            occ_val = weekday_occ[h]
            default_val = default_light_values['Weekday'][h] if h < len(default_light_values['Weekday']) else 1.0
            active_value = max(default_val, 0.50)
            proj_val = occ_val * active_value + (1.0 - occ_val) * 0.05
            weekday_light.append(proj_val)

        for h in range(24):
            # Weekend Lights - Hybrid: occ × MAX(default, 0.50) + (1-occ) × 0.05
            occ_val = weekend_occ[h]
            default_val = default_light_values['Weekend'][h] if h < len(default_light_values['Weekend']) else 1.0
            active_value = max(default_val, 0.50)
            proj_val = occ_val * active_value + (1.0 - occ_val) * 0.05
            weekend_light.append(proj_val)
            
        light_schedules = [s for s in idf.idfobjects["SCHEDULE:COMPACT"] if s.Name == light_sch_name]
        if light_schedules:
            light_sch = light_schedules[0]
            light_sch.obj = ["Schedule:Compact"] + create_compact_schedule(
                light_sch_name, "Fractional", {
                    'Weekday': to_hour_value_list(weekday_light),
                    'Weekend': to_hour_value_list(weekend_light)
                }
            )

        # 4. Equipment schedule (Equip_Bldg_X) - presence-adjusted
        # Formula: updated_schedule = default_schedule × presence_mask
        equip_sch_name = f"Equip_{bldg_id}"
        weekday_equip = []
        weekend_equip = []
        for h in range(24):
            # Weekday Equipment - Hybrid: occ × MAX(default, 0.50) + (1-occ) × 0.35
            occ_val = weekday_occ[h]
            default_val = default_equip_values['Weekday'][h] if h < len(default_equip_values['Weekday']) else 1.0
            active_value = max(default_val, 0.50)
            proj_val = occ_val * active_value + (1.0 - occ_val) * 0.35
            weekday_equip.append(proj_val)

        for h in range(24):
            # Weekend Equipment - Hybrid: occ × MAX(default, 0.50) + (1-occ) × 0.35
            occ_val = weekend_occ[h]
            default_val = default_equip_values['Weekend'][h] if h < len(default_equip_values['Weekend']) else 1.0
            active_value = max(default_val, 0.50)
            proj_val = occ_val * active_value + (1.0 - occ_val) * 0.35
            weekend_equip.append(proj_val)

        equip_schedules = [s for s in idf.idfobjects["SCHEDULE:COMPACT"] if s.Name == equip_sch_name]
        if equip_schedules:
            equip_sch = equip_schedules[0]
            equip_sch.obj = ["Schedule:Compact"] + create_compact_schedule(
                equip_sch_name, "Fractional", {
                    'Weekday': to_hour_value_list(weekday_equip),
                    'Weekend': to_hour_value_list(weekend_equip)
                }
            )

        # 5. Water Use schedule (Water_Bldg_X) - presence-adjusted
        # Formula: updated_schedule = default_schedule × presence_mask
        water_sch_name = f"Water_{bldg_id}"
        weekday_water = []
        weekend_water = []
        for h in range(24):
            # Weekday Water
            default_val = default_water_values['Weekday'][h] if h < len(default_water_values['Weekday']) else 1.0
            presence = 1.0 if weekday_occ[h] > threshold else 0.0
            if presence > 0:
                weekday_water.append(max(default_val, 0.0)) # No active floor
            else:
                weekday_water.append(0.0) # Baseload (No draw)

        for h in range(24):
             # Weekend Water
            default_val = default_water_values['Weekend'][h] if h < len(default_water_values['Weekend']) else 1.0
            presence = 1.0 if weekend_occ[h] > threshold else 0.0
            if presence > 0:
                weekend_water.append(max(default_val, 0.0)) # No active floor
            else:
                weekend_water.append(0.0) # Baseload

        water_schedules = [s for s in idf.idfobjects["SCHEDULE:COMPACT"] if s.Name == water_sch_name]
        
        # If schedule doesn't exist, create it (unlike Lights/Equip where we seemingly only update if exists?)
        # Actually for Lights/Equip we checked `if light_schedules`. If inconsistent, we should consistently CREATE or UPDATE.
        # Since we want to ensure it exists for the WaterUse object update below, we should create/update.
        
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


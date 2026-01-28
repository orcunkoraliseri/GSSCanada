"""
IDF Optimizer Module.

Prepares IDF files for simulation by:
1. Fixing deprecated field values (E+ version compatibility)
2. Adding required output variables for energy analysis
3. Adding Output:SQLite for result extraction
4. Fixing simulation settings (timestep, solar distribution)
5. Injecting missing objects (OtherSideCoefficients, etc.)
6. Standardizing residential schedules to DOE MidRise Apartment baseline
"""
import os
import re
import json
from typing import Optional, List
from eppy.modeleditor import IDF
from bem_utils import config

# Constants for Lighting Override
DEFAULT_LIGHTING_SOURCE_IDF = "US+SF+CZ5A+elecres+slab+IECC_2024.idf"
DEFAULT_LIGHTING_SCHEDULE_NAME = "LightingDay_EELighting"


# Output variables required for comprehensive energy analysis
REQUIRED_OUTPUT_VARIABLES = [
    ('Zone Lights Electricity Energy', 'Hourly'),
    ('Zone Electric Equipment Electricity Energy', 'Hourly'),
    ('Fan Electricity Energy', 'Hourly'),
    ('Zone Air System Sensible Heating Energy', 'Hourly'),
    ('Zone Air System Sensible Cooling Energy', 'Hourly'),
    ('Zone Ideal Loads Supply Air Total Heating Energy', 'Hourly'),
    ('Zone Ideal Loads Supply Air Total Cooling Energy', 'Hourly'),
]

# Field value fixes for E+ 24.2 compatibility
FIELD_FIXES = {
    'PEOPLE': {
        'Mean_Radiant_Temperature_Calculation_Type': {
            'ZoneAveraged': 'EnclosureAveraged',
            'zoneaveraged': 'EnclosureAveraged',
        }
    }
}

# Missing objects that need to be injected if referenced but not defined
MISSING_OBJECTS = {
    'SURFPROPOTHSDCOEFSLABAVERAGE': {
        'object_type': 'SurfaceProperty:OtherSideCoefficients',
        'fields': {
            'Combined_ConvectiveRadiative_Film_Coefficient': 0,
            'Constant_Temperature': 18.0,
            'Constant_Temperature_Coefficient': 1,
            'External_DryBulb_Temperature_Coefficient': 0,
            'Ground_Temperature_Coefficient': 0,
            'Wind_Speed_Coefficient': 0,
            'Zone_Air_Temperature_Coefficient': 0,
        }
    }
}


def get_idf_version(file_path: str) -> Optional[str]:
    """Reads the IDF file to find the Version object."""
    with open(file_path, 'r', errors='ignore') as f:
        content = f.read()
    
    match = re.search(r"Version,\s*(\d+\.\d+);", content, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def optimize_idf(idf: IDF, verbose: bool = True) -> List[str]:
    """
    Optimizes an IDF object for simulation.
    
    Args:
        idf: Eppy IDF object.
        verbose: If True, print optimization messages.
    
    Returns:
        List of optimization actions performed.
    """
    actions = []
    
    # 1. Fix deprecated field values
    for obj_type, field_fixes in FIELD_FIXES.items():
        objs = idf.idfobjects.get(obj_type, [])
        for obj in objs:
            for field_name, value_map in field_fixes.items():
                if hasattr(obj, field_name):
                    current_val = getattr(obj, field_name)
                    if current_val and current_val.lower() in [k.lower() for k in value_map.keys()]:
                        new_val = value_map.get(current_val, value_map.get(current_val.lower()))
                        if new_val:
                            setattr(obj, field_name, new_val)
                            msg = f"Fixed {obj_type}.{field_name}: {current_val} -> {new_val}"
                            actions.append(msg)
                            if verbose:
                                print(f"  {msg}")
    
    # 2. Update Version to 24.2
    versions = idf.idfobjects.get('VERSION', [])
    if versions:
        current_ver = versions[0].Version_Identifier
        if current_ver != '24.2':
            versions[0].Version_Identifier = '24.2'
            msg = f"Updated Version: {current_ver} -> 24.2"
            actions.append(msg)
            if verbose:
                print(f"  {msg}")
    
    # 3. Add Output:SQLite if not present
    sql_outputs = idf.idfobjects.get('OUTPUT:SQLITE', [])
    if not sql_outputs:
        sql_obj = idf.newidfobject("Output:SQLite")
        sql_obj.Option_Type = "SimpleAndTabular"
        msg = "Added Output:SQLite (SimpleAndTabular)"
        actions.append(msg)
        if verbose:
            print(f"  {msg}")
    
    # 4. Add required output variables if missing
    existing_vars = set()
    for var in idf.idfobjects.get('OUTPUT:VARIABLE', []):
        existing_vars.add(var.Variable_Name)
    
    added_vars = 0
    for var_name, frequency in REQUIRED_OUTPUT_VARIABLES:
        if var_name not in existing_vars:
            var_obj = idf.newidfobject("Output:Variable")
            var_obj.Key_Value = "*"
            var_obj.Variable_Name = var_name
            var_obj.Reporting_Frequency = frequency
            added_vars += 1
    
    if added_vars > 0:
        msg = f"Added {added_vars} output variables"
        actions.append(msg)
        if verbose:
            print(f"  {msg}")
    
    # 4b. Add Output:Meter for Monthly Totals (for time-series plotting)
    REQUIRED_METERS = [
        ('Heating:EnergyTransfer', 'Monthly'),
        ('Cooling:EnergyTransfer', 'Monthly'),
        ('InteriorLights:Electricity', 'Monthly'),
        ('InteriorEquipment:Electricity', 'Monthly'),
        ('InteriorEquipment:Gas', 'Monthly'),
        ('Fans:Electricity', 'Monthly'),
        ('WaterSystems:EnergyTransfer', 'Monthly'),
        ('Electricity:Facility', 'Monthly'),
        ('Gas:Facility', 'Monthly')
    ]
    
    existing_meters = set()
    for meter in idf.idfobjects.get('OUTPUT:METER', []):
        existing_meters.add(meter.Key_Name)
        
    added_meters = 0
    for meter_name, frequency in REQUIRED_METERS:
        if meter_name not in existing_meters:
            meter_obj = idf.newidfobject("Output:Meter")
            meter_obj.Key_Name = meter_name
            meter_obj.Reporting_Frequency = frequency
            added_meters += 1
            
    if added_meters > 0:
        msg = f"Added {added_meters} output meters (Monthly)"
        actions.append(msg)
        if verbose:
            print(f"  {msg}")
    
    # 5. Fix missing SurfaceProperty:OtherSideCoefficients
    for obj_name, obj_config in MISSING_OBJECTS.items():
        obj_type = obj_config['object_type']
        obj_type_upper = obj_type.upper().replace(':', '')
        
        # Check if object exists
        existing_objs = idf.idfobjects.get(obj_type.upper(), [])
        obj_exists = any(o.Name.upper() == obj_name for o in existing_objs)
        
        if not obj_exists:
            # Check if any surface references it
            surfaces = idf.idfobjects.get('BUILDINGSURFACE:DETAILED', [])
            needs_obj = any(
                hasattr(s, 'Outside_Boundary_Condition_Object') and 
                s.Outside_Boundary_Condition_Object.upper() == obj_name 
                for s in surfaces
            )
            
            if needs_obj:
                new_obj = idf.newidfobject(obj_type)
                new_obj.Name = obj_name
                for field, value in obj_config['fields'].items():
                    setattr(new_obj, field, value)
                msg = f"Injected missing {obj_type}: {obj_name}"
                actions.append(msg)
                if verbose:
                    print(f"  {msg}")
    
    # 6. Fix Timestep (set to 4 if different)
    timesteps = idf.idfobjects.get('TIMESTEP', [])
    if timesteps:
        current_ts = timesteps[0].Number_of_Timesteps_per_Hour
        if current_ts != 4:
            timesteps[0].Number_of_Timesteps_per_Hour = 4
            msg = f"Updated Timestep: {current_ts} -> 4"
            actions.append(msg)
            if verbose:
                print(f"  {msg}")
    
    # 7. Fix Solar Distribution (FullInteriorAndExterior -> FullExterior for speed)
    buildings = idf.idfobjects.get('BUILDING', [])
    if buildings:
        for bldg in buildings:
            if hasattr(bldg, 'Solar_Distribution'):
                if bldg.Solar_Distribution == 'FullInteriorAndExterior':
                    bldg.Solar_Distribution = 'FullExterior'
                    msg = "Changed Solar Distribution: FullInteriorAndExterior -> FullExterior"
                    actions.append(msg)
                    if verbose:
                        print(f"  {msg}")
    
    return actions



# Cache for standard residential schedules (loaded once)
_STANDARD_SCHEDULES_CACHE: Optional[dict] = None


def load_lighting_override_from_idf() -> Optional[list[float]]:
    """
    Loads the high-usage lighting schedule from the standard Single Family IDF template.
    Returns:
        List of 24 float values representing the hourly profile, or None if failed.
    """
    try:
        # Construct path to BEM_Setup/Templates
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Use config for path safety if needed (though templates are in repo)
        template_idf_path = os.path.join(base_dir, 'BEM_Setup', 'Templates', DEFAULT_LIGHTING_SOURCE_IDF)
        
        if not os.path.exists(template_idf_path):
            return None
            
        # Ensure IDD is set
        if not IDF.getiddname():
             IDF.setiddname(config.IDD_FILE)

        idf = IDF(template_idf_path)
        
        # Use simple extraction (assuming it's a Schedule details we can parse or Schedule:Compact)
        # Note: We need helper 'parse_schedule_values' logic here or duplicate distinct logic.
        # But 'parse_schedule_values' is in integration.py. 
        # To avoid circular imports, we implement specific extraction for this known template.
        
        if not IDF.getiddname():
             IDF.setiddname(config.IDD_FILE)

        idf = IDF(template_idf_path)
        
        # Target: Schedule:Day:Hourly "LightingDay_EELighting"
        # Note: Previous inspection confirmed it is Schedule:Day:Hourly
        day_obj = idf.getobject('SCHEDULE:DAY:HOURLY', DEFAULT_LIGHTING_SCHEDULE_NAME)
        if day_obj:
            # Schedule:Day:Hourly format: Name, Type, Hour1, Hour2...
            # Fields in eppy obj.obj: [Type, Name, LimitsName, Hour1, Hour2...]
            # Hour 1 is at index 3
            raw_vals = day_obj.obj[3:]
            # Ensure we have 24 values
            if len(raw_vals) >= 24:
                return [float(x) for x in raw_vals[:24]]
                
        # Fallback to Interval if Hourly fails (for robustness)
        day_obj = idf.getobject('SCHEDULE:DAY:INTERVAL', DEFAULT_LIGHTING_SCHEDULE_NAME)
        if day_obj:
            values = [0.0] * 24
            fields = day_obj.obj[4:]  # Skip name, type, interpolate
            last_hour = 0
            i = 0
            while i < len(fields) - 1:
                time_str = str(fields[i]).strip() if fields[i] else ""
                val_str = str(fields[i+1]).strip() if fields[i+1] else "0"
                
                try:
                    if ':' in time_str:
                        hour_part = time_str.split(':')[0]
                        end_hour = int(hour_part)
                    else:
                        end_hour = int(time_str)
                    
                    value = float(val_str)
                    for h in range(last_hour, min(end_hour, 24)):
                        values[h] = value
                    last_hour = end_hour
                except:
                    pass
                i += 2
            return values
            
        print(f"  Warning: Lighting Schedule {DEFAULT_LIGHTING_SCHEDULE_NAME} not found in template.")
        return None

    except Exception as e:
        print(f"  Warning: Failed to load lighting override: {e}")
        return None


def load_standard_residential_schedules(verbose: bool = False) -> dict:
    """
    Loads standardized MidRise Apartment schedules from the DOE Commercial
    Reference Buildings (via OpenStudio Standards / schedule.json).

    Data Source:
        - U.S. Department of Energy (DOE) Commercial Reference Buildings
        - OpenStudio Standards Gem (NREL)
        - File: BEM_Setup/Templates/schedule.json

    Returns:
        dict: Standard residential schedules with 24-hour profiles:
              {
                  'occupancy': {'Weekday': [24 values], 'Weekend': [24 values]},
                  'equipment': {'Weekday': [24 values], 'Weekend': [24 values]},
                  'lighting':  {'Weekday': [24 values], 'Weekend': [24 values]},
                  'dhw':       {'Weekday': [24 values], 'Weekend': [24 values]},
                  'activity':  95.0  # Metabolic rate in Watts
              }
    """
    global _STANDARD_SCHEDULES_CACHE

    if _STANDARD_SCHEDULES_CACHE is not None:
        return _STANDARD_SCHEDULES_CACHE

    # Locate schedule.json
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    schedule_json_path = os.path.join(
        base_dir, 'BEM_Setup', 'Templates', 'schedule.json'
    )

    if not os.path.exists(schedule_json_path):
        if verbose:
            print(f"  Warning: schedule.json not found at {schedule_json_path}")
        return _get_fallback_schedules()

    try:
        with open(schedule_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        if verbose:
            print(f"  Warning: Could not load schedule.json: {e}")
        return _get_fallback_schedules()

    # Target schedules from MidRise Apartment
    schedule_mapping = {
        'occupancy': 'ApartmentMidRise OCC_APT_SCH',
        'equipment': 'ApartmentMidRise EQP_APT_SCH',
        'lighting': 'ApartmentMidRise LTG_APT_SCH',
        'dhw': 'ApartmentMidRise APT_DHW_SCH',
        'activity': 'ApartmentMidRise Activity Schedule',
    }

    result = {}

    for key, schedule_name in schedule_mapping.items():
        if schedule_name not in data:
            if verbose:
                print(f"  Warning: Schedule '{schedule_name}' not found")
            continue

        sch = data[schedule_name]

        if key == 'activity':
            # Activity is constant metabolic rate
            for ds in sch.get('day_schedules', []):
                if 'Default' in ds.get('identifier', ''):
                    result['activity'] = ds['values'][0]
                    break
            continue

        # Extract 24-hour profile from Default day schedule
        hourly_values = [0.0] * 24

        for ds in sch.get('day_schedules', []):
            if 'Default' in ds.get('identifier', ''):
                values = ds.get('values', [])
                times = ds.get('times', [])

                # Convert time-value pairs to 24-hour array
                for i, time_pair in enumerate(times):
                    hour = time_pair[0]
                    value = values[i] if i < len(values) else values[-1]

                    # Fill from this hour until next time point
                    if i + 1 < len(times):
                        end_hour = times[i + 1][0]
                    else:
                        end_hour = 24

                    for h in range(hour, min(end_hour, 24)):
                        hourly_values[h] = value

                break

        # For residential, Weekday and Weekend are often the same in DOE models
        result[key] = {
            'Weekday': hourly_values.copy(),
            'Weekend': hourly_values.copy()
        }

    # Ensure activity has a default
    if 'activity' not in result:
        result['activity'] = 95.0

    if verbose:
        print("  Loaded standard MidRise Apartment schedules from schedule.json")

    
    # [OVERRIDE] Apply Single Family High-Usage Lighting Schedule
    override_lighting = load_lighting_override_from_idf()
    if override_lighting:
        if verbose:
            print(f"  Applied Lighting Override from {DEFAULT_LIGHTING_SOURCE_IDF}")
        result['lighting'] = {
            'Weekday': override_lighting,
            'Weekend': override_lighting
        }

    _STANDARD_SCHEDULES_CACHE = result
    return result


def _get_fallback_schedules() -> dict:
    """
    Returns hardcoded fallback schedules if schedule.json is unavailable.
    Based on DOE MidRise Apartment reference building.
    """
    # MidRise Apartment Occupancy (high night, low day)
    occ_weekday = [
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.85,
        0.39, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25,
        0.30, 0.52, 0.87, 0.87, 0.87, 1.0, 1.0, 1.0
    ]

    # MidRise Apartment Equipment
    eqp_weekday = [
        0.45, 0.41, 0.39, 0.38, 0.38, 0.43, 0.54, 0.65,
        0.66, 0.67, 0.69, 0.70, 0.69, 0.66, 0.65, 0.68,
        0.80, 1.00, 1.00, 0.93, 0.89, 0.85, 0.71, 0.58
    ]

    # MidRise Apartment Lighting (low values - efficient lighting)
    ltg_weekday = [
        0.01, 0.01, 0.01, 0.01, 0.03, 0.07, 0.08, 0.07,
        0.03, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.04,
        0.08, 0.11, 0.15, 0.18, 0.18, 0.12, 0.07, 0.03
    ]

    # MidRise Apartment DHW (morning and evening peaks)
    dhw_weekday = [
        0.08, 0.04, 0.02, 0.02, 0.04, 0.27, 0.94, 1.00,
        0.96, 0.84, 0.76, 0.61, 0.53, 0.47, 0.41, 0.47,
        0.55, 0.73, 0.86, 0.82, 0.75, 0.61, 0.53, 0.29
    ]

    return {
        'occupancy': {'Weekday': occ_weekday, 'Weekend': occ_weekday.copy()},
        'equipment': {'Weekday': eqp_weekday, 'Weekend': eqp_weekday.copy()},
        'lighting': {'Weekday': ltg_weekday, 'Weekend': ltg_weekday.copy()},
        'dhw': {'Weekday': dhw_weekday, 'Weekend': dhw_weekday.copy()},
        'activity': 95.0
    }


def prepare_idf_for_simulation(idf_path: str, output_path: str = None, 
                                verbose: bool = True,
                                standardize_schedules: bool = True) -> bool:
    """
    Prepares an IDF file for simulation.
    
    Args:
        idf_path: Path to the source IDF file.
        output_path: Path to save the optimized IDF. If None, overwrites source.
        verbose: If True, print progress messages.
        standardize_schedules: If True, replaces schedules with DOE MidRise standard.
    
    Returns:
        True if successful, False otherwise.
    """
    if output_path is None:
        output_path = idf_path
    
    try:
        # Set IDD
        idd_file = os.environ.get('IDD_FILE')
        if idd_file:
            IDF.setiddname(idd_file)
        
        if verbose:
            print(f"Optimizing: {os.path.basename(idf_path)}")
        
        idf = IDF(idf_path)
        actions = optimize_idf(idf, verbose=verbose)
        
        # Apply residential schedule standardization if requested
        if standardize_schedules:
            std_schedules = load_standard_residential_schedules(verbose=verbose)
            std_actions = standardize_residential_schedules(idf, std_schedules, verbose=verbose)
            actions.extend(std_actions)
        
        if actions:
            idf.saveas(output_path)
            if verbose:
                print(f"  Saved optimized IDF: {os.path.basename(output_path)}")
        else:
            if verbose:
                print("  No optimizations needed.")
        
        return True
        
    except Exception as e:
        print(f"Error optimizing {idf_path}: {e}")
        return False

def scale_water_use_peak_flow(
    idf: IDF, 
    standard_schedules: dict, 
    target_vol_m3: float = 0.22, 
    verbose: bool = False
) -> List[str]:
    """
    Scales the Peak Flow Rate of all WaterUse:Equipment objects so that the
    total daily consumption matches the target volume (default 220 L/day)
    when driven by the Standard Residential DHW schedule.
    """
    actions = []
    water_objs = idf.idfobjects.get('WATERUSE:EQUIPMENT', [])
    
    if not water_objs or 'dhw' not in standard_schedules:
        return actions

    # Calculate sum of hourly fractions in standard schedule
    dhw_sch = standard_schedules['dhw']['Weekday']
    sum_fractions = sum(dhw_sch)
    
    if sum_fractions <= 0:
        return actions

    # Derived Total Peak Flow (m3/s) needed to hit daily target
    # Peak * Sum_Fractions * 3600 = Daily_Vol
    target_total_peak = target_vol_m3 / (sum_fractions * 3600)
    
    # Calculate existing total peak
    original_total_peak = 0.0
    for w in water_objs:
        if hasattr(w, 'Peak_Flow_Rate'):
             try:
                 val = float(w.Peak_Flow_Rate)
                 original_total_peak += val
             except:
                 pass
    
    scaling_factor = 1.0
    if original_total_peak > 0:
        scaling_factor = target_total_peak / original_total_peak
        if verbose:
            msg = f"  Rescaling WaterUse Peak Flows by {scaling_factor:.4f} (Target: ~{target_vol_m3*1000:.0f} L/day)"
            print(msg)
            actions.append(msg)
    
    # Apply scaling
    for w in water_objs:
        if hasattr(w, 'Peak_Flow_Rate'):
             try:
                 old_val = float(w.Peak_Flow_Rate)
                 new_val = old_val * scaling_factor
                 w.Peak_Flow_Rate = new_val
             except:
                 pass
            
    if verbose and scaling_factor != 1.0 and scaling_factor != 0.0:
         actions.append(f"Updated {len(water_objs)} WaterUse:Equipment objects with scaled flow")
         
    return actions


def standardize_residential_schedules(
    idf: IDF, 
    standard_schedules: dict,
    verbose: bool = True
) -> List[str]:
    """
    Standardizes residential schedules in an IDF to DOE MidRise Apartment baseline.
    
    This is the "gatekeeper" function that ensures ALL IDFs start from the same
    schedule baseline, enabling fair comparisons between Default and year scenarios.
    
    Data Source:
        - U.S. Department of Energy (DOE) Commercial Reference Buildings
        - OpenStudio Standards Gem (NREL)
        - ASHRAE Standard 90.1 compliant schedules
    
    Args:
        idf: Eppy IDF object to modify.
        standard_schedules: Dict from load_standard_residential_schedules().
        verbose: If True, print progress messages.
    
    Returns:
        List of actions performed.
    """
    actions = []
    
    def create_compact_schedule_obj(
        idf: IDF, 
        name: str, 
        type_limit: str, 
        hourly_values: list
    ):
        """Creates a Schedule:Compact object with 24 hourly values."""
        sch = idf.newidfobject("Schedule:Compact")
        
        # Build fields list
        fields = [
            "Schedule:Compact",
            name,
            type_limit,
            "Through: 12/31",
            "For: AllDays",
        ]
        
        # Add hourly values
        for hour in range(24):
            val = hourly_values[hour] if hour < len(hourly_values) else hourly_values[-1]
            fields.append(f"Until: {hour+1:02d}:00")
            fields.append(f"{val:.4f}")
        
        sch.obj = fields
        return sch
    
    # 1. Create standard schedule objects
    schedule_names = {}
    
    # Occupancy schedule
    if 'occupancy' in standard_schedules:
        occ_name = "Standard_Residential_Occupancy"
        create_compact_schedule_obj(
            idf, occ_name, "Fraction", 
            standard_schedules['occupancy']['Weekday']
        )
        schedule_names['occupancy'] = occ_name
        actions.append(f"Created schedule: {occ_name}")
    
    # Equipment schedule
    if 'equipment' in standard_schedules:
        eqp_name = "Standard_Residential_Equipment"
        create_compact_schedule_obj(
            idf, eqp_name, "Fraction", 
            standard_schedules['equipment']['Weekday']
        )
        schedule_names['equipment'] = eqp_name
        actions.append(f"Created schedule: {eqp_name}")
    
    # Lighting schedule
    if 'lighting' in standard_schedules:
        ltg_name = "Standard_Residential_Lighting"
        create_compact_schedule_obj(
            idf, ltg_name, "Fraction", 
            standard_schedules['lighting']['Weekday']
        )
        schedule_names['lighting'] = ltg_name
        actions.append(f"Created schedule: {ltg_name}")
    
    # DHW schedule
    if 'dhw' in standard_schedules:
        dhw_name = "Standard_Residential_DHW"
        create_compact_schedule_obj(
            idf, dhw_name, "Fraction", 
            standard_schedules['dhw']['Weekday']
        )
        schedule_names['dhw'] = dhw_name
        actions.append(f"Created schedule: {dhw_name}")
    
    # Activity schedule (constant metabolic rate)
    activity_val = standard_schedules.get('activity', 95.0)
    act_name = "Standard_Residential_Activity"
    act_sch = idf.newidfobject("Schedule:Compact")
    act_sch.obj = [
        "Schedule:Compact",
        act_name,
        "Any Number",
        "Through: 12/31",
        "For: AllDays",
        "Until: 24:00",
        f"{activity_val:.1f}"
    ]
    schedule_names['activity'] = act_name
    actions.append(f"Created schedule: {act_name} ({activity_val}W)")
    
    # 2. Apply schedules to load objects
    # People objects
    people_objs = idf.idfobjects.get('PEOPLE', [])
    for p in people_objs:
        if 'occupancy' in schedule_names:
            p.Number_of_People_Schedule_Name = schedule_names['occupancy']
        if 'activity' in schedule_names:
            p.Activity_Level_Schedule_Name = schedule_names['activity']
    if people_objs:
        actions.append(f"Updated {len(people_objs)} People objects")
    
    # Lights objects
    lights_objs = idf.idfobjects.get('LIGHTS', [])
    for lt in lights_objs:
        if 'lighting' in schedule_names:
            lt.Schedule_Name = schedule_names['lighting']
    if lights_objs:
        actions.append(f"Updated {len(lights_objs)} Lights objects")
    
    # Electric Equipment objects
    equip_objs = idf.idfobjects.get('ELECTRICEQUIPMENT', [])
    for eq in equip_objs:
        if 'equipment' in schedule_names:
            eq.Schedule_Name = schedule_names['equipment']
    if equip_objs:
        actions.append(f"Updated {len(equip_objs)} ElectricEquipment objects")
    
    # Gas Equipment objects
    gas_objs = idf.idfobjects.get('GASEQUIPMENT', [])
    for g in gas_objs:
        if 'equipment' in schedule_names:
            g.Schedule_Name = schedule_names['equipment']
    if gas_objs:
        actions.append(f"Updated {len(gas_objs)} GasEquipment objects")
    
    # WaterUse:Equipment objects
    water_objs = idf.idfobjects.get('WATERUSE:EQUIPMENT', [])
    if water_objs and 'dhw' in schedule_names:
        for w in water_objs:
            if hasattr(w, 'Flow_Rate_Fraction_Schedule_Name'):
                w.Flow_Rate_Fraction_Schedule_Name = schedule_names['dhw']
        
        # Scale Peak Flow Rates (Consolidated Load Strategy)
        scaling_actions = scale_water_use_peak_flow(idf, standard_schedules, verbose=verbose)
        actions.extend(scaling_actions)
        
        actions.append(f"Updated {len(water_objs)} WaterUse:Equipment objects with standard schedule and scaled flow")
    
    if verbose:
        print("  Standardized residential schedules (DOE MidRise Apartment baseline)")
        for action in actions:
            print(f"    {action}")
    
    return actions

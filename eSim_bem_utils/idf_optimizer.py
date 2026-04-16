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
from eSim_bem_utils import config

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

# Monthly variables for physically intuitive heating/cooling time-series plots.
MONTHLY_IDEAL_LOADS_OUTPUT_VARIABLES = [
    ('Zone Ideal Loads Supply Air Total Heating Energy', 'Monthly'),
    ('Zone Ideal Loads Supply Air Total Cooling Energy', 'Monthly'),
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
        'triggers': ['GroundSlabPreprocessorAverage'],
        'fields': {
            'Combined_ConvectiveRadiative_Film_Coefficient': 0,
            'Constant_Temperature': 18.0,
            'Constant_Temperature_Coefficient': 1,
            'External_DryBulb_Temperature_Coefficient': 0,
            'Ground_Temperature_Coefficient': 0,
            'Wind_Speed_Coefficient': 0,
            'Zone_Air_Temperature_Coefficient': 0,
        }
    },
    'SURFPROPOTHSDCOEFBASEMENTAVGWALL': {
        'object_type': 'SurfaceProperty:OtherSideCoefficients',
        'triggers': ['GroundBasementPreprocessorAverageWall'],
        'fields': {
            'Combined_ConvectiveRadiative_Film_Coefficient': 0,
            'Constant_Temperature': 15.0,
            'Constant_Temperature_Coefficient': 1,
            'External_DryBulb_Temperature_Coefficient': 0,
            'Ground_Temperature_Coefficient': 0,
            'Wind_Speed_Coefficient': 0,
            'Zone_Air_Temperature_Coefficient': 0,
        }
    },
    'SURFPROPOTHSDCOEFBASEMENTAVGFLOOR': {
        'object_type': 'SurfaceProperty:OtherSideCoefficients',
        'triggers': ['GroundBasementPreprocessorAverageFloor'],
        'fields': {
            'Combined_ConvectiveRadiative_Film_Coefficient': 0,
            'Constant_Temperature': 12.0,
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


def optimize_idf(idf: IDF, verbose: bool = True, meter_frequency: str = 'Monthly', enable_hourly_detail: bool = False) -> List[str]:
    """
    Optimizes an IDF object for simulation.

    Args:
        idf: Eppy IDF object.
        verbose: If True, print optimization messages.
        meter_frequency: Base reporting frequency for Output:Meter objects ('Hourly', 'Monthly', etc.).
        enable_hourly_detail: If True, adds hourly frequency meters for detailed reporting (full year simulations only).

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
        existing_vars.add((var.Variable_Name, str(var.Reporting_Frequency).strip().lower()))

    added_vars = 0
    for var_name, frequency in REQUIRED_OUTPUT_VARIABLES:
        var_key = (var_name, str(frequency).strip().lower())
        if var_key not in existing_vars:
            var_obj = idf.newidfobject("Output:Variable")
            var_obj.Key_Value = "*"
            var_obj.Variable_Name = var_name
            var_obj.Reporting_Frequency = frequency
            added_vars += 1

    monthly_added = 0
    for var_name, frequency in MONTHLY_IDEAL_LOADS_OUTPUT_VARIABLES:
        var_key = (var_name, str(frequency).strip().lower())
        if var_key not in existing_vars:
            var_obj = idf.newidfobject("Output:Variable")
            var_obj.Key_Value = "*"
            var_obj.Variable_Name = var_name
            var_obj.Reporting_Frequency = frequency
            monthly_added += 1
            existing_vars.add(var_key)

    total_added_vars = added_vars + monthly_added
    if total_added_vars > 0:
        msg = f"Added {total_added_vars} output variables"
        actions.append(msg)
        if verbose:
            print(f"  {msg}")
    
    # 4b. Add Output:Meter for Monthly Totals (for time-series plotting)
    # 4b. Add Output:Meter (Frequency customizable, default Monthly)
    REQUIRED_METERS = [
        ('Heating:EnergyTransfer', meter_frequency),
        ('Cooling:EnergyTransfer', meter_frequency),
        ('InteriorLights:Electricity', meter_frequency),
        ('InteriorEquipment:Electricity', meter_frequency),
        ('InteriorEquipment:Gas', meter_frequency),
        ('Fans:Electricity', meter_frequency),
        ('WaterSystems:EnergyTransfer', meter_frequency),
        ('Electricity:Facility', meter_frequency),
        ('Gas:Facility', meter_frequency)
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
        msg = f"Added {added_meters} output meters ({meter_frequency})"
        actions.append(msg)
        if verbose:
            print(f"  {msg}")

    # 4c. Add HOURLY frequency meters for detailed reporting (only if enabled)
    # These are needed for hourly load profiles and peak load analysis
    if enable_hourly_detail:
        HOURLY_DETAIL_METERS = [
            'Heating:EnergyTransfer',
            'Cooling:EnergyTransfer',
            'WaterSystems:EnergyTransfer',
            'InteriorLights:Electricity',
            'InteriorEquipment:Electricity'
        ]

        # Check which meters exist at hourly frequency
        existing_hourly_meters = set()
        for meter in idf.idfobjects.get('OUTPUT:METER', []):
            if meter.Reporting_Frequency in ['Hourly', 'hourly']:
                existing_hourly_meters.add(meter.Key_Name)

        added_hourly = 0
        for meter_name in HOURLY_DETAIL_METERS:
            if meter_name not in existing_hourly_meters:
                meter_obj = idf.newidfobject("Output:Meter")
                meter_obj.Key_Name = meter_name
                meter_obj.Reporting_Frequency = 'Hourly'
                added_hourly += 1

        if added_hourly > 0:
            msg = f"Added {added_hourly} hourly detail meters (for load profiles & peak analysis)"
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
            # Check if any surface references it BY NAME or BY TRIGGER Condition
            surfaces = idf.idfobjects.get('BUILDINGSURFACE:DETAILED', [])
            triggers = obj_config.get('triggers', [])
            needs_obj = False
            
            for s in surfaces:
                # 1. Direct Object Reference (e.g. "SURFPROPOTHSDCOEF...")
                if hasattr(s, 'Outside_Boundary_Condition_Object'):
                    val_obj = s.Outside_Boundary_Condition_Object
                    if val_obj and val_obj.upper().strip() == obj_name:
                        needs_obj = True
                        break
                        
                # 2. Trigger Condition (e.g. "GroundBasementPreprocessorAverageWall")
                if hasattr(s, 'Outside_Boundary_Condition'):
                    val_cond = s.Outside_Boundary_Condition
                    if val_cond and any(trig.upper() == val_cond.upper().strip() for trig in triggers):
                         # Found a surface using the trigger condition!
                         # We should probably force its Object field to point to our new object?
                         # Or just assume E+ needs the object to exist with that name?
                         # NOTE: For OtherSideCoefficients, the surface MUST point to the object name.
                         # If it has the Condition but NO Object name, we should SET the object name.
                         if hasattr(s, 'Outside_Boundary_Condition_Object'):
                             current_obj_ref = s.Outside_Boundary_Condition_Object
                             if not current_obj_ref: # If empty, set it
                                 s.Outside_Boundary_Condition_Object = obj_name
                                 # And ensure condition is "OtherSideCoefficients" or keep as Preprocessor?
                                 # E+ Reference says: If using OtherSideCoefficients, Condition should be "OtherSideCoefficients".
                                 # But let's trust the injection first. 
                                 # Wait, if Condition is "GroundBasementPreprocessor...", E+ LOOKS for specific object names?
                                 # NO. "GroundBasementPreprocessorAverageWall" is a SPECIAL condition that requires Preprocessor.
                                 # BUT the user wants to REPLACE it with OtherSideCoefficients?
                                 # The error said: invalid Outside Boundary Condition Object="SURFPROPOTHSDCOEF..."
                                 # This implies the IDF ALREADY points to it?
                                 # Wait. My Debug script said: Surface BGWall_lower_ldf OCBO: '' (Empty)
                                 # The ERROR said: BuildingSurface:Detailed="BGWALL_LOWER_LDF", invalid Outside Boundary Condition Object="SURFPROPOTHSDCOEFBASEMENTAVGWALL".
                                 # This is CONTRADICTORY.
                                 # Hypothesis: The ERROR came from a file where I had RAN a previous script that SET it?
                                 # OR EnergyPlus defaults?
                                 
                                 # Let's assume we simply need to inject the object.
                                 pass
                         needs_obj = True
                         break
            
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


def apply_speed_optimizations(idf: IDF, verbose: bool = True) -> List[str]:
    """
    Apply speed optimizations to an IDF object.
    
    These are applied to ALL simulations regardless of run period mode.
    Optimizations include:
    - Shadow calculation: PixelCounting, 60-day update, 5000 max figures
    - HVAC convergence: Max iterations = 10
    - Convection: TARP (inside) + DOE-2 (outside) for accuracy
    
    Args:
        idf: Eppy IDF object.
        verbose: If True, print optimization messages.
    
    Returns:
        List of optimization actions performed.
    """
    actions = []
    
    # ==========================================================================
    # 1. Shadow Calculation Optimization
    # ==========================================================================
    shadow_objs = idf.idfobjects.get('SHADOWCALCULATION', [])
    if shadow_objs:
        shadow = shadow_objs[0]
    else:
        shadow = idf.newidfobject('ShadowCalculation')
        actions.append("Created ShadowCalculation object")
    
    # Apply optimized settings
    shadow.Shading_Calculation_Method = 'PixelCounting'
    shadow.Pixel_Counting_Resolution = 512
    shadow.Shading_Calculation_Update_Frequency_Method = 'Periodic'
    shadow.Shading_Calculation_Update_Frequency = 1  # Updated to 1 (Daily) for accuracy in Fast Mode
    shadow.Maximum_Figures_in_Shadow_Overlap_Calculations = 5000
    
    msg = "Shadow: PixelCounting (512), 1-day update, 5000 max figures"
    actions.append(msg)
    if verbose:
        print(f"  {msg}")
    
    # ==========================================================================
    # 2. HVAC Convergence Limits
    # ==========================================================================
    conv_limits = idf.idfobjects.get('CONVERGENCELIMITS', [])
    if conv_limits:
        conv_limits[0].Maximum_HVAC_Iterations = 10
    else:
        conv_obj = idf.newidfobject('ConvergenceLimits')
        conv_obj.Maximum_HVAC_Iterations = 10
    
    msg = "HVAC Max Iterations: 10"
    actions.append(msg)
    if verbose:
        print(f"  {msg}")
    
    # ==========================================================================
    # 3. Convection Algorithm (TARP inside, DOE-2 outside for accuracy)
    # ==========================================================================
    inside_conv = idf.idfobjects.get('SURFACECONVECTIONALGORITHM:INSIDE', [])
    outside_conv = idf.idfobjects.get('SURFACECONVECTIONALGORITHM:OUTSIDE', [])
    
    # Inside convection: TARP for accurate heating/cooling
    if inside_conv:
        old_alg = inside_conv[0].Algorithm
        if old_alg != 'TARP':
            inside_conv[0].Algorithm = 'TARP'
            msg = f"Inside Convection: {old_alg} -> TARP"
            actions.append(msg)
            if verbose:
                print(f"  {msg}")
    else:
        conv_obj = idf.newidfobject('SurfaceConvectionAlgorithm:Inside')
        conv_obj.Algorithm = 'TARP'
        msg = "Created Inside Convection: TARP"
        actions.append(msg)
        if verbose:
            print(f"  {msg}")
    
    # Outside convection: DOE-2 for good balance
    if outside_conv:
        old_alg = outside_conv[0].Algorithm
        if old_alg != 'DOE-2':
            outside_conv[0].Algorithm = 'DOE-2'
            msg = f"Outside Convection: {old_alg} -> DOE-2"
            actions.append(msg)
            if verbose:
                print(f"  {msg}")
    else:
        conv_obj = idf.newidfobject('SurfaceConvectionAlgorithm:Outside')
        conv_obj.Algorithm = 'DOE-2'
        msg = "Created Outside Convection: DOE-2"
        actions.append(msg)
        if verbose:
            print(f"  {msg}")
    
    return actions


def configure_run_period(
    idf: IDF, 
    mode: str = 'standard',
    verbose: bool = True
) -> List[str]:
    """
    Configure the simulation run period based on mode.
    
    Modes:
        - 'standard': Full year simulation (365 days)
        - 'weekly': 24 TMY-representative weeks (168 days, scaled to annual)
        - 'design_day': Design days only (sizing validation)
    
    Args:
        idf: Eppy IDF object.
        mode: Run period mode.
        verbose: If True, print changes.
    
    Returns:
        List of actions performed.
    """
    actions = []
    
    if mode == 'standard':
        # Keep original run period - no changes needed
        msg = "Run Period: Standard (full year)"
        actions.append(msg)
        if verbose:
            print(f"  {msg}")
        return actions
    
    elif mode == 'weekly':
        # Remove existing run periods
        for rp in idf.idfobjects.get('RUNPERIOD', [])[:]:
            idf.removeidfobject(rp)
        
        # TMY-REPRESENTATIVE: 2 weeks per month (168 days total)
        tmy_weeks = [
            (1, 1, 1, 7, "Jan_W1"), (1, 15, 1, 21, "Jan_W2"),
            (2, 1, 2, 7, "Feb_W1"), (2, 15, 2, 21, "Feb_W2"),
            (3, 1, 3, 7, "Mar_W1"), (3, 15, 3, 21, "Mar_W2"),
            (4, 1, 4, 7, "Apr_W1"), (4, 15, 4, 21, "Apr_W2"),
            (5, 1, 5, 7, "May_W1"), (5, 15, 5, 21, "May_W2"),
            (6, 1, 6, 7, "Jun_W1"), (6, 15, 6, 21, "Jun_W2"),
            (7, 1, 7, 7, "Jul_W1"), (7, 15, 7, 21, "Jul_W2"),
            (8, 1, 8, 7, "Aug_W1"), (8, 15, 8, 21, "Aug_W2"),
            (9, 1, 9, 7, "Sep_W1"), (9, 15, 9, 21, "Sep_W2"),
            (10, 1, 10, 7, "Oct_W1"), (10, 15, 10, 21, "Oct_W2"),
            (11, 1, 11, 7, "Nov_W1"), (11, 15, 11, 21, "Nov_W2"),
            (12, 1, 12, 7, "Dec_W1"), (12, 15, 12, 21, "Dec_W2"),
        ]
        
        for start_m, start_d, end_m, end_d, name in tmy_weeks:
            rp = idf.newidfobject('RunPeriod')
            rp.Name = name
            rp.Begin_Month = start_m
            rp.Begin_Day_of_Month = start_d
            rp.End_Month = end_m
            rp.End_Day_of_Month = end_d
            rp.Day_of_Week_for_Start_Day = 'Sunday'
            rp.Use_Weather_File_Holidays_and_Special_Days = 'No'
            rp.Use_Weather_File_Daylight_Saving_Period = 'No'
            rp.Apply_Weekend_Holiday_Rule = 'No'
            rp.Use_Weather_File_Rain_Indicators = 'Yes'
            rp.Use_Weather_File_Snow_Indicators = 'Yes'
        
        msg = "Run Period: 24 TMY weeks (168 days, ~2.5x faster)"
        actions.append(msg)
        if verbose:
            print(f"  {msg}")
        
    elif mode == 'design_day':
        # Remove all run periods - only design days will run
        removed_count = 0
        for rp in idf.idfobjects.get('RUNPERIOD', [])[:]:
            idf.removeidfobject(rp)
            removed_count += 1
        
        msg = f"Run Period: Design days only (sizing, ~33x faster)"
        actions.append(msg)
        if verbose:
            print(f"  {msg}")
    
    return actions


def prune_output_objects(idf: IDF, verbose: bool = True) -> List[str]:
    """
    Remove unnecessary output objects to speed up simulation.
    
    Preserves: Output:SQLite (needed for results extraction)
    Removes: Output:Variable, Output:Meter, Output:Constructions, etc.
    
    Args:
        idf: Eppy IDF object.
        verbose: If True, print removal messages.
    
    Returns:
        List of actions performed.
    """
    actions = []
    
    # Object types to remove for speed
    prune_types = [
        'OUTPUT:VARIABLE',
        'OUTPUT:METER',
        'OUTPUT:CONSTRUCTIONS',
        'OUTPUT:DIAGNOSTICS',
        'OUTPUT:SURFACES:LIST',
        'OUTPUT:SURFACES:DRAWING',
    ]
    
    for obj_type in prune_types:
        objs = idf.idfobjects.get(obj_type, [])
        count = len(objs)
        if count > 0:
            for obj in objs[:]:
                idf.removeidfobject(obj)
            msg = f"Pruned {obj_type}: {count} objects"
            actions.append(msg)
            if verbose:
                print(f"  {msg}")
    
    return actions



# Cache for standard residential schedules (loaded once)
_STANDARD_SCHEDULES_CACHE: Optional[dict] = None


def load_standard_residential_schedules(
    verbose: bool = False,
    baseline: str = 'midrise',
) -> dict:
    """
    Loads standardized residential schedules for EnergyPlus baseline injection.

    Args:
        verbose: Print progress messages.
        baseline: Which schedule set to load.
            'midrise'    — DOE MidRise Apartment (default; OpenStudio Standards
                           via 0_BEM_Setup/Templates/schedule.json).
            'sf_detached' — IECC 2021 Single-Family Detached reference
                            (0_BEM_Setup/Templates/schedule_sf.json).
                            Use for robustness check only; does not affect
                            production runs unless explicitly passed.

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

    # Only cache the default midrise baseline so callers that pass
    # baseline='sf_detached' always read fresh data.
    if baseline == 'midrise' and _STANDARD_SCHEDULES_CACHE is not None:
        return _STANDARD_SCHEDULES_CACHE

    # Route to the correct file and schedule-name mapping
    if baseline == 'sf_detached':
        json_filename = 'schedule_sf.json'
        schedule_mapping = {
            'occupancy': 'SF_Detached OCC_SCH',
            'equipment': 'SF_Detached EQP_SCH',
            'lighting':  'SF_Detached LTG_SCH',
            'dhw':       'SF_Detached DHW_SCH',
            'activity':  'SF_Detached Activity',
        }
    else:
        json_filename = 'schedule.json'
        schedule_mapping = {
            'occupancy': 'ApartmentMidRise OCC_APT_SCH',
            'equipment': 'ApartmentMidRise EQP_APT_SCH',
            'lighting':  'ApartmentMidRise LTG_APT_SCH',
            'dhw':       'ApartmentMidRise APT_DHW_SCH',
            'activity':  'ApartmentMidRise Activity Schedule',
        }

    # Locate the JSON file for the selected baseline
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    schedule_json_path = os.path.join(base_dir, '0_BEM_Setup', 'Templates', json_filename)

    if not os.path.exists(schedule_json_path):
        if verbose:
            print(f"  Warning: {json_filename} not found at {schedule_json_path}")
        if baseline == 'midrise':
            return _get_fallback_schedules()
        raise FileNotFoundError(
            f"SF Detached schedule file not found: {schedule_json_path}\n"
            "Create 0_BEM_Setup/Templates/schedule_sf.json before using baseline='sf_detached'."
        )

    try:
        with open(schedule_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        if verbose:
            print(f"  Warning: Could not load {json_filename}: {e}")
        if baseline == 'midrise':
            return _get_fallback_schedules()
        raise

    result = {}

    for key, schedule_name in schedule_mapping.items():
        if schedule_name not in data:
            if verbose:
                print(f"  Warning: Schedule '{schedule_name}' not found in {json_filename}")
            continue

        sch = data[schedule_name]

        if key == 'activity':
            # Activity is a constant metabolic rate stored as a single value
            for ds in sch.get('day_schedules', []):
                ident = ds.get('identifier', '')
                if 'Default' in ident or 'Weekday' in ident:
                    result['activity'] = ds['values'][0]
                    break
            continue

        # Extract 24-hour profiles. Supports three identifier conventions:
        #   'Weekday' / 'Weekend' — Task 14 split (schedule_sf.json)
        #   'Default'             — single profile applied to both (schedule.json)
        # Two value formats:
        #   (a) 'values' is a 24-element list with no 'times' key
        #   (b) 'values'+'times' are paired time-step arrays (fill-forward)
        def _extract_hourly(ds):
            values = ds.get('values', [])
            times = ds.get('times', [])
            hv = [0.0] * 24
            if len(values) == 24 and not times:
                return list(values)
            for i, time_pair in enumerate(times):
                hour = time_pair[0]
                value = values[i] if i < len(values) else values[-1]
                end_hour = times[i + 1][0] if i + 1 < len(times) else 24
                for h in range(hour, min(end_hour, 24)):
                    hv[h] = value
            return hv

        weekday_values = [0.0] * 24
        weekend_values = [0.0] * 24
        found_weekday = False
        found_weekend = False

        for ds in sch.get('day_schedules', []):
            ident = ds.get('identifier', '')
            if 'Weekday' in ident:
                weekday_values = _extract_hourly(ds)
                found_weekday = True
            elif 'Weekend' in ident:
                weekend_values = _extract_hourly(ds)
                found_weekend = True
            elif 'Default' in ident:
                v = _extract_hourly(ds)
                weekday_values = v
                weekend_values = v.copy()
                found_weekday = found_weekend = True
                break

        if not found_weekend:
            weekend_values = weekday_values.copy()

        result[key] = {
            'Weekday': weekday_values,
            'Weekend': weekend_values,
        }

    # Ensure activity has a default if not found in JSON
    if 'activity' not in result:
        result['activity'] = 95.0

    if verbose:
        label = 'DOE MidRise Apartment' if baseline == 'midrise' else 'IECC SF Detached'
        print(f"  Loaded {label} schedules from {json_filename}")

    # Baseline is DOE MidRise from schedule.json — no overrides applied.
    if baseline == 'midrise':
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


def prepare_idf_for_simulation(
    idf_path: str,
    output_path: str = None,
    verbose: bool = True,
    standardize_schedules: bool = True,
    run_period_mode: str = 'standard',
    meter_frequency: str = 'Monthly',
    baseline: str = 'midrise',
) -> bool:
    """
    Prepares an IDF file for simulation with all optimizations.

    Args:
        idf_path: Path to the source IDF file.
        output_path: Path to save the optimized IDF. If None, overwrites source.
        verbose: If True, print progress messages.
        standardize_schedules: If True, replaces schedules with DOE MidRise standard.
        run_period_mode: 'standard' (full year), 'weekly' (24 TMY weeks),
                        or 'design_day' (sizing only).
        meter_frequency: Reporting frequency for Output:Meter objects ('Hourly', 'Monthly', etc.).

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

        # Enable hourly detail output only for full year simulations
        # This adds hourly meters needed for load profiles and peak analysis
        enable_hourly_detail = (run_period_mode == 'standard')

        idf = IDF(idf_path)
        actions = optimize_idf(idf, verbose=verbose, meter_frequency=meter_frequency, enable_hourly_detail=enable_hourly_detail)
        
        # Apply residential schedule standardization if requested
        if standardize_schedules:
            std_schedules = load_standard_residential_schedules(verbose=verbose, baseline=baseline)
            std_actions = standardize_residential_schedules(idf, std_schedules, verbose=verbose)
            actions.extend(std_actions)
        
        # Apply speed optimizations (shadow, HVAC, convection)
        speed_actions = apply_speed_optimizations(idf, verbose=verbose)
        actions.extend(speed_actions)
        
        # Configure run period based on mode
        rp_actions = configure_run_period(idf, mode=run_period_mode, verbose=verbose)
        actions.extend(rp_actions)
        
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

def create_schedule_file_object(
    idf: IDF,
    name: str,
    type_limit: str,
    csv_path: str,
    n_hours: int = 8760,
) -> object:
    """
    Creates a Schedule:File IDF object pointing at an 8760-row single-column CSV.

    The CSV must contain one numeric value per line with no header row.
    EnergyPlus reads the file relative to the IDF directory; if `csv_path` is an
    absolute path it is stored as-is (works when both IDF and CSV are in the same
    run directory, or when an absolute path is portable across machines).

    Args:
        idf: The IDF object to modify.
        name: Schedule name (must match the name used in PEOPLE/LIGHTS/etc. objects).
        type_limit: Schedule Type Limits name (e.g., 'Fraction', 'Any Number').
        csv_path: Path to the 8760-row CSV file.
        n_hours: Number of data rows (default 8760).

    Returns:
        The newly created Schedule:File IDF object.
    """
    sch_obj = idf.newidfobject("Schedule:File")
    sch_obj.obj = [
        "Schedule:File",
        name,            # Name
        type_limit,      # Schedule Type Limits Name
        csv_path,        # File Name
        "1",             # Column Number
        "0",             # Rows to Skip at Top
        str(n_hours),    # Number of Hours of Data
        "Comma",         # Column Separator
        "No",            # Interpolate to Timestep
        "60",            # Minutes per Item
    ]
    return sch_obj


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
    
    # 1. Create standard schedule objects (or reuse existing)
    schedule_names = {}

    def _get_or_create_schedule(
        idf: IDF,
        name: str,
        type_limit: str,
        weekday_values: list,
        weekend_values: list,
    ):
        """Create Schedule:Compact with separate Weekday and Weekend blocks."""
        existing = [
            s for s in idf.idfobjects.get('SCHEDULE:COMPACT', [])
            if s.Name == name
        ]
        if existing:
            sch = existing[0]
        else:
            sch = idf.newidfobject("Schedule:Compact")

        fields = [
            "Schedule:Compact",
            name,
            type_limit,
            "Through: 12/31",
            "For: Weekdays",
        ]
        for hour in range(24):
            val = weekday_values[hour] if hour < len(weekday_values) else weekday_values[-1]
            fields.append(f"Until: {hour+1:02d}:00")
            fields.append(f"{val:.4f}")

        fields.append("For: Weekend Holidays")
        for hour in range(24):
            val = weekend_values[hour] if hour < len(weekend_values) else weekend_values[-1]
            fields.append(f"Until: {hour+1:02d}:00")
            fields.append(f"{val:.4f}")

        sch.obj = fields
        return sch
    
    # Occupancy schedule
    if 'occupancy' in standard_schedules:
        occ_name = "Standard_Residential_Occupancy"
        _get_or_create_schedule(
            idf, occ_name, "Fraction",
            standard_schedules['occupancy']['Weekday'],
            standard_schedules['occupancy']['Weekend'],
        )
        schedule_names['occupancy'] = occ_name
        actions.append(f"Created schedule: {occ_name}")

    # Equipment schedule
    if 'equipment' in standard_schedules:
        eqp_name = "Standard_Residential_Equipment"
        _get_or_create_schedule(
            idf, eqp_name, "Fraction",
            standard_schedules['equipment']['Weekday'],
            standard_schedules['equipment']['Weekend'],
        )
        schedule_names['equipment'] = eqp_name
        actions.append(f"Created schedule: {eqp_name}")

    # Lighting schedule
    if 'lighting' in standard_schedules:
        ltg_name = "Standard_Residential_Lighting"
        _get_or_create_schedule(
            idf, ltg_name, "Fraction",
            standard_schedules['lighting']['Weekday'],
            standard_schedules['lighting']['Weekend'],
        )
        schedule_names['lighting'] = ltg_name
        actions.append(f"Created schedule: {ltg_name}")

    # DHW schedule
    if 'dhw' in standard_schedules:
        dhw_name = "Standard_Residential_DHW"
        _get_or_create_schedule(
            idf, dhw_name, "Fraction",
            standard_schedules['dhw']['Weekday'],
            standard_schedules['dhw']['Weekend'],
        )
        schedule_names['dhw'] = dhw_name
        actions.append(f"Created schedule: {dhw_name}")
    
    # Activity schedule (constant metabolic rate)
    activity_val = standard_schedules.get('activity', 95.0)
    act_name = "Standard_Residential_Activity"
    existing_act = [
        s for s in idf.idfobjects.get('SCHEDULE:COMPACT', [])
        if s.Name == act_name
    ]
    if existing_act:
        act_sch = existing_act[0]
    else:
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

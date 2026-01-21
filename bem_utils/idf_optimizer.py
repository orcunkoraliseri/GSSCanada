"""
IDF Optimizer Module.

Prepares IDF files for simulation by:
1. Fixing deprecated field values (E+ version compatibility)
2. Adding required output variables for energy analysis
3. Adding Output:SQLite for result extraction
4. Fixing simulation settings (timestep, solar distribution)
5. Injecting missing objects (OtherSideCoefficients, etc.)
"""
import os
import re
from typing import Optional, List
from eppy.modeleditor import IDF


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


def prepare_idf_for_simulation(idf_path: str, output_path: str = None, 
                                verbose: bool = True) -> bool:
    """
    Prepares an IDF file for simulation.
    
    Args:
        idf_path: Path to the source IDF file.
        output_path: Path to save the optimized IDF. If None, overwrites source.
        verbose: If True, print progress messages.
    
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

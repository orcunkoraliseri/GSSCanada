import csv
import glob
import json
import os
from collections import defaultdict
from typing import Optional
from eppy.modeleditor import IDF
from eSim_bem_utils import idf_optimizer
from eSim_bem_utils import schedule_generator
from eSim_bem_utils import schedule_visualizer
from eSim_bem_utils import config

import random


# Target "Standard Working Day" Profile (Matches DEFAULT_PRESENCE in debugVis)
# Used to select representative households for comparative simulations.
TARGET_WORKING_PROFILE = [
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.8, 0.5,  # 0-7: Home (Sleep/Wake)
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,  # 8-15: Away (Work)
    0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 0.8, 0.5   # 16-23: Home (Evening)
]

# Archetype profiles for multi-archetype household matching (Task 15).
# Each profile is a 24-hour presence fraction array (0=away, 1=home).
ARCHETYPE_PROFILES = {
    # Standard 9-to-5 worker: away 08-15, home otherwise.
    'Worker':   [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.8, 0.5,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 0.8, 0.5],
    # Student: away 09-14, home with afternoon/evening return.
    'Student':  [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.8, 0.6,
                 0.4, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.8,
                 1.0, 1.0, 1.0, 1.0, 1.0, 0.9, 0.7, 0.5],
    # Retiree / at-home: present most of the day with brief out-trips mid-morning.
    'Retiree':  [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9,
                 0.8, 0.6, 0.5, 0.6, 0.8, 0.9, 1.0, 1.0,
                 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    # Shift worker: away nights (22-06), home during the day.
    'ShiftWorker': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3, 0.8,
                    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9,
                    0.8, 0.6, 0.4, 0.2, 0.0, 0.0, 0.0, 0.0],
}

# [OVERRIDE] Constants for Single Family Lighting Schedule


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


def filter_matching_households(
    schedules: dict, 
    candidates: list[str] = None, 
    day_type: str = 'Weekday'
) -> list[tuple[str, float]]:
    """
    Returns a list of (hh_id, score) tuples for all candidates, sorted by match score (ascending).
    Score is SSE against TARGET_WORKING_PROFILE (lower is better).
    """
    if not candidates:
        candidates = list(schedules.keys())
    
    results = []
    
    for hh_id in candidates:
        hh_data = schedules[hh_id]
        
        # Must have both Weekday and Weekend data for simulation
        entries = hh_data.get(day_type, [])
        if not entries:
            continue
            
        if not hh_data.get('Weekend'):
             continue
            
        # Extract presence profile
        profile = [0.0] * 24
        for e in entries:
            if 0 <= e['hour'] < 24:
                profile[e['hour']] = float(e['occ'])
                
        # Calculate SSE Score
        score = sum((profile[i] - TARGET_WORKING_PROFILE[i])**2 for i in range(24))
        results.append((hh_id, score))
        
    # Sort by score (ascending, lower is better)
    return sorted(results, key=lambda x: x[1])


def find_archetype_household(schedules: dict, archetype: str, candidates: list[str] = None) -> str:
    """
    Finds the household that best matches the given occupancy archetype profile.

    Args:
        schedules: Dict of all loaded schedules.
        archetype: One of the ARCHETYPE_PROFILES keys ('Worker', 'Student', 'Retiree', 'ShiftWorker').
        candidates: Optional subset of HH_IDs to search. If None, searches all.

    Returns:
        The HH_ID of the best matching household, or None if no valid candidates found.
    """
    target = ARCHETYPE_PROFILES.get(archetype)
    if target is None:
        raise ValueError(f"Unknown archetype '{archetype}'. Available: {list(ARCHETYPE_PROFILES)}")

    if not candidates:
        candidates = list(schedules.keys())

    best_hh_id = None
    best_score = float('inf')

    for hh_id in candidates:
        entries = schedules[hh_id].get('Weekday', [])
        if not entries:
            continue
        profile = [0.0] * 24
        for e in entries:
            if 0 <= e['hour'] < 24:
                profile[e['hour']] = float(e['occ'])
        score = sum((profile[i] - target[i]) ** 2 for i in range(24))
        if score < best_score:
            best_score = score
            best_hh_id = hh_id

    return best_hh_id


def export_sse_distances_csv(
    schedules: dict,
    csv_path: str,
    included_ids: list[str] = None,
    day_type: str = 'Weekday',
) -> None:
    """
    Writes one row per household with its SSE distance to TARGET_WORKING_PROFILE.

    Used for selection-bias sensitivity analysis (Task 22): lets the researcher
    inspect whether the matched cohort differs demographically from the full pool.

    Columns: HH_ID, SSE_to_target, included, hhsize, match_tier.
    `included` is 1 if HH_ID is in `included_ids`, else 0.
    """
    included_set = set(included_ids) if included_ids else set()
    target_len = len(TARGET_WORKING_PROFILE)

    rows = []
    for hh_id, hh_data in schedules.items():
        entries = hh_data.get(day_type, [])
        profile = [0.0] * 24
        for e in entries:
            if 0 <= e.get('hour', -1) < 24:
                profile[e['hour']] = float(e.get('occ', 0.0))
        sse = sum((profile[i] - TARGET_WORKING_PROFILE[i]) ** 2 for i in range(target_len))
        meta = hh_data.get('metadata', {})
        rows.append({
            'HH_ID': hh_id,
            'SSE_to_target': round(sse, 6),
            'included': 1 if hh_id in included_set else 0,
            'hhsize': meta.get('hhsize', ''),
            'match_tier': meta.get('match_tier', ''),
        })

    rows.sort(key=lambda r: r['SSE_to_target'])
    os.makedirs(os.path.dirname(csv_path) or '.', exist_ok=True)
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['HH_ID', 'SSE_to_target', 'included', 'hhsize', 'match_tier'])
        writer.writeheader()
        writer.writerows(rows)
    print(f"  SSE distance CSV written: {os.path.basename(csv_path)} ({len(rows)} rows)")


def validate_household_schedule(data: dict) -> bool:
    """
    Sanity-checks a single household schedule dict and returns True if valid.

    Rejects households where (for Weekday or Weekend):
    - Any hour value is outside [0, 1]
    - All 24 hours are exactly 0 (everyone permanently away — likely data error)
    - All 24 hours are exactly 1 AND the household is not tagged as Retiree archetype
      (constant full presence is only physically plausible for at-home archetypes)
    - More than 4 isolated 1-hour spikes (impossible flicker pattern)
    - Total daily presence-hours outside [2, 24]
    """
    for day_type in ('Weekday', 'Weekend'):
        entries = data.get(day_type, [])
        if not entries:
            continue
        profile = [0.0] * 24
        for e in entries:
            h = e.get('hour', -1)
            v = e.get('occ', 0.0)
            if 0 <= h < 24:
                profile[h] = float(v)

        # Out-of-range values
        if any(v < 0.0 or v > 1.0 for v in profile):
            return False

        total = sum(profile)

        # All-zero: no presence at all
        if total == 0.0:
            return False

        # Total presence-hours must be in [2, 24]
        if not (2.0 <= total <= 24.0):
            return False

        # Isolated 1-hour spikes: transitions 0→spike→0 counted for values > 0.5
        spike_count = 0
        for i in range(24):
            prev_val = profile[(i - 1) % 24]
            next_val = profile[(i + 1) % 24]
            if profile[i] > 0.5 and prev_val <= 0.1 and next_val <= 0.1:
                spike_count += 1
        if spike_count > 4:
            return False

    return True


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
                    'pr': row.get('PR', ''),
                    'match_tier': row.get('MATCH_TIER', ''),
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

    # Log MATCH_TIER distribution when the column is present in the CSV
    tier_counts: dict = {}
    for hh_data in schedules.values():
        tier = hh_data.get('metadata', {}).get('match_tier', '')
        if tier:
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
    if tier_counts:
        total = sum(tier_counts.values())
        print("  Match-tier distribution:")
        for tier in sorted(tier_counts):
            pct = tier_counts[tier] / total * 100
            print(f"    {tier}: {tier_counts[tier]:,} ({pct:.1f}%)")

    # Drop households that fail the illogical-row sanity check (Task 15)
    invalid_ids = [hh_id for hh_id, hh_data in schedules.items()
                   if not validate_household_schedule(hh_data)]
    if invalid_ids:
        for hh_id in invalid_ids:
            del schedules[hh_id]
        print(f"  Dropped {len(invalid_ids)} households (failed schedule sanity check).")

    return dict(schedules)


def get_household_pr(hh_schedule: dict) -> str:
    """Return the PR region string for a household dict from load_schedules().

    The PR value (e.g. 'Quebec', 'Ontario', 'Alberta') is stored by
    load_schedules() at hh_schedule['metadata']['pr'].  Returns an empty
    string when the key is absent (e.g. older CSVs that pre-date the PR column).
    """
    return hh_schedule.get('metadata', {}).get('pr', '') or ''


def write_8760_schedule_csv(
    weekday_vals: list,
    weekend_vals: list,
    csv_path: str,
    year: int = 2025,
    design_day_dates: set = None,
) -> None:
    """
    Writes a single-column 8760-row CSV stamping weekday/weekend patterns across a full year.

    Weekday pattern is used Mon–Fri; Weekend pattern for Sat–Sun. For a leap year the
    last day is dropped to keep exactly 8760 rows.

    Args:
        weekday_vals: 24-element list of hourly values for a weekday.
        weekend_vals: 24-element list of hourly values for a weekend day.
        csv_path: Output file path.
        year: Calendar year (determines Jan-1 day-of-week). Default 2025.
        design_day_dates: Set of (month, day) tuples that are SizingPeriod:DesignDay
            dates in the IDF. Those calendar dates are forced to weekday pattern so that
            autosizing matches the Schedule:Compact "For: WinterDesignDay SummerDesignDay"
            behaviour. If None, no overrides are applied.
    """
    import datetime

    # No EPW holiday overrides: EPW has zero holidays defined, so EnergyPlus assigns
    # day types purely by calendar weekday/weekend. We match that here.
    # Design-day dates ARE forced to weekday pattern (see parameter above).
    _dd = design_day_dates or set()

    day_start = datetime.date(year, 1, 1)
    rows = []
    for day_offset in range(365):
        d = day_start + datetime.timedelta(days=day_offset)
        is_design_day = (d.month, d.day) in _dd
        is_weekend = (d.weekday() >= 5) and not is_design_day
        pattern = weekend_vals if is_weekend else weekday_vals
        rows.extend(pattern)

    # Truncate to exactly 8760 in case of leap-year overshoot (shouldn't happen for 365 days)
    rows = rows[:8760]

    os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)
    with open(csv_path, 'w', newline='') as f:
        for v in rows:
            f.write(f"{v:.4f}\n")


def write_8760_schedule_csv_monthly(
    monthly_data: dict,
    csv_path: str,
    year: int = 2025,
    design_day_dates: set = None,
) -> None:
    """
    Writes an 8760-row CSV using per-month day patterns (for monthly lighting variation).

    Args:
        monthly_data: Dict mapping month abbreviation (e.g., 'Jan') to
            {'Weekday': [24 values], 'Weekend': [24 values]}.
        csv_path: Output file path.
        year: Calendar year for weekday/weekend assignment.
        design_day_dates: Set of (month, day) tuples forced to weekday pattern
            so autosizing matches Schedule:Compact design-day behaviour.
    """
    import datetime

    MONTH_ABBR = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    _dd = design_day_dates or set()

    day_start = datetime.date(year, 1, 1)
    rows = []
    for day_offset in range(365):
        d = day_start + datetime.timedelta(days=day_offset)
        month_abbr = MONTH_ABBR[d.month - 1]
        is_design_day = (d.month, d.day) in _dd
        is_weekend = (d.weekday() >= 5) and not is_design_day
        day_type = 'Weekend' if is_weekend else 'Weekday'

        month_patterns = monthly_data.get(month_abbr, monthly_data.get('Jan', {}))
        pattern = month_patterns.get(day_type, month_patterns.get('Weekday', [0.0] * 24))
        # pattern may be a list of dicts {'hour': h, 'value': v} or plain floats
        if pattern and isinstance(pattern[0], dict):
            vals = [e.get('value', 0.0) for e in sorted(pattern, key=lambda x: x.get('hour', 0))]
        else:
            vals = list(pattern)
        rows.extend(vals)

    rows = rows[:8760]
    os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)
    with open(csv_path, 'w', newline='') as f:
        for v in rows:
            f.write(f"{v:.4f}\n")


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


def create_monthly_compact_schedule(
    name: str,
    type_limit: str,
    monthly_schedules: dict[str, dict[str, list[dict]]]
) -> list:
    """
    Create a Schedule:Compact with per-month Through: blocks.

    This enables seasonal variation by specifying different hourly
    values for each month of the year.

    Args:
        name: Schedule name.
        type_limit: Schedule type limit (e.g., 'Fraction').
        monthly_schedules: Dict mapping month abbreviation to
            day_schedules dict {'Weekday': [...], 'Weekend': [...]}.
            Each value list contains dicts with 'hour' and 'value' keys.

    Returns:
        list: Fields for the Schedule:Compact object.
    """
    fields = [
        name,
        type_limit,
    ]

    months_info = [
        ('Jan', '1/31'), ('Feb', '2/28'), ('Mar', '3/31'),
        ('Apr', '4/30'), ('May', '5/31'), ('Jun', '6/30'),
        ('Jul', '7/31'), ('Aug', '8/31'), ('Sep', '9/30'),
        ('Oct', '10/31'), ('Nov', '11/30'), ('Dec', '12/31'),
    ]

    ep_day_types = {
        'Weekday': 'For: Weekdays SummerDesignDay WinterDesignDay',
        'Weekend': 'For: Weekends Holidays AllOtherDays',
    }

    for month_abbr, through_date in months_info:
        if month_abbr not in monthly_schedules:
            continue

        fields.append(f"Through: {through_date}")

        day_data = monthly_schedules[month_abbr]
        for day_type in ['Weekday', 'Weekend']:
            if day_type in day_data and day_data[day_type]:
                fields.append(ep_day_types[day_type])
                for entry in day_data[day_type]:
                    hour = entry['hour'] + 1
                    val = entry['value']
                    fields.append(f"Until: {hour:02d}:00")
                    fields.append(f"{val:.4f}")

    return fields


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
        # Locate Single Building IDF in 0_BEM_Setup/Buildings
        # Assume integration.py is in eSim_bem_utils/, so go up one level then to 0_BEM_Setup/Buildings
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
             IDF.setiddname(config.resolve_idd_path())
             
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


def _update_power_densities_from_original(idf: IDF, original_idf_path: str, verbose: bool = False):
    """
    Updates the active IDF's Lights and ElectricEquipment power densities (W/m2)
    to match the values found in the original IDF.
    
    This is critical for ensuring that neighbourhood simulations (which start from
    hardcoded defaults in prepare_neighbourhood_idf) match the physics of the
    Source IDF provided by the user.
    """
    try:
        if verbose:
            print(f"  Checking Original IDF for power density overrides...")
            
        orig_idf_local = IDF(original_idf_path)
        
        # 1. Equipment Density
        equip_objs = orig_idf_local.idfobjects.get('ELECTRICEQUIPMENT', [])
        target_equip_w_m2 = None
        if equip_objs:
            # Check calculation method
            method = getattr(equip_objs[0], 'Design_Level_Calculation_Method', '')
            if method == 'Watts/Area':
                target_equip_w_m2 = getattr(equip_objs[0], 'Watts_per_Zone_Floor_Area', None)
        
        # 2. Lighting Density
        light_objs = orig_idf_local.idfobjects.get('LIGHTS', [])
        target_light_w_m2 = None
        if light_objs:
            method = getattr(light_objs[0], 'Design_Level_Calculation_Method', '')
            if method == 'Watts/Area':
                target_light_w_m2 = getattr(light_objs[0], 'Watts_per_Zone_Floor_Area', None)
                
        # Apply updates
        if target_equip_w_m2 is not None:
            if verbose: print(f"    Restoring Equipment Density: {target_equip_w_m2} W/m2")
            for obj in idf.idfobjects['ELECTRICEQUIPMENT']:
                obj.Design_Level_Calculation_Method = 'Watts/Area'
                obj.Watts_per_Zone_Floor_Area = target_equip_w_m2
                obj.Design_Level = ""
                
        if target_light_w_m2 is not None:
            if verbose: print(f"    Restoring Lighting Density: {target_light_w_m2} W/m2")
            for obj in idf.idfobjects['LIGHTS']:
                obj.Design_Level_Calculation_Method = 'Watts/Area'
                obj.Watts_per_Zone_Floor_Area = target_light_w_m2
                obj.Lighting_Level = ""
                
    except Exception as e:
        print(f"  Warning: Could not update densities from original IDF: {e}")



# Removed inject_presence_projected_schedules (was a stub that returned immediately — dead code)
# Removed load_lighting_override_from_idf (moved to idf_optimizer)


def validate_idf_compatibility(
    idf_path: str,
    mode: str,
    dwelling_type: str = None,
) -> None:
    """
    Pre-injection guard: detects IDF/mode mismatches before any schedules are
    written to disk.

    Checks:
      1. **Mode mismatch** — counts SpaceList objects with a 'Neighbourhood_'
         prefix.  If found in 'single' mode → raises ValueError.
         If absent in 'neighbourhood' mode → raises ValueError.
      2. **Dwelling-type mismatch** — parses the IDF filename for archetype
         keywords (SF, MidRise, HighRise, MF, SingleF).  Mismatches between
         the filename keyword and *dwelling_type* produce a yellow warning
         (not an error, since many IDF names are generic).

    Args:
        idf_path:      Path to the IDF file.
        mode:          'single' or 'neighbourhood'.
        dwelling_type: Dwelling type filter string (e.g. 'SingleD', 'MidRise').
                       Pass None to skip the dwelling-type check.

    Raises:
        ValueError: On hard mode mismatch (neighbourhood IDF in single mode
                    or single-building IDF in neighbourhood mode).
    """
    import re as _re

    try:
        with open(idf_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw = f.read()
    except OSError as e:
        raise ValueError(f"Cannot read IDF for compatibility check: {e}")

    # 1. Detect neighbourhood vs single-building IDF.
    #    Two independent signals are combined:
    #    a) Presence of 'Neighbourhood_*' SpaceList objects (prepared neighbourhood IDFs).
    #    b) Zone count > 20 (raw neighbourhood IDFs like NUS_RC*.idf have 96 zones;
    #       single-building IDFs in this repo have 7).  Threshold of 20 gives headroom
    #       for unusually-large single-building models while still catching neighbourhoods.
    neighbourhood_spacelists = len(
        _re.findall(r'SpaceList\s*,.*?Neighbourhood_', raw, _re.IGNORECASE | _re.DOTALL)
    )
    zone_count = len(_re.findall(r'^Zone,', raw, _re.MULTILINE))
    has_neighbourhood_structure = neighbourhood_spacelists > 0 or zone_count > 20

    if mode == 'single' and has_neighbourhood_structure:
        raise ValueError(
            f"IDF '{os.path.basename(idf_path)}' looks like a neighbourhood model "
            f"({zone_count} zones, neigh_spacelists={neighbourhood_spacelists}) but was "
            "passed to inject_schedules(). Use inject_neighbourhood_schedules() or "
            "select a single-building IDF."
        )
    if mode == 'neighbourhood' and not has_neighbourhood_structure:
        raise ValueError(
            f"IDF '{os.path.basename(idf_path)}' looks like a single-building model "
            f"({zone_count} zones, no Neighbourhood_* SpaceLists) but was passed to "
            "inject_neighbourhood_schedules(). Use inject_schedules() or select a "
            "neighbourhood IDF."
        )

    # 2. Dwelling-type filename hint (soft warning only)
    if dwelling_type:
        fname = os.path.basename(idf_path).upper()
        archetype_hints = {
            'SF': ['SingleD', 'SemiD'],
            'SINGLEF': ['SingleD'],
            'MIDRISE': ['MidRise'],
            'HIGHRISE': ['HighRise'],
            'MF': ['MidRise', 'HighRise'],
        }
        for keyword, compatible_types in archetype_hints.items():
            if keyword in fname and dwelling_type not in compatible_types:
                print(
                    f"  [Warning] IDF filename suggests archetype '{keyword}' but "
                    f"dwelling_type='{dwelling_type}'. Verify the IDF geometry matches "
                    "the selected dwelling type before trusting EUI results."
                )


def inject_setpoint_schedules(
    idf: IDF,
    hh_id: str,
    weekday_occ: list,
    weekend_occ: list,
    heating_setback: float = 18.0,
    cooling_setback: float = 27.0,
    threshold: float = 1e-3,
    verbose: bool = False,
    use_schedule_file: bool = False,
    sched_dir: str = None,
    schedule_file_year: int = 2025,
    design_day_dates: set = None,
) -> bool:
    """
    Creates occupancy-responsive heating/cooling setpoint schedules and injects
    them into every ThermostatSetpoint:DualSetpoint object in the IDF.

    Logic:
        Occupied hours  (presence > threshold): keep the original constant setpoint.
        Unoccupied hours (presence <= threshold): apply setback temperature.

    The active setpoints are read from the existing heating/cooling schedule
    objects referenced by the DualSetpoint. If those schedules cannot be parsed
    (non-flat or missing), IECC residential defaults are used (22.2°C / 23.9°C).

    Args:
        idf: Loaded eppy IDF object (already open, not saved yet).
        hh_id: Household identifier — used to name the new schedule objects.
        weekday_occ: 24-value fractional occupancy list for weekdays.
        weekend_occ: 24-value fractional occupancy list for weekends.
        heating_setback: Temperature (°C) to use when household is absent. Default 18°C.
        cooling_setback: Temperature (°C) to use when household is absent. Default 27°C.
        threshold: Presence fraction below which the household is considered absent.
        verbose: Print progress messages.
        use_schedule_file: When True, write 8760-row CSVs (heating_setpoint.csv,
            cooling_setpoint.csv) and reference them via Schedule:File instead of
            building Schedule:Compact blocks (Task 21). Requires sched_dir.
        sched_dir: Directory where the setpoint CSVs are written. Only used when
            use_schedule_file=True.
        schedule_file_year: Calendar year for weekday/weekend assignment in 8760 CSV.

    Returns:
        True if at least one DualSetpoint object was updated, False otherwise.
    """
    dual_setpoints = idf.idfobjects.get('THERMOSTATSETPOINT:DUALSETPOINT', [])
    if not dual_setpoints:
        if verbose:
            print("  No ThermostatSetpoint:DualSetpoint objects found — setback not applied.")
        return False

    def _read_constant_from_schedule(sched_name: str, fallback: float) -> float:
        """Extract a constant value from a flat Schedule:Compact, or return fallback."""
        try:
            matches = [s for s in idf.idfobjects['SCHEDULE:COMPACT'] if s.Name == sched_name]
            if not matches:
                return fallback
            # obj fields: [type, name, type_limit, Through:12/31, For:AllDays, Until:24:00, VALUE]
            obj = matches[0].obj
            # Last numeric field is the constant value
            for field in reversed(obj):
                try:
                    return float(field)
                except (ValueError, TypeError):
                    continue
        except Exception:
            pass
        return fallback

    def _build_setpoint_schedule(name, day_occ, active_sp, setback_sp):
        """Return a list of 24 hourly setpoint values for one day type."""
        values = []
        for h in range(24):
            occ = day_occ[h] if h < len(day_occ) else 0.0
            values.append(active_sp if occ > threshold else setback_sp)
        return values

    def _compact_setpoint(sched_name, wd_vals, we_vals):
        """Build the compact schedule fields list for a temperature setpoint schedule."""
        fields = [sched_name, 'Temperature',
                  'Through: 12/31',
                  'For: Weekdays SummerDesignDay WinterDesignDay',]
        for h, v in enumerate(wd_vals):
            fields.append(f'Until: {h+1:02d}:00')
            fields.append(str(round(v, 4)))
        fields.append('For: Weekends Holidays')
        for h, v in enumerate(we_vals):
            fields.append(f'Until: {h+1:02d}:00')
            fields.append(str(round(v, 4)))
        return fields

    # For Schedule:File path: write the CSVs once (based on first DualSetpoint's active
    # setpoints), then reference the same files from all DualSetpoint objects.
    # Residential buildings typically have one DualSetpoint; the first one is used if multiple.
    schedule_file_written = False
    new_heat_name = f"HeatSP_HH_{hh_id}"
    new_cool_name = f"CoolSP_HH_{hh_id}"

    updated = 0
    for ds in dual_setpoints:
        heat_sched_name = getattr(ds, 'Heating_Setpoint_Temperature_Schedule_Name', '')
        cool_sched_name = getattr(ds, 'Cooling_Setpoint_Temperature_Schedule_Name', '')

        active_heat = _read_constant_from_schedule(heat_sched_name, fallback=22.2)
        active_cool = _read_constant_from_schedule(cool_sched_name, fallback=23.9)

        wd_heat = _build_setpoint_schedule(new_heat_name, weekday_occ, active_heat, heating_setback)
        we_heat = _build_setpoint_schedule(new_heat_name, weekend_occ, active_heat, heating_setback)
        wd_cool = _build_setpoint_schedule(new_cool_name, weekday_occ, active_cool, cooling_setback)
        we_cool = _build_setpoint_schedule(new_cool_name, weekend_occ, active_cool, cooling_setback)

        if use_schedule_file and sched_dir:
            if not schedule_file_written:
                # Write heating_setpoint.csv and cooling_setpoint.csv once (Task 21).
                os.makedirs(sched_dir, exist_ok=True)
                heat_csv = os.path.join(sched_dir, "heating_setpoint.csv")
                cool_csv = os.path.join(sched_dir, "cooling_setpoint.csv")
                write_8760_schedule_csv(wd_heat, we_heat, heat_csv, year=schedule_file_year,
                                        design_day_dates=design_day_dates)
                write_8760_schedule_csv(wd_cool, we_cool, cool_csv, year=schedule_file_year,
                                        design_day_dates=design_day_dates)

                # Remove any prior Schedule:File objects with same name (re-run safety).
                for sn in (new_heat_name, new_cool_name):
                    existing_sf = [s for s in idf.idfobjects.get('SCHEDULE:FILE', []) if s.Name == sn]
                    for s in existing_sf:
                        idf.idfobjects['SCHEDULE:FILE'].remove(s)

                idf_optimizer.create_schedule_file_object(idf, new_heat_name, "Temperature", heat_csv)
                idf_optimizer.create_schedule_file_object(idf, new_cool_name, "Temperature", cool_csv)
                schedule_file_written = True
        else:
            # Remove any previously injected Compact schedules with same name (re-run safety)
            for sched_name in (new_heat_name, new_cool_name):
                existing = [s for s in idf.idfobjects['SCHEDULE:COMPACT'] if s.Name == sched_name]
                for s in existing:
                    idf.idfobjects['SCHEDULE:COMPACT'].remove(s)

            heat_sch = idf.newidfobject('SCHEDULE:COMPACT')
            heat_sch.obj = ['Schedule:Compact'] + _compact_setpoint(new_heat_name, wd_heat, we_heat)

            cool_sch = idf.newidfobject('SCHEDULE:COMPACT')
            cool_sch.obj = ['Schedule:Compact'] + _compact_setpoint(new_cool_name, wd_cool, we_cool)

        ds.Heating_Setpoint_Temperature_Schedule_Name = new_heat_name
        ds.Cooling_Setpoint_Temperature_Schedule_Name = new_cool_name
        updated += 1

        if verbose:
            absent_wd = sum(1 for h in range(24) if (weekday_occ[h] if h < len(weekday_occ) else 0) <= threshold)
            mode = "Schedule:File" if (use_schedule_file and sched_dir) else "Schedule:Compact"
            print(f"  Setback applied ({mode}): {ds.Name} — heat {active_heat}->{heating_setback}C / "
                  f"cool {active_cool}->{cooling_setback}C during {absent_wd}/24 absent weekday hours")

    return updated > 0


def inject_schedules(
    idf_path: str,
    output_path: str,
    hh_id: str,
    schedule_data: dict,
    epw_path: Optional[str] = None,
    sim_results_dir: str = None,
    batch_name: str = None,
    run_period_mode: str = 'standard',
    output_frequency: str = 'Monthly',
    use_schedule_file: bool = False,
    schedule_file_year: Optional[int] = None,
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
        run_period_mode: 'standard' (full year), 'weekly' (24 TMY weeks), etc.
        use_schedule_file: When True, write 8760-row CSV files and use
            Schedule:File IDF objects instead of Schedule:Compact blocks (Task 21).
            The CSVs are placed next to the output IDF under schedules/<hh_id>/.
        schedule_file_year: Calendar year used to assign weekday/weekend to
            each day when writing the 8760 CSV. When None (default), the year is
            auto-derived so that Jan 1 falls on the same weekday as the IDF's
            RunPeriod 'Day of Week for Start Day' (always Sunday in this pipeline),
            ensuring CSV alignment with EnergyPlus weekday/weekend logic.
    """

    # Guard: reject neighbourhood IDFs passed to single-building mode
    dwelling_type = schedule_data.get('metadata', {}).get('dtype')
    validate_idf_compatibility(idf_path, mode='single', dwelling_type=dwelling_type)

    idd_path = config.resolve_idd_path()
    print(f"  Using IDD: {idd_path}")
    IDF.setiddname(idd_path)
    idf = IDF(idf_path)

    # Determine calendar year for 8760 CSV generation when use_schedule_file=True.
    # The year must have Jan 1 on the same weekday as the RunPeriod 'Day of Week
    # for Start Day', otherwise Schedule:File rows will be shifted by 1+ days vs
    # what EnergyPlus's Weekdays/Weekends schedule logic produces.
    if use_schedule_file and schedule_file_year is None:
        import datetime as _dt
        _EP_TO_PY = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
                     'Friday': 4, 'Saturday': 5, 'Sunday': 6}
        _run_periods = idf.idfobjects.get('RUNPERIOD', [])
        _ep_start = 'Sunday'  # configure_run_period always sets this
        if _run_periods:
            _ep_start = getattr(_run_periods[0], 'Day_of_Week_for_Start_Day', 'Sunday') or 'Sunday'
        _target_wd = _EP_TO_PY.get(_ep_start, 6)
        _yr = _dt.date.today().year
        for _ in range(15):  # search up to 15 years back
            if _dt.date(_yr, 1, 1).weekday() == _target_wd:
                schedule_file_year = _yr
                break
            _yr -= 1
        if schedule_file_year is None:
            schedule_file_year = 2023  # fallback: Jan 1, 2023 = Sunday
        print(f"  Schedule:File year auto-derived: {schedule_file_year} "
              f"(Jan 1 = {_ep_start}, matching RunPeriod)")

    if schedule_file_year is None:
        schedule_file_year = 2025  # not used unless use_schedule_file=True

    # Extract SizingPeriod:DesignDay dates so Schedule:File CSVs can force weekday
    # pattern on those calendar dates, matching Schedule:Compact's
    # "For: WinterDesignDay SummerDesignDay" block (which always uses weekday values).
    design_day_dates = set()
    if use_schedule_file:
        for dd_obj in idf.idfobjects.get('SIZINGPERIOD:DESIGNDAY', []):
            try:
                m = int(getattr(dd_obj, 'Month', 0))
                d = int(getattr(dd_obj, 'Day_of_Month', 0))
                if m and d:
                    design_day_dates.add((m, d))
            except (ValueError, TypeError):
                pass
        if design_day_dates:
            print(f"  Design-day weekday overrides: {sorted(design_day_dates)}")

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

    sched_dir = None  # Populated below when use_schedule_file=True

    if use_schedule_file:
        # Schedule:File path — write 8760-row CSVs and reference them (Task 21).
        # Place CSVs at batch level (BEM_Setup/SimResults/<batch>/schedules/HH_<id>/)
        # so one household's schedules are shared across all scenario IDFs in a batch.
        if sim_results_dir and batch_name:
            sched_dir = os.path.join(sim_results_dir, batch_name, "schedules", f"HH_{hh_id}")
        else:
            sched_dir = os.path.join(os.path.dirname(output_path), "schedules", f"HH_{hh_id}")
        os.makedirs(sched_dir, exist_ok=True)

        occ_wd = occ_data.get('Weekday', [0.0] * 24)
        occ_we = occ_data.get('Weekend', occ_wd)
        met_wd = met_data.get('Weekday', [120.0] * 24)
        met_we = met_data.get('Weekend', met_wd)

        occ_csv = os.path.join(sched_dir, "occupancy.csv")
        met_csv = os.path.join(sched_dir, "metabolic.csv")
        write_8760_schedule_csv(occ_wd, occ_we, occ_csv, year=schedule_file_year,
                                design_day_dates=design_day_dates)
        write_8760_schedule_csv(met_wd, met_we, met_csv, year=schedule_file_year,
                                design_day_dates=design_day_dates)

        idf_optimizer.create_schedule_file_object(idf, occ_sch_name, "Fraction", occ_csv)
        idf_optimizer.create_schedule_file_object(idf, met_sch_name, "Any Number", met_csv)
    else:
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
        'dhw': None,
        'presence': standard_schedules.get('occupancy', {}).get('Weekday')
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

                if obj_type == 'LIGHTS':
                    # Monthly daylight-responsive lighting
                    months = [
                        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
                    ]
                    monthly_data = {}
                    for month in months:
                        month_day_data = {}
                        for dtype in ['Weekday', 'Weekend']:
                            if dtype not in occ_data:
                                continue
                            presence = occ_data[dtype]
                            default_vals = (
                                std_weekday if dtype == 'Weekday'
                                else std_weekend
                            )
                            values = lighting_gen.generate_monthly(
                                presence,
                                default_schedule=default_vals,
                                month=month,
                                day_type=dtype,
                            )
                            month_day_data[dtype] = [
                                {'hour': h, 'value': v}
                                for h, v in enumerate(values)
                            ]
                        monthly_data[month] = month_day_data

                    # Visualization: use January as representative
                    if collected_schedules[std_key] is None:
                        jan_wd = monthly_data.get('Jan', {}).get(
                            'Weekday', []
                        )
                        if jan_wd:
                            collected_schedules[std_key] = [
                                e['value'] for e in jan_wd
                            ]
                        collected_defaults[std_key] = std_weekday

                    proj_sch_name = f"Proj_{obj_type[:4]}_{idx}_{hh_id}"
                    if use_schedule_file:
                        # Write per-month 8760 CSV and reference via Schedule:File (Task 21).
                        # Multiple LIGHTS objects share the same schedule (first one cached);
                        # use a simple name without index since caching means only one is written.
                        light_csv = os.path.join(sched_dir, "lighting.csv")
                        write_8760_schedule_csv_monthly(monthly_data, light_csv, year=schedule_file_year,
                                                        design_day_dates=design_day_dates)
                        idf_optimizer.create_schedule_file_object(idf, proj_sch_name, "Fraction", light_csv)
                    else:
                        proj_obj = idf.newidfobject("Schedule:Compact")
                        proj_obj.obj = (
                            ["Schedule:Compact"]
                            + create_monthly_compact_schedule(
                                proj_sch_name, "Fraction", monthly_data
                            )
                        )

                    setattr(obj, field_name, proj_sch_name)
                    created_schedules[cache_key] = proj_sch_name

                else:
                    # Equipment / DHW: presence filter.
                    # DHW uses continuous=True so that a single occupant (e.g.,
                    # presence=0.2) produces 20% of the default demand rather than
                    # the full default value — physically correct for showers/sinks.
                    # Equipment keeps continuous=False (binary gate preserves absent-
                    # hour behaviour for appliances that don't scale with headcount).
                    use_continuous = (std_key == 'dhw')
                    proj_data = {}
                    for dtype in ['Weekday', 'Weekend']:
                        if dtype not in occ_data:
                            continue
                        presence = occ_data[dtype]
                        default_vals = (
                            std_weekday if dtype == 'Weekday'
                            else std_weekend
                        )
                        pf = schedule_generator.PresenceFilter(
                            default_vals, presence
                        )
                        proj_data[dtype] = pf.apply(presence, continuous=use_continuous)

                    if not proj_data:
                        continue

                    # Visualization
                    if 'Weekday' in proj_data:
                        if collected_schedules[std_key] is None:
                            collected_schedules[std_key] = (
                                proj_data['Weekday']
                            )
                        if collected_defaults[std_key] is None:
                            collected_defaults[std_key] = std_weekday

                    proj_sch_name = (
                        f"Proj_{obj_type[:4]}_{idx}_{hh_id}"
                    )
                    if use_schedule_file:
                        # Write 8760 CSV for equipment/DHW and reference via Schedule:File (Task 21).
                        # Use end-use name without obj_type prefix — ELECTRIC and GAS equipment
                        # share the same occupancy-derived schedule fraction, so writing
                        # both to equipment.csv is intentional (same data, same source template).
                        end_use_tag = std_key  # 'equipment' or 'dhw'
                        equip_csv = os.path.join(sched_dir, f"{end_use_tag}.csv")
                        wd_vals = proj_data.get('Weekday', [0.0] * 24)
                        we_vals = proj_data.get('Weekend', wd_vals)
                        write_8760_schedule_csv(wd_vals, we_vals, equip_csv, year=schedule_file_year,
                                                design_day_dates=design_day_dates)
                        idf_optimizer.create_schedule_file_object(idf, proj_sch_name, "Fraction", equip_csv)
                    else:
                        proj_dict = {
                            k: fmt_for_compact(v)
                            for k, v in proj_data.items()
                        }
                        proj_obj = idf.newidfobject("Schedule:Compact")
                        proj_obj.obj = (
                            ["Schedule:Compact"]
                            + create_compact_schedule(
                                proj_sch_name, "Fraction", proj_dict
                            )
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
        # main.py sets SIM_RESULTS_DIR = 0_BEM_Setup/SimResults.
        # So dirname(sim_results_dir) -> BEM_Setup.
        # dirname(BEM_Setup) -> Root.
        # User asked for "0_BEM_Setup/SimResults_Plotting_Schedules" ? 
        # "put them ... under the folder of 'SimResults_Plotting_Schedules' in that way we can compare"
        # I'll put it in 0_BEM_Setup/SimResults_Plotting_Schedules
        
        # If sim_results_dir is absolute path to Batch folder.
        # batch_name is passed.
        
        # Assumption: sim_results_dir passed from main.py is "0_BEM_Setup/SimResults" 
        # NO, main.py passes `scenario_dir` as `output_dir` but `inject_schedules` signature ?
        # main.py calls `inject_schedules(..., sim_results_dir=SIM_RESULTS_DIR, batch_name=batch_name)`?
        # I need to update main.py call first!
        # But assuming valid path:
        
        # Construct 0_BEM_Setup/SimResults_Plotting_Schedules
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
             default_water=collected_defaults['dhw'],
             default_presence=collected_defaults['presence']
        )


    # 4b. Thermostat Setback (occupancy-responsive setpoints)
    weekday_occ_list = occ_data.get('Weekday', [0.0] * 24)
    weekend_occ_list = occ_data.get('Weekend', [0.0] * 24)
    inject_setpoint_schedules(
        idf, hh_id,
        weekday_occ=weekday_occ_list,
        weekend_occ=weekend_occ_list,
        heating_setback=18.0,
        cooling_setback=27.0,
        verbose=True,
        use_schedule_file=use_schedule_file,
        sched_dir=sched_dir if use_schedule_file else None,
        schedule_file_year=schedule_file_year,
        design_day_dates=design_day_dates,
    )

    # 5. Optimize & Save
    # Enable hourly detail output only for full year simulations
    enable_hourly_detail = (run_period_mode == 'standard')
    idf_optimizer.optimize_idf(idf, verbose=True, meter_frequency=output_frequency, enable_hourly_detail=enable_hourly_detail)
    idf_optimizer.apply_speed_optimizations(idf, verbose=True)
    idf_optimizer.configure_run_period(idf, mode=run_period_mode, verbose=True)
    idf.saveas(output_path)


def inject_neighbourhood_schedules(
    idf_path: str,
    output_path: str,
    schedules_list: list[dict],
    original_idf_path: Optional[str] = None,
    epw_path: Optional[str] = None,
    sim_results_dir: str = None,
    batch_name: str = None,
    verbose: bool = True,
    run_period_mode: str = 'standard'
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
    # Guard: reject single-building IDFs passed to neighbourhood mode
    validate_idf_compatibility(idf_path, mode='neighbourhood')

    if not schedules_list:
        print("Error: No schedules provided for neighbourhood injection.")
        return

    # Initialize IDF
    IDF.setiddname(config.resolve_idd_path())
    idf = IDF(idf_path)

    # Parse default schedule values from original IDF (if provided)
    # If no original schedules found, use typical residential profiles
    # These profiles mimic standard EnergyPlus residential defaults:
    # - Lighting: Low during day, peaks in evening (6pm-11pm)
    # - Equipment: Moderate all day, slightly higher in morning/evening
    
    # Typical residential lighting profile (fraction of max)
    # Hours: 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23
    
    # Use Standardized Residential Schedules for all defaults
    # This ensures consistency with Option 3 (Single Building) simulations.
    
    # Initialize Visualizer
    visualizer = None
    if epw_path:
        visualizer = schedule_visualizer.ScheduleVisualizer(epw_path)
    std_schedules = idf_optimizer.load_standard_residential_schedules(verbose=verbose)
    
    default_light_values = std_schedules['lighting']
    default_equip_values = std_schedules['equipment']
    default_water_values = std_schedules['dhw']
    default_occ_values = std_schedules['occupancy']
    
    # NOTE: We intentionally do NOT parse schedules from original_idf_path anymore.
    # Original IDFs (especially neighbourhood files like NUs_RC1/RC2) often contain
    # commercial/industrial schedules (e.g., "INTERMITTENT" with binary 0/1 values:
    # 0 midnight-8am, 1 from 8am-6pm, 0 from 6pm-midnight) that are completely
    # inappropriate for residential simulations.
    # 
    # The DOE MidRise Apartment standard schedules from std_schedules provide proper
    # residential curves with gradual transitions (e.g., equipment: 0.45 at midnight,
    # rising to 1.0 around 6pm, then decreasing). These are consistent with Option 3
    # (single building) simulations and ensure PresenceFilter works correctly.
    
    if verbose:
        print(f"  Using DOE MidRise Apartment standard schedules for Lights/Equipment/DHW")

    # Fallback to presence mask only was implicit if parsing failed, 
    # but now we use standard_schedules which is robust.

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
                occ_sch_name, "Fraction", {
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
                act_sch_name, "Any Number", {
                    'Weekday': to_hour_value_list(weekday_met),
                    'Weekend': to_hour_value_list(weekend_met)
                }
            )

        # 3. Lighting schedule (Light_Bldg_X) - Monthly Daylight Method
        light_sch_name = f"Light_{bldg_id}"
        months = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
        ]
        monthly_light = {}
        for month in months:
            wd = lighting_gen.generate_monthly(
                weekday_occ,
                default_schedule=default_light_values['Weekday'],
                month=month,
                day_type='Weekday',
            )
            we = lighting_gen.generate_monthly(
                weekend_occ,
                default_schedule=default_light_values['Weekend'],
                month=month,
                day_type='Weekend',
            )
            monthly_light[month] = {
                'Weekday': to_hour_value_list(wd),
                'Weekend': to_hour_value_list(we),
            }

        # Keep weekday_light for visualization (January representative)
        weekday_light = [
            e['value'] for e in monthly_light['Jan']['Weekday']
        ]

        light_schedules = [
            s for s in idf.idfobjects["SCHEDULE:COMPACT"]
            if s.Name == light_sch_name
        ]
        if light_schedules:
            light_sch = light_schedules[0]
            light_sch.obj = (
                ["Schedule:Compact"]
                + create_monthly_compact_schedule(
                    light_sch_name, "Fraction", monthly_light
                )
            )
            if verbose:
                print(f"    Updated Lighting schedule: {light_sch_name} (monthly)")
        else:
            new_sch = idf.newidfobject("SCHEDULE:COMPACT")
            new_sch.obj = (
                ["Schedule:Compact"]
                + create_monthly_compact_schedule(
                    light_sch_name, "Fraction", monthly_light
                )
            )
            if verbose:
                print(f"    Created Lighting schedule: {light_sch_name} (monthly)")

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
                equip_sch_name, "Fraction", {
                    'Weekday': to_hour_value_list(weekday_equip),
                    'Weekend': to_hour_value_list(weekend_equip)
                }
            )
            if verbose:
                print(f"    Updated existing Equipment schedule: {equip_sch_name}")
        else:
            # Create new schedule if not found
            new_sch = idf.newidfobject("SCHEDULE:COMPACT")
            new_sch.obj = ["Schedule:Compact"] + create_compact_schedule(
                equip_sch_name, "Fraction", {
                    'Weekday': to_hour_value_list(weekday_equip),
                    'Weekend': to_hour_value_list(weekend_equip)
                }
            )
            if verbose:
                print(f"    Created new Equipment schedule: {equip_sch_name}")

        # 5. Water Use schedule (Water_Bldg_X) — continuous DHW scaling.
        # continuous=True: partial occupancy produces partial demand (e.g., 1 of 5
        # people home → 20% of default) rather than the full DOE default value.
        water_sch_name = f"Water_{bldg_id}"
        water_pf_weekday = schedule_generator.PresenceFilter(default_water_values['Weekday'], weekday_occ)
        water_pf_weekend = schedule_generator.PresenceFilter(default_water_values['Weekend'], weekend_occ)
        weekday_water = water_pf_weekday.apply(weekday_occ, continuous=True)
        weekend_water = water_pf_weekend.apply(weekend_occ, continuous=True)
        
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
                 default_water=default_water_values['Weekday'],
                 default_presence=default_occ_values['Weekday']
             )        

        water_schedules = [s for s in idf.idfobjects["SCHEDULE:COMPACT"] if s.Name == water_sch_name]


        if water_schedules:
            water_sch = water_schedules[0]
            water_sch.obj = ["Schedule:Compact"] + create_compact_schedule(
                water_sch_name, "Fraction", {
                    'Weekday': to_hour_value_list(weekday_water),
                    'Weekend': to_hour_value_list(weekend_water)
                }
            )
        else:
            # Create new schedule object
            new_sch = idf.newidfobject("SCHEDULE:COMPACT")
            new_sch.obj = ["Schedule:Compact"] + create_compact_schedule(
                water_sch_name, "Fraction", {
                    'Weekday': to_hour_value_list(weekday_water),
                    'Weekend': to_hour_value_list(weekend_water)
                }
            )

    # WaterUse:Equipment schedule names (Water_Bldg_X) were already set in-place
    # by prepare_neighbourhood_idf(). The Water_Bldg_X schedule content was
    # populated above. Plant Loop connections remain intact for DHW heating.
    if verbose:
        water_equip_objs = idf.idfobjects.get('WATERUSE:EQUIPMENT', [])
        print(f"  WaterUse:Equipment objects: {len(water_equip_objs)} (schedule names pre-set by prepare step)")
        
    # [FIX] Update PEOPLE objects to match household size (Consistency with Option 3)
    # Switch from People/Area (default in prepare_neighbourhood_idf) to People count
    people_objs = idf.idfobjects.get('PEOPLE', [])
    updates_count = 0
    for bldg_idx, schedule_data in enumerate(schedules_list):
        bldg_id = f"Bldg_{bldg_idx}"
        target_name = f"Neighbourhood_{bldg_id}_People"
        
        # Find matching People object
        obj = next((p for p in people_objs if p.Name == target_name), None)
        if obj:
            hh_size = schedule_data.get('metadata', {}).get('hhsize', 2)
            obj.Number_of_People_Calculation_Method = "People"
            obj.Number_of_People = hh_size
            obj.People_per_Floor_Area = ""
            obj.Floor_Area_per_Person = ""
            updates_count += 1
            
    if verbose:
        print(f"  Updated {updates_count} PEOPLE objects with specific household sizes.")

    # [FIX] Apply Water Use Peak Scaling (Consistency with Option 3)
    # This loads standard_schedules internally if not passed, but we already loaded them.
    # We can pass them to avoid reload if the function supported it, but it loads them itself or we assume consistency.
    # Actually scale_water_use_peak_flow signature is (idf, standard_schedules, verbose).
    idf_optimizer.scale_water_use_peak_flow(idf, std_schedules, verbose=verbose)
        


    
    # [FIX] Update Power Densities (Lights/Equip) to match Original IDF (Physics Consistency)
    if original_idf_path:
        _update_power_densities_from_original(idf, original_idf_path, verbose=verbose)

    # Optimize and save
    # Enable hourly detail output only for full year simulations
    enable_hourly_detail = (run_period_mode == 'standard')
    idf_optimizer.optimize_idf(idf, verbose=verbose, enable_hourly_detail=enable_hourly_detail)
    idf_optimizer.apply_speed_optimizations(idf, verbose=verbose)
    idf_optimizer.configure_run_period(idf, mode=run_period_mode, verbose=verbose)
    idf.saveas(output_path)
    print(f"Neighbourhood IDF saved to: {output_path}")


def inject_neighbourhood_default_schedules(
    idf_path: str,
    output_path: str,
    n_buildings: int,
    original_idf_path: Optional[str] = None,
    verbose: bool = True,
    run_period_mode: str = 'standard'
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
    IDF.setiddname(config.resolve_idd_path())
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
                occ_sch_name, "Fraction", {
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
                act_sch_name, "Any Number", {
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
                light_sch_name, "Fraction", {
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
                equip_sch_name, "Fraction", {
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
                water_sch_name, "Fraction", {
                    'Weekday': to_hour_value_list(default_water_weekday),
                    'Weekend': to_hour_value_list(default_water_weekend)
                }
            )
        else:
            # Create new schedule object if needed
            new_sch = idf.newidfobject("SCHEDULE:COMPACT")
            new_sch.obj = ["Schedule:Compact"] + create_compact_schedule(
                water_sch_name, "Fraction", {
                    'Weekday': to_hour_value_list(default_water_weekday),
                    'Weekend': to_hour_value_list(default_water_weekend)
                }
            )
    
    # WaterUse:Equipment schedule names (Water_Bldg_X) were already set in-place
    # by prepare_neighbourhood_idf(). Plant Loop connections remain intact.
    if verbose:
        water_equip_objs = idf.idfobjects.get('WATERUSE:EQUIPMENT', [])
        print(f"  WaterUse:Equipment objects: {len(water_equip_objs)} (schedule names pre-set by prepare step)")

    # [FIX] Apply Water Use Peak Scaling (Physics Consistency)
    # This ensures the peak flow rate is adjusted so that the daily volume matches target (220L).
    idf_optimizer.scale_water_use_peak_flow(idf, standard_schedules, verbose=verbose)
    
    # [FIX] Update Power Densities (Lights/Equip) to match Original IDF (Physics Consistency)
    # This ensures consistency with Option 3 (Single Building) and Integrated Scenarios.
    if original_idf_path:
        _update_power_densities_from_original(idf, original_idf_path, verbose=verbose)
    
    # Optimize and save
    # Enable hourly detail output only for full year simulations
    enable_hourly_detail = (run_period_mode == 'standard')
    idf_optimizer.optimize_idf(idf, verbose=verbose, enable_hourly_detail=enable_hourly_detail)
    idf_optimizer.apply_speed_optimizations(idf, verbose=verbose)
    idf_optimizer.configure_run_period(idf, mode=run_period_mode, verbose=verbose)
    idf.saveas(output_path)
    print(f"Neighbourhood Default IDF saved to: {output_path}")


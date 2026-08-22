# -*- coding: utf-8 -*-
"""
KBEM Ankara - Urban Building Energy Modeling (UBEM) Pipeline
Extracted and refactored from Grasshopper definition: KBEM_Ankara_220622.gh
Authors of original components: Orcun, Siser, IPG (2021-2022)

This module provides pure Python implementations of all custom algorithmic logic
found in the Ankara UBEM Grasshopper definition.
"""

from typing import List, Tuple, Any, Optional, Dict
from itertools import groupby
import math


# ==============================================================================
# 1. LIST FILTERING, TREE HANDLING & CONDITIONAL UTILITIES
# ==============================================================================

def split_by_boolean(in_list: List[Any], condition_mask: Optional[List[bool]] = None) -> Tuple[List[Any], List[Any]]:
    """
    Splits a list into two lists based on truthiness or an explicit boolean mask.
    (Derived from custom components idx 1211, 1220, 1228, 1253, 1314)
    """
    true_list = []
    false_list = []
    
    if condition_mask is not None:
        for val, mask in zip(in_list, condition_mask):
            if bool(mask):
                true_list.append(val)
            else:
                false_list.append(val)
    else:
        for val in in_list:
            if bool(val):
                true_list.append(val)
            else:
                false_list.append(val)
                
    return true_list, false_list


def extract_true_indices(items: List[Any]) -> List[int]:
    """
    Extracts 0-based indices where values are True or string 'True'.
    (Derived from custom components idx 3803, 5710)
    """
    return [i for i, val in enumerate(items) if val is True or val == 'True' or val == 1]


def filter_by_inclusion_flag(flags: List[int], target_flag: int = 2) -> List[int]:
    """
    Filters indices where the spatial relationship test equals the target flag
    (e.g., 2 = 'Point is inside polygon curve').
    (Derived from custom component idx 3353)
    """
    return [i for i, flag in enumerate(flags) if flag == target_flag]


def count_consecutive_group_lengths(data: List[Any]) -> List[int]:
    """
    Calculates the run lengths of consecutive identical items.
    (Derived from custom components idx 4393, 5604)
    """
    return [sum(1 for _ in group) for _, group in groupby(data)]


# ==============================================================================
# 2. SPATIAL & PARCEL ORIENTATION ALGORITHMS (Phase 1)
# ==============================================================================

def normalize_parcel_angle(angle_deg: float) -> float:
    """
    Normalizes parcel orientation angle for consistent axis alignment.
    (Derived from custom components idx 3669, 3675)
    """
    if angle_deg >= 90.0:
        angle_deg -= 90.0
    if angle_deg == 0.0:
        angle_deg += 0.1  # Prevents degenerate edge alignment in GH vector math
    return angle_deg


def compare_centroids(c1: Tuple[float, float, float], c2: Tuple[float, float, float], tol: float = 1e-4) -> bool:
    """
    Checks if two centroid points match within numerical tolerance.
    (Derived from custom component idx 4955)
    """
    return math.isclose(c1[0], c2[0], abs_tol=tol) and            math.isclose(c1[1], c2[1], abs_tol=tol) and            math.isclose(c1[2], c2[2], abs_tol=tol)


def format_building_identifier(neighborhood_code: str, parcel_num: int, building_num: int) -> str:
    """
    Formats the standard UBEM identifier: {neighborhoodName2digits}_{parcelNumber}_{buildingNumber}
    (Derived from Ankara KBEM naming convention)
    """
    return f"{neighborhood_code}_{parcel_num}_{building_num}"


# ==============================================================================
# 3. UNIT DIVISION & SPATIAL TYPOLOGY MAPPING (Phase 3)
# ==============================================================================

def get_grid_division_counts(units_per_floor: int) -> Tuple[int, int]:
    """
    Determines the (U, V) grid subdivision counts based on the target number of flats per floor.
    (Derived from custom components idx 1938, 4188)
    
    Subdivision Rules:
      - 1 unit/floor  -> 1 x 1
      - 2 units/floor -> 2 x 1
      - 3-4 units/floor -> 2 x 2
      - 5-6 units/floor -> 3 x 2
      - >6 units/floor  -> 4 x 2
    """
    if units_per_floor <= 1:
        return (1, 1)
    elif units_per_floor == 2:
        return (2, 1)
    elif units_per_floor in (3, 4):
        return (2, 2)
    elif units_per_floor in (5, 6):
        return (3, 2)
    else:
        return (4, 2)


def map_unit_square_meters(flats_per_floor: int, gross_floor_area: float) -> float:
    """
    Calculates average area per unit flat.
    """
    if flats_per_floor <= 0:
        return gross_floor_area
    return gross_floor_area / flats_per_floor


# ==============================================================================
# 4. BUILDING ATTRIBUTES, VINTAGE & INFILTRATION MAPPING (Phase 4)
# ==============================================================================

def map_building_occupancy_type(program_name: str) -> str:
    """
    Maps EnergyPlus/OpenStudio space use type to internal category ('res' or 'off').
    (Derived from custom component idx 4340)
    """
    if "MidriseApartment" in program_name or "Apartment" in program_name or "Residential" in program_name:
        return "res"
    return "off"


def map_construction_vintage(year_built: int) -> int:
    """
    Classifies building construction year into representative TABULA / UBEM vintage bins.
    (Derived from custom component idx 4569)
    
    Vintage Bins:
      - Before 1980  -> 1960 Archetype
      - 1980 to 1999 -> 1980 Archetype
      - 2000+        -> 2000 Archetype (Post-TS 825 thermal regulation standard)
    """
    if year_built < 1980:
        return 1960
    elif 1980 <= year_built < 2000:
        return 1980
    else:
        return 2000


def get_infiltration_rate(vintage_year: int) -> float:
    """
    Returns design infiltration rate in m³/s per m² of envelope area.
    (Derived from custom component idx 6595)
    
    Standards:
      - 1960 Archetype -> 0.000500 m³/(s·m²) (~1.80 m³/(h·m²))
      - 1980 Archetype -> 0.000400 m³/(s·m²) (~1.44 m³/(h·m²))
      - 2000 Archetype -> 0.000285 m³/(s·m²) (~1.02 m³/(h·m²))
    """
    vintage = map_construction_vintage(vintage_year)
    if vintage == 1960:
        return 0.000500
    elif vintage == 1980:
        return 0.000400
    else:
        return 0.000285

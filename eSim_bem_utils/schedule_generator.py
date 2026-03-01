"""
Schedule Generator Module for Occupancy-Based BEM Integration.

This module provides classes to transform default schedules based on:
1. LightingGenerator: Uses daylight threshold logic (Gatekeeper).
2. PresenceFilter: Uses min/max toggling based on presence.

References:
    - Occupancy_Integration_Plan.md
    - Default Schedule Standardization.md
"""
import os
import re
from typing import Optional


class StatFileParser:
    """
    Parses EnergyPlus .stat files to extract solar radiation statistics.

    The .stat file contains "Average Hourly Statistics for Global Horizontal
    Solar Radiation [Wh/m²]" which provides monthly hourly averages.
    """

    def __init__(self, stat_path: str) -> None:
        """
        Initialize the parser with a path to a .stat file.

        Args:
            stat_path: Absolute path to the .stat file.
        """
        self.stat_path = stat_path
        self._solar_data: Optional[dict[str, list[float]]] = None

    @staticmethod
    def find_stat_for_epw(epw_path: str) -> Optional[str]:
        """
        Attempts to find the .stat file corresponding to an EPW file.

        Looks in the same directory for a file with the same basename
        but with a .stat extension.

        Args:
            epw_path: Path to the EPW file.

        Returns:
            Path to the .stat file if found, otherwise None.
        """
        if not epw_path:
            return None

        directory = os.path.dirname(epw_path)
        basename = os.path.splitext(os.path.basename(epw_path))[0]
        stat_path = os.path.join(directory, f"{basename}.stat")

        if os.path.exists(stat_path):
            return stat_path
        return None

    def parse_solar_radiation(self) -> dict[str, list[float]]:
        """
        Parses the "Average Hourly Statistics for Global Horizontal Solar
        Radiation" table from the .stat file.

        Returns:
            A dictionary with month names as keys (e.g., 'Jan', 'Feb') and
            lists of 24 hourly average solar radiation values (Wh/m²).
        """
        if self._solar_data is not None:
            return self._solar_data

        self._solar_data = {}
        months = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]

        try:
            with open(self.stat_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Find the table start
            table_marker = "Average Hourly Statistics for Global Horizontal Solar Radiation"
            start_idx = content.find(table_marker)
            if start_idx == -1:
                print(f"  Warning: Solar radiation table not found in {self.stat_path}")
                return self._solar_data

            # Extract lines after the marker
            lines = content[start_idx:].split("\n")

            # Initialize month data
            for month in months:
                self._solar_data[month] = [0.0] * 24

            # Parse data rows (format: "0:01- 1:00    val1  val2  ... val12")
            for line in lines[2:26]:  # Skip header lines, 24 data rows
                line = line.strip()
                if not line or ":" not in line[:10]:
                    continue

                # Extract hour range and values
                parts = line.split()
                if len(parts) < 13:
                    continue

                # Parse hour (e.g., "0:01- 1:00" -> hour 0)
                hour_match = re.match(r"(\d+):.*-\s*(\d+):", parts[0] + parts[1])
                if hour_match:
                    hour = int(hour_match.group(1))
                else:
                    continue

                # Parse 12 month values
                values = parts[2:14] if len(parts) >= 14 else parts[2:]
                for i, val_str in enumerate(values):
                    if i < len(months):
                        try:
                            self._solar_data[months[i]][hour] = float(val_str)
                        except ValueError:
                            pass

        except Exception as e:
            print(f"  Warning: Error parsing .stat file: {e}")

        return self._solar_data


class LightingGenerator:
    """
    Generates lighting schedules using the Daylight Threshold Method.

    Logic: IF (Household is Active) AND (Solar Radiation < Threshold)
           THEN Lighting Load = default_schedule[hour] (preserve gradual changes)
           ELSE Lighting Load = 0.0
    """

    DEFAULT_THRESHOLD = 150.0  # Wh/m² (Global Horizontal)

    def __init__(
        self,
        epw_path: Optional[str] = None,
        threshold: float = DEFAULT_THRESHOLD
    ) -> None:
        """
        Initialize the Lighting Generator.

        Args:
            epw_path: Path to the EPW file (used to find the .stat file).
            threshold: Solar radiation threshold in Wh/m² below which
                       artificial lighting is needed.
        """
        self.threshold = threshold
        self.solar_data: dict[str, list[float]] = {}

        stat_path = StatFileParser.find_stat_for_epw(epw_path) if epw_path else None
        if stat_path:
            parser = StatFileParser(stat_path)
            self.solar_data = parser.parse_solar_radiation()
            if self.solar_data:
                print(f"  LightingGenerator: Loaded solar data from {os.path.basename(stat_path)}")
        else:
            print("  LightingGenerator: No .stat file found, using conservative fallback.")

    def _get_annual_average_solar(self) -> list[float]:
        """
        Calculates the annual average solar radiation for each hour.

        Returns:
            A list of 24 hourly average values across all months.
        """
        if not self.solar_data:
            # Fallback: Assume daylight from 7AM to 7PM (hours 7-18)
            return [0.0 if h < 7 or h > 18 else 200.0 for h in range(24)]

        hourly_avg = []
        for hour in range(24):
            values = [self.solar_data[m][hour] for m in self.solar_data if hour < len(self.solar_data[m])]
            hourly_avg.append(sum(values) / len(values) if values else 0.0)
        return hourly_avg

    def generate(
        self,
        presence_schedule: list[float],
        default_schedule: Optional[list[float]] = None,
        day_type: str = "Weekday"
    ) -> list[float]:
        """
        Generate a lighting schedule for a single day (non-seasonal).

        Logic: Same as Equipment/DHW PresenceFilter:
        - Present: use default schedule value (gradual changes)
        - Absent: use base_load (minimum from absent hours)

        Note: This non-seasonal version is kept for backward compatibility.
        For seasonal variation, use generate_monthly().

        Args:
            presence_schedule: A list of 24 fractional occupancy values (0-1).
            default_schedule: A list of 24 default lighting values. If provided,
                              uses these values when present (preserves
                              gradual changes). If None, uses 1.0.
            day_type: 'Weekday' or 'Weekend' (for future use).

        Returns:
            A list of 24 lighting schedule values.
        """
        # Calculate base_load from absent hours (like PresenceFilter)
        if default_schedule and presence_schedule:
            absent_hours = [h for h in range(24) if h < len(presence_schedule) and presence_schedule[h] == 0.0]
            if absent_hours:
                absent_values = [default_schedule[h] for h in absent_hours if h < len(default_schedule)]
                base_load = min(absent_values) if absent_values else 0.0
            else:
                # No absent hours, use typical away hours (9-17)
                away_hours = list(range(9, 17))
                away_values = [default_schedule[h] for h in away_hours if h < len(default_schedule)]
                base_load = min(away_values) if away_values else 0.0
        else:
            base_load = 0.0

        result = []

        for hour in range(24):
            presence = presence_schedule[hour] if hour < len(presence_schedule) else 0.0

            if presence > 0.0:
                # Present: use default schedule value (gradual changes)
                if default_schedule and hour < len(default_schedule):
                    result.append(default_schedule[hour])
                else:
                    result.append(1.0)
            else:
                # Absent: use base_load (like Equipment/DHW)
                result.append(base_load)

        return result

    def get_monthly_daylight_factor(self, month: str) -> list[float]:
        """
        Calculate hourly daylight reduction factors for a given month.

        For each hour, computes how much artificial lighting can be
        reduced based on available solar radiation. Higher solar radiation
        means less artificial lighting is needed.

        Args:
            month: Three-letter month abbreviation (e.g., 'Jan', 'Jul').

        Returns:
            A list of 24 factors (0.0 to 1.0) where:
            - 1.0 = full artificial lighting needed (nighttime/low solar)
            - lower values = solar displaces some artificial lighting
        """
        if not self.solar_data or month not in self.solar_data:
            return [1.0] * 24

        monthly_solar = self.solar_data[month]

        # Find peak solar radiation across all months for normalization
        peak_solar = 0.0
        for m in self.solar_data:
            for val in self.solar_data[m]:
                if val > peak_solar:
                    peak_solar = val

        if peak_solar == 0.0:
            return [1.0] * 24

        factors = []
        for hour in range(24):
            solar = monthly_solar[hour] if hour < len(monthly_solar) else 0.0

            if solar <= self.threshold:
                # Below threshold: full artificial lighting needed
                factors.append(1.0)
            else:
                # Above threshold: reduce lighting proportional to solar
                # Scale: threshold → 1.0, peak → minimum factor (0.3)
                min_factor = 0.3  # Never reduce below 30% (some rooms have no windows)
                normalized = (solar - self.threshold) / (peak_solar - self.threshold)
                factor = 1.0 - normalized * (1.0 - min_factor)
                factors.append(max(min_factor, min(1.0, factor)))

        return factors

    def generate_monthly(
        self,
        presence_schedule: list[float],
        default_schedule: Optional[list[float]] = None,
        month: str = "Jan",
        day_type: str = "Weekday"
    ) -> list[float]:
        """
        Generate a lighting schedule with monthly daylight variation.

        Combines presence filtering with monthly solar radiation data
        to produce seasonal lighting demand. During daylight hours with
        high solar radiation, artificial lighting demand is reduced.

        Args:
            presence_schedule: A list of 24 fractional occupancy values.
            default_schedule: A list of 24 default lighting values.
            month: Three-letter month abbreviation (e.g., 'Jan', 'Jul').
            day_type: 'Weekday' or 'Weekend'.

        Returns:
            A list of 24 lighting schedule values with seasonal scaling.
        """
        # Start with the base presence-filtered schedule
        base_schedule = self.generate(
            presence_schedule, default_schedule, day_type
        )

        # Apply monthly daylight factors
        daylight_factors = self.get_monthly_daylight_factor(month)

        result = []
        for hour in range(24):
            result.append(base_schedule[hour] * daylight_factors[hour])

        return result


class PresenceFilter:
    """
    Filters default schedules using the Presence Filter Method.

    Logic: IF (Household is Active/Home)
           THEN Load = default_schedule[hour] (preserve gradual changes)
           ELSE Load = Base Load (value from default schedule during typical absent hours)
    """

    # Typical work hours when occupants are away (9 AM to 5 PM)
    TYPICAL_AWAY_HOURS = list(range(9, 17))

    def __init__(
        self,
        default_schedule: list[float],
        presence_schedule: Optional[list[float]] = None
    ) -> None:
        """
        Initialize the Presence Filter.

        Args:
            default_schedule: A list of 24 hourly values from the
                              standardized default schedule.
            presence_schedule: Optional presence schedule. If provided, base_load
                               is calculated as the minimum of default_schedule
                               during hours when presence is 0. If not provided,
                               uses typical away hours (9AM-5PM).
        """
        self.default_schedule = default_schedule
        self.active_load = max(default_schedule) if default_schedule else 1.0

        threshold = 1e-3
        # Calculate base_load from absent hours
        if presence_schedule and default_schedule:
            # Find hours where presence is near 0 (absent)
            absent_hours = [h for h in range(24) if h < len(presence_schedule) and presence_schedule[h] < threshold]
            if absent_hours:
                # Use minimum of default schedule during absent hours
                absent_values = [default_schedule[h] for h in absent_hours if h < len(default_schedule)]
                self.base_load = min(absent_values) if absent_values else 0.0
            else:
                # No absent hours, use typical away hours
                away_values = [default_schedule[h] for h in self.TYPICAL_AWAY_HOURS if h < len(default_schedule)]
                self.base_load = min(away_values) if away_values else min(default_schedule)
        elif default_schedule:
            # No presence schedule provided, use typical away hours
            away_values = [default_schedule[h] for h in self.TYPICAL_AWAY_HOURS if h < len(default_schedule)]
            self.base_load = min(away_values) if away_values else min(default_schedule)
        else:
            self.base_load = 0.0

    def apply(self, presence_schedule: list[float]) -> list[float]:
        """
        Apply the presence filter to generate a modified schedule.

        Args:
            presence_schedule: A list of 24 fractional occupancy values (0-1).

        Returns:
            A list of 24 schedule values: default values when present,
            base load (minimum from absent hours) when absent.
        """
        result = []
        threshold = 1e-3
        for hour in range(24):
            presence = presence_schedule[hour] if hour < len(presence_schedule) else 0.0
            default_val = self.default_schedule[hour] if hour < len(self.default_schedule) else self.base_load

            if presence > threshold:
                # When present: use the exact default schedule value (gradual changes)
                result.append(default_val)
            else:
                # When absent: use base load (minimum from absent hours)
                result.append(self.base_load)

        return result


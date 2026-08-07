import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eSim_bem_utils import integration

# Standard-schedule stub: typical away hours (9-16) set to 0.15 so that
# PresenceFilter computes base_load = 0.15 for a fully-absent household.
_STD_AWAY = 0.15
_STD_PEAK = 0.80
_STD_SCH  = [_STD_AWAY] * 9 + [_STD_AWAY] * 8 + [_STD_PEAK] * 7  # [0-8]=away, [9-16]=away, [17-23]=peak

_MOCK_STANDARD_SCHEDULES = {
    'occupancy':  {'Weekday': [1.0] * 24, 'Weekend': [1.0] * 24},
    'lighting':   {'Weekday': _STD_SCH[:],  'Weekend': _STD_SCH[:]},
    'equipment':  {'Weekday': _STD_SCH[:],  'Weekend': _STD_SCH[:]},
    'dhw':        {'Weekday': _STD_SCH[:],  'Weekend': _STD_SCH[:]},
    'activity':   {'Weekday': [120.0] * 24, 'Weekend': [120.0] * 24},
}


class TestIntegrationLogic(unittest.TestCase):

    def test_baseload_logic_single_home(self):
        """
        Equipment schedule uses PresenceFilter: absent hours → base_load.

        With standard schedule having away-hour values of 0.15 and presence=0.0
        for all hours, PresenceFilter.base_load = 0.15 and every schedule value
        should be 0.15.  Critically, no value should be 0.0 (which would indicate
        the binary gate was incorrectly zeroing absent hours instead of applying
        base_load) and no value should equal the peak (0.80) either.
        """

        mock_idf = MagicMock()
        mock_idf.idfobjects = {
            'PEOPLE':            [MagicMock()],
            'LIGHTS':            [MagicMock(Schedule_Name='Lights_Sch')],
            'ELECTRICEQUIPMENT': [MagicMock(Schedule_Name='Equip_Sch')],
            'GASEQUIPMENT':      [MagicMock(Schedule_Name='Gas_Sch')],
            'WATERUSE:EQUIPMENT': [
                MagicMock(Flow_Rate_Fraction_Schedule_Name='Water_Sch')
            ],
        }

        schedule_data = {
            'metadata': {'hhsize': 2},
            'Weekday': [{'hour': i, 'occ': 0.0, 'met': 120.0} for i in range(24)],
            'Weekend': [{'hour': i, 'occ': 0.0, 'met': 120.0} for i in range(24)],
        }

        created_schedules = []

        def side_effect_newidf(obj_type):
            obj = MagicMock()
            created_schedules.append(obj)
            return obj

        mock_idf.newidfobject.side_effect = side_effect_newidf

        # Build a mock idf_optimizer that returns proper standard schedules so
        # PresenceFilter receives a real list instead of a MagicMock.
        mock_idf_opt = MagicMock()
        mock_idf_opt.load_standard_residential_schedules.return_value = _MOCK_STANDARD_SCHEDULES
        mock_idf_opt.scale_water_use_peak_flow.return_value = []

        with patch('eSim_bem_utils.integration.validate_idf_compatibility'), \
             patch('eSim_bem_utils.integration.idf_optimizer', mock_idf_opt), \
             patch('eSim_bem_utils.integration.IDF', return_value=mock_idf):
            integration.inject_schedules(
                "dummy.idf", "output.idf", "test_hh", schedule_data
            )

        # Find the projected Equipment and Lights schedules
        equip_sch_obj  = None
        lights_sch_obj = None

        for obj in created_schedules:
            if hasattr(obj, 'obj') and len(obj.obj) > 1:
                name = str(obj.obj[1])
                if 'Proj_ELEC' in name:
                    equip_sch_obj  = obj
                elif 'Proj_LIGH' in name:
                    lights_sch_obj = obj

        self.assertIsNotNone(equip_sch_obj,  "Projected ELECTRICEQUIPMENT schedule not created")

        # Parse float values from the Compact schedule object list
        def parse_vals(sch_obj):
            vals = []
            for item in sch_obj.obj:
                try:
                    vals.append(float(item))
                except (ValueError, TypeError):
                    pass
            return vals

        equip_vals = parse_vals(equip_sch_obj)

        # Absent household → all hours should equal base_load (= 0.15).
        # No value should be 0.0 (binary-gate zero) or 0.80 (full peak).
        self.assertTrue(
            equip_vals,
            "Equipment schedule has no numeric values"
        )
        self.assertTrue(
            all(abs(v - _STD_AWAY) < 1e-6 for v in equip_vals),
            f"Expected all Equipment values = {_STD_AWAY} (base_load). Got: {equip_vals}"
        )
        self.assertFalse(
            any(v == 0.0 for v in equip_vals),
            f"Equipment should NOT have 0.0 (absent hours must get base_load). Got: {equip_vals}"
        )

        print("PASS: Absent household → Equipment schedule = base_load throughout")


if __name__ == '__main__':
    unittest.main()

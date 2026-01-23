import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bem_utils import integration

class TestIntegrationLogic(unittest.TestCase):
    
    def test_baseload_logic_single_home(self):
        """Test that Equipment gets 0.15 baseload when absent in inject_schedules logic."""
        
        # Mock IDF object
        mock_idf = MagicMock()
        mock_idf.idfobjects = {
            'PEOPLE': [MagicMock()],
            'LIGHTS': [MagicMock(Schedule_Name='Lights_Sch')],
            'ELECTRICEQUIPMENT': [MagicMock(Schedule_Name='Equip_Sch')],
            'GASEQUIPMENT': [MagicMock(Schedule_Name='Gas_Sch')],
            'WATERUSE:EQUIPMENT': [MagicMock(Flow_Rate_Fraction_Schedule_Name='Water_Sch')]
        }
        
        # Mock parse_schedule_values to return a constant 1.0 schedule
        # This simulates a "Always On" default schedule
        with patch('bem_utils.integration.parse_schedule_values') as mock_parse:
            mock_parse.return_value = {
                'Weekday': [1.0] * 24,
                'Weekend': [1.0] * 24
            }
            
            # Create a mock schedule data where occupancy is 0.0 (Absent) for all hours
            # This should trigger the baseload logic
            schedule_data = {
                'metadata': {'hhsize': 2},
                'Weekday': [{'hour': i, 'occ': 0.0, 'met': 120.0} for i in range(24)],
                'Weekend': [{'hour': i, 'occ': 0.0, 'met': 120.0} for i in range(24)]
            }
            
            # We need to spy on 'newidfobject' to check what schedules are created
            created_schedules = []
            def side_effect_newidf(obj_type):
                obj = MagicMock()
                created_schedules.append(obj)
                return obj
            mock_idf.newidfobject.side_effect = side_effect_newidf
            
            # Run the function
            # Note: We need to mock idf_optimizer and idf.saveas to avoid errors
            with patch('bem_utils.integration.idf_optimizer'), patch.object(integration, 'IDF'):
                 # We are passing our mock_idf directly, but the function re-instantiates IDF(idf_path)
                 # So we need to patch IDF class to return our mock_idf
                 with patch('bem_utils.integration.IDF', return_value=mock_idf):
                    integration.inject_schedules("dummy.idf", "output.idf", "test_hh", schedule_data)

            # Analyze created schedules
            # We expect projected schedules for Lights, Equip, Gas, Water
            
            # Find the Equipment schedule
            equip_sch_obj = None
            lights_sch_obj = None
            
            for obj in created_schedules:
                # obj.obj is the list of fields. e.g. ["Schedule:Compact", Name, Type, ...]
                # field[1] is Name
                if hasattr(obj, 'obj') and len(obj.obj) > 1:
                    name = obj.obj[1]
                    if "Proj_ELEC" in name: # Proj_ELECTRICEQUIPMENT...
                        equip_sch_obj = obj
                    elif "Proj_LIGH" in name:
                        lights_sch_obj = obj
            
            self.assertIsNotNone(equip_sch_obj, "Projected Electric Equipment schedule not found")
            self.assertIsNotNone(lights_sch_obj, "Projected Lights schedule not found")
            
            # Check values in Equipment Schedule
            # Since occupancy is 0.0 (Absent), Equipment should be 0.15 (Baseload)
            # The schedule format is Schedule:Compact.
            # We need to parse the fields to find the values.
            # Fields: Name, Type, Field1, ... "Until: HH:MM", "Value", ...
            equip_vals = []
            for item in equip_sch_obj.obj:
                try:
                     val = float(item)
                     equip_vals.append(val)
                except (ValueError, TypeError):
                    pass
            
            # Verify we have 0.15 in the values
            self.assertTrue(any(v == 0.15 for v in equip_vals), f"Equipment values should contain 0.15. Found: {equip_vals}")
            self.assertFalse(any(v == 0.0 for v in equip_vals), f"Equipment values should NOT contain 0.0. Found: {equip_vals}")
            
            # Check values in Lights Schedule
            # Since occupancy is 0.0, Lights should be 0.0
            lights_vals = []
            for item in lights_sch_obj.obj:
                try:
                     val = float(item)
                     lights_vals.append(val)
                except (ValueError, TypeError):
                    pass
            
            self.assertTrue(any(v == 0.0 for v in lights_vals), f"Lights values should contain 0.0. Found: {lights_vals}")
            self.assertFalse(any(v == 0.15 for v in lights_vals), f"Lights values should NOT contain 0.15. Found: {lights_vals}")

            print("Test passed: Equipment set to 0.15 baseload when absent, Lights set to 0.0")

if __name__ == '__main__':
    unittest.main()

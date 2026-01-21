import sys
import os
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bem_utils import main as main_module

def test_option_5():
    """Test Option 5 with the schedule injection fix."""
    print("=== AUTOMATED TEST FOR OPTION 5 (Schedule Fix Validation) ===")
    print("Target: NUs_RC1.idf (24 buildings) | Weather: Toronto (Ontario)")
    print("Testing: default_schedule × presence_mask formula\n")
    
    # Inputs for Option 5:
    # 1. IDF selection: 1 (NUs_RC1.idf - first in sorted list)
    # 2. Weather selection: 1 (Toronto - first in sorted list)
    # 3. Confirm: y
    inputs = iter(['1', '1', 'y'])

    def mock_input(prompt=""):
        print(f"[AUTO] Prompt: {prompt.strip()}")
        try:
            val = next(inputs)
            print(f"[AUTO] Entering: {val}")
            return val
        except StopIteration:
            print("[AUTO] Input exhausted, returning 'n'")
            return 'n'

    with patch('builtins.input', side_effect=mock_input):
        try:
            main_module.option_comparative_neighbourhood_simulation()
        except StopIteration:
            pass
        except Exception as e:
            print(f"Test Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_option_5()

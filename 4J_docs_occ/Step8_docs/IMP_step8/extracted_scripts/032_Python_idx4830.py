\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 4830
Instance GUID: 7b1d4983-6e00-402c-adc4-712a4d2b5ade
Description: Provides a scripting component.

Inputs:
  - x
  - y

Outputs:
  - out
  - BuildingwithExtraUnit
  - BuildingwithoutExtraUnit
\"\"\"
"""Provides a scripting component.
    Inputs:
        x: The x script variable
        y: The y script variable
    Output:
        a: The a output variable"""

__author__ = "Siser"
__version__ = "2022.03.04"

import rhinoscriptsyntax as rs
if x == True:
    BuildingwithoutExtraUnit = y
else:
    BuildingwithExtraUnit = y
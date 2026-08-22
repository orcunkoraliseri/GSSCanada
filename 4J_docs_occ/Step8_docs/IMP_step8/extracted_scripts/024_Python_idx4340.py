\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 4340
Instance GUID: d7a4dd6b-740a-424c-aa6f-94cc572b2b0b
Description: Provides a scripting component.

Inputs:
  - x

Outputs:
  - out
  - a
\"\"\"
"""Provides a scripting component.
    Inputs:
        x: The x script variable
        y: The y script variable
    Output:
        a: The a output variable"""

__author__ = "Siser"
__version__ = "2022.03.07"

import rhinoscriptsyntax as rs
if x == 'MidriseApartment::Apartment':
    a = 'res'
else:
    a = 'off'
\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 4393
Instance GUID: fd79773e-37a4-4397-9008-cea4b206a632
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
__version__ = "2022.03.08"

import rhinoscriptsyntax as rs
from itertools import groupby
a = [sum(1 for _ in group) for _, group in groupby(x)]
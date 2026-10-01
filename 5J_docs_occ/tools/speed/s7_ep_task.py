# -*- coding: utf-8 -*-
"""Array task of the Step 7 EnergyPlus pilot: the campaign's own camp_task.py (unchanged), with the twin rows added to the building table.
usage: s7_ep_task.py <climate_id> <block>   ; environment CAMP_ROOT=district/ep/ CAMP_PLAN=district/ep/plan_pilot/ CAMP_HH=district/hh/pool/"""
import os, sys
import s7_common as s7
assert os.environ.get("CAMP_ROOT", "").startswith(s7.D), "CAMP_ROOT must be under district/"
cc = s7.install_twins()
import camp_task
camp_task.main()

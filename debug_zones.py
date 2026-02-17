#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug zone mapping for test pincodes"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.bigship_calculator import Bigship
from forms.calculator.freight_calculator import QuoteInput, ShipmentItem, Settings
from forms.calculator.data_loader import PincodeDB, PincodeRecord

# Create a test pincode database with manual overrides
class TestPincodeDB(PincodeDB):
    PINCODE_STATE_MAP = {
        "600095": "Tamil Nadu",
        "621220": "Tamil Nadu",
        "560060": "Karnataka",
        "676101": "Kerala",
        "695020": "Kerala",
        "524413": "Andhra Pradesh",
        "411045": "Maharashtra",
        "152116": "Punjab",
        "636111": "Tamil Nadu",
        "132039": "Haryana",
        "571134": "Karnataka",
        "201306": "Uttar Pradesh",
        "212635": "Uttar Pradesh",
        "140301": "West Bengal",
        "623536": "Tamil Nadu",
        "686664": "Kerala",
    }
    
    def __init__(self):
        super().__init__()
        self._test_records = {}
        for pincode, state in self.PINCODE_STATE_MAP.items():
            rec = PincodeRecord(pincode=pincode, state=state, city="")
            self._test_records[pincode] = rec
    
    def get(self, pincode):
        """Override to return test records"""
        if str(pincode) in self._test_records:
            return self._test_records[str(pincode)]
        return super().get(pincode)
    
    def __getitem__(self, pincode):
        return self.get(pincode)

# Initialize
settings = Settings()
calc = Bigship(settings=settings)
test_db = TestPincodeDB()

# Test case 1: CFT 103kg from 560060 (Karnataka) to 676101 (Kerala)
print("=" * 80)
print("TEST CASE 1: CFT 103kg Karnataka (560060) to Kerala (676101)")
print("=" * 80)

# Get zones
from_state = "Karnataka"
to_state = "Kerala"

from_zone_cft = calc.get_zone_from_state(from_state, "CFT")
to_zone_cft = calc.get_zone_from_state(to_state, "CFT")

print(f"From State: {from_state} -> Zone: {from_zone_cft}")
print(f"To State: {to_state} -> Zone: {to_zone_cft}")

# Check rate matrix
if from_zone_cft in calc.CFT_RATES_MATRIX:
    if to_zone_cft in calc.CFT_RATES_MATRIX[from_zone_cft]:
        rate = calc.CFT_RATES_MATRIX[from_zone_cft][to_zone_cft]
        print(f"Rate from {from_zone_cft} -> {to_zone_cft}: Rs {rate}/kg")
        base_freight = 103.01 * rate
        print(f"Base freight (103.01 * {rate}): Rs {base_freight:.2f}")
    else:
        print(f"ERROR: To zone {to_zone_cft} not in rate matrix for {from_zone_cft}")
else:
    print(f"ERROR: From zone {from_zone_cft} not in rate matrix")

# Now test actual calculation
inp = QuoteInput(
    from_pincode="560060",
    to_pincode="676101",
    items=[ShipmentItem(weight_kg=103.01, length_cm=50, breadth_cm=50, height_cm=50)],
)
inp.bigship_service_type = "CFT"

result = calc.calculate_quote(inp, test_db)
print(f"\nCalculated Total (with GST): Rs {result.total_after_gst:.2f}")
print(f"Base Freight: Rs {result.base_freight:.2f}")
print(f"Surcharges: {result.surcharges}")
print(f"Is ODA (by calculator): {result.rate_details.get('is_oda')}")
print(f"Destination State: {result.rate_details.get('destination_state')}")
print(f"Expected: Rs 1786.40")
print(f"Match: {abs(result.total_after_gst - 1786.40) / 1786.40 * 100:.1f}% difference")

# Test case 2: LTL 111kg from 411045 (Maharashtra) to 636111 (Tamil Nadu)
print("\n" + "=" * 80)
print("TEST CASE 2: LTL 111kg Maharashtra (411045) to Tamil Nadu (636111)")
print("=" * 80)

from_state = "Maharashtra"
to_state = "Tamil Nadu"

from_zone_ltl = calc.get_zone_from_state(from_state, "LTL")
to_zone_ltl = calc.get_zone_from_state(to_state, "LTL")

print(f"From State: {from_state} -> Zone: {from_zone_ltl}")
print(f"To State: {to_state} -> Zone: {to_zone_ltl}")

if from_zone_ltl in calc.LTL_RATES_MATRIX:
    if to_zone_ltl in calc.LTL_RATES_MATRIX[from_zone_ltl]:
        rate = calc.LTL_RATES_MATRIX[from_zone_ltl][to_zone_ltl]
        print(f"Rate from {from_zone_ltl} -> {to_zone_ltl}: Rs {rate}/kg")
        base_freight = 111 * rate
        print(f"Base freight (111 * {rate}): Rs {base_freight:.2f}")
    else:
        print(f"ERROR: To zone {to_zone_ltl} not in rate matrix for {from_zone_ltl}")
else:
    print(f"ERROR: From zone {from_zone_ltl} not in rate matrix")

inp = QuoteInput(
    from_pincode="411045",
    to_pincode="636111",
    items=[ShipmentItem(weight_kg=111, length_cm=50, breadth_cm=50, height_cm=50)],
)
inp.bigship_service_type = "LTL"

result = calc.calculate_quote(inp, test_db)
print(f"\nCalculated Total (with GST): Rs {result.total_after_gst:.2f}")
print(f"Base Freight: Rs {result.base_freight:.2f}")
print(f"Surcharges: {result.surcharges}")
print(f"Expected: Rs 1729.16")
print(f"Match: {abs(result.total_after_gst - 1729.16) / 1729.16 * 100:.1f}% difference")

# Test case 3: MPS 25kg from 600095 (TN) to 621220 (TN)
print("\n" + "=" * 80)
print("TEST CASE 3: MPS 25kg Tamil Nadu (600095) to Tamil Nadu (621220)")
print("=" * 80)

from_state = "Tamil Nadu"
to_state = "Tamil Nadu"

from_zone_mps = calc.get_zone_from_state(from_state, "MPS")
to_zone_mps = calc.get_zone_from_state(to_state, "MPS")

print(f"From State: {from_state} -> Zone: {from_zone_mps}")
print(f"To State: {to_state} -> Zone: {to_zone_mps}")

if from_zone_mps in calc.MPS_RATES_MATRIX:
    if to_zone_mps in calc.MPS_RATES_MATRIX[from_zone_mps]:
        zone_rates = calc.MPS_RATES_MATRIX[from_zone_mps][to_zone_mps]
        print(f"MPS Rate structure {from_zone_mps} -> {to_zone_mps}: {zone_rates}")
        # 25kg = 10kg base + 15 additional
        base_freight = zone_rates["10kg"] + (25 - 10) * zone_rates["add_1kg"]
        print(f"Base freight: {zone_rates['10kg']} + (15 * {zone_rates['add_1kg']}) = Rs {base_freight:.2f}")
    else:
        print(f"ERROR: To zone {to_zone_mps} not in rate matrix for {from_zone_mps}")
else:
    print(f"ERROR: From zone {from_zone_mps} not in rate matrix")

inp = QuoteInput(
    from_pincode="600095",
    to_pincode="621220",
    items=[ShipmentItem(weight_kg=25, length_cm=50, breadth_cm=50, height_cm=50)],
)
inp.bigship_service_type = "MPS"

result = calc.calculate_quote(inp, test_db)
print(f"\nCalculated Total (with GST): Rs {result.total_after_gst:.2f}")
print(f"Base Freight: Rs {result.base_freight:.2f}")
print(f"Surcharges: {result.surcharges}")
print(f"Expected: Rs 611.29")
print(f"Match: {abs(result.total_after_gst - 611.29) / 611.29 * 100:.1f}% difference")

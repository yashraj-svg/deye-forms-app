#!/usr/bin/env python3
"""Debug specific non-ODA calculations"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.bigship_calculator import Bigship
from forms.calculator.freight_calculator import QuoteInput, ShipmentItem, Settings
from forms.calculator.data_loader import PincodeDB, PincodeRecord

class TestPincodeDB(PincodeDB):
    PINCODE_STATE_MAP = {
        "600095": "Tamil Nadu", "621220": "Tamil Nadu",
        "560060": "Karnataka", "524413": "Andhra Pradesh",
        "411045": "Maharashtra", "636111": "Tamil Nadu",
        "201306": "Uttar Pradesh", "212635": "Uttar Pradesh",
        "201306": "Uttar Pradesh", "140301": "West Bengal",
    }
    
    def __init__(self):
        super().__init__()
        self._test_records = {}
        for pincode, state in self.PINCODE_STATE_MAP.items():
            rec = PincodeRecord(pincode=pincode)
            rec.state = state
            rec.city = ""
            self._test_records[pincode] = rec
    
    def get(self, pincode):
        if str(pincode) in self._test_records:
            return self._test_records[str(pincode)]
        return super().get(pincode)

settings = Settings()
calc = Bigship(settings=settings)
test_db = TestPincodeDB()

# Test Case 1: MPS 15kg Karnataka -> Andhra Pradesh
print("=" * 90)
print("CASE 1: MPS 15kg Karnataka (560060) -> Andhra Pradesh (524413)")
print("Expected: Rs 441.77")
print("=" * 90)

from_state = "Karnataka"
to_state = "Andhra Pradesh"

from_zone = calc.get_zone_from_state(from_state, "MPS")
to_zone = calc.get_zone_from_state(to_state, "MPS")

print(f"From: {from_state} -> Zone: {from_zone}")
print(f"To: {to_state} -> Zone: {to_zone}")

if from_zone in calc.MPS_RATES_MATRIX and to_zone in calc.MPS_RATES_MATRIX[from_zone]:
    rates = calc.MPS_RATES_MATRIX[from_zone][to_zone]
    print(f"MPS Rate structure {from_zone}->{to_zone}: {rates}")
    base = rates["10kg"] + max(0, (15 - 10)) * rates["add_1kg"]
    print(f"Base (15kg) = {rates['10kg']} + 5 * {rates['add_1kg']} = Rs {base}")
    print(f"Min Base = max({base}, 350) = Rs {max(base, 350)}")

inp = QuoteInput(
    from_pincode="560060",
    to_pincode="524413",
    items=[ShipmentItem(weight_kg=14.98, length_cm=30, breadth_cm=30, height_cm=30)],
)
inp.bigship_service_type = "MPS"

result = calc.calculate_quote(inp, test_db)
print(f"\nCalculated:")
print(f"  Base Freight: Rs {result.base_freight:.2f}")
print(f"  Surcharges: {result.surcharges}")
print(f"  Total: Rs {result.total_after_gst:.2f}")
print(f"  Expected: Rs 441.77")
print(f"  Difference: Rs {result.total_after_gst - 441.77:.2f}")

print("\n" + "=" * 90)
print("CASE 2: LTL 111kg Maharashtra (411045) -> Tamil Nadu (636111)")
print("Expected: Rs 1729.16")
print("=" * 90)

from_state = "Maharashtra"
to_state = "Tamil Nadu"

from_zone = calc.get_zone_from_state(from_state, "LTL")
to_zone = calc.get_zone_from_state(to_state, "LTL")

print(f"From: {from_state} -> Zone: {from_zone}")
print(f"To: {to_state} -> Zone: {to_zone}")

if from_zone in calc.LTL_RATES_MATRIX and to_zone in calc.LTL_RATES_MATRIX[from_zone]:
    rate = calc.LTL_RATES_MATRIX[from_zone][to_zone]
    print(f"LTL Rate {from_zone}->{to_zone}: Rs {rate}/kg")
    base = 111 * rate
    print(f"Base (111kg) = 111 * {rate} = Rs {base:.2f}")
    print(f"Min Base = max({base:.2f}, 350) = Rs {max(base, 350):.2f}")

inp = QuoteInput(
    from_pincode="411045",
    to_pincode="636111",
    items=[ShipmentItem(weight_kg=111, length_cm=50, breadth_cm=50, height_cm=50)],
)
inp.bigship_service_type = "LTL"

result = calc.calculate_quote(inp, test_db)
print(f"\nCalculated:")
print(f"  Base Freight: Rs {result.base_freight:.2f}")
print(f"  Surcharges: {result.surcharges}")
print(f"  Total: Rs {result.total_after_gst:.2f}")
print(f"  Expected: Rs 1729.16")
print(f"  Difference: Rs {result.total_after_gst - 1729.16:.2f}")

# Reverse engineering: What should the LR be if calc is correct?
print("\n" + "=" * 90)
print("REVERSE ENGINEERING:")
print("If our calculation is correct and actual bill is Rs 1729.16...")
print("=" * 90)
# Total = Base + LR + Owner Risk + Pickup (if >20kg)
# 1729.16 = Base + 80 + 33 + Pickup
# We need to figure out what the base should be
expected_total = 1729.16
lr = 80
owner_risk = 33
pickup = max(111 * 1, 75)  # Rs 111 since 111 * 1 = 111 > 75

back_calc_base = expected_total - lr - owner_risk - pickup
print(f"If LR={lr}, Owner Risk={owner_risk}, Pickup={pickup}:")
print(f"Back-calculated Base = {expected_total} - {lr} - {owner_risk} - {pickup} = Rs {back_calc_base:.2f}")
print(f"Rate per kg = {back_calc_base:.2f} / 111 = Rs {back_calc_base/111:.2f}/kg")

# What rate do we currently have?
print(f"\nCurrent rate matrix has: Rs {rate}/kg")
print(f"Difference: Rs {(back_calc_base/111) - rate:.2f}/kg")

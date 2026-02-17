#!/usr/bin/env python
"""
Test script to verify the zone mapping fix for Kerala
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
sys.path.insert(0, '/root/app')

import pathlib
base_dir = str(pathlib.Path(__file__).resolve().parent)
sys.path.insert(0, base_dir)

django.setup()

from forms.calculator import get_all_partner_quotes, QuoteInput, ShipmentItem

print("=" * 80)
print("VERIFYING KERALA ZONE MAPPING FIX")
print("=" * 80)

# Test case: 560060 (Karnataka - S1) → 688529 (Kerala - should now be S2)
test_case = QuoteInput(
    from_pincode="560060",
    to_pincode="688529",
    items=[
        ShipmentItem(
            weight_kg=73.0,
            length_cm=1.0,
            breadth_cm=1.0,
            height_cm=1.0,
        ),
    ],
    reverse_pickup=False,
    insured_value=0.0,
    days_in_transit_storage=0,
    gst_mode='12pct',
    bigship_service_type='CFT',
)

print(f"\nTest: 560060 (Karnataka/S1) → 688529 (Kerala/S2)")
print(f"Weight: 73kg | Service: CFT")
print(f"\nExpected rate: S1 → S2 = ₹10.84/kg")
print(f"Expected base freight: 73 × 10.84 = ₹791.32")

results = get_all_partner_quotes(test_case)

bigship_result = next((r for r in results if r.partner_name == "Bigship"), None)
if bigship_result:
    print("\n" + "=" * 80)
    print("BIGSHIP RESULT")
    print("=" * 80)
    print(f"From Zone: {bigship_result.from_zone}")
    print(f"To Zone: {bigship_result.to_zone}")
    print(f"Chargeable Weight: {bigship_result.chargeable_weight_kg}kg")
    print(f"Rate per KG: ₹{bigship_result.rate_per_kg}")
    print(f"Base Freight: ₹{bigship_result.base_freight}")
    print(f"ODA Charge: ₹{bigship_result.surcharges.get('oda', 0)}")
    print(f"Total (Before GST): ₹{bigship_result.total_before_gst}")
    
    if bigship_result.from_zone == "S1" and bigship_result.to_zone == "S2":
        print("\n✅ ZONE MAPPING FIX SUCCESSFUL!")
        if abs(bigship_result.rate_per_kg - 10.84) < 0.01:
            print("✅ RATE CORRECT: ₹10.84/kg")
        else:
            print(f"❌ RATE WRONG: Expected ₹10.84/kg, got ₹{bigship_result.rate_per_kg}/kg")
    else:
        print(f"\n❌ ZONE MAPPING ISSUE: Expected S1→S2, got {bigship_result.from_zone}→{bigship_result.to_zone}")
else:
    print("❌ Bigship result not found")

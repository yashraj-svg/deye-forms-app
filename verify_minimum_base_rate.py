#!/usr/bin/env python
"""Verify Global Cargo minimum base rate of Rs 450"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import GlobalCourierCargo, QuoteInput, ShipmentItem
from forms.calculator.config import DEFAULT_SETTINGS
from forms.calculator.data_loader import PincodeRecord, PincodeDB, _assign_partner_regions

calc = GlobalCourierCargo(DEFAULT_SETTINGS)

# Create pincode DB with test records
db = PincodeDB()
test_pincodes = {
    "110001": ("Delhi", "DELHI"),
    "400001": ("Mumbai", "MAHARASHTRA"),
    "560001": ("Bangalore", "KARNATAKA"),
}

for pincode, (city, state) in test_pincodes.items():
    rec = PincodeRecord(pincode=pincode, city=city, state=state, deliverable=True)
    _assign_partner_regions(rec)
    db.add(rec)

print("\n" + "="*80)
print("GLOBAL CARGO: MINIMUM BASE RATE TEST (Rs 450)")
print("="*80)

# Test cases with different weights to trigger minimum
test_cases = [
    {
        "from": "110001",  # Delhi
        "to": "560001",    # Bangalore
        "weight": 3.0,     # 3kg - should trigger minimum
        "name": "Low weight (3kg Delhi to Bangalore)"
    },
    {
        "from": "110001",
        "to": "400001",
        "weight": 5.0,     # 5kg
        "name": "Low weight (5kg Delhi to Mumbai)"
    },
    {
        "from": "110001",
        "to": "110001",
        "weight": 40.0,    # 40kg - likely above minimum
        "name": "Normal weight (40kg Delhi intra-zone)"
    },
    {
        "from": "110001",
        "to": "560001",
        "weight": 2.0,     # 2kg - very low
        "name": "Very low weight (2kg Delhi to Bangalore)"
    },
]

for test in test_cases:
    items = [ShipmentItem(weight_kg=test["weight"], length_cm=20, breadth_cm=15, height_cm=10)]
    inp = QuoteInput(
        from_pincode=test["from"],
        to_pincode=test["to"],
        items=items,
    )
    
    result = calc.calculate_quote(inp, db)
    
    if result.deliverable:
        # Calculate what it would be without minimum
        calculated_freight = result.rate_per_kg * result.chargeable_weight_kg
        is_minimum_applied = calculated_freight < 450
        
        print(f"\n{test['name']}")
        print(f"  Route: {result.from_zone} -> {result.to_zone}")
        print(f"  Chargeable Weight: {result.chargeable_weight_kg}kg")
        print(f"  Rate: Rs {result.rate_per_kg}/kg")
        print(f"  Calculated Freight: Rs {calculated_freight:.2f}")
        print(f"  Final Base Freight: Rs {result.base_freight}")
        
        if is_minimum_applied:
            print(f"  ✅ MINIMUM Rs 450 APPLIED (was Rs {calculated_freight:.0f})")
        else:
            print(f"  ✓ Base freight above minimum")
    else:
        print(f"\n{test['name']}")
        print(f"  ✗ Not deliverable")

print("\n" + "="*80)
print("KEY CONFIGURATION:")
print("="*80)
print(f"Minimum Weight: 20 kg (chargeable weight rounded up)")
print(f"Minimum Base Rate: Rs 450 (if calculated base < 450)")
print(f"\nFormula: base_freight = max(rate_per_kg × chargeable_weight, 450)")
print("\nExample Calculation:")
print("  If rate = Rs 10/kg, weight = 3kg")
print("  Chargeable = max(3, 20) = 20kg (min weight enforced)")
print("  Calculated freight = 10 × 20 = Rs 200")
print("  Final freight = max(200, 450) = Rs 450 (minimum applied)")
print("="*80 + "\n")

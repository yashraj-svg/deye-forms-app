#!/usr/bin/env python
"""Test Global Cargo rates update (14-02-2026)"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import GlobalCourierCargo, QuoteInput, ShipmentItem
from forms.calculator.data_loader import PincodeDB, PincodeRecord
from forms.calculator.config import DEFAULT_SETTINGS

def test_global_cargo():
    """Test Global Cargo quotes with updated rates"""
    calc = GlobalCourierCargo(DEFAULT_SETTINGS)
    
    # Create test items
    items = [ShipmentItem(weight_kg=10.0, length_cm=20, breadth_cm=15, height_cm=10)]
    
    # Create pincode database with test records
    db = PincodeDB()
    
    # Import the _assign_partner_regions function to set zones properly
    from forms.calculator.data_loader import _assign_partner_regions
    
    # Add test pincodes with state information
    test_pincodes = {
        "110001": ("Delhi", "DELHI"),        # DEL zone
        "400001": ("Mumbai", "MAHARASHTRA"), # BOM zone
        "560001": ("Bangalore", "KARNATAKA"),# BLR zone
    }
    
    for pincode, (city, state) in test_pincodes.items():
        rec = PincodeRecord(pincode=pincode, city=city, state=state, deliverable=True)
        _assign_partner_regions(rec)  # This sets global_cargo_region
        db.add(rec)
    
    # Test cases
    test_cases = [
        {
            "from_pin": "110001",  # Delhi
            "to_pin": "400001",    # Mumbai (Gurgaon → Mumbai = BOM zone)
            "expected_zone": ("DEL", "BOM"),
            "expected_rate": 15.0,  # DEL→BOM should be 15.0
        },
        {
            "from_pin": "110001",  # Delhi
            "to_pin": "560001",    # Bangalore (Gurgaon → Bangalore = BLR zone)
            "expected_zone": ("DEL", "BLR"),
            "expected_rate": 14.0,  # DEL→BLR should be 14.0
        },
        {
            "from_pin": "400001",  # Mumbai
            "to_pin": "110001",    # Delhi (Mumbai → Gurgaon)
            "expected_zone": ("BOM", "DEL"),
            "expected_rate": 13.0,  # BOM→DEL should be 13.0
        },
        {
            "from_pin": "560001",  # Bangalore
            "to_pin": "560001",    # Bangalore (same zone)
            "expected_zone": ("BLR", "BLR"),
            "expected_rate": 10.0,  # BLR→BLR should be 10.0 (intra-zone)
        },
    ]
    
    print("\n" + "="*80)
    print("GLOBAL CARGO RATES TEST (Updated 14-02-2026)")
    print("="*80)
    
    for i, test in enumerate(test_cases, 1):
        from_pin = test["from_pin"]
        to_pin = test["to_pin"]
        
        # Try to get PincodeRecord data
        from_rec = db.get(from_pin) or PincodeRecord(pincode=from_pin, state="")
        to_rec = db.get(to_pin) or PincodeRecord(pincode=to_pin, state="")
        
        inp = QuoteInput(
            from_pincode=from_pin,
            to_pincode=to_pin,
            items=items,
        )
        
        result = calc.calculate_quote(inp, db)
        
        from_zone_actual = result.from_zone or "UNKNOWN"
        to_zone_actual = result.to_zone or "UNKNOWN"
        expected_from, expected_to = test["expected_zone"]
        
        print(f"\nTest {i}: {from_pin} → {to_pin}")
        print(f"  Zones: {from_zone_actual} → {to_zone_actual} (expected {expected_from} → {expected_to})")
        
        if result.deliverable:
            print(f"  CW: {result.chargeable_weight_kg}kg, Rate: ₹{result.rate_per_kg}/kg")
            print(f"  Base Freight: ₹{result.base_freight}")
            print(f"  Surcharges: {result.surcharges}")
            print(f"  Total (w/ GST): ₹{result.total_after_gst}")
            
            # Check rate
            if result.rate_per_kg == test["expected_rate"]:
                print(f"  ✓ Rate matches: ₹{result.rate_per_kg}/kg")
            else:
                print(f"  ✗ Rate MISMATCH: got ₹{result.rate_per_kg}, expected ₹{test['expected_rate']}")
        else:
            print(f"  ✗ Not Deliverable: {result.reason}")
    
    # Test volumetric weight
    print("\n" + "-"*80)
    print("VOLUMETRIC WEIGHT TEST")
    print("-"*80)
    
    vol_item = ShipmentItem(weight_kg=5.0, length_cm=100, breadth_cm=50, height_cm=50)  # 5kg actual, ~63kg volumetric
    vol_inp = QuoteInput(
        from_pincode="110001",
        to_pincode="400001",
        items=[vol_item],
    )
    
    vol_result = calc.calculate_quote(vol_inp, db)
    print(f"\nScenario: 5kg actual, 100×50×50cm")
    print(f"  Volumetric Weight: {vol_result.volumetric_weight_kg}kg (divisor 4000 = 7kg per CFT)")
    print(f"  Chargeable Weight: {vol_result.chargeable_weight_kg}kg (max of actual and volumetric)")
    print(f"  Base Freight: ₹{vol_result.base_freight}")
    
    # Verify minimum weight enforcement
    min_item = ShipmentItem(weight_kg=2.0, length_cm=10, breadth_cm=10, height_cm=10)
    min_inp = QuoteInput(
        from_pincode="110001",
        to_pincode="400001",
        items=[min_item],
    )
    
    min_result = calc.calculate_quote(min_inp, db)
    print(f"\nScenario: 2kg actual (below 20kg minimum)")
    print(f"  Actual Weight: 2kg")
    print(f"  Chargeable Weight: {min_result.chargeable_weight_kg}kg (should be 20kg minimum)")
    
    if min_result.chargeable_weight_kg >= 20.0:
        print(f"  ✓ Minimum 20kg enforced")
    else:
        print(f"  ✗ Minimum 20kg NOT enforced")
    
    # Test minimum docket
    print(f"\nScenario: 20kg, DEL→BOM (rate ₹15)")
    print(f"  Base Freight: ₹{min_result.base_freight}")
    if min_result.base_freight >= 450.0:
        print(f"  ✓ Minimum docket ₹450 applied")
    else:
        print(f"  ✗ Minimum docket ₹450 might not be applied (base is ₹{min_result.base_freight})")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    try:
        test_global_cargo()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

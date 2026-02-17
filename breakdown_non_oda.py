#!/usr/bin/env python3
"""
Detailed breakdown of Bigship calculator for NON-ODA locations
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.bigship_calculator import Bigship
from forms.calculator.freight_calculator import QuoteInput, ShipmentItem, Settings
from forms.calculator.data_loader import PincodeDB, PincodeRecord

# Test pincode mappings
PINCODE_STATE_MAP = {
    "600095": "Tamil Nadu", "621220": "Tamil Nadu",
    "560060": "Karnataka", "676101": "Kerala", "695020": "Kerala",
    "524413": "Andhra Pradesh", "411045": "Maharashtra",
    "152116": "Punjab", "636111": "Tamil Nadu",
    "132039": "Haryana", "571134": "Karnataka",
    "201306": "Uttar Pradesh", "212635": "Uttar Pradesh",
    "140301": "West Bengal", "623536": "Tamil Nadu",
    "686664": "Kerala",
}

# ODA pincodes (to filter them out)
ODA_PINCODES = {"686664"}  # 40kg CFT case is ODA

class TestPincodeDB(PincodeDB):
    def get(self, pincode):
        if str(pincode) in self._test_records:
            return self._test_records[str(pincode)]
        result = super().get(pincode)
        if result is None and str(pincode) in PINCODE_STATE_MAP:
            result = PincodeRecord(pincode=str(pincode))
            result.state = PINCODE_STATE_MAP[str(pincode)]
            result.city = ""
        return result
    
    def __init__(self):
        super().__init__()
        self._test_records = {}

settings = Settings()
calc = Bigship(settings=settings)
test_db = TestPincodeDB()

# Test cases - NON-ODA ONLY
test_cases = [
    # (from_pin, to_pin, weight, service_type, expected_total, description)
    (600095, 621220, 25.00, "MPS", 611.29, "MPS - 25kg Tamil Nadu → Tamil Nadu"),
    (560060, 695020, 27.75, "CFT", 408.00, "CFT - 28kg Karnataka → Kerala"),
    (560060, 524413, 14.98, "MPS", 441.77, "MPS - 15kg Karnataka → Andhra Pradesh"),
    (411045, 152116, 14.98, "MPS", 441.77, "MPS - 15kg Maharashtra → Punjab"),
    (201306, 212635, 23.22, "MPS", 659.75, "MPS - 23kg Uttar Pradesh → Uttar Pradesh"),
    (201306, 140301, 26.00, "LTL", 420.96, "LTL - 26kg Uttar Pradesh → West Bengal"),
    (600095, 623536, 30.00, "LTL", 473.60, "LTL - 30kg Tamil Nadu → Tamil Nadu"),
]

print("=" * 120)
print("BIGSHIP CALCULATOR - NON-ODA LOCATIONS BREAKDOWN")
print("=" * 120)

total_pass = 0
total_fail = 0

for from_pin, to_pin, weight, service_type, expected_total, desc in test_cases:
    print(f"\n{desc}")
    print("-" * 120)
    
    # Skip ODA pincodes
    if str(to_pin) in ODA_PINCODES:
        print(f"SKIPPED (ODA location)")
        continue
    
    try:
        # Create input
        inp = QuoteInput(
            items=[ShipmentItem(weight_kg=weight, length_cm=50, breadth_cm=50, height_cm=50)],
            from_pincode=str(from_pin),
            to_pincode=str(to_pin),
        )
        inp.bigship_service_type = service_type
        
        # Get zones
        from_state = PINCODE_STATE_MAP.get(str(from_pin), "Unknown")
        to_state = PINCODE_STATE_MAP.get(str(to_pin), "Unknown")
        
        if service_type == "CFT":
            from_zone = calc.get_zone_from_state(from_state, "CFT")
            to_zone = calc.get_zone_from_state(to_state, "CFT")
            print(f"Route: {from_state} ({from_zone}) → {to_state} ({to_zone})")
            
            # Get rate
            if from_zone in calc.CFT_RATES_MATRIX and to_zone in calc.CFT_RATES_MATRIX[from_zone]:
                rate = calc.CFT_RATES_MATRIX[from_zone][to_zone]
                print(f"CFT Rate Matrix: {from_zone} → {to_zone} = Rs {rate}/kg")
            
        elif service_type == "MPS":
            from_zone = calc.get_zone_from_state(from_state, "MPS")
            to_zone = calc.get_zone_from_state(to_state, "MPS")
            print(f"Route: {from_state} ({from_zone}) → {to_state} ({to_zone})")
            
            # Get rate structure
            if from_zone in calc.MPS_RATES_MATRIX and to_zone in calc.MPS_RATES_MATRIX[from_zone]:
                rates = calc.MPS_RATES_MATRIX[from_zone][to_zone]
                print(f"MPS Rate Structure: {from_zone} → {to_zone} = 10kg: Rs {rates['10kg']}, Add 1kg: Rs {rates['add_1kg']}/kg")
                
        elif service_type == "LTL":
            from_zone = calc.get_zone_from_state(from_state, "LTL")
            to_zone = calc.get_zone_from_state(to_state, "LTL")
            print(f"Route: {from_state} ({from_zone}) → {to_state} ({to_zone})")
            
            # Get rate
            if from_zone in calc.LTL_RATES_MATRIX and to_zone in calc.LTL_RATES_MATRIX[from_zone]:
                rate = calc.LTL_RATES_MATRIX[from_zone][to_zone]
                print(f"LTL Rate Matrix: {from_zone} → {to_zone} = Rs {rate}/kg")
        
        # Calculate quote
        result = calc.calculate_quote(inp, test_db)
        
        print(f"\nChargeable Weight: {result.chargeable_weight_kg:.2f} kg")
        print(f"Base Freight: Rs {result.base_freight:.2f}")
        print(f"Surcharges: {result.surcharges}")
        print(f"Total Before GST: Rs {result.total_before_gst:.2f}")
        print(f"GST Amount: Rs {result.gst_amount:.2f}")
        print(f"TOTAL: Rs {result.total_after_gst:.2f}")
        
        print(f"\nEXPECTED: Rs {expected_total:.2f}")
        
        difference = abs(result.total_after_gst - expected_total)
        pct_diff = (difference / expected_total * 100) if expected_total > 0 else 0
        
        status = "✓ PASS" if difference <= 100 else "✗ FAIL"
        print(f"DIFFERENCE: Rs {difference:.2f} ({pct_diff:.1f}%)")
        print(f"STATUS: {status}")
        
        if difference <= 100:
            total_pass += 1
        else:
            total_fail += 1
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        total_fail += 1

print("\n" + "=" * 120)
print(f"SUMMARY: {total_pass} PASSED, {total_fail} FAILED")
print("=" * 120)

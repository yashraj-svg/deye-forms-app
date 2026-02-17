#!/usr/bin/env python3
"""
Test Bigship calculator for NON-ODA pincodes only
Compare calculated vs actual bills for locations without ODA charges
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.models import PincodeData
from forms.calculator.bigship_calculator import Bigship
from forms.calculator.freight_calculator import QuoteInput, ShipmentItem
from forms.calculator.data_loader import PincodeDB, PincodeRecord
from forms.calculator.config import Settings

# Manually map test pincodes to states
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

class TestPincodeDB(PincodeDB):
    """Override to return test pincode states"""
    def get(self, pincode):
        result = super().get(pincode)
        if result is None and str(pincode) in PINCODE_STATE_MAP:
            result = PincodeRecord(
                pincode=str(pincode),
                state=PINCODE_STATE_MAP[str(pincode)],
                city="Test City"
            )
        return result

def test_non_oda_bills():
    """Test calculator against non-ODA bills only"""
    
    settings = Settings()
    calc = Bigship(settings=settings)
    pincodes = TestPincodeDB()
    
    # Test cases from actual bills
    test_cases = [
        # Format: (from_pin, to_pin, weight, service_type, expected_total, description, is_oda)
        (600095, 621220, 25, "MPS", 611.29, "MPS - 25kg TN→TN", False),
        (560060, 676101, 103.01, "CFT", 1786.4, "CFT - 103kg KA→KL", True),  # SKIP - ODA
        (560060, 695020, 27.75, "CFT", 408, "CFT - 28kg KA→KL", True),  # SKIP - ODA
        (560060, 524413, 14.98, "MPS", 441.77, "MPS - 15kg KA→AP", False),
        (411045, 152116, 14.98, "MPS", 441.77, "MPS - 15kg MH→PB", False),
        (411045, 636111, 111, "LTL", 1729.16, "LTL - 111kg MH→TN", False),
        (411045, 132039, 111, "LTL", 1683.65, "LTL - 111kg MH→HR", False),
        (411045, 571134, 111, "LTL", 1653.68, "LTL - 111kg MH→KA", False),
        (201306, 212635, 23.22, "MPS", 659.75, "MPS - 23kg UP→UP", False),
        (201306, 140301, 26, "LTL", 420.96, "LTL - 26kg UP→WB", False),
        (600095, 623536, 30, "LTL", 473.6, "LTL - 30kg TN→TN", False),
        (560060, 686664, 40, "CFT", 1504.30, "CFT - 40kg KA→KL", True),  # SKIP - ODA
    ]
    
    print("\n" + "="*110)
    print("BIGSHIP CALCULATOR TEST - NON-ODA PINCODES ONLY")
    print("="*110)
    print(f"{'From':<10} {'To':<10} {'Wt(kg)':<10} {'Type':<6} {'Expected':<12} {'Calculated':<12} {'Diff':<10} {'%':<8} {'Status'}")
    print("-"*110)
    
    matches = 0
    total_tests = 0
    non_oda_count = 0
    
    for from_pin, to_pin, weight, service_type, expected_total, desc, is_oda in test_cases:
        # Skip ODA locations for this test
        if is_oda:
            print(f"{from_pin:<10} {to_pin:<10} {weight:<10.2f} {service_type:<6} {'ODA':<12} {'SKIP':<12} {'-':<10} {'-':<8} SKIPPED (ODA)")
            continue
        
        total_tests += 1
        non_oda_count += 1
        
        try:
            inp = QuoteInput(
                items=[ShipmentItem(weight_kg=weight, length_cm=50, breadth_cm=50, height_cm=50)],
                from_pincode=str(from_pin),
                to_pincode=str(to_pin),
            )
            inp.bigship_service_type = service_type
            
            result = calc.calculate_quote(inp, pincodes)
            calculated = result.total_after_gst
            difference = abs(calculated - expected_total)
            percentage_diff = (difference / expected_total * 100) if expected_total > 0 else 0
            
            # Tolerance: Rs 0-100 is acceptable
            status = "PASS" if difference <= 100 else "WARN" if difference <= 200 else "FAIL"
            if status == "PASS":
                matches += 1
            
            print(f"{from_pin:<10} {to_pin:<10} {weight:<10.2f} {service_type:<6} Rs{expected_total:<11.2f} Rs{calculated:<11.2f} Rs{difference:<9.2f} {percentage_diff:<7.1f}% {status}")
            
        except Exception as e:
            print(f"{from_pin:<10} {to_pin:<10} {weight:<10.2f} {service_type:<6} {'ERROR':<12} {'N/A':<12} {str(e)[:40]}")
    
    print("-"*110)
    print(f"\nNON-ODA TEST RESULTS: {matches}/{total_tests} tests passed (within Rs 100 tolerance)")
    print(f"Pass Rate: {matches/total_tests*100:.1f}% for non-ODA locations")
    print(f"Total ODA locations skipped: {len(test_cases) - total_tests}")
    print("="*110 + "\n")
    
    return matches, total_tests

if __name__ == "__main__":
    matches, total = test_non_oda_bills()
    sys.exit(0 if matches == total else 1)

#!/usr/bin/env python3
"""
Test Bigship calculator against REAL bill data from user spreadsheet
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.models import PincodeData
from forms.calculator.bigship_calculator import Bigship
from forms.calculator.freight_calculator import QuoteInput, ShipmentItem
from forms.calculator.data_loader import PincodeDB, PincodeRecord
from forms.calculator.config import Settings

# Manually map test pincodes to states
PINCODE_STATE_MAP = {
    "751007": "Odisha",
    "560060": "Karnataka",
    "600091": "Tamil Nadu", 
    "641042": "Tamil Nadu",
    "321220": "West Bengal",
    "248013": "Uttarakhand",
    "201305": "Uttar Pradesh",
    "600095": "Tamil Nadu",
    "534426": "Andhra Pradesh",
    "673010": "Kerala",
    "688529": "Kerala",
    "683503": "Kerala",
}

class TestPincodeDB(PincodeDB):
    def get(self, pincode):
        result = super().get(pincode)
        if result is None and str(pincode) in PINCODE_STATE_MAP:
            result = PincodeRecord(
                pincode=str(pincode),
                state=PINCODE_STATE_MAP[str(pincode)],
                city="Test City"
            )
        return result


def test_real_bills():
    """Test calculator against real bill data from spreadsheet"""
    
    settings = Settings()
    calc = Bigship(settings=settings)
    
    # Real test cases from spreadsheet with actual dimensions
    test_cases = [
        # (from_pin, to_pin, weight, l, b, h, service_type, expected_total, description)
        (751007, 560060, 25, 74, 48, 31, "LTL", 560.5, "LTL 25kg OD→KA"),
        (600091, 641042, 47, 0, 0, 0, "LTL", 713.46, "LTL 47kg TN→TN"),
        (321220, 560060, 25, 74, 48, 31, "LTL", 477.75, "LTL 25kg WB→KA"),
        (248013, 201305, 11, 43, 43, 26, "MPS", 380.43, "MPS 11kg UT→UP"),
        (600095, 621220, 25, 74, 48, 31, "MPS", 611.29, "MPS 25kg TN→TN"),
        (534426, 560060, 11, 43, 43, 26, "MPS", 294.05, "MPS 11kg AP→KA"),
        (560060, 688529, 73, 0, 0, 0, "CFT", 1450, "CFT 73kg KA→KL ODA"),
        (673010, 560060, 27.75, 63, 41, 29, "CFT", 483, "CFT 27.75kg KL→KA"),
        (560060, 683503, 27.75, 63, 41, 29, "CFT", 408, "CFT 27.75kg KA→KL"),
    ]
    
    print("\n" + "="*120)
    print("BIGSHIP CALCULATOR - REAL BILL DATA TEST")
    print("="*120)
    print(f"{'From':<8} {'To':<8} {'Wt':<6} {'Dims':<16} {'Type':<6} {'Expected':<12} {'Calculated':<12} {'Diff':<10} {'Match':<8}")
    print("-"*120)
    
    matches = 0
    total_tests = len(test_cases)
    
    for from_pin, to_pin, weight, length, breadth, height, service_type, expected_total, desc in test_cases:
        try:
            # Create quote input with real dimensions (when available)
            if length > 0 and breadth > 0 and height > 0:
                items = [ShipmentItem(weight_kg=weight, length_cm=length, breadth_cm=breadth, height_cm=height)]
            else:
                # For cases without dimensions, use minimal dimensions to keep vol weight close to actual
                dim = (weight * 30) ** (1/3)  # Cube root to get dimension
                items = [ShipmentItem(weight_kg=weight, length_cm=dim, breadth_cm=dim, height_cm=dim)]
            
            inp = QuoteInput(
                items=items,
                from_pincode=str(from_pin),
                to_pincode=str(to_pin),
            )
            inp.bigship_service_type = service_type
            
            # Get pincodes
            pincodes = TestPincodeDB()
            
            # Calculate quote
            quote = calc.calculate_quote(inp, pincodes)
            
            # Compare
            calculated = quote.total_after_gst
            difference = calculated - expected_total
            percentage_diff = (abs(difference) / expected_total * 100) if expected_total > 0 else 0
            
            # Tolerance: Rs 0-100 is acceptable
            if abs(difference) <= 100:
                status = "PASS"
                matches += 1
            elif abs(difference) <= 200:
                status = "WARN"
            else:
                status = "FAIL"
            
            dims_str = f"{length}×{breadth}×{height}" if length > 0 else "N/A"
            print(f"{from_pin:<8} {to_pin:<8} {weight:<6.2f} {dims_str:<16} {service_type:<6} Rs{expected_total:<11.2f} Rs{calculated:<11.2f} {difference:>+9.2f} {status:<8}")
            
        except Exception as e:
            print(f"{from_pin:<8} {to_pin:<8} {weight:<6.2f} {'N/A':<16} {service_type:<6} Rs{expected_total:<11.2f} ERROR: {str(e)[:40]}")
    
    print("-"*120)
    print(f"RESULT: {matches}/{total_tests} tests passed (within Rs 100 tolerance)")
    print("="*120 + "\n")


if __name__ == "__main__":
    test_real_bills()

#!/usr/bin/env python3
"""
Test Bigship calculator against actual bills provided
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

# Manually map test pincodes to states (since they're not in DB)
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

def test_actual_bills():
    """Test calculator against real bill data"""
    
    # Initialize settings
    settings = Settings()
    
    # Initialize calculator
    calc = Bigship(settings=settings)
    
    # Test cases from actual bills
    test_cases = [
        # Format: (from_pin, to_pin, weight, l, b, h, service_type, expected_total, description)
        # Using real dimensions from bills where available
        (600095, 621220, 25, 74, 48, 31, "MPS", 611.29, "MPS - 25kg"),
        (560060, 676101, 103.01, 0, 0, 0, "CFT", 1786.4, "CFT - 103kg"),
        (560060, 695020, 27.75, 63, 41, 29, "CFT", 408, "CFT - 28kg"),
        (560060, 524413, 14.98, 43, 43, 26, "MPS", 441.77, "MPS - 15kg"),
        (411045, 152116, 14.98, 43, 43, 26, "MPS", 441.77, "MPS - 15kg DUP"),
        (411045, 636111, 111, 0, 0, 0, "LTL", 1729.16, "LTL - 111kg"),
        (411045, 132039, 111, 0, 0, 0, "LTL", 1683.65, "LTL - 111kg VAR"),
        (411045, 571134, 111, 0, 0, 0, "LTL", 1653.68, "LTL - 111kg VAR2"),
        (201306, 212635, 23.22, 0, 0, 0, "MPS", 659.75, "MPS - 23kg"),
        (201306, 140301, 26, 0, 0, 0, "LTL", 420.96, "LTL - 26kg"),
        (600095, 623536, 30, 0, 0, 0, "LTL", 473.6, "LTL - 30kg"),
        (560060, 686664, 40, 0, 0, 0, "CFT", 1504.30, "CFT - 40kg ODA"),
    ]
    
    print("\n" + "="*100)
    print("BIGSHIP CALCULATOR TEST - ACTUAL BILLS COMPARISON")
    print("="*100)
    print(f"{'From':<10} {'To':<10} {'Wt(kg)':<10} {'Type':<6} {'Expected':<12} {'Calculated':<12} {'Match':<8} {'Notes'}")
    print("-"*100)
    
    matches = 0
    total_tests = len(test_cases)
    
    for from_pin, to_pin, weight, length, breadth, height, service_type, expected_total, desc in test_cases:
        try:
            # Use provided dimensions, or smart defaults if not provided
            if length > 0 and breadth > 0 and height > 0:
                # Use actual dimensions from bill
                l, b, h = length, breadth, height
            else:
                # For cases without dimensions, use minimal dimensions to keep vol weight close to actual
                # This assumes dimensions that: L×B×H/divisor ≤ actual_weight
                # For simplicity: use cube root approach
                dim = max(30, (weight * 25) ** (1/3))  # Cube root, minimum 30cm
                l, b, h = dim, dim, dim
            
            inp = QuoteInput(
                items=[ShipmentItem(weight_kg=weight, length_cm=l, breadth_cm=b, height_cm=h)],
                from_pincode=str(from_pin),
                to_pincode=str(to_pin),
            )
            
            # Add service type
            inp.bigship_service_type = service_type
            
            # Create custom pincode records with states (for test pincodes not in DB)
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
            
            # Get pincodes
            pincodes = TestPincodeDB()
            
            # Calculate quote
            quote = calc.calculate_quote(inp, pincodes)
            
            # Compare
            calculated = quote.total_after_gst
            difference = abs(calculated - expected_total)
            percentage_diff = (difference / expected_total * 100) if expected_total > 0 else 0
            
            # Tolerance: Rs 0-100 is acceptable
            match = "PASS" if difference <= 100 else "WARN" if difference <= 200 else "FAIL"
            if match == "PASS":
                matches += 1
            
            print(f"{from_pin:<10} {to_pin:<10} {weight:<10.2f} {service_type:<6} Rs{expected_total:<11.2f} Rs{calculated:<11.2f} {match:<8} {desc} (Rs{difference:.2f})")
            
        except Exception as e:
            print(f"{from_pin:<10} {to_pin:<10} {weight:<10.2f} {service_type:<6} {'ERROR':<12} {'N/A':<12} {'FAIL':<8} {str(e)[:40]}")
    
    print("-"*100)
    print(f"RESULT: {matches}/{total_tests} tests passed (within Rs 100 tolerance)")
    print("="*100 + "\n")
    
    return matches == total_tests

if __name__ == "__main__":
    success = test_actual_bills()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Test Bigship Calculator - CFT, LTL, MPS service types
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from forms.calculator.bigship_calculator import Bigship
from forms.calculator.freight_calculator import QuoteInput, ShipmentItem, Settings
from forms.calculator.data_loader import load_pincode_master

def test_bigship():
    """Test Bigship calculator with different service types"""
    
    pins = load_pincode_master('.')
    bigship = Bigship(Settings())
    
    print("="*100)
    print("BIGSHIP CALCULATOR TEST - CFT, LTL, MPS Service Types")
    print("="*100)
    
    # Test serviceable pincodes
    test_cases = [
        {
            "from": "110001",
            "to": "146002",
            "weight": 15.0,
            "service": "LTL",
            "city": "Hoshiarpur, Punjab"
        },
        {
            "from": "110001",
            "to": "394650",
            "weight": 50.0,
            "service": "CFT",
            "city": "Songadh, Gujarat"
        },
        {
            "from": "110001",
            "to": "455459",
            "weight": 100.0,
            "service": "MPS",
            "city": "Khategaon, Madhya Pradesh"
        },
    ]
    
    for idx, test in enumerate(test_cases, 1):
        print(f"\nTest Case {idx}: {test['from']} -> {test['to']} ({test['city']}, {test['weight']}kg, {test['service']})")
        print("-" * 100)
        
        inp = QuoteInput(
            from_pincode=test['from'],
            to_pincode=test['to'],
            items=[ShipmentItem(weight_kg=test['weight'], length_cm=0, breadth_cm=0, height_cm=0)],
            bigship_service_type=test['service']
        )
        
        result = bigship.calculate_quote(inp, pins)
        
        if result.deliverable:
            print(f"Chargeable Weight: {result.chargeable_weight_kg}kg")
            print(f"Base Freight: Rs.{result.base_freight:.2f}")
            print(f"Rate per kg: Rs.{result.rate_per_kg:.2f}")
            print(f"Surcharges: {result.surcharges}")
            print(f"Total Before GST: Rs.{result.total_before_gst:.2f}")
            print(f"GST (18%): Rs.{result.gst_amount:.2f}")
            print(f"Total After GST: Rs.{result.total_after_gst:.2f}")
            print(f"Service Details: {result.rate_details}")
        else:
            print(f"NOT DELIVERABLE: {result.reason}")
    
    print("\n" + "="*100)
    print("TEST COMPLETE")
    print("="*100)

if __name__ == "__main__":
    try:
        test_bigship()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

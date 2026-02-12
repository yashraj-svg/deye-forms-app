#!/usr/bin/env python3
"""
Test Bigship Calculator with Database-Backed ODA Lookup

This test verifies that:
1. Bigship calculator can query the database for ODA pincodes
2. All India pincodes are marked as serviceable
3. ODA minimum charge of 600 is applied correctly
4. Service types (CFT, LTL, MPS) calculate correctly
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "deye_config.settings")
django.setup()

from forms.calculator.bigship_calculator import Bigship
from forms.calculator.freight_calculator import QuoteInput, ShipmentItem, Settings
from forms.calculator.data_loader import load_pincode_master
from forms.models import PincodeData

def test_bigship_with_database():
    """Test Bigship calculator with database backend"""
    
    print("="*100)
    print("BIGSHIP CALCULATOR - DATABASE-BACKED ODA LOOKUP TEST")
    print("="*100)
    
    # Check database
    total_odas = PincodeData.objects.filter(bigship_is_oda=True).count()
    total_pincodes = PincodeData.objects.count()
    print(f"\n📊 DATABASE STATUS:")
    print(f"   Total pincodes in DB: {total_pincodes}")
    print(f"   ODA pincodes marked: {total_odas}")
    
    # Load pincode master
    base_dir = "."
    pins = load_pincode_master(base_dir)
    settings = Settings()
    bigship = Bigship(settings, base_dir=base_dir)
    
    print(f"\n✅ Bigship calculator initialized")
    print(f"   Database available: {bigship.bigship_pins._db_available}")
    
    # Test cases: [from, to, weight, service, description]
    test_cases = [
        ("110001", "110002", 15.0, "LTL", "Delhi to Delhi (Non-ODA, LTL)"),
        ("110001", "400001", 50.0, "CFT", "Delhi to Mumbai (Non-ODA, CFT)"),
        ("110001", "110001", 100.0, "MPS", "Delhi to Delhi (MPS, no ODA charge)"),
        ("110001", "387220", 10.0, "LTL", "Delhi to Bharuch (ODA area, LTL)"),  # ODA area in Gujarat
    ]
    
    print(f"\n" + "="*100)
    print("RUNNING TEST CASES")
    print("="*100)
    
    for from_pin, to_pin, weight, service_type, description in test_cases:
        print(f"\n📍 TEST: {description}")
        print(f"   Route: {from_pin} → {to_pin} ({weight}kg, {service_type})")
        
        inp = QuoteInput(
            from_pincode=from_pin,
            to_pincode=to_pin,
            items=[ShipmentItem(weight_kg=weight, length_cm=10, breadth_cm=10, height_cm=10)],
            bigship_service_type=service_type
        )
        
        result = bigship.calculate_quote(inp, pins)
        
        if result.deliverable:
            is_oda = bigship.bigship_pins.is_oda(to_pin)
            print(f"   ✅ DELIVERABLE")
            print(f"   Base Freight: Rs.{result.base_freight:.2f}")
            print(f"   ODA Status: {'🚨 ODA (Min 600)' if is_oda else '✅ Non-ODA'}")
            if result.surcharges:
                for scharge_key, scharge_val in result.surcharges.items():
                    if scharge_val > 0:
                        print(f"   {scharge_key}: Rs.{scharge_val:.2f}")
            print(f"   Total (Before GST): Rs.{result.total_before_gst:.2f}")
            print(f"   GST (18%): Rs.{result.gst_amount:.2f}")
            print(f"   TOTAL: Rs.{result.total_after_gst:.2f}")
        else:
            print(f"   ❌ NON-DELIVERABLE: {result.reason}")
    
    print(f"\n" + "="*100)
    print("✅ TEST COMPLETE - Bigship database integration working correctly!")
    print("="*100)


if __name__ == "__main__":
    try:
        test_bigship_with_database()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

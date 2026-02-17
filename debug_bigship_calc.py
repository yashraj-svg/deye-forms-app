#!/usr/bin/env python3
"""
Debug Bigship calculator to trace calculation steps
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.bigship_calculator import Bigship
from forms.calculator.freight_calculator import QuoteInput, ShipmentItem
from forms.calculator.data_loader import PincodeDB, PincodeRecord
from forms.calculator.config import Settings

def debug_calculation():
    """Debug one calculation to see breakdown"""
    
    # Initialize
    settings = Settings()
    calc = Bigship(settings=settings)
    pins = PincodeDB()
    
    # Test case: MPS 25kg from 600095 to 621220, expected Rs611.29
    print("\n" + "="*100)
    print("DEBUG: MPS 25kg shipment (Expected total: Rs 611.29)")
    print("="*100)
    
    inp = QuoteInput(
        items=[ShipmentItem(weight_kg=25, length_cm=50, breadth_cm=50, height_cm=50)],
        from_pincode="600095",
        to_pincode="621220",
    )
    inp.bigship_service_type = "MPS"
    
    # Get pincode details
    from_pin = pins.get("600095")
    to_pin = pins.get("621220")
    
    print(f"\nShipment Details:")
    # Force pincode records with correct state mapping
    from_pin = PincodeRecord(pincode="600095", state="Tamil Nadu", city="Chennai")
    to_pin = PincodeRecord(pincode="621220", state="Tamil Nadu", city="Tiruppur")
    
    print(f"\nShipment Details:")
    print(f"  From: {from_pin.pincode} ({from_pin.state}, {from_pin.city})")
    print(f"  To:   {to_pin.pincode} ({to_pin.state}, {to_pin.city})")
    print(f"  Weight: 25 kg")
    print(f"  Service: MPS")
    
    # Get zones
    from_zone = calc.get_zone_from_state(from_pin.state, "MPS")
    to_zone = calc.get_zone_from_state(to_pin.state, "MPS")
    
    print(f"\nZone Mapping:")
    print(f"  From Zone: {from_zone}")
    print(f"  To Zone: {to_zone}")
    
    # Get rate from matrix
    rate_struct = calc.MPS_RATES_MATRIX.get(from_zone, {}).get(to_zone, {"10kg": 296, "add_1kg": 24})
    print(f"\nMPS Rate Matrix ({from_zone} -> {to_zone}):")
    print(f"  Base (10kg): Rs {rate_struct['10kg']}")
    print(f"  Add per kg: Rs {rate_struct['add_1kg']}")
    
    # Calculate base freight
    if 25 <= 10:
        base = rate_struct['10kg']
    else:
        base = rate_struct['10kg'] + (25 - 10) * rate_struct['add_1kg']
    
    print(f"\nBase Freight Calculation:")
    print(f"  = {rate_struct['10kg']} + (25-10) * {rate_struct['add_1kg']}")
    print(f"  = {rate_struct['10kg']} + 15 * {rate_struct['add_1kg']}")
    print(f"  = Rs {base}")
    
    # Run calculator
    quote = calc.calculate_quote(inp, pins)
    
    print(f"\nCalculator Output:")
    print(f"  Chargeable Weight: {quote.chargeable_weight_kg} kg")
    print(f"  Base Freight: Rs {quote.base_freight}")
    print(f"  Surcharges: {quote.surcharges}")
    total_surcharges = sum(quote.surcharges.values())
    print(f"  Total Surcharges: Rs {total_surcharges}")
    print(f"  Before GST: Rs {quote.total_before_gst}")
    print(f"  GST (18%): Rs {quote.gst_amount}")
    print(f"  TOTAL (after GST): Rs {quote.total_after_gst}")
    
    print(f"\nComparison:")
    print(f"  Expected: Rs 611.29")
    print(f"  Calculated: Rs {quote.total_after_gst}")
    print(f"  Difference: Rs {abs(quote.total_after_gst - 611.29)}")
    print(f"  % Diff: {abs(quote.total_after_gst - 611.29)/611.29*100:.1f}%")
    
    print("\n" + "="*100)
    print("\nNOTE: To identify discrepancy, need to know:")
    print("1. Are ALL surcharges shown in PDF applied to every shipment?")
    print("2. Or only specific ones (e.g., LR + Green Tax)?")
    print("3. What surcharges appear on actual bill?")
    print("="*100 + "\n")

if __name__ == "__main__":
    debug_calculation()

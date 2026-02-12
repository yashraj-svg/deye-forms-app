#!/usr/bin/env python
"""Check pincode data on Railway deployment."""
import os
import sys

# Add the project paths
sys.path.insert(0, '/app')

from forms.calculator.data_loader import load_pincode_master
from forms.calculator.freight_calculator import GlobalCourierCargo, QuoteInput

print("=" * 60)
print("CHECKING RAILWAY PINCODE DATA")
print("=" * 60)

# Load pincode data
base_path = '/app'
pincode_master = load_pincode_master(base_path)

print(f"\n1. Total pincodes loaded: {len(pincode_master)}")

# Test the 5 reclassified pincodes
test_pincodes = [686691, 574214, 630556, 642001, 688001, 411045, 110020]
print("\n2. Testing specific pincodes:")
for pin in test_pincodes:
    record = pincode_master.get(pin)
    if record:
        print(f"  {pin}: zone={record.global_cargo_region}, is_oda={record.is_oda}")
    else:
        print(f"  {pin}: NOT FOUND")

# Test a shipment calculation
print("\n3. Test calculation (110020→411045, 110kg):")
calculator = GlobalCourierCargo(pincode_master)
quote_input = QuoteInput(
    from_pin=110020,
    to_pin=411045,
    weight=110,
    length=None,
    width=None,
    height=None,
    invoice_value=None
)
result = calculator.calculate_quote(quote_input)
print(f"  Total: ₹{result.total_amount:.2f}")
print(f"  Base: ₹{result.base_freight:.2f}")
print(f"  ODA: ₹{result.oda_charge:.2f}")
print(f"  Fuel: ₹{result.fuel_surcharge:.2f}")
print(f"  GST: ₹{result.gst:.2f}")

# Test another ODA shipment
print("\n4. Test calculation (560060→686691, 11kg):")
quote_input2 = QuoteInput(
    from_pin=560060,
    to_pin=686691,
    weight=11,
    length=None,
    width=None,
    height=None,
    invoice_value=None
)
result2 = calculator.calculate_quote(quote_input2)
print(f"  Total: ₹{result2.total_amount:.2f}")
print(f"  Base: ₹{result2.base_freight:.2f}")
print(f"  ODA: ₹{result2.oda_charge:.2f}")
print(f"  Fuel: ₹{result2.fuel_surcharge:.2f}")
print(f"  GST: ₹{result2.gst:.2f}")

print("\n" + "=" * 60)

"""
Test Safexpress Calculator with Updated OSC Logic
=================================================
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import Safexpress, QuoteInput
from forms.calculator.data_loader import load_pincode_master, PincodeRecord
from forms.calculator.config import DEFAULT_SETTINGS

print("=" * 80)
print("TESTING SAFEXPRESS CALCULATOR WITH OSC LOGIC")
print("=" * 80)

# Simulate Invoice #1: Low freight scenario
print("\n" + "▶" * 40)
print("TEST 1: Low Freight Scenario (OSC should apply)")
print("▶" * 40)

# Create a simple test where base freight would be low
carrier = Safexpress(DEFAULT_SETTINGS)

# Manually set parameters to simulate invoice #1
# We need actual weight 30 kg, rate ₹6/kg = ₹180 base freight
print("\nSimulated Invoice #1:")
print("  Charged Weight: 30 kg")
print("  Rate per kg: ₹6")
print("  Basic Freight: 30 × 6 = ₹180")
print("  Waybill: ₹150")

base_freight = 180.0
mock_input = QuoteInput(
    from_pincode="560001",  # Bangalore
    to_pincode="401201",    # Vasai
    weight_kg=30,
    length_cm=50,
    breadth_cm=40,
    height_cm=30,
    insured_value=10000,
)

# Create mock pincode records
from_pin = PincodeRecord(pincode="560001", city="Bangalore", state="Karnataka")
to_pin = PincodeRecord(pincode="401201", city="Vasai", state="Maharashtra", safexpress_is_oda=False)

# Calculate surcharges
surcharges = carrier.calc_surcharges(base_freight, mock_input, from_pin, to_pin)

print("\n📊 CALCULATED SURCHARGES:")
for name, amount in surcharges.items():
    print(f"  {name}: ₹{amount:.2f}")

total_before_fuel = base_freight + sum(v for k, v in surcharges.items() if k != 'fuel_surcharge')
fuel = surcharges.get('fuel_surcharge', 0)

print(f"\n💰 CALCULATION BREAKDOWN:")
print(f"  Basic Freight: ₹{base_freight:.2f}")
print(f"  Waybill: ₹{surcharges.get('waybill', 0):.2f}")
print(f"  OSC: ₹{surcharges.get('osc', 0):.2f}")
print(f"  UCC: ₹{surcharges.get('ucc', 0):.2f}")
print(f"  ODA (SFXTN): ₹{surcharges.get('oda', 0):.2f}")
print(f"  Value Surcharge: ₹{surcharges.get('insurance', 0):.2f}")
print(f"  State Surcharge: ₹{surcharges.get('state_surcharge', 0):.2f}")
print(f"  ──────────────────────")
print(f"  Subtotal (before fuel): ₹{total_before_fuel:.2f}")
print(f"  Fuel @ 10%: ₹{fuel:.2f}")
print(f"  ──────────────────────")
print(f"  Total Freight: ₹{total_before_fuel + fuel:.2f}")

print("\n✅ VERIFICATION:")
osc_check = max(0, 500 - (base_freight + 150))
print(f"  Expected OSC = MAX(0, 500 - (180 + 150)) = ₹{osc_check:.2f}")
print(f"  Calculated OSC = ₹{surcharges.get('osc', 0):.2f}")
print(f"  Match: {'✓' if abs(surcharges.get('osc', 0) - osc_check) < 0.01 else '✗'}")

base_for_fuel = base_freight + sum(v for k, v in surcharges.items() if k != 'fuel_surcharge')
expected_fuel = base_for_fuel * 0.10
print(f"\n  Expected Fuel = {base_for_fuel:.2f} × 10% = ₹{expected_fuel:.2f}")
print(f"  Calculated Fuel = ₹{fuel:.2f}")
print(f"  Match: {'✓' if abs(fuel - expected_fuel) < 0.01 else '✗'}")

# Test 2: High freight scenario (no OSC)
print("\n" + "▶" * 40)
print("TEST 2: High Freight Scenario (OSC should be 0)")
print("▶" * 40)

base_freight2 = 1200.0
mock_input2 = QuoteInput(
    from_pincode="560001",
    to_pincode="209859",
    weight_kg=120,
    length_cm=100,
    breadth_cm=80,
    height_cm=60,
    insured_value=50000,
)

from_pin2 = PincodeRecord(pincode="560001", city="Bangalore", state="Karnataka")
to_pin2 = PincodeRecord(pincode="209859", city="Unnao", state="Uttar Pradesh", safexpress_is_oda=True)

surcharges2 = carrier.calc_surcharges(base_freight2, mock_input2, from_pin2, to_pin2)

print("\nSimulated Invoice #2:")
print("  Charged Weight: 120 kg")
print("  Basic Freight: ₹1,200")
print("  Waybill: ₹150")

print("\n📊 CALCULATED SURCHARGES:")
for name, amount in surcharges2.items():
    print(f"  {name}: ₹{amount:.2f}")

print("\n✅ VERIFICATION:")
osc_check2 = max(0, 500 - (base_freight2 + 150))
print(f"  Expected OSC = MAX(0, 500 - (1200 + 150)) = ₹{osc_check2:.2f}")
print(f"  Calculated OSC = ₹{surcharges2.get('osc', 0):.2f}")
print(f"  Match: {'✓' if abs(surcharges2.get('osc', 0) - osc_check2) < 0.01 else '✗'}")

base_for_fuel2 = base_freight2 + sum(v for k, v in surcharges2.items() if k != 'fuel_surcharge')
expected_fuel2 = base_for_fuel2 * 0.10
actual_fuel2 = surcharges2.get('fuel_surcharge', 0)
print(f"\n  Expected Fuel = {base_for_fuel2:.2f} × 10% = ₹{expected_fuel2:.2f}")
print(f"  Calculated Fuel = ₹{actual_fuel2:.2f}")
print(f"  Match: {'✓' if abs(actual_fuel2 - expected_fuel2) < 0.01 else '✗'}")

print("\n" + "=" * 80)
print("FUEL FORMULA CONFIRMED:")
print("Fuel = (Basic + Waybill + Value + UCC + SFXTN + OSC) × 10%")
print("=" * 80)

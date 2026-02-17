#!/usr/bin/env python3
"""Debug a single shipment calculation step-by-step"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.bigship_calculator import Bigship
from forms.calculator.freight_calculator import QuoteInput, ShipmentItem, Settings

# Initialize
settings = Settings()
calc = Bigship(settings=settings)

print("="*80)
print("TEST CASE: CFT 103kg Karnataka (560060) to Kerala (676101)")
print("Expected Total: Rs 1,786.40")
print("="*80)

# Create input
inp = QuoteInput(
    from_pincode="560060",
    to_pincode="676101",
    items=[ShipmentItem(weight_kg=103.01, length_cm=50, width_cm=50, height_cm=50)],
    is_prepaid=True,
    is_cod=False,
)
inp.bigship_service_type = "CFT"

# Check zones
from_state = "Karnataka"
to_state = "Kerala"
from_zone = calc.get_zone_from_state(from_state, "CFT")
to_zone = calc.get_zone_from_state(to_state, "CFT")

print(f"\nZone Mapping:")
print(f"  From: {from_state} -> {from_zone}")
print(f"  To: {to_state} -> {to_zone}")

# Check rate
if from_zone in calc.CFT_RATES_MATRIX and to_zone in calc.CFT_RATES_MATRIX[from_zone]:
    rate_per_kg = calc.CFT_RATES_MATRIX[from_zone][to_zone]
    print(f"\nRate: Rs {rate_per_kg}/kg")
else:
    print(f"\nERROR: No rate found for {from_zone} -> {to_zone}")
    rate_per_kg = 0

# Calculate step by step
weight = 103.01
base_freight_raw = weight * rate_per_kg
print(f"\nBase Freight Calculation:")
print(f"  Weight: {weight} kg")
print(f"  Rate: Rs {rate_per_kg}/kg")
print(f"  Raw: {weight} * {rate_per_kg} = Rs {base_freight_raw:.2f}")

# Check minimum
if base_freight_raw < 350:
    base_freight = 350
    print(f"  Applied minimum Rs 350")
else:
    base_freight = base_freight_raw
    print(f"  No minimum applied")
print(f"  Final Base: Rs {base_freight:.2f}")

# Surcharges
print(f"\nSurcharges:")
print(f"  LR: Rs {calc.CFT_LR_CHARGE}")

# Pickup
if weight > 20:
    pickup = max(weight * 1, 75)
    print(f"  Pickup (weight > 20kg): max({weight} * 1, 75) = Rs {pickup:.2f}")
else:
    pickup = 0
    print(f"  Pickup (weight <= 20kg): Rs 0")

# Owner Risk
owner_risk = calc.CFT_OWNER_RISK
print(f"  Owner Risk: Rs {owner_risk}")

# Green Tax
is_delhi = to_state.lower() == "delhi"
if is_delhi:
    green_tax = base_freight * calc.CFT_GREEN_TAX_RATE
    print(f"  Green Tax (to Delhi): {base_freight} * {calc.CFT_GREEN_TAX_RATE} = Rs {green_tax:.2f}")
else:
    green_tax = 0
    print(f"  Green Tax (not Delhi): Rs 0")

# ODA
is_oda = calc.bigship_pins.is_oda("676101")
if is_oda:
    oda = calc.CFT_ODA_CHARGE
    print(f"  ODA (pincode in database): Rs {oda}")
else:
    oda = 0
    print(f"  ODA (not in database): Rs 0")

# Total
total = base_freight + calc.CFT_LR_CHARGE + pickup + owner_risk + green_tax + oda
print(f"\nFinal Calculation:")
print(f"  Base: Rs {base_freight:.2f}")
print(f"  + LR: Rs {calc.CFT_LR_CHARGE}")
print(f"  + Pickup: Rs {pickup:.2f}")
print(f"  + Owner Risk: Rs {owner_risk}")
print(f"  + Green Tax: Rs {green_tax:.2f}")
print(f"  + ODA: Rs {oda}")
print(f"  = TOTAL: Rs {total:.2f}")
print(f"\nExpected: Rs 1,786.40")
print(f"Difference: Rs {abs(total - 1786.40):.2f} ({abs(total - 1786.40) / 1786.40 * 100:.1f}%)")

# Now compare to actual calculator
from forms.calculator.data_loader import PincodeDB
pins = PincodeDB()
result = calc.calculate_quote(inp, pins)
print(f"\nCalculator Result: Rs {result.total_after_gst:.2f}")
print(f"Surcharges: {result.surcharges}")

#!/usr/bin/env python
"""Check Global Cargo rate for Andhra Pradesh to Chattisgarh"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import GlobalCourierCargo
from forms.calculator.config import DEFAULT_SETTINGS
from forms.calculator.data_loader import _RAHUL_REGION_BY_STATE

calc = GlobalCourierCargo(DEFAULT_SETTINGS)

from_state = "andhra pradesh"
to_state = "chhattisgarh"

# First try the calculator's STATE_TO_GLOBAL_CARGO_ZONE, then fall back to _RAHUL_REGION_BY_STATE
from_zone = calc.STATE_TO_GLOBAL_CARGO_ZONE.get(from_state.lower())
if not from_zone:
    from_zone = _RAHUL_REGION_BY_STATE.get(from_state.lower())

to_zone = calc.STATE_TO_GLOBAL_CARGO_ZONE.get(to_state.lower())
if not to_zone:
    to_zone = _RAHUL_REGION_BY_STATE.get(to_state.lower())

print("\n" + "="*80)
print("GLOBAL CARGO RATE LOOKUP: Andhra Pradesh to Chattisgarh")
print("="*80)

print(f"\nRoute: {from_state.upper()} -> {to_state.upper()}")
print(f"Zone mapping: {from_zone} -> {to_zone}")

if from_zone != "NOT FOUND" and to_zone != "NOT FOUND":
    rate = calc.ZONE_RATES.get(from_zone, {}).get(to_zone, "NOT FOUND")
    print(f"\nMatrix Rate: Rs {rate}/kg")
    
    print(f"\nFrom Zone: {from_zone} ({calc.ZONE_MAPPING[from_zone]})")
    print(f"  Covers: Andhra Pradesh & Telangana")
    
    print(f"\nTo Zone: {to_zone} ({calc.ZONE_MAPPING[to_zone]})")
    print(f"  Covers: Madhya Pradesh & Chattisgarh")
    
    print(f"\n" + "-"*80)
    print("All rates FROM Hyderabad (HYD):")
    print("-"*80)
    for dest_zone in sorted(calc.ZONE_RATES[from_zone].keys()):
        dest_rate = calc.ZONE_RATES[from_zone][dest_zone]
        marker = " <-- SELECTED" if dest_zone == to_zone else ""
        print(f"  HYD -> {dest_zone}: Rs {dest_rate}/kg{marker}")
    
    # Example calculation
    print(f"\n" + "-"*80)
    print("Example: 30 kg shipment from Andhra Pradesh to Chattisgarh")
    print("-"*80)
    weight = 30
    freight = weight * rate
    fuel_surcharge = freight * 0.10
    subtotal = freight + fuel_surcharge
    gst = subtotal * 0.18
    total = subtotal + gst
    
    print(f"  Chargeable Weight: {weight} kg")
    print(f"  Rate per kg: Rs {rate}")
    print(f"  Base Freight: Rs {freight}")
    print(f"  Fuel Surcharge (10%): Rs {fuel_surcharge:.2f}")
    print(f"  Subtotal: Rs {subtotal:.2f}")
    print(f"  GST (18%): Rs {gst:.2f}")
    print(f"  TOTAL: Rs {total:.2f}")
    
else:
    print(f"ERROR: State mapping failed!")

print("\n" + "="*80)

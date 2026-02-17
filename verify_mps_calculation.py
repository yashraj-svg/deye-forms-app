#!/usr/bin/env python
"""
Verify MPS weight slab calculation for 73kg shipment to SPL (Kerala)
Based on user's MPS rate card
"""

print("=" * 80)
print("MPS WEIGHT SLAB PRICING VERIFICATION")
print("=" * 80)

# User's MPS rates for SPL zone (Kerala)
mps_spl_rates = {
    "10kg": 376,      # First 10kg
    "add_1kg": 32     # Each additional 1kg
}

shipment_weight = 73  # kg
lr_charge = 25  # Rupees

print(f"\nShipment Weight: {shipment_weight} kg")
print(f"Destination Zone: SPL (Kerala - out of delivery area)")
print(f"\nMPS Rate Card (per user):")
print(f"  First 10kg: ₹{mps_spl_rates['10kg']}")
print(f"  Each Additional 1kg: ₹{mps_spl_rates['add_1kg']}")

# Calculate base freight using weight slab logic
if shipment_weight <= 10:
    base_freight = mps_spl_rates["10kg"]
    print(f"\nCalculation:")
    print(f"  Weight ({shipment_weight}kg) ≤ 10kg")
    print(f"  Base Freight = ₹{base_freight}")
else:
    additional_kg = shipment_weight - 10
    base_freight = mps_spl_rates["10kg"] + (additional_kg * mps_spl_rates["add_1kg"])
    print(f"\nCalculation:")
    print(f"  First 10kg: ₹{mps_spl_rates['10kg']}")
    print(f"  Additional kg: {additional_kg}kg × ₹{mps_spl_rates['add_1kg']}/kg = ₹{additional_kg * mps_spl_rates['add_1kg']}")
    print(f"  Base Freight = ₹{mps_spl_rates['10kg']} + ₹{additional_kg * mps_spl_rates['add_1kg']} = ₹{base_freight}")

# Add surcharges
total_before_surcharge = base_freight
surcharges = {
    "LR Charge": lr_charge
}

print(f"\nSurcharges:")
for charge, amount in surcharges.items():
    print(f"  {charge}: ₹{amount}")

# Final total
total = base_freight + lr_charge

print(f"\n" + "=" * 80)
print(f"BASE FREIGHT: ₹{base_freight}")
print(f"LR CHARGE: ₹{lr_charge}")
print(f"─────────────────")
print(f"TOTAL (inclusive of GST & FSC): ₹{total}")
print("=" * 80)

print(f"\nNote: MPS rates are inclusive of GST & FSC (per user's rate table)")
print(f"MPS does NOT charge ODA fee even for ODA locations")

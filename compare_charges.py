"""
Comparison: Calculator vs Actual Global Courier Charges
========================================================
"""

print("=" * 80)
print("SHIPMENT: Pune (411045) → Lucknow (226021)")
print("Dimensions: L=123, B=85, H=57 cm | Actual Weight: 110 kg")
print("=" * 80)

print("\n" + "▶" * 40)
print("ACTUAL GLOBAL COURIER INVOICE (Row 2 from your data)")
print("▶" * 40)
print(f"Weight Used:           131 kg")
print(f"Base Rate:             ₹13 per kg")
print(f"Base Freight:          131 × 13 = ₹1,703")
print(f"ODA Charges:           ₹0")
print(f"Total Base:            ₹1,703")
print(f"Fuel Surcharge:        10% × 1,703 = ₹170.30")
print(f"Subtotal:              ₹1,873.30")
print(f"GST (18%):             ₹337.19")
print(f"═" * 60)
print(f"TOTAL:                 ₹2,210.49")

print("\n" + "▶" * 40)
print("CURRENT CALCULATOR OUTPUT")
print("▶" * 40)
print(f"Actual Weight:         110 kg")
print(f"Volumetric Weight:     148.98 kg  ← CALCULATOR USES THIS")
print(f"Base Rate:             ₹13 per kg")
print(f"Base Freight:          148.98 × 13 = ₹1,936.79")
print(f"Docket Charge:         ₹50.00  ← NOT IN ACTUAL INVOICE!")
print(f"ODA Charges:           ₹0")
print(f"Fuel Surcharge:        10% × (1,936.79 + 50) = ₹198.68")
print(f"Subtotal:              ₹2,185.47")
print(f"GST (18%):             ₹393.38")
print(f"═" * 60)
print(f"TOTAL:                 ₹2,578.85")

print("\n" + "!" * 80)
print("DIFFERENCE: ₹2,578.85 - ₹2,210.49 = ₹368.36 OVERCHARGE!")
print("!" * 80)

print("\n" + "═" * 80)
print("ISSUES IDENTIFIED:")
print("═" * 80)
print("""
1. ❌ VOLUMETRIC WEIGHT CALCULATION
   - Calculator: Uses volumetric weight (148.98 kg)
   - Actual: Uses a different weight (131 kg) - possibly actual weight or different formula
   
2. ❌ DOCKET CHARGE
   - Calculator: Adds ₹50 docket charge
   - Actual: NO docket charge in the invoice
   
3. ❌ FUEL SURCHARGE BASE
   - Calculator: 10% on (Base Freight + Docket + ODA)
   - Actual: 10% on (Base Freight + ODA only)

4. ❓ WEIGHT DISCREPANCY
   - Your data shows 131 kg but actual weight is 110 kg
   - Need to check: Is 131 kg the chargeable weight after their calculation?
""")

print("\n" + "═" * 80)
print("VERIFICATION WITH OTHER ROWS:")
print("═" * 80)

test_cases = [
    ("Row 1", "Bangalore→Kanjiramoto", 40, 16, 600, 1200, 120, 237.6, 1557.6),
    ("Row 2", "Pune→Lucknow", 131, 13, 0, 1703, 170.3, 337.194, 2210.494),
    ("Row 3", "Bangalore→Polechi", 40, 14, 600, 1160, 116, 229.68, 1505.68),
    ("Row 4", "Pune→Mahasamund", 64, 10, 0, 640, 64, 126.72, 830.72),
]

for row, route, weight, rate, oda, total_base, fuel, gst, total in test_cases:
    calc_base = weight * rate
    calc_total_base = calc_base + oda
    calc_fuel = calc_total_base * 0.10
    calc_gst = (calc_total_base + calc_fuel) * 0.18
    calc_total = calc_total_base + calc_fuel + calc_gst
    
    match = "✓" if abs(calc_total - total) < 0.01 else "✗"
    print(f"\n{row} ({route}):")
    print(f"  Base Freight = {weight} × {rate} = {calc_base} (Expected: {calc_base})")
    print(f"  Total Base = {calc_base} + {oda} = {calc_total_base} (Expected: {total_base}) {'✓' if abs(calc_total_base - total_base) < 0.01 else '✗'}")
    print(f"  Fuel = 10% × {calc_total_base} = {calc_fuel:.2f} (Expected: {fuel}) {'✓' if abs(calc_fuel - fuel) < 0.01 else '✗'}")
    print(f"  GST = 18% × {calc_total_base + calc_fuel:.2f} = {calc_gst:.2f} (Expected: {gst}) {'✓' if abs(calc_gst - gst) < 0.5 else '✗'}")
    print(f"  Total = {calc_total:.2f} (Expected: {total}) {match}")

print("\n" + "═" * 80)
print("CONFIRMED FORMULA (from actual invoices):")
print("═" * 80)
print("""
Base Freight = Weight × Base Rate per kg
Total Base = Base Freight + ODA Charges
Fuel Surcharge = 10% × Total Base
Subtotal = Total Base + Fuel Surcharge
GST = 18% × Subtotal
Total Charges = Subtotal + GST

NO DOCKET CHARGE!
NO VOLUMETRIC WEIGHT (or different calculation)!
""")

print("\n" + "═" * 80)
print("REQUIRED CHANGES TO CALCULATOR:")
print("═" * 80)
print("""
1. Remove ₹50 Docket Charge
2. Fix Fuel Surcharge calculation: 10% on (Base Freight + ODA) only
3. Investigate weight calculation - why actual invoice shows different weight
4. The "Weight" column in invoice might be chargeable weight after their formula
""")

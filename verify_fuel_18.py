"""
Verify Safexpress Fuel Surcharge @ 18%
======================================
"""

print("Testing Fuel Surcharge = 18% × (Basic + Waybill + Value + UCC + SFXTN)\n")

print("=" * 80)
print("Invoice #1: Vasai (401201)")
print("=" * 80)
base1 = 180 + 150 + 100 + 100 + 0
fuel1_calc = base1 * 0.18
print(f"Base for Fuel = 180 + 150 + 100 + 100 + 0 = ₹{base1}")
print(f"Fuel @ 18% = ₹{base1} × 18% = ₹{fuel1_calc:.2f}")
print(f"Actual Fuel = ₹170")
print(f"Match: {'✓' if abs(fuel1_calc - 170) < 1 else '✗'}")

print("\n" + "=" * 80)
print("Invoice #2: Unnao (209859)")
print("=" * 80)
base2 = 1200 + 150 + 100 + 0 + 1500
fuel2_calc = base2 * 0.18
print(f"Base for Fuel = 1200 + 150 + 100 + 0 + 1500 = ₹{base2}")
print(f"Fuel @ 18% = ₹{base2} × 18% = ₹{fuel2_calc:.2f}")
print(f"Actual Fuel = ₹295")
print(f"Match: {'✓' if abs(fuel2_calc - 295) < 1 else '✗'}")

print("\n" + "=" * 80)
print("Testing with 10% (current calculator setting):")
print("=" * 80)
print(f"Invoice #1: ₹{base1} × 10% = ₹{base1 * 0.10:.2f} (Actual: 170) {'✓' if abs(base1 * 0.10 - 170) < 1 else '✗'}")
print(f"Invoice #2: ₹{base2} × 10% = ₹{base2 * 0.10:.2f} (Actual: 295) {'✓' if abs(base2 * 0.10 - 295) < 1 else '✗'}")

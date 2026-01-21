"""
Detailed Safexpress Invoice #1 Analysis - Fuel Surcharge Issue
==============================================================
"""

print("=" * 80)
print("INVESTIGATING FUEL SURCHARGE DISCREPANCY - INVOICE #1")
print("=" * 80)

print("\n📋 INVOICE #1 DATA:")
print("   Charged Weight:    30 kg")
print("   Basic Freight:     ₹180")
print("   Waybill:           ₹150")
print("   Value Surcharge:   ₹100")
print("   UCC:               ₹100")
print("   SFXTN (ODA):       ₹0")
print("   OSC:               ₹0")
print("   Fuel Surcharge:    ₹170  ← ACTUAL")

print("\n" + "─" * 80)
print("TESTING DIFFERENT FUEL SURCHARGE FORMULAS:")
print("─" * 80)

# Test 1: 10% of all charges
subtotal1 = 180 + 150 + 100 + 100 + 0 + 0
fuel1 = subtotal1 * 0.10
print(f"\n1️⃣  10% of all charges:")
print(f"   {subtotal1} × 10% = ₹{fuel1:.2f} ✗ (Expected: 170)")

# Test 2: Different fuel percentage
fuel_percent = 170 / subtotal1
print(f"\n2️⃣  Actual fuel percentage:")
print(f"   {170} ÷ {subtotal1} = {fuel_percent:.2%}")

# Test 3: Maybe fuel is on total + fuel itself?
# Total Freight = 770, so before fuel = 600
before_fuel = 770 - 170
print(f"\n3️⃣  Working backwards from total freight:")
print(f"   Total Freight (770) - Fuel (170) = {before_fuel}")
print(f"   But Basic + Waybill + Value + UCC = {180 + 150 + 100 + 100} ≠ {before_fuel}")

# Test 4: Maybe there's a hidden charge?
hidden = before_fuel - subtotal1
print(f"\n4️⃣  Is there a hidden charge?")
print(f"   {before_fuel} - {subtotal1} = {hidden}")
print(f"   {hidden} / 30 kg = ₹{hidden/30:.2f} per kg")

# Test 5: Fuel on Basic Freight only?
fuel_on_basic = 180 * 0.10
print(f"\n5️⃣  10% on Basic Freight only:")
print(f"   {180} × 10% = ₹{fuel_on_basic:.2f} ✗")

# Test 6: Could fuel be tiered or flat?
print(f"\n6️⃣  Could it be a flat/minimum fuel charge?")
print(f"   Fuel = ₹170 might be: MAX(10% × charges, minimum_fuel)")

# Test 7: Percentage calculation
print(f"\n7️⃣  If fuel is calculated differently:")
print(f"   Let's check if Basic Freight is calculated correctly")
print(f"   ₹180 ÷ 30 kg = ₹{180/30:.2f} per kg")

# Test 8: Maybe fuel is 10% on (Basic + some multiplier?)
print(f"\n8️⃣  Testing various multipliers:")
for mult in [1.5, 2.0, 2.5, 3.0, 3.5]:
    test_base = 180 * mult
    test_fuel = test_base * 0.10
    if abs(test_fuel - 170) < 1:
        print(f"   ✓ {180} × {mult} × 10% = ₹{test_fuel:.2f}")
        break
    else:
        print(f"   ✗ {180} × {mult} × 10% = ₹{test_fuel:.2f}")

# Test 9: Could OSC be hidden?
print(f"\n9️⃣  Could there be hidden OSC (Other State Charges)?")
print(f"   If OSC exists: Basic + Waybill + Value + UCC + OSC = ?")
print(f"   And Fuel = 10% × (Basic + Waybill + Value + UCC + OSC)")
print(f"   Then: 170 = 0.10 × (530 + OSC)")
osc_needed = (170 / 0.10) - 530
print(f"   OSC needed = ₹{osc_needed:.2f}")
print(f"   OSC per kg = ₹{osc_needed/30:.2f} per kg")

print("\n" + "=" * 80)
print("HYPOTHESIS:")
print("=" * 80)
print(f"""
The invoice shows OSC = 0, but there might be:

1. A hidden state charge of ₹{osc_needed:.2f} (₹{osc_needed/30:.2f} per kg)
2. A different fuel surcharge percentage ({fuel_percent:.2%} instead of 10%)
3. A minimum fuel charge policy
4. Basic Freight might include additional charges not shown separately

To verify, need to know:
- Origin and destination states for Invoice #1
- Complete rate card for that route
- If Vasai (401201) has special charges
""")

print("\n" + "=" * 80)
print("INVOICE #2 VERIFICATION (which matched perfectly):")
print("=" * 80)
print("""
Invoice #2 calculations were PERFECT:
- Fuel = 10% × (1200 + 150 + 100 + 1500) = 295 ✓
- This confirms the formula works when all charges are visible

Therefore, Invoice #1 likely has:
- Hidden charges not shown in the table you provided, OR
- Different fuel percentage for certain routes, OR
- Basic freight is incorrectly reported
""")

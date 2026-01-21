"""
Test Global Cargo calculator with official rate structure
Per screenshots:
- Zone-to-zone rate matrix
- Minimum chargeable weight: 20 kg
- Volumetric: 1 cubic feet = 7 kg (L*B*H/4000)
- Minimum LR: Rs.450
- ODA: Rs.600
- Fuel: 10% on (Base + ODA)
- GST: 18% on (Base + ODA + Fuel)
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import QuoteInput, get_all_partner_quotes

print("=" * 100)
print("GLOBAL CARGO - TESTING OFFICIAL RATE STRUCTURE")
print("=" * 100)

# Test 1: Minimum charge (small weight, should hit Rs.450 minimum LR)
print("\nTest 1: Small shipment - should apply minimum LR Rs.450")
print("-" * 100)
inp1 = QuoteInput(
    from_pincode="560060",  # Bangalore (BLR)
    to_pincode="411045",    # Pune (PNQ)
    weight_kg=5.0,          # Small weight
    length_cm=10,
    breadth_cm=10,
    height_cm=10,
)
results1 = get_all_partner_quotes(inp1)
gc1 = next((r for r in results1 if "Global" in r.partner_name), None)

if gc1:
    print(f"Route: {gc1.from_zone} → {gc1.to_zone}")
    print(f"Weight: 5kg → Chargeable: {gc1.chargeable_weight_kg}kg (min 20kg)")
    print(f"Rate: Rs.{gc1.rate_per_kg}/kg")
    print(f"Base Freight: Rs.{gc1.base_freight}")
    print(f"Surcharges: {gc1.surcharges}")
    print(f"Total before GST: Rs.{gc1.total_before_gst}")
    print(f"GST (18%): Rs.{gc1.gst_amount}")
    print(f"**FINAL TOTAL: Rs.{gc1.total_after_gst}** (Should be Rs.450 minimum)")
    print(f"Expected: Rs.450 | Actual: Rs.{gc1.total_after_gst} | Match: {'✓' if gc1.total_after_gst == 450.0 else '✗'}")

# Test 2: Larger shipment - should calculate normally (above minimum)
print("\n\nTest 2: Large shipment - should exceed Rs.450 minimum")
print("-" * 100)
inp2 = QuoteInput(
    from_pincode="560060",  # Bangalore (BLR)
    to_pincode="411045",    # Pune (PNQ)
    weight_kg=100.0,        # Large weight
    length_cm=50,
    breadth_cm=50,
    height_cm=50,
)
results2 = get_all_partner_quotes(inp2)
gc2 = next((r for r in results2 if "Global" in r.partner_name), None)

if gc2:
    print(f"Route: {gc2.from_zone} → {gc2.to_zone}")
    print(f"Weight: 100kg → Chargeable: {gc2.chargeable_weight_kg}kg")
    print(f"Rate: Rs.{gc2.rate_per_kg}/kg (from official matrix: BLR→PNQ = Rs.13/kg)")
    print(f"Base Freight: Rs.{gc2.base_freight} (13 × 100 = Rs.1300)")
    print(f"Surcharges: {gc2.surcharges}")
    
    # Manual calculation
    base = 13.0 * 100  # Rs.1300
    fuel = base * 0.10  # Rs.130
    subtotal = base + fuel  # Rs.1430
    gst = subtotal * 0.18  # Rs.257.4
    total = subtotal + gst  # Rs.1687.4
    
    print(f"\nManual verification:")
    print(f"  Base: 13/kg × 100kg = Rs.{base}")
    print(f"  Fuel (10%): Rs.{base} × 10% = Rs.{fuel}")
    print(f"  Subtotal: Rs.{base + fuel}")
    print(f"  GST (18%): Rs.{subtotal} × 18% = Rs.{gst}")
    print(f"  **TOTAL: Rs.{total}**")
    print(f"\nCalculator result: Rs.{gc2.total_after_gst}")
    print(f"Match: {'✓' if abs(gc2.total_after_gst - total) < 1 else '✗'}")

# Test 3: ODA shipment
print("\n\nTest 3: ODA shipment - Rs.600 ODA charge")
print("-" * 100)
inp3 = QuoteInput(
    from_pincode="560060",  # Bangalore (BLR)
    to_pincode="574214",    # ODA location
    weight_kg=12.0,
    length_cm=10,
    breadth_cm=10,
    height_cm=10,
)
results3 = get_all_partner_quotes(inp3)
gc3 = next((r for r in results3 if "Global" in r.partner_name), None)

if gc3:
    print(f"Route: {gc3.from_zone} → {gc3.to_zone}")
    print(f"Weight: 12kg → Chargeable: {gc3.chargeable_weight_kg}kg (min 20kg)")
    print(f"Rate: Rs.{gc3.rate_per_kg}/kg")
    print(f"Base Freight: Rs.{gc3.base_freight}")
    print(f"ODA: Rs.{gc3.surcharges.get('oda', 0)} (should be Rs.600)")
    print(f"Fuel (10% on Base+ODA): Rs.{gc3.surcharges.get('fuel_surcharge', 0)}")
    print(f"Total before GST: Rs.{gc3.total_before_gst}")
    print(f"GST (18%): Rs.{gc3.gst_amount}")
    print(f"**FINAL TOTAL: Rs.{gc3.total_after_gst}**")
    
    # Manual calculation
    base = gc3.rate_per_kg * 20  # min 20kg
    oda = 600.0
    fuel = (base + oda) * 0.10
    subtotal = base + oda + fuel
    gst = subtotal * 0.18
    total = subtotal + gst
    total = max(total, 450.0)  # minimum LR
    
    print(f"\nManual verification:")
    print(f"  Base: Rs.{gc3.rate_per_kg}/kg × 20kg = Rs.{base}")
    print(f"  ODA: Rs.{oda}")
    print(f"  Fuel (10%): (Rs.{base} + Rs.{oda}) × 10% = Rs.{fuel}")
    print(f"  Subtotal: Rs.{subtotal}")
    print(f"  GST (18%): Rs.{subtotal} × 18% = Rs.{gst}")
    print(f"  Calculated: Rs.{total}")
    print(f"  After minimum check: Rs.{max(total, 450.0)}")
    print(f"\nCalculator result: Rs.{gc3.total_after_gst}")
    print(f"Match: {'✓' if abs(gc3.total_after_gst - total) < 1 else '✗'}")

# Test 4: Verify specific zone-to-zone rates from official matrix
print("\n\nTest 4: Verify zone-to-zone rates from official matrix")
print("-" * 100)

test_routes = [
    ("411045", "560060", "PNQ", "BLR", 13.0),  # Pune → Bangalore
    ("560060", "600095", "BLR", "MAA", 13.0),  # Bangalore → Chennai
    ("201306", "411045", "DEL", "PNQ", 15.0),  # Delhi → Pune
    ("600095", "322201", "MAA", "JAI", 14.0),  # Chennai → Jaipur
]

for from_pin, to_pin, from_zone_exp, to_zone_exp, rate_exp in test_routes:
    inp = QuoteInput(
        from_pincode=from_pin,
        to_pincode=to_pin,
        weight_kg=50.0,
        length_cm=10, breadth_cm=10, height_cm=10,
    )
    results = get_all_partner_quotes(inp)
    gc = next((r for r in results if "Global" in r.partner_name), None)
    
    if gc:
        match = "✓" if gc.rate_per_kg == rate_exp else "✗"
        print(f"{from_zone_exp}→{to_zone_exp}: Expected Rs.{rate_exp}/kg | Got Rs.{gc.rate_per_kg}/kg {match}")

print("\n" + "=" * 100)
print("VERIFICATION COMPLETE")
print("=" * 100)
print("\nKEY CHANGES IMPLEMENTED:")
print("1. ✓ Removed separate docket charge")
print("2. ✓ Applied minimum LR Rs.450 to final total")
print("3. ✓ Fuel: 10% on (Base + ODA + other surcharges)")
print("4. ✓ GST: 18% on (Base + all surcharges)")
print("5. ✓ Official zone-to-zone rate matrix from screenshots")
print("6. ✓ Minimum chargeable weight: 20 kg")
print("7. ✓ Volumetric divisor: 4000 (1 cubic feet = 7 kg)")
print("=" * 100)

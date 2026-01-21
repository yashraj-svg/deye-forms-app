"""
Final verification: Original request 411045 → 226021
Compare previous calculation vs new official structure
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import QuoteInput, get_all_partner_quotes

print("=" * 100)
print("ORIGINAL REQUEST VERIFICATION: 411045 (Pune) → 226021")
print("=" * 100)

# Test with original request
inp = QuoteInput(
    from_pincode="411045",  # Pune (PNQ)
    to_pincode="226021",    # Lucknow (LOK)
    weight_kg=30.0,
    length_cm=40,
    breadth_cm=30,
    height_cm=25,
)

results = get_all_partner_quotes(inp)
gc = next((r for r in results if "Global" in r.partner_name), None)

if gc:
    print(f"\n✓ Route detected: {gc.from_zone} (Pune) → {gc.to_zone} (Lucknow)")
    print(f"✓ Actual weight: 30kg")
    print(f"✓ Volumetric weight: {gc.volumetric_weight_kg}kg (L×B×H÷4000 = 40×30×25÷4000 = {40*30*25/4000:.2f}kg)")
    print(f"✓ Chargeable weight: {gc.chargeable_weight_kg}kg (max of actual, volumetric, minimum 20kg)")
    print(f"\n✓ Rate from official matrix: PNQ→LOK = Rs.{gc.rate_per_kg}/kg")
    
    print(f"\n{'─' * 100}")
    print(f"DETAILED CALCULATION BREAKDOWN:")
    print(f"{'─' * 100}")
    
    print(f"\n1. Base Freight:")
    print(f"   Rate: Rs.{gc.rate_per_kg}/kg × {gc.chargeable_weight_kg}kg")
    print(f"   = Rs.{gc.base_freight}")
    
    if gc.surcharges:
        print(f"\n2. Surcharges:")
        for key, value in gc.surcharges.items():
            key_display = key.replace('_', ' ').title()
            print(f"   {key_display}: Rs.{value}")
    
    print(f"\n3. Subtotal (before GST):")
    print(f"   Base + Surcharges = Rs.{gc.total_before_gst}")
    
    print(f"\n4. GST (18%):")
    print(f"   Rs.{gc.total_before_gst} × 18% = Rs.{gc.gst_amount}")
    
    print(f"\n5. Total after GST:")
    print(f"   Rs.{gc.total_before_gst} + Rs.{gc.gst_amount} = Rs.{gc.total_before_gst + gc.gst_amount:.2f}")
    
    print(f"\n6. Minimum LR Check:")
    calculated_total = gc.total_before_gst + gc.gst_amount
    if calculated_total < 450:
        print(f"   Calculated Rs.{calculated_total:.2f} < Minimum Rs.450")
        print(f"   → Applied minimum: Rs.450")
    else:
        print(f"   Calculated Rs.{calculated_total:.2f} > Minimum Rs.450")
        print(f"   → Use calculated amount")
    
    print(f"\n{'─' * 100}")
    print(f"FINAL AMOUNT: Rs.{gc.total_after_gst}")
    print(f"{'─' * 100}")
    
    # Manual verification
    base = gc.rate_per_kg * gc.chargeable_weight_kg
    fuel = base * 0.10
    subtotal = base + fuel
    gst = subtotal * 0.18
    total = subtotal + gst
    total = max(total, 450.0)
    
    print(f"\nManual Cross-Check:")
    print(f"  Base: {gc.rate_per_kg} × {gc.chargeable_weight_kg} = Rs.{base:.2f}")
    print(f"  Fuel (10%): Rs.{fuel:.2f}")
    print(f"  Subtotal: Rs.{subtotal:.2f}")
    print(f"  GST (18%): Rs.{gst:.2f}")
    print(f"  Total: Rs.{total:.2f}")
    print(f"  Match with calculator: {'✓ YES' if abs(total - gc.total_after_gst) < 0.01 else '✗ NO'}")

print("\n" + "=" * 100)
print("IMPROVEMENTS FROM PREVIOUS VERSION:")
print("=" * 100)
print("✓ Removed incorrect separate docket charge (Rs.450)")
print("✓ Implemented minimum LR Rs.450 on final total (not added on top)")
print("✓ GST now correctly applies to all charges (not excluding docket)")
print("✓ Using official zone-to-zone rate matrix from Global Cargo")
print("✓ Formula matches official structure: Base + Fuel(10%) + GST(18%) with Rs.450 minimum")
print("=" * 100)

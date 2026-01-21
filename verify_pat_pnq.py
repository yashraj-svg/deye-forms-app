"""
Verify calculation for screenshot: 844124 → 411045, 111kg
User says actual Delhivery price is Rs.1887 but calculator shows Rs.2612.05
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import QuoteInput, get_all_partner_quotes

print("=" * 100)
print("VERIFYING: 844124 (Patna) → 411045 (Pune), 111kg")
print("User reports actual Delhivery price: Rs.1887")
print("Calculator showing: Rs.2612.05")
print("=" * 100)

# Test WITH reverse pickup and insurance (as shown in screenshot)
inp = QuoteInput(
    from_pincode="844124",  # Patna (PAT)
    to_pincode="411045",    # Pune (PNQ)
    weight_kg=111.0,
    length_cm=0,
    breadth_cm=0,
    height_cm=0,
    insured_value=1000.0,   # Rs.1000 insurance
    reverse_pickup=True,     # Checked in screenshot
)

results = get_all_partner_quotes(inp)
gc = next((r for r in results if "Global" in r.partner_name), None)

if gc:
    print(f"\nGLOBAL CARGO (with Reverse Pickup + Insurance):")
    print(f"{'-' * 100}")
    print(f"Route: {gc.from_zone} → {gc.to_zone}")
    print(f"Rate from official matrix: Rs.{gc.rate_per_kg}/kg")
    print(f"Chargeable weight: {gc.chargeable_weight_kg}kg")
    print(f"Base Freight: Rs.{gc.base_freight}")
    
    print(f"\nSurcharges:")
    for key, value in gc.surcharges.items():
        print(f"  {key.replace('_', ' ').title()}: Rs.{value}")
    
    print(f"\nGST (18%): Rs.{gc.gst_amount}")
    print(f"Calculator Total: Rs.{gc.total_after_gst}")
    
    print(f"\n{'-' * 100}")
    print(f"BREAKDOWN:")
    print(f"{'-' * 100}")
    print(f"Base: {gc.rate_per_kg} × {gc.chargeable_weight_kg} = Rs.{gc.base_freight}")
    
    reverse = gc.surcharges.get('reverse_pickup', 0)
    insurance = gc.surcharges.get('insurance', 0)
    fuel = gc.surcharges.get('fuel_surcharge', 0)
    
    if reverse:
        print(f"Reverse Pickup: Rs.{reverse}")
    if insurance:
        print(f"Insurance: Rs.{insurance}")
    
    base_for_fuel = gc.base_freight + reverse + insurance
    print(f"Fuel (10%): (Rs.{gc.base_freight} + Rs.{reverse} + Rs.{insurance}) × 10% = Rs.{fuel}")
    
    subtotal = gc.total_before_gst
    print(f"Subtotal: Rs.{subtotal}")
    print(f"GST (18%): Rs.{subtotal} × 18% = Rs.{gc.gst_amount}")
    print(f"Total: Rs.{gc.total_after_gst}")

# Now calculate what it SHOULD be per December billing
print(f"\n\n{'=' * 100}")
print(f"COMPARISON WITH DECEMBER ACTUAL BILLING:")
print(f"{'=' * 100}")

print(f"\nDecember Bill #15: 844124 → 411045, 111kg, Actual: Rs.1887")
print(f"\nReverse engineering December rate:")
print(f"  Formula: Total = Base × 1.298 + 450 (if minimum applies)")
print(f"  Rs.1887 = Base × 1.298")
print(f"  Base = (1887) / 1.298 = Rs.{1887/1.298:.2f}")
print(f"  Rate/kg = Rs.{1887/1.298/111:.2f}/kg")

print(f"\n{'-' * 100}")
print(f"DIFFERENCE ANALYSIS:")
print(f"{'-' * 100}")
print(f"Official Rate Card (PAT→PNQ): Rs.{gc.rate_per_kg}/kg")
print(f"December Actual Rate: Rs.{1887/1.298/111:.2f}/kg")
print(f"Difference: Rs.{gc.rate_per_kg - 1887/1.298/111:.2f}/kg higher in official card")

print(f"\nCalculator (with extras): Rs.{gc.total_after_gst}")
print(f"December Actual: Rs.1887")
print(f"Difference: Rs.{gc.total_after_gst - 1887:.2f}")

print(f"\n{'-' * 100}")
print(f"REASONS FOR DIFFERENCE:")
print(f"{'-' * 100}")
print(f"1. Official rate Rs.{gc.rate_per_kg}/kg vs December rate Rs.{1887/1.298/111:.2f}/kg")
print(f"2. Reverse Pickup: Rs.{reverse} (not in December bill)")
print(f"3. Insurance: Rs.{insurance} (not in December bill)")
print(f"4. December may have had promotional/discounted rates")

print(f"\n{'-' * 100}")
print(f"TO MATCH Rs.1887 EXACTLY:")
print(f"{'-' * 100}")
print(f"Option 1: Remove Reverse Pickup and Insurance from inputs")
print(f"Option 2: Use December rates instead of official rate card")
print(f"Option 3: Current setup uses official rates (as you chose Option A)")
print("=" * 100)

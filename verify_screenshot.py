"""
Verify the exact calculation shown in the screenshot
From: 560060 → To: 574214, Weight: 12kg, Insured Value: Rs.10000
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import QuoteInput, get_all_partner_quotes

print("=" * 100)
print("VERIFYING SCREENSHOT CALCULATION")
print("From: 560060 (Bangalore) → To: 574214 (ODA location)")
print("Weight: 12kg, Insured Value: Rs.10,000")
print("=" * 100)

inp = QuoteInput(
    from_pincode="560060",
    to_pincode="574214",
    weight_kg=12.0,
    length_cm=0,
    breadth_cm=0,
    height_cm=0,
    insured_value=10000.0,  # This is the key difference!
)

results = get_all_partner_quotes(inp)

for r in results:
    print(f"\n{'-' * 100}")
    print(f"{r.partner_name}")
    print(f"{'-' * 100}")
    print(f"Route: {r.from_zone} → {r.to_zone}")
    print(f"Chargeable Weight: {r.chargeable_weight_kg}kg")
    print(f"Base Freight: Rs.{r.base_freight}")
    
    if r.surcharges:
        print(f"\nSurcharges:")
        for key, value in r.surcharges.items():
            print(f"  {key.replace('_', ' ').title()}: Rs.{value}")
    
    print(f"\nGST (18%): Rs.{r.gst_amount}")
    print(f"TOTAL: Rs.{r.total_after_gst}")
    
    # Detailed breakdown for Global Cargo
    if "Global" in r.partner_name:
        print(f"\n*** GLOBAL CARGO DETAILED BREAKDOWN ***")
        print(f"Step 1: Base = Rs.10/kg × 20kg (min) = Rs.{r.base_freight}")
        
        oda = r.surcharges.get('oda', 0)
        insurance = r.surcharges.get('insurance', 0)
        fuel = r.surcharges.get('fuel_surcharge', 0)
        
        print(f"Step 2: ODA charge = Rs.{oda}")
        print(f"Step 3: Insurance (Rs.10,000 × 0.2% or min Rs.100) = Rs.{insurance}")
        print(f"Step 4: Fuel (10% on Base+ODA+Insurance) = (Rs.{r.base_freight}+Rs.{oda}+Rs.{insurance}) × 10% = Rs.{fuel}")
        
        subtotal = r.base_freight + sum(r.surcharges.values())
        print(f"Step 5: Subtotal = Rs.{r.base_freight} + Rs.{oda} + Rs.{insurance} + Rs.{fuel} = Rs.{subtotal}")
        print(f"Step 6: GST (18%) = Rs.{subtotal} × 18% = Rs.{r.gst_amount}")
        print(f"Step 7: Total = Rs.{subtotal} + Rs.{r.gst_amount} = Rs.{r.total_after_gst}")
        print(f"Step 8: Minimum LR check: max(Rs.{r.total_after_gst}, Rs.450) = Rs.{r.total_after_gst}")
        
        # Compare with screenshot
        print(f"\n*** COMPARISON WITH SCREENSHOT ***")
        screenshot_total = 1168.20
        diff = abs(r.total_after_gst - screenshot_total)
        
        if diff < 0.5:
            print(f"Calculator: Rs.{r.total_after_gst}")
            print(f"Screenshot: Rs.{screenshot_total}")
            print(f"Match: YES (diff Rs.{diff:.2f})")
        else:
            print(f"Calculator: Rs.{r.total_after_gst}")
            print(f"Screenshot: Rs.{screenshot_total}")
            print(f"Match: NO (diff Rs.{diff:.2f})")

print("\n" + "=" * 100)

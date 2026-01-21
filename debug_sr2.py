"""
Detailed breakdown for SR 2 to understand the mismatch
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import QuoteInput, get_all_partner_quotes

# SR 2: Pune (411045) → Lucknow (226021), 131kg @ ₹13/kg
inp = QuoteInput(
    from_pincode="411045",
    to_pincode="226021",
    weight_kg=131,
    length_cm=0,
    breadth_cm=0,
    height_cm=0,
)

results = get_all_partner_quotes(inp)
global_result = next((r for r in results if "Global" in r.partner_name), None)

print("SR 2: Pune → Lucknow, 131kg")
print("=" * 60)
print("\nINVOICE:")
print(f"  Base Rate: ₹13/kg")
print(f"  Weight: 131kg")
print(f"  Base Freight: 13 × 131 = ₹1703.00")
print(f"  ODA: ₹0")
print(f"  Docket: ₹50")
print(f"  Fuel SC (10%): 10% × 1703 = ₹170.30")
print(f"  Subtotal before GST: 1703 + 50 + 170.30 = ₹1923.30")
print(f"  GST (18%): 18% × 1923.30 = ₹346.19")
print(f"  Total: 1923.30 + 346.19 = ₹2269.49")
print(f"  Invoice Total: ₹2260.49")
print(f"  Difference: ₹9.00")

print("\nCALCULATOR:")
print(f"  Rate: ₹{global_result.rate_per_kg:.2f}/kg")
print(f"  Chargeable Weight: {global_result.chargeable_weight_kg:.2f}kg")
print(f"  Base Freight: ₹{global_result.base_freight:.2f}")
print(f"  ODA: ₹{global_result.surcharges.get('oda', 0):.2f}")
print(f"  Docket: ₹{global_result.surcharges.get('docket', 0):.2f}")
print(f"  Fuel SC: ₹{global_result.surcharges.get('fuel_surcharge', 0):.2f}")
print(f"  Total before GST: ₹{global_result.total_before_gst:.2f}")
print(f"  GST: ₹{global_result.gst_amount:.2f}")
print(f"  Total: ₹{global_result.total_after_gst:.2f}")

# Manual calculation
base = 13 * 131
fuel = base * 0.10
subtotal = base + 50 + fuel
gst = subtotal * 0.18
total = subtotal + gst

print("\nMANUAL CALCULATION:")
print(f"  Base: 13 × 131 = ₹{base:.2f}")
print(f"  Fuel: 10% × {base} = ₹{fuel:.2f}")
print(f"  Subtotal: {base} + 50 + {fuel} = ₹{subtotal:.2f}")
print(f"  GST: 18% × {subtotal} = ₹{gst:.2f}")
print(f"  Total: ₹{total:.2f}")

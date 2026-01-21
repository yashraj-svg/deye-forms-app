"""
Test new Global Cargo zone-based calculator
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import QuoteInput, get_all_partner_quotes

# Test cases from previous invoices
test_cases = [
    {"name": "Bangalore → Kanjiramattom (Kerala)", "from": "560060", "to": "686664", "weight": 40},
    {"name": "Pune → Lucknow", "from": "411045", "to": "226021", "weight": 131},
    {"name": "Bangalore → Mangaluru", "from": "560060", "to": "575006", "weight": 7},
    {"name": "Bangalore → Visakhapatnam", "from": "560060", "to": "531173", "weight": 11},
]

print("=" * 80)
print("TESTING NEW GLOBAL CARGO ZONE-BASED CALCULATOR")
print("=" * 80)
print("\nNew structure:")
print("  - 18 zones (AMB, JAI, DEL, AMD, PNQ, BOM, NAG, IDR, BLR, HYD, MAA, CJB, etc.)")
print("  - Zone-to-zone rate matrix")
print("  - Minimum weight: 20kg")
print("  - Minimum docket: Rs.450")
print("  - Volumetric: L*B*H/4000")
print("=" * 80)

for tc in test_cases:
    print(f"\n{tc['name']}")
    print(f"  {tc['from']} → {tc['to']}, {tc['weight']}kg")
    
    inp = QuoteInput(
        from_pincode=tc['from'],
        to_pincode=tc['to'],
        weight_kg=tc['weight'],
        length_cm=0,
        breadth_cm=0,
        height_cm=0,
    )
    
    try:
        results = get_all_partner_quotes(inp)
        global_result = next((r for r in results if "Global" in r.partner_name), None)
        
        if global_result:
            print(f"  Zone: {global_result.from_zone} → {global_result.to_zone}")
            print(f"  Rate: ₹{global_result.rate_per_kg:.2f}/kg")
            print(f"  Chargeable Weight: {global_result.chargeable_weight_kg:.0f}kg")
            print(f"  Base Freight: ₹{global_result.base_freight:.2f}")
            print(f"  ODA: ₹{global_result.surcharges.get('oda', 0):.2f}")
            print(f"  Docket: ₹{global_result.surcharges.get('docket', 0):.2f}")
            print(f"  Fuel SC: ₹{global_result.surcharges.get('fuel_surcharge', 0):.2f}")
            print(f"  GST: ₹{global_result.gst_amount:.2f}")
            print(f"  Total: ₹{global_result.total_after_gst:.2f}")
        else:
            print("  ❌ No Global Cargo quote found")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "=" * 80)

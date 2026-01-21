"""
Verify new Global Cargo invoices from attachment
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import QuoteInput, get_all_partner_quotes

# Invoice data from attachment
invoices = [
    {
        "sr": 1,
        "from_pin": "560060",
        "to_pin": "686664",
        "from_loc": "Bangalore",
        "to_loc": "Kanjiramattom",
        "base_rate": 16,
        "weight": 40,
        "oda": 600,
        "total_base": 1240,
        "docket": 50,
        "fuel_sc": 124,
        "gst": 245.52,
        "total": 1609.52,
    },
    {
        "sr": 2,
        "from_pin": "411045",
        "to_pin": "226021",
        "from_loc": "Pune",
        "to_loc": "Lucknow",
        "base_rate": 13,
        "weight": 131,
        "oda": 0,
        "total_base": 1703,
        "docket": 50,
        "fuel_sc": 170.3,
        "gst": 337.194,
        "total": 2210.494,
    },
    {
        "sr": 3,
        "from_pin": "560060",
        "to_pin": "642103",
        "from_loc": "Bangalore",
        "to_loc": "Pollachi",
        "base_rate": 14,
        "weight": 40,
        "oda": 600,
        "total_base": 1160,
        "docket": 50,
        "fuel_sc": 116,
        "gst": 229.68,
        "total": 1505.68,
    },
    {
        "sr": 4,
        "from_pin": "411045",
        "to_pin": "493449",
        "from_loc": "Pune",
        "to_loc": "Mahasamund",
        "base_rate": 10,
        "weight": 64,
        "oda": 0,
        "total_base": 640,
        "docket": 50,
        "fuel_sc": 64,
        "gst": 126.72,
        "total": 830.72,
    },
    {
        "sr": 5,
        "from_pin": "411045",
        "to_pin": "148101",
        "from_loc": "Pune",
        "to_loc": "Barnala",
        "base_rate": 13,
        "weight": 20,
        "oda": 0,
        "total_base": 260,
        "docket": 50,
        "fuel_sc": 26,
        "gst": 51.48,
        "total": 337.48,
    },
]

print("=" * 100)
print("GLOBAL CARGO INVOICE VERIFICATION - NEW SET")
print("=" * 100)

mismatches = []

for inv in invoices:
    print(f"\n{'='*100}")
    print(f"SR {inv['sr']}: {inv['from_loc']} ({inv['from_pin']}) → {inv['to_loc']} ({inv['to_pin']})")
    print(f"Weight: {inv['weight']}kg, Base Rate: ₹{inv['base_rate']}/kg")
    print("=" * 100)
    
    # Calculate using our calculator
    inp = QuoteInput(
        from_pincode=inv['from_pin'],
        to_pincode=inv['to_pin'],
        weight_kg=inv['weight'],
        length_cm=0,
        breadth_cm=0,
        height_cm=0,
    )
    
    results = get_all_partner_quotes(inp)
    global_result = next((r for r in results if "Global" in r.partner_name), None)
    
    if not global_result:
        print("❌ Global Cargo quote not found!")
        mismatches.append(f"SR {inv['sr']}: Quote not generated")
        continue
    
    # Manual calculation to verify invoice
    print(f"\nINVOICE BREAKDOWN:")
    base_freight_invoice = inv['base_rate'] * inv['weight']
    print(f"  Base Freight = {inv['base_rate']} × {inv['weight']} = ₹{base_freight_invoice:.2f}")
    print(f"  ODA Charges = ₹{inv['oda']:.2f}")
    print(f"  Total Base = ₹{inv['total_base']:.2f}")
    print(f"  Fuel SC (10%) = ₹{inv['fuel_sc']:.2f}")
    print(f"  Docket = ₹{inv['docket']:.2f}")
    
    # Verify fuel calculation
    expected_fuel = (inv['total_base']) * 0.10
    fuel_match = abs(expected_fuel - inv['fuel_sc']) < 0.5
    print(f"    Fuel check: 10% × {inv['total_base']} = ₹{expected_fuel:.2f} {'✓' if fuel_match else '❌'}")
    
    # Verify GST calculation
    # GST should be on (Total Base + Fuel SC) excluding docket
    gst_base = inv['total_base'] + inv['fuel_sc']
    expected_gst = gst_base * 0.18
    gst_match = abs(expected_gst - inv['gst']) < 0.5
    print(f"  GST (18%) = 18% × ({inv['total_base']} + {inv['fuel_sc']}) = ₹{expected_gst:.2f} {'✓' if gst_match else '❌'}")
    print(f"  Invoice GST = ₹{inv['gst']:.2f}")
    
    # Verify total
    expected_total = inv['total_base'] + inv['docket'] + inv['fuel_sc'] + inv['gst']
    total_match = abs(expected_total - inv['total']) < 0.5
    print(f"  Total = {inv['total_base']} + {inv['docket']} + {inv['fuel_sc']} + {inv['gst']} = ₹{expected_total:.2f}")
    print(f"  Invoice Total = ₹{inv['total']:.2f} {'✓' if total_match else '❌'}")
    
    print(f"\nCALCULATOR OUTPUT:")
    print(f"  From Zone: {global_result.from_zone}")
    print(f"  To Zone: {global_result.to_zone}")
    print(f"  Rate per kg: ₹{global_result.rate_per_kg:.2f}/kg")
    print(f"  Chargeable Weight: {global_result.chargeable_weight_kg:.2f}kg")
    print(f"  Base Freight: ₹{global_result.base_freight:.2f}")
    print(f"  ODA: ₹{global_result.surcharges.get('oda', 0):.2f}")
    print(f"  Docket: ₹{global_result.surcharges.get('docket', 0):.2f}")
    print(f"  Fuel SC: ₹{global_result.surcharges.get('fuel_surcharge', 0):.2f}")
    print(f"  GST: ₹{global_result.gst_amount:.2f}")
    print(f"  Total: ₹{global_result.total_after_gst:.2f}")
    
    print(f"\nCOMPARISON:")
    # Check base rate
    rate_match = abs(global_result.rate_per_kg - inv['base_rate']) < 0.1
    print(f"  Base Rate: Invoice ₹{inv['base_rate']}/kg vs Calc ₹{global_result.rate_per_kg:.2f}/kg {'✓' if rate_match else '❌ MISMATCH'}")
    
    # Check base freight
    base_match = abs(base_freight_invoice - global_result.base_freight) < 1.0
    print(f"  Base Freight: Invoice ₹{base_freight_invoice:.2f} vs Calc ₹{global_result.base_freight:.2f} {'✓' if base_match else '❌ MISMATCH'}")
    
    # Check ODA
    oda_match = abs(inv['oda'] - global_result.surcharges.get('oda', 0)) < 1.0
    print(f"  ODA: Invoice ₹{inv['oda']:.2f} vs Calc ₹{global_result.surcharges.get('oda', 0):.2f} {'✓' if oda_match else '❌ MISMATCH'}")
    
    # Check fuel
    calc_fuel = global_result.surcharges.get('fuel_surcharge', 0)
    fuel_calc_match = abs(inv['fuel_sc'] - calc_fuel) < 1.0
    print(f"  Fuel SC: Invoice ₹{inv['fuel_sc']:.2f} vs Calc ₹{calc_fuel:.2f} {'✓' if fuel_calc_match else '❌ MISMATCH'}")
    
    # Check GST
    gst_calc_match = abs(inv['gst'] - global_result.gst_amount) < 1.0
    print(f"  GST: Invoice ₹{inv['gst']:.2f} vs Calc ₹{global_result.gst_amount:.2f} {'✓' if gst_calc_match else '❌ MISMATCH'}")
    
    # Check total
    total_calc_match = abs(inv['total'] - global_result.total_after_gst) < 1.0
    print(f"  Total: Invoice ₹{inv['total']:.2f} vs Calc ₹{global_result.total_after_gst:.2f} {'✓' if total_calc_match else '❌ MISMATCH'}")
    
    if not (rate_match and base_match and oda_match and fuel_calc_match and gst_calc_match and total_calc_match):
        mismatches.append(f"SR {inv['sr']}")
        print(f"\n❌ OVERALL: MISMATCH DETECTED")
    else:
        print(f"\n✓ OVERALL: PERFECT MATCH")

print("\n" + "=" * 100)
if mismatches:
    print(f"❌ MISMATCHES FOUND IN: {', '.join(mismatches)}")
else:
    print("✓ ALL INVOICES MATCH PERFECTLY")
print("=" * 100)

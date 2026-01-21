"""
Analyze problematic invoices SR 1, 6-9
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import QuoteInput, get_all_partner_quotes

problems = [
    {"sr": 1, "from": "560060", "to": "686664", "loc": "Bangalore → Kanjiramattom", "weight": 40, "rate": 16, "base": 1240, "fuel": 124, "gst": 254.52, "total": 1668.52},
    {"sr": 6, "from": "560060", "to": "690544", "loc": "Bangalore → Kollam", "weight": 46, "rate": 16, "base": 736, "fuel": 73.6, "gst": 145.728, "total": 1005.328},
    {"sr": 7, "from": "560060", "to": "575006", "loc": "Bangalore → Mangaluru", "weight": 7, "rate": 10, "base": 70, "fuel": 13.86, "gst": 13.86, "total": 140.86},
    {"sr": 8, "from": "686691", "to": "560060", "loc": "Perumbavoor → Bangalore", "weight": 55, "rate": 16, "base": 880, "fuel": 88, "gst": 174.24, "total": 1192.24},
    {"sr": 9, "from": "560060", "to": "531173", "loc": "Bangalore → Visakhapatnam", "weight": 11, "rate": 14, "base": 154, "fuel": 15.4, "gst": 30.492, "total": 249.892},
]

print("Analyzing problematic invoices:\n")

for p in problems:
    print(f"SR {p['sr']}: {p['loc']}")
    print(f"  Weight: {p['weight']}kg @ ₹{p['rate']}/kg = ₹{p['base']}")
    
    # Check base calculation
    expected_base = p['rate'] * p['weight']
    if abs(expected_base - p['base']) > 0.5:
        print(f"  ❌ Base mismatch: {p['rate']} × {p['weight']} = ₹{expected_base}, invoice shows ₹{p['base']}")
    
    # Check fuel
    expected_fuel = p['base'] * 0.10
    if abs(expected_fuel - p['fuel']) > 0.5:
        print(f"  ❌ Fuel mismatch: 10% × {p['base']} = ₹{expected_fuel:.2f}, invoice shows ₹{p['fuel']}")
    
    # Check GST - with and without docket
    gst_with_docket = (p['base'] + p['fuel'] + 50) * 0.18
    gst_without_docket = (p['base'] + p['fuel']) * 0.18
    
    if abs(gst_with_docket - p['gst']) < 0.5:
        print(f"  ✓ GST includes docket: {gst_with_docket:.2f}")
    elif abs(gst_without_docket - p['gst']) < 0.5:
        print(f"  ✓ GST excludes docket: {gst_without_docket:.2f}")
    else:
        print(f"  ❌ GST neither: with={gst_with_docket:.2f}, without={gst_without_docket:.2f}, invoice={p['gst']}")
    
    # Run calculator
    inp = QuoteInput(from_pincode=p['from'], to_pincode=p['to'], weight_kg=p['weight'], length_cm=0, breadth_cm=0, height_cm=0)
    results = get_all_partner_quotes(inp)
    gr = next((r for r in results if "Global" in r.partner_name), None)
    if gr:
        print(f"  Calculator: ₹{gr.rate_per_kg:.0f}/kg, {gr.from_zone}→{gr.to_zone}, charge_wt={gr.chargeable_weight_kg:.0f}kg, total=₹{gr.total_after_gst:.2f}")
    print()

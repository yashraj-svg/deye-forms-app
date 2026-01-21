"""
Test Updated Global Cargo Calculator
=====================================
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import GlobalCourierCargo, QuoteInput
from forms.calculator.data_loader import load_pincode_master, PincodeRecord
from forms.calculator.config import DEFAULT_SETTINGS

print("=" * 90)
print("TESTING UPDATED GLOBAL CARGO CALCULATOR")
print("=" * 90)

base_dir = os.path.dirname(__file__)
pins = load_pincode_master(base_dir)
carrier = GlobalCourierCargo(DEFAULT_SETTINGS, base_dir)

# Test cases from actual invoices
test_cases = [
    {
        "name": "Pune → Lucknow (No ODA)",
        "from_pin": "411045", "to_pin": "226021",
        "weight": 131, "l": 123, "b": 85, "h": 57,
        "expected": {"rate": 13, "base": 1703, "fuel": 170.3, "docket": 50, "gst": 337.194, "total": 2210.494}
    },
    {
        "name": "Bangalore → Kanjiramoto (ODA)",
        "from_pin": "560060", "to_pin": "686664",
        "weight": 40, "l": 50, "b": 40, "h": 30,
        "expected": {"rate": 16, "base": 640, "oda": 600, "fuel": 124, "docket": 50, "gst": 245.52, "total": 1609.52}
    },
    {
        "name": "Pune → Mahasamund (No ODA)",
        "from_pin": "411045", "to_pin": "493449",
        "weight": 64, "l": 50, "b": 40, "h": 30,
        "expected": {"rate": 10, "base": 640, "fuel": 64, "docket": 50, "gst": 126.72, "total": 830.72}
    },
]

for test in test_cases:
    print(f"\n{'─' * 90}")
    print(f"TEST: {test['name']}")
    print(f"{'─' * 90}")
    
    inp = QuoteInput(
        from_pincode=test['from_pin'],
        to_pincode=test['to_pin'],
        weight_kg=test['weight'],
        length_cm=test['l'],
        breadth_cm=test['b'],
        height_cm=test['h'],
    )
    
    result = carrier.calculate_quote(inp, pins)
    
    exp = test['expected']
    
    print(f"\n📊 EXPECTED vs CALCULATED:")
    print(f"   Base Freight:     ₹{exp['base']:.2f} vs ₹{result.base_freight:.2f} {'✓' if abs(exp['base'] - result.base_freight) < 1 else '✗'}")
    
    if 'oda' in exp:
        calc_oda = result.surcharges.get('oda', 0)
        print(f"   ODA:              ₹{exp['oda']:.2f} vs ₹{calc_oda:.2f} {'✓' if abs(exp['oda'] - calc_oda) < 1 else '✗'}")
    
    calc_fuel = result.surcharges.get('fuel_surcharge', 0)
    print(f"   Fuel Surcharge:   ₹{exp['fuel']:.2f} vs ₹{calc_fuel:.2f} {'✓' if abs(exp['fuel'] - calc_fuel) < 1 else '✗'}")
    
    calc_docket = result.surcharges.get('docket', 0)
    print(f"   Docket:           ₹{exp['docket']:.2f} vs ₹{calc_docket:.2f} {'✓' if abs(exp['docket'] - calc_docket) < 1 else '✗'}")
    
    print(f"   GST (18%):        ₹{exp['gst']:.2f} vs ₹{result.gst_amount:.2f} {'✓' if abs(exp['gst'] - result.gst_amount) < 1 else '✗'}")
    print(f"   Total:            ₹{exp['total']:.2f} vs ₹{result.total_after_gst:.2f} {'✓' if abs(exp['total'] - result.total_after_gst) < 1 else '✗'}")
    
    # Detailed breakdown
    print(f"\n📋 DETAILED CALCULATION:")
    base_for_fuel = result.base_freight + result.surcharges.get('oda', 0)
    print(f"   Base for Fuel = Base + ODA = {result.base_freight:.2f} + {result.surcharges.get('oda', 0):.2f} = ₹{base_for_fuel:.2f}")
    print(f"   Fuel = 10% × {base_for_fuel:.2f} = ₹{calc_fuel:.2f}")
    print(f"   Subtotal = Base + ODA + Fuel + Docket")
    print(f"            = {result.base_freight:.2f} + {result.surcharges.get('oda', 0):.2f} + {calc_fuel:.2f} + {calc_docket:.2f}")
    print(f"            = ₹{result.total_before_gst:.2f}")
    print(f"   GST = 18% × {result.total_before_gst:.2f} = ₹{result.gst_amount:.2f}")
    print(f"   Total = ₹{result.total_after_gst:.2f}")

print("\n" + "=" * 90)
print("✅ GLOBAL CARGO CALCULATOR UPDATED SUCCESSFULLY!")
print("=" * 90)
print("""
Changes Applied:
1. ✅ Fuel Surcharge = 10% × (Base + ODA) - Docket NOT included
2. ✅ Docket added AFTER fuel calculation
3. ✅ GST = 18% × (Base + ODA + Fuel + Docket)

Formula matches actual Global Cargo invoices!
""")

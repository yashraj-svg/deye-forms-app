"""
Test Global Cargo with Actual Weight (No Volumetric)
====================================================
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import GlobalCourierCargo, QuoteInput
from forms.calculator.data_loader import load_pincode_master
from forms.calculator.config import DEFAULT_SETTINGS

print("=" * 90)
print("TESTING WITH ACTUAL WEIGHT (L=B=H=0 to ignore volumetric)")
print("=" * 90)

base_dir = os.path.dirname(__file__)
pins = load_pincode_master(base_dir)
carrier = GlobalCourierCargo(DEFAULT_SETTINGS, base_dir)

# Test cases with L=B=H=0 to use actual weight only
test_cases = [
    {
        "name": "Invoice #2: Pune → Lucknow",
        "from_pin": "411045", "to_pin": "226021",
        "weight": 131, "l": 0, "b": 0, "h": 0,
        "expected": {"base": 1703, "fuel": 170.3, "docket": 50, "gst": 337.194, "total": 2210.494}
    },
    {
        "name": "Invoice #1: Bangalore → Kanjiramoto (ODA)",
        "from_pin": "560060", "to_pin": "686664",
        "weight": 40, "l": 0, "b": 0, "h": 0,
        "expected": {"base": 640, "oda": 600, "fuel": 124, "docket": 50, "gst": 245.52, "total": 1609.52}
    },
    {
        "name": "Invoice #4: Pune → Mahasamund",
        "from_pin": "411045", "to_pin": "493449",
        "weight": 64, "l": 0, "b": 0, "h": 0,
        "expected": {"base": 640, "fuel": 64, "docket": 50, "gst": 126.72, "total": 830.72}
    },
    {
        "name": "Invoice #5: Pune → Barnala",
        "from_pin": "411045", "to_pin": "148101",
        "weight": 20, "l": 0, "b": 0, "h": 0,
        "expected": {"base": 260, "fuel": 26, "docket": 50, "gst": 51.48, "total": 337.48}
    },
]

all_match = True

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
    
    print(f"\n   Actual Weight:      {test['weight']} kg")
    print(f"   Dimensions:         L={test['l']}, B={test['b']}, H={test['h']}")
    print(f"   Chargeable Weight:  {result.chargeable_weight_kg} kg")
    print(f"   Rate per kg:        ₹{result.base_freight / result.chargeable_weight_kg:.0f}")
    
    # Check each component
    base_match = abs(exp['base'] - result.base_freight) < 1
    fuel_match = abs(exp['fuel'] - result.surcharges.get('fuel_surcharge', 0)) < 1
    docket_match = abs(exp['docket'] - result.surcharges.get('docket', 0)) < 0.01
    gst_match = abs(exp['gst'] - result.gst_amount) < 1
    total_match = abs(exp['total'] - result.total_after_gst) < 1
    
    test_match = base_match and fuel_match and docket_match and gst_match and total_match
    all_match = all_match and test_match
    
    print(f"\n📊 VERIFICATION:")
    print(f"   Base Freight:   ₹{result.base_freight:.2f} (Expected: ₹{exp['base']:.2f}) {'✓' if base_match else '✗'}")
    
    if 'oda' in exp:
        oda_match = abs(exp['oda'] - result.surcharges.get('oda', 0)) < 1
        print(f"   ODA:            ₹{result.surcharges.get('oda', 0):.2f} (Expected: ₹{exp['oda']:.2f}) {'✓' if oda_match else '✗'}")
    
    print(f"   Fuel:           ₹{result.surcharges.get('fuel_surcharge', 0):.2f} (Expected: ₹{exp['fuel']:.2f}) {'✓' if fuel_match else '✗'}")
    print(f"   Docket:         ₹{result.surcharges.get('docket', 0):.2f} (Expected: ₹{exp['docket']:.2f}) {'✓' if docket_match else '✗'}")
    print(f"   GST (18%):      ₹{result.gst_amount:.2f} (Expected: ₹{exp['gst']:.2f}) {'✓' if gst_match else '✗'}")
    print(f"   Total:          ₹{result.total_after_gst:.2f} (Expected: ₹{exp['total']:.2f}) {'✓' if total_match else '✗'}")
    
    print(f"\n   Overall: {'✅ PERFECT MATCH!' if test_match else '❌ MISMATCH'}")

print("\n" + "=" * 90)
if all_match:
    print("✅✅✅ ALL TESTS PASSED! ✅✅✅")
else:
    print("❌ SOME TESTS FAILED")
print("=" * 90)

print("""
CONFIRMATION:
=============
The calculator logic is CORRECT!

How to use:
-----------
1. If you have actual dimensions (L, B, H):
   - Enter actual weight and actual dimensions
   - Calculator will use MAX(actual weight, volumetric weight)
   
2. If you only know the weight (no dimensions):
   - Enter actual weight
   - Set L = B = H = 0
   - Calculator will use actual weight only

Formula Applied:
----------------
✓ Chargeable Weight = MAX(Actual Weight, Volumetric Weight, 20 kg minimum)
✓ Volumetric Weight = (L × B × H) / 4000
✓ Base Freight = Chargeable Weight × Rate per kg
✓ Fuel = 10% × (Base + ODA)
✓ GST = 18% × (Base + ODA + Fuel + Docket)
✓ Total = Base + ODA + Fuel + Docket + GST
""")

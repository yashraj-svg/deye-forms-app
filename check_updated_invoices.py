"""
Verify updated Global Cargo invoices (with docket included)
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.freight_calculator import QuoteInput, get_all_partner_quotes
import pathlib
from forms.calculator.data_loader import load_pincode_master

# Updated invoice data
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
        "gst": 254.52,
        "total": 1668.52,
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
        "total": 2260.494,
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
        "total": 1555.68,
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
        "total": 880.72,
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
        "total": 387.48,
    },
    {
        "sr": 6,
        "from_pin": "560060",
        "to_pin": "690544",
        "from_loc": "Bangalore",
        "to_loc": "Kollam",
        "base_rate": 16,
        "weight": 46,
        "oda": 0,
        "total_base": 736,
        "docket": 50,
        "fuel_sc": 73.6,
        "gst": 145.728,
        "total": 1005.328,
    },
    {
        "sr": 7,
        "from_pin": "560060",
        "to_pin": "575006",
        "from_loc": "Bangalore",
        "to_loc": "Mangaluru",
        "base_rate": 10,
        "weight": 7,
        "oda": 0,
        "total_base": 70,
        "docket": 50,
        "fuel_sc": 13.86,
        "gst": 13.86,
        "total": 140.86,
    },
    {
        "sr": 8,
        "from_pin": "686691",
        "to_pin": "560060",
        "from_loc": "Perumbavoor",
        "to_loc": "Bangalore",
        "base_rate": 16,
        "weight": 55,
        "oda": 0,
        "total_base": 880,
        "docket": 50,
        "fuel_sc": 88,
        "gst": 174.24,
        "total": 1192.24,
    },
    {
        "sr": 9,
        "from_pin": "560060",
        "to_pin": "531173",
        "from_loc": "Banglore",
        "to_loc": "Visakhapatnam",
        "base_rate": 14,
        "weight": 11,
        "oda": 0,
        "total_base": 154,
        "docket": 50,
        "fuel_sc": 15.4,
        "gst": 30.492,
        "total": 249.892,
    },
]

print("=" * 100)
print("CHECKING UPDATED GLOBAL CARGO INVOICES")
print("=" * 100)

# First, check for missing pincodes
base_dir = str(pathlib.Path(__file__).resolve().parents[0])
pins = load_pincode_master(base_dir)

missing_pincodes = []
all_pincodes = set()

for inv in invoices:
    all_pincodes.add(inv['from_pin'])
    all_pincodes.add(inv['to_pin'])

for pin in all_pincodes:
    if pin not in pins:
        missing_pincodes.append(pin)

if missing_pincodes:
    print(f"\n⚠️  WARNING: {len(missing_pincodes)} PINCODE(S) NOT FOUND IN DATABASE:")
    for pin in sorted(missing_pincodes):
        # Find which invoices use this pincode
        invoices_using = []
        for inv in invoices:
            if inv['from_pin'] == pin:
                invoices_using.append(f"SR{inv['sr']} From: {inv['from_loc']}")
            if inv['to_pin'] == pin:
                invoices_using.append(f"SR{inv['sr']} To: {inv['to_loc']}")
        print(f"  📍 {pin}: {', '.join(invoices_using)}")
    print("\n" + "=" * 100)
else:
    print("\n✓ All pincodes found in database\n")
    print("=" * 100)

# Analyze invoice format - check if docket is included in GST
print("\nANALYZING INVOICE FORMAT:")
sample = invoices[0]
print(f"\nSample (SR {sample['sr']}):")
print(f"  Base + ODA = {sample['total_base']}")
print(f"  Fuel SC = {sample['fuel_sc']}")
print(f"  Docket = {sample['docket']}")

# Check if GST includes docket
gst_with_docket = (sample['total_base'] + sample['fuel_sc'] + sample['docket']) * 0.18
gst_without_docket = (sample['total_base'] + sample['fuel_sc']) * 0.18

print(f"\n  GST if calculated WITH docket: {gst_with_docket:.2f}")
print(f"  GST if calculated WITHOUT docket: {gst_without_docket:.2f}")
print(f"  Invoice GST: {sample['gst']:.2f}")

if abs(gst_with_docket - sample['gst']) < 0.5:
    print(f"\n  ✓ These invoices INCLUDE DOCKET in GST calculation")
    docket_in_gst = True
elif abs(gst_without_docket - sample['gst']) < 0.5:
    print(f"\n  ✓ These invoices EXCLUDE DOCKET from GST calculation")
    docket_in_gst = False
else:
    print(f"\n  ❌ GST calculation doesn't match either pattern!")
    docket_in_gst = None

print("\n" + "=" * 100)
print("\nNOTE: Current calculator settings:")
print("  - docket_charge_global_cargo = 0.0 (docket NOT charged)")
print("  - GST excludes docket")
print("\nThese invoices show:")
print("  - docket_charge = ₹50 (docket IS charged)")
print(f"  - GST {'includes' if docket_in_gst else 'excludes'} docket")
print("\n⚠️  CALCULATOR SETTINGS NEED UPDATE FOR THESE INVOICES")
print("=" * 100)

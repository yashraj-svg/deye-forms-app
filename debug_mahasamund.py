"""
Debug Mahasamund region detection
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

base_dir = str(pathlib.Path(__file__).resolve().parents[0])
pins = load_pincode_master(base_dir)

print("Checking pincode 493449 (Mahasamund):")
pin_data = pins.get("493449")

if pin_data:
    print(f"  City: {pin_data.city}")
    print(f"  State: {pin_data.state}")
    print(f"  Global Cargo Region: {pin_data.global_courier_cargo_region}")
    print(f"  Is ODA: {pin_data.is_oda}")
else:
    print("  ❌ Not found in database")

print("\nRunning quote calculation:")
inp = QuoteInput(
    from_pincode="411045",
    to_pincode="493449",
    weight_kg=64,
    length_cm=0,
    breadth_cm=0,
    height_cm=0,
)

results = get_all_partner_quotes(inp, base_dir)
global_result = next((r for r in results if "Global" in r.partner_name), None)

if global_result:
    print(f"\nGlobal Cargo Quote:")
    print(f"  From Zone: {global_result.from_zone}")
    print(f"  To Zone: {global_result.to_zone}")
    print(f"  Rate per kg: ₹{global_result.rate_per_kg:.2f}/kg")
    print(f"  Rate Details: {global_result.rate_details}")

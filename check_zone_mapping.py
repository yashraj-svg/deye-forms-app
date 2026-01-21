"""
Check zone mapping for Lucknow
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

import pathlib
from forms.calculator.data_loader import load_pincode_master

base_dir = str(pathlib.Path(__file__).resolve().parents[0])
pins = load_pincode_master(base_dir)

test_pins = [
    ("226021", "Lucknow"),
    ("560060", "Bangalore"),
    ("411045", "Pune"),
    ("575006", "Mangaluru"),
    ("531173", "Visakhapatnam"),
]

print("Checking pincode to zone mapping:\n")
for pin, name in test_pins:
    pin_data = pins.get(pin)
    if pin_data:
        print(f"{pin} ({name}):")
        print(f"  City: {pin_data.city}")
        print(f"  State: {pin_data.state}")
        print(f"  Zone: {pin_data.global_cargo_region}")
    else:
        print(f"{pin} ({name}): NOT FOUND")
    print()

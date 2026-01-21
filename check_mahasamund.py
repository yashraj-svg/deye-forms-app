"""
Check region for Mahasamund pincode 493449
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.data_loader import load_pincode_master
import pathlib

base_dir = str(pathlib.Path(__file__).resolve().parents[0])
pins = load_pincode_master(base_dir)
pin_data = pins.get("493449")

if pin_data:
    print(f"Pincode: 493449 (Mahasamund)")
    print(f"City: {pin_data.city}")
    print(f"State: {pin_data.state}")
    print(f"Global Cargo Region: {pin_data.global_courier_cargo_region}")
    print(f"Is ODA: {pin_data.is_oda}")
else:
    print("Pincode 493449 not found in database")

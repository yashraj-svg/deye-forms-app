"""
Debug Pincode Region Mapping
============================
"""

import os, sys, django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.data_loader import load_pincode_master

base_dir = os.path.dirname(__file__)
pins = load_pincode_master(base_dir)

test_pins = {
    "560060": "Bangalore (should be S1 = ₹13)",
    "686664": "Kanjiramoto (Kerala, should be S3 = ₹16)",
    "642103": "Pollachi (Tamil Nadu, should be S2 = ₹14)",
    "690544": "Kollam (Kerala, should be S3 = ₹16)",
    "575006": "Mangaluru (Karnataka, should be S2 = ₹14)",
    "686691": "Perumbavoor (Kerala, should be S3 = ₹16)",
    "531173": "Visakhapatnam (Andhra Pradesh, should be S2 = ₹14)",
    "493449": "Mahasamund (Chhattisgarh, should be C2 = ₹13)",
}

for pin, desc in test_pins.items():
    rec = pins.get(pin)
    if rec:
        print(f"{pin}: {rec.city}, {rec.state} → {rec.global_cargo_region} - {desc}")
    else:
        print(f"{pin}: NOT FOUND - {desc}")

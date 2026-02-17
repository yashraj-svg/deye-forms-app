#!/usr/bin/env python3
"""Check ODA status of test pincodes"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.models import PincodeData
from forms.calculator.bigship_calculator import Bigship
from forms.calculator.config import Settings

# Initialize Bigship
settings = Settings()
calc = Bigship(settings=settings)

# Test pincodes from actual bills
test_pincodes = [
    ("676101", "CFT 103kg case"),
    ("695020", "CFT 28kg case"),
    ("621220", "MPS 25kg case"),
    ("636111", "LTL 111kg case"),
    ("686664", "CFT 40kg case - marked as passing ODA case"),
]

print("=" * 70)
print("ODA STATUS CHECK - Database vs. Actual Bills")
print("=" * 70)

for pincode, description in test_pincodes:
    is_oda = calc.bigship_pins.is_oda(pincode)
    
    # Check database directly
    try:
        db_rec = PincodeData.objects.filter(pincode=pincode, bigship_is_oda=True).exists()
    except:
        db_rec = False
    
    print(f"\nPincode: {pincode} ({description})")
    print(f"  Bigship Calculator says ODA: {is_oda}")
    print(f"  Database record exists: {db_rec}")

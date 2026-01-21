"""
Add missing pincode 493449 (Mahasamund, Chhattisgarh)
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.models import PincodeData

# Add pincode 493449 - Mahasamund, Chhattisgarh
pincode = "493449"
city = "Mahasamund"
state = "Chhattisgarh"

# Check if already exists
existing = PincodeData.objects.filter(pincode=pincode).first()

if existing:
    print(f"Pincode {pincode} already exists:")
    print(f"  City: {existing.city}")
    print(f"  State: {existing.state}")
    print(f"  Global Cargo Region: {existing.global_cargo_region}")
    
    # Update if needed
    if existing.global_cargo_region != "C1":
        existing.global_cargo_region = "C1"
        existing.state = state
        existing.city = city
        existing.save()
        print(f"✓ Updated to region C1")
else:
    # Create new entry
    PincodeData.objects.create(
        pincode=pincode,
        city=city,
        state=state,
        global_cargo_region="C1",
        is_oda=False,  # Based on invoice showing no ODA charge
    )
    print(f"✓ Added pincode {pincode} - {city}, {state} with region C1")

# Verify
pin_data = PincodeData.objects.filter(pincode=pincode).first()
if pin_data:
    print(f"\nVerification:")
    print(f"  Pincode: {pin_data.pincode}")
    print(f"  City: {pin_data.city}")
    print(f"  State: {pin_data.state}")
    print(f"  Region: {pin_data.global_cargo_region}")
    print(f"  Is ODA: {pin_data.is_oda}")

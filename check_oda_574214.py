"""
Check ODA status for pincode 574214 and verify database loading
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.models import PincodeData
from forms.calculator.data_loader import load_pincode_master

print("=" * 100)
print("CHECKING PINCODE 574214 ODA STATUS")
print("=" * 100)

# Check in database
print("\n1. Checking Django Database:")
print("-" * 100)
try:
    pin_db = PincodeData.objects.filter(pincode='574214').first()
    if pin_db:
        print(f"Pincode: {pin_db.pincode}")
        print(f"City: {pin_db.city}")
        print(f"State: {pin_db.state}")
        print(f"is_oda (Global Cargo): {pin_db.is_oda}")
        print(f"deliverable: {pin_db.deliverable}")
        print(f"safexpress_is_oda: {pin_db.safexpress_is_oda}")
        print(f"global_cargo_region: {pin_db.global_cargo_region}")
    else:
        print("Pincode 574214 NOT FOUND in database!")
except Exception as e:
    print(f"Error: {e}")

# Check via data loader
print("\n2. Checking via Data Loader:")
print("-" * 100)
base_dir = os.path.dirname(os.path.abspath(__file__))
pins_db = load_pincode_master(base_dir)
rec = pins_db.get('574214')

if rec:
    print(f"Pincode: {rec.pincode}")
    print(f"City: {rec.city}")
    print(f"State: {rec.state}")
    print(f"is_oda (Global Cargo): {rec.is_oda}")
    print(f"deliverable: {rec.deliverable}")
    print(f"global_cargo_region: {rec.global_cargo_region}")
else:
    print("Pincode 574214 NOT FOUND in loaded data!")

# Check a few nearby ODA pincodes
print("\n3. Checking Related Pincodes:")
print("-" * 100)
test_pins = ['574201', '574214', '574227', '686610', '690518']
for pin in test_pins:
    db_rec = PincodeData.objects.filter(pincode=pin).first()
    if db_rec:
        oda_status = "ODA" if db_rec.is_oda else "NON-ODA"
        print(f"{pin}: {db_rec.city}, {db_rec.state} - {oda_status}")
    else:
        print(f"{pin}: NOT IN DATABASE")

# Check total ODA pincodes
print("\n4. Total ODA Pincodes in Database:")
print("-" * 100)
total = PincodeData.objects.count()
oda_count = PincodeData.objects.filter(is_oda=True).count()
non_oda = PincodeData.objects.filter(is_oda=False).count()
null_oda = PincodeData.objects.filter(is_oda__isnull=True).count()

print(f"Total pincodes: {total}")
print(f"ODA pincodes (is_oda=True): {oda_count}")
print(f"Non-ODA pincodes (is_oda=False): {non_oda}")
print(f"Null ODA status: {null_oda}")

print("\n" + "=" * 100)
print("DIAGNOSIS:")
print("=" * 100)

if rec and rec.is_oda:
    print("RESULT: 574214 is correctly marked as ODA in the system")
    print("If web interface shows non-ODA, the issue is in the frontend/view layer")
elif rec and not rec.is_oda:
    print("PROBLEM FOUND: 574214 is marked as NON-ODA in database")
    print("SOLUTION: Need to update database with correct ODA status from Rahul CSV")
elif not rec:
    print("PROBLEM FOUND: 574214 is missing from database")
    print("SOLUTION: Need to import pincode data from Rahul CSV")

print("=" * 100)

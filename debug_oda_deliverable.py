#!/usr/bin/env python3
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.bigship_calculator import Bigship
from forms.calculator.freight_calculator import QuoteInput, ShipmentItem
from forms.calculator.data_loader import PincodeDB, PincodeRecord
from forms.calculator.config import Settings
from forms.models import PincodeData

print("="*100)
print("DEBUG: CFT 73kg KA→KL (688529) - ODA CHECK")
print("="*100)

settings = Settings()
calc = Bigship(settings=settings)

# Check if 688529 is in the database as ODA
try:
    pin_rec = PincodeData.objects.get(pincode='688529')
    print(f"\nPincode 688529 found in database:")
    print(f"  City: {pin_rec.city}")
    print(f"  State: {pin_rec.state}")
    print(f"  Bigship ODA: {pin_rec.bigship_is_oda}")
    print(f"  Is ODA per calculator: {calc.bigship_pins.is_oda('688529')}")
except PincodeData.DoesNotExist:
    print(f"\nPincode 688529 NOT found in database")

# Now test the quote calculation
print("\n" + "="*100)
print("CALCULATING QUOTE")
print("="*100)

PINCODE_STATE_MAP = {
    "560060": "Karnataka",
    "688529": "Kerala",
}

class TestPincodeDB(PincodeDB):
    def get(self, pincode):
        result = super().get(pincode)
        if result is None and str(pincode) in PINCODE_STATE_MAP:
            result = PincodeRecord(
                pincode=str(pincode),
                state=PINCODE_STATE_MAP[str(pincode)],
                city="Test City"
            )
        return result

pincodes = TestPincodeDB()

# Create quote with minimal dimensions (1x1x1 to keep volumetric low)
inp = QuoteInput(
    items=[ShipmentItem(weight_kg=73, length_cm=1, breadth_cm=1, height_cm=1)],
    from_pincode="560060",
    to_pincode="688529",
)
inp.bigship_service_type = "CFT"

result = calc.calculate_quote(inp, pincodes)

print(f"\nQuote Result:")
print(f"  Service: CFT")
print(f"  From: 560060 (Karnataka)")
print(f"  To: 688529 (Kerala)")
print(f"  Weight: 73 kg")
print(f"  Deliverable: {result.deliverable}")
print(f"  Partner Name: {result.partner_name}")
print(f"")
print(f"Rate Details:")
print(f"  From Zone: {result.from_zone}")
print(f"  To Zone: {result.to_zone}")
print(f"  Rate per kg: Rs {result.rate_per_kg}")
print(f"")
print(f"Chargeable Weight: {result.chargeable_weight_kg} kg")
print(f"Base Freight: Rs {result.base_freight}")
print(f"")
print(f"Surcharges:")
for name, amount in result.surcharges.items():
    print(f"  {name}: Rs {amount}")
print(f"")
print(f"Total: Rs {result.total_after_gst}")
print(f"")
print(f"Rate Details Dict:")
for key, val in result.rate_details.items():
    print(f"  {key}: {val}")

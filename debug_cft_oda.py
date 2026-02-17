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

settings = Settings()
calc = Bigship(settings=settings)
pincodes = TestPincodeDB()

print("="*80)
print("DEBUG: CFT 73kg KA→KL (ODA)")
print("="*80)

# CFT 73kg with no dimensions given - use minimal to keep vol weight close to actual
dim = (73 * 30) ** (1/3)
print(f"\nCalculated minimal dimension: {dim:.2f} cm (cubic)")

inp = QuoteInput(
    items=[ShipmentItem(weight_kg=73, length_cm=dim, breadth_cm=dim, height_cm=dim)],
    from_pincode="560060",
    to_pincode="688529",
)
inp.bigship_service_type = "CFT"

result = calc.calculate_quote(inp, pincodes)

from_pin = pincodes.get("560060")
to_pin = pincodes.get("688529")
from_zone = calc.get_zone_from_state(from_pin.state, "CFT")
to_zone = calc.get_zone_from_state(to_pin.state, "CFT")

print(f"\nFrom: {from_pin.state} (Zone: {from_zone})")
print(f"To: {to_pin.state} (Zone: {to_zone})")
print(f"")
print(f"Actual Weight: {result.actual_weight_kg} kg")
print(f"Chargeable Weight: {result.chargeable_weight_kg} kg")
print(f"")

rate = calc.CFT_RATES_MATRIX.get(from_zone, {}).get(to_zone, 10.0)
print(f"Rate from {from_zone}→{to_zone}: Rs {rate}/kg")
print(f"Base Freight: Rs {result.base_freight}")
print(f"  = {result.chargeable_weight_kg} kg × Rs {rate} = Rs {result.chargeable_weight_kg * rate:.2f}")
print(f"")
print(f"Surcharges:")
for charge, amount in result.surcharges.items():
    print(f"  {charge}: Rs {amount}")
print(f"")
print(f"Total: Rs {result.total_after_gst}")
print(f"Expected: Rs 1450")
print(f"Difference: Rs {result.total_after_gst - 1450}")
print(f"")

# Now let's manually calculate what 1450 should be
print("\nReverse-engineering expected value:")
print(f"Total: 1450")
print(f"Base + LR + Pickup + Owner Risk + ODA = 1450")
print(f"Base + 25 + ? + 33 + 600 = 1450")
print(f"Base + Pickup = 1450 - 25 - 33 - 600 = 792")
print(f"For 73kg with pickup threshold 20kg:")
print(f"  Pickup = 73 × 1 = 73 (but min 75, so 75)")
print(f"  Base = 792 - 75 = 717")
print(f"  Base/weight = 717 / 73 = 9.82 Rs/kg")

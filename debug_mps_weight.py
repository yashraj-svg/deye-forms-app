import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.bigship_calculator import Bigship
from forms.calculator.freight_calculator import QuoteInput, ShipmentItem
from forms.calculator.config import Settings

settings = Settings()
bigship = Bigship(settings=settings)

# Test item: 30x25x20 cm, 14.98 kg
item = ShipmentItem(length_cm=30, breadth_cm=25, height_cm=20, weight_kg=14.98)
inp = QuoteInput(
    from_pincode="560060",
    to_pincode="524413",
    items=[item],
    bigship_service_type="MPS"
)

print("="*80)
print("MPS Weight Calculation Debug")
print("="*80)

# Calculate volumetric weight manually
volumetric = 30 * 25 * 20 / 5000
print(f"\nManual Volumetric Weight = 30 × 25 × 20 / 5000 = {volumetric:.2f} kg")

# Calculate using chargeable_weight method
chargeable = bigship.chargeable_weight(inp, volumetric_divisor=5000.0, min_weight=0.0)
print(f"Bigship chargeable_weight method = {chargeable:.2f} kg")

# Check what's being used in the actual calculation
actual_weight = sum(item.weight_kg for item in inp.items)
volumetric_weight = bigship.chargeable_weight(inp, volumetric_divisor=bigship.MPS_VOLUMETRIC_DIVISOR, min_weight=0.0)
chargeable_weight = max(actual_weight, volumetric_weight)

print(f"\nActual weight = {actual_weight} kg")
print(f"Volumetric weight = {volumetric_weight} kg")
print(f"MPS_VOLUMETRIC_DIVISOR = {bigship.MPS_VOLUMETRIC_DIVISOR}")
print(f"Chargeable weight = max({actual_weight}, {volumetric_weight}) = {chargeable_weight} kg")

# Check the zones
from forms.calculator.data_loader import PincodeDB, PincodeRecord

PINCODE_STATE_MAP = {
    "560060": "Karnataka",
    "524413": "Andhra Pradesh",
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
from_pin = pincodes.get("560060")
to_pin = pincodes.get("524413")
from_state = from_pin.state if from_pin else "Unknown"
to_state = to_pin.state if to_pin else "Unknown"

from_zone = bigship.get_zone_from_state(from_state, "MPS")
to_zone = bigship.get_zone_from_state(to_state, "MPS")

print(f"\nFrom Zone: {from_zone} (from {from_state})")
print(f"To Zone: {to_zone} (to {to_state})")

# Check MPS rates
zone_rates = bigship.MPS_RATES_MATRIX.get(from_zone, {}).get(to_zone, {"10kg": 296, "add_1kg": 24})
print(f"MPS Rates for {from_zone}->{to_zone}: {zone_rates}")

# Calculate base freight using actual chargeable weight
if chargeable_weight <= 10:
    base = zone_rates["10kg"]
else:
    base = zone_rates["10kg"] + (chargeable_weight - 10) * zone_rates["add_1kg"]

print(f"\nBase freight calculation:")
print(f"  If {chargeable_weight} <= 10: use {zone_rates['10kg']}")
print(f"  Else: {zone_rates['10kg']} + ({chargeable_weight} - 10) × {zone_rates['add_1kg']}")
print(f"  = {zone_rates['10kg']} + {(chargeable_weight - 10) * zone_rates['add_1kg']:.2f}")
print(f"  = Rs {base:.2f}")

print(f"\nTotal = {base:.2f} + 80 (LR) = Rs {base + 80:.2f}")
print(f"Expected: Rs 441.77")

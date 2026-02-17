import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deye_config.settings')
django.setup()

from forms.calculator.bigship_calculator import Bigship
from forms.calculator.freight_calculator import QuoteInput, ShipmentItem
from forms.calculator.config import Settings
from forms.calculator.data_loader import PincodeDB, PincodeRecord

# Pincode to state mapping
PINCODE_STATE_MAP = {
    "560060": "Karnataka",
    "524413": "Andhra Pradesh",
    "695020": "Kerala",
    "201306": "Uttar Pradesh",
    "140301": "West Bengal",
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

# Test MPS - 15kg KA→AP (Expected Rs 441.77)
print("="*80)
print("DEBUG: MPS - 15kg KA to AP")
print("="*80)

settings = Settings()
bigship = Bigship(settings=settings)
pincodes = TestPincodeDB()

inp = QuoteInput(
    from_pincode="560060",  # KA
    to_pincode="524413",    # AP
    items=[ShipmentItem(length_cm=30, breadth_cm=25, height_cm=20, weight_kg=14.98)]
)

result = bigship.calculate_quote(inp, pincodes)

print(f"\nFrom State: Karnataka")
print(f"To State: Andhra Pradesh")
print(f"Service Type: MPS")
print(f"")
print(f"Actual Weight: {result.actual_weight_kg} kg")
print(f"Chargeable Weight: {result.chargeable_weight_kg} kg")
print(f"")
print(f"Base Freight: Rs {result.base_freight}")
print(f"LR Charge: Rs {result.surcharges.get('lr', 0)}")
print(f"Green Tax: Rs {result.surcharges.get('green_tax', 0)}")
print(f"")
print(f"Total: Rs {result.total_after_gst}")
print(f"Expected: Rs 441.77")
print(f"Difference: Rs {result.total_after_gst - 441.77}")
print(f"")

# Also test CFT - 28kg KA→KL (Expected Rs 408.00)
print("\n" + "="*80)
print("DEBUG: CFT - 28kg KA to KL")
print("="*80)

inp2 = QuoteInput(
    from_pincode="560060",  # KA
    to_pincode="695020",    # KL
    items=[ShipmentItem(length_cm=30, breadth_cm=25, height_cm=20, weight_kg=27.75)],
    bigship_service_type="CFT"
)

result2 = bigship.calculate_quote(inp2, pincodes)

print(f"\nFrom State: Karnataka")
print(f"To State: Kerala")
print(f"Service Type: CFT")
print(f"")
print(f"Actual Weight: {result2.actual_weight_kg} kg")
print(f"Chargeable Weight: {result2.chargeable_weight_kg} kg")
print(f"")
print(f"Base Freight: Rs {result2.base_freight}")
print(f"LR Charge: Rs {result2.surcharges.get('lr', 0)}")
print(f"Pickup Charge: Rs {result2.surcharges.get('pickup', 0)}")
print(f"Owner Risk: Rs {result2.surcharges.get('owner_risk', 0)}")
print(f"Green Tax: Rs {result2.surcharges.get('green_tax', 0)}")
print(f"ODA Charge: Rs {result2.surcharges.get('oda', 0)}")
print(f"")
print(f"Total: Rs {result2.total_after_gst}")
print(f"Expected: Rs 408.00")
print(f"Difference: Rs {result2.total_after_gst - 408.00}")
print(f"")

# Also test LTL - 26kg UP→WB (Expected Rs 420.96)
print("\n" + "="*80)
print("DEBUG: LTL - 26kg UP to WB")
print("="*80)

inp3 = QuoteInput(
    from_pincode="201306",  # UP
    to_pincode="140301",    # WB (should be different state)
    items=[ShipmentItem(length_cm=30, breadth_cm=25, height_cm=20, weight_kg=26.0)],
    bigship_service_type="LTL"
)

result3 = bigship.calculate_quote(inp3, pincodes)

print(f"\nFrom Pincode: 201306")
print(f"To Pincode: 140301")
print(f"Service Type: LTL")
print(f"")
print(f"Actual Weight: {result3.actual_weight_kg} kg")
print(f"Chargeable Weight: {result3.chargeable_weight_kg} kg")
print(f"")
print(f"Base Freight: Rs {result3.base_freight}")
print(f"LR Charge: Rs {result3.surcharges.get('lr', 0)}")
print(f"Pickup Charge: Rs {result3.surcharges.get('pickup', 0)}")
print(f"Owner Risk: Rs {result3.surcharges.get('owner_risk', 0)}")
print(f"Green Tax: Rs {result3.surcharges.get('green_tax', 0)}")
print(f"ODA Charge: Rs {result3.surcharges.get('oda', 0)}")
print(f"")
print(f"Total: Rs {result3.total_after_gst}")
print(f"Expected: Rs 420.96")
print(f"Difference: Rs {result3.total_after_gst - 420.96}")
